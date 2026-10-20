#!/usr/bin/env python3
"""Prepare an ASIM CSV fixture with exact, run-specific Kusto timestamps.

Example:
  python asim_fixture_preparation.py prepare \
      "Sample Data/ASIM/AWS_GuardDuty_AlertEvent_AWSGuardDuty_IngestedLogs.csv" \
      --expected-source-raw-table AWSGuardDuty \
      --target-id asimalerteventawsguardduty \
      --run-id 123456789 \
      --run-attempt 1 \
      --target-slot 0 \
      --target-count 2 \
      --output prepared-fixture.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence


ARTIFACT_VERSION = 1
MAX_FIXTURE_BYTES = 5 * 1024 * 1024
MAX_SCHEMA_BYTES = 1024 * 1024
TICKS_PER_SECOND = 10_000_000
TICKS_PER_MICROSECOND = 10
SAFETY_DELAY_SECONDS = 5 * 60
MAX_SAMPLE_SPAN_TICKS = 36 * 60 * 60 * TICKS_PER_SECOND
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

RESERVED_COLUMNS = {
    "_ItemId",
    "_ResourceId",
    "_ResourceId_s",
    "_SubscriptionId",
    "id",
    "MG",
    "TenantId",
    "Title",
    "Type",
    "UniqueId",
    "verbose",
    "verbose_b",
}

ISO_FRACTION_RE = re.compile(r"(?<=\d{2}:\d{2}:\d{2})\.(\d+)")
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

LEGACY_TIMESTAMP_FORMATS = (
    "%m/%d/%Y, %I:%M:%S.%f %p",
    "%m/%d/%Y, %I:%M:%S %p",
    "%m/%d/%Y %I:%M:%S.%f %p",
    "%m/%d/%Y %I:%M:%S %p",
    "%d/%m/%Y, %H:%M:%S.%f",
    "%d/%m/%Y, %H:%M:%S",
    "%d/%m/%Y",
    "%d-%m-%Y %H:%M",
    "%d-%m-%y %H:%M",
)


@dataclass(frozen=True)
class TimestampNamespace:
    target_id: str
    target_group: str
    slot: int
    quantum_ticks: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "targetId": self.target_id,
            "targetGroup": self.target_group,
            "slot": self.slot,
            "quantumTicks": self.quantum_ticks,
        }


def datetime_to_ticks(value: datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    delta = value - EPOCH
    return (
        (delta.days * 86_400 + delta.seconds) * TICKS_PER_SECOND
        + delta.microseconds * TICKS_PER_MICROSECOND
    )


def ticks_to_kusto_datetime(ticks: int) -> str:
    seconds, fraction_ticks = divmod(ticks, TICKS_PER_SECOND)
    value = EPOCH + timedelta(seconds=seconds)
    return (
        f"{value:%Y-%m-%dT%H:%M:%S}."
        f"{fraction_ticks:07d}Z"
    )


def parse_kusto_datetime_ticks(value: Any) -> int:
    if isinstance(value, datetime):
        return datetime_to_ticks(value)
    normalized = str(value).strip()
    if not normalized:
        raise ValueError("Timestamp cannot be empty.")
    normalized = re.sub(r"^0(?=\d{2}/\d{2}/\d{4})", "", normalized)

    fraction_match = ISO_FRACTION_RE.search(normalized)
    fraction = fraction_match.group(1) if fraction_match else ""
    if len(fraction) > 7:
        raise ValueError(
            f"Timestamp exceeds Kusto 100ns precision: {value}"
        )
    parse_value = normalized.replace("Z", "+00:00")
    if fraction_match:
        parse_fraction = fraction[:6].ljust(6, "0")
        parse_value = (
            parse_value[: fraction_match.start(1)]
            + parse_fraction
            + parse_value[fraction_match.end(1) :]
        )
    try:
        parsed = datetime.fromisoformat(parse_value)
    except ValueError:
        parsed = None
    if parsed is not None:
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
        base_ticks = datetime_to_ticks(parsed.replace(microsecond=0))
        fraction_ticks = int(fraction.ljust(7, "0") or "0")
        return base_ticks + fraction_ticks

    for timestamp_format in LEGACY_TIMESTAMP_FORMATS:
        try:
            parsed = datetime.strptime(normalized, timestamp_format)
            return datetime_to_ticks(parsed.replace(tzinfo=timezone.utc))
        except ValueError:
            continue
    raise ValueError(f"Unsupported timestamp value: {value}")


def timestamp_quantum_for_target_count(target_count: int) -> int:
    if target_count < 1:
        raise ValueError("target_count must be at least 1.")
    quantum = 1
    while quantum < target_count:
        quantum *= 10
    if quantum > TICKS_PER_SECOND:
        raise ValueError(
            f"Cannot allocate {target_count} parser timestamp slots in one second."
        )
    return quantum


def allocate_timestamp_namespaces(
    targets: Sequence[tuple[str, str]],
) -> dict[str, TimestampNamespace]:
    """Allocate non-overlapping low-order tick slots by target group."""
    grouped: dict[str, set[str]] = {}
    for target_id, target_group in targets:
        if not target_id or not target_group:
            raise ValueError("target_id and target_group must be non-empty.")
        grouped.setdefault(target_group, set()).add(target_id)

    namespaces: dict[str, TimestampNamespace] = {}
    for target_group, target_ids in sorted(grouped.items()):
        ordered_ids = sorted(target_ids)
        quantum = timestamp_quantum_for_target_count(len(ordered_ids))
        for slot, target_id in enumerate(ordered_ids):
            if target_id in namespaces:
                raise ValueError(
                    f"Target '{target_id}' appears in multiple timestamp groups."
                )
            namespaces[target_id] = TimestampNamespace(
                target_id=target_id,
                target_group=target_group,
                slot=slot,
                quantum_ticks=quantum,
            )
    return namespaces


def _hash_to_run_slot(run_key: str, quantum_ticks: int) -> int:
    available_slots = TICKS_PER_SECOND // quantum_ticks
    digest = hashlib.sha256(run_key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % available_slots


def build_run_key(
    repository: str,
    pull_request: str,
    run_id: str,
    run_attempt: int,
) -> str:
    if not repository or not run_id:
        raise ValueError("repository and run_id must be non-empty.")
    if run_attempt < 1:
        raise ValueError("run_attempt must be at least 1.")
    return "|".join(
        (repository, str(pull_request), str(run_id), str(run_attempt))
    )


def compute_latest_rebased_tick(
    now_ticks: int,
    run_key: str,
    namespace: TimestampNamespace,
    safety_delay_seconds: int = SAFETY_DELAY_SECONDS,
) -> tuple[int, int]:
    if namespace.slot < 0 or namespace.slot >= namespace.quantum_ticks:
        raise ValueError("Timestamp namespace slot is outside its quantum.")
    base_second = (
        now_ticks
        - (now_ticks % TICKS_PER_SECOND)
        - safety_delay_seconds * TICKS_PER_SECOND
    )
    run_slot = _hash_to_run_slot(run_key, namespace.quantum_ticks)
    latest_tick = (
        base_second
        + run_slot * namespace.quantum_ticks
        + namespace.slot
    )
    return latest_tick, run_slot


def rebase_time_generated(
    rows: Sequence[dict[str, Any]],
    run_key: str,
    namespace: TimestampNamespace,
    now_ticks: int,
    max_span_ticks: int = MAX_SAMPLE_SPAN_TICKS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not rows:
        raise ValueError("Fixture must contain at least one row.")

    parsed_ticks: list[int | None] = []
    for row_index, row in enumerate(rows, start=1):
        if "TimeGenerated" not in row:
            raise ValueError(
                f"Fixture row {row_index} is missing TimeGenerated."
            )
        raw_value = row["TimeGenerated"]
        parsed_ticks.append(
            None
            if raw_value is None or not str(raw_value).strip()
            else parse_kusto_datetime_ticks(raw_value)
        )

    nonempty_ticks = [tick for tick in parsed_ticks if tick is not None]
    if not nonempty_ticks:
        raise ValueError("Fixture has no non-empty TimeGenerated values.")
    latest_source_tick = max(nonempty_ticks)
    earliest_source_tick = min(nonempty_ticks)
    source_span = latest_source_tick - earliest_source_tick
    compress_span = source_span > max_span_ticks

    latest_rebased_tick, run_slot = compute_latest_rebased_tick(
        now_ticks, run_key, namespace
    )
    timestamp_suffix_ticks = latest_rebased_tick % TICKS_PER_SECOND
    distance_by_source_tick: dict[int, int] = {}
    previous_units = -1
    distance_quantum = TICKS_PER_SECOND
    max_units = max_span_ticks // distance_quantum
    ordered_source_ticks = sorted(set(nonempty_ticks), reverse=True)
    if len(ordered_source_ticks) > max_units + 1:
        raise ValueError(
            "Fixture has too many distinct timestamps to preserve within "
            "the configured maximum span."
        )
    for index, source_tick in enumerate(ordered_source_ticks):
        distance = latest_source_tick - source_tick
        if compress_span:
            distance = distance * max_span_ticks // source_span
        desired_units = (
            distance + distance_quantum - 1
        ) // distance_quantum
        lower_bound = 0 if previous_units < 0 else previous_units + 1
        remaining_values = len(ordered_source_ticks) - index - 1
        upper_bound = max_units - remaining_values
        units = min(max(desired_units, lower_bound), upper_bound)
        distance_by_source_tick[source_tick] = (
            units * distance_quantum
        )
        previous_units = units

    prepared_rows: list[dict[str, Any]] = []
    timestamp_values: list[str] = []
    for row, source_tick in zip(rows, parsed_ticks):
        prepared_row = dict(row)
        rebased_tick = (
            latest_rebased_tick
            if source_tick is None
            else latest_rebased_tick - distance_by_source_tick[source_tick]
        )
        if rebased_tick % TICKS_PER_SECOND != timestamp_suffix_ticks:
            raise AssertionError("Rebased timestamp escaped its run suffix.")
        if rebased_tick % namespace.quantum_ticks != namespace.slot:
            raise AssertionError("Rebased timestamp escaped its target slot.")
        timestamp_value = ticks_to_kusto_datetime(rebased_tick)
        prepared_row["TimeGenerated"] = timestamp_value
        prepared_rows.append(prepared_row)
        timestamp_values.append(timestamp_value)

    unique_timestamps = sorted(set(timestamp_values))
    timestamp_hash = hashlib.sha256(
        "\n".join(unique_timestamps).encode("utf-8")
    ).hexdigest()
    return prepared_rows, {
        "latestTick": latest_rebased_tick,
        "latestTimeGenerated": ticks_to_kusto_datetime(
            latest_rebased_tick
        ),
        "runSlot": run_slot,
        "timestampSuffixTicks": timestamp_suffix_ticks,
        "sourceSpanTicks": source_span,
        "rebasedSpanTicks": (
            max(parse_kusto_datetime_ticks(value) for value in timestamp_values)
            - min(
                parse_kusto_datetime_ticks(value)
                for value in timestamp_values
            )
        ),
        "compressed": compress_span,
        "timestampValues": unique_timestamps,
        "timestampSetHash": f"sha256:{timestamp_hash}",
    }


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


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser(
        "prepare", help="Prepare one ASIM fixture artifact."
    )
    prepare.add_argument("fixture", type=Path)
    prepare.add_argument(
        "--expected-source-raw-table",
        required=True,
    )
    prepare.add_argument("--target-id", required=True)
    prepare.add_argument("--target-group", required=True)
    prepare.add_argument(
        "--repository", default="Azure/Azure-Sentinel"
    )
    prepare.add_argument("--pull-request", default="0")
    prepare.add_argument("--run-id", required=True)
    prepare.add_argument("--run-attempt", type=int, default=1)
    prepare.add_argument("--target-slot", type=int, default=0)
    prepare.add_argument("--target-count", type=int, default=1)
    prepare.add_argument("--schema-path", type=Path)
    prepare.add_argument(
        "--now",
        help="Optional deterministic UTC timestamp for testing.",
    )
    prepare.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            if args.output is not None and (
                args.output.resolve() == args.fixture.resolve()
            ):
                raise ValueError(
                    "Output path must not replace the source fixture."
                )
            now_ticks = (
                parse_kusto_datetime_ticks(args.now)
                if args.now
                else None
            )
            artifact = prepare_fixture(
                fixture_path=args.fixture,
                expected_source_raw_table=args.expected_source_raw_table,
                target_id=args.target_id,
                target_group=args.target_group,
                repository=args.repository,
                pull_request=args.pull_request,
                run_id=args.run_id,
                run_attempt=args.run_attempt,
                target_slot=args.target_slot,
                target_count=args.target_count,
                schema_path=args.schema_path,
                now_ticks=now_ticks,
            )
            _write_json(artifact, args.output)
            return 0
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
