# Tiite: Trend Micro XDR Data Connector
# Language: Python 3.8
# Author: Trend Micro 
# Last Modified: 11/11/2020
# Comment: Intial Release

import datetime
import logging
import requests
import base64
import json
import datetime
import hmac
import hashlib
import sys
import os
import re
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    logging.info("Starting Program")
    run = function()
    logging.info(run)   
    logging.info('Program ran at %s', utc_timestamp)

#Global Variables

region = {'us': 'https://api.xdr.trendmicro.com', 'eu': 'https://api.eu.xdr.trendmicro.com', 'in': 'https://api.in.xdr.trendmicro.com',
          'jp': 'https://api.xdr.trendmicro.co.jp', 'sg': 'https://api.sg.xdr.trendmicro.com', 'au': 'https://api.au.xdr.trendmicro.com'}

customer_id = os.environ['workspaceId'] 
shared_key = os.environ['workspaceKey']
api_id = os.environ ['api_key']
regioncode = os.environ ['regioncode']
url_base = region[regioncode]
log_type = 'TrendMicro_XDR'
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Trend Micro: Invalid Log Analytics Uri.")

#Get List of Events
def getWorkbenchList():
    query_params = 'source=all&investigationStatus=null&sortBy=createdTime&queryTimeField=createdTime&offset=0&limit=100'
    headers = {'Authorization': 'Bearer ' + api_id, 'Content-Type': 'application/json;charset=utf-8'}
    url = url_base + '/v2.0/siem/events' + '?' + query_params
    response = requests.get(url, headers=headers)
    workbench_list = response.json()
    #Checks if API Call got error for API key
    if "error" in workbench_list:
        workbench_list = 'Invalid API Key'
    return workbench_list

# Get each Workbench Data from API and return Json Data
def getWorkbench(workbenchIds):
    url_path = '/v2.0/xdr/workbench/workbenches/'+workbenchIds
    url = url_base+url_path
    headers = {'Authorization': 'Bearer ' + api_id, 'Content-Type': 'application/json;charset=utf-8'}
    response_event = requests.get(url, headers=headers)
    workbench_details = response_event.json()
    workbench_details_json = workbench_details['data']
    return workbench_details_json

# Customizes the Json Arrays to make it easier to parse in Azure Sentinel 
def customize_json(json_data):
    for impact_scope in json_data['impactScope']:
        entity_type = impact_scope['entityType']
        if entity_type == 'host':
            scope_value = impact_scope['entityValue']['ips'][0]
            hostname = impact_scope['entityValue']['name']
            host_guid = impact_scope['entityValue']['guid']
        else: scope_value = impact_scope['entityValue']


        simple_str_field = 'impactScope_' + entity_type
        if simple_str_field not in json_data:  # use first element only
            json_data[simple_str_field] = scope_value
        if entity_type == 'host':
            json_data['impactScope_hostname'] = hostname
            json_data['impactScope_hostGuid'] = host_guid

        comma_seperated_field = 'impactScope_' + entity_type + 's'
        if comma_seperated_field not in json_data:
            json_data[comma_seperated_field] = scope_value
        else:
            json_data[comma_seperated_field] = "{}, {}".format(json_data[comma_seperated_field], scope_value)

    return json_data

# Azure Provided Code for posting data to Azure Log Ingestion
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding='utf-8') 
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Required Function to create and invoke an API POST request to the Azure Log Analytics Data Collector API. Reference: https://docs.microsoft.com/azure/azure-functions/functions-reference-python#environment-variables

def post_data(customer_id, shared_key, body, log_type, workbencheIds):
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

    response = requests.post(uri, data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print ('Accepted ' + workbencheIds)
    #Uncomment for easy troublshooting of log posting to Sentinel 
        #print (body)
    else:
        print (response)


# Main Code: If inital list events contains new workbenchs, loop through all new workbenchs and pull data and forward to Sentinal API
def function():
    workbench_list = getWorkbenchList()
    a = 0
    if workbench_list == "Invalid API Key":
        status = "Invalid API Key"
    else:
        if "totalCount" in workbench_list['data']:
            print("Key exist in JSON data")
        workbenchcount = workbench_list['data']['totalCount']
        status = ("New WorkBench Alerts:"+ str(workbenchcount))
        
        while a < workbenchcount:
         workbenchIds = workbench_list['data']['workbenchRecords'][a]['workbenchId']
         print ("Retrieved Workbench:"+workbenchIds)
         workbench_details = getWorkbench(workbenchIds)
         customized_workbench_json = customize_json(workbench_details)
         body = json.dumps(customized_workbench_json, sort_keys=True)
        
         #Uncomment out the below line for troubleshooting easier 
         #print (body)
         post_data(customer_id, shared_key, body, log_type, workbenchIds)
         a += 1
    return status
  

