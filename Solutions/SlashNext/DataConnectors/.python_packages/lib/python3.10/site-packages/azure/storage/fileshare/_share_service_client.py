# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Dict, List,
    TYPE_CHECKING
)


try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import Pipeline
from ._shared.base_client import StorageAccountHostsMixin, TransportWrapper, parse_connection_str, parse_query
from ._shared.response_handlers import process_storage_error
from ._generated import AzureFileStorage
from ._generated.models import StorageServiceProperties
from ._share_client import ShareClient
from ._serialize import get_api_version
from ._models import (
    SharePropertiesPaged,
    service_properties_deserialize,
)

if TYPE_CHECKING:
    from datetime import datetime
    from ._models import (
        ShareProperties,
        Metrics,
        CorsRule,
        ShareProtocolSettings
    )


class ShareServiceClient(StorageAccountHostsMixin):
    """A client to interact with the File Share Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete shares within the account.
    For operations relating to a specific share, a client for that entity
    can also be retrieved using the :func:`get_share_client` function.

    For more optional configuration, please click
    `here <https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-share
    #optional-configuration>`_.

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
    :keyword int max_range_size: The maximum range size used for a file upload. Defaults to 4*1024*1024.

    .. admonition:: Example:

        .. literalinclude:: ../samples/file_samples_authentication.py
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
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))
        if hasattr(credential, 'get_token'):
            raise ValueError("Token credentials not supported by the File Share service.")

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account shared key or SAS token when creating a storage service.')
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(ShareServiceClient, self).__init__(parsed_url, service='file-share', credential=credential, **kwargs)
        self._client = AzureFileStorage(url=self.url, pipeline=self._pipeline)
        default_api_version = self._client._config.version  # pylint: disable=protected-access
        self._client._config.version = get_api_version(kwargs, default_api_version) # pylint: disable=protected-access

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}/{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            credential=None, # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> ShareServiceClient
        """Create ShareServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credential with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials or an account
            shared access key.
        :returns: A File Share service client.
        :rtype: ~azure.storage.fileshare.ShareServiceClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_authentication.py
                :start-after: [START create_share_service_client_from_conn_string]
                :end-before: [END create_share_service_client_from_conn_string]
                :language: python
                :dedent: 8
                :caption: Create the share service client with connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    @distributed_trace
    def get_service_properties(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Gets the properties of a storage account's File Share service, including
        Azure Storage Analytics.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A dictionary containing file service properties such as
            analytics logging, hour/minute metrics, cors rules, etc.
        :rtype: Dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START get_service_properties]
                :end-before: [END get_service_properties]
                :language: python
                :dedent: 8
                :caption: Get file share service properties.
        """
        timeout = kwargs.pop('timeout', None)
        try:
            service_props = self._client.service.get_properties(timeout=timeout, **kwargs)
            return service_properties_deserialize(service_props)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def set_service_properties(
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
        :param protocol:
            Sets protocol settings
        :type protocol: ~azure.storage.fileshare.ShareProtocolSettings
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
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
            self._client.service.set_properties(storage_service_properties=props, timeout=timeout, **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_shares(
            self, name_starts_with=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            include_snapshots=False, # type: Optional[bool]
            **kwargs
        ):
        # type: (...) -> ItemPaged[ShareProperties]
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
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.fileshare.ShareProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START fsc_list_shares]
                :end-before: [END fsc_list_shares]
                :language: python
                :dedent: 12
                :caption: List shares in the file share service.
        """
        timeout = kwargs.pop('timeout', None)
        include = []
        include_deleted = kwargs.pop('include_deleted', None)
        if include_deleted:
            include.append("deleted")
        if include_metadata:
            include.append('metadata')
        if include_snapshots:
            include.append('snapshots')

        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.service.list_shares_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=SharePropertiesPaged)

    @distributed_trace
    def create_share(
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
        :rtype: ~azure.storage.fileshare.ShareClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START fsc_create_shares]
                :end-before: [END fsc_create_shares]
                :language: python
                :dedent: 8
                :caption: Create a share in the file share service.
        """
        metadata = kwargs.pop('metadata', None)
        quota = kwargs.pop('quota', None)
        timeout = kwargs.pop('timeout', None)
        share = self.get_share_client(share_name)
        kwargs.setdefault('merge_span', True)
        share.create_share(metadata=metadata, quota=quota, timeout=timeout, **kwargs)
        return share

    @distributed_trace
    def delete_share(
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

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START fsc_delete_shares]
                :end-before: [END fsc_delete_shares]
                :language: python
                :dedent: 12
                :caption: Delete a share in the file share service.
        """
        timeout = kwargs.pop('timeout', None)
        share = self.get_share_client(share_name)
        kwargs.setdefault('merge_span', True)
        share.delete_share(
            delete_snapshots=delete_snapshots, timeout=timeout, **kwargs)

    @distributed_trace
    def undelete_share(self, deleted_share_name, deleted_share_version, **kwargs):
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
        :rtype: ~azure.storage.fileshare.ShareClient
        """
        share = self.get_share_client(deleted_share_name)

        try:
            share._client.share.restore(deleted_share_name=deleted_share_name,  # pylint: disable = protected-access
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
        :rtype: ~azure.storage.fileshare.ShareClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
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

        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return ShareClient(
            self.url, share_name=share_name, snapshot=snapshot, credential=self.credential,
            api_version=self.api_version, _hosts=self._hosts,
            _configuration=self._config, _pipeline=_pipeline, _location_mode=self._location_mode)
