# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Dict, List, Optional, Any
import logging
from io import BytesIO, StringIO
from os import linesep
from urllib.parse import ParseResult, urlparse, unquote_to_bytes
from wsgiref.headers import Headers

from ._abc import Context
from ._http import HttpRequest, HttpResponse
from ._thirdparty.werkzeug._compat import string_types, wsgi_encoding_dance


class WsgiRequest:
    _environ_cache: Optional[Dict[str, Any]] = None

    def __init__(self,
                 func_req: HttpRequest,
                 func_ctx: Optional[Context] = None):
        url: ParseResult = urlparse(func_req.url)
        func_req_body = func_req.get_body() or b''

        # Convert function request headers to lowercase header
        self._lowercased_headers = {
            k.lower(): v for k, v in func_req.headers.items()
        }

        # Implement interfaces for PEP 3333 environ
        self.request_method = getattr(func_req, 'method', None)
        self.script_name = ''
        self.path_info = (
            unquote_to_bytes(getattr(url, 'path', None))  # type: ignore
            .decode('latin-1' if type(self) is WsgiRequest else 'utf-8')
        )

        self.query_string = getattr(url, 'query', None)
        self.content_type = self._lowercased_headers.get('content-type')
        self.content_length = str(len(func_req_body))
        self.server_name = getattr(url, 'hostname', None)
        self.server_port = str(self._get_port(url, self._lowercased_headers))
        self.server_protocol = 'HTTP/1.1'

        # Propagate http request headers into HTTP_ environ
        self._http_environ: Dict[str, str] = self._get_http_headers(
            func_req.headers
        )

        # Wsgi environ
        self.wsgi_version = (1, 0)
        self.wsgi_url_scheme = url.scheme
        self.wsgi_input = BytesIO(func_req_body)
        self.wsgi_multithread = False
        self.wsgi_multiprocess = False
        self.wsgi_run_once = False

        # Azure Functions context
        self.af_function_directory = getattr(func_ctx,
                                             'function_directory', None)
        self.af_function_name = getattr(func_ctx, 'function_name', None)
        self.af_invocation_id = getattr(func_ctx, 'invocation_id', None)
        self.af_thread_local_storage = getattr(func_ctx,
                                               'thread_local_storage',
                                               None)
        self.af_trace_context = getattr(func_ctx, 'trace_context', None)
        self.af_retry_context = getattr(func_ctx, 'retry_context', None)

    def to_environ(self, errors_buffer: StringIO) -> Dict[str, Any]:
        if self._environ_cache is not None:
            return self._environ_cache

        environ = {
            'REQUEST_METHOD': self.request_method,
            'SCRIPT_NAME': self.script_name,
            'PATH_INFO': self.path_info,
            'QUERY_STRING': self.query_string,
            'CONTENT_TYPE': self.content_type,
            'CONTENT_LENGTH': self.content_length,
            'SERVER_NAME': self.server_name,
            'SERVER_PORT': self.server_port,
            'SERVER_PROTOCOL': self.server_protocol,
            'wsgi.version': self.wsgi_version,
            'wsgi.url_scheme': self.wsgi_url_scheme,
            'wsgi.input': self.wsgi_input,
            'wsgi.errors': errors_buffer,
            'wsgi.multithread': self.wsgi_multithread,
            'wsgi.multiprocess': self.wsgi_multiprocess,
            'wsgi.run_once': self.wsgi_run_once,
            'azure_functions.function_directory': self.af_function_directory,
            'azure_functions.function_name': self.af_function_name,
            'azure_functions.invocation_id': self.af_invocation_id,
            'azure_functions.thread_local_storage':
                self.af_thread_local_storage,
            'azure_functions.trace_context': self.af_trace_context,
            'azure_functions.retry_context': self.af_retry_context
        }
        environ.update(self._http_environ)

        # Ensure WSGI string fits in IOS-8859-1 code points
        for k, v in environ.items():
            if isinstance(v, string_types):
                environ[k] = wsgi_encoding_dance(v)

        # Remove None values
        self._environ_cache = {
            k: v for k, v in environ.items() if v is not None
        }
        return self._environ_cache

    def _get_port(self, parsed_url, lowercased_headers: Dict[str, str]) -> int:
        port: int = 80
        if lowercased_headers.get('x-forwarded-port'):
            return int(lowercased_headers['x-forwarded-port'])
        elif getattr(parsed_url, 'port', None):
            return int(parsed_url.port)
        elif parsed_url.scheme == 'https':
            return 443
        return port

    def _get_http_headers(self,
                          func_headers: Dict[str, str]) -> Dict[str, str]:
        # Content-Type -> HTTP_CONTENT_TYPE
        return {f'HTTP_{k.upper().replace("-", "_")}': v for k, v in
                func_headers.items()}


class WsgiResponse:
    def __init__(self):
        self._status = ''
        self._status_code = 0
        self._headers = {}
        self._buffer: List[bytes] = []

    @classmethod
    def from_app(cls, app, environ) -> 'WsgiResponse':
        res = cls()
        res._buffer = [x or b'' for x in app(environ, res._start_response)]
        return res

    def to_func_response(self) -> HttpResponse:
        lowercased_headers = {k.lower(): v for k, v in self._headers.items()}
        return HttpResponse(
            body=b''.join(self._buffer),
            status_code=self._status_code,
            headers=self._headers,
            mimetype=lowercased_headers.get('content-type'),
            charset=lowercased_headers.get('content-encoding')
        )

    # PEP 3333 start response implementation
    def _start_response(self, status: str, response_headers: List[Any]):
        self._status = status
        self._headers = Headers(response_headers)  # type: ignore
        self._status_code = int(self._status.split(' ')[0])  # 200 OK


class WsgiMiddleware:
    """This middleware is to adapt a WSGI supported Python server
    framework into Azure Functions. It can be used by either calling the
    .handle() function or exposing the .main property in a HttpTrigger.
    """
    _logger = logging.getLogger('azure.functions.WsgiMiddleware')
    _usage_reported = False

    def __init__(self, app):
        """Instantiate a WSGI middleware to convert Azure Functions HTTP
        request into WSGI Python object. Example on handling WSGI app in a HTTP
        trigger by overwriting the .main() method:

        import azure.functions as func

        from FlaskApp import app

        main = func.WsgiMiddleware(app.wsgi_app).main
        """
        if not self._usage_reported:
            self._logger.info("Instantiating Azure Functions WSGI middleware.")
            self._usage_reported = True

        self._app = app
        self._wsgi_error_buffer = StringIO()
        self.main = self._handle

    def handle(self, req: HttpRequest, context: Optional[Context] = None):
        """Method to convert an Azure Functions HTTP request into a WSGI
        Python object. Example on handling WSGI app in a HTTP trigger by
        calling .handle() in .main() method:

        import azure.functions as func

        from FlaskApp import app

        def main(req, context):
            return func.WsgiMiddleware(app.wsgi_app).handle(req, context)
        """
        return self._handle(req, context)

    def _handle(self, req, context):
        wsgi_request = WsgiRequest(req, context)
        environ = wsgi_request.to_environ(self._wsgi_error_buffer)
        wsgi_response = WsgiResponse.from_app(self._app, environ)
        self._handle_errors(wsgi_response)
        return wsgi_response.to_func_response()

    def _handle_errors(self, wsgi_response):
        if self._wsgi_error_buffer.tell() > 0:
            self._wsgi_error_buffer.seek(0)
            error_message = linesep.join(
                self._wsgi_error_buffer.readline()
            )
            raise Exception(error_message)

        if wsgi_response._status_code >= 500:
            raise Exception(b''.join(wsgi_response._buffer))
