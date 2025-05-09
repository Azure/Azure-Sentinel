# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Optional, Iterable

from azure.functions.decorators.constants import HTTP_TRIGGER, HTTP_OUTPUT
from azure.functions.decorators.core import AuthLevel, Trigger, \
    OutputBinding, DataType, StringifyEnum


class HttpMethod(StringifyEnum):
    """All http methods Azure Python function supports."""
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    HEAD = "HEAD"
    PATCH = "PATCH"
    PUT = "PUT"
    OPTIONS = "OPTIONS"


class HttpTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return HTTP_TRIGGER

    def __init__(self,
                 name,
                 methods: Optional[Iterable[HttpMethod]] = None,
                 data_type: Optional[DataType] = None,
                 auth_level: Optional[AuthLevel] = None,
                 route: Optional[str] = None,
                 **kwargs) -> None:
        self.auth_level = auth_level
        self.methods = methods
        self.route = route
        super().__init__(name=name, data_type=data_type)


class HttpOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return HTTP_OUTPUT

    def __init__(self,
                 name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs) -> None:
        super().__init__(name=name, data_type=data_type)
