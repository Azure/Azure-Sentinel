# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type

from .utils import to_camel_case, \
    ABCBuildDictMeta, StringifyEnum

SCRIPT_FILE_NAME = "function_app.py"


# Enums
class BindingDirection(StringifyEnum):
    """Direction of the binding used in function.json"""
    IN = 0
    """Input binding direction."""
    OUT = 1
    """Output binding direction."""
    INOUT = 2
    """Some bindings support a special binding direction. """


class DataType(StringifyEnum):
    """Data type of the binding used in function.json"""
    """Parse binding argument as undefined."""
    UNDEFINED = 0
    """Parse binding argument as string."""
    STRING = 1
    """Parse binding argument as binary."""
    BINARY = 2
    """Parse binding argument as stream."""
    STREAM = 3


class AuthLevel(StringifyEnum):
    """Azure HTTP authorization level, determines what keys, if any, need to
    be present on the request in order to invoke the function. """
    FUNCTION = "function"
    """A function-specific API key is required. This is the default value if
    none is provided. """
    ANONYMOUS = "anonymous"
    """No API key is required."""
    ADMIN = "admin"
    """The master key is required."""


class Cardinality(StringifyEnum):
    """Used for all non-C# languages. Set to many in order to enable
    batching. If omitted or set to one, a single message is passed to the
    function. """
    ONE = "one"
    """Singe message passed to the function."""
    MANY = "many"
    """Multiple messaged passed to the function per invocation."""


class AccessRights(StringifyEnum):
    """Access rights for the connection string. The default is manage,
    which indicates that the connection has the Manage permission. """
    MANAGE = "manage"
    """Confers the right to manage the topology of the namespace, including
    creating and deleting entities. """
    LISTEN = "listen"
    """Confers the right to listen (relay) or receive (queue, subscriptions)
    and all related message handling. """


class Binding(ABC):
    """Abstract binding class which captures common attributes and
    functions. :meth:`get_dict_repr` can auto generate the function.json for
    every binding, the only restriction is ***ENSURE*** __init__ parameter
    names of any binding class are snake case form of corresponding
    attribute in function.json when new binding classes are created.
    Ref: https://aka.ms/azure-function-binding-http """

    EXCLUDED_INIT_PARAMS = {'self', 'kwargs', 'type', 'data_type', 'direction'}

    @staticmethod
    @abstractmethod
    def get_binding_name() -> str:
        pass

    def __init__(self, name: str,
                 direction: BindingDirection,
                 data_type: Optional[DataType] = None,
                 type: Optional[str] = None):  # NoQa
        # For natively supported bindings, get_binding_name is always
        # implemented, and for generic bindings, type is a required argument
        # in decorator functions.
        self.type = self.get_binding_name() \
            if self.get_binding_name() is not None else type
        self.name = name
        self._direction = direction
        self._data_type = data_type
        self._dict = {
            "direction": self._direction,
            "dataType": self._data_type,
            "type": self.type
        }

    @property
    def data_type(self) -> Optional[int]:
        return self._data_type.value if self._data_type else None

    @property
    def direction(self) -> int:
        return self._direction.value

    def get_dict_repr(self) -> Dict:
        """Build a dictionary of a particular binding. The keys are camel
        cased binding field names defined in `init_params` list and
        :class:`Binding` class. \n
        This method is invoked in function :meth:`get_raw_bindings` of class
        :class:`Function` to generate json dict for each binding.

        :return: Dictionary representation of the binding.
        """
        params = list(dict.fromkeys(getattr(self, 'init_params', [])))
        for p in params:
            if p not in Binding.EXCLUDED_INIT_PARAMS:
                self._dict[to_camel_case(p)] = getattr(self, p, None)

        return self._dict


class Trigger(Binding, ABC, metaclass=ABCBuildDictMeta):
    """Class representation of Azure Function Trigger. \n
    Ref: https://aka.ms/functions-triggers-bindings-overview
    """

    @staticmethod
    def is_supported_trigger_type(trigger_instance: 'Trigger',
                                  trigger_type: Type['Trigger']):
        return isinstance(trigger_instance,
                          trigger_type) or trigger_instance.type == \
            trigger_type.get_binding_name()

    def __init__(self, name: str, data_type: Optional[DataType] = None,
                 type: Optional[str] = None) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name, data_type=data_type, type=type)


class InputBinding(Binding, ABC, metaclass=ABCBuildDictMeta):
    """Class representation of Azure Function Input Binding. \n
    Ref: https://aka.ms/functions-triggers-bindings-overview
    """

    def __init__(self, name: str, data_type: Optional[DataType] = None,
                 type: Optional[str] = None) -> None:
        super().__init__(direction=BindingDirection.IN,
                         name=name, data_type=data_type, type=type)


class OutputBinding(Binding, ABC, metaclass=ABCBuildDictMeta):
    """Class representation of Azure Function Output Binding. \n
    Ref: https://aka.ms/functions-triggers-bindings-overview
    """

    def __init__(self, name: str, data_type: Optional[DataType] = None,
                 type: Optional[str] = None) -> None:
        super().__init__(direction=BindingDirection.OUT,
                         name=name, data_type=data_type, type=type)


class Setting(ABC, metaclass=ABCBuildDictMeta):
    """ Abstract class for all settings of a function app.
        This class represents all the decorators that cannot be
        classified as bindings or triggers. e.g function_name, retry etc.
    """

    EXCLUDED_INIT_PARAMS = {'self', 'kwargs', 'setting_name'}

    def __init__(self, setting_name: str) -> None:
        self.setting_name = setting_name
        self._dict: Dict = {
            "setting_name": self.setting_name
        }

    def get_setting_name(self) -> str:
        return self.setting_name

    def get_dict_repr(self) -> Dict:
        """Build a dictionary of a particular binding. The keys are camel
        cased binding field names defined in `init_params` list and
        :class:`Binding` class. \n
        This method is invoked in function :meth:`get_raw_bindings` of class
        :class:`Function` to generate json dict for each binding.

        :return: Dictionary representation of the binding.
        """
        params = list(dict.fromkeys(getattr(self, 'init_params', [])))
        for p in params:
            if p not in Setting.EXCLUDED_INIT_PARAMS:
                self._dict[p] = getattr(self, p, None)

        return self._dict

    def get_settings_value(self, settings_attribute_key: str) -> Optional[str]:
        """
        Get the value of a particular setting attribute.
        """
        return self.get_dict_repr().get(settings_attribute_key)
