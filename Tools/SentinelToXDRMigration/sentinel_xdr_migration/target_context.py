from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from .artifacts import artifact_path, existing_artifact_path
from .onboarding import CONFIG_NAME, _read_json, _state_dir, configure_workspace


TARGET_FILE_NAME = "qualification-target.json"
DIAGNOSTICS_FILE_NAME = "qualification-diagnostics.json"
REPAIR_FILE_NAME = "qualification-repair.json"
TARGET_SCHEMA_VERSION = "1.0.0"

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _guid(value: str, field: str) -> str:
    try:
        return str(uuid.UUID(value.strip()))
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"{field} must be a GUID") from exc


def workspace_identity(workspace_resource_id: str) -> dict[str, str]:
    normalized = workspace_resource_id.strip().rstrip("/")
    parts = normalized.split("/")
    if (
        len(parts) != 9
        or parts[1].lower() != "subscriptions"
        or parts[3].lower() != "resourcegroups"
        or parts[5].lower() != "providers"
        or parts[6].lower() != "microsoft.operationalinsights"
        or parts[7].lower() != "workspaces"
        or not parts[8]
    ):
        raise ValueError(
            "workspace-resource-id must be a full Log Analytics workspace ARM ID"
        )
    return {
        "workspaceResourceId": normalized,
        "subscriptionId": _guid(parts[2], "workspace subscription ID"),
        "resourceGroup": parts[4],
        "workspaceName": parts[8],
    }


def build_target(
    *,
    tenant_id: str,
    subscription_id: str,
    workspace_resource_id: str,
    workspace_customer_id: str,
) -> dict[str, Any]:
    workspace = workspace_identity(workspace_resource_id)
    normalized_subscription = _guid(subscription_id, "subscription ID")
    if workspace["subscriptionId"] != normalized_subscription:
        raise ValueError(
            "workspace ARM ID subscription does not match subscription-id"
        )
    return {
        "schemaVersion": TARGET_SCHEMA_VERSION,
        "locked": True,
        "tenantId": _guid(tenant_id, "tenant ID"),
        "subscriptionId": normalized_subscription,
        "workspaceResourceId": workspace["workspaceResourceId"],
        "workspaceCustomerId": _guid(
            workspace_customer_id, "workspace customer ID"
        ),
        "resourceGroup": workspace["resourceGroup"],
        "workspaceName": workspace["workspaceName"],
    }


def _target_from_context(context: dict[str, Any]) -> dict[str, Any]:
    required = (
        "tenantId",
        "subscriptionId",
        "workspaceResourceId",
        "workspaceCustomerId",
    )
    missing = [name for name in required if not context.get(name)]
    if missing or context.get("targetContextLocked") is not True:
        raise ValueError(
            "qualification target is not locked; initialize or repair it with "
            f"all required identifiers ({', '.join(required)})"
        )
    return build_target(
        tenant_id=context["tenantId"],
        subscription_id=context["subscriptionId"],
        workspace_resource_id=context["workspaceResourceId"],
        workspace_customer_id=context["workspaceCustomerId"],
    )


def write_target(solution: str | Path, target: dict[str, Any]) -> Path:
    path = artifact_path(solution, TARGET_FILE_NAME, create_parent=True)
    path.write_text(
        json.dumps(target, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def require_locked_target(
    solution: str | Path,
    *,
    tenant_id: str | None = None,
    subscription_id: str | None = None,
    workspace_resource_id: str | None = None,
    workspace_customer_id: str | None = None,
) -> dict[str, Any]:
    state_path = existing_artifact_path(solution, "workflow-state.json")
    if not state_path.is_file():
        raise ValueError("qualification workflow state does not exist")
    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    context = state.get("context") or {}
    if context.get("workflowProfile") != "qualification":
        raise ValueError("live operations require a qualification workflow")
    target = _target_from_context(context)
    supplied = {
        "tenantId": tenant_id,
        "subscriptionId": subscription_id,
        "workspaceResourceId": (
            workspace_resource_id.strip().rstrip("/")
            if workspace_resource_id
            else None
        ),
        "workspaceCustomerId": workspace_customer_id,
    }
    normalizers = {
        "tenantId": lambda value: _guid(value, "tenant ID"),
        "subscriptionId": lambda value: _guid(value, "subscription ID"),
        "workspaceResourceId": lambda value: workspace_identity(value)[
            "workspaceResourceId"
        ],
        "workspaceCustomerId": lambda value: _guid(
            value, "workspace customer ID"
        ),
    }
    for name, value in supplied.items():
        if value is None:
            continue
        normalized = normalizers[name](value)
        expected = target[name]
        comparison = (
            normalized.lower() == expected.lower()
            if name == "workspaceResourceId"
            else normalized == expected
        )
        if not comparison:
            raise ValueError(
                f"{name} does not match the locked qualification target"
            )
    target_path = artifact_path(solution, TARGET_FILE_NAME)
    if target_path.is_file():
        recorded = json.loads(target_path.read_text(encoding="utf-8-sig"))
        for field in (
            "tenantId",
            "subscriptionId",
            "workspaceResourceId",
            "workspaceCustomerId",
        ):
            if str(recorded.get(field) or "").lower() != str(target[field]).lower():
                raise ValueError(
                    "qualification target artifact does not match workflow state"
                )
    else:
        write_target(solution, target)
    target["targetPath"] = str(target_path)
    return target


def _az_executable() -> str:
    executable = shutil.which("az.cmd" if os.name == "nt" else "az")
    if not executable:
        executable = shutil.which("az")
    if not executable:
        raise RuntimeError("Azure CLI is not installed or available on PATH")
    return executable


def _run_az(
    arguments: Sequence[str],
    *,
    runner: CommandRunner = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    return runner(
        [_az_executable(), *arguments, "--output", "json", "--only-show-errors"],
        capture_output=True,
        text=True,
        check=False,
    )


def _json_output(result: subprocess.CompletedProcess[str]) -> Any:
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "").strip())
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Azure CLI returned invalid JSON") from exc


def diagnose_target(
    solution: str | Path,
    *,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    target = require_locked_target(solution)
    account = _json_output(_run_az(("account", "show"), runner=runner))
    if _guid(account.get("tenantId", ""), "authenticated tenant ID") != target["tenantId"]:
        status = "tenant-mismatch"
        detail = "authenticated Azure tenant does not match the locked target"
        proposed = None
    elif _guid(account.get("id", ""), "authenticated subscription ID") != target[
        "subscriptionId"
    ]:
        status = "subscription-mismatch"
        detail = "active Azure subscription does not match the locked target"
        proposed = None
    else:
        resource = _run_az(
            (
                "resource",
                "show",
                "--ids",
                target["workspaceResourceId"],
                "--api-version",
                "2023-09-01",
            ),
            runner=runner,
        )
        if resource.returncode == 0:
            workspace = _json_output(resource)
            actual_customer = str(
                ((workspace.get("properties") or {}).get("customerId") or "")
            ).strip()
            if not actual_customer:
                status = "blocked"
                detail = "the exact workspace response did not include its customer ID"
            elif _guid(actual_customer, "workspace customer ID") != target[
                "workspaceCustomerId"
            ]:
                status = "workspace-identity-mismatch"
                detail = (
                    "the exact ARM resource customer ID does not match the locked target"
                )
            else:
                status = "ready"
                detail = "the exact locked workspace ARM resource is accessible"
            proposed = None
        else:
            escaped_customer = target["workspaceCustomerId"].replace("'", "''")
            query = (
                "resources "
                "| where type =~ 'microsoft.operationalinsights/workspaces' "
                f"| where tostring(properties.customerId) =~ '{escaped_customer}' "
                "| project id, name, resourceGroup, subscriptionId, "
                "customerId=tostring(properties.customerId)"
            )
            graph = _json_output(
                _run_az(
                    (
                        "graph",
                        "query",
                        "--subscriptions",
                        target["subscriptionId"],
                        "--first",
                        "2",
                        "-q",
                        query,
                    ),
                    runner=runner,
                )
            )
            rows = graph.get("data") if isinstance(graph, dict) else None
            rows = rows if isinstance(rows, list) else []
            if len(rows) == 1:
                row = rows[0]
                proposed = build_target(
                    tenant_id=target["tenantId"],
                    subscription_id=target["subscriptionId"],
                    workspace_resource_id=str(row.get("id") or ""),
                    workspace_customer_id=target["workspaceCustomerId"],
                )
                status = (
                    "repair-available"
                    if proposed["workspaceResourceId"].lower()
                    != target["workspaceResourceId"].lower()
                    else "blocked"
                )
                detail = (
                    "the locked ARM path is stale; one exact customer-ID match "
                    "was found in the locked subscription"
                    if status == "repair-available"
                    else "the exact workspace exists but the ARM read remains blocked"
                )
            else:
                proposed = None
                status = "blocked"
                detail = (
                    "the locked workspace ARM path failed and the exact customer-ID "
                    f"lookup returned {len(rows)} matches"
                )
    report = {
        "checkedAt": _utc_now(),
        "status": status,
        "detail": detail,
        "target": target,
        "proposedTarget": proposed,
        "writesPerformed": False,
    }
    path = artifact_path(solution, DIAGNOSTICS_FILE_NAME, create_parent=True)
    report["reportPath"] = str(path)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def repair_target(
    solution: str | Path,
    *,
    approve_target_update: bool,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    if not approve_target_update:
        raise ValueError("--approve-target-update is required")
    diagnostics_path = artifact_path(solution, DIAGNOSTICS_FILE_NAME)
    if not diagnostics_path.is_file():
        raise ValueError("qualification diagnostics do not exist")
    diagnostics = json.loads(diagnostics_path.read_text(encoding="utf-8-sig"))
    if diagnostics.get("status") != "repair-available":
        raise ValueError("diagnostics do not contain an approved repair candidate")
    current = require_locked_target(solution)
    recorded = diagnostics.get("target") or {}
    for field in (
        "tenantId",
        "subscriptionId",
        "workspaceResourceId",
        "workspaceCustomerId",
    ):
        if str(current[field]).lower() != str(recorded.get(field) or "").lower():
            raise ValueError("qualification target changed after diagnostics; rerun diagnosis")
    proposed = diagnostics.get("proposedTarget") or {}
    repaired = build_target(
        tenant_id=proposed.get("tenantId", ""),
        subscription_id=proposed.get("subscriptionId", ""),
        workspace_resource_id=proposed.get("workspaceResourceId", ""),
        workspace_customer_id=proposed.get("workspaceCustomerId", ""),
    )
    for field in ("tenantId", "subscriptionId", "workspaceCustomerId"):
        if repaired[field] != current[field]:
            raise ValueError(f"repair cannot change locked {field}")

    from .workflow import _load, _write

    state_path, state = _load(solution)
    context = state["context"]
    context.update(
        {
            "tenantId": repaired["tenantId"],
            "subscriptionId": repaired["subscriptionId"],
            "workspaceResourceId": repaired["workspaceResourceId"],
            "workspaceCustomerId": repaired["workspaceCustomerId"],
            "targetContextLocked": True,
        }
    )
    deployment = state["stages"]["deployment"]
    if deployment["status"] == "blocked":
        deployment.update(
            {
                "status": "pending",
                "startedAt": None,
                "completedAt": None,
                "message": None,
                "artifacts": {},
                "evidence": [],
            }
        )
        state["workflowStatus"] = "inProgress"
    _write(state_path, state)
    target_path = write_target(solution, repaired)
    configure_workspace(
        repaired["workspaceResourceId"],
        workspace_customer_id=repaired["workspaceCustomerId"],
        tenant_id=repaired["tenantId"],
        subscription_id=repaired["subscriptionId"],
        state_dir=state_dir,
    )
    report = {
        "repairedAt": _utc_now(),
        "status": "repaired",
        "previousTarget": current,
        "target": repaired,
        "targetPath": str(target_path),
        "workflowStatePath": str(state_path),
        "writesPerformed": ["local-config", "workflow-state", "target-context"],
    }
    path = artifact_path(solution, REPAIR_FILE_NAME, create_parent=True)
    report["reportPath"] = str(path)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
