# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.exceptions import ClientAuthenticationError

from .. import CredentialUnavailableError
from .._internal import encode_base64, resolve_tenant, within_dac, validate_tenant_id, validate_scope
from .._internal.decorators import log_get_token


_LOGGER = logging.getLogger(__name__)

CLI_NOT_FOUND = (
    "Azure Developer CLI could not be found. "
    "Please visit https://aka.ms/azure-dev for installation instructions and then,"
    "once installed, authenticate to your Azure account using 'azd auth login'."
)
UNKNOWN_CLAIMS_FLAG = (
    "Claims challenges are not supported by the Azure Developer CLI version you are using. "
    "Please update to version 1.18.1 or later."
)
COMMAND_LINE = ["auth", "token", "--output", "json", "--no-prompt"]
EXECUTABLE_NAME = "azd"
NOT_LOGGED_IN = "Please run 'azd auth login' from a command prompt to authenticate before using this credential."


class AzureDeveloperCliCredential:
    """Authenticates by requesting a token from the Azure Developer CLI.

    Azure Developer CLI is a command-line interface tool that allows developers to create, manage, and deploy
    resources in Azure. It's built on top of the Azure CLI and provides additional functionality specific
    to Azure developers. It allows users to authenticate as a user and/or a service principal against
    `Microsoft Entra ID <"https://learn.microsoft.com/entra/fundamentals/">`__.
    The AzureDeveloperCliCredential authenticates in a development environment and acquires a token on behalf of
    the logged-in user or service principal in Azure Developer CLI. It acts as the Azure Developer CLI logged-in user
    or service principal and executes an Azure CLI command underneath to authenticate the application against
    Microsoft Entra ID.

    To use this credential, the developer needs to authenticate locally in Azure Developer CLI using one of the
    commands below:

      * Run "azd auth login" in Azure Developer CLI to authenticate interactively as a user.
      * Run "azd auth login --client-id 'client_id' --client-secret 'client_secret' --tenant-id 'tenant_id'"
        to authenticate as a service principal.

    You may need to repeat this process after a certain time period, depending on the refresh token validity in your
    organization. Generally, the refresh token validity period is a few weeks to a few months.
    AzureDeveloperCliCredential will prompt you to sign in again.

    :keyword str tenant_id: Optional tenant to include in the token request.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    :keyword int process_timeout: Seconds to wait for the Azure Developer CLI process to respond. Defaults
        to 10 seconds.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START azure_developer_cli_credential]
            :end-before: [END azure_developer_cli_credential]
            :language: python
            :dedent: 4
            :caption: Create an AzureDeveloperCliCredential.
    """

    def __init__(
        self,
        *,
        tenant_id: str = "",
        additionally_allowed_tenants: Optional[List[str]] = None,
        process_timeout: int = 10,
    ) -> None:
        if tenant_id:
            validate_tenant_id(tenant_id)
        self.tenant_id = tenant_id
        self._additionally_allowed_tenants = additionally_allowed_tenants or []
        self._process_timeout = process_timeout

    def __enter__(self) -> "AzureDeveloperCliCredential":
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
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken

        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke
          the Azure Developer CLI.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked
          the Azure Developer CLI but didn't receive an access token.
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

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.

        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke
          the Azure Developer CLI.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked
          the Azure Developer CLI but didn't receive an access token.
        """
        return self._get_token_base(*scopes, options=options)

    def _get_token_base(
        self, *scopes: str, options: Optional[TokenRequestOptions] = None, **kwargs: Any
    ) -> AccessTokenInfo:
        if not scopes:
            raise ValueError("Missing scope in request. \n")

        tenant_id = options.get("tenant_id") if options else None
        claims = options.get("claims") if options else None
        if tenant_id:
            validate_tenant_id(tenant_id)
        for scope in scopes:
            validate_scope(scope)

        command_args = COMMAND_LINE.copy()
        for scope in scopes:
            command_args += ["--scope", scope]
        tenant = resolve_tenant(
            default_tenant=self.tenant_id,
            tenant_id=tenant_id,
            additionally_allowed_tenants=self._additionally_allowed_tenants,
            **kwargs,
        )
        if tenant:
            command_args += ["--tenant-id", tenant]
        if claims:
            command_args += ["--claims", encode_base64(claims)]
        output = _run_command(command_args, self._process_timeout)

        token = parse_token(output)
        if not token:
            # Try to extract a meaningful error from azd consoleMessage JSON lines
            extracted = extract_cli_error_message(output)
            if extracted:
                message = extracted
            else:
                sanitized_output = sanitize_output(output)
                message = (
                    f"Unexpected output from Azure Developer CLI: '{sanitized_output}'. \n"
                    f"To mitigate this issue, please refer to the troubleshooting guidelines here at "
                    f"https://aka.ms/azsdk/python/identity/azdevclicredential/troubleshoot."
                )
            if within_dac.get():
                raise CredentialUnavailableError(message=message)
            raise ClientAuthenticationError(message=message)

        return token


def parse_token(output: str) -> Optional[AccessTokenInfo]:
    """Parse to an AccessToken.

    In particular, convert the "expiresOn" value to epoch seconds. This value is a naive local datetime as returned by
    datetime.fromtimestamp.

    :param str output: The output of the Azure Developer CLI command.
    :return: An AccessToken or None if the output isn't valid.
    :rtype: azure.core.credentials.AccessToken or None
    """
    try:
        token = json.loads(output)
        dt = datetime.strptime(token["expiresOn"], "%Y-%m-%dT%H:%M:%SZ")
        expires_on = dt.timestamp()

        return AccessTokenInfo(token["token"], int(expires_on))
    except (KeyError, ValueError):
        return None


def get_safe_working_dir() -> str:
    """Invoke 'azd' from a directory controlled by the OS, not the executing program's directory.

    :return: The path to the directory.
    :rtype: str
    :raises ~azure.identity.CredentialUnavailableError: the SYSTEMROOT environment variable is not set.
    """

    if sys.platform.startswith("win"):
        path = os.environ.get("SYSTEMROOT")
        if not path:
            raise CredentialUnavailableError(
                message="Azure Developer CLI credential" + " expects a 'SystemRoot' environment variable"
            )
        return path

    return "/bin"


def sanitize_output(output: str) -> str:
    """Redact tokens from CLI output to prevent error messages revealing them.

    :param str output: The output of the Azure Developer CLI command.
    :return: The output with tokens redacted.
    :rtype: str
    """
    return re.sub(r"\"token\": \"(.*?)(\"|$)", "****", output)


def extract_cli_error_message(output: str) -> Optional[str]:
    """
    Extract a single, user-friendly message from azd consoleMessage JSON output.

    :param str output: The output from the Azure Developer CLI command.
    :return: A user-friendly error message if found, otherwise None.
    :rtype: Optional[str]

    Preference order:
    1) A message containing "Suggestion" (case-insensitive)
    2) The second message if multiple are present
    3) The first message if only one exists
    Returns None if no messages can be parsed.
    """
    messages: List[str] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:  # not JSON -> ignore
            continue
        if isinstance(obj, dict):
            data = obj.get("data")
            if isinstance(data, dict):
                msg = data.get("message")
                if isinstance(msg, str) and msg.strip():
                    messages.append(msg.strip())
                    continue
            msg = obj.get("message")
            if isinstance(msg, str) and msg.strip():
                messages.append(msg.strip())

    if not messages:
        return None

    # Prefer the suggestion line if present
    for msg in messages:
        if "suggestion" in msg.lower():
            return sanitize_output(msg)

    # If more than one message exists, return the last one
    if len(messages) > 1:
        return sanitize_output(messages[-1])
    return sanitize_output(messages[0])


def _run_command(command_args: List[str], timeout: int) -> str:
    # Ensure executable exists in PATH first. This avoids a subprocess call that would fail anyway.
    azd_path = shutil.which(EXECUTABLE_NAME)
    if not azd_path:
        raise CredentialUnavailableError(message=CLI_NOT_FOUND)

    args = [azd_path] + command_args
    try:
        working_directory = get_safe_working_dir()

        kwargs: Dict[str, Any] = {
            "stderr": subprocess.PIPE,
            "stdin": subprocess.DEVNULL,
            "cwd": working_directory,
            "universal_newlines": True,
            "env": dict(os.environ, NO_COLOR="true"),
            "timeout": timeout,
        }

        _LOGGER.debug("Executing subprocess with the following arguments %s", args)
        return subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError as ex:
        # non-zero return from shell
        # Fallback check in case the executable is not found while executing subprocess.
        if ex.returncode == 127 or (ex.stderr is not None and ex.stderr.startswith("'azd' is not recognized")):
            raise CredentialUnavailableError(message=CLI_NOT_FOUND) from ex
        combined_text = "{}\n{}".format(ex.output or "", ex.stderr or "")
        if "not logged in, run `azd auth login` to login" in combined_text and "AADSTS" not in combined_text:
            raise CredentialUnavailableError(message=NOT_LOGGED_IN) from ex
        if "unknown flag: --claims" in combined_text:
            raise CredentialUnavailableError(message=UNKNOWN_CLAIMS_FLAG) from ex

        # return code is from the CLI -> propagate its output
        message = (
            extract_cli_error_message(ex.output or "")
            or extract_cli_error_message(ex.stderr or "")
            or (sanitize_output(ex.stderr) if ex.stderr else "Failed to invoke Azure Developer CLI")
        )
        if within_dac.get():
            raise CredentialUnavailableError(message=message) from ex
        raise ClientAuthenticationError(message=message) from ex
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
        raise error from ex
    except Exception as ex:
        # could be a timeout, for example
        error = CredentialUnavailableError(message="Failed to invoke the Azure Developer CLI")
        raise error from ex
