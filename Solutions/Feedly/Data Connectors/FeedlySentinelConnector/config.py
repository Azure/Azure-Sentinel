import os
from dataclasses import field

from marshmallow import EXCLUDE, Schema, pre_load
from marshmallow.validate import Regexp
from marshmallow_dataclass import dataclass


class PascalCaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    def on_bind_field(self, field_name, field_obj):
        """Use pascal-case for its external representation and snake-case for internal representation"""
        field_obj.data_key = field_name.title().replace("_", "")


@dataclass(base_schema=PascalCaseSchema)
class FeedlySentinelConfig:
    azure_web_jobs_storage: str
    data_collection_endpoint: str
    dcr_immutable_id: str
    dcr_stream_name: str
    
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str

    feedly_api_key: str
    feedly_stream_ids: str

    days_to_backfill: int = 7

    @staticmethod
    def from_env() -> "FeedlySentinelConfig":
        return FeedlySentinelConfig.Schema().load(os.environ)
