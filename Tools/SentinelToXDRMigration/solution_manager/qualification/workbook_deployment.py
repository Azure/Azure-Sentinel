from __future__ import annotations

from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any
import urllib.parse

from solution_manager.core.artifacts import artifact_path, write_json_artifact
from solution_manager.core.onboarding import (
    GRAPH_CLIENT_ID,
    _load_auth_record,
    _read_json,
    _state_dir,
)
from solution_manager.core.target_context import require_locked_target
from solution_manager.qualification.deployment import (
    MAX_GRAPH_DEPLOY_WORKERS,
    _graph_request,
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

WORKBOOK_DEPLOYMENT_SCOPE = "https://graph.microsoft.com/Workbooks.ReadWrite.All"
WORKBOOK_READ_SCOPE = "https://graph.microsoft.com/Workbooks.Read.All"
WORKBOOK_DEPLOYMENT_ENDPOINT = (
    "https://graph.microsoft.com/beta/security/workbooks"
)
WORKBOOK_AUTH_RECORD_NAME = "workbooks-auth-record.json"
WORKBOOK_TOKEN_CACHE_NAME = "sentinel_xdr_migration_workbooks"
_GUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def xdr_workbook_files(directory: str | Path) -> list[Path]:
    root = Path(directory)
    if not root.is_dir():
        return []
    return sorted(
        (
            path
            for path in root.rglob("*.json")
            if path.is_file() and not path.name.startswith(".")
        ),
        key=lambda item: item.as_posix().casefold(),
    )


def _validate_guid(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not _GUID_PATTERN.fullmatch(value.strip()):
        raise ValueError(f"{field_name} must be a valid GUID")
    return value.strip().lower()


def graph_workbook_payload(
    document: dict[str, Any],
    *,
    package_context: dict[str, str] | None = None,
) -> tuple[str, dict[str, Any], dict[str, str]]:
    """Build a Microsoft Graph security workbook PATCH body from an XDR Workbook JSON document.

    Graph contract (`PATCH https://graph.microsoft.com/beta/security/workbooks/{workbookId}`):
    - URL `{workbookId}` is `xdrMetadata.instanceId`
    - Request body contains only `{"name": <displayName>, "content": <Notebook/1.0 JSON object>}`
    - Must not supply `id`, `etag`, `createdByUpn`, `lastUpdatedByUpn`, `createdAtDateTime`, or `updatedAtDateTime` in body
    """
    if not isinstance(document, dict):
        raise ValueError("workbook document must be a JSON object")
    if document.get("version") != "Notebook/1.0":
        raise ValueError("workbook document version must be 'Notebook/1.0'")
    if not isinstance(document.get("items"), list):
        raise ValueError("workbook document must contain an 'items' list")

    xdr_meta = document.get("xdrMetadata")
    if not isinstance(xdr_meta, dict):
        raise ValueError("workbook document is missing 'xdrMetadata'")
    content_id = _validate_guid(
        xdr_meta.get("contentId"), field_name="xdrMetadata.contentId"
    )
    instance_id = _validate_guid(
        xdr_meta.get("instanceId"), field_name="xdrMetadata.instanceId"
    )
    display_name = xdr_meta.get("displayName")
    if not isinstance(display_name, str) or not display_name.strip():
        raise ValueError("xdrMetadata.displayName must be a non-empty string")
    display_name = display_name.strip()

    provenance = document.get("contentProvenance")
    if not isinstance(provenance, dict):
        raise ValueError("workbook document is missing 'contentProvenance'")
    conversion = provenance.get("conversion")
    if isinstance(conversion, dict):
        status = conversion.get("status")
        if status == "needsReview" or bool(conversion.get("reviewRequired")):
            raise ValueError(
                "workbook must have no unresolved conversion reviewRequired items"
            )

    notebook = deepcopy(document)
    notebook.pop("xdrMetadata", None)
    if package_context is not None:
        package_id = str(package_context.get("packageId") or "").strip()
        package_version = str(package_context.get("packageVersion") or "").strip()
        if not package_id or not package_version:
            raise ValueError(
                "package_context must provide non-empty packageId and packageVersion"
            )
        notebook["contentProvenance"] = {
            "packageId": package_id,
            "packageVersion": package_version,
            "contentId": content_id,
            "contentVersion": package_version,
        }
    else:
        notebook.pop("contentProvenance", None)

    payload = {
        "name": display_name,
        "content": notebook,
    }
    metadata = {
        "contentId": content_id,
        "instanceId": instance_id,
        "displayName": display_name,
    }
    return instance_id, payload, metadata


def _workbook_deployment_credential(
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
        state_root, "workbooks", client_id
    )
    record_path = graph_auth_record_path(
        state_root,
        "workbooks",
        selected_client_id,
        WORKBOOK_AUTH_RECORD_NAME,
    )
    record = _load_auth_record(record_path)
    config = _read_json(state_root / "config.json")
    if record is not None:
        verify_graph_auth_binding(
            record_path,
            record,
            purpose="workbooks",
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
                "workbooks", selected_client_id, WORKBOOK_TOKEN_CACHE_NAME
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


def _validate_workbook_deployment_token(
    token: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    from solution_manager.qualification.graph_readiness import _token_claims

    return validate_delegated_graph_claims(
        _token_claims(token),
        tenant_id=tenant_id,
        required_scopes=(WORKBOOK_DEPLOYMENT_SCOPE,),
        purpose="Defender Workbook",
    )


def _workbook_deployment_token(
    state_dir: str | Path | None = None,
    *,
    require_record: bool = False,
    tenant_id: str | None = None,
) -> str:
    state_root = _state_dir(state_dir)
    client_id = resolve_graph_client_id(state_root, "workbooks")
    record_path = graph_auth_record_path(
        state_root, "workbooks", client_id, WORKBOOK_AUTH_RECORD_NAME
    )
    if record_path.exists():
        credential = _workbook_deployment_credential(
            state_root, tenant_id=tenant_id, client_id=client_id
        )
        token = credential.get_token(WORKBOOK_DEPLOYMENT_SCOPE).token
    elif not require_record:
        if client_id != GRAPH_CLIENT_ID:
            raise RuntimeError(
                "the configured custom Graph client has no cached Defender Workbook "
                "authentication; run setup-workbook-deployment with device-code or browser"
            )
        try:
            token = azure_cli_credential(
                tenant_id=tenant_id, state_root=state_root
            ).get_token(
                credential_token_scope("azure-cli", WORKBOOK_DEPLOYMENT_SCOPE)
            ).token
        except Exception:
            token = None
    else:
        token = None
    if token is None:
        raise RuntimeError(
            "Defender Workbook deployment authentication is missing; run "
            "`sentinel-xdr-migration setup-workbook-deployment --auth-method azure-cli` first"
        )
    _validate_workbook_deployment_token(token, tenant_id=tenant_id or "")
    return token


def setup_workbook_deployment_authentication(
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
        state_root, "workbooks", graph_client_id
    )
    if auth_method == "azure-cli" and selected_client_id != GRAPH_CLIENT_ID:
        raise ValueError(
            "Azure CLI authentication uses the Azure CLI client, not the "
            "configured custom Graph client; use device-code or browser."
        )
    if graph_client_id:
        configure_graph_client(state_root, "workbooks", graph_client_id)
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
            WORKBOOK_DEPLOYMENT_SCOPE,
        ]
        if tenant_id:
            command.extend(["--tenant", tenant_id])
        with azure_cli_profile(
            azure_config_dir or configured_azure_cli_profile(state_root)
        ):
            result = subprocess.run(command, check=False)
        if result.returncode:
            raise RuntimeError("Azure CLI Defender Workbook authentication failed")
        token = _workbook_deployment_token(
            state_root, require_record=False, tenant_id=tenant_id
        )
        return {
            "status": "completed",
            "tenantId": tenant_id,
            "username": None,
            "scope": WORKBOOK_DEPLOYMENT_SCOPE,
            "authMethod": auth_method,
            "clientId": None,
            "azureConfigDir": configured_azure_cli_profile(state_root),
            "tokenAcquired": bool(token),
        }
    credential = _workbook_deployment_credential(
        state_root,
        interactive=True,
        auth_method=auth_method,
        tenant_id=tenant_id,
        client_id=selected_client_id,
    )
    try:
        record = credential.authenticate(scopes=[WORKBOOK_DEPLOYMENT_SCOPE])
        access_token = credential.get_token(WORKBOOK_DEPLOYMENT_SCOPE).token
        scope_diagnostics = _validate_workbook_deployment_token(
            access_token,
            tenant_id=tenant_id or getattr(record, "tenant_id", None) or "",
        )
    except Exception as exc:
        raise RuntimeError(
            f"Defender Workbook authentication failed: {exc}"
        ) from exc
    record_path = graph_auth_record_path(
        state_root,
        "workbooks",
        selected_client_id,
        WORKBOOK_AUTH_RECORD_NAME,
    )
    record_path.write_text(record.serialize(), encoding="utf-8")
    restrict_private_permissions(record_path, 0o600)
    write_graph_auth_metadata(
        record_path,
        purpose="workbooks",
        client_id=selected_client_id,
        tenant_id=getattr(record, "tenant_id", None) or tenant_id,
    )
    return {
        "status": "completed",
        "tenantId": getattr(record, "tenant_id", None),
        "username": getattr(record, "username", None),
        "scope": WORKBOOK_DEPLOYMENT_SCOPE,
        "authMethod": auth_method,
        "clientId": selected_client_id,
        "azureConfigDir": configured_azure_cli_profile(state_root),
        "scopeDiagnostics": scope_diagnostics["delegatedScopes"],
    }


def _verify_workbook_readback(
    verified: Any,
    *,
    expected_instance_id: str,
    expected_payload: dict[str, Any],
) -> tuple[bool, bool]:
    if not isinstance(verified, dict):
        return False, False
    returned_id = str(verified.get("id") or "").strip()
    if returned_id.casefold() != expected_instance_id.casefold():
        return False, False
    if verified.get("name") != expected_payload.get("name"):
        return False, False
    content = verified.get("content")
    if not isinstance(content, dict) or content.get("version") != "Notebook/1.0":
        return False, False
    if not isinstance(content.get("items"), list):
        return False, False
    expected_provenance = (expected_payload.get("content") or {}).get(
        "contentProvenance"
    )
    actual_provenance = content.get("contentProvenance")
    provenance_verified = (
        actual_provenance is None or actual_provenance == expected_provenance
    )
    return True, provenance_verified


def ensure_source_workbooks_unchanged(
    solution: str | Path,
    *,
    files: list[Path] | None = None,
) -> None:
    """Verify Sentinel source workbooks under Workbooks/ have not been modified after conversion."""
    root = Path(solution).expanduser().resolve()
    wb_files = (
        list(files)
        if files is not None
        else xdr_workbook_files(root / "XDR Workbooks")
    )
    checked_sources: dict[str, str] = {}
    for path in wb_files:
        if not path.is_file():
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(doc, Mapping):
            continue
        prov = doc.get("contentProvenance")
        if not isinstance(prov, Mapping):
            continue
        source = prov.get("source")
        if not isinstance(source, Mapping) and prov.get("format") == "public-workbook-v1":
            try:
                from solution_manager.authoring.workbook_publication import _receipt_path

                receipt_file = _receipt_path(root, dict(doc))
                if receipt_file.is_file():
                    receipt = json.loads(receipt_file.read_text(encoding="utf-8-sig"))
                    evidence = (receipt.get("evidence") or {}) if isinstance(receipt, Mapping) else {}
                    baseline_text = evidence.get("baselineArtifact") or evidence.get("inputArtifact")
                    if isinstance(baseline_text, str) and baseline_text.strip():
                        baseline_doc = json.loads(baseline_text)
                        if isinstance(baseline_doc, Mapping):
                            b_prov = baseline_doc.get("contentProvenance")
                            if isinstance(b_prov, Mapping):
                                source = b_prov.get("source")
                    if not isinstance(source, Mapping):
                        source_artifacts = evidence.get("sourceArtifacts")
                        if isinstance(source_artifacts, Mapping):
                            for s_rel, s_text in source_artifacts.items():
                                if isinstance(s_rel, str) and s_rel.strip() and isinstance(s_text, str):
                                    checked_sources[s_rel.strip().replace("\\", "/")] = (
                                        hashlib.sha256(s_text.encode("utf-8")).hexdigest().lower()
                                    )
            except Exception:
                source = None
        if isinstance(source, Mapping):
            src_rel = source.get("path")
            expected_sha = source.get("sha256")
            if (
                isinstance(src_rel, str)
                and src_rel.strip()
                and isinstance(expected_sha, str)
                and len(expected_sha.strip()) == 64
            ):
                checked_sources[src_rel.strip().replace("\\", "/")] = expected_sha.strip().lower()

    logs_root = root / "Logs" / "sentinel-xdr-migration"
    if logs_root.is_dir():
        for state_file in sorted(logs_root.glob("*/workflow-state.json")):
            try:
                state_doc = json.loads(state_file.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            wb_section = state_doc.get("workbooks") if isinstance(state_doc, Mapping) else None
            inventory = wb_section.get("inventory") if isinstance(wb_section, Mapping) else None
            if isinstance(inventory, list):
                for item in inventory:
                    if not isinstance(item, Mapping):
                        continue
                    src_rel = item.get("path") or item.get("sourcePath")
                    expected_sha = item.get("sha256") or item.get("sourceSha256")
                    if (
                        isinstance(src_rel, str)
                        and src_rel.strip()
                        and isinstance(expected_sha, str)
                        and len(expected_sha.strip()) == 64
                    ):
                        checked_sources[src_rel.strip().replace("\\", "/")] = (
                            expected_sha.strip().lower()
                        )

    for src_rel, expected_sha in sorted(checked_sources.items()):
        src_path = (root / src_rel).resolve()
        if not src_path.is_relative_to(root) or not src_path.is_file():
            continue
        actual_sha = hashlib.sha256(src_path.read_bytes()).hexdigest().lower()
        if actual_sha != expected_sha:
            raise ValueError(
                f"Sentinel source workbook '{src_rel}' was modified after conversion. "
                f"Never modify Sentinel source workbooks under Workbooks/ to fix Defender XDR issues; "
                f"revert '{src_rel}' and apply fixes only to 'XDR Workbooks/' via "
                f"workbook-update-plan, workbook-update-review, and workbook-update-apply."
            )


def deploy_workbooks(
    solution: str | Path,
    *,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Create or replace generated XDR Workbooks through Microsoft Graph beta and verify via GET readback."""
    root = Path(solution).expanduser().resolve()
    report_path = artifact_path(
        root, "deployment.workbooks.graph.json", create_parent=True
    )
    target = require_locked_target(root)
    output = root / "XDR Workbooks"
    files = xdr_workbook_files(output)
    ensure_source_workbooks_unchanged(root, files=files)
    from solution_manager.packaging.packaging_selection import (
        current_applied_package_selection,
    )

    applied_selection = current_applied_package_selection(root)
    if applied_selection is not None:
        selected_list = (applied_selection["plan"].get("selection") or {}).get(
            "xdrWorkbooks"
        )
        if isinstance(selected_list, list) and selected_list:
            selected_paths = {
                str(value).replace("\\", "/").casefold()
                for value in selected_list
            }
            files_by_path = {
                path.relative_to(root).as_posix().casefold(): path
                for path in files
            }
            if not selected_paths.issubset(files_by_path):
                raise ValueError(
                    "current applied package selection has missing XDR Workbook files"
                )
            files = [files_by_path[path] for path in sorted(selected_paths)]
    if not files:
        raise ValueError(f"no generated XDR Workbook JSON files found under {output}")

    from solution_manager.authoring.dependencies import solution_package_context

    package_context = solution_package_context(root)
    token = _workbook_deployment_token(state_dir, tenant_id=target["tenantId"])

    def _deploy_one(path: Path) -> dict[str, Any]:
        try:
            document = json.loads(path.read_text(encoding="utf-8-sig"))
            instance_id, payload, metadata = graph_workbook_payload(
                document, package_context=package_context
            )
            encoded_id = urllib.parse.quote(instance_id, safe="")
            item_url = f"{WORKBOOK_DEPLOYMENT_ENDPOINT}/{encoded_id}"
            # Graph beta security/workbooks supports client-selected GUID upsert via PATCH
            # returning 201 Created (new) or 200 OK (replaced).
            response_status, response = _graph_request(
                "PATCH", item_url, token, payload
            )
            if response_status == 201:
                operation = "created"
                success = True
            elif response_status == 200:
                operation = "updated"
                success = True
            else:
                operation = "failed"
                success = False

            error = response.get("error") if isinstance(response, dict) else None
            readback_verified = False
            provenance_verified = None
            if success:
                verify_status, verified = _graph_request("GET", item_url, token)
                content_ok, provenance_verified = _verify_workbook_readback(
                    verified,
                    expected_instance_id=instance_id,
                    expected_payload=payload,
                )
                readback_verified = bool(
                    verify_status == 200 and content_ok and provenance_verified
                )
                if not readback_verified:
                    success = False
                    operation = "failed"
                    error = {
                        "code": "WorkbookDeploymentVerificationFailed",
                        "message": (
                            "deployed Defender Workbook did not match its expected "
                            "instanceId, displayName, Notebook/1.0 content, or provenance on GET readback"
                        ),
                        "statusCode": verify_status,
                        "contentProvenanceVerified": provenance_verified,
                    }

            return {
                "file": str(path),
                "id": instance_id,
                "contentId": metadata["contentId"],
                "displayName": metadata["displayName"],
                "portalUrl": f"https://security.microsoft.com/workbook/{instance_id}?tid={target['tenantId']}",
                "operation": operation if success else "failed",
                "statusCode": response_status,
                "success": success,
                "readbackVerified": readback_verified,
                "contentProvenanceVerified": provenance_verified,
                "error": error,
            }
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return {
                "file": str(path),
                "id": None,
                "contentId": None,
                "displayName": None,
                "operation": "failed",
                "statusCode": None,
                "success": False,
                "readbackVerified": False,
                "contentProvenanceVerified": None,
                "error": {"message": str(exc)},
            }

    if len(files) <= 1:
        results = [_deploy_one(path) for path in files]
    else:
        with ThreadPoolExecutor(
            max_workers=min(MAX_GRAPH_DEPLOY_WORKERS, len(files))
        ) as pool:
            results = list(pool.map(_deploy_one, files))

    succeeded = sum(1 for item in results if item["success"])
    failed = len(results) - succeeded
    all_readback_verified = bool(
        results and all(item.get("readbackVerified") for item in results)
    )
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "solution": str(root),
        "endpoint": WORKBOOK_DEPLOYMENT_ENDPOINT,
        "status": "passed" if failed == 0 and all_readback_verified else "failed",
        "deployed": succeeded,
        "failed": failed,
        "readbackReconciliation": {
            "status": "passed" if failed == 0 and all_readback_verified else "failed",
            "httpMethod": "GET",
            "readbackVerified": all_readback_verified,
        },
        "results": results,
        "reportPath": str(report_path),
    }
    write_json_artifact(root, report_path, report)
    return report
