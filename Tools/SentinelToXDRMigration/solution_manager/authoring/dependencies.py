"""Offline dependency records and interpretation of Log Analytics input metadata."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from solution_manager.migration.catalog import NATIVE_XDR_TABLES, query_table_references

WORKLOADS = (
    "mde", "mdo", "mdi", "mda", "mdc", "entraid", "purview",
    "appgovernance", "sentinel", "mtp",
)
PLATFORM_REFERENCE_INPUTS = frozenset({"Watchlist"})


def telemetry_data_types(tables):
    """Platform reference data is source lineage, not connector telemetry."""
    return sorted(set(tables) - PLATFORM_REFERENCE_INPUTS)


TABLE_WORKLOADS = {
    **{table: "mde" for table in NATIVE_XDR_TABLES if table.startswith("Device")},
    **{table: "mdo" for table in (
        "EmailAttachmentInfo", "EmailEvents", "EmailPostDeliveryEvents",
        "EmailUrlInfo", "FileMaliciousContentInfo", "MessageEvents",
        "MessagePostDeliveryEvents", "MessageUrlInfo", "UrlClickEvents",
    )},
    **{table: "mdi" for table in (
        "IdentityDirectoryEvents", "IdentityLogonEvents", "IdentityQueryEvents",
    )},
    **{table: "mtp" for table in ("AlertInfo", "AlertEvidence", "IdentityInfo")},
    "CloudAppEvents": "mda",
    **{table: "sentinel" for table in (
        "Syslog", "SecurityAlert", "SecurityIncident", "SecurityEvent", "WindowsEvent", "Event",
        "AzureActivity", "AzureDiagnostics", "CommonSecurityLog", "SigninLogs", "AuditLogs",
        "OfficeActivity", "PowerBIActivity", "PowerPlatformAdminActivity", "AWSCloudTrail", "AWSGuardDuty",
    )},
}


def data_source_tables(metadata: Any) -> list[str]:
    if metadata is None:
        return []
    if not isinstance(metadata, list):
        raise ValueError("Log Analytics dataSources must be an array")
    tables: set[str] = set()
    for source in metadata:
        if not isinstance(source, dict):
            raise ValueError("each dataSources entry must be an object")
        source_tables = source.get("tables")
        if source_tables is None:
            continue
        if not isinstance(source_tables, list):
            raise ValueError("dataSources.tables must be an array")
        for entry in source_tables:
            name = entry.get("name") if isinstance(entry, dict) else entry
            if not isinstance(name, str) or not name.strip():
                raise ValueError("dataSources contains an invalid input table name")
            tables.add(name)
    return sorted(tables)


def resolve_data_types(query: str, metadata: Any = None) -> dict[str, Any]:
    returned = data_source_tables(metadata)
    if 0 < len(returned) <= 10:
        return {"method": "log-analytics", "dataTypes": returned, "returnedDataTypes": returned}
    tables = sorted({
        str(item["table"])
        for item in query_table_references(query, known_tables=TABLE_WORKLOADS)
    })
    return {
        "method": "regex",
        "dataTypes": tables,
        "returnedDataTypes": returned,
        "fallbackReason": "more-than-10-tables" if len(returned) > 10 else "missing-data-sources",
    }


def workload_records(tables: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    unknown = []
    for table in tables:
        if table in PLATFORM_REFERENCE_INPUTS:
            continue
        workload = TABLE_WORKLOADS.get(table)
        if workload is None and table.endswith("_CL"):
            workload = "sentinel"
        if workload is None:
            unknown.append(table)
        else:
            grouped[workload].add(table)
    return [
        {"workload": workload, "dataTypes": sorted(data_types)}
        for workload, data_types in sorted(grouped.items())
    ], sorted(unknown)


STANDARD_BUILTIN_ASIM_PARSER_RE = re.compile(
    r"\b(_(?:asim|im)_(?!test\b)[A-Za-z0-9_]+)\b",
    re.IGNORECASE,
)


def extract_builtin_asim_parsers(query: str) -> list[str]:
    from solution_manager.migration._workbook_core import rewrite
    code = "".join(text if kind == "code" else " " * len(text)
                   for kind, text in rewrite._segments(query or ""))
    found: set[str] = set()
    for match in STANDARD_BUILTIN_ASIM_PARSER_RE.finditer(code):
        found.add(match.group(1))
    return sorted(found)


def dependency_plan(
    source_query: str,
    *,
    target_query: str | None = None,
    metadata: Any = None,
    connectors: Any = None,
    table_mappings: dict[str, str] | None = None,
) -> dict[str, Any]:
    from solution_manager.migration._workbook_core import rewrite
    source_free_literal = rewrite.is_source_free_literal_query(source_query)
    resolution = resolve_data_types(source_query, None if source_free_literal else metadata)
    source_types = set(resolution["dataTypes"])
    code = "".join(text if kind == "code" else " " * len(text)
                   for kind, text in rewrite._segments(source_query))
    if re.search(r"\b_GetWatchlist\s*\(", code):
        source_types.add("Watchlist")
    builtin_asim_parsers = extract_builtin_asim_parsers(source_query)
    if not source_types and builtin_asim_parsers and isinstance(connectors, list):
        for record in connectors:
            if isinstance(record, dict) and isinstance(record.get("dataTypes"), list):
                source_types.update(
                    table.strip() for table in record["dataTypes"]
                    if isinstance(table, str) and table.strip()
                )
    references = sorted(source_types & PLATFORM_REFERENCE_INPUTS)
    resolution["dataTypes"] = telemetry_data_types(source_types)
    mappings = table_mappings or {}
    target_table_names = {mappings.get(table, table) for table in resolution["dataTypes"]}
    if target_query is not None:
        target_table_names.update(resolve_data_types(target_query)["dataTypes"])
    target_tables = telemetry_data_types(target_table_names)
    workloads, unknown = workload_records(target_tables)
    reasons = []
    if (not source_types and not source_free_literal
            and not (builtin_asim_parsers and isinstance(connectors, list))):
        reasons.append("No source inputs resolved; provide source evidence and any telemetry connector prerequisites.")
    if unknown:
        reasons.append(f"Provide workload mappings for: {', '.join(unknown)}.")
    required_connectors = deepcopy(connectors) if connectors is not None else []
    if isinstance(required_connectors, list):
        required_connectors = [
            {**record, "dataTypes": telemetry_data_types(record["dataTypes"])}
            if isinstance(record, dict) and isinstance(record.get("dataTypes"), list) else record
            for record in required_connectors
            if not isinstance(record, dict) or not isinstance(record.get("dataTypes"), list)
            or telemetry_data_types(record["dataTypes"])
        ]
    if any(item["workload"] == "sentinel" for item in workloads) and connectors is None:
        reasons.append("Provide or explicitly confirm the Sentinel connector prerequisites.")
    return {
        **resolution,
        "targetDataTypes": target_tables,
        "targetDiscoveryMethod": "regex" if target_query is not None else "source-table-mappings",
        "requiredWorkloads": workloads,
        "requiredDataConnectors": required_connectors,
        "unmappedDataTypes": unknown,
        "reviewRequired": bool(reasons),
        "reviewReasons": reasons,
        "runtimeParityVerified": False,
        **({"sourceDataTypes": sorted(source_types), "referenceInputs": references} if references else {}),
        **({"builtinAsimParsers": builtin_asim_parsers} if builtin_asim_parsers else {}),
    }


def dependency_validation_errors(document: dict[str, Any]) -> list[str]:
    provenance = document.get("contentProvenance")
    if not isinstance(provenance, dict):
        return ["contentProvenance must contain requiredWorkloads and requiredDataConnectors"]
    errors = []
    for field, identity in (
        ("requiredWorkloads", "workload"),
        ("requiredDataConnectors", "connectorId"),
    ):
        records = provenance.get(field)
        if not isinstance(records, list):
            errors.append(f"contentProvenance.{field} must be an array")
            continue
        for index, record in enumerate(records):
            prefix = f"contentProvenance.{field}[{index}]"
            if not isinstance(record, dict):
                errors.append(f"{prefix} must be an object")
                continue
            name = record.get(identity)
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{prefix}.{identity} must be a non-empty string")
            elif identity == "workload" and name not in WORKLOADS:
                errors.append(f"{prefix}.workload must be one of {', '.join(WORKLOADS)}")
            data_types = record.get("dataTypes")
            if not isinstance(data_types, list) or any(
                not isinstance(table, str) or not table.strip() for table in data_types
            ):
                errors.append(f"{prefix}.dataTypes must be an array of non-empty strings")
            elif any(table in PLATFORM_REFERENCE_INPUTS for table in data_types):
                errors.append(f"{prefix}.dataTypes must not include platform reference input Watchlist")
    if provenance.get("dependencyReviewRequired") is True:
        errors.append("Dependency provenance needs review; use sentinel-xdr-dependency-helper.")
    return errors


def live_dependency_check(
    document: dict[str, Any], source_query: str, metadata: Any,
    *, table_mappings: dict[str, str] | None = None,
    source_connectors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    errors = dependency_validation_errors(document)
    if errors:
        return {"status": "failed", "errors": errors, "method": "not-evaluated"}
    plan = dependency_plan(
        source_query, metadata=metadata,
        target_query=((document.get("properties") or {}).get("queryCondition") or {}).get("queryText"),
        connectors=(document.get("contentProvenance") or {}).get("requiredDataConnectors"),
        table_mappings=table_mappings,
    )
    declared = (document.get("contentProvenance") or {}).get("requiredWorkloads") or []
    declared_pairs = {
        (item["workload"], table)
        for item in declared if isinstance(item, dict) and isinstance(item.get("dataTypes"), list)
        for table in item["dataTypes"]
        if isinstance(item.get("workload"), str) and isinstance(table, str)
    }
    for record in plan["requiredWorkloads"]:
        for table in record["dataTypes"]:
            if (record["workload"], table) not in declared_pairs:
                errors.append(f"YAML does not declare {record['workload']} data type {table}")
    unknown = [
        table for table in plan["unmappedDataTypes"]
        if not any(pair[1] == table for pair in declared_pairs)
    ]
    if unknown:
        errors.append(f"Provide workload mappings for: {', '.join(unknown)}.")
    if not plan["dataTypes"] and not plan.get("referenceInputs") and not plan.get("builtinAsimParsers"):
        errors.append("No data types resolved; provide the data types and required connectors.")
    connector_records = (document.get("contentProvenance") or {}).get("requiredDataConnectors") or []
    connector_pairs = {
        (record.get("connectorId"), table)
        for record in connector_records
        if isinstance(record, dict) and isinstance(record.get("dataTypes"), list)
        for table in record["dataTypes"]
        if isinstance(record.get("connectorId"), str) and isinstance(table, str)
    }
    if source_connectors is not None:
        source_errors = dependency_validation_errors({"contentProvenance": {
            "requiredWorkloads": [], "requiredDataConnectors": source_connectors,
        }})
        if source_errors:
            return {**plan, "status": "failed", "errors": errors + source_errors}
    declared_connectors = {record["connectorId"] for record in connector_records}
    for record in (source_connectors if isinstance(source_connectors, list) else []):
        if record["connectorId"] not in declared_connectors:
            errors.append(f"YAML does not declare connector {record['connectorId']}")
        for table in record["dataTypes"]:
            if (record.get("connectorId"), table) not in connector_pairs:
                errors.append(f"YAML does not declare connector {record.get('connectorId')} data type {table}")
    return {**plan, "status": "failed" if errors else "passed", "errors": errors}


def plan_solution_dependencies(
    solution: str | Path, *, results_path: str | Path | None = None,
    workspace_id: str | None = None,
) -> dict[str, Any]:
    # Import here because conversion itself uses the pure dependency helpers.
    from solution_manager.migration.converter import load_config, runtime_validation_plan

    root = Path(solution).expanduser().resolve()
    rules = runtime_validation_plan(root)["rules"]
    if not rules:
        raise ValueError("dependency planning requires current XDR detections")
    config = load_config(root / "XDR Detections")
    entries = {}
    if results_path is not None:
        if not workspace_id:
            raise ValueError("dependency metadata import requires the explicitly approved workspace ID")
        raw = json.loads(Path(results_path).expanduser().read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or not isinstance(raw.get("results"), list):
            raise ValueError("dependency results must contain a results array")
        for entry in raw["results"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("detection"), str):
                raise ValueError("each dependency result must identify a detection")
            name = entry["detection"]
            if name in entries:
                raise ValueError(f"duplicate dependency metadata for {name}")
            entries[name] = entry
        if set(entries) != {item["detection"] for item in rules}:
            raise ValueError("dependency metadata must match the complete current detection inventory")
    results = []
    for rule in rules:
        document = yaml.safe_load(
            (root / "XDR Detections" / rule["detection"]).read_text(encoding="utf-8-sig")
        )
        source = yaml.safe_load(Path(rule["sourceRule"]).read_text(encoding="utf-8-sig"))
        entry = entries.get(rule["detection"])
        metadata = None
        if entry is not None:
            if (
                entry.get("status") != "passed"
                or entry.get("partial") is True
                or entry.get("error")
                or entry.get("errorDetails")
                or entry.get("failureKind")
                or (
                    entry.get("statusCode") is not None
                    and entry["statusCode"] != 200
                )
                or entry.get("workspaceId") != workspace_id
                or entry.get("querySha256") != rule["sentinelQuerySha256"]
            ):
                raise ValueError(
                    f"dependency metadata failed or has stale/cross-workspace scope: {rule['detection']}"
                )
            metadata = entry.get("dataSources")
        proposal = dependency_plan(
            rule["sentinelQuery"], metadata=metadata,
            target_query=rule["advancedHuntingQuery"],
            connectors=source.get("requiredDataConnectors"),
            table_mappings=config.get("tableMappings"),
        )
        results.append({
            **rule,
            **proposal,
            "workspaceId": workspace_id,
            "dataSources": metadata,
            "validation": live_dependency_check(
                document, rule["sentinelQuery"], metadata,
                table_mappings=config.get("tableMappings"),
                source_connectors=source.get("requiredDataConnectors"),
            ) if entry is not None else None,
        })
    return {"solution": str(root), "writesYaml": False, "liveQueriesExecuted": False, "results": results}


def solution_package_context(solution: str | Path) -> dict[str, str]:
    from solution_manager.core.content_paths import content_path
    from solution_manager.packaging.packaging import _solution_data_file

    root = Path(solution).expanduser().resolve()
    data = json.loads(_solution_data_file(root / "Data").read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("solution Data must be an object")
    metadata_path = data.get("Metadata")
    if not isinstance(metadata_path, str) or not metadata_path.strip():
        raise ValueError("solution Data must explicitly reference its Metadata")
    metadata = json.loads(content_path(root, metadata_path).read_text(encoding="utf-8-sig"))
    if not isinstance(metadata, dict):
        raise ValueError("solution Metadata must be an object")
    values = [metadata.get("publisherId"), metadata.get("offerId"), data.get("Version")]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError("deployment provenance requires publisherId, offerId and solution Version")
    return {"packageId": f"{values[0]}.{values[1]}", "packageVersion": values[2]}


def deployed_provenance(document: dict[str, Any], package_context: dict[str, str]) -> dict[str, str]:
    values = {
        "packageId": package_context.get("packageId"),
        "packageVersion": package_context.get("packageVersion"),
        "contentId": (document.get("properties") or {}).get("id"),
        "contentVersion": document.get("version"),
    }
    result: dict[str, str] = {}
    for key, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError("deployed provenance requires resolved package and content identity/version")
        result[key] = value
    return result


def dependency_identity(document: dict[str, Any]) -> str:
    provenance = document.get("contentProvenance") or {}
    values = {
        field: provenance.get(field)
        for field in ("requiredWorkloads", "requiredDataConnectors")
    }
    values["dependencyReviewRequired"] = provenance.get("dependencyReviewRequired", False)
    if "requiredWorkspaceFunctions" in provenance:
        values["requiredWorkspaceFunctions"] = provenance["requiredWorkspaceFunctions"]
    return hashlib.sha256(json.dumps(
        values, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()
