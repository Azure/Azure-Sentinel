"""Field-level static validation for one ingestion-time parser."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .common import (
    IDENTIFIER_RE,
    MAX_DCR_TRANSFORM_KQL_CHARS,
    PARSER_NAME_RE,
    STREAM_NAME_RE,
    TARGET_TABLE_BY_SCHEMA,
    VALIDATION_RESULT_VERSION,
    VERSION_RE,
    Finding,
    _find_repo_root,
    _get_nested,
    load_yaml_file,
)
from .kql import (
    ALLOWED_DCR_OPERATORS,
    ALLOWED_FILTER_OPERATORS,
    KQL_RULES,
    _identity_key,
    _pipeline_operator,
    _query_uses_source_table,
    _validate_statement_shape,
    compact_kql,
    mask_kql,
    resolve_source_specific_fixture,
    split_kql_statements,
    split_pipeline,
)

def _require_string(
    document: dict[str, Any],
    findings: list[Finding],
    field: str,
    *keys: str,
) -> str | None:
    value = _get_nested(document, *keys)
    if not isinstance(value, str) or not value.strip():
        findings.append(
            Finding("META001", field, "Required field must be a non-empty string.")
        )
        return None
    return value.strip()


def _validate_date(
    value: str | None, field: str, findings: list[Finding]
) -> None:
    if value is None:
        return
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        findings.append(
            Finding("META002", field, "Date must use yyyy-MM-dd format.")
        )


def _validate_version(
    value: str | None, field: str, findings: list[Finding]
) -> None:
    if value is not None and not VERSION_RE.fullmatch(value):
        findings.append(
            Finding("META003", field, "Version must use X.X.X format.")
        )


def _scan_kql(query: str, field: str) -> list[Finding]:
    findings: list[Finding] = []
    masked_query = mask_kql(query)
    for rule in KQL_RULES:
        for match in rule.pattern.finditer(masked_query):
            line_number = masked_query.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    rule.code,
                    field,
                    f"Unsupported DCR construct '{rule.construct}'. {rule.message}",
                    line=line_number,
                )
            )
    return findings


def _validate_pipeline_operators(
    query: str,
    field: str,
    allowed_operators: set[str],
    findings: list[Finding],
) -> list[str]:
    final_statement = _validate_statement_shape(query, field, findings)
    if final_statement is None:
        return []
    stages = split_pipeline(final_statement)
    if not stages or stages[0].casefold() != "source":
        findings.append(
            Finding(
                "KQL039",
                field,
                "Query must be a single source-rooted pipeline.",
            )
        )
        return stages
    for stage_index, stage in enumerate(stages[1:], start=1):
        operator = _pipeline_operator(stage)
        if operator is None:
            findings.append(
                Finding(
                    "KQL040",
                    field,
                    f"Pipeline stage {stage_index} does not start with a recognized operator.",
                )
            )
        elif operator not in allowed_operators:
            findings.append(
                Finding(
                    "KQL041",
                    field,
                    f"Pipeline operator '{operator}' is not supported by the ingestion parser contract.",
                )
            )
    return stages


def _validate_filter_consistency(
    filter_query: str, parser_query: str, findings: list[Finding]
) -> None:
    filter_statements = split_kql_statements(filter_query)
    parser_statements = split_kql_statements(parser_query)
    if not filter_statements or not parser_statements:
        return
    filter_lets = filter_statements[:-1]
    parser_lets = parser_statements[:-1]
    parser_let_index = 0
    for filter_let in filter_lets:
        try:
            parser_let_index = parser_lets.index(
                filter_let, parser_let_index
            ) + 1
        except ValueError:
            findings.append(
                Finding(
                    "FILTER003",
                    "ParserFilterQuery",
                    "Every filter let statement must appear in ParserQuery in the same order.",
                )
            )
            return
    filter_stages = split_pipeline(filter_statements[-1])
    parser_stages = split_pipeline(parser_statements[-1])
    if not filter_stages or filter_stages[0].casefold() != "source":
        return
    filter_has_where = any(
        _pipeline_operator(stage) == "where"
        for stage in filter_stages[1:]
    )
    parser_has_where = any(
        _pipeline_operator(stage) == "where"
        for stage in parser_stages[1:]
    )
    if parser_has_where and not filter_has_where:
        findings.append(
            Finding(
                "FILTER004",
                "ParserFilterQuery",
                "ParserFilterQuery must contain a where stage when ParserQuery contains one.",
            )
        )
    if len(filter_stages) == 1:
        return
    if not filter_has_where:
        findings.append(
            Finding(
                "FILTER001",
                "ParserFilterQuery",
                "A non-pass-through filter must contain at least one where stage.",
            )
        )
    search_index = 1
    for filter_stage in filter_stages[1:]:
        try:
            found_index = parser_stages.index(filter_stage, search_index)
        except ValueError:
            findings.append(
                Finding(
                    "FILTER002",
                    "ParserFilterQuery",
                    "Every filter stage must appear in ParserQuery in the same order.",
                )
            )
            return
        search_index = found_index + 1


def _validate_fixture_contract(
    repo_root: Path | None,
    parser_query: str | None,
    schema: str | None,
    source_raw_table: str | None,
    findings: list[Finding],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "invalid",
        "eventVendor": None,
        "eventProduct": None,
        "path": None,
    }
    if (
        parser_query is None
        or schema is None
        or source_raw_table is None
    ):
        return result
    try:
        event_vendor, event_product, fixture_path = (
            resolve_source_specific_fixture(
                parser_query,
                schema,
                source_raw_table,
            )
        )
    except ValueError as exc:
        findings.append(
            Finding("FIXTURE001", "ParserQuery", str(exc))
        )
        return result

    result.update(
        {
            "eventVendor": event_vendor,
            "eventProduct": event_product,
            "path": fixture_path,
        }
    )
    if repo_root is None:
        findings.append(
            Finding(
                "FIXTURE002",
                "fixture",
                "Repository root is required to validate the resolved "
                f"fixture: {fixture_path}.",
            )
        )
        return result

    absolute_path = repo_root / fixture_path
    if not absolute_path.is_file():
        result["status"] = "missing"
        findings.append(
            Finding(
                "FIXTURE002",
                "fixture",
                f"Missing source-table-specific fixture: {fixture_path}.",
            )
        )
        return result

    try:
        with absolute_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or "Type" not in reader.fieldnames:
                raise ValueError("Fixture must contain a Type column.")
            type_values = {
                str(row.get("Type", "")).strip()
                for row in reader
                if str(row.get("Type", "")).strip()
            }
    except (OSError, UnicodeDecodeError, csv.Error, ValueError) as exc:
        findings.append(
            Finding(
                "FIXTURE003",
                "fixture",
                f"Invalid source-table-specific fixture "
                f"{fixture_path}: {exc}",
            )
        )
        return result

    if type_values != {source_raw_table}:
        findings.append(
            Finding(
                "FIXTURE004",
                "fixture.Type",
                f"Fixture Type values must be exactly "
                f"{source_raw_table!r}; found {sorted(type_values)}.",
            )
        )
        return result
    result["status"] = "resolved"
    return result


def validate_ingest_time_parser(
    parser_path: Path,
    query_time_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    findings: list[Finding] = []
    query_findings: list[Finding] = []
    document: dict[str, Any] | None = None
    try:
        document = load_yaml_file(parser_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        findings.append(Finding("YAML001", "document", str(exc)))

    metadata: dict[str, Any] = {}
    fixture_resolution: dict[str, Any] = {
        "status": "invalid",
        "eventVendor": None,
        "eventProduct": None,
        "path": None,
    }
    query_eligibility: dict[str, Any] = {
        "status": (
            "not-applicable"
            if query_time_path is None
            else "blocked"
        ),
        "supportsDisabled": False,
        "supportsPack": False,
    }
    if document is not None:
        display_name = _require_string(
            document, findings, "Parser.DisplayName", "Parser", "DisplayName"
        )
        parser_version = _require_string(
            document, findings, "Parser.Version", "Parser", "Version"
        )
        last_updated = _require_string(
            document, findings, "Parser.LastUpdated", "Parser", "LastUpdated"
        )
        product = _require_string(
            document, findings, "Product.Name", "Product", "Name"
        )
        schema = _require_string(
            document, findings, "Normalization.Schema", "Normalization", "Schema"
        )
        schema_version = _require_string(
            document,
            findings,
            "Normalization.Version",
            "Normalization",
            "Version",
        )
        author = _require_string(document, findings, "Author", "Author")
        description = _require_string(
            document, findings, "Description", "Description"
        )
        parser_name = _require_string(
            document, findings, "ParserName", "ParserName"
        )
        dcr_type = _require_string(document, findings, "DCRType", "DCRType")
        raw_input_stream = document.get("InputStream")
        input_stream = (
            raw_input_stream.strip()
            if isinstance(raw_input_stream, str)
            and raw_input_stream.strip()
            else None
        )
        source_raw_table = _require_string(
            document, findings, "SourceRawTable", "SourceRawTable"
        )
        target_asim_table = _require_string(
            document, findings, "TargetASIMTable", "TargetASIMTable"
        )
        filter_query = _require_string(
            document, findings, "ParserFilterQuery", "ParserFilterQuery"
        )
        parser_query = _require_string(
            document, findings, "ParserQuery", "ParserQuery"
        )
        raw_parser_query = _get_nested(document, "ParserQuery")
        change_date = _require_string(
            document, findings, "Change.Date", "Change", "Date"
        )
        change_description = _require_string(
            document,
            findings,
            "Change.Description",
            "Change",
            "Description",
        )

        _validate_version(parser_version, "Parser.Version", findings)
        _validate_version(schema_version, "Normalization.Version", findings)
        _validate_date(last_updated, "Parser.LastUpdated", findings)
        _validate_date(change_date, "Change.Date", findings)
        if (
            last_updated is not None
            and change_date is not None
            and last_updated != change_date
        ):
            findings.append(
                Finding(
                    "META004",
                    "Change.Date",
                    "Change.Date must match Parser.LastUpdated.",
                )
            )

        if parser_name is not None:
            if not PARSER_NAME_RE.fullmatch(parser_name):
                findings.append(
                    Finding(
                        "META005",
                        "ParserName",
                        "ParserName must match ^[A-Za-z][A-Za-z0-9_]+$.",
                    )
                )
            if schema and not parser_name.startswith(f"ASim{schema}"):
                findings.append(
                    Finding(
                        "META006",
                        "ParserName",
                        f"ParserName must start with ASim{schema}.",
                    )
                )
        if dcr_type is not None and dcr_type not in {"Standard", "Workspace"}:
            findings.append(
                Finding(
                    "META007",
                    "DCRType",
                    "DCRType must be Standard or Workspace.",
                )
            )
        if (
            dcr_type == "Standard"
            and (
                input_stream is None
                or input_stream.casefold() == "none"
            )
        ):
            findings.append(
                Finding(
                    "META008",
                    "InputStream",
                    "A Standard DCR parser must declare the stream that writes SourceRawTable.",
                )
            )
        if (
            input_stream is not None
            and input_stream.casefold() != "none"
            and not STREAM_NAME_RE.fullmatch(input_stream)
        ):
            findings.append(
                Finding(
                    "META009",
                    "InputStream",
                    "InputStream contains unsupported characters.",
                )
            )
        if source_raw_table is not None and not IDENTIFIER_RE.fullmatch(
            source_raw_table
        ):
            findings.append(
                Finding(
                    "META010",
                    "SourceRawTable",
                    "SourceRawTable must be a KQL identifier.",
                )
            )
        if schema is not None:
            expected_target = TARGET_TABLE_BY_SCHEMA.get(schema)
            if expected_target is None:
                findings.append(
                    Finding(
                        "META011",
                        "Normalization.Schema",
                        f"Unsupported ASIM schema '{schema}'.",
                    )
                )
            elif target_asim_table != expected_target:
                findings.append(
                    Finding(
                        "META012",
                        "TargetASIMTable",
                        f"{schema} parsers must target {expected_target}.",
                    )
                )

        effective_repo_root = repo_root or _find_repo_root(parser_path)

        if filter_query is not None:
            _validate_pipeline_operators(
                filter_query,
                "ParserFilterQuery",
                ALLOWED_FILTER_OPERATORS,
                findings,
            )
            findings.extend(_scan_kql(filter_query, "ParserFilterQuery"))
        if parser_query is not None:
            if isinstance(raw_parser_query, str):
                compacted_length = len(compact_kql(raw_parser_query))
                if compacted_length > MAX_DCR_TRANSFORM_KQL_CHARS:
                    findings.append(
                        Finding(
                            "KQL044",
                            "ParserQuery",
                            f"ParserQuery is {compacted_length} characters "
                            "after removing comments and indentation "
                            f"({len(raw_parser_query)} before compaction); "
                            "Azure DCR TransformKql supports at most "
                            f"{MAX_DCR_TRANSFORM_KQL_CHARS} characters.",
                        )
                    )
            _validate_pipeline_operators(
                parser_query,
                "ParserQuery",
                ALLOWED_DCR_OPERATORS,
                findings,
            )
            findings.extend(_scan_kql(parser_query, "ParserQuery"))
        if filter_query is not None and parser_query is not None:
            _validate_filter_consistency(filter_query, parser_query, findings)

        fixture_resolution = _validate_fixture_contract(
            effective_repo_root,
            parser_query,
            schema,
            source_raw_table,
            findings,
        )

        if query_time_path is not None:
            def block_query(
                code: str, field: str, message: str
            ) -> None:
                query_findings.append(
                    Finding(
                        code,
                        field,
                        message,
                        severity="blocked",
                    )
                )

            try:
                query_document = load_yaml_file(query_time_path)
            except (OSError, ValueError, yaml.YAMLError) as exc:
                block_query("PAIR001", "queryTimeParser", str(exc))
            else:
                query_schema = _get_nested(
                    query_document, "Normalization", "Schema"
                )
                query_product = _get_nested(query_document, "Product", "Name")
                query_parser_name = query_document.get("ParserName")
                query_body = query_document.get("ParserQuery")
                required_query_values = {
                    "ParserName": query_parser_name,
                    "Normalization.Schema": query_schema,
                    "Product.Name": query_product,
                    "ParserQuery": query_body,
                }
                for field, value in required_query_values.items():
                    if not isinstance(value, str) or not value.strip():
                        block_query(
                            "PAIR006",
                            field,
                            "Mapped query-time parser execution metadata "
                            "must be a non-empty string.",
                        )
                if schema != query_schema:
                    block_query(
                        "PAIR002",
                        "Normalization.Schema",
                        "Query-time and ingestion-time schemas must match.",
                    )
                if (
                    isinstance(product, str)
                    and isinstance(query_product, str)
                    and _identity_key(product)
                    != _identity_key(query_product)
                ):
                    block_query(
                        "PAIR004",
                        "Product.Name",
                        "Query-time and ingestion-time product identities "
                        "must match.",
                    )
                if (
                    source_raw_table is not None
                    and isinstance(query_body, str)
                    and not _query_uses_source_table(
                        query_body, source_raw_table
                    )
                ):
                    block_query(
                        "PAIR005",
                        "SourceRawTable",
                        "SourceRawTable is not used as a source table by "
                        "the mapped query-time parser.",
                    )
                parser_params = query_document.get("ParserParams")
                parameter_names = (
                    {
                        str(parameter.get("Name", "")).casefold()
                        for parameter in parser_params
                        if isinstance(parameter, dict)
                    }
                    if isinstance(parser_params, list)
                    else set()
                )
                query_eligibility["supportsDisabled"] = (
                    "disabled" in parameter_names
                )
                query_eligibility["supportsPack"] = (
                    "pack" in parameter_names
                )
            query_eligibility["status"] = (
                "blocked" if query_findings else "eligible"
            )

        metadata = {
            "displayName": display_name,
            "parserVersion": parser_version,
            "lastUpdated": last_updated,
            "product": product,
            "schema": schema,
            "schemaVersion": schema_version,
            "author": author,
            "description": description,
            "parserName": parser_name,
            "dcrType": dcr_type,
            "inputStream": input_stream,
            "sourceRawTable": source_raw_table,
            "targetASIMTable": target_asim_table,
            "changeDate": change_date,
            "changeDescription": change_description,
        }

    finding_dicts = [
        finding.to_dict()
        for finding in (*findings, *query_findings)
    ]
    return {
        "version": VALIDATION_RESULT_VERSION,
        "path": str(parser_path),
        "queryTimeParserPath": str(query_time_path)
        if query_time_path is not None
        else None,
        "valid": not any(
            finding["severity"] == "error" for finding in finding_dicts
        ),
        "metadata": metadata,
        "fixtureResolution": fixture_resolution,
        "queryTimeEligibility": query_eligibility,
        "findings": finding_dicts,
    }
