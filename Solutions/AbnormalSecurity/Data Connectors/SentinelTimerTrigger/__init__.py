# This function an HTTP starter function for Durable Functions.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable activity function (default name is "Hello")
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
 
import logging

import azure.functions as func
import azure.durable_functions as df

async def main(mytimer: func.TimerRequest, starter: str):
    logging.info("Executing SentinelTimerTrigger function")
    client = df.DurableOrchestrationClient(starter)
    instance_id = "singleton_instance"
    existing_instance = await client.get_status(instance_id)
    if existing_instance is None or str(existing_instance.runtime_status) in ["None", "OrchestrationRuntimeStatus.Completed", "OrchestrationRuntimeStatus.Failed", "OrchestrationRuntimeStatus.Terminated"]:
        instance_id = await client.start_new("SentinelFunctionsOrchestrator", instance_id)
        logging.info(f"Starting new orchestration - the runtime status is: {str(existing_instance.runtime_status)}")
    else:
        logging.info(f"Skipped orchestration - runtime status is : {str(existing_instance.runtime_status)}") 
