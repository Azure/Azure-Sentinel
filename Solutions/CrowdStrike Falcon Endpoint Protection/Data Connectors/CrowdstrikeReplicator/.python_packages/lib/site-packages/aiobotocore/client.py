from botocore.awsrequest import prepare_request_dict
from botocore.client import logger, PaginatorDocstring, ClientCreator, \
    BaseClient, ClientEndpointBridge, S3ArnParamHandler, S3EndpointSetter, \
    resolve_checksum_context, apply_request_checksum
from botocore.discovery import block_endpoint_discovery_required_operations
from botocore.exceptions import OperationNotPageableError
from botocore.history import get_global_history_recorder
from botocore.utils import get_service_module_name
from botocore.waiter import xform_name
from botocore.hooks import first_non_none_response

from .paginate import AioPaginator
from .args import AioClientArgsCreator
from .utils import AioS3RegionRedirector
from .discovery import AioEndpointDiscoveryManager, AioEndpointDiscoveryHandler
from .retries import adaptive
from . import waiter

history_recorder = get_global_history_recorder()


class AioClientCreator(ClientCreator):
    async def create_client(self, service_name, region_name, is_secure=True,
                            endpoint_url=None, verify=None,
                            credentials=None, scoped_config=None,
                            api_version=None,
                            client_config=None):
        responses = await self._event_emitter.emit(
            'choose-service-name', service_name=service_name)
        service_name = first_non_none_response(responses, default=service_name)
        service_model = self._load_service_model(service_name, api_version)
        cls = await self._create_client_class(service_name, service_model)
        region_name, client_config = self._normalize_fips_region(
            region_name, client_config)
        endpoint_bridge = ClientEndpointBridge(
            self._endpoint_resolver, scoped_config, client_config,
            service_signing_name=service_model.metadata.get('signingName'),
            config_store=self._config_store)
        client_args = self._get_client_args(
            service_model, region_name, is_secure, endpoint_url,
            verify, credentials, scoped_config, client_config, endpoint_bridge)
        service_client = cls(**client_args)
        self._register_retries(service_client)
        self._register_s3_events(
            service_client, endpoint_bridge, endpoint_url, client_config,
            scoped_config)
        self._register_s3_control_events(
            service_client, endpoint_bridge, endpoint_url, client_config,
            scoped_config)
        self._register_endpoint_discovery(
            service_client, endpoint_url, client_config
        )
        return service_client

    async def _create_client_class(self, service_name, service_model):
        class_attributes = self._create_methods(service_model)
        py_name_to_operation_name = self._create_name_mapping(service_model)
        class_attributes['_PY_TO_OP_NAME'] = py_name_to_operation_name
        bases = [AioBaseClient]
        service_id = service_model.service_id.hyphenize()
        await self._event_emitter.emit(
            'creating-client-class.%s' % service_id,
            class_attributes=class_attributes,
            base_classes=bases)
        class_name = get_service_module_name(service_model)
        cls = type(str(class_name), tuple(bases), class_attributes)
        return cls

    def _register_endpoint_discovery(self, client, endpoint_url, config):
        if endpoint_url is not None:
            # Don't register any handlers in the case of a custom endpoint url
            return
        # Only attach handlers if the service supports discovery
        if client.meta.service_model.endpoint_discovery_operation is None:
            return
        events = client.meta.events
        service_id = client.meta.service_model.service_id.hyphenize()
        enabled = False
        if config and config.endpoint_discovery_enabled is not None:
            enabled = config.endpoint_discovery_enabled
        elif self._config_store:
            enabled = self._config_store.get_config_variable(
                'endpoint_discovery_enabled')

        enabled = self._normalize_endpoint_discovery_config(enabled)
        if enabled and self._requires_endpoint_discovery(client, enabled):
            discover = enabled is True
            manager = AioEndpointDiscoveryManager(client, always_discover=discover)
            handler = AioEndpointDiscoveryHandler(manager)
            handler.register(events, service_id)
        else:
            events.register('before-parameter-build',
                            block_endpoint_discovery_required_operations)

    def _register_retries(self, client):
        # botocore retry handlers may block. We add our own implementation here.
        # botocore provides three implementations:
        #
        # 1) standard
        # This one doesn't block. A threading.Lock is used in quota.RetryQuota,
        # but it's only used to protect concurrent modifications of internal
        # state inside multithreaded programs. When running under a single
        # asyncio thread, this lock will be acquired and released in the same
        # coroutine, and the coroutine will never block waiting for the lock.
        # Thus, we don't need to redefine this strategy.
        #
        # 2) adaptive
        # This one blocks when the client is applying self rate limiting.
        # We override the corresponding definition to replace it with async
        # objects.
        #
        # 3) legacy
        # This one probably doesn't block.
        #
        # The code for this method comes directly from botocore. We could
        # override `_register_v2_adaptive_retries` only. The override for
        # `_register_retries` is only included for clarity.
        retry_mode = client.meta.config.retries['mode']
        if retry_mode == 'standard':
            self._register_v2_standard_retries(client)
        elif retry_mode == 'adaptive':
            self._register_v2_standard_retries(client)
            self._register_v2_adaptive_retries(client)
        elif retry_mode == 'legacy':
            self._register_legacy_retries(client)

    def _register_v2_adaptive_retries(self, client):
        # See comment in `_register_retries`.
        # Note that this `adaptive` module is an aiobotocore reimplementation.
        adaptive.register_retry_handler(client)

    def _register_s3_events(self, client, endpoint_bridge, endpoint_url,
                            client_config, scoped_config):
        if client.meta.service_model.service_name != 's3':
            return
        AioS3RegionRedirector(endpoint_bridge, client).register()
        S3ArnParamHandler().register(client.meta.events)
        use_fips_endpoint = client.meta.config.use_fips_endpoint
        S3EndpointSetter(
            endpoint_resolver=self._endpoint_resolver,
            region=client.meta.region_name,
            s3_config=client.meta.config.s3,
            endpoint_url=endpoint_url,
            partition=client.meta.partition,
            use_fips_endpoint=use_fips_endpoint
        ).register(client.meta.events)
        self._set_s3_presign_signature_version(
            client.meta, client_config, scoped_config)

    def _get_client_args(self, service_model, region_name, is_secure,
                         endpoint_url, verify, credentials,
                         scoped_config, client_config, endpoint_bridge):
        # This is a near copy of ClientCreator. What's replaced
        # is ClientArgsCreator->AioClientArgsCreator
        args_creator = AioClientArgsCreator(
            self._event_emitter, self._user_agent,
            self._response_parser_factory, self._loader,
            self._exceptions_factory, config_store=self._config_store)
        return args_creator.get_client_args(
            service_model, region_name, is_secure, endpoint_url,
            verify, credentials, scoped_config, client_config, endpoint_bridge)


class AioBaseClient(BaseClient):
    async def _async_getattr(self, item):
        event_name = 'getattr.%s.%s' % (
            self._service_model.service_id.hyphenize(), item
        )
        handler, event_response = await self.meta.events.emit_until_response(
            event_name, client=self)

        return event_response

    def __getattr__(self, item):
        # NOTE: we can not reliably support this because if we were to make this a
        # deferred attrgetter (See #803), it would resolve in hasattr always returning
        # true.  This ends up breaking ddtrace for example when it tries to set a pin.
        raise AttributeError(
            "'%s' object has no attribute '%s'" % (self.__class__.__name__, item))

    async def _make_api_call(self, operation_name, api_params):
        operation_model = self._service_model.operation_model(operation_name)
        service_name = self._service_model.service_name
        history_recorder.record('API_CALL', {
            'service': service_name,
            'operation': operation_name,
            'params': api_params,
        })
        if operation_model.deprecated:
            logger.debug('Warning: %s.%s() is deprecated',
                         service_name, operation_name)
        request_context = {
            'client_region': self.meta.region_name,
            'client_config': self.meta.config,
            'has_streaming_input': operation_model.has_streaming_input,
            'auth_type': operation_model.auth_type,
        }
        request_dict = await self._convert_to_request_dict(
            api_params, operation_model, context=request_context)
        resolve_checksum_context(request_dict, operation_model, api_params)

        service_id = self._service_model.service_id.hyphenize()
        handler, event_response = await self.meta.events.emit_until_response(
            'before-call.{service_id}.{operation_name}'.format(
                service_id=service_id,
                operation_name=operation_name),
            model=operation_model, params=request_dict,
            request_signer=self._request_signer, context=request_context)

        if event_response is not None:
            http, parsed_response = event_response
        else:
            apply_request_checksum(request_dict)
            http, parsed_response = await self._make_request(
                operation_model, request_dict, request_context)

        await self.meta.events.emit(
            'after-call.{service_id}.{operation_name}'.format(
                service_id=service_id,
                operation_name=operation_name),
            http_response=http, parsed=parsed_response,
            model=operation_model, context=request_context
        )

        if http.status_code >= 300:
            error_code = parsed_response.get("Error", {}).get("Code")
            error_class = self.exceptions.from_code(error_code)
            raise error_class(parsed_response, operation_name)
        else:
            return parsed_response

    async def _make_request(self, operation_model, request_dict, request_context):
        try:
            return await self._endpoint.make_request(operation_model, request_dict)
        except Exception as e:
            await self.meta.events.emit(
                'after-call-error.{service_id}.{operation_name}'.format(
                    service_id=self._service_model.service_id.hyphenize(),
                    operation_name=operation_model.name),
                exception=e, context=request_context
            )
            raise

    async def _convert_to_request_dict(self, api_params, operation_model,
                                       context=None):
        api_params = await self._emit_api_params(
            api_params, operation_model, context)
        request_dict = self._serializer.serialize_to_request(
            api_params, operation_model)
        if not self._client_config.inject_host_prefix:
            request_dict.pop('host_prefix', None)
        prepare_request_dict(request_dict, endpoint_url=self._endpoint.host,
                             user_agent=self._client_config.user_agent,
                             context=context)
        return request_dict

    async def _emit_api_params(self, api_params, operation_model, context):
        # Given the API params provided by the user and the operation_model
        # we can serialize the request to a request_dict.
        operation_name = operation_model.name

        # Emit an event that allows users to modify the parameters at the
        # beginning of the method. It allows handlers to modify existing
        # parameters or return a new set of parameters to use.
        service_id = self._service_model.service_id.hyphenize()
        responses = await self.meta.events.emit(
            'provide-client-params.{service_id}.{operation_name}'.format(
                service_id=service_id,
                operation_name=operation_name),
            params=api_params, model=operation_model, context=context)
        api_params = first_non_none_response(responses, default=api_params)

        event_name = (
            'before-parameter-build.{service_id}.{operation_name}')
        await self.meta.events.emit(
            event_name.format(
                service_id=service_id,
                operation_name=operation_name),
            params=api_params, model=operation_model, context=context)
        return api_params

    def get_paginator(self, operation_name):
        """Create a paginator for an operation.

        :type operation_name: string
        :param operation_name: The operation name.  This is the same name
            as the method name on the client.  For example, if the
            method name is ``create_foo``, and you'd normally invoke the
            operation as ``client.create_foo(**kwargs)``, if the
            ``create_foo`` operation can be paginated, you can use the
            call ``client.get_paginator("create_foo")``.

        :raise OperationNotPageableError: Raised if the operation is not
            pageable.  You can use the ``client.can_paginate`` method to
            check if an operation is pageable.

        :rtype: L{botocore.paginate.Paginator}
        :return: A paginator object.

        """
        if not self.can_paginate(operation_name):
            raise OperationNotPageableError(operation_name=operation_name)
        else:
            actual_operation_name = self._PY_TO_OP_NAME[operation_name]

            # Create a new paginate method that will serve as a proxy to
            # the underlying Paginator.paginate method. This is needed to
            # attach a docstring to the method.
            def paginate(self, **kwargs):
                return AioPaginator.paginate(self, **kwargs)

            paginator_config = self._cache['page_config'][
                actual_operation_name]
            # Add the docstring for the paginate method.
            paginate.__doc__ = PaginatorDocstring(
                paginator_name=actual_operation_name,
                event_emitter=self.meta.events,
                service_model=self.meta.service_model,
                paginator_config=paginator_config,
                include_signature=False
            )

            # Rename the paginator class based on the type of paginator.
            paginator_class_name = str('%s.Paginator.%s' % (
                get_service_module_name(self.meta.service_model),
                actual_operation_name))

            # Create the new paginator class
            documented_paginator_cls = type(
                paginator_class_name, (AioPaginator,), {'paginate': paginate})

            operation_model = self._service_model.operation_model(actual_operation_name)
            paginator = documented_paginator_cls(
                getattr(self, operation_name),
                paginator_config,
                operation_model)
            return paginator

    # NOTE: this method does not differ from botocore, however it's important to keep
    #   as the "waiter" value points to our own asyncio waiter module
    def get_waiter(self, waiter_name):
        """Returns an object that can wait for some condition.

        :type waiter_name: str
        :param waiter_name: The name of the waiter to get. See the waiters
            section of the service docs for a list of available waiters.

        :returns: The specified waiter object.
        :rtype: botocore.waiter.Waiter
        """
        config = self._get_waiter_config()
        if not config:
            raise ValueError("Waiter does not exist: %s" % waiter_name)
        model = waiter.WaiterModel(config)
        mapping = {}
        for name in model.waiter_names:
            mapping[xform_name(name)] = name
        if waiter_name not in mapping:
            raise ValueError("Waiter does not exist: %s" % waiter_name)

        return waiter.create_waiter_with_client(
            mapping[waiter_name], model, self)

    async def __aenter__(self):
        await self._endpoint.http_session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._endpoint.http_session.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        """Close all http connections."""
        return await self._endpoint.http_session.close()
