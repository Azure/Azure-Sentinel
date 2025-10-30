"""This __init__ file will be called once triggered is generated."""
import datetime
import inspect
from .sentinel import MicrosoftSentinel
from ..SharedCode.logger import applogger
import azure.functions as func
from ..SharedCode.consts import LOGS_STARTS_WITH, SENTINEL_TO_COFENSE


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    __method_name = inspect.currentframe().f_code.co_name
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    applogger.info(
        "{}(method={}) : {} : Started execution of Cofense MS Sentinel Integration.".format(
            LOGS_STARTS_WITH,
            __method_name,
            SENTINEL_TO_COFENSE,
        )
    )
    sentinel_obj = MicrosoftSentinel()
    sentinel_obj.get_indicators_from_sentinel()

    if mytimer.past_due:
        applogger.info("The timer is past due!")

    applogger.info("Python timer trigger function ran at %s", utc_timestamp)
