"""Get infoblox data and store it in azure storage with max of 20 MB file."""

import inspect
import datetime
import requests
import json
from azure.storage.fileshare import ShareDirectoryClient
from ..SharedCode import consts
from ..SharedCode.infoblox_exception import InfobloxException
from ..SharedCode.logger import applogger
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import Utils
from ..SharedCode.sentinel import post_data


class InfobloxToAzureStorage(Utils):
    """Class for storing the data from infoblox to azure storage."""

    def __init__(self, start_time) -> None:
        """Initialize InfobloxToAzureStorage object."""
        super().__init__(consts.CURRENT_I_TO_S_FUNCTION_NAME)
        self.start_time = start_time
        self.ioc_type = consts.TYPE
        self.check_environment_var_exist(
            [
                {"Api_Token": consts.API_TOKEN},
                {"File_Share_Name": consts.FILE_SHARE_NAME},
                {"File_Name": consts.FILE_NAME},
                {"Base_Url": consts.BASE_URL},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY}
            ]
        )
        self.authenticate_infoblox_api()
        self.parent_file = ShareDirectoryClient.from_connection_string(
            conn_str=consts.CONN_STRING,
            share_name=consts.FILE_SHARE_NAME_DATA,
            directory_path="",
        )

    def get_infoblox_data_into_azure_storage(self) -> None:
        """Get infoblox data and send the data to azure storage, initialization method."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            checkpoint_file_name = consts.FILE_NAME + "-" + self.ioc_type
            date_state_manager_obj = StateManager(consts.CONN_STRING, checkpoint_file_name, consts.FILE_SHARE_NAME)
            self.initiate_and_iterate_through_response_obj(date_state_manager_obj)

        except InfobloxException:
            raise InfobloxException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()

    def initiate_and_iterate_through_response_obj(self, date_state_manager_obj):
        """Initiate and iterate through the response object.

        Fetches checkpoint data, processes dates, and query parameters.
        Handles response object iteration and posts data to Azure storage.

        Args:
            date_state_manager_obj: State management object.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Fetching checkpoint data",
                )
            )
            checkpoint_data = self.get_checkpoint_data(date_state_manager_obj, load_flag=True)
            from_date = None
            if checkpoint_data:
                from_date = checkpoint_data.get("to_date", None)

            if not from_date:
                # !This means function app is running first time
                to_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                from_date = self.add_xh_to_iso_time_string(to_date, -abs(consts.CURRENT_TIME_INTERVAL))
                data_to_post = {"to_date": from_date}
                self.post_checkpoint_data(date_state_manager_obj, data_to_post, dump_flag=True)
            else:
                to_date = self.add_xh_to_iso_time_string(from_date, consts.CURRENT_TIME_INTERVAL)

            base_checkpoint_file_name_for_from_and_to_dates = self.create_checkpoint_file_name_using_dates(
                from_date, to_date, self.ioc_type
            )

            self.checkpoint_for_from_and_to_dates = StateManager(
                consts.CONN_STRING,
                base_checkpoint_file_name_for_from_and_to_dates,
                consts.FILE_SHARE_NAME_DATA,
            )
            status_of_last_from_date = self.get_checkpoint_data(self.checkpoint_for_from_and_to_dates)

            if status_of_last_from_date:
                status_of_last_from_date = int(status_of_last_from_date)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Retry count from last iteration = {}".format(status_of_last_from_date),
                    )
                )
                list_of_file_with_prefix = self.list_file_names_in_file_share(
                    self.parent_file,
                    base_checkpoint_file_name_for_from_and_to_dates,
                )
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "No. of file = {} with prefix = {}".format(
                            len(list_of_file_with_prefix),
                            base_checkpoint_file_name_for_from_and_to_dates,
                        ),
                    )
                )
                # ! delete all checkpoints file starting with prefix base_checkpoint_file_name_for_from_and_to_dates
                if list_of_file_with_prefix:
                    self.delete_files_from_azure_storage(list_of_file_with_prefix, self.parent_file)
                if status_of_last_from_date > 2:
                    self.store_failed_range(from_date, to_date)

                    data_to_post = {"to_date": to_date}
                    self.post_checkpoint_data(date_state_manager_obj, data_to_post, dump_flag=True)

                    from_date = to_date
                    to_date = self.add_xh_to_iso_time_string(from_date, consts.CURRENT_TIME_INTERVAL)
                    base_checkpoint_file_name_for_from_and_to_dates = self.create_checkpoint_file_name_using_dates(
                        from_date, to_date, self.ioc_type
                    )
                    self.checkpoint_for_from_and_to_dates = StateManager(
                        consts.CONN_STRING,
                        base_checkpoint_file_name_for_from_and_to_dates,
                        consts.FILE_SHARE_NAME_DATA,
                    )
                    status_of_last_from_date = 1
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "This to_date occur for the first time. Storing retry count = 1",
                        )
                    )
                    self.post_checkpoint_data(
                        self.checkpoint_for_from_and_to_dates,
                        str(status_of_last_from_date),
                    )
                else:
                    status_of_last_from_date += 1
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Storing retry count = {}".format(status_of_last_from_date),
                        )
                    )
                    self.post_checkpoint_data(
                        self.checkpoint_for_from_and_to_dates,
                        str(status_of_last_from_date),
                    )
            else:
                status_of_last_from_date = 1
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "This to_date occur for the first time. Storing retry count = 1",
                    )
                )
                self.post_checkpoint_data(self.checkpoint_for_from_and_to_dates, str(status_of_last_from_date))

            query_params = {"from_date": from_date, "to_date": to_date}

            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Query params = {}".format(query_params),
                )
            )

            response_obj = self.initiate_response_obj(query_params, self.ioc_type)

            base_checkpoint_file_name_for_from_and_to_dates += "_" + self.start_time

            self.iterate_through_response_obj(response_obj, base_checkpoint_file_name_for_from_and_to_dates)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "IOCs posted to azure storage from_date = {}, to_date = {}".format(from_date, to_date),
                )
            )
            data_to_post = {"to_date": to_date}
            self.post_checkpoint_data(date_state_manager_obj, data_to_post, dump_flag=True)

            self.checkpoint_for_from_and_to_dates.delete()
        except InfobloxException:
            raise InfobloxException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()

    def initiate_response_obj(self, query_params, ioc_type):
        """Initiate the response object.

        Create URL based on the endpoint and IOC type,
        then sends a request to get the Infoblox stream response object using the given query parameters.

        Args:
            query_params: A dictionary containing query parameters.
            ioc_type: The type of IOC (Indicator of Compromise).

        Returns:
            The response object obtained from Infoblox.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            endpoint = consts.ENDPOINTS["active_threats_by_type"]
            url = self.url_builder(endpoint, ioc_type)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Url = {}".format(url),
                )
            )
            response_obj = self.get_infoblox_stream_response_obj(url, query_parameters=query_params)

            return response_obj
        except InfobloxException:
            raise InfobloxException()
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Key error : Error-{}".format(key_error),
                )
            )
            raise InfobloxException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()

    def create_checkpoint_file_name_using_dates(self, from_date, to_date, ioc_type):
        """Create a checkpoint file name using the specified from_date, to_date, and IOC type.

        Args:
            from_date: The starting date for the checkpoint.
            to_date: The ending date for the checkpoint.
            ioc_type: The type of IOC (Indicator of Compromise).

        Returns:
            The generated checkpoint file name.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            from_epoch = self.iso_to_epoch_str(from_date)
            to_epoch = self.iso_to_epoch_str(to_date)

            checkpoint_file_name = "infoblox_raw_{}_{}_{}".format(ioc_type, from_epoch, to_epoch)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Checkpoint file name = {}".format(checkpoint_file_name),
                )
            )
            return checkpoint_file_name
        except InfobloxException:
            raise InfobloxException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()

    def iterate_through_response_obj(self, response_obj, base_checkpoint_file_name_for_from_and_to_dates):
        """Iterate through the response object, processes the data in chunks, and sends it to Azure storage.

        Args:
            response_obj: The response object to iterate through.
            base_checkpoint_file_name_for_from_and_to_dates: The base name for the checkpoint data file.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            response_data = None
            max_file_size = consts.MAX_FILE_SIZE
            max_chunk_size = consts.MAX_CHUNK_SIZE
            index = 1
            for chunk in response_obj.iter_content(max_chunk_size):
                if chunk is None:
                    break
                chunk_len = len(chunk)
                if response_data is None:
                    response_data = chunk
                elif (len(response_data) + chunk_len) > max_file_size:
                    applogger.debug(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Index = {}, Len = {}, Max File Size = {}".format(index, len(response_data), max_file_size),
                        )
                    )
                    self.send_to_azure_storage(
                        response_data,
                        base_checkpoint_file_name_for_from_and_to_dates,
                        index,
                    )
                    index += 1
                    response_data = chunk
                else:
                    response_data += chunk
            if response_data:
                self.send_to_azure_storage(
                    response_data,
                    base_checkpoint_file_name_for_from_and_to_dates,
                    index,
                )
        except InfobloxException:
            raise InfobloxException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()

    def send_to_azure_storage(self, response_data, base_checkpoint_file_name_for_from_and_to_dates, index):
        """Send response data to Azure storage.

        Args:
            response_data: The data to be sent to Azure storage.
            base_checkpoint_file_name_for_from_and_to_dates: The base file name for the checkpoint data.
            index: The index of the data being sent.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Index = {}, Checkpoint File Name = {}, Sending data...".format(
                        index,
                        base_checkpoint_file_name_for_from_and_to_dates + "_" + str(index),
                    ),
                )
            )
            checkpoint_obj = StateManager(
                consts.CONN_STRING,
                base_checkpoint_file_name_for_from_and_to_dates + "_" + str(index),
                consts.FILE_SHARE_NAME_DATA,
            )
            self.post_checkpoint_data(checkpoint_obj, response_data)
        except InfobloxException:
            raise InfobloxException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()

    def get_infoblox_stream_response_obj(self, url, query_parameters=None):
        """Return the response object obtained from Infoblox.

        Args:
            url: The URL to send the request to
            query_parameters: Optional query parameters (default is None)

        Returns:
            The response object from the URL request
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            max_retries = consts.MAX_RETRIES
            for _ in range(max_retries):
                response = requests.get(url=url, headers=self.headers, params=query_parameters, stream=True)
                if response.status_code == 200:
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Got response object, Status Code = {}".format(response.status_code),
                        )
                    )
                    return response
                elif response.status_code == 500:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Internal Server Error, Retrying..., Status Code = {}".format(response.status_code),
                        )
                    )
                    continue
                elif response.status_code == 429:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Rate Limit Exceeded, Retrying..., Status Code = {}".format(response.status_code),
                        )
                    )
                    continue
                elif response.status_code == 401:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Unauthorized, Provide valid API TOKEN, Status Code = {}".format(response.status_code),
                        )
                    )
                    raise InfobloxException()
                elif response.status_code == 403:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Forbidden, user does not have access to this API, Status Code = {}".format(
                                response.status_code
                            ),
                        )
                    )
                    raise InfobloxException()
                else:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Unexpected error, Status Code = {}, Error-{}".format(
                                response.status_code, response.content
                            ),
                        )
                    )
                    raise InfobloxException()
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Max retries reached",
                )
            )
            raise InfobloxException()
        except requests.ConnectionError as conn_err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Connection error : Error-{}".format(conn_err),
                )
            )
            raise InfobloxException()
        except requests.HTTPError as http_err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "HTTP error : Error-{}".format(http_err),
                )
            )
            raise InfobloxException()
        except requests.Timeout as timeout_err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Timeout error : Error-{}".format(timeout_err),
                )
            )
            raise InfobloxException()
        except requests.RequestException as request_err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Request error : Error-{}".format(request_err),
                )
            )
            raise InfobloxException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()

    def url_builder(self, endpoint, path_variable=None):
        """Build a URL based on the provided endpoint and optional path variable.

        Args:
            endpoint: The base endpoint to build the URL.
            path_variable: Optional path variable to append to the endpoint.

        Returns:
            The constructed URL.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if path_variable:
                url = consts.BASE_URL.format(endpoint.format(path_variable))
            else:
                url = consts.BASE_URL.format(endpoint)
                url += "?fields={}".format(consts.FIELDS)
                if consts.CONFIDENCE_THRESHOLD:
                    url += "&confidence={}".format(consts.CONFIDENCE_THRESHOLD)
            return url
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()

    def store_failed_range(self, from_date, to_date):
        """Store range of date which are failed to fetch in table.

        Args:
            from_date (str): from date of range
            to_date (str): to date of range
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            range_to_append = [
                {
                    "From Date": from_date,
                    "To Date": to_date,
                    "Threat Type": self.ioc_type,
                }
            ]
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Ingesting failed range = {}".format(range_to_append),
                )
            )
            post_data(json.dumps(range_to_append), "Failed_Range_To_Ingest")
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise InfobloxException()
