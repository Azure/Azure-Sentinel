from azure.durable_functions.models.actions.NoOpAction import NoOpAction
from azure.durable_functions.models.actions.CompoundAction import CompoundAction
from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from azure.durable_functions.models.actions.Action import Action
from azure.durable_functions.models.actions.WhenAnyAction import WhenAnyAction
from azure.durable_functions.models.actions.WhenAllAction import WhenAllAction

import enum
from typing import Any, List, Optional, Set, Type, Union


class TaskState(enum.Enum):
    """The possible states that a Task can be in."""

    RUNNING = 0
    SUCCEEDED = 1
    FAILED = 2


class TaskBase:
    """The base class of all Tasks.

    Contains shared logic that drives all of its sub-classes. Should never be
    instantiated on its own.
    """

    def __init__(self, id_: Union[int, str], actions: Union[List[Action], Action]):
        """Initialize the TaskBase.

        Parameters
        ----------
        id_ : int
            An ID for the task
        actions : List[Any]
            The list of DF actions representing this Task.
            Needed for reconstruction in the extension.
        """
        self.id: Union[int, str] = id_
        self.state = TaskState.RUNNING
        self.parent: Optional[CompoundTask] = None
        self._api_name: str

        api_action: Union[Action, Type[CompoundAction]]
        if isinstance(actions, list):
            if len(actions) == 1:
                api_action = actions[0]
            else:
                api_action = CompoundAction
        else:
            api_action = actions

        self._api_name = api_action.__class__.__name__

        self.result: Any = None
        self.action_repr: Union[List[Action], Action] = actions
        self.is_played = False

    def set_is_played(self, is_played: bool):
        """Set the is_played flag for the Task.

        Needed for updating the orchestrator's is_replaying flag.

        Parameters
        ----------
        is_played : bool
            Whether the latest event for this Task has been played before.
        """
        self.is_played = is_played

    def change_state(self, state: TaskState):
        """Transition a running Task to a terminal state: success or failure.

        Parameters
        ----------
        state : TaskState
            The terminal state to assign to this Task

        Raises
        ------
        Exception
            When the input state is RUNNING
        """
        if state is TaskState.RUNNING:
            raise Exception("Cannot change Task to the RUNNING state.")
        self.state = state

    def set_value(self, is_error: bool, value: Any):
        """Set the value of this Task: either an exception of a result.

        Parameters
        ----------
        is_error : bool
            Whether the value represents an exception of a result.
        value : Any
            The value of this Task

        Raises
        ------
        Exception
            When the Task failed but its value was not an Exception
        """
        new_state = self.state
        if is_error:
            if not isinstance(value, Exception):
                if not (isinstance(value, TaskBase) and isinstance(value.result, Exception)):
                    err_message = f"Task ID {self.id} failed but it's value was not an Exception"
                    raise Exception(err_message)
            new_state = TaskState.FAILED
        else:
            new_state = TaskState.SUCCEEDED
        self.change_state(new_state)
        self.result = value
        self.propagate()

    def propagate(self):
        """Notify parent Task of this Task's state change."""
        has_completed = not (self.state is TaskState.RUNNING)
        has_parent = not (self.parent is None)
        if has_completed and has_parent:
            self.parent.handle_completion(self)


class CompoundTask(TaskBase):
    """A Task of Tasks.

    Contains shared logic that drives all of its sub-classes.
    Should never be instantiated on its own.
    """

    def __init__(self, tasks: List[TaskBase], compound_action_constructor=None):
        """Instantiate CompoundTask attributes.

        Parameters
        ----------
        tasks : List[Task]
            The children/sub-tasks of this Task
        compound_action_constructor : Union[WhenAllAction, WhenAnyAction, None]
            Either None or, a WhenAllAction or WhenAnyAction constructor.
            It is None when using the V1 replay protocol, where no Compound Action
            objects size and compound actions are represented as arrays of actions.
            It is not None when using the V2 replay protocol.
        """
        super().__init__(-1, [])
        child_actions = []
        for task in tasks:
            task.parent = self
            action_repr = task.action_repr
            if isinstance(action_repr, list):
                child_actions.extend(action_repr)
            else:
                child_actions.append(action_repr)
        if compound_action_constructor is None:
            self.action_repr = child_actions
        else:  # replay_schema is ReplaySchema.V2
            self.action_repr = compound_action_constructor(child_actions)
        self._first_error: Optional[Exception] = None
        self.pending_tasks: Set[TaskBase] = set(tasks)
        self.completed_tasks: List[TaskBase] = []
        self.children = tasks

    def handle_completion(self, child: TaskBase):
        """Manage sub-task completion events.

        Parameters
        ----------
        child : TaskBase
            The sub-task that completed

        Raises
        ------
        Exception
            When the calling sub-task was not registered
            with this Task's pending sub-tasks.
        """
        try:
            self.pending_tasks.remove(child)
        except KeyError:
            raise Exception(
                f"Parent Task {self.id} does not have pending sub-task with ID {child.id}."
                f"This most likely means that Task {child.id} completed twice.")

        self.completed_tasks.append(child)
        self.set_is_played(child.is_played)
        self.try_set_value(child)

    def try_set_value(self, child: TaskBase):
        """Transition a CompoundTask to a terminal state and set its value.

        Should be implemented by sub-classes.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by each subclass.
        """
        raise NotImplementedError


class AtomicTask(TaskBase):
    """A Task with no subtasks."""

    pass


class WhenAllTask(CompoundTask):
    """A Task representing `when_all` scenarios."""

    def __init__(self, task: List[TaskBase], replay_schema: ReplaySchema):
        """Initialize a WhenAllTask.

        Parameters
        ----------
        task : List[Task]
            The list of child tasks
        replay_schema : ReplaySchema
            The ReplaySchema, which determines the inner action payload representation
        """
        compound_action_constructor = None
        if replay_schema is ReplaySchema.V2:
            compound_action_constructor = WhenAllAction
        super().__init__(task, compound_action_constructor)

    def try_set_value(self, child: TaskBase):
        """Transition a WhenAll Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if child.state is TaskState.SUCCEEDED:
            # A WhenAll Task only completes when it has no pending tasks
            # i.e _when all_ of its children have completed
            if len(self.pending_tasks) == 0:
                results = list(map(lambda x: x.result, self.completed_tasks))
                self.set_value(is_error=False, value=results)
        else:  # child.state is TaskState.FAILED:
            # a single error is sufficient to fail this task
            if self._first_error is None:
                self._first_error = child.result
                self.set_value(is_error=True, value=self._first_error)


class WhenAnyTask(CompoundTask):
    """A Task representing `when_any` scenarios."""

    def __init__(self, task: List[TaskBase], replay_schema: ReplaySchema):
        """Initialize a WhenAnyTask.

        Parameters
        ----------
        task : List[Task]
            The list of child tasks
        replay_schema : ReplaySchema
            The ReplaySchema, which determines the inner action payload representation
        """
        compound_action_constructor = None
        if replay_schema is ReplaySchema.V2:
            compound_action_constructor = WhenAnyAction
        super().__init__(task, compound_action_constructor)

    def try_set_value(self, child: TaskBase):
        """Transition a WhenAny Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if self.state is TaskState.RUNNING:
            self.set_value(is_error=False, value=child)


class RetryAbleTask(WhenAllTask):
    """A Task representing `with_retry` scenarios.

    It inherits from WhenAllTask because retryable scenarios are Tasks
    with equivalent to WhenAll Tasks with dynamically increasing lists
    of children. At every failure, we add a Timer child and a Task child
    to the list of pending tasks.
    """

    def __init__(self, child: TaskBase, retry_options: RetryOptions, context):
        self.id_ = str(child.id) + "_retryable_proxy"
        tasks = [child]
        super().__init__(tasks, context._replay_schema)

        self.retry_options = retry_options
        self.num_attempts = 1
        self.context = context
        self.actions = child.action_repr

    def try_set_value(self, child: TaskBase):
        """Transition a Retryable Task to a terminal state and set its value.

        Parameters
        ----------
        child : TaskBase
            A sub-task that just completed
        """
        if child.state is TaskState.SUCCEEDED:
            if len(self.pending_tasks) == 0:
                # if all pending tasks have completed,
                # and we have a successful child, then
                # we can set the Task's event
                self.set_value(is_error=False, value=child.result)

        else:  # child.state is TaskState.FAILED:
            if self.num_attempts >= self.retry_options.max_number_of_attempts:
                # we have reached the maximum number of attempts, set error
                self.set_value(is_error=True, value=child.result)
            else:
                # still have some retries left.
                # increase size of pending tasks by adding a timer task
                # and then re-scheduling the current task after that
                timer_task = self.context._generate_task(action=NoOpAction(), parent=self)
                self.pending_tasks.add(timer_task)
                self.context._add_to_open_tasks(timer_task)
                rescheduled_task = self.context._generate_task(action=NoOpAction(), parent=self)
                self.pending_tasks.add(rescheduled_task)
                self.context._add_to_open_tasks(rescheduled_task)
            self.num_attempts += 1
