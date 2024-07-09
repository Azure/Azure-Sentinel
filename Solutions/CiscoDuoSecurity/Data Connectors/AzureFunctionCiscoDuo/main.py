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
MAX_SYNC_WINDOW_PER_RUN_MINUTES = os.getenv('MAX_SYNC_WINDOW_PER_RUN_MINUTES', "60")
MAX_SCRIPT_EXEC_TIME_MINUTES = 10

LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


def main(mytimer: func.TimerRequest) -> None:
    logging.info('Starting script')
    start_ts = int(time.time())
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

    log_types = get_log_types()

    if 'trust_monitor' in log_types:
        state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_trust_monitor_logs_last_ts.txt')
        process_trust_monitor_events(admin_api, state_manager=state_manager, sentinel=sentinel)
        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            return

    if 'authentication' in log_types:
        state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_auth_logs_last_ts.txt')
        process_auth_logs(admin_api, start_ts, state_manager=state_manager, sentinel=sentinel)
        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            return
    
    if 'administrator' in log_types:
        state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_admin_logs_last_ts.txt')
        process_admin_logs(admin_api, start_ts, state_manager=state_manager, sentinel=sentinel)
        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            return
    
    if 'telephony' in log_types:
        state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_tele_logs_last_ts.txt')
        process_tele_logs(admin_api, start_ts, state_manager=state_manager, sentinel=sentinel)
        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            return
    
    if 'offline_enrollment' in log_types:
        state_manager = StateManager(FILE_SHARE_CONN_STRING, file_path='cisco_duo_offline_enrollment_logs_last_ts.txt')
        process_offline_enrollment_logs(admin_api, start_ts, state_manager=state_manager, sentinel=sentinel)

    logging.info('Script finished. Sent events: {}'.format(sentinel.successfull_sent_events_number))


def get_log_types():
    res = str(os.environ.get('CISCO_DUO_LOG_TYPES', ''))
    if not res:
        res = 'trust_monitor,authentication,administrator,telephony,offline_enrollment'
    return [x.lower().strip() for x in res.split(',')]


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
    diff = maxtime - mintime
    maxwindow = int(MAX_SYNC_WINDOW_PER_RUN_MINUTES) * 60000
    if(diff > maxwindow):
        maxtime = mintime + maxwindow
        logging.warn('Ingestion is lagging for trust_monitor logs, limiting synchronization window to {}'.format(maxwindow))

    logging.info('Making trust_monitor logs request: mintime={}, maxtime={}'.format(mintime, maxtime))
    for event in admin_api.get_trust_monitor_events_iterator(mintime=mintime, maxtime=maxtime):
        sentinel.send(event)
    sentinel.flush()
    
    logging.info('Saving trust_monitor logs last timestamp {}'.format(maxtime))
    state_manager.post(str(maxtime))


def process_auth_logs(admin_api: duo_client.Admin, start_ts, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    limit = 1000
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
    diff = maxtime - mintime
    maxwindow = int(MAX_SYNC_WINDOW_PER_RUN_MINUTES) * 60000
    if(diff > maxwindow):
        maxtime = mintime + maxwindow
        logging.warn('Ingestion is lagging for authentication logs, limiting synchronization window to {}'.format(maxwindow))

    events, next_offset = get_auth_logs(admin_api, mintime, maxtime)

    for event in events:
        sentinel.send(event)

    sentinel.flush()
    
    logging.info('Saving auth logs last timestamp {}'.format(maxtime))
    state_manager.post(str(maxtime))

    while len(events) == limit:
        if next_offset and next_offset is not None:
            next_offset = ','.join(next_offset)
        else:
            break
        logging.info('Making authentication logs request: next_offset={}'.format(next_offset))
            
        try:
            response = admin_api.get_authentication_log(api_version=2, mintime=mintime, maxtime=maxtime, limit=str(limit), sort='ts:asc', next_offset=next_offset)
            logging.info('Response recieved {}'.format(response))
        except Exception as ex:
            logging.info('Error in while loop while getting authentication logs- {}'.format(ex))
            if ex.status == 429:
                logging.info('429 exception occurred, trying retry after 60 seconds')
                time.sleep(60)
                response = admin_api.get_authentication_log(api_version=2, mintime=mintime, maxtime=maxtime, limit=str(limit), sort='ts:asc', next_offset=next_offset)
            
        if(response is not None): 
            events = response['authlogs']
            logging.info('Obtained {} auth events'.format(len(events)))
        else:
            logging.info('returned response as Null')

        for event in events:
            sentinel.send(event)
        sentinel.flush()
    
        logging.info('Saving auth logs last timestamp {}'.format(maxtime))
        state_manager.post(str(maxtime))

        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            return


def get_auth_logs(admin_api: duo_client.Admin, mintime: int, maxtime: int):
    limit = 1000
    logging.info('Making authentication logs request: mintime={}, maxtime={}'.format(mintime, maxtime))
    try:
        res = admin_api.get_authentication_log(api_version=2, mintime=mintime, maxtime=maxtime, limit=str(limit), sort='ts:asc')
    except Exception as err:
        logging.info('Error while getting authentication logs- {}'.format(err))
        if err.status == 429:
            logging.info('429 exception occurred, trying retry after 60 seconds')
            time.sleep(60)
            res = admin_api.get_authentication_log(api_version=2, mintime=mintime, maxtime=maxtime, limit=str(limit), sort='ts:asc')
    
    if(res is not None):
        events = res['authlogs']
        next_offset = res['metadata']['next_offset']
        logging.info('Obtained {} auth events'.format(len(events)))
    else:
        logging.info('Error while getting authentication logs')   
        events = None
        next_offset = None 
    return events, next_offset


def process_admin_logs(admin_api: duo_client.Admin, start_ts, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    limit = 1000
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
    events = get_admin_logs(admin_api, mintime)

    for event in events:
        last_ts = event['timestamp']
        sentinel.send(event)

    sentinel.flush()
    
    if last_ts:
        logging.info('Saving admin logs last timestamp {}'.format(last_ts))
        state_manager.post(str(last_ts))

    while len(events) == limit:
        mintime = last_ts
        mintime += 1
        logging.info('Making administrator logs request: mintime={}'.format(mintime))
        try:
            events = admin_api.get_administrator_log(mintime)
        except Exception as ex:
            logging.info('Error while getting administrator logs- {}'.format(ex))
            if ex.status == 429:
                logging.info('429 exception occurred, trying retry after 60 seconds')
                time.sleep(60)
                events = admin_api.get_administrator_log(mintime)
            
        if(events is not None):
            logging.info('Obtained {} admin events'.format(len(events)))
                
        else:
            logging.info('Events returned as null in administrator logs')

        for event in events:
            last_ts = event['timestamp']
            sentinel.send(event)

        sentinel.flush()
    
        if last_ts:
            logging.info('Saving admin logs last timestamp {}'.format(last_ts))
            state_manager.post(str(last_ts))

        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            return
   

def get_admin_logs(admin_api: duo_client.Admin, mintime: int) -> Iterable[dict]:
    limit = 1000
    logging.info('Making administrator logs request: mintime={}'.format(mintime))
    try:
        events = admin_api.get_administrator_log(mintime)
    except Exception as err:
        logging.info('Error while getting administrator logs- {}'.format(err))
        if err.status == 429:
            logging.info('429 exception occurred, trying retry after 60 seconds')
            time.sleep(60)
            events = admin_api.get_administrator_log(mintime)

    if(events is not None):
        logging.info('Obtained {} admin events'.format(len(events)))

    else:
        logging.info('Error while getting administrator logs')
        events = None    
    return events
    
def process_tele_logs(admin_api: duo_client.Admin, start_ts, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    limit = 1000
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

    events = get_tele_logs(admin_api, mintime)

    for event in events:
        last_ts = event['timestamp']
        sentinel.send(event)
    
    sentinel.flush()

    if last_ts:
        logging.info('Saving telephony logs last timestamp {}'.format(last_ts))
        state_manager.post(str(last_ts))

    while len(events) == limit:
        mintime = last_ts
        mintime += 1
        logging.info('Making telephony logs request: mintime={}'.format(mintime))
        try:
            events = admin_api.get_telephony_log(mintime)
        except Exception as ex:                
            logging.info('Error while getting telephony logs - {}'.format(ex))
            if ex.status == 429:
                logging.info('429 exception occurred, trying retry after 60 seconds')
                time.sleep(60)
                events = admin_api.get_telephony_log(mintime)
        
        if(events is not None):
            logging.info('Obtained {} tele events'.format(len(events)))
    
        else:
            logging.info('Events returned as null in telephony logs')

        for event in events:
            last_ts = event['timestamp']
            sentinel.send(event)
    
        sentinel.flush()

        if last_ts:
            logging.info('Saving telephony logs last timestamp {}'.format(last_ts))
            state_manager.post(str(last_ts))

        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            return

        
def get_tele_logs(admin_api: duo_client.Admin, mintime: int) -> Iterable[dict]:
    limit = 1000
    logging.info('Making telephony logs request: mintime={}'.format(mintime))
    try:
        events = admin_api.get_telephony_log(mintime)
    except Exception as err:
        logging.info('Error while getting telephony logs - {}'.format(err))
        if err.status == 429:
            logging.info('429 exception occurred, trying retry after 60 seconds')
            time.sleep(60)
            events = admin_api.get_telephony_log(mintime)
    
    if(events is not None):
        logging.info('Obtained {} tele events'.format(len(events)))
    else:
        logging.info('Error while getting telephony logs')  
        events = None
    return events  


def process_offline_enrollment_logs(admin_api: duo_client.Admin, start_ts, state_manager: StateManager, sentinel: AzureSentinelConnector) -> None:
    limit = 1000
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

    events = get_offline_enrollment_logs(admin_api, mintime)

    for event in events:
        last_ts = event['timestamp']
        sentinel.send(event)

    sentinel.flush()
    
    if last_ts:
        logging.info('Saving offline_enrollment logs last timestamp {}'.format(last_ts))
        state_manager.post(str(last_ts))

    while len(events) == limit:
        mintime = last_ts
        mintime += 1
        logging.info('Making offline_enrollment logs request: mintime={}'.format(mintime))
        try:
            events = make_offline_enrollment_logs_request(admin_api, mintime)
        except Exception as ex:
            logging.info('Error while getting offline_enrollment logs - {}'.format(ex))
            if ex.status == 429:
                logging.info('429 exception occurred, trying retry after 60 seconds')
                time.sleep(60)
                events = make_offline_enrollment_logs_request(admin_api, mintime)
        
        if(events is not None):
            logging.info('Obtained {} offline_enrollment events'.format(len(events)))
        
        else:
            logging.info('Events returned as null in offline_enrollment logs')

        for event in events:
            last_ts = event['timestamp']
            sentinel.send(event)

        sentinel.flush()
    
        if last_ts:
            logging.info('Saving offline_enrollment logs last timestamp {}'.format(last_ts))
            state_manager.post(str(last_ts))

        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            return

        
def get_offline_enrollment_logs(admin_api: duo_client.Admin, mintime: int) -> Iterable[dict]:
    limit = 1000
    logging.info('Making offline_enrollment logs request: mintime={}'.format(mintime))
    try:
        events = make_offline_enrollment_logs_request(admin_api, mintime)
    except Exception as err:
        logging.info('Error while getting offline_enrollment logs- {}'.format(err))
        if err.status == 429:
            logging.info('429 exception occurred, trying retry after 60 seconds')
            time.sleep(60)
            events = make_offline_enrollment_logs_request(admin_api, mintime)
    
    if(events is not None):
        logging.info('Obtained {} offline_enrollment events'.format(len(events)))
        
    else:
        logging.info('Error while getting offline_enrollment logs')   
        events = None
    return events 

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

def check_if_script_runs_too_long(start_ts):
    now = int(time.time())
    duration = now - start_ts
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.85)
    return duration > max_duration

