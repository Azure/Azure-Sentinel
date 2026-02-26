"""This __init__ file will be called by Http Starter function to pass the Other Events data to activity function."""
import azure.durable_functions as df
from shared_code.consts import EVENTS_LOG_TYPE, LOGS_STARTS_WITH
from shared_code.logger import applogger


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Get General data from durable orchestration context and schedule an activity for execution.

    Args:
        context (df.DurableOrchestrationContext): Context of the durable orchestration execution.

    Returns:
        str: result of Activity function
    """
    applogger.info("{} RubrikEventOrchestrator function called!".format(LOGS_STARTS_WITH))
    json_data = context.get_input()

    result1 = yield context.call_activity(
        "RubrikActivity", {"data": json_data, "log_type": EVENTS_LOG_TYPE}
    )
    applogger.info(
        "{} RubrikEventOrchestrator function completed!".format(LOGS_STARTS_WITH)
    )
    return result1


main = df.Orchestrator.create(orchestrator_function)
