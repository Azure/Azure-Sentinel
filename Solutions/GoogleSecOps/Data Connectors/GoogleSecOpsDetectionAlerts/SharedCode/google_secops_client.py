"""Client for Google SecOps Detection Alerts API.

Polls Google SecOps for detection alerts. The API responds with a streaming
JSON array of detection batches that may stay open for extended periods.

Key Concepts:
  - Stream Format: JSON array of objects: [{batch1}, {batch2}, ...]
  - Streaming: Responses stream character-by-character at detection granularity
  - Pagination: pageToken continues mid-window, pageStartTime starts new window
  - Heartbeats: Server sends heartbeat messages to keep connection alive
"""

import inspect
import io
import json
import random
import re
import time
from typing import Iterator, Optional, Tuple

import httpx
import google.auth.transport.requests

from . import consts
from .exceptions import GoogleSecOpsApiError, GoogleSecOpsConnectorError
from .google_auth import GoogleServiceAccountAuth
from .logger import applogger

_RE_NEXT_TOKEN = re.compile(r'"nextPageToken"\s*:\s*"([^"]+)"')
_RE_NEXT_START = re.compile(r'"nextPageStartTime"\s*:\s*"([^"]+)"')
_RE_HEARTBEAT = re.compile(r'"heartbeat"\s*:\s*true', re.IGNORECASE)

# Tokenizer: matches only the characters Python needs to inspect.
# Complete JSON string literals ("...") are consumed in a single C-level
# re operation, so Python never iterates over their content character by
# character. Only structural tokens ({, }, [, ], :) and string boundaries
# reach the Python loop — typically 5–20x fewer iterations than char-by-char
# for payloads dominated by string values (base64 logs, IDs, timestamps).
# Matches a complete JSON string literal, an escape sequence, or a single
# structural character. Used with .match(buf, pos) — NOT finditer — so it
# only fires at an explicitly supplied position, never inside an incomplete
# string that spans a chunk boundary.
_TOKEN_RE = re.compile(
    r'"(?:[^"\\]|\\.)*"'    # complete JSON string literal (handles \" escapes)
    r'|\\.'                  # escape sequence outside a string (defensive)
    r'|[{}\[\]:]',           # structural character (colon included for key detection)
    re.DOTALL,
)

# Matches a run of characters that are not structural, not string-starting,
# and not backslash — i.e. whitespace, commas, digits, true/false/null, etc.
# Used to fast-skip gap content between tokens without per-character Python loops.
_GAP_RE = re.compile(r'[^{}\[\]:"\\]+', re.DOTALL)


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
        applogger.debug(f"GoogleAuthTransport: Signed {request.method} request to {str(request.url)[:50]}...")
        return self._transport.handle_request(request)


class GoogleSecOpsClient:
    """Client for streaming Google SecOps Detection Alerts at detection granularity.

    Handles:
      - Authentication via Google service account (HTTPX transport)
      - Streaming HTTP connections
      - Character-level JSON parsing: yields one detection at a time
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

    def stream_detections(
        self,
        page_start_time: str = "",
        page_token: Optional[str] = None,
    ) -> Iterator[Tuple[str, Optional[str], Optional[str]]]:
        """Stream detections from one API call, then yield a batch-end sentinel.

        Makes a single HTTP request (with retry on transient failures), streams
        individual detection objects, then yields a sentinel carrying whatever
        pagination token the API returned. The caller updates the checkpoint from
        the sentinel and decides whether to call again.

        Yields:
            (json_string, None, None)  — one detection
            ("", next_token, next_start) — sentinel: batch done, update checkpoint

        Raises:
            GoogleSecOpsConnectorError: After MAX_CONSECUTIVE_FAILURES retries.
            GoogleSecOpsApiError: On non-retryable HTTP or network errors.
        """
        __method_name = inspect.currentframe().f_code.co_name
        pagination = {"next_token": None, "next_start": None}
        det_count = 0
        last_exc: Optional[Exception] = None

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleSecOpsClient",
                f"API call: start={page_start_time},"
                f" token={'yes' if page_token else 'no'}",
            )
        )

        for attempt in range(consts.MAX_CONSECUTIVE_FAILURES + 1):
            if attempt > 0:
                self._sleep_with_backoff(attempt)

            last_exc = None
            try:
                request_body = self._build_request_body(page_start_time, page_token)
                applogger.debug(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        "GoogleSecOpsClient",
                        f"Built request body: batch_size={request_body.get('detectionBatchSize')}, "
                        f"max_detections={request_body.get('maxDetections')}",
                    )
                )
                with self.http_client.stream(
                    "POST",
                    url=self._endpoint,
                    content=json.dumps(request_body),
                    timeout=consts.API_TIMEOUT_SECONDS,
                ) as response:
                    self._check_response_status(response, page_token, page_start_time)
                    applogger.debug(
                        consts.LOG_FORMAT.format(
                            consts.LOG_PREFIX,
                            __method_name,
                            "GoogleSecOpsClient",
                            f"Response status: {response.status_code}, "
                            f"content-type: {response.headers.get('content-type', 'unknown')}",
                        )
                    )
                    stream_deadline = time.time() + consts.STREAM_MAX_SECONDS
                    applogger.debug(
                        consts.LOG_FORMAT.format(
                            consts.LOG_PREFIX,
                            __method_name,
                            "GoogleSecOpsClient",
                            f"Starting stream parsing with {consts.STREAM_MAX_SECONDS}s deadline",
                        )
                    )
                    for det_raw in self._iter_detections_from_response(
                        response, pagination, stream_deadline, page_start_time
                    ):
                        det_count += 1
                        yield det_raw, None, None
                applogger.debug(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        "GoogleSecOpsClient",
                        f"Stream parsing completed successfully, detections parsed: {det_count}",
                    )
                )
                break  # success

            except GoogleSecOpsApiError:
                raise

            except (httpx.TimeoutException, httpx.RequestError) as exc:
                error_msg = consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX, __method_name, "GoogleSecOpsClient",
                    f"Transient error attempt {attempt + 1}: {exc}",
                )
                if not self._should_retry(exc):
                    applogger.error(error_msg)
                    raise GoogleSecOpsApiError(error_msg) from exc
                last_exc = exc
                applogger.warning(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX, __method_name, "GoogleSecOpsClient",
                        f"Retrying ({attempt + 1}/{consts.MAX_CONSECUTIVE_FAILURES}): {exc}",
                    )
                )

            except Exception as exc:
                # Detect Google auth failures specifically for a clearer error message.
                # RefreshError / invalid_grant means the service account key is wrong,
                # revoked, or the host clock has drifted >5 minutes (Google rejects
                # JWTs whose iat/exp timestamps are too far from server time).
                exc_str = str(exc).lower()
                if "invalid_grant" in exc_str or "refresherror" in type(exc).__name__.lower():
                    error_msg = consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX, __method_name, "GoogleSecOpsClient",
                        f"Google auth failed (invalid_grant). Possible causes: "
                        f"(1) service account key was rotated/revoked in Google Cloud Console — "
                        f"re-add the key JSON to the GoogleSecopsServiceAccountJson app setting; "
                        f"(2) Azure host clock skew >5 min — restart the Function App to resync; "
                        f"(3) private_key newlines corrupted in app settings. "
                        f"Original error: {exc}",
                    )
                else:
                    error_msg = consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX, __method_name, "GoogleSecOpsClient",
                        f"Unexpected error: {exc}",
                    )
                applogger.error(error_msg)
                raise GoogleSecOpsApiError(error_msg) from exc

        if last_exc is not None:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX, __method_name, "GoogleSecOpsClient",
                f"Giving up after {consts.MAX_CONSECUTIVE_FAILURES} retries: {last_exc}",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsConnectorError(error_msg)

        next_token = pagination["next_token"]
        next_start = pagination["next_start"]

        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX, __method_name, "GoogleSecOpsClient",
                f"Batch complete: {det_count} detections,"
                f" next_token={'yes' if next_token else 'no'},"
                f" next_start={'yes' if next_start else 'no'}",
            )
        )

        yield "", next_token, next_start

    # ─── Internal: Detection-level stream parser ───────────────────────────────

    @staticmethod
    def _iter_detections_from_response(
        response: httpx.Response,
        pagination_out: dict,
        stream_deadline: Optional[float] = None,
        page_start_time: str = "",
    ) -> Iterator[str]:
        """Parse HTTP response at detection granularity.

        Uses _TOKEN_RE.match(buf, pos) in a manual while-loop rather than
        finditer. This is the critical difference from a naive approach:

        WHY NOT finditer?
        finditer scans the whole buffer looking for any match. If a string
        value spans a chunk boundary, finditer cannot match the incomplete
        string — but it WILL match { or } characters *inside* that incomplete
        string as structural tokens. This corrupts det_depth, causes premature
        detection yields, and produces invalid JSON in the output files.

        WHY match(buf, pos)?
        match only tries at the exact position pos. If buf[pos] is '"' but
        the string has no closing '"' in this chunk, match returns None.
        We detect this, set carry = buf[pos:], and wait for the next chunk
        to complete the string. Structural chars inside incomplete strings
        are never seen by the state machine.

        _GAP_RE fast-skips runs of whitespace/commas/numbers/booleans in
        a single C-level regex call rather than iterating char-by-char.

        State machine:
          SCAN_BATCH   → find opening { of a batch/heartbeat object
          SCAN_KEY     → scan top-level keys inside the batch object
          AFTER_KEY    → saw string "detections" at batch_depth==1, want :
          WAIT_ARRAY   → saw :, want [
          BETWEEN_DETS → inside detections [], between individual objects
          IN_DET       → accumulate one detection object into det_buf
          BATCH_TAIL   → after ] of detections array, collect pagination tail
        """
        SCAN_BATCH, SCAN_KEY, AFTER_KEY = 0, 1, 2
        WAIT_ARRAY, BETWEEN_DETS, IN_DET, BATCH_TAIL = 3, 4, 5, 6

        state = SCAN_BATCH
        batch_depth = 0
        det_depth = 0
        det_buf = io.StringIO()
        tail_buf = io.StringIO()
        # scan_buf accumulates each non-detection batch object so we can
        # extract pagination fields from it and detect the heartbeat flag.
        scan_buf = io.StringIO()
        carry = ""
        # Tracks nextPageStartTime seen inside heartbeat objects.
        # Used as a fallback when stream_deadline is hit before a pure
        # nextPageStartTime object arrives (no-detection windows can stream
        # heartbeats for the entire window duration, exceeding the function
        # timeout if we wait for the definitive signal).
        candidate_next_start: Optional[str] = None

        def _flush_pagination():
            tail = tail_buf.getvalue()
            next_token_match = _RE_NEXT_TOKEN.search(tail)
            next_start_match = _RE_NEXT_START.search(tail)
            pagination_out["next_token"] = next_token_match.group(1) if next_token_match else None
            pagination_out["next_start"] = next_start_match.group(1) if next_start_match else None

        try:
            for chunk in response.iter_text():
                # Deadline check: we've been streaming too long with no detections.
                # The server streams heartbeats for the entire window duration;
                # for a live or long window with no data that can exceed the
                # 10-minute Azure Function timeout.
                # Use the nextPageStartTime seen in heartbeats as the new
                # checkpoint start. If the server never sent one (bare heartbeats),
                # fall back to the current UTC time so the checkpoint advances
                # and we don't loop forever on the same empty window.
                if (
                    stream_deadline
                    and time.time() > stream_deadline
                    and state in (SCAN_BATCH, SCAN_KEY)
                ):
                    pagination_out["next_start"] = (
                        candidate_next_start
                        or page_start_time
                    )
                    applogger.warning(
                        f"Stream deadline reached without complete pagination object. "
                        f"Using fallback next_start: {pagination_out['next_start']}"
                    )
                    return

                buf = carry + chunk
                carry = ""
                pos = 0
                buf_len = len(buf)

                while pos < buf_len:
                    token_match = _TOKEN_RE.match(buf, pos)

                    if token_match:
                        tok = token_match.group(0)
                        is_str = tok[0] == '"'

                        # ── state machine ─────────────────────────────────
                        if state == SCAN_BATCH:
                            if tok == "{":
                                batch_depth = 1
                                scan_buf.seek(0)
                                scan_buf.truncate()
                                state = SCAN_KEY

                        elif state == SCAN_KEY:
                            # Capture every token for pagination / heartbeat detection
                            if batch_depth >= 1:
                                scan_buf.write(tok)

                            if is_str and tok[1:-1] == "detections" and batch_depth == 1:
                                state = AFTER_KEY
                            elif tok == "{":
                                batch_depth += 1
                            elif tok == "}":
                                batch_depth -= 1
                                if batch_depth == 0:
                                    # Object closed without a detections array.
                                    content = scan_buf.getvalue()
                                    scan_buf.seek(0)
                                    scan_buf.truncate()
                                    if not _RE_HEARTBEAT.search(content):
                                        # Pure pagination object (no heartbeat flag):
                                        # return immediately — this is the definitive
                                        # window-complete or next-page signal.
                                        next_token_match = _RE_NEXT_TOKEN.search(content)
                                        next_start_match = _RE_NEXT_START.search(content)
                                        if next_token_match or next_start_match:
                                            pagination_out["next_token"] = next_token_match.group(1) if next_token_match else None
                                            pagination_out["next_start"] = next_start_match.group(1) if next_start_match else None
                                            applogger.debug(
                                                f"Pagination object found: "
                                                f"next_token={'yes' if pagination_out['next_token'] else 'no'}, "
                                                f"next_start={'yes' if pagination_out['next_start'] else 'no'}"
                                            )
                                            return
                                    else:
                                        # Heartbeat: save any nextPageStartTime as a
                                        # deadline-fallback candidate (the server sends
                                        # its current position so we know how far along
                                        # the window it is even if the definitive signal
                                        # never arrives before our deadline).
                                        next_start_match = _RE_NEXT_START.search(content)
                                        if next_start_match:
                                            candidate_next_start = next_start_match.group(1)
                                    state = SCAN_BATCH

                        elif state == AFTER_KEY:
                            if tok == ":":
                                state = WAIT_ARRAY
                            else:
                                state = SCAN_KEY
                                if is_str and tok[1:-1] == "detections" and batch_depth == 1:
                                    state = AFTER_KEY
                                elif tok == "{":
                                    batch_depth += 1
                                elif tok == "}":
                                    batch_depth -= 1
                                    if batch_depth == 0:
                                        state = SCAN_BATCH

                        elif state == WAIT_ARRAY:
                            if tok == "[":
                                state = BETWEEN_DETS
                            elif tok != ":":
                                state = SCAN_KEY
                                if tok == "{":
                                    batch_depth += 1
                                elif tok == "}":
                                    batch_depth -= 1
                                    if batch_depth == 0:
                                        state = SCAN_BATCH

                        elif state == BETWEEN_DETS:
                            if tok == "{":
                                det_buf.seek(0)
                                det_buf.truncate()
                                det_buf.write(tok)
                                det_depth = 1
                                state = IN_DET
                            elif tok == "]":
                                state = BATCH_TAIL

                        elif state == IN_DET:
                            det_buf.write(tok)
                            if tok == "{":
                                det_depth += 1
                            elif tok == "}":
                                det_depth -= 1
                                if det_depth == 0:
                                    yield det_buf.getvalue()
                                    det_buf.seek(0)
                                    det_buf.truncate()
                                    state = BETWEEN_DETS

                        elif state == BATCH_TAIL:
                            tail_buf.write(tok)
                            if tok == "{":
                                batch_depth += 1
                            elif tok == "}":
                                batch_depth -= 1
                                if batch_depth == 0:
                                    _flush_pagination()
                                    return

                        pos = token_match.end()

                    else:
                        ch = buf[pos]
                        if ch == '"':
                            # Incomplete string — chunk boundary falls inside this
                            # string. Carry everything from the opening " so the
                            # next chunk can complete the match. Do NOT let any
                            # { or } inside the incomplete string be seen as tokens.
                            carry = buf[pos:]
                            break
                        elif ch == '\\':
                            # Lone backslash at chunk end (very rare: \ before \n etc.)
                            # Carry so the next char arrives and \. can match.
                            carry = buf[pos:]
                            break
                        else:
                            # Gap content: whitespace, commas, digits, true/false/null
                            gap_match = _GAP_RE.match(buf, pos)
                            if gap_match:
                                gap = gap_match.group(0)
                                if state == IN_DET:
                                    det_buf.write(gap)
                                elif state == BATCH_TAIL:
                                    tail_buf.write(gap)
                                elif state == SCAN_KEY and batch_depth >= 1:
                                    scan_buf.write(gap)
                                pos = gap_match.end()
                            else:
                                # Single unrecognised char — write and advance
                                if state == IN_DET:
                                    det_buf.write(ch)
                                elif state == BATCH_TAIL:
                                    tail_buf.write(ch)
                                elif state == SCAN_KEY and batch_depth >= 1:
                                    scan_buf.write(ch)
                                pos += 1

            # Stream ended before the batch object's closing }
            if state == BATCH_TAIL:
                applogger.debug("Stream ended in BATCH_TAIL state, flushing pagination")
                _flush_pagination()

        finally:
            # Close the HTTP connection immediately so httpx does NOT try to
            # drain the remaining stream body. Without this, httpx drains the
            # response to allow connection reuse — but the Google SecOps API
            # streams heartbeats indefinitely, causing a full function timeout.
            response.close()
            det_buf.close()
            tail_buf.close()
            scan_buf.close()
            applogger.debug("Stream parser resources cleaned up: response, buffers closed")

    # ─── Internal: Request helpers ─────────────────────────────────────────────

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

        applogger.debug(f"Response status check: {status}")
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
