"""This __init__ file is called by the Http Starter to pass Anomaly data to the activity function."""
import inspect
import azure.durable_functions as df
from shared_code.consts import (
    ANOMALY_LOG_TYPE,
    ANOMALY_STREAM,
    DCR_WEBHOOK_RULE_ID,
    LOGS_STARTS_WITH,
    LOG_FORMAT,
)
from shared_code.logger import applogger

FUNCTION_NAME = "RubrikAnomalyOrchestrator"


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Route Anomaly data from the orchestration context to the activity function.

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
            "Routing Anomaly data to RubrikActivity (log_type={}, stream={}).".format(
                ANOMALY_LOG_TYPE, ANOMALY_STREAM
            ),
        )
    )
    result1 = yield context.call_activity(
        "RubrikActivity",
        {
            "data": json_data,
            "log_type": ANOMALY_LOG_TYPE,
            "stream_name": ANOMALY_STREAM,
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
