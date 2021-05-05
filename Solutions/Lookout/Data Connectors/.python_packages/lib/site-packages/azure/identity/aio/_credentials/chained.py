# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import logging
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError
from .._internal import AsyncContextManager
from ... import CredentialUnavailableError
from ..._credentials.chained import _get_error_message

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken
    from azure.core.credentials_async import AsyncTokenCredential

_LOGGER = logging.getLogger(__name__)


class ChainedTokenCredential(AsyncContextManager):
    """A sequence of credentials that is itself a credential.

    Its :func:`get_token` method calls ``get_token`` on each credential in the sequence, in order, returning the first
    valid token received.

    :param credentials: credential instances to form the chain
    :type credentials: :class:`azure.core.credentials.AsyncTokenCredential`
    """

    def __init__(self, *credentials: "AsyncTokenCredential") -> None:
        if not credentials:
            raise ValueError("at least one credential is required")

        self._successful_credential = None  # type: Optional[AsyncTokenCredential]
        self.credentials = credentials

    async def close(self):
        """Close the transport sessions of all credentials in the chain."""

        await asyncio.gather(*(credential.close() for credential in self.credentials))

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Asynchronously request a token from each credential, in order, returning the first token received.

        If no credential provides a token, raises :class:`azure.core.exceptions.ClientAuthenticationError`
        with an error message from each credential.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :raises ~azure.core.exceptions.ClientAuthenticationError: no credential in the chain provided a token
        """
        history = []
        for credential in self.credentials:
            try:
                token = await credential.get_token(*scopes, **kwargs)
                _LOGGER.info("%s acquired a token from %s", self.__class__.__name__, credential.__class__.__name__)
                self._successful_credential = credential
                return token
            except CredentialUnavailableError as ex:
                # credential didn't attempt authentication because it lacks required data or state -> continue
                history.append((credential, ex.message))
                _LOGGER.info("%s - %s is unavailable", self.__class__.__name__, credential.__class__.__name__)
            except Exception as ex:  # pylint: disable=broad-except
                # credential failed to authenticate, or something unexpectedly raised -> break
                history.append((credential, str(ex)))
                _LOGGER.warning(
                    '%s.get_token failed: %s raised unexpected error "%s"',
                    self.__class__.__name__,
                    credential.__class__.__name__,
                    ex,
                    exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
                )
                break

        attempts = _get_error_message(history)
        message = self.__class__.__name__ + " failed to retrieve a token from the included credentials." + attempts
        raise ClientAuthenticationError(message=message)
