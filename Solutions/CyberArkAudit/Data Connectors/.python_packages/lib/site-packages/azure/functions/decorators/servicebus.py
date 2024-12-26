#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import SERVICE_BUS_TRIGGER, \
    SERVICE_BUS
from azure.functions.decorators.core import Trigger, OutputBinding, DataType, \
    Cardinality, AccessRights


class ServiceBusQueueTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return SERVICE_BUS_TRIGGER

    def __init__(self,
                 name: str,
                 connection: str,
                 queue_name: str,
                 data_type: Optional[DataType] = None,
                 access_rights: Optional[AccessRights] = None,
                 is_sessions_enabled: Optional[bool] = None,
                 cardinality: Optional[Cardinality] = None,
                 **kwargs):
        self.connection = connection
        self.queue_name = queue_name
        self.access_rights = access_rights
        self.is_sessions_enabled = is_sessions_enabled
        self.cardinality = cardinality
        super().__init__(name=name, data_type=data_type)


class ServiceBusQueueOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return SERVICE_BUS

    def __init__(self,
                 name: str,
                 connection: str,
                 queue_name: str,
                 data_type: Optional[DataType] = None,
                 access_rights: Optional[AccessRights] = None,
                 **kwargs):
        self.connection = connection
        self.queue_name = queue_name
        self.access_rights = access_rights
        super().__init__(name=name, data_type=data_type)


class ServiceBusTopicTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return SERVICE_BUS_TRIGGER

    def __init__(self,
                 name: str,
                 connection: str,
                 topic_name: str,
                 subscription_name: str,
                 data_type: Optional[DataType] = None,
                 access_rights: Optional[AccessRights] = None,
                 is_sessions_enabled: Optional[bool] = None,
                 cardinality: Optional[Cardinality] = None,
                 **kwargs):
        self.connection = connection
        self.topic_name = topic_name
        self.subscription_name = subscription_name
        self.access_rights = access_rights
        self.is_sessions_enabled = is_sessions_enabled
        self.cardinality = cardinality
        super().__init__(name=name, data_type=data_type)


class ServiceBusTopicOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return SERVICE_BUS

    def __init__(self,
                 name: str,
                 connection: str,
                 topic_name: str,
                 subscription_name: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 access_rights: Optional[AccessRights] = None,
                 **kwargs):
        self.connection = connection
        self.topic_name = topic_name
        self.subscription_name = subscription_name
        self.access_rights = access_rights
        super().__init__(name=name, data_type=data_type)
