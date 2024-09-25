"""This __init__ file will be called once triggered is generated."""

import time
import logging
import datetime
import azure.functions as func
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .account_usage_data import AccountUsageDataCollector


def main(mytimer: func.TimerRequest) -> None:
    """
    Start the execution.

    Args:
        mytimer (func.TimerRequest): The timer object that triggered the function.
    """
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    start_time = time.time()
    account_usage_obj = AccountUsageDataCollector()
    account_usage_obj.get_account_usage_data()
    end_time = time.time()

    applogger.info("{} AccountUsageDataCollector: Time taken to ingest data is {}".format(consts.LOGS_STARTS_WITH, end_time - start_time))
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
