"""Netskope azure storage to sentinel."""
import inspect
import json
import aiohttp
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareDirectoryClient
from ..SharedCode.state_manager import StateManager
from ..SharedCode import consts
from .sentinel import post_data
from ..SharedCode.logger import applogger
from ..SharedCode.netskope_exception import NetskopeException
from math import ceil


class NetskopeAzureStorageToSentinel:
    """Netskope azure storage to sentinel utility class."""

    def __init__(self, share_name: str) -> None:
        """Initialize variables."""
        self.arr_to_return = []
        self.share_name = share_name
        if self.share_name.startswith("events"):
            self.nskp_data_type_for_logging = "_".join(["events", (share_name.split("events")[-1]).replace("data", "")])
        else:
            self.nskp_data_type_for_logging = "_".join(["alerts", (share_name.split("alerts")[-1]).replace("data", "")])
        iterators_state_manager_obj = StateManager(consts.CONNECTION_STRING, "iteratorsname", self.share_name)
        self.iterators_name = json.loads(iterators_state_manager_obj.get(consts.NETSKOPE_REMOVE_DUPLICATES))

    def is_response_empty(self, json_response):
        """Check if response is empty or not.

        Args:
            json_response (dict): Response from the netskope api.

        Raises:
            NetskopeException: Netskope Custom Exception.

        Returns:
            bool: True if response is empty else False.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if len(json_response.get("result")) == 0:
                applogger.info(
                    "{}(method={}) : {} ({}) : The data returned is empty. Continuing to next iteration.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                        self.nskp_data_type_for_logging,
                    )
                )
                return True
        except KeyError as key_error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while accessing the data key in the response. Error-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    key_error,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Unknown Error. Error-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()
        return False

    async def separate_data_into_chunks(self, raw_data):
        """Async generator function to separate data into 15 mb chunks and return them.

        Args:
            raw_data (bytes): raw bytes data from the file.

        Yields:
            bytearray: separated chunks in bytearray.
        """
        __method_name = inspect.currentframe().f_code.co_name
        raw_data = raw_data[20:-46]
        main_bytearray = bytearray(raw_data)
        index = 0
        start_index = 0
        original_index = consts.ORIGINAL_INDEX
        number_of_iterations = ceil(len(main_bytearray) / original_index)
        end_index = original_index
        is_first_chunk = True
        for _ in range(number_of_iterations):
            if len(main_bytearray) < end_index:
                chunk = main_bytearray[start_index:len(main_bytearray)]
                if not is_first_chunk:
                    chunk.insert(0, 91)
                yield chunk
                break

            chunk2 = bytearray()
            chunk = main_bytearray[start_index:end_index]
            if not is_first_chunk:
                chunk.insert(0, 91)  # adding square bracket to start of bytearray
            index = end_index
            open_brac_counter = 0
            read_counter = 0
            while True:
                if chr(main_bytearray[index]) == "{":
                    if read_counter == 0:
                        open_brac_counter = -1
                        read_counter += 1
                    open_brac_counter += 1
                if chr(main_bytearray[index]) == "}":
                    if read_counter == 0:
                        read_counter += 1
                    open_brac_counter -= 1
                chunk2.append(main_bytearray[index])
                index += 1
                if open_brac_counter < 0:
                    try:
                        chunk2.append(93)
                        json.loads(chunk + chunk2)
                        break
                    except Exception:
                        applogger.error(
                            "{}(method={}) : {} ({}) : Error while loading the json in split data, continuing.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                                self.nskp_data_type_for_logging,
                            )
                        )
                        open_brac_counter = 0
                        chunk2.pop()
            chunk3 = chunk + chunk2
            index += 2
            start_index = index
            end_index = start_index + original_index
            is_first_chunk = False
            yield chunk3

    def return_file_names_to_query(self, file_names: list):
        """Return the file names for current execution.

        Args:
            file_names (list): list of file
            prefix_to_search (str): file name prefix to search

        Returns:
            list: list of files
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            file_names_to_query = []
            for iterator_name in self.iterators_name:
                for file in file_names:
                    if iterator_name in file and "epoch" not in file and "failed" not in file:
                        file_names_to_query.append(file)
            applogger.info("{}(method={}) : {} ({}) : Number of files found to ingest to sentinel are {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                self.nskp_data_type_for_logging,
                len(file_names_to_query)
                )
            )
            return file_names_to_query
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while searching file names, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    def delete_file_from_file_share(self, file_name, parent_dir):
        """Delete the file from azure file share.

        Args:
            file_name (str): name of the file to delete
            parent_dir (ShareDirectory.from_connection_string): Object of ShareDirectory to perform operations
            on file share.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            parent_dir.delete_file(file_name)
            applogger.debug(
                "{}(method={}) : {} ({}) : File deleted successfully, filename-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    file_name,
                )
            )
        except ResourceNotFoundError:
            applogger.info(
                "{}(method={}) : {} ({}) : File not found while deleting, filename-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    file_name,
                )
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while deleting file, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    def get_files_list(self, parent_dir):
        """Get list of file names from directory.

        Args:
            parent_dir (ShareDirectory.from_connection_string): Object of ShareDirectory to perform operations
            on file share.

        Returns:
            list: list of files
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            files_list = list(parent_dir.list_directories_and_files())
            file_names = []
            if (len(files_list)) > 0:
                file_names = [file["name"] for file in files_list]
                return file_names
            return None
        except ResourceNotFoundError:
            applogger.error(
                "{}(method={}) : {} ({}) : No storage directory found.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                )
            )
            return None
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while getting list of files, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def generate_chunks_and_ingest_data_to_sentinel(self, raw_data, log_type, session):
        """Separate the data into chunks and post the chunks to Log Analytics.

        Args:
            raw_data (bytes): raw bytes data from the stored data.
            log_type (str): Name of the table to ingest data to.
            session (aiohttp.ClientSession): session object.
        """
        async for i in self.separate_data_into_chunks(raw_data):
            await post_data(json.dumps(json.loads(i)), log_type, session)

    def get_data_from_file(self, file_name):
        """Read file from azure storage.

        Args:
            file_name (str): file name to read

        Returns:
            json: Netskope data
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            state_manager_obj = StateManager(consts.CONNECTION_STRING, file_name, self.share_name)
            raw_data = state_manager_obj.get_data_bytes(consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL)
            return raw_data
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while reading netskope data from File, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def list_files_and_ingest_files_data_to_sentinel(self):
        """Read files list and ingest data to sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            parent_dir = ShareDirectoryClient.from_connection_string(
                conn_str=consts.CONNECTION_STRING,
                share_name=self.share_name,
                directory_path="",
            )
            count_data = 0
            file_names_to_query = self.get_files_list(parent_dir)
            file_names_to_get_data = self.return_file_names_to_query(file_names_to_query)
            if len(file_names_to_query) == 0:
                applogger.info(
                    "{}(method={}) : {} ({}) : The data is not yet processed for duplication.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                        self.nskp_data_type_for_logging,
                    )
                )

            async with aiohttp.ClientSession() as session:
                for file in file_names_to_get_data:
                    file_data = self.get_data_from_file(file)
                    if file_data is not None:
                        if self.is_response_empty(json.loads(file_data)):
                            applogger.info(
                                "{}(method={}) : {} ({}) : File Data was empty, hence deleting : {}.".format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                                    self.nskp_data_type_for_logging,
                                    file,
                                )
                            )
                        elif len(file_data) > 26214400:
                            await self.generate_chunks_and_ingest_data_to_sentinel(file_data, self.share_name, session)
                            count_data += 1
                            applogger.info(
                                "{}(method={}) : {} ({}) : Total files posted to Sentinel Till now : {}.".format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                                    self.nskp_data_type_for_logging,
                                    count_data,
                                )
                            )
                        else:
                            await post_data(
                                json.dumps(json.loads(file_data)["result"]),
                                self.share_name,
                                session,
                            )
                            applogger.info(
                                "{}(method={}) : {} ({}) : Netskope data posted successfully of file : {}.".format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                                    self.nskp_data_type_for_logging,
                                    file,
                                )
                            )
                            count_data += 1
                            applogger.info(
                                "{}(method={}) : {} ({}) : Total files posted to Sentinel Till now : {}.".format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                                    self.nskp_data_type_for_logging,
                                    count_data,
                                )
                            )
                    self.delete_file_from_file_share(file, parent_dir)
        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} ({}) : Error occurred in Netskope azure storage to sentinel.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error occurred in netskope azure storage to sentinel, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()
