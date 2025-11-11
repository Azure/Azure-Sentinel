import requests
import datetime
import dateutil
import logging
import boto3
import gzip
import io
import csv
import time
import os
import sys
import json
import hashlib
import hmac
import base64
import re
from threading import Thread
from io import StringIO

import azure.functions as func


sentinel_customer_id = os.environ.get('WorkspaceID')
sentinel_shared_key = os.environ.get('WorkspaceKey')
aws_access_key_id = os.environ.get('AWSAccessKeyId')
aws_secret_acces_key = os.environ.get('AWSSecretAccessKey')
aws_s3_bucket = os.environ.get('S3Bucket')
aws_region_name = os.environ.get('AWSRegionName')
cloud_trail_folder = os.environ.get('CloudTrailFolderName')
sentinel_log_type = os.environ.get('LogAnalyticsCustomLogName')
fresh_event_timestamp = os.environ.get('FreshEventTimeStamp')

logAnalyticsUri = os.environ.get('LAURI')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + sentinel_customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("AWSCloudTrailAzFunc: Invalid Log Analytics Uri.")

# Boolean Values
isCoreFieldsAllTable = os.environ.get('CoreFieldsAllTable')
isSplitAWSResourceTypes = os.environ.get('SplitAWSResourceTypes')

# TODO: Read Collection schedule from environment variable as CRON expression; This is also Azure Function Trigger Schedule
collection_schedule = int(fresh_event_timestamp)


def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Starting program')
    
    cli = S3Client(aws_access_key_id, aws_secret_acces_key, aws_region_name, aws_s3_bucket)
    ts_from, ts_to = cli.get_time_interval()
    print("From:{0}".format(ts_from))
    print("To:{0}".format(ts_to))

    logging.info('Searching files last modified from {} to {}'.format(ts_from, ts_to))
    obj_list = cli.get_files_list(ts_from, ts_to)

    logging.info('Total number of files is {}. Total size is {} MB'.format(
        len(obj_list),
        round(sum([x['Size'] for x in obj_list]) / 10**6, 2)
    ))

    failed_sent_events_number = 0
    successfull_sent_events_number = 0
    eventobjectlist = {'eventTime', 'eventVersion', 'userIdentity', 'eventSource', 'eventName', 'awsRegion', 'sourceIPAddress', 'userAgent', 'errorCode', 'errorMessage', 'requestID', 'eventID', 'eventType', 'apiVersion', 'managementEvent', 'readOnly', 'resources', 'recipientAccountId', 'serviceEventDetails', 'sharedEventID', 'vpcEndpointId', 'eventCategory', 'additionalEventData'}
    groupEvents = {}
    coreEvents = []
    eventSources = []

    for obj in obj_list:
        log_events = cli.process_obj(obj)       
        
        for log in log_events:
            logDetails={}
            logDetails1={}
            logEventSource = log['eventSource'].split('.')[0].replace('-', '')
            if (logEventSource == 'ec2'):
                for col in eventobjectlist:
                    if col in log:
                        logDetails1[col]=log[col]
                
                ec2Header = logEventSource + '_Header'
                if ec2Header not in groupEvents:
                    groupEvents[ec2Header]=[]
                    eventSources.append(ec2Header)
                    groupEvents[ec2Header].append(logDetails1)
                else:
                    groupEvents[ec2Header].append(logDetails1)

                ec2Request = logEventSource + '_Request'
                
                if ec2Request not in groupEvents:
                    groupEvents[ec2Request]=[]
                    eventSources.append(ec2Request)

                    ec2Events = {}
                    ec2Events['eventID']=log['eventID']
                    ec2Events['awsRegion']=log['awsRegion']
                    ec2Events['requestID']=log['requestID']
                    ec2Events['eventTime']=log['eventTime']
                    ec2Events['requestParameters']=log['requestParameters']

                    groupEvents[ec2Request].append(ec2Events)
                else:
                    ec2Events = {}
                    ec2Events['eventID']=log['eventID']
                    ec2Events['awsRegion']=log['awsRegion']
                    ec2Events['requestID']=log['requestID']
                    ec2Events['eventTime']=log['eventTime']
                    ec2Events['requestParameters']=log['requestParameters']

                    groupEvents[ec2Request].append(ec2Events)

                ec2Response=logEventSource + '_Response'
                if ec2Response not in groupEvents:
                    groupEvents[ec2Response]=[]
                    eventSources.append(ec2Response)

                    ec2Events = {}
                    ec2Events['eventID']=log['eventID']
                    ec2Events['awsRegion']=log['awsRegion']
                    ec2Events['requestID']=log['requestID']
                    ec2Events['eventTime']=log['eventTime']
                    ec2Events['responseElements']=log['responseElements']

                    groupEvents[ec2Response].append(ec2Events)
                else:
                    ec2Events = {}
                    ec2Events['eventID']=log['eventID']
                    ec2Events['awsRegion']=log['awsRegion']
                    ec2Events['requestID']=log['requestID']
                    ec2Events['eventTime']=log['eventTime']
                    ec2Events['responseElements']=log['responseElements']

                    groupEvents[ec2Response].append(ec2Events)
            else:
                if logEventSource not in groupEvents:
                    groupEvents[logEventSource]=[]
                    eventSources.append(logEventSource)                    
                    groupEvents[logEventSource].append(log)
                else: 
                    groupEvents[logEventSource].append(log)

            for col in eventobjectlist:
                if col in log:
                    logDetails[col]=log[col]      
            
            coreEvents.append(logDetails)

    if (isCoreFieldsAllTable == "true" and isSplitAWSResourceTypes == "true"):
        file_events = 0
        t0 = time.time()    
        for event in coreEvents:
            sentinel = AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_ALL' , queue_size=10000, bulks_number=10)
            with sentinel:
                sentinel.send(event)
            file_events += 1 
            failed_sent_events_number += sentinel.failed_sent_events_number
            successfull_sent_events_number += sentinel.successfull_sent_events_number                
        
        for resource_type in eventSources:
            resource_type_events_collection = groupEvents[resource_type]
            for resource_type_event in resource_type_events_collection:
                sentinel = AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_' + resource_type, queue_size=10000, bulks_number=10)
                with sentinel:
                    sentinel.send(resource_type_event)       
        
    elif (isCoreFieldsAllTable == "true" and isSplitAWSResourceTypes == "false"):
        file_events = 0
        t0 = time.time()
        for event in coreEvents:
            sentinel = AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_ALL', queue_size=10000, bulks_number=10)
            with sentinel:
                sentinel.send(event)
            file_events += 1
            failed_sent_events_number += sentinel.failed_sent_events_number
            successfull_sent_events_number += sentinel.successfull_sent_events_number
            
    elif (isCoreFieldsAllTable == "false" and isSplitAWSResourceTypes == "true"):
        file_events = 0
        t0 = time.time()
        for resource_type in eventSources:
            resource_type_events_collection = groupEvents[resource_type]
            for resource_type_event in resource_type_events_collection:
                sentinel = AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_' + resource_type, queue_size=10000, bulks_number=10)
                with sentinel:
                    sentinel.send(resource_type_event)
                file_events += 1
                failed_sent_events_number += sentinel.failed_sent_events_number
                successfull_sent_events_number += sentinel.successfull_sent_events_number                      
        
    if failed_sent_events_number:
        logging.info('{} events have not been sent'.format(failed_sent_events_number))

    if successfull_sent_events_number:
        logging.info('Program finished. {} events have been sent.'.format(successfull_sent_events_number))

    if successfull_sent_events_number == 0 and failed_sent_events_number == 0:
        logging.info('No Fresh CloudTrail Events')


class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_acces_key, aws_region_name, aws_s3_bucket):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_acces_key = aws_secret_acces_key
        self.aws_region_name = aws_region_name
        self.aws_s3_bucket = self._get_s3_bucket_name(aws_s3_bucket)
        self.aws_s3_prefix = self._get_s3_prefix(aws_s3_bucket)        
        self.total_events = 0
        self.input_date_format = '%Y-%m-%d %H:%M:%S'
        self.output_date_format = '%Y-%m-%dT%H:%M:%SZ'

        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_acces_key,
            region_name=self.aws_region_name
        )       
       
    def _get_aws_account_id(self):
        self.sts = boto3.client(
            "sts", 
            aws_access_key_id=self.aws_access_key_id, 
            aws_secret_access_key=self.aws_secret_acces_key,
            region_name=self.aws_region_name
        )    
        return self.sts.get_caller_identity()["Account"]

    def _get_s3_bucket_name(self, aws_s3_bucket):
        aws_s3_bucket = self._normalize_aws_s3_bucket_string(aws_s3_bucket)
        tokens = aws_s3_bucket.split('/')
        aws_s3_bucket = tokens[0]
        return aws_s3_bucket

    def _get_s3_prefix(self, aws_s3_bucket):
        aws_s3_bucket = self._normalize_aws_s3_bucket_string(aws_s3_bucket)
        tokens = aws_s3_bucket.split('/')
        if len(tokens) > 1:
            prefix = '/'.join(tokens[1:]) + '/'
        else:
            prefix = ''
        return prefix

    def _normalize_aws_s3_bucket_string(self, aws_s3_bucket):
        aws_s3_bucket = aws_s3_bucket.strip()
        aws_s3_bucket = aws_s3_bucket.replace('s3://', '')
        if aws_s3_bucket.startswith('/'):
            aws_s3_bucket = aws_s3_bucket[1:]
        if aws_s3_bucket.endswith('/'):
            aws_s3_bucket = aws_s3_bucket[:-1]
        return aws_s3_bucket

    def get_time_interval(self):
        ts_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=collection_schedule + 1)
        ts_to = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        ts_from = ts_from.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0)
        ts_to = ts_to.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0)
        return ts_from, ts_to                   
    
    def _make_objects_list_request(self, marker='', prefix=''):
        response = self.s3.list_objects(
            Bucket=self.aws_s3_bucket, 
            Marker=marker,
            Prefix=prefix
        )
        try:
            response_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode', None)
            if response_code == 200:
                return response
            else:
                raise Exception('HTTP Response Code - {}'.format(response_code))
        except Exception as err:
            logging.error('Error while getting objects list - {}'.format(err))
            raise Exception

    def get_files_list(self, ts_from, ts_to):
        files = []
        folders = self.s3.list_objects(Bucket=self.aws_s3_bucket, Prefix=self.aws_s3_prefix, Delimiter='/')        
       

        marker_end = (ts_from - datetime.timedelta(minutes=60)).strftime("/%Y-%m-%d/%Y-%m-%d-%H-%M")
        
        for o in folders.get('CommonPrefixes'):        
            marker = o.get('Prefix') + cloud_trail_folder + marker_end   
            folder = o.get('Prefix') + cloud_trail_folder           
            while True:                
                response = self._make_objects_list_request(marker=marker, prefix=folder)
                for file_obj in response.get('Contents', []):
                    if ts_to > file_obj['LastModified'] >= ts_from:
                        files.append(file_obj)

                if response['IsTruncated'] is True:
                    marker = response['Contents'][-1]['Key']
                else:
                    break

        return self.sort_files_by_date(files)

    def download_obj(self, key):
        logging.info('Started downloading {}'.format(key))
        res = self.s3.get_object(Bucket=self.aws_s3_bucket, Key=key)
        try:
            response_code = res.get('ResponseMetadata', {}).get('HTTPStatusCode', None)
            if response_code == 200:
                body = res['Body']
                data = body.read()
                logging.info('File {} downloaded'.format(key))
                return data
            else:
                logging.error('Error while getting object {}. HTTP Response Code - {}'.format(key, response_code))
        except Exception as err:
            logging.error('Error while getting object {} - {}'.format(key, err))

    def unpack_file(self, downloaded_obj, key):
        try:
            file_obj = io.BytesIO(downloaded_obj)
            if '.csv.gz' in key.lower():
                extracted_file = gzip.GzipFile(fileobj=file_obj).read().decode()
            elif '.json.gz' in key.lower():
                extracted_file = gzip.GzipFile(fileobj=file_obj)
            elif '.json' in key.lower():
                extracted_file = file_obj
            return extracted_file

        except Exception as err:
            logging.error('Error while unpacking file {} - {}'.format(key, err))

  
    @staticmethod
    def format_date(date_string, input_format, output_format):
        try:
            date = datetime.datetime.strptime(date_string, input_format)
            date_string = date.strftime(output_format)
        except Exception:
            pass
        return date_string    

    @staticmethod
    def sort_files_by_date(ls):
        return sorted(ls, key=lambda k: k['LastModified'])

    def process_obj(self, obj):        
        key = obj['Key']        
        if '.json.gz' in key.lower():
            downloaded_obj = self.download_obj(key)
            json_file = self.unpack_file(downloaded_obj, key)
            logEvents = json.load(json_file)['Records']
            sortedLogEvents = sorted(logEvents, key=lambda r: r['eventTime'])
            return sortedLogEvents


class AzureSentinelConnector:
    def __init__(self, log_analytics_uri, customer_id, shared_key, log_type, queue_size=200, bulks_number=10, queue_size_bytes=25 * (2**20)):
        self.log_analytics_uri = log_analytics_uri
        self.customer_id = customer_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.queue_size = queue_size
        self.bulks_number = bulks_number
        self.queue_size_bytes = queue_size_bytes
        self._queue = []
        self._bulks_list = []
        self.successfull_sent_events_number = 0
        self.failed_sent_events_number = 0

    def send(self, event):
        self._queue.append(event)
        if len(self._queue) >= self.queue_size:
            self.flush(force=False)

    def flush(self, force=True):
        self._bulks_list.append(self._queue)
        if force:
            self._flush_bulks()
        else:
            if len(self._bulks_list) >= self.bulks_number:
                self._flush_bulks()

        self._queue = []

    def _flush_bulks(self):
        jobs = []
        for queue in self._bulks_list:
            if queue:
                queue_list = self._split_big_request(queue)
                for q in queue_list:
                    jobs.append(Thread(target=self._post_data, args=(self.customer_id, self.shared_key, q, self.log_type, )))

        for job in jobs:
            job.start()

        for job in jobs:
            job.join()

        self._bulks_list = []

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self.flush()

    def _build_signature(self, customer_id, shared_key, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def _post_data(self, customer_id, shared_key, body, log_type):
        events_number = len(body)
        body = json.dumps(body)
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self._build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
        uri = self.log_analytics_uri + resource + '?api-version=2016-04-01'
        
        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': log_type,
            'x-ms-date': rfc1123date
        }

        response = requests.post(uri, data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            logging.info('{} events have been successfully sent to Azure Sentinel'.format(events_number))
            self.successfull_sent_events_number += events_number
        else:
            logging.error("Error during sending events to Azure Sentinel. Response code: {}".format(response.status_code))
            self.failed_sent_events_number += events_number

    def _check_size(self, queue):
        data_bytes_len = len(json.dumps(queue).encode())
        return data_bytes_len < self.queue_size_bytes

    def _split_big_request(self, queue):
        if self._check_size(queue):
            return [queue]
        else:
            middle = int(len(queue) / 2)
            queues_list = [queue[:middle], queue[middle:]]
            return self._split_big_request(queues_list[0]) + self._split_big_request(queues_list[1])
