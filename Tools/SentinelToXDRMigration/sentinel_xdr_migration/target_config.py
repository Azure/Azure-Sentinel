from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

from .target_context import resolve_workspace_customer_id, workspace_identity

ENV_FILE_NAME = ".env"
ENV_KEYS = {
    "AZURE_TENANT_ID": "tenantId",
    "SENTINEL_WORKSPACE_RESOURCE_ID": "workspaceResourceId",
}


def _normalize_env_value(key: str, value: str, line_number: int) -> str:
    if not value or value != value.strip():
        raise ValueError(
            f"{ENV_FILE_NAME}:{line_number}: {key} must have a non-empty value "
            "without surrounding whitespace"
        )
    if any(character.isspace() for character in value) or any(
        character in value for character in ("$", "`", ";", "#", "'", '"', "\\")
    ):
        raise ValueError(
            f"{ENV_FILE_NAME}:{line_number}: {key} contains unsupported syntax; "
            "enter the literal identifier only (no quotes, expansion, or commands)"
        )
    if key == "AZURE_TENANT_ID":
        if not re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            value,
        ):
            raise ValueError(
                f"{ENV_FILE_NAME}:{line_number}: AZURE_TENANT_ID must be a tenant GUID; "
                "replace the placeholder in the example file"
            )
        return str(uuid.UUID(value))
    try:
        workspace = workspace_identity(value)
    except ValueError as exc:
        raise ValueError(
            f"{ENV_FILE_NAME}:{line_number}: SENTINEL_WORKSPACE_RESOURCE_ID must be "
            "a full Log Analytics workspace ARM ID; replace the placeholder in "
            "the example file"
        ) from exc
    parts = value.split("/")
    if not re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        parts[2],
    ) or any(
        not re.fullmatch(r"[A-Za-z0-9_.()\-]+", part)
        for part in (workspace["resourceGroup"], workspace["workspaceName"])
    ):
        raise ValueError(
            f"{ENV_FILE_NAME}:{line_number}: SENTINEL_WORKSPACE_RESOURCE_ID contains "
            "an invalid subscription, resource-group, or workspace segment"
        )
    if workspace["workspaceResourceId"] != value:
        raise ValueError(
            f"{ENV_FILE_NAME}:{line_number}: SENTINEL_WORKSPACE_RESOURCE_ID must not "
            "have surrounding whitespace or a trailing slash"
        )
    return value


def read_solution_target_config(solution: str | Path) -> dict[str, str]:
    root = Path(solution).expanduser().resolve()
    path = root / ENV_FILE_NAME
    if path.is_symlink():
        raise ValueError("solution .env must not be a symlink")
    if not path.exists():
        return {}
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError("cannot read solution .env as UTF-8 text") from exc

    values: dict[str, str] = {}
    for line_number, original in enumerate(lines, start=1):
        if not original.strip() or original.lstrip().startswith("#"):
            continue
        key, separator, value = original.partition("=")
        if not separator or key not in ENV_KEYS:
            raise ValueError(
                f"{ENV_FILE_NAME}:{line_number}: unsupported entry; use only "
                "AZURE_TENANT_ID and SENTINEL_WORKSPACE_RESOURCE_ID assignments"
            )
        if key in values:
            raise ValueError(f"{ENV_FILE_NAME}:{line_number}: duplicate {key}")
        values[key] = _normalize_env_value(key, value, line_number)
    return {ENV_KEYS[key]: value for key, value in values.items()}


def _same_value(name: str, left: str, right: str) -> bool:
    if name == "workspaceResourceId":
        return left.rstrip("/").casefold() == right.rstrip("/").casefold()
    try:
        return str(uuid.UUID(left)) == str(uuid.UUID(right))
    except ValueError:
        return left.casefold() == right.casefold()


def resolve_qualification_target(
    solution: str | Path,
    *,
    tenant_id: str | None = None,
    subscription_id: str | None = None,
    workspace_resource_id: str | None = None,
    workspace_customer_id: str | None = None,
    confirm_configured_target: bool = False,
    locked_context: dict[str, Any] | None = None,
) -> dict[str, str]:
    configured = read_solution_target_config(solution)
    locked = locked_context or {}
    locked_target = {
        name: str(locked[name])
        for name in (
            "tenantId",
            "subscriptionId",
            "workspaceResourceId",
            "workspaceCustomerId",
        )
        if locked.get(name)
    }

    supplied = {
        "tenantId": tenant_id,
        "subscriptionId": subscription_id,
        "workspaceResourceId": workspace_resource_id,
        "workspaceCustomerId": workspace_customer_id,
    }
    for name in ("tenantId", "workspaceResourceId"):
        configured_value = configured.get(name)
        if configured_value and supplied[name] and not _same_value(
            name, configured_value, supplied[name]
        ):
            raise ValueError(
                f"command-line {name} conflicts with solution .env; reconcile the "
                "values explicitly before initializing"
            )
        locked_value = locked_target.get(name)
        if locked_value and configured_value and not _same_value(
            name, locked_value, configured_value
        ):
            raise ValueError(
                f"solution .env {name} conflicts with the locked Qualification run; "
                "the run target is authoritative and cannot be changed by editing .env"
            )

    explicit_target = bool(tenant_id and workspace_resource_id)
    if (
        configured
        and not locked_target
        and not confirm_configured_target
        and not explicit_target
    ):
        raise ValueError(
            "solution .env contains a Qualification target. Review it with "
            "`sentinel-xdr-migration doctor --solution <solution>` and pass "
            "`--confirm-configured-target`, or explicitly supply both "
            "`--tenant-id` and `--workspace-resource-id`"
        )
    if confirm_configured_target and not configured and not locked_target:
        raise ValueError(
            "--confirm-configured-target requires a configured solution .env"
        )

    resolved: dict[str, str] = {}
    for name in (
        "tenantId",
        "subscriptionId",
        "workspaceResourceId",
        "workspaceCustomerId",
    ):
        value = supplied[name] or locked_target.get(name)
        if name in {"tenantId", "workspaceResourceId"}:
            value = value or configured.get(name)
        if value:
            resolved[name] = str(value)

    if "workspaceResourceId" in resolved:
        workspace = workspace_identity(resolved["workspaceResourceId"])
        derived_subscription = workspace["subscriptionId"]
        if resolved.get("subscriptionId") and not _same_value(
            "subscriptionId", resolved["subscriptionId"], derived_subscription
        ):
            raise ValueError(
                "workspace ARM ID subscription does not match subscription-id"
            )
        resolved["subscriptionId"] = derived_subscription

    for name, value in locked_target.items():
        current = resolved.get(name)
        if current and not _same_value(name, value, current):
            raise ValueError(
                f"{name} does not match the locked Qualification target; "
                "the existing run cannot be retargeted"
            )
        resolved[name] = value

    missing = [
        name
        for name in ("tenantId", "subscriptionId", "workspaceResourceId")
        if not resolved.get(name)
    ]
    if missing:
        raise ValueError(
            "Qualification requires AZURE_TENANT_ID and "
            "SENTINEL_WORKSPACE_RESOURCE_ID in solution .env, or explicit "
            "tenant/workspace command-line values; missing "
            + ", ".join(missing)
        )

    if not resolved.get("workspaceCustomerId"):
        resolved["workspaceCustomerId"] = resolve_workspace_customer_id(
            resolved["tenantId"],
            resolved["workspaceResourceId"],
        )
    return resolved


def doctor_solution_target(solution: str | Path) -> dict[str, Any]:
    target = read_solution_target_config(solution)
    config_path = Path(solution).expanduser().resolve() / ENV_FILE_NAME
    if not target:
        return {"status": "notConfigured", "configPath": str(config_path)}
    workspace = target.get("workspaceResourceId")
    return {
        "status": "configured",
        "configPath": str(config_path),
        "tenantId": target.get("tenantId"),
        "workspaceResourceId": workspace,
        "subscriptionId": (
            workspace_identity(workspace)["subscriptionId"] if workspace else None
        ),
        "workspaceCustomerId": "resolved only after explicit target confirmation",
    }
