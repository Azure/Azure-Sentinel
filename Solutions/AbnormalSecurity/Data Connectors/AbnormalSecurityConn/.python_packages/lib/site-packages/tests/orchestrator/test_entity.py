from azure.durable_functions.models.ReplaySchema import ReplaySchema
from .orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result, assert_valid_schema, \
            get_entity_state_result, assert_entity_state_equals
from tests.test_utils.ContextBuilder import ContextBuilder
from tests.test_utils.EntityContextBuilder import EntityContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.entities.EntityState import EntityState, OperationResult
from azure.durable_functions.models.actions.CallEntityAction \
    import CallEntityAction
from azure.durable_functions.models.actions.SignalEntityAction \
    import SignalEntityAction
from tests.test_utils.testClasses import SerializableClass
import azure.durable_functions as df
from typing import Any, Dict, List
import json

def generator_function_call_entity(context):
    outputs = []
    entityId = df.EntityId("Counter", "myCounter")
    x = yield context.call_entity(entityId, "add", 3)
    
    outputs.append(x)
    return outputs

def generator_function_signal_entity(context):
    outputs = []
    entityId = df.EntityId("Counter", "myCounter")
    context.signal_entity(entityId, "add", 3)
    x = yield context.call_entity(entityId, "get")
    
    outputs.append(x)
    return outputs

def counter_entity_function(context):
    """A Counter Durable Entity.

    A simple example of a Durable Entity that implements
    a simple counter.
    """

    current_value = context.get_state(lambda: 0)
    operation = context.operation_name
    if operation == "add":
        amount = context.get_input()
        current_value += amount
    elif operation == "reset":
        current_value = 0
    elif operation == "get":
        pass

    result = f"The state is now: {current_value}"
    context.set_state(current_value)
    context.set_result(result)


def test_entity_signal_then_call():
    """Tests that a simple counter entity outputs the correct value
    after a sequence of operations. Mostly just a sanity check.
    """

    # Create input batch
    batch = []
    add_to_batch(batch, name="add", input_=3)
    add_to_batch(batch, name="get")
    context_builder = EntityContextBuilder(batch=batch)

    # Run the entity, get observed result
    result = get_entity_state_result(
        context_builder,
        counter_entity_function,
        )

    # Construct expected result
    expected_state = entity_base_expected_state()
    apply_operation(expected_state, result="The state is now: 3", state=3)
    expected = expected_state.to_json()

    # Ensure expectation matches observed behavior
    #assert_valid_schema(result)
    assert_entity_state_equals(expected, result)


def apply_operation(entity_state: EntityState, result: Any, state: Any, is_error: bool = False):
    """Apply the effects of an operation to the expected entity state object

    Parameters
    ----------
    entity_state: EntityState
        The expected entity state object
    result: Any
        The result of the latest operation
    state: Any
        The state right after the latest operation
    is_error: bool
        Whether or not the operation resulted in an exception. Defaults to False
    """
    entity_state.state = state

    # We cannot control duration, so default it to zero and avoid checking for it
    # in later asserts
    duration = 0
    operation_result = OperationResult(
        is_error=is_error,
        duration=duration,
        result=result
    )
    entity_state._results.append(operation_result)

def add_to_batch(batch: List[Dict[str, Any]], name: str, input_: Any=None):
    """Add new work item to the batch of entity operations.

    Parameters
    ----------
    batch: List[Dict[str, Any]]
        Current list of json-serialized entity work items
    name: str
        Name of the entity operation to be performed
    input_: Optional[Any]:
        Input to the operation. Defaults to None.

    Returns
    --------
    List[Dict[str, str]]:
        Batch of json-serialized entity work items
    """
    # It is key to serialize the input twice, as this is
    # the extension behavior
    packet = {
        "name": name,
        "input": json.dumps(json.dumps(input_))
    }
    batch.append(packet)
    return batch


def entity_base_expected_state() -> EntityState:
    """Get a base entity state.

    Returns
    -------
    EntityState:
        An EntityState with no results, no signals, a None state, and entity_exists set to True.
    """
    return EntityState(results=[], signals=[], entity_exists=True, state=None)

def add_call_entity_action_for_entity(state: OrchestratorState, id_: df.EntityId, op: str, input_: Any):
    action = CallEntityAction(entity_id=id_, operation=op, input_=input_)
    state.actions.append([action])


def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)

def add_call_entity_action(state: OrchestratorState, id_: df.EntityId, op: str, input_: Any):
    action = CallEntityAction(entity_id=id_, operation=op, input_=input_)
    state.actions.append([action])

def add_signal_entity_action(state: OrchestratorState, id_: df.EntityId, op: str, input_: Any):
    action = SignalEntityAction(entity_id=id_, operation=op, input_=input_)
    state.actions.append([action])

def add_call_entity_completed_events(
        context_builder: ContextBuilder, op: str, instance_id=str, input_=None, event_id=0):
    context_builder.add_event_sent_event(instance_id, event_id)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_event_raised_event(name="0000", id_=0, input_=input_, is_entity=True)

def test_call_entity_sent():
    context_builder = ContextBuilder('test_simple_function')

    entityId = df.EntityId("Counter", "myCounter")
    result = get_orchestration_state_result(
        context_builder, generator_function_call_entity)

    expected_state = base_expected_state()
    add_call_entity_action(expected_state, entityId, "add", 3)
    expected = expected_state.to_json()

    #assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
    
def test_signal_entity_sent():
    context_builder = ContextBuilder('test_simple_function')

    entityId = df.EntityId("Counter", "myCounter")
    result = get_orchestration_state_result(
        context_builder, generator_function_signal_entity)

    expected_state = base_expected_state()
    add_signal_entity_action(expected_state, entityId, "add", 3)
    add_call_entity_action(expected_state, entityId, "get", None)
    expected = expected_state.to_json()

    #assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_signal_entity_sent_and_response_received():
    entityId = df.EntityId("Counter", "myCounter")
    context_builder = ContextBuilder('test_simple_function')
    add_call_entity_completed_events(context_builder, "get", df.EntityId.get_scheduler_id(entityId), 3, 1)


    result = get_orchestration_state_result(
        context_builder, generator_function_signal_entity)

    expected_state = base_expected_state([3])
    add_signal_entity_action(expected_state, entityId, "add", 3)
    add_call_entity_action(expected_state, entityId, "get", None)
    expected_state._is_done = True
    expected = expected_state.to_json()

    #assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_call_entity_raised():
    entityId = df.EntityId("Counter", "myCounter")
    context_builder = ContextBuilder('test_simple_function')
    add_call_entity_completed_events(context_builder, "add", df.EntityId.get_scheduler_id(entityId), 3, 0)

    result = get_orchestration_state_result(
        context_builder, generator_function_call_entity)

    expected_state = base_expected_state(
        [3]
    )

    add_call_entity_action(expected_state, entityId, "add", 3)
    expected_state._is_done = True
    expected = expected_state.to_json()

    #assert_valid_schema(result)

    assert_orchestration_state_equals(expected, result)