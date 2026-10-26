"""This file contains methods for creating Microsoft Sentinel custom log table entries."""

import inspect
from azure.identity import AzureAuthorityHosts, ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from SharedCode.logger import applogger
from SharedCode import consts
from SharedCode.exceptions import GTIRelevanceSystemAlertsException


def send_data_to_sentinel(data, data_table):
    """Post data to Azure Sentinel via the Log Ingestion API.

    Args:
        data (dict or list): Data to be ingested into Sentinel.
        data_table (str): Log type/table name for ingestion (without _CL suffix).

    Raises:
        GTIRelevanceSystemAlertsException: For any error during data upload to Sentinel.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        # Determine appropriate Azure credentials based on cloud environment
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

        dcr_stream = "Custom-{}".format(data_table)
        azure_client.upload(
            rule_id=consts.DCR_RULE_ID,
            stream_name=dcr_stream,
            logs=data,
        )
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                "SentinelConnector",
                "Successfully uploaded {} records to stream {}".format(len(data), dcr_stream),
            )
        )

    except ClientAuthenticationError as error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                "SentinelConnector",
                "Authentication error while uploading data to Sentinel. Error: {}".format(error),
            )
        )
        raise GTIRelevanceSystemAlertsException(
            "Authentication error while uploading data to Sentinel: {}".format(error)
        )
    except HttpResponseError as error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                "SentinelConnector",
                "HTTP response error while uploading data to Sentinel. Error: {}".format(error),
            )
        )
        raise GTIRelevanceSystemAlertsException(
            "HTTP response error while uploading data to Sentinel: {}".format(error)
        )
    except GTIRelevanceSystemAlertsException:
        raise
    except Exception as error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                "SentinelConnector",
                "Unexpected error while uploading data to Sentinel. Error: {}".format(error),
            )
        )
        raise GTIRelevanceSystemAlertsException(
            "Unexpected error while uploading data to Sentinel: {}".format(error)
        )
