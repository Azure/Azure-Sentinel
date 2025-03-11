"""Handle retry failed indicators."""

import time
from ..SharedCode.utils import Utils
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.infoblox_exception import InfobloxException
from ..SharedCode.state_manager import StateManager
import inspect


class InfobloxRetryFailedIndicators(Utils):
    """Class for retrying failed indicators."""

    def __init__(self, start):
        """Initialize the CreateThreatIndicator object.

        Args:
            start(int): The starting time for the retrying failed indicator process.
        """
        super().__init__(consts.FAILED_INDICATOR_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
                {"AzureTenantId": consts.AZURE_TENANT_ID},
                {"AzureClientId": consts.AZURE_CLIENT_ID},
                {"AzureClientSecret": consts.AZURE_CLIENT_SECRET},
                {"AzureAuthURL": consts.AZURE_AUTHENTICATION_URL},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"ConnectionString": consts.CONN_STRING},
                {"FILE_SHARE_NAME_DATA": consts.FILE_SHARE_NAME_DATA},
            ]
        )
        self.start = start
        self.auth_sentinel()

    def get_failed_indicators_and_retry(self):
        """Get failed indicators data from checkpoint and try creating them again."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Starting Retrial for Failed Indicators",
                )
            )
            failed_file_list = self.filter_file_list(consts.FAILED_INDICATOR_FILE_PREFIX)
            if len(failed_file_list) != 0:
                for file_item in failed_file_list:
                    if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                        applogger.info(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.azure_function_name,
                                "Infoblox: 9:00 mins executed hence breaking.",
                            )
                        )
                        break
                    state_file_obj = StateManager(consts.CONN_STRING, file_item, consts.FILE_SHARE_NAME_DATA)
                    request_body = self.get_checkpoint_data(state_file_obj, load_flag=True)
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "No. of records in  storage file = {}".format(len(request_body)),
                        )
                    )
                    self.upload_indicator(request_body)
                    state_file_obj.delete()
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "File name : {} deleted".format(file_item),
                        )
                    )
                return
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "No Failed Indicators found",
                )
            )

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
