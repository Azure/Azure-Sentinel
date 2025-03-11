"""This File contains custom Exception class foe Bitsight."""


class BitSightException(Exception):
    """Exception class to handle BitSight exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom BitSightException with custom message."""
        super().__init__(message)
