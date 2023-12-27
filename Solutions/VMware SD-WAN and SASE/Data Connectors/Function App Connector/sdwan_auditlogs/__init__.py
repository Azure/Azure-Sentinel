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
# Need the storage account connection to store state information
from azure.storage.fileshare import ShareDirectoryClient
from azure.storage.fileshare import ShareFileClient

def initialize(event_type=""):
    # This script is to pull in relevant settings and verify if everything is given to run the API calls.
    # Pull in environmental variables

    # VECO settings
    host = os.environ["api_veco_fqdn"]
    token = os.environ["api_veco_authorization"]
    # Log Analytics settings for writing data
    dce = os.environ["dce_endpoint"]
    dcr_cwshealth_immutableid = os.environ["dcr_cwshealth_immutableid"]
    dcr_cwsweblog_immutableid = os.environ["dcr_cwsweblog_immutableid"]
    dcr_cwsdlplog_immutableid = os.environ["dcr_cwsdlplog_immutableid"]
    dcr_efsfwlog_immutableid = os.environ["dcr_efsfwlog_immutableid"]
    dcr_efshealth_immutableid = os.environ["dcr_efshealth_immutableid"]
    # Audit - future use
    dcr_auditlog_immutableid = os.environ["dcr_saseaudit_immutableid"]

    cwshealth_stream = os.environ["stream_cwshealth"]
    weblog_stream = os.environ["stream_cwsweblog"]
    dlplog_stream = os.environ["stream_cwsdlplog"]
    efsfwlog_stream = os.environ["stream_efsfwlog"]
    efshealth_stream = os.environ["stream_efshealth"]
    # Audit - future use
    auditlog_stream = os.environ["stream_saseaudit"]

    #Function App frequency in mins
    frequency = os.environ["app_frequency_mins"]
    frequency_sec = int(frequency) * 60
    frequency_msec = frequency_sec * 1000
    # Storage Account connectivity
   
    # FIXME: Clean up JSON file and get rid of the extra variables
    #validate that none of the settings are empty and add them to a JSON list
    if not [x for x in (host, token, dce, dcr_cwshealth_immutableid, dcr_cwsweblog_immutableid, weblog_stream, cwshealth_stream, dcr_cwsdlplog_immutableid, dlplog_stream, efsfwlog_stream, dcr_efsfwlog_immutableid) if x is None]:
        global j_config_list
        j_config_list = {
            "host": host,
            "token": token,
            "logingestion_api": {
                "dce": dce,
                "streams": {
                    "cws_health": cwshealth_stream,
                    "cws_health_imi": dcr_cwshealth_immutableid,
                    "cws_weblog": weblog_stream,
                    "cws_weblog_imi": dcr_cwsweblog_immutableid,
                    "cws_dlplog": dlplog_stream,
                    "cws_dlplog_imi": dcr_cwsdlplog_immutableid,
                    "efs_fwlog": efsfwlog_stream, 
                    "efs_fwlog_imi": dcr_efsfwlog_immutableid
                    },
                "cws": {
                    "health": {
                        "stream": cwshealth_stream,
                        "imi": dcr_cwshealth_immutableid
                    },
                    "web": {
                        "stream": weblog_stream,
                        "imi": dcr_cwsweblog_immutableid
                    },
                    "dlp": {
                        "stream": dlplog_stream,
                        "imi": dcr_cwsdlplog_immutableid
                    }
                },
                "sdwan": {
                    "efs": {
                        "stream": efsfwlog_stream,
                        "imi": dcr_efsfwlog_immutableid,
                    },
                    "efs_health": {
                        "stream": efshealth_stream,
                        "imi": dcr_efshealth_immutableid
                    },
                    "audit": {
                        "stream": auditlog_stream,
                        "imi": dcr_auditlog_immutableid
                    }
                }
                },
            "frequency_sec": frequency_sec,
            "frequency_msec": frequency_msec
        }

        logging.info("FUNCTION-INIT: All variables set, initialization complete")
        return j_config_list
    else:
        logging.error("FUNCTION-INIT: Missing parameter, function stopped. Please check the Application settings tab in your Function App configuration")
        j_config_list = {"error": "missing app settings parameter"}
        return j_config_list

def VECOvalidate(host):
    # This portion will run reachability tests against the target VECO host.
    veco_ipaddr=(socket.getaddrinfo(host, 443)[0][-1][0])
    logging.info("FUNCTION-VECO-CONNECTIVITY: Target orchestrator: " + host + "IP address: " + veco_ipaddr)
    veco_https = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    veco_https.settimeout(2)
    socket_result = veco_https.connect_ex((veco_ipaddr,443))
    if socket_result == 0:
        return 0
    else:
        return 1

def EventCompiler(j_rawevent, event_type, metadata={}):
    # event_type is a new variable so that we can do two things:
    # 1. the def knows how to process data
    # 2. it keeps the changes required for a new event type relatively compact
    # metadata is a dynamic variable that can be anything in JSON format. Combined with the event type this can be used to pass additional data

    # Event logs (Audit and other)
    # Check if "event" is found in metadata. If yes, send to log ingestion
    # Multipage support needed
    if event_type == "eventlog":
        # CWS Access logs - pagination, JSON array of events

        # This var is just for the feedback loop, we send events to the tables page by page
        j_multipage_processed = []
        multi_page_result = False
        # Do while loop intro
        while True:
            # This is the array that will contain the final formatting
            j_array_processing = []
            # Event counter for statistics
            events = 0
            for log_item in j_rawevent["data"]:
                j_log_event = {
                    "eventTime": log_item["eventTime"],
                    "event": log_item["event"],
                    "category": log_item["category"],
                    "severity": log_item["severity"],
                    "message": log_item["message"],
                    "detail": log_item["detail"]
                }
                # Check if the message detail contains "username" or it's an interesting event type.
                for event_category in metadata:
                    logging.info("Searching for events category: " + str(event_category))
                    j_event_category = metadata[event_category]
                    for event_type in j_event_category:
                        logging.info("Searching for event type: " + str(event_type))
                        if (("username" in j_log_event) or (j_log_event["event"] == event_type)):
                            # Update the array object-by-object
                            j_array_processing.append(j_log_event)
                            events = events + 1
            if events > 0:
                logging.info("FUNCTION-EVENTCOMPILER: Extracted " + str(events) + " events, sending it over for processing")
                j_processed_events=callLogAnalyticsAPI(j_array_processing, j_config_list["logingestion_api"]["dce"], j_config_list["logingestion_api"]["sdwan"]["audit"]["imi"], j_config_list["logingestion_api"]["sdwan"]["audit"]["stream"])
            else:
                logging.info("FUNCTION-EVENTCOMPILER: Extracted " + str(events) + " events, skip processing...")
            if j_rawevent["metaData"]["more"] != False:
                # Multi-page response found
                # Run a new API call, and...
                logging.info("FUNCTION-EVENTCOMPILER: API Metadata provided with nextpage token, processing")
                nextpage_params = "/logs?nextPageLink=" + j_rawevent["metaData"]["nextPageLink"]
                header = {
                    "Authorization": j_config_list["token"]
                }
                query = craftAPIurl(j_config_list["host"], "/api/cws/v1/enterprises/", j_config_list["token"], True, nextpage_params)
                logging.info("FUNCTION-EVENTCOMPILER: API call to: " + query)
                nextpage_response = requests.get(url=query, headers=header)
                if nextpage_response.status_code != 200:
                    # If the API call fails, skip next steps
                    logging.error("FUNCTION-EVENTCOMPILER: Unexpected error when sending API call")
                    break
                else:
                    # If the API call succeeds, do two things:
                    # 1. Add events we have sent to the event processing from this page to a larger reporting array
                    j_multipage_processed.append(j_processed_events)
                    # 2. Reset input event list to new page, start processing again
                    logging.info("FUNCTION-EVENTCOMPILER: Next page of the results loaded, starting processing...")
                    multi_page_result = True
                    j_rawevent = nextpage_response.json()
            else:
                # This clause is single paged, update main def and quit
                if multi_page_result == False:
                    logging.info("FUNCTION-EVENTCOMPILER: Single-page response, processing complete.")
                    j_processed_events = []
                else:
                    logging.info("FUNCTION-EVENTCOMPILER: Last page reached, stopping the recursive processing.")
                    j_multipage_processed.append(j_processed_events)
                    j_processed_events = j_multipage_processed
                break
        return j_processed_events

def callLogAnalyticsAPI(j_array_events, dce_endpoint, immutableid, stream_name):
    #This def calls the Log Ingestion API to post all collected events
    # To have further info on the Log Analytics API implementation, please check: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-code?tabs=python

    # Resources for API call
    api_credentials = DefaultAzureCredential()
    j_processed_events = []

    logging.info("FUNCTION-API-LOGANALYTICS: Calling Log Ingestion API ...")
    client = LogsIngestionClient(endpoint=dce_endpoint, credential=api_credentials, logging_enable=True)
    try:
        client.upload(rule_id=immutableid, stream_name=stream_name, logs=j_array_events)
        logging.info("FUNCTION-API-LOGANALYTICS: Log Ingestion API - Successful Event upload")
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
        logging.error("FUNCTION-API-LOGANALYTICS: Upload failed. Message details: " + str(e))
        logging.error("FUNCTION-API-LOGANALYTICS: LogAnalytics API reported an issue with the API call")
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
        logging.error("FUNCTION-API-LOGICALID: Could not fetch Logical ID from APIv1, error: " + str(j_entid_response.status_code))
    else:
        j_enterpriseid_response = j_entid_response.json()
        logging.info("FUNCTION-API-LOGICALID: Successful API call, Logical ID is set to: " + j_enterpriseid_response["logicalId"] + " for Enterprise: " + j_enterpriseid_response["name"])
    return j_enterpriseid_response

def craftAPIurl(host, endpoint, token="", need_logicalid=False, queryparams=""):
    # This def is really simple, it just creates the APIv2 query, then it can be passed on to the API caller
    if need_logicalid == False:
        query = "https://" + host + endpoint + queryparams
    else:
        j_enterpriseid = callVECOAPIenterprise(host, token)
        logicalid = j_enterpriseid["logicalId"]
        query = "https://" + host + endpoint + logicalid + queryparams
    logging.info("FUNCTION-URL-PARSER: API endpoint created: " + query)
    return query

def callVECOAPIendpoint(method, query, token, metadata={}):
    # APIv2 handling
    # This function should handle API calls as a single def, but in case of multi-page responses, we might need to re-think this approach
    # Metadata is there to support customization via optional JSON content.
    if method != "GET":
        logging.error("FUNCTION-VECO_API_ENGINE: Unsupported APIv2 method" + method)
        j_apiengine_response = {
            "error": "FUNCTION-VECO_API_ENGINE: Unsupported APIv2 method: " + method
        }
    else:
        # This is where we make the actual API call
        header = {
            "Authorization": token
            }
        j_veco_response = requests.get(url=query, headers=header)

        if (j_veco_response.status_code != 200):
            logging.info("FUNCTION-VECO_API_ENGINE: API call encountered an error: " + str(j_veco_response.status_code))
            # FIXME: Add more error handling here for specific use-cases like 404, 500, etc.
            j_apiengine_response = {
                "error": str(j_veco_response.status_code)
            }
        else:
            logging.info("FUNCTION-VECO_API_ENGINE: API call successful, processing response...")            
            j_rawevent = j_veco_response.json()
            # Send raw event with event type so that we can carve out smaller chunks of the API response, pagination, etc.
            j_apiengine_response=EventCompiler(j_rawevent, "eventlog", metadata)
    # Return list of processed events to main
    return j_apiengine_response

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info("Script initializing...")
    j_parameters = initialize(event_type="sdwan_audit")
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
            event_metadata = {
                "css" : [ "ALL_CSS_DOWN", "CSS_UP", "VPN_DATACENTER_STATUS" ],
                "audit" : [ "BROWSER_ENTERPRISE_LOGIN", "USER_LOGIN_FAILURE", "USER_LOGIN_SSO", "USER_LOGIN_FAILURE_SSO", "EDGE_SSH_LOGIN", "NEW_INTEGRATED_CA", "CERTIFICATE_REVOCATION", "CERTIFICATE_RENEWAL", "UPDATED_CLIENT_DEVICE_HOSTNAME_VIA_API",
                           "CREATE_USER", "EDIT_PROFILE" ],
                "mgd" : [
                    "NTP_CONF_APPLIED", "MGD_CONF_APPLIED", "MGD_CONF_FAILED", "MGD_CONF_PENDING", "MGD_CONF_UPDATE_INVALID", "MGD_DEACTIVATED",
                    "MGD_DIAG_REBOOT", "MGD_DIAG_RESTART", "MGD_EDGE_TUNNEL_DISABLED", "MGD_EDGE_TUNNEL_ENABLED", "MGD_EXITING", "MGD_HARD_RESET",
                    "MGD_INVALID_VCO_ADDRESS", "MGD_NETWORK_SETTINGS_UPDATED", "MGD_ROUTE_CHANGE", "MGD_ROUTE_DIRECT", "MGD_ROUTE_GATEWAY", "MGD_SHUTDOWN",
                    "MGD_START", "MGD_CONF_ROLLBACK"
                ],
                "edge" : [
                    "EDGE_MGD_SERVICE_DISABLED", "EDGE_MGD_SERVICE_FAILED", "EDGE_NEW_DEVICE", "EDGE_NEW_USER", "EDGE_DHCP_BAD_OPTION", "EDGE_DOT1X_SERVICE_DISABLED",
                    "EDGE_DOT1X_SERVICE_FAILED", "EDGE_MEMORY_USAGE_ERROR", "EDGE_MEMORY_USAGE_WARNING", "EDGE_OTHER_SERVICE_DISABLED", "EDGE_OTHER_SERVICE_FAILED",
                    "EDGE_REBOOTING", "EDGE_RESTARTING", "EDGE_SERVICE_DISABLED", "EDGE_SERVICE_DUMPED", "EDGE_SERVICE_FAILED", "EDGE_SHUTTING_DOWN",
                    "EDGE_STARTUP", "EDGE_USB_PORTS_ENABLE_FAILURE", "EDGE_USB_PORTS_DISABLE_FAILURE", "EDGE_USB_PLUGGED_IN", "EDGE_USB_UNPLUGGED",
                    "EDGE_NVS_TUNNEL_UP", "EDGE_NVS_TUNNEL_DOWN", "EDGE_TUNNEL_CAP_WARNING", "EDGE_DIRECT_TUNNEL_UNKNOWN", "EDGE_CONGESTED", "EDGE_STABLE"
                ],
                "cws" : [ "CWS_EVENT" ],
                "efs" : [
                    "POLL_IDPS_SIGNATURE_FAIL", "MGD_ATPUP_DOWNLOAD_IDPS_SIGNATURE_FAILED", "MGD_ATPUP_DECRYPT_IDPS_SIGNATURE_FAILED", "MGD_ATPUP_APPLY_IDPS_SIGNATURE_FAILED",
                    "MGD_ATPUP_APPLY_IDPS_SIGNATURE_SUCCEEDED", "MGD_ATPUP_STANDBY_UPDATE_START", "MGD_ATPUP_STANDBY_UPDATE_FAILED", "MGD_ATPUP_STANDBY_UPDATED",
                    "MGD_ATPUP_INVALID_IDPS_SIGNATURE", "IDPS_SIGNATURE_VCO_VERSION_CHECK_FAIL", "IDPS_SIGNATURE_GSM_VERSION_CHECK_FAIL", "IDPS_SIGNATURE_SKIP_DOWNLOAD_NO_UPDATE",
                    "IDPS_SIGNATURE_STORE_FAILURE_NO_PATH", "IDPS_SIGNATURE_DOWNLOAD_SUCCESS", "IDPS_SIGNATURE_DOWNLOAD_FAILURE", "IDPS_SIGNATURE_STORE_SUCCESS",
                    "IDPS_SIGNATURE_STORE_SIGNATURE_FAILURE", "IDPS_SIGNATURE_METADATA_INSERT_SUCCESS", "IDPS_SIGNATURE_METADATA_INSERT_FAILURE", "IDPS_SIGNATURE_INCORRECT_CHECKSUM"
                ]
            }
            start_ms = (epochs_now - j_config_list["frequency_sec"]) * 1000 + 1
            epochms_now = epochs_now * 1000
            params = "/events?start=" + str(start_ms) + "&end=" + str(epochms_now)
            query = craftAPIurl(j_parameters["host"], "/api/sdwan/v2/enterprises/", j_parameters["token"], True, params)

            j_apiengine_response = callVECOAPIendpoint("GET", query, j_parameters["token"], event_metadata)
            for api_call in j_apiengine_response:
                if api_call["metadata"]["loganalytics_status"] == "200":
                    logging.info("FUNCTION-CORE:: API call subroutine logged successful event upload to Endpoint " + api_call["metadata"]["loganalytics_dce"] + " into table " + api_call["metadata"]["loganalytics_table"])
                else:
                    if api_call["metadata"]["loganalytics_status"] == "000":
                        logging.info("FUNCTION-CORE: API call subroutine received empty response, skipped Log Analytics workflow.")
                    else:
                        logging.error("FUNCTION-CORE:: API call subroutine logged an error in event upload to Endpoint " + api_call["metadata"]["loganalytics_dce"] + " into table " + api_call["metadata"]["loganalytics_table"])

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)