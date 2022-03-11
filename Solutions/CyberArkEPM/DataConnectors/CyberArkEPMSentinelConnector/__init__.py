import requests
import datetime
import hashlib
import hmac
import base64
import logging
from .pyepm import getAggregatedEvents, getDetailedRawEvents, epmAuth, getSetsList
import os
from datetime import datetime, timedelta
import json
from .state_manager import StateManager
import re
import azure.functions as func

dispatcher = os.environ['CyberArkEPMServerURL']
username = os.environ['CyberArkEPMUsername']
password = os.environ['CyberArkEPMPassword']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
log_type = "CyberArkEPM"
connection_string = os.environ['AzureWebJobsStorage']
chunksize = 2000
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("CyberArkEPM: Invalid Log Analytics Uri.")

def generate_date():
    current_time = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(minutes=10)
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info("The last time point is: {}".format(past_time))
    else:
        logging.info("There is no last time point, trying to get events for last hour.")
        past_time = (current_time - timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state.post(current_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return past_time, current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
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
    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info("{} events was injected".format(len(chunk)))
        return response.status_code
    else:
        logging.warn("Events are not processed into Azure. Response code: {}".format(response.status_code))
        return None

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

def get_events(func_name, auth, filter_date, set_id, next_cursor="start"):
    events_json = func_name(epmserver=auth.json()["ManagerURL"],
                            epmToken=auth.json()['EPMAuthenticationResult'],
                            authType='EPM', setid=set_id['Id'],
                            data=filter_date,
                            next_cursor=next_cursor).json()

    if events_json["nextCursor"]:
        response_json = get_events(auth=auth, filter_date=filter_date, set_id=set_id, func_name=func_name,
                                   next_cursor=events_json["nextCursor"])
        events_json["events"] += response_json["events"]
    return events_json

def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    start_time, end_time = generate_date()
    logging.info('Data processing. Period(UTC): {} - {}'.format(start_time, end_time))
    auth = epmAuth(dispatcher=dispatcher, username=username, password=password)
    sets_list = getSetsList(epmserver=dispatcher, epmToken=auth.json()['EPMAuthenticationResult'], authType='EPM')
    filter_date = '{"filter": "eventDate GE ' + str(start_time) + ' AND eventDate LE ' + end_time + '"}'

    for set_id in sets_list.json()["Sets"]:
        aggregated_events_json = get_events(func_name=getAggregatedEvents, auth=auth, filter_date=filter_date,
                                            set_id=set_id)
        raw_events_json = get_events(func_name=getDetailedRawEvents, auth=auth, filter_date=filter_date, set_id=set_id)

    # Send data via data collector API
    aggregated_events = aggregated_events_json["events"]
    raw_events = raw_events_json["events"]
    for aggregated_event in aggregated_events:
        aggregated_event["event_type"] = "aggregated_events"
    for raw_event in raw_events:
        raw_event["event_type"] = "raw_event"
    gen_chunks(aggregated_events + raw_events)
