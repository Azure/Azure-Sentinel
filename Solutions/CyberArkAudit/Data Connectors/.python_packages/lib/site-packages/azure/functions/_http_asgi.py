# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import asyncio
from asyncio import Event, Queue
from warnings import warn
from wsgiref.headers import Headers

from ._abc import Context
from ._http import HttpRequest, HttpResponse
from ._http_wsgi import WsgiRequest

ASGI_VERSION = "2.1"
ASGI_SPEC_VERSION = "2.1"


class AsgiRequest(WsgiRequest):
    def __init__(self, func_req: HttpRequest,
                 func_ctx: Optional[Context] = None):
        self.asgi_version = ASGI_VERSION
        self.asgi_spec_version = ASGI_SPEC_VERSION
        self._headers = func_req.headers
        super().__init__(func_req, func_ctx)

    def _get_encoded_http_headers(self) -> List[Tuple[bytes, bytes]]:
        return [(k.encode("utf8"), v.encode("utf8"))
                for k, v in self._headers.items()]

    def _get_server_address(self):
        if self.server_name is not None:
            return (self.server_name, int(self.server_port))
        return None

    def to_asgi_http_scope(self):
        if self.path_info is not None:
            _raw_path = self.path_info.encode("utf-8")
        else:
            _raw_path = b''
        if self.query_string is not None:
            _query_string = self.query_string.encode("utf-8")
        else:
            _query_string = b''

        return {
            "type": "http",
            "asgi.version": self.asgi_version,
            "asgi.spec_version": self.asgi_spec_version,
            "http_version": "1.1",
            "method": self.request_method,
            "scheme": "https",
            "path": self.path_info,
            "raw_path": _raw_path,
            "query_string": _query_string,
            "root_path": self.script_name,
            "headers": self._get_encoded_http_headers(),
            "server": self._get_server_address(),
            "client": None,
            "azure_functions.function_directory": self.af_function_directory,
            "azure_functions.function_name": self.af_function_name,
            "azure_functions.invocation_id": self.af_invocation_id,
            "azure_functions.thread_local_storage":
                self.af_thread_local_storage,
            "azure_functions.trace_context": self.af_trace_context,
            "azure_functions.retry_context": self.af_retry_context
        }
        # Notes, missing client name, port


class AsgiResponse:
    def __init__(self):
        self._status_code = 0
        self._headers: Union[Headers, Dict] = {}
        self._buffer: List[bytes] = []
        self._request_body: Optional[bytes] = b""
        self._has_received_response: bool = False

    @classmethod
    async def from_app(cls, app, scope: Dict[str, Any],
                       body: bytes) -> "AsgiResponse":
        res = cls()
        res._request_body = body
        await app(scope, res._receive, res._send)
        return res

    def to_func_response(self) -> HttpResponse:
        lowercased_headers = {k.lower(): v for k, v in self._headers.items()}
        return HttpResponse(
            body=b"".join(self._buffer),
            status_code=self._status_code,
            headers=self._headers,  # type: ignore
            mimetype=lowercased_headers.get("content-type"),
            charset=lowercased_headers.get("content-encoding"),
        )

    def _handle_http_response_start(self, message: Dict[str, Any]):
        self._headers = Headers(
            [(k.decode(), v.decode())
             for k, v in message["headers"]])
        self._status_code = message["status"]

    def _handle_http_response_body(self, message: Dict[str, Any]):
        self._buffer.append(message["body"])
        self._has_received_response = not message.get("more_body", False)
        # XXX : Chunked bodies not supported, see
        # https://github.com/Azure/azure-functions-host/issues/4926

    async def _receive(self):
        if self._request_body is not None:
            reply = {
                "type": "http.request",
                "body": self._request_body,
                "more_body": False,
            }
            self._request_body = None
            return reply
        else:
            while not self._has_received_response:
                await asyncio.sleep(0.1)
            return {
                "type": "http.disconnect",
            }

    async def _send(self, message):
        logging.debug("Received %s from ASGI worker.", message)
        if message["type"] == "http.response.start":
            self._handle_http_response_start(message)
        elif message["type"] == "http.response.body":
            self._handle_http_response_body(message)
        elif message["type"] == "http.disconnect":
            pass  # Nothing todo here


class AsgiMiddleware:
    """This middleware is to adapt an ASGI supported Python server
    framework into Azure Functions. It can be used by either calling the
    .handle() function or exposing the .main property in a HttpTrigger.
    """
    _logger = logging.getLogger('azure.functions.AsgiMiddleware')
    _usage_reported = False

    def __init__(self, app):
        """Instantiate an ASGI middleware to convert Azure Functions HTTP
        request into ASGI Python object. Example on handling ASGI app in a HTTP
        trigger by overwriting the .main() method:

        import azure.functions as func

        from FastapiApp import app

        main = func.AsgiMiddleware(app).main
        """
        if not self._usage_reported:
            self._logger.debug("Starting Azure Functions ASGI middleware.")
            self._usage_reported = True

        self._app = app
        self.main = self._handle
        self.state = {}
        self.lifespan_receive_queue: Optional[Queue] = None
        self.lifespan_startup_event: Optional[Event] = None
        self.lifespan_shutdown_event: Optional[Event] = None
        self._startup_succeeded = False

    def handle(self, req: HttpRequest, context: Optional[Context] = None):
        """Deprecated. Please use handle_async instead:

        import azure.functions as func

        from FastapiApp import app

        async def main(req, context):
            return await func.AsgiMiddleware(app).handle_async(req, context)
        """
        warn("handle() is deprecated. Please await .handle_async() instead.",
             DeprecationWarning, stacklevel=2)
        self._logger.warning(
            "handle() is deprecated. Please `await .handle_async()` instead.")
        return self._handle(req, context)

    def _handle(self, req, context):
        asgi_request = AsgiRequest(req, context)
        scope = asgi_request.to_asgi_http_scope()
        asgi_response = asyncio.run(
            AsgiResponse.from_app(self._app, scope, req.get_body())
        )

        return asgi_response.to_func_response()

    async def handle_async(self,
                           req: HttpRequest,
                           context: Optional[Context] = None):
        """Method to convert an Azure Functions HTTP request into a ASGI
        Python object. Example on handling ASGI app in a HTTP trigger by
        calling .handle_async() in .main() method:

            import azure.functions as func

            from FastapiApp import app

            async def main(req, context):
                return await func.AsgiMiddleware(app).handle_async(req,
                                                                   context)
        """
        return await self._handle_async(req, context)

    async def _handle_async(self, req, context):
        asgi_request = AsgiRequest(req, context)
        scope = asgi_request.to_asgi_http_scope()
        asgi_response = await AsgiResponse.from_app(self._app,
                                                    scope,
                                                    req.get_body())
        return asgi_response.to_func_response()

    async def _lifespan_receive(self):
        if not self.lifespan_receive_queue:
            raise RuntimeError("notify_startup() must be called first.")
        return await self.lifespan_receive_queue.get()

    async def _lifespan_send(self, message):
        logging.debug("Received lifespan message %s.", message)
        if not self.lifespan_startup_event or not self.lifespan_shutdown_event:
            raise RuntimeError("notify_startup() must be called first.")
        if message["type"] == "lifespan.startup.complete":
            self.lifespan_startup_event.set()
            self._startup_succeeded = True
        elif message["type"] == "lifespan.shutdown.complete":
            self.lifespan_shutdown_event.set()
        elif message["type"] == "lifespan.startup.failed":
            self.lifespan_startup_event.set()
            self._startup_succeeded = False
            if message.get("message"):
                self._logger.error("Failed ASGI startup with message '%s'.",
                                   message["message"])
            else:
                self._logger.error("Failed ASGI startup event.")
        elif message["type"] == "lifespan.shutdown.failed":
            self.lifespan_shutdown_event.set()
            if message.get("message"):
                self._logger.error("Failed ASGI shutdown with message '%s'.",
                                   message["message"])
            else:
                self._logger.error("Failed ASGI shutdown event.")

    async def _lifespan_main(self):
        scope = {
            "type": "lifespan",
            "asgi.version": ASGI_VERSION,
            "asgi.spec_version": ASGI_SPEC_VERSION,
            "state": self.state,
        }
        if not self.lifespan_startup_event or not self.lifespan_shutdown_event:
            raise RuntimeError("notify_startup() must be called first.")
        try:
            await self._app(scope, self._lifespan_receive, self._lifespan_send)
        finally:
            self.lifespan_startup_event.set()
            self.lifespan_shutdown_event.set()

    async def notify_startup(self):
        """Notify the ASGI app that the server has started."""
        self._logger.debug("Notifying ASGI app of startup.")

        # Initialize signals and queues
        if not self.lifespan_receive_queue:
            self.lifespan_receive_queue = Queue()
        if not self.lifespan_startup_event:
            self.lifespan_startup_event = Event()
        if not self.lifespan_shutdown_event:
            self.lifespan_shutdown_event = Event()

        startup_event = {"type": "lifespan.startup"}
        await self.lifespan_receive_queue.put(startup_event)
        task = asyncio.create_task(self._lifespan_main())  # NOQA
        await self.lifespan_startup_event.wait()
        return self._startup_succeeded

    async def notify_shutdown(self):
        """Notify the ASGI app that the server is shutting down."""
        if not self.lifespan_receive_queue or not self.lifespan_shutdown_event:
            raise RuntimeError("notify_startup() must be called first.")

        self._logger.debug("Notifying ASGI app of shutdown.")
        shutdown_event = {"type": "lifespan.shutdown"}
        await self.lifespan_receive_queue.put(shutdown_event)
        await self.lifespan_shutdown_event.wait()
