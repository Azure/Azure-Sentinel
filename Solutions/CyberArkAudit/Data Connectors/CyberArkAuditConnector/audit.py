import datetime
import json
import logging
import requests
import os
from .models import TokenModel, QueryModel
from .storage import AzureBlobStorage, LocalStorage

client_id = os.environ.get('OAuthUsername')
client_secret = os.environ.get('OAuthPassword')
identity_endpoint = os.environ.get('IdentityEndpoint')
api_key = os.environ.get('ApiKey')
api_base_url = os.environ.get('ApiBaseUrl')
webapp_id = os.environ.get('WebAppID')

storage = LocalStorage() if os.environ.get('Storage') == 'LocalStorage' else AzureBlobStorage()


def _get_oauth_token() -> str:
    token = None
    header = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = {
        'grant_type': 'client_credentials',
        'scope': 'isp.audit.events:read',
        'client_id': client_id,
        'client_secret': client_secret
    }
    url = f'{identity_endpoint}/oauth2/token/{webapp_id}'
    try:
        token_data = storage.load(file_name=TokenModel.get_file_name())

        if token_data:
            token_model = TokenModel(**token_data)
            if not token_model.is_expired():
                return token_model.token
            else:
                logging.warning(f'Stored token expired')
        logging.info('Creating new token')
        response = requests.post(url=url, headers=header, data=body)
        res_content = response.json()
        if 200 <= response.status_code <= 299:
            expiration = res_content['expires_in']
            logging.info(f"Access Token obtained successfully. Valid for {expiration} sec")
            token = res_content['access_token']
            storage.save(data=TokenModel(token=token, expiration=expiration).model_dump(), file_name=TokenModel.get_file_name())
        elif response.status_code == 400:
            logging.error(f"{res_content['error']} {res_content['error_description']}")
        else:
            logging.error(f'error during access token negotiation: {response.status_code}')
    except Exception as err:
        logging.error(f"Something went wrong. Exception error text: {err}")
    return token


def _add_filters(body: dict) -> dict:
    filter_model = {}
    filters = [
        {
            'env': 'ActionFilter',
            'param': 'action'
        },
        {
            'env': 'ApplicationCodeFilter',
            'param': 'applicationCode'
        },
        {
            'env': 'AuditTypeFilter',
            'param': 'auditType'
        }
        ]
    filter_model['date'] = {'dateFrom': os.environ.get('DateFrom') or datetime.datetime.now().isoformat()}
    for filter in filters:
        if os.environ.get(filter['env']):
            filter_model[filter['param']] = [{'op': 'include', 'params': os.environ.get(filter['env']).split(',')}]
    if filter_model:
        body['query']['filterModel'] = filter_model
    return body


def _call_audit_api(route: str, body: dict) -> dict:
    res_content = None
    token = _get_oauth_token()
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'x-api-key': api_key,
        'IntegrationName': 'Azure Sentinel Audit',
        'IntegrationType': 'SIEM',
        'IntegrationVersion': '1.0',
        'CyberArkService': 'Audit',
        'VendorName': 'Azure',
        'VendorProductName': 'Sentinel'
    }
    url = f'{api_base_url}/api/audits/stream/{route}'
    try:
        response = requests.post(url=url, headers=header, data=json.dumps(body))
        if response.status_code == 200:
            res_content = response.json()
        elif response.status_code in [400, 401, 403]:
            logging.error(f'Error {response.status_code} {response.text}')
        elif response.status_code == 500:
            logging.error(f'Error {response.status_code}')
    except Exception as err:
        logging.error(f'Something went wrong {err}')
    return res_content


def get_query_model() -> QueryModel:
    cursor_data = storage.load(file_name=QueryModel.get_file_name())
    if cursor_data:
        model = QueryModel(**cursor_data)
        logging.info(f'Fetched stored cursor cursorRef: {model.cursor}')
        return model
    if os.environ.get('cursorRef'):
        model = QueryModel(cursor=os.environ.get('cursorRef'))
        logging.info(f'Using local cursorRef: {model.cursor}')
        return model
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
                "identity_type"
            ],
        }
    }
    body = _add_filters(body)
    res_content = _call_audit_api(route='createQuery', body=body)
    if res_content:
        query_model = QueryModel(query=body['query'], cursor=res_content['cursorRef'])
        logging.info('Saving cursor from new query')
        storage.save(data=query_model.model_dump(), file_name=QueryModel.get_file_name())
        logging.info(f'Saved new cursorRef: {query_model.cursor}')
        return query_model
    return None


def get_cursor_results(query_model: QueryModel) -> list:
    body = {
        'cursorRef': query_model.cursor
    }
    res_content = _call_audit_api(route='results', body=body)
    if res_content:
        query_model.cursor = res_content['paging']['cursor']['cursorRef']
        storage.save(data=query_model.model_dump(), file_name=QueryModel.get_file_name())
        return res_content['data']
    return []
