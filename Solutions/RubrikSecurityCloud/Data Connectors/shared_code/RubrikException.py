"""This File contains custom Exception class foe Rubrik."""


class RubrikException(Exception):
    """Exception class to handle Rubrik exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message: str) -> None:
        """Initialize custom RubrikException with custom message."""
        super().__init__(message)
