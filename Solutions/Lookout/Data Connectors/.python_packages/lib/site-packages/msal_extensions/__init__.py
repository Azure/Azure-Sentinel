"""Provides auxiliary functionality to the `msal` package."""
__version__ = "0.3.0"

import sys

from .persistence import (
    FilePersistence,
    FilePersistenceWithDataProtection,
    KeychainPersistence,
    LibsecretPersistence,
    )
from .cache_lock import CrossPlatLock
from .token_cache import PersistedTokenCache

if sys.platform.startswith('win'):
    from .token_cache import WindowsTokenCache as TokenCache
elif sys.platform.startswith('darwin'):
    from .token_cache import OSXTokenCache as TokenCache
else:
    from .token_cache import FileTokenCache as TokenCache
