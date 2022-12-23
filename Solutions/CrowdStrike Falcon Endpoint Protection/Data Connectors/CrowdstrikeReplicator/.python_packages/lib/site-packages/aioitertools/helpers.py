# Copyright 2018 John Reese
# Licensed under the MIT license

import inspect
import sys
import warnings
from functools import wraps
from typing import Awaitable, Callable, Union

from .types import P, R, T

if sys.version_info < (3, 8):  # pragma: no cover
    from typing_extensions import Protocol
else:  # pragma: no cover
    from typing import Protocol


class Orderable(Protocol):  # pragma: no cover
    def __lt__(self, other):
        ...

    def __gt__(self, other):
        ...


async def maybe_await(object: Union[Awaitable[T], T]) -> T:
    if inspect.isawaitable(object):
        return await object  # type: ignore
    return object  # type: ignore


def deprecated_wait_param(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if "loop" in kwargs:  # type: ignore
            warnings.warn(
                f"{fn.__name__}() parameter `loop` is deprecated and ignored, "
                "will be removed in aioitertools v0.11.0",
                DeprecationWarning,
                stacklevel=2,
            )

        return fn(*args, **kwargs)

    return wrapper
