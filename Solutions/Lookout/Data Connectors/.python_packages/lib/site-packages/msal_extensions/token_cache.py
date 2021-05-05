"""Generic functions and types for working with a TokenCache that is not platform specific."""
import os
import warnings
import time
import logging

import msal

from .cache_lock import CrossPlatLock
from .persistence import (
    _mkdir_p, PersistenceNotFound, FilePersistence,
    FilePersistenceWithDataProtection, KeychainPersistence)


logger = logging.getLogger(__name__)

class PersistedTokenCache(msal.SerializableTokenCache):
    """A token cache using given persistence layer, coordinated by a file lock."""

    def __init__(self, persistence, lock_location=None):
        super(PersistedTokenCache, self).__init__()
        self._lock_location = (
            os.path.expanduser(lock_location) if lock_location
            else persistence.get_location() + ".lockfile")
        _mkdir_p(os.path.dirname(self._lock_location))
        self._persistence = persistence
        self._last_sync = 0  # _last_sync is a Unixtime
        self.is_encrypted = persistence.is_encrypted

    def _reload_if_necessary(self):
        # type: () -> None
        """Reload cache from persistence layer, if necessary"""
        try:
            if self._last_sync < self._persistence.time_last_modified():
                self.deserialize(self._persistence.load())
                self._last_sync = time.time()
        except PersistenceNotFound:
            # From cache's perspective, a nonexistent persistence is a NO-OP.
            pass
        # However, existing data unable to be decrypted will still be bubbled up.

    def modify(self, credential_type, old_entry, new_key_value_pairs=None):
        with CrossPlatLock(self._lock_location):
            self._reload_if_necessary()
            super(PersistedTokenCache, self).modify(
                credential_type,
                old_entry,
                new_key_value_pairs=new_key_value_pairs)
            self._persistence.save(self.serialize())
            self._last_sync = time.time()

    def find(self, credential_type, **kwargs):  # pylint: disable=arguments-differ
        with CrossPlatLock(self._lock_location):
            self._reload_if_necessary()
            return super(PersistedTokenCache, self).find(credential_type, **kwargs)


class FileTokenCache(PersistedTokenCache):
    """A token cache which uses plain text file to store your tokens."""
    def __init__(self, cache_location, **ignored):  # pylint: disable=unused-argument
        warnings.warn("You are using an unprotected token cache", RuntimeWarning)
        warnings.warn("Use PersistedTokenCache(...) instead", DeprecationWarning)
        super(FileTokenCache, self).__init__(FilePersistence(cache_location))

UnencryptedTokenCache = FileTokenCache  # For backward compatibility


class WindowsTokenCache(PersistedTokenCache):
    """A token cache which uses Windows DPAPI to encrypt your tokens."""
    def __init__(
            self, cache_location, entropy='',
            **ignored):  # pylint: disable=unused-argument
        warnings.warn("Use PersistedTokenCache(...) instead", DeprecationWarning)
        super(WindowsTokenCache, self).__init__(
            FilePersistenceWithDataProtection(cache_location, entropy=entropy))


class OSXTokenCache(PersistedTokenCache):
    """A token cache which uses native Keychain libraries to encrypt your tokens."""
    def __init__(self,
                 cache_location,
                 service_name='Microsoft.Developer.IdentityService',
                 account_name='MSALCache',
                 **ignored):  # pylint: disable=unused-argument
        warnings.warn("Use PersistedTokenCache(...) instead", DeprecationWarning)
        super(OSXTokenCache, self).__init__(
            KeychainPersistence(cache_location, service_name, account_name))

