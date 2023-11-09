from tests.conftest import TASK_HUB_NAME, replace_stand_in_bits


def test_extracts_task_hub_name(binding_info):
    assert TASK_HUB_NAME == binding_info.task_hub_name


def test_extracts_create_new_instance_post_uri(binding_info):
    expected_url = replace_stand_in_bits(
        "BASE_URL/orchestrators/{functionName}[/{instanceId}]?code=AUTH_CODE")
    assert \
        expected_url == binding_info.creation_urls["createNewInstancePostUri"]


def test_extracts_create_and_wait_on_new_instance_post_uri(binding_info):
    expected_url = replace_stand_in_bits(
        "BASE_URL/orchestrators/{functionName}[/{instanceId}]?timeout={"
        "timeoutInSeconds}&pollingInterval={intervalInSeconds}&code=AUTH_CODE")
    assert expected_url == binding_info.creation_urls[
        "createAndWaitOnNewInstancePostUri"]


def test_extracts_status_query_get_uri(binding_info):
    expected_url = replace_stand_in_bits(
        "BASE_URL/instances/INSTANCEID?taskHub=TASK_HUB_NAME&connection"
        "=Storage&code=AUTH_CODE")
    assert expected_url == binding_info.management_urls["statusQueryGetUri"]


def test_extracts_send_event_post_uri(binding_info):
    expected_url = replace_stand_in_bits(
        "BASE_URL/instances/INSTANCEID/raiseEvent/{"
        "eventName}?taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE")
    assert expected_url == binding_info.management_urls["sendEventPostUri"]


def test_extracts_terminate_post_uri(binding_info):
    expected_url = replace_stand_in_bits(
        "BASE_URL/instances/INSTANCEID/terminate?reason={"
        "text}&taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE")
    assert expected_url == binding_info.management_urls["terminatePostUri"]


def test_extracts_rewind_post_uri(binding_info):
    expected_url = replace_stand_in_bits(
        "BASE_URL/instances/INSTANCEID/rewind?reason={"
        "text}&taskHub=TASK_HUB_NAME&connection=Storage&code=AUTH_CODE")
    assert expected_url == binding_info.management_urls["rewindPostUri"]


def test_extracts_purge_history_delete_uri(binding_info):
    expected_url = replace_stand_in_bits(
        "BASE_URL/instances/INSTANCEID?taskHub=TASK_HUB_NAME&connection"
        "=Storage&code=AUTH_CODE")
    assert expected_url == binding_info.management_urls[
        "purgeHistoryDeleteUri"]
