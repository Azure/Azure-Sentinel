from datetime import datetime

from pydantic import BaseModel, Field


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


class Detection(BaseModel):
    context: Context
    networkCommunication: NetworkCommunication
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
    customUuid: str = Field(alias="uuid")


class Detections(BaseModel):
    detections: list[Detection]
    nextPageToken: str
    totalSize: int
