"""This File contains custom Exception class for Vectra."""


class VectraException(Exception):
    """Exception class to handle Vectra exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Vectra exception with custom message."""
        super().__init__(message)


class VectraTimeoutException(Exception):
    """Exception class to handle Vectra exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Vectra exception with custom message."""
        super().__init__(message)
