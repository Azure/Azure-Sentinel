# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import uuid
from typing import (  # pylint: disable=unused-import
    Optional,
    Any,
    Tuple,
)

try:
    from urllib.parse import parse_qs, quote
except ImportError:
    from urlparse import parse_qs  # type: ignore
    from urllib2 import quote  # type: ignore

import six

from azure.core.configuration import Configuration
from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport, HttpTransport
from azure.core.pipeline.policies import (
    RedirectPolicy,
    ContentDecodePolicy,
    BearerTokenCredentialPolicy,
    ProxyPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy,
    AzureSasCredentialPolicy
)

from .constants import STORAGE_OAUTH_SCOPE, SERVICE_HOST_BASE, CONNECTION_TIMEOUT, READ_TIMEOUT
from .models import LocationMode
from .authentication import SharedKeyCredentialPolicy
from .shared_access_signature import QueryStringConstants
from .request_handlers import serialize_batch_body, _get_batch_request_delimiter
from .policies import (
    StorageHeadersPolicy,
    StorageContentValidation,
    StorageRequestHook,
    StorageResponseHook,
    StorageLoggingPolicy,
    StorageHosts,
    QueueMessagePolicy,
    ExponentialRetry,
)
from .._version import VERSION
from .response_handlers import process_storage_error, PartialBatchErrorException


_LOGGER = logging.getLogger(__name__)
_SERVICE_PARAMS = {
    "blob": {"primary": "BLOBENDPOINT", "secondary": "BLOBSECONDARYENDPOINT"},
    "queue": {"primary": "QUEUEENDPOINT", "secondary": "QUEUESECONDARYENDPOINT"},
    "file": {"primary": "FILEENDPOINT", "secondary": "FILESECONDARYENDPOINT"},
    "dfs": {"primary": "BLOBENDPOINT", "secondary": "BLOBENDPOINT"},
}


class StorageAccountHostsMixin(object):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        parsed_url,  # type: Any
        service,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self._location_mode = kwargs.get("_location_mode", LocationMode.PRIMARY)
        self._hosts = kwargs.get("_hosts")
        self.scheme = parsed_url.scheme

        if service not in ["blob", "queue", "file-share", "dfs"]:
            raise ValueError("Invalid service: {}".format(service))
        service_name = service.split('-')[0]
        account = parsed_url.netloc.split(".{}.core.".format(service_name))

        self.account_name = account[0] if len(account) > 1 else None
        if not self.account_name and parsed_url.netloc.startswith("localhost") \
                or parsed_url.netloc.startswith("127.0.0.1"):
            self.account_name = parsed_url.path.strip("/")

        self.credential = _format_shared_key_credential(self.account_name, credential)
        if self.scheme.lower() != "https" and hasattr(self.credential, "get_token"):
            raise ValueError("Token credential is only supported with HTTPS.")

        secondary_hostname = None
        if hasattr(self.credential, "account_name"):
            self.account_name = self.credential.account_name
            secondary_hostname = "{}-secondary.{}.{}".format(
                self.credential.account_name, service_name, SERVICE_HOST_BASE)

        if not self._hosts:
            if len(account) > 1:
                secondary_hostname = parsed_url.netloc.replace(account[0], account[0] + "-secondary")
            if kwargs.get("secondary_hostname"):
                secondary_hostname = kwargs["secondary_hostname"]
            primary_hostname = (parsed_url.netloc + parsed_url.path).rstrip('/')
            self._hosts = {LocationMode.PRIMARY: primary_hostname, LocationMode.SECONDARY: secondary_hostname}

        self.require_encryption = kwargs.get("require_encryption", False)
        self.key_encryption_key = kwargs.get("key_encryption_key")
        self.key_resolver_function = kwargs.get("key_resolver_function")
        self._config, self._pipeline = self._create_pipeline(self.credential, storage_sdk=service, **kwargs)

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self):
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._client.close()

    @property
    def url(self):
        """The full endpoint URL to this entity, including SAS token if used.

        This could be either the primary endpoint,
        or the secondary endpoint depending on the current :func:`location_mode`.
        """
        return self._format_url(self._hosts[self._location_mode])

    @property
    def primary_endpoint(self):
        """The full primary endpoint URL.

        :type: str
        """
        return self._format_url(self._hosts[LocationMode.PRIMARY])

    @property
    def primary_hostname(self):
        """The hostname of the primary endpoint.

        :type: str
        """
        return self._hosts[LocationMode.PRIMARY]

    @property
    def secondary_endpoint(self):
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
    def secondary_hostname(self):
        """The hostname of the secondary endpoint.

        If not available this will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.

        :type: str or None
        """
        return self._hosts[LocationMode.SECONDARY]

    @property
    def location_mode(self):
        """The location mode that the client is currently using.

        By default this will be "primary". Options include "primary" and "secondary".

        :type: str
        """

        return self._location_mode

    @location_mode.setter
    def location_mode(self, value):
        if self._hosts.get(value):
            self._location_mode = value
            self._client._config.url = self.url  # pylint: disable=protected-access
        else:
            raise ValueError("No host URL for location mode: {}".format(value))

    @property
    def api_version(self):
        """The version of the Storage API used for requests.

        :type: str
        """
        return self._client._config.version  # pylint: disable=protected-access

    def _format_query_string(self, sas_token, credential, snapshot=None, share_snapshot=None):
        query_str = "?"
        if snapshot:
            query_str += "snapshot={}&".format(self.snapshot)
        if share_snapshot:
            query_str += "sharesnapshot={}&".format(self.snapshot)
        if sas_token and isinstance(credential, AzureSasCredential):
            raise ValueError(
                "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature.")
        if sas_token and not credential:
            query_str += sas_token
        elif is_credential_sastoken(credential):
            query_str += credential.lstrip("?")
            credential = None
        return query_str.rstrip("?&"), credential

    def _create_pipeline(self, credential, **kwargs):
        # type: (Any, **Any) -> Tuple[Configuration, Pipeline]
        self._credential_policy = None
        if hasattr(credential, "get_token"):
            self._credential_policy = BearerTokenCredentialPolicy(credential, STORAGE_OAUTH_SCOPE)
        elif isinstance(credential, SharedKeyCredentialPolicy):
            self._credential_policy = credential
        elif isinstance(credential, AzureSasCredential):
            self._credential_policy = AzureSasCredentialPolicy(credential)
        elif credential is not None:
            raise TypeError("Unsupported credential: {}".format(credential))

        config = kwargs.get("_configuration") or create_configuration(**kwargs)
        if kwargs.get("_pipeline"):
            return config, kwargs["_pipeline"]
        config.transport = kwargs.get("transport")  # type: ignore
        kwargs.setdefault("connection_timeout", CONNECTION_TIMEOUT)
        kwargs.setdefault("read_timeout", READ_TIMEOUT)
        if not config.transport:
            config.transport = RequestsTransport(**kwargs)
        policies = [
            QueueMessagePolicy(),
            config.proxy_policy,
            config.user_agent_policy,
            StorageContentValidation(),
            ContentDecodePolicy(response_encoding="utf-8"),
            RedirectPolicy(**kwargs),
            StorageHosts(hosts=self._hosts, **kwargs),
            config.retry_policy,
            config.headers_policy,
            StorageRequestHook(**kwargs),
            self._credential_policy,
            config.logging_policy,
            StorageResponseHook(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs)
        ]
        if kwargs.get("_additional_pipeline_policies"):
            policies = policies + kwargs.get("_additional_pipeline_policies")
        return config, Pipeline(config.transport, policies=policies)

    def _batch_send(
        self,
        *reqs,  # type: HttpRequest
        **kwargs
    ):
        """Given a series of request, do a Storage batch call.
        """
        # Pop it here, so requests doesn't feel bad about additional kwarg
        raise_on_any_failure = kwargs.pop("raise_on_any_failure", True)
        batch_id = str(uuid.uuid1())

        request = self._client._client.post(  # pylint: disable=protected-access
            url='{}://{}/{}?{}comp=batch{}{}'.format(
                self.scheme,
                self.primary_hostname,
                kwargs.pop('path', ""),
                kwargs.pop('restype', ""),
                kwargs.pop('sas', ""),
                kwargs.pop('timeout', "")
            ),
            headers={
                'x-ms-version': self.api_version,
                "Content-Type": "multipart/mixed; boundary=" + _get_batch_request_delimiter(batch_id, False, False)
            }
        )

        policies = [StorageHeadersPolicy()]
        if self._credential_policy:
            policies.append(self._credential_policy)

        request.set_multipart_mixed(
            *reqs,
            policies=policies,
            enforce_https=False
        )

        Pipeline._prepare_multipart_mixed_request(request) # pylint: disable=protected-access
        body = serialize_batch_body(request.multipart_mixed_info[0], batch_id)
        request.set_bytes_body(body)

        temp = request.multipart_mixed_info
        request.multipart_mixed_info = None
        pipeline_response = self._pipeline.run(
            request, **kwargs
        )
        response = pipeline_response.http_response
        request.multipart_mixed_info = temp

        try:
            if response.status_code not in [202]:
                raise HttpResponseError(response=response)
            parts = response.parts()
            if raise_on_any_failure:
                parts = list(response.parts())
                if any(p for p in parts if not 200 <= p.status_code < 300):
                    error = PartialBatchErrorException(
                        message="There is a partial failure in the batch operation.",
                        response=response, parts=parts
                    )
                    raise error
                return iter(parts)
            return parts
        except HttpResponseError as error:
            process_storage_error(error)

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


def _format_shared_key_credential(account_name, credential):
    if isinstance(credential, six.string_types):
        if not account_name:
            raise ValueError("Unable to determine account name for shared key credential.")
        credential = {"account_name": account_name, "account_key": credential}
    if isinstance(credential, dict):
        if "account_name" not in credential:
            raise ValueError("Shared key credential missing 'account_name")
        if "account_key" not in credential:
            raise ValueError("Shared key credential missing 'account_key")
        return SharedKeyCredentialPolicy(**credential)
    return credential


def parse_connection_str(conn_str, credential, service):
    conn_str = conn_str.rstrip(";")
    conn_settings = [s.split("=", 1) for s in conn_str.split(";")]
    if any(len(tup) != 2 for tup in conn_settings):
        raise ValueError("Connection string is either blank or malformed.")
    conn_settings = dict((key.upper(), val) for key, val in conn_settings)
    endpoints = _SERVICE_PARAMS[service]
    primary = None
    secondary = None
    if not credential:
        try:
            credential = {"account_name": conn_settings["ACCOUNTNAME"], "account_key": conn_settings["ACCOUNTKEY"]}
        except KeyError:
            credential = conn_settings.get("SHAREDACCESSSIGNATURE")
    if endpoints["primary"] in conn_settings:
        primary = conn_settings[endpoints["primary"]]
        if endpoints["secondary"] in conn_settings:
            secondary = conn_settings[endpoints["secondary"]]
    else:
        if endpoints["secondary"] in conn_settings:
            raise ValueError("Connection string specifies only secondary endpoint.")
        try:
            primary = "{}://{}.{}.{}".format(
                conn_settings["DEFAULTENDPOINTSPROTOCOL"],
                conn_settings["ACCOUNTNAME"],
                service,
                conn_settings["ENDPOINTSUFFIX"],
            )
            secondary = "{}-secondary.{}.{}".format(
                conn_settings["ACCOUNTNAME"], service, conn_settings["ENDPOINTSUFFIX"]
            )
        except KeyError:
            pass

    if not primary:
        try:
            primary = "https://{}.{}.{}".format(
                conn_settings["ACCOUNTNAME"], service, conn_settings.get("ENDPOINTSUFFIX", SERVICE_HOST_BASE)
            )
        except KeyError:
            raise ValueError("Connection string missing required connection details.")
    return primary, secondary, credential


def create_configuration(**kwargs):
    # type: (**Any) -> Configuration
    config = Configuration(**kwargs)
    config.headers_policy = StorageHeadersPolicy(**kwargs)
    config.user_agent_policy = UserAgentPolicy(
        sdk_moniker="storage-{}/{}".format(kwargs.pop('storage_sdk'), VERSION), **kwargs)
    config.retry_policy = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
    config.logging_policy = StorageLoggingPolicy(**kwargs)
    config.proxy_policy = ProxyPolicy(**kwargs)

    # Storage settings
    config.max_single_put_size = kwargs.get("max_single_put_size", 64 * 1024 * 1024)
    config.copy_polling_interval = 15

    # Block blob uploads
    config.max_block_size = kwargs.get("max_block_size", 4 * 1024 * 1024)
    config.min_large_block_upload_threshold = kwargs.get("min_large_block_upload_threshold", 4 * 1024 * 1024 + 1)
    config.use_byte_buffer = kwargs.get("use_byte_buffer", False)

    # Page blob uploads
    config.max_page_size = kwargs.get("max_page_size", 4 * 1024 * 1024)

    # Datalake file uploads
    config.min_large_chunk_upload_threshold = kwargs.get("min_large_chunk_upload_threshold", 100 * 1024 * 1024 + 1)

    # Blob downloads
    config.max_single_get_size = kwargs.get("max_single_get_size", 32 * 1024 * 1024)
    config.max_chunk_get_size = kwargs.get("max_chunk_get_size", 4 * 1024 * 1024)

    # File uploads
    config.max_range_size = kwargs.get("max_range_size", 4 * 1024 * 1024)
    return config


def parse_query(query_str):
    sas_values = QueryStringConstants.to_list()
    parsed_query = {k: v[0] for k, v in parse_qs(query_str).items()}
    sas_params = ["{}={}".format(k, quote(v, safe='')) for k, v in parsed_query.items() if k in sas_values]
    sas_token = None
    if sas_params:
        sas_token = "&".join(sas_params)

    snapshot = parsed_query.get("snapshot") or parsed_query.get("sharesnapshot")
    return snapshot, sas_token


def is_credential_sastoken(credential):
    if not credential or not isinstance(credential, six.string_types):
        return False

    sas_values = QueryStringConstants.to_list()
    parsed_query = parse_qs(credential.lstrip("?"))
    if parsed_query and all([k in sas_values for k in parsed_query.keys()]):
        return True
    return False
