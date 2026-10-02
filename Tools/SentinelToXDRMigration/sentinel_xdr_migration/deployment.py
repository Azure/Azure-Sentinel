from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .artifacts import artifact_path
from .converter import validate_document, xdr_detection_files
from .onboarding import (
    GRAPH_CLIENT_ID,
    _load_auth_record,
    _read_json,
    _state_dir,
)
from .target_context import require_locked_target

DEPLOYMENT_SCOPE = "https://graph.microsoft.com/CustomDetection.ReadWrite.All"
DEPLOYMENT_ENDPOINT = (
    "https://graph.microsoft.com/beta/security/rules/detectionRules"
)
DEPLOYMENT_AUTH_RECORD_NAME = "custom-detection-auth-record.json"
DEPLOYMENT_TOKEN_CACHE_NAME = "sentinel_xdr_migration_custom_detection"


def _deployment_credential(
    state_root: Path,
    *,
    interactive: bool = False,
    auth_method: str = "device-code",
    tenant_id: str | None = None,
):
    from azure.identity import (
        DeviceCodeCredential,
        InteractiveBrowserCredential,
        TokenCachePersistenceOptions,
    )

    record = _load_auth_record(state_root / DEPLOYMENT_AUTH_RECORD_NAME)
    config = _read_json(state_root / "config.json")
    common: dict[str, Any] = {
        "client_id": GRAPH_CLIENT_ID,
        "tenant_id": tenant_id
        or config.get("tenantId")
        or getattr(record, "tenant_id", None),
        "authentication_record": record,
        "cache_persistence_options": TokenCachePersistenceOptions(
            name=DEPLOYMENT_TOKEN_CACHE_NAME
        ),
        "disable_automatic_authentication": not interactive,
    }
    if auth_method == "browser":
        return InteractiveBrowserCredential(**common)
    if auth_method == "device-code":
        if interactive:
            common["prompt_callback"] = lambda uri, code, _expires: print(
                f"Open {uri} and enter code {code}", file=sys.stderr, flush=True
            )
        return DeviceCodeCredential(**common)
    raise ValueError("auth_method must be 'device-code' or 'browser'")


def setup_deployment_authentication(
    *,
    tenant_id: str | None = None,
    auth_method: str = "device-code",
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    state_root = _state_dir(state_dir)
    state_root.mkdir(parents=True, exist_ok=True)
    if auth_method == "azure-cli":
        executable = shutil.which("az")
        if not executable:
            raise RuntimeError("Azure CLI is not installed or not on PATH")
        command = [
            executable,
            "login",
            "--scope",
            DEPLOYMENT_SCOPE,
        ]
        if tenant_id:
            command.extend(["--tenant", tenant_id])
        result = subprocess.run(command, check=False)
        if result.returncode:
            raise RuntimeError("Azure CLI Custom Detection authentication failed")
        token = _deployment_token(state_dir, require_record=False)
        return {
            "status": "completed",
            "tenantId": tenant_id,
            "username": None,
            "scope": DEPLOYMENT_SCOPE,
            "authMethod": auth_method,
            "tokenAcquired": bool(token),
        }
    credential = _deployment_credential(
        state_root,
        interactive=True,
        auth_method=auth_method,
        tenant_id=tenant_id,
    )
    try:
        record = credential.authenticate(scopes=[DEPLOYMENT_SCOPE])
        credential.get_token(DEPLOYMENT_SCOPE)
    except Exception as exc:
        raise RuntimeError(
            f"Custom Detection authentication failed: {exc}"
        ) from exc
    (state_root / DEPLOYMENT_AUTH_RECORD_NAME).write_text(
        record.serialize(), encoding="utf-8"
    )
    return {
        "status": "completed",
        "tenantId": getattr(record, "tenant_id", None),
        "username": getattr(record, "username", None),
        "scope": DEPLOYMENT_SCOPE,
        "authMethod": auth_method,
    }


def _deployment_token(
    state_dir: str | Path | None = None,
    *,
    require_record: bool = False,
    tenant_id: str | None = None,
) -> str:
    state_root = _state_dir(state_dir)
    if (state_root / DEPLOYMENT_AUTH_RECORD_NAME).exists():
        credential = _deployment_credential(state_root, tenant_id=tenant_id)
        return credential.get_token(DEPLOYMENT_SCOPE).token
    if not require_record:
        from azure.identity import AzureCliCredential

        try:
            return AzureCliCredential(tenant_id=tenant_id).get_token(
                DEPLOYMENT_SCOPE
            ).token
        except Exception:
            pass
    if not (state_root / DEPLOYMENT_AUTH_RECORD_NAME).exists():
        raise RuntimeError(
            "Custom Detection deployment authentication is missing; run "
            "`sentinel-xdr-migration setup-deployment --auth-method azure-cli` first"
        )
    raise AssertionError("unreachable")


def _graph_request(
    method: str,
    url: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            content = response.read().decode("utf-8")
            return response.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as exc:
        content = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"error": {"message": content[:4000]}}
        return exc.code, parsed


def graph_detection_payload(document: dict[str, Any]) -> dict[str, Any]:
    errors = validate_document(document)
    conversion = (document.get("contentProvenance") or {}).get("conversion") or {}
    if conversion.get("status") != "converted" or conversion.get("reviewRequired"):
        errors.append("detection must be converted with no review required")
    if errors:
        raise ValueError("; ".join(errors))
    properties = deepcopy(document["properties"])
    properties["@odata.type"] = "#microsoft.graph.security.detectionRule"
    properties["status"] = "disabled"
    return properties


def deploy_solution(
    solution: str | Path,
    *,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    target = require_locked_target(root)
    output = root / "XDR Detections"
    files = xdr_detection_files(output)
    if not files:
        raise ValueError(f"no generated XDR Detection YAML files found under {output}")
    token = _deployment_token(state_dir, tenant_id=target["tenantId"])
    results: list[dict[str, Any]] = []
    for path in files:
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
            payload = graph_detection_payload(document)
            rule_id = urllib.parse.quote(payload["id"], safe="")
            item_url = f"{DEPLOYMENT_ENDPOINT}/{rule_id}"
            status, current = _graph_request("GET", item_url, token)
            if status == 404:
                response_status, response = _graph_request(
                    "POST", DEPLOYMENT_ENDPOINT, token, payload
                )
                operation = "created"
                success = response_status == 201
            elif status == 200:
                update = {key: value for key, value in payload.items() if key not in {"id", "@odata.type"}}
                response_status, response = _graph_request(
                    "PATCH", item_url, token, update
                )
                operation = "updated"
                success = response_status == 200
            else:
                response_status, response = status, current
                operation = "failed"
                success = False
            error = response.get("error") if isinstance(response, dict) else None
            deployed_status = None
            if success:
                verify_status, verified = _graph_request("GET", item_url, token)
                deployed_status = (
                    str(verified.get("status") or "").lower()
                    if isinstance(verified, dict)
                    else ""
                )
                if verify_status != 200 or deployed_status != "disabled":
                    success = False
                    operation = "failed"
                    error = {
                        "code": "DeploymentVerificationFailed",
                        "message": "deployed Custom Detection was not verified as disabled",
                        "statusCode": verify_status,
                        "response": verified,
                    }
            results.append(
                {
                    "file": str(path),
                    "id": payload["id"],
                    "operation": operation if success else "failed",
                    "statusCode": response_status,
                    "success": success,
                    "deployedStatus": deployed_status,
                    "error": error,
                }
            )
        except (OSError, ValueError, yaml.YAMLError) as exc:
            results.append(
                {
                    "file": str(path),
                    "id": None,
                    "operation": "failed",
                    "statusCode": 0,
                    "success": False,
                    "error": {"message": str(exc)},
                }
            )
    report = {
        "solution": str(root),
        "provider": "microsoft-graph-beta",
        "target": target,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "succeeded": sum(result["success"] for result in results),
        "failed": sum(not result["success"] for result in results),
        "results": results,
    }
    report_path = artifact_path(root, "deployment.graph.json", create_parent=True)
    report["reportPath"] = str(report_path)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
