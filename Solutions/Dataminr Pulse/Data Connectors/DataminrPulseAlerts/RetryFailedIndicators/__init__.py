"""init file for Retrying Failed Indicators."""
import datetime
import logging
import azure.functions as func
from .retry_failed_indicators import get_failed_indicators_and_retry


async def main(mytimer: func.TimerRequest) -> None:
    """Driver method for RetryFailedIndicators."""
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    await get_failed_indicators_and_retry()
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
