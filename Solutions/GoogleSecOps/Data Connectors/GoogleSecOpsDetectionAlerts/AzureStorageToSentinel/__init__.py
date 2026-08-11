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

    applogger.info(
        consts.LOG_FORMAT.format(
            consts.LOG_PREFIX, "main", consts.FUNCTION_NAME_INGESTER,
            f"started at {start.isoformat()}",
        )
    )

    if mytimer.past_due:
        applogger.warning(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX, "main", consts.FUNCTION_NAME_INGESTER,
                "timer is past due",
            )
        )

    try:
        runner = AzureStorageToSentinel()
        runner.run()
    except Exception:
        applogger.exception(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX, "main", consts.FUNCTION_NAME_INGESTER,
                "unhandled error",
            )
        )
        raise
    finally:
        end = datetime.datetime.now(datetime.timezone.utc)
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX, "main", consts.FUNCTION_NAME_INGESTER,
                f"ended at {end.isoformat()} (duration={(end - start).total_seconds():.2f}s)",
            )
        )
