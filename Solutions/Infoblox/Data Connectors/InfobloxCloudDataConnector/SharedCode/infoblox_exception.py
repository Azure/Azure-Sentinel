"""This File contains custom Exception class for Infoblox."""


class InfobloxException(Exception):
    """Exception class to handle Infoblox exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Infoblox exception with custom message."""
        super().__init__(message)


class InfobloxTimeoutException(Exception):
    """Exception class to handle Infoblox exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Infoblox exception with custom message."""
        super().__init__(message)
