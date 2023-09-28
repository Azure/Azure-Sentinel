import asyncio
from functools import partial
from functools import wraps
from inspect import iscoroutinefunction
from logging import getLogger
from time import sleep
from typing import TYPE_CHECKING
from typing import Union

from .exceptions import BucketFullException

logger = getLogger(__name__)

if TYPE_CHECKING:
    from .limiter import Limiter


class LimitContextDecorator:
    """A class that can be used as a:

    * decorator
    * async decorator
    * contextmanager
    * async contextmanager

    Intended to be used via :py:meth:`.Limiter.ratelimit`. Depending on arguments, calls that exceed
    the rate limit will either raise an exception, or sleep until space is available in the bucket.

    Args:
        limiter: Limiter object
        identities: Bucket identities
        delay: Delay until the next request instead of raising an exception
        max_delay: The maximum allowed delay time (in seconds); anything over this will raise
            an exception
    """

    def __init__(
        self,
        limiter: "Limiter",
        *identities: str,
        delay: bool = False,
        max_delay: Union[int, float] = None,
    ):
        self.delay = delay
        self.max_delay = max_delay or 0
        self.try_acquire = partial(limiter.try_acquire, *identities)

    def __call__(self, func):
        """Allows usage as a decorator for both normal and async functions"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.delayed_acquire()
            return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            await self.async_delayed_acquire()
            return await func(*args, **kwargs)

        # Return either an async or normal wrapper, depending on the type of the wrapped function
        return async_wrapper if iscoroutinefunction(func) else wrapper

    def __enter__(self):
        """Allows usage as a contextmanager"""
        self.delayed_acquire()

    def __exit__(self, *exc):
        pass

    async def __aenter__(self):
        """Allows usage as an async contextmanager"""
        await self.async_delayed_acquire()

    async def __aexit__(self, *exc):
        pass

    def delayed_acquire(self):
        """Delay and retry until we can successfully acquire an available bucket item"""
        while True:
            try:
                self.try_acquire()
            except BucketFullException as err:
                delay_time = self.delay_or_reraise(err)
                sleep(delay_time)
            else:
                break

    async def async_delayed_acquire(self):
        """Delay and retry until we can successfully acquire an available bucket item"""
        while True:
            try:
                self.try_acquire()
            except BucketFullException as err:
                delay_time = self.delay_or_reraise(err)
                await asyncio.sleep(delay_time)
            else:
                break

    def delay_or_reraise(self, err: BucketFullException) -> float:
        """Determine if we should delay after exceeding a rate limit. If so, return the delay time,
        otherwise re-raise the exception.
        """
        delay_time = float(err.meta_info["remaining_time"])
        logger.debug(f"Rate limit reached; {delay_time:.5f} seconds remaining before next request")
        exceeded_max_delay = bool(self.max_delay) and (delay_time > self.max_delay)
        if self.delay and not exceeded_max_delay:
            return delay_time
        raise err
