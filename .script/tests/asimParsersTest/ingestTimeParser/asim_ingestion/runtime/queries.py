"""Build and evaluate exact-slice filter, QTP, and ASIM tester queries."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

import yaml

from asim_ingestion.fixtures.timestamps import parse_kusto_datetime_ticks
from asim_ingestion.parser.kql import split_kql_statements, split_pipeline

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


def _quote_column_name(value: str) -> str:
    if IDENTIFIER_RE.fullmatch(value):
        return value
    return "['" + value.replace("'", "''") + "']"


def _timestamp_literals(timestamps: Sequence[str]) -> str:
    unique = sorted(set(timestamps))
    if not unique:
        raise ValidationError(
            "query-build", "At least one exact timestamp is required."
        )
    for value in unique:
        parse_kusto_datetime_ticks(value)
    return ", ".join(f"datetime({value})" for value in unique)


def _datatable_type(value: str) -> str:
    normalized = _normalize_column_type(value)
    return "bool" if normalized == "boolean" else normalized


def _datatable_value(value: Any, column_type: str) -> str:
    normalized = _normalize_column_type(column_type)
    if value is None:
        return f"{_datatable_type(normalized)}(null)"
    if normalized == "string":
        return "@'" + str(value).replace("'", "''") + "'"
    if normalized == "datetime":
        parse_kusto_datetime_ticks(str(value))
        return f"datetime({value})"
    if normalized == "boolean":
        if not isinstance(value, bool):
            raise ValidationError(
                "query-build",
                f"Boolean fixture value is invalid: {value!r}",
            )
        return "true" if value else "false"
    if normalized in {"int", "long"}:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError(
                "query-build",
                f"Integer fixture value is invalid: {value!r}",
            )
        return str(value)
    if normalized == "real":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(
                "query-build",
                f"Real fixture value is invalid: {value!r}",
            )
        return repr(float(value))
    if normalized == "dynamic":
        return (
            "dynamic("
            + json.dumps(
                value,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + ")"
        )
    if normalized == "guid":
        return f"guid({value})"
    raise ValidationError(
        "query-build",
        f"Unsupported fixture schema type: {column_type}",
    )


def build_fixture_datatable(
    schema: Sequence[Mapping[str, str]],
    rows: Sequence[Mapping[str, Any]],
) -> str:
    if not schema:
        raise ValidationError(
            "query-build", "Fixture schema must not be empty."
        )
    columns = [
        (
            str(column["name"]),
            str(column["type"]),
        )
        for column in schema
    ]
    declaration = ", ".join(
        f"{_quote_column_name(name)}:{_datatable_type(column_type)}"
        for name, column_type in columns
    )
    values = [
        ", ".join(
            _datatable_value(row.get(name), column_type)
            for name, column_type in columns
        )
        for row in rows
    ]
    return (
        f"datatable({declaration})\n[\n"
        + ",\n".join(values)
        + "\n]"
    )


def build_exact_slice_expression(
    table_name: str,
    timestamps: Sequence[str],
) -> str:
    table_name = _require_identifier(table_name, "table_name")
    return (
        f"{table_name}\n"
        f"| where TimeGenerated in ({_timestamp_literals(timestamps)})"
    )


def _is_source_passthrough(filter_query: str) -> bool:
    statements = split_kql_statements(filter_query)
    if not statements:
        return False
    stages = split_pipeline(statements[-1])
    return len(stages) == 1 and stages[0].casefold() == "source"


def build_filter_count_query(
    filter_query: str,
    *,
    source_schema: Sequence[Mapping[str, str]],
    source_rows: Sequence[Mapping[str, Any]],
) -> str:
    source_expression = build_fixture_datatable(
        source_schema,
        source_rows,
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
) -> str:
    target_expression = build_exact_slice_expression(
        target_table,
        timestamps,
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
