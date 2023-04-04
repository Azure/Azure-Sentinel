"""This __init__ file will be called once triggered is generated."""
import sys
import time
import traceback
import inspect
import azure.functions as func
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .account_detection_collector import AccountDetectionCollector


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    try:
        __method_name = inspect.currentframe().f_code.co_name
        applogger.info(
            "{}(method={}) : {} : execution started.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.ACCOUNT_DETECTION_NAME
            )
        )
        start_time = time.time()
        account_detection_obj = AccountDetectionCollector(applogger, consts.ACCOUNT_DETECTION_NAME)
        account_detection_obj.validate_params()
        applogger.info(
            "{}(method={}) : {} : Parameter validation successful.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ACCOUNT_DETECTION_NAME,
            )
        )
        account_detection_obj.validate_connection()
        applogger.info(
            "{}(method={}) : {} : Established connection with Vectra successfully.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ACCOUNT_DETECTION_NAME,
            )
        )
        account_detection_obj.get_account_detection_data_and_ingest_into_sentinel()
        applogger.info(
            "{}(method={}) : {} : time taken for data ingestion is {} sec".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ACCOUNT_DETECTION_NAME,
                int(time.time() - start_time),
            )
        )
        applogger.info(
            "{}(method={}) : {} : execution completed.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.ACCOUNT_DETECTION_NAME
            )
        )
        if mytimer.past_due:
            applogger.info(
                "{}(method={}) : {} : The timer is past due!".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.ACCOUNT_DETECTION_NAME,
                )
            )
    except Exception as ex:
        applogger.error(
            '{}(method={}) : {} : Unexpected error while getting data: error="{}" error_trace="{}"'.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ACCOUNT_DETECTION_NAME,
                str(ex),
                traceback.format_exc(),
            )
        )
        sys.exit(1)
