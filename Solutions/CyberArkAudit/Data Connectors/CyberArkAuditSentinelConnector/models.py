import time
from pydantic import BaseModel


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

