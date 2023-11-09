from collections import defaultdict
from azure.durable_functions.models.actions.SignalEntityAction import SignalEntityAction
from azure.durable_functions.models.actions.CallEntityAction import CallEntityAction
from azure.durable_functions.models.Task import TaskBase
from azure.durable_functions.models.actions.CallHttpAction import CallHttpAction
from azure.durable_functions.models.DurableHttpRequest import DurableHttpRequest
from azure.durable_functions.models.actions.CallSubOrchestratorWithRetryAction import \
    CallSubOrchestratorWithRetryAction
from azure.durable_functions.models.actions.CallActivityWithRetryAction import \
    CallActivityWithRetryAction
from azure.durable_functions.models.actions.ContinueAsNewAction import \
    ContinueAsNewAction
from azure.durable_functions.models.actions.WaitForExternalEventAction import \
    WaitForExternalEventAction
from azure.durable_functions.models.actions.CallSubOrchestratorAction import \
    CallSubOrchestratorAction
from azure.durable_functions.models.actions.CreateTimerAction import CreateTimerAction
from azure.durable_functions.models.Task import WhenAllTask, WhenAnyTask, AtomicTask, \
    RetryAbleTask
from azure.durable_functions.models.actions.CallActivityAction import CallActivityAction
from azure.durable_functions.models.ReplaySchema import ReplaySchema
import json
import datetime
import inspect
from typing import DefaultDict, List, Any, Dict, Optional, Tuple, Union
from uuid import UUID, uuid5, NAMESPACE_URL, NAMESPACE_OID
from datetime import timezone

from .RetryOptions import RetryOptions
from .FunctionContext import FunctionContext
from .history import HistoryEvent, HistoryEventType
from .actions import Action
from ..models.TokenSource import TokenSource
from .utils.entity_utils import EntityId
from azure.functions._durable_functions import _deserialize_custom_object
from azure.durable_functions.constants import DATETIME_STRING_FORMAT


class DurableOrchestrationContext:
    """Context of the durable orchestration execution.

    Parameter data for orchestration bindings that can be used to schedule
    function-based activities.
    """

    # parameter names are as defined by JSON schema and do not conform to PEP8 naming conventions
    def __init__(self,
                 history: List[Dict[Any, Any]], instanceId: str, isReplaying: bool,
                 parentInstanceId: str, input: Any = None, upperSchemaVersion: int = 0, **kwargs):
        self._histories: List[HistoryEvent] = [HistoryEvent(**he) for he in history]
        self._instance_id: str = instanceId
        self._is_replaying: bool = isReplaying
        self._parent_instance_id: str = parentInstanceId
        self._custom_status: Any = None
        self._new_uuid_counter: int = 0
        self._sub_orchestrator_counter: int = 0
        self._continue_as_new_flag: bool = False
        self.decision_started_event: HistoryEvent = \
            [e_ for e_ in self.histories
             if e_.event_type == HistoryEventType.ORCHESTRATOR_STARTED][0]
        self._current_utc_datetime: datetime.datetime = \
            self.decision_started_event.timestamp
        self._new_uuid_counter = 0
        self._function_context: FunctionContext = FunctionContext(**kwargs)
        self._sequence_number = 0
        self._replay_schema = ReplaySchema(upperSchemaVersion)

        self._action_payload_v1: List[List[Action]] = []
        self._action_payload_v2: List[Action] = []

        # make _input always a string
        # (consistent with Python Functions generic trigger/input bindings)
        if (isinstance(input, Dict)):
            input = json.dumps(input)

        self._input: Any = input
        self.open_tasks: DefaultDict[Union[int, str], Union[List[TaskBase], TaskBase]]
        self.open_tasks = defaultdict(list)
        self.deferred_tasks: Dict[Union[int, str], Tuple[HistoryEvent, bool, str]] = {}

    @classmethod
    def from_json(cls, json_string: str):
        """Convert the value passed into a new instance of the class.

        Parameters
        ----------
        json_string: str
            Context passed a JSON serializable value to be converted into an instance of the class

        Returns
        -------
        DurableOrchestrationContext
            New instance of the durable orchestration context class
        """
        # We should consider parsing the `Input` field here as well,
        # instead of doing so lazily when `get_input` is called.
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    def _generate_task(self, action: Action,
                       retry_options: Optional[RetryOptions] = None,
                       id_: Optional[Union[int, str]] = None,
                       parent: Optional[TaskBase] = None) -> Union[AtomicTask, RetryAbleTask]:
        """Generate an atomic or retryable Task based on an input.

        Parameters
        ----------
        action : Action
            The action backing the Task.
        retry_options : Optional[RetryOptions]
            RetryOptions for a with-retry task, by default None

        Returns
        -------
        Union[AtomicTask, RetryAbleTask]
            Either an atomic task or a retry-able task
        """
        # Create an atomic task
        task: Union[AtomicTask, RetryAbleTask]
        action_payload: Union[Action, List[Action]]

        # TODO: find cleanear way to do this
        if self._replay_schema is ReplaySchema.V1:
            action_payload = [action]
        else:
            action_payload = action
        task = AtomicTask(id_, action_payload)
        task.parent = parent

        # if task is retryable, provide the retryable wrapper class
        if not(retry_options is None):
            task = RetryAbleTask(task, retry_options, self)
        return task

    def _set_is_replaying(self, is_replaying: bool):
        """Set the internal `is_replaying` flag.

        Parameters
        ----------
        is_replaying : bool
            New value of the `is_replaying` flag
        """
        self._is_replaying = is_replaying

    def call_activity(self, name: str, input_: Optional[Any] = None) -> TaskBase:
        """Schedule an activity for execution.

        Parameters
        ----------
        name: str
            The name of the activity function to call.
        input_: Optional[Any]
            The JSON-serializable input to pass to the activity function.

        Returns
        -------
        Task
            A Durable Task that completes when the called activity function completes or fails.
        """
        action = CallActivityAction(name, input_)
        task = self._generate_task(action)
        return task

    def call_activity_with_retry(self,
                                 name: str, retry_options: RetryOptions,
                                 input_: Optional[Any] = None) -> TaskBase:
        """Schedule an activity for execution with retry options.

        Parameters
        ----------
        name: str
            The name of the activity function to call.
        retry_options: RetryOptions
            The retry options for the activity function.
        input_: Optional[Any]
            The JSON-serializable input to pass to the activity function.

        Returns
        -------
        Task
            A Durable Task that completes when the called activity function completes or
            fails completely.
        """
        action = CallActivityWithRetryAction(name, retry_options, input_)
        task = self._generate_task(action, retry_options)
        return task

    def call_http(self, method: str, uri: str, content: Optional[str] = None,
                  headers: Optional[Dict[str, str]] = None,
                  token_source: TokenSource = None) -> TaskBase:
        """Schedule a durable HTTP call to the specified endpoint.

        Parameters
        ----------
        method: str
            The HTTP request method.
        uri: str
            The HTTP request uri.
        content: Optional[str]
            The HTTP request content.
        headers: Optional[Dict[str, str]]
            The HTTP request headers.
        token_source: TokenSource
            The source of OAuth token to add to the request.

        Returns
        -------
        Task
            The durable HTTP request to schedule.
        """
        json_content: Optional[str] = None
        if content and content is not isinstance(content, str):
            json_content = json.dumps(content)
        else:
            json_content = content

        request = DurableHttpRequest(method, uri, json_content, headers, token_source)
        action = CallHttpAction(request)
        task = self._generate_task(action)
        return task

    def call_sub_orchestrator(self,
                              name: str, input_: Optional[Any] = None,
                              instance_id: Optional[str] = None) -> TaskBase:
        """Schedule sub-orchestration function named `name` for execution.

        Parameters
        ----------
        name: str
            The name of the orchestrator function to call.
        input_: Optional[Any]
            The JSON-serializable input to pass to the orchestrator function.
        instance_id: Optional[str]
            A unique ID to use for the sub-orchestration instance.

        Returns
        -------
        Task
            A Durable Task that completes when the called sub-orchestrator completes or fails.
        """
        action = CallSubOrchestratorAction(name, input_, instance_id)
        task = self._generate_task(action)
        return task

    def call_sub_orchestrator_with_retry(self,
                                         name: str, retry_options: RetryOptions,
                                         input_: Optional[Any] = None,
                                         instance_id: Optional[str] = None) -> TaskBase:
        """Schedule sub-orchestration function named `name` for execution, with retry-options.

        Parameters
        ----------
        name: str
            The name of the activity function to schedule.
        retry_options: RetryOptions
            The settings for retrying this sub-orchestrator in case of a failure.
        input_: Optional[Any]
            The JSON-serializable input to pass to the activity function. Defaults to None.
        instance_id: str
            The instance ID of the sub-orchestrator to call.

        Returns
        -------
        Task
            A Durable Task that completes when the called sub-orchestrator completes or fails.
        """
        action = CallSubOrchestratorWithRetryAction(name, retry_options, input_, instance_id)
        task = self._generate_task(action, retry_options)
        return task

    def get_input(self) -> Optional[Any]:
        """Get the orchestration input."""
        return None if self._input is None else json.loads(self._input,
                                                           object_hook=_deserialize_custom_object)

    def new_uuid(self) -> str:
        """Create a new UUID that is safe for replay within an orchestration or operation.

        The default implementation of this method creates a name-based UUID
        using the algorithm from RFC 4122 §4.3. The name input used to generate
        this value is a combination of the orchestration instance ID and an
        internally managed sequence number.

        Returns
        -------
        str
            New UUID that is safe for replay within an orchestration or operation.
        """
        URL_NAMESPACE: str = "9e952958-5e33-4daf-827f-2fa12937b875"

        uuid_name_value = \
            f"{self._instance_id}" \
            f"_{self.current_utc_datetime.strftime(DATETIME_STRING_FORMAT)}" \
            f"_{self._new_uuid_counter}"
        self._new_uuid_counter += 1
        namespace_uuid = uuid5(NAMESPACE_OID, URL_NAMESPACE)
        return str(uuid5(namespace_uuid, uuid_name_value))

    def task_all(self, activities: List[TaskBase]) -> TaskBase:
        """Schedule the execution of all activities.

        Similar to Promise.all. When called with `yield` or `return`, returns an
        array containing the results of all [[Task]]s passed to it. It returns
        when all of the [[Task]] instances have completed.

        Throws an exception if any of the activities fails
        Parameters
        ----------
        activities: List[Task]
            List of activities to schedule

        Returns
        -------
        TaskSet
            The results of all activities.
        """
        return WhenAllTask(activities, replay_schema=self._replay_schema)

    def task_any(self, activities: List[TaskBase]) -> TaskBase:
        """Schedule the execution of all activities.

        Similar to Promise.race. When called with `yield` or `return`, returns
        the first [[Task]] instance to complete.

        Throws an exception if all of the activities fail

        Parameters
        ----------
        activities: List[Task]
            List of activities to schedule

        Returns
        -------
        TaskSet
            The first [[Task]] instance to complete.
        """
        return WhenAnyTask(activities, replay_schema=self._replay_schema)

    def set_custom_status(self, status: Any):
        """Set the customized orchestration status for your orchestrator function.

        This status is also returned by the orchestration client through the get_status API

        Parameters
        ----------
        status : str
            Customized status provided by the orchestrator
        """
        self._custom_status = status

    @property
    def custom_status(self):
        """Get customized status of current orchestration."""
        return self._custom_status

    @property
    def histories(self):
        """Get running history of tasks that have been scheduled."""
        return self._histories

    @property
    def instance_id(self) -> str:
        """Get the ID of the current orchestration instance.

        The instance ID is generated and fixed when the orchestrator function
        is scheduled. It can be either auto-generated, in which case it is
        formatted as a GUID, or it can be user-specified with any format.

        Returns
        -------
        str
            The ID of the current orchestration instance.
        """
        return self._instance_id

    @property
    def is_replaying(self) -> bool:
        """Get the value indicating orchestration replaying itself.

        This property is useful when there is logic that needs to run only when
        the orchestrator function is _not_ replaying. For example, certain
        types of application logging may become too noisy when duplicated as
        part of orchestrator function replay. The orchestrator code could check
        to see whether the function is being replayed and then issue the log
        statements when this value is `false`.

        Returns
        -------
        bool
            Value indicating whether the orchestrator function is currently replaying.
        """
        return self._is_replaying

    @property
    def parent_instance_id(self) -> str:
        """Get the ID of the parent orchestration.

        The parent instance ID is generated and fixed when the parent
        orchestrator function is scheduled. It can be either auto-generated, in
        which case it is formatted as a GUID, or it can be user-specified with
        any format.

        Returns
        -------
        str
            ID of the parent orchestration of the current sub-orchestration instance
        """
        return self._parent_instance_id

    @property
    def current_utc_datetime(self) -> datetime.datetime:
        """Get the current date/time.

        This date/time value is derived from the orchestration history. It
        always returns the same value at specific points in the orchestrator
        function code, making it deterministic and safe for replay.

        Returns
        -------
        datetime
            The current date/time in a way that is safe for use by orchestrator functions
        """
        return self._current_utc_datetime

    @current_utc_datetime.setter
    def current_utc_datetime(self, value: datetime.datetime):
        self._current_utc_datetime = value

    @property
    def function_context(self) -> FunctionContext:
        """Get the function level attributes not used by durable orchestrator.

        Returns
        -------
        FunctionContext
            Object containing function level attributes not used by durable orchestrator.
        """
        return self._function_context

    def call_entity(self, entityId: EntityId,
                    operationName: str, operationInput: Optional[Any] = None):
        """Get the result of Durable Entity operation given some input.

        Parameters
        ----------
        entityId: EntityId
            The ID of the entity to call
        operationName: str
            The operation to execute
        operationInput: Optional[Any]
            The input for tne operation, defaults to None.

        Returns
        -------
        Task
            A Task of the entity call
        """
        action = CallEntityAction(entityId, operationName, operationInput)
        task = self._generate_task(action)
        return task

    def _record_fire_and_forget_action(self, action: Action):
        """Append a responseless-API action object to the actions array.

        Parameters
        ----------
        action : Action
            The action to append
        """
        new_action: Union[List[Action], Action]
        if self._replay_schema is ReplaySchema.V2:
            new_action = action
        else:
            new_action = [action]
        self._add_to_actions(new_action)
        self._sequence_number += 1

    def signal_entity(self, entityId: EntityId,
                      operationName: str, operationInput: Optional[Any] = None):
        """Send a signal operation to Durable Entity given some input.

        Parameters
        ----------
        entityId: EntityId
            The ID of the entity to call
        operationName: str
            The operation to execute
        operationInput: Optional[Any]
            The input for tne operation, defaults to None.

        Returns
        -------
        Task
            A Task of the entity signal
        """
        action = SignalEntityAction(entityId, operationName, operationInput)
        task = self._generate_task(action)
        self._record_fire_and_forget_action(action)
        return task

    @property
    def will_continue_as_new(self) -> bool:
        """Return true if continue_as_new was called."""
        return self._continue_as_new_flag

    def create_timer(self, fire_at: datetime.datetime) -> TaskBase:
        """Create a Durable Timer Task to implement a deadline at which to wake-up the orchestrator.

        Parameters
        ----------
        fire_at : datetime.datetime
            The time for the timer to trigger

        Returns
        -------
        TaskBase
            A Durable Timer Task that schedules the timer to wake up the activity
        """
        action = CreateTimerAction(fire_at)
        task = self._generate_task(action)
        return task

    def wait_for_external_event(self, name: str) -> TaskBase:
        """Wait asynchronously for an event to be raised with the name `name`.

        Parameters
        ----------
        name : str
            The event name of the event that the task is waiting for.

        Returns
        -------
        Task
            Task to wait for the event
        """
        action = WaitForExternalEventAction(name)
        task = self._generate_task(action, id_=name)
        return task

    def continue_as_new(self, input_: Any):
        """Schedule the orchestrator to continue as new.

        Parameters
        ----------
        input_ : Any
            The new starting input to the orchestrator.
        """
        continue_as_new_action: Action = ContinueAsNewAction(input_)
        self._record_fire_and_forget_action(continue_as_new_action)
        self._continue_as_new_flag = True

    def new_guid(self) -> UUID:
        """Generate a replay-safe GUID.

        Returns
        -------
        UUID
            A new globally-unique ID
        """
        guid_name = f"{self.instance_id}_{self.current_utc_datetime}"\
            f"_{self._new_uuid_counter}"
        self._new_uuid_counter += 1
        guid = uuid5(NAMESPACE_URL, guid_name)
        return guid

    @property
    def _actions(self) -> List[List[Action]]:
        """Get the actions payload of this context, for replay in the extension.

        Returns
        -------
        List[List[Action]]
            The actions of this context
        """
        if self._replay_schema is ReplaySchema.V1:
            return self._action_payload_v1
        else:
            return [self._action_payload_v2]

    def _add_to_actions(self, action_repr: Union[List[Action], Action]):
        """Add a Task's actions payload to the context's actions array.

        Parameters
        ----------
        action_repr : Union[List[Action], Action]
            The tasks to add
        """
        # Do not add further actions after `continue_as_new` has been
        # called
        if self.will_continue_as_new:
            return

        if self._replay_schema is ReplaySchema.V1 and isinstance(action_repr, list):
            self._action_payload_v1.append(action_repr)
        elif self._replay_schema is ReplaySchema.V2 and isinstance(action_repr, Action):
            self._action_payload_v2.append(action_repr)
        else:
            raise Exception(f"DF-internal exception: ActionRepr of signature {type(action_repr)}"
                            f"is not compatible on ReplaySchema {self._replay_schema.name}. ")

    def _pretty_print_history(self) -> str:
        """Get a pretty-printed version of the orchestration's internal history."""
        def history_to_string(event):
            json_dict = {}
            for key, val in inspect.getmembers(event):
                if not key.startswith('_') and not inspect.ismethod(val):
                    if isinstance(val, datetime.date):
                        val = val.replace(tzinfo=timezone.utc).timetuple()
                    json_dict[key] = val
            return json.dumps(json_dict)
        return str(list(map(history_to_string, self._histories)))

    def _add_to_open_tasks(self, task: TaskBase):

        if isinstance(task, AtomicTask):
            if task.id is None:
                task.id = self._sequence_number
                self._sequence_number += 1
                self.open_tasks[task.id] = task
            elif task.id != -1:
                self.open_tasks[task.id].append(task)

            if task.id in self.deferred_tasks:
                task_update_action = self.deferred_tasks[task.id]
                task_update_action()
        else:
            for child in task.children:
                self._add_to_open_tasks(child)
