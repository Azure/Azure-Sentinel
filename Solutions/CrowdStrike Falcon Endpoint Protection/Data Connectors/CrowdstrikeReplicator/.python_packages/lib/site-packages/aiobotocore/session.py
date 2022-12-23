from botocore.session import Session, EVENT_ALIASES, ServiceModel, \
    UnknownServiceError, copy

from botocore import UNSIGNED
from botocore import retryhandler, translate
from botocore.exceptions import PartialCredentialsError
from .client import AioClientCreator, AioBaseClient
from .hooks import AioHierarchicalEmitter
from .parsers import AioResponseParserFactory
from .signers import add_generate_presigned_url, add_generate_presigned_post, \
    add_generate_db_auth_token
from .handlers import inject_presigned_url_ec2, inject_presigned_url_rds
from botocore.handlers import \
    inject_presigned_url_rds as boto_inject_presigned_url_rds, \
    inject_presigned_url_ec2 as boto_inject_presigned_url_ec2
from botocore.signers import \
    add_generate_presigned_url as boto_add_generate_presigned_url, \
    add_generate_presigned_post as boto_add_generate_presigned_post, \
    add_generate_db_auth_token as boto_add_generate_db_auth_token
from .configprovider import AioSmartDefaultsConfigStoreFactory
from .credentials import create_credential_resolver, AioCredentials
from .utils import AioIMDSRegionProvider


_HANDLER_MAPPING = {
    boto_inject_presigned_url_ec2: inject_presigned_url_ec2,
    boto_inject_presigned_url_rds: inject_presigned_url_rds,
    boto_add_generate_presigned_url: add_generate_presigned_url,
    boto_add_generate_presigned_post: add_generate_presigned_post,
    boto_add_generate_db_auth_token: add_generate_db_auth_token,
}


class ClientCreatorContext:
    def __init__(self, coro):
        self._coro = coro
        self._client = None

    async def __aenter__(self) -> AioBaseClient:
        self._client = await self._coro
        return await self._client.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.__aexit__(exc_type, exc_val, exc_tb)


class AioSession(Session):

    # noinspection PyMissingConstructor
    def __init__(self, session_vars=None, event_hooks=None,
                 include_builtin_handlers=True, profile=None):
        if event_hooks is None:
            event_hooks = AioHierarchicalEmitter()

        super().__init__(session_vars, event_hooks, include_builtin_handlers, profile)

    def register(self, event_name, handler, unique_id=None,
                 unique_id_uses_count=False):
        handler = _HANDLER_MAPPING.get(handler, handler)

        return super().register(event_name, handler, unique_id, unique_id_uses_count)

    def _register_response_parser_factory(self):
        self._components.register_component('response_parser_factory',
                                            AioResponseParserFactory())

    def _register_smart_defaults_factory(self):
        def create_smart_defaults_factory():
            default_config_resolver = self._get_internal_component(
                'default_config_resolver')
            imds_region_provider = AioIMDSRegionProvider(session=self)
            return AioSmartDefaultsConfigStoreFactory(
                default_config_resolver, imds_region_provider)
        self._internal_components.lazy_register_component(
            'smart_defaults_factory', create_smart_defaults_factory)

    def create_client(self, *args, **kwargs):
        return ClientCreatorContext(self._create_client(*args, **kwargs))

    async def _create_client(self, service_name, region_name=None,
                             api_version=None,
                             use_ssl=True, verify=None, endpoint_url=None,
                             aws_access_key_id=None, aws_secret_access_key=None,
                             aws_session_token=None, config=None):

        default_client_config = self.get_default_client_config()
        # If a config is provided and a default config is set, then
        # use the config resulting from merging the two.
        if config is not None and default_client_config is not None:
            config = default_client_config.merge(config)
        # If a config was not provided then use the default
        # client config from the session
        elif default_client_config is not None:
            config = default_client_config

        region_name = self._resolve_region_name(region_name, config)

        # Figure out the verify value base on the various
        # configuration options.
        if verify is None:
            verify = self.get_config_variable('ca_bundle')

        if api_version is None:
            api_version = self.get_config_variable('api_versions').get(
                service_name, None)

        loader = self.get_component('data_loader')
        event_emitter = self.get_component('event_emitter')
        response_parser_factory = self.get_component(
            'response_parser_factory')
        if config is not None and config.signature_version is UNSIGNED:
            credentials = None
        elif aws_access_key_id is not None and \
                aws_secret_access_key is not None:
            credentials = AioCredentials(
                access_key=aws_access_key_id,
                secret_key=aws_secret_access_key,
                token=aws_session_token)
        elif self._missing_cred_vars(aws_access_key_id,
                                     aws_secret_access_key):
            raise PartialCredentialsError(
                provider='explicit',
                cred_var=self._missing_cred_vars(aws_access_key_id,
                                                 aws_secret_access_key))
        else:
            credentials = await self.get_credentials()
        endpoint_resolver = self._get_internal_component('endpoint_resolver')
        exceptions_factory = self._get_internal_component('exceptions_factory')
        config_store = self.get_component('config_store')
        defaults_mode = self._resolve_defaults_mode(config, config_store)
        if defaults_mode != 'legacy':
            smart_defaults_factory = self._get_internal_component(
                'smart_defaults_factory')
            config_store = copy.deepcopy(config_store)
            await smart_defaults_factory.merge_smart_defaults(
                config_store, defaults_mode, region_name)
        client_creator = AioClientCreator(
            loader, endpoint_resolver, self.user_agent(), event_emitter,
            retryhandler, translate, response_parser_factory,
            exceptions_factory, config_store)
        client = await client_creator.create_client(
            service_name=service_name, region_name=region_name,
            is_secure=use_ssl, endpoint_url=endpoint_url, verify=verify,
            credentials=credentials, scoped_config=self.get_scoped_config(),
            client_config=config, api_version=api_version)
        monitor = self._get_internal_component('monitor')
        if monitor is not None:
            monitor.register(client.meta.events)
        return client

    def _create_credential_resolver(self):
        return create_credential_resolver(
            self, region_name=self._last_client_region_used)

    async def get_credentials(self):
        if self._credentials is None:
            self._credentials = await (self._components.get_component(
                'credential_provider').load_credentials())
        return self._credentials

    def set_credentials(self, access_key, secret_key, token=None):
        self._credentials = AioCredentials(access_key, secret_key, token)

    async def get_service_model(self, service_name, api_version=None):
        service_description = await self.get_service_data(service_name, api_version)
        return ServiceModel(service_description, service_name=service_name)

    async def get_service_data(self, service_name, api_version=None):
        """
        Retrieve the fully merged data associated with a service.
        """
        data_path = service_name
        service_data = self.get_component('data_loader').load_service_model(
            data_path,
            type_name='service-2',
            api_version=api_version
        )
        service_id = EVENT_ALIASES.get(service_name, service_name)
        await self._events.emit('service-data-loaded.%s' % service_id,
                                service_data=service_data,
                                service_name=service_name, session=self)
        return service_data

    async def get_available_regions(self, service_name, partition_name='aws',
                                    allow_non_regional=False):
        resolver = self._get_internal_component('endpoint_resolver')
        results = []
        try:
            service_data = await self.get_service_data(service_name)
            endpoint_prefix = service_data['metadata'].get(
                'endpointPrefix', service_name)
            results = resolver.get_available_endpoints(
                endpoint_prefix, partition_name, allow_non_regional)
        except UnknownServiceError:
            pass
        return results


def get_session(env_vars=None):
    """
    Return a new session object.
    """
    return AioSession(env_vars)
