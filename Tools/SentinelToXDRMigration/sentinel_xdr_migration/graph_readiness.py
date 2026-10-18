from __future__ import annotations

import base64
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from .converter import (
    PREFIXED_SOURCE_ID_PATTERN,
    SOURCE_ID_PATTERN,
    is_sentinel_derived,
    validate_document,
    xdr_detection_files,
)
from .dcr_readiness import preflight_dcr_permissions
from .deployment_planning import build_deployment_plan
from .graph_auth import (
    GRAPH_RESOURCE,
    GRAPH_RESOURCE_DEFAULT_SCOPE,
    credential_token_scope,
    delegated_graph_claim_diagnostics,
    delegated_scope_diagnostics,
)
from .onboarding import GRAPH_CLIENT_ID, _state_dir
from .graph_client_config import (
    azure_cli_credential,
    azure_cli_profile,
    configured_azure_cli_profile,
    graph_auth_record_path,
    resolve_graph_client_id,
)
from .target_context import require_locked_target

AZURE_CLI_GRAPH_SCOPE = GRAPH_RESOURCE_DEFAULT_SCOPE
GRAPH_AUDIENCE_CLAIM = "00000003-0000-0000-c000-000000000000"
GRAPH_DETECTION_RULES_ENDPOINT = (
    "https://graph.microsoft.com/beta/security/rules/detectionRules"
)
WRITE_SCOPE = "https://graph.microsoft.com/CustomDetection.ReadWrite.All"
READ_SCOPE = "https://graph.microsoft.com/CustomDetection.Read.All"
AUTH_RECORD_NAME = "custom-detection-auth-record.json"
DEFAULT_READ_BUDGET = 20
DEFAULT_REQUEST_TIMEOUT_SECONDS = 15


def _detection_id(prepared: dict[str, Any]) -> None:
    properties = prepared.get("properties") or {}
    detection_id = properties.get("id")
    source_id = (
        ((prepared.get("contentProvenance") or {}).get("source") or {}).get("id")
    )
    if isinstance(detection_id, str) and re.fullmatch(
        SOURCE_ID_PATTERN, detection_id
    ):
        if is_sentinel_derived(prepared) and (
            not isinstance(source_id, str)
            or detection_id.casefold() != source_id.casefold()
        ):
            return
        properties["id"] = (
            f"xdr-{source_id if is_sentinel_derived(prepared) else detection_id}"
        )
    elif isinstance(detection_id, str):
        match = re.fullmatch(PREFIXED_SOURCE_ID_PATTERN, detection_id)
        if match:
            guid = detection_id[4:]
            if is_sentinel_derived(prepared) and (
                not isinstance(source_id, str) or guid.casefold() != source_id.casefold()
            ):
                return
            properties["id"] = (
                f"xdr-{source_id if is_sentinel_derived(prepared) else guid}"
            )


def _technique_ids(tactics: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if not isinstance(tactics, list):
        return result
    for item in tactics:
        if not isinstance(item, dict):
            continue
        techniques: list[str] = []
        for technique in item.get("techniques") or []:
            if not isinstance(technique, dict):
                continue
            base = technique.get("technique")
            if isinstance(base, str) and base:
                techniques.append(base)
            subtechniques = technique.get("subTechniques") or []
            if isinstance(subtechniques, list):
                techniques.extend(
                    value
                    for value in subtechniques
                    if isinstance(value, str) and value
                )
        result.append(
            {
                "tactic": item.get("tactic"),
                "techniques": techniques,
            }
        )
    return result


def project_graph_tactics(
    alert_template: dict[str, Any],
) -> dict[str, Any]:
    """Project the authored tactics to the V3.1 single-tactic Graph contract.

    The first authored tactic and its complete nested techniques/subtechniques
    are retained. This is an API-shape projection, not classification parity.
    The caller must keep the authored document and provenance unchanged.
    """
    authored = alert_template.get("tactics")
    source_tactics = authored if isinstance(authored, list) else []
    projected = deepcopy(source_tactics[:1])
    omitted = deepcopy(source_tactics[1:])
    diagnostic = {
        "status": "projected" if omitted else "not-required",
        "reason": (
            "Graph Custom Detection deployment uses the V3.1 single-tactic "
            "projection: preserve the first authored tactic and all techniques "
            "nested under it; omit later tactics and their techniques."
        ),
        "authoredTactics": [
            item.get("tactic") if isinstance(item, dict) else None
            for item in source_tactics
        ],
        "projectedTactics": [
            item.get("tactic") if isinstance(item, dict) else None
            for item in projected
        ],
        "omittedTactics": [
            item.get("tactic") if isinstance(item, dict) else None
            for item in omitted
        ],
        "projectedTechniques": _technique_ids(projected),
        "omittedTechniques": _technique_ids(omitted),
        "classificationParity": "not-established",
    }
    if isinstance(authored, list):
        alert_template["tactics"] = projected
    return diagnostic


def graph_detection_payload_with_projection(
    document: dict[str, Any],
    *, package_context: dict[str, str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build a disabled Graph payload and return explicit projection diagnostics."""
    prepared = deepcopy(document)
    _detection_id(prepared)
    errors = validate_document(prepared)
    conversion = (document.get("contentProvenance") or {}).get("conversion") or {}
    if conversion.get("status") != "converted" or conversion.get("reviewRequired"):
        errors.append("detection must be converted with no review required")
    if errors:
        raise ValueError("; ".join(errors))

    properties = prepared["properties"]
    alert = (
        (properties.get("detectionAction") or {}).get("alertTemplate") or {}
    )
    projection = project_graph_tactics(alert)
    result = deepcopy(properties)
    if isinstance(result.get("schedule"), dict) and result["schedule"].get("frequency") == "NRT":
        result["schedule"]["frequency"] = "PT0S"
    result["@odata.type"] = "#microsoft.graph.security.detectionRule"
    result["status"] = "disabled"
    if package_context is not None:
        from .dependencies import deployed_provenance

        result["contentProvenance"] = deployed_provenance(prepared, package_context)
    return result, projection


def graph_detection_payload(
    document: dict[str, Any], *, package_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Compatibility wrapper returning only the projected Graph request body."""
    payload, _ = graph_detection_payload_with_projection(document, package_context=package_context)
    return payload


def _token_claims(token: str) -> dict[str, Any] | None:
    parts = token.split(".")
    if len(parts) < 2:
        return None
    try:
        encoded = parts[1]
        encoded += "=" * (-len(encoded) % 4)
        value = json.loads(base64.urlsafe_b64decode(encoded.encode("ascii")))
    except (ValueError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _claim_permissions(claims: dict[str, Any] | None) -> dict[str, Any]:
    if claims is None:
        return {
            "status": "unknown",
            "grantType": "unknown",
            "claimType": "unknown",
            "permissions": {},
        }

    scopes_present = "scp" in claims
    roles_present = "roles" in claims
    scopes = claims.get("scp")
    roles = claims.get("roles")
    scopes_valid = isinstance(scopes, str) and bool(scopes.strip())
    roles_valid = isinstance(roles, list) and all(
        isinstance(value, str) for value in roles
    )
    if (scopes_present and not scopes_valid) or (roles_present and not roles_valid):
        return {
            "status": "unknown",
            "grantType": "unknown",
            "claimType": "malformed",
            "permissions": {},
            "delegatedScopeDiagnostics": delegated_scope_diagnostics(
                scopes, (WRITE_SCOPE,)
            ),
        }
    if not scopes_present and not roles_present:
        return {
            "status": "unknown",
            "grantType": "unknown",
            "claimType": "missing",
            "permissions": {},
            "delegatedScopeDiagnostics": delegated_scope_diagnostics(
                None, (WRITE_SCOPE,)
            ),
        }

    delegated_scope_diagnostics_value = delegated_scope_diagnostics(
        scopes if scopes_present else None,
        (WRITE_SCOPE,),
    )
    if delegated_scope_diagnostics_value["claimStatus"] == "malformed":
        return {
            "status": "unknown",
            "grantType": "unknown",
            "claimType": "malformed",
            "permissions": {},
            "delegatedScopeDiagnostics": delegated_scope_diagnostics_value,
        }
    delegated_scopes = {
        value.casefold()
        for value in delegated_scope_diagnostics_value["actualScopeNames"]
    }
    application_roles = {
        value.casefold() for value in roles
    } if roles_valid else set()
    required = "customdetection.readwrite.all"
    if delegated_scopes and application_roles:
        grant_type = "delegated-and-application"
        claim_type = "scp+roles"
    elif delegated_scopes:
        grant_type = "delegated"
        claim_type = "scp"
    else:
        grant_type = "application"
        claim_type = "roles"
    grant_present = required in delegated_scopes
    permissions = {
        "customdetection.read.all": (
            "present-in-token"
            if "customdetection.read.all" in delegated_scopes
            else "not-present-in-token"
        ),
        required: "present-in-token" if grant_present else "not-present-in-token",
    }
    return {
        "status": "ready" if grant_present else "missing",
        "grantType": grant_type,
        "claimType": claim_type,
        "permissions": permissions,
        "delegatedScopeDiagnostics": delegated_scope_diagnostics_value,
    }


def _graph_get(
    url: str,
    token: str,
    *,
    timeout_seconds: int,
) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            content = response.read(1_000_001).decode("utf-8", errors="replace")
            if len(content) > 1_000_000:
                return response.status, {"error": {"code": "ResponseTooLarge"}}
            try:
                value = json.loads(content) if content else {}
            except json.JSONDecodeError:
                value = {"error": {"code": "InvalidJsonResponse"}}
            return response.status, value if isinstance(value, dict) else {
                "error": {"code": "UnexpectedResponseShape"}
            }
    except urllib.error.HTTPError as exc:
        content = exc.read(65_537).decode("utf-8", errors="replace")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"error": {"code": "HttpError"}}
        return exc.code, parsed if isinstance(parsed, dict) else {}
    except (TimeoutError, urllib.error.URLError):
        return 0, {"error": {"code": "NetworkError"}}


def _get_cached_credential(
    *,
    auth_method: str,
    state_dir: str | Path | None,
    tenant_id: str,
):
    from .deployment import _deployment_credential

    state_root = _state_dir(state_dir)
    if auth_method == "azure-cli":
        if resolve_graph_client_id(
            state_root, "customDetection"
        ) != GRAPH_CLIENT_ID:
            return None
        return azure_cli_credential(
            tenant_id=tenant_id, state_root=state_root
        )
    if auth_method in {"device-code", "browser"}:
        client_id = resolve_graph_client_id(state_root, "customDetection")
        record_path = graph_auth_record_path(
            state_root, "customDetection", client_id, AUTH_RECORD_NAME
        )
        if not record_path.is_file():
            return None
        return _deployment_credential(
            state_root,
            auth_method=auth_method,
            tenant_id=tenant_id,
            client_id=client_id,
        )
    raise ValueError("auth_method must be explicitly set to azure-cli, device-code, or browser")


def _token_diagnostics(
    claims: dict[str, Any] | None,
    target_tenant_id: str,
    required_scope: str = WRITE_SCOPE,
) -> dict[str, Any]:
    graph_claims = delegated_graph_claim_diagnostics(
        claims,
        tenant_id=target_tenant_id,
        required_scopes=(required_scope,),
    )
    if claims is None:
        return {
            "tenantMatch": "unknown",
            "graphAudience": "unknown",
            "permissions": {
                "status": "unknown",
                "delegatedScopes": "unknown",
                "applicationRoles": "unknown",
                "delegatedScopeDiagnostics": graph_claims["delegatedScopes"],
            },
            "delegatedScopeDiagnostics": graph_claims["delegatedScopes"],
            "managementPermissionGrant": {
                "status": "unknown",
                "grantType": "unknown",
                "claimType": "unknown",
            },
        }
    claim_info = _claim_permissions(claims)
    permissions = dict(claim_info["permissions"])
    permissions["status"] = claim_info["status"]
    permissions["delegatedScopes"] = (
        "present" if claim_info["claimType"] in {"scp", "scp+roles"}
        else "malformed" if claim_info["claimType"] == "malformed"
        else "not-present"
    )
    permissions["delegatedScopeDiagnostics"] = graph_claims["delegatedScopes"]
    permissions["applicationRoles"] = (
        "present" if claim_info["claimType"] in {"roles", "scp+roles"}
        else "malformed" if claim_info["claimType"] == "malformed"
        else "not-present"
    )
    return {
        "tenantMatch": graph_claims["tenantMatch"],
        "graphAudience": graph_claims["graphAudience"],
        "permissions": permissions,
        "delegatedScopeDiagnostics": graph_claims["delegatedScopes"],
        "managementPermissionGrant": {
            "status": claim_info["status"],
            "grantType": claim_info["grantType"],
            "claimType": claim_info["claimType"],
        },
    }


def preflight_deployment(
    solution: str | Path,
    *,
    auth_method: str | None = None,
    state_dir: str | Path | None = None,
    max_detections: int = DEFAULT_READ_BUDGET,
    request_timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run local payload checks and bounded, read-only checks for exact rules.

    Authentication never prompts or falls back to another credential method.
    The function does not write reports, create/update rules, or change rule
    status. Caller must explicitly select an existing credential method.
    """
    if not 1 <= max_detections <= DEFAULT_READ_BUDGET:
        raise ValueError(f"max_detections must be between 1 and {DEFAULT_READ_BUDGET}")
    if not 1 <= request_timeout_seconds <= 60:
        raise ValueError("request_timeout_seconds must be between 1 and 60")

    root = Path(solution).expanduser().resolve()
    target = require_locked_target(root, materialize_missing=False)
    state_root = _state_dir(state_dir)
    client_id = resolve_graph_client_id(state_root, "customDetection")
    azure_config_dir = configured_azure_cli_profile(state_root)
    with azure_cli_profile(azure_config_dir):
        dcr_permission_preflight = preflight_dcr_permissions(
            root,
            target,
            auth_method=auth_method,
        )
    output = root / "XDR Detections"
    files = xdr_detection_files(output)
    from .packaging_selection import current_applied_package_selection

    applied_selection = current_applied_package_selection(root)
    qualification_scope = None
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
        files = [
            files_by_path[path]
            for path in sorted(selected_paths)
        ]
        qualification_scope = {
            "kind": "applied-package-selection",
            "planSha256": applied_selection["plan"].get("planSha256"),
            "outcome": (applied_selection["plan"].get("summary") or {}).get("outcome"),
            "selectedDetectionPaths": sorted(selected_paths),
            "coverage": applied_selection["plan"].get("summary"),
        }
    report: dict[str, Any] = {
        "status": "unknown",
        "provider": "microsoft-graph-beta",
        "target": {
            "tenantId": target["tenantId"],
            "locked": True,
        },
        "authentication": {
            "method": auth_method,
            "clientId": client_id if auth_method in {"device-code", "browser"} else None,
            "azureConfigDir": azure_config_dir if auth_method == "azure-cli" else None,
            "status": "not-attempted",
            "requestedScope": None,
            "tenantMatch": "unknown",
            "graphAudience": "unknown",
            "tokenPermissionClaims": {"status": "unknown"},
            "claimInterpretation": (
                "Decoded access-token claims are diagnostic only; they do not "
                "prove tenant consent, effective role grants, or write authorization."
            ),
        },
        "requiredManagementPermission": "CustomDetection.ReadWrite.All",
        "managementPermissionGrant": {
            "status": "unknown",
            "grantType": "unknown",
            "claimType": "unknown",
            "permission": "CustomDetection.ReadWrite.All",
            "credentialRequestScope": None,
            "reason": "No access-token permission claim has been inspected.",
        },
        "deploymentReadiness": "unknown",
        "permissions": {
            "readAccess": "unknown",
            "writeScopeInToken": "unknown",
            "requiredDelegatedScopes": {
                "read": "CustomDetection.Read.All",
                "write": "CustomDetection.ReadWrite.All",
            },
            "consent": "unknown",
            "writeRoleGuidance": (
                "Review Defender XDR Unified RBAC Detection tuning > Manage "
                "or an applicable supported Entra security role for the target "
                "workload. This preflight does not inspect effective role grants."
            ),
            "effectiveRole": {
                "status": "unknown",
                "reason": (
                    "Effective Defender XDR Unified RBAC and Entra role grants "
                    "cannot be determined from this Graph permission preflight."
                ),
            },
            "writeAuthorization": "not-tested",
            "documentation": {
                "graphCreate": (
                    "https://learn.microsoft.com/graph/api/"
                    "security-detectionrule-post-detectionrules?view=graph-rest-beta"
                ),
                "graphGet": (
                    "https://learn.microsoft.com/graph/api/"
                    "security-detectionrule-get?view=graph-rest-beta"
                ),
                "defenderCustomDetectionRoles": (
                    "https://learn.microsoft.com/defender-xdr/custom-detection-rules"
                ),
            },
        },
        "payloadReadiness": [],
        "qualificationScope": qualification_scope,
        "readChecks": [],
        "dcrPermissionPreflight": dcr_permission_preflight,
        "deploymentPlanning": build_deployment_plan(
            root,
            target=target,
            dcr_preflight=dcr_permission_preflight,
        ),
        "readBudget": {
            "limit": max_detections,
            "used": 0,
            "requestTimeoutSeconds": request_timeout_seconds,
        },
    }
    if not files:
        report["status"] = "blocked"
        report["deploymentReadiness"] = "blocked"
        report["payloadReadiness"].append(
            {"status": "blocked", "message": f"no generated detections found under {output}"}
        )
        return report

    valid_payloads: list[tuple[str, dict[str, Any]]] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
            payload, projection = graph_detection_payload_with_projection(document)
            valid_payloads.append((relative, payload))
            report["payloadReadiness"].append(
                {
                    "file": relative,
                    "id": payload["id"],
                    "status": "ready",
                    "graphTacticProjection": projection,
                }
            )
        except (OSError, ValueError, yaml.YAMLError) as exc:
            report["payloadReadiness"].append(
                {
                    "file": relative,
                    "id": None,
                    "status": "blocked",
                    "message": str(exc),
                }
            )

    if any(item["status"] == "blocked" for item in report["payloadReadiness"]):
        report["status"] = "blocked"
        report["deploymentReadiness"] = "blocked"
        report["authentication"]["status"] = "not-attempted"
        return report

    if auth_method is None:
        report["authentication"]["status"] = "action-required"
        report["authentication"]["action"] = (
            "Choose an existing cached credential method explicitly "
            "(azure-cli, device-code, or browser); preflight never starts login."
        )
        report["status"] = (
            "blocked"
            if any(item["status"] == "blocked" for item in report["payloadReadiness"])
            else "action-required"
        )
        report["deploymentReadiness"] = "action-required"
        return report

    if auth_method == "azure-cli" and client_id != GRAPH_CLIENT_ID:
        report["authentication"]["status"] = "action-required"
        report["authentication"]["action"] = (
            "The configured custom Graph client is not used by Azure CLI "
            "authentication. Run setup-deployment with device-code or browser."
        )
        report["status"] = "action-required"
        report["deploymentReadiness"] = "action-required"
        return report

    if len(valid_payloads) > max_detections:
        report["authentication"]["status"] = "not-attempted"
        report["readChecks"].append(
            {
                "status": "unknown",
                "reason": "authored detections exceed the bounded exact-rule read budget",
                "detectionCount": len(valid_payloads),
            }
        )
        report["status"] = "unknown"
        report["deploymentReadiness"] = "unknown"
        return report

    try:
        credential = _get_cached_credential(
            auth_method=auth_method,
            state_dir=state_dir,
            tenant_id=target["tenantId"],
        )
        if credential is None:
            report["authentication"]["status"] = "action-required"
            report["authentication"]["action"] = (
                "No stored Custom Detection authentication record exists. Run the "
                "separate setup-deployment command explicitly, then retry."
            )
            report["status"] = "action-required"
            report["deploymentReadiness"] = "action-required"
            return report
        write_request_scope: str | None = None
        read_request_scope: str | None = None
        try:
            write_request_scope = credential_token_scope(auth_method, WRITE_SCOPE)
            with azure_cli_profile(
                azure_config_dir if auth_method == "azure-cli" else None
            ):
                access_token = credential.get_token(write_request_scope).token
            token_scope = (
                "resource-default" if auth_method == "azure-cli" else "write"
            )
        except Exception as write_error:
            report["authentication"]["writeScopeAcquisition"] = {
                "status": "unavailable",
                "errorType": type(write_error).__name__,
                "requestedScope": write_request_scope,
            }
            if auth_method == "azure-cli":
                report["authentication"].update(
                    {
                        "status": "action-required",
                        "requestedScope": write_request_scope,
                        "scopeRequestKind": "graph-resource-default",
                        "permissionUnderReview": "CustomDetection.ReadWrite.All",
                        "readScopeAcquisition": {
                            "status": "not-attempted",
                            "reason": (
                                "AzureCliCredential acquires Graph tokens by resource; "
                                "retrying with a different Custom Detection permission "
                                "would request the same Graph resource."
                            ),
                        },
                    }
                )
                report["status"] = "action-required"
                report["deploymentReadiness"] = "action-required"
                report["authentication"]["action"] = (
                    "The cached Azure CLI credential could not acquire a Microsoft "
                    "Graph resource token. Review the Azure CLI sign-in and its "
                    "previously consented Graph scopes, then retry explicitly; "
                    "preflight will not start login or request consent."
                )
                return report
            try:
                read_request_scope = credential_token_scope(auth_method, READ_SCOPE)
                with azure_cli_profile(
                    azure_config_dir if auth_method == "azure-cli" else None
                ):
                    access_token = credential.get_token(read_request_scope).token
                token_scope = "read"
            except Exception as read_error:
                report["authentication"]["status"] = "action-required"
                report["authentication"]["readScopeAcquisition"] = {
                    "status": "unavailable",
                    "errorType": type(read_error).__name__,
                    "requestedScope": read_request_scope,
                }
                report["status"] = "action-required"
                report["deploymentReadiness"] = "action-required"
                report["authentication"]["action"] = (
                    "The cached credential could not acquire either Custom Detection "
                    "permission scope; review the existing consent and credential "
                    "state, then retry explicitly. Preflight will not start login."
                )
                return report
    except ValueError:
        raise
    except Exception as exc:
        report["authentication"]["status"] = "blocked"
        report["authentication"]["errorType"] = type(exc).__name__
        report["status"] = "blocked"
        report["deploymentReadiness"] = "blocked"
        return report

    claims = _token_claims(access_token)
    required_scope = READ_SCOPE if token_scope == "read" else WRITE_SCOPE
    token_info = _token_diagnostics(
        claims,
        target["tenantId"],
        required_scope=required_scope,
    )
    auth_report = report["authentication"]
    auth_report.update(
        {
            "status": "acquired",
            "requestedScope": (
                write_request_scope if token_scope in {"write", "resource-default"}
                else read_request_scope
            ),
            "scopeRequestKind": (
                "graph-resource-default"
                if token_scope == "resource-default"
                else "explicit-permission"
            ),
            "permissionUnderReview": (
                "CustomDetection.Read.All"
                if token_scope == "read"
                else "CustomDetection.ReadWrite.All"
            ),
            "tenantMatch": token_info["tenantMatch"],
            "graphAudience": token_info["graphAudience"],
            "tokenPermissionClaims": token_info["permissions"],
            "delegatedScopeDiagnostics": token_info["delegatedScopeDiagnostics"],
            "writeScopeAcquisition": {
                "status": (
                    "resource-token-acquired"
                    if token_scope == "resource-default"
                    else "acquired"
                    if token_scope == "write"
                    else "unavailable"
                ),
                "requestedScope": write_request_scope,
            },
            "readScopeAcquisition": {
                "status": (
                    "acquired"
                    if token_scope == "read"
                    else "not-attempted"
                    if token_scope == "resource-default"
                    else "not-requested"
                ),
                "requestedScope": (
                    read_request_scope if token_scope == "read" else None
                ),
            },
        }
    )
    grant = token_info["managementPermissionGrant"]
    report["managementPermissionGrant"].update(
        {
            **grant,
            "credentialRequestScope": auth_report["requestedScope"],
            "reason": (
                "CustomDetection.ReadWrite.All is present in the delegated scp "
                "claim; token claims do not prove tenant "
                "consent, effective user role, Defender XDR RBAC, or write authorization."
                if grant["status"] == "ready"
                else "The token does not contain the required delegated "
                "CustomDetection.ReadWrite.All scope."
                if grant["status"] == "missing"
                else "The token permission claims are missing or malformed; "
                "the management permission grant cannot be determined."
            ),
        }
    )
    report["permissions"]["writeScopeInToken"] = (
        token_info["permissions"].get("customdetection.readwrite.all", "unknown")
        if isinstance(token_info["permissions"], dict)
        else "unknown"
    )
    if (
        token_info["tenantMatch"] is not True
        or token_info["graphAudience"] is not True
        or token_info["delegatedScopeDiagnostics"]["status"] != "satisfied"
    ):
        auth_report["status"] = "blocked"
        auth_report["reason"] = (
            "Cached access token tenant, Graph audience, or required delegated "
            "scopes could not be confirmed against the locked Qualification target."
        )
        report["status"] = "blocked"
        report["deploymentReadiness"] = "blocked"
        return report

    for relative, payload in valid_payloads:
        rule_id = urllib.parse.quote(str(payload["id"]), safe="")
        url = f"{GRAPH_DETECTION_RULES_ENDPOINT}/{rule_id}"
        status_code, response = _graph_get(
            url,
            access_token,
            timeout_seconds=request_timeout_seconds,
        )
        report["readBudget"]["used"] += 1
        error = response.get("error") if isinstance(response, dict) else None
        graph_error = error.get("code") if isinstance(error, dict) else None
        if status_code == 404:
            result = {
                "file": relative,
                "id": payload["id"],
                "status": "not-found",
                "httpStatus": status_code,
                "exists": False,
                "scopeUsed": token_scope,
            }
        elif status_code == 200:
            response_id = response.get("id") if isinstance(response, dict) else None
            if isinstance(response_id, str) and response_id.casefold() == str(
                payload["id"]
            ).casefold():
                result = {
                    "file": relative,
                    "id": payload["id"],
                    "status": "confirmed",
                    "httpStatus": status_code,
                    "exists": True,
                    "scopeUsed": token_scope,
                }
            else:
                result = {
                    "file": relative,
                    "id": payload["id"],
                    "status": "unknown",
                    "httpStatus": status_code,
                    "graphErrorCode": (
                        "UnexpectedDetectionId"
                        if response_id
                        else "DetectionIdMissingFromResponse"
                    ),
                    "scopeUsed": token_scope,
                }
        elif status_code in {401, 403}:
            result = {
                "file": relative,
                "id": payload["id"],
                "status": "denied",
                "httpStatus": status_code,
                "graphErrorCode": graph_error,
                "scopeUsed": token_scope,
                "permissionOrRole": "not-determined",
            }
        else:
            result = {
                "file": relative,
                "id": payload["id"],
                "status": "unknown",
                "httpStatus": status_code,
                "graphErrorCode": graph_error,
                "scopeUsed": token_scope,
            }
        report["readChecks"].append(result)
    read_states = {item["status"] for item in report["readChecks"]}
    if not read_states or read_states == {"confirmed"}:
        report["permissions"]["readAccess"] = "confirmed"
    elif "denied" in read_states:
        report["permissions"]["readAccess"] = "denied"
    else:
        report["permissions"]["readAccess"] = "unknown"
    payloads_ready = all(item["status"] == "ready" for item in report["payloadReadiness"])
    if not payloads_ready or "denied" in read_states:
        report["status"] = "blocked"
        report["deploymentReadiness"] = "blocked"
    elif grant["status"] != "ready":
        report["status"] = "action-required"
        report["deploymentReadiness"] = "action-required"
    elif read_states == {"confirmed"} and token_scope in {"write", "resource-default"}:
        report["status"] = "readiness-unconfirmed"
        report["deploymentReadiness"] = "readiness-unconfirmed"
    else:
        report["status"] = "unknown"
        report["deploymentReadiness"] = "unknown"
    report["readinessLimit"] = (
        "Read checks are read-only. Graph write authorization and effective "
        "Defender XDR Unified RBAC cannot be confirmed without an approved write."
    )
    return report
