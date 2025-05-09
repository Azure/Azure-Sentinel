# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing

from . import meta


class WarmUpContext:
    pass


class WarmUpTriggerConverter(meta.InConverter, binding='warmupTrigger',
                             trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, WarmUpContext)

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> typing.Any:
        return WarmUpContext()
