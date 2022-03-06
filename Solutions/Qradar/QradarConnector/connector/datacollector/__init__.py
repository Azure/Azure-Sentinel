import datetime
import logging
import json
from types import resolve_bases
import requests
import datetime
import hashlib
import hmac
import base64
import os

import azure.functions as func


# QRADAR info (management ip and authentication token)
qradar_host = os.environ["consoleIP"]
qrtoken = os.environ["token"]
# Sentinel info (tenant, workspace id and workspace key)
customer_id = os.environ["customerID"] 
shared_key = os.environ["sharedKey"] 


# For the shared key, use either the primary or the secondary Connected Sources client authentication key   


# The log type is the name of the event that is being submitted
log_type = 'QRadarOffense'

# The SPN credentials for querying Azure Log Analytics 
get_offenese_ids_query = "{0}_CL | project id_d".format(log_type)
tenant = os.environ["tenant"]
sp_id = os.environ["sp_id"]
sp_secret = os.environ["sp_secret"]
# An example JSON web monitor object


#####################
######Functions######  
#####################

# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

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

def get_offenses():
    headers = {'Content-Type':'application/json', 'Version':'12.0', 'SEC':qrtoken}
    time_filter = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())
    print(time_filter)
    url = "https://" + qradar_host + "/api/siem/offenses?filter=start_time%3E" + str(time_filter) 
    response = requests.get(url, headers = headers, verify=False) 
    offense_list = (response.json())
    return(offense_list)

def get_log_analytics_token(tenant, sp_id, sp_secret):
    """Obtain authentication token using a Service Principal"""
    login_url = "https://login.microsoftonline.com/"+tenant+"/oauth2/token"
    resource = "https://api.loganalytics.io"

    payload = {
        'grant_type': 'client_credentials',
        'client_id': sp_id,
        'client_secret': sp_secret,
        'Content-Type': 'x-www-form-urlencoded',
        'resource': resource
    }
    try:
        response = requests.post(login_url, data=payload, verify=False)
        
    except Exception as error:
        logging.error(error)
    
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info('Token obtained')
        token = json.loads(response.content)["access_token"]
        return {"Authorization": str("Bearer "+ token), 'Content-Type': 'application/json'}
    else:
        logging.error("Unable to Read: " + format(response.status_code))

def get_log_analytics_data(query, token, azure_log_customer_id):
    """Executes a KQL on a Azure Log Analytics Workspace
    
    Keyword arguments:
    query -- Kusto query to execute on Azure Log Analytics
    token -- Authentication token generated using get_token
    azure_log_customer_id -- Workspace ID obtained from Advanced Settings
    """
    
    az_url = "https://api.loganalytics.io/v1/workspaces/"+ azure_log_customer_id + "/query"
    query = {"query": query}

    try:
        response = requests.get(az_url, params=query, headers=token)
    except Exception as error:
        logging.error(error)
    
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info('Query ran successfully')
        return json.loads(response.content)
    else:
        logging.error("Unable to Read: " + format(response.status_code))

def check_existed_offenses(offenses_list, log_analytics_data):
    existed_offenses = []
    result = []
    for id in log_analytics_data['tables'][0]['rows']:
        existed_offenses.append(id[0])
    print(existed_offenses)
    for offense in offenses_list:
        if offense['id'] not in existed_offenses:
            print(offense['id'])
            result.append(offense)
    return result
    
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    offenses_list = (get_offenses())
    #print(offenses)
    log_analytics_token = get_log_analytics_token(tenant, sp_id=sp_id, sp_secret=sp_secret) 
    
    try:
        log_analytics_data = get_log_analytics_data(query=get_offenese_ids_query,token=log_analytics_token, azure_log_customer_id=customer_id)
        print(log_analytics_data)
        final_offenses = check_existed_offenses(offenses_list, log_analytics_data)
        body = json.dumps(final_offenses)
    except:
        body = json.dumps(offenses_list)
        pass
    
    print("BODY", body)
    post_data(customer_id, shared_key, body, log_type)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
