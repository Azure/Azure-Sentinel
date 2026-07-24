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


class UpwindClient:
    """Base client for the Upwind API with authentication, retry, and pagination."""

    def __init__(self, config):
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

    def _fetch_paginated(self, url: str, search_body: dict) -> list:
        """
        Fetch all items from a paginated Upwind API search endpoint.
        Uses cursor-based pagination and exponential backoff for 429 rate limits.

        :param url: The full API endpoint URL.
        :param search_body: The JSON search body to POST.
        :return: List of item dictionaries from all pages.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        all_items = []
        cursor = None
        page_number = 0

        while True:
            page_number += 1
            params = {"limit": self.page_size}
            if cursor:
                params["cursor"] = cursor

            response = self._request_with_retry(url, headers, search_body, params)

            if response.status_code != 200:
                raise RuntimeError(
                    f"Upwind API returned status {response.status_code}: {response.text}"
                )

            result = response.json()
            items = result.get("items", [])
            all_items.extend(items)

            logging.info(
                "Page %d: fetched %d items (total so far: %d)",
                page_number,
                len(items),
                len(all_items),
            )

            metadata = result.get("metadata", {})
            cursor = metadata.get("next_cursor")
            if not cursor:
                break

        logging.info("Fetched %d total items from Upwind API.", len(all_items))
        return all_items

    def _request_with_retry(self, url, headers, json_body, params) -> requests.Response:
        """Execute a POST request with exponential backoff on 429 responses."""

        for attempt in range(self.max_retries + 1):
            response = requests.post(
                url, json=json_body, headers=headers, params=params, timeout=60
            )

            if response.status_code != 429:
                return response

            if attempt < self.max_retries:
                wait = min(
                    self.initial_backoff_seconds * (2**attempt),
                    self.max_backoff_seconds,
                )
                logging.warning(
                    "Rate limited (429). Retrying in %ds (attempt %d/%d)...",
                    wait,
                    attempt + 1,
                    self.max_retries,
                )
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"Upwind API rate limit exceeded after {self.max_retries} retries: "
                    f"{response.text}"
                )

    def _get_with_retry(self, url, headers, params) -> requests.Response:
        """Execute a GET request with exponential backoff on 429 responses."""

        for attempt in range(self.max_retries + 1):
            response = requests.get(url, headers=headers, params=params, timeout=60)

            if response.status_code != 429:
                return response

            if attempt < self.max_retries:
                wait = min(
                    self.initial_backoff_seconds * (2**attempt),
                    self.max_backoff_seconds,
                )
                logging.warning(
                    "Rate limited (429). Retrying in %ds (attempt %d/%d)...",
                    wait,
                    attempt + 1,
                    self.max_retries,
                )
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"Upwind API rate limit exceeded after {self.max_retries} retries: "
                    f"{response.text}"
                )

    def _fetch_page_paginated(self, url: str, base_params: dict) -> list:
        """
        Fetch all items from a GET endpoint using 1-based page-number pagination
        (page + per-page query params). Stops when a page returns fewer items
        than the requested page size, or an empty page.

        :param url: The full API endpoint URL.
        :param base_params: Query params to send on every page (time window, per-page, etc).
        :return: List of item dictionaries from all pages.
        """

        token = self._get_access_token()
        headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}

        all_items = []
        page = 1

        while True:
            params = dict(base_params)
            params["page"] = page

            response = self._get_with_retry(url, headers, params)

            if response.status_code != 200:
                raise RuntimeError(
                    f"Upwind API returned status {response.status_code}: {response.text}"
                )

            result = response.json()
            items = result if isinstance(result, list) else result.get("items", result.get("data", []))
            all_items.extend(items)

            logging.info(
                "Page %d: fetched %d items (total so far: %d)",
                page,
                len(items),
                len(all_items),
            )

            if len(items) < self.page_size:
                break
            page += 1

        logging.info("Fetched %d total items from Upwind API.", len(all_items))
        return all_items

    def _fetch_link_header_paginated(self, url: str, base_params: dict) -> list:
        """
        Fetch all items from a GET endpoint that paginates via the standard
        HTTP `Link` response header (rel="next"), e.g. GitHub-style pagination.

        :param url: The full API endpoint URL.
        :param base_params: Query params to send on the first request (e.g. per-page).
        :return: List of item dictionaries from all pages.
        """

        token = self._get_access_token()
        headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}

        all_items = []
        next_url = url
        params = dict(base_params)
        page_number = 0

        while next_url:
            page_number += 1
            response = self._get_with_retry(next_url, headers, params)

            if response.status_code != 200:
                raise RuntimeError(
                    f"Upwind API returned status {response.status_code}: {response.text}"
                )

            result = response.json()
            items = result if isinstance(result, list) else result.get("items", result.get("data", []))
            all_items.extend(items)

            logging.info(
                "Page %d: fetched %d items (total so far: %d)",
                page_number,
                len(items),
                len(all_items),
            )

            next_link = response.links.get("next")
            next_url = next_link["url"] if next_link else None
            params = None  # the next-page URL already carries its own query string

        logging.info("Fetched %d total items from Upwind API.", len(all_items))
        return all_items
