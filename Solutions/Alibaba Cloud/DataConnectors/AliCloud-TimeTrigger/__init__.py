from .ali_mock import LogClient, ListLogstoresRequest
#from aliyun.log import *
import json
import azure.functions as func
import logging
import os
import time
import uuid
import base64
from .state_manager import StateManager, AzureStorageQueueHelper
from datetime import datetime, timedelta

customer_id = os.environ['WorkspaceID']
fetchDelayMinutes = int(os.getenv('FetchDelay',10))
shared_key = os.environ['WorkspaceKey']
connection_string = os.environ['AzureWebJobsStorage']
window_size_in_seconds = int(os.getenv('MaxWindowSizePerApiCallInSeconds',60))
aliEndpoint = os.environ.get('Endpoint', 'cn-hangzhou.log.aliyuncs.com')
aliAccessKeyId = os.environ.get('AliCloudAccessKeyId', '')
aliAccessKey = os.environ.get('AliCloudAccessKey', '')
token = ""
user_projects = os.environ.get("AliCloudProjects", '').replace(" ", "").split(',')
allowed_log_stores = os.environ.get("AliCloudLogStores", '').replace(" ", "").split(',')
max_queue_message_retries = int(os.environ.get('MaxQueueMessageRetries', '100'))

main_queue_name = "alibabacloud-queue-items"
poison_queue_name = "alibabacloud-queue-items-poison"
dead_letter_queue_name = "alibabacloud-queue-items-dead-letter"
max_queue_messages_main_queue = 1000
max_queue_messages_per_iteration_project = 1000
max_script_exec_time_minutes = 9
retry_invisibility_timeout_in_seconds = 60
min_split_time_range_seconds_after_timeout = 15
max_split_time_range_chunks_after_timeout = 4

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
    end_time = (end_time - timedelta(minutes=fetchDelayMinutes))
    logging.info("End time for after default fetch delay {} minute(s) applied - {}".format(fetchDelayMinutes,end_time))        
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
    max_duration = int(max_script_exec_time_minutes * 60 * 0.9)
    return duration > max_duration            


def process_poison_queue_messages(mainQueueHelper, script_start_time):
    poisonQueueHelper = AzureStorageQueueHelper(connectionString=connection_string, queueName=poison_queue_name)
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

        isSuccess = process_poison_queue_single_message(queueItem, message_body, mainQueueHelper)
        poisonQueueHelper.delete_queue_message(queueItem.id, queueItem.pop_receipt)

        if isSuccess == False:
            if deadLetterQueueHelper == None:
                deadLetterQueueHelper = AzureStorageQueueHelper(connectionString=connection_string, queueName=dead_letter_queue_name)
            deadLetterQueueHelper.send_to_queue(message_body,encoded=True)


def process_poison_queue_single_message(queueItem, message_body, mainQueueHelper):
    queueItemId = queueItem.id
    logging.info('Poison queue message received with queue id: {}, message_body: {}, dequeue_count message: {}'.format(queueItemId,message_body,queueItem.dequeue_count))

    message_id = message_body.get('message_id')
    project = message_body.get('project')
    log_store = message_body.get('log_store')
    start_time = message_body.get('start_time')
    end_time = message_body.get('end_time')
    dequeue_count_str = message_body.get('dequeue_count')

    dequeue_count = 1
    if dequeue_count_str is None:
        logging.error('Data loss - Poison queue message received with missing dequeue_count. Moving to dead letter queue. id: {}, message_body: {}, dequeue_count message: {}'.format(queueItem.id, message_body, queueItem.dequeue_count))
        return False
    
    dequeue_count = int(dequeue_count_str)
    if (dequeue_count >= max_queue_message_retries or queueItem.dequeue_count >= max_queue_message_retries):
        logging.error('Data loss - Poison queue message reached its max retry count. Moving to dead letter queue. id: {}, message_body: {}, dequeue_count message: {}'.format(queueItem.id, message_body, queueItem.dequeue_count))
        return False

    if (project == "" or project is None or log_store == "" or log_store is None or start_time == "" or start_time is None or end_time == "" or end_time is None):
        logging.error("Data loss - One of the poison queue message properties was missing or empty. Moving to dead letter queue. message_body: {}".format(message_body))
        return False
    
    start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    if (start_time_dt == datetime.min or end_time_dt == datetime.min or start_time_dt >= end_time_dt or end_time_dt > datetime.utcnow()):
        logging.error("Data loss - The time range included in the poison queue message was incorrect. Moving to dead letter queue. message_body: {}".format(message_body))
        return False

    message_body["dequeue_count"] = dequeue_count+1

    time_pairs = split_time_into_pairs(start_time_dt, end_time_dt)
    logging.info('Poison queue message did not reach max-retries so sending back to main queue. Assuming error was due to timeout, splitting message into {} parts (message_id: {}). Scheduling for retry immediately'.format(len(time_pairs),message_id))

    for pair in time_pairs:
        message_body["start_time"] = pair[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        message_body["end_time"] = pair[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        logging.info('Split poison queue meesage and sending to main queue - new message body: {}'.format(message_body))    
        mainQueueHelper.send_to_queue(message_body,encoded=True)

    return True


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

    if not aliEndpoint or not aliAccessKeyId or not aliAccessKey:
        raise Exception("Endpoint, AliCloudAccessKey and AliCloudAccessKeyId cannot be empty")
    
    try:
        mainQueueHelper = AzureStorageQueueHelper(connectionString=connection_string, queueName=main_queue_name)
        
        logging.info("Check if we already have enough backlog to process in main queue. Maximum set is max_queue_messages_main_queue: {} ".format(max_queue_messages_main_queue))
        mainQueueCount = mainQueueHelper.get_queue_current_count()
        logging.info("Main queue size is {}".format(mainQueueCount))
        while (mainQueueCount) >= max_queue_messages_main_queue:
            logging.info("Queue reached max number of pending messages: {}. Pending for 15 seconds before checking again".format(mainQueueCount))
            time.sleep(15)
            if check_if_script_runs_too_long(script_start_time):
                logging.info("Function running for too long. Stopping. We already have enough messages to process. Not scheduling and more items in this iteration.")
                return
            mainQueueCount = mainQueueHelper.get_queue_current_count()

        client = LogClient(aliEndpoint, aliAccessKeyId, aliAccessKey, token)
        allProjects = GetAllProjectNames(client)  
        stateManager = StateManager(connection_string=connection_string)
        latestTimestamp = ""
        allProjectsDates = GetAllProjectsDates(allProjects, stateManager)
        allowed_log_stores = [log_store.lower() for log_store in allowed_log_stores]

        for project in allProjects:
            logging.info("Started processing project: {} ".format(project))
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
                
                if scheduled_operations >= max_queue_messages_per_iteration_project:
                    logging.info("Sent max number of messages to queue ({}) for project {}. Will resume in next execution".format(scheduled_operations,project))
                    break  # Breaking the while loop so we only stop processing for the current project, but we do move on to the next project
                    
                loop_end_time = end_time
                # check if start_time is less than end_time. If yes, then process sending to queue
                if not(convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") >= convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ")):
                    end_time = (convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(seconds=window_size_in_seconds)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    end_time = end_time[:-4] + 'Z' 
                    format_messages_for_queue_and_add(start_time, end_time, project, log_stores, mainQueueHelper, allowed_log_stores)
                    #update state file
                    latestTimestamp = end_time
                    allProjectsDates[project] = latestTimestamp
                    logging.info("Updating state file with latest timestamp : {} for project {}".format(latestTimestamp, project))
                    stateManager.post(str(json.dumps(allProjectsDates)))
                    start_time = end_time
                    end_time = loop_end_time
                    scheduled_operations += 1

            if (convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ") - convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds() <= window_size_in_seconds and not(convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") >= convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ")):
                format_messages_for_queue_and_add(start_time, end_time, project, log_stores, mainQueueHelper, allowed_log_stores)
                #update state file
                latestTimestamp = end_time
                allProjectsDates[project] = latestTimestamp
                logging.info("Updating state file with latest timestamp : {} for project {}".format(latestTimestamp, project))
                stateManager.post(str(json.dumps(allProjectsDates)))
            logging.info("Finished processing project: {} ".format(project))

        process_poison_queue_messages(mainQueueHelper, script_start_time)

    except Exception as err:
        logging.error("Error: AliBabaCloud timer trigger execution failed with an internal server error. Project: {}, Exception error text: {}".format(project,err))
        raise
    logging.info('Ending AliBabaCloud-TimeTrigger program at {}'.format(time.ctime(int(time.time()))) )