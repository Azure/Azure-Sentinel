"""Base Upwind API client with authentication, retry, and pagination."""

import logging
import time

import requests


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

    def __init__(self, config):
        self.config = config
        self.org_id = config.get("upwind_org_id")
        self.client_id = config.get("upwind_client_id")
        self.client_secret = config.get("upwind_client_secret")
        self.auth_url = config.get("upwind_auth_url")
        self.api_base_url = config.get("upwind_api_base_url")
        self.page_size = config.get("upwind_page_size", 100)
        self.max_retries = config.get("upwind_max_retries")
        self.initial_backoff_seconds = config.get("upwind_initial_backoff_seconds")
        self.max_backoff_seconds = config.get("upwind_max_backoff_seconds")
        self._access_token = None

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
        failures (dropped connections and timeouts). Raises RuntimeError once
        the retry budget is exhausted.
        """

        last_error = None

        for attempt in range(self.max_retries + 1):
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

            if attempt < self.max_retries:
                wait = min(
                    self.initial_backoff_seconds * (2**attempt),
                    self.max_backoff_seconds,
                )
                logging.warning(
                    "Upwind API request failed (%s). Retrying in %ds (attempt %d/%d)...",
                    last_error,
                    wait,
                    attempt + 1,
                    self.max_retries,
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
