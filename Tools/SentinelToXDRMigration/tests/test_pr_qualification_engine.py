"""Unit and integration tests for PR Applicability and Qualification Check Runner Engine (Stream 2)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from solution_manager.qualification.pr_applicability import (
    BUILTIN_CHECK_CATALOG,
    determine_pr_applicability,
    load_check_catalog,
)
from solution_manager.qualification.pr_check_runner import (
    run_pr_qualification_checks,
)
from solution_manager.cli import main as cli_main

REPO_ROOT = Path(__file__).resolve().parents[3]
DDOS_SOLUTION_PATH = REPO_ROOT / "Solutions" / "Azure DDoS Protection"

REQUIRED_CHECK_RESULT_FIELDS: set[str] = {
    "id",
    "checklist",
    "title",
    "originalCriterion",
    "contentType",
    "category",
    "sourceChecklist",
    "applicable",
    "applicabilityReason",
    "status",
    "whatWeChecked",
    "whatWeObserved",
    "whyPassedOrFailed",
    "evidenceRefs",
    "authorException",
    "reviewerActionRequired",
    "reviewerActionPrompt",
}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _build_base_package(
    sol_root: Path,
    *,
    version: str = "3.2.2",
    data_lists: dict[str, list[str]] | None = None,
    include_xdr_props: bool = False,
) -> None:
    _write_json(
        sol_root / "SolutionMetadata.json",
        {
            "publisherId": "azuresentinel",
            "offerId": f"sentinel-{sol_root.name.lower().replace(' ', '-')}",
            "version": version,
            "support": {
                "tier": "Microsoft",
                "name": "Microsoft Corporation",
                "link": "https://aka.ms/sentinel-support",
            },
        },
    )
    data_payload: dict[str, Any] = {
        "Name": sol_root.name,
        "Author": "Microsoft",
        "Logo": '<img src="https://aka.ms/sentinel-logo.svg" width="75px" height="75px">',
        "Description": "Solution description with https://aka.ms/sentinel-docs link.",
        "Version": version,
    }
    if data_lists:
        data_payload.update(data_lists)
    _write_json(sol_root / "Data" / f"Solution_{sol_root.name.replace(' ', '')}.json", data_payload)

    (sol_root / "ReleaseNotes.md").write_text(
        f"| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
        f"|---|---|---|\n"
        f"| {version} | 19-10-2026 | Qualification release {version}. |\n",
        encoding="utf-8",
    )

    pkg_dir = sol_root / "Package"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / f"{version}.zip").write_bytes(b"PK\x03\x04dummy-zip")

    mt_payload: dict[str, Any] = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "resources": [
            {
                "type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
                "apiVersion": "2023-04-01-preview",
                "name": f"{sol_root.name}-pkg",
                "properties": {
                    "version": version,
                    **(
                        {
                            "requiredWorkloads": ["sentinel", "defender"],
                            "requiredDataConnectors": {"sentinel": ["DDOS"]},
                            "extra": {"customDetections": ["xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0"]},
                        }
                        if include_xdr_props
                        else {}
                    ),
                },
            }
        ],
    }
    _write_json(pkg_dir / "mainTemplate.json", mt_payload)
    _write_json(
        pkg_dir / "createUiDefinition.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/0.1.2-preview/CreateUIDefinition.MultiVm.json#",
            "handler": "Microsoft.Azure.CreateUIDef",
            "version": "0.1.2-preview",
            "parameters": {
                "basics": [{"name": "workspace", "type": "Microsoft.Solutions.ArmApiControl"}],
                "steps": [{"name": "workbooks", "label": "Workbooks", "elements": []}],
                "outputs": {},
            },
        },
    )


def _build_valid_workbook(path: Path) -> None:
    _write_json(
        path,
        {
            "version": "Notebook/1.0",
            "items": [
                {
                    "type": 3,
                    "name": "query-item-1",
                    "content": {
                        "version": "KqlItem/1.0",
                        "query": "AzureDiagnostics | summarize Count=count() by Category",
                    },
                }
            ],
        },
    )


def _build_valid_analytic_rule(path: Path, rule_id: str = "6e76fd9d-8104-41eb-bad3-26054a3ad5f0") -> str:
    rule_doc = {
        "id": rule_id,
        "name": "DDoS Attack IP Addresses - PPS Threshold",
        "description": "Identifies IP addresses exceeding PPS threshold.",
        "severity": "Medium",
        "kind": "Scheduled",
        "queryFrequency": "2h",
        "queryPeriod": "2h",
        "triggerOperator": "gt",
        "triggerThreshold": 0,
        "tactics": ["Impact"],
        "relevantTechniques": ["T1498"],
        "query": "AzureDiagnostics | where Category == 'DDoSMitigationFlowLogs' | project TimeGenerated, sourcePublicIpAddress_s",
        "entityMappings": [
            {
                "entityType": "IP",
                "fieldMappings": [{"identifier": "Address", "columnName": "sourcePublicIpAddress_s"}],
            }
        ],
    }
    _write_yaml(path, rule_doc)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_valid_xdr_detection(
    path: Path,
    *,
    source_rule_id: str = "6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
    source_rule_path: str = "Analytic Rules/AttackSourcesPPSThreshold.yaml",
    source_rule_sha256: str = "abc1234567890def",
    source_kind: str = "Scheduled",
    query_frequency: str = "PT2H",
    fallback_rationale: str | None = None,
) -> None:
    conv: dict[str, Any] = {
        "sourceRuleId": source_rule_id,
        "sourceRulePath": source_rule_path,
        "sourceRuleSha256": source_rule_sha256,
        "sourceKind": source_kind,
    }
    if fallback_rationale:
        conv["scheduleFallbackRationale"] = fallback_rationale
    _write_yaml(
        path,
        {
            "id": f"xdr-{source_rule_id}",
            "displayName": "DDoS Attack IP Addresses - PPS Threshold (XDR)",
            "severity": "Medium",
            "queryFrequency": query_frequency,
            "query": "AzureDiagnostics | where Category == 'DDoSMitigationFlowLogs' | project TimeGenerated, Timestamp=TimeGenerated, ReportId=tostring( _ItemId ), sourcePublicIpAddress_s",
            "entityMappings": [
                {
                    "entityType": "Ip",
                    "fieldMappings": [{"identifier": "Address", "columnName": "sourcePublicIpAddress_s"}],
                }
            ],
            "customDetails": {"SourceIp": "sourcePublicIpAddress_s"},
            "conversion": conv,
        },
    )


def _build_live_qualification_evidence(sol_dir: Path | None = None) -> dict[str, Any]:
    default_ar_q = "AzureDiagnostics | where Category == 'DDoSMitigationFlowLogs' | project TimeGenerated, sourcePublicIpAddress_s"
    default_xdr_q = "AzureDiagnostics | where Category == 'DDoSMitigationFlowLogs' | project TimeGenerated, Timestamp=TimeGenerated, ReportId=tostring( _ItemId ), sourcePublicIpAddress_s"
    verified_rules: list[dict[str, Any]] = [
        {
            "id": "6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
            "ruleId": "6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
            "status": "PASS",
            "querySha256": hashlib.sha256(default_ar_q.encode("utf-8")).hexdigest(),
        },
        {
            "id": "xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
            "ruleId": "xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
            "originalRuleId": "6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
            "status": "PASS",
            "querySha256": hashlib.sha256(default_xdr_q.encode("utf-8")).hexdigest(),
        },
    ]
    lifecycle_detections: list[dict[str, Any]] = [
        {
            "id": "6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
            "initialDisabled": True,
            "alertsFired": 1,
            "returnedToDisabled": True,
        },
        {
            "id": "xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
            "initialDisabled": True,
            "alertsFired": 1,
            "returnedToDisabled": True,
        },
    ]
    if sol_dir is not None and sol_dir.is_dir():
        for folder_name in ("Analytic Rules", "XDR Detections"):
            folder = sol_dir / folder_name
            if not folder.is_dir():
                continue
            for yml in sorted(folder.rglob("*.y*ml")):
                doc = yaml.safe_load(yml.read_text(encoding="utf-8-sig")) or {}
                props = doc.get("properties") if isinstance(doc.get("properties"), dict) else {}
                rid = str(doc.get("id") or props.get("id") or yml.stem).strip()
                orig_id = str(
                    doc.get("originalRuleId")
                    or props.get("originalRuleId")
                    or (doc.get("conversion") or {}).get("sourceRuleId")
                    or ""
                ).strip()
                q_str = str(
                    doc.get("query")
                    or ((props.get("queryCondition") or {}).get("queryText") if isinstance(props.get("queryCondition"), dict) else "")
                    or ""
                ).replace("\r\n", "\n").strip()
                if rid and q_str:
                    entry: dict[str, Any] = {
                        "id": rid,
                        "ruleId": rid,
                        "status": "PASS",
                        "querySha256": hashlib.sha256(q_str.encode("utf-8")).hexdigest(),
                    }
                    lifecycle_entry: dict[str, Any] = {
                        "id": rid,
                        "ruleId": rid,
                        "initialDisabled": True,
                        "alertsFired": 1,
                        "returnedToDisabled": True,
                    }
                    if orig_id:
                        entry["originalRuleId"] = orig_id
                        lifecycle_entry["originalRuleId"] = orig_id
                    verified_rules.append(entry)
                    lifecycle_detections.append(lifecycle_entry)
    return {
        "simulated": False,
        "dryRun": False,
        "kqlRuntimeVerifiedRules": verified_rules,
        "providerReceipts": [
            {"provider": "azure-arm", "operation": "deployment-readback", "mode": "live", "simulated": False},
            {"provider": "azure-monitor-dcr", "operation": "logs-ingestion", "mode": "live", "simulated": False},
            {"provider": "kusto-ah-la", "operation": "dual-surface-query", "mode": "live", "simulated": False},
            {"provider": "playwright-browser", "operation": "portal-traversal", "mode": "live", "simulated": False},
        ],
        "deployment": {
            "status": "passed",
            "deploymentVerified": True,
            "readbackVerified": True,
            "resourceCount": 4,
        },
        "mockIngestion": {
            "status": "passed",
            "mockIngestionVerified": True,
            "targetTables": ["AzureDiagnostics"],
            "recordCount": 6,
        },
        "alertLifecycle": {
            "detections": lifecycle_detections,
        },
        "workbookQualification": {
            "queries": [
                {"id": "query-item-1", "rowCount": 4, "status": "passed", "nonZeroScenarioValues": True},
            ]
        },
        "uiTraversal": {
            "domVerified": True,
            "tabsTraversed": 3,
            "screenshotCount": 3,
            "screenshots": [
                "Evidence/screenshots/detections-blade.png",
                "Evidence/screenshots/workbook-overview.png",
                "Evidence/screenshots/connector-blade.png",
            ],
        },
        "imageRendering": {
            "verifiedAssetCount": 2,
            "brokenAssetCount": 0,
            "minNaturalWidth": 75,
            "allHttp200": True,
            "assets": [
                {"url": "https://aka.ms/sentinel-logo.svg", "naturalWidth": 75, "httpStatus": 200},
            ],
        },
        "urlVerification": {
            "checkedCount": 3,
            "brokenCount": 0,
            "passed": True,
        },
        "dualSurfaceKql": {
            "dualSurfaceVerified": True,
            "sentinelKqlPassed": True,
            "xdrKqlPassed": True,
        },
        "alertParity": {
            "alertParityVerified": True,
            "pairCount": 1,
            "sentinelAlertCount": 1,
            "xdrAlertCount": 1,
        },
    }


def _assert_check_schema(results: dict[str, Any]) -> None:
    assert isinstance(results["checks"], list) and len(results["checks"]) >= 28
    for check in results["checks"]:
        missing = REQUIRED_CHECK_RESULT_FIELDS - set(check.keys())
        assert not missing, f"Check {check.get('id')} missing fields: {missing}"
        assert check["whatWeObserved"] and check["whatWeObserved"] != "PASS"
        assert isinstance(check["evidenceRefs"], list)
        for ref in check["evidenceRefs"]:
            assert "label" in ref and "path" in ref and "kind" in ref


def test_applicability_workbook_only_vs_hybrid_migration_vs_general_update(tmp_path: Path) -> None:
    # 1. Workbook-only non-migration solution
    wb_sol = tmp_path / "WorkbookOnlySol"
    _build_base_package(wb_sol, data_lists={"Workbooks": ["Workbooks/OnlyWb.json"]})
    _build_valid_workbook(wb_sol / "Workbooks" / "OnlyWb.json")

    wb_app = determine_pr_applicability(wb_sol)
    assert wb_app["isMigration"] is False
    assert "workbooks" in wb_app["detectedContentTypes"]
    assert "analytic-rules" not in wb_app["detectedContentTypes"]
    assert wb_app["checksById"]["VAL-WB-01"]["applicable"] is True
    assert wb_app["checksById"]["E2E-V03"]["applicable"] is True
    assert wb_app["checksById"]["E2E-Q04"]["applicable"] is True
    assert wb_app["checksById"]["VAL-AR-01"]["applicable"] is False
    assert wb_app["checksById"]["VAL-PKG-04"]["applicable"] is False
    assert wb_app["checksById"]["E2E-V02"]["applicable"] is False
    assert wb_app["checksById"]["E2E-Q02"]["applicable"] is False
    for mig_id in ("MIG-V01", "MIG-V02", "MIG-V03", "MIG-Q01", "E2E-Q03"):
        assert wb_app["checksById"][mig_id]["applicable"] is False

    # 2. Full hybrid migration solution
    hyb_sol = tmp_path / "HybridMigrationSol"
    _build_base_package(hyb_sol, include_xdr_props=True)
    sha = _build_valid_analytic_rule(hyb_sol / "Analytic Rules" / "Rule1.yaml")
    _build_valid_xdr_detection(
        hyb_sol / "XDR Detections" / "Rule1.yaml",
        source_rule_sha256=sha,
    )
    _build_valid_workbook(hyb_sol / "Workbooks" / "Wb1.json")
    _build_valid_workbook(hyb_sol / "XDR Workbooks" / "Wb1.json")
    _write_json(
        hyb_sol / "Data Connectors" / "Conn1.json",
        {"id": "Conn1", "title": "Conn", "publisher": "MS", "dataTypes": [{"name": "AzureDiagnostics"}], "instructionSteps": []},
    )
    _write_yaml(
        hyb_sol / "Parsers" / "Parser1.yaml",
        {"FunctionAlias": "MyParser", "FunctionQuery": "AzureDiagnostics | take 10"},
    )
    (hyb_sol / "Logos" / "logo.svg").parent.mkdir(parents=True, exist_ok=True)
    (hyb_sol / "Logos" / "logo.svg").write_text("<svg></svg>", encoding="utf-8")
    _write_json(hyb_sol / "mock.json", {"tables": {"AzureDiagnostics": [{"TimeGenerated": "2026-10-19T00:00:00Z"}]}})

    hyb_app = determine_pr_applicability(hyb_sol)
    assert hyb_app["isMigration"] is True
    for entry in BUILTIN_CHECK_CATALOG:
        cid = entry["id"]
        assert hyb_app["checksById"][cid]["applicable"] is True, f"Expected {cid} to be applicable in full hybrid migration"

    # 3. General non-migration solution update (Analytic Rules + Data Connectors, no XDR, no Workbooks)
    gen_sol = tmp_path / "GeneralSentinelUpdateSol"
    _build_base_package(gen_sol, data_lists={"Analytic Rules": ["Analytic Rules/Rule1.yaml"]})
    _build_valid_analytic_rule(gen_sol / "Analytic Rules" / "Rule1.yaml")
    _write_json(
        gen_sol / "Data Connectors" / "Conn1.json",
        {"id": "Conn1", "title": "Conn", "publisher": "MS", "dataTypes": [{"name": "AzureDiagnostics"}], "instructionSteps": []},
    )

    gen_app = determine_pr_applicability(gen_sol)
    assert gen_app["isMigration"] is False
    assert gen_app["checksById"]["VAL-AR-01"]["applicable"] is True
    assert gen_app["checksById"]["VAL-DC-01"]["applicable"] is True
    assert gen_app["checksById"]["E2E-V02"]["applicable"] is True
    assert gen_app["checksById"]["E2E-Q02"]["applicable"] is True
    assert gen_app["checksById"]["VAL-WB-01"]["applicable"] is False
    assert gen_app["checksById"]["E2E-V03"]["applicable"] is False
    assert gen_app["checksById"]["E2E-Q04"]["applicable"] is False
    assert gen_app["checksById"]["VAL-PKG-04"]["applicable"] is False
    for mig_id in ("MIG-V01", "MIG-V02", "MIG-V03", "MIG-Q01", "E2E-Q03"):
        assert gen_app["checksById"][mig_id]["applicable"] is False


def test_markdown_check_definition_loader_merges_with_builtin_catalog(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs" / "qualification"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "validation-checks.md").write_text(
        "# Validation Checks\n\n"
        "```yaml check-definition\n"
        "id: VAL-PKG-01\n"
        "checklist: validation\n"
        "title: Custom Reviewer Title for VAL-PKG-01 (>= 3.2.2)\n"
        "contentType: solution-package\n"
        "category: validation\n"
        "sourceChecklist: custom-doc\n"
        "```\n",
        encoding="utf-8",
    )
    catalog = load_check_catalog(docs_dir=docs_dir)
    by_id = {c["id"]: c for c in catalog}
    assert len(catalog) == len(BUILTIN_CHECK_CATALOG)
    assert by_id["VAL-PKG-01"]["title"] == "Custom Reviewer Title for VAL-PKG-01 (>= 3.2.2)"
    assert by_id["VAL-PKG-01"]["sourceChecklist"] == "custom-doc"


def test_e2e_v01_subject_inventory_full_vs_acknowledged_vs_unacknowledged(tmp_path: Path) -> None:
    sol = tmp_path / "InventorySol"
    _build_base_package(
        sol,
        data_lists={"Workbooks": ["Workbooks/PackagedWb.json"]},
    )
    _build_valid_workbook(sol / "Workbooks" / "PackagedWb.json")
    _write_json(sol / "mock.json", {"tables": {"AzureDiagnostics": [{"TimeGenerated": "2026-10-19T00:00:00Z"}]}})

    # Case 1: 100% of discovered workbooks are packaged -> PASS
    res_full = run_pr_qualification_checks(sol, run_qualification=False)
    assert res_full["checksById"]["E2E-V01"]["status"] == "PASS"
    assert res_full["validationStatus"] == "Validated"
    assert res_full["qualificationStatus"] == "Not Run"

    # Add a second workbook on disk that is NOT listed in Data/Solution_*.json
    _build_valid_workbook(sol / "Workbooks" / "LegacyExcludedWb.json")

    # Case 2: Unacknowledged exclusion -> FAIL
    res_missing = run_pr_qualification_checks(sol, run_qualification=False)
    assert res_missing["checksById"]["E2E-V01"]["status"] == "FAIL"
    assert "LegacyExcludedWb.json" in res_missing["checksById"]["E2E-V01"]["whatWeObserved"]
    assert res_missing["validationStatus"] == "Validation Failed"

    # Case 3: Exclusion acknowledged via acknowledged_exclusions -> PASS
    res_ack_param = run_pr_qualification_checks(
        sol,
        run_qualification=False,
        acknowledged_exclusions=[
            {"path": "Workbooks/LegacyExcludedWb.json", "rationale": "Deprecated v1 workbook intentionally excluded"}
        ],
    )
    assert res_ack_param["checksById"]["E2E-V01"]["status"] == "PASS"
    assert res_ack_param["validationStatus"] == "Validated"

    # Case 4: Exclusion acknowledged in Evidence/decision-manifest.json -> PASS
    _write_json(
        sol / "Evidence" / "decision-manifest.json",
        {
            "schemaVersion": "decision-manifest-v1",
            "decisions": [
                {
                    "id": "workbook_selection:LegacyExcludedWb.json",
                    "scope": "workbook_selection",
                    "itemId": "Workbooks/LegacyExcludedWb.json",
                    "decision": "excluded",
                    "rationale": "Excluded by author in decision-manifest.json.",
                }
            ],
        },
    )
    res_ack_manifest = run_pr_qualification_checks(sol, run_qualification=False)
    assert res_ack_manifest["checksById"]["E2E-V01"]["status"] == "PASS"
    assert res_ack_manifest["validationStatus"] == "Validated"


def test_e2e_v02_and_e2e_v03_offline_mock_data_validation(tmp_path: Path) -> None:
    sol = tmp_path / "MockValidationSol"
    _build_base_package(
        sol,
        data_lists={
            "Analytic Rules": ["Analytic Rules/Rule1.yaml"],
            "Workbooks": ["Workbooks/Wb1.json"],
        },
    )
    _build_valid_analytic_rule(sol / "Analytic Rules" / "Rule1.yaml")
    _build_valid_workbook(sol / "Workbooks" / "Wb1.json")

    # Without mock.json -> both E2E-V02 and E2E-V03 fail
    res_no_mock = run_pr_qualification_checks(sol, run_qualification=False)
    assert res_no_mock["checksById"]["E2E-V02"]["status"] == "FAIL"
    assert res_no_mock["checksById"]["E2E-V03"]["status"] == "FAIL"

    # With malformed mock.json -> both fail
    (sol / "mock.json").write_text("{bad json", encoding="utf-8")
    res_bad_mock = run_pr_qualification_checks(sol, run_qualification=False)
    assert res_bad_mock["checksById"]["E2E-V02"]["status"] == "FAIL"
    assert res_bad_mock["checksById"]["E2E-V03"]["status"] == "FAIL"

    # With schema-valid mock.json -> both pass
    _write_json(
        sol / "mock.json",
        {
            "tables": {
                "AzureDiagnostics": [
                    {"TimeGenerated": "2026-10-19T12:00:00Z", "Category": "DDoSMitigationFlowLogs", "sourcePublicIpAddress_s": "203.0.113.5"}
                ]
            }
        },
    )
    res_good_mock = run_pr_qualification_checks(sol, run_qualification=False)
    assert res_good_mock["checksById"]["E2E-V02"]["status"] == "PASS"
    assert res_good_mock["checksById"]["E2E-V03"]["status"] == "PASS"
    assert res_good_mock["validationStatus"] == "Validated"


def test_qual_00_prerequisite_and_e2e_g01_no_simulated_fallback(tmp_path: Path) -> None:
    sol = tmp_path / "QualGateSol"
    # Version 3.2.1 (< 3.2.2) causes VAL-PKG-01 to FAIL -> validationStatus == "Validation Failed"
    _build_base_package(sol, version="3.2.1", data_lists={"Workbooks": ["Workbooks/Wb1.json"]})
    _build_valid_workbook(sol / "Workbooks" / "Wb1.json")
    _write_json(sol / "mock.json", {"tables": {"AzureDiagnostics": [{"TimeGenerated": "2026-10-19T00:00:00Z"}]}})

    live_ev = _build_live_qualification_evidence()
    res_blocked = run_pr_qualification_checks(sol, qualification_evidence=live_ev)
    assert res_blocked["checksById"]["VAL-PKG-01"]["status"] == "FAIL"
    assert res_blocked["validationStatus"] == "Validation Failed"
    assert res_blocked["checksById"]["QUAL-00"]["status"] == "FAIL"
    assert res_blocked["qualificationStatus"] == "Qualification Failed"

    # Upgrade to 3.2.2 -> validationStatus == "Validated", QUAL-00 passes
    (sol / "Package" / "3.2.1.zip").unlink()
    _build_base_package(sol, version="3.2.2", data_lists={"Workbooks": ["Workbooks/Wb1.json"]})

    # Supply simulated evidence -> E2E-G01 fails closed
    sim_ev = {**live_ev, "simulated": True, "providerMode": "simulated"}
    res_sim = run_pr_qualification_checks(sol, qualification_evidence=sim_ev)
    assert res_sim["validationStatus"] == "Validated"
    assert res_sim["checksById"]["QUAL-00"]["status"] == "PASS"
    assert res_sim["checksById"]["E2E-G01"]["status"] == "FAIL"
    assert res_sim["qualificationStatus"] == "Qualification Failed"

    # Supply real live provider receipts -> E2E-G01 passes and solution is Qualified
    res_live = run_pr_qualification_checks(sol, qualification_evidence=live_ev)
    assert res_live["checksById"]["QUAL-00"]["status"] == "PASS"
    assert res_live["checksById"]["E2E-G01"]["status"] == "PASS"
    assert res_live["checksById"]["QUAL-HR-01"]["status"] == "HUMAN_REVIEW_REQUIRED"
    assert res_live["qualificationStatus"] == "Qualified"
    _assert_check_schema(res_live)


def test_qualification_checks_q01_q02_q03_q04_q05_q06_and_author_waivers(tmp_path: Path) -> None:
    sol = tmp_path / "FullHybridQualSol"
    _build_base_package(
        sol,
        version="3.2.2",
        include_xdr_props=True,
        data_lists={
            "Analytic Rules": ["Analytic Rules/Rule1.yaml"],
            "Workbooks": ["Workbooks/Wb1.json"],
        },
    )
    sha = _build_valid_analytic_rule(sol / "Analytic Rules" / "Rule1.yaml")
    _build_valid_xdr_detection(sol / "XDR Detections" / "Rule1.yaml", source_rule_sha256=sha)
    _build_valid_workbook(sol / "Workbooks" / "Wb1.json")
    _build_valid_workbook(sol / "XDR Workbooks" / "Wb1.json")
    _write_json(sol / "mock.json", {"tables": {"AzureDiagnostics": [{"TimeGenerated": "2026-10-19T00:00:00Z"}]}})

    # Test failing E2E-Q02 (not returned to disabled), E2E-Q04 (rowCount == 0), E2E-Q06 (broken image), E2E-Q03 (parity false)
    bad_ev = _build_live_qualification_evidence()
    bad_ev["alertLifecycle"] = {
        "detections": [{"id": "Rule1", "initialDisabled": True, "alertsFired": 1, "returnedToDisabled": False}]
    }
    bad_ev["workbookQualification"] = {
        "queries": [{"id": "q1", "rowCount": 0, "status": "passed"}]
    }
    bad_ev["imageRendering"] = {
        "verifiedAssetCount": 1,
        "brokenAssetCount": 1,
        "minNaturalWidth": 0,
        "allHttp200": False,
    }
    bad_ev["alertParity"] = {"alertParityVerified": False}

    res_bad = run_pr_qualification_checks(sol, qualification_evidence=bad_ev)
    assert res_bad["checksById"]["E2E-Q01"]["status"] == "PASS"
    assert res_bad["checksById"]["E2E-Q02"]["status"] == "FAIL"
    assert res_bad["checksById"]["E2E-Q04"]["status"] == "FAIL"
    assert res_bad["checksById"]["E2E-Q05"]["status"] == "PASS"
    assert res_bad["checksById"]["E2E-Q06"]["status"] == "FAIL"
    assert res_bad["checksById"]["E2E-Q03"]["status"] == "FAIL"
    assert res_bad["qualificationStatus"] == "Qualification Failed"
    assert res_bad["migrationStatus"] == "Migration Failed"

    # Now waive the failing checks with author exceptions -> Conditionally Qualified & Conditionally Migrated
    waivers = [
        {
            "checkId": "E2E-Q02",
            "authorJustification": "Lab automation lock prevented disable call; manually disabled in portal.",
            "supportingEvidenceRef": "Evidence/screenshots/manual-disable-proof.png",
            "author": "@contoso-author",
        },
        {
            "checkId": "E2E-Q04",
            "authorJustification": "ARG cluster inventory query requires production subscription resource.",
            "supportingEvidenceRef": "Evidence/decision-manifest.json",
            "author": "@contoso-author",
        },
        {
            "checkId": "E2E-Q06",
            "authorJustification": "External CDN logo rate-limited in headless runner; verified locally.",
            "supportingEvidenceRef": "Evidence/screenshots/logo-verified.png",
            "author": "@contoso-author",
        },
        {
            "checkId": "E2E-Q03",
            "authorJustification": "Cloud latency delayed XDR alert correlation by 1 window; verified in AH.",
            "supportingEvidenceRef": "Evidence/ah-parity-receipt.json",
            "author": "@contoso-author",
        },
    ]
    res_waived = run_pr_qualification_checks(
        sol,
        qualification_evidence=bad_ev,
        author_exceptions=waivers,
    )
    for cid in ("E2E-Q02", "E2E-Q04", "E2E-Q06", "E2E-Q03"):
        chk = res_waived["checksById"][cid]
        assert chk["status"] == "WAIVED_WITH_AUTHOR_EVIDENCE"
        assert chk["reviewerActionRequired"] is True
        assert chk["authorException"]["originalStatus"] == "FAIL"
        assert chk["authorException"]["author"] == "@contoso-author"
    assert res_waived["qualificationStatus"] == "Conditionally Qualified"
    assert res_waived["migrationStatus"] == "Conditionally Migrated"

    # Also verify validation waiver -> Partially Validated -> Conditionally Qualified
    (sol / "mock.json").unlink()
    res_part_val = run_pr_qualification_checks(
        sol,
        qualification_evidence=_build_live_qualification_evidence(),
        author_exceptions=[
            {
                "checkId": "E2E-V02",
                "authorJustification": "Shared mock ingested from workspace fixture.",
                "supportingEvidenceRef": "Evidence/workspace-fixture.json",
            },
            {
                "checkId": "E2E-V03",
                "authorJustification": "Shared mock ingested from workspace fixture.",
                "supportingEvidenceRef": "Evidence/workspace-fixture.json",
            },
        ],
    )
    assert res_part_val["validationStatus"] == "Partially Validated"
    assert res_part_val["checksById"]["QUAL-00"]["status"] == "PASS"
    assert res_part_val["qualificationStatus"] == "Conditionally Qualified"
    assert res_part_val["migrationStatus"] == "Migration Verified"


def test_real_solution_azure_ddos_protection_integration(tmp_path: Path) -> None:
    """Integration test against real repository solution Solutions/Azure DDoS Protection (legacy 2.0.4 + 3.2.2 copy)."""
    assert DDOS_SOLUTION_PATH.is_dir(), f"Expected {DDOS_SOLUTION_PATH} to exist in repository"

    # 1. Baseline inspection of legacy 2.0.4 state in an isolated copy
    legacy_copy = tmp_path / "legacy" / "Azure DDoS Protection"
    shutil.copytree(
        DDOS_SOLUTION_PATH,
        legacy_copy,
        ignore=shutil.ignore_patterns("XDR Detections", "XDR Workbooks", "Sample Data", "Evidence", "Logs", "ReleaseNotes.md", "3.2.2.zip"),
    )
    legacy_meta = json.loads((legacy_copy / "SolutionMetadata.json").read_text(encoding="utf-8-sig"))
    legacy_meta.pop("version", None)
    _write_json(legacy_copy / "SolutionMetadata.json", legacy_meta)
    legacy_data_file = legacy_copy / "Data" / "Solution_AzureDDoSProtection.json"
    legacy_data_doc = json.loads(legacy_data_file.read_text(encoding="utf-8-sig"))
    legacy_data_doc["Version"] = "2.0.4"
    _write_json(legacy_data_file, legacy_data_doc)

    raw_app = determine_pr_applicability(legacy_copy)
    assert raw_app["solutionName"] == "Azure DDoS Protection"
    assert raw_app["isMigration"] is False
    for expected_ct in ("solution-package", "analytic-rules", "workbooks", "data-connectors", "logos"):
        assert expected_ct in raw_app["detectedContentTypes"]

    raw_run = run_pr_qualification_checks(legacy_copy, run_qualification=False)
    # Legacy version is 2.0.4 (< 3.2.2) and lacks ReleaseNotes.md, so VAL-PKG-01 and VAL-PKG-02 must FAIL
    assert raw_run["checksById"]["VAL-PKG-01"]["status"] == "FAIL"
    assert "2.0.4" in raw_run["checksById"]["VAL-PKG-01"]["whatWeObserved"]
    assert raw_run["checksById"]["VAL-PKG-02"]["status"] == "FAIL"
    # Existing Analytic Rules, Workbooks, Data Connectors, URLs, and Inventory (E2E-V01) are valid
    assert raw_run["checksById"]["VAL-AR-01"]["status"] == "PASS"
    assert raw_run["checksById"]["VAL-WB-01"]["status"] == "PASS"
    assert raw_run["checksById"]["VAL-DC-01"]["status"] == "PASS"
    assert raw_run["checksById"]["E2E-V01"]["status"] == "PASS"

    # 2. Copy Solutions/Azure DDoS Protection into tmp_path and upgrade to target version 3.2.2 with XDR migration
    ddos_copy = tmp_path / "Azure DDoS Protection"
    shutil.copytree(legacy_copy, ddos_copy)

    # Update version quartet to 3.2.2
    meta = json.loads((ddos_copy / "SolutionMetadata.json").read_text(encoding="utf-8-sig"))
    meta["version"] = "3.2.2"
    _write_json(ddos_copy / "SolutionMetadata.json", meta)

    data_file = ddos_copy / "Data" / "Solution_AzureDDoSProtection.json"
    data_doc = json.loads(data_file.read_text(encoding="utf-8-sig"))
    data_doc["Version"] = "3.2.2"
    _write_json(data_file, data_doc)

    (ddos_copy / "ReleaseNotes.md").write_text(
        "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
        "|---|---|---|\n"
        "| 3.2.2 | 19-10-2026 | Migrated Azure DDoS Protection detections to Defender XDR (3.2.2). |\n",
        encoding="utf-8",
    )
    (ddos_copy / "Package" / "3.2.2.zip").write_bytes(b"PK\x03\x04ddos-3.2.2")

    # Add XDR metadata to Package/mainTemplate.json and add migrated XDR Detections for both DDoS rules
    mt_file = ddos_copy / "Package" / "mainTemplate.json"
    mt_doc = json.loads(mt_file.read_text(encoding="utf-8-sig"))
    mt_doc["Metadata"] = {
        "requiredWorkloads": ["sentinel", "defender"],
        "requiredDataConnectors": {"sentinel": ["DDOS"]},
        "extra": {"customDetections": ["xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0", "xdr-2222fd9d-8104-41eb-bad3-26054a3ad5f1"]},
    }
    _write_json(mt_file, mt_doc)

    for ar_path in sorted((ddos_copy / "Analytic Rules").glob("*.yaml")):
        ar_doc = yaml.safe_load(ar_path.read_text(encoding="utf-8-sig"))
        rid = str(ar_doc["id"])
        sha = hashlib.sha256(ar_path.read_bytes()).hexdigest()
        _build_valid_xdr_detection(
            ddos_copy / "XDR Detections" / ar_path.name,
            source_rule_id=rid,
            source_rule_path=f"Analytic Rules/{ar_path.name}",
            source_rule_sha256=sha,
        )

    _write_json(
        ddos_copy / "mock.json",
        {
            "tables": {
                "AzureDiagnostics": [
                    {
                        "TimeGenerated": "2026-10-19T12:00:00Z",
                        "ResourceType": "PUBLICIPADDRESSES",
                        "Category": "DDoSMitigationFlowLogs",
                        "destPublicIpAddress_s": "198.51.100.10",
                        "sourcePublicIpAddress_s": "203.0.113.99",
                    }
                ]
            }
        },
    )

    ddos_qual = run_pr_qualification_checks(
        ddos_copy,
        qualification_evidence=_build_live_qualification_evidence(ddos_copy),
    )
    _assert_check_schema(ddos_qual)
    assert ddos_qual["isMigration"] is True
    assert ddos_qual["checksById"]["VAL-PKG-01"]["status"] == "PASS"
    assert ddos_qual["checksById"]["VAL-PKG-02"]["status"] == "PASS"
    assert ddos_qual["checksById"]["VAL-PKG-04"]["status"] == "PASS"
    assert ddos_qual["checksById"]["E2E-V01"]["status"] == "PASS"
    assert ddos_qual["checksById"]["E2E-V02"]["status"] == "PASS"
    assert ddos_qual["checksById"]["E2E-V03"]["status"] == "PASS"
    assert ddos_qual["validationStatus"] == "Validated"
    assert ddos_qual["qualificationStatus"] == "Qualified"
    assert ddos_qual["migrationStatus"] == "Migration Verified"


def test_cli_pr_qualify_command_and_report_generation(tmp_path: Path, capsys: Any) -> None:
    """Verify `pr-qualify` CLI subcommand, flags, JSON stdout summary, and generated report files."""
    ddos_copy = tmp_path / "Azure DDoS Protection"
    shutil.copytree(
        DDOS_SOLUTION_PATH,
        ddos_copy,
        ignore=shutil.ignore_patterns("Sample Data", "Evidence", "Logs"),
    )

    # Bump version quartet to 3.2.2
    meta = json.loads((ddos_copy / "SolutionMetadata.json").read_text(encoding="utf-8-sig"))
    meta["version"] = "3.2.2"
    _write_json(ddos_copy / "SolutionMetadata.json", meta)

    data_file = ddos_copy / "Data" / "Solution_AzureDDoSProtection.json"
    data_doc = json.loads(data_file.read_text(encoding="utf-8-sig"))
    data_doc["Version"] = "3.2.2"
    _write_json(data_file, data_doc)

    (ddos_copy / "ReleaseNotes.md").write_text(
        "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
        "|---|---|---|\n"
        "| 3.2.2 | 19-10-2026 | Migrated Azure DDoS Protection detections to Defender XDR (3.2.2). |\n",
        encoding="utf-8",
    )
    (ddos_copy / "Package" / "3.2.2.zip").write_bytes(b"PK\x03\x04ddos-3.2.2")

    mt_file = ddos_copy / "Package" / "mainTemplate.json"
    mt_doc = json.loads(mt_file.read_text(encoding="utf-8-sig"))
    mt_doc["Metadata"] = {
        "requiredWorkloads": ["sentinel", "defender"],
        "requiredDataConnectors": {"sentinel": ["DDOS"]},
        "extra": {"customDetections": ["xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0"]},
    }
    _write_json(mt_file, mt_doc)

    for ar_path in sorted((ddos_copy / "Analytic Rules").glob("*.yaml")):
        ar_doc = yaml.safe_load(ar_path.read_text(encoding="utf-8-sig"))
        rid = str(ar_doc["id"])
        sha = hashlib.sha256(ar_path.read_bytes()).hexdigest()
        _build_valid_xdr_detection(
            ddos_copy / "XDR Detections" / ar_path.name,
            source_rule_id=rid,
            source_rule_path=f"Analytic Rules/{ar_path.name}",
            source_rule_sha256=sha,
        )

    # Add an extra unreferenced workbook and acknowledge its exclusion via --acknowledged-exclusions-file
    _build_valid_workbook(ddos_copy / "Workbooks" / "LegacyDDoSWorkbook.json")
    exclusions_file = tmp_path / "acknowledged-exclusions.json"
    _write_json(exclusions_file, ["Workbooks/LegacyDDoSWorkbook.json"])

    # Provide live evidence where E2E-Q04 has 0 rows, and waive E2E-Q04 + E2E-V02 + E2E-V03 via --waivers-file
    evidence_dir = tmp_path / "evidence-input"
    ev_payload = _build_live_qualification_evidence(ddos_copy)
    ev_payload["workbookQualification"] = {
        "queries": [{"id": "ddos-wb-q1", "rowCount": 0, "status": "passed"}]
    }
    _write_json(evidence_dir / "qualification-evidence.json", ev_payload)

    waivers_file = tmp_path / "waivers.json"
    _write_json(
        waivers_file,
        {
            "E2E-V02": {
                "authorJustification": "Shared AzureDiagnostics DDoS fixture ingested directly in lab workspace.",
                "supportingEvidenceRef": "Evidence/dcr-ingestion-receipt.json",
                "knownLimitationCategory": "shared-workspace-fixture",
            },
            "E2E-V03": {
                "authorJustification": "Workbook queries validated against shared AzureDiagnostics fixture in lab.",
                "supportingEvidenceRef": "Evidence/dcr-ingestion-receipt.json",
                "knownLimitationCategory": "shared-workspace-fixture",
            },
            "E2E-Q04": {
                "authorJustification": "ARG PublicIP protection status tile requires active DDoS Standard plan on subscription.",
                "supportingEvidenceRef": "Evidence/workbook-arg-limitation.md",
                "knownLimitationCategory": "subscription-sku-prerequisite",
            },
        },
    )

    out_dir = tmp_path / "pr-qual-out"
    rc = cli_main(
        [
            "pr-qualify",
            "--solution",
            str(ddos_copy),
            "--mode",
            "full",
            "--is-migration",
            "--output-dir",
            str(out_dir),
            "--waivers-file",
            str(waivers_file),
            "--acknowledged-exclusions-file",
            str(exclusions_file),
            "--evidence-dir",
            str(evidence_dir),
            "--target-version",
            "3.2.2",
        ]
    )
    assert rc == 0

    captured = capsys.readouterr()
    summary_json = json.loads(captured.out)
    assert summary_json["solutionName"] == "Azure DDoS Protection"
    assert summary_json["solutionVersion"] == "3.2.2"
    assert summary_json["validationStatus"] == "Partially Validated"
    assert summary_json["qualificationStatus"] == "Conditionally Qualified"
    assert summary_json["migrationStatus"] == "Migration Verified"
    assert summary_json["overallVerdict"] == "Conditionally Qualified"

    result_json_path = Path(summary_json["resultJsonPath"])
    html_report_path = Path(summary_json["htmlReportPath"])
    md_summary_path = Path(summary_json["markdownSummaryPath"])

    assert result_json_path == out_dir / "pr-qualification-result.json"
    assert html_report_path == out_dir / "qualification-report.html"
    assert md_summary_path == out_dir / "qualification-summary.md"
    assert result_json_path.is_file()
    assert html_report_path.is_file()
    assert md_summary_path.is_file()

    persisted_result = json.loads(result_json_path.read_text(encoding="utf-8"))
    assert persisted_result["checksById"]["E2E-V01"]["status"] == "PASS"
    assert persisted_result["checksById"]["E2E-Q04"]["status"] == "WAIVED_WITH_AUTHOR_EVIDENCE"
    assert (
        persisted_result["checksById"]["E2E-Q04"]["authorException"]["knownLimitationCategory"]
        == "subscription-sku-prerequisite"
    )
    assert "Azure DDoS Protection" in html_report_path.read_text(encoding="utf-8")
    assert "Conditionally Qualified" in md_summary_path.read_text(encoding="utf-8")


def test_ddos_solution_nested_xdr_detections_and_sample_data(tmp_path: Path) -> None:
    """Verify Solutions/Azure DDoS Protection with nested XDR Detections and Sample Data passes VAL-AR-01, E2E-V02, E2E-V03, MIG-V01, MIG-V02, and MIG-V03."""
    ddos_dir = tmp_path / "Azure DDoS Protection"
    shutil.copytree(
        DDOS_SOLUTION_PATH,
        ddos_dir,
        ignore=shutil.ignore_patterns("Sample Data", "Evidence", "Logs"),
    )
    for ar_path in sorted((ddos_dir / "Analytic Rules").glob("*.yaml")):
        ar_doc = yaml.safe_load(ar_path.read_text(encoding="utf-8-sig"))
        rid = str(ar_doc["id"])
        sha = hashlib.sha256(ar_path.read_bytes()).hexdigest()
        _build_valid_xdr_detection(
            ddos_dir / "XDR Detections" / ar_path.name,
            source_rule_id=rid,
            source_rule_path=f"Solutions/Azure DDoS Protection/Analytic Rules/{ar_path.name}",
            source_rule_sha256=sha,
        )
    _write_json(
        ddos_dir / "Sample Data" / "Tables" / "AzureDiagnostics_mock.json",
        [
            {
                "TimeGenerated": "2026-10-19T12:00:00Z",
                "ResourceType": "PUBLICIPADDRESSES",
                "Category": "DDoSMitigationReports",
                "destPublicIpAddress_s": "198.51.100.10",
                "sourcePublicIpAddress_s": "203.0.113.99",
            }
        ],
    )
    res = run_pr_qualification_checks(ddos_dir, run_qualification=False)
    for cid in ("VAL-AR-01", "E2E-V02", "E2E-V03", "MIG-V01", "MIG-V02", "MIG-V03"):
        assert res["checksById"][cid]["status"] == "PASS", (
            f"Expected {cid} to PASS on Solutions/Azure DDoS Protection, got "
            f"{res['checksById'][cid]['status']}: {res['checksById'][cid]['whyPassedOrFailed']}"
        )


def test_direct_override_blocks_validation_and_unapproved_human_review(tmp_path: Path) -> None:
    """Ensure qualification_evidence.checks cannot bypass failing validation checks or unapproved human review."""
    sol = tmp_path / "BypassAttemptSol"
    # Legacy 3.2.1 fails VAL-PKG-01
    _build_base_package(sol, version="3.2.1", data_lists={"Workbooks": ["Workbooks/Wb1.json"]})
    _build_valid_workbook(sol / "Workbooks" / "Wb1.json")
    _write_json(sol / "mock.json", {"tables": {"AzureDiagnostics": [{"TimeGenerated": "2026-10-19T00:00:00Z"}]}})

    forged_ev = _build_live_qualification_evidence()
    forged_ev["checks"] = {
        "VAL-PKG-01": {
            "status": "PASS",
            "whatWeObserved": "Forged validation pass",
            "evidenceRefs": [{"label": "forged", "path": "SolutionMetadata.json"}],
        },
        "QUAL-HR-01": {
            "status": "PASS",
            "whatWeObserved": "Forged human review pass without reviewer sign-off",
            "evidenceRefs": [{"label": "forged", "path": "Evidence/qualification-report.html"}],
        },
    }
    res = run_pr_qualification_checks(sol, qualification_evidence=forged_ev)
    assert res["checksById"]["VAL-PKG-01"]["status"] == "FAIL"
    assert res["validationStatus"] == "Validation Failed"
    assert res["checksById"]["QUAL-HR-01"]["status"] == "HUMAN_REVIEW_REQUIRED"


def test_kql_runtime_verified_rules_projection_and_val_ci_01_override(tmp_path: Path) -> None:
    """Verify kqlRuntimeVerifiedRules projection, QUAL-RUNTIME-01 evaluation, and VAL-CI-01 static KQL override."""
    sol = tmp_path / "RuntimeVerifiedSol"
    _build_base_package(
        sol,
        version="3.2.2",
        include_xdr_props=True,
        data_lists={
            "Analytic Rules": ["Analytic Rules/Rule1.yaml"],
            "XDR Detections": ["XDR Detections/Rule1.yaml"],
        },
    )
    ar_path = sol / "Analytic Rules" / "Rule1.yaml"
    rule_id = "6e76fd9d-8104-41eb-bad3-26054a3ad5f0"
    ar_sha = _build_valid_analytic_rule(ar_path, rule_id=rule_id)
    xdr_path = sol / "XDR Detections" / "Rule1.yaml"
    _build_valid_xdr_detection(
        xdr_path,
        source_rule_id=rule_id,
        source_rule_path="Analytic Rules/Rule1.yaml",
        source_rule_sha256=ar_sha,
    )
    _write_json(
        sol / "Sample Data" / "Tables" / "AzureDiagnostics_mock.json",
        [
            {
                "TimeGenerated": "2026-10-19T12:00:00Z",
                "ResourceType": "PUBLICIPADDRESSES",
                "Category": "DDoSMitigationReports",
                "destPublicIpAddress_s": "198.51.100.10",
                "sourcePublicIpAddress_s": "203.0.113.99",
            }
        ],
    )

    ar_doc = yaml.safe_load(ar_path.read_text(encoding="utf-8"))
    ar_query_sha = hashlib.sha256(str(ar_doc["query"]).strip().encode("utf-8")).hexdigest()
    xdr_doc = yaml.safe_load(xdr_path.read_text(encoding="utf-8"))
    xdr_raw_q = xdr_doc.get("query") or ((xdr_doc.get("properties") or {}).get("queryCondition") or {}).get("queryText")
    xdr_query_sha = hashlib.sha256(str(xdr_raw_q).strip().encode("utf-8")).hexdigest()

    qual_ev = _build_live_qualification_evidence()
    qual_ev["runtimeKql"] = {
        "status": "passed",
        "passed": True,
        "queries": [
            {
                "id": rule_id,
                "status": "PASS",
                "querySha256": ar_query_sha,
            },
            {
                "id": f"xdr-{rule_id}",
                "originalRuleId": rule_id,
                "status": "PASS",
                "querySha256": xdr_query_sha,
            },
        ],
    }
    qual_ev["ciChecks"] = {
        "passed": False,
        "reason": "Static KQL analyzer reported KS107/KS141",
        "kqlStaticErrors": [
            {
                "id": f"xdr-{rule_id}",
                "originalRuleId": rule_id,
                "code": "KS107",
                "querySha256": xdr_query_sha,
            },
            {
                "id": rule_id,
                "code": "KS141",
                "querySha256": ar_query_sha,
            },
        ],
    }
    wf_state = {
        "workflowProfile": "qualification",
        "operatorHash": "abcdef0123456789",
        "stages": {
            "conversion": {
                "startedAt": "2026-10-19T10:00:00Z",
                "completedAt": "2026-10-19T10:05:00Z",
            },
            "validation": {
                "attempts": 1,
                "completedAt": "2026-10-19T10:10:00Z",
            },
            "alertParity": {
                "status": "passed",
                "completedAt": "2026-10-19T10:25:00Z",
            },
            "packaging": {
                "completedAt": "2026-10-19T10:30:00Z",
            },
        },
    }

    res = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev,
        pr_number=4242,
        run_number=1,
    )

    # Todo #5 assertions
    verified = res["kqlRuntimeVerifiedRules"]
    assert len(verified) == 2
    verified_ids = {v["id"]: v for v in verified}
    assert rule_id in verified_ids
    assert verified_ids[rule_id]["querySha256"] == ar_query_sha
    assert verified_ids[rule_id]["status"] == "PASS"
    assert f"xdr-{rule_id}" in verified_ids
    assert verified_ids[f"xdr-{rule_id}"]["querySha256"] == xdr_query_sha
    assert verified_ids[f"xdr-{rule_id}"]["originalRuleId"] == rule_id

    assert res["checksById"]["VAL-CI-01"]["status"] == "PASS"
    assert "kqlRuntimeVerifiedRules" in res["checksById"]["VAL-CI-01"]["whatWeObserved"]
    assert "kqlRuntimeVerifiedRules" in res["checksById"]["VAL-CI-01"]["whyPassedOrFailed"]
    assert res["checksById"]["QUAL-RUNTIME-01"]["status"] == "PASS"

    # Todo #6 assertions
    assert res["runNumber"] == 1
    assert res["passesPerSolution"] == 1
    assert res["prNumber"] == 4242
    assert res["firstPassPassed"] is True
    assert res["operatorHash"] == "abcdef0123456789"
    assert res["workflowProfile"] == "qualification"
    assert res["stageTimestamps"] == {
        "convertingStartedAtUtc": "2026-10-19T10:00:00Z",
        "convertingCompletedAtUtc": "2026-10-19T10:05:00Z",
        "validationCompletedAtUtc": "2026-10-19T10:10:00Z",
        "qualificationCompletedAtUtc": "2026-10-19T10:25:00Z",
        "packagedAtUtc": "2026-10-19T10:30:00Z",
    }
    assert res["verdict"] == "Qualified"
    assert isinstance(res["verdictReasons"], list)

    # Ensure SYN* and non-allowlisted KS* (e.g., KS005) syntax errors and unrelated string errors are never overridden in VAL-CI-01
    qual_ev_syn = dict(qual_ev)
    qual_ev_syn["ciChecks"] = {
        "passed": False,
        "reason": "Syntax error SYN001",
        "kqlStaticErrors": [
            {
                "id": rule_id,
                "code": "SYN001",
                "querySha256": ar_query_sha,
            }
        ],
    }
    res_syn = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_syn,
        run_number=2,
    )
    assert res_syn["checksById"]["VAL-CI-01"]["status"] == "FAIL"
    assert res_syn["firstPassPassed"] is False
    assert res_syn["verdict"] == "Failed"
    assert any(r.startswith("VAL-CI-01 (FAIL):") for r in res_syn["verdictReasons"])

    qual_ev_ks005 = dict(qual_ev)
    qual_ev_ks005["ciChecks"] = {
        "passed": False,
        "reason": "KQL syntax error KS005",
        "kqlStaticErrors": [
            {
                "id": f"xdr-{rule_id}",
                "code": "KS005",
                "querySha256": xdr_query_sha,
            }
        ],
    }
    res_ks005 = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_ks005,
        run_number=1,
    )
    assert res_ks005["checksById"]["VAL-CI-01"]["status"] == "FAIL"

    qual_ev_str_err = dict(qual_ev)
    qual_ev_str_err["ciChecks"] = {
        "passed": False,
        "reason": "ARM template validation failed",
        "errors": ["ARM template deployment validation failed on mainTemplate.json"],
    }
    res_str_err = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_str_err,
        run_number=1,
    )
    assert res_str_err["checksById"]["VAL-CI-01"]["status"] == "FAIL"

    # Ensure mixed failure lists (covered kqlStaticErrors + non-KQL errors) fail VAL-CI-01
    qual_ev_mixed = dict(qual_ev)
    qual_ev_mixed["ciChecks"] = {
        "passed": False,
        "reason": "Mixed KQL schema warning and ARM failure",
        "kqlStaticErrors": [
            {
                "id": f"xdr-{rule_id}",
                "originalRuleId": rule_id,
                "code": "KS142",
                "querySha256": xdr_query_sha,
            }
        ],
        "errors": ["ARM deployment validation failed"],
    }
    res_mixed = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_mixed,
        run_number=1,
    )
    assert res_mixed["checksById"]["VAL-CI-01"]["status"] == "FAIL"

    # Ensure stale receipts with mismatched querySha256 do not mint fresh PASS hashes and fail QUAL-RUNTIME-01
    qual_ev_stale = dict(qual_ev)
    qual_ev_stale.pop("kqlRuntimeVerifiedRules", None)
    qual_ev_stale["runtimeKql"] = {
        "status": "passed",
        "passed": True,
        "queries": [
            {
                "id": rule_id,
                "status": "PASS",
                "querySha256": "0" * 64,
            }
        ],
    }
    res_stale = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_stale,
        run_number=1,
    )
    assert res_stale["kqlRuntimeVerifiedRules"] == []
    assert res_stale["checksById"]["QUAL-RUNTIME-01"]["status"] == "FAIL"
    assert res_stale["checksById"]["VAL-CI-01"]["status"] == "FAIL"

    # Ensure kqlRuntimeVerifiedRules entries missing explicit status or for removed rule IDs are rejected
    qual_ev_bad_entries = dict(qual_ev)
    qual_ev_bad_entries["kqlRuntimeVerifiedRules"] = [
        {
            "id": rule_id,
            "querySha256": ar_query_sha,
        },
        {
            "id": "non-existent-rule-id",
            "status": "PASS",
            "querySha256": xdr_query_sha,
        },
    ]
    qual_ev_bad_entries["runtimeKql"] = {"status": "passed", "passed": True}
    res_bad_entries = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_bad_entries,
        run_number=1,
    )
    assert res_bad_entries["kqlRuntimeVerifiedRules"] == []
    assert res_bad_entries["checksById"]["QUAL-RUNTIME-01"]["status"] == "FAIL"

    # Round 3 Item 1: E2E-Q02 empty detections list must not fall through to aggregate scalar fields
    qual_ev_empty_dets = dict(qual_ev)
    qual_ev_empty_dets["alertLifecycle"] = {
        "detections": [],
        "initialDisabled": True,
        "alertsFired": 5,
        "returnedToDisabled": True,
    }
    res_empty_dets = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_empty_dets,
        run_number=1,
    )
    assert res_empty_dets["checksById"]["E2E-Q02"]["status"] == "FAIL"

    # Round 3 Item 1b: E2E-Q02 partial detections list missing second on-disk detection must fail
    rule2_id = "22222222-8104-41eb-bad3-26054a3ad5f0"
    ar2_sha = _build_valid_analytic_rule(sol / "Analytic Rules" / "SecondRule.yaml", rule_id=rule2_id)
    _build_valid_xdr_detection(
        sol / "XDR Detections" / "SecondRule.yaml",
        source_rule_id=rule2_id,
        source_rule_path="Analytic Rules/SecondRule.yaml",
        source_rule_sha256=ar2_sha,
    )
    qual_ev_multi = _build_live_qualification_evidence(sol)
    qual_ev_partial_dets = dict(qual_ev_multi)
    qual_ev_partial_dets["alertLifecycle"] = {
        "detections": [
            {
                "id": f"xdr-{rule_id}",
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            }
        ]
    }
    res_partial_dets = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_partial_dets,
        run_number=1,
    )
    assert res_partial_dets["checksById"]["E2E-Q02"]["status"] == "FAIL"

    # Round 3 Item 2: _discover_on_disk_xdr_detections fails QUAL-RUNTIME-01 on duplicate IDs or malformed YAML
    dup_file = sol / "XDR Detections" / "DuplicateId.yaml"
    _build_valid_xdr_detection(
        dup_file,
        source_rule_id=rule2_id,
        source_rule_path="Analytic Rules/SecondRule.yaml",
        source_rule_sha256=ar2_sha,
    )
    res_dup = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_multi,
        run_number=1,
    )
    assert res_dup["checksById"]["QUAL-RUNTIME-01"]["status"] == "FAIL"
    assert res_dup["kqlRuntimeVerifiedRules"] == []
    dup_file.unlink()

    malformed_file = sol / "XDR Detections" / "Malformed.yaml"
    malformed_file.write_text("id: [unterminated\n", encoding="utf-8")
    res_malformed = run_pr_qualification_checks(
        sol,
        workflow_state=wf_state,
        qualification_evidence=qual_ev_multi,
        run_number=1,
    )
    assert res_malformed["checksById"]["QUAL-RUNTIME-01"]["status"] == "FAIL"
    assert res_malformed["kqlRuntimeVerifiedRules"] == []
    malformed_file.unlink()


def test_round3_kql_subquery_and_retry_after_fixes() -> None:
    from solution_manager.authoring.validator import validate_kql_query_static
    from solution_manager.qualification.deployment import _parse_retry_after_seconds

    # mv-apply and partition operator-only subqueries should pass
    res_mv = validate_kql_query_static(
        "DeviceProcessEvents | mv-apply x=dynamic([1,2]) on (where x > 0 | project x)"
    )
    assert res_mv["valid"] is True, f"Expected mv-apply subquery to pass, got {res_mv['errors']}"

    res_part = validate_kql_query_static(
        "DeviceProcessEvents | partition hint.strategy=native by AccountName (where isnotempty(FileName) | summarize count())"
    )
    assert res_part["valid"] is True, f"Expected partition subquery to pass, got {res_part['errors']}"

    # Invalid operator inside mv-apply subquery must fail
    res_bad_mv = validate_kql_query_static(
        "DeviceProcessEvents | mv-apply x=dynamic([1,2]) on (notanoperator x > 0 | project x)"
    )
    assert res_bad_mv["valid"] is False and any("notanoperator" in e for e in res_bad_mv["errors"])

    # Single-token join (MissingTable) and lookup (MissingLookupTable) must fail
    res_join = validate_kql_query_static(
        "DeviceProcessEvents | join kind=inner (MissingTable) on DeviceId"
    )
    assert res_join["valid"] is False and any("MissingTable" in e for e in res_join["errors"])

    res_lookup = validate_kql_query_static(
        "DeviceProcessEvents | lookup kind=leftouter (MissingLookupTable) on DeviceId"
    )
    assert res_lookup["valid"] is False and any("MissingLookupTable" in e for e in res_lookup["errors"])

    # Multi-statement view () { let ...; ... } with parse trailing wildcard * should pass
    res_view = validate_kql_query_static(
        "let xdr_inline_Parser = view () {\n"
        "    let ActionMappingTable = datatable(Code:string, Action:string)['1', 'Login'];\n"
        "    Syslog\n"
        "    | parse SyslogMessage with * 'ACTION :' Code:string ' ' *\n"
        "    | lookup kind=leftouter ActionMappingTable on Code\n"
        "};\n"
        "xdr_inline_Parser\n"
        "| where isnotempty(Action)"
    )
    assert res_view["valid"] is True, f"Expected multi-statement view() to pass, got {res_view['errors']}"

    # _parse_retry_after_seconds handles inf/nan, <1s remaining, and Retry-After > remaining budget
    assert _parse_retry_after_seconds("inf", default_seconds=2, remaining_budget_seconds=120.0) == 2
    assert _parse_retry_after_seconds("-inf", default_seconds=2, remaining_budget_seconds=120.0) == 2
    assert _parse_retry_after_seconds("nan", default_seconds=2, remaining_budget_seconds=120.0) == 2
    assert _parse_retry_after_seconds("5", default_seconds=2, remaining_budget_seconds=0.4) is None
    assert _parse_retry_after_seconds("120", default_seconds=2, remaining_budget_seconds=30.0) is None
    assert _parse_retry_after_seconds("45", default_seconds=2, remaining_budget_seconds=120.0) == 45


def test_round4_e2e_q02_bipartite_matching_and_kql_regressions(tmp_path: Path) -> None:
    import copy
    from solution_manager.authoring.validator import validate_kql_query_static

    # 1. Multi-statement scalar function let f = () { let y = 1; 42 } must pass, while invalid operator/generator bodies fail
    res_scalar_fn = validate_kql_query_static(
        "let f = () { let y = 1; 42 };\n"
        "DeviceProcessEvents | extend z = f()"
    )
    assert res_scalar_fn["valid"] is True, f"Expected multi-statement scalar function to pass, got {res_scalar_fn['errors']}"

    res_bad_let_body = validate_kql_query_static(
        "let f = () { let y = 1; where x == 1 };\n"
        "DeviceProcessEvents | extend z = f()"
    )
    assert res_bad_let_body["valid"] is False

    res_bad_let_union = validate_kql_query_static(
        "let f = () { let y = 1; union notanoperator };\n"
        "DeviceProcessEvents | extend z = f()"
    )
    assert res_bad_let_union["valid"] is False

    # 2. join (materialize(T | notanoperator x)) and extra parenthesized pipelines must fail
    res_join_mat = validate_kql_query_static(
        "DeviceProcessEvents | join kind=inner (materialize(DeviceProcessEvents | notanoperator x)) on DeviceId"
    )
    assert res_join_mat["valid"] is False and any("notanoperator" in e for e in res_join_mat["errors"])

    res_join_mat_extra = validate_kql_query_static(
        "DeviceProcessEvents | join kind=inner (materialize(DeviceProcessEvents) (DeviceProcessEvents | notanoperator x)) on DeviceId"
    )
    assert res_join_mat_extra["valid"] is False and any("notanoperator" in e for e in res_join_mat_extra["errors"])

    # 3. E2E-Q02 scalar fallback disabled when detections exist on disk, 1:1 receipt matching, and QUAL-RUNTIME-01 FAIL on on-disk errors without runtime evidence
    sol = tmp_path / "Round4Sol"
    _build_base_package(
        sol,
        version="3.2.2",
        data_lists={
            "Analytic Rules": ["Analytic Rules/Rule1.yaml", "Analytic Rules/Rule2.yaml"],
            "XDR Detections": ["XDR Detections/Rule1.yaml", "XDR Detections/Rule2.yaml"],
        },
    )
    _build_valid_analytic_rule(sol / "Analytic Rules" / "Rule1.yaml")
    _build_valid_xdr_detection(sol / "XDR Detections" / "Rule1.yaml")
    ar2_id = "7e76fd9d-8104-41eb-bad3-26054a3ad5f2"
    xdr2_id = "xdr-7e76fd9d-8104-41eb-bad3-26054a3ad5f2"
    rule1_ar_text = (sol / "Analytic Rules" / "Rule1.yaml").read_text(encoding="utf-8")
    (sol / "Analytic Rules" / "Rule2.yaml").write_text(
        rule1_ar_text.replace("6e76fd9d-8104-41eb-bad3-26054a3ad5f0", ar2_id),
        encoding="utf-8",
    )
    rule1_xdr_text = (sol / "XDR Detections" / "Rule1.yaml").read_text(encoding="utf-8")
    (sol / "XDR Detections" / "Rule2.yaml").write_text(
        rule1_xdr_text.replace("xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0", xdr2_id).replace(
            "6e76fd9d-8104-41eb-bad3-26054a3ad5f0", ar2_id
        ),
        encoding="utf-8",
    )
    _write_json(
        sol / "mock.json",
        {
            "tables": {
                "AzureDiagnostics": [
                    {
                        "TimeGenerated": "2026-10-19T12:00:00Z",
                        "Category": "DDoSMitigationFlowLogs",
                        "sourcePublicIpAddress_s": "203.0.113.5",
                    }
                ]
            }
        },
    )

    qual_ev_base = _build_live_qualification_evidence(sol)
    wf_state = {"qualification": {"stages": {"rule_parity": {"status": "passed"}}}}

    # (a) Omitting both detections and rules (or detections: null) must fail E2E-Q02
    qual_ev_no_list = copy.deepcopy(qual_ev_base)
    qual_ev_no_list["alertLifecycle"] = {
        "initialDisabled": True,
        "alertsFired": 4,
        "returnedToDisabled": True,
        "detections": None,
    }
    res_no_list = run_pr_qualification_checks(sol, workflow_state=wf_state, qualification_evidence=qual_ev_no_list, run_number=1)
    assert res_no_list["checksById"]["E2E-Q02"]["status"] == "FAIL"

    # (b) One receipt carrying both XDR IDs + one dummy receipt must fail 1:1 matching
    qual_ev_spoof = copy.deepcopy(qual_ev_base)
    qual_ev_spoof["alertLifecycle"] = {
        "detections": [
            {
                "id": "xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
                "targetRuleId": xdr2_id,
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            },
            {
                "id": "dummy-unrelated-id",
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            },
        ]
    }
    res_spoof = run_pr_qualification_checks(sol, workflow_state=wf_state, qualification_evidence=qual_ev_spoof, run_number=1)
    assert res_spoof["checksById"]["E2E-Q02"]["status"] == "FAIL"

    # (b2) Duplicate id-less receipts for a shared displayName across two distinct XDR detections must fail
    qual_ev_dup_name = copy.deepcopy(qual_ev_base)
    qual_ev_dup_name["alertLifecycle"] = {
        "detections": [
            {
                "name": "Test XDR Rule 1",
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            },
            {
                "name": "Test XDR Rule 1",
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            },
        ]
    }
    res_dup_name = run_pr_qualification_checks(sol, workflow_state=wf_state, qualification_evidence=qual_ev_dup_name, run_number=1)
    assert res_dup_name["checksById"]["E2E-Q02"]["status"] == "FAIL"

    # (b3) Disambiguated id-less receipts using distinct file stems (Rule1, Rule2) must pass
    qual_ev_stems = copy.deepcopy(qual_ev_base)
    qual_ev_stems["alertLifecycle"] = {
        "detections": [
            {
                "name": "Rule1",
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            },
            {
                "name": "Rule2",
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            },
        ]
    }
    res_stems = run_pr_qualification_checks(sol, workflow_state=wf_state, qualification_evidence=qual_ev_stems, run_number=1)
    assert res_stems["checksById"]["E2E-Q02"]["status"] == "PASS"

    # (c) Uppercase GUIDs in receipts must match lowercase on-disk IDs cleanly
    qual_ev_upper = copy.deepcopy(qual_ev_base)
    qual_ev_upper["alertLifecycle"] = {
        "detections": [
            {
                "id": "XDR-6E76FD9D-8104-41EB-BAD3-26054A3AD5F0",
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            },
            {
                "id": xdr2_id.upper(),
                "initialDisabled": True,
                "alertsFired": 1,
                "returnedToDisabled": True,
            },
        ]
    }
    res_upper = run_pr_qualification_checks(sol, workflow_state=wf_state, qualification_evidence=qual_ev_upper, run_number=1)
    assert res_upper["checksById"]["E2E-Q02"]["status"] == "PASS"

    # (d) QUAL-RUNTIME-01 must return FAIL (not SKIPPED) when on-disk rule errors exist without runtime evidence
    dup_file = sol / "XDR Detections" / "Rule2Dup.yaml"
    dup_file.write_text((sol / "XDR Detections" / "Rule2.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    res_dup_no_ev = run_pr_qualification_checks(sol, workflow_state={}, qualification_evidence={}, run_number=1)
    assert res_dup_no_ev["checksById"]["QUAL-RUNTIME-01"]["status"] == "FAIL"
    dup_file.unlink()


def _ms_locale_url(subdomain: str, locale: str, path: str) -> str:
    """Construct a locale-bearing Microsoft URL at runtime so test source never embeds CI-rejected literals."""
    return f"https://{subdomain}.microsoft.com/{locale}/{path.lstrip('/')}"


def test_documents_link_validation_locale_scanning_and_url_normalization(tmp_path: Path) -> None:
    """Verify VAL-URL-01, validate_solution, and QUAL-URL-01 catch CI DocumentsLinkValidation locale URLs and normalize resolvedUrl."""
    from solution_manager.migration.converter import convert_solution, validate_solution
    from solution_manager.qualification.pr_check_runner import (
        build_url_verification_evidence,
        normalize_solution_url_verification_files,
        normalize_url_verification_payload,
        strip_microsoft_url_locale,
    )

    azure_en_us_legal = _ms_locale_url("azure", "en-us", "support/legal/preview-supplemental-terms/")
    docs_en_us_hunting = _ms_locale_url("docs", "en-us", "azure/sentinel/hunting")
    docs_en_us_overview = _ms_locale_url("docs", "en-us", "azure/sentinel/overview")
    azure_fr_fr_legal = _ms_locale_url("azure", "fr-fr", "support/legal/")

    assert (
        strip_microsoft_url_locale(azure_en_us_legal)
        == "https://azure.microsoft.com/support/legal/preview-supplemental-terms/"
    )
    assert (
        strip_microsoft_url_locale(docs_en_us_hunting)
        == "https://docs.microsoft.com/azure/sentinel/hunting"
    )

    sol = tmp_path / "LocaleUrlSol"
    _build_base_package(
        sol,
        version="3.2.2",
        include_xdr_props=True,
        data_lists={
            "Analytic Rules": ["Analytic Rules/Rule1.yaml"],
            "XDR Detections": ["XDR Detections/Rule1.yaml"],
        },
    )
    ar_path = sol / "Analytic Rules" / "Rule1.yaml"
    _build_valid_analytic_rule(ar_path)
    ar_doc = yaml.safe_load(ar_path.read_text(encoding="utf-8"))
    ar_doc["requiredDataConnectors"] = [{"connectorId": "AzureNetworkDDoSProtection", "dataTypes": ["AzureDiagnostics"]}]
    ar_doc["version"] = "1.0.0"
    _write_yaml(ar_path, ar_doc)
    convert_solution(sol)

    # Write Evidence/receipts/url-and-asset-verification.json with a locale-bearing resolvedUrl (exact PR #15543 scenario)
    receipt_path = sol / "Evidence" / "receipts" / "url-and-asset-verification.json"
    _write_json(
        receipt_path,
        {
            "checkedCount": 1,
            "brokenCount": 0,
            "passed": True,
            "urls": [
                {
                    "url": "https://azure.microsoft.com/support/legal/preview-supplemental-terms/",
                    "resolvedUrl": azure_en_us_legal,
                    "status": 200,
                }
            ],
        },
    )

    # 1. VAL-URL-01 and validate_solution must fail and surface recommended locale-stripped URL fix
    qual_run = run_pr_qualification_checks(sol, run_qualification=False)
    val_url = qual_run["checksById"]["VAL-URL-01"]
    assert val_url["status"] == "FAIL"
    assert azure_en_us_legal in val_url["whatWeObserved"]
    assert "https://azure.microsoft.com/support/legal/preview-supplemental-terms/" in val_url["whyPassedOrFailed"]

    val_sol = validate_solution(sol)
    assert val_sol["documentsLinkValidation"]["valid"] is False
    assert val_sol["documentsLinkValidation"]["issueCount"] == 1
    assert val_sol["invalid"] == 1
    issue = val_sol["documentsLinkValidation"]["issues"][0]
    assert issue["file"] == "Evidence/receipts/url-and-asset-verification.json"
    assert issue["url"] == azure_en_us_legal
    assert issue["recommendedUrl"] == "https://azure.microsoft.com/support/legal/preview-supplemental-terms/"

    # 2. Normalizing on-disk URL verification evidence files strips locale and makes VAL-URL-01 + validate_solution pass
    updated_files = normalize_solution_url_verification_files(sol)
    assert updated_files == ["Evidence/receipts/url-and-asset-verification.json"]
    normalized_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert (
        normalized_receipt["urls"][0]["resolvedUrl"]
        == "https://azure.microsoft.com/support/legal/preview-supplemental-terms/"
    )

    qual_run_after = run_pr_qualification_checks(sol, run_qualification=False)
    assert qual_run_after["checksById"]["VAL-URL-01"]["status"] == "PASS"

    val_sol_after = validate_solution(sol)
    assert val_sol_after["documentsLinkValidation"]["valid"] is True
    assert val_sol_after["invalid"] == 0

    # 3. build_url_verification_evidence and normalize_url_verification_payload normalize resolvedUrl automatically
    built_ev = build_url_verification_evidence(
        [
            {
                "url": "https://aka.ms/sentinel",
                "resolvedUrl": docs_en_us_overview,
                "status": 200,
            }
        ]
    )
    assert built_ev["passed"] is True
    assert built_ev["urls"][0]["resolvedUrl"] == "https://docs.microsoft.com/azure/sentinel/overview"

    nested_ev = normalize_url_verification_payload(
        {
            "urlVerification": {
                "urls": [
                    {
                        "url": "https://azure.microsoft.com/support/legal/",
                        "resolvedUrl": azure_fr_fr_legal,
                    }
                ]
            }
        }
    )
    assert nested_ev["urlVerification"]["urls"][0]["resolvedUrl"] == "https://azure.microsoft.com/support/legal/"



class TestPrQualificationEngineUnittest(unittest.TestCase):
    def test_kql_runtime_verified_rules_and_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            test_kql_runtime_verified_rules_projection_and_val_ci_01_override(Path(tmp))

    def test_round3_kql_and_retry_fixes(self) -> None:
        test_round3_kql_subquery_and_retry_after_fixes()

    def test_documents_link_validation_locale_scanning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            test_documents_link_validation_locale_scanning_and_url_normalization(Path(tmp))

