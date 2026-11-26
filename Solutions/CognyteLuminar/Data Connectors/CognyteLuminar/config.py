"""
config.py

Reads and validates the Function App settings used by the Cognyte Luminar
connector. All settings are read once, at the start of a run, so that a
misconfiguration fails fast with a clear message instead of part-way through
ingestion.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from os import environ
from typing import List, Mapping, Optional

logger = logging.getLogger(__name__)

LUMINAR_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# Largest `limit` the Luminar TAXII server accepts; 10000 returns HTTP 400.
LUMINAR_MAX_PAGE_LIMIT = 9999

# TLP marking-definition ids from STIX 2.1 section 7.2.1.4.
TLP_MARKINGS = {
    "white": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9",
    "clear": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9",
    "green": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da",
    "amber": "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82",
    "red": "marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed",
}

# Collections this connector knows how to turn into Sentinel TI. The
# `leakedrecords` collection is deliberately absent: it contains only
# incident / user-account / malware objects, none of which the Sentinel
# upload API accepts, and we do not synthesise indicators from it.
SUPPORTED_COLLECTIONS = ("iocs", "cyberfeeds")
DEFAULT_COLLECTIONS = "iocs,cyberfeeds"

_ISO_DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ConfigError(ValueError):
    """Raised when a required setting is missing or malformed."""


def normalise_luminar_timestamp(value: str) -> str:
    """Return `value` in the exact format the Luminar TAXII server accepts.

    Accepts `YYYY-MM-DD`, or any ISO-8601 UTC timestamp with 0-6 fractional
    digits and a trailing `Z`, and returns
    `YYYY-MM-DDTHH:MM:SS.ffffffZ` (six fractional digits). The server rejects
    any other fractional precision with HTTP 400.
    """
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("timestamp must be a non-empty string")
    text = value.strip()
    if _ISO_DATE_ONLY.match(text):
        text = f"{text}T00:00:00Z"
    if text.endswith("Z"):
        text = text[:-1]
    elif text.endswith("+00:00"):
        text = text[:-6]
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as err:
        raise ConfigError(
            f"timestamp {value!r} is not ISO-8601 UTC (expected e.g. "
            "2026-01-01 or 2026-01-01T00:00:00.000000Z)"
        ) from err
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.strftime(LUMINAR_DATE_FORMAT)


def _int_setting(
    env: Mapping[str, str],
    name: str,
    default: int,
    minimum: int,
    maximum: Optional[int] = None,
) -> int:
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as err:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from err
    if value < minimum:
        raise ConfigError(f"{name} must be >= {minimum}, got {value}")
    if maximum is not None and value > maximum:
        raise ConfigError(f"{name} must be <= {maximum}, got {value}")
    return value


def _optional_int_setting(
    env: Mapping[str, str], name: str, default: Optional[int], lo: int, hi: int
) -> Optional[int]:
    raw = env.get(name, "").strip()
    if not raw:
        return default
    if raw.lower() in ("none", "off", "disabled"):
        return None
    try:
        value = int(raw)
    except ValueError as err:
        raise ConfigError(f"{name} must be an integer or 'none', got {raw!r}") from err
    if not lo <= value <= hi:
        raise ConfigError(f"{name} must be between {lo} and {hi}, got {value}")
    return value


def _bool_setting(env: Mapping[str, str], name: str, default: bool) -> bool:
    raw = env.get(name, "").strip().lower()
    if not raw:
        return default
    if raw in ("1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    raise ConfigError(f"{name} must be true or false, got {raw!r}")


@dataclass(frozen=True)
class Settings:
    # Microsoft Sentinel / Entra
    tenant_id: str
    application_id: str
    client_secret: str
    workspace_id: str

    # Luminar
    luminar_base_url: str
    luminar_client_id: str
    luminar_client_secret: str
    luminar_account_id: str
    luminar_initial_fetch: str  # normalised Luminar timestamp
    collections: List[str] = field(default_factory=list)

    # Transform
    source_system: str = "Cognyte Luminar"
    default_validity_days: int = 90
    default_confidence: Optional[int] = 50
    tlp_marking_ref: str = TLP_MARKINGS["green"]
    enrich_from_reports: bool = True
    skip_expired_indicators: bool = True

    # Runtime
    storage_connection_string: str = ""
    page_limit: int = LUMINAR_MAX_PAGE_LIMIT
    pages_per_batch: int = 1
    max_run_minutes: int = 25
    resume_overlap_seconds: int = 1

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "Settings":
        env = environ if env is None else env

        def required(name: str) -> str:
            value = env.get(name, "")
            if not isinstance(value, str) or not value.strip():
                raise ConfigError(f"Missing required app setting: {name}")
            return value.strip()

        collections_raw = (
            env.get("LuminarCollections", "").strip() or DEFAULT_COLLECTIONS
        )
        collections: List[str] = []
        for alias in (c.strip().lower() for c in collections_raw.split(",")):
            if not alias:
                continue
            if alias not in SUPPORTED_COLLECTIONS:
                if alias == "leakedrecords":
                    logger.warning(
                        "LuminarCollections includes 'leakedrecords'; it has no "
                        "objects the Sentinel upload API accepts and is skipped."
                    )
                    continue
                raise ConfigError(
                    f"Unsupported collection {alias!r} in LuminarCollections; "
                    f"supported: {', '.join(SUPPORTED_COLLECTIONS)}"
                )
            if alias not in collections:
                collections.append(alias)
        if not collections:
            raise ConfigError("LuminarCollections resolved to an empty list")

        tlp = (env.get("TLPLevel", "") or "green").strip().lower()
        if tlp not in TLP_MARKINGS:
            raise ConfigError(
                f"TLPLevel must be one of {sorted(TLP_MARKINGS)}, got {tlp!r}"
            )

        base_url = required("LuminarBaseURL").rstrip("/")
        if not base_url.startswith("https://"):
            raise ConfigError("LuminarBaseURL must start with https://")

        enrich_raw = (env.get("EnrichFromReports", "") or "true").strip().lower()
        enrich = enrich_raw in ("1", "true", "yes", "on")

        return cls(
            tenant_id=required("TenantID"),
            application_id=required("ApplicationID"),
            client_secret=required("ClientSecret"),
            workspace_id=required("WorkspaceID"),
            luminar_base_url=base_url,
            luminar_client_id=required("LuminarAPIClientID"),
            luminar_client_secret=required("LuminarAPIClientSecret"),
            luminar_account_id=required("LuminarAPIAccountID"),
            luminar_initial_fetch=normalise_luminar_timestamp(
                required("LuminarInitialFetchDate")
            ),
            collections=collections,
            source_system=(env.get("SourceSystem", "") or "Cognyte Luminar").strip(),
            default_validity_days=_int_setting(
                env, "DefaultIndicatorValidityDays", 90, 1
            ),
            default_confidence=_optional_int_setting(
                env, "DefaultConfidence", 50, 0, 100
            ),
            tlp_marking_ref=TLP_MARKINGS[tlp],
            enrich_from_reports=enrich,
            skip_expired_indicators=_bool_setting(env, "SkipExpiredIndicators", True),
            storage_connection_string=env.get("AzureWebJobsStorage", ""),
            page_limit=_int_setting(
                env,
                "LuminarPageLimit",
                LUMINAR_MAX_PAGE_LIMIT,
                1,
                LUMINAR_MAX_PAGE_LIMIT,
            ),
            pages_per_batch=_int_setting(env, "LuminarPagesPerBatch", 1, 1),
            max_run_minutes=_int_setting(env, "MaxRunMinutes", 25, 1),
            resume_overlap_seconds=_int_setting(env, "ResumeOverlapSeconds", 1, 0),
        )
