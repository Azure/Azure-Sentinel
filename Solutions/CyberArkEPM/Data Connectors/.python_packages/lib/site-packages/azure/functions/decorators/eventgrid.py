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
                 topic_endpoint_uri: Optional[str] = None,
                 topic_key_setting: Optional[str] = None,
                 connection: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        if (connection is not None and (
                topic_endpoint_uri is not None
                or topic_key_setting is not None)) or \
                (connection is None and (
                topic_endpoint_uri is None
                or topic_key_setting is None)):
            raise ValueError(
                "Specify either the 'Connection' property or both "
                "'TopicKeySetting' and 'TopicEndpointUri' properties,"
                " but not both.")

        self.topic_endpoint_uri = topic_endpoint_uri
        self.topic_key_setting = topic_key_setting
        self.connection = connection
        super().__init__(name=name, data_type=data_type)
