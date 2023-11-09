from typing import List, Optional, Dict, Any
from .Signal import Signal
from azure.functions._durable_functions import _serialize_custom_object
from .OperationResult import OperationResult
import json


class EntityState:
    """Entity State.

    Used to communicate the state of the entity back to the durable extension
    """

    def __init__(self,
                 results: List[OperationResult],
                 signals: List[Signal],
                 entity_exists: bool = False,
                 state: Optional[str] = None):
        self.entity_exists = entity_exists
        self.state = state
        self._results = results
        self._signals = signals

    @property
    def results(self) -> List[OperationResult]:
        """Get list of results of the entity.

        Returns
        -------
        List[OperationResult]:
            The results of the entity
        """
        return self._results

    @property
    def signals(self) -> List[Signal]:
        """Get list of signals to the entity.

        Returns
        -------
        List[Signal]:
            The signals of the entity
        """
        return self._signals

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Any] = {}
        # Serialize the OperationResult list
        serialized_results = list(map(lambda x: x.to_json(), self.results))

        json_dict["entityExists"] = self.entity_exists
        json_dict["entityState"] = json.dumps(self.state, default=_serialize_custom_object)
        json_dict["results"] = serialized_results
        json_dict["signals"] = self.signals
        return json_dict

    def to_json_string(self) -> str:
        """Convert object into a json string.

        Returns
        -------
        str
            The instance of the object in json string format
        """
        # TODO: Same implementation as in Orchestrator.py, we should refactor to shared a base
        json_dict = self.to_json()
        return json.dumps(json_dict)
