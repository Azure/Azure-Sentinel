# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines

from azure.core.async_paging import AsyncPageIterator
from azure.core.exceptions import HttpResponseError
from .._deserialize import parse_tags

from .._models import ContainerProperties, FilteredBlob, parse_page_list
from .._shared.response_handlers import return_context_and_deserialized, process_storage_error

from .._generated.models import FilterBlobItem


class ContainerPropertiesPaged(AsyncPageIterator):
    """An Iterable of Container properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A container name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.ContainerProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only containers whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of container names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
        super(ContainerPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
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
        self.current_page = [self._build_item(item) for item in self._response.container_items]

        return self._response.next_marker or None, self.current_page

    @staticmethod
    def _build_item(item):
        return ContainerProperties._from_generated(item)  # pylint: disable=protected-access


class FilteredBlobPaged(AsyncPageIterator):
    """An Iterable of Blob properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.BlobProperties)
    :ivar str container: The container that the blobs are listed from.
    :param callable command: Function to retrieve the next page of items.
    :param str container: The name of the container.
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
            results_per_page=None,
            continuation_token=None,
            location_mode=None):
        super(FilteredBlobPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.marker = continuation_token
        self.results_per_page = results_per_page
        self.container = container
        self.current_page = None
        self.location_mode = location_mode

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.marker = self._response.next_marker
        self.current_page = [self._build_item(item) for item in self._response.blobs]

        return self._response.next_marker or None, self.current_page

    @staticmethod
    def _build_item(item):
        if isinstance(item, FilterBlobItem):
            tags = parse_tags(item.tags)
            blob = FilteredBlob(name=item.name, container_name=item.container_name, tags=tags)
            return blob
        return item


class PageRangePaged(AsyncPageIterator):
    def __init__(self, command, results_per_page=None, continuation_token=None):
        super(PageRangePaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.current_page = self._build_page(self._response)

        return self._response.next_marker or None, self.current_page

    @staticmethod
    def _build_page(response):
        if not response:
            raise StopIteration

        return parse_page_list(response)
