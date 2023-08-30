import json
import aiohttp
import asyncio
import logging
from collections import deque
import zlib

class AzureSentinelConnectorCLv2Async:
    def __init__(self, session: aiohttp.ClientSession, dce_endpoint, dcr_id, stream_name, azure_client_id, azure_client_secret, azure_tenant, queue_size=1200, queue_size_bytes=2 * (2**20)):
        self.dce_endpoint = dce_endpoint
        self.dcr_id = dcr_id
        self.stream_name = stream_name
        self.queue_size = queue_size
        self.queue_size_bytes = queue_size_bytes
        self._queue = deque()
        self.successful_sent_events_number = 0
        self.failed_sent_events_number = 0
        self.lock = asyncio.Lock()
        self.session = session
        self.AZURE_CLIENT_ID = azure_client_id
        self.AZURE_CLIENT_SECRET = azure_client_secret
        self.AZURE_TENANT_ID = azure_tenant
        self.MONITOR_RESOURCE = "https://monitor.azure.com"
        self.access_token_uri = "https://login.microsoftonline.com/{}/oauth2/token".format(self.AZURE_TENANT_ID)
        self.DCR_DATA_INGESTION_URL = "{}/dataCollectionRules/{}/streams/{}?api-version=2021-11-01-preview"

    # This method returns an access token for required resource
    # resource : string
    async def getAccessToken(self, resource: str):
        request_body = {
                'grant_type' : 'client_credentials',
                'client_id' : self.AZURE_CLIENT_ID,
                'resource' : resource,
                'client_secret' : self.AZURE_CLIENT_SECRET,
                'scope' : "user_impersonation"
            }
        result = await self._get_access_token(self.session, self.access_token_uri, request_body, {'Content-Type': 'application/x-www-form-urlencoded'})
        return json.loads(result)["access_token"]
    
    # This method is a helper function to call and return access_token
    # session : aiohttp session 
    # uri : string
    # body : dictionary
    # headers : dictionary
    async def _get_access_token(self, session, uri, body, headers):
        async with session.post(uri, data=body, headers=headers) as response:
            await response.text()
            if not (200 <= response.status <= 299):
                raise Exception("Error during creation of access token. Response code: {}".format(response.status))
        return await response.text()

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

    # This method sends data in bulk
    # event : List of dictionary
    async def sendBulk(self, events):
        if events:
            await self._flush(events)

    # This method sends data to ingestion endpoint
    async def flush(self):
        await self._flush(list(self._queue))

    # This method is a helper function which sends data to ingestion endpoint
    # list : List of dictionary
    async def _flush(self, data: list):
        if data:
            data = self._split_big_request(data)
            access_token = await self.getAccessToken(self.MONITOR_RESOURCE)
            await asyncio.gather(*[self._post_data(self.session, self.dce_endpoint, self.dcr_id, self.stream_name, access_token, d) for d in data])

    # This method is a helper function which posts data to ingestion endpoint
    # session : aiohttp session
    # dce_endpoint : string
    # dcr_id : string
    # stream_name : string
    # access_token : string
    # data : List of dictionary
    async def _post_data(self, session, dce_endpoint, dcr_id, stream_name, access_token, data):
        dceUri = self.DCR_DATA_INGESTION_URL.format(dce_endpoint,dcr_id,stream_name)
        headers={'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json', 'Content-Encoding': 'gzip'}
        await self._make_request(session, dceUri, self._compress_data(data), headers, len(data))
    
    # This method is a helper function which calls the post_data method for data ingestion
    # session : aiohttp session
    # uri : string
    # body : dictionary
    # headers : dictionary
    # dataLength : int
    async def _make_request(self, session, uri, body, headers, dataLength):
        async with session.post(uri, data=body, headers=headers) as response:
            await response.text()
            if not (200 <= response.status <= 299):
                self.failed_sent_events_number += dataLength
                raise Exception("Error during sending events to Microsoft Sentinel. Response code: {}".format(response.status))
            else:
                self.successful_sent_events_number += dataLength

    # This method is a compresses the data before ingestion
    # data : dictionary
    def _compress_data(self, data):
        body = json.dumps(data)
        zlib_mode = 16 + zlib.MAX_WBITS  # for gzip encoding
        _compress = zlib.compressobj(wbits=zlib_mode)
        compress_data = _compress.compress(bytes(body, encoding="utf-8"))
        compress_data += _compress.flush()
        logging.info("Data getting into LA after compression SizeInKB: {}".format(len(compress_data)/1024))
        return compress_data

    # This method returns true if queue size is less than max allowed queue size
    # queue : List of dictionary
    def _check_size(self, queue):
        data_bytes_len = len(json.dumps(queue).encode())
        #logging.info("Data size {}".format(data_bytes_len))
        return data_bytes_len < self.queue_size_bytes

    # This method splits big list into two equal halves
    # queue : List of dictionary
    def _split_big_request(self, queue):
        if self._check_size(queue):
            return [queue]
        else:
            #logging.info("Split is required")
            middle = int(len(queue) / 2)
            queues_list = [queue[:middle], queue[middle:]]
            return self._split_big_request(queues_list[0]) + self._split_big_request(queues_list[1])

    # This method returns successfully sent events
    def get_success_count(self):
        return self.successful_sent_events_number

    # This method returns the number of failed events
    def get_failure_count(self):
        return self.failed_sent_events_number