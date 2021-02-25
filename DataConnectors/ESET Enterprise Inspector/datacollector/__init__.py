# Taken from https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api

import json
import requests
import datetime
import hashlib
import hmac
import base64
import os
import re

from enterpriseinspector.eifunctions import exit_error
logAnalyticsUri = os.environ['logAnalyticsUri']

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

    if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
        logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

    pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
    match = re.match(pattern,str(logAnalyticsUri))
    
    if(not match):
        raise Exception("ESET Enterprise Inspector: Invalid Log Analytics Uri.")
    
    logAnalyticsUri = logAnalyticsUri + resource + '?api-version=2016-04-01'
    
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(logAnalyticsUri,data=body, headers=headers)

    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
    else:
        exit_error(f'Response code "{response.status_code}" while sending data through data-collector API.')
