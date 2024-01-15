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
from .state_manager import StateManager
from datetime import datetime, timedelta

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
activities = [
            "user_accounts",
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
            "context_aware_access", 
            "chrome", 
            "data_studio",
            "saml", 
            "token"
            ]



# Remove excluded activities
excluded_activities = os.environ.get('ExcludedActivities')
if excluded_activities:
    excluded_activities = excluded_activities.replace(" ", "").split(",")
    activities = [activ for activ in activities if activ not in excluded_activities]


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

def GetEndTime(logType):
    end_time = datetime.utcnow().replace(second=0, microsecond=0)
    if logType == "calendar":
        end_time = (end_time - timedelta(hours=int(calendarFetchDelay)))
    if logType == "chat":
        logging.info("Chat Fecth Delay value - {}".format(int(chatFetchDelay)))
        end_time = (end_time - timedelta(days=int(chatFetchDelay)))
    if logType == "user_accounts":
        end_time = (end_time - timedelta(hours=int(userAccountsFetchDelay)))
    if logType == "login":
        end_time = (end_time - timedelta(hours=int(loginFetchDelay)))
    else:
        end_time = (end_time - timedelta(minutes=int(fetchDelay)))

    return end_time

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

def GetDates(logType):
    end_time = GetEndTime(logType)
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    activity_list = {}
    if past_time is not None and len(past_time) > 0:
        logging.info("The last time point is: {}".format(past_time))
        if is_json(past_time):
            activity_list = past_time
        else:
            for activity in activities:
                newtime = datetime.strptime(past_time[:-1] + '.000Z', "%Y-%m-%dT%H:%M:%S.%fZ")
                newtime = newtime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                newtime = newtime[:-4] + 'Z'
                activity_list[activity] = newtime
            activity_list = json.dumps(activity_list)
    else:
        logging.info("There is no last time point, trying to get events for last one day.")
        past_time = (end_time - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        for activity in activities:
            activity_list[activity] = past_time[:-4] + 'Z'
        activity_list = json.dumps(activity_list)
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time = end_time[:-4] + 'Z'
    return json.loads(activity_list) if (isBlank(logType)) else (json.loads(activity_list)[logType],end_time)

def get_result(activity,start_time, end_time):
    try:
        result_activities = []
        service = build('admin', 'reports_v1', credentials=creds, cache_discovery=False, num_retries=3, static_discovery=True)
        results = service.activities().list(userKey='all', applicationName=activity,
                                                maxResults=1000, startTime=start_time, endTime=end_time).execute()
        next_page_token = results.get('nextPageToken', None)
        result = results.get('items', [])
        result_activities.extend(result)
        logging.info("Name of Activity: {}, Number of events: {})".format(activity, len(result_activities)))
        if result_activities is None or len(result_activities) == 0:
            logging.info("Logs not founded for {} activity".format(activity))
            logging.info("Activity - {}, processing {} events)".format(activity, len(result_activities)))
        else:
            logging.info("Activity - {}, processing {} events)".format(activity, len(result_activities)))
    except Exception as err:
        logging.error("Something wrong while getting the results. Exception error text: {}".format(err))
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
        logging.info("Number of events {}".format(len(result_activities)))
        if result_activities is None or len(result_activities) == 0:
            logging.info("Logs not founded for {} activity".format(activity))
            logging.info("Activity - {}, processing {} events)".format(activity, len(result_activities)))
        else:
            logging.info("Activity - {}, processing {} events)".format(activity, len(result_activities)))
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
        logging.info("Chunk was processed{} events".format(chunk_count))
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
def process_result(result_obj, start_time, postactivity_list, line):
    if result_obj is not None:
        result_obj = expand_data(result_obj)
        logging.info("Activity - {}, Expanded Events {} )".format(line, len(result_obj)))
        sorted_data = sorted(result_obj, key=lambda x: x["id"]["time"],reverse=False)
        json_string = json.dumps(result_obj)
        byte_ = json_string.encode("utf-8")
        byteLength = len(byte_)
        mbLength = byteLength/1024/1024
        if(len(result_obj)) > 0 and int(mbLength) < 25 :
            # Sort the json based on the "timestamp" key
            body = json.dumps(result_obj)
            statuscode = post_data(customer_id, shared_key,body,"GWorkspace_ReportsAPI_"+line, len(result_obj))
            if (statuscode >= 200 and statuscode <= 299):
                latest_timestamp = sorted_data[-1]["id"]["time"]
                dt = datetime.strptime(latest_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                dt += timedelta(milliseconds=1)
                latest_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
                latest_timestamp = latest_timestamp[:-3] + 'Z'
            else:
                logging.warn("There is an issue with Posting data to LA - Response code: {}".format(statuscode))
                latest_timestamp = start_time
        else:
            latest_timestamp = gen_chunks_with_latesttime(sorted_data, "GWorkspace_ReportsAPI_"+line)
            if(isBlank(latest_timestamp)):
                latest_timestamp = start_time
                logging.info("The latest timestamp is same as the original start time {} - {}".format(line,latest_timestamp))
                # Fetch the latest timestamp
                logging.info("The latest timestamp got from api activity is {} - {}".format(line,latest_timestamp))
        postactivity_list[line] = latest_timestamp
        state = StateManager(connection_string)
        state.post(str(json.dumps(postactivity_list)))
    return latest_timestamp 

def check_if_script_runs_too_long(script_start_time):
    now = int(time.time())
    duration = now - script_start_time
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.8)
    return duration > max_duration            

def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    script_start_time = int(time.time())
    global creds
    creds = get_credentials()
    latest_timestamp = ""
    postactivity_list = GetDates("")
    for line in activities:
      try:
        start_time,end_time = GetDates(line)
        if start_time is None:
            logging.info("There is no last time point, trying to get events for last one day.")
            end_time = datetime.strptime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ")
            start_time = (end_time - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Check if start_time  is less than current UTC time minus 180 days. If yes, then set end_time to current UTC time minus 179 days
        # Google Workspace Reports API only supports 180 days of data
        if (datetime.utcnow() - timedelta(days=180)) > datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ"):
            logging.info("End time older than 180 days. Setting start time to current UTC time minus 179 days as Google Workspace Reports API only supports 180 days of data.")
            start_time = (datetime.utcnow() - timedelta(days=179)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            start_time = start_time[:-4] + 'Z'

        # check if differenc between start_time and end_time is more than 15 mins. If yes, then set end_time to start_time + 15 mins
        # This is to avoid fetching too many events in one go
        if (convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ") - convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds() > 900:
            end_time = (convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            logging.info ('end_time is more than 15 mins from start_time. Setting end_time to start_time + 15 mins. New end_time: {}'.format(end_time)) 
        
        if not(convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") >= convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ")):
            logging.info('Data processing. Period(UTC): {} - {}'.format(start_time,end_time))
            latest_timestamp = start_time
            logging.info('Logging the startTime for Activity. Period(UTC): {} - {}' .format(line,start_time))
            result_obj, next_page_token = get_result(line,latest_timestamp,end_time)
            if (result_obj is not None) and (len(result_obj) > 0):
                latest_timestamp = process_result(result_obj, latest_timestamp, postactivity_list, line)
                while next_page_token is not None:
                    result_obj, next_page_token  = get_nextpage_results(line,start_time,end_time,next_page_token)
                    latest_timestamp = process_result(result_obj, latest_timestamp, postactivity_list, line)
                    if check_if_script_runs_too_long(script_start_time):
                        logging.info(f'Script is running too long. Stop processing new events. Finish script.')
                        return
            else:
                logging.info("No events for {} activity".format(line))
                latest_timestamp = end_time
                postactivity_list[line] = latest_timestamp
                state = StateManager(connection_string)
                state.post(str(json.dumps(postactivity_list)))
            postactivity_list[line] = latest_timestamp
      except Exception as err:
        logging.error("Something wrong. Exception error text: {}".format(err))
        logging.error( "Error: Google Workspace Reports data connector execution failed with an internal server error.")
        raise
    logging.info(f'Finish script.')