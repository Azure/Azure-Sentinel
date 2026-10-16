from __future__ import annotations

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
from unittest import mock
from uuid import uuid4
import zipfile

import pytest
import yaml

from sentinel_xdr_migration import cli, packaging, workflow, workbook_workflow as integration
from sentinel_xdr_migration import workbook_validation as validation
from sentinel_xdr_migration.artifacts import artifact_path, report_directory, using_run
from sentinel_xdr_migration._workbook_core import workbook
from test_converter import RULE
from test_workbook_arm_validation import TARGET, ACCESS

ROOT = Path(__file__).resolve().parents[3]
REAL_SUBPROCESS_RUN = subprocess.run


@pytest.fixture
def solution():
    scratch = Path.cwd() / (".workbook-integration-tests-" + uuid4().hex)
    root = scratch / "Solutions" / "Fixture"
    (root / "Workbooks/nested").mkdir(parents=True)
    (root / "Data").mkdir()
    (root / "Data/Solution_Fixture.json").write_text(json.dumps({
        "Name": "Fixture", "Version": "3.2.2", "Workbooks": ["Workbooks/nested/source.json"],
    }))
    (root / "Workbooks/nested/source.json").write_text(json.dumps({
        "version": "Notebook/1.0", "fromTemplateId": str(uuid4()),
        "metadata": {"name": "Fixture", "version": "1.0.0"},
        "items": [{"type": 3, "content": {
            "query": "DeviceEvents | summarize count() by ActionType",
            "queryType": 0, "resourceType": workbook.LA,
        }}],
    }))
    try:
        yield root
    finally:
        shutil.rmtree(scratch)


def initialize(root, **kwargs):
    return workflow.initialize_workflow(root, workflow_profile="authoring",
        workbook_capability_version=1, version_bump="none", **kwargs)


def config(root):
    source = root / "Workbooks/nested/source.json"
    if not source.is_file():
        return
    query = json.loads(source.read_bytes())["items"][0]["content"]["query"]
    path = artifact_path(root, "migration-config.yaml", create_parent=True)
    path.write_text(yaml.safe_dump({"workbookResolutions": {
        "Workbooks/nested/source.json": {"/items/0/content/query": {
            "querySha256": hashlib.sha256(query.encode()).hexdigest(), "tables": ["DeviceEvents"],
            "evidence": "Reviewed exact complete source query in offline fixture",
        }},
    }}))


def content_pass(root):
    config(root)
    workflow.start_workflow_stage(root, "discovery")
    inspection = integration.inspect_content(root)
    workflow.complete_workflow_stage(root, "discovery", status="passed")
    workflow.start_workflow_stage(root, "conversion")
    result = integration.convert_content(root)
    artifacts = {}
    manifest = report_directory(root) / "manifest.json"
    if manifest.is_file():
        artifacts = {"manifest": str(manifest), "manifestSha256": hashlib.sha256(manifest.read_bytes()).hexdigest()}
    workflow.complete_workflow_stage(root, "conversion", status="passed", artifacts=artifacts)
    integration.validate_content(root)
    workflow.start_workflow_stage(root, "validation")
    workflow.complete_workflow_stage(root, "validation", status="passed",
        artifacts={"validationMode": "offline-authoring", "runtimeStatus": "not-run"})
    return inspection, result


def cli_run(arguments):
    stdout, stderr = io.StringIO(), io.StringIO()
    with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
        code = cli.main(arguments)
    return code, json.loads(stdout.getvalue()) if stdout.getvalue() else None, stderr.getvalue()


def test_new_cli_defaults_and_resume_do_not_upgrade_library_runs(solution):
    legacy = workflow.initialize_workflow(solution, workflow_profile="authoring")
    assert "workbookCapabilityVersion" not in legacy["context"]
    code, resumed, error = cli_run(["workflow-init", "--solution", str(solution), "--workflow-profile", "authoring"])
    assert code == 0, error
    assert "workbooks" not in resumed
    code, _, error = cli_run(["workflow-init", "--solution", str(solution), "--workflow-profile", "authoring",
                             "--arm-validation-method", "lab-deployment"])
    assert code == 2
    assert "new run" in error
    code, current, error = cli_run(["workflow-init", "--solution", str(solution), "--workflow-profile", "authoring", "--new-run"])
    assert code == 0, error
    assert current["context"]["workbookCapabilityVersion"] == 1
    assert current["context"]["armValidationMethod"] == "lab-deployment"
    with using_run(solution, current["runId"]):
        assert initialize(solution)["resumed"] is True
        with pytest.raises(ValueError, match="new run"):
            initialize(solution, arm_validation_method="arm-ttk")


def test_explicit_authoring_arm_ttk_is_frozen(solution):
    state = initialize(solution, arm_validation_method="arm-ttk")
    assert state["context"]["armValidationMethod"] == "arm-ttk"
    assert initialize(solution)["context"]["armValidationMethod"] == "arm-ttk"
    with pytest.raises(ValueError, match="new run"):
        initialize(solution, arm_validation_method="lab-deployment")


@pytest.mark.parametrize("change", ["bytes", "add", "remove"])
def test_frozen_recursive_sources_reject_drift(solution, change):
    state = initialize(solution)
    assert state["workbooks"]["inventory"][0]["path"] == "Workbooks/nested/source.json"
    source = solution / "Workbooks/nested/source.json"
    if change == "bytes":
        source.write_bytes(source.read_bytes() + b"\n")
    elif change == "remove":
        source.unlink()
    else:
        document = json.loads(source.read_bytes())
        document["fromTemplateId"] = str(uuid4())
        (source.parent / "new.json").write_text(json.dumps(document))
    for action in (lambda: initialize(solution), lambda: integration.inspect_content(solution),
                   lambda: integration.convert_content(solution)):
        with pytest.raises(ValueError, match="inventory changed"):
            action()


def test_zero_source_inventory_is_frozen_without_fake_detection_manifest(solution):
    (solution / "Workbooks/nested/source.json").unlink()
    state = initialize(solution)
    assert state["workbooks"]["inventory"] == []
    inspection, result = content_pass(solution)
    assert inspection["workbookCount"] == inspection["analyticRuleCount"] == 0
    assert result["workbooks"]["total"] == result["total"] == 0
    assert not (report_directory(solution) / "manifest.json").exists()
    (solution / "Workbooks/nested/new.json").write_text('{"version":"Notebook/1.0","items":[]}')
    with pytest.raises(ValueError, match="inventory changed"):
        initialize(solution)


def test_workbook_only_offline_authoring_is_first_class(solution):
    state = initialize(solution)
    inspection, conversion = content_pass(solution)
    assert inspection["workbookCount"] == inspection["workbookQueryCount"] == 1
    assert inspection["analyticRuleCount"] == 0
    assert conversion["workbooks"]["converted"] == 1
    assert not (solution / "Analytic Rules").exists()
    assert not (report_directory(solution) / "manifest.json").exists()
    current = workflow.workflow_status(solution)
    assert current["stages"]["validation"]["status"] == "passed"
    assert current["workbookSummary"]["selectedCount"] == 1
    assert state["workbooks"]["selection"]["included"] == ["Workbooks/nested/source.json"]
    assert current["stages"]["conversion"]["artifacts"]["workbookManifestSha256"]
    assert current["runtimeAssessment"]["runtimeStatus"] == "not-run"


def test_reports_do_not_ignore_invalid_versioned_workbook_state(solution):
    from sentinel_xdr_migration.solution_report import build_solution_report

    initialize(solution)
    state_path, state = workflow._load(solution)
    del state["workbooks"]
    state_path.write_text(json.dumps(state))
    with pytest.raises(ValueError, match="workbooks.*required property"):
        build_solution_report(solution)


def test_explicit_empty_selection_remains_empty_and_exclusions_visible(solution):
    data = solution / "Data/Solution_Fixture.json"
    document = json.loads(data.read_bytes())
    document["XDR Workbooks"] = []
    data.write_text(json.dumps(document))
    state = initialize(solution)
    assert state["workbooks"]["selection"]["included"] == []
    assert state["workbooks"]["selection"]["excluded"][0]["reason"]
    inspection, result = content_pass(solution)
    assert json.loads(data.read_bytes())["XDR Workbooks"] == []
    assert result["workbookExcluded"] == state["workbooks"]["selection"]["excluded"]
    assert integration.validate_content(solution)["workbooks"]["total"] == 0
    assert inspection["workbookCount"] == 1


def test_blocked_default_sources_are_not_silently_removed(solution):
    initialize(solution)
    workflow.start_workflow_stage(solution, "discovery")
    workflow.complete_workflow_stage(solution, "discovery", status="passed")
    workflow.start_workflow_stage(solution, "conversion")
    converted = integration.convert_content(solution)
    assert converted["workbooks"]["selectedBlocked"] == 1
    assert json.loads((solution / "Data/Solution_Fixture.json").read_bytes())["XDR Workbooks"] == ["XDR Workbooks/nested/source.json"]
    workflow.complete_workflow_stage(solution, "conversion", status="passed")
    with pytest.raises(ValueError, match="review blockers"):
        integration.validate_content(solution)
    workflow.start_workflow_stage(solution, "validation")
    with pytest.raises(ValueError, match="review blockers"):
        workflow.complete_workflow_stage(solution, "validation", status="passed",
            artifacts={"runtimeStatus": "not-run", "validationMode": "offline-authoring"})
    assert workflow.workflow_status(solution)["stages"]["validation"]["status"] != "passed"


@pytest.mark.parametrize("change", ["output", "manifest", "queryEvidence", "selection"])
def test_exact_manifest_outputs_and_query_review_bindings(solution, change):
    initialize(solution)
    content_pass(solution)
    if change == "output":
        output = solution / "XDR Workbooks/nested/source.json"
        output.write_bytes(output.read_bytes() + b"\n")
    elif change in {"manifest", "queryEvidence"}:
        manifest = report_directory(solution) / "workbooks-manifest.json"
        document = json.loads(manifest.read_bytes())
        if change == "queryEvidence":
            document["results"][0]["queries"][0]["resolutionEvidence"] = {"evidence": "unbound changed evidence"}
        else:
            document["added"] = True
        manifest.write_text(json.dumps(document))
    else:
        data = solution / "Data/Solution_Fixture.json"
        document = json.loads(data.read_bytes())
        document["XDR Workbooks"] = []
        data.write_text(json.dumps(document))
    with pytest.raises(ValueError):
        integration.validate_content(solution)


def test_frozen_selection_rejects_state_edits_and_edited_existing_outputs(solution):
    state = initialize(solution)
    state["workbooks"]["selection"]["included"] = []
    with pytest.raises(ValueError, match="selection changed"):
        integration.verify_inventory(solution, state)
    content_pass(solution)
    output = solution / "XDR Workbooks/nested/source.json"
    output.write_bytes(output.read_bytes() + b"\n")
    before = output.read_bytes()
    result = integration.convert_content(solution, overwrite=True)
    assert result["workbooks"]["selectedBlocked"] == 1
    assert result["workbooks"]["results"][0]["status"] == "conflict"
    assert output.read_bytes() == before


def test_selected_release_not_notebook_format_and_no_silent_pre31_promotion(solution):
    data = solution / "Data/Solution_Fixture.json"
    document = json.loads(data.read_bytes())
    document["Version"] = "3.0.8"
    data.write_text(json.dumps(document))
    with pytest.raises(ValueError, match=">= 3.2.0"):
        initialize(solution)
    workflow.initialize_workflow(
        solution, workflow_profile="authoring", workbook_capability_version=1,
    )
    config(solution)
    result = integration.convert_content(solution)
    assert result["workbooks"]["selectedBlocked"] == 1
    assert json.loads(data.read_bytes())["Version"] == "3.0.8"
    next_state = initialize(solution, new_run=True, target_version="3.2.9")
    with using_run(solution, next_state["runId"]):
        config(solution)
        # A previously generated unbound draft cannot be overwritten by a new run.
        (solution / "XDR Workbooks/nested/source.json").unlink()
        result = integration.convert_content(solution)
        authored = json.loads((solution / "XDR Workbooks/nested/source.json").read_bytes())
        assert result["workbooks"]["selectedBlocked"] == 0
        assert authored["version"] == "Notebook/1.0"
        assert authored["xdrMetadata"]["version"] == "3.2.9"
        assert json.loads(data.read_bytes())["Version"] == "3.0.8"


def test_combined_solution_keeps_detection_gates_and_inventory_separate(solution):
    rules = solution / "Analytic Rules"
    rules.mkdir()
    (rules / "rule.yaml").write_text(RULE)
    initialize(solution)
    inspection, result = content_pass(solution)
    assert inspection["analyticRuleCount"] == inspection["workbookCount"] == 1
    assert result["total"] == result["workbooks"]["total"] == 1
    current = workflow.workflow_status(solution)
    artifacts = current["stages"]["conversion"]["artifacts"]
    assert artifacts["manifestSha256"] != artifacts["workbookManifestSha256"]
    (report_directory(solution) / "manifest.json").unlink()
    with pytest.raises(ValueError):
        workflow._validate_offline_authoring_gates(solution, Path(current["statePath"]), workflow._load(solution)[1])


def test_family_overwrite_replaces_managed_workbook_not_detection_conflicts(solution):
    rules = solution / "Analytic Rules"
    rules.mkdir()
    (rules / "rule.yaml").write_text(RULE)
    initialize(solution)
    config(solution)
    first = integration.convert_content(solution)
    assert first["workbooks"]["converted"] == 1
    detection = next((solution / "XDR Detections").glob("*.yaml"))
    detection.write_text(detection.read_text() + "\n# Independent authored change\n")
    before = detection.read_bytes()
    settings_path = artifact_path(solution, "migration-config.yaml")
    settings = yaml.safe_load(settings_path.read_bytes())
    settings["workbookResolutions"]["Workbooks/nested/source.json"]["/items/0/content/query"]["evidence"] += " updated"
    settings_path.write_text(yaml.safe_dump(settings))
    code, result, error = cli_run(["convert", "--solution", str(solution),
                                  "--config", str(settings_path), "--overwrite-workbooks"])
    assert code == 1, error  # Detection conflict is still a real gate.
    assert result["conflicts"] == 1
    assert result["workbooks"]["converted"] == 1
    assert detection.read_bytes() == before
    output = solution / "XDR Workbooks/nested/source.json"
    output.write_text(output.read_text() + "\n")
    workbook_before = output.read_bytes()
    settings["workbookResolutions"]["Workbooks/nested/source.json"]["/items/0/content/query"]["evidence"] += " again"
    settings_path.write_text(yaml.safe_dump(settings))
    result = integration.convert_content(solution, config_path=settings_path, overwrite_workbooks=True)
    assert result["workbooks"]["results"][0]["status"] == "conflict"
    assert output.read_bytes() == workbook_before
    assert detection.read_bytes() == before


def test_family_overwrite_rejects_unfrozen_legacy_run(solution):
    workflow.initialize_workflow(solution, workflow_profile="authoring")
    with pytest.raises(ValueError, match="workbook-capable"):
        integration.convert_content(solution, overwrite_workbooks=True)


def test_workspace_function_fingerprint_and_stale_parser_block_workflow(solution):
    from sentinel_xdr_migration.workbook_functions import candidates
    parser = solution / "Parsers/source.yaml"
    parser.parent.mkdir()
    parser.write_text("FunctionName: ReviewedSource\nFunctionQuery: DeviceEvents | count\n")
    data_path = solution / "Data/Solution_Fixture.json"
    data = json.loads(data_path.read_bytes())
    data["Parsers"] = ["Parsers/source.yaml"]
    data_path.write_text(json.dumps(data))
    source = solution / "Workbooks/nested/source.json"
    document = json.loads(source.read_bytes())
    document["items"][0]["content"]["query"] = "ReviewedSource() | count"
    source.write_text(json.dumps(document))
    state = initialize(solution)
    record = {key: candidates(solution)[0][key] for key in ("functionAlias", "sourcePath", "sourceSha256")}
    settings = {"workbookResolutions": {"Workbooks/nested/source.json": {
        "/items/0/content/query": {"querySha256": workbook.query_hash("ReviewedSource() | count"),
                                  "tables": ["DeviceEvents"], "workspaceFunctions": ["ReviewedSource"],
                                  "evidence": "Reviewed exact fixture"}}},
        "workbookDependencies": {"Workbooks/nested/source.json": {"requiredWorkspaceFunctions": [record]}}}
    settings_path = artifact_path(solution, "migration-config.yaml", create_parent=True)
    settings_path.write_text(yaml.safe_dump(settings))
    workflow.start_workflow_stage(solution, "discovery")
    integration.inspect_content(solution)
    workflow.complete_workflow_stage(solution, "discovery", status="passed")
    workflow.start_workflow_stage(solution, "conversion")
    result = integration.convert_content(solution, config_path=settings_path)
    assert result["workbooks"]["converted"] == 1
    assert len(result["workbookArtifacts"]["workbookFunctionDependenciesSha256"]) == 64
    workflow.complete_workflow_stage(solution, "conversion", status="passed")
    state = workflow._load(solution)[1]
    assert integration.validate_evidence(solution, state)["valid"] == 1
    parser.write_text(parser.read_text() + "# changed\n")
    with pytest.raises(ValueError, match="stale"):
        integration.bind_conversion(solution, state)


def test_workbook_only_yolo_uses_budget_without_invented_rule_guids(solution):
    state = initialize(solution, yolo=True, campaign_id="workbook-fixture")
    with using_run(solution, state["runId"]):
        config(solution)
        result = workflow.run_yolo_authoring(solution)
        assert result["status"] == "inProgress"
        current = workflow._load(solution)[1]
        assert "authoring" not in current
        assert current["context"]["workbookFullInventory"] is True
        assert current["stages"]["validation"]["status"] == "passed"
        assert result["workbookSummary"]["selectedCount"] == 1
        assert "coverage" not in result
        assert initialize(solution, yolo=True, campaign_id="workbook-fixture")["resumed"] is True


def test_schema_explicit_capability_cannot_upgrade_legacy_semantics(solution):
    state = workflow.initialize_workflow(solution, workflow_profile="authoring")
    for addition in ({"armValidationMethod": "lab-deployment"},
                     {"workbookCapabilityVersion": 1}):
        invalid = deepcopy(state)
        invalid.pop("statePath", None)
        invalid.pop("resumed", None)
        invalid.pop("next", None)
        invalid["context"].update(addition)
        with pytest.raises(ValueError, match="invalid workflow state"):
            workflow._validate(invalid)


@pytest.fixture
def emitted():
    from test_defender_workbooks_packaging import DefenderWorkbookPackagingTests
    harness = DefenderWorkbookPackagingTests()
    harness.setUp()
    try:
        harness.notebook["xdrMetadata"]["version"] = harness.data["Version"]
        harness.write()
        (harness.solution / "Data").mkdir()
        (harness.solution / "Data/Solution_Sample.json").write_text(json.dumps({"Name": "Sample", **harness.data}))
        result = harness.invoke(package=True)
        yield harness, result
    finally:
        harness.tearDown()


def test_python_verifies_full_install_registration_stored_template_and_zip(emitted):
    harness, result = emitted
    package = harness.solution / "Package"
    template = json.loads((package / "mainTemplate.json").read_bytes())
    receipt = packaging._verify_workbook_package(harness.solution, [harness.target],
                                               template, package / "3.2.7.zip")
    assert receipt["count"] == 1
    assert receipt["contractSupport"] == "unverified"
    assert template["parameters"]["DeployWorkbook"]["defaultValue"] is True
    assert template["parameters"]["DeployDefenderWorkbook"]["defaultValue"] is False


@pytest.mark.parametrize("change", [None, "clip-newline-eof", "missing-dependency", "conditional-parser", "parameter-drift", "stale-source"])
def test_python_rechecks_required_workspace_function_package_contract(emitted, change):
    harness, _ = emitted
    harness.add_function()
    if change == "clip-newline-eof":
        path = harness.solution / "Parsers/ReviewedParser.yaml"
        path.write_text(path.read_text().rstrip("\n"))
        record = harness.notebook["contentProvenance"]["requiredWorkspaceFunctions"][0]
        record["sourceSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        harness.write()
    (harness.solution / "Data/Solution_Sample.json").write_text(json.dumps({"Name": "Sample", **harness.data}))
    harness.invoke(package=True)
    package = harness.solution / "Package"
    template = json.loads((package / "mainTemplate.json").read_bytes())
    installation = next(row for row in template["resources"] if row["type"] == "Microsoft.Resources/deployments")
    parser = next(row for row in template["resources"] if row["type"].endswith("/savedSearches"))
    if change == "missing-dependency":
        installation["dependsOn"] = installation["dependsOn"][:1]
    elif change == "conditional-parser":
        parser["condition"] = True
    elif change == "parameter-drift":
        parser["properties"]["functionParameters"] = "limit:int=2"
    elif change == "stale-source":
        path = harness.solution / "Parsers/ReviewedParser.yaml"
        path.write_text(path.read_text() + "# changed\n")
    if change not in (None, "clip-newline-eof"):
        with pytest.raises((ValueError, RuntimeError)):
            packaging._verify_workbook_package(harness.solution, [harness.target], template, package / "3.2.7.zip")
    else:
        assert packaging._verify_workbook_package(
            harness.solution, [harness.target], template, package / "3.2.7.zip")["count"] == 1


@pytest.mark.parametrize("change", ["provenance", "registration", "storedTemplate", "install", "dependency", "zip"])
def test_python_rejects_wrong_workbook_package_projection(emitted, change):
    harness, result = emitted
    package = harness.solution / "Package"
    template = json.loads((package / "mainTemplate.json").read_bytes())
    registration = next(row for row in template["resources"] if row.get("properties", {}).get("contentKind") == "DefenderWorkbook")
    install = next(row for row in template["resources"] if row.get("name", "").startswith("DefenderWorkbook-"))
    if change == "provenance":
        registration["properties"]["contentProvenance"]["packageVersion"] = "3.2.8"
    elif change == "registration":
        registration["condition"] = "[parameters('DeployWorkbook')]"
    elif change == "storedTemplate":
        registration["properties"]["mainTemplate"]["languageVersion"] = "1.0"
    elif change == "install":
        install["properties"]["template"]["resources"]["workbook"]["properties"]["id"] = harness.notebook["xdrMetadata"]["contentId"]
    elif change == "dependency":
        template["resources"][0]["properties"]["dependencies"]["criteria"] = []
    else:
        with zipfile.ZipFile(package / "3.2.7.zip", "w") as archive:
            archive.writestr("mainTemplate.json", "{}")
    with pytest.raises(RuntimeError):
        packaging._verify_workbook_package(harness.solution, [harness.target], template, package / "3.2.7.zip")


def test_python_lab_method_forwarding_is_candidate_not_accepted(emitted):
    harness, result = emitted
    # The PowerShell emitter's synthetic source is not a converter fixture;
    # its standalone tests already verify source/query freshness.
    with mock.patch.object(packaging, "_validate_v31_toolkit_root", return_value=ROOT), \
         mock.patch("sentinel_xdr_migration.workbooks.validate_workbooks", return_value={"valid": 1, "invalid": 0}), \
         mock.patch.object(packaging.subprocess, "run", return_value=subprocess.CompletedProcess(
             [], 0, "Starting Package Creation using V3.1 tool", "")) as run:
        receipt = packaging.package_solution_v3_1(harness.solution, version_bump="none",
            toolkit_root=ROOT, arm_validation_method="lab-deployment")
    command = run.call_args.args[0]
    assert command[command.index("-ArmValidationMethod") + 1] == "lab-deployment"
    assert receipt["packageAccepted"] is False
    assert receipt["packageLifecycleStatus"] == "candidate-generated"
    assert receipt["xdrWorkbookCount"] == 1
    assert receipt["deploymentParameters"]["DeployDefenderWorkbook"] is False


def test_missing_receipts_and_unaccepted_candidates_cannot_pass_packaging(solution):
    initialize(solution)
    content_pass(solution)
    workflow.start_workflow_stage(solution, "packaging")
    with pytest.raises(ValueError, match="packageReport"):
        workflow.complete_workflow_stage(solution, "packaging", status="passed", artifacts={"packager": "V3.1"})
    with pytest.raises(ValueError):
        integration.require_accepted(solution, workflow._load(solution)[1])


def test_local_lifecycle_commands_require_explicit_run_and_no_implicit_write_consent(solution):
    with pytest.raises(SystemExit) as exc:
        cli.main(["workflow-arm-plan", "--solution", str(solution), "--target", "lab.json", "--selected-flags", "flags.json"])
    assert exc.value.code == 2


def emit_current_package(root):
    from test_defender_workbooks_packaging import literal
    data_path = root / "Data/Solution_Fixture.json"
    data = json.loads(data_path.read_bytes())
    payload = report_directory(root) / "package-fixture-input.json"
    payload.write_text(json.dumps({
        "data": data,
        "template": {
            "parameters": {"workspace": {"type": "string"}},
            "variables": {"solutionId": "fixture.publisher", "_solutionId": "[variables('solutionId')]",
                          "_solutionVersion": data["Version"]},
            "resources": [{
                "type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
                "apiVersion": "2023-04-01-preview",
                "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_solutionId'))]",
                "properties": {"contentKind": "Solution", "dependencies": {"criteria": []}},
            }],
        },
        "ui": {"parameters": {"outputs": {}, "steps": []}},
    }))
    common = ROOT / "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1"
    command = (
        "$ErrorActionPreference='Stop'; "
        f". {literal(common)}; "
        f"$i=Get-Content -Raw -LiteralPath {literal(payload)} | ConvertFrom-Json; "
        f"$count=Add-XdrDefenderWorkbooksToSolution -SolutionName Fixture -ContentToImport $i.data "
        f"-Template $i.template -RepositoryRoot {literal(root.parent.parent)}; "
        "Add-SolutionContentDeploymentParameters -Template $i.template -UiDefinition $i.ui; "
        "Write-Output '__RESULT__'; $i | ConvertTo-Json -Depth 100 -Compress"
    )
    completed = REAL_SUBPROCESS_RUN(["pwsh", "-NoProfile", "-NonInteractive", "-Command", command],
                                   capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    document = json.loads(completed.stdout.split("__RESULT__", 1)[1])
    package = root / "Package"
    package.mkdir(exist_ok=True)
    (package / "mainTemplate.json").write_text(json.dumps(document["template"]))
    (package / "createUiDefinition.json").write_text(json.dumps(document["ui"]))
    (package / "testParameters.json").write_text(json.dumps(document["template"]["parameters"]))
    with zipfile.ZipFile(package / f"{data['Version']}.zip", "w") as archive:
        for name in ("mainTemplate.json", "createUiDefinition.json"):
            archive.write(package / name, name)


def package_candidate(root, bump="none"):
    def mocked_packager(command, **kwargs):
        selected_bump = command[command.index("-VersionBump") + 1]
        data_path = root / "Data/Solution_Fixture.json"
        data = json.loads(data_path.read_bytes())
        if selected_bump == "patch":
            version = list(map(int, data["Version"].split(".")))
            version[2] += 1
            data["Version"] = ".".join(map(str, version))
            data_path.write_text(json.dumps(data))
        emit_current_package(root)
        return subprocess.CompletedProcess(command, 0, "Starting Package Creation using V3.1 tool", "")
    with mock.patch.object(packaging.subprocess, "run", side_effect=mocked_packager):
        return workflow.package_workflow_v3_1(root, requested_version_bump=bump, toolkit_root=ROOT)


@pytest.fixture
def ready_candidate(solution):
    initialize(solution)
    content_pass(solution)
    package = package_candidate(solution)
    receipt = report_directory(solution) / "build-and-validate-report.md"
    receipt.write_text("Explicit mocked official receipt; parser producer tests run separately")
    binding = {"path": str(receipt), "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest()}
    with mock.patch.object(validation, "_parse_build_validation_receipt", return_value=binding):
        candidate = integration.create_candidate(solution, validation_receipt=receipt)
        yield solution, package, candidate


def test_candidate_preserves_draft_and_exact_four_real_gate_receipts(ready_candidate):
    root, package, candidate = ready_candidate
    assert package["status"] == "blocked"
    assert candidate["accepted"] is False
    assert candidate["status"] == "candidate-generated"
    assert set(candidate["prerequisiteEvidence"]) == {"conversion", "review", "structure", "package"}
    for name, reference in candidate["prerequisiteEvidence"].items():
        receipt_path = root / reference["path"]
        receipt = json.loads(receipt_path.read_bytes())
        assert receipt["status"] == "passed"
        assert receipt["checks"]
        assert receipt["packageInputSha256"] == packaging.package_input_identity(root)["sha256"]
        assert hashlib.sha256(receipt_path.read_bytes()).hexdigest() == reference["sha256"]
        if name in {"structure", "package"}:
            assert receipt["packageArtifactsSha256"] == package["packageArtifactsSha256"]
    state = workflow._load(root)[1]
    assert state["stages"]["packaging"]["status"] == "blocked"
    assert state["packaging"]["lastSuccessful"] is None
    assert (root / package["mainTemplate"]).is_file()


def test_actual_official_receipt_required_before_candidate_creation(solution):
    initialize(solution)
    content_pass(solution)
    package_candidate(solution)
    receipt = report_directory(solution) / "build-and-validate-report.md"
    receipt.write_text("[REPORT_START]\nResult: CANDIDATE_GENERATED\n[REPORT_END]\n")
    with pytest.raises(ValueError, match="repository build-and-validate"):
        integration.create_candidate(solution, validation_receipt=receipt)
    assert not (report_directory(solution) / "arm-candidate.json").exists()
    assert workflow._load(solution)[1]["packaging"]["lastSuccessful"] is None


def test_official_producer_method_is_forwarded_without_fabricated_receipt(solution):
    initialize(solution)
    content_pass(solution)
    package_candidate(solution)
    with mock.patch.object(subprocess, "run",
                           return_value=subprocess.CompletedProcess([], 1, "actual validator failure", "")) as producer:
        with pytest.raises(RuntimeError, match="actual validator failure"):
            integration.create_candidate(solution, toolkit_root=ROOT)
    command = producer.call_args.args[0]
    assert command[command.index("-ArmValidationMethod") + 1] == "lab-deployment"
    assert "-SkipPackaging" in command
    assert command[command.index("-ValidationSkip") + 1] == "kql,detection-schema,non-ascii"
    assert not (report_directory(solution) / "arm-candidate.json").exists()


def test_scope_review_withdrawal_and_immediate_exact_approval_are_independent(ready_candidate):
    root, package, candidate = ready_candidate
    plan = integration.plan_candidate(root, target=TARGET, selected_flags={"DeployDefenderWorkbook": True})
    with pytest.raises(ValueError, match="displayed plan hash"):
        integration.review_scope(root, actor="owner", reference="scope-review", approved=True, expected_plan_sha256="0" * 64)
    consent = integration.review_scope(root, actor="owner", reference="scope-review", approved=True,
                                       expected_plan_sha256=plan["planSha256"])
    assert consent["activationAuthorized"] is False
    with mock.patch("sentinel_xdr_migration.workbook_preflight_workflow.production_identity_check") as identity, \
         mock.patch("sentinel_xdr_migration.arm_acceptance_support._run_cli") as runner:
        with pytest.raises(ValueError, match="immediate exact-plan"):
            integration.execute_candidate(root, expected_plan_sha256=plan["planSha256"], actor="owner",
                                          reference="execute-review", confirmation="not the approval")
        identity.assert_not_called()
        runner.assert_not_called()
    withdrawn = integration.withdraw_scope(root, actor="owner", reference="withdraw")
    assert withdrawn["status"] == "withdrawn"
    with mock.patch("sentinel_xdr_migration.workbook_preflight_workflow.production_identity_check") as identity:
        result = integration.execute_candidate(root, expected_plan_sha256=plan["planSha256"], actor="owner",
            reference="execute-review", confirmation=validation.LAB_ARM_CONFIRMATION)
        identity.assert_not_called()
    assert result["status"] == "blocked"
    assert result["writeAttempted"] is False


def test_write_consent_does_not_implicitly_authorize_preflight_reads(ready_candidate):
    from sentinel_xdr_migration import workbook_preflight_workflow as preflight

    root, _, _ = ready_candidate
    plan = integration.plan_candidate(root, target=TARGET, selected_flags={"DeployDefenderWorkbook": True})
    integration.review_scope(
        root, actor="owner", reference="write-scope", approved=True,
        expected_plan_sha256=plan["planSha256"],
    )
    preflight.create_plan(root)
    with mock.patch("sentinel_xdr_migration.arm_acceptance_support._run_cli") as runner, \
         mock.patch("sentinel_xdr_migration.graph_client_config.azure_cli_credential") as credential:
        result = integration.execute_candidate(
            root, expected_plan_sha256=plan["planSha256"], actor="owner",
            reference="immediate-write", confirmation=validation.LAB_ARM_CONFIRMATION,
        )
        assert result["status"] == "blocked"
        assert result["writeAttempted"] is False
        assert result["identityCheck"]["status"] == "blocked"
        runner.assert_not_called()
        credential.assert_not_called()


def test_preflight_review_execute_revoke_and_archived_receipts(ready_candidate):
    from sentinel_xdr_migration import workbook_preflight_workflow as preflight

    root, _, _ = ready_candidate
    integration.plan_candidate(root, target=TARGET, selected_flags={"DeployDefenderWorkbook": True})
    displayed = preflight.create_plan(root)
    digest = displayed["preflightPlanSha256"]
    with pytest.raises(ValueError, match="exact current displayed"):
        preflight.review(root, expected_sha256="0" * 64, actor="owner", reference="stale", approved=True)
    consent = preflight.review(
        root, expected_sha256=digest, actor="owner", reference="read-review", approved=True,
    )
    assert consent["writesAuthorized"] is False
    reader = mock.Mock(return_value={"statusCode": 403, "body": {}})
    result = preflight.execute(root, expected_sha256=digest, reader=reader)
    assert result["status"] == "blocked"
    assert result["writeAttempted"] is False
    assert reader.call_count == 1
    first = (report_directory(root) / preflight.RESULT_FILE).read_bytes()
    withdrawn = preflight.revoke(root, actor="owner", reference="withdraw-reads")
    assert withdrawn["status"] == "revoked"
    reader.reset_mock()
    result = preflight.execute(root, expected_sha256=digest, reader=reader)
    assert result["status"] == "blocked"
    reader.assert_not_called()
    archives = list(report_directory(root).glob("arm-preflight-result.*.json"))
    assert len(archives) == 1
    assert archives[0].read_bytes() == first


def test_preflight_known_failure_replaces_current_receipt_without_private_details(ready_candidate):
    from sentinel_xdr_migration import workbook_preflight_workflow as preflight

    root, _, _ = ready_candidate
    integration.plan_candidate(root, target=TARGET, selected_flags={"DeployDefenderWorkbook": True})
    displayed = preflight.create_plan(root)
    with mock.patch.object(preflight, "default_reader", side_effect=ValueError("fixture-private-detail")):
        with pytest.raises(ValueError, match="fixture-private-detail"):
            preflight.execute(root, expected_sha256=displayed["preflightPlanSha256"])
    receipt = json.loads((report_directory(root) / preflight.RESULT_FILE).read_bytes())
    assert receipt["status"] == "failed"
    assert receipt["writeAttempted"] is False
    assert "fixture-private-detail" not in json.dumps(receipt)


def test_preflight_cli_reports_blocked_as_nonzero(ready_candidate, capsys):
    root, _, _ = ready_candidate
    run_id = workflow._load(root)[1]["runId"]
    with mock.patch(
        "sentinel_xdr_migration.workbook_preflight_workflow.execute",
        return_value={"status": "blocked", "writeAttempted": False},
    ):
        code = cli.main([
            "workflow-arm-preflight-execute", "--solution", str(root),
            "--run-id", run_id, "--preflight-plan-sha256", "a" * 64,
        ])
    assert code != 0
    assert json.loads(capsys.readouterr().out)["status"] == "blocked"


def test_selected_flags_only_dispatch_and_arm_success_stays_unaccepted(ready_candidate):
    root, package, candidate = ready_candidate
    plan = integration.plan_candidate(root, target=TARGET, selected_flags={"DeployDefenderWorkbook": True})
    integration.review_scope(root, actor="owner", reference="scope-review", approved=True, expected_plan_sha256=plan["planSha256"])
    runner = mock.Mock(return_value=(0, {"id": "fixture-deployment", "properties": {"provisioningState": "Succeeded"}}, ""))
    result = integration.execute_candidate(root, expected_plan_sha256=plan["planSha256"], actor="owner",
        reference="exact-execute", confirmation=validation.LAB_ARM_CONFIRMATION,
        identity_check=lambda target: ACCESS, command_runner=runner)
    assert result["status"] == "arm-accepted-contract-pending"
    assert result["accepted"] is False
    assert "DeployDefenderWorkbook=true" in runner.call_args.args[0]
    assert not any(flag.startswith("DeployWorkbook=") for flag in runner.call_args.args[0])
    assert workflow._load(root)[1]["packaging"]["lastSuccessful"] is None
    with pytest.raises(ValueError, match="independent workbook contract evidence"):
        integration.require_accepted(root, workflow._load(root)[1])


def test_consumed_candidate_version_action_retries_without_second_bump(solution):
    workflow.initialize_workflow(solution, workflow_profile="authoring", workbook_capability_version=1, version_bump="patch")
    content_pass(solution)
    first = package_candidate(solution, "patch")
    assert first["version"] == "3.2.3"
    assert first["packageAccepted"] is False
    with pytest.raises(ValueError, match="consumed"):
        package_candidate(solution, "patch")
    second = package_candidate(solution, "none")
    assert second["version"] == first["version"]
    assert second["effectiveVersionBump"] == "none"
    current = workflow._load(solution)[1]
    assert current["stages"]["packaging"]["attempts"] == 2
    assert current["packaging"]["lastSuccessful"] is None


def test_workbook_report_keeps_excluded_inventory_outside_rule_coverage(solution):
    from sentinel_xdr_migration.solution_report import build_solution_report
    initialize(solution)
    content_pass(solution)
    report = build_solution_report(solution)
    assert report["summary"]["rules"] == 0
    assert report["rules"] == []
    assert report["workbooks"]["inventoryCount"] == 1
    assert report["workbooks"]["sources"][0]["selected"] is True


def test_lab_deployment_preflight_prompt_and_expected_content_counts(solution):
    rules = solution / "Analytic Rules"
    rules.mkdir()
    (rules / "rule1.yaml").write_text(RULE)
    state = initialize(solution)
    content_pass(solution)
    data_path = solution / "Data/Solution_Fixture.json"
    data = json.loads(data_path.read_bytes())
    data["Analytic Rules"] = ["Analytic Rules/rule1.yaml"]
    data["XDR Detections"] = [
        p.relative_to(solution).as_posix()
        for p in sorted((solution / "XDR Detections").glob("*.yaml"))
    ]
    data_path.write_text(json.dumps(data))

    counts = integration.expected_content_counts(solution, state)
    assert counts["sentinelRulesCount"] == 1
    assert counts["sentinelWorkbooksCount"] == 1
    assert counts["defenderWorkbooksCount"] == 1
    assert counts["workbooksCount"] == 2
    assert counts["workbooksBreakdown"] == {"sentinel": 1, "defender": 1}
    assert counts["customDetectionsCount"] == 1

    preflight_info = integration.plan_lab_deployment_preflight(solution)
    assert preflight_info["armValidationMethod"] == "lab-deployment"
    assert preflight_info["defaultArmValidationMethod"] == "lab-deployment"
    assert preflight_info["skipsArmTtk"] is True
    assert preflight_info["functionalQualificationVerified"] is False
    assert preflight_info["alertParityVerified"] is False
    assert preflight_info["labDeploymentPreflightPrompt"] == (
        "Requesting preflight preapproval to deploy the solution ARM templates to the "
        "selected non-production lab to verify ARM template deployment validity "
        "(expected content items: 1 Sentinel rules, 2 workbooks, and 1 custom detections). "
        "Deployment verification alone does not establish functional/runtime qualification or alert parity."
    )
    persisted = json.loads((report_directory(solution) / "arm-deployment-preflight.json").read_bytes())
    assert persisted["labDeploymentPreflightPrompt"] == preflight_info["labDeploymentPreflightPrompt"]
    assert persisted["expectedContentCounts"] == counts
    status = workflow.workflow_status(solution)
    assert status["workbookSummary"]["expectedContentCounts"] == counts
    assert status["workbookSummary"]["labDeploymentPreflightPrompt"] == preflight_info["labDeploymentPreflightPrompt"]


def test_default_lab_deployment_vs_explicit_arm_ttk_and_durable_deployment_findings(ready_candidate):
    root, package, candidate = ready_candidate
    assert integration.default_arm_validation_method("authoring") == "lab-deployment"
    assert integration.default_arm_validation_method("qualification") == "lab-deployment"
    assert candidate["expectedContentCounts"]["workbooksCount"] == 2
    assert "expected content items: 0 Sentinel rules, 2 workbooks, and 0 custom detections" in candidate["labDeploymentPreflightPrompt"]

    plan = integration.plan_candidate(root, target=TARGET, selected_flags={"DeployDefenderWorkbook": True})
    assert (report_directory(root) / "arm-deployment-preflight.json").is_file()
    integration.review_scope(
        root, actor="owner", reference="scope-review", approved=True,
        expected_plan_sha256=plan["planSha256"],
    )
    failing_runner = mock.Mock(
        return_value=(
            1,
            {"id": "fixture-failed-deployment", "properties": {"provisioningState": "Failed"}},
            "DeploymentFailed: InvalidTemplateDeployment",
        )
    )
    failed_result = integration.execute_candidate(
        root,
        expected_plan_sha256=plan["planSha256"],
        actor="owner",
        reference="execute-failure-test",
        confirmation=validation.LAB_ARM_CONFIRMATION,
        identity_check=lambda target: ACCESS,
        command_runner=failing_runner,
    )
    assert failed_result["status"] == "failed"
    assert failed_result["functionalQualificationVerified"] is False
    assert failed_result["alertParityVerified"] is False
    assert failed_result["artifactBindings"]["candidateSha256"] == candidate["candidateSha256"]
    assert failed_result["artifactBindings"]["planSha256"] == plan["planSha256"]
    assert failed_result["artifactBindings"]["mainTemplateSha256"] == plan["mainTemplateSha256"]
    assert any("DeploymentFailed" in item["message"] for item in failed_result["findings"])

    evidence_path = report_directory(root) / "arm-deployment-validation-evidence.json"
    assert evidence_path.is_file()
    durable = json.loads(evidence_path.read_bytes())
    assert durable["outcome"] == "failed"
    assert durable["functionalQualificationVerified"] is False
    assert durable["alertParityVerified"] is False
    assert durable["target"] == plan["target"]
    assert durable["artifactBindings"]["packageArtifactsSha256"] == package["packageArtifactsSha256"]
    state = workflow._load(root)[1]
    assert state["stages"]["packaging"]["artifacts"]["labArmDeploymentOutcome"] == "failed"
    assert state["stages"]["packaging"]["artifacts"]["functionalQualificationVerified"] == "false"
    assert state["stages"]["packaging"]["artifacts"]["alertParityVerified"] == "false"


def test_assess_qualification_readiness_separates_deployment_and_ingestion(solution):
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
    # Initial state without consent or preflight receipts
    initial_readiness = integration.assess_qualification_readiness(solution, run_id=state["runId"])
    assert initial_readiness["status"] == "blocked"
    assert initial_readiness["deploymentAndIngestionSeparated"] is True
    assert initial_readiness["authorizationChecks"]["targetLocked"]["status"] == "ready"
    assert initial_readiness["authorizationChecks"]["runtimeQueryConsent"]["status"] == "missing"
    assert initial_readiness["authorizationChecks"]["armPreflightReadConsent"]["status"] == "missing"
    assert initial_readiness["authorizationChecks"]["deploymentConsent"]["status"] == "missing"
    assert initial_readiness["deploymentPermissionReadiness"]["status"] == "not-evaluated"
    assert initial_readiness["ingestionPermissionReadiness"]["status"] == "not-evaluated"

    # Populate consents and ready ARM preflight, but leave DCR/ingestion blocked
    (run_dir / "runtime-query-consent.json").write_text(json.dumps({
        "status": "approved",
        "withdrawn": False,
        "approvedFamilies": ["sentinelSourceQueryFamily", "defenderXdrQueryFamily"],
    }))
    (run_dir / "arm-preflight-consent.json").write_text(json.dumps({
        "status": "approved",
        "revoked": False,
    }))
    (run_dir / "arm-validation-consent.json").write_text(json.dumps({
        "status": "approved",
        "withdrawn": False,
        "deploymentOnly": True,
    }))
    (run_dir / "arm-preflight-result.json").write_text(json.dumps({
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
            "extensionResourceWriteAllowed": {"status": "not-required", "required": False},
        },
        "reasons": [],
    }))
    (run_dir / "qualification-dcr-preflight.json").write_text(json.dumps({
        "status": "blocked",
        "summary": {"total": 1, "ready": 0, "blocked": 1},
        "candidates": [{
            "table": "Syslog",
            "tableSchemaCompatibility": {"status": "compatible"},
            "resourceProvisioningAuthorization": {"status": "ready"},
            "ingestionAuthorization": {"status": "denied", "requiredAction": "Microsoft.Insights/Telemetry/Write"},
        }],
        "blockers": ["Logs Ingestion permission Microsoft.Insights/Telemetry/Write is denied"],
    }))

    split_readiness = integration.assess_qualification_readiness(solution, run_id=state["runId"])
    assert split_readiness["authorizationChecks"]["status"] == "ready"
    assert split_readiness["deploymentPermissionReadiness"]["status"] == "ready"
    assert split_readiness["deploymentPermissionReadiness"]["ready"] is True
    assert split_readiness["deploymentPermissionReadiness"]["impliesIngestionReadiness"] is False
    assert split_readiness["ingestionPermissionReadiness"]["status"] == "blocked"
    assert split_readiness["ingestionPermissionReadiness"]["ready"] is False
    assert split_readiness["ingestionPermissionReadiness"]["dcrAndDceReadiness"]["status"] == "ready"
    assert split_readiness["ingestionPermissionReadiness"]["logsIngestionReadiness"]["status"] == "blocked"
    assert split_readiness["status"] == "blocked"

    # Now mark Logs Ingestion ready and verify overall readiness
    (run_dir / "qualification-dcr-preflight.json").write_text(json.dumps({
        "status": "ready",
        "summary": {"total": 1, "ready": 1, "blocked": 0},
        "candidates": [{
            "table": "Syslog",
            "tableSchemaCompatibility": {"status": "compatible"},
            "resourceProvisioningAuthorization": {"status": "ready"},
            "ingestionAuthorization": {"status": "ready", "requiredAction": "Microsoft.Insights/Telemetry/Write"},
        }],
        "blockers": [],
    }))
    full_readiness = integration.assess_qualification_readiness(solution, run_id=state["runId"])
    assert full_readiness["status"] == "ready"
    assert full_readiness["deploymentPermissionReadiness"]["ready"] is True
    assert full_readiness["ingestionPermissionReadiness"]["ready"] is True


def test_audit_private_config_and_support_export(solution):
    from sentinel_xdr_migration.evidence import export_evidence

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

    clean_audit = integration.audit_private_config_and_support_export(solution, run_id=state["runId"])
    assert clean_audit["status"] == "isolated"
    assert clean_audit["privateConfigIsolatedToLocalUnexportedConfig"] is True
    assert clean_audit["supportExportsRedacted"] is True
    assert clean_audit["exposureClaimVerified"] is False
    assert clean_audit["localConfig"]["envFilePresent"] is True
    assert ".env" in clean_audit["localConfig"]["localUnexportedArtifacts"]
    assert clean_audit["supportExports"]["checkedFiles"]
    assert clean_audit["supportExports"]["exposures"] == []

    # Simulate an unredacted private identifier leak in support export
    summary_md = solution / "Evidence" / state["runId"] / "summary.md"
    summary_md.write_text(summary_md.read_text(encoding="utf-8") + f"\nLeaked tenant: {TARGET['tenantId']}\n", encoding="utf-8")
    leaked_audit = integration.audit_private_config_and_support_export(solution, run_id=state["runId"])
    assert leaked_audit["status"] == "exposed-in-support-export"
    assert leaked_audit["privateConfigIsolatedToLocalUnexportedConfig"] is False
    assert leaked_audit["supportExportsRedacted"] is False
    assert leaked_audit["exposureClaimVerified"] is True
    assert any(item["identifierKind"] == "tenantId" for item in leaked_audit["supportExports"]["exposures"])

