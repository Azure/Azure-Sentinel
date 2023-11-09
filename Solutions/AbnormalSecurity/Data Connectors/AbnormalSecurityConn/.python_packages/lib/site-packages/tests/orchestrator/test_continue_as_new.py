from azure.durable_functions.models.ReplaySchema import ReplaySchema
from .orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallActivityAction \
    import CallActivityAction
from azure.durable_functions.models.actions.ContinueAsNewAction \
    import ContinueAsNewAction


def generator_function(context):
    yield context.call_activity("Hello", "Tokyo")
    context.continue_as_new("Cause I can")


def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)


def add_hello_action(state: OrchestratorState, input_: str):
    action = CallActivityAction(function_name='Hello', input_=input_)
    state.actions.append([action])


def add_continue_as_new_action(state: OrchestratorState, input_: str):
    action = ContinueAsNewAction(input_=input_)
    state.actions.append([action])
    state._is_done = True


def add_hello_completed_events(
        context_builder: ContextBuilder, id_: int, result: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result)


def test_initial_orchestration_state():
    context_builder = ContextBuilder('test_simple_function')

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_tokyo_state():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    add_continue_as_new_action(expected_state, 'Cause I can')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
