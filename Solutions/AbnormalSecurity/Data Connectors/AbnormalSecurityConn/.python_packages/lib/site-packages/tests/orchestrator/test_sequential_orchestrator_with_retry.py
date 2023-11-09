from azure.durable_functions.models.ReplaySchema import ReplaySchema
from .orchestrator_test_utils \
    import get_orchestration_state_result, assert_orchestration_state_equals, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.RetryOptions import RetryOptions
from azure.durable_functions.models.actions.CallActivityWithRetryAction \
    import CallActivityWithRetryAction


RETRY_OPTIONS = RetryOptions(5000, 3)


def generator_function(context):
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


def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)


def add_hello_action(state: OrchestratorState, input_: str):
    retry_options = RETRY_OPTIONS
    action = CallActivityWithRetryAction(
        function_name='Hello', retry_options=retry_options, input_=input_)
    state._actions.append([action])


def add_hello_failed_events(
        context_builder: ContextBuilder, id_: int, reason: str, details: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_failed_event(
        id_=id_, reason=reason, details=details)


def add_hello_completed_events(
        context_builder: ContextBuilder, id_: int, result: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result)


def add_retry_timer_events(context_builder: ContextBuilder, id_: int):
    fire_at = context_builder.add_timer_created_event(id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_timer_fired_event(id_=id_, fire_at=fire_at)


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
    add_hello_action(expected_state, 'Seattle')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_with_retry():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_with_timer_entry():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_with_failed_retry():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_with_failed_retry_timer_added():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 3)

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_successful_tokyo_with_failed_retry_timer_added():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_completed_events(context_builder, 2, "\"Hello Tokyo!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_tokyo_hit_max_attempts():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(context_builder, 0, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 1)
    add_hello_failed_events(context_builder, 2, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 3)
    add_hello_failed_events(context_builder, 4, failed_reason, failed_details)
    add_retry_timer_events(context_builder, 5)

    try:
        result = get_orchestration_state_result(
            context_builder, generator_function)
        # expected an exception
        assert False
    except Exception as e:
        error_label = "\n\n$OutOfProcData$:"
        error_str = str(e)

        expected_state = base_expected_state()
        add_hello_action(expected_state, 'Tokyo')

        error_msg = f'{failed_reason} \n {failed_details}'
        expected_state._error = error_msg
        state_str = expected_state.to_json_string()
        
        expected_error_str = f"{error_msg}{error_label}{state_str}"
        assert expected_error_str == error_str
