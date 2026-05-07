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
        "%s: %s started at %s",
        consts.LOG_PREFIX,
        consts.FUNCTION_NAME_FETCHER,
        start.isoformat(),
    )

    if mytimer.past_due:
        applogger.warning("%s: timer is past due", consts.LOG_PREFIX)

    try:
        runner = GoogleSecOpsToStorage()
        runner.run()
    except Exception:
        applogger.exception(
            "%s: unhandled error in %s",
            consts.LOG_PREFIX,
            consts.FUNCTION_NAME_FETCHER,
        )
        raise
    finally:
        end = datetime.datetime.now(datetime.timezone.utc)
        applogger.info(
            "%s: %s ended at %s (duration=%.2fs)",
            consts.LOG_PREFIX,
            consts.FUNCTION_NAME_FETCHER,
            end.isoformat(),
            (end - start).total_seconds(),
        )
