from uuid import uuid1
from typing import List, Any, Dict
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.constants import DATETIME_STRING_FORMAT


def history_list() -> List[Dict[Any, Any]]:
    history = [{'EventType': 12, 'EventId': -1, 'IsPlayed': False,
                'Timestamp': '2019-12-08T23:18:41.3240927Z'}, {
                   'OrchestrationInstance': {'InstanceId': '48d0f95957504c2fa579e810a390b938',
                                             'ExecutionId': 'fd183ee02e4b4fd18c95b773cfb5452b'},
                   'EventType': 0, 'ParentInstance': None, 'Name': 'DurableOrchestratorTrigger',
                   'Version': '', 'Input': 'null', 'Tags': None, 'EventId': -1, 'IsPlayed': False,
                   'Timestamp': '2019-12-08T23:18:39.756132Z'}]
    return history


def test_new_uuid():
    instance_id = str(uuid1())
    history = history_list()
    context1 = DurableOrchestrationContext(history, instance_id, False, None)

    result1a = context1.new_uuid()
    result1b = context1.new_uuid()

    context2 = DurableOrchestrationContext(history, instance_id, False, None)

    result2a = context2.new_uuid()
    result2b = context2.new_uuid()

    assert result1a == result2a
    assert result1b == result2b

    assert result1a != result1b
    assert result2a != result2b