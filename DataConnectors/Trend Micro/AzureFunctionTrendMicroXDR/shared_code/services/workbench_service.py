import logging
import requests
from shared_code import configurations
from requests.exceptions import HTTPError
from shared_code.trace_utils.trace import trace_manager

XDR_HOST_URL = configurations.get_xdr_host_url()


def get_header(headers=None):
    headers = headers or {}

    if trace_manager.trace_id:
        headers['x-trace-id'] = trace_manager.trace_id

    if trace_manager.task_id:
        headers['x-task-id'] = trace_manager.task_id

    headers['User-Agent'] = configurations.get_user_agent()

    return headers    


def get_trace_log():
    return f'trace id: {trace_manager.trace_id}, task id: {trace_manager.task_id}.'


# Get List of Events
def get_workbench_list(token, start_time, end_time, offest=0, limit=200):
    query_params = {
        'source': 'all',
        'investigationStatus': 'null',
        'sortBy': 'createdTime',
        'queryTimeField': 'createdTime',
        'offset': offest,
        'limit': limit,
        'startDateTime': start_time,
        'endDateTime': end_time,
    }

    headers = get_header({
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json;charset=utf-8',
    })
    url = f"{XDR_HOST_URL}/v2.0/siem/events"
    logging.info(f'Get workbench list url: {url}\n{get_trace_log()}')

    response = requests.get(url, headers=headers, params=query_params)
    logging.info(f'Get workbench list response: {response.text}')
    response.raise_for_status()
    response_data = response.json()

    workbench_records = response_data['data']['workbenchRecords']
    total_count = response_data['data']['totalCount']

    return total_count, workbench_records


# Get List of Events
def get_workbench_detail(token, workbench_id):
    url = f"{XDR_HOST_URL}/v2.0/xdr/workbench/workbenches/{workbench_id}"
    logging.info(f'Get workbench detail url: {url}\n{get_trace_log()}')

    headers = get_header({
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json;charset=utf-8',
    })
    response = requests.get(url, headers=headers)
    logging.info(f'Get workbench detail response: {response.text}')
    response.raise_for_status()
    response_data = response.json()

    return response_data['data']


def get_rca_task(token, workbench_id):
    try:
        url = f'{XDR_HOST_URL}/v3.0/xdr/mssp/workbench/workbenches/{workbench_id}/tasks/rca'
        logging.info(f'Get rca task url: {url}\n{get_trace_log()}')

        headers = get_header({
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json;charset=utf-8',
        })
        response = requests.get(url, headers=headers)
        logging.info(f'Get rca task response: {response.text}')
        response.raise_for_status()
        response_data = response.json()

        return response_data['data']
    except HTTPError as e:
        logging.warn(f'Failed to get rca tasks. Exception: {e}')
    return []


def get_rca_task_detail(token, task_id, endpoint_guid):

    url = f'{XDR_HOST_URL}/v3.0/xdr/mssp/workbench/tasks/rca/{task_id}/results/{endpoint_guid}'
    logging.info(f'Get rca task detail url: {url}\n{get_trace_log()}')

    headers = get_header({
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json;charset=utf-8',
    })
    response = requests.get(url, headers=headers)
    logging.info(f'Get rca detail response: {response.text}')
    response.raise_for_status()
    response_data = response.json()

    return response_data['data']