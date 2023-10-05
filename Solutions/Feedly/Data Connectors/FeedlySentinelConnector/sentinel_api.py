import datetime
import hashlib
import hmac
import json
from base64 import b64decode, b64encode

import requests


class SentinelApiConnector:
    def __init__(self, *, workspace_id: str, log_analytics_uri: str, shared_key: str, log_type: str):
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.key_encoder = KeyEncoder(shared_key)
        self.log_type = log_type
        self.uri = log_analytics_uri
        self.resource = "/api/logs"

    def post(self, json_body: list) -> None:
        body = json.dumps(json_body)
        headers = self._build_headers(len(body))
        requests.post(
            self.uri + self.resource, params={"api-version": "2016-04-01"}, data=body, headers=headers
        ).raise_for_status()

    def _build_headers(self, content_length: int) -> dict:
        date = _make_rfc1123date()
        signature = self._build_signature(date, content_length)
        return {
            "content-type": "application/json",
            "Authorization": signature,
            "Log-Type": self.log_type,
            "x-ms-date": date,
        }

    def _build_signature(self, date: str, content_length: int) -> str:
        string_to_hash = SIGNATURE_TEMPLATE.format(content_length=content_length, date=date, resource=self.resource)
        encoded_hash = self.key_encoder.encode(string_to_hash)
        return f"SharedKey {self.workspace_id}:{encoded_hash}"


def _make_rfc1123date() -> str:
    return datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")


SIGNATURE_TEMPLATE = """
POST
{content_length}
application/json
x-ms-date:{date}
{resource}
""".strip()


class KeyEncoder:
    def __init__(self, key: str):
        self.key = b64decode(key)

    def encode(self, text: str) -> str:
        return b64encode(hmac.new(self.key, bytes(text, encoding="utf-8"), digestmod=hashlib.sha256).digest()).decode()
