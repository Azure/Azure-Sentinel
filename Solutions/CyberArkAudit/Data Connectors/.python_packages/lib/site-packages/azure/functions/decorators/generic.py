#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Trigger, \
    InputBinding, OutputBinding, DataType


class GenericInputBinding(InputBinding):

    @staticmethod
    def get_binding_name():
        pass

    def __init__(self,
                 name: str,
                 type: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        super().__init__(name=name, data_type=data_type, type=type)


class GenericOutputBinding(OutputBinding):

    @staticmethod
    def get_binding_name():
        pass

    def __init__(self,
                 name: str,
                 type: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        super().__init__(name=name, data_type=data_type, type=type)


class GenericTrigger(Trigger):

    @staticmethod
    def get_binding_name():
        pass

    def __init__(self,
                 name: str,
                 type: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        super().__init__(name=name, data_type=data_type, type=type)
