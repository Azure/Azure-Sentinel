import functools
import json
import time
try:  # Python 2
    from urlparse import urljoin
except:  # Python 3
    from urllib.parse import urljoin
import logging
import sys
import warnings
from threading import Lock

import requests

from .oauth2cli import Client, JwtAssertionCreator
from .authority import Authority
from .mex import send_request as mex_send_request
from .wstrust_request import send_request as wst_send_request
from .wstrust_response import *
from .token_cache import TokenCache
import msal.telemetry


# The __init__.py will import this. Not the other way around.
__version__ = "1.11.0"

logger = logging.getLogger(__name__)

def decorate_scope(
        scopes, client_id,
        reserved_scope=frozenset(['openid', 'profile', 'offline_access'])):
    if not isinstance(scopes, (list, set, tuple)):
        raise ValueError("The input scopes should be a list, tuple, or set")
    scope_set = set(scopes)  # Input scopes is typically a list. Copy it to a set.
    if scope_set & reserved_scope:
        # These scopes are reserved for the API to provide good experience.
        # We could make the developer pass these and then if they do they will
        # come back asking why they don't see refresh token or user information.
        raise ValueError(
            "API does not accept {} value as user-provided scopes".format(
                reserved_scope))
    if client_id in scope_set:
        if len(scope_set) > 1:
            # We make developers pass their client id, so that they can express
            # the intent that they want the token for themselves (their own
            # app).
            # If we do not restrict them to passing only client id then they
            # could write code where they expect an id token but end up getting
            # access_token.
            raise ValueError("Client Id can only be provided as a single scope")
        decorated = set(reserved_scope)  # Make a writable copy
    else:
        decorated = scope_set | reserved_scope
    return list(decorated)


def extract_certs(public_cert_content):
    # Parses raw public certificate file contents and returns a list of strings
    # Usage: headers = {"x5c": extract_certs(open("my_cert.pem").read())}
    public_certificates = re.findall(
        r'-----BEGIN CERTIFICATE-----(?P<cert_value>[^-]+)-----END CERTIFICATE-----',
        public_cert_content, re.I)
    if public_certificates:
        return [cert.strip() for cert in public_certificates]
    # The public cert tags are not found in the input,
    # let's make best effort to exclude a private key pem file.
    if "PRIVATE KEY" in public_cert_content:
        raise ValueError(
            "We expect your public key but detect a private key instead")
    return [public_cert_content.strip()]


def _merge_claims_challenge_and_capabilities(capabilities, claims_challenge):
    # Represent capabilities as {"access_token": {"xms_cc": {"values": capabilities}}}
    # and then merge/add it into incoming claims
    if not capabilities:
        return claims_challenge
    claims_dict = json.loads(claims_challenge) if claims_challenge else {}
    for key in ["access_token"]:  # We could add "id_token" if we'd decide to
        claims_dict.setdefault(key, {}).update(xms_cc={"values": capabilities})
    return json.dumps(claims_dict)


def _str2bytes(raw):
    # A conversion based on duck-typing rather than six.text_type
    try:
        return raw.encode(encoding="utf-8")
    except:
        return raw


def _clean_up(result):
    if isinstance(result, dict):
        result.pop("refresh_in", None)  # MSAL handled refresh_in, customers need not
    return result


class ClientApplication(object):

    ACQUIRE_TOKEN_SILENT_ID = "84"
    ACQUIRE_TOKEN_BY_REFRESH_TOKEN = "85"
    ACQUIRE_TOKEN_BY_USERNAME_PASSWORD_ID = "301"
    ACQUIRE_TOKEN_ON_BEHALF_OF_ID = "523"
    ACQUIRE_TOKEN_BY_DEVICE_FLOW_ID = "622"
    ACQUIRE_TOKEN_FOR_CLIENT_ID = "730"
    ACQUIRE_TOKEN_BY_AUTHORIZATION_CODE_ID = "832"
    ACQUIRE_TOKEN_INTERACTIVE = "169"
    GET_ACCOUNTS_ID = "902"
    REMOVE_ACCOUNT_ID = "903"

    def __init__(
            self, client_id,
            client_credential=None, authority=None, validate_authority=True,
            token_cache=None,
            http_client=None,
            verify=True, proxies=None, timeout=None,
            client_claims=None, app_name=None, app_version=None,
            client_capabilities=None):
        """Create an instance of application.

        :param str client_id: Your app has a client_id after you register it on AAD.

        :param Union[str, dict] client_credential:
            For :class:`PublicClientApplication`, you simply use `None` here.
            For :class:`ConfidentialClientApplication`,
            it can be a string containing client secret,
            or an X509 certificate container in this form::

                {
                    "private_key": "...-----BEGIN PRIVATE KEY-----...",
                    "thumbprint": "A1B2C3D4E5F6...",
                    "public_certificate": "...-----BEGIN CERTIFICATE-----... (Optional. See below.)",
                    "passphrase": "Passphrase if the private_key is encrypted (Optional. Added in version 1.6.0)",
                }

            *Added in version 0.5.0*:
            public_certificate (optional) is public key certificate
            which will be sent through 'x5c' JWT header only for
            subject name and issuer authentication to support cert auto rolls.

            Per `specs <https://tools.ietf.org/html/rfc7515#section-4.1.6>`_,
            "the certificate containing
            the public key corresponding to the key used to digitally sign the
            JWS MUST be the first certificate.  This MAY be followed by
            additional certificates, with each subsequent certificate being the
            one used to certify the previous one."
            However, your certificate's issuer may use a different order.
            So, if your attempt ends up with an error AADSTS700027 -
            "The provided signature value did not match the expected signature value",
            you may try use only the leaf cert (in PEM/str format) instead.

        :param dict client_claims:
            *Added in version 0.5.0*:
            It is a dictionary of extra claims that would be signed by
            by this :class:`ConfidentialClientApplication` 's private key.
            For example, you can use {"client_ip": "x.x.x.x"}.
            You may also override any of the following default claims::

                {
                    "aud": the_token_endpoint,
                    "iss": self.client_id,
                    "sub": same_as_issuer,
                    "exp": now + 10_min,
                    "iat": now,
                    "jti": a_random_uuid
                }

        :param str authority:
            A URL that identifies a token authority. It should be of the format
            https://login.microsoftonline.com/your_tenant
            By default, we will use https://login.microsoftonline.com/common
        :param bool validate_authority: (optional) Turns authority validation
            on or off. This parameter default to true.
        :param TokenCache cache:
            Sets the token cache used by this ClientApplication instance.
            By default, an in-memory cache will be created and used.
        :param http_client: (optional)
            Your implementation of abstract class HttpClient <msal.oauth2cli.http.http_client>
            Defaults to a requests session instance.
            Since MSAL 1.11.0, the default session would be configured
            to attempt one retry on connection error.
            If you are providing your own http_client,
            it will be your http_client's duty to decide whether to perform retry.

        :param verify: (optional)
            It will be passed to the
            `verify parameter in the underlying requests library
            <http://docs.python-requests.org/en/v2.9.1/user/advanced/#ssl-cert-verification>`_
            This does not apply if you have chosen to pass your own Http client
        :param proxies: (optional)
            It will be passed to the
            `proxies parameter in the underlying requests library
            <http://docs.python-requests.org/en/v2.9.1/user/advanced/#proxies>`_
            This does not apply if you have chosen to pass your own Http client
        :param timeout: (optional)
            It will be passed to the
            `timeout parameter in the underlying requests library
            <http://docs.python-requests.org/en/v2.9.1/user/advanced/#timeouts>`_
            This does not apply if you have chosen to pass your own Http client
        :param app_name: (optional)
            You can provide your application name for Microsoft telemetry purposes.
            Default value is None, means it will not be passed to Microsoft.
        :param app_version: (optional)
            You can provide your application version for Microsoft telemetry purposes.
            Default value is None, means it will not be passed to Microsoft.
        :param list[str] client_capabilities: (optional)
            Allows configuration of one or more client capabilities, e.g. ["CP1"].

            Client capability is meant to inform the Microsoft identity platform
            (STS) what this client is capable for,
            so STS can decide to turn on certain features.
            For example, if client is capable to handle *claims challenge*,
            STS can then issue CAE access tokens to resources
            knowing when the resource emits *claims challenge*
            the client will be capable to handle.

            Implementation details:
            Client capability is implemented using "claims" parameter on the wire,
            for now.
            MSAL will combine them into
            `claims parameter <https://openid.net/specs/openid-connect-core-1_0-final.html#ClaimsParameter`_
            which you will later provide via one of the acquire-token request.
        """
        self.client_id = client_id
        self.client_credential = client_credential
        self.client_claims = client_claims
        self._client_capabilities = client_capabilities
        if http_client:
            self.http_client = http_client
        else:
            self.http_client = requests.Session()
            self.http_client.verify = verify
            self.http_client.proxies = proxies
            # Requests, does not support session - wide timeout
            # But you can patch that (https://github.com/psf/requests/issues/3341):
            self.http_client.request = functools.partial(
                self.http_client.request, timeout=timeout)

            # Enable a minimal retry. Better than nothing.
            # https://github.com/psf/requests/blob/v2.25.1/requests/adapters.py#L94-L108
            a = requests.adapters.HTTPAdapter(max_retries=1)
            self.http_client.mount("http://", a)
            self.http_client.mount("https://", a)

        self.app_name = app_name
        self.app_version = app_version
        self.authority = Authority(
                authority or "https://login.microsoftonline.com/common/",
                self.http_client, validate_authority=validate_authority)
            # Here the self.authority is not the same type as authority in input
        self.token_cache = token_cache or TokenCache()
        self.client = self._build_client(client_credential, self.authority)
        self.authority_groups = None
        self._telemetry_buffer = {}
        self._telemetry_lock = Lock()

    def _build_telemetry_context(
            self, api_id, correlation_id=None, refresh_reason=None):
        return msal.telemetry._TelemetryContext(
            self._telemetry_buffer, self._telemetry_lock, api_id,
            correlation_id=correlation_id, refresh_reason=refresh_reason)

    def _build_client(self, client_credential, authority):
        client_assertion = None
        client_assertion_type = None
        default_headers = {
            "x-client-sku": "MSAL.Python", "x-client-ver": __version__,
            "x-client-os": sys.platform,
            "x-client-cpu": "x64" if sys.maxsize > 2 ** 32 else "x86",
        }
        if self.app_name:
            default_headers['x-app-name'] = self.app_name
        if self.app_version:
            default_headers['x-app-ver'] = self.app_version
        default_body = {"client_info": 1}
        if isinstance(client_credential, dict):
            assert ("private_key" in client_credential
                    and "thumbprint" in client_credential)
            headers = {}
            if 'public_certificate' in client_credential:
                headers["x5c"] = extract_certs(client_credential['public_certificate'])
            if not client_credential.get("passphrase"):
                unencrypted_private_key = client_credential['private_key']
            else:
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.backends import default_backend
                unencrypted_private_key = serialization.load_pem_private_key(
                    _str2bytes(client_credential["private_key"]),
                    _str2bytes(client_credential["passphrase"]),
                    backend=default_backend(),  # It was a required param until 2020
                    )
            assertion = JwtAssertionCreator(
                unencrypted_private_key, algorithm="RS256",
                sha1_thumbprint=client_credential.get("thumbprint"), headers=headers)
            client_assertion = assertion.create_regenerative_assertion(
                audience=authority.token_endpoint, issuer=self.client_id,
                additional_claims=self.client_claims or {})
            client_assertion_type = Client.CLIENT_ASSERTION_TYPE_JWT
        else:
            default_body['client_secret'] = client_credential
        server_configuration = {
            "authorization_endpoint": authority.authorization_endpoint,
            "token_endpoint": authority.token_endpoint,
            "device_authorization_endpoint":
                authority.device_authorization_endpoint or
                urljoin(authority.token_endpoint, "devicecode"),
            }
        return Client(
            server_configuration,
            self.client_id,
            http_client=self.http_client,
            default_headers=default_headers,
            default_body=default_body,
            client_assertion=client_assertion,
            client_assertion_type=client_assertion_type,
            on_obtaining_tokens=lambda event: self.token_cache.add(dict(
                event, environment=authority.instance)),
            on_removing_rt=self.token_cache.remove_rt,
            on_updating_rt=self.token_cache.update_rt)

    def initiate_auth_code_flow(
            self,
            scopes,  # type: list[str]
            redirect_uri=None,
            state=None,  # Recommended by OAuth2 for CSRF protection
            prompt=None,
            login_hint=None,  # type: Optional[str]
            domain_hint=None,  # type: Optional[str]
            claims_challenge=None,
            ):
        """Initiate an auth code flow.

        Later when the response reaches your redirect_uri,
        you can use :func:`~acquire_token_by_auth_code_flow()`
        to complete the authentication/authorization.

        :param list scopes:
            It is a list of case-sensitive strings.
        :param str redirect_uri:
            Optional. If not specified, server will use the pre-registered one.
        :param str state:
            An opaque value used by the client to
            maintain state between the request and callback.
            If absent, this library will automatically generate one internally.
        :param str prompt:
            By default, no prompt value will be sent, not even "none".
            You will have to specify a value explicitly.
            Its valid values are defined in Open ID Connect specs
            https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        :param str login_hint:
            Optional. Identifier of the user. Generally a User Principal Name (UPN).
        :param domain_hint:
            Can be one of "consumers" or "organizations" or your tenant domain "contoso.com".
            If included, it will skip the email-based discovery process that user goes
            through on the sign-in page, leading to a slightly more streamlined user experience.
            More information on possible values
            `here <https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an-authorization-code>`_ and
            `here <https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-oapx/86fb452d-e34a-494e-ac61-e526e263b6d8>`_.

        :return:
            The auth code flow. It is a dict in this form::

                {
                    "auth_uri": "https://...",  // Guide user to visit this
                    "state": "...",  // You may choose to verify it by yourself,
                                     // or just let acquire_token_by_auth_code_flow()
                                     // do that for you.
                    "...": "...",  // Everything else are reserved and internal
                }

            The caller is expected to::

            1. somehow store this content, typically inside the current session,
            2. guide the end user (i.e. resource owner) to visit that auth_uri,
            3. and then relay this dict and subsequent auth response to
               :func:`~acquire_token_by_auth_code_flow()`.
        """
        client = Client(
            {"authorization_endpoint": self.authority.authorization_endpoint},
            self.client_id,
            http_client=self.http_client)
        flow = client.initiate_auth_code_flow(
            redirect_uri=redirect_uri, state=state, login_hint=login_hint,
            prompt=prompt,
            scope=decorate_scope(scopes, self.client_id),
            domain_hint=domain_hint,
            claims=_merge_claims_challenge_and_capabilities(
                self._client_capabilities, claims_challenge),
            )
        flow["claims_challenge"] = claims_challenge
        return flow

    def get_authorization_request_url(
            self,
            scopes,  # type: list[str]
            login_hint=None,  # type: Optional[str]
            state=None,  # Recommended by OAuth2 for CSRF protection
            redirect_uri=None,
            response_type="code",  # Could be "token" if you use Implicit Grant
            prompt=None,
            nonce=None,
            domain_hint=None,  # type: Optional[str]
            claims_challenge=None,
            **kwargs):
        """Constructs a URL for you to start a Authorization Code Grant.

        :param list[str] scopes: (Required)
            Scopes requested to access a protected API (a resource).
        :param str state: Recommended by OAuth2 for CSRF protection.
        :param str login_hint:
            Identifier of the user. Generally a User Principal Name (UPN).
        :param str redirect_uri:
            Address to return to upon receiving a response from the authority.
        :param str response_type:
            Default value is "code" for an OAuth2 Authorization Code grant.

            You could use other content such as "id_token" or "token",
            which would trigger an Implicit Grant, but that is
            `not recommended <https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-implicit-grant-flow#is-the-implicit-grant-suitable-for-my-app>`_.

        :param str prompt:
            By default, no prompt value will be sent, not even "none".
            You will have to specify a value explicitly.
            Its valid values are defined in Open ID Connect specs
            https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        :param nonce:
            A cryptographically random value used to mitigate replay attacks. See also
            `OIDC specs <https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest>`_.
        :param domain_hint:
            Can be one of "consumers" or "organizations" or your tenant domain "contoso.com".
            If included, it will skip the email-based discovery process that user goes
            through on the sign-in page, leading to a slightly more streamlined user experience.
            More information on possible values
            `here <https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an-authorization-code>`_ and
            `here <https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-oapx/86fb452d-e34a-494e-ac61-e526e263b6d8>`_.
        :param claims_challenge:
             The claims_challenge parameter requests specific claims requested by the resource provider
             in the form of a claims_challenge directive in the www-authenticate header to be
             returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
             It is a string of a JSON object which contains lists of claims being requested from these locations.

        :return: The authorization url as a string.
        """
        authority = kwargs.pop("authority", None)  # Historically we support this
        if authority:
            warnings.warn(
                "We haven't decided if this method will accept authority parameter")
        # The previous implementation is, it will use self.authority by default.
        # Multi-tenant app can use new authority on demand
        the_authority = Authority(
            authority,
            self.http_client
            ) if authority else self.authority

        client = Client(
            {"authorization_endpoint": the_authority.authorization_endpoint},
            self.client_id,
            http_client=self.http_client)
        warnings.warn(
            "Change your get_authorization_request_url() "
            "to initiate_auth_code_flow()", DeprecationWarning)
        with warnings.catch_warnings(record=True):
            return client.build_auth_request_uri(
                response_type=response_type,
                redirect_uri=redirect_uri, state=state, login_hint=login_hint,
                prompt=prompt,
                scope=decorate_scope(scopes, self.client_id),
                nonce=nonce,
                domain_hint=domain_hint,
                claims=_merge_claims_challenge_and_capabilities(
                    self._client_capabilities, claims_challenge),
                )

    def acquire_token_by_auth_code_flow(
            self, auth_code_flow, auth_response, scopes=None, **kwargs):
        """Validate the auth response being redirected back, and obtain tokens.

        It automatically provides nonce protection.

        :param dict auth_code_flow:
            The same dict returned by :func:`~initiate_auth_code_flow()`.
        :param dict auth_response:
            A dict of the query string received from auth server.
        :param list[str] scopes:
            Scopes requested to access a protected API (a resource).

            Most of the time, you can leave it empty.

            If you requested user consent for multiple resources, here you will
            need to provide a subset of what you required in
            :func:`~initiate_auth_code_flow()`.

            OAuth2 was designed mostly for singleton services,
            where tokens are always meant for the same resource and the only
            changes are in the scopes.
            In AAD, tokens can be issued for multiple 3rd party resources.
            You can ask authorization code for multiple resources,
            but when you redeem it, the token is for only one intended
            recipient, called audience.
            So the developer need to specify a scope so that we can restrict the
            token to be issued for the corresponding audience.

        :return:
            * A dict containing "access_token" and/or "id_token", among others,
              depends on what scope was used.
              (See https://tools.ietf.org/html/rfc6749#section-5.1)
            * A dict containing "error", optionally "error_description", "error_uri".
              (It is either `this <https://tools.ietf.org/html/rfc6749#section-4.1.2.1>`_
              or `that <https://tools.ietf.org/html/rfc6749#section-5.2>`_)
            * Most client-side data error would result in ValueError exception.
              So the usage pattern could be without any protocol details::

                def authorize():  # A controller in a web app
                    try:
                        result = msal_app.acquire_token_by_auth_code_flow(
                            session.get("flow", {}), request.args)
                        if "error" in result:
                            return render_template("error.html", result)
                        use(result)  # Token(s) are available in result and cache
                    except ValueError:  # Usually caused by CSRF
                        pass  # Simply ignore them
                    return redirect(url_for("index"))
        """
        self._validate_ssh_cert_input_data(kwargs.get("data", {}))
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_BY_AUTHORIZATION_CODE_ID)
        response =_clean_up(self.client.obtain_token_by_auth_code_flow(
            auth_code_flow,
            auth_response,
            scope=decorate_scope(scopes, self.client_id) if scopes else None,
            headers=telemetry_context.generate_headers(),
            data=dict(
                kwargs.pop("data", {}),
                claims=_merge_claims_challenge_and_capabilities(
                    self._client_capabilities,
                    auth_code_flow.pop("claims_challenge", None))),
            **kwargs))
        telemetry_context.update_telemetry(response)
        return response

    def acquire_token_by_authorization_code(
            self,
            code,
            scopes,  # Syntactically required. STS accepts empty value though.
            redirect_uri=None,
                # REQUIRED, if the "redirect_uri" parameter was included in the
                # authorization request as described in Section 4.1.1, and their
                # values MUST be identical.
            nonce=None,
            claims_challenge=None,
            **kwargs):
        """The second half of the Authorization Code Grant.

        :param code: The authorization code returned from Authorization Server.
        :param list[str] scopes: (Required)
            Scopes requested to access a protected API (a resource).

            If you requested user consent for multiple resources, here you will
            typically want to provide a subset of what you required in AuthCode.

            OAuth2 was designed mostly for singleton services,
            where tokens are always meant for the same resource and the only
            changes are in the scopes.
            In AAD, tokens can be issued for multiple 3rd party resources.
            You can ask authorization code for multiple resources,
            but when you redeem it, the token is for only one intended
            recipient, called audience.
            So the developer need to specify a scope so that we can restrict the
            token to be issued for the corresponding audience.

        :param nonce:
            If you provided a nonce when calling :func:`get_authorization_request_url`,
            same nonce should also be provided here, so that we'll validate it.
            An exception will be raised if the nonce in id token mismatches.

        :param claims_challenge:
            The claims_challenge parameter requests specific claims requested by the resource provider
            in the form of a claims_challenge directive in the www-authenticate header to be
            returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
            It is a string of a JSON object which contains lists of claims being requested from these locations.

        :return: A dict representing the json response from AAD:

            - A successful response would contain "access_token" key,
            - an error response would contain "error" and usually "error_description".
        """
        # If scope is absent on the wire, STS will give you a token associated
        # to the FIRST scope sent during the authorization request.
        # So in theory, you can omit scope here when you were working with only
        # one scope. But, MSAL decorates your scope anyway, so they are never
        # really empty.
        assert isinstance(scopes, list), "Invalid parameter type"
        self._validate_ssh_cert_input_data(kwargs.get("data", {}))
        warnings.warn(
            "Change your acquire_token_by_authorization_code() "
            "to acquire_token_by_auth_code_flow()", DeprecationWarning)
        with warnings.catch_warnings(record=True):
            telemetry_context = self._build_telemetry_context(
                self.ACQUIRE_TOKEN_BY_AUTHORIZATION_CODE_ID)
            response = _clean_up(self.client.obtain_token_by_authorization_code(
                code, redirect_uri=redirect_uri,
                scope=decorate_scope(scopes, self.client_id),
                headers=telemetry_context.generate_headers(),
                data=dict(
                    kwargs.pop("data", {}),
                    claims=_merge_claims_challenge_and_capabilities(
                        self._client_capabilities, claims_challenge)),
                nonce=nonce,
                **kwargs))
            telemetry_context.update_telemetry(response)
            return response

    def get_accounts(self, username=None):
        """Get a list of accounts which previously signed in, i.e. exists in cache.

        An account can later be used in :func:`~acquire_token_silent`
        to find its tokens.

        :param username:
            Filter accounts with this username only. Case insensitive.
        :return: A list of account objects.
            Each account is a dict. For now, we only document its "username" field.
            Your app can choose to display those information to end user,
            and allow user to choose one of his/her accounts to proceed.
        """
        accounts = self._find_msal_accounts(environment=self.authority.instance)
        if not accounts:  # Now try other aliases of this authority instance
            for alias in self._get_authority_aliases(self.authority.instance):
                accounts = self._find_msal_accounts(environment=alias)
                if accounts:
                    break
        if username:
            # Federated account["username"] from AAD could contain mixed case
            lowercase_username = username.lower()
            accounts = [a for a in accounts
                if a["username"].lower() == lowercase_username]
        # Does not further filter by existing RTs here. It probably won't matter.
        # Because in most cases Accounts and RTs co-exist.
        # Even in the rare case when an RT is revoked and then removed,
        # acquire_token_silent() would then yield no result,
        # apps would fall back to other acquire methods. This is the standard pattern.
        return accounts

    def _find_msal_accounts(self, environment):
        return [a for a in self.token_cache.find(
            TokenCache.CredentialType.ACCOUNT, query={"environment": environment})
            if a["authority_type"] in (
                TokenCache.AuthorityType.ADFS, TokenCache.AuthorityType.MSSTS)]

    def _get_authority_aliases(self, instance):
        if not self.authority_groups:
            resp = self.http_client.get(
                "https://login.microsoftonline.com/common/discovery/instance?api-version=1.1&authorization_endpoint=https://login.microsoftonline.com/common/oauth2/authorize",
                headers={'Accept': 'application/json'})
            resp.raise_for_status()
            self.authority_groups = [
                set(group['aliases']) for group in json.loads(resp.text)['metadata']]
        for group in self.authority_groups:
            if instance in group:
                return [alias for alias in group if alias != instance]
        return []

    def remove_account(self, account):
        """Sign me out and forget me from token cache"""
        self._forget_me(account)

    def _sign_out(self, home_account):
        # Remove all relevant RTs and ATs from token cache
        owned_by_home_account = {
            "environment": home_account["environment"],
            "home_account_id": home_account["home_account_id"],}  # realm-independent
        app_metadata = self._get_app_metadata(home_account["environment"])
        # Remove RTs/FRTs, and they are realm-independent
        for rt in [rt for rt in self.token_cache.find(
                TokenCache.CredentialType.REFRESH_TOKEN, query=owned_by_home_account)
                # Do RT's app ownership check as a precaution, in case family apps
                # and 3rd-party apps share same token cache, although they should not.
                if rt["client_id"] == self.client_id or (
                    app_metadata.get("family_id")  # Now let's settle family business
                    and rt.get("family_id") == app_metadata["family_id"])
                ]:
            self.token_cache.remove_rt(rt)
        for at in self.token_cache.find(  # Remove ATs
                # Regardless of realm, b/c we've removed realm-independent RTs anyway
                TokenCache.CredentialType.ACCESS_TOKEN, query=owned_by_home_account):
            # To avoid the complexity of locating sibling family app's AT,
            # we skip AT's app ownership check.
            # It means ATs for other apps will also be removed, it is OK because:
            # * non-family apps are not supposed to share token cache to begin with;
            # * Even if it happens, we keep other app's RT already, so SSO still works
            self.token_cache.remove_at(at)

    def _forget_me(self, home_account):
        # It implies signout, and then also remove all relevant accounts and IDTs
        self._sign_out(home_account)
        owned_by_home_account = {
            "environment": home_account["environment"],
            "home_account_id": home_account["home_account_id"],}  # realm-independent
        for idt in self.token_cache.find(  # Remove IDTs, regardless of realm
                TokenCache.CredentialType.ID_TOKEN, query=owned_by_home_account):
            self.token_cache.remove_idt(idt)
        for a in self.token_cache.find(  # Remove Accounts, regardless of realm
                TokenCache.CredentialType.ACCOUNT, query=owned_by_home_account):
            self.token_cache.remove_account(a)

    def acquire_token_silent(
            self,
            scopes,  # type: List[str]
            account,  # type: Optional[Account]
            authority=None,  # See get_authorization_request_url()
            force_refresh=False,  # type: Optional[boolean]
            claims_challenge=None,
            **kwargs):
        """Acquire an access token for given account, without user interaction.

        It is done either by finding a valid access token from cache,
        or by finding a valid refresh token from cache and then automatically
        use it to redeem a new access token.

        This method will combine the cache empty and refresh error
        into one return value, `None`.
        If your app does not care about the exact token refresh error during
        token cache look-up, then this method is easier and recommended.

        Internally, this method calls :func:`~acquire_token_silent_with_error`.

        :param claims_challenge:
            The claims_challenge parameter requests specific claims requested by the resource provider
            in the form of a claims_challenge directive in the www-authenticate header to be
            returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
            It is a string of a JSON object which contains lists of claims being requested from these locations.

        :return:
            - A dict containing no "error" key,
              and typically contains an "access_token" key,
              if cache lookup succeeded.
            - None when cache lookup does not yield a token.
        """
        result = self.acquire_token_silent_with_error(
            scopes, account, authority=authority, force_refresh=force_refresh,
            claims_challenge=claims_challenge, **kwargs)
        return result if result and "error" not in result else None

    def acquire_token_silent_with_error(
            self,
            scopes,  # type: List[str]
            account,  # type: Optional[Account]
            authority=None,  # See get_authorization_request_url()
            force_refresh=False,  # type: Optional[boolean]
            claims_challenge=None,
            **kwargs):
        """Acquire an access token for given account, without user interaction.

        It is done either by finding a valid access token from cache,
        or by finding a valid refresh token from cache and then automatically
        use it to redeem a new access token.

        This method will differentiate cache empty from token refresh error.
        If your app cares the exact token refresh error during
        token cache look-up, then this method is suitable.
        Otherwise, the other method :func:`~acquire_token_silent` is recommended.

        :param list[str] scopes: (Required)
            Scopes requested to access a protected API (a resource).
        :param account:
            one of the account object returned by :func:`~get_accounts`,
            or use None when you want to find an access token for this client.
        :param force_refresh:
            If True, it will skip Access Token look-up,
            and try to find a Refresh Token to obtain a new Access Token.
        :param claims_challenge:
            The claims_challenge parameter requests specific claims requested by the resource provider
            in the form of a claims_challenge directive in the www-authenticate header to be
            returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
            It is a string of a JSON object which contains lists of claims being requested from these locations.
        :return:
            - A dict containing no "error" key,
              and typically contains an "access_token" key,
              if cache lookup succeeded.
            - None when there is simply no token in the cache.
            - A dict containing an "error" key, when token refresh failed.
        """
        assert isinstance(scopes, list), "Invalid parameter type"
        self._validate_ssh_cert_input_data(kwargs.get("data", {}))
        correlation_id = msal.telemetry._get_new_correlation_id()
        if authority:
            warnings.warn("We haven't decided how/if this method will accept authority parameter")
        # the_authority = Authority(
        #     authority,
        #     self.http_client,
        #     ) if authority else self.authority
        result = self._acquire_token_silent_from_cache_and_possibly_refresh_it(
            scopes, account, self.authority, force_refresh=force_refresh,
            claims_challenge=claims_challenge,
            correlation_id=correlation_id,
            **kwargs)
        if result and "error" not in result:
            return result
        final_result = result
        for alias in self._get_authority_aliases(self.authority.instance):
            if not self.token_cache.find(
                    self.token_cache.CredentialType.REFRESH_TOKEN,
                    # target=scopes,  # MUST NOT filter by scopes, because:
                        # 1. AAD RTs are scope-independent;
                        # 2. therefore target is optional per schema;
                    query={"environment": alias}):
                # Skip heavy weight logic when RT for this alias doesn't exist
                continue
            the_authority = Authority(
                "https://" + alias + "/" + self.authority.tenant,
                self.http_client,
                validate_authority=False)
            result = self._acquire_token_silent_from_cache_and_possibly_refresh_it(
                scopes, account, the_authority, force_refresh=force_refresh,
                claims_challenge=claims_challenge,
                correlation_id=correlation_id,
                **kwargs)
            if result:
                if "error" not in result:
                    return result
                final_result = result
        if final_result and final_result.get("suberror"):
            final_result["classification"] = {  # Suppress these suberrors, per #57
                "bad_token": "",
                "token_expired": "",
                "protection_policy_required": "",
                "client_mismatch": "",
                "device_authentication_failed": "",
                }.get(final_result["suberror"], final_result["suberror"])
        return final_result

    def _acquire_token_silent_from_cache_and_possibly_refresh_it(
            self,
            scopes,  # type: List[str]
            account,  # type: Optional[Account]
            authority,  # This can be different than self.authority
            force_refresh=False,  # type: Optional[boolean]
            claims_challenge=None,
            **kwargs):
        access_token_from_cache = None
        if not (force_refresh or claims_challenge):  # Bypass AT when desired or using claims
            query={
                    "client_id": self.client_id,
                    "environment": authority.instance,
                    "realm": authority.tenant,
                    "home_account_id": (account or {}).get("home_account_id"),
                    }
            key_id = kwargs.get("data", {}).get("key_id")
            if key_id:  # Some token types (SSH-certs, POP) are bound to a key
                query["key_id"] = key_id
            matches = self.token_cache.find(
                self.token_cache.CredentialType.ACCESS_TOKEN,
                target=scopes,
                query=query)
            now = time.time()
            refresh_reason = msal.telemetry.AT_ABSENT
            for entry in matches:
                expires_in = int(entry["expires_on"]) - now
                if expires_in < 5*60:  # Then consider it expired
                    refresh_reason = msal.telemetry.AT_EXPIRED
                    continue  # Removal is not necessary, it will be overwritten
                logger.debug("Cache hit an AT")
                access_token_from_cache = {  # Mimic a real response
                    "access_token": entry["secret"],
                    "token_type": entry.get("token_type", "Bearer"),
                    "expires_in": int(expires_in),  # OAuth2 specs defines it as int
                    }
                if "refresh_on" in entry and int(entry["refresh_on"]) < now:  # aging
                    refresh_reason = msal.telemetry.AT_AGING
                    break  # With a fallback in hand, we break here to go refresh
                self._build_telemetry_context(-1).hit_an_access_token()
                return access_token_from_cache  # It is still good as new
        else:
            refresh_reason = msal.telemetry.FORCE_REFRESH  # TODO: It could also mean claims_challenge
        assert refresh_reason, "It should have been established at this point"
        try:
            result = _clean_up(self._acquire_token_silent_by_finding_rt_belongs_to_me_or_my_family(
                authority, decorate_scope(scopes, self.client_id), account,
                refresh_reason=refresh_reason, claims_challenge=claims_challenge,
                **kwargs))
            if (result and "error" not in result) or (not access_token_from_cache):
                return result
        except:  # The exact HTTP exception is transportation-layer dependent
            logger.exception("Refresh token failed")  # Potential AAD outage?
        return access_token_from_cache

    def _acquire_token_silent_by_finding_rt_belongs_to_me_or_my_family(
            self, authority, scopes, account, **kwargs):
        query = {
            "environment": authority.instance,
            "home_account_id": (account or {}).get("home_account_id"),
            # "realm": authority.tenant,  # AAD RTs are tenant-independent
            }
        app_metadata = self._get_app_metadata(authority.instance)
        if not app_metadata:  # Meaning this app is now used for the first time.
            # When/if we have a way to directly detect current app's family,
            # we'll rewrite this block, to support multiple families.
            # For now, we try existing RTs (*). If it works, we are in that family.
            # (*) RTs of a different app/family are not supposed to be
            # shared with or accessible by us in the first place.
            at = self._acquire_token_silent_by_finding_specific_refresh_token(
                authority, scopes,
                dict(query, family_id="1"),  # A hack, we have only 1 family for now
                rt_remover=lambda rt_item: None,  # NO-OP b/c RTs are likely not mine
                break_condition=lambda response:  # Break loop when app not in family
                    # Based on an AAD-only behavior mentioned in internal doc here
                    # https://msazure.visualstudio.com/One/_git/ESTS-Docs/pullrequest/1138595
                    "client_mismatch" in response.get("error_additional_info", []),
                **kwargs)
            if at and "error" not in at:
                return at
        last_resp = None
        if app_metadata.get("family_id"):  # Meaning this app belongs to this family
            last_resp = at = self._acquire_token_silent_by_finding_specific_refresh_token(
                authority, scopes, dict(query, family_id=app_metadata["family_id"]),
                **kwargs)
            if at and "error" not in at:
                return at
        # Either this app is an orphan, so we will naturally use its own RT;
        # or all attempts above have failed, so we fall back to non-foci behavior.
        return self._acquire_token_silent_by_finding_specific_refresh_token(
            authority, scopes, dict(query, client_id=self.client_id),
            **kwargs) or last_resp

    def _get_app_metadata(self, environment):
        apps = self.token_cache.find(  # Use find(), rather than token_cache.get(...)
            TokenCache.CredentialType.APP_METADATA, query={
                "environment": environment, "client_id": self.client_id})
        return apps[0] if apps else {}

    def _acquire_token_silent_by_finding_specific_refresh_token(
            self, authority, scopes, query,
            rt_remover=None, break_condition=lambda response: False,
            refresh_reason=None, correlation_id=None, claims_challenge=None,
            **kwargs):
        matches = self.token_cache.find(
            self.token_cache.CredentialType.REFRESH_TOKEN,
            # target=scopes,  # AAD RTs are scope-independent
            query=query)
        logger.debug("Found %d RTs matching %s", len(matches), query)
        client = self._build_client(self.client_credential, authority)

        response = None  # A distinguishable value to mean cache is empty
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_SILENT_ID,
            correlation_id=correlation_id, refresh_reason=refresh_reason)
        for entry in sorted(  # Since unfit RTs would not be aggressively removed,
                              # we start from newer RTs which are more likely fit.
                matches,
                key=lambda e: int(e.get("last_modification_time", "0")),
                reverse=True):
            logger.debug("Cache attempts an RT")
            response = client.obtain_token_by_refresh_token(
                entry, rt_getter=lambda token_item: token_item["secret"],
                on_removing_rt=lambda rt_item: None,  # Disable RT removal,
                    # because an invalid_grant could be caused by new MFA policy,
                    # the RT could still be useful for other MFA-less scope or tenant
                on_obtaining_tokens=lambda event: self.token_cache.add(dict(
                    event,
                    environment=authority.instance,
                    skip_account_creation=True,  # To honor a concurrent remove_account()
                    )),
                scope=scopes,
                headers=telemetry_context.generate_headers(),
                data=dict(
                    kwargs.pop("data", {}),
                    claims=_merge_claims_challenge_and_capabilities(
                        self._client_capabilities, claims_challenge)),
                **kwargs)
            telemetry_context.update_telemetry(response)
            if "error" not in response:
                return response
            logger.debug("Refresh failed. {error}: {error_description}".format(
                error=response.get("error"),
                error_description=response.get("error_description"),
                ))
            if break_condition(response):
                break
        return response  # Returns the latest error (if any), or just None

    def _validate_ssh_cert_input_data(self, data):
        if data.get("token_type") == "ssh-cert":
            if not data.get("req_cnf"):
                raise ValueError(
                    "When requesting an SSH certificate, "
                    "you must include a string parameter named 'req_cnf' "
                    "containing the public key in JWK format "
                    "(https://tools.ietf.org/html/rfc7517).")
            if not data.get("key_id"):
                raise ValueError(
                    "When requesting an SSH certificate, "
                    "you must include a string parameter named 'key_id' "
                    "which identifies the key in the 'req_cnf' argument.")

    def acquire_token_by_refresh_token(self, refresh_token, scopes, **kwargs):
        """Acquire token(s) based on a refresh token (RT) obtained from elsewhere.

        You use this method only when you have old RTs from elsewhere,
        and now you want to migrate them into MSAL.
        Calling this method results in new tokens automatically storing into MSAL.

        You do NOT need to use this method if you are already using MSAL.
        MSAL maintains RT automatically inside its token cache,
        and an access token can be retrieved
        when you call :func:`~acquire_token_silent`.

        :param str refresh_token: The old refresh token, as a string.

        :param list scopes:
            The scopes associate with this old RT.
            Each scope needs to be in the Microsoft identity platform (v2) format.
            See `Scopes not resources <https://docs.microsoft.com/en-us/azure/active-directory/develop/migrate-python-adal-msal#scopes-not-resources>`_.

        :return:
            * A dict contains "error" and some other keys, when error happened.
            * A dict contains no "error" key means migration was successful.
        """
        self._validate_ssh_cert_input_data(kwargs.get("data", {}))
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_BY_REFRESH_TOKEN,
            refresh_reason=msal.telemetry.FORCE_REFRESH)
        response = _clean_up(self.client.obtain_token_by_refresh_token(
            refresh_token,
            scope=decorate_scope(scopes, self.client_id),
            headers=telemetry_context.generate_headers(),
            rt_getter=lambda rt: rt,
            on_updating_rt=False,
            on_removing_rt=lambda rt_item: None,  # No OP
            **kwargs))
        telemetry_context.update_telemetry(response)
        return response

    def acquire_token_by_username_password(
            self, username, password, scopes, claims_challenge=None, **kwargs):
        """Gets a token for a given resource via user credentials.

        See this page for constraints of Username Password Flow.
        https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication

        :param str username: Typically a UPN in the form of an email address.
        :param str password: The password.
        :param list[str] scopes:
            Scopes requested to access a protected API (a resource).
        :param claims_challenge:
            The claims_challenge parameter requests specific claims requested by the resource provider
            in the form of a claims_challenge directive in the www-authenticate header to be
            returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
            It is a string of a JSON object which contains lists of claims being requested from these locations.

        :return: A dict representing the json response from AAD:

            - A successful response would contain "access_token" key,
            - an error response would contain "error" and usually "error_description".
        """
        scopes = decorate_scope(scopes, self.client_id)
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_BY_USERNAME_PASSWORD_ID)
        headers = telemetry_context.generate_headers()
        data = dict(
            kwargs.pop("data", {}),
            claims=_merge_claims_challenge_and_capabilities(
                self._client_capabilities, claims_challenge))
        if not self.authority.is_adfs:
            user_realm_result = self.authority.user_realm_discovery(
                username, correlation_id=headers[msal.telemetry.CLIENT_REQUEST_ID])
            if user_realm_result.get("account_type") == "Federated":
                response = _clean_up(self._acquire_token_by_username_password_federated(
                    user_realm_result, username, password, scopes=scopes,
                    data=data,
                    headers=headers, **kwargs))
                telemetry_context.update_telemetry(response)
                return response
        response = _clean_up(self.client.obtain_token_by_username_password(
                username, password, scope=scopes,
                headers=headers,
                data=data,
                **kwargs))
        telemetry_context.update_telemetry(response)
        return response

    def _acquire_token_by_username_password_federated(
            self, user_realm_result, username, password, scopes=None, **kwargs):
        wstrust_endpoint = {}
        if user_realm_result.get("federation_metadata_url"):
            wstrust_endpoint = mex_send_request(
                user_realm_result["federation_metadata_url"],
                self.http_client)
            if wstrust_endpoint is None:
                raise ValueError("Unable to find wstrust endpoint from MEX. "
                    "This typically happens when attempting MSA accounts. "
                    "More details available here. "
                    "https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication")
        logger.debug("wstrust_endpoint = %s", wstrust_endpoint)
        wstrust_result = wst_send_request(
            username, password,
            user_realm_result.get("cloud_audience_urn", "urn:federation:MicrosoftOnline"),
            wstrust_endpoint.get("address",
                # Fallback to an AAD supplied endpoint
                user_realm_result.get("federation_active_auth_url")),
            wstrust_endpoint.get("action"), self.http_client)
        if not ("token" in wstrust_result and "type" in wstrust_result):
            raise RuntimeError("Unsuccessful RSTR. %s" % wstrust_result)
        GRANT_TYPE_SAML1_1 = 'urn:ietf:params:oauth:grant-type:saml1_1-bearer'
        grant_type = {
            SAML_TOKEN_TYPE_V1: GRANT_TYPE_SAML1_1,
            SAML_TOKEN_TYPE_V2: self.client.GRANT_TYPE_SAML2,
            WSS_SAML_TOKEN_PROFILE_V1_1: GRANT_TYPE_SAML1_1,
            WSS_SAML_TOKEN_PROFILE_V2: self.client.GRANT_TYPE_SAML2
            }.get(wstrust_result.get("type"))
        if not grant_type:
            raise RuntimeError(
                "RSTR returned unknown token type: %s", wstrust_result.get("type"))
        self.client.grant_assertion_encoders.setdefault(  # Register a non-standard type
            grant_type, self.client.encode_saml_assertion)
        return self.client.obtain_token_by_assertion(
            wstrust_result["token"], grant_type, scope=scopes, **kwargs)


class PublicClientApplication(ClientApplication):  # browser app or mobile app

    DEVICE_FLOW_CORRELATION_ID = "_correlation_id"

    def __init__(self, client_id, client_credential=None, **kwargs):
        if client_credential is not None:
            raise ValueError("Public Client should not possess credentials")
        super(PublicClientApplication, self).__init__(
            client_id, client_credential=None, **kwargs)

    def acquire_token_interactive(
            self,
            scopes,  # type: list[str]
            prompt=None,
            login_hint=None,  # type: Optional[str]
            domain_hint=None,  # type: Optional[str]
            claims_challenge=None,
            timeout=None,
            port=None,
            extra_scopes_to_consent=None,
            **kwargs):
        """Acquire token interactively i.e. via a local browser.

        Prerequisite: In Azure Portal, configure the Redirect URI of your
        "Mobile and Desktop application" as ``http://localhost``.

        :param list scopes:
            It is a list of case-sensitive strings.
        :param str prompt:
            By default, no prompt value will be sent, not even "none".
            You will have to specify a value explicitly.
            Its valid values are defined in Open ID Connect specs
            https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        :param str login_hint:
            Optional. Identifier of the user. Generally a User Principal Name (UPN).
        :param domain_hint:
            Can be one of "consumers" or "organizations" or your tenant domain "contoso.com".
            If included, it will skip the email-based discovery process that user goes
            through on the sign-in page, leading to a slightly more streamlined user experience.
            More information on possible values
            `here <https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an-authorization-code>`_ and
            `here <https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-oapx/86fb452d-e34a-494e-ac61-e526e263b6d8>`_.

        :param claims_challenge:
            The claims_challenge parameter requests specific claims requested by the resource provider
            in the form of a claims_challenge directive in the www-authenticate header to be
            returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
            It is a string of a JSON object which contains lists of claims being requested from these locations.

        :param int timeout:
            This method will block the current thread.
            This parameter specifies the timeout value in seconds.
            Default value ``None`` means wait indefinitely.

        :param int port:
            The port to be used to listen to an incoming auth response.
            By default we will use a system-allocated port.
            (The rest of the redirect_uri is hard coded as ``http://localhost``.)

        :param list extra_scopes_to_consent:
            "Extra scopes to consent" is a concept only available in AAD.
            It refers to other resources you might want to prompt to consent for,
            in the same interaction, but for which you won't get back a
            token for in this particular operation.

        :return:
            - A dict containing no "error" key,
              and typically contains an "access_token" key.
            - A dict containing an "error" key, when token refresh failed.
        """
        self._validate_ssh_cert_input_data(kwargs.get("data", {}))
        claims = _merge_claims_challenge_and_capabilities(
            self._client_capabilities, claims_challenge)
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_INTERACTIVE)
        response = _clean_up(self.client.obtain_token_by_browser(
            scope=decorate_scope(scopes, self.client_id) if scopes else None,
            extra_scope_to_consent=extra_scopes_to_consent,
            redirect_uri="http://localhost:{port}".format(
                # Hardcode the host, for now. AAD portal rejects 127.0.0.1 anyway
                port=port or 0),
            prompt=prompt,
            login_hint=login_hint,
            timeout=timeout,
            auth_params={
                "claims": claims,
                "domain_hint": domain_hint,
                },
            data=dict(kwargs.pop("data", {}), claims=claims),
            headers=telemetry_context.generate_headers(),
            **kwargs))
        telemetry_context.update_telemetry(response)
        return response

    def initiate_device_flow(self, scopes=None, **kwargs):
        """Initiate a Device Flow instance,
        which will be used in :func:`~acquire_token_by_device_flow`.

        :param list[str] scopes:
            Scopes requested to access a protected API (a resource).
        :return: A dict representing a newly created Device Flow object.

            - A successful response would contain "user_code" key, among others
            - an error response would contain some other readable key/value pairs.
        """
        correlation_id = msal.telemetry._get_new_correlation_id()
        flow = self.client.initiate_device_flow(
            scope=decorate_scope(scopes or [], self.client_id),
            headers={msal.telemetry.CLIENT_REQUEST_ID: correlation_id},
            **kwargs)
        flow[self.DEVICE_FLOW_CORRELATION_ID] = correlation_id
        return flow

    def acquire_token_by_device_flow(self, flow, claims_challenge=None, **kwargs):
        """Obtain token by a device flow object, with customizable polling effect.

        :param dict flow:
            A dict previously generated by :func:`~initiate_device_flow`.
            By default, this method's polling effect  will block current thread.
            You can abort the polling loop at any time,
            by changing the value of the flow's "expires_at" key to 0.
        :param claims_challenge:
            The claims_challenge parameter requests specific claims requested by the resource provider
            in the form of a claims_challenge directive in the www-authenticate header to be
            returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
            It is a string of a JSON object which contains lists of claims being requested from these locations.

        :return: A dict representing the json response from AAD:

            - A successful response would contain "access_token" key,
            - an error response would contain "error" and usually "error_description".
        """
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_BY_DEVICE_FLOW_ID,
            correlation_id=flow.get(self.DEVICE_FLOW_CORRELATION_ID))
        response = _clean_up(self.client.obtain_token_by_device_flow(
            flow,
            data=dict(
                kwargs.pop("data", {}),
                code=flow["device_code"],  # 2018-10-4 Hack:
                    # during transition period,
                    # service seemingly need both device_code and code parameter.
                claims=_merge_claims_challenge_and_capabilities(
                    self._client_capabilities, claims_challenge),
                ),
            headers=telemetry_context.generate_headers(),
            **kwargs))
        telemetry_context.update_telemetry(response)
        return response


class ConfidentialClientApplication(ClientApplication):  # server-side web app

    def acquire_token_for_client(self, scopes, claims_challenge=None, **kwargs):
        """Acquires token for the current confidential client, not for an end user.

        :param list[str] scopes: (Required)
            Scopes requested to access a protected API (a resource).
        :param claims_challenge:
            The claims_challenge parameter requests specific claims requested by the resource provider
            in the form of a claims_challenge directive in the www-authenticate header to be
            returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
            It is a string of a JSON object which contains lists of claims being requested from these locations.

        :return: A dict representing the json response from AAD:

            - A successful response would contain "access_token" key,
            - an error response would contain "error" and usually "error_description".
        """
        # TBD: force_refresh behavior
        self._validate_ssh_cert_input_data(kwargs.get("data", {}))
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_FOR_CLIENT_ID)
        response = _clean_up(self.client.obtain_token_for_client(
            scope=scopes,  # This grant flow requires no scope decoration
            headers=telemetry_context.generate_headers(),
            data=dict(
                kwargs.pop("data", {}),
                claims=_merge_claims_challenge_and_capabilities(
                    self._client_capabilities, claims_challenge)),
            **kwargs))
        telemetry_context.update_telemetry(response)
        return response

    def acquire_token_on_behalf_of(self, user_assertion, scopes, claims_challenge=None, **kwargs):
        """Acquires token using on-behalf-of (OBO) flow.

        The current app is a middle-tier service which was called with a token
        representing an end user.
        The current app can use such token (a.k.a. a user assertion) to request
        another token to access downstream web API, on behalf of that user.
        See `detail docs here <https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow>`_ .

        The current middle-tier app has no user interaction to obtain consent.
        See how to gain consent upfront for your middle-tier app from this article.
        https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow#gaining-consent-for-the-middle-tier-application

        :param str user_assertion: The incoming token already received by this app
        :param list[str] scopes: Scopes required by downstream API (a resource).
        :param claims_challenge:
            The claims_challenge parameter requests specific claims requested by the resource provider
            in the form of a claims_challenge directive in the www-authenticate header to be
            returned from the UserInfo Endpoint and/or in the ID Token and/or Access Token.
            It is a string of a JSON object which contains lists of claims being requested from these locations.

        :return: A dict representing the json response from AAD:

            - A successful response would contain "access_token" key,
            - an error response would contain "error" and usually "error_description".
        """
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_ON_BEHALF_OF_ID)
        # The implementation is NOT based on Token Exchange
        # https://tools.ietf.org/html/draft-ietf-oauth-token-exchange-16
        response = _clean_up(self.client.obtain_token_by_assertion(  # bases on assertion RFC 7521
            user_assertion,
            self.client.GRANT_TYPE_JWT,  # IDTs and AAD ATs are all JWTs
            scope=decorate_scope(scopes, self.client_id),  # Decoration is used for:
                # 1. Explicitly requesting an RT, without relying on AAD default
                #    behavior, even though it currently still issues an RT.
                # 2. Requesting an IDT (which would otherwise be unavailable)
                #    so that the calling app could use id_token_claims to implement
                #    their own cache mapping, which is likely needed in web apps.
            data=dict(
                kwargs.pop("data", {}),
                requested_token_use="on_behalf_of",
                claims=_merge_claims_challenge_and_capabilities(
                    self._client_capabilities, claims_challenge)),
            headers=telemetry_context.generate_headers(),
            **kwargs))
        telemetry_context.update_telemetry(response)
        return response
