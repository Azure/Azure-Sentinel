"""Unit tests for Qualification readiness and private configuration/support export hygiene."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
from uuid import uuid4

from solution_manager.core import workflow
from solution_manager.core.artifacts import report_directory
from solution_manager.qualification import (
    assess_qualification_readiness,
    audit_private_config_and_support_export,
)
from solution_manager.reporting.evidence import export_evidence

TARGET = {
    "tenantId": "11111111-1111-4111-8111-111111111111",
    "subscriptionId": "22222222-2222-4222-8222-222222222222",
    "resourceGroup": "rg-fixture",
    "workspaceResourceId": (
        "/subscriptions/22222222-2222-4222-8222-222222222222"
        "/resourceGroups/rg-fixture"
        "/providers/Microsoft.OperationalInsights/workspaces/ws-fixture"
    ),
    "workspaceCustomerId": "33333333-3333-4333-8333-333333333333",
}


def _make_solution() -> tuple[Path, Path]:
    scratch = Path.cwd() / f".readiness-support-tests-{uuid4().hex}"
    solution = scratch / "Solutions" / "Fixture"
    (solution / "Workbooks").mkdir(parents=True)
    (solution / "Data").mkdir()
    (scratch / ".gitignore").write_text("Solutions/**/Logs/\n", encoding="utf-8")
    (solution / "Workbooks" / "LinuxMachines.json").write_text(
        json.dumps({"version": "Notebook/1.0", "items": []}),
        encoding="utf-8",
    )
    (solution / "Data" / "Solution_Fixture.json").write_text(
        json.dumps(
            {
                "Name": "Fixture",
                "Version": "3.2.2",
                "Workbooks": ["Workbooks/LinuxMachines.json"],
            }
        ),
        encoding="utf-8",
    )
    return scratch, solution


def test_assess_qualification_readiness_separates_deployment_and_ingestion():
    scratch, solution = _make_solution()
    try:
        state = workflow.initialize_workflow(
            solution,
            workflow_profile="qualification",
            workbook_capability_version=1,
            version_bump="none",
            tenant_id=TARGET["tenantId"],
            subscription_id=TARGET["subscriptionId"],
            workspace_resource_id=TARGET["workspaceResourceId"],
            workspace_customer_id=TARGET["workspaceCustomerId"],
        )
        run_dir = report_directory(solution)
        initial_readiness = assess_qualification_readiness(solution, run_id=state["runId"])
        assert initial_readiness["status"] == "blocked"
        assert initial_readiness["deploymentAndIngestionSeparated"] is True
        assert initial_readiness["armWhatIfSupportedForXdrExtensions"] is False
        assert initial_readiness["authorizationChecks"]["targetLocked"]["status"] == "ready"
        assert initial_readiness["authorizationChecks"]["runtimeQueryConsent"]["status"] == "missing"

        (run_dir / "runtime-query-consent.json").write_text(
            json.dumps(
                {
                    "status": "approved",
                    "withdrawn": False,
                    "approvedFamilies": ["sentinelSourceQueryFamily", "defenderXdrQueryFamily"],
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "arm-preflight-consent.json").write_text(
            json.dumps({"status": "approved", "revoked": False}),
            encoding="utf-8",
        )
        (run_dir / "arm-validation-consent.json").write_text(
            json.dumps({"status": "approved", "withdrawn": False, "deploymentOnly": True}),
            encoding="utf-8",
        )
        (run_dir / "arm-preflight-result.json").write_text(
            json.dumps(
                {
                    "status": "ready",
                    "tenantMatches": True,
                    "subscriptionMatches": True,
                    "workspaceMatches": True,
                    "nonProduction": True,
                    "armDeploymentAllowed": True,
                    "disabledContentVerified": True,
                    "ownershipVerified": True,
                    "extensionResourceWriteAllowed": False,
                    "checks": {
                        "extensionResourceWriteAllowed": {"status": "not-required", "required": False}
                    },
                    "reasons": [],
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "qualification-dcr-preflight.json").write_text(
            json.dumps(
                {
                    "status": "ready",
                    "summary": {"total": 1, "ready": 1, "blocked": 0},
                    "candidates": [
                        {
                            "table": "Syslog",
                            "tableSchemaCompatibility": {"status": "compatible"},
                            "resourceProvisioningAuthorization": {"status": "ready"},
                            "ingestionAuthorization": {
                                "status": "ready",
                                "requiredAction": "Microsoft.Insights/Telemetry/Write",
                            },
                        }
                    ],
                    "blockers": [],
                }
            ),
            encoding="utf-8",
        )

        full_readiness = assess_qualification_readiness(solution, run_id=state["runId"])
        assert full_readiness["status"] == "ready"
        assert full_readiness["deploymentPermissionReadiness"]["ready"] is True
        assert full_readiness["ingestionPermissionReadiness"]["ready"] is True
    finally:
        shutil.rmtree(scratch)


def test_audit_private_config_and_support_export_detects_leaks():
    scratch, solution = _make_solution()
    try:
        (solution / ".env").write_text(
            f"AZURE_TENANT_ID={TARGET['tenantId']}\n"
            f"SENTINEL_WORKSPACE_RESOURCE_ID={TARGET['workspaceResourceId']}\n",
            encoding="utf-8",
        )
        state = workflow.initialize_workflow(
            solution,
            workflow_profile="qualification",
            workbook_capability_version=1,
            version_bump="none",
            tenant_id=TARGET["tenantId"],
            subscription_id=TARGET["subscriptionId"],
            workspace_resource_id=TARGET["workspaceResourceId"],
            workspace_customer_id=TARGET["workspaceCustomerId"],
        )
        export_evidence(solution)

        clean_audit = audit_private_config_and_support_export(solution, run_id=state["runId"])
        assert clean_audit["status"] == "isolated"
        assert clean_audit["privateConfigIsolatedToLocalUnexportedConfig"] is True
        assert clean_audit["supportExportsRedacted"] is True

        summary_md = solution / "Evidence" / state["runId"] / "summary.md"
        summary_md.write_text(
            summary_md.read_text(encoding="utf-8") + f"\nLeaked tenant: {TARGET['tenantId']}\n",
            encoding="utf-8",
        )
        leaked_audit = audit_private_config_and_support_export(solution, run_id=state["runId"])
        assert leaked_audit["status"] == "exposed-in-support-export"
        assert leaked_audit["supportExportsRedacted"] is False
    finally:
        shutil.rmtree(scratch)
