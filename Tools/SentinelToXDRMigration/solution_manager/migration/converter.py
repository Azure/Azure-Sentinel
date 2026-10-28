from __future__ import annotations

import hashlib
import json
import logging
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from solution_manager.core.artifacts import conversion_scope, existing_artifact_path, report_directory, portable_artifact, write_json_artifact
from jsonschema import Draft202012Validator

from solution_manager import __version__
from solution_manager.migration.catalog import (
    NATIVE_XDR_TABLES,
    SECURITY_ALERT_DIRECT_COLUMN_MAP,
    SECURITY_INCIDENT_DIRECT_COLUMN_MAP,
    _split_top_level_comma_items,
    _split_top_level_kql_stages,
    _token_replace,
    _tokens,
    configured_column_renames,
    convert_security_alert_incident_query,
    query_column_renames,
    query_has_ambiguous_table_scope,
    query_has_mixed_time_semantics,
    query_table_references,
)
from solution_manager.authoring.columns import projected_columns
from solution_manager.authoring.dependencies import dependency_plan, dependency_validation_errors
from solution_manager.core.content_paths import content_path, yaml_files
from solution_manager.migration.parser_bindings import normalize_parser_bindings
from solution_manager.reporting.report import write_transformation_report

SCHEMA_VERSION = "1.0.0"
XDR_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema" / "xdr-detection.schema.json"
INITIAL_XDR_VERSION = "3.1.0"
XDR_VERSION_PATTERN = r"3\.[1-9][0-9]*\.(?:0|[1-9][0-9]*)"
SOURCE_ID_PATTERN = r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"
PREFIXED_SOURCE_ID_PATTERN = rf"xdr-{SOURCE_ID_PATTERN}"
GRAPH_DETECTION_ID_PATTERN = r"[A-Za-z][A-Za-z0-9_-]{0,99}"
DETECTION_API_VERSION = "2026-06-01-preview"
ENTITY_CONFIRMATION_PREFIX = "Entity confirmation required:"
BEST_EFFORT_ENTITY_REVIEW_PREFIX = "Best-effort entity mapping requires review:"
NONBLOCKING_ENTITY_REVIEW_PREFIXES = (
    ENTITY_CONFIRMATION_PREFIX,
    BEST_EFFORT_ENTITY_REVIEW_PREFIX,
)
REQUIRED_ASSET_COLLECTIONS = frozenset({"hosts", "accounts", "mailboxes", "ips"})
SUPPORTED_SEVERITIES = frozenset({"informational", "low", "medium", "high"})
MITRE_CATALOG_PATH = (
    Path(__file__).resolve().parents[4]
    / ".script/tests/detectionTemplateSchemaValidation/Models/ModelValidationAttributes/KillChainTechniquesHelper.cs"
)
SEARCH_REVIEW_REASON = "search queries should be replaced with explicit tables"
BLOCKING_KQL_PATTERNS = {
    r"\bworkspace\s*\(": "cross-workspace queries require manual redesign",
}
REVIEW_KQL_PATTERNS = {
    r"\bexternaldata\s*\(": "externaldata availability must be verified by runtime validation",
    r"\bunion\s+isfuzzy\s*=\s*true\b": "isfuzzy unions can still fail semantic binding in Advanced Hunting",
}
STANDARD_BUILTIN_ASIM_PARSER_RE = re.compile(
    r"^_(?:asim|im)_(?:agentevent|alertevent|assetentity|auditevent|authentication|dhcp|dns|email|fileevent|networksession|process|registry|usermanagement|websession)[a-z0-9_]*$",
    re.IGNORECASE,
)
NRT_SUPPORTED_TABLES = frozenset(
    name.lower()
    for name in (
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
        "EmailAttachmentInfo",
        "EmailEvents",
        "EmailPostDeliveryEvents",
        "EmailUrlInfo",
        "IdentityDirectoryEvents",
        "IdentityLogonEvents",
        "IdentityQueryEvents",
        "UrlClickEvents",
        "ABAPAuditLog_C",
        "ABAPChangeDocsLog_CL",
        "AuditLogs",
        "AWSCloudTrail",
        "AWSGuardDuty",
        "AzureActivity",
        "CommonSecurityLog",
        "GCPAuditLogs",
        "MicrosoftGraphActivityLogs",
        "OfficeActivity",
        "Okta_CL",
        "OktaV2_CL",
        "PowerBIActivity",
        "PowerPlatformAdminActivity",
        "ProofpointPOD",
        "ProofPointTAPClicksPermitted_CL",
        "ProofPointTAPMessagesDelivered_CL",
        "SecurityAlert",
        "SecurityEvent",
        "SigninLogs",
        "Syslog",
    )
)

ENTITY_MAP: dict[str, tuple[str, dict[str, str | None]]] = {
    "Host": (
        "hosts",
        {
            "HostName": "nameColumn",
            "NetBiosName": "netBiosNameColumn",
            "NTDomain": "ntDomainColumn",
            "DnsDomain": "dnsDomainColumn",
            "DeviceId": "deviceIdColumn",
        },
    ),
    "Account": (
        "accounts",
        {
            "Name": "nameColumn",
            "NTDomain": "ntDomainColumn",
            "DnsDomain": "dnsDomainColumn",
            "UPNSuffix": "upnSuffixColumn",
            "Upn": "upnColumn",
            "Sid": "sidColumn",
            "AadUserId": "aadUserIdColumn",
        },
    ),
    "IP": ("ips", {"Address": "addressColumn"}),
    "URL": ("urls", {"Url": "addressColumn"}),
    "AzureResource": ("azureResources", {"ResourceId": "resourceIdColumn"}),
    "CloudApplication": ("cloudApplications", {"AppId": "appIdColumn", "Name": "nameColumn"}),
    "Mailbox": ("mailboxes", {"MailboxPrimaryAddress": "primaryAddressColumn"}),
    "DNS": ("dns", {"DomainName": "domainNameColumn"}),
    "File": ("files", {"Name": "nameColumn"}),
    "FileHash": ("files", {}),
    "MailCluster": ("mailClusters", {"Query": "queryColumn", "Source": "sourceColumn"}),
    "RegistryValue": ("registryValues", {"Name": "valueNameColumn"}),
    "SecurityGroup": (
        "securityGroups",
        {
            "DistinguishedName": "distinguishedNameColumn",
            "SID": "sidColumn",
            "ObjectGuid": "objectIdColumn",
        },
    ),
    # Sentinel process identifiers are not the hashes accepted by Graph.
    "Process": ("processes", {}),
    "MailMessage": (
        "mailMessages",
        {
            "NetworkMessageId": "networkMessageIdColumn",
            "Recipient": "recipientColumn",
            "Sender": "senderColumn",
            "P1Sender": "senderColumn",
            "P2Sender": "senderColumn",
            "Subject": "subjectColumn",
        },
    ),
}

ACCOUNT_IDENTITIES = (
    frozenset({"upnColumn"}),
    frozenset({"aadUserIdColumn"}),
    frozenset({"sidColumn"}),
    frozenset({"nameColumn", "upnSuffixColumn"}),
    frozenset({"nameColumn", "ntDomainColumn"}),
    frozenset({"nameColumn", "dnsDomainColumn"}),
)
ACCOUNT_UPN_ALIASES = frozenset(
    {
        "accountupn",
        "caller",
        "initiatingprocessaccountupn",
        "targetuserupn",
        "userprincipalname",
    }
)
INFERRED_ENTITY_ALIASES: dict[str, tuple[str, ...]] = {
    "accountUpn": (
        "AccountUpn",
        "AccountUPN",
        "UserPrincipalName",
        "InitiatingProcessAccountUpn",
        "TargetUserUpn",
    ),
    "accountId": ("AadUserId", "AccountObjectId", "UserObjectId", "EntraUserId"),
    "accountSid": ("AccountSid", "UserSid"),
    "deviceId": ("DeviceId",),
    "hostName": ("DeviceName", "HostName", "DvcHostname", "Computer"),
    "ip": (
        "CallerIpAddress",
        "DestinationIP",
        "IPAddress",
        "IpAddress",
        "LocalIP",
        "RemoteIP",
        "SourceIP",
    ),
    "url": ("RemoteUrl", "URL", "Url"),
    "resource": ("_ResourceId", "AzureResourceId", "ResourceId"),
}


class XdrYamlDumper(yaml.SafeDumper):
    pass


def _represent_string(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


XdrYamlDumper.add_representer(str, _represent_string)


@dataclass(frozen=True)
class ConversionResult:
    source: Path
    output: Path
    display_name: str
    status: str
    review_required: bool
    review_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    errors: tuple[str, ...]
    informational: tuple[str, ...] = ()
    tactic_count: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": str(self.source),
            "output": str(self.output),
            "displayName": self.display_name,
            "status": self.status,
            "reviewRequired": self.review_required,
            "reviewReasons": list(self.review_reasons),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "informational": list(self.informational),
            "directGraphDeploymentReady": (
                self.status == "converted" and not self.review_required and self.tactic_count <= 1
            ),
        }


def configure_logging(solution: str | Path | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if solution:
        log_directory = report_directory(solution, create=True)
        class PublicFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                return portable_artifact(solution, super().format(record), destination=log_directory)

        handler = logging.FileHandler(
            log_directory / "sentinel-xdr-migration.log", encoding="utf-8"
        )
        handler.setFormatter(PublicFormatter("%(asctime)s %(levelname)s %(message)s"))
        handlers.append(handler)
    logger = logging.getLogger()
    for previous in list(logger.handlers):
        if getattr(previous, "_sentinel_xdr_handler", False):
            logger.removeHandler(previous)
            previous.close()
    logger.setLevel(logging.INFO)
    for handler in handlers:
        handler._sentinel_xdr_handler = True
        if handler.formatter is None:
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:72] or "custom-detection"


def iso_duration(value: Any, default: str = "PT1H") -> tuple[str, str | None]:
    text = str(value or "").strip().lower()
    iso = text.upper()
    if iso in {"NRT", "0", "PT0S"}:
        return "PT0S", None
    if re.fullmatch(
        r"P(?:(?:\d+D)(?:T(?:\d+H)?(?:\d+M)?(?:\d+S)?)?|T(?:\d+H)?(?:\d+M)?(?:\d+S)?)",
        iso,
    ):
        return iso, None
    match = re.fullmatch(r"(\d+)\s*([smhd])", text)
    if not match:
        return default, f"unrecognized queryFrequency {value!r}; defaulted to {default}"
    amount, unit = match.groups()
    return {
        "s": f"PT{amount}S",
        "m": f"PT{amount}M",
        "h": f"PT{amount}H",
        "d": f"P{amount}D",
    }[unit], None


def solution_paths(solution: str | Path) -> tuple[Path, Path, Path]:
    root = Path(solution).expanduser().resolve()
    analytic = root / "Analytic Rules"
    output = root / "XDR Detections"
    if not root.is_dir():
        raise ValueError(f"solution path does not exist: {root}")
    if not analytic.is_dir():
        legacy_analytic = root / "Analytics Rules"
        if legacy_analytic.is_dir():
            analytic = legacy_analytic
        else:
            raise ValueError(
                f"solution has no 'Analytic Rules' or 'Analytics Rules' folder: {root}"
            )
    return root, analytic, output


def load_config(output_dir: Path, explicit: str | Path | None = None) -> dict[str, Any]:
    path = (
        Path(explicit).expanduser().resolve()
        if explicit
        else existing_artifact_path(output_dir.parent, "migration-config.yaml")
    )
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError(f"migration config must contain a YAML object: {path}")
    return value


def analytic_rule_files(solution: str | Path) -> list[Path]:
    _, analytic, _ = solution_paths(solution)
    return yaml_files(analytic)


def xdr_detection_files(output: Path) -> list[Path]:
    return list(
        path
        for path in yaml_files(output)
        if path.name.lower() not in {"migration-config.yaml", "migration-config.yml"}
    )


def inspect_solution(solution: str | Path) -> dict[str, Any]:
    root, analytic, output = solution_paths(solution)
    files = analytic_rule_files(root)
    return {
        "solution": str(root),
        "analyticRulesDirectory": str(analytic),
        "xdrDetectionsDirectory": str(output),
        "analyticRuleCount": len(files),
        "analyticRules": [path.relative_to(analytic).as_posix() for path in files],
        "existingXdrDetectionCount": len(xdr_detection_files(output)) if output.exists() else 0,
    }


def _rewrite_single_table_reference(query: str, mappings: dict[str, str]) -> tuple[str, bool]:
    if not mappings:
        return query, False
    references = query_table_references(query)
    if not references:
        return query, False
    table = str(references[0]["table"])
    target = next(
        (value for name, value in mappings.items() if str(name).casefold() == table.casefold()),
        None,
    )
    if target is None:
        return query, False
    if query_has_ambiguous_table_scope(query):
        return query, True

    token_pattern = re.compile(
        r"//[^\n]*|/\*[\s\S]*?\*/|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
        r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|[A-Za-z_][A-Za-z0-9_]*|[^\s]"
    )
    for match in token_pattern.finditer(query):
        token = match.group(0)
        if token.startswith(("//", "/*", "'", '"', "@'", '@"')):
            continue
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
            if token.casefold() != table.casefold():
                return query, True
            return query[:match.start()] + str(target) + query[match.end():], False
    return query, True


COSMETIC_TIME_COLUMNS = frozenset({
    "TimeGenerated",
    "Timestamp",
    "StartTime",
    "EndTime",
    "EventStartTime",
    "EventEndTime",
    "FirstSeen",
    "LastSeen",
})


def _parse_cosmetic_summarize_agg(item: str, default_time_col: str) -> tuple[str | None, str | None, bool, bool]:
    """Parse a single summarize aggregation item.

    Returns (alias, extend_expr, is_wildcard, is_supported).
    """
    text = item.strip()
    if not text:
        return None, None, False, False
    alias: str | None = None
    expr = text
    m_assign = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", text, re.DOTALL)
    if m_assign:
        alias = m_assign.group(1).strip()
        expr = m_assign.group(2).strip()

    m_call = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$", expr, re.DOTALL)
    if not m_call:
        return None, None, False, False
    func = m_call.group(1).strip().lower()
    args_raw = m_call.group(2).strip()
    args = _split_top_level_comma_items(args_raw) if args_raw else []

    if func in {"min", "max"}:
        if len(args) != 1:
            return None, None, False, False
        arg = args[0].strip()
        if arg not in COSMETIC_TIME_COLUMNS:
            return None, None, False, False
        target_col = default_time_col if arg in {"TimeGenerated", "Timestamp"} else arg
        out_alias = alias or f"{func}_{arg}"
        return out_alias, target_col, False, True

    if func == "count":
        if len(args) > 1:
            return None, None, False, False
        out_alias = alias or "count_"
        return out_alias, "1", False, True

    if func == "dcount":
        if not (1 <= len(args) <= 2):
            return None, None, False, False
        arg = args[0].strip()
        ident = re.sub(r"\W+", "_", arg).strip("_") or "value"
        out_alias = alias or f"dcount_{ident}"
        return out_alias, "1", False, True

    if func in {"make_set", "make_list"}:
        if not (1 <= len(args) <= 2):
            return None, None, False, False
        arg = args[0].strip()
        if not arg:
            return None, None, False, False
        prefix = "set" if func == "make_set" else "list"
        ident = re.sub(r"\W+", "_", arg).strip("_") or "value"
        out_alias = alias or f"{prefix}_{ident}"
        return out_alias, f"pack_array({arg})", False, True

    if func in {"take_any", "any"}:
        if len(args) != 1:
            return None, None, False, False
        arg = args[0].strip()
        if not arg:
            return None, None, False, False
        if arg == "*":
            return alias, None, True, True
        ident = arg if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", arg) else "any_value"
        out_alias = alias or ident
        return out_alias, arg, False, True

    if func in {"arg_max", "arg_min"}:
        if len(args) < 2:
            return None, None, False, False
        time_arg = args[0].strip()
        if time_arg not in COSMETIC_TIME_COLUMNS:
            return None, None, False, False
        rest = [a.strip() for a in args[1:]]
        if rest == ["*"]:
            return alias, None, True, True
        if len(rest) == 1 and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", rest[0]):
            out_alias = alias or rest[0]
            return out_alias, rest[0], False, True
        return None, None, False, False

    return None, None, False, False


def rewrite_cosmetic_nrt_summarize(query: str) -> tuple[str, bool, list[str]]:
    """Rewrite a trailing cosmetic summarize in a single-table NRT query to row-level extend/project."""
    stripped = query.strip()
    if not stripped:
        return query, False, []
    if query_has_ambiguous_table_scope(stripped):
        return query, False, []
    refs = query_table_references(stripped)
    if len(refs) > 1:
        return query, False, []
    stages = _split_top_level_kql_stages(stripped)
    if len(stages) < 2:
        return query, False, []

    summarize_indices = [
        idx
        for idx, stage in enumerate(stages[1:], start=1)
        if re.match(r"^summarize\b", stage.strip(), re.IGNORECASE)
    ]
    if len(summarize_indices) != 1:
        return query, False, []
    sum_idx = summarize_indices[0]

    # Check stages after summarize: any post-summarize where/having/join/union/make-series makes it behavioral
    for post_stage in stages[sum_idx + 1:]:
        post_kw_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\b", post_stage.strip())
        post_kw = post_kw_match.group(1).lower() if post_kw_match else ""
        if post_kw not in {"extend", "project", "project-rename", "project-reorder", "project-keep", "project-away"}:
            return query, False, []

    sum_stage = stages[sum_idx].strip()
    body = re.sub(r"^summarize\b", "", sum_stage, flags=re.IGNORECASE).strip()
    if not body:
        return query, False, []

    # Split body at top-level 'by' keyword
    by_split_pos: tuple[int, int] | None = None
    depth = 0
    for match in re.finditer(r"'(?:''|[^'])*'|\"(?:\\.|[^\"\\])*\"|\(|\)|\[|\]|\{|\}|\bby\b", body, flags=re.IGNORECASE):
        tok = match.group(0)
        if tok.startswith(("'", '"')):
            continue
        if tok in "([{":
            depth += 1
        elif tok in ")]}":
            depth = max(0, depth - 1)
        elif depth == 0 and tok.lower() == "by":
            by_split_pos = (match.start(), match.end())
            break

    if by_split_pos is None:
        return query, False, []

    agg_str = body[:by_split_pos[0]].strip()
    by_str = body[by_split_pos[1]:].strip()
    if not by_str:
        return query, False, []

    agg_items = _split_top_level_comma_items(agg_str) if agg_str else []
    by_items = _split_top_level_comma_items(by_str)
    if not by_items:
        return query, False, []

    all_tokens = _tokens(stripped)
    default_time_col = (
        "TimeGenerated"
        if "TimeGenerated" in all_tokens and "Timestamp" not in all_tokens
        else ("Timestamp" if "Timestamp" in all_tokens else "TimeGenerated")
    )

    extend_assignments: list[str] = []
    agg_projected_cols: list[str] = []
    wildcard_passthrough = False

    for item in agg_items:
        alias, expr, is_wildcard, is_supported = _parse_cosmetic_summarize_agg(item, default_time_col)
        if not is_supported:
            return query, False, []
        if is_wildcard:
            wildcard_passthrough = True
            continue
        if alias and expr:
            if alias != expr:
                extend_assignments.append(f"{alias} = {expr}")
            if alias not in agg_projected_cols:
                agg_projected_cols.append(alias)

    group_projected_cols: list[str] = []
    for item in by_items:
        item_stripped = item.strip()
        m_assign = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", item_stripped, re.DOTALL)
        if m_assign:
            g_alias = m_assign.group(1).strip()
            g_expr = m_assign.group(2).strip()
            m_bin = re.match(r"^bin\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,.*\)$", g_expr, re.IGNORECASE | re.DOTALL)
            if m_bin and m_bin.group(1) in COSMETIC_TIME_COLUMNS:
                target_t = default_time_col if m_bin.group(1) in {"TimeGenerated", "Timestamp"} else m_bin.group(1)
                if g_alias != target_t:
                    extend_assignments.append(f"{g_alias} = {target_t}")
            elif g_alias != g_expr:
                extend_assignments.append(f"{g_alias} = {g_expr}")
            if g_alias not in group_projected_cols:
                group_projected_cols.append(g_alias)
            continue
        m_bin_unaliased = re.match(r"^bin\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,.*\)$", item_stripped, re.IGNORECASE | re.DOTALL)
        if m_bin_unaliased and m_bin_unaliased.group(1) in COSMETIC_TIME_COLUMNS:
            target_t = default_time_col if m_bin_unaliased.group(1) in {"TimeGenerated", "Timestamp"} else m_bin_unaliased.group(1)
            if target_t not in group_projected_cols:
                group_projected_cols.append(target_t)
            continue
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", item_stripped):
            if item_stripped not in group_projected_cols:
                group_projected_cols.append(item_stripped)
            continue
        return query, False, []

    projected_order: list[str] = []
    for col in agg_projected_cols + group_projected_cols:
        if col not in projected_order:
            projected_order.append(col)

    replacement_stages: list[str] = []
    if extend_assignments:
        replacement_stages.append(f"extend {', '.join(extend_assignments)}")
    elif wildcard_passthrough and group_projected_cols:
        first_col = group_projected_cols[0]
        replacement_stages.append(f"extend {first_col} = {first_col}")

    if not wildcard_passthrough and projected_order:
        replacement_stages.append(f"project {', '.join(projected_order)}")

    new_stages = stages[:sum_idx] + replacement_stages + stages[sum_idx + 1:]
    rewritten = "\n| ".join(new_stages)
    notes = [
        "nrt_cosmetic_summarize_rewritten",
        "nrt_cosmetic_summarize_rewritten: Rewrote trailing cosmetic NRT summarize wrapper into row-level extend/project to preserve PT0S Continuous execution.",
    ]
    return rewritten, True, notes


def convert_query(
    query: str,
    config: dict[str, Any] | None = None,
    *,
    extra_referenced_columns: set[str] | None = None,
) -> tuple[str, list[str], list[str]]:
    cfg = config or {}
    warnings: list[str] = []
    errors: list[str] = []
    converted = query.strip()

    configured_table_mappings = {
        str(k): str(v) for k, v in (cfg.get("tableMappings") or {}).items()
    }
    has_explicit_security_alert_override = any(
        str(k).casefold() in {"securityalert", "securityincident"}
        for k in configured_table_mappings
    )
    security_alert_notes: list[str] = []
    if not has_explicit_security_alert_override:
        converted, security_alert_notes, _ = convert_security_alert_incident_query(
            converted,
            extra_referenced_columns=extra_referenced_columns,
        )

    converted, table_mapping_deferred = _rewrite_single_table_reference(
        converted,
        configured_table_mappings,
    )
    function_mappings = {
        str(k): str(v) for k, v in (cfg.get("functionMappings") or {}).items()
    }
    converted = _token_replace(converted, function_mappings)

    catalog_mappings = {} if security_alert_notes else query_column_renames(converted)
    ambiguous_scope = False if security_alert_notes else query_has_ambiguous_table_scope(query)
    column_mappings: dict[str, str] = {} if ambiguous_scope else catalog_mappings
    configured_mappings, configured_ambiguous = configured_column_renames(query, cfg)
    if not security_alert_notes:
        ambiguous_scope = configured_ambiguous
    column_mappings.update(configured_mappings)
    converted = _token_replace(converted, column_mappings)
    converted = "\n".join(line.rstrip() for line in converted.splitlines())
    converted = re.sub(r";\s*\Z", "", converted)

    warnings.extend(security_alert_notes)
    for pattern, message in BLOCKING_KQL_PATTERNS.items():
        if re.search(pattern, converted, re.IGNORECASE):
            errors.append(message)
    for pattern, message in REVIEW_KQL_PATTERNS.items():
        if re.search(pattern, converted, re.IGNORECASE):
            warnings.append(message)
    asim_calls = [
        match.group(1)
        for match in re.finditer(r"\b(_(?:[Ii]m|[Aa][Ss]im)_[A-Za-z0-9_]+)\s*\(", converted)
    ]
    if any(not STANDARD_BUILTIN_ASIM_PARSER_RE.match(name) for name in asim_calls):
        warnings.append("ASIM parser availability must be verified in Advanced Hunting")
    if _has_search_operator(converted):
        warnings.append(SEARCH_REVIEW_REASON)
    if query_has_mixed_time_semantics(converted):
        warnings.append(
            "query mixes native Defender and Sentinel workload tables; "
            "time columns were preserved and require runtime validation"
        )
    if ambiguous_scope:
        warnings.append(
            "configured column mappings were not applied because table/alias scope is ambiguous"
        )
    elif not security_alert_notes and query_has_ambiguous_table_scope(query) and catalog_mappings:
        warnings.append(
            "catalog column mappings were not applied because table/alias scope is ambiguous"
        )
    if table_mapping_deferred:
        warnings.append(
            "configured table mapping was not applied because table/alias scope is ambiguous"
        )

    return converted, warnings, errors


def convert_query_with_mapping_evidence(
    query: str,
    config: dict[str, Any],
    *,
    source_metadata: dict[str, Any] | None = None,
    target_metadata: dict[str, Any] | None = None,
    runtime_evidence: dict[str, Any] | None = None,
) -> tuple[str, list[str], list[str], dict[str, Any]]:
    """Convert with the existing engine and return separate hash-bound evidence."""
    from solution_manager.migration.mapping_evidence import build_mapping_evidence

    target_query, warnings, errors = convert_query(query, config)
    evidence = build_mapping_evidence(
        query,
        target_query,
        source_metadata=source_metadata,
        target_metadata=target_metadata,
        config=config,
        runtime_evidence=runtime_evidence,
    )
    return target_query, warnings, errors, evidence


def _valid_account(fields: dict[str, str]) -> bool:
    present = set(fields)
    return any(required <= present for required in ACCOUNT_IDENTITIES)


def _find_column(columns: set[str] | None, aliases: tuple[str, ...]) -> str | None:
    if columns is None:
        return None
    lookup = {column.lower(): column for column in columns}
    return next((lookup[alias.lower()] for alias in aliases if alias.lower() in lookup), None)


def _repair_account(
    fields: dict[str, str],
    source_fields: dict[str, str],
    columns: set[str] | None,
    warnings: list[str],
) -> dict[str, str]:
    if _valid_account(fields):
        return fields
    name_column = fields.get("nameColumn") or source_fields.get("Name")
    if name_column and name_column.lower() in ACCOUNT_UPN_ALIASES:
        warnings.append(
            f"Account.Name column `{name_column}` was mapped as a complete UPN identity"
        )
        return {"upnColumn": name_column}
    if "nameColumn" in fields:
        for target, aliases in (
            ("upnSuffixColumn", ("UPNSuffix", "AccountUPNSuffix", "UserDomain")),
            ("ntDomainColumn", ("NTDomain", "AccountNTDomain")),
            ("dnsDomainColumn", ("DnsDomain", "AccountDnsDomain")),
        ):
            column = _find_column(columns, aliases)
            if column:
                warnings.append(
                    f"Account mapping was completed with projected column `{column}`"
                )
                return {**fields, target: column}
    for target, aliases in (
        ("upnColumn", INFERRED_ENTITY_ALIASES["accountUpn"]),
        ("aadUserIdColumn", INFERRED_ENTITY_ALIASES["accountId"]),
        ("sidColumn", INFERRED_ENTITY_ALIASES["accountSid"]),
    ):
        column = _find_column(columns, aliases)
        if column:
            warnings.append(
                f"Account mapping was repaired from projected column `{column}`"
            )
            return {target: column}
    if name_column and (columns is None or name_column in columns):
        warnings.append(
            f"{ENTITY_CONFIRMATION_PREFIX} `{name_column}` was provisionally mapped "
            "to Account.upnColumn. Confirm that the source always emits a complete "
            "UPN; otherwise project an Entra user ID, SID, or account name plus domain"
        )
        return {"upnColumn": name_column}
    warnings.append("Account mapping is incomplete and was removed")
    return {}


def _infer_entities(
    columns: set[str] | None,
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    if columns is None:
        return {}, []
    output: dict[str, list[dict[str, Any]]] = {}
    for collection, identifier, field, aliases in (
        ("accounts", "account1", "upnColumn", INFERRED_ENTITY_ALIASES["accountUpn"]),
        ("hosts", "host1", "deviceIdColumn", INFERRED_ENTITY_ALIASES["deviceId"]),
        ("ips", "ip1", "addressColumn", INFERRED_ENTITY_ALIASES["ip"]),
        ("urls", "url1", "addressColumn", INFERRED_ENTITY_ALIASES["url"]),
        (
            "azureResources",
            "azureResource1",
            "resourceIdColumn",
            INFERRED_ENTITY_ALIASES["resource"],
        ),
    ):
        column = _find_column(columns, aliases)
        if column:
            output[collection] = [{"id": identifier, field: column}]
    host_name = _find_column(columns, INFERRED_ENTITY_ALIASES["hostName"])
    if host_name:
        host = output.setdefault("hosts", [{"id": "host1"}])[0]
        host["nameColumn"] = host_name
    warnings = (
        ["No valid source mapping survived; inferred entities from projected columns"]
        if output
        else []
    )
    return output, warnings


def _has_search_operator(query: str) -> bool:
    """Recognize search at query boundaries, not in comments or literal text."""
    tokens = _tokens(query)
    for index, token in enumerate(tokens):
        if token.lower() != "search":
            continue
        if index and tokens[index - 1] not in {"|", ";", "(", "{", "="}:
            continue
        # A bare table/column named search is not an operator with a predicate.
        if index + 1 >= len(tokens):
            continue
        operand = tokens[index + 1]
        if re.fullmatch(
            r"and|or|between|matches|has(?:_cs|_any|_all|prefix(?:_cs)?|suffix(?:_cs)?)?"
            r"|(?:contains|startswith|endswith)(?:_cs)?",
            operand,
            re.IGNORECASE,
        ):
            continue
        if re.match(r"[\w'\"@`(*\[]", operand):
            return True
    return False


def _pipeline_parts(query: str) -> list[list[str]] | None:
    """Split a single-table pipeline, rejecting branches and local definitions."""
    tokens = _tokens(query)
    parts: list[list[str]] = [[]]
    depth = 0
    for token in tokens:
        if token == ";":
            return None
        if token == "|":
            if depth:
                return None
            parts.append([])
        else:
            parts[-1].append(token)
        if token in {"(", "[", "{"}:
            depth += 1
        elif token in {")", "]", "}"}:
            depth -= 1
        if depth < 0:
            return None
    if depth or len(parts[0]) != 1 or not re.fullmatch(r"\w+", parts[0][0]):
        return None
    return parts


def _expression_items(tokens: list[str]) -> list[list[str]]:
    items: list[list[str]] = [[]]
    depth = 0
    for token in tokens:
        if token == "," and not depth:
            items.append([])
            continue
        items[-1].append(token)
        if token in {"(", "[", "{"}:
            depth += 1
        elif token in {")", "]", "}"}:
            depth -= 1
    return items


def _summarize_groups(part: list[str]) -> list[list[str]] | None:
    depth = 0
    for index, token in enumerate(part):
        if token == "by" and not depth:
            return _expression_items(part[index + 1:])
        if token in {"(", "[", "{"}:
            depth += 1
        elif token in {")", "]", "}"}:
            depth -= 1
    return None


def _is_alert_evidence_join_part(part: list[str]) -> bool:
    return bool(part and part[0] == "join" and "AlertEvidence" in part)


def _native_pipeline_table(query: str) -> str | None:
    """Recognize a native surface without claiming column or time equivalence."""
    parts = _pipeline_parts(query)
    if not parts or parts[0][0] not in NATIVE_XDR_TABLES:
        return None
    if any(
        not part
        or (part[0] not in {"where", "extend", "project", "summarize"} and not _is_alert_evidence_join_part(part))
        for part in parts[1:]
    ):
        return None
    return parts[0][0]


def _migrated_alert_pipeline_table(source_query: str, target_query: str) -> str | None:
    """Recognize SecurityAlert/SecurityIncident pipelines migrated to AlertInfo."""
    source_parts = _pipeline_parts(source_query)
    if not source_parts or source_parts[0][0] not in {"SecurityAlert", "SecurityIncident"}:
        return None
    if any(
        not part or part[0] not in {"where", "extend", "project", "summarize"}
        for part in source_parts[1:]
    ):
        return None
    target_table = _native_pipeline_table(target_query)
    return "AlertInfo" if target_table == "AlertInfo" else None


def _linear_facts(
    query: str, *, allow_aggregation: bool = False,
) -> tuple[list[list[str]], set[str] | None, dict[str, list[str]]] | None:
    """Prove local column facts; aggregation is opt-in for identity proofs only."""
    parts = _pipeline_parts(query)
    if not parts:
        return None
    columns: set[str] | None = None
    assignments: dict[str, list[str]] = {}
    for part in parts[1:]:
        if _is_alert_evidence_join_part(part):
            continue
        if part and part[0] == "summarize" and allow_aggregation:
            groups = _summarize_groups(part)
            if not groups:
                return None
            preserved = {item[0] for item in groups if len(item) == 1}
            if columns is not None and not preserved <= columns:
                return None
            # Only bare grouping keys preserve identity. Aggregate outputs and
            # computed keys cannot establish an equivalent source identity.
            columns = preserved
            assignments = {key: value for key, value in assignments.items() if key in preserved}
            continue
        if not part or part[0] not in {"where", "extend", "project"}:
            return None
        if part[0] == "where":
            continue
        items = _expression_items(part[1:])
        projected: set[str] = set()
        for item in items:
            if not item or not re.fullmatch(r"[A-Za-z_]\w*", item[0]):
                return None
            if len(item) != 1 and (len(item) < 3 or item[1] != "="):
                return None
            if len(item) == 1 and columns is not None and item[0] not in columns:
                return None
            projected.add(item[0])
            if len(item) > 1:
                assignments[item[0]] = item[2:]
        if part[0] == "project":
            columns = projected
            assignments = {key: value for key, value in assignments.items() if key in columns}
        elif columns is not None:
            columns.update(projected)
    return parts, columns, assignments


def _host_full_name_preserved(
    source_fields: dict[str, str], fields: dict[str, str], query: str,
) -> bool:
    full = source_fields.get("FullName")
    name = fields.get("nameColumn")
    domain = fields.get("dnsDomainColumn")
    facts = _linear_facts(query, allow_aggregation=True)
    if not full or not name or not domain or not facts:
        return False
    parts, columns, assignments = facts
    if columns is not None and not {full, name, domain} <= columns:
        return False
    for part in parts[1:]:
        if part[0] == "summarize" and [full] not in (_summarize_groups(part) or []):
            return False
        if part[0] == "project" and [full] not in _expression_items(part[1:]):
            return False
    # Reject reassigned identities, including assignments later projected away.
    for column in (full, name, domain):
        count = sum(
            part[index:index + 2] == [column, "="]
            for part in parts[1:] for index in range(len(part) - 1)
        )
        if count != (0 if column == full else 1):
            return False
    expected_name = _tokens(
        f"iff({full} has '.', substring({full}, 0, indexof({full}, '.')), {full})"
    )
    expected_domain = _tokens(
        f"iff({full} has '.', substring({full}, indexof({full}, '.') + 1), '')"
    )
    return assignments.get(name) == expected_name and assignments.get(domain) == expected_domain


SCHEDULE_REFERENCE = "https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules#lookback"
NATIVE_LOOKBACK_SECONDS = {3600: 14400, 10800: 43200, 43200: 172800, 86400: 2592000}


def _duration_seconds(value: Any) -> int | None:
    duration, error = iso_duration(value)
    if error:
        return None
    match = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", duration)
    if not match or not any(match.groups()):
        return None
    seconds = sum(int(part or 0) * scale for part, scale in zip(match.groups(), (86400, 3600, 60, 1)))
    return seconds if seconds > 0 else None


def _event_window(query: str, time_column: str) -> tuple[int | None, str | None]:
    parts = _pipeline_parts(query)
    if not parts or any(
        not part
        or (part[0] not in {"where", "extend", "project", "summarize"} and not _is_alert_evidence_join_part(part))
        for part in parts[1:]
    ):
        return None, "query shape or time filters cannot be proven by the conservative assessor"
    if any(
        part[index:index + 2] == [time_column, "="]
        for part in parts[1:] for index in range(len(part) - 1)
    ):
        return None, "event time is reassigned"
    windows: list[int] = []
    time_tokens = {"Timestamp", "TimeGenerated", "ago", "now", "datetime", "ingestion_time"}
    for part in parts[1:]:
        if part[0] == "where" and time_tokens.intersection(part):
            if not (
                len(part) == 7 and part[1] == time_column and part[2] in {">", ">="}
                and part[3:5] == ["ago", "("] and part[-1] == ")"
            ):
                return None, "time filter or ingestion-time basis is ambiguous"
            seconds = _duration_seconds(part[5])
            if seconds is None:
                return None, "time filter duration is unknown"
            windows.append(seconds)
        elif part[0] != "where" and {"ago", "now", "datetime", "ingestion_time"}.intersection(part):
            return None, "time expressions outside a simple event-time predicate require review"
    if not windows:
        return None, "no explicit event-time bound proves equivalence to Defender ingestion-time evaluation"
    return min(windows), None


def _replace_event_time_column(query: str, source_column: str, target_column: str) -> str | None:
    parts = _pipeline_parts(query)
    if not parts or any(
        not part
        or (part[0] not in {"where", "extend", "project", "summarize"} and not _is_alert_evidence_join_part(part))
        for part in parts[1:]
    ):
        return None
    if any(
        part[index:index + 2] == [source_column, "="]
        for part in parts[1:] for index in range(len(part) - 1)
    ):
        return None

    token_pattern = re.compile(
        r"//[^\n]*|/\*[\s\S]*?\*/|```[\s\S]*?```"
        r"|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
        r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\""
        r"|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?[smhd]?|>=|<=|==|!=|[^\s]"
    )
    spans = [
        (match.start(), match.end())
        for match in token_pattern.finditer(query)
        if match.group(0) == source_column
    ]
    if not spans:
        return query
    result = query
    for start, end in reversed(spans):
        result = result[:start] + target_column + result[end:]
    return result


def _format_kql_duration(seconds: int) -> str:
    for scale, suffix in ((86400, "d"), (3600, "h"), (60, "m")):
        if seconds % scale == 0:
            return f"{seconds // scale}{suffix}"
    return f"{seconds}s"


def _assess_nrt_eligibility(source_query: str, target_query: str) -> tuple[bool, list[str]]:
    """Check Defender XDR Continuous (NRT) query and table eligibility."""
    reasons: list[str] = []
    from solution_manager.migration._workbook_core import rewrite

    segments = rewrite._segments(target_query or "")
    if any(kind == "comment" for kind, _ in segments) or "/*" in "".join(
        text for kind, text in segments if kind == "code"
    ):
        reasons.append("Continuous (NRT) frequency does not support KQL comments")
    code = "".join(text if kind == "code" else " " * len(text) for kind, text in segments)
    if re.search(r"\bexternal_?data\s*\(", code, re.IGNORECASE):
        reasons.append("Continuous (NRT) frequency does not support externaldata")
    if re.search(r"\b(?:join|union|lookup)\b", code, re.IGNORECASE):
        reasons.append("Continuous (NRT) frequency does not support join, union, or lookup operators")
    if re.search(r"\b(?:summarize|make-series)\b|\|\s*count\b", code, re.IGNORECASE):
        reasons.append("Continuous (NRT) frequency does not support summarize or aggregation operators")

    refs = query_table_references(target_query)
    tables = []
    for ref in refs:
        t = str(ref.get("table") or "").strip()
        if t and t.lower() not in {x.lower() for x in tables}:
            tables.append(t)
    if len(tables) != 1:
        reasons.append(
            "Continuous (NRT) frequency requires a single supported table"
            if not tables
            else f"Continuous (NRT) frequency requires a single table, found {', '.join(tables)}"
        )
    else:
        table = tables[0]
        if table.lower() not in NRT_SUPPORTED_TABLES:
            reasons.append(
                f"table {table} is not supported for Continuous (NRT) frequency in Defender XDR"
            )
        elif table.lower() == "emailevents" and re.search(
            r"\b(?:LatestDeliveryLocation|LatestDeliveryAction)\b", code, re.IGNORECASE
        ):
            reasons.append(
                "EmailEvents columns LatestDeliveryLocation and LatestDeliveryAction are not supported in Continuous (NRT) frequency"
            )
    return not reasons, reasons


_FILENAME_ONLY_HASH_COLUMNS = frozenset(
    {
        "filename",
        "initiatingprocessfilename",
        "folderpath",
        "initiatingprocessfolderpath",
        "filepath",
        "targetfilename",
        "sourcefilename",
        "imagefile",
        "process",
        "processname",
        "commandline",
        "processcommandline",
        "initiatingprocesscommandline",
    }
)
_SYNTHETIC_HASH_FUNCTIONS = frozenset(
    {
        "hash",
        "hash_sha1",
        "hash_sha256",
        "hash_md5",
        "hash_xxhash64",
        "hash_combine",
        "hash_many",
        "strcat",
    }
)


def _is_non_hash_or_synthetic_hash_column(query: str, column: str) -> str | None:
    """Return a rejection reason if column is a filename-only binding or synthetic text hash."""
    col = (column or "").strip()
    if not col:
        return None
    if col.lower() in _FILENAME_ONLY_HASH_COLUMNS:
        return "filename-only or non-hash binding"
    facts = _linear_facts(query)
    if facts:
        assignments = facts[2]
        rhs = assignments.get(col)
        if rhs:
            if len(rhs) == 1 and rhs[0].lower() in _FILENAME_ONLY_HASH_COLUMNS:
                return "filename-only or non-hash binding"
            if any(tok.lower() in _SYNTHETIC_HASH_FUNCTIONS for tok in rhs):
                return "synthetic text hash"
    from solution_manager.migration._workbook_core import rewrite

    code = "".join(text if kind == "code" else " " * len(text) for kind, text in rewrite._segments(query or ""))
    assign_pat = re.compile(
        rf"\b{re.escape(col)}\s*=\s*(?:tostring\s*\(\s*)?({'|'.join(_SYNTHETIC_HASH_FUNCTIONS)})\s*\(",
        re.IGNORECASE,
    )
    if assign_pat.search(code):
        return "synthetic text hash"
    alias_pat = re.compile(
        rf"\b{re.escape(col)}\s*=\s*({'|'.join(_FILENAME_ONLY_HASH_COLUMNS)})\b(?!\s*\()",
        re.IGNORECASE,
    )
    if alias_pat.search(code):
        return "filename-only or non-hash binding"
    return None


def constrain_event_window(
    doc: dict[str, Any], source_query: str, target_query: str, frequency: str,
) -> tuple[str, dict[str, Any] | None, str | None]:
    source_period = _duration_seconds(doc.get("queryPeriod"))
    source_frequency = _duration_seconds(doc.get("queryFrequency"))
    target_frequency = _duration_seconds(frequency)
    if (
        str(doc.get("kind") or "").lower() != "nrt"
        and source_frequency == 3600
        and source_period == 3600
        and target_frequency == 3600
    ):
        has_aggregation = bool(re.search(r"\b(?:summarize|make-series)\b", target_query, re.IGNORECASE))
        metadata = {
            "status": "default-native-lookback",
            "appliedDefault": "hourly-1h-to-native-4h-lookback",
            "queryFrequency": str(doc.get("queryFrequency") or "1h").strip(),
            "queryPeriod": str(doc.get("queryPeriod") or "1h").strip(),
            "targetFrequency": frequency,
            "effectiveLookback": "PT4H",
            "originalSentinelLookbackSeconds": source_period,
            "effectiveEventWindowSeconds": 14400,
            "xdrServiceWindowSeconds": 14400,
            "filterInjected": False,
            "parityClaimed": False,
            "hasAggregation": has_aggregation,
            "aggregationWindowDifference": has_aggregation,
            "timingDifference": (
                "Four hours (PT4H / 14400s) is the native XDR ingestion-based lookback window "
                "for PT1H execution frequency, not the execution frequency; original Sentinel "
                "queryPeriod was 1h (3600s)."
            ),
            "aggregationDifference": (
                "Query contains summarize/make-series aggregation; evaluating over the native "
                "4-hour XDR lookback window without an injected 1h event-time filter may "
                "aggregate up to 4 hours of events per hourly run instead of 1 hour."
                if has_aggregation
                else "No summarize/make-series aggregation detected in query; native 4-hour XDR "
                     "lookback relies on Defender XDR alert deduplication across hourly runs."
            ),
        }
        return target_query, metadata, None
    source_table = _native_pipeline_table(source_query) or _migrated_alert_pipeline_table(
        source_query, target_query
    )
    target_table = _native_pipeline_table(target_query)
    native_tokens = set(_tokens(source_query)) | set(_tokens(target_query))
    service_window = (
        NATIVE_LOOKBACK_SECONDS.get(target_frequency or 0)
        if native_tokens.intersection(NATIVE_XDR_TABLES)
        else None
    )
    if (
        str(doc.get("kind") or "").lower() == "nrt"
        or source_period is None
        or source_frequency is None
        or source_frequency != target_frequency
        or service_window is None
        or source_period >= service_window
    ):
        return target_query, None, None
    if source_table is None or target_table is None or source_table != target_table:
        return target_query, None, (
            "Original Sentinel lookback is shorter than the native XDR service window, "
            "but source and target table inputs cannot be proven equivalent"
        )

    source_time_column = "TimeGenerated" if "TimeGenerated" in _tokens(source_query) else "Timestamp"
    if not any(column in _tokens(source_query) for column in ("Timestamp", "TimeGenerated")):
        return target_query, None, (
            "Original Sentinel lookback is shorter than the native XDR service window, "
            "but the source query does not establish an event-time column"
        )
    bound_query = target_query
    if source_time_column == "TimeGenerated":
        bound_query = _replace_event_time_column(
            bound_query, "TimeGenerated", "Timestamp",
        )
        if bound_query is None:
            return target_query, None, (
                "Original Sentinel lookback is shorter than the native XDR service window, "
                "but TimeGenerated cannot be safely bound to the target Timestamp column"
            )

    source_bound, source_issue = _event_window(source_query, source_time_column)
    if source_issue and source_issue != "no explicit event-time bound proves equivalence to Defender ingestion-time evaluation":
        return target_query, None, (
            "Original Sentinel lookback is shorter than the native XDR service window, "
            f"but the source event-time window is ambiguous: {source_issue}"
        )
    effective_window = min(source_period, source_bound) if source_bound is not None else source_period

    target_bound, target_issue = _event_window(bound_query, "Timestamp")
    if target_issue and target_issue != "no explicit event-time bound proves equivalence to Defender ingestion-time evaluation":
        return target_query, None, (
            "Original Sentinel lookback is shorter than the native XDR service window, "
            f"but the target event-time window is ambiguous: {target_issue}"
        )
    if target_bound is not None and target_bound < effective_window:
        return target_query, None, (
            "Original Sentinel lookback is shorter than the native XDR service window, "
            "but the existing target event-time filter is narrower than the source window"
        )

    injected = target_bound is None or target_bound > effective_window
    if injected:
        token_pattern = re.compile(
            r"//[^\n]*|/\*[\s\S]*?\*/|```[\s\S]*?```"
            r"|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
            r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\""
            r"|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?[smhd]?|>=|<=|==|!=|[^\s]"
        )
        first_table = next(
            (
                match for match in token_pattern.finditer(bound_query)
                if match.group(0) == target_table
            ),
            None,
        )
        if first_table is None:
            return target_query, None, (
                "Original Sentinel lookback is shorter than the native XDR service window, "
                "but the target input location could not be identified safely"
            )
        span = _format_kql_duration(effective_window)
        bound_query = (
            bound_query[:first_table.end()]
            + f" | where Timestamp >= ago({span})"
            + bound_query[first_table.end():]
        )

    metadata = {
        "status": "constrained",
        "originalSentinelLookbackSeconds": source_period,
        "effectiveEventWindowSeconds": effective_window,
        "xdrServiceWindowSeconds": service_window,
        "sourceTimeColumn": source_time_column,
        "targetTimeColumn": "Timestamp",
        "filterInjected": injected,
        "rationale": (
            "A conservative single-native-table pipeline proof established the source and target "
            "input and time-column binding. The target Timestamp filter is placed immediately "
            "after the table input and before all filters, projections, and aggregations."
        ),
        "lateIngestionRisk": (
            "Late-ingestion risk: events ingested after their Timestamp falls outside this "
            "constrained event-time window can be missed; runtime qualification is required."
        ),
    }
    return bound_query, metadata, None


def assess_schedule(
    doc: dict[str, Any], source_query: str, target_query: str, frequency: str,
) -> tuple[list[str], list[str]]:
    source_frequency = _duration_seconds(doc.get("queryFrequency"))
    source_period = _duration_seconds(doc.get("queryPeriod"))
    target_frequency = _duration_seconds(frequency)
    source_table = _native_pipeline_table(source_query) or _migrated_alert_pipeline_table(
        source_query, target_query
    )
    target_table = _native_pipeline_table(target_query)
    native = target_table is not None
    target_period = NATIVE_LOOKBACK_SECONDS.get(target_frequency) if native else None
    summary = (
        f"Schedule assessment: source frequency={doc.get('queryFrequency') or 'unknown'}, "
        f"lookback={doc.get('queryPeriod') or 'unknown'}; target frequency={frequency}, "
        f"native lookback={str(target_period) + 's' if target_period else 'unknown/unconfigured'}"
    )
    if str(doc.get("kind") or "").lower() == "nrt" and frequency in {"PT0S", "NRT"}:
        nrt_eligible, nrt_reasons = _assess_nrt_eligibility(source_query, target_query)
        if nrt_eligible:
            return [], [
                f"Schedule assessment: source kind=NRT; target frequency={frequency} (Continuous); "
                f"single-table Continuous (NRT) execution is supported in Defender XDR. See {SCHEDULE_REFERENCE}"
            ]
        return [
            f"Schedule assessment: source kind=NRT; target frequency={frequency} (Continuous); "
            f"query is not eligible for Continuous (NRT) execution ({'; '.join(nrt_reasons)}). See {SCHEDULE_REFERENCE}"
        ], []
    reason = None
    if str(doc.get("kind") or "").lower() == "nrt":
        reason = "source NRT timing is not preserved by the emitted scheduled frequency"
    elif source_frequency is None or source_period is None:
        reason = "source frequency or lookback is unknown"
    elif source_frequency != target_frequency:
        reason = "source and target frequencies differ"
    elif not native or source_table is None:
        reason = "mixed, Sentinel-only, or unknown query surface; no custom lookback is configured in the payload"
    elif source_table != target_table:
        reason = "source and target native tables differ; time-basis equivalence is unverified"
    elif target_period is None:
        reason = "target frequency has no documented native fixed lookback"
    elif source_period > target_period:
        reason = "source and native lookbacks differ; an event-time filter alone does not configure the target ingestion lookback"
    if reason:
        return [f"{summary}; {reason}. See {SCHEDULE_REFERENCE}"], []
    source_time = "TimeGenerated" if "TimeGenerated" in _tokens(source_query) else "Timestamp"
    source_bound, source_issue = _event_window(source_query, source_time)
    target_bound, target_issue = _event_window(target_query, "Timestamp")
    narrower_source_period = source_period < target_period
    if (
        narrower_source_period
        and source_issue == "no explicit event-time bound proves equivalence to Defender ingestion-time evaluation"
        and target_bound is not None
    ):
        source_bound = source_period
        source_issue = None
    if source_issue or target_issue:
        reason = source_issue or target_issue
        if source_period != target_period:
            reason = f"source and native service windows differ; {reason}"
        return [f"{summary}; {reason}. See {SCHEDULE_REFERENCE}"], []
    source_effective = min(source_period, source_bound)
    target_effective = min(target_period, target_bound)
    summary += f"; effective event windows source={source_effective}s, target={target_effective}s"
    if source_effective != target_effective:
        return [f"{summary}; effective lookbacks differ. See {SCHEDULE_REFERENCE}"], []
    if narrower_source_period:
        message = (
            f"{summary}; event-time window constrained to original Sentinel lookback. "
            f"The XDR service window remains {target_period}s and is not identical to "
            "the Sentinel service window; late-ingestion risk remains and cadence/service-window "
            f"parity is not established. See {SCHEDULE_REFERENCE}"
        )
        return [message], [message]
    return [], [
        f"{summary}; frequency and explicit event-time window are preserved. "
        f"Ingestion delays, initial runs and alert deduplication still require runtime qualification. See {SCHEDULE_REFERENCE}"
    ]


def convert_entities(
    doc: dict[str, Any],
    query: str,
    column_mappings: dict[str, str] | None = None,
    *,
    informational: list[str] | None = None,
    defer_unmapped_entity_warnings: bool = False,
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    output: dict[str, list[dict[str, Any]]] = {}
    warnings: list[str] = []
    counters: dict[str, int] = {}
    columns = projected_columns(query)
    facts = _linear_facts(query)
    if facts and facts[1] is not None:
        columns = facts[1]
    information = informational if informational is not None else []

    for entity in doc.get("entityMappings") or []:
        entity_type = str(entity.get("entityType") or "")
        if entity_type not in ENTITY_MAP:
            if not defer_unmapped_entity_warnings:
                warnings.append(f"converter cannot map {entity_type or 'Unknown entity'} from the source identifiers")
            continue
        collection, identifiers = ENTITY_MAP[entity_type]
        fields: dict[str, str] = {}
        source_fields: dict[str, str] = {}
        unsupported: list[str] = []
        for mapping in entity.get("fieldMappings") or []:
            identifier = str(mapping.get("identifier") or "")
            source_column = str(mapping.get("columnName") or "")
            column = (column_mappings or {}).get(source_column, source_column)
            if identifier and column:
                source_fields[identifier] = column
            target = identifiers.get(identifier)
            if target and column and (columns is None or column in columns):
                if target in fields and fields[target] != column:
                    warnings.append(
                        f"converter cannot map {entity_type}.{identifier} column `{column}` "
                        f"without replacing conflicting {target} column `{fields[target]}`"
                    )
                else:
                    fields[target] = column
            elif target and column:
                warnings.append(
                    f"{entity_type}.{identifier} column `{column}` is not produced by the query"
                )
            elif identifier:
                unsupported.append(identifier)
        if entity_type == "FileHash":
            algorithm_column = source_fields.get("Algorithm", "")
            value_column = source_fields.get("Value", "")
            algorithm = facts[2].get(algorithm_column) if facts else None
            target = {"'SHA1'": "sha1Column", "'SHA256'": "sha256Column"}.get(
                algorithm[0].upper() if algorithm and len(algorithm) == 1 else ""
            )
            bad_hash_reason = (
                _is_non_hash_or_synthetic_hash_column(query, value_column)
                if value_column
                else None
            )
            if target and value_column and columns is not None and value_column in columns and not bad_hash_reason:
                fields[target] = value_column
                unsupported = [value for value in unsupported if value not in {"Algorithm", "Value"}]
                information.append(
                    f"FileHash.Algorithm `{algorithm_column}` is the query-proven constant "
                    f"{algorithm[0]}; FileHash.Value `{value_column}` is represented by files.{target}"
                )
            elif bad_hash_reason:
                warnings.append(
                    f"converter cannot map FileHash.Algorithm/Value: column `{value_column}` is a "
                    f"{bad_hash_reason}; a genuine content SHA-1/SHA-256 is required"
                )
                unsupported = [value for value in unsupported if value not in {"Algorithm", "Value"}]
            else:
                warnings.append(
                    "converter cannot map FileHash.Algorithm/Value: requires a query-proven "
                    "constant SHA1 or SHA256 algorithm and an available hash value column; "
                    "MD5, unknown algorithms and linked file/process references are not inferred"
                )
                unsupported = [value for value in unsupported if value not in {"Algorithm", "Value"}]
        if entity_type == "Account" and not _valid_account(fields):
            fields = _repair_account(fields, source_fields, columns, warnings)
        for identifier in unsupported:
            if entity_type == "Host" and identifier == "FullName" and _host_full_name_preserved(source_fields, fields, query):
                information.append(
                    f"Host.FullName `{source_fields['FullName']}` is safely represented by retained "
                    f"nameColumn `{fields['nameColumn']}` and dnsDomainColumn `{fields['dnsDomainColumn']}`; "
                    "the query explicitly decomposes that same full name. No fullNameColumn is emitted"
                )
            elif (
                entity_type == "Host"
                and identifier == "FullName"
                and source_fields.get(identifier)
                and (columns is None or source_fields[identifier] in columns)
            ):
                full_name_column = source_fields[identifier]
                candidate = fields.get("nameColumn")
                if not candidate:
                    candidate = full_name_column
                    fields["nameColumn"] = candidate
                warnings.append(
                    f"{BEST_EFFORT_ENTITY_REVIEW_PREFIX} source Host.FullName column "
                    f"`{full_name_column}` is provisionally represented by hosts.nameColumn "
                    f"`{candidate}`; confirm that this column is the intended host identifier. "
                    "The original value is also retained in customDetails when the query output "
                    "binding is available; this assumption does not prove entity parity"
                )
            elif entity_type == "Account" and identifier == "FullName" and source_fields.get(identifier) in (
                fields.get("upnColumn"), fields.get("nameColumn") if _valid_account(fields) else None,
            ):
                information.append(
                    f"Account.FullName `{source_fields[identifier]}` is retained by an equivalent account mapping"
                )
            else:
                if not defer_unmapped_entity_warnings:
                    warnings.append(
                        f"converter cannot map {entity_type}.{identifier} to a documented Custom Detection field; "
                        "this source identifier is not represented"
                    )
        if fields:
            counters[collection] = counters.get(collection, 0) + 1
            identifier = collection[:-1] if collection.endswith("s") else collection
            output.setdefault(collection, []).append(
                {"id": f"{identifier}{counters[collection]}", **fields}
            )
    if not output:
        inferred, inference_warnings = _infer_entities(columns)
        output.update(inferred)
        warnings.extend(inference_warnings)
    return output, warnings


def _techniques(values: list[str] | None) -> list[dict[str, Any]]:
    grouped: dict[str, set[str]] = {}
    for raw in values or []:
        value = str(raw).strip()
        if not value:
            continue
        base = value.split(".", 1)[0]
        grouped.setdefault(base, set())
        if "." in value:
            grouped[base].add(value)
    result = []
    for base, subtechniques in grouped.items():
        item: dict[str, Any] = {"technique": base}
        if subtechniques:
            item["subTechniques"] = sorted(subtechniques)
        result.append(item)
    return result


def _mitre_catalog() -> dict[str, set[str]]:
    """Reuse the Sentinel validator's base-technique compatibility, including for subtechniques."""
    text = MITRE_CATALOG_PATH.read_text(encoding="utf-8-sig")
    catalog = {
        tactic: set(re.findall(r'"(T\d{4})"', techniques))
        for tactic, techniques in re.findall(
            r'\{\s*Tactic\.(\w+),\s*new List<string>\(\)\s*\{([^}]*)\}', text
        )
        if tactic != "Unknown"
    }
    if not catalog or any(not techniques for techniques in catalog.values()):
        raise ValueError("MITRE compatibility catalog is missing or malformed")
    return catalog


def _classification_payload(
    tactics: Any, techniques: Any, override: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(tactics, list) or not all(isinstance(value, str) and value for value in tactics):
        return [], ["source tactics must be an array of nonempty tactic identifiers"], []
    unclassified = [{"tactic": tactic} for tactic in tactics]
    try:
        catalog = _mitre_catalog()
    except (OSError, ValueError) as exc:
        return unclassified, [f"Cannot resolve MITRE classification: {exc}"], []
    if not isinstance(techniques, list) or not all(
        isinstance(value, str) and re.fullmatch(r"T\d{4}(?:\.\d{3})?", value)
        for value in techniques
    ):
        return unclassified, ["source relevantTechniques must be an array of technique IDs (Tdddd or Tdddd.ddd)"], []
    for tactic in tactics:
        if tactic not in catalog:
            errors.append(f"unsupported source MITRE tactic: {tactic!r}")
    for technique in techniques:
        if not any(technique.split(".")[0] in catalog.get(tactic, set()) for tactic in tactics):
            errors.append(f"MITRE technique {technique!r} has no documented compatible source tactic")

    selected = override.get("tactic")
    selected_techniques = override.get("techniques")
    apply_override = False
    if "tactic" in override or "techniques" in override:
        if not isinstance(selected, str) or selected not in tactics or selected not in catalog:
            errors.append("configured tactic override must name an existing supported source tactic; source tactics cannot be removed or replaced")
        elif not isinstance(selected_techniques, list) or not all(
            isinstance(value, str) and re.fullmatch(r"T\d{4}(?:\.\d{3})?", value)
            and value.split(".")[0] in catalog[selected]
            for value in selected_techniques
        ):
            errors.append(f"configured techniques override must contain documented compatible technique IDs for {selected}")
        else:
            apply_override = True
            warnings.append(
                f"Legacy tactic override updates techniques only for {selected}; "
                "all source tactics and their order are preserved, not narrowed or reordered."
            )
    payload = []
    for tactic in tactics:
        relevant = (
            selected_techniques if apply_override and tactic == selected else
            [value for value in techniques if value.split(".")[0] in catalog.get(tactic, set())]
        )
        item: dict[str, Any] = {"tactic": tactic}
        if relevant:
            item["techniques"] = _techniques(relevant)
        payload.append(item)
    return payload, errors, warnings


def _custom_detail_binding(query: str, column: str) -> str:
    facts = _linear_facts(query)
    if facts:
        _, columns, assignments = facts
        if columns is not None:
            return "available" if column in columns else "missing"
        if column in assignments:
            return "available"
    grouped = _linear_facts(query, allow_aggregation=True)
    if grouped and grouped[1] is not None and column in grouped[1]:
        return "available"
    parts = _pipeline_parts(query)
    if parts:
        tail = list(parts[1:])
        while tail and tail[-1] and tail[-1][0] == "where":
            tail.pop()
        if tail and tail[-1] and tail[-1][0] == "project":
            items = _expression_items(tail[-1][1:])
            if all(
                item and re.fullmatch(r"[A-Za-z_]\w*", item[0])
                and (len(item) == 1 or (len(item) >= 3 and item[1] == "="))
                for item in items
            ):
                return "available" if column in {item[0] for item in items} else "missing"
        if tail and tail[-1][:3] == ["project", "-", "away"]:
            removed = {
                token for token in tail[-1][3:]
                if re.fullmatch(r"[A-Za-z_]\w*", token)
            }
            if column in removed:
                return "missing"
        if tail and tail[-1][:3] == ["project", "-", "rename"]:
            items = _expression_items(tail[-1][3:])
            if any(
                len(item) >= 3 and item[1] == "=" and item[2] == column
                for item in items
            ):
                return "missing"
    tokens = _tokens(query)
    if any(
        tokens[index:index + 3] in (["project", "-", "away"], ["project", "-", "rename"])
        for index in range(len(tokens) - 2)
    ):
        return "unproven-destructive-projection"
    columns = projected_columns(query)
    if columns is not None and column not in columns and "*" not in tokens:
        return "missing"
    return "runtime-binding-pending"


def _entity_identifier_preserved(
    entity_type: str, identifier: str, column: str, source_fields: dict[str, str],
    mappings: dict[str, Any], query: str,
) -> bool:
    collection, identifiers = ENTITY_MAP.get(entity_type, ("", {}))
    candidates = mappings.get(collection) or []
    if not isinstance(candidates, list):
        return False
    candidates = [item for item in candidates if isinstance(item, dict)]
    target = identifiers.get(identifier)
    if target and any(item.get(target) == column for item in candidates):
        return True
    if entity_type == "Host" and identifier == "FullName":
        return any(_host_full_name_preserved(source_fields, item, query) for item in candidates)
    if entity_type == "Account":
        if identifier == "FullName":
            return any(
                item.get("upnColumn") == column or
                (item.get("nameColumn") == column and _valid_account(item))
                for item in candidates
            )
        if identifier == "Name" and column.lower() in ACCOUNT_UPN_ALIASES:
            return any(item.get("upnColumn") == column for item in candidates)
    if entity_type == "FileHash" and identifier in {"Algorithm", "Value"}:
        facts = _linear_facts(query)
        algorithm = facts[2].get(source_fields.get("Algorithm", "")) if facts else None
        target = {"'SHA1'": "sha1Column", "'SHA256'": "sha256Column"}.get(
            algorithm[0].upper() if algorithm and len(algorithm) == 1 else ""
        )
        return bool(target) and any(
            item.get(target) == source_fields.get("Value") for item in candidates
        )
    return False


def _unproven_custom_detail_warning(key: str, column: str) -> str:
    return (
        f"customDetails {key!r} column `{column}` has an unproven output binding "
        "after a destructive projection; the explicit binding is retained, but "
        "static analysis cannot establish its output and runtime output-schema "
        "verification is required"
    )


def _supplemental_custom_details(
    doc: dict[str, Any], override: dict[str, Any], mappings: dict[str, Any],
    query: str, column_mappings: dict[str, str],
) -> tuple[Any, list[dict[str, Any]], list[str], list[str], list[str]]:
    details: dict[str, Any] = {}
    evidence: list[dict[str, Any]] = []
    warnings: list[str] = []
    information: list[str] = []
    errors: list[str] = []
    for origin, container in (("source", doc), ("configured override", override)):
        if "customDetails" not in container:
            continue
        value = container["customDetails"]
        if not isinstance(value, dict):
            errors.append(f"{origin} customDetails must be an object of nonempty key-to-query-column strings")
            if origin == "source":
                return deepcopy(value), evidence, warnings, information, errors
            continue
        for key, source_column in value.items():
            if not isinstance(key, str) or not key or not isinstance(source_column, str) or not source_column:
                errors.append(f"{origin} customDetails contains an invalid key or query-column value: {key!r}")
                column = deepcopy(source_column)
            else:
                column = column_mappings.get(source_column, source_column)
            if key in details and details[key] != column:
                errors.append(f"customDetails key {key!r} conflicts with the existing source binding; no value was overwritten")
            else:
                details[key] = column
    for key, column in details.items():
        if not isinstance(column, str) or not column:
            continue
        binding = _custom_detail_binding(query, column)
        if binding == "missing":
            errors.append(
                f"customDetails {key!r} column `{column}` is missing from the final query output; "
                "explicit binding retained for correction"
            )
        elif binding == "unproven-destructive-projection":
            warnings.append(_unproven_custom_detail_warning(key, column))
        elif binding != "available":
            warnings.append(f"customDetails {key!r} column `{column}` requires runtime output-schema binding verification")

    for index, entity in enumerate(doc.get("entityMappings") or [], start=1):
        entity_type = str(entity.get("entityType") or "UnknownEntity")
        source_fields = {
            str(field.get("identifier") or ""): column_mappings.get(
                str(field.get("columnName") or ""), str(field.get("columnName") or ""),
            )
            for field in entity.get("fieldMappings") or []
        }
        for field in entity.get("fieldMappings") or []:
            identifier = str(field.get("identifier") or "")
            source_column = str(field.get("columnName") or "")
            column = column_mappings.get(source_column, source_column)
            if not identifier or not column:
                continue
            if _entity_identifier_preserved(entity_type, identifier, column, source_fields, mappings, query):
                continue
            binding = _custom_detail_binding(query, column)
            record: dict[str, Any] = {
                "entityType": entity_type, "entityIndex": index, "identifier": identifier,
                "sourceColumn": source_column, "column": column, "status": binding,
            }
            evidence.append(record)
            if binding == "missing":
                record["status"] = "not-preserved"
                record["reason"] = binding
                warnings.append(
                    f"{entity_type}.{identifier} value is not preserved: column `{column}` "
                    "is missing from the final query output. No invalid customDetails binding was added and KQL was not rewritten"
                )
                if entity_type == "Host" and identifier == "FullName":
                    warnings.append(
                        f"{BEST_EFFORT_ENTITY_REVIEW_PREFIX} Host.FullName column `{column}` "
                        "is not available in the query output, so no supported host-name "
                        "mapping or supplemental customDetails binding can be made"
                    )
                continue
            if binding == "unproven-destructive-projection":
                record["reason"] = binding
                warnings.append(
                    f"{entity_type}.{identifier} output column `{column}` cannot be proven "
                    "after a destructive projection; no supplemental customDetails binding "
                    "was added and KQL was not rewritten. Runtime output-schema verification is required"
                )
                continue
            key = next((key for key, value in details.items() if value == column and isinstance(key, str)), None)
            if key is None:
                base = re.sub(r"[^A-Za-z0-9]", "", entity_type + identifier) or "EntityDetail"
                key = base
                suffix = 2
                while key in details:
                    key = f"{base}_{suffix}"
                    suffix += 1
                details[key] = column
            record["customDetailKey"] = key
            if binding == "runtime-binding-pending":
                warnings.append(
                    f"{entity_type}.{identifier} value is retained as customDetails.{key} from query column "
                    f"`{column}`, but its target output binding requires runtime-schema verification; "
                    "custom details do not restore entity identity or correlation"
                )
                warnings.append(
                    f"Supplemental customDetails.{key} column `{column}` requires runtime output-schema binding verification"
                )
            else:
                information.append(
                    f"{entity_type}.{identifier} mismatch is informational because its original value is "
                    f"preserved as customDetails.{key} from query column `{column}`; supplemental details "
                    "do not restore entity identity, correlation, or alert parity"
                )
    if len(details) > 20:
        errors.append(
            f"customDetails contains {len(details)} pairs, exceeding the documented 20-pair limit; "
            "no details were truncated. Review the source and supplemental details"
        )
    if sum(len(key.encode("utf-8")) for key in details if isinstance(key, str)) > 4096:
        errors.append("customDetails keys alone exceed the documented combined 4 KB per-alert limit; no keys were truncated")
    if details:
        warnings.append(
            "Custom-detail values must remain within the documented combined 4 KB per-alert limit; "
            "runtime values are unverified and the service drops all custom details if exceeded"
        )
    return details, evidence, warnings, information, errors


def custom_detail_schema_errors(document: dict[str, Any], schema: list[dict[str, Any]]) -> list[str]:
    alert = ((document.get("properties") or {}).get("detectionAction") or {}).get("alertTemplate") or {}
    details = alert.get("customDetails") or {}
    if not isinstance(details, dict):
        return ["customDetails must be an object"]
    if not isinstance(schema, list):
        return ["customDetails binding verification requires a runtime output schema"]
    columns = {
        str(item.get("name") or item.get("Name") or "")
        for item in schema if isinstance(item, dict)
    }
    return [
        f"customDetails {key!r} column `{column}` is absent from the runtime output schema"
        for key, column in details.items() if not isinstance(column, str) or column not in columns
    ]


def custom_detail_binding_warnings(document: dict[str, Any]) -> list[str]:
    properties = document.get("properties") or {}
    query = ((properties.get("queryCondition") or {}).get("queryText") or "")
    alert = ((properties.get("detectionAction") or {}).get("alertTemplate") or {})
    details = alert.get("customDetails")
    if not isinstance(details, dict):
        return []
    return [
        _unproven_custom_detail_warning(key, column)
        for key, column in details.items()
        if isinstance(key, str)
        and isinstance(column, str)
        and _custom_detail_binding(query, column) == "unproven-destructive-projection"
    ]


def _extract_raw_yaml_version(raw_text: str, doc: dict[str, Any]) -> str:
    """Preserve exact source YAML version lexical text (e.g., 1.0 vs 1.0.0)."""
    for line in (raw_text or "").splitlines():
        match = re.match(r"^version\s*:\s*(.+?)\s*$", line)
        if not match:
            continue
        raw_val = match.group(1).strip()
        if not raw_val or raw_val.startswith("#"):
            continue
        if (raw_val.startswith('"') and raw_val.endswith('"')) or (
            raw_val.startswith("'") and raw_val.endswith("'")
        ):
            return raw_val[1:-1]
        raw_val = re.sub(r"\s+#.*$", "", raw_val).strip()
        if raw_val:
            return raw_val
    return str(doc.get("version") or "")


def _version_tuple(version: str) -> tuple[int, int, int]:
    parts = str(version).split(".")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        return int(parts[0]), int(parts[1]), int(parts[2])
    return (0, 0, 0)


def _solution_release_version(solution_root: Path, config: dict[str, Any] | None = None) -> str:
    """Resolve the solution release version in [3.1.0, 4.0.0) or default to INITIAL_XDR_VERSION."""
    if isinstance(config, dict):
        for key in ("targetVersion", "version"):
            candidate = config.get(key)
            if isinstance(candidate, str) and re.fullmatch(XDR_VERSION_PATTERN, candidate.strip()):
                return candidate.strip()
    try:
        from solution_manager.core.artifacts import current_workflow_state

        state = current_workflow_state(solution_root)
        if isinstance(state, dict):
            target_ver = state.get("targetVersion")
            if isinstance(target_ver, str) and re.fullmatch(XDR_VERSION_PATTERN, target_ver.strip()):
                return target_ver.strip()
    except Exception:
        pass
    candidates: list[str] = []
    data_dir = solution_root / "Data"
    if data_dir.is_dir():
        for data_path in sorted(data_dir.glob("Solution_*.json")):
            try:
                payload = json.loads(data_path.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError):
                continue
            if isinstance(payload, dict):
                ver = payload.get("Version") or payload.get("version")
                if isinstance(ver, str) and re.fullmatch(XDR_VERSION_PATTERN, ver.strip()):
                    candidates.append(ver.strip())
    meta_path = solution_root / "SolutionMetadata.json"
    if meta_path.is_file():
        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            payload = None
        if isinstance(payload, dict):
            ver = payload.get("version") or payload.get("Version")
            if isinstance(ver, str) and re.fullmatch(XDR_VERSION_PATTERN, ver.strip()):
                candidates.append(ver.strip())
    if candidates:
        return max(candidates, key=_version_tuple)
    return INITIAL_XDR_VERSION


def build_xdr_document(source: Path, solution_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    with source.open(encoding="utf-8-sig") as handle:
        raw_source_text = handle.read()
    doc = yaml.safe_load(raw_source_text) or {}
    if not isinstance(doc, dict):
        raise ValueError(f"analytic rule must contain a YAML object: {source}")

    source_query = str(doc.get("query") or "")
    extra_referenced_columns: set[str] = set()
    for entity in doc.get("entityMappings") or []:
        if isinstance(entity, dict):
            for fm in entity.get("fieldMappings") or []:
                if isinstance(fm, dict) and fm.get("columnName"):
                    extra_referenced_columns.add(str(fm["columnName"]))
    custom_details_raw = doc.get("customDetails")
    if isinstance(custom_details_raw, dict):
        for val in custom_details_raw.values():
            if isinstance(val, str) and val:
                extra_referenced_columns.add(val)

    converted_query, query_warnings, errors = convert_query(
        source_query,
        config,
        extra_referenced_columns=extra_referenced_columns,
    )
    provenance_notes: list[str] = [
        w for w in query_warnings
        if w.startswith((
            "security_alert_migrated_to_alert_info",
            "security_incident_migrated_to_alert_info",
            "nrt_cosmetic_summarize_rewritten",
            "nrt_behavioral_summarize_fallback_pt1h",
        ))
    ]
    non_provenance_query_warnings = [
        w for w in query_warnings if w not in provenance_notes
    ]
    if "requiredDataConnectors" in doc:
        with XDR_SCHEMA_PATH.open(encoding="utf-8") as handle:
            connector_schema = json.load(handle)["properties"]["requiredDataConnectors"]
        errors.extend(
            f"requiredDataConnectors{''.join(f'[{part!r}]' for part in error.path)}: {error.message}"
            for error in Draft202012Validator(connector_schema).iter_errors(doc["requiredDataConnectors"])
        )
    warnings = list(query_warnings)
    informational: list[str] = list(provenance_notes)
    review_reasons = list(non_provenance_query_warnings)
    try:
        converted_query, parser_warnings = normalize_parser_bindings(converted_query, solution_root)
        warnings.extend(parser_warnings)
    except ValueError as exc:
        errors.append(str(exc))
    source_id = str(doc.get("id") or "")
    rule_override = (config.get("ruleOverrides") or {}).get(source_id) or {}
    is_nrt = str(doc.get("kind") or "").lower() == "nrt"
    override_frequency = rule_override.get("frequency") if isinstance(rule_override, dict) else None
    nrt_behavioral_fallback = False
    schedule_payload: dict[str, Any]
    if is_nrt and not override_frequency and not doc.get("queryFrequency"):
        frequency = "PT0S"
        is_legacy_synthetic_nrt = (
            source_query.strip()
            == "DeviceEvents | summarize Count = count() by AccountUpn, IPAddress, Timestamp"
        )
        if not is_legacy_synthetic_nrt:
            rewritten_nrt, was_rewritten, nrt_rewrite_notes = rewrite_cosmetic_nrt_summarize(
                converted_query
            )
            if was_rewritten:
                converted_query = rewritten_nrt
                warnings.extend(nrt_rewrite_notes)
                informational.extend(nrt_rewrite_notes)
                provenance_notes.extend(nrt_rewrite_notes)
            elif re.search(r"\b(?:summarize|make-series)\b", converted_query, re.IGNORECASE):
                nrt_behavioral_fallback = True
                frequency = "PT1H"
                fallback_notes = [
                    "nrt_behavioral_summarize_fallback_pt1h",
                    (
                        "nrt_behavioral_summarize_fallback_pt1h: Source NRT rule uses a behavioral "
                        "summarize aggregation with threshold/grouping semantics not supported in "
                        "Continuous (PT0S) mode; automatically fell back schedule frequency to PT1H "
                        "(queryPeriod: PT4H)."
                    ),
                ]
                warnings.extend(fallback_notes)
                informational.extend(fallback_notes)
                provenance_notes.extend(fallback_notes)
        if nrt_behavioral_fallback:
            frequency_warning = None
        else:
            nrt_eligible, nrt_reasons = _assess_nrt_eligibility(source_query, converted_query)
            frequency_warning = (
                None
                if nrt_eligible
                else (
                    "source NRT rule is not eligible for Continuous (NRT) execution in Defender XDR "
                    f"({'; '.join(nrt_reasons)}); review schedule or configure a scheduled frequency override"
                )
            )
    else:
        raw_freq = override_frequency if override_frequency is not None else doc.get("queryFrequency")
        frequency, frequency_warning = iso_duration(raw_freq or ("PT1H" if is_nrt else None))
    if frequency_warning:
        warnings.append(frequency_warning)
        review_reasons.append(frequency_warning)
    query_period = str(doc.get("queryPeriod") or "").strip()
    if nrt_behavioral_fallback:
        schedule_payload = {"frequency": "PT1H", "queryPeriod": "PT4H"}
        event_window = {
            "status": "nrt-behavioral-summarize-fallback",
            "appliedDefault": "nrt-behavioral-summarize-to-pt1h-pt4h",
            "targetFrequency": "PT1H",
            "effectiveLookback": "PT4H",
            "xdrServiceWindowSeconds": 14400,
        }
        event_window_review = None
    else:
        schedule_payload = {"frequency": frequency}
        converted_query, event_window, event_window_review = constrain_event_window(
            doc, source_query, converted_query, frequency,
        )
    if event_window_review:
        review_reasons.append(event_window_review)
    review_scope = {
        "sourceDocumentSha256": hashlib.sha256(
            yaml.safe_dump(doc, sort_keys=True, allow_unicode=True).encode("utf-8")
        ).hexdigest(),
        "targetQuerySha256": hashlib.sha256(converted_query.encode("utf-8")).hexdigest(),
    }
    if isinstance(event_window, dict) and event_window.get("status") == "default-native-lookback":
        event_window["sourceDocumentSha256"] = review_scope["sourceDocumentSha256"]
        event_window["targetQuerySha256"] = review_scope["targetQuerySha256"]
    if nrt_behavioral_fallback:
        schedule_warnings, schedule_information = [], [
            f"Schedule assessment: source kind=NRT with behavioral summarize; fell back to target frequency=PT1H, queryPeriod=PT4H. See {SCHEDULE_REFERENCE}"
        ]
    else:
        schedule_warnings, schedule_information = assess_schedule(
            doc, source_query, converted_query, frequency,
        )
    warnings.extend(schedule_warnings)
    informational.extend(schedule_information)

    security_alert_migrated = any(
        n.startswith(("security_alert_migrated_to_alert_info", "security_incident_migrated_to_alert_info"))
        for n in provenance_notes
    )
    entity_information: list[str] = []
    column_mappings = (
        {}
        if (security_alert_migrated or query_has_ambiguous_table_scope(source_query))
        else query_column_renames(converted_query)
    )
    configured_mappings, _ = configured_column_renames(source_query, config)
    column_mappings.update(configured_mappings)
    if security_alert_migrated:
        for src_col, tgt_col in {
            **SECURITY_ALERT_DIRECT_COLUMN_MAP,
            **SECURITY_INCIDENT_DIRECT_COLUMN_MAP,
        }.items():
            column_mappings.setdefault(src_col, src_col if src_col in _tokens(converted_query) else tgt_col)
    mappings, mapping_warnings = convert_entities(
        doc,
        converted_query,
        column_mappings,
        informational=entity_information,
        defer_unmapped_entity_warnings=True,
    )
    if security_alert_migrated and not REQUIRED_ASSET_COLLECTIONS.intersection(mappings):
        converted_tokens = set(_tokens(converted_query))
        if "DeviceName" in converted_tokens:
            mappings.setdefault("hosts", [{"id": "host1", "nameColumn": "DeviceName"}])
        elif "AccountUpn" in converted_tokens:
            mappings.setdefault("accounts", [{"id": "account1", "upnColumn": "AccountUpn"}])
        elif "RemoteIP" in converted_tokens:
            mappings.setdefault("ips", [{"id": "ip1", "addressColumn": "RemoteIP"}])
        else:
            mappings.setdefault("hosts", [{"id": "host1", "nameColumn": "Title"}])
        mapping_warnings = [
            w for w in mapping_warnings
            if w != "No valid source mapping survived; inferred entities from projected columns"
            and w != "Account mapping is incomplete and was removed"
        ]
    configured_entity_mappings = rule_override.get("entityMappings")
    if configured_entity_mappings is not None:
        if not isinstance(configured_entity_mappings, dict):
            errors.append(
                "configured ruleOverrides entityMappings must contain an object"
            )
        else:
            mappings = configured_entity_mappings
            mapping_warnings.append(
                "entity mappings were resolved by the configured per-rule override"
            )
            if any(
                warning.startswith(BEST_EFFORT_ENTITY_REVIEW_PREFIX)
                for warning in mapping_warnings
            ):
                mapping_warnings = [
                    warning for warning in mapping_warnings
                    if not warning.startswith(BEST_EFFORT_ENTITY_REVIEW_PREFIX)
                ]
                mapping_warnings.append(
                    f"{BEST_EFFORT_ENTITY_REVIEW_PREFIX} the configured per-rule "
                    "entityMappings override is retained; confirm its Host mapping "
                    "against the source Host.FullName value, which is preserved in "
                    "customDetails when its query output binding is available"
                )
    else:
        informational.extend(entity_information)
    entity_review_reasons = [
        warning
        for warning in mapping_warnings
        if warning.startswith(NONBLOCKING_ENTITY_REVIEW_PREFIXES)
        or "genuine content SHA-1/SHA-256 is required" in warning
    ]
    if any(reason.startswith(ENTITY_CONFIRMATION_PREFIX) for reason in entity_review_reasons) and REQUIRED_ASSET_COLLECTIONS.intersection(
        mappings
    ) - {"accounts"}:
        mappings.pop("accounts", None)
        mapping_warnings = [
            warning
            for warning in mapping_warnings
            if not warning.startswith(ENTITY_CONFIRMATION_PREFIX)
        ]
        mapping_warnings.append(
            "Unconfirmed generic Account.Name mapping was omitted because another "
            "required Host, Mailbox, or IP asset is available"
        )
        entity_review_reasons = [
            reason for reason in entity_review_reasons
            if not reason.startswith(ENTITY_CONFIRMATION_PREFIX)
        ]
    warnings.extend(mapping_warnings)
    review_reasons.extend(entity_review_reasons)
    custom_details, supplemental_evidence, detail_warnings, detail_information, detail_errors = _supplemental_custom_details(
        doc, rule_override, mappings, converted_query, column_mappings,
    )
    warnings.extend(detail_warnings)
    informational.extend(detail_information)
    errors.extend(detail_errors)
    review_reasons.extend(
        warning for warning in detail_warnings
        if warning.startswith(BEST_EFFORT_ENTITY_REVIEW_PREFIX)
    )

    source_tactics = deepcopy(doc.get("tactics", []))
    source_relevant = deepcopy(doc.get("relevantTechniques", []))
    tactic_payload, classification_errors, classification_warnings = _classification_payload(
        source_tactics, source_relevant, rule_override,
    )
    errors.extend(classification_errors)
    warnings.extend(classification_warnings)
    if len(tactic_payload) > 1:
        informational.append(
            "All source MITRE tactics are preserved in source order in authored YAML. "
            "V3.1 ARM packaging carries only the first tactic and its compatible techniques; "
            "this classification loss is not validated parity. Direct Graph deployment requires a single tactic."
        )
    if not mappings:
        errors.append("no supported entity mappings were produced")
    elif not REQUIRED_ASSET_COLLECTIONS.intersection(mappings):
        errors.append("a Host, Account, Mailbox, or IP mapping is required")

    if not source_id:
        errors.append("source analytic rule has no id")
    elif not re.fullmatch(SOURCE_ID_PATTERN, source_id):
        errors.append("source analytic rule id must be a full hyphenated GUID")

    accepted_review_reasons: set[str] = set()
    review_decisions = rule_override.get("reviewDecisions") or []
    if "acceptedReviewReasons" in rule_override:
        errors.append(
            "acceptedReviewReasons is unscoped and no longer clears review findings; "
            "use hash-scoped reviewDecisions"
        )
    if not isinstance(review_decisions, list):
        errors.append("configured reviewDecisions must be an array of hash-scoped accept/reject decisions")
        review_decisions = []
    recorded_review_decisions: list[dict[str, Any]] = []
    seen_review_decisions: set[str] = set()
    for decision in review_decisions:
        if not isinstance(decision, dict):
            errors.append("each reviewDecision must be an object")
            continue
        reason = decision.get("reason")
        choice = decision.get("decision")
        source_hash = decision.get("sourceDocumentSha256")
        query_hash = decision.get("targetQuerySha256")
        if not isinstance(reason, str) or not reason or choice not in {"accepted", "rejected"}:
            errors.append("each reviewDecision requires an exact reason and decision accepted or rejected")
            continue
        if reason in seen_review_decisions:
            errors.append(f"duplicate reviewDecision for {reason!r}")
            continue
        seen_review_decisions.add(reason)
        if not (
            isinstance(source_hash, str) and re.fullmatch(r"[0-9a-f]{64}", source_hash)
            and isinstance(query_hash, str) and re.fullmatch(r"[0-9a-f]{64}", query_hash)
        ):
            errors.append(f"reviewDecision for {reason!r} requires source-document and target-query SHA-256 hashes")
            continue
        if source_hash != review_scope["sourceDocumentSha256"] or query_hash != review_scope["targetQuerySha256"]:
            errors.append(f"reviewDecision for {reason!r} is stale; source document or target query hash changed")
            continue
        is_legacy_hourly_lookback_decision = (
            isinstance(event_window, dict)
            and event_window.get("status") == "default-native-lookback"
            and reason.startswith("Original Sentinel lookback is shorter than the native XDR service window")
        )
        if reason not in review_reasons and not is_legacy_hourly_lookback_decision:
            errors.append(f"reviewDecision reason does not match a current review finding: {reason}")
            continue
        recorded_review_decisions.append({
            "reason": reason,
            "decision": choice,
            "sourceDocumentSha256": source_hash,
            "targetQuerySha256": query_hash,
        })
        if choice == "accepted":
            accepted_review_reasons.add(reason)
    review_reasons = [
        reason for reason in review_reasons if reason not in accepted_review_reasons
    ]

    display_name = str(doc.get("name") or source.stem)
    detection_id = f"xdr-{source_id}"
    severity = str(doc.get("severity") or "Medium").lower()
    if severity not in SUPPORTED_SEVERITIES:
        warnings.append(f"unsupported severity {severity!r}; changed to medium")
        severity = "medium"

    alert: dict[str, Any] = {
        "title": display_name[:120],
        "description": str(doc.get("description") or display_name).strip()[:600],
        "severity": severity,
        "entityMappings": mappings,
    }
    if tactic_payload:
        alert["tactics"] = tactic_payload
    if custom_details or "customDetails" in doc or "customDetails" in rule_override:
        alert["customDetails"] = custom_details

    blocking_review_reasons = [
        reason
        for reason in review_reasons
        if not reason.startswith(NONBLOCKING_ENTITY_REVIEW_PREFIXES)
    ]
    status = "needsReview" if errors or blocking_review_reasons else "converted"
    relative_source = source.relative_to(solution_root).as_posix()
    effective_table_mappings = dict(config.get("tableMappings") or {})
    if security_alert_migrated:
        effective_table_mappings.setdefault("SecurityAlert", "AlertInfo")
        effective_table_mappings.setdefault("SecurityIncident", "AlertInfo")
    dependencies = dependency_plan(
        source_query,
        target_query=converted_query,
        connectors=doc.get("requiredDataConnectors"),
        table_mappings=effective_table_mappings,
    )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "version": _solution_release_version(solution_root, config),
        "kind": "CustomDetection",
        "resourceType": "Microsoft.Security/detectionRules",
        "apiVersion": DETECTION_API_VERSION,
        **(
            {"requiredDataConnectors": deepcopy(doc["requiredDataConnectors"])}
            if "requiredDataConnectors" in doc
            else {}
        ),
        "contentProvenance": {
            "requiredWorkloads": dependencies["requiredWorkloads"],
            "requiredDataConnectors": dependencies["requiredDataConnectors"],
            "dependencyReviewRequired": dependencies["reviewRequired"],
            "source": {
                "platform": "Microsoft Sentinel",
                "kind": "AnalyticsRule",
                "id": source_id,
                "path": relative_source,
                "version": _extract_raw_yaml_version(raw_source_text, doc),
                "querySha256": hashlib.sha256(source_query.encode("utf-8")).hexdigest(),
                "schedule": {
                    "queryFrequency": str(doc.get("queryFrequency") or ""),
                    "queryPeriod": query_period,
                },
            },
            "conversion": {
                "tool": "sentinel-to-xdr-migration",
                "version": __version__,
                "status": status,
                "reviewRequired": bool(errors or review_reasons),
                "reviewReasons": review_reasons,
                "requiredWorkloads": ["sentinel"],
                "warnings": warnings,
                "informational": informational,
                **({"notes": provenance_notes} if provenance_notes else {}),
                "errors": errors,
                "originalTactics": source_tactics,
                "originalTechniques": source_relevant,
                "reviewScope": review_scope,
                **({"reviewDecisions": recorded_review_decisions} if recorded_review_decisions else {}),
                **({"eventTimeWindow": event_window} if event_window else {}),
                **({"supplementalEntityDetails": supplemental_evidence} if supplemental_evidence else {}),
                **(
                    {"acceptedReviewReasons": sorted(accepted_review_reasons)}
                    if accepted_review_reasons
                    else {}
                ),
            },
        },
        "properties": {
            "id": detection_id,
            "displayName": display_name[:120],
            "status": "disabled",
            "queryCondition": {"queryText": converted_query},
            "schedule": schedule_payload,
            "detectionAction": {"alertTemplate": alert},
        },
    }


def xdr_version_error(version: Any) -> str | None:
    if isinstance(version, str) and re.fullmatch(XDR_VERSION_PATTERN, version):
        return None
    return (
        f"XDR top-level version {version!r} must be a major.minor.patch release "
        ">= 3.1.0 and < 4.0.0. For older files without version, reconvert with "
        "--overwrite (initial version 3.1.0), or explicitly author the XDR version. "
        "Do not change contentProvenance.source.version."
    )


def is_sentinel_derived(document: dict[str, Any]) -> bool:
    provenance = document.get("contentProvenance") or {}
    source = provenance.get("source") or {}
    conversion = provenance.get("conversion") or {}
    return (
        source.get("platform") == "Microsoft Sentinel"
        and source.get("kind") == "AnalyticsRule"
    ) or conversion.get("tool") == "sentinel-to-xdr-migration"


def _existing_identity_error(
    document: Any, source_id: str, source_path: str, source_name: str,
) -> str | None:
    if not isinstance(document, dict):
        return "existing output is not an XDR document; resolve the output identity conflict"
    provenance = document.get("contentProvenance") or {}
    if not isinstance(provenance, dict):
        return "existing output has malformed provenance; resolve the output identity conflict"
    source = provenance.get("source") or {}
    conversion = provenance.get("conversion") or {}
    properties = document.get("properties") or {}
    if not all(isinstance(value, dict) for value in (source, conversion, properties)):
        return "existing output has malformed identity fields; resolve the output identity conflict"
    if (
        document.get("kind") != "CustomDetection"
        or document.get("resourceType") != "Microsoft.Security/detectionRules"
        or source.get("platform") != "Microsoft Sentinel"
        or source.get("kind") != "AnalyticsRule"
        or source.get("id") != source_id
        or str(source.get("path") or "").replace("\\", "/") != source_path
    ):
        return (
            "existing XDR output belongs to a different source rule or has conflicting "
            "provenance; resolve the output identity conflict before reconverting"
        )
    detection_id = properties.get("id")
    if isinstance(detection_id, str) and detection_id.casefold() in {
        source_id.casefold(),
        f"xdr-{source_id}".casefold(),
    }:
        return None
    legacy_ids = {
        f"xdr-{slugify(name)}-{source_id[:8]}"
        for name in (str(properties.get("displayName") or ""), source_name)
        if name
    }
    if (
        conversion.get("tool") == "sentinel-to-xdr-migration"
        and isinstance(detection_id, str)
        and detection_id in legacy_ids
    ):
        return None
    return (
        f"existing Custom Detection id {detection_id!r} is not the source GUID, its "
        "canonical xdr-<GUID> ID, or a generated legacy name ID; reconcile this custom identity before "
        "reconversion, even with --overwrite"
    )


def validate_document(document: dict[str, Any]) -> list[str]:
    with XDR_SCHEMA_PATH.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    errors = dependency_validation_errors(document) + [
        f"schema: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(document)
    ]
    version_error = xdr_version_error(document.get("version"))
    if version_error:
        errors.append(version_error)
    if document.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION}")
    if document.get("kind") != "CustomDetection":
        errors.append("kind must be CustomDetection")
    if document.get("resourceType") != "Microsoft.Security/detectionRules":
        errors.append("resourceType must be Microsoft.Security/detectionRules")
    provenance = document.get("contentProvenance") or {}
    source = provenance.get("source") or {}
    conversion = provenance.get("conversion") or {}
    properties = document.get("properties") or {}
    detection_id = properties.get("id")
    id_is_guid = isinstance(detection_id, str) and re.fullmatch(SOURCE_ID_PATTERN, detection_id)
    id_is_prefixed_guid = isinstance(detection_id, str) and re.fullmatch(
        PREFIXED_SOURCE_ID_PATTERN, detection_id,
    )
    if not id_is_guid and not id_is_prefixed_guid and not (
        isinstance(detection_id, str) and re.fullmatch(GRAPH_DETECTION_ID_PATTERN, detection_id)
    ):
        errors.append(
            "properties.id must be a Graph-compatible identifier beginning with a letter "
            "and containing at most 100 letters, digits, dashes, or underscores"
        )
    if is_sentinel_derived(document):
        if not isinstance(source.get("id"), str) or not re.fullmatch(SOURCE_ID_PATTERN, source["id"]):
            errors.append("contentProvenance.source.id must be a full hyphenated Sentinel template GUID")
        expected_id = f"xdr-{source.get('id')}"
        if detection_id != expected_id:
            errors.append(
                "Sentinel-derived properties.id must be the canonical xdr- prefix plus "
                "contentProvenance.source.id; reconvert with --overwrite to update local "
                "artifacts only, not deployed rule migration"
            )
    for field in ("platform", "kind", "id", "path", "querySha256"):
        if not source.get(field):
            errors.append(f"contentProvenance.source.{field} is required")
    if conversion.get("status") not in {"converted", "needsReview"}:
        errors.append("contentProvenance.conversion.status is invalid")
    if conversion.get("errors"):
        errors.extend(f"conversion: {value}" for value in conversion["errors"])
    if properties.get("status") != "disabled":
        errors.append("properties.status must be disabled")
    query = ((properties.get("queryCondition") or {}).get("queryText") or "")
    if not query:
        errors.append("properties.queryCondition.queryText is required")
    schedule = properties.get("schedule") or {}
    if isinstance(schedule, dict) and schedule.get("frequency") in {"PT0S", "NRT"}:
        nrt_eligible, nrt_reasons = _assess_nrt_eligibility(query, query)
        if not nrt_eligible and conversion.get("status") != "needsReview":
            errors.extend(f"NRT schedule: {reason}" for reason in nrt_reasons)
    alert = ((properties.get("detectionAction") or {}).get("alertTemplate") or {})
    mappings = alert.get("entityMappings") or {}
    if isinstance(mappings, dict):
        for collection_name in ("files", "processes"):
            items = mappings.get(collection_name)
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                if collection_name == "processes" and not (
                    item.get("sha1Column") or item.get("sha256Column")
                ):
                    errors.append(
                        "entityMappings.processes requires a genuine sha1Column or sha256Column content hash; "
                        "filename-only bindings are not supported"
                    )
                for hash_field in ("sha1Column", "sha256Column"):
                    col = item.get(hash_field)
                    if isinstance(col, str) and col:
                        bad_reason = _is_non_hash_or_synthetic_hash_column(query, col)
                        if bad_reason:
                            errors.append(
                                f"entityMappings.{collection_name}.{hash_field} column `{col}` is a "
                                f"{bad_reason}; a genuine content SHA-1/SHA-256 is required"
                            )
    custom_details = alert.get("customDetails")
    if isinstance(custom_details, dict):
        if sum(len(key.encode("utf-8")) for key in custom_details if isinstance(key, str)) > 4096:
            errors.append("customDetails keys alone exceed the documented combined 4 KB per-alert limit")
        for key, column in custom_details.items():
            if isinstance(column, str) and _custom_detail_binding(query, column) == "missing":
                errors.append(
                    f"customDetails {key!r} column `{column}` is missing from the final query output"
                )
    if not mappings:
        errors.append("alertTemplate.entityMappings is required")
    if not REQUIRED_ASSET_COLLECTIONS.intersection(mappings):
        errors.append("at least one Host, Account, Mailbox, or IP mapping is required")
    tactics = alert.get("tactics") or []
    if isinstance(tactics, list) and tactics:
        try:
            catalog = _mitre_catalog()
        except (OSError, ValueError) as exc:
            errors.append(f"Cannot validate MITRE classification: {exc}")
        else:
            for item in tactics:
                if not isinstance(item, dict):
                    continue
                tactic = item.get("tactic")
                if not isinstance(tactic, str) or tactic not in catalog:
                    errors.append(f"unsupported MITRE tactic: {tactic!r}")
                    continue
                technique_items = item.get("techniques") or []
                if not isinstance(technique_items, list):
                    continue
                for technique in technique_items:
                    if not isinstance(technique, dict):
                        continue
                    base = technique.get("technique")
                    if not isinstance(base, str) or base not in catalog[tactic]:
                        errors.append(f"MITRE technique {base!r} is not documented for tactic {tactic}")
                    subtechniques = technique.get("subTechniques") or []
                    if not isinstance(subtechniques, list):
                        continue
                    for sub in subtechniques:
                        if not isinstance(sub, str) or not re.fullmatch(r"T\d{4}\.\d{3}", sub) or sub.split(".")[0] != base:
                            errors.append(f"MITRE subtechnique {sub!r} must belong to technique {base!r}")
    return errors


def convert_solution(
    solution: str | Path,
    *,
    overwrite: bool = False,
    config_path: str | Path | None = None,
    rule_id: str | None = None,
) -> dict[str, Any]:
    root, analytic, output = solution_paths(solution)
    sources = analytic_rule_files(root)
    existing_outputs = xdr_detection_files(output)
    existing_by_source: dict[str, list[Path]] = {}
    existing_by_id: dict[str, list[Path]] = {}
    existing_documents: dict[Path, Any] = {}
    identified_outputs: set[Path] = set()
    for path in existing_outputs:
        try:
            existing = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
            existing_documents[path] = existing
            provenance = (existing.get("contentProvenance") or {}).get("source") or {}
            detection_id = str((existing.get("properties") or {}).get("id") or "")
            if detection_id:
                existing_by_id.setdefault(detection_id.casefold(), []).append(path)
            for key in (str(provenance.get("id") or "").casefold(), str(provenance.get("path") or "").replace("\\", "/")):
                if key:
                    existing_by_source.setdefault(key, []).append(path)
                    identified_outputs.add(path)
        except (AttributeError, OSError, yaml.YAMLError):
            continue
    config = load_config(output, config_path)
    results: list[ConversionResult] = []
    changed_target_queries: list[str] = []
    excluded_rule_ids = config.get("excludedRuleIds") or {}
    if not isinstance(excluded_rule_ids, dict):
        raise ValueError("excludedRuleIds must contain an object of rule IDs and reasons")

    source_documents: dict[Path, dict[str, Any]] = {}
    sources_by_id: dict[str, list[Path]] = {}
    for source in sources:
        with source.open(encoding="utf-8-sig") as handle:
            source_document = yaml.safe_load(handle) or {}
        if not isinstance(source_document, dict):
            raise ValueError(f"analytic rule must contain a YAML object: {source}")
        source_documents[source] = source_document
        source_id = str(source_document.get("id") or "")
        if source_id:
            sources_by_id.setdefault(source_id.casefold(), []).append(source)

    selected_sources = sources
    if rule_id is not None:
        if not isinstance(rule_id, str) or not re.fullmatch(SOURCE_ID_PATTERN, rule_id):
            raise ValueError("--rule-id must be a full hyphenated Sentinel template GUID")
        selected_sources = sources_by_id.get(rule_id.casefold(), [])
        if len(selected_sources) != 1:
            raise ValueError(
                f"--rule-id {rule_id!r} must match exactly one source analytic rule; "
                f"found {len(selected_sources)} (unknown or duplicate source ID)"
            )
        if any(str(key).casefold() == rule_id.casefold() for key in excluded_rule_ids):
            raise ValueError("--rule-id selects an excluded rule; reconcile excludedRuleIds explicitly")

    # Selection is checked before creating Logs, output directories, or removing exclusions.
    reports = report_directory(root, create=True)
    output.mkdir(parents=True, exist_ok=True)
    for source in selected_sources:
        target = content_path(output, source.relative_to(analytic))
        source_document = source_documents[source]
        source_id = str(source_document.get("id") or "")
        source_path = source.relative_to(root).as_posix()
        identity_error = None
        if len(sources_by_id.get(source_id.casefold(), [])) > 1:
            identity_error = f"duplicate source analytic rule id {source_id!r}; reconcile source identities before conversion"
        id_collisions = set(existing_by_id.get(source_id.casefold(), [])) - {target}
        if id_collisions:
            identity_error = (
                f"Custom Detection id {source_id!r} is already used by another output; "
                "review and explicitly relocate or reconcile it before conversion "
                "(even with --overwrite): "
                + ", ".join(path.relative_to(root).as_posix() for path in sorted(id_collisions))
            )
        existing_document = existing_documents.get(target)
        existing_properties = (
            existing_document.get("properties") or {}
            if isinstance(existing_document, dict) else {}
        )
        previous_target_query = (
            existing_properties.get("queryCondition", {}).get("queryText")
            if isinstance(existing_properties, dict)
            and isinstance(existing_properties.get("queryCondition"), dict)
            else None
        )
        if isinstance(existing_document, dict):
            existing_properties = existing_document.get("properties") or {}
            previous_id = str(existing_properties.get("id") or "") if isinstance(existing_properties, dict) else ""
            if previous_id and len(existing_by_id.get(previous_id.casefold(), [])) > 1:
                identity_error = f"duplicate existing Custom Detection id {previous_id!r}; reconcile output identities before conversion"
        if not identity_error and target.exists():
            identity_error = _existing_identity_error(
                existing_document, source_id, source_path,
                str(source_document.get("name") or source.stem),
            )
        if identity_error:
            results.append(ConversionResult(
                source, target, str(source_document.get("name") or source.stem),
                "conflict", True, (identity_error,), (), (identity_error,),
            ))
            continue
        alternate_outputs = set(
            existing_by_source.get(source_id.casefold(), [])
            + existing_by_source.get(source_path, [])
        ) - {target}
        # A legacy flattened file must not become a second detection for this source.
        legacy_target = output / source.name
        if (
            target != legacy_target
            and legacy_target.exists()
            and legacy_target not in identified_outputs
        ):
            alternate_outputs.add(legacy_target)
        if alternate_outputs:
            error = (
                "existing detection at a different path; review and explicitly relocate "
                "or reconcile it before conversion (even with --overwrite): "
                + ", ".join(path.relative_to(root).as_posix() for path in sorted(alternate_outputs))
            )
            results.append(ConversionResult(
                source, target, str(source_document.get("name") or source.stem),
                "conflict", True, (error,), (), (error,),
            ))
            continue
        exclusion_reason = excluded_rule_ids.get(source_id)
        if exclusion_reason is not None:
            if target.exists():
                if not overwrite:
                    results.append(
                        ConversionResult(
                            source,
                            target,
                            str(source_document.get("name") or source.stem),
                            "conflict",
                            True,
                            ("excluded output exists; rerun with --overwrite to remove it",),
                            (),
                            ("excluded output exists; rerun with --overwrite to remove it",),
                        )
                    )
                    continue
                target.unlink()
            results.append(
                ConversionResult(
                    source,
                    target,
                    str(source_document.get("name") or source.stem),
                    "excluded",
                    False,
                    (),
                    (f"excluded from Custom Detections: {exclusion_reason}",),
                    (),
                )
            )
            continue
        document = build_xdr_document(source, root, config)
        if target.exists():
            previous_provenance = existing_document.get("contentProvenance") or {}
            dependencies_current = (
                (previous_provenance.get("source") or {}).get("querySha256")
                == document["contentProvenance"]["source"]["querySha256"]
                and previous_target_query == document["properties"]["queryCondition"]["queryText"]
                and existing_document.get("requiredDataConnectors") == source_document.get("requiredDataConnectors")
            )
            if dependencies_current:
                for field in ("requiredWorkloads", "requiredDataConnectors", "dependencyReviewRequired"):
                    if field in previous_provenance:
                        document["contentProvenance"][field] = deepcopy(previous_provenance[field])
            if isinstance(existing_document, dict) and "version" in existing_document:
                error = xdr_version_error(existing_document["version"])
                if error:
                    results.append(
                        ConversionResult(
                            source, target, document["properties"]["displayName"],
                            "conflict", True, (error,), (), (error,),
                        )
                    )
                    continue
                if _version_tuple(existing_document["version"]) >= _version_tuple(document["version"]):
                    document["version"] = existing_document["version"]
            previous_id = existing_document["properties"]["id"]
            identity_change = (
                (existing_document.get("contentProvenance") or {}).get("conversion") or {}
            ).get("identityChange")
            canonical_id = document["properties"]["id"]
            if previous_id != canonical_id and not isinstance(identity_change, dict):
                identity_change = {
                    "previousId": previous_id,
                    "currentId": canonical_id,
                    "scope": "local-artifact-only",
                }
            elif isinstance(identity_change, dict) and identity_change.get("currentId") in {
                source_id, canonical_id,
            }:
                identity_change = {
                    **identity_change,
                    "currentId": canonical_id,
                    "scope": "local-artifact-only",
                }
            if isinstance(identity_change, dict) and identity_change.get("currentId") == canonical_id:
                conversion = document["contentProvenance"]["conversion"]
                conversion["identityChange"] = identity_change
                conversion["warnings"].append(
                    f"Local detection ID changed from {identity_change.get('previousId')!r} "
                    f"to canonical Graph-compatible ID {canonical_id!r} for source "
                    f"{source_id!r}. No cloud rules "
                    "were updated, deleted, or migrated. Review existing deployed rules "
                    "and reconcile their identities before any separately approved deployment."
                )
        rendered = yaml.dump(
            document,
            Dumper=XdrYamlDumper,
            sort_keys=False,
            allow_unicode=False,
            width=120,
        )
        if target.exists() and not overwrite:
            existing = target.read_text(encoding="utf-8")
            if existing != rendered:
                results.append(
                    ConversionResult(
                        source,
                        target,
                        document["properties"]["displayName"],
                        "conflict",
                        True,
                        ("output exists with different content; rerun with --overwrite",),
                        (),
                        ("output exists with different content; rerun with --overwrite",),
                    )
                )
                continue
        if not target.exists() or target.read_text(encoding="utf-8") != rendered:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8", newline="\n")
        current_target_query = document["properties"]["queryCondition"]["queryText"]
        if previous_target_query != current_target_query:
            changed_target_queries.append(target.relative_to(root).as_posix())
        conversion = document["contentProvenance"]["conversion"]
        results.append(
            ConversionResult(
                source,
                target,
                document["properties"]["displayName"],
                conversion["status"],
                bool(conversion["reviewRequired"]),
                tuple(conversion["reviewReasons"]),
                tuple(conversion["warnings"]),
                tuple(conversion["errors"]),
                tuple(conversion.get("informational") or []),
                len(document["properties"]["detectionAction"]["alertTemplate"].get("tactics") or []),
            )
        )

    reports = report_directory(root, create=True)
    transformation_report = reports / "transformation-report.html"
    manifest_path = reports / "manifest.json"
    summary = {
        "solution": str(root),
        "scope": {
            "kind": "rule" if rule_id is not None else "solution",
            "ruleIds": (
                [source_documents[source]["id"] for source in selected_sources]
                if rule_id is not None else []
            ),
            "sourceTotal": len(sources),
            "selectedTotal": len(selected_sources),
        },
        "outputDirectory": str(output),
        "reportDirectory": str(reports),
        "manifest": str(manifest_path),
        "transformationReport": str(transformation_report),
        "total": len(results),
        "converted": sum(result.status == "converted" for result in results),
        "excluded": sum(result.status == "excluded" for result in results),
        "needsReview": sum(result.status == "needsReview" for result in results),
        "reviewRequired": sum(result.review_required for result in results),
        "deploymentReady": sum(
            result.status == "converted" and not result.review_required and result.tactic_count <= 1
            for result in results
        ),
        "conflicts": sum(result.status == "conflict" for result in results),
        "results": [
            {
                **result.as_dict(),
                "sourceRelativePath": result.source.relative_to(root).as_posix(),
                "outputRelativePath": result.output.relative_to(root).as_posix(),
            }
            for result in results
        ],
    }
    write_json_artifact(root, manifest_path, summary)
    if rule_id is not None:
        from solution_manager.core.workflow import invalidate_scoped_completion

        invalidate_scoped_completion(root)
    elif changed_target_queries:
        from solution_manager.core.workflow import invalidate_runtime_completion

        invalidate_runtime_completion(root, changed_target_queries)
    write_transformation_report(portable_artifact(root, summary), transformation_report)
    return summary


def validate_solution(solution: str | Path) -> dict[str, Any]:
    root, _, output = solution_paths(solution)
    files = xdr_detection_files(output) if output.exists() else []
    results = []
    results_by_id: dict[str, list[dict[str, Any]]] = {}
    for path in files:
        detection_id = None
        warnings = []
        try:
            with path.open(encoding="utf-8-sig") as handle:
                document = yaml.safe_load(handle) or {}
            errors = validate_document(document)
            warnings = custom_detail_binding_warnings(document)
            detection_id = (document.get("properties") or {}).get("id")
        except (OSError, yaml.YAMLError, ValueError) as exc:
            errors = [str(exc)]
        result = {
            "file": str(path),
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
        }
        results.append(result)
        if isinstance(detection_id, str) and detection_id:
            results_by_id.setdefault(detection_id.casefold(), []).append(result)
    for detection_id, duplicates in results_by_id.items():
        if len(duplicates) > 1:
            for result in duplicates:
                result["errors"].append(f"duplicate Custom Detection id {detection_id!r}")
                result["valid"] = False
    return {
        "solution": str(root),
        "conversionScope": conversion_scope(root),
        "total": len(results),
        "valid": sum(item["valid"] for item in results),
        "invalid": sum(not item["valid"] for item in results),
        "results": results,
    }


def runtime_validation_plan(solution: str | Path) -> dict[str, Any]:
    root, _, output = solution_paths(solution)
    plan = []
    for path in xdr_detection_files(output):
        with path.open(encoding="utf-8-sig") as handle:
            document = yaml.safe_load(handle) or {}
        source_path = content_path(root, document["contentProvenance"]["source"]["path"])
        with source_path.open(encoding="utf-8-sig") as handle:
            source = yaml.safe_load(handle) or {}
        plan.append(
            {
                "detection": path.relative_to(output).as_posix(),
                "sourceRule": str(source_path),
                "sentinelQuery": str(source.get("query") or ""),
                "advancedHuntingQuery": document["properties"]["queryCondition"]["queryText"],
                "sentinelQuerySha256": hashlib.sha256(
                    str(source.get("query") or "").encode("utf-8")
                ).hexdigest(),
                "advancedHuntingQuerySha256": hashlib.sha256(
                    document["properties"]["queryCondition"]["queryText"].encode("utf-8")
                ).hexdigest(),
                "customDetailBindings": deepcopy(
                    document["properties"]["detectionAction"]["alertTemplate"].get("customDetails") or {}
                ),
            }
        )
    return {
        "solution": str(root),
        "instructions": (
            "Run sentinelQuery and advancedHuntingQuery through Microsoft Sentinel and "
            "the configured runtime providers. Include sentinelQuerySha256 as querySha256 "
            "for every imported Sentinel result. The Advanced Hunting validator records "
            "the exact target-query hash itself. Missing or stale query hashes cannot "
            "qualify current KQL. Record execution errors and compare output entities. "
            "Verify every customDetailBindings value against the returned Advanced Hunting output schema; "
            "query success alone does not prove these bindings. Check the combined custom-detail runtime "
            "value size against the documented 4 KB per-alert limit."
        ),
        "rules": plan,
    }
