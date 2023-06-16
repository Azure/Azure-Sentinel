# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError
from azure.core.async_paging import AsyncPageIterator

from .._deserialize import (
    _return_context_and_deserialized,
    _convert_to_entity,
    _extract_continuation_token,
)
from .._generated.models import QueryOptions
from .._models import TableItem
from .._error import _process_table_error
from .._constants import NEXT_PARTITION_KEY, NEXT_TABLE_NAME, NEXT_ROW_KEY


class TablePropertiesPaged(AsyncPageIterator):
    """An iterable of Table properties.

    :param callable command: Function to retrieve the next page of items.
    :keyword int results_per_page: The maximum number of results retrieved per API call.
    :keyword str filter: The filter to apply to results.
    :keyword str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, **kwargs):
        super(TablePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token") or "",
        )
        self._command = command
        self._headers = None
        self._response = None
        self.results_per_page = kwargs.get("results_per_page")
        self.filter = kwargs.get("filter")
        self._location_mode = None

    async def _get_next_cb(self, continuation_token, **kwargs):
        query_options = QueryOptions(top=self.results_per_page, filter=self.filter)
        try:
            return await self._command(
                query_options=query_options,
                next_table_name=continuation_token or None,
                cls=kwargs.pop("cls", None) or _return_context_and_deserialized,
                use_location=self._location_mode,
            )
        except HttpResponseError as error:
            _process_table_error(error)

    async def _extract_data_cb(self, get_next_return):
        self._location_mode, self._response, self._headers = get_next_return
        props_list = [
            TableItem._from_generated(t, **self._headers) for t in self._response.value  # pylint: disable=protected-access
        ]
        return self._headers[NEXT_TABLE_NAME] or None, props_list


class TableEntityPropertiesPaged(AsyncPageIterator):
    """An iterable of TableEntity properties.

    :param callable command: Function to retrieve the next page of items.
    :param str table: The name of the table.
    :keyword int results_per_page: The maximum number of results retrieved per API call.
    :keyword str filter: The filter to apply to results.
    :keyword str select: The select filter to apply to results.
    :keyword str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, table, **kwargs):
        super(TableEntityPropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token") or {},
        )
        self._command = command
        self._headers = None
        self._response = None
        self.table = table
        self.results_per_page = kwargs.get("results_per_page")
        self.filter = kwargs.get("filter")
        self.select = kwargs.get("select")
        self._location_mode = None

    async def _get_next_cb(self, continuation_token, **kwargs):
        next_partition_key, next_row_key = _extract_continuation_token(
            continuation_token
        )
        query_options = QueryOptions(
            top=self.results_per_page, select=self.select, filter=self.filter
        )
        try:
            return await self._command(
                query_options=query_options,
                next_row_key=next_row_key,
                next_partition_key=next_partition_key,
                table=self.table,
                cls=kwargs.pop("cls", _return_context_and_deserialized),
                use_location=self._location_mode,
            )
        except HttpResponseError as error:
            _process_table_error(error)

    async def _extract_data_cb(self, get_next_return):
        self._location_mode, self._response, self._headers = get_next_return
        props_list = [_convert_to_entity(t) for t in self._response.value]
        next_entity = {}
        if self._headers[NEXT_PARTITION_KEY] or self._headers[NEXT_ROW_KEY]:
            next_entity = {
                "PartitionKey": self._headers[NEXT_PARTITION_KEY],
                "RowKey": self._headers[NEXT_ROW_KEY],
            }
        return next_entity or None, props_list
