# Taken from https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api

import base64
import datetime
import hashlib
import hmac
import logging

import requests
from esetinspect.eifunctions import exit_error

#####################
######Functions######
#####################

# Build the API signature
def build_signature(
    customer_id: str,
    shared_key: str,
    date: str,
    content_length: int,
    method: str,
    content_type: str,
    resource: str,
) -> str:
    x_headers = f"x-ms-date:{date}"
    string_to_hash = "\n".join([method, str(content_length), content_type, x_headers, resource])
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    ).decode()
    authorization = f"SharedKey {customer_id}:{encoded_hash}"
    return authorization


# Build and send a request to the POST API
def post_data(
    customer_id: str, shared_key: str, body: str, log_type: str, logAnalyticsUri: str
) -> None:
    method = "POST"
    content_type = "application/json"
    resource = "/api/logs"
    rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    content_length = len(body)
    signature = build_signature(
        customer_id, shared_key, rfc1123date, content_length, method, content_type, resource
    )

    uri = f"{logAnalyticsUri}{resource}?api-version=2016-04-01"

    headers = {
        "content-type": content_type,
        "Authorization": signature,
        "Log-Type": log_type,
        "x-ms-date": rfc1123date,
    }

    response = requests.post(uri, data=body, headers=headers)

    try:
        response.raise_for_status()
        logging.info("Accepted")
    except requests.exceptions.HTTPError as err:
        exit_error(f"Error while sending data through data-collector API:\n{err}")
