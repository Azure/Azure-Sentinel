#!/usr/bin/env python3
"""Validate ASIM ingestion-time output and optional query-time parity.

This helper extends the raw/parser DCR harness with:

1. runtime ParserFilterQuery evaluation over the exact raw snapshot;
2. DCR-authoritative schema evidence and ASimDataTester execution over the
   exact target slice;
3. optional query-time parser execution with disabled=false and pack=true
   when those parameters are supported; and
4. typed, duplicate-aware semantic parity comparison.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

import yaml

from asim_fixture_preparation import (
    parse_kusto_datetime_ticks,
    ticks_to_kusto_datetime,
)
from asim_ingest_time_validation import (
    load_yaml_file,
    split_kql_statements,
    split_pipeline,
)
from asim_ingestion_harness import (
    DEFAULT_DCE_NAME,
    DEFAULT_INGESTION_ENDPOINT,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP,
    DEFAULT_SUBSCRIPTION_ID,
    DEFAULT_WORKSPACE_ID,
    DEFAULT_WORKSPACE_NAME,
    AsimIngestionHarness,
    CanaryConfig,
    DefaultAzureTokenProvider,
    HarnessError,
)


VALIDATION_RESULT_VERSION = 1
MAX_MISMATCH_EXAMPLES = 10
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
RESULT_ERROR_PREFIX = "(0) Error:"


class QueryClient(Protocol):
    def query_kql(
        self, query: str, *, stage: str = "query"
    ) -> dict[str, Any]:
        raise NotImplementedError


class ValidationError(RuntimeError):
    def __init__(
        self,
        stage: str,
        message: str,
        *,
        details: Any = None,
    ):
        super().__init__(message)
        self.stage = stage
        self.details = details


def _require_identifier(value: str, field: str) -> str:
    if not IDENTIFIER_RE.fullmatch(value):
        raise ValidationError(
            "query-build",
            f"{field} must be a KQL identifier: {value}",
        )
    return value


def _quote_kql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _timestamp_literals(timestamps: Sequence[str]) -> str:
    unique = sorted(set(timestamps))
    if not unique:
        raise ValidationError(
            "query-build", "At least one exact timestamp is required."
        )
    for value in unique:
        parse_kusto_datetime_ticks(value)
    return ", ".join(f"datetime({value})" for value in unique)


def build_exact_slice_expression(
    table_name: str,
    timestamps: Sequence[str],
    projected_columns: Sequence[str] | None = None,
) -> str:
    table_name = _require_identifier(table_name, "table_name")
    query = (
        f"{table_name}\n"
        f"| where TimeGenerated in ({_timestamp_literals(timestamps)})"
    )
    if projected_columns is not None:
        if not projected_columns:
            raise ValidationError(
                "query-build", "At least one projected column is required."
            )
        columns = [
            _require_identifier(column, "projected column")
            for column in projected_columns
        ]
        query += "\n| project " + ", ".join(columns)
    return query


def _is_source_passthrough(filter_query: str) -> bool:
    statements = split_kql_statements(filter_query)
    if not statements:
        return False
    stages = split_pipeline(statements[-1])
    return len(stages) == 1 and stages[0].casefold() == "source"


def build_filter_count_query(
    source_table: str,
    timestamps: Sequence[str],
    filter_query: str,
) -> str:
    source_expression = build_exact_slice_expression(
        source_table, timestamps
    )
    return (
        f"let source = materialize({source_expression});\n"
        f"{filter_query.strip()}\n"
        "| summarize _AsimSelectedCount=count() by TimeGenerated\n"
        "| project TimeGenerated, _AsimSelectedCount"
    )


def _normalize_column_type(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {
        "bool": "boolean",
        "double": "real",
        "float": "real",
        "int32": "int",
        "int64": "long",
        "integer": "int",
    }
    return aliases.get(normalized, normalized)


def _normalize_query_table(
    query_table: Mapping[str, Any],
    stage: str,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    columns = query_table.get("columns")
    raw_rows = query_table.get("rows")
    if not isinstance(columns, list) or not isinstance(raw_rows, list):
        raise ValidationError(
            stage,
            "Log Analytics result must contain columns and rows.",
        )
    schema: list[dict[str, str]] = []
    column_names: list[str] = []
    for column in columns:
        if not isinstance(column, dict):
            raise ValidationError(stage, "Invalid query column metadata.")
        name = column.get("name")
        column_type = column.get("type")
        if not isinstance(name, str) or not isinstance(column_type, str):
            raise ValidationError(stage, "Invalid query column metadata.")
        if name in column_names:
            raise ValidationError(
                stage, f"Query returned duplicate column {name}."
            )
        column_names.append(name)
        schema.append(
            {
                "name": name,
                "type": _normalize_column_type(column_type),
            }
        )

    rows: list[dict[str, Any]] = []
    for raw_row in raw_rows:
        if (
            not isinstance(raw_row, list)
            or len(raw_row) != len(column_names)
        ):
            raise ValidationError(stage, "Invalid query row shape.")
        rows.append(dict(zip(column_names, raw_row)))
    return schema, rows


def _parse_filter_counts(
    query_table: Mapping[str, Any],
    timestamps: Sequence[str],
) -> dict[str, int]:
    _, rows = _normalize_query_table(query_table, "filter")
    expected_timestamps = set(timestamps)
    counts = {timestamp: 0 for timestamp in expected_timestamps}
    for row in rows:
        timestamp = row.get("TimeGenerated")
        count = row.get("_AsimSelectedCount")
        if not isinstance(timestamp, str) or timestamp not in counts:
            raise ValidationError(
                "filter",
                "ParserFilterQuery returned a row outside the exact "
                "timestamp set.",
                details={"TimeGenerated": timestamp},
            )
        if isinstance(count, bool) or not isinstance(count, (int, float)):
            raise ValidationError(
                "filter", "Filter count must be numeric."
            )
        int_count = int(count)
        if int_count != count or int_count < 0:
            raise ValidationError(
                "filter", "Filter count must be a non-negative integer."
            )
        counts[timestamp] += int_count
    return counts


def _count_snapshot_rows(
    source_snapshot: Mapping[str, Any],
) -> dict[str, int]:
    timestamps = source_snapshot.get("timestampValues")
    rows = source_snapshot.get("rows")
    if not isinstance(timestamps, list) or not isinstance(rows, list):
        raise ValidationError(
            "filter", "Source snapshot is missing timestamps or rows."
        )
    counts = {str(timestamp): 0 for timestamp in timestamps}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValidationError(
                "filter", "Source snapshot row must be an object."
            )
        timestamp = row.get("TimeGenerated")
        if not isinstance(timestamp, str) or timestamp not in counts:
            raise ValidationError(
                "filter",
                "Source snapshot row is outside its timestamp set.",
            )
        counts[timestamp] += 1
    return counts


def _render_kql_default(value: Any, parameter_type: str) -> str:
    normalized_type = parameter_type.strip().lower()
    if normalized_type in {"bool", "boolean"}:
        if not isinstance(value, bool):
            raise ValidationError(
                "qtp-execution", "Boolean parameter default is invalid."
            )
        return "true" if value else "false"
    if normalized_type in {"int", "long", "real"}:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(
                "qtp-execution", "Numeric parameter default is invalid."
            )
        return str(value)
    if normalized_type == "string":
        return _quote_kql_string(str(value))
    if normalized_type == "datetime":
        return f"datetime({value})"
    if normalized_type == "dynamic":
        return "dynamic(" + json.dumps(
            value, ensure_ascii=True, separators=(",", ":")
        ) + ")"
    raise ValidationError(
        "qtp-execution",
        f"Unsupported query-time parser parameter type: {parameter_type}",
    )


def build_query_time_parser_query(
    query_time_document: Mapping[str, Any],
    source_table: str,
    timestamps: Sequence[str],
) -> str:
    parser_query = query_time_document.get("ParserQuery")
    if not isinstance(parser_query, str) or not parser_query.strip():
        raise ValidationError(
            "qtp-execution",
            "Query-time parser is missing ParserQuery.",
        )
    parser_params = query_time_document.get("ParserParams", [])
    if not isinstance(parser_params, list):
        raise ValidationError(
            "qtp-execution", "ParserParams must be an array."
        )

    signature: list[str] = []
    invocation: list[str] = []
    for parameter in parser_params:
        if not isinstance(parameter, Mapping):
            raise ValidationError(
                "qtp-execution", "ParserParams entry must be an object."
            )
        name = parameter.get("Name")
        parameter_type = parameter.get("Type")
        if not isinstance(name, str) or not isinstance(
            parameter_type, str
        ):
            raise ValidationError(
                "qtp-execution",
                "ParserParams entries require Name and Type.",
            )
        _require_identifier(name, "query-time parameter")
        if "Default" not in parameter:
            raise ValidationError(
                "qtp-execution",
                f"Query-time parameter {name} requires a default value.",
            )
        default = _render_kql_default(
            parameter["Default"], parameter_type
        )
        signature.append(f"{name}:{parameter_type}={default}")
        if name.casefold() == "disabled":
            if parameter_type.casefold() not in {"bool", "boolean"}:
                raise ValidationError(
                    "qtp-execution",
                    "The disabled parameter must be boolean.",
                )
            invocation.append(f"{name}=false")
        elif name.casefold() == "pack":
            if parameter_type.casefold() not in {"bool", "boolean"}:
                raise ValidationError(
                    "qtp-execution",
                    "The pack parameter must be boolean.",
                )
            invocation.append(f"{name}=true")

    invocation_text = ", ".join(invocation)
    source_table = _require_identifier(
        source_table, "query-time source table"
    )
    timestamp_literals = _timestamp_literals(timestamps)
    return (
        f"let {source_table} = materialize("
        f"table({_quote_kql_string(source_table)})"
        f" | where TimeGenerated in ({timestamp_literals}));\n"
        + "let _AsimValidationQtp = ("
        + ", ".join(signature)
        + ") {\n"
        + parser_query.strip()
        + "\n};\n"
        + f"_AsimValidationQtp({invocation_text})\n"
        + f"| where TimeGenerated in ({timestamp_literals})"
    )


def _load_tester_query(repo_root: Path, tester_name: str) -> str:
    path = (
        repo_root
        / "ASIM/dev/ASimTester/Testers"
        / f"{tester_name}.yaml"
    )
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValidationError(
            "asim-test", f"{path} must contain a YAML mapping."
        )
    query = document.get("ParserQuery")
    if not isinstance(query, str) or not query.strip():
        raise ValidationError(
            "asim-test", f"{path} is missing ParserQuery."
        )
    return query


def build_asim_tester_query(
    *,
    tester_name: str,
    tester_query: str,
    target_table: str,
    timestamps: Sequence[str],
    schema_name: str,
    projected_columns: Sequence[str] | None = None,
) -> str:
    target_expression = build_exact_slice_expression(
        target_table,
        timestamps,
        projected_columns,
    )
    schema_literal = _quote_kql_string(schema_name)
    if tester_name == "ASimDataTester":
        signature = "T:(*), selected_schema:string=''"
        invocation = (
            "_AsimValidationTargetRows\n"
            f"| invoke _AsimValidationTester({schema_literal})"
        )
    else:
        raise ValidationError(
            "asim-test", f"Unsupported ASIM tester {tester_name}."
        )
    return (
        f"let _AsimValidationTargetRows = materialize("
        f"{target_expression});\n"
        f"let _AsimValidationTester = ({signature}) {{\n"
        f"{tester_query.strip()}\n"
        "};\n"
        f"{invocation}"
    )


def _evaluate_tester_result(
    query_table: Mapping[str, Any],
    tester_name: str,
) -> dict[str, Any]:
    _, rows = _normalize_query_table(query_table, tester_name)
    results: list[str] = []
    for row in rows:
        result = row.get("Result")
        if not isinstance(result, str):
            raise ValidationError(
                "asim-test",
                f"{tester_name} returned a row without Result.",
            )
        results.append(result)
    errors = [
        result
        for result in results
        if result.startswith(RESULT_ERROR_PREFIX)
    ]
    return {
        "status": "failed" if errors else "passed",
        "resultCount": len(results),
        "errorCount": len(errors),
        "results": results,
    }


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


class AsimIngestionValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.data_tester_query = _load_tester_query(
            self.repo_root, "ASimDataTester"
        )

    def evaluate_filter(
        self,
        query_client: QueryClient,
        source_snapshot: Mapping[str, Any],
        parser_document: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        source_table = parser_document.get("SourceRawTable")
        filter_query = parser_document.get("ParserFilterQuery")
        timestamps = source_snapshot.get("timestampValues")
        if (
            not isinstance(source_table, str)
            or not isinstance(filter_query, str)
            or not isinstance(timestamps, list)
        ):
            raise ValidationError(
                "filter",
                "Parser or source snapshot is missing filter metadata.",
            )
        raw_counts = _count_snapshot_rows(source_snapshot)
        query = build_filter_count_query(
            source_table,
            [str(value) for value in timestamps],
            filter_query,
        )
        selected_counts = _parse_filter_counts(
            query_client.query_kql(query, stage="filter"),
            [str(value) for value in timestamps],
        )
        overages = {
            timestamp: {
                "raw": raw_counts[timestamp],
                "selected": selected_counts[timestamp],
            }
            for timestamp in raw_counts
            if selected_counts[timestamp] > raw_counts[timestamp]
        }
        if overages:
            raise ValidationError(
                "filter",
                "ParserFilterQuery selected more rows than exist in the "
                "raw snapshot.",
                details={"overages": overages},
            )
        selected = sum(selected_counts.values())
        raw = sum(raw_counts.values())
        rejected = raw - selected
        passthrough = _is_source_passthrough(filter_query)
        if selected <= 0:
            raise ValidationError(
                "filter",
                "ParserFilterQuery must select at least one fixture row.",
            )
        if not passthrough and rejected <= 0:
            raise ValidationError(
                "filter",
                "A selective ParserFilterQuery fixture must contain at "
                "least one rejected row.",
            )
        return {
            "status": "passed",
            "mode": "pass-through" if passthrough else "selective",
            "rawRowCount": raw,
            "selectedRowCount": selected,
            "rejectedRowCount": rejected,
            "rawCountsByTimestamp": raw_counts,
            "selectedCountsByTimestamp": selected_counts,
        }

    def validate_outputs(
        self,
        query_client: QueryClient,
        source_snapshot: Mapping[str, Any],
        parser_document: Mapping[str, Any],
        query_time_document: Mapping[str, Any] | None,
    ) -> Mapping[str, Any]:
        target_table = parser_document.get("TargetASIMTable")
        source_table = parser_document.get("SourceRawTable")
        schema_name = (
            parser_document.get("Normalization", {}).get("Schema")
            if isinstance(
                parser_document.get("Normalization"), Mapping
            )
            else None
        )
        timestamps = source_snapshot.get("timestampValues")
        if (
            not isinstance(target_table, str)
            or not isinstance(source_table, str)
            or not isinstance(schema_name, str)
            or not isinstance(timestamps, list)
        ):
            raise ValidationError(
                "output-validation",
                "Parser or source snapshot is missing output metadata.",
            )
        timestamp_values = [str(value) for value in timestamps]

        data_query = build_asim_tester_query(
            tester_name="ASimDataTester",
            tester_query=self.data_tester_query,
            target_table=target_table,
            timestamps=timestamp_values,
            schema_name=schema_name,
        )
        data_test = _evaluate_tester_result(
            query_client.query_kql(data_query, stage="asim-data"),
            "ASimDataTester",
        )
        if data_test["status"] == "failed":
            raise ValidationError(
                "asim-data",
                "ASimDataTester reported errors.",
                details=data_test,
            )

        result: dict[str, Any] = {
            "status": "passed",
            "schemaValidation": {
                "status": "passed",
                "authority": "parser-dcr-output-stream",
            },
            "dataTest": data_test,
            "queryTimeExecution": {
                "status": "not-applicable",
            },
            "parity": {
                "status": "not-applicable",
            },
        }
        if query_time_document is None:
            return result

        qtp_query = build_query_time_parser_query(
            query_time_document,
            source_table,
            timestamp_values,
        )
        expected_schema, expected_rows = _normalize_query_table(
            query_client.query_kql(
                qtp_query, stage="qtp-execution"
            ),
            "qtp-execution",
        )
        comparison_columns = [
            column["name"] for column in expected_schema
        ]
        actual_schema, actual_rows = _normalize_query_table(
            query_client.query_kql(
                build_exact_slice_expression(
                    target_table,
                    timestamp_values,
                    comparison_columns,
                ),
                stage="target-output",
            ),
            "target-output",
        )
        result["queryTimeExecution"] = {
            "status": "passed",
            "rowCount": len(expected_rows),
        }
        parity = compare_parser_outputs(
            expected_schema=expected_schema,
            expected_rows=expected_rows,
            actual_schema=actual_schema,
            actual_rows=actual_rows,
        )
        result["parity"] = parity
        if parity["status"] != "passed":
            raise ValidationError(
                "parity",
                "Query-time and ingestion-time outputs differ.",
                details=parity,
            )
        return result


def _load_json_object(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return document


def _write_json(payload: Mapping[str, Any], path: Path | None) -> None:
    serialized = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n"
    )
    if path is None:
        sys.stdout.write(serialized)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialized, encoding="utf-8")


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared_fixture", type=Path)
    parser.add_argument("parser_yaml", type=Path)
    parser.add_argument("--query-time-yaml", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--snapshot-output", type=Path, required=True)
    parser.add_argument("--result-output", type=Path)
    parser.add_argument("--deadline-seconds", type=float, default=900)
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
    harness: AsimIngestionHarness | None = None
    result: dict[str, Any] = {
        "version": VALIDATION_RESULT_VERSION,
        "status": "failed",
    }
    try:
        prepared_fixture = _load_json_object(args.prepared_fixture)
        parser_document = load_yaml_file(args.parser_yaml)
        query_time_document = (
            load_yaml_file(args.query_time_yaml)
            if args.query_time_yaml is not None
            else None
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
            validation_runner=AsimIngestionValidator(args.repo_root),
            query_time_document=query_time_document,
        )
        exit_code = 0
    except (
        HarnessError,
        ValidationError,
        OSError,
        ValueError,
        KeyError,
        yaml.YAMLError,
    ) as exc:
        if harness is not None and harness.last_result is not None:
            result = dict(harness.last_result)
            result["status"] = "failed"
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
        elif isinstance(exc, ValidationError):
            result["error"].update(
                {
                    "stage": exc.stage,
                    "details": exc.details,
                }
            )
        print(f"::error::{exc}", file=sys.stderr)
        exit_code = 1
    _write_json(result, args.result_output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
