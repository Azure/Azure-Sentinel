"""Module with Armis class for interacting with Vectra XDR APIs and posting data to Sentinel."""

from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from .consts import (
    DCR_RULE_ID,
    AZURE_DATA_COLLECTION_ENDPOINT,
    SCOPE,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_TENANT_ID,
    LOG_FORMAT,
)
import logging
from Exceptions import ArmisExceptions
import inspect


def send_data_to_sentinel(data, data_table):
    """
    Post data to Azure Sentinel via the ingestion API.

    Args:
        data (dict or list): Data to be ingested into Sentinel.
        data_table (str): Log type/table name for ingestion.

    Raises:
        ArmisException: For any error during data upload to Sentinel.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        # Determine appropriate Azure credentials
        if ".us" in SCOPE:
            creds = ClientSecretCredential(
                client_id=AZURE_CLIENT_ID,
                client_secret=AZURE_CLIENT_SECRET,
                tenant_id=AZURE_TENANT_ID,
                authority=AzureAuthorityHosts.AZURE_GOVERNMENT,
            )
        else:
            creds = ClientSecretCredential(
                client_id=AZURE_CLIENT_ID,
                client_secret=AZURE_CLIENT_SECRET,
                tenant_id=AZURE_TENANT_ID,
            )
        logging.info(
            LOG_FORMAT.format(__method_name, "Ingesting Data Logs to Sentinel...")
        )
        azure_client = LogsIngestionClient(
            AZURE_DATA_COLLECTION_ENDPOINT, credential=creds, credential_scopes=[SCOPE]
        )
        # Ensure data is a list for ingestion
        if not isinstance(data, list):
            data = [data] if isinstance(data, dict) else list(data)
        dcr_stream = f"Custom-{data_table}"
        azure_client.upload(rule_id=DCR_RULE_ID, stream_name=dcr_stream, logs=data)
    except ClientAuthenticationError as error:
        logging.error(
            LOG_FORMAT.format(
                __method_name, "Authentication error while uploading data to Sentinel."
            )
        )
        raise ArmisExceptions(
            f"Authentication error while uploading data to Sentinel: {error}"
        )
    except HttpResponseError as error:
        logging.error(
            LOG_FORMAT.format(
                __method_name, "HTTP response error while uploading data to Sentinel."
            )
        )
        raise ArmisExceptions(
            f"HTTP response error while uploading data to Sentinel: {error}"
        )
    except Exception as error:
        logging.error(
            LOG_FORMAT.format(
                __method_name, "Unexpected error while uploading data to Sentinel."
            )
        )
        raise ArmisExceptions(
            f"Unexpected error while uploading data to Sentinel: {error}"
        )
