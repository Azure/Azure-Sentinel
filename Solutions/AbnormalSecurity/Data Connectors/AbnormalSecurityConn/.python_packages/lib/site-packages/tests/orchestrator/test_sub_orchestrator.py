from azure.durable_functions.models.ReplaySchema import ReplaySchema
from .orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallSubOrchestratorAction \
    import CallSubOrchestratorAction


def generator_function(context):
    outputs = []
    task1 = yield context.call_sub_orchestrator("HelloSubOrchestrator", "Tokyo")
    task2 = yield context.call_sub_orchestrator("HelloSubOrchestrator", "Seattle")
    task3 = yield context.call_sub_orchestrator("HelloSubOrchestrator", "London")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs

def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)


def add_hello_suborch_action(state: OrchestratorState, input_: str):
    action = CallSubOrchestratorAction(function_name='HelloSubOrchestrator', _input=input_)
    state.actions.append([action])


def add_hello_suborch_completed_events(
        context_builder: ContextBuilder, id_: int, result: str):
    context_builder.add_sub_orchestrator_started_event(name="HelloSubOrchestrator", id_=id_,input_="")
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_sub_orchestrator_completed_event(result=result, id_=id_)

def test_tokyo_and_seattle_and_london_state():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_suborch_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_suborch_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_suborch_completed_events(context_builder, 2, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state(
        ['Hello Tokyo!', 'Hello Seattle!', 'Hello London!'])
    add_hello_suborch_action(expected_state, 'Tokyo')
    add_hello_suborch_action(expected_state, 'Seattle')
    add_hello_suborch_action(expected_state, 'London')
    expected_state._is_done = True
    expected = expected_state.to_json()

    #assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
