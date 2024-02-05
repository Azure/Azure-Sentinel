"""Module to get_log table data from Log Analytics Workspace."""
import datetime
import inspect
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import ClientSecretCredential
from ..shared_code import consts
from ..shared_code.logger import applogger
from ..shared_code.dataminrpulse_exception import DataminrPulseException


def parse_table_data(rows):
    """Parse Table Data and return Dictionary form."""
    data_to_return = []
    for row in rows:
        data = row._row_dict
        data['TimeGenerated'] = data['TimeGenerated'].isoformat()
        data_to_return.append(data)
    return data_to_return


def get_logs_data(time_generated):
    """Get data from log analytics workspace.

    Args:
        time_generated (string): Time generated data

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
    query = """{}_CL
    | extend Source=extract("via (.+)",1,headline_s)
    | extend Source=substring(Source,0,strlen(Source)-1)
    | where Source  in~ ('Greynoise', 'Shodan', 'VirusTotal', 'alienvault open threat exchange', 'URLScan', 'CSIRT')
    | sort by  TimeGenerated asc
    | project TimeGenerated, index_s, _embedded_labels_s, alertType_id_s, headline_s, Source""".format(consts.ALERTS_TABLE_NAME)
    if time_generated is None or time_generated == "":
        start_time = datetime.datetime.now(tz=datetime.timezone.utc)
    else:
        start_time = datetime.datetime.fromisoformat(time_generated)
    end_time = datetime.datetime.now(tz=datetime.timezone.utc)
    try:
        response = client.query_workspace(
            workspace_id=consts.WORKSPACE_ID,
            query=query,
            timespan=(start_time, end_time),
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
        return data_to_send
    except Exception as error:
        if "Failed to resolve table or column expression" in str(error):
            applogger.error(
                "{}(method={}) : {} : TableName provided is not Created or Data is not Ingested.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                )
            )
            raise DataminrPulseException()
        applogger.error(
            "{}(method={}) : {} : Error occurred :{}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                error,
            )
        )
        raise DataminrPulseException()
