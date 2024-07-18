class MimecastResponseCodes:

    success = 200
    """The request was processed and executed. This does not mean that the requested action was successful.
     Function-level success or failure is indicated in the response body content."""

    bad_request = 400
    """The request cannot be processed because it is either malformed or not correct."""

    unauthorized = 401
    """Authorization information is either missing, incomplete or incorrect."""

    forbidden = 403
    """Access is denied to the requested resource. The user may not have enough permission to perform the action."""

    not_found = 404
    """The requested resource does not exist."""

    conflict = 409
    """The current status of the relying data does not match what is defined in the request."""

    binding_expired = 418
    """The TTL of the access key and secret key issued on successful login has lapsed and the binding should be
    refreshed as described in the Authentication guide."""

    quota_exceeded = 429
    """The number of requests sent to the given resource has exceeded the rate limiting policy applied to the resource
    for a given time period. Rate limiting is applied differently per resource and is subject to change."""

    internal_server_error = 500
    """The request was not processed successfully or an issue has occurred in the Mimecast platform."""
