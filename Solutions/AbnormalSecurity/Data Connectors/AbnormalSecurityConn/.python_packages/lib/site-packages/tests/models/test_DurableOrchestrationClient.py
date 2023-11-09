import json
from typing import Any

import pytest

from azure.durable_functions.models.OrchestrationRuntimeStatus import OrchestrationRuntimeStatus
from azure.durable_functions.models.DurableOrchestrationClient \
    import DurableOrchestrationClient
from azure.durable_functions.models.DurableOrchestrationStatus import DurableOrchestrationStatus
from tests.conftest import replace_stand_in_bits
from tests.test_utils.constants import RPC_BASE_URL
from unittest.mock import Mock

TEST_INSTANCE_ID = '2e2568e7-a906-43bd-8364-c81733c5891e'
TEST_CREATED_TIME = '2020-01-01T05:00:00Z'
TEST_LAST_UPDATED_TIME = '2020-01-01T05:00:00Z'
MESSAGE_400 = 'instance failed or terminated'
MESSAGE_404 = 'instance not found or pending'
MESSAGE_500 = 'instance failed with unhandled exception'
MESSAGE_501 = "well we didn't expect that"

INSTANCE_ID = "2e2568e7-a906-43bd-8364-c81733c5891e"
REASON = "Stuff"

TEST_ORCHESTRATOR = "MyDurableOrchestrator"
EXCEPTION_ORCHESTRATOR_NOT_FOUND_EXMESSAGE = "The function <orchestrator> doesn't exist,"\
    " is disabled, or is not an orchestrator function. Additional info: "\
    "the following are the known orchestrator functions: <list>"
EXCEPTION_ORCHESTRATOR_NOT_FOUND_MESSAGE = "One or more of the arguments submitted is incorrect"
EXCEPTION_TYPE_ORCHESTRATOR_NOT_FOUND = "System.ArgumentException"
STACK_TRACE = "'   at Microsoft.Azure.WebJobs.Extensions.DurableTask..."

class MockRequest:
    def __init__(self, expected_url: str, response: [int, any]):
        self._expected_url = expected_url
        self._response = response
        self._get_count = 0

    @property
    def get_count(self):
        return self._get_count

    async def get(self, url: str):
        self._get_count += 1
        assert url == self._expected_url
        return self._response

    async def delete(self, url: str):
        assert url == self._expected_url
        return self._response

    async def post(self, url: str, data: Any = None):
        assert url == self._expected_url
        return self._response


def test_get_start_new_url(binding_string):
    client = DurableOrchestrationClient(binding_string)
    instance_id = "2e2568e7-a906-43bd-8364-c81733c5891e"
    function_name = "my_function"
    start_new_url = client._get_start_new_url(instance_id, function_name)
    expected_url = replace_stand_in_bits(
        f"{RPC_BASE_URL}orchestrators/{function_name}/{instance_id}")
    assert expected_url == start_new_url


def test_get_input_returns_none_when_none_supplied():
    result = DurableOrchestrationClient._get_json_input(None)
    assert result is None


def test_get_input_returns_json_string(binding_string):
    input_ = json.loads(binding_string)
    result = DurableOrchestrationClient._get_json_input(input_)
    input_as_string = json.dumps(input_)
    assert input_as_string == result


def test_get_raise_event_url(binding_string):
    client = DurableOrchestrationClient(binding_string)
    instance_id = "2e2568e7-a906-43bd-8364-c81733c5891e"
    event_name = "test_event_name"
    task_hub_name = "test_task_hub"
    connection_name = "test_connection"
    raise_event_url = client._get_raise_event_url(instance_id, event_name, task_hub_name,
                                                  connection_name)

    expected_url = replace_stand_in_bits(
        f"{RPC_BASE_URL}instances/{instance_id}/raiseEvent/{event_name}"
        f"?taskHub=test_task_hub&connection=test_connection")

    assert expected_url == raise_event_url


def test_create_check_status_response(binding_string):
    client = DurableOrchestrationClient(binding_string)
    instance_id = "2e2568e7-a906-43bd-8364-c81733c5891e"
    request = Mock(url="http://test_azure.net/api/orchestrators/DurableOrchestrationTrigger")
    returned_response = client.create_check_status_response(request, instance_id)

    http_management_payload = {
        "id": instance_id,
        "statusQueryGetUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/"
            r"2e2568e7-a906-43bd-8364-c81733c5891e?taskHub"
            r"=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",
        "sendEventPostUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/"
            r"2e2568e7-a906-43bd-8364-c81733c5891e/raiseEvent/{"
            r"eventName}?taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",
        "terminatePostUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/"
            r"2e2568e7-a906-43bd-8364-c81733c5891e/terminate"
            r"?reason={text}&taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",
        "rewindPostUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/"
            r"2e2568e7-a906-43bd-8364-c81733c5891e/rewind?reason"
            r"={text}&taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE",
        "purgeHistoryDeleteUri":
            r"http://test_azure.net/runtime/webhooks/durabletask/instances/"
            r"2e2568e7-a906-43bd-8364-c81733c5891e"
            r"?taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE"
    }
    for key, _ in http_management_payload.items():
        http_management_payload[key] = replace_stand_in_bits(http_management_payload[key])
    expected_response = {
        "status_code": 202,
        "body": json.dumps(http_management_payload),
        "headers": {
            "Content-Type": "application/json",
            "Location": http_management_payload["statusQueryGetUri"],
            "Retry-After": "10",
        },
    }

    for k, v in expected_response.get("headers").items():
        assert v == returned_response.headers.get(k)
    assert expected_response.get("status_code") == returned_response.status_code
    assert expected_response.get("body") == returned_response.get_body().decode()


@pytest.mark.asyncio
async def test_get_202_get_status_success(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[202, dict(createdTime=TEST_CREATED_TIME,
                                                   lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                                                   runtimeStatus="Running")])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.get_status(TEST_INSTANCE_ID)
    assert result is not None
    assert result.runtime_status.name == "Running"


@pytest.mark.asyncio
async def test_get_200_get_status_success(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[200, dict(createdTime=TEST_CREATED_TIME,
                                                   lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                                                   runtimeStatus="Completed")])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.get_status(TEST_INSTANCE_ID)
    assert result is not None
    assert result.runtime_status.name == "Completed"


@pytest.mark.asyncio
async def test_get_500_get_status_failed(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[500, MESSAGE_500])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.get_status(TEST_INSTANCE_ID)
    assert result is not None
    assert result.message == MESSAGE_500


@pytest.mark.asyncio
async def test_get_400_get_status_failed(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[400, MESSAGE_400])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.get_status(TEST_INSTANCE_ID)
    assert result is not None
    assert result.message == MESSAGE_400


@pytest.mark.asyncio
async def test_get_404_get_status_failed(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[404, MESSAGE_404])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.get_status(TEST_INSTANCE_ID)
    assert result is not None
    assert result.message == MESSAGE_404


@pytest.mark.asyncio
async def test_get_501_get_status_failed(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[501, MESSAGE_501])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    with pytest.raises(Exception):
        await client.get_status(TEST_INSTANCE_ID)


@pytest.mark.asyncio
async def test_get_200_get_status_by_success(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/?runtimeStatus=Running",
                               response=[200, [dict(createdTime=TEST_CREATED_TIME,
                                                    lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                                                    runtimeStatus="Running"),
                                               dict(createdTime=TEST_CREATED_TIME,
                                                    lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                                                    runtimeStatus="Running")
                                               ]])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.get_status_by(runtime_status=[OrchestrationRuntimeStatus.Running])
    assert result is not None
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_500_get_status_by_failed(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/?runtimeStatus=Running",
                               response=[500, MESSAGE_500])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    with pytest.raises(Exception):
        await client.get_status_by(runtime_status=[OrchestrationRuntimeStatus.Running])


@pytest.mark.asyncio
async def test_get_200_get_status_all_success(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/",
                               response=[200, [dict(createdTime=TEST_CREATED_TIME,
                                                    lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                                                    runtimeStatus="Running"),
                                               dict(createdTime=TEST_CREATED_TIME,
                                                    lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                                                    runtimeStatus="Running")
                                               ]])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.get_status_all()
    assert result is not None
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_500_get_status_all_failed(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/",
                               response=[500, MESSAGE_500])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    with pytest.raises(Exception):
        await client.get_status_all()


@pytest.mark.asyncio
async def test_delete_200_purge_instance_history(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[200, dict(instancesDeleted=1)])
    client = DurableOrchestrationClient(binding_string)
    client._delete_async_request = mock_request.delete

    result = await client.purge_instance_history(TEST_INSTANCE_ID)
    assert result is not None
    assert result.instances_deleted == 1


@pytest.mark.asyncio
async def test_delete_404_purge_instance_history(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[404, MESSAGE_404])
    client = DurableOrchestrationClient(binding_string)
    client._delete_async_request = mock_request.delete

    result = await client.purge_instance_history(TEST_INSTANCE_ID)
    assert result is not None
    assert result.instances_deleted == 0


@pytest.mark.asyncio
async def test_delete_500_purge_instance_history(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[500, MESSAGE_500])
    client = DurableOrchestrationClient(binding_string)
    client._delete_async_request = mock_request.delete

    with pytest.raises(Exception):
        await client.purge_instance_history(TEST_INSTANCE_ID)


@pytest.mark.asyncio
async def test_delete_200_purge_instance_history_by(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/?runtimeStatus=Running",
                               response=[200, dict(instancesDeleted=1)])
    client = DurableOrchestrationClient(binding_string)
    client._delete_async_request = mock_request.delete

    result = await client.purge_instance_history_by(
        runtime_status=[OrchestrationRuntimeStatus.Running])
    assert result is not None
    assert result.instances_deleted == 1


@pytest.mark.asyncio
async def test_delete_404_purge_instance_history_by(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/?runtimeStatus=Running",
                               response=[404, MESSAGE_404])
    client = DurableOrchestrationClient(binding_string)
    client._delete_async_request = mock_request.delete

    result = await client.purge_instance_history_by(
        runtime_status=[OrchestrationRuntimeStatus.Running])
    assert result is not None
    assert result.instances_deleted == 0


@pytest.mark.asyncio
async def test_delete_500_purge_instance_history_by(binding_string):
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/?runtimeStatus=Running",
                               response=[500, MESSAGE_500])
    client = DurableOrchestrationClient(binding_string)
    client._delete_async_request = mock_request.delete

    with pytest.raises(Exception):
        await client.purge_instance_history_by(
            runtime_status=[OrchestrationRuntimeStatus.Running])


@pytest.mark.asyncio
async def test_post_202_terminate(binding_string):
    raw_reason = 'stuff and things'
    reason = 'stuff%20and%20things'
    mock_request = MockRequest(
        expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}/terminate?reason={reason}",
        response=[202, None])
    client = DurableOrchestrationClient(binding_string)
    client._post_async_request = mock_request.post

    result = await client.terminate(TEST_INSTANCE_ID, raw_reason)
    assert result is None


@pytest.mark.asyncio
async def test_post_410_terminate(binding_string):
    raw_reason = 'stuff and things'
    reason = 'stuff%20and%20things'
    mock_request = MockRequest(
        expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}/terminate?reason={reason}",
        response=[410, None])
    client = DurableOrchestrationClient(binding_string)
    client._post_async_request = mock_request.post

    result = await client.terminate(TEST_INSTANCE_ID, raw_reason)
    assert result is None


@pytest.mark.asyncio
async def test_post_404_terminate(binding_string):
    raw_reason = 'stuff and things'
    reason = 'stuff%20and%20things'
    mock_request = MockRequest(
        expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}/terminate?reason={reason}",
        response=[404, MESSAGE_404])
    client = DurableOrchestrationClient(binding_string)
    client._post_async_request = mock_request.post

    with pytest.raises(Exception):
        await client.terminate(TEST_INSTANCE_ID, raw_reason)


@pytest.mark.asyncio
async def test_post_500_terminate(binding_string):
    raw_reason = 'stuff and things'
    reason = 'stuff%20and%20things'
    mock_request = MockRequest(
        expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}/terminate?reason={reason}",
        response=[500, MESSAGE_500])
    client = DurableOrchestrationClient(binding_string)
    client._post_async_request = mock_request.post

    with pytest.raises(Exception):
        await client.terminate(TEST_INSTANCE_ID, raw_reason)


@pytest.mark.asyncio
async def test_wait_or_response_200_completed(binding_string):
    output = 'Some output'
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[200, dict(createdTime=TEST_CREATED_TIME,
                                                   lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                                                   runtimeStatus="Completed",
                                                   output=output)])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.wait_for_completion_or_create_check_status_response(
        None, TEST_INSTANCE_ID)
    assert result is not None
    assert result.status_code == 200
    assert result.mimetype == 'application/json'
    assert result.get_body().decode() == output


@pytest.mark.asyncio
async def test_wait_or_response_200_canceled(binding_string):
    status = dict(createdTime=TEST_CREATED_TIME,
                  lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                  runtimeStatus="Canceled")
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[200, status])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.wait_for_completion_or_create_check_status_response(
        None, TEST_INSTANCE_ID)
    assert result is not None
    assert result.status_code == 200
    assert result.mimetype == 'application/json'
    assert json.loads(result.get_body().decode()) == DurableOrchestrationStatus.from_json(
        status).to_json()


@pytest.mark.asyncio
async def test_wait_or_response_200_terminated(binding_string):
    status = dict(createdTime=TEST_CREATED_TIME,
                  lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                  runtimeStatus="Terminated")
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[200, status])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.wait_for_completion_or_create_check_status_response(
        None, TEST_INSTANCE_ID)
    assert result is not None
    assert result.status_code == 200
    assert result.mimetype == 'application/json'
    assert json.loads(result.get_body().decode()) == DurableOrchestrationStatus.from_json(
        status).to_json()


@pytest.mark.asyncio
async def test_wait_or_response_200_failed(binding_string):
    status = dict(createdTime=TEST_CREATED_TIME,
                  lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                  runtimeStatus="Failed")
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[200, status])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    result = await client.wait_for_completion_or_create_check_status_response(
        None, TEST_INSTANCE_ID)
    assert result is not None
    assert result.status_code == 500
    assert result.mimetype == 'application/json'
    assert json.loads(result.get_body().decode()) == DurableOrchestrationStatus.from_json(
        status).to_json()


@pytest.mark.asyncio
async def test_wait_or_response_check_status_response(binding_string):
    status = dict(createdTime=TEST_CREATED_TIME,
                  lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                  runtimeStatus="Running")
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[200, status])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    request = Mock(url="http://test_azure.net/api/orchestrators/DurableOrchestrationTrigger")
    result = await client.wait_for_completion_or_create_check_status_response(
        request, TEST_INSTANCE_ID, timeout_in_milliseconds=2000)
    assert result is not None
    assert mock_request.get_count == 3


@pytest.mark.asyncio
async def test_wait_or_response_null_request(binding_string):
    status = dict(createdTime=TEST_CREATED_TIME,
                  lastUpdatedTime=TEST_LAST_UPDATED_TIME,
                  runtimeStatus="Running")
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}instances/{TEST_INSTANCE_ID}",
                               response=[200, status])
    client = DurableOrchestrationClient(binding_string)
    client._get_async_request = mock_request.get

    with pytest.raises(Exception):
        await client.wait_for_completion_or_create_check_status_response(
            None, TEST_INSTANCE_ID, timeout_in_milliseconds=500)

@pytest.mark.asyncio
async def test_start_new_orchestrator_not_found(binding_string):
    """Test that we throw the right exception when the orchestrator is not found.
    """
    status = dict(ExceptionMessage=EXCEPTION_ORCHESTRATOR_NOT_FOUND_EXMESSAGE,
                  StackTrace=STACK_TRACE,
                  Message=EXCEPTION_ORCHESTRATOR_NOT_FOUND_MESSAGE,
                  ExceptionType=EXCEPTION_TYPE_ORCHESTRATOR_NOT_FOUND)
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}orchestrators/{TEST_ORCHESTRATOR}",
                               response=[400, status])
    client = DurableOrchestrationClient(binding_string)
    client._post_async_request = mock_request.post

    with pytest.raises(Exception) as ex:
        await client.start_new(TEST_ORCHESTRATOR)
    ex.match(EXCEPTION_ORCHESTRATOR_NOT_FOUND_EXMESSAGE)


@pytest.mark.asyncio
async def test_start_new_orchestrator_internal_exception(binding_string):
    """Test that we throw the right exception when the extension fails internally.
    """
    status = dict(ExceptionMessage=EXCEPTION_ORCHESTRATOR_NOT_FOUND_EXMESSAGE,
                  StackTrace=STACK_TRACE,
                  Message=EXCEPTION_ORCHESTRATOR_NOT_FOUND_MESSAGE,
                  ExceptionType=EXCEPTION_TYPE_ORCHESTRATOR_NOT_FOUND)
    mock_request = MockRequest(expected_url=f"{RPC_BASE_URL}orchestrators/{TEST_ORCHESTRATOR}",
                               response=[500, status])
    client = DurableOrchestrationClient(binding_string)
    client._post_async_request = mock_request.post

    status_str = str(status)
    with pytest.raises(Exception) as ex:
        await client.start_new(TEST_ORCHESTRATOR)
    ex.match(status_str)

@pytest.mark.asyncio
async def test_rewind_works_under_200_and_200_http_codes(binding_string):
    """Tests that the rewind API works as expected under 'successful' http codes: 200, 202"""
    client = DurableOrchestrationClient(binding_string)
    for code in [200, 202]:
        mock_request = MockRequest(
            expected_url=f"{RPC_BASE_URL}instances/{INSTANCE_ID}/rewind?reason={REASON}",
            response=[code, ""])
        client._post_async_request = mock_request.post
        result = await client.rewind(INSTANCE_ID, REASON)
        assert result is None

@pytest.mark.asyncio
async def test_rewind_throws_exception_during_404_410_and_500_errors(binding_string):
    """Tests the behaviour of rewind under 'exception' http codes: 404, 410, 500"""
    client = DurableOrchestrationClient(binding_string)
    codes = [404, 410, 500]
    exception_strs = [
        f"No instance with ID {INSTANCE_ID} found.",
        "The rewind operation is only supported on failed orchestration instances.",
        "Something went wrong"
    ]
    for http_code, expected_exception_str in zip(codes, exception_strs):
        mock_request = MockRequest(
            expected_url=f"{RPC_BASE_URL}instances/{INSTANCE_ID}/rewind?reason={REASON}",
            response=[http_code, "Something went wrong"])
        client._post_async_request = mock_request.post

        with pytest.raises(Exception) as ex:
            await client.rewind(INSTANCE_ID, REASON)
        ex_message = str(ex.value)
        assert ex_message == expected_exception_str

@pytest.mark.asyncio
async def test_rewind_with_no_rpc_endpoint(binding_string):
    """Tests the behaviour of rewind without an RPC endpoint / under the legacy HTTP endpoint."""
    client = DurableOrchestrationClient(binding_string)
    mock_request = MockRequest(
        expected_url=f"{RPC_BASE_URL}instances/{INSTANCE_ID}/rewind?reason={REASON}",
        response=[-1, ""])
    client._post_async_request = mock_request.post  
    client._orchestration_bindings._rpc_base_url = None
    expected_exception_str = "The Python SDK only supports RPC endpoints."\
        + "Please remove the `localRpcEnabled` setting from host.json"
    with pytest.raises(Exception) as ex:
        await client.rewind(INSTANCE_ID, REASON)
    ex_message = str(ex.value)
    assert ex_message == expected_exception_str
