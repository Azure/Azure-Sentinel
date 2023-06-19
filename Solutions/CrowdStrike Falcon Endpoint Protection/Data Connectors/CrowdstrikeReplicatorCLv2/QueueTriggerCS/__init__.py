import os
import json
from botocore.config import Config as BotoCoreConfig
from aiobotocore.session import get_session
from gzip_stream import AsyncGZIPDecompressedStream
import re
from .sentinel_connector_clv2_async import AzureSentinelConnectorCLv2Async
import time
import aiohttp
import logging
import azure.functions as func
import requests

AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']
AWS_REGION_NAME = os.environ['AWS_REGION_NAME']
QUEUE_URL = os.environ['QUEUE_URL']
VISIBILITY_TIMEOUT = 1800
LINE_SEPARATOR = os.environ.get('lineSeparator',  '[\n\r\x0b\v\x0c\f\x1c\x1d\x85\x1e\u2028\u2029]+')
connection_string = os.environ['AzureWebJobsStorage']
AZURE_STORAGE_CONNECTION_STRING = os.environ['AzureWebJobsStorage']
AZURE_TENANT = os.environ['AZURE_TENANT']
AZURE_CLIENT_ID = os.environ['AZURE_CLIENT_ID']
AZURE_CLIENT_SECRET = os.environ['AZURE_CLIENT_SECRET']
NORMALIZED_DCE_ENDPOINT = os.environ['NORMALIZATION_DCE_ENDPOINT']
NORMALIZED_DCR_ID = os.environ['NORMALIZATION_DCR_ID']
RAW_DATA_DCE_ENDPOINT = os.environ['RAW_DATA_DCE_ENDPOINT']
RAW_DATA_DCR_ID = os.environ['RAW_DATA_DCR_ID']
NORMALIZED_SCHEMA_NAMES = '{"Dns": "Custom-CrowdstrikeDns","File": "Custom-CrowdstrikeFile","Process": "Custom-CrowdstrikeProcess","Network": "Custom-CrowdstrikeNetwork","Auth": "Custom-CrowdstrikeAuth","Registry": "Custom-CrowdstrikeRegistry","Audit": "Custom-CrowdstrikeAudit","User": "Custom-CrowdstrikeUser","Additional": "Custom-CrowdstrikeAdditional"}'
CUSTOM_SCHEMA_NAMES = '{"Dns": "Custom-CrowdstrikeDns","File": "Custom-CrowdstrikeFile","Process": "Custom-CrowdstrikeProcess","Network": "Custom-CrowdstrikeNetwork","Auth": "Custom-CrowdstrikeAuth","Registry": "Custom-CrowdstrikeRegistry","Audit": "Custom-CrowdstrikeAudit","User": "Custom-CrowdstrikeUser"}'
REQUIRE_RAW_STRING = os.environ["REQUIRE_RAW"]
SECONDARY_DATA_SCHEMA = "Custom-CrowdStrikeSecondary"
EVENT_TO_TABLE_MAPPING_LINK = os.environ['EVENT_TO_TABLE_MAPPING_LINK']
REQUIRED_FIELDS_SCHEMA_LINK = os.environ['REQUIRED_FIELDS_SCHEMA_LINK']

if REQUIRE_RAW_STRING.lower() == "true":
    REQUIRE_RAW = True
else:
    REQUIRE_RAW = False

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

async def main(msg: func.QueueMessage) -> None:
    logging.info('Starting script')
    script_start_time = int(time.time())
    
    try:
        req_body = json.loads(msg.get_body().decode('ascii').replace("'",'"'))
    except ValueError:
        pass
    else:
        link = req_body.get('link')
        bucket = req_body.get('bucket')
        messageId = req_body.get('messageId')

    logging.info("Processing {} file from {} bucket of {} messageId".format(link,bucket,messageId))
    
    eventsSchemaMapping = FileHelper(
                            EVENT_TO_TABLE_MAPPING_LINK,
                            "EventsToTableMapping.json"
                         )
    eventsSchemaMapping.setDict()
    eventsSchemaMappingDict = eventsSchemaMapping.getDict()
    logging.info(len(eventsSchemaMappingDict))

    requiredFieldsMapping = FileHelper(
                            REQUIRED_FIELDS_SCHEMA_LINK,
                            "RequiredFieldsSchema.json"
                         )
    requiredFieldsMapping.setDict()
    requiredFieldsMappingDict = requiredFieldsMapping.getDict()
    logging.info(len(requiredFieldsMappingDict))
    
    async with _create_s3_client() as client:
        async with aiohttp.ClientSession() as session:
            if link:
                logging.info("Processing file {}".format(link))
                try:
                    if link.startswith("fdrv2"):
                        logging.info('Processing a secondary data bucket.')
                        await process_file_secondary_CLv2(bucket, link, client, session)
                    else:
                        await process_file_primary_CLv2(bucket, link, client, session, eventsSchemaMappingDict, requiredFieldsMappingDict)
                    logging.info("Successfully executed {} Bucket.".format(link)) 
                except Exception as e:
                    logging.error('Error while processing bucket. Error: {}'.format(link, str(e)))
                    raise e

def customize_event(line, eventsSchemaMappingDict, requiredFieldsMappingDict, requireRaw):
    
    element = json.loads(line)
    if "event_simpleName" in element and element["event_simpleName"] in eventsSchemaMappingDict:
        schema = eventsSchemaMappingDict[element["event_simpleName"]]
    else:
        schema = "Additional"
    schema_fields_status = requiredFieldsMappingDict[schema]

    normalized_fields = {}
    normalized_additional_fields = {}
    raw_data_fields = {}
    raw_data_additional_fields = {}

    for key in element.keys():

        # Check if the schema field is already present or not
        if key in schema_fields_status:

            # If raw data is required and field is already known,
            # Add the same in raw data fields
            if requireRaw:
                raw_data_fields[key] = element[key]

            # This is only for normalization
            # If schema field is Requried for normalization
            # Add to normalization
            # Otherwise add to additional fields specific to normalized fields (Optional class in mapping)
            if schema_fields_status[key] == "Required":
                normalized_fields[key] = element[key]
            else:
                normalized_additional_fields[key] = element[key]

        # If field is new and never seen before
        # If Raw data is required, add this field to raw data specific to raw data
        # Otherwise only add to additional fields specific to normalized data
        else:
            if requireRaw:
                raw_data_additional_fields[key] = element[key]
            normalized_additional_fields[key] = element[key]

    normalized_additional_fields_text = str(json.dumps(normalized_additional_fields))
    if normalized_additional_fields_text != "{}":
        normalized_fields["AdditionalFields"] = normalized_additional_fields_text

    raw_data_additional_fields_text = str(json.dumps(raw_data_additional_fields))
    if raw_data_additional_fields_text != "{}":
        raw_data_fields["AdditionalFields"] = raw_data_additional_fields_text

    return normalized_fields, raw_data_fields

async def process_file_primary_CLv2(bucket, s3_path, client, session, eventsSchemaMappingDict, requiredFieldsMappingDict):
        logging.info("Start processing bucket {}".format(s3_path))
        normalizedSentinelHelperCollection = SentinelHelperCollection(session, 
                                                                      eventsSchemaMappingDict,
                                                                      NORMALIZED_DCE_ENDPOINT,
                                                                      NORMALIZED_DCR_ID,
                                                                      NORMALIZED_SCHEMA_NAMES
                                                                    )
        
        customizedSentinelHelperCollection = SentinelHelperCollection(session, 
                                                                      eventsSchemaMappingDict,
                                                                      RAW_DATA_DCE_ENDPOINT,
                                                                      RAW_DATA_DCR_ID,
                                                                      CUSTOM_SCHEMA_NAMES
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
                                normalizedEvent, customizedEvent = customize_event(line, eventsSchemaMappingDict, requiredFieldsMappingDict, REQUIRE_RAW)
                            except ValueError as e:
                                logging.error('Error while loading json Event at s value {}. Error: {}'.format(line, str(e)))
                                raise e
                            except Exception as e:
                                logging.error(e)
                            await normalizedSentinelHelperCollection.sendData(normalizedEvent)
                            if REQUIRE_RAW:
                                await customizedSentinelHelperCollection.sendData(customizedEvent)
                s = line
            if s:
                try:
                    normalizedEvent, customizedEvent = customize_event(line, eventsSchemaMappingDict, requiredFieldsMappingDict, REQUIRE_RAW)
                except ValueError as e:
                    logging.error('Error while loading json Event at s value {}. Error: {}'.format(line, str(e)))
                    raise e
                await normalizedSentinelHelperCollection.sendData(normalizedEvent)
                if REQUIRE_RAW:
                    await customizedSentinelHelperCollection.sendData(customizedEvent)
            await normalizedSentinelHelperCollection.flushData()
            if REQUIRE_RAW:
                await customizedSentinelHelperCollection.flushData()

            normalized_total_events_success = normalizedSentinelHelperCollection.getSuccessCountCombined()
            normalized_total_events_failure = normalizedSentinelHelperCollection.getFailureCountCombined()

            if REQUIRE_RAW:
                custom_total_events_success = customizedSentinelHelperCollection.getSuccessCountCombined()
                custom_total_events_failure = customizedSentinelHelperCollection.getFailureCountCombined()
            else:
                custom_total_events_success, custom_total_events_failure = 0,0

            logging.info("Finish processing file {} with {} normalized events and {} custom events.".format(s3_path,normalized_total_events_success,custom_total_events_success))
            if normalized_total_events_failure or custom_total_events_failure:
                logging.info("Failure : {} normalized events failed and {} custom events failed.".format(s3_path,normalized_total_events_failure, custom_total_events_failure))

        except Exception as e:
            logging.warn("Processing file {} was failed. Error: {}".format(s3_path,e))

async def process_file_secondary_CLv2(bucket, s3_path, client, session):
        logging.info("Start processing bucket {}".format(s3_path))
        AzureSentinelConnector = AzureSentinelConnectorCLv2Async(session, NORMALIZED_DCE_ENDPOINT, NORMALIZED_DCR_ID, SECONDARY_DATA_SCHEMA,
                                                         AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT)

        folderName = s3_path.split('/')[-2]

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
                                 secondaryData = {}
                                 secondaryData["FolderName"] = folderName
                                 secondaryData["AdditionalFields"] = line
                            except ValueError as e:
                                logging.error('Error while loading json Event at s value {}. Error: {}'.format(line, str(e)))
                                raise e
                            except Exception as e:
                                logging.error(e)
                            await AzureSentinelConnector.send(secondaryData)
                s = line
            if s:
                try:
                    secondaryData = {}
                    secondaryData["FolderName"] = folderName
                    secondaryData["AdditionalFields"] = line
                except ValueError as e:
                    logging.error('Error while loading json Event at s value {}. Error: {}'.format(line, str(e)))
                    raise e
                await AzureSentinelConnector.send(secondaryData)

            total_events_success = AzureSentinelConnector.get_success_count()
            total_events_failure = AzureSentinelConnector.get_failure_count()
            
            logging.info("Finish processing file {} with {} secondary events.".format(s3_path,total_events_success))
            if total_events_failure:
                logging.info("Failure : {} secondary events failed".format(s3_path,total_events_failure))

        except Exception as e:
            logging.warn("Processing file {} was failed. Error: {}".format(s3_path,e))


class FileHelper:
    def __init__(self,filePath, fileName):
        self.__filePath = filePath
        self.__fileName = fileName
        self.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.__eventToDict = {}

    def setDict(self):
        try:
            response = requests.get(self.__filePath)
            self.__eventToDict = json.loads(response.text)
        except Exception as e:
            logging.warn("Error in fetching file from {}. {}".format(self.__filePath,e))
            if not (200 <= response.status_code <= 299):
                logging.warn("Could not fetch the file path at {}. Retrieving the local copy {}".format(self.__filePath,self.__fileName))
                with open(os.path.join(self.__location__, self.__fileName)) as json_file:
                    self.__eventToDict = json.load(json_file)

    def getDict(self):
        return self.__eventToDict

class SentinelHelperCollection:
    def __init__(self,
                 session, 
                 eventsSchemaMappingDict,
                 DCE_ENDPOINT,
                 DCR_ID,
                 STREAM_MAPPING
               ):
        self.__eventsSchemaMappingDict = eventsSchemaMappingDict
        self.__sentinelHelperList = {}

        schemaMapping = json.loads(STREAM_MAPPING)
        for schema in schemaMapping.keys():
            streamName = schemaMapping[schema]
            sentinelObject = AzureSentinelConnectorCLv2Async(session, DCE_ENDPOINT, DCR_ID, streamName,
                                                         AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT)
            self.__sentinelHelperList[schema] = sentinelObject

    async def sendData(self,event):
        if "event_simpleName" in event and event["event_simpleName"] in self.__eventsSchemaMappingDict:
            schema = self.__eventsSchemaMappingDict[event["event_simpleName"]]
        else:
            schema = "Additional"
        if schema in self.__sentinelHelperList.keys():
            await self.__sentinelHelperList[schema].send(event)

    async def flushData(self):
        for schema in self.__sentinelHelperList:
            await self.__sentinelHelperList[schema].flush()

    def getSuccessCountCombined(self):
        totalCount = 0
        for schema in self.__sentinelHelperList:
            totalCount = totalCount + self.__sentinelHelperList[schema].get_success_count()
        return totalCount

    def getFailureCountCombined(self):
        totalCount = 0
        for schema in self.__sentinelHelperList:
            totalCount = totalCount + self.__sentinelHelperList[schema].get_failure_count()
        return totalCount
