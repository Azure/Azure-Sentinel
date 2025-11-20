from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import requests
import logging
import re
import azure.functions as func
import json
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
import os

requests.packages.urllib3.disable_warnings()
app = func.FunctionApp()

container_name = "sentinelcontainer"
blob_name = "timestamp-v2"

cs = os.environ.get('AzureWebJobsStorage')
if not cs:
    raise ValueError("AzureWebJobsStorage environment variable is not set.")

backfill_days = int(os.environ.get('NumberOfDaysToBackfill', "7")) # Default to 7 days if not specified

customer_id = os.environ.get('AzureSentinelWorkspaceId', '')
if not customer_id:
    raise ValueError("AzureSentinelWorkspaceId environment variable is not set.")

shared_key = os.environ.get('AzureSentinelSharedKey')
if not shared_key:
    raise ValueError("AzureSentinelSharedKey environment variable is not set.")

logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

key_vault_name = os.environ.get("KeyVaultName")

showAllEvents = os.environ.get("ShowAllEvents","false").lower()

url = None
access_token = None
refresh_token = None
access_token_expiry = None
secret_client = None
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "SentinelDataConnector"
}


def is_access_token_expired_or_is_empty(expiry_time: str) -> bool:
    logging.info(f"Checking if access token is expired or empty. Expiry time: {expiry_time}, access_token_expiry: {access_token_expiry}")
    if expiry_time is None or expiry_time == "" or access_token_expiry == -1:
        logging.warning("Access token expiry is None, empty, or -1. Will treat as expired.")
        return True
    current_time = datetime.now(timezone.utc).timestamp()
    if int(expiry_time) <= current_time:
        logging.info(f"Access token expired. expiry_time: {expiry_time}, current_time: {current_time}")
        return True
    return False


def refresh_access_token() -> str:
    global access_token, url, headers, refresh_token, access_token_expiry, secret_client
    try:
        renew_token_url = f"{url}/V4/AccessToken/Renew"
        token_body = {
            "accessToken": access_token,
            "refreshToken": refresh_token
        }
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
            secret_client.set_secret("access-token", access_token)
            secret_client.set_secret("token-expiry-timestamp", str(access_token_expiry))
            secret_client.set_secret("refresh-token", refresh_token)
            
            logging.info("Stored refreshed access token, expiry, and refresh token in Key Vault.")
            return access_token
        elif response.status_code == 403:
            logging.error(f"Failed to renew access token. Status code: 403. Reason: {response.text}")
            raise Exception(f"Failed to renew access token. Status code: 403. Reason: {response.text}")
        elif response.status_code == 404:
            logging.error(f"Invalid Access Token. Please verify if the token is valid.")
            raise Exception(f"Invalid Access Token. Please verify if the token is valid.")
        else:
            logging.error(f"Failed to renew access token with status code: {response.status_code}. Reason: {response.text}")
            raise Exception(f"Failed to renew access token with status code: {response.status_code}. Reason: {response.text}")
    except Exception as e:
        logging.error(f"Error renewing access token: {e}")
        raise


def build_signature(date, content_length, method, content_type, resource):
    """
    Build the authorization signature
    """
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


def post_data(body, chunk_count):
    """
    Post data to log analytics
    """
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    logging.info("Inside Post Data")
    rfc1123date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    logging.info(f"Date :- {rfc1123date}")
    content_length = len(body)
    signature = build_signature(rfc1123date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'
    logging.info(f"URL - {uri}")
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': "CommvaultSecurityIQ_CL",
        'x-ms-date': rfc1123date
    }
    logging.info(f"Request URL : {uri}")
    logging.info(f"Sending {chunk_count} events to Log Analytics")
    response = requests.post(uri, data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info("Chunk was processed {} events with status : {}".format(chunk_count, response.content))
    else:
        logging.error("Error during sending events to Microsoft Sentinel. Response code:{}, Response: {}".format(response.status_code, response.text))


def gen_chunks(data):
    """This method is used to get the chunks and post the data to log analytics work space"""
    # Event codes to filter for (matching the analytic rule)
    target_event_codes = ["7:211", "7:212", "7:293", "7:269", "14:337", "14:338", "69:59", "7:333", "69:60", "35:5575"]
    
    for chunk in gen_chunks_to_object(data, chunksize=10000):
        obj_array = []
        for row in chunk:
            if row != None and row != '':
                if showAllEvents == "true":
                    obj_array.append(row)
                else:
                    event_code = row.get("eventCodeString") or row.get("eventCode")
                    if event_code and event_code in target_event_codes:
                        logging.info(f"Processing target event with code: {event_code}")
                        obj_array.append(row)
                    else:
                        logging.debug(f"Skipping event with code: {event_code} (not in target list)")
        
        if obj_array:  # Only send if we have events to process
            body = json.dumps(obj_array)
            post_data(body, len(obj_array))


def gen_chunks_to_object(data, chunksize=100):
    """This is used to generate chunks to object based on chunk size"""
    chunk = []
    for index, line in enumerate(data):
        if (index % chunksize == 0 and index > 0):
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk


def upload_timestamp_blob(connection_string, container_name, blob_name, timestamp):
    """
    Upload timestamp to blob storage
    """
    try:
        timestamp_str = str(timestamp)
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
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
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob(encoding='UTF-8')
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


def main(mytimer: func.TimerRequest) -> None:
    global access_token, url, headers, secret_client, access_token_expiry, refresh_token
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Executing Python timer trigger function.')

    pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
    match = re.match(pattern, str(logAnalyticsUri))
    if not match:
        logging.info(f"Invalid url : {logAnalyticsUri}")
        raise Exception("Lookout: Invalid Log Analytics Uri.")
    try:
        # Initialize Azure credentials and secret client
        logging.debug("Initializing Azure credentials and secret client.")
        credential = None

        client_id = os.environ.get('AZURE_CLIENT_ID')
        if not client_id:
            logging.warning("AZURE_CLIENT_ID environment variable not set. Falling back to DefaultAzureCredential.")
            credential = ManagedIdentityCredential()
        else:
            credential = ManagedIdentityCredential(client_id=client_id)
            logging.info(f"Using ManagedIdentityCredential with client ID: {client_id}")
        
        secret_client = SecretClient(vault_url=f"https://{key_vault_name}.vault.azure.net", credential=credential)
        
        # 1. Fetch environment-endpoint-url from Key Vault
        secret_name = "environment-endpoint-url"
        secret = secret_client.get_secret(secret_name)
        if secret is None:
            logging.error(f"Failed to retrieve {secret_name} from Key Vault")
            raise ValueError(f"Secret {secret_name} not found in Key Vault")
        url = secret.value
        logging.debug(f"Fetched environment endpoint URL: {url}")

        # 2. Fetch access-token from Key Vault
        secret_name = "access-token"
        access_token = secret_client.get_secret(secret_name).value
        headers["authtoken"] = access_token #sending both authtoken and bearer token, to support both SAAS and On-prem auth flow
        headers["Authorization"] = f"Bearer {access_token}"
        logging.debug("Fetched access token.")

        # 3. Fetch refresh-token from Key Vault
        secret_name = "refresh-token"
        try:
            refresh_token = secret_client.get_secret(secret_name).value
            logging.debug("Fetched refresh token.")
        except Exception as e:
            logging.error(f"Failed to fetch refresh token: {e}")
            refresh_token = None

        # 4. Fetch token-expiry-timestamp if it exists
        secret_name = "token-expiry-timestamp"
        try:
            access_token_expiry = int(secret_client.get_secret(secret_name).value)
            logging.info(f"Fetched token-expiry-timestamp from Key Vault: {access_token_expiry}")
        except Exception as e:
            access_token_expiry = -1
            logging.warning(f"Failed to fetch token-expiry-timestamp from Key Vault: {e}")

        # Check if token is expired and refresh if needed
        if access_token_expiry == -1 or is_access_token_expired_or_is_empty(access_token_expiry):
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
                    logging.info(f"Audit Log request sent successfully. Response: {audit_response.json()}")
                elif audit_response.status_code == 403:
                    logging.error(f"Failed to send Audit Log request. Status code: 403. Reason: {audit_response.text}")
                else:
                    logging.error(f"Failed to send Audit Log request. Status code: {audit_response.status_code}")
        elif company_response.status_code == 403:
            logging.error(f"Failed to get Company ID. Status code: 403. Reason: {company_response.text}")
        else:
            logging.error(f"Failed to get Company ID. Status code: {company_response.status_code}")

        # Fetch fromtime from blob storage
        current_date = datetime.now(timezone.utc)
        to_time = int(current_date.timestamp())
        fromtime = read_blob(cs, container_name, blob_name)
        logging.debug(f"Read from time from blob: {fromtime}")

        if fromtime is None:
            fromtime = int((current_date - timedelta(days=backfill_days)).timestamp())
            logging.info(f"From Time: [{fromtime}], blob doesn't exist, using {backfill_days} days backfill.")
        else:
            fromtime_dt = datetime.fromtimestamp(fromtime, tz=timezone.utc)
            time_diff = current_date - fromtime_dt
            if time_diff > timedelta(days=backfill_days):
                updatedfromtime = int((current_date - timedelta(days=backfill_days)).timestamp())
                logging.info(f"From Time: [{updatedfromtime}], since the time read from blob: [{fromtime}] is older than {backfill_days} days.")
                fromtime = updatedfromtime
            elif time_diff < timedelta(minutes=5):
                updatedfromtime = int((current_date - timedelta(minutes=5)).timestamp())
                logging.info(f"From Time: [{updatedfromtime}], since the time read from blob: [{fromtime}] is less than 5 minutes.")
                fromtime = updatedfromtime

        # Call events API
        if showAllEvents == "false":
            ustring = f"/events?level=10&showInfo=false&showMinor=false&showMajor=true&showCritical=true&showAnomalous=true"
        else:
            ustring = f"/events?level=10&showInfo=true&showMinor=true&showMajor=true&showCritical=true&showAnomalous=false"
        f_url = url + ustring

        max_fetch = 1000
        headers["pagingInfo"] = f"0,{max_fetch}"
        logging.debug(f"Set paging info in headers: {headers['pagingInfo']}")

        logging.info(f"Starts at: [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]")
        event_endpoint = f"{f_url}&fromTime={fromtime}&toTime={to_time}"
        logging.info(f"Event endpoint: {event_endpoint}")

        response = requests.get(event_endpoint, headers=headers)
        logging.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            events = response.json()
            logging.info("Events Data count : {}".format(len(events.get("commservEvents",[]))))
            data = events.get("commservEvents")
            # Push all commservEvents to log analytics workspace
            if data:
                logging.info("Trying Post Data")
                gen_chunks(data)
                logging.info("Job Succeeded")
                print("***Job Succeeded*****")
                logging.info("Function App Executed")
            else:
                print("No new events found.")
            upload_timestamp_blob(cs, container_name, blob_name, to_time + 1)
        elif response.status_code == 403:
            logging.error(f"Failed to get events. Status code: 403. Reason: {response.text}")
        else:
            logging.error(f"Failed to get events. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"HTTP request error: {e}")
        raise