import ssl
import sys
import traceback
from urllib.parse import urlparse

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

from ..errors import ErrorMessages, ErrorType, FncClientError
from ..logger import FncClientLogger

CIPHERS_STRING = '@SECLEVEL=1:ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:ECDH+AESGCM:DH+AESGCM:' \
    'ECDH+AES:DH+AES:RSA+ANESGCM:RSA+AES:!aNULL:!eNULL:!MD5:!DSS'
IS_PY3 = sys.version_info[0] == 3
PY_VER_MINOR = sys.version_info[1]


class SSLAdapter(HTTPAdapter):
    """
        A wrapper used for https communication to enable ciphers that are commonly used
        and are not enabled by default
        :return: No data returned
        :rtype: ``None``
    """
    context = create_urllib3_context(ciphers=CIPHERS_STRING)

    def __init__(self, verify=True, **kwargs):
        # type: (bool, dict) -> None
        if not verify and ssl.OPENSSL_VERSION_INFO >= (3, 0, 0, 0):
            self.context.options |= 0x4
        super().__init__(**kwargs)  # type: ignore[arg-type]

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.context
        return super(SSLAdapter, self).proxy_manager_for(*args, **kwargs)


class FncRestClient:
    logger: FncClientLogger
    default_args: dict

    def set_logger(self, logger: FncClientLogger):
        self.logger = logger

    def validate_request(self, req_args: dict):
        raise NotImplementedError()

    def send_request(self, req_args: dict):
        raise NotImplementedError()


class BasicRestClient(FncRestClient):
    http_session = None
    default_args: dict

    def close_http_session(self):
        try:
            if self.http_session:
                self.http_session.close()
                self.http_session = None
        except AttributeError:
            # we ignore exceptions raised due to session not used by the client and hence do not exist in __del__
            pass
        except Exception as e:
            self.logger.error(
                f"Failed to close FncRestClient session with the following error:\n{traceback.format_exc()}")
            raise FncClientError(
                error_type=ErrorType.REQUEST_CLOSING_SESSION_ERROR,
                error_message=ErrorMessages.REQUEST_CLOSING_SESSION_ERROR,
                error_data={'error': e},
                exception=e
            ) from e

    def __del__(self):
        self.close_http_session()

    def _http_request(self, **kwargs):
        if self.http_session is None:
            self._init_request_session()

        return self.http_session.request(**kwargs)

    def _init_request_session(self) -> Session:
        self.http_session = requests.Session()
        self.http_session.mount(
            'http://', SSLAdapter())
        self.http_session.mount(
            'https://', SSLAdapter())

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
        try:
            parsed_uri = urlparse(req_args['url'])
            masked_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

            self.logger.debug(f"Sending request to: {masked_url}")
            response = self._http_request(**req_args)

            self.logger.debug(f"Response received from the API (status_code = {response.status_code})")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Request failed with the following error:\n{traceback.format_exc()}")
            raise FncClientError(
                error_type=ErrorType.REQUEST_CONNECTION_ERROR,
                error_message=ErrorMessages.REQUEST_CONNECTION_ERROR,
                error_data={'url': masked_url, 'error': e},
                exception=e
            ) from e
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request failed with the following error:\n{traceback.format_exc()}")
            raise FncClientError(
                error_type=ErrorType.REQUEST_TIMEOUT_ERROR,
                error_message=ErrorMessages.REQUEST_TIMEOUT_ERROR,
                error_data={'url': masked_url, 'error': e},
                exception=e
            ) from e
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Request failed with the following error:\n{traceback.format_exc()}")
            raise FncClientError(
                error_type=ErrorType.REQUEST_HTTP_ERROR,
                error_message=ErrorMessages.REQUEST_HTTP_ERROR,
                error_data={'url': masked_url, 'error': e},
                exception=e
            ) from e
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed with the following error:\n{traceback.format_exc()}")
            raise FncClientError(
                error_type=ErrorType.REQUEST_ERROR,
                error_message=ErrorMessages.REQUEST_ERROR,
                error_data={'url': masked_url, 'error': e},
                exception=e
            ) from e
        finally:
            self.close_http_session()

        return response
