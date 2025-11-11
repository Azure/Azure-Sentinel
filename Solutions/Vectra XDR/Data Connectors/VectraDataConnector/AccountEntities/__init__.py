"""This __init__ file will be called once triggered is generated."""

import time
import traceback
import sys
import inspect
import azure.functions as func
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .account_entity_collector import AccountEntityCollector


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        applogger.info(
            "{}(method={}) : {} : execution started.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.ACCOUNT_ENTITIES_NAME
            )
        )
        start_time = time.time()
        account_entity_obj = AccountEntityCollector(
            applogger,
            consts.ACCOUNT_ENTITIES_NAME,
            consts.ACCOUNT_ENTITY_CLIENT_ID,
            consts.ACCOUNT_ENTITY_CLIENT_SECRET,
        )
        account_entity_obj.get_and_ingest_account_entities()
        end_time = time.time()
        applogger.info(
            "{}(method={}) : {} : time taken for data ingestion is {} sec".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ACCOUNT_ENTITIES_NAME,
                end_time - start_time,
            )
        )
        applogger.info(
            "{}(method={}) : {} : execution completed.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.ACCOUNT_ENTITIES_NAME
            )
        )

        if mytimer.past_due:
            applogger.info(
                "{}(method={}) : {} : The timer is past due!".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.ACCOUNT_ENTITIES_NAME,
                )
            )
    except Exception as ex:
        applogger.error(
            '{}(method={}) : {} : Unexpected error while getting data: error="{}" error_trace="{}"'.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ACCOUNT_ENTITIES_NAME,
                str(ex),
                traceback.format_exc(),
            )
        )
        sys.exit(1)
