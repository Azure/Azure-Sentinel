"""Unit and integration tests for PR Applicability and Qualification Check Runner Engine (Stream 2)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

import yaml

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


def _build_live_qualification_evidence() -> dict[str, Any]:
    return {
        "simulated": False,
        "dryRun": False,
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
            "detections": [
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
        qualification_evidence=_build_live_qualification_evidence(),
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
    ev_payload = _build_live_qualification_evidence()
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



