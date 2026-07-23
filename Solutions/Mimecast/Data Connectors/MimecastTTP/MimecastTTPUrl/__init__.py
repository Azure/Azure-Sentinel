"""This is init file for TTP URL."""

import datetime
import logging
import azure.functions as func
from SharedCode.logger import applogger
from SharedCode import consts
from MimecastTTPUrl.mimecast_ttp_url import MimecastTTPUrl
import time


log_format = consts.LOG_FORMAT


def main(mytimer: func.TimerRequest) -> None:
    """Run the main logic of the Function App triggered by a timer."""
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    start = time.time()
    applogger.info(
        "{} : {}, Function App started at {}".format(
            consts.LOGS_STARTS_WITH,
            consts.TTP_URL_FUNCTION_NAME,
            datetime.datetime.fromtimestamp(start),
        )
    )
    mimecastttpurl = MimecastTTPUrl(int(start))
    mimecastttpurl.get_mimecast_ttp_url_data_in_sentinel()
    end = time.time()

    applogger.info(
        "{} : {}, Function App ended at {}".format(
            consts.LOGS_STARTS_WITH,
            consts.TTP_URL_FUNCTION_NAME,
            datetime.datetime.fromtimestamp(end),
        )
    )
    applogger.info(
        "{} : {}, Total time taken = {}".format(
            consts.LOGS_STARTS_WITH, consts.TTP_URL_FUNCTION_NAME, end - start
        )
    )
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
