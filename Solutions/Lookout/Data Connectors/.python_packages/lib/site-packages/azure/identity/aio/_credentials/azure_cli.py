# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import sys
import os

from azure.core.exceptions import ClientAuthenticationError
from .._internal import AsyncContextManager
from .._internal.decorators import log_get_token_async
from ... import CredentialUnavailableError
from ..._credentials.azure_cli import (
    AzureCliCredential as _SyncAzureCliCredential,
    CLI_NOT_FOUND,
    COMMAND_LINE,
    get_safe_working_dir,
    NOT_LOGGED_IN,
    parse_token,
    sanitize_output,
)
from ..._internal import _scopes_to_resource


class AzureCliCredential(AsyncContextManager):
    """Authenticates by requesting a token from the Azure CLI.

    This requires previously logging in to Azure via "az login", and will use the CLI's currently logged in identity.
    """

    @log_get_token_async
    async def get_token(self, *scopes, **kwargs):
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients. Applications calling this method directly must
        also handle token caching because this credential doesn't cache the tokens it acquires.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke the Azure CLI.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked the Azure CLI but didn't
          receive an access token.
        """
        # only ProactorEventLoop supports subprocesses on Windows (and it isn't the default loop on Python < 3.8)
        if sys.platform.startswith("win") and not isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
            return _SyncAzureCliCredential().get_token(*scopes, **kwargs)

        resource = _scopes_to_resource(*scopes)
        output = await _run_command(COMMAND_LINE.format(resource))

        token = parse_token(output)
        if not token:
            sanitized_output = sanitize_output(output)
            raise ClientAuthenticationError(message="Unexpected output from Azure CLI: '{}'".format(sanitized_output))

        return token

    async def close(self):
        """Calling this method is unnecessary"""


async def _run_command(command):
    if sys.platform.startswith("win"):
        args = ("cmd", "/c " + command)
    else:
        args = ("/bin/sh", "-c", command)

    working_directory = get_safe_working_dir()

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=working_directory,
            env=dict(os.environ, AZURE_CORE_NO_COLOR="true")
        )
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'; CLI may or may not be installed
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
        raise error from ex

    stdout, _ = await asyncio.wait_for(proc.communicate(), 10)
    output = stdout.decode()

    if proc.returncode == 0:
        return output

    if proc.returncode == 127 or output.startswith("'az' is not recognized"):
        raise CredentialUnavailableError(CLI_NOT_FOUND)

    if "az login" in output or "az account set" in output:
        raise CredentialUnavailableError(message=NOT_LOGGED_IN)

    message = sanitize_output(output) if output else "Failed to invoke Azure CLI"
    raise ClientAuthenticationError(message=message)
