import json
import datetime
import logging
import requests
import hashlib
import hmac
import base64
import os
import re

import azure.functions as func


SEVERITY_LIST =  ("info", "low", "high", "medium", "critical")
TOKEN = os.environ['token']
CUSTOMER_ID = os.environ['workspaceId']
SHARED_KEY = os.environ['workspaceKey']
BASE_URL = os.environ['api_url']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + CUSTOMER_ID + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash).encode('utf-8')  
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest())
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization


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


def send_net_assets():
    for severity in SEVERITY_LIST:
        response =  requests.request(
            'GET',
            url=BASE_URL + f"/net-assets?severity={severity}&limit=600",
            headers={
                "Authorization": f"Token {TOKEN}", "Content-Type": "application/json"
            }
        )
                
        json_response = response.json()
        json_data = []
        for result in json_response.get("results"):
            ip = result.get("ip")
            json_data.append(
                {
                "ip": ip,
                "severity": severity,
                }
            )
        
        body = json.dumps(json_data)
        post_data(CUSTOMER_ID, SHARED_KEY, body, "net_assets")


def send_web_assets():
    for severity in SEVERITY_LIST:
        response =  requests.request(
            'GET',
            url=BASE_URL + f"/web-assets?severity={severity}&limit=600",
            headers={
                "Authorization": f"Token {TOKEN}", "Content-Type": "application/json"
            }
        )
                
        json_response = response.json()
        json_data = []
        for result in json_response.get("results"):
            uuid = result.get("uuid")
            json_data.append(
                {
                "uuid": uuid,
                "severity": severity,
                }
            )
        body = json.dumps(json_data)
        
        post_data(CUSTOMER_ID, SHARED_KEY, body, "web_assets")
            

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    send_net_assets()
    send_web_assets()

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
