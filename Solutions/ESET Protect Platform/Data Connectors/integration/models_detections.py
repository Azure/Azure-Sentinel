import typing as t
from datetime import datetime

from pydantic import BaseModel, Field, computed_field, field_validator


class NetworkCommunication(BaseModel):
    direction: str
    localIpAddress: str
    localPort: int
    protocolName: str
    remoteIpAddress: str
    remotePort: int


class Context(BaseModel):
    circumstances: str
    deviceUuid: str
    process: dict[str, str]
    userName: str


class Response(BaseModel):
    description: str
    deviceRestartRequired: bool
    displayName: str
    protectionName: str
    actionType: t.Optional[str] = ""


class Device(BaseModel):
    displayName: str
    uuid: str


class Process(BaseModel):
    commandLine: str
    path: str
    uuid: str


class TriggeringEvent(BaseModel):
    type: str
    data: t.Optional[dict[str, t.Any]]


class Detection(BaseModel):
    device: t.Optional[Device] = Field(default=None, exclude=True)
    process: t.Optional[Process] = Field(default=None, exclude=True)
    context: t.Optional[Context] = Field(default=None, exclude=True)
    networkCommunication: t.Optional[NetworkCommunication] = None
    responses: list[Response]
    category: str
    displayName: str
    objectHashSha1: str
    objectName: str
    objectTypeName: str
    objectUrl: str
    occurTime: str
    TimeGenerated: str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    severityLevel: str
    typeName: str
    customUuid: str = Field(alias="uuid", exclude=True)
    detectionOccurenceUuids: t.Optional[list[str]] = Field(default=None, exclude=True)
    groupSize: int = 1
    severityScore: t.Optional[str] = None
    userName: t.Optional[str] = ""
    objectSizeBytes: t.Optional[int] = None
    edrRuleUuid: t.Optional[str] = None
    note: t.Optional[str] = None
    resolved: t.Optional[bool] = None
    cloudOfficeTenantUuid: t.Optional[str] = None
    scanUuid: t.Optional[str] = None
    triggeringEvent: t.Optional[TriggeringEvent] = None

    @computed_field(return_type=str | list[str])
    def detectionUuid(self) -> str | list[str]:
        return self.detectionOccurenceUuids if self.detectionOccurenceUuids else self.customUuid

    @computed_field(return_type=str | None)
    def deviceDisplayName(self)-> str | None :
        return self.device.displayName if self.device else None

    @computed_field(return_type=str | None)
    def deviceUuid(self)-> str | None:
        if self.device:
            return self.device.uuid
        elif self.context:
            return self.context.deviceUuid
        return None

    @computed_field(return_type=str | None)
    def userNameBase(self)-> str | None:
        return self.context.userName if self.context else self.userName

    @computed_field(return_type=str | None)
    def processPath(self)-> str | None:
        if self.process:
            return self.process.path
        elif self.context:
            return self.context.process.get("path")
        return None

    @computed_field(return_type=str | None)
    def processUuid(self)-> str | None:
        return self.process.uuid if self.process else None

    @computed_field(return_type=str | None)
    def processCommandline(self)-> str | None:
        return self.process.commandLine if self.process else None

    @field_validator('severityScore', mode='before')
    @classmethod
    def convert_int_to_str(cls, v: int | str | None) -> str | int | None:
        return str(v) if isinstance(v, int) else v


class Detections(BaseModel):
    detections: list[Detection]
    nextPageToken: str = Field(exclude=True)
    totalSize: t.Optional[int] = Field(default=None, exclude=True)
