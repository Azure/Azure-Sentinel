"""Qualification readiness assessment, inventory discovery, and private-config export auditing."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from solution_manager.migration.workbook_workflow import (
    assess_qualification_readiness as _workbook_assess_qualification_readiness,
    audit_private_config_and_support_export,
    build_lab_deployment_preflight_prompt,
    current_state,
    expected_content_counts,
    plan_lab_deployment_preflight,
    record_lab_deployment_validation_findings,
)

KNOWN_WORKBOOK_TABLES = (
    "AzureDiagnostics",
    "ContainerInventory",
    "ContainerLog",
    "ContainerLogV2",
    "KubeEvents",
    "KubeNodeInventory",
    "KubePodInventory",
    "KubeServices",
    "Perf",
    "Syslog",
    "SecurityEvent",
    "CommonSecurityLog",
    "SigninLogs",
    "AuditLogs",
    "DeviceEvents",
    "DeviceProcessEvents",
    "DeviceNetworkEvents",
    "DeviceFileEvents",
    "DeviceLogonEvents",
    "DeviceRegistryEvents",
    "IdentityLogonEvents",
    "IdentityQueryEvents",
    "IdentityDirectoryEvents",
    "EmailEvents",
    "CloudAppEvents",
    "AlertInfo",
    "AlertEvidence",
)


def _yaml_files_in_dir(directory: Path) -> list[Path]:
    if not directory.is_dir() or directory.is_symlink():
        return []
    files: list[Path] = []
    for ext in ("*.yaml", "*.yml"):
        for candidate in sorted(directory.rglob(ext)):
            if candidate.is_file() and not candidate.is_symlink():
                if candidate.name.lower() not in {"migration-config.yaml", "migration-config.yml"}:
                    files.append(candidate)
    return sorted(set(files))


def _json_files_in_dir(directory: Path) -> list[Path]:
    if not directory.is_dir() or directory.is_symlink():
        return []
    return sorted(
        candidate
        for candidate in directory.rglob("*.json")
        if candidate.is_file() and not candidate.is_symlink()
    )


def _extract_tables_from_kql(query: str) -> list[str]:
    if not isinstance(query, str) or not query.strip():
        return []
    found: list[str] = []
    for table in KNOWN_WORKBOOK_TABLES:
        if re.search(rf"\b{re.escape(table)}\b", query):
            found.append(table)
    for match in re.finditer(r"\b([A-Za-z][A-Za-z0-9_]*_CL)\b", query):
        table_name = match.group(1)
        if table_name not in found:
            found.append(table_name)
    return sorted(set(found))


def discover_solution_qualification_inventory(
    solution_path: str | Path,
    *,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Discover exact rules, workbooks, custom detections, and target tables/streams for a solution."""
    root = Path(solution_path).expanduser().resolve()
    if state is None:
        state = current_state(root)

    base_counts = expected_content_counts(root, state=state)

    rule_files: list[Path] = []
    for folder in ("Analytic Rules", "Analytics Rules"):
        rule_files.extend(_yaml_files_in_dir(root / folder))
    rule_paths = sorted({p.relative_to(root).as_posix() for p in rule_files})

    detection_files = _yaml_files_in_dir(root / "XDR Detections")
    detection_paths = sorted({p.relative_to(root).as_posix() for p in detection_files})

    sentinel_wb_files = _json_files_in_dir(root / "Workbooks")
    sentinel_wb_paths = sorted({p.relative_to(root).as_posix() for p in sentinel_wb_files})

    defender_wb_files = _json_files_in_dir(root / "XDR Workbooks")
    defender_wb_paths = sorted({p.relative_to(root).as_posix() for p in defender_wb_files})

    sentinel_rules_count = max(int(base_counts.get("sentinelRulesCount", 0)), len(rule_paths))
    sentinel_workbooks_count = max(int(base_counts.get("sentinelWorkbooksCount", 0)), len(sentinel_wb_paths))
    defender_workbooks_count = max(int(base_counts.get("defenderWorkbooksCount", 0)), len(defender_wb_paths))
    workbooks_count = max(
        int(base_counts.get("workbooksCount", 0)),
        sentinel_workbooks_count + defender_workbooks_count,
    )
    custom_detections_count = max(int(base_counts.get("customDetectionsCount", 0)), len(detection_paths))

    discovered_tables: set[str] = set()
    for rule_file in rule_files:
        try:
            doc = yaml.safe_load(rule_file.read_text(encoding="utf-8-sig")) or {}
        except Exception:
            doc = {}
        if isinstance(doc, dict):
            for conn in doc.get("requiredDataConnectors") or []:
                if isinstance(conn, dict):
                    for dt in conn.get("dataTypes") or []:
                        if isinstance(dt, str) and dt.strip():
                            discovered_tables.add(dt.strip())
            for tbl in _extract_tables_from_kql(str(doc.get("query") or "")):
                discovered_tables.add(tbl)

    for det_file in detection_files:
        try:
            doc = yaml.safe_load(det_file.read_text(encoding="utf-8-sig")) or {}
        except Exception:
            doc = {}
        if isinstance(doc, dict):
            prov = doc.get("contentProvenance") or {}
            if isinstance(prov, dict):
                for workload in prov.get("requiredWorkloads") or []:
                    if isinstance(workload, dict):
                        for dt in workload.get("dataTypes") or []:
                            if isinstance(dt, str) and dt.strip():
                                discovered_tables.add(dt.strip())
                for conn in prov.get("requiredDataConnectors") or []:
                    if isinstance(conn, dict):
                        for dt in conn.get("dataTypes") or []:
                            if isinstance(dt, str) and dt.strip():
                                discovered_tables.add(dt.strip())
            props = doc.get("properties") or {}
            if isinstance(props, dict):
                q_def = props.get("queryDefinition") or {}
                if isinstance(q_def, dict):
                    for tbl in _extract_tables_from_kql(str(q_def.get("query") or "")):
                        discovered_tables.add(tbl)

    for wb_file in [*sentinel_wb_files, *defender_wb_files]:
        try:
            wb_doc = json.loads(wb_file.read_text(encoding="utf-8-sig"))
        except Exception:
            wb_doc = {}
        if isinstance(wb_doc, dict):
            prov = wb_doc.get("contentProvenance") or {}
            if isinstance(prov, dict):
                for key in ("requiredWorkloads", "requiredDataConnectors"):
                    for item in prov.get(key) or []:
                        if isinstance(item, dict):
                            for dt in item.get("dataTypes") or []:
                                if isinstance(dt, str) and dt.strip():
                                    discovered_tables.add(dt.strip())
            raw_text = json.dumps(wb_doc)
            for tbl in _extract_tables_from_kql(raw_text):
                discovered_tables.add(tbl)

    target_tables = sorted(discovered_tables) or ["Syslog"]
    target_streams = [
        {
            "table": table,
            "streamName": table if table.startswith("Custom-") else f"Custom-{table}",
        }
        for table in target_tables
    ]

    return {
        "sentinelRulesCount": sentinel_rules_count,
        "sentinelWorkbooksCount": sentinel_workbooks_count,
        "defenderWorkbooksCount": defender_workbooks_count,
        "workbooksCount": workbooks_count,
        "workbooksBreakdown": {
            "sentinel": sentinel_workbooks_count,
            "defender": defender_workbooks_count,
        },
        "customDetectionsCount": custom_detections_count,
        "sentinelRulePaths": rule_paths,
        "sentinelWorkbookPaths": sentinel_wb_paths,
        "defenderWorkbookPaths": defender_wb_paths,
        "customDetectionPaths": detection_paths,
        "targetTables": target_tables,
        "targetStreams": target_streams,
    }


def assess_qualification_readiness(
    solution_path: str | Path,
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Assess qualification readiness and enrich with discovered content inventory and Bicep/ARM what-if policy."""
    readiness = _workbook_assess_qualification_readiness(solution_path, run_id=run_id)
    inventory = discover_solution_qualification_inventory(solution_path)
    counts = readiness.get("expectedContentCounts") or {}
    merged_counts = {
        "sentinelRulesCount": max(int(counts.get("sentinelRulesCount", 0)), inventory["sentinelRulesCount"]),
        "sentinelWorkbooksCount": max(int(counts.get("sentinelWorkbooksCount", 0)), inventory["sentinelWorkbooksCount"]),
        "defenderWorkbooksCount": max(int(counts.get("defenderWorkbooksCount", 0)), inventory["defenderWorkbooksCount"]),
        "workbooksCount": max(int(counts.get("workbooksCount", 0)), inventory["workbooksCount"]),
        "workbooksBreakdown": {
            "sentinel": max(
                int((counts.get("workbooksBreakdown") or {}).get("sentinel", 0)),
                inventory["sentinelWorkbooksCount"],
            ),
            "defender": max(
                int((counts.get("workbooksBreakdown") or {}).get("defender", 0)),
                inventory["defenderWorkbooksCount"],
            ),
        },
        "customDetectionsCount": max(int(counts.get("customDetectionsCount", 0)), inventory["customDetectionsCount"]),
    }
    x = merged_counts["sentinelRulesCount"]
    y = merged_counts["workbooksCount"]
    z = merged_counts["customDetectionsCount"]
    readiness["expectedContentCounts"] = merged_counts
    readiness["labDeploymentPreflightPrompt"] = (
        "Requesting preflight preapproval to deploy the solution ARM templates to the "
        "selected non-production lab to verify ARM template deployment validity "
        f"(expected content items: {x} Sentinel rules, {y} workbooks, and {z} custom detections). "
        "Deployment verification alone does not establish functional/runtime qualification or alert parity."
    )
    readiness["armWhatIfSupportedForXdrExtensions"] = False
    readiness["targetTables"] = inventory["targetTables"]
    readiness["targetStreams"] = inventory["targetStreams"]
    return readiness


__all__ = [
    "assess_qualification_readiness",
    "audit_private_config_and_support_export",
    "build_lab_deployment_preflight_prompt",
    "discover_solution_qualification_inventory",
    "expected_content_counts",
    "plan_lab_deployment_preflight",
    "record_lab_deployment_validation_findings",
]
