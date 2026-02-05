from fnc.api import  FncRestClient
from fnc.errors import ErrorMessages, ErrorType, FncClientError
import requests

class FncSentinelRestClient(FncRestClient):
    def validate_request(self, req_args: dict):
        if not req_args or 'url' not in req_args:
            raise FncClientError(
                error_type=ErrorType.REQUEST_VALIDATION_ERROR,
                error_message=ErrorMessages.REQUEST_URL_NOT_PROVIDED
            )

        if 'method' not in req_args:
            raise FncClientError(
                error_type=ErrorType.REQUEST_VALIDATION_ERROR,
                error_message=ErrorMessages.REQUEST_METHOD_NOT_PROVIDED
            )

    def send_request(self, req_args: dict = None):
        url = req_args['url']
        method = req_args['method']
        headers = req_args.get('headers', {})
        timeout = req_args.get('timeout', 70)
        verify = req_args.get('verify', True)
        parameters = req_args.get('params', {})
        json = req_args.get('json', None)
        data = req_args.get('data', None)
        payload = json or data
        response = requests.request(method, url, headers=headers, timeout=timeout, params=parameters, json=payload, verify=verify)
        return response