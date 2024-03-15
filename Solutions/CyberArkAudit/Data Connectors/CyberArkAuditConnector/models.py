import time
from typing import Optional

from pydantic import BaseModel, Field


class TokenModel(BaseModel):
    token: str
    expiration: int
    timestamp: int = int(time.time())

    def is_expired(self) -> bool:
        return self.timestamp + self.expiration <= int(time.time())

    @staticmethod
    def get_file_name() -> str:
        return 'token.json'


class QueryModel(BaseModel):
    query: dict = {}
    cursor: str

    @staticmethod
    def get_file_name() -> str:
        return 'query.json'


class DCREventModel(BaseModel):
    CyberArkTenantId: str = Field(alias='tenantId')  # tenantId is a reserved name in Log Analytics Workspace
    timestamp: int = 0,
    username: Optional[str] = ''
    applicationCode: Optional[str] = ''
    auditCode: Optional[str] = ''
    auditType: Optional[str] = ''
    action: Optional[str] = ''
    userId: Optional[str] = ''
    source: Optional[str] = ''
    actionType: Optional[str] = ''
    component: Optional[str] = ''
    serviceName: Optional[str] = ''
    target: Optional[str] = ''
    command: Optional[str] = ''
    sessionId: Optional[str] = ''
    message: Optional[str] = ''
