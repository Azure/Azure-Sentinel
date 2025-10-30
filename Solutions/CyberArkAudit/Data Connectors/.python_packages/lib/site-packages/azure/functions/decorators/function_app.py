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
    AuthLevel, SCRIPT_FILE_NAME, Cardinality, AccessRights, Setting
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
from .retry_policy import RetryPolicy
from .function_name import FunctionName
from .warmup import WarmUpTrigger
from .._http_asgi import AsgiMiddleware
from .._http_wsgi import WsgiMiddleware, Context


class Function(object):
    """The function object represents a function in Function App. It
    encapsulates function metadata and callable and used in the worker
    function indexing model. Ref: https://aka.ms/azure-function-ref
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

    def __str__(self):
        return self.get_function_json()


class FunctionBuilder(object):
    def __init__(self, func, function_script_file):
        self._function = Function(func, function_script_file)

    def __call__(self, *args, **kwargs):
        pass

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

    @property
    def app_script_file(self) -> str:
        """Name of function app script file in which all the functions
         are defined. \n
         Script file defined here is for placeholder purpose, please refer to
         worker defined script file path as the single point of truth.

        :return: Script file name.
        """
        return self._app_script_file

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
    """Interface to extend for enabling function app level http
    authorization level setting"""

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
              trigger_extra_fields: Dict[str, Any] = {},
              binding_extra_fields: Dict[str, Any] = {}
              ) -> Callable[..., Any]:
        """The route decorator adds :class:`HttpTrigger` and
        :class:`HttpOutput` binding to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining HttpTrigger
        and HttpOutput binding in the function.json which enables your
        function be triggered when http requests hit the specified route.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-http

        :param route: Route for the http endpoint, if None, it will be set
        to function name if present or user defined python function name.
        :param trigger_arg_name: Argument name for :class:`HttpRequest`,
        defaults to 'req'.
        :param binding_arg_name: Argument name for :class:`HttpResponse`,
        defaults to '$return'.
        :param methods: A tuple of the HTTP methods to which the function
        responds.
        :param auth_level: Determines what keys, if any, need to be present
        on the request in order to invoke the function.
        :return: Decorator function.
        :param trigger_extra_fields: Additional fields to include in trigger
        json. For example,
        >>> data_type='STRING' # 'dataType': 'STRING' in trigger json
        :param binding_extra_fields: Additional fields to include in binding
        json. For example,
        >>> data_type='STRING' # 'dataType': 'STRING' in binding json
        """

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

    def timer_trigger(self,
                      arg_name: str,
                      schedule: str,
                      run_on_startup: Optional[bool] = None,
                      use_monitor: Optional[bool] = None,
                      data_type: Optional[Union[DataType, str]] = None,
                      **kwargs: Any) -> Callable[..., Any]:
        """The schedule or timer decorator adds :class:`TimerTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining TimerTrigger
        in the function.json which enables your function be triggered on the
        specified schedule.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-timer

        :param arg_name: The name of the variable that represents the
        :class:`TimerRequest` object in function code.
        :param schedule: A string representing a CRON expression that will
        be used to schedule a function to run.
        :param run_on_startup: If true, the function is invoked when the
        runtime starts.
        :param use_monitor: Set to true or false to indicate whether the
        schedule should be monitored.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
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
        """The warm up decorator adds :class:`WarmUpTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining WarmUpTrigger
        in the function.json which enables your function be triggered on the
        specified schedule.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-warmup

        :param arg_name: The name of the variable that represents the
        :class:`TimerRequest` object in function code.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
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
        """The on_service_bus_queue_change decorator adds
        :class:`ServiceBusQueueTrigger` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusQueueTrigger
        in the function.json which enables your function be triggered when
        new message(s) are sent to the service bus queue.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the
        :class:`ServiceBusMessage` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param queue_name: Name of the queue to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param access_rights: Access rights for the connection string.
        :param is_sessions_enabled: True if connecting to a session-aware
        queue or subscription.
        :param cardinality: Set to many in order to enable batching.
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
        """The on_service_bus_topic_change decorator adds
        :class:`ServiceBusTopicTrigger` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusTopicTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the service bus topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the
        :class:`ServiceBusMessage` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param topic_name: Name of the topic to monitor.
        :param subscription_name: Name of the subscription to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param access_rights: Access rights for the connection string.
        :param is_sessions_enabled: True if connecting to a session-aware
        queue or subscription.
        :param cardinality: Set to many in order to enable batching.
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
        """The queue_trigger decorator adds :class:`QueueTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining QueueTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the storage queue.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-queue

        :param arg_name: The name of the variable that represents the
        :class:`QueueMessage` object in function code.
        :param queue_name: The name of the queue to poll.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Queues.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The event_hub_message_trigger decorator adds
        :class:`EventHubTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining EventHubTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the event hub.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents
        :class:`EventHubEvent` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Event Hubs.
        :param event_hub_name: The name of the event hub.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param cardinality: Set to many in order to enable batching.
        :param consumer_group: An optional property that sets the consumer
        group used to subscribe to events in the hub.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The cosmos_db_trigger_v3 decorator adds :class:`CosmosDBTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 2.x
        or 3.x. For additional details, please refer
        https://aka.ms/cosmosdb-v4-update.
        This is equivalent to defining CosmosDBTrigger in the function.json
         which enables function to be triggered when CosmosDB data is changed.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents
        :class:`DocumentList` object in function code.
        :param database_name: The name of the Azure Cosmos DB database with
        the collection being monitored.
        :param collection_name: The name of the collection being monitored.
        :param connection_string_setting: The name of an app setting or
        setting collection that specifies how to connect to the Azure Cosmos
        DB account being monitored.
        :param lease_collection_name: The name of the collection used to
        store leases.
        :param lease_connection_string_setting: The name of an app setting
        or setting collection that specifies how to connect to the Azure
        Cosmos DB account that holds the lease collection.
        :param lease_database_name: The name of the database that holds the
        collection used to store leases.
        :param create_lease_collection_if_not_exists: When set to true,
        the leases collection is automatically created when it doesn't
        already exist.
        :param leases_collection_throughput: Defines the number of Request
        Units to assign when the leases collection is created.
        :param lease_collection_prefix: When set, the value is added as a
        prefix to the leases created in the Lease collection for this
        Function.
        :param checkpoint_interval: When set, it defines, in milliseconds,
        the interval between lease checkpoints. Default is always after a
        Function call.
        :param checkpoint_document_count: Customizes the amount of documents
        between lease checkpoints. Default is always after a Function call.
        :param feed_poll_delay: The time (in milliseconds) for the delay
        between polling a partition for new changes on the feed, after all
        current changes are drained.
        :param lease_renew_interval: When set, it defines, in milliseconds,
        the renew interval for all leases for partitions currently held by
        an instance.
        :param lease_acquire_interval: When set, it defines,
        in milliseconds, the interval to kick off a task to compute if
        partitions are distributed evenly among known host instances.
        :param lease_expiration_interval: When set, it defines,
        in milliseconds, the interval for which the lease is taken on a
        lease representing a partition.
        :param max_items_per_invocation: When set, this property sets the
        maximum number of items received per Function call.
        :param start_from_beginning: This option tells the Trigger to read
        changes from the beginning of the collection's change history
        instead of starting at the current time.
        :param preferred_locations: Defines preferred locations (regions)
        for geo-replicated database accounts in the Azure Cosmos DB service.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The cosmos_db_trigger decorator adds :class:`CosmosDBTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above. For additional details, please refer
        https://aka.ms/cosmosdb-v4-update.
        This is equivalent to defining CosmosDBTrigger in the function.json
        which enables function to be triggered when CosmosDB data is changed.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v4

        :param arg_name: The name of the variable that represents
        :class:`DocumentList` object in function code
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to the Azure Cosmos DB account being
         monitored.
        :param database_name: The name of the Azure Cosmos DB database with
        the collection being monitored
        :param container_name: The name of the container being monitored
        :param lease_connection: (Optional) The name of an app setting or
         setting container that specifies how to connect to the Azure Cosmos
         DB account that holds the lease container
        :param lease_database_name: The name of the database that holds the
        collection used to store leases
        :param lease_container_name: (Optional) The name of the container used
            to store leases. When not set, the value leases is used
        :param create_lease_container_if_not_exists: (Optional) When set to
        true, the leases container is automatically created when it doesn't
         already exist. The default value is false. When using Azure AD
         identities if you set the value to true, creating containers is not an
          allowed operation and your Function won't be able to start
        :param leases_container_throughput: (Optional) Defines the number of
        Request Units to assign when the leases container is created. This
        setting is only used when createLeaseContainerIfNotExists is set to
        true. This parameter is automatically set when the binding is created
        using the portal
        :param lease_container_prefix: (Optional) When set, the value is added
        as a prefix to the leases created in the Lease container for this
        function. Using a prefix allows two separate Azure Functions to share
        the same Lease container by using different prefixes
        :param feed_poll_delay: The time (in milliseconds) for the delay
        between polling a partition for new changes on the feed, after all
        current changes are drained
        :param lease_acquire_interval: When set, it defines,
        in milliseconds, the interval to kick off a task to compute if
        partitions are distributed evenly among known host instances
        :param lease_expiration_interval: When set, it defines,
        in milliseconds, the interval for which the lease is taken on a
        lease representing a partition
        :param lease_renew_interval: When set, it defines, in milliseconds,
        the renew interval for all leases for partitions currently held by
        an instance
        :param max_items_per_invocation: When set, this property sets the
        maximum number of items received per Function call
        :param start_from_beginning: This option tells the Trigger to read
        changes from the beginning of the collection's change history
        instead of starting at the current time
        :param start_from_time: (Optional) Gets or sets the date and time from
        which to initialize the change feed read operation. The recommended
        format is ISO 8601 with the UTC designator, such as
        2021-02-16T14:19:29Z. This is only used to set the initial trigger
        state. After the trigger has a lease state, changing this value has
        no effect
        :param preferred_locations: Defines preferred locations (regions)
        for geo-replicated database accounts in the Azure Cosmos DB service
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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
                     data_type: Optional[DataType] = None,
                     **kwargs) -> Callable[..., Any]:
        """
        The blob_change_trigger decorator adds :class:`BlobTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining BlobTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the storage blobs.
        All optional fields will be given default value by function host when
        they are parsed by function host.
        Ref: https://aka.ms/azure-function-binding-storage-blob
        :param arg_name: The name of the variable that represents the
        :class:`InputStream` object in function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Blobs.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        The event_grid_trigger decorator adds
        :class:`EventGridTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining event grid trigger
        in the function.json which enables function to be triggered to
        respond to an event sent to an event grid topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/eventgridtrigger

        :param arg_name: the variable name used in function code for the
            parameter that receives the event data.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
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

    def sql_trigger(self,
                    arg_name: str,
                    table_name: str,
                    connection_string_setting: str,
                    leases_table_name: Optional[str] = None,
                    data_type: Optional[DataType] = None,
                    **kwargs) -> Callable[..., Any]:
        """The sql_trigger decorator adds :class:`SqlTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above.
        This is equivalent to defining SqlTrigger in the function.json which
        enables function to be triggered when there are changes in the Sql
        table.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents a
        :class:`SqlRowList` object in the function code
        :param table_name: The name of the table monitored by the trigger
        :param connection_string_setting: The name of an app setting that
        contains the connection string for the database against which the
        query or stored procedure is being executed
        :param leases_table_name: The name of the table used to store
        leases. If not specified, the leases table name will be
        Leases_{FunctionId}_{TableId}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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

    def generic_trigger(self,
                        arg_name: str,
                        type: str,
                        data_type: Optional[Union[DataType, str]] = None,
                        **kwargs
                        ) -> Callable[..., Any]:
        """
        The generic_trigger decorator adds :class:`GenericTrigger`
        to the :class:`FunctionBuilder` object for building :class:`Function`
        object used in worker function indexing model.
        This is equivalent to defining a generic trigger in the
        function.json which triggers function to execute when generic trigger
        events are received by host.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of trigger parameter in the function code.
        :param type: The type of binding.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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

    def dapr_service_invocation_trigger(self,
                                        arg_name: str,
                                        method_name: str,
                                        data_type: Optional[
                                            Union[DataType, str]] = None,
                                        **kwargs: Any) -> Callable[..., Any]:
        """The dapr_service_invocation_trigger decorator adds
        :class:`DaprServiceInvocationTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining
        DaprServiceInvocationTrigger
        in the function.json which enables function to be triggered when new
        service invocation occurs through Dapr.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-trigger-service-invocation

        :param arg_name: The name of the variable that represents
        :param method_name: The name of the method on a remote Dapr App.
        If not specified, the name of the function is used as the method name.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The dapr_binding_trigger decorator adds
        :class:`DaprBindingTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprBindingTrigger
        in the function.json which enables function to be triggered
        on Dapr input binding.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-trigger-binding

        :param arg_name: The name of the variable that represents
        :param binding_name: The name of the Dapr trigger.
        If not specified, the name of the function is used as the trigger name.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The dapr_topic_trigger decorator adds
        :class:`DaprTopicTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprTopicTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the Dapr pubsub.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-trigger-topic

        :param arg_name: The name of the variable that represents
        :param pub_sub_name: The pub/sub name.
        :param topic: The topic. If unspecified the function name will be used.
        :param route: The route for the trigger. If unspecified
        the topic name will be used.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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


class BindingApi(DecoratorApi, ABC):
    """Interface to extend for using existing binding decorator functions."""

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
        """The service_bus_queue_output decorator adds
        :class:`ServiceBusQueueOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusQueueOutput
        in the function.json which enables function to write message(s) to
        the service bus queue.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents service
        bus queue output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param queue_name: Name of the queue to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param access_rights: Access rights for the connection string.
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
        """The service_bus_topic_output decorator adds
        :class:`ServiceBusTopicOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusTopicOutput
        in the function.json which enables function to write message(s) to
        the service bus topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents service
        bus topic output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param topic_name: Name of the topic to monitor.
        :param subscription_name: Name of the subscription to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
        :param access_rights: Access rights for the connection string.
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
        """The queue_output decorator adds :class:`QueueOutput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining QueueOutput
        in the function.json which enables function to write message(s) to
        the storage queue.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-queue

        :param arg_name: The name of the variable that represents storage
        queue output object in function code.
        :param queue_name: The name of the queue to poll.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Queues.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The event_hub_output decorator adds
        :class:`EventHubOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining EventHubOutput
        in the function.json which enables function to write message(s) to
        the event hub.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents event hub
        output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Event Hub.
        :param event_hub_name: The name of the event hub.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The cosmos_db_output_v3 decorator adds
        :class:`CosmosDBOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 2.x
        or 3.x. For additional details, please refer
        https://aka.ms/cosmosdb-v4-update.
         This is equivalent to defining CosmosDBOutput
        in the function.json which enables function to write to the CosmosDB.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents CosmosDB
        output object in function code.
        :param database_name: The name of the Azure Cosmos DB database with
        the collection being monitored.
        :param collection_name: The name of the collection being monitored.
        :param connection_string_setting: The name of an app setting or
        setting collection that specifies how to connect to the Azure Cosmos
        DB account being monitored.
        :param create_if_not_exists: A boolean value to indicate whether the
        collection is created when it doesn't exist.
        :param partition_key: When CreateIfNotExists is true, it defines the
        partition key path for the created collection.
        :param collection_throughput: When CreateIfNotExists is true,
        it defines the throughput of the created collection.
        :param use_multiple_write_locations: When set to true along with
        PreferredLocations, it can leverage multi-region writes in the Azure
        Cosmos DB service.
        :param preferred_locations: Defines preferred locations (regions)
        for geo-replicated database accounts in the Azure Cosmos DB service.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The cosmos_db_output decorator adds
        :class:`CosmosDBOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above. For additional details, please refer
        https://aka.ms/cosmosdb-v4-update.
        This is equivalent to defining CosmosDBOutput
        in the function.json which enables function to write to the CosmosDB.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v4

        :param arg_name: The name of the variable that represents CosmosDB
        output object in function code.
        :param connection: The name of an app setting or
        setting collection that specifies how to connect to the Azure Cosmos
        DB account being monitored
        :param database_name: The name of the Azure Cosmos DB database with
        the collection being monitored
        :param container_name: The name of the container being monitored
        :param create_if_not_exists: A boolean value to indicate whether the
        collection is created when it doesn't exist
        :param partition_key: When CreateIfNotExists is true, it defines the
        partition key path for the created collection
        :param container_throughput: When createIfNotExists is true, it defines
        the throughput of the created container
        PreferredLocations, it can leverage multi-region writes in the Azure
        Cosmos DB service
        :param preferred_locations: Defines preferred locations (regions)
        for geo-replicated database accounts in the Azure Cosmos DB service
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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
        """The cosmos_db_input_v3 decorator adds
        :class:`CosmosDBInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 2.x
        or 3.x. For additional details, please refer
        https://aka.ms/cosmosdb-v4-update.
        This is equivalent to defining CosmosDBInput
        in the function.json which enables function to read from CosmosDB.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents
        :class:`DocumentList` input object in function code.
        :param database_name: The database containing the document.
        :param collection_name: The name of the collection that contains the
        document.
        :param connection_string_setting: The name of the app setting
        containing your Azure Cosmos DB connection string.
        :param id: The ID of the document to retrieve.
        :param sql_query: An Azure Cosmos DB SQL query used for retrieving
        multiple documents.
        :param partition_key: Specifies the partition key value for the
        lookup.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The cosmos_db_input decorator adds
        :class:`CosmosDBInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above. For additional details, please refer
        https://aka.ms/cosmosdb-v4-update.
        This is equivalent to defining CosmosDBInput in the function.json which
         enables function to read from CosmosDB.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v4

        :param arg_name: The name of the variable that represents
        :class:`DocumentList` input object in function code
        :param connection: The name of an app setting or setting container that
         specifies how to connect to the Azure Cosmos DB account being
         monitored containing your Azure Cosmos DB connection string
        :param database_name: The database containing the document
        :param container_name: The name of the container that contains the
        document
        :param partition_key: Specifies the partition key value for the
        lookup
        :param id: The ID of the document to retrieve
        :param sql_query: An Azure Cosmos DB SQL query used for retrieving
        multiple documents
        :param preferred_locations: (Optional) Defines preferred locations
        (regions) for geo-replicated database accounts in the Azure Cosmos DB
        service. Values should be comma-separated. For example, East US,South
        Central US,North Europe
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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
        The blob_input decorator adds :class:`BlobInput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining BlobInput
        in the function.json which enables function to write message(s) to
        the storage blobs.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-storage-blob

        :param arg_name: The name of the variable that represents the blob in
         function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Blobs.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        The blob_output decorator adds :class:`BlobOutput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining BlobOutput
        in the function.json which enables function to write message(s) to
        the storage blobs.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-storage-blob

        :param arg_name: The name of the variable that represents the blob in
         function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection
         that specifies how to connect to Azure Blobs.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.
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
                          topic_endpoint_uri: str,
                          topic_key_setting: str,
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) -> Callable[..., Any]:
        """
        The event_grid_output decorator adds
        :class:`EventGridOutput`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining output binding
        in the function.json which enables function to
        write events to a custom topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/eventgridtrigger

        :param arg_name: The variable name used in function code that
        represents the event.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param topic_endpoint_uri: 	The name of an app setting that
        contains the URI for the custom topic.
        :param topic_key_setting: The name of an app setting that
        contains an access key for the custom topic.
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
        The table_input decorator adds :class:`TableInput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining TableInput
        in the function.json which enables function to read a table in
        an Azure Storage or Cosmos DB account
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/tablesbindings

        :param arg_name: The name of the variable that represents
        the table or entity in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to the table service.
        :param table_name: The Name of the table
        :param row_key: The row key of the table entity to read.
        :param partition_key: The partition key of the table entity to read.
        :param take: The maximum number of entities to return
        :param filter: An OData filter expression for the entities to return
         from the table.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
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
        The table_output decorator adds :class:`TableOutput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining TableOutput
        in the function.json which enables function to write entities
        to a table in an Azure Storage
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/tablesbindings

        :param arg_name: The name of the variable that represents
        the table or entity in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to the table service.
        :param table_name: The Name of the table
        :param row_key: The row key of the table entity to read.
        :param partition_key: The partition key of the table entity to read.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
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
        """The sql_input decorator adds
        :class:`SqlInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above.
        This is equivalent to defining SqlInput in the function.json which
        enables the function to read from a Sql database.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents a
        :class:`SqlRowList` input object in function code
        :param command_text: The Transact-SQL query command or name of the
        stored procedure executed by the binding
        :param connection_string_setting: The name of an app setting that
        contains the connection string for the database against which the
        query or stored procedure is being executed
        :param command_type: A CommandType value, which is Text for a query
        and StoredProcedure for a stored procedure
        :param parameters: Zero or more parameter values passed to the
        command during execution as a single string. Must follow the format
        @param1=param1,@param2=param2
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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
        """The sql_output decorator adds
        :class:`SqlOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above.
        This is equivalent to defining SqlOutput in the function.json which
        enables the function to write to a Sql database.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents
        Sql output object in function code
        :param command_text: The Transact-SQL query command or name of the
        stored procedure executed by the binding
        :param connection_string_setting: The name of an app setting that
        contains the connection string for the database against which the
        query or stored procedure is being executed
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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
        The generic_input_binding decorator adds :class:`GenericInputBinding`
        to the :class:`FunctionBuilder` object for building :class:`Function`
        object used in worker function indexing model.
        This is equivalent to defining a generic input binding in the
        function.json which enables function to read data from a
        custom defined input source.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of input parameter in the function code.
        :param type: The type of binding.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        The generic_output_binding decorator adds :class:`GenericOutputBinding`
        to the :class:`FunctionBuilder` object for building :class:`Function`
        object used in worker function indexing model.
        This is equivalent to defining a generic output binding in the
        function.json which enables function to write data from a
        custom defined output source.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of output parameter in the function code.
        :param type: The type of binding.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The dapr_state_input decorator adds
        :class:`DaprStateInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprStateInput
        in the function.json which enables function to read state from
        underlying state store component.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-state-input-binding

        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param state_store: State store containing the state.
        :param key: The name of the key.
        :param dapr_address: Dapr address, it is optional field, by default
        it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The dapr_secret_input decorator adds
        :class:`DaprSecretInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprSecretInput
        in the function.json which enables function to read secret from
        underlying secret store component.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-secret-input-binding

        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param secret_store_name: The name of the secret store to
        get the secret from.
        :param key: The key identifying the name of the secret to get.
        :param metadata: An array of metadata properties in the form
        "key1=value1&amp;key2=value2".
        :param dapr_address: Dapr address, it is optional field, by default
        it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

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
        """The dapr_state_output decorator adds
        :class:`DaprStateOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model.
        This is equivalent to defining DaprStateOutput
        in the function.json which enables function to write to the dapr
        state store.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-state-output-binding

        :param arg_name: The name of the variable that represents DaprState
        output object in function code.
        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param state_store: State store containing the state for keys.
        :param key: The name of the key.
        :param dapr_address: Dapr address, it is optional field, by default
        it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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
        """The dapr_invoke_output decorator adds
        :class:`DaprInvokeOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model.
        This is equivalent to defining DaprInvokeOutput
        in the function.json which enables function to invoke another Dapr App.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-invoke-output-binding

        :param arg_name: The name of the variable that represents DaprState
        output object in function code.
        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param app_id: The dapr app name to invoke.
        :param method_name: The method name of the app to invoke.
        :param http_verb: The http verb of the app to invoke.
        :param dapr_address: Dapr address, it is optional field, by default
        it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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
        """The dapr_publish_output decorator adds
        :class:`DaprPublishOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model.
        This is equivalent to defining DaprPublishOutput
        in the function.json which enables function to publish topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-publish-output-binding

        :param arg_name: The name of the variable that represents DaprState
        output object in function code.
        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param pub_sub_name: The pub/sub name to publish to.
        :param topic:  The name of the topic to publish to.
        :param dapr_address: Dapr address, it is optional field, by default
        ßit will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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
        """The dapr_binding_output decorator adds
        :class:`DaprBindingOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model.
        This is equivalent to defining DaprBindingOutput
        in the function.json which enables function to send a value to
        a Dapr output binding.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-dapr-binding-output-binding

        :param arg_name: The name of the variable that represents DaprState
        output object in function code.
        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param binding_name: The configured name of the binding.
        :param operation:  The configured operation.
        :param dapr_address: Dapr address, it is optional field, by default
        it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

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


class SettingsApi(DecoratorApi, ABC):
    """Interface to extend for using existing settings decorator in
    functions."""

    def function_name(self, name: str,
                      setting_extra_fields: Dict[str, Any] = {},
                      ) -> Callable[..., Any]:
        """Optional: Sets name of the :class:`Function` object. If not set,
        it will default to the name of the method name.

        :param name: Name of the function.
        :param setting_extra_fields: Keyword arguments for specifying
        additional setting fields
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_setting(setting=FunctionName(
                    function_name=name,
                    **setting_extra_fields))
                return fb

            return decorator()

        return wrap

    def retry(self,
              strategy: str,
              max_retry_count: str,
              delay_interval: Optional[str] = None,
              minimum_interval: Optional[str] = None,
              maximum_interval: Optional[str] = None,
              setting_extra_fields: Dict[str, Any] = {},
              ) -> Callable[..., Any]:
        """The retry decorator adds :class:`RetryPolicy` to the function
        settings object for building :class:`Function` object used in worker
        function indexing model. This is equivalent to defining RetryPolicy
        in the function.json which enables function to retry on failure.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure_functions_retries

        :param strategy: The retry strategy to use.
        :param max_retry_count: The maximum number of retry attempts.
        :param delay_interval: The delay interval between retry attempts.
        :param minimum_interval: The minimum delay interval between retry
        attempts.
        :param maximum_interval: The maximum delay interval between retry
        attempts.
        :param setting_extra_fields: Keyword arguments for specifying
        additional setting fields.
        :return: Decorator function.
        """

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
        """Interface for declaring top level function app class which will
        be directly indexed by Python Function runtime.

        :param auth_level: Determines what keys, if any, need to be present
        on the request in order to invoke the function.
        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        """
        DecoratorApi.__init__(self, *args, **kwargs)
        HttpFunctionsAuthLevelMixin.__init__(self, auth_level, *args, **kwargs)
        self._require_auth_level: Optional[bool] = None

    def get_functions(self) -> List[Function]:
        """Get the function objects in the function app.

        :return: List of functions in the function app.
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

        return functions

    def register_functions(self, function_container: DecoratorApi) -> None:
        """Register a list of functions in the function app.

        :param function_container: Instance extending :class:`DecoratorApi`
        which contains a list of functions.
        """
        if isinstance(function_container, FunctionRegister):
            raise TypeError('functions can not be type of FunctionRegister!')
        self._function_builders.extend(function_container._function_builders)

    register_blueprint = register_functions


class FunctionApp(FunctionRegister, TriggerApi, BindingApi, SettingsApi):
    """FunctionApp object used by worker function indexing model captures
    user defined functions and metadata.

    Ref: https://aka.ms/azure-function-ref
    """

    def __init__(self,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        """Constructor of :class:`FunctionApp` object.

        :param http_auth_level: Determines what keys, if any, need to be
        present
        on the request in order to invoke the function.
        """
        super().__init__(auth_level=http_auth_level)


class Blueprint(TriggerApi, BindingApi, SettingsApi):
    """Functions container class where all the functions
    loaded in it can be registered in :class:`FunctionRegister` subclasses
    but itself can not be indexed directly. The class contains all existing
    supported trigger and binding decorator functions.
    """
    pass


class ExternalHttpFunctionApp(FunctionRegister, TriggerApi, ABC):
    """Interface to extend for building third party http function apps."""

    @abc.abstractmethod
    def _add_http_app(self,
                      http_middleware: Union[
                          AsgiMiddleware, WsgiMiddleware]) -> None:
        """Add a Wsgi or Asgi app integrated http function.

        :param http_middleware: :class:`WsgiMiddleware`
                                or class:`AsgiMiddleware` instance.

        :return: None
        """
        raise NotImplementedError()


class AsgiFunctionApp(ExternalHttpFunctionApp):
    def __init__(self, app,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        """Constructor of :class:`AsgiFunctionApp` object.

        :param app: asgi app object.
        :param http_auth_level: Determines what keys, if any, need to be
        present
        on the request in order to invoke the function.
        """
        super().__init__(auth_level=http_auth_level)
        self.middleware = AsgiMiddleware(app)
        self._add_http_app(self.middleware)
        self.startup_task_done = False

    def __del__(self):
        if self.startup_task_done:
            asyncio.run(self.middleware.notify_shutdown())

    def _add_http_app(self,
                      http_middleware: Union[
                          AsgiMiddleware, WsgiMiddleware]) -> None:
        """Add an Asgi app integrated http function.

        :param http_middleware: :class:`WsgiMiddleware`
                                or class:`AsgiMiddleware` instance.

        :return: None
        """
        if not isinstance(http_middleware, AsgiMiddleware):
            raise TypeError("Please pass AsgiMiddleware instance"
                            " as parameter.")

        asgi_middleware: AsgiMiddleware = http_middleware

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
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        """Constructor of :class:`WsgiFunctionApp` object.

        :param app: wsgi app object.
        """
        super().__init__(auth_level=http_auth_level)
        self._add_http_app(WsgiMiddleware(app))

    def _add_http_app(self,
                      http_middleware: Union[
                          AsgiMiddleware, WsgiMiddleware]) -> None:
        """Add a Wsgi app integrated http function.

        :param http_middleware: :class:`WsgiMiddleware`
                                or class:`AsgiMiddleware` instance.

        :return: None
        """
        if not isinstance(http_middleware, WsgiMiddleware):
            raise TypeError("Please pass WsgiMiddleware instance"
                            " as parameter.")

        wsgi_middleware: WsgiMiddleware = http_middleware

        @self.http_type(http_type='wsgi')
        @self.route(methods=(method for method in HttpMethod),
                    auth_level=self.auth_level,
                    route="/{*route}")
        def http_app_func(req: HttpRequest, context: Context):
            return wsgi_middleware.handle(req, context)
