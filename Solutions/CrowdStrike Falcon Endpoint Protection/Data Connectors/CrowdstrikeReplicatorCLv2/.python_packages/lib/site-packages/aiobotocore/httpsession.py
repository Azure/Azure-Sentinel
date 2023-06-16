import asyncio
import io
import os
import socket
from typing import Dict, Optional

import aiohttp  # lgtm [py/import-and-import-from]
from aiohttp import (
    ClientConnectionError,
    ClientConnectorError,
    ClientHttpProxyError,
    ClientProxyConnectionError,
    ClientSSLError,
    ServerDisconnectedError,
    ServerTimeoutError,
)
from aiohttp.client import URL
from botocore.httpsession import (
    MAX_POOL_CONNECTIONS,
    ConnectionClosedError,
    ConnectTimeoutError,
    EndpointConnectionError,
    HTTPClientError,
    InvalidProxiesConfigError,
    LocationParseError,
    ProxyConfiguration,
    ProxyConnectionError,
    ReadTimeoutError,
    SSLError,
    _is_ipaddress,
    create_urllib3_context,
    ensure_boolean,
    get_cert_path,
    logger,
    mask_proxy_url,
    parse_url,
    urlparse,
)
from multidict import CIMultiDict

import aiobotocore.awsrequest
from aiobotocore._endpoint_helpers import _IOBaseWrapper, _text


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
        connector_args=None,
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
            sock_connect=conn_timeout, sock_read=read_timeout
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

        self._create_connector = lambda: aiohttp.TCPConnector(
            limit=max_pool_connections,
            verify_ssl=bool(verify),
            ssl=ssl_context,
            **self._connector_args
        )
        self._connector = None

    async def __aenter__(self):
        assert not self._session and not self._connector

        self._connector = self._create_connector()

        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=self._timeout,
            skip_auto_headers={'CONTENT-TYPE'},
            auto_decompress=False,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
            self._session = None
            self._connector = None

    def _get_ssl_context(self):
        ssl_context = create_urllib3_context()
        if self._cert_file:
            ssl_context.load_cert_chain(self._cert_file, self._key_file)
        return ssl_context

    def _setup_proxy_ssl_context(self, proxy_url):
        proxies_settings = self._proxy_config.settings
        proxy_ca_bundle = proxies_settings.get('proxy_ca_bundle')
        proxy_cert = proxies_settings.get('proxy_client_cert')
        if proxy_ca_bundle is None and proxy_cert is None:
            return None

        context = self._get_ssl_context()
        try:
            url = parse_url(proxy_url)
            # urllib3 disables this by default but we need it for proper
            # proxy tls negotiation when proxy_url is not an IP Address
            if not _is_ipaddress(url.host):
                context.check_hostname = True
            if proxy_ca_bundle is not None:
                context.load_verify_locations(cafile=proxy_ca_bundle)

            if isinstance(proxy_cert, tuple):
                context.load_cert_chain(proxy_cert[0], keyfile=proxy_cert[1])
            elif isinstance(proxy_cert, str):
                context.load_cert_chain(proxy_cert)

            return context
        except (OSError, LocationParseError) as e:
            raise InvalidProxiesConfigError(error=e)

    async def close(self):
        await self.__aexit__(None, None, None)

    async def send(self, request):
        try:
            proxy_url = self._proxy_config.proxy_url_for(request.url)
            proxy_headers = self._proxy_config.proxy_headers_for(request.url)
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

            headers_ = CIMultiDict(
                (z[0], _text(z[1], encoding='utf-8')) for z in headers.items()
            )

            # https://github.com/boto/botocore/issues/1255
            headers_['Accept-Encoding'] = 'identity'

            chunked = None
            if headers_.get('Transfer-Encoding', '').lower() == 'chunked':
                # aiohttp wants chunking as a param, and not a header
                headers_.pop('Transfer-Encoding', '')
                chunked = True

            if isinstance(data, io.IOBase):
                data = _IOBaseWrapper(data)

            url = URL(url, encoded=True)
            response = await self._session.request(
                request.method,
                url=url,
                chunked=chunked,
                headers=headers_,
                data=data,
                proxy=proxy_url,
                proxy_headers=proxy_headers,
            )

            http_response = aiobotocore.awsrequest.AioAWSResponse(
                str(response.url), response.status, response.headers, response
            )

            if not request.stream_output:
                # Cause the raw stream to be exhausted immediately. We do it
                # this way instead of using preload_content because
                # preload_content will never buffer chunked responses
                await http_response.content

            return http_response
        except ClientSSLError as e:
            raise SSLError(endpoint_url=request.url, error=e)
        except (ClientProxyConnectionError, ClientHttpProxyError) as e:
            raise ProxyConnectionError(
                proxy_url=mask_proxy_url(proxy_url), error=e
            )
        except (
            ServerDisconnectedError,
            aiohttp.ClientPayloadError,
            aiohttp.http_exceptions.BadStatusLine,
        ) as e:
            raise ConnectionClosedError(
                error=e, request=request, endpoint_url=request.url
            )
        except ServerTimeoutError as e:
            if str(e).lower().startswith('connect'):
                raise ConnectTimeoutError(endpoint_url=request.url, error=e)
            else:
                raise ReadTimeoutError(endpoint_url=request.url, error=e)
        except (
            ClientConnectorError,
            ClientConnectionError,
            socket.gaierror,
        ) as e:
            raise EndpointConnectionError(endpoint_url=request.url, error=e)
        except asyncio.TimeoutError as e:
            raise ReadTimeoutError(endpoint_url=request.url, error=e)
        except Exception as e:
            message = 'Exception received when sending urllib3 HTTP request'
            logger.debug(message, exc_info=True)
            raise HTTPClientError(error=e)
