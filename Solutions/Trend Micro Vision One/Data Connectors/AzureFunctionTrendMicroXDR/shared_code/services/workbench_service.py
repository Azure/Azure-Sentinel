import uuid

import requests
from requests.exceptions import HTTPError
from shared_code import configurations
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.trace_utils.trace import trace_manager

logger = get_customized_json_logger()

XDR_HOST_URL = configurations.get_xdr_host_url()
HTTP_TIMEOUT = configurations.get_workbench_api_timeout_seconds()


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


# Get List of Events
def get_workbench_list(token, start_time, end_time, offset=0, limit=200):
    query_params = {
        'source': 'all',
        'investigationStatus': 'null',
        'sortBy': 'createdTime',
        'queryTimeField': 'createdTime',
        'offset': offset,
        'limit': limit,
        'startDateTime': start_time,
        'endDateTime': end_time,
    }

    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json;charset=utf-8',
        }
    )
    url = f"{XDR_HOST_URL}/v2.0/siem/events"
    logger.info(f'Get workbench list url: {url}')

    response = requests.get(
        url, headers=headers, params=query_params, timeout=HTTP_TIMEOUT
    )
    logger.info(
        f'Get workbench list response: {response.text}'
        f'Get workbench list trace: {get_trace_log(response.headers)}'
    )

    if response.status_code in [requests.codes.forbidden, requests.codes.not_found]:
        logger.error(f"response status code: {response.status_code}")
        return 0, []

    response.raise_for_status()
    response_data = response.json()

    workbench_records = response_data['data']['workbenchRecords']
    total_count = response_data['data']['totalCount']

    return total_count, workbench_records


# Get List of Events
def get_workbench_detail(token, workbench_id):
    url = f"{XDR_HOST_URL}/v2.0/xdr/workbench/workbenches/{workbench_id}"
    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json;charset=utf-8',
        }
    )
    logger.info(f'Get workbench detail url: {url}')
    response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
    logger.info(
        f'Get workbench detail response: {response.text}.'
        f'Get workbench detail trace: {get_trace_log(response.headers)}'
    )

    if response.status_code in [requests.codes.forbidden, requests.codes.not_found]:
        logger.error(f"response status code: {response.status_code}")
        return []

    response.raise_for_status()
    response_data = response.json()

    return response_data['data']


def get_workbench_detail_v3(token: str, workbench_id: str):
    url = f'{XDR_HOST_URL}/v3.0/workbench/alerts/{workbench_id}'
    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json;charset=utf-8',
        }
    )
    logger.info(f'Get workbench detail v3 url: {url}')
    response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
    logger.info(
        f'Get workbench detail v3 response: {response.text}.'
        f'Get workbench detail v3 trace: {get_trace_log(response.headers)}'
    )
    response.raise_for_status()
    response_data = response.json()

    return response_data


def get_rca_task(token, workbench_id):
    try:
        url = f'{XDR_HOST_URL}/v3.0/xdr/mssp/workbench/workbenches/{workbench_id}/tasks/rca'
        headers = get_header(
            {
                'Authorization': f"Bearer {token}",
                'Content-Type': 'application/json;charset=utf-8',
            }
        )
        logger.info(f'Get rca task url: {url}')
        response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        logger.info(
            f'Get rca task response: {response.text}'
            f'Get rca task trace: {get_trace_log(response.headers)}'
        )

        if response.status_code in [requests.codes.forbidden, requests.codes.not_found]:
            logger.error(f"response status code: {response.status_code}")
            return []

        response.raise_for_status()
        response_data = response.json()

        return response_data['data']
    except HTTPError as e:
        logger.warn(f'Failed to get rca tasks. Exception: {e}')
    return []


def get_rca_task_detail(token, task_id, endpoint_guid):
    url = f'{XDR_HOST_URL}/v3.0/xdr/mssp/workbench/tasks/rca/{task_id}/results/{endpoint_guid}'
    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json;charset=utf-8',
        }
    )
    logger.info(f'Get rca task detail url: {url}')
    response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
    logger.info(
        f'Get rca detail response: {response.text}'
        f'Get rca detail trace: {get_trace_log(response.headers)}'
    )

    if response.status_code in [requests.codes.forbidden, requests.codes.not_found]:
        logger.error(f"response status code: {response.status_code}")
        return []

    response.raise_for_status()
    response_data = response.json()

    return response_data['data']
