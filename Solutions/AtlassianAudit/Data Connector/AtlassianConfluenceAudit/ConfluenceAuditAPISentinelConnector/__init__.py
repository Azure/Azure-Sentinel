import json
import base64
import hmac
import hashlib
import os
import re
import logging
from datetime import datetime, timezone

import requests
import azure.functions as func

from .state_manager import StateManager


connection_string = os.environ['AzureWebJobsStorage']

atlassian_api_key = os.environ['ATLASSIAN_API_KEY']
atlassian_org_id = os.environ['ATLASSIAN_ORG_ID']
atlassian_org_name = os.environ['ATLASSIAN_ORG_NAME']
atlassian_uri_events = f"https://api.atlassian.com/admin/v1/orgs/{atlassian_org_id}/events"

la_customer_id = os.environ['WORKSPACE_ID'] 
la_shared_key = os.environ['WORKSPACE_KEY']
la_uri = f"https://{la_customer_id}.ods.opinsights.azure.com"
la_log_type = f"AtlassianAudit_{atlassian_org_name}"
la_max_request_size = 1000


pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(la_uri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")


def get_current_timestamp_utc_epoc() -> int:
    """Returns the current time in UTC as POSIX timestamp"""
    current_utc_time_timestamp = datetime.now(timezone.utc).timestamp()
    return int(current_utc_time_timestamp)


def get_result_request(from_time: str, cursor: str, uri: str, api_key: str) -> dict:
    """Returns 30 JSON results from given time and cursor position."""
    params = {"from": from_time}
    if cursor is not None:
        params["cursor"] = cursor

    try:
        response = requests.get(
                url=uri,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                params=params,
        )

        # Raise an exception if the response status code is not in the 200-299 range
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        raise Exception(f"Failed to get result: {err}")


def build_signature(customer_id: str, shared_key: str, date: str, content_length: int, method: str, content_type: str, resource: str) -> str:
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization


def post_data(body: str, logAnalyticsUri: str, log_type: str, customer_id: str, shared_key: str) -> int:
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri, data=body, headers=headers)
    return response.status_code


def get_results(from_time: str, uri: str, api_key: str) -> list:
    """Returns a list of JSON results from the given time."""
    results_list = []
    counter = 1

    try:
        response = get_result_request(from_time, None, uri, api_key)
        cursor = response.get('meta').get('next')
        data = response.get('data')
        if not data:
            return None
        results_list.extend(data)

        while cursor:
            logging.info(f"Getting results page: {counter}")
            response = get_result_request(from_time, cursor, uri, api_key)
            data = response.get('data')
            results_list.extend(data)
            cursor = response.get('meta').get('next')
            counter += 1

    except Exception as e:
        raise

    return results_list


def chunk_list(lst: list, chunk_size: int) -> list:
    """Chunk a given list into sublists of a specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def send_data(max_request_size: int, data: list, log_analytics_uri: str, log_type: str, customer_id: str, shared_key: str):
    """Send data in chunk_size chunks."""
    logging.info(f"Processing {len(data)} records with a max request size of {max_request_size}.")
    
    # Chunk the list of data based on the max request size
    chunked_list = chunk_list(data, max_request_size)
    logging.info(f"Got {len(chunked_list)} chunks.")
    
    # Iterate through each chunk and send the data
    for i, chunk in enumerate(chunked_list, start=1):
        logging.info(f"Posting request number {i} containing {len(chunk)} records")
        chunk_json = json.dumps(chunk)
        status_code = post_data(chunk_json, log_analytics_uri, log_type, customer_id, shared_key)
        
        # Raise an exception if the response code is not in the 2xx range
        if not (200 <= status_code < 300):
            raise Exception(f"Failed to post events. Response code: {status_code}")
    
    logging.info("Posted all events successfully.")



def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')

    try:
        current_utc_timestamp_epoc = get_current_timestamp_utc_epoc()
        current_utc_timestamp_epoc_ms = current_utc_timestamp_epoc * 10**3

        logging.info("The current epoch time in ms is: {}".format(current_utc_timestamp_epoc_ms))

        state = StateManager(connection_string=connection_string)
        last_saved_timestamp = state.get()

        # do we have a past time stored?
        if last_saved_timestamp is not None:
            logging.info("The last state saved time point is: {}".format(last_saved_timestamp))
        # get all events from the dawn of epoch time
        else:
            logging.info("There is no last time point stored in state, getting all events.")
            last_saved_timestamp = 0

        data = get_results(last_saved_timestamp, atlassian_uri_events, atlassian_api_key)
        if data:
            try:
                send_data(la_max_request_size, data, la_uri, la_log_type, la_customer_id, la_shared_key)
                logging.info("Successfully sent data.")

                state.post(str(current_utc_timestamp_epoc_ms))
                logging.info("Successfully saved the current run timestamp to state.")
            except Exception as e:
                logging.error(f"Failed to send data. Error: {e}")
                logging.error("The current timestamp was not saved to state. Exiting.")
                exit(1)
        else:
            logging.info("No data to process.")
            state.post(str(current_utc_timestamp_epoc_ms))
            logging.info("Successfully saved the current run timestamp to state.")
    except Exception as e:
        logging.error(f"Failed to get data. Error: {e}")
        logging.error("The current timestamp was not saved to state. Exiting.")
        exit(1)