"""File for managing checkpoints."""
import json
import inspect
from .state_manager import StateManager
from .logger import applogger
from ..SharedCode import consts
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException


class ManageCheckpoints:
    """Class containing the checkpoint operations."""

    def __init__(self, file_name, azure_function_name) -> None:
        """Initiate connection string."""
        self.state_manager_object = StateManager(
            connection_string=consts.CONNECTION_STRING, file_path=file_name
        )
        self.azure_function_name = azure_function_name

    def get_checkpoint_data(self, key):
        """Get checkpoint data from azure file share.

        Args:
            key (str): The key to find in the checkpoint file.
        Returns:
            string: Checkpoint data
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            checkpoint_data = self.state_manager_object.get(self.azure_function_name)
            if checkpoint_data is None or checkpoint_data == "":
                applogger.info(
                    "{}(method={}) : {} : No checkpoint data found.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.azure_function_name
                    )
                )
                return None
            else:
                check_point_json = json.loads(checkpoint_data)
                applogger.info(
                    "{}(method={}) : {} : checkpoint data found : {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        check_point_json,
                    )
                )
                data = check_point_json.get(key, None)
                return data

        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error while getting checkpoint :{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()

    def post_data_to_checkpoint(self, key, value):
        """Post the checkpoint data to the Azure File share.

        Args:
            key (str): Key to store,
            value (str): Value of the key to store.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            checkpoint_data = self.state_manager_object.get(self.azure_function_name)
            if checkpoint_data == "" or checkpoint_data is None:
                data_to_send = {key: value}
                self.state_manager_object.post(json.dumps(data_to_send))
                applogger.info(
                    "{}(method={}) : {} : checkpoint file created and data posted successfully: {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        data_to_send,
                    )
                )
            else:
                json_checkpoint = json.loads(checkpoint_data)
                json_checkpoint[key] = value
                self.state_manager_object.post(json.dumps(json_checkpoint))
                applogger.info(
                    "{}(method={}) : {} : Updated checkpoint successfully: {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        json_checkpoint,
                    )
                )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error while posting checkpoint :{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()
