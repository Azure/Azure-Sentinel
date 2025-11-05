"""This __init__ file will be called once triggered is generated."""

import time
import traceback
import sys
import azure.functions as func
import inspect
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .host_entity_collector import HostEntityCollector


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        applogger.info(
            "{}(method={}) : {} : execution started.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.HOST_ENTITIES_NAME
            )
        )
        start_time = time.time()
        host_entity_obj = HostEntityCollector(
            applogger,
            consts.HOST_ENTITIES_NAME,
            consts.HOST_ENTITY_CLIENT_ID,
            consts.HOST_ENTITY_CLIENT_SECRET,
        )
        host_entity_obj.get_and_ingest_host_entities()
        end_time = time.time()
        applogger.info(
            "{}(method={}) : {} : time taken for data ingestion is {} sec".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.HOST_ENTITIES_NAME,
                end_time - start_time,
            )
        )
        applogger.info(
            "{}(method={}) : {} : execution completed.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.HOST_ENTITIES_NAME
            )
        )

        if mytimer.past_due:
            applogger.info(
                "{}(method={}) : {} : The timer is past due!".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.HOST_ENTITIES_NAME,
                )
            )
    except Exception as ex:
        applogger.error(
            '{}(method={}) : {} : Unexpected error while getting data: error="{}" error_trace="{}"'.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.HOST_ENTITIES_NAME,
                str(ex),
                traceback.format_exc(),
            )
        )
        sys.exit(1)
