import os
import logging
import time
import re
from typing import Iterable, List
import duo_client
import azure.functions as func

from .sentinel_connector import AzureSentinelConnector
from .state_manager import StateManager


logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


CISCO_DUO_INTEGRATION_KEY = os.environ['CISCO_DUO_INTEGRATION_KEY']
CISCO_DUO_SECRET_KEY = os.environ['CISCO_DUO_SECRET_KEY']
CISCO_DUO_API_HOSTNAME = os.environ['CISCO_DUO_API_HOSTNAME']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
SHARED_KEY = os.environ['SHARED_KEY']
FILE_SHARE_CONN_STRING = os.environ['AzureWebJobsStorage']
LOG_TYPE = 'CiscoDuo'


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


def main(mytimer: func.TimerRequest) -> None:
    logging.info('Starting script')
    admin_api = duo_client.Admin(
        ikey=CISCO_DUO_INTEGRATION_KEY,
        skey=CISCO_DUO_SECRET_KEY,
        host=CISCO_DUO_API_HOSTNAME,
    )
    sentinel = AzureSentinelConnector(
        log_analytics_uri=LOG_ANALYTICS_URI,
        workspace_id=WORKSPACE_ID,
        shared_key=SHARED_KEY,
        log_type=LOG_TYPE,
        queue_size=5000
    )

    state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_trust_monitor_logs_last_ts.txt')
    process_trust_monitor_events(admin_api, state_manager=state_manager, sentinel=sentinel)

    state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_auth_logs_last_ts.txt')
    process_auth_logs(admin_api, state_manager=state_manager, sentinel=sentinel)

    state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_admin_logs_last_ts.txt')
    process_admin_logs(admin_api, state_manager=state_manager, sentinel=sentinel)

    state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_tele_logs_last_ts.txt')
    process_tele_logs(admin_api, state_manager=state_manager, sentinel=sentinel)

    state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_offline_enrollment_logs_last_ts.txt')
    process_offline_enrollment_logs(admin_api, state_manager=state_manager, sentinel=sentinel)

    logging.info('Script finished. Sent events: {}'.format(sentinel.successfull_sent_events_number))


def process_trust_monitor_events(admin_api: duo_client.Admin, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    logging.info('Start processing trust_monitor logs')

    logging.info('Getting last timestamp')
    mintime = state_manager.get()
    if mintime:
        logging.info('Last timestamp is {}'.format(mintime))
        mintime = int(mintime) + 1
    else:
        logging.info('Last timestamp is not known. Getting data for last 24h')
        mintime = int(time.time() - 86400) * 1000

    maxtime = int(time.time() - 120) * 1000

    logging.info('Making trust_monitor logs request: mintime={}, maxtime={}'.format(mintime, maxtime))
    for event in admin_api.get_trust_monitor_events_iterator(mintime=mintime, maxtime=maxtime):
        sentinel.send(event)
    sentinel.flush()
    
    logging.info('Saving trust_monitor logs last timestamp {}'.format(maxtime))
    state_manager.post(str(maxtime))


def process_auth_logs(admin_api: duo_client.Admin, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    logging.info('Start processing authentication logs')

    logging.info('Getting last timestamp')
    mintime = state_manager.get()
    if mintime:
        logging.info('Last timestamp is {}'.format(mintime))
        mintime = int(mintime) + 1
    else:
        logging.info('Last timestamp is not known. Getting data for last 24h')
        mintime = int(time.time() - 86400) * 1000

    maxtime = int(time.time() - 120) * 1000

    for event in get_auth_logs(admin_api, mintime, maxtime):
        sentinel.send(event)

    sentinel.flush()
    
    logging.info('Saving auth logs last timestamp {}'.format(maxtime))
    state_manager.post(str(maxtime))
    

def get_auth_logs(admin_api: duo_client.Admin, mintime: int, maxtime: int) -> Iterable[dict]:
    limit = 1000
    logging.info('Making authentication logs request: mintime={}, maxtime={}'.format(mintime, maxtime))
    res = admin_api.get_authentication_log(api_version=2, mintime=mintime, maxtime=maxtime, limit=str(limit), sort='ts:asc')

    events = res['authlogs']
    logging.info('Obtained {} auth events'.format(len(events)))

    for event in events:
        yield event

    while len(events) == limit:
        next_offset = res['metadata']['next_offset']
        if next_offset:
            next_offset = ','.join(next_offset)
        else:
            break
        logging.info('Making authentication logs request: next_offset={}'.format(next_offset))
        res = admin_api.get_authentication_log(api_version=2, mintime=mintime, maxtime=maxtime, limit=str(limit), sort='ts:asc', next_offset=next_offset)
        events = res['authlogs']
        logging.info('Obtained {} auth events'.format(len(events)))

        for event in events:
            yield event


def process_admin_logs(admin_api: duo_client.Admin, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    logging.info('Start processing administrator logs')

    logging.info('Getting last timestamp')
    mintime = state_manager.get()
    if mintime:
        logging.info('Last timestamp is {}'.format(mintime))
        mintime = int(mintime) + 1
    else:
        logging.info('Last timestamp is not known. Getting data for last 24h')
        mintime = int(time.time() - 86400)

    last_ts = None

    for event in get_admin_logs(admin_api, mintime):
        last_ts = event['timestamp']
        sentinel.send(event)

    sentinel.flush()
    
    if last_ts:
        logging.info('Saving admin logs last timestamp {}'.format(last_ts))
        state_manager.post(str(last_ts))
    

def get_admin_logs(admin_api: duo_client.Admin, mintime: int) -> Iterable[dict]:
    limit = 1000
    logging.info('Making administrator logs request: mintime={}'.format(mintime))
    events = admin_api.get_administrator_log(mintime)
    logging.info('Obtained {} admin events'.format(len(events)))
    for event in events:
        mintime = event['timestamp']
        yield event

    while len(events) == limit:
        mintime += 1
        logging.info('Making administrator logs request: mintime={}'.format(mintime))
        events = admin_api.get_administrator_log(mintime)
        logging.info('Obtained {} admin events'.format(len(events)))
        for event in events:
            mintime = event['timestamp']
            yield event

    
def process_tele_logs(admin_api: duo_client.Admin, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    logging.info('Start processing telephony logs')

    logging.info('Getting last timestamp')
    mintime = state_manager.get()
    if mintime:
        logging.info('Last timestamp is {}'.format(mintime))
        mintime = int(mintime) + 1
    else:
        logging.info('Last timestamp is not known. Getting data for last 24h')
        mintime = int(time.time() - 86400)
    
    last_ts = None

    for event in get_tele_logs(admin_api, mintime):
        last_ts = event['timestamp']
        sentinel.send(event)
    
    sentinel.flush()

    if last_ts:
        logging.info('Saving telephony logs last timestamp {}'.format(last_ts))
        state_manager.post(str(last_ts))
    

def get_tele_logs(admin_api: duo_client.Admin, mintime: int) -> Iterable[dict]:
    limit = 1000
    logging.info('Making telephony logs request: mintime={}'.format(mintime))
    events = admin_api.get_telephony_log(mintime)
    logging.info('Obtained {} tele events'.format(len(events)))
    for event in events:
        mintime = event['timestamp']
        yield event

    while len(events) == limit:
        mintime += 1
        logging.info('Making telephony logs request: mintime={}'.format(mintime))
        events = admin_api.get_telephony_log(mintime)
        logging.info('Obtained {} tele events'.format(len(events)))
        for event in events:
            mintime = event['timestamp']
            yield event


def process_offline_enrollment_logs(admin_api: duo_client.Admin, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    logging.info('Start processing offline_enrollment logs')

    logging.info('Getting last timestamp')
    mintime = state_manager.get()
    if mintime:
        logging.info('Last timestamp is {}'.format(mintime))
        mintime = int(mintime) + 1
    else:
        logging.info('Last timestamp is not known. Getting data for last 24h')
        mintime = int(time.time() - 86400)

    last_ts = None

    for event in get_offline_enrollment_logs(admin_api, mintime):
        last_ts = event['timestamp']
        sentinel.send(event)

    sentinel.flush()
    
    if last_ts:
        logging.info('Saving offline_enrollment logs last timestamp {}'.format(last_ts))
        state_manager.post(str(last_ts))
    

def get_offline_enrollment_logs(admin_api: duo_client.Admin, mintime: int) -> Iterable[dict]:
    limit = 1000
    logging.info('Making offline_enrollment logs request: mintime={}'.format(mintime))
    events = make_offline_enrollment_logs_request(admin_api, mintime)
    logging.info('Obtained {} offline_enrollment events'.format(len(events)))
    for event in events:
        mintime = event['timestamp']
        yield event

    while len(events) == limit:
        mintime += 1
        logging.info('Making offline_enrollment logs request: mintime={}'.format(mintime))
        events = make_offline_enrollment_logs_request(admin_api, mintime)
        logging.info('Obtained {} offline_enrollment events'.format(len(events)))
        for event in events:
            mintime = event['timestamp']
            yield event


def make_offline_enrollment_logs_request(admin_api: duo_client.Admin, mintime) -> List[dict]:
    mintime = str(int(mintime))
    params = {
        'mintime': mintime,
    }
    response = admin_api.json_api_call(
        'GET',
        '/admin/v1/logs/offline_enrollment',
        params,
    )
    return response
