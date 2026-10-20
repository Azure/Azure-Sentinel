#!/usr/bin/env python3
"""Discover and statically validate ASIM ingestion-time parser targets.

Examples:
  python asim_ingest_time_validation.py discover --base-ref upstream/master
  python asim_ingest_time_validation.py validate \
      Parsers/ASimAuthentication/IngestTimeParsers/ASimAuthenticationOktaV2.yaml \
      --query-time-path Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaV2.yaml
"""

from __future__ import annotations

import argparse
import csv
import functools
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence

import yaml


MANIFEST_VERSION = 2
VALIDATION_RESULT_VERSION = 2
MAX_YAML_BYTES = 1024 * 1024

QUERY_TIME_PATH_RE = re.compile(
    r"^Parsers/ASim(?P<schema>[^/]+)/Parsers/(?P<name>ASim[^/]+)\.yaml$"
)
INGEST_TIME_PATH_RE = re.compile(
    r"^Parsers/ASim(?P<schema>[^/]+)/IngestTimeParsers/(?P<name>[^/]+)\.yaml$"
)
FIXTURE_PATH_RE = re.compile(
    r"^Sample Data/ASIM/[^/]+_IngestedLogs\.csv$"
)
PARSER_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]+$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
STREAM_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

ADDITIONAL_UNION_PARSERS = {
    "ProcessEvent": {
        "ASimProcessEventCreate.yaml",
        "ASimProcessEventTerminate.yaml",
    }
}

TARGET_TABLE_BY_SCHEMA = {
    "AgentEvent": "ASimAgentEventLogs",
    "AlertEvent": "ASimAlertEventLogs",
    "AssetEntity": "ASimAssetEntityLogs",
    "AuditEvent": "ASimAuditEventLogs",
    "Authentication": "ASimAuthenticationEventLogs",
    "DhcpEvent": "ASimDhcpEventLogs",
    "Dns": "ASimDnsActivityLogs",
    "EmailEvent": "ASimEmailEventLogs",
    "FileEvent": "ASimFileEventLogs",
    "NetworkSession": "ASimNetworkSessionLogs",
    "ProcessEvent": "ASimProcessEventLogs",
    "RegistryEvent": "ASimRegistryEventLogs",
    "UserManagement": "ASimUserManagementActivityLogs",
    "WebSession": "ASimWebSessionLogs",
}

ALLOWED_DCR_OPERATORS = {
    "extend",
    "parse",
    "project",
    "project-away",
    "project-rename",
    "where",
}
ALLOWED_FILTER_OPERATORS = {
    "extend",
    "parse",
    "project-rename",
    "where",
}


@dataclass(frozen=True)
class KqlRule:
    code: str
    construct: str
    pattern: re.Pattern[str]
    message: str


KQL_RULES = (
    KqlRule("KQL002", "invoke", re.compile(r"\|\s*invoke\b", re.I), "Inline the invoked function."),
    KqlRule("KQL003", "ASIM helper", re.compile(r"\b_ASIM_[A-Za-z0-9_]+", re.I), "Inline ASIM helper functions."),
    KqlRule("KQL004", "lookup", re.compile(r"\|\s*lookup\b", re.I), "Replace lookup with DCR-compatible scalar mapping."),
    KqlRule("KQL006", "union", re.compile(r"(^|\|)\s*union\b", re.I), "A DCR parser must use one source pipeline."),
    KqlRule("KQL007", "distinct", re.compile(r"\|\s*distinct\b", re.I), "Per-row transformations cannot deduplicate records."),
    KqlRule("KQL008", "materialize", re.compile(r"\bmaterialize\s*\(", re.I), "Remove the query-time caching hint."),
    KqlRule("KQL009", "project-reorder", re.compile(r"\|\s*project-reorder\b", re.I), "Column order is not part of the DCR contract."),
    KqlRule("KQL010", "dynamic literal", re.compile(r"\bdynamic\s*\(", re.I), "Use parse_json for dynamic literals."),
    KqlRule("KQL011", "has_any", re.compile(r"\bhas_any\s*\(", re.I), "Expand to supported scalar comparisons."),
    KqlRule("KQL012", "has_all", re.compile(r"\bhas_all\s*\(", re.I), "Expand to supported scalar comparisons."),
    KqlRule("KQL013", "coalesce", re.compile(r"\bcoalesce\s*\(", re.I), "Rewrite with iif and null or empty checks."),
    KqlRule("KQL014", "parse-kv", re.compile(r"\|\s*parse-kv\b", re.I), "Rewrite with supported parsing expressions."),
    KqlRule("KQL015", "parse-where", re.compile(r"\|\s*parse-where\b", re.I), "Rewrite with parse or extract plus where."),
    KqlRule("KQL016", "case-insensitive operator", re.compile(r"==~|!=~|\bin~|\b!in~", re.I), "Normalize operands and use the supported operator."),
    KqlRule("KQL017", "column_ifexists", re.compile(r"\bcolumn_ifexists\s*\(", re.I), "Use columnifexists or a confirmed source column."),
    KqlRule("KQL018", "Unix time conversion", re.compile(r"\bunixtime_(milliseconds|seconds|microseconds|nanoseconds)_todatetime\s*\(", re.I), "Rewrite with datetime arithmetic."),
    KqlRule("KQL019", "between", re.compile(r"\b!?between\s*\(", re.I), "Rewrite as explicit comparisons."),
    KqlRule("KQL020", "bag_pack", re.compile(r"\bbag_pack(_columns)?\s*\(", re.I), "Use pack or an explicit supported projection."),
    KqlRule("KQL021", "replace_string", re.compile(r"\breplace_string\s*\(", re.I), "Use the DCR-supported replace form."),
    KqlRule("KQL022", "array_index_of", re.compile(r"\barray_index_of\s*\(", re.I), "Rewrite as supported scalar logic."),
    KqlRule("KQL023", "array_slice", re.compile(r"\barray_slice\s*\(", re.I), "Rewrite with indexof and substring."),
    KqlRule("KQL024", "trim", re.compile(r"\btrim(_start|_end)?\s*\(", re.I), "Rewrite with anchored replace."),
    KqlRule("KQL025", "parse_url", re.compile(r"\bparse_url\s*\(", re.I), "Extract only the required URL components."),
    KqlRule("KQL026", "parse_user_agent", re.compile(r"\bparse_user_agent\s*\(", re.I), "Extract only the required user-agent fields."),
    KqlRule("KQL027", "mv operator", re.compile(r"\|\s*mv-(apply|expand)\b", re.I), "DCR transformations cannot fan out rows."),
    KqlRule("KQL028", "summarize", re.compile(r"\|\s*summarize\b", re.I), "DCR transformations process each record independently."),
    KqlRule("KQL029", "aggregation function", re.compile(r"\b(make_set|make_list|make_set_if|make_list_if|take_anyif|take_any)\s*\(", re.I), "Aggregation functions are not supported."),
    KqlRule("KQL030", "bag_merge", re.compile(r"\bbag_merge\s*\(", re.I), "No sound DCR equivalent is available."),
    KqlRule("KQL031", "join", re.compile(r"\|\s*join\b", re.I), "A DCR transformation has one input stream."),
    KqlRule("KQL032", "tohex", re.compile(r"\btohex\s*\(", re.I), "No general DCR equivalent is available."),
    KqlRule(
        "KQL033",
        "IP utility",
        re.compile(
            r"\b(ipv4_is_in_range|ipv4_is_match|ipv4_is_private|parse_ipv4|"
            r"parse_ipv6|ipv6_is_match|ipv4_netmask_suffix)\s*\(",
            re.I,
        ),
        "The IP utility is not supported by DCR transformations.",
    ),
    KqlRule("KQL034", "url_decode", re.compile(r"\burl_decode\s*\(", re.I), "No exact DCR equivalent is available."),
    KqlRule("KQL035", "toscalar", re.compile(r"\btoscalar\s*\(", re.I), "Subqueries are not supported by the parser contract."),
    KqlRule("KQL036", "project-keep", re.compile(r"\|\s*project-keep\b", re.I), "Emit an explicit supported projection."),
    KqlRule("KQL037", "wildcard projection", re.compile(r"\|\s*project-(away|keep)\s+[^|\r\n]*\*", re.I), "Resolve wildcard projections explicitly."),
    KqlRule("KQL038", "externaldata", re.compile(r"\bexternaldata\s*\(", re.I), "External data sources cannot be used in a DCR transformation."),
)


class DuplicateKeyError(ValueError):
    """Raised when a YAML mapping contains the same key more than once."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(
                f"Duplicate YAML key '{key}' at line {key_node.start_mark.line + 1}."
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True)
class Finding:
    code: str
    field: str
    message: str
    line: int | None = None
    severity: str = "error"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "field": self.field,
            "message": self.message,
        }
        if self.line is not None:
            payload["line"] = self.line
        return payload


@dataclass(frozen=True)
class ParserRecord:
    path: str
    kind: str
    document: dict[str, Any]
    parser_name: str
    schema: str
    schema_version: str | None
    product: str
    parser_query: str
    source_raw_table: str | None = None
    target_asim_table: str | None = None
    event_vendor: str | None = None
    event_product: str | None = None
    fixture_path: str | None = None
    fixture_errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class PairResolution:
    status: str
    selected: ParserRecord | None
    candidates: tuple[ParserRecord, ...]
    evidence: dict[str, Any]


def _get_nested(document: dict[str, Any], *keys: str) -> Any:
    value: Any = document
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _repo_relative_path(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def normalize_changed_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    pure_path = PurePosixPath(normalized)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        raise ValueError(f"Changed path must stay inside the repository: {path}")
    return pure_path.as_posix().lstrip("./")


def classify_parser_path(path: str) -> str | None:
    normalized = normalize_changed_path(path)
    if INGEST_TIME_PATH_RE.fullmatch(normalized):
        return "ingest-time"
    match = QUERY_TIME_PATH_RE.fullmatch(normalized)
    if not match:
        return None
    schema = match.group("schema")
    filename = PurePosixPath(normalized).name
    if filename == f"ASim{schema}.yaml":
        return None
    if filename in ADDITIONAL_UNION_PARSERS.get(schema, set()):
        return None
    return "query-time"


def classify_changed_path(path: str) -> str | None:
    normalized = normalize_changed_path(path)
    parser_kind = classify_parser_path(normalized)
    if parser_kind is not None:
        return parser_kind
    if FIXTURE_PATH_RE.fullmatch(normalized):
        return "fixture"
    return None


def load_yaml_file(path: Path) -> dict[str, Any]:
    file_size = path.stat().st_size
    if file_size > MAX_YAML_BYTES:
        raise ValueError(
            f"{path} exceeds the {MAX_YAML_BYTES}-byte YAML limit."
        )
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path} must be UTF-8 text.") from exc
    document = yaml.load(content, Loader=UniqueKeyLoader)
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the document root.")
    return document


def _find_repo_root(path: Path) -> Path | None:
    matches: list[Path] = []
    for candidate in (path.parent, *path.parents):
        if (candidate / "Parsers").is_dir():
            matches.append(candidate)
    return matches[-1] if matches else None


def _collect_output_streams(value: Any) -> set[str]:
    streams: set[str] = set()
    if isinstance(value, dict):
        output_stream = value.get("outputStream")
        if isinstance(output_stream, str):
            streams.add(output_stream)
        for child in value.values():
            streams.update(_collect_output_streams(child))
    elif isinstance(value, list):
        for child in value:
            streams.update(_collect_output_streams(child))
    return streams


def _collect_dcr_resources(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        resource_type = value.get("type")
        if (
            isinstance(resource_type, str)
            and resource_type.casefold()
            == "microsoft.insights/datacollectionrules"
        ):
            yield value
        for child in value.values():
            yield from _collect_dcr_resources(child)
    elif isinstance(value, list):
        for child in value:
            yield from _collect_dcr_resources(child)


@functools.lru_cache(maxsize=128)
def find_dcr_output_stream_evidence(
    repo_root_text: str, output_stream: str
) -> tuple[str, ...]:
    repo_root = Path(repo_root_text)
    candidate_paths: set[Path] = set()
    if (repo_root / ".git").exists():
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "grep",
                "-l",
                "-F",
                output_stream,
                "--",
                "Solutions/**/*.json",
                "DataConnectors/**/*.json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        candidate_paths.update(
            repo_root / line
            for line in result.stdout.splitlines()
            if "/Data Connectors/" in line.replace("\\", "/")
            or line.replace("\\", "/").startswith("DataConnectors/")
        )
    else:
        solutions_root = repo_root / "Solutions"
        if solutions_root.is_dir():
            candidate_paths.update(
                solutions_root.glob("*/Data Connectors/**/*.json")
            )
        data_connectors_root = repo_root / "DataConnectors"
        if data_connectors_root.is_dir():
            candidate_paths.update(data_connectors_root.rglob("*.json"))

    evidence_paths: set[str] = set()
    for path in sorted(candidate_paths):
        try:
            raw = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        if "outputStream" not in raw:
            continue
        try:
            document = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for resource in _collect_dcr_resources(document):
            if output_stream in _collect_output_streams(resource):
                evidence_paths.add(_repo_relative_path(repo_root, path))
    return tuple(sorted(evidence_paths))


def mask_kql(text: str) -> str:
    """Mask comments and string contents while preserving positions and lines."""
    chars = list(text)
    index = 0
    length = len(chars)
    while index < length:
        char = chars[index]
        if char == "/" and index + 1 < length and chars[index + 1] == "/":
            while index < length and chars[index] != "\n":
                if chars[index] != "\r":
                    chars[index] = " "
                index += 1
            continue
        if (
            char == "@"
            and index + 1 < length
            and chars[index + 1] in {'"', "'"}
        ):
            quote = chars[index + 1]
            chars[index] = " "
            chars[index + 1] = " "
            index += 2
            while index < length:
                if chars[index] == quote:
                    if index + 1 < length and chars[index + 1] == quote:
                        chars[index] = " "
                        chars[index + 1] = " "
                        index += 2
                        continue
                    chars[index] = " "
                    index += 1
                    break
                if chars[index] not in {"\r", "\n"}:
                    chars[index] = " "
                index += 1
            continue
        if char in {'"', "'"}:
            quote = char
            chars[index] = " "
            index += 1
            while index < length:
                if chars[index] == "\\" and index + 1 < length:
                    chars[index] = " "
                    index += 1
                    if chars[index] not in {"\r", "\n"}:
                        chars[index] = " "
                    index += 1
                    continue
                if chars[index] == quote:
                    if index + 1 < length and chars[index + 1] == quote:
                        chars[index] = " "
                        chars[index + 1] = " "
                        index += 2
                        continue
                    chars[index] = " "
                    index += 1
                    break
                if chars[index] not in {"\r", "\n"}:
                    chars[index] = " "
                index += 1
            continue
        index += 1
    return "".join(chars)


def _canonical_kql(value: str) -> str:
    output: list[str] = []
    index = 0
    length = len(value)
    quote: str | None = None
    verbatim = False
    pending_space = False
    while index < length:
        char = value[index]
        if quote is not None:
            output.append(char)
            if char == quote:
                if index + 1 < length and value[index + 1] == quote:
                    output.append(value[index + 1])
                    index += 2
                    continue
                quote = None
                verbatim = False
            elif not verbatim and char == "\\" and index + 1 < length:
                output.append(value[index + 1])
                index += 2
                continue
            index += 1
            continue
        if char.isspace():
            pending_space = True
            index += 1
            continue
        if pending_space and output:
            output.append(" ")
        pending_space = False
        if (
            char == "@"
            and index + 1 < length
            and value[index + 1] in {'"', "'"}
        ):
            verbatim = True
            quote = value[index + 1]
            output.append(char)
            output.append(quote)
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
        output.append(char)
        index += 1
    return "".join(output).strip()


def split_pipeline(query: str) -> list[str]:
    parts: list[str] = []
    buffer: list[str] = []
    index = 0
    length = len(query)
    quote: str | None = None
    verbatim = False
    while index < length:
        char = query[index]
        if quote is not None:
            buffer.append(char)
            if char == quote:
                if index + 1 < length and query[index + 1] == quote:
                    buffer.append(query[index + 1])
                    index += 2
                    continue
                quote = None
                verbatim = False
            elif not verbatim and char == "\\" and index + 1 < length:
                buffer.append(query[index + 1])
                index += 2
                continue
            index += 1
            continue
        if char == "/" and index + 1 < length and query[index + 1] == "/":
            while index < length and query[index] != "\n":
                index += 1
            buffer.append(" ")
            continue
        if (
            char == "@"
            and index + 1 < length
            and query[index + 1] in {'"', "'"}
        ):
            verbatim = True
            quote = query[index + 1]
            buffer.append(char)
            buffer.append(quote)
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
            buffer.append(char)
            index += 1
            continue
        if char == "|":
            parts.append(_canonical_kql("".join(buffer)))
            buffer = []
            index += 1
            continue
        buffer.append(char)
        index += 1
    parts.append(_canonical_kql("".join(buffer)))
    return parts


def split_kql_statements(query: str) -> list[str]:
    """Split top-level KQL statements while preserving strings and function bodies."""
    statements: list[str] = []
    buffer: list[str] = []
    index = 0
    length = len(query)
    quote: str | None = None
    verbatim = False
    line_comment = False
    paren_depth = 0
    brace_depth = 0
    bracket_depth = 0
    while index < length:
        char = query[index]
        if line_comment:
            if char == "\n":
                line_comment = False
                buffer.append(" ")
            index += 1
            continue
        if quote is not None:
            buffer.append(char)
            if char == quote:
                if index + 1 < length and query[index + 1] == quote:
                    buffer.append(query[index + 1])
                    index += 2
                    continue
                quote = None
                verbatim = False
            elif not verbatim and char == "\\" and index + 1 < length:
                buffer.append(query[index + 1])
                index += 2
                continue
            index += 1
            continue
        if char == "/" and index + 1 < length and query[index + 1] == "/":
            line_comment = True
            index += 2
            continue
        if (
            char == "@"
            and index + 1 < length
            and query[index + 1] in {'"', "'"}
        ):
            verbatim = True
            quote = query[index + 1]
            buffer.append(char)
            buffer.append(quote)
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
            buffer.append(char)
            index += 1
            continue
        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth = max(0, paren_depth - 1)
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth = max(0, brace_depth - 1)
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth = max(0, bracket_depth - 1)
        elif (
            char == ";"
            and paren_depth == 0
            and brace_depth == 0
            and bracket_depth == 0
        ):
            statement = _canonical_kql("".join(buffer))
            if statement:
                statements.append(statement)
            buffer = []
            index += 1
            continue
        buffer.append(char)
        index += 1
    statement = _canonical_kql("".join(buffer))
    if statement:
        statements.append(statement)
    return statements


def _pipeline_operator(stage: str) -> str | None:
    match = re.match(r"([a-z][a-z0-9-]*)\b", stage, re.I)
    return match.group(1).lower() if match else None


def _validate_statement_shape(
    query: str, field: str, findings: list[Finding]
) -> str | None:
    statements = split_kql_statements(query)
    if not statements:
        findings.append(
            Finding("KQL039", field, "Query must not be empty.")
        )
        return None
    for statement in statements[:-1]:
        let_match = re.match(
            r"let\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?P<rhs>.+)$",
            statement,
            re.I | re.S,
        )
        if let_match is None:
            findings.append(
                Finding(
                    "KQL042",
                    field,
                    "Only let statements may precede the final source pipeline.",
                )
            )
            continue
        rhs = let_match.group("rhs").strip()
        if "|" in rhs:
            root_match = re.match(
                r"(source|print|datatable\b)",
                rhs,
                re.I,
            )
            if root_match is None and not rhs.startswith("("):
                findings.append(
                    Finding(
                        "KQL043",
                        field,
                        "A tabular let binding may only use source, print, or datatable.",
                    )
                )
    return statements[-1]


def _query_uses_source_table(query: str, table_name: str) -> bool:
    masked_query = mask_kql(query)
    identifier_pattern = re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(table_name)}(?![A-Za-z0-9_])",
        re.I,
    )
    for match in identifier_pattern.finditer(masked_query):
        line_start = masked_query.rfind("\n", 0, match.start()) + 1
        line_end = masked_query.find("\n", match.end())
        if line_end < 0:
            line_end = len(masked_query)
        prefix = masked_query[line_start:match.start()].rstrip()
        suffix = masked_query[match.end():line_end].lstrip()
        source_position = (
            not prefix
            or prefix[-1:] in {"{", "(", ",", "=", ";"}
            or bool(
                re.search(
                    r"\bunion(?:\s+[A-Za-z_][A-Za-z0-9_]*"
                    r"\s*=\s*\S+)*\s*$",
                    prefix,
                    re.I,
                )
            )
        )
        source_terminator = not suffix or suffix[0] in {"|", ",", ")"}
        if source_position and source_terminator:
            return True
    return False


def _parse_kql_string_literal(
    query: str, start: int
) -> tuple[str, int] | None:
    index = start
    while index < len(query) and query[index].isspace():
        index += 1
    verbatim = False
    if (
        index + 1 < len(query)
        and query[index] == "@"
        and query[index + 1] in {"'", '"'}
    ):
        verbatim = True
        index += 1
    if index >= len(query) or query[index] not in {"'", '"'}:
        return None
    quote = query[index]
    index += 1
    value: list[str] = []
    escapes = {
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "\\": "\\",
        "'": "'",
        '"': '"',
    }
    while index < len(query):
        char = query[index]
        if char == quote:
            if index + 1 < len(query) and query[index + 1] == quote:
                value.append(quote)
                index += 2
                continue
            return "".join(value), index + 1
        if not verbatim and char == "\\":
            if index + 1 >= len(query):
                raise ValueError("KQL string literal ends with an escape.")
            escaped = query[index + 1]
            value.append(escapes.get(escaped, escaped))
            index += 2
            continue
        value.append(char)
        index += 1
    raise ValueError("KQL string literal is not terminated.")


def _resolve_static_string_assignment(query: str, field: str) -> str:
    masked_query = mask_kql(query)
    assignment_pattern = re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(field)}"
        r"(?![A-Za-z0-9_])\s*=",
        re.I,
    )
    matches = list(assignment_pattern.finditer(masked_query))
    if not matches:
        raise ValueError(
            f"ParserQuery does not assign a static {field} value."
        )
    values: list[str] = []
    for match in matches:
        parsed = _parse_kql_string_literal(query, match.end())
        if parsed is None:
            raise ValueError(
                f"ParserQuery assigns {field} from a non-static expression."
            )
        values.append(parsed[0])
    unique_values = sorted(set(values))
    if len(unique_values) != 1:
        raise ValueError(
            f"ParserQuery assigns conflicting {field} values: "
            f"{unique_values}."
        )
    value = unique_values[0]
    if not value:
        raise ValueError(f"ParserQuery assigns an empty {field} value.")
    if any(
        ord(char) < 32 or char in '<>:"/\\|?*'
        for char in value
    ):
        raise ValueError(
            f"ParserQuery {field} value cannot be used in a fixture name: "
            f"{value!r}."
        )
    return value


def resolve_source_specific_fixture(
    parser_query: str,
    schema: str,
    source_raw_table: str,
) -> tuple[str, str, str]:
    event_vendor = _resolve_static_string_assignment(
        parser_query, "EventVendor"
    )
    event_product = _resolve_static_string_assignment(
        parser_query, "EventProduct"
    )
    fixture_name = (
        f"{event_vendor}_{event_product}_{schema}_{source_raw_table}"
        "_IngestedLogs.csv"
    )
    return (
        event_vendor,
        event_product,
        f"Sample Data/ASIM/{fixture_name}",
    )


def _identity_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _name_tokens(value: str) -> list[str]:
    words = re.findall(r"[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|\d+", value)
    return [
        word.lower()
        for word in words
        if word.lower()
        not in {
            "a",
            "asim",
            "ingest",
            "ingestion",
            "parser",
            "sim",
            "time",
        }
    ]


def _token_overlap(first: str, second: str) -> list[str]:
    return sorted(set(_name_tokens(first)) & set(_name_tokens(second)))


def build_parser_record(repo_root: Path, relative_path: str) -> ParserRecord:
    kind = classify_parser_path(relative_path)
    if kind is None:
        raise ValueError(f"Not a supported ASIM parser path: {relative_path}")
    document = load_yaml_file(repo_root / relative_path)
    parser_name = document.get("ParserName")
    schema = _get_nested(document, "Normalization", "Schema")
    schema_version = _get_nested(document, "Normalization", "Version")
    product = _get_nested(document, "Product", "Name")
    parser_query = document.get("ParserQuery")
    required_values = {
        "ParserName": parser_name,
        "Normalization.Schema": schema,
        "Product.Name": product,
        "ParserQuery": parser_query,
    }
    if kind == "ingest-time":
        required_values["Normalization.Version"] = schema_version
    missing = [
        name
        for name, value in required_values.items()
        if not isinstance(value, str) or not value.strip()
    ]
    if missing:
        raise ValueError(
            f"{relative_path} is missing required parser metadata: {', '.join(missing)}."
        )
    source_raw_table = (
        document.get("SourceRawTable")
        if kind == "ingest-time"
        else None
    )
    target_asim_table = (
        document.get("TargetASIMTable")
        if kind == "ingest-time"
        else None
    )
    event_vendor: str | None = None
    event_product: str | None = None
    fixture_path: str | None = None
    fixture_errors: list[str] = []
    if kind == "ingest-time":
        if not isinstance(source_raw_table, str) or not source_raw_table:
            fixture_errors.append(
                f"{relative_path} is missing SourceRawTable."
            )
        else:
            try:
                (
                    event_vendor,
                    event_product,
                    fixture_path,
                ) = resolve_source_specific_fixture(
                    parser_query,
                    schema,
                    source_raw_table,
                )
            except ValueError as exc:
                fixture_errors.append(str(exc))
            else:
                if not (repo_root / fixture_path).is_file():
                    fixture_errors.append(
                        "Missing source-table-specific fixture: "
                        f"{fixture_path}."
                    )
    return ParserRecord(
        path=relative_path,
        kind=kind,
        document=document,
        parser_name=parser_name,
        schema=schema,
        schema_version=schema_version,
        product=product,
        parser_query=parser_query,
        source_raw_table=source_raw_table,
        target_asim_table=target_asim_table,
        event_vendor=event_vendor,
        event_product=event_product,
        fixture_path=fixture_path,
        fixture_errors=tuple(fixture_errors),
    )


def _iter_parser_paths(repo_root: Path, kind: str) -> Iterable[str]:
    if kind == "query-time":
        pattern = "Parsers/ASim*/Parsers/ASim*.yaml"
    else:
        pattern = "Parsers/ASim*/IngestTimeParsers/*.yaml"
    for path in sorted(repo_root.glob(pattern)):
        relative_path = _repo_relative_path(repo_root, path)
        if classify_parser_path(relative_path) == kind:
            yield relative_path


def resolve_query_time_pair(
    ingest_record: ParserRecord, query_records: Sequence[ParserRecord]
) -> PairResolution:
    eligible = [
        record
        for record in query_records
        if record.schema == ingest_record.schema
        and isinstance(ingest_record.source_raw_table, str)
        and _identity_key(record.product)
        == _identity_key(ingest_record.product)
        and _query_uses_source_table(
            record.parser_query, ingest_record.source_raw_table
        )
    ]

    ingestion_identities = {
        _identity_key(ingest_record.parser_name),
        _identity_key(PurePosixPath(ingest_record.path).stem),
    }
    identity_matches = [
        record
        for record in eligible
        if ingestion_identities
        & {
            _identity_key(record.parser_name),
            _identity_key(
                str(record.document.get("EquivalentBuiltInParser", ""))
            ),
            _identity_key(PurePosixPath(record.path).stem),
        }
    ]
    if identity_matches:
        candidates = identity_matches
        tier = "identity"
    else:
        candidates = eligible
        tier = "product"

    candidate_evidence = [
        {
            "path": record.path,
            "identityMatch": record in identity_matches,
            "productMatch": _identity_key(record.product)
            == _identity_key(ingest_record.product),
            "sourceTableMatch": True,
            "schemaMatch": True,
            "nameTokenOverlap": _token_overlap(
                ingest_record.parser_name, record.parser_name
            ),
        }
        for record in candidates
    ]
    evidence = {
        "tier": tier,
        "schema": ingest_record.schema,
        "sourceRawTable": ingest_record.source_raw_table,
        "candidates": candidate_evidence,
    }
    if len(candidates) == 1:
        return PairResolution(
            "paired", candidates[0], tuple(candidates), evidence
        )
    if len(candidates) > 1:
        return PairResolution("ambiguous", None, tuple(candidates), evidence)
    return PairResolution("unpaired", None, tuple(), evidence)


def _make_target_id(record: ParserRecord) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", record.parser_name.lower()).strip("-")
    return slug or hashlib.sha256(record.path.encode("utf-8")).hexdigest()[:12]


def _target_from_ingest(
    ingest_record: ParserRecord,
    resolution: PairResolution,
    trigger_path: str,
) -> dict[str, Any]:
    query_record = resolution.selected
    fixture_status = "resolved"
    if ingest_record.fixture_path is None:
        fixture_status = "invalid"
    elif ingest_record.fixture_errors:
        fixture_status = "missing"
    return {
        "targetId": _make_target_id(ingest_record),
        "triggerPaths": [trigger_path],
        "validationKind": "paired" if query_record else "ingest-only",
        "pairStatus": resolution.status,
        "queryTimeParserPath": query_record.path if query_record else None,
        "ingestTimeParserPath": ingest_record.path,
        "schema": ingest_record.schema,
        "schemaVersion": ingest_record.schema_version,
        "product": ingest_record.product,
        "sourceRawTable": ingest_record.source_raw_table,
        "targetASIMTable": ingest_record.target_asim_table,
        "eventVendor": ingest_record.event_vendor,
        "eventProduct": ingest_record.event_product,
        "fixturePath": ingest_record.fixture_path,
        "fixtureStatus": fixture_status,
        "pairCandidates": [record.path for record in resolution.candidates],
        "pairEvidence": resolution.evidence,
        "discoveryErrors": list(ingest_record.fixture_errors),
    }


def get_changed_files(repo_root: Path, base_ref: str) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "diff",
            "--name-only",
            "--diff-filter=AMRD",
            base_ref,
            "--",
            "Parsers",
            "Sample Data/ASIM",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        normalize_changed_path(line)
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def build_validation_manifest(
    repo_root: Path, changed_files: Sequence[str]
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    normalized_changes = sorted(
        {
            normalize_changed_path(path)
            for path in changed_files
            if classify_changed_path(path)
        }
    )
    index_errors: list[dict[str, str]] = []

    def load_index(kind: str) -> list[ParserRecord]:
        records: list[ParserRecord] = []
        for path in _iter_parser_paths(repo_root, kind):
            try:
                records.append(build_parser_record(repo_root, path))
            except (OSError, ValueError, yaml.YAMLError) as exc:
                index_errors.append({"path": path, "message": str(exc)})
        return records

    query_records = load_index("query-time")
    ingest_records = load_index("ingest-time")
    ingest_by_path = {record.path: record for record in ingest_records}
    resolutions = {
        record.path: resolve_query_time_pair(record, query_records)
        for record in ingest_records
    }
    query_to_ingest: dict[str, list[ParserRecord]] = {}
    fixture_to_ingest: dict[str, list[ParserRecord]] = {}
    for record in ingest_records:
        resolution = resolutions[record.path]
        if resolution.selected is not None:
            query_to_ingest.setdefault(
                resolution.selected.path, []
            ).append(record)
        if record.fixture_path is not None:
            fixture_to_ingest.setdefault(
                record.fixture_path, []
            ).append(record)

    targets: dict[str, dict[str, Any]] = {}

    def add_target(record: ParserRecord, trigger_path: str) -> None:
        target = targets.setdefault(
            record.path,
            _target_from_ingest(
                record,
                resolutions[record.path],
                trigger_path,
            ),
        )
        if trigger_path not in target["triggerPaths"]:
            target["triggerPaths"].append(trigger_path)

    for changed_path in normalized_changes:
        kind = classify_changed_path(changed_path)
        if kind == "ingest-time":
            record = ingest_by_path.get(changed_path)
            if record is None:
                discovery_errors = [
                    error["message"]
                    for error in index_errors
                    if error["path"] == changed_path
                ]
                if not discovery_errors:
                    discovery_errors.append(
                        "Changed ingestion-time parser does not exist "
                        f"in the current revision: {changed_path}."
                    )
                targets[f"invalid:{changed_path}"] = {
                    "targetId": re.sub(
                        r"[^a-z0-9]+",
                        "-",
                        PurePosixPath(changed_path).stem.lower(),
                    ).strip("-"),
                    "triggerPaths": [changed_path],
                    "validationKind": "ingest-only",
                    "pairStatus": "invalid",
                    "queryTimeParserPath": None,
                    "ingestTimeParserPath": changed_path,
                    "schema": None,
                    "schemaVersion": None,
                    "product": None,
                    "sourceRawTable": None,
                    "targetASIMTable": None,
                    "eventVendor": None,
                    "eventProduct": None,
                    "fixturePath": None,
                    "fixtureStatus": "invalid",
                    "pairCandidates": [],
                    "pairEvidence": {},
                    "discoveryErrors": discovery_errors,
                }
                continue
            add_target(record, changed_path)
            continue

        if kind == "query-time":
            for record in query_to_ingest.get(changed_path, []):
                add_target(record, changed_path)
            continue
        if kind == "fixture":
            for record in fixture_to_ingest.get(changed_path, []):
                add_target(record, changed_path)

    ordered_targets = sorted(
        targets.values(),
        key=lambda target: (
            str(target["schema"] or ""),
            str(target["targetId"]),
        ),
    )
    for target in ordered_targets:
        target["triggerPaths"] = sorted(set(target["triggerPaths"]))
    target_id_counts: dict[str, int] = {}
    for target in ordered_targets:
        target_id_counts[target["targetId"]] = (
            target_id_counts.get(target["targetId"], 0) + 1
        )
    for target in ordered_targets:
        if target_id_counts[target["targetId"]] <= 1:
            continue
        identity_path = (
            target["ingestTimeParserPath"]
            or target["queryTimeParserPath"]
            or target["triggerPaths"][0]
        )
        suffix = hashlib.sha256(identity_path.encode("utf-8")).hexdigest()[:8]
        target["targetId"] = f"{target['targetId']}-{suffix}"

    return {
        "version": MANIFEST_VERSION,
        "base": str(repo_root),
        "changedPaths": normalized_changes,
        "changedParserPaths": [
            path
            for path in normalized_changes
            if classify_parser_path(path) is not None
        ],
        "targets": ordered_targets,
        "indexErrors": index_errors,
    }


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
    if len(filter_stages) == 1:
        return
    if not any(_pipeline_operator(stage) == "where" for stage in filter_stages[1:]):
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


def _validate_connector_metadata(
    repo_root: Path | None,
    dcr_type: str | None,
    input_stream: str | None,
    source_raw_table: str | None,
    findings: list[Finding],
) -> list[str]:
    if (
        repo_root is None
        or dcr_type is None
        or input_stream is None
        or source_raw_table is None
    ):
        return []

    repo_root_text = str(repo_root.resolve())
    evidence_paths = list(
        find_dcr_output_stream_evidence(repo_root_text, input_stream)
    )
    expected_streams = {
        f"Custom-{source_raw_table}",
        f"Microsoft-{source_raw_table}",
    }
    if dcr_type == "Standard":
        if input_stream not in expected_streams:
            findings.append(
                Finding(
                    "SOURCE001",
                    "InputStream",
                    f"InputStream must be the DCR output stream that writes "
                    f"{source_raw_table}: one of {sorted(expected_streams)}.",
                )
            )
        if not evidence_paths:
            findings.append(
                Finding(
                    "SOURCE002",
                    "InputStream",
                    "No connector DCR outputStream matching InputStream was "
                    "found under Solutions/**/Data Connectors or DataConnectors.",
                )
            )
    elif dcr_type == "Workspace":
        if input_stream.casefold() != "none":
            findings.append(
                Finding(
                    "SOURCE003",
                    "InputStream",
                    "Workspace parsers must use InputStream: none.",
                )
            )
        contradictory_paths = sorted(
            {
                path
                for expected_stream in expected_streams
                for path in find_dcr_output_stream_evidence(
                    repo_root_text, expected_stream
                )
            }
        )
        if contradictory_paths:
            findings.append(
                Finding(
                    "SOURCE004",
                    "DCRType",
                    "Connector DCR evidence writes SourceRawTable, so DCRType "
                    f"cannot be Workspace. Evidence: {', '.join(contradictory_paths)}",
                )
            )
            evidence_paths.extend(contradictory_paths)
    return sorted(set(evidence_paths))


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
    connector_evidence: list[str] = []
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
        input_stream = _require_string(
            document, findings, "InputStream", "InputStream"
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
            and input_stream is not None
            and input_stream.casefold() == "none"
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
        connector_evidence = _validate_connector_metadata(
            effective_repo_root,
            dcr_type,
            input_stream,
            source_raw_table,
            findings,
        )

        if filter_query is not None:
            _validate_pipeline_operators(
                filter_query,
                "ParserFilterQuery",
                ALLOWED_FILTER_OPERATORS,
                findings,
            )
            findings.extend(_scan_kql(filter_query, "ParserFilterQuery"))
        if parser_query is not None:
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
        "connectorEvidence": connector_evidence,
        "findings": finding_dicts,
    }


def _write_json(payload: dict[str, Any], output: Path | None) -> None:
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(serialized)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialized, encoding="utf-8")
    print(f"Wrote {output}")


def _resolve_repo_path(repo_root: Path, value: str) -> Path:
    normalized = normalize_changed_path(value)
    resolved = (repo_root / normalized).resolve()
    resolved.relative_to(repo_root.resolve())
    return resolved


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover = subparsers.add_parser(
        "discover",
        help="Build the changed-input ITP validation target manifest.",
    )
    discover.add_argument("--repo-root", default=".")
    discover.add_argument("--base-ref", default="upstream/master")
    discover.add_argument(
        "--changed-file",
        action="append",
        default=[],
        help="Use an explicit changed path instead of git diff. Repeat as needed.",
    )
    discover.add_argument("--output", type=Path)

    validate = subparsers.add_parser(
        "validate", help="Validate one ingestion-time parser YAML."
    )
    validate.add_argument("path")
    validate.add_argument("--repo-root", default=".")
    validate.add_argument("--query-time-path")
    validate.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        if args.command == "discover":
            changed_files = (
                args.changed_file
                if args.changed_file
                else get_changed_files(repo_root, args.base_ref)
            )
            manifest = build_validation_manifest(repo_root, changed_files)
            _write_json(manifest, args.output)
            return 0

        parser_path = _resolve_repo_path(repo_root, args.path)
        query_time_path = (
            _resolve_repo_path(repo_root, args.query_time_path)
            if args.query_time_path
            else None
        )
        result = validate_ingest_time_parser(
            parser_path,
            query_time_path=query_time_path,
            repo_root=repo_root,
        )
        _write_json(result, args.output)
        return 0 if result["valid"] else 1
    except (
        DuplicateKeyError,
        OSError,
        subprocess.CalledProcessError,
        ValueError,
        yaml.YAMLError,
    ) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
