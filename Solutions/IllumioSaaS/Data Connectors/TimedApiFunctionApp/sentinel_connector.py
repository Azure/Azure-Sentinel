from collections import deque
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError
import logging

class SentinelConnector:
    def __init__(self, session, dce_endpoint, dcr_id, stream_name, azure_client_id, azure_client_secret, azure_tenant):
        self.dce_endpoint = dce_endpoint
        self.dcr_id = dcr_id
        self.stream_name = stream_name        
        self._queue = deque()
        self.successful_sent_events_number = 0
        self.failed_sent_events_number = 0        
        self.session = session
        self.credential = DefaultAzureCredential()
        self.AZURE_CLIENT_ID = azure_client_id
        self.AZURE_CLIENT_SECRET = azure_client_secret
        self.AZURE_TENANT_ID = azure_tenant
        self.access_token_uri = "https://login.microsoftonline.com/{}/oauth2/token".format(self.AZURE_TENANT_ID)
        self.DCR_DATA_INGESTION_URL = "{}/dataCollectionRules/{}/streams/{}?api-version=2021-11-01-preview"
    

    # This method collects data coming in based on size of the queue
    # event : dictionary
    def send(self, event):                 
        if event:
            self._flush(event)

    # This method is a helper function which sends data to ingestion endpoint
    # list : List of dictionary
    def _flush(self, data: list):
        if data:
            self._post_data(self.dce_endpoint, self.dcr_id, self.stream_name, self.credential, data)

    # This method is a helper function which posts data to ingestion endpoint
    def _post_data(self, dce_endpoint, dcr_id, stream_name, credential, data):
        client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential, logging_enable=True)        
        try:
            client.upload(rule_id=dcr_id, stream_name=stream_name, logs=data)
        except HttpResponseError as e:
            logging.error(f"Upload failed: {e}")    
