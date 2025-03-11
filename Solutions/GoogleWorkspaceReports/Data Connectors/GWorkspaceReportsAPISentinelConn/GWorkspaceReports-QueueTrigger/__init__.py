from __future__ import print_function
import pickle
from googleapiclient.discovery import build
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
from .state_manager import AzureStorageQueueHelper
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials

customer_id = os.environ['WorkspaceID']
fetchDelay = os.getenv('FetchDelay',10)
chunksize = 9999
calendarFetchDelay = os.getenv('CalendarFetchDelay',6)
chatFetchDelay = os.getenv('ChatFetchDelay',1)
userAccountsFetchDelay = os.getenv('UserAccountsFetchDelay',3)
loginFetchDelay = os.getenv('LoginFetchDelay',6)
shared_key = os.environ['WorkspaceKey']
pickle_str = os.environ['GooglePickleString']
pickle_string = base64.b64decode(pickle_str)
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')


MAX_SCRIPT_EXEC_TIME_MINUTES = 10
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Google Workspace Reports: Invalid Log Analytics Uri.")


def get_credentials():
    creds = None
    if is_json(pickle_string):
        try:
            creds = Credentials.from_authorized_user_info(json.loads(pickle_string), SCOPES)
        except Exception as pickle_read_exception:
            logging.error('Error while loading pickle string: {}'.format(pickle_read_exception))
    else:
        try:
            creds = pickle.loads(pickle_string)
        except Exception as pickle_read_exception:
            logging.error('Error while loading pickle string: {}'.format(pickle_read_exception))
    return creds




def isBlank (myString):
    return not (myString and myString.strip())

def isNotBlank (myString):
    return bool(myString and myString.strip())

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

# Function to convert string to datetime
def convertToDatetime(date_time,format):
    #format = '%b %d %Y %I:%M%p'  # The format
    datetime_str = datetime.strptime(date_time, format) 
    return datetime_str

def get_result(activity,start_time, end_time):
    try:
        result_activities = []
        service = build('admin', 'reports_v1', credentials=creds, cache_discovery=False, num_retries=3, static_discovery=True)
        results = service.activities().list(userKey='all', applicationName=activity,
                                                maxResults=1000, startTime=start_time, endTime=end_time).execute()
        next_page_token = results.get('nextPageToken', None)
        result = results.get('items', [])
        result_activities.extend(result)
        if result_activities is None or len(result_activities) == 0:
            logging.info("Logs not founded for {} activity".format(activity))
        else:
            logging.info("Activity - {}, processing {} events".format(activity, len(result_activities)))
    except Exception as err:
        logging.error("Something wrong while getting the results. Exception error text: {}".format(err))
        raise err
    return result_activities, next_page_token
    
def get_nextpage_results(activity,start_time, end_time, next_page_token):
    try:
        result_activities = []
        service = build('admin', 'reports_v1', credentials=creds, cache_discovery=False, num_retries=3, static_discovery=True)
        results = service.activities().list(userKey='all', applicationName=activity,
                                                maxResults=1000, startTime=start_time, endTime=end_time, pageToken=next_page_token).execute()
        next_page_token = results.get('nextPageToken', None)
        result = results.get('items', [])
        result_activities.extend(result)
        if result_activities is None or len(result_activities) == 0:
            logging.info("Logs not founded for {} activity".format(activity))
        else:
            logging.info("Activity - {}, processing {} events".format(activity, len(result_activities)))
    except Exception as err:
        logging.error("Something wrong while getting the results. Exception error text: {}".format(err))
    return result_activities, next_page_token

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

def post_data(customer_id, shared_key, body, log_type,chunk_count):
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
        'x-ms-date': rfc1123date,
        'time-generated-field': "id_time"
    }
    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info("Logs with {} activity was processed into Azure".format(log_type))
        logging.info("Chunk was processed {} events".format(chunk_count))
    else:
        logging.warn("Response code: {}".format(response.status_code))
    return response.status_code

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

def gen_chunks_with_latesttime(data,log_type):
    chunks = [data[i:i+chunksize] for i in range(0, len(data), chunksize)]
    logging.info("Entered into the chunks mode")
    latest_timestamp = "";
    i = 0
    for chunk in chunks:
        try:
            i = i+1
            logging.debug("Iteration chunk {}".format(i))
            body = json.dumps(chunk)
            logging.debug(body)
            statuscode = post_data(customer_id, shared_key,body,log_type, len(chunk))
            if (statuscode >= 200 and statuscode <= 299):
                latest_timestamp = chunk[-1]["id"]["time"]
                dt = datetime.strptime(latest_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                dt += timedelta(milliseconds=1)
                latest_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
                latest_timestamp = latest_timestamp[:-3] + 'Z'
                logging.info("Chunk Timestamp {}".format(latest_timestamp))
            else:
                logging.warn("There is an issue with Posting data to LA - Response code: {}".format(statuscode))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))
    return latest_timestamp

"""This method is used to process and post the results to Log Analytics Workspace
        Returns:
            latest_timestamp : last processed result timestamp
"""
def process_result(result_obj, start_time, activity):
    if result_obj is not None:
        result_obj = expand_data(result_obj)
        logging.info("Activity - {}, Expanded Events {} ".format(activity, len(result_obj)))
        sorted_data = sorted(result_obj, key=lambda x: x["id"]["time"],reverse=True)
        json_string = json.dumps(result_obj)
        byte_ = json_string.encode("utf-8")
        byteLength = len(byte_)
        mbLength = byteLength/1024/1024
        if(len(result_obj)) > 0 and int(mbLength) < 25 :
            # Sort the json based on the "timestamp" key
            body = json.dumps(result_obj)
            statuscode = post_data(customer_id, shared_key,body,"GWorkspace_ReportsAPI_"+activity, len(result_obj))
            if (statuscode >= 200 and statuscode <= 299):
                latest_timestamp = sorted_data[-1]["id"]["time"]
                dt = datetime.strptime(latest_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                dt += timedelta(milliseconds=-1)
                latest_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
                latest_timestamp = latest_timestamp[:-3] + 'Z'
                logging.info("Successfully send data to LA of size {} MB".format(mbLength))
            else:
                logging.warn("There is an issue with Posting data to LA - Response code: {}".format(statuscode))
                latest_timestamp = start_time
        else:
            latest_timestamp = gen_chunks_with_latesttime(sorted_data, "GWorkspace_ReportsAPI_"+activity)
            if(isBlank(latest_timestamp)):
                latest_timestamp = start_time
                logging.info("The latest timestamp is same as the original start time {} - {}".format(activity,latest_timestamp))
                # Fetch the latest timestamp
                logging.info("The latest timestamp got from api activity is {} - {}".format(activity,latest_timestamp))
    return latest_timestamp 

def check_if_script_runs_too_long(script_start_time):
    now = int(time.time())
    duration = now - script_start_time
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.9)
    return duration > max_duration            

def format_message_for_queue_and_add(start_time, end_time, activity, mainQueueHelper):
    queue_body = {}
    queue_body["start_time"] = start_time
    queue_body["end_time"] = end_time
    queue_body["activity"] = activity
    mainQueueHelper.send_to_queue(queue_body,True)
    logging.info("Added to queue: {}".format(queue_body))

def main(queueItem: func.QueueMessage ):
    logging.getLogger().setLevel(logging.INFO)
    script_start_time = int(time.time())
    queue_name = "gworkspace-main-queue"
    message_body = json.loads(queueItem.get_body().decode('ascii').replace("'",'"'))
    # enable below for testing
    #message_body = {'start_time': '2023-12-03T14:01:00.000000Z', 'end_time': '2023-12-07T15:01:00.000Z', 'activity': 'admin'}
    start_time = message_body.get('start_time')
    end_time = message_body.get('end_time')
    activity = message_body.get('activity')
    global creds
    creds = get_credentials()
    latest_timestamp = ""
    mainQueueHelper = AzureStorageQueueHelper(connection_string,queue_name)
    # Initialize the queue body with the same values as the message body
    queue_body = {}
    queue_body["start_time"] = start_time
    queue_body["end_time"] = end_time
    queue_body["activity"] = activity

    logging.info('Starting GWorkspaceReport-QueueTrigger program at {}'.format(time.ctime(int(time.time()))) )
    logging.info('Queue message received with queue Id: {} body: {}'.format(queueItem.id,message_body) )
    try:
        result_obj, next_page_token = get_result(activity,start_time,end_time)
        if (result_obj is not None) and (len(result_obj) > 0):
            latest_timestamp = process_result(result_obj, latest_timestamp, activity)
            # Since the results are in descending order, get the end_time updated with the latest timestamp, no change in start_time
            # udpate the queue body with the latest timestamp
            queue_body["start_time"] = start_time 
            queue_body["end_time"] = latest_timestamp 
            queue_body["activity"] = activity
            while next_page_token is not None and len(next_page_token) > 0:
                result_obj, next_page_token  = get_nextpage_results(activity,start_time,end_time,next_page_token)
                if (result_obj is not None) and (len(result_obj) > 0):
                    latest_timestamp = process_result(result_obj, latest_timestamp, activity)
                    #update the queue body with the latest timestamp
                    queue_body["start_time"] = start_time 
                    queue_body["end_time"] = latest_timestamp 
                    queue_body["activity"] = activity
                    
                if check_if_script_runs_too_long(script_start_time):
                    logging.info(f'Script is running too long. Stop processing new events and updating state before finishing the script.')
                    return_message = mainQueueHelper.send_to_queue(queue_body,True)
                    if return_message is not None and return_message.id is not None:
                        logging.info("Message sent to queue with encoding with Base64. Message Id: {} Message Content: {} Queue Name: {}".format(return_message.id, queue_body, queue_name))
                    else:
                        logging.error("Message not sent to queue. Message Content: {} Queue Name: {}".format(queue_body, queue_name))
                    logging.info(f'Finish script. at {time.ctime(int(time.time()))}')
                    return
        else:
            logging.info("No events for {} activity with {} start time and {} end time".format(activity,start_time,end_time))
    
    except Exception as err:
        logging.error("Something wrong. Exception error text: {}".format(err))
        logging.error( "Error: Google Workspace Reports data connector execution failed with an internal server error.")
        return_message = mainQueueHelper.send_to_queue(queue_body,True)
        if return_message is not None and return_message.id is not None:
            logging.info("Message sent to queue with encoding with Base64. Message Id: {} Message Content: {} Queue Name: {}".format(return_message.id, queue_body, queue_name))       
        else:
            logging.error("Message not sent to queue. Message Content: {} Queue Name: {}".format(queue_body, queue_name))
        logging.info(f'Finish script. at {time.ctime(int(time.time()))}')
        raise
    logging.info(f'Finish script. at {time.ctime(int(time.time()))}')