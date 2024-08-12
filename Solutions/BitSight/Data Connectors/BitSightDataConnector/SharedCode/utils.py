"""This file contains implementation of companies endpoint."""
import json
from ..SharedCode.logger import applogger
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import CONN_STRING, LOGS_STARTS_WITH


class CheckpointManager:
    """Class for managing checkpoints and state information."""

    def __init__(self) -> None:
        """Initialize CheckpointManager object."""
        self.connection_string = CONN_STRING

    def get_state(self, file_path):
        """Get StateManager instance for a specific file path.

        Args:
            file_path (str): File path for the state.

        Returns:
            StateManager: StateManager instance.
        """
        return StateManager(
            connection_string=self.connection_string, file_path=file_path
        )

    def get_last_data(self, state: StateManager, company_name_flag=False):
        """Fetch last data from the checkpoint file.

        Args:
            state (StateManager): StateManager instance.
            company_name_flag (bool): Flag indicating if the company name is requested.

        Returns:
            None/json: Last data from the checkpoint file.
        """
        try:
            last_data = state.get()
            # applogger.info("Checkpoint Data: {}".format(last_data))
            if last_data:
                if company_name_flag:
                    return last_data
                return json.loads(last_data)
            else:
                applogger.debug(
                    "{}: GET LAST DATA: Checkpoint is not available.".format(
                        LOGS_STARTS_WITH
                    )
                )
                return None
        except Exception as err:
            applogger.exception("{}: GET LAST DATA: {}".format(LOGS_STARTS_WITH, err))
            raise BitSightException()

    def save_checkpoint(
        self,
        state,
        data,
        endpoint,
        checkpoint_key=None,
        value=None,
        company_name_flag=False,
    ):
        """Save checkpoint data into the state.

        Args:
            state (StateManager): StateManager instance.
            data (dict): Data to be saved in the checkpoint.
            endpoint (str): Endpoint for which the checkpoint is being saved.
            checkpoint_key (str): Checkpoint key.
            value (str): Value to be set in the checkpoint key.
            company_name_flag (bool): Flag indicating if the company name is used.

        Raises:
            BitSightException: Raised for any exception during checkpoint saving.
        """
        try:
            if company_name_flag:
                state.post(data)
            else:
                if data is None:
                    data = {}
                    # data[endpoint] = {}
                # elif endpoint not in data:
                # data[endpoint] = {}
                data[checkpoint_key] = value
                state.post(json.dumps(data))
                applogger.debug(
                    "BitSight: save_checkpoint: {}: {}: Posted Data: {}".format(
                        endpoint, checkpoint_key, data[checkpoint_key]
                    )
                )
            applogger.info(
                "BitSight: save_checkpoint: {} -> {} successfully posted data.".format(
                    endpoint, checkpoint_key
                )
            )
        except Exception as err:
            applogger.exception("BitSight: SAVE CHECKPOINT: {}".format(err))
            raise BitSightException()

    def get_endpoint_last_data(self, endpoint_last_data, endpoint, checkpoint_key):
        """Get last data for a specific endpoint and checkpoint key.

        Args:
            endpoint_last_data (dict): Last data for the endpoint.
            endpoint (str): Endpoint for which the data is requested.
            checkpoint_key (str): Checkpoint key.

        Returns:
            str: Last data for the specified endpoint and checkpoint key.

        Raises:
            BitSightException: Raised for any exception during data retrieval.
        """
        try:
            if not endpoint_last_data or not endpoint_last_data.get(checkpoint_key):
                applogger.debug(
                    "BitSight: get_endpoint_last_data: No checkpoint data for {} -> {}".format(
                        endpoint, checkpoint_key
                    )
                )
                return None
            last_data = endpoint_last_data.get(checkpoint_key)
            applogger.debug(
                "BitSight: get_endpoint_last_data: {}: {}: Data: {}".format(
                    endpoint, checkpoint_key, last_data
                )
            )
            return last_data
        except Exception as err:
            applogger.exception("BitSight: GET ENDPOINT LAST DATA: {}".format(err))
            raise BitSightException()
