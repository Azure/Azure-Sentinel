import requests
import json
import datetime
from requests.auth import HTTPBasicAuth
import azure.functions as func
import base64
import hmac
import hashlib
import os
import logging
from .state_manager import StateManager
import urllib3
import re
from requests.packages.urllib3.util.retry import Retry

customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
secretKey = os.environ['NessusSecretKey']
accessKey = os.environ['NessusAccessKey']
url = os.environ['NessusUrl']
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
log_type = 'Nessus_VM'
headers = {"X-ApiKeys": "secretKey={}; accessKey={}".format(secretKey, accessKey)}
if url == "https://cloud.tenable.com":
    verify = True
else:
    verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")


def generate_date():
    current_time = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info("The last time point is: {}".format(past_time))
    else:
        logging.info("There is no last time point, trying to get scans information for last 24 hours.")
        past_time = (current_time - datetime.timedelta(hours=24)).strftime("%s")
    state.post(current_time.strftime("%s"))
    return (past_time, current_time.strftime("%s"))


def get_query(sub_req, start_time):
    retries = Retry(
        total=3,
        status_forcelist={429, 501, 502, 503, 504},
        backoff_factor=1,
        respect_retry_after_header=True
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
    session = requests.Session()
    session.mount('https://', adapter)
    if start_time is not None:
        params = {"last_modification_date": start_time}
    else:
        params = {}
    try:
        r = session.get(url="{}/{}".format(url, sub_req),
                         headers=headers,
                         verify=verify,
                         params=params
                         )
        if r.status_code == 200:
            return r
        elif r.status_code == 401:
            logging.error("The authentication credentials are incorrect or missing. Error code: {}".format(r.status_code))
        else:
            logging.error("Something wrong. Error code: {}".format(r.status_code))
    except Exception as err:
        logging.error("Something wrong. Exception error text: {}".format(err))


def get_result(start_time):
    scans_query = get_query("scans", start_time)
    if scans_query is not None:
        scans = scans_query.json().get("scans")
        if scans is not None:
            for scan in scans:
                scan_result_events = []
                logging.info("Getting information events from scan '{}'.".format(scan.get("name")))
                get_scan_details_query = get_query("scans/{}".format(scan.get("id")), None)
                if get_scan_details_query is not None:
                    hosts = get_scan_details_query.json().get("hosts")
                    for host in hosts:
                        get_host_details_query = get_query("scans/{}/hosts/{}".format(scan.get("id"), host.get("host_id")), None)
                        if get_host_details_query is not None:
                            host_details = get_host_details_query.json()
                            for vulnerability_detail in host_details.get("vulnerabilities"):
                                result_event = {
                                        "scan_name": scan.get("name"),
                                        "scan_owner": scan.get("owner"),
                                        "scan_last_modification_date": scan.get("last_modification_date"),
                                        "scan_creation_date": scan.get("creation_date"),
                                        "host_start_time": (host_details.get("info")).get("host_start"),
                                        "host_end_time": (host_details.get("info")).get("host_end"),
                                        "host_mac_addr": (host_details.get("info")).get("mac-address"),
                                        "host_fqdn": (host_details.get("info")).get("host-fqdn"),
                                        "host_operating_system": (host_details.get("info")).get("operating-system"),
                                        "host_ip_addr": (host_details.get("info")).get("host-ip"),
                                        "vulnerability_plugin_name": vulnerability_detail.get("plugin_name"),
                                        "vulnerability_severity": vulnerability_detail.get("severity"),
                                        "vulnerability_cpe": vulnerability_detail.get("cpe"),
                                        "vulnerability_count": vulnerability_detail.get("count"),
                                        "vulnerability_plugin_family": vulnerability_detail.get("plugin_family"),
                                        "type": "host_vulnerability_info"
                                        }
                                scan_result_events.append(result_event)
                            for compliance_detail in host_details.get("compliance"):
                                result_event = {
                                        "scan_name": scan.get("name"),
                                        "scan_owner": scan.get("owner"),
                                        "scan_last_modification_date": scan.get("last_modification_date"),
                                        "scan_creation_date": scan.get("creation_date"),
                                        "host_start_time": (host_details.get("info")).get("host_start"),
                                        "host_end_time": (host_details.get("info")).get("host_end"),
                                        "host_mac_addr": (host_details.get("info")).get("mac-address"),
                                        "host_fqdn": (host_details.get("info")).get("host-fqdn"),
                                        "host_operating_system": (host_details.get("info")).get("operating-system"),
                                        "host_ip_addr": (host_details.get("info")).get("host-ip"),
                                        "compliance_plugin_name": compliance_detail.get("plugin_name"),
                                        "complince_severity": compliance_detail.get("severity"),
                                        "compliance_count": vulnerability_detail.get("count"),
                                        "compliance_plugin_family": compliance_detail.get("plugin_family"),
                                        "type": "host_compliance_info"
                                        }
                                scan_result_events.append(result_event)
                if post_data(json.dumps(scan_result_events)) is not None:
                    logging.info("{} events from scan '{}' successfully processed to Azure".format(len(scan_result_events),scan.get("name")))


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization


def post_data(body):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        return response.status_code
    else:
        logging.warn("Events are not processed into Azure. Response code: {}".format(response.status_code))
        return None


def main(mytimer: func.TimerRequest)  -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    start_time, end_time = generate_date()
    logging.info("Time period parameters: from {} - to {}.".format(start_time,end_time))
    get_result(start_time)

