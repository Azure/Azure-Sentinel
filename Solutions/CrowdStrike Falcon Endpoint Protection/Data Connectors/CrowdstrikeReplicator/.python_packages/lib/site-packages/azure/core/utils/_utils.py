# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import datetime
from typing import Any, MutableMapping


class _FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC.

    Copy/pasted from Python doc

    :param int offset: offset in minutes
    """

    def __init__(self, offset):
        self.__offset = datetime.timedelta(minutes=offset)

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return str(self.__offset.total_seconds() / 3600)

    def __repr__(self):
        return "<FixedOffset {}>".format(self.tzname(None))

    def dst(self, dt):
        return datetime.timedelta(0)


try:
    from datetime import timezone

    TZ_UTC = timezone.utc  # type: ignore
except ImportError:
    TZ_UTC = _FixedOffset(0)  # type: ignore


def _convert_to_isoformat(date_time):
    """Deserialize a date in RFC 3339 format to datetime object.
    Check https://tools.ietf.org/html/rfc3339#section-5.8 for examples.
    """
    if not date_time:
        return None
    if date_time[-1] == "Z":
        delta = 0
        timestamp = date_time[:-1]
    else:
        timestamp = date_time[:-6]
        sign, offset = date_time[-6], date_time[-5:]
        delta = int(sign + offset[:1]) * 60 + int(sign + offset[-2:])

    check_decimal = timestamp.split('.')
    if len(check_decimal) > 1:
        decimal_str = ""
        for digit in check_decimal[1]:
            if digit.isdigit():
                decimal_str += digit
            else:
                break
        if len(decimal_str) > 6:
            timestamp = timestamp.replace(decimal_str, decimal_str[0:6])

    if delta == 0:
        tzinfo = TZ_UTC
    else:
        try:
            tzinfo = datetime.timezone(datetime.timedelta(minutes=delta))
        except AttributeError:
            tzinfo = _FixedOffset(delta)

    try:
        deserialized = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        deserialized = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    deserialized = deserialized.replace(tzinfo=tzinfo)
    return deserialized

def case_insensitive_dict(*args: Any, **kwargs: Any) -> MutableMapping:
    """Return a case-insensitive mutable mapping from an inputted mapping structure.

    :return: A case-insensitive mutable mapping object.
    :rtype: ~collections.abc.MutableMapping
    """

    # Rational is I don't want to re-implement this, but I don't want
    # to assume "requests" or "aiohttp" are installed either.
    # So I use the one from "requests" or the one from "aiohttp" ("multidict")
    # If one day this library is used in an HTTP context without "requests" nor "aiohttp" installed,
    # we can add "multidict" as a dependency or re-implement our own.
    try:
        from requests.structures import CaseInsensitiveDict

        return CaseInsensitiveDict(*args, **kwargs)
    except ImportError:
        pass
    try:
        # multidict is installed by aiohttp
        from multidict import CIMultiDict

        if len(kwargs) == 0 and len(args) == 1 and (not args[0]):
            return CIMultiDict()    # in case of case_insensitive_dict(None), we don't want to raise exception
        return CIMultiDict(*args, **kwargs)
    except ImportError:
        raise ValueError(
            "Neither 'requests' or 'multidict' are installed and no case-insensitive dict impl have been found"
        )
