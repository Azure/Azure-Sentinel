#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import SQL, SQL_TRIGGER
from azure.functions.decorators.core import DataType, InputBinding, \
    OutputBinding, Trigger


class SqlInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return SQL

    def __init__(self,
                 name: str,
                 command_text: str,
                 connection_string_setting: str,
                 command_type: Optional[str] = 'Text',
                 parameters: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.command_text = command_text
        self.connection_string_setting = connection_string_setting
        self.command_type = command_type
        self.parameters = parameters
        super().__init__(name=name, data_type=data_type)


class SqlOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return SQL

    def __init__(self,
                 name: str,
                 command_text: str,
                 connection_string_setting: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.command_text = command_text
        self.connection_string_setting = connection_string_setting
        super().__init__(name=name, data_type=data_type)


class SqlTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return SQL_TRIGGER

    def __init__(self,
                 name: str,
                 table_name: str,
                 connection_string_setting: str,
                 leases_table_name: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.table_name = table_name
        self.connection_string_setting = connection_string_setting
        self.leases_table_name = leases_table_name
        super().__init__(name=name, data_type=data_type)
