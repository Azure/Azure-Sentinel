import asyncio
import os
import sys
import asyncio
import json
from botocore.config import Config as BotoCoreConfig
from aiobotocore.session import get_session
from gzip_stream import AsyncGZIPDecompressedStream
import re
from .sentinel_connector_async import AzureSentinelConnectorAsync
import time
import aiohttp
import logging
import azure.functions as func
import itertools
from operator import itemgetter
from .state_manager import StateManager
from azure.data.tables import TableServiceClient
import datetime

WORKSPACE_ID = os.environ['WorkspaceID']
SHARED_KEY = os.environ['WorkspaceKey']
LOG_TYPE = "CrowdstrikeLogs1"
AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']
AWS_REGION_NAME = os.environ['AWS_REGION_NAME']
QUEUE_URL = os.environ['QUEUE_URL']
VISIBILITY_TIMEOUT = 1800
LINE_SEPARATOR = os.environ.get('lineSeparator',  '[\n\r\x0b\v\x0c\f\x1c\x1d\x85\x1e\u2028\u2029]+')
connection_string = os.environ['AzureWebJobsStorage']
AZURE_STORAGE_CONNECTION_STRING = os.environ['AzureWebJobsStorage']
HTTP_FUNCTION_APP_URL = os.environ['HTTP_FUNCTION_APP_URL']

# Defines how many files can be processed simultaneously
MAX_CONCURRENT_PROCESSING_FILES = int(os.environ.get('MAX_CONCURRENT_PROCESSING_FILES', 20))

# Defines max number of events that can be sent in one request to Azure Sentinel
MAX_BUCKET_SIZE = int(os.environ.get('MAX_BUCKET_SIZE', 2000))

MAX_FILES_PER_INSTANCE = 2

LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')
if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")

drop_files_array = []

def _create_sqs_client():
    sqs_session = get_session()
    return sqs_session.create_client(
                                    'sqs', 
                                    region_name=AWS_REGION_NAME,
                                    aws_access_key_id=AWS_KEY, 
                                    aws_secret_access_key=AWS_SECRET
                                    )

def _create_s3_client():
    s3_session = get_session()
    boto_config = BotoCoreConfig(region_name=AWS_REGION_NAME, retries = {'max_attempts': 10, 'mode': 'standard'})
    return s3_session.create_client(
                                    's3',
                                    region_name=AWS_REGION_NAME,
                                    aws_access_key_id=AWS_KEY,
                                    aws_secret_access_key=AWS_SECRET,
                                    config=boto_config
                                    )

def sort_files_by_bucket(array_obj):
    array_obj = sorted(array_obj, key=itemgetter('bucket'))
    sorted_array = []
    temp_array = []
    for key, value in itertools.groupby(array_obj, key=itemgetter('bucket')):
        for i in value:
            temp_array.append({'path': i.get('path')})
        sorted_array.append({'bucket': key, 'files': temp_array})
    return sorted_array

async def main(mytimer: func.TimerRequest):
    script_start_time = int(time.time())
    
    connTable = AzureTableStorageConnector(AZURE_STORAGE_CONNECTION_STRING)
    table_service_client = connTable._create_table_service_client()

    logging.info("Gathering failed files.")
    failedFiles = []
    with table_service_client:
        currentTime = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        filterStr = "StatusTime ge datetime'{}' and Status eq 'FAILURE'".format(currentTime.strftime('%Y-%m-%dT%H:%M:%S'))
        logging.info(filterStr)
        result = connTable.query_table_data(filterStr)
        for entity in result:
             failedFiles.append({entity['Bucket'],entity['FileName']})

    logging.info("Processing {} failed files.".format(len(failedFiles)))
    if len(failedFiles):
        await download_message_failedfiles(failedFiles, session)
        logging.info("Finished processing failed files.")    
    else:
        logging.info("No failed files to process.")
    
    logging.info("Creating SQS connection")
    async with _create_sqs_client() as client:
        async with aiohttp.ClientSession() as session:
            logging.info('Trying to check messages off the queue...')
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
                            logging.error("Queue message not in correct format")
                            break
                        logging.info("Got message with MessageId {}. Start processing {} files from Bucket: {}. Path prefix: {}. Timestamp: {}.".format(msg["MessageId"], body_obj["fileCount"], body_obj["bucket"], body_obj["pathPrefix"], body_obj["timestamp"]))
                        await download_message_files(body_obj, session)
                        logging.info("Finished processing {} files from MessageId {}. Bucket: {}. Path prefix: {}".format(body_obj["fileCount"], msg["MessageId"], body_obj["bucket"], body_obj["pathPrefix"]))
                        try:
                            await client.delete_message(
                                QueueUrl=QUEUE_URL,
                                ReceiptHandle=msg['ReceiptHandle']
                            )
                        except Exception as e:
                            logging.error("Error during deleting message with MessageId {} from queue. Bucket: {}. Path prefix: {}. Error: {}".format(msg["MessageId"], body_obj["bucket"], body_obj["pathPrefix"], e))
                else:
                    logging.info('No messages in queue. Re-trying to check...')
            except KeyboardInterrupt:
                pass

async def _make_request(session, uri, body):
    async with session.post(uri, data=body) as response:
        await response.text()
        if 200 <= response.status <= 299:
            logging.info("Success {}".format(str(body)))
        elif 500 >= response.status:
            logging.info("File(s) took too long {}.".format(str(body)))
        else:
            logging.info("Failure {}.".format(str(body))) 

async def download_message_failedfiles(failedFiles, session):
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PROCESSING_FILES)
    uri = HTTP_FUNCTION_APP_URL
    async with _create_s3_client() as client:
        cors = []
        for s3_file in failedFiles:
            body = {}
            body["links"] = [s3_file["FileName"]]
            body["bucket"] = s3_file["bucket"]
            logging.info("Starting processing for {}.".format(str(body['links'])))
            cors.append(_make_request(session, uri, json.dumps(body)))            
            if len(cors) >= 100:
                await asyncio.gather(*cors)
                cors = []

        if (cors):
            await asyncio.gather(*cors)

async def download_message_files(msg, session):
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PROCESSING_FILES)
    uri = HTTP_FUNCTION_APP_URL
    async with _create_s3_client() as client:
        cors = []
        files = []
        for s3_file in msg['files']:
            if len(files) < MAX_FILES_PER_INSTANCE:
                files.append(s3_file)
                continue
            body = {}
            body["links"] = [file['path'] for file in files]
            body["bucket"] = msg["bucket"]
            logging.info("Starting processing for {}.".format(str(body['links'])))
            cors.append(_make_request(session, uri, json.dumps(body)))            
            files = []
            if len(cors) >= 100:
                await asyncio.gather(*cors)
                cors = []
            files.append(s3_file)

        if len(files):
            body = {}
            body["links"] = [file['path'] for file in files]
            body["bucket"] = msg["bucket"]
            logging.info("Starting processing for {}.".format(str(body['links'])))
            files = []
            cors.append(_make_request(session, uri, json.dumps(body)))            
            if len(cors) >= 100:
                await asyncio.gather(*cors)
                cors = []

        if (cors):
            await asyncio.gather(*cors)

class AzureTableStorageConnector:
    def __init__(self, conn_string):
        self.__conn_string = conn_string
        self.script_start_time = int(time.time())

    def _create_table_service_client(self):
        return TableServiceClient.from_connection_string(self.__conn_string, logging_enable=False)

    def _get_table_client(self,table_name):
        create_table_service_client = self._create_table_service_client()
        return create_table_service_client.create_table_if_not_exists(table_name=table_name)
    
    def query_table_data(self,filter):
        result = self._get_table_client("crowdstrikestatus").query_entities (filter)
        return result

    def ingest_table_data(self,blob_name,status):
        currentTime =  datetime.datetime.utcnow()
        my_status_record = {
            u'PartitionKey': blob_name,
            u'RowKey': blob_name + " - " + currentTime.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            u'StatusTime': datetime.datetime.utcnow(),
            u'Status': status
        }
        status_record = self._get_table_client("crowdstrikestatus").create_entity(entity=my_status_record)