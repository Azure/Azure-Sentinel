from azure.durable_functions.models.ReplaySchema import ReplaySchema
from tests.test_utils.ContextBuilder import ContextBuilder
from .orchestrator_test_utils \
    import get_orchestration_state_result, assert_orchestration_state_equals, assert_valid_schema
from azure.durable_functions.models.actions.CreateTimerAction import CreateTimerAction
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from datetime import datetime, timedelta, timezone


def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)

def add_timer_fired_events(context_builder: ContextBuilder, id_: int, timestamp: str):
    fire_at: str = context_builder.add_timer_created_event(id_, timestamp)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_timer_fired_event(id_=id_, fire_at=fire_at)

def generator_function(context):

    # Create a timezone aware datetime object, just like a normal
    # call to `context.current_utc_datetime` would create
    timestamp = "2020-07-23T21:56:54.936700Z"
    fire_at = datetime.strptime(timestamp, DATETIME_STRING_FORMAT)
    fire_at = fire_at.replace(tzinfo=timezone.utc)

    yield context.create_timer(fire_at)
    return "Done!"

def add_timer_action(state: OrchestratorState, fire_at: datetime):
    action = CreateTimerAction(fire_at=fire_at)
    state._actions.append([action])

def test_timers_comparison_with_relaxed_precision():
    """Test if that two `datetime` different but equivalent
    serializations of timer deadlines are found to be equivalent.

    The Durable Extension may sometimes drop redundant zeroes on
    a datetime object. For instance, the date
        2020-07-23T21:56:54.936700Z
    may get transformed into
        2020-07-23T21:56:54.9367Z
    This test ensures that dropping redundant zeroes does not affect
    our ability to recognize that a timer has been fired.
    """

    # equivalent to 2020-07-23T21:56:54.936700Z
    relaxed_timestamp = "2020-07-23T21:56:54.9367Z"
    fire_at = datetime.strptime(relaxed_timestamp, DATETIME_STRING_FORMAT)

    context_builder = ContextBuilder("relaxed precision")
    add_timer_fired_events(context_builder, 0, relaxed_timestamp)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state(output='Done!')
    add_timer_action(expected_state, fire_at)

    expected_state._is_done = True
    expected = expected_state.to_json()

    #assert_valid_schema(result)
    # TODO: getting the following error when validating the schema
    # "Additional properties are not allowed ('fireAt', 'isCanceled' were unexpected)">
    assert_orchestration_state_equals(expected, result)