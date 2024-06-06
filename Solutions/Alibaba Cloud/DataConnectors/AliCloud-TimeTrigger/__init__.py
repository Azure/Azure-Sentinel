#from .ali_mock import LogClient, ListLogstoresRequest
from aliyun.log import *
import json
import azure.functions as func
import logging
import os
import time
import uuid
import base64
from datetime import datetime, timedelta
from .state_manager import StateManager, AzureStorageQueueHelper
from .ali_utils import TimeRangeSplitter
from .models import QueueMessage

fetch_delay_in_minutes = int(os.getenv('FetchDelay',10))
storage_connection_string = os.environ['AzureWebJobsStorage']
window_size_in_seconds = int(os.getenv('MaxWindowSizePerApiCallInSeconds',60))
ali_endpoint = os.environ.get('Endpoint', 'cn-hangzhou.log.aliyuncs.com')
ali_access_key_id = os.environ.get('AliCloudAccessKeyId', '')
ali_access_key = os.environ.get('AliCloudAccessKey', '')
token = ""
user_projects = os.environ.get("AliCloudProjects", '').replace(" ", "").split(',')
allowed_log_stores = os.environ.get("AliCloudLogStores", '').replace(" ", "").split(',')
max_queue_message_retries = int(os.environ.get('MaxQueueMessageRetries', '100'))

MAIN_QUEUE_NAME = "alibabacloud-queue-items"
POISON_QUEUE_NAME = "alibabacloud-queue-items-poison"
DEAD_LETTER_QUEUE_NAME = "alibabacloud-queue-items-dead-letter"
MAX_QUEUE_MESSAGES_MAIN_QUEUE = 1000
MAX_QUEUE_MESSAGES_PER_ITERATION_PROJECT = 1000
MAX_SCRIPT_EXECUTION_TIME_IN_MINUTES = 9
RETRY_INVISIBILITY_TIME_IN_SECONDS = 60
MIN_SPLIT_TIME_RANGE_AFTER_TIMEOUT_IN_SECONDS = 15
MAX_SPLIT_TIME_RANGE_CHUNKS_AFTER_TIMEOUT = 4


def GetAllProjectNames(client):
    if user_projects == ['']:
        projects = client.list_project(size=-1).get_projects()
        return list(map(lambda project_name: project_name["projectName"], projects))
    else:
        return user_projects


def GetProjectLogStores(client, project):
    request = ListLogstoresRequest(project)
    response = client.list_logstores(request)
    return response.get_logstores()


def GetEndTime():
    end_time = datetime.utcnow().replace(second=0, microsecond=0)
    end_time = (end_time - timedelta(minutes=fetch_delay_in_minutes))
    logging.info("End time for after default fetch delay {} minute(s) applied - {}".format(fetch_delay_in_minutes,end_time))        
    return end_time


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


def GetProjectDates(allProjectsDates, project):
    end_time = GetEndTime()
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time = end_time[:-4] + 'Z'
    
    return (allProjectsDates[project],end_time)


def GetAllProjectsDates(allProjects, stateManager):
    end_time = GetEndTime()
    default_time = (end_time - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    past_time = stateManager.get()
    project_list = {}
    if past_time is not None and len(past_time) > 0:
        if is_json(past_time):
            project_list = json.loads(past_time)  

            # if a new project has been retrieved (so it doesn't exist in the checkpoint), add it with default time (5 minutes ago)
            for project in allProjects:
                if project not in project_list:
                    project_list[project] = default_time[:-4] + 'Z'
        # Check if state file has non-date format. If yes, then set start_time to past_time
        else:
            try:
                newtime = datetime.strptime(past_time[:-1] + '.000Z', "%Y-%m-%dT%H:%M:%S.%fZ")
                newtime = newtime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                newtime = newtime[:-4] + 'Z'
                for project in allProjects:
                    project_list[project] = newtime
            except Exception as err:
                logging.info("Error while converting state. Its neither a json nor a valid date format {}".format(err))
                logging.info("Setting start time to get events for last 5 minutes.")
                for project in allProjects:
                    project_list[project] = default_time[:-4] + 'Z'
    else:
        logging.info("There is no last time point, trying to get events for last 5 minutes.")
        for project in allProjects:
            project_list[project] = default_time[:-4] + 'Z'

    return project_list


def check_if_script_runs_too_long(script_start_time):
    now = int(time.time())
    duration = now - script_start_time
    max_duration = int(MAX_SCRIPT_EXECUTION_TIME_IN_MINUTES * 60 * 0.9)
    return duration > max_duration            


def process_poison_queue_messages(mainQueueHelper, script_start_time, time_splitter):
    poisonQueueHelper = AzureStorageQueueHelper(connectionString=storage_connection_string, queueName=POISON_QUEUE_NAME)
    deadLetterQueueHelper = None
    
    poisonMessagesCount = poisonQueueHelper.get_queue_current_count()
    if poisonMessagesCount == 0:
        logging.info("Poison queue is empty. Nothing to do.")
        return
    
    logging.info("Poison queue has {} messages to process".format(poisonMessagesCount))

    while (True):
        if check_if_script_runs_too_long(script_start_time):
            logging.info("There are more poison queue messages to process, but ending processing for new data for this iteration, remaining will be processed in next iteration")
            return
        
        queueItem = poisonQueueHelper.deque_from_queue()
        if queueItem is None:
            logging.info("No more messages found in poison queue. Stopping.")
            return
        
        decoded_content = base64.b64decode(queueItem.content).decode('utf-8')
        message_body = json.loads(decoded_content.replace("'",'"'))
        queueItemId = queueItem.id
        queue_message = QueueMessage(message_body, queueItem.dequeue_count, max_queue_message_retries)

        logging.info('Poison queue message received with queue id: {}, message_body: {}, dequeue_count message: {}'.format(queueItemId,message_body,queueItem.dequeue_count))
        isSuccess = process_poison_queue_single_message(mainQueueHelper, queue_message, time_splitter)
        poisonQueueHelper.delete_queue_message(queueItem.id, queueItem.pop_receipt)

        if isSuccess == False:
            if deadLetterQueueHelper == None:
                deadLetterQueueHelper = AzureStorageQueueHelper(connectionString=storage_connection_string, queueName=DEAD_LETTER_QUEUE_NAME)
            deadLetterQueueHelper.send_to_queue(message_body,encoded=True)


def process_poison_queue_single_message(mainQueueHelper, queue_message, time_splitter):
    (is_valid, validation_error) = queue_message.validate()
    if is_valid == False:
        logging.error("Data loss - " + validation_error)
        return False

    queue_message.message_body["dequeue_count"] = queue_message.dequeue_count+1
    time_pairs = time_splitter.split_time_range_into_pairs(queue_message.start_time_dt, queue_message.end_time_dt)
    logging.info('Poison queue message did not reach max-retries so sending back to main queue. Assuming error was due to timeout, splitting message into {} parts (message_id: {}). Scheduling for retry immediately'.format(len(time_pairs),queue_message.message_id))

    if len(time_pairs) > 1:
        for pair in time_pairs:
            queue_message.message_body["start_time"] = pair[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            queue_message.message_body["end_time"] = pair[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            logging.info('Split poison queue meesage and sending to main queue - new message body: {}'.format(queue_message.message_body))    
            mainQueueHelper.send_to_queue(queue_message.message_body,encoded=True)
    else:
        logging.info('Cannot split poison queue meesage further since it reached minimal time range - sending to main queue as is - new message body: {}'.format(queue_message.message_body))    
        mainQueueHelper.send_to_queue(queue_message.message_body,encoded=True)

    return True


def format_messages_for_queue_and_add(start_time, end_time, project, log_stores, mainQueueHelper, allowed_log_stores):
    queue_body = {}
    queue_body["start_time"] = start_time
    queue_body["end_time"] = end_time
    queue_body["project"] = project
    queue_body["dequeue_count"] = 1
    filtered_stores = []

    for log_store in log_stores:
        # Filter out unsupported log stores, if an allow-list was configured
        if allowed_log_stores != [] and allowed_log_stores != ['']:
            if log_store.lower() not in allowed_log_stores:
                filtered_stores.append(log_store)
                continue

        queue_body["log_store"] = log_store
        queue_body["message_id"] = str(uuid.uuid4())

        mainQueueHelper.send_to_queue(queue_body,encoded=True)
        logging.info("Added to queue: {}".format(queue_body))
    
    if len(filtered_stores) > 0:
        logging.info("Stores filtered for project {}: {}".format(project, ','.join(filtered_stores)))


def main(mytimer: func.TimerRequest):
    logging.getLogger().setLevel(logging.INFO)
    if mytimer.past_due:
        logging.info('The timer is past due!')
    script_start_time = int(time.time())
    logging.info('Starting AliBabaCloud-TimeTrigger program at {}'.format(time.ctime(int(time.time()))) )

    if not ali_endpoint or not ali_access_key_id or not ali_access_key:
        raise Exception("Endpoint, AliCloudAccessKey and AliCloudAccessKeyId cannot be empty")
    
    try:
        mainQueueHelper = AzureStorageQueueHelper(connectionString=storage_connection_string, queueName=MAIN_QUEUE_NAME)

        logging.info("Check if we already have enough backlog to process in main queue. Maximum set is MAX_QUEUE_MESSAGES_MAIN_QUEUE: {} ".format(MAX_QUEUE_MESSAGES_MAIN_QUEUE))
        mainQueueCount = mainQueueHelper.get_queue_current_count()
        logging.info("Main queue size is {}".format(mainQueueCount))
        while (mainQueueCount) >= MAX_QUEUE_MESSAGES_MAIN_QUEUE:
            logging.info("Queue reached max number of pending messages: {}. Pending for 15 seconds before checking again".format(mainQueueCount))
            time.sleep(15)
            if check_if_script_runs_too_long(script_start_time):
                logging.info("Function running for too long. Stopping. We already have enough messages to process. Not scheduling and more items in this iteration.")
                return
            mainQueueCount = mainQueueHelper.get_queue_current_count()

        client = LogClient(ali_endpoint, ali_access_key_id, ali_access_key, token)
        allProjects = GetAllProjectNames(client)  
        stateManager = StateManager(connection_string=storage_connection_string)
        latestTimestamp = ""
        allProjectsDates = GetAllProjectsDates(allProjects, stateManager)
        allowed_log_stores_lower = [log_store.lower() for log_store in allowed_log_stores]

        for project in allProjects:
            logging.info("Started processing project: {}  (allowed log-stores: {})".format(project, allowed_log_stores))
            scheduled_operations = 0

            log_stores = GetProjectLogStores(client, project)
            
            if check_if_script_runs_too_long(script_start_time):
                logging.info("Some more backlog to process, but ending processing for new data for this iteration, remaining will be processed in next iteration")
                return
            
            start_time,end_time = GetProjectDates(allProjectsDates, project)
            if start_time is None:
                logging.info("There is no last time point, trying to get events for last one day.")
                end_time = datetime.strptime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ")
                start_time = (end_time - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            logging.info("Start time: {} and End time: {} for project {}".format(start_time,end_time,project))

            # Check if start_time is less than current UTC time minus 1 days. If yes, then set end_time to current UTC time minus 1 days
            if (datetime.utcnow() - timedelta(days=1)) > datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ"):
                logging.info("End time older than 1 days. Setting start time to current UTC time minus 1 days.")
                start_time = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                start_time = start_time[:-4] + 'Z'
            
            # check if difference between start_time and end_time is more than window_size_in_seconds, if yes, then split time window to make each call to window_size_in_seconds
            while (convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ") - convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds() > window_size_in_seconds:
                if check_if_script_runs_too_long(script_start_time):
                    logging.info("Some more backlog to process, but ending processing for new data for this iteration, remaining will be processed in next iteration")
                    return
                
                if scheduled_operations >= MAX_QUEUE_MESSAGES_PER_ITERATION_PROJECT:
                    logging.info("Sent max number of messages to queue ({}) for project {}. Will resume in next execution".format(scheduled_operations,project))
                    break  # Breaking the while loop so we only stop processing for the current project, but we do move on to the next project
                    
                loop_end_time = end_time
                # check if start_time is less than end_time. If yes, then process sending to queue
                if not(convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") >= convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ")):
                    end_time = (convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(seconds=window_size_in_seconds)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    end_time = end_time[:-4] + 'Z' 
                    format_messages_for_queue_and_add(start_time, end_time, project, log_stores, mainQueueHelper, allowed_log_stores_lower)
                    #update state file
                    latestTimestamp = end_time
                    allProjectsDates[project] = latestTimestamp
                    logging.info("Updating state file with latest timestamp : {} for project {}".format(latestTimestamp, project))
                    stateManager.post(str(json.dumps(allProjectsDates)))
                    start_time = end_time
                    end_time = loop_end_time
                    scheduled_operations += 1

            if (convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ") - convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds() <= window_size_in_seconds and not(convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") >= convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ")):
                format_messages_for_queue_and_add(start_time, end_time, project, log_stores, mainQueueHelper, allowed_log_stores_lower)
                #update state file
                latestTimestamp = end_time
                allProjectsDates[project] = latestTimestamp
                logging.info("Updating state file with latest timestamp : {} for project {}".format(latestTimestamp, project))
                stateManager.post(str(json.dumps(allProjectsDates)))
            logging.info("Finished processing project: {} ".format(project))

        time_splitter = TimeRangeSplitter(MIN_SPLIT_TIME_RANGE_AFTER_TIMEOUT_IN_SECONDS, MAX_SPLIT_TIME_RANGE_CHUNKS_AFTER_TIMEOUT)
        process_poison_queue_messages(mainQueueHelper, script_start_time, time_splitter)

    except Exception as err:
        logging.error("Error: AliBabaCloud timer trigger execution failed with an internal server error. Exception error text: {}".format(err))
        raise
    logging.info('Ending AliBabaCloud-TimeTrigger program at {}'.format(time.ctime(int(time.time()))) )