from __future__ import print_function
from aliyun.log import *
import os
import requests
import datetime
import hashlib
import hmac
import base64
import logging
from datetime import datetime, timedelta
from .state_manager import StateManager
import re
import azure.functions as func
import json
import concurrent.futures

endpoint = os.environ.get('Endpoint', 'cn-hangzhou.log.aliyuncs.com')
accessKeyId = os.environ.get('AliCloudAccessKeyId', '')
accessKey = os.environ.get('AliCloudAccessKey', '')
token = ""
topic = os.environ.get('Topic', '')
user_projects = os.environ.get("AliCloudProjects", '').replace(" ", "").split(',')
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
log_type = "AliCloud"
connection_string = os.environ['AzureWebJobsStorage']
chunksize = 2000
logAnalyticsUri = os.environ.get('logAnalyticsUri')
workers = os.environ.get('AliCloudWorkers', '10')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(logAnalyticsUri))
if (not match):
    raise Exception("Ali Cloud: Invalid Log Analytics Uri")


def generate_date():
    current_time = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(minutes=10)
    state = StateManager(connection_string=connection_string)
    i = state.get()
    if i is not None:
        past_time = datetime.strptime(state.get(), "%d.%m.%Y %H:%M:%S")
        if past_time is not None:
            logging.info("The last time point is: {}".format(past_time))
        else:
            logging.info("There is no last time point, trying to get events for last hour")
            past_time = (current_time - timedelta(minutes=60))
    else:
        logging.info("There is no last time point, trying to get events for last hour")
        past_time = (current_time - timedelta(minutes=60))

    state.post(current_time.strftime("%d.%m.%Y %H:%M:%S"))
    return past_time, current_time


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
    current_date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, current_date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': current_date
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
        return 0
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


def gen_chunks(data, start_time, end_time):
    success = 0
    failed = 0
    for chunk in gen_chunks_to_object(data, chunk_size=chunksize):
        status_code = post_data(chunk)
        if 200 <= status_code <= 299:
            success += len(chunk)
        else:
            failed += len(chunk)
    logging.info("{} successfully added, {} failed. Period(UTC): {} - {}".format(success, failed, start_time, end_time))


def get_list_logstores(client, project):
    request = ListLogstoresRequest(project)
    return client.list_logstores(request).get_logstores()


def process_logstores(client, project, start_time, end_time):
    logstores = get_list_logstores(client, project)
    logs_json_all = []
    for logstore in logstores:
        logs_json = []
        res = client.get_log_all(project, logstore, str(start_time), str(end_time), topic)
        for logs in res:
            for log in logs.get_logs():
                logs_json += [{"timestamp": log.timestamp, "source": log.source, "contents": log.contents}]
        logs_json_all += logs_json
        logging.info("Found {} logs from {} logstore from {} project".format(len(logs_json), logstore, project))
    return logs_json_all


def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Starting program')
    start_time, end_time = generate_date()

    if not endpoint or not accessKeyId or not accessKey:
        raise Exception("Endpoint, access_id and access_key cannot be empty")

    # authorization
    client = LogClient(endpoint, accessKeyId, accessKey, token)

    # get logs
    logs_json = []
    try:
        if user_projects == ['']:
            projects = client.list_project(size=-1).get_projects()
            project_names = list(map(lambda project_name: project_name["projectName"], projects))
        else:
            project_names = user_projects

        executor = concurrent.futures.ThreadPoolExecutor(int(workers))
        futures = [executor.submit(process_logstores, client, project, start_time, end_time) for project in
                   project_names]
        concurrent.futures.wait(futures)
        for future in futures:
            if future.result() is not None:
                logs_json += future.result()
    except Exception as err:
        logging.error("Something wrong. Exception error text: {}".format(err))

    # Send data via data collector API
    gen_chunks(logs_json, start_time=start_time, end_time=end_time)
