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
import time
from .state_manager import StateManager

zoom_account_id = os.environ['AccountID']
zoom_client_id = os.environ['ClientID']
zoom_client_secret = os.environ['ClientSecret']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
table_name = "Zoom"
chunksize = 10000
retry = 3 ## To do : need to move function app configuration
error=False
#Max script execution
SCRIPT_EXECUTION_INTERVAL_MINUTES = os.environ.get('EXECUTION_INTERVAL_MINUTES')
#Azure function max execution
AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES = os.environ.get('MAX_EXECUTION_TIME_MINUTES')

##Default values
Default_Values = {
  "SCRIPT_EXECUTION_INTERVAL_MINUTES": 30,
  "AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES": 29,
}
##Original Values
Orginal_Values={
    "SCRIPT_EXECUTION_INTERVAL_MINUTES":SCRIPT_EXECUTION_INTERVAL_MINUTES,
    "AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES":AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES
}

def is_number_regex(sn):
    """ Returns True if string is a number and False for other types. """
    if re.match("^\d+?\.\d+?$", sn) is None:  
         return sn.isdigit()
    else:
        return False

##This code checks for script execution time and azure func max interval mins for null,int,float and assign based on validations and need to validate the varables    
def validate_varable(Var_value,var):
    """ Returns True if string is a number and False for other data types. """   
    if ((Var_value in(None,'') or str(Var_value).isspace())):
        temp_var=Default_Values.get(var)   
        globals()[var]=int(temp_var)
                      
    else:
        logging.info("{}: {}".format(var,Var_value)) 
        if(is_number_regex(Var_value)):
          globals()[var]=int(Var_value)
        else:
          tempmsg="Please enter correct value for {}".format(var)
          raise Exception(tempmsg)
        
def paramter_validation():
    """ Validates the paramters for the inputs with default values by comparing with orginal values. """   
    for key,val in  Orginal_Values.items():
     validate_varable(val,key)       

##This method is used for parameter validation
paramter_validation()

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'


pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(logAnalyticsUri))
if (not match):
    raise Exception("Zoom: Invalid Log Analytics Uri.")


class Zoom:
    """This class has methods of zoom api report generation and oauth token generation
    """
    def __init__(self):
        """This is the method where declares all the self initiating varables

        Raises:
            Exception: Raises the exception when access token object is none
        """
        self.account_id = zoom_account_id
        self.client_id = zoom_client_id
        self.client_secret = zoom_client_secret
        self.retry = retry
        self.error_statuses = [429, 500, 502, 503, 504]
        self.base_url = "https://api.zoom.us/v2"
        self.token_url = "https://zoom.us/oauth/token?grant_type=account_credentials&account_id="+zoom_account_id
        self.oauth_token = self.generate_oauth_token()
        self.from_day, self.to_day = self.generate_date()
        if self.oauth_token is not None:
            self.headers = {
                'Accept': 'application/json',
                'authorization': "Bearer " + self.oauth_token,
            }
        else:
            raise Exception("Unable to generate access token")

    def generate_oauth_token(self):
        """This method used to generate the oauth zoom token

        Returns:
            _type_: the zoom oauth token
        """
        error=False
        for _ in range(self.retry):
            try:
                base64String = base64.b64encode(
                    f"{self.client_id}:{self.client_secret}".encode('utf-8')).decode("ascii")
                headersfortokens = {
                    'Accept': 'application/json',
                    'authorization': "Basic " + base64String,
                }
                query_params = {
                    "grant_type": "account_credentials",
                    "account_id": self.account_id,
                }
                oauth_token = requests.post(url=self.token_url,
                                            params=query_params,
                                            headers=headersfortokens)
                if (oauth_token.status_code in self.error_statuses) or (error==True):
                    error=False
                    continue ## To Do: Need to add delay 
                if oauth_token.status_code == 200:
                    jsonData = json.loads(oauth_token.text)
                    auth_token = jsonData['access_token']
                    return auth_token
                elif oauth_token.status_code == 400:
                    logging.error("The requested report cannot be generated for this account because"
                                  " this account has not subscribed to toll-free audio conference plan."
                                  " Error code: {}".format(oauth_token.status_code))
                elif oauth_token.status_code == 401:
                    logging.error("Invalid access token. Error code: {}".format(
                        oauth_token.status_code))
                elif oauth_token.status_code == 300:
                    logging.error("Only provide report in recent 6 months. Error code: {}".format(
                        oauth_token.status_code))

            except Exception  as err:
                error=True
                logging.error("Something wrong. Exception error text: {}".format(err))

    def generate_date(self):
        """This method is used to generate date and stores in file share state

        Returns:
            _type_: past time and current time
        """
        current_time_day = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        state = StateManager(connection_string)
        past_time = state.get()
        if past_time is not None:
            logging.info("The last time point is: {}".format(past_time))
        else:
            logging.info(
                "There is no last time point, trying to get events for last week.")
            past_time = (current_time_day -
                         datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        past_time_datetime = datetime.datetime.strptime(past_time, '%Y-%m-%d')
        no_days=(current_time_day-past_time_datetime)
        if(no_days.days>7):
           current_time_day= (past_time_datetime +datetime.timedelta(days=7))
        logging.info("The current time point is: {}".format(current_time_day))     
        state.post(current_time_day.strftime("%Y-%m-%d"))
        return (past_time, current_time_day.strftime("%Y-%m-%d"))

    def get_report(self, report_type_suffix, next_page_token=None):
        """This is method is used to get report from zoom api

        Args:
            report_type_suffix (_type_): zoom report types
            next_page_token (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: response from zoom report
        """        
        query_params = {
                "page_size": 300,
                "from": self.from_day,
                "to": self.to_day
        }
        if next_page_token:
            query_params.update({"next_page_token": next_page_token}) 

        error=False    
        for _ in range(self.retry):
            try:
                
                r = requests.get(url=self.base_url + report_type_suffix,
                             params=query_params,
                             headers=self.headers)
                if (r.status_code in self.error_statuses) or (error==True):
                    error=False
                    continue ## To Do: Need to add delay 
                if r.status_code == 200:
                    return r.json()
                elif r.status_code == 400:
                    logging.error("The requested report cannot be generated for this account because"
                              " this account has not subscribed to toll-free audio conference plan."
                              " Error code: {}".format(r.status_code))
                elif r.status_code == 401:
                    logging.error(
                    "Invalid access token. Error code: {}".format(r.status_code))
                elif r.status_code == 300:
                    logging.error("Only provide report in recent 6 months. Error code: {}".format(
                    r.status_code))
                else:
                    logging.error(
                    "Something wrong. Error code: {}".format(r.status_code))
            except Exception  as err:
                error=True
                logging.error("Something wrong. Exception error text: {}".format(err))


class Sentinel:
    """This class have mentods to initate data,post data to log analytics
    """
    def __init__(self):
        """This is used to initiate the varaibles
        """        
        self.logAnalyticsUri = logAnalyticsUri
        self.success_processed = 0
        self.fail_processed = 0
        self.table_name = table_name
        self.chunksize = chunksize

    def gen_chunks_to_object(self, data, chunksize=100):
        """This is used to generate chunks to object based on chunk size

        Args:
            data (_type_): data from zoom reports api
            chunksize (int, optional): _description_. Defaults to 100.

        Yields:
            _type_: the chunk
        """        
        chunk = []
        for index, line in enumerate(data):
            if (index % chunksize == 0 and index > 0):
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

    def gen_chunks(self, data):
        """This method is used to get the chunks and post the data to log analytics work space

        Args:
            data (_type_): _description_
        """        
        for chunk in self.gen_chunks_to_object(data, chunksize=self.chunksize):
            obj_array = []
            for row in chunk:
                if row != None and row != '':
                    obj_array.append(row)
            body = json.dumps(obj_array)
            self.post_data(body, len(obj_array))

    def build_signature(self, date, content_length, method, content_type, resource):
        """This method is used to build signature for log analytics work space

        Args:
            date (_type_): RFC format date
            content_length (_type_): length of the data from zoom api
            method (_type_): This is post call
            content_type (_type_): application/json
            resource (_type_): api/logs

        Returns:
            _type_: authorized signature for log analytics work space
        """        
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + \
            str(content_length) + "\n" + content_type + \
            "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self, body, chunk_count):
        """This method is used to post the data to log analytics work space

        Args:
            body (_type_): content from zoom report api as chunks
            chunk_count (_type_): chunk count
        """        
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
            logging.info("Chunk was processed({} events)".format(chunk_count))
            self.success_processed = self.success_processed + chunk_count
        else:
            logging.error("Error during sending events to Microsoft Sentinel. Response code:{}".format(
                response.status_code))
            self.fail_processed = self.fail_processed + chunk_count


def results_array_join(result_element, api_req_id, api_req_name):
    """This method is used to join all the results from zoom api

    Args:
        result_element (_type_): This will have result element
        api_req_id (_type_): zoom api req id
        api_req_name (_type_): zoom api req name
    """    
    for element in result_element[api_req_id]:
        element['event_type'] = api_req_id
        element['event_name'] = api_req_name
        results_array.append(element)

def check_if_functiontime_is_over(start_time, interval_minutes, max_script_exec_time_minutes):
    """Returns True if function's execution time is less than interval between function executions and
    less than max azure func lifetime. In other case returns False."""

    logging.info("started Max function time check")
    logging.info("interval_minutes({} time)".format(interval_minutes))
    logging.info("max_script_exec_time_minutes({} time)".format(max_script_exec_time_minutes))
    min_minutes = min(interval_minutes, max_script_exec_time_minutes)
    if min_minutes > 1:
        max_time = min_minutes * 60 - 30
    else:
        raise Exception("Script execution mins is less than 1 min")
    logging.info("max time({} time)".format(max_time))
    script_execution_time = time.time() - start_time
    logging.info("script execution time({} time)".format(script_execution_time))
    if script_execution_time > max_time:
        return True
    else:
        return False
    
def get_main_info(start_time):
    """This is the main method to get response from zoom reports api
    """    
    for api_req_id, api_req_info in reports_api_requests_dict.items():
        api_req = api_req_info['api_req']
        api_req_name = api_req_info['name']
        logging.info("Getting report: {}".format(api_req_info['name']))
        result = zoom.get_report(report_type_suffix=api_req)
        if result is not None:
            next_page_token = result.get('next_page_token')
            results_array_join(result, api_req_id, api_req_name)
        else:
            next_page_token = None
        while next_page_token:
            result = zoom.get_report(
                report_type_suffix=api_req, next_page_token=next_page_token)
            if result is not None:
                next_page_token = result.get('next_page_token')
                results_array_join(result, api_req_id, api_req_name)
            else:
                next_page_token = None
        if check_if_functiontime_is_over(start_time, SCRIPT_EXECUTION_INTERVAL_MINUTES, AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES):
            logging.info('Stopping script because time for execution is over')
            break    


def main(mytimer: func.TimerRequest) -> None:
    """This is the main method for starting the zoom functionality

    Args:
        mytimer (func.TimerRequest): Timer based function app
    """    
    start_time = time.time()
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    logging.info('Starting program')
    global results_array, reports_api_requests_dict, zoom
    reports_api_requests_dict = \
        {
            "dates": {"api_req": "/report/daily", "name": "Daily Usage Reports."},
            "users": {"api_req": "/report/users", "name": "Active/Inactive Host Reports."},
            "telephony_usage": {"api_req": "/report/telephone", "name": "Telephone Reports."},
            "cloud_recording_storage": {"api_req": "/report/cloud_recording", "name": "Cloud Recording Usage Reports."},
            "operation_logs": {"api_req": "/report/operationlogs", "name": "Operation Logs Report."},
            "activity_logs": {"api_req": "/report/activities", "name": "Sign In/Sign Out Activity Report."}
        }
    results_array = []
    zoom = Zoom()
    sentinel = Sentinel()
    zoom_class_vars = vars(zoom)
    from_day, to_day = zoom_class_vars['from_day'], zoom_class_vars['to_day']
    logging.info(
        'Trying to get events for period: {} - {}'.format(from_day, to_day))
    get_main_info(start_time)
    sentinel.gen_chunks(results_array)
    sentinel_class_vars = vars(sentinel)
    success_processed, fail_processed = sentinel_class_vars["success_processed"],\
        sentinel_class_vars["fail_processed"]
    logging.info('Total events processed successfully: {}, failed: {}. Period: {} - {}'
                 .format(success_processed, fail_processed, from_day, to_day))
