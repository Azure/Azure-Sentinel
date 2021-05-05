# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys
from typing import TYPE_CHECKING

import msal_extensions

if TYPE_CHECKING:
    from typing import Optional
    import msal


def load_service_principal_cache(allow_unencrypted):
    # type: (Optional[bool]) -> msal.TokenCache
    return _load_persistent_cache(allow_unencrypted, "MSALConfidentialCache", "msal.confidential.cache")


def load_user_cache(allow_unencrypted):
    # type: (Optional[bool]) -> msal.TokenCache
    return _load_persistent_cache(allow_unencrypted, "MSALCache", "msal.cache")


def _load_persistent_cache(allow_unencrypted, account_name, cache_name):
    # type: (Optional[bool], str, str) -> msal.TokenCache
    """Load the persistent cache using msal_extensions.

    On Windows the cache is a file protected by the Data Protection API. On Linux and macOS the cache is stored by
    libsecret and Keychain, respectively. On those platforms the cache uses the modified timestamp of a file on disk to
    decide whether to reload the cache.

    :param bool allow_unencrypted: when True, the cache will be kept in plaintext should encryption be impossible in the
        current environment
    """

    if sys.platform.startswith("win") and "LOCALAPPDATA" in os.environ:
        cache_location = os.path.join(os.environ["LOCALAPPDATA"], ".IdentityService", cache_name)
        persistence = msal_extensions.FilePersistenceWithDataProtection(cache_location)
    elif sys.platform.startswith("darwin"):
        # the cache uses this file's modified timestamp to decide whether to reload
        file_path = os.path.expanduser(os.path.join("~", ".IdentityService", cache_name))
        persistence = msal_extensions.KeychainPersistence(
            file_path, "Microsoft.Developer.IdentityService", account_name
        )
    elif sys.platform.startswith("linux"):
        # The cache uses this file's modified timestamp to decide whether to reload. Note this path is the same
        # as that of the plaintext fallback: a new encrypted cache will stomp an unencrypted cache.
        file_path = os.path.expanduser(os.path.join("~", ".IdentityService", cache_name))
        try:
            persistence = msal_extensions.LibsecretPersistence(
                file_path, cache_name, {"MsalClientID": "Microsoft.Developer.IdentityService"}, label=account_name
            )
        except ImportError:
            if not allow_unencrypted:
                raise ValueError(
                    "PyGObject is required to encrypt the persistent cache. Please install that library or ",
                    "specify 'allow_unencrypted_cache=True' to store the cache without encryption.",
                )
            persistence = msal_extensions.FilePersistence(file_path)
    else:
        raise NotImplementedError("A persistent cache is not available in this environment.")

    return msal_extensions.PersistedTokenCache(persistence)
