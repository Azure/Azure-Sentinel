# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import json
import os
import re
import logging
import shutil
import subprocess
import sys
from typing import List, Optional, Any, Dict

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.exceptions import ClientAuthenticationError

from .. import CredentialUnavailableError
from .._internal import (
    _scopes_to_resource,
    encode_base64,
    resolve_tenant,
    within_dac,
    validate_tenant_id,
    validate_scope,
    validate_subscription,
)
from .._internal.decorators import log_get_token


_LOGGER = logging.getLogger(__name__)

CLI_NOT_FOUND = "Azure CLI not found on path"
# COMMAND_LINE = "account get-access-token --output json --resource {}"
COMMAND_LINE = ["account", "get-access-token", "--output", "json"]
EXECUTABLE_NAME = "az"
NOT_LOGGED_IN = "Please run 'az login' to set up an account"
CLAIMS_UNSUPPORTED_ERROR = (
    "This credential doesn't support claims challenges. To authenticate with the required "
    "claims, please run the following command (requires Azure CLI version 2.76.0 or later): "
    "az login --claims-challenge {claims_value}"
)


class AzureCliCredential:
    """Authenticates by requesting a token from the Azure CLI.

    This requires previously logging in to Azure via "az login", and will use the CLI's currently logged in identity.

    :keyword str tenant_id: Optional tenant to include in the token request.
    :keyword str subscription: The name or ID of a subscription. Set this to acquire tokens for an account other
        than the Azure CLI's current account.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    :keyword int process_timeout: Seconds to wait for the Azure CLI process to respond. Defaults to 10 seconds.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_azure_cli_credential]
            :end-before: [END create_azure_cli_credential]
            :language: python
            :dedent: 4
            :caption: Create an AzureCliCredential.
    """

    def __init__(
        self,
        *,
        tenant_id: str = "",
        subscription: Optional[str] = None,
        additionally_allowed_tenants: Optional[List[str]] = None,
        process_timeout: int = 10,
    ) -> None:
        if tenant_id:
            validate_tenant_id(tenant_id)
        if subscription:
            validate_subscription(subscription)

        self.tenant_id = tenant_id
        self.subscription = subscription
        self._additionally_allowed_tenants = additionally_allowed_tenants or []
        self._process_timeout = process_timeout

    def __enter__(self) -> "AzureCliCredential":
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def close(self) -> None:
        """Calling this method is unnecessary."""

    @log_get_token
    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients. Applications calling this method directly must
        also handle token caching because this credential doesn't cache the tokens it acquires.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token. This credential does not support claims
            challenges.
        :keyword str tenant_id: optional tenant to include in the token request.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken

        :raises ~azure.identity.CredentialUnavailableError: the credential was either unable to invoke the Azure CLI
          or a claims challenge was provided.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked the Azure CLI but didn't
          receive an access token.
        """
        options: TokenRequestOptions = {}
        if tenant_id:
            options["tenant_id"] = tenant_id
        if claims:
            options["claims"] = claims

        token_info = self._get_token_base(*scopes, options=options, **kwargs)
        return AccessToken(token_info.token, token_info.expires_on)

    @log_get_token
    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients. Applications calling this method
        directly must also handle token caching because this credential doesn't cache the tokens it acquires.

        :param str scopes: desired scopes for the access token. This credential allows only one scope per request.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.

        :raises ~azure.identity.CredentialUnavailableError: the credential was either unable to invoke the Azure CLI
          or a claims challenge was provided.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked the Azure CLI but didn't
          receive an access token.
        """
        return self._get_token_base(*scopes, options=options)

    def _get_token_base(
        self, *scopes: str, options: Optional[TokenRequestOptions] = None, **kwargs: Any
    ) -> AccessTokenInfo:
        # Check for claims challenge first
        if options and "claims" in options and options["claims"]:
            error_message = CLAIMS_UNSUPPORTED_ERROR.format(claims_value=encode_base64(options["claims"]))

            # Add tenant if provided in options
            if options.get("tenant_id"):
                error_message += f" --tenant {options.get('tenant_id')}"

            # Add scope if provided
            if scopes:
                error_message += f" --scope {scopes[0]}"

            raise CredentialUnavailableError(message=error_message)

        tenant_id = options.get("tenant_id") if options else None
        if tenant_id:
            validate_tenant_id(tenant_id)
        for scope in scopes:
            validate_scope(scope)

        resource = _scopes_to_resource(*scopes)
        command_args = COMMAND_LINE + ["--resource", resource]
        tenant = resolve_tenant(
            default_tenant=self.tenant_id,
            tenant_id=tenant_id,
            additionally_allowed_tenants=self._additionally_allowed_tenants,
            **kwargs,
        )
        if tenant:
            command_args += ["--tenant", tenant]

        if self.subscription:
            command_args += ["--subscription", self.subscription]
        output = _run_command(command_args, self._process_timeout)

        token = parse_token(output)
        if not token:
            sanitized_output = sanitize_output(output)
            message = (
                f"Unexpected output from Azure CLI: '{sanitized_output}'. \n"
                f"To mitigate this issue, please refer to the troubleshooting guidelines here at "
                f"https://aka.ms/azsdk/python/identity/azclicredential/troubleshoot."
            )
            if within_dac.get():
                raise CredentialUnavailableError(message=message)
            raise ClientAuthenticationError(message=message)

        return token


def parse_token(output) -> Optional[AccessTokenInfo]:
    """Parse output of 'az account get-access-token' to an AccessToken.

    In particular, convert the "expiresOn" value to epoch seconds. This value is a naive local datetime as returned by
    datetime.fromtimestamp.

    :param str output: Output of 'az' command.
    :return: An AccessToken or None if the output isn't valid.
    :rtype: azure.core.credentials.AccessToken or None
    """
    try:
        token = json.loads(output)

        # Use "expires_on" if it's present, otherwise use "expiresOn".
        if "expires_on" in token:
            return AccessTokenInfo(token["accessToken"], int(token["expires_on"]))

        dt = datetime.strptime(token["expiresOn"], "%Y-%m-%d %H:%M:%S.%f")
        expires_on = dt.timestamp()
        return AccessTokenInfo(token["accessToken"], int(expires_on))
    except (KeyError, ValueError):
        return None


def get_safe_working_dir() -> str:
    """Invoke 'az' from a directory controlled by the OS, not the executing program's directory.

    :return: The path to the directory.
    :rtype: str
    """

    if sys.platform.startswith("win"):
        path = os.environ.get("SYSTEMROOT")
        if not path:
            raise CredentialUnavailableError(message="Environment variable 'SYSTEMROOT' has no value")
        return path

    return "/bin"


def sanitize_output(output: str) -> str:
    """Redact access tokens from CLI output to prevent error messages revealing them.

    :param str output: The output of the Azure CLI.
    :return: The output with access tokens redacted.
    :rtype: str
    """
    return re.sub(r"\"accessToken\": \"(.*?)(\"|$)", "****", output)


def _run_command(command_args: List[str], timeout: int) -> str:
    # Ensure executable exists in PATH first. This avoids a subprocess call that would fail anyway.
    if sys.platform.startswith("win"):
        # On Windows, the expected executable is az.cmd, so we check for that first, falling back to 'az' in case.
        az_path = shutil.which(EXECUTABLE_NAME + ".cmd") or shutil.which(EXECUTABLE_NAME)
    else:
        az_path = shutil.which(EXECUTABLE_NAME)
    if not az_path:
        raise CredentialUnavailableError(message=CLI_NOT_FOUND)

    args = [az_path] + command_args
    try:
        working_directory = get_safe_working_dir()

        kwargs: Dict[str, Any] = {
            "stderr": subprocess.PIPE,
            "stdin": subprocess.DEVNULL,
            "cwd": working_directory,
            "universal_newlines": True,
            "timeout": timeout,
            "env": dict(os.environ, AZURE_CORE_NO_COLOR="true"),
        }
        _LOGGER.debug("Executing subprocess with the following arguments %s", args)
        return subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError as ex:
        # non-zero return from shell
        # Fallback check in case the executable is not found while executing subprocess.
        if ex.returncode == 127 or (ex.stderr is not None and ex.stderr.startswith("'az' is not recognized")):
            raise CredentialUnavailableError(message=CLI_NOT_FOUND) from ex
        if ex.stderr is not None and (
            ("az login" in ex.stderr or "az account set" in ex.stderr) and "AADSTS" not in ex.stderr
        ):
            raise CredentialUnavailableError(message=NOT_LOGGED_IN) from ex

        # return code is from the CLI -> propagate its output
        if ex.stderr:
            message = sanitize_output(ex.stderr)
        else:
            message = "Failed to invoke Azure CLI"
        if within_dac.get():
            raise CredentialUnavailableError(message=message) from ex
        raise ClientAuthenticationError(message=message) from ex
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
        raise error from ex
    except Exception as ex:
        # could be a timeout, for example
        error = CredentialUnavailableError(message="Failed to invoke the Azure CLI")
        raise error from ex
