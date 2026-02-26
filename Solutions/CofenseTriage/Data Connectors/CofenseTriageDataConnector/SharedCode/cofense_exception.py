"""This File contains custom Exception class foe Cofense."""


class CofenseException(Exception):
    """Exception class to handle Cofense exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom CofenseException with custom message."""
        super().__init__(message)
