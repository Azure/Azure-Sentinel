from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from . import __version__
from .catalog import (
    query_column_renames,
    query_has_mixed_time_semantics,
    query_requires_timestamp,
)
from .columns import projected_columns
from .report import write_transformation_report

SCHEMA_VERSION = "1.0.0"
DETECTION_API_VERSION = "2026-06-01-preview"
ENTITY_CONFIRMATION_PREFIX = "Entity confirmation required:"
REQUIRED_ASSET_COLLECTIONS = frozenset({"hosts", "accounts", "mailboxes", "ips"})
SUPPORTED_SEVERITIES = frozenset({"informational", "low", "medium", "high"})
BLOCKING_KQL_PATTERNS = {
    r"\bworkspace\s*\(": "cross-workspace queries require manual redesign",
}
REVIEW_KQL_PATTERNS = {
    r"\bexternaldata\s*\(": "externaldata availability must be verified by runtime validation",
    r"\bsearch\b": "search queries should be replaced with explicit tables",
    r"\bunion\s+isfuzzy\s*=\s*true\b": "isfuzzy unions can still fail semantic binding in Advanced Hunting",
    r"\b_[Ii]m_[A-Za-z0-9_]+\s*\(": "ASIM parser availability must be verified in Advanced Hunting",
}

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
        }


def configure_logging(tool_root: Path) -> None:
    log_dir = tool_root / "Data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "sentinel-xdr-migration.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:72] or "custom-detection"


def iso_duration(value: Any, default: str = "PT1H") -> tuple[str, str | None]:
    text = str(value or "").strip().lower()
    iso = text.upper()
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
    path = Path(explicit).expanduser().resolve() if explicit else output_dir / "migration-config.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError(f"migration config must contain a YAML object: {path}")
    return value


def analytic_rule_files(solution: str | Path) -> list[Path]:
    _, analytic, _ = solution_paths(solution)
    return sorted([*analytic.glob("*.yaml"), *analytic.glob("*.yml")])


def xdr_detection_files(output: Path) -> list[Path]:
    return sorted(
        path
        for path in [*output.glob("*.yaml"), *output.glob("*.yml")]
        if path.name.lower() != "migration-config.yaml"
    )


def inspect_solution(solution: str | Path) -> dict[str, Any]:
    root, analytic, output = solution_paths(solution)
    files = analytic_rule_files(root)
    return {
        "solution": str(root),
        "analyticRulesDirectory": str(analytic),
        "xdrDetectionsDirectory": str(output),
        "analyticRuleCount": len(files),
        "analyticRules": [path.name for path in files],
        "existingXdrDetectionCount": len(xdr_detection_files(output)) if output.exists() else 0,
    }


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


def _configured_column_mappings(config: dict[str, Any]) -> dict[str, str]:
    mappings: dict[str, str] = {}
    configured = config.get("columnMappings") or {}
    if configured and all(isinstance(value, str) for value in configured.values()):
        mappings.update({str(key): str(value) for key, value in configured.items()})
    else:
        for value in configured.values():
            if isinstance(value, dict):
                mappings.update({str(key): str(target) for key, target in value.items()})
    return mappings


def convert_query(query: str, config: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    converted = query.strip()

    source_mappings: dict[str, str] = {}
    source_mappings.update(
        {str(k): str(v) for k, v in (config.get("functionMappings") or {}).items()}
    )
    source_mappings.update(
        {str(k): str(v) for k, v in (config.get("tableMappings") or {}).items()}
    )
    converted = _token_replace(converted, source_mappings)

    column_mappings: dict[str, str] = query_column_renames(converted)
    column_mappings.update(_configured_column_mappings(config))
    converted = _token_replace(converted, column_mappings)
    converted = "\n".join(line.rstrip() for line in converted.splitlines())
    converted = re.sub(r";\s*\Z", "", converted)

    for pattern, message in BLOCKING_KQL_PATTERNS.items():
        if re.search(pattern, converted, re.IGNORECASE):
            errors.append(message)
    for pattern, message in REVIEW_KQL_PATTERNS.items():
        if re.search(pattern, converted, re.IGNORECASE):
            warnings.append(message)
    if query_has_mixed_time_semantics(converted):
        warnings.append(
            "query mixes native Defender and Sentinel workload tables; "
            "time columns were preserved and require runtime validation"
        )

    if query_requires_timestamp(converted) and not re.search(r"\bTimestamp\b", converted):
        errors.append("converted query does not expose or reference the required Timestamp column")
    return converted, warnings, errors


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


def convert_entities(
    doc: dict[str, Any],
    query: str,
    column_mappings: dict[str, str] | None = None,
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    output: dict[str, list[dict[str, Any]]] = {}
    warnings: list[str] = []
    counters: dict[str, int] = {}
    columns = projected_columns(query)

    for entity in doc.get("entityMappings") or []:
        entity_type = str(entity.get("entityType") or "")
        if entity_type not in ENTITY_MAP:
            warnings.append(f"{entity_type or 'Unknown entity'} has no supported Custom Detection mapping")
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
                fields[target] = column
            elif target and column:
                warnings.append(
                    f"{entity_type}.{identifier} column `{column}` is not produced by the query"
                )
            elif identifier:
                unsupported.append(identifier)
        if entity_type == "Account" and not _valid_account(fields):
            fields = _repair_account(fields, source_fields, columns, warnings)
        for identifier in unsupported:
            if not (entity_type == "Account" and identifier == "FullName" and fields):
                warnings.append(
                    f"{entity_type}.{identifier} has no supported Custom Detection field"
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


def build_xdr_document(source: Path, solution_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    with source.open(encoding="utf-8-sig") as handle:
        doc = yaml.safe_load(handle) or {}
    if not isinstance(doc, dict):
        raise ValueError(f"analytic rule must contain a YAML object: {source}")

    source_query = str(doc.get("query") or "")
    converted_query, query_warnings, errors = convert_query(source_query, config)
    warnings = list(query_warnings)
    review_reasons = list(query_warnings)
    is_nrt = str(doc.get("kind") or "").lower() == "nrt"
    frequency, frequency_warning = iso_duration(
        doc.get("queryFrequency") or ("PT1H" if is_nrt else None)
    )
    if frequency_warning:
        warnings.append(frequency_warning)
        review_reasons.append(frequency_warning)
    query_period = str(doc.get("queryPeriod") or "").strip()
    if query_period and query_period.lower() not in source_query.lower():
        reason = "source queryPeriod has no direct Custom Detection schedule field; verify the KQL lookback"
        warnings.append(reason)
    source_id = str(doc.get("id") or "")
    rule_override = (config.get("ruleOverrides") or {}).get(source_id) or {}

    mappings, mapping_warnings = convert_entities(
        doc,
        converted_query,
        _configured_column_mappings(config),
    )
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
    entity_review_reasons = [
        warning
        for warning in mapping_warnings
        if warning.startswith(ENTITY_CONFIRMATION_PREFIX)
    ]
    if entity_review_reasons and REQUIRED_ASSET_COLLECTIONS.intersection(
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
        entity_review_reasons = []
    warnings.extend(mapping_warnings)
    review_reasons.extend(entity_review_reasons)

    source_tactics = [str(value) for value in doc.get("tactics") or [] if value]
    source_relevant = [
        str(value) for value in doc.get("relevantTechniques") or [] if value
    ]
    tactics = list(source_tactics)
    relevant = list(source_relevant)
    if len(tactics) > 1:
        selected_tactic = rule_override.get("tactic")
        selected_techniques = rule_override.get("techniques")
        if selected_tactic:
            tactics = [str(selected_tactic)]
            relevant = [str(value) for value in selected_techniques or [] if value]
            warnings.append(
                "multiple source tactics were resolved by the configured per-rule override"
            )
        else:
            reason = (
                "Custom Detections support one tactic; configure ruleOverrides."
                f"{source_id}.tactic and techniques"
            )
            warnings.append(reason)
            review_reasons.append(reason)
            tactics = [tactics[0]]
            relevant = []
    if not mappings:
        errors.append("no supported entity mappings were produced")
    elif not REQUIRED_ASSET_COLLECTIONS.intersection(mappings):
        errors.append("a Host, Account, Mailbox, or IP mapping is required")

    if not source_id:
        errors.append("source analytic rule has no id")

    accepted_review_reasons = {
        str(value)
        for value in rule_override.get("acceptedReviewReasons") or []
        if value
    }
    unknown_acceptances = accepted_review_reasons.difference(review_reasons)
    if unknown_acceptances:
        errors.extend(
            "configured acceptedReviewReasons entry does not match a current review "
            f"reason: {reason}"
            for reason in sorted(unknown_acceptances)
        )
    review_reasons = [
        reason for reason in review_reasons if reason not in accepted_review_reasons
    ]

    display_name = str(doc.get("name") or source.stem)
    detection_id = f"xdr-{slugify(display_name)}-{source_id[:8] or 'unversioned'}"
    severity = str(doc.get("severity") or "Medium").lower()
    if severity not in SUPPORTED_SEVERITIES:
        warnings.append(f"unsupported severity {severity!r}; changed to medium")
        severity = "medium"

    tactic_payload: list[dict[str, Any]] = []
    if tactics:
        tactic = {"tactic": tactics[0]}
        technique_payload = _techniques(relevant)
        if technique_payload:
            tactic["techniques"] = technique_payload
        tactic_payload.append(tactic)

    alert: dict[str, Any] = {
        "title": display_name[:120],
        "description": str(doc.get("description") or display_name).strip()[:600],
        "severity": severity,
        "entityMappings": mappings,
    }
    if tactic_payload:
        alert["tactics"] = tactic_payload

    blocking_review_reasons = [
        reason
        for reason in review_reasons
        if not reason.startswith(ENTITY_CONFIRMATION_PREFIX)
    ]
    status = "needsReview" if errors or blocking_review_reasons else "converted"
    relative_source = source.relative_to(solution_root).as_posix()
    return {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "CustomDetection",
        "resourceType": "Microsoft.Security/detectionRules",
        "apiVersion": DETECTION_API_VERSION,
        "contentProvenance": {
            "source": {
                "platform": "Microsoft Sentinel",
                "kind": "AnalyticsRule",
                "id": source_id,
                "path": relative_source,
                "version": str(doc.get("version") or ""),
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
                "errors": errors,
                "originalTactics": source_tactics,
                "originalTechniques": source_relevant,
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
            "schedule": {"frequency": frequency},
            "detectionAction": {"alertTemplate": alert},
        },
    }


def validate_document(document: dict[str, Any]) -> list[str]:
    schema_path = Path(__file__).resolve().parents[1] / "schema" / "xdr-detection.schema.json"
    with schema_path.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    errors = [
        f"schema: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(document)
    ]
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
    alert = ((properties.get("detectionAction") or {}).get("alertTemplate") or {})
    mappings = alert.get("entityMappings") or {}
    if not mappings:
        errors.append("alertTemplate.entityMappings is required")
    if not REQUIRED_ASSET_COLLECTIONS.intersection(mappings):
        errors.append("at least one Host, Account, Mailbox, or IP mapping is required")
    if len(alert.get("tactics") or []) > 1:
        errors.append("at most one tactic is supported")
    return errors


def convert_solution(
    solution: str | Path,
    *,
    overwrite: bool = False,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    root, _, output = solution_paths(solution)
    output.mkdir(parents=True, exist_ok=True)
    config = load_config(output, config_path)
    results: list[ConversionResult] = []
    excluded_rule_ids = config.get("excludedRuleIds") or {}
    if not isinstance(excluded_rule_ids, dict):
        raise ValueError("excludedRuleIds must contain an object of rule IDs and reasons")

    for source in analytic_rule_files(root):
        target = output / source.name
        with source.open(encoding="utf-8-sig") as handle:
            source_document = yaml.safe_load(handle) or {}
        if not isinstance(source_document, dict):
            raise ValueError(f"analytic rule must contain a YAML object: {source}")
        source_id = str(source_document.get("id") or "")
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
        target.write_text(rendered, encoding="utf-8", newline="\n")
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
            )
        )

    transformation_report = output / "transformation-report.html"
    summary = {
        "solution": str(root),
        "outputDirectory": str(output),
        "transformationReport": str(transformation_report),
        "total": len(results),
        "converted": sum(result.status == "converted" for result in results),
        "excluded": sum(result.status == "excluded" for result in results),
        "needsReview": sum(result.status == "needsReview" for result in results),
        "reviewRequired": sum(result.review_required for result in results),
        "deploymentReady": sum(
            result.status == "converted" and not result.review_required for result in results
        ),
        "conflicts": sum(result.status == "conflict" for result in results),
        "results": [result.as_dict() for result in results],
    }
    (output / "manifest.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    write_transformation_report(summary, transformation_report)
    report_path = Path(__file__).resolve().parents[1] / "Data" / "reports" / "last-conversion.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return summary


def validate_solution(solution: str | Path) -> dict[str, Any]:
    root, _, output = solution_paths(solution)
    files = xdr_detection_files(output) if output.exists() else []
    results = []
    for path in files:
        try:
            with path.open(encoding="utf-8-sig") as handle:
                document = yaml.safe_load(handle) or {}
            errors = validate_document(document)
        except (OSError, yaml.YAMLError, ValueError) as exc:
            errors = [str(exc)]
        results.append({"file": str(path), "valid": not errors, "errors": errors})
    return {
        "solution": str(root),
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
        source_path = root / document["contentProvenance"]["source"]["path"]
        with source_path.open(encoding="utf-8-sig") as handle:
            source = yaml.safe_load(handle) or {}
        plan.append(
            {
                "detection": path.name,
                "sourceRule": str(source_path),
                "sentinelQuery": str(source.get("query") or ""),
                "advancedHuntingQuery": document["properties"]["queryCondition"]["queryText"],
            }
        )
    return {
        "solution": str(root),
        "instructions": (
            "Run sentinelQuery and advancedHuntingQuery through the Microsoft Sentinel "
            "the configured runtime providers. Record execution errors and compare output entities."
        ),
        "rules": plan,
    }
