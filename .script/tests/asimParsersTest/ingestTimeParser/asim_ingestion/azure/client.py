"""Retrying Azure Monitor management, query, upload, and cleanup client."""

from __future__ import annotations

from contextlib import contextmanager
import random
from typing import Any, Mapping, Sequence

import requests

from .common import (
    DCR_API_VERSION,
    INGESTION_API_VERSION,
    INGESTION_SCOPE,
    MANAGEMENT_SCOPE,
    QUERY_SCOPE,
    TABLE_API_VERSION,
    CanaryConfig,
    Clock,
    DcrHandle,
    HarnessError,
    OutcomeUnknownError,
    TokenProvider,
    _compact_json_bytes,
    _normalize_dcr_type,
    _query_timestamp_counts,
    _safe_response_body,
    _validate_timestamp,
    build_exact_timestamp_query,
    build_upload_batches,
    count_rows_by_timestamp,
)

class AzureMonitorClient:
    def __init__(
        self,
        config: CanaryConfig,
        token_provider: TokenProvider,
        *,
        session: requests.Session | None = None,
        clock: Clock | None = None,
        deadline_seconds: float = 900,
        poll_delays: Sequence[float] = (5, 10, 20, 30),
        settling_delay_seconds: float = 5,
        random_source: random.Random | None = None,
    ):
        self.config = config
        self.token_provider = token_provider
        self.session = session or requests.Session()
        self.clock = clock or Clock()
        self.deadline = self.clock.monotonic() + deadline_seconds
        self.poll_delays = tuple(poll_delays)
        self.settling_delay_seconds = settling_delay_seconds
        self.random = random_source or random.Random()
        self.request_attempts: list[dict[str, Any]] = []
        self.stage_timings: dict[str, float] = {}
        self.last_result: dict[str, Any] | None = None

    def _remaining(self) -> float:
        return self.deadline - self.clock.monotonic()

    def _sleep(self, delay: float) -> None:
        remaining = self._remaining()
        if remaining <= 0:
            raise HarnessError("deadline", "Validation deadline expired.")
        self.clock.sleep(min(delay, remaining))

    @contextmanager
    def _stage(self, name: str):
        started = self.clock.monotonic()
        try:
            yield
        finally:
            elapsed = self.clock.monotonic() - started
            self.stage_timings[name] = round(
                self.stage_timings.get(name, 0.0) + elapsed,
                3,
            )

    def _record_request(
        self,
        *,
        stage: str,
        method: str,
        attempt_count: int,
        status_code: int | None,
        error: str | None = None,
    ) -> None:
        entry: dict[str, Any] = {
            "stage": stage,
            "method": method,
            "attemptCount": attempt_count,
            "statusCode": status_code,
        }
        if error is not None:
            entry["error"] = error[:500]
        self.request_attempts.append(entry)

    def _auth_headers(self, scope: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token_provider.get_token(scope)}",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        url: str,
        *,
        scope: str,
        stage: str,
        json_body: Any = None,
        idempotent: bool = True,
        accepted_statuses: set[int] | None = None,
        max_attempts: int = 3,
    ) -> requests.Response:
        accepted = accepted_statuses or {200}
        attempt = 0
        while True:
            if self._remaining() <= 0:
                raise HarnessError(
                    stage, "Validation deadline expired."
                )
            attempt += 1
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=self._auth_headers(scope),
                    json=json_body,
                    timeout=max(1, min(60, int(self._remaining()))),
                )
            except requests.RequestException as exc:
                if not idempotent or attempt >= max_attempts:
                    self._record_request(
                        stage=stage,
                        method=method,
                        attempt_count=attempt,
                        status_code=None,
                        error=str(exc),
                    )
                    raise HarnessError(
                        stage,
                        f"{method} request failed: {exc}",
                    ) from exc
                self._sleep(min(2**attempt, 10))
                continue

            if response.status_code in accepted:
                self._record_request(
                    stage=stage,
                    method=method,
                    attempt_count=attempt,
                    status_code=response.status_code,
                )
                return response
            if response.status_code in {400, 401, 403}:
                self._record_request(
                    stage=stage,
                    method=method,
                    attempt_count=attempt,
                    status_code=response.status_code,
                )
                raise HarnessError(
                    stage,
                    f"{method} failed with HTTP {response.status_code}.",
                    status_code=response.status_code,
                    details=_safe_response_body(response),
                )
            if (
                idempotent
                and response.status_code == 429
                and attempt < max_attempts
            ):
                retry_after = response.headers.get("Retry-After", "1")
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = 1
                self._sleep(delay)
                continue
            if (
                idempotent
                and 500 <= response.status_code < 600
                and attempt < max_attempts
            ):
                jitter = self.random.uniform(0, 0.5)
                self._sleep(min(2**attempt + jitter, 10))
                continue
            self._record_request(
                stage=stage,
                method=method,
                attempt_count=attempt,
                status_code=response.status_code,
            )
            raise HarnessError(
                stage,
                f"{method} failed with HTTP {response.status_code}.",
                status_code=response.status_code,
                details=_safe_response_body(response),
            )

    def _management_url(self, resource_path: str, api_version: str) -> str:
        return (
            "https://management.azure.com"
            f"{resource_path}?api-version={api_version}"
        )

    def ensure_raw_table(
        self, table_name: str, schema: Sequence[Mapping[str, str]]
    ) -> None:
        if not table_name.lower().endswith("_cl"):
            return
        resource_path = (
            f"{self.config.workspace_resource_id}/tables/{table_name}"
        )
        body = {
            "properties": {
                "schema": {
                    "name": table_name,
                    "columns": [
                        {
                            "name": column["name"],
                            "type": _normalize_dcr_type(column["type"]),
                        }
                        for column in schema
                    ],
                },
                "retentionInDays": 30,
                "totalRetentionInDays": 30,
            }
        }
        self._request(
            "PUT",
            self._management_url(resource_path, TABLE_API_VERSION),
            scope=MANAGEMENT_SCOPE,
            stage="raw-table",
            json_body=body,
            accepted_statuses={200, 201, 202},
        )
        self._poll_resource_succeeded(
            resource_path, TABLE_API_VERSION, "raw-table"
        )

    def _poll_resource_succeeded(
        self, resource_path: str, api_version: str, stage: str
    ) -> dict[str, Any]:
        poll_index = 0
        while True:
            response = self._request(
                "GET",
                self._management_url(resource_path, api_version),
                scope=MANAGEMENT_SCOPE,
                stage=stage,
                accepted_statuses={200, 404},
            )
            if response.status_code == 404:
                delay = self.poll_delays[
                    min(poll_index, len(self.poll_delays) - 1)
                ]
                poll_index += 1
                self._sleep(delay)
                continue
            body = _safe_response_body(response)
            if not isinstance(body, dict):
                raise HarnessError(
                    stage, "Azure returned an invalid resource response."
                )
            properties = body.get("properties")
            state = (
                properties.get("provisioningState")
                if isinstance(properties, dict)
                else None
            )
            if state in {None, "Succeeded"}:
                return body
            if state in {"Failed", "Canceled"}:
                raise HarnessError(
                    stage,
                    f"Azure resource provisioning entered {state}.",
                    details=body,
                )
            delay = self.poll_delays[
                min(poll_index, len(self.poll_delays) - 1)
            ]
            poll_index += 1
            self._sleep(delay)

    def create_dcr(
        self,
        *,
        name: str,
        stream_name: str,
        destination_name: str,
        schema: Sequence[Mapping[str, str]],
        transform_kql: str,
        output_stream: str,
    ) -> DcrHandle:
        resource_path = self.dcr_resource_id(name)
        body = {
            "location": self.config.location,
            "properties": {
                "streamDeclarations": {
                    stream_name: {
                        "columns": [
                            {
                                "name": column["name"],
                                "type": _normalize_dcr_type(
                                    column["type"]
                                ),
                            }
                            for column in schema
                        ]
                    }
                },
                "dataCollectionEndpointId": self.config.dce_resource_id,
                "dataSources": {},
                "destinations": {
                    "logAnalytics": [
                        {
                            "workspaceResourceId":
                                self.config.workspace_resource_id,
                            "workspaceId": self.config.workspace_id,
                            "name": destination_name,
                        }
                    ]
                },
                "dataFlows": [
                    {
                        "streams": [stream_name],
                        "destinations": [destination_name],
                        "transformKql": transform_kql,
                        "outputStream": output_stream,
                    }
                ],
            },
        }
        self._request(
            "PUT",
            self._management_url(resource_path, DCR_API_VERSION),
            scope=MANAGEMENT_SCOPE,
            stage="dcr-create",
            json_body=body,
            accepted_statuses={200, 201, 202},
        )
        resource = self._poll_resource_succeeded(
            resource_path, DCR_API_VERSION, "dcr-provisioning"
        )
        properties = resource.get("properties", {})
        immutable_id = properties.get("immutableId")
        if not isinstance(immutable_id, str) or not immutable_id:
            raise HarnessError(
                "dcr-provisioning",
                "Azure DCR response is missing immutableId.",
                details=resource,
            )
        resource_id = resource.get("id", resource_path)
        return DcrHandle(
            name=name,
            resource_id=resource_id,
            immutable_id=immutable_id,
            stream_name=stream_name,
            output_stream=output_stream,
        )

    def dcr_resource_id(self, name: str) -> str:
        return (
            f"/subscriptions/{self.config.subscription_id}/resourceGroups/"
            f"{self.config.resource_group}/providers/"
            f"Microsoft.Insights/dataCollectionRules/{name}"
        )

    def delete_dcr(
        self, handle_or_resource_id: DcrHandle | str
    ) -> dict[str, Any]:
        resource_id = (
            handle_or_resource_id.resource_id
            if isinstance(handle_or_resource_id, DcrHandle)
            else handle_or_resource_id
        )
        url = self._management_url(resource_id, DCR_API_VERSION)
        try:
            for attempt in range(2):
                try:
                    response = self.session.request(
                        "DELETE",
                        url,
                        headers=self._auth_headers(MANAGEMENT_SCOPE),
                        timeout=30,
                    )
                except requests.RequestException as exc:
                    if attempt == 0:
                        self.clock.sleep(1)
                        continue
                    raise HarnessError(
                        "cleanup",
                        f"DELETE request failed: {exc}",
                    ) from exc
                if response.status_code in {200, 202, 204, 404}:
                    return {
                        "resourceId": resource_id,
                        "status": "deleted"
                        if response.status_code != 404
                        else "not-found",
                        "attemptCount": attempt + 1,
                    }
                if (
                    (response.status_code == 429
                     or 500 <= response.status_code < 600)
                    and attempt == 0
                ):
                    retry_after = response.headers.get(
                        "Retry-After", "1"
                    )
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        delay = 1
                    self.clock.sleep(min(delay, 5))
                    continue
                raise HarnessError(
                    "cleanup",
                    f"DELETE failed with HTTP {response.status_code}.",
                    status_code=response.status_code,
                    details=_safe_response_body(response),
                )
            raise AssertionError("Cleanup retry loop did not return.")
        except Exception as exc:
            return {
                "resourceId": resource_id,
                "status": "warning",
                "message": str(exc),
                "attemptCount": 2,
                "statusCode": (
                    exc.status_code
                    if isinstance(exc, HarnessError)
                    else None
                ),
            }

    def query_kql(
        self, query: str, *, stage: str = "query"
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            (
                "https://api.loganalytics.io/v1/workspaces/"
                f"{self.config.workspace_id}/query"
            ),
            scope=QUERY_SCOPE,
            stage=stage,
            json_body={"query": query},
            accepted_statuses={200},
        )
        body = _safe_response_body(response)
        if not isinstance(body, dict):
            raise HarnessError(
                stage, "Log Analytics returned an invalid response."
            )
        tables = body.get("tables")
        if not isinstance(tables, list) or not tables:
            raise HarnessError(
                stage, "Log Analytics returned no result table."
            )
        if not isinstance(tables[0], dict):
            raise HarnessError(
                stage, "Log Analytics returned an invalid result table."
            )
        return tables[0]

    def query_exact_rows(
        self, table_name: str, timestamps: Sequence[str]
    ) -> dict[str, Any]:
        return self.query_kql(
            build_exact_timestamp_query(table_name, timestamps)
        )

    def wait_for_exact_rows(
        self,
        table_name: str,
        timestamps: Sequence[str],
        expected_counts_by_timestamp: Mapping[str, int],
        *,
        stage: str,
    ) -> dict[str, Any]:
        expected_counts = {
            _validate_timestamp(str(timestamp)): int(count)
            for timestamp, count in expected_counts_by_timestamp.items()
        }
        if set(expected_counts) != {
            _validate_timestamp(value) for value in timestamps
        }:
            raise ValueError(
                "Expected counts must cover the exact timestamp set."
            )
        if any(count < 0 for count in expected_counts.values()):
            raise ValueError("Expected counts cannot be negative.")
        poll_index = 0
        stable_once = False
        while True:
            query_table = self.query_exact_rows(table_name, timestamps)
            raw_observed_counts = _query_timestamp_counts(
                query_table, stage
            )
            unexpected = {
                timestamp: count
                for timestamp, count in raw_observed_counts.items()
                if timestamp not in expected_counts
            }
            if unexpected:
                raise HarnessError(
                    stage,
                    "Exact timestamp query returned unexpected timestamps.",
                    details={"unexpected": unexpected},
                )
            observed_counts = {
                timestamp: raw_observed_counts.get(timestamp, 0)
                for timestamp in expected_counts
            }
            overages = {
                timestamp: {
                    "expected": expected_counts.get(timestamp, 0),
                    "observed": observed,
                }
                for timestamp, observed in observed_counts.items()
                if observed > expected_counts.get(timestamp, 0)
            }
            if overages:
                raise HarnessError(
                    stage,
                    "Exact timestamp slice contains more rows than "
                    "expected for one or more timestamps.",
                    details={"overages": overages},
                )
            if observed_counts == expected_counts:
                if stable_once:
                    return query_table
                stable_once = True
                self._sleep(self.settling_delay_seconds)
                continue
            stable_once = False
            if self._remaining() <= 0:
                raise HarnessError(
                    stage,
                    "Timed out waiting for exact table rows.",
                    details={
                        "expectedCounts": expected_counts,
                        "observedCounts": observed_counts,
                    },
                )
            delay = self.poll_delays[
                min(poll_index, len(self.poll_delays) - 1)
            ]
            poll_index += 1
            self._sleep(delay)

    def upload_rows(
        self,
        handle: DcrHandle,
        rows: Sequence[Mapping[str, Any]],
        *,
        reconcile_table: str | None = None,
        expected_counts_by_timestamp:
            Mapping[str, int] | None = None,
        max_batch_bytes: int = 1_000_000,
    ) -> list[dict[str, Any]]:
        batches = build_upload_batches(rows, max_batch_bytes)
        results: list[dict[str, Any]] = []
        endpoint = self.config.ingestion_endpoint.rstrip("/")
        for batch_index, batch in enumerate(batches):
            if self._remaining() <= 0:
                raise HarnessError(
                    "upload", "Validation deadline expired."
                )
            batch_counts = count_rows_by_timestamp(batch)
            url = (
                f"{endpoint}/dataCollectionRules/{handle.immutable_id}/"
                f"streams/{handle.stream_name}"
                f"?api-version={INGESTION_API_VERSION}"
            )
            try:
                response = self.session.request(
                    "POST",
                    url,
                    headers=self._auth_headers(INGESTION_SCOPE),
                    data=_compact_json_bytes(batch),
                    timeout=max(1, min(60, int(self._remaining()))),
                )
            except requests.RequestException as exc:
                self._reconcile_unknown_upload(
                    reconcile_table,
                    expected_counts_by_timestamp,
                    batch_counts,
                    exc,
                )
                results.append(
                    {
                        "batch": batch_index,
                        "rowCount": len(batch),
                        "status": "reconciled",
                        "attemptCount": 1,
                    }
                )
                continue

            if response.status_code in {200, 202, 204}:
                results.append(
                    {
                        "batch": batch_index,
                        "rowCount": len(batch),
                        "status": "accepted",
                        "attemptCount": 1,
                    }
                )
                continue
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "1")
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = 1
                self._sleep(delay)
                try:
                    retry_response = self.session.request(
                        "POST",
                        url,
                        headers=self._auth_headers(INGESTION_SCOPE),
                        data=_compact_json_bytes(batch),
                        timeout=max(
                            1, min(60, int(self._remaining()))
                        ),
                    )
                except requests.RequestException as exc:
                    self._reconcile_unknown_upload(
                        reconcile_table,
                        expected_counts_by_timestamp,
                        batch_counts,
                        exc,
                    )
                    results.append(
                        {
                            "batch": batch_index,
                            "rowCount": len(batch),
                            "status": "reconciled-after-retry",
                            "attemptCount": 2,
                        }
                    )
                    continue
                if retry_response.status_code in {200, 202, 204}:
                    results.append(
                        {
                            "batch": batch_index,
                            "rowCount": len(batch),
                            "status": "accepted-after-retry",
                            "attemptCount": 2,
                        }
                    )
                    continue
                response = retry_response
            raise HarnessError(
                "upload",
                f"Upload failed with HTTP {response.status_code}.",
                status_code=response.status_code,
                details=_safe_response_body(response),
            )
        return results

    def _reconcile_unknown_upload(
        self,
        reconcile_table: str | None,
        expected_counts_by_timestamp: Mapping[str, int] | None,
        batch_counts: Mapping[str, int],
        cause: Exception,
    ) -> None:
        if (
            reconcile_table is None
            or expected_counts_by_timestamp is None
        ):
            raise OutcomeUnknownError(
                "upload",
                "Upload outcome is unknown and cannot be reconciled "
                "without expected target counts.",
            ) from cause
        expected_count = sum(
            expected_counts_by_timestamp.get(timestamp, 0)
            for timestamp in batch_counts
        )
        if expected_count <= 0:
            raise OutcomeUnknownError(
                "upload",
                "Upload outcome is unknown and zero expected output "
                "cannot prove whether the request was accepted.",
            ) from cause
        self.wait_for_exact_rows(
            reconcile_table,
            list(batch_counts),
            {
                timestamp: expected_counts_by_timestamp.get(
                    timestamp, 0
                )
                for timestamp in batch_counts
            },
            stage="upload-reconciliation",
        )
