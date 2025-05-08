from typing import List, Optional
from pydantic import BaseModel, Field


class Label(BaseModel):
    id: str
    key: str
    value: str
    name: str
    color_index: int

class LabelGroup(BaseModel):
    id: str
    name: str


class GuardicoreAsset(BaseModel):
    sampling_timestamp: int
    id: str = Field(alias="_id")
    active: bool
    bios_uuid: Optional[str] = ""
    component_cluster_id: Optional[str] = ""
    doc_version: Optional[int] = 0
    first_seen: int
    hw_uuid: Optional[str] = ""
    is_agent_installed: Optional[bool] = False
    is_on: bool
    label_groups: List[LabelGroup]
    last_guest_agent_details_update: Optional[int] = 0
    last_seen: int
    name: str
    replicated_labels: List[str]
    revision: int
    sync_revision: Optional[int] = 0
    vm_name: str
    vm_id: str
    ip_addresses: List[str]
    mac_addresses: List[str]
    full_name: str
    status: str
    comments: str
    agent_id: Optional[str] = ""
    labels: List[Label]

    class Config:
        extra = "ignore"