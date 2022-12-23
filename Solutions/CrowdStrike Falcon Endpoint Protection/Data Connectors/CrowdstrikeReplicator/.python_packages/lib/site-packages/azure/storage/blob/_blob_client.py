# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines,no-self-use
from functools import partial
from io import BytesIO
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)
try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse  # type: ignore
    from urllib2 import quote, unquote  # type: ignore

import six
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from ._shared import encode_base64
from ._shared.base_client import StorageAccountHostsMixin, parse_connection_str, parse_query
from ._shared.encryption import generate_blob_encryption_data
from ._shared.uploads import IterStreamer
from ._shared.request_handlers import (
    add_metadata_headers, get_length, read_length,
    validate_and_format_range_headers)
from ._shared.response_handlers import return_response_headers, process_storage_error, return_headers_and_deserialized
from ._generated import AzureBlobStorage
from ._generated.models import ( # pylint: disable=unused-import
    DeleteSnapshotsOptionType,
    BlobHTTPHeaders,
    BlockLookupList,
    AppendPositionAccessConditions,
    SequenceNumberAccessConditions,
    QueryRequest,
    CpkInfo)
from ._serialize import (
    get_modify_conditions,
    get_source_conditions,
    get_cpk_scope_info,
    get_api_version,
    serialize_blob_tags_header,
    serialize_blob_tags,
    serialize_query_format, get_access_conditions
)
from ._deserialize import get_page_ranges_result, deserialize_blob_properties, deserialize_blob_stream, parse_tags, \
    deserialize_pipeline_response_into_cls
from ._quick_query_helper import BlobQueryReader
from ._upload_helpers import (
    upload_block_blob,
    upload_append_blob,
    upload_page_blob, _any_conditions)
from ._models import BlobType, BlobBlock, BlobProperties, BlobQueryError
from ._download import StorageStreamDownloader
from ._lease import BlobLeaseClient

if TYPE_CHECKING:
    from datetime import datetime
    from ._generated.models import BlockList
    from ._models import (  # pylint: disable=unused-import
        ContentSettings,
        PremiumPageBlobTier,
        StandardBlobTier,
        SequenceNumberAction
    )

_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION = (
    'The require_encryption flag is set, but encryption is not supported'
    ' for this method.')


class BlobClient(StorageAccountHostsMixin):  # pylint: disable=too-many-public-methods
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

        .. literalinclude:: ../samples/blob_samples_authentication.py
            :start-after: [START create_blob_client]
            :end-before: [END create_blob_client]
            :language: python
            :dedent: 8
            :caption: Creating the BlobClient from a URL to a public blob (no auth needed).

        .. literalinclude:: ../samples/blob_samples_authentication.py
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
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))

        if not (container_name and blob_name):
            raise ValueError("Please specify a container name and blob name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        path_snapshot, sas_token = parse_query(parsed_url.query)

        self.container_name = container_name
        self.blob_name = blob_name
        try:
            self.snapshot = snapshot.snapshot # type: ignore
        except AttributeError:
            try:
                self.snapshot = snapshot['snapshot'] # type: ignore
            except TypeError:
                self.snapshot = snapshot or path_snapshot

        self._query_str, credential = self._format_query_string(sas_token, credential, snapshot=self.snapshot)
        super(BlobClient, self).__init__(parsed_url, service='blob', credential=credential, **kwargs)
        self._client = AzureBlobStorage(self.url, pipeline=self._pipeline)
        default_api_version = self._client._config.version  # pylint: disable=protected-access
        self._client._config.version = get_api_version(kwargs, default_api_version)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        container_name = self.container_name
        if isinstance(container_name, six.text_type):
            container_name = container_name.encode('UTF-8')
        return "{}://{}/{}/{}{}".format(
            self.scheme,
            hostname,
            quote(container_name),
            quote(self.blob_name, safe='~/'),
            self._query_str)

    def _encode_source_url(self, source_url):
        parsed_source_url = urlparse(source_url)
        source_scheme = parsed_source_url.scheme
        source_hostname = parsed_source_url.netloc.rstrip('/')
        source_path = unquote(parsed_source_url.path)
        source_query = parsed_source_url.query
        result = ["{}://{}{}".format(source_scheme, source_hostname, quote(source_path, safe='~/'))]
        if source_query:
            result.append(source_query)
        return '?'.join(result)

    @classmethod
    def from_blob_url(cls, blob_url, credential=None, snapshot=None, **kwargs):
        # type: (str, Optional[Any], Optional[Union[str, Dict[str, Any]]], Any) -> BlobClient
        """Create BlobClient from a blob url. This doesn't support customized blob url with '/' in blob name.

        :param str blob_url:
            The full endpoint URL to the Blob, including SAS token and snapshot if used. This could be
            either the primary endpoint, or the secondary endpoint depending on the current `location_mode`.
        :type blob_url: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
            - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
        :param str snapshot:
            The optional blob snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`create_snapshot`. If specified, this will override
            the snapshot in the url.
        :returns: A Blob client.
        :rtype: ~azure.storage.blob.BlobClient
        """
        try:
            if not blob_url.lower().startswith('http'):
                blob_url = "https://" + blob_url
        except AttributeError:
            raise ValueError("Blob URL must be a string.")
        parsed_url = urlparse(blob_url.rstrip('/'))

        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(blob_url))

        account_path = ""
        if ".core." in parsed_url.netloc:
            # .core. is indicating non-customized url. Blob name with directory info can also be parsed.
            path_blob = parsed_url.path.lstrip('/').split('/', 1)
        elif "localhost" in parsed_url.netloc or "127.0.0.1" in parsed_url.netloc:
            path_blob = parsed_url.path.lstrip('/').split('/', 2)
            account_path += '/' + path_blob[0]
        else:
            # for customized url. blob name that has directory info cannot be parsed.
            path_blob = parsed_url.path.lstrip('/').split('/')
            if len(path_blob) > 2:
                account_path = "/" + "/".join(path_blob[:-2])
        account_url = "{}://{}{}?{}".format(
            parsed_url.scheme,
            parsed_url.netloc.rstrip('/'),
            account_path,
            parsed_url.query)
        container_name, blob_name = unquote(path_blob[-2]), unquote(path_blob[-1])
        if not container_name or not blob_name:
            raise ValueError("Invalid URL. Provide a blob_url with a valid blob and container name.")

        path_snapshot, _ = parse_query(parsed_url.query)
        if snapshot:
            try:
                path_snapshot = snapshot.snapshot # type: ignore
            except AttributeError:
                try:
                    path_snapshot = snapshot['snapshot'] # type: ignore
                except TypeError:
                    path_snapshot = snapshot

        return cls(
            account_url, container_name=container_name, blob_name=blob_name,
            snapshot=path_snapshot, credential=credential, **kwargs
        )

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            container_name,  # type: str
            blob_name,  # type: str
            snapshot=None,  # type: Optional[str]
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> BlobClient
        """Create BlobClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param container_name: The container name for the blob.
        :type container_name: str
        :param blob_name: The name of the blob with which to interact.
        :type blob_name: str
        :param str snapshot:
            The optional blob snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`create_snapshot`.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :returns: A Blob client.
        :rtype: ~azure.storage.blob.BlobClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_authentication.py
                :start-after: [START auth_from_connection_string_blob]
                :end-before: [END auth_from_connection_string_blob]
                :language: python
                :dedent: 8
                :caption: Creating the BlobClient from a connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'blob')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, container_name=container_name, blob_name=blob_name,
            snapshot=snapshot, credential=credential, **kwargs
        )

    @distributed_trace
    def get_account_information(self, **kwargs):
        # type: (**Any) -> Dict[str, str]
        """Gets information related to the storage account in which the blob resides.

        The information can also be retrieved if the user has a SAS to a container or blob.
        The keys in the returned dictionary include 'sku_name' and 'account_kind'.

        :returns: A dict of account information (SKU and account type).
        :rtype: dict(str, str)
        """
        try:
            return self._client.blob.get_account_info(cls=return_response_headers, **kwargs) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _upload_blob_options(  # pylint:disable=too-many-statements
            self, data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            blob_type=BlobType.BlockBlob,  # type: Union[str, BlobType]
            length=None,  # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")
        encryption_options = {
            'required': self.require_encryption,
            'key': self.key_encryption_key,
            'resolver': self.key_resolver_function,
        }
        if self.key_encryption_key is not None:
            cek, iv, encryption_data = generate_blob_encryption_data(self.key_encryption_key)
            encryption_options['cek'] = cek
            encryption_options['vector'] = iv
            encryption_options['data'] = encryption_data

        encoding = kwargs.pop('encoding', 'UTF-8')
        if isinstance(data, six.text_type):
            data = data.encode(encoding) # type: ignore
        if length is None:
            length = get_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        if isinstance(data, bytes):
            stream = BytesIO(data)
        elif hasattr(data, 'read'):
            stream = data
        elif hasattr(data, '__iter__'):
            stream = IterStreamer(data, encoding=encoding)
        else:
            raise TypeError("Unsupported data type: {}".format(type(data)))

        validate_content = kwargs.pop('validate_content', False)
        content_settings = kwargs.pop('content_settings', None)
        overwrite = kwargs.pop('overwrite', False)
        max_concurrency = kwargs.pop('max_concurrency', 1)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        kwargs['cpk_info'] = cpk_info

        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        kwargs['lease_access_conditions'] = get_access_conditions(kwargs.pop('lease', None))
        kwargs['modified_access_conditions'] = get_modify_conditions(kwargs)
        kwargs['cpk_scope_info'] = get_cpk_scope_info(kwargs)
        if content_settings:
            kwargs['blob_headers'] = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=content_settings.content_md5,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )
        kwargs['blob_tags_string'] = serialize_blob_tags_header(kwargs.pop('tags', None))
        kwargs['stream'] = stream
        kwargs['length'] = length
        kwargs['overwrite'] = overwrite
        kwargs['headers'] = headers
        kwargs['validate_content'] = validate_content
        kwargs['blob_settings'] = self._config
        kwargs['max_concurrency'] = max_concurrency
        kwargs['encryption_options'] = encryption_options
        if blob_type == BlobType.BlockBlob:
            kwargs['client'] = self._client.block_blob
            kwargs['data'] = data
        elif blob_type == BlobType.PageBlob:
            kwargs['client'] = self._client.page_blob
        elif blob_type == BlobType.AppendBlob:
            if self.require_encryption or (self.key_encryption_key is not None):
                raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
            kwargs['client'] = self._client.append_blob
        else:
            raise ValueError("Unsupported BlobType: {}".format(blob_type))
        return kwargs

    def _upload_blob_from_url_options(self, source_url, **kwargs):
        # type: (...) -> Dict[str, Any]
        tier = kwargs.pop('standard_blob_tier', None)
        overwrite = kwargs.pop('overwrite', False)
        content_settings = kwargs.pop('content_settings', None)
        if content_settings:
            kwargs['blob_http_headers'] = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'content_length': 0,
            'copy_source_blob_properties': kwargs.pop('include_source_blob_properties', True),
            'source_content_md5': kwargs.pop('source_content_md5', None),
            'copy_source': source_url,
            'modified_access_conditions': get_modify_conditions(kwargs),
            'blob_tags_string': serialize_blob_tags_header(kwargs.pop('tags', None)),
            'cls': return_response_headers,
            'lease_access_conditions': get_access_conditions(kwargs.pop('destination_lease', None)),
            'tier': tier.value if tier else None,
            'source_modified_access_conditions': get_source_conditions(kwargs),
            'cpk_info': cpk_info,
            'cpk_scope_info': get_cpk_scope_info(kwargs)
        }
        options.update(kwargs)
        if not overwrite and not _any_conditions(**options): # pylint: disable=protected-access
            options['modified_access_conditions'].if_none_match = '*'
        return options

    @distributed_trace
    def upload_blob_from_url(self, source_url, **kwargs):
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
            return self._client.block_blob.put_blob_from_url(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def upload_blob(  # pylint: disable=too-many-locals
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
            Required if the blob has an active lease. If specified, upload_blob only succeeds if the
            blob's lease is active and matches this ID. Value can be a BlobLeaseClient object
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

            .. literalinclude:: ../samples/blob_samples_hello_world.py
                :start-after: [START upload_a_blob]
                :end-before: [END upload_a_blob]
                :language: python
                :dedent: 12
                :caption: Upload a blob to the container.
        """
        options = self._upload_blob_options(
            data,
            blob_type=blob_type,
            length=length,
            metadata=metadata,
            **kwargs)
        if blob_type == BlobType.BlockBlob:
            return upload_block_blob(**options)
        if blob_type == BlobType.PageBlob:
            return upload_page_blob(**options)
        return upload_append_blob(**options)

    def _download_blob_options(self, offset=None, length=None, **kwargs):
        # type: (Optional[int], Optional[int], **Any) -> Dict[str, Any]
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")
        if length is not None and offset is None:
            raise ValueError("Offset value must not be None if length is set.")
        if length is not None:
            length = offset + length - 1  # Service actually uses an end-range inclusive index

        validate_content = kwargs.pop('validate_content', False)
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'clients': self._client,
            'config': self._config,
            'start_range': offset,
            'end_range': length,
            'version_id': kwargs.pop('version_id', None),
            'validate_content': validate_content,
            'encryption_options': {
                'required': self.require_encryption,
                'key': self.key_encryption_key,
                'resolver': self.key_resolver_function},
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'cls': kwargs.pop('cls', None) or deserialize_blob_stream,
            'max_concurrency':kwargs.pop('max_concurrency', 1),
            'encoding': kwargs.pop('encoding', None),
            'timeout': kwargs.pop('timeout', None),
            'name': self.blob_name,
            'container': self.container_name}
        options.update(kwargs)
        return options

    @distributed_trace
    def download_blob(self, offset=None, length=None, **kwargs):
        # type: (Optional[int], Optional[int], **Any) -> StorageStreamDownloader
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_hello_world.py
                :start-after: [START download_a_blob]
                :end-before: [END download_a_blob]
                :language: python
                :dedent: 12
                :caption: Download a blob.
        """
        options = self._download_blob_options(
            offset=offset,
            length=length,
            **kwargs)
        return StorageStreamDownloader(**options)

    def _quick_query_options(self, query_expression,
                             **kwargs):
        # type: (str, **Any) -> Dict[str, Any]
        delimiter = '\n'
        input_format = kwargs.pop('blob_format', None)
        if input_format:
            try:
                delimiter = input_format.lineterminator
            except AttributeError:
                try:
                    delimiter = input_format.delimiter
                except AttributeError:
                    raise ValueError("The Type of blob_format can only be DelimitedTextDialect or DelimitedJsonDialect")
        output_format = kwargs.pop('output_format', None)
        if output_format:
            try:
                delimiter = output_format.lineterminator
            except AttributeError:
                try:
                    delimiter = output_format.delimiter
                except AttributeError:
                    pass
        else:
            output_format = input_format
        query_request = QueryRequest(
            expression=query_expression,
            input_serialization=serialize_query_format(input_format),
            output_serialization=serialize_query_format(output_format)
        )
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(
                encryption_key=cpk.key_value,
                encryption_key_sha256=cpk.key_hash,
                encryption_algorithm=cpk.algorithm
            )
        options = {
            'query_request': query_request,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'snapshot': self.snapshot,
            'timeout': kwargs.pop('timeout', None),
            'cls': return_headers_and_deserialized,
        }
        options.update(kwargs)
        return options, delimiter

    @distributed_trace
    def query_blob(self, query_expression, **kwargs):
        # type: (str, **Any) -> BlobQueryReader
        """Enables users to select/project on blob/or blob snapshot data by providing simple query expressions.
        This operations returns a BlobQueryReader, users need to use readall() or readinto() to get query data.

        :param str query_expression:
            Required. a query statement.
        :keyword Callable[~azure.storage.blob.BlobQueryError] on_error:
            A function to be called on any processing errors returned by the service.
        :keyword blob_format:
            Optional. Defines the serialization of the data currently stored in the blob. The default is to
            treat the blob data as CSV data formatted in the default dialect. This can be overridden with
            a custom DelimitedTextDialect, or alternatively a DelimitedJsonDialect.
        :paramtype blob_format: ~azure.storage.blob.DelimitedTextDialect or ~azure.storage.blob.DelimitedJsonDialect
        :keyword output_format:
            Optional. Defines the output serialization for the data stream. By default the data will be returned
            as it is represented in the blob. By providing an output format, the blob data will be reformatted
            according to that profile. This value can be a DelimitedTextDialect or a DelimitedJsonDialect.
        :paramtype output_format: ~azure.storage.blob.DelimitedTextDialect, ~azure.storage.blob.DelimitedJsonDialect
            or list[~azure.storage.blob.ArrowDialect]
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

        :keyword ~azure.storage.blob.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A streaming object (BlobQueryReader)
        :rtype: ~azure.storage.blob.BlobQueryReader

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_query.py
                :start-after: [START query]
                :end-before: [END query]
                :language: python
                :dedent: 4
                :caption: select/project on blob/or blob snapshot data by providing simple query expressions.
        """
        errors = kwargs.pop("on_error", None)
        error_cls = kwargs.pop("error_cls", BlobQueryError)
        encoding = kwargs.pop("encoding", None)
        options, delimiter = self._quick_query_options(query_expression, **kwargs)
        try:
            headers, raw_response_body = self._client.blob.query(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return BlobQueryReader(
            name=self.blob_name,
            container=self.container_name,
            errors=errors,
            record_delimiter=delimiter,
            encoding=encoding,
            headers=headers,
            response=raw_response_body,
            error_cls=error_cls)

    @staticmethod
    def _generic_delete_blob_options(delete_snapshots=False, **kwargs):
        # type: (bool, **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if delete_snapshots:
            delete_snapshots = DeleteSnapshotsOptionType(delete_snapshots)
        options = {
            'timeout': kwargs.pop('timeout', None),
            'snapshot': kwargs.pop('snapshot', None),  # this is added for delete_blobs
            'delete_snapshots': delete_snapshots or None,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions}
        options.update(kwargs)
        return options

    def _delete_blob_options(self, delete_snapshots=False, **kwargs):
        # type: (bool, **Any) -> Dict[str, Any]
        if self.snapshot and delete_snapshots:
            raise ValueError("The delete_snapshots option cannot be used with a specific snapshot.")
        options = self._generic_delete_blob_options(delete_snapshots, **kwargs)
        options['snapshot'] = self.snapshot
        options['version_id'] = kwargs.pop('version_id', None)
        options['blob_delete_type'] = kwargs.pop('blob_delete_type', None)
        return options

    @distributed_trace
    def delete_blob(self, delete_snapshots=None, **kwargs):
        # type: (str, **Any) -> None
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

            .. literalinclude:: ../samples/blob_samples_hello_world.py
                :start-after: [START delete_blob]
                :end-before: [END delete_blob]
                :language: python
                :dedent: 12
                :caption: Delete a blob.
        """
        options = self._delete_blob_options(delete_snapshots=delete_snapshots, **kwargs)
        try:
            self._client.blob.delete(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def undelete_blob(self, **kwargs):
        # type: (**Any) -> None
        """Restores soft-deleted blobs or snapshots.

        Operation will only be successful if used within the specified number of days
        set in the delete retention policy.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common.py
                :start-after: [START undelete_blob]
                :end-before: [END undelete_blob]
                :language: python
                :dedent: 8
                :caption: Undeleting a blob.
        """
        try:
            self._client.blob.undelete(timeout=kwargs.pop('timeout', None), **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace()
    def exists(self, **kwargs):
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
            self._client.blob.get_properties(
                snapshot=self.snapshot,
                **kwargs)
            return True
        except HttpResponseError as error:
            try:
                process_storage_error(error)
            except ResourceNotFoundError:
                return False

    @distributed_trace
    def get_blob_properties(self, **kwargs):
        # type: (**Any) -> BlobProperties
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the blob. It does not return the content of the blob.

        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
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

            .. literalinclude:: ../samples/blob_samples_common.py
                :start-after: [START get_blob_properties]
                :end-before: [END get_blob_properties]
                :language: python
                :dedent: 8
                :caption: Getting the properties for a blob.
        """
        # TODO: extract this out as _get_blob_properties_options
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
            blob_props = self._client.blob.get_properties(
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

    def _set_http_headers_options(self, content_settings=None, **kwargs):
        # type: (Optional[ContentSettings], **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        blob_headers = None
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=content_settings.content_md5,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )
        options = {
            'timeout': kwargs.pop('timeout', None),
            'blob_http_headers': blob_headers,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def set_http_headers(self, content_settings=None, **kwargs):
        # type: (Optional[ContentSettings], **Any) -> None
        """Sets system properties on the blob.

        If one property is set for the content_settings, all properties will be overridden.

        :param ~azure.storage.blob.ContentSettings content_settings:
            ContentSettings object used to set blob properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
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
        :returns: Blob-updated property dict (Etag and last modified)
        :rtype: Dict[str, Any]
        """
        options = self._set_http_headers_options(content_settings=content_settings, **kwargs)
        try:
            return self._client.blob.set_http_headers(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _set_blob_metadata_options(self, metadata=None, **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
            'headers': headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def set_blob_metadata(self, metadata=None, **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Union[str, datetime]]
        """Sets user-defined metadata for the blob as one or more name-value pairs.

        :param metadata:
            Dict containing name and value pairs. Each call to this operation
            replaces all existing metadata attached to the blob. To remove all
            metadata from the blob, call this operation with no metadata headers.
        :type metadata: dict(str, str)
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
            return self._client.blob.set_metadata(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _create_page_blob_options(  # type: ignore
            self, size,  # type: int
            content_settings=None,  # type: Optional[ContentSettings]
            metadata=None, # type: Optional[Dict[str, str]]
            premium_page_blob_tier=None,  # type: Optional[Union[str, PremiumPageBlobTier]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        blob_headers = None
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=content_settings.content_md5,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )

        sequence_number = kwargs.pop('sequence_number', None)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        if premium_page_blob_tier:
            try:
                headers['x-ms-access-tier'] = premium_page_blob_tier.value  # type: ignore
            except AttributeError:
                headers['x-ms-access-tier'] = premium_page_blob_tier  # type: ignore

        blob_tags_string = serialize_blob_tags_header(kwargs.pop('tags', None))

        options = {
            'content_length': 0,
            'blob_content_length': size,
            'blob_sequence_number': sequence_number,
            'blob_http_headers': blob_headers,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'blob_tags_string': blob_tags_string,
            'cls': return_response_headers,
            'headers': headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def create_page_blob(  # type: ignore
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
            return self._client.page_blob.create(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _create_append_blob_options(self, content_settings=None, metadata=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        blob_headers = None
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=content_settings.content_md5,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        blob_tags_string = serialize_blob_tags_header(kwargs.pop('tags', None))

        options = {
            'content_length': 0,
            'blob_http_headers': blob_headers,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'blob_tags_string': blob_tags_string,
            'cls': return_response_headers,
            'headers': headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def create_append_blob(self, content_settings=None, metadata=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Union[str, datetime]]
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
            return self._client.append_blob.create(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _create_snapshot_options(self, metadata=None, **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
            'headers': headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def create_snapshot(self, metadata=None, **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Union[str, datetime]]
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
            Specify a SQL where clause on blob tags to operate only on destination blob with a matching value.

            .. versionadded:: 12.4.0

        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
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

            .. literalinclude:: ../samples/blob_samples_common.py
                :start-after: [START create_blob_snapshot]
                :end-before: [END create_blob_snapshot]
                :language: python
                :dedent: 8
                :caption: Create a snapshot of the blob.
        """
        options = self._create_snapshot_options(metadata=metadata, **kwargs)
        try:
            return self._client.blob.create_snapshot(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _start_copy_from_url_options(self, source_url, metadata=None, incremental_copy=False, **kwargs):
        # type: (str, Optional[Dict[str, str]], bool, **Any) -> Dict[str, Any]
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        if 'source_lease' in kwargs:
            source_lease = kwargs.pop('source_lease')
            try:
                headers['x-ms-source-lease-id'] = source_lease.id # type: str
            except AttributeError:
                headers['x-ms-source-lease-id'] = source_lease

        tier = kwargs.pop('premium_page_blob_tier', None) or kwargs.pop('standard_blob_tier', None)

        if kwargs.get('requires_sync'):
            headers['x-ms-requires-sync'] = str(kwargs.pop('requires_sync'))

        timeout = kwargs.pop('timeout', None)
        dest_mod_conditions = get_modify_conditions(kwargs)
        blob_tags_string = serialize_blob_tags_header(kwargs.pop('tags', None))

        options = {
            'copy_source': source_url,
            'seal_blob': kwargs.pop('seal_destination_blob', None),
            'timeout': timeout,
            'modified_access_conditions': dest_mod_conditions,
            'blob_tags_string': blob_tags_string,
            'headers': headers,
            'cls': return_response_headers,
        }
        if not incremental_copy:
            source_mod_conditions = get_source_conditions(kwargs)
            dest_access_conditions = get_access_conditions(kwargs.pop('destination_lease', None))
            options['source_modified_access_conditions'] = source_mod_conditions
            options['lease_access_conditions'] = dest_access_conditions
            options['tier'] = tier.value if tier else None
        options.update(kwargs)
        return options

    @distributed_trace
    def start_copy_from_url(self, source_url, metadata=None, incremental_copy=False, **kwargs):
        # type: (str, Optional[Dict[str, str]], bool, **Any) -> Dict[str, Union[str, datetime]]
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
        :keyword destination_lease:
            The lease ID specified for this header must match the lease ID of the
            destination blob. If the request does not include the lease ID or it is not
            valid, the operation fails with status code 412 (Precondition Failed).
        :paramtype destination_lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword source_lease:
            Specify this to perform the Copy Blob operation only if
            the lease ID given matches the active lease ID of the source blob.
        :paramtype source_lease: ~azure.storage.blob.BlobLeaseClient or str
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

            .. literalinclude:: ../samples/blob_samples_common.py
                :start-after: [START copy_blob_from_url]
                :end-before: [END copy_blob_from_url]
                :language: python
                :dedent: 12
                :caption: Copy a blob from a URL.
        """
        options = self._start_copy_from_url_options(
            source_url=self._encode_source_url(source_url),
            metadata=metadata,
            incremental_copy=incremental_copy,
            **kwargs)
        try:
            if incremental_copy:
                return self._client.page_blob.copy_incremental(**options)
            return self._client.blob.start_copy_from_url(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    def _abort_copy_options(self, copy_id, **kwargs):
        # type: (Union[str, Dict[str, Any], BlobProperties], **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        try:
            copy_id = copy_id.copy.id
        except AttributeError:
            try:
                copy_id = copy_id['copy_id']
            except TypeError:
                pass
        options = {
            'copy_id': copy_id,
            'lease_access_conditions': access_conditions,
            'timeout': kwargs.pop('timeout', None)}
        options.update(kwargs)
        return options

    @distributed_trace
    def abort_copy(self, copy_id, **kwargs):
        # type: (Union[str, Dict[str, Any], BlobProperties], **Any) -> None
        """Abort an ongoing copy operation.

        This will leave a destination blob with zero length and full metadata.
        This will raise an error if the copy operation has already ended.

        :param copy_id:
            The copy operation to abort. This can be either an ID string, or an
            instance of BlobProperties.
        :type copy_id: str or ~azure.storage.blob.BlobProperties
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common.py
                :start-after: [START abort_copy_blob_from_url]
                :end-before: [END abort_copy_blob_from_url]
                :language: python
                :dedent: 12
                :caption: Abort copying a blob from URL.
        """
        options = self._abort_copy_options(copy_id, **kwargs)
        try:
            self._client.blob.abort_copy_from_url(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def acquire_lease(self, lease_duration=-1, lease_id=None, **kwargs):
        # type: (int, Optional[str], **Any) -> BlobLeaseClient
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
        :rtype: ~azure.storage.blob.BlobLeaseClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common.py
                :start-after: [START acquire_lease_on_blob]
                :end-before: [END acquire_lease_on_blob]
                :language: python
                :dedent: 8
                :caption: Acquiring a lease on a blob.
        """
        lease = BlobLeaseClient(self, lease_id=lease_id) # type: ignore
        lease.acquire(lease_duration=lease_duration, **kwargs)
        return lease

    @distributed_trace
    def set_standard_blob_tier(self, standard_blob_tier, **kwargs):
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
        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to download.

            .. versionadded:: 12.4.0
            This keyword argument was introduced in API version '2019-12-12'.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :rtype: None
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if standard_blob_tier is None:
            raise ValueError("A StandardBlobTier must be specified")
        if self.snapshot and kwargs.get('version_id'):
            raise ValueError("Snapshot and version_id cannot be set at the same time")
        try:
            self._client.blob.set_tier(
                tier=standard_blob_tier,
                snapshot=self.snapshot,
                timeout=kwargs.pop('timeout', None),
                modified_access_conditions=mod_conditions,
                lease_access_conditions=access_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    def _stage_block_options(
            self, block_id,  # type: str
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        block_id = encode_base64(str(block_id))
        if isinstance(data, six.text_type):
            data = data.encode(kwargs.pop('encoding', 'UTF-8'))  # type: ignore
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        if length is None:
            length = get_length(data)
            if length is None:
                length, data = read_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        validate_content = kwargs.pop('validate_content', False)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'block_id': block_id,
            'content_length': length,
            'body': data,
            'transactional_content_md5': None,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'validate_content': validate_content,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
        }
        options.update(kwargs)
        return options

    @distributed_trace
    def stage_block(
            self, block_id,  # type: str
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
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
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
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
        :returns: Blob property dict.
        :rtype: dict[str, Any]
        """
        options = self._stage_block_options(
            block_id,
            data,
            length=length,
            **kwargs)
        try:
            return self._client.block_blob.stage_block(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    def _stage_block_from_url_options(
            self, block_id,  # type: str
            source_url,  # type: str
            source_offset=None,  # type: Optional[int]
            source_length=None,  # type: Optional[int]
            source_content_md5=None,  # type: Optional[Union[bytes, bytearray]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if source_length is not None and source_offset is None:
            raise ValueError("Source offset value must not be None if length is set.")
        if source_length is not None:
            source_length = source_offset + source_length - 1
        block_id = encode_base64(str(block_id))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        range_header = None
        if source_offset is not None:
            range_header, _ = validate_and_format_range_headers(source_offset, source_length)

        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'block_id': block_id,
            'content_length': 0,
            'source_url': source_url,
            'source_range': range_header,
            'source_content_md5': bytearray(source_content_md5) if source_content_md5 else None,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
        }
        options.update(kwargs)
        return options

    @distributed_trace
    def stage_block_from_url(
            self, block_id,  # type: str
            source_url,  # type: str
            source_offset=None,  # type: Optional[int]
            source_length=None,  # type: Optional[int]
            source_content_md5=None,  # type: Optional[Union[bytes, bytearray]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
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
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
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
        :returns: Blob property dict.
        :rtype: dict[str, Any]
        """
        options = self._stage_block_from_url_options(
            block_id,
            source_url=self._encode_source_url(source_url),
            source_offset=source_offset,
            source_length=source_length,
            source_content_md5=source_content_md5,
            **kwargs)
        try:
            return self._client.block_blob.stage_block_from_url(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    def _get_block_list_result(self, blocks):
        # type: (BlockList) -> Tuple[List[BlobBlock], List[BlobBlock]]
        committed = [] # type: List
        uncommitted = [] # type: List
        if blocks.committed_blocks:
            committed = [BlobBlock._from_generated(b) for b in blocks.committed_blocks]  # pylint: disable=protected-access
        if blocks.uncommitted_blocks:
            uncommitted = [BlobBlock._from_generated(b) for b in blocks.uncommitted_blocks]  # pylint: disable=protected-access
        return committed, uncommitted

    @distributed_trace
    def get_block_list(self, block_list_type="committed", **kwargs):
        # type: (Optional[str], **Any) -> Tuple[List[BlobBlock], List[BlobBlock]]
        """The Get Block List operation retrieves the list of blocks that have
        been uploaded as part of a block blob.

        :param str block_list_type:
            Specifies whether to return the list of committed
            blocks, the list of uncommitted blocks, or both lists together.
            Possible values include: 'committed', 'uncommitted', 'all'
        :keyword lease:
            Required if the blob has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on destination blob with a matching value.

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A tuple of two lists - committed and uncommitted blocks
        :rtype: tuple(list(~azure.storage.blob.BlobBlock), list(~azure.storage.blob.BlobBlock))
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        try:
            blocks = self._client.block_blob.get_block_list(
                list_type=block_list_type,
                snapshot=self.snapshot,
                timeout=kwargs.pop('timeout', None),
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return self._get_block_list_result(blocks)

    def _commit_block_list_options( # type: ignore
            self, block_list,  # type: List[BlobBlock]
            content_settings=None,  # type: Optional[ContentSettings]
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
        for block in block_list:
            try:
                if block.state.value == 'committed':
                    block_lookup.committed.append(encode_base64(str(block.id)))
                elif block.state.value == 'uncommitted':
                    block_lookup.uncommitted.append(encode_base64(str(block.id)))
                else:
                    block_lookup.latest.append(encode_base64(str(block.id)))
            except AttributeError:
                block_lookup.latest.append(encode_base64(str(block)))
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        blob_headers = None
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=content_settings.content_md5,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )

        validate_content = kwargs.pop('validate_content', False)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        tier = kwargs.pop('standard_blob_tier', None)
        blob_tags_string = serialize_blob_tags_header(kwargs.pop('tags', None))

        options = {
            'blocks': block_lookup,
            'blob_http_headers': blob_headers,
            'lease_access_conditions': access_conditions,
            'timeout': kwargs.pop('timeout', None),
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers,
            'validate_content': validate_content,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'tier': tier.value if tier else None,
            'blob_tags_string': blob_tags_string,
            'headers': headers
        }
        options.update(kwargs)
        return options

    @distributed_trace
    def commit_block_list( # type: ignore
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
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
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
            Specify a SQL where clause on blob tags to operate only on destination blob with a matching value.

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
            return self._client.block_blob.commit_block_list(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def set_premium_page_blob_tier(self, premium_page_blob_tier, **kwargs):
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
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :rtype: None
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if premium_page_blob_tier is None:
            raise ValueError("A PremiumPageBlobTier must be specified")
        try:
            self._client.blob.set_tier(
                tier=premium_page_blob_tier,
                timeout=kwargs.pop('timeout', None),
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    def _set_blob_tags_options(self, tags=None, **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        tags = serialize_blob_tags(tags)
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)

        options = {
            'tags': tags,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def set_blob_tags(self, tags=None, **kwargs):
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
            value that, when present, specifies the version of the blob to add tags to.
        :keyword bool validate_content:
            If true, calculates an MD5 hash of the tags content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https, as https (the default),
            will already validate. Note that this MD5 hash is not stored with the
            blob.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on destination blob with a matching value.
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
            return self._client.blob.set_tags(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    def _get_blob_tags_options(self, **kwargs):
        # type: (**Any) -> Dict[str, str]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)

        options = {
            'version_id': kwargs.pop('version_id', None),
            'snapshot': self.snapshot,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'timeout': kwargs.pop('timeout', None),
            'cls': return_headers_and_deserialized}
        return options

    @distributed_trace
    def get_blob_tags(self, **kwargs):
        # type: (**Any) -> Dict[str, str]
        """The Get Tags operation enables users to get tags on a blob or specific blob version, or snapshot.

        .. versionadded:: 12.4.0
            This operation was introduced in API version '2019-12-12'.

        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to add tags to.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on destination blob with a matching value.
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
            _, tags = self._client.blob.get_tags(**options)
            return parse_tags(tags) # pylint: disable=protected-access
        except HttpResponseError as error:
            process_storage_error(error)

    def _get_page_ranges_options( # type: ignore
            self, offset=None, # type: Optional[int]
            length=None, # type: Optional[int]
            previous_snapshot_diff=None,  # type: Optional[Union[str, Dict[str, Any]]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if length is not None and offset is None:
            raise ValueError("Offset value must not be None if length is set.")
        if length is not None:
            length = offset + length - 1  # Reformat to an inclusive range index
        page_range, _ = validate_and_format_range_headers(
            offset, length, start_range_required=False, end_range_required=False, align_to_page=True
        )
        options = {
            'snapshot': self.snapshot,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'timeout': kwargs.pop('timeout', None),
            'range': page_range}
        if previous_snapshot_diff:
            try:
                options['prevsnapshot'] = previous_snapshot_diff.snapshot # type: ignore
            except AttributeError:
                try:
                    options['prevsnapshot'] = previous_snapshot_diff['snapshot'] # type: ignore
                except TypeError:
                    options['prevsnapshot'] = previous_snapshot_diff
        options.update(kwargs)
        return options

    @distributed_trace
    def get_page_ranges( # type: ignore
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
                ranges = self._client.page_blob.get_page_ranges_diff(**options)
            else:
                ranges = self._client.page_blob.get_page_ranges(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return get_page_ranges_result(ranges)

    @distributed_trace
    def get_page_range_diff_for_managed_disk(
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
            ranges = self._client.page_blob.get_page_ranges_diff(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return get_page_ranges_result(ranges)

    def _set_sequence_number_options(self, sequence_number_action, sequence_number=None, **kwargs):
        # type: (Union[str, SequenceNumberAction], Optional[str], **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if sequence_number_action is None:
            raise ValueError("A sequence number action must be specified")
        options = {
            'sequence_number_action': sequence_number_action,
            'timeout': kwargs.pop('timeout', None),
            'blob_sequence_number': sequence_number,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def set_sequence_number(self, sequence_number_action, sequence_number=None, **kwargs):
        # type: (Union[str, SequenceNumberAction], Optional[str], **Any) -> Dict[str, Union[str, datetime]]
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
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        options = self._set_sequence_number_options(
            sequence_number_action, sequence_number=sequence_number, **kwargs)
        try:
            return self._client.page_blob.update_sequence_number(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _resize_blob_options(self, size, **kwargs):
        # type: (int, **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if size is None:
            raise ValueError("A content length must be specified for a Page Blob.")

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'blob_content_length': size,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def resize_blob(self, size, **kwargs):
        # type: (int, **Any) -> Dict[str, Union[str, datetime]]
        """Resizes a page blob to the specified size.

        If the specified value is less than the current size of the blob,
        then all pages above the specified value are cleared.

        :param int size:
            Size used to resize blob. Maximum size for a page blob is up to 1 TB.
            The page blob size must be aligned to a 512-byte boundary.
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
            return self._client.page_blob.resize(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _upload_page_options( # type: ignore
            self, page,  # type: bytes
            offset,  # type: int
            length,  # type: int
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if isinstance(page, six.text_type):
            page = page.encode(kwargs.pop('encoding', 'UTF-8'))
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        if offset is None or offset % 512 != 0:
            raise ValueError("offset must be an integer that aligns with 512 page size")
        if length is None or length % 512 != 0:
            raise ValueError("length must be an integer that aligns with 512 page size")
        end_range = offset + length - 1  # Reformat to an inclusive range index
        content_range = 'bytes={0}-{1}'.format(offset, end_range) # type: ignore
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        seq_conditions = SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=kwargs.pop('if_sequence_number_lte', None),
            if_sequence_number_less_than=kwargs.pop('if_sequence_number_lt', None),
            if_sequence_number_equal_to=kwargs.pop('if_sequence_number_eq', None)
        )
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        validate_content = kwargs.pop('validate_content', False)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'body': page[:length],
            'content_length': length,
            'transactional_content_md5': None,
            'timeout': kwargs.pop('timeout', None),
            'range': content_range,
            'lease_access_conditions': access_conditions,
            'sequence_number_access_conditions': seq_conditions,
            'modified_access_conditions': mod_conditions,
            'validate_content': validate_content,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def upload_page( # type: ignore
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
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
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
            return self._client.page_blob.upload_pages(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _upload_pages_from_url_options(  # type: ignore
            self, source_url,  # type: str
            offset,  # type: int
            length,  # type: int
            source_offset,  # type: int
            **kwargs
    ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        # TODO: extract the code to a method format_range
        if offset is None or offset % 512 != 0:
            raise ValueError("offset must be an integer that aligns with 512 page size")
        if length is None or length % 512 != 0:
            raise ValueError("length must be an integer that aligns with 512 page size")
        if source_offset is None or offset % 512 != 0:
            raise ValueError("source_offset must be an integer that aligns with 512 page size")

        # Format range
        end_range = offset + length - 1
        destination_range = 'bytes={0}-{1}'.format(offset, end_range)
        source_range = 'bytes={0}-{1}'.format(source_offset, source_offset + length - 1)  # should subtract 1 here?

        seq_conditions = SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=kwargs.pop('if_sequence_number_lte', None),
            if_sequence_number_less_than=kwargs.pop('if_sequence_number_lt', None),
            if_sequence_number_equal_to=kwargs.pop('if_sequence_number_eq', None)
        )
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        source_mod_conditions = get_source_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        source_content_md5 = kwargs.pop('source_content_md5', None)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'source_url': source_url,
            'content_length': 0,
            'source_range': source_range,
            'range': destination_range,
            'source_content_md5': bytearray(source_content_md5) if source_content_md5 else None,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'sequence_number_access_conditions': seq_conditions,
            'modified_access_conditions': mod_conditions,
            'source_modified_access_conditions': source_mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def upload_pages_from_url(self, source_url,  # type: str
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
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
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
            return self._client.page_blob.upload_pages_from_url(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _clear_page_options(self, offset, length, **kwargs):
        # type: (int, int, **Any) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        seq_conditions = SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=kwargs.pop('if_sequence_number_lte', None),
            if_sequence_number_less_than=kwargs.pop('if_sequence_number_lt', None),
            if_sequence_number_equal_to=kwargs.pop('if_sequence_number_eq', None)
        )
        mod_conditions = get_modify_conditions(kwargs)
        if offset is None or offset % 512 != 0:
            raise ValueError("offset must be an integer that aligns with 512 page size")
        if length is None or length % 512 != 0:
            raise ValueError("length must be an integer that aligns with 512 page size")
        end_range = length + offset - 1  # Reformat to an inclusive range index
        content_range = 'bytes={0}-{1}'.format(offset, end_range)

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'content_length': 0,
            'timeout': kwargs.pop('timeout', None),
            'range': content_range,
            'lease_access_conditions': access_conditions,
            'sequence_number_access_conditions': seq_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def clear_page(self, offset, length, **kwargs):
        # type: (int, int, **Any) -> Dict[str, Union[str, datetime]]
        """Clears a range of pages.

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
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
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
            return self._client.page_blob.clear_pages(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _append_block_options( # type: ignore
            self, data,  # type: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        if isinstance(data, six.text_type):
            data = data.encode(kwargs.pop('encoding', 'UTF-8')) # type: ignore
        if length is None:
            length = get_length(data)
            if length is None:
                length, data = read_length(data)
        if length == 0:
            return {}
        if isinstance(data, bytes):
            data = data[:length]

        appendpos_condition = kwargs.pop('appendpos_condition', None)
        maxsize_condition = kwargs.pop('maxsize_condition', None)
        validate_content = kwargs.pop('validate_content', False)
        append_conditions = None
        if maxsize_condition or appendpos_condition is not None:
            append_conditions = AppendPositionAccessConditions(
                max_size=maxsize_condition,
                append_position=appendpos_condition
            )
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'body': data,
            'content_length': length,
            'timeout': kwargs.pop('timeout', None),
            'transactional_content_md5': None,
            'lease_access_conditions': access_conditions,
            'append_position_access_conditions': append_conditions,
            'modified_access_conditions': mod_conditions,
            'validate_content': validate_content,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def append_block( # type: ignore
            self, data,  # type: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime, int]]
        """Commits a new block of data to the end of the existing append blob.

        :param data:
            Content of the block. This can be bytes, text, an iterable or a file-like object.
        :type data: bytes or str or Iterable
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
            return self._client.append_blob.append_block(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _append_block_from_url_options(  # type: ignore
            self, copy_source_url,  # type: str
            source_offset=None,  # type: Optional[int]
            source_length=None,  # type: Optional[int]
            **kwargs
    ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        # If end range is provided, start range must be provided
        if source_length is not None and source_offset is None:
            raise ValueError("source_offset should also be specified if source_length is specified")
        # Format based on whether length is present
        source_range = None
        if source_length is not None:
            end_range = source_offset + source_length - 1
            source_range = 'bytes={0}-{1}'.format(source_offset, end_range)
        elif source_offset is not None:
            source_range = "bytes={0}-".format(source_offset)

        appendpos_condition = kwargs.pop('appendpos_condition', None)
        maxsize_condition = kwargs.pop('maxsize_condition', None)
        source_content_md5 = kwargs.pop('source_content_md5', None)
        append_conditions = None
        if maxsize_condition or appendpos_condition is not None:
            append_conditions = AppendPositionAccessConditions(
                max_size=maxsize_condition,
                append_position=appendpos_condition
            )
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        source_mod_conditions = get_source_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'source_url': copy_source_url,
            'content_length': 0,
            'source_range': source_range,
            'source_content_md5': source_content_md5,
            'transactional_content_md5': None,
            'lease_access_conditions': access_conditions,
            'append_position_access_conditions': append_conditions,
            'modified_access_conditions': mod_conditions,
            'source_modified_access_conditions': source_mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
            'timeout': kwargs.pop('timeout', None)}
        options.update(kwargs)
        return options

    @distributed_trace
    def append_block_from_url(self, copy_source_url,  # type: str
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
            This indicates the start of the range of bytes (inclusive) that has to be taken from the copy source.
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
            return self._client.append_blob.append_block_from_url(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    def _seal_append_blob_options(self, **kwargs):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        appendpos_condition = kwargs.pop('appendpos_condition', None)
        append_conditions = None
        if appendpos_condition is not None:
            append_conditions = AppendPositionAccessConditions(
                append_position=appendpos_condition
            )
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)

        options = {
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'append_position_access_conditions': append_conditions,
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    @distributed_trace
    def seal_append_blob(self, **kwargs):
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
            return self._client.append_blob.seal(**options) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)
