import logging
import os
import time
from datetime import datetime, timedelta

from typing import Optional

import requests

from .pyepm import (
    get_admin_audit_events,
    get_aggregated_events,
    get_aggregated_policy_audits,
    get_detailed_raw_events,
    get_policy_audit_raw_event_details,
    get_sets_list,
)
from .storage import AzureBlobStorage, LocalStorage


def _get_env(*names: str, default=None):
    for name in names:
        value = os.environ.get(name)
        if value is not None and value != '':
            return value
    return default


client_id = _get_env('OAUTH_USERNAME', 'OAuthUsername')
client_secret = _get_env('OAUTH_PASSWORD', 'OAuthPassword')
identity_endpoint = _get_env('IDENTITY_ENDPOINT', 'IdentityEndpoint')
webapp_id = _get_env('WEBAPP_ID', 'WebAppID')
scope = _get_env('OAUTH_SCOPE', 'OAuthScope', default=None)

dispatcher_url = _get_env('CYBERARK_EPM_SERVER_URL', 'CyberArkEPMServerURL')
fetch_interval_minutes = int(_get_env('FETCH_INTERVAL', 'FetchInterval', default='60'))

storage = LocalStorage() if _get_env('STORAGE', 'Storage') == 'LocalStorage' else AzureBlobStorage()

TOKEN_FILE_NAME = 'token.json'
TIME_FRAME_FILE_NAME = 'time_frame.json'


def _is_token_expired(token: dict) -> bool:
    timestamp = int(token.get('timestamp', 0))
    expiration = int(token.get('expiration', 0))
    return timestamp + expiration <= int(time.time())


def _get_oauth_token() -> Optional[str]:
    if not (client_id and client_secret and identity_endpoint and webapp_id):
        logging.error('Missing OAuth2 configuration environment variables')
        return None

    url = f'{identity_endpoint}/oauth2/token/{webapp_id}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    if scope:
        body['scope'] = scope

    token_data = storage.load(file_name=TOKEN_FILE_NAME)
    if token_data and not _is_token_expired(token_data):
        return token_data.get('token')
    if token_data:
        logging.warning('Stored token expired')

    try:
        logging.info('Creating new token')
        response = requests.post(url=url, headers=headers, data=body)
        res_content = response.json()
        if 200 <= response.status_code <= 299:
            expiration = res_content['expires_in']
            token = res_content['access_token']
            storage.save(
                data={'token': token, 'expiration': expiration, 'timestamp': int(time.time())},
                file_name=TOKEN_FILE_NAME,
            )
            return token
        if response.status_code == 400:
            logging.error(f"{res_content.get('error')} {res_content.get('error_description')}")
        else:
            logging.error(f'error during access token negotiation: {response.status_code} {response.text}')
    except Exception as err:
        logging.error(f'Something went wrong. Exception error text: {err}')
    return None


def _get_time_window() -> tuple[str, str]:
    current_time = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(minutes=10)
    current_time_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    saved = storage.load(file_name=TIME_FRAME_FILE_NAME) or {}
    last_end_str = saved.get('last_end_time')

    if last_end_str:
        try:
            start_time_dt = datetime.strptime(last_end_str, '%Y-%m-%dT%H:%M:%SZ')
        except Exception:
            logging.warning('Invalid last_end_time in storage. Falling back to configured fetch interval.')
            start_time_dt = current_time - timedelta(minutes=fetch_interval_minutes)
    else:
        start_time_dt = current_time - timedelta(minutes=fetch_interval_minutes)

    start_time_str = start_time_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    storage.save(data={'last_end_time': current_time_str}, file_name=TIME_FRAME_FILE_NAME)
    return start_time_str, current_time_str


def _fetch_set_events(fetch_func, token: str, filter_date: str, set_id: dict, next_cursor: str = 'start') -> list:
    response_json = fetch_func(
        epmserver=dispatcher_url,
        epmToken=token,
        setid=set_id['Id'],
        data=filter_date,
        next_cursor=next_cursor,
    ).json()

    if isinstance(response_json, list):
        return []

    events = response_json.get('events') or []
    cursor = response_json.get('nextCursor')
    if cursor:
        events += _fetch_set_events(fetch_func, token=token, filter_date=filter_date, set_id=set_id, next_cursor=cursor)
    for event in events:
        if isinstance(event, dict):
            event['set_name'] = set_id.get('Name')
    return events


def collect_events() -> list:
    if not dispatcher_url:
        logging.error('CyberArkEPMServerURL is missing')
        return []

    token = _get_oauth_token()
    if not token:
        logging.error('Failed to obtain OAuth token')
        return []

    start_time, end_time = _get_time_window()
    logging.info(f'Data processing. Period(UTC): {start_time} - {end_time}')

    filter_date = '{"filter": "arrivalTime GE ' + str(start_time) + ' AND arrivalTime LE ' + end_time + '"}'

    try:
        sets_list = get_sets_list(epmserver=dispatcher_url, epm_token=token)
        sets = sets_list.json().get('Sets') or []
    except Exception:
        logging.error('CyberArkEPMServerURL is invalid')
        return []

    all_events: list = []
    for set_id in sets:
        logging.info(f"Collecting aggregated events from {set_id.get('Name')}")
        for e in _fetch_set_events(get_aggregated_events, token=token, filter_date=filter_date, set_id=set_id):
            if isinstance(e, dict):
                e['event_type'] = 'aggregated_events'
            all_events.append(e)

        logging.info(f"Collecting raw events from {set_id.get('Name')}")
        for e in _fetch_set_events(get_detailed_raw_events, token=token, filter_date=filter_date, set_id=set_id):
            if isinstance(e, dict):
                e['event_type'] = 'raw_event'
            all_events.append(e)

        logging.info(f"Collecting aggregated policy audits from {set_id.get('Name')}")
        for e in _fetch_set_events(get_aggregated_policy_audits, token=token, filter_date=filter_date, set_id=set_id):
            if isinstance(e, dict):
                e['event_type'] = 'aggregated_policy_audits'
            all_events.append(e)

        logging.info(f"Collecting policy audit raw event details from {set_id.get('Name')}")
        for e in _fetch_set_events(get_policy_audit_raw_event_details, token=token, filter_date=filter_date, set_id=set_id):
            if isinstance(e, dict):
                e['event_type'] = 'policy_audit_raw_event_details'
            all_events.append(e)

        logging.info(f"Collecting Admin Audit Data from {set_id.get('Name')}")
        try:
            admin_events = get_admin_audit_events(
                epmserver=dispatcher_url,
                epm_token=token,
                setid=set_id['Id'],
                start_time=start_time,
                end_time=end_time,
                limit=100,
            )
            for e in admin_events:
                all_events.append(e)
        except Exception as err:
            logging.warning(f'Failed fetching Admin Audit Data: {err}')

    return [e for e in all_events if isinstance(e, dict)]
