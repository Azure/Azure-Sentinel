"""This File contains custom Exception class for Mimecast."""


class MimecastException(Exception):
    """Exception class to handle Mimecast exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Mimecast exception with custom message."""
        super().__init__(message)


class MimecastTimeoutException(Exception):
    """Exception class to handle Mimecast exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Mimecast exception with custom message."""
        super().__init__(message)
