import logging
import os

import azure.functions as func
import requests
from requests.models import HTTPError
import datetime
import time
import json
import hashlib
import hmac
import base64
import re
from azure.cosmosdb.table.tableservice import TableService

tenant_id = os.environ["TENANT_ID"]
grant_type = os.environ["GRANT_TYPE"]
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
access_key = os.environ["AZURE_STORAGE_ACCESS_KEY"]
connection_string = os.environ["AzureWebJobsStorage"]
storage_account_name = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
logAnalyticsUri = os.environ.get('logAnalyticsUri')

# Get the customer ID to your Log Analytics workspace Id.
customer_id = os.environ["CUSTOMER_ID"]

# For the shared key, use either the primary or the secondary Connected Sources client authentication key.
shared_key = os.environ["SHARED_KEY"]

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern, str(logAnalyticsUri))
if (not match):
    raise Exception("Invalid Log Analytics Uri.")


# Function to determine if the current timestamp should be used instead of the value stored in the checkpoint file.
# Will return 'true' if the checkpoint time is 1 or more days in the past.
def use_current(now, old) -> bool:
    ret = False

    try:
        current_time = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        current_time = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%SZ')

    try:
        old_time = datetime.datetime.strptime(old, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        old_time = datetime.datetime.strptime(old, '%Y-%m-%dT%H:%M:%SZ')

    diff = current_time - old_time
    delta_days = diff.days

    if (int(delta_days) > 0):
        ret = True

    return ret


# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource) -> str:
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


# Function to build and send a request to the API.
def post_data(customer_id, shared_key, body, log_type, logAnalyticsUri) -> None:
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
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
    if (response.status_code < 200 or response.status_code >= 300):
        logging.error("Unable to Write... " + format(response.status_code))

    # Executor


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due...')

    logging.info('Fetching data from IdentityNow at %s', utc_timestamp)

    url = f'https://{tenant_id}.api.identitynow.com/oauth/token'
    new_checkpoint_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=60)).isoformat() + "Z"
    checkpoint_table_name = 'checkpointTable'
    table_service = TableService(account_name=storage_account_name, account_key=access_key)
    task = {
        'PartitionKey': 'checkpointTime',
        'RowKey': '001',
        'createdTime': new_checkpoint_time
    }
    table_exists = table_service.exists(checkpoint_table_name)

    # Check if table already exists, if yes- get existing checkpoint time from the table entry.
    # If not then create table and insert the row containing new checkpoint time.
    if not table_exists:
        table_service.create_table(checkpoint_table_name)
        table_service.insert_entity(checkpoint_table_name, task)
        checkpoint_time = new_checkpoint_time
    else:
        returned_entity = table_service.get_entity(checkpoint_table_name, 'checkpointTime', '001')
        checkpoint_time = returned_entity.createdTime
        if use_current(new_checkpoint_time, checkpoint_time):
            checkpoint_time = new_checkpoint_time

    tokenparams = {
        'grant_type': grant_type,
        'client_id': client_id,
        'client_secret': client_secret
    }
    oauth_response = requests.request("POST", url=url, params=tokenparams)
    if oauth_response is not None:
        try:
            oauth_response.raise_for_status()
            access_token = oauth_response.json()["access_token"]
            headers = {
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + access_token
            }
        except (HTTPError, KeyError, ValueError):
            logging.error("No access token received..." + str(oauth_response.status_code))
            return 0

    partial_set = False
    audit_events = []

    # Search API results are slightly delayed, allow for 5 minutes though in reality.
    # This time will be much shorter. Cap query at checkpoint time to 5 minutes ago.
    search_delay_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=60)).isoformat() + "Z"

    # Number of Events to return per call to the search API.
    limit = int(os.environ["LIMIT"])

    while True:
        if partial_set == True:
            break

        # Standard query params, but include limit for result set size.
        queryparams = {
            "count": "true",
            "offset": "0",
            "limit": limit
        }
        query_checkpoint_time = checkpoint_time.replace('-', '\\-').replace('.', '\\.').replace(':', '\\:')
        query_search_delay_time = search_delay_time.replace('-', '\\-').replace('.', '\\.').replace(':', '\\:')

        logging.info(f'checkpoint_time {query_checkpoint_time} search_delay_time {query_search_delay_time}')

        # Search criteria - retrieve all audit events since the checkpoint time, sorted by created date
        searchpayload = {
            "queryType": "SAILPOINT",
            "query": {
                "query": f"created:>{query_checkpoint_time} AND created:<{query_search_delay_time}"
            },
            "queryResultFilter": {},
            "sort": ["created"],
            "searchAfter": []
        }
        audit_url = f'https://{tenant_id}.api.identitynow.com/v3/search/events'

        # Initiate request
        audit_events_response = requests.request("POST", url=audit_url, params=queryparams, json=searchpayload,
                                                 headers=headers)

        # API Gateway saturated / rate limit encountered.  Delay and try again. Delay will either be dictated by
        # IdentityNow server response or 5000 seconds
        if audit_events_response.status_code == 429:

            retryDelay = 5000
            retryAfter = audit_events_response.headers['Retry-After']
            if retryAfter is not None:
                retryDelay = int(retryAfter)

            logging.warning(f'429 - Rate Limit Exceeded, retrying in: {retryDelay}')
            time.sleep(retryDelay)

        elif audit_events_response.ok:

            # Check response headers to get total number of search results - if this value is 0 there is nothing to
            # parse, if it is less than the limit value then we are caught up to most recent, and can exit the query
            # loop
            x_total_count = int(audit_events_response.headers['X-Total-Count'])
            if x_total_count > 0:
                try:
                    if x_total_count < int(limit):
                        # Less than limit returned, caught up so exit.
                        partial_set = True

                    results = audit_events_response.json()
                    # Add this set of results to the audit events array
                    audit_events.extend(results)
                    current_last_event = audit_events[-1]
                    checkpoint_time = current_last_event['created']
                except KeyError:
                    logging.info("Response does not contain items...")
                break
            else:
                # Set partial_set to True to exit loop (no results)
                partial_set = True
        else:
            logging.info(f'Failure from server... " {audit_events_response.status_code}')
            # Forced Exit
            return 0

    # Iterate the audit events array and create events for each one.
    if len(audit_events) > 0:
        for audit_event in audit_events:
            data_json = json.dumps(audit_event)
            table_name = "SailPointIDN_Events"
            try:
                post_data(customer_id, shared_key, data_json, table_name, logAnalyticsUri)
            except Exception as error:
                logging.error("Unable to send data to Azure Log...")
                logging.error(error)

        # Get the created date of the last AuditEvent in this run and save it as the checkpoint time in the table.
        last_event = audit_events[-1]
        new_checkpoint_time = last_event['created']

        # Create an entry with new checkpoint time.
        task = {'PartitionKey': 'checkpointTime', 'RowKey': '001', 'createdTime': new_checkpoint_time}

        # Write new checkpoint time back to the table.
        table_service.insert_or_replace_entity(checkpoint_table_name, task)

        logging.info("Table successfully updated...")
    else:
        logging.info("No Events were returned...")
