"""Exceptions raised by the Censys risk events connector."""


class CensysException(Exception):
    """Generic connector error."""


class CensysAuthError(CensysException):
    """The Censys API rejected the credentials or the organization."""


class CensysCursorExpired(CensysException):
    """The checkpoint is older than the Censys event retention window (HTTP 410)."""


class CensysTimeBudgetReached(CensysException):
    """The run used its time budget. Everything ingested so far is already checkpointed."""
