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
    AnyStr,
    Callable,
    Dict,
    List,
    IO,
    Iterable,
    Iterator,
    Optional,
    overload,
    Union,
)
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.pipeline.transport import HttpResponse
from azure.core.tracing.decorator import distributed_trace
from ._blob_client import BlobClient
from ._blob_service_client import BlobServiceClient
from ._download import StorageStreamDownloader
from ._encryption import StorageEncryptionMixin
from ._generated.models import RehydratePriority
from ._lease import BlobLeaseClient
from ._list_blobs_helper import BlobPrefix
from ._models import (
    AccessPolicy,
    BlobProperties,
    BlobType,
    ContainerEncryptionScope,
    ContainerProperties,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    FilteredBlob,
    PremiumPageBlobTier,
    PublicAccess,
    StandardBlobTier,
)
from ._shared.base_client import StorageAccountHostsMixin

class ContainerClient(StorageAccountHostsMixin, StorageEncryptionMixin):
    account_name: str
    container_name: str
    def __init__(
        self,
        account_url: str,
        container_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    def close(self) -> None: ...
    @classmethod
    def from_container_url(
        cls,
        container_url: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any,
    ) -> Self: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        container_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any,
    ) -> Self: ...
    @distributed_trace
    def create_container(
        self,
        metadata: Optional[Dict[str, str]] = None,
        public_access: Optional[Union[PublicAccess, str]] = None,
        *,
        container_encryption_scope: Optional[Union[Dict[str, Any], ContainerEncryptionScope]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def _rename_container(
        self,
        new_name: str,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> "ContainerClient": ...
    @distributed_trace
    def delete_container(
        self,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> None: ...
    @distributed_trace
    def acquire_lease(
        self,
        lease_duration: int = -1,
        lease_id: Optional[str] = None,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> BlobLeaseClient: ...
    @distributed_trace
    def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...
    @distributed_trace
    def get_container_properties(
        self, *, lease: Optional[Union[BlobLeaseClient, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> ContainerProperties: ...
    @distributed_trace
    def exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace
    def set_container_metadata(
        self,
        metadata: Optional[Dict[str, str]] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def _get_blob_service_client(self) -> BlobServiceClient: ...
    @distributed_trace
    def get_container_access_policy(
        self, *, lease: Optional[Union[BlobLeaseClient, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def set_container_access_policy(
        self,
        signed_identifiers: Dict[str, AccessPolicy],
        public_access: Optional[Union[str, PublicAccess]] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def list_blobs(
        self,
        name_starts_with: Optional[str] = None,
        include: Optional[Union[str, List[str]]] = None,
        *,
        results_per_page: Optional[int] = None,
        start_from: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> ItemPaged[BlobProperties]: ...
    @distributed_trace
    def list_blob_names(
        self,
        *,
        name_starts_with: Optional[str] = None,
        results_per_page: Optional[int] = None,
        start_from: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[str]: ...
    @distributed_trace
    def walk_blobs(
        self,
        name_starts_with: Optional[str] = None,
        include: Optional[Union[List[str], str]] = None,
        delimiter: str = "/",
        *,
        start_from: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> ItemPaged[Union[BlobProperties, BlobPrefix]]: ...
    @distributed_trace
    def find_blobs_by_tags(
        self,
        filter_expression: str,
        *,
        results_per_page: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> ItemPaged[FilteredBlob]: ...
    @distributed_trace
    def upload_blob(
        self,
        name: str,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        blob_type: Union[str, BlobType] = BlobType.BLOCKBLOB,
        length: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
        *,
        overwrite: Optional[bool] = None,
        content_settings: Optional[ContentSettings] = None,
        validate_content: Optional[bool] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        premium_page_blob_tier: Optional[PremiumPageBlobTier] = None,
        standard_blob_tier: Optional[StandardBlobTier] = None,
        maxsize_condition: Optional[int] = None,
        max_concurrency: Optional[int] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        encoding: Optional[str] = None,
        progress_hook: Optional[Callable[[int, Optional[int]], None]] = None,
        **kwargs: Any,
    ) -> BlobClient: ...
    @distributed_trace
    def delete_blob(
        self,
        blob: str,
        delete_snapshots: Optional[str] = None,
        *,
        version_id: Optional[str] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def download_blob(
        self,
        blob: str,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        version_id: Optional[str] = None,
        validate_content: Optional[bool] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: Optional[int] = None,
        encoding: str,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        timeout: Optional[int] = None,
    ) -> StorageStreamDownloader[str]: ...
    @overload
    def download_blob(
        self,
        blob: str,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        version_id: Optional[str] = None,
        validate_content: Optional[bool] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: Optional[int] = None,
        encoding: None = None,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> StorageStreamDownloader[bytes]: ...
    @distributed_trace  # type: ignore[misc]
    def download_blob(
        self,
        blob: str,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        version_id: Optional[str] = None,
        validate_content: Optional[bool] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: Optional[int] = None,
        encoding: Optional[str] = None,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> Union[StorageStreamDownloader[str], StorageStreamDownloader[bytes]]: ...
    @distributed_trace
    def delete_blobs(
        self,
        *blobs: Union[str, Dict[str, Any], BlobProperties],
        delete_snapshots: Optional[str] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        if_tags_match_condition: Optional[str] = None,
        raise_on_any_failure: bool = True,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[HttpResponse]: ...
    @distributed_trace
    def set_standard_blob_tier_blobs(
        self,
        standard_blob_tier: Optional[Union[str, StandardBlobTier]],
        *blobs: Union[str, Dict[str, Any], BlobProperties],
        rehydrate_priority: Optional[RehydratePriority] = None,
        if_tags_match_condition: Optional[str] = None,
        raise_on_any_failure: bool = True,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[HttpResponse]: ...
    @distributed_trace
    def set_premium_page_blob_tier_blobs(
        self,
        premium_page_blob_tier: Optional[Union[str, PremiumPageBlobTier]],
        *blobs: Union[str, Dict[str, Any], BlobProperties],
        raise_on_any_failure: bool = True,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[HttpResponse]: ...
    def get_blob_client(
        self, blob: str, snapshot: Optional[str] = None, *, version_id: Optional[str] = None
    ) -> BlobClient: ...
