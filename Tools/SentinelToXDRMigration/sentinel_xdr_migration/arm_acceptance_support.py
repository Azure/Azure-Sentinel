from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

from .onboarding import _state_dir

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parameter_values(
    template: dict[str, Any],
    workspace_name: str,
    approved_flags: dict[str, bool],
) -> dict[str, Any]:
    values: dict[str, Any] = {}
    parameters = template.get("parameters") or {}
    for name, definition in parameters.items():
        if name in approved_flags:
            values[name] = True
        elif name == "workspace":
            values[name] = workspace_name
        elif "defaultValue" in definition:
            continue
        else:
            raise ValueError(
                f"package parameter {name} has no default and no supported locked-target binding"
            )
    if set(approved_flags) != {
        name for name in parameters if name.startswith("Deploy")
    }:
        raise ValueError(
            "approved package flags do not exactly match declared Deploy* parameters"
        )
    return values


def _run_cli(
    command: list[str],
    *,
    runner: CommandRunner | None = None,
) -> tuple[int, Any, str]:
    run = runner or subprocess.run
    executable = shutil.which("az")
    if executable is None:
        return 127, None, "Azure CLI is not installed or not available on PATH"
    try:
        result = run(
            [executable, *command],
            capture_output=True,
            text=True,
            check=False,
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        return (
            124,
            None,
            "Azure CLI command timed out after 1800 seconds; write outcome may be ambiguous",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return (
            126,
            None,
            f"Azure CLI execution failed ({type(exc).__name__}); no retry was attempted",
        )
    except Exception as exc:
        return (
            126,
            None,
            f"Azure CLI runner failed ({type(exc).__name__}); no retry was attempted",
        )
    parsed: Any = None
    if result.stdout:
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            parsed = None
    error = str(result.stderr or "").strip()
    if result.returncode and not error:
        error = f"Azure CLI exited with code {result.returncode}"
    return result.returncode, parsed, error[:4000]


def _verify_existing_cli_target(
    target: dict[str, Any],
    *,
    state_dir: str | Path | None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    from .graph_client_config import azure_cli_profile, configured_azure_cli_profile

    profile = configured_azure_cli_profile(_state_dir(state_dir))
    with azure_cli_profile(profile):
        status, account, error = _run_cli(
            [
                "account",
                "show",
                "--subscription",
                target["subscriptionId"],
                "--output",
                "json",
                "--only-show-errors",
            ],
            runner=runner,
        )
    return {
        "statusCode": status,
        "tenantMatches": (
            isinstance(account, dict)
            and str(account.get("tenantId") or "").casefold()
            == str(target["tenantId"]).casefold()
        ),
        "subscriptionMatches": (
            isinstance(account, dict)
            and str(account.get("id") or "").casefold()
            == str(target["subscriptionId"]).casefold()
        ),
        "error": error or None,
    }


def _deployment_provisioning_state(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    properties = value.get("properties")
    if isinstance(properties, dict):
        state = properties.get("provisioningState")
        if isinstance(state, str):
            return state.casefold()
    state = value.get("provisioningState")
    return state.casefold() if isinstance(state, str) else None


def _validated_members(members: list[dict[str, str]]) -> list[dict[str, str]]:
    if not isinstance(members, list) or not members:
        raise ValueError("at least one exact solution/run member is required")
    normalized: list[dict[str, str]] = []
    seen: set[Path] = set()
    seen_names: set[str] = set()
    for item in members:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("solution"), str)
            or not item["solution"].strip()
            or not isinstance(item.get("runId"), str)
            or not item["runId"].strip()
        ):
            raise ValueError(
                "each batch member requires an exact solution path and run ID"
            )
        candidate = Path(item["solution"]).expanduser()
        if candidate.is_symlink():
            raise ValueError("batch solution paths cannot be symlinks")
        root = candidate.resolve(strict=True)
        if not root.is_dir() or root in seen or root.name in seen_names:
            raise ValueError(
                "batch solution paths must be existing, unique solution directories"
            )
        seen.add(root)
        seen_names.add(root.name)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", item["runId"]):
            raise ValueError("batch member run ID is invalid")
        normalized.append(
            {
                "solution": root.name,
                "solutionPath": str(root),
                "runId": item["runId"],
            }
        )
    return normalized


def _validated_shared_decisions(
    shared_decisions_path: str | Path,
    target: dict[str, Any],
    members: list[dict[str, str]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    source = Path(shared_decisions_path).expanduser()
    if source.is_symlink():
        raise ValueError(
            "shared PR/lab decisions must be a regular non-symlink file"
        )
    source = source.resolve(strict=True)
    try:
        receipt = json.loads(source.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"shared PR/lab decision receipt is unreadable: {exc}"
        ) from exc
    if not isinstance(receipt, dict):
        raise ValueError("shared PR/lab decision receipt must be a JSON object")
    scope = receipt.get("scope")
    decisions = receipt.get("decisions")
    boundary = receipt.get("authorizationBoundary")
    if not all(isinstance(value, dict) for value in (scope, decisions, boundary)):
        raise ValueError("shared PR/lab decision receipt scope is malformed")
    expected_solutions = scope.get("solutions")
    actual_solutions = [item["solution"] for item in members]
    if (
        receipt.get("status") != "User-confirmed shared decisions"
        or not isinstance(receipt.get("userConfirmation"), str)
        or not receipt["userConfirmation"].strip()
        or not isinstance(expected_solutions, list)
        or any(not isinstance(value, str) or not value for value in expected_solutions)
        or len(set(expected_solutions)) != len(expected_solutions)
        or set(expected_solutions) != set(actual_solutions)
    ):
        raise ValueError(
            "batch members must exactly match the solution set in the user-confirmed shared decision receipt"
        )
    expected_target = {
        "tenantId": target["tenantId"],
        "subscriptionId": target["subscriptionId"],
        "resourceGroup": target["resourceGroup"],
        "workspaceResourceId": target["workspaceResourceId"],
        "workspaceCustomerId": target["workspaceCustomerId"],
    }
    for key, value in expected_target.items():
        if str(scope.get(key) or "").casefold() != str(value or "").casefold():
            raise ValueError(
                f"shared decision receipt target does not match locked {key}"
            )
    known_flags = decisions.get("knownFlagSelections")
    if not isinstance(known_flags, dict):
        known_flags = {}
    if (
        decisions.get("deploymentRoute") != "Full-package installation"
        or "all declared content"
        not in str(decisions.get("labTestingContentSelection") or "").casefold()
        or not known_flags
        or any(type(value) is not bool or value is not True for value in known_flags.values())
        or decisions.get("askContentTypeSelectionAgain") is not False
        or decisions.get("askDeploymentRouteAgain") is not False
        or decisions.get("askTacticProjectionPolicyAgain") is not False
    ):
        raise ValueError(
            "shared decisions do not authorize the current all-content full-package route"
        )
    if (
        boundary.get("environmentWritesAuthorized") is not False
        or boundary.get("immediateExactScopeWriteApprovalRequired") is not True
        or boundary.get("oneApprovalMayCoverAnEnumeratedMultiSolutionWriteBatch") is not True
        or boundary.get("unsupportedExecutionRouteAuthorized") is not False
    ):
        raise ValueError(
            "shared decision receipt has a broadened or invalid write-approval boundary"
        )
    return receipt, {
        "path": str(source),
        "sha256": _sha256(source),
        "scope": expected_target,
        "solutions": sorted(expected_solutions),
        "prNumber": scope.get("prNumber"),
        "prIdentityNote": scope.get("prIdentityNote"),
    }
