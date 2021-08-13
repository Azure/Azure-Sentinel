# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Dict, Optional, Any, List, Mapping, Union, TYPE_CHECKING
from uuid import uuid4
try:
    from urllib.parse import parse_qs, quote, urlparse
except ImportError:
    from urlparse import parse_qs, urlparse  # type: ignore
    from urllib2 import quote  # type: ignore

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.utils import parse_connection_string
from azure.core.pipeline.transport import (
    HttpTransport,
    HttpRequest,
)
from azure.core.pipeline.policies import (
    RedirectPolicy,
    ContentDecodePolicy,
    BearerTokenCredentialPolicy,
    ProxyPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy,
    AzureSasCredentialPolicy,
    NetworkTraceLoggingPolicy,
    CustomHookPolicy,
    RequestIdPolicy,
)

from ._generated import AzureTable
from ._common_conversion import _is_cosmos_endpoint
from ._shared_access_signature import QueryStringConstants
from ._constants import (
    STORAGE_OAUTH_SCOPE,
    SERVICE_HOST_BASE,
)
from ._error import RequestTooLargeError, TableTransactionError, _decode_error
from ._models import LocationMode
from ._authentication import SharedKeyCredentialPolicy
from ._policies import (
    CosmosPatchTransformPolicy,
    StorageHeadersPolicy,
    StorageHosts,
    TablesRetryPolicy,
)
from ._sdk_moniker import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_SUPPORTED_API_VERSIONS = ["2019-02-02", "2019-07-07"]


def get_api_version(kwargs, default):
    # type: (Dict[str, Any], str) -> str
    api_version = kwargs.pop("api_version", None)
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = "\n".join(_SUPPORTED_API_VERSIONS)
        raise ValueError(
            "Unsupported API version '{}'. Please select from:\n{}".format(
                api_version, versions
            )
        )
    return api_version or default


class AccountHostsMixin(object):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        account_url,  # type: Any
        credential=None,  # type: Optional[Union[AzureNamedKeyCredential, AzureSasCredential, "TokenCredential"]]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith("http"):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip("/"))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"
            )
        self._query_str, credential = format_query_string(sas_token, credential)
        self._location_mode = kwargs.get("location_mode", LocationMode.PRIMARY)
        self._hosts = kwargs.get("_hosts")
        self.scheme = parsed_url.scheme
        self._cosmos_endpoint = _is_cosmos_endpoint(parsed_url)
        if ".core." in parsed_url.netloc or ".cosmos." in parsed_url.netloc:
            account = parsed_url.netloc.split(".table.core.")
            if "cosmos" in parsed_url.netloc:
                account = parsed_url.netloc.split(".table.cosmos.")
            self.account_name = account[0] if len(account) > 1 else None
        else:
            path_account_name = parsed_url.path.split("/")
            if len(path_account_name) > 1:
                self.account_name = path_account_name[1]
                account = [self.account_name, parsed_url.netloc]
            else:
                # If format doesn't fit Azurite, default to standard parsing
                account = parsed_url.netloc.split(".table.core.")
                self.account_name = account[0] if len(account) > 1 else None

        secondary_hostname = None
        self.credential = credential
        if self.scheme.lower() != "https" and hasattr(self.credential, "get_token"):
            raise ValueError("Token credential is only supported with HTTPS.")
        if hasattr(self.credential, "named_key"):
            self.account_name = self.credential.named_key.name  # type: ignore
            secondary_hostname = "{}-secondary.table.{}".format(
                self.credential.named_key.name, SERVICE_HOST_BASE  # type: ignore
            )

        if not self._hosts:
            if len(account) > 1:
                secondary_hostname = parsed_url.netloc.replace(
                    account[0], account[0] + "-secondary"
                ) + parsed_url.path.replace(
                    account[0], account[0] + "-secondary"
                ).rstrip("/")
            if kwargs.get("secondary_hostname"):
                secondary_hostname = kwargs["secondary_hostname"]
            primary_hostname = (parsed_url.netloc + parsed_url.path).rstrip("/")
            self._hosts = {
                LocationMode.PRIMARY: primary_hostname,
                LocationMode.SECONDARY: secondary_hostname,
            }
        self._credential_policy = None  # type: ignore
        self._configure_credential(self.credential)  # type: ignore
        self._policies = self._configure_policies(hosts=self._hosts, **kwargs)  # type: ignore
        if self._cosmos_endpoint:
            self._policies.insert(0, CosmosPatchTransformPolicy())

    @property
    def url(self):
        """The full endpoint URL to this entity, including SAS token if used.

        This could be either the primary endpoint,
        or the secondary endpoint depending on the current :func:`location_mode`.
        """
        return self._format_url(self._hosts[self._location_mode])

    @property
    def _primary_endpoint(self):
        """The full primary endpoint URL.

        :type: str
        """
        return self._format_url(self._hosts[LocationMode.PRIMARY])

    @property
    def _primary_hostname(self):
        """The hostname of the primary endpoint.

        :type: str
        """
        return self._hosts[LocationMode.PRIMARY]

    @property
    def _secondary_endpoint(self):
        """The full secondary endpoint URL if configured.

        If not available a ValueError will be raised. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.

        :type: str
        :raise ValueError:
        """
        if not self._hosts[LocationMode.SECONDARY]:
            raise ValueError("No secondary host configured.")
        return self._format_url(self._hosts[LocationMode.SECONDARY])

    @property
    def _secondary_hostname(self):
        """The hostname of the secondary endpoint.

        If not available this will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.

        :type: str or None
        """
        return self._hosts[LocationMode.SECONDARY]

    @property
    def api_version(self):
        """The version of the Storage API used for requests.

        :type: str
        """
        return self._client._config.version  # pylint: disable=protected-access


class TablesBaseClient(AccountHostsMixin):

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self,
        endpoint,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        credential = kwargs.pop('credential', None)
        super(TablesBaseClient, self).__init__(endpoint, credential=credential, **kwargs)
        self._client = AzureTable(
            self.url,
            policies=kwargs.pop('policies', self._policies),
            **kwargs
        )
        self._client._config.version = get_api_version(kwargs, self._client._config.version)  # pylint: disable=protected-access

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def _configure_policies(self, **kwargs):
        return [
            RequestIdPolicy(**kwargs),
            StorageHeadersPolicy(**kwargs),
            UserAgentPolicy(sdk_moniker=SDK_MONIKER, **kwargs),
            ProxyPolicy(**kwargs),
            self._credential_policy,
            ContentDecodePolicy(response_encoding="utf-8"),
            RedirectPolicy(**kwargs),
            StorageHosts(**kwargs),
            TablesRetryPolicy(**kwargs),
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]

    def _configure_credential(self, credential):
        # type: (Any) -> None
        if hasattr(credential, "get_token"):
            self._credential_policy = BearerTokenCredentialPolicy(  # type: ignore
                credential, STORAGE_OAUTH_SCOPE
            )
        elif isinstance(credential, SharedKeyCredentialPolicy):
            self._credential_policy = credential  # type: ignore
        elif isinstance(credential, AzureSasCredential):
            self._credential_policy = AzureSasCredentialPolicy(credential)  # type: ignore
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential_policy = SharedKeyCredentialPolicy(credential)  # type: ignore
        elif credential is not None:
            raise TypeError("Unsupported credential: {}".format(credential))

    def _batch_send(self, *reqs, **kwargs):
        # type: (List[HttpRequest], Any) -> List[Mapping[str, Any]]
        """Given a series of request, do a Storage batch call."""
        # Pop it here, so requests doesn't feel bad about additional kwarg
        policies = [StorageHeadersPolicy()]

        changeset = HttpRequest("POST", None)  # type: ignore
        changeset.set_multipart_mixed(
            *reqs, policies=policies, boundary="changeset_{}".format(uuid4())  # type: ignore
        )
        request = self._client._client.post(  # pylint: disable=protected-access
            url="https://{}/$batch".format(self._primary_hostname),
            headers={
                "x-ms-version": self.api_version,
                "DataServiceVersion": "3.0",
                "MaxDataServiceVersion": "3.0;NetFx",
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
        )
        request.set_multipart_mixed(
            changeset,
            policies=policies,
            enforce_https=False,
            boundary="batch_{}".format(uuid4()),
        )
        pipeline_response = self._client._client._pipeline.run(request, **kwargs)  # pylint: disable=protected-access
        response = pipeline_response.http_response
        if response.status_code == 413:
            raise _decode_error(
                response,
                error_message="The transaction request was too large",
                error_type=RequestTooLargeError)
        if response.status_code != 202:
            raise _decode_error(response)

        parts = list(response.parts())
        error_parts = [p for p in parts if not 200 <= p.status_code < 300]
        if any(error_parts):
            if error_parts[0].status_code == 413:
                raise _decode_error(
                    response,
                    error_message="The transaction request was too large",
                    error_type=RequestTooLargeError)
            raise _decode_error(
                response=error_parts[0],
                error_type=TableTransactionError
            )
        return [extract_batch_part_metadata(p) for p in parts]

    def close(self):
        # type: () -> None
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._client.close()


class TransportWrapper(HttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.
    """
    def __init__(self, transport):
        self._transport = transport

    def send(self, request, **kwargs):
        return self._transport.send(request, **kwargs)

    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *args):  # pylint: disable=arguments-differ
        pass


def parse_connection_str(conn_str, credential, keyword_args):
    conn_settings = parse_connection_string(conn_str)
    primary = None
    secondary = None
    if not credential:
        try:
            credential = AzureNamedKeyCredential(name=conn_settings["accountname"], key=conn_settings["accountkey"])
        except KeyError:
            credential = conn_settings.get("sharedaccesssignature", None)
            if not credential:
                raise ValueError("Connection string missing required connection details.")
            credential = AzureSasCredential(credential)
    primary = conn_settings.get("tableendpoint")
    secondary = conn_settings.get("tablesecondaryendpoint")
    if not primary:
        if secondary:
            raise ValueError("Connection string specifies only secondary endpoint.")
        try:
            primary = "{}://{}.table.{}".format(
                conn_settings["defaultendpointsprotocol"],
                conn_settings["accountname"],
                conn_settings["endpointsuffix"],
            )
            secondary = "{}-secondary.table.{}".format(
                conn_settings["accountname"], conn_settings["endpointsuffix"]
            )
        except KeyError:
            pass

    if not primary:
        try:
            primary = "https://{}.table.{}".format(
                conn_settings["accountname"],
                conn_settings.get("endpointsuffix", SERVICE_HOST_BASE),
            )
        except KeyError:
            raise ValueError("Connection string missing required connection details.")

    if "secondary_hostname" not in keyword_args:
        keyword_args["secondary_hostname"] = secondary

    return primary, credential


def extract_batch_part_metadata(response_part):
    metadata = {}
    if 'Etag' in response_part.headers:
        metadata['etag'] = response_part.headers['Etag']
    return metadata


def format_query_string(sas_token, credential):
    query_str = "?"
    if sas_token and isinstance(credential, AzureSasCredential):
        raise ValueError(
            "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature.")
    if sas_token and not credential:
        query_str += sas_token
    elif credential:
        return "", credential
    return query_str.rstrip("?&"), None


def parse_query(query_str):
    sas_values = QueryStringConstants.to_list()
    parsed_query = {k: v[0] for k, v in parse_qs(query_str).items()}
    sas_params = [
        "{}={}".format(k, quote(v, safe=""))
        for k, v in parsed_query.items()
        if k in sas_values
    ]
    sas_token = None
    if sas_params:
        sas_token = "&".join(sas_params)

    snapshot = parsed_query.get("snapshot") or parsed_query.get("sharesnapshot")
    return snapshot, sas_token
