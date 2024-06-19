import base64
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime

import requests

LOG_ANALYTICS_URI = (os.environ.get('LogAnalyticsUri') or "").strip()
SENTINEL_CUSTOMER_ID = (os.environ.get('WorkspaceId') or '').strip()
SENTINEL_RESOURCE = '/api/logs'
if not LOG_ANALYTICS_URI:
    LOG_ANALYTICS_URI = f'https://{SENTINEL_CUSTOMER_ID}.ods.opinsights.azure.com{SENTINEL_RESOURCE}?api-version=2016-04-01'
SENTINEL_SHARED_KEY = (os.environ.get('WorkspaceKey') or '').strip()

def post_data(events: list[dict], log_type_suffix: str):
    """Build and send a request to the POST API"""
    body = json.dumps(events)
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = _build_signature(rfc1123date, content_length, method, content_type, resource)
    log_type = f'FncEvents{log_type_suffix.title()}'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(LOG_ANALYTICS_URI, data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(f'SentinelClient: posted {len(events)} events to {log_type}')
    else:
        logging.error(f"SentinelClient: failed to post events to Sentinel. Response code: {response.status_code}")
        raise requests.exceptions.HTTPError(f"SentinelClient: failed to post events to Sentinel. Response code: {response.status_code}")

def _build_signature(date, content_length, method, content_type, resource):
    '''Build the API signature'''
    x_headers = 'x-ms-date:' + date
    string_to_hash = f'{method}\n{str(content_length)}\n{content_type}\n{x_headers}\n{resource}'
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(SENTINEL_SHARED_KEY)
    encoded_hash = base64.b64encode(hmac.new(
        decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    return f"SharedKey {SENTINEL_CUSTOMER_ID}:{encoded_hash}"
