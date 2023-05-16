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

import azure.durable_functions as df

from .soar_connector_async import AbnormalSoarConnectorAsync
from .sentinel_connector_async import AzureSentinelConnectorAsync


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
    logging.info(f"Executing orchestrator function version 1.1")
    datetimeEntityId = df.EntityId("SoarDatetimeEntity", "latestDatetime")
    stored_datetime = yield context.call_entity(datetimeEntityId, "get")
    logging.info(f"retrieved stored datetime: {stored_datetime}")

    current_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    asyncio.run(transfer_abnormal_data_to_sentinel(stored_datetime, current_datetime))

    context.signal_entity(datetimeEntityId, "set", current_datetime)
    logging.info(f"set last_datetime to {current_datetime}")


async def transfer_abnormal_data_to_sentinel(stored_datetime, current_datetime):
    context = {"gte_datetime": stored_datetime, "lte_datetime": current_datetime}
    queue = asyncio.Queue()
    api_connector = AbnormalSoarConnectorAsync(API_TOKEN)
    sentinel_connector = AzureSentinelConnectorAsync(LOG_ANALYTICS_URI,SENTINEL_WORKSPACE_ID, SENTINEL_SHARED_KEY)
    threat_message_producer = asyncio.create_task(api_connector.get_all_threat_messages(context, queue))
    cases_producer = asyncio.create_task(api_connector.get_all_cases(context, queue))
    consumers = [asyncio.create_task(consume(sentinel_connector, queue)) for _ in range(3)]
    await asyncio.gather(threat_message_producer, cases_producer)
    await queue.join()  # Implicitly awaits consumers, too
    for c in consumers:
        c.cancel()
    await sentinel_connector.flushall()
    

async def consume(sentinel_connector, queue):
    while True:
        message = await queue.get()
        try:
            await sentinel_connector.send(message)
        except Exception as e:
            logging.error(f"Sentinel send request Failed. Err: {e}")
        queue.task_done()

main = df.Orchestrator.create(orchestrator_function)