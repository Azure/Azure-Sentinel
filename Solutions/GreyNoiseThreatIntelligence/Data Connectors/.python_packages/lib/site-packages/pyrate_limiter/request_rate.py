"""Initialize this class to define request-rates for limiter
"""
from enum import Enum
from typing import Any
from typing import Dict

from .exceptions import ImmutableClassProperty


class ResetTypes(Enum):
    SCHEDULED = 1
    INTERVAL = 2


class RequestRate:
    """Request rate definition.

    Args:
        limit: Number of requests allowed within ``interval``
        interval: Time interval, in seconds
    """

    def __init__(
        self,
        limit: int,
        interval: int,
        reset: ResetTypes = ResetTypes.INTERVAL,
    ):
        self._limit = limit
        self._interval = interval
        self._reset = reset
        self._log: Dict[Any, Any] = {}

    @property
    def limit(self) -> int:
        return self._limit

    @limit.setter
    def limit(self, _):
        raise ImmutableClassProperty(self, "limit")

    @property
    def interval(self) -> int:
        return self._interval

    @interval.setter
    def interval(self, _):
        raise ImmutableClassProperty(self, "interval")

    def __str__(self):
        return f"{self.limit}/{self.interval}"
