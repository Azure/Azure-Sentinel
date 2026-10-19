from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

# Native Defender tables expose Timestamp in Advanced Hunting even when their
# Log Analytics connector copy exposes TimeGenerated.
NATIVE_XDR_TABLES = frozenset(
    {
        "AlertEvidence",
        "AlertInfo",
        "CloudAppEvents",
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
        "DeviceTvmSecureConfigurationAssessment",
        "DeviceTvmSoftwareInventory",
        "DeviceTvmSoftwareVulnerabilities",
        "EmailAttachmentInfo",
        "EmailEvents",
        "EmailPostDeliveryEvents",
        "EmailUrlInfo",
        "IdentityDirectoryEvents",
        "IdentityLogonEvents",
        "IdentityQueryEvents",
        "UrlClickEvents",
    }
)

# These tables were verified to resolve in Advanced Hunting with their Sentinel
# name and time-column conventions. The catalog is intentionally extensible;
# runtime validation remains the final authority.
PASSTHROUGH_TABLES: dict[str, dict[str, Any]] = {
    "AzureActivity": {
        "columnRenames": {},
        "notes": "Sentinel workload table; preserve TimeGenerated and source schema.",
    },
    "IdentityInfo": {
        "columnRenames": {
            "AccountUPN": "AccountUpn",
            "AccountCreationTime": "CreatedDateTime",
            "UserType": "TenantMembershipType",
        },
        "notes": "Identity profile table with verified Sentinel-to-AH field names.",
    },
    "Event": {
        "columnRenames": {},
        "notes": "Sentinel workload table; availability depends on the unified tenant.",
    },
    "SecurityEvent": {
        "columnRenames": {},
        "notes": "Sentinel workload table; preserve TimeGenerated and source schema.",
    },
    "WindowsEvent": {
        "columnRenames": {},
        "notes": "Sentinel workload table; preserve TimeGenerated and source schema.",
    },
}


def referenced_catalog_tables(query: str) -> set[str]:
    import re

    known = NATIVE_XDR_TABLES | PASSTHROUGH_TABLES.keys()
    return {
        table
        for table in known
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(table)}(?![A-Za-z0-9_])", query)
    }


def referenced_custom_tables(query: str) -> set[str]:
    return set(
        re.findall(r"(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9_]*_CL)(?![A-Za-z0-9_])", query)
    )


def query_table_references(
    query: str, *, known_tables: Iterable[str] = (),
) -> list[dict[str, str | None]]:
    """Return conservative table/alias bindings found at KQL table positions.

    This deliberately recognizes only common table sources. It is evidence
    gathering, not a KQL parser; callers must treat unrecognized shapes as
    unresolved rather than guessing an alias or column owner.
    """
    token_pattern = re.compile(
        r"//[^\n]*|/\*[\s\S]*?\*/|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
        r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|[A-Za-z_][A-Za-z0-9_]*|[^\s]"
    )
    tokens = [
        match.group(0)
        for match in token_pattern.finditer(query)
        if not match.group(0).startswith(("//", "/*", "'", '"', "@'", '@"'))
    ]
    known = {
        table.casefold(): table
        for table in NATIVE_XDR_TABLES | PASSTHROUGH_TABLES.keys() | set(known_tables)
    }
    let_bindings = {
        tokens[i + 1].casefold()
        for i in range(len(tokens) - 2)
        if tokens[i].casefold() == "let" and tokens[i + 2] == "="
    }
    results: list[dict[str, str | None]] = []
    seen: set[tuple[str, str | None]] = set()
    for index, token in enumerate(tokens):
        lowered = token.casefold()
        is_custom = re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*_CL", token, re.IGNORECASE)
        is_simple_base = (
            (index == 0 or tokens[index - 1] == ";")
            and lowered != "let"
            and lowered not in let_bindings
            and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token)
            and (index + 1 == len(tokens) or tokens[index + 1].casefold() == "as" or tokens[index + 1] == "|")
        )
        if lowered in known or is_custom or is_simple_base:
            previous = tokens[index - 1].casefold() if index else ""
            at_start = index == 0 or previous in {"=", "(", ",", ";", "join", "union", "lookup", "from"}
            if not at_start:
                continue
            canonical = known.get(lowered, token)
            alias: str | None = None
            following = index + 1
            if following < len(tokens) and tokens[following].casefold() == "as":
                if following + 1 < len(tokens) and re.fullmatch(r"[A-Za-z_]\w*", tokens[following + 1]):
                    alias = tokens[following + 1]
            elif following < len(tokens) and re.fullmatch(r"[A-Za-z_]\w*", tokens[following]):
                if tokens[following].casefold() not in {
                    "where", "join", "union", "lookup", "on", "project", "extend",
                    "summarize", "as", "by", "kind",
                }:
                    alias = tokens[following]
            binding = (canonical.casefold(), alias.casefold() if alias else None)
            if binding not in seen:
                results.append({"table": canonical, "alias": alias})
                seen.add(binding)
    return results


def query_has_ambiguous_table_scope(query: str) -> bool:
    references = query_table_references(query)
    if len(references) != 1:
        return True
    lexical = re.compile(
        r"//[^\n]*|/\*[\s\S]*?\*/|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
        r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|[A-Za-z_][A-Za-z0-9_]*"
    )
    tokens = [
        match.group(0).casefold()
        for match in lexical.finditer(query)
        if not match.group(0).startswith(("//", "/*", "'", '"', "@'", '@"'))
    ]
    if any(
        token in {"join", "union", "lookup"}
        and (index == 0 or tokens[index - 1] == "|")
        for index, token in enumerate(tokens)
    ):
        return True
    table = re.escape(str(references[0]["table"]))
    code = query.strip()
    while code.startswith("//") or code.startswith("/*"):
        if code.startswith("//"):
            newline = code.find("\n")
            code = code[newline + 1:] if newline >= 0 else ""
        else:
            close = code.find("*/", 2)
            code = code[close + 2:] if close >= 0 else ""
        code = code.lstrip()
    return not bool(re.match(
        rf"(?is)^\s*{table}\s+(?:as\s+[A-Za-z_]\w*\s*)?(?:\||$)",
        code,
    ) or re.match(rf"(?is)^\s*{table}\s*(?:\||$)", code))


def configured_column_renames(query: str, config: dict[str, Any]) -> tuple[dict[str, str], bool]:
    """Resolve configured column renames only when the query scope is singular."""
    configured = config.get("columnMappings") or {}
    if not configured:
        return {}, False
    if query_has_ambiguous_table_scope(query):
        return {}, True

    references = query_table_references(query)
    if len(references) != 1:
        return {}, True
    table = references[0]["table"].casefold()
    if all(isinstance(value, str) for value in configured.values()):
        return ({str(key): str(value) for key, value in configured.items()}, False)

    selected: dict[str, str] = {}
    for name, value in configured.items():
        if isinstance(value, dict) and table is not None and str(name).casefold() == table:
            selected.update({str(key): str(target) for key, target in value.items()})
    return selected, False


def query_has_mixed_time_semantics(query: str) -> bool:
    tables = referenced_catalog_tables(query)
    return bool(tables & NATIVE_XDR_TABLES) and bool(
        tables & PASSTHROUGH_TABLES.keys()
    )


def query_column_renames(query: str) -> dict[str, str]:
    renames: dict[str, str] = {}
    tables = referenced_catalog_tables(query)
    if tables & NATIVE_XDR_TABLES and not tables & PASSTHROUGH_TABLES.keys():
        renames["TimeGenerated"] = "Timestamp"
    for table in tables & PASSTHROUGH_TABLES.keys():
        renames.update(PASSTHROUGH_TABLES[table]["columnRenames"])
    return renames
