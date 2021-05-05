# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import TYPE_CHECKING

from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpRequest

from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal.managed_identity_client import ManagedIdentityClient
from .._internal.get_token_mixin import GetTokenMixin

if TYPE_CHECKING:
    from typing import Any, Optional


class AppServiceCredential(GetTokenMixin):
    def __init__(self, **kwargs):
        # type: (**Any) -> None
        super(AppServiceCredential, self).__init__()

        client_args = _get_client_args(**kwargs)
        if client_args:
            self._client = ManagedIdentityClient(**client_args)
        else:
            self._client = None

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        if not self._client:
            raise CredentialUnavailableError(
                message="App Service managed identity configuration not found in environment"
            )
        return super(AppServiceCredential, self).get_token(*scopes, **kwargs)

    def _acquire_token_silently(self, *scopes):
        # type: (*str) -> Optional[AccessToken]
        return self._client.get_cached_token(*scopes)

    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        return self._client.request_token(*scopes, **kwargs)


def _get_client_args(**kwargs):
    # type: (dict) -> Optional[dict]
    identity_config = kwargs.pop("_identity_config", None) or {}

    url = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
    secret = os.environ.get(EnvironmentVariables.MSI_SECRET)
    if not (url and secret):
        # App Service managed identity isn't available in this environment
        return None

    if kwargs.get("client_id"):
        identity_config["clientid"] = kwargs.pop("client_id")

    return dict(
        kwargs,
        _content_callback=_parse_app_service_expires_on,
        _identity_config=identity_config,
        base_headers={"secret": secret},
        request_factory=functools.partial(_get_request, url),
    )


def _get_request(url, scope, identity_config):
    # type: (str, str, dict) -> HttpRequest
    request = HttpRequest("GET", url)
    request.format_parameters(dict({"api-version": "2017-09-01", "resource": scope}, **identity_config))
    return request


def _parse_app_service_expires_on(content):
    # type: (dict) -> None
    """Parse an App Service MSI version 2017-09-01 expires_on value to epoch seconds.

    This version of the API returns expires_on as a UTC datetime string rather than epoch seconds. The string's
    format depends on the OS. Responses on Windows include AM/PM, for example "1/16/2020 5:24:12 AM +00:00".
    Responses on Linux do not, for example "06/20/2019 02:57:58 +00:00".

    :raises ValueError: ``expires_on`` didn't match an expected format
    """
    import calendar
    import time

    # parse the string minus the timezone offset
    expires_on = content["expires_on"]
    if expires_on.endswith(" +00:00"):
        date_string = expires_on[: -len(" +00:00")]
        for format_string in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p"):  # (Linux, Windows)
            try:
                t = time.strptime(date_string, format_string)
                content["expires_on"] = calendar.timegm(t)
                return
            except ValueError:
                pass

    raise ValueError("'{}' doesn't match the expected format".format(expires_on))
