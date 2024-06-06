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
from .ali_utils import TimeRangeSplitter
from .models import ProcessingStatus, QueueMessage
#from .ali_mock import LogClient
from aliyun.log import *

# Constants
ALI_TOKEN = ""
LA_CHUNK_SIZE = 2000
LA_LOG_TYPE = "AliCloud"
MAX_RUNTIME_BEFORE_STOPPING_RETRIEVAL_IN_MINUTES = 8
MAX_RUNTIME_BEFORE_STOPPING_LA_SEND_IN_MINUTES = 9
MAX_LA_POST_RETRIES_AFTER_TRANSIENT_ERROR = 3
RETRY_INVISIBILITY_TIME_AFTER_ERROR_IN_SECONDS = 60
RETRY_INVISIBILITY_TIME_AFTER_TIMEOUT_IN_SECONDS = 0
MIN_SPLIT_TIME_RANGE_AFTER_TIMEOUT_IN_SECONDS = 15
MAX_SPLIT_TIME_RANGE_CHUNKS_AFTER_TIMEOUT = 4
QUEUE_SOURCE_NAME = "alibabacloud-queue-items"


def build_LA_post_signature(customer_id, workspace_shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(workspace_shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


def post_data_to_LA(logAnalyticsUri, customer_id, workspace_shared_key, message_id, chunk):
    body = json.dumps(chunk)
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    current_date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_LA_post_signature(customer_id, workspace_shared_key, current_date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': LA_LOG_TYPE,
        'x-ms-date': current_date
    }

    for attempt in range(MAX_LA_POST_RETRIES_AFTER_TRANSIENT_ERROR):
        try:
            response = requests.post(uri, data=body, headers=headers)

            if 200 <= response.status_code <= 299:
                logging.info("{} events were sent to LA (message_id: {})".format(len(chunk), message_id))
                return True
            elif response.status_code == 401:
                logging.error("LA post authentication failure. The authentication credentials are incorrect or missing. Error code: {} (message_id: {})".format(response.status_code, message_id))
                return False
            elif response.status_code >= 500:
                logging.error("LA post transient failure. Retry attempt {} out of {} max in 50ms. Error code: {} (message_id: {})".format(attempt+1, MAX_LA_POST_RETRIES_AFTER_TRANSIENT_ERROR, response.status_code, message_id))
                time.sleep(0.05)
            else:
                logging.error("LA post failure. Error code: {} (message_id: {})".format(response.status_code, message_id))
                return False
        except Exception as err:
            logging.error("LA post failure. Exception thrown (message_id: {}). Exception error text: {}".format(message_id, err))
            return False

    logging.error("LA post transient failure reached max allowed re-tries - failing function. Error code: {} (message_id: {})".format(attempt, MAX_LA_POST_RETRIES_AFTER_TRANSIENT_ERROR, response.status_code, message_id))        
    return False


def get_data_in_chunks(data, chunk_size):
    chunk = []
    for index, line in enumerate(data):
        if index % chunk_size == 0 and index > 0:
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk


def send_data_to_LA_in_chunks(logAnalyticsUri, customer_id, workspace_shared_key, message_id, data, stop_run_time_LA_send_tmst):
    events_sent = 0

    for chunk in get_data_in_chunks(data=data, chunk_size=LA_CHUNK_SIZE):
        if time.time() > stop_run_time_LA_send_tmst:
            logging.error("Stopping processing in the middle of sending logs to LA since execution time exceeded its allotted time. Will continue in next retry (message_id: {})".format(message_id))
            return ProcessingStatus(is_failure=False, is_timeout=True)
        
        isSuccess = post_data_to_LA(logAnalyticsUri, customer_id, workspace_shared_key, message_id, chunk)
        if isSuccess == False:
            return ProcessingStatus(is_failure=True, is_timeout=False)
        
        events_sent += len(chunk)
    
    logging.info("Successfully sent {} events to LA (message_id: {})".format(events_sent, message_id))
    return ProcessingStatus(is_failure=False, is_timeout=False)

def process_logstore_and_send_to_LA(client, queue_message, topic_query, stop_run_time_retrieval_tmst, stop_run_time_LA_send_tmst, logAnalyticsUri, customer_id, workspace_shared_key):
    if time.time() > stop_run_time_retrieval_tmst:
        logging.error("Stopping processing before retrieving logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(queue_message.log_store, queue_message.project, queue_message.message_id))    
        return ProcessingStatus(is_failure=False, is_timeout=True)

    logs_to_send = []
    res = client.get_log_all(project=queue_message.project, logstore=queue_message.log_store, from_time=str(queue_message.start_time_dt), to_time=str(queue_message.end_time_dt), topic=None, query=topic_query)

    for logs in res:
        if time.time() > stop_run_time_retrieval_tmst:
            logging.error("Stopping processing in the middle of retrieving logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(queue_message.log_store, queue_message.project, queue_message.message_id))
            return ProcessingStatus(is_failure=False, is_timeout=True)
    
        internalLogs = logs.get_logs()
        if time.time() > stop_run_time_retrieval_tmst:
            logging.error("Stopping processing in the middle of retrieving logs after get_logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(queue_message.log_store, queue_message.project, queue_message.message_id))
            return ProcessingStatus(is_failure=False, is_timeout=True)
        
        for log in internalLogs:
            if time.time() > stop_run_time_retrieval_tmst:
                logging.error("Stopping processing in the middle of iterating through logs for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry  (message_id: {})".format(queue_message.log_store, queue_message.project, queue_message.message_id))
                return ProcessingStatus(is_failure=False, is_timeout=True)
            
            logs_to_send += [{"timestamp": log.timestamp, "source": log.source, "contents": log.contents}]
        
    logging.info("Finished retrieving all {} logs from {} logstore for {} project - sending to LA (message_id: {})".format(len(logs_to_send), queue_message.log_store, queue_message.project, queue_message.message_id))

    return send_data_to_LA_for_store(logAnalyticsUri, customer_id, workspace_shared_key, queue_message, logs_to_send, stop_run_time_LA_send_tmst)

    
def send_data_to_LA_for_store(logAnalyticsUri, customer_id, workspace_shared_key, queue_message, logs_to_send, stop_run_time_LA_send_tmst):
    if len(logs_to_send) == 0:
        return ProcessingStatus(is_failure=False, is_timeout=False)

    if time.time() > stop_run_time_LA_send_tmst:
        logging.error("Stopping processing before sending logs to LA for store {} for project {} since execution time exceeded its allotted time. Will continue in next retry (message_id: {})".format(queue_message.log_store, queue_message.project, queue_message.message_id))    
        return ProcessingStatus(is_failure=False, is_timeout=True)
    
    return send_data_to_LA_in_chunks(logAnalyticsUri, customer_id, workspace_shared_key, queue_message.message_id, logs_to_send, stop_run_time_LA_send_tmst)


def update_storage_queue_after_failure(sourceQueueHelper, time_splitter, queue_message, queue_dequeue_count, processing_status, max_queue_message_retries):
    queue_message.message_body["dequeue_count"] = queue_message.dequeue_count+1
    isDataLoss = queue_dequeue_count >= max_queue_message_retries or queue_message.dequeue_count >= max_queue_message_retries

    # If we reached the max allowed re-tries, it means we have data-loss.
    # Delete message from the source queue (why? because we don't want it to be re-tried automatically), and send that message to the poison-queue.
    if isDataLoss == True:
        logging.error("Processing of queue message reached max re-tries. Message moved to poison queue and will not be re-tried. Message body: {}".format(queue_message.message_body))
        raise Exception("Processing of queue message reached max re-tries. Message moved to poison queue and will not be re-tried. Message body: {}".format(queue_message.message_body))
    
    # If we haven't reached the max allowed re-tries, it means we don't have a data-loss;
    # For failures, we create a new similar message in the queue that will become visbile in 60 seconds for next retry (we take into account that the current message will be completed automatically by the function in the queue).
    # For timeout, we split the given message into multiple similar messages and send them to the queue (minimal time range is 15s)
    else:
        if processing_status.is_timeout == True:
            time_pairs = time_splitter.split_time_range_into_pairs(queue_message.start_time_dt, queue_message.end_time_dt)
            if len(time_pairs) > 1:
                logging.error('Queue message processing failed but did not reach max-retries. Due to timeout, splitting message into {} parts. Scheduling for retry in {} seconds'.format(len(time_pairs), RETRY_INVISIBILITY_TIME_AFTER_ERROR_IN_SECONDS))

                for pair in time_pairs:
                    queue_message.message_body["start_time"] = pair[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    queue_message.message_body["end_time"] = pair[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    logging.error('Split meesage: new message body: {}'.format(queue_message.message_body))
                    sourceQueueHelper.send_to_queue(queue_message.message_body,encoded=True,visibility_timeout=RETRY_INVISIBILITY_TIME_AFTER_TIMEOUT_IN_SECONDS)
                return

        sourceQueueHelper.send_to_queue(queue_message.message_body,encoded=True,visibility_timeout=RETRY_INVISIBILITY_TIME_AFTER_ERROR_IN_SECONDS)
        logging.error('Queue message processing failed but did not reach max-retries. Scheduling for retry in {} seconds. New message body: {}'.format(RETRY_INVISIBILITY_TIME_AFTER_ERROR_IN_SECONDS,queue_message.message_body))


def main(queueItem: func.QueueMessage):
    logging.getLogger().setLevel(logging.INFO)
    stop_run_time_retrieval = datetime.fromtimestamp(time.time()) + timedelta(minutes=float(MAX_RUNTIME_BEFORE_STOPPING_RETRIEVAL_IN_MINUTES))
    stop_run_time_LA_send = datetime.fromtimestamp(time.time()) + timedelta(minutes=float(MAX_RUNTIME_BEFORE_STOPPING_LA_SEND_IN_MINUTES))
    logging.info('Starting AlibabaCloud-QueueTrigger program at {} stop_run_time_retrieval is {}, stop_run_time_LA_send is {}'.format(time.ctime(int(time.time())),stop_run_time_retrieval, stop_run_time_LA_send) )

    required_env_vars = ['AzureWebJobsStorage', 'WorkspaceID', 'WorkspaceKey', 'AliCloudAccessKeyId', 'AliCloudAccessKey']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    ali_endpoint = os.environ.get('Endpoint', 'cn-hangzhou.log.aliyuncs.com')
    ali_accessKeyId = os.environ.get('AliCloudAccessKeyId')
    ali_accessKey = os.environ.get('AliCloudAccessKey')
    storage_connection_string = os.environ['AzureWebJobsStorage']
    customer_id = os.environ['WorkspaceID']
    max_queue_message_retries = int(os.environ.get('MaxQueueMessageRetries', '15'))
    workspace_shared_key = os.environ['WorkspaceKey']
    logAnalyticsUri = os.environ.get('logAnalyticsUri')

    allowed_topics = os.environ.get("AliCloudTopics", '').replace(" ", "").split(',')
    topic_query = None
    if allowed_topics != [] and allowed_topics != ['']:
        topic_query = ' or '.join([f'__topic__:{item}' for item in allowed_topics])

    if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
        logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

    pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
    match = re.match(pattern, str(logAnalyticsUri))
    if (not match):
        raise Exception("Ali Cloud: Invalid Log Analytics Uri")

    if not ali_endpoint or not ali_accessKeyId or not ali_accessKey:
        raise Exception("Endpoint, AliCloudAccessKeyId and AliCloudAccessKey cannot be empty")
    
    message_body = json.loads(queueItem.get_body().decode('ascii').replace("'",'"'))
    logging.info('Queue message received with queue id: {}, message_body: {}, dequeue_count message: {} (allowed topics: {})'.format(queueItem.id,message_body,queueItem.dequeue_count, allowed_topics))

    queue_dequeue_count = queueItem.dequeue_count
    queue_message = QueueMessage(message_body, queue_dequeue_count, max_queue_message_retries)

    (is_valid, validation_error) = queue_message.validate()
    if is_valid == False:
        logging.error(validation_error)
        raise Exception(validation_error)
    
    processing_status = ProcessingStatus(is_failure=False, is_timeout=False)
    time_splitter = TimeRangeSplitter(MIN_SPLIT_TIME_RANGE_AFTER_TIMEOUT_IN_SECONDS, MAX_SPLIT_TIME_RANGE_CHUNKS_AFTER_TIMEOUT)

    try:
        client = LogClient(ali_endpoint, ali_accessKeyId, ali_accessKey, ALI_TOKEN)
        processing_status = process_logstore_and_send_to_LA(client, queue_message, topic_query, stop_run_time_retrieval.timestamp(), stop_run_time_LA_send.timestamp(), logAnalyticsUri, customer_id, workspace_shared_key)
    except Exception as err:
        logging.error("Error: AlibabaCloud data connector queue trigger execution failed with an internal server error. message_body: {}, Exception error text: {}".format(message_body, err))
        processing_status.is_failure = True

    if processing_status.is_failure == False and processing_status.is_timeout == False:
        logging.info("Finish processing queue message successfully. message_body: {}".format(message_body))
    else:
        sourceQueueHelper = AzureStorageQueueHelper(storage_connection_string, QUEUE_SOURCE_NAME)
        update_storage_queue_after_failure(sourceQueueHelper, time_splitter, queue_message, queue_dequeue_count, processing_status, max_queue_message_retries)