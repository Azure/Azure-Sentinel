import inspect
from . import consts
from .logger import applogger
from .dataminrpulse_exception import DataminrPulseException

def validate_params(azure_function_name):
    """To validate parameters of function app."""
    __method_name = inspect.currentframe().f_code.co_name
    required_params = {
        "AzureClientId": consts.AZURE_CLIENT_ID,
        "AzureClientSecret": consts.AZURE_CLIENT_SECRET,
        "AzureTenantId": consts.AZURE_TENANT_ID,
        "AzureResourceGroup": consts.AZURE_RESOURCE_GROUP,
        "AzureWorkspaceName": consts.AZURE_WORKSPACE_NAME,
        "AzureSubscriptionId": consts.AZURE_SUBSCRIPTION_ID,
        "ConnectionString": consts.CONN_STRING,
        "LogLevel": consts.LOG_LEVEL,
        "WorkspaceID": consts.WORKSPACE_ID,
        "WorkspaceKey": consts.WORKSPACE_KEY,
        "Alerts_Table_Name": consts.ALERTS_TABLE_NAME,
    }
    applogger.debug(
        "{}(method={}) : {} : Checking if all the environment variables exist or not.".format(
            consts.LOGS_STARTS_WITH, __method_name, azure_function_name
        )
    )
    missing_required_field = False
    for label, params in required_params.items():
        if not params or params == "":
            missing_required_field = True
            applogger.error(
                '{}(method={}) : {} : "{}" field is not set in the environment please set '
                "the environment variable and run the app.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    azure_function_name,
                    label,
                )
            )
    if missing_required_field:
        raise DataminrPulseException(
            "Error Occurred while validating params. Required fields missing."
        )
    applogger.info(
        "{}(method={}) : {} : All necessary variables are present in the Configuration.".format(
            consts.LOGS_STARTS_WITH, __method_name, azure_function_name
        )
    )
