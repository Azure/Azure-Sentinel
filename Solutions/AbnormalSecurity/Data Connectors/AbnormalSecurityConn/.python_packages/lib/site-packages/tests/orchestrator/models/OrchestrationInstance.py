import uuid
from typing import Any, Dict

from tests.test_utils.json_utils import add_attrib


class OrchestrationInstance:
    def __init__(self):
        self.instance_id: str = str(uuid.uuid4())
        self.execution_id: str = str(uuid.uuid4())

    def to_json(self) -> Dict[str, Any]:
        json_dict = {}

        add_attrib(json_dict, self, 'instance_id', 'InstanceId')
        add_attrib(json_dict, self, 'execution_id', 'ExecutionId')

        return json_dict
