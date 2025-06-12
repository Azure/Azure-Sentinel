# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
import collections.abc
import datetime
import json
import re
from typing import Dict, Optional, Union, Tuple, Mapping, Any

from ._thirdparty import typing_inspect
from ._utils import (
    try_parse_datetime_with_formats,
    try_parse_timedelta_with_formats
)


def is_iterable_type_annotation(annotation: object, pytype: object) -> bool:
    is_iterable_anno = (
        typing_inspect.is_generic_type(annotation)
        and issubclass(typing_inspect.get_origin(annotation),
                       collections.abc.Iterable)
    )

    if not is_iterable_anno:
        return False

    args = typing_inspect.get_args(annotation)
    if not args:
        return False

    if isinstance(pytype, tuple):
        return any(isinstance(t, type) and issubclass(t, arg)
                   for t in pytype for arg in args)
    else:
        return any(isinstance(pytype, type) and issubclass(pytype, arg)
                   for arg in args)


class Datum:
    def __init__(self, value: Any, type: Optional[str]):
        self.value: Any = value
        self.type: Optional[str] = type

    @property
    def python_value(self) -> Any:
        if self.value is None or self.type is None:
            return None
        elif self.type in ('bytes', 'string', 'int', 'double'):
            return self.value
        elif self.type == 'json':
            return json.loads(self.value)
        elif self.type == 'collection_string':
            return [v for v in self.value.string]
        elif self.type == 'collection_bytes':
            return [v for v in self.value.bytes]
        elif self.type == 'collection_double':
            return [v for v in self.value.double]
        elif self.type == 'collection_sint64':
            return [v for v in self.value.sint64]
        else:
            return self.value

    @property
    def python_type(self) -> type:
        return type(self.python_value)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.value == other.value and self.type == other.type

    def __hash__(self):
        return hash((type(self), (self.value, self.type)))

    def __repr__(self):
        val_repr = repr(self.value)
        if len(val_repr) > 10:
            val_repr = val_repr[:10] + '...'
        return '<Datum {} {}>'.format(self.type, val_repr)


class _ConverterMeta(abc.ABCMeta):

    _bindings: Dict[str, type] = {}

    def __new__(mcls, name, bases, dct, *,
                binding: Optional[str],
                trigger: Optional[str] = None):
        cls = super().__new__(mcls, name, bases, dct)
        cls._trigger = trigger  # type: ignore
        if binding is None:
            return cls

        if binding in mcls._bindings:
            raise RuntimeError(
                f'cannot register a converter for {binding!r} binding: '
                f'another converter for this binding has already been '
                f'registered')

        mcls._bindings[binding] = cls
        if trigger is not None:
            mcls._bindings[trigger] = cls

        return cls

    @classmethod
    def get(cls, binding_name):
        return cls._bindings.get(binding_name)

    def has_trigger_support(cls) -> bool:
        return cls._trigger is not None  # type: ignore


class _BaseConverter(metaclass=_ConverterMeta, binding=None):

    @classmethod
    def _decode_typed_data(
            cls, data: Datum, *,
            python_type: Union[type, Tuple[type, ...]],
            context: str = 'data') -> Any:
        if data is None:
            return None

        data_type = data.type
        if data_type == 'json':
            result = json.loads(data.value)

        elif data_type == 'string':
            result = data.value

        elif data_type == 'int':
            result = data.value

        elif data_type == 'double':
            result = data.value

        elif data_type == 'collection_bytes':
            result = data.value

        elif data_type == 'collection_string':
            result = data.value

        elif data_type == 'collection_sint64':
            result = data.value

        elif data_type is None:
            return None

        else:
            raise ValueError(
                f'unsupported type of {context}: {data_type}')

        if not isinstance(result, python_type):
            if isinstance(python_type, (tuple, list, dict)):
                raise ValueError(
                    f'unexpected value type in {context}: '
                    f'{type(result).__name__}, expected one of: '
                    f'{", ".join(t.__name__ for t in python_type)}')
            else:
                try:
                    # Try coercing into the requested type
                    result = python_type(result)
                except (TypeError, ValueError) as e:
                    raise ValueError(
                        f'cannot convert value of {context} into '
                        f'{python_type.__name__}: {e}') from None

        return result

    @classmethod
    def _decode_trigger_metadata_field(
            cls, trigger_metadata: Mapping[str, Datum],
            field: str, *,
            python_type: Union[type, Tuple[type, ...]]) \
            -> Any:
        data = trigger_metadata.get(field)
        if data is None:
            return None
        else:
            return cls._decode_typed_data(
                data, python_type=python_type,
                context=f'field {field!r} in trigger metadata')

    @classmethod
    def _parse_datetime_metadata(
            cls, trigger_metadata: Mapping[str, Datum],
            field: str) -> Optional[datetime.datetime]:

        datetime_str = cls._decode_trigger_metadata_field(
            trigger_metadata, field, python_type=str)

        if datetime_str is None:
            return None
        else:
            return cls._parse_datetime(datetime_str)

    @classmethod
    def _parse_timedelta_metadata(
            cls, trigger_metadata: Mapping[str, Datum],
            field: str) -> Optional[datetime.timedelta]:

        timedelta_str = cls._decode_trigger_metadata_field(
            trigger_metadata, field, python_type=str)

        if timedelta_str is None:
            return None
        else:
            return cls._parse_timedelta(timedelta_str)

    @classmethod
    def _parse_datetime(
            cls, datetime_str: Optional[str]) -> Optional[datetime.datetime]:

        if not datetime_str:
            return None

        too_fractional = re.match(
            r'(.*\.\d{6})(\d+)(Z|[\+|-]\d{1,2}:\d{1,2}){0,1}', datetime_str)

        if too_fractional:
            # The supplied value contains seven digits in the
            # fractional second part, whereas Python expects
            # a maxium of six, so strip it.
            # https://github.com/Azure/azure-functions-python-worker/issues/269
            datetime_str = too_fractional.group(1) + (
                too_fractional.group(3) or '')

        # Try parse time
        utc_time, utc_time_error = cls._parse_datetime_utc(datetime_str)
        if not utc_time_error and utc_time:
            return utc_time.replace(tzinfo=datetime.timezone.utc)

        local_time, local_time_error = cls._parse_datetime_local(datetime_str)
        if not local_time_error and local_time:
            return local_time.replace(tzinfo=None)

        # Report error
        if utc_time_error:
            raise utc_time_error
        elif local_time_error:
            raise local_time_error
        else:
            return None

    @classmethod
    def _parse_timedelta(
        cls,
        timedelta_str: Optional[str]
    ) -> Optional[datetime.timedelta]:

        if not timedelta_str:
            return None

        # Try parse timedelta
        timedelta, td_error = cls._parse_timedelta_internal(timedelta_str)
        if timedelta is not None:
            return timedelta

        # Report error
        if td_error:
            raise td_error
        else:
            return None

    @classmethod
    def _parse_datetime_utc(
        cls,
        datetime_str: str
    ) -> Tuple[Optional[datetime.datetime], Optional[Exception]]:

        # UTC ISO 8601 assumed
        # 2018-08-07T23:17:57.461050Z
        utc_formats = [
            '%Y-%m-%dT%H:%M:%S+00:00',
            '%Y-%m-%dT%H:%M:%S-00:00',
            '%Y-%m-%dT%H:%M:%S.%f+00:00',
            '%Y-%m-%dT%H:%M:%S.%f-00:00',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',

            '%m/%d/%Y %H:%M:%SZ',
            '%m/%d/%Y %H:%M:%S.%fZ',
            '%m/%d/%Y %H:%M:%S+00:00',
            '%m/%d/%Y %H:%M:%S-00:00',
            '%m/%d/%Y %H:%M:%S.%f+00:00',
            '%m/%d/%Y %H:%M:%S.%f-00:00',
        ]

        dt, _, excpt = try_parse_datetime_with_formats(
            datetime_str, utc_formats)

        if excpt is not None:
            return None, excpt
        return dt, None

    @classmethod
    def _parse_datetime_local(
        cls, datetime_str: str
    ) -> Tuple[Optional[datetime.datetime], Optional[Exception]]:
        """Parse a string into a datetime object, accepts following formats
        1. Without fractional seconds (e.g. 2018-08-07T23:17:57)
        2. With fractional seconds (e.g. 2018-08-07T23:17:57.461050)

        Parameters
        ----------
        datetime_str: str
            The string represents a datetime

        Returns
        -------
        Tuple[Optional[datetime.datetime], Optional[Exception]]
            If the datetime_str is None, will return None immediately.
            If the datetime_str can be parsed correctly, it will return as the
            first element in the tuple.
            If the datetime_str cannot be parsed with all attempts, it will
            return None in the first element, the exception in the second
            element.
        """

        local_formats = [
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',

            '%m/%d/%YT%H:%M:%S.%f',
            '%m/%d/%YT%H:%M:%S'
        ]

        dt, _, excpt = try_parse_datetime_with_formats(
            datetime_str, local_formats)

        if excpt is not None:
            return None, excpt
        return dt, None

    @classmethod
    def _parse_timedelta_internal(
        cls, timedelta_str: str
    ) -> Tuple[Optional[datetime.timedelta], Optional[Exception]]:
        """Parse a string into a timedelta object, accepts following formats
        1. HH:MM:SS (e.g. 12:34:56)
        2. MM:SS (e.g. 34:56)
        3. Pure integer as seconds (e.g. 5819)

        Parameters
        ----------
        timedelta_str: str
            The string represents a datetime

        Returns
        -------
        Tuple[Optional[datetime.timedelta], Optional[Exception]]
            If the timedelta_str is None, will return None immediately.
            If the timedelta_str can be parsed correctly, it will return as the
            first element in the tuple.
            If the timedelta_str cannot be parsed with all attempts, it will
            return None in the first element, the exception in the second
            element.
        """

        timedelta_formats = [
            '%H:%M:%S',
            '%M:%S',
            '%S'
        ]

        td, _, excpt = try_parse_timedelta_with_formats(
            timedelta_str, timedelta_formats)

        if td is not None:
            return td, None
        return None, excpt


class InConverter(_BaseConverter, binding=None):

    @classmethod
    @abc.abstractmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def decode(cls, data: Datum, *, trigger_metadata) -> Any:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def has_implicit_output(cls) -> bool:
        return False


class OutConverter(_BaseConverter, binding=None):

    @classmethod
    @abc.abstractmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> Optional[Datum]:
        raise NotImplementedError


def get_binding_registry():
    return _ConverterMeta
