import json
from typing import Any, List, Dict, Any

class EntityContextBuilder():
    """Mock class for an EntityContext object, includes a batch field for convenience
    """
    def __init__(self,
                 name: str = "",
                 key: str = "",
                 exists: bool = True,
                 state: Any = None,
                 batch: List[Dict[str, Any]] = []):
        """Construct an EntityContextBuilder

        Parameters
        ----------
        name: str:
            The name of the entity. Defaults to the empty string.
        key: str
            The key of the entity. Defaults to the empty string.
        exists: bool
            Boolean representing if the entity exists, defaults to True.
        state: Any
            The state of the entity, defaults ot None.
        batch: List[Dict[str, Any]]
            The upcoming batch of operations for the entity to perform.
            Note that the batch is not technically a part of the entity context
            and so it is here only for convenience. Defaults to the empty list.
        """
        self.name = name
        self.key = key
        self.exists = exists
        self.state = state
        self.batch = batch
    
    def to_json_string(self) -> str:
        """Generate a string-representation of the Entity input payload.

        The payload matches the current durable-extension entity-communication
        schema.

        Returns
        -------
        str:
            A JSON-formatted string for an EntityContext to load via `from_json`
        """
        context_json = {
            "self": {
                "name": self.name,
                "key": self.key
            },
            "state": self.state,
            "exists": self.exists,
            "batch": self.batch
        }
        json_string = json.dumps(context_json)
        return json_string