import sqlite3
from hashlib import sha1
from pathlib import Path
from tempfile import gettempdir
from threading import RLock
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

from .bucket import AbstractBucket

TEMP_DIR = Path(gettempdir())
DEFAULT_DB_PATH = TEMP_DIR / "pyrate_limiter.sqlite"
LOCK_PATH = TEMP_DIR / "pyrate_limiter.lock"
SQLITE_MAX_VARIABLE_NUMBER = 999


class SQLiteBucket(AbstractBucket):
    """Bucket backed by a SQLite database. Will be stored in the system temp directory by default.

    Notes on concurrency:

    * Thread-safe
    * For usage with multiprocessing, see :py:class:`.FileLockSQLiteBucket`.
    * Transactions are locked at the bucket level, but not at the connection or database level.
    * The default isolation level is used (autocommit).
    * Multitple buckets may be used in parallel, but a given bucket will only be used by one
      thread/process at a time.

    Args:
        maxsize: Maximum number of items in the bucket
        identity: Bucket identity, used as the table name
        path: Path to the SQLite database file; defaults to a temp file in the system temp directory
        kwargs: Additional keyword arguments for :py:func:`sqlite3.connect`
    """

    def __init__(
        self,
        maxsize: int = 0,
        identity: str = None,
        path: Union[Path, str] = DEFAULT_DB_PATH,
        **kwargs,
    ):
        super().__init__(maxsize=maxsize)
        kwargs.setdefault("check_same_thread", False)
        self.connection_kwargs = kwargs

        self._connection: Optional[sqlite3.Connection] = None
        self._lock = RLock()
        self._path = Path(path)
        self._size: Optional[int] = None

        if not identity:
            raise ValueError("Bucket identity is required")

        # Hash identity to use as a table name, to avoid potential issues with user-provided values
        self.table = f"ratelimit_{sha1(identity.encode()).hexdigest()}"

    @property
    def connection(self) -> sqlite3.Connection:
        """Create a database connection and initialize the table, if it hasn't already been done.
        This is safe to leave open, but may be manually closed with :py:meth:`.close`, if needed.
        """
        if not self._connection:
            self.connection_kwargs.setdefault("check_same_thread", False)
            self._connection = sqlite3.connect(str(self._path), **self.connection_kwargs)
            assert self._connection
            self._connection.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table} (idx INTEGER PRIMARY KEY AUTOINCREMENT, value REAL)"
            )
        return self._connection

    def lock_acquire(self):
        """Acquire a lock prior to beginning a new transaction"""
        self._lock.acquire()

    def lock_release(self):
        """Release lock following a transaction"""
        self._lock.release()

    def close(self):
        """Close the database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def size(self) -> int:
        """Keep bucket size in memory to avoid some unnecessary reads"""
        if self._size is None:
            self._size = self._query_size()
        return self._size

    def _query_size(self) -> int:
        """Keep bucket size in memory to avoid some unnecessary reads"""
        return self.connection.execute(f"SELECT COUNT(*) FROM {self.table}").fetchone()[0]

    def _update_size(self, amount: int):
        self._size = self.size() + amount

    def put(self, item: float) -> int:
        """Put an item in the bucket.
        Return 1 if successful, else 0
        """
        if self.size() < self.maxsize():
            self.connection.execute(f"INSERT INTO {self.table} (value) VALUES (?)", (item,))
            self.connection.commit()
            self._update_size(1)
            return 1
        return 0

    def get(self, number: int = 1) -> int:
        """Get items and remove them from the bucket in the FIFO fashion.
        Return the number of items that have been removed.
        """
        keys = [str(key) for key in self._get_keys(number)]
        for chunk in chunkify(keys, SQLITE_MAX_VARIABLE_NUMBER):
            placeholders = ",".join("?" * len(chunk))
            self.connection.execute(f"DELETE FROM {self.table} WHERE idx IN ({placeholders})", chunk)
            self.connection.commit()

        self._update_size(0 - len(keys))
        return len(keys)

    def _get_keys(self, number: int = 1) -> List[float]:
        rows = self.connection.execute(f"SELECT idx FROM {self.table} ORDER BY idx LIMIT ?", (number,)).fetchall()
        return [row[0] for row in rows]

    def all_items(self) -> List[float]:
        """Return a list as copies of all items in the bucket"""
        rows = self.connection.execute(f"SELECT value FROM {self.table} ORDER BY idx").fetchall()
        return [row[0] for row in rows]

    def flush(self):
        self.connection.execute(f"DELETE FROM {self.table}")
        self.connection.commit()


def chunkify(iterable: Iterable, max_size: int) -> Iterator[List]:
    """Split an iterable into chunks of a max size"""
    iterable = list(iterable)
    for index in range(0, len(iterable), max_size):
        yield iterable[index : index + max_size]


# Create file lock in module scope to reuse across buckets
try:
    from filelock import FileLock

    FILE_LOCK = FileLock(str(LOCK_PATH))
except ImportError:
    pass


class FileLockSQLiteBucket(SQLiteBucket):
    """Bucket backed by a SQLite database and file lock. Suitable for usage from multiple processes
    with no shared state. Requires installing [py-filelock](https://py-filelock.readthedocs.io).

    The file lock is reentrant and shared across buckets, allowing a process to access multiple
    buckets at once.
    """

    def __init__(self, **kwargs):
        # If not installed, raise ImportError at init time instead of at module import time
        from filelock import FileLock  # noqa: F401

        super().__init__(**kwargs)
        self._lock = FILE_LOCK

    def size(self) -> int:
        """Query current size from the database for each call instead of keeping in memory"""
        return self._query_size()

    def _update_size(self, _):
        pass
