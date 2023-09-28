# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import NamedTuple, List
from .extension_hook_meta import ExtensionHookMeta


class FuncExtensionHooks(NamedTuple):
    """The definition of which type of function hooks are supported in SDK.
    ExtensionMeta will lookup the FuncExtension life-cycle type from here.
    """
    # The default value ([] empty list) is not being set here intentionally
    # since it is impacted by a Python bug https://bugs.python.org/issue33077.
    post_function_load: List[ExtensionHookMeta]
    pre_invocation: List[ExtensionHookMeta]
    post_invocation: List[ExtensionHookMeta]
