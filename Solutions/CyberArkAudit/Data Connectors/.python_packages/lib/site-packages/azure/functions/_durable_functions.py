# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Union
from . import _abc
from importlib import import_module


# Utilities
def _serialize_custom_object(obj):
    """Serialize a user-defined object to JSON.

    This function gets called when `json.dumps` cannot serialize
    an object and returns a serializable dictionary containing enough
    metadata to recontrust the original object.

    Parameters
    ----------
    obj: Object
        The object to serialize

    Returns
    -------
    dict_obj: A serializable dictionary with enough metadata to reconstruct
              `obj`

    Exceptions
    ----------
    TypeError:
        Raise if `obj` does not contain a `to_json` attribute
    """
    # 'safety' guard: raise error if object does not
    # support serialization
    if not hasattr(obj, "to_json"):
        raise TypeError(f"class {type(obj)} does not expose a `to_json` "
                        "function")
    # Encode to json using the object's `to_json`
    obj_type = type(obj)
    return {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__,
        "__data__": obj_type.to_json(obj)
    }


def _deserialize_custom_object(obj: dict) -> object:
    """Deserialize a user-defined object from JSON.

    Deserializes a dictionary encoding a custom object,
    if it contains class metadata suggesting that it should be
    decoded further.

    Parameters:
    ----------
    obj: dict
        Dictionary object that potentially encodes a custom class

    Returns:
    --------
    object
        Either the original `obj` dictionary or the custom object it encoded

    Exceptions
    ----------
    TypeError
        If the decoded object does not contain a `from_json` function
    """
    if ("__class__" in obj) and ("__module__" in obj) and ("__data__" in obj):
        class_name = obj.pop("__class__")
        module_name = obj.pop("__module__")
        obj_data = obj.pop("__data__")

        # Importing the clas
        module = import_module(module_name)
        class_ = getattr(module, class_name)

        if not hasattr(class_, "from_json"):
            raise TypeError(f"class {type(obj)} does not expose a `from_json` "
                            "function")

        # Initialize the object using its `from_json` deserializer
        obj = class_.from_json(obj_data)
    return obj


class OrchestrationContext(_abc.OrchestrationContext):
    """A durable function orchestration context.

    :param str body:
        The body of orchestration context json.
    """

    def __init__(self,
                 body: Union[str, bytes]) -> None:
        if isinstance(body, str):
            self.__body = body
        if isinstance(body, bytes):
            self.__body = body.decode('utf-8')

    @property
    def body(self) -> str:
        return self.__body

    def __repr__(self):
        return (
            f'<azure.OrchestrationContext '
            f'body={self.body}>'
        )

    def __str__(self):
        return self.__body


class EntityContext(_abc.OrchestrationContext):
    """A durable function entity context.

    :param str body:
        The body of orchestration context json.
    """

    def __init__(self,
                 body: Union[str, bytes]) -> None:
        if isinstance(body, str):
            self.__body = body
        if isinstance(body, bytes):
            self.__body = body.decode('utf-8')

    @property
    def body(self) -> str:
        return self.__body

    def __repr__(self):
        return (
            f'<azure.EntityContext '
            f'body={self.body}>'
        )

    def __str__(self):
        return self.__body
