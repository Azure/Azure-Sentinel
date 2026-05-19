import logging
import os
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
    """Upload normalized anomaly data to Microsoft Sentinel."""
    filtered = [row for row in data if row]
    logging.info(f"Total anomaly events to upload: {len(filtered)}")
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
        logging.error(f"An error occurred writing checkpoint blob: {str(e)}")


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


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def decode_anomaly_type(anomaly_type: int) -> list[str]:
    """Decode bitmask anomaly type into human-readable flags.

    ANOMALY_FILE_ACTIVITY (15) is a composite of the four individual file-op
    flags (1|2|4|8). When all four are set we emit only the composite name to
    avoid redundant entries in the description.
    """
    FILE_OP_MASKS = {
        "ANOMALY_CREATED": 1,
        "ANOMALY_RENAMED": 2,
        "ANOMALY_MODIFIED": 4,
        "ANOMALY_DELETED": 8,
    }
    COMPOSITE_MASKS = {
        "ANOMALY_FILE_ACTIVITY": 15,
        "ANOMALY_APPLICATION_SIZE": 16,
        "ANOMALY_MIME_CLASSIFICATION": 32,
        "ANOMALY_RANSOMWARE": 64,
        "ANOMALY_FILE_DATA": 128,
        "ANOMALY_FILE_EXTENSION": 512,
        "ANOMALY_BACKUP_SIZE": 1024,
        "ANOMALY_DATA_WRITTEN": 4096,
        "ANOMALY_VSA_DATA": 8192,
        "ANOMALY_THIRD_PARTY_SOFTWARES": 65536,
    }
    decoded: list[str] = []

    # Composite flags first
    for key, mask in COMPOSITE_MASKS.items():
        if anomaly_type & mask == mask:
            decoded.append(key)

    # Only add individual file-op flags when the full composite (15) is NOT set
    if anomaly_type & 15 != 15:
        for key, mask in FILE_OP_MASKS.items():
            if anomaly_type & mask == mask:
                decoded.append(key)

    return decoded




def normalize_anomaly(anomaly: dict[str, Any]) -> dict[str, Any]:
    """Normalize threat indicator anomalies into the existing Sentinel event shape."""
    client = anomaly.get("client") or {}
    client_id = str(client.get("clientId") or "")
    client_name = str(client.get("clientName") or client.get("displayName") or "")
    ref_time = to_int(anomaly.get("refTime"), 0)
    anomaly_type = to_int(anomaly.get("anomalyType"), 0)
    decoded_types = decode_anomaly_type(anomaly_type)
    occurrence_dt = datetime.fromtimestamp(ref_time, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    severity = "Low"
    if anomaly_type & 64 == 64 or anomaly_type & 8192 == 8192:
        severity = "High"
    elif anomaly_type & 32 == 32 or anomaly_type & 512 == 512:
        severity = "Medium"

    description = (
        f"Threat indicator anomaly detected for client {client_name}. "
        f"anomalyType={anomaly_type}; flags={','.join(decoded_types) if decoded_types else 'UNKNOWN'}; "
        f"jobId={to_int(anomaly.get('jobId'), 0)}; createCount={to_int(anomaly.get('createCount'), 0)}; "
        f"deleteCount={to_int(anomaly.get('deleteCount'), 0)}; modCount={to_int(anomaly.get('modCount'), 0)}; "
        f"renameCount={to_int(anomaly.get('renameCount'), 0)}"
    )

    event_id = f"{client_id}-{to_int(anomaly.get('jobId'), 0)}-{ref_time}-{anomaly_type}"

    return {
        "EventId": event_id,
        "OccurrenceTime": occurrence_dt,
        "Severity": severity,
        "ClientId": client_id,
        "ClientName": client_name,
        "HostName": str(client.get("hostName") or client_name),
        "Program": "ThreatIndicators",
        "EventCode": str(anomaly_type),
        "Description": description,
        "CommcellName": str(client.get("displayName") or client_name),
        "UTCTimestamp": occurrence_dt,
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

        override_from_time_str = os.environ.get("OVERRIDE_FROM_TIME")
        if override_from_time_str:
            fromtime = int(override_from_time_str)
            logging.info(
                f"From Time: [{fromtime}], using OVERRIDE_FROM_TIME env var (blob checkpoint ignored)."
            )
        else:
            fromtime = read_blob(cs, container_name, blob_name)
            logging.debug(f"Read from time from blob: {fromtime}")

            if fromtime is None:
                fromtime = int((current_date - timedelta(days=7)).timestamp())
                logging.info(
                    f"From Time: [{fromtime}], blob doesn't exist, using 7 days backfill."
                )

        logging.info(
            f"Starts at: [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]"
        )

        anomaly_endpoint = f"{url}/Client/Anomaly"
        logging.info(f"Threat Indicators endpoint: {anomaly_endpoint}")

        response = requests.get(anomaly_endpoint, headers=headers)
        logging.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            anomaly_resp = response.json()
            error_resp = anomaly_resp.get("ErrorResponse") or {}
            error_code = to_int(error_resp.get("errorCode"), 0)
            if error_code != 0:
                logging.error(
                    f"Threat Indicators API returned error. errorCode={error_code}, errorMessage={error_resp.get('errorMessage', '')}"
                )
            else:
                anomaly_clients: list[dict[str, Any]] = anomaly_resp.get(
                    "anomalyClients", []
                )
                logging.info(
                    f"Anomaly clients returned by API: {len(anomaly_clients)}"
                )

                filtered_anomalies = [
                    a for a in anomaly_clients if to_int(a.get("refTime"), 0) >= fromtime
                ]
                logging.info(
                    f"Anomaly clients after refTime filtering (fromtime={fromtime}): {len(filtered_anomalies)}"
                )

                if filtered_anomalies:
                    logging.info("Uploading anomaly data to Microsoft Sentinel")
                    normalized_data = [
                        normalize_anomaly(anomaly) for anomaly in filtered_anomalies
                    ]
                    gen_chunks(normalized_data, logs_client)
                    logging.info("Job Succeeded")
                    logging.info("Function App Executed")
                else:
                    logging.info("No new anomalies found to ingest.")

                # Advance the checkpoint so the next run filters from now.
                # Skip when OVERRIDE_FROM_TIME is active — test runs must not
                # corrupt the production checkpoint.
                if not override_from_time_str:
                    upload_timestamp_blob(cs, container_name, blob_name, to_time + 1)
        elif response.status_code == 403:
            logging.error(
                f"Failed to get anomalies. Status code: 403. Reason: {response.text}"
            )
        else:
            logging.error(
                f"Failed to get anomalies. Status code: {response.status_code}"
            )
    except Exception as e:
        logging.error(f"HTTP request error: {e}")
        raise
