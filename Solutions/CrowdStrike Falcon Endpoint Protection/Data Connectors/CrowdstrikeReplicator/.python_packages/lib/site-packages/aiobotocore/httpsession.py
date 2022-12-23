import asyncio
import io
import socket
import os
from typing import Dict, Optional

import aiohttp  # lgtm [py/import-and-import-from]
from aiohttp import ClientSSLError, ClientConnectorError, ClientProxyConnectionError, \
    ClientHttpProxyError, ServerTimeoutError, ServerDisconnectedError
from aiohttp.client import URL
from multidict import MultiDict

from botocore.httpsession import ProxyConfiguration, create_urllib3_context, \
    MAX_POOL_CONNECTIONS, InvalidProxiesConfigError, SSLError, \
    EndpointConnectionError, ProxyConnectionError, ConnectTimeoutError, \
    ConnectionClosedError, HTTPClientError, ReadTimeoutError, logger, get_cert_path, \
    ensure_boolean, urlparse, mask_proxy_url

from aiobotocore._endpoint_helpers import _text, _IOBaseWrapper, \
    ClientResponseProxy


class AIOHTTPSession:
    def __init__(
            self,
            verify: bool = True,
            proxies: Dict[str, str] = None,  # {scheme: url}
            timeout: float = None,
            max_pool_connections: int = MAX_POOL_CONNECTIONS,
            socket_options=None,
            client_cert=None,
            proxies_config=None,
            connector_args=None
    ):
        # TODO: handle socket_options
        self._session: Optional[aiohttp.ClientSession] = None
        self._verify = verify
        self._proxy_config = ProxyConfiguration(
            proxies=proxies, proxies_settings=proxies_config
        )
        if isinstance(timeout, (list, tuple)):
            conn_timeout, read_timeout = timeout
        else:
            conn_timeout = read_timeout = timeout

        timeout = aiohttp.ClientTimeout(
            sock_connect=conn_timeout,
            sock_read=read_timeout
        )

        self._cert_file = None
        self._key_file = None
        if isinstance(client_cert, str):
            self._cert_file = client_cert
        elif isinstance(client_cert, tuple):
            self._cert_file, self._key_file = client_cert

        self._timeout = timeout
        self._connector_args = connector_args
        if self._connector_args is None:
            # AWS has a 20 second idle timeout:
            #   https://forums.aws.amazon.com/message.jspa?messageID=215367
            # aiohttp default timeout is 30s so set something reasonable here
            self._connector_args = dict(keepalive_timeout=12)

        self._max_pool_connections = max_pool_connections
        self._socket_options = socket_options
        if socket_options is None:
            self._socket_options = []

        # aiohttp handles 100 continue so we shouldn't need AWSHTTP[S]ConnectionPool
        # it also pools by host so we don't need a manager, and can pass proxy via
        # request so don't need proxy manager

        ssl_context = None
        if bool(verify):
            if proxies:
                proxies_settings = self._proxy_config.settings
                ssl_context = self._setup_proxy_ssl_context(proxies_settings)
                # TODO: add support for
                #    proxies_settings.get('proxy_use_forwarding_for_https')
            else:
                ssl_context = self._get_ssl_context()

                # inline self._setup_ssl_cert
                ca_certs = get_cert_path(verify)
                if ca_certs:
                    ssl_context.load_verify_locations(ca_certs, None, None)

        self._connector = aiohttp.TCPConnector(
            limit=max_pool_connections,
            verify_ssl=bool(verify),
            ssl=ssl_context,
            **connector_args)

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=self._timeout,
            skip_auto_headers={'CONTENT-TYPE'},
            response_class=ClientResponseProxy,
            auto_decompress=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
            self._session = None

    async def close(self):
        await self.__aexit__(None, None, None)

    def _get_ssl_context(self):
        ssl_context = create_urllib3_context()
        if self._cert_file:
            ssl_context.load_cert_chain(self._cert_file, self._key_file)
        return ssl_context

    def _setup_proxy_ssl_context(self, proxies_settings):
        proxy_ca_bundle = proxies_settings.get('proxy_ca_bundle')
        proxy_cert = proxies_settings.get('proxy_client_cert')
        if proxy_ca_bundle is None and proxy_cert is None:
            return None

        context = self._get_ssl_context()
        try:
            # urllib3 disables this by default but we need
            # it for proper proxy tls negotiation.
            context.check_hostname = True
            if proxy_ca_bundle is not None:
                context.load_verify_locations(cafile=proxy_ca_bundle)

            if isinstance(proxy_cert, tuple):
                context.load_cert_chain(proxy_cert[0], keyfile=proxy_cert[1])
            elif isinstance(proxy_cert, str):
                context.load_cert_chain(proxy_cert)

            return context
        except IOError as e:
            raise InvalidProxiesConfigError(error=e)

    async def send(self, request):
        proxy_url = self._proxy_config.proxy_url_for(request.url)
        proxy_headers = self._proxy_config.proxy_headers_for(request.url)

        try:
            url = request.url
            headers = request.headers
            data = request.body

            if ensure_boolean(
                os.environ.get('BOTO_EXPERIMENTAL__ADD_PROXY_HOST_HEADER', '')
            ):
                # This is currently an "experimental" feature which provides
                # no guarantees of backwards compatibility. It may be subject
                # to change or removal in any patch version. Anyone opting in
                # to this feature should strictly pin botocore.
                host = urlparse(request.url).hostname
                proxy_headers['host'] = host

            # https://github.com/boto/botocore/issues/1255
            headers['Accept-Encoding'] = 'identity'

            headers_ = MultiDict(
                (z[0], _text(z[1], encoding='utf-8')) for z in headers.items())

            if isinstance(data, io.IOBase):
                data = _IOBaseWrapper(data)

            url = URL(url, encoded=True)
            resp = await self._session.request(
                request.method, url=url, headers=headers_, data=data, proxy=proxy_url,
                proxy_headers=proxy_headers
            )

            if not request.stream_output:
                # Cause the raw stream to be exhausted immediately. We do it
                # this way instead of using preload_content because
                # preload_content will never buffer chunked responses
                await resp.read()

            return resp
        except ClientSSLError as e:
            raise SSLError(endpoint_url=request.url, error=e)
        except (ClientConnectorError, socket.gaierror) as e:
            raise EndpointConnectionError(endpoint_url=request.url, error=e)
        except (ClientProxyConnectionError, ClientHttpProxyError) as e:
            raise ProxyConnectionError(proxy_url=mask_proxy_url(proxy_url), error=e)
        except ServerTimeoutError as e:
            raise ConnectTimeoutError(endpoint_url=request.url, error=e)
        except asyncio.TimeoutError as e:
            raise ReadTimeoutError(endpoint_url=request.url, error=e)
        except (ServerDisconnectedError, aiohttp.ClientPayloadError) as e:
            raise ConnectionClosedError(
                error=e,
                request=request,
                endpoint_url=request.url
            )
        except Exception as e:
            message = 'Exception received when sending urllib3 HTTP request'
            logger.debug(message, exc_info=True)
            raise HTTPClientError(error=e)
