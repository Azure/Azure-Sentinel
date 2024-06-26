import logging
import requests
import os
from base64 import b64encode
from .sentinel_connector import SentinelConnector
import azure.functions as func
import pandas as pd
import json

API_KEY = os.environ['API_KEY']
API_PASSWORD = os.environ['API_PASSWORD']
PCE_FQDN = os.environ['PCE_FQDN']
PORT = int(os.environ.get('PCE_PORT', 443))
ORG_ID = os.environ['ORG_ID']

AZURE_TENANT_ID = os.environ['AZURE_TENANT_ID']
AZURE_CLIENT_ID = os.environ['AZURE_CLIENT_ID']
AZURE_CLIENT_SECRET = os.environ['AZURE_CLIENT_SECRET']
DCE_ENDPOINT = os.environ['DCE_ENDPOINT']
DCR_ID = os.environ['DCR_ID']
LOG_ANALYTICS_URI = os.environ['LOG_ANALYTICS_URI']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
MAX_RESULTS = os.environ.get('MAX_WORKLOADS', 100000)

MAX_SCRIPT_EXEC_TIME_MINUTES = int(os.environ.get('MAX_SCRIPT_EXEC_TIME_MINUTES', 10))

URL = 'https://{}:{}/api/v2/orgs/{}/workloads/?max_results={}'.format(PCE_FQDN, PORT, ORG_ID, MAX_RESULTS)

credentials = b64encode(f"{API_KEY}:{API_PASSWORD}".encode()).decode('utf-8')
headers = {
    "Authorization": f"Basic {credentials}",
    "Content-type": "application/json"
}

STREAM_NAME = 'Custom-Illumio_Workloads_Summarized_API_CL'

def getVensByVersion(data):
    # add an exception handler
    # for ex, returns {'22.5.32-9876': 1, '23.3.0': 1}    
    return data[data['managed']==True].groupby('ven.version').size().to_dict()    
    
def getVensByManaged(data):
    return data.groupby('managed').size().to_dict()  

def getVensByType(data):
    return data[data['managed']==True].groupby('ven.ven_type').size().to_dict()

def getVensByOS(data):
    return data[data['managed']==True].groupby('os_id').size().to_dict()

def getVensByEnforcementMode(data):
    return data[data['managed']==True].groupby('enforcement_mode').size().to_dict()

def getVensByStatus(data):
    return data[data['managed']==True].groupby('ven.status').size().to_dict()

def getVensBySyncState(data):
    return data[data['managed']==True].groupby('agent.status.security_policy_sync_state').size().to_dict()


def main(mytimer: func.TimerRequest) -> None:
    logging.info("url to be exercised is {} ".format(URL))

    response = requests.request("GET", URL, headers=headers, data={})

    if response:
        logging.info("Response from url is {}".format(response.headers))
    else:
        logging.info("Error in response {}".format(response))
        return
        
    response = json.loads(response.text)
    df = pd.json_normalize(response)
    
    vens_by_version = getVensByVersion(df)
    vens_by_managed = getVensByManaged(df)
    vens_by_type = getVensByType(df)
    vens_by_os = getVensByOS(df)
    vens_by_enf_mode = getVensByEnforcementMode(df)
    vens_by_status = getVensByStatus(df)
    vens_by_sync_state = getVensBySyncState(df)
    api_response = []
    api_response.append({"vens_by_version": vens_by_version,
                         "vens_by_managed": vens_by_managed,
                         "vens_by_type": vens_by_type,
                         "vens_by_os": vens_by_os,
                         "vens_by_enforcement_mode": vens_by_enf_mode,
                         "vens_by_status": vens_by_status,                        
                         "vens_by_sync_state": vens_by_sync_state
                         })
    
    logging.info("Summary of workload api response that will be stored in log analytics table is {}".format(api_response))
    
    with requests.Session() as session:
        sentinel = SentinelConnector(session, DCE_ENDPOINT, DCR_ID, STREAM_NAME, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)    
        sentinel.send(api_response)
