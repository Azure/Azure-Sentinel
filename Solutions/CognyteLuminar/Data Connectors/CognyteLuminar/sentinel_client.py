"""
sentinel_client.py

Client for the Microsoft Sentinel threat-intelligence upload API (STIX
objects):

    POST https://api.ti.sentinel.azure.com/workspaces/{workspaceId}
         /threat-intelligence-stix-objects:upload?api-version=2024-02-01-preview

Limits documented by Microsoft (per caller): 100 objects per request and 100
requests per minute. A `200` can still carry per-record validation errors in
the body (`errors[].recordIndex`), so success is judged on the body, not just
the status code.

Auth: Entra client-credentials token with scope
`https://management.azure.com/.default`; the app needs the *Microsoft
Sentinel Contributor* role on the workspace.
"""

from __future__ import annotations

import logging
import re
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Dict, List, Optional, Sequence

import requests

logger = logging.getLogger(__name__)

UPLOAD_API_HOST = "https://api.ti.sentinel.azure.com"
UPLOAD_API_VERSION = "2024-02-01-preview"
TOKEN_SCOPE = "https://management.azure.com/.default"

MAX_OBJECTS_PER_REQUEST = 100
MAX_REQUESTS_PER_MINUTE = 100
TIMEOUT = 60.0
RETRY_ATTEMPTS = 5
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_RETRY_AFTER_IN_BODY = re.compile(r"try again in (\d+) seconds", re.IGNORECASE)


class SentinelAuthError(Exception):
    """Token acquisition failed."""


class SentinelUploadError(Exception):
    """A request failed after every retry (non-validation failure)."""


@dataclass
class UploadStats:
    requests: int = 0
    objects_submitted: int = 0
    objects_accepted: int = 0
    objects_rejected: int = 0
    rejected_samples: List[Dict[str, Any]] = field(default_factory=list)
    retries: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "requests": self.requests,
            "objects_submitted": self.objects_submitted,
            "objects_accepted": self.objects_accepted,
            "objects_rejected": self.objects_rejected,
            "retries": self.retries,
            "rejected_samples": self.rejected_samples[:10],
        }


class RateLimiter:
    """Sliding-window limiter: at most `max_calls` within any `period` seconds."""

    def __init__(
        self,
        max_calls: int,
        period: float,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.max_calls = max_calls
        self.period = period
        self._sleep = sleep
        self._clock = clock
        self._calls: Deque[float] = deque()

    def acquire(self) -> None:
        now = self._clock()
        while self._calls and now - self._calls[0] >= self.period:
            self._calls.popleft()
        if len(self._calls) >= self.max_calls:
            wait = self.period - (now - self._calls[0]) + 0.05
            logger.info("Upload API rate limit reached; sleeping %.1fs", wait)
            self._sleep(wait)
            now = self._clock()
            while self._calls and now - self._calls[0] >= self.period:
                self._calls.popleft()
        self._calls.append(self._clock())


class SentinelTIClient:
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        workspace_id: str,
        source_system: str,
        session: Optional[requests.Session] = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not all([tenant_id, client_id, client_secret, workspace_id, source_system]):
            raise ValueError("SentinelTIClient: all constructor arguments are required")
        if source_system.strip().lower() == "microsoft sentinel":
            raise ValueError("sourcesystem 'Microsoft Sentinel' is reserved by the API")
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.workspace_id = workspace_id
        self.source_system = source_system
        self.session = session or requests.Session()
        self._sleep = sleep
        self._clock = clock
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self.limiter = RateLimiter(
            MAX_REQUESTS_PER_MINUTE, 60.0, sleep=sleep, clock=clock
        )
        self.upload_url = (
            f"{UPLOAD_API_HOST}/workspaces/{workspace_id}"
            f"/threat-intelligence-stix-objects:upload?api-version={UPLOAD_API_VERSION}"
        )

    # ----- auth -----

    def _token_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

    def get_token(self, force: bool = False) -> str:
        now = self._clock()
        if not force and self._token and now < self._token_expires_at:
            return self._token
        try:
            resp = self.session.post(
                self._token_url(),
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": TOKEN_SCOPE,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=TIMEOUT,
            )
        except requests.RequestException as err:
            raise SentinelAuthError(f"Entra token request failed: {err}") from err
        if resp.status_code != 200:
            raise SentinelAuthError(
                f"Entra token request returned HTTP {resp.status_code}: {resp.text[:300]}"
            )
        body = resp.json()
        token = body.get("access_token")
        if not token:
            raise SentinelAuthError("Entra token response contained no access_token")
        expires_in = int(body.get("expires_in", 3600))
        self._token = token
        # Renew a minute early so a long upload never races the expiry.
        self._token_expires_at = now + max(60, expires_in - 60)
        return token

    # ----- upload -----

    @staticmethod
    def chunks(items: Sequence[Dict[str, Any]], size: int = MAX_OBJECTS_PER_REQUEST):
        for i in range(0, len(items), size):
            yield items[i : i + size]

    def upload(self, objects: Sequence[Dict[str, Any]]) -> UploadStats:
        """Upload all `objects` in chunks of 100; raise on hard failure.

        Validation errors reported in a `200` body are counted and logged but
        do not raise: the rest of the chunk was accepted and retrying would
        not help.
        """
        stats = UploadStats()
        for chunk in self.chunks(list(objects)):
            self._upload_chunk(list(chunk), stats)
        return stats

    def _upload_chunk(self, chunk: List[Dict[str, Any]], stats: UploadStats) -> None:
        payload = {"sourcesystem": self.source_system, "stixobjects": chunk}
        refreshed_once = False
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            self.limiter.acquire()
            headers = {
                "Authorization": f"Bearer {self.get_token()}",
                "Content-Type": "application/json",
            }
            try:
                resp = self.session.post(
                    self.upload_url, json=payload, headers=headers, timeout=TIMEOUT
                )
            except requests.RequestException as err:
                stats.retries += 1
                if attempt == RETRY_ATTEMPTS:
                    raise SentinelUploadError(
                        f"Upload failed (network): {err}"
                    ) from err
                wait = min(60.0, 2.0**attempt)
                logger.warning("Upload network error (%s); retry in %.0fs", err, wait)
                self._sleep(wait)
                continue

            stats.requests += 1
            if resp.status_code == 200:
                self._record_result(chunk, resp, stats)
                return
            if resp.status_code == 401 and not refreshed_once:
                refreshed_once = True
                logger.info("Upload API returned 401; refreshing Entra token")
                self.get_token(force=True)
                continue
            if resp.status_code in RETRYABLE_STATUS and attempt < RETRY_ATTEMPTS:
                stats.retries += 1
                wait = self._retry_delay(resp, attempt)
                logger.warning(
                    "Upload API HTTP %s; retry %d/%d in %.0fs: %s",
                    resp.status_code,
                    attempt,
                    RETRY_ATTEMPTS,
                    wait,
                    resp.text[:200],
                )
                self._sleep(wait)
                continue
            raise SentinelUploadError(
                f"Upload API HTTP {resp.status_code}: {resp.text[:500]}"
            )

    @staticmethod
    def _retry_delay(resp: requests.Response, attempt: int) -> float:
        header = resp.headers.get("Retry-After")
        if header and header.isdigit():
            return float(header) + 1.0
        match = _RETRY_AFTER_IN_BODY.search(resp.text or "")
        if match:
            return float(match.group(1)) + 1.0
        return min(60.0, 2.0**attempt)

    @staticmethod
    def _record_result(
        chunk: List[Dict[str, Any]], resp: requests.Response, stats: UploadStats
    ) -> None:
        stats.objects_submitted += len(chunk)
        errors: List[Dict[str, Any]] = []
        if resp.content:
            try:
                body = resp.json()
                if isinstance(body, dict) and isinstance(body.get("errors"), list):
                    errors = [e for e in body["errors"] if isinstance(e, dict)]
            except ValueError:
                logger.warning("Upload API 200 with non-JSON body: %s", resp.text[:200])
        rejected = 0
        for err in errors:
            idx = err.get("recordIndex")
            obj = chunk[idx] if isinstance(idx, int) and 0 <= idx < len(chunk) else {}
            rejected += 1
            sample = {
                "id": obj.get("id"),
                "type": obj.get("type"),
                "errors": err.get("errorMessages"),
            }
            if len(stats.rejected_samples) < 50:
                stats.rejected_samples.append(sample)
            logger.warning(
                "Upload API rejected %s %s: %s",
                sample["type"],
                sample["id"],
                sample["errors"],
            )
        stats.objects_rejected += rejected
        stats.objects_accepted += len(chunk) - rejected
