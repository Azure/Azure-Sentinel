"""Timer triggered function: ingest Censys risk events into Microsoft Sentinel."""
import datetime
import time
from typing import List, Optional

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.censys_client import CensysClient
from ..SharedCode.checkpoint import CheckpointManager, checkpoint_key
from ..SharedCode.exceptions import CensysCursorExpired, CensysException, CensysTimeBudgetReached
from ..SharedCode.logger import applogger
from ..SharedCode.sentinel import SentinelIngestor
from ..SharedCode.suppliers import RiskStore, SupplierStore, resolve
from ..SharedCode.validation import Settings, load_settings

_RFC3339 = "%Y-%m-%dT%H:%M:%SZ"


def _supplier_ids(settings: Settings) -> Optional[List[str]]:
    """Look up the ids of the supplier names, once per run. Returns None when no supplier names are set.

    A supplier added to Censys later is used from the next run on, without reading its earlier events. A name that
    matches no supplier is a warning, not an error. An empty list means that no id was found at all.
    """
    if not settings.supplier_names:
        return None
    store = SupplierStore(settings.storage_connection, consts.SUPPLIERS_TABLE_NAME, settings.organization_id)
    ids, missing = resolve(settings.supplier_names, store.load())
    for name in missing:
        applogger.warning(f"{consts.LOG_PREFIX} ingest: supplier name '{name}' was not found "
                          "in the suppliers table, it is skipped")
    if len(ids) > consts.MAX_SUPPLIER_IDS:
        raise CensysException(f"The supplier names in SupplierNames match {len(ids)} suppliers, at most "
                              f"{consts.MAX_SUPPLIER_IDS} are allowed in one request. Enter fewer names.")
    return ids


def _risk_type_ids(settings: Settings) -> Optional[List[str]]:
    """Look up the ids of the risk names, once per run. Returns None when no risk names are set.

    Works like _supplier_ids: an unknown name is a warning, and an empty list means that no id was found at all.
    """
    if not settings.risk_names:
        return None
    store = RiskStore(settings.storage_connection, consts.RISKS_TABLE_NAME, settings.organization_id)
    ids, missing = resolve(settings.risk_names, store.load())
    for name in missing:
        applogger.warning(f"{consts.LOG_PREFIX} ingest: risk name '{name}' was not found "
                          "in the risks table, it is skipped")
    if len(ids) > consts.MAX_RISK_TYPE_IDS:
        raise CensysException(f"The risk names in RiskNames match {len(ids)} risks, at most "
                              f"{consts.MAX_RISK_TYPE_IDS} are allowed in one request. Enter fewer names.")
    return ids


def ingest(start: float) -> int:
    """Read every new event, upload it page by page and move the checkpoint after each page."""
    settings = load_settings()
    supplier_ids = _supplier_ids(settings)
    risk_type_ids = _risk_type_ids(settings)
    for setting, ids in (("SupplierNames", supplier_ids), ("RiskNames", risk_type_ids)):
        if ids is not None and not ids:
            applogger.warning(f"{consts.LOG_PREFIX} ingest: no id found for the names set in {setting}, "
                              "nothing is collected in this run. The next run tries again.")
            return 0
    filters = settings.filters(supplier_ids, risk_type_ids)
    # The suppliers and risks are not part of the checkpoint key. When their names are changed, collection continues
    # from the current checkpoint with the new ids, and the earlier events of a newly selected supplier or risk
    # are not collected.
    key_parts = [f"{k}={v}" for k, v in sorted(filters.items()) if k not in ("supplier_ids", "risk_type_ids")]
    key = checkpoint_key(settings.organization_id, *key_parts)
    manager = CheckpointManager(settings.storage_connection, consts.CHECKPOINT_TABLE_NAME)
    client = CensysClient(settings.api_token, settings.organization_id, deadline=start + consts.MAX_RUN_SECONDS,
                          hard_deadline=start + consts.HARD_LIMIT_SECONDS)
    ingestor = SentinelIngestor(settings.data_collection_endpoint, settings.data_collection_rule_id,
                                consts.STREAM_NAME, consts.SCOPE)

    checkpoint = manager.get(key)
    if checkpoint and checkpoint[0]:
        after_time, after_id = checkpoint
        applogger.info(f"{consts.LOG_PREFIX} ingest: continuing from checkpoint "
                       f"inserted_at={after_time} id={after_id}")
    else:
        after_time, after_id = settings.start_time, None
        applogger.info(f"{consts.LOG_PREFIX} ingest: no checkpoint, starting from {after_time}")

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
                    applogger.warning(f"{consts.LOG_PREFIX} ingest: last event of the page has no inserted_at "
                                      "or id, checkpoint not moved")
                applogger.info(f"{consts.LOG_PREFIX} ingest: ingested {len(events)} events, "
                               f"checkpoint inserted_at={last.get('inserted_at')}")
            return total
        except CensysTimeBudgetReached:
            applogger.info(f"{consts.LOG_PREFIX} ingest: time budget of {consts.MAX_RUN_SECONDS} seconds reached "
                           f"after {total} events. The checkpoint is saved and the next run continues from it.")
            return total
        except CensysCursorExpired:
            if expired:
                raise
            expired = True
            window = datetime.timedelta(days=consts.RETENTION_DAYS)
            after_time = (datetime.datetime.now(datetime.timezone.utc) - window).strftime(_RFC3339)
            after_id = None
            applogger.warning(f"{consts.LOG_PREFIX} ingest: the checkpoint is older than the retention window, "
                              f"restarting from {after_time}")


def main(mytimer: func.TimerRequest) -> None:
    """Entry point called by the timer trigger."""
    start = time.time()
    applogger.info(f"{consts.LOG_PREFIX} main: start processing")
    if mytimer.past_due:
        applogger.info(f"{consts.LOG_PREFIX} main: the timer is past due")
    try:
        total = ingest(start)
    except CensysException as err:
        applogger.error(f"{consts.LOG_PREFIX} main: run failed: {err}")
        raise
    applogger.info(f"{consts.LOG_PREFIX} main: finished, {total} events ingested in {int(time.time() - start)} sec")
