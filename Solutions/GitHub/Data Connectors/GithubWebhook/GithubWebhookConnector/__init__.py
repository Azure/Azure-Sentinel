import datetime
import requests
import logging
import os
import json
import hashlib
import hmac
import base64
import azure.functions as func
import re

sentinel_customer_id = os.environ.get('WorkspaceID')
sentinel_shared_key = os.environ.get('WorkspaceKey')
github_webhook_secret = os.environ.get('GithubWebhookSecret')
sentinel_log_type =  'githubscanaudit'
logging.info("Sentinel Logtype:{}".format(sentinel_log_type))
logAnalyticsUri = os.environ.get('LogAnaltyicsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
 logAnalyticsUri = 'https://' + str(sentinel_customer_id) + '.ods.opinsights.azure.com'

logging.info(logAnalyticsUri)
logging.info(sentinel_log_type)
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("GithubWebhook: Invalid Log Analytics Uri.")

# this function app is fired based on the http trigger
# it is used to capture all the events from github   
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
     logging.info('Info:Current retry count:{}'.format(context.retry_context.retry_count))   
     logging.info('Info:Github webhook data connector started')  
     logging.info("Sentinel Logtype:{}".format(sentinel_log_type))  

     # check webhook signature if GitHubWebhookSecret exists
     if ((github_webhook_secret not in (None, '') and not str(github_webhook_secret).isspace())):    
        hash_object = hmac.new(github_webhook_secret.encode('utf-8'), msg=req.get_body(), digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()
        if 'x-hub-signature-256' not in req.headers:
            return func.HttpResponse(
             "Github webhook signature header is missing.",
             status_code=403
        )
        signature_header = req.headers['x-hub-signature-256']
        if not hmac.compare_digest(expected_signature, signature_header):
            return func.HttpResponse(
             "Github webhook signature verification failed.",
             status_code=403
        )

     req_body = req.get_json()
     body = json.dumps(customizeJson(json.dumps(req_body)))
     logging.info("Info:Converted input json to dict and further to json")
     logging.info(body)     
     
     try:
        post_data(sentinel_customer_id, sentinel_shared_key, body, sentinel_log_type)
        logging.info("Info: Github webhook data connector execution completed successfully.")
        return func.HttpResponse(
             "Github webhook data connector execution completed successfully.",
             status_code=200
        )      
     except Exception as err:
      logging.error("Something wrong. Exception error text: {}".format(err))
      logging.error( "Error: Github webhook data connector execution failed with an internal server error.")
      raise
           
            
#####################
######Functions######  
#####################

#Build new Json Object

def customizeJson(inputJson):
    required_fields_data = {}    
    newJson_dict = json.loads(inputJson)    
    for key, value in newJson_dict.items():
        if(type(value) == type({})):
         required_fields_data[key] = json.dumps(value, indent=4)
        else:
         required_fields_data[key] = value
    return required_fields_data  
     
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
    currentdate = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, currentdate, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'
    
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': currentdate
    }

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Info:Event was injected into Github')
        logging.info('Info:Event was injected into Github') 
    elif (response.status_code == 401):
        logging.error("The authentication credentials are incorrect or missing. Error code: {}".format(response.status_code))
    else:
        print("Response code: {}".format(response.status_code))
        logging.info("Info:Response code: {}".format(response.status_code))  
