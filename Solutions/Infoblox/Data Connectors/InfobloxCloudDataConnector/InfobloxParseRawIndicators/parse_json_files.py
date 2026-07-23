"""Parse the Json files and complete the raw json files."""

import datetime
import time
import inspect
import json
import re
from azure.storage.fileshare import ShareDirectoryClient
from ..SharedCode.logger import applogger
from ..SharedCode.infoblox_exception import InfobloxException, InfobloxTimeoutException
from ..SharedCode import consts
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import Utils


class ParseJsonFiles:
    """Parse JSON files class."""

    def __init__(self, start_time) -> None:
        """Init Function."""
        self.starttime = start_time
        self.parent_dir = ShareDirectoryClient.from_connection_string(
            conn_str=consts.CONN_STRING,
            share_name=consts.FILE_SHARE_NAME_DATA,
            directory_path="",
        )
        self.utils_obj = Utils(consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME)
        self.delete_file_count = 0

    def return_file_names_to_parse(self, files_list: list):
        """Return list of file names which are generated 15 mins ago to parse.

        Args:
            files_list (list): List of file names in the azure file share.

        Returns:
            list: List of file names to parse.
        """
        __method_name = inspect.currentframe().f_code.co_name
        # take each file name from the list and split the file name using '_'
        # Then get the 2nd element from the right and
        # if that epoch value is less than current_epoch (1 Hr) then add it to the list return it.
        try:
            current_epoch = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            list_of_prefix_file = []
            for file_name in files_list[:]:
                file_name_split = file_name.split("_")
                file_name_epoch = int(file_name_split[-2])
                if len(file_name_split) < 7:
                    list_of_prefix_file.append(file_name)
                    files_list.remove(file_name)
                elif (len(file_name_split) == 7) and (
                    (file_name_epoch + consts.TIME_BUFFER_RAW_EPOCH_VALUE) >= current_epoch
                ):
                    files_list.remove(file_name)
            list_of_prefix_file = tuple(list_of_prefix_file)
            for file_name in files_list[:]:
                if file_name.startswith(list_of_prefix_file):
                    files_list.remove(file_name)

            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Files to be parsed = {}, Count = {}".format(files_list, len(files_list)),
                )
            )
            return files_list
        except (ValueError, TypeError) as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    error,
                )
            )
            raise InfobloxException()
        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Error while getting list of files to be parsed: {}".format(error),
                )
            )
            raise InfobloxException()

    def get_checkpoint_data(self, file_name):
        """Retrieve the checkpoint data from the state manager object.

        Returns:
            Tuple: A tuple containing the file prefix and the index to start.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            state_manager_obj = StateManager(consts.CONN_STRING, file_name, consts.FILE_SHARE_NAME_DATA)
            raw_data = state_manager_obj.get()
            index_to_start = None
            if raw_data:
                index_to_start = int(raw_data.split(",")[-1])
            return index_to_start
        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Error while getting checkpoint file: {}".format(error),
                )
            )
            raise InfobloxException()

    def replace_raw_file_with_completed(self, file_name, data):
        """Delete raw file and write data in new checkpoint file.

        Args:
            file_name (str): The name of the file.
            data (any): The data to be written to the checkpoint file.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            new_file_name = file_name.replace("raw", "completed")
            applogger.info(
                "{}: (method = {}) : {} : {} has been successfully parsed data storing in new file name = {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    file_name,
                    new_file_name,
                )
            )
            state_manager_obj = StateManager(consts.CONN_STRING, new_file_name, consts.FILE_SHARE_NAME_DATA)
            state_manager_obj.post(data)
            self.utils_obj.delete_files_from_azure_storage([file_name], self.parent_dir)
            self.delete_file_count += 1
            applogger.info(
                "{}: (method = {}) : {} : Deleting {} file as data parsing is completed.".format(
                    consts.LOGS_STARTS_WITH, __method_name, consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME, file_name
                )
            )
            applogger.info(
                "{}: (method = {}) : {} : Total files deleted till now = {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    self.delete_file_count,
                )
            )
        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Error while writing to checkpoint file : {}".format(error),
                )
            )
            raise InfobloxException()

    def write_to_checkpoint_file(self, file_name, data_file_name, index):
        """Write file_name and index of file to a checkpoint file.

        Args:
            file_name (str): The name of the file.
            data_file_name (str): The name of the data file.
            index (int): The index to start.

        Returns:
            None
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            state_manager_obj = StateManager(consts.CONN_STRING, file_name, consts.FILE_SHARE_NAME_DATA)
            state_manager_obj.post(data_file_name + "," + str(index))
        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Error while writing to checkpoint file : {}".format(error),
                )
            )
            raise InfobloxException()

    def create_list_of_file_name_list(self, file_name_list):
        """Return a nested list of file name list grouped by prefix.

        Args:
            file_name_list (list): List of file names

        Returns:
            list: nested list of file names grouped by prefix
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            grouped_files = {}
            for file_name in file_name_list:
                prefix = file_name.rsplit("_", 1)[0]
                if prefix in grouped_files:
                    grouped_files[prefix].append(file_name)
                else:
                    grouped_files[prefix] = [file_name]
            grouped_files_list = list(grouped_files.values())
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "No. of nested file name lists grouped by prefix = {}".format(grouped_files_list),
                )
            )
            return grouped_files_list
        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Error while getting list of nested file names: {}".format(error),
                )
            )
            raise InfobloxException()

    def make_complete_json_file(self, file_data1, file_data2, is_first_chunk):
        """Combine and returns a single complete JSON data from 2 partial JSON data.

        Args:
            file_data1 (str): Partial JSON data.
            file_data2 (str): Partial JSON data.
            is_first_chunk (bool): Indicates if the file_data1 contains start of JSON data.

        Returns:
            tuple: A tuple containing complete JSON data and the remaining data that is not part of the complete JSON.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            start_index = 0
            original_index = len(file_data1)
            end_index = original_index

            chunk = file_data1[start_index:end_index]
            if not is_first_chunk:
                chunk = "[" + chunk
            index = 0
            open_brac_counter = 0
            read_counter = 0
            while True:
                try:
                    char = file_data2[index]
                except IndexError:
                    break

                if char == "{":
                    if read_counter == 0:
                        open_brac_counter = -1
                        read_counter += 1
                    open_brac_counter += 1
                if char == "}":
                    if read_counter == 0:
                        read_counter += 1
                    open_brac_counter -= 1
                chunk = chunk + file_data2[index]
                index += 1
                if open_brac_counter < 0:
                    try:
                        chunk = chunk + "]"
                        json.loads(chunk)
                        break
                    except json.JSONDecodeError:
                        open_brac_counter = 0
                        chunk = chunk[:-1]

            index += 1
            return chunk, index
        except Exception as err:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "while processing data in split data: Error-{}".format(err),
                )
            )
            raise InfobloxException()

    def fetch_first_data(self, json_file, fail_index=None):
        """Fetch First Data from Azure Storage.

        Args:
            json_file (str): Name of the json file
            fail_index (int, optional): Index for the file to start. Defaults to None.

        Returns:
            dict,bool: The json data from the file and bool for if it is first chunk or not
        """
        state_manager_obj_file1 = StateManager(
            consts.CONN_STRING,
            json_file,
            consts.FILE_SHARE_NAME_DATA,
        )
        if fail_index:
            data1 = state_manager_obj_file1.get()
            data1 = data1[fail_index:]
            return data1, False
        data1 = state_manager_obj_file1.get()
        is_first_chunk = True
        data1 = data1[consts.JSON_START_INDEX:]
        return data1, is_first_chunk

    def timeout_check(self):
        """Check if the execution time has passed 9 minutes 30 seconds and raise timeout exception.

        Raises:
            InfobloxTimeoutException: Timeout Exception
        """
        __method_name = inspect.currentframe().f_code.co_name
        if int(time.time()) > self.starttime + consts.FUNCTION_APP_TIMEOUT_SECONDS:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Runtime exceeded to 9 minutes 30 seconds, Stopping Execution.",
                )
            )
            raise InfobloxTimeoutException()

    def combine_and_make_complete_json(self, threat_iocs_file, fail_index=None):
        """
        Combine and make a complete JSON data from a list of JSON files.

        Args:
            threat_iocs_file (list): A list of JSON files to be combined.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            file_prefix = "_".join(threat_iocs_file[0].split("_")[:-1])
            file_prefix = file_prefix.replace("raw", "parse")
            if len(threat_iocs_file) > 1:
                data1, is_first_chunk = self.fetch_first_data(threat_iocs_file[0], fail_index)
                for index, json_file in enumerate(threat_iocs_file):
                    self.timeout_check()
                    if index < len(threat_iocs_file) - 1:
                        state_manager_obj_file2 = StateManager(
                            consts.CONN_STRING,
                            threat_iocs_file[index + 1],
                            consts.FILE_SHARE_NAME_DATA,
                        )
                        data2 = state_manager_obj_file2.get()
                        json_complete_data, data1_index = self.make_complete_json_file(data1, data2, is_first_chunk)
                        data1 = data2[data1_index:]
                        is_first_chunk = False
                        self.replace_raw_file_with_completed(json_file, json_complete_data)
                        applogger.info(
                            consts.LOG_FORMAT.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                                "Parsed {} file successfully".format(json_file),
                            )
                        )
                        self.write_to_checkpoint_file(file_prefix, threat_iocs_file[index + 1], data1_index)
                        continue
                    data1 = "[" + data1
                    index_of_last = -1
                    while data1[index_of_last] != "]":
                        index_of_last -= 1
                    applogger.info(
                        consts.LOG_FORMAT.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                            "Parsed {} file successfully".format(json_file),
                        )
                    )
                    json_complete_data = data1[: index_of_last + 1]
                    self.replace_raw_file_with_completed(json_file, json_complete_data)
                    self.utils_obj.delete_files_from_azure_storage([file_prefix], self.parent_dir)
                return None
            state_manager_obj = StateManager(consts.CONN_STRING, threat_iocs_file[0], consts.FILE_SHARE_NAME_DATA)
            data = state_manager_obj.get()
            if fail_index:
                data = data[fail_index:]
            else:
                data = data[consts.JSON_START_INDEX:]
            index_of_last = -1
            while data[index_of_last] != "]":
                print(data[index_of_last])
                index_of_last -= 1
            data = data[: index_of_last + 1]
            self.replace_raw_file_with_completed(threat_iocs_file[0], data)
            if fail_index:
                self.utils_obj.delete_files_from_azure_storage([file_prefix], self.parent_dir)
            return None
        except InfobloxTimeoutException:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Timeout occurred 9 minutes 30 seconds passed.",
                )
            )
            return None
        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "While combining and making complete json: Error-{}".format(error),
                )
            )
            raise InfobloxException()

    def list_file_names_and_parse_to_complete_json(self):
        """Prepare the file names and make complete json."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Started",
                )
            )

            list_of_files = self.utils_obj.list_file_names_in_file_share(self.parent_dir, consts.FILE_NAME_PREFIX)
            if not list_of_files:
                applogger.info(
                    consts.LOG_FORMAT.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                        "No files found in file share.",
                    )
                )
                return

            def extract_number(s):
                match = re.search(r"(\d+)$", s)
                return int(match.group(1)) if match else None

            list_of_files = sorted(list_of_files, key=extract_number)

            list_of_files_to_parse = self.return_file_names_to_parse(list_of_files)

            nested_combined_files_list = self.create_list_of_file_name_list(list_of_files_to_parse)

            # Iterate over each sublist and send it to the combine_and_make_complete_json function.
            for threat_iocs_file_list in nested_combined_files_list:
                if len(threat_iocs_file_list) > 0:
                    file_prefix = "_".join(threat_iocs_file_list[0].split("_")[:-1])
                    file_prefix = file_prefix.replace("raw", "parse")
                    index = self.get_checkpoint_data(file_prefix)
                    self.combine_and_make_complete_json(threat_iocs_file_list, index)

        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.PARSE_RAW_JSON_DATA_FUNCTION_NAME,
                    "Unknow error while parsing files: Error-{}".format(error),
                )
            )
            raise InfobloxException()
