from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from solution_manager.core.artifacts import artifact_path, write_json_artifact
from solution_manager.migration.converter import xdr_detection_files
from solution_manager.qualification.graph_readiness import (
    graph_detection_payload_with_projection,
)
from solution_manager.qualification.graph_auth import (
    credential_token_scope,
    validate_delegated_graph_claims,
)
from solution_manager.qualification.graph_client_config import (
    azure_cli_credential,
    azure_cli_profile,
    configure_azure_cli_profile,
    configure_graph_client,
    configured_azure_cli_profile,
    ensure_private_state_root,
    graph_auth_record_path,
    graph_token_cache_name,
    resolve_graph_client_id,
    restrict_private_permissions,
    verify_graph_auth_binding,
    write_graph_auth_metadata,
)
from solution_manager.core.onboarding import (
    GRAPH_CLIENT_ID,
    _load_auth_record,
    _read_json,
    _state_dir,
)
from solution_manager.core.target_context import require_locked_target

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
    client_id: str | None = None,
):
    from azure.identity import (
        DeviceCodeCredential,
        InteractiveBrowserCredential,
        TokenCachePersistenceOptions,
    )

    selected_client_id = resolve_graph_client_id(
        state_root, "customDetection", client_id
    )
    record_path = graph_auth_record_path(
        state_root,
        "customDetection",
        selected_client_id,
        DEPLOYMENT_AUTH_RECORD_NAME,
    )
    record = _load_auth_record(record_path)
    config = _read_json(state_root / "config.json")
    if record is not None:
        verify_graph_auth_binding(
            record_path,
            record,
            purpose="customDetection",
            client_id=selected_client_id,
            tenant_id=tenant_id or config.get("tenantId"),
        )
    common: dict[str, Any] = {
        "client_id": selected_client_id,
        "tenant_id": tenant_id
        or config.get("tenantId")
        or getattr(record, "tenant_id", None),
        "authentication_record": record,
        "cache_persistence_options": TokenCachePersistenceOptions(
            name=graph_token_cache_name(
                "customDetection", selected_client_id, DEPLOYMENT_TOKEN_CACHE_NAME
            )
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
    graph_client_id: str | None = None,
    azure_config_dir: str | Path | None = None,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    state_root = _state_dir(state_dir)
    ensure_private_state_root(state_root)
    selected_client_id = resolve_graph_client_id(
        state_root, "customDetection", graph_client_id
    )
    if auth_method == "azure-cli" and selected_client_id != GRAPH_CLIENT_ID:
        raise ValueError(
            "Azure CLI authentication uses the Azure CLI client, not the "
            "configured custom Graph client; use device-code or browser."
        )
    if graph_client_id:
        configure_graph_client(state_root, "customDetection", graph_client_id)
    if azure_config_dir is not None:
        configure_azure_cli_profile(state_root, azure_config_dir)
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
        with azure_cli_profile(
            azure_config_dir or configured_azure_cli_profile(state_root)
        ):
            result = subprocess.run(command, check=False)
        if result.returncode:
            raise RuntimeError("Azure CLI Custom Detection authentication failed")
        token = _deployment_token(state_root, require_record=False, tenant_id=tenant_id)
        return {
            "status": "completed",
            "tenantId": tenant_id,
            "username": None,
            "scope": DEPLOYMENT_SCOPE,
            "authMethod": auth_method,
            "clientId": None,
            "azureConfigDir": configured_azure_cli_profile(state_root),
            "tokenAcquired": bool(token),
        }
    credential = _deployment_credential(
        state_root,
        interactive=True,
        auth_method=auth_method,
        tenant_id=tenant_id,
        client_id=selected_client_id,
    )
    try:
        record = credential.authenticate(scopes=[DEPLOYMENT_SCOPE])
        access_token = credential.get_token(DEPLOYMENT_SCOPE).token
        scope_diagnostics = _validate_deployment_token(
            access_token,
            tenant_id=tenant_id or getattr(record, "tenant_id", None) or "",
        )
    except Exception as exc:
        raise RuntimeError(
            f"Custom Detection authentication failed: {exc}"
        ) from exc
    record_path = graph_auth_record_path(
        state_root,
        "customDetection",
        selected_client_id,
        DEPLOYMENT_AUTH_RECORD_NAME,
    )
    record_path.write_text(
        record.serialize(), encoding="utf-8"
    )
    restrict_private_permissions(record_path, 0o600)
    write_graph_auth_metadata(
        record_path,
        purpose="customDetection",
        client_id=selected_client_id,
        tenant_id=getattr(record, "tenant_id", None) or tenant_id,
    )
    return {
        "status": "completed",
        "tenantId": getattr(record, "tenant_id", None),
        "username": getattr(record, "username", None),
        "scope": DEPLOYMENT_SCOPE,
        "authMethod": auth_method,
        "clientId": selected_client_id,
        "azureConfigDir": configured_azure_cli_profile(state_root),
        "scopeDiagnostics": scope_diagnostics["delegatedScopes"],
    }


def _validate_deployment_token(
    token: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    from solution_manager.qualification.graph_readiness import _token_claims

    return validate_delegated_graph_claims(
        _token_claims(token),
        tenant_id=tenant_id,
        required_scopes=(DEPLOYMENT_SCOPE,),
        purpose="Custom Detection",
    )


def _deployment_token(
    state_dir: str | Path | None = None,
    *,
    require_record: bool = False,
    tenant_id: str | None = None,
) -> str:
    state_root = _state_dir(state_dir)
    client_id = resolve_graph_client_id(state_root, "customDetection")
    record_path = graph_auth_record_path(
        state_root, "customDetection", client_id, DEPLOYMENT_AUTH_RECORD_NAME
    )
    if record_path.exists():
        credential = _deployment_credential(
            state_root, tenant_id=tenant_id, client_id=client_id
        )
        token = credential.get_token(DEPLOYMENT_SCOPE).token
    elif not require_record:
        if client_id != GRAPH_CLIENT_ID:
            raise RuntimeError(
                "the configured custom Graph client has no cached Custom Detection "
                "authentication; run setup-deployment with device-code or browser"
            )
        try:
            token = azure_cli_credential(
                tenant_id=tenant_id, state_root=state_root
            ).get_token(
                credential_token_scope("azure-cli", DEPLOYMENT_SCOPE)
            ).token
        except Exception:
            token = None
    else:
        token = None
    if token is None:
        raise RuntimeError(
            "Custom Detection deployment authentication is missing; run "
            "`sentinel-xdr-migration setup-deployment --auth-method azure-cli` first"
        )
    _validate_deployment_token(token, tenant_id=tenant_id or "")
    return token


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


def graph_detection_payload(
    document: dict[str, Any], *, package_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    payload, _projection = graph_detection_payload_with_projection(
        document, package_context=package_context,
    )
    return payload


def _normalize_graph_tactics(tactics: Any) -> Any:
    """Drop the empty ``subTechniques`` list that live Graph adds on readback."""
    if isinstance(tactics, list):
        return [_normalize_graph_tactics(item) for item in tactics]
    if isinstance(tactics, dict):
        return {
            key: _normalize_graph_tactics(value)
            for key, value in tactics.items()
            if not (key == "subTechniques" and value in ([], None))
        }
    return tactics


def _graph_provenance_matches(verified: Any, expected: Any) -> bool:
    """Live Graph beta omits contentProvenance; an echoed value must still match."""
    if not isinstance(verified, dict):
        return False
    if "contentProvenance" not in verified or verified["contentProvenance"] is None:
        return True
    return verified["contentProvenance"] == expected


def deploy_solution(
    solution: str | Path,
    *,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    report_path = artifact_path(root, "deployment.graph.json", create_parent=True)
    target = require_locked_target(root)
    output = root / "XDR Detections"
    files = xdr_detection_files(output)
    from solution_manager.packaging.packaging_selection import current_applied_package_selection

    applied_selection = current_applied_package_selection(root)
    if applied_selection is not None:
        selected_paths = {
            str(value).replace("\\", "/").casefold()
            for value in (applied_selection["plan"].get("selection") or {}).get(
                "xdrDetections", []
            )
        }
        files_by_path = {
            path.relative_to(root).as_posix().casefold(): path for path in files
        }
        if not selected_paths or not selected_paths.issubset(files_by_path):
            raise ValueError("current applied package selection has missing Custom Detection files")
        files = [files_by_path[path] for path in sorted(selected_paths)]
    if not files:
        raise ValueError(f"no generated XDR Detection YAML files found under {output}")
    from solution_manager.authoring.dependencies import solution_package_context

    package_context = solution_package_context(root)
    token = _deployment_token(state_dir, tenant_id=target["tenantId"])
    results: list[dict[str, Any]] = []
    for path in files:
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
            payload, tactic_projection = graph_detection_payload_with_projection(
                document, package_context=package_context,
            )
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
            tactic_projection_verified = None
            provenance_verified = None
            if success:
                verify_status, verified = _graph_request("GET", item_url, token)
                deployed_status = (
                    str(verified.get("status") or "").lower()
                    if isinstance(verified, dict)
                    else ""
                )
                projected_tactics = (
                    ((payload.get("detectionAction") or {}).get("alertTemplate") or {}).get(
                        "tactics"
                    )
                    or []
                )
                verified_tactics = (
                    (
                        ((verified.get("detectionAction") or {}).get("alertTemplate") or {})
                    ).get("tactics")
                    or []
                    if isinstance(verified, dict)
                    else []
                )
                tactic_projection_verified = _normalize_graph_tactics(
                    verified_tactics
                ) == _normalize_graph_tactics(projected_tactics)
                provenance_verified = _graph_provenance_matches(
                    verified, payload["contentProvenance"]
                )
                if (
                    verify_status != 200
                    or deployed_status != "disabled"
                    or not tactic_projection_verified
                    or not provenance_verified
                ):
                    success = False
                    operation = "failed"
                    error = {
                        "code": "DeploymentVerificationFailed",
                        "message": (
                            "deployed Custom Detection did not match its disabled "
                            "status, projected tactic payload and content provenance"
                        ),
                        "statusCode": verify_status,
                        "tacticProjectionVerified": tactic_projection_verified,
                        "contentProvenanceVerified": provenance_verified,
                    }
            results.append(
                {
                    "file": str(path),
                    "id": payload["id"],
                    "operation": operation if success else "failed",
                    "statusCode": response_status,
                    "success": success,
                    "deployedStatus": deployed_status,
                    "tacticProjection": tactic_projection,
                    "tacticProjectionVerified": tactic_projection_verified,
                    "contentProvenanceVerified": provenance_verified,
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
    if applied_selection is not None:
        report["qualificationScope"] = {
            "kind": "applied-package-selection",
            "planSha256": applied_selection["plan"].get("planSha256"),
            "outcome": (applied_selection["plan"].get("summary") or {}).get("outcome"),
            "selectedDetectionPaths": sorted(
                str(value).replace("\\", "/")
                for value in (applied_selection["plan"].get("selection") or {}).get(
                    "xdrDetections", []
                )
            ),
            "coverage": applied_selection["plan"].get("summary"),
        }
    report["reportPath"] = str(report_path)
    write_json_artifact(root, report_path, report)
    return report
