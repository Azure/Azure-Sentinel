# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import Optional, Dict, Any
from azure.core.rest import HttpRequest

from .._constants import EnvironmentVariables
from .._internal.msal_managed_identity_client import MsalManagedIdentityClient


class AppServiceCredential(MsalManagedIdentityClient):
    def get_unavailable_message(self, desc: str = "") -> str:
        return f"App Service managed identity configuration not found in environment. {desc}"


def _get_client_args(**kwargs: Any) -> Optional[Dict]:
    identity_config = kwargs.pop("identity_config", None) or {}

    url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
    secret = os.environ.get(EnvironmentVariables.IDENTITY_HEADER)
    if not (url and secret):
        # App Service managed identity isn't available in this environment
        return None

    return dict(
        kwargs,
        identity_config=identity_config,
        base_headers={"X-IDENTITY-HEADER": secret},
        request_factory=functools.partial(_get_request, url),
    )


def _get_request(url: str, scope: str, identity_config: Dict) -> HttpRequest:
    return HttpRequest("GET", url, params=dict({"api-version": "2019-08-01", "resource": scope}, **identity_config))
