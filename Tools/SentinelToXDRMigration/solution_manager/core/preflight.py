from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from solution_manager.core.artifacts import existing_artifact_path
from solution_manager.core.onboarding import _command_status, _state_dir
from solution_manager.core.target_context import require_locked_target
from solution_manager.qualification.graph_client_config import (
    azure_cli_profile,
    configured_azure_cli_profile,
)


PREFLIGHT_API_VERSION = "1.0.0"
PREFLIGHT_STATUSES = {
    "passed",
    "failed",
    "unknown",
    "notRun",
    "notApplicable",
}
TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
WRITE_COMMAND_PATTERN = re.compile(
    r"(?im)^\s*\.(?:set|drop|create|alter|delete|ingest|clear|rename|move)\b"
)
READ_SCOPES = {
    "sentinel-source-table-read": ("logAnalytics", "table"),
    "sentinel-source-query-read": ("logAnalytics", "query"),
    "converted-graph-table-read": ("graphAdvancedHunting", "table"),
    "converted-graph-query-read": ("graphAdvancedHunting", "query"),
}

ReadExecutor = Callable[[Mapping[str, Any]], Mapping[str, Any]]


def _record(name: str, status: str, **fields: Any) -> dict[str, Any]:
    if status not in PREFLIGHT_STATUSES:
        raise ValueError(f"unsupported preflight status: {status}")
    return {"name": name, "status": status, **fields}


def _target_record(status: str, target: Mapping[str, Any] | None = None, reason=None):
    fields: dict[str, Any] = {"reason": reason}
    if target is not None:
        fields["identity"] = {
            key: target[key]
            for key in (
                "tenantId",
                "subscriptionId",
                "workspaceResourceId",
                "workspaceCustomerId",
            )
        }
    return _record("lockedQualificationTarget", status, **fields)


def _target_failure_reason(error: Exception) -> str:
    message = str(error).casefold()
    if "does not match" in message or "mismatch" in message:
        return "locked-target-identity-mismatch"
    if "does not exist" in message:
        return "qualification-workflow-state-missing"
    if "locked" in message or "missing" in message or "required" in message:
        return "locked-target-incomplete"
    return "locked-target-invalid"


def _validate_read_query(query: str, field: str) -> None:
    if not query.strip():
        raise ValueError(f"{field} must not be empty")
    if ";" in query or WRITE_COMMAND_PATTERN.search(query):
        raise ValueError(f"{field} must contain one read-only KQL query")


def _provider_record(provider: str, *, applicable: bool) -> dict[str, Any]:
    initial = "notRun" if applicable else "notApplicable"
    return {
        "provider": provider,
        "authentication": _record("authentication", initial),
        "authorization": _record("authorization", initial),
        "tableAccess": _record("tableAccess", initial),
        "queryExecution": _record("queryExecution", initial),
    }


def _response_status(
    response: Mapping[str, Any] | None, *, exception: Exception | None = None
) -> tuple[str, str]:
    if exception is not None:
        status_code = getattr(
            exception, "status_code", getattr(exception, "code", None)
        )
        if status_code == 401:
            return "failed", "authentication-denied"
        if status_code == 403:
            return "failed", "authorization-denied"
        if status_code == 429:
            return "unknown", "throttled"
        return "unknown", "provider-unavailable"

    assert response is not None
    status_code = response.get("statusCode", response.get("status_code"))
    failure_kind = str(response.get("failureKind") or "").casefold()
    if status_code == 401:
        return "failed", "authentication-denied"
    if status_code == 403:
        return "failed", "authorization-denied"
    if status_code == 429:
        return "unknown", "throttled"
    if isinstance(status_code, int) and status_code >= 500:
        return "unknown", "provider-unavailable"
    if (
        response.get("tableAvailable") is False
        or failure_kind in {"missing-table", "table-not-found"}
        or status_code == 404
    ):
        return "failed", "table-unavailable"
    if response.get("ok") is True:
        return "passed", "read-succeeded"
    if failure_kind in {"query", "kql"} or status_code == 400:
        return "failed", "query-rejected"
    return "unknown", "provider-result-inconclusive"


def _run_read(
    *,
    scope: str,
    provider: str,
    operation: str,
    query: str,
    target: Mapping[str, Any],
    executor: ReadExecutor,
) -> dict[str, Any]:
    request = {
        "scope": scope,
        "provider": provider,
        "operation": operation,
        "query": query,
        "target": {
            key: target[key]
            for key in (
                "tenantId",
                "subscriptionId",
                "workspaceResourceId",
                "workspaceCustomerId",
            )
        },
    }
    try:
        response = executor(request)
    except Exception as exc:
        status, reason = _response_status(None, exception=exc)
        return {
            "status": status,
            "reason": reason,
            "querySha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
        }
    if not isinstance(response, Mapping):
        return {
            "status": "unknown",
            "reason": "provider-result-inconclusive",
            "querySha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
        }
    status, reason = _response_status(response)
    return {
        "status": status,
        "reason": reason,
        "querySha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
    }


def _apply_read_result(
    provider_record: dict[str, Any], operation: str, result: Mapping[str, Any]
) -> None:
    key = "tableAccess" if operation == "table" else "queryExecution"
    provider_record[key] = _record(key, result["status"], reason=result["reason"])
    if result["status"] == "passed":
        provider_record["authentication"] = _record(
            "authentication", "passed", reason="provider-read-succeeded"
        )
        provider_record["authorization"] = _record(
            "authorization", "passed", reason="provider-read-succeeded"
        )
    elif result["reason"] == "authentication-denied":
        provider_record["authentication"] = _record(
            "authentication", "failed", reason=result["reason"]
        )
    elif result["reason"] == "authorization-denied":
        provider_record["authorization"] = _record(
            "authorization", "failed", reason=result["reason"]
        )


def validate_preflight_report(report: Mapping[str, Any]) -> dict[str, Any]:
    """Validate this module's integration API record without claiming a W2 schema."""
    required = {
        "apiVersion",
        "profile",
        "overallStatus",
        "localTools",
        "target",
        "providers",
        "deploymentPermissions",
        "safety",
    }
    if not isinstance(report, Mapping) or set(report) != required:
        raise ValueError("preflight report has an invalid top-level shape")
    if report["apiVersion"] != PREFLIGHT_API_VERSION:
        raise ValueError("unsupported preflight API version")
    if report["profile"] not in {"authoring", "qualification", "unknown"}:
        raise ValueError("preflight report has an invalid workflow profile")
    local_tools = report["localTools"]
    if not isinstance(local_tools, Mapping) or set(local_tools) != {
        "python",
        "azureCli",
    }:
        raise ValueError("preflight local tool checks are incomplete")
    for value in local_tools.values():
        if not isinstance(value, Mapping) or value.get("status") not in PREFLIGHT_STATUSES:
            raise ValueError("preflight local tool has an invalid status")
    target = report["target"]
    if not isinstance(target, Mapping) or target.get("status") not in PREFLIGHT_STATUSES:
        raise ValueError("preflight target has an invalid status")
    if report["overallStatus"] not in PREFLIGHT_STATUSES:
        raise ValueError("preflight report has an invalid overall status")
    providers = report["providers"]
    if not isinstance(providers, Mapping) or set(providers) != {
        "source",
        "converted",
    }:
        raise ValueError("preflight provider records are incomplete")
    expected_providers = {
        "source": "logAnalytics",
        "converted": "graphAdvancedHunting",
    }
    for key, provider in providers.items():
        if not isinstance(provider, Mapping) or provider.get("provider") != expected_providers[key]:
            raise ValueError("preflight provider family is invalid")
        for check in (
            "authentication",
            "authorization",
            "tableAccess",
            "queryExecution",
        ):
            if (
                check not in provider
                or not isinstance(provider[check], Mapping)
                or provider[check].get("status") not in PREFLIGHT_STATUSES
            ):
                raise ValueError("preflight provider check has an invalid status")
    deployment = report["deploymentPermissions"]
    if not isinstance(deployment, Mapping) or deployment.get("status") not in PREFLIGHT_STATUSES:
        raise ValueError("deployment permission check has an invalid status")
    if not isinstance(report["safety"], Mapping):
        raise ValueError("preflight safety record is invalid")
    if report["safety"] != {
        "writesPerformed": False,
        "workspaceEnumerationPerformed": False,
        "newAuthenticationPerformed": False,
    }:
        raise ValueError("preflight safety record is invalid")
    return dict(report)


def run_preflight(
    solution: str | Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    tenant_id: str | None = None,
    subscription_id: str | None = None,
    workspace_resource_id: str | None = None,
    workspace_customer_id: str | None = None,
    source_table: str | None = None,
    source_query: str | None = None,
    converted_table: str | None = None,
    converted_query: str | None = None,
    read_executor: ReadExecutor | None = None,
) -> dict[str, Any]:
    """Collect local prerequisites and optional, explicitly scoped read evidence.

    Runtime providers are never called directly. Supplying an executor and
    individual named read inputs is the only way this API dispatches a read.
    """
    root = Path(solution).expanduser().resolve()
    profile = "unknown"
    target_record = _target_record("unknown", reason="workflow-state-not-found")
    target: dict[str, Any] | None = None
    try:
        state_path = existing_artifact_path(root, "workflow-state.json")
    except (OSError, ValueError):
        state_path = None
        target_record = _target_record("failed", reason="workflow-state-invalid")
    if state_path is not None and state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            state = None
            target_record = _target_record("failed", reason="workflow-state-invalid")
        if isinstance(state, dict):
            context = state.get("context")
            profile = (
                context.get("workflowProfile", "unknown")
                if isinstance(context, dict)
                else "unknown"
            )
            if profile == "qualification":
                try:
                    target = require_locked_target(
                        root,
                        tenant_id=tenant_id,
                        subscription_id=subscription_id,
                        workspace_resource_id=workspace_resource_id,
                        workspace_customer_id=workspace_customer_id,
                        materialize_missing=False,
                    )
                except (OSError, ValueError) as exc:
                    target_record = _target_record(
                        "failed", reason=_target_failure_reason(exc)
                    )
                else:
                    target_record = _target_record("passed", target)
            elif profile == "authoring":
                target_record = _target_record(
                    "notApplicable",
                    reason="authoring-does-not-require-a-workspace",
                )
            else:
                target_record = _target_record(
                    "unknown", reason="workflow-profile-is-not-explicit"
                )

    qualification = profile == "qualification"
    python_supported = sys.version_info[:2] in {(3, 11), (3, 12)}
    configured_profile = (
        configured_azure_cli_profile(_state_dir()) if qualification else None
    )
    with azure_cli_profile(configured_profile):
        azure_cli = (
            _command_status(
                "azureCli",
                ("az", "version", "--output", "none"),
                runner=runner,
                azure_config_dir=configured_profile,
            )
            if qualification
            else _record(
                "azureCli",
                "notApplicable",
                detail="Azure CLI is not required for offline authoring",
            )
        )
    local_tools = {
        "python": _record(
            "python",
            "passed" if python_supported else "failed",
            version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            requiredVersions=["3.11", "3.12"],
        ),
        "azureCli": azure_cli,
    }
    providers = {
        "source": _provider_record("logAnalytics", applicable=qualification),
        "converted": _provider_record(
            "graphAdvancedHunting", applicable=qualification
        ),
    }

    requested_reads = (
        (
            "source_table",
            source_table,
            "sentinel-source-table-read",
            "logAnalytics",
            "table",
            "source",
        ),
        (
            "source_query",
            source_query,
            "sentinel-source-query-read",
            "logAnalytics",
            "query",
            "source",
        ),
        (
            "converted_table",
            converted_table,
            "converted-graph-table-read",
            "graphAdvancedHunting",
            "table",
            "converted",
        ),
        (
            "converted_query",
            converted_query,
            "converted-graph-query-read",
            "graphAdvancedHunting",
            "query",
            "converted",
        ),
    )
    for input_name, requested, scope, provider, operation, provider_key in requested_reads:
        if not requested:
            continue
        if scope not in READ_SCOPES or READ_SCOPES[scope] != (provider, operation):
            raise ValueError("preflight read scope does not match its provider")
        if operation == "table":
            if not TABLE_NAME_PATTERN.fullmatch(requested):
                raise ValueError(f"{input_name} must be one exact table name")
            query = f"{requested} | take 0"
        else:
            _validate_read_query(requested, input_name)
            query = requested
        if read_executor is None or target is None:
            result = {
                "status": "notRun",
                "reason": (
                    "explicit-read-executor-not-provided"
                    if read_executor is None
                    else "locked-target-not-valid"
                ),
                "querySha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
            }
        else:
            result = _run_read(
                scope=scope,
                provider=provider,
                operation=operation,
                query=query,
                target=target,
                executor=read_executor,
            )
        _apply_read_result(providers[provider_key], operation, result)
        check_key = "tableAccess" if operation == "table" else "queryExecution"
        providers[provider_key][check_key]["querySha256"] = result["querySha256"]

    deployment_status = (
        "notApplicable" if profile == "authoring" else "unknown"
    )
    deployment_reason = (
        "authoring-does-not-require-deployment-permissions"
        if profile == "authoring"
        else "not-probed-no-deployment-or-write-checks"
    )
    deployment_permissions = _record(
        "deploymentPermissions", deployment_status, reason=deployment_reason
    )

    component_statuses = [
        local_tools["python"]["status"],
        local_tools["azureCli"]["status"],
        target_record["status"],
        deployment_permissions["status"],
        *(
            provider[check]["status"]
            for provider in providers.values()
            for check in (
                "authentication",
                "authorization",
                "tableAccess",
                "queryExecution",
            )
        ),
    ]
    if "failed" in component_statuses:
        overall = "failed"
    elif all(status in {"passed", "notApplicable"} for status in component_statuses):
        overall = "passed"
    elif all(status in {"notRun", "notApplicable"} for status in component_statuses):
        overall = "notRun"
    else:
        overall = "unknown"

    report = {
        "apiVersion": PREFLIGHT_API_VERSION,
        "profile": profile,
        "overallStatus": overall,
        "localTools": local_tools,
        "target": target_record,
        "providers": providers,
        "deploymentPermissions": deployment_permissions,
        "safety": {
            "writesPerformed": False,
            "workspaceEnumerationPerformed": False,
            "newAuthenticationPerformed": False,
        },
    }
    return validate_preflight_report(report)
