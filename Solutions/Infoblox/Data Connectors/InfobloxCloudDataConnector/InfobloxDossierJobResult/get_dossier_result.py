"""Get Dossier Result using job id provided from another activity function."""

import inspect
import json
import sys
from math import ceil
from ..SharedCode.infoblox_exception import InfobloxException
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.utils import Utils
from ..SharedCode.sentinel import post_data


class DossierGetResult(Utils):
    """Class for get dossier result."""

    def __init__(self):
        """Init method for get dossier result."""
        super().__init__(consts.DOSSIER_GET_RESULT_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"API_Token": consts.API_TOKEN},
            ]
        )
        self.authenticate_infoblox_api()

    def get_size_of_json(self, json_response):
        """Calculate the size of a JSON object after converting it to a string.

        Args:
            json_response: The JSON object to calculate the size for.

        Returns:
            int: The size of the JSON object after conversion to a string.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            return sys.getsizeof(json.dumps(json_response))
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise InfobloxException()

    def separate_data_into_chunks(self, raw_data, size_of_data):
        """Return data by separating it into 20 mb chunks.

        Args:
            raw_data (list): list of json objects.

        Yields:
            list: separated chunks in list.
        """
        original_index = consts.SIZE_OF_CHUNK_TO_INGEST
        count_of_data_for_original_index = int((len(raw_data) * original_index) / size_of_data)
        number_of_iterations = ceil(len(raw_data) / count_of_data_for_original_index)
        start_count = 0
        for _ in range(number_of_iterations):
            end_index = start_count + count_of_data_for_original_index
            if end_index > len(raw_data):
                yield raw_data[start_count:]
                break
            yield raw_data[start_count:end_index]
            start_count = end_index

    def send_to_sentinel(self, suffix, data, source):
        """Send data to Sentinel after processing it in chunks.

        Args:
            suffix (str): A suffix to be used in the data processing.
            data (dict): The data to be processed and sent to Sentinel.
            source (str): The source of the data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            size_of_list = self.get_size_of_json(data)
            for chunk in self.separate_data_into_chunks(data, size_of_list):
                post_data(
                    json.dumps(chunk, ensure_ascii=False),
                    "{}_{}_{}".format(consts.DOSSIER, source, suffix),
                )
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise InfobloxException()

    def store_data_in_separate_table(self, key, data, source):
        """Store data in a separate table based on the key, data, and source.

        Args:
            key (str): The key to identify the data to be stored.
            data (dict): The data containing information to be stored.
            source (str): The source of the data.

        Returns:
            dict: The modified data after storing the information.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            inner_data = data.get("data").get(key)
            for temp in inner_data:
                temp["task_id"] = data.get("task_id")
            if len(inner_data) > 0:
                self.send_to_sentinel(key, inner_data, source)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Ingested data = {}, For source = {}".format(key, source),
                    )
                )
            del data["data"][key]
            return data
        except KeyError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Key error : Error-{} source = {}".format(error, source),
                )
            )
            raise InfobloxException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Unexpected error : Error-{} source = {}".format(error, source),
                )
            )
            raise InfobloxException()

    def parse_response_and_ingest_to_sentinel(self, json_response):
        """Parse the JSON response and ingest the data to Sentinel based on the source.

        Args:
            self: The object instance.
            json_response: The JSON response containing the results data.

        Raises:
            InfobloxException: If an InfobloxException occurs during the process.
            Exception: If an unexpected error occurs.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            results_data = json_response["results"]
            for result_data in results_data:
                source = result_data["params"]["source"]
                if (source == "atp") and ("threat" in result_data["data"]):
                    result_data = self.store_data_in_separate_table("threat", result_data, source)
                elif (source == "rpz_feeds") and ("records" in result_data["data"]):
                    result_data = self.store_data_in_separate_table("records", result_data, source)
                elif (source == "nameserver") and ("matches" in result_data["data"]):
                    result_data = self.store_data_in_separate_table("matches", result_data, source)
                elif source == "threat_actor":
                    del result_data["data"]["related_indicators"]
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Ingesting data for source = {}".format(source),
                    )
                )
                result_data["status_message_for_dossier"] = consts.DOSSIER_STATUS_MESSAGE
                post_data(json.dumps(result_data, ensure_ascii=False), "{}_{}".format(consts.DOSSIER, source))
        except InfobloxException:
            raise InfobloxException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Unexpected error : Error-{} source = {}".format(error, source),
                )
            )
            raise InfobloxException()

    def get_job_result_and_ingest_in_sentinel(self, job_id):
        """Retrieve the job result and ingest it in Sentinel.

        Args:
            job_id (str): The ID of the job for which the result is to be retrieved.

        Returns:
            str: A message indicating the success of fetching and ingesting the dossier data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            url = consts.BASE_URL.format(consts.DOSSIER_ENDPOINTS["Result"]).format(job_id)
            response_json = self.make_dossier_call(url, method="GET", headers=self.headers)
            status = response_json.get("status")
            if status == "success":
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Dossier result fetched successfully",
                    )
                )
                self.parse_response_and_ingest_to_sentinel(response_json)
                return "Fetched and Ingested the dossier data successfully"
            else:
                return "Dossier result failed"
        except InfobloxException:
            raise InfobloxException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise InfobloxException()
