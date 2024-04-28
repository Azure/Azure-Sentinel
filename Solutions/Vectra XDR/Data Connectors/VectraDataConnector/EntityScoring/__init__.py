"""This __init__ file will be called once triggered is generated."""
import sys
import time
import traceback
import inspect
import azure.functions as func
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .entity_scoring_collector import EntityScoringCollector


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    try:
        __method_name = inspect.currentframe().f_code.co_name
        applogger.info(
            "{}(method={}) : {} : execution started.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.ENTITY_SCORING_NAME
            )
        )
        start_time = time.time()
        entity_scoring_obj = EntityScoringCollector(
            applogger,
            consts.ENTITY_SCORING_NAME,
            consts.ENTITY_SCORING_CLIENT_ID,
            consts.ENTITY_SCORING_CLIENT_SECRET,
        )
        entity_scoring_obj.validate_params(
            "ENTITY_SCORING_CLIENT_ID",
            "ENTITY_SCORING_CLIENT_SECRET",
        )
        applogger.info(
            "{}(method={}) : {} : Parameter validation successful.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ENTITY_SCORING_NAME,
            )
        )
        entity_scoring_obj.validate_connection()
        applogger.info(
            "{}(method={}) : {} : Established connection with Vectra successfully.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ENTITY_SCORING_NAME,
            )
        )
        entity_scoring_obj.function_name = consts.ENTITY_SCORING_ACCOUNT_NAME
        entity_scoring_obj.get_entity_scoring_data_and_ingest_into_sentinel_account()
        entity_scoring_obj.function_name = consts.ENTITY_SCORING_HOST_NAME
        entity_scoring_obj.get_entity_scoring_data_and_ingest_into_sentinel_host()
        entity_scoring_obj.function_name = consts.ENTITY_SCORING_NAME
        applogger.info(
            "{}(method={}) : {} : time taken for data ingestion is {} sec".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ENTITY_SCORING_NAME,
                int(time.time() - start_time),
            )
        )
        applogger.info(
            "{}(method={}) : {} : execution completed.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.ENTITY_SCORING_NAME
            )
        )
        if mytimer.past_due:
            applogger.info(
                "{}(method={}) : {} : The timer is past due!".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.ENTITY_SCORING_NAME,
                )
            )
    except Exception as ex:
        applogger.error(
            '{}(method={}) : {} : Unexpected error while getting data: error="{}" error_trace="{}"'.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ENTITY_SCORING_NAME,
                str(ex),
                traceback.format_exc(),
            )
        )
        sys.exit(1)
