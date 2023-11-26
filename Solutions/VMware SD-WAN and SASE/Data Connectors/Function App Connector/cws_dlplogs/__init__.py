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

global g_state
g_state = {
                "services": {
                    "efs": {
                        "delay_value": 0,
                        "delay_unit": "msec",
                        "update_timestamp": "",
                        # This is to keep track of the last IDPS events collected by the script
                        "idps_events": []
                    }
                }            
}

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
    # Extra steps for EFS:
    # FW logs have delays beyond 5-10 mins, and if this happens, we need to deal with it to avoid event loss.
    # 1. Check if the state config exists in the storage account
    # 2a. If not, and type is efs, add JSON entry that sets the delay to 0
    # 2b. If file exists, read delay entry so that we can adjust queries
    efs_delay = 0
    j_efs_events = []
    if event_type == "efs":
        logging.warning("FUNCTION-INIT: Verifying state library presence...")
        statedir = ShareDirectoryClient.from_connection_string(conn_str=os.environ["azsa_share_connectionstring"], share_name=os.environ["azsa_share_name"], directory_path="function_state")
        if statedir.exists():
            logging.info("FUNCTION-INIT: State Directory found, skip directory creation...")
            logging.warning("FUNCTION-INIT: Searching for existing state conditions...")
            filelist = list(statedir.list_directories_and_files())
            statedir.close()
            statefile = ShareFileClient.from_connection_string(conn_str=os.environ["azsa_share_connectionstring"], share_name=os.environ["azsa_share_name"], file_path="function_state/state.json")
            if filelist == []:
                logging.info("FUNCTION-INIT: No state configuration found, the script will assume first run, assuming delay of zero ...")
                g_state["services"]["efs"]["delay_value"] = 0
                g_state["services"]["efs"]["update_timestamp"] = str(datetime.datetime.utcnow())
                statefile.upload_file(data=json.dumps(g_state))
            else:
                raw_state = statefile.download_file()
                j_state = json.loads(raw_state.readall())
                # Now that we have the json read in a var, we can zeroize the event list in the file again
                g_state["services"]["efs"]["idps_events"] = []
                statefile.upload_file(data=json.dumps(g_state))
                statefile.close()
                if not j_state["services"]["efs"]["delay_value"] is None:
                    efs_delay = j_state["services"]["efs"]["delay_value"]
                if not j_state["services"]["efs"]["idps_events"] == []:
                    for j_state_event in j_state["services"]["efs"]["idps_events"]:
                        logging.info("Found last logged event with the following details: " + json.dumps(j_state_event))
                        g_state["services"]["efs"]["idps_events"].append(j_state_event)
                    logging.info("FUNCTION-INIT: EFS delay found in state file, current delay observed is " + str(efs_delay) + str(j_state["services"]["efs"]["delay_unit"]))
        else:
            logging.info("FUNCTION-INIT: State Directory is not found, creating new one...")
            statedir.create_directory()
            statedir.close()
            logging.info("FUNCTION-INIT: Writing initial state configuration, assuming delay of zero ...")
            statefile = ShareFileClient.from_connection_string(conn_str=os.environ["azsa_share_connectionstring"], share_name="azsa_share_name", file_path="function_state/state.json")
            g_state["services"]["efs"]["delay_value"] = 0                        
            g_state["services"]["efs"]["update_timestamp"] = str(datetime.datetime.utcnow())
            statefile.upload_file(data=json.dumps(g_state))
            statefile.close()            
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
                        "delay": efs_delay
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

def veco_fwlog_delayadjust():
    logging.info("FUNCTION-EFSDELAY: Starting Search API delay measurement.")
    # Re-adjust delay information in state so that the next iteration is aware of logging issues.
    # Return value structure defined:
    j_epoch_delay = {
        "data": {
            "1hr": {
                "event_count": 0,
                "avg_delay": 0,
                "measurement_unit": "msec"
            },
            "4hr": {
                "event_count": 0,
                "avg_delay": 0,
                "measurement_unit": "msec"
            },
            "8hr": {
                "event_count": 0,
                "avg_delay": 0,
                "measurement_unit": "msec"
            }
        },
        "metadata": {
            "loganalytics_api_result": 0,
            "new_state_stored": False,
            "veco_searchapi_result": 000
        }
    }

    # Run 0 to 0 query (from=0&size=0) to see how many events are in the log storage from the past 1/4/8 hours, we will use this as a baseline for calculating delay spread
    query_end = datetime.datetime.utcnow().isoformat()
    query_start = {
        "now-1hrs": datetime.datetime.isoformat(datetime.datetime.fromisoformat(query_end) - datetime.timedelta(hours=1)) + "Z",
        "now-4hrs": datetime.datetime.isoformat(datetime.datetime.fromisoformat(query_end) - datetime.timedelta(hours=4)) + "Z",
        "now-8hrs": datetime.datetime.isoformat(datetime.datetime.fromisoformat(query_end) - datetime.timedelta(hours=8)) + "Z"
    }
    # Again, for verbosity, capture delays (now-timestamp)
    j_delays = {
        "1hr": [],
        "4hr": [],
        "8hr": []
    }
    for query_start_timestamp in query_start:
        params= "/edgeFirewall?from=0&size=0&startTime=" + str(query_start[query_start_timestamp]) + "&endTime=" + str(query_end) + "Z"
        query = craftAPIurl(j_config_list["host"], "/api/search/v1/enterprises/", j_config_list["token"], True, params)
        logging.info("FUNCTION-EFSDELAY: API Call to: " + query)
        header = {
                        "Authorization": j_config_list["token"]
            }
        nullrequest = requests.get(url=query, headers=header)
        if nullrequest.status_code != 200:
                        # If the API call fails, skip next steps
                        logging.error("FUNCTION-EFSDELAY: Unexpected error when sending API call, terminating function...")
                        j_epoch_delay["metadata"]["veco_searchapi_result"] = nullrequest.status_code
                        return j_epoch_delay
        else:
            j_count_response = nullrequest.json()
            logging.warning("Firewall events: " + str(j_count_response["count"]))
            date_format = "%Y-%m-%dT%H:%M:%S.000Z"
            if j_count_response["count"] != 0:
                # 200 OK and events were found, go in and extract them
                if query_start[query_start_timestamp] == query_start["now-1hrs"]:
                    # Get the first 100 events form the past hour to calculate average delay
                    params_1hr = "/edgeFirewall?from=0&size=100&startTime=" + str(query_start[query_start_timestamp]) + "&endTime=" + str(query_end) + "Z"
                    query = craftAPIurl(j_config_list["host"], "/api/search/v1/enterprises/", j_config_list["token"], True, params_1hr)
                    past1hrrequest = requests.get(url=query, headers=header)
                    if past1hrrequest.status_code != 200:
                        # If the API call fails, skip next steps
                        logging.error("FUNCTION-EFSDELAY: Unexpected error when sending API call, terminating function...")
                        j_epoch_delay["metadata"]["veco_searchapi_result"] = nullrequest.status_code
                        return j_epoch_delay
                    else:
                        j_log_items = past1hrrequest.json()
                        logging.info("FUNCTION-EFSDELAY: Found firewall events to process in the past 1 hours: " + str(j_log_items["count"]))
                        j_epoch_delay["data"]["1hr"]["event_count"] = j_log_items["count"]
                        for log_item in j_log_items["data"]:
                            delay = datetime.datetime.fromisoformat(query_end) - datetime.datetime.strptime(log_item["_source"]["timestamp"], date_format)
                            j_delays["1hr"].append(int(delay.total_seconds() * 1000))

                if query_start[query_start_timestamp] == query_start["now-4hrs"]:
                    # Get the first 100 events form the past 4 hours to calculate average delay
                    params_4hr = "/edgeFirewall?from=0&size=100&startTime=" + str(query_start[query_start_timestamp]) + "&endTime=" + str(query_end) + "Z"
                    query = craftAPIurl(j_config_list["host"], "/api/search/v1/enterprises/", j_config_list["token"], True, params_4hr)
                    past4hrrequest = requests.get(url=query, headers=header)
                    if past4hrrequest.status_code != 200:
                        # If the API call fails, skip next steps
                        logging.error("FUNCTION-EFSDELAY: Unexpected error when sending API call, terminating function...")
                        j_epoch_delay["metadata"]["veco_searchapi_result"] = nullrequest.status_code
                        return j_epoch_delay
                    else:
                        j_log_items = past4hrrequest.json()
                        logging.info("FUNCTION-EFSDELAY: Found firewall events to process in the past 4 hours: " + str(j_log_items["count"]))
                        j_epoch_delay["data"]["4hr"]["event_count"] = j_log_items["count"]
                        for log_item in j_log_items["data"]:
                            delay = datetime.datetime.fromisoformat(query_end) - datetime.datetime.strptime(log_item["_source"]["timestamp"], date_format)
                            j_delays["4hr"].append(int(delay.total_seconds() * 1000))
                        
                if query_start[query_start_timestamp] == query_start["now-8hrs"]:
                    logging.info("FUNCTION-EFSDELAY: Found firewall logs to process in the past 8 hours: " + str(j_count_response["count"]))
                    # Get the first 100 events form the past 8 hours to calculate average delay
                    params_8hr = "/edgeFirewall?from=0&size=100&startTime=" + str(query_start[query_start_timestamp]) + "&endTime=" + str(query_end) + "Z"
                    query = craftAPIurl(j_config_list["host"], "/api/search/v1/enterprises/", j_config_list["token"], True, params_8hr)
                    past8hrrequest = requests.get(url=query, headers=header)
                    if past8hrrequest.status_code != 200:
                        # If the API call fails, skip next steps
                        logging.error("FUNCTION-EFSDELAY: Unexpected error when sending API call, terminating function...")
                        j_epoch_delay["metadata"]["veco_searchapi_result"] = nullrequest.status_code
                        return j_epoch_delay
                    else:
                        j_log_items = past8hrrequest.json()
                        logging.info("FUNCTION-EFSDELAY: Found firewall events to process in the past 8 hours: " + str(j_log_items["count"]))
                        j_epoch_delay["data"]["8hr"]["event_count"] = j_log_items["count"]
                        for log_item in j_log_items["data"]:
                            delay = datetime.datetime.fromisoformat(query_end) - datetime.datetime.strptime(log_item["_source"]["timestamp"], date_format)
                            j_delays["8hr"].append(int(delay.total_seconds() * 1000))

    # Average calculated delays in milliseconds
    # FIXME: sanitize this portion, very pedestrian code, but verbosity is advisable
    avg_count = 3
    sum = 0
    count = 0
    if j_delays["1hr"] != []:
        for delay_item in j_delays["1hr"]:
            sum = sum + delay_item
            count = count + 1
        avgdelay_1hr = sum // count
        j_epoch_delay["data"]["1hr"]["avg_delay"] = avgdelay_1hr
    else:
        avg_count = avg_count - 1
        avgdelay_1hr = 0

    if j_delays["4hr"] != []:
        for delay_item in j_delays["4hr"]:
            sum = sum + delay_item
            count = count + 1
        avgdelay_4hr = sum // count
        j_epoch_delay["data"]["4hr"]["avg_delay"] = avgdelay_4hr
    else:
        avg_count = avg_count - 1
        avgdelay_4hr = 0

    if j_delays["8hr"] != []:
        for delay_item in j_delays["8hr"]:
            sum = sum + delay_item
            count = count + 1
        avgdelay_8hr = sum // count
        j_epoch_delay["data"]["8hr"]["avg_delay"] = avgdelay_8hr
    else:
        avgdelay_8hr = 0
    logging.warning("FUNCTION-EFSDELAY: The script measured the first 100 events.")
    avgdelay = (avgdelay_1hr + avgdelay_4hr + avgdelay_8hr) // avg_count
    logging.info("FUNCTION-EFSDELAY: 1 hours measured average delay is: " + str(avgdelay_1hr) + "msec, 4 hours: " + str(avgdelay_4hr) + "msecs, 8 hours: " + str(avgdelay_8hr) + "msec")
    logging.info("FUNCTION-EFSDELAY: Next iteration will use the delay of : " + str(avgdelay) + " msecs, this is cca. " + str(avgdelay / 1000 / 60 / 60) + " hours.")

    # Now that we have the delay measured, we will write the state data to the storage account.
    logging.info("FUNCTION-EFSDELAY: Measurement complete, writing to file share...")
    statefile = ShareFileClient.from_connection_string(conn_str=os.environ["azsa_share_connectionstring"], share_name=os.environ["azsa_share_name"], file_path="function_state/state.json")
    g_state["services"]["efs"]["delay_value"] = avgdelay
    g_state["services"]["efs"]["delay_unit"] = "msec"
    g_state["services"]["efs"]["update_timestamp"]: str(datetime.datetime.utcnow())
    statefile.upload_file(data=json.dumps(g_state))
    statefile.close()
    j_epoch_delay["metadata"]["new_state_stored"] = True
    j_epoch_delay["metadata"]["veco_searchapi_result"] = 200

    if j_count_response["count"] == 0:
        logging.warning("FUNCTION-EFSDELAY: The delay measured by the script might be larger than 8 hours. If you suspect that you should be seeing firewall logs from the past 8 hours, please raise a case on my.vmware.com.")
    callLogAnalyticsAPI(j_epoch_delay, j_config_list["logingestion_api"]["dce"], j_config_list["logingestion_api"]["sdwan"]["efs_health"]["imi"], j_config_list["logingestion_api"]["sdwan"]["efs_health"]["stream"])
    return j_epoch_delay

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
    # metadata is a new variable that can be anything in JSON format. Combined with the event type this can be used to pass additional data
    now = datetime.datetime.now()
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
                "healthtest_timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "healthtest_status": j_rawevent["checks"][component]["status"],
                "healthtest_observed_unit": j_rawevent["checks"][component]["observedUnit"],
                "healthtest_observed_value": j_rawevent["checks"][component]["observedValue"]
            }
            j_array_processing.append(j_health_event)
            events = events + 1
        logging.info("FUNCTION-EVENTCOMPILER: Extracted " + str(events) + " events, sending them to the Log Analytics API for processing")
        j_processed_events=callLogAnalyticsAPI(j_array_processing, j_config_list["logingestion_api"]["dce"], j_config_list["logingestion_api"]["streams"]["cws_health_imi"], j_config_list["logingestion_api"]["streams"]["cws_health"])
        return j_processed_events
    
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
            logging.info("FUNCTION-EVENTCOMPILER: Extracted " + str(events) + " events, sending it over for processing")
            j_processed_events=callLogAnalyticsAPI(j_array_processing, j_config_list["logingestion_api"]["dce"], j_config_list["logingestion_api"]["streams"]["cws_weblog_imi"], j_config_list["logingestion_api"]["streams"]["cws_weblog"])
            # Current page is fully processed here, need to think about next page
            logging.info("FUNCTION-EVENTCOMPILER: Searching for multi-page response...")
            multi_page_result=False
            if j_rawevent["metaData"]["nextPageLink"] != "":
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
                else:
                    logging.info("FUNCTION-EVENTCOMPILER: Last page reached, stopping the recursive processing.")
                    j_multipage_processed.append(j_processed_events)
                    j_processed_events = j_multipage_processed
                break
        return j_processed_events
    

    # DLP Logs
    # Same as web but different event format
    if event_type == "cws_dlplog":
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
                j_ccl_array = []
                count_item = 0 
                for item in log_item["cclIds"]:
                    j_ccl_entity = {
                        "id": log_item["cclIds"][count_item],
                        "count": log_item["cclMatchCounts"][count_item],
                        "score": log_item["cclScores"][count_item]
                    }
                    count_item = count_item + 1
                    j_ccl_array.append(j_ccl_entity)    
                j_log_event = {
                    "eventTime": log_item["eventTime"],
                    "action": log_item["action"],
                    "alerted": log_item["alerted"],
                    # Content Control List items are concatenated int a single array as it bugs out in Azure Log Analytics
                    #"cclIds": log_item["cclIds"],
                    #"cclMatchCounts": log_item["cclMatchCounts"],
                    #"cclScores": log_item["cclScores"],
                    "ccl": j_ccl_array,
                    "domain": log_item["domain"],
                    "dstUrl": log_item["dstUrl"],
                    "eventId": log_item["eventId"],
                    "fileType": log_item["fileType"],
                    "filename": log_item["filename"],
                    "protocol": log_item["protocol"],
                    "requestType": log_item["requestType"],
                    "ruleId": log_item["ruleId"],
                    "ruleName": log_item["ruleName"],
                    "sha256": log_item["sha256"],
                    "srcUrl": log_item["srcUrl"],
                    "status": log_item["status"],
                    "streamName": log_item["streamName"],
                    "userInput": log_item["userInput"],
                    "userId": log_item["userId"]
                }
                # Update the array object-by-object
                j_array_processing.append(j_log_event)
                events = events + 1
            if events == 0:
                logging.info("Empty API response, skipping processing...")
                j_processed_events = []
                break
            else:
                logging.info("FUNCTION-EVENTCOMPILER: Extracted " + str(events) + " events, sending it over for processing")
                j_processed_events=callLogAnalyticsAPI(j_array_processing, j_config_list["logingestion_api"]["dce"], j_config_list["logingestion_api"]["cws"]["dlp"]["imi"], j_config_list["logingestion_api"]["cws"]["dlp"]["stream"])
                # Current page is fully processed here, need to think about next page
                logging.info("FUNCTION-EVENTCOMPILER: Searching for multi-page response...")
                multi_page_result=False
                if j_rawevent["metaData"]["nextPageLink"] != "":
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
                    else:
                        logging.info("FUNCTION-EVENTCOMPILER: Last page reached, stopping the recursive processing.")
                        j_multipage_processed.append(j_processed_events)
                        j_processed_events = j_multipage_processed
                    break
        return j_processed_events



    # EFS logs
    # So this is what we will do:
    # 1. Process response - skip upload for empty responses
    # 2. Deal with pagination, chances are that we will not have 100+ IOC events in a 10 min interval, but you never know.
    # 3. Gauge current delay:
    #               - Search back to past 4 hours, or first 2000 events.
    #               - Calculate delay (min, max, avg) in msecs
    #               - Write delay into storage account
    # Return data to main loop
    if event_type == "efs_fwlog":
        j_multipage_processed = []
        if j_rawevent["count"] == 0:
            logging.warning("FUNCTION-EVENTCOMPILER: Search API call resulted in empty response, nothing to report...")
            j_processed_events = [{
                "events": "None",
                "metadata": {
                    "loganalytics_status": "000",
                    "loganalytics_dce": "N/A",
                    "loganalytics_table": "N/A"
                }    
            }]
            j_delay = veco_fwlog_delayadjust()
            if j_delay["metadata"]["veco_searchapi_result"] == "000":
                logging.warning("FUNCTION-EVENTCOMPILER: Delay measurement failed.")
            return j_processed_events
        else:
            mp_from = 100
            mp_size = 100
            while True:
                # This is the array that will contain the final formatting
                j_array_processing = []
                # Event counter for statistics
                events = 0
                # Extract events from the response
                for log_item in j_rawevent["data"]:
                    j_log_event = {
                        "sessionId": log_item["_source"]["sessionId"],
                        "firewallPolicyName": log_item["_source"]["firewallPolicyName"],
                        "segmentLogicalId": log_item["_source"]["segmentLogicalId"],
                        "domainName": log_item["_source"]["domainName"],
                        "category": log_item["_source"]["category"],
                        "attackTarget": log_item["_source"]["attackTarget"],
                        "severity": log_item["_source"]["severity"],
                        "destination": log_item["_source"]["destination"],
                        "signature": log_item["_source"]["signature"],
                        "edgeLogicalId": log_item["_source"]["edgeLogicalId"],
                        "closeReason": log_item["_source"]["closeReason"],
                        "ipsAlert": log_item["_source"]["ipsAlert"],
                        "@timestamp": log_item["_source"]["@timestamp"],
                        "bytesReceived": log_item["_source"]["bytesReceived"],
                        "signatureId": log_item["_source"]["signatureId"],
                        "@version": log_item["_source"]["@version"],
                        "destinationIp": log_item["_source"]["destinationIp"],
                        "sourcePort": log_item["_source"]["sourcePort"],
                        "application": log_item["_source"]["application"],
                        "bytesSent": log_item["_source"]["bytesSent"],
                        "destinationPort": log_item["_source"]["destinationPort"],
                        "idsAlert": log_item["_source"]["idsAlert"],
                        "enterpriseLogicalId": log_item["_source"]["enterpriseLogicalId"],
                        "inputInterface": log_item["_source"]["inputInterface"],
                        "segmentName": log_item["_source"]["segmentName"],
                        "protocol": log_item["_source"]["protocol"],
                        "actionTaken": log_item["_source"]["actionTaken"],
                        "verdict": log_item["_source"]["verdict"],
                        "edgeName": log_item["_source"]["edgeName"],
                        "ruleId": log_item["_source"]["ruleId"],
                        "extensionHeader": log_item["_source"]["extensionHeader"],
                        "logType": log_item["_source"]["logType"],
                        "ruleVersion": log_item["_source"]["ruleVersion"],
                        "attackSource": log_item["_source"]["attackSource"],
                        "timestamp": log_item["_source"]["timestamp"],
                        "sessionDurationSecs": log_item["_source"]["sessionDurationSecs"],
                        "sourceIp": log_item["_source"]["sourceIp"]
                    }
                    # FIXME: Deal with duplicate events
                    # An event should be considered duplicate of an event in the array if:
                    # 1. The session ID is matching
                    # AND
                    # 2. The signature ID is matching
                    # AND
                    # 3. The timestamp is matching
                    state_event = {
                            "timestamp": j_log_event["timestamp"],
                            "sessionId": j_log_event["sessionId"],
                            "signatureId": j_log_event["signatureId"]
                        }
                    if g_state["services"]["efs"]["idps_events"] == []:
                        # State is missing the last event upload
                        logging.warning("No IDPS Event found in state config, assuming this is the first event...")                       
                        g_state["services"]["efs"]["idps_events"].append(state_event)
                        logging.warning("State file contents: " + json.dumps(g_state["services"]["efs"]))

                        j_array_processing.append(j_log_event)
                    else:
                        # Check if the current event is a duplicate of an already processed event
                        new_event = True
                        for j_eventsummary in g_state["services"]["efs"]["idps_events"]:
                            logging.warning("=== Iteration ===")
                            logging.warning("State file data: " + j_eventsummary["timestamp"] + " " + str(j_eventsummary["sessionId"]) + " " + str(j_eventsummary["signatureId"]))
                            logging.warning("API data: " + j_log_event["timestamp"] + " " + str(j_log_event["sessionId"]) + " " + str(j_log_event["signatureId"]))
                            logging.warning("=== Iteration ===")
                            if ((j_eventsummary["timestamp"] == j_log_event["timestamp"]) and (j_eventsummary["sessionId"] == j_log_event["sessionId"]) and (j_eventsummary["signatureId"] == j_log_event["signatureId"])):
                                logging.warning("Duplicate Event Detected.")
                                new_event = False
                        if new_event is True:
                            logging.warning("New event found, adding to the state file.")
                            logging.warning("State file data: " + j_eventsummary["timestamp"] + " " + str(j_eventsummary["sessionId"]) + " " + str(j_eventsummary["signatureId"]))
                            logging.warning("API data: " + j_log_event["timestamp"] + " " + str(j_log_event["sessionId"]) + " " + str(j_log_event["signatureId"]))
                            g_state["services"]["efs"]["idps_events"].append(state_event)
                            j_array_processing.append(j_log_event)
                            events = events + 1
                    
                logging.info("FUNCTION-EVENTCOMPILER: Extracted " + str(events) + " events, sending it over for processing")
                j_processed_events=callLogAnalyticsAPI(j_array_processing, j_config_list["logingestion_api"]["dce"], j_config_list["logingestion_api"]["sdwan"]["efs"]["imi"], j_config_list["logingestion_api"]["sdwan"]["efs"]["stream"])
                logging.info("FUNCTION-EVENTCOMPILER: Searching for multi-page response...")
                multi_page_result=False
                if j_rawevent["metaData"]["more"] != False:
                    # Multi-page response found
                    # Run a new API call, and...
                    logging.info("FUNCTION-EVENTCOMPILER: API Metadata indicates multipage answer, iterating through additional entries")
                    # FIXME: need to play with "from" and "size" based on the API response "count" to deal with multi-page, just break for now.
                    query_start = str(metadata["event_compiler"]["query_start"])
                    query_end = str(metadata["event_compiler"]["query_end"])
                    nextpage_params = "/edgeFirewall?from=" + str(mp_from) + "&size=" + mp_size + "&startTime=" + str(query_start) + "&endTime=" + str(query_end) + "Z&IDS_ALERT={\"IS\":1}"
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
                        mp_from = mp_from + 100
                else:
                    # This clause is single paged, update main def and quit
                    if multi_page_result == False:
                        logging.info("FUNCTION-EVENTCOMPILER: Single-page response, processing complete.")
                        break
                    else:
                        logging.info("FUNCTION-EVENTCOMPILER: Last page reached, stopping the recursive processing.")
                        j_multipage_processed.append(j_processed_events)
                        j_processed_events = j_multipage_processed
                        break
            statefile = ShareFileClient.from_connection_string(conn_str=os.environ["azsa_share_connectionstring"], share_name=os.environ["azsa_share_name"], file_path="function_state/state.json")
            statefile.upload_file(data=json.dumps(g_state))
            statefile.close()
            j_delay = veco_fwlog_delayadjust()
            return j_processed_events

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
    logging.info("The Log Analytics API engine subroutine recorded an event with payload: " + json.dumps(j_processed_events))
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
            j_apiengine_response=EventCompiler(j_rawevent, "cws_dlplog", metadata)
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
            start_s = (epochs_now - j_config_list["frequency_sec"]) + 1
            params = "/dlp/logs?start=" + str(start_s)
            query = craftAPIurl(j_parameters["host"], "/api/cws/v1/enterprises/", j_parameters["token"], True, params)

            j_apiengine_response = callVECOAPIendpoint("GET", query, j_parameters["token"])
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