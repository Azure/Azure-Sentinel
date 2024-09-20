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
FIELD_SIZE_LIMIT_BYTES = 1000 * 32
logging.getLogger(
    'azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


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
error = False


def main(mytimer: func.TimerRequest):
    logging.info('Script started.')
    script_start_time = int(time.time())
    state_manager = StateManager(
        FILE_SHARE_CONNECTION_STRING, file_path='auth0_confing.json')
    config_string = state_manager.get()
    if config_string:
        config = json.loads(config_string)
    else:
        config = json.loads('{"last_log_id": "","last_date": ""}')
    logging.info(f'Config loaded\n\t{config}')
    connector = Auth0Connector(
        DOMAIN, API_PATH, CLIENT_ID, CLIENT_SECRET, AUDIENCE)
    connector.get_log_events(script_start_time, config)
    logging.info(f'Finish script.')


class Auth0Connector:
    def __init__(self, domain, api_path, client_id, client_secret, audience):
        self.state_manager = StateManager(
            FILE_SHARE_CONNECTION_STRING, file_path='auth0_confing.json')
        self.sentinel = AzureSentinelConnector(
            LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, LOG_TYPE, queue_size=1000)
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
        # last_log_id = "90020230126121002244690048186607762971591195832157732866"
        logging.info(f'\tLast log id extracted: {last_log_id}.')
        if last_log_id is None:
            # return '', []
            self.update_statemarker_file(config, '', [])
            return
        # first request
        params = {'from': last_log_id, 'take': '100'}
        count = 0
        error = True
        while error:
            try:
                error = False
                resp = requests.get(
                    self.uri, headers=self.header, params=params)
                if not resp.json():
                    self.update_statemarker_file(config, last_log_id, [])
                    return
                events = resp.json()
                if 'statusCode' in events:
                    raise Exception(events['error'])
            except Exception as err:
                error = True
                count += 1
                if (err == 'Too Many Requests'):
                    time.sleep(1)
                logging.error(
                    "Something wrong. Exception error text: {}".format(err))
                if count > self.retry:
                    logging.error("Exceeded maximum Retries")
                    break
        logging.info('\tFirst request executed.')
        if not resp.json():
            # return last_log_id, []
            self.update_statemarker_file(config, last_log_id, [])
            return
        events = resp.json()
        logging.info(f'Response Object : {events}')
        events.sort(key=lambda item: item['date'], reverse=True)
        last_log_id = events[0]['log_id']
        for el in events:
            self.customize_event(el)
            self.sentinel.send(el)
        self.sentinel.flush()
        logging.info('Events sent to Sentinel.')
        self.update_statemarker_file(config, last_log_id, events)

        if "Link" in resp.headers:
            next_link = resp.headers['Link']
            next_uri = next_link[next_link.index('<') + 1:next_link.index('>')]
            page_num = 1
            while resp.json() and len(events) != 0:
                count = 0
                error = True
                while error:
                    try:
                        error = False
                        resp = requests.get(next_uri, headers=self.header)
                        events = resp.json()
                        if 'statusCode' in events:
                            raise Exception(events['error'])
                    except Exception as err:
                        error = True
                        count += 1
                        if (err == 'Too Many Requests'):
                            time.sleep(1)
                        logging.error(
                            "Something wrong. Exception error text: {}".format(err))
                        if count > self.retry:
                            logging.error("Exceeded maximum Retries")
                            break
                # logging.info(f'\t Response message {resp.headers}')
                try:
                    next_link = resp.headers['Link']
                    next_uri = next_link[next_link.index(
                        '<') + 1:next_link.index('>')]
                    events = resp.json()
                    logging.info(f'\t#{page_num} extracted')
                    page_num += 1
                    if page_num % 9 == 0:
                        time.sleep(1)
                    if len(events) != 0:
                        events.sort(
                            key=lambda item: item['date'], reverse=True)
                        last_log_id = events[0]['log_id']

                        for el in events:
                            self.customize_event(el)
                            self.sentinel.send(el)
                        self.sentinel.flush()

                        self.update_statemarker_file(
                            config, last_log_id, events)

                    if self.check_if_script_runs_too_long(script_start_time):
                        logging.info(
                            f'Script is running too long. Stop processing new events. Finish script.')
                        break
                except Exception as err:
                    logging.error(
                        "Something wrong. Exception error text: {}".format(err))
                    break
        # logging.info(f'\t New last log id: {last_log_id}\n at date {events[0]["date"]}. Events extracted.')
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
        error = True
        while error:
            try:
                error = False
                resp = requests.post(
                    self.domain + '/oauth/token', headers=header, data=params)
                try:
                    token = resp.json()['access_token']
                except KeyError:
                    raise Exception('Token not provided.')
            except Exception as err:
                error = True
                count += 1
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

    """This method is used to  limit the column count
        Returns:
            events: Updated Events
    """

    def customize_event(self, el):
        if "details" in el:
            if "body" in el["details"]:
                myjson = str(el["details"]["body"])
                if (myjson.startswith("{")):
                    if "app" in el["details"]["body"]:
                        if "metadata" in el["details"]["body"]["app"]:
                            el["details"]["body"]["app"]["metadata"] = json.dumps(
                                el["details"]["body"]["app"]["metadata"])

                    if "transaction" in el["details"]["body"]:
                        el["details"]["body"]["transaction"] = json.dumps(
                            el["details"]["body"]["transaction"])

                    if "user" in el["details"]["body"]:
                        if "metadata" in el["details"]["body"]["user"]:
                            el["details"]["body"]["user"]["metadata"] = json.dumps(
                                el["details"]["body"]["user"]["metadata"])

            if "request" in el["details"]:
                if "auth" in el["details"]["request"]:
                    el["details"]["request"]["auth"] = json.dumps(
                        el["details"]["request"]["auth"])

                if "body" in el["details"]["request"]:
                    myjson = str(el["details"]["request"]["body"])
                    if (myjson.startswith("{")):
                        if "app" in el["details"]["request"]["body"]:
                            if "metadata" in el["details"]["request"]["body"]["app"]:
                                el["details"]["request"]["body"]["app"]["metadata"] = json.dumps(
                                    el["details"]["request"]["body"]["app"]["metadata"])

                        if "client" in el["details"]["request"]["body"]:
                            el["details"]["request"]["body"]["client"] = json.dumps(
                                el["details"]["request"]["body"]["client"])

                        if "refresh" in el["details"]["request"]["body"]:
                            if "token" in el["details"]["request"]["body"]["refresh"]:
                                el["details"]["request"]["body"]["refresh"]["token"] = json.dumps(
                                    el["details"]["request"]["body"]["refresh"]["token"])

                        if "template" in el["details"]["request"]["body"]:
                            el["details"]["request"]["body"]["template"] = json.dumps(
                                el["details"]["request"]["body"]["template"])
                            details_request_body_template = el["details"]["request"]["body"]["template"]
                            if (len(json.dumps(details_request_body_template).encode()) > FIELD_SIZE_LIMIT_BYTES):
                                queue_list = self._split_big_request(
                                    details_request_body_template)
                                count = 1
                                for q in queue_list:
                                    columnname = 'templatePart' + str(count)
                                    el['details']['request']['body'][columnname] = q
                                    count += 1
                                if 'templatePart2' in el['details']['request']['body']:
                                    del el["details"]["request"]["body"]["template"]

                        if "user" in el["details"]["request"]["body"]:
                            if "metadata" in el["details"]["request"]["body"]["user"]:
                                el["details"]["request"]["body"]["user"]["metadata"] = json.dumps(
                                    el["details"]["request"]["body"]["user"]["metadata"])

            if "response" in el["details"]:
                if "body" in el["details"]["response"]:
                    myjson = str(el["details"]["response"]["body"])
                    if (myjson.startswith("{")):
                        if "app" in el["details"]["response"]["body"]:
                            if "metadata" in el["details"]["response"]["body"]["app"]:
                                el["details"]["response"]["body"]["app"]["metadata"] = json.dumps(
                                    el["details"]["response"]["body"]["app"]["metadata"])

                        if "flags" in el["details"]["response"]["body"]:
                            el["details"]["response"]["body"]["flags"] = json.dumps(
                                el["details"]["response"]["body"]["flags"])

                        if "refresh" in el["details"]["response"]["body"]:
                            if "token" in el["details"]["response"]["body"]["refresh"]:
                                el["details"]["response"]["body"]["refresh"]["token"] = json.dumps(
                                    el["details"]["response"]["body"]["refresh"]["token"])

                        if "universal" in el["details"]["response"]["body"]:
                            if "login" in el["details"]["response"]["body"]["universal"]:
                                el["details"]["response"]["body"]["universal"]["login"] = json.dumps(
                                    el["details"]["response"]["body"]["universal"]["login"])

                        if "user" in el["details"]["response"]["body"]:
                            if "metadata" in el["details"]["response"]["body"]["user"]:
                                el["details"]["response"]["body"]["user"]["metadata"] = json.dumps(
                                    el["details"]["response"]["body"]["user"]["metadata"])

                        if "bindings" in el['details']['response']['body']:
                            el['details']['response']['body']['bindings'] = json.dumps(
                                el['details']['response']['body']['bindings'])
                            details_response_body_bindings = el['details']['response']['body']['bindings']
                            if (len(json.dumps(details_response_body_bindings).encode()) > FIELD_SIZE_LIMIT_BYTES):
                                queue_list = self._split_big_request(
                                    details_response_body_bindings)
                                count = 1
                                for q in queue_list:
                                    columnname = 'bindingsPart' + str(count)
                                    el['details']['response']['body'][columnname] = q
                                    count += 1
                                if 'bindingsPart2' in el['details']['response']['body']:
                                    del el['details']['response']['body']['bindings']
        return el

    def _check_size(self, queue):
        data_bytes_len = len(json.dumps(queue).encode())
        return data_bytes_len < FIELD_SIZE_LIMIT_BYTES

    def _split_big_request(self, queue):
        if self._check_size(queue):
            return [queue]
        else:
            middle = int(len(queue) / 2)
            queues_list = [queue[:middle], queue[middle:]]
            return self._split_big_request(queues_list[0]) + self._split_big_request(queues_list[1])

    def clear_event(self, el):
        if 'details' in el and 'response' in el['details'] and 'body' in el['details']['response'] and 'bindingsPart2' in el['details']['response']['body']:
            del el['details']['response']['body']['bindings']
        if 'details' in el and 'request' in el['details'] and 'body' in el['details']['request'] and 'templatePart2' in el['details']['request']['body']:
            del el["details"]["request"]["body"]["template"]
        return el

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
