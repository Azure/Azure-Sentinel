import base64
import datetime
import hashlib
import hmac
import json
import math

import requests
from retry import retry
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.trace_utils.trace import trace_manager

logger = get_customized_json_logger()

# limit 30 MB per api call.
LOG_SIZE_LIMIT = 25 * 1024 * 1024


class LogAnalytics:
    def __init__(self, workspace_id, workspace_key, log_type):
        self.workspace_id = workspace_id
        self.workspace_key = workspace_key
        self.log_type = log_type

    # Azure Provided Code for posting data to Azure Log Ingestion
    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
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
        bytes_to_hash = bytes(string_to_hash, encoding='utf-8')
        decoded_key = base64.b64decode(self.workspace_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = "SharedKey {}:{}".format(self.workspace_id, encoded_hash)
        return authorization

    @retry(tries=3, delay=60)
    def post_data(self, data):
        body = json.dumps(data, sort_keys=True)
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self.build_signature(
            rfc1123date,
            content_length,
            method,
            content_type,
            resource,
        )
        uri = f'https://{self.workspace_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01'

        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': self.log_type,
            'x-ms-date': rfc1123date,
        }

        response = requests.post(uri, data=body, headers=headers)
        if response.status_code == requests.codes.request_entity_too_large:
            array_size = len(data)
            logger.warning(
                f'Get 413 error, retry with smaller array.\ndata count: {array_size}, content_length: {content_length}.'
                f'Task id: {trace_manager.task_id}'
            )
            batch_count = math.ceil(content_length / LOG_SIZE_LIMIT)
            batch_size = math.ceil(array_size / batch_count)
            for i in range(batch_count):
                batch_start = i * batch_size
                batch_end = batch_start + batch_size
                logger.warning(
                    f'Start batch send log, batch: {i}.'
                    f'Task id: {trace_manager.task_id}'
                )
                self.post_data(data[batch_start:batch_end])
        else:
            # raise error
            response.raise_for_status()
