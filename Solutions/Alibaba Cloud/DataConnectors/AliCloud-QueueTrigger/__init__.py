import os
import requests
import datetime
import hashlib
import hmac
import base64
import logging
from datetime import datetime, timedelta
import re
import azure.functions as func
import json
import time
from .state_manager import AzureStorageQueueHelper
#from .ali_mock import LogClient, ListLogstoresRequest
from aliyun.log import *

# Configuration - get from env variables
ali_endpoint = os.environ.get('Endpoint', 'cn-hangzhou.log.aliyuncs.com')
ali_accessKeyId = os.environ.get('AliCloudAccessKeyId', '')
ali_accessKey = os.environ.get('AliCloudAccessKey', '')
ali_topic = os.environ.get('Topic', '')
connection_string = os.environ['AzureWebJobsStorage']
customer_id = os.environ['WorkspaceID']
max_queue_message_retries = int(os.environ.get('MaxQueueMessageRetries', '100'))
shared_key = os.environ['WorkspaceKey']
user_projects = os.environ.get("AliCloudProjects", '').replace(" ", "").split(',')

# Constants
ali_token = ""
la_chunk_size = 2000
log_type = "AliCloud"
max_runtime_before_stopping_in_minutes = 8
max_LA_post_retries_after_transient = 3
retry_invisibility_timeout_in_seconds = 60
queue_source_name = "alibabacloud-queue-items"
queue_poison_name = queue_source_name + '-poison'


def build_LA_post_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


def post_data_to_LA(message_id, chunk, dequeue_count):
    body = json.dumps(chunk)
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    current_date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_LA_post_signature(customer_id, shared_key, current_date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': current_date
    }

    for attempt in range(max_LA_post_retries_after_transient):
        try:
            response = requests.post(uri, data=body, headers=headers)

            if 200 <= response.status_code <= 299:
                logging.info("{} events were sent to LA".format(len(chunk)))
                return True
            elif response.status_code == 401:
                logging.error("LA post authentication failure. The authentication credentials are incorrect or missing. Error code: {} (message_id: {})".format(response.status_code, message_id))
                return False
            elif response.status_code >= 500:
                logging.error("LA post transient failure. Retry attempt {} out of {} max in 50ms. Error code: {} (message_id: {})".format(attempt+1, max_LA_post_retries_after_transient, response.status_code, message_id))
                time.sleep(0.05)
            else:
                logging.error("LA post failure. Error code: {} (message_id: {})".format(response.status_code, message_id))
                return False
        except Exception as err:
            logging.error("LA post failure. Exception thrown (message_id: {}). Exception error text: {}".format(message_id, err))
            return False

    logging.error("LA post transient failure reached max allowed re-tries - failing function. Error code: {} (message_id: {})".format(attempt, max_LA_post_retries_after_transient, response.status_code, message_id))        
    return False


def get_data_in_chunks(data, chunk_size):
    chunk = []
    for index, line in enumerate(data):
        if index % chunk_size == 0 and index > 0:
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk


def send_data_to_LA_in_chunks(message_id, data, start_time, end_time, stop_run_time_tmst, dequeue_count):
    events_sent = 0

    for chunk in get_data_in_chunks(data, chunk_size=la_chunk_size):
        if time.time() > stop_run_time_tmst:
            logging.error("Stopping processing in the middle of sending logs to LA since execution time exceeded its allotted time. Will continue in next retry. Period(UTC): {} - {} (message_id: {})".format(start_time, end_time, message_id))
            return False
        
        isSuccess = post_data_to_LA(message_id, chunk, dequeue_count)
        if isSuccess == False:
            return isSuccess
        
        events_sent += len(chunk)
    
    logging.info("Successfully sent {} events to LA. Period(UTC): {} - {} (message_id: {})".format(events_sent, start_time, end_time, message_id))
    return True


def get_list_logstores(client, project):
    request = ListLogstoresRequest(project)
    response = client.list_logstores(request)
    return response.get_logstores()


def process_logstores_and_send_to_LA(client, message_id, project, start_time, end_time, retrieved_log_stores, finished_log_stores, stop_run_time_tmst, dequeue_count):
    if len(retrieved_log_stores) == 0:
        retrieved_log_stores.extend(get_list_logstores(client, project))
        logging.info("Retrieved {} logstores for project {} (message_id: {})".format(len(retrieved_log_stores), project, message_id))
    else:
        logging.info("Continuing from previously retrieved {} logstores for project {} (message_id: {})".format(len(retrieved_log_stores), project, message_id))

    for logstore in retrieved_log_stores:
        logging.info("Starting to handle store {} for project {} (message_id: {})".format(logstore, project, message_id))    

        if logstore in finished_log_stores:
            logging.info("Not retrieving get_log_all for store {} for project {} since it was already processed and sent to LA in previous runs (message_id: {})".format(logstore, project, message_id))    
            continue

        if time.time() > stop_run_time_tmst:
            logging.error("Stopping processing before retrieving logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(logstore, project, message_id))    
            return False

        logs_to_send = []
        res = client.get_log_all(project, logstore, str(start_time), str(end_time), ali_topic)
        logging.info("Retrieved get_log_all responses for store {} for project {} (message_id: {})".format(logstore, project, message_id))

        for logs in res:
            if time.time() > stop_run_time_tmst:
                logging.error("Stopping processing in the middle of retrieving logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(logstore, project, message_id))
                return False
        
            internalLogs = logs.get_logs()
            for log in internalLogs:
                logs_to_send += [{"timestamp": log.timestamp, "source": log.source, "contents": log.contents}]
            
        logging.info("Finished retrieving all {} logs from {} logstore for {} project (message_id: {})".format(len(logs_to_send), logstore, project, message_id))

        isSuccess = send_data_to_LA_for_stores_and_update_finished_log_stores(message_id, project, start_time, end_time, logstore, finished_log_stores, logs_to_send, stop_run_time_tmst, dequeue_count)
        logging.info("After sending {} logs to LA for store {} for project {} with success: {} (message_id: {})".format(len(logs_to_send), logstore, project, isSuccess, message_id))

        if isSuccess == False:
            return isSuccess
    
    return True

    
def send_data_to_LA_for_stores_and_update_finished_log_stores(message_id, project, start_time, end_time, logstore, finished_log_stores, logs_to_send, stop_run_time_tmst, dequeue_count):
    if len(logs_to_send) == 0:
        finished_log_stores.append(logstore)
        return True

    if time.time() > stop_run_time_tmst:
        logging.error("Stopping processing before sending logs to LA for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry (message_id: {})".format(logstore, project, message_id))    
        return False
    
    isSuccess = send_data_to_LA_in_chunks(message_id, logs_to_send, start_time, end_time, stop_run_time_tmst, dequeue_count)
    if isSuccess == True:
        finished_log_stores.append(logstore)
    
    return isSuccess


def update_storage_queue_after_failure(queueItem, message_body, message_id, dequeue_count, retrieved_log_stores, finished_log_stores):
    message_body["dequeue_count"] = dequeue_count+1
    message_body["retrieved_log_stores"] = ','.join(retrieved_log_stores)
    message_body["finished_log_stores"] = ','.join(finished_log_stores)
    isDataLoss = queueItem.dequeue_count >= max_queue_message_retries or dequeue_count >= max_queue_message_retries

    sourceQueueHelper = AzureStorageQueueHelper(connection_string, queue_source_name)

    # If we reached the max allowed re-tries, it means we have data-loss.
    # Delete message from the source queue (why? because we don't want it to be re-tried automatically), and send that message to the poison-queue.
    if isDataLoss == True:
        poisonQueueHelper = AzureStorageQueueHelper(connection_string, queue_poison_name)
        poisonQueueHelper.send_to_queue(message_body,encoded=True)

        try:
            sourceQueueHelper.delete_queue_message(queueItem.id, queueItem.pop_receipt)
        except Exception as err:
            logging.error("Error while deleting queue message from source queue (already sent to poison queue). message_id: {}, exception error text: {}".format(message_id, err))
        
        logging.error("Data loss! Processing of queue message reached max re-tries. Message moved to poison queue and will not be re-tried. Message body: {}".format(message_body))
        raise Exception("Data loss! Processing of queue message reached max re-tries. Message moved to poison queue and will not be re-tried. Message body: {}".format(message_body))
    
    # If we haven't reached the max allowed re-tries, it means we don't have a data-loss;
    # we create a new similar message in the queue that will become visbile in 60 seconds for next retry (we take into account that the current message will be completed automatically by the function in the queue).
    else:
        sourceQueueHelper.send_to_queue(message_body,encoded=True,visibility_timeout=retry_invisibility_timeout_in_seconds)    
        logging.error('Queue message processing failed but did not reach max-retries. Scheduling for retry in {} seconds. New message body: {}'.format(retry_invisibility_timeout_in_seconds,message_body))


def main(queueItem: func.QueueMessage):
    logging.getLogger().setLevel(logging.INFO)
    stop_run_time = datetime.fromtimestamp(time.time()) + timedelta(minutes=float(max_runtime_before_stopping_in_minutes))
    logging.info('Starting AlibabaCloud-QueueTrigger program at {} stop_run_time is {}'.format(time.ctime(int(time.time())),stop_run_time) )

    if not ali_endpoint or not ali_accessKeyId or not ali_accessKey:
        raise Exception("Endpoint, AliCloudAccessKeyId and AliCloudAccessKey cannot be empty")
    
    pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
    match = re.match(pattern, str('https://' + customer_id + '.ods.opinsights.azure.com'))
    if (not match):
        raise Exception("Ali Cloud: Invalid Log Analytics Uri")
    
    message_body = json.loads(queueItem.get_body().decode('ascii').replace("'",'"'))
    queueItemId = queueItem.id
    logging.info('Queue message received with queue id: {}, message_body: {}, dequeue_count message: {}'.format(queueItemId,message_body,queueItem.dequeue_count))

    message_id = message_body.get('message_id')
    project = message_body.get('project')
    start_time = message_body.get('start_time')
    end_time = message_body.get('end_time')
    dequeue_count_str = message_body.get('dequeue_count')
    retrieved_log_stores_str = message_body.get('retrieved_log_stores')
    finished_log_stores_str = message_body.get('finished_log_stores')

    dequeue_count = 1
    if dequeue_count is not None:
        dequeue_count = int(dequeue_count_str)

    if (dequeue_count > max_queue_message_retries or queueItem.dequeue_count > max_queue_message_retries):
        logging.error("The queue messages reached its max allowed re-try attempts. Not retrying it again. message_body: {}".format(message_body))
        return

    if (project == "" or start_time == "" or end_time == ""):
        raise Exception("One of the storage queue message was missing or empty, could not perform operation. message_body: {}".format(message_body))
    
    start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    if (start_time_dt == datetime.min or end_time_dt == datetime.min or start_time_dt >= end_time_dt or end_time_dt > datetime.utcnow()):
        raise Exception("The time range included in the storage queue message was incorrect, could not perform operation. message_body: {}".format(message_body))
    
    retrieved_log_stores = []
    if retrieved_log_stores_str is not None and retrieved_log_stores_str != "":
        retrieved_log_stores = retrieved_log_stores_str.split(",")

    finished_log_stores = []    
    if finished_log_stores_str is not None and finished_log_stores_str != "":
        finished_log_stores = finished_log_stores_str.split(",")

    isSuccess = False
    
    try:
        client = LogClient(ali_endpoint, ali_accessKeyId, ali_accessKey, ali_token)
        isSuccess = process_logstores_and_send_to_LA(client, message_id, project, start_time_dt, end_time_dt, retrieved_log_stores, finished_log_stores, stop_run_time.timestamp(), dequeue_count)
    except Exception as err:
        logging.error("Error: AlibabaCloud data connector queue trigger execution failed with an internal server error. message_body: {}, Exception error text: {}".format(message_body, err))
        isSuccess = False

    if isSuccess == False:
        update_storage_queue_after_failure(queueItem, message_body, message_id, dequeue_count, retrieved_log_stores, finished_log_stores)
    else:
        logging.info("Finish processing queue message successfully. message_body: {}".format(message_body))