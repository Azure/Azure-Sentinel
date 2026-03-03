#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import abc
import asyncio
import json
import logging
from abc import ABC
from datetime import time
from typing import Any, Callable, Dict, List, Optional, Union, \
    Iterable

from azure.functions.decorators.blob import BlobTrigger, BlobInput, BlobOutput
from azure.functions.decorators.core import Binding, Trigger, DataType, \
    AuthLevel, SCRIPT_FILE_NAME, Cardinality, AccessRights, Setting, BlobSource
from azure.functions.decorators.cosmosdb import CosmosDBTrigger, \
    CosmosDBOutput, CosmosDBInput, CosmosDBTriggerV3, CosmosDBInputV3, \
    CosmosDBOutputV3
from azure.functions.decorators.dapr import DaprBindingOutput, \
    DaprBindingTrigger, DaprInvokeOutput, DaprPublishOutput, \
    DaprSecretInput, DaprServiceInvocationTrigger, DaprStateInput, \
    DaprStateOutput, DaprTopicTrigger
from azure.functions.decorators.eventgrid import EventGridTrigger, \
    EventGridOutput
from azure.functions.decorators.eventhub import EventHubTrigger, EventHubOutput
from azure.functions.decorators.http import HttpTrigger, HttpOutput, \
    HttpMethod
from azure.functions.decorators.kafka import KafkaTrigger, KafkaOutput, \
    BrokerAuthenticationMode, BrokerProtocol, OAuthBearerMethod
from azure.functions.decorators.queue import QueueTrigger, QueueOutput
from azure.functions.decorators.servicebus import ServiceBusQueueTrigger, \
    ServiceBusQueueOutput, ServiceBusTopicTrigger, \
    ServiceBusTopicOutput
from azure.functions.decorators.sql import SqlTrigger, SqlInput, SqlOutput
from azure.functions.decorators.table import TableInput, TableOutput
from azure.functions.decorators.timer import TimerTrigger
from azure.functions.decorators.utils import parse_singular_param_to_enum, \
    parse_iterable_param_to_enums, StringifyEnumJsonEncoder
from azure.functions.http import HttpRequest
from .generic import GenericInputBinding, GenericTrigger, GenericOutputBinding
from .openai import AssistantSkillTrigger, OpenAIModels, TextCompletionInput, \
    AssistantCreateOutput, \
    AssistantQueryInput, AssistantPostInput, InputType, EmbeddingsInput, \
    semantic_search_system_prompt, \
    SemanticSearchInput, EmbeddingsStoreOutput
from .mcp import MCPToolTrigger
from .retry_policy import RetryPolicy
from .function_name import FunctionName
from .warmup import WarmUpTrigger
from .._http_asgi import AsgiMiddleware
from .._http_wsgi import WsgiMiddleware, Context
from azure.functions.decorators.mysql import MySqlInput, MySqlOutput, \
    MySqlTrigger


class Function(object):
    """
    The function object represents a function in Function App. It
    encapsulates function metadata and callable and used in the worker
    function indexing model.

    Ref: https://aka.ms/azure-function-ref
    """

    def __init__(self, func: Callable[..., Any], script_file: str):
        """Constructor of :class:`FunctionBuilder` object.

        :param func: User defined python function instance.
        :param script_file: File name indexed by worker to find function.
        :param trigger: The trigger object of the function.
        :param bindings: The list of binding objects of a function.
        :param settings: The list of setting objects of a function.
        :param http_type: Http function type.
        :param is_http_function: Whether the function is a http function.
        """
        self._name: str = func.__name__
        self._func = func
        self._trigger: Optional[Trigger] = None
        self._bindings: List[Binding] = []
        self._settings: List[Setting] = []
        self.function_script_file = script_file
        self.http_type = 'function'
        self._is_http_function = False

    def __str__(self):
        """Return the function.json representation of the function"""
        return self.get_function_json()

    def __call__(self, *args, **kwargs):
        """This would allow the Function object to be directly
        callable and runnable directly using the interpreter
        locally.

        Example:
        @app.route(route="http_trigger")
        def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
            return "Hello, World!"

        print(http_trigger(None))

        ➜ python function_app.py
        Hello, World!
        """
        return self._func(*args, **kwargs)

    def add_binding(self, binding: Binding) -> None:
        """Add a binding instance to the function.

        :param binding: The binding object to add.
        """
        self._bindings.append(binding)

    def add_trigger(self, trigger: Trigger) -> None:
        """Add a trigger instance to the function.

        :param trigger: The trigger object to add.
        :raises ValueError: Raises trigger already exists error if a trigger is
             being added to a function which has trigger attached.
        """
        if self._trigger:
            raise ValueError("A trigger was already registered to this "
                             "function. Adding another trigger is not the "
                             "correct behavior as a function can only have one"
                             " trigger. Existing registered trigger "
                             f"is {self._trigger.get_dict_repr()} and New "
                             f"trigger "
                             f"being added is {trigger.get_dict_repr()}")

        self._trigger = trigger
        #  We still add the trigger info to the bindings to ensure that
        #  function.json is complete
        self._bindings.append(trigger)

    def add_setting(self, setting: Setting) -> None:
        """Add a setting instance to the function.

        :param setting: The setting object to add
        """
        self._settings.append(setting)

    def set_http_type(self, http_type: str) -> None:
        """Set or update the http type for the function if :param:`http_type`
        .
        :param http_type: Http function type.
        """
        self.http_type = http_type

    def is_http_function(self) -> bool:
        return self._is_http_function

    def get_trigger(self) -> Optional[Trigger]:
        """Get attached trigger instance of the function.

        :return: Trigger instance or None.
        """
        return self._trigger

    def get_bindings(self) -> List[Binding]:
        """Get all the bindings attached to the function.

        :return: Bindings attached to the function.
        """
        return self._bindings

    def get_setting(self, setting_name: str) -> Optional[Setting]:
        """Get a specific setting attached to the function.

        :param setting_name: The name of the setting to search for.
        :return: The setting attached to the function (or None if not found).
        """
        for setting in self._settings:
            if setting.setting_name == setting_name:
                return setting
        return None

    def get_settings_dict(self, setting_name) -> Optional[Dict]:
        """Get a dictionary representation of a setting.

        :param: setting_name: The name of the setting to search for.
        :return: The dictionary representation of the setting (or None if not
        found).
        """
        setting = self.get_setting(setting_name)
        return setting.get_dict_repr() if setting else None

    def get_function_name(self) -> Optional[str]:
        """Get the name of the function.
        :return: The name of the function.
        """
        function_name_setting = \
            self.get_setting("function_name")
        return function_name_setting.get_settings_value("function_name") \
            if function_name_setting else self._name

    def get_raw_bindings(self) -> List[str]:
        return [json.dumps(b.get_dict_repr(), cls=StringifyEnumJsonEncoder)
                for b in self._bindings]

    def get_bindings_dict(self) -> Dict:
        """Get dictionary representation of the bindings of the function.

        :return: Dictionary representation of the bindings.
        """
        return {"bindings": [b.get_dict_repr() for b in self._bindings]}

    def get_dict_repr(self) -> Dict:
        """Get the dictionary representation of the function.

        :return: The dictionary representation of the function.
        """
        stub_f_json = {
            "scriptFile": self.function_script_file
        }
        stub_f_json.update(self.get_bindings_dict())  # NoQA
        return stub_f_json

    def get_user_function(self) -> Callable[..., Any]:
        """Get the python function customer defined.

        :return: The python function customer defined.
        """
        return self._func

    def get_function_json(self) -> str:
        """Get the json stringified form of function.

        :return: The json stringified form of function.
        """
        return json.dumps(self.get_dict_repr(), cls=StringifyEnumJsonEncoder)


class FunctionBuilder(object):

    def __init__(self, func, function_script_file):
        self._function = Function(func, function_script_file)

    def __call__(self, *args, **kwargs):
        """Call the Function object directly"""
        return self._function(*args, **kwargs)

    def configure_http_type(self, http_type: str) -> 'FunctionBuilder':
        self._function.set_http_type(http_type)

        return self

    def add_trigger(self, trigger: Trigger) -> 'FunctionBuilder':
        self._function.add_trigger(trigger=trigger)
        return self

    def add_binding(self, binding: Binding) -> 'FunctionBuilder':
        self._function.add_binding(binding=binding)
        return self

    def add_setting(self, setting: Setting) -> 'FunctionBuilder':
        self._function.add_setting(setting=setting)
        return self

    def _validate_function(self,
                           auth_level: Optional[AuthLevel] = None) -> None:
        """
        Validates the function information before building the function.

        Functions with the same function name are not supported and should
        fail indexing. If a function name is not defined, the default is the
        method name. This also means that two functions with the same
        method name will also fail indexing.
        https://github.com/Azure/azure-functions-python-worker/issues/1489

        :param auth_level: Http auth level that will be set if http
        trigger function auth level is None.
        """
        function_name = self._function.get_function_name()
        trigger = self._function.get_trigger()
        if trigger is None:
            raise ValueError(
                f"Function {function_name} does not have a trigger. A valid "
                f"function must have one and only one trigger registered.")

        bindings = self._function.get_bindings()
        if trigger not in bindings:
            raise ValueError(
                f"Function {function_name} trigger {trigger} not present"
                f" in bindings {bindings}")

        # Set route to function name if unspecified in the http trigger
        # Set auth level to function app auth level if unspecified in the
        # http trigger
        if Trigger.is_supported_trigger_type(trigger, HttpTrigger):
            if getattr(trigger, 'route', None) is None:
                getattr(trigger, 'init_params').append('route')
                setattr(trigger, 'route', function_name)
            if getattr(trigger, 'auth_level',
                       None) is None and auth_level is not None:
                getattr(trigger, 'init_params').append('auth_level')
                setattr(trigger, 'auth_level',
                        parse_singular_param_to_enum(auth_level, AuthLevel))
            self._function._is_http_function = True

    def build(self, auth_level: Optional[AuthLevel] = None) -> Function:
        """
        Validates and builds the function object.

        :param auth_level: Http auth level that will be set if http
        trigger function auth level is None.
        """
        self._validate_function(auth_level)
        return self._function


class DecoratorApi(ABC):
    """Interface which contains essential decorator function building blocks
    to extend for creating new function app or blueprint classes.
    """

    def __init__(self, *args, **kwargs):
        self._function_builders: List[FunctionBuilder] = []
        self._app_script_file: str = SCRIPT_FILE_NAME

    def _invoke_df_decorator(self, df_decorator):
        """
        Invoke a Durable Functions decorator from the DF SDK, and store the
        resulting :class:`FunctionBuilder` object within the `DecoratorApi`.

        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                function_builder = df_decorator(fb._function._func)

                # remove old function builder from `self` and replace
                # it with the result of the DF decorator
                self._function_builders.pop()
                self._function_builders.append(function_builder)
                return function_builder

            return decorator()

        return wrap

    def _get_durable_blueprint(self):
        """Attempt to import the Durable Functions SDK from which DF
        decorators are implemented.
        """
        try:
            import azure.durable_functions as df
            df_bp = df.Blueprint()
            return df_bp
        except ImportError:
            error_message = \
                "Attempted to use a Durable Functions decorator, " \
                "but the `azure-functions-durable` SDK package could not be " \
                "found. Please install `azure-functions-durable` to use " \
                "Durable Functions."
            raise Exception(error_message)

    @property
    def app_script_file(self) -> str:
        """Name of function app script file in which all the functions
         are defined.

         Script file defined here is for placeholder purpose, please refer to
         worker defined script file path as the single point of truth.

        :return: Script file name.
        """
        return self._app_script_file

    def function_name(self, name: str,
                      setting_extra_fields: Optional[Dict[str, Any]] = None,
                      ) -> Callable[..., Any]:
        """Optional: Sets name of the :class:`Function` object. If not set,
        it will default to the name of the method name.

        :param name: Name of the function.
        :param setting_extra_fields: Keyword arguments for specifying
        additional setting fields
        :return: Decorator function.
        """
        if setting_extra_fields is None:
            setting_extra_fields = {}

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_setting(setting=FunctionName(
                    function_name=name,
                    **setting_extra_fields))
                return fb

            return decorator()

        return wrap

    def _validate_type(self,
                       func: Union[Callable[..., Any], FunctionBuilder]) \
            -> FunctionBuilder:
        """Validate the type of the function object and return the created
        :class:`FunctionBuilder` object.


        :param func: Function object passed to
         :meth:`_configure_function_builder`
        :raises ValueError: Raise error when func param is neither
         :class:`Callable` nor :class:`FunctionBuilder`.
        :return: :class:`FunctionBuilder` object.
        """
        if isinstance(func, FunctionBuilder):
            fb = self._function_builders.pop()
        elif callable(func):
            fb = FunctionBuilder(func, self._app_script_file)
        else:
            raise ValueError(
                "Unsupported type for function app decorator found.")
        return fb

    def _configure_function_builder(self, wrap) -> Callable[..., Any]:
        """Decorator function on user defined function to create and return
        :class:`FunctionBuilder` object from :class:`Callable` func.
        """

        def decorator(func):
            fb = self._validate_type(func)
            self._function_builders.append(fb)
            return wrap(fb)

        return decorator

    def http_type(self, http_type: str) -> Callable[..., Any]:
        """Set http type of the :class:`Function` object.

        :param http_type: Http type of the function.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.configure_http_type(http_type)
                return fb

            return decorator()

        return wrap


class HttpFunctionsAuthLevelMixin(ABC):
    """Interface to extend for enabling function app-level HTTP authorization level setting."""

    def __init__(self, auth_level: Union[AuthLevel, str], *args, **kwargs):
        self._auth_level = AuthLevel[auth_level] \
            if isinstance(auth_level, str) else auth_level

    @property
    def auth_level(self) -> AuthLevel:
        """Authorization level of the function app. Will be applied to the http
         trigger functions which do not have authorization level specified.

        :return: Authorization level of the function app.
        """
        return self._auth_level


class TriggerApi(DecoratorApi, ABC):
    """Interface to extend for using existing trigger decorator functions."""

    def route(self,
              route: Optional[str] = None,
              trigger_arg_name: str = 'req',
              binding_arg_name: str = '$return',
              methods: Optional[
                  Union[Iterable[str], Iterable[HttpMethod]]] = None,
              auth_level: Optional[Union[AuthLevel, str]] = None,
              trigger_extra_fields: Optional[Dict[str, Any]] = None,
              binding_extra_fields: Optional[Dict[str, Any]] = None
              ) -> Callable[..., Any]:
        """
        The `route` decorator adds :class:`HttpTrigger` and :class:`HttpOutput`
        bindings to the :class:`FunctionBuilder` object for building a :class:`Function`
        used in the worker function indexing model.

        This is equivalent to defining both `HttpTrigger` and `HttpOutput` bindings
        in the `function.json`, which enables your function to be triggered when
        HTTP requests hit the specified route.

        All optional fields will be given default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-binding-http

        :param route: Route for the HTTP endpoint. If None, it defaults to the function
            name (if present) or the user-defined Python function name.
        :param trigger_arg_name: Argument name for :class:`HttpRequest`. Defaults to `'req'`.
        :param binding_arg_name: Argument name for :class:`HttpResponse`. Defaults to `'$return'`.
        :param methods: A tuple of the HTTP methods to which the function responds.
        :param auth_level: Determines what keys, if any, need to be present
            on the request in order to invoke the function.
        :param trigger_extra_fields: Additional fields to include in the trigger JSON.
            For example:
            >>> data_type='STRING'  # results in 'dataType': 'STRING' in the trigger JSON
        :param binding_extra_fields: Additional fields to include in the binding JSON.
            For example:
            >>> data_type='STRING'  # results in 'dataType': 'STRING' in the binding JSON

        :return: Decorator function.
        """
        if trigger_extra_fields is None:
            trigger_extra_fields = {}
        if binding_extra_fields is None:
            binding_extra_fields = {}

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(trigger=HttpTrigger(
                    name=trigger_arg_name,
                    methods=parse_iterable_param_to_enums(methods, HttpMethod),
                    auth_level=parse_singular_param_to_enum(auth_level,
                                                            AuthLevel),
                    route=route, **trigger_extra_fields))
                fb.add_binding(binding=HttpOutput(
                    name=binding_arg_name, **binding_extra_fields))
                return fb

            return decorator()

        return wrap

    def orchestration_trigger(self, context_name: str,
                              orchestration: Optional[str] = None):
        """Register an Orchestrator Function.

        Parameters
        ----------
        context_name: str
            Parameter name of the DurableOrchestrationContext object.
        orchestration: Optional[str]
            Name of Orchestrator Function.
            By default, the name of the method is used.
        """
        df_bp = self._get_durable_blueprint()
        df_decorator = df_bp.orchestration_trigger(context_name,
                                                   orchestration)
        result = self._invoke_df_decorator(df_decorator)
        return result

    def entity_trigger(self, context_name: str,
                       entity_name: Optional[str] = None):
        """Register an Entity Function.

        Parameters
        ----------
        context_name: str
            Parameter name of the Entity input.
        entity_name: Optional[str]
            Name of Entity Function.
        """
        df_bp = self._get_durable_blueprint()
        df_decorator = df_bp.entity_trigger(context_name,
                                            entity_name)
        result = self._invoke_df_decorator(df_decorator)
        return result

    def activity_trigger(self, input_name: str,
                         activity: Optional[str] = None):
        """Register an Activity Function.

        Parameters
        ----------
        input_name: str
            Parameter name of the Activity input.
        activity: Optional[str]
            Name of Activity Function.
        """
        df_bp = self._get_durable_blueprint()
        df_decorator = df_bp.activity_trigger(input_name, activity)
        result = self._invoke_df_decorator(df_decorator)
        return result

    def timer_trigger(self,
                      arg_name: str,
                      schedule: str,
                      run_on_startup: Optional[bool] = None,
                      use_monitor: Optional[bool] = None,
                      data_type: Optional[Union[DataType, str]] = None,
                      **kwargs: Any) -> Callable[..., Any]:
        """
        The `schedule` or `timer` decorator adds :class:`TimerTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining a `TimerTrigger` in the `function.json`, which
        enables your function to be triggered on the specified schedule.

        All optional fields will be given default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-binding-timer

        :param arg_name: The name of the variable that represents the
            :class:`TimerRequest` object in function code.
        :param schedule: A string representing a CRON expression used to schedule
            the function execution.
        :param run_on_startup: If True, the function is invoked when the runtime starts.
        :param use_monitor: Set to True or False to indicate whether the
            schedule should be monitored.
        :param data_type: Defines how the Functions runtime should treat the parameter value.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=TimerTrigger(
                        name=arg_name,
                        schedule=schedule,
                        run_on_startup=run_on_startup,
                        use_monitor=use_monitor,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    schedule = timer_trigger

    def warm_up_trigger(self,
                        arg_name: str,
                        data_type: Optional[Union[DataType, str]] = None,
                        **kwargs) -> Callable:
        """
        The `warm_up` decorator adds :class:`WarmUpTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining a `WarmUpTrigger` in the `function.json`, which
        enables your function to be triggered on the specified schedule.

        All optional fields will be given default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-binding-warmup

        :param arg_name: The name of the variable that represents the
            :class:`TimerRequest` object in the function code.
        :param data_type: Defines how the Functions runtime should treat the parameter value.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=WarmUpTrigger(
                        name=arg_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def service_bus_queue_trigger(
            self,
            arg_name: str,
            connection: str,
            queue_name: str,
            data_type: Optional[Union[DataType, str]] = None,
            access_rights: Optional[Union[AccessRights, str]] = None,
            is_sessions_enabled: Optional[bool] = None,
            cardinality: Optional[Union[Cardinality, str]] = None,
            **kwargs: Any) -> Callable[..., Any]:
        """
        The `on_service_bus_queue_change` decorator adds :class:`ServiceBusQueueTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the worker
        function indexing model.

        This is equivalent to defining a `ServiceBusQueueTrigger` in the `function.json`,
        which enables the function to be triggered when new message(s) are sent to the
        Service Bus queue.

        All optional fields will be given default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the
            :class:`ServiceBusMessage` object in the function code.
        :param connection: The name of an app setting or setting collection that specifies
            how to connect to Service Bus.
        :param queue_name: The name of the queue to monitor.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param access_rights: Access rights for the connection string.
        :param is_sessions_enabled: Set to True if connecting to a session-aware queue
            or subscription.
        :param cardinality: Set to "many" to enable batching.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=ServiceBusQueueTrigger(
                        name=arg_name,
                        connection=connection,
                        queue_name=queue_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        access_rights=parse_singular_param_to_enum(
                            access_rights,
                            AccessRights),
                        is_sessions_enabled=is_sessions_enabled,
                        cardinality=parse_singular_param_to_enum(cardinality,
                                                                 Cardinality),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def service_bus_topic_trigger(
            self,
            arg_name: str,
            connection: str,
            topic_name: str,
            subscription_name: str,
            data_type: Optional[Union[DataType, str]] = None,
            access_rights: Optional[Union[AccessRights, str]] = None,
            is_sessions_enabled: Optional[bool] = None,
            cardinality: Optional[Union[Cardinality, str]] = None,
            **kwargs: Any) -> Callable[..., Any]:
        """
        The `on_service_bus_topic_change` decorator adds :class:`ServiceBusTopicTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the worker
        function indexing model.

        This is equivalent to defining a `ServiceBusTopicTrigger` in the `function.json`,
        which enables the function to be triggered when new message(s) are sent to a
        Service Bus topic.

        All optional fields will be given default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the
            :class:`ServiceBusMessage` object in the function code.
        :param connection: The name of an app setting or setting collection that specifies
            how to connect to Service Bus.
        :param topic_name: The name of the topic to monitor.
        :param subscription_name: The name of the subscription to monitor.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param access_rights: Access rights for the connection string.
        :param is_sessions_enabled: Set to True if connecting to a session-aware queue
            or subscription.
        :param cardinality: Set to "many" to enable batching.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=ServiceBusTopicTrigger(
                        name=arg_name,
                        connection=connection,
                        topic_name=topic_name,
                        subscription_name=subscription_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        access_rights=parse_singular_param_to_enum(
                            access_rights,
                            AccessRights),
                        is_sessions_enabled=is_sessions_enabled,
                        cardinality=parse_singular_param_to_enum(cardinality,
                                                                 Cardinality),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def queue_trigger(self,
                      arg_name: str,
                      queue_name: str,
                      connection: str,
                      data_type: Optional[DataType] = None,
                      **kwargs) -> Callable[..., Any]:
        """
        The `queue_trigger` decorator adds :class:`QueueTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining a `QueueTrigger` in the `function.json`, which
        enables the function to be triggered when new message(s) are sent to an Azure Storage queue.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-binding-queue

        :param arg_name: The name of the variable that represents the
            :class:`QueueMessage` object in the function code.
        :param queue_name: The name of the queue to monitor.
        :param connection: The name of an app setting or setting collection that specifies
            how to connect to Azure Queues.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=QueueTrigger(
                        name=arg_name,
                        queue_name=queue_name,
                        connection=connection,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def event_hub_message_trigger(self,
                                  arg_name: str,
                                  connection: str,
                                  event_hub_name: str,
                                  data_type: Optional[
                                      Union[DataType, str]] = None,
                                  cardinality: Optional[
                                      Union[Cardinality, str]] = None,
                                  consumer_group: Optional[
                                      str] = None,
                                  **kwargs: Any) -> Callable[..., Any]:
        """
        The `event_hub_message_trigger` decorator adds :class:`EventHubTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining an `EventHubTrigger` in the `function.json`, which
        enables the function to be triggered when new message(s) are sent to the Event Hub.

        All optional fields will be given default values by the function host when they are parsed.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents the
            :class:`EventHubEvent` object in the function code.
        :param connection: The name of an app setting or setting collection that specifies
            how to connect to Event Hubs.
        :param event_hub_name: The name of the Event Hub.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param cardinality: Set to "many" to enable batching.
        :param consumer_group: Optional. The consumer group used to subscribe to events in the hub.
        :param kwargs: Additional keyword arguments to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=EventHubTrigger(
                        name=arg_name,
                        connection=connection,
                        event_hub_name=event_hub_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        cardinality=parse_singular_param_to_enum(cardinality,
                                                                 Cardinality),
                        consumer_group=consumer_group,
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def cosmos_db_trigger_v3(self,
                             arg_name: str,
                             database_name: str,
                             collection_name: str,
                             connection_string_setting: str,
                             lease_collection_name: Optional[str] = None,
                             lease_connection_string_setting: Optional[
                                 str] = None,
                             lease_database_name: Optional[str] = None,
                             create_lease_collection_if_not_exists: Optional[
                                 bool] = None,
                             leases_collection_throughput: Optional[int] =
                             None,
                             lease_collection_prefix: Optional[str] = None,
                             checkpoint_interval: Optional[int] = None,
                             checkpoint_document_count: Optional[int] = None,
                             feed_poll_delay: Optional[int] = None,
                             lease_renew_interval: Optional[int] = None,
                             lease_acquire_interval: Optional[int] = None,
                             lease_expiration_interval: Optional[int] = None,
                             max_items_per_invocation: Optional[int] = None,
                             start_from_beginning: Optional[bool] = None,
                             preferred_locations: Optional[str] = None,
                             data_type: Optional[
                                 Union[DataType, str]] = None,
                             **kwargs: Any) -> \
            Callable[..., Any]:
        """
        The `cosmos_db_trigger_v3` decorator adds :class:`CosmosDBTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model. This decorator only works with
        extension bundle 2.x or 3.x.

        This is equivalent to defining `CosmosDBTrigger` in the `function.json`,
        which enables the function to be triggered when Cosmos DB data changes.
        All optional fields will be assigned default values by the function host
        when they are parsed.

        See: https://aka.ms/cosmosdb-v4-update
        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents the
            :class:`DocumentList` object in the function code.
        :param database_name: The name of the Azure Cosmos DB database containing
            the monitored collection.
        :param collection_name: The name of the collection being monitored.
        :param connection_string_setting: The name of an app setting or setting
            collection specifying how to connect to the monitored Azure Cosmos DB account.
        :param lease_collection_name: The name of the collection used to store leases.
        :param lease_connection_string_setting: The name of an app setting or setting
            collection that specifies how to connect to the Azure Cosmos DB account
            that holds the lease collection.
        :param lease_database_name: The name of the database that holds the lease
            collection.
        :param create_lease_collection_if_not_exists: If `True`, the lease collection
            is automatically created when it does not already exist.
        :param leases_collection_throughput: The number of Request Units (RUs)
            assigned when the lease collection is created.
        :param lease_collection_prefix: A prefix added to leases created in the lease
            collection for this Function.
        :param checkpoint_interval: The interval (in milliseconds) between lease
            checkpoints. The default behavior is to checkpoint after every function call.
        :param checkpoint_document_count: Number of documents processed between
            lease checkpoints. Default is after every function call.
        :param feed_poll_delay: The delay (in milliseconds) between polling a
            partition for new changes after all current changes are drained.
        :param lease_renew_interval: The interval (in milliseconds) to renew leases
            for partitions currently held by an instance.
        :param lease_acquire_interval: The interval (in milliseconds) to trigger a
            task that checks whether partitions are evenly distributed among host
            instances.
        :param lease_expiration_interval: The interval (in milliseconds) for which
            a lease is held for a partition.
        :param max_items_per_invocation: Maximum number of items received per
            function call.
        :param start_from_beginning: If `True`, the trigger starts reading changes
            from the beginning of the collection's change history rather than from
            the current time.
        :param preferred_locations: Preferred locations (regions) for geo-replicated
            database accounts in Azure Cosmos DB.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            in the `function.json`.

        :return: Decorator function.
        """
        trigger = CosmosDBTriggerV3(
            name=arg_name,
            database_name=database_name,
            collection_name=collection_name,
            connection_string_setting=connection_string_setting,
            lease_collection_name=lease_collection_name,
            lease_connection_string_setting=lease_connection_string_setting,
            lease_database_name=lease_database_name,
            create_lease_collection_if_not_exists=create_lease_collection_if_not_exists,  # NoQA
            leases_collection_throughput=leases_collection_throughput,
            lease_collection_prefix=lease_collection_prefix,
            checkpoint_interval=checkpoint_interval,
            checkpoint_document_count=checkpoint_document_count,
            feed_poll_delay=feed_poll_delay,
            lease_renew_interval=lease_renew_interval,
            lease_acquire_interval=lease_acquire_interval,
            lease_expiration_interval=lease_expiration_interval,
            max_items_per_invocation=max_items_per_invocation,
            start_from_beginning=start_from_beginning,
            preferred_locations=preferred_locations,
            data_type=parse_singular_param_to_enum(data_type, DataType),
            **kwargs)

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(trigger=trigger)
                return fb

            return decorator()

        return wrap

    def cosmos_db_trigger(self,
                          arg_name: str,
                          connection: str,
                          database_name: str,
                          container_name: str,
                          lease_connection: Optional[str] = None,
                          lease_database_name: Optional[str] = None,
                          lease_container_name: Optional[str] = None,
                          create_lease_container_if_not_exists: Optional[
                              bool] = None,
                          leases_container_throughput: Optional[int] = None,
                          lease_container_prefix: Optional[str] = None,
                          feed_poll_delay: Optional[int] = None,
                          lease_acquire_interval: Optional[int] = None,
                          lease_expiration_interval: Optional[int] = None,
                          lease_renew_interval: Optional[int] = None,
                          max_items_per_invocation: Optional[int] = None,
                          start_from_beginning: Optional[time] = None,
                          start_from_time: Optional[time] = None,
                          preferred_locations: Optional[str] = None,
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs: Any) -> \
            Callable[..., Any]:
        """
        The `cosmos_db_trigger` decorator adds :class:`CosmosDBTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 4.x and above. It is
        equivalent to defining `CosmosDBTrigger` in the `function.json`, which
        enables the function to be triggered when Cosmos DB data changes. All
        optional fields are assigned default values by the function host when parsed.

        See: https://aka.ms/cosmosdb-v4-update
        Ref: https://aka.ms/azure-function-binding-cosmosdb-v4

        :param arg_name: The name of the variable that represents the
            :class:`DocumentList` object in the function code.
        :param connection: The name of an app setting or setting collection
            that specifies how to connect to the monitored Azure Cosmos DB account.
        :param database_name: The name of the Azure Cosmos DB database containing
            the monitored collection.
        :param container_name: The name of the container being monitored.
        :param lease_connection: (Optional) The name of an app setting or setting
            collection that specifies how to connect to the Cosmos DB account
            that holds the lease container.
        :param lease_database_name: The name of the database that holds the
            collection used to store leases.
        :param lease_container_name: (Optional) The name of the container used
            to store leases. If not set, the default value "leases" is used.
        :param create_lease_container_if_not_exists: (Optional) If `True`, the leases
            container is created automatically if it does not exist. Defaults to `False`.
            Note: When using Azure AD identities, container creation is not allowed,
            and the function will not start if this is `True`.
        :param leases_container_throughput: (Optional) The number of Request Units
            (RUs) to assign when the leases container is created. This is used only
            when `create_lease_container_if_not_exists` is `True`. It is automatically
            set when configured through the Azure Portal.
        :param lease_container_prefix: (Optional) A prefix added to leases created
            in the lease container for this function. Use this to allow multiple
            functions to share the same lease container with different prefixes.
        :param feed_poll_delay: The delay (in milliseconds) between polling a
            partition for new changes after draining current changes.
        :param lease_acquire_interval: The interval (in milliseconds) to trigger a
            task to check if partitions are evenly distributed across host instances.
        :param lease_expiration_interval: The interval (in milliseconds) for which a
            lease is held for a partition.
        :param lease_renew_interval: The interval (in milliseconds) to renew all
            leases for partitions currently held by an instance.
        :param max_items_per_invocation: Maximum number of items received per
            function call.
        :param start_from_beginning: If `True`, the trigger starts reading changes
            from the beginning of the collection's change history instead of the
            current time.
        :param start_from_time: (Optional) The date and time from which to begin
            reading the change feed. Use ISO 8601 format with a UTC designator,
            e.g., `2021-02-16T14:19:29Z`. Only used to set the initial trigger state;
            has no effect once the trigger has a lease state.
        :param preferred_locations: Preferred locations (regions) for geo-replicated
            Cosmos DB accounts.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """
        trigger = CosmosDBTrigger(
            name=arg_name,
            connection=connection,
            database_name=database_name,
            container_name=container_name,
            lease_connection=lease_connection,
            lease_database_name=lease_database_name,
            lease_container_name=lease_container_name,
            create_lease_container_if_not_exists=create_lease_container_if_not_exists,  # NoQA
            leases_container_throughput=leases_container_throughput,
            lease_container_prefix=lease_container_prefix,
            feed_poll_delay=feed_poll_delay,
            lease_acquire_interval=lease_acquire_interval,
            lease_expiration_interval=lease_expiration_interval,
            lease_renew_interval=lease_renew_interval,
            max_items_per_invocation=max_items_per_invocation,
            start_from_beginning=start_from_beginning,
            start_from_time=start_from_time,
            preferred_locations=preferred_locations,
            data_type=parse_singular_param_to_enum(data_type, DataType),
            **kwargs)

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(trigger=trigger)
                return fb

            return decorator()

        return wrap

    def blob_trigger(self,
                     arg_name: str,
                     path: str,
                     connection: str,
                     source: Optional[BlobSource] =
                     None,
                     data_type: Optional[DataType] = None,
                     **kwargs) -> Callable[..., Any]:
        """
        The blob_change_trigger decorator adds :class:`BlobTrigger` to the
        :class:`FunctionBuilder` object for building :class:`Function` object
        used in worker function indexing model. This is equivalent to defining
        BlobTrigger in the function.json which enables the function to be triggered
        when new message(s) are sent to storage blobs.

        All optional fields will be given default values by the function host when
        they are parsed.

        Ref: https://aka.ms/azure-function-binding-storage-blob

        :param arg_name: The name of the variable that represents the
            :class:`InputStream` object in function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection
            that specifies how to connect to Azure Blobs.
        :param source: Sets the source of the triggering event.
            Use "EventGrid" for an Event Grid-based blob trigger,
            which provides much lower latency.
            The default is "LogsAndContainerScan", which uses the standard
            polling mechanism to detect changes in the container.
        :param data_type: Defines how Functions runtime should treat the
            parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
            fields to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=BlobTrigger(
                        name=arg_name,
                        path=path,
                        connection=connection,
                        source=source,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def event_grid_trigger(self,
                           arg_name: str,
                           data_type: Optional[
                               Union[DataType, str]] = None,
                           **kwargs) -> Callable[..., Any]:
        """
        The `event_grid_trigger` decorator adds :class:`EventGridTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining an Event Grid trigger in `function.json`, which
        enables the function to be triggered in response to an event sent to an Event Grid topic.

        All optional fields will be given default values by the function host when they are parsed.

        Ref: https://aka.ms/eventgridtrigger

        :param arg_name: The variable name used in the function code for the parameter
            that receives the event data.
        :param data_type: Defines how the Functions runtime should treat the parameter value.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=EventGridTrigger(
                        name=arg_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def kafka_trigger(self,
                      arg_name: str,
                      topic: str,
                      broker_list: str,
                      event_hub_connection_string: Optional[str] = None,
                      consumer_group: Optional[str] = None,
                      avro_schema: Optional[str] = None,
                      username: Optional[str] = None,
                      password: Optional[str] = None,
                      ssl_key_location: Optional[str] = None,
                      ssl_ca_location: Optional[str] = None,
                      ssl_certificate_location: Optional[str] = None,
                      ssl_key_password: Optional[str] = None,
                      schema_registry_url: Optional[str] = None,
                      schema_registry_username: Optional[str] = None,
                      schema_registry_password: Optional[str] = None,
                      o_auth_bearer_method: Optional[Union[OAuthBearerMethod, str]] = None,  # noqa E501
                      o_auth_bearer_client_id: Optional[str] = None,
                      o_auth_bearer_client_secret: Optional[str] = None,
                      o_auth_bearer_scope: Optional[str] = None,
                      o_auth_bearer_token_endpoint_url: Optional[str] = None,
                      o_auth_bearer_extensions: Optional[str] = None,
                      authentication_mode: Optional[Union[BrokerAuthenticationMode, str]] = "NotSet", # noqa E501
                      protocol: Optional[Union[BrokerProtocol, str]] = "NotSet", # noqa E501
                      cardinality: Optional[Union[Cardinality, str]] = "One",
                      lag_threshold: int = 1000,
                      data_type: Optional[Union[DataType, str]] = None,
                      **kwargs) -> Callable[..., Any]:
        """
        The `kafka_trigger` decorator adds :class:`KafkaTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining a Kafka trigger in `function.json`, which enables
        the function to be triggered in response to an event sent to a Kafka topic.

        All optional fields will be given default values by the function host when
        parsed.

        Ref: https://aka.ms/kafkatrigger

        :param arg_name: The variable name used in the function code for the parameter
            that receives the Kafka event data.
        :param topic: The topic monitored by the trigger.
        :param broker_list: The list of Kafka brokers monitored by the trigger.
        :param event_hub_connection_string: The name of an app setting that contains the
            connection string for Event Hub (when using Kafka protocol headers with
            Azure Event Hubs).
        :param consumer_group: Kafka consumer group used by the trigger.
        :param avro_schema: Used only if a generic Avro record should be generated.
        :param username: SASL username for use with the PLAIN or SASL-SCRAM mechanisms.
            Equivalent to 'sasl.username' in librdkafka. Default is empty string.
        :param password: SASL password for use with the PLAIN or SASL-SCRAM mechanisms.
            Equivalent to 'sasl.password' in librdkafka. Default is empty string.
        :param ssl_key_location: Path to the client’s private key (PEM) used for
            authentication. Equivalent to 'ssl.key.location' in librdkafka.
        :param ssl_ca_location: Path to the CA certificate file for verifying the broker's
            certificate. Equivalent to 'ssl.ca.location' in librdkafka.
        :param ssl_certificate_location: Path to the client's certificate.
            Equivalent to 'ssl.certificate.location' in librdkafka.
        :param ssl_key_password: Password for the client’s certificate.
            Equivalent to 'ssl.key.password' in librdkafka.
        :param schema_registry_url: URL of the Avro Schema Registry.
        :param schema_registry_username: Username for the Schema Registry.
        :param schema_registry_password: Password for the Schema Registry.
        :param o_auth_bearer_method: Either 'default' or 'oidc'. Equivalent to
            'sasl.oauthbearer.method' in librdkafka.
        :param o_auth_bearer_client_id: Specify only if `o_auth_bearer_method` is 'oidc'.
            Equivalent to 'sasl.oauthbearer.client.id' in librdkafka.
        :param o_auth_bearer_client_secret: Specify only if `o_auth_bearer_method` is 'oidc'.
            Equivalent to 'sasl.oauthbearer.client.secret' in librdkafka.
        :param o_auth_bearer_scope: Specify only if `o_auth_bearer_method` is 'oidc'.
            Used to specify access scope. Equivalent to 'sasl.oauthbearer.scope'.
        :param o_auth_bearer_token_endpoint_url: Specify only if `o_auth_bearer_method` is 'oidc'.
            Equivalent to 'sasl.oauthbearer.token.endpoint.url' in librdkafka.
        :param o_auth_bearer_extensions: Additional information for the broker, in the form
            of a comma-separated list of key=value pairs (e.g., "orgId=abc,flag=true").
            Equivalent to 'sasl.oauthbearer.extensions' in librdkafka.
        :param authentication_mode: SASL mechanism to use. Allowed: Gssapi, Plain,
            ScramSha256, ScramSha512. Default: Plain. Equivalent to 'sasl.mechanism'.
        :param protocol: Security protocol used to communicate with brokers.
            Default: plaintext. Equivalent to 'security.protocol'.
        :param lag_threshold: Max number of unprocessed messages per worker instance.
            Used in scaling logic to estimate needed worker instances. Default is 1000.
        :param data_type: Defines how Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for extra binding fields in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=KafkaTrigger(
                        name=arg_name,
                        topic=topic,
                        broker_list=broker_list,
                        event_hub_connection_string=event_hub_connection_string,  # noqa: E501
                        consumer_group=consumer_group,
                        avro_schema=avro_schema,
                        username=username,
                        password=password,
                        ssl_key_location=ssl_key_location,
                        ssl_ca_location=ssl_ca_location,
                        ssl_certificate_location=ssl_certificate_location,
                        ssl_key_password=ssl_key_password,
                        schema_registry_url=schema_registry_url,
                        schema_registry_username=schema_registry_username,
                        schema_registry_password=schema_registry_password,
                        o_auth_bearer_method=parse_singular_param_to_enum(
                            o_auth_bearer_method, OAuthBearerMethod),
                        o_auth_bearer_client_id=o_auth_bearer_client_id,
                        o_auth_bearer_client_secret=o_auth_bearer_client_secret,  # noqa: E501
                        o_auth_bearer_scope=o_auth_bearer_scope,
                        o_auth_bearer_token_endpoint_url=o_auth_bearer_token_endpoint_url,  # noqa: E501
                        o_auth_bearer_extensions=o_auth_bearer_extensions,
                        authentication_mode=parse_singular_param_to_enum(
                            authentication_mode, BrokerAuthenticationMode),
                        protocol=parse_singular_param_to_enum(protocol,
                                                              BrokerProtocol),
                        cardinality=parse_singular_param_to_enum(cardinality,
                                                                 Cardinality),
                        lag_threshold=lag_threshold,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def sql_trigger(self,
                    arg_name: str,
                    table_name: str,
                    connection_string_setting: str,
                    leases_table_name: Optional[str] = None,
                    data_type: Optional[DataType] = None,
                    **kwargs) -> Callable[..., Any]:
        """
        The `sql_trigger` decorator adds :class:`SqlTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 4.x and above. It is
        equivalent to defining `SqlTrigger` in the `function.json`, which enables
        the function to be triggered when there are changes in the SQL table.
        All optional fields are assigned default values by the function host
        when parsed.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents a
            :class:`SqlRowList` object in the function code.
        :param table_name: The name of the SQL table monitored by the trigger.
        :param connection_string_setting: The name of an app setting that contains
            the connection string for the database against which the query or
            stored procedure is executed.
        :param leases_table_name: The name of the table used to store leases.
            If not specified, the default name is
            `Leases_{FunctionId}_{TableId}`.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=SqlTrigger(
                        name=arg_name,
                        table_name=table_name,
                        connection_string_setting=connection_string_setting,
                        leases_table_name=leases_table_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def mysql_trigger(self,
                      arg_name: str,
                      table_name: str,
                      connection_string_setting: str,
                      leases_table_name: Optional[str] = None,
                      data_type: Optional[DataType] = None,
                      **kwargs) -> Callable[..., Any]:
        """
        The `mysql_trigger` decorator adds :class:`MySqlTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 4.x and above. It is
        equivalent to defining `MySqlTrigger` in the `function.json`, which enables
        the function to be triggered when there are changes in the MySQL table.
        All optional fields are assigned default values by the function host
        when parsed.

        Ref: https://aka.ms/mysqlbindings

        :param arg_name: The name of the variable that represents a
            :class:`MySqlRowList` object in the function code.
        :param table_name: The name of the MySQL table monitored by the trigger.
        :param connection_string_setting: The name of an app setting that contains
            the connection string for the database against which the query or
            stored procedure is executed.
        :param leases_table_name: The name of the table used to store leases.
            If not specified, the default table name is
            `Leases_{FunctionId}_{TableId}`.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=MySqlTrigger(
                        name=arg_name,
                        table_name=table_name,
                        connection_string_setting=connection_string_setting,
                        leases_table_name=leases_table_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def generic_trigger(self,
                        arg_name: str,
                        type: str,
                        data_type: Optional[Union[DataType, str]] = None,
                        **kwargs
                        ) -> Callable[..., Any]:
        """
        The `generic_trigger` decorator adds :class:`GenericTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining a generic trigger in the `function.json`, which
        triggers the function to execute when generic trigger events are received by
        the host.

        All optional fields will be given default values by the function host when
        they are parsed.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of the trigger parameter in the function code.
        :param type: The type of the binding.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
            fields to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=GenericTrigger(
                        name=arg_name,
                        type=type,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def mcp_tool_trigger(self,
                         arg_name: str,
                         tool_name: str,
                         description: Optional[str] = None,
                         tool_properties: Optional[str] = None,
                         data_type: Optional[Union[DataType, str]] = None,
                         **kwargs) -> Callable[..., Any]:
        """
        The `mcp_tool_trigger` decorator adds :class:`MCPToolTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This is equivalent to defining `MCPToolTrigger` in the `function.json`,
        which enables the function to be triggered when MCP tool requests are
        received by the host.

        All optional fields will be given default values by the function host when
        they are parsed.

        Ref: https://aka.ms/remote-mcp-functions-python

        :param arg_name: The name of the trigger parameter in the function code.
        :param tool_name: The logical tool name exposed to the host.
        :param description: Optional human-readable description of the tool.
        :param tool_properties: JSON-serialized tool properties/parameters list.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
            fields to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=MCPToolTrigger(
                        name=arg_name,
                        tool_name=tool_name,
                        description=description,
                        tool_properties=tool_properties,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_service_invocation_trigger(self,
                                        arg_name: str,
                                        method_name: str,
                                        data_type: Optional[
                                            Union[DataType, str]] = None,
                                        **kwargs: Any) -> Callable[..., Any]:
        """
        The `dapr_service_invocation_trigger` decorator adds
        :class:`DaprServiceInvocationTrigger` to the :class:`FunctionBuilder` object
        for building a :class:`Function` used in the worker function indexing model.

        This is equivalent to defining `DaprServiceInvocationTrigger` in the
        `function.json`, which enables the function to be triggered when a service
        invocation occurs through Dapr.

        All optional fields will be given default values by the function host when
        they are parsed.

        Ref: https://aka.ms/azure-function-dapr-trigger-service-invocation

        :param arg_name: The name of the variable that represents the service invocation
            input in the function code.
        :param method_name: The name of the method on a remote Dapr App.
            If not specified, the name of the function is used as the method name.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
            fields to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=DaprServiceInvocationTrigger(
                        name=arg_name,
                        method_name=method_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_binding_trigger(self,
                             arg_name: str,
                             binding_name: str,
                             data_type: Optional[
                                 Union[DataType, str]] = None,
                             **kwargs: Any) -> Callable[..., Any]:
        """
        The `dapr_binding_trigger` decorator adds :class:`DaprBindingTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining `DaprBindingTrigger` in the `function.json`,
        which enables the function to be triggered by a Dapr input binding.

        All optional fields will be given default values by the function host when
        they are parsed.

        Ref: https://aka.ms/azure-function-dapr-trigger-binding

        :param arg_name: The name of the variable that represents the trigger input
            in the function code.
        :param binding_name: The name of the Dapr trigger. If not specified, the
            function name is used as the trigger name.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Keyword arguments for specifying additional binding fields
            to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=DaprBindingTrigger(
                        name=arg_name,
                        binding_name=binding_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_topic_trigger(self,
                           arg_name: str,
                           pub_sub_name: str,
                           topic: str,
                           route: Optional[str] = None,
                           data_type: Optional[
                               Union[DataType, str]] = None,
                           **kwargs: Any) -> Callable[..., Any]:
        """
        The `dapr_topic_trigger` decorator adds :class:`DaprTopicTrigger` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in the
        worker function indexing model.

        This is equivalent to defining `DaprTopicTrigger` in the `function.json`,
        which enables the function to be triggered when new message(s) are sent to
        the Dapr pub/sub system.

        All optional fields will be assigned default values by the function host
        when they are parsed.

        Ref: https://aka.ms/azure-function-dapr-trigger-topic

        :param arg_name: The name of the variable that represents the trigger input
            in the function code.
        :param pub_sub_name: The name of the Dapr pub/sub component.
        :param topic: The topic name. If unspecified, the function name is used.
        :param route: The route for the trigger. If unspecified, the topic name is used.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying extra binding
            fields to include in the binding JSON.

        :return: Decorator function.
        """
        # TODO: This is a temporary check, it should be removed once route
        # issue is fixed at python worker.
        # Currently, python worker treats route as HttpTrigger attribute and
        # expects value for route. Route could be nil for dapr topic trigger.
        if not route:
            route = topic

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=DaprTopicTrigger(
                        name=arg_name,
                        pub_sub_name=pub_sub_name,
                        topic=topic,
                        route=route,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def assistant_skill_trigger(self,
                                arg_name: str,
                                function_description: str,
                                function_name: Optional[str] = None,
                                parameter_description_json: Optional[str] = None,  # NoQA
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                **kwargs: Any) -> Callable[..., Any]:
        """
        Assistants build on top of chat functionality by supporting custom skills
        defined as functions. This internally uses OpenAI’s function calling
        capabilities in GPT models to determine which functions to invoke and when.

        Ref: https://platform.openai.com/docs/guides/function-calling

        You can define functions to be triggered by assistants using the
        `assistantSkillTrigger` trigger binding. These functions are invoked by the
        extension when an assistant signals it would like to invoke a function in
        response to a user prompt.

        The function name, its description (provided via the trigger), and the
        parameter descriptions are all used as hints by the language model to
        determine when and how to invoke an assistant function.

        :param arg_name: The name of the trigger parameter in the function code.
        :param function_description: A description of the assistant function,
            which is provided to the model.
        :param function_name: The name of the assistant function, which is
            passed to the language model.
        :param parameter_description_json: A JSON-formatted description of the
            function parameters, provided to the model.
            If omitted, the description is autogenerated.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=AssistantSkillTrigger(
                        name=arg_name,
                        function_description=function_description,
                        function_name=function_name,
                        parameter_description_json=parameter_description_json,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap


class BindingApi(DecoratorApi, ABC):
    """Interface to extend for using existing binding decorator functions."""

    def durable_client_input(self,
                             client_name: str,
                             task_hub: Optional[str] = None,
                             connection_name: Optional[str] = None
                             ):
        """Register a Durable-client Function.

        Parameters
        ----------
        client_name: str
            Parameter name of durable client.
        task_hub: Optional[str]
            Used in scenarios where multiple function apps share the
            same storage account but need to be isolated from each other.
            If not specified, the default value from host.json is used.
            This value must match the value used by the target
            orchestrator functions.
        connection_name: Optional[str]
            The name of an app setting that contains a storage account
            connection string.  The storage account represented by this
            connection string must be the same one used by the target
            orchestrator functions. If not specified, the default storage
            account connection string for the function app is used.
        """
        df_bp = self._get_durable_blueprint()
        df_decorator = df_bp.durable_client_input(client_name,
                                                  task_hub,
                                                  connection_name)
        result = self._invoke_df_decorator(df_decorator)
        return result

    def service_bus_queue_output(self,
                                 arg_name: str,
                                 connection: str,
                                 queue_name: str,
                                 data_type: Optional[
                                     Union[DataType, str]] = None,
                                 access_rights: Optional[Union[
                                     AccessRights, str]] = None,
                                 **kwargs) -> \
            Callable[..., Any]:
        """
        The `service_bus_queue_output` decorator adds :class:`ServiceBusQueueOutput`
        to the :class:`FunctionBuilder` object for building a :class:`Function` used
        in the worker function indexing model.

        This is equivalent to defining `ServiceBusQueueOutput` in the `function.json`,
        which enables the function to write messages to a Service Bus queue.

        All optional fields will be assigned default values by the function host
        when they are parsed.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the Service Bus queue
            output object in the function code.
        :param connection: The name of an app setting or setting collection that
            specifies how to connect to Service Bus.
        :param queue_name: The name of the queue to which messages will be sent.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param access_rights: The access rights required for the connection string.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=ServiceBusQueueOutput(
                        name=arg_name,
                        connection=connection,
                        queue_name=queue_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        access_rights=parse_singular_param_to_enum(
                            access_rights, AccessRights),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def service_bus_topic_output(self,
                                 arg_name: str,
                                 connection: str,
                                 topic_name: str,
                                 subscription_name: Optional[str] = None,
                                 data_type: Optional[
                                     Union[DataType, str]] = None,
                                 access_rights: Optional[Union[
                                     AccessRights, str]] = None,
                                 **kwargs) -> \
            Callable[..., Any]:
        """
        The `service_bus_topic_output` decorator adds :class:`ServiceBusTopicOutput`
        to the :class:`FunctionBuilder` object for building a :class:`Function` used
        in the worker function indexing model.

        This is equivalent to defining `ServiceBusTopicOutput` in the `function.json`,
        which enables the function to write messages to a Service Bus topic.

        All optional fields will be assigned default values by the function host
        when they are parsed.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the Service Bus topic
            output object in the function code.
        :param connection: The name of an app setting or setting collection that
            specifies how to connect to Service Bus.
        :param topic_name: The name of the topic to which messages will be sent.
        :param subscription_name: The name of the subscription (optional for output).
        :param data_type: Defines how the Functions runtime should treat the
            parameter value. Defaults to DataType.UNDEFINED.
        :param access_rights: The access rights required for the connection string.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=ServiceBusTopicOutput(
                        name=arg_name,
                        connection=connection,
                        topic_name=topic_name,
                        subscription_name=subscription_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        access_rights=parse_singular_param_to_enum(
                            access_rights,
                            AccessRights),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def queue_output(self,
                     arg_name: str,
                     queue_name: str,
                     connection: str,
                     data_type: Optional[DataType] = None,
                     **kwargs) -> Callable[..., Any]:
        """
        The `queue_output` decorator adds :class:`QueueOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` used in
        the worker function indexing model.

        This is equivalent to defining `QueueOutput` in the `function.json`, which
        enables the function to write messages to an Azure Storage Queue.

        All optional fields will be given default values by the function host
        when parsed.

        Ref: https://aka.ms/azure-function-binding-queue

        :param arg_name: The name of the variable that represents the storage queue
            output object in the function code.
        :param queue_name: The name of the queue to which messages will be written.
        :param connection: The name of an app setting or setting collection that
            specifies how to connect to Azure Queues.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=QueueOutput(name=arg_name,
                                        queue_name=queue_name,
                                        connection=connection,
                                        data_type=parse_singular_param_to_enum(
                                            data_type, DataType),
                                        **kwargs))
                return fb

            return decorator()

        return wrap

    def event_hub_output(self,
                         arg_name: str,
                         connection: str,
                         event_hub_name: str,
                         data_type: Optional[
                             Union[DataType, str]] = None,
                         **kwargs) -> \
            Callable[..., Any]:
        """
        The `event_hub_output` decorator adds :class:`EventHubOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This is equivalent to defining `EventHubOutput` in the `function.json`,
        which enables the function to write messages to an Azure Event Hub.

        All optional fields will be given default values by the function host
        when parsed.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable representing the Event Hub output
            object in the function code.
        :param connection: The name of an app setting or setting collection that
            specifies how to connect to Event Hub.
        :param event_hub_name: The name of the Event Hub to send messages to.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=EventHubOutput(
                        name=arg_name,
                        connection=connection,
                        event_hub_name=event_hub_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def cosmos_db_output_v3(self,
                            arg_name: str,
                            database_name: str,
                            collection_name: str,
                            connection_string_setting: str,
                            create_if_not_exists: Optional[bool] = None,
                            partition_key: Optional[str] = None,
                            collection_throughput: Optional[int] = None,
                            use_multiple_write_locations: Optional[
                                bool] = None,
                            preferred_locations: Optional[str] = None,
                            data_type: Optional[
                                Union[DataType, str]] = None,
                            **kwargs) \
            -> Callable[..., Any]:
        """
        The `cosmos_db_output_v3` decorator adds :class:`CosmosDBOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 2.x or 3.x. It is equivalent
        to defining `CosmosDBOutput` in the `function.json`, which enables the
        function to write to Azure Cosmos DB. All optional fields are assigned
        default values by the function host when parsed.

        For additional details, see: https://aka.ms/cosmosdb-v4-update
        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents the Cosmos DB
            output object in the function code.
        :param database_name: The name of the Azure Cosmos DB database containing
            the monitored collection.
        :param collection_name: The name of the collection to which documents
            are written.
        :param connection_string_setting: The name of an app setting or setting
            collection that specifies how to connect to the Azure Cosmos DB account.
        :param create_if_not_exists: A boolean indicating whether the collection
            should be created automatically if it does not exist.
        :param partition_key: When `create_if_not_exists` is `True`, this defines
            the partition key path for the created collection.
        :param collection_throughput: When `create_if_not_exists` is `True`, this
            defines the throughput (Request Units) for the created collection.
        :param use_multiple_write_locations: When set to `True` and used in
            conjunction with `preferred_locations`, this enables multi-region writes
            in the Azure Cosmos DB service.
        :param preferred_locations: Preferred geographic regions for geo-replicated
            database accounts in Azure Cosmos DB.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=CosmosDBOutputV3(
                        name=arg_name,
                        database_name=database_name,
                        collection_name=collection_name,
                        connection_string_setting=connection_string_setting,
                        create_if_not_exists=create_if_not_exists,
                        partition_key=partition_key,
                        collection_throughput=collection_throughput,
                        use_multiple_write_locations=use_multiple_write_locations,  # NoQA
                        preferred_locations=preferred_locations,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def cosmos_db_output(self,
                         arg_name: str,
                         connection: str,
                         database_name: str,
                         container_name: str,
                         create_if_not_exists: Optional[bool] = None,
                         partition_key: Optional[str] = None,
                         container_throughput: Optional[int] = None,
                         preferred_locations: Optional[str] = None,
                         data_type: Optional[
                             Union[DataType, str]] = None,
                         **kwargs) \
            -> Callable[..., Any]:
        """
        The `cosmos_db_output` decorator adds :class:`CosmosDBOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 4.x and above. It is
        equivalent to defining `CosmosDBOutput` in the `function.json`, which
        enables the function to write to Azure Cosmos DB. All optional fields are
        assigned default values by the function host when parsed.

        For additional details, see: https://aka.ms/cosmosdb-v4-update
        Ref: https://aka.ms/azure-function-binding-cosmosdb-v4

        :param arg_name: The name of the variable that represents the Cosmos DB
            output object in the function code.
        :param connection: The name of an app setting or setting collection that
            specifies how to connect to the Azure Cosmos DB account.
        :param database_name: The name of the Azure Cosmos DB database containing
            the target container.
        :param container_name: The name of the container to which documents
            are written.
        :param create_if_not_exists: A boolean indicating whether the container
            should be created automatically if it does not exist.
        :param partition_key: When `create_if_not_exists` is `True`, this defines
            the partition key path for the created container.
        :param container_throughput: When `create_if_not_exists` is `True`, this
            defines the throughput (Request Units) for the created container.
        :param preferred_locations: Preferred geographic regions for geo-replicated
            database accounts in Azure Cosmos DB. When set along with
            `use_multiple_write_locations`, it enables multi-region writes.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=CosmosDBOutput(
                        name=arg_name,
                        connection=connection,
                        database_name=database_name,
                        container_name=container_name,
                        create_if_not_exists=create_if_not_exists,
                        partition_key=partition_key,
                        container_throughput=container_throughput,
                        preferred_locations=preferred_locations,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def cosmos_db_input_v3(self,
                           arg_name: str,
                           database_name: str,
                           collection_name: str,
                           connection_string_setting: str,
                           id: Optional[str] = None,
                           sql_query: Optional[str] = None,
                           partition_key: Optional[str] = None,
                           data_type: Optional[
                               Union[DataType, str]] = None,
                           **kwargs) \
            -> Callable[..., Any]:
        """
        The `cosmos_db_input_v3` decorator adds :class:`CosmosDBInput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 2.x or 3.x. It is equivalent
        to defining `CosmosDBInput` in the `function.json`, which enables the
        function to read from Azure Cosmos DB. All optional fields are assigned
        default values by the function host when parsed.

        For additional details, see: https://aka.ms/cosmosdb-v4-update
        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents the
            :class:`DocumentList` input object in the function code.
        :param database_name: The name of the Azure Cosmos DB database containing
            the target collection.
        :param collection_name: The name of the collection that contains the document(s).
        :param connection_string_setting: The name of the app setting that contains
            the Azure Cosmos DB connection string.
        :param id: The ID of a single document to retrieve.
        :param sql_query: An Azure Cosmos DB SQL query used to retrieve
            multiple documents.
        :param partition_key: Specifies the partition key value for the lookup.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=CosmosDBInputV3(
                        name=arg_name,
                        database_name=database_name,
                        collection_name=collection_name,
                        connection_string_setting=connection_string_setting,
                        id=id,
                        sql_query=sql_query,
                        partition_key=partition_key,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def cosmos_db_input(self,
                        arg_name: str,
                        connection: str,
                        database_name: str,
                        container_name: str,
                        partition_key: Optional[str] = None,
                        id: Optional[str] = None,
                        sql_query: Optional[str] = None,
                        preferred_locations: Optional[str] = None,
                        data_type: Optional[
                            Union[DataType, str]] = None,
                        **kwargs) \
            -> Callable[..., Any]:
        """
        The `cosmos_db_input` decorator adds :class:`CosmosDBInput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle version 4.x and above.
        It is equivalent to defining `CosmosDBInput` in the `function.json`, which
        enables the function to read from Azure Cosmos DB.

        All optional fields will be assigned default values by the function host
        when they are parsed.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v4
        Additional details: https://aka.ms/cosmosdb-v4-update

        :param arg_name: The name of the variable that represents the
            :class:`DocumentList` input object in the function code.
        :param connection: The name of an app setting or setting container that specifies
            how to connect to the Azure Cosmos DB account being monitored.
        :param database_name: The name of the Cosmos DB database that contains the document.
        :param container_name: The name of the container that holds the document.
        :param partition_key: The partition key value for the document lookup.
        :param id: The ID of the document to retrieve.
        :param sql_query: An Azure Cosmos DB SQL query used to retrieve multiple documents.
        :param preferred_locations: (Optional) Preferred geo-replicated regions. Values should be
            comma-separated, e.g., "East US,South Central US,North Europe".
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional binding fields to include in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=CosmosDBInput(
                        name=arg_name,
                        connection=connection,
                        database_name=database_name,
                        container_name=container_name,
                        partition_key=partition_key,
                        id=id,
                        sql_query=sql_query,
                        preferred_locations=preferred_locations,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def blob_input(self,
                   arg_name: str,
                   path: str,
                   connection: str,
                   data_type: Optional[DataType] = None,
                   **kwargs) -> Callable[..., Any]:
        """
        The `blob_input` decorator adds :class:`BlobInput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used
        in the worker function indexing model.

        This is equivalent to defining `BlobInput` in the `function.json`, which
        enables the function to read from Azure Storage blobs.

        All optional fields will be assigned default values by the function host
        when parsed.

        Ref: https://aka.ms/azure-function-binding-storage-blob

        :param arg_name: The name of the variable that represents the blob in the function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection that specifies
            how to connect to Azure Blobs.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Keyword arguments for specifying additional binding fields to include
            in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=BlobInput(
                        name=arg_name,
                        path=path,
                        connection=connection,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def blob_output(self,
                    arg_name: str,
                    path: str,
                    connection: str,
                    data_type: Optional[DataType] = None,
                    **kwargs) -> Callable[..., Any]:
        """
        The `blob_output` decorator adds :class:`BlobOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used
        in the worker function indexing model.

        This is equivalent to defining `BlobOutput` in the `function.json`, which
        enables the function to write message(s) to Azure Storage blobs.

        All optional fields will be assigned default values by the function host
        when parsed.

        Ref: https://aka.ms/azure-function-binding-storage-blob

        :param arg_name: The name of the variable that represents the blob in the function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection that specifies
            how to connect to Azure Blobs.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Keyword arguments for specifying additional binding fields to include
            in the binding JSON.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=BlobOutput(
                        name=arg_name,
                        path=path,
                        connection=connection,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def event_grid_output(self,
                          arg_name: str,
                          topic_endpoint_uri: Optional[str] = None,
                          topic_key_setting: Optional[str] = None,
                          connection: Optional[str] = None,
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) -> Callable[..., Any]:
        """
        The `event_grid_output` decorator adds :class:`EventGridOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used
        in the worker function indexing model.

        This is equivalent to defining the output binding in the `function.json`,
        which enables the function to write events to a custom topic.

        All optional fields will be assigned default values by the function host
        when parsed.

        Ref: https://aka.ms/eventgridtrigger

        :param arg_name: The variable name used in the function code that represents the event.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param topic_endpoint_uri: The name of an app setting that contains the URI for the
            custom topic.
        :param topic_key_setting: The name of an app setting that contains an access key for the
            custom topic.
        :param connection: The value of the common prefix for the setting that contains the topic
            endpoint URI.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=EventGridOutput(
                        name=arg_name,
                        topic_endpoint_uri=topic_endpoint_uri,
                        topic_key_setting=topic_key_setting,
                        connection=connection,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def kafka_output(self,
                     arg_name: str,
                     topic: str,
                     broker_list: str,
                     avro_schema: Optional[str] = None,
                     username: Optional[str] = None,
                     password: Optional[str] = None,
                     ssl_key_location: Optional[str] = None,
                     ssl_ca_location: Optional[str] = None,
                     ssl_certificate_location: Optional[str] = None,
                     ssl_key_password: Optional[str] = None,
                     schema_registry_url: Optional[str] = None,
                     schema_registry_username: Optional[str] = None,
                     schema_registry_password: Optional[str] = None,
                     o_auth_bearer_method: Optional[Union[OAuthBearerMethod, str]] = None,  # noqa E501
                     o_auth_bearer_client_id: Optional[str] = None,
                     o_auth_bearer_client_secret: Optional[str] = None,
                     o_auth_bearer_scope: Optional[str] = None,
                     o_auth_bearer_token_endpoint_url: Optional[str] = None,
                     o_auth_bearer_extensions: Optional[str] = None,
                     max_message_bytes: int = 1_000_000,
                     batch_size: int = 10_000,
                     enable_idempotence: bool = False,
                     message_timeout_ms: int = 300_000,
                     request_timeout_ms: int = 5_000,
                     max_retries: int = 2_147_483_647,
                     authentication_mode: Optional[Union[BrokerAuthenticationMode, str]] = "NOTSET",  # noqa E501
                     protocol: Optional[Union[BrokerProtocol, str]] = "NOTSET",
                     linger_ms: int = 5,
                     data_type: Optional[Union[DataType, str]] = None,
                     **kwargs) -> Callable[..., Any]:
        """
        The `kafka_output` decorator adds :class:`KafkaOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This is equivalent to defining a Kafka output binding in `function.json`,
        which enables the function to write events to a Kafka topic. All optional
        fields are assigned default values by the function host when parsed.

        Ref: https://aka.ms/kafkaoutput

        :param arg_name: The variable name used in the function code that
            represents the output event.
        :param topic: The Kafka topic to which messages are published.
        :param broker_list: The list of Kafka brokers to which the producer connects.
        :param avro_schema: Optional. Avro schema to generate a generic record.
        :param username: SASL username for use with the PLAIN and SASL-SCRAM
            mechanisms. Equivalent to `'sasl.username'` in librdkafka.
        :param password: SASL password for use with the PLAIN and SASL-SCRAM
            mechanisms. Equivalent to `'sasl.password'` in librdkafka.
        :param ssl_key_location: Path to the client's private key (PEM) for
            authentication. Equivalent to `'ssl.key.location'` in librdkafka.
        :param ssl_ca_location: Path to the CA certificate for verifying the broker's
            certificate. Equivalent to `'ssl.ca.location'` in librdkafka.
        :param ssl_certificate_location: Path to the client's certificate file.
            Equivalent to `'ssl.certificate.location'` in librdkafka.
        :param ssl_key_password: Password for the client's SSL key.
            Equivalent to `'ssl.key.password'` in librdkafka.
        :param schema_registry_url: URL of the Avro Schema Registry.
        :param schema_registry_username: Username for accessing the Schema Registry.
        :param schema_registry_password: Password for accessing the Schema Registry.
        :param o_auth_bearer_method: OAuth bearer method to use, e.g., `'default'` or `'oidc'`.
            Equivalent to `'sasl.oauthbearer.method'` in librdkafka.
        :param o_auth_bearer_client_id: Used with `oidc` method. Equivalent to
            `'sasl.oauthbearer.client.id'` in librdkafka.
        :param o_auth_bearer_client_secret: Used with `oidc` method. Equivalent to
            `'sasl.oauthbearer.client.secret'` in librdkafka.
        :param o_auth_bearer_scope: Scope of the access request sent to the broker.
            Equivalent to `'sasl.oauthbearer.scope'` in librdkafka.
        :param o_auth_bearer_token_endpoint_url: OAuth token endpoint.
            Equivalent to `'sasl.oauthbearer.token.endpoint.url'` in librdkafka.
        :param o_auth_bearer_extensions: Additional metadata sent to the broker.
            Comma-separated key=value pairs, e.g.,
            `"supportFeatureX=true,organizationId=sales-emea"`.
            Equivalent to `'sasl.oauthbearer.extensions'` in librdkafka.
        :param max_message_bytes: Maximum size (in bytes) of a transmitted message.
            Default is 1MB.
        :param batch_size: Maximum number of messages batched in one MessageSet.
            Default is 10,000.
        :param enable_idempotence: If `True`, ensures messages are delivered exactly
            once and in order. Default is `False`.
        :param message_timeout_ms: Local timeout for message delivery. Default is 300000 ms.
        :param request_timeout_ms: Timeout for producer request acknowledgment.
            Default is 5000 ms.
        :param max_retries: Maximum number of retry attempts for failed messages.
            Default is 2147483647. Retrying may cause reordering unless
            `enable_idempotence=True`.
        :param authentication_mode: SASL mechanism used for authentication.
            Allowed values: `Gssapi`, `Plain`, `ScramSha256`, `ScramSha512`.
            Default is `Plain`. Equivalent to `'sasl.mechanism'` in librdkafka.
        :param protocol: Security protocol used for broker communication.
            Default is plaintext. Equivalent to `'security.protocol'` in librdkafka.
        :param linger_ms: Time to wait between sending batches of messages to allow
            for better throughput via batching.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=KafkaOutput(
                        name=arg_name,
                        topic=topic,
                        broker_list=broker_list,
                        avro_schema=avro_schema,
                        username=username,
                        password=password,
                        ssl_key_location=ssl_key_location,
                        ssl_ca_location=ssl_ca_location,
                        ssl_certificate_location=ssl_certificate_location,
                        ssl_key_password=ssl_key_password,
                        schema_registry_url=schema_registry_url,
                        schema_registry_username=schema_registry_username,
                        schema_registry_password=schema_registry_password,
                        o_auth_bearer_method=parse_singular_param_to_enum(
                            o_auth_bearer_method, OAuthBearerMethod),
                        o_auth_bearer_client_id=o_auth_bearer_client_id,
                        o_auth_bearer_client_secret=o_auth_bearer_client_secret,  # noqa: E501
                        o_auth_bearer_scope=o_auth_bearer_scope,
                        o_auth_bearer_token_endpoint_url=o_auth_bearer_token_endpoint_url,  # noqa: E501
                        o_auth_bearer_extensions=o_auth_bearer_extensions,
                        max_message_bytes=max_message_bytes,
                        batch_size=batch_size,
                        enable_idempotence=enable_idempotence,
                        message_timeout_ms=message_timeout_ms,
                        request_timeout_ms=request_timeout_ms,
                        max_retries=max_retries,
                        authentication_mode=parse_singular_param_to_enum(
                            authentication_mode, BrokerAuthenticationMode),
                        protocol=parse_singular_param_to_enum(protocol,
                                                              BrokerProtocol),
                        linger_ms=linger_ms,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def table_input(self,
                    arg_name: str,
                    connection: str,
                    table_name: str,
                    row_key: Optional[str] = None,
                    partition_key: Optional[str] = None,
                    take: Optional[int] = None,
                    filter: Optional[str] = None,
                    data_type: Optional[
                        Union[DataType, str]] = None) -> Callable[..., Any]:
        """
        The `table_input` decorator adds :class:`TableInput` to the :class:`FunctionBuilder`
        object for building a :class:`Function` object used in the worker function indexing model.

        This is equivalent to defining `TableInput` in the `function.json`, which enables the
        function to read from a table in Azure Storage or a Cosmos DB account.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/tablesbindings

        :param arg_name: The name of the variable that represents the table or entity in the
            function code.
        :param connection: The name of an app setting or setting collection that specifies how
            to connect to the table service.
        :param table_name: The name of the table.
        :param row_key: The row key of the table entity to read.
        :param partition_key: The partition key of the table entity to read.
        :param take: The maximum number of entities to return.
        :param filter: An OData filter expression to apply when retrieving entities.
        :param data_type: Defines how the Functions runtime should treat the parameter value.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=TableInput(
                        name=arg_name,
                        connection=connection,
                        table_name=table_name,
                        row_key=row_key,
                        partition_key=partition_key,
                        take=take,
                        filter=filter,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType)))
                return fb

            return decorator()

        return wrap

    def table_output(self,
                     arg_name: str,
                     connection: str,
                     table_name: str,
                     row_key: Optional[str] = None,
                     partition_key: Optional[str] = None,
                     data_type: Optional[
                         Union[DataType, str]] = None) -> Callable[..., Any]:
        """
        The `table_output` decorator adds :class:`TableOutput` to the :class:`FunctionBuilder`
        object for building a :class:`Function` object used in the worker function indexing model.

        This is equivalent to defining `TableOutput` in the `function.json`, which enables the
        function to write entities to a table in Azure Storage.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/tablesbindings

        :param arg_name: The name of the variable that represents the table or entity in the
            function code.
        :param connection: The name of an app setting or setting collection that specifies how
            to connect to the table service.
        :param table_name: The name of the table.
        :param row_key: The row key of the table entity to read.
        :param partition_key: The partition key of the table entity to read.
        :param data_type: Defines how the Functions runtime should treat the parameter value.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=TableOutput(
                        name=arg_name,
                        connection=connection,
                        table_name=table_name,
                        row_key=row_key,
                        partition_key=partition_key,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType)))
                return fb

            return decorator()

        return wrap

    def sql_input(self,
                  arg_name: str,
                  command_text: str,
                  connection_string_setting: str,
                  command_type: Optional[str] = 'Text',
                  parameters: Optional[str] = None,
                  data_type: Optional[DataType] = None,
                  **kwargs) -> Callable[..., Any]:
        """
        The `sql_input` decorator adds :class:`SqlInput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 4.x and above. It is
        equivalent to defining `SqlInput` in the `function.json`, which enables the
        function to read from a SQL database. All optional fields are assigned
        default values by the function host when parsed.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents a
            :class:`SqlRowList` input object in the function code.
        :param command_text: The Transact-SQL query or the name of the stored
            procedure executed by the binding.
        :param connection_string_setting: The name of the app setting that contains
            the connection string to the target SQL database.
        :param command_type: The command type. Use `"Text"` for a raw SQL query and
            `"StoredProcedure"` for a stored procedure.
        :param parameters: A comma-separated string of parameter assignments to pass
            to the SQL command. Format:
            `@param1=value1,@param2=value2`
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields to
            include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=SqlInput(
                        name=arg_name,
                        command_text=command_text,
                        connection_string_setting=connection_string_setting,
                        command_type=command_type,
                        parameters=parameters,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def sql_output(self,
                   arg_name: str,
                   command_text: str,
                   connection_string_setting: str,
                   data_type: Optional[DataType] = None,
                   **kwargs) -> Callable[..., Any]:
        """
        The `sql_output` decorator adds :class:`SqlOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 4.x and above. It is
        equivalent to defining `SqlOutput` in the `function.json`, which enables
        the function to write to a SQL database. All optional fields are assigned
        default values by the function host when parsed.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents the SQL output
            object in the function code.
        :param command_text: The Transact-SQL query or the name of the stored
            procedure executed by the binding.
        :param connection_string_setting: The name of the app setting that contains
            the connection string to the target SQL database.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields to
            include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=SqlOutput(
                        name=arg_name,
                        command_text=command_text,
                        connection_string_setting=connection_string_setting,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def generic_input_binding(self,
                              arg_name: str,
                              type: str,
                              data_type: Optional[Union[DataType, str]] = None,
                              **kwargs
                              ) -> Callable[..., Any]:
        """
        The `generic_input_binding` decorator adds :class:`GenericInputBinding` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used in the
        worker function indexing model.

        This is equivalent to defining a generic input binding in the `function.json`, which
        enables the function to read data from a custom-defined input source.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of the input parameter in the function code.
        :param type: The type of the binding.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields in the
            `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=GenericInputBinding(
                        name=arg_name,
                        type=type,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def generic_output_binding(self,
                               arg_name: str,
                               type: str,
                               data_type: Optional[
                                   Union[DataType, str]] = None,
                               **kwargs
                               ) -> Callable[..., Any]:
        """
        The `generic_output_binding` decorator adds :class:`GenericOutputBinding` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used in the
        worker function indexing model.

        This is equivalent to defining a generic output binding in the `function.json`, which
        enables the function to write data to a custom-defined output source.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of the output parameter in the function code.
        :param type: The type of the binding.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields in the
            `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=GenericOutputBinding(
                        name=arg_name,
                        type=type,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_state_input(self,
                         arg_name: str,
                         state_store: str,
                         key: str,
                         dapr_address: Optional[str] = None,
                         data_type: Optional[
                             Union[DataType, str]] = None,
                         **kwargs) \
            -> Callable[..., Any]:
        """
        The `dapr_state_input` decorator adds :class:`DaprStateInput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used in the
        worker function indexing model.

        This is equivalent to defining `DaprStateInput` in the `function.json`, which enables
        the function to read state from the underlying state store component.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-dapr-state-input-binding

        :param arg_name: The name of the variable that represents the Dapr state input object
            in the function code.
        :param state_store: The state store containing the state.
        :param key: The name of the key to retrieve.
        :param dapr_address: The Dapr address. Optional;
            Defaults to http://localhost:{daprHttpPort}.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields in the
            `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprStateInput(
                        name=arg_name,
                        state_store=state_store,
                        key=key,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_secret_input(self,
                          arg_name: str,
                          secret_store_name: str,
                          key: str,
                          metadata: str,
                          dapr_address: Optional[str] = None,
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) \
            -> Callable[..., Any]:
        """
        The `dapr_secret_input` decorator adds :class:`DaprSecretInput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used in the
        worker function indexing model.

        This is equivalent to defining `DaprSecretInput` in the `function.json`, which enables
        the function to read secrets from the underlying secret store component.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-dapr-secret-input-binding

        :param arg_name: The name of the variable that represents the Dapr state input object
            in the function code.
        :param secret_store_name: The name of the secret store from which to retrieve the secret.
        :param key: The key identifying the name of the secret to retrieve.
        :param metadata: Metadata properties in the form "key1=value1&key2=value2".
        :param dapr_address: The Dapr address. Optional;
            Defaults to http://localhost:{daprHttpPort}.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields in the
            `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprSecretInput(
                        name=arg_name,
                        secret_store_name=secret_store_name,
                        key=key,
                        metadata=metadata,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_state_output(self,
                          arg_name: str,
                          state_store: str,
                          key: str,
                          dapr_address: Optional[str] = None,
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) \
            -> Callable[..., Any]:
        """
        The `dapr_state_output` decorator adds :class:`DaprStateOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used in
        the worker function indexing model.

        This is equivalent to defining `DaprStateOutput` in the `function.json`, which
        enables the function to write to the Dapr state store.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-dapr-state-output-binding

        :param arg_name: The name of the variable that represents the Dapr state
            output object in the function code.
        :param state_store: The state store containing the state for the specified keys.
        :param key: The name of the key used to store the state.
        :param dapr_address: The Dapr address. Optional; defaults to
            http://localhost:{daprHttpPort}.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields in the
            `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprStateOutput(
                        name=arg_name,
                        state_store=state_store,
                        key=key,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_invoke_output(self,
                           arg_name: str,
                           app_id: str,
                           method_name: str,
                           http_verb: str,
                           dapr_address: Optional[str] = None,
                           data_type: Optional[
                               Union[DataType, str]] = None,
                           **kwargs) \
            -> Callable[..., Any]:
        """
        The `dapr_invoke_output` decorator adds :class:`DaprInvokeOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used in
        the worker function indexing model.

        This is equivalent to defining `DaprInvokeOutput` in the `function.json`, which
        enables the function to invoke another Dapr app.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-dapr-invoke-output-binding

        :param arg_name: The name of the variable that represents the Dapr state output
            object in the function code.
        :param app_id: The Dapr app ID to invoke.
        :param method_name: The method name of the app to invoke.
        :param http_verb: The HTTP verb to use for the invocation (e.g., GET, POST).
        :param dapr_address: The Dapr address. Optional; defaults to
            http://localhost:{daprHttpPort}.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields in the
            `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprInvokeOutput(
                        name=arg_name,
                        app_id=app_id,
                        method_name=method_name,
                        http_verb=http_verb,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_publish_output(self,
                            arg_name: str,
                            pub_sub_name: str,
                            topic: str,
                            dapr_address: Optional[str] = None,
                            data_type: Optional[
                                Union[DataType, str]] = None,
                            **kwargs) \
            -> Callable[..., Any]:
        """
        The `dapr_publish_output` decorator adds :class:`DaprPublishOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used in
        the worker function indexing model.

        This is equivalent to defining `DaprPublishOutput` in the `function.json`, which
        enables the function to publish to a topic.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-dapr-publish-output-binding

        :param arg_name: The name of the variable that represents the Dapr state output
            object in the function code.
        :param pub_sub_name: The pub/sub component name to publish to.
        :param topic: The name of the topic to publish to.
        :param dapr_address: The Dapr address. Optional; defaults to
            http://localhost:{daprHttpPort}.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields in the
            `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprPublishOutput(
                        name=arg_name,
                        pub_sub_name=pub_sub_name,
                        topic=topic,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_binding_output(self,
                            arg_name: str,
                            binding_name: str,
                            operation: str,
                            dapr_address: Optional[str] = None,
                            data_type: Optional[
                                Union[DataType, str]] = None,
                            **kwargs) \
            -> Callable[..., Any]:
        """
        The `dapr_binding_output` decorator adds :class:`DaprBindingOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object used in
        the worker function indexing model.

        This is equivalent to defining `DaprBindingOutput` in the `function.json`, which
        enables the function to send a value to a Dapr output binding.

        All optional fields will be assigned default values by the function host when parsed.

        Ref: https://aka.ms/azure-function-dapr-binding-output-binding

        :param arg_name: The name of the variable that represents the Dapr state output
            object in the function code.
        :param binding_name: The configured name of the binding.
        :param operation: The configured operation.
        :param dapr_address: The Dapr address. Optional; defaults to
            http://localhost:{daprHttpPort}.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields in the
            `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprBindingOutput(
                        name=arg_name,
                        binding_name=binding_name,
                        operation=operation,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def text_completion_input(self,
                              arg_name: str,
                              prompt: str,
                              ai_connection_name: Optional[str] = "",
                              chat_model: Optional
                              [Union[str, OpenAIModels]]
                              = OpenAIModels.DefaultChatModel,
                              temperature: Optional[str] = "0.5",
                              top_p: Optional[str] = None,
                              max_tokens: Optional[str] = "100",
                              is_reasoning_model: Optional[bool] = False,
                              data_type: Optional[Union[DataType, str]] = None,
                              **kwargs) \
            -> Callable[..., Any]:
        """
        The `textCompletion` input binding is used to invoke the OpenAI Chat Completions API
        and return the generated results to the function.

        Ref: https://platform.openai.com/docs/guides/text-generation/chat-completions-vs-completions

        The examples typically define an HTTP-triggered function with a hardcoded
        prompt such as `"who is {name}?"`, where `{name}` is dynamically substituted
        from the HTTP request path. The OpenAI input binding sends this prompt to the
        configured GPT model and returns the generated response to the function, which
        then returns the result as the HTTP response content.

        :param arg_name: The name of the binding parameter in the function code.
        :param prompt: The text prompt to generate completions for.
        :param ai_connection_name: The name of the configuration section that defines
            AI service connectivity settings.

            - For **Azure OpenAI**: If specified, it looks for `"Endpoint"` and/or
            `"Key"` in this section. If not specified or missing, it falls back to
            the environment variables `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY`.
            - For **user-assigned managed identity**, this setting is required.
            - For **non-Azure OpenAI**, ensure the `OPENAI_API_KEY` environment
            variable is set.

        :param model: *(Deprecated)* Use `chat_model` instead. This parameter is
            unused and will be removed in future versions.
        :param chat_model: The deployment or model name to use for the Chat
            Completions API. Default is `"gpt-3.5-turbo"`.
        :param temperature: Sampling temperature (0–2). Higher values (e.g., 0.8)
            produce more random output; lower values (e.g., 0.2) make output more
            focused and deterministic.
        :param top_p: Controls nucleus sampling. For example, `top_p=0.1` considers
            only tokens in the top 10% cumulative probability. Recommended to use
            either `temperature` or `top_p`, but not both.
        :param max_tokens: The maximum number of tokens to generate. The sum of prompt
            tokens and `max_tokens` must not exceed the model’s context length
            (usually 2048 or 4096 for newer models).
        :param is_reasoning_model: If `True`, indicates that the configured chat model
            is a reasoning model. In this case, `max_tokens` and `temperature` are
            not supported.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=TextCompletionInput(
                        name=arg_name,
                        prompt=prompt,
                        ai_connection_name=ai_connection_name,
                        chat_model=chat_model,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        is_reasoning_model=is_reasoning_model,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def assistant_create_output(self, arg_name: str,
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                **kwargs) \
            -> Callable[..., Any]:
        """
        The `assistantCreate` output binding creates a new assistant with a specified system prompt.

        :param arg_name: The name of the binding parameter in the function code.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying extra binding fields
            to include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=AssistantCreateOutput(
                        name=arg_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def assistant_query_input(self,
                              arg_name: str,
                              id: str,
                              timestamp_utc: str,
                              chat_storage_connection_setting: Optional[str] = "AzureWebJobsStorage",       # noqa: E501
                              collection_name: Optional[str] = "ChatState",       # noqa: E501
                              data_type: Optional[
                                  Union[DataType, str]] = None,
                              **kwargs) \
            -> Callable[..., Any]:
        """
        The `assistantQuery` input binding retrieves assistant chat history and
        passes it to the function.

        This is typically used to provide the function access to previous messages
        in a conversation, enabling more context-aware responses.

        :param arg_name: The name of the binding parameter in the function code.
        :param timestamp_utc: The earliest timestamp (in UTC) for the messages to
            retrieve from the chat history. Must be in ISO 8601 format, e.g.,
            `"2023-08-01T00:00:00Z"`.
        :param chat_storage_connection_setting: The name of the configuration section
            containing the connection settings for assistant chat storage. Defaults to
            `"AzureWebJobsStorage"`.
        :param collection_name: The name of the table or collection used for assistant
            chat storage. Defaults to `"ChatState"`.
        :param id: The unique identifier of the assistant whose history is being
            queried.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments for specifying binding fields to
            include in the `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=AssistantQueryInput(
                        name=arg_name,
                        id=id,
                        timestamp_utc=timestamp_utc,
                        chat_storage_connection_setting=chat_storage_connection_setting,       # noqa: E501
                        collection_name=collection_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def assistant_post_input(self, arg_name: str,
                             id: str,
                             user_message: str,
                             ai_connection_name: Optional[str] = "",
                             chat_model: Optional
                             [Union[str, OpenAIModels]]
                             = OpenAIModels.DefaultChatModel,
                             chat_storage_connection_setting: Optional[str] = "AzureWebJobsStorage",       # noqa: E501
                             collection_name: Optional[str] = "ChatState",      # noqa: E501
                             temperature: Optional[str] = "0.5",
                             top_p: Optional[str] = None,
                             max_tokens: Optional[str] = "100",
                             is_reasoning_model: Optional[bool] = False,
                             data_type: Optional[
                                 Union[DataType, str]] = None,
                             **kwargs) \
            -> Callable[..., Any]:
        """
        The `assistantPost` output binding sends a message to the assistant and saves
        the response in its internal state.

        :param arg_name: The name of the binding parameter in the function code.
        :param id: The ID of the assistant to update.
        :param user_message: The message entered by the user for the assistant to
            respond to.
        :param ai_connection_name: The name of the configuration section for AI service
            connectivity.

            - **Azure OpenAI**: If specified, looks for "Endpoint" and/or "Key" in the section.
            - If not specified or missing, falls back to the `AZURE_OPENAI_ENDPOINT` and
              `AZURE_OPENAI_KEY` environment variables.
            - **Managed Identity**: Required for user-assigned identity auth.
            - **OpenAI (non-Azure)**: Set the `OPENAI_API_KEY` environment variable.

        :param model: *Deprecated.* Use `chat_model` instead. This parameter is unused
            and will be removed in future versions.
        :param chat_model: The deployment or model name of the OpenAI Chat Completion API.
            Default is `"gpt-3.5-turbo"`.
        :param chat_storage_connection_setting: The config section name for assistant
            chat table storage. Default is `"AzureWebJobsStorage"`.
        :param collection_name: The collection or table name used for assistant chat
            storage. Default is `"ChatState"`.
        :param temperature: Sampling temperature, between 0 and 2. Higher values
            (e.g., 0.8) increase randomness; lower values (e.g., 0.2) make output more
            deterministic.
        :param top_p: Alternative to temperature sampling. Uses nucleus sampling to
            consider only the tokens comprising the top `top_p` probability mass.
            Recommended to use either this or `temperature`.
        :param max_tokens: Maximum tokens to generate. Total tokens (prompt + output)
            must not exceed the model's context length.
        :param is_reasoning_model: Whether the chat model is a reasoning model. If
            true, `max_tokens` and `temperature` are not supported.
        :param data_type: Defines how the Functions runtime should treat the parameter value.
        :param kwargs: Additional keyword arguments for specifying extra binding fields
            in `function.json`.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=AssistantPostInput(
                        name=arg_name,
                        id=id,
                        user_message=user_message,
                        ai_connection_name=ai_connection_name,
                        chat_model=chat_model,
                        chat_storage_connection_setting=chat_storage_connection_setting,       # noqa: E501
                        collection_name=collection_name,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        is_reasoning_model=is_reasoning_model,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def embeddings_input(self,
                         arg_name: str,
                         input: str,
                         input_type: InputType,
                         ai_connection_name: Optional[str] = "",
                         embeddings_model: Optional
                         [Union[str, OpenAIModels]]
                         = OpenAIModels.DefaultEmbeddingsModel,
                         max_chunk_length: Optional[int] = 8 * 1024,
                         max_overlap: Optional[int] = 128,
                         data_type: Optional[
                             Union[DataType, str]] = None,
                         **kwargs) \
            -> Callable[..., Any]:
        """
        The embeddings input decorator generates embeddings used to measure the
        relatedness of text strings.

        Ref: https://platform.openai.com/docs/guides/embeddings

        :param arg_name: The name of the binding parameter in the function code.
        :param input: The input source containing the data to generate embeddings for.
        :param input_type: The type of the input (e.g., string, list, file reference).
        :param ai_connection_name: The name of the configuration section for AI service
            connectivity settings.

            - **Azure OpenAI**: If specified, looks for "Endpoint" and/or "Key" in this
              section.
            - If not specified or not found, falls back to the environment variables
              `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY`.
            - For user-assigned managed identity authentication, this is required.
            - **OpenAI (non-Azure)**: Set the `OPENAI_API_KEY` environment variable.

        :param model: *(Deprecated)* Use `embeddings_model` instead. This parameter is unused and
            will be removed in future versions.
        :param embeddings_model: The deployment or model name for OpenAI Embeddings.
            Default is `"text-embedding-ada-002"`.
        :param max_chunk_length: The maximum number of characters into which the input
            should be chunked. Default is `8 * 1024`.
        :param max_overlap: The maximum number of characters to overlap between input
            chunks. Default is `128`.
        :param data_type: Optional. Defines how the Functions runtime should interpret the
            parameter value.
        :param kwargs: Additional keyword arguments to include in the `function.json`
            binding configuration.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=EmbeddingsInput(
                        name=arg_name,
                        input=input,
                        input_type=input_type,
                        ai_connection_name=ai_connection_name,
                        embeddings_model=embeddings_model,
                        max_chunk_length=max_chunk_length,
                        max_overlap=max_overlap,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def semantic_search_input(self,
                              arg_name: str,
                              search_connection_name: str,
                              collection: str,
                              query: Optional[str] = None,
                              ai_connection_name: Optional[str] = "",
                              embeddings_model: Optional
                              [Union[str, OpenAIModels]]
                              = OpenAIModels.DefaultEmbeddingsModel,
                              chat_model: Optional
                              [Union[str, OpenAIModels]]
                              = OpenAIModels.DefaultChatModel,
                              system_prompt: Optional[str] = semantic_search_system_prompt,  # NoQA
                              max_knowledge_count: Optional[int] = 1,
                              temperature: Optional[str] = "0.5",
                              top_p: Optional[str] = None,
                              max_tokens: Optional[str] = "100",
                              is_reasoning_model: Optional[bool] = False,
                              data_type: Optional[
                                  Union[DataType, str]] = None,
                              **kwargs) \
            -> Callable[..., Any]:
        """
        Enable semantic search capabilities using vector databases and OpenAI models.

        This feature allows you to import documents into a vector database via an output binding
        and perform semantic queries against them via an input binding. For example, one function
        can import documents into the database, while another function issues queries to OpenAI
        using that data as context — a pattern known as Retrieval Augmented Generation (RAG).

        Ref: https://platform.openai.com/docs/guides/embeddings

        :param arg_name: The name of the binding parameter in the function code.
        :param search_connection_name: The name of the app setting or environment variable
            that contains the vector search connection value.
        :param collection: The name of the collection or table to search or store.
        :param query: The semantic query text used for searching the database.
        :param ai_connection_name: The name of the configuration section for AI service
            connectivity settings.

            - For Azure OpenAI: If specified, looks for "Endpoint" and/or "Key" in this
              configuration section.
            - If not specified or the section is missing, defaults to the environment variables
              `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY`.
            - For user-assigned managed identity authentication, this field is required.
            - For OpenAI (non-Azure), set the `OPENAI_API_KEY` environment variable.

        :param embeddings_model: The deployment or model name for OpenAI Embeddings.
            Defaults to "text-embedding-ada-002".
        :param chat_model: The deployment or model name for the OpenAI Chat Completion API.
            Defaults to "gpt-3.5-turbo".
        :param system_prompt: Optional. The system prompt provided to the large language model.
        :param max_knowledge_count: Optional. The number of knowledge items to inject into
            the system prompt. Default is 1.
        :param temperature: The sampling temperature to use (range: 0 to 2). Higher values like
            0.8 yield more random output; lower values like 0.2 make output more focused.
        :param top_p: Alternative to temperature sampling (nucleus sampling). For example, 0.1
            considers only the top 10% of tokens by probability mass. Use this or `temperature`.
        :param max_tokens: The maximum number of tokens to generate in the completion.
            The sum of prompt tokens and `max_tokens` must not exceed the model's context length
            (usually 2048 or 4096 for newer models).
        :param is_reasoning_model: Indicates whether the chat model is a reasoning model.
            If True, `max_tokens` and `temperature` are not supported.
        :param data_type: Optional. Defines how the Functions runtime should interpret the
            parameter value. Default is None.
        :param kwargs: Additional keyword arguments for specifying extra fields in the
            `function.json` binding.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=SemanticSearchInput(
                        name=arg_name,
                        search_connection_name=search_connection_name,
                        collection=collection,
                        query=query,
                        ai_connection_name=ai_connection_name,
                        embeddings_model=embeddings_model,
                        chat_model=chat_model,
                        system_prompt=system_prompt,
                        max_knowledge_count=max_knowledge_count,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        is_reasoning_model=is_reasoning_model,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def embeddings_store_output(self,
                                arg_name: str,
                                input: str,
                                input_type: InputType,
                                store_connection_name: str,
                                collection: str,
                                ai_connection_name: Optional[str] = "",
                                embeddings_model: Optional
                                [Union[str, OpenAIModels]]
                                = OpenAIModels.DefaultEmbeddingsModel,
                                max_chunk_length: Optional[int] = 8 * 1024,
                                max_overlap: Optional[int] = 128,
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                **kwargs) \
            -> Callable[..., Any]:
        """
        Add an embeddings input binding to the function.

        The supported list of embeddings stores is extensible. Additional providers can be
        integrated by authoring a specially crafted NuGet package. Refer to the provider-specific
        folders for detailed usage instructions:

        - Azure AI Search
        - Azure Data Explorer
        - Azure Cosmos DB using MongoDB

        :param arg_name: The name of the binding parameter in the function code.
        :param input: The input data for which embeddings should be generated.
        :param input_type: The type of the input (e.g., string, list).
        :param store_connection_name: The name of an app setting or environment variable
            containing the vector store connection value.
        :param collection: The collection or table to search within.
        :param ai_connection_name: The name of the configuration section for AI service
            connectivity settings.

            - For Azure OpenAI: If specified, looks for "Endpoint" and/or "Key" in this
              configuration section.
            - If not specified, or if the section is missing, falls back to environment
              variables: `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY`.
            - For user-assigned managed identity, this property is required.
            - For OpenAI (non-Azure), set the `OPENAI_API_KEY` environment variable.

        :param model: Deprecated. Use `embeddings_model` instead. This parameter is unused and
            will be removed in future versions.
        :param embeddings_model: The deployment or model name for OpenAI Embeddings. The default
            is "text-embedding-ada-002".
        :param max_chunk_length: The maximum number of characters to chunk the input into.
        :param max_overlap: The maximum number of characters to overlap between chunks.
        :param data_type: Optional. Defines how the Functions runtime should treat the parameter
            value. Defaults to None.
        :param kwargs: Additional keyword arguments to include in the `function.json` binding.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=EmbeddingsStoreOutput(
                        name=arg_name,
                        input=input,
                        input_type=input_type,
                        store_connection_name=store_connection_name,
                        collection=collection,
                        ai_connection_name=ai_connection_name,
                        embeddings_model=embeddings_model,
                        max_chunk_length=max_chunk_length,
                        max_overlap=max_overlap,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def mysql_input(self,
                    arg_name: str,
                    command_text: str,
                    connection_string_setting: str,
                    command_type: Optional[str] = 'Text',
                    parameters: Optional[str] = None,
                    data_type: Optional[DataType] = None,
                    **kwargs) -> Callable[..., Any]:
        """
        The `mysql_input` decorator adds :class:`MySqlInput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator works only with extension bundle 4.x and above. It is
        equivalent to defining `MySqlInput` in the `function.json`, which enables
        the function to read data from a MySQL database. All optional fields are
        automatically assigned default values by the function host when parsed.

        Ref: https://aka.ms/mysqlbindings

        :param arg_name: The name of the variable that represents a
            :class:`MySqlRowList` input object in the function code.
        :param command_text: The SQL query string or the name of the stored procedure
            to execute.
        :param connection_string_setting: The name of the app setting that contains
            the connection string to the MySQL database.
        :param command_type: The type of command being executed. Accepts `"Text"` for
            SQL queries or `"StoredProcedure"` for stored procedures.
        :param parameters: One or more parameter values passed to the SQL command.
            Should be provided as a comma-separated string in the format:
            `"@param1=value1,@param2=value2"`.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments used to define fields in the
            `function.json` binding.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=MySqlInput(
                        name=arg_name,
                        command_text=command_text,
                        connection_string_setting=connection_string_setting,
                        command_type=command_type,
                        parameters=parameters,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def mysql_output(self,
                     arg_name: str,
                     command_text: str,
                     connection_string_setting: str,
                     data_type: Optional[DataType] = None,
                     **kwargs) -> Callable[..., Any]:
        """
        The `mysql_output` decorator adds :class:`MySqlOutput` to the
        :class:`FunctionBuilder` object for building a :class:`Function` object
        used in the worker function indexing model.

        This decorator is supported only with extension bundle 4.x and above.
        It is equivalent to defining `MySqlOutput` in the `function.json`,
        enabling the function to write data to a MySQL database.

        All optional fields will be assigned default values by the function host
        when parsed.

        Ref: https://aka.ms/mysqlbindings

        :param arg_name: The name of the variable that represents the MySQL output
            object in the function code.
        :param command_text: The SQL command or the name of the stored procedure
            executed by the binding.
        :param connection_string_setting: The name of the app setting that contains
            the connection string for the target MySQL database.
        :param data_type: Defines how the Functions runtime should treat the
            parameter value.
        :param kwargs: Additional keyword arguments used to define fields in the
            `function.json` binding.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=MySqlOutput(
                        name=arg_name,
                        command_text=command_text,
                        connection_string_setting=connection_string_setting,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap


class SettingsApi(DecoratorApi, ABC):
    """Interface to extend for using an existing settings decorator in functions."""

    def retry(self,
              strategy: str,
              max_retry_count: str,
              delay_interval: Optional[str] = None,
              minimum_interval: Optional[str] = None,
              maximum_interval: Optional[str] = None,
              setting_extra_fields: Optional[Dict[str, Any]] = None,
              ) -> Callable[..., Any]:
        """
        The `retry` decorator adds a :class:`RetryPolicy` to the function settings object.

        Used for building a :class:`Function` object in the worker function indexing model.
        This is equivalent to defining a RetryPolicy in `function.json`, which enables
        the function to automatically retry on failure.

        All optional fields are assigned default values by the function host during parsing.

        Ref: https://aka.ms/azure_functions_retries

        :param strategy: The retry strategy to use.
        :param max_retry_count: The maximum number of retry attempts.
        :param delay_interval: The delay interval between retry attempts.
        :param minimum_interval: The minimum delay interval between retry attempts.
        :param maximum_interval: The maximum delay interval between retry attempts.
        :param setting_extra_fields: Keyword arguments for specifying additional setting fields.
        :return: Decorator function.
        """
        if setting_extra_fields is None:
            setting_extra_fields = {}

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_setting(setting=RetryPolicy(
                    strategy=strategy,
                    max_retry_count=max_retry_count,
                    minimum_interval=minimum_interval,
                    maximum_interval=maximum_interval,
                    delay_interval=delay_interval,
                    **setting_extra_fields))
                return fb

            return decorator()

        return wrap


class FunctionRegister(DecoratorApi, HttpFunctionsAuthLevelMixin, ABC):
    def __init__(self, auth_level: Union[AuthLevel, str], *args, **kwargs):
        """
        Initialize the top-level function app interface.

        This class will be directly indexed by the Python Functions runtime.

        :param auth_level: Determines what keys, if any, must be present
            on the request to invoke the function.
        :param args: Variable-length argument list.
        :param kwargs: Arbitrary keyword arguments.
        """
        DecoratorApi.__init__(self, *args, **kwargs)
        HttpFunctionsAuthLevelMixin.__init__(self, auth_level, *args, **kwargs)
        self._require_auth_level: Optional[bool] = None
        self.functions_bindings: Optional[Dict[Any, Any]] = None

    def get_functions(self) -> List[Function]:
        """
        Get the function objects in the function app.

        :return: A list of :class:`Function` objects defined in the app.
        """
        functions = [function_builder.build(self.auth_level)
                     for function_builder in self._function_builders]

        if not self._require_auth_level:
            self._require_auth_level = any(
                function.is_http_function() for function in functions)

        if not self._require_auth_level:
            logging.warning(
                'Auth level is not applied to non http '
                'function app. Ref: '
                'https://docs.microsoft.com/azure/azure-functions/functions'
                '-bindings-http-webhook-trigger?tabs=in-process'
                '%2Cfunctionsv2&pivots=programming-language-python#http-auth')

        self.validate_function_names(functions=functions)

        return functions

    def validate_function_names(self, functions: List[Function]):
        """
        Validate that all functions have unique names within the app.

        The `functions_bindings` dictionary maps function names to their bindings.
        If multiple functions share the same name, indexing will fail.

        :param functions: A list of :class:`Function` objects to validate.
        :raises ValueError: If any function name is duplicated.
        """
        if not self.functions_bindings:
            self.functions_bindings = {}
        for function in functions:
            function_name = function.get_function_name()
            if function_name in self.functions_bindings:
                raise ValueError(
                    f"Function {function_name} does not have a unique"
                    f" function name. Please change @app.function_name() or"
                    f" the function method name to be unique.")
            # The value of the key doesn't matter. We're using a dict for
            # faster lookup times.
            self.functions_bindings[function_name] = True

    def register_functions(self, function_container: DecoratorApi) -> None:
        """
        Register a list of functions in the function app.

        :param function_container: Instance extending :class:`DecoratorApi`,
            which contains a list of functions to be registered.
        :raises TypeError: If the provided container is an instance of
            :class:`FunctionRegister`.
        """
        if isinstance(function_container, FunctionRegister):
            raise TypeError('functions can not be type of FunctionRegister!')
        self._function_builders.extend(function_container._function_builders)

    register_blueprint = register_functions


class FunctionApp(FunctionRegister, TriggerApi, BindingApi, SettingsApi):
    """
    FunctionApp object used by the worker function indexing model.

    Captures user-defined functions and associated metadata.

    Ref: https://aka.ms/azure-function-ref
    """

    def __init__(self,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        """
        Initialize a :class:`FunctionApp` object.

        :param http_auth_level: Determines what keys, if any, must be present
            on the request in order to invoke the function. Defaults to
            `AuthLevel.FUNCTION`.
        """
        super().__init__(auth_level=http_auth_level)


class Blueprint(TriggerApi, BindingApi, SettingsApi):
    """
    Container class for Azure Functions.

    This class holds all available trigger and binding decorator functions.
    Functions loaded into this container can be registered in
    :class:`FunctionRegister` subclasses, but the container itself
    cannot be directly indexed.
    """

    pass


class ExternalHttpFunctionApp(
    FunctionRegister,
    TriggerApi,
    SettingsApi,
    BindingApi,
    ABC
):
    """Interface to extend for building third party http function apps."""

    @abc.abstractmethod
    def _add_http_app(self,
                      http_middleware: Union[
                          AsgiMiddleware, WsgiMiddleware],
                      function_name: str = 'http_app_func') -> None:
        """
        Add a WSGI or ASGI app as an integrated HTTP function.

        :param http_middleware: An instance of either :class:`WsgiMiddleware` or
            :class:`AsgiMiddleware` to handle incoming HTTP requests.
        :param function_name: The name to assign to the registered function.
            Defaults to `'http_app_func'`.

        :return: None

        :raises NotImplementedError: Always raised since this method must be
            implemented by a subclass.
        """
        raise NotImplementedError()


class AsgiFunctionApp(ExternalHttpFunctionApp):
    def __init__(self, app,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION,
                 function_name: str = 'http_app_func'):
        """
        Initialize an :class:`AsgiFunctionApp` instance.

        :param app: The ASGI application instance.
        :param http_auth_level: Determines what keys, if any, need to be
            present on the request to invoke the function. Defaults to `AuthLevel.FUNCTION`.
        :param function_name: The name to assign to the registered function.
            Defaults to `'http_app_func'`.
        """
        super().__init__(auth_level=http_auth_level)
        self.middleware = AsgiMiddleware(app)
        self._add_http_app(self.middleware, function_name)
        self.startup_task_done = False

    def __del__(self):
        if self.startup_task_done:
            asyncio.run(self.middleware.notify_shutdown())

    def _add_http_app(self,
                      http_middleware: Union[
                          AsgiMiddleware, WsgiMiddleware],
                      function_name: str = 'http_app_func') -> None:
        """
        Add an ASGI app-integrated HTTP function.

        :param http_middleware: An instance of :class:`AsgiMiddleware` or :class:`WsgiMiddleware`.
        :param function_name: The name to assign to the registered function.
            Defaults to 'http_app_func'.
        :raises TypeError: If the provided `http_middleware` is not an instance
            of :class:`AsgiMiddleware`.
        :return: None.
        """
        if not isinstance(http_middleware, AsgiMiddleware):
            raise TypeError("Please pass AsgiMiddleware instance"
                            " as parameter.")

        asgi_middleware: AsgiMiddleware = http_middleware

        @self.function_name(name=function_name)
        @self.http_type(http_type='asgi')
        @self.route(methods=(method for method in HttpMethod),
                    auth_level=self.auth_level,
                    route="/{*route}")
        async def http_app_func(req: HttpRequest, context: Context):
            if not self.startup_task_done:
                success = await asgi_middleware.notify_startup()
                if not success:
                    raise RuntimeError("ASGI middleware startup failed.")
                self.startup_task_done = True

            return await asgi_middleware.handle_async(req, context)


class WsgiFunctionApp(ExternalHttpFunctionApp):
    def __init__(self, app,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION,
                 function_name: str = 'http_app_func'):
        """
        Initialize a :class:`WsgiFunctionApp` object.

        :param app: The WSGI application object to wrap.
        :param http_auth_level: The HTTP authorization level for the function.
            Can be an instance of :class:`AuthLevel` or a string. Defaults to AuthLevel.FUNCTION.
        :param function_name: The name to assign to the registered function.
            Defaults to 'http_app_func'.
        """
        super().__init__(auth_level=http_auth_level)
        self._add_http_app(WsgiMiddleware(app), function_name)

    def _add_http_app(self,
                      http_middleware: Union[
                          AsgiMiddleware, WsgiMiddleware],
                      function_name: str = 'http_app_func') -> None:
        """
        Add a WSGI app-integrated HTTP function.

        This registers a function that handles HTTP requests using a WSGI middleware instance.

        :param http_middleware: Middleware instance to handle HTTP requests.
        :param function_name: Name to assign to the registered function.
        :raises TypeError: If `http_middleware` is not a WsgiMiddleware instance.
        :return: None
        """
        if not isinstance(http_middleware, WsgiMiddleware):
            raise TypeError("Please pass WsgiMiddleware instance"
                            " as parameter.")

        wsgi_middleware: WsgiMiddleware = http_middleware

        @self.function_name(function_name)
        @self.http_type(http_type='wsgi')
        @self.route(methods=(method for method in HttpMethod),
                    auth_level=self.auth_level,
                    route="/{*route}")
        def http_app_func(req: HttpRequest, context: Context):
            return wsgi_middleware.handle(req, context)
