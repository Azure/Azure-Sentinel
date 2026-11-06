"""This file contains custom Exception classes for Rubrik."""


class RubrikException(Exception):
    """Base exception class to handle Rubrik errors.

    Args:
        message (str): exception message to surface.
    """

    def __init__(self, message: str = "") -> None:
        """Initialize custom RubrikException with a custom message."""
        super().__init__(message)


class RubrikTimeoutException(RubrikException):
    """Raised when the function approaches the Azure Functions execution timeout."""


class RubrikAuthenticationException(RubrikException):
    """Raised when authentication to the Log Ingestion API fails after retries."""
