import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import azure.functions as func
import requests
import urllib3
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
)
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from azure.monitor.ingestion import LogsIngestionClient
from azure.storage.blob import BlobServiceClient

urllib3.disable_warnings()

app = func.FunctionApp()

container_name = "sentinelcontainer"
blob_name = "timestamp-v2"

cs = os.environ.get("AzureWebJobsStorage")
if cs is None:
    raise ValueError("AzureWebJobsStorage environment variable is not set.")

backfill_days = int(
    os.environ.get("NumberOfDaysToBackfill", "7")
)  # Default to 7 days if not specified

# Azure Monitor Logs Ingestion API configuration
data_collection_endpoint = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT")
if data_collection_endpoint is None:
    raise ValueError("AZURE_DATA_COLLECTION_ENDPOINT environment variable is not set.")

data_collection_rule_id = os.environ.get("AZURE_DATA_COLLECTION_RULE_ID")
if data_collection_rule_id is None:
    raise ValueError("AZURE_DATA_COLLECTION_RULE_ID environment variable is not set.")

sentinel_table_name = os.environ.get("SENTINEL_TABLE_NAME", "CommvaultAlerts")
stream_name = f"Custom-{sentinel_table_name}"

key_vault_name = os.environ.get("KeyVaultName")
if key_vault_name is None:
    raise ValueError("KeyVaultName environment variable is not set.")

showAllEvents = os.environ.get("ShowAllEvents", "false").lower()

url = None
access_token = None
refresh_token = None
access_token_expiry = None
secret_client = None
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "SentinelDataConnector",
}


def is_access_token_expired_or_is_empty(expiry_time: int) -> bool:
    logging.info(
        f"Checking if access token is expired or empty. Expiry time: {expiry_time}, access_token_expiry: {access_token_expiry}"
    )
    if expiry_time is None or expiry_time == -1 or access_token_expiry == -1:
        logging.warning(
            "Access token expiry is None, empty, or -1. Will treat as expired."
        )
        return True
    current_time = datetime.now(timezone.utc).timestamp()
    if expiry_time <= current_time:
        logging.info(
            f"Access token expired. expiry_time: {expiry_time}, current_time: {current_time}"
        )
        return True
    return False


def refresh_access_token() -> str:
    global access_token, url, headers, refresh_token, access_token_expiry, secret_client
    try:
        renew_token_url = f"{url}/V4/AccessToken/Renew"
        token_body = {"accessToken": access_token, "refreshToken": refresh_token}
        logging.info(f"Attempting to refresh access token via API: {renew_token_url}")
        response = requests.post(renew_token_url, headers=headers, json=token_body)
        logging.info(f"Refresh access token response status: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("accessToken")
            refresh_token = response_data.get("refreshToken")
            access_token_expiry = response_data.get("tokenExpiryTimestamp")
            logging.info(f"Refreshed access token. New expiry: {access_token_expiry}")

            # Set the new values
            if secret_client is None:
                logging.error(
                    "Secret client is not initialized. Cannot store refreshed tokens in Key Vault."
                )
                raise Exception(
                    "Secret client is not initialized. Cannot store refreshed tokens in Key Vault."
                )
            secret_client.set_secret("access-token", access_token)
            secret_client.set_secret("token-expiry-timestamp", str(access_token_expiry))
            secret_client.set_secret("refresh-token", refresh_token)

            logging.info(
                "Stored refreshed access token, expiry, and refresh token in Key Vault."
            )
            return access_token
        elif response.status_code == 403:
            logging.error(
                f"Failed to renew access token. Status code: 403. Reason: {response.text}"
            )
            raise Exception(
                f"Failed to renew access token. Status code: 403. Reason: {response.text}"
            )
        elif response.status_code == 404:
            logging.error(f"Invalid Access Token. Please verify if the token is valid.")
            raise Exception(
                f"Invalid Access Token. Please verify if the token is valid."
            )
        else:
            logging.error(
                f"Failed to renew access token with status code: {response.status_code}. Reason: {response.text}"
            )
            raise Exception(
                f"Failed to renew access token with status code: {response.status_code}. Reason: {response.text}"
            )
    except Exception as e:
        logging.error(f"Error renewing access token: {e}")
        raise


def upload_to_sentinel(
    logs_client: LogsIngestionClient,
    logs: list[dict[str, Any]],
):
    """
    Upload logs to Microsoft Sentinel using Azure Monitor Logs Ingestion API.

    Args:
        logs_client: LogsIngestionClient instance
        logs: List of log dictionaries to upload
        chunk_count: Number of events being uploaded (for logging)
    """
    try:
        events_count = len(logs)
        logging.info(
            f"Uploading {events_count} events to Microsoft Sentinel via Logs Ingestion API"
        )
        logging.info(f"Using DCR: {data_collection_rule_id}, Stream: {stream_name}")

        logs_client.upload(
            rule_id=str(data_collection_rule_id), stream_name=stream_name, logs=logs  # type: ignore
        )

        logging.info(
            f"Successfully uploaded {events_count} events to Microsoft Sentinel"
        )
    except ClientAuthenticationError as e:
        logging.error(
            f"Authentication failed when uploading to Sentinel. Ensure Managed Identity has proper permissions on DCR. Error: {e}"
        )
        raise
    except HttpResponseError as e:
        logging.error(
            f"HTTP error during upload to Sentinel. Status: {e.status_code}, Reason: {e.reason}, Message: {e.message}"
        )
        raise
    except Exception as e:
        logging.error(f"Unexpected error during upload to Sentinel: {e}")
        raise


def gen_chunks(data: list[dict[str, Any]], logs_client: LogsIngestionClient):
    """Filter and upload data to Microsoft Sentinel"""
    target_event_codes = {
        "7:211",
        "7:212",
        "7:293",
        "7:269",
        "14:337",
        "14:338",
        "69:59",
        "7:333",
        "69:60",
        "35:5575",
        "35:5636",
        "7:349",
        "17:193",
        "17:195",
    }

    if showAllEvents == "true":
        filtered = [row for row in data if row]
    else:
        filtered = [
            row for row in data if row and row.get("EventCode") in target_event_codes
        ]

    logging.info(
        f"Total events after filtering: {len(filtered)}. showAllEvents={showAllEvents}"
    )

    if filtered:
        upload_to_sentinel(logs_client, filtered)


def upload_timestamp_blob(connection_string, container_name, blob_name, timestamp):
    """
    Upload timestamp to blob storage
    """
    try:
        timestamp_str = str(timestamp)
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.get_container_client(container_name)

        try:
            container_client.get_container_properties()
        except Exception:
            container_client.create_container()

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(timestamp_str, overwrite=True)
        logging.info(f"Timestamp data uploaded to blob: {blob_name}")
    except Exception as e:
        logging.info(f"An error occurred: {str(e)}")


def read_blob(connection_string, container_name, blob_name):
    """
    Read blob from blob storage
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        blob_data = blob_client.download_blob(encoding="UTF-8")
        content = blob_data.readall()
        timestamp = None
        if content:
            timestamp = int(content)
        logging.info(f"Timestamp read from blob {blob_name}: {timestamp}")
        return timestamp

    except ResourceNotFoundError:
        logging.info(f"Blob '{blob_name}' does not exist.")
        return None

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise


def extract_client_from_description(description: str) -> str | None:
    """Extract computer/client name from description using regex patterns."""
    patterns = [
        r"on the machine \[([^\]]+)\]",
        r"on client \[([^\]]+)\]",
        r"for client \[([^\]]+)\]",
        r"client \[([^\]]+)\]",
        r"machine \[([^\]]+)\]",
    ]
    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            return match.group(1)
    return None


def extract_hidden_info_from_description(description: str) -> dict[str, str | None]:
    """Extract hidden information from description within <span style="display: none"> tags."""
    hidden_info: dict[str, str | None] = {}

    # Find content inside <span style="display: none">...</span>
    span_pattern = r'<span\s+style\s*=\s*["\']display:\s*none["\']>\s*([^<]+)\s*</span>'
    span_match = re.search(span_pattern, description, re.IGNORECASE)

    if not span_match:
        return hidden_info

    span_content = span_match.group(1)

    # Extract clientId and clientName from within the hidden span
    patterns = {
        "clientId": r"ClientId:\[([^\]]+)\]",
        "hostName": r"ClientName:\[([^\]]+)\]",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, span_content)
        if match:
            hidden_info[key] = str(match.group(1))

    return hidden_info


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    client_entity = event.get("clientEntity") or {}
    client_name = extract_client_from_description(
        event.get("description", "")
    ) or client_entity.get("clientName", "")
    hidden_info = extract_hidden_info_from_description(event.get("description", ""))

    return {
        "EventId": str(event.get("id", "")),
        "OccurrenceTime": str(event.get("timeSource", "")),
        "Severity": str(event.get("severity", "")),
        "ClientId": hidden_info.get("clientId", ""),
        "ClientName": client_name,
        "HostName": hidden_info.get("hostName", client_name),
        "Program": event.get("subsystem") or "",
        "EventCode": event.get("eventCodeString") or "",
        "Description": event.get("description") or "",
        "CommcellName": client_entity.get("displayName") or "",
        "UTCTimestamp": str(event.get("timeSource", "")),
    }


def main(mytimer: func.TimerRequest) -> None:
    global access_token, url, headers, secret_client, access_token_expiry, refresh_token
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Executing Python timer trigger function.")

    try:
        # Initialize Azure credentials
        logging.debug("Initializing Azure credentials.")
        credential = None

        client_id = os.environ.get("AZURE_CLIENT_ID")
        if not client_id:
            logging.warning(
                "AZURE_CLIENT_ID environment variable not set. Falling back to DefaultAzureCredential."
            )
            credential = DefaultAzureCredential()
        else:
            credential = ManagedIdentityCredential(client_id=client_id)
            logging.info(f"Using ManagedIdentityCredential with client ID: {client_id}")

        # Initialize LogsIngestionClient for Azure Monitor Logs Ingestion API
        logging.info(
            f"Initializing LogsIngestionClient with endpoint: {data_collection_endpoint}"
        )
        logs_client = LogsIngestionClient(
            endpoint=str(data_collection_endpoint), credential=credential
        )

        # Initialize secret client for Key Vault
        secret_client = SecretClient(
            vault_url=f"https://{key_vault_name}.vault.azure.net", credential=credential
        )

        # 1. Fetch environment-endpoint-url from Key Vault
        secret_name = "environment-endpoint-url"
        secret = secret_client.get_secret(secret_name)
        url = secret.value
        if url is None:
            logging.error(f"Failed to retrieve {secret_name} from Key Vault")
            raise ValueError(f"Secret {secret_name} not found in Key Vault")
        logging.debug(f"Fetched environment endpoint URL: {url}")

        # 2. Fetch access-token from Key Vault
        secret_name = "access-token"
        access_token = secret_client.get_secret(secret_name).value
        if access_token is None:
            logging.error(f"Failed to retrieve {secret_name} from Key Vault")
            raise ValueError(f"Secret {secret_name} not found in Key Vault")
        headers["authtoken"] = (
            access_token  # sending both authtoken and bearer token, to support both SAAS and On-prem auth flow
        )
        headers["Authorization"] = f"Bearer {access_token}"
        logging.debug("Fetched access token.")

        # 3. Fetch refresh-token from Key Vault
        secret_name = "refresh-token"
        try:
            refresh_token = secret_client.get_secret(secret_name).value
            if refresh_token is None:
                logging.warning(
                    f"Refresh token not found in Key Vault under secret name: {secret_name}"
                )
            else:
                logging.debug("Fetched refresh token.")
        except Exception as e:
            logging.error(f"Failed to fetch refresh token: {e}")
            refresh_token = None

        # 4. Fetch token-expiry-timestamp if it exists
        secret_name = "token-expiry-timestamp"
        try:
            access_token_expiry_str = secret_client.get_secret(secret_name).value
            if access_token_expiry_str is None:
                logging.warning(
                    f"Token expiry timestamp not found in Key Vault under secret name: {secret_name}"
                )
                raise ValueError(f"Secret {secret_name} not found in Key Vault")
            access_token_expiry = int(access_token_expiry_str)
            logging.info(
                f"Fetched token-expiry-timestamp from Key Vault: {access_token_expiry}"
            )
        except Exception as e:
            access_token_expiry = -1
            logging.warning(
                f"Failed to fetch token-expiry-timestamp from Key Vault: {e}"
            )

        # Check if token is expired and refresh if needed
        if access_token_expiry == -1 or is_access_token_expired_or_is_empty(
            access_token_expiry
        ):
            logging.info("Token is expired or missing, refreshing access token")
            headers["authtoken"] = refresh_access_token()
            headers["Authorization"] = f"Bearer {headers['authtoken']}"
        else:
            logging.info("Access token is valid and not expired.")

        # Fetch company ID
        companyId_url = f"{url}/v2/WhoAmI"
        logging.debug(f"Fetching company ID from URL: {companyId_url}")
        company_response = requests.get(companyId_url, headers=headers)

        if company_response.status_code == 401:
            company_data_json = company_response.json()
            if "errorCode" in company_data_json and company_data_json["errorCode"] != 0:
                error_code = company_data_json["errorCode"]
                error_message = company_data_json.get("errorMessage")
                if error_message == "Access denied" and error_code == 5:
                    headers["authtoken"] = refresh_access_token()
                    headers["Authorization"] = f"Bearer {headers['authtoken']}"
                    company_response = requests.get(companyId_url, headers=headers)

        if company_response.status_code == 200:
            company_data_json = company_response.json()
            logging.info(f"Company Response: {company_data_json}")
            company_data = company_data_json.get("company", {})
            companyId = company_data.get("id")
            if companyId is not None:
                logging.debug(f"Fetched company ID: {companyId}")

                # Call SecurityPartners/Register/6
                audit_url = f"{url}/V4/Company/{companyId}/SecurityPartners/Register/6"
                logging.debug(f"Sending audit log request to URL: {audit_url}")
                audit_response = requests.put(audit_url, headers=headers)
                if audit_response.status_code == 200:
                    logging.info(
                        f"Audit Log request sent successfully. Response: {audit_response.json()}"
                    )
                elif audit_response.status_code == 403:
                    logging.error(
                        f"Failed to send Audit Log request. Status code: 403. Reason: {audit_response.text}"
                    )
                else:
                    logging.error(
                        f"Failed to send Audit Log request. Status code: {audit_response.status_code}"
                    )
        elif company_response.status_code == 403:
            logging.error(
                f"Failed to get Company ID. Status code: 403. Reason: {company_response.text}"
            )
        else:
            logging.error(
                f"Failed to get Company ID. Status code: {company_response.status_code}"
            )

        # Fetch fromtime from blob storage
        current_date = datetime.now(timezone.utc)
        to_time = int(current_date.timestamp())
        fromtime = read_blob(cs, container_name, blob_name)
        logging.debug(f"Read from time from blob: {fromtime}")

        if fromtime is None:
            fromtime = int((current_date - timedelta(days=backfill_days)).timestamp())
            logging.info(
                f"From Time: [{fromtime}], blob doesn't exist, using {backfill_days} days backfill."
            )
        else:
            fromtime_dt = datetime.fromtimestamp(fromtime, tz=timezone.utc)
            time_diff = current_date - fromtime_dt
            if time_diff > timedelta(days=backfill_days):
                updatedfromtime = int(
                    (current_date - timedelta(days=backfill_days)).timestamp()
                )
                logging.info(
                    f"From Time: [{updatedfromtime}], since the time read from blob: [{fromtime}] is older than {backfill_days} days."
                )
                fromtime = updatedfromtime
            elif time_diff < timedelta(minutes=5):
                updatedfromtime = int((current_date - timedelta(minutes=5)).timestamp())
                logging.info(
                    f"From Time: [{updatedfromtime}], since the time read from blob: [{fromtime}] is less than 5 minutes."
                )
                fromtime = updatedfromtime

        # Call events API
        ustring = ""
        if showAllEvents == "false":
            ustring = "/events?level=10&showInfo=false&showMinor=false&showMajor=true&showCritical=true&showAnomalous=true"
        else:
            ustring = "/events?level=10&showInfo=true&showMinor=true&showMajor=true&showCritical=true&showAnomalous=true"
        f_url = url + ustring

        max_fetch = 1000
        headers["pagingInfo"] = f"0,{max_fetch}"
        logging.debug(f"Set paging info in headers: {headers['pagingInfo']}")

        logging.info(
            f"Starts at: [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]"
        )
        event_endpoint = f"{f_url}&fromTime={fromtime}&toTime={to_time}"
        logging.info(f"Event endpoint: {event_endpoint}")

        response = requests.get(event_endpoint, headers=headers)
        logging.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            events = response.json()
            logging.info(
                "Events Data count : {}".format(len(events.get("commservEvents", [])))
            )
            data: list[dict[str, Any]] = events.get("commservEvents")
            # Push all commservEvents to log analytics workspace
            if data:
                logging.info("Uploading data to Microsoft Sentinel")
                data = [normalize_event(event) for event in data]
                gen_chunks(data, logs_client)
                logging.info("Job Succeeded")
                print("***Job Succeeded*****")
                logging.info("Function App Executed")
            else:
                print("No new events found.")
            upload_timestamp_blob(cs, container_name, blob_name, to_time + 1)
        elif response.status_code == 403:
            logging.error(
                f"Failed to get events. Status code: 403. Reason: {response.text}"
            )
        else:
            logging.error(f"Failed to get events. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"HTTP request error: {e}")
        raise
