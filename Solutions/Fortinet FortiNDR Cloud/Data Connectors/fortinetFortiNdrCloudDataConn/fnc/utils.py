
from datetime import datetime, timezone

import dateparser

from .errors import ErrorMessages, ErrorType, FncClientError
from .global_variables import DEFAULT_DATE_FORMAT

__all__ = ['datetime_to_utc_str', 'str_to_utc_datetime']


def datetime_to_utc_str(datetime_obj: datetime = None, format: str = None) -> str:
    if not datetime_obj:
        return ''

    if not datetime_obj.tzinfo:
        datetime_obj.replace(tzinfo=timezone.utc)
    else:
        datetime_obj = datetime_obj.astimezone(timezone.utc)

    format = format or DEFAULT_DATE_FORMAT
    try:
        return datetime.strftime(datetime_obj, format)
    except Exception as e:
        error = f'Date cannot be converted to str due to: {e}'
        raise FncClientError(
            error_type=ErrorType.GENERIC_ERROR,
            error_message=ErrorMessages.GENERIC_ERROR_MESSAGE,
            error_data={'error': error},
            exception=e
        ) from e


def str_to_utc_datetime(datetime_str: str = None, format: str = None) -> datetime:
    if not datetime_str:
        return None
    format = format or DEFAULT_DATE_FORMAT

    datetime_obj = None
    try:
        datetime_obj = datetime.strptime(datetime_str, format)
    except Exception as e:
        try:
            datetime_obj = dateparser.parse(datetime_str, settings={'STRICT_PARSING': True, 'TIMEZONE': 'UTC'})
        except Exception as ex:
            error = f"Date '{datetime_str}' cannot be converted from str due to: {e}.\n Parsing it as a relative date also failed due to: {ex}."
            raise ValueError(error)

    if not datetime_obj:
        error = f"Date '{datetime_str}' cannot be parsed."
        error += " Ensure it is in proper format '{format}' or it is a relative dates string like '1 day ago', 'yesterday', etc."
        raise ValueError(error)

    if not datetime_obj.tzinfo:
        datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)
    else:
        datetime_obj = datetime_obj.astimezone(timezone.utc)

    return datetime_obj
