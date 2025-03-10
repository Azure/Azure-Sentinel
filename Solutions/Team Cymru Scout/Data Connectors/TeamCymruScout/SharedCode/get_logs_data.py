"""This file contains methods to get_log table data from Log Analytics Workspace."""

import inspect

from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus

from .teamcymruscout_exception import TeamCymruScoutException
from . import consts
from .logger import applogger


def parse_table_data(rows):
    """Parse Table Data and return Dictionary form."""
    data_to_return = []
    for row in rows:
        data = row._row_dict
        data_to_return.append(data)
    return data_to_return


def get_logs_data(query):
    """Get data from log analytics workspace.

    Args:
        query (string): Time generated data

    Returns:
        list: List containing the table data.
    """
    __method_name = inspect.currentframe().f_code.co_name
    credential = ClientSecretCredential(
        client_id=consts.AZURE_CLIENT_ID,
        client_secret=consts.AZURE_CLIENT_SECRET,
        tenant_id=consts.AZURE_TENANT_ID,
    )
    client = LogsQueryClient(credential)
    try:
        response = client.query_workspace(workspace_id=consts.WORKSPACE_ID, query=query, timespan=None)
        if response.status == LogsQueryStatus.SUCCESS:
            data = response.tables
        else:
            data = response.partial_data
            applogger.warning(response.partial_error)
        data_to_send = []
        for table in data:
            rows = table.rows
            data_to_send.extend(parse_table_data(rows=rows))
        applogger.debug("{} get_logs_data: Data count: {}".format(consts.LOGS_STARTS_WITH, len(data_to_send)))
        return data_to_send, True
    except Exception as error:
        table_not_exist = "Failed to resolve table expression"
        column_not_exist = "Failed to resolve scalar expression"
        if table_not_exist or column_not_exist in str(error):
            applogger.warning(
                "{}(method={}) : TableName provided is not Created or Data is not Ingested.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                )
            )
            return None, False
        applogger.error(
            "{}(method={}) : Error occurred :{}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise TeamCymruScoutException()
