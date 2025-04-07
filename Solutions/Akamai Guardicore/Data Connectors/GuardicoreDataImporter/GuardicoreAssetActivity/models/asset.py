from typing import List, Optional
from pydantic import BaseModel, Field

class GuardicoreAsset(BaseModel):
    sampling_timestamp: int
    id: str = Field(alias="_id")
    active: bool
    bios_uuid: Optional[str] = ""
    doc_version: Optional[int] = 0
    first_seen: int
    hw_uuid: Optional[str] = ""
    is_agent_installed: Optional[bool] = False
    is_on: bool
    last_guest_agent_details_update: Optional[int] = 0
    last_seen: int
    name: str
    revision: int
    vm_name: str
    vm_id: str
    full_name: str
    status: str
    comments: str
    agent_id: Optional[str] = ""

    class Config:
        extra = "ignore"