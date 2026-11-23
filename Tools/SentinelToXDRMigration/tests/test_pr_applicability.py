"""Unit tests for per-file XDR detection provenance classification and PR check applicability."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import yaml

from solution_manager.qualification.pr_applicability import (
    classify_xdr_detection_files,
    determine_pr_applicability,
    is_migrated_xdr_detection_doc,
)
from solution_manager.qualification.pr_check_runner import (
    run_pr_qualification_checks,
)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _build_base_v31_package(
    sol_root: Path,
    *,
    version: str = "3.2.2",
    custom_detection_ids: list[str] | None = None,
) -> None:
    det_ids = custom_detection_ids or ["a1b2c3d4-1111-4222-8333-444455556666"]
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
    _write_json(
        sol_root / "Data" / f"Solution_{sol_root.name.replace(' ', '')}.json",
        {
            "Name": sol_root.name,
            "Author": "Microsoft",
            "Logo": '<img src="https://aka.ms/sentinel-logo.svg" width="75px" height="75px">',
            "Description": "Solution description with https://aka.ms/sentinel-docs link.",
            "Version": version,
        },
    )
    (sol_root / "ReleaseNotes.md").write_text(
        f"| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
        f"|---|---|---|\n"
        f"| {version} | 17-11-2026 | Release {version}. |\n",
        encoding="utf-8",
    )
    pkg_dir = sol_root / "Package"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / f"{version}.zip").write_bytes(b"PK\x03\x04dummy-zip")
    _write_json(
        pkg_dir / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [
                {
                    "type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
                    "apiVersion": "2023-04-01-preview",
                    "name": f"{sol_root.name}-pkg",
                    "properties": {
                        "version": version,
                        "requiredWorkloads": ["defender"],
                        "requiredDataConnectors": {"defender": ["MDE"]},
                        "extra": {"customDetections": det_ids},
                    },
                }
            ],
        },
    )
    _write_json(
        pkg_dir / "createUiDefinition.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/0.1.2-preview/CreateUIDefinition.MultiVm.json#",
            "handler": "Microsoft.Azure.CreateUIDef",
            "version": "0.1.2-preview",
            "parameters": {
                "basics": [{"name": "workspace", "type": "Microsoft.Solutions.ArmApiControl"}],
                "steps": [{"name": "detections", "label": "Custom Detections", "elements": []}],
                "outputs": {},
            },
        },
    )


def _build_native_xdr_detection(
    path: Path,
    *,
    det_id: str = "a1b2c3d4-1111-4222-8333-444455556666",
) -> None:
    _write_yaml(
        path,
        {
            "apiVersion": "2026-03-01",
            "kind": "CustomDetection",
            "properties": {
                "id": det_id,
                "displayName": "Directly Authored Defender XDR Detection",
                "queryCondition": {
                    "queryText": "DeviceProcessEvents | where FileName =~ 'cmd.exe' | project Timestamp, DeviceId, ReportId",
                },
                "schedule": {
                    "frequency": "PT1H",
                    "period": "PT1H",
                },
                "detectionAction": {
                    "alertTemplate": {
                        "severity": "medium",
                        "tactics": [
                            {
                                "tactic": "Execution",
                                "techniques": [{"technique": "T1059"}],
                            }
                        ],
                        "impactedAssets": [
                            {
                                "@odata.type": "#microsoft.graph.security.impactedDeviceAsset",
                                "identifier": "deviceId",
                                "inputColumnName": "DeviceId",
                            }
                        ],
                        "customDetails": {
                            "ReportId": "ReportId",
                        },
                    }
                },
            },
        },
    )


def _build_migrated_xdr_detection(
    path: Path,
    *,
    source_rule_id: str = "6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
    source_rule_path: str = "Analytic Rules/MigratedRule.yaml",
    source_rule_sha256: str = "cbabeb0916d52c15d6d9354534022ab1735fb22815d2336a3c616141a035c0a1",
) -> None:
    _write_yaml(
        path,
        {
            "apiVersion": "2026-03-01",
            "kind": "CustomDetection",
            "contentProvenance": {
                "source": {
                    "kind": "AnalyticsRule",
                    "id": source_rule_id,
                    "path": source_rule_path,
                    "querySha256": source_rule_sha256,
                },
                "conversion": {
                    "reviewScope": {
                        "sourceDocumentSha256": source_rule_sha256,
                    }
                },
            },
            "properties": {
                "id": f"xdr-{source_rule_id}",
                "displayName": "Migrated Defender XDR Detection",
                "queryCondition": {
                    "queryText": "DeviceProcessEvents | where FileName =~ 'powershell.exe' | project Timestamp, DeviceId, ReportId",
                },
                "schedule": {
                    "frequency": "PT1H",
                    "period": "PT1H",
                },
                "detectionAction": {
                    "alertTemplate": {
                        "severity": "high",
                        "tactics": [
                            {
                                "tactic": "Execution",
                                "techniques": [{"technique": "T1059"}],
                            }
                        ],
                        "impactedAssets": [
                            {
                                "@odata.type": "#microsoft.graph.security.impactedDeviceAsset",
                                "identifier": "deviceId",
                                "inputColumnName": "DeviceId",
                            }
                        ],
                        "customDetails": {
                            "ReportId": "ReportId",
                        },
                    }
                },
            },
        },
    )


def test_pure_native_detection_solution_applicability_and_runner(tmp_path: Path) -> None:
    """1. Pure native detection solution (no Analytic Rules/, XDR Detections/*.yaml without source/conversion)."""
    sol = tmp_path / "PureNativeXdrSol"
    native_id = "a1b2c3d4-1111-4222-8333-444455556666"
    _build_base_v31_package(sol, custom_detection_ids=[native_id])
    _build_native_xdr_detection(sol / "XDR Detections" / "NativeRule.yaml", det_id=native_id)
    _write_json(
        sol / "mock.json",
        {
            "tables": {
                "DeviceProcessEvents": [
                    {
                        "Timestamp": "2026-11-17T00:00:00Z",
                        "FileName": "cmd.exe",
                        "DeviceId": "dev-01",
                        "ReportId": "rep-01",
                    }
                ]
            }
        },
    )

    app = determine_pr_applicability(sol)
    assert app["isMigration"] is False
    assert app["xdrDetectionMode"] == "native"
    assert app["migratedXdrDetectionFiles"] == []
    assert app["nativeXdrDetectionFiles"] == ["XDR Detections/NativeRule.yaml"]
    assert app["xdrDetectionProvenanceByFile"] == {"XDR Detections/NativeRule.yaml": "native"}

    # Target structural, V3.1 packaging, mock data, deployment, and runtime checks apply
    for cid in ("VAL-PKG-01", "VAL-PKG-02", "VAL-PKG-03", "VAL-PKG-04", "VAL-AR-01", "E2E-V01", "E2E-V02", "QUAL-DEP-01", "E2E-Q01", "E2E-Q02"):
        assert app["checksById"][cid]["applicable"] is True, f"Expected {cid} to be applicable for native XDR solution"

    # Migration-only checks (MIG-V01, E2E-Q03, etc.) do NOT apply
    for mig_id in ("MIG-V01", "MIG-V02", "MIG-V03", "MIG-Q01", "E2E-Q03"):
        assert app["checksById"][mig_id]["applicable"] is False

    # Run validation checks and verify no failure on MIG-V01 or parity
    res = run_pr_qualification_checks(sol, run_qualification=False)
    assert res["isMigration"] is False
    assert res["validationStatus"] == "Validated"
    assert res["migrationStatus"] == "Not Applicable"
    assert res["overallVerdict"] == "Validated"
    assert res["checksById"]["VAL-AR-01"]["status"] == "PASS"
    assert res["checksById"]["VAL-PKG-04"]["status"] == "PASS"
    assert res["checksById"]["E2E-V01"]["status"] == "PASS"
    assert res["checksById"]["E2E-V02"]["status"] == "PASS"
    assert res["checksById"]["MIG-V01"]["status"] == "NOT_APPLICABLE"
    assert res["checksById"]["E2E-Q03"]["status"] == "NOT_APPLICABLE"


def test_mixed_solution_migrated_and_native_detections_applicability_and_runner(tmp_path: Path) -> None:
    """2. Mixed solution (one migrated detection with source/conversion + one native detection without source/conversion)."""
    sol = tmp_path / "MixedXdrSol"
    src_id = "6e76fd9d-8104-41eb-bad3-26054a3ad5f0"
    migrated_id = f"xdr-{src_id}"
    native_id = "b2c3d4e5-2222-4333-9444-555566667777"

    _build_base_v31_package(sol, custom_detection_ids=[migrated_id, native_id])
    _write_yaml(
        sol / "Analytic Rules" / "MigratedRule.yaml",
        {
            "id": src_id,
            "name": "Migrated Sentinel Rule",
            "description": "Source Sentinel rule for migration.",
            "severity": "High",
            "kind": "Scheduled",
            "queryFrequency": "1h",
            "queryPeriod": "1h",
            "triggerOperator": "gt",
            "triggerThreshold": 0,
            "tactics": ["Execution"],
            "relevantTechniques": ["T1059"],
            "query": "SecurityEvent | where EventID == 4688",
            "entityMappings": [
                {
                    "entityType": "Host",
                    "fieldMappings": [{"identifier": "HostName", "columnName": "Computer"}],
                }
            ],
        },
    )
    _build_migrated_xdr_detection(
        sol / "XDR Detections" / "MigratedRule.yaml",
        source_rule_id=src_id,
        source_rule_path="Analytic Rules/MigratedRule.yaml",
    )
    _build_native_xdr_detection(
        sol / "XDR Detections" / "NativeRule.yaml",
        det_id=native_id,
    )
    _write_json(
        sol / "mock.json",
        {
            "tables": {
                "DeviceProcessEvents": [
                    {
                        "Timestamp": "2026-11-17T00:00:00Z",
                        "FileName": "powershell.exe",
                        "DeviceId": "dev-01",
                        "ReportId": "rep-01",
                    }
                ]
            }
        },
    )

    classification = classify_xdr_detection_files(
        sol,
        ["XDR Detections/MigratedRule.yaml", "XDR Detections/NativeRule.yaml"],
    )
    assert classification["detectionMode"] == "mixed"
    assert classification["migratedFiles"] == ["XDR Detections/MigratedRule.yaml"]
    assert classification["nativeFiles"] == ["XDR Detections/NativeRule.yaml"]

    app = determine_pr_applicability(sol)
    assert app["isMigration"] is True
    assert app["xdrDetectionMode"] == "mixed"
    assert app["migratedXdrDetectionFiles"] == ["XDR Detections/MigratedRule.yaml"]
    assert app["nativeXdrDetectionFiles"] == ["XDR Detections/NativeRule.yaml"]
    assert app["checksById"]["MIG-V01"]["applicable"] is True
    assert "skipped" in app["checksById"]["MIG-V01"]["applicabilityReason"].lower()
    assert app["checksById"]["E2E-Q03"]["applicable"] is True

    # Offline validation run: MIG-V01 evaluates only MigratedRule.yaml and skips NativeRule.yaml -> PASS
    res_val = run_pr_qualification_checks(sol, run_qualification=False)
    assert res_val["checksById"]["VAL-AR-01"]["status"] == "PASS"
    assert res_val["checksById"]["MIG-V01"]["status"] == "PASS"
    assert "skipped 1 native/standalone" in res_val["checksById"]["MIG-V01"]["whatWeObserved"]
    assert res_val["checksById"]["MIG-V02"]["status"] == "PASS"
    assert res_val["checksById"]["MIG-V03"]["status"] == "PASS"
    assert res_val["validationStatus"] == "Validated"

    # Qualification run with per-pair parity receipt for the migrated detection only -> E2E-Q03 PASS
    qual_ev = {
        "alertParity": {
            "pairs": [
                {
                    "id": migrated_id,
                    "sourceRuleId": src_id,
                    "parityPassed": True,
                }
            ]
        },
        "dualSurfaceKql": {"dualSurfaceVerified": True},
    }
    res_qual = run_pr_qualification_checks(sol, run_qualification=True, qualification_evidence=qual_ev)
    assert res_qual["checksById"]["MIG-V01"]["status"] == "PASS"
    assert res_qual["checksById"]["E2E-Q03"]["status"] == "PASS"
    assert "1 native/standalone XDR Detection(s) skipped" in res_qual["checksById"]["E2E-Q03"]["whatWeObserved"]


def test_is_migrated_xdr_detection_doc_variants() -> None:
    """Verify is_migrated_xdr_detection_doc distinguishes migrated vs native YAML structures."""
    assert is_migrated_xdr_detection_doc({"properties": {"id": "11111111-2222-4333-8444-555555555555"}}) is False
    assert is_migrated_xdr_detection_doc(
        {
            "contentProvenance": {"origin": "native"},
            "properties": {"id": "11111111-2222-4333-8444-555555555555"},
        }
    ) is False
    assert is_migrated_xdr_detection_doc(
        {
            "contentProvenance": {"source": {"id": "6e76fd9d-8104-41eb-bad3-26054a3ad5f0"}},
            "properties": {"id": "xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0"},
        }
    ) is True
    assert is_migrated_xdr_detection_doc(
        {
            "contentProvenance": {"conversion": {"reviewScope": {"sourceDocumentSha256": "abc"}}},
            "properties": {"id": "xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0"},
        }
    ) is True


def test_native_only_solution_with_workbooks_is_not_classified_as_workbook_only(
    tmp_path: Path,
) -> None:
    """Gap 3 regression: native-only solution with XDR Detections + Workbooks is not workbook-only."""
    from solution_manager.migration import workbook_workflow

    sol = tmp_path / "NativeWithWorkbookSol"
    native_id = "xdr-a1b2c3d4-1111-4222-8333-444455556666"
    _build_base_v31_package(sol, custom_detection_ids=[native_id])
    _build_native_xdr_detection(
        sol / "XDR Detections" / "NativeThreatDetection.yaml",
        det_id=native_id,
    )
    _write_json(
        sol / "Workbooks" / "OverviewWorkbook.json",
        {"version": "Notebook/1.0", "items": []},
    )

    assert workbook_workflow.has_analytic_rules(sol) is False
    assert workbook_workflow.has_detection_content(sol) is True
    state = {"context": {"workbookCapabilityVersion": workbook_workflow.CAPABILITY_VERSION}}
    assert workbook_workflow.enabled(state) is True
    workbook_only = workbook_workflow.enabled(state) and not workbook_workflow.has_detection_content(sol)
    assert workbook_only is False

    wb_only_sol = tmp_path / "PureWorkbookOnlySol"
    wb_only_sol.mkdir(parents=True)
    _write_json(
        wb_only_sol / "Workbooks" / "OverviewWorkbook.json",
        {"version": "Notebook/1.0", "items": []},
    )
    assert workbook_workflow.has_detection_content(wb_only_sol) is False
    assert (workbook_workflow.enabled(state) and not workbook_workflow.has_detection_content(wb_only_sol)) is True

