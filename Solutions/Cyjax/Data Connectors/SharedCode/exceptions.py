"""This file contains custom Exception classes for Cyjax IOC connector."""


class CyjaxException(Exception):
    """Exception class to handle general Cyjax connector exceptions.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Cyjax exception with custom message."""
        super().__init__(message)


class CyjaxTimeoutException(Exception):
    """Exception class to handle Cyjax function timeout exceptions.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Cyjax timeout exception with custom message."""
        super().__init__(message)


class CyjaxAuthenticationException(Exception):
    """Exception class to handle Cyjax authentication exceptions.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Cyjax authentication exception with custom message."""
        super().__init__(message)


class CyjaxDataNotFoundException(Exception):
    """Exception class to handle Cyjax data not found exceptions.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Cyjax data not found exception with custom message."""
        super().__init__(message)


class CyjaxAPIException(Exception):
    """Exception class to handle Cyjax API call exceptions.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Cyjax API exception with custom message."""
        super().__init__(message)


class SentinelUploadException(Exception):
    """Exception class to handle Sentinel Upload Indicator API exceptions.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Sentinel upload exception with custom message."""
        super().__init__(message)
