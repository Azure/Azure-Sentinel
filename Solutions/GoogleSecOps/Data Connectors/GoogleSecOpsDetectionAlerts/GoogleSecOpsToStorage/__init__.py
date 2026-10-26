"""Timer-trigger entry point for the GoogleSecOpsToStorage function.

Fetches detection alerts from the Google SecOps API and saves
raw detection batches to Azure File Share for durable buffering.

The companion AzureStorageToSentinel function monitors the file share and
ingests the records into Microsoft Sentinel.

Trigger schedule: controlled by the Schedule CRON expression
(e.g. "0 */10 * * * *" for every 10 minutes).
"""

import datetime

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .google_secops_to_storage import GoogleSecOpsToStorage


def main(mytimer: func.TimerRequest) -> None:
    """Fetch detection alerts from SecOps and save to Azure File Share."""
    start = datetime.datetime.now(datetime.timezone.utc)

    applogger.info(
        consts.LOG_FORMAT.format(
            consts.LOG_PREFIX, "main", consts.FUNCTION_NAME_FETCHER,
            f"started at {start.isoformat()}",
        )
    )

    if mytimer.past_due:
        applogger.warning(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX, "main", consts.FUNCTION_NAME_FETCHER,
                "timer is past due",
            )
        )

    try:
        runner = GoogleSecOpsToStorage()
        runner.run()
    except Exception:
        applogger.exception(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX, "main", consts.FUNCTION_NAME_FETCHER,
                "unhandled error",
            )
        )
        raise
    finally:
        end = datetime.datetime.now(datetime.timezone.utc)
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX, "main", consts.FUNCTION_NAME_FETCHER,
                f"ended at {end.isoformat()} (duration={(end - start).total_seconds():.2f}s)",
            )
        )
