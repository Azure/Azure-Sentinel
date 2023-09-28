#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import EVENT_HUB_TRIGGER, EVENT_HUB
from azure.functions.decorators.core import Trigger, DataType, OutputBinding, \
    Cardinality


class EventHubTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return EVENT_HUB_TRIGGER

    def __init__(self,
                 name: str,
                 connection: str,
                 event_hub_name: str,
                 data_type: Optional[DataType] = None,
                 cardinality: Optional[Cardinality] = None,
                 consumer_group: Optional[str] = None,
                 **kwargs):
        self.connection = connection
        self.event_hub_name = event_hub_name
        self.cardinality = cardinality
        self.consumer_group = consumer_group
        super().__init__(name=name, data_type=data_type)


class EventHubOutput(OutputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return EVENT_HUB

    def __init__(self,
                 name: str,
                 connection: str,
                 event_hub_name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.connection = connection
        self.event_hub_name = event_hub_name
        super().__init__(name=name, data_type=data_type)
