# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, AnyStr, Dict, List, Tuple, IO, Iterator,
    TYPE_CHECKING
)


try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote, unquote # type: ignore

import six

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest

from ._shared.base_client import StorageAccountHostsMixin, TransportWrapper, parse_connection_str, parse_query
from ._shared.request_handlers import add_metadata_headers, serialize_iso
from ._shared.response_handlers import (
    process_storage_error,
    return_response_headers,
    return_headers_and_deserialized)
from ._generated import AzureBlobStorage
from ._generated.models import SignedIdentifier
from ._deserialize import deserialize_container_properties
from ._serialize import get_modify_conditions, get_container_cpk_scope_info, get_api_version, get_access_conditions
from ._models import ( # pylint: disable=unused-import
    ContainerProperties,
    BlobProperties,
    BlobType)
from ._list_blobs_helper import BlobPrefix, BlobPropertiesPaged
from ._lease import BlobLeaseClient
from ._blob_client import BlobClient

if TYPE_CHECKING:
    from azure.core.pipeline.transport import HttpTransport, HttpResponse  # pylint: disable=ungrouped-imports
    from azure.core.pipeline.policies import HTTPPolicy # pylint: disable=ungrouped-imports
    from datetime import datetime
    from ._models import (  # pylint: disable=unused-import
        PublicAccess,
        AccessPolicy,
        ContentSettings,
        StandardBlobTier,
        PremiumPageBlobTier)


def _get_blob_name(blob):
    """Return the blob name.

    :param blob: A blob string or BlobProperties
    :rtype: str
    """
    try:
        return blob.get('name')
    except AttributeError:
        return blob


class ContainerClient(StorageAccountHostsMixin):
    """A client to interact with a specific container, although that container
    may not yet exist.

    For operations relating to a specific blob within this container, a blob client can be
    retrieved using the :func:`~get_blob_client` function.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the container,
        use the :func:`from_container_url` classmethod.
    :param container_name:
        The name of the container for the blob.
    :type container_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential from azure.core.credentials, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-07-07'.
        Setting to an older version may result in reduced feature compatibility.

        .. versionadded:: 12.2.0

    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword int max_block_size: The maximum chunk size for uploading a block blob in chunks.
        Defaults to 4*1024*1024, or 4MB.
    :keyword int max_single_put_size: If the blob size is less than or equal max_single_put_size, then the blob will be
        uploaded with only one http PUT request. If the blob size is larger than max_single_put_size,
        the blob will be uploaded in chunks. Defaults to 64*1024*1024, or 64MB.
    :keyword int min_large_block_upload_threshold: The minimum chunk size required to use the memory efficient
        algorithm when uploading a block blob. Defaults to 4*1024*1024+1.
    :keyword bool use_byte_buffer: Use a byte buffer for block blob uploads. Defaults to False.
    :keyword int max_page_size: The maximum chunk size for uploading a page blob. Defaults to 4*1024*1024, or 4MB.
    :keyword int max_single_get_size: The maximum size for a blob to be downloaded in a single call,
        the exceeded part will be downloaded in chunks (could be parallel). Defaults to 32*1024*1024, or 32MB.
    :keyword int max_chunk_get_size: The maximum chunk size used for downloading a blob. Defaults to 4*1024*1024,
        or 4MB.

    .. admonition:: Example:

        .. literalinclude:: ../samples/blob_samples_containers.py
            :start-after: [START create_container_client_from_service]
            :end-before: [END create_container_client_from_service]
            :language: python
            :dedent: 8
            :caption: Get a ContainerClient from an existing BlobServiceClient.

        .. literalinclude:: ../samples/blob_samples_containers.py
            :start-after: [START create_container_client_sasurl]
            :end-before: [END create_container_client_sasurl]
            :language: python
            :dedent: 8
            :caption: Creating the container client directly.
    """
    def __init__(
            self, account_url,  # type: str
            container_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Container URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not container_name:
            raise ValueError("Please specify a container name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        _, sas_token = parse_query(parsed_url.query)
        self.container_name = container_name
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(ContainerClient, self).__init__(parsed_url, service='blob', credential=credential, **kwargs)
        self._client = AzureBlobStorage(self.url, pipeline=self._pipeline)
        default_api_version = self._client._config.version  # pylint: disable=protected-access
        self._client._config.version = get_api_version(kwargs, default_api_version) # pylint: disable=protected-access

    def _format_url(self, hostname):
        container_name = self.container_name
        if isinstance(container_name, six.text_type):
            container_name = container_name.encode('UTF-8')
        return "{}://{}/{}{}".format(
            self.scheme,
            hostname,
            quote(container_name),
            self._query_str)

    @classmethod
    def from_container_url(cls, container_url, credential=None, **kwargs):
        # type: (str, Optional[Any], Any) -> ContainerClient
        """Create ContainerClient from a container url.

        :param str container_url:
            The full endpoint URL to the Container, including SAS token if used. This could be
            either the primary endpoint, or the secondary endpoint depending on the current `location_mode`.
        :type container_url: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
            - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
        :returns: A container client.
        :rtype: ~azure.storage.blob.ContainerClient
        """
        try:
            if not container_url.lower().startswith('http'):
                container_url = "https://" + container_url
        except AttributeError:
            raise ValueError("Container URL must be a string.")
        parsed_url = urlparse(container_url.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(container_url))

        container_path = parsed_url.path.lstrip('/').split('/')
        account_path = ""
        if len(container_path) > 1:
            account_path = "/" + "/".join(container_path[:-1])
        account_url = "{}://{}{}?{}".format(
            parsed_url.scheme,
            parsed_url.netloc.rstrip('/'),
            account_path,
            parsed_url.query)
        container_name = unquote(container_path[-1])
        if not container_name:
            raise ValueError("Invalid URL. Please provide a URL with a valid container name")
        return cls(account_url, container_name=container_name, credential=credential, **kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            container_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> ContainerClient
        """Create ContainerClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param container_name:
            The container name for the blob.
        :type container_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :returns: A container client.
        :rtype: ~azure.storage.blob.ContainerClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_authentication.py
                :start-after: [START auth_from_connection_string_container]
                :end-before: [END auth_from_connection_string_container]
                :language: python
                :dedent: 8
                :caption: Creating the ContainerClient from a connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'blob')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, container_name=container_name, credential=credential, **kwargs)

    @distributed_trace
    def create_container(self, metadata=None, public_access=None, **kwargs):
        # type: (Optional[Dict[str, str]], Optional[Union[PublicAccess, str]], **Any) -> None
        """
        Creates a new container under the specified account. If the container
        with the same name already exists, the operation fails.

        :param metadata:
            A dict with name_value pairs to associate with the
            container as metadata. Example:{'Category':'test'}
        :type metadata: dict[str, str]
        :param ~azure.storage.blob.PublicAccess public_access:
            Possible values include: 'container', 'blob'.
        :keyword container_encryption_scope:
            Specifies the default encryption scope to set on the container and use for
            all future writes.

            .. versionadded:: 12.2.0

        :paramtype container_encryption_scope: dict or ~azure.storage.blob.ContainerEncryptionScope
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START create_container]
                :end-before: [END create_container]
                :language: python
                :dedent: 12
                :caption: Creating a container to store blobs.
        """
        headers = kwargs.pop('headers', {})
        timeout = kwargs.pop('timeout', None)
        headers.update(add_metadata_headers(metadata)) # type: ignore
        container_cpk_scope_info = get_container_cpk_scope_info(kwargs)
        try:
            return self._client.container.create( # type: ignore
                timeout=timeout,
                access=public_access,
                container_cpk_scope_info=container_cpk_scope_info,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def _rename_container(self, new_name, **kwargs):
        # type: (str, **Any) -> ContainerClient
        """Renames a container.

        Operation is successful only if the source container exists.

        :param str new_name:
            The new container name the user wants to rename to.
        :keyword lease:
            Specify this to perform only if the lease ID given
            matches the active lease ID of the source container.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.blob.ContainerClient
        """
        lease = kwargs.pop('lease', None)
        try:
            kwargs['source_lease_id'] = lease.id  # type: str
        except AttributeError:
            kwargs['source_lease_id'] = lease
        try:
            renamed_container = ContainerClient(
                "{}://{}".format(self.scheme, self.primary_hostname), container_name=new_name,
                credential=self.credential, api_version=self.api_version, _configuration=self._config,
                _pipeline=self._pipeline, _location_mode=self._location_mode, _hosts=self._hosts,
                require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
                key_resolver_function=self.key_resolver_function)
            renamed_container._client.container.rename(self.container_name, **kwargs)   # pylint: disable = protected-access
            return renamed_container
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def delete_container(
            self, **kwargs):
        # type: (Any) -> None
        """
        Marks the specified container for deletion. The container and any blobs
        contained within it are later deleted during garbage collection.

        :keyword lease:
            If specified, delete_container only succeeds if the
            container's lease is active and matches this ID.
            Required if the container has an active lease.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START delete_container]
                :end-before: [END delete_container]
                :language: python
                :dedent: 12
                :caption: Delete a container.
        """
        lease = kwargs.pop('lease', None)
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modify_conditions(kwargs)
        timeout = kwargs.pop('timeout', None)
        try:
            self._client.container.delete(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def acquire_lease(
            self, lease_duration=-1,  # type: int
            lease_id=None,  # type: Optional[str]
            **kwargs):
        # type: (...) -> BlobLeaseClient
        """
        Requests a new lease. If the container does not have an active lease,
        the Blob service creates a lease on the container and returns a new
        lease ID.

        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param str lease_id:
            Proposed lease ID, in a GUID string format. The Blob service returns
            400 (Invalid request) if the proposed lease ID is not in the correct format.
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A BlobLeaseClient object, that can be run in a context manager.
        :rtype: ~azure.storage.blob.BlobLeaseClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START acquire_lease_on_container]
                :end-before: [END acquire_lease_on_container]
                :language: python
                :dedent: 8
                :caption: Acquiring a lease on the container.
        """
        lease = BlobLeaseClient(self, lease_id=lease_id) # type: ignore
        kwargs.setdefault('merge_span', True)
        timeout = kwargs.pop('timeout', None)
        lease.acquire(lease_duration=lease_duration, timeout=timeout, **kwargs)
        return lease

    @distributed_trace
    def get_account_information(self, **kwargs):
        # type: (**Any) -> Dict[str, str]
        """Gets information related to the storage account.

        The information can also be retrieved if the user has a SAS to a container or blob.
        The keys in the returned dictionary include 'sku_name' and 'account_kind'.

        :returns: A dict of account information (SKU and account type).
        :rtype: dict(str, str)
        """
        try:
            return self._client.container.get_account_info(cls=return_response_headers, **kwargs) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def get_container_properties(self, **kwargs):
        # type: (Any) -> ContainerProperties
        """Returns all user-defined metadata and system properties for the specified
        container. The data returned does not include the container's list of blobs.

        :keyword lease:
            If specified, get_container_properties only succeeds if the
            container's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: Properties for the specified container within a container object.
        :rtype: ~azure.storage.blob.ContainerProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START get_container_properties]
                :end-before: [END get_container_properties]
                :language: python
                :dedent: 12
                :caption: Getting properties on the container.
        """
        lease = kwargs.pop('lease', None)
        access_conditions = get_access_conditions(lease)
        timeout = kwargs.pop('timeout', None)
        try:
            response = self._client.container.get_properties(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                cls=deserialize_container_properties,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        response.name = self.container_name
        return response # type: ignore

    @distributed_trace
    def exists(self, **kwargs):
        # type: (**Any) -> bool
        """
        Returns True if a container exists and returns False otherwise.

        :kwarg int timeout:
            The timeout parameter is expressed in seconds.
        :returns: boolean
        """
        try:
            self._client.container.get_properties(**kwargs)
            return True
        except HttpResponseError as error:
            try:
                process_storage_error(error)
            except ResourceNotFoundError:
                return False

    @distributed_trace
    def set_container_metadata( # type: ignore
            self, metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets one or more user-defined name-value pairs for the specified
        container. Each call to this operation replaces all existing metadata
        attached to the container. To remove all metadata from the container,
        call this operation with no metadata dict.

        :param metadata:
            A dict containing name-value pairs to associate with the container as
            metadata. Example: {'category':'test'}
        :type metadata: dict[str, str]
        :keyword lease:
            If specified, set_container_metadata only succeeds if the
            container's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Container-updated property dict (Etag and last modified).
        :rtype: dict[str, str or datetime]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START set_container_metadata]
                :end-before: [END set_container_metadata]
                :language: python
                :dedent: 12
                :caption: Setting metadata on the container.
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        lease = kwargs.pop('lease', None)
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modify_conditions(kwargs)
        timeout = kwargs.pop('timeout', None)
        try:
            return self._client.container.set_metadata( # type: ignore
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def get_container_access_policy(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Gets the permissions for the specified container.
        The permissions indicate whether container data may be accessed publicly.

        :keyword lease:
            If specified, get_container_access_policy only succeeds if the
            container's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Access policy information in a dict.
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START get_container_access_policy]
                :end-before: [END get_container_access_policy]
                :language: python
                :dedent: 12
                :caption: Getting the access policy on the container.
        """
        lease = kwargs.pop('lease', None)
        access_conditions = get_access_conditions(lease)
        timeout = kwargs.pop('timeout', None)
        try:
            response, identifiers = self._client.container.get_access_policy(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                cls=return_headers_and_deserialized,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return {
            'public_access': response.get('blob_public_access'),
            'signed_identifiers': identifiers or []
        }

    @distributed_trace
    def set_container_access_policy(
            self, signed_identifiers,  # type: Dict[str, AccessPolicy]
            public_access=None,  # type: Optional[Union[str, PublicAccess]]
            **kwargs
        ):  # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets the permissions for the specified container or stored access
        policies that may be used with Shared Access Signatures. The permissions
        indicate whether blobs in a container may be accessed publicly.

        :param signed_identifiers:
            A dictionary of access policies to associate with the container. The
            dictionary may contain up to 5 elements. An empty dictionary
            will clear the access policies set on the service.
        :type signed_identifiers: dict[str, ~azure.storage.blob.AccessPolicy]
        :param ~azure.storage.blob.PublicAccess public_access:
            Possible values include: 'container', 'blob'.
        :keyword lease:
            Required if the container has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A datetime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified date/time.
        :keyword ~datetime.datetime if_unmodified_since:
            A datetime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Container-updated property dict (Etag and last modified).
        :rtype: dict[str, str or ~datetime.datetime]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START set_container_access_policy]
                :end-before: [END set_container_access_policy]
                :language: python
                :dedent: 12
                :caption: Setting access policy on the container.
        """
        if len(signed_identifiers) > 5:
            raise ValueError(
                'Too many access policies provided. The server does not support setting '
                'more than 5 access policies on a single resource.')
        identifiers = []
        for key, value in signed_identifiers.items():
            if value:
                value.start = serialize_iso(value.start)
                value.expiry = serialize_iso(value.expiry)
            identifiers.append(SignedIdentifier(id=key, access_policy=value)) # type: ignore
        signed_identifiers = identifiers # type: ignore
        lease = kwargs.pop('lease', None)
        mod_conditions = get_modify_conditions(kwargs)
        access_conditions = get_access_conditions(lease)
        timeout = kwargs.pop('timeout', None)
        try:
            return self._client.container.set_access_policy(
                container_acl=signed_identifiers or None,
                timeout=timeout,
                access=public_access,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_blobs(self, name_starts_with=None, include=None, **kwargs):
        # type: (Optional[str], Optional[Union[str, List[str]]], **Any) -> ItemPaged[BlobProperties]
        """Returns a generator to list the blobs under the specified container.
        The generator will lazily follow the continuation tokens returned by
        the service.

        :param str name_starts_with:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :param list[str] or str include:
            Specifies one or more additional datasets to include in the response.
            Options include: 'snapshots', 'metadata', 'uncommittedblobs', 'copy', 'deleted', 'tags'.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) response of BlobProperties.
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.blob.BlobProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START list_blobs_in_container]
                :end-before: [END list_blobs_in_container]
                :language: python
                :dedent: 8
                :caption: List the blobs in the container.
        """
        if include and not isinstance(include, list):
            include = [include]

        results_per_page = kwargs.pop('results_per_page', None)
        timeout = kwargs.pop('timeout', None)
        command = functools.partial(
            self._client.container.list_blob_flat_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=BlobPropertiesPaged)

    @distributed_trace
    def walk_blobs(
            self, name_starts_with=None, # type: Optional[str]
            include=None, # type: Optional[Any]
            delimiter="/", # type: str
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> ItemPaged[BlobProperties]
        """Returns a generator to list the blobs under the specified container.
        The generator will lazily follow the continuation tokens returned by
        the service. This operation will list blobs in accordance with a hierarchy,
        as delimited by the specified delimiter character.

        :param str name_starts_with:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :param list[str] include:
            Specifies one or more additional datasets to include in the response.
            Options include: 'snapshots', 'metadata', 'uncommittedblobs', 'copy', 'deleted'.
        :param str delimiter:
            When the request includes this parameter, the operation returns a BlobPrefix
            element in the response body that acts as a placeholder for all blobs whose
            names begin with the same substring up to the appearance of the delimiter
            character. The delimiter may be a single character or a string.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) response of BlobProperties.
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.blob.BlobProperties]
        """
        if include and not isinstance(include, list):
            include = [include]

        results_per_page = kwargs.pop('results_per_page', None)
        timeout = kwargs.pop('timeout', None)
        command = functools.partial(
            self._client.container.list_blob_hierarchy_segment,
            delimiter=delimiter,
            include=include,
            timeout=timeout,
            **kwargs)
        return BlobPrefix(
            command,
            prefix=name_starts_with,
            results_per_page=results_per_page,
            delimiter=delimiter)

    @distributed_trace
    def upload_blob(
            self, name,  # type: Union[str, BlobProperties]
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            blob_type=BlobType.BlockBlob,  # type: Union[str, BlobType]
            length=None,  # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> BlobClient
        """Creates a new blob from a data source with automatic chunking.

        :param name: The blob with which to interact. If specified, this value will override
            a blob value specified in the blob URL.
        :type name: str or ~azure.storage.blob.BlobProperties
        :param data: The blob data to upload.
        :param ~azure.storage.blob.BlobType blob_type: The type of the blob. This can be
            either BlockBlob, PageBlob or AppendBlob. The default value is BlockBlob.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :keyword bool overwrite: Whether the blob to be uploaded should overwrite the current data.
            If True, upload_blob will overwrite the existing data. If set to False, the
            operation will fail with ResourceExistsError. The exception to the above is with Append
            blob types: if set to False and the data already exists, an error will not be raised
            and the data will be appended to the existing blob. If set overwrite=True, then the existing
            append blob will be deleted, and a new one created. Defaults to False.
        :keyword ~azure.storage.blob.ContentSettings content_settings:
            ContentSettings object used to set blob properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :keyword bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https, as https (the default), will
            already validate. Note that this MD5 hash is not stored with the
            blob. Also note that if enabled, the memory-efficient upload algorithm
            will not be used, because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :keyword lease:
            Required if the container has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :keyword ~azure.storage.blob.PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :keyword ~azure.storage.blob.StandardBlobTier standard_blob_tier:
            A standard blob tier value to set the blob to. For this version of the library,
            this is only applicable to block blobs on standard storage accounts.
        :keyword int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :keyword int max_concurrency:
            Maximum number of parallel connections to use when the blob size exceeds
            64MB.
        :keyword ~azure.storage.blob.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :keyword str encryption_scope:
            A predefined encryption scope used to encrypt the data on the service. An encryption
            scope can be created using the Management API and referenced here by name. If a default
            encryption scope has been defined at the container, this value will override it if the
            container-level scope is configured to allow overrides. Otherwise an error will be raised.

            .. versionadded:: 12.2.0

        :keyword str encoding:
            Defaults to UTF-8.
        :returns: A BlobClient to interact with the newly uploaded blob.
        :rtype: ~azure.storage.blob.BlobClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START upload_blob_to_container]
                :end-before: [END upload_blob_to_container]
                :language: python
                :dedent: 8
                :caption: Upload blob to the container.
        """
        blob = self.get_blob_client(name)
        kwargs.setdefault('merge_span', True)
        timeout = kwargs.pop('timeout', None)
        encoding = kwargs.pop('encoding', 'UTF-8')
        blob.upload_blob(
            data,
            blob_type=blob_type,
            length=length,
            metadata=metadata,
            timeout=timeout,
            encoding=encoding,
            **kwargs
        )
        return blob

    @distributed_trace
    def delete_blob(
            self, blob,  # type: Union[str, BlobProperties]
            delete_snapshots=None,  # type: Optional[str]
            **kwargs
        ):
        # type: (...) -> None
        """Marks the specified blob or snapshot for deletion.

        The blob is later deleted during garbage collection.
        Note that in order to delete a blob, you must delete all of its
        snapshots. You can delete both at the same time with the delete_blob
        operation.

        If a delete retention policy is enabled for the service, then this operation soft deletes the blob or snapshot
        and retains the blob or snapshot for specified number of days.
        After specified number of days, blob's data is removed from the service during garbage collection.
        Soft deleted blob or snapshot is accessible through :func:`list_blobs()` specifying `include=["deleted"]`
        option. Soft-deleted blob or snapshot can be restored using :func:`~BlobClient.undelete()`

        :param blob: The blob with which to interact. If specified, this value will override
            a blob value specified in the blob URL.
        :type blob: str or ~azure.storage.blob.BlobProperties
        :param str delete_snapshots:
            Required if the blob has associated snapshots. Values include:
             - "only": Deletes only the blobs snapshots.
             - "include": Deletes the blob along with all snapshots.
        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to delete.

            .. versionadded:: 12.4.0
            This keyword argument was introduced in API version '2019-12-12'.

        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        blob_client = self.get_blob_client(blob) # type: ignore
        kwargs.setdefault('merge_span', True)
        timeout = kwargs.pop('timeout', None)
        blob_client.delete_blob( # type: ignore
            delete_snapshots=delete_snapshots,
            timeout=timeout,
            **kwargs)

    @distributed_trace
    def download_blob(self, blob, offset=None, length=None, **kwargs):
        # type: (Union[str, BlobProperties], Optional[int], Optional[int], **Any) -> StorageStreamDownloader
        """Downloads a blob to the StorageStreamDownloader. The readall() method must
        be used to read all the content or readinto() must be used to download the blob into
        a stream.

        :param blob: The blob with which to interact. If specified, this value will override
            a blob value specified in the blob URL.
        :type blob: str or ~azure.storage.blob.BlobProperties
        :param int offset:
            Start of byte range to use for downloading a section of the blob.
            Must be set if length is provided.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :keyword bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https, as https (the default), will
            already validate. Note that this MD5 hash is not stored with the
            blob. Also note that if enabled, the memory-efficient upload algorithm
            will not be used because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :keyword lease:
            Required if the blob has an active lease. If specified, download_blob only
            succeeds if the blob's lease is active and matches this ID. Value can be a
            BlobLeaseClient object or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword ~azure.storage.blob.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :keyword int max_concurrency:
            The number of parallel connections with which to download.
        :keyword str encoding:
            Encoding to decode the downloaded bytes. Default is None, i.e. no decoding.
        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :returns: A streaming object (StorageStreamDownloader)
        :rtype: ~azure.storage.blob.StorageStreamDownloader
        """
        blob_client = self.get_blob_client(blob) # type: ignore
        kwargs.setdefault('merge_span', True)
        return blob_client.download_blob(offset=offset, length=length, **kwargs)

    def _generate_delete_blobs_subrequest_options(
        self, snapshot=None,
        delete_snapshots=None,
        lease_access_conditions=None,
        modified_access_conditions=None,
        **kwargs
    ):
        """This code is a copy from _generated.

        Once Autorest is able to provide request preparation this code should be removed.
        """
        lease_id = None
        if lease_access_conditions is not None:
            lease_id = lease_access_conditions.lease_id
        if_modified_since = None
        if modified_access_conditions is not None:
            if_modified_since = modified_access_conditions.if_modified_since
        if_unmodified_since = None
        if modified_access_conditions is not None:
            if_unmodified_since = modified_access_conditions.if_unmodified_since
        if_match = None
        if modified_access_conditions is not None:
            if_match = modified_access_conditions.if_match
        if_none_match = None
        if modified_access_conditions is not None:
            if_none_match = modified_access_conditions.if_none_match
        if_tags = None
        if modified_access_conditions is not None:
            if_tags = modified_access_conditions.if_tags

        # Construct parameters
        timeout = kwargs.pop('timeout', None)
        query_parameters = {}
        if snapshot is not None:
            query_parameters['snapshot'] = self._client._serialize.query("snapshot", snapshot, 'str')  # pylint: disable=protected-access
        if timeout is not None:
            query_parameters['timeout'] = self._client._serialize.query("timeout", timeout, 'int', minimum=0)  # pylint: disable=protected-access

        # Construct headers
        header_parameters = {}
        if delete_snapshots is not None:
            header_parameters['x-ms-delete-snapshots'] = self._client._serialize.header(  # pylint: disable=protected-access
                "delete_snapshots", delete_snapshots, 'DeleteSnapshotsOptionType')
        if lease_id is not None:
            header_parameters['x-ms-lease-id'] = self._client._serialize.header(  # pylint: disable=protected-access
                "lease_id", lease_id, 'str')
        if if_modified_since is not None:
            header_parameters['If-Modified-Since'] = self._client._serialize.header(  # pylint: disable=protected-access
                "if_modified_since", if_modified_since, 'rfc-1123')
        if if_unmodified_since is not None:
            header_parameters['If-Unmodified-Since'] = self._client._serialize.header(  # pylint: disable=protected-access
                "if_unmodified_since", if_unmodified_since, 'rfc-1123')
        if if_match is not None:
            header_parameters['If-Match'] = self._client._serialize.header(  # pylint: disable=protected-access
                "if_match", if_match, 'str')
        if if_none_match is not None:
            header_parameters['If-None-Match'] = self._client._serialize.header(  # pylint: disable=protected-access
                "if_none_match", if_none_match, 'str')
        if if_tags is not None:
            header_parameters['x-ms-if-tags'] = self._client._serialize.header("if_tags", if_tags, 'str')  # pylint: disable=protected-access

        return query_parameters, header_parameters

    def _generate_delete_blobs_options(self,
                                       *blobs,  # type: List[Union[str, BlobProperties, dict]]
                                       **kwargs
                                       ):
        timeout = kwargs.pop('timeout', None)
        raise_on_any_failure = kwargs.pop('raise_on_any_failure', True)
        delete_snapshots = kwargs.pop('delete_snapshots', None)
        if_modified_since = kwargs.pop('if_modified_since', None)
        if_unmodified_since = kwargs.pop('if_unmodified_since', None)
        if_tags_match_condition = kwargs.pop('if_tags_match_condition', None)
        kwargs.update({'raise_on_any_failure': raise_on_any_failure,
                       'sas': self._query_str.replace('?', '&'),
                       'timeout': '&timeout=' + str(timeout) if timeout else "",
                       'path': self.container_name,
                       'restype': 'restype=container&'
                       })

        reqs = []
        for blob in blobs:
            blob_name = _get_blob_name(blob)
            container_name = self.container_name

            try:
                options = BlobClient._generic_delete_blob_options(  # pylint: disable=protected-access
                    snapshot=blob.get('snapshot'),
                    delete_snapshots=delete_snapshots or blob.get('delete_snapshots'),
                    lease=blob.get('lease_id'),
                    if_modified_since=if_modified_since or blob.get('if_modified_since'),
                    if_unmodified_since=if_unmodified_since or blob.get('if_unmodified_since'),
                    etag=blob.get('etag'),
                    if_tags_match_condition=if_tags_match_condition or blob.get('if_tags_match_condition'),
                    match_condition=blob.get('match_condition') or MatchConditions.IfNotModified if blob.get('etag')
                    else None,
                    timeout=blob.get('timeout'),
                )
            except AttributeError:
                options = BlobClient._generic_delete_blob_options(  # pylint: disable=protected-access
                    delete_snapshots=delete_snapshots,
                    if_modified_since=if_modified_since,
                    if_unmodified_since=if_unmodified_since,
                    if_tags_match_condition=if_tags_match_condition
                )

            query_parameters, header_parameters = self._generate_delete_blobs_subrequest_options(**options)

            req = HttpRequest(
                "DELETE",
                "/{}/{}{}".format(quote(container_name), quote(blob_name, safe='/~'), self._query_str),
                headers=header_parameters
            )
            req.format_parameters(query_parameters)
            reqs.append(req)

        return reqs, kwargs

    @distributed_trace
    def delete_blobs(self, *blobs, **kwargs):
        # type: (...) -> Iterator[HttpResponse]
        """Marks the specified blobs or snapshots for deletion.

        The blobs are later deleted during garbage collection.
        Note that in order to delete blobs, you must delete all of their
        snapshots. You can delete both at the same time with the delete_blobs operation.

        If a delete retention policy is enabled for the service, then this operation soft deletes the blobs or snapshots
        and retains the blobs or snapshots for specified number of days.
        After specified number of days, blobs' data is removed from the service during garbage collection.
        Soft deleted blobs or snapshots are accessible through :func:`list_blobs()` specifying `include=["deleted"]`
        Soft-deleted blobs or snapshots can be restored using :func:`~BlobClient.undelete()`

        :param blobs:
            The blobs to delete. This can be a single blob, or multiple values can
            be supplied, where each value is either the name of the blob (str) or BlobProperties.

            .. note::
                When the blob type is dict, here's a list of keys, value rules.

                blob name:
                    key: 'name', value type: str
                snapshot you want to delete:
                    key: 'snapshot', value type: str
                whether to delete snapthots when deleting blob:
                    key: 'delete_snapshots', value: 'include' or 'only'
                if the blob modified or not:
                    key: 'if_modified_since', 'if_unmodified_since', value type: datetime
                etag:
                    key: 'etag', value type: str
                match the etag or not:
                    key: 'match_condition', value type: MatchConditions
                tags match condition:
                    key: 'if_tags_match_condition', value type: str
                lease:
                    key: 'lease_id', value type: Union[str, LeaseClient]
                timeout for subrequest:
                    key: 'timeout', value type: int

        :type blobs: list[str], list[dict], or list[~azure.storage.blob.BlobProperties]
        :keyword str delete_snapshots:
            Required if a blob has associated snapshots. Values include:
             - "only": Deletes only the blobs snapshots.
             - "include": Deletes the blob along with all snapshots.
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword bool raise_on_any_failure:
            This is a boolean param which defaults to True. When this is set, an exception
            is raised even if there is a single operation failure.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: An iterator of responses, one for each blob in order
        :rtype: Iterator[~azure.core.pipeline.transport.HttpResponse]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common.py
                :start-after: [START delete_multiple_blobs]
                :end-before: [END delete_multiple_blobs]
                :language: python
                :dedent: 8
                :caption: Deleting multiple blobs.
        """
        if len(blobs) == 0:
            return iter(list())

        reqs, options = self._generate_delete_blobs_options(*blobs, **kwargs)

        return self._batch_send(*reqs, **options)

    def _generate_set_tiers_subrequest_options(
        self, tier, snapshot=None, version_id=None, rehydrate_priority=None, lease_access_conditions=None, **kwargs
    ):
        """This code is a copy from _generated.

        Once Autorest is able to provide request preparation this code should be removed.
        """
        if not tier:
            raise ValueError("A blob tier must be specified")
        if snapshot and version_id:
            raise ValueError("Snapshot and version_id cannot be set at the same time")
        if_tags = kwargs.pop('if_tags', None)

        lease_id = None
        if lease_access_conditions is not None:
            lease_id = lease_access_conditions.lease_id

        comp = "tier"
        timeout = kwargs.pop('timeout', None)
        # Construct parameters
        query_parameters = {}
        if snapshot is not None:
            query_parameters['snapshot'] = self._client._serialize.query("snapshot", snapshot, 'str')  # pylint: disable=protected-access
        if version_id is not None:
            query_parameters['versionid'] = self._client._serialize.query("version_id", version_id, 'str')  # pylint: disable=protected-access
        if timeout is not None:
            query_parameters['timeout'] = self._client._serialize.query("timeout", timeout, 'int', minimum=0)  # pylint: disable=protected-access
        query_parameters['comp'] = self._client._serialize.query("comp", comp, 'str')  # pylint: disable=protected-access, specify-parameter-names-in-call

        # Construct headers
        header_parameters = {}
        header_parameters['x-ms-access-tier'] = self._client._serialize.header("tier", tier, 'str')  # pylint: disable=protected-access, specify-parameter-names-in-call
        if rehydrate_priority is not None:
            header_parameters['x-ms-rehydrate-priority'] = self._client._serialize.header(  # pylint: disable=protected-access
                "rehydrate_priority", rehydrate_priority, 'str')
        if lease_id is not None:
            header_parameters['x-ms-lease-id'] = self._client._serialize.header("lease_id", lease_id, 'str')  # pylint: disable=protected-access
        if if_tags is not None:
            header_parameters['x-ms-if-tags'] = self._client._serialize.header("if_tags", if_tags, 'str')  # pylint: disable=protected-access

        return query_parameters, header_parameters

    def _generate_set_tiers_options(self,
                                    blob_tier,  # type: Optional[Union[str, StandardBlobTier, PremiumPageBlobTier]]
                                    *blobs,  # type: List[Union[str, BlobProperties, dict]]
                                    **kwargs
                                    ):
        timeout = kwargs.pop('timeout', None)
        raise_on_any_failure = kwargs.pop('raise_on_any_failure', True)
        rehydrate_priority = kwargs.pop('rehydrate_priority', None)
        if_tags = kwargs.pop('if_tags_match_condition', None)
        kwargs.update({'raise_on_any_failure': raise_on_any_failure,
                       'sas': self._query_str.replace('?', '&'),
                       'timeout': '&timeout=' + str(timeout) if timeout else "",
                       'path': self.container_name,
                       'restype': 'restype=container&'
                       })

        reqs = []
        for blob in blobs:
            blob_name = _get_blob_name(blob)
            container_name = self.container_name

            try:
                tier = blob_tier or blob.get('blob_tier')
                query_parameters, header_parameters = self._generate_set_tiers_subrequest_options(
                    tier=tier,
                    snapshot=blob.get('snapshot'),
                    version_id=blob.get('version_id'),
                    rehydrate_priority=rehydrate_priority or blob.get('rehydrate_priority'),
                    lease_access_conditions=blob.get('lease_id'),
                    if_tags=if_tags or blob.get('if_tags_match_condition'),
                    timeout=timeout or blob.get('timeout')
                )
            except AttributeError:
                query_parameters, header_parameters = self._generate_set_tiers_subrequest_options(
                    blob_tier, rehydrate_priority=rehydrate_priority, if_tags=if_tags)

            req = HttpRequest(
                "PUT",
                "/{}/{}{}".format(quote(container_name), quote(blob_name, safe='/~'), self._query_str),
                headers=header_parameters
            )
            req.format_parameters(query_parameters)
            reqs.append(req)

        return reqs, kwargs

    @distributed_trace
    def set_standard_blob_tier_blobs(
        self,
        standard_blob_tier,  # type: Optional[Union[str, StandardBlobTier]]
        *blobs,  # type: List[Union[str, BlobProperties, dict]]
        **kwargs
    ):
        # type: (...) -> Iterator[HttpResponse]
        """This operation sets the tier on block blobs.

        A block blob's tier determines Hot/Cool/Archive storage type.
        This operation does not update the blob's ETag.

        :param standard_blob_tier:
            Indicates the tier to be set on all blobs. Options include 'Hot', 'Cool',
            'Archive'. The hot tier is optimized for storing data that is accessed
            frequently. The cool storage tier is optimized for storing data that
            is infrequently accessed and stored for at least a month. The archive
            tier is optimized for storing data that is rarely accessed and stored
            for at least six months with flexible latency requirements.

            .. note::
                If you want to set different tier on different blobs please set this positional parameter to None.
                Then the blob tier on every BlobProperties will be taken.

        :type standard_blob_tier: str or ~azure.storage.blob.StandardBlobTier
        :param blobs:
            The blobs with which to interact. This can be a single blob, or multiple values can
            be supplied, where each value is either the name of the blob (str) or BlobProperties.

            .. note::
                When the blob type is dict, here's a list of keys, value rules.

                blob name:
                    key: 'name', value type: str
                standard blob tier:
                    key: 'blob_tier', value type: StandardBlobTier
                rehydrate priority:
                    key: 'rehydrate_priority', value type: RehydratePriority
                lease:
                    key: 'lease_id', value type: Union[str, LeaseClient]
                snapshot:
                    key: "snapshost", value type: str
                version id:
                    key: "version_id", value type: str
                tags match condition:
                    key: 'if_tags_match_condition', value type: str
                timeout for subrequest:
                    key: 'timeout', value type: int

        :type blobs: list[str], list[dict], or list[~azure.storage.blob.BlobProperties]
        :keyword ~azure.storage.blob.RehydratePriority rehydrate_priority:
            Indicates the priority with which to rehydrate an archived blob
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :keyword bool raise_on_any_failure:
            This is a boolean param which defaults to True. When this is set, an exception
            is raised even if there is a single operation failure.
        :return: An iterator of responses, one for each blob in order
        :rtype: Iterator[~azure.core.pipeline.transport.HttpResponse]
        """
        reqs, options = self._generate_set_tiers_options(standard_blob_tier, *blobs, **kwargs)

        return self._batch_send(*reqs, **options)

    @distributed_trace
    def set_premium_page_blob_tier_blobs(
        self,
        premium_page_blob_tier,  # type: Optional[Union[str, PremiumPageBlobTier]]
        *blobs,  # type: List[Union[str, BlobProperties, dict]]
        **kwargs
    ):
        # type: (...) -> Iterator[HttpResponse]
        """Sets the page blob tiers on all blobs. This API is only supported for page blobs on premium accounts.

        :param premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.

            .. note::
                If you want to set different tier on different blobs please set this positional parameter to None.
                Then the blob tier on every BlobProperties will be taken.

        :type premium_page_blob_tier: ~azure.storage.blob.PremiumPageBlobTier
        :param blobs:
            The blobs with which to interact. This can be a single blob, or multiple values can
            be supplied, where each value is either the name of the blob (str) or BlobProperties.

            .. note::
                When the blob type is dict, here's a list of keys, value rules.

                blob name:
                    key: 'name', value type: str
                premium blob tier:
                    key: 'blob_tier', value type: PremiumPageBlobTier
                lease:
                    key: 'lease_id', value type: Union[str, LeaseClient]
                timeout for subrequest:
                    key: 'timeout', value type: int

        :type blobs: list[str], list[dict], or list[~azure.storage.blob.BlobProperties]
        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :keyword bool raise_on_any_failure:
            This is a boolean param which defaults to True. When this is set, an exception
            is raised even if there is a single operation failure.
        :return: An iterator of responses, one for each blob in order
        :rtype: iterator[~azure.core.pipeline.transport.HttpResponse]
        """
        reqs, options = self._generate_set_tiers_options(premium_page_blob_tier, *blobs, **kwargs)

        return self._batch_send(*reqs, **options)

    def get_blob_client(
            self, blob,  # type: Union[str, BlobProperties]
            snapshot=None  # type: str
        ):
        # type: (...) -> BlobClient
        """Get a client to interact with the specified blob.

        The blob need not already exist.

        :param blob:
            The blob with which to interact.
        :type blob: str or ~azure.storage.blob.BlobProperties
        :param str snapshot:
            The optional blob snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`~BlobClient.create_snapshot()`.
        :returns: A BlobClient.
        :rtype: ~azure.storage.blob.BlobClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers.py
                :start-after: [START get_blob_client]
                :end-before: [END get_blob_client]
                :language: python
                :dedent: 8
                :caption: Get the blob client.
        """
        blob_name = _get_blob_name(blob)
        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return BlobClient(
            self.url, container_name=self.container_name, blob_name=blob_name, snapshot=snapshot,
            credential=self.credential, api_version=self.api_version, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode, _hosts=self._hosts,
            require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
