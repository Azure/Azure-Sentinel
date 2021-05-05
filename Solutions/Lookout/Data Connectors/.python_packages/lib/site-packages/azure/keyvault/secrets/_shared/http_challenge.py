# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse  # type: ignore


class HttpChallenge(object):
    def __init__(self, request_uri, challenge, response_headers=None):
        """ Parses an HTTP WWW-Authentication Bearer challenge from a server. """
        self.source_authority = self._validate_request_uri(request_uri)
        self.source_uri = request_uri
        self._parameters = {}

        # get the scheme of the challenge and remove from the challenge string
        trimmed_challenge = self._validate_challenge(challenge)
        split_challenge = trimmed_challenge.split(" ", 1)
        self.scheme = split_challenge[0]
        trimmed_challenge = split_challenge[1]

        # split trimmed challenge into comma-separated name=value pairs. Values are expected
        # to be surrounded by quotes which are stripped here.
        for item in trimmed_challenge.split(","):
            # process name=value pairs
            comps = item.split("=")
            if len(comps) == 2:
                key = comps[0].strip(' "')
                value = comps[1].strip(' "')
                if key:
                    self._parameters[key] = value

        # minimum set of parameters
        if not self._parameters:
            raise ValueError("Invalid challenge parameters")

        # must specify authorization or authorization_uri
        if "authorization" not in self._parameters and "authorization_uri" not in self._parameters:
            raise ValueError("Invalid challenge parameters")

        # if the response headers were supplied
        if response_headers:
            # get the message signing key and message key encryption key from the headers
            self.server_signature_key = response_headers.get("x-ms-message-signing-key", None)
            self.server_encryption_key = response_headers.get("x-ms-message-encryption-key", None)

    def is_bearer_challenge(self):
        """ Tests whether the HttpChallenge a Bearer challenge.
        rtype: bool """
        if not self.scheme:
            return False

        return self.scheme.lower() == "bearer"

    def is_pop_challenge(self):
        """ Tests whether the HttpChallenge is a proof of possession challenge.
        rtype: bool """
        if not self.scheme:
            return False

        return self.scheme.lower() == "pop"

    def get_value(self, key):
        return self._parameters.get(key)

    def get_authorization_server(self):
        """ Returns the URI for the authorization server if present, otherwise empty string. """
        value = ""
        for key in ["authorization_uri", "authorization"]:
            value = self.get_value(key) or ""
            if value:
                break
        return value

    def get_resource(self):
        """ Returns the resource if present, otherwise empty string. """
        return self.get_value("resource") or ""

    def get_scope(self):
        """ Returns the scope if present, otherwise empty string. """
        return self.get_value("scope") or ""

    def supports_pop(self):
        """ Returns True if challenge supports pop token auth else False """
        return self._parameters.get("supportspop", "").lower() == "true"

    def supports_message_protection(self):
        """ Returns True if challenge vault supports message protection """
        return self.supports_pop() and self.server_encryption_key and self.server_signature_key

    # pylint:disable=no-self-use
    def _validate_challenge(self, challenge):
        """ Verifies that the challenge is a valid auth challenge and returns the key=value pairs. """
        if not challenge:
            raise ValueError("Challenge cannot be empty")

        return challenge.strip()

    # pylint:disable=no-self-use
    def _validate_request_uri(self, uri):
        """ Extracts the host authority from the given URI. """
        if not uri:
            raise ValueError("request_uri cannot be empty")

        uri = parse.urlparse(uri)
        if not uri.netloc:
            raise ValueError("request_uri must be an absolute URI")

        if uri.scheme.lower() not in ["http", "https"]:
            raise ValueError("request_uri must be HTTP or HTTPS")

        return uri.netloc
