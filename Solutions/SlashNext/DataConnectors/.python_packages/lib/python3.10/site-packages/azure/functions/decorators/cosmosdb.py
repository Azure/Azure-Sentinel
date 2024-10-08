#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from datetime import time
from typing import Optional, Union

from azure.functions.decorators.constants import COSMOS_DB, COSMOS_DB_TRIGGER
from azure.functions.decorators.core import DataType, InputBinding, \
    OutputBinding, Trigger


#  Used by cosmos_db_input_v3
class CosmosDBInputV3(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 data_type: Optional[DataType] = None,
                 id: Optional[str] = None,
                 sql_query: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 **kwargs):
        self.database_name = database_name
        self.collection_name = collection_name
        self.connection_string_setting = connection_string_setting
        self.partition_key = partition_key
        self.id = id
        self.sql_query = sql_query
        super().__init__(name=name, data_type=data_type)


#  Used by cosmos_db_output_v3
class CosmosDBOutputV3(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 create_if_not_exists: Optional[bool] = None,
                 collection_throughput: Optional[int] = None,
                 use_multiple_write_locations: Optional[bool] = None,
                 preferred_locations: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.database_name = database_name
        self.collection_name = collection_name
        self.connection_string_setting = connection_string_setting
        self.create_if_not_exists = create_if_not_exists
        self.partition_key = partition_key
        self.collection_throughput = collection_throughput
        self.use_multiple_write_locations = use_multiple_write_locations
        self.preferred_locations = preferred_locations
        super().__init__(name=name, data_type=data_type)


# Used by cosmos_db_output_v3
class CosmosDBTriggerV3(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB_TRIGGER

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 leases_collection_throughput: Optional[int] = None,
                 checkpoint_interval: Optional[int] = None,
                 checkpoint_document_count: Optional[int] = None,
                 feed_poll_delay: Optional[int] = None,
                 lease_renew_interval: Optional[int] = None,
                 lease_acquire_interval: Optional[int] = None,
                 lease_expiration_interval: Optional[int] = None,
                 max_items_per_invocation: Optional[int] = None,
                 start_from_beginning: Optional[bool] = None,
                 create_lease_collection_if_not_exists: Optional[bool] = None,
                 preferred_locations: Optional[str] = None,
                 data_type: Optional[Union[DataType]] = None,
                 lease_collection_name: Optional[str] = None,
                 lease_connection_string_setting: Optional[str] = None,
                 lease_database_name: Optional[str] = None,
                 lease_collection_prefix: Optional[str] = None,
                 **kwargs):
        self.lease_collection_name = lease_collection_name
        self.lease_connection_string_setting = lease_connection_string_setting
        self.lease_database_name = lease_database_name
        self.create_lease_collection_if_not_exists = \
            create_lease_collection_if_not_exists
        self.leases_collection_throughput = leases_collection_throughput
        self.lease_collection_prefix = lease_collection_prefix
        self.checkpoint_interval = checkpoint_interval
        self.checkpoint_document_count = checkpoint_document_count
        self.feed_poll_delay = feed_poll_delay
        self.lease_renew_interval = lease_renew_interval
        self.lease_acquire_interval = lease_acquire_interval
        self.lease_expiration_interval = lease_expiration_interval
        self.max_items_per_invocation = max_items_per_invocation
        self.start_from_beginning = start_from_beginning
        self.preferred_locations = preferred_locations
        self.connection_string_setting = connection_string_setting
        self.database_name = database_name
        self.collection_name = collection_name
        super().__init__(name=name, data_type=data_type)


#  Used by cosmos_db_input
class CosmosDBInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB

    def __init__(self,
                 name: str,
                 connection: str,
                 database_name: str,
                 container_name: str,
                 partition_key: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 id: Optional[str] = None,
                 sql_query: Optional[str] = None,
                 preferred_locations: Optional[str] = None,
                 **kwargs):
        self.database_name = database_name
        self.container_name = container_name
        self.connection = connection
        self.partition_key = partition_key
        self.id = id
        self.sql_query = sql_query
        self.preferred_locations = preferred_locations
        super().__init__(name=name, data_type=data_type)


#  Used by cosmos_db_output
class CosmosDBOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB

    def __init__(self,
                 name: str,
                 connection: str,
                 database_name: str,
                 container_name: str,
                 create_if_not_exists: Optional[bool] = None,
                 partition_key: Optional[str] = None,
                 container_throughput: Optional[int] = None,
                 preferred_locations: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.connection = connection
        self.database_name = database_name
        self.container_name = container_name
        self.create_if_not_exists = create_if_not_exists
        self.partition_key = partition_key
        self.container_throughput = container_throughput
        self.preferred_locations = preferred_locations
        super().__init__(name=name, data_type=data_type)


#  Used by cosmos_db_trigger
class CosmosDBTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB_TRIGGER

    def __init__(self,
                 name: str,
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
                 data_type: Optional[Union[DataType]] = None,
                 **kwargs):
        self.connection = connection
        self.database_name = database_name
        self.container_name = container_name
        self.lease_connection = lease_connection
        self.lease_database_name = lease_database_name
        self.lease_container_name = lease_container_name
        self.create_lease_container_if_not_exists = \
            create_lease_container_if_not_exists
        self.leases_container_throughput = leases_container_throughput
        self.lease_container_prefix = lease_container_prefix
        self.feed_poll_delay = feed_poll_delay
        self.lease_acquire_interval = lease_acquire_interval
        self.lease_expiration_interval = lease_expiration_interval
        self.lease_renew_interval = lease_renew_interval
        self.max_items_per_invocation = max_items_per_invocation
        self.start_from_beginning = start_from_beginning
        self.start_from_time = start_from_time
        self.preferred_locations = preferred_locations
        super().__init__(name=name, data_type=data_type)
