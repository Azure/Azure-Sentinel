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

import azure.durable_functions as df

from .soar_connector_async import AbnormalSoarConnectorAsync
from .sentinel_connector_async import AzureSentinelConnectorAsync


API_TOKEN ="****"
SENTINEL_WORKSPACE_ID="****"
SENTINEL_SHARED_KEY="****"
LOG_ANALYTICS_URI = 'https://' + SENTINEL_WORKSPACE_ID + '.ods.opinsights.azure.com'

def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info(f"Executing orchestrator function")
    datetimeEntityId = df.EntityId("SoarDatetimeEntity", "latestDatetime")
    stored_datetime = yield context.call_entity(datetimeEntityId, "get")
    logging.info(f"retrieved stored datetime: {stored_datetime}")
    # stored_datetime = "2020-08-01T01:01:01Z"

    # threatCacheEntity = df.EntityId("SoarCacheEntity", Cacher.THREAT_MESSAGE_CACHE_KEY)
    # message_id_cache = yield context.call_entity(threatCacheEntity, "get")
    # logging.info(f"current message_id_cache: {message_id_cache}")

    # caseCacheEntity = df.EntityId("SoarCacheEntity", Cacher.CASE_CACHE_KEY)
    # case_id_cache = yield context.call_entity(caseCacheEntity, "get")
    # logging.info(f"current case_id_cache: {case_id_cache}")

    # dfCacher = Cacher(message_id_cache, case_id_cache)

    current_datetime=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    asyncio.run(transfer_abnormal_data_to_sentinel(stored_datetime, current_datetime))

    # context.signal_entity(threatCacheEntity, "set", dfCacher.new_message_ids)
    # logging.info(f"set new_message_ids to {dfCacher.new_message_ids}")

    # context.signal_entity(caseCacheEntity, "set", dfCacher.new_case_ids)
    # logging.info(f"set new_case_ids to {dfCacher.new_case_ids}")

    context.signal_entity(datetimeEntityId, "set", current_datetime)
    logging.info(f"set last_datetime to {current_datetime}")
    
async def transfer_abnormal_data_to_sentinel(stored_datetime, current_datetime):
    queue = asyncio.Queue()
    api_connector = AbnormalSoarConnectorAsync(API_TOKEN)
    sentinel_connector = AzureSentinelConnectorAsync(LOG_ANALYTICS_URI,SENTINEL_WORKSPACE_ID, SENTINEL_SHARED_KEY)
    threat_message_producer = asyncio.create_task(api_connector.get_all_threat_messages(stored_datetime, current_datetime, queue))
    cases_producer = asyncio.create_task(api_connector.get_all_cases(stored_datetime, current_datetime, queue))
    consumers = [asyncio.create_task(consume(sentinel_connector, queue)) for _ in range(3)]
    await asyncio.gather(threat_message_producer, cases_producer)
    await queue.join()  # Implicitly awaits consumers, too
    for c in consumers:
        c.cancel()
    await sentinel_connector.flushall()


# async def transfer_abnormal_data_to_sentinel(stored_datetime, current_datetime, dfCacher):
#     queue = asyncio.Queue()
#     api_connector = AbnormalSoarConnectorAsync(API_TOKEN)
#     sentinel_connector = AzureSentinelConnectorAsync(LOG_ANALYTICS_URI,SENTINEL_WORKSPACE_ID, SENTINEL_SHARED_KEY)
#     threat_message_producer = asyncio.create_task(api_connector.get_all_threat_messages(stored_datetime, current_datetime, queue, caching_func=dfCacher.cache_threat_message_ids))
#     cases_producer = asyncio.create_task(api_connector.get_all_cases(stored_datetime, current_datetime, queue, caching_func=dfCacher.cache_cases_ids))
#     consumers = [asyncio.create_task(consume(sentinel_connector, queue)) for _ in range(3)]
#     await asyncio.gather(threat_message_producer, cases_producer)
#     await queue.join()  # Implicitly awaits consumers, too
#     for c in consumers:
#         c.cancel()
#     await sentinel_connector.flushall()
    

async def consume(sentinel_connector, queue):
    while True:
        message = await queue.get()
        try:
            await sentinel_connector.send(message)
        except Exception as e:
            logging.error(f"Sentinel send request Failed. Err: {e}")
        queue.task_done()


class Cacher:
    THREAT_MESSAGE_CACHE_KEY = "threat_message_id_cache"
    CASE_CACHE_KEY = "case_id_cache"

    def __init__(self, message_id_cache, case_id_cache) -> None:
        self.message_id_cache = set(message_id_cache) if message_id_cache else set()
        self.new_message_ids = []
        self.case_id_cache = set(case_id_cache) if case_id_cache else set()
        self.new_case_ids = []

    def cache_threat_message_ids(self, message_ids):
        # return message_ids
        new_message_ids = []
        for id in message_ids:
            if id not in self.message_id_cache:
                self.message_id_cache.add(id)
                self.new_message_ids.append(id)
                new_message_ids.append(id)
        return new_message_ids
    
    def cache_cases_ids(self, case_ids):
        # return message_ids
        new_case_ids = []
        for id in case_ids:
            if id not in self.case_id_cache:
                self.case_id_cache.add(id)
                self.new_case_ids.append(id)
                new_case_ids.append(id)
        return new_case_ids


main = df.Orchestrator.create(orchestrator_function)