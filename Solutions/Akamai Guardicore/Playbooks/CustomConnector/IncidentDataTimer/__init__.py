import logging

import azure.functions as func
import azure.durable_functions as df


async def main(timer: func.TimerRequest, starter: str) -> None:
    if timer.past_due:
        logging.info('The timer is past due!')
    client = df.DurableOrchestrationClient(starter)
    instance_id = "singleton_instance_incident_enrichment"
    existing_instance = await client.get_status(instance_id)
    if existing_instance is None or existing_instance.runtime_status in [df.OrchestrationRuntimeStatus.Completed,
                                                                              df.OrchestrationRuntimeStatus.Failed,
                                                                              df.OrchestrationRuntimeStatus.Terminated,
                                                                              None]:
        await client.start_new("IncidentEnrichment", instance_id)
        logging.info(f"Starting new orchestration")
    else:
        logging.info(
            f"Orchestration already running with instance id: {instance_id} and status: {existing_instance.runtime_status}")
