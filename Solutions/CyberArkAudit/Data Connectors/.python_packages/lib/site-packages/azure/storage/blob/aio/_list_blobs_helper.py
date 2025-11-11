# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from urllib.parse import unquote

from azure.core.async_paging import AsyncPageIterator, AsyncItemPaged
from azure.core.exceptions import HttpResponseError

from .._deserialize import (
    get_blob_properties_from_generated_code,
    load_many_xml_nodes,
    load_xml_int,
    load_xml_string,
)
from .._generated.models import BlobItemInternal, BlobPrefix as GenBlobPrefix
from .._models import BlobProperties
from .._shared.models import DictMixin
from .._shared.response_handlers import (
    return_context_and_deserialized,
    return_raw_deserialized,
    process_storage_error,
)


class BlobPropertiesPaged(AsyncPageIterator):
    """An Iterable of Blob properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.BlobProperties)
    :ivar str container: The container that the blobs are listed from.
    :ivar str delimiter: A delimiting character used for hierarchy listing.

    :param callable command: Function to retrieve the next page of items.
    :param str container: The container that the blobs are listed from.
    :param str prefix: Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    :param str delimiter:
        Used to capture blobs whose names begin with the same substring up to
        the appearance of the delimiter character. The delimiter may be a single
        character or a string.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(
            self, command,
            container=None,
            prefix=None,
            results_per_page=None,
            continuation_token=None,
            delimiter=None,
            location_mode=None):
        super(BlobPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.container = container
        self.delimiter = delimiter
        self.current_page = None
        self.location_mode = location_mode

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.container = self._response.container_name
        self.current_page = [self._build_item(item) for item in self._response.segment.blob_items]

        return self._response.next_marker or None, self.current_page

    def _build_item(self, item):
        if isinstance(item, BlobProperties):
            return item
        if isinstance(item, BlobItemInternal):
            blob = get_blob_properties_from_generated_code(item)  # pylint: disable=protected-access
            blob.container = self.container
            return blob
        return item


class BlobNamesPaged(AsyncPageIterator):
    """An Iterable of Blob names.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(str)
    :ivar str container: The container that the blobs are listed from.
    :ivar str delimiter: A delimiting character used for hierarchy listing.

    :param callable command: Function to retrieve the next page of items.
    :param str container: The name of the container.
    :param str prefix: Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(
            self, command,
            container=None,
            prefix=None,
            results_per_page=None,
            continuation_token=None,
            location_mode=None):
        super(BlobNamesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.container = container
        self.current_page = None
        self.location_mode = location_mode

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_raw_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.get('ServiceEndpoint')
        self.prefix = load_xml_string(self._response, 'Prefix')
        self.marker = load_xml_string(self._response, 'Marker')
        self.results_per_page = load_xml_int(self._response, 'MaxResults')
        self.container = self._response.get('ContainerName')

        blobs = load_many_xml_nodes(self._response, 'Blob', wrapper='Blobs')
        self.current_page = [load_xml_string(blob, 'Name') for blob in blobs]

        next_marker = load_xml_string(self._response, 'NextMarker')
        return next_marker or None, self.current_page


class BlobPrefix(AsyncItemPaged, DictMixin):
    """An Iterable of Blob properties.

    Returned from walk_blobs when a delimiter is used.
    Can be thought of as a virtual blob directory.

    :ivar str name: The prefix, or "directory name" of the blob.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str marker: The continuation token of the current page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.BlobProperties)
    :ivar str container: The container that the blobs are listed from.
    :ivar str delimiter: A delimiting character used for hierarchy listing.
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str marker: An opaque continuation token.
    :param str delimiter:
        Used to capture blobs whose names begin with the same substring up to
        the appearance of the delimiter character. The delimiter may be a single
        character or a string.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(self, *args, **kwargs):
        super(BlobPrefix, self).__init__(*args, page_iterator_class=BlobPrefixPaged, **kwargs)
        self.name = kwargs.get('prefix')
        self.prefix = kwargs.get('prefix')
        self.results_per_page = kwargs.get('results_per_page')
        self.container = kwargs.get('container')
        self.delimiter = kwargs.get('delimiter')
        self.location_mode = kwargs.get('location_mode')


class BlobPrefixPaged(BlobPropertiesPaged):
    def __init__(self, *args, **kwargs):
        super(BlobPrefixPaged, self).__init__(*args, **kwargs)
        self.name = self.prefix

    async def _extract_data_cb(self, get_next_return):
        continuation_token, _ = await super(BlobPrefixPaged, self)._extract_data_cb(get_next_return)
        self.current_page = self._response.segment.blob_prefixes + self._response.segment.blob_items
        self.current_page = [self._build_item(item) for item in self.current_page]
        self.delimiter = self._response.delimiter

        return continuation_token, self.current_page

    def _build_item(self, item):
        item = super(BlobPrefixPaged, self)._build_item(item)
        if isinstance(item, GenBlobPrefix):
            if item.name.encoded:
                name = unquote(item.name.content)
            else:
                name = item.name.content
            return BlobPrefix(
                self._command,
                container=self.container,
                prefix=name,
                results_per_page=self.results_per_page,
                location_mode=self.location_mode)
        return item
