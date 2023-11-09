from azure.durable_functions.models.ReplaySchema import ReplaySchema
from typing import List

from azure.durable_functions.models.actions.Action import Action
from azure.durable_functions.models.actions.CallActivityAction \
    import CallActivityAction
from azure.durable_functions.models.OrchestratorState import OrchestratorState


def test_empty_state_to_json_string():
    actions: List[List[Action]] = []
    state = OrchestratorState(is_done=False, actions=actions, output=None, replay_schema=ReplaySchema.V1.value)
    result = state.to_json_string()
    expected_result = '{"isDone": false, "actions": []}'
    assert expected_result == result


def test_single_action_state_to_json_string():
    actions: List[List[Action]] = []
    action: Action = CallActivityAction(
        function_name="MyFunction", input_="AwesomeInput")
    actions.append([action])
    state = OrchestratorState(is_done=False, actions=actions, output=None, replay_schema=ReplaySchema.V1.value)
    result = state.to_json_string()
    expected_result = ('{"isDone": false, "actions": [[{"actionType": 0, '
                       '"functionName": "MyFunction", "input": '
                       '"\\"AwesomeInput\\""}]]}')
    assert expected_result == result
