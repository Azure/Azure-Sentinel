"""Get required source list from log analytics workspace."""

import inspect
import datetime
from ..SharedCode.infoblox_exception import InfobloxException
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.utils import Utils
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import ClientSecretCredential


class DossierListSources(Utils):
    """Class for Dossier List Sources."""

    def __init__(self, type_of_data, target):
        """Init for Dossier List Sources."""
        super().__init__(consts.DOSSIER_REQUIRED_SOURCE_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
                {"AzureTenantId": consts.AZURE_TENANT_ID},
                {"AzureClientId": consts.AZURE_CLIENT_ID},
                {"AzureClientSecret": consts.AZURE_CLIENT_SECRET},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"API_Token": consts.API_TOKEN},
            ]
        )
        self.type_of_data = type_of_data
        self.target = target

    def get_logs_data(self, ioc_type, ioc_val):
        """Get data from log analytics workspace.

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
        query = """let dummyschema = datatable"""
        query += """(TimeGenerated:datetime, params_type_s:string, params_target_s:string, Count:int)[];"""
        for val in consts.SOURCES.get(ioc_type):
            query += f"""let {val}_count =
                union isfuzzy=true
                dummyschema,
                dossier_{val}_CL
                | where TimeGenerated >= ago(24h)
                | where params_type_s =="{ioc_type}" and params_target_s =="{ioc_val}"
                | count
                | project {val}_count = Count
                ;\n"""
        query += "union "
        for val in consts.SOURCES.get(ioc_type):
            query += f"""{val}_count, """
        query = query[:-2]

        start_time = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=1)
        end_time = datetime.datetime.now(tz=datetime.timezone.utc)
        applogger.debug(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                self.azure_function_name,
                "Query to check data in sentinel table = {}".format(query),
            )
        )
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
            column_names = []
            row_values = []

            column_names = data[0].columns
            row_values = data[0].rows

            result = []
            for row in row_values:
                row_dict = {}
                for i, value in enumerate(row):
                    if value is not None:
                        column_name = column_names[i]
                        row_dict[column_name.removesuffix("_count")] = value
                result.append(row_dict)
            combined_dict = {}
            for d in result:
                combined_dict.update(d)

            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Sources with available data = {}".format(combined_dict),
                )
            )
            return combined_dict
        except IndexError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Index error : Error-{}".format(error),
                )
            )
            raise InfobloxException()
        except Exception as error:
            if "Failed to resolve table or column expression" in str(error):
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "TableName provided is not Created or Data is not Ingested.",
                    )
                )
                raise InfobloxException()
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Unexpected error : Error-{}".format(error),
                )
            )
            raise InfobloxException()

    def required_lookup_sources(self):
        """Fetch required lookup source for dossier lookup.

        Returns:
            list: A list of keys from the response table where the corresponding value is 0.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            response_from_table = self.get_logs_data(self.type_of_data, self.target)
            required_lookup_sources = [key for key, val in response_from_table.items() if val == 0]
            required_lookup_sources.sort(reverse=True)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Sources for lookup = {}, type = {}, target = {}".format(
                        required_lookup_sources, self.type_of_data, self.target
                    ),
                )
            )
            return required_lookup_sources
        except InfobloxException:
            raise InfobloxException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Unexpected error : Error-{}".format(error),
                )
            )
            raise InfobloxException()
