"""This entity_collector file will pull and push the data of account entities."""

from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode import consts
import inspect


class AccountEntityCollector(BaseCollector):
    """This class contains methods to create object and call get entities checkpoint and 'pull and push entities data' method."""

    def __init__(self, applogger, function_name, client_id, client_secret) -> None:
        """Initialize instance variable for class."""
        self.access_token_key = "access-token-account-entity"
        self.refresh_token_key = "refresh-token-account-entity"
        self.access_token_expiry = "expires_in_account_entity"
        self.refresh_token_expiry = "refresh_expires_in_account_entity"
        super(AccountEntityCollector, self).__init__(
            applogger, function_name, client_id, client_secret
        )
        self.entities_table_name = consts.ENTITIES_TABLE_NAME
        self.state = StateManager(
            connection_string=self.connection_string,
            file_path="entities_account",
        )

    def get_and_ingest_account_entities(self):
        """To get and ingest host and account entities data."""
        __method_name = inspect.currentframe().f_code.co_name
        self.validate_params(
            "ACCOUNT_ENTITY_CLIENT_ID",
            "ACCOUNT_ENTITY_CLIENT_SECRET",
        )
        self.applogger.info(
            "{}(method={}) : {} : Parameter validation successful.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ACCOUNT_ENTITIES_NAME,
            )
        )
        self.validate_connection()
        self.applogger.info(
            "{}(method={}) : {} : Established connection with Vectra successfully.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.ACCOUNT_ENTITIES_NAME,
            )
        )
        checkpoint = self.get_entities_checkpoint(self.state)
        self.pull_and_push_entities_data(
            consts.ENTITIES_ENDPOINT,
            checkpoint,
            self.entities_table_name,
            "account",
            self.state,
        )
