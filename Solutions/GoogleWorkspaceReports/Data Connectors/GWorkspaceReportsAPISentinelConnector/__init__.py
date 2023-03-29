from __future__ import print_function
import pickle
from googleapiclient.discovery import build
import datetime
import json
import base64
import hashlib
import hmac
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import azure.functions as func
import logging
import os
import time
import re
from .state_manager import StateManager

customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
pickle_str = os.environ['GooglePickleString']
pickle_string = base64.b64decode(pickle_str)
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']
activities = [
            "access_transparency", 
            "admin",
            "calendar",
            "chat",
            "drive",
            "gcp",
            "gplus",
            "groups",
            "groups_enterprise",
            "jamboard", 
            "login", 
            "meet", 
            "mobile", 
            "rules", 
            "saml", 
            "token", 
            "user_accounts", 
            "context_aware_access", 
            "chrome", 
            "data_studio"
            ]

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Google Workspace Reports: Invalid Log Analytics Uri.")

def get_credentials():
    creds = None
    if pickle_string:
        try:
            creds = pickle.loads(pickle_string)
        except Exception as pickle_read_exception:
            logging.error('Error while loading pickle string: {}'.format(pickle_read_exception))
    else:
        raise Exception("Google Workspace Reports: Pickle_string is empty. Exit.")
    return creds

def generate_date():
    current_time = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=10)
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info("The last time point is: {}".format(past_time))
    else:
        logging.info("There is no last time point, trying to get events for last hour.")
        past_time = (current_time - datetime.timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state.post(current_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return (past_time, current_time.strftime("%Y-%m-%dT%H:%M:%SZ"))

def get_result(activity,start_time, end_time):
    result_activities = []
    service = build('admin', 'reports_v1', credentials=creds, cache_discovery=False)
    results = service.activities().list(userKey='all', applicationName=activity,
                                              maxResults=1000, startTime=start_time, endTime=end_time).execute()
    next_page_token = results.get('nextPageToken', None)
    result = results.get('items', [])
    result_activities.extend(result)
    while next_page_token is not None:
        results = service.activities().list(userKey='all', applicationName=activity,
                                            maxResults=1000, startTime=start_time, endTime=end_time, pageToken=next_page_token).execute()
        next_page_token = results.get('nextPageToken', None)
        result = results.get('items', [])
        result_activities.extend(result)
    if result_activities == None or len(result_activities) == 0:
        logging.info("Logs not founded for {} activity".format(activity))
        logging.info("Activity - {}, processing {} events)".format(activity, len(result_activities)))
    else:
        logging.info("Activity - {}, processing {} events)".format(activity, len(result_activities)))
        return result_activities

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

def post_data(customer_id, shared_key, body, log_type):
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
        'x-ms-date': rfc1123date,
        'time-generated-field': "id_time"
    }
    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info("Logs with {} activity was processed into Azure".format(log_type))
    else:
        logging.warn("Response code: {}".format(response.status_code))

def expand_data(obj):
    new_obj = []
    for event in obj:
        nested_events_arr = event["events"]
        for nested in nested_events_arr:
            head_event_part = event.copy()
            head_event_part.pop("events")
            if 'name' in nested:
                head_event_part.update({'event_name': nested["name"]})
            if 'type' in nested:
                head_event_part.update({'event_type': nested["type"]})
            if 'parameters' in nested:
                for parameter in nested["parameters"]:
                    if 'name' in parameter:
                        for param_name in ["value", "boolValue", "multiValue", "multiMessageValue", "multiIntValue", "messageValue", "intValue"]:
                            if param_name in parameter:
                                head_event_part.update({parameter["name"]: parameter[param_name]})
            new_obj.append(head_event_part)
    return new_obj

def gen_chunks_to_object(data,chunksize=100):
    chunk = []
    for index, line in enumerate(data):
        if (index % chunksize == 0 and index > 0):
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk

def gen_chunks(data,log_type):
    for chunk in gen_chunks_to_object(data, chunksize=2000):
        body = json.dumps(chunk)
        post_data(customer_id, shared_key,body,log_type)

def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    global creds
    creds = get_credentials()
    start_time, end_time = generate_date()
    logging.info('Data processing. Period(UTC): {} - {}'.format(start_time,end_time))
    for line in activities:
        result_obj = get_result(line,start_time,end_time)
        if result_obj is not None:
            result_obj = expand_data(result_obj)
            gen_chunks(result_obj, "GWorkspace_ReportsAPI_"+line)