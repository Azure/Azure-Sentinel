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
            at_start = index == 0 or previous in {"=", "(", ",", ";", "{", "join", "union", "lookup", "from"}
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


def _replace_code_segment(segment: str, pattern: re.Pattern[str], mappings: dict[str, str]) -> str:
    pieces = re.split(r"""('(?:''|[^'])*'|"(?:\\"|[^"])*")""", segment)
    for index in range(0, len(pieces), 2):
        pieces[index] = pattern.sub(lambda match: mappings[match.group(0)], pieces[index])
    return "".join(pieces)


def _token_replace(query: str, mappings: dict[str, str]) -> str:
    if not mappings:
        return query
    pattern = re.compile(
        r"\b(?:" + "|".join(re.escape(source) for source in sorted(mappings, key=len, reverse=True)) + r")\b"
    )
    output = []
    for line in query.splitlines(keepends=True):
        code, separator, comment = line.partition("//")
        output.append(_replace_code_segment(code, pattern, mappings))
        if separator:
            output.append(separator + comment)
    return "".join(output)


def _tokens(query: str) -> list[str]:
    """Tokenize only for conservative local proofs, never to rewrite KQL."""
    tokens = re.findall(
        r"//[^\n]*|/\*[\s\S]*?\*/|```[\s\S]*?```"
        r"|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
        r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\""
        r"|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?[smhd]?|>=|<=|==|!=|[^\s]",
        query,
    )
    return [
        "'" + token[1:-1] + "'" if token.startswith('"') else token
        for token in tokens
        if not token.startswith(("//", "/*"))
    ]


SECURITY_ALERT_DIRECT_COLUMN_MAP: dict[str, str] = {
    "TimeGenerated": "Timestamp",
    "SystemAlertId": "AlertId",
    "AlertName": "Title",
    "DisplayName": "Title",
    "AlertSeverity": "Severity",
    "ProviderName": "DetectionSource",
    "ProductName": "ServiceSource",
    "Tactics": "AttackTechniques",
    "Entities": "AdditionalFields",
}
ALERT_EVIDENCE_CROSS_SURFACE_EXPRESSIONS: dict[str, str] = {
    "ResourceId": 'coalesce(tostring(column_ifexists("ResourceID", "")), tostring(column_ifexists("AzureResourceId", "")))',
    "AzureResourceId": 'coalesce(tostring(column_ifexists("ResourceID", "")), tostring(column_ifexists("AzureResourceId", "")))',
    "ResourceID": 'coalesce(tostring(column_ifexists("ResourceID", "")), tostring(column_ifexists("AzureResourceId", "")))',
    "ResourceType": 'coalesce(tostring(column_ifexists("ResourceType", "")), tostring(column_ifexists("AzureResourceType", "")))',
    "AzureResourceType": 'coalesce(tostring(column_ifexists("ResourceType", "")), tostring(column_ifexists("AzureResourceType", "")))',
    "SubscriptionId": 'coalesce(tostring(column_ifexists("SubscriptionId", "")), tostring(column_ifexists("AzureSubscriptionId", "")))',
    "AzureSubscriptionId": 'coalesce(tostring(column_ifexists("SubscriptionId", "")), tostring(column_ifexists("AzureSubscriptionId", "")))',
}
SECURITY_ALERT_COMPAT_ALIAS_EXPRESSIONS: dict[str, str] = {
    "SystemAlertId": "AlertId",
    "AlertName": "Title",
    "DisplayName": "Title",
    "AlertSeverity": "Severity",
    "ProviderName": "DetectionSource",
    "ProductName": "ServiceSource",
    "Tactics": "AttackTechniques",
    "Description": "Title",
    "Entities": "AdditionalFields",
    "CompromisedEntity": "DeviceName",
    "HostName": "DeviceName",
    "IPAddress": "RemoteIP",
    "UserPrincipalName": "AccountUpn",
    **ALERT_EVIDENCE_CROSS_SURFACE_EXPRESSIONS,
}
SECURITY_INCIDENT_DIRECT_COLUMN_MAP: dict[str, str] = {
    "TimeGenerated": "Timestamp",
    "IncidentName": "Title",
    "IncidentNumber": "AlertId",
    "ProviderName": "DetectionSource",
    "Entities": "AdditionalFields",
}
SECURITY_INCIDENT_COMPAT_ALIAS_EXPRESSIONS: dict[str, str] = {
    "IncidentName": "Title",
    "IncidentNumber": "AlertId",
    "Severity": "Severity",
    "Status": 'column_ifexists("Status", "Active")',
    "ProviderName": "DetectionSource",
    "Description": "Title",
    "AlertIds": "pack_array(AlertId)",
    "Entities": "AdditionalFields",
    "CompromisedEntity": "DeviceName",
    "HostName": "DeviceName",
    "IPAddress": "RemoteIP",
    "UserPrincipalName": "AccountUpn",
    **ALERT_EVIDENCE_CROSS_SURFACE_EXPRESSIONS,
}
ALERT_EVIDENCE_INDICATOR_TOKENS = frozenset({
    "Entities",
    "AlertEvidence",
    "EntityType",
    "EvidenceRole",
    "EvidenceDirection",
    "AdditionalFields",
    "AccountUpn",
    "AccountName",
    "AccountDomain",
    "AccountSid",
    "AccountObjectId",
    "DeviceName",
    "DeviceId",
    "RemoteIP",
    "LocalIP",
    "RemoteUrl",
    "FileName",
    "FolderPath",
    "SHA256",
    "SHA1",
    "RegistryKey",
    "RegistryValueName",
    "RegistryValueData",
    "CloudResource",
    "Application",
    "ApplicationId",
    "OAuthApplicationId",
    "ThreatFamily",
    "CompromisedEntity",
    "HostName",
    "IPAddress",
    "UserPrincipalName",
    *ALERT_EVIDENCE_CROSS_SURFACE_EXPRESSIONS.keys(),
})
MITRE_TACTIC_NAMES = frozenset({
    "InitialAccess",
    "Execution",
    "Persistence",
    "PrivilegeEscalation",
    "DefenseEvasion",
    "CredentialAccess",
    "Discovery",
    "LateralMovement",
    "Collection",
    "Exfiltration",
    "CommandAndControl",
    "Impact",
    "PreAttack",
    "Reconnaissance",
    "ResourceDevelopment",
})


def _split_top_level_kql_stages(query: str) -> list[str]:
    stages: list[str] = []
    current: list[str] = []
    depth = 0
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    i = 0
    n = len(query)
    while i < n:
        ch = query[i]
        nxt = query[i + 1] if i + 1 < n else ""
        if in_line_comment:
            current.append(ch)
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue
        if in_block_comment:
            current.append(ch)
            if ch == "*" and nxt == "/":
                current.append(nxt)
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_single:
            current.append(ch)
            if ch == "'" and nxt == "'":
                current.append(nxt)
                i += 2
                continue
            if ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            current.append(ch)
            if ch == "\\" and nxt:
                current.append(nxt)
                i += 2
                continue
            if ch == '"':
                in_double = False
            i += 1
            continue
        if ch == "/" and nxt == "/":
            in_line_comment = True
            current.append(ch)
            current.append(nxt)
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            current.append(ch)
            current.append(nxt)
            i += 2
            continue
        if ch == "'":
            in_single = True
            current.append(ch)
            i += 1
            continue
        if ch == '"':
            in_double = True
            current.append(ch)
            i += 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == "|" and depth == 0:
            stages.append("".join(current).strip())
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    tail = "".join(current).strip()
    if tail or stages:
        stages.append(tail)
    return stages


def _split_top_level_comma_items(expr: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    depth = 0
    in_single = False
    in_double = False
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        nxt = expr[i + 1] if i + 1 < n else ""
        if in_single:
            current.append(ch)
            if ch == "'" and nxt == "'":
                current.append(nxt)
                i += 2
                continue
            if ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            current.append(ch)
            if ch == "\\" and nxt:
                current.append(nxt)
                i += 2
                continue
            if ch == '"':
                in_double = False
            i += 1
            continue
        if ch == "'":
            in_single = True
            current.append(ch)
            i += 1
            continue
        if ch == '"':
            in_double = True
            current.append(ch)
            i += 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    tail = "".join(current).strip()
    if tail:
        items.append(tail)
    return items


def convert_security_alert_incident_query(
    query: str,
    *,
    extra_referenced_columns: set[str] | None = None,
) -> tuple[str, list[str], dict[str, str]]:
    """Deterministically migrate SecurityAlert / SecurityIncident KQL to AlertInfo / AlertEvidence."""
    stripped = query.strip()
    if not stripped:
        return query, [], {}
    all_tokens_list = _tokens(stripped)
    all_tokens = set(all_tokens_list)
    if not (all_tokens & {"SecurityAlert", "SecurityIncident"}):
        return query, [], {}

    references = query_table_references(
        stripped,
        known_tables={"SecurityAlert", "SecurityIncident", "AlertInfo", "AlertEvidence"},
    )
    ref_tables = {str(r.get("table") or "") for r in references if r.get("table")}
    if not (ref_tables & {"SecurityAlert", "SecurityIncident"}):
        return query, [], {}
    # Do not rewrite if mixed with unrelated tables (e.g. EmailEvents | join (SecurityIncident ...))
    non_alert_tables = ref_tables - {"SecurityAlert", "SecurityIncident", "AlertInfo", "AlertEvidence"}
    if non_alert_tables:
        return query, [], {}

    first_table = str(references[0].get("table") or "")
    extra_cols = set(extra_referenced_columns or set())
    combined_tokens = all_tokens | extra_cols
    needs_evidence = bool(combined_tokens & ALERT_EVIDENCE_INDICATOR_TOKENS) or bool(
        re.search(r"\b(?:parse_json|todynamic)\s*\(\s*Entities\b|\bmv-expand\b[^\n|]*\bEntities\b", stripped)
    )

    stages = _split_top_level_kql_stages(stripped)
    head_tokens = _tokens(stages[0]) if stages else []
    has_other_joins = any(
        tok in {"join", "union", "lookup"}
        for tok in [t.casefold() for t in all_tokens_list]
    )
    if (
        first_table not in {"SecurityAlert", "SecurityIncident"}
        or head_tokens != [first_table]
        or has_other_joins
        or ";" in all_tokens_list
    ):
        # Fallback for multi-statement / let / join queries over SecurityAlert / SecurityIncident only
        is_incident = "SecurityIncident" in ref_tables and "SecurityAlert" not in ref_tables
        direct_map = {
            **SECURITY_ALERT_DIRECT_COLUMN_MAP,
            **SECURITY_INCIDENT_DIRECT_COLUMN_MAP,
            "SecurityAlert": "AlertInfo",
            "SecurityIncident": "AlertInfo",
        }
        converted_multi = _token_replace(stripped, direct_map)
        renamed_multi = {
            tbl: "AlertInfo"
            for tbl in ("SecurityAlert", "SecurityIncident")
            if tbl in ref_tables
        }
        note_key = (
            "security_incident_migrated_to_alert_info"
            if is_incident
            else (
                "security_alert_migrated_to_alert_info_and_evidence"
                if needs_evidence
                else "security_alert_migrated_to_alert_info"
            )
        )
        return (
            converted_multi,
            [
                f"{note_key}: Migrated {', '.join(sorted(renamed_multi))} query to AlertInfo/AlertEvidence schema."
            ],
            renamed_multi,
        )

    is_incident = first_table == "SecurityIncident"
    direct_map = dict(
        SECURITY_INCIDENT_DIRECT_COLUMN_MAP if is_incident else SECURITY_ALERT_DIRECT_COLUMN_MAP
    )
    compat_map = (
        SECURITY_INCIDENT_COMPAT_ALIAS_EXPRESSIONS
        if is_incident
        else SECURITY_ALERT_COMPAT_ALIAS_EXPRESSIONS
    )

    # Check which compatibility aliases are needed by downstream projections / expressions
    compat_ordered_keys = (
        [
            "IncidentNumber",
            "IncidentName",
            "Severity",
            "Status",
            "ProviderName",
            "Description",
            "AlertIds",
            "Entities",
            "CompromisedEntity",
            "HostName",
            "IPAddress",
            "UserPrincipalName",
            *ALERT_EVIDENCE_CROSS_SURFACE_EXPRESSIONS.keys(),
        ]
        if is_incident
        else [
            "SystemAlertId",
            "AlertName",
            "DisplayName",
            "AlertSeverity",
            "ProviderName",
            "ProductName",
            "Tactics",
            "Description",
            "Entities",
            "CompromisedEntity",
            "HostName",
            "IPAddress",
            "UserPrincipalName",
            *ALERT_EVIDENCE_CROSS_SURFACE_EXPRESSIONS.keys(),
        ]
    )

    downstream_stages = stages[1:]
    has_project_or_extend = any(
        re.match(r"^(?:project(?:-away|-keep|-rename|-reorder)?|extend|summarize|mv-expand)\b", stage.strip(), re.IGNORECASE)
        for stage in downstream_stages
    )
    always_compat_keys = {
        "Description",
        "Entities",
        "Status",
        "AlertIds",
        "CompromisedEntity",
        "HostName",
        "IPAddress",
        "UserPrincipalName",
        *ALERT_EVIDENCE_CROSS_SURFACE_EXPRESSIONS.keys(),
    }
    if is_incident:
        always_compat_keys = always_compat_keys | {"IncidentName", "IncidentNumber", "Severity", "Status"}

    needed_compat: list[str] = []
    for col in compat_ordered_keys:
        if col in combined_tokens and (has_project_or_extend or col in always_compat_keys):
            expr = compat_map[col]
            needed_compat.append(f"{col} = {expr}")
    if is_incident and not needed_compat:
        needed_compat = [
            "IncidentName = Title",
            "Severity = Severity",
            'Status = column_ifexists("Status", "Active")',
        ]

    rewritten_downstream: list[str] = []
    for stage in downstream_stages:
        stage_stripped = stage.strip()
        m_kw = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\b", stage_stripped)
        kw = m_kw.group(1).lower() if m_kw else ""
        if kw == "where":
            stage_map = dict(direct_map)
            if not is_incident and "Tactics" in _tokens(stage_stripped):
                if any(tactic in stage_stripped for tactic in MITRE_TACTIC_NAMES) and not re.search(r"\bT\d{4}\b", stage_stripped):
                    stage_map["Tactics"] = "Category"
                else:
                    stage_map["Tactics"] = "AttackTechniques"
            rewritten_stage = _token_replace(stage_stripped, stage_map)
            rewritten_downstream.append(rewritten_stage)
        elif kw == "project":
            # Replace TimeGenerated -> Timestamp in project, while keeping both compatibility
            # aliases and mapped AlertInfo/AlertEvidence columns available.
            rewritten_stage = _token_replace(stage_stripped, {"TimeGenerated": "Timestamp"})
            proj_body = rewritten_stage[len(m_kw.group(0)):].strip() if m_kw else ""
            proj_items = _split_top_level_comma_items(proj_body)
            existing_proj_names: set[str] = set()
            for item in proj_items:
                item_tokens = _tokens(item)
                if item_tokens:
                    existing_proj_names.add(item_tokens[0])
            appended_proj: list[str] = []
            for src_col, tgt_col in direct_map.items():
                if src_col in existing_proj_names and tgt_col not in existing_proj_names:
                    appended_proj.append(tgt_col)
                    existing_proj_names.add(tgt_col)
            for extra_col in sorted(extra_cols):
                mapped_extra = direct_map.get(extra_col, extra_col)
                if extra_col not in existing_proj_names:
                    appended_proj.append(extra_col)
                    existing_proj_names.add(extra_col)
                if mapped_extra not in existing_proj_names:
                    appended_proj.append(mapped_extra)
                    existing_proj_names.add(mapped_extra)
            if appended_proj:
                rewritten_stage = f"{rewritten_stage}, {', '.join(appended_proj)}"
            rewritten_downstream.append(rewritten_stage)
        else:
            stage_map = {"TimeGenerated": "Timestamp"}
            if not needed_compat:
                stage_map.update(direct_map)
            rewritten_stage = _token_replace(stage_stripped, stage_map)
            rewritten_downstream.append(rewritten_stage)

    new_stages: list[str] = ["AlertInfo"]
    if needs_evidence:
        new_stages.append("join kind=leftouter AlertEvidence on AlertId")
    if needed_compat:
        new_stages.append(f"extend {', '.join(needed_compat)}")
    new_stages.extend(rewritten_downstream)

    converted = "\n| ".join(new_stages)
    if is_incident:
        if needs_evidence:
            notes = [
                "security_incident_migrated_to_alert_info",
                "security_incident_migrated_to_alert_info: Migrated SecurityIncident query to AlertInfo joined with AlertEvidence on AlertId and added incident compatibility aliases (IncidentName -> Title, Severity -> Severity, Status -> Status).",
            ]
        else:
            notes = [
                "security_incident_migrated_to_alert_info",
                "security_incident_migrated_to_alert_info: Migrated SecurityIncident query to AlertInfo and added incident compatibility aliases (IncidentName -> Title, Severity -> Severity, Status -> Status).",
            ]
        renamed = {"SecurityIncident": "AlertInfo"}
    else:
        if needs_evidence:
            notes = [
                "security_alert_migrated_to_alert_info_and_evidence",
                "security_alert_migrated_to_alert_info_and_evidence: Migrated SecurityAlert query to AlertInfo | join kind=leftouter AlertEvidence on AlertId with AlertInfo/AlertEvidence column mappings.",
            ]
        else:
            notes = [
                "security_alert_migrated_to_alert_info",
                "security_alert_migrated_to_alert_info: Migrated SecurityAlert query to AlertInfo with AlertInfo column mappings (SystemAlertId -> AlertId, AlertName -> Title, AlertSeverity -> Severity, ProviderName -> DetectionSource, ProductName -> ServiceSource, Tactics -> AttackTechniques).",
            ]
        renamed = {"SecurityAlert": "AlertInfo"}
    return converted, notes, renamed
