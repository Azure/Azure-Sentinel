from azure.durable_functions.models.ReplaySchema import ReplaySchema
import json
from typing import Dict

from azure.durable_functions.constants import HTTP_ACTION_NAME
from azure.durable_functions.models import DurableHttpRequest
from .orchestrator_test_utils import assert_orchestration_state_equals, \
    get_orchestration_state_result, assert_valid_schema, assert_dict_are_equal
from tests.test_utils.ContextBuilder import ContextBuilder
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.actions.CallHttpAction import CallHttpAction
from azure.durable_functions.models.TokenSource import ManagedIdentityTokenSource

TEST_URI: str = \
    'https://localhost:7071/we_just_need_a_uri_to_use_for_testing'
SIMPLE_RESULT: str = json.dumps({'name': 'simple'})
CONTENT = json.dumps({'name': 'some data', 'additional': 'data'})
HEADERS = {'header1': 'value1', 'header2': 'value2'}
TOKEN_SOURCE = ManagedIdentityTokenSource('https://management.core.windows.net/')


def simple_get_generator_function(context):
    url = TEST_URI
    yield context.call_http("GET", url)


def complete_generator_function(context):
    url = TEST_URI

    yield context.call_http(method="POST", uri=url, content=json.loads(CONTENT),
                            headers=HEADERS, token_source=TOKEN_SOURCE)


def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema.value)


def add_http_action(state: OrchestratorState, request):
    action = CallHttpAction(request)
    state.actions.append([action])


def add_completed_http_events(
        context_builder: ContextBuilder, id_: int, result: str):
    context_builder.add_task_scheduled_event(name=HTTP_ACTION_NAME, id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=result)


def add_failed_http_events(
        context_builder: ContextBuilder, id_: int, reason: str, details: str):
    context_builder.add_task_scheduled_event(name=HTTP_ACTION_NAME, id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_failed_event(
        id_=id_, reason=reason, details=details)


def get_request() -> DurableHttpRequest:
    return DurableHttpRequest(method='GET', uri=TEST_URI)


def post_request() -> DurableHttpRequest:
    return DurableHttpRequest(method="POST", uri=TEST_URI, content=json.dumps(CONTENT),
                              headers=HEADERS, token_source=TOKEN_SOURCE)


def test_initial_orchestration_state():
    context_builder = ContextBuilder('test_simple_function')

    result = get_orchestration_state_result(
        context_builder, simple_get_generator_function)

    expected_state = base_expected_state()
    request = get_request()
    add_http_action(expected_state, request)
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_completed_state():
    context_builder = ContextBuilder('test_simple_function')
    add_completed_http_events(context_builder, 0, SIMPLE_RESULT)

    result = get_orchestration_state_result(
        context_builder, simple_get_generator_function)

    expected_state = base_expected_state()
    request = get_request()
    add_http_action(expected_state, request)
    expected_state._is_done = True
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)


def test_failed_state():
    failed_reason = 'Reasons'
    failed_details = 'Stuff and Things'
    context_builder = ContextBuilder('test_simple_function')
    add_failed_http_events(
        context_builder, 0, failed_reason, failed_details)

    try:
        result = get_orchestration_state_result(
            context_builder, simple_get_generator_function)
        # We expected an exception
        assert False
    except Exception as e:
        error_label = "\n\n$OutOfProcData$:"
        error_str = str(e)

        expected_state = base_expected_state()
        request = get_request()
        add_http_action(expected_state, request)

        error_msg = f'{failed_reason} \n {failed_details}'
        expected_state._error = error_msg
        state_str = expected_state.to_json_string()
        
        expected_error_str = f"{error_msg}{error_label}{state_str}"
        assert expected_error_str == error_str


def test_initial_post_state():
    context_builder = ContextBuilder('test_simple_function')

    result = get_orchestration_state_result(
        context_builder, complete_generator_function)

    expected_state = base_expected_state()
    request = post_request()
    add_http_action(expected_state, request)
    expected = expected_state.to_json()

    # assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
    validate_result_http_request(result)


def validate_result_http_request(result):
    http_request = result['actions'][0][0]['httpRequest']
    assert http_request is not None
    assert http_request['method'] == 'POST'
    assert http_request['uri'] == TEST_URI
    content = http_request['content']
    assert isinstance(content, str)
    content = json.loads(content)
    test_content = json.loads(CONTENT)
    assert_dict_are_equal(test_content, content)
    assert content['name'] == 'some data'
    headers: Dict[str, str] = http_request['headers']
    assert_dict_are_equal(HEADERS, headers)
    assert http_request['tokenSource']['resource'] == TOKEN_SOURCE.resource


def test_post_completed_state():
    context_builder = ContextBuilder('test_simple_function')
    add_completed_http_events(context_builder, 0, SIMPLE_RESULT)

    result = get_orchestration_state_result(
        context_builder, complete_generator_function)

    expected_state = base_expected_state()
    request = post_request()
    add_http_action(expected_state, request)
    expected_state._is_done = True
    expected = expected_state.to_json()

    # assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
    validate_result_http_request(result)
