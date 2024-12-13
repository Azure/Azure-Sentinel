"""This __init__ file will be called by Http Starter function to pass the data to activity function."""
import azure.durable_functions as df
from shared_code.logger import applogger


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Get data from durable orchestration context and schedule an activity for execution.

    Args:
        context (df.DurableOrchestrationContext): Context of the durable orchestration execution.

    Returns:
        str: result of Activity function
    """
    applogger.debug("Orchestrator function called.")
    json_data = context.get_input()
    result1 = yield context.call_activity(
        json_data.get("activity"), json_data.get("data")
    )
    return result1


main = df.Orchestrator.create(orchestrator_function)
