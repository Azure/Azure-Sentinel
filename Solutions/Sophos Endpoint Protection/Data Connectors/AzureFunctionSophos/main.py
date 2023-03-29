import os
import logging
import re
import time
import datetime
import calendar
from typing import Callable

import requests
import azure.functions as func

from .sentinel_connector import AzureSentinelConnector
from .state_manager import StateManager


TOKEN = os.environ['SOPHOS_TOKEN']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
SHARED_KEY = os.environ['SHARED_KEY']
FILE_SHARE_CONNECTION_STRING = os.environ['AzureWebJobsStorage']
LOG_TYPE = 'SophosEP'

MAX_SCRIPT_EXEC_TIME_MINUTES = 5


logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


def main(mytimer: func.TimerRequest):
    logging.info('Starting script.')
    sentinel_connector = AzureSentinelConnector(LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, LOG_TYPE, queue_size=1000)
    sophos = SophosConnector(
        token_string=TOKEN,
        file_share_connection_string=FILE_SHARE_CONNECTION_STRING,
        sentinel_connector=sentinel_connector
    )
    sophos.process_alerts()
    sophos.process_events()
    logging.info('Script finished. Sent items: {}'.format(sophos.sentinel.successfull_sent_events_number))


class Params:
    def __init__(self, cursor=None, since=None):
        self.cursor = cursor
        self.since = since

    def to_dict(self) -> dict:
        d = dict()
        if self.cursor:
            d['cursor'] = self.cursor
        else:
            d['from_date'] = self.since
        return d


class Token:
    def __init__(self, token_txt):
        rex_txt = r"url\: (?P<url>https\://.+), x-api-key\: (?P<api_key>.+), Authorization\: (?P<authorization>.+)$"
        rex = re.compile(rex_txt)
        m = rex.search(token_txt)
        self.url = m.group("url")
        self.api_key = m.group("api_key")
        self.authorization = m.group("authorization").strip()


class SophosConnector:
    def __init__(self, token_string: str, file_share_connection_string: str, sentinel_connector: AzureSentinelConnector):
        self._start_time = int(time.time())
        self.token = Token(token_string)
        self.sentinel = sentinel_connector
        self.events_state_manager = StateManager(file_share_connection_string, file_path='events_cursor.txt')
        self.alerts_state_manager = StateManager(file_share_connection_string, file_path='alerts_cursor.txt')
        self.default_since_time_hours = 24

    def _get_params(self, state_manager: StateManager) -> Params:
        cursor = state_manager.get()
        if cursor:
            params = Params(cursor=cursor)
        else:
            since = int(calendar.timegm(((datetime.datetime.utcnow() - datetime.timedelta(hours=self.default_since_time_hours)).timetuple())))
            params = Params(since=since)
        return params

    def get_events_params(self) -> Params:
        return self._get_params(self.events_state_manager)

    def get_alerts_params(self) -> Params:
        return self._get_params(self.alerts_state_manager)

    def _save_cursor(self, cursor: str, state_manager: StateManager) -> None:
        if cursor:
            state_manager.post(cursor)

    def save_events_cursor(self, cursor) -> None:
        logging.info(f'saving events cursor {cursor}')
        self._save_cursor(cursor, self.events_state_manager)

    def save_alerts_cursor(self, cursor) -> None:
        logging.info(f'saving alerts cursor {cursor}')
        self._save_cursor(cursor, self.alerts_state_manager)

    @property
    def _headers(self) -> dict:
        return {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'X-Locale': 'en',
            'Authorization': self.token.authorization,
            'x-api-key': self.token.api_key
        }

    def _get_url_params(self, params: Params) -> dict:
        url_params = {
            'limit': 1000
        }
        url_params.update(params.to_dict())
        return url_params

    def _process_endpoint(self, endpoint: str, params: Params, record_type: str, save_cursor_func: Callable) -> None:
        url = f'{self.token.url}{endpoint}'

        while True:
            if self.check_if_script_runs_too_long():
                logging.info('Script is running too long. Exit script.')
                break

            url_params = self._get_url_params(params)
            logging.info(f'Making request - url: {url}, params: {url_params}')
            res = requests.get(url, headers=self._headers, params=url_params)

            if not res.ok:
                raise Exception(f'Error while obtaining data (response code: {res.status_code}): {res.text}')

            res = res.json()

            for item in res['items']:
                item['datastream'] = record_type
                self.sentinel.send(item)

            self.sentinel.flush()

            next_cursor = res['next_cursor']
            save_cursor_func(next_cursor)

            if not res['has_more']:
                break
            else:
                params = Params(cursor=next_cursor, since=None)

    def process_events(self):
        self._process_endpoint(
            endpoint='/siem/v1/events',
            params=self.get_events_params(),
            record_type='event',
            save_cursor_func=self.save_events_cursor
        )

    def process_alerts(self):
        self._process_endpoint(
            endpoint='/siem/v1/alerts',
            params=self.get_alerts_params(),
            record_type='alert',
            save_cursor_func=self.save_alerts_cursor
        )

    def check_if_script_runs_too_long(self):
        now = int(time.time())
        duration = now - self._start_time
        max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.85)
        return duration > max_duration
