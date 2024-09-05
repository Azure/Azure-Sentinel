import json
import os
from google.cloud.logging_v2 import Client
import datetime
import logging
import re
import time
import azure.functions as func
from dateutil.parser import parse as parse_date
from google.api_core.exceptions import TooManyRequests
from google.api_core.retry import Retry

from .sentinel_connector import AzureSentinelConnector
from .state_manager import StateManager


CREDENTIALS_FILE_CONTENT = os.environ['CREDENTIALS_FILE_CONTENT']
RESOURCE_NAMES = os.environ['RESOURCE_NAMES']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
SHARED_KEY = os.environ['SHARED_KEY']
LOG_TYPE = 'GCP_DNS'


# interval of script execution
SCRIPT_EXECUTION_INTERVAL_MINUTES = 10
# if ts of last processed file is older than "now - MAX_PERIOD_MINUTES" then script will get events from "now - MAX_PERIOD_MINUTES"
MAX_PERIOD_MINUTES = 60 * 24 * 7

MAX_SCRIPT_EXEC_TIME_MINUTES = 10


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


CREDS_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.creds')


logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


def main(mytimer: func.TimerRequest):
    logging.info('Starting script')

    start_ts = int(time.time())

    create_credentials_file()

    gcp_cli = Client(_use_grpc=False)
    sentinel = AzureSentinelConnector(log_analytics_uri=LOG_ANALYTICS_URI, workspace_id=WORKSPACE_ID, shared_key=SHARED_KEY, log_type=LOG_TYPE, queue_size=3000)
    state_manager = StateManager(os.environ['AzureWebJobsStorage'])

    last_ts = get_last_ts(state_manager)

    filt = """
        (protoPayload.serviceName="dns.googleapis.com" OR resource.type="dns_query") AND
        timestamp>="{}"
    """.format(last_ts)

    last_ts = None
    with sentinel:
        # Retry logic with exponential backoff for handling 429 errors
        retry = Retry(
            predicate=lambda exc: isinstance(exc, TooManyRequests),
            initial=1.0,
            maximum=30.0,
            multiplier=2.0,
        )
        try:
            entries = gcp_cli.list_entries(
                resource_names=get_recource_names(),
                filter_=filt,
                order_by='timestamp',
                page_size=1000,
                retry=retry  # Apply retry settings
            )
            for entry in entries:
                event = parse_entry(entry)
                sentinel.send(event)
                last_ts = event['timestamp']
                if sentinel.is_empty():
                    logging.info('Saving last timestamp - {}'.format(last_ts))
                    state_manager.post(last_ts)
                    if check_if_script_runs_too_long(start_ts):
                        logging.info(
                            'Script is running too long. Saving progress and exit.')
                        break
        except TooManyRequests as e:
            logging.error(
                f"Encountered a 429 error: {str(e)}. Retrying with exponential backoff...")

    if last_ts:
        last_ts = event['timestamp']
        logging.info('Saving last timestamp - {}'.format(last_ts))
        state_manager.post(last_ts)

    remove_credentials_file()
    logging.info('Script finished. Sent events number: {}'.format(sentinel.successfull_sent_events_number))


def create_credentials_file():
    with open(CREDS_FILE_PATH, 'w') as f:
        content = CREDENTIALS_FILE_CONTENT.strip().replace('\n', '\\n')
        f.write(content)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDS_FILE_PATH
    
    
def list_entries_with_backoff(client, resource_names, filter_, order_by, page_size):
    max_retries = 5
    retry_delay = 1  # initial delay in seconds
    max_delay = 32  # maximum delay in seconds

    for attempt in range(max_retries):
        try:
            return client.list_entries(resource_names=resource_names, filter_=filter_, order_by=order_by, page_size=page_size)
        except Exception as e:
            if e.code() == 429:  # Quota exceeded
                logging.warning(f"Quota exceeded. Retrying in {retry_delay} seconds.")
                time.sleep(retry_delay + random.random())  # add some jitter to the delay
                retry_delay *= 2  # exponential backoff
                if retry_delay > max_delay:
                    retry_delay = max_delay
            else:
                raise

    logging.error(f"Failed to list entries after {max_retries} retries.")
    return []


def remove_credentials_file():
    if os.path.exists(CREDS_FILE_PATH):
        os.remove(CREDS_FILE_PATH)


def get_recource_names():
    return [x for x in RESOURCE_NAMES.split(',') if x]


def parse_entry(entry):
    event = entry._asdict()
    if isinstance(event.get('timestamp'), datetime.datetime):
        event['timestamp'] = event['timestamp'].isoformat()
    if 'logger' in event:
        del event['logger']
    if event.get('resource'):
        event['resource'] = event['resource']._asdict()
    return event


def get_last_ts(state_manager: StateManager):
    logging.info('Getting last timestamp')
    last_ts = state_manager.get()
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    if last_ts:
        last_ts = parse_date(last_ts)
        logging.info('Last timestamp - {}'.format(last_ts.isoformat()))
    else:
        last_ts = now - datetime.timedelta(minutes=SCRIPT_EXECUTION_INTERVAL_MINUTES)
        logging.info('Last timestamp is not known')

    diff_seconds = (now - last_ts).days * 86400 + (now - last_ts).seconds
    if diff_seconds > MAX_PERIOD_MINUTES * 60:
        old_last_ts = last_ts
        last_ts = now - datetime.timedelta(minutes=MAX_PERIOD_MINUTES)
        logging.info('Last timestamp {} is older than max search period ({} minutes). Getting data for max search period (from {})'.format(old_last_ts, MAX_PERIOD_MINUTES, last_ts))
    else:
        last_ts += datetime.timedelta(microseconds=1)
        logging.info('Getting data from {}'.format(last_ts.isoformat()))

    return last_ts.isoformat()


def check_if_script_runs_too_long(start_ts):
    now = int(time.time())
    duration = now - start_ts
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.85)
    return duration > max_duration