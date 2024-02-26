import base64
import datetime
import hashlib
import hmac
import json
import logging
import requests
import os

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


class DataExporter:
    def __init__(self, workspace_id: str, shared_key: str, log_type: str):
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.content_type = 'application/json'
        self.chunk_size = 2000

    def _build_post_signature(self, content_length: int, resource: str) -> str:
        x_headers = 'x-ms-date:' + self.date
        string_to_hash = "POST" + "\n" + str(content_length) + "\n" + self.content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(self.workspace_id, encoded_hash)
        return authorization

    def _gen_chunks_to_object(self, data: list, chunk_size: int):
        chunk = []
        for index, line in enumerate(data):
            if index % chunk_size == 0 and index > 0:
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

    def post_data(self, data: list) -> int:
        body = json.dumps(data)
        resource = '/api/logs'
        content_length = len(body)
        signature = self._build_post_signature(content_length, resource)
        uri = 'https://' + self.workspace_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

        headers = {
            'content-type': self.content_type,
            'Authorization': signature,
            'Log-Type': self.log_type,
            'x-ms-date': self.date
        }
        try:
            response = requests.post(uri, data=body, headers=headers)

            if 200 <= response.status_code <= 299:
                logging.info("{} events was injected".format(len(data)))
                return response.status_code
            elif response.status_code == 401:
                logging.error(
                    "The authentication credentials are incorrect or missing. Error code: {}".format(response.status_code))
            else:
                logging.error(f"Something wrong. Error code: {response.status_code} Reason: {response.reason}")
            return response.status_code
        except Exception as err:
            logging.error(f"Something went wrong. Exception error text: {err}")

    def gen_chunks(self, data: list) -> None:
        chunk_size = 2000
        for chunk in self._gen_chunks_to_object(data, chunk_size=chunk_size):
            self.post_data(chunk)

    @staticmethod
    def send_dcr_data(data: list):
        endpoint = os.environ.get('DATA_COLLECTION_ENDPOINT')
        rule_id = os.environ.get('LOGS_DCR_RULE_ID')
        try:
            credential = DefaultAzureCredential()
            client = LogsIngestionClient(endpoint=endpoint, credential=credential)
            client.upload(rule_id=rule_id, stream_name=os.environ.get('LOGS_DCR_STREAM_NAME'), logs=data)
        except Exception as e:
            logging.error(f"Upload failed: {e}")
