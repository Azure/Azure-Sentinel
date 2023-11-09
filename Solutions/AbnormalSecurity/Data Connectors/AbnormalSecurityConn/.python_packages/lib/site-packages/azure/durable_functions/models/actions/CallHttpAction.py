from typing import Any, Dict

from .Action import Action
from .ActionType import ActionType
from ..DurableHttpRequest import DurableHttpRequest
from ..utils.json_utils import add_attrib, add_json_attrib


class CallHttpAction(Action):
    """Defines the structure of the Call Http object.

    Provides the information needed by the durable extension to be able to schedule the activity.
    """

    def __init__(self, http_request: DurableHttpRequest):
        self._action_type: int = ActionType.CALL_HTTP
        self.http_request = http_request

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.CALL_HTTP

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Any] = {}
        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_json_attrib(json_dict, self, 'http_request', 'httpRequest')
        return json_dict
