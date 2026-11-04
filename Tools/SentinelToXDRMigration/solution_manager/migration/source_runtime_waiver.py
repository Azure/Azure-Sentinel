from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any


SOURCE_PROVIDERS = {
    "triage-mcp": "microsoft-sentinel-triage",
    "azure-monitor-sdk": "log-analytics-workspace",
    "log-analytics-cli": "log-analytics-workspace",
}

# This is deliberately a finite, global source-runtime whitelist.
MISSING_SCHEMA_TABLES = ("IdentityInfo",)
_WHITELIST_CASEFOLDED = frozenset(table.casefold() for table in MISSING_SCHEMA_TABLES)
_SEMANTIC_CODE = re.compile(r"\bSEM\d{4,}\b", re.IGNORECASE)
_TABLE_DIAGNOSTIC = re.compile(
    r"\bfailed\s+to\s+resolve\s+"
    r"(?:table\s+or\s+column\s+expression\s+named|table)\s+"
    r"['\"`]?([A-Za-z_][A-Za-z0-9_]*)['\"`]?",
    re.IGNORECASE,
)
_IDENTITYINFO_MISSING_MESSAGE = re.compile(
    r"^\s*(?:SEM0100\s*:\s*)?"
    r"(?:['\"`][^'\"`]+['\"`]\s+operator\s*:\s*)?"
    r"Failed\s+to\s+resolve\s+"
    r"(?:table\s+or\s+column\s+expression\s+named|table)\s+"
    r"['\"`]?IdentityInfo['\"`]?\s*\.?\s*$",
    re.IGNORECASE,
)
_AUTH_FAILURE = re.compile(
    r"\b(authentication|authorization|unauthorized|forbidden|tenant mismatch)\b",
    re.IGNORECASE,
)
_ALLOWED_ERROR_CODES = frozenset({"badargumenterror", "semanticerror", "sem0100"})
_GENERIC_ERROR_MESSAGES = frozenset({
    "query execution failed.",
    "query failed.",
    "the query failed.",
})


def _collect_diagnostics(value: Any) -> tuple[list[str], list[str], list[str]]:
    messages: list[str] = []
    codes: list[str] = []
    structured_messages: list[str] = []
    visited: set[int] = set()

    def visit(item: Any, key: str | None = None) -> None:
        if isinstance(item, str):
            if key and key.casefold() in {"code", "errorcode", "failurecode"}:
                codes.append(item)
            stripped = item.strip()
            if stripped.startswith(("{", "[")):
                try:
                    decoded = json.loads(stripped)
                except (json.JSONDecodeError, RecursionError):
                    pass
                else:
                    if not isinstance(decoded, str):
                        visit(decoded)
                        return
            if key and key.casefold() in {"message", "description"}:
                structured_messages.append(item)
            messages.append(item)
            return
        if isinstance(item, Mapping):
            identity = id(item)
            if identity in visited:
                return
            visited.add(identity)
            for child_key, child in item.items():
                visit(child, str(child_key))
            return
        if isinstance(item, (list, tuple)):
            identity = id(item)
            if identity in visited:
                return
            visited.add(identity)
            for child in item:
                visit(child)

    visit(value)
    return messages, codes, structured_messages


def missing_schema_whitelist_match(
    entry: Mapping[str, Any],
    *,
    provider: str,
    expected_query_sha256: str | None = None,
) -> dict[str, Any] | None:
    """Classify only a complete, exact Sentinel table-resolution failure.

    This is a derived assessment. It never edits the raw provider result or
    turns a failed source query into a successful execution.
    """
    if provider not in SOURCE_PROVIDERS:
        return None
    if (
        entry.get("status") != "failed"
        or entry.get("statusCode") != 400
        or entry.get("failureKind") != "query"
        or entry.get("partial") is True
        or entry.get("partialError")
        or (
            expected_query_sha256 is not None
            and entry.get("querySha256") != expected_query_sha256
        )
    ):
        return None

    messages, explicit_codes, structured_messages = _collect_diagnostics(
        {"error": entry.get("error"), "errorDetails": entry.get("errorDetails")}
    )
    diagnostic = "\n".join(dict.fromkeys(message for message in messages if message))
    semantic_codes = {code.upper() for code in _SEMANTIC_CODE.findall(diagnostic)}
    normalized_codes = {code.casefold() for code in explicit_codes}
    if semantic_codes != {"SEM0100"}:
        return None
    if any(code not in _ALLOWED_ERROR_CODES for code in normalized_codes):
        return None
    code_text = {code.casefold() for code in explicit_codes}
    if any(
        message.strip().casefold() not in _GENERIC_ERROR_MESSAGES
        and message.strip().casefold() not in code_text
        and not _IDENTITYINFO_MISSING_MESSAGE.fullmatch(message)
        for message in messages
    ):
        return None
    if any(
        not _IDENTITYINFO_MISSING_MESSAGE.fullmatch(message)
        and message.strip().casefold() not in _GENERIC_ERROR_MESSAGES
        and message.strip().casefold() not in code_text
        for message in structured_messages
    ):
        return None
    if _AUTH_FAILURE.search(diagnostic):
        return None

    resolved_tables = {
        table.casefold() for table in _TABLE_DIAGNOSTIC.findall(diagnostic)
    }
    if not resolved_tables or resolved_tables != _WHITELIST_CASEFOLDED:
        return None
    table = next(
        canonical
        for canonical in MISSING_SCHEMA_TABLES
        if canonical.casefold() in resolved_tables
    )
    return {
        "status": "source-waived",
        "table": table,
        "reason": (
            f"Sentinel source query failed with HTTP 400 SEM0100 because "
            f"the source surface could not resolve table {table}."
        ),
        "rawFailure": {
            "status": entry["status"],
            "statusCode": entry["statusCode"],
            "failureKind": entry["failureKind"],
            "querySha256": entry.get("querySha256"),
            "error": entry.get("error"),
            "errorDetails": entry.get("errorDetails"),
        },
        "sourceExecutionPassed": False,
        "runtimeQualified": False,
    }
