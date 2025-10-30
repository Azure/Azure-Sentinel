"""This __init__ file will be called by Http Starter function to pass the data to activity function."""

import inspect

from azure.durable_functions import DurableOrchestrationContext, Orchestrator
from SharedCode.consts import LOGS_STARTS_WITH
from SharedCode.logger import applogger


def orchestrator_function(context: DurableOrchestrationContext):
    """Get data from durable orchestration context and schedule an activity for execution.

    Args:
        context (df.DurableOrchestrationContext): Context of the durable orchestration execution.

    Returns:
        str: result of Activity function
    """
    __method_name = inspect.currentframe().f_code.co_name
    applogger.debug("{}(method={}) Orchestrator function Called.".format(LOGS_STARTS_WITH, __method_name))
    json_data = context.get_input()
    result = yield context.call_activity("ExtraHopSentinelActivity", json_data)
    return result


main = Orchestrator.create(orchestrator_function)
