# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import inspect
from io import SEEK_SET, UnsupportedOperation
from typing import TypeVar, TYPE_CHECKING

from azure.core.exceptions import ResourceModifiedError, HttpResponseError

from .._shared.response_handlers import process_storage_error, return_response_headers
from .._shared.uploads_async import (
    upload_data_chunks,
    upload_substream_blocks,
    BlockBlobChunkUploader,
    PageBlobChunkUploader,
    AppendBlobChunkUploader
)
from .._generated.models import (
    BlockLookupList,
    AppendPositionAccessConditions,
    ModifiedAccessConditions,
)
from .._encryption import (
    GCMBlobEncryptionStream,
    encrypt_blob,
    get_adjusted_upload_size,
    get_blob_encryptor_and_padder,
    generate_blob_encryption_data,
    _ENCRYPTION_PROTOCOL_V1,
    _ENCRYPTION_PROTOCOL_V2
)
from .._upload_helpers import _convert_mod_error, _any_conditions

if TYPE_CHECKING:
    BlobLeaseClient = TypeVar("BlobLeaseClient")


async def upload_block_blob(  # pylint: disable=too-many-locals, too-many-statements
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
            adjusted_count = get_adjusted_upload_size(adjusted_count, encryption_options['version'])
        blob_headers = kwargs.pop('blob_headers', None)
        tier = kwargs.pop('standard_blob_tier', None)
        blob_tags_string = kwargs.pop('blob_tags_string', None)

        immutability_policy = kwargs.pop('immutability_policy', None)
        immutability_policy_expiry = None if immutability_policy is None else immutability_policy.expiry_time
        immutability_policy_mode = None if immutability_policy is None else immutability_policy.policy_mode
        legal_hold = kwargs.pop('legal_hold', None)
        progress_hook = kwargs.pop('progress_hook', None)

        # Do single put if the size is smaller than config.max_single_put_size
        if adjusted_count is not None and (adjusted_count <= blob_settings.max_single_put_size):
            try:
                data = data.read(length)
                if inspect.isawaitable(data):
                    data = await data
                if not isinstance(data, bytes):
                    raise TypeError('Blob data should be of type bytes.')
            except AttributeError:
                pass
            if encryption_options.get('key'):
                encryption_data, data = encrypt_blob(data, encryption_options['key'], encryption_options['version'])
                headers['x-ms-meta-encryptiondata'] = encryption_data
            response = await client.upload(
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
                immutability_policy_expiry=immutability_policy_expiry,
                immutability_policy_mode=immutability_policy_mode,
                legal_hold=legal_hold,
                **kwargs)

            if progress_hook:
                await progress_hook(adjusted_count, adjusted_count)

            return response

        use_original_upload_path = blob_settings.use_byte_buffer or \
            validate_content or encryption_options.get('required') or \
            blob_settings.max_block_size < blob_settings.min_large_block_upload_threshold or \
            hasattr(stream, 'seekable') and not stream.seekable() or \
            not hasattr(stream, 'seek') or not hasattr(stream, 'tell')

        if use_original_upload_path:
            total_size = length
            encryptor, padder = None, None
            if encryption_options and encryption_options.get('key'):
                cek, iv, encryption_data = generate_blob_encryption_data(
                    encryption_options['key'],
                    encryption_options['version'])
                headers['x-ms-meta-encryptiondata'] = encryption_data

                if encryption_options['version'] == _ENCRYPTION_PROTOCOL_V1:
                    encryptor, padder = get_blob_encryptor_and_padder(cek, iv, True)

                # Adjust total_size for encryption V2
                if encryption_options['version'] == _ENCRYPTION_PROTOCOL_V2:
                    # Adjust total_size for encryption V2
                    total_size = adjusted_count
                    # V2 wraps the data stream with an encryption stream
                    stream = GCMBlobEncryptionStream(cek, stream)

            block_ids = await upload_data_chunks(
                service=client,
                uploader_class=BlockBlobChunkUploader,
                total_size=total_size,
                chunk_size=blob_settings.max_block_size,
                max_concurrency=max_concurrency,
                stream=stream,
                validate_content=validate_content,
                progress_hook=progress_hook,
                encryptor=encryptor,
                padder=padder,
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
                progress_hook=progress_hook,
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
            immutability_policy_expiry=immutability_policy_expiry,
            immutability_policy_mode=immutability_policy_mode,
            legal_hold=legal_hold,
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
            raise ValueError(f"Invalid page blob size: {length}. "
                             "The size must be aligned to a 512-byte boundary.")
        tier = None
        if kwargs.get('premium_page_blob_tier'):
            premium_page_blob_tier = kwargs.pop('premium_page_blob_tier')
            try:
                tier = premium_page_blob_tier.value
            except AttributeError:
                tier = premium_page_blob_tier

        if encryption_options and encryption_options.get('key'):
            cek, iv, encryption_data = generate_blob_encryption_data(
                encryption_options['key'],
                encryption_options['version'])
            headers['x-ms-meta-encryptiondata'] = encryption_data

        blob_tags_string = kwargs.pop('blob_tags_string', None)
        progress_hook = kwargs.pop('progress_hook', None)

        response = await client.create(
            content_length=0,
            blob_content_length=length,
            blob_sequence_number=None,
            blob_http_headers=kwargs.pop('blob_headers', None),
            blob_tags_string=blob_tags_string,
            tier=tier,
            cls=return_response_headers,
            headers=headers,
            **kwargs)
        if length == 0:
            return response

        if encryption_options and encryption_options.get('key'):
            if encryption_options['version'] == _ENCRYPTION_PROTOCOL_V1:
                encryptor, padder = get_blob_encryptor_and_padder(cek, iv, False)
                kwargs['encryptor'] = encryptor
                kwargs['padder'] = padder

        kwargs['modified_access_conditions'] = ModifiedAccessConditions(if_match=response['etag'])
        return await upload_data_chunks(
            service=client,
            uploader_class=PageBlobChunkUploader,
            total_size=length,
            chunk_size=blob_settings.max_page_size,
            stream=stream,
            max_concurrency=max_concurrency,
            validate_content=validate_content,
            progress_hook=progress_hook,
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
        progress_hook = kwargs.pop('progress_hook', None)

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
                progress_hook=progress_hook,
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
                except UnsupportedOperation as exc:
                    # if body is not seekable, then retry would not work
                    raise error from exc
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
                progress_hook=progress_hook,
                headers=headers,
                **kwargs)
    except HttpResponseError as error:
        process_storage_error(error)
