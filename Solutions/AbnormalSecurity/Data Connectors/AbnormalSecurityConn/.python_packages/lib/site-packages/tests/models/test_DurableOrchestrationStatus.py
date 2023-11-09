from datetime import datetime
from typing import Dict, Any

from dateutil.parser import parse as dt_parse

from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from azure.durable_functions.models.DurableOrchestrationStatus import DurableOrchestrationStatus
from azure.durable_functions.models.OrchestrationRuntimeStatus import OrchestrationRuntimeStatus
from azure.durable_functions.models.history import HistoryEventType

TEST_NAME = 'what ever I want it to be'
TEST_INSTANCE_ID = '2e2568e7-a906-43bd-8364-c81733c5891e'
TEST_CREATED_TIME = '2020-01-01T05:00:00Z'
TEST_LAST_UPDATED_TIME = '2020-01-01T05:00:00Z'
TEST_INPUT = 'My Input'
TEST_OUTPUT = 'My Output'
TEST_RUNTIME_STATUS = "Running"
TEST_CUSTOM_STATUS = "My Custom Status"


def get_event(
        event_type: HistoryEventType, id_: int = -1,
        is_played: bool = False, timestamp=None) -> Dict[str, Any]:
    if not timestamp:
        timestamp = datetime.now()
    event = dict(EventType=event_type, EventId=id_, IsPlayed=is_played,
                 Timestamp=timestamp.strftime(DATETIME_STRING_FORMAT))
    return event


def test_all_the_args():
    orchestration_started = get_event(HistoryEventType.ORCHESTRATOR_STARTED)
    execution_started = get_event(HistoryEventType.EXECUTION_STARTED)
    history = [orchestration_started, execution_started]
    response = dict(name=TEST_NAME, instanceId=TEST_INSTANCE_ID, createdTime=TEST_CREATED_TIME,
                    lastUpdatedTime=TEST_LAST_UPDATED_TIME, input=TEST_INPUT, output=TEST_OUTPUT,
                    runtimeStatus=TEST_RUNTIME_STATUS, customStatus=TEST_CUSTOM_STATUS,
                    history=history)

    result = DurableOrchestrationStatus.from_json(response)

    assert result.runtime_status.name == TEST_RUNTIME_STATUS
    assert result.custom_status == TEST_CUSTOM_STATUS
    assert result.instance_id == TEST_INSTANCE_ID
    assert result.output == TEST_OUTPUT
    assert result.created_time == dt_parse(TEST_CREATED_TIME)
    assert result.last_updated_time == dt_parse(TEST_LAST_UPDATED_TIME)
    assert result.input_ == TEST_INPUT
    assert result.name == TEST_NAME
    assert result.history[0]['EventType'] == HistoryEventType.ORCHESTRATOR_STARTED
    assert result.history[1]['EventType'] == HistoryEventType.EXECUTION_STARTED


def test_no_args():
    response = ''

    result = DurableOrchestrationStatus.from_json(response)

    assert result is not None
