/*  
    Title:          Azure Function App TEMPLATE - <PROVIDER NAME APPLIANCE NAME> API Ingestion to Azure Sentinel API 
    Language:       Python
    Version:        1.0
    Last Modified:  5/30/2020
    Comment:        Inital Release

    DESCRIPTION:    The following Python Function App code is a generic data connector to pull logs from your <PROVIDER NAME APPLIANCE NAME> API, transform the data logs into a Azure Sentinel acceptable format (JSON) and POST the logs to the 
                     Azure Sentinel workspace using the Azure Log Analytics Data Collector API. Use this generic template and replace with specific code needed to authenticate to the <PROVIDER NAME APPLIANCE NAME> API and format the data received into JSON format.
*/

# Modules to support run the script
import datetime
import logging
import json
import requests
import datetime
import hashlib
import hmac
import base64
import re
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)


# Define the application settings (environmental variables) for the Workspace ID, Workspace Key, <Data Source> API Key(s) or Token, URI, and/or Other variables. Reference:  https://docs.microsoft.com/azure/azure-functions/functions-reference-python 

# The following variables are required by the Log Analytics Data Collector API functions below. Reference: https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api
customer_id = os.environ['workspaceId'] 
shared_key = os.envviron['workspaceKey']
log_type = os.envviron['tableName']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + customerId + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")
    
/* Used this block to build the <PROVIDER NAME APPLIANCE NAME> REQUEST header needed to call the API. Refer to the <PROVIDER NAME APPLIANCE NAME> API Documentation.

For example:
apikey =  os.environ['api_id']
api_id = os.environ ['api_key']
url = os.environ['uri']


payload = {}
headers = {
  'x-auth-token': '"+ api_key +" " + / + " "+ api_id +"'
}
*/

/* Used this block to send a GET REQUEST to the <PROVIDER NAME APPLIANCE NAME> API. Refer to the <PROVIDER NAME APPLIANCE NAME> API Documentation.

For example:
response = requests.request("GET", url, headers=headers, data = payload)

json_data = response.text.encode('utf8')

*/

/* Used this block to transform the data recieved from the <PROVIDER NAME APPLIANCE NAME> API into JSON format, which is acceptable format for the Azure Log Analytics Data Collector API

For example:
body = json.dumps(json_data)

*/


# Required Function to build the Authorization signature for the Azure Log Analytics Data Collector API. References: https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api and https://docs.microsoft.com/azure/azure-functions/functions-reference-python#environment-variables

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash).encode('utf-8')  
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest())
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Required Function to create and invoke an API POST request to the Azure Log Analytics Data Collector API. Reference: https://docs.microsoft.com/azure/azure-functions/functions-reference-python#environment-variables

def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + "?api-version=2016-04-01"

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    try:
        response = requests.post(uri, data=body, headers=headers)
    except Exception as err:
        print("Error during sending logs to Azure Sentinel: {}".format(err))
    else:
        if (response.status_code >= 200 and response.status_code <= 299):
            print("logs have been successfully sent to Azure Sentinel.")
        else:
            print("Error during sending logs to Azure Sentinel. Response code: {}".format(response.status_code))

/* Use this block to post the JSON formated data into Azure Log Analytics via the Azure Log Analytics Data Collector API

For example:
if (len(response) > 0):
    post_data(customer_id, shared_key, body, log_type)
else:
    print "No records were found."
*/
