"""This __init__ file will be called once triggered is generated."""
import inspect
import datetime
import azure.functions as func
from ..SharedCode.logger import applogger
from .cofense_to_sentinel_mapping import CofenseToSentinelMapping
from ..SharedCode.consts import LOGS_STARTS_WITH, COFENSE_TO_SENTINEL


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    __method_name = inspect.currentframe().f_code.co_name
    applogger.info(
        "{}(method={}) : {} : Started execution of Cofense MS Sentinel Integration.".format(
            LOGS_STARTS_WITH,
            __method_name,
            COFENSE_TO_SENTINEL,
        )
    )
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    cofense_obj = CofenseToSentinelMapping()
    cofense_obj.create_sentinel_indicator()

    if mytimer.past_due:
        applogger.info('The timer is past due!')

    applogger.info('Python timer trigger function ran at %s', utc_timestamp)
