"""Exceptions for SecOps connector."""


class GoogleSecOpsConnectorError(Exception):
    """Base error for the SecOps connector."""


class GoogleSecOpsAuthError(GoogleSecOpsConnectorError):
    """Raised when Google OAuth token acquisition fails."""


class GoogleSecOpsApiError(GoogleSecOpsConnectorError):
    """Raised when the SecOps API returns a non-retryable error."""

    def __init__(self, message: str, status_code: int = 0, body: str = ""):
        """Initialize with message, HTTP status code, and optional response body."""
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class SentinelIngestionError(GoogleSecOpsConnectorError):
    """Raised when posting to Sentinel DCR fails."""
