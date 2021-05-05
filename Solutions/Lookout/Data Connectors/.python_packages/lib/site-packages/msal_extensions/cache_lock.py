"""Provides a mechanism for not competing with other processes interacting with an MSAL cache."""
import os
import sys
import errno
import portalocker
from distutils.version import LooseVersion


class CrossPlatLock(object):
    """Offers a mechanism for waiting until another process is finished interacting with a shared
    resource. This is specifically written to interact with a class of the same name in the .NET
    extensions library.
    """
    def __init__(self, lockfile_path):
        self._lockpath = lockfile_path
        # Support for passing through arguments to the open syscall was added in v1.4.0
        open_kwargs = {'buffering': 0} if LooseVersion(portalocker.__version__) >= LooseVersion("1.4.0") else {}
        self._lock = portalocker.Lock(
            lockfile_path,
            mode='wb+',
            # In posix systems, we HAVE to use LOCK_EX(exclusive lock) bitwise ORed
            # with LOCK_NB(non-blocking) to avoid blocking on lock acquisition.
            # More information here:
            # https://docs.python.org/3/library/fcntl.html#fcntl.lockf
            flags=portalocker.LOCK_EX | portalocker.LOCK_NB,
            **open_kwargs)

    def __enter__(self):
        file_handle = self._lock.__enter__()
        file_handle.write('{} {}'.format(os.getpid(), sys.argv[0]).encode('utf-8'))
        return file_handle

    def __exit__(self, *args):
        self._lock.__exit__(*args)
        try:
            # Attempt to delete the lockfile. In either of the failure cases enumerated below, it is
            # likely that another process has raced this one and ended up clearing or locking the
            # file for itself.
            os.remove(self._lockpath)
        except OSError as ex:  # pylint: disable=invalid-name
            if ex.errno != errno.ENOENT and ex.errno != errno.EACCES:
                raise
