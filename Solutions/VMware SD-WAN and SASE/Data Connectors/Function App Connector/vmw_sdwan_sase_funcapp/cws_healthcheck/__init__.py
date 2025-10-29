import datetime
import logging
import json
import os
import requests
import socket
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
    dcr_cwshealth_immutableid = os.environ["dcr_cwshealth_immutableid"]
    dcr_cwsweblog_immutableid = os.environ["dcr_cwsweblog_immutableid"]
    cwshealth_stream = os.environ["stream_cwshealth"]
    weblog_stream = os.environ["stream_cwsweblog"]
    #Function App frequency in mins and convert them to seconds and milliseconds for multiple epoch format handling
    frequency = os.environ["app_frequency_mins"]
    frequency_sec = int(frequency) * 60
    frequency_msec = frequency_sec * 1000

    #validate that none of the settings are empty and add them to a JSON list, so we can reuse it as needed
    global j_config_list
    j_config_list = {}
    if not [x for x in (host, token, dce, dcr_cwshealth_immutableid, dcr_cwsweblog_immutableid, weblog_stream, cwshealth_stream) if x is None]:
        j_config_list = {
            "host": host,
            "token": token,
            "logingestion_api": {
                "dce": dce,
                "streams": {
                    "cws_health": cwshealth_stream,
                    "cws_health_imi": dcr_cwshealth_immutableid,
                    "cws_weblog": weblog_stream,
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

    # Create JSON object for returning details on processed events for diagnostics and troubleshooting:
    j_processed_events = []
    if event_type == "cws_health":
        # CWS Health data: no pagination, JSON list of subcomponents.
        # Enumerate solution components
        j_list_cwscomponents= [ "vni:responseTime", "database:connection", "database:responseTime", "cwsManager:responseTime"]
        # Go through each checks and create a standalone event
        j_array_processing = []
        events = 0
        for component in j_list_cwscomponents:
            out_component = component.replace(":", "_")
            j_health_event = {
                "cws_component": out_component,
                "healthtest_timestamp": j_rawevent["checks"][component]["time"],
                "healthtest_status": j_rawevent["checks"][component]["status"],
                "healthtest_observed_unit": j_rawevent["checks"][component]["observedUnit"],
                "healthtest_observed_value": j_rawevent["checks"][component]["observedValue"]
            }
            j_array_processing.append(j_health_event)
            events = events + 1
        logging.info("Extracted " + str(events) + " events, sending them to the Log Analytics API for processing")
        j_processed_events=callLogAnalyticsAPI(j_array_processing, j_config_list["logingestion_api"]["dce"], j_config_list["logingestion_api"]["streams"]["cws_health_imi"], j_config_list["logingestion_api"]["streams"]["cws_health"])
    # Return data to main loop
    return j_processed_events


def callLogAnalyticsAPI(j_array_events, dce_endpoint, immutableid, stream_name):
    #This def calls the Log Ingestion API to post all collected events
    # To have further info on the Log Analytics API implementation, please check: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-code?tabs=python

    # Resources for API call
    api_credentials = DefaultAzureCredential()
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
            j_apiengine_response=EventCompiler(j_rawevent, "cws_health")
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
            # For this particular function, we do not need the logical ID, so the below line is commented out
            # logicalid = callVECOAPIenterprise(j_parameters["host"], j_parameters["token"])

            # We will start building the API call now
            # FIXME: potentially we can rebuild this part a bit so that we contain the supported event types in a list
            query = craftAPIurl(j_parameters["host"], "/api/cws/v1/healthcheck")

            j_apiengine_response = callVECOAPIendpoint("GET", query, j_parameters["token"])
            for api_call in j_apiengine_response:
                if api_call["metadata"]["loganalytics_status"] == "200":
                    logging.info("API call subroutine logged successful event upload to Endpoint " + api_call["metadata"]["loganalytics_dce"] + " into table " + api_call["metadata"]["loganalytics_table"])
                else:
                    logging.error("API call subroutine logged an error in event upload to Endpoint " + api_call["metadata"]["loganalytics_dce"] + " into table " + api_call["metadata"]["loganalytics_table"])
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

