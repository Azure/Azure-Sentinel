from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

from sentinel_xdr_migration import workbook_preflight as preflight
from sentinel_xdr_migration import workbook_validation as validation
from sentinel_xdr_migration.arm_acceptance_support import _canonical_sha256

ROOT = Path(__file__).resolve().parents[3]
TARGET = {
    "tenantId": "11111111-2222-3333-4444-555555555555",
    "subscriptionId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "resourceGroup": "fixture-rg",
    "workspaceResourceId": "/subscriptions/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/resourceGroups/fixture-rg/providers/Microsoft.OperationalInsights/workspaces/fixture-ws",
    "workspaceCustomerId": "99999999-8888-7777-6666-555555555555",
}
PRINCIPAL = "cccccccc-1111-2222-3333-444444444444"
CONTENT = "aaaaaaaa-1111-2222-3333-444444444444"
INSTANCE = "bbbbbbbb-1111-2222-3333-444444444444"
CONTEXT = {
    "runId": "preflight-fixture", "workflowProfile": "authoring", "profileSelectionConfirmed": True,
    "workbookCapabilityVersion": 1, "armValidationMethod": "lab-deployment",
}


def seal(value, field):
    value.pop(field, None)
    value[field] = _canonical_sha256(value)
    return value


def template():
    provenance = {"packageId": "publisher.fixture", "packageVersion": "3.1.1",
                  "contentId": CONTENT, "contentVersion": "3.1.1"}
    notebook = {"version": "Notebook/1.0", "items": [], "contentProvenance": provenance}
    inner = {
        "languageVersion": "2.0",
        "imports": {"MicrosoftSecurity": {"provider": "MicrosoftSecurity", "version": "1.0.0"}},
        "resources": {"workbook": {
            "type": "Microsoft.Security/workbooks@2026-06-01-preview", "import": "MicrosoftSecurity",
            "properties": {"id": INSTANCE, "name": "Fixture", "content": notebook},
        }},
    }
    return {
        "parameters": {"workspace": {"type": "string"}, "DeployDefenderWorkbook": {"type": "bool", "defaultValue": False}},
        "resources": [
            {"type": "Microsoft.Resources/deployments", "name": "install",
             "condition": "[parameters('DeployDefenderWorkbook')]",
             "properties": {"mode": "Incremental", "template": inner}},
            {"type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
             "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/fixture')]",
             "properties": {"contentId": CONTENT, "contentKind": "DefenderWorkbook", "version": "3.1.1",
                            "packageId": "publisher.fixture", "packageVersion": "3.1.1",
                            "mainTemplate": copy.deepcopy(inner), "contentProvenance": provenance}},
            {"type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
             "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/publisher.fixture')]",
             "properties": {"contentId": "publisher.fixture", "contentKind": "Solution",
                            "dependencies": {"criteria": [{"kind": "DefenderWorkbook", "contentId": CONTENT}]} }},
        ],
    }


@pytest.fixture
def case():
    directory = ROOT / ".script/local-validation/Logs" / ("preflight-tests-" + uuid.uuid4().hex)
    directory.mkdir(parents=True)
    path = directory / "mainTemplate.json"
    path.write_text(json.dumps(template()), encoding="utf-8")
    candidate = seal({
        "status": "candidate-generated", "accepted": False, "armValidationMethod": "lab-deployment",
        "runId": CONTEXT["runId"], "workflowProfile": "authoring", "solutionPath": str(directory),
        "artifactPaths": {"mainTemplate": "mainTemplate.json"}, "packageIdentity": {"packageId": "publisher.fixture"},
        "prerequisiteEvidence": {}, "validationReceipt": {},
        "mainTemplateSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }, "candidateSha256")
    arm = validation.plan_lab_arm_validation(CONTEXT, candidate, target=TARGET,
        selected_flags={"DeployDefenderWorkbook": True})
    plan = preflight.plan_arm_preflight(arm)
    consent = preflight.review_arm_preflight(plan, "fixture-reviewer", "metadata-approval", True)
    try:
        yield {"plan": plan, "arm": arm, "path": path, "consent": consent}
    finally:
        shutil.rmtree(directory)


def response_for(operation, case):
    identifier = operation["id"]
    if identifier == "account":
        body = {"id": TARGET["subscriptionId"], "tenantId": TARGET["tenantId"], "user": {"name": "fixture@example.invalid"},
                "principal": {"objectId": PRINCIPAL, "tenantId": TARGET["tenantId"],
                              "audience": preflight.ARM_BASE, "expiresOn": time.time() + 3600,
                              "source": "authenticated-arm-token"}}
    elif identifier == "workspace":
        body = {"id": TARGET["workspaceResourceId"], "properties": {"customerId": TARGET["workspaceCustomerId"]}}
    elif identifier == "resource-group":
        body = {"id": TARGET["workspaceResourceId"].split("/providers/")[0], "tags": {"Environment": "sandbox"}}
    elif identifier.startswith("permissions-"):
        body = {"value": [{"actions": ["*"], "notActions": [], "dataActions": [], "notDataActions": []}]}
    elif identifier.startswith(("denies-", "role-assignments-")):
        body = {"value": []}
    elif identifier.startswith("registrations-"):
        family = identifier.split("-", 1)[1]
        resource = next(row for row in template()["resources"] if row["type"].endswith("/" + family))
        name = "fixture" if family == "contentTemplates" else "publisher.fixture"
        body = {"value": [{"id": TARGET["workspaceResourceId"] + "/providers/Microsoft.SecurityInsights/" + family + "/" + name,
                           "properties": copy.deepcopy(resource["properties"])}]}
    elif identifier == "workbook-" + INSTANCE:
        body = {"id": INSTANCE, "name": "Fixture", "content": copy.deepcopy(
            template()["resources"][0]["properties"]["template"]["resources"]["workbook"]["properties"]["content"])}
    else:
        raise AssertionError(identifier)
    result = {"statusCode": 200, "body": body}
    if operation["kind"] != "azure-cli-account":
        result.update(principalId=PRINCIPAL, tenantId=TARGET["tenantId"], provenance={
            "requestUrl": operation["url"], "method": "GET",
            "source": "authenticated-arm-token" if operation["kind"] == "arm-get" else "authenticated-graph-token",
            "principalId": PRINCIPAL, "tenantId": TARGET["tenantId"],
        })
    return result


def execute(case, change=None, consent_reader=None):
    calls = []

    def reader(operation):
        calls.append(copy.deepcopy(operation))
        result = response_for(operation, case)
        if change:
            change(operation, result)
        return result

    result = preflight.execute_arm_preflight(case["plan"],
        read_consent=consent_reader or (lambda: case["consent"]), reader=reader)
    return result, calls


def refresh_arm(case, current):
    case["path"].write_text(json.dumps(current))
    arm = copy.deepcopy(case["arm"])
    arm["mainTemplateSha256"] = hashlib.sha256(case["path"].read_bytes()).hexdigest()
    arm["candidateSha256"] = _canonical_sha256({"updatedTemplate": arm["mainTemplateSha256"]})
    arm["resources"] = validation._resource_inventory(current, arm["parameters"], arm["target"])
    arm["expectedWorkbooks"] = validation._expected_workbook_contracts(current, True)
    arm["resourceCount"] = len(arm["resources"])
    arm["scope"]["resourceTypes"] = sorted({row["type"] for row in arm["resources"]} | {"Microsoft.Resources/deployments"})
    return seal(arm, "planSha256")


def test_deterministic_bounded_exact_read_plan_and_bindings(case):
    plan = case["plan"]
    assert plan == preflight.plan_arm_preflight(case["arm"])
    assert plan["armPlanSha256"] == case["arm"]["planSha256"]
    assert plan["candidateSha256"] == case["arm"]["candidateSha256"]
    assert plan["mainTemplateSha256"] == case["arm"]["mainTemplateSha256"]
    assert plan["preflightScopeSha256"] == _canonical_sha256(plan["readScope"])
    assert plan["operations"][0]["subscriptionId"] == TARGET["subscriptionId"]
    assert len(plan["operations"]) == 12
    for operation in plan["operations"][1:]:
        assert operation["method"] == "GET"
        assert operation["url"].startswith((preflight.ARM_BASE + "/", preflight.GRAPH_BASE + "/"))
        assert operation["timeoutSeconds"] == 15 and operation["retryCount"] == 0
    assert next(row for row in plan["operations"] if row["kind"] == "graph-get")["url"] == (
        preflight.GRAPH_BASE + "/beta/security/workbooks/" + INSTANCE)
    assert all(Path(name).name == name for name in plan["artifacts"].values())
    assert plan["writesAuthorized"] is False
    assert plan["tokenAcquisitionAuthorized"] is True
    assert plan["signInAuthorized"] is False
    assert all("atScope()" in operation["url"] for operation in plan["operations"]
               if operation["id"].startswith(("denies-", "role-assignments-")))


def test_verified_facts_but_imported_provider_write_contract_stays_blocked(case):
    result, calls = execute(case)
    assert calls == case["plan"]["operations"]
    assert result["status"] == "blocked"
    for flag in preflight._ACCESS_FLAGS:
        assert result[flag] is (flag != "extensionResourceWriteAllowed")
    assert result["identityId"] == PRINCIPAL
    assert result["providerWriteContractVerified"] is False
    assert result["writeAttempted"] is False
    assert "VERIFIED documented MicrosoftSecurity" in result["checks"]["extensionResourceWriteAllowed"]["reasons"][0]
    assert result["checks"]["nonProduction"]["tenantNonProductionVerified"] is False
    assert result["checks"]["armDeploymentAllowed"]["actions"]["Microsoft.SecurityInsights/contentTemplates/write"]["status"] == "ready"
    assert result["observationSha256"]


def test_parent_minimal_trusted_reader_protocol_and_unverified_graph(case):
    def change(operation, response):
        response.pop("provenance", None)
        if operation["kind"] == "graph-get":
            response.update(statusCode=0, body={"error": {"code": "MicrosoftSecurityIdentityUnverified"}})
    result, calls = execute(case, change)
    assert len(calls) == len(case["plan"]["operations"])
    assert result["tenantMatches"] is True
    assert result["armDeploymentAllowed"] is True
    assert result["ownershipVerified"] is False
    assert result["extensionResourceWriteAllowed"] is False
    assert result["target"] == TARGET
    assert result["preflightPlanSha256"] == case["plan"]["preflightPlanSha256"]
    assert result["observations"]["responses"][1]["provenance"]["source"] == "consent-bound-reader-dispatch"


def test_read_consent_explicitly_limits_arm_token_acquisition_and_refresh(case):
    plan, consent = case["plan"], case["consent"]
    token_access = {
        "scope": "https://management.azure.com/.default",
        "tenantId": TARGET["tenantId"], "subscriptionId": TARGET["subscriptionId"],
        "existingCachedIdentityOnly": True, "acquisitionAuthorized": True, "refreshAuthorized": True,
        "interactiveSignInAuthorized": False, "newCredentialsAuthorized": False,
        "permissionGrantsAuthorized": False, "graphTokenAcquisitionAuthorized": False,
        "graphTokenReuseAuthorized": False,
        "advancedHuntingCredentialReuseAuthorized": False,
    }
    for record in (plan, plan["readScope"], consent, consent["readScope"]):
        assert record["tokenAcquisitionAuthorized"] is True
        assert record["armTokenAccess"] == token_access
        assert all(record[key] is False for key in preflight._FORBIDDEN_AUTHORIZATIONS)
    assert plan["readScope"]["principalContract"]["armTokenAccess"] == token_access
    assert consent["preflightScopeSha256"] == _canonical_sha256(consent["readScope"])


@pytest.mark.parametrize("field", [
    "signInAuthorized", "interactiveSignInAuthorized", "newCredentialsAuthorized",
    "permissionGrantsAuthorized", "graphTokenAcquisitionAuthorized",
    "graphTokenReuseAuthorized",
    "advancedHuntingCredentialReuseAuthorized", "existingCachedIdentityOnly", "scope", "tenantId",
])
def test_resealed_consent_cannot_authorize_sign_in_credentials_graph_or_ah_reuse(case, field):
    consent = copy.deepcopy(case["consent"])
    if field == "existingCachedIdentityOnly":
        consent["armTokenAccess"][field] = False
    elif field == "scope":
        consent["armTokenAccess"][field] = "https://graph.microsoft.com/.default"
    elif field == "tenantId":
        consent["armTokenAccess"][field] = str(uuid.uuid4())
    else:
        consent[field] = True
    seal(consent, "consentSha256")
    result, calls = execute(case, consent_reader=lambda: consent)
    assert calls == []
    assert result["readAttempted"] is False


def test_old_no_acquisition_consent_requires_renewed_explicit_token_scope_review(case):
    consent = copy.deepcopy(case["consent"])
    consent["tokenAcquisitionAuthorized"] = False
    consent.pop("armTokenAccess")
    seal(consent, "consentSha256")
    result, calls = execute(case, consent_reader=lambda: consent)
    assert calls == []
    assert result["checks"]["readConsentVerified"]["status"] == "blocked"


@pytest.mark.parametrize("decision", ["missing", "declined", "revoked", "wrong-target", "tampered", "wrong-plan"])
def test_no_current_exact_approval_means_zero_reader_calls(case, decision):
    consent = copy.deepcopy(case["consent"])
    if decision == "missing":
        consent = None
    elif decision == "declined":
        consent = preflight.review_arm_preflight(case["plan"], "reviewer", "declined", False)
    elif decision == "revoked":
        consent = preflight.revoke_arm_preflight(consent, "reviewer", "revoked")
    elif decision == "wrong-target":
        consent["target"]["tenantId"] = str(uuid.uuid4())
        seal(consent, "consentSha256")
    elif decision == "wrong-plan":
        consent["preflightScopeSha256"] = "0" * 64
        seal(consent, "consentSha256")
    else:
        consent["operations"][1]["method"] = "POST"
    result, calls = execute(case, consent_reader=lambda: consent)
    assert calls == []
    assert result["readAttempted"] is False
    assert result["status"] == "blocked"
    assert result["ownershipVerified"] is False


def test_revoke_during_read_invalidates_evidence_and_stops(case):
    calls = []
    consent = case["consent"]

    def reader(operation):
        nonlocal consent
        calls.append(operation)
        consent = preflight.revoke_arm_preflight(consent, "reviewer", "mid-read")
        return response_for(operation, case)

    result = preflight.execute_arm_preflight(case["plan"], read_consent=lambda: consent, reader=reader)
    assert len(calls) == 1
    assert result["observations"]["responses"][0]["status"] == "blocked"
    assert result["checks"]["readConsentVerified"]["status"] == "blocked"


def test_same_read_scope_reuses_consent_for_fresh_same_id_candidate(case):
    current = template()
    inner = current["resources"][0]["properties"]["template"]
    inner["resources"]["workbook"]["properties"]["content"]["items"] = [{"shipped": "new-version"}]
    current["resources"][1]["properties"]["mainTemplate"] = copy.deepcopy(inner)
    arm = refresh_arm(case, current)
    old_plan = case["plan"]
    case["plan"] = preflight.plan_arm_preflight(arm)
    assert case["plan"]["preflightPlanSha256"] != old_plan["preflightPlanSha256"]
    assert case["plan"]["candidateSha256"] != old_plan["candidateSha256"]
    assert case["plan"]["mainTemplateSha256"] != old_plan["mainTemplateSha256"]
    assert case["plan"]["preflightScopeSha256"] == old_plan["preflightScopeSha256"]
    result, calls = execute(case)
    assert calls == case["plan"]["operations"]
    assert result["checks"]["readConsentVerified"]["status"] == "verified"
    assert result["ownershipVerified"] is True
    assert result["preflightPlanSha256"] == case["plan"]["preflightPlanSha256"]


def test_new_instance_url_requires_renewed_exact_metadata_scope_consent(case):
    current = template()
    inner = current["resources"][0]["properties"]["template"]
    inner["resources"]["workbook"]["properties"]["id"] = str(uuid.uuid4())
    current["resources"][1]["properties"]["mainTemplate"] = copy.deepcopy(inner)
    arm = refresh_arm(case, current)
    old_scope = case["plan"]["preflightScopeSha256"]
    case["plan"] = preflight.plan_arm_preflight(arm)
    assert case["plan"]["preflightScopeSha256"] != old_scope
    result, calls = execute(case)
    assert calls == []
    assert result["readAttempted"] is False


@pytest.mark.parametrize("status", [403, 429, 404, 500])
def test_failed_reads_are_not_empty_success(case, status):
    def change(operation, response):
        if operation["id"] == "workspace":
            response.update(statusCode=status, body={"error": {"message": "Bearer synthetic-token"}})
    result, calls = execute(case, change)
    assert len(calls) == 2
    assert result["workspaceMatches"] is False
    assert result["armDeploymentAllowed"] is False
    assert result["observations"]["responses"][-1]["body"]["error"]["message"] == "Bearer [redacted]"


@pytest.mark.parametrize("bad", ["nextLink", "@odata.nextLink", "empty-body", "non-object", "wrong-status-type"])
def test_malformed_and_partial_responses_remain_unknown(case, bad):
    def change(operation, response):
        if operation["id"] != "workspace":
            return
        if bad in {"nextLink", "@odata.nextLink"}:
            response["body"][bad] = "https://unreviewed.example.invalid/next"
        elif bad == "empty-body":
            response["body"] = {}
        elif bad == "non-object":
            response["body"] = []
        else:
            response["statusCode"] = True
    result, _ = execute(case, change)
    assert result["workspaceMatches"] is False
    assert result["status"] == "blocked"


def test_timeout_reader_error_is_sanitized_and_bounded(case):
    calls = []

    def reader(operation):
        calls.append(operation)
        raise TimeoutError("Bearer do-not-persist-this")
    result = preflight.execute_arm_preflight(case["plan"], read_consent=lambda: case["consent"], reader=reader)
    assert len(calls) == 1
    assert "TimeoutError" in result["observations"]["responses"][0]["reason"]
    assert "do-not-persist" not in json.dumps(result)


@pytest.mark.parametrize("failure", [ValueError, RuntimeError, OSError, KeyError, TypeError])
@pytest.mark.parametrize("phase", ["consent", "reader"])
def test_supported_provider_and_consent_failures_are_sanitized_blockers(case, failure, phase):
    calls = []

    def unavailable():
        raise failure("Bearer forbidden-sensitive-message")

    def reader(operation):
        calls.append(operation)
        if phase == "reader":
            unavailable()
        return response_for(operation, case)
    result = preflight.execute_arm_preflight(case["plan"],
        read_consent=unavailable if phase == "consent" else lambda: case["consent"], reader=reader)
    assert len(calls) == (0 if phase == "consent" else 1)
    assert result["status"] == "blocked"
    assert "forbidden-sensitive-message" not in json.dumps(result)


@pytest.mark.parametrize("failure", [AssertionError, AttributeError, IndexError, MemoryError])
@pytest.mark.parametrize("phase", ["consent", "reader"])
def test_unexpected_programmer_or_system_exceptions_propagate(case, failure, phase):
    def unexpected(*args):
        raise failure("unexpected implementation failure")
    with pytest.raises(failure):
        preflight.execute_arm_preflight(case["plan"],
            read_consent=unexpected if phase == "consent" else lambda: case["consent"],
            reader=unexpected if phase == "reader" else lambda operation: response_for(operation, case))


def test_reader_overrun_is_rejected_without_retry(case, monkeypatch):
    times = iter([0.0, 16.0])
    monkeypatch.setattr(preflight.time, "monotonic", lambda: next(times))
    result, calls = execute(case)
    assert len(calls) == 1
    assert result["observations"]["responses"][0]["reason"] == "reader exceeded bounded timeout"
    assert result["status"] == "blocked"


def test_mutation_of_caller_plan_during_read_stops_dispatch(case):
    calls = []

    def reader(operation):
        calls.append(operation)
        case["plan"]["operations"][1]["method"] = "POST"
        return response_for(operation, case)
    result = preflight.execute_arm_preflight(case["plan"], read_consent=lambda: case["consent"], reader=reader)
    assert len(calls) == 1
    assert result["observations"]["responses"][0]["status"] == "blocked"


@pytest.mark.parametrize("bad", ["account-name-only", "wrong-principal", "wrong-request-proof", "expired", "wrong-audience", "wrong-tenant"])
def test_identity_requires_observed_authenticated_arm_principal(case, bad):
    def change(operation, response):
        if bad == "account-name-only" and operation["id"] == "account":
            del response["body"]["principal"]
        elif bad == "expired" and operation["id"] == "account":
            response["body"]["principal"]["expiresOn"] = time.time() - 1
        elif bad == "wrong-audience" and operation["id"] == "account":
            response["body"]["principal"]["audience"] = preflight.GRAPH_BASE
        elif bad == "wrong-tenant" and operation["id"] == "account":
            response["body"]["principal"]["tenantId"] = str(uuid.uuid4())
        elif bad == "wrong-principal" and operation["kind"] != "azure-cli-account":
            response["principalId"] = str(uuid.uuid4())
        elif bad == "wrong-request-proof" and operation["kind"] != "azure-cli-account":
            response["provenance"]["requestUrl"] = "https://evil.example.invalid"
    result, _ = execute(case, change)
    assert result["identityId"] is None
    assert result["tenantMatches"] is False
    assert result["armDeploymentAllowed"] is False


@pytest.mark.parametrize("bad", ["data-actions-only", "not-actions", "permission-condition", "assignment-condition", "deny"])
def test_control_plane_permissions_exclusions_conditions_and_denies(case, bad):
    def change(operation, response):
        if operation["id"].startswith("permissions-"):
            if bad == "data-actions-only":
                response["body"]["value"] = [{"actions": [], "notActions": [], "dataActions": ["*"]}]
            elif bad == "not-actions":
                response["body"]["value"][0]["notActions"] = ["Microsoft.Resources/deployments/*", "Microsoft.SecurityInsights/*"]
            elif bad == "permission-condition":
                response["body"]["value"].append({"actions": ["*"], "notActions": [], "condition": "unknown"})
        if operation["id"].startswith("role-assignments-") and bad == "assignment-condition":
            response["body"]["value"] = [{"properties": {
                "scope": TARGET["workspaceResourceId"].split("/providers/")[0], "principalId": PRINCIPAL,
                "roleDefinitionId": "/providers/Microsoft.Authorization/roleDefinitions/" + str(uuid.uuid4()),
                "condition": "unknown", "conditionVersion": "2.0",
            }}]
        if operation["id"].startswith("denies-") and bad == "deny":
            response["body"]["value"] = [{"properties": {"permissions": [{"actions": ["*"]}]}}]
    result, _ = execute(case, change)
    assert result["armDeploymentAllowed"] is False


def test_not_actions_are_per_grant_not_global_denials(case):
    def change(operation, response):
        if operation["id"].startswith("permissions-"):
            response["body"]["value"] = [
                {"actions": ["*"], "notActions": ["Microsoft.SecurityInsights/*"]},
                {"actions": ["Microsoft.SecurityInsights/*"], "notActions": []},
            ]
    result, _ = execute(case, change)
    assert result["armDeploymentAllowed"] is True


@pytest.mark.parametrize("conditions", [
    {"condition": None, "conditionVersion": None},
    {"condition": "", "conditionVersion": ""},
    {"condition": None},
    {"conditionVersion": ""},
])
def test_nullable_rest_condition_fields_preserve_unconditional_grants(case, conditions):
    rg = TARGET["workspaceResourceId"].split("/providers/")[0]

    def change(operation, response):
        if operation["id"].startswith("permissions-"):
            response["body"]["value"][0].update(conditions)
        elif operation["id"].startswith("role-assignments-"):
            assignment_id = rg + "/providers/Microsoft.Authorization/roleAssignments/" + str(uuid.uuid4())
            response["body"]["value"] = [{
                "id": assignment_id, "type": "Microsoft.Authorization/roleAssignments",
                "properties": {
                    "scope": rg, "principalId": PRINCIPAL, "principalType": "User",
                    "roleDefinitionId": "/subscriptions/" + TARGET["subscriptionId"]
                    + "/providers/Microsoft.Authorization/roleDefinitions/" + str(uuid.uuid4()),
                    **conditions,
                },
            }]
    result, _ = execute(case, change)
    assert result["armDeploymentAllowed"] is True
    assert all(row["status"] == "verified" for row in result["checks"]["armDeploymentAllowed"]["roleAssignments"].values())


@pytest.mark.parametrize("conditions", [
    {"condition": "", "conditionVersion": "2.0"},
    {"condition": "@Resource[unknown]"},
    {"condition": []}, {"condition": False}, {"conditionVersion": 2},
])
@pytest.mark.parametrize("family", ["permissions-", "role-assignments-"])
def test_real_or_malformed_nullable_conditions_still_block(case, conditions, family):
    def change(operation, response):
        if not operation["id"].startswith(family):
            return
        if family == "permissions-":
            response["body"]["value"][0].update(conditions)
        else:
            response["body"]["value"] = [{"properties": {
                "scope": TARGET["workspaceResourceId"].split("/providers/")[0],
                "principalId": PRINCIPAL,
                "roleDefinitionId": "/providers/Microsoft.Authorization/roleDefinitions/" + str(uuid.uuid4()),
                **conditions,
            }}]
    result, _ = execute(case, change)
    assert result["armDeploymentAllowed"] is False


def test_nonempty_denies_are_conservatively_blocked_without_applicability_claim(case):
    def change(operation, response):
        if operation["id"].startswith("denies-"):
            response["body"]["value"] = [{"properties": {
                "scope": TARGET["workspaceResourceId"],
                "doNotApplyToChildScopes": True,
                "principals": [{"id": PRINCIPAL, "type": "User"}],
                "excludePrincipals": [{"id": PRINCIPAL, "type": "User"}],
                "permissions": [{"actions": ["*"], "notActions": []}],
            }}]
    result, _ = execute(case, change)
    assert result["armDeploymentAllowed"] is False
    for check in result["checks"]["armDeploymentAllowed"]["denies"].values():
        assert check["status"] == "unknown"
        assert check["applicabilityEvaluated"] is False
        assert check["policy"] == "require-complete-empty-ancestor-deny-list"


def test_absent_imports_have_no_extension_blocker_in_ready_result(case):
    current = template()
    current["resources"] = [current["resources"][2]]
    case["path"].write_text(json.dumps(current))
    arm = copy.deepcopy(case["arm"])
    arm["mainTemplateSha256"] = hashlib.sha256(case["path"].read_bytes()).hexdigest()
    arm["candidateSha256"] = _canonical_sha256({"metadataOnly": arm["mainTemplateSha256"]})
    arm["selectedFlags"]["DeployDefenderWorkbook"] = False
    arm["parameters"]["DeployDefenderWorkbook"] = False
    arm["resources"] = validation._resource_inventory(current, arm["parameters"], arm["target"])
    arm["expectedWorkbooks"] = []
    arm["resourceCount"] = len(arm["resources"])
    arm["scope"]["contentTypes"] = []
    arm["scope"]["resourceTypes"] = sorted({row["type"] for row in arm["resources"]} | {"Microsoft.Resources/deployments"})
    seal(arm, "planSha256")
    case["plan"] = preflight.plan_arm_preflight(arm)
    case["consent"] = preflight.review_arm_preflight(case["plan"], "reviewer", "metadata-only", True)
    result, _ = execute(case)
    assert result["status"] == "ready"
    assert result["extensionResourceWriteAllowed"] is False
    assert result["checks"]["extensionResourceWriteAllowed"]["status"] == "not-required"
    assert result["checks"]["extensionResourceWriteAllowed"]["writeAccessVerified"] is False
    assert result["reasons"] == []


@pytest.mark.parametrize("bad", ["wrong-id", "foreign-package", "wrong-content", "404", "ambiguous-registration", "foreign-registration", "wrong-registration-content", "malformed-registration"])
def test_exact_managed_identity_ownership_boundaries(case, bad):
    def change(operation, response):
        if operation["kind"] == "graph-get":
            if bad == "wrong-id":
                response["body"]["id"] = str(uuid.uuid4())
            elif bad == "foreign-package":
                response["body"]["content"]["contentProvenance"]["packageId"] = "foreign.publisher"
            elif bad == "wrong-content":
                response["body"]["content"]["contentProvenance"]["contentId"] = str(uuid.uuid4())
            elif bad == "404":
                response.update(statusCode=404, body={})
        if operation["id"] == "registrations-contentTemplates":
            if bad == "ambiguous-registration":
                response["body"]["value"].append(copy.deepcopy(response["body"]["value"][0]))
            elif bad == "foreign-registration":
                response["body"]["value"][0]["properties"]["packageId"] = "foreign.publisher"
            elif bad == "wrong-registration-content":
                response["body"]["value"][0]["properties"]["contentId"] = str(uuid.uuid4())
            elif bad == "malformed-registration":
                response["body"]["value"] = [{}]
    result, _ = execute(case, change)
    assert result["ownershipVerified"] is False


def test_intended_same_id_upsert_allows_old_or_edited_content_and_surfaces_change(case):
    def change(operation, response):
        if operation["kind"] == "graph-get":
            response["body"]["content"]["items"] = [{"edited": True}]
            response["body"]["content"]["contentProvenance"].update(packageVersion="1.0.0", contentVersion="1.0.0")
        if operation["id"] == "registrations-contentTemplates":
            response["body"]["value"][0]["properties"].update(version="1.0.0", mainTemplate={"old": "edited"})
    result, _ = execute(case, change)
    assert result["ownershipVerified"] is True
    updates = result["checks"]["ownershipVerified"]["managedUpdates"]
    assert any(row.get("instanceId") == INSTANCE and row["contentChanged"] for row in updates)
    assert all(row["policy"] == "managed-same-id-upsert" for row in updates)
    assert result["extensionResourceWriteAllowed"] is False


@pytest.mark.parametrize("tag", [None, {"environment": "production"}, {"arbitrary": "lab"}, {"Environment": "dev", "env": "production"}])
def test_only_existing_recognized_exact_scope_environment_tag_is_nonproduction(case, tag):
    def change(operation, response):
        if operation["id"] == "resource-group":
            response["body"]["tags"] = tag
    result, _ = execute(case, change)
    assert result["nonProduction"] is False


def test_resealed_operation_forgery_and_template_staleness_block_dispatch(case):
    forged = copy.deepcopy(case["plan"])
    forged["operations"][1]["url"] = "https://evil.example.invalid"
    seal(forged, "preflightPlanSha256")
    with pytest.raises(ValueError, match="reconstruct"):
        preflight.review_arm_preflight(forged, "reviewer", "no", True)
    current = json.loads(case["path"].read_text())
    current["resources"][0]["properties"]["template"]["resources"]["workbook"]["properties"]["name"] = "Changed"
    case["path"].write_text(json.dumps(current))
    with pytest.raises(ValueError, match="current template"):
        preflight.execute_arm_preflight(case["plan"], read_consent=lambda: case["consent"], reader=lambda _: pytest.fail("dispatch"))
    result = preflight.assess_arm_preflight(case["plan"], {})
    assert result["disabledContentVerified"] is False


def test_unique_string_name_uses_complete_canonical_registration_not_approximation(case):
    current = template()
    current["resources"][1]["name"] = "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/', uniqueString('fixture'))]"
    case["path"].write_text(json.dumps(current))
    arm = copy.deepcopy(case["arm"])
    arm["mainTemplateSha256"] = hashlib.sha256(case["path"].read_bytes()).hexdigest()
    arm["resources"] = validation._resource_inventory(current, arm["parameters"], arm["target"])
    seal(arm, "planSha256")
    case["plan"] = preflight.plan_arm_preflight(arm)
    case["consent"] = preflight.review_arm_preflight(case["plan"], "reviewer", "unique-name", True)
    result, calls = execute(case)
    assert result["ownershipVerified"] is True
    assert all("uniqueString" not in operation.get("url", "") for operation in calls)


def test_other_resource_families_are_not_promised_ready(case):
    current = template()
    current["resources"].append({
        "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
        "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/disabled-rule')]",
        "properties": {"enabled": False},
    })
    case["path"].write_text(json.dumps(current))
    arm = copy.deepcopy(case["arm"])
    arm["mainTemplateSha256"] = hashlib.sha256(case["path"].read_bytes()).hexdigest()
    arm["resources"] = validation._resource_inventory(current, arm["parameters"], arm["target"])
    arm["resourceCount"] = len(arm["resources"])
    arm["scope"]["resourceTypes"] = sorted({row["type"] for row in arm["resources"]} | {"Microsoft.Resources/deployments"})
    seal(arm, "planSha256")
    case["plan"] = preflight.plan_arm_preflight(arm)
    case["consent"] = preflight.review_arm_preflight(case["plan"], "reviewer", "non-workbook", True)
    result, _ = execute(case)
    assert result["disabledContentVerified"] is True
    assert result["ownershipVerified"] is False
    assert result["armDeploymentAllowed"] is False
    assert "non-workbook resource families" in result["checks"]["ownershipVerified"]["reasons"][0]


def test_forged_disabled_inventory_is_not_evidence(case):
    current = template()
    current["resources"][0]["properties"]["template"]["resources"]["workbook"]["type"] = "Microsoft.Security/detectionRules@2026-06-01-preview"
    current["resources"][0]["properties"]["template"]["resources"]["workbook"]["properties"]["isEnabled"] = True
    case["path"].write_text(json.dumps(current))
    arm = copy.deepcopy(case["arm"])
    arm["mainTemplateSha256"] = hashlib.sha256(case["path"].read_bytes()).hexdigest()
    arm["disabledContentVerified"] = True
    seal(arm, "planSha256")
    with pytest.raises(ValueError, match="disabled content"):
        preflight.plan_arm_preflight(arm)


def test_assessment_rejects_copied_flags_instead_of_observations(case):
    result = preflight.assess_arm_preflight(case["plan"], {
        **{key: True for key in preflight._ACCESS_FLAGS},
        "identityId": PRINCIPAL, "target": TARGET,
    })
    assert result["identityId"] is None
    assert result["ownershipVerified"] is False
    assert result["extensionResourceWriteAllowed"] is False
    assert result["status"] == "blocked"


def test_observation_target_or_candidate_change_and_duplicate_responses_block(case):
    result, _ = execute(case)
    observations = copy.deepcopy(result["observations"])
    observations["candidateSha256"] = "0" * 64
    assert preflight.assess_arm_preflight(case["plan"], observations)["ownershipVerified"] is False
    observations = copy.deepcopy(result["observations"])
    observations["responses"].append(copy.deepcopy(observations["responses"][0]))
    assert preflight.assess_arm_preflight(case["plan"], observations)["ownershipVerified"] is False


def test_response_size_bound_and_reader_cannot_assert_access(case, monkeypatch):
    monkeypatch.setattr(preflight, "MAX_RESPONSE_BYTES", 400)
    case["plan"] = preflight.plan_arm_preflight(case["arm"])
    case["consent"] = preflight.review_arm_preflight(case["plan"], "reviewer", "bounded", True)
    def change(operation, response):
        response["extensionResourceWriteAllowed"] = True
        response["body"]["accessToken"] = "never-persist"
        response["body"]["oversized"] = "x" * 500
    result, calls = execute(case, change)
    assert len(calls) == 1
    assert result["extensionResourceWriteAllowed"] is False
    assert "never-persist" not in json.dumps(result)


def test_operation_and_collection_bounds_fail_closed(case, monkeypatch):
    monkeypatch.setattr(preflight, "MAX_OPERATIONS", 2)
    with pytest.raises(ValueError, match="operation count"):
        preflight.plan_arm_preflight(case["arm"])
    monkeypatch.setattr(preflight, "MAX_OPERATIONS", 64)
    monkeypatch.setattr(preflight, "MAX_LIST_ITEMS", 0)
    case["plan"] = preflight.plan_arm_preflight(case["arm"])
    case["consent"] = preflight.review_arm_preflight(case["plan"], "reviewer", "list-bounds", True)
    result, _ = execute(case)
    assert result["armDeploymentAllowed"] is False
    assert result["ownershipVerified"] is False


def test_secret_fields_are_redacted_and_extra_reader_flags_ignored(case):
    def change(operation, response):
        response["extensionResourceWriteAllowed"] = True
        response["accessToken"] = "secret-top-level"
        response["body"]["accessToken"] = "secret-body"
        response["body"]["client_secret"] = "secret-client"
    result, _ = execute(case, change)
    assert "secret-top-level" not in json.dumps(result)
    assert "secret-body" not in json.dumps(result)
    assert "secret-client" not in json.dumps(result)
    assert result["extensionResourceWriteAllowed"] is False


def test_provenance_and_consent_checks_cannot_be_replaced_with_asserted_flags(case):
    result, _ = execute(case)
    observations = copy.deepcopy(result["observations"])
    for row in observations["responses"]:
        row.pop("provenance", None)
    assessed = preflight.assess_arm_preflight(case["plan"], observations)
    assert assessed["identityId"] is None
    observations = copy.deepcopy(result["observations"])
    observations["consentChecks"] = [{"status": "ready", "reasons": []}] * len(observations["consentChecks"])
    assessed = preflight.assess_arm_preflight(case["plan"], observations)
    assert assessed["nonProduction"] is False
    assert assessed["checks"]["readConsentVerified"]["status"] == "blocked"


def test_module_import_does_not_authenticate_or_dispatch_network():
    script = """
import platform, socket, subprocess, urllib.request
platform.platform = lambda: "offline-fixture"
def forbidden(*args, **kwargs):
    raise AssertionError("import attempted authentication/network/CLI")
socket.socket.connect = forbidden
urllib.request.urlopen = forbidden
subprocess.run = forbidden
import azure.identity
azure.identity.DefaultAzureCredential = forbidden
import sentinel_xdr_migration.workbook_preflight
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
