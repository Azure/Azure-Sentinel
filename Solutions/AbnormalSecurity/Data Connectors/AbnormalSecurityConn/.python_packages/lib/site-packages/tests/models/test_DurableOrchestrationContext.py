import pytest
import json
from dateutil.parser import parse as dt_parse
from azure.durable_functions.models.ReplaySchema import ReplaySchema

from azure.durable_functions.models.DurableOrchestrationContext \
    import DurableOrchestrationContext
from tests.test_utils.ContextBuilder import ContextBuilder


@pytest.fixture
def starting_context():
    context = DurableOrchestrationContext.from_json(
        '{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,'
        '"Timestamp":"2019-12-08T23:18:41.3240927Z"}, '
        '{"OrchestrationInstance":{'
        '"InstanceId":"48d0f95957504c2fa579e810a390b938", '
        '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},"EventType":0,'
        '"ParentInstance":null, '
        '"Name":"DurableOrchestratorTrigger","Version":"","Input":"null",'
        '"Tags":null,"EventId":-1,"IsPlayed":false, '
        '"Timestamp":"2019-12-08T23:18:39.756132Z"}],"input":null,'
        '"instanceId":"48d0f95957504c2fa579e810a390b938", '
        '"isReplaying":false,"parentInstanceId":null} ')
    return context

@pytest.fixture
def starting_context_v2():
    context = DurableOrchestrationContext.from_json(
        '{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,'
        '"Timestamp":"2019-12-08T23:18:41.3240927Z"}, '
        '{"OrchestrationInstance":{'
        '"InstanceId":"48d0f95957504c2fa579e810a390b938", '
        '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},"EventType":0,'
        '"ParentInstance":null, '
        '"Name":"DurableOrchestratorTrigger","Version":"","Input":"null",'
        '"Tags":null,"EventId":-1,"IsPlayed":false, '
        '"Timestamp":"2019-12-08T23:18:39.756132Z"}],"input":null,'
        '"instanceId":"48d0f95957504c2fa579e810a390b938", '
        '"upperSchemaVersion": 1, '
        '"isReplaying":false,"parentInstanceId":null} ')
    return context


def test_extracts_is_replaying(starting_context):
    assert not starting_context.is_replaying

def test_assumes_v1_replayschema(starting_context):
    assert starting_context._replay_schema is ReplaySchema.V1

def test_assumes_v2_replayschema(starting_context_v2):
    assert starting_context_v2._replay_schema is ReplaySchema.V2

def test_extracts_instance_id(starting_context):
    assert "48d0f95957504c2fa579e810a390b938" == starting_context.instance_id


def test_sets_current_utc_datetime(starting_context):
    assert \
        dt_parse("2019-12-08T23:18:41.3240927Z") == \
        starting_context.current_utc_datetime


def test_extracts_histories(starting_context):
    assert 2 == len(starting_context.histories)


def test_added_function_context_args():
    context_builder = ContextBuilder('test_function_context')

    additional_attributes = {"attrib1": 1, "attrib2": "two",
                             "attrib3": {"randomDictionary": "random"}}

    context_as_string = context_builder.to_json_string(**additional_attributes)

    durable_context = DurableOrchestrationContext.from_json(context_as_string)

    assert durable_context.function_context is not None
    for key in additional_attributes:
        assert additional_attributes[key] == getattr(durable_context.function_context, key)


def test_get_input_none(starting_context):
    test = starting_context.get_input()
    assert None == test


def test_get_input_string():
    builder = ContextBuilder('test_function_context')
    builder.input_ = json.dumps('Seattle')
    context = DurableOrchestrationContext.from_json(builder.to_json_string())
    assert 'Seattle' == context.get_input()


def test_get_input_json_str():
    builder = ContextBuilder('test_function_context')
    builder.input_ = json.dumps({ 'city': 'Seattle' })
    context = DurableOrchestrationContext.from_json(builder.to_json_string())

    result = context.get_input()

    assert 'Seattle' == result['city']
