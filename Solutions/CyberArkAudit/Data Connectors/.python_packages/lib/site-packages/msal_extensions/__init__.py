"""Provides auxiliary functionality to the `msal` package."""
__version__ = "1.1.0"

from .persistence import (
    FilePersistence,
    build_encrypted_persistence,
    FilePersistenceWithDataProtection,
    KeychainPersistence,
    LibsecretPersistence,
    )
from .cache_lock import CrossPlatLock
from .token_cache import PersistedTokenCache

