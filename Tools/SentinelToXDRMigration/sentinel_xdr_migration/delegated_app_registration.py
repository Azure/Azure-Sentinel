from __future__ import annotations

import hashlib
import json
import urllib.parse
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .artifacts import (
    artifact_path,
    existing_artifact_path,
    using_run,
    write_json_artifact,
)
from .deployment import _graph_request
from .graph_auth import (
    delegated_graph_claim_diagnostics,
    delegated_scope_diagnostics,
    validate_delegated_graph_claims,
)
from .graph_client_config import (
    configure_graph_client,
    ensure_private_state_root,
    graph_auth_record_path,
    graph_token_cache_name,
    read_delegated_app_registration,
    read_private_auth_config,
    resolve_graph_client_id,
    restrict_private_permissions,
    verify_graph_auth_binding,
    write_delegated_app_registration,
    write_graph_auth_metadata,
)
from .onboarding import _load_auth_record, _state_dir
from .target_context import require_locked_target

GRAPH_RESOURCE_APP_ID = "00000003-0000-0000-c000-000000000000"
CUSTOM_DETECTION_SCOPE_ID = "c34088fb-0649-4714-af0b-bcbfec155897"
CUSTOM_DETECTION_SCOPE = "CustomDetection.ReadWrite.All"
THREAT_HUNTING_SCOPE_ID = "b152eca8-ea73-4a48-8c98-1a6742673d99"
THREAT_HUNTING_SCOPE = "ThreatHunting.Read.All"
APP_DISPLAY_NAME = "Sentinel-XDR-CustomDetection"
APP_REDIRECT_URI = "http://localhost"
APPLICATIONS_ENDPOINT = "https://graph.microsoft.com/v1.0/applications"
READBACK_AUTH_RECORD_NAME = "app-readback-auth-record.json"
READBACK_TOKEN_CACHE_NAME = "sentinel_xdr_migration_app_readback"
READBACK_SCOPES = (
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Application.Read.All",
)
OWNED_APPLICATIONS_ENDPOINT = (
    "https://graph.microsoft.com/v1.0/me/ownedObjects/"
    "microsoft.graph.application"
)
BOOTSTRAP_SCOPE = "https://graph.microsoft.com/AppRegistration.Create"
OWNED_APP_READ_SCOPE = "https://graph.microsoft.com/User.Read"
BOOTSTRAP_SCOPES = (BOOTSTRAP_SCOPE, OWNED_APP_READ_SCOPE)
BOOTSTRAP_AUTH_RECORD_NAME = "app-registration-auth-record.json"
BOOTSTRAP_TOKEN_CACHE_NAME = "sentinel_xdr_migration_app_registration"

TokenProvider = Callable[[Path, str], str]
GraphRequest = Callable[..., tuple[int, dict[str, Any]]]


def setup_app_registration_authentication(
    *,
    tenant_id: str,
    auth_method: str = "device-code",
    bootstrap_client_id: str | None = None,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    if auth_method not in {"device-code", "browser"}:
        raise ValueError("app registration bootstrap auth supports device-code or browser only")
    try:
        from azure.identity import (
            DeviceCodeCredential,
            InteractiveBrowserCredential,
            TokenCachePersistenceOptions,
        )
    except ImportError as exc:
        raise RuntimeError("azure-identity is required for app registration bootstrap authentication") from exc

    state_root = _state_dir(state_dir)
    ensure_private_state_root(state_root)
    selected_client_id = resolve_graph_client_id(
        state_root, "appRegistration", bootstrap_client_id
    )
    if bootstrap_client_id:
        configure_graph_client(
            state_root, "appRegistration", selected_client_id
        )
    credential_type = (
        InteractiveBrowserCredential
        if auth_method == "browser"
        else DeviceCodeCredential
    )
    kwargs: dict[str, Any] = {
        "client_id": selected_client_id,
        "tenant_id": tenant_id,
        "cache_persistence_options": TokenCachePersistenceOptions(
            name=graph_token_cache_name(
                "appRegistration", selected_client_id, BOOTSTRAP_TOKEN_CACHE_NAME
            )
        ),
    }
    if auth_method == "device-code":
        import sys

        kwargs["prompt_callback"] = lambda uri, code, _expires: print(
            f"Open {uri} and enter code {code}", file=sys.stderr, flush=True
        )
    credential = credential_type(**kwargs)
    record = credential.authenticate(scopes=list(BOOTSTRAP_SCOPES))
    access_token = credential.get_token(*BOOTSTRAP_SCOPES).token
    from .graph_readiness import _token_claims

    scope_diagnostics = validate_delegated_graph_claims(
        _token_claims(access_token),
        tenant_id=getattr(record, "tenant_id", None) or tenant_id,
        required_scopes=BOOTSTRAP_SCOPES,
        purpose="app-registration bootstrap",
    )
    record_path = graph_auth_record_path(
        state_root,
        "appRegistration",
        selected_client_id,
        BOOTSTRAP_AUTH_RECORD_NAME,
    )
    record_path.write_text(record.serialize(), encoding="utf-8")
    restrict_private_permissions(record_path, 0o600)
    write_graph_auth_metadata(
        record_path,
        purpose="appRegistration",
        client_id=selected_client_id,
        tenant_id=getattr(record, "tenant_id", None) or tenant_id,
    )
    return {
        "status": "completed",
        "tenantId": getattr(record, "tenant_id", None) or tenant_id,
        "username": getattr(record, "username", None),
        "scopes": list(BOOTSTRAP_SCOPES),
        "clientId": selected_client_id,
        "authMethod": auth_method,
        "appRegistrationPerformed": False,
        "adminConsentRequested": False,
        "scopeDiagnostics": scope_diagnostics["delegatedScopes"],
    }


def _bootstrap_token(state_root: Path, tenant_id: str) -> str:
    from azure.identity import DeviceCodeCredential, TokenCachePersistenceOptions

    client_id = resolve_graph_client_id(state_root, "appRegistration")

    record_path = graph_auth_record_path(
        state_root,
        "appRegistration",
        client_id,
        BOOTSTRAP_AUTH_RECORD_NAME,
    )
    record = _load_auth_record(record_path)
    if record is None:
        raise RuntimeError(
            "app registration bootstrap authentication is missing; run "
            "`setup-app-registration-auth` explicitly first"
        )
    verify_graph_auth_binding(
        record_path,
        record,
        purpose="appRegistration",
        client_id=client_id,
        tenant_id=tenant_id,
    )
    credential = DeviceCodeCredential(
        client_id=client_id,
        tenant_id=tenant_id,
        authentication_record=record,
        cache_persistence_options=TokenCachePersistenceOptions(
            name=graph_token_cache_name(
                "appRegistration", client_id, BOOTSTRAP_TOKEN_CACHE_NAME
            )
        ),
        disable_automatic_authentication=True,
    )
    token = credential.get_token(*BOOTSTRAP_SCOPES).token
    from .graph_readiness import _token_claims

    validate_delegated_graph_claims(
        _token_claims(token),
        tenant_id=tenant_id,
        required_scopes=BOOTSTRAP_SCOPES,
        purpose="app-registration bootstrap",
    )
    return token


def setup_app_readback_authentication(
    *,
    tenant_id: str,
    readback_client_id: str,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Set up a separate browser-only, read-only app reconciliation credential."""
    if not isinstance(readback_client_id, str) or not readback_client_id.strip():
        raise ValueError("an existing, separately approved readback client ID is required")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("app readback authentication requires an explicit tenant ID")
    state_root = _state_dir(state_dir)
    ensure_private_state_root(state_root)
    selected_client_id = resolve_graph_client_id(
        state_root, "appReadback", readback_client_id
    )
    configure_graph_client(state_root, "appReadback", selected_client_id)
    try:
        from azure.identity import (
            InteractiveBrowserCredential,
            TokenCachePersistenceOptions,
        )
    except ImportError as exc:
        raise RuntimeError(
            "azure-identity is required for app readback browser authentication"
        ) from exc
    credential = InteractiveBrowserCredential(
        client_id=selected_client_id,
        tenant_id=tenant_id,
        cache_persistence_options=TokenCachePersistenceOptions(
            name=graph_token_cache_name(
                "appReadback", selected_client_id, READBACK_TOKEN_CACHE_NAME
            )
        ),
    )
    record = credential.authenticate(scopes=list(READBACK_SCOPES))
    access_token = credential.get_token(*READBACK_SCOPES).token
    from .graph_readiness import _token_claims

    scope_diagnostics = validate_delegated_graph_claims(
        _token_claims(access_token),
        tenant_id=getattr(record, "tenant_id", None) or tenant_id,
        required_scopes=READBACK_SCOPES,
        purpose="app readback",
    )
    record_path = graph_auth_record_path(
        state_root,
        "appReadback",
        selected_client_id,
        READBACK_AUTH_RECORD_NAME,
    )
    record_path.write_text(record.serialize(), encoding="utf-8")
    restrict_private_permissions(record_path, 0o600)
    write_graph_auth_metadata(
        record_path,
        purpose="appReadback",
        client_id=selected_client_id,
        tenant_id=getattr(record, "tenant_id", None) or tenant_id,
    )
    return {
        "status": "completed",
        "purpose": "appReadback",
        "tenantId": getattr(record, "tenant_id", None) or tenant_id,
        "username": getattr(record, "username", None),
        "clientId": selected_client_id,
        "authMethod": "browser",
        "scopes": list(READBACK_SCOPES),
        "graphWritesPermittedByCommand": False,
        "scopeDiagnostics": scope_diagnostics["delegatedScopes"],
    }


def _readback_scope_diagnostic(scope_claim: Any) -> dict[str, Any]:
    scopes = delegated_scope_diagnostics(scope_claim, READBACK_SCOPES)
    status = (
        "required-scopes-present"
        if scopes["status"] == "satisfied"
        else "scope-mismatch"
        if scopes["status"] == "missing-required"
        else "diagnostic-blocked"
    )
    return {
        "status": status,
        "scopeClaimStatus": scopes["claimStatus"],
        "expectedScopeNames": scopes["requiredScopeNames"],
        "actualScopeNames": scopes["actualScopeNames"],
        "missingScopeNames": scopes["missingScopeNames"],
        "extraScopeNames": scopes["extraScopeNames"],
    }


def _acquire_app_readback_token_and_scope_diagnostic(
    state_root: Path,
    tenant_id: str,
) -> tuple[str, dict[str, Any]]:
    from azure.identity import (
        InteractiveBrowserCredential,
        TokenCachePersistenceOptions,
    )

    configured_client = read_private_auth_config(state_root).get(
        "graphClientIds", {}
    ).get("appReadback")
    if not isinstance(configured_client, str):
        raise RuntimeError(
            "a separately approved app readback client ID is not configured; "
            "run `setup-app-readback-auth` explicitly first"
        )
    client_id = resolve_graph_client_id(state_root, "appReadback")
    record_path = graph_auth_record_path(
        state_root,
        "appReadback",
        client_id,
        READBACK_AUTH_RECORD_NAME,
    )
    record = _load_auth_record(record_path)
    if record is None:
        raise RuntimeError(
            "app readback browser authentication is missing; run "
            "`setup-app-readback-auth` explicitly first"
        )
    verify_graph_auth_binding(
        record_path,
        record,
        purpose="appReadback",
        client_id=client_id,
        tenant_id=tenant_id,
    )
    credential = InteractiveBrowserCredential(
        client_id=client_id,
        tenant_id=tenant_id,
        authentication_record=record,
        cache_persistence_options=TokenCachePersistenceOptions(
            name=graph_token_cache_name(
                "appReadback", client_id, READBACK_TOKEN_CACHE_NAME
            )
        ),
        disable_automatic_authentication=True,
    )
    token = credential.get_token(*READBACK_SCOPES).token
    from .graph_readiness import _token_claims

    claims = _token_claims(token)
    if claims is None:
        raise RuntimeError("app readback access token claims could not be inspected")
    token_info = delegated_graph_claim_diagnostics(
        claims,
        tenant_id=tenant_id,
        required_scopes=READBACK_SCOPES,
    )
    if token_info["tenantMatch"] is not True:
        raise RuntimeError("app readback token tenant does not match the approved lab tenant")
    if token_info["graphAudience"] is not True:
        raise RuntimeError("app readback token is not issued for Microsoft Graph")
    return token, _readback_scope_diagnostic(claims.get("scp"))


def _app_readback_token(state_root: Path, tenant_id: str) -> str:
    token, scope_diagnostic = _acquire_app_readback_token_and_scope_diagnostic(
        state_root,
        tenant_id,
    )
    if scope_diagnostic["status"] != "required-scopes-present":
        raise RuntimeError(
            "app readback token must include the separately approved "
            "delegated User.Read and Application.Read.All scopes"
        )
    return token


def _app_display_name(value: str | None) -> str:
    if value is None:
        return APP_DISPLAY_NAME
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 256
    ):
        raise ValueError("app display name must be 1-256 characters without surrounding whitespace")
    return value


def _registration_payload(app_display_name: str | None = None) -> dict[str, Any]:
    return {
        "displayName": _app_display_name(app_display_name),
        "signInAudience": "AzureADMyOrg",
        "publicClient": {"redirectUris": [APP_REDIRECT_URI]},
        "requiredResourceAccess": [
            {
                "resourceAppId": GRAPH_RESOURCE_APP_ID,
                "resourceAccess": [
                    {
                        "id": CUSTOM_DETECTION_SCOPE_ID,
                        "type": "Scope",
                    }
                ],
            }
        ],
    }


def _approved_dual_purpose_resource_access() -> list[dict[str, Any]]:
    return [{
        "resourceAppId": GRAPH_RESOURCE_APP_ID,
        "resourceAccess": [
            {"id": CUSTOM_DETECTION_SCOPE_ID, "type": "Scope"},
            {"id": THREAT_HUNTING_SCOPE_ID, "type": "Scope"},
        ],
    }]


def _legacy_custom_detection_resource_access() -> list[dict[str, Any]]:
    return _registration_payload()["requiredResourceAccess"]


def _manual_permission_update_plan(
    tenant_id: str,
    registration: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "tenantId": tenant_id,
        "applicationId": registration["applicationId"],
        "objectId": registration["objectId"],
        "displayName": registration["displayName"],
        "previouslyApprovedRequiredResourceAccess": (
            _legacy_custom_detection_resource_access()
        ),
        "desiredRequiredResourceAccess": _approved_dual_purpose_resource_access(),
        "desiredDelegatedScopeNames": [
            CUSTOM_DETECTION_SCOPE,
            THREAT_HUNTING_SCOPE,
        ],
        "adminConsentRequested": False,
        "applicationRolesAdded": False,
        "credentialsCreated": False,
        "automatedReplacementSupported": False,
        "automationBlockReason": (
            "Microsoft Graph's documented application update contract does not "
            "specify a server-enforced conditional update for requiredResourceAccess; "
            "a fresh GET or local lock cannot prevent another owner from changing "
            "the permission collection before PATCH"
        ),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["planSha256"] = hashlib.sha256(encoded).hexdigest()
    payload["status"] = "manual-readback-required"
    payload["writeOperations"] = []
    payload["readOperations"] = [
        "list-current-user-owned-application-object-IDs",
        "GET-exact-application-after-manual-update",
    ]
    payload["manualSteps"] = [
        "if-current-settings-equal-the-previously-approved-set-add-only-delegated-ThreatHunting.Read.All",
        "if-settings-already-match-the-desired-set-make-no-change",
        "if-settings-differ-from-both-reviewed-sets-stop-for-manual-review",
        "preserve-delegated-CustomDetection.ReadWrite.All",
        "do-not-add-application-roles-or-credentials-or-grant-consent",
        "run-verify-delegated-app-permission-update-with-this-plan-hash",
    ]
    payload["authorization"] = {
        "manualChangeApprovalRequired": True,
        "expectedPlanSha256": payload["planSha256"],
        "automatedGraphWrites": False,
    }
    return payload


def _plan_sha256(
    tenant_id: str,
    payload: dict[str, Any],
    bootstrap_client_id: str,
) -> str:
    encoded = json.dumps(
        {
            "tenantId": tenant_id.casefold(),
            "payload": payload,
            "bootstrapScopes": list(BOOTSTRAP_SCOPES),
            "bootstrapClientId": bootstrap_client_id,
            "adminConsentRequested": False,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def plan_delegated_app_registration(
    solution: str | Path,
    *,
    state_dir: str | Path | None = None,
    app_display_name: str | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    target = require_locked_target(root, materialize_missing=False)
    state_root = _state_dir(state_dir)
    persisted = read_delegated_app_registration(state_root)
    selected_name = _app_display_name(app_display_name)
    payload = _registration_payload(selected_name)
    bootstrap_client_id = resolve_graph_client_id(
        state_root, "appRegistration"
    )
    plan_hash = _plan_sha256(
        target["tenantId"], payload, bootstrap_client_id
    )
    registration_status = persisted.get("status") if persisted else None
    same_tenant = (
        persisted
        and str(persisted.get("tenantId", "")).casefold()
        == target["tenantId"].casefold()
    )
    if same_tenant and persisted.get("displayName") != selected_name:
        status = "reconciliation-required"
    elif (
        same_tenant
        and registration_status == "configured"
        and persisted.get("displayName") == selected_name
    ):
        status = "already-configured"
    elif same_tenant and persisted.get("displayName") == selected_name:
        status = "reconciliation-required"
    else:
        status = "approval-required"
    return {
        "status": status,
        "provider": "microsoft-graph-v1.0",
        "tenantId": target["tenantId"],
        "targetLocked": True,
        "appDisplayName": selected_name,
        "planSha256": plan_hash,
        "app": payload,
        "bootstrap": {
            "delegatedScopes": list(BOOTSTRAP_SCOPES),
            "clientId": bootstrap_client_id,
            "adminConsentRequested": False,
            "requiredPermissionDeclaration": {
                "resourceAppId": GRAPH_RESOURCE_APP_ID,
                "scopeId": CUSTOM_DETECTION_SCOPE_ID,
                "scope": CUSTOM_DETECTION_SCOPE,
                "type": "Scope",
            },
            "declarationIsNotConsent": True,
        },
        "writeOperations": ["create-application"],
        "readOperations": ["list-current-user-owned-applications-before-and-after-create"],
        "maximumApplicationCreates": 1,
        "ownedAppListingPageLimit": 10,
        "tenantWideDisplayNameUniqueness": (
            "not-verified; no broad directory read permission is requested"
        ),
        "authorization": {
            "exactScopeApprovalRequired": True,
            "expectedPlanSha256": plan_hash,
            "writeApprovalArgument": "--approve-exact-app-registration",
        },
        "recordedRegistration": {
            "applicationId": persisted.get("applicationId"),
            "tenantId": persisted.get("tenantId"),
            "displayName": persisted.get("displayName"),
            "status": registration_status,
        } if persisted else None,
    }


def _list_owned_apps(
    token: str,
    *,
    graph_request: GraphRequest = _graph_request,
) -> list[dict[str, Any]]:
    url = OWNED_APPLICATIONS_ENDPOINT + "?" + urllib.parse.urlencode(
        {"$select": "id,appId,displayName,signInAudience,publicClient,requiredResourceAccess"}
    )
    result: list[dict[str, Any]] = []
    pages = 0
    while url:
        pages += 1
        if pages > 10:
            raise RuntimeError("owned application inventory exceeded the 10-page safety bound")
        status, body = graph_request("GET", url, token)
        if status != 200:
            error = (body.get("error") or {}).get("message") if isinstance(body, dict) else None
            raise RuntimeError(
                "cannot safely verify ownership and existing app count with the "
                f"bootstrap permission (HTTP {status}): {error or 'Graph request failed'}"
            )
        values = body.get("value") if isinstance(body, dict) else None
        if not isinstance(values, list) or any(not isinstance(item, dict) for item in values):
            raise RuntimeError("owned application inventory response is malformed")
        result.extend(values)
        next_link = body.get("@odata.nextLink")
        if next_link is not None and not isinstance(next_link, str):
            raise RuntimeError("owned application inventory continuation link is invalid")
        if next_link:
            parsed = urllib.parse.urlsplit(next_link)
            if (
                parsed.scheme != "https"
                or parsed.hostname != "graph.microsoft.com"
                or parsed.username
                or parsed.password
                or not parsed.path.startswith("/v1.0/me/ownedObjects/")
            ):
                raise RuntimeError(
                    "owned application inventory returned an unsafe continuation URL"
                )
        url = next_link or ""
    return result


def _matches_requested_app(
    value: dict[str, Any],
    app_display_name: str = APP_DISPLAY_NAME,
) -> bool:
    public_client = value.get("publicClient")
    if not isinstance(public_client, dict):
        return False
    redirects = public_client.get("redirectUris") or []
    resources = value.get("requiredResourceAccess") or []
    expected = {
        "resourceAppId": GRAPH_RESOURCE_APP_ID,
        "resourceAccess": [
            {"id": CUSTOM_DETECTION_SCOPE_ID, "type": "Scope"}
        ],
    }
    return (
        value.get("displayName") == app_display_name
        and value.get("signInAudience") == "AzureADMyOrg"
        and redirects == [APP_REDIRECT_URI]
        and resources == [expected]
    )


def _require_owned_app_details(owned: list[dict[str, Any]]) -> None:
    required = (
        "id",
        "appId",
        "displayName",
        "signInAudience",
        "publicClient",
        "requiredResourceAccess",
    )
    if any(
        any(field not in app or app[field] is None for field in required)
        for app in owned
    ):
        raise RuntimeError(
            "the bootstrap permission cannot read enough owned-app properties "
            "to verify existing app count and exact settings; no app write was attempted"
        )


def _list_owned_application_ids(
    token: str,
    *,
    graph_request: GraphRequest = _graph_request,
) -> list[str]:
    url = OWNED_APPLICATIONS_ENDPOINT + "?" + urllib.parse.urlencode(
        {"$select": "id", "$top": "100"}
    )
    object_ids: list[str] = []
    pages = 0
    while url:
        pages += 1
        if pages > 10:
            raise RuntimeError("owned application inventory exceeded the 10-page safety bound")
        status, body = graph_request("GET", url, token)
        if status != 200:
            error = (body.get("error") or {}).get("message") if isinstance(body, dict) else None
            raise RuntimeError(
                "cannot verify current-user ownership with the approved readback "
                f"permission (HTTP {status}): {error or 'Graph request failed'}"
            )
        values = body.get("value") if isinstance(body, dict) else None
        if not isinstance(values, list) or any(not isinstance(item, dict) for item in values):
            raise RuntimeError("owned application ID inventory response is malformed")
        for item in values:
            object_id = item.get("id")
            if (
                not isinstance(object_id, str)
                or not object_id
                or (
                    item.get("@odata.type") is not None
                    and item.get("@odata.type") != "#microsoft.graph.application"
                )
            ):
                raise RuntimeError(
                    "owned application response has a missing ID or conflicting explicit object type"
                )
            object_ids.append(object_id)
        if len(object_ids) > 100:
            raise RuntimeError("owned application inventory exceeds the 100-item safety bound")
        next_link = body.get("@odata.nextLink")
        if next_link is not None and not isinstance(next_link, str):
            raise RuntimeError("owned application continuation link is invalid")
        if next_link:
            parsed = urllib.parse.urlsplit(next_link)
            if (
                parsed.scheme != "https"
                or parsed.hostname != "graph.microsoft.com"
                or parsed.username
                or parsed.password
                or not parsed.path.startswith("/v1.0/me/ownedObjects/")
            ):
                raise RuntimeError("owned application inventory returned an unsafe continuation URL")
        url = next_link or ""
    return object_ids


def _readback_application_url(object_id: str) -> str:
    fields = (
        "id",
        "appId",
        "displayName",
        "signInAudience",
        "publicClient",
        "requiredResourceAccess",
        "passwordCredentials",
        "keyCredentials",
    )
    return APPLICATIONS_ENDPOINT + "/" + urllib.parse.quote(object_id, safe="") + "?" + urllib.parse.urlencode(
        {"$select": ",".join(fields)}
    )


def _validate_readback_application(
    application: dict[str, Any],
    registration: dict[str, Any],
) -> list[str]:
    issues = _validate_readback_application_identity(application, registration)
    if issues:
        return issues
    resource_access = application["requiredResourceAccess"]
    if resource_access == _approved_dual_purpose_resource_access():
        return []
    if resource_access == _legacy_custom_detection_resource_access():
        return [
            "application permission declaration is update-needed; expected the exact "
            "delegated CustomDetection.ReadWrite.All and ThreatHunting.Read.All set"
        ]
    return [
        "application declares a missing or additional permission; expected the exact "
        "delegated CustomDetection.ReadWrite.All and ThreatHunting.Read.All set"
    ]


def _validate_readback_application_identity(
    application: dict[str, Any],
    registration: dict[str, Any],
) -> list[str]:
    required = (
        "id",
        "appId",
        "displayName",
        "signInAudience",
        "publicClient",
        "requiredResourceAccess",
        "passwordCredentials",
        "keyCredentials",
    )
    missing = [
        key for key in required
        if key not in application or application[key] is None
    ]
    if missing:
        return [f"Graph did not return required settings: {', '.join(missing)}"]
    if (
        not isinstance(application.get("id"), str)
        or application["id"].casefold() != registration["objectId"].casefold()
    ):
        return ["Graph returned a different application object ID"]
    if (
        not isinstance(application.get("appId"), str)
        or application["appId"].casefold() != registration["applicationId"].casefold()
    ):
        return ["Graph returned a different application/client ID"]
    if application.get("displayName") != registration["displayName"]:
        return ["application display name does not match the exact approved name"]
    if application.get("signInAudience") != "AzureADMyOrg":
        return ["application is not restricted to the approved single-tenant audience"]
    public_client = application.get("publicClient")
    if (
        not isinstance(public_client, dict)
        or public_client.get("redirectUris") != [APP_REDIRECT_URI]
    ):
        return ["application localhost public-client redirect settings do not match"]
    if not isinstance(application.get("requiredResourceAccess"), list):
        return ["application permission declaration is unavailable"]
    if not isinstance(application.get("passwordCredentials"), list):
        return ["password-credential inventory is not a list"]
    if application["passwordCredentials"]:
        return ["application has password credentials; refusing to configure it"]
    if not isinstance(application.get("keyCredentials"), list):
        return ["key-credential inventory is not a list"]
    if application["keyCredentials"]:
        return ["application has key credentials; refusing to configure it"]
    return []


def _safe_readback_error(_solution: Path, _error: Exception) -> str:
    safe_message = (
        "app readback browser authentication is missing; run "
        "`setup-app-readback-auth` explicitly first"
    )
    try:
        message = str(_error).strip()
    except Exception:
        return "details suppressed to prevent disclosure of credentials or token claims"
    if message.startswith(safe_message):
        return safe_message
    return "details suppressed to prevent disclosure of credentials or token claims"


def _require_readback_registration(
    state_root: Path,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    registration = read_delegated_app_registration(state_root)
    if not isinstance(registration, dict):
        raise RuntimeError("private app-registration record is missing")
    if str(registration.get("tenantId") or "").casefold() != tenant_id.casefold():
        raise RuntimeError(
            "private app-registration record is not bound to the locked tenant"
        )
    for key in ("applicationId", "objectId"):
        value = registration.get(key)
        try:
            uuid.UUID(value) if isinstance(value, str) else None
        except (ValueError, AttributeError):
            value = None
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(
                f"private app-registration record has no valid {key}; "
                "complete supported app discovery or registration first"
            )
    display_name = registration.get("displayName")
    if not isinstance(display_name, str) or not display_name.strip():
        raise RuntimeError(
            "private app-registration record has no verified display name"
        )
    registration["applicationId"] = str(uuid.UUID(registration["applicationId"]))
    registration["objectId"] = str(uuid.UUID(registration["objectId"]))
    if registration.get("status") not in {
        "created-needs-ownership-verification",
        "create-outcome-unknown",
        "reconciliation-required",
        "configured",
    }:
        raise RuntimeError(
            "readback and permission update require an existing recorded app "
            "registration; they do not replace the registration workflow"
        )
    return registration


def diagnose_app_readback_scopes(
    solution: str | Path,
    *,
    run_id: str,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Report approved cached-token scope names without calling Microsoft Graph."""
    root = Path(solution).expanduser().resolve()
    with using_run(root, run_id):
        return _diagnose_selected_app_readback_scopes(
            root,
            run_id=run_id,
            state_dir=state_dir,
        )


def _diagnose_selected_app_readback_scopes(
    root: Path,
    *,
    run_id: str,
    state_dir: str | Path | None,
) -> dict[str, Any]:
    state_path = existing_artifact_path(root, "workflow-state.json")
    try:
        state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "the exact selected qualification workflow state is unavailable"
        ) from exc
    context = state.get("context") if isinstance(state, dict) else None
    if (
        not isinstance(state, dict)
        or state.get("runId") != run_id
        or not isinstance(context, dict)
        or context.get("workflowProfile") != "qualification"
        or context.get("targetContextLocked") is not True
    ):
        raise ValueError(
            "scope diagnostic requires the exact pinned Qualification run and tenant"
        )
    target = require_locked_target(root, materialize_missing=False)
    tenant_id = str(target.get("tenantId") or "")

    state_root = _state_dir(state_dir)
    _require_readback_registration(state_root, tenant_id=tenant_id)
    try:
        token, diagnostic = _acquire_app_readback_token_and_scope_diagnostic(
            state_root,
            tenant_id,
        )
        del token
    except Exception as exc:
        diagnostic = _readback_scope_diagnostic(None)
        diagnostic.update(
            status="diagnostic-blocked",
            scopeClaimStatus="not-available",
        )
        diagnostic["reason"] = (
            "cached readback token unavailable or invalid: "
            + _safe_readback_error(root, exc)
        )
    else:
        diagnostic["reason"] = (
            "scope names were checked from the approved cached readback credential; "
            "no Microsoft Graph resource request was made"
        )
    diagnostic["graphResourceRequests"] = 0
    diagnostic["interactivePromptUsed"] = False
    diagnostic["privateConfigurationChanged"] = False
    return diagnostic


def verify_delegated_app_readback(
    solution: str | Path,
    *,
    state_dir: str | Path | None = None,
    token_provider: TokenProvider | None = None,
    graph_request: GraphRequest = _graph_request,
) -> dict[str, Any]:
    """Verify the approved app using owned-object enumeration and exact GET only."""
    root = Path(solution).expanduser().resolve()
    target = require_locked_target(root, materialize_missing=False)
    tenant_id = str(target.get("tenantId") or "")
    state_root = _state_dir(state_dir)
    registration = _require_readback_registration(
        state_root,
        tenant_id=tenant_id,
    )
    application_id = registration["applicationId"]
    object_id = registration["objectId"]
    display_name = registration["displayName"]
    prior_status = registration.get("status")
    if token_provider is None:
        token_provider = _app_readback_token
    try:
        token = token_provider(state_root, tenant_id)
    except Exception as exc:
        return {
            "status": "verification-blocked",
            "tenantId": tenant_id,
            "applicationId": application_id,
            "objectId": object_id,
            "authentication": "missing-or-invalid",
            "ownership": "not-run",
            "settings": "not-run",
            "reason": "readback authentication unavailable: "
            + _safe_readback_error(root, exc),
            "graphWritesPerformed": False,
            "privateConfigurationCompleted": False,
        }
    try:
        owned_ids = _list_owned_application_ids(token, graph_request=graph_request)
    except Exception as exc:
        return {
            "status": "verification-blocked",
            "tenantId": tenant_id,
            "applicationId": application_id,
            "objectId": object_id,
            "ownership": "unverified",
            "settings": "not-read",
            "reason": "owned-object readback failed: "
            + _safe_readback_error(root, exc),
            "graphWritesPerformed": False,
            "privateConfigurationCompleted": False,
        }
    if owned_ids.count(object_id) != 1:
        return {
            "status": "verification-blocked",
            "tenantId": tenant_id,
            "applicationId": application_id,
            "objectId": object_id,
            "ownership": (
                "not-owned-or-not-visible"
                if object_id not in owned_ids
                else "duplicate-owned-object"
            ),
            "settings": "not-read",
            "reason": "the exact approved object ID did not appear exactly once in the current user's owned applications",
            "graphWritesPerformed": False,
            "privateConfigurationCompleted": False,
        }
    try:
        status, application = graph_request(
            "GET",
            _readback_application_url(object_id),
            token,
        )
    except Exception as exc:
        return {
            "status": "verification-blocked",
            "tenantId": tenant_id,
            "applicationId": application_id,
            "objectId": object_id,
            "ownership": "verified",
            "settings": "not-read",
            "reason": "exact application GET failed: "
            + _safe_readback_error(root, exc),
            "graphWritesPerformed": False,
            "privateConfigurationCompleted": False,
        }
    if status != 200 or not isinstance(application, dict):
        return {
            "status": "verification-blocked",
            "tenantId": tenant_id,
            "applicationId": application_id,
            "objectId": object_id,
            "ownership": "verified",
            "settings": "unavailable",
            "httpStatus": status,
            "reason": "exact application settings could not be read",
            "graphWritesPerformed": False,
            "privateConfigurationCompleted": False,
        }
    issues = _validate_readback_application(application, registration)
    if issues:
        return {
            "status": "verification-blocked",
            "tenantId": tenant_id,
            "applicationId": application_id,
            "objectId": object_id,
            "ownership": "verified",
            "settings": "mismatch-or-incomplete",
            "issues": issues,
            "graphWritesPerformed": False,
            "privateConfigurationCompleted": False,
        }

    snapshot = {
        key: application[key]
        for key in (
            "id",
            "appId",
            "displayName",
            "signInAudience",
            "publicClient",
            "requiredResourceAccess",
            "passwordCredentials",
            "keyCredentials",
        )
    }
    updated_registration = dict(registration)
    updated_registration.setdefault("creationStatus", prior_status)
    updated_registration["applicationId"] = application_id
    updated_registration["objectId"] = object_id
    updated_registration["tenantId"] = tenant_id
    updated_registration["status"] = "configured"
    updated_registration["readbackVerification"] = {
        "status": "passed",
        "verifiedAt": datetime.now(timezone.utc).isoformat(),
        "tenantId": tenant_id,
        "clientId": application_id,
        "objectId": object_id,
        "ownership": "current-user-owned-object-confirmed",
        "settingsSha256": hashlib.sha256(
            json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "verifiedSettings": [
            "exact-object-and-client-IDs",
            "exact-display-name",
            "single-tenant-audience",
            "localhost-public-client-redirect",
            "exact-delegated-CustomDetection.ReadWrite.All-and-ThreatHunting.Read.All-declared",
            "no-password-or-key-credentials",
        ],
        "graphMethods": ["GET"],
        "graphWritesPerformed": False,
        "adminConsentVerified": False,
    }
    write_delegated_app_registration(
        state_root,
        updated_registration,
        custom_detection_client_id=application_id,
        advanced_hunting_client_id=application_id,
    )
    return {
        "status": "readback-verified-private-config-completed",
        "tenantId": tenant_id,
        "applicationId": application_id,
        "objectId": object_id,
        "displayName": display_name,
        "ownership": "current-user-owned-object-confirmed",
        "settings": "exact-approved-settings-confirmed",
        "privateConfigurationCompleted": True,
        "preservedCreationStatus": prior_status,
        "graphWritesPerformed": False,
        "adminConsentVerified": False,
        "deploymentOrWriteAuthorizationVerified": False,
    }


def plan_delegated_app_permission_update(
    solution: str | Path,
    *,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    target = require_locked_target(
        Path(solution).expanduser().resolve(),
        materialize_missing=False,
    )
    tenant_id = str(target.get("tenantId") or "")
    registration = _require_readback_registration(
        _state_dir(state_dir),
        tenant_id=tenant_id,
    )
    return _manual_permission_update_plan(tenant_id, registration)


def verify_delegated_app_permission_update(
    solution: str | Path,
    *,
    expected_plan_sha256: str,
    state_dir: str | Path | None = None,
    token_provider: TokenProvider | None = None,
    graph_request: GraphRequest = _graph_request,
) -> dict[str, Any]:
    """Verify a separately completed manual permission update with GET only."""
    plan = plan_delegated_app_permission_update(solution, state_dir=state_dir)
    if expected_plan_sha256.casefold() != plan["planSha256"]:
        raise ValueError("the delegated app permission update plan has changed")
    result = verify_delegated_app_readback(
        solution,
        state_dir=state_dir,
        token_provider=token_provider,
        graph_request=graph_request,
    )
    issues = result.get("issues", [])
    if result.get("status") == "readback-verified-private-config-completed":
        status = "manual-permission-update-verified"
    elif any("update-needed" in issue for issue in issues):
        status = "manual-update-required"
    else:
        status = "verification-blocked"
    return {
        "status": status,
        "planSha256": plan["planSha256"],
        "applicationId": plan["applicationId"],
        "objectId": plan["objectId"],
        "manualPermissionAdditionRequired": status == "manual-update-required",
        "automatedUpdatePerformed": False,
        "graphWritesPerformed": False,
        "adminConsentRequested": False,
        "readback": result,
    }


def register_delegated_app(
    solution: str | Path,
    *,
    expected_plan_sha256: str,
    approve_exact_app_registration: bool = False,
    state_dir: str | Path | None = None,
    app_display_name: str | None = None,
    token_provider: TokenProvider | None = None,
    graph_request: GraphRequest = _graph_request,
) -> dict[str, Any]:
    """Create at most one approved delegated desktop app; never grants consent."""
    if not approve_exact_app_registration:
        raise PermissionError(
            "app registration requires explicit --approve-exact-app-registration"
        )
    selected_name = _app_display_name(app_display_name)
    plan = plan_delegated_app_registration(
        solution,
        state_dir=state_dir,
        app_display_name=selected_name,
    )
    if expected_plan_sha256.casefold() != plan["planSha256"]:
        raise ValueError("the exact delegated app registration plan has changed")
    if plan["status"] == "already-configured":
        return {"status": "already-configured", "plan": plan}
    if plan["status"] == "reconciliation-required":
        persisted = read_delegated_app_registration(_state_dir(state_dir)) or {}
        application_id = persisted.get("applicationId")
        object_id = persisted.get("objectId")
        pending_tenant = persisted.get("tenantId")
        if not isinstance(application_id, str) or not isinstance(object_id, str):
            raise RuntimeError(
                "a previous app-create attempt has an unknown outcome; inspect "
                "the target tenant before any further write"
            )
        if str(pending_tenant or "").casefold() != plan["tenantId"].casefold():
            raise RuntimeError("pending app registration belongs to a different tenant")

    root = Path(solution).expanduser().resolve()
    state_root = _state_dir(state_dir)
    tenant_id = plan["tenantId"]
    if token_provider is None:
        token_provider = _bootstrap_token
    token = token_provider(state_root, tenant_id)

    owned = _list_owned_apps(token, graph_request=graph_request)
    _require_owned_app_details(owned)
    matching_name = [
        item for item in owned if item.get("displayName") == selected_name
    ]
    if len(matching_name) > 1:
        raise RuntimeError(
            "multiple same-name applications are owned by this user; refusing to create or select one"
        )
    if matching_name:
        existing = matching_name[0]
        if not _matches_requested_app(existing, selected_name):
            raise RuntimeError(
                "an owned application with the requested name has different settings; "
                "refusing to modify or reuse it"
            )
        if plan["status"] == "reconciliation-required" and (
            existing.get("appId") != application_id
            or existing.get("id") != object_id
        ):
            raise RuntimeError(
                "the owned application does not match the pending registration "
                "identifiers; refusing to reconfigure private client state"
            )
        application_id = existing.get("appId")
        object_id = existing.get("id")
        if not isinstance(application_id, str) or not isinstance(object_id, str):
            raise RuntimeError("matching owned application is missing application/object identifiers")
        response = existing
        status = 200
        operation = "reused-exact-owned-app"
    else:
        if plan["status"] == "reconciliation-required":
            raise RuntimeError(
                "a previous app-create attempt is not visible in the current user's "
                "owned applications; refusing to create a duplicate"
            )
        if len(owned) >= 100:
            raise RuntimeError("owned application inventory exceeds the 100-item safety bound")
        try:
            status, response = graph_request(
                "POST",
                APPLICATIONS_ENDPOINT,
                token,
                plan["app"],
            )
        except Exception as exc:
            write_delegated_app_registration(
                state_root,
                {
                    "schemaVersion": 1,
                    "applicationId": None,
                    "objectId": None,
                    "tenantId": tenant_id,
                    "displayName": selected_name,
                    "status": "create-outcome-unknown",
                },
            )
            write_json_artifact(
                root,
                artifact_path(
                    root,
                    "delegated-app-registration.report.json",
                    create_parent=True,
                ),
                {
                    "status": "reconciliation-required",
                    "tenantId": tenant_id,
                    "reason": (
                        "The application create request outcome is unknown "
                        f"({type(exc).__name__}); inspect the tenant before retrying."
                    ),
                    "adminConsent": "not-requested",
                },
            )
            raise RuntimeError(
                "application create outcome is unknown; inspect the target tenant "
                "before retrying to avoid a duplicate"
            ) from exc
        if status != 201:
            error = (response.get("error") or {}).get("message") if isinstance(response, dict) else None
            raise RuntimeError(
                "application registration failed; verify the signed-in user has "
                f"the supported least-privilege bootstrap permission: {error or f'HTTP {status}'}"
            )
        application_id = response.get("appId")
        object_id = response.get("id")
        pending_registration = {
            "schemaVersion": 1,
            "applicationId": application_id,
            "objectId": object_id,
            "tenantId": tenant_id,
            "displayName": selected_name,
            "redirectUri": APP_REDIRECT_URI,
            "delegatedScope": CUSTOM_DETECTION_SCOPE,
            "scopeId": CUSTOM_DETECTION_SCOPE_ID,
            "permissionDeclarationOnly": True,
            "adminConsentGranted": False,
            "status": "created-needs-ownership-verification",
        }
        write_delegated_app_registration(state_root, pending_registration)
        if not isinstance(application_id, str) or not isinstance(object_id, str):
            write_json_artifact(
                root,
                artifact_path(
                    root,
                    "delegated-app-registration.report.json",
                    create_parent=True,
                ),
                {
                    "status": "reconciliation-required",
                    "tenantId": tenant_id,
                    "graphResponseStatus": status,
                    "reason": (
                        "Graph returned a successful create response without both "
                        "application and object IDs. No retry or corrective write was attempted."
                    ),
                    "adminConsent": "not-requested",
                },
            )
            raise RuntimeError(
                "Graph created an application but omitted identifiers; inspect "
                "the tenant before retrying to avoid a duplicate"
            )
        if (
            not _matches_requested_app(response, selected_name)
        ):
            raise RuntimeError(
                "created application response did not match the approved configuration; "
                "no corrective writes were attempted"
            )
        operation = "created"

    if operation == "created":
        try:
            owned_after_create = _list_owned_apps(token, graph_request=graph_request)
        except Exception as exc:
            reason = (
                "Application creation succeeded, but ownership could not be "
                f"verified: {type(exc).__name__}: {exc}"
            )
            write_json_artifact(
                root,
                artifact_path(
                    root,
                    "delegated-app-registration.report.json",
                    create_parent=True,
                ),
                {
                    "status": "reconciliation-required",
                    "operation": operation,
                    "tenantId": tenant_id,
                    "applicationId": application_id,
                    "objectId": object_id,
                    "displayName": selected_name,
                    "reason": reason,
                    "error": reason,
                    "adminConsent": "not-requested",
                },
            )
            return {
                "status": "reconciliation-required",
                "operation": operation,
                "tenantId": tenant_id,
                "applicationId": application_id,
                "objectId": object_id,
                "displayName": selected_name,
                "ownershipVerified": False,
                "reason": reason,
                "error": reason,
            }
        owned_matches = [
            item
            for item in owned_after_create
            if item.get("id") == object_id
            and item.get("@odata.type", "#microsoft.graph.application")
            == "#microsoft.graph.application"
            and _matches_requested_app(item, selected_name)
        ]
        if len(owned_matches) != 1:
            reason = (
                "The created application did not appear exactly once with the "
                "approved display name and settings in the current user's owned applications."
            )
            write_json_artifact(
                root,
                artifact_path(
                    root,
                    "delegated-app-registration.report.json",
                    create_parent=True,
                ),
                {
                    "status": "reconciliation-required",
                    "operation": operation,
                    "tenantId": tenant_id,
                    "applicationId": application_id,
                    "objectId": object_id,
                    "displayName": selected_name,
                    "reason": reason,
                    "error": reason,
                    "adminConsent": "not-requested",
                },
            )
            return {
                "status": "reconciliation-required",
                "operation": operation,
                "tenantId": tenant_id,
                "applicationId": application_id,
                "objectId": object_id,
                "displayName": selected_name,
                "ownershipVerified": False,
                "reason": reason,
                "error": reason,
            }

    registration = {
        "schemaVersion": 1,
        "applicationId": application_id,
        "objectId": object_id,
        "tenantId": tenant_id,
        "displayName": selected_name,
        "redirectUri": APP_REDIRECT_URI,
        "delegatedScope": CUSTOM_DETECTION_SCOPE,
        "scopeId": CUSTOM_DETECTION_SCOPE_ID,
        "permissionDeclarationOnly": True,
        "adminConsentGranted": False,
        "status": "configured",
    }
    write_delegated_app_registration(
        state_root,
        registration,
        custom_detection_client_id=application_id,
    )
    write_json_artifact(
        root,
        artifact_path(
            root,
            "delegated-app-registration.report.json",
            create_parent=True,
        ),
        {
            "status": "configured",
            "operation": operation,
            "tenantId": tenant_id,
            "applicationId": application_id,
            "objectId": object_id,
            "displayName": selected_name,
            "delegatedPermissionDeclaration": CUSTOM_DETECTION_SCOPE,
            "adminConsent": "not-requested",
            "applicationPermissionGrant": "not-requested",
            "armRoles": "not-requested",
            "reportingDoesNotProve": [
                "OAuth consent",
                "effective delegated permission",
                "Defender XDR role assignment",
                "write authorization",
            ],
            "graphResponseStatus": status,
        },
    )
    return {
        "status": "configured",
        "operation": operation,
        "tenantId": tenant_id,
        "applicationId": application_id,
        "objectId": object_id,
        "displayName": selected_name,
        "adminConsent": "not-requested",
    }
