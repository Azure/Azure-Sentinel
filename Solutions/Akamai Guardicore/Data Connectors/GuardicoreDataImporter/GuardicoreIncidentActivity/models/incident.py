from typing import Optional, List
from pydantic import BaseModel


class Metadata(BaseModel):
    internal: Optional[bool] = False
    country_code: Optional[str] = None
    country: Optional[str] = None
    display_name: Optional[str] = None


class PropertyData(BaseModel):
    type: str
    key: str
    value: str
    metadata: Optional[Metadata] = None


class Properties(BaseModel):
    data: List[PropertyData]
    count: int


class TagData(BaseModel):
    data: List[str]
    count: int


class AffectedAssetData(BaseModel):
    type: str
    value: str
    display_name: str


class AffectedAssets(BaseModel):
    data: List[AffectedAssetData]
    count: int


class GuardicoreIncident(BaseModel):
    id: str
    type: str
    severity: str
    affected_assets: AffectedAssets
    description: str
    tags: TagData
    time: int
    is_legacy: bool
    properties: Properties

    class Config:
        extra = "ignore"