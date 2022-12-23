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

# Defines how many files can be processed simultaneously
MAX_CONCURRENT_PROCESSING_FILES = int(os.environ.get('MAX_CONCURRENT_PROCESSING_FILES', 20))

# Defines max number of events that can be sent in one request to Azure Sentinel
MAX_BUCKET_SIZE = int(os.environ.get('MAX_BUCKET_SIZE', 2000))

MAX_FILES_PER_INSTANCE = int(os.environ.get('MAX_FILES_PER_INSTANCE', 2))

MAX_SCRIPT_EXEC_TIME_MINUTES = 5

LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')
if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")

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

async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Starting script')
    script_start_time = int(time.time())
    logging.info('Concurrency parameters: MAX_CONCURRENT_PROCESSING_FILES {}, MAX_BUCKET_SIZE {}.'.format(MAX_CONCURRENT_PROCESSING_FILES, MAX_BUCKET_SIZE))
        
    connTable = AzureTableStorageConnector(AZURE_STORAGE_CONNECTION_STRING)
    table_service_client = connTable._create_table_service_client()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PROCESSING_FILES)

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        links = req_body.get('links')
        bucket = req_body.get('bucket')

    succMessage = ""
    errorMessage = ""
    succCount, failureCount = 0,0
    async with _create_s3_client() as client:
        with table_service_client:
            async with aiohttp.ClientSession() as session:
                if links:
                    cors = []
                    for link in links:
                        logging.info("Processing file {}".format(link))
                        try:
                            if check_if_script_runs_too_long(script_start_time):
                                logging.info('Script is running too long. Stop processing new files.')
                                connTable.ingest_table_data(link,bucket,"FAILURE")
                                continue
                            cor = process_file(bucket, link, client, semaphore, session)
                            cors.append(cor)
                            connTable.ingest_table_data(link,bucket,"SUCCESS")                        
                            succMessage += "Successfully completed blob {}.\n".format(link)
                            succCount = succCount + 1
                        except Exception as err:
                            connTable.ingest_table_data(link,bucket,"FAILURE")
                            errorMessage += "Could not process the blob {}.\n".format(link)
                            failureCount = failureCount + 1                    
                    if cors:
                        await asyncio.gather(*cors)
                else:
                    return func.HttpResponse("No links are present in the request body to process", status_code=404)
    if not failureCount:
        logging.info("Successfully completed {} blob.".format(succCount)) 
        return func.HttpResponse(succMessage, status_code=200)
    else:
        return func.HttpResponse(succMessage + errorMessage, status_code=404)

def check_if_script_runs_too_long(script_start_time):
    now = int(time.time())
    duration = now - script_start_time
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.85)
    return duration > max_duration

def customize_event(line,tableType,requiredFieldsMapping):
    #element = json.loads(line)
    required_fields = requiredFieldsMapping[tableType]
    required_fields_data = {}
    custom_fields_data = {}
    for key, value in line.items():
        if key in required_fields:
            required_fields_data[key] = value
        else:
            custom_fields_data[key] = value
    event = required_fields_data
    custom_fields_data_text = str(json.dumps(custom_fields_data))
    if custom_fields_data_text != "{}":
        event["custom_fields_message"] = custom_fields_data_text
    
    return event

async def process_file(bucket, s3_path, client, semaphore, session):
    async with semaphore:
        total_events_success = 0
        total_events_failure = 0
        logging.info("Start processing file {}".format(s3_path))
        sentinelHelper = SentinelTableHelper("EventsToTableMapping.json",session)
        try:
            response = await client.get_object(Bucket=bucket, Key=s3_path)
            s = ''
            async for decompressed_chunk in AsyncGZIPDecompressedStream(response["Body"]):
                s += decompressed_chunk.decode(errors='ignore')
                lines = re.split(r'{0}'.format(LINE_SEPARATOR), s)
                for n, line in enumerate(lines):
                    if n < len(lines) - 1:
                        if line:
                            try:
                                event = json.loads(line)
                            except ValueError as e:
                                logging.error('Error while loading json Event at s value {}. Error: {}'.format(line, str(e)))
                                raise e
                            await sentinelHelper.send_events(event)
                s = line
            if s:
                try:
                    event = json.loads(line)
                except ValueError as e:
                    logging.error('Error while loading json Event at s value {}. Error: {}'.format(line, str(e)))
                    raise e
                await sentinelHelper.send_events(event)
            await sentinelHelper.flush_all()
            total_events_success += sentinelHelper.get_success_events()
            total_events_failure += sentinelHelper.get_failure_events()
            logging.info("Finish processing file {} with {} events.".format(s3_path,total_events_success))
            if total_events_failure:
                logging.info("Failure : {} events failed".format(s3_path,total_events_failure))
        except Exception as e:
            logging.warn("Processing file {} was failed. Error: {}".format(s3_path,e))

class SentinelTableHelper:
    def __init__(self,fileName,session):
        self.__filename = fileName
        self.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.__session = session
        self.__tabletypes = ["Dns","File","Process","Network","Additional","Auth","Registry","Audit","Image","Inventory","Billing","AD","Agent","Etw","Firmware","Module"]
        self.__sentinelConnector = {}
        self.__eventToTable = {}
        self.__requiredFieldsMapping = {}
        with open(os.path.join(self.__location__, fileName)) as json_file:
            self.__eventToTable = json.load(json_file)    
        with open(os.path.join(self.__location__, "RequiredFieldsSchema.json")) as json_file:
            self.__requiredFieldsMapping = json.load(json_file)        
        for table in self.__tabletypes:
            tablename = "Crowdstrike" + table + "Events"
            self.__sentinelConnector[table] = AzureSentinelConnectorAsync(self.__session, LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, tablename, queue_size=MAX_BUCKET_SIZE)

    def get_mapping_dict(self):
        return self.__eventToTable
    
    async def send_events(self,event):
        try:
            event["timestamp_iso"] = datetime.datetime.fromtimestamp(int(event["timestamp"]) / 1000.0).strftime('%a, %d %b %Y %H:%M:%S GMT')
        except Exception as exc:
            event["TimeGenerated"] = event["timestamp"]

        eventToTable = self.get_mapping_dict()
        if "event_simpleName" in event and event['event_simpleName'] in eventToTable.keys():
            tableType = eventToTable[event['event_simpleName']]
        else:
            tableType = "Additional"

        if tableType == "Additional":
            event = customize_event(event,"Additional",self.__requiredFieldsMapping)
        
        if tableType in self.__sentinelConnector.keys():
            await self.__sentinelConnector[tableType].send(event)

    def get_success_events(self):
        successEvents = 0
        for key in self.__sentinelConnector:
            successEvents += self.__sentinelConnector[key].successfull_sent_events_number
        return successEvents

    def get_failure_events(self):
        failedEvents = 0
        for key in self.__sentinelConnector:
            failedEvents += self.__sentinelConnector[key].failed_sent_events_number
        return failedEvents

    async def flush_all(self):
        for key in self.__sentinelConnector:
            await self.__sentinelConnector[key].flush()

class AzureTableStorageConnector:
    def __init__(self, conn_string):
        self.__conn_string = conn_string
        self.script_start_time = int(time.time())

    def _create_table_service_client(self):
        return TableServiceClient.from_connection_string(self.__conn_string, logging_enable=False)

    def _get_table_client(self,table_name):
        create_table_service_client = self._create_table_service_client()
        return create_table_service_client.create_table_if_not_exists(table_name=table_name)
    
    def ingest_table_data(self,file_name,bucket,status):
        currentTime =  datetime.datetime.utcnow()
        my_status_record = {
            u'PartitionKey': file_name,
            u'RowKey': file_name + " - " + currentTime.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            u'StatusTime': datetime.datetime.utcnow(),
            u'Bucket' : bucket,
            u'Status': status
        }
        status_record = self._get_table_client("crowdstrikestatus").create_entity(entity=my_status_record)
        if status_record:
            logging.info("Status Table updated for {}".format(file_name))