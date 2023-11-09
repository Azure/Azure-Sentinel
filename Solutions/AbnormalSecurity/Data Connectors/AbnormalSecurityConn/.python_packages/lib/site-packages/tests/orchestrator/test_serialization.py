from azure.durable_functions.models.ReplaySchema import ReplaySchema
from tests.test_utils.ContextBuilder import ContextBuilder
from .orchestrator_test_utils \
    import get_orchestration_state_result, assert_orchestration_state_equals, assert_valid_schema
from azure.durable_functions.models.OrchestratorState import OrchestratorState

def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)

def generator_function(context):
    return False

def test_serialization_of_False():
    """Test that an orchestrator can return False."""

    context_builder = ContextBuilder("serialize False")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state(output=False)

    expected_state._is_done = True
    expected = expected_state.to_json()

    # Since we're essentially testing the `to_json` functionality,
    # we explicitely ensure that the output is set
    expected["output"] = False

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)