# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Any, Dict, List, Optional, Union,
    TYPE_CHECKING)
from urllib.parse import urlparse

from typing_extensions import Self

from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator import distributed_trace
from ._shared.base_client import StorageAccountHostsMixin, TransportWrapper, parse_connection_str, parse_query
from ._shared.models import LocationMode
from ._shared.response_handlers import process_storage_error
from ._generated import AzureQueueStorage
from ._generated.models import StorageServiceProperties
from ._encryption import StorageEncryptionMixin
from ._models import (
    QueuePropertiesPaged,
    service_stats_deserialize,
    service_properties_deserialize,
)
from ._serialize import get_api_version
from ._queue_client import QueueClient

if TYPE_CHECKING:
    from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
    from ._models import (
        CorsRule,
        Metrics,
        QueueProperties,
        QueueAnalyticsLogging,
    )


class QueueServiceClient(StorageAccountHostsMixin, StorageEncryptionMixin):
    """A client to interact with the Queue Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete queues within the account.
    For operations relating to a specific queue, a client for this entity
    can be retrieved using the :func:`~get_queue_client` function.

    For more optional configuration, please click
    `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue
    #optional-configuration>`_.

    :param str account_url:
        The URL to the queue service endpoint. Any other entities included
        in the URL path (e.g. queue) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
        an account shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
        If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
        should be the storage account key.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is the most recent service version that is
        compatible with the current SDK. Setting to an older version may result in reduced feature compatibility.
    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.

    .. admonition:: Example:

        .. literalinclude:: ../samples/queue_samples_authentication.py
            :start-after: [START create_queue_service_client]
            :end-before: [END create_queue_service_client]
            :language: python
            :dedent: 8
            :caption: Creating the QueueServiceClient with an account url and credential.

        .. literalinclude:: ../samples/queue_samples_authentication.py
            :start-after: [START create_queue_service_client_token]
            :end-before: [END create_queue_service_client_token]
            :language: python
            :dedent: 8
            :caption: Creating the QueueServiceClient with Azure Identity credentials.
    """

    def __init__(
            self, account_url: str,
            credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "TokenCredential"]] = None,  # pylint: disable=line-too-long
            **kwargs: Any
        ) -> None:
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError(f"Invalid URL: {account_url}")

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError("You need to provide either a SAS token or an account shared key to authenticate.")
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(QueueServiceClient, self).__init__(parsed_url, service='queue', credential=credential, **kwargs)
        self._client = AzureQueueStorage(self.url, base_url=self.url, pipeline=self._pipeline)
        self._client._config.version = get_api_version(kwargs)  # pylint: disable=protected-access
        self._configure_encryption(kwargs)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return f"{self.scheme}://{hostname}/{self._query_str}"

    @classmethod
    def from_connection_string(
            cls, conn_str: str,
            credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "TokenCredential"]] = None,  # pylint: disable=line-too-long
            **kwargs: Any
        ) -> Self:
        """Create QueueServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
            an account shared access key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
            If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
            should be the storage account key.
        :returns: A Queue service client.
        :rtype: ~azure.storage.queue.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_authentication.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the QueueServiceClient with a connection string.
        """
        account_url, secondary, credential = parse_connection_str(
            conn_str, credential, 'queue')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    @distributed_trace
    def get_service_stats(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Retrieves statistics related to replication for the Queue service.

        It is only available when read-access geo-redundant replication is enabled for
        the storage account.

        With geo-redundant replication, Azure Storage maintains your data durable
        in two locations. In both locations, Azure Storage constantly maintains
        multiple healthy replicas of your data. The location where you read,
        create, update, or delete data is the primary storage account location.
        The primary location exists in the region you choose at the time you
        create an account via the Azure Management Azure classic portal, for
        example, North Central US. The location to which your data is replicated
        is the secondary location. The secondary location is automatically
        determined based on the location of the primary; it is in a second data
        center that resides in the same region as the primary location. Read-only
        access is available from the secondary location, if read-access geo-redundant
        replication is enabled for your storage account.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: The queue service stats.
        :rtype: Dict[str, Any]
        """
        timeout = kwargs.pop('timeout', None)
        try:
            stats = self._client.service.get_statistics( # type: ignore
                timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs)
            return service_stats_deserialize(stats)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def get_service_properties(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Gets the properties of a storage account's Queue service, including
        Azure Storage Analytics.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An object containing queue service properties such as
            analytics logging, hour/minute metrics, cors rules, etc.
        :rtype: Dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service.py
                :start-after: [START get_queue_service_properties]
                :end-before: [END get_queue_service_properties]
                :language: python
                :dedent: 8
                :caption: Getting queue service properties.
        """
        timeout = kwargs.pop('timeout', None)
        try:
            service_props = self._client.service.get_properties(timeout=timeout, **kwargs) # type: ignore
            return service_properties_deserialize(service_props)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def set_service_properties( # type: ignore
            self, analytics_logging=None,  # type: Optional[QueueAnalyticsLogging]
            hour_metrics=None,  # type: Optional[Metrics]
            minute_metrics=None,  # type: Optional[Metrics]
            cors=None,  # type: Optional[List[CorsRule]]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        """Sets the properties of a storage account's Queue service, including
        Azure Storage Analytics.

        If an element (e.g. analytics_logging) is left as None, the
        existing settings on the service for that functionality are preserved.

        :param analytics_logging:
            Groups the Azure Analytics Logging settings.
        :type analytics_logging: ~azure.storage.queue.QueueAnalyticsLogging
        :param hour_metrics:
            The hour metrics settings provide a summary of request
            statistics grouped by API in hourly aggregates for queues.
        :type hour_metrics: ~azure.storage.queue.Metrics
        :param minute_metrics:
            The minute metrics settings provide request statistics
            for each minute for queues.
        :type minute_metrics: ~azure.storage.queue.Metrics
        :param cors:
            You can include up to five CorsRule elements in the
            list. If an empty list is specified, all CORS rules will be deleted,
            and CORS will be disabled for the service.
        :type cors: list(~azure.storage.queue.CorsRule)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service.py
                :start-after: [START set_queue_service_properties]
                :end-before: [END set_queue_service_properties]
                :language: python
                :dedent: 8
                :caption: Setting queue service properties.
        """
        timeout = kwargs.pop('timeout', None)
        props = StorageServiceProperties(
            logging=analytics_logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors
        )
        try:
            return self._client.service.set_properties(props, timeout=timeout, **kwargs) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_queues(
            self, name_starts_with=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            **kwargs  # type: Any
        ):
        # type: (...) -> ItemPaged[QueueProperties]
        """Returns a generator to list the queues under the specified account.

        The generator will lazily follow the continuation tokens returned by
        the service and stop when all queues have been returned.

        :param str name_starts_with:
            Filters the results to return only queues whose names
            begin with the specified prefix.
        :param bool include_metadata:
            Specifies that queue metadata be returned in the response.
        :keyword int results_per_page:
            The maximum number of queue names to retrieve per API
            call. If the request does not specify the server will return up to 5,000 items.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/en-us/rest/api/storageservices/setting-timeouts-for-queue-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue
            #other-client--per-operation-configuration>`_. This function may make multiple
            calls to the service in which case the timeout value specified will be
            applied to each individual call.
        :returns: An iterable (auto-paging) of QueueProperties.
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.queue.QueueProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service.py
                :start-after: [START qsc_list_queues]
                :end-before: [END qsc_list_queues]
                :language: python
                :dedent: 12
                :caption: List queues in the service.
        """
        results_per_page = kwargs.pop('results_per_page', None)
        timeout = kwargs.pop('timeout', None)
        include = ['metadata'] if include_metadata else None
        command = functools.partial(
            self._client.service.list_queues_segment,
            prefix=name_starts_with,
            include=include,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=QueuePropertiesPaged
        )

    @distributed_trace
    def create_queue(
            self, name,  # type: str
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs  # type: Any
        ):
        # type: (...) -> QueueClient
        """Creates a new queue under the specified account.

        If a queue with the same name already exists, the operation fails.
        Returns a client with which to interact with the newly created queue.

        :param str name: The name of the queue to create.
        :param metadata:
            A dict with name_value pairs to associate with the
            queue as metadata. Example: {'Category': 'test'}
        :type metadata: dict(str, str)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.queue.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service.py
                :start-after: [START qsc_create_queue]
                :end-before: [END qsc_create_queue]
                :language: python
                :dedent: 8
                :caption: Create a queue in the service.
        """
        timeout = kwargs.pop('timeout', None)
        queue = self.get_queue_client(name)
        kwargs.setdefault('merge_span', True)
        queue.create_queue(
            metadata=metadata, timeout=timeout, **kwargs)
        return queue

    @distributed_trace
    def delete_queue(
            self,
            queue,  # type: Union[QueueProperties, str]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        """Deletes the specified queue and any messages it contains.

        When a queue is successfully deleted, it is immediately marked for deletion
        and is no longer accessible to clients. The queue is later removed from
        the Queue service during garbage collection.

        Note that deleting a queue is likely to take at least 40 seconds to complete.
        If an operation is attempted against the queue while it was being deleted,
        an :class:`HttpResponseError` will be thrown.

        :param queue:
            The queue to delete. This can either be the name of the queue,
            or an instance of QueueProperties.
        :type queue: str or ~azure.storage.queue.QueueProperties
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service.py
                :start-after: [START qsc_delete_queue]
                :end-before: [END qsc_delete_queue]
                :language: python
                :dedent: 12
                :caption: Delete a queue in the service.
        """
        timeout = kwargs.pop('timeout', None)
        queue_client = self.get_queue_client(queue)
        kwargs.setdefault('merge_span', True)
        queue_client.delete_queue(timeout=timeout, **kwargs)

    def get_queue_client(self,
                         queue,  # type: Union[QueueProperties, str]
                         **kwargs  # type: Any
                         ):
        # type: (...) -> QueueClient
        """Get a client to interact with the specified queue.

        The queue need not already exist.

        :param queue:
            The queue. This can either be the name of the queue,
            or an instance of QueueProperties.
        :type queue: str or ~azure.storage.queue.QueueProperties
        :returns: A :class:`~azure.storage.queue.QueueClient` object.
        :rtype: ~azure.storage.queue.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service.py
                :start-after: [START get_queue_client]
                :end-before: [END get_queue_client]
                :language: python
                :dedent: 8
                :caption: Get the queue client.
        """
        try:
            queue_name = queue.name
        except AttributeError:
            queue_name = queue

        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )

        return QueueClient(
            self.url, queue_name=queue_name, credential=self.credential,
            key_resolver_function=self.key_resolver_function, require_encryption=self.require_encryption,
            encryption_version=self.encryption_version, key_encryption_key=self.key_encryption_key,
            api_version=self.api_version, _pipeline=_pipeline, _configuration=self._config,
            _location_mode=self._location_mode, _hosts=self._hosts, **kwargs)
