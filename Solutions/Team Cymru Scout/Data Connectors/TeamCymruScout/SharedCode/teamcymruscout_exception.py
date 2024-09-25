"""This File contains custom Exception class for TeamCymruScout."""


class TeamCymruScoutException(Exception):
    """Exception class to handle TeamCymruScout exception."""

    def __init__(self, message=None):
        """Initialize custom TeamCymruScoutException with custom message."""
        super().__init__(message)


class SentinelIncorrectCredentialsException(Exception):
    """Exception class to handle Sentinel Invalid Credentials or Sentinel Service is unreachable."""

    def __init__(self, message=None):
        """Initialize exception with custom message."""
        super().__init__(message)


class InvalidDataFormatException(Exception):
    """Exception class to handle Invalid Data Format Exception when ingesting logs to sentinel."""

    def __init__(self, message=None):
        """Initialize exception with custom message."""
        super().__init__(message)
