from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from . import __version__

LOG_ANALYTICS_RESOURCE = "https://api.loganalytics.io"
GRAPH_SCOPE = "https://graph.microsoft.com/ThreatHunting.Read.All"
GRAPH_CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
DEFAULT_STATE_DIR = Path.home() / ".sentinel-xdr-migration"
AUTH_RECORD_NAME = "advanced-hunting-auth-record.json"
CONFIG_NAME = "config.json"
SETUP_STATE_NAME = "setup-state.json"
TOKEN_CACHE_NAME = "sentinel_xdr_migration_advanced_hunting"

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


def _state_dir(state_dir: str | Path | None = None) -> Path:
    configured = state_dir or os.getenv("SENTINEL_XDR_MIGRATION_STATE_DIR")
    return Path(configured).expanduser() if configured else DEFAULT_STATE_DIR


def _run(
    command: Sequence[str], runner: CommandRunner = subprocess.run
) -> subprocess.CompletedProcess[str]:
    return runner(
        list(command),
        capture_output=True,
        text=True,
        check=False,
    )


def _command_status(
    name: str,
    command: Sequence[str],
    *,
    runner: CommandRunner,
) -> dict[str, Any]:
    executable = shutil.which(command[0])
    if executable is None:
        return {
            "name": name,
            "status": "missing",
            "detail": f"{command[0]} is not installed or not on PATH",
        }
    resolved_command = [executable, *command[1:]]
    result = _run(resolved_command, runner)
    if result.returncode == 0:
        return {"name": name, "status": "ready", "detail": None}
    detail = (result.stderr or result.stdout).strip()
    return {
        "name": name,
        "status": "actionRequired",
        "detail": detail[-1000:] if detail else f"command exited {result.returncode}",
    }


def _load_auth_record(path: Path):
    if not path.exists():
        return None
    from azure.identity import AuthenticationRecord

    try:
        return AuthenticationRecord.deserialize(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def configure_workspace(
    workspace_resource_id: str,
    *,
    workspace_customer_id: str | None = None,
    tenant_id: str | None = None,
    subscription_id: str | None = None,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    normalized = workspace_resource_id.strip().rstrip("/")
    lowered = normalized.lower()
    if not (
        lowered.startswith("/subscriptions/")
        and "/resourcegroups/" in lowered
        and "/providers/microsoft.operationalinsights/workspaces/" in lowered
    ):
        raise ValueError("workspace-resource-id must be a full Log Analytics ARM ID")
    workspace_subscription_id = normalized.split("/")[2]
    if (
        subscription_id
        and workspace_subscription_id.lower() != subscription_id.strip().lower()
    ):
        raise ValueError(
            "workspace ARM ID subscription does not match subscription-id"
        )

    state_root = _state_dir(state_dir)
    state_root.mkdir(parents=True, exist_ok=True)
    config_path = state_root / CONFIG_NAME
    config = _read_json(config_path)
    config["workspaceResourceId"] = normalized
    if workspace_customer_id:
        config["workspaceId"] = workspace_customer_id.strip()
    if tenant_id:
        config["tenantId"] = tenant_id.strip()
    if subscription_id:
        config["subscriptionId"] = subscription_id.strip()
    config_path.write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "status": "configured",
        "workspaceResourceId": normalized,
        "workspaceCustomerId": config.get("workspaceId"),
        "tenantId": config.get("tenantId"),
        "subscriptionId": config.get("subscriptionId"),
        "configPath": str(config_path),
    }


def _advanced_hunting_status(
    state_root: Path, tenant_id: str | None = None
) -> dict[str, Any]:
    try:
        from azure.core.exceptions import ClientAuthenticationError
        from azure.identity import (
            AuthenticationRequiredError,
            DeviceCodeCredential,
            TokenCachePersistenceOptions,
        )
    except ImportError:
        return {
            "name": "advancedHunting",
            "status": "missing",
            "detail": "azure-identity is not installed",
        }

    record_path = state_root / AUTH_RECORD_NAME
    record = _load_auth_record(record_path)
    if record is None:
        return {
            "name": "advancedHunting",
            "status": "actionRequired",
            "detail": "one-time Microsoft Graph device-code sign-in is required",
        }

    tenant_id = (
        os.getenv("AH_TENANT_ID")
        or tenant_id
        or getattr(record, "tenant_id", None)
    )
    credential = DeviceCodeCredential(
        client_id=GRAPH_CLIENT_ID,
        tenant_id=tenant_id,
        authentication_record=record,
        cache_persistence_options=TokenCachePersistenceOptions(name=TOKEN_CACHE_NAME),
        disable_automatic_authentication=True,
    )
    try:
        credential.get_token(GRAPH_SCOPE)
    except (AuthenticationRequiredError, ClientAuthenticationError) as exc:
        return {
            "name": "advancedHunting",
            "status": "actionRequired",
            "detail": f"cached sign-in needs renewal: {exc}",
        }
    return {
        "name": "advancedHunting",
        "status": "ready",
        "detail": f"authenticated as {getattr(record, 'username', '') or 'cached user'}",
    }


def doctor(
    *,
    state_dir: str | Path | None = None,
    runner: CommandRunner = subprocess.run,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    state_root = _state_dir(state_dir)
    env = environment if environment is not None else os.environ
    setup_state = state_root / SETUP_STATE_NAME
    config = _read_json(state_root / CONFIG_NAME)

    python_status = {
        "name": "python",
        "status": "ready" if sys.version_info >= (3, 10) else "unsupported",
        "detail": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    azure_cli = _command_status(
        "azureCli",
        ("az", "version", "--output", "none"),
        runner=runner,
    )
    sentinel_auth = _command_status(
        "sentinelAuthentication",
        (
            "az",
            "account",
            "get-access-token",
            "--resource",
            LOG_ANALYTICS_RESOURCE,
            "--query",
            "expiresOn",
            "--output",
            "tsv",
        ),
        runner=runner,
    )
    workspace_id = env.get("LA_WORKSPACE_ID") or config.get("workspaceId")
    workspace_resource_id = config.get("workspaceResourceId")
    workspace_configured = bool(workspace_id or workspace_resource_id)
    workspace = {
        "name": "sentinelWorkspace",
        "status": "ready" if workspace_configured else "optional",
        "detail": (
            "a reusable workspace is configured"
            if workspace_configured
            else "set LA_WORKSPACE_ID to enable original Sentinel query execution"
        ),
        "workspaceResourceId": workspace_resource_id,
        "workspaceCustomerId": workspace_id,
    }
    hunting = _advanced_hunting_status(state_root, config.get("tenantId"))
    checks = [python_status, azure_cli, sentinel_auth, workspace, hunting]
    runtime_ready = sentinel_auth["status"] == "ready" and hunting["status"] == "ready"

    actions: list[str] = []
    if azure_cli["status"] != "ready" or sentinel_auth["status"] != "ready":
        actions.append("Run `sentinel-xdr-migration setup` to authenticate Azure CLI.")
    if not workspace_id:
        actions.append("Set `LA_WORKSPACE_ID` to enable Sentinel runtime validation.")
    if hunting["status"] != "ready":
        actions.append(
            "Run `sentinel-xdr-migration setup` for the one-time Advanced Hunting sign-in."
        )

    return {
        "toolVersion": __version__,
        "firstRun": not setup_state.exists(),
        "mode": "runtime" if runtime_ready else "offline",
        "conversionAvailable": python_status["status"] == "ready",
        "runtimeValidationAvailable": runtime_ready,
        "configuredWorkspaceResourceId": workspace_resource_id,
        "configuredWorkspaceCustomerId": workspace_id,
        "configuredTenantId": config.get("tenantId"),
        "configuredSubscriptionId": config.get("subscriptionId"),
        "checks": checks,
        "recommendedActions": actions,
    }


def _login_advanced_hunting(
    state_root: Path, tenant_id: str | None, auth_method: str = "device-code"
) -> dict[str, Any]:
    from azure.identity import (
        DeviceCodeCredential,
        InteractiveBrowserCredential,
        TokenCachePersistenceOptions,
    )

    state_root.mkdir(parents=True, exist_ok=True)
    common_kwargs: dict[str, Any] = {
        "client_id": GRAPH_CLIENT_ID,
        "cache_persistence_options": TokenCachePersistenceOptions(name=TOKEN_CACHE_NAME),
    }
    if tenant_id:
        common_kwargs["tenant_id"] = tenant_id
    if auth_method == "browser":
        credential = InteractiveBrowserCredential(**common_kwargs)
    elif auth_method == "device-code":
        credential = DeviceCodeCredential(
            **common_kwargs,
            prompt_callback=lambda uri, code, _expires: print(
                f"Open {uri} and enter code {code}", file=sys.stderr, flush=True
            ),
        )
    else:
        raise ValueError(
            "hunting_auth_method must be 'device-code' or 'browser'"
        )
    record = credential.authenticate(scopes=[GRAPH_SCOPE])
    (state_root / AUTH_RECORD_NAME).write_text(record.serialize(), encoding="utf-8")
    credential.get_token(GRAPH_SCOPE)
    return {
        "name": "advancedHuntingAuthentication",
        "status": "completed",
        "detail": f"authenticated as {getattr(record, 'username', '') or 'user'}",
    }


def setup(
    *,
    interactive: bool = False,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    skip_sentinel_auth: bool = False,
    skip_hunting_auth: bool = False,
    hunting_auth_method: str = "device-code",
    state_dir: str | Path | None = None,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    state_root = _state_dir(state_dir)
    state_root.mkdir(parents=True, exist_ok=True)
    actions: list[dict[str, Any]] = []

    config_path = state_root / CONFIG_NAME
    config = _read_json(config_path)
    if tenant_id:
        config["tenantId"] = tenant_id
    if workspace_id:
        config["workspaceId"] = workspace_id
    if config:
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    if workspace_id:
        actions.append(
            {
                "name": "workspaceConfiguration",
                "status": "completed",
                "detail": "workspace identifier saved in the local non-secret configuration",
            }
        )

    current = doctor(state_dir=state_root, runner=runner)
    sentinel_check = next(
        check for check in current["checks"] if check["name"] == "sentinelAuthentication"
    )
    if not skip_sentinel_auth and sentinel_check["status"] != "ready":
        if interactive:
            az_executable = shutil.which("az")
            if az_executable is None:
                actions.append(
                    {
                        "name": "sentinelAuthentication",
                        "status": "failed",
                        "detail": "Azure CLI is not installed or not on PATH",
                    }
                )
                az_executable = ""
            command = [az_executable, "login"]
            if tenant_id:
                command.extend(["--tenant", tenant_id])
            if az_executable:
                result = subprocess.run(command, check=False)
                actions.append(
                    {
                        "name": "sentinelAuthentication",
                        "status": "completed" if result.returncode == 0 else "failed",
                        "detail": None if result.returncode == 0 else "az login failed",
                    }
                )
        else:
            actions.append(
                {
                    "name": "sentinelAuthentication",
                    "status": "actionRequired",
                    "detail": "rerun setup interactively to launch `az login`",
                }
            )

    hunting_check = next(
        check for check in current["checks"] if check["name"] == "advancedHunting"
    )
    if not skip_hunting_auth and hunting_check["status"] != "ready":
        if interactive:
            try:
                actions.append(
                    _login_advanced_hunting(
                        state_root, tenant_id, auth_method=hunting_auth_method
                    )
                )
            except Exception as exc:
                actions.append(
                    {
                        "name": "advancedHuntingAuthentication",
                        "status": "failed",
                        "detail": f"{type(exc).__name__}: {exc}",
                    }
                )
        else:
            actions.append(
                {
                    "name": "advancedHuntingAuthentication",
                    "status": "actionRequired",
                    "detail": (
                        "rerun setup interactively for device-code or browser sign-in"
                    ),
                }
            )

    state = {
        "toolVersion": __version__,
        "initializedAt": datetime.now(timezone.utc).isoformat(),
        "interactiveAuthenticationRequested": interactive,
    }
    (state_root / SETUP_STATE_NAME).write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )
    final_status = doctor(state_dir=state_root, runner=runner)
    return {
        "setupCompleted": True,
        "mode": final_status["mode"],
        "actions": actions,
        "doctor": final_status,
        "message": (
            "Runtime validation is ready."
            if final_status["runtimeValidationAvailable"]
            else "Offline conversion is ready; runtime authentication can be completed later."
        ),
    }
