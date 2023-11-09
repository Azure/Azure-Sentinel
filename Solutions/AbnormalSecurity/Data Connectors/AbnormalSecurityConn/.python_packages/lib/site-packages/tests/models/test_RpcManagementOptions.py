from furl import furl
from datetime import datetime, timedelta

from azure.durable_functions.models import OrchestrationRuntimeStatus
from azure.durable_functions.models.RpcManagementOptions import RpcManagementOptions
from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from tests.test_utils.constants import RPC_BASE_URL


def assert_urls_match(expected, result):
    expected_url = furl(expected)
    result_url = furl(result)

    assert result_url.path == expected_url.path
    assert len(result_url.args) == len(expected_url.args)

    for arg in expected_url.args:
        assert expected_url.args[arg] == result_url.args[arg]


def test_just_instance_id():
    instance_id = 'test1234'
    options = RpcManagementOptions(instance_id=instance_id)
    result = options.to_url(RPC_BASE_URL)
    expected = f"{RPC_BASE_URL}instances/{instance_id}"
    assert_urls_match(expected=expected, result=result)


def test_instance_id_with_optional_booleans():
    instance_id = 'test1234'
    options = RpcManagementOptions(instance_id=instance_id, show_history=True,
                                   show_history_output=True, show_input=True)
    result = options.to_url(RPC_BASE_URL)
    expected = f"{RPC_BASE_URL}instances/{instance_id}?" \
               "showHistory=True&showHistoryOutput=True&showInput=True"

    assert_urls_match(expected=expected, result=result)


def test_just_the_strings():
    task_hub_name = 'my_hub'
    connection_name = 'my_connection'
    options = RpcManagementOptions(connection_name=connection_name, task_hub_name=task_hub_name)
    result = options.to_url(RPC_BASE_URL)
    expected = f"{RPC_BASE_URL}instances/?connectionName={connection_name}&taskHub={task_hub_name}"

    assert_urls_match(expected=expected, result=result)


def test_one_runtime_status():
    runtime_status = [OrchestrationRuntimeStatus.Running]
    options = RpcManagementOptions(runtime_status=runtime_status)
    result = options.to_url(RPC_BASE_URL)
    expected = f"{RPC_BASE_URL}instances/?runtimeStatus=Running"

    assert_urls_match(expected=expected, result=result)


def test_two_runtime_status():
    runtime_status = [OrchestrationRuntimeStatus.Running, OrchestrationRuntimeStatus.Completed]
    options = RpcManagementOptions(runtime_status=runtime_status)
    result = options.to_url(RPC_BASE_URL)
    expected = f"{RPC_BASE_URL}instances/?runtimeStatus=Running,Completed"

    assert_urls_match(expected=expected, result=result)


def test_datetime_status():
    created_time_from = datetime.now()
    created_time_to = created_time_from + timedelta(minutes=1)
    options = RpcManagementOptions(created_time_from=created_time_from,
                                   created_time_to=created_time_to)
    result = options.to_url(RPC_BASE_URL)
    from_as_string = created_time_from.strftime(DATETIME_STRING_FORMAT)
    to_as_string = created_time_to.strftime(DATETIME_STRING_FORMAT)
    expected = f"{RPC_BASE_URL}instances/?createdTimeFrom={from_as_string}" \
               f"&createdTimeTo={to_as_string}"

    assert_urls_match(expected=expected, result=result)
