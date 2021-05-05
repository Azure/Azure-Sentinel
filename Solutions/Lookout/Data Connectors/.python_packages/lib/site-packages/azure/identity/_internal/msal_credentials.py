# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc

import msal

from .msal_client import MsalClient
from .persistent_cache import load_user_cache
from .._internal import get_default_authority, normalize_authority, validate_tenant_id

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports,unused-import
    from typing import Any, Mapping, Optional, Type, Union


class MsalCredential(ABC):
    """Base class for credentials wrapping MSAL applications"""

    def __init__(self, client_id, client_credential=None, **kwargs):
        # type: (str, Optional[Union[str, Mapping[str, str]]], **Any) -> None
        authority = kwargs.pop("authority", None)
        self._authority = normalize_authority(authority) if authority else get_default_authority()
        self._tenant_id = kwargs.pop("tenant_id", None) or "organizations"
        validate_tenant_id(self._tenant_id)

        self._client_credential = client_credential
        self._client_id = client_id

        self._cache = kwargs.pop("_cache", None)  # internal, for use in tests
        if not self._cache:
            if kwargs.pop("_enable_persistent_cache", False):
                allow_unencrypted = kwargs.pop("_allow_unencrypted_cache", False)
                self._cache = load_user_cache(allow_unencrypted)
            else:
                self._cache = msal.TokenCache()

        self._client = MsalClient(**kwargs)

        # postpone creating the wrapped application because its initializer uses the network
        self._msal_app = None  # type: Optional[msal.ClientApplication]
        super(MsalCredential, self).__init__()

    @abc.abstractmethod
    def _get_app(self):
        # type: () -> msal.ClientApplication
        pass

    def _create_app(self, cls):
        # type: (Type[msal.ClientApplication]) -> msal.ClientApplication
        app = cls(
            client_id=self._client_id,
            client_credential=self._client_credential,
            authority="{}/{}".format(self._authority, self._tenant_id),
            token_cache=self._cache,
            http_client=self._client,
        )

        return app
