from ast import Pass
import os
import datetime
import logging
import re
from xmlrpc.client import Boolean
import requests
import json
from requests.auth import HTTPBasicAuth
from dateutil.parser import parse as parse_datetime
from typing import List
import azure.functions as func

from .sentinel_connector import AzureSentinelConnector
from .state_manager import StateManager


logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


CISCO_SE_API_API_HOST = os.environ['CISCO_SE_API_API_HOST']
CISCO_SE_API_CLIENT_ID = os.environ['CISCO_SE_API_CLIENT_ID']
CISCO_SE_API_KEY = os.environ['CISCO_SE_API_KEY']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
SHARED_KEY = os.environ['SHARED_KEY']
FILE_SHARE_CONN_STRING = os.environ['AzureWebJobsStorage']
LOG_TYPE = 'CiscoSecureEndpoint'


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


def main(mytimer: func.TimerRequest):
    logging.info('Script started.')
    sentinel = AzureSentinelConnector(LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, LOG_TYPE, queue_size=1000)
    audit_logs_state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_se_auditlogs_last_ts')
    events_state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_se_events_last_ts')
    cli = CiscoAMPClient(CISCO_SE_API_API_HOST, CISCO_SE_API_CLIENT_ID, CISCO_SE_API_KEY)

    audit_logs_last_ts = audit_logs_state_manager.get()
    audit_logs_last_ts = parse_date_from(audit_logs_last_ts)
    logging.info(f'Getting audit logs from {audit_logs_last_ts}')
    for events in cli.get_audit_logs(audit_logs_last_ts):
        for event in events:
            sentinel.send(event)
        sentinel.flush()
        audit_logs_last_ts = get_last_event_ts(events=events, last_ts=audit_logs_last_ts, field_name='created_at')
        if isinstance(audit_logs_last_ts, datetime.datetime):
            audit_logs_state_manager.post(audit_logs_last_ts.isoformat())

    events_last_ts = events_state_manager.get()
    events_last_ts = parse_date_from(events_last_ts)
    logging.info(f'Getting events from {events_last_ts}')
    
    for events in cli.get_events(events_last_ts):
        for event in events:
            sentinel.send(event)
        sentinel.flush()
        events_last_ts = get_last_event_ts(events=events, last_ts=events_last_ts, field_name='date')
        if isinstance(events_last_ts, datetime.datetime):
            events_state_manager.post(events_last_ts.isoformat())

    logging.info(f'Script finished. Total sent records: {sentinel.successfull_sent_events_number}')


class CiscoAMPClient:
    def __init__(self, host, client_id, api_key):
        host = host.lower()
        self._validate_host(host)
        self.host = host
        self._client_id = client_id
        self._api_key = api_key

    def _validate_host(self, host):
        hosts_list = [
            'api.amp.cisco.com',
            'api.apjc.amp.cisco.com',
            'api.eu.amp.cisco.com'
        ]
        if host not in hosts_list:
            raise ValueError(f'Host {host} is not correct. Use one of {hosts_list}.')
    
    def get_audit_logs(self, start_time: datetime.datetime):
        url = f'https://{self.host}/v1/audit_logs'
        params = {
            'limit': 500
        }
        if isinstance(start_time, datetime.datetime):
            start_time = start_time + datetime.timedelta(microseconds=1)
            start_time = start_time.isoformat()
            params['start_time'] = start_time
        res = requests.get(url, params=params, auth=HTTPBasicAuth(self._client_id, self._api_key), timeout=30)
        if not res.ok:
            raise Exception(f'Error while calling Cisco API. Response code: {res.status_code}')
        jsonData = json.loads(res.text)
        yield jsonData['data']
        next_link = jsonData['metadata']['links'].get('next')
        while next_link:
            res = requests.get(next_link, auth=HTTPBasicAuth(self._client_id, self._api_key), timeout=30)
            if not res.ok:
                raise Exception(f'Error while calling Cisco API. Response code: {res.status_code}')
            jsonData = json.loads(res.text)
            yield jsonData['data']
            next_link = jsonData['metadata']['links'].get('next')
        
    def get_events(self, start_time: datetime.datetime):
        url = f'https://{self.host}/v1/events'
        params = {
            'limit': 500
        }
        if isinstance(start_time, datetime.datetime):
            start_time = start_time + datetime.timedelta(microseconds=1)
            start_time = start_time.isoformat()
            params['start_date'] = start_time
        res = requests.get(url, params=params, auth=HTTPBasicAuth(self._client_id, self._api_key), timeout=30)
        if not res.ok:
            raise Exception(f'Error while calling Cisco API. Response code: {res.status_code}')
        jsonData = json.loads(res.text)
        yield jsonData['data']
        next_link = jsonData['metadata']['links'].get('next')
        while next_link:
            res = requests.get(next_link, auth=HTTPBasicAuth(self._client_id, self._api_key), timeout=30)
            if not res.ok:
                raise Exception(f'Error while calling Cisco API. Response code: {res.status_code}')
            jsonData = json.loads(res.text)
            yield jsonData['data']
            next_link = jsonData['metadata']['links'].get('next')


def parse_date_from(date_from: str) -> datetime.datetime:
    try:
        date_from = parse_datetime(date_from)
    except:
        pass
    if not isinstance(date_from, datetime.datetime):
        date_from = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=1)
    return date_from


def get_last_event_ts(events: List[dict], last_ts: datetime.datetime, field_name: str) -> datetime.datetime:
    for event in events:
        event_ts = event.get(field_name)
        try:
            event_ts = parse_datetime(event_ts)
        except:
            pass
        if isinstance(event_ts, datetime.datetime):
            if isinstance(last_ts, datetime.datetime) and event_ts > last_ts:
                last_ts = event_ts
    if check_on_future_event_time(last_ts):
        current_timestap_utc = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        last_ts = current_timestap_utc.isoformat()
    return last_ts


def check_on_future_event_time(time_field: datetime):
    event_ts = time_field
    try:
        event_ts = parse_datetime(event_ts)
    except:
        pass
    if isinstance(event_ts, datetime.datetime):
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        if event_ts > now + datetime.timedelta(days=1):
            msg = 'Event timestamp {} is larger that now. Exit script.'.format(event_ts.isoformat())
            logging.info(msg)
            return True
        else:
            return False