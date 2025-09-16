#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import inspect
import re
from abc import ABCMeta
from enum import Enum
from json import JSONEncoder
from typing import Any, TypeVar, Optional, Union, Iterable, Type, Callable

T = TypeVar("T", bound=Enum)
SNAKE_CASE_RE = re.compile(r'^([a-zA-Z]+\d*_|_+[a-zA-Z\d])\w*$')
WORD_RE = re.compile(r'^([a-zA-Z]+\d*)$')


class StringifyEnum(Enum):
    """This class output name of enum object when printed as string."""

    def __str__(self):
        return str(self.name)


class BuildDictMeta(type):
    def __new__(mcs, name, bases, dct):
        """BuildDictMeta will apply to every binding.
        It will apply :meth:`add_to_dict` decorator to :meth:`__init__` of
        every binding class to collect list of params to include in building
        json dictionary which corresponds to function.json in legacy app.
        It will also apply :meth:`skip_none` to :meth:`get_dict_repr` to
        enable json dictionary generated for every binding has non-empty
        value fields. It is needed for enabling binding param optionality.
        """
        cls = super().__new__(mcs, name, bases, dct)
        setattr(cls, '__init__',
                cls.add_to_dict(getattr(cls, '__init__')))
        setattr(cls, 'get_dict_repr',
                cls.skip_none(getattr(cls, 'get_dict_repr')))
        return cls

    @staticmethod
    def skip_none(func):
        def wrapper(*args, **kw):
            res = func(*args, **kw)
            return BuildDictMeta.clean_nones(res)

        return wrapper

    @staticmethod
    def add_to_dict(func: Callable[..., Any]):
        def wrapper(*args, **kwargs):
            if args is None or len(args) == 0:
                raise ValueError(
                    f'{func.__name__} has no args. Please ensure func is an '
                    f'object method.')

            func(*args, **kwargs)

            self = args[0]

            init_params = list(inspect.signature(func).parameters.keys())
            init_params.extend(list(kwargs.keys()))
            for key in kwargs.keys():
                if not hasattr(self, key):
                    setattr(self, key, kwargs[key])

            setattr(self, 'init_params', init_params)

        return wrapper

    @staticmethod
    def clean_nones(value):
        """
        Recursively remove all None values from dictionaries and lists,
        and returns
        the result as a new dictionary or list.
        """
        if isinstance(value, list):
            return [BuildDictMeta.clean_nones(x) for x in value if
                    x is not None]
        elif isinstance(value, dict):
            return {
                key: BuildDictMeta.clean_nones(val)
                for key, val in value.items()
                if val is not None
            }
        else:
            return value


class ABCBuildDictMeta(ABCMeta, BuildDictMeta):
    pass


def parse_singular_param_to_enum(param: Optional[Union[T, str]],
                                 class_name: Type[T]) -> Optional[T]:
    if param is None:
        return None
    if isinstance(param, str):
        try:
            return class_name[param.upper()]
        except KeyError:
            raise KeyError(
                f"Can not parse str '{param}' to {class_name.__name__}. "
                f"Allowed values are {[e.name for e in class_name]}")

    return param


def parse_iterable_param_to_enums(
        param_values: Optional[Union[Iterable[str], Iterable[T]]],
        class_name: Type[T]) -> Optional[Iterable[T]]:
    if param_values is None:
        return None

    try:
        return [class_name[value.upper()] if isinstance(value, str) else value
                for value in param_values]
    except KeyError:
        raise KeyError(
            f"Can not parse '{param_values}' to "
            f"Optional[Iterable[{class_name.__name__}]]. "
            f"Please ensure param all list elements exist in "
            f"{[e.name for e in class_name]}")


def to_camel_case(snake_case_str: str):
    if snake_case_str is None or len(snake_case_str) == 0:
        raise ValueError(
            f"Please ensure arg name {snake_case_str} is not empty!")

    if not is_snake_case(snake_case_str) and not is_word(snake_case_str):
        raise ValueError(
            f"Please ensure {snake_case_str} is a word or snake case "
            f"string with underscore as separator.")
    words = snake_case_str.split('_')
    return words[0] + ''.join([ele.title() for ele in words[1:]])


def is_snake_case(input_string: str) -> bool:
    """
    Checks if a string is formatted as "snake case".
    A string is considered snake case when:
    - it's composed only by lowercase/uppercase letters and digits
    - it contains at least one underscore
    - it does not start with a number
    *Examples:*
    >>> is_snake_case('foo_bar_baz') # returns true
    >>> is_snake_case('foo') # returns false
    :param input_string: String to test.
    :return: True for a snake case string, false otherwise.
    """
    return SNAKE_CASE_RE.match(input_string) is not None


def is_word(input_string: str) -> bool:
    """
    Checks if a string is one word.
    A string is considered one word when:
    - it's composed only by lowercase/uppercase letters and digits
    - it does not start with a number
    *Examples:*
    >>> is_word('1foo') # returns false
    >>> is_word('foo_') # returns false
    >>> is_word('foo') # returns true
    :param input_string: String to test.
    :return: True for one word string, false otherwise.
    """
    return WORD_RE.match(input_string) is not None


class StringifyEnumJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, StringifyEnum):
            return str(o)

        return super().default(o)
