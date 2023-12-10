# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use

from io import SEEK_SET, UnsupportedOperation
from typing import Optional, Union, Any, TypeVar, TYPE_CHECKING # pylint: disable=unused-import

import six
from azure.core.exceptions import ResourceModifiedError, HttpResponseError

from .._shared.response_handlers import (
    process_storage_error,
    return_response_headers)
from .._shared.uploads_async import (
    upload_data_chunks,
    upload_substream_blocks,
    BlockBlobChunkUploader,
    PageBlobChunkUploader,
    AppendBlobChunkUploader)
from .._shared.encryption import generate_blob_encryption_data, encrypt_blob
from .._generated.models import (
    BlockLookupList,
    AppendPositionAccessConditions,
    ModifiedAccessConditions,
)
from .._upload_helpers import _convert_mod_error, _any_conditions

if TYPE_CHECKING:
    from datetime import datetime # pylint: disable=unused-import
    BlobLeaseClient = TypeVar("BlobLeaseClient")


async def upload_block_blob(  # pylint: disable=too-many-locals
        client=None,
        data=None,
        stream=None,
        length=None,
        overwrite=None,
        headers=None,
        validate_content=None,
        max_concurrency=None,
        blob_settings=None,
        encryption_options=None,
        **kwargs):
    try:
        if not overwrite and not _any_conditions(**kwargs):
            kwargs['modified_access_conditions'].if_none_match = '*'
        adjusted_count = length
        if (encryption_options.get('key') is not None) and (adjusted_count is not None):
            adjusted_count += (16 - (length % 16))
        blob_headers = kwargs.pop('blob_headers', None)
        tier = kwargs.pop('standard_blob_tier', None)
        blob_tags_string = kwargs.pop('blob_tags_string', None)

        # Do single put if the size is smaller than config.max_single_put_size
        if adjusted_count is not None and (adjusted_count <= blob_settings.max_single_put_size):
            try:
                data = data.read(length)
                if not isinstance(data, six.binary_type):
                    raise TypeError('Blob data should be of type bytes.')
            except AttributeError:
                pass
            if encryption_options.get('key'):
                encryption_data, data = encrypt_blob(data, encryption_options['key'])
                headers['x-ms-meta-encryptiondata'] = encryption_data
            return await client.upload(
                body=data,
                content_length=adjusted_count,
                blob_http_headers=blob_headers,
                headers=headers,
                cls=return_response_headers,
                validate_content=validate_content,
                data_stream_total=adjusted_count,
                upload_stream_current=0,
                tier=tier.value if tier else None,
                blob_tags_string=blob_tags_string,
                **kwargs)

        use_original_upload_path = blob_settings.use_byte_buffer or \
            validate_content or encryption_options.get('required') or \
            blob_settings.max_block_size < blob_settings.min_large_block_upload_threshold or \
            hasattr(stream, 'seekable') and not stream.seekable() or \
            not hasattr(stream, 'seek') or not hasattr(stream, 'tell')

        if use_original_upload_path:
            if encryption_options.get('key'):
                cek, iv, encryption_data = generate_blob_encryption_data(encryption_options['key'])
                headers['x-ms-meta-encryptiondata'] = encryption_data
                encryption_options['cek'] = cek
                encryption_options['vector'] = iv
            block_ids = await upload_data_chunks(
                service=client,
                uploader_class=BlockBlobChunkUploader,
                total_size=length,
                chunk_size=blob_settings.max_block_size,
                max_concurrency=max_concurrency,
                stream=stream,
                validate_content=validate_content,
                encryption_options=encryption_options,
                headers=headers,
                **kwargs
            )
        else:
            block_ids = await upload_substream_blocks(
                service=client,
                uploader_class=BlockBlobChunkUploader,
                total_size=length,
                chunk_size=blob_settings.max_block_size,
                max_concurrency=max_concurrency,
                stream=stream,
                validate_content=validate_content,
                headers=headers,
                **kwargs
            )

        block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
        block_lookup.latest = block_ids
        return await client.commit_block_list(
            block_lookup,
            blob_http_headers=blob_headers,
            cls=return_response_headers,
            validate_content=validate_content,
            headers=headers,
            tier=tier.value if tier else None,
            blob_tags_string=blob_tags_string,
            **kwargs)
    except HttpResponseError as error:
        try:
            process_storage_error(error)
        except ResourceModifiedError as mod_error:
            if not overwrite:
                _convert_mod_error(mod_error)
            raise


async def upload_page_blob(
        client=None,
        stream=None,
        length=None,
        overwrite=None,
        headers=None,
        validate_content=None,
        max_concurrency=None,
        blob_settings=None,
        encryption_options=None,
        **kwargs):
    try:
        if not overwrite and not _any_conditions(**kwargs):
            kwargs['modified_access_conditions'].if_none_match = '*'
        if length is None or length < 0:
            raise ValueError("A content length must be specified for a Page Blob.")
        if length % 512 != 0:
            raise ValueError("Invalid page blob size: {0}. "
                             "The size must be aligned to a 512-byte boundary.".format(length))
        if kwargs.get('premium_page_blob_tier'):
            premium_page_blob_tier = kwargs.pop('premium_page_blob_tier')
            try:
                headers['x-ms-access-tier'] = premium_page_blob_tier.value
            except AttributeError:
                headers['x-ms-access-tier'] = premium_page_blob_tier
        if encryption_options and encryption_options.get('data'):
            headers['x-ms-meta-encryptiondata'] = encryption_options['data']
        blob_tags_string = kwargs.pop('blob_tags_string', None)

        response = await client.create(
            content_length=0,
            blob_content_length=length,
            blob_sequence_number=None,
            blob_http_headers=kwargs.pop('blob_headers', None),
            blob_tags_string=blob_tags_string,
            cls=return_response_headers,
            headers=headers,
            **kwargs)
        if length == 0:
            return response

        kwargs['modified_access_conditions'] = ModifiedAccessConditions(if_match=response['etag'])
        return await upload_data_chunks(
            service=client,
            uploader_class=PageBlobChunkUploader,
            total_size=length,
            chunk_size=blob_settings.max_page_size,
            stream=stream,
            max_concurrency=max_concurrency,
            validate_content=validate_content,
            encryption_options=encryption_options,
            headers=headers,
            **kwargs)

    except HttpResponseError as error:
        try:
            process_storage_error(error)
        except ResourceModifiedError as mod_error:
            if not overwrite:
                _convert_mod_error(mod_error)
            raise


async def upload_append_blob(  # pylint: disable=unused-argument
        client=None,
        stream=None,
        length=None,
        overwrite=None,
        headers=None,
        validate_content=None,
        max_concurrency=None,
        blob_settings=None,
        encryption_options=None,
        **kwargs):
    try:
        if length == 0:
            return {}
        blob_headers = kwargs.pop('blob_headers', None)
        append_conditions = AppendPositionAccessConditions(
            max_size=kwargs.pop('maxsize_condition', None),
            append_position=None)
        blob_tags_string = kwargs.pop('blob_tags_string', None)

        try:
            if overwrite:
                await client.create(
                    content_length=0,
                    blob_http_headers=blob_headers,
                    headers=headers,
                    blob_tags_string=blob_tags_string,
                    **kwargs)
            return await upload_data_chunks(
                service=client,
                uploader_class=AppendBlobChunkUploader,
                total_size=length,
                chunk_size=blob_settings.max_block_size,
                stream=stream,
                max_concurrency=max_concurrency,
                validate_content=validate_content,
                append_position_access_conditions=append_conditions,
                headers=headers,
                **kwargs)
        except HttpResponseError as error:
            if error.response.status_code != 404:
                raise
            # rewind the request body if it is a stream
            if hasattr(stream, 'read'):
                try:
                    # attempt to rewind the body to the initial position
                    stream.seek(0, SEEK_SET)
                except UnsupportedOperation:
                    # if body is not seekable, then retry would not work
                    raise error
            await client.create(
                content_length=0,
                blob_http_headers=blob_headers,
                headers=headers,
                blob_tags_string=blob_tags_string,
                **kwargs)
            return await upload_data_chunks(
                service=client,
                uploader_class=AppendBlobChunkUploader,
                total_size=length,
                chunk_size=blob_settings.max_block_size,
                stream=stream,
                max_concurrency=max_concurrency,
                validate_content=validate_content,
                append_position_access_conditions=append_conditions,
                headers=headers,
                **kwargs)
    except HttpResponseError as error:
        process_storage_error(error)
