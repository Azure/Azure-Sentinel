# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional, Dict, cast, Union, Mapping
import abc
import time
import logging

import msal
from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.exceptions import ClientAuthenticationError

from .msal_client import MsalClient
from .utils import within_credential_chain
from .._internal import _scopes_to_resource
from .._exceptions import CredentialUnavailableError

_LOGGER = logging.getLogger(__name__)


class MsalManagedIdentityClient(abc.ABC):  # pylint:disable=client-accepts-api-version-keyword
    """Base class for managed identity client wrapping MSAL ManagedIdentityClient."""

    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(
        self, *, client_id: Optional[str] = None, identity_config: Optional[Mapping[str, str]] = None, **kwargs: Any
    ) -> None:
        self._settings = {"client_id": client_id, "identity_config": identity_config or {}}
        self._client = MsalClient(**kwargs)
        managed_identity = self.get_managed_identity()
        self._msal_client = msal.ManagedIdentityClient(managed_identity, http_client=self._client)

    def __enter__(self) -> "MsalManagedIdentityClient":
        self._client.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.__exit__(*args)

    @abc.abstractmethod
    def get_unavailable_message(self, desc: str = "") -> str:
        pass

    def close(self) -> None:
        self.__exit__()

    def _request_token(self, *scopes: str, **kwargs: Any) -> AccessTokenInfo:
        if not scopes:
            raise ValueError('"get_token" requires at least one scope')
        resource = _scopes_to_resource(*scopes)
        result = self._msal_client.acquire_token_for_client(resource=resource, claims_challenge=kwargs.get("claims"))
        now = int(time.time())
        if result and "access_token" in result and "expires_in" in result:
            refresh_on = int(result["refresh_on"]) if "refresh_on" in result else None
            return AccessTokenInfo(
                result["access_token"],
                now + int(result["expires_in"]),
                token_type=result.get("token_type", "Bearer"),
                refresh_on=refresh_on,
            )
        error_desc = ""
        if result and "error" in result:
            error_desc = f"Token request error: ({result['error']}) {result.get('error_description', '')}"
        error_message = self.get_unavailable_message(error_desc)
        raise CredentialUnavailableError(error_message)

    def get_managed_identity(self) -> Union[msal.UserAssignedManagedIdentity, msal.SystemAssignedManagedIdentity]:
        """
        Get the managed identity configuration.

        :rtype: msal.UserAssignedManagedIdentity or msal.SystemAssignedManagedIdentity
        :return: The managed identity configuration.
        """

        if "client_id" in self._settings and self._settings["client_id"]:
            return msal.UserAssignedManagedIdentity(client_id=self._settings["client_id"])
        identity_config = cast(Dict, self._settings.get("identity_config")) or {}
        if "client_id" in identity_config and identity_config["client_id"]:
            return msal.UserAssignedManagedIdentity(client_id=identity_config["client_id"])
        if "resource_id" in identity_config and identity_config["resource_id"]:
            return msal.UserAssignedManagedIdentity(resource_id=identity_config["resource_id"])
        if "object_id" in identity_config and identity_config["object_id"]:
            return msal.UserAssignedManagedIdentity(object_id=identity_config["object_id"])
        return msal.SystemAssignedManagedIdentity()

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Request an access token for `scopes`.

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
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        options: TokenRequestOptions = {}
        if claims:
            options["claims"] = claims
        if tenant_id:
            options["tenant_id"] = tenant_id
        options["enable_cae"] = enable_cae

        token_info = self._get_token_base(*scopes, options=options, base_method_name="get_token", **kwargs)
        return AccessToken(token_info.token, token_info.expires_on)

    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        return self._get_token_base(*scopes, options=options, base_method_name="get_token_info")

    def _get_token_base(
        self,
        *scopes: str,
        options: Optional[TokenRequestOptions] = None,
        base_method_name: str = "get_token_info",
        **kwargs: Any,
    ) -> AccessTokenInfo:
        if not scopes:
            raise ValueError(f'"{base_method_name}" requires at least one scope')
        _scopes_to_resource(*scopes)
        token = None

        options = options or {}
        claims = options.get("claims")
        tenant_id = options.get("tenant_id")
        enable_cae = options.get("enable_cae", False)

        try:
            token = self._request_token(*scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs)
            if token:
                _LOGGER.log(
                    logging.DEBUG if within_credential_chain.get() else logging.INFO,
                    "%s.%s succeeded",
                    self.__class__.__name__,
                    base_method_name,
                )
                return token
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s.%s failed",
                self.__class__.__name__,
                base_method_name,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise CredentialUnavailableError(self.get_unavailable_message())
        except msal.ManagedIdentityError as ex:
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s.%s failed: %s",
                self.__class__.__name__,
                base_method_name,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise ClientAuthenticationError(self.get_unavailable_message(str(ex))) from ex
        except Exception as ex:
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s.%s failed: %s",
                self.__class__.__name__,
                base_method_name,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise

    def __getstate__(self) -> Dict[str, Any]:  # pylint:disable=client-method-name-no-double-underscore
        state = self.__dict__.copy()
        # Remove the non-picklable entries
        del state["_msal_client"]
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:  # pylint:disable=client-method-name-no-double-underscore
        self.__dict__.update(state)
        # Re-create the unpickable entries
        managed_identity = self.get_managed_identity()
        self._msal_client = msal.ManagedIdentityClient(managed_identity, http_client=self._client)
