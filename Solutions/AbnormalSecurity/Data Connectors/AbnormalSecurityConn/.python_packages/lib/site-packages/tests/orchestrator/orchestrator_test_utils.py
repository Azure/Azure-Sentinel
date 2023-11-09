import json
from typing import Callable, Iterator, Any, Dict, List
from jsonschema import validate

from azure.durable_functions.models import DurableOrchestrationContext, DurableEntityContext
from azure.durable_functions.orchestrator import Orchestrator
from azure.durable_functions.entity import Entity
from .schemas.OrchetrationStateSchema import schema


def assert_orchestration_state_equals(expected, result):
    """Ensure that the observable OrchestratorState matches the expected result.
    """
    assert_attribute_equal(expected, result, "isDone")
    assert_attribute_equal(expected, result, "schemaVersion")
    assert_actions_are_equal(expected, result)
    assert_attribute_equal(expected, result, "output")
    assert_attribute_equal(expected, result, "error")
    assert_attribute_equal(expected, result, "customStatus")

def assert_entity_state_equals(expected, result):
    """Ensure the that the observable EntityState json matches the expected result.
    """
    assert_attribute_equal(expected, result,"entityExists")
    assert "results" in result
    observed_results = result["results"]
    expected_results = expected["results"]
    assert_results_are_equal(expected_results, observed_results)
    assert_attribute_equal(expected, result, "entityState")
    assert_attribute_equal(expected, result, "signals")

def assert_results_are_equal(expected: Dict[str, Any], result: Dict[str, Any]) -> bool:
    assert_attribute_equal(expected, result, "result")
    assert_attribute_equal(expected, result, "isError")

def assert_attribute_equal(expected, result, attribute):
    if attribute in expected:
        assert result.get(attribute) == expected.get(attribute)
    else:
        assert attribute not in result


def assert_actions_are_equal(expected, result):
    expected_actions = expected.get("actions")
    result_actions = result.get("actions")
    assert len(expected_actions) == len(result_actions)
    for index in range(len(expected_actions)):
        assert len(expected_actions[index]) == len(result_actions[index])
        for action_index in range(len(expected_actions[index])):
            expected_action = expected_actions[index][action_index]
            result_action = result_actions[index][action_index]
            assert_action_is_equal(expected_action, result_action)


def assert_action_is_equal(expected_action, result_action):
    assert_attribute_equal(expected_action, result_action, "functionName")
    assert_attribute_equal(expected_action, result_action, "input")
    assert_attribute_equal(expected_action, result_action, "actionType")


def get_orchestration_state_result(
        context_builder,
        activity_func: Callable[[DurableOrchestrationContext], Iterator[Any]]):
    context_as_string = context_builder.to_json_string()
    orchestrator = Orchestrator(activity_func)
    result_of_handle = orchestrator.handle(
        DurableOrchestrationContext.from_json(context_as_string))
    result = json.loads(result_of_handle)
    return result

def get_entity_state_result(
        context_builder: DurableEntityContext,
        user_code: Callable[[DurableEntityContext], Any],
        ) -> Dict[str, Any]:
    """Simulate the result of running the entity function with the provided context and batch.

    Parameters
    ----------
    context_builder: DurableEntityContext
        A mocked entity context
    user_code: Callable[[DurableEntityContext], Any]
        A function implementing an entity

    Returns:
    -------
    Dict[str, Any]:
        JSON-response of the entity
    """
    # The durable-extension automatically wraps the data within a 'self' key
    context_as_string = context_builder.to_json_string()
    entity = Entity(user_code)

    context, batch = DurableEntityContext.from_json(context_as_string)
    result_of_handle = entity.handle(context, batch)
    result = json.loads(result_of_handle)
    return result

def get_orchestration_property(
        context_builder,
        activity_func: Callable[[DurableOrchestrationContext], Iterator[Any]],
        prop: str):
    context_as_string = context_builder.to_json_string()
    orchestrator = Orchestrator(activity_func)
    result_of_handle = orchestrator.handle(
        DurableOrchestrationContext.from_json(context_as_string))
    result = getattr(orchestrator, prop)
    return result


def assert_valid_schema(orchestration_state):
    validation_results = validate(instance=orchestration_state, schema=schema)
    assert validation_results is None


def assert_dict_are_equal(expected: Dict[Any, Any], result: Dict[Any, Any]):
    assert len(expected.keys()) == len(result.keys())
    for key in expected.keys():
        assert expected[key] == result[key]
    for key in result.keys():
        assert result[key] == expected[key]
