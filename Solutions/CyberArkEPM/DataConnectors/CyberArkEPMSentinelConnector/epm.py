import base64
from datetime import datetime, timedelta
import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import os
from .storage import AzureBlobStorage, LocalStorage

client_id = os.environ.get('OAuthUsername')
client_secret = os.environ.get('OAuthPassword')
identity_endpoint = os.environ.get('IdentityEndpoint')
api_base_url = os.environ.get('ApiBaseUrl')
webapp_id = os.environ.get('WebAppID')
fetch_interval = int(os.environ.get('FetchInterval', '60'))

storage = LocalStorage() if os.environ.get('Storage') == 'LocalStorage' else AzureBlobStorage()

TOKEN_FILE_NAME = 'token.json'
TIME_FRAME_FILE_NAME = 'time_frame.json'


def _is_token_expired(token: dict):
    timestamp = int(token['timestamp'])
    expiration = int(token['expiration'])
    return timestamp + expiration <= int(time.time())


def _get_oauth_token() -> str:
    token = None
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    body = {
        'grant_type': 'client_credentials',
    }
    url = f'{identity_endpoint}/oauth2/token/{webapp_id}'
    try:
        token_data = storage.load(file_name=TOKEN_FILE_NAME)
        if token_data:
            if not _is_token_expired(token_data):
                return token_data['token']
            else:
                logging.warning(f'Stored token expired')
        logging.info('Creating new token')
        response = requests.post(url=url, headers=header, data=body, auth=(client_id, client_secret))
        res_content = response.json()
        if 200 <= response.status_code <= 299:
            expiration = res_content['expires_in']
            logging.info(f"Access Token obtained successfully. Valid for {expiration} sec")
            token = res_content['access_token']
            storage.save(data={'token': token, 'expiration': expiration, 'timestamp': int(time.time())}, file_name=TOKEN_FILE_NAME)
        elif response.status_code == 400:
            logging.error(f"{res_content['error']} {res_content['error_description']}")
        else:
            logging.error(f'error during access token negotiation: {response.status_code}')
    except Exception as err:
        logging.error(f"Something went wrong. Exception error text: {err}")
    return token


def _call_epm_api(route: str, body: dict) -> dict:
    res_content = None
    token = _get_oauth_token()
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        # TODO: 'x-cybr-telemetry': '---'
    }
    url = f'{api_base_url}/EPM/API/{route}'
    session = requests.Session()
    retry = Retry(total=3,
                  backoff_factor=10,
                  status_forcelist=(403, 429),
                  allowed_methods=frozenset(['POST', 'GET']),
                  respect_retry_after_header=True)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    
    try:
        response = session.post(url=url, headers=header, data=json.dumps(body))
        if 200 <= response.status_code <= 299:
            res_content = response.json()
        elif response.status_code in [400, 401, 403]:
            logging.error(f'Error {response.status_code} {response.text}')
        else:
            logging.error(f'Error HTTP {response.status_code} when calling {url}')
    except Exception as err:
        logging.error(f'Something went wrong {err}')
    return res_content

def _generate_date():
    """
    Determine the time window to fetch events for this run and persist the end time for the next run.
    - Default window is 60 minutes, configurable via env FetchInterval (minutes).
    - We store the last end time in storage to use as the next run's start time.
    - We also apply a 10 minute delay buffer to account for ingestion delays.
    Returns tuple (start_time_iso, end_time_iso).
    """
    # End time is "now" minus a safety buffer
    current_time = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(minutes=10)
    current_time_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Load previously saved end time
    saved = storage.load(file_name=TIME_FRAME_FILE_NAME) or {}
    last_end_str = saved.get('last_end_time')

    if last_end_str:
        try:
            # Use the last end time as the new start time
            past_time_dt = datetime.strptime(last_end_str, "%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            logging.warning("Invalid last_end_time in storage. Falling back to configured fetch interval.")
            past_time_dt = current_time - timedelta(minutes=fetch_interval)
        logging.info(f"Using last recorded end time as start: {past_time_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    else:
        logging.info(f"No recorded time frame. Using configured fetch interval of {fetch_interval} minutes.")
        past_time_dt = current_time - timedelta(minutes=fetch_interval)

    past_time_str = past_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    storage.save(data={"last_end_time": current_time_str}, file_name=TIME_FRAME_FILE_NAME)

    return past_time_str, current_time_str



def get_query_data() -> dict:
    start_time, end_time = _generate_date()
    logging.info('Data processing. Period(UTC): {} - {}'.format(start_time, end_time))


    cursor_data = storage.load(file_name=QUERY_FILE_NAME)
    if cursor_data:
        currentPosition='unknown'
        try:
            cursorRef = json.loads(base64.b64decode(cursor_data['cursorRef']))
            currentPosition=cursorRef['currentPosition'][0]
        except Exception as err:
            logging.warning(f'Failed to decode cursorRef: {err}')
        logging.info(f"Fetched stored cursor cursorRef: {cursor_data['cursorRef']}, currentPosition: {currentPosition}")
        return cursor_data
    if os.environ.get('cursorRef'):
        cursor_data['cursor'] = os.environ.get('cursorRef')
        logging.info(f"Using local cursorRef: {cursor_data['cursorRef']}")
        return cursor_data
    body = {
        "query": {
            "pageSize": 500,
            "selectedFields": [
                "tenant_id",
                "custom_data",
                "arrival_timestamp",
                "checksum",
                "application_code",
                "audit_code",
                "timestamp",
                "user_id",
                "session_id",
                "source",
                "action_type",
                "audit_type",
                "component",
                "target",
                "command",
                "message",
                "username",
                "action",
                "uuid",
                "icon",
                "service_name",
                "cloud_roles",
                "cloud_workspaces",
                "cloud_workspaces_and_roles",
                "cloud_assets",
                "cloud_identities",
                "vaulted_accounts",
                "cloud_provider",
                "account_name",
                "target_platform",
                "safe",
                "target_account",
                "identity_type",
                "access_method",
                "account_id",
                "correlation_id"
            ],
        }
    }
    body = _add_filters(body)
    logging.info(f'Creating a new query {body}')
    query_data = _call_audit_api(route='createQuery', body=body)
    if query_data:
        storage.save(data=query_data, file_name=QUERY_FILE_NAME)
        logging.info(f"Saved new cursorRef: {query_data['cursorRef']}")
        return query_data
    return cursor_data


def get_cursor_results(query_data: dict) -> list:
    body = {
        'cursorRef': query_data['cursorRef']
    }
    res_content = _call_audit_api(route='results', body=body)
    if res_content:
        query_data['cursorRef'] = res_content['paging']['cursor']['cursorRef']
        storage.save(data=query_data, file_name=QUERY_FILE_NAME)
        return res_content['data']
    return []
