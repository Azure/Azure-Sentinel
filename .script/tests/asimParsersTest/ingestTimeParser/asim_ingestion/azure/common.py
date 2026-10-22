"""Azure configuration, result models, exact-slice queries, and artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
from collections import Counter, OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

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
        raise NotImplementedError


class ValidationRunner(Protocol):
    def evaluate_filter(
        self,
        query_client: Any,
        source_snapshot: Mapping[str, Any],
        parser_document: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        raise NotImplementedError

    def validate_outputs(
        self,
        query_client: Any,
        source_snapshot: Mapping[str, Any],
        parser_document: Mapping[str, Any],
        query_time_document: Mapping[str, Any] | None,
    ) -> Mapping[str, Any]:
        raise NotImplementedError


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
