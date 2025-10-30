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


cas_token = os.environ['TrendMicroCASToken']
serviceURL = os.environ['TrendMicroCASServiceURL']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
table_name = "TrendMicroCAS"
chunksize = 10000

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Trend Micro CAS Data Connector: Invalid Log Analytics Uri.")

class TD_CAS():

    def __init__(self, tuple, from_time, to_time):
        self.event = tuple[1]
        self.service = tuple[0]
        self.token = cas_token
        self.url = f'https://{serviceURL}/v1/siem/security_events'
        self.params = {
                    "start": from_time,
                    "end": to_time,
                    "service": self.service,
                    "event": self.event
                  }
        self.headers = {
            'Authorization': 'Bearer {}'.format(cas_token),
            'Content-Type': 'application/json'
        }

    def get_query(self, url):
        retries = Retry(
            total=3,
            status_forcelist={429, 500, 503},
            backoff_factor=1,
            respect_retry_after_header=True
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        session = requests.Session()
        session.mount('https://', adapter)
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
        r = self.get_query(self.url)
        if "security_events" in r:
            result_array = r.get("security_events")
            next_page = r.get("next_link")
            while next_page != '':
                r = self.get_query(next_page)
                if "security_events" in r:
                    result_array_next_page = r.get("security_events")
                    next_page = r.get("next_link")
                    if len(result_array_next_page) > 0:
                        result_array += result_array_next_page
        return result_array

def generate_date():
    current_time = datetime.datetime.utcnow()
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info("The last time point is: {}".format(past_time))
    else:
        logging.info("There is no last time point, trying to get scans information for last 24 hours.")
        past_time = (current_time - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    state.post(current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    return (past_time, current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))


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
    service_array = [
                    "exchange", "sharepoint",
                    "onedrive", "dropbox",
                    "box", "googledrive",
                    "gmail", "teams",
                    "exchangeserver", "salesforce_sandbox",
                    "salesforce_production", "teams_chat"
                    ]
    event_array =   [
                    "securityrisk",
                    "virtualanalyzer",
                    "ransomware",
                    "dlp"
                    ]
    from_time,to_time = generate_date()
    all_combinations = list(itertools.product(service_array, event_array))
    map_iterator = map(lambda x: TD_CAS(x, from_time, to_time),all_combinations)
    for elem in map_iterator:
        sentinel = Sentinel()
        results_array = elem.get_result()
        if len(results_array) > 0:
            sentinel.gen_chunks(results_array)
            sentinel_class_vars = vars(sentinel)
            success_processed, fail_processed = sentinel_class_vars["success_processed"], \
                                                sentinel_class_vars["fail_processed"]
            logging.info('Service: {}. Event type: {}. Total events processed successfully: {}, failed: {}. Period: {} - {}'
                  .format(elem.service, elem.event, success_processed, fail_processed, from_time, to_time))
        else:
            logging.info('Service: {}. Event type: {}. There are no events for processing. Period: {} - {}'
                  .format(elem.service, elem.event, from_time, to_time))
        time.sleep(3)
