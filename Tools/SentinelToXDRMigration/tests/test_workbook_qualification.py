from __future__ import annotations

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import shutil
from unittest import mock
from uuid import uuid4

import pytest
import yaml

from sentinel_xdr_migration import workbook_qualification as qualification
from sentinel_xdr_migration import workbook_workflow, workflow, runtime, cli
from sentinel_xdr_migration._workbook_core.workbook_mock import inventory
from sentinel_xdr_migration.artifacts import artifact_path, report_directory, using_run
from test_workbook_arm_validation import TARGET


@pytest.fixture
def qualified_source():
    scratch = Path.cwd() / f".workbook-qualification-tests-{uuid4().hex}"
    root = scratch / "Solutions" / "Fixture"
    (root / "Workbooks").mkdir(parents=True)
    (root / "Data").mkdir()
    (scratch / ".gitignore").write_text("Solutions/**/Logs/\n")
    original = Path(__file__).parent / "fixtures/workbooks/sources/Syslog/Workbooks/LinuxMachines.json"
    source = root / "Workbooks/LinuxMachines.json"
    source.write_bytes(original.read_bytes())
    (root / "Data/Solution_Fixture.json").write_text(json.dumps({
        "Name": "Fixture", "Version": "3.2.3",
        "Workbooks": ["Workbooks/LinuxMachines.json"],
    }))
    state = workflow.initialize_workflow(
        root, workflow_profile="qualification", workbook_capability_version=1,
        tenant_id=TARGET["tenantId"], subscription_id=TARGET["subscriptionId"],
        workspace_resource_id=TARGET["workspaceResourceId"],
        workspace_customer_id=TARGET["workspaceCustomerId"],
    )
    try:
        with using_run(root, state["runId"]):
            resolutions = {
                row["sourcePath"]: {
                    "querySha256": row["querySha256"], "tables": row["tables"],
                    "evidence": "Reviewed complete public synthetic fixture query contract.",
                }
                for row in inventory(json.loads(source.read_bytes()))
            }
            config = artifact_path(root, "migration-config.yaml", create_parent=True)
            config.write_text(yaml.safe_dump({
                "targetVersion": "3.2.3",
                "workbookResolutions": {"Workbooks/LinuxMachines.json": resolutions},
                "workbookDependencies": {"Workbooks/LinuxMachines.json": {
                    "requiredWorkloads": [{"workload": "sentinel", "dataTypes": ["Syslog"]}],
                    "requiredDataConnectors": [{"connectorId": "FixtureSyslog", "dataTypes": ["Syslog"]}],
                }},
            }))
            workflow.start_workflow_stage(root, "discovery")
            workflow.complete_workflow_stage(root, "discovery", status="passed")
            workflow.start_workflow_stage(root, "conversion")
            result = workbook_workflow.convert_content(root)
            assert result["workbooks"]["selectedBlocked"] == 0
            workflow.complete_workflow_stage(root, "conversion", status="passed")
            yield root, state
    finally:
        shutil.rmtree(scratch)


def query_plan(root):
    return qualification.plan_workbook_queries(
        root, workbook="XDR Workbooks/LinuxMachines.json", clock="2026-10-07T12:00:00Z",
    )


def consent(plan):
    return qualification.review_workbook_query_consent(
        plan, actor="fixture-reviewer", reference="explicit-fixture-approval", approved=True,
    )


def providers(plan):
    def provider(side):
        expected = {
            row["querySha256"]: row["expected"]
            for row in plan["queries"] if row["side"] == side
        }

        def execute(query, target):
            digest = hashlib.sha256(query.encode()).hexdigest()
            result = expected[digest]
            return {
                "status": "passed", "complete": True, "provider": side,
                "target": target, "querySha256": digest,
                "result": {"columns": deepcopy(result["columns"]), "rows": deepcopy(result["rows"])},
            }

        return execute

    return {side: provider(side) for side in ("sentinel", "advanced-hunting")}


def ui_plan(root):
    kinds = ("pickers", "dependent-refresh", "filters", "drill-down", "reload", "layout", "conditional-visibility")
    return qualification.plan_workbook_ui(
        root, workbook="XDR Workbooks/LinuxMachines.json",
        url="https://security.microsoft.com/workbooks/fixture",
        readiness_selectors={"tenant": "#tenant", "workbook": "#workbook", "ready": "#ready"},
        steps=[{"id": kind, "kind": kind, "action": "observe"} for kind in kinds],
        background_activity_review="Explicit synthetic service-worker and background-request review.",
    )


def browser(plan):
    return {
        "target": plan["target"], "url": plan["url"],
        "readiness": {
            "tenantId": plan["target"]["tenantId"], "contentId": plan["contentId"],
            "instanceId": plan["instanceId"], "ready": True,
        },
        "steps": [{"id": step["id"], "kind": step["kind"], "status": "passed", "evidence": "Synthetic browser fixture observation."} for step in plan["steps"]],
        "queryErrors": [], "javascriptErrors": [], "saveEditObserved": False,
        "backgroundActivityReview": plan["backgroundActivityReview"],
    }


def test_plan_binds_all_exact_parameter_cases_and_independent_diagnostics(qualified_source):
    root, state = qualified_source
    plan = query_plan(root)
    assert len(plan["queries"]) == 202
    for side in ("sentinel", "advanced-hunting"):
        assert len({row["caseId"] for row in plan["queries"] if row["side"] == side}) == 101
    assert plan["runId"] == state["runId"]
    assert plan["ingestion"] == "not-ingestible"
    assert query_plan(root) == plan
    assert plan["targetSha256"] == hashlib.sha256((root / plan["workbook"]).read_bytes()).hexdigest()


def test_workbook_only_content_validation_does_not_require_installed_ui(qualified_source):
    root, state = qualified_source
    assert state["context"]["workbookQualificationAfterArm"] is True
    workbook_workflow.validate_content(root)
    workflow.start_workflow_stage(root, "validation")
    workflow.complete_workflow_stage(root, "validation", status="passed")
    current = workflow._load(root)[1]
    artifacts = current["stages"]["validation"]["artifacts"]
    assert artifacts["validationMode"] == "workbook-content"
    assert artifacts["workbookQueryStatus"] == artifacts["workbookUiStatus"] == "not-run"
    with pytest.raises(ValueError):
        qualification.require_current_qualification(root, current)
    current["stages"]["report"]["status"] = "running"
    state_path = workflow._load(root)[0]
    workflow._write(state_path, current)
    with pytest.raises(ValueError, match="query and UI qualification evidence is missing"):
        workflow.complete_workflow_stage(root, "report", status="passed")


def test_complete_exact_execution_and_ui_are_separate(qualified_source):
    root, state = qualified_source
    plan = query_plan(root)
    approval = consent(plan)
    result = qualification.execute_workbook_queries(
        root, plan, read_consent=lambda: approval, providers=providers(plan),
    )
    assert result["cases"] == 202
    assert result["uiStatus"] == "not-run"
    with pytest.raises(ValueError, match="UI qualification evidence is missing"):
        qualification.require_current_qualification(root, workflow._load(root)[1])
    portal = ui_plan(root)
    qualification.execute_workbook_ui(root, portal, read_consent=lambda: consent(portal), browser_runner=browser)
    qualification.require_current_qualification(root, workflow._load(root)[1])


@pytest.mark.parametrize("change", ["declined", "withdrawn", "hash", "target"])
def test_query_consent_blocks_before_provider_dispatch(qualified_source, change):
    root, _ = qualified_source
    plan = query_plan(root)
    approval = consent(plan)
    if change == "declined":
        approval["approved"] = False
    elif change == "withdrawn":
        approval["withdrawn"] = True
    elif change == "hash":
        approval["planSha256"] = "0" * 64
    else:
        approval["target"] = {**approval["target"], "tenantId": str(uuid4())}
    provider = mock.Mock()
    with pytest.raises(ValueError, match="consent"):
        qualification.execute_workbook_queries(
            root, plan, read_consent=lambda: approval,
            providers={"sentinel": provider, "advanced-hunting": mock.Mock()},
        )
    provider.assert_not_called()


def test_edited_plan_and_target_cannot_dispatch(qualified_source):
    root, _ = qualified_source
    plan = query_plan(root)
    approval = consent(plan)
    plan["queries"][0]["query"] += "\n| take 0"
    provider = mock.Mock()
    with pytest.raises(ValueError, match="stale or has been edited"):
        qualification.execute_workbook_queries(
            root, plan, read_consent=lambda: approval,
            providers={"sentinel": provider, "advanced-hunting": mock.Mock()},
        )
    provider.assert_not_called()


@pytest.mark.parametrize("fault", ["partial", "wrong-query", "wrong-target", "cells"])
def test_provider_errors_and_exact_result_mismatch_persist_failure(qualified_source, fault):
    root, _ = qualified_source
    plan = query_plan(root)
    callbacks = providers(plan)
    original = callbacks["sentinel"]

    def faulty(query, target):
        result = original(query, target)
        if fault == "partial":
            result["complete"] = False
        elif fault == "wrong-query":
            result["querySha256"] = "0" * 64
        elif fault == "wrong-target":
            result["target"] = {**target, "tenantId": str(uuid4())}
        else:
            result["result"]["rows"] = []
        return result

    callbacks["sentinel"] = faulty
    with pytest.raises(ValueError):
        qualification.execute_workbook_queries(root, plan, read_consent=lambda: consent(plan), providers=callbacks)
    receipt = json.loads((report_directory(root) / f"workbook-queries.{plan['contentId']}.json").read_bytes())
    assert receipt["status"] == "failed"
    assert receipt["results"] == []


@pytest.mark.parametrize("fault", ["save", "javascript", "missing-step", "tenant", "instance", "ui-query-consent"])
def test_ui_errors_incomplete_steps_and_wrong_consent_are_not_qualification(qualified_source, fault):
    root, _ = qualified_source
    plan = ui_plan(root)
    approval = consent(query_plan(root)) if fault == "ui-query-consent" else consent(plan)

    def faulty(current):
        capture = browser(current)
        if fault == "save":
            capture["saveEditObserved"] = True
        elif fault == "javascript":
            capture["javascriptErrors"] = ["Synthetic error"]
        elif fault == "missing-step":
            capture["steps"].pop()
        elif fault == "tenant":
            capture["readiness"]["tenantId"] = str(uuid4())
        elif fault == "instance":
            capture["readiness"]["instanceId"] = str(uuid4())
        return capture

    with pytest.raises(ValueError):
        qualification.execute_workbook_ui(root, plan, read_consent=lambda: approval, browser_runner=faulty)


def test_query_schema_normalization_preserves_exact_values():
    result = qualification._normalize_result(
        [{"name": "TimeGenerated", "type": "DateTime"}, {"name": "Count", "type": "Int64"}],
        [{"TimeGenerated": "2026-10-07T12:00:00+00:00", "Count": 2}],
    )
    assert result == {
        "columns": [{"name": "TimeGenerated", "type": "datetime"}, {"name": "Count", "type": "long"}],
        "rows": [["2026-10-07T12:00:00Z", 2]],
    }
    with pytest.raises(ValueError, match="timezone-less"):
        qualification._normalize_result([{"name": "Time", "type": "datetime"}], [["2026-10-07T12:00:00"]])
    with pytest.raises(ValueError, match="unsupported"):
        qualification._normalize_result([{"name": "Count", "type": "Unknown"}], [[2]])


def test_graph_full_capture_is_opt_in_and_never_uses_truncated_sample():
    rows = [{"Count": index} for index in range(runtime.MAX_ADVANCED_HUNTING_SAMPLE_ROWS + 1)]
    body = {"schema": [{"name": "Count", "type": "Int64"}], "results": rows}
    response = mock.MagicMock()
    response.__enter__.return_value = response
    response.status = 200
    response.read.return_value = json.dumps(body).encode()
    with mock.patch.object(runtime.urllib.request, "urlopen", return_value=response):
        old = runtime.run_advanced_hunting_query("datatable(Count:long)[1]", _token="fixture-only")
        complete = runtime.run_advanced_hunting_query(
            "datatable(Count:long)[1]", _token="fixture-only", capture_full_results=True,
        )
    assert "results" not in old
    assert old["sampleRowsTruncated"] is True
    assert complete["results"] == rows
    with pytest.raises(ValueError, match="boolean"):
        runtime.run_advanced_hunting_query("query", capture_full_results="true")


def cli_run(arguments):
    stdout, stderr = io.StringIO(), io.StringIO()
    with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
        code = cli.main(arguments)
    return code, json.loads(stdout.getvalue()) if stdout.getvalue() else None, stderr.getvalue()


def test_qualification_cli_exact_plan_review_execute_and_withdrawal(qualified_source):
    root, state = qualified_source
    common = ["--solution", str(root), "--run-id", state["runId"]]
    code, planned, error = cli_run([
        "workbook-query-plan", *common,
        "--workbook", "XDR Workbooks/LinuxMachines.json", "--clock", "2026-10-07T12:00:00Z",
    ])
    assert code == 0, error
    assert planned["queryCount"] == 202
    binding = [
        "--plan", planned["planPath"], "--plan-sha256", planned["planSha256"],
    ]
    code, _, error = cli_run([
        "workbook-query-review", *common, *binding,
        "--actor", "fixture-reviewer", "--reference", "explicit-fixture-approval", "--decision", "approved",
    ])
    assert code == 0, error
    with mock.patch.object(qualification, "default_query_providers", return_value=providers(query_plan(root))):
        code, executed, error = cli_run(["workbook-query-execute", *common, *binding])
    assert code == 0, error
    assert executed["cases"] == 202
    code, revoked, error = cli_run([
        "workbook-query-revoke", *common, "--plan", planned["planPath"],
        "--actor", "fixture-reviewer", "--reference", "explicit-withdrawal",
    ])
    assert code == 0, error
    assert revoked["status"] == "withdrawn"
    with mock.patch.object(qualification, "default_query_providers", return_value=providers(query_plan(root))):
        code, _, error = cli_run(["workbook-query-execute", *common, *binding])
    assert code == 2
    assert "withdrawn" in error


def test_qualification_cli_requires_exact_run_and_declines_authoring(qualified_source):
    root, state = qualified_source
    with pytest.raises(SystemExit) as error:
        cli.main(["workbook-query-plan", "--solution", str(root),
                  "--workbook", "XDR Workbooks/LinuxMachines.json", "--clock", "2026-10-07T12:00:00Z"])
    assert error.value.code == 2
    state_path, current = workflow._load(root)
    current["context"]["workflowProfile"] = "authoring"
    current["context"].pop("workbookQualificationAfterArm")
    workflow._write(state_path, current)
    code, _, error = cli_run([
        "workbook-query-plan", "--solution", str(root), "--run-id", state["runId"],
        "--workbook", "XDR Workbooks/LinuxMachines.json", "--clock", "2026-10-07T12:00:00Z",
    ])
    assert code == 2
    assert "Qualification run" in error


def test_ui_cli_import_and_failed_retry_preserve_current_failure(qualified_source):
    root, state = qualified_source
    plan = ui_plan(root)
    selectors_path = artifact_path(root, "ui-selectors.json", create_parent=True)
    steps_path = artifact_path(root, "ui-steps.json", create_parent=True)
    capture_path = artifact_path(root, "ui-capture.json", create_parent=True)
    selectors_path.write_text(json.dumps(plan["readinessSelectors"]))
    steps_path.write_text(json.dumps(plan["steps"]))
    capture_path.write_text(json.dumps(browser(plan)))
    common = ["--solution", str(root), "--run-id", state["runId"]]
    code, planned, error = cli_run([
        "workbook-ui-plan", *common, "--workbook", plan["workbook"], "--url", plan["url"],
        "--readiness-selectors", selectors_path.relative_to(root).as_posix(),
        "--steps", steps_path.relative_to(root).as_posix(),
        "--background-activity-review", plan["backgroundActivityReview"],
    ])
    assert code == 0, error
    binding = ["--plan", planned["planPath"], "--plan-sha256", planned["planSha256"]]
    reviewer = ["--actor", "fixture-reviewer", "--reference", "explicit-ui-approval"]
    code, _, error = cli_run(["workbook-ui-review", *common, *binding, *reviewer, "--decision", "approved"])
    assert code == 0, error
    command = ["workbook-ui-import", *common, *binding, *reviewer,
               "--evidence", capture_path.relative_to(root).as_posix()]
    code, imported, error = cli_run(command)
    assert code == 0, error
    assert "not executed by this command" in imported["browserExecution"]
    bad_capture = browser(plan)
    bad_capture["javascriptErrors"] = ["Synthetic failed retry"]
    capture_path.write_text(json.dumps(bad_capture))
    code, _, error = cli_run(command)
    assert code == 2
    assert "errors" in error
    receipt = json.loads(Path(imported["reportPath"]).read_bytes())
    assert receipt["status"] == "failed"
    assert list(report_directory(root).glob(f"workbook-ui.{plan['contentId']}.*.json"))


def test_provider_overruns_family_deadline_cannot_pass(qualified_source):
    root, _ = qualified_source
    plan = query_plan(root)
    with mock.patch.object(qualification.time, "monotonic", side_effect=(0, 0, 2)):
        with pytest.raises(ValueError, match="timeout"):
            qualification.execute_workbook_queries(
                root, plan, read_consent=lambda: consent(plan),
                providers=providers(plan), family_timeout_seconds=1,
            )
    receipt = json.loads((report_directory(root) / f"workbook-queries.{plan['contentId']}.json").read_bytes())
    assert receipt["status"] == "failed"
    assert receipt["error"] == "query-family-timeout"


def test_ui_final_consent_withdrawal_persists_failed_receipt(qualified_source):
    root, _ = qualified_source
    plan = ui_plan(root)
    approval = consent(plan)
    withdrawn = {**approval, "withdrawn": True}
    with pytest.raises(ValueError, match="withdrawn"):
        qualification.execute_workbook_ui(
            root, plan, read_consent=mock.Mock(side_effect=[approval, approval, withdrawn]),
            browser_runner=browser,
        )
    receipt = json.loads((report_directory(root) / f"workbook-ui.{plan['contentId']}.json").read_bytes())
    assert receipt["status"] == "failed"
