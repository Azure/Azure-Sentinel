"""This module is for generating exception."""


class APIKeyNotProvidedError(Exception):
    """Represents an APIKeyNotProvidedError Exception object."""

    pass


class DomainNotProvidedError(Exception):
    """Represents an DomainNotProvidedError Exception object."""

    pass


class BaseURLNotProvidedError(ValueError):
    """Represents an BaseURLNotProvidedError Exception object."""

    pass


class NoDataError(ValueError):
    """Represents an NoDataError Exception object."""

    pass


class SSFactorException(Exception):
    """Represents an SecurityScorecard FactorException Exception object."""

    pass
