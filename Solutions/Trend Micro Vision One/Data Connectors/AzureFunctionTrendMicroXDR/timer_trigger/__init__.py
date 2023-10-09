import logging
import typing
import json

import os
import azure.functions as func
import jwt

from datetime import datetime, timedelta
from azure.cosmosdb.table.tableservice import TableService
from azure.common import AzureMissingResourceHttpError
from requests.exceptions import HTTPError

from shared_code import configurations, utils
from shared_code.data_collector import LogAnalytics
from shared_code.services.workbench_service import get_workbench_list

WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
API_TOKENS = configurations.get_api_tokens()
STORAGE_CONNECTION_STRING = configurations.get_storage_connection_string()
MAX_WORKBENCH_QUERY_MINUTES = configurations.get_max_workbench_query_minutes()
DEFAULT_WORKBENCH_QUERY_MINUTES = configurations.get_default_workbench_query_minutes()
DATETIME_FORMAT = configurations.get_datetime_format()
LOG_TYPE = configurations.get_health_check_log_type()

TABLE_NAME = 'XdrConnectorStatus'
PARTITION_KEY = 'last_success_time'


def get_last_success_time(table_service, clp_id):
    table_service.create_table(TABLE_NAME)
    try:
        entity = table_service.get_entity(TABLE_NAME, PARTITION_KEY, clp_id)
        return datetime.strptime(entity.last_success_time, DATETIME_FORMAT)
    except AzureMissingResourceHttpError:
        return None


def update_last_success_time(table_service, clp_id, time):
    table_service.insert_or_merge_entity(
        TABLE_NAME,
        {
            'PartitionKey': PARTITION_KEY,
            'RowKey': clp_id,
            'last_success_time': time.strftime(DATETIME_FORMAT),
        },
    )


def generate_time(table_service, clp_id):
    end_time = datetime.utcnow()
    start_time = get_last_success_time(table_service, clp_id)
    if start_time is None:
        start_time = end_time - timedelta(minutes=DEFAULT_WORKBENCH_QUERY_MINUTES)
    elif start_time + timedelta(minutes=MAX_WORKBENCH_QUERY_MINUTES) < end_time:
        end_time = start_time + timedelta(minutes=MAX_WORKBENCH_QUERY_MINUTES)

    return start_time, end_time


def build_queue_message(clp_id, workbench_record):
    return json.dumps({'clp_id': clp_id, 'workbench_record': workbench_record})


def main(mytimer: func.TimerRequest, wbMsg: func.Out[typing.List[str]]) -> None:
    table_service = TableService(connection_string=STORAGE_CONNECTION_STRING)
    log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, LOG_TYPE)
    error = None

    for token in API_TOKENS:
        try:
            health_check_data = {}
            clp_id = utils.get_clp_id(token)
            health_check_data['clpId'] = clp_id

            start_time, end_time = generate_time(table_service, clp_id)
            start_time_str = start_time.strftime(DATETIME_FORMAT)
            end_time_str = end_time.strftime(DATETIME_FORMAT)
            health_check_data['queryStartTime'] = start_time_str
            health_check_data['queryEndTime'] = end_time_str

            logging.info(
                f'start to poll workbench events from {start_time_str} to {end_time_str}.'
            )

            # get workbench ids
            total_count, workbench_records = get_workbench_list(
                token, start_time_str, end_time_str
            )
            while total_count > len(workbench_records):
                workbench_records.extend(
                    get_workbench_list(
                        token, start_time_str, end_time_str, len(workbench_records)
                    )[1]
                )

            logging.debug(f'workbench_records: {workbench_records}')
            logging.info(f'{total_count} workbench events received.')

            wbMsg.set(
                [
                    build_queue_message(clp_id, workbench_record)
                    for workbench_record in workbench_records
                ]
            )

            update_last_success_time(table_service, clp_id, end_time)

            health_check_data['newWorkbenchCount'] = len(workbench_records)
        except HTTPError as e:
            logging.exception(
                f'Fail to get workbench list! Exception: {e}',
            )
            error, health_check_data['error'] = e, str(e)
        except Exception as e:
            logging.exception('Internal error.')
            error, health_check_data['error'] = e, str(e)
        finally:
            # send heatch check log to log analytics
            log_analytics.post_data(health_check_data)

    if error:
        raise error
