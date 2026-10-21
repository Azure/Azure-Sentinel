"""Timer triggered function: keep the supplier names and ids in a storage table.

Nothing is sent to Microsoft Sentinel.
"""
import time

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.censys_client import CensysClient
from ..SharedCode.exceptions import CensysException
from ..SharedCode.logger import applogger
from ..SharedCode.suppliers import SupplierStore
from ..SharedCode.validation import load_common


def sync_suppliers(start: float) -> int:
    """Read all suppliers from Censys and store their ids and display names. Returns the number of suppliers."""
    token, organization_id, storage = load_common()
    store = SupplierStore(storage, consts.SUPPLIERS_TABLE_NAME, organization_id)
    client = CensysClient(token, organization_id, deadline=start + consts.MAX_RUN_SECONDS,
                          hard_deadline=start + consts.HARD_LIMIT_SECONDS)
    stored, removed = store.sync(client.iter_suppliers())
    applogger.info(f"{consts.LOG_PREFIX} sync_suppliers: suppliers table updated, "
                   f"{stored} suppliers stored, {removed} removed")
    return stored


def main(mytimer: func.TimerRequest) -> None:
    """Entry point called by the timer trigger."""
    start = time.time()
    applogger.info(f"{consts.LOG_PREFIX} main: suppliers sync start processing")
    try:
        stored = sync_suppliers(start)
    except CensysException as err:
        applogger.error(f"{consts.LOG_PREFIX} main: suppliers sync failed: {err}")
        raise
    applogger.info(f"{consts.LOG_PREFIX} main: suppliers sync finished, "
                   f"{stored} suppliers in {int(time.time() - start)} sec")
