from datetime import datetime
import logging
import requests
from shared_code import configurations
from shared_code.models.oat import OATDetectionResult
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
def get_oat_list(
    token: str,
    start_time: datetime,
    end_time: datetime,
    size: int = 40,
    next_batch_token: str = None,
) -> OATDetectionResult:
    risk_levels = ['low', 'medium', 'high', 'critical']
    query_params = {
        'start': int(start_time.timestamp()),
        'end': int(end_time.timestamp()),
        'size': size,
        'riskLevels': risk_levels,
    }
    if next_batch_token:
        query_params['nextBatchToken'] = next_batch_token

    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json;charset=utf-8',
        }
    )
    url = f"{XDR_HOST_URL}/v2.0/xdr/oat/detections"
    logging.info(f'Get oat list url: {url}\n{get_trace_log()}')

    response = requests.get(url, headers=headers, params=query_params)
    logging.info(f'Get oat list response: {response.text}')
    response.raise_for_status()
    response_data = response.json()

    detections = response_data['data']['detections']
    total_count = response_data['data']['totalCount']
    next_batch_token = response_data['data'].get('nextBatchToken')
    search_api_post_data = response_data['data']['searchApiPostData']

    return OATDetectionResult(
        total_count=total_count,
        detections=detections,
        search_api_post_data=search_api_post_data,
        next_batch_token=next_batch_token,
    )


# Get raw logs from search api
def get_search_data(token, post_data):
    url = f"{XDR_HOST_URL}/v2.0/xdr/search/data"
    logging.info(f'Get search data url: {url} \ndata: {post_data}\n{get_trace_log()}')

    headers = get_header(
        {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json;charset=utf-8',
        }
    )
    response = requests.post(url, headers=headers, json=post_data)
    logging.info(f'Get search data response: {response.text}')
    response.raise_for_status()
    response_data = response.json()

    return response_data['data']['logs']
