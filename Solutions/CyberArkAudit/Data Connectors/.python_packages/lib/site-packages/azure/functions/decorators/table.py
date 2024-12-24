#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import TABLE
from azure.functions.decorators.core import DataType, OutputBinding, \
    InputBinding


class TableInput(InputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return TABLE

    def __init__(self,
                 name: str,
                 connection: str,
                 table_name: str,
                 row_key: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 take: Optional[int] = None,
                 filter: Optional[str] = None,
                 data_type: Optional[DataType] = None):
        self.connection = connection
        self.table_name = table_name
        self.row_key = row_key
        self.partition_key = partition_key
        self.take = take
        self.filter = filter
        super().__init__(name=name, data_type=data_type)


class TableOutput(OutputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return TABLE

    def __init__(self,
                 name: str,
                 connection: str,
                 table_name: str,
                 row_key: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 data_type: Optional[DataType] = None):
        self.connection = connection
        self.table_name = table_name
        self.row_key = row_key
        self.partition_key = partition_key
        super().__init__(name=name, data_type=data_type)
