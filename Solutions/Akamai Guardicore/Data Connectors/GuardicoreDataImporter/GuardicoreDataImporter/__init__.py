import logging
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info('Executing guardicore orchestration')
    tasks = [
        context.call_activity("GuardicoreAssetActivity", "Orchestrator"),
        context.call_activity("GuardicorePolicyEntity", "Orchestrator"),
        context.call_activity("GuardicoreAgentActivity", "Orchestrator"),
        context.call_activity("GuardicoreApplicationActivity", "Orchestrator"),
    ]
    yield context.task_all(tasks)


main = df.Orchestrator.create(orchestrator_function)
