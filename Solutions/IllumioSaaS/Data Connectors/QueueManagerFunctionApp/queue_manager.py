import os
import time
import logging
import azure.functions as func
from .azure_storage_queue import AzureStorageQueueHelper

AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']
AWS_REGION_NAME = os.environ['AWS_REGION_NAME']
QUEUE_URL = os.environ['QUEUE_URL']
VISIBILITY_TIMEOUT = 1800
LINE_SEPARATOR = os.environ.get('lineSeparator',  '[\n\r\x0b\v\x0c\f\x1c\x1d\x85\x1e\u2028\u2029]+')
MAX_SCRIPT_EXEC_TIME_MINUTES = int(os.environ.get('MAX_SCRIPT_EXEC_TIME_MINUTES', 10))
FLOW_LOGS_CUSTOM_TABLE = os.environ['FLOW_LOGS_CUSTOM_TABLE']
AUDIT_LOGS_CUSTOM_TABLE = os.environ['AUDIT_LOGS_CUSTOM_TABLE']
AZURE_STORAGE_CONNECTION_STRING = os.environ['AzureWebJobsStorage'] 
MAX_QUEUE_MESSAGES_MAIN_QUEUE = int(os.environ.get('MAX_QUEUE_MESSAGES_MAIN_QUEUE', 80))


def check_if_script_runs_too_long(percentage, script_start_time):
    now = int(time.time())
    duration = now - script_start_time
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * percentage)
    return duration > max_duration

async def main(mytimer: func.TimerRequest):
    script_start_time = int(time.time())
    mainQueueHelper = AzureStorageQueueHelper(connectionString=AZURE_STORAGE_CONNECTION_STRING, queueName="python-queue-items")
    backlogQueueHelper = AzureStorageQueueHelper(connectionString=AZURE_STORAGE_CONNECTION_STRING, queueName="python-queue-items-backlog")                

    backlogQueueCount = backlogQueueHelper.get_queue_current_count()
    logging.info("File count in backlog queue is {}".format(backlogQueueCount))
        
    mainQueueCount = mainQueueHelper.get_queue_current_count()
    logging.info("File count in main queue is {}".format(mainQueueCount))        
    
    while True:
        # attempt to exhaust backlog queue and feed enough to mainQueue
        if backlogQueueCount > 0:
            if mainQueueCount >= MAX_QUEUE_MESSAGES_MAIN_QUEUE:
                logging.info('Backlog queue and main queue are at limits, do not process any new messages from sqs')
                return
            else:
                messageFromBacklog = backlogQueueHelper.deque_from_queue()
                if messageFromBacklog != None:
                    mainQueueHelper.send_to_queue(messageFromBacklog.content,False)
                    backlogQueueHelper.delete_queue_message(messageFromBacklog.id, messageFromBacklog.pop_receipt)

        else:
            return
        if check_if_script_runs_too_long(0.90, script_start_time):  
            logging.warn("Azure Queue manager has run close to 90 percentage of max time. Exiting")            
            return 
            