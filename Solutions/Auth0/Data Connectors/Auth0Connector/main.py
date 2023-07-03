import logging
import requests
import os
import re
import json
import time
from typing import Tuple, List, Union
from datetime import datetime as dt
from datetime import timedelta

import azure.functions as func
from Auth0Connector.sentinel_connector import AzureSentinelConnector
from Auth0Connector.state_manager import StateManager


WORKSPACE_ID = os.environ['WorkspaceID']
SHARED_KEY = os.environ['WorkspaceKey']

FILE_SHARE_CONNECTION_STRING = os.environ['AzureWebJobsStorage']
LOG_TYPE = 'Auth0AM'

MAX_SCRIPT_EXEC_TIME_MINUTES = 5
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")

DOMAIN = os.environ['DOMAIN']
API_PATH = '/api/v2/logs'
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
AUDIENCE = DOMAIN + '/api/v2/'


def main(mytimer: func.TimerRequest):
    logging.info('Script started.')
    state_manager = StateManager(FILE_SHARE_CONNECTION_STRING, file_path='auth0_confing.json')
    config_string = state_manager.get()
    if config_string:
        config = json.loads(config_string)
    else:
        config = json.loads('{"last_log_id": "","last_date": ""}')
    logging.info(f'Config loaded\n\t{config}')
    connector = Auth0Connector(DOMAIN, API_PATH, CLIENT_ID, CLIENT_SECRET, AUDIENCE)
    last_log_id, events = connector.get_log_events(config)

    config['last_log_id'] = last_log_id
    try:
        config['last_date'] = events[0]['date'] if last_log_id else config['last_date']
    except IndexError:
        pass
    logging.info("new config" + str(config))
    state_manager.post(json.dumps(config))
    sentinel = AzureSentinelConnector(LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, LOG_TYPE, queue_size=1000)
    for el in events:
        sentinel.send(el)
    sentinel.flush()
    logging.info('Events sent to Sentinel.')


class Auth0Connector:
    def __init__(self, domain, api_path, client_id, client_secret, audience):
        self.domain = domain
        self.api_path = api_path
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience
        self.uri = self.domain + self.api_path
        self.token = None
        self.header = None

    def get_log_events(self, config: dict) -> Tuple[str, List]:
        self.token = self._get_token()
        logging.info(f'Token provided.')
        self.header = self._get_header()
        last_log_id = self._get_last_log_id(config)
        #last_log_id = "90020230126121002244690048186607762971591195832157732866"
        logging.info(f'\tLast log id extracted: {last_log_id}.')
        if last_log_id is None:
            return '', []
        # first request
        params = {'from': last_log_id, 'take': '100'}
        resp = requests.get(self.uri, headers=self.header, params=params)
        logging.info('\tFirst request executed.')
        if not resp.json():
            return last_log_id, []
        events = resp.json()
        logging.info('\t response object : {events}')
        if "Link" in resp.headers :
            next_link = resp.headers['Link']
            next_uri = next_link[next_link.index('<') + 1:next_link.index('>')]
            page_num = 1
            while resp.json():
                resp = requests.get(next_uri, headers=self.header)
                #logging.info(f'\t Response message {resp.headers}')
                try:
                    next_link = resp.headers['Link']
                    next_uri = next_link[next_link.index('<') + 1:next_link.index('>')]
                    events.extend(resp.json())
                    logging.info(f'\t#{page_num} extracted')
                    page_num += 1
                    if page_num % 9 == 0:
                        time.sleep(1)
                except:
                    logging.info(f'Next link is not available, exiting')
                    break            
        events.sort(key=lambda item: item['date'], reverse=True)
        last_log_id = events[0]['log_id']
        logging.info(f'\t New last log id: {last_log_id}\n at date {events[0]["date"]}. Events extracted.')
        return last_log_id, events

    def _get_last_log_id(self, config: dict) -> Union[str, None]:
        if config['last_log_id'] == '':
            start_time = str(dt.now() - timedelta(hours=1))
            # start_time = '2022-04-06T14:45:15.861Z'
            params = {'q': f'date:[{start_time} TO {str(dt.now())}]',
                      'sort': 'date:1'}
            resp = requests.get(self.uri, headers=self.header, params=params)
            if not resp.json():
                return None
            last_log_id = resp.json()[0]['log_id']
        else:
            last_log_id = config['last_log_id']
        return last_log_id

    def _get_token(self):
        params = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'audience': self.audience
            }
        header = {'content-type': "application/x-www-form-urlencoded"}
        resp = requests.post(self.domain + '/oauth/token', headers=header, data=params)
        try:
            token = resp.json()['access_token']
        except KeyError:
            raise Exception('Token not provided.')
        return token

    def _get_header(self):
        return {'Authorization': 'Bearer ' + self.token}
