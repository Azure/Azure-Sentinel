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


client_id = os.environ.get('OAuthUsername')
client_secret = os.environ.get('OAuthPassword')
identity_endpoint = os.environ.get('IdentityEndpoint')
epm_host = os.environ.get('EPMRegionHost')
webapp_id = os.environ.get('WebAppID')

fetch_interval_minutes = int(os.environ.get('FetchInterval', '60'))

storage = LocalStorage() if os.environ.get('STORAGE', 'Storage') == 'LocalStorage' else AzureBlobStorage()

TOKEN_FILE_NAME = 'token.json'
EPM_TENANT_URL_FILE_NAME = 'epm_tenant_url.json'
TIME_FRAME_FILE_NAME = 'time_frame.json'


def _is_token_expired(token: dict) -> bool:
    timestamp = int(token.get('timestamp', 0))
    expiration = int(token.get('expires_in', 0))
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


def _fetch_set_events(fetch_func, dispatcher_url: str, token: str, filter_date: str, set_id: dict, next_cursor: str = 'start') -> list:
    response_json = fetch_func(
        epm_server=dispatcher_url,
        epm_token=token,
        set_id=set_id['Id'],
        data=filter_date,
        next_cursor=next_cursor,
    ).json()

    if isinstance(response_json, list):
        return []

    events = response_json.get('events') or []
    cursor = response_json.get('nextCursor')
    if cursor:
        events += _fetch_set_events(fetch_func, dispatcher_url=dispatcher_url, token=token, filter_date=filter_date, set_id=set_id, next_cursor=cursor)
    return [e | {"SetName": set_id.get("Name")} for e in events if isinstance(e, dict)]


def _get_dispatcher_url(auth_token: str):
    url = f'{epm_host}/EPM/API/accounts/tenanturl'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }
    tenant_url = storage.load(file_name=EPM_TENANT_URL_FILE_NAME)
    if tenant_url:
        return tenant_url.get('tenantUrl')

    try:
        logging.info('Getting tenant URL')
        response = requests.get(url=url, headers=headers)
        res_content = response.json()
        if 200 <= response.status_code <= 299:
            tenant_url = res_content['tenantUrl']
            storage.save(
                data={'tenantUrl': tenant_url},
                file_name=EPM_TENANT_URL_FILE_NAME,
            )
            return tenant_url
        if response.status_code == 400:
            logging.error(f"{res_content.get('error')} {res_content.get('error_description')}")
        else:
            logging.error(f'error fetching tenant URL: {response.status_code} {response.text}')
    except Exception as err:
        logging.error(f'Something went wrong. Exception error text: {err}')
    return None


def collect_events() -> list:
    token = _get_oauth_token()
    dispatcher_url = _get_dispatcher_url(token)
    if not token or not dispatcher_url:
        logging.error('Failed to obtain OAuth token or dispatcher URL')
        return []

    start_time, end_time = _get_time_window()
    logging.info(f'Data processing. Period(UTC): {start_time} - {end_time}')

    filter_date = '{"filter": "arrivalTime GE ' + str(start_time) + ' AND arrivalTime LE ' + end_time + '"}'

    try:
        sets_list = get_sets_list(epm_server=dispatcher_url, epm_token=token)
        sets = sets_list.json().get('Sets') or []
    except Exception:
        logging.error('CyberArkEPMServerURL is invalid')
        return []

    all_events: list = []
    for set_id in sets:
        aggregated_events = _fetch_set_events(get_aggregated_events, dispatcher_url=dispatcher_url, token=token, filter_date=filter_date, set_id=set_id)
        logging.info(f"Fetched {len(aggregated_events)} aggregated events from {set_id.get('Name')}")
        all_events.extend([e | {"eventType": 'aggregated_events'} for e in aggregated_events if isinstance(e, dict)])

        detailed_raw_events =  _fetch_set_events(get_detailed_raw_events, dispatcher_url=dispatcher_url, token=token, filter_date=filter_date, set_id=set_id)
        logging.info(f"Fetched {len(detailed_raw_events)} detailed raw events from {set_id.get('Name')}")
        all_events.extend([e | {"eventType": 'raw_event'} for e in detailed_raw_events if isinstance(e, dict)])

        aggregated_policy_audits = _fetch_set_events(get_aggregated_policy_audits, dispatcher_url=dispatcher_url, token=token, filter_date=filter_date, set_id=set_id)
        logging.info(f"Fetched {len(aggregated_policy_audits)} aggregated policy audits from {set_id.get('Name')}")
        all_events.extend([e | {"eventType": 'aggregated_policy_audits'} for e in aggregated_policy_audits if isinstance(e, dict)])

        audit_raw_event_details = _fetch_set_events(get_policy_audit_raw_event_details, dispatcher_url=dispatcher_url, token=token, filter_date=filter_date, set_id=set_id)
        logging.info(f"Fetched {len(audit_raw_event_details)} policy audit raw events from {set_id.get('Name')}")
        all_events.extend([e | {"eventType": 'policy_audit_raw_event_details'} for e in audit_raw_event_details if isinstance(e, dict)])

        try:
            admin_events = get_admin_audit_events(
                epm_server=dispatcher_url,
                epm_token=token,
                set_id=set_id['Id'],
                start_time=start_time,
                end_time=end_time,
                limit=100,
            )
            logging.info(f"Fetched {len(admin_events)} admin audit events from {set_id.get('Name')}")
            all_events.extend(admin_events)
        except Exception as err:
            logging.warning(f'Failed fetching Admin Audit Data: {err}')

    return [e for e in all_events if isinstance(e, dict)]
