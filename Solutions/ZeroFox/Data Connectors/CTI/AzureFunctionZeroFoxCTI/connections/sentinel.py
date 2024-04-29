import base64
import datetime
import hashlib
import hmac
import json
import logging
from threading import Thread
import requests


class SentinelConnector:
    def __init__(
        self,
        customer_id,
        shared_key,
        log_type,
        queue_size=200,
        bulks_number=10,
        queue_size_bytes=25 * (2**20),
    ):
        self.log_analytics_uri = f"https://{customer_id}.ods.opinsights.azure.com"
        self.customer_id = customer_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.queue_size = queue_size
        self.bulks_number = bulks_number
        self.queue_size_bytes = queue_size_bytes
        self._queue = []
        self._bulks_list = []
        self.successfull_sent_events_number = 0
        self.failed_sent_events_number = 0

    def send(self, event):
        self._queue.append(event)
        if len(self._queue) >= self.queue_size:
            self.flush(force=False)

    def flush(self, force=True):
        self._bulks_list.append(self._queue)
        if force:
            self._flush_bulks()
        else:
            if len(self._bulks_list) >= self.bulks_number:
                self._flush_bulks()

        self._queue = []

    def _flush_bulks(self):
        jobs = []
        for queue in self._bulks_list:
            if queue:
                queue_list = self._split_big_request(queue)
                for q in queue_list:
                    jobs.append(
                        Thread(
                            target=self._post_data,
                            args=(
                                self.customer_id,
                                self.shared_key,
                                q,
                                self.log_type,
                            ),
                        )
                    )

        for job in jobs:
            job.start()

        for job in jobs:
            job.join()

        self._bulks_list = []

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self.flush()

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
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def _post_data(self, customer_id, shared_key, body, log_type):
        events_number = len(body)
        body = json.dumps(body)
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
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

        response = requests.post(uri, data=body, headers=headers)
        if response.status_code >= 200 and response.status_code <= 299:
            logging.info(
                "{} events have been successfully sent to Microsoft Sentinel".format(
                    events_number
                )
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
