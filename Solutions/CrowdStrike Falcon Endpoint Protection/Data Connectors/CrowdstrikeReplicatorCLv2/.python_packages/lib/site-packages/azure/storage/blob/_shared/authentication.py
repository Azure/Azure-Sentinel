# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import sys

try:
    from urllib.parse import urlparse, unquote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import unquote # type: ignore

try:
    from yarl import URL
except ImportError:
    pass

try:
    from azure.core.pipeline.transport import AioHttpTransport
except ImportError:
    AioHttpTransport = None

from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy

from . import sign_string


logger = logging.getLogger(__name__)



# wraps a given exception with the desired exception type
def _wrap_exception(ex, desired_type):
    msg = ""
    if ex.args:
        msg = ex.args[0]
    if sys.version_info >= (3,):
        # Automatic chaining in Python 3 means we keep the trace
        return desired_type(msg)
    # There isn't a good solution in 2 for keeping the stack trace
    # in general, or that will not result in an error in 3
    # However, we can keep the previous error type and message
    # TODO: In the future we will log the trace
    return desired_type('{}: {}'.format(ex.__class__.__name__, msg))


class AzureSigningError(ClientAuthenticationError):
    """
    Represents a fatal error when attempting to sign a request.
    In general, the cause of this exception is user error. For example, the given account key is not valid.
    Please visit https://docs.microsoft.com/en-us/azure/storage/common/storage-create-storage-account for more info.
    """


# pylint: disable=no-self-use
class SharedKeyCredentialPolicy(SansIOHTTPPolicy):

    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key
        super(SharedKeyCredentialPolicy, self).__init__()

    @staticmethod
    def _get_headers(request, headers_to_sign):
        headers = dict((name.lower(), value) for name, value in request.http_request.headers.items() if value)
        if 'content-length' in headers and headers['content-length'] == '0':
            del headers['content-length']
        return '\n'.join(headers.get(x, '') for x in headers_to_sign) + '\n'

    @staticmethod
    def _get_verb(request):
        return request.http_request.method + '\n'

    def _get_canonicalized_resource(self, request):
        uri_path = urlparse(request.http_request.url).path
        try:
            if isinstance(request.context.transport, AioHttpTransport) or \
                    isinstance(getattr(request.context.transport, "_transport", None), AioHttpTransport) or \
                    isinstance(getattr(getattr(request.context.transport, "_transport", None), "_transport", None),
                               AioHttpTransport):
                uri_path = URL(uri_path)
                return '/' + self.account_name + str(uri_path)
        except TypeError:
            pass
        return '/' + self.account_name + uri_path

    @staticmethod
    def _get_canonicalized_headers(request):
        string_to_sign = ''
        x_ms_headers = []
        for name, value in request.http_request.headers.items():
            if name.startswith('x-ms-'):
                x_ms_headers.append((name.lower(), value))
        x_ms_headers.sort()
        for name, value in x_ms_headers:
            if value is not None:
                string_to_sign += ''.join([name, ':', value, '\n'])
        return string_to_sign

    @staticmethod
    def _get_canonicalized_resource_query(request):
        sorted_queries = list(request.http_request.query.items())
        sorted_queries.sort()

        string_to_sign = ''
        for name, value in sorted_queries:
            if value is not None:
                string_to_sign += '\n' + name.lower() + ':' + unquote(value)

        return string_to_sign

    def _add_authorization_header(self, request, string_to_sign):
        try:
            signature = sign_string(self.account_key, string_to_sign)
            auth_string = 'SharedKey ' + self.account_name + ':' + signature
            request.http_request.headers['Authorization'] = auth_string
        except Exception as ex:
            # Wrap any error that occurred as signing error
            # Doing so will clarify/locate the source of problem
            raise _wrap_exception(ex, AzureSigningError)

    def on_request(self, request):
        string_to_sign = \
            self._get_verb(request) + \
            self._get_headers(
                request,
                [
                    'content-encoding', 'content-language', 'content-length',
                    'content-md5', 'content-type', 'date', 'if-modified-since',
                    'if-match', 'if-none-match', 'if-unmodified-since', 'byte_range'
                ]
            ) + \
            self._get_canonicalized_headers(request) + \
            self._get_canonicalized_resource(request) + \
            self._get_canonicalized_resource_query(request)

        self._add_authorization_header(request, string_to_sign)
        #logger.debug("String_to_sign=%s", string_to_sign)
