"""This __init__ file will be called once triggered is generated."""
import datetime
import time
import inspect
from .sentinel import MicrosoftSentinel
from ..SharedCode.logger import applogger
import azure.functions as func
from ..SharedCode import consts


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    if consts.IS_DEFENDER_USER == "Yes":
        __method_name = inspect.currentframe().f_code.co_name
        utc_timestamp = (
            datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        )
        applogger.info(
            "{}(method={}) : {} : Started execution of Cofense MS Sentinel Integration.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.SENTINEL_TO_DEFENDER,
            )
        )
        start = time.time()
        sentinel_obj = MicrosoftSentinel()
        sentinel_obj.get_indicators_from_sentinel()
        end = time.time()
        applogger.info(
            "{}total time taken for this trigger is {} sec".format(
                consts.LOGS_STARTS_WITH, int(end - start)
            )
        )
        if mytimer.past_due:
            applogger.info("The timer is past due!")

        applogger.info("Python timer trigger function ran at %s", utc_timestamp)
    else:
        applogger.info("Not a defender user.")
