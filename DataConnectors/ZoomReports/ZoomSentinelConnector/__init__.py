import azure.functions as func
import jwt
import datetime
import json
import base64
import hashlib
import hmac
import requests
import re
import os
import logging
from .state_manager import StateManager

jwt_api_key = os.environ['ZoomApiKey']
jwt_api_secret = os.environ['ZoomApiSecret']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
table_name = "Zoom"
chunksize = 10000

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Zoom: Invalid Log Analytics Uri.")

class Zoom:

    def __init__(self):
        self.api_key = jwt_api_key
        self.api_secret = jwt_api_secret
        self.base_url = "https://api.zoom.us/v2"
        self.jwt_token_exp_hours = 1
        self.jwt_token = self.generate_jwt_token()
        self.from_day,self.to_day = self.generate_date()
        self.headers = {
                             'Accept': 'application/json',
                             'authorization': "Bearer " + self.jwt_token,
                         }

    def generate_jwt_token(self):
        payload = {
            'iss': self.api_key,
            'exp': datetime.datetime.now() + datetime.timedelta(hours=self.jwt_token_exp_hours)
        }
        jwt_token = jwt.encode(payload, self.api_secret)
        return jwt_token

    def generate_date(self):
        current_time_day = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        state = StateManager(connection_string)
        past_time = state.get()
        if past_time is not None:
            logging.info("The last time point is: {}".format(past_time))
        else:
            logging.info("There is no last time point, trying to get events for last week.")
            past_time = (current_time_day - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        state.post(current_time_day.strftime("%Y-%m-%d"))
        return (past_time, current_time_day.strftime("%Y-%m-%d"))

    def get_report(self, report_type_suffix,next_page_token = None):
        query_params = {
                        "page_size": 300,
                        "from": self.from_day,
                        "to": self.to_day
                        }
        if next_page_token:
            query_params.update({"next_page_token": next_page_token})
        try:
            r = requests.get(url = self.base_url + report_type_suffix,
                         params = query_params,
                         headers = self.headers)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 400:
                logging.error("The requested report cannot be generated for this account because"
                      " this account has not subscribed to toll-free audio conference plan."
                      " Error code: {}".format(r.status_code))
            elif r.status_code == 401:
                logging.error("Invalid access token. Error code: {}".format(r.status_code))
            elif r.status_code == 300:
                logging.error("Only provide report in recent 6 months. Error code: {}".format(
            r.status_code))
            else:
                logging.error("Something wrong. Error code: {}".format(r.status_code))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))

class Sentinel:

    def __init__(self):
        self.logAnalyticsUri = logAnalyticsUri
        self.success_processed = 0
        self.fail_processed = 0
        self.table_name = table_name
        self.chunksize = chunksize
        
    def gen_chunks_to_object(self, data, chunksize=100):
        chunk = []
        for index, line in enumerate(data):
            if (index % chunksize == 0 and index > 0):
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

    def gen_chunks(self, data):
        for chunk in self.gen_chunks_to_object(data, chunksize=self.chunksize):
            obj_array = []
            for row in chunk:
                if row != None and row != '':
                    obj_array.append(row)
            body = json.dumps(obj_array)
            self.post_data(body, len(obj_array))


    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self, body, chunk_count):
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self.build_signature(rfc1123date, content_length, method, content_type,
                                         resource)
        uri = self.logAnalyticsUri + resource + '?api-version=2016-04-01'
        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': self.table_name,
            'x-ms-date': rfc1123date
        }
        response = requests.post(uri, data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            logging.info("Chunk was processed({} events)".format(chunk_count))
            self.success_processed = self.success_processed + chunk_count
        else:
            logging.error("Error during sending events to Azure Sentinel. Response code:{}".format(response.status_code))
            self.fail_processed = self.fail_processed + chunk_count

def results_array_join(result_element,api_req_id,api_req_name):
    for element in result_element[api_req_id]:
        element['event_type'] = api_req_id
        element['event_name'] = api_req_name
        results_array.append(element)

def get_main_info():
    for api_req_id, api_req_info in reports_api_requests_dict.items():
        api_req = api_req_info['api_req']
        api_req_name = api_req_info['name']
        logging.info("Getting report: {}".format(api_req_info['name']))
        result = zoom.get_report(report_type_suffix = api_req)
        if result is not None:
            next_page_token = result.get('next_page_token')
            results_array_join(result,api_req_id,api_req_name)
        else:
            next_page_token = None
        while next_page_token:
            result = zoom.get_report(report_type_suffix=api_req, next_page_token = next_page_token)
            if result is not None:
                next_page_token = result.get('next_page_token')
                results_array_join(result, api_req_id, api_req_name)
            else:
                next_page_token = None

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    logging.info('Starting program')
    global results_array, reports_api_requests_dict, zoom
    reports_api_requests_dict = \
        {
            "dates": {"api_req": "/report/daily", "name": "Daily Usage Reports."},
            "users": {"api_req": "/report/users", "name": "Active/Inactive Host Reports."},
            "telephony_usage": {"api_req": "/report/telephone", "name": "Telephone Reports."},
            "cloud_recording_storage": {"api_req": "/report/cloud_recording", "name": "Cloud Recording Usage Reports."},
            "operation_logs": {"api_req": "/report/operationlogs", "name": "Operation Logs Report."},
            "activity_logs": {"api_req": "/report/activities", "name": "Sign In/Sign Out Activity Report."}
        }
    results_array = []
    zoom = Zoom()
    sentinel = Sentinel()
    zoom_class_vars = vars(zoom)
    from_day, to_day = zoom_class_vars['from_day'], zoom_class_vars['to_day']
    logging.info('Trying to get events for period: {} - {}'.format(from_day, to_day))
    get_main_info()
    sentinel.gen_chunks(results_array)
    sentinel_class_vars = vars(sentinel)
    success_processed, fail_processed = sentinel_class_vars["success_processed"],\
                                        sentinel_class_vars["fail_processed"]
    logging.info('Total events processed successfully: {}, failed: {}. Period: {} - {}'
          .format(success_processed, fail_processed, from_day, to_day))
