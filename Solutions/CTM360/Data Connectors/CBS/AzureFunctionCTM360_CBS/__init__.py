import logging
import hashlib
import hmac
import os
import azure.functions as func
import json
import re
import base64
import requests
import datetime
import traceback
import time
from .state_manager import StateManager

# Environment Variables
cbs_api_key = os.environ.get('api_key')
customer_id = os.environ.get('WorkspaceID')
shared_key = os.environ.get('WorkspaceKey')
logAnalyticsUri = os.environ.get('logAnalyticsUri')
olddate_from = os.environ.get('date_from')   # Expected as epoch ms string for backup
olddate_to = os.environ.get('date_to')       # Expected as epoch ms string for static backup
backupflag = os.environ.get('backupflag')      # "true" means backup is desired
log_type = 'CBSLog_Azure_1_CL'
MAX_RETRIES = 10
RETRY_INTERVAL_SECONDS = 10
connection_string = os.environ['AzureWebJobsStorage']

logging.info("Initializing function...")

# Ensure logAnalyticsUri has a default if empty.
if not logAnalyticsUri or str(logAnalyticsUri).isspace():
    logAnalyticsUri = f'https://{customer_id}.ods.opinsights.azure.com'
    logging.info(f"logAnalyticsUri not provided. Using default: {logAnalyticsUri}")

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
if not re.match(pattern, str(logAnalyticsUri)):
    raise Exception("CBS Data Connector: Invalid Log Analytics Uri.")
else:
    logging.info("Log Analytics URI validated.")

# Timezone offset if needed (currently set to 0)
bahrain_timezone_offset = 0

# API base URL (Sentinel endpoint)
base_url = "https://cbs.ctm360.com/api/v2/sentinel"
logging.info(f"Using API base URL: {base_url}")

# Module configurations
module_configs = [
    {"module_type": "incidents", "max_hits": 10000},
    {"module_type": "malware_logs", "max_hits": 10000},
    {"module_type": "breached_credentials", "max_hits": 10000},
    {"module_type": "compromised_cards", "max_hits": 10000},
    {"module_type": "domain_infringement", "max_hits": 10000},
    {"module_type": "subdomain_infringement", "max_hits": 10000}
]

def format_iso8601(timestamp):
    return time.strftime("%d-%m-%Y %H:%M", time.gmtime(timestamp))

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    """
    Build the authorization signature for Azure Log Analytics.
    """
    x_headers = 'x-ms-date:' + date
    string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    ).decode()
    authorization = f"SharedKey {customer_id}:{encoded_hash}"
    return authorization

def parse_response_data(response_json):
    logging.debug(f"Parsing response JSON: {response_json}")
    if "hits" in response_json:
        return response_json["hits"]
    return [response_json]

def perform_request(url, headers):
    logging.info(f"Performing GET request to: {url}")
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=(5, 10))
            logging.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
            if response.status_code == 429:
                logging.warning("HTTP 429 (Too Many Requests) received. Retrying...")
                time.sleep(RETRY_INTERVAL_SECONDS)
            else:
                message_json = response.json()
                logging.debug(f"Response JSON: {message_json}")
                records = parse_response_data(message_json)
                post_data_to_sentinel(json.dumps(records))
                return True
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request attempt {attempt+1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Retrying in {RETRY_INTERVAL_SECONDS} seconds...")
                time.sleep(RETRY_INTERVAL_SECONDS)
            else:
                logging.error("Max retries reached. Exiting perform_request.")
                return False

def post_data_to_sentinel(body):
    """
    Send the final JSON payload to Azure Sentinel (Log Analytics Workspace).
    """
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    # Use UTC timestamp. (Your working code uses utcnow here.)
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(
        customer_id, shared_key, rfc1123date, content_length, method, content_type, resource
    )
    uri = f"{logAnalyticsUri}{resource}?api-version=2016-04-01"
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    logging.info(f"Posting data to Sentinel. URI: {uri}")
    try:
        response = requests.post(uri, data=body, headers=headers)
        logging.info(f"POST response code: {response.status_code}")
        if 200 <= response.status_code <= 299:
            logging.info("Data successfully sent to Azure Sentinel.")
            return response.status_code
        else:
            logging.error(f"Failed to send data. Response code: {response.status_code}")
            return None
    except Exception:
        logging.error("Exception occurred while posting data to Sentinel:")
        logging.error(traceback.format_exc())
        return None

def main(mytimer: func.TimerRequest) -> None:
    logging.info("Function execution started.")
    if mytimer.past_due:
        logging.warning("Timer is past due!")

    current_ms = int(time.time() * 1000)
    logging.info(f"Current timestamp (ms): {current_ms}")
    # Default: rolling window (last 5 minutes)
    timestamp_from = current_ms - (5 * 60 * 1000)
    timestamp_to = current_ms
    logging.info(f"Default rolling window: from {timestamp_from} to {timestamp_to}")

    if backupflag == "true":
        logging.info("Backup flag is true. Checking state for backup mode.")
        state = StateManager(connection_string)
        stored = state.get()  # Expected to be "true" or "false"
        logging.info(f"State retrieved: {stored}")
        if stored is None:
            stored = "true"
            logging.info("No state found; defaulting to backup mode (true).")
        if stored == "true":
            logging.info("Backup requested. Using provided backup dates.")
            try:
                timestamp_from = int(olddate_from)
                timestamp_to = int(olddate_to)
                logging.info(f"Using backup window: from {timestamp_from} to {timestamp_to}")
            except (TypeError, ValueError):
                logging.error("Invalid backup date values; falling back to rolling window.")
                timestamp_from = current_ms - (5 * 60 * 1000)
                timestamp_to = current_ms
            logging.info("Updating state to false after backup processing.")
            state.post("false")
        else:
            logging.info("Backup already processed; using rolling window.")
            timestamp_from = current_ms - (5 * 60 * 1000)
            timestamp_to = current_ms

    headers = {
        "accept": "application/json",
        "api-key": cbs_api_key
    }

    for config in module_configs:
        module_type = config["module_type"]
        max_hits = config["max_hits"]
        q_value = current_ms
        url = (f"{base_url}?date_from={timestamp_from}"
               f"&date_to={timestamp_to}"
               f"&module_type={module_type}"
               f"&max_hits={max_hits}"
               f"&q={q_value}")
        if module_type in ["domain_infringement", "subdomain_infringement"]:
            url += "&risk_score_min=0&risk_score_max=100"
        logging.warning(f"Request URL => {url}")
        success = perform_request(url, headers)
        if success:
            logging.info(f"Data successfully retrieved and posted for module_type: {module_type}")
        else:
            logging.error(f"Failed to retrieve data for module_type: {module_type}")
    logging.info("Function execution completed.")