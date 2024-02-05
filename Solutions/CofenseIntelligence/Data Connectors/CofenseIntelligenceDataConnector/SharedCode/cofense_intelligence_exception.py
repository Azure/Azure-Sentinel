"""This File contains custom Exception class for Cofense."""


class CofenseIntelligenceException(Exception):
    """Exception class to handle Cofense exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom CofenseIntelligenceException with custom message."""
        super().__init__(message)
