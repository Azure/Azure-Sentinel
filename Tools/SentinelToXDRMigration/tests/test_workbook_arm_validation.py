from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path
from unittest import mock

import pytest

from sentinel_xdr_migration import workbook_validation as validation
from sentinel_xdr_migration.arm_acceptance_support import _canonical_sha256
from sentinel_xdr_migration.packaging import package_input_file_hashes, package_input_identity

ROOT = Path(__file__).resolve().parents[3]
TARGET = {
    "tenantId": "11111111-2222-3333-4444-555555555555",
    "subscriptionId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "resourceGroup": "fixture-rg",
    "workspaceResourceId": "/subscriptions/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/resourceGroups/fixture-rg/providers/Microsoft.OperationalInsights/workspaces/fixture-ws",
    "workspaceCustomerId": "99999999-8888-7777-6666-555555555555",
}
CONTEXT = {"runId": "fixture-run", "workflowProfile": "authoring", "profileSelectionConfirmed": True,
           "workbookCapabilityVersion": 1, "armValidationMethod": "lab-deployment"}
FLAGS = {"DeployWorkbook": False, "DeployDefenderWorkbook": True}
ACCESS = {key: True for key in ("tenantMatches", "subscriptionMatches", "workspaceMatches", "nonProduction",
                              "armDeploymentAllowed", "extensionResourceWriteAllowed", "disabledContentVerified", "ownershipVerified")}
ACCESS.update(identityId="fixture-principal", **{key: TARGET[key] for key in ("tenantId", "subscriptionId", "workspaceResourceId")})


def workbook_template():
    provenance = {"packageId": "publisher.fixture", "packageVersion": "3.2.1",
                  "contentId": "aaaaaaaa-1111-2222-3333-444444444444", "contentVersion": "3.2.1"}
    notebook = {"version": "Notebook/1.0", "items": [], "contentProvenance": provenance}
    inner = {
        "languageVersion": "2.0", "imports": {"MicrosoftSecurity": {"provider": "MicrosoftSecurity", "version": "1.0.0"}},
        "resources": {"workbook": {"import": "MicrosoftSecurity", "type": "Microsoft.Security/workbooks@2026-06-01-preview",
                                   "properties": {"id": "bbbbbbbb-1111-2222-3333-444444444444", "name": "Fixture", "content": notebook}}},
    }
    return {
        "parameters": {"workspace": {"type": "string"}, **{key: {"type": "bool", "defaultValue": False} for key in FLAGS}},
        "resources": [
            {"type": "Microsoft.Resources/deployments", "name": "fixture-install", "condition": "[parameters('DeployDefenderWorkbook')]",
             "properties": {"mode": "Incremental", "expressionEvaluationOptions": {"scope": "inner"}, "template": inner}},
            {"type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
             "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(parameters('workspace'),'-dwb-',uniqueString('fixture')))]",
             "condition": "[parameters('DeployDefenderWorkbook')]",
             "properties": {"contentKind": "DefenderWorkbook", "contentId": provenance["contentId"], "version": "3.2.1",
                            "packageId": provenance["packageId"], "packageVersion": "3.2.1", "mainTemplate": copy.deepcopy(inner),
                            "contentProvenance": {**provenance, "requiredWorkloads": [], "requiredDataConnectors": []}}},
        ],
    }


@pytest.fixture
def case():
    directory = ROOT / ".script/local-validation/Logs" / ("workbook-tests-" + uuid.uuid4().hex)
    solution = directory / "Solutions/Fixture"
    package = solution / "Package"
    logs = solution / "Logs"
    package.mkdir(parents=True)
    logs.mkdir()
    (solution / "input.json").write_text("{}")
    template = workbook_template()
    (package / "mainTemplate.json").write_text(json.dumps(template))
    (package / "createUiDefinition.json").write_text("{}")
    (package / "testParameters.json").write_text("{}")
    with zipfile.ZipFile(package / "3.2.1.zip", "w") as archive:
        archive.write(package / "mainTemplate.json", "mainTemplate.json")
        archive.write(package / "createUiDefinition.json", "createUiDefinition.json")
    paths = {"mainTemplate": "Package/mainTemplate.json", "createUiDefinition": "Package/createUiDefinition.json",
             "testParameters": "Package/testParameters.json", "zip": "Package/3.2.1.zip"}
    hashes = {name: hashlib.sha256((solution / path).read_bytes()).hexdigest() for name, path in paths.items()}
    identity = package_input_identity(solution)
    report = {"packager": "V3.1", "workflowRunId": CONTEXT["runId"], "packageAttemptId": "fixture-attempt", "version": "3.2.1",
              "armValidationMethod": "lab-deployment", "packageInputs": {"after": {**identity, "files": package_input_file_hashes(solution)}},
              "packageArtifactHashes": hashes, "packageArtifactsSha256": _canonical_sha256(hashes), **paths}
    report_path = logs / "packaging.v3_1.json"
    report_path.write_text(json.dumps(report))
    gates = {}
    for gate in ("conversion", "review", "structure", "package"):
        path = logs / f"{gate}.json"
        path.write_text(json.dumps({"status": "passed", "workflowRunId": CONTEXT["runId"], "packageInputSha256": identity["sha256"],
                                   "packageArtifactsSha256": report["packageArtifactsSha256"]}))
        gates[gate] = {"path": f"Logs/{gate}.json", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    receipt = logs / "build-and-validate-report.md"
    receipt.write_text("mocked official producer receipt")
    receipt_binding = {"path": str(receipt), "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest()}
    # Official receipt parsing is independently tested below against its full
    # producer layout. These lifecycle fixtures isolate artifacts and dispatch.
    with mock.patch.object(validation, "_parse_build_validation_receipt", return_value=receipt_binding):
        candidate = validation.create_arm_candidate(
            CONTEXT, solution=solution, package_report="Logs/packaging.v3_1.json",
            validation_receipt=receipt, prerequisite_evidence=gates,
        )
        yield {"solution": solution, "candidate": candidate, "report": report, "gates": gates, "receipt": receipt}
    shutil.rmtree(directory)


def plan(case, *, flags=None, target=None):
    return validation.plan_lab_arm_validation(CONTEXT, case["candidate"], target=target or TARGET, selected_flags=FLAGS if flags is None else flags)


def consent_for(plan):
    return validation.review_lab_arm_scope(plan, actor="fixture-reviewer", approval_reference="scope-approval", approved=True)


def execute(case, *, runner=None, consent_reader=None, access=None, refresh=None, **kwargs):
    current_plan = plan(case)
    consent = consent_for(current_plan)
    return validation.execute_lab_arm_validation(
        CONTEXT, case["candidate"], target=TARGET, selected_flags=FLAGS,
        expected_plan_sha256=current_plan["planSha256"], actor="fixture-reviewer", approval_reference="immediate-approval",
        confirmation=validation.LAB_ARM_CONFIRMATION, evidence_directory=case["solution"] / "Logs/sentinel-xdr-migration/fixture-run",
        refresh_candidate=refresh or (lambda: case["candidate"]), read_consent=consent_reader or (lambda: consent),
        identity_check=lambda _target: ACCESS if access is None else access,
        command_runner=runner or (lambda _command: (0, {"id": "fixture-deployment", "properties": {"provisioningState": "Succeeded"}}, "")),
        **kwargs,
    )


def test_methods_legacy_and_versioned_boundaries():
    assert validation.arm_validation_method({"armValidationMethod": "lab-deployment"}) == "arm-ttk"
    assert validation.arm_validation_method(CONTEXT) == "lab-deployment"
    assert validation.arm_validation_method({**CONTEXT, "armValidationMethod": "arm-ttk"}) == "arm-ttk"
    for change in ({"workbookCapabilityVersion": True}, {"workbookCapabilityVersion": 2},
                   {"armValidationMethod": None}, {"profileSelectionConfirmed": False},
                   {"workflowProfile": "qualification", "armValidationMethod": "arm-ttk"}):
        with pytest.raises(ValueError):
            validation.arm_validation_method({**CONTEXT, **change})


def test_qualification_retains_locked_target_and_runtime_gate(case):
    qualification = {**CONTEXT, **TARGET, "workflowProfile": "qualification", "targetContextLocked": True}
    assert validation.arm_validation_method(qualification) == "lab-deployment"
    with pytest.raises(ValueError, match="locked target"):
        validation.arm_validation_method({**qualification, "targetContextLocked": False})
    with pytest.raises(ValueError, match="another workflow run"):
        validation.plan_lab_arm_validation(qualification, case["candidate"], target=TARGET, selected_flags=FLAGS)
    with pytest.raises(ValueError, match="gate evidence"):
        validation.create_arm_candidate(qualification, solution=case["solution"], package_report="Logs/packaging.v3_1.json",
                                        validation_receipt=case["receipt"], prerequisite_evidence=case["gates"])
    path = case["solution"] / "Logs/qualification.json"
    path.write_text(json.dumps({"status": "passed", "packageInputSha256": case["candidate"]["packageIdentity"]["packageInputSha256"],
                               "workflowRunId": CONTEXT["runId"], "qualificationRuntimeVerified": False, "target": TARGET}))
    evidence = {**case["gates"], "qualification": {"path": "Logs/qualification.json", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}}
    with pytest.raises(ValueError, match="existing runtime/target"):
        validation.create_arm_candidate(qualification, solution=case["solution"], package_report="Logs/packaging.v3_1.json",
                                        validation_receipt=case["receipt"], prerequisite_evidence=evidence)
    payload = json.loads(path.read_text())
    payload["qualificationRuntimeVerified"] = True
    path.write_text(json.dumps(payload))
    evidence["qualification"]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    candidate = validation.create_arm_candidate(qualification, solution=case["solution"], package_report="Logs/packaging.v3_1.json",
                                               validation_receipt=case["receipt"], prerequisite_evidence=evidence)
    assert validation.plan_lab_arm_validation(qualification, candidate, target=TARGET, selected_flags=FLAGS)["status"] == "ready"
    retargeted = {**TARGET, "tenantId": "cccccccc-bbbb-cccc-dddd-eeeeeeeeeeee"}
    with pytest.raises(ValueError, match="locked target"):
        validation.plan_lab_arm_validation(qualification, candidate, target=retargeted, selected_flags=FLAGS)


def test_candidate_is_not_accepted_and_binds_every_artifact(case):
    candidate = case["candidate"]
    assert candidate["accepted"] is False
    assert candidate["status"] == "candidate-generated"
    assert set(candidate["packageIdentity"]["packageArtifactHashes"]) == {"mainTemplate", "createUiDefinition", "testParameters", "zip"}
    assert validation.refresh_arm_candidate(CONTEXT, candidate) == candidate


def test_workbook_only_qualification_candidate_precedes_query_and_ui_proof(case):
    context = {
        **CONTEXT, **TARGET, "workflowProfile": "qualification",
        "targetContextLocked": True, "workbookQualificationAfterArm": True,
    }
    candidate = validation.create_arm_candidate(
        context, solution=case["solution"], package_report="Logs/packaging.v3_1.json",
        validation_receipt=case["receipt"], prerequisite_evidence=case["gates"],
    )
    assert candidate["accepted"] is False
    assert validation.plan_lab_arm_validation(
        context, candidate, target=TARGET, selected_flags=FLAGS,
    )["status"] == "ready"
    assert validation.refresh_arm_candidate(context, candidate) == candidate
    case["report"]["xdrDetectionCount"] = 1
    (case["solution"] / "Logs/packaging.v3_1.json").write_text(json.dumps(case["report"]))
    with pytest.raises(ValueError, match="cannot bypass detection runtime"):
        validation.create_arm_candidate(
            context, solution=case["solution"], package_report="Logs/packaging.v3_1.json",
            validation_receipt=case["receipt"], prerequisite_evidence=case["gates"],
        )


def test_production_input_manifest_is_verified_without_rejecting_additive_fields(case):
    recorded = case["report"]["packageInputs"]["after"]
    assert set(recorded) == {"sha256", "fileCount", "files"}
    assert recorded["files"] == package_input_file_hashes(case["solution"])
    case["report"]["packageInputs"]["after"]["captureStatus"] = "complete"
    (case["solution"] / "Logs/packaging.v3_1.json").write_text(json.dumps(case["report"]))
    candidate = validation.create_arm_candidate(
        CONTEXT, solution=case["solution"], package_report="Logs/packaging.v3_1.json",
        validation_receipt=case["receipt"], prerequisite_evidence=case["gates"],
    )
    assert candidate["packageIdentity"]["packageInputSha256"] == recorded["sha256"]


@pytest.mark.parametrize("corruption", ["missing", "null", "list", "wrong-hash", "missing-file", "extra-file"])
def test_production_input_manifest_must_be_exact_even_when_aggregate_is_current(case, corruption):
    recorded = case["report"]["packageInputs"]["after"]
    if corruption == "missing":
        recorded.pop("files")
    elif corruption == "null":
        recorded["files"] = None
    elif corruption == "list":
        recorded["files"] = []
    elif corruption == "wrong-hash":
        recorded["files"]["input.json"] = "b" * 64
    elif corruption == "missing-file":
        recorded["files"].pop("input.json")
    else:
        recorded["files"]["unexpected.json"] = "c" * 64
    (case["solution"] / "Logs/packaging.v3_1.json").write_text(json.dumps(case["report"]))
    with pytest.raises(ValueError, match="input file manifest"):
        validation.create_arm_candidate(
            CONTEXT, solution=case["solution"], package_report="Logs/packaging.v3_1.json",
            validation_receipt=case["receipt"], prerequisite_evidence=case["gates"],
        )


@pytest.mark.parametrize("item", ["input.json", "Package/mainTemplate.json", "Package/3.2.1.zip", "Logs/review.json", "Logs/packaging.v3_1.json"])
def test_stale_input_artifact_gate_or_report_blocks_dispatch(case, item):
    path = case["solution"] / item
    path.write_bytes(path.read_bytes() + b"\n")
    runner = mock.Mock()
    with pytest.raises(ValueError):
        execute(case, runner=runner)
    runner.assert_not_called()


@pytest.mark.parametrize("gate", ["conversion", "review", "structure", "package"])
def test_failed_or_missing_gate_is_not_candidate(case, gate):
    case["gates"].pop(gate)
    with pytest.raises(ValueError, match="gate evidence"):
        validation.create_arm_candidate(CONTEXT, solution=case["solution"], package_report="Logs/packaging.v3_1.json",
                                        validation_receipt=case["receipt"], prerequisite_evidence=case["gates"])


def test_selected_flags_are_exact_and_tenant_extension_scope_is_explicit(case):
    current = plan(case)
    assert current["parameters"]["DeployWorkbook"] is False
    assert current["parameters"]["DeployDefenderWorkbook"] is True
    assert current["scope"]["contentTypes"] == ["DefenderWorkbook"]
    assert "Microsoft.Security/workbooks" in current["scope"]["resourceTypes"]
    assert any(item["scope"] == f"/tenants/{TARGET['tenantId']}" for item in current["resources"])
    for flags in ({"DeployDefenderWorkbook": True}, {**FLAGS, "DeployUnsupported": True}, {**FLAGS, "DeployWorkbook": "false"}):
        with pytest.raises(ValueError):
            plan(case, flags=flags)
    empty = plan(case, flags={name: False for name in FLAGS})
    assert empty["resources"] == [] and empty["expectedWorkbooks"] == []


@pytest.mark.parametrize("change", ["scope", "subscription", "link", "extension", "extension-tenant", "copy", "unknown-condition", "grant"])
def test_nested_or_unresolved_scope_fails_closed(case, change):
    template = workbook_template()
    deployment = template["resources"][0]
    inner = deployment["properties"]["template"]
    if change == "scope":
        deployment["scope"] = "/subscriptions/other/resourceGroups/other"
    elif change == "subscription":
        deployment["subscriptionId"] = "other"
    elif change == "link":
        deployment["properties"]["templateLink"] = {"uri": "https://example.invalid/template"}
    elif change == "extension":
        inner["imports"]["MicrosoftSecurity"]["provider"] = "Unknown"
    elif change == "extension-tenant":
        inner["imports"]["MicrosoftSecurity"]["config"] = {"tenantId": "other"}
    elif change == "copy":
        deployment["copy"] = {"count": 2}
    elif change == "unknown-condition":
        deployment["condition"] = "[unreviewed('something')]"
    else:
        deployment["type"] = "Microsoft.Authorization/roleAssignments"
    with pytest.raises(ValueError):
        validation._resource_inventory(template, {"workspace": "fixture-ws", **FLAGS}, TARGET)


def test_scope_reuses_types_but_not_new_lab_types_or_revocation(case):
    current = plan(case)
    consent = consent_for(current)
    changed = copy.deepcopy(current)
    changed["candidateSha256"] = "b" * 64
    changed["resourceCount"] += 4
    changed.pop("planSha256")
    changed["planSha256"] = _canonical_sha256(changed)
    assert validation.check_lab_arm_scope(changed, consent)["status"] == "ready"
    for field, value in (("contentTypes", "Workbook"), ("resourceTypes", "Microsoft.Compute/virtualMachines"), ("operations", "deletion")):
        extra = copy.deepcopy(changed)
        extra["scope"][field].append(value)
        extra.pop("planSha256")
        extra["planSha256"] = _canonical_sha256(extra)
        assert validation.check_lab_arm_scope(extra, consent)["status"] == "blocked"
    new_lab = copy.deepcopy(changed)
    new_lab["scope"]["lab"]["tenantId"] = "other"
    new_lab.pop("planSha256")
    new_lab["planSha256"] = _canonical_sha256(new_lab)
    assert validation.check_lab_arm_scope(new_lab, consent)["status"] == "blocked"
    assert validation.check_lab_arm_scope(current, None)["status"] == "blocked"
    revoked = validation.withdraw_lab_arm_scope(consent, actor="fixture-reviewer", withdrawal_reference="withdrawn")
    assert validation.check_lab_arm_scope(current, revoked)["status"] == "blocked"


def test_execution_one_executor_and_no_automatic_content_flags(case):
    commands = []
    def runner(command):
        commands.append(command)
        paths = list((case["solution"] / "Logs/sentinel-xdr-migration/fixture-run").glob("arm-validation-attempt-*.json"))
        assert len(paths) == 1
        assert json.loads(paths[0].read_text())["status"] == "write-intent-persisted"
        return 0, {"id": "fixture-deployment", "properties": {"provisioningState": "Succeeded"}}, ""
    report = execute(case, runner=runner)
    assert report["status"] == "arm-accepted-contract-pending" and report["accepted"] is False
    assert "DeployWorkbook=false" in commands[0] and "DeployDefenderWorkbook=true" in commands[0]
    assert len(commands) == 1
    with pytest.raises(ValueError, match="reconciliation"):
        execute(case, runner=runner)
    assert len(commands) == 1


@pytest.mark.parametrize("state,code,expected", [("Failed", 1, "failed"), ("Running", 0, "nonterminal"),
                                                (None, 124, "unknown"), ("Succeeded", 1, "failed")])
def test_failed_unknown_and_nonterminal_are_durable(case, state, code, expected):
    report = execute(case, runner=lambda _: (code, {"properties": {"provisioningState": state}}, "fixture error"))
    assert report["status"] == expected and report["accepted"] is False
    assert json.loads(Path(report["attemptPath"]).read_text())["status"] == expected


def test_exception_is_unknown_and_missing_permissions_block_without_write(case):
    runner = mock.Mock(side_effect=TimeoutError())
    assert execute(case, access={**ACCESS, "extensionResourceWriteAllowed": False}, runner=runner)["writeAttempted"] is False
    runner.assert_not_called()
    report = execute(case, runner=runner)
    assert report["status"] == "unknown" and report["retryAuthorized"] is False


def test_revocation_at_dispatch_boundary_is_durable_and_never_dispatches(case):
    consent = consent_for(plan(case))
    count = 0
    def read():
        nonlocal count
        count += 1
        return consent if count < 3 else validation.withdraw_lab_arm_scope(consent, actor="fixture-reviewer", withdrawal_reference="stop")
    runner = mock.Mock()
    report = execute(case, consent_reader=read, runner=runner)
    assert report["status"] == "blocked-before-write" and report["writeAttempted"] is False
    runner.assert_not_called()


def readback(plan):
    wanted = plan["expectedWorkbooks"][0]
    observed = {}
    for phase in ("installation", "registration", "repeatInstallation", "update"):
        template = workbook_template()
        if phase == "registration":
            resource_id = TARGET["workspaceResourceId"] + "/providers/Microsoft.SecurityInsights/contentTemplates/fixture-registration"
            props = template["resources"][1]["properties"]
        else:
            resource_id = f"/tenants/{TARGET['tenantId']}/providers/Microsoft.Security/workbooks/{wanted['instanceId']}"
            props = template["resources"][0]["properties"]["template"]["resources"]["workbook"]["properties"]
        response_path = Path(plan["solutionPath"]) / "Logs" / f"{phase}-readback.json"
        response_path.write_text(json.dumps({"id": resource_id, "properties": props}))
        write_attempt_path = Path(plan["solutionPath"]) / "Logs" / f"{phase}-attempt.json"
        write_attempt_path.write_text(json.dumps({
            "status": "arm-accepted-contract-pending", "target": TARGET,
            "mainTemplateSha256": plan["mainTemplateSha256"], "parameters": plan["parameters"],
            "candidateSha256": plan["candidateSha256"], "packageIdentity": plan["packageIdentity"],
            "deploymentId": f"fixture-{phase}-write",
        }))
        observed[phase] = {"status": "passed", "httpMethod": "GET",
                           "provider": "microsoft-security" if phase != "registration" else "azure-resource-manager",
                           "operationId": f"fixture-{phase}", "responseSha256": hashlib.sha256(response_path.read_bytes()).hexdigest(),
                           "responsePath": f"Logs/{phase}-readback.json", "requestResourceId": resource_id,
                           "writeOperationId": f"fixture-{phase}-write", "writeStatus": "succeeded",
                           "writeAttemptPath": f"Logs/{phase}-attempt.json", "writeAttemptSha256": hashlib.sha256(write_attempt_path.read_bytes()).hexdigest()}
    return {"planSha256": plan["planSha256"], "target": TARGET, "armStatus": "succeeded",
            "deploymentId": "fixture-deployment", "workbooks": [observed]}


def test_contract_requires_independent_registration_provenance_and_repeat_update(case):
    current = plan(case)
    evidence = readback(current)
    result = validation.verify_workbook_readback(current, evidence)
    assert result["status"] == "verified" and result["accepted"] is True
    assert result["uiVerified"] is False and result["parityVerified"] is False
    for phase in ("installation", "registration", "repeatInstallation", "update"):
        broken = copy.deepcopy(evidence)
        broken["workbooks"][0][phase]["status"] = "denied"
        assert validation.verify_workbook_readback(current, broken)["accepted"] is False
    stale = copy.deepcopy(evidence)
    path = case["solution"] / stale["workbooks"][0]["registration"]["responsePath"]
    payload = json.loads(path.read_text())
    payload["properties"]["contentProvenance"]["packageId"] = "unexpected"
    path.write_text(json.dumps(payload))
    stale["workbooks"][0]["registration"]["responseSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert validation.verify_workbook_readback(current, stale)["status"] == "blocked"


def test_arm_success_alone_never_verifies_workbook_contract(case):
    current = plan(case)
    result = validation.verify_workbook_readback(current, {"planSha256": current["planSha256"], "target": TARGET, "armStatus": "succeeded"})
    assert result["accepted"] is False


def test_powershell_method_route_replaces_only_native_arm_branch():
    script = ROOT / ".script/local-validation/build-and-validate.ps1"
    source = script.read_text()
    section = source.split("# ARM-TTK Validator (local", 1)[1].split("# STEP 4:", 1)[0]
    # Isolate only the official ARM routing block; no dependency installation,
    # authentication or other live/network validator is invoked in these tests.
    branch = section[section.index('    if ($ArmValidationMethod -eq "lab-deployment")'):section.rfind("\n}")]
    command = (
        "$ErrorActionPreference='Stop';$ArmValidationMethod='lab-deployment';"
        "$overallSuccess=$true;$reportEntries=[System.Collections.ArrayList]::new();"
        "function Test-Path { throw 'unexpected filesystem/dependency route' };"
        + branch
        + ";if($reportEntries.Count -ne 1 -or $reportEntries[0].Name -ne 'ARM-TTK' -or $reportEntries[0].Status -ne 'skipped' -or -not $overallSuccess){exit 1};'Lab ARM routing passed'"
    )
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", command], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "Lab ARM routing passed" in result.stdout
    assert "STEP 4: CI PowerShell Validators" in source
    assert "Complete-ValidationEvidenceBinding" in source
    assert 'packageAccepted = $false' in source
    assert "**CANDIDATE GENERATED — NOT ACCEPTED**" in source


def test_arm_ttk_metadata_finding_is_not_filtered_and_actual_resource_id_still_fails(case):
    (case["solution"] / "Package/createUiDefinition.json").unlink()
    runner = ROOT / ".script/local-validation/run-arm-ttk.ps1"
    command = """
function Get-Module { return @{Name='arm-ttk'} }
function Import-Module {}
function Test-AzTemplate {
    $errors=@(
        [pscustomobject]@{Exception=[Exception]::new('Property "packageId" must use resourceId() at contentProvenance.packageId')},
        [pscustomobject]@{Exception=[Exception]::new('Property "resourceId" contains a hardcoded actual resource ID')}
    )
    @([pscustomobject]@{Name='IDs Should Be Derived From ResourceIDs';Errors=$errors},
      [pscustomobject]@{Name='Summary';Errors=@();Summary=[pscustomobject]@{Pass=0;Fail=2}})
}
""" + f"& '{runner}' -SolutionPath '{case['solution']}' -ToolkitRoot '{ROOT}'"
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", command], text=True, capture_output=True)
    assert result.returncode == 1, result.stderr
    assert "Fail=2" in result.stdout
    assert "resourceId" not in runner.read_text()


def test_official_receipt_method_binding_distinguishes_candidates_and_legacy():
    import test_arm_acceptance as fixtures
    from sentinel_xdr_migration import arm_acceptance

    harness = fixtures.ArmTemplateAcceptanceTests()
    created = harness._write_build_validation_receipt(
        rows=["| TS | JSON Syntax | PASS | fixture |", "| .NET | ARM-TTK | SKIP | replaced |"],
        result="CANDIDATE_GENERATED",
    )
    toolkit, receipt, report, identity, package_files = created
    try:
        binding_path = receipt.parent / "build-and-validate-binding.json"
        old_hash = hashlib.sha256(binding_path.read_bytes()).hexdigest()
        binding = json.loads(binding_path.read_text())
        binding.update(validationResult="PASSED", armValidationMethod="lab-deployment", armValidationStatus="pending",
                       packageLifecycleStatus="candidate-generated", packageAccepted=False, workbookCapabilityVersion=1)
        binding_path.write_text(json.dumps(binding))
        receipt.write_text(receipt.read_text().replace("**BUILD SUCCESSFUL**", "**CANDIDATE GENERATED — NOT ACCEPTED**").replace("**BUILD FAILED**", "**CANDIDATE GENERATED — NOT ACCEPTED**").replace("Validation binding result: CANDIDATE_GENERATED", "Validation binding result: PASSED").replace(old_hash, hashlib.sha256(binding_path.read_bytes()).hexdigest()))
        result = arm_acceptance._parse_build_validation_receipt(
            fixtures.FIXTURE_ROOT, receipt, package_report_path=report, package_identity=identity,
            arm_validation_method="lab-deployment",
        )
        assert result["binding"]["packageAccepted"] is False
        with pytest.raises(ValueError):
            arm_acceptance._parse_build_validation_receipt(
                fixtures.FIXTURE_ROOT, receipt, package_report_path=report, package_identity=identity,
            )
        with pytest.raises(ValueError):
            arm_acceptance._parse_build_validation_receipt(
                fixtures.FIXTURE_ROOT, receipt, package_report_path=report, package_identity=identity, arm_validation_method="arm-ttk",
            )
    finally:
        harness._cleanup_build_validation_fixture(toolkit, report, package_files)


def test_actual_arm_ttk_pass_is_required_for_explicit_new_alternative():
    import test_arm_acceptance as fixtures
    from sentinel_xdr_migration import arm_acceptance

    harness = fixtures.ArmTemplateAcceptanceTests()
    created = harness._write_build_validation_receipt(
        rows=["| TS | JSON Syntax | PASS | fixture |", "| .NET | ARM-TTK | PASS | actual runner |"],
        summary="Total: 2 validators | 2 passed | 0 failed | 0 skipped",
    )
    toolkit, receipt, report, identity, package_files = created
    try:
        assert arm_acceptance._parse_build_validation_receipt(
            fixtures.FIXTURE_ROOT, receipt, package_report_path=report, package_identity=identity, arm_validation_method="arm-ttk",
        )["status"] == "PASSED"
    finally:
        harness._cleanup_build_validation_fixture(toolkit, report, package_files)
    created = harness._write_build_validation_receipt()
    toolkit, receipt, report, identity, package_files = created
    try:
        with pytest.raises(ValueError, match="actual passed ARM-TTK"):
            arm_acceptance._parse_build_validation_receipt(
                fixtures.FIXTURE_ROOT, receipt, package_report_path=report, package_identity=identity, arm_validation_method="arm-ttk",
            )
    finally:
        harness._cleanup_build_validation_fixture(toolkit, report, package_files)


def test_raw_readback_hash_identity_and_arm_output_reuse_block(case):
    current = plan(case)
    evidence = readback(current)
    for field, value in (("responseSha256", "b" * 64), ("requestResourceId", "/tenants/other/workbooks/other"),
                         ("httpMethod", "PUT"), ("provider", "arm-deployment-output"),
                         ("operationId", "fixture-registration")):
        broken = copy.deepcopy(evidence)
        broken["workbooks"][0]["installation"][field] = value
        assert validation.verify_workbook_readback(current, broken)["status"] == "blocked"
    broken = copy.deepcopy(evidence)
    broken["workbooks"][0]["update"]["writeOperationId"] = "fixture-installation-write"
    assert validation.verify_workbook_readback(current, broken)["status"] == "blocked"


def test_unreconciled_attempt_blocks_changed_candidates_and_execution_references(case):
    execute(case, runner=lambda _: (124, None, "timeout"))
    case["candidate"]["packageIdentity"]["packageAttemptId"] = "changed-attempt"
    case["candidate"].pop("candidateSha256")
    case["candidate"]["candidateSha256"] = _canonical_sha256(case["candidate"])
    runner = mock.Mock()
    with mock.patch.object(validation, "refresh_arm_candidate", return_value=case["candidate"]):
        with pytest.raises(ValueError, match="executor requires independent reconciliation"):
            execute(case, runner=runner)
    runner.assert_not_called()


def test_reconcile_requires_independent_exact_terminal_get_and_retains_history(case):
    first = execute(case, runner=lambda _: (124, None, "timeout"))
    resource_id = (
        f"/subscriptions/{TARGET['subscriptionId']}/resourceGroups/{TARGET['resourceGroup']}"
        f"/providers/Microsoft.Resources/deployments/{first['deploymentName']}"
    )
    response_path = case["solution"] / "Logs/deployment-get.json"
    response_path.write_text(json.dumps({"id": resource_id, "properties": {"provisioningState": "Failed"}}))
    observation = {"status": "passed", "httpMethod": "GET", "target": TARGET, "deploymentId": resource_id,
                   "provisioningState": "Failed", "responsePath": "Logs/deployment-get.json",
                   "responseSha256": hashlib.sha256(response_path.read_bytes()).hexdigest()}
    for change in ({"httpMethod": "PUT"}, {"provisioningState": "Running"}, {"deploymentId": "other"}, {"status": "denied"}):
        with pytest.raises(ValueError):
            validation.reconcile_lab_arm_attempt(first["attemptPath"], observation={**observation, **change}, actor="reviewer", reference="reconciliation")
    reconciled = validation.reconcile_lab_arm_attempt(first["attemptPath"], observation=observation, actor="reviewer", reference="reconciliation")
    assert reconciled["status"] == "failed" and reconciled["accepted"] is False and reconciled["retryAuthorized"] is False
    assert reconciled["commandExitCode"] == 124
    with pytest.raises(ValueError):
        execute(case)
    # A new explicit immediate approval reference is a new attempt, after
    # independent terminal reconciliation; the old receipt is never overwritten.
    current_plan = plan(case)
    consent = consent_for(current_plan)
    next_result = validation.execute_lab_arm_validation(
        CONTEXT, case["candidate"], target=TARGET, selected_flags=FLAGS,
        expected_plan_sha256=current_plan["planSha256"], actor="reviewer", approval_reference="new-immediate-approval",
        confirmation=validation.LAB_ARM_CONFIRMATION,
        evidence_directory=case["solution"] / "Logs/sentinel-xdr-migration/fixture-run",
        refresh_candidate=lambda: case["candidate"], read_consent=lambda: consent, identity_check=lambda _: ACCESS,
        command_runner=lambda _: (0, {"properties": {"provisioningState": "Succeeded"}}, ""),
    )
    assert next_result["status"] == "arm-accepted-contract-pending"
    assert next_result["attemptPath"] != first["attemptPath"]
    assert json.loads(Path(first["attemptPath"]).read_text())["status"] == "failed"


def test_same_type_changed_hash_count_uses_old_scope_only_with_fresh_evidence(case):
    original = plan(case)
    consent = consent_for(original)
    root = case["solution"]
    template_path = root / "Package/mainTemplate.json"
    template = json.loads(template_path.read_text())
    template["resources"].append({
        "type": "Microsoft.Resources/deployments", "name": "another-fixture-install",
        "properties": {"mode": "Incremental", "template": {"resources": []}},
    })
    template_path.write_text(json.dumps(template))
    with zipfile.ZipFile(root / "Package/3.2.1.zip", "w") as archive:
        archive.write(template_path, "mainTemplate.json")
        archive.write(root / "Package/createUiDefinition.json", "createUiDefinition.json")
    report = case["report"]
    report["packageArtifactHashes"] = {name: hashlib.sha256((root / report[name]).read_bytes()).hexdigest()
                                      for name in report["packageArtifactHashes"]}
    report["packageArtifactsSha256"] = _canonical_sha256(report["packageArtifactHashes"])
    (root / "Logs/packaging.v3_1.json").write_text(json.dumps(report))
    with pytest.raises(ValueError, match="exact current candidate artifacts"):
        validation.create_arm_candidate(CONTEXT, solution=root, package_report="Logs/packaging.v3_1.json",
                                        validation_receipt=case["receipt"], prerequisite_evidence=case["gates"])
    for name in ("structure", "package"):
        path = root / case["gates"][name]["path"]
        payload = json.loads(path.read_text())
        payload["packageArtifactsSha256"] = report["packageArtifactsSha256"]
        path.write_text(json.dumps(payload))
        case["gates"][name]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    case["candidate"] = validation.create_arm_candidate(
        CONTEXT, solution=root, package_report="Logs/packaging.v3_1.json",
        validation_receipt=case["receipt"], prerequisite_evidence=case["gates"],
    )
    current = plan(case)
    assert original["candidateSha256"] != current["candidateSha256"]
    assert current["resourceCount"] == original["resourceCount"] + 1
    assert validation.check_lab_arm_scope(current, consent)["status"] == "ready"
    assert execute(case, consent_reader=lambda: consent)["status"] == "arm-accepted-contract-pending"


def test_powershell_native_arm_route_still_calls_original_validator():
    source = (ROOT / ".script/local-validation/build-and-validate.ps1").read_text()
    section = source.split("# ARM-TTK Validator (local", 1)[1].split("# STEP 4:", 1)[0]
    branch = section[section.index('    if ($ArmValidationMethod -eq "lab-deployment")'):section.rfind("\n}")]
    command = (
        "$ErrorActionPreference='Stop';$ArmValidationMethod='arm-ttk';$overallSuccess=$true;"
        "$reportEntries=[System.Collections.ArrayList]::new();$saveProcessOutput={param($name,$output)'fixture-log'};"
        f"$toolkitRoot='{ROOT}';$solutionPath='{ROOT}';$packageDir='{ROOT}';"
        "function Test-Path {return $true};function pwsh {$global:LASTEXITCODE=0;'ARM-TTK-SUMMARY: Pass=1 Fail=0 Total=1'};"
        + branch
        + ";if($reportEntries.Count -ne 1 -or $reportEntries[0].Name -ne 'ARM-TTK' -or $reportEntries[0].Status -ne 'passed' -or -not $overallSuccess){exit 1};'Native ARM routing passed'"
    )
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", command], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "Native ARM routing passed" in result.stdout


def test_arm_ttk_contract_plan_is_read_only_and_cannot_authorize_lab_write(case):
    context = {**CONTEXT, "armValidationMethod": "arm-ttk"}
    candidate = copy.deepcopy(case["candidate"])
    candidate["armValidationMethod"] = "arm-ttk"
    candidate.pop("candidateSha256")
    candidate["candidateSha256"] = _canonical_sha256(candidate)
    current = validation.plan_workbook_contract_verification(context, candidate, target=TARGET, selected_flags=FLAGS)
    assert current["deploymentAuthorizedRoute"] is False and current["purpose"] == "workbook-contract-readback"
    with pytest.raises(ValueError):
        consent_for(current)
    with pytest.raises(ValueError):
        validation.plan_lab_arm_validation(context, candidate, target=TARGET, selected_flags=FLAGS)
    assert validation.verify_workbook_readback(current, readback(current))["status"] == "verified"


def test_readback_becomes_stale_after_current_candidate_inputs_change(case):
    current = plan(case)
    evidence = readback(current)
    (case["solution"] / "input.json").write_text('{"changed":true}')
    assert validation.verify_workbook_readback(current, evidence)["status"] == "blocked"
