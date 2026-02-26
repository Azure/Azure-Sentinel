import os
import asyncio
import logging
import time
import re
import aiohttp
import azure.functions as func
from google.cloud.monitoring_v3.services.metric_service import MetricServiceAsyncClient
from google.cloud.monitoring_v3.types import TimeInterval
from google.cloud.monitoring_v3.types import TimeSeries
from google.protobuf.json_format import MessageToDict

from .sentinel_connector_async import AzureSentinelConnectorAsync
from .state_manager import StateManager


logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


CREDENTIALS_FILE_CONTENT = os.environ['GCP_CREDENTIALS_FILE_CONTENT']
GCP_PROJECT_ID_LIST = os.environ['GCP_PROJECT_ID']
METRICS = os.environ['GCP_METRICS']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
SHARED_KEY = os.environ['SHARED_KEY']
LOG_TYPE = 'GCP_MONITORING'
CREDS_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.creds')

MAX_SEARCH_PERIOD_MINUTES = 120
DEFAULT_SEARCH_PERIOD_MINUTES = 5


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


async def main(mytimer: func.TimerRequest):
    logging.info('Starting script')

    create_credentials_file()

    projects = GCP_PROJECT_ID_LIST.split()
    metrics = METRICS.split()

    state_manager = StateManager(os.environ['AzureWebJobsStorage'])

    logging.info('Getting last timestamp')
    last_ts = state_manager.get()
    logging.info('Last timestamp: {}'.format(last_ts))

    time_interval, last_ts = gen_time_interval(last_ts)

    async with aiohttp.ClientSession() as session:
        cors = []
        client = MetricServiceAsyncClient()
        for project in projects:
            for metric in metrics:
                cors.append(process_metric(client, project, metric, time_interval, session))
        
        await asyncio.gather(*cors)

    logging.info('Saving last timestamp: {}'.format(last_ts))
    state_manager.post(str(last_ts))
    remove_credentials_file()

    logging.info('Script finished')


def gen_time_interval(last_ts: int):
    now = int(time.time())

    if last_ts:
        try:
            last_ts = int(last_ts)
        except Exception:
            last_ts = None

    if last_ts:
        last_ts = int(last_ts)
        if now - last_ts < MAX_SEARCH_PERIOD_MINUTES * 60:
            start_time = last_ts
            logging.info('Getting data from {}'.format(start_time))
        else:
            start_time = now - MAX_SEARCH_PERIOD_MINUTES * 60
            logging.warning('Last timestamp is too old. Getting data from {}'.format(start_time))
    else:
        start_time = now -  DEFAULT_SEARCH_PERIOD_MINUTES * 60
        logging.info('Last timestamp is not known. Getting data from {}'.format(start_time))
    
    end_time = now - 30

    interval = {
        "start_time": {"seconds": start_time, "nanos": 0},
        "end_time": {"seconds": end_time, "nanos": 0}
    }
    logging.info('Getting data for interval: {}'.format(interval))
    return TimeInterval(interval), end_time


async def process_metric(client: MetricServiceAsyncClient, project_name: str, metric_type: str, time_interval: TimeInterval, session_sentinel: aiohttp.ClientSession):
    logging.info('Start processing metric: {} in {}'.format(metric_type, project_name))

    sentinel = AzureSentinelConnectorAsync(session_sentinel, LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, LOG_TYPE, queue_size=10000)

    metric_string = 'metric.type = ' + '"' + metric_type + '"'

    time_series_async_iterator = await client.list_time_series(name=project_name, filter=metric_string, interval=time_interval)
    async for time_series in time_series_async_iterator:
        async for event in parse_time_series(time_series):
            await sentinel.send(event)

    await sentinel.flush()

    logging.info('Finish processing metric: {} in {}. Sent events: {}'.format(metric_type, project_name, sentinel.successfull_sent_events_number))


async def parse_time_series(time_series: TimeSeries):
    d = MessageToDict(time_series._pb)
    points = d.pop('points', [])

    for p in points:
        p = parse_point(p)
        event = {}
        event.update(d)
        event.update(p)
        yield event


def parse_bool(val):
    if val == 'true':
        val = True
    elif val == 'false':
        val = False
    return val


def parse_point(point: dict):
    parse_functions = {
        'boolValue': parse_bool,
        'int64Value': int,
        'doubleValue': float
    }

    if 'value' in point:
        for field in point['value']:
            if field in parse_functions:
                try:
                    val = point['value'][field]
                    func = parse_functions[field]
                    point['value'][field] = func(val)
                except Exception:
                    pass

    return point


def create_credentials_file():
    with open(CREDS_FILE_PATH, 'w') as f:
        content = CREDENTIALS_FILE_CONTENT.strip().replace('\n', '\\n')
        f.write(content)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDS_FILE_PATH


def remove_credentials_file():
    if os.path.exists(CREDS_FILE_PATH):
        os.remove(CREDS_FILE_PATH)
