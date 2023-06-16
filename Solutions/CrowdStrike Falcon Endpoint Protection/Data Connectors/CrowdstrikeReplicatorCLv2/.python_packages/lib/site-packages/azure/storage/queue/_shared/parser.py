# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from datetime import datetime, timezone

EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as MS filetime
HUNDREDS_OF_NANOSECONDS = 10000000

if sys.version_info < (3,):
    def _str(value):
        if isinstance(value, unicode):  # pylint: disable=undefined-variable
            return value.encode('utf-8')

        return str(value)
else:
    _str = str


def _to_utc_datetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')

def _rfc_1123_to_datetime(rfc_1123: str) -> datetime:
    """Converts an RFC 1123 date string to a UTC datetime.
    """
    if not rfc_1123:
        return None

    return datetime.strptime(rfc_1123, "%a, %d %b %Y %H:%M:%S %Z")

def _filetime_to_datetime(filetime: str) -> datetime:
    """Converts an MS filetime string to a UTC datetime. "0" indicates None.
    If parsing MS Filetime fails, tries RFC 1123 as backup.
    """
    if not filetime:
        return None

    # Try to convert to MS Filetime
    try:
        filetime = int(filetime)
        if filetime == 0:
            return None

        return datetime.fromtimestamp((filetime - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS, tz=timezone.utc)
    except ValueError:
        pass

    # Try RFC 1123 as backup
    return _rfc_1123_to_datetime(filetime)
