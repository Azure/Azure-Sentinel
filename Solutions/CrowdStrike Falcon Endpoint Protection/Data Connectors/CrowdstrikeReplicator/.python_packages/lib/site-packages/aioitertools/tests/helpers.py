# Copyright 2018 John Reese
# Licensed under the MIT license

import asyncio
import functools
from unittest import TestCase

from aioitertools.helpers import deprecated_wait_param, maybe_await


def async_test(fn):
    def wrapped(*args, **kwargs):
        try:
            loop = asyncio.new_event_loop()
            loop.set_debug(False)
            result = loop.run_until_complete(fn(*args, **kwargs))
            return result
        finally:
            loop.close()

    return wrapped


class HelpersTest(TestCase):

    # aioitertools.helpers.maybe_await()

    @async_test
    async def test_maybe_await(self):
        self.assertEqual(await maybe_await(42), 42)

    @async_test
    async def test_maybe_await_async_def(self):
        async def forty_two():
            await asyncio.sleep(0.0001)
            return 42

        self.assertEqual(await maybe_await(forty_two()), 42)

    @async_test
    async def test_maybe_await_coroutine(self):
        @asyncio.coroutine
        def forty_two():
            yield from asyncio.sleep(0.0001)
            return 42

        self.assertEqual(await maybe_await(forty_two()), 42)

    @async_test
    async def test_maybe_await_partial(self):
        async def multiply(a, b):
            await asyncio.sleep(0.0001)
            return a * b

        self.assertEqual(await maybe_await(functools.partial(multiply, 6)(7)), 42)

    @async_test
    async def test_deprecated_wait(self):
        @deprecated_wait_param
        async def foo(a, *, loop=None, frob=False):
            if frob:
                return a * a
            else:
                return a

        self.assertEqual(4, await foo(4))
        self.assertEqual(16, await foo(4, frob=True))

        with self.assertWarnsRegex(
            DeprecationWarning, r"foo\(\) parameter `loop` is deprecated"
        ):
            result = await foo(9, loop=object(), frob=True)
            self.assertEqual(81, result)

        with self.assertWarnsRegex(
            DeprecationWarning, r"foo\(\) parameter `loop` is deprecated"
        ):
            result = await foo(5, loop=None)
            self.assertEqual(5, result)
