#!/usr/bin/env python3
"""Execute prepared ASIM fixtures through raw and parser DCRs.

This helper is intentionally workflow-agnostic. It consumes the immutable
artifact emitted by ``asim_fixture_preparation.py`` and an ingestion-time
parser YAML, then:

1. provisions a custom raw table when required;
2. creates a pass-through raw-ingestion DCR;
3. uploads and reconciles the prepared fixture;
4. queries the exact raw-table timestamp slice into a source snapshot;
5. creates a parser DCR containing the exact ParserQuery;
6. uploads the source snapshot; and
7. attempts idempotent DCR cleanup.

The later validation stage supplies expected parser-output counts and performs
ASIM data/parity validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import tempfile
import time
from collections import Counter, OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

import requests
import yaml


HARNESS_RESULT_VERSION = 1
SNAPSHOT_VERSION = 1

MANAGEMENT_SCOPE = "https://management.azure.com/.default"
QUERY_SCOPE = "https://api.loganalytics.io/.default"
INGESTION_SCOPE = "https://monitor.azure.com/.default"

DCR_API_VERSION = "2022-06-01"
TABLE_API_VERSION = "2022-10-01"
INGESTION_API_VERSION = "2023-01-01"

DEFAULT_SUBSCRIPTION_ID = "419581d6-4853-49bd-83b6-d94bb8a77887"
DEFAULT_RESOURCE_GROUP = "asim-schemadatatester-githubshared-canary"
DEFAULT_WORKSPACE_NAME = "ASIM-SchemaDataTester-GithubShared-Canary"
DEFAULT_WORKSPACE_ID = "cb6a2b4f-7073-4e59-9ab0-803cde6b2221"
DEFAULT_DCE_NAME = "ASIM-SchemaDataTester-GithubShared-Canary"
DEFAULT_INGESTION_ENDPOINT = (
    "https://asim-schemadatatester-githubshared-canary-qa1f."
    "eastus2euap-1.canary.ingest.monitor.azure.com"
)
DEFAULT_LOCATION = "eastus2euap"

IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
RESOURCE_NAME_RE = re.compile(r"[^a-z0-9-]+")
KUSTO_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{7}Z$"
)

REPLAY_EXCLUDED_COLUMNS = {
    "_BilledSize",
    "_IsBillable",
    "_ItemId",
    "_ResourceId",
    "_SubscriptionId",
    "_TimeReceived",
}


class HarnessError(RuntimeError):
    def __init__(
        self,
        stage: str,
        message: str,
        *,
        status_code: int | None = None,
        details: Any = None,
    ):
        super().__init__(message)
        self.stage = stage
        self.status_code = status_code
        self.details = details


class OutcomeUnknownError(HarnessError):
    pass


class TokenProvider(Protocol):
    def get_token(self, scope: str) -> str:
        ...


class DefaultAzureTokenProvider:
    def __init__(self):
        from azure.identity import DefaultAzureCredential

        self._credential = DefaultAzureCredential()

    def get_token(self, scope: str) -> str:
        return self._credential.get_token(scope).token


class Clock:
    def monotonic(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


@dataclass(frozen=True)
class CanaryConfig:
    subscription_id: str = DEFAULT_SUBSCRIPTION_ID
    resource_group: str = DEFAULT_RESOURCE_GROUP
    workspace_name: str = DEFAULT_WORKSPACE_NAME
    workspace_id: str = DEFAULT_WORKSPACE_ID
    dce_name: str = DEFAULT_DCE_NAME
    ingestion_endpoint: str = DEFAULT_INGESTION_ENDPOINT
    location: str = DEFAULT_LOCATION

    @property
    def workspace_resource_id(self) -> str:
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/"
            f"{self.resource_group}/providers/"
            f"Microsoft.OperationalInsights/workspaces/"
            f"{self.workspace_name}"
        )

    @property
    def dce_resource_id(self) -> str:
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/"
            f"{self.resource_group}/providers/"
            f"Microsoft.Insights/dataCollectionEndpoints/{self.dce_name}"
        )


@dataclass(frozen=True)
class DcrHandle:
    name: str
    resource_id: str
    immutable_id: str
    stream_name: str
    output_stream: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "resourceId": self.resource_id,
            "immutableId": self.immutable_id,
            "streamName": self.stream_name,
            "outputStream": self.output_stream,
        }


def _require_identifier(value: str, field: str) -> str:
    if not IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"{field} must be a KQL identifier: {value}")
    return value


def _validate_timestamp(value: str) -> str:
    if not KUSTO_TIMESTAMP_RE.fullmatch(value):
        raise ValueError(
            f"Expected exact Kusto timestamp with seven digits: {value}"
        )
    return value


def _compact_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _safe_response_body(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        text = response.text.strip()
        return text[:2000] if text else None


def _normalize_dcr_type(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {
        "bool": "boolean",
        "boolean": "boolean",
        "datetime": "datetime",
        "dynamic": "dynamic",
        "guid": "string",
        "int": "int",
        "integer": "int",
        "long": "long",
        "real": "real",
        "double": "real",
        "float": "real",
        "string": "string",
    }
    if normalized not in aliases:
        raise ValueError(f"Unsupported DCR stream type: {value}")
    return aliases[normalized]


def _json_safe_value(value: Any, column_type: str) -> Any:
    if value is None:
        return None
    if column_type == "datetime" and isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        return value.isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
    if column_type == "dynamic" and isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def build_exact_timestamp_query(
    table_name: str, timestamps: Sequence[str]
) -> str:
    _require_identifier(table_name, "table_name")
    unique_timestamps = sorted({_validate_timestamp(value) for value in timestamps})
    if not unique_timestamps:
        raise ValueError("At least one timestamp is required.")
    values = ",\n    ".join(
        f"datetime({timestamp})" for timestamp in unique_timestamps
    )
    return (
        "let TestTimes = datatable(_AsimTestTime:datetime) [\n"
        f"    {values}\n"
        "];\n"
        f"{table_name}\n"
        "| join kind=inner TestTimes on "
        "$left.TimeGenerated == $right._AsimTestTime\n"
        "| project-away _AsimTestTime"
    )


def _normalize_query_columns(
    columns: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    schema: list[dict[str, str]] = []
    seen: set[str] = set()
    for column in columns:
        name = column.get("name")
        column_type = column.get("type")
        if not isinstance(name, str) or not isinstance(column_type, str):
            raise HarnessError(
                "query",
                "Log Analytics returned an invalid column definition.",
                details=column,
            )
        if name in seen:
            raise HarnessError(
                "query", f"Log Analytics returned duplicate column {name}."
            )
        seen.add(name)
        schema.append(
            {"name": name, "type": _normalize_dcr_type(column_type)}
        )
    return schema


def build_source_snapshot(
    *,
    target_id: str,
    table_name: str,
    timestamps: Sequence[str],
    query_table: Mapping[str, Any],
) -> dict[str, Any]:
    columns = query_table.get("columns")
    raw_rows = query_table.get("rows")
    if not isinstance(columns, list) or not isinstance(raw_rows, list):
        raise HarnessError(
            "source-snapshot",
            "Log Analytics query response must contain columns and rows.",
        )
    query_schema = _normalize_query_columns(columns)
    column_names = [column["name"] for column in query_schema]
    if any(not isinstance(row, list) for row in raw_rows):
        raise HarnessError(
            "source-snapshot", "Query rows must be arrays."
        )

    included_schema = [
        column
        for column in query_schema
        if column["name"] not in REPLAY_EXCLUDED_COLUMNS
    ]
    included_names = [column["name"] for column in included_schema]
    type_by_name = {
        column["name"]: column["type"] for column in included_schema
    }
    timestamp_set = {_validate_timestamp(value) for value in timestamps}
    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        if len(row) != len(column_names):
            raise HarnessError(
                "source-snapshot",
                "Query row length does not match the returned schema.",
            )
        source = dict(zip(column_names, row))
        prepared = {
            name: _json_safe_value(source.get(name), type_by_name[name])
            for name in included_names
        }
        timestamp = prepared.get("TimeGenerated")
        if not isinstance(timestamp, str) or timestamp not in timestamp_set:
            raise HarnessError(
                "source-snapshot",
                "Query returned a row outside the exact timestamp set.",
                details={"TimeGenerated": timestamp},
            )
        rows.append(prepared)

    timestamp_hash = hashlib.sha256(
        "\n".join(sorted(timestamp_set)).encode("utf-8")
    ).hexdigest()
    return {
        "version": SNAPSHOT_VERSION,
        "targetId": target_id,
        "sourceRawTable": table_name,
        "rowCount": len(rows),
        "timestampValues": sorted(timestamp_set),
        "timestampSetHash": f"sha256:{timestamp_hash}",
        "excludedColumns": sorted(
            set(column_names) & REPLAY_EXCLUDED_COLUMNS
        ),
        "schema": included_schema,
        "rows": rows,
    }


def count_rows_by_timestamp(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        timestamp = row.get("TimeGenerated")
        if not isinstance(timestamp, str):
            raise ValueError("Every upload row must contain TimeGenerated.")
        counts[_validate_timestamp(timestamp)] += 1
    return dict(counts)


def _query_timestamp_counts(
    query_table: Mapping[str, Any], stage: str
) -> dict[str, int]:
    columns = query_table.get("columns")
    rows = query_table.get("rows")
    if not isinstance(columns, list) or not isinstance(rows, list):
        raise HarnessError(
            stage, "Log Analytics result must contain columns and rows."
        )
    column_names = [
        column.get("name") if isinstance(column, dict) else None
        for column in columns
    ]
    try:
        timestamp_index = column_names.index("TimeGenerated")
    except ValueError as exc:
        raise HarnessError(
            stage,
            "Log Analytics result does not contain TimeGenerated.",
        ) from exc
    counts: Counter[str] = Counter()
    for row in rows:
        if not isinstance(row, list) or timestamp_index >= len(row):
            raise HarnessError(stage, "Log Analytics row shape is invalid.")
        timestamp = row[timestamp_index]
        if not isinstance(timestamp, str):
            raise HarnessError(
                stage, "TimeGenerated must be returned as a string."
            )
        counts[_validate_timestamp(timestamp)] += 1
    return dict(counts)


def build_upload_batches(
    rows: Sequence[Mapping[str, Any]],
    max_bytes: int = 1_000_000,
) -> list[list[dict[str, Any]]]:
    if max_bytes < 3:
        raise ValueError("max_bytes is too small for a JSON array.")
    grouped_rows: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for input_row in rows:
        row = dict(input_row)
        timestamp = row.get("TimeGenerated")
        if not isinstance(timestamp, str):
            raise ValueError("Every upload row must contain TimeGenerated.")
        _validate_timestamp(timestamp)
        grouped_rows.setdefault(timestamp, []).append(row)

    batches: list[list[dict[str, Any]]] = []
    current_batch: list[dict[str, Any]] = []
    for group in grouped_rows.values():
        if len(_compact_json_bytes(group)) > max_bytes:
            raise ValueError(
                "Rows sharing one TimeGenerated value exceed the upload "
                "request limit and cannot be split safely."
            )
        candidate = current_batch + group
        if current_batch and len(_compact_json_bytes(candidate)) > max_bytes:
            batches.append(current_batch)
            current_batch = list(group)
        else:
            current_batch = candidate
    if current_batch:
        batches.append(current_batch)
    return batches


def _write_json_no_clobber(
    payload: Mapping[str, Any], output_path: Path
) -> None:
    serialized = (
        json.dumps(
            payload, indent=2, sort_keys=True, ensure_ascii=True
        )
        + "\n"
    ).encode("utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        if output_path.read_bytes() == serialized:
            return
        raise ValueError(
            f"Refusing to overwrite existing artifact: {output_path}"
        )
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            dir=output_path.parent,
            delete=False,
        ) as temporary:
            temporary.write(serialized)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        try:
            os.link(temporary_path, output_path)
        except FileExistsError:
            if output_path.read_bytes() != serialized:
                raise ValueError(
                    f"Artifact was created concurrently: {output_path}"
                )
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _load_json_object(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return document


def _load_parser_yaml(path: Path) -> dict[str, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a YAML mapping.")
    required = (
        "ParserName",
        "SourceRawTable",
        "TargetASIMTable",
        "ParserQuery",
    )
    for field in required:
        if not isinstance(document.get(field), str) or not document[field].strip():
            raise ValueError(f"{path} is missing {field}.")
    return document


def _resource_slug(value: str, max_length: int = 24) -> str:
    normalized = RESOURCE_NAME_RE.sub(
        "-", value.lower()
    ).strip("-")
    return normalized[:max_length] or "target"


def build_resource_names(
    target_id: str,
    pull_request: str,
    run_id: str,
    run_attempt: int,
) -> dict[str, str]:
    identity = "|".join(
        (target_id, str(pull_request), str(run_id), str(run_attempt))
    )
    suffix = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:10]
    prefix = (
        f"asimv-{pull_request}-{str(run_id)[-6:]}-"
        f"{run_attempt}-{_resource_slug(target_id)}-{suffix}"
    )[:58].rstrip("-")
    return {
        "rawDcr": f"{prefix}-raw",
        "parserDcr": f"{prefix}-it",
        "rawStream": f"Custom-asimv-{suffix}-raw",
        "parserStream": f"Custom-asimv-{suffix}-it",
        "destination": f"asimv-{suffix}",
    }


class AsimIngestionHarness:
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

    def _remaining(self) -> float:
        return self.deadline - self.clock.monotonic()

    def _sleep(self, delay: float) -> None:
        remaining = self._remaining()
        if remaining <= 0:
            raise HarnessError("deadline", "Validation deadline expired.")
        self.clock.sleep(min(delay, remaining))

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
                    raise HarnessError(
                        stage,
                        f"{method} request failed: {exc}",
                    ) from exc
                self._sleep(min(2**attempt, 10))
                continue

            if response.status_code in accepted:
                return response
            if response.status_code in {400, 401, 403}:
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
                "statusCode": (
                    exc.status_code
                    if isinstance(exc, HarnessError)
                    else None
                ),
            }

    def query_exact_rows(
        self, table_name: str, timestamps: Sequence[str]
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            (
                "https://api.loganalytics.io/v1/workspaces/"
                f"{self.config.workspace_id}/query"
            ),
            scope=QUERY_SCOPE,
            stage="query",
            json_body={
                "query": build_exact_timestamp_query(
                    table_name, timestamps
                )
            },
            accepted_statuses={200},
        )
        body = _safe_response_body(response)
        if not isinstance(body, dict):
            raise HarnessError(
                "query", "Log Analytics returned an invalid response."
            )
        tables = body.get("tables")
        if not isinstance(tables, list) or not tables:
            raise HarnessError(
                "query", "Log Analytics returned no result table."
            )
        if not isinstance(tables[0], dict):
            raise HarnessError(
                "query", "Log Analytics returned an invalid result table."
            )
        return tables[0]

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
                    }
                )
                continue

            if response.status_code in {200, 202, 204}:
                results.append(
                    {
                        "batch": batch_index,
                        "rowCount": len(batch),
                        "status": "accepted",
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
                        }
                    )
                    continue
                if retry_response.status_code in {200, 202, 204}:
                    results.append(
                        {
                            "batch": batch_index,
                            "rowCount": len(batch),
                            "status": "accepted-after-retry",
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

    def run(
        self,
        prepared_fixture: Mapping[str, Any],
        parser_document: Mapping[str, Any],
        *,
        snapshot_output: Path,
        expected_target_counts: Mapping[str, int],
    ) -> dict[str, Any]:
        target_id = str(prepared_fixture["targetId"])
        namespace = prepared_fixture["namespace"]
        source_table = str(prepared_fixture["sourceRawTable"])
        target_table = str(parser_document["TargetASIMTable"])
        parser_query = str(parser_document["ParserQuery"])
        if str(parser_document["SourceRawTable"]) != source_table:
            raise ValueError(
                "Prepared fixture SourceRawTable does not match parser."
            )
        timestamps = list(namespace["timestampValues"])
        rows = list(prepared_fixture["rows"])
        schema = list(prepared_fixture["schema"])
        if len(rows) != int(prepared_fixture["rowCount"]):
            raise ValueError("Prepared fixture rowCount does not match rows.")
        if set(count_rows_by_timestamp(rows)) != set(timestamps):
            raise ValueError(
                "Prepared fixture timestamps do not match its namespace."
            )
        normalized_target_counts = {
            _validate_timestamp(str(timestamp)): int(count)
            for timestamp, count in expected_target_counts.items()
        }
        if set(normalized_target_counts) != set(timestamps):
            raise ValueError(
                "Expected target counts must include every prepared "
                "timestamp exactly once."
            )
        if any(count < 0 for count in normalized_target_counts.values()):
            raise ValueError(
                "Expected target counts cannot contain negative values."
            )

        names = build_resource_names(
            target_id,
            str(namespace.get("pullRequest", "0")),
            str(namespace["runId"]),
            int(namespace["runAttempt"]),
        )
        raw_handle: DcrHandle | None = None
        parser_handle: DcrHandle | None = None
        attempted_dcr_ids: list[str] = []
        cleanup: list[dict[str, Any]] = []
        result: dict[str, Any] = {
            "version": HARNESS_RESULT_VERSION,
            "targetId": target_id,
            "sourceRawTable": source_table,
            "targetASIMTable": target_table,
            "rawDcr": None,
            "parserDcr": None,
            "rawUpload": [],
            "parserUpload": [],
            "snapshotPath": str(snapshot_output),
            "cleanup": cleanup,
        }
        try:
            self.ensure_raw_table(source_table, schema)
            raw_resource_id = self.dcr_resource_id(names["rawDcr"])
            attempted_dcr_ids.append(raw_resource_id)
            raw_handle = self.create_dcr(
                name=names["rawDcr"],
                stream_name=names["rawStream"],
                destination_name=names["destination"],
                schema=schema,
                transform_kql="source",
                output_stream=(
                    f"Custom-{source_table}"
                    if source_table.lower().endswith("_cl")
                    else f"Microsoft-{source_table}"
                ),
            )
            result["rawDcr"] = raw_handle.to_dict()
            raw_counts = count_rows_by_timestamp(rows)
            result["rawUpload"] = self.upload_rows(
                raw_handle,
                rows,
                reconcile_table=source_table,
                expected_counts_by_timestamp=raw_counts,
            )
            raw_query_table = self.wait_for_exact_rows(
                source_table,
                timestamps,
                raw_counts,
                stage="raw-visibility",
            )
            snapshot = build_source_snapshot(
                target_id=target_id,
                table_name=source_table,
                timestamps=timestamps,
                query_table=raw_query_table,
            )
            _write_json_no_clobber(snapshot, snapshot_output)
            result["snapshot"] = {
                "rowCount": snapshot["rowCount"],
                "timestampSetHash": snapshot["timestampSetHash"],
                "excludedColumns": snapshot["excludedColumns"],
            }

            parser_resource_id = self.dcr_resource_id(
                names["parserDcr"]
            )
            attempted_dcr_ids.append(parser_resource_id)
            parser_handle = self.create_dcr(
                name=names["parserDcr"],
                stream_name=names["parserStream"],
                destination_name=names["destination"],
                schema=snapshot["schema"],
                transform_kql=parser_query,
                output_stream=f"Microsoft-{target_table}",
            )
            result["parserDcr"] = parser_handle.to_dict()
            result["parserUpload"] = self.upload_rows(
                parser_handle,
                snapshot["rows"],
                reconcile_table=target_table,
                expected_counts_by_timestamp=normalized_target_counts,
            )
            self.wait_for_exact_rows(
                target_table,
                list(normalized_target_counts),
                normalized_target_counts,
                stage="target-visibility",
            )
            result["status"] = "completed"
            return result
        finally:
            for resource_id in reversed(attempted_dcr_ids):
                cleanup.append(self.delete_dcr(resource_id))


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared_fixture", type=Path)
    parser.add_argument("parser_yaml", type=Path)
    parser.add_argument("--snapshot-output", type=Path, required=True)
    parser.add_argument("--result-output", type=Path)
    parser.add_argument(
        "--expected-target-counts", type=Path, required=True
    )
    parser.add_argument(
        "--deadline-seconds", type=float, default=900
    )
    parser.add_argument(
        "--subscription-id",
        default=os.getenv(
            "ASIM_CANARY_SUBSCRIPTION_ID",
            DEFAULT_SUBSCRIPTION_ID,
        ),
    )
    parser.add_argument(
        "--resource-group",
        default=os.getenv(
            "ASIM_CANARY_RESOURCE_GROUP",
            DEFAULT_RESOURCE_GROUP,
        ),
    )
    parser.add_argument(
        "--workspace-name",
        default=os.getenv(
            "ASIM_CANARY_WORKSPACE_NAME",
            DEFAULT_WORKSPACE_NAME,
        ),
    )
    parser.add_argument(
        "--workspace-id",
        default=os.getenv(
            "ASIM_CANARY_WORKSPACE_ID",
            DEFAULT_WORKSPACE_ID,
        ),
    )
    parser.add_argument(
        "--dce-name",
        default=os.getenv("ASIM_CANARY_DCE_NAME", DEFAULT_DCE_NAME),
    )
    parser.add_argument(
        "--ingestion-endpoint",
        default=os.getenv(
            "ASIM_CANARY_INGESTION_ENDPOINT",
            DEFAULT_INGESTION_ENDPOINT,
        ),
    )
    parser.add_argument(
        "--location",
        default=os.getenv(
            "ASIM_CANARY_LOCATION", DEFAULT_LOCATION
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    result: dict[str, Any] = {
        "version": HARNESS_RESULT_VERSION,
        "status": "failed",
        "cleanup": [],
    }
    exit_code = 1
    try:
        prepared_fixture = _load_json_object(args.prepared_fixture)
        parser_document = _load_parser_yaml(args.parser_yaml)
        expected_counts = _load_json_object(
            args.expected_target_counts
        )
        config = CanaryConfig(
            subscription_id=args.subscription_id,
            resource_group=args.resource_group,
            workspace_name=args.workspace_name,
            workspace_id=args.workspace_id,
            dce_name=args.dce_name,
            ingestion_endpoint=args.ingestion_endpoint,
            location=args.location,
        )
        harness = AsimIngestionHarness(
            config,
            DefaultAzureTokenProvider(),
            deadline_seconds=args.deadline_seconds,
        )
        result = harness.run(
            prepared_fixture,
            parser_document,
            snapshot_output=args.snapshot_output,
            expected_target_counts=expected_counts,
        )
        exit_code = 0
    except (HarnessError, OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        result["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
        if isinstance(exc, HarnessError):
            result["error"].update(
                {
                    "stage": exc.stage,
                    "statusCode": exc.status_code,
                    "details": exc.details,
                }
            )
        print(f"::error::{exc}", file=sys.stderr)
    if args.result_output is not None:
        _write_json_no_clobber(result, args.result_output)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
