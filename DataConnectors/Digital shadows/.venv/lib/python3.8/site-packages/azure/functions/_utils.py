# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List, Tuple, Optional
from datetime import datetime, timedelta


def try_parse_datetime_with_formats(
    datetime_str: str,
    datetime_formats: List[str]
) -> Tuple[Optional[datetime], Optional[str], Optional[Exception]]:
    """Try parsing the datetime string with a list of formats
    Parameters
    ----------
    datetime_str: str
        The datetime string needs to be parsed (e.g. 2018-12-12T03:16:34.2191Z)
    datetime_formats: List[str]
        A list of datetime formats that the parser would try to match

    Returns
    -------
    dict_obj: A serializable dictionary with enough metadata to reconstruct
              `obj`

    Exceptions
    ----------
    Tuple[Optional[datetime], Optional[str], Optional[Exception]]:
        If the datetime can be successfully parsed, the first element is the
        paresd datetime object and the second is the matched format.
        If the datetime cannot be parsed, the first and second element will be
        None, and the third is the exception from the datetime.strptime()
        method.
    """
    for fmt in datetime_formats:
        try:
            dt = datetime.strptime(datetime_str, fmt)
            return (dt, fmt, None)
        except ValueError as ve:
            last_exception = ve

    return (None, None, last_exception)


def try_parse_timedelta_with_formats(
    timedelta_str: str,
    timedelta_formats: List[str]
) -> Tuple[Optional[timedelta], Optional[str], Optional[Exception]]:
    """Try parsing the datetime delta string with a list of formats
    Parameters
    ----------
    timedelta_str: str
        The timedelta string needs to be parsed (e.g. 12:34:56)
    timedelta_formats: List[str]
        A list of datetime formats that the parser would try to match

    Returns
    -------
    dict_obj: A serializable dictionary with enough metadata to reconstruct
              `obj`

    Exceptions
    ----------
    Tuple[Optional[timedelta], Optional[str], Optional[Exception]]:
        If the timedelta can be successfully parsed, the first element is the
        paresd timedelta object and the second is the matched format.
        If the timedelta cannot be parsed, the first and second element will be
        None, and the third is the exception from the datetime.strptime()
        method.
    """

    for fmt in timedelta_formats:
        try:
            # If singular form %S, %M, %H, will just return the timedelta
            if fmt == '%S':
                td = timedelta(seconds=int(timedelta_str))
            elif fmt == '%M':
                td = timedelta(minutes=int(timedelta_str))
            elif fmt == '%H':
                td = timedelta(hours=int(timedelta_str))
            else:
                dt = datetime.strptime(timedelta_str, fmt)
                td = timedelta(hours=dt.hour,
                               minutes=dt.minute,
                               seconds=dt.second)
            return (td, fmt, None)
        except ValueError as ve:
            last_exception = ve

    return (None, None, last_exception)
