import aiohttp
import asyncio
from collections import deque
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient
from azure.core.exceptions import HttpResponseError
import logging

class AzureSentinelConnectorAsync:
    def __init__(self, session: aiohttp.ClientSession, dce_endpoint, dcr_id, stream_name, azure_client_id, azure_client_secret, azure_tenant, queue_size=4000):
        self.dce_endpoint = dce_endpoint
        self.dcr_id = dcr_id
        self.stream_name = stream_name
        self.queue_size = queue_size
        self._queue = deque()
        self.successful_sent_events_number = 0
        self.failed_sent_events_number = 0
        self.lock = asyncio.Lock()
        self.session = session
        self.credential = DefaultAzureCredential()
        self.AZURE_CLIENT_ID = azure_client_id
        self.AZURE_CLIENT_SECRET = azure_client_secret
        self.AZURE_TENANT_ID = azure_tenant
        self.access_token_uri = "https://login.microsoftonline.com/{}/oauth2/token".format(self.AZURE_TENANT_ID)
        self.DCR_DATA_INGESTION_URL = "{}/dataCollectionRules/{}/streams/{}?api-version=2021-11-01-preview"
    

    # This method collects data coming in based on size of the queue
    # event : dictionary
    async def send(self, event):
        events = None
        async with self.lock:
            self._queue.append(event)
            if len(self._queue) >= self.queue_size:
                events = list(self._queue)
                self._queue.clear()
        if events:
            await self._flush(events)

    # This method sends data to ingestion endpoint. Send whatever is accumulated till now.
    async def flush(self):
        await self._flush(list(self._queue))

    # This method is a helper function which sends data to ingestion endpoint
    # list : List of dictionary
    async def _flush(self, data: list):
        if data:
            await self._post_data(self.dce_endpoint, self.dcr_id, self.stream_name, self.credential, data)
            self._queue.clear()

    # This method is a helper function which posts data to ingestion endpoint
    # session : aiohttp session
    # dce_endpoint : string
    # dcr_id : string
    # stream_name : string
    # credential : string
    # data : List of dictionary
    async def _post_data(self, dce_endpoint, dcr_id, stream_name, credential, data):
        client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential, logging_enable=True)
        async with client:
            try:
                await client.upload(rule_id=dcr_id, stream_name=stream_name, logs=data)                
            except HttpResponseError as e:
                logging.error(f"Upload failed: {e.message}, status code is {e.status_code}")  
            except Exception as e:
                # Handle any other exceptions
                print(f"An unexpected error occurred: {str(e)}")                  
