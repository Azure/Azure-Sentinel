import sys
import azure.functions as func
import datetime
import json
import base64
import hashlib
import hmac
import requests
import re
import os
import logging
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError

jwt_api_key = os.environ['LookoutClientId']
jwt_api_secret = os.environ['LookoutApiSecret']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
baseurl =  os.environ['Baseurl'] 
maxResults = os.environ['MaxResults'] 
Authurl = baseurl+"/apigw/v1/authenticate"
table_name = "LookoutCloudSecurity"
Schedule = os.environ['Schedule']
fetchDelay = os.environ['FetchDelay']
pastDays = os.environ['PastDays']
chunksize = 500
token = ""
if(fetchDelay is None):
 fetchDelay = 5

if(pastDays is None):
    pastDays = 7

logging.info("The Past days were taken as {}".format(pastDays))
logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(logAnalyticsUri))
if (not match):
    raise Exception("Lookout: Invalid Log Analytics Uri.")

##############################
######State Manager######  
##############################
class StateManager:
    def __init__(self, connection_string, share_name='funcstatemarkershare', file_path='Violationfuncstatemarkerfile'):
        self.share_cli = ShareClient.from_connection_string(conn_str=connection_string, share_name=share_name)
        self.file_cli = ShareFileClient.from_connection_string(conn_str=connection_string, share_name=share_name, file_path=file_path)

    def post(self, marker_text: str):
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self):
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None
##############################
######lookout Connector######  
##############################

class LookOut:

    def __init__(self):
        self.api_key = jwt_api_key
        self.api_secret = jwt_api_secret
        self.base_url = baseurl
        self.jwt_token_exp_hours = 1
        self.jwt_token = self.get_new_token()          

    def get_new_token(self):
        url = Authurl
        payload = json.dumps({
                "clientId": self.api_key,
                "clientSecret": self.api_secret,
                "grant_type": "refresh_token"
                })
        headers = {
                'Content-Type': 'application/json'
                }
        response = requests.request("POST", url, headers=headers, data=payload)
        tokens = json.loads(response.text) 
        return tokens['id_token']        
	    
    def generate_date(self):
        current_time_day = datetime.datetime.utcnow().replace(second=0, microsecond=0) 
        logging.info("Present time {}".format(current_time_day))
        current_time_day = (current_time_day - datetime.timedelta(minutes=int(fetchDelay))).strftime("%Y-%m-%dT%H:%M:%S")+".000-00:00"       
        logging.info("the fetch delay taken as {} minutes".format(fetchDelay))
        logging.info("After fetch time {}".format(current_time_day))
        state = StateManager(connection_string)
        past_time = state.get()
        if past_time is not None:
            logging.info("The last time run happened at: {}".format(past_time))
        else:
            logging.info("There is no last run timestamp, trying to get events for last week.")
            logging.info("The past days were taken as {} days".format(pastDays))
            past_time = (datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=int(pastDays))).strftime("%Y-%m-%dT%H:%M:%S")+".000-00:00"
        state.post(current_time_day)
        return (past_time, current_time_day)

    def get_Data(self,report_type_suffix,startTime,endTime):
            
        try:
            headers = {
                    'Authorization':'Bearer'+' '+ self.jwt_token
                     }
            payload = {}
            logging.info("The url being called: {}".format(baseurl + report_type_suffix+"&startTime="+startTime+"&endTime="+endTime+"&maxResults="+maxResults))
            response = requests.request("GET", baseurl + report_type_suffix+"&startTime="+startTime+"&endTime="+endTime+"&maxResults="+maxResults, headers=headers, data=payload)
            if response.status_code == 200:
                jsondata = json.loads(response.text)
                try:
                  return jsondata['data']
                except KeyError:
                    return []
            elif response.status_code == 400:
                logging.error("The requested report cannot be generated for this account because"
                      " this account has not subscribed to toll-free audio conference plan."
                      " Error code: {}".format(response.status_code))
            elif response.status_code == 401:
                logging.error("Invalid access token. Error code: {}".format(response.status_code))            
            else:
                logging.error("Something wrong. Error code: {}".format(response.status_code))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))

##############################
######Sentinel Connector######  
##############################

class Sentinel:

    def __init__(self):
        self.logAnalyticsUri = logAnalyticsUri
        self.success_processed = 0
        self.fail_processed = 0
        self.table_name = table_name
        self.chunksize = chunksize 
        self.sharedkey = shared_key       
        
    def gen_chunks_to_object(self, data, chunksize=500):
        chunk = []
        for index, line in enumerate(data):
            if (index % chunksize == 0 and index > 0):
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

    def gen_chunks(self, data):
        for chunk in self.gen_chunks_to_object(data, chunksize=self.chunksize):
            obj_array = []
            for row in chunk:
                if row != None and row != '':
                    obj_array.append(row)
            body = json.dumps(obj_array)
            self.post_data(body, len(obj_array))


    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(self.sharedkey)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self, body, chunk_count):
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self.build_signature(rfc1123date, content_length, method, content_type,
                                         resource)
        uri = self.logAnalyticsUri + resource + '?api-version=2016-04-01'
        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': self.table_name,
            'x-ms-date': rfc1123date
        }
        response = requests.post(uri, data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            logging.info("Chunk was processed{} Violations".format(chunk_count))
            self.success_processed = self.success_processed + chunk_count
        else:
            logging.error("Error during sending events to Microsoft Sentinel. Response code:{}".format(response.status_code))
            self.fail_processed = self.fail_processed + chunk_count  

# this function app is fired based on the Timer trigger
# it is used to capture all the events from LookOut cloud security API   
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
     logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    logging.info('Starting program')
    results_events = []
    try:
        Lookout = LookOut()
        sentinel = Sentinel()
        sentinel.sharedkey = shared_key
        sentinel.table_name= table_name    
        startTime,endTime = Lookout.generate_date()  
        logging.info("The current run Start time {}".format(startTime))
        logging.info("The current run End time {}".format(endTime))        
        logging.info('Start: to get Violation')
        results_events = Lookout.get_Data("/apigw/v1/events?eventType=Violation",startTime,endTime)
        logging.info("Activities was processed {} ".format(len(results_events)))
        logging.info('End: to get Violation')         
        
        if(len(results_events)) > 0:
         # Sort the json based on the "timestamp" key
         sorted_data = sorted(results_events, key=lambda x: x["timeStamp"],reverse=False) 
         # Fetch the latest timestamp
         latest_timestamp = sorted_data[-1]["timeStamp"]       
         logging.info("The latest timestamp {}".format(latest_timestamp))               
         state = StateManager(connection_string)         
         state.post(str(latest_timestamp).replace("Z", "-00:00"))
         body = json.dumps(results_events)
         if(len(results_events) <= 2000):            
            sentinel.post_data(body,len(results_events))
         elif(len(results_events) > 2000):   
            sentinel.gen_chunks(body)

        sentinel_class_vars = vars(sentinel)
        success_processed, fail_processed = sentinel_class_vars["success_processed"],\
                                            sentinel_class_vars["fail_processed"]
        logging.info('Total events processed successfully: {}, failed: {}. Period: {} - {}'
            .format(success_processed, fail_processed, startTime, endTime))
    except Exception as err:
      logging.error("Something wrong. Exception error text: {}".format(err))
      logging.error( "Error: LookOut Cloud Security events data connector execution failed with an internal server error.")
      raise
    
          
    
