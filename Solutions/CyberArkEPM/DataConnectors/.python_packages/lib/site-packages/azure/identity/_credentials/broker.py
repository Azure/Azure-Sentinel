# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from typing import Any

import msal
from azure.core.credentials import AccessToken, AccessTokenInfo, SupportsTokenInfo
from .._exceptions import CredentialUnavailableError
from .._internal.utils import get_broker_credential, is_wsl


class BrokerCredential(SupportsTokenInfo):
    """A broker credential that handles prerequisite checking and falls back appropriately.

    This credential checks if the azure-identity-broker package is available and the platform
    is supported. If both conditions are met, it uses the real broker credential. Otherwise,
    it raises CredentialUnavailableError with an appropriate message.
    """

    def __init__(self, **kwargs: Any) -> None:

        self._tenant_id = kwargs.pop("tenant_id", None)
        self._client_id = kwargs.pop("client_id", None)
        self._broker_credential = None
        self._unavailable_message = None

        # Check prerequisites and initialize the appropriate credential
        broker_credential_class = get_broker_credential()
        if broker_credential_class and (sys.platform.startswith("win") or is_wsl()):
            # The silent auth flow for brokered auth is available on Windows/WSL with the broker package
            try:
                broker_credential_args = {
                    "tenant_id": self._tenant_id,
                    "parent_window_handle": msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE,
                    "use_default_broker_account": True,
                    "disable_interactive_fallback": True,
                    **kwargs,
                }
                if self._client_id:
                    broker_credential_args["client_id"] = self._client_id
                self._broker_credential = broker_credential_class(**broker_credential_args)
            except Exception as ex:  # pylint: disable=broad-except
                self._unavailable_message = f"InteractiveBrowserBrokerCredential initialization failed: {ex}"
        else:
            # Determine the specific reason for unavailability
            if broker_credential_class is None:
                self._unavailable_message = (
                    "InteractiveBrowserBrokerCredential unavailable. "
                    "The 'azure-identity-broker' package is required to use brokered authentication."
                )
            else:
                self._unavailable_message = (
                    "InteractiveBrowserBrokerCredential unavailable. "
                    "Brokered authentication is only supported on Windows and WSL platforms."
                )

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        if self._broker_credential:
            return self._broker_credential.get_token(*scopes, **kwargs)
        raise CredentialUnavailableError(message=self._unavailable_message)

    def get_token_info(self, *scopes: str, **kwargs: Any) -> AccessTokenInfo:
        if self._broker_credential:
            return self._broker_credential.get_token_info(*scopes, **kwargs)
        raise CredentialUnavailableError(message=self._unavailable_message)

    def __enter__(self) -> "BrokerCredential":
        if self._broker_credential:
            self._broker_credential.__enter__()
        return self

    def __exit__(self, *args):
        if self._broker_credential:
            self._broker_credential.__exit__(*args)

    def close(self) -> None:
        self.__exit__()
