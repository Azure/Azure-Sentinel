#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import DAPR_BINDING, DAPR_INVOKE, \
    DAPR_PUBLISH, DAPR_SECRET, DAPR_SERVICE_INVOCATION_TRIGGER, \
    DAPR_BINDING_TRIGGER, DAPR_STATE, DAPR_TOPIC_TRIGGER
from azure.functions.decorators.core import InputBinding, Trigger, DataType, \
    OutputBinding


class DaprServiceInvocationTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return DAPR_SERVICE_INVOCATION_TRIGGER

    def __init__(self,
                 name: str,
                 method_name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.method_name = method_name
        super().__init__(name=name, data_type=data_type)


class DaprBindingTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return DAPR_BINDING_TRIGGER

    def __init__(self,
                 name: str,
                 binding_name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.binding_name = binding_name
        super().__init__(name=name, data_type=data_type)


class DaprTopicTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return DAPR_TOPIC_TRIGGER

    def __init__(self,
                 name: str,
                 pub_sub_name: str,
                 topic: str,
                 route: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.pub_sub_name = pub_sub_name
        self.topic = topic
        self.route = route
        super().__init__(name=name, data_type=data_type)


class DaprStateInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return DAPR_STATE

    def __init__(self,
                 name: str,
                 state_store: str,
                 key: str,
                 dapr_address: Optional[str],
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.state_store = state_store
        self.key = key
        self.dapr_address = dapr_address
        super().__init__(name=name, data_type=data_type)


class DaprSecretInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return DAPR_SECRET

    def __init__(self,
                 name: str,
                 secret_store_name: str,
                 key: str,
                 metadata: str,
                 dapr_address: Optional[str],
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.secret_store_name = secret_store_name
        self.key = key
        self.metadata = metadata
        self.dapr_address = dapr_address
        super().__init__(name=name, data_type=data_type)


class DaprStateOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return DAPR_STATE

    def __init__(self,
                 name: str,
                 state_store: str,
                 key: str,
                 dapr_address: Optional[str],
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.state_store = state_store
        self.key = key
        self.dapr_address = dapr_address
        super().__init__(name=name, data_type=data_type)


class DaprInvokeOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return DAPR_INVOKE

    def __init__(self,
                 name: str,
                 app_id: str,
                 method_name: str,
                 http_verb: str,
                 dapr_address: Optional[str],
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.app_id = app_id
        self.method_name = method_name
        self.http_verb = http_verb
        self.dapr_address = dapr_address
        super().__init__(name=name, data_type=data_type)


class DaprPublishOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return DAPR_PUBLISH

    def __init__(self,
                 name: str,
                 pub_sub_name: str,
                 topic: str,
                 dapr_address: Optional[str],
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.pub_sub_name = pub_sub_name
        self.topic = topic
        self.dapr_address = dapr_address
        super().__init__(name=name, data_type=data_type)


class DaprBindingOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return DAPR_BINDING

    def __init__(self,
                 name: str,
                 binding_name: str,
                 operation: str,
                 dapr_address: Optional[str],
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.binding_name = binding_name
        self.operation = operation
        self.dapr_address = dapr_address
        super().__init__(name=name, data_type=data_type)
