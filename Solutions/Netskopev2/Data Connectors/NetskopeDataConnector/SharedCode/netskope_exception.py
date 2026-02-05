"""This File contains custom Exception class for Netskope."""


class NetskopeException(Exception):
    """Exception class to handle Netskope exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom NetskopeException with custom message."""
        super().__init__(message)
