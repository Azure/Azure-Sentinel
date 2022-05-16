from distutils import core
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

# AWS INFORMATION
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION_NAME = os.environ["AWS_REGION_NAME"]
AWS_MACIE_S3_BUCKET = os.environ["AWS_MACIE_S3_BUCKET"]
AWS_INSPECTOR_S3_BUCKET = os.environ["AWS_INSPECTOR_S3_BUCKET"]
# MICROSOFT SENTINEL  (LOG ANALYTICS SPACE) INFORMATION
CUSTOMER_ID = os.environ["CUSTOMER_ID"]
SHARED_KEY = os.environ["SHARED_KEY"]

class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region_name, AWS_MACIE_S3_BUCKET):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region_name = aws_region_name
        self.AWS_MACIE_S3_BUCKET = self.get_s3_bucket_name(AWS_MACIE_S3_BUCKET)
        self.aws_s3_prefix = self.get_s3_prefix(AWS_MACIE_S3_BUCKET)        
        self.total_events = 0
        self.input_date_format = '%Y-%m-%d %H:%M:%S'
        self.output_date_format = '%Y-%m-%dT%H:%M:%SZ'

        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region_name
        )
        self.get_time_interval()       
       
    def get_aws_account_id(self):
        self.sts = boto3.client(
            "sts", 
            aws_access_key_id=self.aws_access_key_id, 
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region_name
        )
        print(self.sts)    
        return self.sts.get_caller_identity()["Account"]

    def get_s3_bucket_name(self, AWS_MACIE_S3_BUCKET):
        AWS_MACIE_S3_BUCKET = self.normalize_AWS_MACIE_S3_BUCKET_string(AWS_MACIE_S3_BUCKET)
        tokens = AWS_MACIE_S3_BUCKET.split('/')
        AWS_MACIE_S3_BUCKET = tokens[0]
        return AWS_MACIE_S3_BUCKET
    
    def normalize_AWS_MACIE_S3_BUCKET_string(self, AWS_MACIE_S3_BUCKET):
        AWS_MACIE_S3_BUCKET = AWS_MACIE_S3_BUCKET.strip()
        AWS_MACIE_S3_BUCKET = AWS_MACIE_S3_BUCKET.replace('s3://', '')
        if AWS_MACIE_S3_BUCKET.startswith('/'):
            AWS_MACIE_S3_BUCKET = AWS_MACIE_S3_BUCKET[1:]
        if AWS_MACIE_S3_BUCKET.endswith('/'):
            AWS_MACIE_S3_BUCKET = AWS_MACIE_S3_BUCKET[:-1]
        return AWS_MACIE_S3_BUCKET

    def get_s3_prefix(self, AWS_MACIE_S3_BUCKET):
        AWS_MACIE_S3_BUCKET = self.normalize_AWS_MACIE_S3_BUCKET_string(AWS_MACIE_S3_BUCKET)
        tokens = AWS_MACIE_S3_BUCKET.split('/')
        if len(tokens) > 1:
            prefix = '/'.join(tokens[1:]) + '/'
        else:
            prefix = ''
        return prefix
    
    def get_time_interval(self):
        self.ts_from = datetime.datetime.utcnow() - datetime.timedelta(days=500)
        self.ts_to = datetime.datetime.utcnow()
        self.ts_from = self.ts_from.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0)
        self.ts_to = self.ts_to.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0)              
    
    def make_objects_list_request(self, marker='', prefix=''):
        response = self.s3.list_objects(
            Bucket=self.AWS_MACIE_S3_BUCKET, 
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

    def get_files_list(self):
        files = []
        folders = self.s3.list_objects(Bucket=self.AWS_MACIE_S3_BUCKET, Prefix=self.aws_s3_prefix, Delimiter='/').get("Contents")
        for file_obj in folders:
            if self.ts_to > file_obj['LastModified'] >= self.ts_from:
                files.append(file_obj)
        print(files)

        return self.sort_files_by_date(files)

    def download_obj(self, key):
        logging.info('Started downloading {}'.format(key))
        res = self.s3.get_object(Bucket=self.AWS_MACIE_S3_BUCKET, Key=key)
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
            elif '.jsonl.gz' in key.lower():
                extracted_file = gzip.GzipFile(fileobj=file_obj).read().decode('utf-8')
            elif '.log.gz' in key.lower():
                extracted_file = gzip.GzipFile(fileobj=file_obj).read().decode('utf-8')                             
            elif '.json' in key.lower():
                extracted_file = file_obj
            return extracted_file

        except Exception as err:
            logging.error('Error while unpacking file {} - {}'.format(key, err))

    @staticmethod
    def convert_empty_string_to_null_values(d: dict):
        for k, v in d.items():
            if v == '' or (isinstance(v, list) and len(v) == 1 and v[0] == ''):
                d[k] = None
        return d
        
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
        elif '.jsonl.gz' in key.lower():
            downloaded_obj = self.download_obj(key)
            json_file = self.unpack_file(downloaded_obj, key)
            sortedLogEvents = json_file.split('\n')
        elif '.csv.gz' in key.lower():
            downloaded_obj = self.download_obj(key)
            csv_file = self.unpack_file(downloaded_obj, key)
            sortedLogEvents = self.parse_csv_file(csv_file)
        elif '.log.gz' in key.lower():
            downloaded_obj = self.download_obj(key)
            csv_file = self.unpack_file(downloaded_obj, key)
            sortedLogEvents = self.parse_log_file(csv_file)
        elif '.json' in key.lower():
            downloaded_obj = self.download_obj(key)
            sortedLogEvents = self.unpack_file(downloaded_obj, key)            
            
        return sortedLogEvents


class SentinelConnector():
    def __init__(self, CUSTOMER_ID, SHARED_KEY):
        self.customer_id = CUSTOMER_ID
        self.shared_key = SHARED_KEY
        return
    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(self.customer_id,encoded_hash)
        return authorization

    # Build and send a request to the POST API
    def post_data(self, body, log_type):
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self.build_signature(rfc1123date, content_length, method, content_type, resource)
        uri = 'https://' + self.customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': log_type,
            'x-ms-date': rfc1123date
        }

        response = requests.post(uri,data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            print(response)
        else:
            print("Response code: {}".format(response.status_code))

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    s3 = S3Client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME, AWS_INSPECTOR_S3_BUCKET)
    sentinel = SentinelConnector(CUSTOMER_ID, SHARED_KEY)
    obj_list = s3.get_files_list()
    coreEvents = []   

    for obj in obj_list:
        log_events = s3.process_obj(obj)       
        for log in log_events:
            if len(log) > 0:
                coreEvents.append(json.loads(log))
    sentinel.post_data(json.dumps(coreEvents), 'AWS_Inspector')

    s3 = S3Client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME, AWS_INSPECTOR_S3_BUCKET)
    obj_list = s3.get_files_list()
    coreEvents = []   
    for obj in obj_list:
        log_events = s3.process_obj(obj)       
        for log in log_events:
            if len(log) > 0:
                coreEvents.append(json.loads(log))
    sentinel.post_data(json.dumps(coreEvents), 'Macie')