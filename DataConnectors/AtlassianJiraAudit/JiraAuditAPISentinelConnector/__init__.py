import requests
import json
import datetime
from requests.auth import HTTPBasicAuth
import azure.functions as func
import base64
import hmac
import hashlib
import os
import logging
import re
from .state_manager import StateManager

customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
jira_token = os.environ['JiraAccessToken']
jira_username = os.environ['JiraUsername']
jira_homesite_name = os.environ['JiraHomeSiteName']
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
log_type = 'Jira_Audit'
jira_uri_audit = "https://" + jira_homesite_name + ".atlassian.net/rest/api/3/auditing/record"

if logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace():
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern, str(logAnalyticsUri))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


def generate_date() -> tuple:
    current_time = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=10)
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info(f"The last time point is: {past_time}")
    else:
        logging.info("There is no last time point, trying to get events for last hour.")
        past_time = (current_time - datetime.timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state.post(current_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return past_time, current_time.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_result_request(offset, limit, from_time, to_time):
    try:
        r = requests.get(url=jira_uri_audit,
                         headers={'Accept': 'application/json'},
                         auth=HTTPBasicAuth(jira_username, jira_token),
                         params={
                             "offset": offset,
                             "limit": limit,
                             "from": from_time,
                             "to": to_time
                         })
        if r.status_code == 200:
            return r.json().get("records")
        if r.status_code == 401:    # redundant to use an 'elif' after 'return', just use 'if'
            logging.error(
                f"The authentication credentials are incorrect or missing. HTTP error code: {r.status_code}")
        elif r.status_code == 403:
            logging.error("The user does not have the required permissions or Jira products are on free plans." +
                          "Audit logs are available when at least one Jira product is on a paid plan." +
                          f"HTTP error code: {r.status_code}")
        else:
            logging.error(f"Something wrong. HTTP error code: {r.status_code}")
    except Exception as err:
        logging.error(f"Something wrong. requests.get raised exception, error text: {err}")
    return None


def get_result(time_range: tuple) -> None:
    from_time = time_range[0]
    to_time = time_range[1]
    offset = 0
    limit = 1000
    element_count = None
    global_element_count = 0
    while element_count != 0:
        result = get_result_request(offset, limit, from_time, to_time)
        if result:
            element_count = len(result)
        else:
            break          # Amir: if no results from Jira, get out
        if offset == 0 and element_count == 0:
            logging.info(f"Jira audit logs were not found for time period: from {from_time} to {to_time}")
            break          # Amir: if no results from Jira, get out
        elif offset != 0 and element_count != 0:
            logging.info(f"Processing {element_count} events")
        offset = offset + limit
        if element_count > 0:
            post_status_code = post_data(json.dumps(result))
            if post_status_code is not None:
                global_element_count = global_element_count + element_count

    logging.info(f"Processed {global_element_count} events to Microsoft Sentinel." +
                 f" Time period: from {from_time} to {to_time}.")


def build_signature(x_customer_id, x_shared_key, date, content_length, method, content_type, resource) -> str:
    x_headers = 'x-ms-date:' + date
    string_to_hash = '\n'.join([method, str(content_length), content_type, x_headers, resource])
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(x_shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = f"SharedKey {x_customer_id}:{encoded_hash}"
    return authorization


def post_data(body):
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
    if 200 <= response.status_code <= 299:
        return response.status_code

    logging.warning(f"Events are not processed into Azure. Response code: {response.status_code}")
    return None


def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    get_result(generate_date())
