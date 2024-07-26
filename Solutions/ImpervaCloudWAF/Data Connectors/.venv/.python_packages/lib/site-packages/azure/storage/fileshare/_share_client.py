# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Optional, Union, Dict, Any, Iterable, TYPE_CHECKING
)
try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote, unquote # type: ignore

import six
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import Pipeline
from ._shared.base_client import StorageAccountHostsMixin, TransportWrapper, parse_connection_str, parse_query
from ._shared.request_handlers import add_metadata_headers, serialize_iso
from ._shared.response_handlers import (
    return_response_headers,
    process_storage_error,
    return_headers_and_deserialized)
from ._generated import AzureFileStorage
from ._generated.version import VERSION
from ._generated.models import (
    StorageErrorException,
    SignedIdentifier,
    DeleteSnapshotsOptionType,
    SharePermission)
from ._deserialize import deserialize_share_properties, deserialize_permission_key, deserialize_permission
from ._serialize import get_api_version
from ._directory_client import ShareDirectoryClient
from ._file_client import ShareFileClient
from ._lease import ShareLeaseClient

if TYPE_CHECKING:
    from ._models import ShareProperties, AccessPolicy


class ShareClient(StorageAccountHostsMixin):
    """A client to interact with a specific share, although that share may not yet exist.

    For operations relating to a specific directory or file in this share, the clients for
    those entities can also be retrieved using the :func:`get_directory_client` and :func:`get_file_client` functions.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the share,
        use the :func:`from_share_url` classmethod.
    :param share_name:
        The name of the share with which to interact.
    :type share_name: str
    :param str snapshot:
        An optional share snapshot on which to operate. This can be the snapshot ID string
        or the response returned from :func:`create_snapshot`.
    :param credential:
        The credential with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string or an account
        shared access key.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-07-07'.
        Setting to an older version may result in reduced feature compatibility.

        .. versionadded:: 12.1.0

    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword int max_range_size: The maximum range size used for a file upload. Defaults to 4*1024*1024.
    """
    def __init__( # type: ignore
            self, account_url,  # type: str
            share_name,  # type: str
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not share_name:
            raise ValueError("Please specify a share name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))
        if hasattr(credential, 'get_token'):
            raise ValueError("Token credentials not supported by the File service.")

        path_snapshot = None
        path_snapshot, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account shared key or SAS token when creating a storage service.')
        try:
            self.snapshot = snapshot.snapshot # type: ignore
        except AttributeError:
            try:
                self.snapshot = snapshot['snapshot'] # type: ignore
            except TypeError:
                self.snapshot = snapshot or path_snapshot

        self.share_name = share_name
        self._query_str, credential = self._format_query_string(
            sas_token, credential, share_snapshot=self.snapshot)
        super(ShareClient, self).__init__(parsed_url, service='file-share', credential=credential, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)
        self._client._config.version = get_api_version(kwargs, VERSION)  # pylint: disable=protected-access

    @classmethod
    def from_share_url(cls, share_url,  # type: str
                       snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
                       credential=None,  # type: Optional[Any]
                       **kwargs  # type: Any
                       ):
        # type: (...) -> ShareClient
        """
        :param str share_url: The full URI to the share.
        :param str snapshot:
            An optional share snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`create_snapshot`.
        :param credential:
            The credential with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string or an account
            shared access key.
        :returns: A share client.
        :rtype: ~azure.storage.fileshare.ShareClient
        """
        try:
            if not share_url.lower().startswith('http'):
                share_url = "https://" + share_url
        except AttributeError:
            raise ValueError("Share URL must be a string.")
        parsed_url = urlparse(share_url.rstrip('/'))
        if not (parsed_url.path and parsed_url.netloc):
            raise ValueError("Invalid URL: {}".format(share_url))

        share_path = parsed_url.path.lstrip('/').split('/')
        account_path = ""
        if len(share_path) > 1:
            account_path = "/" + "/".join(share_path[:-1])
        account_url = "{}://{}{}?{}".format(
            parsed_url.scheme,
            parsed_url.netloc.rstrip('/'),
            account_path,
            parsed_url.query)

        share_name = unquote(share_path[-1])
        path_snapshot, _ = parse_query(parsed_url.query)
        if snapshot:
            try:
                path_snapshot = snapshot.snapshot # type: ignore
            except AttributeError:
                try:
                    path_snapshot = snapshot['snapshot'] # type: ignore
                except TypeError:
                    path_snapshot = snapshot

        if not share_name:
            raise ValueError("Invalid URL. Please provide a URL with a valid share name")
        return cls(account_url, share_name, path_snapshot, credential, **kwargs)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        share_name = self.share_name
        if isinstance(share_name, six.text_type):
            share_name = share_name.encode('UTF-8')
        return "{}://{}/{}{}".format(
            self.scheme,
            hostname,
            quote(share_name),
            self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share_name, # type: str
            snapshot=None,  # type: Optional[str]
            credential=None, # type: Optional[Any]
            **kwargs # type: Any
        ):
        # type: (...) -> ShareClient
        """Create ShareClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param share_name: The name of the share.
        :type share_name: str
        :param str snapshot:
            The optional share snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`create_snapshot`.
        :param credential:
            The credential with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string or an account
            shared access key.
        :returns: A share client.
        :rtype: ~azure.storage.fileshare.ShareClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START create_share_client_from_conn_string]
                :end-before: [END create_share_client_from_conn_string]
                :language: python
                :dedent: 8
                :caption: Gets the share client from connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, share_name=share_name, snapshot=snapshot, credential=credential, **kwargs)

    def get_directory_client(self, directory_path=None):
        # type: (Optional[str]) -> ShareDirectoryClient
        """Get a client to interact with the specified directory.
        The directory need not already exist.

        :param str directory_path:
            Path to the specified directory.
        :returns: A Directory Client.
        :rtype: ~azure.storage.fileshare.ShareDirectoryClient
        """
        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )

        return ShareDirectoryClient(
            self.url, share_name=self.share_name, directory_path=directory_path or "", snapshot=self.snapshot,
            credential=self.credential, api_version=self.api_version,
            _hosts=self._hosts, _configuration=self._config, _pipeline=_pipeline,
            _location_mode=self._location_mode)

    def get_file_client(self, file_path):
        # type: (str) -> ShareFileClient
        """Get a client to interact with the specified file.
        The file need not already exist.

        :param str file_path:
            Path to the specified file.
        :returns: A File Client.
        :rtype: ~azure.storage.fileshare.ShareFileClient
        """
        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )

        return ShareFileClient(
            self.url, share_name=self.share_name, file_path=file_path, snapshot=self.snapshot,
            credential=self.credential, api_version=self.api_version,
            _hosts=self._hosts, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode)

    @distributed_trace
    def _acquire_lease(self, lease_duration=-1, lease_id=None, **kwargs):
        # type: (int, Optional[str], **Any) -> ShareLeaseClient
        """Requests a new lease.

        If the share does not have an active lease, the Share
        Service creates a lease on the share and returns a new lease.

        .. versionadded:: 12.6.0

        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param str lease_id:
            Proposed lease ID, in a GUID string format. The Share Service
            returns 400 (Invalid request) if the proposed lease ID is not
            in the correct format.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A ShareLeaseClient object.
        :rtype: ~azure.storage.fileshare.ShareLeaseClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START acquire_and_release_lease_on_share]
                :end-before: [END acquire_and_release_lease_on_share]
                :language: python
                :dedent: 8
                :caption: Acquiring a lease on a share.
        """
        kwargs['lease_duration'] = lease_duration
        lease = ShareLeaseClient(self, lease_id=lease_id)  # type: ignore
        lease.acquire(**kwargs)
        return lease

    @distributed_trace
    def create_share(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Creates a new Share under the account. If a share with the
        same name already exists, the operation fails.

        :keyword dict(str,str) metadata:
            Name-value pairs associated with the share as metadata.
        :keyword int quota:
            The quota to be allotted.
        :keyword access_tier:
            Specifies the access tier of the share.
            Possible values: 'TransactionOptimized', 'Hot', 'Cool'
        :paramtype access_tier: str or ~azure.storage.fileshare.models.ShareAccessTier

            .. versionadded:: 12.6.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START create_share]
                :end-before: [END create_share]
                :language: python
                :dedent: 8
                :caption: Creates a file share.
        """
        metadata = kwargs.pop('metadata', None)
        quota = kwargs.pop('quota', None)
        access_tier = kwargs.pop('access_tier', None)
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata)) # type: ignore

        try:
            return self._client.share.create( # type: ignore
                timeout=timeout,
                metadata=metadata,
                quota=quota,
                access_tier=access_tier,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def create_snapshot( # type: ignore
            self,
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> Dict[str, Any]
        """Creates a snapshot of the share.

        A snapshot is a read-only version of a share that's taken at a point in time.
        It can be read, copied, or deleted, but not modified. Snapshots provide a way
        to back up a share as it appears at a moment in time.

        A snapshot of a share has the same name as the base share from which the snapshot
        is taken, with a DateTime value appended to indicate the time at which the
        snapshot was taken.

        :keyword dict(str,str) metadata:
            Name-value pairs associated with the share as metadata.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Snapshot ID, Etag, and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START create_share_snapshot]
                :end-before: [END create_share_snapshot]
                :language: python
                :dedent: 12
                :caption: Creates a snapshot of the file share.
        """
        metadata = kwargs.pop('metadata', None)
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata)) # type: ignore
        try:
            return self._client.share.create_snapshot( # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def delete_share(
            self, delete_snapshots=False, # type: Optional[bool]
            **kwargs
        ):
        # type: (...) -> None
        """Marks the specified share for deletion. The share is
        later deleted during garbage collection.

        :param bool delete_snapshots:
            Indicates if snapshots are to be deleted.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START delete_share]
                :end-before: [END delete_share]
                :language: python
                :dedent: 12
                :caption: Deletes the share and any snapshots.
        """
        timeout = kwargs.pop('timeout', None)
        delete_include = None
        if delete_snapshots:
            delete_include = DeleteSnapshotsOptionType.include
        try:
            self._client.share.delete(
                timeout=timeout,
                sharesnapshot=self.snapshot,
                delete_snapshots=delete_include,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def get_share_properties(self, **kwargs):
        # type: (Any) -> ShareProperties
        """Returns all user-defined metadata and system properties for the
        specified share. The data returned does not include the shares's
        list of files or directories.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: The share properties.
        :rtype: ~azure.storage.fileshare.ShareProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_hello_world.py
                :start-after: [START get_share_properties]
                :end-before: [END get_share_properties]
                :language: python
                :dedent: 12
                :caption: Gets the share properties.
        """
        timeout = kwargs.pop('timeout', None)
        try:
            props = self._client.share.get_properties(
                timeout=timeout,
                sharesnapshot=self.snapshot,
                cls=deserialize_share_properties,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        props.name = self.share_name
        props.snapshot = self.snapshot
        return props # type: ignore

    @distributed_trace
    def set_share_quota(self, quota, **kwargs):
        # type: (int, Any) ->  Dict[str, Any]
        """Sets the quota for the share.

        :param int quota:
            Specifies the maximum size of the share, in gigabytes.
            Must be greater than 0, and less than or equal to 5TB.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START set_share_quota]
                :end-before: [END set_share_quota]
                :language: python
                :dedent: 12
                :caption: Sets the share quota.
        """
        timeout = kwargs.pop('timeout', None)
        try:
            return self._client.share.set_properties( # type: ignore
                timeout=timeout,
                quota=quota,
                access_tier=None,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def set_share_properties(self, **kwargs):
        # type: (Any) ->  Dict[str, Any]
        """Sets the share properties.

        .. versionadded:: 12.6.0

        :keyword access_tier:
            Specifies the access tier of the share.
            Possible values: 'TransactionOptimized', 'Hot', and 'Cool'
        :paramtype access_tier: str or ~azure.storage.fileshare.models.ShareAccessTier
        :keyword int quota:
            Specifies the maximum size of the share, in gigabytes.
            Must be greater than 0, and less than or equal to 5TB.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START set_share_properties]
                :end-before: [END set_share_properties]
                :language: python
                :dedent: 12
                :caption: Sets the share properties.
        """
        timeout = kwargs.pop('timeout', None)
        access_tier = kwargs.pop('access_tier', None)
        quota = kwargs.pop('quota', None)
        if all(parameter is None for parameter in [access_tier, quota]):
            raise ValueError("set_share_properties should be called with at least one parameter.")
        try:
            return self._client.share.set_properties( # type: ignore
                timeout=timeout,
                quota=quota,
                access_tier=access_tier,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def set_share_metadata(self, metadata, **kwargs):
        # type: (Dict[str, Any], Any) ->  Dict[str, Any]
        """Sets the metadata for the share.

        Each call to this operation replaces all existing metadata
        attached to the share. To remove all metadata from the share,
        call this operation with no metadata dict.

        :param metadata:
            Name-value pairs associated with the share as metadata.
        :type metadata: dict(str, str)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START set_share_metadata]
                :end-before: [END set_share_metadata]
                :language: python
                :dedent: 12
                :caption: Sets the share metadata.
        """
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return self._client.share.set_metadata( # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def get_share_access_policy(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Gets the permissions for the share. The permissions
        indicate whether files in a share may be accessed publicly.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Access policy information in a dict.
        :rtype: dict[str, Any]
        """
        timeout = kwargs.pop('timeout', None)
        try:
            response, identifiers = self._client.share.get_access_policy(
                timeout=timeout,
                cls=return_headers_and_deserialized,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return {
            'public_access': response.get('share_public_access'),
            'signed_identifiers': identifiers or []
        }

    @distributed_trace
    def set_share_access_policy(self, signed_identifiers, **kwargs):
        # type: (Dict[str, AccessPolicy], Any) -> Dict[str, str]
        """Sets the permissions for the share, or stored access
        policies that may be used with Shared Access Signatures. The permissions
        indicate whether files in a share may be accessed publicly.

        :param signed_identifiers:
            A dictionary of access policies to associate with the share. The
            dictionary may contain up to 5 elements. An empty dictionary
            will clear the access policies set on the service.
        :type signed_identifiers: dict(str, :class:`~azure.storage.fileshare.AccessPolicy`)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        timeout = kwargs.pop('timeout', None)
        if len(signed_identifiers) > 5:
            raise ValueError(
                'Too many access policies provided. The server does not support setting '
                'more than 5 access policies on a single resource.')
        identifiers = []
        for key, value in signed_identifiers.items():
            if value:
                value.start = serialize_iso(value.start)
                value.expiry = serialize_iso(value.expiry)
            identifiers.append(SignedIdentifier(id=key, access_policy=value))
        signed_identifiers = identifiers # type: ignore
        try:
            return self._client.share.set_access_policy( # type: ignore
                share_acl=signed_identifiers or None,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def get_share_stats(self, **kwargs):
        # type: (Any) -> int
        """Gets the approximate size of the data stored on the share in bytes.

        Note that this value may not include all recently created
        or recently re-sized files.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: The approximate size of the data (in bytes) stored on the share.
        :rtype: int
        """
        timeout = kwargs.pop('timeout', None)
        try:
            stats = self._client.share.get_statistics(
                timeout=timeout,
                **kwargs)
            return stats.share_usage_bytes # type: ignore
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def list_directories_and_files(
            self, directory_name=None,  # type: Optional[str]
            name_starts_with=None,  # type: Optional[str]
            marker=None,  # type: Optional[str]
            **kwargs  # type: Any
        ):
        # type: (...) -> Iterable[Dict[str,str]]
        """Lists the directories and files under the share.

        :param str directory_name:
            Name of a directory.
        :param str name_starts_with:
            Filters the results to return only directories whose names
            begin with the specified prefix.
        :param str marker:
            An opaque continuation token. This value can be retrieved from the
            next_marker field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share.py
                :start-after: [START share_list_files_in_dir]
                :end-before: [END share_list_files_in_dir]
                :language: python
                :dedent: 12
                :caption: List directories and files in the share.
        """
        timeout = kwargs.pop('timeout', None)
        directory = self.get_directory_client(directory_name)
        kwargs.setdefault('merge_span', True)
        return directory.list_directories_and_files(
            name_starts_with=name_starts_with, marker=marker, timeout=timeout, **kwargs)

    @staticmethod
    def _create_permission_for_share_options(file_permission,  # type: str
                                             **kwargs):
        options = {
            'share_permission': SharePermission(permission=file_permission),
            'cls': deserialize_permission_key,
            'timeout': kwargs.pop('timeout', None),
        }
        options.update(kwargs)
        return options

    @distributed_trace
    def create_permission_for_share(self, file_permission,  # type: str
                                    **kwargs  # type: Any
                                    ):
        # type: (...) -> str
        """Create a permission (a security descriptor) at the share level.

        This 'permission' can be used for the files/directories in the share.
        If a 'permission' already exists, it shall return the key of it, else
        creates a new permission at the share level and return its key.

        :param str file_permission:
            File permission, a Portable SDDL
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A file permission key
        :rtype: str
        """
        timeout = kwargs.pop('timeout', None)
        options = self._create_permission_for_share_options(file_permission, timeout=timeout, **kwargs)
        try:
            return self._client.share.create_permission(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def get_permission_for_share(  # type: ignore
            self, permission_key,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> str
        """Get a permission (a security descriptor) for a given key.

        This 'permission' can be used for the files/directories in the share.

        :param str permission_key:
            Key of the file permission to retrieve
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A file permission (a portable SDDL)
        :rtype: str
        """
        timeout = kwargs.pop('timeout', None)
        try:
            return self._client.share.get_permission(  # type: ignore
                file_permission_key=permission_key,
                cls=deserialize_permission,
                timeout=timeout,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def create_directory(self, directory_name, **kwargs):
        # type: (str, Any) -> ShareDirectoryClient
        """Creates a directory in the share and returns a client to interact
        with the directory.

        :param str directory_name:
            The name of the directory.
        :keyword metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: ShareDirectoryClient
        :rtype: ~azure.storage.fileshare.ShareDirectoryClient
        """
        directory = self.get_directory_client(directory_name)
        kwargs.setdefault('merge_span', True)
        directory.create_directory(**kwargs)
        return directory # type: ignore

    @distributed_trace
    def delete_directory(self, directory_name, **kwargs):
        # type: (str, Any) -> None
        """Marks the directory for deletion. The directory is
        later deleted during garbage collection.

        :param str directory_name:
            The name of the directory.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        directory = self.get_directory_client(directory_name)
        directory.delete_directory(**kwargs)
