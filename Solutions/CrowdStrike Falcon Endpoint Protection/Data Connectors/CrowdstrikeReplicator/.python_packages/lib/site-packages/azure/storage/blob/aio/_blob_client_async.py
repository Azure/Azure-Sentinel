# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines, invalid-overridden-method
from functools import partial
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from .._shared.base_client_async import AsyncStorageAccountHostsMixin
from .._shared.policies_async import ExponentialRetry
from .._shared.response_handlers import return_response_headers, process_storage_error
from .._deserialize import get_page_ranges_result, parse_tags, deserialize_pipeline_response_into_cls
from .._serialize import get_modify_conditions, get_api_version, get_access_conditions
from .._generated.aio import AzureBlobStorage
from .._generated.models import CpkInfo
from .._deserialize import deserialize_blob_properties
from .._blob_client import BlobClient as BlobClientBase
from ._upload_helpers import (
    upload_block_blob,
    upload_append_blob,
    upload_page_blob)
from .._models import BlobType, BlobBlock, BlobProperties
from ._lease_async import BlobLeaseClient
from ._download_async import StorageStreamDownloader


if TYPE_CHECKING:
    from datetime import datetime
    from .._models import (  # pylint: disable=unused-import
        ContentSettings,
        PremiumPageBlobTier,
        StandardBlobTier,
        SequenceNumberAction
    )


class BlobClient(AsyncStorageAccountHostsMixin, BlobClientBase):  # pylint: disable=too-many-public-methods
    """A client to interact with a specific blob, although that blob may not yet exist.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the blob,
        use the :func:`from_blob_url` classmethod.
    :param container_name: The container name for the blob.
    :type container_name: str
    :param blob_name: The name of the blob with which to interact. If specified, this value will override
        a blob value specified in the blob URL.
    :type blob_name: str
    :param str snapshot:
        The optional blob snapshot on which to operate. This can be the snapshot ID string
        or the response returned from :func:`create_snapshot`.
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

        .. literalinclude:: ../samples/blob_samples_authentication_async.py
            :start-after: [START create_blob_client]
            :end-before: [END create_blob_client]
            :language: python
            :dedent: 8
            :caption: Creating the BlobClient from a URL to a public blob (no auth needed).

        .. literalinclude:: ../samples/blob_samples_authentication_async.py
            :start-after: [START create_blob_client_sas_url]
            :end-before: [END create_blob_client_sas_url]
            :language: python
            :dedent: 8
            :caption: Creating the BlobClient from a SAS URL to a blob.
    """
    def __init__(
            self, account_url,  # type: str
            container_name,  # type: str
            blob_name,  # type: str
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        kwargs['retry_policy'] = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
        super(BlobClient, self).__init__(
            account_url,
            container_name=container_name,
            blob_name=blob_name,
            snapshot=snapshot,
            credential=credential,
            **kwargs)
        self._client = AzureBlobStorage(url=self.url, pipeline=self._pipeline)
        default_api_version = self._client._config.version  # pylint: disable=protected-access
        self._client._config.version = get_api_version(kwargs, default_api_version)  # pylint: disable=protected-access
        self._loop = kwargs.get('loop', None)

    @distributed_trace_async
    async def get_account_information(self, **kwargs): # type: ignore
        # type: (Optional[int]) -> Dict[str, str]
        """Gets information related to the storage account in which the blob resides.

        The information can also be retrieved if the user has a SAS to a container or blob.
        The keys in the returned dictionary include 'sku_name' and 'account_kind'.

        :returns: A dict of account information (SKU and account type).
        :rtype: dict(str, str)
        """
        try:
            return await self._client.blob.get_account_info(cls=return_response_headers, **kwargs) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_blob_from_url(self, source_url, **kwargs):
        # type: (str, Any) -> Dict[str, Any]
        """
        Creates a new Block Blob where the content of the blob is read from a given URL.
        The content of an existing blob is overwritten with the new blob.

        :param str source_url:
            A URL of up to 2 KB in length that specifies a file or blob.
            The value should be URL-encoded as it would appear in a request URI.
            If the source is in another account, the source must either be public
            or must be authenticated via a shared access signature. If the source
            is public, no authentication is required.
            Examples:
            https://myaccount.blob.core.windows.net/mycontainer/myblob

            https://myaccount.blob.core.windows.net/mycontainer/myblob?snapshot=<DateTime>

            https://otheraccount.blob.core.windows.net/mycontainer/myblob?sastoken
        :keyword bool overwrite: Whether the blob to be uploaded should overwrite the current data.
            If True, upload_blob will overwrite the existing data. If set to False, the
            operation will fail with ResourceExistsError.
        :keyword bool include_source_blob_properties:
            Indicates if properties from the source blob should be copied. Defaults to True.
        :keyword tags:
            Name-value pairs associated with the blob as tag. Tags are case-sensitive.
            The tag set may contain at most 10 tags.  Tag keys must be between 1 and 128 characters,
            and tag values must be between 0 and 256 characters.
            Valid tag key and value characters include: lowercase and uppercase letters, digits (0-9),
            space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals (=), underscore (_)
        :paramtype tags: dict(str, str)
        :keyword bytearray source_content_md5:
            Specify the md5 that is used to verify the integrity of the source bytes.
        :keyword ~datetime.datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the source resource has been modified since the specified time.
        :keyword ~datetime.datetime source_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the source resource has not been modified since the specified date/time.
        :keyword str source_etag:
            The source ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions source_match_condition:
            The source match condition to use upon the etag.
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
            The destination ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The destination match condition to use upon the etag.
        :keyword destination_lease:
            The lease ID specified for this header must match the lease ID of the
            destination blob. If the request does not include the lease ID or it is not
            valid, the operation fails with status code 412 (Precondition Failed).
        :paramtype destination_lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :keyword ~azure.storage.blob.ContentSettings content_settings:
            ContentSettings object used to set blob properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
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
        :keyword ~azure.storage.blob.StandardBlobTier standard_blob_tier:
            A standard blob tier value to set the blob to. For this version of the library,
            this is only applicable to block blobs on standard storage accounts.
        """
        options = self._upload_blob_from_url_options(
            source_url=self._encode_source_url(source_url),
            **kwargs)
        try:
            return await self._client.block_blob.put_blob_from_url(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_blob(
            self, data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            blob_type=BlobType.BlockBlob,  # type: Union[str, BlobType]
            length=None,  # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> Any
        """Creates a new blob from a data source with automatic chunking.

        :param data: The blob data to upload.
        :param ~azure.storage.blob.BlobType blob_type: The type of the blob. This can be
            either BlockBlob, PageBlob or AppendBlob. The default value is BlockBlob.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :keyword tags:
            Name-value pairs associated with the blob as tag. Tags are case-sensitive.
            The tag set may contain at most 10 tags.  Tag keys must be between 1 and 128 characters,
            and tag values must be between 0 and 256 characters.
            Valid tag key and value characters include: lowercase and uppercase letters, digits (0-9),
            space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals (=), underscore (_)

            .. versionadded:: 12.4.0

        :paramtype tags: dict(str, str)
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
            will not be used because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :keyword lease:
            If specified, upload_blob only succeeds if the
            blob's lease is active and matches this ID.
            Required if the blob has an active lease.
        :paramtype: ~azure.storage.blob.aio.BlobLeaseClient
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
        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :returns: Blob-updated property dict (Etag and last modified)
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_hello_world_async.py
                :start-after: [START upload_a_blob]
                :end-before: [END upload_a_blob]
                :language: python
                :dedent: 16
                :caption: Upload a blob to the container.
        """
        options = self._upload_blob_options(
            data,
            blob_type=blob_type,
            length=length,
            metadata=metadata,
            **kwargs)
        if blob_type == BlobType.BlockBlob:
            return await upload_block_blob(**options)
        if blob_type == BlobType.PageBlob:
            return await upload_page_blob(**options)
        return await upload_append_blob(**options)

    @distributed_trace_async
    async def download_blob(self, offset=None, length=None, **kwargs):
        # type: (Optional[int], Optional[int], Any) -> StorageStreamDownloader
        """Downloads a blob to the StorageStreamDownloader. The readall() method must
        be used to read all the content or readinto() must be used to download the blob into
        a stream.

        :param int offset:
            Start of byte range to use for downloading a section of the blob.
            Must be set if length is provided.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to download.

            .. versionadded:: 12.4.0
            This keyword argument was introduced in API version '2019-12-12'.

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
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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
        :rtype: ~azure.storage.blob.aio.StorageStreamDownloader

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_hello_world_async.py
                :start-after: [START download_a_blob]
                :end-before: [END download_a_blob]
                :language: python
                :dedent: 16
                :caption: Download a blob.
        """
        options = self._download_blob_options(
            offset=offset,
            length=length,
            **kwargs)
        downloader = StorageStreamDownloader(**options)
        await downloader._setup()  # pylint: disable=protected-access
        return downloader

    @distributed_trace_async
    async def delete_blob(self, delete_snapshots=None, **kwargs):
        # type: (str, Any) -> None
        """Marks the specified blob for deletion.

        The blob is later deleted during garbage collection.
        Note that in order to delete a blob, you must delete all of its
        snapshots. You can delete both at the same time with the delete_blob()
        operation.

        If a delete retention policy is enabled for the service, then this operation soft deletes the blob
        and retains the blob for a specified number of days.
        After the specified number of days, the blob's data is removed from the service during garbage collection.
        Soft deleted blob is accessible through :func:`~ContainerClient.list_blobs()` specifying `include=['deleted']`
        option. Soft-deleted blob can be restored using :func:`undelete` operation.

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
            Required if the blob has an active lease. If specified, delete_blob only
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_hello_world_async.py
                :start-after: [START delete_blob]
                :end-before: [END delete_blob]
                :language: python
                :dedent: 16
                :caption: Delete a blob.
        """
        options = self._delete_blob_options(delete_snapshots=delete_snapshots, **kwargs)
        try:
            await self._client.blob.delete(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def undelete_blob(self, **kwargs):
        # type: (Any) -> None
        """Restores soft-deleted blobs or snapshots.

        Operation will only be successful if used within the specified number of days
        set in the delete retention policy.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common_async.py
                :start-after: [START undelete_blob]
                :end-before: [END undelete_blob]
                :language: python
                :dedent: 12
                :caption: Undeleting a blob.
        """
        try:
            await self._client.blob.undelete(timeout=kwargs.pop('timeout', None), **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def exists(self, **kwargs):
        # type: (**Any) -> bool
        """
        Returns True if a blob exists with the defined parameters, and returns
        False otherwise.

        :kwarg str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to check if it exists.
        :kwarg int timeout:
            The timeout parameter is expressed in seconds.
        :returns: boolean
        """
        try:
            await self._client.blob.get_properties(
                snapshot=self.snapshot,
                **kwargs)
            return True
        except HttpResponseError as error:
            try:
                process_storage_error(error)
            except ResourceNotFoundError:
                return False

    @distributed_trace_async
    async def get_blob_properties(self, **kwargs):
        # type: (Any) -> BlobProperties
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the blob. It does not return the content of the blob.

        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to get properties.

            .. versionadded:: 12.4.0
            This keyword argument was introduced in API version '2019-12-12'.

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
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: BlobProperties
        :rtype: ~azure.storage.blob.BlobProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common_async.py
                :start-after: [START get_blob_properties]
                :end-before: [END get_blob_properties]
                :language: python
                :dedent: 12
                :caption: Getting the properties for a blob.
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        try:
            cls_method = kwargs.pop('cls', None)
            if cls_method:
                kwargs['cls'] = partial(deserialize_pipeline_response_into_cls, cls_method)
            blob_props = await self._client.blob.get_properties(
                timeout=kwargs.pop('timeout', None),
                version_id=kwargs.pop('version_id', None),
                snapshot=self.snapshot,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=kwargs.pop('cls', None) or deserialize_blob_properties,
                cpk_info=cpk_info,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        blob_props.name = self.blob_name
        if isinstance(blob_props, BlobProperties):
            blob_props.container = self.container_name
            blob_props.snapshot = self.snapshot
        return blob_props # type: ignore

    @distributed_trace_async
    async def set_http_headers(self, content_settings=None, **kwargs):
        # type: (Optional[ContentSettings], Any) -> None
        """Sets system properties on the blob.

        If one property is set for the content_settings, all properties will be overridden.

        :param ~azure.storage.blob.ContentSettings content_settings:
            ContentSettings object used to set blob properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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
        :returns: Blob-updated property dict (Etag and last modified)
        :rtype: Dict[str, Any]
        """
        options = self._set_http_headers_options(content_settings=content_settings, **kwargs)
        try:
            return await self._client.blob.set_http_headers(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_blob_metadata(self, metadata=None, **kwargs):
        # type: (Optional[Dict[str, str]], Any) -> Dict[str, Union[str, datetime]]
        """Sets user-defined metadata for the blob as one or more name-value pairs.

        :param metadata:
            Dict containing name and value pairs. Each call to this operation
            replaces all existing metadata attached to the blob. To remove all
            metadata from the blob, call this operation with no metadata headers.
        :type metadata: dict(str, str)
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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
        :keyword str encryption_scope:
            A predefined encryption scope used to encrypt the data on the service. An encryption
            scope can be created using the Management API and referenced here by name. If a default
            encryption scope has been defined at the container, this value will override it if the
            container-level scope is configured to allow overrides. Otherwise an error will be raised.

            .. versionadded:: 12.2.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag and last modified)
        """
        options = self._set_blob_metadata_options(metadata=metadata, **kwargs)
        try:
            return await self._client.blob.set_metadata(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def create_page_blob(  # type: ignore
            self, size,  # type: int
            content_settings=None,  # type: Optional[ContentSettings]
            metadata=None, # type: Optional[Dict[str, str]]
            premium_page_blob_tier=None,  # type: Optional[Union[str, PremiumPageBlobTier]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """Creates a new Page Blob of the specified size.

        :param int size:
            This specifies the maximum size for the page blob, up to 1 TB.
            The page blob size must be aligned to a 512-byte boundary.
        :param ~azure.storage.blob.ContentSettings content_settings:
            ContentSettings object used to set blob properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param ~azure.storage.blob.PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :keyword tags:
            Name-value pairs associated with the blob as tag. Tags are case-sensitive.
            The tag set may contain at most 10 tags.  Tag keys must be between 1 and 128 characters,
            and tag values must be between 0 and 256 characters.
            Valid tag key and value characters include: lowercase and uppercase letters, digits (0-9),
            space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals (=), underscore (_)

            .. versionadded:: 12.4.0

        :paramtype tags: dict(str, str)
        :keyword int sequence_number:
            Only for Page blobs. The sequence number is a user-controlled value that you can use to
            track requests. The value of the sequence number must be between 0
            and 2^63 - 1.The default value is 0.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]
        """
        options = self._create_page_blob_options(
            size,
            content_settings=content_settings,
            metadata=metadata,
            premium_page_blob_tier=premium_page_blob_tier,
            **kwargs)
        try:
            return await self._client.page_blob.create(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def create_append_blob(self, content_settings=None, metadata=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], Any) -> Dict[str, Union[str, datetime]]
        """Creates a new Append Blob.

        :param ~azure.storage.blob.ContentSettings content_settings:
            ContentSettings object used to set blob properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :keyword tags:
            Name-value pairs associated with the blob as tag. Tags are case-sensitive.
            The tag set may contain at most 10 tags.  Tag keys must be between 1 and 128 characters,
            and tag values must be between 0 and 256 characters.
            Valid tag key and value characters include: lowercase and uppercase letters, digits (0-9),
            space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals (=), underscore (_)

            .. versionadded:: 12.4.0

        :paramtype tags: dict(str, str)
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]
        """
        options = self._create_append_blob_options(
            content_settings=content_settings,
            metadata=metadata,
            **kwargs)
        try:
            return await self._client.append_blob.create(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def create_snapshot(self, metadata=None, **kwargs):
        # type: (Optional[Dict[str, str]], Any) -> Dict[str, Union[str, datetime]]
        """Creates a snapshot of the blob.

        A snapshot is a read-only version of a blob that's taken at a point in time.
        It can be read, copied, or deleted, but not modified. Snapshots provide a way
        to back up a blob as it appears at a moment in time.

        A snapshot of a blob has the same name as the base blob from which the snapshot
        is taken, with a DateTime value appended to indicate the time at which the
        snapshot was taken.

        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
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

        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Snapshot ID, Etag, and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common_async.py
                :start-after: [START create_blob_snapshot]
                :end-before: [END create_blob_snapshot]
                :language: python
                :dedent: 12
                :caption: Create a snapshot of the blob.
        """
        options = self._create_snapshot_options(metadata=metadata, **kwargs)
        try:
            return await self._client.blob.create_snapshot(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def start_copy_from_url(self, source_url, metadata=None, incremental_copy=False, **kwargs):
        # type: (str, Optional[Dict[str, str]], bool, Any) -> Any
        """Copies a blob asynchronously.

        This operation returns a copy operation
        object that can be used to wait on the completion of the operation,
        as well as check status or abort the copy operation.
        The Blob service copies blobs on a best-effort basis.

        The source blob for a copy operation may be a block blob, an append blob,
        or a page blob. If the destination blob already exists, it must be of the
        same blob type as the source blob. Any existing destination blob will be
        overwritten. The destination blob cannot be modified while a copy operation
        is in progress.

        When copying from a page blob, the Blob service creates a destination page
        blob of the source blob's length, initially containing all zeroes. Then
        the source page ranges are enumerated, and non-empty ranges are copied.

        For a block blob or an append blob, the Blob service creates a committed
        blob of zero length before returning from this operation. When copying
        from a block blob, all committed blocks and their block IDs are copied.
        Uncommitted blocks are not copied. At the end of the copy operation, the
        destination blob will have the same committed block count as the source.

        When copying from an append blob, all committed blocks are copied. At the
        end of the copy operation, the destination blob will have the same committed
        block count as the source.

        For all blob types, you can call status() on the returned polling object
        to check the status of the copy operation, or wait() to block until the
        operation is complete. The final blob will be committed when the copy completes.

        :param str source_url:
            A URL of up to 2 KB in length that specifies a file or blob.
            The value should be URL-encoded as it would appear in a request URI.
            If the source is in another account, the source must either be public
            or must be authenticated via a shared access signature. If the source
            is public, no authentication is required.
            Examples:
            https://myaccount.blob.core.windows.net/mycontainer/myblob

            https://myaccount.blob.core.windows.net/mycontainer/myblob?snapshot=<DateTime>

            https://otheraccount.blob.core.windows.net/mycontainer/myblob?sastoken
        :param metadata:
            Name-value pairs associated with the blob as metadata. If no name-value
            pairs are specified, the operation will copy the metadata from the
            source blob or file to the destination blob. If one or more name-value
            pairs are specified, the destination blob is created with the specified
            metadata, and metadata is not copied from the source blob or file.
        :type metadata: dict(str, str)
        :param bool incremental_copy:
            Copies the snapshot of the source page blob to a destination page blob.
            The snapshot is copied such that only the differential changes between
            the previously copied snapshot are transferred to the destination.
            The copied snapshots are complete copies of the original snapshot and
            can be read or copied from as usual. Defaults to False.
        :keyword tags:
            Name-value pairs associated with the blob as tag. Tags are case-sensitive.
            The tag set may contain at most 10 tags.  Tag keys must be between 1 and 128 characters,
            and tag values must be between 0 and 256 characters.
            Valid tag key and value characters include: lowercase and uppercase letters, digits (0-9),
            space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals (=), underscore (_)

            .. versionadded:: 12.4.0

        :paramtype tags: dict(str, str)
        :keyword ~datetime.datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this conditional header to copy the blob only if the source
            blob has been modified since the specified date/time.
        :keyword ~datetime.datetime source_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this conditional header to copy the blob only if the source blob
            has not been modified since the specified date/time.
        :keyword str source_etag:
            The source ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions source_match_condition:
            The source match condition to use upon the etag.
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this conditional header to copy the blob only
            if the destination blob has been modified since the specified date/time.
            If the destination blob has not been modified, the Blob service returns
            status code 412 (Precondition Failed).
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this conditional header to copy the blob only
            if the destination blob has not been modified since the specified
            date/time. If the destination blob has been modified, the Blob service
            returns status code 412 (Precondition Failed).
        :keyword str etag:
            The destination ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The destination match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword destination_lease:
            The lease ID specified for this header must match the lease ID of the
            destination blob. If the request does not include the lease ID or it is not
            valid, the operation fails with status code 412 (Precondition Failed).
        :paramtype destination_lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword source_lease:
            Specify this to perform the Copy Blob operation only if
            the lease ID given matches the active lease ID of the source blob.
        :paramtype source_lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :keyword ~azure.storage.blob.PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :keyword ~azure.storage.blob.StandardBlobTier standard_blob_tier:
            A standard blob tier value to set the blob to. For this version of the library,
            this is only applicable to block blobs on standard storage accounts.
        :keyword ~azure.storage.blob.RehydratePriority rehydrate_priority:
            Indicates the priority with which to rehydrate an archived blob
        :keyword bool seal_destination_blob:
            Seal the destination append blob. This operation is only for append blob.

            .. versionadded:: 12.4.0

        :keyword bool requires_sync:
            Enforces that the service will not return a response until the copy is complete.
        :returns: A dictionary of copy properties (etag, last_modified, copy_id, copy_status).
        :rtype: dict[str, str or ~datetime.datetime]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common_async.py
                :start-after: [START copy_blob_from_url]
                :end-before: [END copy_blob_from_url]
                :language: python
                :dedent: 16
                :caption: Copy a blob from a URL.
        """
        options = self._start_copy_from_url_options(
            source_url=self._encode_source_url(source_url),
            metadata=metadata,
            incremental_copy=incremental_copy,
            **kwargs)
        try:
            if incremental_copy:
                return await self._client.page_blob.copy_incremental(**options)
            return await self._client.blob.start_copy_from_url(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def abort_copy(self, copy_id, **kwargs):
        # type: (Union[str, Dict[str, Any], BlobProperties], Any) -> None
        """Abort an ongoing copy operation.

        This will leave a destination blob with zero length and full metadata.
        This will raise an error if the copy operation has already ended.

        :param copy_id:
            The copy operation to abort. This can be either an ID, or an
            instance of BlobProperties.
        :type copy_id: str or ~azure.storage.blob.BlobProperties
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common_async.py
                :start-after: [START abort_copy_blob_from_url]
                :end-before: [END abort_copy_blob_from_url]
                :language: python
                :dedent: 16
                :caption: Abort copying a blob from URL.
        """
        options = self._abort_copy_options(copy_id, **kwargs)
        try:
            await self._client.blob.abort_copy_from_url(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def acquire_lease(self, lease_duration=-1, lease_id=None, **kwargs):
        # type: (int, Optional[str], Any) -> BlobLeaseClient
        """Requests a new lease.

        If the blob does not have an active lease, the Blob
        Service creates a lease on the blob and returns a new lease.

        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param str lease_id:
            Proposed lease ID, in a GUID string format. The Blob Service
            returns 400 (Invalid request) if the proposed lease ID is not
            in the correct format.
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
        :returns: A BlobLeaseClient object.
        :rtype: ~azure.storage.blob.aio.BlobLeaseClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common_async.py
                :start-after: [START acquire_lease_on_blob]
                :end-before: [END acquire_lease_on_blob]
                :language: python
                :dedent: 12
                :caption: Acquiring a lease on a blob.
        """
        lease = BlobLeaseClient(self, lease_id=lease_id) # type: ignore
        await lease.acquire(lease_duration=lease_duration, **kwargs)
        return lease

    @distributed_trace_async
    async def set_standard_blob_tier(self, standard_blob_tier, **kwargs):
        # type: (Union[str, StandardBlobTier], Any) -> None
        """This operation sets the tier on a block blob.

        A block blob's tier determines Hot/Cool/Archive storage type.
        This operation does not update the blob's ETag.

        :param standard_blob_tier:
            Indicates the tier to be set on the blob. Options include 'Hot', 'Cool',
            'Archive'. The hot tier is optimized for storing data that is accessed
            frequently. The cool storage tier is optimized for storing data that
            is infrequently accessed and stored for at least a month. The archive
            tier is optimized for storing data that is rarely accessed and stored
            for at least six months with flexible latency requirements.
        :type standard_blob_tier: str or ~azure.storage.blob.StandardBlobTier
        :keyword ~azure.storage.blob.RehydratePriority rehydrate_priority:
            Indicates the priority with which to rehydrate an archived blob
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :rtype: None
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if standard_blob_tier is None:
            raise ValueError("A StandardBlobTier must be specified")
        try:
            await self._client.blob.set_tier(
                tier=standard_blob_tier,
                timeout=kwargs.pop('timeout', None),
                modified_access_conditions=mod_conditions,
                lease_access_conditions=access_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def stage_block(
            self, block_id,  # type: str
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Creates a new block to be committed as part of a blob.

        :param str block_id: A string value that identifies the block.
             The string should be less than or equal to 64 bytes in size.
             For a given blob, the block_id must be the same size for each block.
        :param data: The blob data.
        :param int length: Size of the block.
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
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword str encoding:
            Defaults to UTF-8.
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        options = self._stage_block_options(
            block_id,
            data,
            length=length,
            **kwargs)
        try:
            return await self._client.block_blob.stage_block(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def stage_block_from_url(
            self, block_id,  # type: str
            source_url,  # type: str
            source_offset=None,  # type: Optional[int]
            source_length=None,  # type: Optional[int]
            source_content_md5=None,  # type: Optional[Union[bytes, bytearray]]
            **kwargs
        ):
        # type: (...) -> None
        """Creates a new block to be committed as part of a blob where
        the contents are read from a URL.

        :param str block_id: A string value that identifies the block.
             The string should be less than or equal to 64 bytes in size.
             For a given blob, the block_id must be the same size for each block.
        :param str source_url: The URL.
        :param int source_offset:
            Start of byte range to use for the block.
            Must be set if source length is provided.
        :param int source_length: The size of the block in bytes.
        :param bytearray source_content_md5:
            Specify the md5 calculated for the range of
            bytes that must be read from the copy source.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        options = self._stage_block_from_url_options(
            block_id,
            source_url=self._encode_source_url(source_url),
            source_offset=source_offset,
            source_length=source_length,
            source_content_md5=source_content_md5,
            **kwargs)
        try:
            return await self._client.block_blob.stage_block_from_url(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_block_list(self, block_list_type="committed", **kwargs):
        # type: (Optional[str], Any) -> Tuple[List[BlobBlock], List[BlobBlock]]
        """The Get Block List operation retrieves the list of blocks that have
        been uploaded as part of a block blob.

        :param str block_list_type:
            Specifies whether to return the list of committed
            blocks, the list of uncommitted blocks, or both lists together.
            Possible values include: 'committed', 'uncommitted', 'all'
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A tuple of two lists - committed and uncommitted blocks
        :rtype: tuple(list(~azure.storage.blob.BlobBlock), list(~azure.storage.blob.BlobBlock))
        """
        access_conditions = get_access_conditions(kwargs.pop('kease', None))
        mod_conditions = get_modify_conditions(kwargs)
        try:
            blocks = await self._client.block_blob.get_block_list(
                list_type=block_list_type,
                snapshot=self.snapshot,
                timeout=kwargs.pop('timeout', None),
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return self._get_block_list_result(blocks)

    @distributed_trace_async
    async def commit_block_list( # type: ignore
            self, block_list,  # type: List[BlobBlock]
            content_settings=None,  # type: Optional[ContentSettings]
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """The Commit Block List operation writes a blob by specifying the list of
        block IDs that make up the blob.

        :param list block_list:
            List of Blockblobs.
        :param ~azure.storage.blob.ContentSettings content_settings:
            ContentSettings object used to set blob properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict[str, str]
        :keyword tags:
            Name-value pairs associated with the blob as tag. Tags are case-sensitive.
            The tag set may contain at most 10 tags.  Tag keys must be between 1 and 128 characters,
            and tag values must be between 0 and 256 characters.
            Valid tag key and value characters include: lowercase and uppercase letters, digits (0-9),
            space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals (=), underscore (_)

            .. versionadded:: 12.4.0

        :paramtype tags: dict(str, str)
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword bool validate_content:
            If true, calculates an MD5 hash of the page content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https, as https (the default),
            will already validate. Note that this MD5 hash is not stored with the
            blob.
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

        :keyword ~azure.storage.blob.StandardBlobTier standard_blob_tier:
            A standard blob tier value to set the blob to. For this version of the library,
            this is only applicable to block blobs on standard storage accounts.
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        options = self._commit_block_list_options(
            block_list,
            content_settings=content_settings,
            metadata=metadata,
            **kwargs)
        try:
            return await self._client.block_blob.commit_block_list(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_premium_page_blob_tier(self, premium_page_blob_tier, **kwargs):
        # type: (Union[str, PremiumPageBlobTier], **Any) -> None
        """Sets the page blob tiers on the blob. This API is only supported for page blobs on premium accounts.

        :param premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :type premium_page_blob_tier: ~azure.storage.blob.PremiumPageBlobTier
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :rtype: None
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if premium_page_blob_tier is None:
            raise ValueError("A PremiumPageBlobTiermust be specified")
        try:
            await self._client.blob.set_tier(
                tier=premium_page_blob_tier,
                timeout=kwargs.pop('timeout', None),
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_blob_tags(self, tags=None, **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        """The Set Tags operation enables users to set tags on a blob or specific blob version, but not snapshot.
            Each call to this operation replaces all existing tags attached to the blob. To remove all
            tags from the blob, call this operation with no tags set.

        .. versionadded:: 12.4.0
            This operation was introduced in API version '2019-12-12'.

        :param tags:
            Name-value pairs associated with the blob as tag. Tags are case-sensitive.
            The tag set may contain at most 10 tags.  Tag keys must be between 1 and 128 characters,
            and tag values must be between 0 and 256 characters.
            Valid tag key and value characters include: lowercase and uppercase letters, digits (0-9),
            space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals (=), underscore (_)
        :type tags: dict(str, str)
        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to delete.
        :keyword bool validate_content:
            If true, calculates an MD5 hash of the tags content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https, as https (the default),
            will already validate. Note that this MD5 hash is not stored with the
            blob.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag and last modified)
        :rtype: Dict[str, Any]
        """
        options = self._set_blob_tags_options(tags=tags, **kwargs)
        try:
            return await self._client.blob.set_tags(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_blob_tags(self, **kwargs):
        # type: (**Any) -> Dict[str, str]
        """The Get Tags operation enables users to get tags on a blob or specific blob version, but not snapshot.

        .. versionadded:: 12.4.0
            This operation was introduced in API version '2019-12-12'.

        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to add tags to.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Key value pairs of blob tags.
        :rtype: Dict[str, str]
        """
        options = self._get_blob_tags_options(**kwargs)
        try:
            _, tags = await self._client.blob.get_tags(**options)
            return parse_tags(tags)  # pylint: disable=protected-access
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_page_ranges( # type: ignore
            self, offset=None, # type: Optional[int]
            length=None, # type: Optional[int]
            previous_snapshot_diff=None,  # type: Optional[Union[str, Dict[str, Any]]]
            **kwargs
        ):
        # type: (...) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]
        """Returns the list of valid page ranges for a Page Blob or snapshot
        of a page blob.

        :param int offset:
            Start of byte range to use for getting valid page ranges.
            If no length is given, all bytes after the offset will be searched.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length must be a modulus of
            512.
        :param int length:
            Number of bytes to use for getting valid page ranges.
            If length is given, offset must be provided.
            This range will return valid page ranges from the offset start up to
            the specified length.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length must be a modulus of
            512.
        :param str previous_snapshot_diff:
            The snapshot diff parameter that contains an opaque DateTime value that
            specifies a previous blob snapshot to be compared
            against a more recent snapshot or the current blob.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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
        :returns:
            A tuple of two lists of page ranges as dictionaries with 'start' and 'end' keys.
            The first element are filled page ranges, the 2nd element is cleared page ranges.
        :rtype: tuple(list(dict(str, str), list(dict(str, str))
        """
        options = self._get_page_ranges_options(
            offset=offset,
            length=length,
            previous_snapshot_diff=previous_snapshot_diff,
            **kwargs)
        try:
            if previous_snapshot_diff:
                ranges = await self._client.page_blob.get_page_ranges_diff(**options)
            else:
                ranges = await self._client.page_blob.get_page_ranges(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return get_page_ranges_result(ranges)

    @distributed_trace_async
    async def get_page_range_diff_for_managed_disk(
            self, previous_snapshot_url,  # type: str
            offset=None, # type: Optional[int]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]
        """Returns the list of valid page ranges for a managed disk or snapshot.

        .. note::
            This operation is only available for managed disk accounts.

        .. versionadded:: 12.2.0
            This operation was introduced in API version '2019-07-07'.

        :param previous_snapshot_url:
            Specifies the URL of a previous snapshot of the managed disk.
            The response will only contain pages that were changed between the target blob and
            its previous snapshot.
        :param int offset:
            Start of byte range to use for getting valid page ranges.
            If no length is given, all bytes after the offset will be searched.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length must be a modulus of
            512.
        :param int length:
            Number of bytes to use for getting valid page ranges.
            If length is given, offset must be provided.
            This range will return valid page ranges from the offset start up to
            the specified length.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length must be a modulus of
            512.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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
        :returns:
            A tuple of two lists of page ranges as dictionaries with 'start' and 'end' keys.
            The first element are filled page ranges, the 2nd element is cleared page ranges.
        :rtype: tuple(list(dict(str, str), list(dict(str, str))
        """
        options = self._get_page_ranges_options(
            offset=offset,
            length=length,
            prev_snapshot_url=previous_snapshot_url,
            **kwargs)
        try:
            ranges = await self._client.page_blob.get_page_ranges_diff(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return get_page_ranges_result(ranges)

    @distributed_trace_async
    async def set_sequence_number( # type: ignore
            self, sequence_number_action,  # type: Union[str, SequenceNumberAction]
            sequence_number=None,  # type: Optional[str]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets the blob sequence number.

        :param str sequence_number_action:
            This property indicates how the service should modify the blob's sequence
            number. See :class:`~azure.storage.blob.SequenceNumberAction` for more information.
        :param str sequence_number:
            This property sets the blob's sequence number. The sequence number is a
            user-controlled property that you can use to track requests and manage
            concurrency issues.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        options = self._set_sequence_number_options(
            sequence_number_action, sequence_number=sequence_number, **kwargs)
        try:
            return await self._client.page_blob.update_sequence_number(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def resize_blob(self, size, **kwargs):
        # type: (int, Any) -> Dict[str, Union[str, datetime]]
        """Resizes a page blob to the specified size.

        If the specified value is less than the current size of the blob,
        then all pages above the specified value are cleared.

        :param int size:
            Size used to resize blob. Maximum size for a page blob is up to 1 TB.
            The page blob size must be aligned to a 512-byte boundary.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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

        :keyword ~azure.storage.blob.PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        options = self._resize_blob_options(size, **kwargs)
        try:
            return await self._client.page_blob.resize(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_page( # type: ignore
            self, page,  # type: bytes
            offset,  # type: int
            length,  # type: int
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """The Upload Pages operation writes a range of pages to a page blob.

        :param bytes page:
            Content of the page.
        :param int offset:
            Start of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length must be a modulus of
            512.
        :param int length:
            Number of bytes to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length must be a modulus of
            512.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword bool validate_content:
            If true, calculates an MD5 hash of the page content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https, as https (the default),
            will already validate. Note that this MD5 hash is not stored with the
            blob.
        :keyword int if_sequence_number_lte:
            If the blob's sequence number is less than or equal to
            the specified value, the request proceeds; otherwise it fails.
        :keyword int if_sequence_number_lt:
            If the blob's sequence number is less than the specified
            value, the request proceeds; otherwise it fails.
        :keyword int if_sequence_number_eq:
            If the blob's sequence number is equal to the specified
            value, the request proceeds; otherwise it fails.
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
        :keyword str encryption_scope:
            A predefined encryption scope used to encrypt the data on the service. An encryption
            scope can be created using the Management API and referenced here by name. If a default
            encryption scope has been defined at the container, this value will override it if the
            container-level scope is configured to allow overrides. Otherwise an error will be raised.

            .. versionadded:: 12.2.0

        :keyword str encoding:
            Defaults to UTF-8.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        options = self._upload_page_options(
            page=page,
            offset=offset,
            length=length,
            **kwargs)
        try:
            return await self._client.page_blob.upload_pages(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_pages_from_url(self, source_url,  # type: str
                                    offset,  # type: int
                                    length,  # type: int
                                    source_offset,  # type: int
                                    **kwargs
                                    ):
        # type: (...) -> Dict[str, Any]
        """
        The Upload Pages operation writes a range of pages to a page blob where
        the contents are read from a URL.

        :param str source_url:
            The URL of the source data. It can point to any Azure Blob or File, that is either public or has a
            shared access signature attached.
        :param int offset:
            Start of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length  must be a modulus of
            512.
        :param int length:
            Number of bytes to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length must be a modulus of
            512.
        :param int source_offset:
            This indicates the start of the range of bytes(inclusive) that has to be taken from the copy source.
            The service will read the same number of bytes as the destination range (length-offset).
        :keyword bytes source_content_md5:
            If given, the service will calculate the MD5 hash of the block content and compare against this value.
        :keyword ~datetime.datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the source resource has been modified since the specified time.
        :keyword ~datetime.datetime source_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the source resource has not been modified since the specified date/time.
        :keyword str source_etag:
            The source ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions source_match_condition:
            The source match condition to use upon the etag.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword int if_sequence_number_lte:
            If the blob's sequence number is less than or equal to
            the specified value, the request proceeds; otherwise it fails.
        :keyword int if_sequence_number_lt:
            If the blob's sequence number is less than the specified
            value, the request proceeds; otherwise it fails.
        :keyword int if_sequence_number_eq:
            If the blob's sequence number is equal to the specified
            value, the request proceeds; otherwise it fails.
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
            The destination ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The destination match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        """

        options = self._upload_pages_from_url_options(
            source_url=self._encode_source_url(source_url),
            offset=offset,
            length=length,
            source_offset=source_offset,
            **kwargs
        )
        try:
            return await self._client.page_blob.upload_pages_from_url(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def clear_page(self, offset, length, **kwargs):
        # type: (int, int, Any) -> Dict[str, Union[str, datetime]]
        """Clears a range of pages.

        :param int offset:
            Start of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length  must be a modulus of
            512.
        :param int length:
            Number of bytes to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the length must be a modulus of
            512.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword int if_sequence_number_lte:
            If the blob's sequence number is less than or equal to
            the specified value, the request proceeds; otherwise it fails.
        :keyword int if_sequence_number_lt:
            If the blob's sequence number is less than the specified
            value, the request proceeds; otherwise it fails.
        :keyword int if_sequence_number_eq:
            If the blob's sequence number is equal to the specified
            value, the request proceeds; otherwise it fails.
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
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        options = self._clear_page_options(offset, length, **kwargs)
        try:
            return await self._client.page_blob.clear_pages(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def append_block( # type: ignore
            self, data,  # type: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime, int]]
        """Commits a new block of data to the end of the existing append blob.

        :param data:
            Content of the block.
        :param int length:
            Size of the block in bytes.
        :keyword bool validate_content:
            If true, calculates an MD5 hash of the block content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https, as https (the default),
            will already validate. Note that this MD5 hash is not stored with the
            blob.
        :keyword int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :keyword int appendpos_condition:
            Optional conditional header, used only for the Append Block operation.
            A number indicating the byte offset to compare. Append Block will
            succeed only if the append position is equal to this number. If it
            is not, the request will fail with the AppendPositionConditionNotMet error
            (HTTP status code 412 - Precondition Failed).
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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

        :keyword str encoding:
            Defaults to UTF-8.
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag, last modified, append offset, committed block count).
        :rtype: dict(str, Any)
        """
        options = self._append_block_options(
            data,
            length=length,
            **kwargs
        )
        try:
            return await self._client.append_blob.append_block(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async()
    async def append_block_from_url(self, copy_source_url,  # type: str
                                    source_offset=None,  # type: Optional[int]
                                    source_length=None,  # type: Optional[int]
                                    **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime, int]]
        """
        Creates a new block to be committed as part of a blob, where the contents are read from a source url.

        :param str copy_source_url:
            The URL of the source data. It can point to any Azure Blob or File, that is either public or has a
            shared access signature attached.
        :param int source_offset:
            This indicates the start of the range of bytes(inclusive) that has to be taken from the copy source.
        :param int source_length:
            This indicates the end of the range of bytes that has to be taken from the copy source.
        :keyword bytearray source_content_md5:
            If given, the service will calculate the MD5 hash of the block content and compare against this value.
        :keyword int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :keyword int appendpos_condition:
            Optional conditional header, used only for the Append Block operation.
            A number indicating the byte offset to compare. Append Block will
            succeed only if the append position is equal to this number. If it
            is not, the request will fail with the
            AppendPositionConditionNotMet error
            (HTTP status code 412 - Precondition Failed).
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
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
            The destination ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The destination match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword ~datetime.datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the source resource has been modified since the specified time.
        :keyword ~datetime.datetime source_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the source resource has not been modified since the specified date/time.
        :keyword str source_etag:
            The source ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions source_match_condition:
            The source match condition to use upon the etag.
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        """
        options = self._append_block_from_url_options(
            copy_source_url=self._encode_source_url(copy_source_url),
            source_offset=source_offset,
            source_length=source_length,
            **kwargs
        )
        try:
            return await self._client.append_blob.append_block_from_url(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async()
    async def seal_append_blob(self, **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime, int]]
        """The Seal operation seals the Append Blob to make it read-only.

            .. versionadded:: 12.4.0

        :keyword int appendpos_condition:
            Optional conditional header, used only for the Append Block operation.
            A number indicating the byte offset to compare. Append Block will
            succeed only if the append position is equal to this number. If it
            is not, the request will fail with the AppendPositionConditionNotMet error
            (HTTP status code 412 - Precondition Failed).
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
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Blob-updated property dict (Etag, last modified, append offset, committed block count).
        :rtype: dict(str, Any)
        """
        options = self._seal_append_blob_options(**kwargs)
        try:
            return await self._client.append_blob.seal(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)
