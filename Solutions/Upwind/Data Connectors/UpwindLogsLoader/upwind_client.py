"""Base Upwind API client with authentication, retry, and pagination."""

import logging
import time

import requests


class UpwindClient:
    """Base client for the Upwind API with authentication, retry, and pagination."""

    _RETRYABLE_STATUS_CODES = {429, 502, 503, 504}

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

        logging.debug("Requesting Upwind API access token...")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "audience": self.api_base_url,
        }

        response = requests.post(self.auth_url, json=payload, timeout=30)
        response.raise_for_status()

        self._access_token = response.json()["access_token"]
        logging.debug("Upwind API access token obtained.")
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

            logging.debug(
                "Page %d: fetched %d items (total so far: %d)",
                page_number,
                len(items),
                len(all_items),
            )

            metadata = result.get("metadata", {})
            cursor = metadata.get("next_cursor")
            if not cursor:
                break

        logging.debug("Fetched %d total items from Upwind API.", len(all_items))
        return all_items

    def _request_with_retry(self, url, headers, json_body, params) -> requests.Response:
        """Execute a POST request with exponential backoff on retryable errors."""

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    url, json=json_body, headers=headers, params=params, timeout=60
                )

                if response.status_code not in self._RETRYABLE_STATUS_CODES:
                    return response

                if attempt < self.max_retries:
                    wait = min(
                        self.initial_backoff_seconds * (2**attempt),
                        self.max_backoff_seconds,
                    )
                    logging.warning(
                        "Retryable status %d. Retrying in %ds (attempt %d/%d)...",
                        response.status_code,
                        wait,
                        attempt + 1,
                        self.max_retries,
                    )
                    time.sleep(wait)
                else:
                    raise RuntimeError(
                        f"Upwind API request failed after {self.max_retries} retries "
                        f"(status {response.status_code}): {response.text}"
                    )

            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt < self.max_retries:
                    wait = min(
                        self.initial_backoff_seconds * (2**attempt),
                        self.max_backoff_seconds,
                    )
                    logging.warning(
                        "%s. Retrying in %ds (attempt %d/%d)...",
                        type(e).__name__,
                        wait,
                        attempt + 1,
                        self.max_retries,
                    )
                    time.sleep(wait)
                else:
                    raise RuntimeError(
                        f"Upwind API request failed after {self.max_retries} retries: {e}"
                    ) from e
