"""Unit tests for End-to-End Qualification Orchestrator (solution_manager.qualification.orchestrator)."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
from uuid import uuid4

import yaml

from solution_manager.core import workflow
from solution_manager.qualification import (
    QUALIFICATION_STAGES,
    QualificationOrchestrator,
    evaluate_qualification_promotion_gate,
    plan_qualification_pipeline,
    run_qualification_pipeline,
)

LAB_TARGET = {
    "tenantId": "11111111-1111-4111-8111-111111111111",
    "subscriptionId": "22222222-2222-4222-8222-222222222222",
    "resourceGroup": "rg-sentinel-xdr-lab",
    "workspaceResourceId": (
        "/subscriptions/22222222-2222-4222-8222-222222222222"
        "/resourceGroups/rg-sentinel-xdr-lab"
        "/providers/Microsoft.OperationalInsights/workspaces/ws-qualification-lab"
    ),
    "workspaceCustomerId": "33333333-3333-4333-8333-333333333333",
}


def _create_solution_fixture(
    *,
    num_rules: int = 1,
    num_sentinel_workbooks: int = 1,
    num_defender_workbooks: int = 1,
    num_detections: int = 1,
    table_name: str = "KubeEvents",
) -> tuple[Path, Path]:
    scratch = Path.cwd() / f".qual-orchestrator-test-{uuid4().hex}"
    sol_root = scratch / "Solutions" / "HybridFixture"
    (sol_root / "Data").mkdir(parents=True)
    (scratch / ".gitignore").write_text("Solutions/**/Logs/\n", encoding="utf-8")

    rule_rels: list[str] = []
    if num_rules > 0:
        (sol_root / "Analytic Rules").mkdir(parents=True, exist_ok=True)
        for idx in range(num_rules):
            rel = f"Analytic Rules/rule_{idx + 1}.yaml"
            rule_rels.append(rel)
            (sol_root / rel).write_text(
                yaml.safe_dump(
                    {
                        "id": f"00000000-0000-4000-8000-00000000000{idx + 1}",
                        "name": f"Fixture Rule {idx + 1}",
                        "kind": "Scheduled",
                        "severity": "High",
                        "query": f"{table_name} | where TimeGenerated > ago(1h)",
                        "requiredDataConnectors": [
                            {"connectorId": "FixtureConnector", "dataTypes": [table_name]}
                        ],
                    }
                ),
                encoding="utf-8",
            )

    det_rels: list[str] = []
    if num_detections > 0:
        (sol_root / "XDR Detections").mkdir(parents=True, exist_ok=True)
        for idx in range(num_detections):
            rel = f"XDR Detections/detection_{idx + 1}.yaml"
            det_rels.append(rel)
            (sol_root / rel).write_text(
                yaml.safe_dump(
                    {
                        "kind": "CustomDetection",
                        "contentProvenance": {
                            "origin": "sentinel-analytic-rule",
                            "source": {"id": f"00000000-0000-4000-8000-00000000000{idx + 1}"},
                            "requiredWorkloads": [{"workload": "sentinel", "dataTypes": [table_name]}],
                            "requiredDataConnectors": [
                                {"connectorId": "FixtureConnector", "dataTypes": [table_name]}
                            ],
                        },
                        "properties": {
                            "id": f"xdr-00000000-0000-4000-8000-00000000000{idx + 1}",
                            "displayName": f"Fixture Detection {idx + 1}",
                            "enabled": False,
                            "queryDefinition": {
                                "query": f"{table_name} | where TimeGenerated > ago(1h)"
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )

    wb_rels: list[str] = []
    if num_sentinel_workbooks > 0:
        (sol_root / "Workbooks").mkdir(parents=True, exist_ok=True)
        for idx in range(num_sentinel_workbooks):
            rel = f"Workbooks/Workbook_{idx + 1}.json"
            wb_rels.append(rel)
            (sol_root / rel).write_text(
                json.dumps(
                    {
                        "version": "Notebook/1.0",
                        "items": [
                            {
                                "type": 3,
                                "content": {
                                    "version": "KqlItem/1.0",
                                    "query": f"{table_name} | summarize count()",
                                    "queryType": 0,
                                    "resourceType": "microsoft.operationalinsights/workspaces",
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

    xdr_wb_rels: list[str] = []
    if num_defender_workbooks > 0:
        (sol_root / "XDR Workbooks").mkdir(parents=True, exist_ok=True)
        for idx in range(num_defender_workbooks):
            rel = f"XDR Workbooks/Workbook_{idx + 1}.json"
            xdr_wb_rels.append(rel)
            (sol_root / rel).write_text(
                json.dumps(
                    {
                        "version": "Notebook/1.0",
                        "items": [
                            {
                                "type": 3,
                                "content": {
                                    "version": "KqlItem/1.0",
                                    "query": f"{table_name} | summarize count()",
                                    "queryType": 0,
                                    "resourceType": "microsoft.security/workbooks",
                                },
                            }
                        ],
                        "contentProvenance": {
                            "source": {"path": f"Workbooks/Workbook_{idx + 1}.json"},
                            "requiredWorkloads": [{"workload": "sentinel", "dataTypes": [table_name]}],
                            "requiredDataConnectors": [
                                {"connectorId": "FixtureConnector", "dataTypes": [table_name]}
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )

    (sol_root / "Data" / "Solution_HybridFixture.json").write_text(
        json.dumps(
            {
                "Name": "HybridFixture",
                "Version": "3.2.2",
                "Analytic Rules": rule_rels,
                "Workbooks": wb_rels,
                "XDR Workbooks": xdr_wb_rels,
                "XDR Detections": det_rels,
            }
        ),
        encoding="utf-8",
    )
    return scratch, sol_root


def _valid_consents_for_plan(plan: dict) -> tuple[dict, dict, dict]:
    plan_sha = plan["planSha256"]
    target = plan["target"]
    counts = plan["expectedContentCounts"]
    tables = plan["mockIngestionPreapproval"]["targetTables"]
    streams = plan["mockIngestionPreapproval"]["streamNames"]
    runtime_query_consent = {
        "approved": True,
        "status": "approved",
        "readOnly": True,
        "resourceMutation": False,
        "approvedFamilies": ["sentinelSourceQueryFamily", "defenderXdrQueryFamily"],
        "planSha256": plan_sha,
        "target": target,
    }
    deployment_consent = {
        "approved": True,
        "status": "approved",
        "enabled": False,
        "allResourcesDeployedDisabled": True,
        "expectedContentCounts": counts,
        "planSha256": plan_sha,
        "target": target,
    }
    mock_ingestion_consent = {
        "approved": True,
        "status": "approved",
        "syntheticOnly": True,
        "approvedTables": tables,
        "approvedStreams": streams,
        "planSha256": plan_sha,
        "target": target,
    }
    return runtime_query_consent, deployment_consent, mock_ingestion_consent


def test_plan_qualification_pipeline_builds_consolidated_preflight_packet():
    scratch, sol_root = _create_solution_fixture(
        num_rules=2,
        num_sentinel_workbooks=1,
        num_defender_workbooks=1,
        num_detections=2,
        table_name="KubeEvents",
    )
    try:
        plan = plan_qualification_pipeline(sol_root, target=LAB_TARGET)
        packet = plan["consolidatedPreflightPacket"]

        assert plan["armWhatIfSupportedForXdrExtensions"] is False
        assert packet["armWhatIfSupportedForXdrExtensions"] is False
        assert packet["deploymentPreapproval"]["armWhatIfSupportedForXdrExtensions"] is False
        assert (
            packet["deploymentPreapproval"]["validationStrategy"]
            == "arm-template-validation-and-live-disabled-readback"
        )

        counts = packet["expectedContentCounts"]
        assert counts["sentinelRulesCount"] == 2
        assert counts["workbooksCount"] == 2
        assert counts["customDetectionsCount"] == 2
        assert "2 Sentinel rules, 2 workbooks, and 2 custom detections" in packet["deploymentScopeSummary"]
        assert "2 Sentinel rules, 2 workbooks, and 2 custom detections" in packet["deploymentPreapproval"]["prompt"]

        assert packet["runtimeQueryConsent"]["readOnly"] is True
        assert packet["runtimeQueryConsent"]["resourceMutation"] is False
        assert set(packet["runtimeQueryConsent"]["requiredFamilies"]) == {
            "sentinelSourceQueryFamily",
            "defenderXdrQueryFamily",
        }

        assert packet["mockIngestionPreapproval"]["targetTables"] == ["KubeEvents"]
        assert packet["mockIngestionPreapproval"]["streamNames"] == ["Custom-KubeEvents"]
        assert packet["stages"]["rule_parity"]["required"] is True
        assert packet["stages"]["workbook_qualification"]["required"] is True
    finally:
        shutil.rmtree(scratch)


def test_fail_closed_when_consents_missing_or_scope_mismatched():
    scratch, sol_root = _create_solution_fixture(
        num_rules=1,
        num_sentinel_workbooks=1,
        num_defender_workbooks=1,
        num_detections=1,
        table_name="Syslog",
    )
    try:
        plan = plan_qualification_pipeline(sol_root, target=LAB_TARGET)
        rq_consent, dep_consent, ing_consent = _valid_consents_for_plan(plan)

        # 1. Missing runtime query consent -> fails closed at preflight without invoking deployment
        deploy_called = []
        state_no_rq = run_qualification_pipeline(
            sol_root,
            target=LAB_TARGET,
            runtime_query_consent=None,
            deployment_consent=dep_consent,
            mock_ingestion_consent=ing_consent,
            deployment_runner=lambda req: deploy_called.append(req) or {"status": "succeeded"},
        )
        assert state_no_rq["status"] == "blocked"
        assert state_no_rq["preflightPassed"] is False
        assert state_no_rq["deploymentVerified"] is False
        assert deploy_called == []

        # 2. Scope mismatch on deployment consent (wrong customDetectionsCount) -> fails closed
        mismatched_dep = {
            **dep_consent,
            "expectedContentCounts": {
                **dep_consent["expectedContentCounts"],
                "customDetectionsCount": 99,
            },
        }
        state_bad_dep = run_qualification_pipeline(
            sol_root,
            target=LAB_TARGET,
            runtime_query_consent=rq_consent,
            deployment_consent=mismatched_dep,
            mock_ingestion_consent=ing_consent,
            deployment_runner=lambda req: deploy_called.append(req) or {"status": "succeeded"},
            resume=False,
        )
        assert state_bad_dep["status"] == "blocked"
        assert state_bad_dep["preflightPassed"] is False
        assert deploy_called == []
        assert any(
            "scope mismatch" in r
            for r in state_bad_dep["qualificationStages"]["preflight"]["reasons"]
        )

        # 3. Unapproved target table in mock_ingestion_consent -> fails closed
        mismatched_ing = {
            **ing_consent,
            "approvedTables": ["UnrelatedTable_CL"],
        }
        state_bad_ing = run_qualification_pipeline(
            sol_root,
            target=LAB_TARGET,
            runtime_query_consent=rq_consent,
            deployment_consent=dep_consent,
            mock_ingestion_consent=mismatched_ing,
            deployment_runner=lambda req: deploy_called.append(req) or {"status": "succeeded"},
            resume=False,
        )
        assert state_bad_ing["status"] == "blocked"
        assert state_bad_ing["preflightPassed"] is False
        assert deploy_called == []
    finally:
        shutil.rmtree(scratch)


def test_resumable_progression_across_all_5_stages_for_hybrid_solution():
    scratch, sol_root = _create_solution_fixture(
        num_rules=1,
        num_sentinel_workbooks=1,
        num_defender_workbooks=1,
        num_detections=1,
        table_name="Syslog",
    )
    try:
        plan = plan_qualification_pipeline(sol_root, target=LAB_TARGET)
        rq_consent, dep_consent, ing_consent = _valid_consents_for_plan(plan)

        stage_calls: list[str] = []

        def deploy_cb(req):
            stage_calls.append("deployment")
            assert req["enabled"] is False
            assert req["armWhatIfSupportedForXdrExtensions"] is False
            return {"status": "succeeded", "writeAttempted": True, "enabled": False}

        def readback_cb(req, res):
            stage_calls.append("readback")
            return {"status": "passed", "httpMethod": "GET", "readbackVerified": True, "allDisabledVerified": True}

        def ingest_cb(stream, records, target):
            stage_calls.append(f"ingest:{stream['streamName']}")
            return {"status": "accepted", "recordCount": len(records), "ingestionTimestamp": "2026-10-07T12:05:00Z"}

        def parity_cb(pair, ing_ev, target):
            stage_calls.append(f"parity:{pair['sentinelRuleId']}")
            rows = [{"HostName": "node-1", "Severity": "High"}]
            return {"sentinelRows": rows, "xdrRows": rows, "parityVerified": True}

        def wb_query_cb(wb_path, target):
            stage_calls.append(f"wb_query:{wb_path}")
            return {"workbook": wb_path, "status": "passed", "executedQueryCount": 5, "failedQueryCount": 0}

        def pw_cb(wb_path, target):
            stage_calls.append(f"playwright:{wb_path}")
            return {
                "workbook": wb_path,
                "status": "passed",
                "tilesRendered": True,
                "saveEditObserved": False,
                "queryErrors": [],
                "javascriptErrors": [],
            }

        # Step 1: Run up to deployment
        partial_state = run_qualification_pipeline(
            sol_root,
            target=LAB_TARGET,
            runtime_query_consent=rq_consent,
            deployment_consent=dep_consent,
            mock_ingestion_consent=ing_consent,
            deployment_runner=deploy_cb,
            readback_verifier=readback_cb,
            ingestion_client=ingest_cb,
            parity_evaluator=parity_cb,
            workbook_query_runner=wb_query_cb,
            playwright_runner=pw_cb,
            up_to_stage="deployment",
        )
        assert partial_state["preflightPassed"] is True
        assert partial_state["deploymentVerified"] is True
        assert partial_state["mockIngestionVerified"] is False
        assert partial_state["completedStages"] == ["preflight", "deployment"]
        assert stage_calls == ["deployment", "readback"]

        # Step 2: Resume from saved state and complete remaining stages without re-running deployment
        final_state = run_qualification_pipeline(
            sol_root,
            target=LAB_TARGET,
            runtime_query_consent=rq_consent,
            deployment_consent=dep_consent,
            mock_ingestion_consent=ing_consent,
            deployment_runner=deploy_cb,
            readback_verifier=readback_cb,
            ingestion_client=ingest_cb,
            parity_evaluator=parity_cb,
            workbook_query_runner=wb_query_cb,
            playwright_runner=pw_cb,
            resume=True,
        )
        # Deployment and readback were NOT called a second time on resume
        assert stage_calls.count("deployment") == 1
        assert stage_calls.count("readback") == 1
        assert "ingest:Custom-Syslog" in stage_calls
        assert any(c.startswith("parity:") for c in stage_calls)
        assert any(c.startswith("wb_query:") for c in stage_calls)
        assert any(c.startswith("playwright:") for c in stage_calls)

        assert final_state["completedStages"] == list(QUALIFICATION_STAGES)
        assert final_state["mockIngestionVerified"] is True
        assert final_state["ingestionEvidence"]["table"] == "Syslog"
        assert final_state["ingestionEvidence"]["landingQueryVerified"] is True
        assert final_state["ruleParityVerified"] is True
        assert final_state["alertParityVerified"] is True
        assert final_state["workbookQualificationVerified"] is True
        assert final_state["functionalQualificationVerified"] is True
        assert final_state["workbookContractResult"]["accepted"] is True
        assert final_state["sanitizedEvidenceReady"] is True

        gate = evaluate_qualification_promotion_gate(final_state)
        assert gate["passed"] is True
        assert gate["promoted"] is True
        assert gate["missingGates"] == []

        wf_state = workflow._load(sol_root)[1]
        assert wf_state["workflowStatus"] == "completed"
        assert wf_state["stages"]["deployment"]["status"] == "passed"
        assert wf_state["stages"]["mockIngestion"]["status"] == "passed"
        assert wf_state["stages"]["alertParity"]["status"] == "passed"
    finally:
        shutil.rmtree(scratch)


def test_workbook_only_solution_like_aks_marks_rule_parity_not_applicable():
    scratch, sol_root = _create_solution_fixture(
        num_rules=0,
        num_sentinel_workbooks=1,
        num_defender_workbooks=1,
        num_detections=0,
        table_name="KubeEvents",
    )
    try:
        plan = plan_qualification_pipeline(sol_root, target=LAB_TARGET)
        assert "0 Sentinel rules, 2 workbooks, and 0 custom detections" in plan["deploymentScopeSummary"]
        assert plan["stages"]["rule_parity"]["required"] is False
        assert plan["stages"]["workbook_qualification"]["required"] is True

        rq_consent, dep_consent, ing_consent = _valid_consents_for_plan(plan)
        final_state = run_qualification_pipeline(
            sol_root,
            target=LAB_TARGET,
            runtime_query_consent=rq_consent,
            deployment_consent=dep_consent,
            mock_ingestion_consent=ing_consent,
        )

        assert final_state["qualificationStages"]["rule_parity"]["status"] == "not_applicable"
        assert final_state["ruleParityVerified"] == "not_applicable"
        assert final_state["alertParityVerified"] == "not_applicable"
        assert final_state["workbookQualificationVerified"] is True
        assert final_state["functionalQualificationVerified"] is True

        gate = evaluate_qualification_promotion_gate(final_state)
        assert gate["passed"] is True
        assert gate["ruleParityVerified"] == "not_applicable"
        assert gate["workbookQualificationVerified"] is True

        wf_state = workflow._load(sol_root)[1]
        assert wf_state["stages"]["alertParity"]["status"] == "notRequired"
    finally:
        shutil.rmtree(scratch)


def test_evaluate_qualification_promotion_gate_pass_and_block_conditions():
    # 1. Hybrid solution with all gates satisfied -> passes
    passing_hybrid = evaluate_qualification_promotion_gate(
        {
            "expectedContentCounts": {
                "sentinelRulesCount": 1,
                "workbooksCount": 2,
                "customDetectionsCount": 1,
            },
            "preflightPassed": True,
            "deploymentVerified": True,
            "mockIngestionVerified": True,
            "ruleParityVerified": True,
            "workbookQualificationVerified": True,
            "sanitizedEvidenceReady": True,
        }
    )
    assert passing_hybrid["passed"] is True
    assert passing_hybrid["status"] == "passed"
    assert passing_hybrid["blockers"] == []

    # 2. Workbook-only solution (0 rules) automatically marks ruleParityVerified="not_applicable" -> passes
    passing_wb_only = evaluate_qualification_promotion_gate(
        {
            "expectedContentCounts": {
                "sentinelRulesCount": 0,
                "workbooksCount": 2,
                "customDetectionsCount": 0,
            },
            "preflightPassed": True,
            "deploymentVerified": True,
            "mockIngestionVerified": True,
            "workbookQualificationVerified": True,
            "sanitizedEvidenceReady": True,
        }
    )
    assert passing_wb_only["passed"] is True
    assert passing_wb_only["ruleParityVerified"] == "not_applicable"

    # 3. Rules-only solution (0 workbooks) automatically marks workbookQualificationVerified="not_applicable" -> passes
    passing_rules_only = evaluate_qualification_promotion_gate(
        {
            "expectedContentCounts": {
                "sentinelRulesCount": 2,
                "workbooksCount": 0,
                "customDetectionsCount": 2,
            },
            "preflightPassed": True,
            "deploymentVerified": True,
            "mockIngestionVerified": True,
            "ruleParityVerified": True,
            "sanitizedEvidenceReady": True,
        }
    )
    assert passing_rules_only["passed"] is True
    assert passing_rules_only["workbookQualificationVerified"] == "not_applicable"

    # 4. Blocked when sanitizedEvidenceReady is False or ruleParityVerified is False
    blocked = evaluate_qualification_promotion_gate(
        {
            "expectedContentCounts": {
                "sentinelRulesCount": 1,
                "workbooksCount": 1,
                "customDetectionsCount": 1,
            },
            "preflightPassed": True,
            "deploymentVerified": True,
            "mockIngestionVerified": True,
            "ruleParityVerified": False,
            "workbookQualificationVerified": True,
            "sanitizedEvidenceReady": False,
        }
    )
    assert blocked["passed"] is False
    assert blocked["status"] == "blocked"
    assert "ruleParityVerified" in blocked["missingGates"]
    assert "sanitizedEvidenceReady" in blocked["missingGates"]
