"""This file contains methods for creating microsoft custom log table."""

import inspect
from azure.identity import AzureAuthorityHosts, ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.monitor.ingestion.aio import LogsIngestionClient as AsyncLogsIngestionClient
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from SharedCode.logger import applogger
from SharedCode import consts
from SharedCode.mimecast_exception import MimecastException


def send_data_to_sentinel(data, data_table):
    """
    Post data to Azure Sentinel via the ingestion API.

    Args:
        data (dict or list): Data to be ingested into Sentinel.
        data_table (str): Log type/table name for ingestion.

    Raises:
        MimecastException: For any error during data upload to Sentinel.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        # Determine appropriate Azure credentials
        if ".us" in consts.SCOPE:
            creds = ClientSecretCredential(
                client_id=consts.AZURE_CLIENT_ID,
                client_secret=consts.AZURE_CLIENT_SECRET,
                tenant_id=consts.AZURE_TENANT_ID,
                authority=AzureAuthorityHosts.AZURE_GOVERNMENT,
            )
        else:
            creds = ClientSecretCredential(
                client_id=consts.AZURE_CLIENT_ID,
                client_secret=consts.AZURE_CLIENT_SECRET,
                tenant_id=consts.AZURE_TENANT_ID,
            )

        azure_client = LogsIngestionClient(
            consts.AZURE_DATA_COLLECTION_ENDPOINT,
            credential=creds,
            credential_scopes=[consts.SCOPE],
        )

        # Ensure data is a list for ingestion
        if not isinstance(data, list):
            data = [data] if isinstance(data, dict) else list(data)

        dcr_stream = f"Custom-{data_table}"
        azure_client.upload(
            rule_id=consts.DCR_RULE_ID, stream_name=dcr_stream, logs=data
        )

    except ClientAuthenticationError as error:
        applogger.error(
            "{}(method={}) : Authentication error while uploading data to Sentinel. Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise MimecastException(
            f"Authentication error while uploading data to Sentinel: {error}"
        )
    except HttpResponseError as error:
        applogger.error(
            "{}(method={}) : HTTP response error while uploading data to Sentinel. Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise MimecastException(
            f"HTTP response error while uploading data to Sentinel: {error}"
        )
    except Exception as error:
        applogger.error(
            "{}(method={}) : Unexpected error while uploading data to Sentinel. Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise MimecastException(
            f"Unexpected error while uploading data to Sentinel: {error}"
        )


async def async_send_data_to_sentinel(data, data_table):
    """
    Post data to Azure Sentinel via the ingestion API.

    Args:
        data (dict or list): Data to be ingested into Sentinel.
        data_table (str): Log type/table name for ingestion.

    Raises:
        MimecastException: For any error during data upload to Sentinel.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        # Determine appropriate Azure credentials
        if ".us" in consts.SCOPE:
            creds = AsyncClientSecretCredential(
                client_id=consts.AZURE_CLIENT_ID,
                client_secret=consts.AZURE_CLIENT_SECRET,
                tenant_id=consts.AZURE_TENANT_ID,
                authority=AzureAuthorityHosts.AZURE_GOVERNMENT,
            )
        else:
            creds = AsyncClientSecretCredential(
                client_id=consts.AZURE_CLIENT_ID,
                client_secret=consts.AZURE_CLIENT_SECRET,
                tenant_id=consts.AZURE_TENANT_ID,
            )

        azure_client = AsyncLogsIngestionClient(
            consts.AZURE_DATA_COLLECTION_ENDPOINT,
            credential=creds,
            credential_scopes=[consts.SCOPE],
        )
        # Ensure data is a list for ingestion
        if not isinstance(data, list):
            data = [data] if isinstance(data, dict) else list(data)

        dcr_stream = f"Custom-{data_table}"
        await azure_client.upload(
            rule_id=consts.DCR_RULE_ID, stream_name=dcr_stream, logs=data
        )

    except ClientAuthenticationError as error:
        applogger.error(
            "{}(method={}) : Authentication error while uploading data to Sentinel. Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise MimecastException(
            f"Authentication error while uploading data to Sentinel: {error}"
        )
    except HttpResponseError as error:
        applogger.error(
            "{}(method={}) : HTTP response error while uploading data to Sentinel. Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise MimecastException(
            f"HTTP response error while uploading data to Sentinel: {error}"
        )
    except Exception as error:
        applogger.error(
            "{}(method={}) : Unexpected error while uploading data to Sentinel. Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise MimecastException(
            f"Unexpected error while uploading data to Sentinel: {error}"
        )
    finally:
        await azure_client.close()
        await creds.close()