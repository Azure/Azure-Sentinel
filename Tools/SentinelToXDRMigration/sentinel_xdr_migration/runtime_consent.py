from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import uuid
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping

import yaml

from .artifacts import (
    artifact_path,
    existing_artifact_path,
    write_json_artifact,
)
from .content_paths import content_path
from .converter import analytic_rule_files, xdr_detection_files
from .graph_client_config import (
    configured_azure_cli_profile,
    graph_auth_record_path,
    resolve_graph_client_id,
)
from .onboarding import (
    AUTH_RECORD_NAME,
    CONFIG_NAME,
    _read_json,
    _state_dir,
)
from .target_context import require_locked_target

PLAN_FILE_NAME = "runtime-query-plan.json"
CONSENT_FILE_NAME = "runtime-query-consent.json"
AUTHORING_CONSENT_FILE_NAME = "authoring-runtime-query-consent.json"
PLAN_SCHEMA_VERSION = "2.0.0"
LAB_CONSENT_SCHEMA_VERSION = "1.0.0"
AUTHORING_CONSENT_SCHEMA_VERSION = "1.0.0"
LAB_ACCESS_DIRECTORY = "lab-runtime-access"
PRIMARY_SETTING_FILE = "primary-setting.json"
LAB_CONSENT_FILE = "runtime-query-consent.json"
LAB_DECISION_FILE = "runtime-query-decision.json"
FAMILIES = {"sentinelSourceQueryFamily", "defenderXdrQueryFamily"}
SOURCE_FAMILY = "sentinelSourceQueryFamily"
SOURCE_PROVIDERS = {
    "azure-monitor-sdk",
    "triage-mcp",
    "log-analytics-cli",
}
_SOURCE_PROVIDER_NAMES = {
    "azure-monitor-sdk": "Azure Monitor Logs Query SDK",
    "triage-mcp": "Microsoft Sentinel Triage MCP",
    "log-analytics-cli": "Microsoft Sentinel Log Analytics CLI",
}
_LAB_IDENTITY_FIELDS = (
    "tenantId",
    "subscriptionId",
    "resourceGroup",
    "workspaceResourceId",
    "workspaceCustomerId",
)
_OPERATION_FAMILIES = {
    "sentinelSourceQueryFamily": {
        "operationId": "sentinel-source-kql-read",
        "providerSurface": "Azure Monitor Logs query / Sentinel source KQL",
        "httpMethod": "POST",
        "operationSemantics": "read-only query execution",
        "resourceMutation": False,
    },
    "defenderXdrQueryFamily": {
        "operationId": "defender-advanced-hunting-query-read",
        "providerSurface": "Microsoft Defender XDR Advanced Hunting",
        "httpMethod": "POST",
        "operationSemantics": "read-only query execution",
        "resourceMutation": False,
    },
}
_LAB_SCOPE_POLICY = {
    "crossSolution": True,
    "crossRun": True,
    "sourceQueryHashesAreSnapshotsOnly": True,
    "xdrQueryHashesAreSnapshotsOnly": True,
    "querySnapshotsAreNotConsentBindings": True,
}
_LAB_AUTHORIZATION_BOUNDARY = {
    "interactiveAuthenticationAuthorized": False,
    "adminConsentAuthorized": False,
    "permissionChangesAuthorized": False,
    "roleAssignmentsAuthorized": False,
    "environmentWritesAuthorized": False,
    "packageOrDeploymentAuthorized": False,
    "ingestionOrParityAuthorized": False,
    "ruleEnablementOrCleanupAuthorized": False,
}


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _runtime_query_plan_sha256(plan: Mapping[str, Any]) -> str:
    """Hash plan identity while keeping consent-decision summaries mutable."""
    identity = dict(plan)
    identity.pop("planSha256", None)
    consent = identity.get("labReadConsent")
    if isinstance(consent, Mapping):
        stable_consent = dict(consent)
        for field in (
            "status",
            "approvedFamilies",
            "requiresExplicitApproval",
            "recordedAt",
            "latestDecision",
        ):
            stable_consent.pop(field, None)
        identity["labReadConsent"] = stable_consent
    return _canonical_sha256(identity)


def _lab_access_directory() -> Path:
    return _state_dir() / LAB_ACCESS_DIRECTORY


def _lab_identity(target: Mapping[str, Any]) -> dict[str, str]:
    return {key: str(target[key]) for key in _LAB_IDENTITY_FIELDS}


def _lab_fingerprint(target: Mapping[str, Any]) -> str:
    return _canonical_sha256(_lab_identity(target))


def _lab_paths(target: Mapping[str, Any]) -> tuple[Path, Path]:
    fingerprint = _lab_fingerprint(target)
    directory = _lab_access_directory()
    return (
        directory / f"{fingerprint}.{PRIMARY_SETTING_FILE}",
        directory / f"{fingerprint}.{LAB_CONSENT_FILE}",
    )


def _lab_decision_path(target: Mapping[str, Any]) -> Path:
    return _lab_access_directory() / f"{_lab_fingerprint(target)}.{LAB_DECISION_FILE}"


@contextmanager
def _lab_lock(target: Mapping[str, Any]) -> Iterator[None]:
    directory = _lab_access_directory()
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / f"{_lab_fingerprint(target)}.lock"
    with lock_path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _atomic_write_json(path: Path, record: Mapping[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    payload = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def confirm_primary_lab_setting(
    solution: str | Path,
    *,
    actor: str,
    primary_setting_name: str,
    confirmed: bool,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    state, run_id = _run_context(root)
    if (state.get("context") or {}).get("workflowProfile") != "qualification":
        raise ValueError("primary lab-setting confirmation is Qualification-only")
    target = require_locked_target(root, materialize_missing=False)
    if confirmed is not True:
        raise ValueError("primary lab setting requires explicit --confirm-primary-setting")
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("primary-setting confirmation requires an explicit actor")
    if (
        not isinstance(primary_setting_name, str)
        or not primary_setting_name.strip()
        or len(primary_setting_name.strip()) > 128
    ):
        raise ValueError("primary-setting name must be nonempty text of at most 128 characters")
    observed_primary_setting = _load_primary_setting(target)
    observed_primary_version = (
        observed_primary_setting.get("recordSha256")
        if observed_primary_setting is not None
        else None
    )
    with _lab_lock(target):
        current_target = require_locked_target(root, materialize_missing=False)
        if _lab_identity(current_target) != _lab_identity(target):
            raise ValueError("locked lab target changed during primary-setting confirmation; retry")
        current_state, current_run_id = _run_context(root)
        if current_run_id != run_id or current_state.get("context", {}).get("workflowProfile") != "qualification":
            raise ValueError("Qualification run changed during primary-setting confirmation; retry")
        target = current_target
        current_primary_setting = _load_primary_setting(target)
        current_primary_version = (
            current_primary_setting.get("recordSha256")
            if current_primary_setting is not None
            else None
        )
        if current_primary_version != observed_primary_version:
            raise ValueError(
                "primary lab setting changed during confirmation; review the current setting and retry"
            )
        setting_path, _ = _lab_paths(target)
        setting = {
            "schemaVersion": LAB_CONSENT_SCHEMA_VERSION,
            "status": "confirmed",
            "solution": root.name,
            "runId": run_id,
            "target": _lab_identity(target),
            "targetFingerprintSha256": _lab_fingerprint(target),
            "primarySetting": {
                "name": primary_setting_name.strip(),
                "value": target["workspaceResourceId"],
                "confirmed": True,
                "confirmationType": "explicit-user-attestation",
                "serviceVerified": False,
            },
            "actor": actor.strip(),
            "confirmedAt": datetime.now(timezone.utc).isoformat(),
        }
        setting["recordSha256"] = _canonical_sha256(setting)
        _atomic_write_json(setting_path, setting)
    return {
        "status": "confirmed",
        "path": str(setting_path),
        "target": setting["target"],
        "primarySetting": setting["primarySetting"],
        "serviceVerified": False,
    }


def _load_primary_setting(target: Mapping[str, Any]) -> dict[str, Any] | None:
    setting_path, _ = _lab_paths(target)
    try:
        record = json.loads(setting_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(record, dict) or record.get("status") != "confirmed":
        return None
    if (
        record.get("schemaVersion") != LAB_CONSENT_SCHEMA_VERSION
        or record.get("target") != _lab_identity(target)
        or record.get("targetFingerprintSha256") != _lab_fingerprint(target)
        or not isinstance(record.get("actor"), str)
        or not record["actor"].strip()
        or not isinstance(record.get("confirmedAt"), str)
    ):
        return None
    primary = record.get("primarySetting")
    if (
        not isinstance(primary, dict)
        or primary.get("confirmed") is not True
        or primary.get("serviceVerified") is not False
        or primary.get("confirmationType") != "explicit-user-attestation"
        or primary.get("value") != target.get("workspaceResourceId")
        or not isinstance(primary.get("name"), str)
        or not primary["name"].strip()
    ):
        return None
    fingerprinted = {key: value for key, value in record.items() if key != "recordSha256"}
    if record.get("recordSha256") != _canonical_sha256(fingerprinted):
        return None
    return record


def _read_lab_decision(target: Mapping[str, Any]) -> dict[str, Any] | None:
    try:
        record = json.loads(_lab_decision_path(target).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(record, dict):
        return None
    unsigned = {key: value for key, value in record.items() if key != "decisionSha256"}
    if (
        record.get("schemaVersion") != LAB_CONSENT_SCHEMA_VERSION
        or record.get("decisionType") != "non-authorizing-runtime-query-decision"
        or record.get("status") not in {"declined", "revised"}
        or not isinstance(record.get("actor"), str)
        or not record["actor"].strip()
        or not isinstance(record.get("reason"), str)
        or not record["reason"].strip()
        or not isinstance(record.get("binding"), dict)
        or record.get("authorizesRuntimeQueries") is not False
        or record.get("revokesExistingGrant") is not False
        or record.get("decisionSha256") != _canonical_sha256(unsigned)
    ):
        return None
    return record


def _lab_decision_summary(
    target: Mapping[str, Any],
    run_binding: Mapping[str, Any],
    primary_setting: Mapping[str, Any] | None,
) -> dict[str, Any]:
    record = _read_lab_decision(target)
    if record is None:
        return {"status": "unanswered"}
    expected_lab_binding = (
        _lab_binding(target, primary_setting)
        if primary_setting is not None
        else None
    )
    if (
        record["binding"] != run_binding
        or record.get("labBinding") != expected_lab_binding
    ):
        return {"status": "prior-decision-not-current"}
    return {
        "status": record["status"],
        "actor": record["actor"],
        "reason": record["reason"],
        "recordedAt": record["recordedAt"],
        "authorizesRuntimeQueries": False,
        "revokesExistingGrant": False,
    }


def _lab_binding(
    target: Mapping[str, Any],
    primary_setting: Mapping[str, Any],
) -> dict[str, Any]:
    primary = primary_setting["primarySetting"]
    return {
        "labFingerprintSha256": _lab_fingerprint(target),
        "target": _lab_identity(target),
        "confirmedPrimarySetting": {
            "name": primary["name"],
            "value": primary["value"],
            "confirmationType": primary["confirmationType"],
            "serviceVerified": False,
        },
        "operationFamilies": {
            name: _OPERATION_FAMILIES[name]
            for name in sorted(FAMILIES)
        },
        "readOnlyOnly": True,
        "authenticationOrPermissionChangesAuthorized": False,
        "environmentWritesAuthorized": False,
    }


def _query_sha256(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()


def _run_context(solution: Path) -> tuple[dict[str, Any], str]:
    state_path = existing_artifact_path(solution, "workflow-state.json")
    if not state_path.is_file():
        raise ValueError("workflow state does not exist; runtime query consent is unavailable")
    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    context = state.get("context") or {}
    if context.get("workflowProfile") not in {"authoring", "qualification"}:
        raise ValueError("runtime query consent requires an explicit workflow profile")
    run_id = state.get("runId")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("workflow state has no run ID")
    return state, run_id


def _authoring_tenant_id(state: Mapping[str, Any]) -> str:
    context = state.get("context") or {}
    tenant_id = context.get("tenantId") if isinstance(context, Mapping) else None
    try:
        normalized = str(uuid.UUID(tenant_id)) if isinstance(tenant_id, str) else ""
    except ValueError:
        normalized = ""
    if not normalized:
        raise ValueError(
            "Authoring Advanced Hunting requires an explicit tenant ID in the "
            "selected workflow run; no target discovery is performed"
        )
    return normalized


def _build_authoring_runtime_query_plan(
    root: Path,
    state: Mapping[str, Any],
    run_id: str,
    *,
    source_provider: str,
) -> dict[str, Any]:
    tenant_id = _authoring_tenant_id(state)
    xdr_rules, _ = _xdr_inventory(root)
    target_fingerprint = _canonical_sha256({"tenantId": tenant_id})
    source_provider_identity = {
        "provider": source_provider,
        "name": _SOURCE_PROVIDER_NAMES[source_provider],
        "route": "qualification-only",
        "authentication": {
            "classification": "qualification-only",
            "cachedAuthConfigured": False,
            "interactiveSignInPermittedByThisConsent": False,
        },
    }
    graph_provider_identity = {
        "provider": "graph",
        "name": "Microsoft Defender XDR Advanced Hunting",
        "route": "defender-xdr-query-family",
        "authentication": _authentication_requirement(
            "graph",
            {"tenantId": tenant_id},
        ),
    }
    families = {
        SOURCE_FAMILY: {
            "provider": source_provider_identity,
            "ruleCount": 0,
            "queryCount": 0,
            "queries": [],
            "status": "qualification-only",
        },
        "defenderXdrQueryFamily": {
            "provider": graph_provider_identity,
            "ruleCount": len(xdr_rules),
            "queryCount": len(xdr_rules),
            "queries": xdr_rules,
            "status": "ready" if xdr_rules else "incomplete",
        },
    }
    for family in families.values():
        family["familySha256"] = _canonical_sha256(family)
    plan = {
        "schemaVersion": PLAN_SCHEMA_VERSION,
        "status": "ready" if xdr_rules else "incomplete",
        "solution": root.name,
        "solutionPath": ".",
        "runId": run_id,
        "workflowProfile": "authoring",
        "target": {
            "tenantId": tenant_id,
            "fingerprintSha256": target_fingerprint,
            "workspaceSelected": False,
        },
        "labReadConsent": {
            "scope": {
                "scopeType": "one-run-authoring-query-only",
                "tenantId": tenant_id,
                "targetFingerprintSha256": target_fingerprint,
                "crossSolution": False,
                "crossRun": False,
            },
            "status": "requires-explicit-approval",
            "approvedFamilies": [],
            "requiresExplicitApproval": True,
            "reusableAcrossSolutionsAndRuns": False,
            "queryHashesAreConsentBindings": True,
            "operationFamilies": {
                "defenderXdrQueryFamily": _OPERATION_FAMILIES[
                    "defenderXdrQueryFamily"
                ]
            },
            "preselectedFamilies": [],
        },
        "families": families,
        "consentChoices": {
            "availableFamilies": ["defenderXdrQueryFamily"],
            "preselectedFamilies": [],
            "noResponseMeans": "not-approved-and-not-run",
            "declineOrReviseBlocksOfflineAuthoring": False,
        },
        "safety": {
            "providerQueriesPerformed": False,
            "newAuthenticationPerformed": False,
            "workspaceDiscoveryPerformed": False,
            "cloudWritesPerformed": False,
        },
        "authorizationBoundary": {
            "readOnlyRuntimeQueriesOnly": True,
            "interactiveAuthenticationAuthorized": False,
            "permissionChangesAuthorized": False,
            "environmentWritesAuthorized": False,
            "sourceSdkValidationAuthorized": False,
            "packageOrDeploymentAuthorized": False,
            "ingestionOrParityAuthorized": False,
            "ruleEnablementOrCleanupAuthorized": False,
        },
    }
    authoring_record, authoring_status = _load_authoring_consent(root, plan)
    plan["labReadConsent"].update(
        _authoring_consent_summary(authoring_record, authoring_status)
    )
    plan["planSha256"] = _runtime_query_plan_sha256(plan)
    return plan


def _authentication_requirement(provider: str, target: Mapping[str, Any]) -> dict[str, Any]:
    if provider == "graph":
        state_dir = _state_dir()
        client_id = resolve_graph_client_id(state_dir, "advancedHunting")
        auth_record = graph_auth_record_path(
            state_dir,
            "advancedHunting",
            client_id,
            AUTH_RECORD_NAME,
        )
        record_present = auth_record.is_file()
        record_valid = False
        record_tenant = None
        if record_present:
            try:
                from azure.identity import AuthenticationRecord

                record = AuthenticationRecord.deserialize(
                    auth_record.read_text(encoding="utf-8")
                )
                record_tenant = getattr(record, "tenant_id", None)
                record_valid = bool(record_tenant)
            except (ImportError, OSError, ValueError):
                pass
        configured_tenant = _read_json(state_dir / CONFIG_NAME).get("tenantId")
        if configured_tenant is None:
            configured_tenant = record_tenant
        tenant_matches = (
            configured_tenant.casefold() == str(target["tenantId"]).casefold()
            if isinstance(configured_tenant, str)
            else None
        )
        cached = record_valid and tenant_matches is not False
        return {
            "purpose": "advancedHunting",
            "clientId": client_id,
            "classification": (
                "cached-auth-configured-unverified"
                if cached
                else "separate-interactive-sign-in-required"
            ),
            "cachedAuthConfigured": cached,
            "interactiveSignInPermittedByThisConsent": False,
            "evidence": "local Graph authentication-record/config presence only; token validity is not tested",
        }
    if provider == "azure-monitor-sdk":
        cli = shutil.which("az")
        azure_config_dir = configured_azure_cli_profile(_state_dir())
        cached = False
        if cli and azure_config_dir:
            try:
                environment = os.environ.copy()
                environment["AZURE_CONFIG_DIR"] = azure_config_dir
                result = subprocess.run(
                    [cli, "account", "show", "--output", "json"],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=10,
                    env=environment,
                )
                if result.returncode == 0:
                    account = json.loads(result.stdout)
                    cached = (
                        isinstance(account, dict)
                        and str(account.get("tenantId", "")).casefold()
                        == str(target["tenantId"]).casefold()
                    )
            except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
                cached = False
        return {
            "classification": (
                "existing-cached-auth-available"
                if cached
                else "separate-interactive-sign-in-required"
            ),
            "cachedAuthConfigured": cached,
            "interactiveSignInPermittedByThisConsent": False,
            "evidence": "local az account show result for the locked tenant; no login is started",
        }
    return {
        "classification": "existing-provider-session-required-unverified",
        "cachedAuthConfigured": None,
        "interactiveSignInPermittedByThisConsent": False,
        "evidence": (
            "authentication is managed outside this CLI; dispatch must use an "
            "existing provider session, and any sign-in needs a separate immediate approval"
        ),
    }


def _query_entry(
    *, rule_id: Any, path: str, query: str, kind: str = "rule-query"
) -> dict[str, Any]:
    return {
        "ruleId": str(rule_id).strip() if rule_id is not None else None,
        "path": path,
        "kind": kind,
        "queryText": query,
        "querySha256": _query_sha256(query),
    }


def _source_inventory(root: Path) -> list[dict[str, Any]]:
    inventory = []
    for path in analytic_rule_files(root):
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        if not isinstance(document, dict) or not isinstance(document.get("query"), str):
            raise ValueError(f"source Analytic Rule has no query: {path}")
        inventory.append(
            _query_entry(
                rule_id=document.get("id"),
                path=path.relative_to(root).as_posix(),
                query=document["query"],
            )
        )
    return sorted(inventory, key=lambda item: item["path"])


def _xdr_inventory(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output = root / "XDR Detections"
    rules: list[dict[str, Any]] = []
    for path in xdr_detection_files(output):
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        query = (
            (((document or {}).get("properties") or {}).get("queryCondition") or {})
            .get("queryText")
        )
        if not isinstance(document, dict) or not isinstance(query, str) or not query.strip():
            raise ValueError(f"Custom Detection has no Advanced Hunting query: {path}")
        relative = path.relative_to(output).as_posix()
        rule = _query_entry(
            rule_id=document.get("id"),
            path=relative,
            query=query,
        )
        rules.append(rule)
    return (
        sorted(rules, key=lambda item: item["path"]),
        [],
    )


def build_runtime_query_plan(
    solution: str | Path,
    *,
    source_provider: str = "azure-monitor-sdk",
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    if source_provider not in SOURCE_PROVIDERS:
        raise ValueError(f"unsupported Sentinel source provider: {source_provider}")
    state, run_id = _run_context(root)
    profile = (state.get("context") or {}).get("workflowProfile")
    if profile == "authoring":
        return _build_authoring_runtime_query_plan(
            root,
            state,
            run_id,
            source_provider=source_provider,
        )
    target = require_locked_target(root, materialize_missing=False)
    primary_setting_record = _load_primary_setting(target)
    target_fingerprint = _canonical_sha256(
        {
            key: target[key]
            for key in (
                "tenantId",
                "subscriptionId",
                "resourceGroup",
                "workspaceResourceId",
                "workspaceName",
                "workspaceCustomerId",
            )
        }
    )
    source_provider_identity = {
        "provider": source_provider,
        "name": _SOURCE_PROVIDER_NAMES[source_provider],
        "route": "sentinel-source-query-family",
        "authentication": _authentication_requirement(source_provider, target),
    }
    graph_provider_identity = {
        "provider": "graph",
        "name": "Microsoft Defender XDR Advanced Hunting",
        "route": "defender-xdr-query-family",
        "authentication": _authentication_requirement("graph", target),
    }
    source_queries = _source_inventory(root)
    xdr_rules, _ = _xdr_inventory(root)
    xdr_queries = xdr_rules
    if primary_setting_record is None:
        lab_consent_status = "requires-explicit-primary-setting-confirmation"
        lab_consent_record = None
        lab_approved = set()
    else:
        lab_consent_record, lab_consent_status = _load_lab_consent(
            target,
            primary_setting_record,
        )
        lab_approved = (
            _approved_families(
                lab_consent_record,
                binding=_lab_binding(target, primary_setting_record),
            )
            if lab_consent_record is not None
            else set()
        ) or set()
    families = {
        "sentinelSourceQueryFamily": {
            "provider": source_provider_identity,
            "ruleCount": len(source_queries),
            "queryCount": len(source_queries),
            "queries": source_queries,
        },
        "defenderXdrQueryFamily": {
            "provider": graph_provider_identity,
            "ruleCount": len(xdr_rules),
            "queryCount": len(xdr_queries),
            "queries": xdr_queries,
        },
    }
    for family in families.values():
        family["status"] = "ready" if family["ruleCount"] else "incomplete"
        family["familySha256"] = _canonical_sha256(family)
    plan = {
        "schemaVersion": PLAN_SCHEMA_VERSION,
        "status": "ready" if source_queries or xdr_queries else "incomplete",
        "solution": root.name,
        "solutionPath": ".",
        "runId": run_id,
        "workflowProfile": "qualification",
        "target": {
            **{
                key: target[key]
                for key in (
                    "tenantId",
                    "subscriptionId",
                    "resourceGroup",
                    "workspaceResourceId",
                    "workspaceName",
                    "workspaceCustomerId",
                )
            },
            "fingerprintSha256": target_fingerprint,
        },
        "labReadConsent": {
            "scope": (
                _lab_binding(target, primary_setting_record)
                if primary_setting_record is not None
                else None
            ),
            "status": lab_consent_status,
            "approvedFamilies": sorted(lab_approved),
            "requiresExplicitApproval": not bool(lab_approved),
            "recordedAt": (
                lab_consent_record.get("recordedAt")
                if lab_consent_record is not None
                else None
            ),
            "reusableAcrossSolutionsAndRuns": True,
            "queryHashesAreRunSnapshotsNotLabConsentBindings": True,
            "operationFamilies": {
                name: _OPERATION_FAMILIES[name]
                for name in sorted(FAMILIES)
            },
            "preselectedFamilies": [],
        },
        "families": families,
        "consentChoices": {
            "availableFamilies": list(sorted(FAMILIES)),
            "preselectedFamilies": [],
            "noResponseMeans": "not-approved-and-not-run",
            "declineOrReviseBlocksOfflineAuthoring": False,
        },
        "safety": {
            "providerQueriesPerformed": False,
            "newAuthenticationPerformed": False,
            "cloudWritesPerformed": False,
        },
        "authorizationBoundary": {
            "readOnlyRuntimeQueriesOnly": True,
            "interactiveAuthenticationAuthorized": False,
            "permissionChangesAuthorized": False,
            "environmentWritesAuthorized": False,
            "packageOrDeploymentAuthorized": False,
            "ingestionOrParityAuthorized": False,
            "ruleEnablementOrCleanupAuthorized": False,
        },
    }
    plan["labReadConsent"]["latestDecision"] = _lab_decision_summary(
        target,
        _decision_binding(plan),
        primary_setting_record,
    )
    plan["planSha256"] = _runtime_query_plan_sha256(plan)
    return plan


def persist_runtime_query_plan(
    solution: str | Path,
    *,
    source_provider: str = "azure-monitor-sdk",
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    plan = build_runtime_query_plan(root, source_provider=source_provider)
    path = artifact_path(root, PLAN_FILE_NAME, create_parent=True)
    write_json_artifact(root, path, plan)
    return {**plan, "planPath": str(path)}


def _current_binding(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "solution": plan["solution"],
        "workflowProfile": plan["workflowProfile"],
        "runId": plan["runId"],
        "targetFingerprintSha256": plan["target"]["fingerprintSha256"],
        "planSha256": plan.get("planSha256"),
        "families": {
            name: {
                "familySha256": family["familySha256"],
                "ruleCount": family["ruleCount"],
                "queryCount": family["queryCount"],
                "provider": family["provider"],
            }
            for name, family in sorted(plan["families"].items())
        },
    }


def _decision_binding(plan: Mapping[str, Any]) -> dict[str, Any]:
    binding = _current_binding(plan)
    binding.pop("planSha256", None)
    return binding


def _valid_authoring_consent(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    unsigned = {
        key: value for key, value in record.items() if key != "consentSha256"
    }
    approved = record.get("approvedFamilies")
    return bool(
        record.get("schemaVersion") == AUTHORING_CONSENT_SCHEMA_VERSION
        and record.get("consentType") == "authoring-run-bound-runtime-query"
        and record.get("status") in {"approved", "declined", "revised"}
        and isinstance(record.get("actor"), str)
        and record["actor"].strip()
        and isinstance(record.get("recordedAt"), str)
        and isinstance(approved, list)
        and all(isinstance(item, str) for item in approved)
        and len(set(approved)) == len(approved)
        and (
            (record.get("status") == "approved"
             and approved == ["defenderXdrQueryFamily"])
            or (record.get("status") != "approved" and not approved)
        )
        and record.get("scopePolicy") == {
            "crossSolution": False,
            "crossRun": False,
            "queryHashesAreConsentBindings": True,
        }
        and record.get("authorizationBoundary")
        == {
            "readOnlyAdvancedHuntingOnly": True,
            "interactiveAuthenticationAuthorized": False,
            "sourceSdkValidationAuthorized": False,
            "permissionChangesAuthorized": False,
            "environmentWritesAuthorized": False,
            "packageOrDeploymentAuthorized": False,
            "ingestionOrParityAuthorized": False,
            "ruleEnablementOrCleanupAuthorized": False,
        }
        and isinstance(record.get("binding"), dict)
        and record.get("authorizesRuntimeQueries")
        is (record.get("status") == "approved")
        and record.get("consentSha256") == _canonical_sha256(unsigned)
    )


def _load_authoring_consent(
    root: Path,
    plan: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, str]:
    path = existing_artifact_path(root, AUTHORING_CONSENT_FILE_NAME)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "not-approved"
    except (OSError, json.JSONDecodeError):
        return None, "invalid"
    if not _valid_authoring_consent(record):
        return None, "invalid"
    if record.get("binding") != _decision_binding(plan):
        return record, "stale"
    return record, str(record["status"])


def _authoring_consent_summary(
    record: Mapping[str, Any] | None,
    status: str,
) -> dict[str, Any]:
    approved = (
        ["defenderXdrQueryFamily"]
        if status == "approved" and record is not None
        else []
    )
    decision = (
        {
            "status": record["status"],
            "actor": record["actor"],
            "reason": record.get("reason"),
            "recordedAt": record["recordedAt"],
            "authorizesRuntimeQueries": status == "approved",
        }
        if record is not None
        else {"status": "unanswered", "authorizesRuntimeQueries": False}
    )
    return {
        "status": status,
        "approvedFamilies": approved,
        "requiresExplicitApproval": not bool(approved),
        "recordedAt": (
            record.get("recordedAt") if status == "approved" and record else None
        ),
        "reusableAcrossSolutionsAndRuns": False,
        "latestDecision": decision,
    }


def _valid_lab_record(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    fingerprinted = {
        key: value for key, value in record.items() if key != "consentSha256"
    }
    approved = record.get("approvedFamilies")
    return bool(
        record.get("schemaVersion") == LAB_CONSENT_SCHEMA_VERSION
        and record.get("consentType") == "shared-lab-read-only-runtime-query"
        and record.get("status") in {"approved", "declined", "revoked"}
        and isinstance(record.get("actor"), str)
        and record["actor"].strip()
        and isinstance(record.get("recordedAt"), str)
        and isinstance(approved, list)
        and all(isinstance(item, str) and item in FAMILIES for item in approved)
        and len(set(approved)) == len(approved)
        and record.get("scopePolicy") == _LAB_SCOPE_POLICY
        and record.get("authorizationBoundary") == _LAB_AUTHORIZATION_BOUNDARY
        and isinstance(record.get("binding"), dict)
        and (
            (record.get("status") == "approved" and bool(approved))
            or (record.get("status") != "approved" and not approved)
        )
        and record.get("consentSha256") == _canonical_sha256(fingerprinted)
    )


def _load_lab_consent(
    target: Mapping[str, Any],
    primary_setting: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    _, consent_path = _lab_paths(target)
    try:
        record = json.loads(consent_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "not-approved"
    except (OSError, json.JSONDecodeError):
        return None, "invalid"
    if not _valid_lab_record(record):
        return None, "invalid"
    if record.get("binding") != _lab_binding(target, primary_setting):
        return None, "stale"
    if record.get("status") != "approved":
        return None, str(record.get("status"))
    return record, "approved"


def revoke_runtime_query_consent(
    solution: str | Path,
    *,
    actor: str,
    reason: str,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("revoking lab runtime-query consent requires an explicit actor")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("revoking lab runtime-query consent requires a reason")
    target = require_locked_target(root, materialize_missing=False)
    with _lab_lock(target):
        current_target = require_locked_target(root, materialize_missing=False)
        if _lab_identity(current_target) != _lab_identity(target):
            raise ValueError("locked lab target changed during consent revocation; retry")
        target = current_target
        _, consent_path = _lab_paths(target)
        setting = _load_primary_setting(target)
        binding = (
            _lab_binding(target, setting)
            if setting is not None
            else {
                "labFingerprintSha256": _lab_fingerprint(target),
                "target": _lab_identity(target),
                "primarySettingConfirmed": False,
            }
        )
        record = {
            "schemaVersion": LAB_CONSENT_SCHEMA_VERSION,
            "status": "revoked",
            "consentType": "shared-lab-read-only-runtime-query",
            "actor": actor.strip(),
            "recordedAt": datetime.now(timezone.utc).isoformat(),
            "reason": reason.strip(),
            "approvedFamilies": [],
            "binding": binding,
            "scopePolicy": _LAB_SCOPE_POLICY,
            "authorizationBoundary": _LAB_AUTHORIZATION_BOUNDARY,
        }
        record["consentSha256"] = _canonical_sha256(record)
        _atomic_write_json(consent_path, record)
        try:
            _lab_decision_path(target).unlink()
        except FileNotFoundError:
            pass
    return {"status": "revoked", "path": str(consent_path)}


def _approved_families(
    record: Mapping[str, Any],
    *,
    binding: Mapping[str, Any],
) -> set[str] | None:
    approved = record.get("approvedFamilies")
    if (
        not _valid_lab_record(record)
        or record.get("status") != "approved"
        or record.get("binding") != binding
    ):
        return None
    return set(approved)


def _family_execution_status(
    root: Path,
    family: Mapping[str, Any],
) -> dict[str, Any]:
    provider = family["provider"]["provider"]
    report_provider = {
        "azure-monitor-sdk": "azure-monitor-sdk",
        "triage-mcp": "triage-mcp",
        "log-analytics-cli": "log-analytics-cli",
        "graph": "graph",
    }[provider]
    path = existing_artifact_path(
        root,
        f"runtime-validation.{report_provider}.json",
    )
    if not path.is_file():
        return {"executionStatus": "not-run"}
    try:
        report = json.loads(path.read_text(encoding="utf-8-sig"))
        results = report.get("results")
        if report.get("provider") != report_provider or not isinstance(results, list):
            return {"executionStatus": "stale-or-invalid-report"}
        expected = Counter(
            entry["querySha256"]
            for entry in family["queries"]
            if entry["kind"] == "rule-query"
        )
        actual = Counter(
            item.get("querySha256")
            for item in results
            if isinstance(item, dict) and isinstance(item.get("querySha256"), str)
        )
        if actual != expected:
            return {"executionStatus": "stale-or-incomplete"}
        counts = {
            status: sum(item.get("status") == status for item in results)
            for status in ("passed", "failed", "blocked", "not-run")
        }
        return {
            "executionStatus": (
                "recorded" if counts["not-run"] == 0 else "incomplete"
            ),
            "results": counts,
            "runtimeReport": path.name,
        }
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return {"executionStatus": "stale-or-invalid-report"}


def record_runtime_query_consent(
    solution: str | Path,
    *,
    expected_plan_sha256: str,
    actor: str,
    approved_families: list[str],
    declined: bool = False,
    revised: bool = False,
    reason: str | None = None,
    source_provider: str = "azure-monitor-sdk",
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("runtime query consent requires an explicit nonempty actor")
    if sum((declined, revised)) > 1:
        raise ValueError("decline and revise cannot be combined")
    if declined or revised:
        if approved_families:
            raise ValueError("decline or revise cannot be combined with approved families")
        if declined and (not isinstance(reason, str) or not reason.strip()):
            raise ValueError("declining runtime query consent requires a reason")
    elif not approved_families:
        raise ValueError("select at least one query family; no selection is not consent")
    if len(set(approved_families)) != len(approved_families):
        raise ValueError("runtime query consent families must be unique")
    unknown = set(approved_families) - FAMILIES
    if unknown:
        raise ValueError("unsupported runtime query family: " + ", ".join(sorted(unknown)))

    plan = build_runtime_query_plan(root, source_provider=source_provider)
    if not isinstance(expected_plan_sha256, str) or expected_plan_sha256 != plan["planSha256"]:
        raise ValueError(
            "runtime query plan changed; review the current inventory and plan hash before selecting again"
        )
    for family in approved_families:
        if plan["families"][family]["status"] != "ready":
            raise ValueError(f"{family} has no complete current query inventory")
    if plan["workflowProfile"] == "authoring":
        if approved_families and approved_families != ["defenderXdrQueryFamily"]:
            raise ValueError(
                "Authoring consent is limited to its exact Defender XDR query family"
            )
        current_state, current_run_id = _run_context(root)
        if (
            current_run_id != plan["runId"]
            or (current_state.get("context") or {}).get("workflowProfile")
            != "authoring"
        ):
            raise ValueError("the selected Authoring run changed during consent review")
        current_plan = build_runtime_query_plan(
            root,
            source_provider=source_provider,
        )
        if current_plan["planSha256"] != expected_plan_sha256:
            raise ValueError(
                "runtime query plan changed during consent review; prepare and review the current plan"
            )
        record = {
            "schemaVersion": AUTHORING_CONSENT_SCHEMA_VERSION,
            "status": "revised" if revised else "declined" if declined else "approved",
            "consentType": "authoring-run-bound-runtime-query",
            "actor": actor.strip(),
            "recordedAt": datetime.now(timezone.utc).isoformat(),
            "reason": reason.strip() if isinstance(reason, str) else None,
            "approvedFamilies": (
                ["defenderXdrQueryFamily"]
                if not declined and not revised
                else []
            ),
            "planSha256": current_plan["planSha256"],
            "binding": _decision_binding(current_plan),
            "scopePolicy": {
                "crossSolution": False,
                "crossRun": False,
                "queryHashesAreConsentBindings": True,
            },
            "authorizationBoundary": {
                "readOnlyAdvancedHuntingOnly": True,
                "interactiveAuthenticationAuthorized": False,
                "sourceSdkValidationAuthorized": False,
                "permissionChangesAuthorized": False,
                "environmentWritesAuthorized": False,
                "packageOrDeploymentAuthorized": False,
                "ingestionOrParityAuthorized": False,
                "ruleEnablementOrCleanupAuthorized": False,
            },
            "authorizesRuntimeQueries": not (declined or revised),
        }
        record["consentSha256"] = _canonical_sha256(record)
        path = artifact_path(
            root,
            AUTHORING_CONSENT_FILE_NAME,
            create_parent=True,
        )
        _atomic_write_json(path, record)
        return {
            "status": record["status"],
            "consentRecorded": record["status"] == "approved",
            "decisionRecorded": record["status"] != "approved",
            "path": str(path),
            "planSha256": current_plan["planSha256"],
            "approvedFamilies": record["approvedFamilies"],
            "consentScope": "one-run-authoring-query-only",
            "crossSolution": False,
            "crossRun": False,
            "environmentWritesAuthorized": False,
        }
    target = require_locked_target(root, materialize_missing=False)
    status = "revised" if revised else "declined" if declined else "approved"
    with _lab_lock(target):
        current_target = require_locked_target(root, materialize_missing=False)
        if _lab_identity(current_target) != _lab_identity(target):
            raise ValueError("locked lab target changed during consent review; prepare a new plan")
        target = current_target
        current_plan = build_runtime_query_plan(root, source_provider=source_provider)
        if current_plan["planSha256"] != expected_plan_sha256:
            raise ValueError(
                "runtime query plan changed during consent review; prepare and review the current plan"
            )
        for family in approved_families:
            if current_plan["families"][family]["status"] != "ready":
                raise ValueError(f"{family} has no complete current query inventory")
        primary_setting = _load_primary_setting(target)
        if primary_setting is None:
            raise ValueError(
                "the lab primary setting has not been explicitly confirmed; run "
                "confirm-primary-lab-setting before requesting shared lab read consent"
            )
        _, consent_path = _lab_paths(target)
        existing_record, _ = _load_lab_consent(target, primary_setting)
        if existing_record is not None and not _valid_lab_record(existing_record):
            raise ValueError("shared lab consent record failed integrity validation")
        recorded_at = datetime.now(timezone.utc).isoformat()
        if status in {"declined", "revised"}:
            decision = {
                "schemaVersion": LAB_CONSENT_SCHEMA_VERSION,
                "decisionType": "non-authorizing-runtime-query-decision",
                "status": status,
                "actor": actor.strip(),
                "reason": (
                    reason.strip()
                    if isinstance(reason, str) and reason.strip()
                    else "Plan review deferred."
                ),
                "recordedAt": recorded_at,
                "binding": _decision_binding(current_plan),
                "labBinding": _lab_binding(target, primary_setting),
                "planSha256": current_plan["planSha256"],
                "offeredFamilies": sorted(
                    family
                    for family in FAMILIES
                    if current_plan["families"][family]["status"] == "ready"
                ),
                "authorizesRuntimeQueries": False,
                "revokesExistingGrant": False,
            }
            decision["decisionSha256"] = _canonical_sha256(decision)
            decision_path = _lab_decision_path(target)
            _atomic_write_json(decision_path, decision)
            return {
                "status": status,
                "decisionRecorded": True,
                "consentRecorded": False,
                "approvedFamilies": [],
                "existingGrantPreserved": bool(existing_record),
                "decisionPath": str(decision_path),
                "planSha256": current_plan["planSha256"],
            }
        approved_to_store = sorted(
            (set(existing_record["approvedFamilies"]) if existing_record else set())
            | set(approved_families)
        )
        record = {
            "schemaVersion": LAB_CONSENT_SCHEMA_VERSION,
            "status": "approved",
            "consentType": "shared-lab-read-only-runtime-query",
            "actor": actor.strip(),
            "recordedAt": recorded_at,
            "reason": reason.strip() if isinstance(reason, str) else None,
            "approvedFamilies": approved_to_store,
            "binding": _lab_binding(target, primary_setting),
            "scopePolicy": _LAB_SCOPE_POLICY,
            "authorizationBoundary": _LAB_AUTHORIZATION_BOUNDARY,
        }
        record["consentSha256"] = _canonical_sha256(record)
        _atomic_write_json(consent_path, record)
        try:
            _lab_decision_path(target).unlink()
        except FileNotFoundError:
            pass
    return {
        "status": "approved",
        "consentRecorded": True,
        "path": str(consent_path),
        "planSha256": current_plan["planSha256"],
        "approvedFamilies": record["approvedFamilies"],
        "crossSolution": True,
        "crossRun": True,
    }


def runtime_query_consent_status(
    solution: str | Path,
    *,
    source_provider: str | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    try:
        if source_provider is None:
            plan_path = existing_artifact_path(root, PLAN_FILE_NAME)
            if plan_path.is_file():
                persisted_plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
                persisted_route = (
                    (((persisted_plan.get("families") or {}).get(SOURCE_FAMILY) or {}).get("provider") or {}).get("provider")
                )
                source_provider = (
                    persisted_route
                    if persisted_route in SOURCE_PROVIDERS
                    else "azure-monitor-sdk"
                )
            else:
                source_provider = "azure-monitor-sdk"
        plan = build_runtime_query_plan(root, source_provider=source_provider)
        if plan["workflowProfile"] == "authoring":
            record, status = _load_authoring_consent(root, plan)
            families = {}
            for name, family in plan["families"].items():
                family_status = family["status"]
                if name == "defenderXdrQueryFamily" and status == "approved":
                    family_status = "approved"
                families[name] = {
                    "status": family_status,
                    **(
                        _family_execution_status(root, family)
                        if name == "defenderXdrQueryFamily"
                        else {"executionStatus": "qualification-only"}
                    ),
                }
            current_binding = _current_binding(plan)
            try:
                snapshot = json.loads(
                    existing_artifact_path(root, CONSENT_FILE_NAME).read_text(
                        encoding="utf-8-sig"
                    )
                )
            except (OSError, json.JSONDecodeError):
                snapshot = None
            snapshot_current = bool(
                isinstance(snapshot, dict)
                and snapshot.get("binding") == current_binding
                and snapshot.get("workflowProfile") == "authoring"
                and snapshot.get("status") == "approved"
            )
            return {
                "status": status,
                "workflowProfile": "authoring",
                "consentScope": "one-run-authoring-query-only",
                "approvedFamilies": (
                    ["defenderXdrQueryFamily"] if status == "approved" else []
                ),
                "families": families,
                "runSnapshot": {
                    "status": "current" if snapshot_current else "not-current",
                    "binding": current_binding if snapshot_current else None,
                },
                "latestDecision": plan["labReadConsent"]["latestDecision"],
                "crossSolution": False,
                "crossRun": False,
                "targetTenantId": plan["target"]["tenantId"],
                "authorizingConsentSha256": (
                    record.get("consentSha256")
                    if status == "approved" and record
                    else None
                ),
            }
        target = require_locked_target(root, materialize_missing=False)
        setting = _load_primary_setting(target)
        if setting is None:
            lab_status, record, approved = (
                "requires-primary-setting-confirmation",
                None,
                set(),
            )
        else:
            record, lab_status = _load_lab_consent(target, setting)
            approved = (
                _approved_families(
                    record,
                    binding=_lab_binding(target, setting),
                )
                if record is not None
                else set()
            ) or set()
        run_snapshot = _current_binding(plan)
        snapshot_path = existing_artifact_path(root, CONSENT_FILE_NAME)
        try:
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            snapshot = None
        if (
            not isinstance(snapshot, dict)
            or snapshot.get("binding") != run_snapshot
            or snapshot.get("labConsentSha256")
            != (record.get("consentSha256") if record is not None else None)
        ):
            snapshot = None
        return {
            "status": lab_status,
            "approvedFamilies": sorted(approved),
            "consentScope": "lab-wide-across-solutions-and-runs",
            "labConsentPath": str(_lab_paths(target)[1]),
            "latestDecision": plan["labReadConsent"]["latestDecision"],
            "labConsentRecordedAt": (
                record.get("recordedAt") if record is not None else None
            ),
            "runSnapshot": {
                "status": "current" if snapshot is not None else "not-current",
                "binding": run_snapshot,
                "planSha256": plan["planSha256"],
                "queryHashesAreConsentBindings": False,
            },
            "families": {
                name: {
                    "status": "approved" if name in approved else "not-approved",
                    **(
                        _family_execution_status(
                            root,
                            plan["families"][name],
                        )
                        if name in approved
                        else {"executionStatus": "not-run"}
                    ),
                }
                for name in sorted(FAMILIES)
            },
            "planSha256": plan["planSha256"],
            "stale": lab_status == "stale",
        }
    except ValueError as exc:
        if "only available for Qualification" in str(exc):
            return {
                "status": "notApplicable",
                "approvedFamilies": [],
                "families": {
                    name: {
                        "status": "notApplicable",
                        "executionStatus": "not-run",
                    }
                    for name in sorted(FAMILIES)
                },
                "planSha256": None,
                "stale": False,
                "reason": "runtime query consent is Qualification-only",
            }
        return {
            "status": "unavailable",
            "approvedFamilies": [],
            "families": {
                name: {
                    "status": "unavailable",
                    "executionStatus": "not-run",
                }
                for name in sorted(FAMILIES)
            },
            "planSha256": None,
            "stale": False,
            "reason": str(exc),
        }
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return {
            "status": "unavailable",
            "approvedFamilies": [],
            "families": {
                name: {
                    "status": "unavailable",
                    "executionStatus": "not-run",
                }
                for name in sorted(FAMILIES)
            },
            "planSha256": None,
            "stale": False,
            "reason": str(exc),
        }


def require_runtime_query_consent(
    solution: str | Path,
    *,
    family: str,
    provider: str,
    source_provider: str = "azure-monitor-sdk",
    allow_legacy: bool = False,
) -> dict[str, Any] | None:
    root = Path(solution).expanduser().resolve()
    try:
        state, run_id = _run_context(root)
    except ValueError as exc:
        if allow_legacy and "workflow state does not exist" in str(exc):
            return None
        raise
    route = provider
    plan = build_runtime_query_plan(
        root,
        source_provider=source_provider,
    )
    if family not in FAMILIES:
        raise ValueError(f"unsupported runtime query family: {family}")
    if plan["families"][family]["status"] != "ready":
        raise ValueError(
            f"{family} has no complete current query inventory; runtime execution is blocked"
        )
    if plan["workflowProfile"] == "authoring":
        if family != "defenderXdrQueryFamily" or route != "graph":
            raise ValueError(
                "Authoring runtime validation is limited to explicitly approved "
                "Defender XDR Advanced Hunting queries"
            )
        authentication = plan["families"][family]["provider"]["authentication"]
        if authentication.get("classification") == "separate-interactive-sign-in-required":
            raise ValueError(
                "Advanced Hunting has no existing cached authentication for the "
                "explicit Authoring tenant; runtime-query consent does not "
                "authorize interactive sign-in"
            )
        record, authoring_status = _load_authoring_consent(root, plan)
        if (
            authoring_status != "approved"
            or record is None
            or record.get("approvedFamilies") != [family]
            or record.get("authorizesRuntimeQueries") is not True
        ):
            raise ValueError(
                "one-run Authoring Advanced Hunting consent is not current "
                f"(status: {authoring_status}); review the exact current query plan"
            )
        binding = _current_binding(plan)
        run_snapshot = {
            "schemaVersion": PLAN_SCHEMA_VERSION,
            "status": "approved",
            "consentType": "run-bound-authoring-runtime-query-authorization-snapshot",
            "workflowProfile": "authoring",
            "family": family,
            "provider": route,
            "authoringConsentSha256": record["consentSha256"],
            "authoringConsentActor": record["actor"],
            "authoringConsentRecordedAt": record["recordedAt"],
            "approvedFamilies": [family],
            "binding": binding,
            "planSha256": plan["planSha256"],
            "queryHashesAreConsentBindings": True,
            "interactiveAuthenticationAuthorized": False,
            "sourceSdkValidationAuthorized": False,
            "permissionChangesAuthorized": False,
            "environmentWritesAuthorized": False,
            "providerExecutionSucceeded": False,
            "recordedAt": datetime.now(timezone.utc).isoformat(),
        }
        snapshot_path = artifact_path(root, CONSENT_FILE_NAME, create_parent=True)
        write_json_artifact(root, snapshot_path, run_snapshot)
        return {
            "status": "approved",
            "family": family,
            "provider": route,
            "workflowProfile": "authoring",
            "planSha256": plan["planSha256"],
            "binding": binding,
            "consentScope": "one-run-authoring-query-only",
            "authoringConsentSha256": record["consentSha256"],
            "runSnapshotPath": str(snapshot_path),
            "authenticationClassification": authentication.get("classification"),
            "interactiveAuthenticationAuthorized": False,
            "environmentWritesAuthorized": False,
        }
    target = require_locked_target(root, materialize_missing=False)
    primary_setting = _load_primary_setting(target)
    if primary_setting is None:
        raise ValueError(
            "the primary lab setting has not been explicitly confirmed; "
            "runtime queries are not approved"
        )
    record, lab_status = _load_lab_consent(target, primary_setting)
    approved = (
        _approved_families(
            record,
            binding=_lab_binding(target, primary_setting),
        )
        if record is not None
        else None
    )
    if approved is None:
        raise ValueError(
            "shared lab read-only runtime-query consent is not approved "
            f"(status: {lab_status}); review the current bounded plan and obtain "
            "explicit lab approval"
        )
    if family not in approved:
        raise ValueError(f"runtime-query consent does not approve {family}")
    planned_provider = plan["families"][family]["provider"]["provider"]
    if route != planned_provider:
        raise ValueError(
            f"runtime-query consent is bound to provider {planned_provider}, not {route}; "
            "refresh the plan and obtain renewed explicit consent"
        )
    authentication = plan["families"][family]["provider"]["authentication"]
    if authentication.get("classification") == "separate-interactive-sign-in-required":
        raise ValueError(
            f"{route} has no existing cached authentication for the locked tenant; "
            "runtime-query consent does not authorize interactive sign-in"
        )
    binding = _current_binding(plan)
    run_snapshot = {
        "schemaVersion": PLAN_SCHEMA_VERSION,
        "status": "derived-from-lab-consent",
        "consentType": "run-bound-runtime-query-authorization-snapshot",
        "labConsentSha256": record["consentSha256"],
        "labConsentRecordedAt": record["recordedAt"],
        "labConsentActor": record["actor"],
        "approvedFamilies": sorted(approved),
        "binding": binding,
        "planSha256": plan["planSha256"],
        "querySnapshotsAreNotConsentBindings": True,
        "interactiveAuthenticationAuthorized": False,
        "adminConsentAuthorized": False,
        "permissionChangesAuthorized": False,
        "environmentWritesAuthorized": False,
        "providerExecutionSucceeded": False,
        "recordedAt": datetime.now(timezone.utc).isoformat(),
    }
    snapshot_path = artifact_path(root, CONSENT_FILE_NAME, create_parent=True)
    write_json_artifact(root, snapshot_path, run_snapshot)
    return {
        "status": "approved",
        "family": family,
        "provider": route,
        "planSha256": plan["planSha256"],
        "binding": binding,
        "consentScope": "lab-wide-across-solutions-and-runs",
        "labConsentSha256": record["consentSha256"],
        "runSnapshotPath": str(snapshot_path),
        "authenticationClassification": authentication.get("classification"),
        "interactiveAuthenticationAuthorized": False,
        "environmentWritesAuthorized": False,
    }
