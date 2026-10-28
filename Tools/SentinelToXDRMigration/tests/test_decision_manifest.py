"""Tests for sanitized PR decision manifest generation and solution report integration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sentinel_xdr_migration.decision_manifest import (
    ALLOWED_DECISION_SCOPES,
    DECISION_MANIFEST_SCHEMA_VERSION,
    build_sanitized_decision_manifest as compat_build_sanitized_decision_manifest,
)
from solution_manager.reporting import (
    build_sanitized_decision_manifest,
    verify_sanitized_decision_manifest,
    write_sanitized_decision_manifest,
)
from solution_manager.reporting.review_workflow import (
    build_sanitized_decision_manifest as review_workflow_build_manifest,
)
from solution_manager.reporting.solution_report import build_solution_report


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_sample_solution(tmp_path: Path) -> Path:
    sol = tmp_path / "ContosoCloud"
    (sol / "Analytic Rules").mkdir(parents=True)
    (sol / "XDR Detections").mkdir(parents=True)
    (sol / "Workbooks").mkdir(parents=True)
    (sol / "Data Connectors").mkdir(parents=True)

    (sol / "SolutionMetadata.json").write_text(
        json.dumps(
            {
                "publisherId": "contoso",
                "offerId": "contoso-cloud",
                "version": "3.2.2",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (sol / "Analytic Rules" / "rule1.yaml").write_text(
        "id: 11111111-2222-3333-4444-555555555551\n"
        "name: Contoso High Severity Alert\n"
        "kind: Scheduled\n"
        "severity: High\n"
        "queryFrequency: 5m\n"
        "queryPeriod: 5m\n"
        "triggerOperator: gt\n"
        "triggerThreshold: 0\n"
        "query: |\n"
        "  CommonSecurityLog\n"
        "  | where DeviceVendor == 'Contoso'\n",
        encoding="utf-8",
    )
    (sol / "XDR Detections" / "rule1.yaml").write_text(
        "id: 11111111-2222-3333-4444-555555555551\n"
        "displayName: Contoso High Severity Alert\n"
        "enabled: false\n"
        "frequency: NRT\n"
        "query: |\n"
        "  CommonSecurityLog\n"
        "  | where DeviceVendor == 'Contoso'\n",
        encoding="utf-8",
    )
    (sol / "Workbooks" / "ContosoWorkbook.json").write_text(
        json.dumps({"version": "Notebook/1.0", "items": []}, indent=2),
        encoding="utf-8",
    )
    (sol / "Data Connectors" / "ContosoConnector.json").write_text(
        json.dumps({"id": "ContosoConnector", "title": "Contoso Connector"}, indent=2),
        encoding="utf-8",
    )
    return sol


def _write_workflow_state(sol: Path, *, include_private_context: bool = False) -> Path:
    run_dir = sol / ".sentinel-xdr-runs" / "authoring-20260420T100000Z"
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (sol / ".sentinel-xdr-runs" / "latest-run.txt").write_text(
        f"{run_dir.name}\n",
        encoding="utf-8",
    )

    context_block = {
        "workflowProfile": "qualification",
        "armValidationMethod": "arm-ttk",
        "decisionRecords": [
            {
                "scope": "rule_review",
                "itemId": "Analytic Rules/rule1.yaml",
                "decision": "approved_nrt",
                "rationale": "Approved NRT conversion after verifying single-table query eligibility.",
            }
        ],
        "workbookReviewDecisions": {
            "Workbooks/ContosoWorkbook.json": {
                "decision": "approved_defender_ready",
                "rationale": "Verified workbook KQL panels and ARM parameters.",
            }
        },
        "connectorSelections": {
            "Analytic Rules/rule1.yaml": {
                "decision": "selected_connector",
                "connectorIds": ["ContosoConnector"],
                "rationale": "Mapped CommonSecurityLog to ContosoConnector.",
            }
        },
        "waivers": [
            {
                "itemId": "Workbooks/LegacyPanel",
                "decision": "waived",
                "rationale": "Legacy LA-only panel retained with explicit warning banner.",
            }
        ],
        "exclusions": [
            {
                "itemId": "Analytic Rules/deprecated_rule.yaml",
                "decision": "excluded",
                "rationale": "Deprecated rule excluded from XDR migration scope.",
            }
        ],
    }

    if include_private_context:
        context_block.update(
            {
                "tenantId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "subscriptionId": "bbbbbbbb-cccc-dddd-eeee-ffffffffffff",
                "workspaceCustomerId": "cccccccc-dddd-eeee-ffff-111111111111",
                "workspaceResourceId": (
                    "/subscriptions/bbbbbbbb-cccc-dddd-eeee-ffffffffffff"
                    "/resourceGroups/rg-private-secops"
                    "/providers/Microsoft.OperationalInsights/workspaces/ws-private-lab"
                ),
                "resourceGroup": "rg-private-secops",
                "workspaceName": "ws-private-lab",
            }
        )
        context_block["decisionRecords"].append(
            {
                "scope": "rule_review",
                "itemId": "Analytic Rules/rule1.yaml",
                "decision": "approved_with_lab_notes",
                "rationale": (
                    "Validated by analyst@contoso.com in tenantId=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee "
                    "subscription /subscriptions/bbbbbbbb-cccc-dddd-eeee-ffffffffffff/resourceGroups/rg-private-secops "
                    "workspaceId cccccccc-dddd-eeee-ffff-111111111111 from /Users/secadmin/private/repo/rule1.yaml "
                    "and C:\\Users\\secadmin\\Work\\rule1.yaml"
                ),
            }
        )

    state = {
        "schemaVersion": "1.1.0",
        "solutionName": "ContosoCloud",
        "solutionVersion": "3.2.2",
        "workflowProfile": "qualification",
        "armValidationMethod": "arm-ttk",
        "context": context_block,
        "stages": {
            "rule_conversion": {
                "status": "completed",
                "summary": "Converted 1 rule",
            },
            "workbook_migration": {
                "status": "completed",
                "summary": "Migrated 1 workbook",
            },
            "packaging": {
                "status": "completed",
                "summary": "Packaged V3.1 template validated with arm-ttk",
                "details": {
                    "armValidationMethod": "arm-ttk",
                },
            },
            "parity": {
                "status": "completed",
                "summary": "Validated 1 alert parity pair",
                "details": {
                    "rationale": "Both Sentinel AR and Defender XDR CD fired with matching entities.",
                },
            },
        },
    }
    state_path = run_dir / "workflow-state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state_path


def test_build_and_write_sanitized_decision_manifest_all_scopes(tmp_path: Path) -> None:
    sol = _write_sample_solution(tmp_path)
    state_path = _write_workflow_state(sol, include_private_context=False)

    manifest = build_sanitized_decision_manifest(sol, state_path=state_path)
    assert manifest["schemaVersion"] == DECISION_MANIFEST_SCHEMA_VERSION
    assert manifest["solutionName"] == "ContosoCloud"
    assert manifest["solutionVersion"] == "3.2.2"
    assert manifest["workflowProfile"] == "qualification"
    assert manifest["armValidationMethod"] == "arm-ttk"

    scopes = {item["scope"] for item in manifest["decisions"]}
    assert scopes == set(ALLOWED_DECISION_SCOPES)

    for record in manifest["decisions"]:
        assert set(record.keys()) == {
            "id",
            "scope",
            "itemId",
            "decision",
            "rationale",
            "sourceSha256",
            "targetSha256",
            "decisionSha256",
        }
        assert len(record["sourceSha256"]) == 64
        assert len(record["targetSha256"]) == 64
        assert len(record["decisionSha256"]) == 64
        expected_decision_sha = _sha256_text(
            json.dumps(
                {
                    "scope": record["scope"],
                    "itemId": record["itemId"],
                    "decision": record["decision"],
                    "rationale": record["rationale"],
                    "sourceSha256": record["sourceSha256"],
                    "targetSha256": record["targetSha256"],
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
        )
        assert record["decisionSha256"] == expected_decision_sha

    rule_record = next(
        r for r in manifest["decisions"] if r["scope"] == "rule_review"
    )
    assert rule_record["sourceSha256"] == hashlib.sha256(
        (sol / "Analytic Rules" / "rule1.yaml").read_bytes()
    ).hexdigest()
    assert rule_record["targetSha256"] == hashlib.sha256(
        (sol / "XDR Detections" / "rule1.yaml").read_bytes()
    ).hexdigest()

    # Deterministic across repeated calls and shim imports
    manifest_compat = compat_build_sanitized_decision_manifest(sol, state_path=state_path)
    manifest_review_wf = review_workflow_build_manifest(sol, state_path=state_path)
    assert manifest == manifest_compat == manifest_review_wf

    out_path = tmp_path / "out" / "decision-manifest.json"
    written = write_sanitized_decision_manifest(sol, state_path=state_path, output_path=out_path)
    assert out_path.is_file()
    persisted = json.loads(out_path.read_text(encoding="utf-8"))
    assert persisted == manifest
    assert written["manifestSha256"] == manifest["manifestSha256"]


def test_decision_manifest_sanitizes_private_identifiers_and_fails_closed(tmp_path: Path) -> None:
    sol = _write_sample_solution(tmp_path)
    state_path = _write_workflow_state(sol, include_private_context=True)

    manifest = build_sanitized_decision_manifest(sol, state_path=state_path)
    serialized = json.dumps(manifest, sort_keys=True)

    assert "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" not in serialized
    assert "bbbbbbbb-cccc-dddd-eeee-ffffffffffff" not in serialized
    assert "cccccccc-dddd-eeee-ffff-111111111111" not in serialized
    assert "rg-private-secops" not in serialized
    assert "ws-private-lab" not in serialized
    assert "analyst@contoso.com" not in serialized
    assert "/Users/secadmin" not in serialized
    assert "C:\\Users\\secadmin" not in serialized

    # Strict mode raises ValueError when raw private identifiers are present before redaction
    with pytest.raises(ValueError, match="Unsafe content remained"):
        build_sanitized_decision_manifest(
            sol,
            state_path=state_path,
            strict_reject_private=True,
        )

    # Direct fail-closed verification raises ValueError if an unredacted identifier or path leaks into a manifest
    tampered = json.loads(serialized)
    tampered["decisions"][0]["rationale"] = (
        "Leaked subscription /subscriptions/bbbbbbbb-cccc-dddd-eeee-ffffffffffff/resourceGroups/rg-leak"
    )
    with pytest.raises(ValueError, match="Unsafe content remained"):
        verify_sanitized_decision_manifest(tampered)

    tampered_path = json.loads(serialized)
    tampered_path["decisions"][0]["rationale"] = "Local path /Users/developer/secret/file.yaml"
    with pytest.raises(ValueError, match="Unsafe content remained"):
        verify_sanitized_decision_manifest(tampered_path)


def test_build_solution_report_includes_decision_manifest_summary(tmp_path: Path) -> None:
    sol = _write_sample_solution(tmp_path)
    _write_workflow_state(sol, include_private_context=True)

    report = build_solution_report(sol)
    assert "decisionManifestSummary" in report
    summary = report["decisionManifestSummary"]
    assert summary["schemaVersion"] == DECISION_MANIFEST_SCHEMA_VERSION
    assert summary["sanitizedVerified"] is True
    assert summary["decisionCount"] >= 7
    assert summary["count"] == summary["decisionCount"]
    assert len(summary["manifestSha256"]) == 64
    assert "rule_review" in summary["scopes"]


def test_decision_manifest_includes_sanitized_overrides(tmp_path: Path) -> None:
    sol = _write_sample_solution(tmp_path)
    _write_workflow_state(sol, include_private_context=True)

    manifest = build_sanitized_decision_manifest(sol)
    assert "overrides" in manifest
    overrides = manifest["overrides"]
    assert isinstance(overrides, list)
    assert len(overrides) >= 3

    override_types = {o["overrideType"] for o in overrides}
    assert "waiver" in override_types
    assert "manual_edit" in override_types
    assert "rejection" in override_types

    for ov in overrides:
        assert set(ov.keys()) >= {"itemId", "overrideType", "reason", "timestampUtc"}
        assert ov["overrideType"] in {"waiver", "manual_edit", "rejection"}
        assert "analyst@contoso.com" not in ov["reason"]
        assert "ws-private-lab" not in ov["reason"]

    verify_sanitized_decision_manifest(manifest)


class TestDecisionManifestUnittest(unittest.TestCase):
    def test_decision_manifest_sanitized_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            test_decision_manifest_includes_sanitized_overrides(Path(tmp))

