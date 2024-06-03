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
from .state_manager import AzureStorageQueueHelper, ProcessingStatus
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
max_runtime_before_stopping_retrieval_in_minutes = 8
max_runtime_before_stopping_LA_send_in_minutes = 9
max_LA_post_retries_after_transient = 3
retry_invisibility_timeout_in_seconds = 60
min_split_time_range_seconds_after_timeout = 15
max_split_time_range_chunks_after_timeout = 4
queue_source_name = "alibabacloud-queue-items"


def build_LA_post_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


def post_data_to_LA(message_id, chunk):
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


def send_data_to_LA_in_chunks(message_id, data, stop_run_time_LA_send_tmst):
    events_sent = 0

    for chunk in get_data_in_chunks(data, chunk_size=la_chunk_size):
        if time.time() > stop_run_time_LA_send_tmst:
            logging.error("Stopping processing in the middle of sending logs to LA since execution time exceeded its allotted time. Will continue in next retry (message_id: {})".format(message_id))
            return ProcessingStatus(is_failure=False, is_timeout=True)
        
        isSuccess = post_data_to_LA(message_id, chunk)
        if isSuccess == False:
            return ProcessingStatus(is_failure=True, is_timeout=False)
        
        events_sent += len(chunk)
    
    logging.info("Successfully sent {} events to LA (message_id: {})".format(events_sent, message_id))
    return ProcessingStatus(is_failure=False, is_timeout=False)


def process_logstore_and_send_to_LA(client, message_id, project, logstore, start_time, end_time, stop_run_time_retrieval_tmst, stop_run_time_LA_send_tmst):
    if time.time() > stop_run_time_retrieval_tmst:
        logging.error("Stopping processing before retrieving logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(logstore, project, message_id))    
        return ProcessingStatus(is_failure=False, is_timeout=True)

    logs_to_send = []
    res = client.get_log_all(project, logstore, str(start_time), str(end_time), ali_topic)

    for logs in res:
        if time.time() > stop_run_time_retrieval_tmst:
            logging.error("Stopping processing in the middle of retrieving logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(logstore, project, message_id))
            return ProcessingStatus(is_failure=False, is_timeout=True)
    
        internalLogs = logs.get_logs()
        if time.time() > stop_run_time_retrieval_tmst:
            logging.error("Stopping processing in the middle of retrieving logs after get_logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(logstore, project, message_id))
            return ProcessingStatus(is_failure=False, is_timeout=True)
        
        for log in internalLogs:
            if time.time() > stop_run_time_retrieval_tmst:
                logging.error("Stopping processing in the middle of iterating through logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(logstore, project, message_id))
                return ProcessingStatus(is_failure=False, is_timeout=True)
            
            logs_to_send += [{"timestamp": log.timestamp, "source": log.source, "contents": log.contents}]
        
    logging.info("Finished retrieving all {} logs from {} logstore for {} project - sending to LA (message_id: {})".format(len(logs_to_send), logstore, project, message_id))

    return send_data_to_LA_for_store(message_id, project, logstore, logs_to_send, stop_run_time_LA_send_tmst)

    
def send_data_to_LA_for_store(message_id, project, logstore, logs_to_send, stop_run_time_LA_send_tmst):
    if len(logs_to_send) == 0:
        return ProcessingStatus(is_failure=False, is_timeout=False)

    if time.time() > stop_run_time_LA_send_tmst:
        logging.error("Stopping processing before sending logs to LA for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry (message_id: {})".format(logstore, project, message_id))    
        return ProcessingStatus(is_failure=False, is_timeout=True)
    
    return send_data_to_LA_in_chunks(message_id, logs_to_send, stop_run_time_LA_send_tmst)


def update_storage_queue_after_failure(queueItem, message_body, dequeue_count, start_time, end_time, processing_status):
    message_body["dequeue_count"] = dequeue_count+1
    isDataLoss = queueItem.dequeue_count >= max_queue_message_retries or dequeue_count >= max_queue_message_retries

    sourceQueueHelper = AzureStorageQueueHelper(connection_string, queue_source_name)

    # If we reached the max allowed re-tries, it means we have data-loss.
    # Delete message from the source queue (why? because we don't want it to be re-tried automatically), and send that message to the poison-queue.
    if isDataLoss == True:
        logging.error("Processing of queue message reached max re-tries. Message moved to poison queue and will not be re-tried. Message body: {}".format(message_body))
        raise Exception("Processing of queue message reached max re-tries. Message moved to poison queue and will not be re-tried. Message body: {}".format(message_body))
    
    # If we haven't reached the max allowed re-tries, it means we don't have a data-loss;
    # For failures, we create a new similar message in the queue that will become visbile in 60 seconds for next retry (we take into account that the current message will be completed automatically by the function in the queue).
    # For timeout, we split the given message into multiple similar messages and send them to the queue (minimal time range is 15s)
    else:
        if processing_status.is_timeout == True:
            time_pairs = split_time_into_pairs(start_time, end_time)
            if len(time_pairs) > 1:
                logging.error('Queue message processing failed but did not reach max-retries. Due to timeout, splitting message into {} parts. Scheduling for retry in {} seconds'.format(len(time_pairs), retry_invisibility_timeout_in_seconds))

                for pair in time_pairs:
                    message_body["start_time"] = pair[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    message_body["end_time"] = pair[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    logging.error('Split meesage: new message body: {}'.format(message_body))    
                    sourceQueueHelper.send_to_queue(message_body,encoded=True,visibility_timeout=0)
                return

        sourceQueueHelper.send_to_queue(message_body,encoded=True,visibility_timeout=retry_invisibility_timeout_in_seconds)
        logging.error('Queue message processing failed but did not reach max-retries. Scheduling for retry in {} seconds. New message body: {}'.format(retry_invisibility_timeout_in_seconds,message_body))


def split_time_into_pairs(start_time, end_time):
    # Calculate the total difference in seconds
    total_difference = int((end_time - start_time).total_seconds())

    # Ensure minimum difference of 15 seconds
    if total_difference < min_split_time_range_seconds_after_timeout:
        return [(start_time, end_time)]  # Single pair for differences less than 15 seconds

    # Calculate minimum possible pair duration (ensuring at least 15 seconds)
    min_pair_duration = max(min_split_time_range_seconds_after_timeout, total_difference // max_split_time_range_chunks_after_timeout) 

    # Check if 4 pairs fit with minimum difference
    if min_pair_duration * max_split_time_range_chunks_after_timeout <= total_difference:
        # Create pairs with minimum duration
        time_pairs = []
        current_time = start_time
        for i in range(max_split_time_range_chunks_after_timeout):
            if i == max_split_time_range_chunks_after_timeout-1:
                # Last pair: adjust duration to cover remaining difference
                next_time = end_time
            else:
                next_time = current_time + timedelta(seconds=min_pair_duration)
            time_pairs.append((current_time, next_time))
            current_time = next_time
        return time_pairs

    # Calculate maximum possible pairs (considering remaining difference)
    max_pairs = min(max_split_time_range_chunks_after_timeout, total_difference // min_pair_duration)

    # Create pairs with adjustments for remaining difference
    time_pairs = []
    current_time = start_time
    for i in range(max_pairs):
        if i == max_pairs - 1:
            # Last pair: adjust duration to cover remaining difference
            next_time = end_time
        else:
            next_time = current_time + timedelta(seconds=min_pair_duration)
        time_pairs.append((current_time, next_time))
        current_time = next_time

    return time_pairs  


def main(queueItem: func.QueueMessage):
    logging.getLogger().setLevel(logging.INFO)
    stop_run_time_retrieval = datetime.fromtimestamp(time.time()) + timedelta(minutes=float(max_runtime_before_stopping_retrieval_in_minutes))
    stop_run_time_LA_send = datetime.fromtimestamp(time.time()) + timedelta(minutes=float(max_runtime_before_stopping_LA_send_in_minutes))
    logging.info('Starting AlibabaCloud-QueueTrigger program at {} stop_run_time_retrieval is {}, stop_run_time_LA_send is {}'.format(time.ctime(int(time.time())),stop_run_time_retrieval, stop_run_time_LA_send) )

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
    log_store = message_body.get('log_store')
    start_time = message_body.get('start_time')
    end_time = message_body.get('end_time')
    dequeue_count_str = message_body.get('dequeue_count')

    dequeue_count = 1
    if dequeue_count_str is not None:
        dequeue_count = int(dequeue_count_str)

    if (dequeue_count >= max_queue_message_retries or queueItem.dequeue_count >= max_queue_message_retries):
        logging.error("The queue messages reached its max allowed re-try attempts. Not retrying it again. message_body: {}".format(message_body))
        raise Exception("The queue messages reached its max allowed re-try attempts. Not retrying it again. message_body: {}".format(message_body))

    if (project == "" or project is None or log_store == "" or log_store is None or start_time == "" or start_time is None or end_time == "" or end_time is None):
        logging.error("One of the storage queue message properties was missing or empty, could not perform operation. message_body: {}".format(message_body))
        raise Exception("One of the storage queue message properties was missing or empty, could not perform operation. message_body: {}".format(message_body))
    
    start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    if (start_time_dt == datetime.min or end_time_dt == datetime.min or start_time_dt >= end_time_dt or end_time_dt > datetime.utcnow()):
        logging.error("The time range included in the storage queue message was incorrect, could not perform operation. message_body: {}".format(message_body))
        raise Exception("The time range included in the storage queue message was incorrect, could not perform operation. message_body: {}".format(message_body))
    
    processing_status = ProcessingStatus(is_failure=False, is_timeout=False)
    
    try:
        client = LogClient(ali_endpoint, ali_accessKeyId, ali_accessKey, ali_token)
        processing_status = process_logstore_and_send_to_LA(client, message_id, project, log_store, start_time_dt, end_time_dt, stop_run_time_retrieval.timestamp(), stop_run_time_LA_send.timestamp())
    except Exception as err:
        logging.error("Error: AlibabaCloud data connector queue trigger execution failed with an internal server error. message_body: {}, Exception error text: {}".format(message_body, err))
        processing_status.is_failure = True

    if processing_status.is_failure == False and processing_status.is_timeout == False:
        logging.info("Finish processing queue message successfully. message_body: {}".format(message_body))
    else:
        update_storage_queue_after_failure(queueItem, message_body, dequeue_count, start_time_dt, end_time_dt, processing_status)