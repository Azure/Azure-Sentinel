import base64
import hashlib
import hmac
import datetime
import json
import requests


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

    # Required Function to create and invoke an API POST request to the Azure Log Analytics Data Collector API. Reference: https://docs.microsoft.com/azure/azure-functions/functions-reference-python#environment-variables
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
        response.raise_for_status()
