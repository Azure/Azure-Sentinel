"""Init file for RetryFailedIndicators function app."""
import datetime
import time
from ..SharedCode.logger import applogger
import azure.functions as func
from .retry_failed_indicators import InfobloxRetryFailedIndicators


def main(mytimer: func.TimerRequest) -> None:
    """Driver method for RetryFailedIndicators."""
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    start = time.time()
    retry_obj = InfobloxRetryFailedIndicators(int(start))
    retry_obj.get_failed_indicators_and_retry()

    if mytimer.past_due:
        applogger.info("The timer is past due!")

    applogger.info("Python timer trigger function ran at %s", utc_timestamp)
