"""Module with DataminrPulse class for interacting with DataminrPulse APIs and posting data to Sentinel."""
from azure.identity import AzureAuthorityHosts, ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from shared_code.consts import (DCR_RULE_ID, AZURE_DATA_COLLECTION_ENDPOINT,
                                SCOPE, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
from shared_code.logger import applogger
from shared_code.dataminrpulse_exception import DataminrPulseException


def send_data_to_sentinel(data, data_table):
    """
    Post data to Azure Sentinel via the ingestion API.

    Args:
        data (dict or list): Data to be ingested into Sentinel.
        data_table (str): Log type/table name for ingestion.

    Raises:
        DataminrPulseException: For any error during data upload to Sentinel.
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

        azure_client = LogsIngestionClient(
            AZURE_DATA_COLLECTION_ENDPOINT,
            credential=creds,
            credential_scopes=[SCOPE]
        )

        # Ensure data is a list for ingestion
        if not isinstance(data, list):
            data = [data] if isinstance(data, dict) else list(data)

        dcr_stream = f"Custom-{data_table}"
        for index, row in enumerate(data):
            if "_embedded" in row:
                row["embedded"] = row.pop("_embedded")
            if "type" in row:
                row["type_"] = row.pop("type")
            if "flag" in row:
                row["flag_"] = row.pop("flag")
            data[index] = row
        azure_client.upload(rule_id=DCR_RULE_ID, stream_name=dcr_stream, logs=data)

    except ClientAuthenticationError as error:
        applogger.error(
                "DataminrPulse: Authentication error while uploading data to Sentinel. "
                f"Error: {error}"
            )
        raise DataminrPulseException(
            f"Authentication error while uploading data to Sentinel: {error}"
        )
    except HttpResponseError as error:
        applogger.error(
            "DataminrPulse: HTTP response error while uploading data to Sentinel. "
            f"Error: {error}"
        )
        raise DataminrPulseException(
            f"HTTP response error while uploading data to Sentinel: {error}"
        )
    except Exception as error:
        applogger.error(
            "DataminrPulse: Unexpected error while uploading data to Sentinel. "
            f"Error: {error}"
        )
        raise DataminrPulseException(
            f"Unexpected error while uploading data to Sentinel: {error}"
        )
