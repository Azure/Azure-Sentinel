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
from .kusto_analyzer import KustoAnalyzerError, analyze_kql
from .kql import (
    ALLOWED_DCR_OPERATORS,
    ALLOWED_FILTER_OPERATORS,
    ASIM_HELPER_RULE,
    KQL_CONSTRUCT_RULES,
    KQL_FUNCTION_RULES,
    KQL_OPERATOR_RULES,
    KqlRule,
    _identity_key,
    query_uses_source_table,
    resolve_source_specific_fixture,
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


def _finding_for_kql_fact(
    rule: KqlRule,
    field: str,
    fact: dict[str, Any],
) -> Finding:
    location = fact.get("location", {})
    line = location.get("line")
    return Finding(
        rule.code,
        field,
        f"Unsupported DCR construct '{rule.construct}'. {rule.message}",
        line=line if isinstance(line, int) else None,
    )


def _scan_kql(
    analysis: dict[str, Any],
    field: str,
) -> list[Finding]:
    matches: list[tuple[str, int, Finding]] = []

    def add(rule: KqlRule, fact: dict[str, Any]) -> None:
        location = fact.get("location", {})
        start = location.get("start")
        matches.append(
            (
                rule.code,
                start if isinstance(start, int) else -1,
                _finding_for_kql_fact(rule, field, fact),
            )
        )

    for operator in analysis["operators"]:
        rule = KQL_OPERATOR_RULES.get(operator["type"])
        if rule is not None:
            add(rule, operator)
    for function in analysis["functions"]:
        name = function.get("name")
        rule = (
            KQL_FUNCTION_RULES.get(name.casefold())
            if isinstance(name, str)
            else None
        )
        if rule is not None:
            add(rule, function)
    for construct in analysis["constructs"]:
        name = construct.get("name")
        if (
            isinstance(name, str)
            and name.casefold().startswith("_asim_")
        ):
            add(ASIM_HELPER_RULE, construct)
            continue
        kind = construct["kind"]
        rule = KQL_CONSTRUCT_RULES.get(kind)
        if rule is None:
            rule = KQL_CONSTRUCT_RULES.get(construct["type"])
        if rule is None:
            continue
        if (
            kind == "WildcardedName"
            and construct.get("ownerOperator")
            not in {"ProjectAwayOperator", "ProjectKeepOperator"}
        ):
            continue
        add(rule, construct)
    return [
        finding
        for _, _, finding in sorted(
            matches,
            key=lambda match: (match[0], match[1]),
        )
    ]


def _validate_statement_shape(
    analysis: dict[str, Any],
    field: str,
    findings: list[Finding],
) -> dict[str, Any] | None:
    statements = analysis["statements"]
    if not statements:
        findings.append(
            Finding("KQL039", field, "Query must not be empty.")
        )
        return None
    for statement in statements[:-1]:
        location = statement["location"]
        line = location.get("line")
        if statement["type"] != "LetStatement":
            findings.append(
                Finding(
                    "KQL042",
                    field,
                    "Only let statements may precede the final source pipeline.",
                    line=line if isinstance(line, int) else None,
                )
            )
            continue
        if not statement["hasPipe"]:
            continue
        root_type = statement.get("expressionRootType")
        root_text = statement.get("expressionRootText")
        allowed_root = (
            root_type
            in {
                "DataTableExpression",
                "FunctionDeclaration",
                "ParenthesizedExpression",
                "PrintOperator",
            }
            or (
                root_type == "NameReference"
                and isinstance(root_text, str)
                and root_text.casefold() == "source"
            )
        )
        if not allowed_root:
            findings.append(
                Finding(
                    "KQL043",
                    field,
                    "A tabular let binding may only use source, print, or datatable.",
                    line=line if isinstance(line, int) else None,
                )
            )
    return analysis.get("pipeline")


def _operator_name(operator: dict[str, Any]) -> str | None:
    location = operator.get("location")
    text = location.get("text") if isinstance(location, dict) else None
    if not isinstance(text, str):
        return None
    parts = text.split(maxsplit=1)
    return parts[0].casefold() if parts else None


def _validate_pipeline_operators(
    analysis: dict[str, Any],
    field: str,
    allowed_operators: set[str],
    findings: list[Finding],
) -> None:
    pipeline = _validate_statement_shape(analysis, field, findings)
    if pipeline is None:
        if analysis["statements"]:
            findings.append(
                Finding(
                    "KQL039",
                    field,
                    "Query must be a single source-rooted pipeline.",
                )
            )
        return
    root_text = pipeline.get("rootText")
    if (
        pipeline.get("rootType") != "NameReference"
        or not isinstance(root_text, str)
        or root_text.casefold() != "source"
    ):
        findings.append(
            Finding(
                "KQL039",
                field,
                "Query must be a single source-rooted pipeline.",
            )
        )
        return
    for stage_index, operator_fact in enumerate(
        pipeline["operators"],
        start=1,
    ):
        operator = _operator_name(operator_fact)
        location = operator_fact.get("location", {})
        line = location.get("line")
        if operator is None:
            findings.append(
                Finding(
                    "KQL040",
                    field,
                    f"Pipeline stage {stage_index} does not start with a recognized operator.",
                    line=line if isinstance(line, int) else None,
                )
            )
        elif operator not in allowed_operators:
            findings.append(
                Finding(
                    "KQL041",
                    field,
                    f"Pipeline operator '{operator}' is not supported by the ingestion parser contract.",
                    line=line if isinstance(line, int) else None,
                )
            )


def _validate_kql(
    query: str,
    field: str,
    allowed_operators: set[str],
    findings: list[Finding],
) -> dict[str, Any] | None:
    try:
        analysis = analyze_kql(query)
    except KustoAnalyzerError as exc:
        findings.append(
            Finding(
                "KQL000",
                field,
                f"Trusted Kusto.Language analyzer failed: {exc}",
            )
        )
        return None

    diagnostics = analysis["diagnostics"]
    for diagnostic in diagnostics:
        findings.append(
            Finding(
                "KQL001",
                field,
                "Kusto syntax diagnostic "
                f"{diagnostic['code']} at column "
                f"{diagnostic['column']}: {diagnostic['message']}",
                line=diagnostic["line"],
            )
        )
    if diagnostics:
        return analysis

    _validate_pipeline_operators(
        analysis,
        field,
        allowed_operators,
        findings,
    )
    findings.extend(_scan_kql(analysis, field))
    return analysis


def _validate_filter_consistency(
    filter_analysis: dict[str, Any],
    parser_analysis: dict[str, Any],
    findings: list[Finding],
) -> None:
    filter_statements = filter_analysis["statements"]
    parser_statements = parser_analysis["statements"]
    if not filter_statements or not parser_statements:
        return
    filter_lets = [
        statement["location"]["normalizedText"]
        for statement in filter_statements[:-1]
    ]
    parser_lets = [
        statement["location"]["normalizedText"]
        for statement in parser_statements[:-1]
    ]
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
    filter_pipeline = filter_analysis.get("pipeline")
    parser_pipeline = parser_analysis.get("pipeline")
    if (
        not isinstance(filter_pipeline, dict)
        or filter_pipeline.get("rootType") != "NameReference"
        or str(filter_pipeline.get("rootText", "")).casefold() != "source"
        or not isinstance(parser_pipeline, dict)
    ):
        return
    filter_operators = filter_pipeline["operators"]
    parser_operators = parser_pipeline["operators"]
    filter_has_where = any(
        operator["type"] == "FilterOperator"
        for operator in filter_operators
    )
    parser_has_where = any(
        operator["type"] == "FilterOperator"
        for operator in parser_operators
    )
    if parser_has_where and not filter_has_where:
        findings.append(
            Finding(
                "FILTER004",
                "ParserFilterQuery",
                "ParserFilterQuery must contain a where stage when ParserQuery contains one.",
            )
        )
    if not filter_operators:
        return
    if not filter_has_where:
        findings.append(
            Finding(
                "FILTER001",
                "ParserFilterQuery",
                "A non-pass-through filter must contain at least one where stage.",
            )
        )
    parser_stages = [
        operator["location"]["normalizedText"]
        for operator in parser_operators
    ]
    search_index = 0
    for filter_operator in filter_operators:
        filter_stage = filter_operator["location"]["normalizedText"]
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
    parser_analysis: dict[str, Any] | None,
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
        parser_analysis is None
        or schema is None
        or source_raw_table is None
    ):
        return result
    try:
        event_vendor, event_product, fixture_path = (
            resolve_source_specific_fixture(
                parser_analysis,
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
        filter_analysis: dict[str, Any] | None = None
        parser_analysis: dict[str, Any] | None = None

        if filter_query is not None:
            filter_analysis = _validate_kql(
                filter_query,
                "ParserFilterQuery",
                ALLOWED_FILTER_OPERATORS,
                findings,
            )
        if parser_query is not None:
            if isinstance(raw_parser_query, str):
                query_length = len(raw_parser_query)
                if query_length > MAX_DCR_TRANSFORM_KQL_CHARS:
                    findings.append(
                        Finding(
                            "KQL044",
                            "ParserQuery",
                            f"ParserQuery is {query_length} characters; "
                            "Azure DCR TransformKql supports at most "
                            f"{MAX_DCR_TRANSFORM_KQL_CHARS} characters.",
                        )
                    )
            parser_analysis = _validate_kql(
                parser_query,
                "ParserQuery",
                ALLOWED_DCR_OPERATORS,
                findings,
            )
        if (
            filter_analysis is not None
            and parser_analysis is not None
            and not filter_analysis["diagnostics"]
            and not parser_analysis["diagnostics"]
        ):
            _validate_filter_consistency(
                filter_analysis,
                parser_analysis,
                findings,
            )

        fixture_resolution = _validate_fixture_contract(
            effective_repo_root,
            parser_analysis,
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
                query_analysis: dict[str, Any] | None = None
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
                if isinstance(query_body, str) and query_body.strip():
                    try:
                        query_analysis = analyze_kql(query_body)
                    except KustoAnalyzerError as exc:
                        block_query(
                            "KQL000",
                            "ParserQuery",
                            "Trusted Kusto.Language analyzer failed: "
                            f"{exc}",
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
                    and query_analysis is not None
                    and not query_uses_source_table(
                        query_analysis,
                        source_raw_table,
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
