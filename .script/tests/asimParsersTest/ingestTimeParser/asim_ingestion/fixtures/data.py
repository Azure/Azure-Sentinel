"""Fixture CSV loading, schema resolution, conversion, and artifact writing."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from .timestamps import (
    TimestampNamespace,
    build_run_key,
    datetime_to_ticks,
    parse_kusto_datetime_ticks,
    rebase_time_generated,
    ticks_to_kusto_datetime,
    timestamp_quantum_for_target_count,
)

ARTIFACT_VERSION = 1
MAX_FIXTURE_BYTES = 5 * 1024 * 1024
MAX_SCHEMA_BYTES = 1024 * 1024
RESERVED_COLUMNS = {
    "_ItemId", "_ResourceId", "_ResourceId_s", "_SubscriptionId",
    "id", "MG", "TenantId", "Title", "Type", "UniqueId",
    "verbose", "verbose_b",
}
INTEGER_RE = re.compile(r"^-?(?:0|[1-9]\d*)$")
REAL_RE = re.compile(
    r"^-?(?:(?:0|[1-9]\d*)\.\d+|(?:0|[1-9]\d*)[eE][+-]?\d+|"
    r"(?:0|[1-9]\d*)\.\d+[eE][+-]?\d+)$"
)
STRING_LIKE_COLUMN_RE = re.compile(
    r"(?:^|_)(?:id|identifier|version)$|(?:Id|ID|Guid|Version)$"
)
INT32_MIN = -(2**31)
INT32_MAX = 2**31 - 1
INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1

def _normalized_column_name(column_name: str) -> tuple[str, bool]:
    for suffix in (" [UTC]", " [Local Time]"):
        if column_name.endswith(suffix):
            return column_name[: -len(suffix)], True
    return column_name, False


def load_fixture_csv(
    path: Path,
) -> tuple[list[dict[str, str]], str, set[str]]:
    if path.stat().st_size > MAX_FIXTURE_BYTES:
        raise ValueError(
            f"{path} exceeds the {MAX_FIXTURE_BYTES}-byte fixture limit."
        )
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"{path} has no CSV header.")

        renamed_fields: list[str] = []
        datetime_columns: set[str] = set()
        field_mapping: dict[str, str] = {}
        for original_name in reader.fieldnames:
            normalized_name, is_datetime = _normalized_column_name(
                original_name
            )
            if normalized_name in renamed_fields:
                raise ValueError(
                    f"{path} has duplicate column '{normalized_name}' "
                    "after timestamp suffix normalization."
                )
            renamed_fields.append(normalized_name)
            field_mapping[original_name] = normalized_name
            if is_datetime:
                datetime_columns.add(normalized_name)

        if "Type" not in renamed_fields:
            raise ValueError(f"{path} must contain a Type column.")
        if "TimeGenerated" not in renamed_fields:
            raise ValueError(f"{path} must contain TimeGenerated.")
        datetime_columns.add("TimeGenerated")

        rows: list[dict[str, str]] = []
        table_names: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            normalized_row = {
                field_mapping[key]: value
                for key, value in row.items()
                if key is not None
            }
            table_name = normalized_row.get("Type", "").strip()
            if not table_name:
                raise ValueError(
                    f"{path} row {row_number} has an empty Type value."
                )
            table_names.add(table_name)
            rows.append(normalized_row)

    if not rows:
        raise ValueError(f"{path} contains no data rows.")
    if len(table_names) != 1:
        raise ValueError(
            f"{path} contains multiple Type values: {sorted(table_names)}"
        )
    return rows, next(iter(table_names)), datetime_columns


def _normalize_schema_type(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {
        "bool": "boolean",
        "double": "real",
        "float": "real",
        "int16": "int",
        "int32": "int",
        "int64": "long",
        "integer": "int",
        "object": "dynamic",
        "short": "int",
        "ushort": "int",
        "uint16": "int",
        "uint32": "long",
    }
    return aliases.get(normalized, normalized)


def load_schema_csv(path: Path) -> list[dict[str, str]]:
    if path.stat().st_size > MAX_SCHEMA_BYTES:
        raise ValueError(
            f"{path} exceeds the {MAX_SCHEMA_BYTES}-byte schema limit."
        )
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"{path} has no CSV header.")
        if not {"ColumnName", "ColumnType"}.issubset(reader.fieldnames):
            raise ValueError(
                f"{path} must contain ColumnName and ColumnType headers."
            )
        schema = []
        for row in reader:
            name = row["ColumnName"].strip()
            column_type = _normalize_schema_type(row["ColumnType"])
            if not name or name in RESERVED_COLUMNS:
                continue
            schema.append({"name": name, "type": column_type})
    if not schema:
        raise ValueError(f"{path} contains no ingestible schema columns.")
    return schema


def _find_repo_root(path: Path) -> Path | None:
    matches: list[Path] = []
    for candidate in (path.parent, *path.parents):
        if (candidate / ".script").is_dir() and (
            candidate / "Sample Data"
        ).is_dir():
            matches.append(candidate)
    return matches[-1] if matches else None


def load_table_schema_json(path: Path) -> list[dict[str, str]]:
    if path.stat().st_size > MAX_SCHEMA_BYTES:
        raise ValueError(
            f"{path} exceeds the {MAX_SCHEMA_BYTES}-byte schema limit."
        )
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    properties = document.get("Properties")
    if not isinstance(properties, list):
        raise ValueError(f"{path} must contain a Properties array.")
    schema: list[dict[str, str]] = []
    for property_value in properties:
        if not isinstance(property_value, dict):
            continue
        name = property_value.get("name", property_value.get("Name"))
        column_type = property_value.get(
            "type", property_value.get("Type")
        )
        if (
            not isinstance(name, str)
            or not isinstance(column_type, str)
            or name in RESERVED_COLUMNS
        ):
            continue
        schema.append(
            {
                "name": name,
                "type": _normalize_schema_type(column_type),
            }
        )
    if not schema:
        raise ValueError(f"{path} contains no ingestible schema columns.")
    return schema


def _nonempty_values(
    rows: Sequence[dict[str, Any]], column_name: str
) -> list[str]:
    return [
        str(row[column_name]).strip()
        for row in rows
        if column_name in row
        and row[column_name] is not None
        and str(row[column_name]).strip()
    ]


def _all_json_containers(values: Sequence[str]) -> bool:
    if not values:
        return False
    for value in values:
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return False
        if not isinstance(parsed, (dict, list)):
            return False
    return True


def infer_schema(
    rows: Sequence[dict[str, Any]], datetime_columns: set[str]
) -> list[dict[str, str]]:
    schema: list[dict[str, str]] = []
    for column_name in rows[0]:
        if column_name in RESERVED_COLUMNS:
            continue
        values = _nonempty_values(rows, column_name)
        if column_name in datetime_columns:
            column_type = "datetime"
        elif STRING_LIKE_COLUMN_RE.search(column_name):
            column_type = "string"
        elif values and all(
            value.casefold() in {"true", "false"} for value in values
        ):
            column_type = "boolean"
        elif values and all(INTEGER_RE.fullmatch(value) for value in values):
            numeric_values = [int(value) for value in values]
            if all(
                INT32_MIN <= value <= INT32_MAX
                for value in numeric_values
            ):
                column_type = "int"
            elif all(
                INT64_MIN <= value <= INT64_MAX
                for value in numeric_values
            ):
                column_type = "long"
            else:
                column_type = "string"
        elif values and all(
            INTEGER_RE.fullmatch(value) or REAL_RE.fullmatch(value)
            for value in values
        ):
            column_type = "real"
        elif _all_json_containers(values):
            column_type = "dynamic"
        else:
            column_type = "string"
        schema.append({"name": column_name, "type": column_type})
    if not any(column["name"] == "TimeGenerated" for column in schema):
        schema.append({"name": "TimeGenerated", "type": "datetime"})
    return schema


def _adapt_schema_to_rows(
    schema: Sequence[dict[str, str]],
    rows: Sequence[dict[str, Any]],
) -> list[dict[str, str]]:
    adapted: list[dict[str, str]] = []
    for column in schema:
        name = column["name"]
        column_type = _normalize_schema_type(column["type"])
        if column_type in {"byte", "sbyte"}:
            values = _nonempty_values(rows, name)
            if values and all(
                value.casefold() in {"true", "false"}
                for value in values
            ):
                column_type = "boolean"
            else:
                column_type = "int"
        adapted.append({"name": name, "type": column_type})
    return adapted


def _convert_boolean(value: str, column_name: str) -> bool:
    normalized = value.casefold()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(
        f"Column {column_name} value '{value}' is not a boolean."
    )


def convert_rows_to_schema(
    rows: Sequence[dict[str, Any]],
    schema: Sequence[dict[str, str]],
) -> list[dict[str, Any]]:
    schema_by_name = {
        column["name"]: _normalize_schema_type(column["type"])
        for column in schema
    }
    converted_rows: list[dict[str, Any]] = []
    for row_number, row in enumerate(rows, start=1):
        converted_row: dict[str, Any] = {}
        for column_name, value in row.items():
            column_type = schema_by_name.get(column_name)
            if column_type is None:
                converted_row[column_name] = value
                continue
            text = "" if value is None else str(value).strip()
            if not text and column_type != "string":
                converted_row[column_name] = None
            elif column_type == "string":
                converted_row[column_name] = "" if value is None else str(value)
            elif column_type == "boolean":
                converted_row[column_name] = _convert_boolean(
                    text, column_name
                )
            elif column_type in {"int", "long"}:
                converted_row[column_name] = int(text)
            elif column_type == "real":
                converted_row[column_name] = float(text)
            elif column_type == "datetime":
                converted_row[column_name] = ticks_to_kusto_datetime(
                    parse_kusto_datetime_ticks(text)
                )
            elif column_type == "dynamic":
                converted_row[column_name] = json.loads(text)
            elif column_type == "guid":
                converted_row[column_name] = text
            else:
                raise ValueError(
                    f"Unsupported schema type '{column_type}' for "
                    f"{column_name}."
                )
        converted_rows.append(converted_row)
    return converted_rows


def _resolve_schema(
    fixture_path: Path,
    table_name: str,
    rows: Sequence[dict[str, Any]],
    datetime_columns: set[str],
    schema_path: Path | None,
) -> tuple[list[dict[str, str]], Path | None, str]:
    if schema_path is not None:
        return load_schema_csv(schema_path), schema_path, "explicit"
    discovered_path = fixture_path.parent / f"{table_name}_Schema.csv"
    if discovered_path.is_file():
        return (
            load_schema_csv(discovered_path),
            discovered_path,
            "discovered",
        )
    repo_root = _find_repo_root(fixture_path)
    if repo_root is not None:
        table_schema_path = (
            repo_root
            / ".script/tests/KqlvalidationsTests/CustomTables"
            / f"{table_name}.json"
        )
        if table_schema_path.is_file():
            return (
                load_table_schema_json(table_schema_path),
                table_schema_path,
                "repository",
            )
    return infer_schema(rows, datetime_columns), None, "inferred"


def _sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def prepare_fixture(
    fixture_path: Path,
    expected_source_raw_table: str,
    target_id: str,
    target_group: str,
    repository: str,
    pull_request: str,
    run_id: str,
    run_attempt: int,
    target_slot: int = 0,
    target_count: int = 1,
    schema_path: Path | None = None,
    now_ticks: int | None = None,
) -> dict[str, Any]:
    fixture_path = fixture_path.resolve()
    if schema_path is not None:
        schema_path = schema_path.resolve()
    rows, table_name, datetime_columns = load_fixture_csv(fixture_path)
    if table_name != expected_source_raw_table:
        raise ValueError(
            f"Fixture Type must be {expected_source_raw_table!r}; "
            f"found {table_name!r}."
        )
    schema, resolved_schema_path, schema_source = _resolve_schema(
        fixture_path,
        table_name,
        rows,
        datetime_columns,
        schema_path,
    )
    schema = _adapt_schema_to_rows(schema, rows)
    if target_slot < 0 or target_slot >= target_count:
        raise ValueError(
            "target_slot must be between 0 and target_count - 1."
        )
    namespace = TimestampNamespace(
        target_id=target_id,
        target_group=target_group,
        slot=target_slot,
        quantum_ticks=timestamp_quantum_for_target_count(target_count),
    )
    if now_ticks is None:
        now_ticks = datetime_to_ticks(datetime.now(timezone.utc))
    run_key = build_run_key(
        repository, pull_request, run_id, run_attempt
    )
    rebased_rows, timestamp_metadata = rebase_time_generated(
        rows,
        run_key=run_key,
        namespace=namespace,
        now_ticks=now_ticks,
    )
    converted_rows = convert_rows_to_schema(rebased_rows, schema)
    return {
        "version": ARTIFACT_VERSION,
        "targetId": target_id,
        "targetGroup": target_group,
        "fixturePath": str(fixture_path),
        "fixtureHash": _sha256_bytes(fixture_path.read_bytes()),
        "schemaPath": str(resolved_schema_path)
        if resolved_schema_path is not None
        else None,
        "schemaSource": schema_source,
        "sourceRawTable": table_name,
        "rowCount": len(converted_rows),
        "schema": list(schema),
        "datetimeColumns": sorted(datetime_columns),
        "namespace": {
            **namespace.to_dict(),
            "repository": repository,
            "pullRequest": str(pull_request),
            "runId": str(run_id),
            "runAttempt": run_attempt,
            **timestamp_metadata,
        },
        "rows": converted_rows,
    }


def assert_disjoint_timestamp_sets(
    artifacts: Sequence[dict[str, Any]],
) -> None:
    by_group: dict[str, dict[str, set[str]]] = {}
    for artifact in artifacts:
        namespace = artifact["namespace"]
        group = str(namespace["targetGroup"])
        target_id = str(namespace["targetId"])
        timestamps = set(namespace["timestampValues"])
        existing = by_group.setdefault(group, {})
        for other_target, other_timestamps in existing.items():
            overlap = timestamps & other_timestamps
            if overlap:
                raise ValueError(
                    f"Timestamp overlap between {target_id} and "
                    f"{other_target}: {sorted(overlap)[:3]}"
                )
        existing[target_id] = timestamps


def _write_json(payload: dict[str, Any], output_path: Path | None) -> None:
    serialized = (
        json.dumps(
        payload, indent=2, sort_keys=True, ensure_ascii=True
        )
        + "\n"
    )
    if output_path is None:
        sys.stdout.write(serialized)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized_bytes = serialized.encode("utf-8")
    if output_path.exists():
        if output_path.read_bytes() == serialized_bytes:
            print(f"Reused identical {output_path}")
            return
        raise ValueError(
            f"Refusing to overwrite existing fixture artifact: {output_path}"
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
            temporary.write(serialized_bytes)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        try:
            os.link(temporary_path, output_path)
        except FileExistsError:
            if output_path.read_bytes() != serialized_bytes:
                raise ValueError(
                    "Fixture artifact was created concurrently with "
                    f"different content: {output_path}"
                )
        print(f"Wrote {output_path}")
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
