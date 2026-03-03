# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Optional, Union, Dict, List
import abc
from .app_extension_hooks import AppExtensionHooks
from .func_extension_hooks import FuncExtensionHooks
from .extension_hook_meta import ExtensionHookMeta
from .extension_scope import ExtensionScope
from .function_extension_exception import FunctionExtensionException
from .._jsonutils import json


class ExtensionMeta(abc.ABCMeta):
    """The metaclass handles extension registration.

    AppExtension is registered in __init__, it is applied to all triggers.
    FuncExtension is registered in __call__, as users need to instantiate it
    inside hook script.

    After registration, the extension class will be flatten into the following
    structure to speed up worker lookup:
        _func_exts[<trigger_name>].<hook_name>.(ext_name, ext_impl)
        (e.g. _func_exts['HttpTrigger'].pre_invocation.ext_impl)

        _app_exts.<hook_name>.(ext_name, ext_impl)
        (e.g. _app_exts.pre_invocation_app_level.ext_impl)

    The extension tree information is stored in _info for diagnostic
    purpose. The dictionary is serializable to json:
        _info['FuncExtension']['<Trigger>'] = list(<Extension>)
        _info['AppExtension'] = list(<Extension>)
    """
    _func_exts: Dict[str, FuncExtensionHooks] = {}
    _app_exts: Optional[AppExtensionHooks] = None
    _info: Dict[str, Union[Dict[str, List[str]], List[str]]] = {}

    def __init__(cls, *args, **kwargs):
        """Executes on 'import extension', once the AppExtension class is
        loaded, call the setup() method and add the life-cycle hooks into
        _app_exts.
        """
        super(ExtensionMeta, cls).__init__(*args, **kwargs)
        scope = ExtensionMeta._get_extension_scope(cls)

        # Only register application extension here
        if scope is ExtensionScope.APPLICATION:
            ExtensionMeta._register_application_extension(cls)

    def __call__(cls, *args, **kwargs):
        """Executes on 'inst = extension(__file__)', once the FuncExtension
        class is instantiate, overwrite the __init__() method and add the
        instance into life-cycle hooks.
        """
        scope = ExtensionMeta._get_extension_scope(cls)

        # Only register function extension here
        if scope is ExtensionScope.FUNCTION:
            instance = super(ExtensionMeta, cls).__call__(*args, **kwargs)
            ExtensionMeta._register_function_extension(instance)
            return instance
        elif scope is ExtensionScope.APPLICATION:
            raise FunctionExtensionException(
                f'Python worker extension with scope:{scope} should not be'
                'instantiable. Please access via class method directly.'
            )
        else:
            raise FunctionExtensionException(
                f'Python worker extension:{cls.__name__} is not properly '
                'implemented from AppExtensionBase or FuncExtensionBase.'
            )

    @classmethod
    def get_function_hooks(cls, name: str) -> Optional[FuncExtensionHooks]:
        """Return all function extension hooks indexed by trigger name.

        Returns
        -------
        Optional[FuncExtensionHooks]:
            Example to look up a certain life-cycle name:
            get_function_hooks('HttpTrigger').pre_invocation.ext_name
        """
        return cls._func_exts.get(name.lower())

    @classmethod
    def get_application_hooks(cls) -> Optional[AppExtensionHooks]:
        """Return all application hooks

        Returns
        -------
        Optional[AppExtensionHooks]:
            Example to look up a certain life-cycle name:
            get_application_hooks().pre_invocation_app_level.ext_name
        """
        return cls._app_exts

    @classmethod
    def get_registered_extensions_json(cls) -> str:
        """Return a json string of the registered

        Returns
        -------
        str:
            The json string will be constructed in a structure of
            {
                "FuncExtension": {
                    "<TriggerA>": [
                        "ExtensionName"
                    ]
                },
                "AppExtension": [
                    "ExtensionName"
                ]
            }
        """
        return json.dumps(cls._info)

    @classmethod
    def _get_extension_scope(cls, extension) -> ExtensionScope:
        """Return the scope of an extension"""
        return getattr(extension, '_scope', ExtensionScope.UNKNOWN)

    @classmethod
    def _set_hooks_for_function(cls, trigger_name: str, ext):
        ext_hooks = cls._func_exts.setdefault(
            trigger_name.lower(),
            cls._create_default_function_hook()
        )

        # Flatten extension class to cls._func_exts
        for hook_name in ext_hooks._fields:
            hook_impl = getattr(ext, hook_name, None)
            if hook_impl is not None:
                hook_meta = ExtensionHookMeta(
                    ext_name=ext.__class__.__name__,
                    ext_impl=hook_impl,
                )
                getattr(ext_hooks, hook_name).append(hook_meta)

    @classmethod
    def _set_hooks_for_application(cls, ext):
        if cls._app_exts is None:
            cls._app_exts = cls._create_default_app_hook()

        # Check for definition in AppExtensionHooks NamedTuple
        for hook_name in cls._app_exts._fields:
            hook_impl = getattr(ext, hook_name, None)
            if hook_impl is not None:
                getattr(cls._app_exts, hook_name).append(ExtensionHookMeta(
                    ext_name=ext.__name__,
                    ext_impl=hook_impl
                ))

    @classmethod
    def _register_function_extension(cls, extension):
        """Flatten the function extension structure into function hooks"""
        # Should skip registering FuncExtensionBase, cannot use isinstance(),
        # referring to func_extension_hooks introduces a dependency cycle
        if extension.__class__.__name__ == 'FuncExtensionBase':
            return

        trigger_name = extension._trigger_name
        cls._set_hooks_for_function(trigger_name, extension)

        # Record function extension information
        hooks_info = cls._info.setdefault(  # type: ignore
            'FuncExtension', {}).setdefault(trigger_name, [])
        hooks_info.append(extension.__class__.__name__)

    @classmethod
    def _register_application_extension(cls, extension):
        """Flatten the application extension structure into function hooks"""
        # Should skip registering AppExtensionBase, cannot use isinstance(),
        # referring to app_extension_hooks introduces a dependency cycle
        if extension.__name__ == 'AppExtensionBase':
            return

        if getattr(extension, 'init', None):
            extension.init()

        cls._set_hooks_for_application(extension)

        # Record application extension information
        hooks_info = cls._info.setdefault('AppExtension', [])
        hooks_info.append(extension.__name__)   # type: ignore

    @classmethod
    def _create_default_function_hook(cls) -> FuncExtensionHooks:
        return FuncExtensionHooks(
            post_function_load=[],
            pre_invocation=[],
            post_invocation=[]
        )

    @classmethod
    def _create_default_app_hook(cls) -> AppExtensionHooks:
        return AppExtensionHooks(
            post_function_load_app_level=[],
            pre_invocation_app_level=[],
            post_invocation_app_level=[]
        )
