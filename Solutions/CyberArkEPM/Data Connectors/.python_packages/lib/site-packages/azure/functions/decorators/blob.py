#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import BLOB_TRIGGER, BLOB
from azure.functions.decorators.core import BlobSource, Trigger, \
    OutputBinding, DataType, InputBinding


class BlobTrigger(Trigger):
    def __init__(self,
                 name: str,
                 path: str,
                 connection: str,
                 source: Optional[BlobSource] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.path = path
        self.connection = connection
        if isinstance(source, BlobSource):
            self.source = source.value
        else:
            self.source = source  # type: ignore
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name() -> str:
        return BLOB_TRIGGER


class BlobInput(InputBinding):
    def __init__(self,
                 name: str,
                 path: str,
                 connection: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.path = path
        self.connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name() -> str:
        return BLOB


class BlobOutput(OutputBinding):
    def __init__(self,
                 name: str,
                 path: str,
                 connection: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.path = path
        self.connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name() -> str:
        return BLOB
