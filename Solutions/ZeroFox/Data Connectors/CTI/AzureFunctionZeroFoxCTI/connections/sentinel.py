import asyncio
import base64
import hashlib
import hmac
import json
import logging
from collections import deque
from datetime import datetime, timezone

import aiohttp


class SentinelConnector:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        customer_id,
        shared_key,
        log_type,
        queue_size=2000,
        queue_size_bytes=25 * (2**20),
    ):
        self.log_analytics_uri = f"https://{customer_id}.ods.opinsights.azure.com"
        self.customer_id = customer_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.queue_size = queue_size
        self.queue_size_bytes = queue_size_bytes
        self._queue = deque()
        self.lock = asyncio.Lock()
        self.successfull_sent_events_number = 0
        self.failed_sent_events_number = 0
        self.session = session

    async def send(self, batch):
        self._queue.extend(batch)
        queue_size = len(self._queue)
        if queue_size >= self.queue_size:
            await self.flush()
            self._queue.clear()

    async def flush(self):
        await self._flush(list(self._queue))

    async def _flush(self, data: list):
        if not data:
            return
        split_data = self._split_big_request(data)
        await asyncio.gather(
            *[
                self._post_data(
                    session=self.session,
                    customer_id=self.customer_id,
                    shared_key=self.shared_key,
                    body=d,
                    log_type=self.log_type,
                )
                for d in split_data
            ]
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        await self.flush()

    def _build_signature(
        self,
        customer_id,
        shared_key,
        date,
        content_length,
        method,
        content_type,
        resource,
    ):
        x_headers = "x-ms-date:" + date
        string_to_hash = (
            method
            + "\n"
            + str(content_length)
            + "\n"
            + content_type
            + "\n"
            + x_headers
            + "\n"
            + resource
        )
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = f"SharedKey {customer_id}:{encoded_hash}"
        return authorization

    async def _post_data(
        self, session: aiohttp.ClientSession, customer_id, shared_key, body, log_type
    ):
        events_number = len(body)
        body = json.dumps(body)
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_length = len(body)
        signature = self._build_signature(
            customer_id,
            shared_key,
            rfc1123date,
            content_length,
            method,
            content_type,
            resource,
        )
        uri = self.log_analytics_uri + resource + "?api-version=2016-04-01"

        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date,
        }

        async with session.post(uri, data=body, headers=headers) as response:
            if 200 <= response.status <= 299:
                logging.info(
                    f"{events_number} events have been successfully sent to Microsoft Sentinel"
                )
                self.successfull_sent_events_number += events_number
            else:
                logging.error(
                    f"Error during sending events to Microsoft Sentinel. Response code: {response.status_code}, with message: {response.text}"
                )
                self.failed_sent_events_number += events_number

    def _check_size(self, queue):
        data_bytes_len = len(json.dumps(queue).encode())
        return data_bytes_len < self.queue_size_bytes

    def _split_big_request(self, queue):
        if self._check_size(queue):
            return [queue]
        else:
            middle = int(len(queue) / 2)
            queues_list = [queue[:middle], queue[middle:]]
            return self._split_big_request(queues_list[0]) + self._split_big_request(
                queues_list[1]
            )
