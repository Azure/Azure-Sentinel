import json
from typing import List, Any, Dict, Optional, Union

from azure.durable_functions.models.ReplaySchema import ReplaySchema

from .utils.json_utils import add_attrib
from azure.durable_functions.models.actions.Action import Action


class OrchestratorState:
    """Orchestration State.

    Used to communicate the state of the orchestration back to the durable
    extension
    """

    def __init__(self,
                 is_done: bool,
                 actions: List[List[Action]],
                 output: Any,
                 replay_schema: ReplaySchema,
                 error: str = None,
                 custom_status: Any = None):
        self._is_done: bool = is_done
        self._actions: List[List[Action]] = actions
        self._output: Any = output
        self._error: Optional[str] = error
        self._custom_status: Any = custom_status
        self._replay_schema: ReplaySchema = replay_schema

    @property
    def actions(self) -> List[List[Action]]:
        """Get the ordered list of async actions the orchestrator function should perform.

        This list is append-only; it must contain all scheduled async actions up to the latest
        requested work, even actions that have already been completed.

        Actions are grouped by execution. Each subsequent orchestrator execution should add a
        new array of action objects to the collection.
        """
        return self._actions

    @property
    def is_done(self) -> bool:
        """Get indicator of whether this is the last execution of this orchestrator instance.

        When this value is true, the Durable Functions extension will consider the orchestration
        instance completed and will attempt to return the output value.
        """
        return self._is_done

    @property
    def output(self):
        """Get the JSON-serializable value returned by the orchestrator instance completion.

        Optional.
        """
        return self._output

    @property
    def error(self) -> Optional[str]:
        """Get the error received when running the orchestration.

        Optional.
        """
        return self._error

    @property
    def custom_status(self):
        """Get the JSON-serializable value used by DurableOrchestrationContext.SetCustomStatus."""
        return self._custom_status

    @property
    def schema_version(self):
        """Get the Replay Schema represented in this OrchestratorState payload."""
        return self._replay_schema.value

    def to_json(self) -> Dict[str, Union[str, int]]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Union[str, int]] = {}
        add_attrib(json_dict, self, '_is_done', 'isDone')
        if self._replay_schema != ReplaySchema.V1:
            add_attrib(json_dict, self, 'schema_version', 'schemaVersion')
        self._add_actions(json_dict)
        if not (self._output is None):
            json_dict['output'] = self._output
        if self._error:
            json_dict['error'] = self._error
        if self._custom_status:
            json_dict['customStatus'] = self._custom_status
        return json_dict

    def _add_actions(self, json_dict):
        json_dict['actions'] = []
        for action_list in self._actions:
            action_result_list = []
            for action_obj in action_list:
                action_result_list.append(action_obj.to_json())
            json_dict['actions'].append(action_result_list)

    def to_json_string(self) -> str:
        """Convert object into a json string.

        Returns
        -------
        str
            The instance of the object in json string format
        """
        json_dict = self.to_json()
        return json.dumps(json_dict)
