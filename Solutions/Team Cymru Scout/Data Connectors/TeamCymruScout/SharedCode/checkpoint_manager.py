"""This file contains CheckpointManager class to handle checkpoint related functions."""

import inspect
from . import consts
from .logger import applogger
from .state_manager import StateManager
from .teamcymruscout_exception import TeamCymruScoutException


class CheckpointManager:
    """Class for performing various tasks."""

    def __init__(self, file_path) -> None:
        """
        Initialize the insatnce object of CheckpointManager.

        Args:
            file_path (str): path of the file.
        """
        self.state = StateManager(connection_string=consts.CONN_STRING, file_path=file_path, share_name="teamcymruscout-checkpoints")

    def get_checkpoint(self, indicator_type):
        """
        To retrieve the checkpoint for a given indicator type.

        Args:
            indicator_type (str): The type of the indicator.

        Returns:
            Any: The checkpoint value if it exists, otherwise None.

        Raises:
            TeamCymruScoutException: If an error occurs while retrieving the checkpoint.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            last_data_index = self.state.get()
            if last_data_index:
                return last_data_index
            else:
                applogger.debug(
                    "{} (method={}): Checkpoint is not available for {}.".format(consts.LOGS_STARTS_WITH, __method_name, indicator_type)
                )
                return None
        except Exception as err:
            applogger.error("{}: (method={}): {}".format(consts.LOGS_STARTS_WITH, __method_name, err))
            raise TeamCymruScoutException()

    def save_checkpoint(self, data, indicator_type):
        """
        Save the checkpoint for a given indicator type.

        Args:
            data (Any): The data to be saved as the checkpoint.
            indicator_type (str): The type of the indicator.

        Raises:
            TeamCymruScoutException: If an error occurs while saving the checkpoint.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.state.post(data)
            applogger.info(
                "{} (method={}) Checkpoint data={} saved for {}".format(consts.LOGS_STARTS_WITH, __method_name, data, indicator_type)
            )
        except Exception as err:
            applogger.error("{} (method={}) {}".format(consts.LOGS_STARTS_WITH, __method_name, err))
            raise TeamCymruScoutException()
