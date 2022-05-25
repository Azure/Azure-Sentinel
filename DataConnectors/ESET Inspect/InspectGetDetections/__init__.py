# Title:          ESET Inspect Data Connector
# Language:       Python
# Version:        1.1
# Author(s):      ESET Netherlands - Donny Maasland, Katelyn Overbeeke
# Last Modified:  05/25/2021
# Comment:        Update stability, add ESET Inspect Cloud support
#
# DESCRIPTION
# This Function App calls the ESET Inspect API (https://help.eset.com/ei_navigate/latest/en-US/api.html)
# and gathers all new detections that have been triggered.
#
# The response from the ESET Inspect API is recieved in JSON format. This function will build
# the signature and authorization header needed to post the data to the Log Analytics workspace via
# the HTTP Data Connector API. The Function App will will post all detections to the ESETInspect_CL
# table in Log Analytivs.

import datetime
import json
import logging
import os
import re
from distutils.util import strtobool

import azure.functions as func
from datacollector import post_data
from esetinspect import Inspect

# Hack to keep the EI object cached (preventing multiple logins).
# See: https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/azure-functions/functions-reference-python.md#global-variables
ei = None


def main(
    eitimer: func.TimerRequest,
    inputblob: func.InputStream,
    outputblob: func.Out[str],
) -> None:

    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if eitimer.past_due:
        logging.info("The timer is past due!")

    # Set variables
    global ei
    log_type = "ESETInspect"
    base_url = os.environ["baseUrl"]
    username = os.environ["eiUsername"]
    password = os.environ["eiPassword"]
    domain = bool(strtobool(os.environ["domainLogin"]))
    verify = bool(strtobool(os.environ["verifySsl"]))
    start_from_id = int(os.environ["startFromID"])
    workspace_id = os.environ["workspaceId"]
    workspace_key = os.environ["workspaceKey"]

    # Optionals
    client_id = os.environ.get("clientId")
    logAnalyticsUri = os.environ.get("logAnalyticsUri")

    # Set client id
    if client_id == "" or str(client_id).isspace():
        client_id = None

    # Get log analytics URI
    if logAnalyticsUri in (None, "") or str(logAnalyticsUri).isspace():
        logAnalyticsUri = f"https://{workspace_id}.ods.opinsights.azure.com"

    pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"

    if not re.match(pattern, str(logAnalyticsUri)):
        raise Exception("ESET Inspect: Invalid Log Analytics Uri.")

    # Connect to ESET Inspect server
    if ei is None:
        ei = Inspect.getinstance(
            base_url=base_url,
            username=username,
            password=password,
            domain=domain,
            client_id=client_id,
            verify=verify,
        )

    # Get last processed detection id
    last_id = start_from_id
    if inputblob:
        last_id = json.loads(inputblob.read())["id"]

    # Get new detections
    detections = ei.detections(last_id)

    # Get detection details and send to queue
    if detections:
        logging.info("Processing detections..")

        for detection in detections:
            logging.info(f"ID: {detection['id']}")
            detection_details = ei.detection_details(detection)
            body = json.dumps(detection_details)
            post_data(
                customer_id=workspace_id,
                shared_key=workspace_key,
                body=body,
                log_type=log_type,
                logAnalyticsUri=str(
                    logAnalyticsUri,
                ),
            )

            # Write last succesfully processed detetion to blob storage
            latest_detection = detection
            outputblob.set(json.dumps({"id": latest_detection["id"]}))

        logging.info("Done processing detections.")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
