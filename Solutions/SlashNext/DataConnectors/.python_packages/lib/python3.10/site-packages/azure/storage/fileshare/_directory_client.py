# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
import time
from typing import (  # pylint: disable=unused-import
    Optional, Union, Any, Dict, TYPE_CHECKING
)


try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote, unquote # type: ignore

import six
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator import distributed_trace

from ._generated import AzureFileStorage
from ._shared.base_client import StorageAccountHostsMixin, TransportWrapper, parse_connection_str, parse_query
from ._shared.request_handlers import add_metadata_headers
from ._shared.response_handlers import return_response_headers, process_storage_error
from ._shared.parser import _str
from ._parser import _get_file_permission, _datetime_to_str
from ._deserialize import deserialize_directory_properties
from ._serialize import get_api_version
from ._file_client import ShareFileClient
from ._models import DirectoryPropertiesPaged, HandlesPaged, NTFSAttributes  # pylint: disable=unused-import

if TYPE_CHECKING:
    from datetime import datetime
    from ._models import ShareProperties, DirectoryProperties, ContentSettings
    from ._generated.models import HandleItem


class ShareDirectoryClient(StorageAccountHostsMixin):
    """A client to interact with a specific directory, although it may not yet exist.

    For operations relating to a specific subdirectory or file in this share, the clients for those
    entities can also be retrieved using the :func:`get_subdirectory_client` and :func:`get_file_client` functions.

    For more optional configuration, please click
    `here <https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-share
    #optional-configuration>`_.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the directory,
        use the :func:`from_directory_url` classmethod.
    :param share_name:
        The name of the share for the directory.
    :type share_name: str
    :param str directory_path:
        The directory path for the directory with which to interact.
        If specified, this value will override a directory value specified in the directory URL.
    :param str snapshot:
        An optional share snapshot on which to operate. This can be the snapshot ID string
        or the response returned from :func:`ShareClient.create_snapshot`.
    :param credential:
        The credential with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential from azure.core.credentials or an account
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
            share_name, # type: str
            directory_path, # type: str
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None, # type: Optional[Any]
            **kwargs # type: Optional[Any]
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
        self.directory_path = directory_path

        self._query_str, credential = self._format_query_string(
            sas_token, credential, share_snapshot=self.snapshot)
        super(ShareDirectoryClient, self).__init__(parsed_url, service='file-share', credential=credential, **kwargs)
        self._client = AzureFileStorage(url=self.url, pipeline=self._pipeline)
        default_api_version = self._client._config.version  # pylint: disable=protected-access
        self._client._config.version = get_api_version(kwargs, default_api_version)  # pylint: disable=protected-access

    @classmethod
    def from_directory_url(cls, directory_url,  # type: str
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None, # type: Optional[Any]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> ShareDirectoryClient
        """Create a ShareDirectoryClient from a directory url.

        :param str directory_url:
            The full URI to the directory.
        :param str snapshot:
            An optional share snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`ShareClient.create_snapshot`.
        :param credential:
            The credential with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials or an account
            shared access key.
        :returns: A directory client.
        :rtype: ~azure.storage.fileshare.ShareDirectoryClient
        """
        try:
            if not directory_url.lower().startswith('http'):
                directory_url = "https://" + directory_url
        except AttributeError:
            raise ValueError("Directory URL must be a string.")
        parsed_url = urlparse(directory_url.rstrip('/'))
        if not parsed_url.path and not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(directory_url))
        account_url = parsed_url.netloc.rstrip('/') + "?" + parsed_url.query
        path_snapshot, _ = parse_query(parsed_url.query)

        share_name, _, path_dir = parsed_url.path.lstrip('/').partition('/')
        share_name = unquote(share_name)

        directory_path = path_dir
        snapshot = snapshot or path_snapshot

        return cls(
            account_url=account_url, share_name=share_name, directory_path=directory_path,
            credential=credential, **kwargs)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        share_name = self.share_name
        if isinstance(share_name, six.text_type):
            share_name = share_name.encode('UTF-8')
        directory_path = ""
        if self.directory_path:
            directory_path = "/" + quote(self.directory_path, safe='~')
        return "{}://{}/{}{}{}".format(
            self.scheme,
            hostname,
            quote(share_name),
            directory_path,
            self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share_name,  # type: str
            directory_path,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> ShareDirectoryClient
        """Create ShareDirectoryClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param share_name: The name of the share.
        :type share_name: str
        :param str directory_path:
            The directory path.
        :param credential:
            The credential with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials or an account
            shared access key.
        :returns: A directory client.
        :rtype: ~azure.storage.fileshare.ShareDirectoryClient
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, share_name=share_name, directory_path=directory_path, credential=credential, **kwargs)

    def get_file_client(self, file_name, **kwargs):
        # type: (str, Any) -> ShareFileClient
        """Get a client to interact with a specific file.

        The file need not already exist.

        :param file_name:
            The name of the file.
        :returns: A File Client.
        :rtype: ~azure.storage.fileshare.ShareFileClient
        """
        if self.directory_path:
            file_name = self.directory_path.rstrip('/') + "/" + file_name

        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return ShareFileClient(
            self.url, file_path=file_name, share_name=self.share_name, napshot=self.snapshot,
            credential=self.credential, api_version=self.api_version,
            _hosts=self._hosts, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode, **kwargs)

    def get_subdirectory_client(self, directory_name, **kwargs):
        # type: (str, Any) -> ShareDirectoryClient
        """Get a client to interact with a specific subdirectory.

        The subdirectory need not already exist.

        :param str directory_name:
            The name of the subdirectory.
        :returns: A Directory Client.
        :rtype: ~azure.storage.fileshare.ShareDirectoryClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_directory.py
                :start-after: [START get_subdirectory_client]
                :end-before: [END get_subdirectory_client]
                :language: python
                :dedent: 12
                :caption: Gets the subdirectory client.
        """
        directory_path = self.directory_path.rstrip('/') + "/" + directory_name

        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return ShareDirectoryClient(
            self.url, share_name=self.share_name, directory_path=directory_path, snapshot=self.snapshot,
            credential=self.credential, api_version=self.api_version,
            _hosts=self._hosts, _configuration=self._config, _pipeline=_pipeline,
            _location_mode=self._location_mode, **kwargs)

    @distributed_trace
    def create_directory(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Creates a new directory under the directory referenced by the client.

        :keyword dict(str,str) metadata:
            Name-value pairs associated with the directory as metadata.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_directory.py
                :start-after: [START create_directory]
                :end-before: [END create_directory]
                :language: python
                :dedent: 12
                :caption: Creates a directory.
        """
        timeout = kwargs.pop('timeout', None)
        metadata = kwargs.pop('metadata', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata)) # type: ignore
        try:
            return self._client.directory.create( # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def delete_directory(self, **kwargs):
        # type: (**Any) -> None
        """Marks the directory for deletion. The directory is
        later deleted during garbage collection.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_directory.py
                :start-after: [START delete_directory]
                :end-before: [END delete_directory]
                :language: python
                :dedent: 12
                :caption: Deletes a directory.
        """
        timeout = kwargs.pop('timeout', None)
        try:
            self._client.directory.delete(timeout=timeout, **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_directories_and_files(self, name_starts_with=None, **kwargs):
        # type: (Optional[str], **Any) -> ItemPaged
        """Lists all the directories and files under the directory.

        :param str name_starts_with:
            Filters the results to return only entities whose names
            begin with the specified prefix.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties
        :rtype: ~azure.core.paging.ItemPaged[DirectoryProperties and FileProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_directory.py
                :start-after: [START lists_directory]
                :end-before: [END lists_directory]
                :language: python
                :dedent: 12
                :caption: List directories and files.
        """
        timeout = kwargs.pop('timeout', None)
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_files_and_directories_segment,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=DirectoryPropertiesPaged)

    @distributed_trace
    def list_handles(self, recursive=False, **kwargs):
        # type: (bool, Any) -> ItemPaged
        """Lists opened handles on a directory or a file under the directory.

        :param bool recursive:
            Boolean that specifies if operation should apply to the directory specified by the client,
            its files, its subdirectories and their files. Default value is False.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of HandleItem
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.fileshare.HandleItem]
        """
        timeout = kwargs.pop('timeout', None)
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_handles,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            recursive=recursive,
            **kwargs)
        return ItemPaged(
            command, results_per_page=results_per_page,
            page_iterator_class=HandlesPaged)

    @distributed_trace
    def close_handle(self, handle, **kwargs):
        # type: (Union[str, HandleItem], Any) -> Dict[str, int]
        """Close an open file handle.

        :param handle:
            A specific handle to close.
        :type handle: str or ~azure.storage.fileshare.Handle
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns:
            The number of handles closed (this may be 0 if the specified handle was not found)
            and the number of handles failed to close in a dict.
        :rtype: dict[str, int]
        """
        try:
            handle_id = handle.id # type: ignore
        except AttributeError:
            handle_id = handle
        if handle_id == '*':
            raise ValueError("Handle ID '*' is not supported. Use 'close_all_handles' instead.")
        try:
            response = self._client.directory.force_close_handles(
                handle_id,
                marker=None,
                recursive=None,
                sharesnapshot=self.snapshot,
                cls=return_response_headers,
                **kwargs
            )
            return {
                'closed_handles_count': response.get('number_of_handles_closed', 0),
                'failed_handles_count': response.get('number_of_handles_failed', 0)
            }
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def close_all_handles(self, recursive=False, **kwargs):
        # type: (bool, Any) -> Dict[str, int]
        """Close any open file handles.

        This operation will block until the service has closed all open handles.

        :param bool recursive:
            Boolean that specifies if operation should apply to the directory specified by the client,
            its files, its subdirectories and their files. Default value is False.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: The number of handles closed (this may be 0 if the specified handle was not found)
            and the number of handles failed to close in a dict.
        :rtype: dict[str, int]
        """
        timeout = kwargs.pop('timeout', None)
        start_time = time.time()

        try_close = True
        continuation_token = None
        total_closed = 0
        total_failed = 0
        while try_close:
            try:
                response = self._client.directory.force_close_handles(
                    handle_id='*',
                    timeout=timeout,
                    marker=continuation_token,
                    recursive=recursive,
                    sharesnapshot=self.snapshot,
                    cls=return_response_headers,
                    **kwargs
                )
            except HttpResponseError as error:
                process_storage_error(error)
            continuation_token = response.get('marker')
            try_close = bool(continuation_token)
            total_closed += response.get('number_of_handles_closed', 0)
            total_failed += response.get('number_of_handles_failed', 0)
            if timeout:
                timeout = max(0, timeout - (time.time() - start_time))
        return {
            'closed_handles_count': total_closed,
            'failed_handles_count': total_failed
        }

    @distributed_trace
    def get_directory_properties(self, **kwargs):
        # type: (Any) -> DirectoryProperties
        """Returns all user-defined metadata and system properties for the
        specified directory. The data returned does not include the directory's
        list of files.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: DirectoryProperties
        :rtype: ~azure.storage.fileshare.DirectoryProperties
        """
        timeout = kwargs.pop('timeout', None)
        try:
            response = self._client.directory.get_properties(
                timeout=timeout,
                cls=deserialize_directory_properties,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return response # type: ignore

    @distributed_trace
    def set_directory_metadata(self, metadata, **kwargs):
        # type: (Dict[str, Any], Any) ->  Dict[str, Any]
        """Sets the metadata for the directory.

        Each call to this operation replaces all existing metadata
        attached to the directory. To remove all metadata from the directory,
        call this operation with an empty metadata dict.

        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return self._client.directory.set_metadata( # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def set_http_headers(self, file_attributes="none",  # type: Union[str, NTFSAttributes]
                         file_creation_time="preserve",  # type: Union[str, datetime]
                         file_last_write_time="preserve",  # type: Union[str, datetime]
                         file_permission=None,   # type: Optional[str]
                         permission_key=None,   # type: Optional[str]
                         **kwargs  # type: Any
                         ):
        # type: (...) -> Dict[str, Any]
        """Sets HTTP headers on the directory.

        :param file_attributes:
            The file system attributes for files and directories.
            If not set, indicates preservation of existing values.
            Here is an example for when the var type is str: 'Temporary|Archive'
        :type file_attributes: str or :class:`~azure.storage.fileshare.NTFSAttributes`
        :param file_creation_time: Creation time for the file
            Default value: Preserve.
        :type file_creation_time: str or datetime
        :param file_last_write_time: Last write time for the file
            Default value: Preserve.
        :type file_last_write_time: str or datetime
        :param file_permission: If specified the permission (security
            descriptor) shall be set for the directory/file. This header can be
            used if Permission size is <= 8KB, else x-ms-file-permission-key
            header shall be used. Default value: Inherit. If SDDL is specified as
            input, it must have owner, group and dacl. Note: Only one of the
            x-ms-file-permission or x-ms-file-permission-key should be specified.
        :type file_permission: str
        :param permission_key: Key of the permission to be set for the
            directory/file. Note: Only one of the x-ms-file-permission or
            x-ms-file-permission-key should be specified.
        :type permission_key: str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        timeout = kwargs.pop('timeout', None)
        file_permission = _get_file_permission(file_permission, permission_key, 'preserve')
        try:
            return self._client.directory.set_properties(  # type: ignore
                file_attributes=_str(file_attributes),
                file_creation_time=_datetime_to_str(file_creation_time),
                file_last_write_time=_datetime_to_str(file_last_write_time),
                file_permission=file_permission,
                file_permission_key=permission_key,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def create_subdirectory(
            self, directory_name,  # type: str
            **kwargs):
        # type: (...) -> ShareDirectoryClient
        """Creates a new subdirectory and returns a client to interact
        with the subdirectory.

        :param str directory_name:
            The name of the subdirectory.
        :keyword dict(str,str) metadata:
            Name-value pairs associated with the subdirectory as metadata.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: ShareDirectoryClient
        :rtype: ~azure.storage.fileshare.ShareDirectoryClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_directory.py
                :start-after: [START create_subdirectory]
                :end-before: [END create_subdirectory]
                :language: python
                :dedent: 12
                :caption: Create a subdirectory.
        """
        metadata = kwargs.pop('metadata', None)
        timeout = kwargs.pop('timeout', None)
        subdir = self.get_subdirectory_client(directory_name)
        subdir.create_directory(metadata=metadata, timeout=timeout, **kwargs)
        return subdir # type: ignore

    @distributed_trace
    def delete_subdirectory(
            self, directory_name,  # type: str
            **kwargs
        ):
        # type: (...) -> None
        """Deletes a subdirectory.

        :param str directory_name:
            The name of the subdirectory.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_directory.py
                :start-after: [START delete_subdirectory]
                :end-before: [END delete_subdirectory]
                :language: python
                :dedent: 12
                :caption: Delete a subdirectory.
        """
        timeout = kwargs.pop('timeout', None)
        subdir = self.get_subdirectory_client(directory_name)
        subdir.delete_directory(timeout=timeout, **kwargs)

    @distributed_trace
    def upload_file(
            self, file_name,  # type: str
            data, # type: Any
            length=None, # type: Optional[int]
            **kwargs # type: Any
        ):
        # type: (...) -> ShareFileClient
        """Creates a new file in the directory and returns a ShareFileClient
        to interact with the file.

        :param str file_name:
            The name of the file.
        :param Any data:
            Content of the file.
        :param int length:
            Length of the file in bytes. Specify its maximum size, up to 1 TiB.
        :keyword dict(str,str) metadata:
            Name-value pairs associated with the file as metadata.
        :keyword ~azure.storage.fileshare.ContentSettings content_settings:
            ContentSettings object used to set file properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :keyword bool validate_content:
            If true, calculates an MD5 hash for each range of the file. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            file.
        :keyword int max_concurrency:
            Maximum number of parallel connections to use.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :keyword str encoding:
            Defaults to UTF-8.
        :returns: ShareFileClient
        :rtype: ~azure.storage.fileshare.ShareFileClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_directory.py
                :start-after: [START upload_file_to_directory]
                :end-before: [END upload_file_to_directory]
                :language: python
                :dedent: 12
                :caption: Upload a file to a directory.
        """
        file_client = self.get_file_client(file_name)
        file_client.upload_file(
            data,
            length=length,
            **kwargs)
        return file_client # type: ignore

    @distributed_trace
    def delete_file(
            self, file_name,  # type: str
            **kwargs  # type: Optional[Any]
        ):
        # type: (...) -> None
        """Marks the specified file for deletion. The file is later
        deleted during garbage collection.

        :param str file_name:
            The name of the file to delete.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_directory.py
                :start-after: [START delete_file_in_directory]
                :end-before: [END delete_file_in_directory]
                :language: python
                :dedent: 12
                :caption: Delete a file in a directory.
        """
        file_client = self.get_file_client(file_name)
        file_client.delete_file(**kwargs)
