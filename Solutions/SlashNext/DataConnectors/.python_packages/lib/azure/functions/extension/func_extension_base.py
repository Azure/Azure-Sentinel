# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
import os
import typing
from logging import Logger
from .extension_meta import ExtensionMeta
from .extension_scope import ExtensionScope
from .function_extension_exception import FunctionExtensionException
from .._abc import Context


class FuncExtensionBase(metaclass=ExtensionMeta):
    """An abstract class defines the life-cycle hooks which to be implemented
    by customer's extension.

    Everytime when a new extension is initialized in customer function scripts,
    the ExtensionManager._func_exts field records the extension to this
    specific function name.
    """

    _scope = ExtensionScope.FUNCTION

    @abc.abstractmethod
    def __init__(self, file_path: str):
        """Constructor for extension. This needs to be implemented and ensure
        super().__init__(file_path) is called.

        The initializer serializes the extension to a tree. This speeds
        up the worker lookup and reduce the overhead on each invocation.
        _func_exts[<trigger_name>].<hook_name>.(ext_name, ext_impl)
        (e.g. _func_exts['HttpTrigger'].pre_invocation.ext_impl)

        Parameters
        ----------
        file_path: str
            The name of trigger the extension attaches to (e.g. __file__).
        """
        script_root = os.getenv('AzureWebJobsScriptRoot')
        if script_root is None:
            raise FunctionExtensionException(
                'AzureWebJobsScriptRoot environment variable is not defined. '
                'Please ensure the extension is running in Azure Functions.'
            )

        # Split will always return ('') in if no folder exist in the path
        relpath_to_project_root = os.path.relpath(
            os.path.normpath(file_path),
            os.path.normpath(script_root)
        )

        trigger_name = (relpath_to_project_root.split(os.sep) or [''])[0]
        if not trigger_name or trigger_name.startswith(('.', '..')):
            raise FunctionExtensionException(
                'Failed to parse trigger name from filename. '
                'Function extension should bind to a trigger script, '
                'not share folder. Please ensure extension is create inside a'
                'trigger while __file__ is passed into the argument. '
                'The trigger name is resolved from os.path.relpath(file_path,'
                'project_root).'
            )

        # This is used in ExtensionMeta._register_function_extension
        self._trigger_name = trigger_name

    # DO NOT decorate this with @abc.abstractmethod
    # since implementation by subclass is not mandatory
    def post_function_load(self,
                           function_name: str,
                           function_directory: str,
                           *args, **kwargs) -> None:
        """This hook will be called right after a customer's function loaded.
        In this stage, the customer's logger is not fully initialized, so it
        is not provided. Please use print() to emit message if necessary.

        Parameters
        ----------
        function_name: str
            The name of customer's function (e.g. HttpTrigger)
        function_directory: str
            The path to customer's function directory
            (e.g. /home/site/wwwroot/HttpTrigger)
        """
        pass

    # DO NOT decorate this with @abc.abstractmethod
    # since implementation by subclass is not mandatory
    def pre_invocation(
            self,
            logger: Logger,
            context: Context,
            func_args: typing.Optional[typing.Dict[str, object]] = None,
            *args,
            **kwargs) -> None:
        """This hook will be called right before customer's function
        is being executed.

        Parameters
        ----------
        logger: logging.Logger
            A logger provided by Python worker. Extension developer should
            use this logger to emit telemetry to Azure Functions customers.
        context: azure.functions.Context
            This will include the function_name, function_directory and an
            invocation_id of this specific invocation.
        func_args: typing.Dict[str, object]
            Arguments that are passed into the Azure Functions. The name of
            each parameter is defined in function.json. Extension developers
            may also want to do isinstance() check if you want to apply
            operations to specific trigger types or input binding types.
        """
        pass

    # DO NOT decorate this with @abc.abstractmethod
    # since implementation by subclass is not mandatory
    def post_invocation(
            self,
            logger: Logger,
            context: Context,
            func_args: typing.Optional[typing.Dict[str, object]] = None,
            func_ret: typing.Optional[object] = None,
            *args,
            **kwargs) -> None:
        """This hook will be called right after a customer's function
        is executed.

        Parameters
        ----------
        logger: logging.Logger
            A logger provided by Python worker. Extension developer should
            use this logger to emit telemetry to Azure Functions customers.
        context: azure.functions.Context
            This will include the function_name, function_directory and an
            invocation_id of this specific invocation.
        func_args: typing.Dict[str, object]
            Arguments that are passed into the Azure Functions. The name of
            each parameter is defined in function.json. Extension developers
            may also want to do isinstance() check if you want to apply
            operations to specific trigger types or input binding types.
        func_ret: typing.Optional[object]
            Return value from Azure Functions. This is usually the value
            defined in function.json $return section. Extension developers
            may also want to do isinstance() check if you want to apply
            operations to specific types or input binding types.
        """
        pass
