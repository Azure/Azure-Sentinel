"""Init file for AzureStorageToIndicators function app."""

import datetime
import time
import logging
import azure.functions as func
from .create_indicator import CreateThreatIndicator
from ..SharedCode.logger import applogger
from ..SharedCode import consts


def main(mytimer: func.TimerRequest) -> None:
    """Driver method for Infoblox to sentinel."""
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    start = time.time()
    applogger.info(
        "{} : {} : Start Creating Indicators Execution".format(consts.LOGS_STARTS_WITH, consts.INDICATOR_FUNCTION_NAME)
    )
    indicator_obj = CreateThreatIndicator(int(start))
    indicator_obj.parse_file_list()
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
