"""This file contains custom exception classes for the Google Threat Intelligence connector."""


class GTIRelevanceSystemAlertsException(Exception):
    """Exception class to handle Google Threat Intelligence Relevance System Alerts connector exceptions.

    Args:
        Exception (string): Will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom GTI Relevance System Alerts exception with custom message."""
        super().__init__(message)


class GTIRelevanceSystemAlertsTimeoutException(Exception):
    """Exception class to handle Google Threat Intelligence Relevance System Alerts function timeout.

    Raised when the Azure Function approaches the 9:30-minute execution limit.

    Args:
        Exception (string): Will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom GTI Relevance System Alerts timeout exception with custom message."""
        super().__init__(message)


class GTIRelevanceSystemAlertsAuthException(Exception):
    """Exception class to handle Google Threat Intelligence Relevance System Alerts authentication failures.

    Raised when token exchange fails or credentials are invalid.

    Args:
        Exception (string): Will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom GTI Relevance System Alerts authentication exception with custom message."""
        super().__init__(message)
