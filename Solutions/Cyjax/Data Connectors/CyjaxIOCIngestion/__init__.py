"""This is init file for CyjaxIOCIngestion Timer Trigger Function."""

import datetime
import logging
import time
import azure.functions as func
from SharedCode.logger import applogger
from SharedCode import consts
from SharedCode.exceptions import CyjaxTimeoutException
from CyjaxIOCIngestion.cyjax_ioc_helper import CyjaxIOCHelper


def main(mytimer: func.TimerRequest) -> None:
    """Run the main logic of the Cyjax IOC Function App triggered by a timer.

    Args:
        mytimer (func.TimerRequest): The timer trigger request object.
    """
    utc_timestamp = (
        datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    )
    start = time.time()
    applogger.info(
        "{} : {}, Function App started at {}".format(
            consts.LOGS_STARTS_WITH,
            consts.FUNCTION_NAME,
            datetime.datetime.fromtimestamp(start),
        )
    )

    try:
        cyjax_helper = CyjaxIOCHelper(int(start))
        cyjax_helper.run()
    except CyjaxTimeoutException:
        applogger.info(
            "{} : {}, Function App timed out gracefully. Checkpoint saved.".format(
                consts.LOGS_STARTS_WITH,
                consts.FUNCTION_NAME,
            )
        )
    except Exception as err:
        applogger.error(
            "{} : {}, Function App encountered an error: {}".format(
                consts.LOGS_STARTS_WITH,
                consts.FUNCTION_NAME,
                err,
            )
        )
        raise

    end = time.time()
    applogger.info(
        "{} : {}, Function App ended at {}".format(
            consts.LOGS_STARTS_WITH,
            consts.FUNCTION_NAME,
            datetime.datetime.fromtimestamp(end),
        )
    )
    applogger.info(
        "{} : {}, Total time taken = {} seconds".format(
            consts.LOGS_STARTS_WITH,
            consts.FUNCTION_NAME,
            end - start,
        )
    )
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
