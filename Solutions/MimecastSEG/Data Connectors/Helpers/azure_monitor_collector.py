import requests
import datetime
import hashlib
import hmac
import base64
import logging

from ..Models.Error.errors import AzureMonitorCollectorRequestError


class AzureMonitorCollector:
    """AzureMonitorCollector responsible for sending data from all functions to Log Analytics Workspace(Sentinel)."""

    @staticmethod
    def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
        """Generating proper Authorization header."""
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self, customer_id, shared_key, body, log_type):
        """Sending logs through proper API version to Log Analytics Workspace."""
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self.build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type,
                                         resource)
        uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': log_type,
            'x-ms-date': rfc1123date,
            'time-generated-field': 'time_generated'
        }

        response = requests.post(uri, data=body, headers=headers)
        if 200 <= response.status_code <= 299:
            logging.info('Logs sent successfully!')
        else:
            logging.error("Azure Monitor Collector response code: {}".format(response.status_code))
            raise AzureMonitorCollectorRequestError("Azure Monitor Collector response code: {}".format(response.status_code))
