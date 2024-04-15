"""This __init__ file will be called by Http Starter function to pass the ThreatHunt data to activity function."""
import azure.durable_functions as df
from shared_code.consts import THREATHUNT_LOG_TYPE, LOGS_STARTS_WITH
from shared_code.logger import applogger


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Get ThreatHunt data from durable orchestration context and schedule an activity for execution.

    Args:
        context (df.DurableOrchestrationContext): Context of the durable orchestration execution.

    Returns:
        str: result of Activity function
    """
    applogger.debug(
        "{} ThreatHuntOrchestrator function called!".format(LOGS_STARTS_WITH)
    )
    json_data = context.get_input()
    result1 = yield context.call_activity(
        "RubrikActivity", {"data": json_data, "log_type": THREATHUNT_LOG_TYPE}
    )
    applogger.debug(
        "{} ThreatHuntOrchestrator function completed!".format(LOGS_STARTS_WITH)
    )
    return result1


main = df.Orchestrator.create(orchestrator_function)
