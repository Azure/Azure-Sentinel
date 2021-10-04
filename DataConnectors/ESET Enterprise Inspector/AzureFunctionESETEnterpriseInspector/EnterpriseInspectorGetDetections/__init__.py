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

import datetime
import logging
import json
import os

import azure.functions as func

from distutils.util import strtobool
from enterpriseinspector import EnterpriseInspector
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def main(eeitimer: func.TimerRequest, inputblob: func.InputStream, outputblob: func.Out[func.InputStream], outputqueue: func.Out[str]):

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if eeitimer.past_due:
        logging.info('The timer is past due!')

    # Set variables
    base_url = os.environ['baseUrl']
    username = os.environ['eeiUsername']
    password = os.environ['eeiPassword']
    domain = bool(strtobool(os.environ['domainLogin']))
    verify = bool(strtobool(os.environ['verifySsl']))
    start_from_id = int(os.environ['startFromID'])

    # Connect to ESET Enterprise Inspector server
    ei = EnterpriseInspector(
        base_url=base_url,
        username=username,
        password=password,
        domain=domain,
        verify=verify
    )

    # Get last processed detection id
    if inputblob:
        last_id = json.loads(inputblob.read())['id']
    else:
        last_id = start_from_id

    # Get new detections
    detections = ei.detections(last_id)

    # Get detection details and send to queue
    if detections:
        logging.info('Processing detections..')
        outputqueue.set(
            json.dumps(detections)
        )
 
        # Write last succesfully processed detetion to blob storage
        latest_detection = detections[-1]

        outputblob.set(
            json.dumps({
                'id': latest_detection['id']
            })
        )
                
        logging.info('Done processing detections.')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
