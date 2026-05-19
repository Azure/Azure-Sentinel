import base64
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone

import requests
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import AzureAuthorityHosts, ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient

LOG_ANALYTICS_URI = (os.environ.get("LogAnalyticsUri") or "").strip()
SENTINEL_RESOURCE = "/api/logs"
if not LOG_ANALYTICS_URI:
    LOG_ANALYTICS_URI = f"https://{SENTINEL_CUSTOMER_ID}.ods.opinsights.azure.com{SENTINEL_RESOURCE}?api-version=2016-04-01"

# no longer needed
# SENTINEL_CUSTOMER_ID = (os.environ.get("WorkspaceId") or "").strip()
# SENTINEL_SHARED_KEY = (os.environ.get("WorkspaceKey") or "").strip()

# New Environment Variables
AZURE_TENANT_ID = (os.environ.get("TENANT_ID") or "").strip()
AZURE_CLIENT_ID = (os.environ.get("CLIENT_ID") or "").strip()
AZURE_CLIENT_SECRET = (os.environ.get("CLIENT_SECRET") or "").strip()
AZURE_ENDPOINT = (os.environ.get("DceUri") or "").strip()
DCR_ID = (os.environ.get("DcrImmutableId") or "").strip()


def post_data(events: list[dict], log_type_suffix: str):
    """
    Post data using the official Azure Monitor Ingestion SDK.
    """
    if not events:
        return

    try:
        # Use DefaultAzureCredential (supports Managed Identity in Azure)
        # credential = DefaultAzureCredential()

        logging.info("Creating the Client Secret Credential object.")
        creds = ClientSecretCredential(
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET,
            tenant_id=AZURE_TENANT_ID,
        )

        logging.info("Creating the Log Ingestion Client object.")
        client = LogsIngestionClient(
            endpoint=AZURE_ENDPOINT,
            credential=creds
        )

    except Exception as e:
        logging.error(
            f"{log_type_suffix.title()}: Failed to create Azure credential/client. "
            f"Check TENANT_ID, CLIENT_ID, CLIENT_SECRET, DCE_ENDPOINT. Error: {exc}"
        )
        logging.error(f"SentinelClient: Unexpected error: {e}")
        raise

    try:
        # The stream name must match your DCR definition
        # Usually "Custom-<TableName>_CL"
        stream_name = f"Custom-FncEvents{log_type_suffix.title()}_CL"

        logging.info(
            f"Uploading {len(events)} events using the new Log Ingestion Client.")

        client.upload(
            rule_id=DCR_ID,
            stream_name=stream_name,
            logs=events
        )

        logging.info(
            f"SentinelClient: Successfully uploaded {len(events)} events.")

    except ClientAuthenticationError as exc:
        logging.error(
            f"{log_type_suffix} : Authentication failed — verify CLIENT_ID, "
            f"CLIENT_SECRET, TENANT_ID, and that the App Registration has "
            f"'Monitoring Metrics Publisher' role on the DCR. Error: {exc}"
        )
        raise
    except HttpResponseError as e:
        logging.error(f"SentinelClient: HTTP error during upload: {e}")
        raise
    except Exception as e:
        logging.error(f"SentinelClient: Unexpected error: {e}")
        raise

# def post_data(events: list[dict], log_type_suffix: str):
#     """Build and send a request to the POST API"""
#     body = json.dumps(events)
#     method = "POST"
#     content_type = "application/json"
#     resource = "/api/logs"
#     rfc1123date = datetime.now(tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
#     content_length = len(body)
#     signature = _build_signature(
#         rfc1123date, content_length, method, content_type, resource
#     )
#     log_type = f"FncEvents{log_type_suffix.title()}"

#     headers = {
#         "content-type": content_type,
#         "Authorization": signature,
#         "Log-Type": log_type,
#         "x-ms-date": rfc1123date,
#     }
#     response = requests.post(LOG_ANALYTICS_URI, data=body, headers=headers)
#     if response.status_code >= 200 and response.status_code <= 299:
#         logging.info(f"SentinelClient: posted {len(events)} events to {log_type}")
#     else:
#         logging.error(
#             f"SentinelClient: failed to post events to Sentinel. Response code: {response.status_code}"
#         )
#         raise requests.exceptions.HTTPError(
#             f"SentinelClient: failed to post events to Sentinel. Response code: {response.status_code}"
#         )


def _build_signature(date, content_length, method, content_type, resource):
    """Build the API signature"""
    x_headers = "x-ms-date:" + date
    string_to_hash = (
        f"{method}\n{str(content_length)}\n{content_type}\n{x_headers}\n{resource}"
    )
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(SENTINEL_SHARED_KEY)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    ).decode()
    return f"SharedKey {SENTINEL_CUSTOMER_ID}:{encoded_hash}"
