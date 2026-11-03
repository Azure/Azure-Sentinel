from __future__ import annotations

import re
from typing import Any, Iterable

GRAPH_RESOURCE = "https://graph.microsoft.com"
GRAPH_RESOURCE_DEFAULT_SCOPE = f"{GRAPH_RESOURCE}/.default"
GRAPH_AUDIENCE_CLAIM = "00000003-0000-0000-c000-000000000000"
_SCOPE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


def delegated_scope_diagnostics(
    scope_claim: Any,
    required_scopes: Iterable[str],
) -> dict[str, Any]:
    """Compare required Graph scopes to a valid delegated ``scp`` claim."""
    expected_by_key: dict[str, str] = {}
    for scope in required_scopes:
        if not isinstance(scope, str):
            raise ValueError("required delegated scopes must be strings")
        name = scope.rsplit("/", 1)[-1]
        if not _SCOPE_NAME.fullmatch(name):
            raise ValueError("required delegated scope name is invalid")
        expected_by_key[name.casefold()] = name
    if not expected_by_key:
        raise ValueError("at least one required delegated scope must be specified")

    if scope_claim is None:
        claim_status = "missing"
        actual_by_key: dict[str, str] = {}
    elif not isinstance(scope_claim, str) or not scope_claim.strip():
        claim_status = "malformed"
        actual_by_key = {}
    else:
        scope_names = scope_claim.split()
        if any(not _SCOPE_NAME.fullmatch(name) for name in scope_names):
            claim_status = "malformed"
            actual_by_key = {}
        else:
            claim_status = "valid"
            actual_by_key = {
                name.casefold(): expected_by_key.get(name.casefold(), name)
                for name in scope_names
            }

    missing = [
        name for key, name in expected_by_key.items()
        if key not in actual_by_key
    ]
    extra = [
        name for key, name in actual_by_key.items()
        if key not in expected_by_key
    ]
    status = (
        "satisfied"
        if claim_status == "valid" and not missing
        else "missing-required"
        if claim_status == "valid"
        else claim_status
    )
    return {
        "status": status,
        "claimStatus": claim_status,
        "requiredScopeNames": sorted(expected_by_key.values(), key=str.casefold),
        "actualScopeNames": sorted(actual_by_key.values(), key=str.casefold),
        "missingScopeNames": sorted(missing, key=str.casefold),
        "extraScopeNames": sorted(extra, key=str.casefold),
    }


def delegated_graph_claim_diagnostics(
    claims: dict[str, Any] | None,
    *,
    tenant_id: str,
    required_scopes: Iterable[str],
) -> dict[str, Any]:
    """Return safe tenant, audience, and delegated-scope claim diagnostics."""
    if not isinstance(claims, dict):
        return {
            "tenantMatch": "unknown",
            "graphAudience": "unknown",
            "delegatedScopes": delegated_scope_diagnostics(None, required_scopes),
        }
    claim_tenant = claims.get("tid")
    tenant_match = (
        claim_tenant.casefold() == tenant_id.casefold()
        if isinstance(claim_tenant, str)
        else "unknown"
    )
    audience = claims.get("aud")
    graph_audience = (
        audience.casefold() in {
            GRAPH_RESOURCE.casefold(),
            GRAPH_AUDIENCE_CLAIM.casefold(),
        }
        if isinstance(audience, str)
        else "unknown"
    )
    return {
        "tenantMatch": tenant_match,
        "graphAudience": graph_audience,
        "delegatedScopes": delegated_scope_diagnostics(
            claims.get("scp"), required_scopes
        ),
    }


def validate_delegated_graph_claims(
    claims: dict[str, Any] | None,
    *,
    tenant_id: str,
    required_scopes: Iterable[str],
    purpose: str,
) -> dict[str, Any]:
    """Require a tenant-bound Graph audience and all required delegated scopes."""
    diagnostics = delegated_graph_claim_diagnostics(
        claims,
        tenant_id=tenant_id,
        required_scopes=required_scopes,
    )
    if diagnostics["tenantMatch"] is not True:
        raise RuntimeError(f"{purpose} access token tenant does not match the target")
    if diagnostics["graphAudience"] is not True:
        raise RuntimeError(f"{purpose} access token is not issued for Microsoft Graph")
    if diagnostics["delegatedScopes"]["status"] != "satisfied":
        raise RuntimeError(
            f"{purpose} access token is missing valid required delegated scopes"
        )
    return diagnostics


def credential_token_scope(auth_method: str, permission_scope: str) -> str:
    """Map an operation's permission scope to the selected credential contract.

    AzureCliCredential requests Azure CLI resource tokens. Its `/.default`
    scope maps to the Graph resource URI; other credentials keep the exact
    delegated permission scope.
    """
    if auth_method == "azure-cli":
        return GRAPH_RESOURCE_DEFAULT_SCOPE
    return permission_scope
