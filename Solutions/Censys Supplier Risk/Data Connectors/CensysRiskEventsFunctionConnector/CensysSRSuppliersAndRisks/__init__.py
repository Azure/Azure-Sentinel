"""Timer triggered function: keep the supplier names and risk names with their ids in storage tables.

Nothing is sent to Microsoft Sentinel.
"""
import time
from typing import Tuple

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.censys_client import CensysClient
from ..SharedCode.exceptions import CensysException
from ..SharedCode.logger import applogger
from ..SharedCode.suppliers import RiskStore, SupplierStore
from ..SharedCode.validation import load_common


def _client(token: str, organization_id: str, start: float) -> CensysClient:
    """Create a client that stays within the time budget of the run."""
    return CensysClient(token, organization_id, deadline=start + consts.MAX_RUN_SECONDS,
                        hard_deadline=start + consts.HARD_LIMIT_SECONDS)


def sync_suppliers(start: float) -> int:
    """Read all suppliers from Censys and store their ids and display names. Returns the number of suppliers."""
    token, organization_id, storage = load_common()
    store = SupplierStore(storage, consts.SUPPLIERS_TABLE_NAME, organization_id)
    stored, removed = store.sync(_client(token, organization_id, start).iter_suppliers())
    applogger.info(f"{consts.LOG_PREFIX} sync_suppliers: suppliers table updated, "
                   f"{stored} suppliers stored, {removed} removed")
    return stored


def sync_risks(start: float) -> int:
    """Read all risks from Censys and store their ids and names. Returns the number of risks."""
    token, organization_id, storage = load_common()
    store = RiskStore(storage, consts.RISKS_TABLE_NAME, organization_id)
    stored, removed = store.sync(_client(token, organization_id, start).iter_risks())
    applogger.info(f"{consts.LOG_PREFIX} sync_risks: risks table updated, {stored} risks stored, {removed} removed")
    return stored


def sync_all(start: float) -> Tuple[int, int]:
    """Sync the suppliers and the risks. A failure of one does not stop the other, and any failure is raised."""
    counts, errors = [], []
    for name, sync in (("suppliers", sync_suppliers), ("risks", sync_risks)):
        try:
            counts.append(sync(start))
        except CensysException as err:
            applogger.error(f"{consts.LOG_PREFIX} sync_all: {name} sync failed: {err}")
            errors.append(f"{name}: {err}")
    if errors:
        raise CensysException("Sync failed for " + "; ".join(errors))
    return counts[0], counts[1]


def main(mytimer: func.TimerRequest) -> None:
    """Entry point called by the timer trigger."""
    start = time.time()
    applogger.info(f"{consts.LOG_PREFIX} main: suppliers and risks sync start processing")
    try:
        suppliers, risks = sync_all(start)
    except CensysException as err:
        applogger.error(f"{consts.LOG_PREFIX} main: suppliers and risks sync failed: {err}")
        raise
    applogger.info(f"{consts.LOG_PREFIX} main: suppliers and risks sync finished, {suppliers} suppliers and "
                   f"{risks} risks in {int(time.time() - start)} sec")
