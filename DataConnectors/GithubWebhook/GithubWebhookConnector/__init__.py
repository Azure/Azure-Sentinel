from dataclasses import replace
import datetime
from email.quoprimime import body_check
from xml.etree.ElementTree import tostring
import requests
import logging
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
import azure.functions as func
import re

sentinel_customer_id = os.environ.get('WorkspaceID')
#sentinel_shared_key = os.environ.get('WorkspaceKey')
sentinel_shared_key = "nocXTlJ8alnPLo8RIChmG/6Jl9lb4dJW3nccybPx3qgK64B+36XndmDoc0yMeE5"
sentinel_log_type =  os.environ.get('logtype') 
logging.info("Sentinel Logtype:{}".format(sentinel_log_type))
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
 logAnalyticsUri = 'https://' + str(sentinel_customer_id) + '.ods.opinsights.azure.com'

logging.info(logAnalyticsUri)
logging.info(sentinel_log_type)
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("GithubWebhook: Invalid Log Analytics Uri.")
    
def main(req: func.HttpRequest) -> func.HttpResponse:
     logging.info('Python HTTP trigger function processed a request.')    
     logging.info('Started function app trigger.')
     req_body = req.get_json()
     logging.info(req_body)
     print('printing body')
     print(req_body)
     print(sentinel_log_type)
     body = json.dumps(customizeJson(json.dumps(req_body)))
     logging.info("Converted input json to dict and to json")
     #body = json.dumps(req_body)
     logging.info(body)     
     print(body)
     post_data(sentinel_customer_id, sentinel_shared_key, body, sentinel_log_type)                 
     return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )   
#####################
######Functions######  
#####################

#Build new Json Object

def customizeJson(inputJson):
    required_fields_data = {}
    newJson_dict = json.loads(inputJson)
    for key, value in newJson_dict.items():
       required_fields_data[key] = str(value)
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
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': currentdate
    }

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
        logging.info('Accepted')  
    else:
        print("Response code: {}".format(response.status_code))
        logging.info("Response code: {}".format(response.status_code))  
