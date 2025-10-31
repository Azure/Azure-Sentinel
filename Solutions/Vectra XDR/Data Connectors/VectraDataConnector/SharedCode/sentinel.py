"""Module with Vectra XDR class for interacting with Vectra XDR APIs and posting data to Sentinel."""
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from .consts import (
    DCR_RULE_ID,
    AZURE_DATA_COLLECTION_ENDPOINT,
    SCOPE,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_TENANT_ID
)
from .logger import applogger
from .vectra_exception import VectraException


def send_data_to_sentinel(data, data_table):
    """
    Post data to Azure Sentinel via the ingestion API.

    Args:
        data (dict or list): Data to be ingested into Sentinel.
        data_table (str): Log type/table name for ingestion.

    Raises:
        VectraException: For any error during data upload to Sentinel.
    """
    try:
        # Determine appropriate Azure credentials
        if ".us" in SCOPE:
            creds = ClientSecretCredential(
                client_id=AZURE_CLIENT_ID,
                client_secret=AZURE_CLIENT_SECRET,
                tenant_id=AZURE_TENANT_ID,
                authority=AzureAuthorityHosts.AZURE_GOVERNMENT
            )
        else:
            creds = ClientSecretCredential(
                client_id=AZURE_CLIENT_ID,
                client_secret=AZURE_CLIENT_SECRET,
                tenant_id=AZURE_TENANT_ID
            )
        applogger.info("Vectra XDR: Ingesting Data Logs to Sentinel...1")
        azure_client = LogsIngestionClient(
            AZURE_DATA_COLLECTION_ENDPOINT,
            credential=creds,
            credential_scopes=[SCOPE]
        )
        applogger.info("Vectra XDR: Ingesting Data Logs to Sentinel...2")
        # Ensure data is a list for ingestion
        if not isinstance(data, list):
            data = [data] if isinstance(data, dict) else list(data)
        applogger.info("Vectra XDR: Ingesting Data Logs to Sentinel...3")
        dcr_stream = f"Custom-{data_table}"
        azure_client.upload(rule_id=DCR_RULE_ID, stream_name=dcr_stream, logs=data)
        applogger.info("Vectra XDR: Ingesting Data Logs to Sentinel...4")
    except ClientAuthenticationError as error:
        applogger.error(
                "Vectra XDR: Authentication error while uploading data to Sentinel. "
                f"Error: {error}"
            )
        raise VectraException(
            f"Authentication error while uploading data to Sentinel: {error}"
        )
    except HttpResponseError as error:
        applogger.error(
            "Vectra XDR: HTTP response error while uploading data to Sentinel. "
            f"Error: {error}"
        )
        raise VectraException(
            f"HTTP response error while uploading data to Sentinel: {error}"
        )
    except Exception as error:
        applogger.error(
            "Vectra XDR: Unexpected error while uploading data to Sentinel. "
            f"Error: {error}"
        )
        raise VectraException(
            f"Unexpected error while uploading data to Sentinel: {error}"
        )