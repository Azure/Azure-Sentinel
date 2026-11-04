"""Typed canonical row-multiset comparison and diagnostics."""

from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any, Mapping, Sequence

from asim_ingestion.fixtures.timestamps import (
    parse_kusto_datetime_ticks,
    ticks_to_kusto_datetime,
)
from .queries import MAX_MISMATCH_EXAMPLES, _normalize_column_type

def _normalize_dynamic(value: Any) -> Any:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return value
    if isinstance(value, dict):
        return {
            str(key): _normalize_dynamic(value[key])
            for key in sorted(value, key=str)
        }
    if isinstance(value, list):
        return [_normalize_dynamic(item) for item in value]
    return value


def _canonical_value(value: Any, column_type: str) -> Any:
    if value is None:
        return None
    if column_type == "datetime":
        return ticks_to_kusto_datetime(
            parse_kusto_datetime_ticks(value)
        )
    if column_type == "dynamic":
        return _normalize_dynamic(value)
    if column_type == "real" and isinstance(value, float):
        if math.isnan(value):
            return {"specialReal": "NaN"}
        if math.isinf(value):
            return {
                "specialReal": "Infinity" if value > 0 else "-Infinity"
            }
    return value


def _schema_by_name(
    schema: Sequence[Mapping[str, str]],
) -> dict[str, str]:
    return {
        str(column["name"]): _normalize_column_type(
            str(column["type"])
        )
        for column in schema
    }


def _canonical_row(
    row: Mapping[str, Any],
    schema: Mapping[str, str],
    columns: Sequence[str],
) -> list[dict[str, Any]]:
    return [
        {
            "column": column,
            "type": schema[column],
            "value": _canonical_value(row.get(column), schema[column]),
        }
        for column in columns
    ]


def _canonical_counter(
    rows: Sequence[Mapping[str, Any]],
    schema: Mapping[str, str],
    columns: Sequence[str],
) -> tuple[Counter[str], dict[str, list[dict[str, Any]]]]:
    counter: Counter[str] = Counter()
    payloads: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        payload = _canonical_row(row, schema, columns)
        key = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        counter[key] += 1
        payloads[key] = payload
    return counter, payloads


def _counter_examples(
    difference: Counter[str],
    payloads: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "count": count,
            "row": payloads[key],
        }
        for key, count in difference.most_common(
            MAX_MISMATCH_EXAMPLES
        )
    ]


def _stable_key_diagnostics(
    expected_rows: Sequence[Mapping[str, Any]],
    actual_rows: Sequence[Mapping[str, Any]],
    schema: Mapping[str, str],
    columns: Sequence[str],
) -> dict[str, Any] | None:
    candidates = (
        ("EventUid", "TimeGenerated"),
        ("EventOriginalUid", "TimeGenerated"),
        ("EventUid",),
        ("EventOriginalUid",),
    )
    column_set = set(columns)
    for candidate in candidates:
        if not set(candidate).issubset(column_set):
            continue

        def build_index(
            rows: Sequence[Mapping[str, Any]],
        ) -> dict[str, Mapping[str, Any]] | None:
            index: dict[str, Mapping[str, Any]] = {}
            for row in rows:
                key_payload = [
                    _canonical_value(row.get(column), schema[column])
                    for column in candidate
                ]
                if any(value in {None, ""} for value in key_payload):
                    return None
                key = json.dumps(
                    key_payload,
                    ensure_ascii=True,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                if key in index:
                    return None
                index[key] = row
            return index

        expected_index = build_index(expected_rows)
        actual_index = build_index(actual_rows)
        if expected_index is None or actual_index is None:
            continue
        diagnostics: list[dict[str, Any]] = []
        for key in sorted(
            set(expected_index) & set(actual_index)
        ):
            expected = expected_index[key]
            actual = actual_index[key]
            differences = []
            for column in columns:
                expected_value = _canonical_value(
                    expected.get(column), schema[column]
                )
                actual_value = _canonical_value(
                    actual.get(column), schema[column]
                )
                if expected_value != actual_value:
                    differences.append(
                        {
                            "column": column,
                            "expected": expected_value,
                            "actual": actual_value,
                        }
                    )
            if differences:
                diagnostics.append(
                    {
                        "key": json.loads(key),
                        "differences": differences,
                    }
                )
            if len(diagnostics) >= MAX_MISMATCH_EXAMPLES:
                break
        return {
            "keyColumns": list(candidate),
            "mismatches": diagnostics,
        }
    return None


def compare_parser_outputs(
    *,
    expected_schema: Sequence[Mapping[str, str]],
    expected_rows: Sequence[Mapping[str, Any]],
    actual_schema: Sequence[Mapping[str, str]],
    actual_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    expected_types = _schema_by_name(expected_schema)
    actual_types = _schema_by_name(actual_schema)
    expected_columns = set(expected_types)
    actual_columns = set(actual_types)
    missing_in_ingest = sorted(expected_columns - actual_columns)
    ignored_additional = sorted(actual_columns - expected_columns)
    type_mismatches = [
        {
            "column": column,
            "queryTimeType": expected_types[column],
            "ingestTimeType": actual_types.get(column),
        }
        for column in sorted(expected_columns & actual_columns)
        if actual_types.get(column) != expected_types[column]
    ]
    schema_result = {
        "status": (
            "passed"
            if not missing_in_ingest
            and not type_mismatches
            else "failed"
        ),
        "missingInIngestTime": missing_in_ingest,
        "ignoredAdditionalIngestTime": ignored_additional,
        "typeMismatches": type_mismatches,
    }
    if schema_result["status"] == "failed":
        return {
            "status": "failed",
            "schema": schema_result,
            "rows": None,
        }

    columns = sorted(expected_columns)
    expected_counter, expected_payloads = _canonical_counter(
        expected_rows, expected_types, columns
    )
    actual_counter, actual_payloads = _canonical_counter(
        actual_rows, actual_types, columns
    )
    missing = expected_counter - actual_counter
    extra = actual_counter - expected_counter
    duplicate_differences = [
        {
            "row": expected_payloads.get(
                key, actual_payloads.get(key)
            ),
            "queryTimeCount": expected_counter[key],
            "ingestTimeCount": actual_counter[key],
        }
        for key in sorted(set(expected_counter) & set(actual_counter))
        if expected_counter[key] != actual_counter[key]
    ][:MAX_MISMATCH_EXAMPLES]
    row_status = "passed" if not missing and not extra else "failed"
    row_result = {
        "status": row_status,
        "queryTimeRowCount": sum(expected_counter.values()),
        "ingestTimeRowCount": sum(actual_counter.values()),
        "missingRowCount": sum(missing.values()),
        "extraRowCount": sum(extra.values()),
        "duplicateCountDifferences": duplicate_differences,
        "missingExamples": _counter_examples(
            missing, expected_payloads
        ),
        "extraExamples": _counter_examples(extra, actual_payloads),
        "columnDiagnostics": _stable_key_diagnostics(
            expected_rows,
            actual_rows,
            expected_types,
            columns,
        ),
    }
    return {
        "status": row_status,
        "schema": schema_result,
        "rows": row_result,
    }
