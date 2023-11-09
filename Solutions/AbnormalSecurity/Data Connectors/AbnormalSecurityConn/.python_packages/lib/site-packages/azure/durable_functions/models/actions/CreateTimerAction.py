from typing import Any, Dict, Union

from .ActionType import ActionType
from .Action import Action
from ..utils.json_utils import add_attrib, add_datetime_attrib
import datetime


class CreateTimerAction(Action):
    """Defines the structure of the Create Timer object.

    Returns
    -------
        Information needed by durable extension to schedule the activity

    Raises
    ------
    ValueError
        if the event fired is not of valid datetime object
    """

    def __init__(self, fire_at: datetime.datetime, is_cancelled: bool = False):
        self._action_type: ActionType = ActionType.CREATE_TIMER
        self.fire_at: datetime.datetime = fire_at
        self.is_cancelled: bool = is_cancelled

        if not isinstance(self.fire_at, datetime.date):
            raise ValueError("fireAt: Expected valid datetime object but got ", self.fire_at)

    def to_json(self) -> Dict[str, Any]:
        """
        Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Union[int, str]] = {}
        add_attrib(json_dict, self, 'action_type', 'actionType')
        add_datetime_attrib(json_dict, self, 'fire_at', 'fireAt')
        add_attrib(json_dict, self, 'is_cancelled', 'isCanceled')
        return json_dict

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.CREATE_TIMER
