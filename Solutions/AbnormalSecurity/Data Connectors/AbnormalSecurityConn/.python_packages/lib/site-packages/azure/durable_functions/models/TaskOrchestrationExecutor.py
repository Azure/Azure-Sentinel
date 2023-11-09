from azure.durable_functions.models.Task import TaskBase, TaskState, AtomicTask
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from typing import Any, List, Optional, Union
from azure.durable_functions.models.history.HistoryEventType import HistoryEventType
from azure.durable_functions.models.history.HistoryEvent import HistoryEvent
from types import GeneratorType
import warnings
from collections import namedtuple
import json
from ..models.entities.ResponseMessage import ResponseMessage
from azure.functions._durable_functions import _deserialize_custom_object


class TaskOrchestrationExecutor:
    """Manages the execution and replay of user-defined orchestrations."""

    def __init__(self):
        """Initialize TaskOrchestrationExecutor."""
        # A mapping of event types to a tuple of
        #   (1) whether the event type represents a task success
        #   (2) the attribute in the corresponding event object that identifies the Task
        # this mapping is used for processing events that transition a Task from its running state
        # to a terminal one
        SetTaskValuePayload = namedtuple("SetTaskValuePayload", ("is_success", "task_id_key"))
        self.event_to_SetTaskValuePayload = dict([
            (HistoryEventType.TASK_COMPLETED, SetTaskValuePayload(True, "TaskScheduledId")),
            (HistoryEventType.TIMER_FIRED, SetTaskValuePayload(True, "TimerId")),
            (HistoryEventType.SUB_ORCHESTRATION_INSTANCE_COMPLETED,
             SetTaskValuePayload(True, "TaskScheduledId")),
            (HistoryEventType.EVENT_RAISED, SetTaskValuePayload(True, "Name")),
            (HistoryEventType.TASK_FAILED, SetTaskValuePayload(False, "TaskScheduledId")),
            (HistoryEventType.SUB_ORCHESTRATION_INSTANCE_FAILED,
             SetTaskValuePayload(False, "TaskScheduledId"))
        ])
        self.task_completion_events = set(self.event_to_SetTaskValuePayload.keys())
        self.initialize()

    def initialize(self):
        """Initialize the TaskOrchestrationExecutor for a new orchestration invocation."""
        # The first task is just a placeholder to kickstart the generator.
        # So it's value is `None`.
        self.current_task: TaskBase = AtomicTask(-1, [])
        self.current_task.set_value(is_error=False, value=None)

        self.output: Any = None
        self.exception: Optional[Exception] = None
        self.orchestrator_returned: bool = False

    def execute(self, context: DurableOrchestrationContext,
                history: List[HistoryEvent], fn) -> str:
        """Execute an orchestration using the orchestration history to evaluate Tasks and replay events.

        Parameters
        ----------
        context : DurableOrchestrationContext
            The user's orchestration context, to interact with the user code.
        history : List[HistoryEvent]
            The orchestration history, to evaluate tasks and replay events.
        fn : function
            The user's orchestration function.

        Returns
        -------
        str
            A JSON-formatted string of the user's orchestration state, payload for the extension.
        """
        self.context = context
        evaluated_user_code = fn(context)

        # If user code is a generator, then it uses `yield` statements (the DF API)
        # and so we iterate through the DF history, generating tasks and populating
        # them with values when the history provides them
        if isinstance(evaluated_user_code, GeneratorType):
            self.generator = evaluated_user_code
            for event in history:
                self.process_event(event)
                if self.has_execution_completed:
                    break

        # Due to backwards compatibility reasons, it's possible
        # for the `continue_as_new` API to be called without `yield` statements.
        # Therefore, we explicitely check if `continue_as_new` was used before
        # flatting the orchestration as returned/completed
        elif not self.context.will_continue_as_new:
            self.orchestrator_returned = True
            self.output = evaluated_user_code
        return self.get_orchestrator_state_str()

    def process_event(self, event: HistoryEvent):
        """Evaluate a history event.

        This might result in updating some orchestration internal state deterministically,
        to evaluating some Task, or have no side-effects.

        Parameters
        ----------
        event : HistoryEvent
            The history event to process
        """
        event_type = event.event_type
        if event_type == HistoryEventType.ORCHESTRATOR_STARTED:
            # update orchestration's deterministic timestamp
            timestamp = event.timestamp
            if timestamp > self.context.current_utc_datetime:
                self.context.current_utc_datetime = event.timestamp
        elif event.event_type == HistoryEventType.CONTINUE_AS_NEW:
            # re-initialize the orchestration state
            self.initialize()
        elif event_type == HistoryEventType.EXECUTION_STARTED:
            # begin replaying user code
            self.resume_user_code()
        elif event_type == HistoryEventType.EVENT_SENT:
            # we want to differentiate between a "proper" event sent, and a signal/call entity
            key = getattr(event, "event_id")
            if key in self.context.open_tasks.keys():
                task = self.context.open_tasks[key]
                if task._api_name == "CallEntityAction":
                    # in the signal entity case, the Task is represented
                    # with a GUID, not with a sequential integer
                    self.context.open_tasks.pop(key)
                    event_id = json.loads(event.Input)["id"]
                    self.context.open_tasks[event_id] = task

        elif self.is_task_completion_event(event.event_type):
            # transition a task to a success or failure state
            (is_success, id_key) = self.event_to_SetTaskValuePayload[event_type]
            self.set_task_value(event, is_success, id_key)
            self.resume_user_code()

    def set_task_value(self, event: HistoryEvent, is_success: bool, id_key: str):
        """Set a running task to either a success or failed state, and sets its value.

        Parameters
        ----------
        event : HistoryEvent
            The history event containing the value for the Task
        is_success : bool
            Whether the Task succeeded or failed (throws exception)
        id_key : str
            The attribute in the event object containing the ID of the Task to target
        """

        def parse_history_event(directive_result):
            """Based on the type of event, parse the JSON.serializable portion of the event."""
            event_type = directive_result.event_type
            if event_type is None:
                raise ValueError("EventType is not found in task object")

            # We provide the ability to deserialize custom objects, because the output of this
            # will be passed directly to the orchestrator as the output of some activity
            if event_type == HistoryEventType.SUB_ORCHESTRATION_INSTANCE_COMPLETED:
                return json.loads(directive_result.Result, object_hook=_deserialize_custom_object)
            if event_type == HistoryEventType.TASK_COMPLETED:
                return json.loads(directive_result.Result, object_hook=_deserialize_custom_object)
            if event_type == HistoryEventType.EVENT_RAISED:
                # TODO: Investigate why the payload is in "Input" instead of "Result"
                response = json.loads(directive_result.Input,
                                      object_hook=_deserialize_custom_object)
                return response
            return None

        # get target task
        key = getattr(event, id_key)
        try:
            task: Union[TaskBase, List[TaskBase]] = self.context.open_tasks.pop(key)
            if isinstance(task, list):
                task_list = task
                task = task_list.pop()
                if len(task_list) > 0:
                    self.context.open_tasks[key] = task_list
        except KeyError:
            warning = f"Potential duplicate Task completion for TaskId: {key}"
            warnings.warn(warning)
            self.context.deferred_tasks[key] = lambda: self.set_task_value(
                event, is_success, id_key)
            return

        if is_success:
            # retrieve result
            new_value = parse_history_event(event)
            if task._api_name == "CallEntityAction":
                new_value = ResponseMessage.from_dict(new_value)
                new_value = json.loads(new_value.result)
        else:
            # generate exception
            new_value = Exception(f"{event.Reason} \n {event.Details}")

        # with a yielded task now evaluated, we can try to resume the user code
        task.set_is_played(event._is_played)
        task.set_value(is_error=not(is_success), value=new_value)

    def resume_user_code(self):
        """Attempt to continue executing user code.

        We can only continue executing if the active/current task has resolved to a value.
        """
        current_task = self.current_task
        self.context._set_is_replaying(current_task.is_played)
        if current_task.state is TaskState.RUNNING:
            # if the current task hasn't been resolved, we can't
            # continue executing the user code.
            return

        new_task = None
        try:
            # resume orchestration with a resolved task's value
            task_value = current_task.result
            task_succeeded = current_task.state is TaskState.SUCCEEDED
            new_task = self.generator.send(
                task_value) if task_succeeded else self.generator.throw(task_value)
            self.context._add_to_open_tasks(new_task)
        except StopIteration as stop_exception:
            # the orchestration returned,
            # flag it as such and capture its output
            self.orchestrator_returned = True
            self.output = stop_exception.value
        except Exception as exception:
            # the orchestration threw an exception
            self.exception = exception

        self.current_task = new_task
        if not (new_task is None):
            if not (new_task.state is TaskState.RUNNING):
                # user yielded the same task multiple times, continue executing code
                # until a new/not-previously-yielded task is encountered
                self.resume_user_code()
            else:
                # new task is received. it needs to be resolved to a value
                self.context._add_to_actions(self.current_task.action_repr)

    def get_orchestrator_state_str(self) -> str:
        """Obtain a JSON-formatted string representing the orchestration's state.

        Returns
        -------
        str
            String represented orchestration's state, payload to the extension

        Raises
        ------
        Exception
            When the orchestration's state represents an error. The exception's
            message contains in it the string representation of the orchestration's
            state
        """
        state = OrchestratorState(
            is_done=self.orchestration_invocation_succeeded,
            actions=self.context._actions,
            output=self.output,
            replay_schema=self.context._replay_schema,
            error=None if self.exception is None else str(self.exception),
            custom_status=self.context.custom_status
        )

        if self.exception is not None:
            # Create formatted error, using out-of-proc error schema
            error_label = "\n\n$OutOfProcData$:"
            state_str = state.to_json_string()
            formatted_error = f"{self.exception}{error_label}{state_str}"

            # Raise exception, re-set stack to original location
            raise Exception(formatted_error) from self.exception
        return state.to_json_string()

    def is_task_completion_event(self, event_type: HistoryEventType) -> bool:
        """Determine if some event_type corresponds to a Task-resolution event.

        Parameters
        ----------
        event_type : HistoryEventType
            The event_type to analyze.

        Returns
        -------
        bool
            True if the event corresponds to a Task being resolved. False otherwise.
        """
        return event_type in self.task_completion_events

    @property
    def has_execution_completed(self) -> bool:
        """Determine if the orchestration invocation is completed.

        An orchestration can complete either by returning,
        continuing-as-new, or through an exception.

        Returns
        -------
        bool
            Whether the orchestration invocation is completed.
        """
        return self.orchestration_invocation_succeeded or not(self.exception is None)

    @property
    def orchestration_invocation_succeeded(self) -> bool:
        """Whether the orchestration returned or continued-as-new.

        Returns
        -------
        bool
            Whether the orchestration returned or continued-as-new
        """
        return self.orchestrator_returned or self.context.will_continue_as_new
