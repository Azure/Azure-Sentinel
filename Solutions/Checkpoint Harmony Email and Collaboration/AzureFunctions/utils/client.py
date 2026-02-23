import base64
import datetime
import hashlib
import time
import uuid
from abc import ABC, abstractmethod
from typing import List
from urllib.parse import urlencode

import requests
from cached_property import cached_property
from jose import jwt


class ApiClientBase(ABC):
    def __init__(self, host: str, client_id: str, client_secret: str):
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expiry = None
        self.api_version = 'v1.0'

    @abstractmethod
    def get_token(self) -> str:
        pass

    @abstractmethod
    def headers(self, request_string: str = None, auth: bool = False) -> dict:
        pass

    @abstractmethod
    def get_path(self, endpoint: str) -> str:
        pass

    @abstractmethod
    def get_request_string(self, endpoint: str, params: dict = None) -> str:
        pass

    def call_api(self, method: str, endpoint: str, params: dict = None, body: dict = None,
                 headers: dict = None) -> (
            dict):
        """
        Perform call to the Avanan Smart API

        :param method: HTTP method - post, get
        :param endpoint: API Endpoint
        :param params: GET parameters
        :param body: JSON Body
        :return: Response JSON
        """
        headers = headers or self.headers(self.get_request_string(endpoint, params))
        res = requests.request(method, f'https://{self.host}/{self.get_path(endpoint)}', headers=headers,
                               params=params, json=body)
        from pprint import pprint
        pprint(res.headers)
        try:
            res.raise_for_status()

        except requests.exceptions.HTTPError as e:
            print(f'request exception: status_code[{e.response.status_code}] response[{e.response.content}]')
            raise e

        return res.json()

    @staticmethod
    def strip_none(payload: dict):
        for key, value in dict(payload).items():
            if value is None:
                del payload[key]

    def get_scopes(self):
        """
        Get list of scopes available for app client (client_id + client_secret)
        Scopes are made of 2 values separated by ":", for example, mt-prod-3:customer1
        The first is the farm (internal Avanan designation), the second is your customer name used to access the Avanan
        portal (customer1.avanan.net)

        Currently there are 3 production farms, one in each supported region:
        US: mt-prod-3
        EU: mt-prod-av-1
        CA: mt-proc-av-ca-2

        :return: List of scopes as <farm>:<customer>
        """
        return self.call_api('get', 'scopes')

    def get_exceptions2(self):
        return self.call_api('get', 'sectool-exceptions/avanan_dlp/exceptions/sender_email/test@e.com')
        return self.call_api('get', 'sectool-exceptions/avanan_dlp/exceptions/sender_email')

    def get_event(self, event_id: str):
        """
        Get single SaaS entity

        :param event_id: Avanan Security Event ID
        :return: Security Event
        """
        return self.call_api('get', f'event/{event_id}')

    def query_events(self, start_date: str, end_date: str = None, event_types: List[str] = None,
                     event_states: List[str] = None, severities: List[str] = None, saas: List[str] = None,
                     description: str = None, event_ids: List[str] = None, scroll_id: str = None,
                     scopes: List[str] = None):
        """
        Query Security Events

        :param start_date: Start date (iso 8601)
        :param end_date: End date (iso 8601)
        :param event_types: List of event types
        :param event_states: List of event states
        :param severities: List of severities
        :param saas: SaaS Name
        :param description: Description
        :param event_ids: List of Event ID
        :param scroll_id: Scroll ID for pagination
        :param scopes: List of scopes as <farm>:<customer>
        :return: Security events
        """
        request_data = {
            'scopes': scopes,
            'eventTypes': event_types,
            'eventStates': event_states,
            'severities': severities,
            'startDate': start_date,
            'endDate': end_date,
            'saas': saas,
            'description': description,
            'eventIds': event_ids,
            'scrollId': scroll_id
        }
        self.strip_none(request_data)
        payload = {
            'requestData': request_data
        }
        return self.call_api('post', 'event/query', body=payload)

    def get_entity(self, entity_id: str):
        """
        Get single SaaS entity

        :param entity_id: Avanan SaaS Entity ID
        :return: Entity
        """
        return self.call_api('get', f'search/entity/{entity_id}')

    def query_entities(self, saas: str, start_date: str, end_date: str = None, entity_type: str = None,
                       extended_filter: List[dict] = None, scroll_id: str = None, scopes: List[str] = None):
        """
        Query SaaS entities

        :param saas: SaaS Name
        :param start_date: Start date (iso 8601)
        :param end_date: End date (iso 8601)
        :param entity_type: SaaS Entity Type
        :param extended_filter: Extended filters list
        :param scroll_id: Scroll ID for pagination
        :param scopes: List of scopes as <farm>:<customer>
        :return: Entities
        """
        entity_filter = {
            'saas': saas,
            'saasEntity': entity_type,
            'startDate': start_date,
            'endDate': end_date,
        }
        self.strip_none(entity_filter)
        request_data = {
            'scopes': scopes,
            'entityFilter': entity_filter,
            'entityExtendedFilter': extended_filter,
            'scrollId': scroll_id
        }
        self.strip_none(request_data)
        payload = {
            'requestData': request_data
        }
        return self.call_api('post', 'search/query', body=payload)

    def event_action(self, event_ids: List[str], action: str, scope: str = None):
        """
        Perform action on the entities associated with a security event

        :param event_ids: List of Event ID
        :param action: Action to perform ('quarantine' or 'restore')
        :param scope: Single scope (mandatory for multi scope app clients)
        :return: Task information
        """
        request_data = {
            'scope': scope,
            'eventIds': event_ids,
            'eventActionName': action
        }
        self.strip_none(request_data)
        payload = {
            'requestData': request_data
        }
        return self.call_api('post', 'action/event', body=payload)

    def entity_action(self, entity_ids: List[str], entity_type: str, action: str, scope: str = None,
                      restore_decline_reason=''):
        """
        Enqueues an action on SaaS entity

        :param entity_ids: List of Entity ID
        :param entity_type: SaaS Entity Type
        :param action: Action to perform ('quarantine' or 'restore')
        :param scope: Single scope (mandatory for multi scope app clients)
        :return: Task information
        """
        request_data = {
            'scope': scope,
            'entityIds': entity_ids,
            'entityType': entity_type,
            'entityActionName': action,
            'restoreDeclineReason': restore_decline_reason
        }
        self.strip_none(request_data)
        payload = {
            'requestData': request_data
        }
        return self.call_api('post', 'action/entity', body=payload)

    def get_task(self, task_id: int, scope: str = None):
        """
        Returns the state of actions enqueued with "entity_action".

        :param task_id: Task ID from "Task Information" (returned by the action endpoints)
        :param scope: Single scope (mandatory for multi scope app clients)
        :return: Updated Task Information
        """
        params = {'scope': scope} if scope else None
        return self.call_api('get', f'task/{task_id}', params=params)

    def report_mis_classification(self):
        """
        Returns the state of actions enqueued with "entity_action".

        :param task_id: Task ID from "Task Information" (returned by the action endpoints)
        :param scope: Single scope (mandatory for multi scope app clients)
        :return: Updated Task Information
        """
        entityIds = ['7f0e023d3e28b3de71beddba9bc1031f']
        classification = 'Clean Email'
        confident = 'High Confidence'
        _action = {
            'entityIds': entityIds,
            'classification': classification,
            'confident': confident,
        }
        payload = {
            'requestData': _action
        }
        # params = {'action': scope} if scope else None
        return self.call_api('post', f'report/mis-classification', body=payload)

    def send_email(self, entity_id: str, emails: List[str]):
        request_data = {
            'entityId': entity_id,
            'emails': emails,
        }
        self.strip_none(request_data)
        payload = {
            'requestData': request_data
        }
        return self.call_api('post', 'soar/notify', body=payload)

    def get_anonly_exceptions(self):
        return self.call_api('get', 'sectools/anomaly/exceptions')

    def get_exceptions(self, exc_type: str, scope: str = None):
        """
        Returns list of exception by the type (whitelist/blacklist).

        :param exc_type: Exception type - whitelist/blacklist
        :param scope: Single scope (mandatory for multi scope app clients)
        """
        params = {'scope': scope} if scope else None
        return self.call_api('get', f'exceptions/{exc_type}', params=params)

    def get_exception(self, exc_type: str, exc_id: str, scope: str = None):
        """
        Returns a single exception by the type (whitelist/blacklist) and ID.

        :param exc_type: Exception type - whitelist/blacklist
        :param exc_id: Exception ID
        :param scope: Single scope (mandatory for multi scope app clients)
        """
        params = {'scope': scope} if scope else None
        return self.call_api('get', f'exceptions/{exc_type}/{exc_id}', params=params)

    def create_exception(self, exc_type: str, exc: dict, scopes: List[str] = None):
        """
        Create exception of the type (whitelist/blacklist).

        :param exc_type: Exception type - whitelist/blacklist
        :param exc: Exception data
        :param scopes: List of scopes as <farm>:<customer>
        """
        request_data = {
            'scopes': scopes,
            **exc
        }
        self.strip_none(request_data)
        payload = {
            'requestData': request_data
        }
        return self.call_api('post', f'exceptions/{exc_type}', body=payload)

    def update_exception(self, exc_type: str, exc_id: str, exc: dict, scopes: List[str] = None):
        """
        Returns a single exception by the type (whitelist/blacklist) and ID.

        :param exc_type: Exception type - whitelist/blacklist
        :param exc_id: Exception ID
        :param exc: Exception data
        :param scopes: List of scopes as <farm>:<customer>
        """
        request_data = {
            'scopes': scopes,
            **exc
        }
        self.strip_none(request_data)
        payload = {
            'requestData': request_data
        }
        return self.call_api('put', f'exceptions/{exc_type}/{exc_id}', body=payload)

    def delete_exception(self, exc_type: str, exc_id: str, scopes: List[str] = None):
        """
        Delete a single exception by the type (whitelist/blacklist) and ID.

        :param exc_type: Exception type - whitelist/blacklist
        :param exc_id: Exception ID
        :param scopes: List of scopes as <farm>:<customer>
        """
        request_data = {
            'scopes': scopes
        }
        self.strip_none(request_data)
        payload = {
            'requestData': request_data
        }
        return self.call_api('post', f'exceptions/{exc_type}/delete/{exc_id}', body=payload)

class ApiClient(ApiClientBase):
    def __init__(self, host: str, client_id: str, client_secret: str):
        """
        :param host: API host name
        :param client_id: Client ID
        :param client_secret: Client Secret
        """
        super().__init__(host, client_id, client_secret)
        self.token_buffer = 60

    def generate_signature(self, request_id: str, timestamp: str, request_string: str = None) -> str:
        """
        Generate request signature

        :param request_id: Request ID
        :param timestamp: Timestamp
        :param request_string: Request string
        :return: Signature
        """
        if request_string:
            signature_string = f'{request_id}{self.client_id}{timestamp}{request_string}' \
                               f'{self.client_secret}'
        else:
            signature_string = f'{request_id}{self.client_id}{timestamp}{self.client_secret}'
        signature_bytes = signature_string.encode('utf-8')
        signature_base64_bytes = base64.b64encode(signature_bytes)
        signature_hash = hashlib.sha256(signature_base64_bytes).hexdigest()
        return signature_hash

    def headers(self, request_string: str = None, auth: bool = False) -> dict:
        """
        Generate request headers

        :param request_string: Request string
        :param auth: Is authenticated request
        :return: Headers
        """
        request_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        headers = {
            'x-av-req-id': request_id,
            'x-av-app-id': self.client_id,
            'x-av-date': timestamp,
            'x-av-sig': self.generate_signature(request_id, timestamp, request_string)
        }
        if not auth:
            headers['x-av-token'] = self.get_token()
        return headers

    def should_refresh_token(self) -> bool:
        if not self.token:
            return True

        return time.time() + self.token_buffer > self.token_expiry

    @cached_property
    def public_key(self) -> dict:
        """

        :return: Public key JSON data (JWK)
        """
        res = requests.get(f'https://{self.host}/{self.api_version}/public_key')
        res.raise_for_status()
        return res.json()

    def get_token(self) -> str:
        """
        Perform authentication and returns access token

        :return: Token (JWT)
        """
        if not self.should_refresh_token():
            return self.token

        res = requests.get(f'https://{self.host}/{self.api_version}/auth', headers=self.headers(auth=True))
        res.raise_for_status()
        self.token = res.content.decode('utf-8')
        decoded_token = jwt.decode(self.token, self.public_key)
        self.token_expiry = decoded_token['exp']
        return self.token

    def get_path(self, endpoint: str) -> str:
        return '/'.join([self.api_version, endpoint])

    def get_request_string(self, endpoint: str, params: dict = None) -> str:
        request_string = f'/{self.api_version}/{endpoint}'
        if params:
            request_string += f'?{urlencode(params)}'
        return request_string

class CloudInfraApiClient(ApiClientBase):
    def _should_refresh_token(self) -> bool:
        return not self.token or time.time() >= self.token_expiry

    def get_token(self) -> str:
        if self._should_refresh_token():
            payload = {
                "clientId": self.client_id,
                "accessKey": self.client_secret
            }
            timestamp = time.time()

            res = requests.post(f'https://{self.host}/auth/external', json=payload)
            res.raise_for_status()
            data = res.json()['data']
            self.token = data.get('token')
            self.token_expiry = timestamp + float(data.get('expiresIn'))

        print(self.token)
        return self.token

    def headers(self, request_string: str = None, auth: bool = False) -> dict:
        request_id = str(uuid.uuid4())
        token = self.get_token()
        return {
            'Authorization': f'Bearer {token}',
            'x-av-req-id': request_id,
        }

    def get_path(self, endpoint: str) -> str:
        return '/'.join(['app', 'hec-api', self.api_version, endpoint])

    def get_request_string(self, endpoint: str, params: dict = None) -> str:
        return ''

def get_brand_client(brand: str, host, client_id, client_secret):
    if brand == 'checkpoint':
        client = CloudInfraApiClient(host=host, client_id=client_id, client_secret=client_secret)
    elif brand == 'avanan':
        client = ApiClient(host=host, client_id=client_id, client_secret=client_secret)
    else:
        return None
    return client