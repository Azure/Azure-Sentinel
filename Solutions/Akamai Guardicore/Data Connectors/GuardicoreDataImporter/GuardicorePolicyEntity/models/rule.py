from typing import Optional, Any, List, Dict
from datetime import datetime
from pydantic import BaseModel, field_serializer


class WorkSite(BaseModel):
    id: str
    name: str


class Attributes(BaseModel):
    worksite: Optional[WorkSite] = None
    k8s_cluster_type: Optional[str] = None
    restricted_rule: Optional[bool] = None


class ICMPCode(BaseModel):
    icmp_type: int
    version: str
    icmp_codes: List[int]


class Asset(BaseModel):
    id: str


class LabelAndCondition(BaseModel):
    and_labels: List[Dict[str, str]]


class Labels(BaseModel):
    or_labels: List[LabelAndCondition]


class LabelGroup(BaseModel):
    id: str


class UserGroup(BaseModel):
    id: str
    name: str


class EndpointDefinition(BaseModel):
    subnets: List[Any] = []
    assets: List[Asset] = []
    address_classification: Optional[str] = None
    labels: Optional[Labels] = None
    label_groups: List[LabelGroup] = []
    user_groups: List[UserGroup] = []
    processes: List[Any] = []
    domains: List[Any] = []


class PortRange(BaseModel):
    start: int
    end: int


class StaticAssets(BaseModel):
    id: str
    name: str
    ip_addresses: List[str]


class Criteria(BaseModel):
    label_id: str
    source: str
    field: str
    op: str
    argument: str
    id: str
    compound_criteria: Optional[List[Dict[str, Any]]] = None


class ScopeItem(BaseModel):
    static_assets: Optional[StaticAssets] = None
    key: Optional[str] = None
    implicit_criteria: Optional[Criteria] = None
    static_criteria: Optional[Criteria] = None
    rules_with_label: int = 0
    dynamic_criteria_counter: int = 0
    dynamic_assets: Optional[StaticAssets] = None
    dynamic_assets_counter: int = 0
    id: str
    static_assets_counter: int = 0
    value: Optional[str] = None
    dynamic_criteria: List[Criteria] = []
    static_criteria_counter: int = 0


class Author(BaseModel):
    id: str
    username: str
    description: Optional[str] = None


class GuardicorePolicyRule(BaseModel):
    sampling_timestamp: int
    attributes: Optional[Attributes] = None
    icmp_matches: List[ICMPCode] = []
    ports: List[int] = []
    enabled: bool
    section_position: str
    comments: Optional[str] = ""
    destination: EndpointDefinition
    exclude_ports: List[int] = []
    hit_count: int = 0
    read_only: bool
    id: str
    action: str
    state: str
    scope: List[ScopeItem] = []
    ruleset_name: str
    source: EndpointDefinition
    port_ranges: List[PortRange] = []
    network_profile: str
    exclude_port_ranges: List[PortRange] = []
    ip_protocols: List[str] = []
    author: Author


    class Config:
        extra = "ignore"