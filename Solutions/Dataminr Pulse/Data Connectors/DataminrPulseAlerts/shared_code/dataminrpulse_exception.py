"""This File contains custom Exception class for DataminrPulse."""


class DataminrPulseException(Exception):
    """Exception class to handle DataminrPulse exception."""

    def __init__(self, message=None):
        """Initialize custom DatMinrException with custom message."""
        super().__init__(message)
