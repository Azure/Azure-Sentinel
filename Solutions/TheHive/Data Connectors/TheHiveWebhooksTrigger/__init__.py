import logging
import hashlib
import hmac
import os
import azure.functions as func
import json
import re
import base64
import requests
import datetime

TheHiveBearerToken = os.environ['TheHiveBearerToken']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
log_type = 'TheHive'

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("TheHive Data Connector: Invalid Log Analytics Uri.")

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

def post_data_to_sentinel(body):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info("TheHive event successfully processed to the Azure Sentinel.")
        return response.status_code
    else:
        logging.warn("Event is not processed into Azure. Response code: {}".format(response.status_code))
        return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request. Start of processing.')
    method = req.method
    params = req.params
    if method == 'POST':
        if 'Authorization' in req.headers:
            bearer_string = re.match("^Bearer\s+(.*)", req.headers['Authorization'])
            if bearer_string:
                bearer_token = bearer_string.group(1)
                if bearer_token == TheHiveBearerToken:
                    post_req_data = req.get_body()
                    message = post_req_data.decode('utf-8')
                    logging.info("200 OK HTTPS")
                    try:
                        message = json.loads(message)
                        post_data_to_sentinel(json.dumps(message))
                    except Exception as err:
                        logging.error(f"Is not valid Message format. Error: {err}. Message: {message}.")
                    return func.HttpResponse("200 OK HTTPS", status_code=200)
                else:
                    logging.error("Unauthorized, Bearer token is not right. Error code: 401.")
                    return func.HttpResponse("Unauthorized, Bearer token is not right.", status_code=401)
            else:
                logging.error("Unauthorized, Bearer token is not present in the request. Error code: 401.")
                return func.HttpResponse("Unauthorized, Bearer token is not present in the request.", status_code=401)
        else:
            logging.error("Unauthorized, Bearer token is not right. Error code: 401.")
            return func.HttpResponse("Unauthorized, Bearer token is not present in the request.", status_code=401)
    logging.error("HTTP method not supported. Error code: 405.")
    return func.HttpResponse("HTTP method not supported", status_code=405)