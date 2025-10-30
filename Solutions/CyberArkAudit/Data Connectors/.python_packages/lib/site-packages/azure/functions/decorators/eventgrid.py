#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import EVENT_GRID, EVENT_GRID_TRIGGER
from azure.functions.decorators.core import Trigger, DataType, OutputBinding


class EventGridTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return EVENT_GRID_TRIGGER

    def __init__(self,
                 name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        super().__init__(name=name, data_type=data_type)


class EventGridOutput(OutputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return EVENT_GRID

    def __init__(self,
                 name: str,
                 topic_endpoint_uri: str,
                 topic_key_setting: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.topic_endpoint_uri = topic_endpoint_uri
        self.topic_key_setting = topic_key_setting
        super().__init__(name=name, data_type=data_type)
