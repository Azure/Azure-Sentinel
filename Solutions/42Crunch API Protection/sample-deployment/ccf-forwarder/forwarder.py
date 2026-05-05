"""
42Crunch CCF Log Forwarder
==========================
Replaces the legacy 42c-fw-2la container (Workspace ID + Primary Key)
with a CCF-compatible forwarder that pushes to Azure Monitor via DCE/DCR
using OAuth2 client credentials (Entra ID).

Guardian log files are line-delimited JSON written to:
    /opt/guardian/logs/<GUARDIAN_NODE_NAME>/api-<uuid>.transaction.log
    /opt/guardian/logs/<GUARDIAN_NODE_NAME>/api-unknown.transaction.log

Each line is a JSON object. This script tracks the last processed line per
instance in a state file and resumes from there on restart.
"""

import datetime
import json
import logging
import os
import time
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Configuration from environment ────────────────────────────────────────────
TENANT_ID = os.environ["TENANT_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
DCE_ENDPOINT = os.environ["DCE_ENDPOINT"].rstrip("/")
DCR_IMMUTABLE_ID = os.environ["DCR_IMMUTABLE_ID"]
DCR_STREAM_NAME = os.environ.get("DCR_STREAM_NAME", "Custom-FortyTwoCrunchAPIProtectionV2_CL")
LOGS_FOLDER = os.environ.get("LOGS_FOLDER", "/opt/guardian/logs")
STATE_FOLDER = os.environ.get("STATE_FOLDER", "/app/.state")
TICK_INTERVAL = int(os.environ.get("TICK_INTERVAL", "10"))

# ── Token cache ────────────────────────────────────────────────────────────────
_token_cache: dict = {"token": None, "expires_at": 0.0}


def get_access_token() -> str:
    """Obtain an OAuth2 bearer token from Entra ID with in-memory caching."""
    now = time.monotonic()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    response = requests.post(
        url,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "https://monitor.azure.com//.default",
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    _token_cache["token"] = payload["access_token"]
    _token_cache["expires_at"] = now + payload["expires_in"]
    logger.info("Obtained new access token (expires in %ds)", payload["expires_in"])
    return _token_cache["token"]


def push_events(events: list) -> None:
    """POST a batch of events to the Azure Monitor DCE/DCR ingestion endpoint."""
    token = get_access_token()
    url = (
        f"{DCE_ENDPOINT}/dataCollectionRules/{DCR_IMMUTABLE_ID}"
        f"/streams/{DCR_STREAM_NAME}?api-version=2023-01-01"
    )
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(events),
        timeout=60,
    )
    response.raise_for_status()
    logger.info("Pushed %d event(s) → HTTP %d", len(events), response.status_code)


def map_log_line(raw_line: str, log_type: int) -> dict | None:
    """
    Parse one guardian JSON log line and map it to the CCF table schema.

    Guardian log JSON fields → CCF column mappings:
      uuid                       → Uuid
      pod.instance_name          → InstanceName
      date_epoch (microseconds)  → Timestamp (ISO-8601 UTC)
      api                        → ApiId
      non_blocking_mode          → NonBlockingMode
      source_ip / source_port    → SourceIp / SourcePort
      destination_port           → DestinationPort
      hostname                   → Hostname
      uri_path                   → UriPath
      status                     → Status
      query                      → Query
      params.request_header      → RequestHeader (JSON string)
      params.response_header     → ResponseHeader (JSON string)
      errors (array)             → Errors (JSON string)
      errors[-1].message         → ErrorMessage
      log_type (1/2)             → EventType ("request" / "unknown")
    """
    line = raw_line.strip()
    if not line:
        return None

    try:
        log = json.loads(line)
    except json.JSONDecodeError as exc:
        logger.warning("Skipping unparseable log line: %s", exc)
        return None

    # date_epoch is in microseconds → convert to UTC datetime
    try:
        ts = datetime.datetime.utcfromtimestamp(log["date_epoch"] / 1_000_000)
        timestamp = ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    except (KeyError, OSError, ValueError):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"

    # Parse error details from the errors array
    errors_raw = log.get("errors", [])
    error_message = ""
    errors_str = ""
    try:
        if isinstance(errors_raw, list) and errors_raw:
            error_message = str(errors_raw[-1].get("message", ""))
        errors_str = json.dumps(errors_raw) if errors_raw else ""
    except Exception:
        pass

    params = log.get("params", {})

    return {
        "Uuid": str(log.get("uuid", "")),
        "Timestamp": timestamp,
        "InstanceName": str(log.get("pod", {}).get("instance_name", "")),
        "Hostname": str(log.get("hostname", "")),
        "SourceIp": str(log.get("source_ip", "")),
        "SourcePort": int(log.get("source_port", 0)),
        "DestinationPort": int(log.get("destination_port", 0)),
        "UriPath": str(log.get("uri_path", "")),
        "Query": str(log.get("query", "") or ""),
        "Status": int(log.get("status", 0)),
        "ErrorMessage": error_message,
        "Errors": errors_str,
        "RequestHeader": json.dumps(params.get("request_header", {})),
        "ResponseHeader": json.dumps(params.get("response_header", {})),
        "ApiId": str(log.get("api", "") or ""),
        "NonBlockingMode": bool(log.get("non_blocking_mode", False)),
        "EventType": "unknown" if log_type == 2 else "request",
    }


# ── State management ───────────────────────────────────────────────────────────

def _state_path(instance_name: str) -> Path:
    return Path(STATE_FOLDER) / f"{instance_name}.json"


def _load_state(instance_name: str, api_filename: str, unknown_filename: str) -> dict:
    path = _state_path(instance_name)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Could not read state file %s: %s — resetting", path, exc)
    return {
        "instance_name": instance_name,
        "api_log": {"filename": api_filename, "last_line_sent": 0},
        "unknown_log": {"filename": unknown_filename, "last_line_sent": 0},
    }


def _save_state(instance_name: str, state: dict) -> None:
    path = _state_path(instance_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── Log file processing ────────────────────────────────────────────────────────

def _process_log_file(log_path: Path, last_line_sent: int, log_type: int) -> int:
    """
    Read new lines from log_path starting at last_line_sent, push them,
    and return the updated last_line_sent. Returns the original value on error
    so the next tick retries.
    """
    if not log_path.exists():
        return last_line_sent

    try:
        all_lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        logger.warning("Cannot read %s: %s", log_path, exc)
        return last_line_sent

    new_lines = all_lines[last_line_sent:]
    if not new_lines:
        return last_line_sent

    events = []
    for raw in new_lines:
        event = map_log_line(raw, log_type)
        if event:
            events.append(event)

    if events:
        try:
            push_events(events)
        except Exception as exc:
            logger.error("Failed to push %d event(s): %s — will retry next tick", len(events), exc)
            return last_line_sent  # do not advance pointer; retry next tick

    return last_line_sent + len(new_lines)


def _process_instance(instance_dir: Path) -> None:
    """Process both transaction log files for one guardian instance directory."""
    instance_name = instance_dir.name

    # Locate the API-specific log file (api-<uuid>.transaction.log)
    api_log_path = None
    unknown_log_path = instance_dir / "api-unknown.transaction.log"

    for candidate in instance_dir.glob("api-*.transaction.log"):
        if candidate.name != "api-unknown.transaction.log":
            api_log_path = candidate
            break

    if api_log_path is None or not unknown_log_path.exists():
        logger.debug("Skipping %s — log files not ready yet", instance_dir)
        return

    state = _load_state(instance_name, api_log_path.name, unknown_log_path.name)

    state["api_log"]["last_line_sent"] = _process_log_file(
        api_log_path, state["api_log"]["last_line_sent"], log_type=1
    )
    state["unknown_log"]["last_line_sent"] = _process_log_file(
        unknown_log_path, state["unknown_log"]["last_line_sent"], log_type=2
    )

    _save_state(instance_name, state)


# ── Main loop ──────────────────────────────────────────────────────────────────

def run() -> None:
    logs_path = Path(LOGS_FOLDER)
    Path(STATE_FOLDER).mkdir(parents=True, exist_ok=True)

    logger.info("42Crunch CCF Log Forwarder starting")
    logger.info("  LOGS_FOLDER      = %s", LOGS_FOLDER)
    logger.info("  STATE_FOLDER     = %s", STATE_FOLDER)
    logger.info("  DCE_ENDPOINT     = %s", DCE_ENDPOINT)
    logger.info("  DCR_IMMUTABLE_ID = %s", DCR_IMMUTABLE_ID)
    logger.info("  DCR_STREAM_NAME  = %s", DCR_STREAM_NAME)
    logger.info("  TICK_INTERVAL    = %ds", TICK_INTERVAL)

    while True:
        try:
            if logs_path.exists():
                for entry in logs_path.iterdir():
                    if entry.is_dir():
                        _process_instance(entry)
            else:
                logger.debug("Logs folder %s does not exist yet — waiting", LOGS_FOLDER)
        except Exception as exc:
            logger.error("Unexpected error in processing loop: %s", exc)

        time.sleep(TICK_INTERVAL)


if __name__ == "__main__":
    run()
