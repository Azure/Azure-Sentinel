import json
try:
    from urllib.parse import urlparse
except ImportError:  # Fall back to Python 2
    from urlparse import urlparse
import logging

# Historically some customers patched this module-wide requests instance.
# We keep it here for now. They will be removed in next major release.
import requests
import requests as _requests

from .exceptions import MsalServiceError


logger = logging.getLogger(__name__)
WORLD_WIDE = 'login.microsoftonline.com'  # There was an alias login.windows.net
WELL_KNOWN_AUTHORITY_HOSTS = set([
    WORLD_WIDE,
    'login.chinacloudapi.cn',
    'login-us.microsoftonline.com',
    'login.microsoftonline.us',
    'login.microsoftonline.de',
    ])
WELL_KNOWN_B2C_HOSTS = [
    "b2clogin.com",
    "b2clogin.cn",
    "b2clogin.us",
    "b2clogin.de",
    ]


class Authority(object):
    """This class represents an (already-validated) authority.

    Once constructed, it contains members named "*_endpoint" for this instance.
    TODO: It will also cache the previously-validated authority instances.
    """
    _domains_without_user_realm_discovery = set([])

    @property
    def http_client(self):  # Obsolete. We will remove this in next major release.
        # A workaround: if module-wide requests is patched, we honor it.
        return self._http_client if requests is _requests else requests

    def __init__(self, authority_url, http_client, validate_authority=True):
        """Creates an authority instance, and also validates it.

        :param validate_authority:
            The Authority validation process actually checks two parts:
            instance (a.k.a. host) and tenant. We always do a tenant discovery.
            This parameter only controls whether an instance discovery will be
            performed.
        """
        self._http_client = http_client
        authority, self.instance, tenant = canonicalize(authority_url)
        parts = authority.path.split('/')
        is_b2c = any(self.instance.endswith("." + d) for d in WELL_KNOWN_B2C_HOSTS) or (
            len(parts) == 3 and parts[2].lower().startswith("b2c_"))
        if (tenant != "adfs" and (not is_b2c) and validate_authority
                and self.instance not in WELL_KNOWN_AUTHORITY_HOSTS):
            payload = instance_discovery(
                "https://{}{}/oauth2/v2.0/authorize".format(
                    self.instance, authority.path),
                self.http_client)
            if payload.get("error") == "invalid_instance":
                raise ValueError(
                    "invalid_instance: "
                    "The authority you provided, %s, is not whitelisted. "
                    "If it is indeed your legit customized domain name, "
                    "you can turn off this check by passing in "
                    "validate_authority=False"
                    % authority_url)
            tenant_discovery_endpoint = payload['tenant_discovery_endpoint']
        else:
            tenant_discovery_endpoint = (
                'https://{}{}{}/.well-known/openid-configuration'.format(
                    self.instance,
                    authority.path,  # In B2C scenario, it is "/tenant/policy"
                    "" if tenant == "adfs" else "/v2.0" # the AAD v2 endpoint
                    ))
        try:
            openid_config = tenant_discovery(
                tenant_discovery_endpoint,
                self.http_client)
        except ValueError:
            raise ValueError(
                "Unable to get authority configuration for {}. "
                "Authority would typically be in a format of "
                "https://login.microsoftonline.com/your_tenant_name".format(
                authority_url))
        logger.debug("openid_config = %s", openid_config)
        self.authorization_endpoint = openid_config['authorization_endpoint']
        self.token_endpoint = openid_config['token_endpoint']
        self.device_authorization_endpoint = openid_config.get('device_authorization_endpoint')
        _, _, self.tenant = canonicalize(self.token_endpoint)  # Usually a GUID
        self.is_adfs = self.tenant.lower() == 'adfs'

    def user_realm_discovery(self, username, correlation_id=None, response=None):
        # It will typically return a dict containing "ver", "account_type",
        # "federation_protocol", "cloud_audience_urn",
        # "federation_metadata_url", "federation_active_auth_url", etc.
        if self.instance not in self.__class__._domains_without_user_realm_discovery:
            resp = response or self.http_client.get(
                "https://{netloc}/common/userrealm/{username}?api-version=1.0".format(
                    netloc=self.instance, username=username),
                headers={'Accept': 'application/json',
                         'client-request-id': correlation_id},)
            if resp.status_code != 404:
                resp.raise_for_status()
                return json.loads(resp.text)
            self.__class__._domains_without_user_realm_discovery.add(self.instance)
        return {}  # This can guide the caller to fall back normal ROPC flow


def canonicalize(authority_url):
    # Returns (url_parsed_result, hostname_in_lowercase, tenant)
    authority = urlparse(authority_url)
    parts = authority.path.split("/")
    if authority.scheme != "https" or len(parts) < 2 or not parts[1]:
        raise ValueError(
            "Your given address (%s) should consist of "
            "an https url with a minimum of one segment in a path: e.g. "
            "https://login.microsoftonline.com/<tenant> "
            "or https://<tenant_name>.b2clogin.com/<tenant_name>.onmicrosoft.com/policy"
            % authority_url)
    return authority, authority.hostname, parts[1]

def instance_discovery(url, http_client, **kwargs):
    resp = http_client.get(  # Note: This URL seemingly returns V1 endpoint only
        'https://{}/common/discovery/instance'.format(
            WORLD_WIDE  # Historically using WORLD_WIDE. Could use self.instance too
                # See https://github.com/AzureAD/microsoft-authentication-library-for-dotnet/blob/4.0.0/src/Microsoft.Identity.Client/Instance/AadInstanceDiscovery.cs#L101-L103
                # and https://github.com/AzureAD/microsoft-authentication-library-for-dotnet/blob/4.0.0/src/Microsoft.Identity.Client/Instance/AadAuthority.cs#L19-L33
            ),
        params={'authorization_endpoint': url, 'api-version': '1.0'},
        **kwargs)
    return json.loads(resp.text)

def tenant_discovery(tenant_discovery_endpoint, http_client, **kwargs):
    # Returns Openid Configuration
    resp = http_client.get(tenant_discovery_endpoint, **kwargs)
    if resp.status_code == 200:
        payload = json.loads(resp.text)  # It could raise ValueError
        if 'authorization_endpoint' in payload and 'token_endpoint' in payload:
            return payload  # Happy path
        raise ValueError("OIDC Discovery does not provide enough information")
    if 400 <= resp.status_code < 500:
        # Nonexist tenant would hit this path
        # e.g. https://login.microsoftonline.com/nonexist_tenant/v2.0/.well-known/openid-configuration
        raise ValueError("OIDC Discovery endpoint rejects our request")
    # Transient network error would hit this path
    resp.raise_for_status()
    raise RuntimeError(  # A fallback here, in case resp.raise_for_status() is no-op
        "Unable to complete OIDC Discovery: %d, %s" % (resp.status_code, resp.text))

