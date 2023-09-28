from time import monotonic
from typing import Any
from typing import Callable
from typing import Dict
from typing import Type
from typing import Union

from .bucket import AbstractBucket
from .bucket import MemoryQueueBucket
from .exceptions import BucketFullException
from .exceptions import InvalidParams
from .limit_context_decorator import LimitContextDecorator
from .request_rate import RequestRate


class Limiter:
    """Main rate-limiter class

    Args:
        rates: Request rate definitions
        bucket_class: Bucket backend to use; may be any subclass of :py:class:`.AbstractBucket`.
            See :py:mod`pyrate_limiter.bucket` for available bucket classes.
        bucket_kwargs: Extra keyword arguments to pass to the bucket class constructor.
        time_function: Time function that returns the current time as a float, in seconds
    """

    def __init__(
        self,
        *rates: RequestRate,
        bucket_class: Type[AbstractBucket] = MemoryQueueBucket,
        bucket_kwargs: Dict[str, Any] = None,
        time_function: Callable[[], float] = None,
    ):
        self._validate_rate_list(rates)

        self._rates = rates
        self._bkclass = bucket_class
        self._bucket_args = bucket_kwargs or {}
        self._validate_bucket()

        self.bucket_group: Dict[str, AbstractBucket] = {}
        self.time_function = monotonic
        if time_function is not None:
            self.time_function = time_function
        # Call for time_function to make an anchor if required.
        self.time_function()

    def _validate_rate_list(self, rates):  # pylint: disable=no-self-use
        """Raise exception if rates are incorrectly ordered."""
        if not rates:
            raise InvalidParams("Rate(s) must be provided")

        for idx, rate in enumerate(rates[1:]):
            prev_rate = rates[idx]
            invalid = rate.limit <= prev_rate.limit or rate.interval <= prev_rate.interval
            if invalid:
                msg = f"{prev_rate} cannot come before {rate}"
                raise InvalidParams(msg)

    def _validate_bucket(self):
        """Try initialize a bucket to check if ok"""
        bucket = self._bkclass(maxsize=self._rates[-1].limit, identity="_", **self._bucket_args)
        del bucket

    def _init_buckets(self, identities) -> None:
        """Initialize a bucket for each identity, if needed.
        The bucket's maxsize equals the max limit of request-rates.
        """
        maxsize = self._rates[-1].limit
        for item_id in sorted(identities):
            if not self.bucket_group.get(item_id):
                self.bucket_group[item_id] = self._bkclass(
                    maxsize=maxsize,
                    identity=item_id,
                    **self._bucket_args,
                )
            self.bucket_group[item_id].lock_acquire()

    def _release_buckets(self, identities) -> None:
        """Release locks after bucket transactions, if applicable"""
        for item_id in sorted(identities):
            self.bucket_group[item_id].lock_release()

    def try_acquire(self, *identities: str) -> None:
        """Attempt to acquire an item, or raise an error if a rate limit has been exceeded.

        Args:
            identities: One or more identities to acquire. Typically this is the name of a service
                or resource that is being rate-limited.

        Raises:
            :py:exc:`BucketFullException`: If the bucket is full and the item cannot be acquired
        """
        self._init_buckets(identities)
        now = round(self.time_function(), 3)

        for rate in self._rates:
            for item_id in identities:
                bucket = self.bucket_group[item_id]
                volume = bucket.size()

                if volume < rate.limit:
                    continue

                # Determine rate's starting point, and check requests made during its time window
                item_count, remaining_time = bucket.inspect_expired_items(now - rate.interval)
                if item_count >= rate.limit:
                    self._release_buckets(identities)
                    raise BucketFullException(item_id, rate, remaining_time)

                # Remove expired bucket items beyond the last (maximum) rate limit,
                if rate is self._rates[-1]:
                    bucket.get(volume - item_count)

        # If no buckets are full, add another item to each bucket representing the next request
        for item_id in identities:
            self.bucket_group[item_id].put(now)
        self._release_buckets(identities)

    def ratelimit(
        self,
        *identities: str,
        delay: bool = False,
        max_delay: Union[int, float] = None,
    ):
        """A decorator and contextmanager that applies rate-limiting, with async support.
        Depending on arguments, calls that exceed the rate limit will either raise an exception, or
        sleep until space is available in the bucket.

        Args:
            identities: One or more identities to acquire. Typically this is the name of a service
                or resource that is being rate-limited.
            delay: Delay until the next request instead of raising an exception
            max_delay: The maximum allowed delay time (in seconds); anything over this will raise
                an exception

        Raises:
            :py:exc:`BucketFullException`: If the rate limit is reached, and ``delay=False`` or the
                delay exceeds ``max_delay``
        """
        return LimitContextDecorator(self, *identities, delay=delay, max_delay=max_delay)

    def get_current_volume(self, identity) -> int:
        """Get current bucket volume for a specific identity"""
        bucket = self.bucket_group[identity]
        return bucket.size()

    def flush_all(self) -> int:
        cnt = 0

        for _, bucket in self.bucket_group.items():
            bucket.flush()
            cnt += 1

        return cnt
