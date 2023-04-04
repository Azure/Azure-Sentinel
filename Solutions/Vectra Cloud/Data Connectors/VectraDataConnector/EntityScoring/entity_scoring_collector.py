"""This entity_scoring_collector file will pull and push the data of entity scoring."""
from ..SharedCode.collector import BaseCollector
from ..SharedCode.state_manager import StateManager
from ..SharedCode.consts import ENTITY_SCORING_TABLE_NAME

ENTITY_SCORING_ENDPOINT = "/api/v3.2/events/entity_scoring"


class EntityScoringCollector(BaseCollector):
    """This class contains methods to create object and call get checkpoint and 'pull and push the data'method."""

    def __init__(self, applogger, function_name) -> None:
        """Initialize instance variable for class."""
        super(EntityScoringCollector, self).__init__(applogger, function_name)
        self.entity_scoring_table_name = ENTITY_SCORING_TABLE_NAME
        self.state = StateManager(connection_string=self.connection_string, file_path="entity_scoring")

    def get_entity_scoring_data_and_ingest_into_sentinel(self):
        """To call get checkpoint and 'pull and push the data' method."""
        field, checkpoint = self.get_checkpoint_field_and_value()
        self.pull_and_push_the_data(ENTITY_SCORING_ENDPOINT, field, checkpoint, self.entity_scoring_table_name)
