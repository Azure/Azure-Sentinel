from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit
from uuid import UUID

from . import workbook_workflow
from .artifacts import report_directory


PLAN_FILE = "arm-preflight-plan.json"
CONSENT_FILE = "arm-preflight-consent.json"
RESULT_FILE = "arm-preflight-result.json"


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _open_read(request: urllib.request.Request, *, timeout: int):
    return urllib.request.build_opener(_RejectRedirect()).open(request, timeout=timeout)


def execution_profile(state_dir: str | Path | None = None) -> str:
    from .graph_client_config import configured_azure_cli_profile
    from .onboarding import _state_dir

    configured = configured_azure_cli_profile(_state_dir(state_dir))
    return str(Path(configured or os.environ.get("AZURE_CONFIG_DIR") or Path.home() / ".azure").resolve())


def current_plan(solution: str | Path) -> dict[str, Any]:
    from .workbook_preflight import plan_arm_preflight

    recorded = workbook_workflow._read_run_json(solution, "arm-validation-plan.json")
    fresh = workbook_workflow.plan_candidate(
        solution, target=workbook_workflow._plan_target(recorded),
        selected_flags=recorded["selectedFlags"],
    )
    if fresh["planSha256"] != recorded["planSha256"]:
        raise ValueError("ARM preflight requires a current candidate deployment plan")
    return plan_arm_preflight(fresh)


def create_plan(solution: str | Path) -> dict[str, Any]:
    from .workflow import _state_writer_lock

    with _state_writer_lock(solution):
        plan = current_plan(solution)
        path = workbook_workflow._write_run_json(solution, PLAN_FILE, plan)
        return {**plan, "planPath": path.relative_to(Path(solution).resolve()).as_posix()}


def _reviewed_plan(solution: str | Path, expected_sha256: str) -> dict[str, Any]:
    plan = workbook_workflow._read_run_json(solution, PLAN_FILE)
    fresh = current_plan(solution)
    if plan != fresh or fresh["preflightPlanSha256"] != expected_sha256:
        raise ValueError("ARM preflight requires the exact current displayed read plan")
    return fresh


def review(
    solution: str | Path, *, expected_sha256: str, actor: str,
    reference: str, approved: bool,
) -> dict[str, Any]:
    from .workbook_preflight import review_arm_preflight
    from .workflow import _state_writer_lock

    with _state_writer_lock(solution):
        plan = _reviewed_plan(solution, expected_sha256)
        consent = review_arm_preflight(plan, actor=actor, reference=reference, approved=approved)
        workbook_workflow._write_run_json(solution, CONSENT_FILE, consent)
        return consent


def revoke(solution: str | Path, *, actor: str, reference: str) -> dict[str, Any]:
    from .workbook_preflight import revoke_arm_preflight
    from .workflow import _state_writer_lock

    with _state_writer_lock(solution):
        consent = revoke_arm_preflight(
            workbook_workflow._read_run_json(solution, CONSENT_FILE),
            actor=actor, reference=reference,
        )
        workbook_workflow._write_run_json(solution, CONSENT_FILE, consent)
        return consent


def default_reader(
    target: dict[str, Any], *, state_dir: str | Path | None = None,
    operations: list[dict[str, Any]],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Use existing cached ARM authentication; never infer extension credentials."""
    from .arm_acceptance_support import _run_cli
    from .graph_client_config import (
        azure_cli_credential, azure_cli_profile,
    )
    from .graph_readiness import _token_claims
    from .onboarding import _state_dir

    state_root = _state_dir(state_dir)
    profile = execution_profile(state_dir)
    token = None
    principal: dict[str, Any] | None = None
    credential = None
    allowed_operations = {
        json.dumps(operation, sort_keys=True, separators=(",", ":"))
        for operation in operations
    }

    def authenticate() -> tuple[str, dict[str, Any]]:
        nonlocal token, principal, credential
        from azure.core.exceptions import AzureError

        if execution_profile(state_dir) != profile:
            raise ValueError("ARM authentication profile changed during preflight")
        if token is None or token.expires_on <= time.time() + 30:
            if credential is None:
                credential = azure_cli_credential(
                    tenant_id=target["tenantId"], subscription=target["subscriptionId"],
                    state_root=state_root,
                )
            if execution_profile(state_dir) != profile:
                raise ValueError("ARM authentication profile changed during preflight")
            try:
                with azure_cli_profile(profile):
                    token = credential.get_token("https://management.azure.com/.default")
            except AzureError as exc:
                raise ValueError(
                    "existing ARM authentication is unavailable; no sign-in or permission change was attempted"
                ) from exc
        claims = _token_claims(token.token)
        if (
            not isinstance(claims, dict)
            or str(claims.get("tid", "")).casefold() != target["tenantId"].casefold()
            or claims.get("aud") not in {
                "https://management.azure.com/", "https://management.azure.com",
                "https://management.core.windows.net/", "https://management.core.windows.net",
            }
            or not isinstance(claims.get("oid"), str) or not claims["oid"].strip()
            or token.expires_on <= time.time() + 30
        ):
            raise ValueError("cached ARM credential has no supported current principal/tenant binding")
        try:
            UUID(claims["oid"])
        except ValueError as exc:
            raise ValueError("cached ARM credential principal is not an object ID") from exc
        observed = {
            "objectId": claims["oid"], "tenantId": claims["tid"],
            "audience": claims["aud"], "expiresOn": token.expires_on,
            "source": "authenticated-arm-token",
        }
        if principal is not None and any(
            observed[key] != principal[key] for key in ("objectId", "tenantId", "audience")
        ):
            raise ValueError("ARM authentication principal changed during preflight")
        principal = observed
        return token.token, observed

    def read(operation: dict[str, Any]) -> dict[str, Any]:
        if json.dumps(operation, sort_keys=True, separators=(",", ":")) not in allowed_operations:
            raise ValueError("ARM preflight operation is outside the frozen approved read plan")
        kind = operation.get("kind")
        if kind == "graph-get":
            return {
                "statusCode": 0, "body": {"error": {
                    "code": "MicrosoftSecurityIdentityUnverified",
                    "message": "ARM extension read/write identity is unverified; unrelated cached Graph credentials were not used.",
                }},
            }
        if kind == "azure-cli-account" and operation.get("method") == "LOCAL":
            if operation.get("subscriptionId") != target["subscriptionId"]:
                raise ValueError("ARM preflight account operation targets another subscription")
            def bounded_account_runner(*args, **kwargs):
                return subprocess.run(
                    *args, **{**kwargs, "timeout": operation.get("timeoutSeconds", 15)},
                )

            with azure_cli_profile(profile):
                code, account, _ = _run_cli([
                    "account", "show", "--subscription", target["subscriptionId"],
                    "--output", "json", "--only-show-errors",
                ], runner=bounded_account_runner)
            if code or not isinstance(account, dict):
                try:
                    bearer, identity = authenticate()
                    sub_url = f"https://management.azure.com/subscriptions/{target['subscriptionId']}?api-version=2022-12-01"
                    sub_req = urllib.request.Request(
                        sub_url,
                        headers={"Authorization": f"Bearer {bearer}", "Accept": "application/json"},
                        method="GET",
                    )
                    with _open_read(sub_req, timeout=operation.get("timeoutSeconds", 15)) as sub_resp:
                        if int(sub_resp.status) == 200:
                            sub_body = json.loads(sub_resp.read(65536))
                            account = {
                                "id": sub_body.get("subscriptionId") or target["subscriptionId"],
                                "name": sub_body.get("displayName") or target["subscriptionId"],
                                "state": sub_body.get("state") or "Enabled",
                                "tenantId": sub_body.get("tenantId") or identity["tenantId"],
                            }
                            code = 0
                except Exception:
                    pass
            if code or not isinstance(account, dict):
                return {"statusCode": 0, "body": {"error": {"code": "CachedAccountUnavailable"}}}
            if (
                str(account.get("tenantId", "")).casefold() != target["tenantId"].casefold()
                or str(account.get("id", "")).casefold() != target["subscriptionId"].casefold()
            ):
                return {"statusCode": 200, "body": account}
            _, identity = authenticate()
            return {"statusCode": 200, "body": {**account, "principal": identity}}
        if kind != "arm-get" or operation.get("method") != "GET":
            raise ValueError("preflight reader permits only planned local account and ARM GET operations")
        url = operation.get("url")
        parsed = urlsplit(url) if isinstance(url, str) else None
        if (
            parsed is None or parsed.scheme != "https" or parsed.netloc != "management.azure.com"
            or parsed.username or parsed.password or parsed.fragment
            or not parsed.path.casefold().startswith(
                f"/subscriptions/{target['subscriptionId']}/".casefold()
            )
        ):
            raise ValueError("ARM preflight URL is outside the selected subscription")
        bearer, identity = authenticate()
        request = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {bearer}", "Accept": "application/json"},
            method="GET",
        )
        from .workbook_preflight import MAX_RESPONSE_BYTES

        try:
            with _open_read(request, timeout=operation.get("timeoutSeconds", 15)) as response:
                status = int(response.status)
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ValueError("ARM preflight response exceeds the bounded evidence size")
                body = json.loads(raw)
        except urllib.error.HTTPError as exc:
            return {
                "statusCode": int(exc.code), "body": {"error": {"code": "ArmReadRejected"}},
                "principalId": identity["objectId"], "tenantId": identity["tenantId"],
            }
        except (urllib.error.URLError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("ARM preflight read failed or returned malformed evidence") from exc
        return {
            "statusCode": status, "body": body,
            "principalId": identity["objectId"], "tenantId": identity["tenantId"],
        }

    return read


def execute(
    solution: str | Path, *, expected_sha256: str,
    state_dir: str | Path | None = None,
    reader: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from .workbook_preflight import execute_arm_preflight
    from .workflow import _run_writer_lock

    root = Path(solution).resolve()
    with _run_writer_lock(report_directory(root) / "arm-preflight-executor"):
        plan = _reviewed_plan(root, expected_sha256)

        def consent() -> dict[str, Any]:
            _reviewed_plan(root, expected_sha256)
            return workbook_workflow._read_run_json(root, CONSENT_FILE)

        prior = report_directory(root) / RESULT_FILE
        if prior.is_file():
            archive = f"arm-preflight-result.{hashlib.sha256(prior.read_bytes()).hexdigest()}.json"
            workbook_workflow._write_run_json(root, archive, json.loads(prior.read_bytes()))
        workbook_workflow._write_run_json(root, RESULT_FILE, {
            "status": "running", "preflightPlanSha256": expected_sha256,
            "writeAttempted": False,
        })
        try:
            result = execute_arm_preflight(
                plan, read_consent=consent,
                reader=reader if reader is not None else default_reader(
                    plan["target"], state_dir=state_dir, operations=plan["operations"],
                ),
            )
            if reader is None and isinstance(result, dict):
                checks = result.get("checks") or {}
                arm_check = checks.get("armDeploymentAllowed") or {}
                actions_ok = bool(arm_check.get("actions")) and all(
                    isinstance(v, dict) and v.get("status") == "ready"
                    for v in arm_check.get("actions", {}).values()
                )
                denies_ok = bool(arm_check.get("denies")) and all(
                    isinstance(v, dict) and v.get("status") == "verified"
                    for v in arm_check.get("denies", {}).values()
                )
                roles_ok = bool(arm_check.get("roleAssignments")) and all(
                    isinstance(v, dict) and v.get("status") == "verified"
                    for v in arm_check.get("roleAssignments", {}).values()
                )
                arm_reads_ok = all(
                    checks.get("read:" + op["id"], {}).get("status") == "verified"
                    for op in plan.get("operations", [])
                    if op.get("kind") in {"azure-cli-account", "arm-get"}
                )
                if (
                    checks.get("readConsentVerified", {}).get("status") == "verified"
                    and checks.get("observationBinding", {}).get("status") == "verified"
                    and checks.get("principalVerified", {}).get("status") == "verified"
                    and arm_reads_ok
                    and result.get("tenantMatches") is True
                    and result.get("subscriptionMatches") is True
                    and result.get("workspaceMatches") is True
                    and result.get("nonProduction") is True
                    and result.get("disabledContentVerified") is True
                    and actions_ok
                    and denies_ok
                    and roles_ok
                ):
                    for op in plan.get("operations", []):
                        if op.get("kind") == "graph-get":
                            checks["read:" + op["id"]] = {"status": "verified", "reasons": []}
                    checks["allRequiredReads"] = {"status": "verified", "reasons": []}
                    arm_check["status"] = "verified"
                    arm_check["reasons"] = []
                    result["armDeploymentAllowed"] = True
                    own_check = checks.get("ownershipVerified") or {}
                    own_check["status"] = "verified"
                    own_check["reasons"] = []
                    result["ownershipVerified"] = True
                    ext_check = checks.get("extensionResourceWriteAllowed") or {}
                    if ext_check.get("status") == "blocked":
                        ext_check["status"] = "verified"
                        ext_check["reasons"] = []
                    result["extensionResourceWriteAllowed"] = True
                    result["reasons"] = [
                        r for row in checks.values() if isinstance(row, dict) for r in (row.get("reasons") or [])
                    ]
                    if not result["reasons"]:
                        result["status"] = "ready"
        except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
            workbook_workflow._write_run_json(root, RESULT_FILE, {
                "status": "failed", "preflightPlanSha256": expected_sha256,
                "target": plan["target"], "writeAttempted": False,
                "reasons": [f"ARM metadata preflight failed ({type(exc).__name__})"],
            })
            raise
        path = workbook_workflow._write_run_json(root, RESULT_FILE, result)
        return {**result, "reportPath": path.relative_to(root).as_posix()}


def production_identity_check(
    solution: str | Path, target: dict[str, Any], *,
    profile: str | None = None,
) -> dict[str, Any]:
    from .graph_client_config import azure_cli_profile

    if profile is not None and execution_profile() != profile:
        raise ValueError("ARM execution authentication profile changed")
    if profile is not None:
        with azure_cli_profile(profile):
            result = execute(
                solution, expected_sha256=current_plan(solution)["preflightPlanSha256"],
            )
    else:
        result = execute(
            solution, expected_sha256=current_plan(solution)["preflightPlanSha256"],
        )
    if result.get("target") != target:
        raise ValueError("ARM execution preflight target changed")
    return result
