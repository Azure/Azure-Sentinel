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
from .graph_auth import validate_delegated_graph_claims
from .graph_client_config import (
    DEFAULT_GRAPH_CLIENT_ID,
    azure_cli_profile,
    configure_graph_client,
    configured_azure_cli_profile,
    configure_azure_cli_profile,
    graph_auth_record_path,
    graph_token_cache_name,
    ensure_private_state_root,
    restrict_private_permissions,
    verify_graph_auth_binding,
    write_graph_auth_metadata,
)

LOG_ANALYTICS_RESOURCE = "https://api.loganalytics.io"
GRAPH_SCOPE = "https://graph.microsoft.com/ThreatHunting.Read.All"
GRAPH_CLIENT_ID = DEFAULT_GRAPH_CLIENT_ID
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
            "status": "failed",
            "detail": f"{command[0]} is not installed or not on PATH",
        }
    resolved_command = [executable, *command[1:]]
    result = _run(resolved_command, runner)
    if result.returncode == 0:
        return {"name": name, "status": "passed", "detail": None}
    detail = (result.stderr or result.stdout).strip()
    return {
        "name": name,
        "status": "failed",
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
    ensure_private_state_root(state_root)
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
    state_root: Path, tenant_id: str | None = None, *, probe: bool = False
) -> dict[str, Any]:
    if not probe:
        return {
            "name": "advancedHunting",
            "status": "notRun",
            "detail": "Graph authentication and access require an explicitly scoped runtime read",
        }
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
            "status": "failed",
            "detail": "azure-identity is not installed",
        }
    from .graph_client_config import resolve_graph_client_id

    client_id = resolve_graph_client_id(state_root, "advancedHunting")
    record_path = graph_auth_record_path(
        state_root, "advancedHunting", client_id, AUTH_RECORD_NAME
    )
    record = _load_auth_record(record_path)
    if record is None:
        return {
            "name": "advancedHunting",
            "status": "failed",
            "detail": "one-time Microsoft Graph device-code sign-in is required",
        }
    try:
        verify_graph_auth_binding(
            record_path,
            record,
            purpose="advancedHunting",
            client_id=client_id,
            tenant_id=tenant_id,
        )
    except ValueError as exc:
        return {"name": "advancedHunting", "status": "failed", "detail": str(exc)}
    tenant_id = tenant_id or getattr(record, "tenant_id", None)
    credential = DeviceCodeCredential(
        client_id=client_id,
        tenant_id=tenant_id,
        authentication_record=record,
        cache_persistence_options=TokenCachePersistenceOptions(
            name=graph_token_cache_name(
                "advancedHunting", client_id, TOKEN_CACHE_NAME
            )
        ),
        disable_automatic_authentication=True,
    )
    try:
        access_token = credential.get_token(GRAPH_SCOPE).token
    except (AuthenticationRequiredError, ClientAuthenticationError) as exc:
        return {
            "name": "advancedHunting",
            "status": "failed",
            "detail": f"cached sign-in needs renewal: {exc}",
        }
    from .graph_readiness import _token_claims

    try:
        scope_diagnostics = validate_delegated_graph_claims(
            _token_claims(access_token),
            tenant_id=tenant_id or "",
            required_scopes=(GRAPH_SCOPE,),
            purpose="Advanced Hunting",
        )
    except RuntimeError as exc:
        return {
            "name": "advancedHunting",
            "status": "failed",
            "detail": str(exc),
        }
    return {
        "name": "advancedHunting",
        "status": "passed",
        "detail": "a Graph access token was obtained; provider authorization was not tested",
        "scopeDiagnostics": scope_diagnostics["delegatedScopes"],
    }


def _sentinel_authentication_status(
    *, runner: CommandRunner, probe: bool, azure_config_dir: str | None = None
) -> dict[str, Any]:
    if not probe:
        return {
            "name": "sentinelAuthentication",
            "status": "notRun",
            "detail": "Log Analytics authentication and access require an explicitly scoped runtime read",
        }
    with azure_cli_profile(azure_config_dir):
        result = _command_status(
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
    result["name"] = "sentinelAuthentication"
    if result["status"] == "passed":
        result["detail"] = "an access token was obtained; provider authorization was not tested"
    return result


def doctor(
    *,
    state_dir: str | Path | None = None,
    runner: CommandRunner = subprocess.run,
    environment: Mapping[str, str] | None = None,
    solution: str | Path | None = None,
    probe_authentication: bool = False,
) -> dict[str, Any]:
    state_root = _state_dir(state_dir)
    env = environment if environment is not None else os.environ
    azure_config_dir = configured_azure_cli_profile(state_root)
    setup_state = state_root / SETUP_STATE_NAME
    config = _read_json(state_root / CONFIG_NAME)

    python_supported = sys.version_info[:2] in {(3, 11), (3, 12)}
    python_status = {
        "name": "python",
        "status": "passed" if python_supported else "failed",
        "detail": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    azure_cli = _command_status(
        "azureCli",
        ("az", "version", "--output", "none"),
        runner=runner,
    )
    sentinel_auth = _sentinel_authentication_status(
        runner=runner,
        probe=probe_authentication,
        azure_config_dir=azure_config_dir,
    )
    workspace_id = env.get("LA_WORKSPACE_ID") or config.get("workspaceId")
    workspace_resource_id = config.get("workspaceResourceId")
    tenant_id = env.get("AZURE_TENANT_ID") or config.get("tenantId")
    subscription_id = env.get("AZURE_SUBSCRIPTION_ID") or config.get("subscriptionId")
    resolved_subscription_id = subscription_id
    missing_binding = [
        name
        for name, value in {
            "tenantId": tenant_id,
            "workspaceResourceId": workspace_resource_id,
            "workspaceCustomerId": workspace_id,
        }.items()
        if not value
    ]
    if missing_binding:
        workspace_status = "unknown"
        workspace_detail = "incomplete local target binding; missing " + ", ".join(
            missing_binding
        )
    else:
        try:
            from .target_context import build_target, workspace_identity

            derived_subscription = workspace_identity(str(workspace_resource_id))[
                "subscriptionId"
            ]
            resolved_subscription_id = subscription_id or derived_subscription
            build_target(
                tenant_id=str(tenant_id),
                subscription_id=str(resolved_subscription_id),
                workspace_resource_id=str(workspace_resource_id),
                workspace_customer_id=str(workspace_id),
            )
        except (AttributeError, TypeError, ValueError) as exc:
            workspace_status = "failed"
            workspace_detail = str(exc)
        else:
            workspace_status = "passed"
            workspace_detail = "complete local workspace binding; access not tested"
    workspace = {
        "name": "sentinelWorkspace",
        "status": workspace_status,
        "detail": workspace_detail,
        "workspaceResourceId": workspace_resource_id,
        "workspaceCustomerId": workspace_id,
        "subscriptionId": resolved_subscription_id,
    }
    hunting = _advanced_hunting_status(
        state_root, config.get("tenantId"), probe=probe_authentication
    )
    checks = [python_status, azure_cli, sentinel_auth, workspace, hunting]
    runtime_ready = False

    actions: list[str] = []
    if azure_cli["status"] != "passed":
        actions.append("Run `sentinel-xdr-migration setup` to authenticate Azure CLI.")
    if workspace_status != "passed":
        actions.append(
            "Complete the exact tenant, subscription, workspace ARM ID, and customer-ID binding."
        )
    if sentinel_auth["status"] != "passed" or hunting["status"] != "passed":
        actions.append(
            "Authentication, authorization, table access, and query access remain unverified until an explicitly scoped runtime read."
        )

    result = {
        "toolVersion": __version__,
        "firstRun": not setup_state.exists(),
        "mode": "runtime" if runtime_ready else "offline",
        "conversionAvailable": python_supported,
        "runtimeValidationAvailable": runtime_ready,
        "configuredWorkspaceResourceId": workspace_resource_id,
        "configuredWorkspaceCustomerId": workspace_id,
        "configuredTenantId": config.get("tenantId"),
        "configuredSubscriptionId": resolved_subscription_id,
        "checks": checks,
        "recommendedActions": actions,
    }
    if solution is not None:
        from .target_config import doctor_solution_target

        result["solutionTarget"] = doctor_solution_target(solution)
    return result


def _login_advanced_hunting(
    state_root: Path,
    tenant_id: str | None,
    auth_method: str = "device-code",
    client_id: str | None = None,
) -> dict[str, Any]:
    from azure.identity import (
        DeviceCodeCredential,
        InteractiveBrowserCredential,
        TokenCachePersistenceOptions,
    )

    ensure_private_state_root(state_root)
    from .graph_client_config import resolve_graph_client_id

    selected_client = resolve_graph_client_id(
        state_root, "advancedHunting", client_id
    )
    record_path = graph_auth_record_path(
        state_root, "advancedHunting", selected_client, AUTH_RECORD_NAME
    )
    common_kwargs: dict[str, Any] = {
        "client_id": selected_client,
        "cache_persistence_options": TokenCachePersistenceOptions(
            name=graph_token_cache_name(
                "advancedHunting", selected_client, TOKEN_CACHE_NAME
            )
        ),
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
    access_token = credential.get_token(GRAPH_SCOPE).token
    from .graph_readiness import _token_claims

    try:
        scope_diagnostics = validate_delegated_graph_claims(
            _token_claims(access_token),
            tenant_id=getattr(record, "tenant_id", None) or tenant_id or "",
            required_scopes=(GRAPH_SCOPE,),
            purpose="Advanced Hunting",
        )
    except RuntimeError as exc:
        return {
            "name": "advancedHuntingAuthentication",
            "status": "failed",
            "detail": str(exc),
        }
    record_path.write_text(record.serialize(), encoding="utf-8")
    restrict_private_permissions(record_path, 0o600)
    write_graph_auth_metadata(
        record_path,
        purpose="advancedHunting",
        client_id=selected_client,
        tenant_id=getattr(record, "tenant_id", None) or tenant_id,
    )
    return {
        "name": "advancedHuntingAuthentication",
        "status": "completed",
        "detail": f"authenticated as {getattr(record, 'username', '') or 'user'}",
        "scopeDiagnostics": scope_diagnostics["delegatedScopes"],
    }


def setup(
    *,
    interactive: bool = False,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    skip_sentinel_auth: bool = False,
    skip_hunting_auth: bool = False,
    hunting_auth_method: str = "device-code",
    hunting_client_id: str | None = None,
    azure_config_dir: str | Path | None = None,
    state_dir: str | Path | None = None,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    state_root = _state_dir(state_dir)
    ensure_private_state_root(state_root)
    actions: list[dict[str, Any]] = []

    config_path = state_root / CONFIG_NAME
    config = _read_json(config_path)
    tenant_id = tenant_id or config.get("tenantId")
    if tenant_id:
        config["tenantId"] = tenant_id
    if workspace_id:
        config["workspaceId"] = workspace_id
    if config:
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    if hunting_client_id:
        configure_graph_client(
            state_root, "advancedHunting", hunting_client_id
        )
    if azure_config_dir is not None:
        configure_azure_cli_profile(state_root, azure_config_dir)
    if workspace_id:
        actions.append(
            {
                "name": "workspaceConfiguration",
                "status": "completed",
                "detail": "workspace identifier saved in the local non-secret configuration",
            }
        )

    current = doctor(
        state_dir=state_root, runner=runner, probe_authentication=True
    )
    sentinel_check = next(
        check for check in current["checks"] if check["name"] == "sentinelAuthentication"
    )
    if not skip_sentinel_auth and sentinel_check["status"] != "passed":
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
                with azure_cli_profile(
                    str(azure_config_dir)
                    if azure_config_dir is not None
                    else configured_azure_cli_profile(state_root)
                ):
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
    if not skip_hunting_auth and hunting_check["status"] != "passed":
        if interactive:
            try:
                actions.append(
                    _login_advanced_hunting(
                        state_root,
                        tenant_id,
                        auth_method=hunting_auth_method,
                        client_id=hunting_client_id,
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
    final_status = doctor(
        state_dir=state_root, runner=runner, probe_authentication=True
    )
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
