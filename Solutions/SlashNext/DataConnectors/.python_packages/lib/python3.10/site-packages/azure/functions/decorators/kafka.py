#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import KAFKA, KAFKA_TRIGGER
from azure.functions.decorators.core import Cardinality, DataType, \
    OutputBinding, Trigger
from .utils import StringifyEnum


class BrokerAuthenticationMode(StringifyEnum):
    NOTSET = -1
    GSSAPI = 0
    PLAIN = 1
    SCRAMSHA256 = 2
    SCRAMSHA512 = 3


class BrokerProtocol(StringifyEnum):
    NOTSET = -1
    PLAINTEXT = 0
    SSL = 1
    SASLPLAINTEXT = 2
    SASLSSL = 3


class OAuthBearerMethod(StringifyEnum):
    DEFAULT = 0,
    OIDC = 1


class KafkaOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return KAFKA

    def __init__(self,
                 name: str,
                 topic: str,
                 broker_list: str,
                 avro_schema: Optional[str],
                 username: Optional[str],
                 password: Optional[str],
                 ssl_key_location: Optional[str],
                 ssl_ca_location: Optional[str],
                 ssl_certificate_location: Optional[str],
                 ssl_key_password: Optional[str],
                 schema_registry_url: Optional[str],
                 schema_registry_username: Optional[str],
                 schema_registry_password: Optional[str],
                 o_auth_bearer_method: Optional[OAuthBearerMethod] = None,
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
                 authentication_mode: Optional[BrokerAuthenticationMode] = BrokerAuthenticationMode.NOTSET,  # noqa: E501
                 protocol: Optional[BrokerProtocol] = BrokerProtocol.NOTSET,
                 linger_ms: int = 5,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.topic = topic
        self.broker_list = broker_list
        self.avro_schema = avro_schema
        self.username = username
        self.password = password
        self.ssl_key_location = ssl_key_location
        self.ssl_ca_location = ssl_ca_location
        self.ssl_certificate_location = ssl_certificate_location
        self.ssl_key_password = ssl_key_password
        self.schema_registry_url = schema_registry_url
        self.schema_registry_username = schema_registry_username
        self.schema_registry_password = schema_registry_password
        self.o_auth_bearer_method = o_auth_bearer_method
        self.o_auth_bearer_client_id = o_auth_bearer_client_id
        self.o_auth_bearer_client_secret = o_auth_bearer_client_secret
        self.o_auth_bearer_scope = o_auth_bearer_scope
        self.o_auth_bearer_token_endpoint_url = o_auth_bearer_token_endpoint_url  # noqa: E501
        self.o_auth_bearer_extensions = o_auth_bearer_extensions
        self.max_message_bytes = max_message_bytes
        self.batch_size = batch_size
        self.enable_idempotence = enable_idempotence
        self.message_timeout_ms = message_timeout_ms
        self.request_timeout_ms = request_timeout_ms
        self.max_retries = max_retries
        self.authentication_mode = authentication_mode
        self.protocol = protocol
        self.linger_ms = linger_ms
        super().__init__(name=name, data_type=data_type)


class KafkaTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return KAFKA_TRIGGER

    def __init__(self,
                 name: str,
                 topic: str,
                 broker_list: str,
                 event_hub_connection_string: Optional[str],
                 consumer_group: Optional[str],
                 avro_schema: Optional[str],
                 username: Optional[str],
                 password: Optional[str],
                 ssl_key_location: Optional[str],
                 ssl_ca_location: Optional[str],
                 ssl_certificate_location: Optional[str],
                 ssl_key_password: Optional[str],
                 schema_registry_url: Optional[str],
                 schema_registry_username: Optional[str],
                 schema_registry_password: Optional[str],
                 o_auth_bearer_method: Optional[OAuthBearerMethod] = None,
                 o_auth_bearer_client_id: Optional[str] = None,
                 o_auth_bearer_client_secret: Optional[str] = None,
                 o_auth_bearer_scope: Optional[str] = None,
                 o_auth_bearer_token_endpoint_url: Optional[str] = None,
                 o_auth_bearer_extensions: Optional[str] = None,
                 authentication_mode: Optional[BrokerAuthenticationMode] = BrokerAuthenticationMode.NOTSET,  # noqa: E501
                 protocol: Optional[BrokerProtocol] = BrokerProtocol.NOTSET,
                 cardinality: Optional[Cardinality] = Cardinality.ONE,
                 lag_threshold: int = 1000,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.topic = topic
        self.broker_list = broker_list
        self.event_hub_connection_string = event_hub_connection_string
        self.consumer_group = consumer_group
        self.avro_schema = avro_schema
        self.username = username
        self.password = password
        self.ssl_key_location = ssl_key_location
        self.ssl_ca_location = ssl_ca_location
        self.ssl_certificate_location = ssl_certificate_location
        self.ssl_key_password = ssl_key_password
        self.schema_registry_url = schema_registry_url
        self.schema_registry_username = schema_registry_username
        self.schema_registry_password = schema_registry_password
        self.o_auth_bearer_method = o_auth_bearer_method
        self.o_auth_bearer_client_id = o_auth_bearer_client_id
        self.o_auth_bearer_client_secret = o_auth_bearer_client_secret
        self.o_auth_bearer_scope = o_auth_bearer_scope
        self.o_auth_bearer_token_endpoint_url = o_auth_bearer_token_endpoint_url  # noqa: E501
        self.o_auth_bearer_extensions = o_auth_bearer_extensions
        self.authentication_mode = authentication_mode
        self.protocol = protocol
        self.cardinality = cardinality
        self.lag_threshold = lag_threshold
        super().__init__(name=name, data_type=data_type)
