"""Client for the Censys Supply Chain risk-events API."""
import time
from typing import Dict, Iterator, List, Optional

import requests

from . import consts
from .exceptions import CensysAuthError, CensysCursorExpired, CensysException, CensysTimeBudgetReached
from .logger import applogger


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

    def get_page(self, params: Dict[str, str], path: Optional[str] = None) -> dict:
        """GET one page, retrying throttling and transient server errors, within the time budget."""
        path = path or consts.RISK_EVENTS_PATH
        url = consts.API_BASE_URL + path
        for attempt in range(1, consts.MAX_RETRIES + 1):
            self._check_budget()
            try:
                resp = self.session.get(url, params=params, timeout=self._timeout())
            except requests.RequestException as err:
                applogger.warning(f"{consts.LOG_PREFIX} get_page: request error (attempt {attempt}): {err}")
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
                items = result.get("risk_events") if path == consts.RISK_EVENTS_PATH else result.get("suppliers")
                what = "events" if path == consts.RISK_EVENTS_PATH else "suppliers"
                applogger.info(f"{consts.LOG_PREFIX} get_page: API call GET {path} params={shown} -> HTTP 200, "
                               f"{len(items or [])} {what}, next_page_token={'yes' if result.get('next_page_token') else 'no'}")
                return body
            if status in (401, 403):
                raise CensysAuthError(f"Censys API rejected the request (HTTP {status}). Check the CensysApiToken and OrganizationId settings: "
                                      f"{resp.text[:300]}")
            if status == 404:
                raise CensysException("Censys returned 404: the organization has no default supply chain. Check the OrganizationId setting.")
            if status == 410:
                raise CensysCursorExpired("The checkpoint is older than the Censys retention window (HTTP 410).")
            if status in (429, 500, 502, 503, 504):
                try:
                    wait = int(resp.headers.get("Retry-After", ""))
                except ValueError:
                    wait = 2 ** attempt
                applogger.warning(f"{consts.LOG_PREFIX} get_page: HTTP {status}, retrying in {min(wait, 60)}s (attempt {attempt})")
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

    def iter_suppliers(self) -> Iterator[List[dict]]:
        """Yield each page of suppliers of the default supply chain until the last page (no next_page_token)."""
        base = {"organization_id": self.organization_id, "page_size": consts.SUPPLIERS_PAGE_SIZE, "order_by": "created_at_asc"}
        page_token, seen = None, set()
        while True:
            params = dict(base)
            if page_token:
                params["page_token"] = page_token
            result = (self.get_page(params, consts.SUPPLIERS_PATH) or {}).get("result") or {}
            suppliers = result.get("suppliers") or []
            if suppliers:
                yield suppliers
            page_token = result.get("next_page_token")
            if not page_token:
                return
            if page_token in seen:
                raise CensysException("Censys returned the same suppliers page token twice, stopping to avoid a loop.")
            seen.add(page_token)
