# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid

from typing import (  # pylint: disable=unused-import
    Optional, Any, TypeVar, TYPE_CHECKING
)

from azure.core.tracing.decorator import distributed_trace

from ._shared.response_handlers import return_response_headers, process_storage_error
from ._generated.models import StorageErrorException
from ._generated.operations import FileOperations, ShareOperations

if TYPE_CHECKING:
    from datetime import datetime
    ShareFileClient = TypeVar("ShareFileClient")
    ShareClient = TypeVar("ShareClient")


class ShareLeaseClient(object):
    """Creates a new ShareLeaseClient.

    This client provides lease operations on a ShareFileClient.

    :ivar str id:
        The ID of the lease currently being maintained. This will be `None` if no
        lease has yet been acquired.
    :ivar str etag:
        The ETag of the lease currently being maintained. This will be `None` if no
        lease has yet been acquired or modified.
    :ivar ~datetime.datetime last_modified:
        The last modified timestamp of the lease currently being maintained.
        This will be `None` if no lease has yet been acquired or modified.

    :param client:
        The client of the file to lease.
    :type client: ~azure.storage.fileshare.ShareFileClient
    :param str lease_id:
        A string representing the lease ID of an existing lease. This value does not
        need to be specified in order to acquire a new lease, or break one.
    """
    def __init__(
            self, client, lease_id=None
    ):  # pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
        # type: (ShareFileClient, Optional[str]) -> None
        self.id = lease_id or str(uuid.uuid4())
        self.last_modified = None
        self.etag = None
        if hasattr(client, 'file_name'):
            self._client = client._client.file  # type: ignore # pylint: disable=protected-access
            self._snapshot = None
        elif hasattr(client, 'share_name'):
            self._client = client._client.share
            self._snapshot = client.snapshot
        else:
            raise TypeError("Lease must use ShareFileClient or ShareClient.")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()

    @distributed_trace
    def acquire(self, **kwargs):
        # type: (**Any) -> None
        """Requests a new lease. This operation establishes and manages a lock on a
        file for write and delete operations. If the file does not have an active lease,
        the File service creates a lease on the file. If the file has an active lease,
        you can only request a new lease using the active lease ID.


        If the file does not have an active lease, the File service creates a
        lease on the file and returns a new lease ID.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        try:
            lease_duration = kwargs.pop('lease_duration', -1)
            if self._snapshot:
                kwargs['sharesnapshot'] = self._snapshot
            response = self._client.acquire_lease(
                timeout=kwargs.pop('timeout', None),
                duration=lease_duration,
                proposed_lease_id=self.id,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime
        self.etag = response.get('etag')  # type: str

    @distributed_trace
    def _renew(self, **kwargs):
        # type: (Any) -> None
        """Renews the share lease.

        The share lease can be renewed if the lease ID specified in the
        lease client matches that associated with the share. Note that
        the lease may be renewed even if it has expired as long as the share
        has not been leased again since the expiration of that lease. When you
        renew a lease, the lease duration clock resets.

        .. versionadded:: 12.6.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        if isinstance(self._client, FileOperations):
            raise TypeError("Lease renewal operations are only valid for ShareClient.")
        try:
            response = self._client.renew_lease(
                lease_id=self.id,
                timeout=kwargs.pop('timeout', None),
                sharesnapshot=self._snapshot,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    @distributed_trace
    def release(self, **kwargs):
        # type: (Any) -> None
        """Releases the lease. The lease may be released if the lease ID specified on the request matches
        that associated with the file. Releasing the lease allows another client to immediately acquire
        the lease for the or file as soon as the release is complete.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        try:
            if self._snapshot:
                kwargs['sharesnapshot'] = self._snapshot
            response = self._client.release_lease(
                lease_id=self.id,
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    @distributed_trace
    def change(self, proposed_lease_id, **kwargs):
        # type: (str, Any) -> None
        """ Changes the lease ID of an active lease. A change must include the current lease ID in x-ms-lease-id and
        a new lease ID in x-ms-proposed-lease-id.

        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The File service will raise an error
            (Invalid request) if the proposed lease ID is not in the correct format.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        try:
            if self._snapshot:
                kwargs['sharesnapshot'] = self._snapshot
            response = self._client.change_lease(
                lease_id=self.id,
                proposed_lease_id=proposed_lease_id,
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    @distributed_trace
    def break_lease(self, **kwargs):
        # type: (Any) -> int
        """Force breaks the lease if the file has an active lease. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID. An infinite lease breaks immediately.

        Once a lease is broken, it cannot be changed. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID.
        When a lease is successfully broken, the response indicates the interval
        in seconds until a new lease can be acquired.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: Approximate time remaining in the lease period, in seconds.
        :rtype: int
        """
        try:
            lease_break_period = kwargs.pop('lease_break_period', None)
            if self._snapshot:
                kwargs['sharesnapshot'] = self._snapshot
            if isinstance(self._client, ShareOperations):
                kwargs['break_period'] = lease_break_period
            if isinstance(self._client, FileOperations) and lease_break_period:
                raise TypeError("Setting a lease break period is only applicable to Share leases.")

            response = self._client.break_lease(
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return response.get('lease_time')  # type: ignore
