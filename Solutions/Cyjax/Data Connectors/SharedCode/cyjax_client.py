"""This module contains the Cyjax API client for IOC collection and enrichment."""

import inspect
import time
import requests
from SharedCode import consts
from SharedCode.logger import applogger
from SharedCode.exceptions import (
    CyjaxException,
    CyjaxAuthenticationException,
    CyjaxAPIException,
)


class CyjaxClient:
    """Cyjax API client for fetching IOCs and enrichment data.

    This class handles communication with the Cyjax API v2 endpoints
    for indicator of compromise collection and enrichment.
    """

    def __init__(self):
        """Initialize the Cyjax API client with authentication headers."""
        self.base_url = consts.CYJAX_BASE_URL.rstrip("/")
        self.headers = {
            "Authorization": "Bearer {}".format(consts.CYJAX_ACCESS_TOKEN),
            "Content-Type": "application/json",
        }
        self.log_format = consts.LOG_FORMAT

    def get_indicators(self, since, until, page, query=None, indicator_types=None):
        """Fetch IOC indicators from the Cyjax API.

        Args:
            since (str): Start date/time in ISO8601 format.
            until (str): End date/time in ISO8601 format.
            page (int): Page number (1-indexed).
            query (str): Optional free-text search query to filter IOCs (e.g. keyword,
                         threat actor, or campaign name). Pass None or empty string to
                         fetch all IOCs without filtering.
            indicator_types (str): Optional comma-separated indicator types to filter
                                   (e.g., "URL,Domain,IPv4"). Pass None or empty string
                                   to fetch all types.

        Returns:
            list: List of IOC indicator objects.

        Raises:
            CyjaxAuthenticationException: If authentication fails.
            CyjaxAPIException: If API returns an error status code.
            CyjaxException: For unexpected errors.
        """
        __method_name = inspect.currentframe().f_code.co_name
        url = "{}{}".format(self.base_url, consts.CYJAX_IOC_ENDPOINT)
        params = {
            "since": since,
            "until": until,
            "page": page,
            "per-page": consts.CYJAX_PAGE_SIZE,
        }
        if query:
            params["query"] = query
        if indicator_types:
            params["type"] = indicator_types
        return self._make_api_request(url, params, __method_name)

    def get_enrichment(self, ioc_value):
        """Fetch enrichment data for a specific IOC value.

        Uses a dedicated request method that suppresses per-IOC success logs.
        Only failures are logged individually; the caller is responsible for
        logging a batch-level success summary after processing all IOCs.

        Args:
            ioc_value (str): The IOC value to enrich (IP, domain, hash, etc.).

        Returns:
            dict: Enrichment data including GeoIP, ASN, and sightings,
                  or None if no enrichment data is available (404).

        Raises:
            CyjaxAuthenticationException: If authentication fails (401/403).
            CyjaxAPIException: If API returns a non-retryable error.
            CyjaxException: For unexpected errors after retries.
        """
        url = "{}{}".format(self.base_url, consts.CYJAX_ENRICHMENT_ENDPOINT)
        params = {"value": ioc_value}
        return self._make_enrichment_request(url, params, ioc_value)

    def _make_enrichment_request(self, url, params, ioc_value):
        """Make an enrichment API request with enrichment-specific logging.

        Unlike _make_api_request(), this method:
        - Does NOT log each request at INFO level (reduces noise for 100 IOCs/batch)
        - Treats 404 as a valid "no data" response (returns None, no error)
        - Logs only failures (per-IOC) so the caller can build a batch success summary

        Args:
            url (str): The enrichment endpoint URL.
            params (dict): Query parameters (must include 'value').
            ioc_value (str): The IOC value being enriched (used in log messages).

        Returns:
            dict: Parsed enrichment JSON response, or None if 404 (no data).

        Raises:
            CyjaxAuthenticationException: If authentication fails (401/403).
            CyjaxAPIException: If API returns a non-retryable error.
            CyjaxException: For unexpected errors after retries.
        """
        __method_name = inspect.currentframe().f_code.co_name
        retry_count = 0
        while retry_count <= consts.MAX_RETRIES:
            try:
                response = requests.get(
                    url=url,
                    headers=self.headers,
                    params=params,
                    timeout=consts.REQUEST_TIMEOUT,
                )
                if 200 <= response.status_code <= 299:
                    return response.json()
                elif response.status_code == 404:
                    return None
                elif response.status_code == 401:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Enrichment authentication failed (401) for IOC value={}".format(ioc_value),
                        )
                    )
                    raise CyjaxAuthenticationException("Authentication failed: Invalid or expired API token.")
                elif response.status_code == 403:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Enrichment forbidden (403) for IOC value={}".format(ioc_value),
                        )
                    )
                    raise CyjaxAuthenticationException("Forbidden: Insufficient permissions for enrichment endpoint.")
                elif response.status_code in consts.RETRY_STATUS_CODE:
                    if retry_count >= consts.MAX_RETRIES:
                        break
                    retry_count += 1
                    sleep_time = min(
                        consts.MIN_SLEEP_TIME * (consts.BACKOFF_MULTIPLIER**retry_count),
                        consts.MAX_SLEEP_TIME,
                    )
                    if response.status_code == 429:
                        retry_after = response.headers.get("X-Rate-Limit-Reset")
                        if retry_after:
                            sleep_time = int(retry_after)
                    applogger.warning(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Enrichment rate limited ({}), IOC value={}, retry {}/{}, sleeping {} seconds".format(
                                response.status_code,
                                ioc_value,
                                retry_count,
                                consts.MAX_RETRIES,
                                sleep_time,
                            ),
                        )
                    )
                    time.sleep(sleep_time)
                else:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Enrichment unexpected status code ({}), IOC value={}, response: {}".format(
                                response.status_code, ioc_value, response.text
                            ),
                        )
                    )
                    raise CyjaxAPIException(
                        "Enrichment unexpected API error: status code {}".format(response.status_code)
                    )
            except (CyjaxAuthenticationException, CyjaxAPIException):
                raise
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ) as network_err:
                retry_count += 1
                if retry_count > consts.MAX_RETRIES:
                    raise CyjaxException(
                        "Enrichment network error after {} retries for IOC value={}: {}".format(
                            consts.MAX_RETRIES, ioc_value, network_err
                        )
                    )
                sleep_time = min(
                    consts.MIN_SLEEP_TIME * (consts.BACKOFF_MULTIPLIER**retry_count),
                    consts.MAX_SLEEP_TIME,
                )
                error_type = (
                    "connection error" if isinstance(network_err, requests.exceptions.ConnectionError) else "timeout"
                )
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Enrichment {}, IOC value={}, retry {}/{}, sleeping {} seconds: {}".format(
                            error_type,
                            ioc_value,
                            retry_count,
                            consts.MAX_RETRIES,
                            sleep_time,
                            network_err,
                        ),
                    )
                )
                time.sleep(sleep_time)
            except requests.exceptions.RequestException as req_err:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Enrichment request error, IOC value={}: {}".format(ioc_value, req_err),
                    )
                )
                raise CyjaxException("Enrichment request error for IOC value={}: {}".format(ioc_value, req_err))
            except Exception as err:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Enrichment unexpected error, IOC value={}: {}".format(ioc_value, err),
                    )
                )
                raise CyjaxException("Enrichment unexpected error for IOC value={}: {}".format(ioc_value, err))
        applogger.error(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Enrichment max retries ({}) exceeded for IOC value={}".format(consts.MAX_RETRIES, ioc_value),
            )
        )
        raise CyjaxException("Enrichment max retries exceeded for IOC value={}".format(ioc_value))

    def _make_api_request(self, url, params, method_name):
        """Make an API request with retry logic and error handling.

        Args:
            url (str): The API endpoint URL.
            params (dict): Query parameters for the request.
            method_name (str): Name of the calling method for logging.

        Returns:
            dict or list: Parsed JSON response from the API.

        Raises:
            CyjaxAuthenticationException: If authentication fails (401/403).
            CyjaxAPIException: If API returns a non-retryable error.
            CyjaxException: For unexpected errors after retries.
        """
        __method_name = inspect.currentframe().f_code.co_name
        retry_count = 0
        while retry_count <= consts.MAX_RETRIES:
            try:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        method_name,
                        consts.FUNCTION_NAME,
                        "Making API request to {} with params {}".format(url, params),
                    )
                )
                response = requests.get(
                    url=url,
                    headers=self.headers,
                    params=params,
                    timeout=consts.REQUEST_TIMEOUT,
                )
                if 200 <= response.status_code <= 299:
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            method_name,
                            consts.FUNCTION_NAME,
                            "API request successful, status code: {}".format(response.status_code),
                        )
                    )
                    return response.json()
                elif response.status_code == 401:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            method_name,
                            consts.FUNCTION_NAME,
                            "Authentication failed, status code: 401",
                        )
                    )
                    raise CyjaxAuthenticationException("Authentication failed: Invalid or expired API token.")
                elif response.status_code == 403:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            method_name,
                            consts.FUNCTION_NAME,
                            "Forbidden, status code: 403",
                        )
                    )
                    raise CyjaxAuthenticationException("Forbidden: Insufficient permissions for this API endpoint.")
                elif response.status_code in consts.RETRY_STATUS_CODE:
                    if retry_count >= consts.MAX_RETRIES:
                        break
                    sleep_time = min(
                        consts.MIN_SLEEP_TIME * (consts.BACKOFF_MULTIPLIER ** (retry_count + 1)),
                        consts.MAX_SLEEP_TIME,
                    )
                    if response.status_code == 429:
                        retry_after = response.headers.get("X-Rate-Limit-Reset")
                        if retry_after:
                            sleep_time = int(retry_after)
                    applogger.warning(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            method_name,
                            consts.FUNCTION_NAME,
                            "Retryable error, status code: {}, retry {}/{}, sleeping {} seconds".format(
                                response.status_code,
                                retry_count + 1,
                                consts.MAX_RETRIES,
                                sleep_time,
                            ),
                        )
                    )
                    time.sleep(sleep_time)
                    retry_count += 1
                else:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            method_name,
                            consts.FUNCTION_NAME,
                            "Unexpected status code: {}, response: {}".format(response.status_code, response.text),
                        )
                    )
                    raise CyjaxAPIException("Unexpected API error: status code {}".format(response.status_code))
            except (CyjaxAuthenticationException, CyjaxAPIException):
                raise
            except requests.exceptions.ConnectionError as conn_err:
                retry_count += 1
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        consts.CONNECTION_ERROR_MSG.format(conn_err),
                    )
                )
                if retry_count > consts.MAX_RETRIES:
                    raise CyjaxException("Connection error after {} retries: {}".format(consts.MAX_RETRIES, conn_err))
                sleep_time = min(
                    consts.MIN_SLEEP_TIME * (consts.BACKOFF_MULTIPLIER**retry_count),
                    consts.MAX_SLEEP_TIME,
                )
                time.sleep(sleep_time)
            except requests.exceptions.Timeout as timeout_err:
                retry_count += 1
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        consts.TIME_OUT_ERROR_MSG.format(timeout_err),
                    )
                )
                if retry_count > consts.MAX_RETRIES:
                    raise CyjaxException("Timeout error after {} retries: {}".format(consts.MAX_RETRIES, timeout_err))
                sleep_time = min(
                    consts.MIN_SLEEP_TIME * (consts.BACKOFF_MULTIPLIER**retry_count),
                    consts.MAX_SLEEP_TIME,
                )
                time.sleep(sleep_time)
            except requests.exceptions.RequestException as req_err:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        consts.REQUEST_ERROR_MSG.format(req_err),
                    )
                )
                raise CyjaxException("Request error: {}".format(req_err))
            except Exception as err:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        consts.UNEXPECTED_ERROR_MSG.format(err),
                    )
                )
                raise CyjaxException("Unexpected error: {}".format(err))
        applogger.error(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                method_name,
                consts.FUNCTION_NAME,
                "Max retries ({}) exceeded for API request".format(consts.MAX_RETRIES),
            )
        )
        raise CyjaxException("Max retries exceeded for API request to {}".format(url))
