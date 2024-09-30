"""This file contains implementation of companies endpoint."""

import json
from ..SharedCode.logger import applogger
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import CONN_STRING, LOGS_STARTS_WITH, CHECKPOINT_DATA_QUERY
from ..SharedCode.azure_sentinel import MicrosoftSentinel
from ..SharedCode.get_logs_data import get_logs_data


class CheckpointManager:
    """Class for managing checkpoints and state information."""

    def __init__(self) -> None:
        """Initialize CheckpointManager object."""
        self.connection_string = CONN_STRING
        self.sentinel_obj = MicrosoftSentinel()

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

    def remove_truncated_data(self, data):
        """Function to remove the truncated data from the checkpoint file.

        Args:
            data (str): data from the checkpoint file.

        Returns:
            list: data after removing the truncated data.
        """
        truncated_log_prefix = "REMOVE TRUNCATED DATA"
        try:
            reversed_data = data[::-1]
            comma_index = reversed_data.find(",")
            updated_data = data[: -comma_index - 1] + "]"
            data = json.loads(updated_data)
            return data
        except json.JSONDecodeError as err:
            applogger.error(
                "{} {}: JSONDecodeError: Unable to loads JSON data from Sentinel table. Error: {}".format(
                    LOGS_STARTS_WITH, truncated_log_prefix, err
                )
            )
            raise BitSightException()
        except Exception as err:
            applogger.error(
                "{} {}: Exception: Unknown error while loads JSON data from Sentinel table. Error: {}".format(
                    LOGS_STARTS_WITH, truncated_log_prefix, err
                )
            )
            raise BitSightException()

    def set_checkpoint_file_content(self, state: StateManager, content, company_flag):
        """Function update checkpoint file after getting corrupted data.

        Args:
            state (StateManager): StateManager instance.
            content (list): list of objects from Checkpoint Table for corresponding function.
            company_flag (bool): Flag indicating if the company name is requested.

        Raises:
            BitSightException: Raised for any exception during updating Checkpoint file.

        Returns:
            dict: dict object of checkpoint data.
            str: company name if company_flag is True
        """
        checkpoint_content = {}
        log_prefix = "SET CHECKPOINT FILE CONTENT"
        try:
            for data in content:
                val_val = data.get("Value_s")
                key_val = data.get("Key_g") or data.get("Key_s")
                if not key_val:
                    continue
                if "[" in val_val and "]" in val_val:
                    try:
                        checkpoint_content[key_val] = json.loads(val_val)
                    except json.JSONDecodeError:
                        applogger.error(
                            "{} {}: JSONDecodeError: Unable to loads JSON data for {} key from Sentinel table.".format(
                                LOGS_STARTS_WITH, log_prefix, key_val
                            )
                        )
                        continue
                elif "[" in val_val:
                    applogger.info(
                        "{} {}: Truncated data found for {} key from Sentinel table.".format(
                            LOGS_STARTS_WITH, log_prefix, key_val
                        )
                    )
                    updated_val = self.remove_truncated_data(val_val)
                    checkpoint_content[key_val] = updated_val
                else:
                    checkpoint_content[key_val] = val_val
            state.post(json.dumps(checkpoint_content))
            applogger.info(
                "{} {}: Checkpoint file data updated from corrupted data.".format(
                    LOGS_STARTS_WITH, log_prefix
                )
            )
            if company_flag:
                return val_val
            return checkpoint_content
        except Exception as error:
            applogger.error("{} {} Error: {}".format(LOGS_STARTS_WITH, log_prefix, error))
            raise BitSightException()

    def get_last_data(
        self, state: StateManager, table_name=None, company_name_flag=False, checkpoint_query=CHECKPOINT_DATA_QUERY
    ):
        """Fetch last data from the checkpoint file.

        Args:
            state (StateManager): StateManager instance.
            table_name (str): Table name for the checkpoint file.
            company_name_flag (bool): Flag indicating if the company name is requested.
            checkpoint_query (str): Query for fetching checkpoint data from table.default query is CHECKPOINT_DATA_QUERY

        Returns:
            None/json: Last data from the checkpoint file or None.
            str: company name if company_name_flag is True
        """
        try:
            last_data = state.get()
            if last_data:
                if company_name_flag:
                    company_name = json.loads(last_data).get("company_name")
                    return company_name
                return json.loads(last_data)
            else:
                applogger.debug("{} GET LAST DATA: Checkpoint is not available.".format(LOGS_STARTS_WITH))
                return None
        except json.decoder.JSONDecodeError as error:
            applogger.error("{} GET LAST DATA: JSONDecodeError: {}".format(LOGS_STARTS_WITH, error))
            if company_name_flag:
                table = "{}_{}".format(table_name, "Company_Checkpoint")
            else:
                table = "{}_{}".format(table_name, "Checkpoint")
            applogger.debug("{} Fetching Checkpoint data from table: {}".format(LOGS_STARTS_WITH, table))
            logs_data, logs_flag = get_logs_data(checkpoint_query.format(table))
            if logs_flag:
                return self.set_checkpoint_file_content(state, logs_data, company_flag=company_name_flag)
            else:
                return None
        except Exception as err:
            applogger.exception("{} GET LAST DATA Error: {}".format(LOGS_STARTS_WITH, err))
            raise BitSightException()

    def save_checkpoint(
        self,
        state,
        data,
        endpoint,
        table_name,
        checkpoint_key=None,
        value=None,
        company_name_flag=False,
    ):
        """Save checkpoint data into the state.

        Args:
            state (StateManager): StateManager instance.
            data (dict): Data to be saved in the checkpoint.
            endpoint (str): Endpoint for which the checkpoint is being saved.
            table_name (str): Table name for which the checkpoint is being saved.
            checkpoint_key (str): Checkpoint key.
            value (str): Value to be set in the checkpoint key.
            company_name_flag (bool): Flag indicating if the company name is used.

        Raises:
            BitSightException: Raised for any exception during checkpoint saving.
        """
        try:
            if company_name_flag:
                company_data = {"company_name": data}
                state.post(json.dumps(company_data))
                self.save_checkpoint_to_sentinel("company_name", data, table_name)
                applogger.info(
                    "{} save_checkpoint: {} -> {} successfully posted data.".format(LOGS_STARTS_WITH, endpoint, data)
                )
            else:
                if data is None:
                    data = {}
                data[checkpoint_key] = value
                self.save_checkpoint_to_sentinel(checkpoint_key, value, table_name)
                state.post(json.dumps(data))
                applogger.debug(
                    "BitSight: save_checkpoint: {}: {}: Posted Data: {}".format(
                        endpoint, checkpoint_key, data[checkpoint_key]
                    )
                )
        except Exception as err:
            applogger.exception("BitSight: SAVE CHECKPOINT: {}".format(err))
            raise BitSightException()

    def save_checkpoint_to_sentinel(self, checkpoint_key, checkpoint_value, table_name):
        """Save Checkpoint data into sentinel for backup purpose

        Args:
            checkpoint_key (str): unique key of the checkpoint value
            checkpoint_value (str): checkpoint value of the key to be stored
            table_name (str): Name of the Table in which data to be stored

        Raises:
            BitSightException: Raised for any exception during checkpoint data ingesting into sentinel.
        """
        try:
            json_data = self.convert_data_to_dict(checkpoint_key, checkpoint_value)
            body = json.dumps(json_data)
            ingestion_status_code = self.sentinel_obj.post_data(body, table_name)
            if ingestion_status_code >= 200 and ingestion_status_code <= 299:
                applogger.info(
                    "{} Checkpoint value: {} Stored to Sentinel Table Name: {} : Status code: {}".format(
                        LOGS_STARTS_WITH,
                        body,
                        table_name,
                        ingestion_status_code,
                    )
                )
            else:
                applogger.error(
                    "{} Error while storing Checkpoint value: {} into Sentinel Table Name: {} : Status code: {}".format(
                        LOGS_STARTS_WITH,
                        body,
                        table_name,
                        ingestion_status_code,
                    )
                )
                raise BitSightException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.error("{} SAVE CHECKPOINT TO SENTINEL: {}".format(LOGS_STARTS_WITH, err))
            raise BitSightException()

    def convert_data_to_dict(self, key, value):
        """Convert Key Value of checkpoint into a dict for storing into MS Sentinel Table

        Args:
            key (str): unique key of the value
            value (str): value of key
        """
        try:
            if not key and not value:
                applogger.warning(
                    "{} Both Key and Value must be non empty. Key: {} and Value: {}.".format(
                        LOGS_STARTS_WITH, key, value
                    )
                )
                raise ValueError()
            return {"Key": key, "Value": value}
        except ValueError as err:
            applogger.exception(
                "{} Error Occurred while creating dict from key value: {}".format(LOGS_STARTS_WITH, err)
            )
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
