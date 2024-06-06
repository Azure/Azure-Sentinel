import logging
import datetime
import json
import base64
import hashlib
import hmac
import requests
import os
import azure.functions as func

# Environment variables
customer_id = os.getenv('WorkspaceID')
shared_key = os.getenv('WorkspaceKey')
log_analytics_uri = os.getenv('logAnalyticsUri', f'https://{customer_id}.ods.opinsights.azure.com')


class TransmitSecurityConnector:
    def __init__(self):
        self.token_endpoint = os.getenv('TransmitSecurityTokenEndpoint')
        self.events_endpoint = os.getenv('TransmitSecurityEventsEndpoint')
        self.client_id = os.getenv('TransmitSecurityClientID')
        self.client_secret = os.getenv('TransmitSecurityClientSecret')
        self.results_array = []

    def get_access_token(self):
        response = requests.post(
            self.token_endpoint,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def fetch_events(self):
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(self.events_endpoint, headers=headers)
        response.raise_for_status()
        self.results_array.extend(response.json())


def gen_chunks(data, chunksize=100):
    chunk = []
    for index, item in enumerate(data):
        if index % chunksize == 0 and index > 0:
            yield chunk
            chunk = []
        chunk.append(item)
    yield chunk


def build_signature(date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = f"SharedKey {customer_id}:{encoded_hash}"
    return authorization


class AzureSentinel:
    def __init__(self):
        self.log_analytics_uri = log_analytics_uri
        self.success_processed = 0
        self.fail_processed = 0
        self.table_name = "TransmitSecurity"
        self.chunksize = 10000

    def post_results(self, data):
        for chunk in gen_chunks(data, chunksize=self.chunksize):
            body = json.dumps(chunk)
            self.post_data(body, len(chunk))

    def post_data(self, body, chunk_count):
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = build_signature(rfc1123date, content_length, method, content_type, resource)
        uri = f"{self.log_analytics_uri}{resource}?api-version=2016-04-01"
        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': self.table_name,
            'x-ms-date': rfc1123date
        }
        response = requests.post(uri, data=body, headers=headers)
        if 200 <= response.status_code <= 299:
            logging.info(f"Chunk processed ({chunk_count} events)")
            self.success_processed += chunk_count
        else:
            logging.error(f"Error sending events to Azure Sentinel. Response code: {response.status_code}")
            self.fail_processed += chunk_count


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.warning("The timer is past due!")

    logging.info(f"Python timer trigger function ran at {utc_timestamp}")
    logging.info("Starting program")

    connector = TransmitSecurityConnector()
    azure_sentinel = AzureSentinel()

    connector.fetch_events()
    azure_sentinel.post_results(connector.results_array)

    logging.info(f"Total events processed successfully: {azure_sentinel.success_processed}, failed: {azure_sentinel.fail_processed}")
