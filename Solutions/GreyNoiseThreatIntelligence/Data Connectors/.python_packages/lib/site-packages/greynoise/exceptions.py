"""GreyNoise API client exceptions."""


class RequestFailure(Exception):
    """Exception to capture a failed request."""


class RateLimitError(RequestFailure):
    """API rate limit passed."""


class NotFound(Exception):
    """API rate limit passed."""
