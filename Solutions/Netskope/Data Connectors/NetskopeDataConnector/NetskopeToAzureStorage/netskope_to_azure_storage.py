"""Fetch Netskope data and post to azure storage."""
import inspect
import json
import time
import aiohttp
import asyncio

from SharedCode.netskope_exception import NetskopeException
from .netskope_api_async import NetskopeAPIAsync
from ..SharedCode.state_manager import StateManager
from ..SharedCode.logger import applogger
from ..SharedCode import consts
from ..SharedCode.validate_params import validate_parameters
from azure.storage.fileshare import ShareServiceClient


class NetskopeToAzureStorage:
    """Netskope to azure storage utility class."""

    def __init__(self, type_of_data, sub_type) -> None:
        """Initialize variables.

        Args:
            type_of_data (str): type of Netskope data
            sub_type (str): subtype of Netskope data
        """
        self.iterators = None
        self.starttime = int(time.time())
        self.netskope_api_async_obj = NetskopeAPIAsync(type_of_data, sub_type)
        self.share_name = type_of_data + sub_type + "data"
        self.share_name_for_duplication_check = type_of_data + sub_type + "duplicationcheck"
        self.type_of_data = type_of_data
        self.sub_type = sub_type
        self.nskp_data_type_for_logging = self.type_of_data + "_" + self.sub_type
        self.count = 0
        self.start_epoch_filename = "{}_start_epoch"
        try:
            validate_parameters(consts.NETSKOPE_TO_AZURE_STORAGE)
        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while initializing the class.".format(
                    consts.LOGS_STARTS_WITH,
                    "__init__",
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
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
                    "{}(method={}) : {} ({}) : The data returned is empty. Continuing to next iteration.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                    )
                )
                return True
        except KeyError as key_error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while accessing the data key in the response. Error-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
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
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()
        return False

    def delete_file_share(self):
        """Delete the file share.

        Raises:
            NetskopeException: Netskope Custom Exception.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                "{}(method={}) : {} ({}) : Deleting the file share.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            parent_dir = ShareServiceClient.from_connection_string(
                conn_str=consts.CONNECTION_STRING,
            )
            # deleting both the file shares for initializing iterators again.
            # deleting both share as if only one is deleted then there would be error in storage to sentinel. 
            parent_dir.delete_share(self.share_name)
            parent_dir.delete_share(self.share_name_for_duplication_check)
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Unknown Error. Error-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def honour_wait_time(self, data):
        """Honour the wait time returned in the response.

        Args:
            data (dict): The response returned by the netskope api.

        Raises:
            NetskopeException: Netskope custom exception.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            wait_time = int(data.get("wait_time"))
            if wait_time > 0:
                applogger.info(
                    "{}(method={}) : {} ({}) : The wait time returned is {}. Sleeping....".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                        wait_time,
                    )
                )
                await asyncio.sleep(wait_time)
        except KeyError as key_error:
            applogger.error(
                "{}(method={}) : {} ({}) : The Key wait_time not found. Error-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    key_error,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while honouring wait time. Error-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def reset_iterators(self, index, last_data_epoch, end_epoch, session):
        """Reset Netskope iterator.

        Args:
            index (int): index of iterator
            last_epoch (int): last epoch time
            session (aiohttp.ClientSession): session object

        Returns:
            int: updated epoch time
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            last_epoch_save_obj = StateManager(
                consts.CONNECTION_STRING,
                "{}_end_epoch_{}".format(index, str(int(time.time()))),
                self.share_name_for_duplication_check,
            )
            last_epoch_save_obj.post(str(last_data_epoch))
            updated_epoch = (3 * consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS) + end_epoch
            temp_state_manager_obj = StateManager(
                consts.CONNECTION_STRING,
                self.start_epoch_filename.format(index),
                self.share_name,
            )
            url = self.netskope_api_async_obj.url_builder(index, updated_epoch)
            data = await self.netskope_api_async_obj.aio_http_handler(url, session)
            temp_state_manager_obj.post(str(updated_epoch))
            applogger.info(
                "{}(method={}) : {} ({}) : Reset epoch {} for iterator {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    updated_epoch,
                    index,
                )
            )
            file_name_for_saving = "{}_{}_{}_{}"
            epoch = int(data.get("timestamp_hwm"))
            if epoch > updated_epoch + 2 * consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS:
                applogger.info(
                    "{}(method={}) : {} ({}) : The epoch timestamp is more than the next iterator,"
                    "allowed chunk for iterator-{}. Current-{}, End-{} .".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                        index,
                        epoch,
                        updated_epoch + consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS,
                    )
                )
                file_name_for_saving = "{}_{}_{}_{}_empty_file"
                data = {"ok": 1, "result": [], "wait_time": data.get("wait_time"), "timestamp_hwm": updated_epoch}
            state_manager_obj_to_post_data = StateManager(
                consts.CONNECTION_STRING,
                file_name_for_saving.format(
                    index,
                    str(self.starttime),
                    str(updated_epoch),
                    str(int(time.time())),
                ),
                self.share_name_for_duplication_check,
            )
            state_manager_obj_to_post_data.post(json.dumps(data))
            start_epoch_state_manager_obj_for_duplicate_handle = StateManager(
                consts.CONNECTION_STRING,
                "{}_start_epoch_{}".format(index, str(int(time.time()))),
                self.share_name_for_duplication_check,
            )
            start_epoch_state_manager_obj_for_duplicate_handle.post(str(updated_epoch))
            await self.honour_wait_time(data)
            return updated_epoch
        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while reseting iterators.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while reseting iterators, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def initiate_iterators(self):
        """Initialize Netskope iterators."""
        __method_name = inspect.currentframe().f_code.co_name
        applogger.info(
            "{}(method={}) : {} ({}) : Initializing the iterators.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_TO_AZURE_STORAGE,
                self.nskp_data_type_for_logging,
            )
        )
        try:
            iterators_state_manager_obj = StateManager(consts.CONNECTION_STRING, "iteratorsname", self.share_name)
            self.iterators = []
            for i in range(4):
                self.iterators.append(
                    "{}{}NSKPIterator{}_{}".format(self.type_of_data, self.sub_type, str(int(time.time())), i)
                )
            iterators_state_manager_obj.post(json.dumps(self.iterators))
            share_name = self.share_name
            async with aiohttp.ClientSession(
                headers={
                    "User-Agent": "Netskope MSSentinel",
                    "Netskope-Api-Token": consts.NETSKOPE_TOKEN,
                }
            ) as session:
                is_first_iterator = True
                for iterator in self.iterators:
                    if is_first_iterator:
                        url = self.netskope_api_async_obj.url_builder(iterator, "head")
                        data = await self.netskope_api_async_obj.aio_http_handler(url, session)
                        epoch = int(data.get("timestamp_hwm"))
                        applogger.info(
                            "{}(method={}) : {} ({}) : Initial epoch for first iterator {} is {}.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_TO_AZURE_STORAGE,
                                self.nskp_data_type_for_logging,
                                iterator,
                                epoch,
                            )
                        )
                        is_first_iterator = False
                    else:
                        share_name = self.share_name_for_duplication_check
                        epoch += consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS
                        applogger.info(
                            "{}(method={}) : {} ({}) : Initial epoch for {} is {}.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_TO_AZURE_STORAGE,
                                self.nskp_data_type_for_logging,
                                iterator,
                                epoch,
                            )
                        )
                        url = self.netskope_api_async_obj.url_builder(iterator, epoch)
                        data = await self.netskope_api_async_obj.aio_http_handler(url, session)
                        # start_epoch_state_manager_obj_for_duplicate_handle this is the epoch value of the file stored
                        # so that it can be used in removing the overlapping duplicates.
                        start_epoch_state_manager_obj_for_duplicate_handle = StateManager(
                            consts.CONNECTION_STRING,
                            "{}_start_epoch_{}".format(iterator, str(int(time.time()))),
                            share_name,
                        )
                        start_epoch_state_manager_obj_for_duplicate_handle.post(str(epoch))
                    write_data_state_manager_obj = StateManager(
                        consts.CONNECTION_STRING,
                        "{}_{}_{}_{}".format(
                            iterator,
                            str(self.starttime),
                            str(epoch),
                            str(int(time.time())),
                        ),
                        share_name,
                    )
                    write_data_state_manager_obj.post(json.dumps(data))
                    is_last_failed_state_manager_obj = StateManager(
                        consts.CONNECTION_STRING,
                        "{}_is_last_failed".format(iterator),
                        self.share_name,
                    )
                    is_last_failed_state_manager_obj.post("False")
                    start_epoch_state_manager_obj = StateManager(
                        consts.CONNECTION_STRING,
                        self.start_epoch_filename.format(iterator),
                        self.share_name,
                    )
                    start_epoch_state_manager_obj.post(str(epoch))
                    await self.honour_wait_time(data)
        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while Initializing iterators.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while Initializing iterators, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def remove_duplicates_generated_due_to_data_saving_failures(self, index, data, epoch):
        """Remove duplicate data if any due to data saving failure in the previous invocation.

        Args:
            index (str): The iterator name.
            data (dict): The data to check duplicate for.
            epoch (int): The epoch value in the data.

        Raises:
            NetskopeException: Custom Netskope Exception.

        Returns:
            bool: True if data is duplicate else False.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info("Checking for Duplicates")
            from azure.storage.fileshare import ShareDirectoryClient

            parent_dir = ShareDirectoryClient.from_connection_string(
                conn_str=consts.CONNECTION_STRING,
                share_name=self.share_name,
                directory_path="",
            )
            list_of_files_response = parent_dir.list_directories_and_files(name_starts_with=index)
            list_of_files = [file["name"] for file in list_of_files_response]
            file_name_with_provided_epoch = None
            epoch_of_file = 0
            for file in list_of_files:
                if (
                    "epoch" not in file
                    and "failed" not in file
                    and int(file.split("_")[-2]) == epoch
                    and int(file.split("_")[-1]) > epoch_of_file
                ):
                    file_name_with_provided_epoch = file
                    epoch_of_file = int(file.split("_")[-1])
            if file_name_with_provided_epoch:
                try:
                    state_manager_obj = StateManager(
                        consts.CONNECTION_STRING, file_name_with_provided_epoch, self.share_name
                    )
                    # Here we are fetching the previously saved data and comparing it with the data
                    # recieved in the current iteration and check if the data is duplicate or not.
                    duplicate_data = state_manager_obj.get(consts.NETSKOPE_TO_AZURE_STORAGE)
                    duplicate_json_data = json.loads(duplicate_data)
                    if duplicate_json_data == data or self.is_response_empty(duplicate_json_data):
                        applogger.error(
                            "{}(method={}) : {} ({}) : The data with epoch-{} and iterator-{} is duplicate.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_TO_AZURE_STORAGE,
                                self.nskp_data_type_for_logging,
                                epoch,
                                index,
                            )
                        )
                        return True
                    return False
                except json.JSONDecodeError:
                    parent_dir.delete_file(file_name_with_provided_epoch)
                    return False
            return False
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Unknown Error, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def get_netskope_data_and_post_to_azure_storage(self, index, url, session, end_epoch, is_resend=False):
        """Fetch Netskope data and post to azure storage.

        Args:
            index (str): name of iterator
            url (str): url for request
            session (aiohttp.ClientSession): session object
            end_epoch (int): end time epoch
            is_resend (bool): if it is resend or not.
        Returns:
            int: updated epoch time
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            share_name = self.share_name
            data = await self.netskope_api_async_obj.aio_http_handler(url, session)
            epoch = int(data.get("timestamp_hwm"))
            is_duplicate = False
            if is_resend:
                is_duplicate = await self.remove_duplicates_generated_due_to_data_saving_failures(index, data, epoch)

            if is_duplicate:
                applogger.info("The data for epoch {} and iterator {} was duplicate".format(epoch, index))
                return None

            applogger.info(
                "{}(method={}) : {} ({}) : Netskope data fetched for iterator {} till {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    index,
                    epoch,
                )
            )
            file_name_for_saving = "{}_{}_{}_{}"
            if epoch >= end_epoch:
                share_name = self.share_name_for_duplication_check
            if epoch > end_epoch + consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS:
                applogger.info(
                    "{}(method={}) : {} ({}) : The epoch timestamp is more than the next iterator,"
                    "allowed chunk for iterator-{}. Current-{}, End-{} .".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                        index,
                        epoch,
                        end_epoch,
                    )
                )
                share_name = self.share_name_for_duplication_check
                epoch = end_epoch
                file_name_for_saving = "{}_{}_{}_{}_empty_file"
                data = {"ok": 1, "result": [], "wait_time": data.get("wait_time"), "timestamp_hwm": end_epoch}
            state_manager_obj_to_post_data = StateManager(
                consts.CONNECTION_STRING,
                file_name_for_saving.format(
                    index,
                    str(self.starttime),
                    str(epoch),
                    str(int(time.time())),
                ),
                share_name,
            )
            state_manager_obj_to_post_data.post(json.dumps(data))
            applogger.info(
                "{}(method={}) : {} ({}) : Netskope data posted to azure storage for iterator {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    index,
                )
            )
            if epoch >= end_epoch:
                applogger.info(
                    "{}(method={}) : {} ({}) : Iterator-{} : Got the {} seconds netskope data at time-{}, "
                    "Breaking Execution.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                        index,
                        consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS,
                        int(time.time()),
                    )
                )

                updated_start = await self.reset_iterators(index, epoch, end_epoch, session)
                update_end_epoch = updated_start + consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS
                return update_end_epoch
            await self.honour_wait_time(data)
        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while getting data and post to state manager.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error captured in perform_request_function, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def check_last_failed_status_and_start_execution(self, index, end_epoch):
        """Check if last invocation was interrupted or not and start the execution accordingly.

        Args:
            index (int): index of iterator
            end_epoch (int): end epoch time
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            async with aiohttp.ClientSession(
                headers={
                    "User-Agent": "Netskope MSSentinel",
                    "Netskope-Api-Token": consts.NETSKOPE_TOKEN,
                }
            ) as session:
                is_last_failed_obj = StateManager(
                    consts.CONNECTION_STRING,
                    "{}_is_last_failed".format(index),
                    self.share_name,
                )
                while True:
                    # DATA_COLLECTION_TIMEOUT value is 570 seconds which is 9 minutes and 30 seconds
                    # We stop the exection at 9 minutes and 30 seconds to avoid issues due to function timeout.
                    if int(time.time()) >= self.starttime + consts.DATA_COLLECTION_TIMEOUT:
                        applogger.info(
                            "{}(method={}) : {} ({}) : 9:30 mins executed hence breaking.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_TO_AZURE_STORAGE,
                                self.nskp_data_type_for_logging,
                            )
                        )
                        break
                    is_last_failed = is_last_failed_obj.get(consts.NETSKOPE_TO_AZURE_STORAGE)
                    if is_last_failed == "False":
                        applogger.debug(
                            "{}(method={}) : {} ({}) : Fetching next Netskope data for iterator {}.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_TO_AZURE_STORAGE,
                                self.nskp_data_type_for_logging,
                                index,
                            )
                        )
                        is_last_failed_obj.post("True")
                        url = self.netskope_api_async_obj.url_builder(index, "next")
                        end_epoch_to_update = await self.get_netskope_data_and_post_to_azure_storage(
                            index, url, session, end_epoch
                        )
                        is_last_failed_obj.post("False")
                    else:
                        applogger.debug(
                            "{}(method={}) : {} ({}) : Last iteration failed for iterator {}, hence retrying.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_TO_AZURE_STORAGE,
                                self.nskp_data_type_for_logging,
                                index,
                            )
                        )
                        url = self.netskope_api_async_obj.url_builder(index, "resend")
                        end_epoch_to_update = await self.get_netskope_data_and_post_to_azure_storage(
                            index, url, session, end_epoch, True
                        )
                        is_last_failed_obj.post("False")
                    self.count += 1
                    applogger.debug(
                        "{}(method={}) : {} ({}) : The number of files stored to azure storage is {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_TO_AZURE_STORAGE,
                            self.nskp_data_type_for_logging,
                            self.count,
                        )
                    )
                    if end_epoch_to_update is not None:
                        end_epoch = end_epoch_to_update
        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} ({}) : Error while getting Netskope data.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error captured in get data, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()

    async def create_tasks(self, start_epochs_list):
        """Create asynchronous tasks of the get data function.

        Args:
            start_epochs_list (list): list of the start epochs

        Raises:
            NetskopeException: Netskope Custom Exception

        Returns:
            list: lists of created tasks
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            tasks_to_return = []
            for i, start_epoch in enumerate(start_epochs_list):
                # DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS is the time difference between any two iterators.
                # We calculate the end epoch of an iterator and reset epoch based on this value.
                end_epoch = start_epoch + consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS
                if end_epoch > int(time.time()):
                    applogger.info(
                        "{}(method={}) : {} ({}) : The iterator-{} is in {} seconds range of the current time,"
                        "hence skipping execution.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_TO_AZURE_STORAGE,
                            self.nskp_data_type_for_logging,
                            self.iterators[i],
                            consts.DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS,
                        )
                    )
                    continue
                tasks_to_return.append(
                    asyncio.create_task(self.check_last_failed_status_and_start_execution(self.iterators[i], end_epoch))
                )
            return tasks_to_return
        except Exception as e:
            applogger.error(
                "{}(method={}) : {} ({}) : Error occurred in Netskope to azure storage, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    e,
                )
            )
            raise NetskopeException()

    async def initiate_and_manage_iterators(self):
        """Initiate the iterators if first run and start the normal execution."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                "{}(method={}) : {} ({}) : Starting execution.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            iterators_state_manager_obj = StateManager(consts.CONNECTION_STRING, "iteratorsname", self.share_name)
            self.iterators = iterators_state_manager_obj.get(consts.NETSKOPE_TO_AZURE_STORAGE)
            if self.iterators is None:
                await self.initiate_iterators()
            else:
                self.iterators = json.loads(self.iterators)
            start_epochs_list = []
            iterator_initialize_successful = False
            retry_initiate_iterators = 0
            while not iterator_initialize_successful and retry_initiate_iterators < 3:
                iterator_initialize_successful = True
                for index in self.iterators:
                    start_epoch_obj = StateManager(
                        consts.CONNECTION_STRING,
                        self.start_epoch_filename.format(index),
                        self.share_name,
                    )
                    start_epoch_raw = start_epoch_obj.get(consts.NETSKOPE_TO_AZURE_STORAGE)
                    if start_epoch_raw is None:
                        applogger.error(
                            "{}(method={}) : {} ({}) : None returned in the start epoch for iterator-{}.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.NETSKOPE_TO_AZURE_STORAGE,
                                self.nskp_data_type_for_logging,
                                index,
                            )
                        )
                        iterator_initialize_successful = False
                        break
                    start_epochs_list.append(int(start_epoch_raw))
                if not iterator_initialize_successful:
                    applogger.info(
                        "{}(method={}) : {} ({}) : Initialization Failed, Deleting the file share and Retrying.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_TO_AZURE_STORAGE,
                            self.nskp_data_type_for_logging,
                        )
                    )
                    self.delete_file_share()
                    await self.initiate_iterators()
                    retry_initiate_iterators += 1
            if not iterator_initialize_successful:
                applogger.error(
                    "{}(method={}) : {} ({}) : Iterator initialization was not successful."
                    "Try execution after sometime.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                    )
                )
                raise NetskopeException()
            tasks = await self.create_tasks(start_epochs_list)
            await asyncio.gather(*tasks, return_exceptions=True)
        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} ({}) : Error occurred in Netskope to azure storage.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}) : Error occurred in Netskope to azure storage, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()
