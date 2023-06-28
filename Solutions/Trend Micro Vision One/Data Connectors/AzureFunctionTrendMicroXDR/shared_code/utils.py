from datetime import datetime, timedelta, timezone

import jwt
import pytz
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.data.tables import TableClient, TableServiceClient, UpdateMode
from azure.storage.queue import QueueClient, TextBase64EncodePolicy
from shared_code import configurations
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.decorators.timer import timer

STORAGE_CONNECTION_STRING = configurations.get_storage_connection_string()
DATETIME_FORMAT = configurations.get_datetime_format()
LAST_SUCCESS_TIME_PARTITION_KEY = 'last_success_time'
REGISTER_STATUS_TABLE = 'XdrOatRegisterStatus'

logger = get_customized_json_logger()


def get_clp_id(token):
    return jwt.decode(token, options={"verify_signature": False}).get('cid')


def find_token_by_clp(clp_id, api_tokens):
    return next(filter(lambda token: get_clp_id(token) == clp_id, api_tokens), None)


@timer
def get_last_success_time(table_name, clp_id):
    try:
        table_service_client = TableServiceClient.from_connection_string(
            conn_str=STORAGE_CONNECTION_STRING
        )
        table_service_client.create_table_if_not_exists(table_name)

        table_client = TableClient.from_connection_string(
            conn_str=STORAGE_CONNECTION_STRING, table_name=table_name
        )

        entity = table_client.get_entity(LAST_SUCCESS_TIME_PARTITION_KEY, clp_id)
        return pytz.utc.localize(
            datetime.strptime(entity['last_success_time'], DATETIME_FORMAT)
        )
    except ResourceNotFoundError:
        return None


@timer
def update_last_success_time(table_name, clp_id, time):
    table_client = TableClient.from_connection_string(
        conn_str=STORAGE_CONNECTION_STRING, table_name=table_name
    )
    table_client.upsert_entity(
        {
            'PartitionKey': LAST_SUCCESS_TIME_PARTITION_KEY,
            'RowKey': clp_id,
            'last_success_time': time.strftime(DATETIME_FORMAT),
        },
        mode=UpdateMode.MERGE,
    )





@timer
def send_message_to_storage_queue(
    queue_name, message, conn_str=STORAGE_CONNECTION_STRING
):
    queue_client = QueueClient.from_connection_string(
        conn_str,
        queue_name,
        message_encode_policy=TextBase64EncodePolicy(),
    )

    try:
        queue_client.create_queue()
    except ResourceExistsError as e:
        logger.error(e)

    queue_client.send_message(message)
