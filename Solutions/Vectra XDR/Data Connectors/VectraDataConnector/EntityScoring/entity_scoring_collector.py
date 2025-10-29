"""This entity_scoring_collector file will pull and push the data of entity scoring."""

from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import (
    ENTITY_SCORING_TABLE_NAME,
    ENTITY_SCORING_ENDPOINT,
    INCLUDE_SCORE_DECREASE,
)

MODIFIED_FIELDS = ["last_detection"]


class EntityScoringCollector(BaseCollector):
    """This class contains methods to create object and call get checkpoint and 'pull and push the data'method."""

    def __init__(self, applogger, function_name, client_id, client_secret) -> None:
        """Initialize instance variable for class."""
        self.access_token_key = "access-token-entityscore"
        self.refresh_token_key = "refresh-token-entityscore"
        self.access_token_expiry = "expires_in_entityscore"
        self.refresh_token_expiry = "refresh_expires_in_entityscore"
        super(EntityScoringCollector, self).__init__(
            applogger, function_name, client_id, client_secret
        )
        self.state = StateManager(
            connection_string=self.connection_string, file_path="entity_scoring_account"
        )
        self.entity_scoring_table_name = ENTITY_SCORING_TABLE_NAME

    def get_entity_scoring_data_and_ingest_into_sentinel_account(self):
        """To call get checkpoint and 'pull and push the data' method for account data."""
        params = {"type": "account"}
        if INCLUDE_SCORE_DECREASE == "true":
            params.update({"include_score_decreases": "true"})
        field, checkpoint = self.get_checkpoint_field_and_value()
        self.pull_and_push_the_data(
            ENTITY_SCORING_ENDPOINT,
            field,
            checkpoint,
            self.entity_scoring_table_name,
            query_params=params,
        )

    def get_entity_scoring_data_and_ingest_into_sentinel_host(self):
        """To call get checkpoint and 'pull and push the data' method for host data."""
        self.state = StateManager(
            connection_string=self.connection_string, file_path="entity_scoring_host"
        )
        params = {"type": "host"}
        if INCLUDE_SCORE_DECREASE == "true":
            params.update({"include_score_decreases": "true"})
        field, checkpoint = self.get_checkpoint_field_and_value()
        self.pull_and_push_the_data(
            ENTITY_SCORING_ENDPOINT,
            field,
            checkpoint,
            self.entity_scoring_table_name,
            query_params=params,
        )
