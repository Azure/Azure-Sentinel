# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from typing import Any, Optional, Union

from azure.core import MatchConditions
from azure.core.tracing.decorator_async import distributed_trace_async
from ._blob_client_async import BlobClient
from ._container_client_async import ContainerClient

class BlobLeaseClient:
    id: str
    etag: Optional[str]
    last_modified: Optional[datetime]
    def __init__(self, client: Union[BlobClient, ContainerClient], lease_id: Optional[str] = None) -> None: ...
    @distributed_trace_async
    async def acquire(
        self,
        lease_duration: int = -1,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def renew(
        self,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def release(
        self,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def change(
        self,
        proposed_lease_id: str,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def break_lease(
        self,
        lease_break_period: Optional[int] = None,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> int: ...
