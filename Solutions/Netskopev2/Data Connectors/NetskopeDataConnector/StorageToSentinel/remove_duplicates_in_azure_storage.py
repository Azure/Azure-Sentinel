"""Remove duplicate Netskope data from azure storage."""
import hashlib
import json
import inspect
import re
from ..SharedCode.state_manager import StateManager
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareDirectoryClient
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from itertools import cycle
from ..SharedCode.netskope_exception import NetskopeException


class RemoveDuplicatesInAzureStorage:
    """Utility class for removing duplicate Netskope data from azure storage."""

    def __init__(self, data_folder_share_name, share_name) -> None:
        """Initialize variables."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.duplicate_count = 0
            self.share_name = share_name
            self.data_folder_share_name = data_folder_share_name
            iterators_state_manager_obj = StateManager(
                consts.CONNECTION_STRING, "iteratorsname", self.data_folder_share_name
            )
            self.iterators_name = json.loads(iterators_state_manager_obj.get(consts.NETSKOPE_REMOVE_DUPLICATES))
            applogger.error(self.iterators_name)
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while removing duplicates from Azure Storage, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    error,
                )
            )
            raise NetskopeException()

    def move_to_data_folder(self, file_data, file_name, parent_dir, is_empty_in_file_name=False):
        """Move the file to the data folder for ingestion to sentinel.

        Args:
            file_data (list): data to write in file
            file_name (str): name of the file
            parent_dir (ShareDirectory.from_connection_string): Object of ShareDirectory to perform operations
            on file share.
            is_empty_in_file_name (bool, optional): True if the file name endswith empty. Defaults to False.
        """
        if not is_empty_in_file_name and not self.is_response_empty(file_data):
            new_file_state_manager_obj = StateManager(consts.CONNECTION_STRING, file_name, self.data_folder_share_name)
            new_file_state_manager_obj.post(json.dumps(file_data))
        self.delete_file_from_file_share(file_name, parent_dir)

    def filter_files(self, filter1, filter2, unfiltered_list):
        """Filter the given files list.

        Args:
            filter1 (str): first string to search
            filter2 (str): second string to search
            unfiltered_list (list): list to filter


        Returns:
            list: filtered files list
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info("The filter names are {} and {}".format(filter1, filter2))
            pattern = r"{filter1}_\d+_{filter2}_\d+".format(filter1=re.escape(filter1), filter2=re.escape(filter2))
            filtered_list = []
            filtered_list = [i for i in unfiltered_list if re.match(pattern, i)]
            return filtered_list
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while filtering files, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    error,
                )
            )
            raise NetskopeException()

    def list_file_names_in_file_share(self, parent_dir):
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
                for file in files_list:
                    file_names.append(file["name"])
            return file_names
        except ResourceNotFoundError:
            applogger.error(
                "{}(method={}) : {} : No storage directory found.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                )
            )
            return None
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while getting list of files, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
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
                "{}(method={}) : {} : File deleted successfully, filename-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    file_name,
                )
            )
        except ResourceNotFoundError:
            applogger.info(
                "{}(method={}) : {} : File not found while deleting, filename-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    file_name,
                )
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while deleting file, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    error,
                )
            )
            raise NetskopeException()

    def delete_duplicate_files(self, list_of_files, parent_dir):
        """Delete the duplicate files from the given list of files.

        Args:
            list_of_files (list): list of file names to check duplicates.
            parent_dir (ShareDirectoryClient): ShareDirectory client object

        Raises:
            NetskopeException: Netskope Custom Exception.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if len(list_of_files) == 1:
                return
            hashes = []
            for file in list_of_files:
                state_manager_obj = StateManager(consts.CONNECTION_STRING, file, self.share_name)
                file_data = state_manager_obj.get(consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL)
                hashes.append(hashlib.sha256(file_data.encode("utf-8")).hexdigest())
            duplicate_file_names = []
            applogger.info(list_of_files)
            for index, hashed_data in enumerate(hashes):
                is_hash_duplicate = hashed_data in hashes[:index]
                if is_hash_duplicate:
                    duplicate_file_names.append(list_of_files.pop(index))
            for duplicate_file in duplicate_file_names:
                self.delete_file_from_file_share(duplicate_file, parent_dir)
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while deleting duplicates, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    error,
                )
            )
            raise NetskopeException()

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
                    "{}(method={}) : {} : The data returned is empty. Continuing to next iteration.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    )
                )
                return True
        except KeyError as key_error:
            applogger.error(
                "{}(method={}) : {} : Error while accessing the data key in the response. Error-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    key_error,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Unknown Error. Error-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    error,
                )
            )
            raise NetskopeException()
        return False

    def remove_duplicates(self, list_of_old_files, new_files_to_compare, parent_dir):
        """Remove duplicates from given files.

        Args:
            list_of_old_files (list): list of old files
            new_files_to_compare (str): new file to compare
            parent_dir(ShareDirectoryClient): parent_dir object
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.delete_duplicate_files(list_of_old_files, parent_dir)
            self.delete_duplicate_files(new_files_to_compare, parent_dir)
            file: str
            for file in list_of_old_files:
                if file.endswith("empty_file"):
                    applogger.error(
                        "{}(method={}) : {} : Empty data is found in file name-{}.".format(
                            consts.LOGS_STARTS_WITH, __method_name, consts.NETSKOPE_REMOVE_DUPLICATES, file
                        )
                    )
                    self.move_to_data_folder(None, file, parent_dir, True)
                    continue
                state_manager_obj_for_old_file = StateManager(consts.CONNECTION_STRING, file, self.share_name)
                old_data_raw = state_manager_obj_for_old_file.get(consts.NETSKOPE_REMOVE_DUPLICATES)
                old_data = json.loads(old_data_raw)
                state_manager_obj_for_new_file = StateManager(
                    consts.CONNECTION_STRING, new_files_to_compare[0], self.share_name
                )
                new_data_raw = state_manager_obj_for_new_file.get(consts.NETSKOPE_REMOVE_DUPLICATES)
                new_data = json.loads(new_data_raw)
                if self.is_response_empty(old_data) or self.is_response_empty(new_data):
                    applogger.error(
                        "{}(method={}) : {} : Empty data is found in a file.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_REMOVE_DUPLICATES,
                        )
                    )
                    self.move_to_data_folder(old_data, file, parent_dir)
                    continue
                old_list_id = []
                for cur_data in old_data.get("result"):
                    old_list_id.append(cur_data["_id"])
                final_list = []
                for cur_data in new_data.get("result"):
                    if cur_data["_id"] in old_list_id:
                        self.duplicate_count += 1
                        continue
                    final_list.append(cur_data)
                new_data["result"] = final_list
                self.move_to_data_folder(old_data, file, parent_dir)
                state_manager_obj_for_new_file.post(json.dumps(new_data))
            # Fetch the updated new file data.
            if new_files_to_compare[0].endswith("empty_file"):
                self.move_to_data_folder(None, new_files_to_compare[0], parent_dir, True)
                return
            state_manager_obj_for_new_file = StateManager(
                consts.CONNECTION_STRING, new_files_to_compare[0], self.share_name
            )
            new_data_raw = state_manager_obj_for_new_file.get(consts.NETSKOPE_REMOVE_DUPLICATES)
            new_data = json.loads(new_data_raw)
            # move the new file to data folder.
            self.move_to_data_folder(new_data, new_files_to_compare[0], parent_dir)

        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while removing duplicates from azure storage, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    error,
                )
            )
            raise NetskopeException()

    def parse_files_and_find_duplicates(self, start_end_epochs, list_of_files, parent_dir):
        """Fetch the start and end epoch files data, get the file names with potential duplicates and remove duplicates.

        Args:
            start_end_epochs (dict): dictionary of epochs
            list_of_files (list): list of files
            parent_dir(ShareDirectoryClient): parent_dir object
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            it1_start = start_end_epochs.get("it1_start_epochs")
            it2_start = start_end_epochs.get("it2_start_epochs")
            it3_start = start_end_epochs.get("it3_start_epochs")
            it4_start = start_end_epochs.get("it4_start_epochs")
            it1_end = start_end_epochs.get("it1_end_epochs")
            it2_end = start_end_epochs.get("it2_end_epochs")
            it3_end = start_end_epochs.get("it3_end_epochs")
            it4_end = start_end_epochs.get("it4_end_epochs")
            queue_for_execution = [
                it1_end,
                it2_start,
                it2_end,
                it3_start,
                it3_end,
                it4_start,
                it4_end,
                it1_start,
            ]
            end_epoch_counter = [0, 1, 2, 3]
            start_epoch_counter = [1, 2, 3, 0]
            end_epoch_pool = cycle(end_epoch_counter)
            start_epoch_pool = cycle(start_epoch_counter)

            for _ in range(4):
                end_epochs_list = queue_for_execution.pop(0)
                start_epochs_list = queue_for_execution.pop(0)
                number_of_files_to_scan = min(len(end_epochs_list), len(start_epochs_list))
                end_counter = next(end_epoch_pool)
                start_counter = next(start_epoch_pool)
                for index in range(number_of_files_to_scan):
                    state_manager_obj_for_end_epoch = StateManager(
                        consts.CONNECTION_STRING,
                        "{}_end_epoch_{}".format(self.iterators_name[end_counter], end_epochs_list[index]),
                        self.share_name,
                    )
                    epoch_for_end_file = state_manager_obj_for_end_epoch.get(consts.NETSKOPE_REMOVE_DUPLICATES)
                    state_manager_obj_for_start_epoch = StateManager(
                        consts.CONNECTION_STRING,
                        "{}_start_epoch_{}".format(self.iterators_name[start_counter], start_epochs_list[index]),
                        self.share_name,
                    )
                    epoch_for_start_file = state_manager_obj_for_start_epoch.get(consts.NETSKOPE_REMOVE_DUPLICATES)
                    if epoch_for_end_file is None or epoch_for_start_file is None:
                        applogger.error(
                            "{}(method={}) : {} : Epoch File Returned None."
                            "End Epoch: {} and Start Epoch: {}".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_REMOVE_DUPLICATES,
                                epoch_for_end_file,
                                epoch_for_start_file,
                            )
                        )
                    end_epoch_files = self.filter_files(
                        self.iterators_name[end_counter],
                        epoch_for_end_file,
                        list_of_files,
                    )
                    start_epoch_files = self.filter_files(
                        self.iterators_name[start_counter],
                        epoch_for_start_file,
                        list_of_files,
                    )
                    if len(end_epoch_files) > 0 and len(start_epoch_files) > 0:
                        self.remove_duplicates(end_epoch_files, start_epoch_files, parent_dir)
                    state_manager_obj_for_sentinel_ingestion = StateManager(
                        consts.CONNECTION_STRING,
                        "{}_sentinel_ingestion_epoch".format(self.iterators_name[end_counter]),
                        self.share_name,
                    )
                    state_manager_obj_for_sentinel_ingestion.post(epoch_for_end_file)
                    self.delete_file_from_file_share(
                        "{}_end_epoch_{}".format(self.iterators_name[end_counter], end_epochs_list[index]),
                        parent_dir,
                    )
                    self.delete_file_from_file_share(
                        "{}_start_epoch_{}".format(self.iterators_name[start_counter], start_epochs_list[index]),
                        parent_dir,
                    )

        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} : Error while parsing files and finding duplicates.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while parsing files and finding duplicates, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    error,
                )
            )
            raise NetskopeException()

    def return_list_of_iterator_files(self, list_of_files):
        """Parse the list of iterator files and extract the epoch time created from the file names.

        Args:
            list_of_files (list): list of file names.

        Returns:
            dict: dictionary containing start epochs and end epochs.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            epochs = {}
            epochs["it1_start_epochs"] = []
            epochs["it2_start_epochs"] = []
            epochs["it3_start_epochs"] = []
            epochs["it4_start_epochs"] = []
            epochs["it1_end_epochs"] = []
            epochs["it2_end_epochs"] = []
            epochs["it3_end_epochs"] = []
            epochs["it4_end_epochs"] = []
            for file in list_of_files:
                epochs["it{}_{}_epochs".format(int(file.split("_")[-4]) + 1, file.split("_")[-3])].append(
                    file.split("_")[-1]
                )
            return epochs
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while parsing epoch from file list, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    error,
                )
            )
            raise NetskopeException()

    def list_file_names_and_remove_duplicate_data(self):
        """Code for removing duplicates from azure storage."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            parent_dir = ShareDirectoryClient.from_connection_string(
                conn_str=consts.CONNECTION_STRING,
                share_name=self.share_name,
                directory_path="",
            )
            all_file_list = self.list_file_names_in_file_share(parent_dir)
            list_of_epoch_files = []
            for file_name in all_file_list:
                if "_start_epoch_" in file_name or "_end_epoch_" in file_name:
                    list_of_epoch_files.append(file_name)
            applogger.info("The list of epoch files are {}".format(list_of_epoch_files))
            if len(list_of_epoch_files) > 0:
                dict_of_iter_epochs = self.return_list_of_iterator_files(list_of_epoch_files)
                self.parse_files_and_find_duplicates(dict_of_iter_epochs, all_file_list, parent_dir)
            applogger.info(
                "{}(method={}) : {} : Removed duplicate counts are {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    self.duplicate_count,
                )
            )
        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} : Failed to remove duplicates from azure storage.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Failed to remove duplicates from azure storage, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_REMOVE_DUPLICATES,
                    error,
                )
            )
            raise NetskopeException()
