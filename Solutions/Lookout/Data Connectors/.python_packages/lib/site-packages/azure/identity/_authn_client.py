# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import calendar
import time

from msal import TokenCache

from azure.core.configuration import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    RetryPolicy,
    UserAgentPolicy,
)
from azure.core.pipeline.transport import RequestsTransport, HttpRequest
from ._constants import DEVELOPER_SIGN_ON_CLIENT_ID, DEFAULT_REFRESH_OFFSET, DEFAULT_TOKEN_REFRESH_RETRY_DELAY
from ._internal import get_default_authority, normalize_authority
from ._internal.user_agent import USER_AGENT

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from time import struct_time
    from typing import Any, Dict, Iterable, Mapping, Optional, Union
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy


class AuthnClientBase(ABC):
    """Sans I/O authentication client methods"""

    def __init__(self, endpoint=None, authority=None, tenant=None, **kwargs):  # pylint:disable=unused-argument
        # type: (Optional[str], Optional[str], Optional[str], **Any) -> None
        super(AuthnClientBase, self).__init__()
        if authority and endpoint:
            raise ValueError(
                "'authority' and 'endpoint' are mutually exclusive. 'authority' should be the authority of an AAD"
                + " endpoint, whereas 'endpoint' should be the endpoint's full URL."
            )

        if endpoint:
            self._auth_url = endpoint
        else:
            if not tenant:
                raise ValueError("'tenant' is required")
            authority = normalize_authority(authority) if authority else get_default_authority()
            self._auth_url = "/".join((authority, tenant.strip("/"), "oauth2/v2.0/token"))
        self._cache = kwargs.get("cache") or TokenCache()  # type: TokenCache
        self._token_refresh_retry_delay = DEFAULT_TOKEN_REFRESH_RETRY_DELAY
        self._token_refresh_offset = DEFAULT_REFRESH_OFFSET
        self._last_refresh_time = 0

    @property
    def auth_url(self):
        return self._auth_url

    def should_refresh(self, token):
        # type: (AccessToken) -> bool
        """ check if the token needs refresh or not
        """
        expires_on = int(token.expires_on)
        now = int(time.time())
        if expires_on - now > self._token_refresh_offset:
            return False
        if now - self._last_refresh_time < self._token_refresh_retry_delay:
            return False
        return True

    def get_cached_token(self, scopes):
        # type: (Iterable[str]) -> Optional[AccessToken]
        tokens = self._cache.find(TokenCache.CredentialType.ACCESS_TOKEN, target=list(scopes))
        for token in tokens:
            expires_on = int(token["expires_on"])
            if expires_on > int(time.time()):
                return AccessToken(token["secret"], expires_on)
        return None

    def get_refresh_token_grant_request(self, refresh_token, scopes):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token["secret"],
            "scope": " ".join(scopes),
            "client_id": DEVELOPER_SIGN_ON_CLIENT_ID,
        }
        return self._prepare_request(form_data=data)

    @abc.abstractmethod
    def request_token(self, scopes, method, headers, form_data, params, **kwargs):
        pass

    def _deserialize_and_cache_token(self, response, scopes, request_time):
        # type: (PipelineResponse, Iterable[str], int) -> AccessToken
        """Deserialize and cache an access token from an AAD response"""

        # ContentDecodePolicy sets this, and should have raised if it couldn't deserialize the response
        payload = response.context[ContentDecodePolicy.CONTEXT_NAME]

        if not payload or "access_token" not in payload or not ("expires_in" in payload or "expires_on" in payload):
            if payload and "access_token" in payload:
                payload["access_token"] = "****"
            raise ClientAuthenticationError(
                message="Unexpected response '{}'".format(payload), response=response.http_response
            )

        token = payload["access_token"]

        # AccessToken wants expires_on as an int
        expires_on = payload.get("expires_on") or int(payload["expires_in"]) + request_time  # type: Union[str, int]
        try:
            expires_on = int(expires_on)
        except ValueError:
            # probably an App Service MSI 2017-09-01 response, convert it to epoch seconds
            try:
                t = self._parse_app_service_expires_on(expires_on)  # type: ignore
                expires_on = calendar.timegm(t)
            except ValueError:
                # have a token but don't know when it expires -> treat it as single-use
                expires_on = request_time

        # now we have an int expires_on, ensure the cache entry gets it
        payload["expires_on"] = expires_on

        self._cache.add({"response": payload, "scope": scopes})

        return AccessToken(token, expires_on)

    @staticmethod
    def _parse_app_service_expires_on(expires_on):
        # type: (str) -> struct_time
        """Parse an App Service MSI version 2017-09-01 expires_on value to struct_time.

        This version of the API returns expires_on as a UTC datetime string rather than epoch seconds. The string's
        format depends on the OS. Responses on Windows include AM/PM, for example "1/16/2020 5:24:12 AM +00:00".
        Responses on Linux do not, for example "06/20/2019 02:57:58 +00:00".

        :raises ValueError: ``expires_on`` didn't match an expected format
        """

        # parse the string minus the timezone offset
        if expires_on.endswith(" +00:00"):
            date_string = expires_on[: -len(" +00:00")]
            for format_string in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p"):  # (Linux, Windows)
                try:
                    return time.strptime(date_string, format_string)
                except ValueError:
                    pass

        raise ValueError("'{}' doesn't match the expected format".format(expires_on))

    # TODO: public, factor out of request_token
    def _prepare_request(
        self,
        method="POST",  # type: Optional[str]
        headers=None,  # type: Optional[Mapping[str, str]]
        form_data=None,  # type: Optional[Mapping[str, str]]
        params=None,  # type: Optional[Dict[str, str]]
    ):
        # type: (...) -> HttpRequest
        request = HttpRequest(method, self._auth_url, headers=headers)
        if form_data:
            request.headers["Content-Type"] = "application/x-www-form-urlencoded"
            request.set_formdata_body(form_data)
        if params:
            request.format_parameters(params)
        return request


class AuthnClient(AuthnClientBase):
    """Synchronous authentication client.

    :param str auth_url:
    :param config: Optional configuration for the HTTP pipeline.
    :type config: :class:`azure.core.configuration`
    :param policies: Optional policies for the HTTP pipeline.
    :type policies:
    :param transport: Optional HTTP transport.
    :type transport:
    """

    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(
        self,
        config=None,  # type: Optional[Configuration]
        policies=None,  # type: Optional[Iterable[HTTPPolicy]]
        transport=None,  # type: Optional[HttpTransport]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        config = config or self._create_config(**kwargs)
        policies = policies or [
            ContentDecodePolicy(),
            config.user_agent_policy,
            config.proxy_policy,
            config.retry_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        if not transport:
            transport = RequestsTransport(**kwargs)
        self._pipeline = Pipeline(transport=transport, policies=policies)
        super(AuthnClient, self).__init__(**kwargs)

    def request_token(
        self,
        scopes,  # type: Iterable[str]
        method="POST",  # type: Optional[str]
        headers=None,  # type: Optional[Mapping[str, str]]
        form_data=None,  # type: Optional[Mapping[str, str]]
        params=None,  # type: Optional[Dict[str, str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> AccessToken
        request = self._prepare_request(method, headers=headers, form_data=form_data, params=params)
        request_time = int(time.time())
        self._last_refresh_time = request_time   # no matter succeed or not, update the last refresh time
        response = self._pipeline.run(request, stream=False, **kwargs)
        token = self._deserialize_and_cache_token(response=response, scopes=scopes, request_time=request_time)
        return token

    @staticmethod
    def _create_config(**kwargs):
        # type: (Mapping[str, Any]) -> Configuration
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
        return config
