import snowflake.connector
from snowflake.connector import DictCursor
import datetime
from typing import Iterable
from dateutil.parser import parse as parse_datetime
import logging
import os
import re
import time
import azure.functions as func

from .sentinel_connector import AzureSentinelConnector
from .state_manager import StateManager


logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)
logging.getLogger('snowflake.connector').setLevel(logging.ERROR)


SNOWFLAKE_ACCOUNT = os.environ['SNOWFLAKE_ACCOUNT']
SNOWFLAKE_USER = os.environ['SNOWFLAKE_USER']
SNOWFLAKE_PASSWORD = os.environ['SNOWFLAKE_PASSWORD']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
SHARED_KEY = os.environ['SHARED_KEY']
FILE_SHARE_CONN_STRING = os.environ['AzureWebJobsStorage']
LOG_TYPE = 'Snowflake'

MAX_SCRIPT_EXEC_TIME_MINUTES = 5

LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


def main(mytimer: func.TimerRequest):
    logging.info('Script started.')
    script_start_time = int(time.time())
    ctx = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT
    )
    sentinel = AzureSentinelConnector(
        log_analytics_uri=LOG_ANALYTICS_URI,
        workspace_id=WORKSPACE_ID,
        shared_key=SHARED_KEY,
        log_type=LOG_TYPE,
        queue_size=1000
    )
    state_manager_logins = StateManager(FILE_SHARE_CONN_STRING, file_path='snowflake_logins')
    state_manager_queries = StateManager(FILE_SHARE_CONN_STRING, file_path='snowflake_queries')
    state_manager_rlogins = StateManager(FILE_SHARE_CONN_STRING, file_path='snowflake_rlogins')
    state_manager_rqueries = StateManager(FILE_SHARE_CONN_STRING, file_path='snowflake_rqueries')

    logins_date_from = state_manager_logins.get()
    logins_date_from = parse_date_from(logins_date_from)
    logging.info(f'Getting LOGIN events from {logins_date_from}')
    last_ts = None
    for event in get_login_events(ctx, logins_date_from):
        sentinel.send(event)
        last_ts = event.get('EVENT_TIMESTAMP')
        if sentinel.is_empty() and last_ts:
            state_manager_logins.post(last_ts)
            if check_if_script_runs_too_long(script_start_time):
                logging.info(f'Script is running too long. Stop processing new events. Finish script. Sent events: {sentinel.successfull_sent_events_number}')
                return
    sentinel.flush()
    if last_ts:
        state_manager_logins.post(last_ts)
    
    if check_if_script_runs_too_long(script_start_time):
        logging.info(f'Script is running too long. Stop processing new events. Finish script. Sent events: {sentinel.successfull_sent_events_number}')
        return

    queries_date_from = state_manager_queries.get()
    queries_date_from = parse_date_from(queries_date_from)
    logging.info(f'Getting QUERIES events from {queries_date_from}')
    last_ts = None
    for event in get_query_events(ctx, queries_date_from):
        sentinel.send(event)
        last_ts = event.get('START_TIME')
        if sentinel.is_empty() and last_ts:
            state_manager_queries.post(last_ts)
            if check_if_script_runs_too_long(script_start_time):
                logging.info(f'Script is running too long. Stop processing new events. Finish script. Sent events: {sentinel.successfull_sent_events_number}')
                return
    sentinel.flush()
    if last_ts:
        state_manager_queries.post(last_ts)

    if check_if_script_runs_too_long(script_start_time):
        logging.info(f'Script is running too long. Stop processing new events. Finish script. Sent events: {sentinel.successfull_sent_events_number}')
        return

    rlogins_date_from = state_manager_rlogins.get()
    rlogins_date_from = parse_date_from(rlogins_date_from)
    logging.info(f'Getting READER LOGIN events from {rlogins_date_from}')
    last_ts = None
    for event in get_reader_login_events(ctx, rlogins_date_from):
        sentinel.send(event)
        last_ts = event.get('EVENT_TIMESTAMP')
        if sentinel.is_empty() and last_ts:
            state_manager_rlogins.post(last_ts)
            if check_if_script_runs_too_long(script_start_time):
                logging.info(f'Script is running too long. Stop processing new events. Finish script. Sent events: {sentinel.successfull_sent_events_number}')
                return
    sentinel.flush()
    if last_ts:
        state_manager_rlogins.post(last_ts)

    if check_if_script_runs_too_long(script_start_time):
        logging.info(f'Script is running too long. Stop processing new events. Finish script. Sent events: {sentinel.successfull_sent_events_number}')
        return

    rqueries_date_from = state_manager_rqueries.get()
    rqueries_date_from = parse_date_from(rqueries_date_from)
    logging.info(f'Getting READER QUERIES events from {rqueries_date_from}')
    last_ts = None
    for event in get_reader_query_events(ctx, rqueries_date_from):
        sentinel.send(event)
        last_ts = event.get('START_TIME')
        if sentinel.is_empty() and last_ts:
            state_manager_rqueries.post(last_ts)
            if check_if_script_runs_too_long(script_start_time):
                logging.info(f'Script is running too long. Stop processing new events. Finish script. Sent events: {sentinel.successfull_sent_events_number}')
                return
    sentinel.flush()
    if last_ts:
        state_manager_rqueries.post(last_ts)

    if check_if_script_runs_too_long(script_start_time):
        logging.info(f'Script is running too long. Stop processing new events. Finish script. Sent events: {sentinel.successfull_sent_events_number}')
        return
    
    ctx.close()
    logging.info(f'Script finished. Sent events: {sentinel.successfull_sent_events_number}')


def parse_date_from(date_from: str) -> datetime.datetime:
    try:
        date_from = parse_datetime(date_from)
    except:
        pass
    if not isinstance(date_from, datetime.datetime):
        date_from = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=1)
    return date_from


def get_login_events(ctx: snowflake.connector.SnowflakeConnection, date_from: datetime.datetime) -> Iterable[dict]:
    cs = ctx.cursor(DictCursor)
    try:
        cs.execute("use schema snowflake.account_usage")
        cs.execute(f"SELECT * from LOGIN_HISTORY WHERE EVENT_TIMESTAMP > '{date_from.isoformat()}' ORDER BY EVENT_TIMESTAMP ASC")
        for row in cs:
            row = parse_login_event(row)
            yield row
    finally:
        cs.close()


def get_reader_login_events(ctx: snowflake.connector.SnowflakeConnection, date_from: datetime.datetime) -> Iterable[dict]:
    cs = ctx.cursor(DictCursor)
    try:
        cs.execute("use schema snowflake.reader_account_usage")
        cs.execute(f"SELECT * from LOGIN_HISTORY WHERE EVENT_TIMESTAMP > '{date_from.isoformat()}' ORDER BY EVENT_TIMESTAMP ASC")
        for row in cs:
            row = parse_login_event(row)
            yield row
    finally:
        cs.close()


def get_query_events(ctx: snowflake.connector.SnowflakeConnection, date_from: datetime.datetime) -> Iterable[dict]:
    cs = ctx.cursor(DictCursor)
    try:
        cs.execute("use schema snowflake.account_usage")
        cs.execute(f"SELECT * from QUERY_HISTORY WHERE START_TIME > '{date_from.isoformat()}' ORDER BY START_TIME ASC")
        for row in cs:
            row = parse_query_event(row)
            yield row
    finally:
        cs.close()


def get_reader_query_events(ctx: snowflake.connector.SnowflakeConnection, date_from: datetime.datetime) -> Iterable[dict]:
    cs = ctx.cursor(DictCursor)
    try:
        cs.execute("use schema snowflake.reader_account_usage")
        cs.execute(f"SELECT * from QUERY_HISTORY WHERE START_TIME > '{date_from.isoformat()}' ORDER BY START_TIME ASC")
        for row in cs:
            row = parse_query_event(row)
            yield row
    finally:
        cs.close()


def parse_login_event(event: dict) -> dict:
    if 'EVENT_TIMESTAMP' in event and isinstance(event['EVENT_TIMESTAMP'], datetime.datetime):
        event['EVENT_TIMESTAMP'] = event['EVENT_TIMESTAMP'].isoformat()
    event['source_table'] = 'LOGIN_HISTORY'
    return event


def parse_query_event(event: dict) -> dict:
    if 'START_TIME' in event and isinstance(event['START_TIME'], datetime.datetime):
        event['START_TIME'] = event['START_TIME'].isoformat()
    if 'END_TIME' in event and isinstance(event['END_TIME'], datetime.datetime):
        event['END_TIME'] = event['END_TIME'].isoformat()
    event['source_table'] = 'QUERY_HISTORY'
    return event


def check_if_script_runs_too_long(script_start_time: int) -> bool:
        now = int(time.time())
        duration = now - script_start_time
        max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.85)
        return duration > max_duration
