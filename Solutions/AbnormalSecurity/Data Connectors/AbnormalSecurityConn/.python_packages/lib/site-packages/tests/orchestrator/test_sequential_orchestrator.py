from azure.durable_functions.models.actions.WhenAnyAction import WhenAnyAction
from azure.durable_functions.models.actions.WhenAllAction import WhenAllAction
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from datetime import datetime, timedelta
from .orchestrator_test_utils \
    import assert_orchestration_state_equals, get_orchestration_state_result, assert_valid_schema
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallActivityAction \
    import CallActivityAction
from tests.test_utils.testClasses import SerializableClass


def generator_function(context):
    outputs = []

    task1 = yield context.call_activity("Hello", "Tokyo")
    task2 = yield context.call_activity("Hello", "Seattle")
    task3 = yield context.call_activity("Hello", "London")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs

def generator_function_no_yield(context):
    outputs = []

    task1 = context.call_activity("Hello", "Tokyo")
    task2 = context.call_activity("Hello", "Seattle")
    task3 = yield context.call_activity("Hello", "London")

    return task3

def generator_function_duplicate_yield(context):
    task1 = context.call_activity("Hello", "Tokyo")
    yield task1
    yield task1

    return ""

def generator_function_compound_tasks(context):
    yield context.call_activity("Hello", "Tokyo")

    task1 = context.call_activity("Hello", "Tokyo")
    task2 = context.call_activity("Hello", "Tokyo")
    task3 = context.call_activity("Hello", "Tokyo")
    task4 = context.task_any([task3])
    task5 = context.task_all([task1, task2, task4])
    task6 = context.task_any([task5])
    yield task6

    return ""

def generator_function_time_is_not_none(context):
    outputs = []

    now = context.current_utc_datetime
    if not now:
        raise Exception("No time! 1st attempt")
    task1 = yield context.call_activity("Hello", "Tokyo")

    now = context.current_utc_datetime
    if not now:
        raise Exception("No time! 2nd attempt")
    task2 = yield context.call_activity("Hello", "Seattle")

    now = context.current_utc_datetime
    if not now:
        raise Exception("No time! 3rd attempt")
    task3 = yield context.call_activity("Hello", "London")

    now = context.current_utc_datetime
    if not now:
        raise Exception("No time! 4th attempt")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs

def generator_function_time_gather(context):
    outputs = []

    outputs.append(context.current_utc_datetime.strftime("%m/%d/%Y, %H:%M:%S"))
    yield context.call_activity("Hello", "Tokyo")

    outputs.append(context.current_utc_datetime.strftime("%m/%d/%Y, %H:%M:%S"))
    yield context.call_activity("Hello", "Seattle")

    outputs.append(context.current_utc_datetime.strftime("%m/%d/%Y, %H:%M:%S"))
    yield context.call_activity("Hello", "London")

    outputs.append(context.current_utc_datetime.strftime("%m/%d/%Y, %H:%M:%S"))
    return outputs

def generator_function_rasing_ex(context):
    outputs = []

    task1 = yield context.call_activity("Hello", "Tokyo")
    task2 = yield context.call_activity("Hello", "Seattle")
    task3 = yield context.call_activity("Hello", "London")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    raise ValueError("Oops!")

def generator_function_with_serialization(context):
    """Ochestrator to test sequential activity calls with a serializable input arguments."""
    outputs = []

    task1 = yield context.call_activity("Hello", SerializableClass("Tokyo"))
    task2 = yield context.call_activity("Hello", SerializableClass("Seattle"))
    task3 = yield context.call_activity("Hello", SerializableClass("London"))

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs

def generator_function_new_guid(context):
    """Simple orchestrator that generates 3 GUIDs"""
    outputs = []

    output1 = context.new_guid()
    output2 = context.new_guid()
    output3 = context.new_guid()

    outputs.append(str(output1))
    outputs.append(str(output2))
    outputs.append(str(output3))
    return outputs


def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema)


def add_hello_action(state: OrchestratorState, input_: str):
    action = CallActivityAction(function_name='Hello', input_=input_)
    state.actions.append([action])

def add_hello_completed_events(
        context_builder: ContextBuilder, id_: int, result: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result)


def add_hello_failed_events(
        context_builder: ContextBuilder, id_: int, reason: str, details: str):
    context_builder.add_task_scheduled_event(name='Hello', id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_failed_event(
        id_=id_, reason=reason, details=details)


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


def test_failed_tokyo_state():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_hello_failed_events(
        context_builder, 0, failed_reason, failed_details)

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


def test_user_code_raises_exception():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 2, "\"Hello London!\"")

    try:
        result = get_orchestration_state_result(
            context_builder, generator_function_rasing_ex)
        # expected an exception
        assert False
    except Exception as e:
        error_label = "\n\n$OutOfProcData$:"
        error_str = str(e)

        expected_state = base_expected_state()
        add_hello_action(expected_state, 'Tokyo')
        add_hello_action(expected_state, 'Seattle')
        add_hello_action(expected_state, 'London')
        error_msg = 'Oops!'
        expected_state._error = error_msg
        state_str = expected_state.to_json_string()
        
        expected_error_str = f"{error_msg}{error_label}{state_str}"
        assert expected_error_str == error_str

def test_tokyo_and_seattle_state():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state()
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    add_hello_action(expected_state, 'London')
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_tokyo_and_seattle_and_london_state():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 2, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function)

    expected_state = base_expected_state(
        ['Hello Tokyo!', 'Hello Seattle!', 'Hello London!'])
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    add_hello_action(expected_state, 'London')
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_sequential_orchestration_no_yield():
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_no_yield)

    expected_state = base_expected_state('Hello London!')
    add_hello_action(expected_state, 'London')
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_tokyo_and_seattle_and_london_with_serialization_state():
    """Tests the sequential function pattern with custom object serialization.
    
    This simple test validates that a sequential function pattern returns
    the expected state when the input to activities is a user-provided
    serializable class.
    """
    context_builder = ContextBuilder('test_simple_function')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 2, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_with_serialization)

    expected_state = base_expected_state(
        ['Hello Tokyo!', 'Hello Seattle!', 'Hello London!'])
    add_hello_action(expected_state, SerializableClass("Tokyo"))
    add_hello_action(expected_state, SerializableClass("Seattle"))
    add_hello_action(expected_state, SerializableClass("London"))
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_utc_time_is_never_none():
    """Tests an orchestrator that errors out if its current_utc_datetime is ever None.

    If we receive all activity results, it means we never error'ed out. Our test has
    a history events array with identical timestamps, simulating events arriving
    very close to one another."""

    # we set `increase_time` to False to make sure the changes are resilient
    # to undistinguishable timestamps (events arrive very close to each other)
    context_builder = ContextBuilder('test_simple_function', increase_time=False)
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 2, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_deterministic_utc_time)

    expected_state = base_expected_state(
        ['Hello Tokyo!', 'Hello Seattle!', 'Hello London!'])
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    add_hello_action(expected_state, 'London')
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_utc_time_is_never_none():
    """Tests an orchestrator that errors out if its current_utc_datetime is ever None.

    If we receive all activity results, it means we never error'ed out. Our test has
    a history events array with identical timestamps, simulating events arriving
    very close to one another."""

    # we set `increase_time` to False to make sure the changes are resilient
    # to undistinguishable timestamps (events arrive very close to each other)
    context_builder = ContextBuilder('test_simple_function', increase_time=False)
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 2, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_time_is_not_none)

    expected_state = base_expected_state(
        ['Hello Tokyo!', 'Hello Seattle!', 'Hello London!'])
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    add_hello_action(expected_state, 'London')
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_utc_time_updates_correctly():
    """Tests that current_utc_datetime updates correctly"""

    now = datetime.utcnow()
    # the first orchestrator-started event starts 1 second after `now`
    context_builder = ContextBuilder('test_simple_function', starting_time=now)
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")
    add_hello_completed_events(context_builder, 1, "\"Hello Seattle!\"")
    add_hello_completed_events(context_builder, 2, "\"Hello London!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_time_gather)

    # In the expected history, the orchestrator starts again every 4 seconds
    # The current_utc_datetime should update to the orchestrator start event timestamp
    num_restarts = 3
    expected_utc_time = now + timedelta(seconds=1)
    outputs = [expected_utc_time.strftime("%m/%d/%Y, %H:%M:%S")]
    for _ in range(num_restarts):
        expected_utc_time += timedelta(seconds=4)
        outputs.append(expected_utc_time.strftime("%m/%d/%Y, %H:%M:%S"))

    expected_state = base_expected_state(outputs)
    add_hello_action(expected_state, 'Tokyo')
    add_hello_action(expected_state, 'Seattle')
    add_hello_action(expected_state, 'London')
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_new_guid_orchestrator():
    """Tests that the new_guid API is replay-safe and produces new GUIDs every time"""
    context_builder = ContextBuilder('test_guid_orchestrator')

    # To test that the API is replay-safe, we generate two orchestrators
    # with the same starting context
    result1 = get_orchestration_state_result(
        context_builder, generator_function_new_guid)
    outputs1 = result1["output"]

    result2 = get_orchestration_state_result(
        context_builder, generator_function_new_guid)
    outputs2 = result2["output"]

    # All GUIDs should be unique
    assert len(outputs1) == len(set(outputs1))
    # The two GUID lists should be the same
    assert outputs1 == outputs2

def test_duplicate_yields_do_not_add_duplicate_actions():
    """Tests that yield'ing a Task twice does not double the task's actions"""
    context_builder = ContextBuilder('test_guid_orchestrator')
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_duplicate_yield)

    expected_state = base_expected_state("")
    add_hello_action(expected_state, 'Tokyo')
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_compound_tasks_return_single_action_in_V2():
    """Tests that compound tasks, in the v2 replay schema, are represented as a single "deep" action"""
    context_builder = ContextBuilder('test_v2_replay_schema', replay_schema=ReplaySchema.V2)
    add_hello_completed_events(context_builder, 0, "\"Hello Tokyo!\"")

    result = get_orchestration_state_result(
        context_builder, generator_function_compound_tasks)

    expected_state = base_expected_state(replay_schema=ReplaySchema.V2)
    expected_state._actions = [
        [CallActivityAction("Hello", "Tokyo"), WhenAnyAction(
            [WhenAllAction(
                [CallActivityAction("Hello", "Tokyo"), CallActivityAction("Hello", "Tokyo"), WhenAnyAction(
                    [CallActivityAction("Hello", "Tokyo")])
                ])
            ])
        ]
    ]
    expected_state._is_done = False
    expected = expected_state.to_json()

    #assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)