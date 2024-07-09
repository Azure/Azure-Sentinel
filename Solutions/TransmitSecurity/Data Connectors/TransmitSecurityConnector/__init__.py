import logging
import datetime
import json
import base64
import hashlib
import hmac
import requests
import os
import azure.functions as func
from typing import List, Dict, Optional


def build_signature(date: str, content_length: int, method: str, content_type: str, resource: str, shared_key: str, customer_id: str) -> str:
    x_headers = f'x-ms-date:{date}'
    string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = f"SharedKey {customer_id}:{encoded_hash}"
    return authorization


class TransmitSecurityConnector:
    def __init__(self, token_endpoint: str, client_id: str, client_secret: str):
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self) -> str:
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

    def fetch_events(self, token: str, endpoint: str) -> List[Dict]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()


def gen_chunks(data: List[Dict], chunksize: int = 100) -> List[Dict]:
    chunk = []
    for index, item in enumerate(data):
        if index % chunksize == 0 and index > 0:
            yield chunk
            chunk = []
        chunk.append(item)
    yield chunk


class AzureSentinel:
    def __init__(self, log_analytics_uri: str, shared_key: str, customer_id: str):
        self.log_analytics_uri = log_analytics_uri
        self.shared_key = shared_key
        self.customer_id = customer_id
        self.success_user_events = 0
        self.success_admin_events = 0
        self.failed_user_events = 0
        self.failed_admin_events = 0
        self.chunksize = 10000

    def post_results(self, data: List[Dict], table: str):
        for chunk in gen_chunks(data, chunksize=self.chunksize):
            body = json.dumps(chunk)
            self.post_data(body, len(chunk), table)

    def increase_counters(self, chunk_count: int, table: str, status: str):
        if table == "TransmitSecurityUserActivity" and status == "success":
            self.success_user_events += chunk_count
        elif table == "TransmitSecurityAdminActivity" and status == "success":
            self.success_admin_events += chunk_count
        elif table == "TransmitSecurityUserActivity" and status == "fail":
            self.failed_user_events += chunk_count
        elif table == "TransmitSecurityAdminActivity" and status == "fail":
            self.failed_admin_events += chunk_count

    def post_data(self, body: str, chunk_count: int, table: str):
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = build_signature(rfc1123date, content_length, method, content_type, resource, self.shared_key, self.customer_id)
        uri = f"{self.log_analytics_uri}{resource}?api-version=2016-04-01"
        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': table,
            'x-ms-date': rfc1123date
        }
        response = requests.post(uri, data=body, headers=headers)
        if 200 <= response.status_code <= 299:
            logging.info(f"Chunk processed ({chunk_count} events)")
            self.increase_counters(chunk_count, table, "success")
        else:
            logging.error(f"Error sending events to Azure Sentinel. Response code: {response.status_code}")
            self.increase_counters(chunk_count, table, "fail")


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.warning("The timer is past due!")

    logging.info(f"Python timer trigger function ran at {utc_timestamp}")
    
    try:
        user_activity_endpoint = os.getenv('TransmitSecurityUserActivityEndpoint', None)
        admin_activity_endpoint = os.getenv('TransmitSecurityAdminActivityEndpoint', None)
        token_endpoint = os.getenv('TransmitSecurityTokenEndpoint', '')
        client_id = os.getenv('TransmitSecurityClientID', '')
        client_secret = os.getenv('TransmitSecurityClientSecret', '')
        user_activity_tbl_name = "TransmitSecurityUserActivity"
        admin_activity_tbl_name = "TransmitSecurityAdminActivity"
        customer_id = os.getenv('WorkspaceID', '')
        shared_key = os.getenv('WorkspaceKey', '')
        log_analytics_uri = os.getenv('logAnalyticsUri', f'https://{customer_id}.ods.opinsights.azure.com')

        if not user_activity_endpoint and not admin_activity_endpoint:
            raise ValueError("One of the endpoints is required to be set.")
    
        connector = TransmitSecurityConnector(token_endpoint, client_id, client_secret)
        azure_sentinel = AzureSentinel(log_analytics_uri, shared_key, customer_id)
        
        token = connector.get_access_token()
        config = zip([user_activity_endpoint, admin_activity_endpoint], [user_activity_tbl_name, admin_activity_tbl_name])
        for endpoint, table in config:
            if endpoint:
                logging.info(f"Processing events for {table}")
                events = connector.fetch_events(token, endpoint)
                while events:
                    azure_sentinel.post_results(events, table)
                    events = connector.fetch_events(token, endpoint)

    except ValueError as ve:
        logging.error(f"Configuration error: {ve}")
        raise
    except requests.RequestException as re:
        logging.error(f"Request error: {re}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

    logging.info(f"Events processed successfully - Admin: {azure_sentinel.success_admin_events}, User: {azure_sentinel.success_user_events}")
    logging.info(f"Events failed - Admin: {azure_sentinel.failed_admin_events}, User: {azure_sentinel.failed_user_events}")