"""Module to get_log table data from Log Analytics Workspace."""
import logging
import os
from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from Exceptions.ArmisExceptions import ArmisException

AZURE_CLIENT_ID = os.environ["Azure_Client_Id"]
AZURE_CLIENT_SECRET = os.environ["Azure_Client_Secret"]
AZURE_TENANT_ID = os.environ["Azure_Tenant_Id"]
ALERTS_TABLE_NAME = os.environ["ArmisAlertsTableName"]
WORKSPACE_ID = os.environ["WorkspaceID"]


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
        query (string): kql query

    Returns:
        list: List containing the table data.
    """
    credential = ClientSecretCredential(
        client_id=AZURE_CLIENT_ID,
        client_secret=AZURE_CLIENT_SECRET,
        tenant_id=AZURE_TENANT_ID,
    )
    client = LogsQueryClient(credential)
    try:
        response = client.query_workspace(workspace_id=WORKSPACE_ID, query=query, timespan=None)
        if response.status == LogsQueryStatus.SUCCESS:
            data = response.tables
        else:
            data = response.partial_data
            logging.warning(response.partial_error)
        data_to_send = []
        for table in data:
            rows = table.rows
            data_to_send.extend(parse_table_data(rows=rows))
        logging.info("Armis Activity Connector: found alerts data count: {}".format(len(data_to_send)))
        return data_to_send, True
    except Exception as error:
        if "Failed to resolve table or column expression" in str(error):
            logging.error("Armis Activity Connector: TableName provided is not Created or Data is not Ingested.")
            return None, False
        logging.error(error)
        raise ArmisException("Armis Activity Connector: Error occurred while getting data from log analytics.")
