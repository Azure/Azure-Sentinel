"""This __init__ file is called by the Http Starter to pass ThreatHunt data to the activity function."""
import inspect
import azure.durable_functions as df
from shared_code.consts import (
    THREATHUNT_LOG_TYPE,
    THREATHUNT_STREAM,
    DCR_WEBHOOK_RULE_ID,
    LOGS_STARTS_WITH,
    LOG_FORMAT,
)
from shared_code.logger import applogger

FUNCTION_NAME = "RubrikThreatHuntOrchestrator"


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Route ThreatHunt data from the orchestration context to the activity function.

    Args:
        context (df.DurableOrchestrationContext): durable orchestration context.

    Returns:
        str: result of the Activity function.
    """
    __method_name = inspect.currentframe().f_code.co_name
    applogger.info(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, "function called!"
        )
    )
    json_data = context.get_input()
    applogger.debug(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
            "Routing ThreatHunt data to RubrikActivity (log_type={}, stream={}).".format(
                THREATHUNT_LOG_TYPE, THREATHUNT_STREAM
            ),
        )
    )
    result1 = yield context.call_activity(
        "RubrikActivity",
        {
            "data": json_data,
            "log_type": THREATHUNT_LOG_TYPE,
            "stream_name": THREATHUNT_STREAM,
            "rule_id": DCR_WEBHOOK_RULE_ID,
        },
    )
    applogger.debug(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
            "RubrikActivity returned: {}".format(result1),
        )
    )
    applogger.info(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, "function completed!"
        )
    )
    return result1


main = df.Orchestrator.create(orchestrator_function)
