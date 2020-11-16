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

customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
pickle_str = os.environ['GooglePickleString']
pickle_string = base64.b64decode(pickle_str)
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']
activities = ["login", "calendar", "drive", "admin", "mobile", "token", "user_accounts"]

def get_credentials():
    creds = None
    if pickle_string:
        try:
            creds = pickle.loads(pickle_string)
        except Exception as pickle_read_exception:
            print("ERROR " + str(pickle_read_exception))
            logging.error('Error while loading pickle string: {}'.format(pickle_read_exception))
    else:
        print("ERROR - pickle_string is empty. Exit")
        logging.error('Error - pickle_string is empty. Exit')
        exit(1)
    return creds

def generate_date():
    current_time = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=10)
    past_time = current_time - datetime.timedelta(minutes=10)
    return (past_time.strftime("%Y-%m-%dT%H:%M:%SZ"), current_time.strftime("%Y-%m-%dT%H:%M:%SZ"))

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
        print("Logs not founded for {} activity".format(activity))
        logging.info("Logs not founded for {} activity".format(activity))
        logging.info("Activity - {}, {} events was processed)".format(activity, len(result_activities)))
    else:
        logging.info("Activity - {}, {} events was processed)".format(activity, len(result_activities)))
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
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info("Logs with {} activity was processed into Azure".format(log_type))
    else:
        logging.warn("Response code: {}".format(response.status_code))

def expand_data(obj):
    for event in obj:
        for nested in event["events"]:
            if 'name' in nested:
                event.update({'event_name': nested["name"]})
            if 'type' in nested:
                event.update({'event_type': nested["type"]})
            if 'parameters' in nested:
                for parameter in nested["parameters"]:
                    if 'value' in parameter:
                        event.update({parameter["name"]: parameter["value"]})
                    if 'boolValue' in parameter:
                        event.update({parameter["name"]: parameter["boolValue"]})
                    if 'multiValue' in parameter:
                        event.update({parameter["name"]: parameter["multiValue"]})
                    if 'multiMessageValue' in parameter:
                        event.update({parameter["name"]: parameter["multiMessageValue"]})
                    if 'multiIntValue' in parameter:
                        event.update({parameter["name"]: parameter["multiIntValue"]})
                    if 'messageValue' in parameter:
                        event.update({parameter["name"]: parameter["messageValue"]})
                    if 'intValue' in parameter:
                        event.update({parameter["name"]: parameter["intValue"]})
    return obj

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
        obj_array = []
        body = json.dumps(chunk)
        post_data(customer_id, shared_key,body,log_type)

def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    global creds
    creds = get_credentials()
    start_time = generate_date()[0]
    end_time = generate_date()[1]
    logging.info('Data processing. Period(UTC): {} - {}'.format(start_time,end_time))
    for line in activities:
        result_obj = get_result(line,start_time,end_time)
        if result_obj is not None:
            result_obj = expand_data(result_obj)
            gen_chunks(result_obj, "GWorkspace_ReportsAPI_"+line)