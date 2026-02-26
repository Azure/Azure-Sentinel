import json
from time import sleep, strptime
from .rest_api import get_alerts, get_logs
import requests
import datetime
import hashlib
import hmac
import base64
import logging
import os
from datetime import datetime, timedelta
from .state_manager import StateManager
import re
import azure.functions as func

env_id = os.environ['MuleSoftEnvId']
app_name = os.environ['MuleSoftAppName']
username = os.environ['MuleSoftUsername']
password = os.environ['MuleSoftPassword']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
log_type = "MuleSoft_Cloudhub"
connection_string = os.environ['AzureWebJobsStorage']
chunksize = 2000
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logging.warning("logAnalyticsUri is None, used default value.")
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(logAnalyticsUri))
if (not match):
    raise Exception("MuleSoft: Invalid Log Analytics Uri.")


def generate_date():
    current_time = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(minutes=10)
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info("The last time point is: {}".format(past_time))
    else:
        logging.info("There is no last time point, trying to get events for last hour.")
        past_time = (current_time - timedelta(minutes=60)).strftime("%s")
    state.post(current_time.strftime("%s"))
    return past_time, current_time.strftime("%s")


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


def post_data(chunk):
    body = json.dumps(chunk)
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    try:
        response = requests.post(uri, data=body, headers=headers)

        if 200 <= response.status_code <= 299:
            logging.info("{} events was injected".format(len(chunk)))
            return response.status_code
        elif response.status_code == 401:
            logging.error(
                "The authentication credentials are incorrect or missing. Error code: {}".format(response.status_code))
        else:
            logging.error("Something wrong. Error code: {}".format(response.status_code))
        return None
    except Exception as err:
        logging.error("Something wrong. Exception error text: {}".format(err))


def gen_chunks_to_object(data, chunk_size=100):
    chunk = []
    for index, line in enumerate(data):
        if index % chunk_size == 0 and index > 0:
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk


def gen_chunks(data):
    for chunk in gen_chunks_to_object(data, chunk_size=chunksize):
        post_data(chunk)


def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Starting program')
    start_time, end_time = generate_date()
    logging.info('Data processing. Period(UTC): {} - {}'.format(datetime.fromtimestamp(int(start_time)).strftime("%d.%m.%Y %H:%M:%S"), datetime.fromtimestamp(int(end_time)).strftime("%d.%m.%Y %H:%M:%S")))
    start_time_millisec = int(start_time) * 1000
    end_time_millisec = int(end_time) * 1000

    # get alerts
    logging.info('Collecting alerts...')
    alerts_json = get_alerts(username=username, password=password, app_name=app_name, env_id=env_id,
                             start_time=start_time_millisec, end_time=end_time_millisec)

    # get logs
    logging.info('Collecting logs...')
    logs_json = get_logs(username=username, password=password, env_id=env_id, start_time=start_time_millisec,
                         end_time=end_time_millisec)

    # Send data via data collector API
    for alert in alerts_json:
        alert["event_type"] = "alerts"
    for log in logs_json:
        log["event_type"] = "logs"
    gen_chunks(alerts_json + logs_json)
