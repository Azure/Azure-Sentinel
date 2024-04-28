import os
import json
import datetime
import time
from boxsdk.auth.jwt_auth import JWTAuth
from boxsdk import Client
from boxsdk.object.events import Events, EnterpriseEventsStreamType
#from boxsdk.util.api_call_decorator import api_call
from .sentinel_connector import AzureSentinelConnector
from .state_manager import StateManager
from dateutil.parser import parse as parse_date
import azure.functions as func
import logging
import re
#from datetime import datetime, timedelta
from dateutil.parser import parse as parse_datetime
from typing import List


WORKSPACE_ID = os.environ['AzureSentinelWorkspaceId']
SHARED_KEY = os.environ['AzureSentinelSharedKey']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
LOG_TYPE = 'BoxEvents'
Delay_Minutes = os.environ.get('Delay_Minutes',2)
Historical_Data_Days = os.environ.get('Historical_Data_Days',0)
Delay_Minutes = int(Delay_Minutes)
Historical_Data_Days = int(Historical_Data_Days)

# interval of script execution
SCRIPT_EXECUTION_INTERVAL_MINUTES = 10
# if ts of last extracted event is older than now - MAX_PERIOD_MINUTES -> script will get events from now - SCRIPT_EXECUTION_INTERVAL_MINUTES
MAX_PERIOD_MINUTES = 60
# max azure function lifetime
AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES = 9

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")

def main(mytimer: func.TimerRequest):
    logging.getLogger().setLevel(logging.INFO)
    start_time = time.time()
    config_json = os.environ['BOX_CONFIG_JSON']
    config_dict = json.loads(config_json)

    logging.info(f'Parameters initialized are  WORKSPACE_ID: {WORKSPACE_ID} SHARED_KEY: ItsASecret logAnalyticsUri: {logAnalyticsUri} LOG_TYPE: {LOG_TYPE}  Delay_Minutes: {Delay_Minutes} Historical_Data_Days: {Historical_Data_Days} SCRIPT_EXECUTION_INTERVAL_MINUTES: {SCRIPT_EXECUTION_INTERVAL_MINUTES} AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES: {AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES} MAX_PERIOD_MINUTES: {MAX_PERIOD_MINUTES} ')

    created_before = datetime.datetime.utcnow() - datetime.timedelta(minutes=Delay_Minutes)
    created_before = created_before.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0).isoformat()

    file_storage_connection_string = os.environ['AzureWebJobsStorage']
    state_manager = StateManager(connection_string=file_storage_connection_string)

    stream_position, created_after = get_stream_pos_and_date_from(
        marker=state_manager.get(),
        max_period_minutes=MAX_PERIOD_MINUTES,
        script_execution_interval_minutes=SCRIPT_EXECUTION_INTERVAL_MINUTES
    )

    created_after = parse_datetime(str(created_after)) + datetime.timedelta(seconds=1)

    if parse_datetime(str(created_after)) + datetime.timedelta(minutes=MAX_PERIOD_MINUTES)  < parse_datetime(str(created_before)):
        created_before = parse_datetime(str(created_after)) + datetime.timedelta(minutes=MAX_PERIOD_MINUTES)
        logging.info('Backlog to process is more than than {} minutes. So changing created_before to {}. Remaining data will be processed during next invocation'.format(MAX_PERIOD_MINUTES, created_before))


    logging.info('Script started. Getting events from created_before {}, created_after {}'.format(created_before, created_after))

    sentinel = AzureSentinelConnector(workspace_id=WORKSPACE_ID, logAnalyticsUri = logAnalyticsUri, shared_key=SHARED_KEY, log_type=LOG_TYPE, queue_size=10000)
    with sentinel:
        last_event_date = None
        for events, stream_position in get_events(start_time, config_dict, created_after=created_after, created_before=created_before, stream_position=stream_position):
            for event in events:
                sentinel.send(event)
            last_event_date = get_last_event_ts(events=events, last_ts=created_after, field_name='created_at') if events else last_event_date
            logging.getLogger().setLevel(logging.INFO)

    if last_event_date:
        save_marker(state_manager, stream_position, str(last_event_date))
        logging.info(f"Events are available. Saving Marker processed till: {last_event_date}")
    elif created_before:
        save_marker(state_manager, stream_position, str(created_before))
        logging.info(f"Events are not available. Saving Marker processed till: {created_before}")

    if sentinel.failed_sent_events_number:
        logging.error('Script finished unsuccessfully. {} events have been sent. {} events have not been sent'.format(sentinel.successfull_sent_events_number, sentinel.failed_sent_events_number))
        exit(1)
    else:
        logging.info('Script finished successfully. {} events have been sent. {} events have not been sent'.format(sentinel.successfull_sent_events_number, sentinel.failed_sent_events_number))

def get_last_event_ts(events: List[dict], last_ts: datetime.datetime, field_name: str) -> datetime.datetime:
    logging.getLogger().setLevel(logging.INFO)
    for event in events:
        event_ts = event.get(field_name)
        try:
            event_ts = parse_datetime(event_ts)
        except:
            pass
        if isinstance(event_ts, datetime.datetime):
            if isinstance(last_ts, datetime.datetime) and event_ts > last_ts:
                last_ts = event_ts
    return last_ts

def get_stream_pos_and_date_from(marker, max_period_minutes, script_execution_interval_minutes):
    logging.getLogger().setLevel(logging.INFO)
    """Returns last saved checkpoint. If last checkpoint is older than max_period_minutes - returns now - script_execution_interval_minutes."""

    def get_default_date_from(script_execution_interval_minutes):
        date_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=Historical_Data_Days*24*60)
        #date_from = datetime.datetime(2023, 1, 30, 13, 45, 0, 000000)
        date_from = date_from.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0).isoformat()
        return date_from

    def get_token_from_marker(marker, max_period_minutes):
        token = 0
        last_event_date = None
        try:
            last_token, last_event_date = marker.split(' ',1)
            last_event_date = parse_date(last_event_date)
            
            minutes_from_last_ingested_event = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - last_event_date).total_seconds() / 60
            if minutes_from_last_ingested_event < max_period_minutes:
                token = last_token
        except Exception:
            pass
        return token, last_event_date

    token, last_event_date = get_token_from_marker(marker, max_period_minutes)
    if last_event_date:
        date_from = last_event_date
    else:
        date_from = get_default_date_from(script_execution_interval_minutes)

    return int(token), date_from


def save_marker(state_manager, stream_position, last_event_date):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Saving last stream_position {} and last_event_date {}'.format(stream_position, last_event_date))
    state_manager.post(str(stream_position) + ' ' + last_event_date)


def check_if_time_is_over(start_time, interval_minutes, max_script_exec_time_minutes):
    """Returns True if function's execution time is less than interval between function executions and
    less than max azure func lifetime. In other case returns False."""
    
    logging.getLogger().setLevel(logging.INFO)
    max_minutes = min(interval_minutes, max_script_exec_time_minutes)
    if max_minutes > 1:
        max_time = max_minutes * 60 - 30
    else:
        max_time = 50
    script_execution_time = time.time() - start_time
    if script_execution_time > max_time:
        return True
    else:
        return False


class ExtendedEvents(Events):
    #@api_call
    def get_events(self, start_time, stream_position=0, stream_type=EnterpriseEventsStreamType.ADMIN_LOGS, created_after=None, created_before=None, limit=100):
        url = self.get_url()
        params = {
            'limit': limit,
            'stream_position': stream_position,
            'stream_type': stream_type,
            'created_after': created_after,
            'created_before': created_before
        }
        box_response = self._session.get(url, params=params)
        response = box_response.json().copy()
        return self.translator.translate(self._session, response_object=response)


def get_events(start_time, config_dict, created_after=None, created_before=None, stream_position=0):
    logging.getLogger().setLevel(logging.WARNING)
    limit = 500
    config = JWTAuth.from_settings_dictionary(config_dict)
    client = Client(config)
    events_client = ExtendedEvents(client._session)

    while True:
        if parse_datetime(str(created_after)) >= parse_datetime(str(created_before)):
            logging.warning(f"Created After param {created_after} is greater then Created Before param {created_before} ")
            break
        stream_position = 0
        res = events_client.get_events(start_time, stream_position=stream_position, created_after=created_after, created_before=created_before, limit=limit)
        stream_position = res['next_stream_position']
        logging.info(f"Next stream position is {stream_position}")
        events = [event.response_object for event in res['entries']]
        yield events, stream_position
        if check_if_time_is_over(start_time, SCRIPT_EXECUTION_INTERVAL_MINUTES, AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES):
            logging.info('Stopping script because time for execution is over')
            break
        if len(events) < limit:
            break
        created_after = get_last_event_ts(events=events,last_ts=created_after,field_name='created_at') + datetime.timedelta(seconds=1)