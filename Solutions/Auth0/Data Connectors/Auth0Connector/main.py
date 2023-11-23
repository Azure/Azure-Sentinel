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
retry = 3
error=False 


def main(mytimer: func.TimerRequest):
    logging.info('Script started.')
    script_start_time = int(time.time())
    state_manager = StateManager(FILE_SHARE_CONNECTION_STRING, file_path='auth0_confing.json')
    config_string = state_manager.get()
    if config_string:
        config = json.loads(config_string)
    else:
        config = json.loads('{"last_log_id": "","last_date": ""}')
    logging.info(f'Config loaded\n\t{config}')
    connector = Auth0Connector(DOMAIN, API_PATH, CLIENT_ID, CLIENT_SECRET, AUDIENCE)
    connector.get_log_events(script_start_time, config)
    logging.info(f'Finish script.')

class Auth0Connector:
    def __init__(self, domain, api_path, client_id, client_secret, audience):
        self.state_manager = StateManager(FILE_SHARE_CONNECTION_STRING, file_path='auth0_confing.json')
        self.sentinel = AzureSentinelConnector(LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, LOG_TYPE, queue_size=1000)
        self.domain = domain
        self.api_path = api_path
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience
        self.uri = self.domain + self.api_path
        self.token = None
        self.header = None
        self.retry = retry  

    """This method is used to process and post the results to Log Analytics Workspace
        Returns:
            last_log_id : last processed eventId
            events: last processed Events
    """
    def get_log_events(self, script_start_time, config: dict) -> Tuple[str, List]:
        self.token = self._get_token()
        logging.info(f'Token provided.')
        self.header = self._get_header()
        last_log_id = self._get_last_log_id(config)
        #last_log_id = "90020230126121002244690048186607762971591195832157732866"
        logging.info(f'\tLast log id extracted: {last_log_id}.')
        if last_log_id is None:
            #return '', []
            self.update_statemarker_file(config, '', [])
            return
        # first request
        params = {'from': last_log_id, 'take': '100'}
        count = 0
        error=True
        while error:
            try:
                error=False
                resp = requests.get(self.uri, headers=self.header, params=params)
            except Exception as err:
                error = True
                count+=1
                logging.error("Something wrong. Exception error text: {}".format(err))
                if count > self.retry:
                    logging.error("Exceeded maximum Retries")
                    break
        logging.info('\tFirst request executed.')
        if not resp.json():
            #return last_log_id, []
            self.update_statemarker_file(config, last_log_id, [])
            return
        events = resp.json()
        logging.info('\t response object : {events}')
        events.sort(key=lambda item: item['date'], reverse=True)
        last_log_id = events[0]['log_id']
        for el in events:
            self.sentinel.send(el)
        self.sentinel.flush()
        logging.info('Events sent to Sentinel.')
        self.update_statemarker_file(config, last_log_id , events)

        if "Link" in resp.headers :
            next_link = resp.headers['Link']
            next_uri = next_link[next_link.index('<') + 1:next_link.index('>')]
            page_num = 1
            while resp.json() and len(events)!=0:
                count = 0
                error=True
                while error:
                    try:
                        error=False
                        resp = requests.get(next_uri, headers=self.header)
                    except Exception as err:
                        error = True
                        count+=1
                        logging.error("Something wrong. Exception error text: {}".format(err))
                        if count > self.retry:
                            logging.error("Exceeded maximum Retries")
                            break
                #logging.info(f'\t Response message {resp.headers}')
                try:
                    next_link = resp.headers['Link']
                    next_uri = next_link[next_link.index('<') + 1:next_link.index('>')]
                    events = resp.json()
                    logging.info(f'\t#{page_num} extracted')
                    page_num += 1
                    if page_num % 9 == 0:
                        time.sleep(1)
                    if len(events)!=0:
                        events.sort(key=lambda item: item['date'], reverse=True)
                        last_log_id = events[0]['log_id']
                        
                        for el in events:
                            self.sentinel.send(el)
                        self.sentinel.flush()

                        self.update_statemarker_file(config, last_log_id , events)

                    if self.check_if_script_runs_too_long(script_start_time):
                        logging.info(f'Script is running too long. Stop processing new events. Finish script.')
                        break
                except Exception as err:
                    logging.error("Something wrong. Exception error text: {}".format(err))
                    break           
        #logging.info(f'\t New last log id: {last_log_id}\n at date {events[0]["date"]}. Events extracted.')
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
        count = 0
        error=True
        while error:
            try:
                error=False
                resp = requests.post(self.domain + '/oauth/token', headers=header, data=params)
                try:
                    token = resp.json()['access_token']
                except KeyError:
                    raise Exception('Token not provided.')
            except Exception as err:
                error = True
                count+=1
                if count > self.retry:
                    break
        return token

    def _get_header(self):
        return {'Authorization': 'Bearer ' + self.token}
    
    def check_if_script_runs_too_long(self, script_start_time: int) -> bool:
        now = int(time.time())
        duration = now - script_start_time
        max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.80)
        return duration > max_duration

    """This method is used to update the statemareker file with lastprocessed event details
    """
    def update_statemarker_file(self, config, last_log_id, events):
        config['last_log_id'] = last_log_id
        try:
            config['last_date'] = events[0]['date'] if last_log_id else config['last_date']
        except IndexError:
            logging.info('Known Indexing Scenario. Proceed with execution')
        logging.info("new config" + str(config))
        self.state_manager.post(json.dumps(config))


        
