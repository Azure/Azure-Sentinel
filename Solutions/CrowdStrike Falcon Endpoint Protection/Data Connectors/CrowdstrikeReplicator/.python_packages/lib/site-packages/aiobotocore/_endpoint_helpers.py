import aiohttp.http_exceptions
from aiohttp.client_reqrep import ClientResponse
import asyncio
import botocore.retryhandler
import wrapt


# Monkey patching: We need to insert the aiohttp exception equivalents
# The only other way to do this would be to have another config file :(
_aiohttp_retryable_exceptions = [
    aiohttp.ClientConnectionError,
    aiohttp.ClientPayloadError,
    aiohttp.ServerDisconnectedError,
    aiohttp.http_exceptions.HttpProcessingError,
    asyncio.TimeoutError,
]

botocore.retryhandler.EXCEPTION_MAP['GENERAL_CONNECTION_ERROR'].extend(
    _aiohttp_retryable_exceptions
)


def _text(s, encoding='utf-8', errors='strict'):
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    return s  # pragma: no cover


# Unfortunately aiohttp changed the behavior of streams:
#   github.com/aio-libs/aiohttp/issues/1907
# We need this wrapper until we have a final resolution
class _IOBaseWrapper(wrapt.ObjectProxy):
    def close(self):
        # this stream should not be closed by aiohttp, like 1.x
        pass


# This is similar to botocore.response.StreamingBody
class ClientResponseContentProxy(wrapt.ObjectProxy):
    """Proxy object for content stream of http response.  This is here in case
    you want to pass around the "Body" of the response without closing the
    response itself."""

    def __init__(self, response):
        super().__init__(response.__wrapped__.content)
        self._self_response = response

    # Note: we don't have a __del__ method as the ClientResponse has a __del__
    # which will warn the user if they didn't close/release the response
    # explicitly.  A release here would mean reading all the unread data
    # (which could be very large), and a close would mean being unable to re-
    # use the connection, so the user MUST chose.  Default is to warn + close
    async def __aenter__(self):
        await self._self_response.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._self_response.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def url(self):
        return self._self_response.url

    def close(self):
        self._self_response.close()


class ClientResponseProxy(wrapt.ObjectProxy):
    """Proxy object for http response useful for porting from
    botocore underlying http library."""

    def __init__(self, *args, **kwargs):
        super().__init__(ClientResponse(*args, **kwargs))

        # this matches ClientResponse._body
        self._self_body = None

    @property
    def status_code(self):
        return self.status

    @status_code.setter
    def status_code(self, value):
        # botocore tries to set this, see:
        # https://github.com/aio-libs/aiobotocore/issues/190
        # Luckily status is an attribute we can set
        self.status = value

    @property
    def content(self):
        return self._self_body

    @property
    def raw(self):
        return ClientResponseContentProxy(self)

    async def read(self):
        self._self_body = await self.__wrapped__.read()
        return self._self_body
