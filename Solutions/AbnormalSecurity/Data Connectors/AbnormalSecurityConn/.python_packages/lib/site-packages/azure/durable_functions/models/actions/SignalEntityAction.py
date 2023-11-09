from typing import Any, Dict

from .Action import Action
from .ActionType import ActionType
from ..utils.json_utils import add_attrib
from json import dumps
from azure.functions._durable_functions import _serialize_custom_object
from ..utils.entity_utils import EntityId


class SignalEntityAction(Action):
    """Defines the structure of the Signal Entity object.

    Provides the information needed by the durable extension to be able to signal an entity
    """

    def __init__(self, entity_id: EntityId, operation: str, input_=None):
        self.entity_id: EntityId = entity_id

        # Validating that EntityId exists before trying to parse its instanceId
        if not self.entity_id:
            raise ValueError("entity_id cannot be empty")

        self.instance_id: str = EntityId.get_scheduler_id(entity_id)
        self.operation: str = operation
        self.input_: str = dumps(input_, default=_serialize_custom_object)

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.SIGNAL_ENTITY

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Any] = {}
        add_attrib(json_dict, self, "action_type", "actionType")
        add_attrib(json_dict, self, 'instance_id', 'instanceId')
        add_attrib(json_dict, self, 'operation', 'operation')
        add_attrib(json_dict, self, 'input_', 'input')

        return json_dict
