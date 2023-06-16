# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=invalid-overridden-method
import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List,
    TYPE_CHECKING
)

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator_async import distributed_trace_async

from .._shared.base_client_async import AsyncStorageAccountHostsMixin, AsyncTransportWrapper
from .._shared.response_handlers import process_storage_error
from .._shared.policies_async import ExponentialRetry
from .._generated.aio import AzureFileStorage
from .._generated.models import StorageServiceProperties
from .._share_service_client import ShareServiceClient as ShareServiceClientBase
from .._serialize import get_api_version
from ._share_client_async import ShareClient
from ._models import SharePropertiesPaged
from .._models import service_properties_deserialize

if TYPE_CHECKING:
    from datetime import datetime
    from .._shared.models import ResourceTypes, AccountSasPermissions
    from .._models import (
        ShareProperties,
        Metrics,
        CorsRule,
        ShareProtocolSettings,
    )


class ShareServiceClient(AsyncStorageAccountHostsMixin, ShareServiceClientBase):
    """A client to interact with the File Share Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete shares within the account.
    For operations relating to a specific share, a client for that entity
    can also be retrieved using the :func:`get_share_client` function.

    :param str account_url:
        The URL to the file share storage account. Any other entities included
        in the URL path (e.g. share or file) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :param credential:
        The credential with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential from azure.core.credentials or an account
        shared access key.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-07-07'.
        Setting to an older version may result in reduced feature compatibility.

        .. versionadded:: 12.1.0

    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword loop:
        The event loop to run the asynchronous tasks.
    :keyword int max_range_size: The maximum range size used for a file upload. Defaults to 4*1024*1024.

    .. admonition:: Example:

        .. literalinclude:: ../samples/file_samples_authentication_async.py
            :start-after: [START create_share_service_client]
            :end-before: [END create_share_service_client]
            :language: python
            :dedent: 8
            :caption: Create the share service client with url and credential.
    """
    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        kwargs['retry_policy'] = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
        loop = kwargs.pop('loop', None)
        super(ShareServiceClient, self).__init__(
            account_url,
            credential=credential,
            loop=loop,
            **kwargs)
        self._client = AzureFileStorage(url=self.url, pipeline=self._pipeline, loop=loop)
        default_api_version = self._client._config.version  # pylint: disable=protected-access
        self._client._config.version = get_api_version(kwargs, default_api_version)  # pylint: disable=protected-access
        self._loop = loop

    @distributed_trace_async
    async def get_service_properties(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Gets the properties of a storage account's File Share service, including
        Azure Storage Analytics.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A dictionary containing file service properties such as
            analytics logging, hour/minute metrics, cors rules, etc.
        :rtype: Dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service_async.py
                :start-after: [START get_service_properties]
                :end-before: [END get_service_properties]
                :language: python
                :dedent: 12
                :caption: Get file share service properties.
        """
        timeout = kwargs.pop('timeout', None)
        try:
            service_props = await self._client.service.get_properties(timeout=timeout, **kwargs)
            return service_properties_deserialize(service_props)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_service_properties(
            self, hour_metrics=None,  # type: Optional[Metrics]
            minute_metrics=None,  # type: Optional[Metrics]
            cors=None,  # type: Optional[List[CorsRule]]
            protocol=None,  # type: Optional[ShareProtocolSettings],
            **kwargs
        ):
        # type: (...) -> None
        """Sets the properties of a storage account's File Share service, including
        Azure Storage Analytics. If an element (e.g. hour_metrics) is left as None, the
        existing settings on the service for that functionality are preserved.

        :param hour_metrics:
            The hour metrics settings provide a summary of request
            statistics grouped by API in hourly aggregates for files.
        :type hour_metrics: ~azure.storage.fileshare.Metrics
        :param minute_metrics:
            The minute metrics settings provide request statistics
            for each minute for files.
        :type minute_metrics: ~azure.storage.fileshare.Metrics
        :param cors:
            You can include up to five CorsRule elements in the
            list. If an empty list is specified, all CORS rules will be deleted,
            and CORS will be disabled for the service.
        :type cors: list(:class:`~azure.storage.fileshare.CorsRule`)
        :param protocol_settings:
            Sets protocol settings
        :type protocol: ~azure.storage.fileshare.ShareProtocolSettings
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service_async.py
                :start-after: [START set_service_properties]
                :end-before: [END set_service_properties]
                :language: python
                :dedent: 8
                :caption: Sets file share service properties.
        """
        timeout = kwargs.pop('timeout', None)
        props = StorageServiceProperties(
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors,
            protocol=protocol
        )
        try:
            await self._client.service.set_properties(props, timeout=timeout, **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_shares(
            self, name_starts_with=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            include_snapshots=False, # type: Optional[bool]
            **kwargs  # type: Any
        ):  # type: (...) -> AsyncItemPaged
        """Returns auto-paging iterable of dict-like ShareProperties under the specified account.
        The generator will lazily follow the continuation tokens returned by
        the service and stop when all shares have been returned.

        :param str name_starts_with:
            Filters the results to return only shares whose names
            begin with the specified name_starts_with.
        :param bool include_metadata:
            Specifies that share metadata be returned in the response.
        :param bool include_snapshots:
            Specifies that share snapshot be returned in the response.
        :keyword bool include_deleted:
            Specifies that deleted shares be returned in the response.
            This is only for share soft delete enabled account.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) of ShareProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.fileshare.ShareProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service_async.py
                :start-after: [START fsc_list_shares]
                :end-before: [END fsc_list_shares]
                :language: python
                :dedent: 16
                :caption: List shares in the file share service.
        """
        timeout = kwargs.pop('timeout', None)
        include = []
        if include_metadata:
            include.append('metadata')
        if include_snapshots:
            include.append('snapshots')
        include_deleted = kwargs.pop('include_deleted', None)
        if include_deleted:
            include.append("deleted")

        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.service.list_shares_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return AsyncItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=SharePropertiesPaged)

    @distributed_trace_async
    async def create_share(
            self, share_name,  # type: str
            **kwargs
        ):
        # type: (...) -> ShareClient
        """Creates a new share under the specified account. If the share
        with the same name already exists, the operation fails. Returns a client with
        which to interact with the newly created share.

        :param str share_name: The name of the share to create.
        :keyword dict(str,str) metadata:
            A dict with name_value pairs to associate with the
            share as metadata. Example:{'Category':'test'}
        :keyword int quota:
            Quota in bytes.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.fileshare.aio.ShareClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service_async.py
                :start-after: [START fsc_create_shares]
                :end-before: [END fsc_create_shares]
                :language: python
                :dedent: 12
                :caption: Create a share in the file share service.
        """
        metadata = kwargs.pop('metadata', None)
        quota = kwargs.pop('quota', None)
        timeout = kwargs.pop('timeout', None)
        share = self.get_share_client(share_name)
        kwargs.setdefault('merge_span', True)
        await share.create_share(metadata=metadata, quota=quota, timeout=timeout, **kwargs)
        return share

    @distributed_trace_async
    async def delete_share(
            self, share_name,  # type: Union[ShareProperties, str]
            delete_snapshots=False, # type: Optional[bool]
            **kwargs
        ):
        # type: (...) -> None
        """Marks the specified share for deletion. The share is
        later deleted during garbage collection.

        :param share_name:
            The share to delete. This can either be the name of the share,
            or an instance of ShareProperties.
        :type share_name: str or ~azure.storage.fileshare.ShareProperties
        :param bool delete_snapshots:
            Indicates if snapshots are to be deleted.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service_async.py
                :start-after: [START fsc_delete_shares]
                :end-before: [END fsc_delete_shares]
                :language: python
                :dedent: 16
                :caption: Delete a share in the file share service.
        """
        timeout = kwargs.pop('timeout', None)
        share = self.get_share_client(share_name)
        kwargs.setdefault('merge_span', True)
        await share.delete_share(
            delete_snapshots=delete_snapshots, timeout=timeout, **kwargs)

    @distributed_trace_async
    async def undelete_share(self, deleted_share_name, deleted_share_version, **kwargs):
        # type: (str, str, **Any) -> ShareClient
        """Restores soft-deleted share.

        Operation will only be successful if used within the specified number of days
        set in the delete retention policy.

        .. versionadded:: 12.2.0
            This operation was introduced in API version '2019-12-12'.

        :param str deleted_share_name:
            Specifies the name of the deleted share to restore.
        :param str deleted_share_version:
            Specifies the version of the deleted share to restore.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.fileshare.aio.ShareClient
        """
        share = self.get_share_client(deleted_share_name)
        try:
            await share._client.share.restore(deleted_share_name=deleted_share_name,  # pylint: disable = protected-access
                                              deleted_share_version=deleted_share_version,
                                              timeout=kwargs.pop('timeout', None), **kwargs)
            return share
        except HttpResponseError as error:
            process_storage_error(error)

    def get_share_client(self, share, snapshot=None):
        # type: (Union[ShareProperties, str],Optional[Union[Dict[str, Any], str]]) -> ShareClient
        """Get a client to interact with the specified share.
        The share need not already exist.

        :param share:
            The share. This can either be the name of the share,
            or an instance of ShareProperties.
        :type share: str or ~azure.storage.fileshare.ShareProperties
        :param str snapshot:
            An optional share snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`create_snapshot`.
        :returns: A ShareClient.
        :rtype: ~azure.storage.fileshare.aio.ShareClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service_async.py
                :start-after: [START get_share_client]
                :end-before: [END get_share_client]
                :language: python
                :dedent: 8
                :caption: Gets the share client.
        """
        try:
            share_name = share.name
        except AttributeError:
            share_name = share

        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return ShareClient(
            self.url, share_name=share_name, snapshot=snapshot, credential=self.credential,
            api_version=self.api_version, _hosts=self._hosts, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode, loop=self._loop)
