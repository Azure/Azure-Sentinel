import requests
import datetime
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
from threading import Thread
from io import StringIO
from .state_manager import StateManager
from dateutil.parser import parse as parse_datetime
import azure.functions as func
import re



MAX_SCRIPT_EXEC_TIME_MINUTES = 10

DIVIDE_TO_MULTIPLE_TABLES = True


sentinel_customer_id = os.environ.get('WorkspaceID')
sentinel_shared_key = os.environ.get('WorkspaceKey')
sentinel_log_type = 'Cisco_Umbrella'

aws_s3_bucket = os.environ.get('S3Bucket')
aws_access_key_id = os.environ.get('AWSAccessKeyId')
aws_secret_acces_key = os.environ.get('AWSSecretAccessKey')
logAnalyticsUri = os.environ.get('logAnalyticsUri')
FILE_SHARE_CONN_STRING = os.environ['AzureWebJobsStorage']

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + sentinel_customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Cisco_Umbrella: Invalid Log Analytics Uri.")


def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Starting program')
    
    script_start_time = int(time.time())
    state_manager_cu = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_umbrella')
    
    ts_from = state_manager_cu.get()
    ts_to = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    if ts_from is not None:
        if (datetime.datetime.utcnow() - datetime.timedelta(days=3)) > datetime.datetime.strptime(ts_from,"%Y-%m-%dT%H:%M:%S.%fZ"):
            ts_from = parse_date_from(ts_from)
            ts_to = ts_from +  datetime.timedelta(days=1)
        else:
            ts_to = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    ts_from = parse_date_from(ts_from)
    ts_to = ts_to.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0)
        
    cli = UmbrellaClient(aws_access_key_id, aws_secret_acces_key, aws_s3_bucket)
    
    logging.info('Searching files last modified from {} to {}'.format(ts_from, ts_to))
    obj_list = cli.get_files_list(ts_from, ts_to)

    logging.info('Total number of files is {}. Total size is {} MB'.format(
        len(obj_list),
        round(sum([x['Size'] for x in obj_list]) / 10**6, 2)
    ))

    failed_sent_events_number = 0
    successfull_sent_events_number = 0

    if DIVIDE_TO_MULTIPLE_TABLES:
        sentinel_dict = {
        'dns': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_dns', queue_size=10000, bulks_number=10),
        'proxy': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_proxy', queue_size=10000, bulks_number=10),
        'ip': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_ip', queue_size=10000, bulks_number=10),
        'cloudfirewall': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_cloudfirewall', queue_size=10000, bulks_number=10),
        'firewall': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_firewall', queue_size=10000, bulks_number=10),
        'dlp': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_dlp', queue_size=10000, bulks_number=10),  # Added DLP
        'ravpn': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_ravpnlogs', queue_size=10000, bulks_number=10),
        'audit': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_audit', queue_size=10000, bulks_number=10),
        'ztna': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_ztna', queue_size=10000, bulks_number=10),
        'intrusion': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_intrusion', queue_size=10000, bulks_number=10),
        'ztaflow': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_ztaflow', queue_size=10000, bulks_number=10),
        'fileevent': AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type + '_fileevent', queue_size=10000, bulks_number=10)
                        }
        last_ts = None
        for obj in sorted(obj_list, key=lambda k: k['LastModified']):
            key = obj.get('Key', '')
            if 'dnslogs' in key.lower():
                sentinel = sentinel_dict['dns']
            elif 'proxylogs' in key.lower():
                sentinel = sentinel_dict['proxy']
            elif 'iplogs' in key.lower():
                sentinel = sentinel_dict['ip']
            elif 'cloudfirewalllogs' in key.lower() or 'cdfwlogs' in key.lower():
                sentinel = sentinel_dict['cloudfirewall']
            elif 'firewalllogs' in key.lower():
                sentinel = sentinel_dict['firewall']
            elif 'dlplogs' in key.lower():  # Added DLP
                sentinel = sentinel_dict['dlp']
            elif 'ravpnlogs' in key.lower():  # Added RAVPN
                sentinel = sentinel_dict['ravpn']
            elif 'auditlogs' in key.lower(): # Added Audit
                sentinel = sentinel_dict['audit']
            elif 'ztnalogs' in key.lower():  # Added ZTNA
                sentinel = sentinel_dict['ztna']
            elif 'intrusionlogs' in key.lower():  # Added Intrusion
                sentinel = sentinel_dict['intrusion']
            elif 'ztaflowlogs' in key.lower():  # Added ZTA Flow
                sentinel = sentinel_dict['ztaflow']
            elif 'fileeventlogs' in key.lower():  # Added File Event
                sentinel = sentinel_dict['fileevent']
            else:
                # skip files of unknown types
                continue
            with sentinel:
                cli.process_file(obj, dest=sentinel)
                last_ts = obj['LastModified']
                if last_ts:
                    state_manager_cu.post(datetime.datetime.strftime(last_ts, '%Y-%m-%dT%H:%M:%S.%fZ'))
                    if check_if_script_runs_too_long(script_start_time):
                        logging.info(f'Script is running too long. Stop processing new events. Finish script.')
                        break
                else:
                    state_manager_cu.post(datetime.datetime.strftime(ts_to, '%Y-%m-%dT%H:%M:%S.%fZ'))
                    if check_if_script_runs_too_long(script_start_time):
                        logging.info(f'Script is running too long. Stop processing new events. Finish script.')
                        break
        if last_ts:
            state_manager_cu.post(datetime.datetime.strftime(last_ts, '%Y-%m-%dT%H:%M:%S.%fZ'))
        else:
            state_manager_cu.post(datetime.datetime.strftime(ts_to, '%Y-%m-%dT%H:%M:%S.%fZ'))

        failed_sent_events_number = sum([sentinel.failed_sent_events_number for sentinel in sentinel_dict.values()])
        successfull_sent_events_number = sum([sentinel.successfull_sent_events_number for sentinel in sentinel_dict.values()])


    else:
        sentinel = AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type, queue_size=10000, bulks_number=10)
        with sentinel:
            for obj in sorted(obj_list, key=lambda k: k['LastModified']):
                cli.process_file(obj, dest=sentinel)
                last_ts = obj['LastModified']
                if last_ts:
                    state_manager_cu.post(datetime.datetime.strftime(last_ts, '%Y-%m-%dT%H:%M:%S.%fZ'))
                    if check_if_script_runs_too_long(script_start_time):
                        logging.info(f'Script is running too long. Stop processing new events. Finish script.')
                        return
                else:
                    state_manager_cu.post(datetime.datetime.strftime(ts_to, '%Y-%m-%dT%H:%M:%S.%fZ'))
                    if check_if_script_runs_too_long(script_start_time):
                        logging.info(f'Script is running too long. Stop processing new events. Finish script.')
                        return
            
            if last_ts:
                state_manager_cu.post(datetime.datetime.strftime(last_ts, '%Y-%m-%dT%H:%M:%S.%fZ'))
            else:
                state_manager_cu.post(datetime.datetime.strftime(ts_to, '%Y-%m-%dT%H:%M:%S.%fZ'))   
                
        failed_sent_events_number += sentinel.failed_sent_events_number
        successfull_sent_events_number += sentinel.successfull_sent_events_number

    if failed_sent_events_number:
        logging.error('{} events have not been sent'.format(failed_sent_events_number))

    logging.info('Program finished. {} events have been sent. {} events have not been sent'.format(successfull_sent_events_number, failed_sent_events_number))


def convert_list_to_csv_line(ls):
    line = StringIO()
    writer = csv.writer(line)
    writer.writerow(ls)
    return line.getvalue()


def check_if_script_runs_too_long(script_start_time: int) -> bool:
        now = int(time.time())
        duration = now - script_start_time
        max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.80)
        return duration > max_duration


def parse_date_from(date_from: str) -> datetime.datetime:
    try:
        date_from = parse_datetime(date_from)+ datetime.timedelta(milliseconds=1)
    except:
        pass
    if not isinstance(date_from, datetime.datetime):
        date_from = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(minutes=10)
    return date_from

    
class UmbrellaClient:

    def __init__(self, aws_access_key_id, aws_secret_acces_key, aws_s3_bucket):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_acces_key = aws_secret_acces_key
        self.aws_s3_bucket = self._get_s3_bucket_name(aws_s3_bucket)
        self.aws_s3_prefix = self._get_s3_prefix(aws_s3_bucket)
        self.total_events = 0
        self.input_date_format = '%Y-%m-%d %H:%M:%S'
        self.output_date_format = '%Y-%m-%dT%H:%M:%SZ'

        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_acces_key
        )

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
        folders = ['dnslogs', 'proxylogs', 'iplogs', 'firewalllogs', 'cloudfirewalllogs', 'cdfwlogs',
                   'dlplogs', 'ravpnlogs', 'auditlogs', 'ztnalogs', 'intrusionlogs', 'ztaflowlogs', 'fileeventlogs']
        if self.aws_s3_prefix:
            folders = [self.aws_s3_prefix + folder for folder in folders]

        marker_end = (ts_from - datetime.timedelta(minutes=60)).strftime("/%Y-%m-%d/%Y-%m-%d-%H-%M")

        for folder in folders:
            marker = folder + marker_end
            while True:
                response = self._make_objects_list_request(marker=marker, prefix=folder)
                for file_obj in response.get('Contents', []):
                    if ts_to > file_obj['LastModified'] >= ts_from:
                        files.append(file_obj)

                if response['IsTruncated'] is True and ts_to > file_obj['LastModified']:
                    marker = response['Contents'][-1]['Key']
                else:
                    break
                
        return files

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
            csv_file = gzip.GzipFile(fileobj=file_obj).read().decode()
            return csv_file

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

    def parse_csv_ip(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 7:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'Identity': row[1],
                        'Source IP': row[2],
                        'Source Port': row[3],
                        'Destination IP': row[4],
                        'Destination Port': row[5],
                        'Categories': row[6].split(',')
                    }
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event = self.convert_empty_string_to_null_values(event)
                event['EventType'] = 'iplogs'
                yield event
                
    def parse_csv_dlp(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 25:
                # Adjust the field mapping as per Cisco DLP log format documentation
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'Event Type': row[1],
                        'Unique Event ID': row[2],
                        'Severity': row[3],
                        'Identities': row[4],
                        'Owner': row[5],
                        'Name': row[6],
                        'Application': row[7],
                        'Destination': row[8],
                        'Action': row[9],
                        'Rule Name': row[10],
                        'Data Classification': row[11],
                        'Data Identifier': row[12],
                        'Content Type': row[13],
                        'File Size': row[14],
                        'SHA256 Hash': row[15],
                        'File Label': row[16],
                        'Application Category Name': row[17],
                        'Traffic Direction': row[18],
                        'Private Resource Name': row[19],
                        'Private Resource Group Name': row[20],
                        'Destination Protocol': row[21],
                        'Destination IP': row[22],
                        'Destination Port': row[23],
                        'Organization ID': row[24]
                    }
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event = self.convert_empty_string_to_null_values(event)
                event['EventType'] = 'dlplogs'
                yield event

    def parse_csv_proxy(self, csv_file):
        sanitized_csv_file = csv_file.replace('\x00', '')
        
        csv_reader = csv.reader(sanitized_csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            try:
                if len(row) > 1:
                    if len(row) >= 21:
                        event = {
                            'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                            'Identities': row[1],
                            'Policy Identity': row[1],
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
                            'AMP Score': row[20],
                            'Policy Identity Type': row[21]
                        }
                        try:
                            event['Blocked Categories'] = row[22].split(',')
                        except IndexError:
                            pass
                         #Version 5 — The same as version 4, but adds three new fields: all Identities, all Identity Types, and Request Method for Proxy logs.
                        try:
                            event['Identities'] = row[23]
                        except IndexError:
                            pass
                        try:
                            event['Identity Types'] = row[24]
                        except IndexError:
                            pass
                        try:
                            event['Request Method'] = row[25]
                        except IndexError:
                            pass
                        #Version 6 — The same as version 5 with these additional fields to Proxy logs: Certificate Errors, Destination Lists IDs, DLP Status, File Name, Rule ID, and Ruleset ID.
                        try:
                            event['DLP Status'] = row[26]
                        except IndexError:
                            pass                     
                        try:
                            event['Certificate Errors'] = row[27]
                        except IndexError:
                            pass
                        try:
                            event['File Name'] = row[28]
                        except IndexError:
                            pass
                        try:
                            event['Ruleset ID'] = row[29]
                        except IndexError:
                            pass                                                         
                        try:
                            event['Rule ID'] = row[30]
                        except IndexError:
                            pass
                        try:
                            event['Destination List IDs'] = row[31]
                        except IndexError:
                            pass
                        try:                                         
                            event['Isolate Action'] = row[32]
                        except IndexError:
                            pass
                        try:
                            event['File Action'] = row[33]
                        except IndexError:
                            pass
                        try:
                            event['Warn Status'] = row[34]
                        except IndexError:
                            pass    
                        try:
                            event['Forwarding Method'] = row[35]
                        except IndexError:
                            pass
                        try:
                            event['Producer'] = row[36]
                        except IndexError:
                            pass
                        try:
                            event['MSP Organization ID'] = row[37]
                        except IndexError:
                            pass
                        try:
                            event['Geo Location Of Blocked Destination Countries'] = row[38]
                        except IndexError:
                            pass
                        try:
                            event['Application IDs'] = row[39]
                        except IndexError:
                            pass
                        try:
                            event['Host Name'] = row[40]
                        except IndexError:
                            pass
                        try:
                            event['Data Center'] = row[41]
                        except IndexError:
                            pass
                        try:
                            event['Egress'] = row[42]
                        except IndexError:
                            pass
                        try:
                            event['Server Name'] = row[43]
                        except IndexError:
                            pass
                        try:
                            event['Time Based Rule'] = row[44]
                        except IndexError:
                            pass
                        try:
                            event['Security Overridden'] = row[45]
                        except IndexError:
                            pass
                        try:
                            event['Detected Response File Type'] = row[46]
                        except IndexError:
                            pass
                        try:
                            event['Warn Categories'] = row[47]
                        except IndexError:
                            pass
                        try:
                            event['Organization ID'] = row[48]
                        except IndexError:
                            pass
                        try:
                            event['Application Entity Name'] = row[49]
                        except IndexError:
                            pass
                        try:
                            event['Application Entity Category'] = row[50]
                        except IndexError:
                            pass
                        # Version 12 — The same as version 11, but adds the Egress IP field to Proxy logs.
                        try:
                            event['Egress IP'] = row[51]
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
                    event['EventType'] = 'proxylogs'
                    yield event
            except Exception as e:
                logging.error(f"Error processing row {row}: {e}")
                continue

    def parse_csv_dns(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 10:
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
                    try:
                        event['Rule ID'] = row[13]
                    except IndexError:
                        pass
                    try:
                        event['Destination Countries'] = row[14]
                    except IndexError:
                        pass
                    try:
                        event['Organization ID'] = row[15]
                    except IndexError:
                        pass
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event = self.convert_empty_string_to_null_values(event)
                event['EventType'] = 'dnslogs'
                yield event

    def parse_csv_cdfw(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 14:
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
                    try:
                        event['FQDNS'] = row[14]
                    except IndexError:
                        pass
                    try:
                        event['Destination List IDs'] = row[15]
                    except IndexError:
                        pass
                    try:
                        event['First Packet Timestamp'] = row[16]
                    except IndexError:
                        pass
                    try:
                        event['Last Packet Timestamp'] = row[17]
                    except IndexError:
                        pass
                    try:
                        event['Packets Sent'] = row[18]
                    except IndexError:
                        pass
                    try:
                        event['Packets Received'] = row[19]
                    except IndexError:
                        pass
                    try:
                        event['Bytes Sent'] = row[20]
                    except IndexError:
                        pass
                    try:
                        event['Bytes Received'] = row[21]
                    except IndexError:
                        pass
                    try:
                        event['FW Event ID'] = row[22]
                    except IndexError:
                        pass
                    try:
                        event['Destination Country'] = row[23]
                    except IndexError:
                        pass
                    try:
                        event['AWS Region'] = row[24]
                    except IndexError:
                        pass
                    try:
                        event['App ID'] = row[25]
                    except IndexError:
                        pass
                    try:
                        event['Private App ID'] = row[26]
                    except IndexError:
                        pass
                    try:
                        event['Private Flow'] = row[27]
                    except IndexError:
                        pass
                    try:
                        event['Posture ID'] = row[28]
                    except IndexError:
                        pass
                    try:
                        event['CASI Category IDs'] = row[29]
                    except IndexError:
                        pass
                    try:
                        event['Traffic Source'] = row[30]
                    except IndexError:
                        pass
                    try:
                        event['Content Category IDs'] = row[31]
                    except IndexError:
                        pass
                    try:
                        event['Content Category List IDs'] = row[32]
                    except IndexError:
                        pass
                    try:
                        event['Organization ID'] = row[33]
                    except IndexError:
                        pass
                    try:
                        event['Egress IP'] = row[34]
                    except IndexError:
                        pass
                    try:
                        event['Egress'] = row[35]
                    except IndexError:
                        pass
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event['EventType'] = 'cloudfirewalllogs'
                yield event

    def parse_csv_ravpn(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 14:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'Host Name': row[1],
                        'AWS Region': row[2],
                        'Event Type': row[3],
                        'Origin IDs': row[4],
                        'Origin Type': row[5],
                        'User ID': row[6],
                        'Organization ID': row[7],
                        'Retention Days': row[8],
                        'Storage Location': row[9],
                        'MSP Organization ID': row[10],
                        'Session ID': row[11],
                        'Session Type': row[12],
                        'VPN Profile': row[13],
                        'Public IP': row[14],
                        'Assigned IP': row[15],
                        'Connected At': row[16],
                        'Disconnection Reason': row[17],
                        'OS Version': row[18],
                        'Any Connect Version': row[19],
                    }
                    try:
                        event['ASA Syslog ID'] = row[20]
                    except IndexError:
                        pass
                    try:
                        event['Device ID'] = row[21]
                    except IndexError:
                        pass
                    try:
                        event['Machine ID'] = row[22]
                    except IndexError:
                        pass
                    try:
                        event['Public IPv6'] = row[23]
                    except IndexError:
                        pass
                    try:
                        event['Assigned IPv6'] = row[24]
                    except IndexError:
                        pass
                    try:
                        event['Security Group Tag'] = row[25]
                    except IndexError:
                        pass
                    try:
                        event['DAP Record Name'] = row[26]
                    except IndexError:
                        pass
                    try:
                        event['DAP Connection Type'] = row[27]
                    except IndexError:
                        pass
                    try:
                        event['Failed Reasons'] = row[28]
                    except IndexError:
                        pass
                    try:
                        event['log message'] = row[29]
                    except IndexError:
                        pass
                    try:
                        event['asa syslog severity'] = row[30]
                    except IndexError:
                        pass
                    try:
                        event['asa syslog class'] = row[31]
                    except IndexError:
                        pass
                    try:
                        event['asa syslog description'] = row[32]
                    except IndexError:
                        pass
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event['EventType'] = 'ravpnlogs'
                yield event

    def parse_csv_audit(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 9:
                    event = {
                        'id': row[0],
                        'Timestamp': self.format_date(row[1], self.input_date_format, self.output_date_format),
                        'email': row[2],
                        'user': row[3],
                        'type': row[4],
                        'action': row[5],
                        'logged in from': row[6],
                        'before': row[7],
                        'after': row[8]
                    }
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event['EventType'] = 'auditlogs'
                yield event

    def parse_csv_ztna(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 29:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'identity email': row[1],
                        'identity labels': row[2],
                        'identity type labels': row[3],
                        'hostname': row[4],
                        'verdict': row[5],
                        'client os': row[6],
                        'client browser': row[7],
                        'client geo location': row[8],
                        'client ip': row[9],
                        'ruleset id': row[10],
                        'rule id': row[11],
                        'private app group id': row[12],
                        'private app id': row[13],
                        'private resource id': row[14],
                        'private resource group id': row[15],
                        'step up auth type': row[16],
                        'step up auth result': row[17],
                        'step up auth token life': row[18],
                        'posture id': row[19],
                        'requested id fqdn': row[20],
                        'resolved ip': row[21],
                        'app Connector group id': row[22],
                        'headend type': row[23],
                        'duo device id': row[24],
                        'duo device id string': row[25],
                        'system password': row[26],
                        'client firewall': row[27],
                        'disk encryption': row[28],
                        'anti malware agents': row[29]
                    }
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event['EventType'] = 'ztnalogs'
                yield event

    def parse_csv_ztaflow(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 23:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'identity email': row[1],
                        'identity labels': row[2],
                        'identity type labels': row[3],
                        'organization id': row[4],
                        'msp organization id': row[5],
                        'hostname': row[6],
                        'transaction id': row[7],
                        'private resource id': row[8],
                        'private resource group id': row[9],
                        'app connector id': row[10],
                        'app connector group id': row[11],
                        'ruleset id': row[12],
                        'rule id': row[13],
                        'connection status': row[14],
                        'connection failure reason': row[15],
                        'headend type': row[16],
                        'event type': row[17],
                        'rxbytes': row[18],
                        'txbytes': row[19],
                        'egress ip': row[20],
                        'egress port': row[21],
                        'nt group id': row[22],
                        'zta source port': row[23]
                    }
                    try:
                        event['enforced by'] = row[24]
                    except IndexError:
                        pass
                    try:
                        event['ftd enforcement id'] = row[25]
                    except IndexError:
                        pass
                    try:
                        event['ftd enforcement name'] = row[26]
                    except IndexError:
                        pass
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event['EventType'] = 'ztaflowlogs'
                yield event

    def parse_csv_fileevent(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 19:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'organization id': row[1],
                        'retention policy': row[2],
                        'aws region': row[3],
                        'firewall event id': row[4],
                        'file action': row[5],
                        'disposition': row[6],
                        'sha256': row[7],
                        'direction': row[8],
                        'threat name': row[9],
                        'file static analysis': row[10],
                        'threat score': row[11],
                        'file type id': row[12],
                        'file name': row[13],
                        'file size': row[14],
                        'archive file name': row[15],
                        'archive depth': row[16],
                        'archive sha': row[17],
                        'dlp status': row[18]
                    }
                    try:
                        event['enforced by'] = row[19]
                    except IndexError:
                        pass
                    try:
                        event['ftd enforcement id'] = row[20]
                    except IndexError:
                        pass
                    try:
                        event['ftd enforcement name'] = row[21]
                    except IndexError:
                        pass
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event['EventType'] = 'fileeventlogs'
                yield event

    def parse_csv_intrusion(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 16:
                    event = {
                        'Timestamp': self.format_date(row[0], self.input_date_format, self.output_date_format),
                        'identities': row[1],
                        'identity types': row[2],
                        'generator id': row[3],
                        'signature ID': row[4],
                        'signature message': row[5],
                        'signature List ID': row[6],
                        'severity': row[7],
                        'attack classification': row[8],
                        'CVEs': row[9],
                        'IP protocol': row[10],
                        'session ID': row[11],
                        'source IP': row[12],
                        'source port': row[13],
                        'destination IP': row[14],
                        'destination Port': row[15],
                        'action': row[16]
                    }
                    try:
                        event['operation mode'] = row[17]
                    except IndexError:
                        pass
                    try:
                        event['policy resource ID'] = row[18]
                    except IndexError:
                        pass
                    try:
                        event['direction'] = row[19]
                    except IndexError:
                        pass
                    try:
                        event['firewall rule ID'] = row[20]
                    except IndexError:
                        pass
                    try:
                        event['IPS config type'] = row[21]
                    except IndexError:
                        pass
                    try:
                        event['AWS region'] = row[22]
                    except IndexError:
                        pass
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event['EventType'] = 'intrusionlogs'
                yield event
    
    def parse_csv_fw(self, csv_file):
        csv_reader = csv.reader(csv_file.split('\n'), delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                if len(row) >= 14:
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
                    try:
                        event['FQDNS'] = row[14]
                    except IndexError:
                        pass
                    try:
                        event['Destination List IDs'] = row[15]
                    except IndexError:
                        pass
                    try:
                        event['First Packet Timestamp'] = row[16]
                    except IndexError:
                        pass
                    try:
                        event['Last Packet Timestamp'] = row[17]
                    except IndexError:
                        pass
                    try:
                        event['Packets Sent'] = row[18]
                    except IndexError:
                        pass
                    try:
                        event['Packets Received'] = row[19]
                    except IndexError:
                        pass
                    try:
                        event['Bytes Sent'] = row[20]
                    except IndexError:
                        pass
                    try:
                        event['Bytes Received'] = row[21]
                    except IndexError:
                        pass
                    try:
                        event['FW Event ID'] = row[22]
                    except IndexError:
                        pass
                    try:
                        event['Destination Country'] = row[23]
                    except IndexError:
                        pass
                    try:
                        event['AWS Region'] = row[24]
                    except IndexError:
                        pass
                    try:
                        event['App ID'] = row[25]
                    except IndexError:
                        pass
                    try:
                        event['Private App ID'] = row[26]
                    except IndexError:
                        pass
                    try:
                        event['Private Flow'] = row[27]
                    except IndexError:
                        pass
                    try:
                        event['Posture ID'] = row[28]
                    except IndexError:
                        pass
                    try:
                        event['CASI Category IDs'] = row[29]
                    except IndexError:
                        pass
                    try:
                        event['Traffic Source'] = row[30]
                    except IndexError:
                        pass
                    try:
                        event['Content Category IDs'] = row[31]
                    except IndexError:
                        pass
                    try:
                        event['Content Category List IDs'] = row[32]
                    except IndexError:
                        pass
                    try:
                        event['Organization ID'] = row[33]
                    except IndexError:
                        pass
                    try:
                        event['Egress IP'] = row[34]
                    except IndexError:
                        pass
                    try:
                        event['Egress'] = row[35]
                    except IndexError:
                        pass
                else:
                    event = {"message": convert_list_to_csv_line(row)}
                event['EventType'] = 'firewalllogs'
                yield event

    def process_file(self, obj, dest):
        t0 = time.time()
        key = obj['Key']
        if 'csv.gz' in key.lower():
            downloaded_obj = self.download_obj(key)

            csv_file = self.unpack_file(downloaded_obj, key)

            parser_func = None
            if 'dnslogs' in key.lower():
                parser_func = self.parse_csv_dns
            elif 'proxylogs' in key.lower():
                parser_func = self.parse_csv_proxy
            elif 'iplogs' in key.lower():
                parser_func = self.parse_csv_ip
            elif 'cloudfirewalllogs' in key.lower() or 'cdfwlogs' in key.lower():
                parser_func = self.parse_csv_cdfw
            elif 'firewalllogs' in key.lower():
                parser_func =  self.parse_csv_fw
            elif 'dlplogs' in key.lower():  # Added DLP logs
                parser_func = self.parse_csv_dlp
            elif 'ravpnlogs' in key.lower():  # Added RAVPN logs
                parser_func = self.parse_csv_ravpn
            elif 'auditlogs' in key.lower():  # Added Audit logs
                parser_func = self.parse_csv_audit
            elif 'ztnalogs' in key.lower():  # Added ZTNA logs
                parser_func = self.parse_csv_ztna
            elif 'intrusionlogs' in key.lower():  # Added Intrusion logs
                parser_func = self.parse_csv_intrusion
            elif 'ztaflowlogs' in key.lower():  # Added ztaflowlogs logs
                parser_func = self.parse_csv_ztaflow
            elif 'fileeventlogs' in key.lower():  # Added fileeventlogs logs
                parser_func = self.parse_csv_fileevent
            if parser_func:
                file_events = 0
                for event in parser_func(csv_file):
                    dest.send(event)

                    file_events += 1
                    self.total_events += 1

                logging.info('File processed | TIME {} sec | SIZE {} MB | Events {} | Key {}'.format(round(time.time() - t0, 2), round(obj['Size'] / 10**6, 2), file_events, key))


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
            logging.info('{} events have been successfully sent to Microsoft Sentinel'.format(events_number))
            self.successfull_sent_events_number += events_number
        else:
            logging.error("Error during sending events to Microsoft Sentinel. Response code: {}".format(response.status_code))
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