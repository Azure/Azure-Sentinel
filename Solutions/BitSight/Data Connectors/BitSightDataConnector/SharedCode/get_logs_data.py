"""Module to get_log table data from Log Analytics Workspace."""
import inspect

from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus

from .bitsight_exception import BitSightException
from .consts import (
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_TENANT_ID,
    COMPANIES_TABLE_NAME,
    LOGS_STARTS_WITH,
    WORKSPACE_ID,
)
from .logger import applogger


def parse_table_data(rows):
    """Parse Table Data and return Dictionary form."""
    data_to_return = []
    for row in rows:
        data = row._row_dict
        data_to_return.append(data)
    return data_to_return


def get_logs_data():
    """Get data from log analytics workspace.

    Args:
        time_generated (string): Time generated data

    Returns:
        list: List containing the table data.
    """
    __method_name = inspect.currentframe().f_code.co_name
    credential = ClientSecretCredential(
        client_id=AZURE_CLIENT_ID,
        client_secret=AZURE_CLIENT_SECRET,
        tenant_id=AZURE_TENANT_ID,
    )
    client = LogsQueryClient(credential)
    query = """{}_CL
    | sort by name_s asc
    | project name_s, guid_g""".format(
        COMPANIES_TABLE_NAME
    )
    try:
        response = client.query_workspace(
            workspace_id=WORKSPACE_ID, query=query, timespan=None
        )
        if response.status == LogsQueryStatus.SUCCESS:
            data = response.tables
        else:
            data = response.partial_data
            applogger.warning(response.partial_error)
        data_to_send = []
        for table in data:
            rows = table.rows
            data_to_send.extend(parse_table_data(rows=rows))
        applogger.debug("BitSight: get_logs_data: Data count: {}".format(len(data_to_send)))
        return data_to_send, True
    except Exception as error:
        if "Failed to resolve table or column expression" in str(error):
            applogger.error(
                "{}(method={}) : TableName provided is not Created or Data is not Ingested.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                )
            )
            return None, False
        applogger.error(
            "{}(method={}) : Error occurred :{}.".format(
                LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise BitSightException()
