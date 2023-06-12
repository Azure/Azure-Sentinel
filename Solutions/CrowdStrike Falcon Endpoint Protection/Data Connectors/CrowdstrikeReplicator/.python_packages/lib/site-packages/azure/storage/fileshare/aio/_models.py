# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines

from azure.core.async_paging import AsyncPageIterator
from azure.core.exceptions import HttpResponseError

from .._shared.response_handlers import return_context_and_deserialized, process_storage_error
from .._generated.models import DirectoryItem
from .._models import Handle, ShareProperties


def _wrap_item(item):
    if isinstance(item, DirectoryItem):
        return {'name': item.name, 'is_directory': True}
    return {'name': item.name, 'size': item.properties.content_length, 'is_directory': False}


class SharePropertiesPaged(AsyncPageIterator):
    """An iterable of Share properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A file name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.fileshare.ShareProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only shares whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
        super(SharePropertiesPaged, self).__init__(
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
        self.current_page = [ShareProperties._from_generated(i) for i in self._response.share_items]  # pylint: disable=protected-access
        return self._response.next_marker or None, self.current_page


class HandlesPaged(AsyncPageIterator):
    """An iterable of Handles.

    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.fileshare.Handle)

    :param callable command: Function to retrieve the next page of items.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, results_per_page=None, continuation_token=None):
        super(HandlesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
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
        self.current_page = [Handle._from_generated(h) for h in self._response.handle_list]  # pylint: disable=protected-access
        return self._response.next_marker or None, self.current_page


class DirectoryPropertiesPaged(AsyncPageIterator):
    """An iterable for the contents of a directory.

    This iterable will yield dicts for the contents of the directory. The dicts
    will have the keys 'name' (str) and 'is_directory' (bool).
    Items that are files (is_directory=False) will have an additional 'content_length' key.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A file name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(dict(str, Any))

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only directories whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
        super(DirectoryPropertiesPaged, self).__init__(
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
                prefix=self.prefix,
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
        self.current_page = [_wrap_item(i) for i in self._response.segment.directory_items]
        self.current_page.extend([_wrap_item(i) for i in self._response.segment.file_items])
        return self._response.next_marker or None, self.current_page
