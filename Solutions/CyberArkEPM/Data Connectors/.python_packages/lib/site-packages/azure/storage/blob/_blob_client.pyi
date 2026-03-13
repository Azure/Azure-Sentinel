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
    IO,
    Iterable,
    List,
    Literal,
    Optional,
    overload,
    Tuple,
    Union,
)
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._container_client import ContainerClient
from ._download import StorageStreamDownloader
from ._encryption import StorageEncryptionMixin
from ._generated.models import RehydratePriority
from ._lease import BlobLeaseClient
from ._models import (
    ArrowDialect,
    BlobBlock,
    BlobProperties,
    BlobQueryError,
    BlobType,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    DelimitedTextDialect,
    DelimitedJsonDialect,
    ImmutabilityPolicy,
    PageRange,
    PremiumPageBlobTier,
    QuickQueryDialect,
    SequenceNumberAction,
    StandardBlobTier,
)
from ._quick_query_helper import BlobQueryReader
from ._shared.base_client import StorageAccountHostsMixin

class BlobClient(StorageAccountHostsMixin, StorageEncryptionMixin):
    container_name: str
    blob_name: str
    snapshot: Optional[str]
    version_id: Optional[str]
    def __init__(
        self,
        account_url: str,
        container_name: str,
        blob_name: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        version_id: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None: ...
    def close(self) -> None: ...
    @classmethod
    def from_blob_url(
        cls,
        blob_url: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        version_id: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any
    ) -> Self: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        container_name: str,
        blob_name: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        version_id: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...
    @distributed_trace
    def upload_blob_from_url(
        self,
        source_url: str,
        *,
        metadata: Optional[Dict[str, str]] = None,
        overwrite: Optional[bool] = None,
        include_source_blob_properties: bool = True,
        tags: Optional[Dict[str, str]] = None,
        source_content_md5: Optional[bytearray] = None,
        source_if_modified_since: Optional[datetime] = None,
        source_if_unmodified_since: Optional[datetime] = None,
        source_etag: Optional[str] = None,
        source_match_condition: Optional[MatchConditions] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        destination_lease: Optional[Union[BlobLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        content_settings: Optional[ContentSettings] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        standard_blob_tier: Optional[StandardBlobTier] = None,
        source_authorization: Optional[str] = None,
        source_token_intent: Optional[Literal["backup"]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def upload_blob(
        self,
        data: Union[bytes, str, Iterable[AnyStr], IO[bytes]],
        blob_type: Union[str, BlobType] = BlobType.BLOCKBLOB,
        length: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
        *,
        tags: Optional[Dict[str, str]] = None,
        overwrite: bool = False,
        content_settings: Optional[ContentSettings] = None,
        validate_content: bool = False,
        lease: Optional[BlobLeaseClient] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        premium_page_blob_tier: Optional[PremiumPageBlobTier] = None,
        immutability_policy: Optional[ImmutabilityPolicy] = None,
        legal_hold: Optional[bool] = None,
        standard_blob_tier: Optional[StandardBlobTier] = None,
        maxsize_condition: Optional[int] = None,
        max_concurrency: int = 1,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        encoding: str = "UTF-8",
        progress_hook: Optional[Callable[[int, Optional[int]], None]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @overload
    def download_blob(
        self,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        version_id: Optional[str] = None,
        validate_content: bool = False,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: int = 1,
        encoding: str,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        decompress: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> StorageStreamDownloader[str]: ...
    @overload
    def download_blob(
        self,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        version_id: Optional[str] = None,
        validate_content: bool = False,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: int = 1,
        encoding: None = None,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        decompress: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> StorageStreamDownloader[bytes]: ...
    @distributed_trace  # type: ignore[misc]
    def download_blob(
        self,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        version_id: Optional[str] = None,
        validate_content: bool = False,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: int = 1,
        encoding: Optional[str] = None,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        decompress: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Union[StorageStreamDownloader[str], StorageStreamDownloader[bytes]]: ...
    @distributed_trace
    def query_blob(
        self,
        query_expression: str,
        *,
        on_error: Optional[Callable[[BlobQueryError], None]] = None,
        blob_format: Optional[Union[DelimitedTextDialect, DelimitedJsonDialect, QuickQueryDialect, str]] = None,
        output_format: Optional[
            Union[DelimitedTextDialect, DelimitedJsonDialect, QuickQueryDialect, List[ArrowDialect], str]
        ] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> BlobQueryReader: ...
    @distributed_trace
    def delete_blob(
        self,
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
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def undelete_blob(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def exists(self, *, version_id: Optional[str] = None, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace
    def get_blob_properties(
        self,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        version_id: Optional[str] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> BlobProperties: ...
    @distributed_trace
    def set_http_headers(
        self,
        content_settings: Optional[ContentSettings] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def set_blob_metadata(
        self,
        metadata: Optional[Dict[str, str]] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def set_immutability_policy(
        self,
        immutability_policy: ImmutabilityPolicy,
        *,
        version_id: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, str]: ...
    @distributed_trace
    def delete_immutability_policy(
        self, *, version_id: Optional[str] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def set_legal_hold(
        self, legal_hold: bool, *, version_id: Optional[str] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Union[str, datetime, bool]]: ...
    @distributed_trace
    def create_page_blob(
        self,
        size: int,
        content_settings: Optional[ContentSettings] = None,
        metadata: Optional[Dict[str, str]] = None,
        premium_page_blob_tier: Optional[Union[str, PremiumPageBlobTier]] = None,
        *,
        tags: Optional[Dict[str, str]] = None,
        sequence_number: Optional[int] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        immutability_policy: Optional[ImmutabilityPolicy] = None,
        legal_hold: Optional[bool] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def create_append_blob(
        self,
        content_settings: Optional[ContentSettings] = None,
        metadata: Optional[Dict[str, str]] = None,
        *,
        tags: Optional[Dict[str, str]] = None,
        immutability_policy: Optional[ImmutabilityPolicy] = None,
        legal_hold: Optional[bool] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def create_snapshot(
        self,
        metadata: Optional[Dict[str, str]] = None,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def start_copy_from_url(
        self,
        source_url: str,
        metadata: Optional[Dict[str, str]] = None,
        incremental_copy: bool = False,
        *,
        tags: Optional[Union[Dict[str, str], Literal["COPY"]]] = None,
        immutability_policy: Optional[ImmutabilityPolicy] = None,
        legal_hold: Optional[bool] = None,
        source_if_modified_since: Optional[datetime] = None,
        source_if_unmodified_since: Optional[datetime] = None,
        source_etag: Optional[str] = None,
        source_match_condition: Optional[MatchConditions] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        destination_lease: Optional[Union[BlobLeaseClient, str]] = None,
        source_lease: Optional[Union[BlobLeaseClient, str]] = None,
        premium_page_blob_tier: Optional[PremiumPageBlobTier] = None,
        standard_blob_tier: Optional[StandardBlobTier] = None,
        rehydrate_priority: Optional[RehydratePriority] = None,
        seal_destination_blob: Optional[bool] = None,
        requires_sync: Optional[bool] = None,
        source_authorization: Optional[str] = None,
        source_token_intent: Optional[Literal["backup"]] = None,
        encryption_scope: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def abort_copy(self, copy_id: Union[str, Dict[str, Any], BlobProperties], **kwargs: Any) -> None: ...
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
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> BlobLeaseClient: ...
    @distributed_trace
    def set_standard_blob_tier(
        self,
        standard_blob_tier: Union[str, StandardBlobTier],
        *,
        rehydrate_priority: Optional[RehydratePriority] = None,
        version_id: Optional[str] = None,
        if_tags_match_condition: Optional[str] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def stage_block(
        self,
        block_id: str,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        length: Optional[int] = None,
        *,
        validate_content: Optional[bool] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        encoding: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def stage_block_from_url(
        self,
        block_id: str,
        source_url: str,
        source_offset: Optional[int] = None,
        source_length: Optional[int] = None,
        source_content_md5: Optional[Union[bytes, bytearray]] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        source_authorization: Optional[str] = None,
        source_token_intent: Optional[Literal["backup"]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def get_block_list(
        self,
        block_list_type: str = "committed",
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Tuple[List[BlobBlock], List[BlobBlock]]: ...
    @distributed_trace
    def commit_block_list(
        self,
        block_list: List[BlobBlock],
        content_settings: Optional[ContentSettings] = None,
        metadata: Optional[Dict[str, str]] = None,
        *,
        tags: Optional[Dict[str, str]] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        immutability_policy: Optional[ImmutabilityPolicy] = None,
        legal_hold: Optional[bool] = None,
        validate_content: Optional[bool] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        standard_blob_tier: Optional[StandardBlobTier] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def set_premium_page_blob_tier(
        self,
        premium_page_blob_tier: PremiumPageBlobTier,
        *,
        if_tags_match_condition: Optional[str] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def set_blob_tags(
        self,
        tags: Optional[Dict[str, str]] = None,
        *,
        version_id: Optional[str] = None,
        validate_content: Optional[bool] = None,
        if_tags_match_condition: Optional[str] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def get_blob_tags(
        self,
        *,
        version_id: Optional[str] = None,
        if_tags_match_condition: Optional[str] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, str]: ...
    @distributed_trace
    def get_page_ranges(
        self,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        previous_snapshot_diff: Optional[Union[str, Dict[str, Any]]] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...
    @distributed_trace
    def list_page_ranges(
        self,
        *,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        previous_snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        results_per_page: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[PageRange]: ...
    @distributed_trace
    def get_page_range_diff_for_managed_disk(
        self,
        previous_snapshot_url: str,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...
    @distributed_trace
    def set_sequence_number(
        self,
        sequence_number_action: Union[str, SequenceNumberAction],
        sequence_number: Optional[str] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def resize_blob(
        self,
        size: int,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        premium_page_blob_tier: Optional[PremiumPageBlobTier] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def upload_page(
        self,
        page: bytes,
        offset: int,
        length: int,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        validate_content: Optional[bool] = None,
        if_sequence_number_lte: Optional[int] = None,
        if_sequence_number_lt: Optional[int] = None,
        if_sequence_number_eq: Optional[int] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        encoding: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def upload_pages_from_url(
        self,
        source_url: str,
        offset: int,
        length: int,
        source_offset: int,
        *,
        source_content_md5: Optional[bytes] = None,
        source_if_modified_since: Optional[datetime] = None,
        source_if_unmodified_since: Optional[datetime] = None,
        source_etag: Optional[str] = None,
        source_match_condition: Optional[MatchConditions] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_sequence_number_lte: Optional[int] = None,
        if_sequence_number_lt: Optional[int] = None,
        if_sequence_number_eq: Optional[int] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        source_authorization: Optional[str] = None,
        source_token_intent: Optional[Literal["backup"]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def clear_page(
        self,
        offset: int,
        length: int,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_sequence_number_lte: Optional[int] = None,
        if_sequence_number_lt: Optional[int] = None,
        if_sequence_number_eq: Optional[int] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def append_block(
        self,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        length: Optional[int] = None,
        *,
        validate_content: Optional[bool] = None,
        maxsize_condition: Optional[int] = None,
        appendpos_condition: Optional[int] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        encoding: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime, int]]: ...
    @distributed_trace
    def append_block_from_url(
        self,
        copy_source_url: str,
        source_offset: Optional[int] = None,
        source_length: Optional[int] = None,
        *,
        source_content_md5: Optional[bytearray] = None,
        maxsize_condition: Optional[int] = None,
        appendpos_condition: Optional[int] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        source_if_modified_since: Optional[datetime] = None,
        source_if_unmodified_since: Optional[datetime] = None,
        source_etag: Optional[str] = None,
        source_match_condition: Optional[MatchConditions] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        source_authorization: Optional[str] = None,
        source_token_intent: Optional[Literal["backup"]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime, int]]: ...
    @distributed_trace
    def seal_append_blob(
        self,
        *,
        appendpos_condition: Optional[int] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime, int]]: ...
    @distributed_trace
    def _get_container_client(self) -> ContainerClient: ...
