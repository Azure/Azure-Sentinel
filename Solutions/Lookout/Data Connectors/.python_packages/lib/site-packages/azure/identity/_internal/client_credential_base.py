# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

import msal

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from .get_token_mixin import GetTokenMixin
from .persistent_cache import load_service_principal_cache

from . import wrap_exceptions
from .msal_credentials import MsalCredential

if TYPE_CHECKING:
    from typing import Any, Optional


class ClientCredentialBase(MsalCredential, GetTokenMixin):
    """Base class for credentials authenticating a service principal with a certificate or secret"""

    def __init__(self, **kwargs):
        if kwargs.pop("_enable_persistent_cache", False):
            allow_unencrypted = kwargs.pop("_allow_unencrypted_cache", False)
            cache = load_service_principal_cache(allow_unencrypted)
        else:
            cache = msal.TokenCache()
        super(ClientCredentialBase, self).__init__(_cache=cache, **kwargs)

    @wrap_exceptions
    def _acquire_token_silently(self, *scopes, **kwargs):
        # type: (*str, **Any) -> Optional[AccessToken]
        app = self._get_app()
        request_time = int(time.time())
        result = app.acquire_token_silent_with_error(list(scopes), account=None, **kwargs)
        if result and "access_token" in result and "expires_in" in result:
            return AccessToken(result["access_token"], request_time + int(result["expires_in"]))
        return None

    @wrap_exceptions
    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> Optional[AccessToken]
        app = self._get_app()
        request_time = int(time.time())
        result = app.acquire_token_for_client(list(scopes))
        if "access_token" not in result:
            message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            raise ClientAuthenticationError(message=message)

        return AccessToken(result["access_token"], request_time + int(result["expires_in"]))

    def _get_app(self):
        # type: () -> msal.ConfidentialClientApplication
        if not self._msal_app:
            self._msal_app = self._create_app(msal.ConfidentialClientApplication)
        return self._msal_app
