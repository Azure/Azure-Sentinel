"""Offline static KQL syntax and known-schema validator for XDR artifacts.

Validates KQL queries in XDR Detections (`Solutions/<Solution>/XDR Detections/*.yaml`)
and XDR Workbooks (`Solutions/<Solution>/XDR Workbooks/*.json`) without requiring live
Azure or Defender XDR connectivity.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Iterable

import yaml

from solution_manager.authoring.dependencies import (
    PLATFORM_REFERENCE_INPUTS,
    TABLE_WORKLOADS,
    extract_builtin_asim_parsers,
)
from solution_manager.migration import catalog
from solution_manager.migration._workbook_core import mapping_catalog, workbook

KNOWN_TABULAR_OPERATORS = frozenset(
    {
        "as",
        "consume",
        "count",
        "datatable",
        "distinct",
        "evaluate",
        "extend",
        "externaldata",
        "facet",
        "find",
        "flapping",
        "fork",
        "getschema",
        "graph-mark-components",
        "graph-match",
        "graph-shortest-paths",
        "graph-to-table",
        "invoke",
        "join",
        "limit",
        "lookup",
        "make-graph",
        "make-series",
        "mv-apply",
        "mv-expand",
        "mvapply",
        "mvexpand",
        "order",
        "parse",
        "parse-kv",
        "parse-where",
        "partition",
        "print",
        "project",
        "project-away",
        "project-keep",
        "project-rename",
        "project-reorder",
        " project-smart",
        "project-smart",
        "range",
        "reduce",
        "render",
        "sample",
        "sample-distinct",
        "scan",
        "search",
        "serialize",
        "sort",
        "summarize",
        "take",
        "top",
        "top-hitters",
        "top-nested",
        "union",
        "where",
    }
)

KNOWN_STATEMENT_KEYWORDS = frozenset(
    {
        "alias",
        "declare",
        "let",
        "pattern",
        "restrict",
        "set",
    }
)

TABULAR_GENERATOR_KEYWORDS = frozenset(
    {
        "datatable",
        "external_data",
        "externaldata",
        "find",
        "print",
        "range",
        "search",
        "union",
    }
)

CROSS_WORKSPACE_CALL_RE = re.compile(r"(?<![A-Za-z0-9_.])workspace\s*\(", re.IGNORECASE)
WORKBOOK_TOKEN_RE = re.compile(r"\{[A-Za-z_][\w .:-]*\}")


def _known_tables_catalog() -> set[str]:
    known: set[str] = set(catalog.NATIVE_XDR_TABLES)
    known.update(catalog.PASSTHROUGH_TABLES.keys())
    known.update(TABLE_WORKLOADS.keys())
    known.update(PLATFORM_REFERENCE_INPUTS)
    try:
        mc = mapping_catalog.load_mapping_catalog()
        for table_name, info in (mc.get("tables") or {}).items():
            known.add(str(table_name))
            if isinstance(info, dict):
                target = info.get("targetTable") or info.get("ahTable")
                if isinstance(target, str) and target.strip():
                    known.add(target.strip())
    except Exception:
        # Mapping catalog is optional during static table discovery; proceed with built-in catalog.
        pass
    known.update(
        {
            "AADNonInteractiveUserSignInLogs",
            "AADManagedIdentitySignInLogs",
            "AADProvisioningLogs",
            "AADRiskyServicePrincipals",
            "AADRiskyUsers",
            "AADServicePrincipalRiskEvents",
            "AADServicePrincipalSignInLogs",
            "AADSignInEventsBeta",
            "AADSpnSignInEventsBeta",
            "AADUserRiskEvents",
            "AuditLogs",
            "AzureActivity",
            "AzureDiagnostics",
            "BehaviorEntities",
            "BehaviorInfo",
            "CampaignInfo",
            "CloudAppEvents",
            "CommonSecurityLog",
            "ConfigurationAssessment",
            "CustomDetectionEvents",
            "DeviceBaselineComplianceAssessment",
            "DeviceCustomScriptEvents",
            "DeviceEvents",
            "DeviceFileCertificateInfo",
            "DeviceFileEvents",
            "DeviceImageLoadEvents",
            "DeviceInfo",
            "DeviceLogonEvents",
            "DeviceNetworkEvents",
            "DeviceNetworkInfo",
            "DeviceProcessEvents",
            "DeviceRegistryEvents",
            "DeviceTvmBrowserExtensions",
            "DeviceTvmCertificateInfo",
            "DeviceTvmHardwareFirmware",
            "DeviceTvmInfoGathering",
            "DeviceTvmInfoGatheringKB",
            "DeviceTvmSecureConfigurationAssessment",
            "DeviceTvmSecureConfigurationAssessmentKB",
            "DeviceTvmSoftwareEvidenceBeta",
            "DeviceTvmSoftwareInventory",
            "DeviceTvmSoftwareVulnerabilities",
            "DeviceTvmSoftwareVulnerabilitiesKB",
            "DnsEvents",
            "DnsInventory",
            "EmailAttachmentInfo",
            "EmailEvents",
            "EmailPostDeliveryEvents",
            "EmailUrlInfo",
            "Event",
            "ExposureGraphEdges",
            "ExposureGraphNodes",
            "FileMaliciousContentInfo",
            "Heartbeat",
            "HuntingBookmark",
            "IdentityDirectoryEvents",
            "IdentityInfo",
            "IdentityLogonEvents",
            "IdentityQueryEvents",
            "LAQueryLogs",
            "MdiSensorEvents",
            "MessageEvents",
            "MessagePostDeliveryEvents",
            "MessageUrlInfo",
            "MicrosoftGraphActivityLogs",
            "NetworkAccessTraffic",
            "OAuthAppInfo",
            "OfficeActivity",
            "Operation",
            "PowerBIActivity",
            "PowerPlatformAdminActivity",
            "ProtectionStatus",
            "SecurityAlert",
            "SecurityBaseline",
            "SecurityBaselineSummary",
            "SecurityDetection",
            "SecurityEvent",
            "SecurityIncident",
            "SecurityIoTRawEvent",
            "SecurityNestedRecommendation",
            "SecurityRecommendation",
            "SentinelHealth",
            "SigninLogs",
            "StorageBlobLogs",
            "StorageFileLogs",
            "Syslog",
            "ThreatIntelIndicators",
            "ThreatIntelligenceIndicator",
            "Update",
            "UpdateSummary",
            "UrlClickEvents",
            "Usage",
            "UserAccessAnalytics",
            "UserPeerAnalytics",
            "VMConnection",
            "W3CIISLog",
            "Watchlist",
            "WindowsEvent",
            "WindowsFirewall",
        }
    )
    return known


def _scan_lexical_structure(query: str) -> tuple[str, list[str]]:
    """Mask comments and string literals with spaces while checking balanced quotes/delimiters."""
    errors: list[str] = []
    chars = list(query)
    n = len(query)
    i = 0
    stack: list[tuple[str, int]] = []
    matching = {"(": ")", "[": "]", "{": "}"}
    closing = {")": "(", "]": "[", "}": "{"}

    while i < n:
        c = query[i]
        # Single-line comment //
        if c == "/" and i + 1 < n and query[i + 1] == "/":
            j = query.find("\n", i + 2)
            if j == -1:
                j = n
            for k in range(i, j):
                if chars[k] not in ("\r", "\n"):
                    chars[k] = " "
            i = j
            continue

        # Multi-line comment /* ... */
        if c == "/" and i + 1 < n and query[i + 1] == "*":
            j = query.find("*/", i + 2)
            if j == -1:
                errors.append(f"Unclosed block comment '/*' starting at offset {i}")
                for k in range(i, n):
                    if chars[k] not in ("\r", "\n"):
                        chars[k] = " "
                break
            for k in range(i, j + 2):
                if chars[k] not in ("\r", "\n"):
                    chars[k] = " "
            i = j + 2
            continue

        # Verbatim string @"..." or @'...'
        if c == "@" and i + 1 < n and query[i + 1] in ('"', "'"):
            quote = query[i + 1]
            start = i
            chars[i] = "_"
            chars[i + 1] = "_"
            i += 2
            closed = False
            while i < n:
                if query[i] == quote:
                    if i + 1 < n and query[i + 1] == quote:
                        chars[i] = "_"
                        chars[i + 1] = "_"
                        i += 2
                        continue
                    chars[i] = "_"
                    i += 1
                    closed = True
                    break
                if chars[i] not in ("\r", "\n"):
                    chars[i] = "_"
                i += 1
            if not closed:
                errors.append(f"Unclosed verbatim string literal @{quote} starting at offset {start}")
            continue

        # Triple-backtick or ```multi-line string``` in KQL
        if c == "`" and i + 2 < n and query[i : i + 3] == "```":
            start = i
            j = query.find("```", i + 3)
            if j == -1:
                errors.append(f"Unclosed multi-line string literal '```' starting at offset {start}")
                for k in range(i, n):
                    if chars[k] not in ("\r", "\n"):
                        chars[k] = "_"
                break
            for k in range(i, j + 3):
                if chars[k] not in ("\r", "\n"):
                    chars[k] = "_"
            i = j + 3
            continue

        # Standard string literal "..." or '...'
        if c in ('"', "'"):
            quote = c
            start = i
            chars[i] = "_"
            i += 1
            closed = False
            while i < n:
                ch = query[i]
                if ch == "\\":
                    chars[i] = "_"
                    if i + 1 < n and chars[i + 1] not in ("\r", "\n"):
                        chars[i + 1] = "_"
                    i += 2
                    continue
                if ch in ("\r", "\n"):
                    break
                chars[i] = "_"
                if ch == quote:
                    i += 1
                    closed = True
                    break
                i += 1
            if not closed:
                errors.append(f"Unclosed string literal {quote} starting at offset {start}")
            continue

        # Delimiters (), [], {}
        if c in matching:
            stack.append((c, i))
        elif c in closing:
            expected_open = closing[c]
            if not stack:
                errors.append(f"Unexpected closing delimiter '{c}' at offset {i}")
            else:
                actual_open, open_pos = stack.pop()
                if actual_open != expected_open:
                    errors.append(
                        f"Mismatched delimiter '{c}' at offset {i} (expected '{matching[actual_open]}' for '{actual_open}' at offset {open_pos})"
                    )
        i += 1

    for open_char, open_pos in stack:
        errors.append(f"Unclosed delimiter '{open_char}' starting at offset {open_pos}")

    return "".join(chars), errors


def _split_top_level(text: str, separator: str) -> list[str]:
    """Split `text` by single-character `separator` at top-level delimiter depth 0."""
    parts: list[str] = []
    depth = 0
    start = 0
    for idx, ch in enumerate(text):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth > 0:
                depth -= 1
        elif ch == separator and depth == 0:
            parts.append(text[start:idx])
            start = idx + 1
    parts.append(text[start:])
    return parts


def validate_kql_query_static(
    query_text: str,
    *,
    surface: str = "advancedHunting",
    known_functions: Iterable[str] = (),
    known_tables: Iterable[str] = (),
    allow_workbook_parameters: bool = False,
) -> dict[str, Any]:
    """Validate a single KQL query offline for syntax, pipeline operators, and known tables."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(query_text, str) or not query_text.strip():
        return {
            "valid": False,
            "errors": ["Query text must be a non-empty string"],
            "warnings": [],
            "referencedTables": [],
            "operators": [],
        }

    work_query = query_text
    if allow_workbook_parameters:
        work_query = WORKBOOK_TOKEN_RE.sub("_wb_param_", work_query)

    masked, lex_errors = _scan_lexical_structure(work_query)
    errors.extend(lex_errors)

    if not masked.strip():
        errors.append("Query contains only comments or whitespace and no executable KQL statement")
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "referencedTables": [],
            "operators": [],
        }

    if surface == "advancedHunting" and CROSS_WORKSPACE_CALL_RE.search(masked):
        errors.append("Advanced Hunting query must not contain cross-workspace 'workspace(...)' calls")

    known_table_map = {t.casefold(): t for t in (_known_tables_catalog() | set(known_tables))}
    approved_fn_set = {fn.strip().casefold() for fn in known_functions if isinstance(fn, str) and fn.strip()}
    builtin_asim = {fn.casefold() for fn in extract_builtin_asim_parsers(query_text)}

    statements = _split_top_level(masked, ";")
    let_bindings: set[str] = set()
    operators_seen: list[str] = []
    referenced_tables: set[str] = set()
    has_tabular_expression = False

    for stmt_idx, raw_stmt in enumerate(statements):
        stmt = raw_stmt.strip()
        if not stmt:
            continue

        first_word_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)", stmt)
        first_word = first_word_match.group(1).casefold() if first_word_match else ""

        if first_word in KNOWN_STATEMENT_KEYWORDS:
            if first_word == "let":
                _validate_let_statement(
                    stmt,
                    stmt_idx=stmt_idx,
                    known_table_map=known_table_map,
                    let_bindings=let_bindings,
                    approved_fn_set=approved_fn_set | builtin_asim,
                    operators_seen=operators_seen,
                    referenced_tables=referenced_tables,
                    errors=errors,
                )
            continue

        has_tabular_expression = True
        _validate_pipeline_stages(
            stmt,
            stmt_label=f"statement #{stmt_idx + 1}",
            known_table_map=known_table_map,
            let_bindings=let_bindings,
            approved_fn_set=approved_fn_set | builtin_asim,
            operators_seen=operators_seen,
            referenced_tables=referenced_tables,
            errors=errors,
        )

    if not has_tabular_expression:
        errors.append("Query must contain at least one tabular expression statement")

    # Also collect any known tables referenced inside subqueries/joins/unions
    for tbl in catalog.referenced_catalog_tables(query_text) | catalog.referenced_custom_tables(query_text):
        referenced_tables.add(tbl)
    for ref in catalog.query_table_references(query_text, known_tables=known_table_map.values()):
        tbl = ref.get("table")
        if isinstance(tbl, str) and (tbl.casefold() in known_table_map or tbl.endswith("_CL")):
            referenced_tables.add(known_table_map.get(tbl.casefold(), tbl))

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "referencedTables": sorted(referenced_tables),
        "operators": operators_seen,
    }


_NON_FUNCTION_KEYWORDS_BEFORE_PARENS = frozenset(
    {
        "and",
        "or",
        "not",
        "in",
        "!in",
        "in~",
        "!in~",
        "has",
        "!has",
        "has_any",
        "has_all",
        "contains",
        "!contains",
        "startswith",
        "!startswith",
        "endswith",
        "!endswith",
        "matches",
        "regex",
        "between",
        "by",
        "on",
        "where",
        "extend",
        "project",
        "summarize",
        "join",
        "lookup",
        "union",
        "top",
        "take",
        "limit",
        "sort",
        "order",
        "parse",
        "mv-expand",
        "mvexpand",
    }
)


def _has_empty_parenthesized_expression(rest: str) -> bool:
    for m in re.finditer(r"\(\s*\)", rest):
        prefix = rest[: m.start()].rstrip()
        if not prefix:
            return True
        ident_match = re.search(r"([A-Za-z_!][A-Za-z0-9_-]*)$", prefix)
        if not ident_match:
            return True
        if ident_match.group(1).casefold() in _NON_FUNCTION_KEYWORDS_BEFORE_PARENS:
            return True
    return False


def _extract_top_level_parenthesized_groups(text: str) -> list[str]:
    groups: list[str] = []
    depth = 0
    start_idx = -1
    for idx, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start_idx = idx + 1
            depth += 1
        elif ch == ")":
            if depth > 0:
                depth -= 1
                if depth == 0 and start_idx >= 0:
                    inner = text[start_idx:idx].strip()
                    if inner:
                        groups.append(inner)
                        if len(_split_top_level(inner, "|")) <= 1:
                            groups.extend(_extract_top_level_parenthesized_groups(inner))
                    start_idx = -1
    return groups


def _extract_join_or_lookup_rhs_source(rest: str) -> str | None:
    rem = rest.strip()
    while True:
        param_match = re.match(
            r"^(?:kind|withsource|isfuzzy|hint\.[A-Za-z0-9_]+)\s*=\s*[^\s(]+\s*",
            rem,
            re.IGNORECASE,
        )
        if not param_match:
            break
        rem = rem[param_match.end() :].strip()
    if not rem:
        return None
    if rem.startswith("("):
        depth = 0
        for idx, ch in enumerate(rem):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return rem[1:idx].strip()
        return None
    ident_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)(?:\s*\([^)]*\))?", rem)
    if ident_match:
        return ident_match.group(0).strip()
    return None


def _validate_let_statement(
    stmt: str,
    *,
    stmt_idx: int,
    known_table_map: dict[str, str],
    let_bindings: set[str],
    approved_fn_set: set[str],
    operators_seen: list[str],
    referenced_tables: set[str],
    errors: list[str],
    stmt_label_prefix: str = "",
) -> None:
    let_match = re.match(r"^let\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([\s\S]+)$", stmt, re.IGNORECASE)
    if not let_match:
        label = f"{stmt_label_prefix}statement #{stmt_idx + 1}" if stmt_label_prefix else f"statement #{stmt_idx + 1}"
        errors.append(f"Malformed 'let' statement in {label}")
        return
    let_name = let_match.group(1)
    let_bindings.add(let_name.casefold())
    rhs = let_match.group(2).strip()
    let_label = f"{stmt_label_prefix}let {let_name}".strip()

    view_match = re.match(r"^(?:view\s*)?\(([^)]*)\)\s*\{([\s\S]*)\}\s*$", rhs, re.IGNORECASE)
    if view_match:
        params_raw = view_match.group(1).strip()
        body_raw = view_match.group(2).strip()
        scoped_bindings = set(let_bindings)
        if params_raw:
            for param_part in _split_top_level(params_raw, ","):
                p_match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", param_part)
                if p_match:
                    scoped_bindings.add(p_match.group(1).casefold())
        inner_stmts = [s.strip() for s in _split_top_level(body_raw, ";") if s.strip()]
        if len(inner_stmts) > 1:
            for inner_idx, inner_stmt in enumerate(inner_stmts):
                inner_first_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)", inner_stmt)
                inner_first = inner_first_match.group(1).casefold() if inner_first_match else ""
                if inner_first in KNOWN_STATEMENT_KEYWORDS:
                    if inner_first == "let":
                        _validate_let_statement(
                            inner_stmt,
                            stmt_idx=inner_idx,
                            known_table_map=known_table_map,
                            let_bindings=scoped_bindings,
                            approved_fn_set=approved_fn_set,
                            operators_seen=operators_seen,
                            referenced_tables=referenced_tables,
                            errors=errors,
                            stmt_label_prefix=f"{let_label} ",
                        )
                    continue
                unwrapped_inner = inner_stmt
                while unwrapped_inner.startswith("(") and unwrapped_inner.endswith(")"):
                    cand_inner = unwrapped_inner[1:-1].strip()
                    _, inner_errs = _scan_lexical_structure(cand_inner)
                    if inner_errs:
                        break
                    unwrapped_inner = cand_inner
                head_ident_match = re.match(r"^(?:\(\s*)*([A-Za-z_][A-Za-z0-9_-]*)", unwrapped_inner)
                head_ident_low = head_ident_match.group(1).casefold() if head_ident_match else ""
                is_tabular_stmt = (
                    len(_split_top_level(unwrapped_inner, "|")) > 1
                    or head_ident_low in KNOWN_TABULAR_OPERATORS
                    or head_ident_low in TABULAR_GENERATOR_KEYWORDS
                    or inner_idx < len(inner_stmts) - 1
                )
                if is_tabular_stmt:
                    _validate_pipeline_stages(
                        unwrapped_inner,
                        stmt_label=let_label,
                        known_table_map=known_table_map,
                        let_bindings=scoped_bindings,
                        approved_fn_set=approved_fn_set,
                        operators_seen=operators_seen,
                        referenced_tables=referenced_tables,
                        errors=errors,
                    )
                else:
                    for sub_group in _extract_top_level_parenthesized_groups(unwrapped_inner):
                        if len(_split_top_level(sub_group, "|")) > 1:
                            _validate_pipeline_stages(
                                sub_group,
                                stmt_label=f"{let_label} subquery",
                                known_table_map=known_table_map,
                                let_bindings=scoped_bindings,
                                approved_fn_set=approved_fn_set,
                                operators_seen=operators_seen,
                                referenced_tables=referenced_tables,
                                errors=errors,
                            )
                    if head_ident_match:
                        ident = head_ident_match.group(1)
                        if ident.casefold() in known_table_map:
                            referenced_tables.add(known_table_map[ident.casefold()])
                        elif re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*_CL", ident, re.IGNORECASE):
                            referenced_tables.add(ident)
            return
        rhs = body_raw
        let_bindings = scoped_bindings

    unwrapped_rhs = rhs
    while unwrapped_rhs.startswith("(") and unwrapped_rhs.endswith(")"):
        inner_rhs = unwrapped_rhs[1:-1].strip()
        _, inner_errs = _scan_lexical_structure(inner_rhs)
        if inner_errs:
            break
        unwrapped_rhs = inner_rhs
    if len(_split_top_level(unwrapped_rhs, "|")) > 1:
        _validate_pipeline_stages(
            unwrapped_rhs,
            stmt_label=let_label,
            known_table_map=known_table_map,
            let_bindings=let_bindings,
            approved_fn_set=approved_fn_set,
            operators_seen=operators_seen,
            referenced_tables=referenced_tables,
            errors=errors,
        )
    else:
        for sub_group in _extract_top_level_parenthesized_groups(unwrapped_rhs):
            if len(_split_top_level(sub_group, "|")) > 1:
                _validate_pipeline_stages(
                    sub_group,
                    stmt_label=f"{let_label} subquery",
                    known_table_map=known_table_map,
                    let_bindings=let_bindings,
                    approved_fn_set=approved_fn_set,
                    operators_seen=operators_seen,
                    referenced_tables=referenced_tables,
                    errors=errors,
                )
        head_ident_match = re.match(r"^(?:\(\s*)*([A-Za-z_][A-Za-z0-9_]*)", unwrapped_rhs)
        if head_ident_match:
            ident = head_ident_match.group(1)
            if ident.casefold() in known_table_map:
                referenced_tables.add(known_table_map[ident.casefold()])
            elif re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*_CL", ident, re.IGNORECASE):
                referenced_tables.add(ident)


def _validate_pipeline_stages(
    expr: str,
    *,
    stmt_label: str,
    known_table_map: dict[str, str],
    let_bindings: set[str],
    approved_fn_set: set[str],
    operators_seen: list[str],
    referenced_tables: set[str],
    errors: list[str],
    allow_leading_operator: bool = False,
) -> None:
    stages = _split_top_level(expr, "|")
    for stage_idx, raw_stage in enumerate(stages):
        stage = raw_stage.strip()
        if not stage:
            errors.append(f"Empty pipeline stage in {stmt_label} at stage #{stage_idx + 1}")
            continue

        lead_op_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)", stage)
        lead_op_low = lead_op_match.group(1).casefold() if lead_op_match else ""
        is_leading_operator_stage = (
            stage_idx == 0
            and allow_leading_operator
            and bool(lead_op_low)
            and lead_op_low in KNOWN_TABULAR_OPERATORS
            and lead_op_low not in TABULAR_GENERATOR_KEYWORDS
        )

        if stage_idx == 0 and not is_leading_operator_stage:
            _validate_pipeline_source(
                stage,
                stmt_label=stmt_label,
                known_table_map=known_table_map,
                let_bindings=let_bindings,
                approved_fn_set=approved_fn_set,
                referenced_tables=referenced_tables,
                errors=errors,
            )
            for sub_group in _extract_top_level_parenthesized_groups(stage):
                if len(_split_top_level(sub_group, "|")) > 1:
                    _validate_pipeline_stages(
                        sub_group,
                        stmt_label=f"{stmt_label} stage #{stage_idx + 1} subquery",
                        known_table_map=known_table_map,
                        let_bindings=let_bindings,
                        approved_fn_set=approved_fn_set,
                        operators_seen=operators_seen,
                        referenced_tables=referenced_tables,
                        errors=errors,
                    )
        else:
            op_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)", stage)
            if not op_match:
                errors.append(f"Invalid tabular operator syntax '{stage[:32]}' in {stmt_label} at stage #{stage_idx + 1}")
                continue
            op = op_match.group(1).casefold()
            if op not in KNOWN_TABULAR_OPERATORS:
                errors.append(f"Unknown KQL tabular operator '{op_match.group(1)}' in {stmt_label} at stage #{stage_idx + 1}")
            else:
                operators_seen.append(op)
                rest = stage[op_match.end() :].strip()
                if op in {"where", "extend", "project", "summarize", "join", "lookup", "mv-expand", "mvexpand", "parse", "top", "take", "limit", "sort", "order"}:
                    if not rest:
                        errors.append(f"KQL operator '{op_match.group(1)}' is missing required arguments in {stmt_label} at stage #{stage_idx + 1}")
                    else:
                        if _has_empty_parenthesized_expression(rest):
                            errors.append(
                                f"KQL operator '{op_match.group(1)}' contains an empty parenthesized expression in {stmt_label} at stage #{stage_idx + 1}"
                            )
                        trailing_op_pattern = (
                            r"(?:==|!=|=~|!~|<=|>=|<|>|=|\+|\-|/|%|,|\band\b|\bor\b|\bhas\b|\bcontains\b|\bin\b|\bstartswith\b|\bendswith\b|\bmatches\s+regex\b)\s*$"
                            if op == "parse"
                            else r"(?:==|!=|=~|!~|<=|>=|<|>|=|\+|\-|\*|/|%|,|\band\b|\bor\b|\bhas\b|\bcontains\b|\bin\b|\bstartswith\b|\bendswith\b|\bmatches\s+regex\b)\s*$"
                        )
                        if re.search(
                            trailing_op_pattern,
                            rest,
                            re.IGNORECASE,
                        ):
                            errors.append(
                                f"KQL operator '{op_match.group(1)}' has an incomplete trailing expression in {stmt_label} at stage #{stage_idx + 1}"
                            )
                if op in {"join", "lookup"}:
                    rhs_source = _extract_join_or_lookup_rhs_source(rest)
                    if rhs_source:
                        _validate_pipeline_source(
                            rhs_source,
                            stmt_label=f"{stmt_label} stage #{stage_idx + 1} ({op_match.group(1)})",
                            known_table_map=known_table_map,
                            let_bindings=let_bindings,
                            approved_fn_set=approved_fn_set,
                            referenced_tables=referenced_tables,
                            errors=errors,
                        )
                elif op in {"mv-apply", "mvapply", "partition"}:
                    for sub_group in _extract_top_level_parenthesized_groups(rest):
                        sub_lead = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)", sub_group.strip())
                        sub_lead_op = sub_lead.group(1).casefold() if sub_lead else ""
                        if len(_split_top_level(sub_group, "|")) > 1 or (
                            sub_lead_op in KNOWN_TABULAR_OPERATORS and sub_lead_op not in TABULAR_GENERATOR_KEYWORDS
                        ):
                            _validate_pipeline_stages(
                                sub_group,
                                stmt_label=f"{stmt_label} stage #{stage_idx + 1} ({op_match.group(1)}) subquery",
                                known_table_map=known_table_map,
                                let_bindings=let_bindings,
                                approved_fn_set=approved_fn_set,
                                operators_seen=operators_seen,
                                referenced_tables=referenced_tables,
                                errors=errors,
                                allow_leading_operator=True,
                            )
                else:
                    for sub_group in _extract_top_level_parenthesized_groups(rest):
                        if len(_split_top_level(sub_group, "|")) > 1:
                            _validate_pipeline_stages(
                                sub_group,
                                stmt_label=f"{stmt_label} stage #{stage_idx + 1} ({op_match.group(1)}) subquery",
                                known_table_map=known_table_map,
                                let_bindings=let_bindings,
                                approved_fn_set=approved_fn_set,
                                operators_seen=operators_seen,
                                referenced_tables=referenced_tables,
                                errors=errors,
                            )


def _validate_pipeline_source(
    source_stage: str,
    *,
    stmt_label: str,
    known_table_map: dict[str, str],
    let_bindings: set[str],
    approved_fn_set: set[str],
    referenced_tables: set[str],
    errors: list[str],
) -> None:
    unwrapped = source_stage.strip()
    while unwrapped.startswith("(") and unwrapped.endswith(")"):
        inner = unwrapped[1:-1].strip()
        _, inner_errs = _scan_lexical_structure(inner)
        if inner_errs:
            break
        unwrapped = inner

    if "|" in _split_top_level(unwrapped, "|") or len(_split_top_level(unwrapped, "|")) > 1:
        _validate_pipeline_stages(
            unwrapped,
            stmt_label=stmt_label,
            known_table_map=known_table_map,
            let_bindings=let_bindings,
            approved_fn_set=approved_fn_set,
            operators_seen=[],
            referenced_tables=referenced_tables,
            errors=errors,
        )
        return

    head_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)", unwrapped)
    if not head_match:
        if unwrapped.startswith("["):
            return
        errors.append(f"Unrecognized tabular source '{source_stage[:32]}' in {stmt_label}")
        return

    ident = head_match.group(1)
    lowered = ident.casefold()
    after = unwrapped[head_match.end() :].strip()

    sub_groups = _extract_top_level_parenthesized_groups(unwrapped)
    for idx, sub_group in enumerate(sub_groups):
        if idx == 0 and lowered in {"materialize", "toscalar"}:
            if sub_group:
                _validate_pipeline_source(
                    sub_group,
                    stmt_label=f"{stmt_label} ({ident})",
                    known_table_map=known_table_map,
                    let_bindings=let_bindings,
                    approved_fn_set=approved_fn_set,
                    referenced_tables=referenced_tables,
                    errors=errors,
                )
        elif len(_split_top_level(sub_group, "|")) > 1:
            _validate_pipeline_stages(
                sub_group,
                stmt_label=f"{stmt_label} subquery",
                known_table_map=known_table_map,
                let_bindings=let_bindings,
                approved_fn_set=approved_fn_set,
                operators_seen=[],
                referenced_tables=referenced_tables,
                errors=errors,
            )

    if lowered in TABULAR_GENERATOR_KEYWORDS:
        if lowered == "union":
            for op_name, _ in workbook._union_operands(unwrapped):
                op_low = op_name.casefold()
                if op_low in known_table_map:
                    referenced_tables.add(known_table_map[op_low])
                elif re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*_CL", op_name, re.IGNORECASE):
                    referenced_tables.add(op_name)
                elif (
                    op_low not in let_bindings
                    and op_low not in approved_fn_set
                    and not workbook.is_standard_builtin_asim_parser(op_name)
                    and op_low not in {"withsource", "isfuzzy", "kind", "_wb_param_", "print", "range", "datatable", "externaldata", "external_data"}
                ):
                    errors.append(f"Unknown table or function '{op_name}' in union operand of {stmt_label}")
        return

    if lowered in known_table_map:
        referenced_tables.add(known_table_map[lowered])
        return

    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*_CL", ident, re.IGNORECASE):
        referenced_tables.add(ident)
        return

    if lowered in let_bindings or lowered in approved_fn_set or workbook.is_standard_builtin_asim_parser(ident):
        return

    if lowered in {"_getwatchlist", "_getwatchlistalias", "table", "totable", "externaldata", "external_data", "materialize", "toscalar", "_wb_param_"}:
        return

    if after.startswith("("):
        # Function call as tabular source
        if lowered in {fn.casefold() for fn in workbook._BUILTINS}:
            return
        errors.append(f"Unknown tabular function or unapproved workspace function '{ident}(...)' in {stmt_label}")
        return

    errors.append(f"Unknown table or tabular identifier '{ident}' in {stmt_label}")


def _provenance_known_tables(doc: dict[str, Any]) -> set[str]:
    props = doc.get("properties") if isinstance(doc.get("properties"), dict) else {}
    provenance = doc.get("contentProvenance") if isinstance(doc.get("contentProvenance"), dict) else {}
    if not provenance and isinstance(props.get("contentProvenance"), dict):
        provenance = props["contentProvenance"]
    tables: set[str] = set()
    for container in (doc, props, provenance):
        if not isinstance(container, dict):
            continue
        for key in ("requiredWorkloads", "requiredDataConnectors"):
            records = container.get(key)
            if isinstance(records, list):
                for record in records:
                    if isinstance(record, dict) and isinstance(record.get("dataTypes"), list):
                        for dt in record["dataTypes"]:
                            if isinstance(dt, str) and dt.strip():
                                tables.add(dt.strip())
    for query_list in (
        provenance.get("queries"),
        provenance.get("nativeReview", {}).get("queries") if isinstance(provenance.get("nativeReview"), dict) else None,
    ):
        if isinstance(query_list, list):
            for query_entry in query_list:
                if not isinstance(query_entry, dict):
                    continue
                if isinstance(query_entry.get("tables"), list):
                    for dt in query_entry["tables"]:
                        if isinstance(dt, str) and dt.strip():
                            tables.add(dt.strip())
                conv = query_entry.get("conversion")
                if isinstance(conv, dict):
                    for list_key in ("resolvedTables", "targetTables"):
                        vals = conv.get(list_key)
                        if isinstance(vals, list):
                            for dt in vals:
                                if isinstance(dt, str) and dt.strip():
                                    tables.add(dt.strip())
    return tables


def validate_xdr_detection_kql(
    doc: dict[str, Any],
    *,
    known_functions: Iterable[str] = (),
    known_tables: Iterable[str] = (),
) -> dict[str, Any]:
    """Validate the KQL query inside an authored XDR Detection YAML document."""
    if not isinstance(doc, dict):
        return {"valid": False, "errors": ["XDR Detection document must be a mapping"], "referencedTables": []}

    props = doc.get("properties") if isinstance(doc.get("properties"), dict) else {}
    qc = props.get("queryCondition") if isinstance(props.get("queryCondition"), dict) else {}
    query_text = qc.get("queryText")
    if query_text is None:
        query_text = doc.get("query")

    declared_tables: set[str] = set(known_tables) | _provenance_known_tables(doc)
    fn_aliases: set[str] = set(known_functions)

    return validate_kql_query_static(
        query_text if isinstance(query_text, str) else "",
        surface="advancedHunting",
        known_functions=fn_aliases,
        known_tables=declared_tables,
        allow_workbook_parameters=False,
    )


def validate_xdr_workbook_kql(
    doc: dict[str, Any],
    *,
    known_functions: Iterable[str] = (),
    known_tables: Iterable[str] = (),
) -> dict[str, Any]:
    """Validate all Advanced Hunting / Log Analytics KQL query surfaces in an XDR Workbook JSON document."""
    if not isinstance(doc, dict):
        return {"valid": False, "errors": ["XDR Workbook document must be a JSON object"], "queries": []}

    declared_tables: set[str] = set(known_tables) | _provenance_known_tables(doc)
    fn_aliases: set[str] = set(known_functions)

    surfaces = workbook.query_surfaces(doc)
    errors: list[str] = []
    query_reports: list[dict[str, Any]] = []

    for surface_entry in surfaces:
        if workbook.is_preserved_provider_surface(surface_entry):
            continue
        qt = surface_entry.get("queryType", 0)
        if qt not in (0, None, workbook.AH):
            continue
        pointer = surface_entry["path"]
        raw_query_value = surface_entry["node"].get("query")
        surface_kind = "advancedHunting" if qt == workbook.AH else "logAnalytics"
        try:
            unwrapped_query = workbook._raw_query(raw_query_value, qt)
        except ValueError as exc:
            err_msg = f"{pointer}: {exc}"
            errors.append(err_msg)
            query_reports.append({"path": pointer, "valid": False, "errors": [str(exc)]})
            continue

        res = validate_kql_query_static(
            unwrapped_query,
            surface=surface_kind,
            known_functions=fn_aliases,
            known_tables=declared_tables,
            allow_workbook_parameters=True,
        )
        for err in res["errors"]:
            errors.append(f"{pointer}: {err}")
        query_reports.append(
            {
                "path": pointer,
                "surface": surface_kind,
                "valid": res["valid"],
                "errors": res["errors"],
                "referencedTables": res["referencedTables"],
            }
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "queries": query_reports,
    }


def _solution_parser_aliases(solution_root: Path) -> set[str]:
    aliases: set[str] = set()
    parsers_dir = solution_root / "Parsers"
    if not parsers_dir.is_dir():
        return aliases
    for path in sorted(parsers_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml"}:
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(doc, dict):
            for key in ("FunctionAlias", "FunctionName", "Title"):
                val = doc.get(key)
                if isinstance(val, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", val.strip()):
                    aliases.add(val.strip())
    return aliases


def _solution_connector_tables(solution_root: Path) -> set[str]:
    try:
        from solution_manager.authoring.workbook_dependencies import _connectors
        from solution_manager.migration.workbooks import _solution_data
        connectors = _connectors(solution_root, _solution_data(solution_root))
    except Exception:
        return set()
    return {
        dt.strip()
        for c in connectors
        if isinstance(c, dict) and isinstance(c.get("dataTypes"), list)
        for dt in c["dataTypes"]
        if isinstance(dt, str) and dt.strip()
    }


def validate_xdr_artifacts_kql(solution_path: Path | str) -> dict[str, Any]:
    """Perform offline static KQL validation across XDR Detections and XDR Workbooks in a solution."""
    root = Path(solution_path).expanduser().resolve()
    parser_aliases = _solution_parser_aliases(root)
    connector_tables = _solution_connector_tables(root)

    detection_results: list[dict[str, Any]] = []
    workbook_results: list[dict[str, Any]] = []
    all_errors: list[str] = []

    det_dir = root / "XDR Detections"
    if det_dir.is_dir():
        det_files = sorted(
            [
                p
                for p in det_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in {".yaml", ".yml"}
            ],
            key=lambda p: p.as_posix().lower(),
        )
        for det_file in det_files:
            rel = det_file.relative_to(root).as_posix()
            try:
                doc = yaml.safe_load(det_file.read_text(encoding="utf-8"))
            except Exception as exc:
                err = f"Failed to parse YAML: {exc}"
                detection_results.append({"path": rel, "valid": False, "errors": [err], "referencedTables": []})
                all_errors.append(f"{rel}: {err}")
                continue

            res = validate_xdr_detection_kql(doc, known_functions=parser_aliases, known_tables=connector_tables)
            detection_results.append(
                {
                    "path": rel,
                    "valid": res["valid"],
                    "errors": res["errors"],
                    "referencedTables": res.get("referencedTables", []),
                }
            )
            for err in res["errors"]:
                all_errors.append(f"{rel}: {err}")

    wb_dir = root / "XDR Workbooks"
    if wb_dir.is_dir():
        wb_files = sorted(
            [p for p in wb_dir.rglob("*") if p.is_file() and p.suffix.lower() == ".json"],
            key=lambda p: p.as_posix().lower(),
        )
        for wb_file in wb_files:
            rel = wb_file.relative_to(root).as_posix()
            try:
                doc = json.loads(wb_file.read_text(encoding="utf-8"))
            except Exception as exc:
                err = f"Failed to parse JSON: {exc}"
                workbook_results.append({"path": rel, "valid": False, "errors": [err], "queries": []})
                all_errors.append(f"{rel}: {err}")
                continue

            res = validate_xdr_workbook_kql(doc, known_functions=parser_aliases, known_tables=connector_tables)
            workbook_results.append(
                {
                    "path": rel,
                    "valid": res["valid"],
                    "errors": res["errors"],
                    "queries": res.get("queries", []),
                }
            )
            for err in res["errors"]:
                all_errors.append(f"{rel}: {err}")

    return {
        "solution": root.name,
        "valid": len(all_errors) == 0,
        "staticKqlValidated": True,
        "detections": detection_results,
        "workbooks": workbook_results,
        "errors": all_errors,
    }
