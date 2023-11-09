from azure.durable_functions.models.ReplaySchema import ReplaySchema
from tests.test_utils.ContextBuilder import ContextBuilder
from .orchestrator_test_utils \
    import get_orchestration_property, assert_orchestration_state_equals, assert_valid_schema
from azure.durable_functions.models.actions.CreateTimerAction import CreateTimerAction
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from datetime import datetime, timedelta, timezone

def generator_function(context):
    # Create a timezone aware datetime object, just like a normal
    # call to `context.current_utc_datetime` would create
    timestamp = "2020-07-23T21:56:54.936700Z"
    deadline = datetime.strptime(timestamp, DATETIME_STRING_FORMAT)
    deadline = deadline.replace(tzinfo=timezone.utc)

    for _ in range(0, 3):
        deadline = deadline + timedelta(seconds=30)
        yield context.create_timer(deadline)

def generator_function_compound_task(context):
    # Create a timezone aware datetime object, just like a normal
    # call to `context.current_utc_datetime` would create
    timestamp = "2020-07-23T21:56:54.936700Z"
    deadline = datetime.strptime(timestamp, DATETIME_STRING_FORMAT)
    deadline = deadline.replace(tzinfo=timezone.utc)

    tasks = []
    for _ in range(0, 3):
        deadline = deadline + timedelta(seconds=30)
        tasks.append(context.create_timer(deadline))
    yield context.task_any(tasks)

def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)

def add_timer_fired_events(context_builder: ContextBuilder, id_: int, timestamp: str,
        is_played: bool = True):
    fire_at: str = context_builder.add_timer_created_event(id_, timestamp)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_timer_fired_event(id_=id_, fire_at=fire_at, is_played=is_played)

def add_timer_action(state: OrchestratorState, fire_at: datetime):
    action = CreateTimerAction(fire_at=fire_at)
    state._actions.append([action])

def test_is_replaying_initial_value():

    context_builder = ContextBuilder("")
    result = get_orchestration_property(
        context_builder, generator_function, "durable_context")

    assert result.is_replaying == False

def test_is_replaying_one_replayed_event():

    timestamp = "2020-07-23T21:56:54.9367Z"
    fire_at = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=30)
    fire_at_str = fire_at.strftime(DATETIME_STRING_FORMAT)

    context_builder = ContextBuilder("")
    add_timer_fired_events(context_builder, 0, fire_at_str, is_played=True)

    result = get_orchestration_property(
        context_builder, generator_function, "durable_context")

    assert result.is_replaying == True

def test_is_replaying_one_replayed_one_not():

    timestamp = "2020-07-23T21:56:54.9367Z"
    fire_at = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=30)
    fire_at_str = fire_at.strftime(DATETIME_STRING_FORMAT)
    fire_at2 = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=60)
    fire_at_str2 = fire_at2.strftime(DATETIME_STRING_FORMAT)

    context_builder = ContextBuilder("")
    add_timer_fired_events(context_builder, 0, fire_at_str, is_played=True)
    add_timer_fired_events(context_builder, 1, fire_at_str2, is_played=False)


    result = get_orchestration_property(
        context_builder, generator_function, "durable_context")

    assert result.is_replaying == False

def test_is_replaying_propagates_in_compound_task():

    timestamp = "2020-07-23T21:56:54.9367Z"
    fire_at = datetime.strptime(timestamp, DATETIME_STRING_FORMAT) + timedelta(seconds=30)
    fire_at_str = fire_at.strftime(DATETIME_STRING_FORMAT)

    context_builder = ContextBuilder("")
    add_timer_fired_events(context_builder, 0, fire_at_str, is_played=True)

    result = get_orchestration_property(
        context_builder, generator_function_compound_task, "durable_context")

    assert result.is_replaying == True

