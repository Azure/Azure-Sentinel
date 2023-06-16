import asyncio
import os
import sys
import asyncio
import json
from unittest.mock import sentinel
from botocore.config import Config as BotoCoreConfig
from aiobotocore.session import get_session
from gzip_stream import AsyncGZIPDecompressedStream
import re
from .sentinel_connector_clv2_async import AzureSentinelConnectorCLv2Async
import time
import aiohttp
import logging
import azure.functions as func
import itertools
from operator import itemgetter
import datetime
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
NORMALIZED_DCE_ENDPOINT = os.environ['DCE_ENDPOINT']
NORMALIZED_DCR_ID = os.environ['DCR_ID']
CUSTOMIZED_DCE_ENDPOINT = os.environ['DCE_ENDPOINT']
CUSTOMIZED_DCR_ID = os.environ['DCR_ID']
NORMALIZED_SCHEMA_NAMES = '{"Dns": "Custom-CrowdstrikeDns","File": "Custom-CrowdstrikeFile","Process": "Custom-CrowdstrikeProcess","Network": "Custom-CrowdstrikeNetwork","Auth": "Custom-CrowdstrikeAuth","Registry": "Custom-CrowdstrikeRegistry","Audit": "Custom-CrowdstrikeAudit","User": "Custom-CrowdstrikeUser","Web": "Custom-CrowdstrikeWeb","Additional": "Custom-CrowdstrikeAdditional"}'
CUSTOM_SCHEMA_NAMES = '{"Dns": "Custom-CrowdstrikeDns","File": "Custom-CrowdstrikeFile","Process": "Custom-CrowdstrikeProcess","Network": "Custom-CrowdstrikeNetwork","Auth": "Custom-CrowdstrikeAuth","Registry": "Custom-CrowdstrikeRegistry","Audit": "Custom-CrowdstrikeAudit","User": "Custom-CrowdstrikeUser","Web": "Custom-CrowdstrikeWeb"}'
REQUIRE_RAW = False

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
                            "https://raw.githubusercontent.com/Azure/Azure-Sentinel/users/demehra/crowdstrike/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdstrikeReplicator/HttpTriggerCrowdstrike/EventsToTableMapping.json",
                            "EventsToTableMapping.json"
                         )
    eventsSchemaMapping.setDict()
    eventsSchemaMappingDict = eventsSchemaMapping.getDict()
    logging.info(len(eventsSchemaMappingDict))

    requiredFieldsMapping = FileHelper(
                            "https://raw.githubusercontent.com/Azure/Azure-Sentinel/users/demehra/crowdstrike/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdstrikeReplicator/HttpTriggerCrowdstrike/RequiredFieldsSchema.json",
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
                    await process_file_CLv2(bucket, link, client, session, eventsSchemaMappingDict, requiredFieldsMappingDict)
                except Exception as e:
                    logging.error('Error while processing bucket. Error: {}'.format(link, str(e)))
                    raise e
    logging.info("Successfully executed {} Bucket.".format(link)) 

def customize_event(line, eventsSchemaMappingDict, requiredFieldsMappingDict, requireRaw):
    
    element = json.loads(line)
    common_fields_status = requiredFieldsMappingDict["Common"]
    if "event_simpleName" in element and element["event_simpleName"] in eventsSchemaMappingDict:
        schema = eventsSchemaMappingDict[element["event_simpleName"]]
    else:
        schema = "Additional"
    schema_fields_status = requiredFieldsMappingDict[schema]
    fields_data = {}
    common_fields_additional_data = {}
    schema_fields_additional_data = {}
    customizedEvent = {}

    for key in common_fields_status.keys():
        if key in element:
            if requireRaw:
                customizedEvent[key] = element[key]
            if common_fields_status[key] == "Required":
                fields_data[key] = element[key]
            else:
                common_fields_additional_data[key] = element[key]
            element.pop(key)

    elementCopy = element.copy()
    for key in elementCopy.keys():
        if key in schema_fields_status:
            if requireRaw:
                customizedEvent[key] = element[key]
            if schema_fields_status[key] == "Required":
                fields_data[key] = element[key]
            else:
                schema_fields_additional_data[key] = element[key]
            element.pop(key)

    normalizedEvent = fields_data
    common_fields_additional_data_text = str(json.dumps(common_fields_additional_data))
    if common_fields_additional_data_text != "{}":
        normalizedEvent["CommonAdditionalFields"] = common_fields_additional_data_text

    schema_fields_additional_data_text = str(json.dumps(schema_fields_additional_data))
    if schema_fields_additional_data_text != "{}":
        normalizedEvent["SchemaAdditionalFields"] = schema_fields_additional_data_text
        
    unknown_additional_data_text = str(json.dumps(element))
    if unknown_additional_data_text != "{}":
        normalizedEvent["AdditionalFields"] = unknown_additional_data_text
        if requireRaw:
            customizedEvent["AdditionalFields"] = unknown_additional_data_text

    return normalizedEvent, customizedEvent

async def process_file_CLv2(bucket, s3_path, client, session, eventsSchemaMappingDict, requiredFieldsMappingDict):
        logging.info("Start processing bucket {}".format(s3_path))
        normalizedSentinelHelperCollection = SentinelHelperCollection(session, 
                                                                      eventsSchemaMappingDict,
                                                                      NORMALIZED_DCE_ENDPOINT,
                                                                      NORMALIZED_DCR_ID,
                                                                      NORMALIZED_SCHEMA_NAMES
                                                                    )
        
        customizedSentinelHelperCollection = SentinelHelperCollection(session, 
                                                                      eventsSchemaMappingDict,
                                                                      CUSTOMIZED_DCE_ENDPOINT,
                                                                      CUSTOMIZED_DCR_ID,
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


class FileHelper:
    def __init__(self,filePath, fileName):
        self.__filePath = filePath
        self.__fileName = fileName
        self.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.__eventToDict = {}

    def setDict(self):
        #try:
            #response = requests.get(self.__filePath)
        #    logging.info("Status Code is {}".format(response.status_code))
        #    self.__eventToDict = json.loads(response.text)
        #except Exception as e:
        #    logging.warn("Error in fetching file from {}. {}".format(self.__filePath,e))
        #    if True:
            #if not (200 <= response.status_code <= 299):
                #logging.warn("Could not fetch the file path at {}. Retrieving the local copy {}".format(self.__filePath,self.__fileName))
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
