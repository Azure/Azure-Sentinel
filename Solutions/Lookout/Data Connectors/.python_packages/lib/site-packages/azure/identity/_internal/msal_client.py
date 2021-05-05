# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import six

from azure.core.configuration import Configuration
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
from azure.core.pipeline.transport import HttpRequest, RequestsTransport

from .user_agent import USER_AGENT

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Dict, List, Optional, Union
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.policies import HTTPPolicy, SansIOHTTPPolicy
    from azure.core.pipeline.transport import HttpTransport

    PolicyList = List[Union[HTTPPolicy, SansIOHTTPPolicy]]
    RequestData = Union[Dict[str, str], str]


class MsalResponse(object):
    """Wraps HttpResponse according to msal.oauth2cli.http"""

    def __init__(self, response):
        # type: (PipelineResponse) -> None
        self._response = response

    @property
    def status_code(self):
        # type: () -> int
        return self._response.http_response.status_code

    @property
    def text(self):
        # type: () -> str
        return self._response.http_response.text(encoding="utf-8")

    def raise_for_status(self):
        if self.status_code < 400:
            return

        if ContentDecodePolicy.CONTEXT_NAME in self._response.context:
            content = self._response.context[ContentDecodePolicy.CONTEXT_NAME]
            if "error" in content or "error_description" in content:
                message = "Authentication failed: {}".format(content.get("error_description") or content.get("error"))
            else:
                for secret in ("access_token", "refresh_token"):
                    if secret in content:
                        content[secret] = "***"
                message = 'Unexpected response from Azure Active Directory: "{}"'.format(content)
        else:
            message = "Unexpected response from Azure Active Directory"

        raise ClientAuthenticationError(message=message, response=self._response.http_response)


class MsalClient(object):
    """Wraps Pipeline according to msal.oauth2cli.http"""

    def __init__(self, **kwargs):  # pylint:disable=missing-client-constructor-parameter-credential
        # type: (**Any) -> None
        self._pipeline = _build_pipeline(**kwargs)

    def post(self, url, params=None, data=None, headers=None, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Optional[Dict[str, str]], RequestData, Optional[Dict[str, str]], **Any) -> MsalResponse
        request = HttpRequest("POST", url, headers=headers)
        if params:
            request.format_parameters(params)
        if data:
            if isinstance(data, dict):
                request.headers["Content-Type"] = "application/x-www-form-urlencoded"
                request.set_formdata_body(data)
            elif isinstance(data, six.text_type):
                body_bytes = six.ensure_binary(data)
                request.set_bytes_body(body_bytes)
            else:
                raise ValueError('expected "data" to be text or a dict')

        response = self._pipeline.run(request)
        return MsalResponse(response)

    def get(self, url, params=None, headers=None, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Optional[Dict[str, str]], Optional[Dict[str, str]], **Any) -> MsalResponse
        request = HttpRequest("GET", url, headers=headers)
        if params:
            request.format_parameters(params)
        response = self._pipeline.run(request)
        return MsalResponse(response)


def _create_config(**kwargs):
    # type: (Any) -> Configuration
    config = Configuration(**kwargs)
    config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
    config.retry_policy = RetryPolicy(**kwargs)
    config.proxy_policy = ProxyPolicy(**kwargs)
    config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
    return config


def _build_pipeline(config=None, policies=None, transport=None, **kwargs):
    # type: (Optional[Configuration], Optional[PolicyList], Optional[HttpTransport], **Any) -> Pipeline
    config = config or _create_config(**kwargs)

    if policies is None:  # [] is a valid policy list
        policies = [
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

    return Pipeline(transport=transport, policies=policies)
