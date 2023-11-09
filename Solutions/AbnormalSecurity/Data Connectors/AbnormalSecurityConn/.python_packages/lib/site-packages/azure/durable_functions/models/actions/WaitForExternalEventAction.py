from typing import Any, Dict, Union

from .Action import Action
from .ActionType import ActionType
from ..utils.json_utils import add_attrib


class WaitForExternalEventAction(Action):
    """Defines the structure of Wait for External Event object.

    Returns
    -------
    WaitForExternalEventAction
        Returns a WaitForExternalEventAction Class.

    Raises
    ------
    ValueError
        Raises error if external_event_name is not defined.
    """

    def __init__(self, external_event_name: str):
        self.external_event_name: str = external_event_name
        self.reason = "ExternalEvent"

        if not self.external_event_name:
            raise ValueError("external_event_name cannot be empty")

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.WAIT_FOR_EXTERNAL_EVENT

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Union[str, int]]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Union[str, int]] = {}

        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_attrib(json_dict, self, 'external_event_name', 'externalEventName')
        add_attrib(json_dict, self, 'reason', 'reason')
        return json_dict

    def __eq__(self, other):
        """Override the default __eq__ method.

        Returns
        -------
        Bool
            Returns True if two class instances has same values at all properties,
            and returns False otherwise.
        """
        if not isinstance(other, WaitForExternalEventAction):
            return False
        else:
            return self.action_type == other.action_type \
                and self.external_event_name == other.external_event_name \
                and self.reason == other.reason
