from azure.durable_functions.models.ReplaySchema import ReplaySchema
import json

from azure.durable_functions.models import OrchestratorState
from azure.durable_functions.models.actions import CallActivityAction
from .orchestrator_test_utils import get_orchestration_state_result, \
    assert_orchestration_state_equals, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder


def generator_function(context):
    activity_count = yield context.call_activity("GetActivityCount")
    tasks = []
    for i in range(activity_count):
        current_task = context.call_activity("ParrotValue", str(i))
        tasks.append(current_task)
    values = yield context.task_all(tasks)
    results = yield context.call_activity("ShowMeTheSum", values)
    return results


def base_expected_state(output=None, error=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema)


def add_completed_event(
        context_builder: ContextBuilder, id_: int, name: str, result):
    context_builder.add_task_scheduled_event(name=name, id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=json.dumps(result))


def add_failed_event(
        context_builder: ContextBuilder, id_: int, name: str, reason: str, details: str):
    context_builder.add_task_scheduled_event(name=name, id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_failed_event(
        id_=id_, reason=reason, details=details)


def add_completed_task_set_events(
        context_builder: ContextBuilder, start_id: int, name: str, volume: int,
        failed_index: int = -1, failed_reason: str = '', failed_details: str = ''):
    for i in range(volume):
        if i != failed_index:
            add_completed_event(context_builder, start_id + i, name, i)
        else:
            add_failed_event(context_builder, start_id + i, name, failed_reason, failed_details)


def add_single_action(state: OrchestratorState, function_name: str, input_):
    action = CallActivityAction(function_name=function_name, input_=input_)
    state.actions.append([action])


def add_multi_actions(state: OrchestratorState, function_name: str, volume: int):
    actions = []
    for i in range(volume):
        action = CallActivityAction(function_name=function_name, input_=json.dumps(i))
        actions.append(action)
    state.actions.append(actions)


def test_initial_call():
    context_builder = ContextBuilder('test_fan_out_fan_in_function')

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_single_action(expected_state, function_name='GetActivityCount', input_=None)
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_get_activity_count_success():
    activity_count = 5
    context_builder = ContextBuilder('test_fan_out_fan_in_function')
    add_completed_event(context_builder, 0, 'GetActivityCount', activity_count)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_single_action(expected_state, function_name='GetActivityCount', input_=None)
    add_multi_actions(expected_state, function_name='ParrotValue', volume=activity_count)
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_parrot_value_success():
    activity_count = 5
    context_builder = ContextBuilder('test_fan_out_fan_in_function')
    add_completed_event(context_builder, 0, 'GetActivityCount', activity_count)
    add_completed_task_set_events(context_builder, 1, 'ParrotValue', activity_count)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_single_action(expected_state, function_name='GetActivityCount', input_=None)
    add_multi_actions(expected_state, function_name='ParrotValue', volume=activity_count)
    results = []
    for i in range(activity_count):
        results.append(i)
    add_single_action(expected_state, function_name='ShowMeTheSum', input_=results)
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_show_me_the_sum_success():
    activity_count = 5
    sum_ = 0
    for i in range(activity_count):
        sum_ += i
    sum_results = f"Well that's nice {sum_}!"
    context_builder = ContextBuilder('test_fan_out_fan_in_function')
    add_completed_event(context_builder, 0, 'GetActivityCount', activity_count)
    add_completed_task_set_events(context_builder, 1, 'ParrotValue', activity_count)
    add_completed_event(
        context_builder, activity_count + 1, 'ShowMeTheSum', sum_results)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state(sum_results)
    add_single_action(expected_state, function_name='GetActivityCount', input_=None)
    add_multi_actions(expected_state, function_name='ParrotValue', volume=activity_count)
    results = []
    for i in range(activity_count):
        results.append(i)
    add_single_action(expected_state, function_name='ShowMeTheSum', input_=results)
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_parrot_value():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    activity_count = 5
    context_builder = ContextBuilder('test_fan_out_fan_in_function')
    add_completed_event(context_builder, 0, 'GetActivityCount', activity_count)
    add_completed_task_set_events(context_builder, 1, 'ParrotValue', activity_count,
                                  2, failed_reason, failed_details)

    try:
        result = get_orchestration_state_result(
            context_builder, generator_function)
        # we expected an exception
        assert False
    except Exception as e:
        error_label = "\n\n$OutOfProcData$:"
        error_str = str(e)

        expected_state = base_expected_state(error=f'{failed_reason} \n {failed_details}')
        add_single_action(expected_state, function_name='GetActivityCount', input_=None)
        add_multi_actions(expected_state, function_name='ParrotValue', volume=activity_count)

        error_msg = f'{failed_reason} \n {failed_details}'
        expected_state._error = error_msg
        state_str = expected_state.to_json_string()
        
        expected_error_str = f"{error_msg}{error_label}{state_str}"
        assert expected_error_str == error_str
