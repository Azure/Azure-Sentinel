from datetime import datetime
from dateutil.parser import parse as dt_parse
from typing import Any, List, Dict, Optional, Union
from .OrchestrationRuntimeStatus import OrchestrationRuntimeStatus
from .utils.json_utils import add_attrib, add_datetime_attrib


class DurableOrchestrationStatus:
    """Represents the status of a durable orchestration instance.

    Can be fetched using [[DurableOrchestrationClient]].[[get_status]].
    """

    # parameter names are as defined by JSON schema and do not conform to PEP8 naming conventions
    def __init__(self, name: Optional[str] = None, instanceId: Optional[str] = None,
                 createdTime: Optional[str] = None, lastUpdatedTime: Optional[str] = None,
                 input: Optional[Any] = None, output: Optional[Any] = None,
                 runtimeStatus: Optional[OrchestrationRuntimeStatus] = None,
                 customStatus: Optional[Any] = None,
                 history: Optional[List[Any]] = None,
                 **kwargs):
        self._name: Optional[str] = name
        self._instance_id: Optional[str] = instanceId
        self._created_time: Optional[datetime] = \
            dt_parse(createdTime) if createdTime is not None else None
        self._last_updated_time: Optional[datetime] = dt_parse(lastUpdatedTime) \
            if lastUpdatedTime is not None else None
        self._input: Any = input
        self._output: Any = output
        self._runtime_status: Optional[OrchestrationRuntimeStatus] = runtimeStatus
        if runtimeStatus is not None:
            self._runtime_status = OrchestrationRuntimeStatus(runtimeStatus)
        self._custom_status: Any = customStatus
        self._history: Optional[List[Any]] = history
        if kwargs is not None:
            for key, value in kwargs.items():
                self.__setattr__(key, value)

    def __bool__(self):
        """Determine if a class resolves to True or False.

        We say that a DurableOrchestrationStatus if False if it has a value
        `None` for its `_created_time` value, which should be empty if it
        refers to a non-existent orchestration. This facilitates a clean
        implementation of the Singleton pattern

        Returns
        -------
        bool
            True if self._created_time is not None. False otherwise.
        """
        return self._created_time is not None

    @classmethod
    def from_json(cls, json_obj: Any):
        """Convert the value passed into a new instance of the class.

        Parameters
        ----------
        json_obj: any
            JSON object to be converted into an instance of the class

        Returns
        -------
        DurableOrchestrationStatus
            New instance of the durable orchestration status class
        """
        if isinstance(json_obj, str):
            return cls(message=json_obj)
        else:
            return cls(**json_obj)

    def to_json(self) -> Dict[str, Union[int, str]]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Union[int, str]]
            The instance of the class converted into a json dictionary
        """
        json: Dict[str, Union[int, str]] = {}
        add_attrib(json, self, 'name')
        add_attrib(json, self, 'instance_id', 'instanceId')
        add_datetime_attrib(json, self, 'created_time', 'createdTime')
        add_datetime_attrib(json, self, 'last_updated_time', 'lastUpdatedTime')
        add_attrib(json, self, 'output')
        add_attrib(json, self, 'input_', 'input')
        if self.runtime_status is not None:
            json["runtimeStatus"] = self.runtime_status.name
        add_attrib(json, self, 'custom_status', 'customStatus')
        add_attrib(json, self, 'history')
        return json

    @property
    def name(self) -> Optional[str]:
        """Get the orchestrator function name."""
        return self._name

    @property
    def instance_id(self) -> Optional[str]:
        """Get the unique ID of the instance.

        The instance ID is generated and fixed when the orchestrator
        function is scheduled. It can either auto-generated, in which case
        it is formatted as a UUID, or it can be user-specified with any
        format.
        """
        return self._instance_id

    @property
    def created_time(self) -> Optional[datetime]:
        """Get the time at which the orchestration instance was created.

        If the orchestration instance is in the [[Pending]] status, this
        time represents the time at which the orchestration instance was
        scheduled.
        """
        return self._created_time

    @property
    def last_updated_time(self) -> Optional[datetime]:
        """Get the time at which the orchestration instance last updated its execution history."""
        return self._last_updated_time

    @property
    def input_(self) -> Any:
        """Get the input of the orchestration instance."""
        return self._input

    @property
    def output(self) -> Any:
        """Get the output of the orchestration instance."""
        return self._output

    @property
    def runtime_status(self) -> Optional[OrchestrationRuntimeStatus]:
        """Get the runtime status of the orchestration instance."""
        return self._runtime_status

    @property
    def custom_status(self) -> Any:
        """Get the custom status payload (if any).

        Set by [[DurableOrchestrationContext]].[[set_custom_status]].
        """
        return self._custom_status

    @property
    def history(self) -> Optional[List[Any]]:
        """Get the execution history of the orchestration instance.

        The history log can be large and is therefore `undefined` by
        default. It is populated only when explicitly requested in the call
        to [[DurableOrchestrationClient]].[[get_status]].
        """
        return self._history
