"""Timer-trigger entry point for the AzureStorageToSentinel function.

Monitors Azure File Share for raw detection files saved by GoogleSecOpsToStorage
and ingests them into Microsoft Sentinel via the Logs Ingestion API (DCR).

Checks every 5 minutes for new eligible files and posts detections in batches.

Trigger schedule: controlled by the Schedule CRON expression
(e.g. "0 */10 * * * *" for every 10 minutes).
"""

import datetime

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .azure_storage_to_sentinel import AzureStorageToSentinel


def main(mytimer: func.TimerRequest) -> None:
    """Ingest detection files from Azure File Share into Microsoft Sentinel."""
    start = datetime.datetime.now(datetime.timezone.utc)

    if mytimer.past_due:
        applogger.warning("%s: timer is past due", consts.LOG_PREFIX)

    try:
        runner = AzureStorageToSentinel()
        runner.run()
    except Exception:
        applogger.exception(
            "%s: unhandled error in %s",
            consts.LOG_PREFIX,
            consts.FUNCTION_NAME_INGESTER,
        )
        raise
    finally:
        end = datetime.datetime.now(datetime.timezone.utc)
        applogger.info(
            "%s: %s ended at %s (duration=%.2fs)",
            consts.LOG_PREFIX,
            consts.FUNCTION_NAME_INGESTER,
            end.isoformat(),
            (end - start).total_seconds(),
        )
