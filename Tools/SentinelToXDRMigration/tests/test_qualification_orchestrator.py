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


def test_initial_disabled_deployment_and_get_readback_receipts():
    from unittest.mock import patch
    from solution_manager.qualification.analytic_deployment import deploy_analytic_rules
    from solution_manager.qualification.deployment import deploy_solution

    scratch, sol_root = _create_solution_fixture(
        num_rules=1,
        num_sentinel_workbooks=0,
        num_defender_workbooks=0,
        num_detections=1,
        table_name="Syslog",
    )
    try:
        rule_id = "00000000-0000-4000-8000-000000000001"
        rule_path = sol_root / "Analytic Rules" / "rule_1.yaml"
        rule_path.write_text(
            yaml.safe_dump(
                {
                    "id": rule_id,
                    "name": "Fixture Rule 1",
                    "description": "Test rule",
                    "severity": "High",
                    "queryFrequency": "1h",
                    "queryPeriod": "2h",
                    "triggerOperator": "gt",
                    "triggerThreshold": 0,
                    "query": "Syslog | take 1",
                    "tactics": ["InitialAccess"],
                    "relevantTechniques": ["T1190"],
                    "entityMappings": [
                        {
                            "entityType": "Host",
                            "fieldMappings": [
                                {"identifier": "HostName", "columnName": "HostName"}
                            ],
                        }
                    ],
                    "version": "1.0.0",
                    "kind": "Scheduled",
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        det_path = sol_root / "XDR Detections" / "detection_1.yaml"
        det_path.write_text(
            yaml.safe_dump(
                {
                    "schemaVersion": "1.0.0",
                    "version": "3.1.0",
                    "kind": "CustomDetection",
                    "resourceType": "Microsoft.Security/detectionRules",
                    "apiVersion": "2026-06-01-preview",
                    "contentProvenance": {
                        "requiredWorkloads": [{"workload": "sentinel", "dataTypes": ["Syslog"]}],
                        "requiredDataConnectors": [],
                        "source": {
                            "platform": "Microsoft Sentinel",
                            "kind": "AnalyticsRule",
                            "id": rule_id,
                            "path": "Analytic Rules/rule_1.yaml",
                            "querySha256": "hash",
                            "schedule": {"queryFrequency": "1h", "queryPeriod": "1h"},
                        },
                        "conversion": {
                            "tool": "sentinel-to-xdr-migration",
                            "version": "0.1.0",
                            "status": "converted",
                            "reviewRequired": False,
                            "reviewReasons": [],
                            "requiredWorkloads": ["sentinel"],
                            "warnings": [],
                            "errors": [],
                        },
                    },
                    "properties": {
                        "id": f"xdr-{rule_id}",
                        "displayName": "Fixture Detection 1",
                        "status": "disabled",
                        "queryCondition": {"queryText": "Syslog | take 1"},
                        "schedule": {"frequency": "PT1H"},
                        "detectionAction": {
                            "alertTemplate": {
                                "title": "Fixture Detection 1",
                                "description": "Test",
                                "severity": "high",
                                "entityMappings": {
                                    "hosts": [{"id": "host1", "hostNameColumn": "HostName"}]
                                },
                            }
                        },
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        arm_calls: list[tuple[str, str]] = []

        def fake_arm_request(method, url, token, payload=None):
            arm_calls.append((method, url))
            if method == "PUT":
                assert payload["properties"]["enabled"] is False
                return 200, {"name": rule_id, "properties": {"enabled": False}}
            if method == "GET":
                return 200, {"name": rule_id, "properties": {"enabled": False}}
            raise AssertionError(f"Unexpected ARM method: {method}")

        with patch("solution_manager.qualification.analytic_deployment.require_locked_target", return_value=LAB_TARGET), patch(
            "solution_manager.qualification.analytic_deployment._arm_token", return_value="arm-tok"
        ), patch(
            "solution_manager.qualification.analytic_deployment._arm_request",
            side_effect=fake_arm_request,
        ):
            analytic_report = deploy_analytic_rules(
                sol_root,
                workspace_resource_id=LAB_TARGET["workspaceResourceId"],
                verify_readback=True,
            )

        assert analytic_report["succeeded"] == 1
        assert analytic_report["initialDisabled"] is True
        assert analytic_report["results"][0]["initialDisabled"] is True
        assert analytic_report["results"][0]["readbackVerified"] is True
        assert [m for m, _ in arm_calls] == ["PUT", "GET"]

        graph_calls: list[str] = []
        created_payload: dict = {}

        def fake_graph_request(method, url, token, body=None):
            graph_calls.append(method)
            if method == "GET" and not created_payload:
                return 404, {}
            if method == "POST":
                assert body["status"] == "disabled"
                created_payload.update(body)
                return 201, {**body, "isEnabled": False, "status": "disabled"}
            if method == "GET" and created_payload:
                return 200, {**created_payload, "isEnabled": False, "status": "disabled"}
            raise AssertionError(f"Unexpected Graph call: {method} {url}")

        (sol_root / "Data" / "Solution_HybridFixture.json").write_text(
            json.dumps({"Version": "3.1.0", "Metadata": "SolutionMetadata.json"}),
            encoding="utf-8",
        )
        (sol_root / "SolutionMetadata.json").write_text(
            json.dumps({"publisherId": "testpublisher", "offerId": "test-sentinel"}),
            encoding="utf-8",
        )

        with patch("solution_manager.qualification.deployment.require_locked_target", return_value=LAB_TARGET), patch(
            "solution_manager.qualification.deployment._deployment_token", return_value="graph-tok"
        ), patch(
            "solution_manager.qualification.deployment._graph_request",
            side_effect=fake_graph_request,
        ):
            xdr_report = deploy_solution(sol_root)

        assert xdr_report["succeeded"] == 1
        assert xdr_report["initialDisabled"] is True
        assert xdr_report["results"][0]["initialDisabled"] is True
        assert xdr_report["results"][0]["readbackVerified"] is True
        assert graph_calls == ["GET", "POST", "GET"]
    finally:
        shutil.rmtree(scratch)


def test_full_enable_fire_disable_lifecycle_and_tk_q11_readbacks():
    from unittest.mock import patch
    from solution_manager.qualification import alert_parity

    scratch, sol_root = _create_solution_fixture(
        num_rules=1,
        num_sentinel_workbooks=0,
        num_defender_workbooks=0,
        num_detections=1,
        table_name="Syslog",
    )
    try:
        contract = scratch / "contract.json"
        payload = scratch / "payload.json"
        plan_path = scratch / "batch-plan.json"
        contract.write_text("{}", encoding="utf-8")
        payload.write_text('[{"HostName": "host-tkq11"}]', encoding="utf-8")
        plan_path.write_text(
            json.dumps(
                {
                    "fixtures": [
                        {
                            "detection": "detection_1.yaml",
                            "contract": str(contract),
                            "payload": str(payload),
                            "scenarioMarker": "host-tkq11",
                            "expectedMatchKeys": ["host-tkq11"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        pair = {
            "detection": "detection_1.yaml",
            "displayName": "Fixture Detection 1",
            "analyticRuleId": "00000000-0000-4000-8000-000000000001",
            "customDetectionId": "xdr-rule-1",
            "entityMappings": {},
        }

        call_sequence: list[str] = []
        sentinel_enabled = False
        xdr_enabled = False

        def fake_arm(method, url, token, body=None):
            nonlocal sentinel_enabled
            if method == "GET":
                call_sequence.append(f"sentinel_get:{sentinel_enabled}")
                return 200, {
                    "name": "00000000-0000-4000-8000-000000000001",
                    "etag": "etag-1",
                    "kind": "Scheduled",
                    "properties": {
                        "displayName": "Fixture Rule 1",
                        "enabled": sentinel_enabled,
                        "query": "Syslog | where TimeGenerated > ago(1h)",
                    },
                }
            if method == "PUT":
                sentinel_enabled = bool(body["properties"]["enabled"])
                call_sequence.append(f"sentinel_put:{sentinel_enabled}")
                return 200, {"properties": {"enabled": sentinel_enabled}}
            raise AssertionError(f"Unexpected ARM request: {method} {url}")

        def fake_graph(method, url, token, body=None):
            nonlocal xdr_enabled
            if method == "GET":
                call_sequence.append(f"xdr_get:{xdr_enabled}")
                return 200, {
                    "id": "xdr-rule-1",
                    "displayName": "Fixture Detection 1",
                    "isEnabled": xdr_enabled,
                    "status": "enabled" if xdr_enabled else "disabled",
                }
            if method == "PATCH":
                xdr_enabled = bool(body.get("isEnabled"))
                call_sequence.append(f"xdr_patch:{xdr_enabled}")
                return 200, {
                    "id": "xdr-rule-1",
                    "isEnabled": xdr_enabled,
                    "status": "enabled" if xdr_enabled else "disabled",
                }
            raise AssertionError(f"Unexpected Graph request: {method} {url}")

        def fake_ingest(c, p):
            call_sequence.append("ingest_e2e_q01")
            return {"recordsAccepted": 1}

        with patch.object(alert_parity, "require_locked_target", return_value=LAB_TARGET), patch.object(
            alert_parity, "_arm_token", return_value="arm-tok"
        ), patch.object(
            alert_parity, "_deployment_token", return_value="graph-tok"
        ), patch.object(
            alert_parity, "_load_pairs", return_value=(sol_root, [pair])
        ), patch.object(
            alert_parity, "_arm_request", side_effect=fake_arm
        ), patch.object(
            alert_parity, "_graph_request", side_effect=fake_graph
        ), patch.object(
            alert_parity, "_ingest", side_effect=fake_ingest
        ):
            started = alert_parity.start_alert_parity_batch(sol_root, plan_path=plan_path)
            assert started["status"] == "awaiting-alerts"
            assert started["initialDisabled"] is True
            assert started["alertLifecycle"]["initialDisabled"] is True
            assert call_sequence.index("ingest_e2e_q01") < call_sequence.index("sentinel_put:True")
            assert call_sequence.index("ingest_e2e_q01") < call_sequence.index("xdr_patch:True")
            assert sentinel_enabled is True
            assert xdr_enabled is True

            sample_alert = {
                "matchKey": "host-tkq11",
                "severity": "high",
                "tactics": ["Execution"],
                "entities": {"hosts": [{"hostName": "host-tkq11"}]},
                "evidence": {"eventIds": ["host-tkq11"]},
            }
            report = alert_parity.poll_alert_parity_batch(
                sol_root,
                results={
                    "results": [
                        {
                            "detection": "detection_1.yaml",
                            "analyticRule": {"alerts": [sample_alert]},
                            "customDetection": {"alerts": [sample_alert]},
                        }
                    ]
                },
            )

        assert report["status"] == "passed"
        assert report["initialDisabled"] is True
        assert report["returnedToDisabled"] is True
        assert report["tkQ11Passed"] is True
        assert report["alertLifecycle"]["initialDisabled"] is True
        assert report["alertLifecycle"]["returnedToDisabled"] is True
        assert report["alertLifecycle"]["tkQ11Verified"] is True
        assert report["cleanup"][0]["disabled"] is True
        assert report["cleanup"][0]["returnedToDisabled"] is True
        assert sentinel_enabled is False
        assert xdr_enabled is False
        assert call_sequence[-2:] == ["sentinel_get:False", "xdr_get:False"]
    finally:
        shutil.rmtree(scratch)


def test_streaming_compiler_error_e2e_q02_captures_diagnostics_and_runs_finally_disable():
    from unittest.mock import patch
    from solution_manager.qualification import alert_parity

    scratch, sol_root = _create_solution_fixture(
        num_rules=1,
        num_sentinel_workbooks=0,
        num_defender_workbooks=0,
        num_detections=1,
        table_name="Syslog",
    )
    try:
        contract = scratch / "contract.json"
        payload = scratch / "payload.json"
        plan_path = scratch / "batch-plan.json"
        contract.write_text("{}", encoding="utf-8")
        payload.write_text('[{"HostName": "host-e2eq02"}]', encoding="utf-8")
        plan_path.write_text(
            json.dumps(
                {
                    "fixtures": [
                        {
                            "detection": "detection_1.yaml",
                            "contract": str(contract),
                            "payload": str(payload),
                            "scenarioMarker": "host-e2eq02",
                            "expectedMatchKeys": ["host-e2eq02"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        pair = {
            "detection": "detection_1.yaml",
            "displayName": "Fixture Detection 1",
            "analyticRuleId": "00000000-0000-4000-8000-000000000001",
            "customDetectionId": "xdr-rule-1",
            "entityMappings": {},
        }

        sentinel_enabled = False
        xdr_enabled = False
        call_log: list[str] = []

        def fake_arm(method, url, token, body=None):
            nonlocal sentinel_enabled
            if method == "GET":
                call_log.append(f"sentinel_get:{sentinel_enabled}")
                return 200, {
                    "name": "00000000-0000-4000-8000-000000000001",
                    "etag": "etag-1",
                    "kind": "Scheduled",
                    "properties": {
                        "displayName": "Fixture Rule 1",
                        "enabled": sentinel_enabled,
                        "query": "Syslog | where TimeGenerated > ago(1h)",
                    },
                }
            if method == "PUT":
                sentinel_enabled = bool(body["properties"]["enabled"])
                call_log.append(f"sentinel_put:{sentinel_enabled}")
                return 200, {"properties": {"enabled": sentinel_enabled}}
            raise AssertionError(f"Unexpected ARM request: {method} {url}")

        def fake_graph(method, url, token, body=None):
            nonlocal xdr_enabled
            if method == "GET":
                call_log.append(f"xdr_get:{xdr_enabled}")
                return 200, {
                    "id": "xdr-rule-1",
                    "displayName": "Fixture Detection 1",
                    "isEnabled": xdr_enabled,
                    "status": "enabled" if xdr_enabled else "disabled",
                }
            if method == "PATCH":
                if body.get("isEnabled") is True or body.get("status") == "enabled":
                    call_log.append("xdr_patch_enable_compiler_error")
                    return 400, {
                        "error": {
                            "code": "HuntingRuleQueryStreamingNotSupported",
                            "message": "KqlCompilationFailed: Unsupported streaming table or dynamic literal in query.",
                        }
                    }
                xdr_enabled = False
                call_log.append("xdr_patch:False")
                return 200, {"id": "xdr-rule-1", "isEnabled": False, "status": "disabled"}
            raise AssertionError(f"Unexpected Graph request: {method} {url}")

        with patch.object(alert_parity, "require_locked_target", return_value=LAB_TARGET), patch.object(
            alert_parity, "_arm_token", return_value="arm-tok"
        ), patch.object(
            alert_parity, "_deployment_token", return_value="graph-tok"
        ), patch.object(
            alert_parity, "_load_pairs", return_value=(sol_root, [pair])
        ), patch.object(
            alert_parity, "_arm_request", side_effect=fake_arm
        ), patch.object(
            alert_parity, "_graph_request", side_effect=fake_graph
        ), patch.object(
            alert_parity, "_ingest", return_value={"recordsAccepted": 1}
        ):
            batch_res = alert_parity.start_alert_parity_batch(sol_root, plan_path=plan_path)

        assert batch_res["status"] == "failed"
        assert batch_res["initialDisabled"] is True
        assert batch_res["returnedToDisabled"] is True
        assert batch_res["tkQ11Passed"] is True
        assert len(batch_res["e2eQ02Diagnostics"]) == 1
        diag = batch_res["e2eQ02Diagnostics"][0]
        assert diag["checkId"] == "E2E-Q02"
        assert diag["errorCode"] == "HuntingRuleQueryStreamingNotSupported"
        assert diag["stage"] == "enablement"
        assert diag["streamingCompilerError"] is True
        assert diag["ruleId"] == "xdr-rule-1"
        assert sentinel_enabled is False
        assert xdr_enabled is False
        assert call_log[-2:] == ["sentinel_get:False", "xdr_get:False"]

        # Also verify orchestrator run_rule_parity surfaces alertLifecycle and e2eQ02Diagnostics
        plan = plan_qualification_pipeline(sol_root, target=LAB_TARGET)
        rq_consent, dep_consent, ing_consent = _valid_consents_for_plan(plan)

        def failing_parity_evaluator(pair, ing_ev, target):
            return {
                "statusCode": 400,
                "errorPayload": {
                    "error": {
                        "code": "KqlCompilationFailed",
                        "message": "Dynamic literals are not supported in streaming custom detections.",
                    }
                },
                "initialDisabled": True,
                "returnedToDisabled": True,
                "parityVerified": False,
            }

        orch_state = run_qualification_pipeline(
            sol_root,
            target=LAB_TARGET,
            runtime_query_consent=rq_consent,
            deployment_consent=dep_consent,
            mock_ingestion_consent=ing_consent,
            parity_evaluator=failing_parity_evaluator,
            resume=False,
        )
        rp_stage = orch_state["qualificationStages"]["rule_parity"]
        assert rp_stage["status"] == "failed"
        assert rp_stage["alertLifecycle"]["initialDisabled"] is True
        assert rp_stage["alertLifecycle"]["returnedToDisabled"] is True
        assert rp_stage["alertLifecycle"]["tkQ11Verified"] is True
        assert len(rp_stage["alertLifecycle"]["e2eQ02Diagnostics"]) == 1
        assert rp_stage["alertLifecycle"]["e2eQ02Diagnostics"][0]["checkId"] == "E2E-Q02"
        assert rp_stage["alertLifecycle"]["e2eQ02Diagnostics"][0]["errorCode"] == "KqlCompilationFailed"
    finally:
        shutil.rmtree(scratch)


import unittest


class QualificationOrchestratorTestCase(unittest.TestCase):
    def test_plan_qualification_pipeline_builds_consolidated_preflight_packet(self):
        test_plan_qualification_pipeline_builds_consolidated_preflight_packet()

    def test_fail_closed_when_consents_missing_or_scope_mismatched(self):
        test_fail_closed_when_consents_missing_or_scope_mismatched()

    def test_resumable_progression_across_all_5_stages_for_hybrid_solution(self):
        test_resumable_progression_across_all_5_stages_for_hybrid_solution()

    def test_workbook_only_solution_like_aks_marks_rule_parity_not_applicable(self):
        test_workbook_only_solution_like_aks_marks_rule_parity_not_applicable()

    def test_evaluate_qualification_promotion_gate_pass_and_block_conditions(self):
        test_evaluate_qualification_promotion_gate_pass_and_block_conditions()

    def test_initial_disabled_deployment_and_get_readback_receipts(self):
        test_initial_disabled_deployment_and_get_readback_receipts()

    def test_full_enable_fire_disable_lifecycle_and_tk_q11_readbacks(self):
        test_full_enable_fire_disable_lifecycle_and_tk_q11_readbacks()

    def test_streaming_compiler_error_e2e_q02_captures_diagnostics_and_runs_finally_disable(self):
        test_streaming_compiler_error_e2e_q02_captures_diagnostics_and_runs_finally_disable()

