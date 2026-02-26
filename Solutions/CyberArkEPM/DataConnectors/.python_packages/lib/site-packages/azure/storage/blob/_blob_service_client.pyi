# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: skip-file

from datetime import datetime
from types import TracebackType
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._blob_client import BlobClient
from ._container_client import ContainerClient
from ._encryption import StorageEncryptionMixin
from ._lease import BlobLeaseClient
from ._models import (
    BlobAnalyticsLogging,
    ContainerEncryptionScope,
    ContainerProperties,
    CorsRule,
    FilteredBlob,
    Metrics,
    PublicAccess,
    RetentionPolicy,
    StaticWebsite,
)
from ._shared.base_client import StorageAccountHostsMixin
from ._shared.models import UserDelegationKey

class BlobServiceClient(StorageAccountHostsMixin, StorageEncryptionMixin):
    def __init__(
        self,
        account_url: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: bool = False,
        max_page_size: int = 4 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    def close(self) -> None: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: bool = False,
        max_page_size: int = 4 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def get_user_delegation_key(
        self, key_start_time: datetime, key_expiry_time: datetime, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> UserDelegationKey: ...
    @distributed_trace
    def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...
    @distributed_trace
    def get_service_stats(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]: ...
    @distributed_trace
    def get_service_properties(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]: ...
    @distributed_trace
    def set_service_properties(
        self,
        analytics_logging: Optional[BlobAnalyticsLogging] = None,
        hour_metrics: Optional[Metrics] = None,
        minute_metrics: Optional[Metrics] = None,
        cors: Optional[List[CorsRule]] = None,
        target_version: Optional[str] = None,
        delete_retention_policy: Optional[RetentionPolicy] = None,
        static_website: Optional[StaticWebsite] = None,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def list_containers(
        self,
        name_starts_with: Optional[str] = None,
        include_metadata: bool = False,
        *,
        include_deleted: Optional[bool] = None,
        include_system: Optional[bool] = None,
        results_per_page: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[ContainerProperties]: ...
    @distributed_trace
    def find_blobs_by_tags(
        self,
        filter_expression: str,
        *,
        results_per_page: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[FilteredBlob]: ...
    @distributed_trace
    def create_container(
        self,
        name: str,
        metadata: Optional[Dict[str, str]] = None,
        public_access: Optional[Union[PublicAccess, str]] = None,
        *,
        container_encryption_scope: Optional[Union[dict, ContainerEncryptionScope]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ContainerClient: ...
    @distributed_trace
    def delete_container(
        self,
        container: Union[ContainerProperties, str],
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def _rename_container(
        self,
        name: str,
        new_name: str,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ContainerClient: ...
    @distributed_trace
    def undelete_container(
        self,
        deleted_container_name: str,
        deleted_container_version: str,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ContainerClient: ...
    def get_container_client(self, container: Union[ContainerProperties, str]) -> ContainerClient: ...
    def get_blob_client(
        self,
        container: Union[ContainerProperties, str],
        blob: str,
        snapshot: Optional[Union[Dict[str, Any], str]] = None,
        *,
        version_id: Optional[str] = None
    ) -> BlobClient: ...
