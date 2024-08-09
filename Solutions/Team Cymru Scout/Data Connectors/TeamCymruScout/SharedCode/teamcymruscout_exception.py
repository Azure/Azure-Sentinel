"""This File contains custom Exception class for TeamCymruScout."""


class TeamCymruScoutException(Exception):
    """Exception class to handle TeamCymruScout exception."""

    def __init__(self, message=None):
        """Initialize custom TeamCymruScoutException with custom message."""
        super().__init__(message)
