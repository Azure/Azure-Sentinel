from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_serializer


class Label(BaseModel):
    id: str
    key: str
    value: Optional[str] = ""
    name: str
    color_index: Optional[int] = 0


class LabelGroup(BaseModel):
    id: str
    name: str
    key: Optional[str] = ""
    value: Optional[str] = ""


class Capability(BaseModel):
    is_ok: bool
    name: str
    state: int
    text: str


class Aggregator(BaseModel):
    cluster_id: str
    component_id: str
    hostname: str


class AgentHealth(BaseModel):
    aggregator: Optional[Aggregator] = None
    aggregator_component_id: Optional[str] = None
    capabilities: Optional[List[Capability]] = []
    status: Optional[str] = None
    default_operating_mode: Optional[Any] = None
    dump_present: Optional[bool] = False


class Health(BaseModel):
    controller: Optional[AgentHealth] = None
    deception_agent: Optional[AgentHealth] = None
    enforcement_agent: Optional[AgentHealth] = None
    reveal_agent: Optional[AgentHealth] = None
    access_agent: Optional[AgentHealth] = None
    detection_agent: Optional[AgentHealth] = None


class StatusFlag(BaseModel):
    flag_type: str
    raised_time: Optional[int] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = {}


class GuardicoreAgent(BaseModel):
    sampling_timestamp: int
    id: str = Field(alias="_id")
    agent_id: Optional[str] = ""
    asset_id: Optional[str] = ""
    component_id: Optional[str] = ""
    display_name: Optional[str] = ""
    first_seen: int
    health: Optional[Health] = None
    hostname: Optional[str] = ""
    installed_modules: Optional[List[str]] = []
    ip_addresses: List[str]
    is_agent_missing: Optional[bool] = False
    is_missing: Optional[bool] = False
    last_seen: int
    not_monitored: Optional[bool] = False
    os: Optional[str] = ""
    policy_revision: Optional[int] = 0
    status: str
    status_flags: Optional[List[StatusFlag]] = []
    supported_features: Optional[List[str]] = []
    version: Optional[str] = ""
    is_agent_enforcing: Optional[bool] = False
    configuration: Optional[Dict[str, Any]] = None

    @field_serializer('is_agent_enforcing')
    def serialize_is_agent_enforcing(self, _: bool, _info: Any) -> bool:
        """Determine if agent is in enforcing mode based on configuration data"""
        if hasattr(self, 'configuration') and self.configuration:
            if 'enforcementagent' in self.configuration and 'agent_operating_mode' in self.configuration['enforcementagent']:
                return self.configuration['enforcementagent']['agent_operating_mode'] == "Enforcing"
        return False

    class Config:
        extra = "ignore"