# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from typing import List, Union, Any, Optional, Mapping, Iterable, Dict, overload, cast, TYPE_CHECKING
try:
    from urllib.parse import urlparse, unquote
except ImportError:
    from urlparse import urlparse  # type: ignore
    from urllib2 import unquote  # type: ignore

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._base_client import parse_connection_str
from .._entity import TableEntity
from .._generated.models import SignedIdentifier, TableProperties, QueryOptions
from .._models import TableAccessPolicy, TableItem
from .._serialize import serialize_iso, _parameter_filter_substitution
from .._deserialize import deserialize_iso, _return_headers_and_deserialized
from .._error import (
    _process_table_error,
    _validate_table_name,
    _decode_error,
    _reraise_error
)
from .._models import UpdateMode
from .._deserialize import _convert_to_entity, _trim_service_metadata
from .._serialize import _add_entity_properties, _get_match_headers
from .._table_client import EntityType, TransactionOperationType
from ._base_client_async import AsyncTablesBaseClient
from ._models import TableEntityPropertiesPaged
from ._table_batch_async import TableBatchOperations

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class TableClient(AsyncTablesBaseClient):
    """A client to interact with a specific Table in an Azure Tables account.

    :ivar str account_name: The name of the Tables account.
    :ivar str table_name: The name of the table.
    :ivar str url: The full URL to the Tables account.
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self,
        endpoint: str,
        table_name: str,
        *,
        credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, "AsyncTokenCredential"]] = None,
        **kwargs
    ) -> None:
        """Create TableClient from a Credential.

        :param str endpoint: A URL to an Azure Tables account.
        :param str table_name: The table name.
        :keyword credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be one of AzureNamedKeyCredential (azure-core),
            AzureSasCredential (azure-core), or TokenCredentials from azure-identity.
        :paramtype credential:
            :class:`~azure.core.credentials.AzureNamedKeyCredential` or
            :class:`~azure.core.credentials.AzureSasCredential` or
            :class:`~azure.core.credentials.TokenCredential`

        :returns: None
        """
        if not table_name:
            raise ValueError("Please specify a table name.")
        _validate_table_name(table_name)
        self.table_name = table_name
        super(TableClient, self).__init__(endpoint, credential=credential, **kwargs)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        table_name: str,
        **kwargs
    ) -> 'TableClient':
        """Create TableClient from a Connection string.

        :param str conn_str: A connection string to an Azure Tables account.
        :param str table_name: The table name.
        :returns: A table client.
        :rtype: :class:`~azure.data.tables.TableClient`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_client_async.py
                :start-after: [START create_table_client]
                :end-before: [END create_table_client]
                :language: python
                :dedent: 8
                :caption: Creating the TableClient from a connection string.
        """
        endpoint, credential = parse_connection_str(
            conn_str=conn_str, credential=None, keyword_args=kwargs
        )
        return cls(endpoint, table_name=table_name, credential=credential, **kwargs)

    @classmethod
    def from_table_url(
        cls,
        table_url: str,
        **kwargs
    ) -> 'TableClient':
        """A client to interact with a specific Table.

        :param str table_url: The full URI to the table, including SAS token if used.
        :keyword credential:
            The credentials with which to authenticate. This is optional if the
            table URL already has a SAS token. The value can be one of AzureNamedKeyCredential
            or AzureSasCredential from azure-core.
        :paramtype credential:
            :class:`~azure.core.credentials.AzureNamedKeyCredential` or
            :class:`~azure.core.credentials.AzureSasCredential`
        :returns: A table client.
        :rtype: :class:`~azure.data.tables.TableClient`
        """
        try:
            if not table_url.lower().startswith("http"):
                table_url = "https://" + table_url
        except AttributeError:
            raise ValueError("Table URL must be a string.")
        parsed_url = urlparse(table_url.rstrip("/"))

        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(table_url))

        table_path = parsed_url.path.lstrip("/").split("/")
        account_path = ""
        if len(table_path) > 1:
            account_path = "/" + "/".join(table_path[:-1])
        endpoint = "{}://{}{}?{}".format(
            parsed_url.scheme,
            parsed_url.netloc.rstrip("/"),
            account_path,
            parsed_url.query,
        )
        table_name = unquote(table_path[-1])
        if table_name.lower().startswith("tables('"):
            table_name = table_name[8:-2]
        if not table_name:
            raise ValueError(
                "Invalid URL. Please provide a URL with a valid table name"
            )
        return cls(endpoint, table_name=table_name, **kwargs)

    @distributed_trace_async
    async def get_table_access_policy(self, **kwargs) -> Mapping[str, Optional[TableAccessPolicy]]:
        """
        Retrieves details about any stored access policies specified on the table that may be
        used with Shared Access Signatures.

        :return: Dictionary of SignedIdentifiers
        :rtype: Dict[str, Optional[:class:`~azure.data.tables.TableAccessPolicy`]]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        timeout = kwargs.pop("timeout", None)
        try:
            _, identifiers = await self._client.table.get_access_policy(
                table=self.table_name,
                timeout=timeout,
                cls=kwargs.pop("cls", None) or _return_headers_and_deserialized,
                **kwargs
            )
        except HttpResponseError as error:
            _process_table_error(error)
        output = {}  # type: Dict[str, Optional[TableAccessPolicy]]
        for identifier in cast(List[SignedIdentifier], identifiers):
            if identifier.access_policy:
                output[identifier.id] = TableAccessPolicy(
                    start=deserialize_iso(identifier.access_policy.start),
                    expiry=deserialize_iso(identifier.access_policy.expiry),
                    permission=identifier.access_policy.permission
                )
            else:
                output[identifier.id] = None
        return output

    @distributed_trace_async
    async def set_table_access_policy(
        self,
        signed_identifiers: Mapping[str, Optional[TableAccessPolicy]],
        **kwargs
    ) -> None:
        """Sets stored access policies for the table that may be used with Shared Access Signatures.

        :param signed_identifiers: Access policies to set for the table
        :type signed_identifiers: Dict[str, :class:`~azure.data.tables.TableAccessPolicy`]
        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        identifiers = []
        for key, value in signed_identifiers.items():
            payload = None
            if value:
                payload = TableAccessPolicy(
                    start=serialize_iso(value.start),
                    expiry=serialize_iso(value.expiry),
                    permission=value.permission
                )
            identifiers.append(SignedIdentifier(id=key, access_policy=payload))
        try:
            await self._client.table.set_access_policy(
                table=self.table_name, table_acl=identifiers or None, **kwargs  # type: ignore
            )
        except HttpResponseError as error:
            try:
                _process_table_error(error)
            except HttpResponseError as table_error:
                if (table_error.error_code == 'InvalidXmlDocument'  # type: ignore
                and len(identifiers) > 5):
                    raise ValueError(
                        'Too many access policies provided. The server does not support setting '
                        'more than 5 access policies on a single resource.'
                    )
                raise

    @distributed_trace_async
    async def create_table(self, **kwargs) -> TableItem:
        """Creates a new table under the given account.

        :return: A TableItem representing the created table.
        :rtype: :class:`~azure.data.tables.TableItem`
        :raises: :class:`~azure.core.exceptions.ResourceExistsError` If the entity already exists

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START create_table]
                :end-before: [END create_table]
                :language: python
                :dedent: 8
                :caption: Creating a table from the TableClient object.
        """
        table_properties = TableProperties(table_name=self.table_name)
        try:
            result = await self._client.table.create(table_properties, **kwargs)
        except HttpResponseError as error:
            _process_table_error(error)
        return TableItem(name=result.table_name)  # type: ignore

    @distributed_trace_async
    async def delete_table(self, **kwargs) -> None:
        """Deletes the table under the current account. No error will be raised if
        the given table name is not found.

        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START delete_from_table_client]
                :end-before: [END delete_from_table_client]
                :language: python
                :dedent: 8
                :caption: Deleting a table from the TableClient object.
        """
        try:
            await self._client.table.delete(table=self.table_name, **kwargs)
        except HttpResponseError as error:
            if error.status_code == 404:
                return
            _process_table_error(error)

    @overload
    async def delete_entity(self, partition_key: str, row_key: str, **kwargs: Any) -> None:
        ...

    @overload
    async def delete_entity(self, entity: Union[TableEntity, Mapping[str, Any]], **kwargs: Any) -> None:
        ...

    @distributed_trace_async
    async def delete_entity(self, *args: Union[TableEntity, str], **kwargs: Any) -> None:
        """Deletes the specified entity in a table. No error will be raised if
        the entity or PartitionKey-RowKey pairing is not found.

        :param str partition_key: The partition key of the entity.
        :param str row_key: The row key of the entity.
        :param entity: The entity to delete
        :type entity: Union[TableEntity, Mapping[str, str]]
        :keyword str etag: Etag of the entity
        :keyword match_condition: The condition under which to perform the operation.
            Supported values include: MatchConditions.IfNotModified, MatchConditions.Unconditionally.
            The default value is Unconditionally.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_insert_delete_entities_async.py
                :start-after: [START delete_entity]
                :end-before: [END delete_entity]
                :language: python
                :dedent: 8
                :caption: Adding an entity to a Table
        """
        try:
            entity = kwargs.pop('entity', None)
            if not entity:
                entity = args[0]
            partition_key = entity['PartitionKey']
            row_key = entity['RowKey']
        except (TypeError, IndexError):
            partition_key = kwargs.pop('partition_key', None)
            if not partition_key:
                partition_key = args[0]
            row_key = kwargs.pop("row_key", None)
            if not row_key:
                row_key = args[1]

        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and entity and not etag:
            try:
                etag = entity.metadata.get("etag", None)  # type: ignore
            except (AttributeError, TypeError):
                pass
        if_match = _get_match_headers(
            etag=etag,
            match_condition=match_condition or MatchConditions.Unconditionally,
        )

        try:
            await self._client.table.delete_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                if_match=if_match,
                **kwargs
            )
        except HttpResponseError as error:
            if error.status_code == 404:
                return
            _process_table_error(error)

    @distributed_trace_async
    async def create_entity(
        self,
        entity: EntityType,
        **kwargs
    ) -> Mapping[str, Any]:
        """Insert entity in a table.

        :param entity: The properties for the table entity.
        :type entity: Union[TableEntity, Mapping[str, Any]]
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: Dict[str,str]
        :raises: :class:`~azure.core.exceptions.ResourceExistsError` If the entity already exists


        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_insert_delete_entities_async.py
                :start-after: [START create_entity]
                :end-before: [END create_entity]
                :language: python
                :dedent: 8
                :caption: Adding an entity to a Table
        """
        entity = _add_entity_properties(entity)
        try:
            metadata, content = await self._client.table.insert_entity(  # type: ignore
                table=self.table_name,
                table_entity_properties=entity,  # type: ignore
                cls=kwargs.pop("cls", _return_headers_and_deserialized),
                **kwargs
            )
        except HttpResponseError as error:
            decoded = _decode_error(error.response, error.message)
            if decoded.error_code == "PropertiesNeedValue":
                if entity.get("PartitionKey") is None:
                    raise ValueError("PartitionKey must be present in an entity")
                if entity.get("RowKey") is None:
                    raise ValueError("RowKey must be present in an entity")
            _reraise_error(error)
        return _trim_service_metadata(metadata, content=content)  # type: ignore


    @distributed_trace_async
    async def update_entity(
        self,
        entity: EntityType,
        mode: Union[str, UpdateMode] = UpdateMode.MERGE,
        **kwargs
    ) -> Mapping[str, Any]:
        """Update entity in a table.

        :param entity: The properties for the table entity.
        :type entity: :class:`~azure.data.tables.TableEntity` or Dict[str,str]
        :param mode: Merge or Replace entity
        :type mode: :class:`~azure.data.tables.UpdateMode`
        :keyword str etag: Etag of the entity
        :keyword match_condition: The condition under which to perform the operation.
            Supported values include: MatchConditions.IfNotModified, MatchConditions.Unconditionally.
            The default value is Unconditionally.
        :paramtype match_condition: ~azure.core.MatchCondition
        :return: Dictionary of operation metadata returned from service
        :rtype: Dict[str,str]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_update_upsert_merge_entities_async.py
                :start-after: [START update_entity]
                :end-before: [END update_entity]
                :language: python
                :dedent: 16
                :caption: Querying entities from a TableClient
        """
        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and entity and not etag:
            try:
                etag = entity.metadata.get("etag", None)  # type: ignore
            except (AttributeError, TypeError):
                pass
        if_match = _get_match_headers(
            etag=etag,
            match_condition=match_condition or MatchConditions.Unconditionally,
        )

        partition_key = entity["PartitionKey"]
        row_key = entity["RowKey"]
        entity = _add_entity_properties(entity)
        try:
            metadata = None
            content = None
            if mode is UpdateMode.REPLACE:
                metadata, content = await self._client.table.update_entity(  # type: ignore
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,  # type: ignore
                    if_match=if_match,
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs
                )
            elif mode is UpdateMode.MERGE:
                metadata, content = await self._client.table.merge_entity(  # type: ignore
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    if_match=if_match,
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    table_entity_properties=entity,  # type: ignore
                    **kwargs
                )
            else:
                raise ValueError("Mode type is not supported")
        except HttpResponseError as error:
            _process_table_error(error)
        return _trim_service_metadata(metadata, content=content)  # type: ignore

    @distributed_trace
    def list_entities(self, **kwargs) -> AsyncItemPaged[TableEntity]:
        """Lists entities in a table.

        :keyword int results_per_page: Number of entities returned per service request.
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or List[str]
        :return: AsyncItemPaged[:class:`~azure.data.tables.TableEntity`]
        :rtype: ~azure.core.async_paging.AsyncItemPaged[TableEntity]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_update_upsert_merge_entities_async.py
                :start-after: [START list_entities]
                :end-before: [END list_entities]
                :language: python
                :dedent: 16
                :caption: Querying entities from a TableClient
        """
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ",".join(user_select)
        top = kwargs.pop("results_per_page", None)

        command = functools.partial(self._client.table.query_entities, **kwargs)
        return AsyncItemPaged(
            command,
            table=self.table_name,
            results_per_page=top,
            select=user_select,
            page_iterator_class=TableEntityPropertiesPaged,
        )

    @distributed_trace
    def query_entities(
        self,
        query_filter: str,
        **kwargs
    ) -> AsyncItemPaged[TableEntity]:
        """Lists entities in a table.

        :param str query_filter: Specify a filter to return certain entities
        :keyword int results_per_page: Number of entities returned per service request.
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or List[str]
        :keyword parameters: Dictionary for formatting query with additional, user defined parameters
        :paramtype parameters: Dict[str, Any]
        :return: AsyncItemPaged[:class:`~azure.data.tables.TableEntity`]
        :rtype: ~azure.core.async_paging.AsyncItemPaged[TableEntity]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_query_table_async.py
                :start-after: [START query_entities]
                :end-before: [END query_entities]
                :language: python
                :dedent: 8
                :caption: Querying entities from a TableClient
        """
        parameters = kwargs.pop("parameters", None)
        query_filter = _parameter_filter_substitution(
            parameters, query_filter
        )
        top = kwargs.pop("results_per_page", None)
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ",".join(user_select)

        command = functools.partial(self._client.table.query_entities, **kwargs)
        return AsyncItemPaged(
            command,
            table=self.table_name,
            results_per_page=top,
            filter=query_filter,
            select=user_select,
            page_iterator_class=TableEntityPropertiesPaged,
        )

    @distributed_trace_async
    async def get_entity(
        self,
        partition_key: str,
        row_key: str,
        **kwargs
    ) -> TableEntity:
        """Get a single entity in a table.

        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or List[str]
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: :class:`~azure.data.tables.TableEntity`
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_update_upsert_merge_entities_async.py
                :start-after: [START get_entity]
                :end-before: [END get_entity]
                :language: python
                :dedent: 16
                :caption: Getting an entity from PartitionKey and RowKey
        """
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ",".join(user_select)
        try:
            entity = await self._client.table.query_entity_with_partition_and_row_key(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                query_options=QueryOptions(select=user_select),
                **kwargs
            )
            properties = _convert_to_entity(entity)
        except HttpResponseError as error:
            _process_table_error(error)
        return properties

    @distributed_trace_async
    async def upsert_entity(
        self,
        entity: EntityType,
        mode: Union[str, UpdateMode] = UpdateMode.MERGE,
        **kwargs
    ) -> Mapping[str, Any]:
        """Update/Merge or Insert entity into table.

        :param entity: The properties for the table entity.
        :type entity: :class:`~azure.data.tables.TableEntity` or Dict[str,str]
        :param mode: Merge or Replace entity
        :type mode: :class:`~azure.data.tables.UpdateMode`
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: Dict[str,str]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_update_upsert_merge_entities_async.py
                :start-after: [START upsert_entity]
                :end-before: [END upsert_entity]
                :language: python
                :dedent: 16
                :caption: Update/Merge or Insert an entity into a table
        """

        partition_key = entity["PartitionKey"]
        row_key = entity["RowKey"]
        entity = _add_entity_properties(entity)

        try:
            metadata = None
            content = None
            if mode is UpdateMode.MERGE:
                metadata, content = await self._client.table.merge_entity(  # type: ignore
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,  # type: ignore
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs
                )
            elif mode is UpdateMode.REPLACE:
                metadata, content = await self._client.table.update_entity(  # type: ignore
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,  # type: ignore
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs
                )
            else:
                raise ValueError(
                    """Update mode {} is not supported.
                    For a list of supported modes see the UpdateMode enum""".format(
                        mode
                    )
                )
        except HttpResponseError as error:
            _process_table_error(error)
        return _trim_service_metadata(metadata, content=content)  # type: ignore

    @distributed_trace_async
    async def submit_transaction(
        self,
        operations: Iterable[TransactionOperationType],
        **kwargs
    ) -> List[Mapping[str, Any]]:
        """Commit a list of operations as a single transaction.

        If any one of these operations fails, the entire transaction will be rejected.

        :param operations: The list of operations to commit in a transaction. This should be a list of
         tuples containing an operation name, the entity on which to operate, and optionally, a dict of additional
         kwargs for that operation.
        :type operations: Iterable[Tuple[str, EntityType]]
        :return: A list of mappings with response metadata for each operation in the transaction.
        :rtype: List[Mapping[str, Any]]
        :raises ~azure.data.tables.TableTransactionError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_batching_async.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Using transactions to send multiple requests at once
        """
        batched_requests = TableBatchOperations(
            self._client,
            self._client._serialize,  # pylint: disable=protected-access
            self._client._deserialize,  # pylint: disable=protected-access
            self._client._config,  # pylint: disable=protected-access
            self.table_name,
            is_cosmos_endpoint=self._cosmos_endpoint,
            **kwargs
        )
        for operation in operations:
            try:
                operation_kwargs = operation[2]  # type: ignore
            except IndexError:
                operation_kwargs = {}
            try:
                getattr(batched_requests, operation[0].lower())(operation[1], **operation_kwargs)
            except AttributeError:
                raise ValueError("Unrecognized operation: {}".format(operation))
        return await self._batch_send(*batched_requests.requests, **kwargs)
