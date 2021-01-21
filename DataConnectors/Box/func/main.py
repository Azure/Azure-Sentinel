import os
import json
import datetime
from boxsdk.auth.jwt_auth import JWTAuth
from boxsdk import Client
from boxsdk.object.events import Events, EnterpriseEventsStreamType
from boxsdk.util.api_call_decorator import api_call
from .sentinel_connector import AzureSentinelConnector
import azure.functions as func
import logging


WORKSPACE_ID = os.environ['AzureSentinelWorkspaceId']
SHARED_KEY = os.environ['AzureSentinelSharedKey']
LOG_TYPE = 'BoxEvents'
TIME_INTERVAL_MINUTES = 2


def main(mytimer: func.TimerRequest):
    config_json = os.environ['BOX_CONFIG_JSON']
    config_dict = json.loads(config_json)

    created_after, created_before = get_time_interval(TIME_INTERVAL_MINUTES, delay=1)
    logging.info('Script started. Getting events from {} to {}'.format(created_after, created_before))

    sentinel = AzureSentinelConnector(workspace_id=WORKSPACE_ID, shared_key=SHARED_KEY, log_type=LOG_TYPE, queue_size=10000)
    with sentinel:
        for n, event in enumerate(get_events(config_dict, created_after, created_before), start=1):
            sentinel.send(event)

    if sentinel.failed_sent_events_number:
        logging.error('Script finished unsuccessfully. {} events have been sent. {} events have not been sent'.format(sentinel.successfull_sent_events_number, sentinel.failed_sent_events_number))
        exit(1)
    else:
        logging.info('Script finished successfully. {} events have been sent. {} events have not been sent'.format(sentinel.successfull_sent_events_number, sentinel.failed_sent_events_number))


def get_time_interval(interval, delay=1):
        ts_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=interval + delay)
        ts_to = datetime.datetime.utcnow() - datetime.timedelta(minutes=delay)
        ts_from = ts_from.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0).isoformat()
        ts_to = ts_to.replace(tzinfo=datetime.timezone.utc, second=0, microsecond=0).isoformat()
        return ts_from, ts_to


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


def get_events(config_dict, created_after, created_before):
    limit = 500
    config = JWTAuth.from_settings_dictionary(config_dict)
    client = Client(config)
    events_client = ExtendedEvents(client._session)

    events = events_client.get_events(created_after=created_after, created_before=created_before, limit=limit)
    for event in events['entries']:
        yield event.response_object
    next_stream_position = events['next_stream_position']

    while next_stream_position:
        events = events_client.get_events(stream_position=next_stream_position, created_before=created_before, limit=limit)
        for event in events['entries']:
            yield event.response_object
        next_stream_position = events['next_stream_position']
        if len(events['entries']) < limit:
            break
