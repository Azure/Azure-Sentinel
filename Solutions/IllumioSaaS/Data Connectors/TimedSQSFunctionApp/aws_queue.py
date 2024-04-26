import os
import json
from aiobotocore.session import get_session
import time
import logging
import azure.functions as func
import urllib.parse
from .azure_storage_queue import AzureStorageQueueHelper
import traceback
import base64

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
MAX_ACCUMULATED_FILE_SIZE = 500*1000 # 500kb since 64kb is limit per sqs message; tried earlier with 10kb
MAX_QUEUE_SIZE = 64*1000 # 64KB
QUEUE_LIMIT = 0.5 * MAX_QUEUE_SIZE #32kb
LOGS_TO_CONSUME = os.environ.get('LogTypes', 'All') # by default, ingest all
sentinel_connectors = {}

# Defining the SQS Client object based on AWS Credentials
def _create_sqs_client():
    sqs_session = get_session()
    return sqs_session.create_client(
                                    'sqs', 
                                    region_name=AWS_REGION_NAME,
                                    aws_access_key_id=AWS_KEY, 
                                    aws_secret_access_key=AWS_SECRET
                                    )

# This method checks if the script has ran "percentage" amount of time from starting of the script
# percentage: double
# script_start_time : datetime
def check_if_script_runs_too_long(percentage, script_start_time):
    now = int(time.time())
    duration = now - script_start_time
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * percentage)
    return duration > max_duration

def process_body_obj(body):
    # body is a hash of Records. Records is an array that contains s3 object's key and file size
     
    record = body['Records'][0] # typically one record
    file_path = record['s3']['object']['key'] # full path to s3
    file_size = record['s3']['object']['size'] # in bytes
    bucket_name = record['s3']['bucket']['name']
    
    return file_path, file_size, bucket_name

def getStringSize(file_arr):
    message_bytes = str(file_arr).encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return len(base64_bytes)

def split_request_payload(file_arr):
    mid = len(file_arr)//2
    return file_arr[:mid], file_arr[mid:]

def enqueue_message(mainQueueHelper, backlogQueueHelper, file_arr):
    if mainQueueHelper.get_queue_current_count() >= MAX_QUEUE_MESSAGES_MAIN_QUEUE:
        backlogQueueHelper.send_to_queue(file_arr,True)
    else:
        mainQueueHelper.send_to_queue(file_arr,True)

def fileToBeFiltered(file_path):
    if LOGS_TO_CONSUME == 'All':
        return False 
    
    if 'auditable' in file_path:
        return 'Flow Summaries' in LOGS_TO_CONSUME            
    else:
        return 'Auditable Events' in LOGS_TO_CONSUME


async def download_message_files_queue(mainQueueHelper, backlogQueueHelper, file_arr):
    if len(file_arr) > 0:
        if getStringSize(file_arr) >= QUEUE_LIMIT: # greater than 32kb; each queue element can be upto 64kb in size
            first_half, second_half = split_request_payload(file_arr)            
            enqueue_message(mainQueueHelper, backlogQueueHelper, first_half)
            enqueue_message(mainQueueHelper, backlogQueueHelper, second_half)
        else:
            enqueue_message(mainQueueHelper, backlogQueueHelper, file_arr)

# Ensure flushing messages happens during these times:
#        1. When script has reached 90% of execution time
#        2. When files accumulated has crossed MAX_ACCUMULATED_FILE_SIZE
#        3. When there are no more messages in SQS
#        4. Check if user chose a specific log type or wants all logs types to be processed, in this case, lesser storage         
async def main(mytimer: func.TimerRequest):
    #logger = logging.getLogger('azure')
    #logger.setLevel(logging.INFO)

    script_start_time = int(time.time())

    async with _create_sqs_client() as client:
        mainQueueHelper = AzureStorageQueueHelper(connectionString=AZURE_STORAGE_CONNECTION_STRING, queueName="python-queue-items")
        backlogQueueHelper = AzureStorageQueueHelper(connectionString=AZURE_STORAGE_CONNECTION_STRING, queueName="python-queue-items-backlog")                
        files_processed = 0
        accumulated_file_size = 0 # logic is to accumulate file sizes upto MAX_ACCUMULATED_FILE_SIZE
        file_arr = []

        while True:
            try:
                # This should return 1 message from SQS only
                response = await client.receive_message(QueueUrl=QUEUE_URL, WaitTimeSeconds=2, VisibilityTimeout=VISIBILITY_TIMEOUT)

                if 'Messages' in response: # this is an array
                    for msg in response['Messages']: # typically only one message since client.receive_message retrieves only one msg by default                        
                        body_obj = json.loads(msg['Body'])
                        file_path, file_size, bucket_name = process_body_obj(body_obj)

                        if fileToBeFiltered(file_path):
                            logging.warn('[AWSQueue] Skipping file since logs to be consumed is {}, but file is {}'.format(LOGS_TO_CONSUME, file_path))
                            continue                        

                        files_processed += 1

                        accumulated_file_size += file_size
                            
                        file_arr.append({"link": urllib.parse.unquote(file_path),
                                         "file_size": file_size,
                                         "bucket_name": bucket_name,
                                         "sqs_message_id": msg['MessageId']
                                         })
                        
                        try:
                            await client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg['ReceiptHandle'])
                        except Exception as e:
                            logging.error("[AWSQueue] Error during deleting message with MessageId {} from queue. Bucket: {}. Error: {}".format(msg['MessageId'], body_obj['s3']['bucket'], e))                            
                            continue
                        
                    if check_if_script_runs_too_long(0.90, script_start_time):  
                        logging.warn('[AWSQueue]SQS Queue manager has run close to 90 percentage of max time. Flushing files to queue before termination')
                        await download_message_files_queue(mainQueueHelper, backlogQueueHelper, file_arr)
                        return                         

                else:
                    logging.info("[AWSQueue] There are no messages in SQS, attempting to flush files seen so far")
                    await download_message_files_queue(mainQueueHelper, backlogQueueHelper, file_arr)
                    file_stats = {"Trigger":"Timer", "Type":"FileStats", "file_count": len(file_arr), "azure_queue_size": getStringSize(file_arr), "aggregated_file_size": accumulated_file_size}
                    logging.info(json.dumps(file_stats))
                    return
                
                # decide whether file size accumulated so far has reached limit or not
                # if not, wait, else if nothing else left, just add it to queue and terminate function
                        
                if getStringSize(file_arr) >= QUEUE_LIMIT or accumulated_file_size >= MAX_ACCUMULATED_FILE_SIZE:
                    await download_message_files_queue(mainQueueHelper, backlogQueueHelper, file_arr)
                    file_stats = {"Trigger":"Timer", "Type":"FileStats", "file_count": len(file_arr), "azure_queue_size": getStringSize(file_arr), "aggregated_file_size": accumulated_file_size}
                    logging.info(json.dumps(file_stats))
                    accumulated_file_size = 0
                    file_arr.clear()                    
                    

                if check_if_script_runs_too_long(0.90, script_start_time):  
                    logging.warn('[AWSQueue] SQS Queue manager has run close to 90 percentage of max time. Flushing files to queue before termination')
                    await download_message_files_queue(mainQueueHelper, backlogQueueHelper, file_arr)
                    return 

            except Exception as e:
                logging.warning(traceback.format_exc())
                return                