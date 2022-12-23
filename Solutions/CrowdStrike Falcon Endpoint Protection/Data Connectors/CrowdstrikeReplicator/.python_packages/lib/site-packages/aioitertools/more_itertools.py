# Copyright 2020 John Reese
# Licensed under the MIT license

from typing import AsyncIterable, List, TypeVar

from .builtins import iter
from .itertools import islice
from .types import AnyIterable

T = TypeVar("T")


async def take(n: int, iterable: AnyIterable[T]) -> List[T]:
    """
    Return the first n items of iterable as a list.

    If there are too few items in iterable, all of them are returned.
    n needs to be at least 0. If it is 0, an empty list is returned.

    Example::

        first_two = await take(2, [1, 2, 3, 4, 5])

    """
    if n < 0:
        raise ValueError("take's first parameter can't be negative")
    return [item async for item in islice(iterable, n)]


async def chunked(iterable: AnyIterable[T], n: int) -> AsyncIterable[List[T]]:
    """
    Break iterable into chunks of length n.

    The last chunk will be shorter if the total number of items is not
    divisible by n.

    Example::

        async for chunk in chunked([1, 2, 3, 4, 5], n=2):
            ...  # first iteration: chunk == [1, 2]; last one: chunk == [5]
    """
    it = iter(iterable)
    chunk = await take(n, it)
    while chunk != []:
        yield chunk
        chunk = await take(n, it)
