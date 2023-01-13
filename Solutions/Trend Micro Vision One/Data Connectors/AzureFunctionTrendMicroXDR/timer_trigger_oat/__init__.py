import logging
import typing

import azure.functions as func

from datetime import datetime, timedelta
from azure.cosmosdb.table.tableservice import TableService
from azure.common import AzureMissingResourceHttpError
from requests.exceptions import HTTPError

from shared_code import configurations, utils
from shared_code.data_collector import LogAnalytics
from shared_code.models.oat import OATDetectionResult, OATQueueMessage
from shared_code.services.oat_service import get_oat_list

WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
API_TOKENS = configurations.get_api_tokens()
STORAGE_CONNECTION_STRING = configurations.get_storage_connection_string()
MAX_OAT_QUERY_MINUTES = configurations.get_max_oat_query_minutes()
DEFAULT_OAT_QUERY_MINUTES = configurations.get_default_oat_query_minutes()
OAT_QUERY_TIME_BUFFER_MINUTES = configurations.get_oat_query_time_buffer_minutes()
DATETIME_FORMAT = configurations.get_datetime_format()
LOG_TYPE = configurations.get_oat_health_check_log_type()

TABLE_NAME = 'XdrOatConnectorStatus'
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
    end_time = datetime.utcnow() - timedelta(minutes=OAT_QUERY_TIME_BUFFER_MINUTES)
    start_time = get_last_success_time(table_service, clp_id)
    if start_time is None:
        start_time = end_time - timedelta(minutes=DEFAULT_OAT_QUERY_MINUTES)
    elif start_time + timedelta(minutes=MAX_OAT_QUERY_MINUTES) < end_time:
        end_time = start_time + timedelta(minutes=MAX_OAT_QUERY_MINUTES)

    return start_time, end_time


def build_queue_message(clp_id: str, oat_result: OATDetectionResult):
    return [
        OATQueueMessage(
            clp_id=clp_id,
            detections=[
                detection
                for detection in oat_result.detections
                if detection['uuid'] in post_data['query']
            ],
            post_data=post_data,
        ).json()
        for post_data in oat_result.search_api_post_data
    ]


def main(mytimer: func.TimerRequest, msg: func.Out[typing.List[str]]) -> None:
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
                f'start to poll oat events from {start_time_str} to {end_time_str}.'
            )

            messages = []

            # get oat list
            oat_result = get_oat_list(token, start_time, end_time)

            messages.extend(build_queue_message(clp_id, oat_result))
            while oat_result.next_batch_token:
                oat_result = get_oat_list(
                    token,
                    start_time,
                    end_time,
                    next_batch_token=oat_result.next_batch_token,
                )
                messages.extend(build_queue_message(clp_id, oat_result))

            logging.debug(f'oat detections: {oat_result.total_count}')
            logging.info(f'{oat_result.total_count} oat detections events received.')

            msg.set(messages)

            update_last_success_time(table_service, clp_id, end_time)

            health_check_data['newOatCount'] = oat_result.total_count
        except HTTPError as e:
            logging.exception(
                f'Fail to get OAT list! Exception: {e}',
            )
            error, health_check_data['error'] = e, str(e)
        except Exception as e:
            logging.exception('Internal error.')
            error, health_check_data['error'] = e, str(e)
        finally:
            # send healtch check log to log analytics
            log_analytics.post_data(health_check_data)

    if error:
        raise error
