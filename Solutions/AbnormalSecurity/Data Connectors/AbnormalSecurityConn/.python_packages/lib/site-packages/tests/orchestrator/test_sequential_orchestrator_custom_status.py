from azure.durable_functions.models.ReplaySchema import ReplaySchema
from .orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallActivityAction \
    import CallActivityAction
from typing import Any


def generator_function(context):
    task1 = yield context.call_activity("Hello", "Tokyo")
    context.set_custom_status("--- Tokyo ->")
    task2 = yield context.call_activity("Hello", "Seattle")
    context.set_custom_status("Seattle ->")
    task3 = yield context.call_activity("Hello", "London")
    context.set_custom_status("London ---")


def generator_function_with_object_status(context):
    task1 = yield context.call_activity("Hello", "Tokyo")
    obj_status = {}
    obj_status["tokyo"] = "completed"
    context.set_custom_status(obj_status)

def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)

def add_custom_status(state:OrchestratorState, status:Any):
    state._custom_status = status

def add_hello_action(state: OrchestratorState, input_: str):
    action = CallActivityAction(function_name='Hello', input_=input_)
    state.actions.append([action])

def add_is_done(state:OrchestratorState, is_completed:bool):
    state._is_done = is_completed

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
    add_hello_action(expected_state,'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_custom_status_tokyo():
    context_builder = ContextBuilder('test_custom_status')

    # Complete the first event so that it sets the custom status
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state,'Tokyo')
    add_hello_action(expected_state,'Seattle')
    add_custom_status(expected_state,"--- Tokyo ->")
    expected = expected_state.to_json()
        
    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_custom_status_tokyo_seattle():
   context_builder = ContextBuilder('test_custom_status_seattle')

   # Complete the two event so that it sets the custom status accordingly
   add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
   add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")

   result = get_orchestration_state_result(
        context_builder, generator_function)

   expected_state = base_expected_state()
   add_hello_action(expected_state,'Tokyo')
   add_hello_action(expected_state,'Seattle')
   add_hello_action(expected_state,'London')
   add_custom_status(expected_state,"Seattle ->")
   expected = expected_state.to_json()
        
   assert_valid_schema(result)
   assert_orchestration_state_equals(expected, result) 

def test_custom_status_as_object():
    context_builder = ContextBuilder('test_custom_status_as_object')

    # Add first event as completed
    add_hello_completed_events(context_builder,0,"\"Hello Tokyo!\"")

    # pass generator_function_with_object_status as target test
    result = get_orchestration_state_result(
        context_builder, generator_function_with_object_status)
  
    # construct expected state
    expected_state = base_expected_state()
    add_hello_action(expected_state,'Tokyo')
    obj_status = {}
    obj_status['tokyo'] = 'completed'
    add_custom_status(expected_state,obj_status)
    add_is_done(expected_state,True)
    expected = expected_state.to_json()
        
    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result) 