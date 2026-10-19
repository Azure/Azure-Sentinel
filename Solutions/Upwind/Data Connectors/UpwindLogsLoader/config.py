"""Configuration management for the Upwind Catalog Loader function."""

import logging
import os
from datetime import datetime, timezone

from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from croniter import croniter
from dotenv import load_dotenv


# Datasets that support severity filtering default to this minimum. Setting the
# corresponding UPWIND_*_MIN_SEVERITY app setting to an empty value disables
# filtering for that dataset and ingests every severity.
DEFAULT_MIN_SEVERITY = "high"

DEFAULT_SCHEDULE = "0 0 * * * *"

# Each run looks back over the gap since the previous scheduled run plus this
# overlap, so records landing right at a run boundary aren't missed.
LOOKBACK_OVERLAP_MINUTES = 5

# Used only when the schedule can't be parsed: an hourly run plus the overlap.
FALLBACK_LOOKBACK_MINUTES = 65

# How far ahead to scan the schedule for its longest gap between runs. A week
# covers day-of-week patterns such as business-hours-only schedules.
_SCHEDULE_SCAN_DAYS = 7
_SCHEDULE_SCAN_MAX_RUNS = 20000


class ConfigStore:
    """External parameters required by the function application."""

    def __init__(self, **kwargs):
        self._config = {}
        for key, value in kwargs.items():
            self._config[key] = value

    def get(self, key, default=None):
        """Retrieve a config value by key."""
        return self._config.get(key, default)

    def __repr__(self):
        return f"ConfigStore(keys={list(self._config.keys())})"


# Stream names are deliberately not required: clearing a dataset's STREAM_NAME_*
# app setting is how that dataset is turned off.
_REQUIRED_CONFIG_KEYS = [
    "azure_dce_endpoint",
    "azure_dcr_immutableid",
    "upwind_org_id",
    "upwind_client_id",
    "upwind_auth_url",
]


def _parse_int_env(name: str, default: str) -> int:
    raw = os.getenv(name, default)
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"Invalid integer for {name}: '{raw}'")


def lookback_minutes_for_schedule(schedule: str) -> int:
    """
    Derive each run's lookback window from the function's timer schedule.

    The window is the longest gap between consecutive scheduled runs plus
    LOOKBACK_OVERLAP_MINUTES, so every moment is covered by at least one run
    even for irregular schedules (e.g. business hours only, where the longest
    gap spans the weekend).

    :param schedule: The Azure Functions NCRONTAB expression (six fields,
        seconds first), e.g. "0 0 * * * *" for hourly.
    :return: Lookback in whole minutes.
    """

    try:
        start = datetime(2026, 1, 5, tzinfo=timezone.utc)  # a Monday at 00:00
        runs = croniter(schedule, start, second_at_beginning=True)
        previous = runs.get_next(datetime)
        scan_end = previous.timestamp() + _SCHEDULE_SCAN_DAYS * 24 * 3600
        longest_gap_seconds = 0.0

        for _ in range(_SCHEDULE_SCAN_MAX_RUNS):
            current = runs.get_next(datetime)
            longest_gap_seconds = max(
                longest_gap_seconds, (current - previous).total_seconds()
            )
            if current.timestamp() >= scan_end:
                break
            previous = current
    except Exception as e:
        logging.warning(
            "Could not parse schedule %r (%s); using a %d-minute lookback.",
            schedule,
            e,
            FALLBACK_LOOKBACK_MINUTES,
        )
        return FALLBACK_LOOKBACK_MINUTES

    return -(-int(longest_gap_seconds) // 60) + LOOKBACK_OVERLAP_MINUTES


def _resolve_upwind_secret(azure_client_id, key_vault_uri, secret_name):
    """Retrieve Upwind client secret from Key Vault (preferred) or env var (fallback)."""

    if key_vault_uri and secret_name:
        try:
            credential = (
                ManagedIdentityCredential(client_id=azure_client_id)
                if azure_client_id
                else ManagedIdentityCredential()
            )
            secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
            retrieved_secret = secret_client.get_secret(secret_name)
            logging.info("Successfully retrieved Upwind secret from Key Vault.")
            return retrieved_secret.value
        except Exception as e:
            logging.error("Failed to retrieve Upwind secret from Key Vault: %s", e)
            return None

    logging.warning(
        "Key Vault not fully configured. "
        "Falling back to UPWIND_CLIENT_SECRET env var."
    )
    return os.getenv("UPWIND_CLIENT_SECRET")


def load_configuration() -> ConfigStore:
    """Load and validate configuration from environment variables and Key Vault."""

    load_dotenv()

    azure_client_id = os.getenv("AZURE_CLIENT_ID")
    upwind_client_secret = _resolve_upwind_secret(
        azure_client_id,
        os.getenv("KEY_VAULT_URI"),
        os.getenv("UPWIND_SECRET_NAME"),
    )

    config = ConfigStore(
        azure_client_id=azure_client_id,
        azure_dce_endpoint=os.getenv("DCE_ENDPOINT"),
        azure_dcr_immutableid=os.getenv("DCR_IMMUTABLEID"),
        # Inventory/catalog keeps the original STREAM_NAME env var as a fallback
        # so Function Apps deployed before the multi-endpoint update keep working
        # without needing every new app setting populated immediately.
        azure_stream_name_inventory=os.getenv("STREAM_NAME_INVENTORY", os.getenv("STREAM_NAME")),
        azure_stream_name_vulnerability=os.getenv("STREAM_NAME_VULNERABILITY"),
        azure_stream_name_threat_detections=os.getenv("STREAM_NAME_THREAT_DETECTIONS"),
        azure_stream_name_threat_events=os.getenv("STREAM_NAME_THREAT_EVENTS"),
        azure_stream_name_threat_stories=os.getenv("STREAM_NAME_THREAT_STORIES"),
        azure_stream_name_config_findings=os.getenv("STREAM_NAME_CONFIG_FINDINGS"),
        upwind_org_id=os.getenv("UPWIND_ORG_ID"),
        upwind_client_id=os.getenv("UPWIND_CLIENT_ID"),
        upwind_client_secret=upwind_client_secret,
        upwind_auth_url=os.getenv("UPWIND_AUTH_URL", "https://auth.upwind.io/oauth/token"),
        upwind_api_base_url=os.getenv("UPWIND_API_BASE_URL", "https://api.upwind.io"),
        upwind_page_size=_parse_int_env("UPWIND_PAGE_SIZE", "100"),
        upwind_max_retries=_parse_int_env("UPWIND_MAX_RETRIES", "5"),
        upwind_initial_backoff_seconds=_parse_int_env("UPWIND_INITIAL_BACKOFF_SECONDS", "1"),
        upwind_max_backoff_seconds=_parse_int_env("UPWIND_MAX_BACKOFF_SECONDS", "60"),
        # The inventory API allows 600 catalog requests per minute per org,
        # shared by every API key in the org. Half of that leaves room for the
        # org's other clients; 0 disables pacing.
        upwind_max_requests_per_minute=_parse_int_env("UPWIND_MAX_REQUESTS_PER_MINUTE", "300"),
        upwind_lookback_minutes=lookback_minutes_for_schedule(
            os.getenv("UPWIND_CATALOG_SCHEDULE", DEFAULT_SCHEDULE)
        ),
        # Wall-clock budget for one run, kept under host.json's 10-minute
        # functionTimeout with room for an in-flight request (60s timeout) and
        # its upload to finish after the last budget check.
        upwind_run_time_budget_seconds=_parse_int_env("UPWIND_RUN_TIME_BUDGET_SECONDS", "480"),
        # Hours between full catalog syncs, which re-ingest assets that haven't
        # changed so they don't age out of the table; 0 turns them off. Their
        # progress is kept in the Function App's own storage account.
        upwind_full_sync_interval_hours=_parse_int_env("UPWIND_FULL_SYNC_INTERVAL_HOURS", "24"),
        azure_webjobs_storage=os.getenv("AzureWebJobsStorage"),
        upwind_min_severity_vulnerability=os.getenv(
            "UPWIND_VULNERABILITY_MIN_SEVERITY", DEFAULT_MIN_SEVERITY
        ),
        upwind_min_severity_threat_detections=os.getenv(
            "UPWIND_THREAT_DETECTIONS_MIN_SEVERITY", DEFAULT_MIN_SEVERITY
        ),
        upwind_min_severity_threat_events=os.getenv(
            "UPWIND_THREAT_EVENTS_MIN_SEVERITY", DEFAULT_MIN_SEVERITY
        ),
        upwind_min_severity_threat_stories=os.getenv(
            "UPWIND_THREAT_STORIES_MIN_SEVERITY", DEFAULT_MIN_SEVERITY
        ),
        upwind_min_severity_config_findings=os.getenv(
            "UPWIND_CONFIG_FINDINGS_MIN_SEVERITY", DEFAULT_MIN_SEVERITY
        ),
    )

    # Validate required config
    missing = []
    for key in _REQUIRED_CONFIG_KEYS:
        if not config.get(key):
            missing.append(key)
    if not upwind_client_secret:
        missing.append("UPWIND_CLIENT_SECRET (or KEY_VAULT_URI + UPWIND_SECRET_NAME)")
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    if os.getenv("UPWIND_THREAT_LOOKBACK_MINUTES"):
        logging.warning(
            "UPWIND_THREAT_LOOKBACK_MINUTES is no longer used and is ignored; the "
            "lookback is now derived from UPWIND_CATALOG_SCHEDULE (%d minutes).",
            config.get("upwind_lookback_minutes"),
        )

    logging.info(
        "Config loaded: dce_endpoint=%s, org_id=%s, page_size=%s, lookback_minutes=%s, "
        "min_severity(vuln=%s, detections=%s, events=%s, stories=%s, config=%s)",
        config.get("azure_dce_endpoint"),
        config.get("upwind_org_id"),
        config.get("upwind_page_size"),
        config.get("upwind_lookback_minutes"),
        config.get("upwind_min_severity_vulnerability") or "all",
        config.get("upwind_min_severity_threat_detections") or "all",
        config.get("upwind_min_severity_threat_events") or "all",
        config.get("upwind_min_severity_threat_stories") or "all",
        config.get("upwind_min_severity_config_findings") or "all",
    )

    return config
