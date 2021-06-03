# Title:          ESET Enterprise Inspector Data Connector
# Language:       Python
# Version:        1.0
# Author(s):      ESET Netherlands - Donny Maasland
# Last Modified:  11/25/2020
# Comment:        Initial release
#
# DESCRIPTION
# This Function App calls the ESET Enterprise Inspector API (https://help.eset.com/eei/1.5/en-US/api.html)
# and gathers all new detections that have been triggered.
#
# The response from the ESET Enterprise Inspector API is recieved in JSON format. This function will build
# the signature and authorization header needed to post the data to the Log Analytics workspace via 
# the HTTP Data Connector API. The Function App will will post all detections to the ESETEnterpriseInspector_CL
# table in Log Analytivs.

import logging
import json
import os

import azure.functions as func

from datacollector import post_data
from distutils.util import strtobool
from enterpriseinspector import EnterpriseInspector


def main(eeimsg: func.QueueMessage) -> None:

    detection = json.loads(eeimsg.get_body().decode('utf-8'))
    logging.info(f"Queue trigger function processed item: {detection['id']}")

    # Set variables
    base_url = os.environ['baseUrl']
    username = os.environ['eeiUsername']
    password = os.environ['eeiPassword']
    domain = bool(strtobool(os.environ['domainLogin']))
    verify = bool(strtobool(os.environ['verifySsl']))
    workspace_id = os.environ['workspaceId']
    workspace_key = os.environ['workspaceKey']
    logAnalyticsUri = os.environ.get('logAnalyticsUri')
    log_type = 'ESETEnterpriseInspector'

    if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
        logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

    pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
    match = re.match(pattern,str(logAnalyticsUri))
    
    if(not match):
        raise Exception("ESET Enterprise Inspector: Invalid Log Analytics Uri.")

    # Connect to ESET Enterprise Inspector server
    ei = EnterpriseInspector(
        base_url=base_url,
        username=username,
        password=password,
        domain=domain,
        verify=verify
    )

    # Get detection details
    detection_details = ei.detection_details(detection)

    # Send data via data collector API
    body = json.dumps(detection_details)
    post_data(
        customer_id=workspace_id,
        shared_key=workspace_key,
        body=body,
        log_type=log_type,
        logAnalyticsUri = logAnalyticsUri
    )
