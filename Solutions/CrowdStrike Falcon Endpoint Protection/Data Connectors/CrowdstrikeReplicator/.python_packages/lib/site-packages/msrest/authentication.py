# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import Optional, Dict

import requests
from requests.auth import HTTPBasicAuth
import requests_oauthlib as oauth


class Authentication(object):
    """Default, simple auth object.
    Doesn't actually add any auth headers.
    """

    header = "Authorization"

    def signed_session(self, session=None):
        # type: (Optional[requests.Session]) -> requests.Session
        """Create requests session with any required auth headers applied.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        return session or requests.Session()


class BasicAuthentication(Authentication):
    """Implementation of Basic Authentication.

    :param str username: Authentication username.
    :param str password: Authentication password.
    """

    def __init__(self, username, password):
        # type: (str, str) -> None
        self.scheme = 'Basic'
        self.username = username
        self.password = password

    def signed_session(self, session=None):
        # type: (Optional[requests.Session]) -> requests.Session
        """Create requests session with any required auth headers
        applied.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        session = super(BasicAuthentication, self).signed_session(session)
        session.auth = HTTPBasicAuth(self.username, self.password)
        return session


class BasicTokenAuthentication(Authentication):
    """Simple Token Authentication.
    Does not adhere to OAuth, simply adds provided token as a header.

    :param dict[str,str] token: Authentication token, must have 'access_token' key.
    """

    def __init__(self, token):
        # type: (Dict[str, str]) -> None
        self.scheme = 'Bearer'
        self.token = token

    def set_token(self):
        # type: () -> None
        """Should be used to define the self.token attribute.

        In this implementation, does nothing since the token is statically provided
        at creation.
        """
        pass

    def signed_session(self, session=None):
        # type: (Optional[requests.Session]) -> requests.Session
        """Create requests session with any required auth headers
        applied.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        session = super(BasicTokenAuthentication, self).signed_session(session)
        header = "{} {}".format(self.scheme, self.token['access_token'])
        session.headers['Authorization'] = header
        return session


class OAuthTokenAuthentication(BasicTokenAuthentication):
    """OAuth Token Authentication.

    Requires that supplied token contains an expires_in field.

    :param str client_id: Account Client ID.
    :param dict[str,str] token: OAuth2 token.
    """

    def __init__(self, client_id, token):
        # type: (str, Dict[str, str]) -> None
        super(OAuthTokenAuthentication, self).__init__(token)
        self.id = client_id
        self.store_key = self.id

    def construct_auth(self):
        # type: () -> str
        """Format token header.

        :rtype: str
        """
        return "{} {}".format(self.scheme, self.token)

    def refresh_session(self, session=None):
        # type: (Optional[requests.Session]) -> requests.Session
        """Return updated session if token has expired, attempts to
        refresh using refresh token.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        return self.signed_session(session)

    def signed_session(self, session=None):
        # type: (Optional[requests.Session]) -> requests.Session
        """Create requests session with any required auth headers applied.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        session = session or requests.Session()  # Don't call super on purpose, let's "auth" manage the headers.
        session.auth = oauth.OAuth2(self.id, token=self.token)
        return session


class KerberosAuthentication(Authentication):
    """Kerberos Authentication
    Kerberos Single Sign On (SSO); requires requests_kerberos is installed.

    :param mutual_authentication: whether to require mutual authentication. Use values from requests_kerberos import REQUIRED, OPTIONAL, or DISABLED
    """
    def __init__(self, mutual_authentication=None):
        super(KerberosAuthentication, self).__init__()
        self.mutual_authentication = mutual_authentication

    def signed_session(self, session=None):
        """Create requests session with Negotiate (SPNEGO) headers applied.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        session = super(KerberosAuthentication, self).signed_session(session)
        try:
            from requests_kerberos import HTTPKerberosAuth
        except ImportError:
            raise ImportError("In order to use KerberosAuthentication please do 'pip install requests_kerberos' first")
        if self.mutual_authentication:
            session.auth = HTTPKerberosAuth(mutual_authentication=self.mutual_authentication)
        else:
            session.auth = HTTPKerberosAuth()
        return session


class ApiKeyCredentials(Authentication):
    """Represent the ApiKey feature of Swagger.

    Dict should be dict[str,str] to be accepted by requests.

    :param dict[str,str] in_headers: Headers part of the ApiKey
    :param dict[str,str] in_query: ApiKey in the query as parameters
    """
    def __init__(self, in_headers=None, in_query=None):
        # type: (Optional[Dict[str, str]], Optional[Dict[str, str]]) -> None
        super(ApiKeyCredentials, self).__init__()
        if in_headers is None:
            in_headers = {}
        if in_query is None:
            in_query = {}

        if not in_headers and not in_query:
            raise ValueError("You need to define in_headers or in_query")

        self.in_headers = in_headers
        self.in_query = in_query

    def signed_session(self, session=None):
        # type: (Optional[requests.Session]) -> requests.Session
        """Create requests session with ApiKey.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        session = super(ApiKeyCredentials, self).signed_session(session)
        session.headers.update(self.in_headers)
        try:
            # params is actually Union[bytes, MutableMapping[Text, Text]]
            session.params.update(self.in_query)  # type: ignore
        except AttributeError:  # requests.params can be bytes
            raise ValueError("session.params must be a dict to be used in ApiKeyCredentials")
        return session


class CognitiveServicesCredentials(ApiKeyCredentials):
    """Cognitive Services authentication.

    :param str subscription_key: The CS subscription key
    """

    _subscription_key_header = 'Ocp-Apim-Subscription-Key'

    def __init__(self, subscription_key):
        # type: (str) -> None
        if not subscription_key:
            raise ValueError("Subscription key cannot be None")
        super(CognitiveServicesCredentials, self).__init__(
            in_headers={
                self._subscription_key_header: subscription_key,
                'X-BingApis-SDK-Client': 'Python-SDK'
            }
        )


class TopicCredentials(ApiKeyCredentials):
    """Event Grid authentication.

    :param str topic_key: The Event Grid topic key
    """

    _topic_key_header = 'aeg-sas-key'

    def __init__(self, topic_key):
        # type: (str) -> None
        if not topic_key:
            raise ValueError("Topic key cannot be None")
        super(TopicCredentials, self).__init__(
            in_headers={
                self._topic_key_header: topic_key,
            }
        )


class DomainCredentials(ApiKeyCredentials):
    """Event Grid domain authentication.

    :param str domain_key: The Event Grid domain key
    """

    _domain_key_header = 'aeg-sas-key'

    def __init__(self, domain_key):
        # type: (str) -> None
        if not domain_key:
            raise ValueError("Domain key cannot be None")
        super(DomainCredentials, self).__init__(
            in_headers={
                self._domain_key_header: domain_key,
            }
        )
