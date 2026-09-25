"""
Shared Azure SDK client factories.

DefaultAzureCredential performs a probe across several credential
sources (environment, managed identity, Azure CLI, etc.) the first
time a token is requested. Constructing a new instance on every blob
or ingestion call (as the original code did) repeats that cost on
every single checkpoint read/write -- which happens once per page,
i.e. potentially dozens of times per hourly run -- and can also add
unnecessary load against the managed identity token endpoint (IMDS).

These factories are cached for the lifetime of the Function App
worker process so the credential and each BlobServiceClient are
created once and reused.
"""

from functools import lru_cache

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


@lru_cache(maxsize=1)
def get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


@lru_cache(maxsize=None)
def get_blob_service_client(storage_account_name: str) -> BlobServiceClient:
    account_url = (
        f"https://{storage_account_name}.blob.core.windows.net"
    )

    return BlobServiceClient(
        account_url=account_url,
        credential=get_credential(),
    )
