# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import os
import shutil
import sys
from typing import Any, List, Optional

from azure.core.exceptions import ClientAuthenticationError
from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from .._internal import AsyncContextManager
from .._internal.decorators import log_get_token_async
from ... import CredentialUnavailableError
from ..._credentials.azd_cli import (
    AzureDeveloperCliCredential as _SyncAzureDeveloperCliCredential,
    CLI_NOT_FOUND,
    COMMAND_LINE,
    EXECUTABLE_NAME,
    get_safe_working_dir,
    NOT_LOGGED_IN,
    UNKNOWN_CLAIMS_FLAG,
    parse_token,
    sanitize_output,
    extract_cli_error_message,
)
from ..._internal import encode_base64, resolve_tenant, within_dac, validate_tenant_id, validate_scope


_LOGGER = logging.getLogger(__name__)


class AzureDeveloperCliCredential(AsyncContextManager):
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
            :start-after: [START azure_developer_cli_credential_async]
            :end-before: [END azure_developer_cli_credential_async]
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

    @log_get_token_async
    async def get_token(
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
        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke the Azure Developer CLI.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked the Azure Developer CLI
          but didn't receive an access token.
        """
        # only ProactorEventLoop supports subprocesses on Windows (and it isn't the default loop on Python < 3.8)
        if sys.platform.startswith("win") and not isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
            return _SyncAzureDeveloperCliCredential().get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

        options: TokenRequestOptions = {}
        if tenant_id:
            options["tenant_id"] = tenant_id
        if claims:
            options["claims"] = claims

        token_info = await self._get_token_base(*scopes, options=options, **kwargs)
        return AccessToken(token_info.token, token_info.expires_on)

    @log_get_token_async
    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
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
        # only ProactorEventLoop supports subprocesses on Windows (and it isn't the default loop on Python < 3.8)
        if sys.platform.startswith("win") and not isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
            return _SyncAzureDeveloperCliCredential().get_token_info(*scopes, options=options)
        return await self._get_token_base(*scopes, options=options)

    async def _get_token_base(
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
        output = await _run_command(command_args, self._process_timeout)

        token = parse_token(output)
        if not token:
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

    async def close(self) -> None:
        """Calling this method is unnecessary"""


async def _run_command(command_args: List[str], timeout: int) -> str:
    # Ensure executable exists in PATH first. This avoids a subprocess call that would fail anyway.
    azd_path = shutil.which(EXECUTABLE_NAME)
    if not azd_path:
        raise CredentialUnavailableError(message=CLI_NOT_FOUND)

    args = [azd_path] + command_args
    working_directory = get_safe_working_dir()

    try:
        _LOGGER.debug("Executing subprocess with the following arguments %s", args)
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.DEVNULL,
            cwd=working_directory,
            env=dict(os.environ, NO_COLOR="true"),
        )
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout)
        output = stdout_b.decode()
        stderr = stderr_b.decode()
    except asyncio.TimeoutError as ex:
        proc.kill()
        raise CredentialUnavailableError(message="Timed out waiting for Azure Developer CLI") from ex
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
        raise error from ex

    if proc.returncode == 0:
        return output

    # Fallback check in case the executable is not found while executing subprocess.
    if proc.returncode == 127 or stderr.startswith("'azd' is not recognized"):
        raise CredentialUnavailableError(CLI_NOT_FOUND)

    combined_text = f"{output}\n{stderr}"
    if "not logged in, run `azd auth login` to login" in combined_text and "AADSTS" not in combined_text:
        raise CredentialUnavailableError(message=NOT_LOGGED_IN)
    if "unknown flag: --claims" in combined_text:
        raise CredentialUnavailableError(message=UNKNOWN_CLAIMS_FLAG)

    message = (
        extract_cli_error_message(output)
        or extract_cli_error_message(stderr)
        or (sanitize_output(stderr) if stderr else "Failed to invoke Azure Developer CLI")
    )
    if within_dac.get():
        raise CredentialUnavailableError(message=message)
    raise ClientAuthenticationError(message=message)
