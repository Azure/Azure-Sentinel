import requests
import datetime
import hashlib
import hmac
import base64
import logging
from .pyepm import getAggregatedEvents, getDetailedRawEvents, epmAuth, getSetsList, getPolicyAuditRawEventDetails, \
    getAggregatedPolicyAudits, getAdminAuditEvents, samlAuth
import os
from datetime import datetime, timedelta
import json
from .state_manager import StateManager
import re
import azure.functions as func

dispatcher = os.environ['CyberArkEPMServerURL']
username = os.environ['CyberArkEPMUsername']
password = os.environ['CyberArkEPMPassword']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
use_saml_auth = os.environ['UseSAMLAuth']
identity_tenant_url = os.environ['IdentityTenantURL']
identity_tenant_id = os.environ['IdentityTenantID']
identity_appkey = os.environ['IdentityAppKey']
log_type = "CyberArkEPM"
connection_string = os.environ['AzureWebJobsStorage']
chunksize = 2000
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if dispatcher == "":
    raise Exception("CyberArkEPMServerURL is missing")

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logging.warning("logAnalyticsUri is None, used default value.")
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(logAnalyticsUri))
if (not match):
    raise Exception("CyberArkEPM: Invalid Log Analytics Uri.")


def generate_date():
    current_time = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(minutes=10)
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info("The last time point is: {}".format(past_time))
    else:
        logging.info("There is no last time point, trying to get events for last hour.")
        past_time = (current_time - timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state.post(current_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return past_time, current_time.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


def post_data(chunk):
    body = json.dumps(chunk)
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    try:
        response = requests.post(uri, data=body, headers=headers)

        if 200 <= response.status_code <= 299:
            logging.info("{} events was injected".format(len(chunk)))
            return response.status_code
        elif response.status_code == 401:
            logging.error(
                "The authentication credentials are incorrect or missing. Error code: {}".format(response.status_code))
        else:
            logging.error("Something wrong. Error code: {}".format(response.status_code))
        return None
    except Exception as err:
        logging.error("Something wrong. Exception error text: {}".format(err))


def gen_chunks_to_object(data, chunk_size=100):
    chunk = []
    for index, line in enumerate(data):
        if index % chunk_size == 0 and index > 0:
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk


def gen_chunks(data):
    for chunk in gen_chunks_to_object(data, chunk_size=chunksize):
        post_data(chunk)


def get_events(func_name, auth, filter_date, set_id, next_cursor="start"):
    events_json = func_name(epmserver=auth.json()["ManagerURL"],
                            epmToken=auth.json()['EPMAuthenticationResult'],
                            authType='EPM', setid=set_id['Id'],
                            data=filter_date,
                            next_cursor=next_cursor).json()
    if type(events_json) == list:
        logging.info("Set - {} is empty.".format(set_id["Name"]))
        return {'events': []}
    else:
        if events_json["nextCursor"]:
            response_json = get_events(auth=auth, filter_date=filter_date, set_id=set_id, func_name=func_name,
                                       next_cursor=events_json["nextCursor"])
            events_json["events"] += response_json["events"]
    for event in events_json["events"]:
        event["set_name"] = set_id["Name"]
    return events_json


def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Starting program')
    start_time, end_time = generate_date()
    logging.info('Data processing. Period(UTC): {} - {}'.format(start_time, end_time))
    try:
        if(str(use_saml_auth).lower() == "true"):
            auth = samlAuth(dispatcher=dispatcher, username=username, password=password, identityTenantID=identity_tenant_id, identityTenantURL=identity_tenant_url, identityAppKey=identity_appkey)
        else:
            auth = epmAuth(dispatcher=dispatcher, username=username, password=password)
        if auth.status_code == 401:
            logging.error(
                "The authentication credentials are incorrect or missing. Error code: {}".format(auth.status_code))
            return
        sets_list = getSetsList(epmserver=dispatcher, epmToken=auth.json()['EPMAuthenticationResult'], authType='EPM')
    except Exception as err:
        logging.error("CyberArkEPMServerURL is invalid")
        return
    filter_date = '{"filter": "eventDate GE ' + str(start_time) + ' AND eventDate LE ' + end_time + '"}'
    aggregated_events = []
    raw_events = []
    aggregated_policy_audits = []
    policy_audit_raw_event_details = []
    for set_id in sets_list.json()["Sets"]:
        logging.info("Collecting aggregated events from {}".format(set_id["Name"]))
        aggregated_events += get_events(func_name=getAggregatedEvents, auth=auth, filter_date=filter_date,
                                        set_id=set_id)["events"]
        logging.info("Collecting raw events from {}".format(set_id["Name"]))
        raw_events += get_events(func_name=getDetailedRawEvents,
                                 auth=auth, filter_date=filter_date, set_id=set_id)["events"]
        logging.info("Collecting aggregated policy audits from {}".format(set_id["Name"]))
        aggregated_policy_audits += get_events(func_name=getAggregatedPolicyAudits,
                                               auth=auth, filter_date=filter_date, set_id=set_id)["events"]
        logging.info("Collecting policy audit raw event details from {}".format(set_id["Name"]))
        policy_audit_raw_event_details += get_events(func_name=getPolicyAuditRawEventDetails,
                                                     auth=auth, filter_date=filter_date, set_id=set_id)["events"]
        logging.info("Collecting Admin Audit Data from {}".format(set_id["Name"]))
        admin_audit_data = getAdminAuditEvents(epmserver=dispatcher, epmToken=auth.json()['EPMAuthenticationResult'], authType='EPM', setid=set_id['Id'], start_time=start_time, end_time=end_time, limit=100)

    # Send data via data collector API
    for aggregated_event in aggregated_events:
        aggregated_event["event_type"] = "aggregated_events"
    for raw_event in raw_events:
        raw_event["event_type"] = "raw_event"
    for aggregated_policy_audit in aggregated_policy_audits:
        aggregated_policy_audit["event_type"] = "aggregated_policy_audits"
    for policy_audit_raw_event_detail in policy_audit_raw_event_details:
        policy_audit_raw_event_detail["event_type"] = "policy_audit_raw_event_details"
    gen_chunks(aggregated_events + raw_events + aggregated_policy_audits + policy_audit_raw_event_details + admin_audit_data)
