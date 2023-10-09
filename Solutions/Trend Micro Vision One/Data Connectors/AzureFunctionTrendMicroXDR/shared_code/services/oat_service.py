'''
Azure Table SDK
Currently using azure-cosmosdb-table, see: https://pypi.org/project/azure-cosmosdb-table/
TODO: Use azure-data-tables instead, see: https://pypi.org/project/azure-data-tables/
E.g. create_table_if_not_exists only supported by azure-data-tables
'''
import gzip
import uuid
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import orjson
import requests
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableClient, TableServiceClient, UpdateMode
from shared_code import configurations
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.data_collector import LogAnalytics
from shared_code.models.oat import OATDetectionResult
from shared_code.trace_utils.trace import trace_manager
from shared_code.transform_utils import transform_oat_log

logger = get_customized_json_logger()


XDR_HOST_URL = configurations.get_xdr_host_url()
OAT_ROWS_BULK_COUNT = configurations.get_oat_rows_bulk_count()
WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
OAT_LOG_TYPE = configurations.get_oat_log_type()
STORAGE_CONNECTION_STRING = configurations.get_storage_connection_string()
OAT_PIPELINE_PROCESSED_INFO_TABLE = 'OatPipelineFileProcessedInfo'
REGISTER_STATUS_TABLE = 'XdrOatRegisterStatus'


def get_header(headers=None):
    headers = headers or {}

    trace_manager.trace_id = headers['x-trace-id'] = str(uuid.uuid4())

    if trace_manager.task_id:
        headers['x-task-id'] = trace_manager.task_id

    headers['User-Agent'] = configurations.get_user_agent()

    return headers


def get_trace_log(headers):
    log = 'headers is empty.'
    if headers:
        task_id = headers.get('x-task-id')
        trace_id = headers.get('x-trace-id')
        log = f'task id: {task_id}, trace id: {trace_id}.'
    return log


def update_oat_pipeline_config(token: str, patch_data: Dict[str, Any]) -> None:
    # See: https://adc.github.trendmicro.com/pages/CoreTech-SG/xdr-doc/?urls.primaryName=public-merged-beta#/Observed%20Attack%20Techniques%20Pipeline/patch_beta_xdr_oat_dataPipeline
    url = f"{XDR_HOST_URL}/beta/xdr/oat/dataPipeline"
    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        }
    )
    logger.info(f'Update oat pipeline config api: {url} \ndata: {patch_data}')
    response = requests.patch(url, headers=headers, json=patch_data)
    logger.info(
        f'Update oat config response: {response.text}, '
        f'response headers: {get_trace_log(response.headers)}'
    )
    response.raise_for_status()


def get_oat_package_list(
    token: str, start_time: str, end_time: str, pipeline_id: str
) -> Tuple[int, List[Dict[str, str]]]:
    """Get OAT package list
    Args:
        token (str): account token
        start_time (str): The beginning of the time interval
        end_time (str): The end of the time interval
        pipeline_id (str): Unique alphanumeric string that identifies a data pipeline.
    Returns:
        Tuple[int, List[Dict[str, str]]]: Number of items retrieved and package list
    """

    query_params = {
        'startDateTime': start_time,
        'endDateTime': end_time,
    }
    url = f"{XDR_HOST_URL}/v1.0/preview/ath/oat/dataPipelines/{pipeline_id}/packages"
    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        }
    )
    logger.info(f'Get oat package list: {url}\nquery params: {query_params}')
    response = requests.get(url, headers=headers, params=query_params)
    logger.info(
        f'Get oat package list response: {response.text}, '
        f'response headers: {get_trace_log(response.headers)}'
    )

    if response.status_code == requests.codes.bad_request:
        response_data = response.json()
        if (
            response_data.get('error', {}).get('innererror', {}).get('code', '')
            == 'OutOfRetentionTime'
        ):
            logger.warning(
                'The OAT file is out of retention time, '
                f'start_time: {start_time}, end_time: {end_time}'
            )
            return 0, []

    response.raise_for_status()

    response_data = response.json()
    package_list = response_data['items']
    count = response_data['count']

    return count, package_list


def download_oat_file(
    token: str, oat_file_id: str, pipeline_id: str
) -> Optional[BytesIO]:
    """Download OAT package
    Args:
        token (str): account token
        oat_file_id (str): Identification associated with an OAT event
        pipeline_id (str): Unique alphanumeric string that identifies a data pipeline.
    Returns:
        Optional[BytesIO]
    """

    url = f'{XDR_HOST_URL}/v1.0/preview/ath/oat/dataPipelines/{pipeline_id}/packages/{oat_file_id}'
    headers = get_header(
        {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/gzip',
        }
    )
    logger.info(f'Download oat file url: {url}')

    response = requests.get(url, headers=headers)
    logger.info(
        f'Download oat file response status_code: {response.status_code}, '
        f'response headers: {get_trace_log(response.headers)}'
    )

    if response.status_code == requests.codes.bad_request:
        response_data = response.json()
        if (
            response_data.get('error', {}).get('innererror', {}).get('code', '')
            == 'OutOfRetentionTime'
        ):
            logger.warning(
                f'The OAT file is out of retention time, file_id: {oat_file_id}'
            )
            return None

    response.raise_for_status()

    bytes_io = BytesIO()
    with gzip.GzipFile(filename='', fileobj=bytes_io, mode='wb') as fp:
        bytes_written = fp.write(response.content)
    bytes_io.seek(0)
    logger.info(f'Download oat file total bytes: {bytes_written}')

    return bytes_io


def _file_line_generator(file: BytesIO) -> str:
    try:
        file.seek(0)
        with gzip.open(file, mode='rt') as fp:
            for line in fp:
                yield line
    except Exception as e:
        logger.exception(f'Fail to generate file rows. Exception: {e}')
        raise


def _send_logs_to_log_analytics(logs: List[Dict[str, Any]]) -> None:
    log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, OAT_LOG_TYPE)
    log_analytics.post_data(logs)
    logger.info(f'Send oat data to Sentinel successfully. count: {len(logs)}')


def get_oat_file_processed_lines(
    table_client: TableClient, file_id: str, clp_id: str
) -> Optional[int]:
    try:
        entity = table_client.get_entity(file_id, clp_id)
        return entity['processed_lines']
    except ResourceNotFoundError:
        return None


def update_oat_file_processed_lines(
    table_client: TableClient, clp_id: str, file_id: str, processed_lines: int
) -> None:
    logger.info(
        f'Update oat file processed lines. clp_id:{clp_id}, '
        f'file_id: {file_id}, {processed_lines} lines.'
    )
    table_client.upsert_entity(
        {
            'PartitionKey': file_id,
            'RowKey': clp_id,
            'processed_lines': processed_lines,
        },
        mode=UpdateMode.MERGE,
    )


def delete_oat_file_processed_lines(
    table_client: TableClient, clp_id: str, file_id: str
) -> None:
    logger.info(f'Delete processed record. clp_id: {clp_id}, file_id: {file_id}.')
    table_client.delete_entity(file_id, clp_id)


def oat_file_handler(clp_id: str, file_id: str, file: BytesIO) -> None:
    table_service_client = TableServiceClient.from_connection_string(
        conn_str=STORAGE_CONNECTION_STRING
    )
    table_service_client.create_table_if_not_exists(OAT_PIPELINE_PROCESSED_INFO_TABLE)
    table_client = TableClient.from_connection_string(
        conn_str=STORAGE_CONNECTION_STRING,
        table_name=OAT_PIPELINE_PROCESSED_INFO_TABLE,
    )

    processed_lines = get_oat_file_processed_lines(table_client, file_id, clp_id)
    if processed_lines:
        logger.info(f'The OAT gzip has been processed {processed_lines} lines.')

    rows = []
    for row_idx, row in enumerate(_file_line_generator(file)):
        if processed_lines and row_idx <= processed_lines:
            continue

        rows.append(orjson.loads(row))
        if len(rows) == OAT_ROWS_BULK_COUNT:
            oat_logs = [transform_oat_log(clp_id, log) for log in rows]
            _send_logs_to_log_analytics(oat_logs)
            rows = []
            update_oat_file_processed_lines(table_client, clp_id, file_id, row_idx)

    if rows:
        oat_logs = [transform_oat_log(clp_id, log) for log in rows]
        _send_logs_to_log_analytics(oat_logs)
        if row_idx >= OAT_ROWS_BULK_COUNT:
            delete_oat_file_processed_lines(table_client, clp_id, file_id)


def get_oat_pipeline_id(clp_id):
    try:
        table_service_client = TableServiceClient.from_connection_string(
            conn_str=STORAGE_CONNECTION_STRING
        )
        table_service_client.create_table_if_not_exists(REGISTER_STATUS_TABLE)

        table_client = TableClient.from_connection_string(
            conn_str=STORAGE_CONNECTION_STRING, table_name=REGISTER_STATUS_TABLE
        )

        entity = table_client.get_entity(clp_id, clp_id)
        return entity.get('pipelineId', None)

    except ResourceNotFoundError:
        return None


def update_oat_pipeline_id(clp_id, pipeline_id):
    table_client = TableClient.from_connection_string(
        conn_str=STORAGE_CONNECTION_STRING, table_name=REGISTER_STATUS_TABLE
    )
    table_client.upsert_entity(
        {
            'PartitionKey': clp_id,
            'RowKey': clp_id,
            'pipelineId': pipeline_id,
        },
        mode=UpdateMode.MERGE,
    )


def get_pipeline_id_for_migration(token: str) -> str:
    """Get pipeline id from single config api
    Returns:
        str: pipelineId
    """

    url = f"{XDR_HOST_URL}/beta/xdr/oat/dataPipeline"
    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        }
    )
    logger.info(f'Get oat pipeline id for migration: {url}.')
    response = requests.get(url, headers=headers)
    logger.info(f'Get oat pipeline id for migration, response: {response.text}, ')

    response.raise_for_status()
    response_data = response.json()
    return response_data['pipelineId']


def is_registered_by_pipeline_id(token: str, pipeline_id: str) -> bool:
    """Get customer settings
    Returns:
        bool: http code is ok
    """

    url = f"{XDR_HOST_URL}/v1.0/preview/ath/oat/dataPipelines/{pipeline_id}"
    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        }
    )
    logger.info(f'Get oat customer setting from multiple config api: {url}.')
    response = requests.get(url, headers=headers)
    logger.info(f'Get oat customer setting response: {response.text}, ')

    if response.status_code == requests.codes.ok:
        return True
    else:
        return False


def register_oat_and_get_pipeline_id(
    token: str, post_data: Dict[str, Any], clp_id: str
) -> str:
    """Register multiple config OAT
    Args:
        token (str): account token
        post_data (Dict): registration information for OAT
        clp_id (str): clp id
    Returns:
        str: pipeline_id
    """
    url = f"{XDR_HOST_URL}/v1.0/preview/ath/oat/dataPipelines"

    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        }
    )
    logger.info(f'Register oat from multiple config api: {url} \ndata: {post_data}')

    response = requests.post(url, headers=headers, json=post_data)
    logger.info(
        f'Register oat from multiple config api response: {response.text}, header: {response.headers} '
    )

    response.raise_for_status()

    # pipeline id is gotten from Location of response header that is the string behind the last slash
    location = response.headers.get('Location').split('/')
    pipeline_id = location[-1]
    if not pipeline_id:
        raise Exception(f'Pipeline id of customer [{clp_id}] is invalid.')

    logger.info(
        f'Customer [{clp_id}] registers to OAT successfully. pipeline id: {pipeline_id}'
    )
    return pipeline_id
