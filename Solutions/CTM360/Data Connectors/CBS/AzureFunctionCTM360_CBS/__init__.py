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
from time import time, localtime, strftime, gmtime
cbs_api_key = os.environ.get('api_key')
customer_id = os.environ.get('WorkspaceID')
shared_key = os.environ.get('WorkspaceKey')
logAnalyticsUri = os.environ.get('logAnalyticsUri')
olddate_from = os.environ.get('date_from')
olddate_to = os.environ.get('date_to')
backupflag = os.environ.get('backupflag')
log_type = 'CBSLog_Azure_1_CL'
MAX_RETRIES = 3
RETRY_INTERVAL_SECONDS = 60

connection_string = os.environ['AzureWebJobsStorage']

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(logAnalyticsUri))
if (not match):
    raise Exception("CBS Data Connector: Invalid Log Analytics Uri.")

bahrain_timezone_offset = 0


def format_iso8601(timestamp):
    return strftime("%d-%m-%Y %H:%M", gmtime(timestamp))


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):

    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + \
        str(content_length) + "\n" + content_type + \
        "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(
        decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)

    return authorization


def perform_request(url, headers):
    for attempt in range(MAX_RETRIES):
        try:
            # Set a timeout for the request
            response = requests.get(url, headers=headers, timeout=(5, 10))
            
            response.raise_for_status()  # Raises HTTPError for bad responses

            if response.status_code == 429:
                # Log specific error for HTTP status code 429 (Too Many Requests)
                logging.warning(
                    "HTTP status code 429 (Too Many Requests). Retrying...")
                time.sleep(RETRY_INTERVAL_SECONDS)
            else:
                message1 = response.json()
                


                post_data_to_sentinel(json.dumps(message1["incident_list"]))
                return True  # Request successful, break out of the loop

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {str(e)}")

            if "Max retries exceeded with url" in str(e):
                # Log specific error for Max retries exceeded with URL
                logging.error("Max retries exceeded with the URL.")
            elif "ReadTimeout" in str(e):
                # Log specific error for ReadTimeout
                logging.error("ReadTimeout occurred.")
            elif "HTTPSConnectionPool" in str(e) or "ConnectionError" in str(e):
                # Log specific error for ConnectionError
                logging.error("ConnectionError: HTTPSConnectionPool.")
            else:
                # Log other types of exceptions
                logging.error(f"Unhandled exception: {str(e)}")

            if attempt < MAX_RETRIES - 1:
                logging.info(
                    f"Retrying in {RETRY_INTERVAL_SECONDS} seconds...")
                time.sleep(RETRY_INTERVAL_SECONDS)
            else:
                logging.error(f"Max retries reached. Exiting.")
                return False  # Max retries reached, break out of the loop


def post_data_to_sentinel(body):

    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)

    signature = build_signature(
        customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)

    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    try:
        response = requests.post(uri, data=body, headers=headers)

        if (response.status_code >= 200 and response.status_code <= 299):
            logging.info(
                "CBS event successfully processed to the Azure Sentinel.")
            return response.status_code
        else:
            logging.error("Event is not processed into Azure. Response code: {}".format(
                response.status_code))
            return None
    except Exception:
        print(traceback.format_exc())




def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.warn('The timer is past due!')

    current_time = time()

    five_minutes_ago_bahrain = current_time - 5 * 60 + bahrain_timezone_offset

    current_time_str = format_iso8601(current_time + bahrain_timezone_offset)
    five_minutes_ago_str = format_iso8601(five_minutes_ago_bahrain)

    if backupflag == "true":
        state = StateManager(connection_string)
        statsusss= state.get()
        # if statsusss is not None:
        if statsusss in [None, "", "false"]:
            date_from = olddate_from
            date_to = olddate_to
            url = f"https://cbs.ctm360.com/api/v2/incidents?date_from={date_from}&date_to={date_to}"
            headers = {
                "accept": "application/json",
                "api-key": cbs_api_key
            }
            response = requests.get(url, headers=headers)
            logging.warn(url)
            message1 = response.json()
            
            
            if perform_request(url, headers):
                statsusss= state.post("true")
        else:
            
            date_from = five_minutes_ago_str
            date_to = current_time_str
            url = f"https://cbs.ctm360.com/api/v2/incidents?date_from={date_from}&date_to={date_to}"
            
            headers = {
                "accept": "application/json",
                "api-key": cbs_api_key
            }

            response = requests.get(url, headers=headers)
            logging.warn(url)
            message1 = response.json()
            
            perform_request(url, headers)

    else:
        date_from = five_minutes_ago_str
        date_to = current_time_str
        url = f"https://cbs.ctm360.com/api/v2/incidents?date_from={date_from}&date_to={date_to}"
        headers = {
            "accept": "application/json",
            "api-key": cbs_api_key
        }

        response = requests.get(url, headers=headers)
        logging.warn(url)

        message1 = response.json()
        
        perform_request(url, headers)
        
