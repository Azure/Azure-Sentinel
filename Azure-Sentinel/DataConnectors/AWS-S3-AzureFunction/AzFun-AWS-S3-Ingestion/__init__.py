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
s3_folder = os.environ.get('S3Folder')
sentinel_log_type = os.environ.get('LogAnalyticsCustomLogName')
fresh_event_timestamp = os.environ.get('FreshEventTimeStamp')

logAnalyticsUri = os.environ.get('LAURI')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + sentinel_customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")

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

    failed_sent_events_number = 0
    successfull_sent_events_number = 0    
    coreEvents = []   

    for obj in obj_list:
        log_events = cli.process_obj(obj)       
        
        for log in log_events:
            if len(log) > 0:
                coreEvents.append(log)
    
    file_events = 0
    t0 = time.time()    
    logging.info('Total number of files is {}'.format(len(coreEvents)))                                                                       
    for event in coreEvents:
        sentinel = AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type, queue_size=10000, bulks_number=10)
        with sentinel:
            sentinel.send(event)
        file_events += 1 
        failed_sent_events_number += sentinel.failed_sent_events_number
        successfull_sent_events_number += sentinel.successfull_sent_events_number
        
    if failed_sent_events_number:
        logging.info('{} AWS S3 files have not been sent'.format(failed_sent_events_number))

    if successfull_sent_events_number:
        logging.info('Program finished. {} AWS S3 files have been sent.'.format(successfull_sent_events_number))

    if successfull_sent_events_number == 0 and failed_sent_events_number == 0:
        logging.info('No Fresh AWS S3 files')

def convert_list_to_csv_line(ls):
    line = StringIO()
    writer = csv.writer(line)
    writer.writerow(ls)
    return line.getvalue()

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
            marker = o.get('Prefix') + s3_folder + marker_end   
            folder = o.get('Prefix') + s3_folder           
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

    def parse_csv_file(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) == 10:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'Policy Identity': row[1],
                        'Identities': row[2].split(','),
                        'InternalIp': row[3],
                        'ExternalIp': row[4],
                        'Action': row[5],
                        'QueryType': row[6],
                        'ResponseCode': row[7],
                        'Domain': row[8],
                        'Categories': row[9].split(',')
                    }
                    try:
                        event['Policy Identity Type'] = row[10]
                    except IndexError:
                        pass
                    try:
                        event['Identity Types'] = row[11].split(',')
                    except IndexError:
                        pass
                    try:
                        event['Blocked Categories'] = row[12].split(',')
                    except IndexError:
                        pass
                elif len(row) == 14:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'originId': row[1],
                        'Identity': row[2],
                        'Identity Type': row[3],
                        'Direction': row[4],
                        'ipProtocol': row[5],
                        'packetSize': row[6],
                        'sourceIp': row[7],
                        'sourcePort': row[8],
                        'destinationIp': row[9],
                        'destinationPort': row[10],
                        'dataCenter': row[11],
                        'ruleId': row[12],
                        'verdict': row[13]
                    }
                elif len(row) == 21:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'Identities': row[1],
                        'Internal IP': row[2],
                        'External IP': row[3],
                        'Destination IP': row[4],
                        'Content Type': row[5],
                        'Verdict': row[6],
                        'URL': row[7],
                        'Referer': row[8],
                        'userAgent': row[9],
                        'statusCode': row[10],
                        'requestSize': row[11],
                        'responseSize': row[12],
                        'responseBodySize': row[13],
                        'SHA-SHA256': row[14],
                        'Categories': row[15].split(','),
                        'AVDetections': row[16].split(','),
                        'PUAs': row[17].split(','),
                        'AMP Disposition': row[18],
                        'AMP Malware Name': row[19],
                        'AMP Score': row[20]
                    }
                    try:
                        event['Blocked Categories'] = row[21].split(',')
                    except IndexError:
                        pass

                    int_fields = [
                        'requestSize',
                        'responseSize',
                        'responseBodySize'
                    ]

                    for field in int_fields:
                        try:
                            event[field] = int(event[field])
                        except Exception:
                            pass                
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                
                event = self.convert_empty_string_to_null_values(event)                
                yield event
                
    def parse_log_file(self, log_file):
        log_reader = csv.reader(log_file.split('\n'), delimiter=' ')        
        for row in log_reader:
            if len(row) > 1:
                if len(row) == 28: #Service name, traffic path, and flow direction
                    event = {                    
                        'version': row[0],
                        'srcaddr': row[1],
                        'dstaddr': row[2],
                        'srcport': row[3],
                        'dstport': row[4],
                        'protocol': row[5],
                        'start': row[6],
                        'end': row[7],
                        'type': row[8],
                        'packets': row[9],
                        'bytes': row[10],
                        'account-id': row[11],                    
                        'vpc-id': row[12],
                        'subnet-id': row[13],
                        'instance-id': row[14],
                        'region': row[15],
                        'az-id': row[16],
                        'sublocation-type': row[17],
                        'sublocation-id': row[18],
                        'action': row[19],
                        'tcp-flags': row[20],
                        'pkt-srcaddr': row[21],
                        'pkt-dstaddr': row[22],
                        'pkt-src-aws-service': row[23],
                        'pkt-dst-aws-service': row[24],
                        'traffic-path': row[25],
                        'flow-direction': row[26],
                        'log-status': row[27]                    
                    }                   
                elif len(row) == 6: #Traffic through a NAT gateway
                    event = {                    
                        'instance-id': row[0],
                        'interface-id': row[1],
                        'srcaddr': row[2],
                        'dstaddr': row[3],
                        'pkt-srcaddr': row[4],
                        'pkt-dstaddr': row[5]
                    }                    
                elif len(row) == 17: #Traffic through a transit gateway
                    event = {                    
                        'version': row[0],
                        'interface-id': row[1],
                        'account-id': row[2],
                        'vpc-id': row[3],
                        'subnet-id': row[4],
                        'instance-id': row[5],
                        'srcaddr': row[6],
                        'dstaddr': row[7],
                        'srcport': row[8],
                        'dstport': row[9],
                        'protocol': row[10],
                        'tcp-flags': row[11],                    
                        'type': row[12],
                        'pkt-srcaddr': row[13],
                        'pkt-dstaddr': row[14],
                        'action': row[15],
                        'log-status': row[16]
                    }                    
                elif len(row) == 21: #TCP flag sequence
                    event = {                    
                        'version': row[0],
                        'vpc-id': row[1],
                        'subnet-id': row[2],
                        'instance-id': row[3],
                        'interface-id': row[4],
                        'account-id': row[5],
                        'type': row[6],
                        'srcaddr': row[7],
                        'dstaddr': row[8],
                        'srcport': row[9],
                        'dstport': row[10],
                        'pkt-srcaddr': row[11],                    
                        'pkt-dstaddr': row[12],
                        'protocol': row[13],
                        'bytes': row[14],
                        'packets': row[15],
                        'start': row[16],
                        'end': row[17],
                        'action': row[18],
                        'tcp-flags': row[19],
                        'log-status': row[20]
                    }                    
                elif len(row) == 14: 
                    #Accepted and rejected traffic; No data and skipped records
                    #Security group and network ACL rules; IPv6 traffic
                    event = {                    
                        'version': row[0],
                        'account-id': row[1],
                        'interface-id': row[2],
                        'srcaddr': row[3],
                        'dstaddr': row[4],
                        'srcport': row[5],
                        'dstport': row[6],
                        'protocol': row[7],
                        'packets': row[8],
                        'bytes': row[9],
                        'start': row[10],
                        'end': row[11],                    
                        'action': row[12],
                        'log-status': row[13]                        
                    }                    
                else:
                    event = {"message": convert_list_to_csv_line(row)}

                event = self.convert_empty_string_to_null_values(event)                
                yield event


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
        body = re.sub(r'\\', '', body)
        body = re.sub(r'"{', '{', body)
        body = re.sub(r'}"', '}', body)
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
