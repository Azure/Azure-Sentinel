from typing import Dict, Union

from .Action import Action
from .ActionType import ActionType
from ..utils.json_utils import add_attrib
from json import dumps
from azure.functions._durable_functions import _serialize_custom_object


class ContinueAsNewAction(Action):
    """Defines the structure of the Continue As New object.

    Provides the information needed by the durable extension to be able to reset the orchestration
    and continue as new.
    """

    def __init__(self, input_=None):
        self.input_ = dumps(input_, default=_serialize_custom_object)

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.CONTINUE_AS_NEW

    def to_json(self) -> Dict[str, Union[int, str]]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Union[int, str]] = {}
        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_attrib(json_dict, self, 'input_', 'input')
        return json_dict
