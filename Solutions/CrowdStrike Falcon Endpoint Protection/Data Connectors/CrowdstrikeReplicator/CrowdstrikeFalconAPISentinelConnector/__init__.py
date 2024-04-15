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

WORKSPACE_ID = os.environ['WorkspaceID']
SHARED_KEY = os.environ['WorkspaceKey']
LOG_TYPE = "CrowdstrikeReplicatorLogs"
AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']
AWS_REGION_NAME = os.environ['AWS_REGION_NAME']
QUEUE_URL = os.environ['QUEUE_URL']
VISIBILITY_TIMEOUT = 1800
LINE_SEPARATOR = os.environ.get('lineSeparator',  '[\n\r\x0b\v\x0c\f\x1c\x1d\x85\x1e\u2028\u2029]+')
connection_string = os.environ['AzureWebJobsStorage']

# Defines how many files can be processed simultaneously
MAX_CONCURRENT_PROCESSING_FILES = int(os.environ.get('SimultaneouslyProcessingFiles', 20))

# Defines max number of events that can be sent in one request to Microsoft Sentinel
MAX_BUCKET_SIZE = int(os.environ.get('EventsBucketSize', 2000))

LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')
if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")

drop_files_array = []
failed_files_array = []

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

def customize_event(line):
    element = json.loads(line)
    required_fileds = [
                        "timestamp", "aip", "aid", "EventType", "LogonType", "HostProcessType", "UserPrincipal", "DomainName",
                        "RemoteAddressIP", "ConnectionDirection", "TargetFileName", "LocalAddressIP4", "IsOnRemovableDisk",
                        "UserPrincipal", "UserIsAdmin", "LogonTime", "LogonDomain", "RemoteAccount", "UserId", "Prevalence",
                        "CurrentProcess", "ConnectionDirection", "event_simpleName", "TargetProcessId", "ProcessStartTime",
                        "UserName", "DeviceProductId", "TargetSHA256HashData", "SHA256HashData", "MD5HashData", "TargetDirectoryName",
                        "TargetFileName", "FirewallRule", "TaskName", "TaskExecCommand", "TargetAddress", "TargetProcessId",
                        "SourceFileName", "RegObjectName", "RegValueName", "ServiceObjectName", "RegistryPath", "RawProcessId",
                        "event_platform", "CommandLine", "ParentProcessId", "ParentCommandLine", "ParentBaseFileName",
                        "GrandParentBaseFileName", "RemotePort", "VolumeDeviceType", "VolumeName", "ClientComputerName", "ProductId", "ComputerName"
                    ]
    required_fields_data = {}
    custom_fields_data = {}
    for key, value in element.items():
        if key in required_fileds:
            required_fields_data[key] = value
        else:
            custom_fields_data[key] = value
    event = required_fields_data
    custom_fields_data_text = str(json.dumps(custom_fields_data))
    if custom_fields_data_text != "{}":
        event["custom_fields_message"] = custom_fields_data_text
    return event

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
    global drop_files_array, failed_files_array
    drop_files_array.clear()
    failed_files_array.clear()
    script_start_time = int(time.time())
    filepath = 'drop_files_array_file'
    state = StateManager(connection_string=connection_string, share_name='funcstatemarkershare', file_path=filepath)
    last_dropped_messages = state.get()
    last_dropped_messages_obj = ''
    if last_dropped_messages != None and last_dropped_messages != '':
        last_dropped_messages_obj = json.loads(last_dropped_messages)
        state.post('')
        logging.info("Detected files which not processed or previously processed with errors. Files count: {}. These files will be added to the common array for re-processing".format(len(last_dropped_messages_obj)))
    logging.info("Creating SQS connection")
    async with _create_sqs_client() as client:
        async with aiohttp.ClientSession() as session:
            if len(last_dropped_messages_obj) > 0:
                logging.info("Processing files which added to re-processing. Files: {}".format(last_dropped_messages_obj))
                last_dropped_messages_obj_sorted = sort_files_by_bucket(last_dropped_messages_obj)
                for reprocessing_file_msg in last_dropped_messages_obj_sorted:
                    await download_message_files(reprocessing_file_msg, session, retrycount=1)
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
                        logging.info("Got message with MessageId {}. Start processing {} files from Bucket: {}. Path prefix: {}. Timestamp: {}.".format(msg["MessageId"], body_obj["fileCount"], body_obj["bucket"], body_obj["pathPrefix"], body_obj["timestamp"]))
                        await download_message_files(body_obj, session, retrycount=0)
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
    if len(drop_files_array) > 0:
        logging.info("list of files that were not processed: {}".format(drop_files_array))
        state.post(str(json.dumps(drop_files_array)))

    if len(failed_files_array) > 0:
        logging.info("list of files that were not processed after defined no. of retries: {}".format(failed_files_array))
        
async def process_file(bucket, s3_path, client, semaphore, session, retrycount):
    async with semaphore:
        total_events = 0
        logging.info("Start processing file {}".format(s3_path))
        sentinel = AzureSentinelConnectorAsync(
                                                session,
                                                LOG_ANALYTICS_URI,
                                                WORKSPACE_ID,
                                                SHARED_KEY,
                                                LOG_TYPE, 
                                                queue_size=MAX_BUCKET_SIZE
                                                )
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
                                event = customize_event(line)
                            except ValueError as e:
                                logging.error('Error while loading json Event at s value {}. Error: {}'.format(line, str(e)))
                                raise e
                            await sentinel.send(event)
                s = line
            if s:
                try:
                    event = customize_event(line)
                except ValueError as e:
                    logging.error('Error while loading json Event at s value {}. Error: {}'.format(line, str(e)))
                    raise e
                await sentinel.send(event)
            await sentinel.flush()
            total_events += sentinel.successfull_sent_events_number
            logging.info("Finish processing file {}. Sent events: {}".format(s3_path, sentinel.successfull_sent_events_number))
        except Exception as e:
            if(retrycount<=0):
                logging.warn("Processing file {} was failed. Error: {}".format(s3_path,e))
                drop_files_array.append({'bucket': bucket, 'path': s3_path})
            else:
                logging.warn("Processing file {} was failed after defined no. of retries. Error: {}".format(s3_path,e))
                failed_files_array.append({'bucket': bucket, 'path': s3_path})
                

async def download_message_files(msg, session, retrycount):
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PROCESSING_FILES)
    async with _create_s3_client() as client:
        cors = []
        for s3_file in msg['files']:
            cors.append(process_file(msg['bucket'], s3_file['path'], client, semaphore, session, retrycount))
        await asyncio.gather(*cors)
