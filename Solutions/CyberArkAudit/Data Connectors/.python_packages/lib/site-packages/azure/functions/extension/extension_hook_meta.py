# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Callable, NamedTuple


class ExtensionHookMeta(NamedTuple):
    """The metadata of a single life-cycle hook.
    The ext_name has the class name of an extension class.
    The ext_impl has the callable function that is used by the worker.
    """
    ext_name: str
    ext_impl: Callable

    # When adding more fields, make sure they have default values (e.g.
    # ext_new_field: Optional[str] = None
