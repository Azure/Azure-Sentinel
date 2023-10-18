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
    sentinel_workspace_id: str
    sentinel_workspace_key: str
    sentinel_log_analytics_uri: str = field(
        metadata={"validate": Regexp(r"^https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$")}
    )

    feedly_api_key: str
    feedly_stream_ids: str

    days_to_backfill: int = 7

    @pre_load
    def make_default_log_analytics_uri(self, data: dict, **kwargs) -> dict:
        if "SentinelLogAnalyticsUri" not in data:
            data["SentinelLogAnalyticsUri"] = "https://" + data["SentinelWorkspaceId"] + ".ods.opinsights.azure.com"
        return data

    @staticmethod
    def from_env() -> "FeedlySentinelConfig":
        return FeedlySentinelConfig.Schema().load(os.environ)
