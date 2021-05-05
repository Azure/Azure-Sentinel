# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import time

from azure.core.exceptions import ClientAuthenticationError

from .._constants import DEVELOPER_SIGN_ON_CLIENT_ID
from .._internal import InteractiveCredential, wrap_exceptions

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Optional


class DeviceCodeCredential(InteractiveCredential):
    """Authenticates users through the device code flow.

    When :func:`get_token` is called, this credential acquires a verification URL and code from Azure Active Directory.
    A user must browse to the URL, enter the code, and authenticate with Azure Active Directory. If the user
    authenticates successfully, the credential receives an access token.

    For more information about the device code flow, see Azure Active Directory documentation:
    https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-device-code

    :param str client_id: client ID of the application users will authenticate to. When not specified users will
          authenticate to an Azure development application.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword str tenant_id: an Azure Active Directory tenant ID. Defaults to the 'organizations' tenant, which can
          authenticate work or school accounts. **Required for single-tenant applications.**
    :keyword int timeout: seconds to wait for the user to authenticate. Defaults to the validity period of the
          device code as set by Azure Active Directory, which also prevails when ``timeout`` is longer.
    :keyword prompt_callback: A callback enabling control of how authentication
          instructions are presented. Must accept arguments (``verification_uri``, ``user_code``, ``expires_on``):

            - ``verification_uri`` (str) the URL the user must visit
            - ``user_code`` (str) the code the user must enter there
            - ``expires_on`` (datetime.datetime) the UTC time at which the code will expire
          If this argument isn't provided, the credential will print instructions to stdout.
    :paramtype prompt_callback: Callable[str, str, ~datetime.datetime]
    """

    def __init__(self, client_id=DEVELOPER_SIGN_ON_CLIENT_ID, **kwargs):
        # type: (Optional[str], **Any) -> None
        self._timeout = kwargs.pop("timeout", None)  # type: Optional[int]
        self._prompt_callback = kwargs.pop("prompt_callback", None)
        super(DeviceCodeCredential, self).__init__(client_id=client_id, **kwargs)

    @wrap_exceptions
    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> dict

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore

        app = self._get_app()
        flow = app.initiate_device_flow(scopes)
        if "error" in flow:
            raise ClientAuthenticationError(
                message="Couldn't begin authentication: {}".format(flow.get("error_description") or flow.get("error"))
            )

        if self._prompt_callback:
            self._prompt_callback(
                flow["verification_uri"], flow["user_code"], datetime.utcfromtimestamp(flow["expires_at"])
            )
        else:
            print(flow["message"])

        if self._timeout is not None and self._timeout < flow["expires_in"]:
            # user specified an effective timeout we will observe
            deadline = int(time.time()) + self._timeout
            result = app.acquire_token_by_device_flow(flow, exit_condition=lambda flow: time.time() > deadline)
        else:
            # MSAL will stop polling when the device code expires
            result = app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:
            if result.get("error") == "authorization_pending":
                message = "Timed out waiting for user to authenticate"
            else:
                message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            raise ClientAuthenticationError(message=message)

        return result
