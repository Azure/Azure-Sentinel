# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import NamedTuple, List
from .extension_hook_meta import ExtensionHookMeta


class AppExtensionHooks(NamedTuple):
    """The definition of which type of global hooks are supported in SDK.
    ExtensionMeta will lookup the AppExtension life-cycle type from here.
    """
    # The default value ([] empty list) is not being set here intentionally
    # since it is impacted by a Python bug https://bugs.python.org/issue33077.
    post_function_load_app_level: List[ExtensionHookMeta]
    pre_invocation_app_level: List[ExtensionHookMeta]
    post_invocation_app_level: List[ExtensionHookMeta]
