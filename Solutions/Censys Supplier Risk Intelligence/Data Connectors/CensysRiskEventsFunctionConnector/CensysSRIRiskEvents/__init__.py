"""Timer triggered function: ingest Censys risk events into Microsoft Sentinel."""
import datetime
import time

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.censys_client import CensysClient, build_filters
from ..SharedCode.checkpoint import CheckpointManager, checkpoint_key
from ..SharedCode.exceptions import CensysCursorExpired, CensysException, CensysTimeBudgetReached
from ..SharedCode.logger import applogger
from ..SharedCode.sentinel import SentinelIngestor

_RFC3339 = "%Y-%m-%dT%H:%M:%SZ"


def _start_time() -> str:
    """Initial start time from the settings. Empty or unset means all events Censys still retains."""
    value = (consts.INITIAL_START_TIME or "").strip()
    if not value or value == "InitialStartTime":
        return consts.DEFAULT_START_TIME
    try:
        datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise CensysException(f"InitialStartTime '{value}' is not a valid RFC3339 date and time, for example 2026-10-01T00:00:00Z.")
    return value


def _validate_settings() -> None:
    missing = [name for name, value in (
        ("CensysApiToken", consts.API_TOKEN), ("OrganizationId", consts.ORGANIZATION_ID),
        ("AzureWebJobsStorage", consts.CONN_STRING), ("AZURE_DATA_COLLECTION_ENDPOINT", consts.DATA_COLLECTION_ENDPOINT),
        ("AZURE_DATA_COLLECTION_RULE_ID", consts.DATA_COLLECTION_RULE_ID)) if not value]
    if missing:
        raise CensysException(f"Missing application settings: {', '.join(missing)}")


def ingest(start: float) -> int:
    """Read every new event, upload it page by page and move the checkpoint after each page."""
    _validate_settings()
    filters = build_filters(consts.SUPPLIER_IDS, consts.CHANGE_TYPES, consts.SEVERITY, consts.RAPID_RESPONSE, consts.RISK_TYPE_IDS)
    key = checkpoint_key(consts.ORGANIZATION_ID, *[f"{k}={v}" for k, v in sorted(filters.items())])
    manager = CheckpointManager(consts.CONN_STRING, consts.CHECKPOINT_TABLE_NAME)
    client = CensysClient(consts.API_TOKEN, consts.ORGANIZATION_ID, deadline=start + consts.MAX_RUN_SECONDS,
                          hard_deadline=start + consts.HARD_LIMIT_SECONDS)
    ingestor = SentinelIngestor(consts.DATA_COLLECTION_ENDPOINT, consts.DATA_COLLECTION_RULE_ID, consts.STREAM_NAME, consts.SCOPE)

    checkpoint = manager.get(key)
    if checkpoint and checkpoint[0]:
        after_time, after_id = checkpoint
        applogger.info(f"{consts.LOG_PREFIX}: continuing from checkpoint inserted_at={after_time} id={after_id}")
    else:
        after_time, after_id = _start_time(), None
        applogger.info(f"{consts.LOG_PREFIX}: no checkpoint, starting from {after_time}")

    total, expired = 0, False
    while True:
        try:
            for events in client.iter_pages(after_time, after_id, filters):
                ingestor.upload(events)
                total += len(events)
                last = events[-1]
                if last.get("inserted_at") and last.get("id"):
                    manager.set(key, last["inserted_at"], last["id"])
                else:
                    applogger.warning(f"{consts.LOG_PREFIX}: last event of the page has no inserted_at or id, checkpoint not moved")
                applogger.info(f"{consts.LOG_PREFIX}: ingested {len(events)} events, checkpoint inserted_at={last.get('inserted_at')}")
            return total
        except CensysTimeBudgetReached:
            applogger.info(f"{consts.LOG_PREFIX}: time budget of {consts.MAX_RUN_SECONDS} seconds reached after {total} events; "
                           "the checkpoint is saved and the next run continues from it")
            return total
        except CensysCursorExpired:
            if expired:
                raise
            expired = True
            after_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=consts.RETENTION_DAYS)).strftime(_RFC3339)
            after_id = None
            applogger.warning(f"{consts.LOG_PREFIX}: checkpoint is older than the retention window, restarting from {after_time}")


def main(mytimer: func.TimerRequest) -> None:
    """Entry point called by the timer trigger."""
    start = time.time()
    applogger.info(f"{consts.LOG_PREFIX}: start processing")
    if mytimer.past_due:
        applogger.info(f"{consts.LOG_PREFIX}: the timer is past due")
    try:
        total = ingest(start)
    except CensysException as err:
        applogger.error(f"{consts.LOG_PREFIX}: run failed: {err}")
        raise
    applogger.info(f"{consts.LOG_PREFIX}: finished, {total} events ingested in {int(time.time() - start)} sec")
