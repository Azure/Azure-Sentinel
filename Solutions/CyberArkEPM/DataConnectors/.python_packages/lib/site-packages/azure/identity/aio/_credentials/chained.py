# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from typing import Any, Optional, cast

from azure.core.exceptions import ClientAuthenticationError
from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.credentials_async import AsyncSupportsTokenInfo, AsyncTokenCredential, AsyncTokenProvider
from .._internal import AsyncContextManager
from ... import CredentialUnavailableError
from ..._credentials.chained import _get_error_message
from ..._internal import within_credential_chain

_LOGGER = logging.getLogger(__name__)


class ChainedTokenCredential(AsyncContextManager):
    """A sequence of credentials that is itself a credential.

    Its :func:`get_token` method calls ``get_token`` on each credential in the sequence, in order, returning the first
    valid token received. For more information, see
    https://aka.ms/azsdk/python/identity/credential-chains#chainedtokencredential-overview.

    :param credentials: credential instances to form the chain
    :type credentials: ~azure.core.credentials_async.AsyncTokenProvider

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_chained_token_credential_async]
            :end-before: [END create_chained_token_credential_async]
            :language: python
            :dedent: 4
            :caption: Create a ChainedTokenCredential.
    """

    def __init__(self, *credentials: AsyncTokenProvider) -> None:
        if not credentials:
            raise ValueError("at least one credential is required")

        self._successful_credential: Optional[AsyncTokenProvider] = None
        self.credentials = credentials

    async def close(self) -> None:
        """Close the transport sessions of all credentials in the chain."""

        await asyncio.gather(*(credential.close() for credential in self.credentials))

    async def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Asynchronously request a token from each credential, in order, returning the first token received.

        If no credential provides a token, raises :class:`azure.core.exceptions.ClientAuthenticationError`
        with an error message from each credential.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.
        :keyword bool enable_cae: indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Defaults to False.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises ~azure.core.exceptions.ClientAuthenticationError: no credential in the chain provided a token
        """
        within_credential_chain.set(True)
        history = []
        for credential in self.credentials:
            try:
                # Prioritize "get_token". Fall back to "get_token_info" if not available.
                if hasattr(credential, "get_token"):
                    token = await cast(AsyncTokenCredential, credential).get_token(
                        *scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
                    )
                else:
                    options: TokenRequestOptions = {}
                    if claims:
                        options["claims"] = claims
                    if tenant_id:
                        options["tenant_id"] = tenant_id
                    options["enable_cae"] = enable_cae
                    token_info = await cast(AsyncSupportsTokenInfo, credential).get_token_info(*scopes, **kwargs)
                    token = AccessToken(token_info.token, token_info.expires_on)

                _LOGGER.info("%s acquired a token from %s", self.__class__.__name__, credential.__class__.__name__)
                self._successful_credential = credential
                within_credential_chain.set(False)
                return token
            except CredentialUnavailableError as ex:
                # credential didn't attempt authentication because it lacks required data or state -> continue
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                # credential failed to authenticate, or something unexpectedly raised -> break
                history.append((credential, str(ex)))
                _LOGGER.debug(
                    '%s.get_token failed: %s raised unexpected error "%s"',
                    self.__class__.__name__,
                    credential.__class__.__name__,
                    ex,
                    exc_info=True,
                )
                break
        within_credential_chain.set(False)
        attempts = _get_error_message(history)
        message = (
            self.__class__.__name__
            + " failed to retrieve a token from the included credentials."
            + attempts
            + "\nTo mitigate this issue, please refer to the troubleshooting guidelines here at "
            "https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
        )
        raise ClientAuthenticationError(message=message)

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request a token from each chained credential, in order, returning the first token received.

        If no credential provides a token, raises :class:`azure.core.exceptions.ClientAuthenticationError`
        with an error message from each credential.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.

        :raises ~azure.core.exceptions.ClientAuthenticationError: no credential in the chain provided a token.
        """
        within_credential_chain.set(True)
        history = []
        options = options or {}
        for credential in self.credentials:
            try:
                # Prioritize "get_token_info". Fall back to "get_token" if not available.
                if hasattr(credential, "get_token_info"):
                    token_info = await cast(AsyncSupportsTokenInfo, credential).get_token_info(*scopes, options=options)
                else:
                    if options.get("pop"):
                        raise CredentialUnavailableError(
                            "Proof of possession arguments are not supported for this credential."
                        )
                    token = await cast(AsyncTokenCredential, credential).get_token(*scopes, **options)
                    token_info = AccessTokenInfo(token=token.token, expires_on=token.expires_on)

                _LOGGER.info("%s acquired a token from %s", self.__class__.__name__, credential.__class__.__name__)
                self._successful_credential = credential
                within_credential_chain.set(False)
                return token_info
            except CredentialUnavailableError as ex:
                # credential didn't attempt authentication because it lacks required data or state -> continue
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                # credential failed to authenticate, or something unexpectedly raised -> break
                history.append((credential, str(ex)))
                _LOGGER.debug(
                    '%s.get_token_info failed: %s raised unexpected error "%s"',
                    self.__class__.__name__,
                    credential.__class__.__name__,
                    ex,
                    exc_info=True,
                )
                break

        within_credential_chain.set(False)
        attempts = _get_error_message(history)
        message = (
            self.__class__.__name__
            + " failed to retrieve a token from the included credentials."
            + attempts
            + "\nTo mitigate this issue, please refer to the troubleshooting guidelines here at "
            "https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
        )
        _LOGGER.warning(message)
        raise ClientAuthenticationError(message=message)
