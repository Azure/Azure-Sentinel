import os
import json
from aiobotocore.session import get_session
import time
import logging
import azure.functions as func
from azure.storage.queue import QueueServiceClient
from azure.core.exceptions import ResourceExistsError
import base64
from dateutil import parser

AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']
AWS_REGION_NAME = os.environ['AWS_REGION_NAME']
QUEUE_URL = os.environ['QUEUE_URL']
VISIBILITY_TIMEOUT = 1800
LINE_SEPARATOR = os.environ.get('lineSeparator',  '[\n\r\x0b\v\x0c\f\x1c\x1d\x85\x1e\u2028\u2029]+')
connection_string = os.environ['AzureWebJobsStorage']
AZURE_STORAGE_CONNECTION_STRING = os.environ['AzureWebJobsStorage']
MAX_QUEUE_MESSAGES_MAIN_QUEUE = int(os.environ.get('MAX_QUEUE_MESSAGES_MAIN_QUEUE', 80))
MAX_SCRIPT_EXEC_TIME_MINUTES = int(os.environ.get('MAX_SCRIPT_EXEC_TIME_MINUTES', 10))
REQUIRE_SECONDARY_STRING = os.environ.get('USER_SELECTION_REQUIRE_SECONDARY', 'false')

if REQUIRE_SECONDARY_STRING.lower() == "true":
    REQUIRE_SECONDARY = True
else:
    REQUIRE_SECONDARY = False

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

async def main(mytimer: func.TimerRequest):
    script_start_time = int(time.time())
   
    logging.info("Creating SQS connection")
    async with _create_sqs_client() as client:
            mainQueueHelper = AzureStorageQueueHelper(connectionString=AZURE_STORAGE_CONNECTION_STRING, queueName="python-queue-items")
            backlogQueueHelper = AzureStorageQueueHelper(connectionString=AZURE_STORAGE_CONNECTION_STRING, queueName="python-queue-items-backlog")    

            logging.info("Check if we already have enough backlog to process")
            mainQueueCount = mainQueueHelper.get_queue_current_count()
            logging.info("Main queue size is {}".format(mainQueueCount))
            while (mainQueueCount ) >= MAX_QUEUE_MESSAGES_MAIN_QUEUE:
                time.sleep(15)
                if check_if_script_runs_too_long(0.7, script_start_time):
                    logging.warn("We already have queue already have enough messages to process. Not clearing any backlog or reading a new SQS message in this iteration.")
                    return
                mainQueueCount = mainQueueHelper.get_queue_current_count()

            logging.info("Check if backlog queue have any records.")
            backlogQueueCount = backlogQueueHelper.get_queue_current_count()
            logging.info("Backlog queue size is {}".format(backlogQueueCount))
            mainQueueCount = mainQueueHelper.get_queue_current_count()
            while backlogQueueCount > 0:
                while mainQueueCount >= MAX_QUEUE_MESSAGES_MAIN_QUEUE:
                    time.sleep(15)
                    mainQueueCount = mainQueueHelper.get_queue_current_count()
                messageFromBacklog = backlogQueueHelper.deque_from_queue()
                if messageFromBacklog != None:
                    mainQueueHelper.send_to_queue(messageFromBacklog.content,False)
                    backlogQueueHelper.delete_queue_message(messageFromBacklog.id, messageFromBacklog.pop_receipt)
                    backlogQueueCount = backlogQueueHelper.get_queue_current_count()
                    mainQueueCount = mainQueueHelper.get_queue_current_count()
                if check_if_script_runs_too_long(0.7, script_start_time):
                    logging.warn("Main queue already have enough messages to process. Read messages from backlog queue but not reading a new SQS message in this iteration.")
                    return

            if check_if_script_runs_too_long(0.5, script_start_time):
                logging.warn("Queue already have enough messages to process. Read all messages from backlog queue but not reading a new SQS message in this iteration.")
                return

            logging.info('Trying to check messages off the SQS...')
            try:
                response = await client.receive_message(
                    QueueUrl=QUEUE_URL,
                    WaitTimeSeconds=2,
                    VisibilityTimeout=VISIBILITY_TIMEOUT
                )
                if 'Messages' in response:
                    for msg in response['Messages']:
                        body_obj = json.loads(msg["Body"])
                        if "files" not in body_obj.keys():
                            logging.error("SQS message not in correct format")
                            break
                        logging.info("Got message with MessageId {}. Start processing {} files from Bucket: {}. Path prefix: {}. Timestamp: {}.".format(msg["MessageId"], body_obj["fileCount"], body_obj["bucket"], body_obj["pathPrefix"], body_obj["timestamp"]))
                        
                        diffFromNow = int(time.time()*1000) - int(body_obj["timestamp"])
                        if diffFromNow >= 3600:
                            logging.warn("More than 1 hour old records are getting processed now. This indicates requirement for additional function app.")
                        
                            await download_message_files_queue(mainQueueHelper, backlogQueueHelper, msg["MessageId"], body_obj)
                        logging.info("Finished processing {} files from MessageId {}. Bucket: {}. Path prefix: {}".format(body_obj["fileCount"], msg["MessageId"], body_obj["bucket"], body_obj["pathPrefix"]))
                        try:
                            await client.delete_message(
                                QueueUrl=QUEUE_URL,
                                ReceiptHandle=msg['ReceiptHandle']
                            )
                        except Exception as e:
                            logging.error("Error during deleting message with MessageId {} from queue. Bucket: {}. Path prefix: {}. Error: {}".format(msg["MessageId"], body_obj["bucket"], body_obj["pathPrefix"], e))
                else:
                    logging.info('No messages in SQS. Re-trying to check...')
            except Exception as e:
                logging.warn("Processing the SQS Message failed. Error: {}".format(e))

# This method is used to download all bucket names mentioned in the SQS message and send to Azure Storage Queue
# mainQueueHelper : AzureStorageQueueHelper
# backlogQueueHelper : AzureStorageQueueHelper
# messageId : string
# msg : string
async def download_message_files_queue(mainQueueHelper, backlogQueueHelper, messageId, msg):
    for s3_file in msg['files']:
        link = s3_file['path']
        if not(REQUIRE_SECONDARY) and "fdrv2/" in link:
            logging.info('Skip processing a secondary data bucket {}.'.format(link))
            continue
                        
        body = {}
        body["messageId"] = messageId
        body["link"] = link
        body["bucket"] = msg["bucket"]
        if mainQueueHelper.get_queue_current_count() >= MAX_QUEUE_MESSAGES_MAIN_QUEUE:
            backlogQueueHelper.send_to_queue(body,True)
        else:
            mainQueueHelper.send_to_queue(body,True)

class AzureStorageQueueHelper:
    def __init__(self,connectionString,queueName):
        self.__service_client = QueueServiceClient.from_connection_string(conn_str=connectionString)
        self.__queue = self.__service_client.get_queue_client(queueName)
        try:
            self.__queue.create_queue()
        except ResourceExistsError:
            # Resource exists
            pass
    
    # Helper function to encode message in base64
    def base64Encoded(self,message):
        messageString = str(message)
        message_bytes = messageString.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message

    # This method is used to read messages from the queue. 
    # This will pop the message from the queue (deque operation)
    def deque_from_queue(self):
        message = self.__queue.receive_message()
        return message

    # This method send data into the queue
    def send_to_queue(self, message, encoded):
        if encoded:
            self.__queue.send_message(self.base64Encoded(message))
        else:
            self.__queue.send_message(message)
    
    # This method deletes the message based on messageId
    def delete_queue_message(self, messageId, popReceipt):
        self.__queue.delete_message(messageId,popReceipt)

    # This method reads an approximate count of messages in the queue
    def get_queue_current_count(self):
        properties = self.__queue.get_queue_properties()
        return properties.approximate_message_count