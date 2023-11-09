from typing import List, Optional, Any
from ..utils.entity_utils import EntityId
import json


class RequestMessage:
    """RequestMessage.

    Specifies a request to an entity.
    """

    def __init__(self,
                 id_: str,
                 name: Optional[str] = None,
                 signal: Optional[bool] = None,
                 input_: Optional[str] = None,
                 arg: Optional[Any] = None,
                 parent: Optional[str] = None,
                 lockset: Optional[List[EntityId]] = None,
                 pos: Optional[int] = None,
                 **kwargs):
        # TODO: this class has too many optionals, may speak to
        # over-caution, but it mimics the JS class. Investigate if
        # these many Optionals are necessary.
        self.id = id_
        self.name = name
        self.signal = signal
        self.input = input_
        self.arg = arg
        self.parent = parent
        self.lockset = lockset
        self.pos = pos

    @classmethod
    def from_json(cls, json_str: str) -> 'RequestMessage':
        """Instantiate a RequestMessage object from the durable-extension provided JSON data.

        Parameters
        ----------
        json_str: str
            A durable-extension provided json-formatted string representation of
            a RequestMessage

        Returns
        -------
        RequestMessage:
            A RequestMessage object from the json_str parameter
        """
        # We replace the `id` key for `id_` to avoid clashes with reserved
        # identifiers in Python
        json_dict = json.loads(json_str)
        json_dict["id_"] = json_dict.pop("id")
        return cls(**json_dict)
