#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.

from azure.functions.decorators.core import Setting

FUNCTION_NAME = "function_name"


class FunctionName(Setting):

    def __init__(self, function_name: str,
                 **kwargs):
        self.function_name = function_name
        super().__init__(setting_name=FUNCTION_NAME)
