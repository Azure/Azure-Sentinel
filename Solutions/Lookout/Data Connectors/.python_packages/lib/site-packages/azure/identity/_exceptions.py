# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional


class CredentialUnavailableError(ClientAuthenticationError):
    """The credential did not attempt to authenticate because required data or state is unavailable."""


class AuthenticationRequiredError(CredentialUnavailableError):
    """Interactive authentication is required to acquire a token."""

    def __init__(self, scopes, message=None, error_details=None, **kwargs):
        # type: (Iterable[str], Optional[str], Optional[str], **Any) -> None
        self._scopes = scopes
        self._error_details = error_details
        if not message:
            message = "Interactive authentication is required to get a token. Call 'authenticate' to begin."
        super(AuthenticationRequiredError, self).__init__(message=message, **kwargs)

    @property
    def scopes(self):
        # type: () -> Iterable[str]
        """Scopes requested during the failed authentication"""
        return self._scopes

    @property
    def error_details(self):
        # type: () -> Optional[str]
        """Additional authentication error details from Azure Active Directory"""
        return self._error_details
