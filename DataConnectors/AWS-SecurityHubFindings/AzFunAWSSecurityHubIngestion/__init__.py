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
import asn1
import cffi
from boto3.session import Session
import azure.functions as func
from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential, DefaultAzureCredential
import botocore
from azure.core.exceptions import ClientAuthenticationError

client_id = os.environ.get('ClientID')
sentinel_customer_id = os.environ.get('WorkspaceID')
sentinel_shared_key = os.environ.get('WorkspaceKey')
aws_role_arn = os.environ.get('AWSRoleArn') # Should be full ARN, including AWS account number eg. arn:aws:iam::133761391337:role/AzureSentinelSyncRole
aws_role_session_name =  os.environ.get('AWSRoleSessionName')
aws_region_name = os.environ.get('AWSRegionName')
aws_securityhub_filters = os.environ.get('SecurityHubFilters')
sentinel_log_type = os.environ.get('LogAnalyticsCustomLogName')
fresh_event_timestamp = os.environ.get('FreshEventTimeStamp')
logAnalyticsUri = os.environ.get('LAURI')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + sentinel_customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("AWSSecurityHubFindingsDataconnector: Invalid Log Analytics Uri.")


def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Starting program')
    # auth to azure ad
    logging.info ("Authenticating to Azure AD.")
    try:
        managed_identity = ManagedIdentityCredential()
        azure_cli = AzureCliCredential()
        default_azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        credential_chain = ChainedTokenCredential(managed_identity, azure_cli, default_azure_credential)
        token_meta = credential_chain.get_token(client_id)
        token = token_meta.token
    except ClientAuthenticationError as error:
        logging.info ("Authenticating to Azure AD: %s" % error)
    
    sentinel = AzureSentinelConnector(logAnalyticsUri, sentinel_customer_id, sentinel_shared_key, sentinel_log_type, queue_size=10000, bulks_number=10)
    securityHubSession = SecurityHubClient(aws_role_arn, aws_role_session_name, aws_region_name, token)
    securityhub_filters_dict = {}
    logging.info ('SecurityHubFilters : {0}'.format(aws_securityhub_filters))
    if aws_securityhub_filters:
        securityhub_filters = aws_securityhub_filters.replace("\'", "\"") 
        securityhub_filters_dict = eval(securityhub_filters)
        
    results = securityHubSession.getFindings(securityhub_filters_dict)
    fresh_events_after_this_time = securityHubSession.freshEventTimestampGenerator(int(fresh_event_timestamp))
    fresh_events = True
    first_call = True
    failed_sent_events_number = 0
    successfull_sent_events_number = 0
    
    while ((first_call or 'NextToken' in results) and fresh_events):
        # Loop through all findings (100 per page) returned by Security Hub API call		
		# Break out of the loop when we have looked back across the last hour of events (based on the finding's LastObservedAt timestamp)
        first_call = False
        
        for finding in results['Findings']:
            finding_timestamp = securityHubSession.findingTimestampGenerator(finding['LastObservedAt'])
                        
            if (finding_timestamp > fresh_events_after_this_time):
                logging.info ('SecurityHub Finding:{0}'.format(json.dumps(finding)))
                payload = {}                
                payload.update({'SchemaVersion':finding['SchemaVersion']})
                payload.update({'Id':finding['Id']})
                payload.update({'ProductArn':finding['ProductArn']})
                payload.update({'GeneratorId':finding['GeneratorId']})
                payload.update({'AwsAccountId':finding['AwsAccountId']})
                payload.update({'Types':finding['Types']})
                payload.update({'FirstObservedAt':finding['FirstObservedAt']})
                payload.update({'LastObservedAt':finding['LastObservedAt']})
                payload.update({'UpdatedAt':finding['UpdatedAt']})
                payload.update({'Severity':json.dumps(finding['Severity'], sort_keys=True)})
                payload.update({'Title':finding['Title']})                        
                payload.update({'ProductFields':json.dumps(finding['ProductFields'], sort_keys=True)})
                payload.update({'ProductArn':finding['ProductArn']})
                payload.update({'CreatedAt':finding['CreatedAt']})            
                payload.update({'Resources':finding['Resources']})            
                payload.update({'WorkflowState':finding['WorkflowState']})                
                payload.update({'RecordState':finding['RecordState']})
                
                with sentinel:
                    sentinel.send(payload)
                    
                failed_sent_events_number = sentinel.failed_sent_events_number
                successfull_sent_events_number = sentinel.successfull_sent_events_number              
            else:
                fresh_events = False
                break
            
        if (fresh_events and 'NextToken' in results):
            results = securityHubSession.getFindingsWithToken(results['NextToken'], securityhub_filters_dict)
    
    if failed_sent_events_number:
        logging.error('{} events have not been sent'.format(failed_sent_events_number))

    if successfull_sent_events_number:
        logging.info('Program finished. {} events have been sent. {} events have not been sent'.format(successfull_sent_events_number, failed_sent_events_number))

    if successfull_sent_events_number == 0 and failed_sent_events_number == 0:
        logging.info('No Fresh SecurityHub Events')

class SecurityHubClient:
    def __init__(self, aws_role_arn, aws_role_session_name, aws_region_name, token):

        # define input
        self.role_arn = aws_role_arn
        self.role_session_name = aws_role_session_name
        self.aws_region_name = aws_region_name
        self.web_identity_token = token

        # create an STS client object that represents a live connection to the STS service
        sts_client = boto3.client('sts')
	
        # call assume_role method using input + client
        try:
            assumed_role_object=sts_client.assume_role_with_web_identity(
                RoleArn=self.role_arn,
                RoleSessionName=self.role_session_name,
                WebIdentityToken=self.web_identity_token
                )
            logging.info ("Successfully assumed role with web identity.")            
        except botocore.exceptions.ClientError as error:
            logging.info ("Assuming role with web identity failed: %s" % error)

        # from the response, get credentials
        credentials=assumed_role_object['Credentials']
        logging.info ('AccessKeyId : {0}'.format(credentials['AccessKeyId']))
        logging.info ('AssumedRoleArn : {0}'.format(assumed_role_object['AssumedRoleUser']['Arn']))

        # use temp creds to make connection
        self.securityhub = boto3.client(
            'securityhub',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=self.aws_region_name
        )

    def freshEventTimestampGenerator(self, freshEventsDuration):
        tm = datetime.datetime.utcfromtimestamp(time.time())
        return time.mktime((tm - datetime.timedelta(minutes=freshEventsDuration)).timetuple())

    # Gets the epoch time of a UTC timestamp in a Security Hub finding
    def findingTimestampGenerator(self, finding_time):
        d = dateutil.parser.parse(finding_time)
        d.astimezone(dateutil.tz.tzutc())
        return time.mktime(d.timetuple())

    # Gets 100 most recent findings from securityhub
    def getFindings(self, filters={}):
        return self.securityhub.get_findings(
            Filters=filters,
            MaxResults=100,
            SortCriteria=[{"Field": "LastObservedAt", "SortOrder": "desc"}])
        
    # Gets 100 findings from securityhub using the NextToken from a previous request
    def getFindingsWithToken(self, token, filters={}):
        return self.securityhub.get_findings(
	        Filters=filters,
	        NextToken=token,
            MaxResults=100,
            SortCriteria=[{"Field": "LastObservedAt", "SortOrder": "desc"}]
	    )


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
        self.failedToSend = False

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
        body = json.dumps(body, sort_keys=True)
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
            self.successfull_sent_events_number += events_number
            self.failedToSend = False
        else:
            logging.error("Error during sending events to Azure Sentinel. Response code: {}".format(response.status_code))
            self.failed_sent_events_number += events_number
            self.failedToSend = True

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
