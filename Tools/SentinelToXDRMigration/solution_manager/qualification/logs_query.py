from __future__ import annotations

import base64
import json
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from decimal import Decimal
from typing import Any, Callable, Mapping

from solution_manager.qualification.graph_client_config import azure_cli_credential as profiled_azure_cli_credential
from solution_manager.core.onboarding import _state_dir


DEFAULT_REQUEST_TIMEOUT_SECONDS = 90
DEFAULT_FAMILY_TIMEOUT_SECONDS = 30 * 60
MAX_TRANSIENT_RETRIES = 2
MAX_SERVER_TIMEOUT_SECONDS = 600


class LogsQueryFailure(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        failure_kind: str,
        status_code: int = 0,
        error_details: str | None = None,
    ) -> None:
        super().__init__(message)
        self.failure_kind = failure_kind
        self.status_code = status_code
        self.error_details = error_details or message


def azure_cli_credential(target: Mapping[str, str]):
    """Create a non-interactive credential pinned to the locked target."""
    return profiled_azure_cli_credential(
        tenant_id=target["tenantId"],
        state_root=_state_dir(),
    )


def logs_query_client(credential: Any, *, retry_total: int = 0):
    from azure.monitor.query import LogsQueryClient

    return LogsQueryClient(credential, retry_total=retry_total)


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return {"$datetime": value.isoformat()}
    if isinstance(value, date):
        return {"$date": value.isoformat()}
    if isinstance(value, timedelta):
        return {"$timedeltaSeconds": value.total_seconds()}
    if isinstance(value, Decimal):
        return {"$decimal": str(value)}
    if isinstance(value, uuid.UUID):
        return {"$uuid": str(value)}
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"$base64": base64.b64encode(bytes(value)).decode("ascii")}
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    raise TypeError(f"unsupported Azure Monitor result value: {type(value).__name__}")


def _table_result(table: Any) -> dict[str, Any]:
    table_name = getattr(table, "name", None)
    columns = getattr(table, "columns", None)
    column_types = getattr(table, "columns_types", None)
    rows = getattr(table, "rows", None)
    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table name is missing or invalid")
    if not isinstance(columns, list) or not columns:
        raise ValueError(f"table {table_name!r} has no column names")
    if not isinstance(column_types, list) or len(column_types) != len(columns):
        raise ValueError(f"table {table_name!r} has missing or mismatched column types")
    if any(not isinstance(name, str) or not name.strip() for name in columns):
        raise ValueError(f"table {table_name!r} has an invalid column name")
    if any(not isinstance(value_type, str) or not value_type.strip() for value_type in column_types):
        raise ValueError(f"table {table_name!r} has an invalid column type")
    if not isinstance(rows, list):
        raise ValueError(f"table {table_name!r} has invalid rows")
    schema = [
        {"name": name, "type": value_type}
        for name, value_type in zip(columns, column_types)
    ]
    serialized_rows = []
    for row in rows:
        try:
            if len(row) != len(columns):
                raise ValueError(
                    f"table {table_name!r} row has {len(row)} values for {len(columns)} columns"
                )
            serialized_rows.append([_json_value(value) for value in row])
        except TypeError as exc:
            raise ValueError(f"table {table_name!r} has a malformed row") from exc
    return {
        "name": table_name,
        "columns": schema,
        "rowCount": len(serialized_rows),
        "rows": serialized_rows,
    }


def _error_details(error: Any) -> str:
    if error is None:
        return "Azure Monitor returned a partial query result without error details"
    message = getattr(error, "message", None)
    if message:
        return str(message)[:8000]
    if isinstance(error, Mapping):
        return str(_json_value(error))[:8000]
    return str(error)[:8000]


def _error_payload(error: Any) -> Any:
    if error is None:
        return None
    if isinstance(error, Mapping):
        return _json_value(error)
    payload = {
        key: getattr(error, key)
        for key in ("code", "message", "details", "target")
        if getattr(error, key, None) is not None
    }
    return _json_value(payload or {"message": str(error)})


def _status_code(error: Exception) -> int:
    value = getattr(error, "status_code", None)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _retry_after(error: Exception) -> float | None:
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", None)
    value = headers.get("Retry-After") if headers is not None else None
    try:
        return min(30.0, max(0.0, float(value)))
    except (TypeError, ValueError):
        try:
            retry_at = parsedate_to_datetime(str(value))
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return min(
            30.0,
            max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds()),
        )


def _failure_kind(error: Exception) -> tuple[str, bool]:
    from azure.core.exceptions import (
        ClientAuthenticationError,
        ServiceRequestError,
        ServiceResponseError,
    )
    from azure.identity import CredentialUnavailableError

    if isinstance(error, (ClientAuthenticationError, CredentialUnavailableError)):
        return "authentication", False
    if isinstance(error, (ServiceRequestError, ServiceResponseError, TimeoutError, OSError)):
        return "transport", True
    status_code = _status_code(error)
    if status_code == 401:
        return "authentication", False
    if status_code == 403:
        return "authorization", False
    if status_code == 400:
        return "query", False
    if status_code in {408, 429, 500, 502, 503, 504}:
        return "transient-provider-error", True
    return "provider", False


def execute_workspace_query(
    client: Any,
    workspace_id: str,
    query: str,
    *,
    request_timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
    retry_count: int = MAX_TRANSIENT_RETRIES,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    budget_seconds: int | None = None,
) -> dict[str, Any]:
    """Execute the exact KQL text once per attempt, with no shell or time filter."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("source query must be non-empty text")
    if not 1 <= request_timeout_seconds <= MAX_SERVER_TIMEOUT_SECONDS:
        raise ValueError("request timeout must be between 1 and 600 seconds")
    if not 0 <= retry_count <= MAX_TRANSIENT_RETRIES:
        raise ValueError("retry count must be between 0 and 2")

    attempts = 0
    deadline = monotonic() + budget_seconds if budget_seconds is not None else None
    while True:
        remaining = deadline - monotonic() if deadline is not None else request_timeout_seconds
        if remaining < 1:
            raise LogsQueryFailure(
                "the bounded query request budget expired",
                failure_kind="timeout",
            )
        effective_timeout = min(request_timeout_seconds, max(1, int(remaining)))
        attempts += 1
        metadata: dict[str, Any] = {}

        def capture_response(pipeline_response: Any) -> None:
            if pipeline_response.http_response.status_code != 200:
                return
            body = json.loads(pipeline_response.http_response.text())
            if not isinstance(body, dict):
                raise ValueError("Log Analytics response must be a JSON object")
            metadata["dataSources"] = body.get("dataSources")

        def request_metadata(pipeline_request: Any) -> None:
            headers = pipeline_request.http_request.headers
            preference = headers.get("Prefer", "")
            headers["Prefer"] = ",".join(
                value for value in (preference, "include-dataSources=true") if value
            )

        try:
            response = client.query_workspace(
                workspace_id,
                query,
                timespan=None,
                server_timeout=effective_timeout,
                connection_timeout=min(10, effective_timeout),
                read_timeout=effective_timeout,
                raw_request_hook=request_metadata,
                raw_response_hook=capture_response,
            )
        except Exception as exc:
            kind, retryable = _failure_kind(exc)
            status_code = _status_code(exc)
            if retryable and attempts <= retry_count:
                delay = _retry_after(exc)
                delay = delay if delay is not None else min(2**attempts, 8)
                remaining = deadline - monotonic() if deadline is not None else None
                if remaining is not None and delay >= remaining:
                    raise LogsQueryFailure(
                        "the bounded query request budget expired before a retry",
                        failure_kind="timeout",
                        status_code=status_code,
                        error_details=str(exc)[:8000],
                    ) from exc
                sleep(delay)
                continue
            message = str(exc)[:2000] or type(exc).__name__
            raise LogsQueryFailure(
                message,
                failure_kind=kind,
                status_code=status_code,
                error_details=str(exc)[:8000] or type(exc).__name__,
            ) from exc

        partial = hasattr(response, "partial_data")
        raw_tables = response.partial_data if partial else getattr(response, "tables", None)
        if partial and raw_tables is None:
            raw_tables = []
        try:
            if not isinstance(raw_tables, list):
                raise ValueError("query response has no table list")
            if not partial and not raw_tables:
                raise ValueError("successful query response has no result tables")
            tables = [_table_result(table) for table in raw_tables]
        except (AttributeError, TypeError, ValueError) as exc:
            raise LogsQueryFailure(
                f"Azure Monitor SDK returned malformed table data: {exc}",
                failure_kind="provider",
                error_details=str(exc),
            ) from exc
        schema = [
            column
            for table in tables
            for column in table["columns"]
        ]
        return {
            "status": "failed" if partial else "passed",
            "statusCode": 206 if partial else 200,
            "rowCount": sum(table["rowCount"] for table in tables),
            "schema": schema,
            "tables": tables,
            "attempts": attempts,
            "failureKind": "partial-response" if partial else None,
            "partial": partial,
            "error": _error_details(getattr(response, "partial_error", None)) if partial else None,
            "errorDetails": _error_details(getattr(response, "partial_error", None)) if partial else None,
            "partialError": _error_payload(getattr(response, "partial_error", None)) if partial else None,
            "dataSources": metadata.get("dataSources"),
        }


def verify_azure_cli_target(target: Mapping[str, str]) -> None:
    """Reject missing or cross-target Azure CLI identity without signing in."""
    import subprocess

    from solution_manager.core.target_context import _json_output, _run_az

    result = _run_az(("account", "show"), runner=subprocess.run)
    if result.returncode:
        raise LogsQueryFailure(
            "Azure CLI is not authenticated; sign in separately to the locked Qualification target",
            failure_kind="authentication",
        )
    account = _json_output(result)
    if not isinstance(account, dict):
        raise LogsQueryFailure(
            "Azure CLI did not return its active tenant and subscription",
            failure_kind="authentication",
        )
    try:
        tenant = str(uuid.UUID(str(account.get("tenantId") or "")))
        subscription = str(uuid.UUID(str(account.get("id") or "")))
    except (ValueError, AttributeError) as exc:
        raise LogsQueryFailure(
            "Azure CLI did not return valid active tenant and subscription identifiers",
            failure_kind="authentication",
        ) from exc
    if tenant != target["tenantId"] or subscription != target["subscriptionId"]:
        raise LogsQueryFailure(
            "Azure CLI tenant or subscription does not match the locked Qualification target",
            failure_kind="authentication",
        )


def preflight_read_executor(
    request: Mapping[str, Any],
    *,
    request_timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Adapt the SDK executor to preflight.run_preflight's read-executor contract."""
    if request.get("provider") != "logAnalytics":
        raise ValueError("Azure Monitor SDK preflight only supports the logAnalytics provider")
    target = request.get("target")
    query = request.get("query")
    if not isinstance(target, Mapping) or not isinstance(query, str):
        raise ValueError("preflight SDK requests require a locked target and KQL query")
    verify_azure_cli_target(target)
    credential = azure_cli_credential(target)
    client = logs_query_client(credential, retry_total=0)
    try:
        result = execute_workspace_query(
            client,
            target["workspaceCustomerId"],
            query,
            request_timeout_seconds=request_timeout_seconds,
            retry_count=MAX_TRANSIENT_RETRIES,
        )
    except LogsQueryFailure as exc:
        return {
            "ok": False,
            "statusCode": exc.status_code,
            "failureKind": exc.failure_kind,
            "error": str(exc),
        }
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()
    return {
        "ok": result["status"] == "passed",
        "statusCode": result["statusCode"],
        "rowCount": result["rowCount"],
        "schema": result["schema"],
        "failureKind": result["failureKind"],
        "tableAvailable": result["status"] == "passed",
    }


def query_family(
    client: Any,
    workspace_id: str,
    queries: list[dict[str, str]],
    *,
    request_timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
    family_timeout_seconds: int = DEFAULT_FAMILY_TIMEOUT_SECONDS,
    retry_count: int = MAX_TRANSIENT_RETRIES,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> list[dict[str, Any]]:
    if not 1 <= family_timeout_seconds <= 6 * 60 * 60:
        raise ValueError("family timeout must be between 1 and 21600 seconds")
    deadline = monotonic() + family_timeout_seconds
    results: list[dict[str, Any]] = []
    stop_family = False
    for item in queries:
        started = monotonic()
        detection = item["detection"]
        query = item["query"]
        if stop_family:
            results.append({
                "detection": detection,
                "status": "not-run",
                "valid": False,
                "querySha256": item["querySha256"],
                "statusCode": 0,
                "rowCount": 0,
                "schema": [],
                "error": "not executed after an earlier provider-level failure",
                "errorDetails": None,
            })
            continue
        remaining = deadline - monotonic()
        if remaining < 1:
            response = LogsQueryFailure(
                "the complete Sentinel query-family time budget expired",
                failure_kind="timeout",
            )
            stop_family = True
            result = {
                "status": "not-run",
                "valid": False,
                "querySha256": item["querySha256"],
                "statusCode": 0,
                "rowCount": 0,
                "schema": [],
                "error": str(response),
                "errorDetails": str(response),
                "failureKind": response.failure_kind,
            }
        else:
            try:
                result = execute_workspace_query(
                    client,
                    workspace_id,
                    query,
                    request_timeout_seconds=min(
                        request_timeout_seconds,
                        MAX_SERVER_TIMEOUT_SECONDS,
                        max(1, int(remaining)),
                    ),
                    retry_count=retry_count,
                    sleep=sleep,
                    monotonic=monotonic,
                    budget_seconds=max(1, int(remaining)),
                )
            except LogsQueryFailure as exc:
                result = {
                    "status": "failed" if exc.failure_kind == "query" else "blocked",
                    "valid": False,
                    "querySha256": item["querySha256"],
                    "statusCode": exc.status_code,
                    "rowCount": 0,
                    "schema": [],
                    "error": str(exc),
                    "errorDetails": exc.error_details,
                    "failureKind": exc.failure_kind,
                    "attempts": None,
                    "tables": [],
                }
                if exc.failure_kind != "query":
                    stop_family = True
        result.update({
            "detection": detection,
            "querySha256": item["querySha256"],
            "valid": result["status"] == "passed",
            "durationMs": max(0, int((monotonic() - started) * 1000)),
        })
        results.append(result)
    return results
