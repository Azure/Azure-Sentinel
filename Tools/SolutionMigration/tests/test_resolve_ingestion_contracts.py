from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from unittest import mock

import yaml

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
MIGRATION_ROOT = TOOLS.parent / "SentinelToXDRMigration"
sys.path.insert(0, str(MIGRATION_ROOT))
INGESTION_ROOT = TOOLS.parent / "AzureMonitorLogsIngestion"
sys.path.insert(0, str(INGESTION_ROOT))

import resolve_ingestion_contracts as planner


TARGET = {
    "tenantId": "tenant-id",
    "subscriptionId": "subscription-id",
    "workspaceResourceId": (
        "/subscriptions/subscription-id/resourceGroups/lab-rg/providers/"
        "Microsoft.OperationalInsights/workspaces/lab-workspace"
    ),
    "workspaceCustomerId": "workspace-customer-id",
}


def _write_yaml(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def _create_solution(root: Path, contract_root: Path) -> tuple[Path, Path]:
    solution = root / "Solutions" / "Example"
    rule_path = solution / "Analytic Rules" / "Nested" / "rule.yaml"
    detection_path = solution / "XDR Detections" / "Nested" / "detection.yaml"
    _write_yaml(
        rule_path,
        {
            "id": "rule-1",
            "name": "Synthetic network event",
            "query": (
                'CommonSecurityLog | where DeviceEventClassID == "733101"'
            ),
        },
    )
    _write_yaml(
        detection_path,
        {
            "id": "detection-1",
            "sourceRuleId": "rule-1",
            "name": "Synthetic network event",
            "query": (
                'CommonSecurityLog | where DeviceEventClassID == "733101"'
            ),
        },
    )
    destination = contract_root / "contracts" / "CommonSecurityLog.yaml"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        INGESTION_ROOT / "contracts" / "CommonSecurityLog.yaml",
        destination,
    )
    _write_yaml(
        contract_root / "registry.yaml",
        {
            "version": 1,
            "tables": [
                {
                    "table": "CommonSecurityLog",
                    "contract": "contracts/CommonSecurityLog.yaml",
                    "route": "logs-ingestion-api",
                    "inputKind": "custom-stream",
                    "outputKind": "standard-table",
                    "outputStream": "Microsoft-CommonSecurityLog",
                    "schemaReference": "https://learn.microsoft.com/azure/azure-monitor/reference/tables/commonsecuritylog",
                    "metadataReference": "https://api.loganalytics.io/v1/metadata",
                    "capabilityReference": "https://learn.microsoft.com/azure/azure-monitor/reference/tables-features",
                    "routeReference": "https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview",
                    "liveValidated": False,
                }
            ],
        },
    )
    return solution, rule_path


def test_recursive_inventory_plan_groups_by_table_and_binds_exact_target(tmp_path):
    solution, _ = _create_solution(tmp_path, tmp_path / "ingestion")

    plan = planner.build_plan(
        solution,
        TARGET,
        registry_path=tmp_path / "ingestion" / "registry.yaml",
    )

    assert plan["status"] == "planned"
    assert plan["writesPerformed"] is False
    assert plan["cloudCallsPerformed"] is False
    assert plan["target"] == TARGET
    assert plan["inventory"]["complete"] is True
    assert plan["inventory"]["recursiveRuleCount"] == 1
    assert plan["rules"][0]["status"] == "ready-for-fixture-review"
    assert plan["rules"][0]["sourcePath"] == "Analytic Rules/Nested/rule.yaml"
    assert plan["rules"][0]["customDetectionPath"] == (
        "XDR Detections/Nested/detection.yaml"
    )
    assert plan["rules"][0]["requiredSourceFields"] == {
        "DeviceEventClassID": "string"
    }
    assert len(plan["groups"]) == 1
    assert plan["groups"][0]["ruleIds"] == ["rule-1"]


def test_plan_blocks_predicate_fields_missing_from_registered_contract(tmp_path):
    solution, rule_path = _create_solution(tmp_path, tmp_path / "ingestion")
    query = (
        'CommonSecurityLog | where DeviceEventClassID == "733101" '
        "| where DestinationUserName == 'alice'"
    )
    rule = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    rule["query"] = query
    _write_yaml(rule_path, rule)
    detection_path = solution / "XDR Detections" / "Nested" / "detection.yaml"
    detection = yaml.safe_load(detection_path.read_text(encoding="utf-8"))
    detection["query"] = query
    _write_yaml(detection_path, detection)

    plan = planner.build_plan(
        solution,
        TARGET,
        registry_path=tmp_path / "ingestion" / "registry.yaml",
    )

    planned_rule = plan["rules"][0]
    assert planned_rule["status"] == "manual-review-required"
    assert planned_rule["requiredSourceFields"] == {
        "DeviceEventClassID": "string",
        "DestinationUserName": None,
    }
    assert any(
        "DestinationUserName" in blocker
        for blocker in planned_rule["contractResolution"]["blockers"]
    )


def test_plan_does_not_report_output_alias_as_a_source_requirement(tmp_path):
    solution, rule_path = _create_solution(tmp_path, tmp_path / "ingestion")
    query = (
        "CommonSecurityLog | extend EventClass = DeviceEventClassID "
        "| where EventClass == '733101'"
    )
    rule = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    rule["query"] = query
    _write_yaml(rule_path, rule)
    detection_path = solution / "XDR Detections" / "Nested" / "detection.yaml"
    detection = yaml.safe_load(detection_path.read_text(encoding="utf-8"))
    detection["query"] = query
    _write_yaml(detection_path, detection)

    plan = planner.build_plan(
        solution,
        TARGET,
        registry_path=tmp_path / "ingestion" / "registry.yaml",
    )

    planned_rule = plan["rules"][0]
    assert planned_rule["status"] == "manual-review-required"
    assert "EventClass" not in planned_rule["requiredSourceFields"]
    assert any(
        "EventClass" in blocker and "query alias" in blocker
        for blocker in planned_rule["contractResolution"]["blockers"]
    )


def test_plan_rejects_stale_inventory_and_target_identity(tmp_path):
    solution, rule_path = _create_solution(tmp_path, tmp_path / "ingestion")
    registry_path = tmp_path / "ingestion" / "registry.yaml"
    first = planner.build_plan(solution, TARGET, registry_path=registry_path)
    expected_inventory = first["inventory"]["sha256"]
    expected_target = first["targetSha256"]

    rule = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    rule["query"] += "\n| where DeviceProduct == 'ASA'"
    _write_yaml(rule_path, rule)
    changed_target = dict(TARGET, workspaceCustomerId="different-customer")
    stale = planner.build_plan(
        solution,
        changed_target,
        registry_path=registry_path,
        expected_inventory_sha256=expected_inventory,
        expected_target_sha256=expected_target,
    )

    assert stale["status"] == "stale-plan"
    assert len(stale["staleReasons"]) == 2
    assert stale["rules"][0]["sourceQuerySha256"] != first["rules"][0]["sourceQuerySha256"]


def test_planner_cli_requires_and_validates_locked_workspace_context(tmp_path, capsys):
    solution, _ = _create_solution(tmp_path, tmp_path / "ingestion")
    target_path = tmp_path / "qualification-target.json"
    target_path.write_text(json.dumps(TARGET), encoding="utf-8")
    output_path = tmp_path / "plan.json"

    result = planner.main(
        [
            "--solution",
            str(solution),
            "--target-context",
            str(target_path),
            "--registry",
            str(tmp_path / "ingestion" / "registry.yaml"),
            "--output",
            str(output_path),
        ]
    )

    capsys.readouterr()
    assert result == 0
    assert json.loads(output_path.read_text(encoding="utf-8"))["target"] == TARGET


def test_partial_selection_plans_only_selected_pairs_but_keeps_full_denominator(tmp_path):
    solution, first_rule = _create_solution(tmp_path, tmp_path / "ingestion")
    ids = [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
        "33333333-3333-3333-3333-333333333333",
    ]
    paths = []
    for index, rule_id in enumerate(ids):
        source_path = (
            first_rule if index == 0
            else solution / "Analytic Rules" / f"rule-{index}.yaml"
        )
        detection_path = (
            solution / "XDR Detections" / "Nested" / "detection.yaml"
            if index == 0
            else solution / "XDR Detections" / "Nested" / f"detection-{index}.yaml"
        )
        source = {
            "id": rule_id,
            "name": f"rule-{index}",
            "query": "CommonSecurityLog | where DeviceEventClassID == '733101'",
        }
        detection = {
            "id": f"xdr-{rule_id}",
            "sourceRuleId": rule_id,
            "name": f"detection-{index}",
            "query": "CommonSecurityLog | where DeviceEventClassID == '733101'",
        }
        _write_yaml(source_path, source)
        _write_yaml(detection_path, detection)
        paths.append((source_path, detection_path))

    from sentinel_xdr_migration.packaging_selection import _coverage_summary

    summary = {
        **_coverage_summary(
            [{"id": rule_id} for rule_id in ids],
            ids[:2],
        ),
        "outcome": "partial",
    }
    plan = {
        "runId": "run-partial",
        "planSha256": "a" * 64,
        "summary": summary,
        "selection": {
            "analyticRules": [
                source.relative_to(solution).as_posix()
                for source, _ in paths[:2]
            ],
            "xdrDetections": [
                detection.relative_to(solution).as_posix()
                for _, detection in paths[:2]
            ],
        },
        "analyticRules": [
            {"id": rule_id, "path": source.relative_to(solution).as_posix(), "included": index < 2}
            for index, (rule_id, (source, _)) in enumerate(zip(ids, paths))
        ],
        "xdrDetections": [
            {
                "id": f"xdr-{rule_id}",
                "sourceId": rule_id,
                "path": detection.relative_to(solution).as_posix(),
                "included": index < 2,
            }
            for index, (rule_id, (_, detection)) in enumerate(zip(ids, paths))
        ],
    }
    selection_path = solution / "Logs" / "sentinel-xdr-migration" / "run-partial" / "package-selection-plan.json"
    selection_path.parent.mkdir(parents=True)
    selection_path.write_text(json.dumps(plan), encoding="utf-8")

    with mock.patch.object(
        planner,
        "verify_applied_package_selection",
        return_value={
            "plan": plan,
            "planPath": selection_path.relative_to(solution).as_posix(),
            "receiptPath": "Logs/sentinel-xdr-migration/run-partial/package-selection-applied.json",
        },
    ):
        result = planner.build_plan(
            solution,
            TARGET,
            registry_path=tmp_path / "ingestion" / "registry.yaml",
            selection_plan_path=selection_path,
            expected_selection_plan_sha256="a" * 64,
        )

    assert result["inventory"]["complete"] is True
    assert result["inventory"]["recursiveRuleCount"] == 3
    assert result["qualificationScope"]["coverageNumerator"] == 2
    assert result["qualificationScope"]["coverageDenominator"] == 3
    assert result["qualificationScope"]["planSha256"] == "a" * 64
    assert [item["status"] for item in result["rules"]].count("not-selected") == 1
    assert {item.get("ruleId") for item in result["rules"] if item["status"] != "not-selected"} == set(ids[:2])
