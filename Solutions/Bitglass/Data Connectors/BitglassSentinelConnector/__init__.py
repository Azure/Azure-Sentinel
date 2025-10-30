import logging
import azure.functions as func
import requests
import itertools
import datetime
from requests.packages.urllib3.util.retry import Retry
import os
import base64
import hashlib
import hmac
import json
import re
import time
from .state_manager import StateManager

bitglass_token = os.environ['BitglassToken']
bitglass_serviceURL = os.environ['BitglassServiceURL']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
table_name = "BitglassLogs"
chunksize = 10000

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Bitglass: Invalid Log Analytics Uri.")

class BG_CASB():

    def __init__(self, type):
        self.event_type = type
        filepath=f'{self.event_type}_funcstatemarkerfile'
        self.token = bitglass_token
        self.url = f'{bitglass_serviceURL}/api/bitglassapi/logs/v1/'

        self.headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'Content-Type': 'application/json'
        }
        self.state = StateManager(connection_string=connection_string, share_name='funcstatemarkershare', file_path=filepath)
        self.from_time = self.generate_date()

    def get_query(self, url, token):
        retries = Retry(
            total=3,
            status_forcelist={429, 500, 503},
            backoff_factor=3,
            respect_retry_after_header=True
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        session = requests.Session()
        session.mount('https://', adapter)
        if token is None:
            self.params = {
                "startdate": self.from_time,
                "cv": "1.0.1",
                "type": self.event_type,
                "responseformat": "json"
            }
        else:
            self.params = {
                "nextpagetoken": token,
                "cv": "1.0.1",
                "type": self.event_type,
                "responseformat": "json"
            }
        try:
            r = session.get(url=url,
                            headers=self.headers,
                            params=self.params
                            )
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 401:
                logging.error("The authentication credentials are incorrect or missing. Error code: {}".format(r.status_code))
            else:
                logging.error("Something wrong. Error: {}".format(r.text))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))

    def get_result(self):
        result_array = []
        r = self.get_query(self.url, None)
        if r is not None:
            if r.get("status") == "Request was successful":
                result = (r.get("response")).get("data")
                result_array += result
                nextpagetoken = r.get("nextpagetoken")
                while len(result) != 0:
                    r = self.get_query(self.url, nextpagetoken)
                    if r is not None:
                        if r.get("status") == "Request was successful":
                            nextpagetoken = r.get("nextpagetoken")
                            result = (r.get("response")).get("data")
                            result_array += result
        time_array = []
        for event in result_array:
            event.update({'log_type': self.event_type})
            time = event["time"]
            time_array.append(time)
        if len(time_array) > 0:
            sortedArray = sorted(time_array, key=lambda x: datetime.datetime.strptime(x, '%d %b %Y %H:%M:%S'), reverse=True)
            last_time = sortedArray[0]
            last_time = datetime.datetime.strptime(last_time, '%d %b %Y %H:%M:%S').strftime("%Y-%m-%dT%H:%M:%SZ")
            self.state.post(last_time)
        return result_array

    def generate_date(self):
        current_time = datetime.datetime.utcnow()
        past_time = self.state.get()
        if past_time is not None:
            logging.info("The last time point for \"{}\" log type is: {}".format(self.event_type,past_time))
        else:
            logging.info("There is no last time point for \"{}\" log type , trying to get logs for last 24 hour.".format(self.event_type))
            past_time = (current_time - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return (past_time)

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
            logging.info("Error during sending events to Azure Sentinel. Response code:{}".format(response.status_code))
            self.fail_processed = self.fail_processed + chunk_count

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info("Python timer trigger function ran at %s", utc_timestamp)
    logging.info("Starting program") 
    logs_type_array = [
                    "cloudaudit", "access",
                    "admin", "swgweb",
                    "swgwebdlp", "healthproxy",
                    "healthapi"
                    ]
    map_iterator = map(lambda x: BG_CASB(x),logs_type_array)
    for elem in map_iterator:
        results_array = elem.get_result()
        sentinel = Sentinel()
        if len(results_array) > 0:
            sentinel.gen_chunks(results_array)
            sentinel_class_vars = vars(sentinel)
            success_processed, fail_processed = sentinel_class_vars["success_processed"], \
                                                sentinel_class_vars["fail_processed"]
            logging.info('Logs type: {}. Total events processed successfully: {}, failed: {}. Period from : {}'
                  .format(elem.event_type, success_processed, fail_processed, elem.from_time))
        else:
            logging.info('Logs type: {}. There are no events for processing. Period from: {}'
                  .format(elem.event_type, elem.from_time))
        time.sleep(3)
