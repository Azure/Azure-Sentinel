# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
from typing import Any, Optional

import msal
from azure.core.credentials import AccessToken, TokenRequestOptions, AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError

from .._auth_record import AuthenticationRecord
from .._exceptions import CredentialUnavailableError
from .._constants import AZURE_VSCODE_CLIENT_ID
from .._internal import within_dac

from .._internal.decorators import log_get_token
from .._internal.utils import get_broker_credential, validate_tenant_id

MAX_AUTH_RECORD_SIZE = 10 * 1024  # 10KB - more than enough for a small auth record
VSCODE_AUTH_RECORD_PATHS = [
    "~/.azure/ms-azuretools.vscode-azureresourcegroups/authRecord.json",
    "~/.Azure/ms-azuretools.vscode-azureresourcegroups/authRecord.json",
]


def load_vscode_auth_record() -> Optional[AuthenticationRecord]:
    """Load the authentication record corresponding to a known location.

    This will load from ~/.azure/ms-azuretools.vscode-azureresourcegroups/authRecord.json
    or ~/.Azure/ms-azuretools.vscode-azureresourcegroups/authRecord.json

    :return: The authentication record if it exists, otherwise None.
    :rtype: Optional[AuthenticationRecord]
    :raises: ValueError if the authentication record is not in the expected format
    """

    # Try each possible auth record path
    for auth_record_path in VSCODE_AUTH_RECORD_PATHS:
        expanded_path = os.path.expanduser(auth_record_path)
        if os.path.exists(expanded_path):
            file_size = os.path.getsize(expanded_path)
            if file_size > MAX_AUTH_RECORD_SIZE:
                error_message = (
                    "VS Code auth record file is unexpectedly large. "
                    "Please check the file for corruption or unexpected content."
                )
                raise ValueError(error_message)
            with open(expanded_path, "r", encoding="utf-8") as f:
                deserialized = json.load(f)

            # Validate the authentication record for security and structural integrity
            _validate_auth_record_json(deserialized)

            # Deserialize the authentication record
            auth_record = AuthenticationRecord(
                authority=deserialized["authority"],
                client_id=deserialized["clientId"],
                home_account_id=deserialized["homeAccountId"],
                tenant_id=deserialized["tenantId"],
                username=deserialized["username"],
            )

            return auth_record

    # No auth record found in any of the expected locations
    return None


def _validate_auth_record_json(data: dict) -> None:
    """Validate the authentication record.

    :param dict data: The authentication record data to validate.
    :raises ValueError: If the authentication record fails validation checks.
    """
    errors = []

    # Schema Validation - Required Fields
    try:
        tenant_id = data["tenantId"]
        if not tenant_id or not isinstance(tenant_id, str):
            errors.append("tenantId must be a non-empty string")
        else:
            try:
                validate_tenant_id(tenant_id)
            except ValueError as e:
                errors.append(f"tenantId validation failed: {e}")
    except KeyError:
        errors.append("tenantId field is missing")

    try:
        client_id = data["clientId"]
        if not client_id or not isinstance(client_id, str):
            errors.append("clientId must be a non-empty string")
        elif client_id != AZURE_VSCODE_CLIENT_ID:
            errors.append(
                f"clientId must match expected VS Code Azure Resources extension client ID: {AZURE_VSCODE_CLIENT_ID}"
            )
    except KeyError:
        errors.append("clientId field is missing")

    try:
        username = data["username"]
        if not username or not isinstance(username, str):
            errors.append("username must be a non-empty string")
    except KeyError:
        errors.append("username field is missing")

    try:
        home_account_id = data["homeAccountId"]
        if not home_account_id or not isinstance(home_account_id, str):
            errors.append("homeAccountId must be a non-empty string")
    except KeyError:
        errors.append("homeAccountId field is missing")

    try:
        authority = data["authority"]
        if not authority or not isinstance(authority, str):
            errors.append("authority must be a non-empty string")
    except KeyError:
        errors.append("authority field is missing")

    if errors:
        error_message = "Authentication record validation failed: " + "; ".join(errors)
        raise ValueError(error_message)


class VisualStudioCodeCredential:
    """Authenticates as the Azure user signed in to Visual Studio Code via the 'Azure Resources' extension.

    This currently only works in Windows/WSL environments and requires the 'azure-identity-broker'
    package to be installed.

    :keyword str tenant_id: A Microsoft Entra tenant ID. Defaults to the tenant specified in the authentication
        record file used by the Azure Resources extension.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(self, **kwargs: Any) -> None:

        self._broker_credential = None
        self._unavailable_message = (
            "VisualStudioCodeCredential requires the 'azure-identity-broker' package to be installed. "
            "You must also ensure you have the Azure Resources extension installed and have "
            "signed in to Azure via Visual Studio Code."
        )

        broker_credential_class = get_broker_credential()
        if broker_credential_class:
            try:
                # Load the authentication record from the VS Code extension
                authentication_record = load_vscode_auth_record()
                if not authentication_record:
                    self._unavailable_message = (
                        "VisualStudioCodeCredential requires the user to be signed in to Azure via Visual Studio Code. "
                        "Please ensure you have the Azure Resources extension installed and have signed in."
                    )
                    return
                self._broker_credential = broker_credential_class(
                    client_id=AZURE_VSCODE_CLIENT_ID,
                    authentication_record=authentication_record,
                    parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE,
                    use_default_broker_account=True,
                    disable_interactive_fallback=True,
                    **kwargs,
                )
            except ValueError as ex:
                self._unavailable_message = (
                    "Failed to load authentication record from Visual Studio Code: "
                    f"{ex}. Please ensure you have the Azure Resources extension installed and signed in."
                )

    def __enter__(self) -> "VisualStudioCodeCredential":
        if self._broker_credential:
            self._broker_credential.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._broker_credential:
            self._broker_credential.__exit__(*args)

    def close(self) -> None:
        """Close the credential's transport session."""
        if self._broker_credential:
            self._broker_credential.close()

    @log_get_token
    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        """Request an access token for `scopes` as the user currently signed in to Visual Studio Code.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises ~azure.identity.CredentialUnavailableError: the credential cannot retrieve user details from Visual
          Studio Code
        """
        if not self._broker_credential:
            raise CredentialUnavailableError(message=self._unavailable_message)
        if within_dac.get():
            try:
                token = self._broker_credential.get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)
                return token
            except ClientAuthenticationError as ex:
                raise CredentialUnavailableError(message=ex.message) from ex
        return self._broker_credential.get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes` as the user currently signed in to Visual Studio Code.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.
        :raises ~azure.identity.CredentialUnavailableError: the credential cannot retrieve user details from Visual
          Studio Code.
        """
        if not self._broker_credential:
            raise CredentialUnavailableError(message=self._unavailable_message)
        if within_dac.get():
            try:
                token = self._broker_credential.get_token_info(*scopes, options=options)
                return token
            except ClientAuthenticationError as ex:
                raise CredentialUnavailableError(message=ex.message) from ex
        return self._broker_credential.get_token_info(*scopes, options=options)
