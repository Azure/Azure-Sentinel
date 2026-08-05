"""GTI API client for Google Threat Intelligence connector.

Handles token exchange, token caching (in KeyVault), and alert pagination.
"""

import inspect
import json
import time
import requests
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError as RequestsConnectionError

from SharedCode.logger import applogger
from SharedCode import consts
from SharedCode.exceptions import GTIRelevanceSystemAlertsException, GTIRelevanceSystemAlertsAuthException

GTI_TOKEN_SECRET_NAME = "gti-access-token"


def _backoff_sleep(attempt: int) -> float:
    """Return exponential backoff delay for the given 1-based attempt number."""
    return min(consts.MIN_SLEEP_TIME * (consts.BACKOFF_MULTIPLIER ** (attempt - 1)), consts.MAX_SLEEP_TIME)


class GTIClient:
    """Google Threat Intelligence API client.

    Manages Bearer token lifecycle (exchange, KeyVault caching, and refresh)
    and provides paginated access to GTI alerts.
    """

    def __init__(self):
        """Initialize the GTI client with empty token state."""
        self._access_token = None
        self._token_expiry = 0

    def _is_token_expired(self):
        """Check whether the current access token is expired or near expiry.

        Returns:
            bool: True if token should be refreshed, False if still valid.
        """
        return time.time() >= (self._token_expiry - consts.TOKEN_EXPIRY_BUFFER_SECONDS)

    def _get_headers(self):
        """Build request headers using the current access token."""
        return {
            "Authorization": "Bearer {}".format(self._access_token),
            "x-goog-user-project": consts.GTI_PROJECT_ID,
            "Content-Type": "application/json",
            "User-Agent": "Azure-Sentinel-GTIRelevanceSystemAlerts/1.0.0",
        }

    def _load_token_from_keyvault(self):
        """Attempt to load a cached access token from Azure Key Vault.

        Populates self._access_token and self._token_expiry if a valid,
        non-expired token is found.  Silently ignores all errors so that
        a missing or misconfigured vault does not block execution.
        """
        if not consts.KEYVAULT_NAME:
            return
        try:
            from SharedCode.keyvault_secrets_management import KeyVaultSecretManage
            kv = KeyVaultSecretManage()
            token_data_str = kv.get_keyvault_secret(GTI_TOKEN_SECRET_NAME)
            if token_data_str:
                token_data = json.loads(token_data_str)
                self._access_token = token_data.get("access_token")
                self._token_expiry = float(token_data.get("expires_at", 0))
                applogger.info(
                    consts.LOG_FORMAT.format(
                        consts.LOGS_STARTS_WITH, "_load_token_from_keyvault", "GTIClient",
                        "Loaded cached token from KeyVault, expires_at={}".format(self._token_expiry),
                    )
                )
        except Exception as err:
            applogger.warning(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, "_load_token_from_keyvault", "GTIClient",
                    "Could not load token from KeyVault (will re-exchange): {}".format(err),
                )
            )
            self._access_token = None
            self._token_expiry = 0

    def _save_token_to_keyvault(self):
        """Persist the current access token to Azure Key Vault for reuse across invocations.

        Silently ignores all errors so that a missing vault does not break ingestion.
        """
        if not consts.KEYVAULT_NAME:
            return
        try:
            from SharedCode.keyvault_secrets_management import KeyVaultSecretManage
            kv = KeyVaultSecretManage()
            token_data = json.dumps({"access_token": self._access_token, "expires_at": self._token_expiry})
            kv.set_keyvault_secret(GTI_TOKEN_SECRET_NAME, token_data)
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, "_save_token_to_keyvault", "GTIClient",
                    "Stored access token in KeyVault.",
                )
            )
        except Exception as err:
            applogger.warning(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, "_save_token_to_keyvault", "GTIClient",
                    "Could not store token in KeyVault (non-fatal): {}".format(err),
                )
            )

    def _handle_token_exchange_response(self, response, method_name: str) -> bool:
        """Process a token exchange HTTP response.

        Returns:
            bool: True if the token was successfully obtained and cached.
                  False if the response has a retryable status code.

        Raises:
            GTIRelevanceSystemAlertsAuthException: For 401/403 or missing access_token.
            GTIRelevanceSystemAlertsException: For unexpected status codes.
        """
        if response.status_code == 200:
            response_json = response.json()
            self._access_token = response_json.get("access_token")
            if not self._access_token:
                raise GTIRelevanceSystemAlertsAuthException(
                    "Token exchange response missing 'access_token' field"
                )
            expires_in = response_json.get("expires_in", 3600)
            self._token_expiry = time.time() + expires_in
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    "Successfully obtained GTI Bearer token, expires_in={}s".format(expires_in),
                )
            )
            self._save_token_to_keyvault()
            return True

        if response.status_code in (401, 403):
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    "Token exchange returned {} - invalid GTI API key or project. Response: {}".format(
                        response.status_code, response.text
                    ),
                )
            )
            raise GTIRelevanceSystemAlertsAuthException(
                "GTI token exchange returned {}: {}".format(response.status_code, response.text)
            )

        if response.status_code in consts.RETRY_STATUS_CODE:
            return False

        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                "Token exchange unexpected status {}: {}".format(response.status_code, response.text),
            )
        )
        raise GTIRelevanceSystemAlertsAuthException(
            "GTI token exchange failed with status {}: {}".format(response.status_code, response.text)
        )

    def _handle_token_exchange_attempt_errors(self, error, attempt: int, method_name: str):
        """Handle per-attempt exceptions during token exchange.

        Re-raises non-retryable errors immediately; applies backoff sleep for
        connection errors that still have remaining retries.

        Args:
            error: The caught exception.
            attempt (int): Current 1-based attempt number.
            method_name (str): Caller method name for log context.

        Raises:
            GTIRelevanceSystemAlertsException: Always — either wrapping the error or
                propagating a max-retries exceeded message.
        """
        if isinstance(error, requests.exceptions.Timeout):
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    consts.TIME_OUT_ERROR_MSG.format(error),
                )
            )
            raise GTIRelevanceSystemAlertsException("Timeout during GTI token exchange: {}".format(error))
        if isinstance(error, RequestsConnectionError):
            if attempt < consts.MAX_RETRIES:
                sleep_time = _backoff_sleep(attempt)
                applogger.warning(
                    consts.LOG_FORMAT.format(
                        consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                        "Connection error, retrying in {}s (attempt {}/{}): {}".format(
                            sleep_time, attempt, consts.MAX_RETRIES, error
                        ),
                    )
                )
                time.sleep(sleep_time)
                return
            raise GTIRelevanceSystemAlertsException(
                "Connection error after {} retries during token exchange: {}".format(consts.MAX_RETRIES, error)
            )
        if isinstance(error, JSONDecodeError):
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    consts.JSON_DECODE_ERROR_MSG.format(error),
                )
            )
            raise GTIRelevanceSystemAlertsException("JSON decode error during GTI token exchange: {}".format(error))
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                consts.UNEXPECTED_ERROR_MSG.format(error),
            )
        )
        raise GTIRelevanceSystemAlertsException("Unexpected error during GTI token exchange: {}".format(error))

    def _exchange_api_key(self):
        """Exchange GTI API key for a Bearer access token with exponential backoff retry.

        Calls the GTI IdP token exchange endpoint, caches the resulting token
        in memory and in Azure Key Vault for reuse across function invocations.

        Raises:
            GTIRelevanceSystemAlertsAuthException: If token exchange fails with 401/403 or
                max retries are exceeded for retryable status codes.
            GTIRelevanceSystemAlertsException: For unexpected errors during token exchange.
        """
        __method_name = inspect.currentframe().f_code.co_name
        payload = json.dumps({"api_key": consts.GTI_API_KEY})

        for attempt in range(1, consts.MAX_RETRIES + 1):
            try:
                applogger.info(
                    consts.LOG_FORMAT.format(
                        consts.LOGS_STARTS_WITH, __method_name, "GTIClient",
                        "Exchanging GTI API key for Bearer token (attempt {}/{})".format(attempt, consts.MAX_RETRIES),
                    )
                )
                response = requests.request(
                    method="POST",
                    url=consts.GTI_TOKEN_EXCHANGE_URL,
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Azure-Sentinel-GTIRelevanceSystemAlerts/1.0.0",
                    },
                    timeout=consts.MAX_TIMEOUT_SENTINEL,
                )

                success = self._handle_token_exchange_response(response, __method_name)
                if success:
                    return

                # Retryable status code path
                if attempt < consts.MAX_RETRIES:
                    sleep_time = _backoff_sleep(attempt)
                    applogger.warning(
                        consts.LOG_FORMAT.format(
                            consts.LOGS_STARTS_WITH, __method_name, "GTIClient",
                            "Token exchange retryable status {} - retrying in {}s (attempt {}/{})".format(
                                response.status_code, sleep_time, attempt, consts.MAX_RETRIES
                            ),
                        )
                    )
                    time.sleep(sleep_time)
                    continue
                raise GTIRelevanceSystemAlertsException(
                    "Max retries exceeded for token exchange, last status: {}".format(response.status_code)
                )

            except (GTIRelevanceSystemAlertsAuthException, GTIRelevanceSystemAlertsException):
                raise
            except Exception as error:
                self._handle_token_exchange_attempt_errors(error, attempt, __method_name)

    def ensure_authenticated(self):
        """Ensure a valid Bearer token is available, using KeyVault cache then exchange if needed.

        Load order:
        1. In-memory token (set during this invocation).
        2. KeyVault cached token (persisted from a previous invocation).
        3. Fresh token exchange via GTI IdP.

        Raises:
            GTIRelevanceSystemAlertsAuthException: If token exchange fails.
            GTIRelevanceSystemAlertsException: For unexpected errors.
        """
        __method_name = inspect.currentframe().f_code.co_name
        if self._access_token is None or self._is_token_expired():
            # Try KeyVault cache first before doing a full exchange
            self._load_token_from_keyvault()

        if self._access_token is None or self._is_token_expired():
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, __method_name, "GTIClient",
                    "Token is missing or expired, performing token exchange",
                )
            )
            self._exchange_api_key()

    def _handle_response(self, response, method_name):
        """Interpret an HTTP response, returning parsed JSON or raising for non-retryable errors.

        Returns:
            dict: Parsed JSON on HTTP 200.
            requests.Response: Returned as-is for retryable status codes (caller retries).

        Raises:
            GTIRelevanceSystemAlertsException: For 400, 403, and unexpected status codes.
        """
        if response.status_code == 200:
            response_json = response.json()
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    "Received {} alerts".format(len(response_json.get("alerts", []))),
                )
            )
            return response_json

        if response.status_code == 400:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    "Bad Request (400): filter syntax error. Response: {}".format(response.text),
                )
            )
            raise GTIRelevanceSystemAlertsException("GTI API returned 400 Bad Request: {}".format(response.text))

        if response.status_code == 403:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    "Forbidden (403): wrong project ID or inactive GTI subscription. Response: {}".format(response.text),
                )
            )
            raise GTIRelevanceSystemAlertsException("GTI API returned 403 Forbidden: {}".format(response.text))

        if response.status_code in consts.RETRY_STATUS_CODE:
            applogger.warning(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    "Retryable status code {}.".format(response.status_code),
                )
            )
            return response

        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                "Unexpected status code {}: {}".format(response.status_code, response.text),
            )
        )
        raise GTIRelevanceSystemAlertsException(
            "GTI API returned unexpected status {}: {}".format(response.status_code, response.text)
        )

    def _refresh_token_on_401(self, response, url: str, params: dict, method_name: str):
        """Refresh the access token on a 401 response and retry the request once.

        Args:
            response: The original HTTP response object with status 401.
            url (str): Request URL to retry after token refresh.
            params (dict): Query parameters to include in the retry request.
            method_name (str): Caller method name for log context.

        Returns:
            requests.Response: The response from the retried request.
        """
        applogger.warning(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                "Unauthorized (401): refreshing token and retrying.",
            )
        )
        self._access_token = None
        self._token_expiry = 0
        self.ensure_authenticated()
        return requests.get(
            url=url,
            headers=self._get_headers(),
            params=params,
            timeout=consts.MAX_TIMEOUT_SENTINEL,
        )

    def _handle_alerts_attempt_errors(self, error, attempt: int, method_name: str):
        """Handle per-attempt exceptions during the alerts API call.

        Re-raises non-retryable errors immediately; applies backoff sleep for
        connection errors that still have remaining retries.

        Args:
            error: The caught exception.
            attempt (int): Current 1-based attempt number.
            method_name (str): Caller method name for log context.

        Raises:
            GTIRelevanceSystemAlertsException: Always — either wrapping the error or
                propagating a max-retries exceeded message.
        """
        if isinstance(error, requests.exceptions.Timeout):
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    consts.TIME_OUT_ERROR_MSG.format(error),
                )
            )
            raise GTIRelevanceSystemAlertsException("Timeout during GTI alerts API call: {}".format(error))
        if isinstance(error, RequestsConnectionError):
            if attempt < consts.MAX_RETRIES:
                sleep_time = _backoff_sleep(attempt)
                applogger.warning(
                    consts.LOG_FORMAT.format(
                        consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                        "Connection error, retrying in {}s (attempt {}/{}): {}".format(
                            sleep_time, attempt, consts.MAX_RETRIES, error
                        ),
                    )
                )
                time.sleep(sleep_time)
                return
            raise GTIRelevanceSystemAlertsException(
                "Connection error after {} retries during GTI alerts API call: {}".format(consts.MAX_RETRIES, error)
            )
        if isinstance(error, JSONDecodeError):
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                    consts.JSON_DECODE_ERROR_MSG.format(error),
                )
            )
            raise GTIRelevanceSystemAlertsException(
                "JSON decode error during GTI alerts API call: {}".format(error)
            )
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH, method_name, "GTIClient",
                consts.UNEXPECTED_ERROR_MSG.format(error),
            )
        )
        raise GTIRelevanceSystemAlertsException(
            "Unexpected error during GTI alerts API call: {}".format(error)
        )

    def list_alerts(self, filter_expr=None, page_token=None):
        """Fetch one page of GTI alerts with exponential backoff retry.

        Args:
            filter_expr (str, optional): GTI API filter expression.
            page_token (str, optional): Continuation token from the previous page.

        Returns:
            dict: JSON response with 'alerts' list and optional 'nextPageToken'.

        Raises:
            GTIRelevanceSystemAlertsException: For non-retryable API errors or max retries exceeded.
            GTIRelevanceSystemAlertsAuthException: If authentication fails.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.ensure_authenticated()

            url = "{}/{}/projects/{}/alerts".format(
                consts.GTI_BASE_URL, consts.GTI_API_VERSION, consts.GTI_PROJECT_ID
            )
            params = {
                "pageSize": consts.PAGE_SIZE,
                "orderBy": "audit.update_time asc",
            }
            if filter_expr:
                params["filter"] = filter_expr
            if page_token:
                params["pageToken"] = page_token

            for attempt in range(1, consts.MAX_RETRIES + 1):
                try:
                    applogger.info(
                        consts.LOG_FORMAT.format(
                            consts.LOGS_STARTS_WITH, __method_name, "GTIClient",
                            "Calling GTI alerts API (attempt {}/{}), page_token_present={}".format(
                                attempt, consts.MAX_RETRIES, bool(page_token)
                            ),
                        )
                    )
                    response = requests.get(
                        url=url,
                        headers=self._get_headers(),
                        params=params,
                        timeout=consts.MAX_TIMEOUT_SENTINEL,
                    )

                    if response.status_code == 401:
                        response = self._refresh_token_on_401(response, url, params, __method_name)

                    result = self._handle_response(response, __method_name)

                    # _handle_response returns a dict on 200, raises on 400/403/unexpected,
                    # and returns the Response object for retryable status codes (429, 500, etc.).
                    if isinstance(result, dict):
                        return result

                    # result is a Response with a retryable status code — apply backoff and retry.
                    retryable_status = result.status_code
                    if attempt < consts.MAX_RETRIES:
                        sleep_time = _backoff_sleep(attempt)
                        applogger.warning(
                            consts.LOG_FORMAT.format(
                                consts.LOGS_STARTS_WITH, __method_name, "GTIClient",
                                "Status {} - retrying in {}s (attempt {}/{})".format(
                                    retryable_status, sleep_time, attempt, consts.MAX_RETRIES
                                ),
                            )
                        )
                        time.sleep(sleep_time)
                        continue
                    raise GTIRelevanceSystemAlertsException(
                        "Max retries exceeded for GTI alerts API, last status: {}".format(retryable_status)
                    )

                except (GTIRelevanceSystemAlertsException, GTIRelevanceSystemAlertsAuthException):
                    raise
                except Exception as error:
                    self._handle_alerts_attempt_errors(error, attempt, __method_name)

        except (GTIRelevanceSystemAlertsException, GTIRelevanceSystemAlertsAuthException):
            raise
        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH, __method_name, "GTIClient",
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise GTIRelevanceSystemAlertsException("Unexpected error during GTI alerts API call: {}".format(error))
