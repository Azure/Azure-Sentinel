import requests
import datetime
import logging
import json
import hashlib
import hmac
import base64
import time

class AzureSentinelConnector:
    def __init__(self, log_analytics_uri, workspace_id, shared_key, log_type, queue_size=200, queue_size_bytes=25 * (2**20)):
        self.log_analytics_uri = log_analytics_uri
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.queue_size = queue_size
        self.bulks_number = 1
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
        for queue in self._bulks_list:
            if queue:
                queue_list = self._split_big_request(queue)
                for q in queue_list:
                    self._post_data(self.workspace_id, self.shared_key, q, self.log_type)

        self._bulks_list = []

    def is_empty(self):
        return not self._queue and not self._bulks_list

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self.flush()

    def _build_signature(self, workspace_id, shared_key, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(workspace_id, encoded_hash)
        return authorization

    def _post_data(self, workspace_id, shared_key, body, log_type):
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
                self._make_request(uri, body, headers)
            except Exception as err:
                if try_number < 3:
                    logging.warning('Error while sending data to Microsoft Sentinel. Try number: {}. {}'.format(try_number, err))
                    time.sleep(try_number)
                    try_number += 1
                else:
                    logging.error(str(err))
                    if not hasattr(self, "failed_sent_events_number"):
                        setattr(self, "failed_sent_events_number", 0)
                    
                    self.failed_sent_events_number += events_number
                    raise err
            else:
                logging.info('{} events have been successfully sent to Microsoft Sentinel'.format(events_number))
                self.successfull_sent_events_number += events_number
                break

    def _make_request(self, uri, body, headers):
        response = requests.post(uri, data=body, headers=headers)
        if not (200 <= response.status_code <= 299):
            raise Exception("Error during sending events to Microsoft Sentinel. Response code: {}".format(response.status_code))

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
