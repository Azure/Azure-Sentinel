import os
import json
import datetime
import time
from boxsdk.auth.jwt_auth import JWTAuth
from boxsdk import Client
from boxsdk.object.events import Events, EnterpriseEventsStreamType
from boxsdk.util.api_call_decorator import api_call
from .sentinel_connector import AzureSentinelConnector
from .state_manager import StateManager
from dateutil.parser import parse as parse_date
import azure.functions as func
import logging
import re


WORKSPACE_ID = os.environ['AzureSentinelWorkspaceId']
SHARED_KEY = os.environ['AzureSentinelSharedKey']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
LOG_TYPE = 'BoxEvents'

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")

# interval of script execution
SCRIPT_EXECUTION_INTERVAL_MINUTES = 2
# if ts of last extracted event is older than now - MAX_PERIOD_MINUTES -> script will get events from now - SCRIPT_EXECUTION_INTERVAL_MINUTES
MAX_PERIOD_MINUTES = 1440
# max azure function lifetime
AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES = 9


def main(mytimer: func.TimerRequest):
    start_time = time.time()
    config_json = os.environ['BOX_CONFIG_JSON']
    config_dict = json.loads(config_json)

    file_storage_connection_string = os.environ['AzureWebJobsStorage']
    state_manager = StateManager(connection_string=file_storage_connection_string)

    stream_position, created_after = get_stream_pos_and_date_from(
        marker=state_manager.get(),
        max_period_minutes=MAX_PERIOD_MINUTES,
        script_execution_interval_minutes=SCRIPT_EXECUTION_INTERVAL_MINUTES
    )

    logging.info('Script started. Getting events from stream_position {}, created_after {}'.format(stream_position, created_after))

    sentinel = AzureSentinelConnector(workspace_id=WORKSPACE_ID, logAnalyticsUri = logAnalyticsUri, shared_key=SHARED_KEY, log_type=LOG_TYPE, queue_size=10000)
    with sentinel:
        for events, stream_position in get_events(config_dict, created_after, stream_position=stream_position):
            for event in events:
                sentinel.send(event)
            last_event_date = events[-1]['created_at']
            if check_if_time_is_over(start_time, SCRIPT_EXECUTION_INTERVAL_MINUTES, AZURE_FUNC_MAX_EXECUTION_TIME_MINUTES):
                logging.info('Stopping script because time for execution is over.')
                break

    save_marker(state_manager, stream_position, last_event_date)

    if sentinel.failed_sent_events_number:
        logging.error('Script finished unsuccessfully. {} events have been sent. {} events have not been sent'.format(sentinel.successfull_sent_events_number, sentinel.failed_sent_events_number))
        exit(1)
    else:
        logging.info('Script finished successfully. {} events have been sent. {} events have not been sent'.format(sentinel.successfull_sent_events_number, sentinel.failed_sent_events_number))



def get_stream_pos_and_date_from(marker, max_period_minutes, script_execution_interval_minutes):
    """Returns last saved checkpoint. If last checkpoint is older than max_period_minutes - returns now - script_execution_interval_minutes."""

    def get_default_date_from(script_execution_interval_minutes):
        date_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=script_execution_interval_minutes)
        date_from = date_from.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0).isoformat()
        return date_from

    def get_token_from_marker(marker, max_period_minutes):
        token = 0
        try:
            last_token, last_event_date = marker.split()
            last_event_date = parse_date(last_event_date)
            minutes_from_last_ingested_event = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - last_event_date).seconds / 60
            if minutes_from_last_ingested_event < max_period_minutes:
                token = last_token
        except Exception:
            pass
        return token

    token = get_token_from_marker(marker, max_period_minutes)
    if token:
        date_from = None
    else:
        date_from = get_default_date_from(script_execution_interval_minutes)

    return int(token), date_from


def save_marker(state_manager, stream_position, last_event_date):
    logging.info('Saving last stream_position {} and last_event_date {}'.format(stream_position, last_event_date))
    state_manager.post(str(stream_position) + ' ' + last_event_date)


def check_if_time_is_over(start_time, interval_minutes, max_script_exec_time_minutes):
    """Returns True if function's execution time is less than interval between function executions and
    less than max azure func lifetime. In other case returns False."""

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
    @api_call
    def get_events(self, stream_position=0, stream_type=EnterpriseEventsStreamType.ADMIN_LOGS, created_after=None, created_before=None, limit=100):
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


def get_events(config_dict, created_after=None, stream_position=0):
    limit = 500
    config = JWTAuth.from_settings_dictionary(config_dict)
    client = Client(config)
    events_client = ExtendedEvents(client._session)

    while True:
        res = events_client.get_events(stream_position=stream_position, created_after=created_after, limit=limit)
        stream_position = res['next_stream_position']
        events = [event.response_object for event in res['entries']]
        yield events, stream_position
        if len(events) < limit:
            break
