"""This entity_collector file will pull and push the data of host entities."""

from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode.logger import applogger
from SharedCode.vectra_exception import VectraException
from ..SharedCode.consts import (
    ENTITIES_TABLE_NAME,
    ENTITIES_ENDPOINT,
    HOST_ENTITIES_NAME,
    LOGS_STARTS_WITH
)
import inspect


class HostEntityCollector(BaseCollector):
    """This class contains methods to create object and call get entities checkpoint and 'pull and push entities data'method."""

    def __init__(self, start_time, function_name, client_id, client_secret) -> None:
        """Initialize instance variable for class."""
        self.access_token_key = "access-token-host-entity"
        self.refresh_token_key = "refresh-token-host-entity"
        self.access_token_expiry = "expires_in_host_entity"
        self.refresh_token_expiry = "refresh_expires_in_host_entity"
        super(HostEntityCollector, self).__init__(
            start_time, function_name, client_id, client_secret
        )
        self.entities_table_name = ENTITIES_TABLE_NAME
        self.state = StateManager(
            connection_string=self.connection_string, file_path="entities_host"
        )

    def get_and_ingest_host_entities(self):
        """To get and ingest host and account entities data."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.validate_params(
                "HOST_ENTITY_CLIENT_ID",
                "HOST_ENTITY_CLIENT_SECRET",
            )
            applogger.info(
                "{}(method={}) : {} : Parameter validation successful.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    HOST_ENTITIES_NAME,
                )
            )
            self.validate_connection()
            applogger.info(
                "{}(method={}) : {} : Established connection with Vectra successfully.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    HOST_ENTITIES_NAME,
                )
            )
            last_modified_timestamp, page = self.get_entities_checkpoint(self.state)
            self.pull_and_push_entities_data(
                ENTITIES_ENDPOINT,
                last_modified_timestamp,
                page,
                self.entities_table_name,
                "host",
                self.state,
            )
        except VectraException:
            raise VectraException()
