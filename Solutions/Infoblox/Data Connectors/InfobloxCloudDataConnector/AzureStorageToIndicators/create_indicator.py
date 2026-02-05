"""Create indicators ."""

import inspect
import time
from ..SharedCode import consts
from ..SharedCode.infoblox_exception import InfobloxException, InfobloxTimeoutException
from ..SharedCode.logger import applogger
from .indicator_mapping import Mapping
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import Utils


class CreateThreatIndicator(Utils):
    """Class to create indicators."""

    def __init__(self, start):
        """Initialize the CreateThreatIndicator object.

        Args:
            start(int): The starting time for the indicator creation process.
        """
        super().__init__(consts.INDICATOR_FUNCTION_NAME)
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
        self.mapping_obj = Mapping()
        self.start = start
        self.auth_sentinel()

    def parse_file_list(self):
        """Get list of file names and upload indicators to Sentinel.

        Raises:
            InfobloxException: Raised if any error occurs while fetching data from file and uploading indicators.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            file_list = self.filter_file_list(consts.FILE_NAME_PREFIX_COMPLETED)
            count_state_obj = StateManager(
                connection_string=consts.CONN_STRING,
                file_path="indicator_count",
                share_name=consts.FILE_SHARE_NAME_DATA,
            )
            for file_item in file_list:
                if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                    raise InfobloxTimeoutException()

                state_file_obj = StateManager(consts.CONN_STRING, file_item, consts.FILE_SHARE_NAME_DATA)
                request_body = self.get_checkpoint_data(state_file_obj, load_flag=True)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "No. of records in  storage file = {} File = {}".format(len(request_body), file_item),
                    )
                )
                checkpoint_file_count = self.get_checkpoint_data(count_state_obj)
                stored_indicator_count = 0 if not checkpoint_file_count else int(checkpoint_file_count)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Indicator Count from Checkpoint : {}".format(stored_indicator_count),
                    )
                )

                chunked_data = self.mapping_obj.create_chunks(request_body, stored_indicator_count)
                self.iterate_chunks_and_upload_indicators(
                    chunked_data,
                    file_item,
                    stored_indicator_count,
                    state_file_obj,
                    count_state_obj,
                )
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Indicators created for all available files",
                )
            )
        except InfobloxTimeoutException:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Infoblox: 9:30 mins executed hence breaking.",
                )
            )
            return
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

    def iterate_chunks_and_upload_indicators(
        self,
        chunked_data,
        file_item,
        stored_indicator_count,
        state_file_obj,
        count_state_obj,
    ):
        """Iterate through chunked data and uploads indicators to a storage location.

        Args:
            chunked_data: A list of data chunks to process.
            file_item: The file item to work on.
            stored_indicator_count: The count of stored indicators.
            state_file_obj: The state file object.
            count_state_obj: The count state object.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            index = 0
            filtered_indicators = 0
            for chunk in chunked_data:
                if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                    raise InfobloxTimeoutException()

                mapped_data = self.mapping_obj.map_threat_data(chunk)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "File name = {}, Uploading {} Indicators, index = {}".format(
                            file_item, len(mapped_data), index
                        ),
                    )
                )
                if len(mapped_data) != 0:
                    filtered_indicators += len(mapped_data)
                    self.upload_indicator(mapped_data)
                stored_indicator_count += len(chunk)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Indicator Count to post to Checkpoint file : {}".format(
                            stored_indicator_count,
                        ),
                    )
                )
                self.post_checkpoint_data(
                    count_state_obj,
                    str(stored_indicator_count),
                )
                index += 1

            self.post_checkpoint_data(count_state_obj, "")
            state_file_obj.delete()
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "File deleted = {}, Total indicators = {}, Filtered indicators = {}".format(
                        file_item, stored_indicator_count, filtered_indicators
                    ),
                )
            )
        except InfobloxTimeoutException:
            raise InfobloxTimeoutException()
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
