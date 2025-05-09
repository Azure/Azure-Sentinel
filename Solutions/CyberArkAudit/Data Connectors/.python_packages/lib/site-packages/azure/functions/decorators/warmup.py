#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import WARMUP_TRIGGER
from azure.functions.decorators.core import Trigger, DataType


class WarmUpTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return WARMUP_TRIGGER

    def __init__(self,
                 name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs) -> None:
        super().__init__(name=name, data_type=data_type)
