# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
import datetime
import logging
import asyncio
import os
import re
import sys
import azure.durable_functions as df

from .soar_connector_async import AbnormalSoarConnectorAsync
from .sentinel_connector_async import AzureSentinelConnectorAsync
from .soar_connector_async_v2 import get_cases, get_threats
from .utils import (
    get_context,
    should_use_v2_logic,
    set_date_on_entity,
    TIME_FORMAT,
    Resource,
)

RESET_ORCHESTRATION = os.environ.get("RESET_OPERATION", "false")
PERSIST_TO_SENTINEL = os.environ.get("PERSIST_TO_SENTINEL", "true")
API_TOKEN = os.environ['ABNORMAL_SECURITY_REST_API_TOKEN']
SENTINEL_WORKSPACE_ID = os.environ['SENTINEL_WORKSPACE_ID']
SENTINEL_SHARED_KEY = os.environ['SENTINEL_SHARED_KEY']
LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')
if ((LOG_ANALYTICS_URI in (None, '') or str(LOG_ANALYTICS_URI).isspace())):
    LOG_ANALYTICS_URI = 'https://' + SENTINEL_WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(LOG_ANALYTICS_URI))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")

def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info(f"Executing orchestrator function version 1.2")
    datetimeEntityId = df.EntityId("SoarDatetimeEntity", "latestDatetime")
    
    if should_reset_date_params():
        context.signal_entity(datetimeEntityId, "reset")

    stored_threats_datetime = yield context.call_entity(datetimeEntityId, "get", {"type": "threats_date"})
    logging.info(f"Retrieved stored threats datetime: {stored_threats_datetime}")
    
    stored_cases_datetime = yield context.call_entity(datetimeEntityId, "get", {"type": "cases_date"})
    logging.info(f"Retrieved stored cases datetime: {stored_cases_datetime}")

    current_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    logging.info(f"Current python version:: {sys.version}")
    if should_use_v2_logic():
        logging.info(
            f"Using v2 fetching logic with inputs (threats, cases):: ({stored_threats_datetime},{stored_cases_datetime})"
        )
        asyncio.run(
            fetch_and_store_abnormal_data_v2(
                context=context,
                stored_threats_datetime=stored_threats_datetime,
                stored_cases_datetime=stored_cases_datetime,
            )
        )
        logging.info("Finished v2 fetching")
        return
    else:
        logging.info(
            f"Running legacy logic with inputs (threats, cases):: ({stored_threats_datetime},{stored_cases_datetime})"
        )

    asyncio.run(transfer_abnormal_data_to_sentinel(stored_threats_datetime, stored_cases_datetime, current_datetime, context))
    logging.info("Orchestrator execution finished") 
    
def should_reset_date_params():
    return RESET_ORCHESTRATION == "true"

async def transfer_abnormal_data_to_sentinel(stored_threats_datetime,stored_cases_datetime, current_datetime, context):
    threats_date_filter = {"gte_datetime": stored_threats_datetime, "lte_datetime": current_datetime}
    cases_date_filter = {"gte_datetime": stored_cases_datetime, "lte_datetime": current_datetime}
    queue = asyncio.Queue()
    api_connector = AbnormalSoarConnectorAsync(API_TOKEN)
    threat_message_producer = asyncio.create_task(api_connector.get_all_threat_messages(threats_date_filter, queue, context))
    cases_producer = asyncio.create_task(api_connector.get_all_cases(cases_date_filter, queue, context))
    await asyncio.gather(threat_message_producer, cases_producer)

    if should_persist_data_to_sentinel():
        logging.info("Persisting to sentinel")
        sentinel_connector = AzureSentinelConnectorAsync(LOG_ANALYTICS_URI,SENTINEL_WORKSPACE_ID, SENTINEL_SHARED_KEY)
        consumers = [asyncio.create_task(consume(sentinel_connector, queue)) for _ in range(3)]
        await asyncio.gather(threat_message_producer, cases_producer)
        await queue.join()  # Implicitly awaits consumers, too
        for c in consumers:
            c.cancel()
        await sentinel_connector.flushall()
    
def should_persist_data_to_sentinel():
   return PERSIST_TO_SENTINEL == "true"
    

async def consume(sentinel_connector, queue):
    while True:
        message = await queue.get()
        try:
            await sentinel_connector.send(message)
        except Exception as e:
            logging.error(f"Sentinel send request Failed. Err: {e}")
        queue.task_done()

async def fetch_and_store_abnormal_data_v2(
    context: df.DurableOrchestrationContext,
    stored_threats_datetime: str,
    stored_cases_datetime: str,
):
    queue = asyncio.Queue()
    try:
        threats_ctx = get_context(stored_date_time=stored_threats_datetime)

        logging.info(f"Logging out threats ctx:: {threats_ctx.json(exclude={'API_TOKEN'})}")
        logging.info(
            f"Threats Timestamps (stored, current): ({stored_threats_datetime}, {threats_ctx.CURRENT_TIME})"
        )

        await get_threats(ctx=threats_ctx, output_queue=queue)
        logging.info("Fetching v2 threats completed")

    except Exception as e:
        logging.error("Failed to process v2 threats", exc_info=e)
    finally:
        threats_time = threats_ctx.CURRENT_TIME.strftime(TIME_FORMAT)
        set_date_on_entity(
            context=context,
            time=threats_time,
            resource=Resource.threats,
        )
        logging.info(f"Stored new v2 threats date: {threats_time}")

    try:
        cases_ctx = get_context(stored_date_time=stored_cases_datetime)
        
        logging.info(f"Logging out cases ctx:: {cases_ctx.json(exclude={'API_TOKEN'})}")
        logging.info(
            f"Cases Timestamps (stored, current): ({stored_cases_datetime}, {cases_ctx.CURRENT_TIME})"
        )

        await get_cases(ctx=cases_ctx, output_queue=queue)
        logging.info("Fetching v2 cases completed")

    except Exception as e:
        logging.error("Failed to process v2 cases", exc_info=e)
    finally:
        cases_time = cases_ctx.CURRENT_TIME.strftime(TIME_FORMAT)
        set_date_on_entity(
            context=context,
            time=cases_time,
            resource=Resource.cases,
        )
        logging.info(f"Stored new v2 cases date: {cases_time}")

    if should_persist_data_to_sentinel():
        logging.info("Persisting to sentinel")
        sentinel_connector = AzureSentinelConnectorAsync(
            LOG_ANALYTICS_URI, SENTINEL_WORKSPACE_ID, SENTINEL_SHARED_KEY
        )
        consumers = [
            asyncio.create_task(consume(sentinel_connector, queue)) for _ in range(3)
        ]
        await queue.join()  # Implicitly awaits consumers, too
        for c in consumers:
            c.cancel()
        await sentinel_connector.flushall()


main = df.Orchestrator.create(orchestrator_function)