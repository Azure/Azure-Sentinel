"""Client for Google SecOps Detection Alerts API.

Polls Google SecOps for detection alerts. The API responds with a streaming
JSON array of detection batches that may stay open for extended periods.

Key Concepts:
  - Stream Format: JSON array of objects: [{batch1}, {batch2}, ...]
  - Streaming: Responses stream line-by-line to reduce buffering
  - Pagination: pageToken continues mid-window, pageStartTime starts new window
  - Heartbeats: Server sends heartbeat messages to keep connection alive
"""

import inspect
import json
import random
import time
from typing import Iterator, Optional, Tuple

import httpx
import google.auth.transport.requests

from . import consts
from .exceptions import GoogleSecOpsApiError, GoogleSecOpsConnectorError
from .google_auth import GoogleServiceAccountAuth
from .logger import applogger


class GoogleAuthTransport(httpx.BaseTransport):
    """HTTPX transport that signs each request with Google service account credentials."""

    def __init__(self, credentials, transport: Optional[httpx.BaseTransport] = None):
        """Initialize the transport with Google credentials.

        Args:
            credentials: Google service account credentials used to sign requests.
            transport: Underlying HTTPX transport; defaults to HTTPTransport if omitted.
        """
        self._transport = transport or httpx.HTTPTransport()
        self._auth_request = google.auth.transport.requests.Request()
        self._credentials = credentials

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Attach Google auth headers and forward the request."""
        self._credentials.before_request(
            self._auth_request,
            request.method,
            str(request.url),
            request.headers,
        )
        return self._transport.handle_request(request)


class GoogleSecOpsClient:
    """Client for polling Google SecOps Detection Alerts API.

    Handles:
      - Authentication via Google service account (HTTPX transport)
      - Streaming HTTP connections
      - Line-by-line JSON stream parsing
      - Automatic retry with exponential backoff
    """

    def __init__(
        self,
        auth: GoogleServiceAccountAuth,
        project_id: str = consts.GOOGLE_SECOPS_PROJECT_ID,
        region: str = consts.GOOGLE_SECOPS_REGION,
        instance_id: str = consts.GOOGLE_SECOPS_INSTANCE_ID,
    ):
        """Initialize SecOps client.

        Args:
            auth: GoogleServiceAccountAuth instance for API authentication.
            project_id: Google SecOps project ID.
            region: Google SecOps region (us, europe, asia-southeast1).
            instance_id: Google SecOps instance ID.

        Raises:
            ValueError: If any required configuration is missing.
        """
        __method_name = inspect.currentframe().f_code.co_name

        if not all([project_id, region, instance_id]):
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"Missing Google SecOps config: project_id={project_id}, "
                f"region={region}, instance_id={instance_id}",
            )
            applogger.error(error_msg)
            raise ValueError(error_msg)

        self._auth = auth
        self._endpoint = self._build_endpoint(project_id, region, instance_id)

        transport = GoogleAuthTransport(credentials=auth.get_credentials())
        self.http_client = httpx.Client(transport=transport)

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"Initialized Google SecOps client with endpoint: {self._endpoint[:50]}...",
            )
        )

    @staticmethod
    def _build_endpoint(project_id: str, region: str, instance_id: str) -> str:
        """Build Google SecOps API endpoint URL."""
        return (
            f"https://{region}-chronicle.googleapis.com/v1alpha/"
            f"projects/{project_id}/locations/{region}/"
            f"instances/{instance_id}/legacy:legacyStreamDetectionAlerts"
        )

    # ─── Public API ────────────────────────────────────────────────────────────

    def poll_detection_batches(
        self,
        page_start_time: str = "",
        page_token: Optional[str] = None,
        deadline_epoch: Optional[float] = None,
    ) -> Iterator[Tuple[dict, Optional[str], Optional[str]]]:
        """Poll SecOps API for detection batches.

        Yields detection batches with automatic retry on transient failures.
        Returns when the time budget is exhausted or the pagination window
        is complete (nextPageStartTime received).

        Args:
            page_start_time: Start of time window to fetch (ISO timestamp).
            page_token: Pagination token from previous call (continues mid-window).
            deadline_epoch: Unix timestamp at which to stop polling.

        Yields:
            Tuple of (batch_dict, next_token, next_start_time).

        Raises:
            GoogleSecOpsConnectorError: If too many consecutive API failures occur.
        """
        __method_name = inspect.currentframe().f_code.co_name
        current_token = page_token
        current_start = page_start_time
        consecutive_failures = 0

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"Starting detection batch polling from {page_start_time}",
            )
        )

        while True:
            if consecutive_failures > consts.MAX_CONSECUTIVE_FAILURES:
                error_msg = consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    "GoogleSecOpsClient",
                    f"Too many consecutive API failures: {consecutive_failures}",
                )
                applogger.error(error_msg)
                raise GoogleSecOpsConnectorError(error_msg)

            if consecutive_failures > 0:
                self._sleep_with_backoff(consecutive_failures)

            try:
                batch = self._make_api_call(
                    current_start, current_token, deadline_epoch
                )
            except Exception as exc:
                if not self._should_retry(exc):
                    raise

                consecutive_failures += 1
                applogger.warning(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        "GoogleSecOpsClient",
                        f"API call failed, retrying "
                        f"(attempt {consecutive_failures}/{consts.MAX_CONSECUTIVE_FAILURES}): "
                        f"{str(exc)[:100]}",
                    )
                )
                continue

            consecutive_failures = 0

            next_token = batch.get("nextPageToken")
            next_start = batch.get("nextPageStartTime")

            yield batch, next_token, next_start

            if next_start:
                applogger.info(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        "GoogleSecOpsClient",
                        "Window complete, moving to next",
                    )
                )
                return

            if deadline_epoch and time.time() >= deadline_epoch:
                applogger.warning(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        "GoogleSecOpsClient",
                        "Time budget exhausted",
                    )
                )
                return

            current_token = next_token or current_token
            current_start = next_start or current_start

    # ─── Internal: API Communication ───────────────────────────────────────────

    def _make_api_call(
        self,
        page_start: str,
        page_token: Optional[str],
        deadline: Optional[float],
    ) -> dict:
        """Make a single streaming HTTP request to the Google SecOps API.

        Args:
            page_start: Window start time.
            page_token: Pagination token (if continuing mid-window).
            deadline: Function timeout deadline.

        Returns:
            Parsed JSON batch dict.

        Raises:
            GoogleSecOpsApiError: On HTTP errors or stream read failures.
            GoogleSecOpsConnectorError: If deadline exceeded.
        """
        __method_name = inspect.currentframe().f_code.co_name

        if deadline and time.time() >= deadline:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                "Time budget exhausted before API call",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsConnectorError(error_msg)

        request_body = self._build_request_body(page_start, page_token)

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"API call (batch={consts.DETECTION_BATCH_SIZE}, "
                f"max={consts.MAX_DETECTIONS}, "
                f"timeout={consts.API_TIMEOUT_SECONDS}s)",
            )
        )

        final_response = {}
        batch = ""
        depth = 0
        try:
            with self.http_client.stream(
                "POST",
                url=self._endpoint,
                content=json.dumps(request_body),
                timeout=consts.API_TIMEOUT_SECONDS,
            ) as response:
                self._check_response_status(response, page_token, page_start)

                for line in response.iter_lines():
                    if not line:
                        continue

                    # Slice from first { so array openers like "[{" or bare
                    # "[", "]", "," are skipped without entering the buffer
                    if depth == 0:
                        start = line.find('{')
                        if start == -1:
                            continue
                        line = line[start:]

                    batch += line
                    # str.count() is C-level — not char-by-char Python iteration
                    depth += line.count('{') - line.count('}')

                    if depth != 0:
                        continue

                    # depth == 0: complete object in buffer; strip trailing },  }] }],
                    try:
                        obj = json.loads(batch.rstrip(' ,]'))
                    except json.JSONDecodeError as exc:
                        error_msg = consts.LOG_FORMAT.format(
                            consts.LOG_PREFIX,
                            __method_name,
                            "GoogleSecOpsClient",
                            f"Failed to parse stream JSON: {exc}",
                        )
                        applogger.error(error_msg)
                        raise GoogleSecOpsApiError(error_msg) from exc
                    batch = ""

                    if obj.get("heartbeat"):
                        applogger.debug(
                            consts.LOG_FORMAT.format(
                                consts.LOG_PREFIX,
                                __method_name,
                                "GoogleSecOpsClient",
                                "Heartbeat received (connection active)",
                            )
                        )
                        continue

                    if "detections" in obj or "nextPageStartTime" in obj:
                        applogger.info(
                            consts.LOG_FORMAT.format(
                                consts.LOG_PREFIX,
                                __method_name,
                                "GoogleSecOpsClient",
                                f"Batch received with "
                                f"{len(obj.get('detections', []))} detections",
                            )
                        )
                        final_response = obj
                        break

        except GoogleSecOpsApiError:
            # Already wrapped/logged by _check_response_status; don't re-wrap
            raise
        except httpx.TimeoutException as exc:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"Request timed out after {consts.API_TIMEOUT_SECONDS}s: {exc}",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsApiError(error_msg) from exc
        except httpx.RequestError as exc:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"Network error: {exc}",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsApiError(error_msg) from exc
        except Exception as exc:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"Unexpected error during API call: {exc}",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsApiError(error_msg) from exc

        return final_response

    @staticmethod
    def _build_request_body(page_start: str, page_token: Optional[str]) -> dict:
        """Build Google SecOps API request body.

        Picks pageToken when continuing mid-window, otherwise pageStartTime.
        """
        body = {
            "detectionBatchSize": consts.DETECTION_BATCH_SIZE,
            "maxDetections": consts.MAX_DETECTIONS,
        }

        if page_token:
            body["pageToken"] = page_token
        else:
            body["pageStartTime"] = page_start

        return body

    @staticmethod
    def _check_response_status(
        response: httpx.Response,
        page_token: Optional[str],
        page_start: str,
    ) -> None:
        """Check HTTP response status and raise GoogleSecOpsApiError on errors.

        Provides config-specific guidance for the common SecOps misconfigurations:
          - 400: malformed request body or invalid parameter values
          - 401: invalid/expired credentials or wrong instance ID
          - 403: service account lacks permission, or wrong project ID
          - 404: wrong region, project, or instance ID (endpoint not found)

        Args:
            response: HTTPX streaming response.
            page_token: Request's pagination token (for diagnostics).
            page_start: Request's start time (for diagnostics).

        Raises:
            GoogleSecOpsApiError: On HTTP error responses.
        """
        __method_name = inspect.currentframe().f_code.co_name
        status = response.status_code

        if status < 400:
            return

        # Streaming responses don't buffer the body; read it before .text works.
        try:
            response.read()
            body_snippet = response.text[:500] if response.text else ""
        except Exception:
            body_snippet = ""

        diagnostics = (
            f"project_id={consts.GOOGLE_SECOPS_PROJECT_ID}, "
            f"region={consts.GOOGLE_SECOPS_REGION}, "
            f"instance_id={consts.GOOGLE_SECOPS_INSTANCE_ID}, "
            f"pageToken={'set' if page_token else 'not set'}, "
            f"pageStart={page_start or 'not set'}"
        )

        if status == 400:
            hint = (
                "Bad Request (400) - malformed request body or invalid params. "
                "Check pageStartTime format (ISO 8601 with 'Z') and batch sizes."
            )
        elif status == 401:
            hint = (
                "Unauthorized (401) - invalid or expired credentials, or "
                "incorrect GoogleSecopsInstanceId. Verify the instance ID."
            )
        elif status == 403:
            hint = (
                "Forbidden (403) - service account lacks Google SecOps API "
                "permission, or incorrect GoogleSecopsProjectId. Verify the project "
                "ID and that the service account has the Google SecOps API Viewer "
                "(or equivalent) role."
            )
        elif status == 404:
            hint = (
                "Not Found (404) - endpoint does not exist. Verify "
                "GoogleSecopsRegion (e.g. 'us', 'europe', 'asia-southeast1') and "
                "that the project/instance combination is valid for that region."
            )
        else:
            hint = f"HTTP error {status}"

        error_msg = consts.LOG_FORMAT.format(
            consts.LOG_PREFIX,
            __method_name,
            "GoogleSecOpsClient",
            f"{hint} | {diagnostics}"
            + (f" | response_body={body_snippet}" if body_snippet else ""),
        )
        applogger.error(error_msg)
        raise GoogleSecOpsApiError(error_msg, status_code=status)

    # ─── Internal: Retry Logic ─────────────────────────────────────────────────

    @staticmethod
    def _should_retry(exc: Exception) -> bool:
        """Return True if the exception is transient and worth retrying.

        Retryable: HTTP 429/5xx, network timeouts, transport errors.
        Not retryable: HTTP 400/401, JSON parse errors.
        """
        if isinstance(exc, GoogleSecOpsApiError):
            return exc.status_code in consts.RETRYABLE_STATUS_CODES

        # httpx.TimeoutException is a subclass of RequestError, so this covers both
        return isinstance(exc, httpx.RequestError)

    @staticmethod
    def _sleep_with_backoff(attempt: int) -> None:
        """Sleep with exponential backoff plus jitter before retrying.

        delay = base * 2^attempt + random(0, 1)
        """
        __method_name = inspect.currentframe().f_code.co_name
        delay = consts.RETRY_BASE_DELAY_SECONDS * (2**attempt) + random.uniform(0, 1.0)
        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"Backoff {delay:.1f}s before retry {attempt}/{consts.MAX_CONSECUTIVE_FAILURES}",
            )
        )
        time.sleep(delay)
