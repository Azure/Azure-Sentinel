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
from ..._credentials.azure_cli import (
    AzureCliCredential as _SyncAzureCliCredential,
    CLI_NOT_FOUND,
    COMMAND_LINE,
    EXECUTABLE_NAME,
    get_safe_working_dir,
    NOT_LOGGED_IN,
    parse_token,
    sanitize_output,
    CLAIMS_UNSUPPORTED_ERROR,
)
from ..._internal import (
    _scopes_to_resource,
    encode_base64,
    resolve_tenant,
    within_dac,
    validate_tenant_id,
    validate_scope,
    validate_subscription,
)


_LOGGER = logging.getLogger(__name__)


class AzureCliCredential(AsyncContextManager):
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
            :start-after: [START create_azure_cli_credential_async]
            :end-before: [END create_azure_cli_credential_async]
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
        # only ProactorEventLoop supports subprocesses on Windows (and it isn't the default loop on Python < 3.8)
        if sys.platform.startswith("win") and not isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
            return _SyncAzureCliCredential().get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

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
        # only ProactorEventLoop supports subprocesses on Windows (and it isn't the default loop on Python < 3.8)
        if sys.platform.startswith("win") and not isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
            return _SyncAzureCliCredential().get_token_info(*scopes, options=options)
        return await self._get_token_base(*scopes, options=options)

    async def _get_token_base(
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
        output = await _run_command(command_args, self._process_timeout)

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

    async def close(self) -> None:
        """Calling this method is unnecessary"""


async def _run_command(command_args: List[str], timeout: int) -> str:
    # Ensure executable exists in PATH first. This avoids a subprocess call that would fail anyway.
    if sys.platform.startswith("win"):
        # On Windows, the expected executable is az.cmd, so we check for that first, falling back to 'az' in case.
        az_path = shutil.which(EXECUTABLE_NAME + ".cmd") or shutil.which(EXECUTABLE_NAME)
    else:
        az_path = shutil.which(EXECUTABLE_NAME)
    if not az_path:
        raise CredentialUnavailableError(message=CLI_NOT_FOUND)

    args = [az_path] + command_args
    working_directory = get_safe_working_dir()
    try:
        _LOGGER.debug("Executing subprocess with the following arguments %s", args)
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.DEVNULL,
            cwd=working_directory,
            env=dict(os.environ, AZURE_CORE_NO_COLOR="true"),
        )
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout)
        output = stdout_b.decode()
        stderr = stderr_b.decode()
    except asyncio.TimeoutError as ex:
        proc.kill()
        raise CredentialUnavailableError(message="Timed out waiting for Azure CLI") from ex
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
        raise error from ex

    if proc.returncode == 0:
        return output

    # Fallback check in case the executable is not found while executing subprocess.
    if proc.returncode == 127 or stderr.startswith("'az' is not recognized"):
        raise CredentialUnavailableError(CLI_NOT_FOUND)

    if ("az login" in stderr or "az account set" in stderr) and "AADSTS" not in stderr:
        raise CredentialUnavailableError(message=NOT_LOGGED_IN)

    message = sanitize_output(stderr) if stderr else "Failed to invoke Azure CLI"
    if within_dac.get():
        raise CredentialUnavailableError(message=message)
    raise ClientAuthenticationError(message=message)
