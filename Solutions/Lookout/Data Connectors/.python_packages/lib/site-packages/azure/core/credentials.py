# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import TYPE_CHECKING
import six


if TYPE_CHECKING:
    from typing import Any, NamedTuple
    from typing_extensions import Protocol

    AccessToken = NamedTuple("AccessToken", [("token", str), ("expires_on", int)])

    class TokenCredential(Protocol):
        """Protocol for classes able to provide OAuth tokens.

        :param str scopes: Lets you specify the type of access needed.
        """

        # pylint:disable=too-few-public-methods
        def get_token(self, *scopes, **kwargs):
            # type: (*str, **Any) -> AccessToken
            pass


else:
    from collections import namedtuple

    AccessToken = namedtuple("AccessToken", ["token", "expires_on"])

__all__ = ["AzureKeyCredential", "AzureSasCredential", "AccessToken"]


class AzureKeyCredential(object):
    """Credential type used for authenticating to an Azure service.
    It provides the ability to update the key without creating a new client.

    :param str key: The key used to authenticate to an Azure service
    :raises: TypeError
    """

    def __init__(self, key):
        # type: (str) -> None
        if not isinstance(key, six.string_types):
            raise TypeError("key must be a string.")
        self._key = key  # type: str

    @property
    def key(self):
        # type () -> str
        """The value of the configured key.

        :rtype: str
        """
        return self._key

    def update(self, key):
        # type: (str) -> None
        """Update the key.

        This can be used when you've regenerated your service key and want
        to update long-lived clients.

        :param str key: The key used to authenticate to an Azure service
        :raises: ValueError or TypeError
        """
        if not key:
            raise ValueError("The key used for updating can not be None or empty")
        if not isinstance(key, six.string_types):
            raise TypeError("The key used for updating must be a string.")
        self._key = key


class AzureSasCredential(object):
    """Credential type used for authenticating to an Azure service.
    It provides the ability to update the shared access signature without creating a new client.

    :param str signature: The shared access signature used to authenticate to an Azure service
    :raises: TypeError
    """

    def __init__(self, signature):
        # type: (str) -> None
        if not isinstance(signature, six.string_types):
            raise TypeError("signature must be a string.")
        self._signature = signature  # type: str

    @property
    def signature(self):
        # type () -> str
        """The value of the configured shared access signature.

        :rtype: str
        """
        return self._signature

    def update(self, signature):
        # type: (str) -> None
        """Update the shared access signature.

        This can be used when you've regenerated your shared access signature and want
        to update long-lived clients.

        :param str signature: The shared access signature used to authenticate to an Azure service
        :raises: ValueError or TypeError
        """
        if not signature:
            raise ValueError("The signature used for updating can not be None or empty")
        if not isinstance(signature, six.string_types):
            raise TypeError("The signature used for updating must be a string.")
        self._signature = signature
