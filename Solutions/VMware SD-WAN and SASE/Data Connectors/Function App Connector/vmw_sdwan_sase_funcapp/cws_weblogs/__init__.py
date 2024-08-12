import datetime
import logging
import json
import os
import requests
import socket
import time
# Needed by the Log Ingestion API
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError

import azure.functions as func

def initialize():
    # This script is to pull in relevant settings and verify if everything is given to run the API calls.
 
    # Pull in environmental variables

    # VECO settings
    host = os.environ["api_veco_fqdn"]
    token = os.environ["api_veco_authorization"]
    # Log Analytics settings for writing data
    dce = os.environ["dce_endpoint"]
    dcr_cwsweblog_immutableid = os.environ["dcr_cwsweblog_immutableid"]
    cws_weblog_stream = os.environ["stream_cwsweblog"]
    #Function App frequency in mins
    frequency = os.environ["app_frequency_mins"]
    frequency_sec = int(frequency) * 60
    frequency_msec = frequency_sec * 1000
    #validate that none of the settings are empty and add them to a JSON list
    if not [x for x in (host, token, dce, dcr_cwsweblog_immutableid, cws_weblog_stream) if x is None]:
        global j_config_list
        j_config_list = {
            "host": host,
            "token": token,
            "logingestion_api": {
                "dce": dce,
                "streams": {
                    "cws_weblog": cws_weblog_stream,
                    "cws_weblog_imi": dcr_cwsweblog_immutableid
                    }
                },
            "frequency_sec": frequency_sec,
            "frequency_msec": frequency_msec
        }
        logging.info("All variables set, initialization complete")
        return j_config_list
    else:
        logging.error("Missing parameter, function stopped. Please check the Application settings tab in your Function App configuration")
        j_config_list = {"error": "missing app settings parameter"}
        return j_config_list

def VECOvalidate(host):
    # This portion will run reachability tests against the target VECO host.
    veco_ipaddr=(socket.getaddrinfo(host, 443)[0][-1][0])
    logging.info("Target orchestrator: " + host + "IP address: " + veco_ipaddr)
    veco_https = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    veco_https.settimeout(2)
    socket_result = veco_https.connect_ex((veco_ipaddr,443))
    if socket_result == 0:
        return 0
    else:
        return 1

def EventCompiler(j_rawevent, event_type):
    # event_type is a new variable so that we can do two things:
    # 1. the def knows how to process data
    # 2. it keeps the changes required for a new event type relatively compact

    # Create JSON array that we will use for processed event signaling
    j_processed_events = []

    if event_type == "cws_weblog":
        # CWS Access logs - pagination, JSON array of events

        # This var is just for the feedback loop, we send events to the tables page by page
        j_multipage_processed = []

        # Do while loop intro
        while True:
            # This is the array that will contain the final formatting
            j_array_processing = []
            # Event counter for statistics
            events = 0
            for log_item in j_rawevent["data"]:
                j_log_event = {
                    #Date is reserved, need new key
                    "cws_timestamp": log_item["date"],
                    # Leave rest as-is, for future changes
                    "userId": log_item["userId"],
                    "url": log_item["url"],
                    "domain": log_item["domain"],
                    "categories": log_item["categories"],
                    "threatTypes": log_item["threatTypes"],
                    "webRiskScore": log_item["webRiskScore"],
                    "action": log_item["action"],
                    "userAgent": log_item["userAgent"],
                    "browserType": log_item["browserType"],
                    "browserVersion": log_item["browserVersion"],
                    "requestType": log_item["requestType"],
                    "requestMethod": log_item["requestMethod"],
                    "egressIp": log_item["egressIp"],
                    "destinationIp": log_item["destinationIp"],
                    "dnsResponse": log_item["dnsResponse"],
                    "sourceIp": log_item["sourceIp"],
                    "contentType": log_item["contentType"],
                    "accessMode": log_item["accessMode"],
                    "responseCode": log_item["responseCode"],
                    "protocol": log_item["protocol"],
                    "region": log_item["region"],
                    "ruleMatched": log_item["ruleMatched"],
                    "policyHeaders": log_item["policyHeaders"],
                    "fileHash": log_item["fileHash"],
                    "fileHashScore": log_item["fileHashScore"],
                    "fileSize": log_item["fileSize"],
                    "fileType": log_item["fileType"],
                    "fileName": log_item["fileName"],
                    "mimeType": log_item["mimeType"],
                    "fileScanResult": log_item["fileScanResult"],
                    "virusList": log_item["virusList"],
                    "sandboxInspectionResult": log_item["sandboxInspectionResult"],
                    "sandboxScore": log_item["sandboxScore"],
                    "sandboxMaliciousActivitiesFound": log_item["sandboxMaliciousActivitiesFound"],
                    "casbAppName": log_item["casbAppName"],
                    "casbCatName": log_item["casbCatName"],
                    "casbFunName": log_item["casbFunName"],
                    "casbOrgName": log_item["casbOrgName"],
                    "casbRiskScore": log_item["casbRiskScore"],
                    "userGroups": log_item["userGroups"],
                    "userGroupsMatched": log_item["userGroupsMatched"],
                    "risks": log_item["risks"],
                    "srcCountry": log_item["srcCountry"],
                    "dstCountry": log_item["dstCountry"],
                    "saasEgressHeaders": log_item["saasEgressHeaders"],
                    "policyName": log_item["policyName"]
                }
                # Update the array object-by-object
                j_array_processing.append(j_log_event)
                events = events + 1
            logging.info("Extracted " + str(events) + " events, sending it over for processing")
            j_processed_events=callLogAnalyticsAPI(j_array_processing, j_config_list["logingestion_api"]["dce"], j_config_list["logingestion_api"]["streams"]["cws_weblog_imi"], j_config_list["logingestion_api"]["streams"]["cws_weblog"])
            # Current page is fully processed here, need to think about next page
            logging.info("Searching for multi-page response...")
            multi_page_result=False
            if j_rawevent["metaData"]["nextPageLink"] != "":
                # Multi-page response found
                # Run a new API call, and...
                logging.info("API Metadata provided with nextpage token, processing")
                nextpage_params = "/logs?nextPageLink=" + j_rawevent["metaData"]["nextPageLink"]
                header = {
                    "Authorization": j_config_list["token"]
                }
                query = craftAPIurl(j_config_list["host"], "/api/cws/v1/enterprises/", j_config_list["token"], True, nextpage_params)
                logging.info("API call to: " + query)
                nextpage_response = requests.get(url=query, headers=header)
                if nextpage_response.status_code != 200:
                    # If the API call fails, skip next steps
                    logging.error("Unexpected error when sending API call")
                    break
                else:
                    # If the API call succeeds, do two things:
                    # 1. Add events we have sent to the event processing from this page to a larger reporting array
                    j_multipage_processed.append(j_processed_events)
                    # 2. Reset input event list to new page, start processing again
                    logging.info("Next page of the results loaded, starting processing...")
                    multi_page_result = True
                    j_rawevent = nextpage_response.json()
            else:
                # This clause is single paged, update main def and quit
                if multi_page_result == False:
                    logging.info("Single-page response, processing complete.")
                else:
                    logging.info("Last page reached, stopping the recursive processing.")
                    j_multipage_processed.append(j_processed_events)
                    j_processed_events = j_multipage_processed
                break
    return j_processed_events
    # Return data to main loop


def callLogAnalyticsAPI(j_array_events, dce_endpoint, immutableid, stream_name):
    #This def calls the Log Ingestion API to post all collected events
    # To have further info on the Log Analytics API implementation, please check: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-code?tabs=python

    # Resources for API call
    api_credentials = DefaultAzureCredential()
    
    # Create JSON Array for thelist of processed events
    j_processed_events = []

    logging.info("Calling Log Ingestion API ...")
    client = LogsIngestionClient(endpoint=dce_endpoint, credential=api_credentials, logging_enable=True)
    try:
        client.upload(rule_id=immutableid, stream_name=stream_name, logs=j_array_events)
        logging.info("Log Ingestion API - Successful Event upload")
        j_event = {
            "events": j_array_events,
            "metadata": {
                "loganalytics_status": "200",
                "loganalytics_dce": dce_endpoint,
                "loganalytics_table": stream_name
            }
        }
        j_processed_events.append(j_event)
    except HttpResponseError as e:
        logging.error("Upload failed. Message details: " + str(e))
        logging.error("LogAnalytics API reported an issue with the API call")
        j_event = {
            "events": j_array_events,
            "metadata": {
                "loganalytics_status": "{e}",
                "loganalytics_dce": dce_endpoint,
                "loganalytics_table": stream_name
            }
        }
        j_processed_events.append(j_event)

    # HTTP Data Collector API can deal with a JSON array, so multiple events can be added to the events payload.
    print("The Log Analytics API engine subroutine recorded an event with payload: " + json.dumps(j_processed_events))
    return j_processed_events

def callVECOAPIenterprise(host, token):
    # To be able to craft the APIv2 endpoints, we need the logicalID of the enterprise.
    # To get the logical ID, we need to call an APIv1 endpoint first, with POST and body set
    url = "https://" + host + "/portal/rest/enterprise/getEnterprise"
    header = {
        "Authorization": token
    }
    post_body = {
        "id": 0,
        "enterpriseId": 0,
        "with": [
            "enterpriseProxy"
        ]
    }
    j_entid_response = requests.post(url=url, headers=header, json=post_body)
    if j_entid_response.status_code != 200:
        logging.error("Could not fetch Logical ID from APIv1, error: " + str(j_entid_response.status_code))
    else:
        j_enterpriseid_response = j_entid_response.json()
        logging.info("Successful API call, Logical ID is set to: " + j_enterpriseid_response["logicalId"] + " for Enterprise: " + j_enterpriseid_response["name"])
    return j_enterpriseid_response

def craftAPIurl(host, endpoint, token="", need_logicalid=False, queryparams=""):
    # This def is really simple, it just creates the APIv2 query, then it can be passed on to the API caller
    if need_logicalid == False:
        query = "https://" + host + endpoint + queryparams
    else:
        j_enterpriseid = callVECOAPIenterprise(host, token)
        logicalid = j_enterpriseid["logicalId"]
        query = "https://" + host + endpoint + logicalid + queryparams
    logging.info("API endpoint created: " + query)
    return query

def callVECOAPIendpoint(method, query, token):
    # APIv2 handling
    # This function should handle API calls as a single def, but in case of multi-page responses, we might need to re-think this approach
    if method != "GET":
        logging.error("Unsupported APIv2 method" + method)
        j_apiengine_response = {
            "error": "Unsupported APIv2 method: " + method
        }
    else:
        # This is where we make the actual API call
        header = {
            "Authorization": token
            }
        j_veco_response = requests.get(url=query, headers=header)

        if (j_veco_response.status_code != 200):
            logging.info("API call encountered an error: " + str(j_veco_response.status_code))
            # FIXME: Add more error handling here for specific use-cases like 404, 500, etc.
            j_apiengine_response = {
                "error": str(j_veco_response.status_code)
            }
        else:
            logging.info("API call successful, crafting response")            
            j_rawevent = j_veco_response.json()
            # Send raw event with event type so that we can carve out smaller chunks of the API response, pagination, etc.
            j_apiengine_response=EventCompiler(j_rawevent, "cws_weblog")
    # Return list of processed events to main
    return j_apiengine_response

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    logging.info("Script initializing...")
    j_parameters = initialize()
    if "error" in j_parameters:
        logging.error("The function could not initialize, stopping...")
    else:
        logging.info("All input parameters have been received, running connectivity tests to API service.")
        veco_reachability = VECOvalidate(j_parameters["host"])
        if veco_reachability == 1:
            logging.error("Orchestrator is not reachable, stopping.")
        if veco_reachability == 0:
            logging.info("Orchestrator network connectivity tests were successful.")
            # At this point, we can start executing API functions
            # We will start building the API call now
            # FIXME: potentially we can rebuild this part a bit so that we contain the supported event types in a list
            epochs_now = int(time.time())
            logging.info("Measured epoch time in seconds: " + str(epochs_now))
            # Calculate the start time based on the frequency of the script and add 1 sec to avoid overlapping events
            start_s = epochs_now - j_config_list["frequency_sec"] + 1
            params = "/logs?start=" + str(start_s)
            query = craftAPIurl(j_parameters["host"], "/api/cws/v1/enterprises/", j_parameters["token"], True, params)

            j_apiengine_response = callVECOAPIendpoint("GET", query, j_parameters["token"])
            for api_call in j_apiengine_response:
                if api_call["metadata"]["loganalytics_status"] == "200":
                    logging.info("API call subroutine logged successful event upload to Endpoint " + api_call["metadata"]["loganalytics_dce"] + " into table " + api_call["metadata"]["loganalytics_table"])
                else:
                    logging.error("API call subroutine logged an error in event upload to Endpoint " + api_call["metadata"]["loganalytics_dce"] + " into table " + api_call["metadata"]["loganalytics_table"])
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

