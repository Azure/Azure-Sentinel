"""Azure Function Timer Trigger entry point for the GTI Alerts connector."""

import datetime
import time

import azure.functions as func

from SharedCode.logger import applogger
from SharedCode import consts
from RelevanceSystemAlerts.gti_alerts_helper import GTIRelevanceSystemAlertsHelper


log_format = consts.LOG_FORMAT


def main(mytimer: func.TimerRequest) -> None:
    """Run the main logic of the GTI Alerts Function App triggered by a timer.

    Args:
        mytimer (func.TimerRequest): The Azure Functions timer trigger binding.
    """
    utc_timestamp = (
        datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    start = time.time()

    applogger.info(
        "{} : {}, Function App started at {}".format(
            consts.LOGS_STARTS_WITH,
            "RelevanceSystemAlerts",
            datetime.datetime.fromtimestamp(start),
        )
    )

    gti_alerts_helper = GTIRelevanceSystemAlertsHelper(int(start))
    gti_alerts_helper.get_gti_alerts_in_sentinel()

    end = time.time()

    applogger.info(
        "{} : {}, Function App ended at {}".format(
            consts.LOGS_STARTS_WITH,
            "RelevanceSystemAlerts",
            datetime.datetime.fromtimestamp(end),
        )
    )
    applogger.info(
        "{} : {}, Total time taken = {} seconds".format(
            consts.LOGS_STARTS_WITH,
            "RelevanceSystemAlerts",
            round(end - start, 2),
        )
    )

    if mytimer.past_due:
        applogger.info(
            "{} : {}, The timer is past due!".format(
                consts.LOGS_STARTS_WITH,
                "RelevanceSystemAlerts",
            )
        )

    applogger.info(
        "{} : {}, Python timer trigger function ran at {}".format(
            consts.LOGS_STARTS_WITH,
            "RelevanceSystemAlerts",
            utc_timestamp,
        )
    )
