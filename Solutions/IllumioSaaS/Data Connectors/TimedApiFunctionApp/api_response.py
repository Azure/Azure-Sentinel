import logging
import requests
from base64 import b64encode
from .sentinel_connector import SentinelConnector
import azure.functions as func
import pandas as pd
import json
from .. import constants
from ..sentinel_connector import AzureSentinelConnectorAsync

API_KEY = constants.API_KEY
API_SECRET = constants.API_SECRET
PCE_FQDN = constants.PCE_FQDN
PORT = constants.PORT
ORG_ID = constants.ORG_ID

AZURE_TENANT_ID = constants.AZURE_TENANT_ID
AZURE_CLIENT_ID = constants.AZURE_CLIENT_ID
AZURE_CLIENT_SECRET = constants.AZURE_CLIENT_SECRET
DCE_ENDPOINT = constants.DCE_ENDPOINT
DCR_ID = constants.DCR_ID
LOG_ANALYTICS_URI = constants.LOG_ANALYTICS_URI
WORKLOADS_API_LOGS_CUSTOM_TABLE = constants.WORKLOADS_API_LOGS_CUSTOM_TABLE
WORKSPACE_ID = constants.WORKSPACE_ID
MAX_WORKLOADS = constants.MAX_WORKLOADS

URL = 'https://{}:{}/api/v2/orgs/{}/workloads/?max_results={}'.format(PCE_FQDN, PORT, ORG_ID, MAX_WORKLOADS)

credentials = b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode('utf-8')
headers = {
    "Authorization": f"Basic {credentials}",
    "Content-type": "application/json"
}

def getVensByVersion(data):
    try:
        return data[data['managed'] == True].groupby('ven.version').size().to_dict()
    except Exception as e:
        # You can log the exception here if needed
        logging.error("getVensByVersion error: {e}")
        return {}  
    
def getVensByManaged(data):
    try:    
        return data.groupby('managed').size().to_dict()  
    except Exception as e:
        logging.error("getVensByManaged error: {e}")
        return {}          

def getVensByType(data):
    try:        
        return data[data['managed']==True].groupby('ven.ven_type').size().to_dict()
    except Exception as e:
        logging.error("getVensByType error: {e}")
        return {}                  

def getVensByOS(data):
    try:        
        return data[data['managed']==True].groupby('os_id').size().to_dict()
    except Exception as e:
        logging.error("getVensByOS error: {e}")
        return {}                          

def getVensByEnforcementMode(data):
    try:
        return data[data['managed']==True].groupby('enforcement_mode').size().to_dict()
    except Exception as e:
        logging.error("getVensByEnforcementMode error: {e}")
        return {}                                  

def getVensByStatus(data):
    try:    
        return data[data['managed']==True].groupby('ven.status').size().to_dict()
    except Exception as e:
        logging.error("getVensByStatus error: {e}")
        return {}                                          

def getVensBySyncState(data):
    try:    
        return data[data['managed']==True].groupby('agent.status.security_policy_sync_state').size().to_dict()
    except Exception as e:
        logging.error("getVensBySyncState error: {e}")
        return {}                                                  

def main(mytimer: func.TimerRequest) -> None:
    logging.debug("url to be exercised is {} ".format(URL))

    response = requests.request("GET", URL, headers=headers, data={})

    if response:
        logging.info("[TimedApi] Response from url is {}".format(response.headers))
    else:
        logging.info("[TimedApi] Error in response {}".format(response))
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
                         "vens_by_sync_state": vens_by_sync_state,
                         "pce_fqdn": PCE_FQDN
                         })
    
    logging.info("[TimedApi] Summary of workload api response that will be stored in log analytics table is {}".format(api_response))
    
    with requests.Session() as session:
        sentinel = AzureSentinelConnectorAsync(session, DCE_ENDPOINT, DCR_ID, WORKLOADS_API_LOGS_CUSTOM_TABLE, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, queue_size=1)    
        sentinel.send(api_response)
