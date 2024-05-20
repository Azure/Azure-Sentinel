#from .ali_mock import LogClient
from aliyun.log import *
import json
import azure.functions as func
import logging
import os
import time
import uuid
from .state_manager import StateManager, AzureStorageQueueHelper
from datetime import datetime, timedelta

customer_id = os.environ['WorkspaceID']
fetchDelayMinutes = os.getenv('FetchDelay',10)
shared_key = os.environ['WorkspaceKey']
connection_string = os.environ['AzureWebJobsStorage']
window_size_in_seconds = int(os.getenv('MaxWindowSizePerApiCallInSeconds',60))
aliEndpoint = os.environ.get('Endpoint', 'cn-hangzhou.log.aliyuncs.com')
aliAccessKeyId = os.environ.get('AliCloudAccessKeyId', '')
aliAccessKey = os.environ.get('AliCloudAccessKey', '')
token = ""
user_projects = os.environ.get("AliCloudProjects", '').replace(" ", "").split(',')

QUEUE_NAME = "alibabacloud-queue-items"
MAX_QUEUE_MESSAGES_MAIN_QUEUE = 1000
MAX_QUEUE_MESSAGES_PER_ITERATION_PROJECT = 1000
MAX_SCRIPT_EXEC_TIME_MINUTES = 9

def GetAllProjectNames():
    if user_projects == ['']:
        client = LogClient(aliEndpoint, aliAccessKeyId, aliAccessKey, token)
        projects = client.list_project(size=-1).get_projects()
        return list(map(lambda project_name: project_name["projectName"], projects))
    else:
        return user_projects

def GetEndTime():
    end_time = datetime.utcnow().replace(second=0, microsecond=0)
    end_time = (end_time - timedelta(minutes=int(fetchDelayMinutes)))
    logging.info("End time for after default fetch delay {} minute(s) applied - {}".format(int(fetchDelayMinutes),end_time))        
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
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.9)
    return duration > max_duration            

def format_message_for_queue_and_add(start_time, end_time, project, mainQueueHelper):
    queue_body = {}
    queue_body["message_id"] = str(uuid.uuid4())
    queue_body["start_time"] = start_time
    queue_body["end_time"] = end_time
    queue_body["project"] = project
    queue_body["dequeue_count"] = 1
    mainQueueHelper.send_to_queue(queue_body,True)
    logging.info("Added to queue: {}".format(queue_body))
    

def main(mytimer: func.TimerRequest):
    logging.getLogger().setLevel(logging.INFO)
    if mytimer.past_due:
        logging.info('The timer is past due!')
    script_start_time = int(time.time())
    logging.info('Starting AliBabaCloud-TimeTrigger program at {}'.format(time.ctime(int(time.time()))) )

    if not aliEndpoint or not aliAccessKeyId or not aliAccessKey:
        raise Exception("Endpoint, AliCloudAccessKey and AliCloudAccessKeyId cannot be empty")
    
    mainQueueHelper = AzureStorageQueueHelper(connectionString=connection_string, queueName=QUEUE_NAME)
    
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

    allProjects = GetAllProjectNames()  
    stateManager = StateManager(connection_string=connection_string)
    latestTimestamp = ""
    allProjectsDates = GetAllProjectsDates(allProjects, stateManager)

    for project in allProjects:
        logging.info("Started processing project: {} ".format(project))
        scheduled_operations = 0
        
        if check_if_script_runs_too_long(script_start_time):
            logging.info("Some more backlog to process, but ending processing for new data for this iteration, remaining will be processed in next iteration")
            return
        try:
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
                    format_message_for_queue_and_add(start_time, end_time, project, mainQueueHelper)
                    #update state file
                    latestTimestamp = end_time
                    allProjectsDates[project] = latestTimestamp
                    logging.info("Updating state file with latest timestamp : {} for project {}".format(latestTimestamp, project))
                    stateManager.post(str(json.dumps(allProjectsDates)))
                    start_time = end_time
                    end_time = loop_end_time
                    scheduled_operations += 1

            if (convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ") - convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds() <= window_size_in_seconds and not(convertToDatetime(start_time,"%Y-%m-%dT%H:%M:%S.%fZ") >= convertToDatetime(end_time,"%Y-%m-%dT%H:%M:%S.%fZ")):
                format_message_for_queue_and_add(start_time, end_time, project, mainQueueHelper)
                #update state file
                latestTimestamp = end_time
                allProjectsDates[project] = latestTimestamp
                logging.info("Updating state file with latest timestamp : {} for project {}".format(latestTimestamp, project))
                stateManager.post(str(json.dumps(allProjectsDates)))
            logging.info("Finished processing project: {} ".format(project))

        except Exception as err:
            logging.error("Error: AliBabaCloud timer trigger execution failed with an internal server error. Project: {}, Exception error text: {}".format(project,err))
            raise
    logging.info('Ending AliBabaCloud-TimeTrigger program at {}'.format(time.ctime(int(time.time()))) )