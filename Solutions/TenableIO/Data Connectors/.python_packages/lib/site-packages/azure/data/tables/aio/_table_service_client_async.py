# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from typing import (
    Optional,
    Dict,
    List,
    TYPE_CHECKING
)

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._base_client import parse_connection_str
from .._generated.models import TableServiceProperties
from .._models import service_stats_deserialize, service_properties_deserialize
from .._error import _process_table_error
from .._models import TableItem, LocationMode
from .._serialize import _parameter_filter_substitution
from ._table_client_async import TableClient
from ._base_client_async import AsyncTablesBaseClient, AsyncTransportWrapper
from ._models import TablePropertiesPaged

if TYPE_CHECKING:
    from .._models import TableCorsRule, TableMetrics, TableAnalyticsLogging


class TableServiceClient(AsyncTablesBaseClient):
    """A client to interact with the Table Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete tables within the account.
    For operations relating to a specific table, a client for this entity
    can be retrieved using the :func:`~get_table_client` function.

    :ivar str account_name: The name of the Tables account.
    :ivar str url: The full URL to the Tables account.
    :param str endpoint:
        The URL to the table service endpoint. Any other entities included
        in the URL path (e.g. table) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :keyword credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be one of AzureNamedKeyCredential (azure-core),
        AzureSasCredential (azure-core), or TokenCredentials from azure-identity.
    :paramtype credential:
        :class:`~azure.core.credentials.AzureNamedKeyCredential` or
        :class:`~azure.core.credentials.AzureSasCredential` or
        :class:`~azure.core.credentials.TokenCredential`
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-02-02'.
        Setting to an older version may result in reduced feature compatibility.

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START auth_from_shared_key]
            :end-before: [END auth_from_shared_key]
            :language: python
            :dedent: 8
            :caption: Creating the tableServiceClient with an account url and credential.

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START auth_by_sas]
            :end-before: [END auth_by_sas]
            :language: python
            :dedent: 8
            :caption: Creating the tableServiceClient with Shared Access Signature.
    """

    def _format_url(self, hostname: str) -> str:
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs) -> 'TableServiceClient':
        """Create TableServiceClient from a Connection String.

        :param str conn_str: A connection string to an Azure Tables account.
        :returns: A Table service client.
        :rtype: :class:`~azure.data.tables.aio.TableServiceClient`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the tableServiceClient from a connection string

        """
        endpoint, credential = parse_connection_str(
            conn_str=conn_str, credential=None, keyword_args=kwargs
        )
        return cls(endpoint, credential=credential, **kwargs)

    @distributed_trace_async
    async def get_service_stats(self, **kwargs) -> Dict[str, object]:
        """Retrieves statistics related to replication for the Table service. It is only available on the secondary
        location endpoint when read-access geo-redundant replication is enabled for the account.

        :return: Dictionary of service stats
        :rtype: Dict[str, object]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        try:
            timeout = kwargs.pop("timeout", None)
            stats = await self._client.service.get_statistics(  # type: ignore
                timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs
            )
        except HttpResponseError as error:
            _process_table_error(error)
        return service_stats_deserialize(stats)

    @distributed_trace_async
    async def get_service_properties(self, **kwargs) -> Dict[str, object]:
        """Gets the properties of an account's Table service,
        including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableServiceProperties, or the result of cls(response)
        :rtype: Dict[str, object]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        timeout = kwargs.pop("timeout", None)
        try:
            service_props = await self._client.service.get_properties(timeout=timeout, **kwargs)  # type: ignore
        except HttpResponseError as error:
            _process_table_error(error)
        return service_properties_deserialize(service_props)

    @distributed_trace_async
    async def set_service_properties(
        self,
        *,
        analytics_logging: Optional['TableAnalyticsLogging'] = None,
        hour_metrics: Optional['TableMetrics'] = None,
        minute_metrics: Optional['TableMetrics'] = None,
        cors: Optional[List['TableCorsRule']] = None,
        **kwargs
    ) -> None:
        """Sets properties for an account's Table service endpoint,
         including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :keyword analytics_logging: Properties for analytics
        :paramtype analytics_logging: ~azure.data.tables.TableAnalyticsLogging
        :keyword hour_metrics: Hour level metrics
        :paramtype hour_metrics: ~azure.data.tables.TableMetrics
        :keyword minute_metrics: Minute level metrics
        :paramtype minute_metrics: ~azure.data.tables.TableMetrics
        :keyword cors: Cross-origin resource sharing rules
        :paramtype cors: List[~azure.data.tables.TableCorsRule]
        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        if cors:
            cors = [c._to_generated() for c in cors]  # pylint:disable=protected-access
        props = TableServiceProperties(
            logging=analytics_logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors,  # type: ignore
        )
        try:
            await self._client.service.set_properties(props, **kwargs)  # type: ignore
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def create_table(self, table_name: str, **kwargs) -> TableClient:
        """Creates a new table under the given account.

        :param headers:
        :param str table_name: The Table name.
        :return: TableClient, or the result of cls(response)
        :rtype: :class:`~azure.data.tables.aio.TableClient`
        :raises: :class:`~azure.core.exceptions.ResourceExistsError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START create_table]
                :end-before: [END create_table]
                :language: python
                :dedent: 8
                :caption: Creating a table from TableServiceClient.
        """
        table = self.get_table_client(table_name=table_name)
        await table.create_table(**kwargs)
        return table

    @distributed_trace_async
    async def create_table_if_not_exists(self, table_name: str, **kwargs) -> TableClient:
        """Creates a new table if it does not currently exist.
        If the table currently exists, the current table is
        returned.

        :param table_name: The Table name.
        :type table_name: str
        :return: TableClient
        :rtype: :class:`~azure.data.tables.aio.TableClient`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START create_if_not_exists]
                :end-before: [END create_if_not_exists]
                :language: python
                :dedent: 8
                :caption: Creating a table if it does not already exist
        """
        table = self.get_table_client(table_name=table_name)
        try:
            await table.create_table(**kwargs)
        except ResourceExistsError:
            pass
        return table

    @distributed_trace_async
    async def delete_table(self, table_name: str, **kwargs) -> None:
        """Deletes a table under the current account. No error will be raised if
        the table is not found.

        :param str table_name: The Table name.
        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START delete_table]
                :end-before: [END delete_table]
                :language: python
                :dedent: 8
                :caption: Deleting a table
        """
        table = self.get_table_client(table_name=table_name)
        await table.delete_table(**kwargs)

    @distributed_trace
    def list_tables(self, **kwargs) -> AsyncItemPaged[TableItem]:
        """Queries tables under the given account.

        :keyword int results_per_page: Number of tables per page in returned ItemPaged
        :return: AsyncItemPaged[:class:`~azure.data.tables.TableItem`]
        :rtype: ~azure.core.async_paging.AsyncItemPaged
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_query_tables_async.py
                :start-after: [START tsc_list_tables]
                :end-before: [END tsc_list_tables]
                :language: python
                :dedent: 16
                :caption: Listing all tables in an account
        """
        top = kwargs.pop("results_per_page", None)

        command = functools.partial(self._client.table.query, **kwargs)
        return AsyncItemPaged(
            command,
            results_per_page=top,
            page_iterator_class=TablePropertiesPaged,
        )

    @distributed_trace
    def query_tables(self, query_filter: str, **kwargs) -> AsyncItemPaged[TableItem]:
        """Queries tables under the given account.

        :param str query_filter: Specify a filter to return certain tables.
        :keyword int results_per_page: Number of tables per page in return ItemPaged
        :keyword parameters: Dictionary for formatting query with additional, user defined parameters
        :paramtype parameters:  Dict[str, Any]
        :return: AsyncItemPaged[:class:`~azure.data.tables.TableItem`]
        :rtype: ~azure.core.async_paging.AsyncItemPaged
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_query_tables_async.py
                :start-after: [START tsc_query_tables]
                :end-before: [END tsc_query_tables]
                :language: python
                :dedent: 16
                :caption: Querying tables in an account given specific parameters
        """
        parameters = kwargs.pop("parameters", None)
        query_filter = _parameter_filter_substitution(
            parameters, query_filter
        )
        top = kwargs.pop("results_per_page", None)
        command = functools.partial(self._client.table.query, **kwargs)
        return AsyncItemPaged(
            command,
            results_per_page=top,
            filter=query_filter,
            page_iterator_class=TablePropertiesPaged,
        )

    def get_table_client(self, table_name: str, **kwargs) -> TableClient:
        """Get a client to interact with the specified table.

        The table need not already exist.

        :param str table_name: The table name
        :returns: A :class:`~azure.data.tables.aio.TableClient` object.
        :rtype: :class:`~azure.data.tables.aio.TableClient`

        """
        pipeline = AsyncPipeline(  # type: ignore
            transport=AsyncTransportWrapper(self._client._client._pipeline._transport), # pylint:disable=protected-access
            policies=self._policies,
        )
        return TableClient(
            self.url,
            table_name=table_name,
            credential=self.credential,  # type: ignore
            api_version=self.api_version,
            pipeline=pipeline,
            location_mode=self._location_mode,
            _hosts=self._hosts,
            **kwargs
        )
