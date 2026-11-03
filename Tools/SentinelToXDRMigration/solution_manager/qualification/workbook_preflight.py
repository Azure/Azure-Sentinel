"""Consent-bound candidate metadata reads, never authentication or cloud writes.

The injected reader must honor each operation's timeout and retry limits. Read
consent permits only scoped ARM token acquisition/refresh with an already cached
identity, never sign-in, new credentials, permission grants or Graph/AH tokens.
The reader attests request/principal provenance, not access booleans. Nonempty
deny lists conservatively block; their applicability is not evaluated. Seals
bind evidence, not signatures or a substitute for a trusted reader.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from solution_manager.qualification.arm_acceptance_support import _canonical_sha256
from solution_manager.core.content_paths import content_path
from solution_manager.core.target_context import workspace_identity
from solution_manager.authoring.workbook_validation import (
    _expected_workbook_contracts,
    _FLAG_KINDS,
    _resource_inventory,
    _resolve,
    _sealed,
    _target,
)

ARM_BASE = "https://management.azure.com"
ARM_SCOPE = ARM_BASE + "/.default"
GRAPH_BASE = "https://graph.microsoft.com"
WORKSPACE_API_VERSION = "2023-09-01"  # Existing target_context workspace reads.
RESOURCE_GROUP_API_VERSION = "2021-04-01"
PERMISSIONS_API_VERSION = "2022-04-01"  # dcr_readiness control-plane API.
DENY_API_VERSION = "2022-04-01"  # List-for-scope atScope() includes ancestors.
CONTENT_API_VERSION = "2025-09-01"  # Verified current Content Hub read/list contract.
MAX_OPERATIONS = 64
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
MAX_TEMPLATE_BYTES = 16 * 1024 * 1024
MAX_LIST_ITEMS = 5000
TIMEOUT_SECONDS = 15
_HASH = re.compile(r"^[a-f0-9]{64}$")
_REGISTRATION_TYPES = {
    "microsoft.operationalinsights/workspaces/providers/contenttemplates": "contentTemplates",
    "microsoft.operationalinsights/workspaces/providers/contentpackages": "contentPackages",
}
_ACCESS_FLAGS = (
    "tenantMatches", "subscriptionMatches", "workspaceMatches", "nonProduction",
    "armDeploymentAllowed", "disabledContentVerified", "ownershipVerified",
    "extensionResourceWriteAllowed",
)
_REDACTED_KEYS = {
    "authorization", "accesstoken", "refreshtoken", "token", "secret",
    "clientsecret", "password", "cookie", "setcookie",
}
_PRINCIPAL_CONTRACT = {
    "source": "authenticated-arm-token",
    "audiences": [
        ARM_BASE, ARM_BASE + "/",
        "https://management.core.windows.net", "https://management.core.windows.net/",
    ],
    "currentExpiryRequired": True, "sameArmTokenPrincipalRequired": True,
    "accountUserNameIsPrincipalProof": False, "graphReadProvesExtensionWriteIdentity": False,
}
_FORBIDDEN_AUTHORIZATIONS = (
    "writesAuthorized", "signInAuthorized", "interactiveSignInAuthorized",
    "newCredentialsAuthorized", "permissionGrantsAuthorized",
    "graphTokenAcquisitionAuthorized", "graphTokenReuseAuthorized",
    "advancedHuntingCredentialReuseAuthorized",
)
_READ_FAILURES = (ValueError, RuntimeError, OSError, KeyError, TypeError)


def _arm_token_access(target: dict) -> dict:
    return {
        "scope": ARM_SCOPE, "tenantId": target["tenantId"], "subscriptionId": target["subscriptionId"],
        "existingCachedIdentityOnly": True, "acquisitionAuthorized": True, "refreshAuthorized": True,
        "interactiveSignInAuthorized": False, "newCredentialsAuthorized": False,
        "permissionGrantsAuthorized": False, "graphTokenAcquisitionAuthorized": False,
        "graphTokenReuseAuthorized": False,
        "advancedHuntingCredentialReuseAuthorized": False,
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _guid(value: Any) -> bool:
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value.lower()
    except (ValueError, AttributeError):
        return False


def _same(left: Any, right: Any) -> bool:
    return isinstance(left, str) and isinstance(right, str) and left.casefold() == right.casefold()


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, allow_nan=False))


def _sanitize(value: Any, *, depth: int = 0) -> Any:
    if depth > 50:
        return "[redacted: depth limit]"
    if isinstance(value, dict):
        return {
            key: "[redacted]" if key.casefold().replace("_", "").replace("-", "") in _REDACTED_KEYS
            else _sanitize(item, depth=depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_sanitize(item, depth=depth + 1) for item in value]
    if isinstance(value, str):
        value = re.sub(r"(?i)\bBearer\s+\S+", "Bearer [redacted]", value)
        value = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "[redacted-token]", value)
        return value
    return value


def _resource_at(template: dict[str, Any], path: str) -> dict[str, Any]:
    current: Any = template
    for part in path.strip("/").split("/"):
        current = current[int(part)] if isinstance(current, list) else current[part]
    if not isinstance(current, dict):
        raise ValueError("resource inventory path does not identify a resource")
    return current


def _inspect(arm_plan: dict[str, Any]) -> dict[str, Any]:
    """Re-run the actual fail-closed planner against current template bytes."""
    if not isinstance(arm_plan, dict) or not _sealed(arm_plan, "planSha256"):
        raise ValueError("candidate ARM plan seal is missing or stale")
    if arm_plan.get("status") != "ready" or arm_plan.get("workbookCapabilityVersion") != 1:
        raise ValueError("preflight requires a versioned ready candidate ARM plan")
    if not _HASH.fullmatch(str(arm_plan.get("candidateSha256", ""))):
        raise ValueError("candidate binding is missing")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", str(arm_plan.get("runId", ""))):
        raise ValueError("run identity is unsafe")
    target = _target(arm_plan["target"])
    parameters, flags = arm_plan["parameters"], arm_plan["selectedFlags"]
    if not isinstance(parameters, dict) or not isinstance(flags, dict):
        raise ValueError("candidate parameters or content selection are malformed")
    path = content_path(Path(arm_plan["solutionPath"]), arm_plan["artifactPaths"]["mainTemplate"])
    if path.stat().st_size > MAX_TEMPLATE_BYTES:
        raise ValueError("candidate template exceeds bounded inspection size")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != arm_plan.get("mainTemplateSha256"):
        raise ValueError("current template does not match candidate")
    template = json.loads(raw.decode("utf-8-sig"))
    definitions = template.get("parameters", {})
    declared = {key for key in definitions if key.startswith("Deploy")}
    if set(flags) != declared or declared - set(_FLAG_KINDS) or any(
        type(value) is not bool or parameters.get(key) is not value
        or not isinstance(definitions[key], dict) or definitions[key].get("type") != "bool"
        for key, value in flags.items()
    ):
        raise ValueError("candidate selection cannot be reconstructed")
    if parameters.get("workspace") != workspace_identity(target["workspaceResourceId"])["workspaceName"]:
        raise ValueError("candidate workspace parameter differs from selected target")
    inventory = _resource_inventory(template, parameters, target)
    contracts = _expected_workbook_contracts(template, flags.get("DeployDefenderWorkbook") is True)
    if inventory != arm_plan.get("resources") or contracts != arm_plan.get("expectedWorkbooks"):
        raise ValueError("candidate inventory or workbook contract differs from current template")
    if arm_plan.get("resourceCount") != len(inventory):
        raise ValueError("candidate resource count is stale")
    scope = arm_plan.get("scope", {})
    expected_types = sorted({item["type"] for item in inventory} | {"Microsoft.Resources/deployments"})
    if scope.get("lab") != target or scope.get("resourceTypes") != expected_types:
        raise ValueError("candidate scope is not bound to current inventory")
    if scope.get("contentTypes") != sorted({_FLAG_KINDS[key] for key, selected in flags.items() if selected}):
        raise ValueError("candidate content scope differs from exact selections")
    registrations, unsupported = [], []
    for row in inventory:
        kind = row["type"].casefold()
        if kind in _REGISTRATION_TYPES:
            resource = _resource_at(template, row["path"])
            identities = {}
            for field in ("contentId", "packageId", "contentKind"):
                try:
                    identities[field] = _resolve(resource.get("properties", {}).get(field), template, parameters, target)
                except ValueError:
                    identities[field] = None
            try:
                resolved_name = _resolve(row["name"], template, parameters, target)
            except ValueError:
                resolved_name = None
            registrations.append({
                "family": _REGISTRATION_TYPES[kind],
                "properties": resource.get("properties", {}),
                "name": row["name"], "resolvedName": resolved_name, "identity": identities,
            })
        elif kind not in {"microsoft.resources/deployments", "microsoft.security/workbooks"}:
            unsupported.append(row["type"])
    return {
        "inventory": inventory, "expectedWorkbooks": contracts,
        "registrations": registrations, "unsupportedOwnershipTypes": sorted(set(unsupported)),
    }


def _make_plan(arm_plan: dict[str, Any], inspection: dict[str, Any]) -> dict[str, Any]:
    target = _target(arm_plan["target"])
    workspace = target["workspaceResourceId"]
    rg = f"/subscriptions/{target['subscriptionId']}/resourceGroups/{target['resourceGroup']}"
    operations = [{
        "id": "account", "kind": "azure-cli-account", "method": "LOCAL",
        "subscriptionId": target["subscriptionId"], "timeoutSeconds": TIMEOUT_SECONDS, "retryCount": 0,
    }]

    def get(identifier: str, kind: str, url: str) -> None:
        operations.append({
            "id": identifier, "kind": kind, "method": "GET", "url": url,
            "timeoutSeconds": TIMEOUT_SECONDS, "retryCount": 0,
        })

    def arm(identifier: str, resource: str, version: str, suffix: str = "") -> None:
        get(identifier, "arm-get", f"{ARM_BASE}{quote(resource, safe='/')}?api-version={version}{suffix}")

    arm("workspace", workspace, WORKSPACE_API_VERSION)
    arm("resource-group", rg, RESOURCE_GROUP_API_VERSION)
    for identifier, scope in (("rg", rg), ("workspace", workspace)):
        arm(f"permissions-{identifier}", scope + "/providers/Microsoft.Authorization/permissions", PERMISSIONS_API_VERSION)
        arm(f"role-assignments-{identifier}", scope + "/providers/Microsoft.Authorization/roleAssignments",
            PERMISSIONS_API_VERSION, "&$filter=atScope()")
        arm(f"denies-{identifier}", scope + "/providers/Microsoft.Authorization/denyAssignments",
            DENY_API_VERSION, "&$filter=atScope()")
    for family in ("contentPackages", "contentTemplates"):
        arm(f"registrations-{family}", workspace + "/providers/Microsoft.SecurityInsights/" + family,
            CONTENT_API_VERSION)
    for workbook in sorted(inspection["expectedWorkbooks"], key=lambda row: row["instanceId"]):
        iid = workbook["instanceId"]
        if not _guid(iid):
            raise ValueError("selected workbook instance identity is malformed")
        get("workbook-" + iid, "graph-get", f"{GRAPH_BASE}/beta/security/workbooks/{iid}")
    if len(operations) > MAX_OPERATIONS:
        raise ValueError("candidate exceeds bounded preflight operation count")
    binding = {key: arm_plan[key] for key in ("runId", "candidateSha256", "mainTemplateSha256", "target")}
    binding["armPlanSha256"] = arm_plan["planSha256"]
    prefix = arm_plan["planSha256"]
    token_access = _arm_token_access(target)
    authorization = {
        "readOnly": True, "tokenAcquisitionAuthorized": True,
        **{key: False for key in _FORBIDDEN_AUTHORIZATIONS},
        "armTokenAccess": token_access,
    }
    read_scope = {
        "purpose": "candidate-arm-read-preflight", "runId": arm_plan["runId"], "target": target,
        "operations": operations,
        "principalContract": {**_copy(_PRINCIPAL_CONTRACT), "armTokenAccess": _copy(token_access)},
        **authorization,
    }
    plan = {
        "schemaVersion": 1, "purpose": "candidate-arm-read-preflight",
        **binding, "armPlan": _copy(arm_plan), "operations": operations,
        "inspectionSha256": _canonical_sha256(inspection),
        **authorization, "paginationPolicy": "reject-next-link",
        "readScope": read_scope, "preflightScopeSha256": _canonical_sha256(read_scope),
        "maxOperations": MAX_OPERATIONS, "maxResponseBytes": MAX_RESPONSE_BYTES,
        "maxListItems": MAX_LIST_ITEMS,
        "artifacts": {
            "plan": "arm-preflight-plan.json", "consent": "arm-preflight-consent.json",
            "observations": f"arm-preflight-observations-{prefix}.json",
            "result": f"arm-preflight-result-{prefix}.json",
        },
    }
    plan["preflightPlanSha256"] = _canonical_sha256(plan)
    return plan


def plan_arm_preflight(arm_plan: dict) -> dict:
    """Inspect local candidate bytes and seal a bounded exact metadata read list."""
    try:
        arm_plan = _copy(arm_plan)
        return _make_plan(arm_plan, _inspect(arm_plan))
    except (KeyError, TypeError, AttributeError, IndexError, OSError, RecursionError) as exc:
        raise ValueError(f"candidate preflight plan cannot be reconstructed ({type(exc).__name__})") from exc


def _validate(plan: dict) -> None:
    if not isinstance(plan, dict) or not _sealed(plan, "preflightPlanSha256"):
        raise ValueError("preflight plan seal is missing or stale")
    if plan != plan_arm_preflight(plan["armPlan"]):
        raise ValueError("preflight plan does not reconstruct from current candidate")


def _binding(plan: dict) -> dict:
    return {key: plan[key] for key in (
        "preflightPlanSha256", "preflightScopeSha256", "armPlanSha256", "candidateSha256",
        "mainTemplateSha256", "runId", "target",
    )}


def review_arm_preflight(plan: dict, actor: str, reference: str, approved: bool) -> dict:
    _validate(plan)
    if not isinstance(actor, str) or not actor.strip() or not isinstance(reference, str) or not reference.strip() or type(approved) is not bool:
        raise ValueError("read review requires actor, reference and an explicit boolean decision")
    consent = {
        "schemaVersion": 1, "consentPolicyVersion": 1, **_binding(plan),
        "readScope": _copy(plan["readScope"]), "reviewedPreflightPlanSha256": plan["preflightPlanSha256"],
        "operations": _copy(plan["operations"]), "status": "approved" if approved else "declined",
        "actor": actor.strip(), "reference": reference.strip(), "recordedAt": _now(),
        "revoked": False, "readOnly": True, "tokenAcquisitionAuthorized": True,
        **{key: False for key in _FORBIDDEN_AUTHORIZATIONS},
        "armTokenAccess": _copy(plan["armTokenAccess"]),
    }
    consent["consentSha256"] = _canonical_sha256(consent)
    return consent


def revoke_arm_preflight(consent: dict, actor: str, reference: str) -> dict:
    if not isinstance(consent, dict) or not _sealed(consent, "consentSha256"):
        raise ValueError("read consent seal is missing or stale")
    if not isinstance(actor, str) or not actor.strip() or not isinstance(reference, str) or not reference.strip():
        raise ValueError("revocation requires actor and reference")
    result = _copy(consent)
    result.pop("consentSha256")
    result.update(status="revoked", revoked=True, revocationActor=actor.strip(),
                  revocationReference=reference.strip(), revokedAt=_now())
    result["consentSha256"] = _canonical_sha256(result)
    return result


def _check_consent(plan: dict, consent: Any) -> dict:
    reasons = []
    try:
        _validate(plan)
        if not isinstance(consent, dict) or not _sealed(consent, "consentSha256"):
            raise ValueError("read consent is missing or stale")
        if consent.get("status") != "approved" or consent.get("revoked") is not False:
            raise ValueError("read consent is declined or revoked")
        if any(consent.get(key) != plan[key] for key in ("preflightScopeSha256", "runId", "target")) or consent.get("readScope") != plan["readScope"]:
            raise ValueError("read consent belongs to another exact metadata scope, principal contract, run or target")
        if consent.get("operations") != plan["operations"]:
            raise ValueError("read consent operation scope differs")
        if consent.get("schemaVersion") != 1 or consent.get("consentPolicyVersion") != 1 or consent.get("readOnly") is not True or (
            consent.get("tokenAcquisitionAuthorized") is not True or consent.get("armTokenAccess") != plan["armTokenAccess"]
        ) or any(
            consent.get(key) is not False for key in _FORBIDDEN_AUTHORIZATIONS
        ) or not consent.get("actor") or not consent.get("reference"):
            raise ValueError("read-only consent boundary is invalid")
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
        reasons.append(str(exc) if isinstance(exc, ValueError) else type(exc).__name__)
    return {"status": "ready" if not reasons else "blocked", "reasons": reasons}


def _normalize_response(operation: dict, response: Any, elapsed: float) -> dict:
    result = {"operation": _copy(operation), "operationSha256": _canonical_sha256(operation)}
    if elapsed > operation["timeoutSeconds"]:
        return {**result, "status": "unknown", "reason": "reader exceeded bounded timeout"}
    try:
        if not isinstance(response, dict) or type(response.get("statusCode")) is not int or not isinstance(response.get("body"), dict):
            raise ValueError("reader returned malformed status/body")
        encoded = json.dumps(response, allow_nan=False).encode()
        if len(encoded) > MAX_RESPONSE_BYTES:
            raise ValueError("response exceeds bounded evidence size")
        sanitized = _sanitize(_copy({key: response[key] for key in (
            "statusCode", "body", "principalId", "tenantId", "provenance",
        ) if key in response}))
        if operation["kind"] != "azure-cli-account" and "provenance" not in sanitized:
            sanitized["provenance"] = {
                "requestUrl": operation["url"], "method": operation["method"],
                "source": "consent-bound-reader-dispatch",
                "principalId": sanitized.get("principalId"), "tenantId": sanitized.get("tenantId"),
            }
        if response["statusCode"] != 200:
            return {**result, **sanitized, "status": "blocked" if response["statusCode"] in {401, 403} else "unknown",
                    "reason": f"metadata read HTTP {response['statusCode']}; not success or proven absence"}
        if response["body"].get("nextLink") not in (None, "") or response["body"].get("@odata.nextLink") not in (None, ""):
            raise ValueError("paginated response is incomplete; nextLink is not followed")
        return {**result, **sanitized, "operation": _copy(operation),
                "operationSha256": _canonical_sha256(operation), "status": "observed"}
    except (ValueError, TypeError, RecursionError):
        return {**result, "status": "unknown", "reason": "malformed, oversized or paginated metadata response"}


def execute_arm_preflight(plan: dict, *, read_consent: Callable[[], dict], reader: Callable[[dict], dict]) -> dict:
    """Dispatch only exact reviewed reads; no default reader or credential creation."""
    _validate(plan)
    current = copy.deepcopy(plan)
    observations = {**_binding(current), "responses": [], "consentChecks": [], "readAttempted": False}

    def consent_check() -> dict:
        try:
            consent = read_consent()
            check = {**_check_consent(current, consent), "consent": _copy(consent)}
            _validate(plan)
            if plan != current:
                raise ValueError("preflight plan mutated during execution")
        except _READ_FAILURES as exc:
            check = {"status": "blocked", "reasons": [f"current read consent/plan unavailable ({type(exc).__name__})"]}
        observations["consentChecks"].append(check)
        return check

    for operation in current["operations"]:
        if consent_check()["status"] != "ready":
            break
        observations["readAttempted"] = True
        started = time.monotonic()
        try:
            response = reader(_copy(operation))
            normalized = _normalize_response(operation, response, time.monotonic() - started)
        except _READ_FAILURES as exc:
            normalized = {"operation": _copy(operation), "operationSha256": _canonical_sha256(operation),
                          "status": "unknown", "reason": f"metadata reader failed ({type(exc).__name__})"}
        observations["responses"].append(normalized)
        if consent_check()["status"] != "ready":
            normalized.update(status="blocked", reason="read consent/plan changed after dispatch; evidence unusable")
            break
        if normalized["status"] != "observed":
            break
    result = assess_arm_preflight(current, observations)
    return {**result, "observations": observations, "readAttempted": observations["readAttempted"],
            "writeAttempted": False}


def _expiry(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError("invalid token expiry")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("token expiry requires timezone")
        return parsed.timestamp()
    raise ValueError("invalid token expiry")


def _principal(account: dict) -> dict | None:
    principal = account.get("principal")
    if not isinstance(principal, dict) or not _guid(principal.get("objectId")) or not _guid(principal.get("tenantId")):
        return None
    if principal.get("source") != _PRINCIPAL_CONTRACT["source"] or principal.get("audience") not in _PRINCIPAL_CONTRACT["audiences"]:
        return None
    try:
        if _expiry(principal.get("expiresOn")) <= time.time():
            return None
    except (ValueError, OverflowError):
        return None
    return principal


def _trusted_response(row: Any, operation: dict, principal: dict | None) -> bool:
    if not isinstance(row, dict) or row.get("operation") != operation or row.get("operationSha256") != _canonical_sha256(operation):
        return False
    normalized = _normalize_response(operation, row, 0)
    if row.get("status") != "observed" or normalized.get("status") != "observed":
        return False
    body = row["body"]
    if operation["kind"] == "azure-cli-account":
        return _guid(body.get("id")) and _guid(body.get("tenantId")) and _principal(body) is not None
    identifier = operation["id"]
    if identifier == "workspace" and not (
        isinstance(body.get("id"), str) and isinstance(body.get("properties"), dict)
        and _guid(body["properties"].get("customerId"))
    ):
        return False
    if identifier == "resource-group" and not isinstance(body.get("id"), str):
        return False
    if identifier.startswith(("permissions-", "role-assignments-", "denies-", "registrations-")) and _collection(body) is None:
        return False
    if identifier.startswith("workbook-") and not (isinstance(body.get("id"), str) and isinstance(body.get("content"), dict)):
        return False
    proof = row.get("provenance")
    source = "authenticated-arm-token" if operation["kind"] == "arm-get" else "authenticated-graph-token"
    return bool(principal and isinstance(proof, dict) and proof.get("requestUrl") == operation["url"]
                and proof.get("method") == "GET" and proof.get("source") in {source, "consent-bound-reader-dispatch"}
                and _same(proof.get("principalId"), principal["objectId"])
                and _same(proof.get("tenantId"), principal["tenantId"])
                and _same(row.get("principalId"), principal["objectId"])
                and _same(row.get("tenantId"), principal["tenantId"]))


def _collection(body: dict | None) -> list[dict] | None:
    if not isinstance(body, dict):
        return None
    rows = body.get("value")
    if not isinstance(rows, list) or len(rows) > MAX_LIST_ITEMS or any(not isinstance(row, dict) for row in rows):
        return None
    return rows


def _unconditional(value: dict) -> bool:
    return all(
        value.get(key) is None or (isinstance(value.get(key), str) and value[key] == "")
        for key in ("condition", "conditionVersion")
    )


def _permissions(rows: list[dict] | None, action: str) -> dict:
    if rows is None:
        return {"status": "unknown", "reason": "complete effective permissions are unavailable"}
    projected = []
    for row in rows:
        if not _unconditional(row):
            return {"status": "unknown", "reason": "control-plane grant conditions cannot be evaluated"}
        if any(not isinstance(row.get(key), list) or any(not isinstance(item, str) for item in row[key])
               for key in ("actions", "notActions")):
            return {"status": "unknown", "reason": "malformed control-plane actions/notActions"}
        projected.append({key: row[key] for key in ("actions", "notActions")})
    from solution_manager.qualification.dcr_readiness import _action_permission
    return _action_permission(projected, action)


def assess_arm_preflight(plan: dict, observations: dict) -> dict:
    """Evaluate independently observed metadata, retaining explicit unknown blockers."""
    access = {key: False for key in _ACCESS_FLAGS}
    access.update(identityId=None, tenantId=None, subscriptionId=None, workspaceResourceId=None)
    checks: dict[str, dict] = {}

    def check(name: str, passed: bool, reason: str, **details: Any) -> None:
        checks[name] = {"status": "verified" if passed else "blocked", "reasons": [] if passed else [reason], **details}
        if name in access:
            access[name] = passed

    try:
        observations = _copy(observations)
    except (ValueError, TypeError, RecursionError):
        observations = {}
    try:
        _validate(plan)
        inspection = _inspect(plan["armPlan"])
        check("disabledContentVerified", True, "")
    except (ValueError, KeyError, TypeError, AttributeError, OSError, RecursionError) as exc:
        check("disabledContentVerified", False, f"fresh candidate inspection failed ({type(exc).__name__})")
        bindings = {key: plan.get(key) for key in (
            "target", "preflightPlanSha256", "preflightScopeSha256", "candidateSha256",
            "armPlanSha256", "mainTemplateSha256", "runId",
        )} if isinstance(plan, dict) else {"target": None, "preflightPlanSha256": None}
        return {"schemaVersion": 1, **bindings, "status": "blocked", **access, "checks": checks,
                "reasons": checks["disabledContentVerified"]["reasons"], "writeAttempted": False,
                "providerWriteContractVerified": False}
    binding_valid = isinstance(observations, dict) and all(observations.get(key) == value for key, value in _binding(plan).items())
    check("observationBinding", binding_valid, "observations are not bound to exact target/run/candidate/plan")
    raw_rows = observations.get("responses") if binding_valid else None
    if not isinstance(raw_rows, list) or len(raw_rows) > MAX_OPERATIONS:
        raw_rows = []
    by_id = {}
    for row in raw_rows:
        identifier = row.get("operation", {}).get("id") if isinstance(row, dict) and isinstance(row.get("operation"), dict) else None
        if identifier in by_id:
            check("observationBinding", False, "duplicate operation observations")
            by_id = {}
            break
        by_id[identifier] = row
    account_row = by_id.get("account", {})
    account = account_row.get("body", {}) if _trusted_response(account_row, plan["operations"][0], None) else {}
    principal = _principal(account)
    check("principalVerified", principal is not None, "verified current authenticated ARM principal proof is unavailable; account.user.name is insufficient")
    bodies = {}
    for operation in plan["operations"]:
        row = by_id.get(operation["id"])
        trusted = _trusted_response(row, operation, principal)
        check("read:" + operation["id"], trusted, "missing, partial, failed or unbound authenticated metadata response")
        if trusted:
            bodies[operation["id"]] = row["body"]
    principal_bound = principal is not None and any(
        operation["kind"] == "arm-get" and operation["id"] in bodies for operation in plan["operations"]
    )
    check("principalVerified", principal_bound, "authenticated ARM principal is not bound to any successful exact ARM observation")
    if principal_bound:
        access["identityId"], access["tenantId"] = principal["objectId"], principal["tenantId"]
    complete = len(raw_rows) == len(plan["operations"]) and all(
        checks["read:" + operation["id"]]["status"] == "verified" for operation in plan["operations"]
    )
    check("allRequiredReads", complete, "every exact planned metadata read requires complete authenticated evidence")
    consent_checks = observations.get("consentChecks") if binding_valid else None
    consent_current = (
        isinstance(consent_checks, list) and len(consent_checks) == 2 * len(plan["operations"])
        and all(isinstance(row, dict) and row.get("status") == "ready"
                and _check_consent(plan, row.get("consent"))["status"] == "ready" for row in consent_checks)
    )
    check("readConsentVerified", consent_current, "current consent checks before and after every required read are missing or blocked")
    target = plan["target"]
    check("tenantMatches", bool(principal_bound and _same(principal["tenantId"], target["tenantId"])
                               and _same(account.get("tenantId"), target["tenantId"])), "observed account/token tenant mismatches or is unavailable")
    subscription = account.get("id")
    if isinstance(subscription, str):
        access["subscriptionId"] = subscription
    check("subscriptionMatches", principal_bound and _same(subscription, target["subscriptionId"]), "observed ARM account subscription mismatches or is unavailable")
    workspace = bodies.get("workspace", {})
    observed_workspace = workspace.get("id")
    if isinstance(observed_workspace, str):
        access["workspaceResourceId"] = observed_workspace
    workspace_properties = workspace.get("properties")
    check("workspaceMatches", _same(observed_workspace, target["workspaceResourceId"])
          and isinstance(workspace_properties, dict) and _same(workspace_properties.get("customerId"), target["workspaceCustomerId"]),
          "fresh selected workspace resource/customer identity mismatches or is unavailable")
    rg_id = f"/subscriptions/{target['subscriptionId']}/resourceGroups/{target['resourceGroup']}"
    group = bodies.get("resource-group", {})
    tags = group.get("tags")
    ws_tags = workspace.get("tags") if isinstance(workspace, dict) else None
    environment = [(key, value) for key, value in tags.items()
                   if key.casefold() in {"environment", "env"} and isinstance(value, str)] if isinstance(tags, dict) else []
    if not environment and tags is None and isinstance(ws_tags, dict):
        environment = [
            (key, value)
            for key, value in ws_tags.items()
            if (
                (key.casefold() in {"environment", "env"} and isinstance(value, str))
                or (key.casefold() == "tenantorigin" and isinstance(value, str) and value.strip().casefold() == "ttp")
            )
        ]
    approved_environments = {"lab", "test", "testing", "dev", "development", "sandbox", "non-production", "nonproduction", "ttp"}
    lab = bool(environment and all(value.strip().casefold() in approved_environments for _, value in environment))
    check("nonProduction", lab and _same(group.get("id"), rg_id) and access["workspaceMatches"]
          and access["tenantMatches"] and access["subscriptionMatches"] and consent_current,
          "exact approved RG/workspace lacks consistent recognized existing non-production environment tags",
          scope="selected-resource-group-and-workspace-only", tenantNonProductionVerified=False,
          environmentTags=environment)
    action_checks = {}
    required = {"Microsoft.Resources/deployments/*": "rg"}
    for resource in inspection["inventory"]:
        family = _REGISTRATION_TYPES.get(resource["type"].casefold())
        if family:
            required[f"Microsoft.SecurityInsights/{family}/write"] = "workspace"
    for action, scope in required.items():
        action_checks[action] = _permissions(_collection(bodies.get("permissions-" + scope)), action)
    deny_checks = {}
    assignment_checks = {}
    for scope in ("rg", "workspace"):
        denies = _collection(bodies.get("denies-" + scope))
        deny_checks[scope] = {
            "status": "verified" if denies == [] else "unknown",
            "reason": "" if denies == [] else "deny applicability/conditions cannot be safely resolved from unavailable or nonempty assignments",
            "ancestorCoverage": "atScope(): selected scope and above",
            "applicabilityEvaluated": False, "policy": "require-complete-empty-ancestor-deny-list",
        }
        assignments = _collection(bodies.get("role-assignments-" + scope))
        selected_scope = rg_id if scope == "rg" else target["workspaceResourceId"]
        unconditioned = assignments is not None and all(
            isinstance(row.get("properties"), dict)
            and isinstance(row["properties"].get("scope"), str)
            and _guid(row["properties"].get("principalId"))
            and isinstance(row["properties"].get("roleDefinitionId"), str)
            and (selected_scope.casefold() == row["properties"]["scope"].casefold()
                 or selected_scope.casefold().startswith(row["properties"]["scope"].rstrip("/").casefold() + "/"))
            and _unconditional(row["properties"])
            for row in assignments
        )
        assignment_checks[scope] = {
            "status": "verified" if unconditioned else "unknown",
            "reason": "" if unconditioned else "role assignment conditions/applicability are unresolved; effective permissions alone cannot prove access",
        }
    arm_allowed = (all(row["status"] == "ready" for row in action_checks.values())
                   and all(row["status"] == "verified" for row in deny_checks.values())
                   and all(row["status"] == "verified" for row in assignment_checks.values())
                   and not inspection["unsupportedOwnershipTypes"]
                   and access["tenantMatches"] and access["subscriptionMatches"] and access["workspaceMatches"])
    check("armDeploymentAllowed", arm_allowed, "effective control-plane allow/exclusion or ancestor deny evidence is insufficient",
          actions=action_checks, denies=deny_checks, roleAssignments=assignment_checks,
          unsupportedResourceWrites=inspection["unsupportedOwnershipTypes"])
    managed_updates, ownership_reasons = [], []
    for workbook in inspection["expectedWorkbooks"]:
        installed = bodies.get("workbook-" + workbook["instanceId"])
        if not installed:
            ownership_reasons.append(f"{workbook['instanceId']}: no credible existing workbook evidence; Graph 404 absence contract is unverified")
            continue
        content = installed.get("content")
        provenance = content.get("contentProvenance") if isinstance(content, dict) else None
        expected = workbook["installation"]["contentProvenance"]
        if installed.get("id") != workbook["instanceId"] or not isinstance(provenance, dict) or set(provenance) != set(expected) or any(
            provenance.get(key) != expected[key] for key in ("packageId", "contentId")
        ) or any(not isinstance(provenance.get(key), str) or not provenance[key] for key in ("packageVersion", "contentVersion")):
            ownership_reasons.append(f"{workbook['instanceId']}: wrong instance/package/canonical-content identity or unintended copy")
            continue
        managed_updates.append({
            "instanceId": workbook["instanceId"], "contentId": workbook["contentId"],
            "contentChanged": _canonical_sha256(content) != workbook["installation"]["contentSha256"],
            "observedContentSha256": _canonical_sha256(content),
            "observedProvenance": provenance, "policy": "managed-same-id-upsert",
        })
    for expected in inspection["registrations"]:
        rows = _collection(bodies.get("registrations-" + expected["family"]))
        properties = expected["properties"]
        identities = expected["identity"]
        identity_key = "contentId" if isinstance(identities.get("contentId"), str) else "packageId"
        expected_identity = identities.get(identity_key)
        if not isinstance(expected_identity, str) or expected_identity.startswith("[") or rows is None:
            ownership_reasons.append(f"{expected['family']}: incomplete list or unresolved canonical registration identity")
            continue
        prefix = target["workspaceResourceId"] + "/providers/Microsoft.SecurityInsights/" + expected["family"] + "/"
        if any(not isinstance(row.get("properties"), dict) or not isinstance(row.get("id"), str)
               or not row["id"].casefold().startswith(prefix.casefold())
               or not isinstance(row["properties"].get("contentId"), str) for row in rows):
            ownership_reasons.append(f"{expected['family']}: malformed or out-of-scope complete-list entry")
            continue
        resolved_name = expected["resolvedName"]
        name_parts = resolved_name.split("/", 2) if isinstance(resolved_name, str) else []
        resolved_id = prefix + name_parts[2] if len(name_parts) == 3 and name_parts[1] == "Microsoft.SecurityInsights" else None
        exact_id_matches = [row for row in rows if resolved_id is not None and _same(row["id"], resolved_id)]
        if len(exact_id_matches) > 1 or any(row["properties"].get(identity_key) != expected_identity for row in exact_id_matches):
            ownership_reasons.append(f"{expected['family']}: exact selected registration ID has ambiguous/foreign canonical identity")
            continue
        matches = [row for row in rows if isinstance(row.get("properties"), dict)
                   and row["properties"].get(identity_key) == expected_identity]
        if len(matches) > 1:
            ownership_reasons.append(f"{expected['family']}: ambiguous canonical registration matches")
            continue
        if not matches:
            if resolved_id is None:
                ownership_reasons.append(f"{expected['family']}: unresolved resource name has no complete canonical identity mapping; absence cannot be proved")
            continue  # Only a complete list and resolved exact ID prove registration absence.
        actual = matches[0]
        props = actual["properties"]
        package = identities.get("packageId") or identities.get("contentId")
        actual_package = props.get("packageId", props.get("contentId"))
        if (actual_package != package or props.get("contentKind") != identities.get("contentKind")
                or (resolved_id is not None and not _same(actual["id"], resolved_id))):
            ownership_reasons.append(f"{expected['family']}: foreign/out-of-scope registration collision")
            continue
        managed_updates.append({
            "registrationId": actual["id"], "contentChanged": props != properties,
            "dependenciesPresent": isinstance(props.get("dependencies"), dict),
            "storedTemplatePresent": isinstance(props.get("mainTemplate"), dict),
            "policy": "managed-same-id-upsert",
        })
    if inspection["unsupportedOwnershipTypes"]:
        ownership_reasons.append("ownership unsupported for non-workbook resource families: " + ", ".join(inspection["unsupportedOwnershipTypes"]))
    check("ownershipVerified", not ownership_reasons and complete and access["tenantMatches"]
          and access["subscriptionMatches"] and access["workspaceMatches"],
          "; ".join(ownership_reasons) or "incomplete exact-target ownership metadata",
          managedUpdates=managed_updates)
    imported = any(resource["import"] for resource in inspection["inventory"])
    if imported:
        check("extensionResourceWriteAllowed", False,
              "VERIFIED documented MicrosoftSecurity ARM authentication/write contract is unavailable; GET, portal roles and known IDs do not establish imported-resource writes")
    else:
        checks["extensionResourceWriteAllowed"] = {
            "status": "not-required", "reasons": [], "required": False,
            "writeAccessVerified": False,
        }
    reasons = [reason for row in checks.values() for reason in row["reasons"]]
    ready = all(access[key] for key in _ACCESS_FLAGS if key != "extensionResourceWriteAllowed") and (
        not imported or access["extensionResourceWriteAllowed"]
    ) and checks["readConsentVerified"]["status"] == "verified" and checks["observationBinding"]["status"] == "verified"
    return {
        "schemaVersion": 1, **_binding(plan), "status": "ready" if ready else "blocked",
        **access, "checks": checks, "reasons": reasons, "writeAttempted": False,
        "observationSha256": _canonical_sha256(_sanitize(observations)),
        "providerWriteContractVerified": False,
    }
