from tests.test_utils.ContextBuilder import ContextBuilder
from tests.test_utils.testClasses import SerializableClass
from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from .orchestrator_test_utils import get_orchestration_state_result
from typing import List, Tuple
from datetime import datetime

RETRY_OPTIONS = RetryOptions(5000, 2)
REASONS = "Stuff"
DETAILS = "Things"
RESULT_PREFIX = "Hello "
CITIES = ["Tokyo", "Seattle", "London"]

def generator_function(context: DurableOrchestrationContext):
    """Orchestrator function for testing retry'ing semantics

    Parameters
    ----------
    context: DurableOrchestrationContext
        Durable orchestration context, exposes the Durable API

    Returns
    -------
    List[str]:
        Output of activities, a list of hello'd cities
    """

    outputs = []

    retry_options = RETRY_OPTIONS
    task1 = yield context.call_activity_with_retry(
        "Hello", retry_options, "Tokyo")
    task2 = yield context.call_activity_with_retry(
        "Hello",  retry_options, "Seattle")
    task3 = yield context.call_activity_with_retry(
        "Hello",  retry_options, "London")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs


def generator_function_with_serialization(context: DurableOrchestrationContext):
    """Orchestrator function for testing retry'ing with serializable input arguments.

    Parameters
    ----------
    context: DurableOrchestrationContext
        Durable orchestration context, exposes the Durable API

    Returns
    -------
    List[str]:
        Output of activities, a list of hello'd cities
    """

    outputs = []

    retry_options = RETRY_OPTIONS
    task1 = yield context.call_activity_with_retry(
        "Hello", retry_options, SerializableClass("Tokyo"))
    task2 = yield context.call_activity_with_retry(
        "Hello",  retry_options, SerializableClass("Seatlle"))
    task3 = yield context.call_activity_with_retry(
        "Hello",  retry_options, SerializableClass("London"))

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs


def get_context_with_retries_and_corrupted_completion() -> ContextBuilder:
    """Get a ContextBuilder whose history contains a late completion event
    for an event that already failed.

    Returns
    -------
    ContextBuilder:
        The context whose history contains the requested event sequence.
    """
    context = get_context_with_retries()
    context.add_orchestrator_started_event()
    context.add_task_completed_event(id_=0, result="'Do not pick me up'")
    context.add_orchestrator_completed_event()
    return context

def get_context_with_retries(will_fail: bool=False) -> ContextBuilder:
    """Get a ContextBuilder whose history contains retried events.

    Parameters
    ----------
    will_fail: (bool, optional)
        If set to true, returns a context with a history where the orchestrator fails.
        If false, returns a context with a history where events fail but eventually complete.
        Defaults to False.

    Returns
    -------
    ContextBuilder:
        The context whose history contains the requested event sequence.
    """
    context = ContextBuilder()
    num_activities = len(CITIES)

    def _schedule_events(context: ContextBuilder, id_counter: int) -> Tuple[ContextBuilder, int, List[int]]:
        """Add scheduled events to the context.

        Parameters
        ----------
        context: ContextBuilder
            Orchestration context mock, to which we'll add the event completion events
        id_counter: int
            The current event counter

        Returns
        -------
        Tuple[ContextBuilder, int, List[int]]:
            The updated context, the updated counter, a list of event IDs for each scheduled event
        """
        id_counter = id_counter + 1
        context.add_task_scheduled_event(name='Hello', id_=id_counter)
        return context, id_counter

    def _fail_events(context: ContextBuilder, id_counter: int) -> Tuple[ContextBuilder, int]:
        """Add event failed to the context.

        Parameters
        ----------
        context: ContextBuilder
            Orchestration context mock, to which we'll add the event completion events
        id_counter: int
            The current event counter

        Returns
        -------
        Tuple[ContextBuilder, int]:
            The updated context, the updated id_counter
        """
        context.add_orchestrator_started_event()
        context.add_task_failed_event(
            id_=id_counter, reason=REASONS, details=DETAILS)
        return context, id_counter

    def _schedule_timers(context: ContextBuilder, id_counter: int) -> Tuple[ContextBuilder, int, List[datetime]]:
        """Add timer created events to the context.

        Parameters
        ----------
        context: ContextBuilder
            Orchestration context mock, to which we'll add the event completion events
        id_counter: int
            The current event counter

        Returns
        -------
        Tuple[ContextBuilder, int, List[datetime]]:
            The updated context, the updated counter, a list of timer deadlines
        """
        id_counter = id_counter + 1
        deadlines: List[datetime] = []
        deadlines.append((id_counter, context.add_timer_created_event(id_counter)))
        return context, id_counter, deadlines
    
    def _fire_timer(context: ContextBuilder, id_counter: int, deadlines: List[datetime]) -> Tuple[ContextBuilder, int]:
        """Add timer fired events to the context.

        Parameters
        ----------
        context: ContextBuilder
            Orchestration context mock, to which we'll add the event completion events
        id_counter: int
            The current event counter
        deadlines: List[datetime]
            List of dates at which to fire the timers

        Returns
        -------
        Tuple[ContextBuilder, int]:
            The updated context, the updated id_counter
        """
        for id_, fire_at in deadlines:
            context.add_timer_fired_event(id_=id_, fire_at=fire_at)
        return context, id_counter

    def _complete_event(context: ContextBuilder, id_counter: int, city:str) -> Tuple[ContextBuilder, int]:
        """Add event / task completions to the context.

        Parameters
        ----------
        context: ContextBuilder
            Orchestration context mock, to which we'll add the event completion events
        id_counter: int
            The current event counter

        Returns
        -------
        Tuple[ContextBuilder, int]
            The updated context, the updated id_counter
        """
        result = f"\"{RESULT_PREFIX}{city}\""
        context.add_task_completed_event(id_=id_counter, result=result)
        return context, id_counter


    id_counter = -1

    for city in CITIES:
        # Schedule the events
        context, id_counter = _schedule_events(context, id_counter)
        context.add_orchestrator_completed_event()

        # Record failures, schedule timers
        context, id_counter = _fail_events(context, id_counter)
        context, id_counter, deadlines = _schedule_timers(context, id_counter)
        context.add_orchestrator_completed_event()

        # Fire timers, re-schedule events
        context.add_orchestrator_started_event()
        context, id_counter = _fire_timer(context, id_counter, deadlines)
        context, id_counter = _schedule_events(context, id_counter)
        context.add_orchestrator_completed_event()

        context.add_orchestrator_started_event()

        # Either complete the event or, if we want all failed events, then
        # fail the events, schedule timer, and fire time.
        if will_fail:
            context, id_counter = _fail_events(context, id_counter)
            context, id_counter, deadlines = _schedule_timers(context, id_counter)
            context.add_orchestrator_completed_event()

            context.add_orchestrator_started_event()
            context, id_counter = _fire_timer(context, id_counter, deadlines)
        else:
            context, id_counter = _complete_event(context, id_counter, city)

        context.add_orchestrator_completed_event()
    return context

def test_redundant_completion_doesnt_get_processed():
    """Tests that our implementation processes the state array
    sequentially, which previous implementations did not guarantee. In this test,
    we add a completion event for a task that was cancelled, meaning that it failed and got
    re-scheduled. Older implementations would pick up this completion event and cause
    non-determinism.
    """
    context_1 = get_context_with_retries()
    context_2 = get_context_with_retries_and_corrupted_completion()

    result_1 = get_orchestration_state_result(
        context_1, generator_function)

    result_2 = get_orchestration_state_result(
        context_2, generator_function)

    assert "output" in result_1
    assert "output" in result_2
    assert result_1["output"] == result_2["output"]


def test_failed_tasks_do_not_hang_orchestrator():
    """Tests that our implementation correctly handles up re-scheduled events,
    which previous implementations failed to correctly handle. """
    context = get_context_with_retries()

    result = get_orchestration_state_result(
        context, generator_function)

    expected_output = list(map(lambda x: RESULT_PREFIX + x, CITIES))
    assert "output" in result
    assert result["output"] == expected_output

def test_retries_can_fail():
    """Tests the code path where a retry'ed Task fails"""
    context = get_context_with_retries(will_fail=True)

    try:
        result = get_orchestration_state_result(
            context, generator_function)
        # We expected an exception
        assert False
    except Exception as e:
        error_label = "\n\n$OutOfProcData$:"
        error_str = str(e)

        error_msg = f"{REASONS} \n {DETAILS}"
        
        expected_error_str = f"{error_msg}{error_label}"
        assert str.startswith(error_str, expected_error_str)

def test_retries_with_serializable_input():
    # Tests that retried tasks work with serialized input classes.
    context = get_context_with_retries()

    result_1 = get_orchestration_state_result(
        context, generator_function)

    result_2 = get_orchestration_state_result(
        context, generator_function_with_serialization)

    assert "output" in result_1
    assert "output" in result_2
    assert result_1["output"] == result_2["output"]