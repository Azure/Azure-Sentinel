import requests
import json
import datetime
import azure.functions as func
import base64
import hmac
import hashlib
import os
import logging
import re
import threading
from .mes_request import MESRequest

#Azure WorkSpace credentials, if not saved by an Keyerror Exception has been raised
customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']

#Azure Secret client setting
keyVaultName = str(os.environ['KeyVaultName'])
KVUri = "https://" + keyVaultName + ".vault.azure.net/"

#RISK MES API credentials
lookout_mes_uri = "https://api.lookout.com"
ent_name = os.environ.get('EnterpriseName')
api_key = os.environ.get('ApiKey')

log_type = 'Lookout'
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    '''
    Build API Signature required to send events to Sentinel
    - Returns auth signature
    '''
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization


def post_data(body):
    '''
    Method to send data to sentinel via POST HTTP Request
    '''
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
        return response.status_code
    else:
        logging.warn("Events are not processed into Azure. Response code: {}".format(response.status_code))
        return None

def single_ent_events(KVUri= None, ent_name= None, api_key= None, lookout_mes_uri= None, ent_index= 0):
    '''
    Fetching events for an ENT and syncing fetched events into sentinel
    '''
    logging.info("Events fetching for ent_name %s..." % str(ent_name))
    mes = MESRequest(lookout_mes_uri, ent_name, api_key, KVUri, ent_index)
    
    events = mes.get_events()
    if events and len(events) > 0:
        logging.info("Got events")        
        logging.info("Processing {} events".format(len(events)))
        post_status_code = post_data(json.dumps(events))
        if post_status_code is not None:
            logging.info("Events processed to Sentinel successfully")
        else:
            logging.info("Failed to Post Events to Sentinel")
            
def main(mytimer: func.TimerRequest)  -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    logging.info("Application starting")

    #Check for MES credentials and fetch events using RISK API
    if api_key and ent_name:
        logging.info("Fetching RISK API Events")
        # For now we are passing hardcoded ent index to 0 
        #threading mechanism is not supported in Azure function
        
        single_ent_events(KVUri, ent_name, api_key, lookout_mes_uri, 0)
    else:
        logging.info("No API key or Enterprise name found in Key Vault")