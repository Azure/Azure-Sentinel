"""Client for the Censys Supply Chain risk-events API."""
import time
from typing import Dict, Iterator, List, Optional

import requests

from . import consts
from .exceptions import CensysAuthError, CensysCursorExpired, CensysException, CensysTimeBudgetReached
from .logger import applogger


def _split(value: str) -> List[str]:
    return [v.strip() for v in (value or "").replace("\n", ",").split(",") if v.strip()]


def build_filters(supplier_ids: str, change_types: str, severity: str, rapid_response: str, risk_type_ids: str = "") -> Dict[str, str]:
    """Return the optional filter query parameters. A filter that is empty is left out of the request."""
    filters: Dict[str, str] = {}
    suppliers = [s for s in _split(supplier_ids) if s.lower() != "supplierids"]
    if suppliers:
        filters["supplier_ids"] = ",".join(suppliers)
    risk_types = [r for r in _split(risk_type_ids) if r.lower() != "risktypeids"]
    if risk_types:
        filters["risk_type_ids"] = ",".join(risk_types)
    types = [t.lower() for t in _split(change_types)]
    bad = [t for t in types if t not in consts.ALLOWED_CHANGE_TYPES]
    if bad:
        applogger.warning(f"{consts.LOG_PREFIX}: ignoring unsupported change_types {bad}")
    types = [t for t in types if t in consts.ALLOWED_CHANGE_TYPES]
    if types:
        filters["change_types"] = ",".join(types)
    sevs = [s.upper() for s in _split(severity)]
    bad = [s for s in sevs if s not in consts.ALLOWED_SEVERITIES]
    if bad:
        applogger.warning(f"{consts.LOG_PREFIX}: ignoring unsupported severity values {bad}")
    sevs = [s for s in sevs if s in consts.ALLOWED_SEVERITIES]
    if sevs:
        filters["severity"] = ",".join(sevs)
    rr = (rapid_response or "").strip().lower()
    if rr in ("true", "false"):
        filters["rapid_response"] = rr
    return filters


class CensysClient:
    """Reads risk events page by page, following the Censys cursor rules."""

    def __init__(self, api_token: str, organization_id: str, deadline: Optional[float] = None,
                 hard_deadline: Optional[float] = None, session: Optional[requests.Session] = None):
        """Create the client with a bearer token.

        deadline: no API call is started at or after this time (epoch seconds).
        hard_deadline: no API call is allowed to run past this time.
        """
        self.deadline = deadline
        self.hard_deadline = hard_deadline
        self.organization_id = organization_id
        self.url = consts.API_BASE_URL + consts.RISK_EVENTS_PATH
        self.session = session or requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_token}", "Accept": "application/json"})

    def _check_budget(self) -> None:
        if self.deadline is not None and time.time() >= self.deadline:
            raise CensysTimeBudgetReached("Time budget reached, no further Censys API call is started.")

    def _wait(self, seconds: float) -> None:
        """Sleep, but never past the deadline."""
        if self.deadline is not None:
            seconds = min(seconds, max(0.0, self.deadline - time.time()))
        time.sleep(seconds)

    def _timeout(self) -> float:
        if self.hard_deadline is None:
            return consts.REQUEST_TIMEOUT
        return max(1.0, min(consts.REQUEST_TIMEOUT, self.hard_deadline - time.time()))

    def get_page(self, params: Dict[str, str]) -> dict:
        """GET one page, retrying throttling and transient server errors, within the time budget."""
        for attempt in range(1, consts.MAX_RETRIES + 1):
            self._check_budget()
            try:
                resp = self.session.get(self.url, params=params, timeout=self._timeout())
            except requests.RequestException as err:
                applogger.warning(f"{consts.LOG_PREFIX}: request error (attempt {attempt}): {err}")
                self._wait(min(2 ** attempt, 60))
                continue
            status = resp.status_code
            if status == 200:
                try:
                    body = resp.json()
                except ValueError:
                    raise CensysException(f"Censys returned HTTP 200 with a body that is not valid JSON: {resp.text[:200]}")
                result = (body or {}).get("result") or {}
                shown = {k: ("<set>" if k == "page_token" else v) for k, v in params.items()}
                applogger.info(f"{consts.LOG_PREFIX}: API call GET {consts.RISK_EVENTS_PATH} params={shown} -> HTTP 200, "
                               f"{len(result.get('risk_events') or [])} events, next_page_token={'yes' if result.get('next_page_token') else 'no'}")
                return body
            if status in (401, 403):
                raise CensysAuthError(f"Censys API rejected the request (HTTP {status}): {resp.text[:300]}")
            if status == 404:
                raise CensysException("Censys returned 404: the organization has no default supply chain.")
            if status == 410:
                raise CensysCursorExpired("The checkpoint is older than the Censys retention window (HTTP 410).")
            if status in (429, 500, 502, 503, 504):
                try:
                    wait = int(resp.headers.get("Retry-After", ""))
                except ValueError:
                    wait = 2 ** attempt
                applogger.warning(f"{consts.LOG_PREFIX}: HTTP {status}, retrying in {min(wait, 60)}s (attempt {attempt})")
                self._wait(min(wait, 60))
                continue
            raise CensysException(f"Censys API error (HTTP {status}): {resp.text[:300]}")
        raise CensysException(f"Censys API still failing after {consts.MAX_RETRIES} attempts.")

    def iter_pages(self, inserted_after_time: str, inserted_after_event_id: Optional[str],
                   filters: Dict[str, str]) -> Iterator[List[dict]]:
        """Yield each page of events, oldest first, until the last page (no next_page_token).

        Every request of one read keeps the same inserted_after_time / inserted_after_event_id, as the API
        requires when page_token is used.
        """
        base = {
            "organization_id": self.organization_id,
            "page_size": consts.PAGE_SIZE,
            "inserted_after_time": inserted_after_time,
        }
        if inserted_after_event_id:
            base["inserted_after_event_id"] = inserted_after_event_id
        base.update(filters)
        page_token = None
        while True:
            params = dict(base)
            if page_token:
                params["page_token"] = page_token
            result = (self.get_page(params) or {}).get("result") or {}
            events = result.get("risk_events") or []
            if events:
                yield events
            page_token = result.get("next_page_token")
            if not page_token:
                return
