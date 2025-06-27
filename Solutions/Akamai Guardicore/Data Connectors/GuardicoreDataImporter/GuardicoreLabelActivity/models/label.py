from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LabelAsset(BaseModel):
    hw_uuid: Optional[str] = ""
    bios_uuid: Optional[str] = ""
    id: str
    orchestration_details: Optional[List[Dict[str, Any]]] = []
    name: str
    labels: Optional[List[str]] = []
    nics: Optional[List[Dict[str, Any]]] = []
    ip_addresses: Optional[List[str]] = []
    guest_agent_details: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}
    label_groups: Optional[List[str]] = []


class LabelCriteria(BaseModel):
    argument: Optional[Any] = ""
    source: Optional[str] = ""
    op: Optional[str] = ""
    field: Optional[str] = ""
    id: Optional[str] = ""
    label_id: Optional[str] = ""


class GuardicoreLabel(BaseModel):
    sampling_timestamp: int
    value: Optional[str] = ""
    dynamic_criteria_counter: Optional[int] = 0
    static_assets: Optional[List[LabelAsset]] = []
    dynamic_assets_counter: Optional[int] = 0
    id: str
    key: str
    dynamic_assets: Optional[List[LabelAsset]] = []
    static_criteria_counter: Optional[int] = 0
    rules_with_label: Optional[int] = 0
    static_assets_counter: Optional[int] = 0
    name: Optional[str] = ""

    class Config:
        extra = "ignore"
