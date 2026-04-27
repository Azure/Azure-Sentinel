"""
Lumen Threat Feed Connector V2 - Simplified paginated API approach.

This module provides core classes for Microsoft Sentinel integration:
- MSALSetup: Microsoft Authentication Library configuration
- SentinelUploader: Handles Sentinel TI API uploads with retry logic
- LumenClientV2: Handles Lumen API communication with retry logic

V2 Architecture:
- Single timer-triggered function (no Durable Functions)
- Paginated Lumen API (no blob staging)
- Direct page-by-page processing and upload to Sentinel
- Robust retry logic for enterprise resilience

Environment Variables Required:
- TENANT_ID: Azure tenant ID
- CLIENT_ID: Azure app registration client ID
- CLIENT_SECRET: Azure app registration client secret
- WORKSPACE_ID: Sentinel workspace ID
"""

import base64
import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Iterator, List, Optional, TypeVar

import requests
from msal import ConfidentialClientApplication

# Constants
CHUNK_SIZE = 100  # Sentinel API batch limit
DEFAULT_CONFIDENCE_THRESHOLD = 60
POLL_INTERVAL = 5  # Seconds between status polls
POLL_TIMEOUT = 300  # Max seconds to wait for query completion
MAX_PAGES = 1000  # Safeguard against infinite pagination

# Retry configuration
DEFAULT_MAX_RETRIES = 5
DEFAULT_BASE_DELAY = 1.0  # seconds
DEFAULT_MAX_DELAY = 60.0  # seconds

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    retryable_exceptions: tuple = (requests.exceptions.RequestException,),
    retryable_status_codes: tuple = (429, 500, 502, 503, 504),
) -> Callable:
    """Decorator that adds exponential backoff retry logic to a function.

    Retries on specified exceptions and HTTP status codes with exponential
    backoff. Useful for handling transient network failures and rate limiting.

    Args:
        max_retries: Maximum number of retry attempts (default: 5)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay cap in seconds (default: 60.0)
        retryable_exceptions: Tuple of exception types to retry on
        retryable_status_codes: HTTP status codes that trigger a retry

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)

                    # Check if result is a Response object with retryable status
                    if isinstance(result, requests.Response):
                        if result.status_code in retryable_status_codes:
                            if attempt < max_retries:
                                delay = _calculate_delay(
                                    attempt, base_delay, max_delay, result
                                )
                                logger.warning(
                                    "%s returned HTTP %d on attempt %d/%d, "
                                    "retrying in %.1fs",
                                    func.__name__, result.status_code,
                                    attempt + 1, max_retries + 1, delay
                                )
                                time.sleep(delay)
                                continue
                            else:
                                # Max retries exhausted, let caller handle
                                result.raise_for_status()

                    return result

                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = _calculate_delay(attempt, base_delay, max_delay)
                        logger.warning(
                            "%s failed on attempt %d/%d with %s: %s, "
                            "retrying in %.1fs",
                            func.__name__, attempt + 1, max_retries + 1,
                            type(e).__name__, str(e), delay
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            func.__name__, max_retries + 1, str(e)
                        )
                        raise

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            return result

        return wrapper
    return decorator


def _calculate_delay(
    attempt: int,
    base_delay: float,
    max_delay: float,
    response: Optional[requests.Response] = None
) -> float:
    """Calculate delay for retry attempt with optional Retry-After header.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap
        response: Optional response object to check for Retry-After header

    Returns:
        float: Delay in seconds
    """
    # Check for Retry-After header
    if response is not None:
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return min(float(retry_after), max_delay)
            except ValueError:
                pass  # Fall through to exponential backoff

    # Exponential backoff with jitter
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)


def chunks(lst: List, n: int) -> Iterator[List]:
    """Yield successive n-sized chunks from lst.

    Args:
        lst: List to split into chunks
        n: Maximum size of each chunk

    Yields:
        List chunks of size n or smaller (for the final chunk)
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class MSALSetup:
    """Microsoft Authentication Library configuration for Sentinel API access.

    Handles MSAL ConfidentialClientApplication setup for client credentials flow.

    Attributes:
        tenant_id: Azure AD tenant ID
        client_id: Application (client) ID from Azure app registration
        client_secret: Client secret for the app registration
        workspace_id: Microsoft Sentinel workspace ID
        authority: Azure AD authority URL
        scope: OAuth2 scope for Sentinel API
        app: MSAL ConfidentialClientApplication instance
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, workspace_id: str):
        """Initialize MSAL configuration.

        Args:
            tenant_id: Azure AD tenant ID
            client_id: Application (client) ID from Azure app registration
            client_secret: Client secret for the app registration
            workspace_id: Microsoft Sentinel workspace ID

        Raises:
            ValueError: If any required parameter is empty or None
        """
        # Validate required parameters
        required_params = {
            'TENANT_ID': tenant_id,
            'CLIENT_ID': client_id,
            'CLIENT_SECRET': client_secret,
            'WORKSPACE_ID': workspace_id
        }

        for param_name, value in required_params.items():
            if not value:
                raise ValueError(f"{param_name} is required but was not provided")

        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.workspace_id = workspace_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://management.azure.com/.default"]

        # Create MSAL ConfidentialClientApplication
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )

        logger.info("MSALSetup initialized for workspace %s", self.workspace_id)


class SentinelUploader:
    """Handles Sentinel Threat Intelligence API uploads with retry logic.

    Uploads STIX indicators to Microsoft Sentinel using the TI API.
    Implements exponential backoff for rate limiting (HTTP 429) and
    transient failures.

    Attributes:
        msal_setup: MSALSetup instance for authentication
        access_token: Cached access token
        token_expiry: Token expiration timestamp
        session: Requests session for connection pooling
    """

    # Sentinel TI API endpoint template
    UPLOAD_URL_TEMPLATE = (
        "https://api.ti.sentinel.azure.com/workspaces/{workspace_id}/"
        "threat-intelligence-stix-objects:upload"
    )
    API_VERSION = "2024-02-01-preview"

    def __init__(self, msal_setup: MSALSetup):
        """Initialize SentinelUploader with MSAL configuration.

        Args:
            msal_setup: MSALSetup instance containing authentication config
        """
        self.msal_setup = msal_setup
        self.access_token = None
        self.token_expiry = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LumenSentinelConnectorV2/2.0',
            'Content-Type': 'application/json'
        })

        logger.info("SentinelUploader initialized")

    def _get_access_token(self, force_refresh: bool = False) -> str:
        """Acquire or return cached access token using MSAL client credentials flow.

        Implements retry logic for transient AAD failures. Tokens are cached
        for 50 minutes (typical token lifetime is 60 minutes).

        Args:
            force_refresh: If True, ignore cached token and acquire new one

        Returns:
            str: Valid access token for Sentinel API

        Raises:
            Exception: If token acquisition fails after all retries
        """
        now = datetime.utcnow()

        # Return cached token if still valid (unless force refresh)
        if not force_refresh and self.access_token and self.token_expiry and now < self.token_expiry:
            logger.debug("Using cached access token (expires in %s)",
                        self.token_expiry - now)
            return self.access_token

        logger.info("Acquiring new access token via MSAL client credentials flow")

        # Retry token acquisition with exponential backoff
        max_retries = DEFAULT_MAX_RETRIES
        base_delay = DEFAULT_BASE_DELAY
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                result = self.msal_setup.app.acquire_token_for_client(
                    scopes=self.msal_setup.scope
                )

                if "access_token" in result:
                    self.access_token = result["access_token"]
                    # Cache token for 50 minutes (buffer before 60-minute expiry)
                    self.token_expiry = now + timedelta(minutes=50)
                    logger.info("Access token acquired successfully")
                    return self.access_token
                else:
                    error_msg = result.get("error_description", result.get("error", "Unknown error"))
                    last_error = f"Token acquisition failed: {error_msg}"

                    # Check if error is retryable (transient)
                    error_code = result.get("error", "")
                    retryable_errors = [
                        "temporarily_unavailable",
                        "service_unavailable",
                        "connection_error"
                    ]

                    if any(err in error_code.lower() for err in retryable_errors):
                        if attempt < max_retries:
                            delay = min(base_delay * (2 ** attempt), DEFAULT_MAX_DELAY)
                            logger.warning(
                                "Token acquisition failed on attempt %d/%d: %s, "
                                "retrying in %.1fs",
                                attempt + 1, max_retries + 1, error_msg, delay
                            )
                            time.sleep(delay)
                            continue

                    # Non-retryable error or max retries exceeded
                    logger.error("Failed to acquire access token: %s", error_msg)
                    raise Exception(f"Failed to acquire access token: {error_msg}")

            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    delay = min(base_delay * (2 ** attempt), DEFAULT_MAX_DELAY)
                    logger.warning(
                        "Token acquisition error on attempt %d/%d: %s, "
                        "retrying in %.1fs",
                        attempt + 1, max_retries + 1, str(e), delay
                    )
                    time.sleep(delay)
                else:
                    logger.error("Token acquisition failed after %d attempts: %s",
                               max_retries + 1, str(e))
                    raise

        raise Exception(f"Failed to acquire access token after {max_retries + 1} attempts: {last_error}")

    def upload_indicators(self, stix_objects: list) -> dict:
        """Upload STIX indicators to Microsoft Sentinel.

        Uploads indicators in batches of CHUNK_SIZE (100) to comply with
        Sentinel API limits. Implements exponential backoff for rate limiting
        and automatic token refresh on 401 errors.

        Args:
            stix_objects: List of STIX indicator objects to upload

        Returns:
            dict: Upload results containing:
                - uploaded_count: Number of successfully uploaded indicators
                - error_count: Number of failed indicators
                - rate_limit_events: Number of 429 responses encountered
                - success: Overall success status (True if no errors)
        """
        if not stix_objects:
            logger.info("No indicators to upload")
            return {
                'uploaded_count': 0,
                'error_count': 0,
                'rate_limit_events': 0,
                'success': True
            }

        # Get access token
        access_token = self._get_access_token()

        # Prepare upload URL
        upload_url = self.UPLOAD_URL_TEMPLATE.format(
            workspace_id=self.msal_setup.workspace_id
        )

        params = {'api-version': self.API_VERSION}

        # Statistics
        uploaded_count = 0
        error_count = 0
        rate_limit_events = 0

        # Process in chunks
        indicator_chunks = list(chunks(stix_objects, CHUNK_SIZE))
        total_chunks = len(indicator_chunks)

        logger.info("Uploading %d indicators in %d batches",
                   len(stix_objects), total_chunks)

        for chunk_num, chunk in enumerate(indicator_chunks, 1):
            payload = {
                'sourcesystem': 'Lumen',
                'stixobjects': chunk
            }

            # Retry configuration
            max_retries = 6
            base_delay = 1.0
            token_refreshed = False

            for attempt in range(max_retries):
                try:
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }

                    logger.info("Uploading batch %d/%d (%d indicators, attempt %d)",
                               chunk_num, total_chunks, len(chunk), attempt + 1)

                    response = self.session.post(
                        upload_url,
                        json=payload,
                        headers=headers,
                        params=params,
                        timeout=60
                    )

                    if response.status_code == 200:
                        uploaded_count += len(chunk)
                        logger.info("Batch %d/%d uploaded successfully (%d indicators)",
                                   chunk_num, total_chunks, len(chunk))
                        break

                    elif response.status_code == 401 and not token_refreshed:
                        # Token expired, refresh and retry
                        logger.warning("Received 401, refreshing access token")
                        access_token = self._get_access_token(force_refresh=True)
                        token_refreshed = True
                        continue

                    elif response.status_code == 429:
                        # Rate limiting - apply exponential backoff
                        rate_limit_events += 1

                        if attempt < max_retries - 1:
                            delay = _calculate_delay(attempt, base_delay, DEFAULT_MAX_DELAY, response)
                            logger.warning(
                                "Rate limited on batch %d/%d (attempt %d), "
                                "retrying in %.1fs",
                                chunk_num, total_chunks, attempt + 1, delay
                            )
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(
                                "Batch %d/%d failed after %d rate limit retries",
                                chunk_num, total_chunks, max_retries
                            )
                            error_count += len(chunk)
                            break

                    elif response.status_code in (500, 502, 503, 504):
                        # Server error - retry with backoff
                        if attempt < max_retries - 1:
                            delay = min(base_delay * (2 ** attempt), DEFAULT_MAX_DELAY)
                            logger.warning(
                                "Server error %d on batch %d/%d (attempt %d), "
                                "retrying in %.1fs",
                                response.status_code, chunk_num, total_chunks,
                                attempt + 1, delay
                            )
                            time.sleep(delay)
                            continue
                        else:
                            error_text = response.text[:500] if response.text else "No response body"
                            logger.error(
                                "Batch %d/%d failed with HTTP %d after %d retries: %s",
                                chunk_num, total_chunks, response.status_code,
                                max_retries, error_text
                            )
                            error_count += len(chunk)
                            break
                    else:
                        # Other HTTP errors - don't retry
                        error_text = response.text[:500] if response.text else "No response body"
                        logger.error(
                            "Batch %d/%d failed with HTTP %d: %s",
                            chunk_num, total_chunks, response.status_code, error_text
                        )
                        error_count += len(chunk)
                        break

                except requests.exceptions.RequestException as e:
                    logger.error(
                        "Batch %d/%d network error on attempt %d: %s",
                        chunk_num, total_chunks, attempt + 1, str(e)
                    )
                    if attempt == max_retries - 1:
                        error_count += len(chunk)
                    else:
                        delay = min(base_delay * (2 ** attempt), DEFAULT_MAX_DELAY)
                        time.sleep(delay)

        # Log summary
        success = error_count == 0
        logger.info(
            "Upload complete: %d uploaded, %d errors, %d rate limit events",
            uploaded_count, error_count, rate_limit_events
        )

        return {
            'uploaded_count': uploaded_count,
            'error_count': error_count,
            'rate_limit_events': rate_limit_events,
            'success': success
        }


class LumenAPIError(Exception):
    """Custom exception for Lumen API errors."""
    pass


class LumenClientV2:
    """V2 Lumen API client using paginated endpoints with retry logic.

    Handles communication with the Lumen Threat Feed API v2 for retrieving
    threat intelligence data using a paginated query flow:
    1. Initiate query -> get cache_id
    2. Poll status -> get token_id when completed
    3. Retrieve pages -> iterate through paginated results

    All API calls include retry logic with exponential backoff for resilience
    against transient network failures.

    Attributes:
        api_key: Lumen API key for authentication
        base_url: Base URL for Lumen API endpoints
        session: Requests session with pre-configured headers
        max_retries: Maximum retry attempts for API calls
    """

    def __init__(self, api_key: str, base_url: str, max_retries: int = DEFAULT_MAX_RETRIES):
        """Initialize LumenClientV2 with API credentials.

        Args:
            api_key: Lumen API key for authentication
            base_url: Base URL for Lumen API (trailing slash will be stripped)
            max_retries: Maximum retry attempts for transient failures
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LumenSentinelConnectorV2/2.0'
        })

        logger.info("LumenClientV2 initialized for %s", self.base_url)

    def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments passed to requests

        Returns:
            requests.Response: Successful response

        Raises:
            requests.exceptions.HTTPError: If request fails after all retries
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Check for retryable status codes
                if response.status_code in (429, 500, 502, 503, 504):
                    if attempt < self.max_retries:
                        delay = _calculate_delay(
                            attempt, DEFAULT_BASE_DELAY, DEFAULT_MAX_DELAY, response
                        )
                        logger.warning(
                            "Request to %s returned HTTP %d on attempt %d/%d, "
                            "retrying in %.1fs",
                            url, response.status_code,
                            attempt + 1, self.max_retries + 1, delay
                        )
                        time.sleep(delay)
                        continue

                # Raise for other error status codes
                if response.status_code >= 400:
                    # Log response body for debugging before raising
                    error_body = response.text[:1000] if response.text else "No response body"
                    logger.warning(
                        "HTTP %d error from %s - Response body: %s",
                        response.status_code, url, error_body
                    )
                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                # Don't retry client errors (4xx) except 429 (rate limit)
                # These are handled in the status_code checks above, so if we get here
                # it's a non-retryable HTTP error
                logger.error(
                    "Request to %s failed with HTTP error: %s",
                    url, str(e)
                )
                raise

            except requests.exceptions.RequestException as e:
                # Retry network/connection errors (not HTTP errors)
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(DEFAULT_BASE_DELAY * (2 ** attempt), DEFAULT_MAX_DELAY)
                    logger.warning(
                        "Request to %s failed on attempt %d/%d: %s, "
                        "retrying in %.1fs",
                        url, attempt + 1, self.max_retries + 1, str(e), delay
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "Request to %s failed after %d attempts: %s",
                        url, self.max_retries + 1, str(e)
                    )
                    raise

        # Should not reach here
        if last_exception:
            raise last_exception

    def initiate_query(self) -> str:
        """Initiate a reputation query to start data retrieval.

        POST /v3/reputation-query -> cache_id

        Includes retry logic for transient failures.

        Returns:
            str: The cache_id to use for polling query status

        Raises:
            requests.exceptions.HTTPError: If the API request fails after retries
            KeyError: If response is missing cache_id
        """
        url = f"{self.base_url}/v3/reputation-query"

        logger.info("Initiating reputation query at %s", url)

        response = self._request_with_retry('POST', url, timeout=60)
        data = response.json()
        cache_id = data['cache_id']

        logger.info("Query initiated successfully, cache_id: %s", cache_id)

        return cache_id

    def poll_status(self, cache_id: str, poll_interval: int = POLL_INTERVAL,
                    poll_timeout: int = POLL_TIMEOUT) -> tuple[str | None, list | None]:
        """Poll query status until completion or timeout.

        GET /v3/reputation-query/query-status/{cache_id} -> token_id or inline results

        Polls the query status endpoint in a loop, waiting for the query
        to complete. Each individual poll request has retry logic.

        When the query completes with results, returns a token_id for pagination.
        When the query completes with no results, the API returns inline empty results:
        {"status": "COMPLETED", "results": {"sourcesystem": "Lumen", "stixobjects": []}}

        Args:
            cache_id: The cache_id returned from initiate_query()
            poll_interval: Seconds to wait between status checks (default: POLL_INTERVAL)
            poll_timeout: Maximum seconds to wait for completion (default: POLL_TIMEOUT)

        Returns:
            tuple: A tuple containing:
                - str | None: The token_id for retrieving paginated results, or None if no results
                - list | None: Inline results (empty list) when no results found, or None if token_id is returned

        Raises:
            LumenAPIError: If query fails or expires
            TimeoutError: If poll_timeout is exceeded
            requests.exceptions.HTTPError: If the API request fails after retries
        """
        url = f"{self.base_url}/v3/reputation-query/query-status/{cache_id}"
        start_time = time.time()

        logger.info("Polling query status for cache_id: %s", cache_id)

        while True:
            elapsed = time.time() - start_time

            if elapsed > poll_timeout:
                logger.error("Query polling timed out after %d seconds", poll_timeout)
                raise TimeoutError(f"Query polling timed out after {poll_timeout} seconds")

            logger.debug("Polling status (elapsed: %.1fs)", elapsed)

            try:
                response = self._request_with_retry('GET', url, timeout=60)
                data = response.json()
                status = data.get('status')

                logger.debug("Query status: %s", status)

                if status == 'COMPLETED':
                    # API v3 always returns token_id for pagination, even for empty results
                    # (empty results are uploaded as an empty chunk file with total_chunks=1)
                    token_id = data.get('token_id')
                    if token_id:
                        logger.info("Query completed successfully, token_id: %s", token_id)
                        return (token_id, None)

                    # Fallback: check for inline results (legacy API behavior)
                    # API v3 doesn't return inline results, but kept for backward compatibility
                    if 'results' in data:
                        stix_objects = data.get('results', {}).get('stixobjects', [])
                        if not stix_objects:
                            logger.info("Query completed with no results (empty stixobjects)")
                            return (None, [])
                        else:
                            logger.warning(
                                "Query completed with %d inline results (unexpected), "
                                "returning inline data",
                                len(stix_objects)
                            )
                            return (None, stix_objects)

                    # No token_id and no results - treat as empty
                    logger.info("Query completed with no token_id and no results")
                    return (None, [])

                elif status in ('PENDING', 'RUNNING', 'QUEUED'):
                    # API v3 uses QUEUED instead of PENDING, but we handle both for compatibility
                    logger.debug("Query %s, waiting %d seconds", status.lower(), poll_interval)
                    time.sleep(poll_interval)
                    continue

                elif status == 'FAILED':
                    error_msg = data.get('error', 'Unknown error')
                    logger.error("Query failed: %s", error_msg)
                    raise LumenAPIError(f"Query failed: {error_msg}")

                elif status == 'EXPIRED':
                    # Note: API v3 no longer uses EXPIRED status, kept for backward compatibility
                    logger.warning("Query expired for cache_id: %s", cache_id)
                    raise LumenAPIError("Query expired")

                else:
                    # Unknown status - log and continue polling
                    logger.warning("Unknown query status: %s, continuing to poll", status)
                    time.sleep(poll_interval)

            except (LumenAPIError, TimeoutError):
                # Re-raise these specific exceptions
                raise
            except Exception as e:
                # For other exceptions during polling, log and continue
                # (the retry logic in _request_with_retry handles transient failures)
                logger.warning("Error during poll: %s, continuing to poll", str(e))
                time.sleep(poll_interval)

    def retrieve_page(self, token_id: str) -> tuple[list, str | None]:
        """Retrieve a page of results using the token_id.

        GET /v3/reputation-query/retrieve-results/{token_id} -> (indicators, next_token)

        Includes retry logic for transient failures. Handles the case where the
        API returns a 400 error indicating no results found for the token.

        Args:
            token_id: The token_id for retrieving results (from poll_status or previous page)

        Returns:
            tuple: A tuple containing:
                - list: STIX objects from the current page (empty list if no results)
                - str | None: Next token for pagination, or None if no more pages

        Raises:
            requests.exceptions.HTTPError: If the API request fails after retries
                (except for 400 "no results" which returns empty list)
        """
        url = f"{self.base_url}/v3/reputation-query/retrieve-results/{token_id}"

        logger.debug("Retrieving results page with token_id: %s", token_id)

        try:
            response = self._request_with_retry('GET', url, timeout=60)
            data = response.json()
        except requests.exceptions.HTTPError as e:
            # Handle 400 "No results found" as empty results, not an error
            if e.response is not None and e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', '')
                    if 'No results found' in error_message:
                        logger.info(
                            "No results found for token_id (API returned 400): %s",
                            token_id
                        )
                        return ([], None)
                except (ValueError, KeyError):
                    pass  # Could not parse response, re-raise original error
            raise

        stix_objects = data.get('results', {}).get('stixobjects', [])
        next_token = data.get('next_token')

        # Validate next_token - check if it points to a valid chunk
        # The API may return a next_token even on the last page that's invalid
        if next_token:
            try:
                token_data = json.loads(base64.b64decode(next_token).decode())
                next_index = token_data.get('index', 0)
                total_chunks = token_data.get('total_chunks', 1)
                if next_index >= total_chunks:
                    logger.debug(
                        "next_token points beyond available chunks (index=%d, total=%d), "
                        "treating as last page",
                        next_index, total_chunks
                    )
                    next_token = None
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.debug("Could not validate next_token format: %s", e)
                # Keep the token as-is if we can't parse it

        logger.debug("Retrieved %d STIX objects, next_token: %s",
                    len(stix_objects), next_token if next_token else "None")

        return (stix_objects, next_token)
