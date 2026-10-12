"""Base Upwind API client with authentication, retry, and pagination."""

import logging
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests


class RunTimeBudgetExceeded(Exception):
    """
    Raised when a fetch is stopped because the run's time budget is spent.

    Stopping on our own terms, before the Functions host kills the invocation
    at ``functionTimeout``, lets the run finish cleanly and log what it did.
    Every page fetched before the stop has already been uploaded.
    """



class RunTimeBudget:
    """Wall-clock budget shared by every dataset fetched in a single run."""

    def __init__(self, seconds: float):
        self._deadline = time.monotonic() + seconds

    def remaining_seconds(self) -> float:
        """Seconds left before the budget is spent (never negative)."""
        return max(0.0, self._deadline - time.monotonic())

    def is_exhausted(self) -> bool:
        """True once no time is left in the budget."""
        return self.remaining_seconds() <= 0

    def share(self, parts: int) -> "RunTimeBudget":
        """A new budget holding an even 1/``parts`` share of the time left."""
        return RunTimeBudget(self.remaining_seconds() / parts)


def parse_retry_after_seconds(retry_after):
    """
    Parse an HTTP ``Retry-After`` header value into seconds.

    :param retry_after: Header value, either delta-seconds ("30") or an
        HTTP-date ("Wed, 21 Oct 2015 07:28:00 GMT").
    :return: Non-negative seconds to wait, or None if absent or unparseable.
    """

    if not retry_after:
        return None

    value = str(retry_after).strip()
    if value.isdigit():
        return int(value)

    try:
        retry_at = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None

    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    return max(0, int((retry_at - datetime.now(timezone.utc)).total_seconds()))


def rename_reserved_columns(records: list, rename_map: dict) -> list:
    """
    Rename dictionary keys that collide with reserved/invalid Log Analytics
    custom-table column names (e.g. "title", "type" are rejected by the
    workspace table schema API) before the records are uploaded.

    :param records: List of raw API record dictionaries.
    :param rename_map: Mapping of {original_key: new_key} to apply per record.
    :return: New list of dictionaries with the renamed keys (original list is
        not mutated).
    """

    if not rename_map:
        return records

    renamed = []
    for record in records:
        new_record = dict(record)
        for old_key, new_key in rename_map.items():
            if old_key in new_record:
                new_record[new_key] = new_record.pop(old_key)
        renamed.append(new_record)
    return renamed


# Severity ladder shared by every dataset that supports severity filtering.
# Ordered from least to most severe; a configured minimum selects that level
# and everything above it.
SEVERITY_ORDER = ("low", "medium", "high", "critical")


def severities_at_least(min_severity) -> list:
    """
    Expand a minimum severity into the list of severities at or above it.

    The Upwind API filters by explicit severity values rather than a threshold,
    so "high" becomes ["high", "critical"].

    :param min_severity: Configured minimum, case-insensitive. Falsy disables
        filtering.
    :return: List of severity values, or None when no filtering should apply.
    """

    if not min_severity:
        return None

    normalized = str(min_severity).strip().lower()
    if normalized not in SEVERITY_ORDER:
        logging.warning(
            "Ignoring unrecognized minimum severity %r; expected one of %s. "
            "No severity filter will be applied.",
            min_severity,
            ", ".join(SEVERITY_ORDER),
        )
        return None

    return list(SEVERITY_ORDER[SEVERITY_ORDER.index(normalized):])


class UpwindClient:
    """Base client for the Upwind API with authentication, retry, and pagination."""

    # Rate limiting plus transient server-side failures. Any other status is
    # returned to the caller untouched.
    RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)

    def __init__(self, config, time_budget: RunTimeBudget = None):
        self.config = config
        self.time_budget = time_budget
        self.org_id = config.get("upwind_org_id")
        self.client_id = config.get("upwind_client_id")
        self.client_secret = config.get("upwind_client_secret")
        self.auth_url = config.get("upwind_auth_url")
        self.api_base_url = config.get("upwind_api_base_url")
        self.page_size = config.get("upwind_page_size", 100)
        self.max_retries = config.get("upwind_max_retries")
        self.initial_backoff_seconds = config.get("upwind_initial_backoff_seconds")
        self.max_backoff_seconds = config.get("upwind_max_backoff_seconds")
        self.max_requests_per_minute = config.get("upwind_max_requests_per_minute")
        self._next_request_at = 0.0
        self._access_token = None

    def _wait_for_request_slot(self) -> None:
        """
        Pace requests to at most ``max_requests_per_minute``.

        The Upwind inventory API rate-limits per organization, shared by every
        API key and integration in that org, so sending as fast as possible
        both trips the limit and starves the org's other clients. A falsy
        limit disables pacing.
        """

        if not self.max_requests_per_minute:
            return

        delay = self._next_request_at - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self._next_request_at = time.monotonic() + 60.0 / self.max_requests_per_minute

    def _stop_if_time_budget_exhausted(self) -> None:
        """Raise RunTimeBudgetExceeded once the run's time budget is spent."""

        if self.time_budget and self.time_budget.is_exhausted():
            raise RunTimeBudgetExceeded()

    def _retry_wait_seconds(self, attempt: int, response) -> int:
        """
        How long to wait before the next retry.

        A 429 carrying ``Retry-After`` is honored as-is, since that is exactly
        when the server will accept the request again; retrying sooner just
        burns the retry budget on more 429s. Otherwise exponential backoff.
        """

        if response is not None and response.status_code == 429:
            retry_after = parse_retry_after_seconds(response.headers.get("Retry-After"))
            if retry_after is not None:
                return retry_after

        return min(
            self.initial_backoff_seconds * (2**attempt),
            self.max_backoff_seconds,
        )

    def _get_access_token(self) -> str:
        """Obtain a bearer token from the Upwind auth endpoint using client credentials."""

        logging.info("Requesting Upwind API access token...")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "audience": self.api_base_url,
        }

        response = requests.post(self.auth_url, json=payload, timeout=30)
        response.raise_for_status()

        self._access_token = response.json()["access_token"]
        logging.info("Upwind API access token obtained.")
        return self._access_token

    def _fetch_paginated(self, url: str, search_body: dict, on_page) -> int:
        """
        Fetch all items from a paginated Upwind API search endpoint.
        Uses cursor-based pagination and exponential backoff for 429 rate limits.

        :param url: The full API endpoint URL.
        :param search_body: The JSON search body to POST.
        :param on_page: Callback invoked with each page's items as they are
            fetched, so pages can be uploaded without buffering the whole
            dataset in memory.
        :return: Total number of items fetched across all pages.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        :raises RunTimeBudgetExceeded: If the run's time budget runs out first.
        """

        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        total = 0
        cursor = None
        page_number = 0

        while True:
            self._stop_if_time_budget_exhausted()
            page_number += 1
            params = {"limit": self.page_size}
            if cursor:
                params["cursor"] = cursor

            response = self._request_with_retry(url, headers, search_body, params)

            if not 200 <= response.status_code < 300:
                raise RuntimeError(
                    f"Upwind API returned status {response.status_code}: {response.text}"
                )

            result = response.json()
            items = result.get("items", [])
            total += len(items)
            on_page(items)

            logging.info(
                "Page %d: fetched %d items (total so far: %d)",
                page_number,
                len(items),
                total,
            )

            metadata = result.get("metadata", {})
            cursor = metadata.get("next_cursor")
            if not cursor:
                break

        logging.info("Fetched %d total items from Upwind API.", total)
        return total

    def _send_with_retry(
        self, method, url, headers, params, json_body=None
    ) -> requests.Response:
        """
        Execute an HTTP request with exponential backoff.

        Retries on rate limiting (429), transient server errors, and network
        failures (dropped connections and timeouts). A 429 is retried for as
        long as the run's time budget allows, since the limit is shared across
        the org and waiting it out is the only way through; other failures get
        ``max_retries`` attempts. Raises RuntimeError once retries are
        exhausted, or RunTimeBudgetExceeded when the next wait would run past
        the run's time budget.
        """

        last_error = None
        attempt = 0

        while True:
            self._wait_for_request_slot()
            response = None
            try:
                response = requests.request(
                    method,
                    url,
                    json=json_body,
                    headers=headers,
                    params=params,
                    timeout=60,
                )

                if response.status_code not in self.RETRYABLE_STATUS_CODES:
                    return response

                last_error = f"HTTP {response.status_code}: {response.text}"
            except (requests.ConnectionError, requests.Timeout) as e:
                last_error = f"{type(e).__name__}: {e}"

            is_rate_limited = response is not None and response.status_code == 429
            retries_unbounded = is_rate_limited and self.time_budget is not None

            if attempt >= self.max_retries and not retries_unbounded:
                break

            wait = self._retry_wait_seconds(attempt, response)

            # Sleeping past the deadline only hands the invocation to the
            # host's hard timeout; stop now so the run ends cleanly.
            if self.time_budget and wait >= self.time_budget.remaining_seconds():
                logging.warning(
                    "Upwind API request failed (%s) and the %ds retry wait "
                    "exceeds the remaining run time budget. Stopping.",
                    last_error,
                    wait,
                )
                raise RunTimeBudgetExceeded()

            attempt += 1
            logging.warning(
                "Upwind API request failed (%s). Retrying in %ds (attempt %d)...",
                last_error,
                wait,
                attempt,
            )
            time.sleep(wait)

        raise RuntimeError(
            f"Upwind API request to {url} failed after "
            f"{self.max_retries} retries: {last_error}"
        )

    def _request_with_retry(self, url, headers, json_body, params) -> requests.Response:
        """Execute a POST request with retry on transient failures."""

        return self._send_with_retry("POST", url, headers, params, json_body=json_body)

    def _get_with_retry(self, url, headers, params) -> requests.Response:
        """Execute a GET request with retry on transient failures."""

        return self._send_with_retry("GET", url, headers, params)

    def _fetch_page_paginated(self, url: str, base_params: dict, on_page) -> int:
        """
        Fetch all items from a GET endpoint using 1-based page-number pagination
        (page + per-page query params). Stops when a page returns fewer items
        than the requested page size, or an empty page.

        :param url: The full API endpoint URL.
        :param base_params: Query params to send on every page (time window, per-page, etc).
        :param on_page: Callback invoked with each page's items as they are
            fetched, so pages can be uploaded without buffering the whole
            dataset in memory.
        :return: Total number of items fetched across all pages.
        """

        token = self._get_access_token()
        headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}

        total = 0
        page = 1

        while True:
            self._stop_if_time_budget_exhausted()
            params = dict(base_params)
            params["page"] = page

            response = self._get_with_retry(url, headers, params)

            if not 200 <= response.status_code < 300:
                raise RuntimeError(
                    f"Upwind API returned status {response.status_code}: {response.text}"
                )

            result = response.json()
            items = result if isinstance(result, list) else result.get("items", result.get("data", []))
            total += len(items)
            on_page(items)

            logging.info(
                "Page %d: fetched %d items (total so far: %d)",
                page,
                len(items),
                total,
            )

            if len(items) < self.page_size:
                break
            page += 1

        logging.info("Fetched %d total items from Upwind API.", total)
        return total

    def _fetch_link_header_paginated(self, url: str, base_params: dict, on_page) -> int:
        """
        Fetch all items from a GET endpoint that paginates via the standard
        HTTP `Link` response header (rel="next"), e.g. GitHub-style pagination.

        :param url: The full API endpoint URL.
        :param base_params: Query params to send on the first request (e.g. per-page).
        :param on_page: Callback invoked with each page's items as they are
            fetched, so pages can be uploaded without buffering the whole
            dataset in memory.
        :return: Total number of items fetched across all pages.
        """

        token = self._get_access_token()
        headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}

        total = 0
        next_url = url
        params = dict(base_params)
        page_number = 0

        while next_url:
            self._stop_if_time_budget_exhausted()
            page_number += 1
            response = self._get_with_retry(next_url, headers, params)

            if not 200 <= response.status_code < 300:
                raise RuntimeError(
                    f"Upwind API returned status {response.status_code}: {response.text}"
                )

            result = response.json()
            items = result if isinstance(result, list) else result.get("items", result.get("data", []))
            total += len(items)
            on_page(items)

            logging.info(
                "Page %d: fetched %d items (total so far: %d)",
                page_number,
                len(items),
                total,
            )

            next_link = response.links.get("next")
            next_url = next_link["url"] if next_link else None
            params = None  # the next-page URL already carries its own query string

        logging.info("Fetched %d total items from Upwind API.", total)
        return total
