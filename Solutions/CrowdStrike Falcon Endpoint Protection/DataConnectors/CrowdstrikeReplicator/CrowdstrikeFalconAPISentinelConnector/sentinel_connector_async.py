import datetime
import logging
import json
import hashlib
import hmac
import base64
import aiohttp
import asyncio
from collections import deque


class AzureSentinelConnectorAsync:
    def __init__(self, session: aiohttp.ClientSession, log_analytics_uri, workspace_id, shared_key, log_type, queue_size=1000, queue_size_bytes=25 * (2**20)):
        self.log_analytics_uri = log_analytics_uri
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.queue_size = queue_size
        self.queue_size_bytes = queue_size_bytes
        self._queue = deque()
        self.successfull_sent_events_number = 0
        self.failed_sent_events_number = 0
        self.lock = asyncio.Lock()
        self.session = session

    async def send(self, event):
        events = None
        async with self.lock:
            self._queue.append(event)
            if len(self._queue) >= self.queue_size:
                events = list(self._queue)
                self._queue.clear()
        if events:
            await self._flush(events)

    async def flush(self):
        await self._flush(list(self._queue))

    async def _flush(self, data: list):
        if data:
            data = self._split_big_request(data)
            await asyncio.gather(*[self._post_data(self.session, self.workspace_id, self.shared_key, d, self.log_type) for d in data])

    def _build_signature(self, workspace_id, shared_key, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(workspace_id, encoded_hash)
        return authorization

    async def _post_data(self, session: aiohttp.ClientSession, workspace_id, shared_key, body, log_type):
        logging.debug('Start sending data to sentinel')
        events_number = len(body)
        body = json.dumps(body)
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self._build_signature(workspace_id, shared_key, rfc1123date, content_length, method, content_type, resource)
        uri = self.log_analytics_uri + resource + '?api-version=2016-04-01'

        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': log_type,
            'x-ms-date': rfc1123date
        }

        try_number = 1
        while True:
            try:
                if len(body) < 10:
                    logging.info(body)
                await self._make_request(session, uri, body, headers)
            except Exception as err:
                if try_number < 3:
                    logging.warning('Error while sending data to Azure Sentinel. Try number: {}. Trying one more time. {}'.format(try_number, err))
                    await asyncio.sleep(try_number)
                    try_number += 1
                else:
                    logging.error(str(err))
                    self.failed_sent_events_number += events_number
                    raise err
            else:
                logging.debug('{} events have been successfully sent to Azure Sentinel'.format(events_number))
                self.successfull_sent_events_number += events_number
                break


    async def _make_request(self, session, uri, body, headers):
        async with session.post(uri, data=body, headers=headers, ssl=False) as response:
            if not (200 <= response.status <= 299):
                raise Exception("Error during sending events to Azure Sentinel. Response code: {}".format(response.status))

    def _check_size(self, queue):
        data_bytes_len = len(json.dumps(queue).encode())
        return data_bytes_len < self.queue_size_bytes

    def _split_big_request(self, queue):
        if self._check_size(queue):
            return [queue]
        else:
            middle = int(len(queue) / 2)
            queues_list = [queue[:middle], queue[middle:]]
            return self._split_big_request(queues_list[0]) + self._split_big_request(queues_list[1])
