"""Discover a workspace DCR and optionally ingest a reviewed JSON payload.

This tool is intentionally standalone: it uses Azure CLI authentication and the
Python standard library only. Payload generation and rule validation are separate
steps. A successful HTTP response proves ingestion acceptance, not rule execution.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_DIR = Path.home() / ".sentinel-xdr-migration"
CONFIG_NAME = "config.json"
ARM_RESOURCE = "https://management.azure.com/"
MONITOR_RESOURCE = "https://monitor.azure.com/"
LOG_ANALYTICS_RESOURCE = "https://api.loganalytics.io/"
RESOURCE_GRAPH_URL = (
    "https://management.azure.com/providers/Microsoft.ResourceGraph/resources"
    "?api-version=2021-03-01"
)
DCE_API_VERSION = "2023-03-11"
STREAM_API_VERSION = "2023-01-01"
WORKSPACE_API_VERSION = "2022-10-01"
PERMISSIONS_API_VERSION = "2022-04-01"
DATA_CONNECTORS_API_VERSION = "2023-02-01-preview"
INGESTION_ACTION = "Microsoft.Insights/Telemetry/Write"
DEFENDER_XDR_CONNECTOR_KINDS = frozenset({
    "microsoftthreatprotection",
    "microsoftdefenderxdr",
})


class ToolError(RuntimeError):
    """A user-actionable discovery or ingestion failure."""


def _az_executable() -> str:
    executable = shutil.which("az.cmd" if os.name == "nt" else "az")
    if not executable:
        executable = shutil.which("az")
    if not executable:
        raise ToolError("Azure CLI is not installed or is not available on PATH.")
    return executable


def _run_az(*args: str) -> Any:
    command = [_az_executable(), *args, "--output", "json", "--only-show-errors"]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (FileNotFoundError, OSError) as exc:
        raise ToolError("Azure CLI could not be started.") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "").strip()
        raise ToolError(message or f"Azure CLI command failed: {' '.join(command)}") from exc

    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ToolError("Azure CLI returned an invalid JSON response.") from exc


def _active_account(login: bool) -> dict:
    try:
        return _run_az("account", "show")
    except ToolError:
        if not login:
            raise ToolError("Azure authentication is required. Run `az login` and retry.")
        subprocess.run([_az_executable(), "login"], check=True)
        return _run_az("account", "show")


def _access_token(resource: str) -> str:
    response = _run_az("account", "get-access-token", "--resource", resource)
    token = response.get("accessToken")
    if not token:
        raise ToolError(f"Azure CLI did not return an access token for {resource}.")
    return token


def _request_json(
    method: str,
    url: str,
    token: str,
    body: Optional[Any] = None,
) -> Tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            text = response.read().decode("utf-8")
            return response.status, json.loads(text) if text else None
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(text)
        except json.JSONDecodeError:
            detail = text
        raise ToolError(f"Azure request failed with HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ToolError(f"Azure request failed: {exc.reason}") from exc


def _resource_graph_query(token: str, query: str, subscriptions: List[str]) -> List[dict]:
    _, response = _request_json(
        "POST",
        RESOURCE_GRAPH_URL,
        token,
        {"query": query, "subscriptions": subscriptions},
    )
    return response.get("data", []) if isinstance(response, dict) else []


def _state_dir() -> Path:
    configured = os.getenv("SENTINEL_XDR_MIGRATION_STATE_DIR")
    return Path(configured).expanduser() if configured else DEFAULT_STATE_DIR


def _read_workspace_settings() -> dict:
    path = _state_dir() / CONFIG_NAME
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _save_workspace_settings(workspace: dict, tenant_id: Optional[str]) -> Path:
    state_root = _state_dir()
    state_root.mkdir(parents=True, exist_ok=True)
    path = state_root / CONFIG_NAME
    settings = _read_workspace_settings()
    settings.update({
        "tenantId": tenant_id,
        "workspaceId": workspace["id"],
        "workspaceName": workspace["name"],
        "workspaceVerifiedAt": datetime.now(timezone.utc).isoformat(),
    })
    path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return path


def _workspace_query(selection: Optional[str]) -> str:
    base = "Resources | where type =~ 'microsoft.operationalinsights/workspaces'"
    if not selection:
        return base + " | project id, name, subscriptionId, resourceGroup, properties"
    escaped = selection.replace("'", "''")
    return (
        base
        + f" | where id =~ '{escaped}' or name =~ '{escaped}' "
        + f"or tostring(properties.customerId) =~ '{escaped}'"
        + " | project id, name, subscriptionId, resourceGroup, properties"
    )


def _tenant_subscriptions(account: dict) -> List[dict]:
    try:
        subscriptions = _run_az("account", "list", "--all")
    except ToolError:
        return [account]
    tenant_id = str(account.get("tenantId") or "").lower()
    accessible = [
        subscription
        for subscription in subscriptions
        if isinstance(subscription, dict)
        and str(subscription.get("tenantId") or "").lower() == tenant_id
        and str(subscription.get("state") or "Enabled").lower() == "enabled"
        and subscription.get("id")
    ]
    return accessible or [account]


def _subscription_ids(value: str | Sequence[str]) -> List[str]:
    return [value] if isinstance(value, str) else list(value)


def _defender_xdr_primary_candidates(
    token: str,
    workspaces: List[dict],
) -> Tuple[List[dict], List[dict]]:
    candidates: List[dict] = []
    inaccessible: List[dict] = []
    for workspace in workspaces:
        url = (
            f"https://management.azure.com{workspace['id']}"
            "/providers/Microsoft.SecurityInsights/dataConnectors"
            f"?api-version={DATA_CONNECTORS_API_VERSION}"
        )
        try:
            _, response = _request_json("GET", url, token)
        except ToolError as exc:
            inaccessible.append({
                "name": workspace.get("name"),
                "id": workspace.get("id"),
                "error": str(exc),
            })
            continue
        connectors = (response or {}).get("value", [])
        if any(_is_primary_defender_xdr_connector(connector) for connector in connectors):
            candidates.append(workspace)
    return candidates, inaccessible


def _is_primary_defender_xdr_connector(connector: Any) -> bool:
    if not isinstance(connector, dict):
        return False
    if str(connector.get("kind") or "").lower() not in DEFENDER_XDR_CONNECTOR_KINDS:
        return False
    data_types = ((connector.get("properties") or {}).get("dataTypes") or {})
    return all(
        str(((data_types.get(name) or {}).get("state") or "")).lower() == "enabled"
        for name in ("alerts", "incidents")
    )


def discover_workspace(
    token: str,
    subscription_ids: str | Sequence[str],
    requested_workspace: Optional[str],
    rediscover_workspace: bool = False,
    tenant_id: Optional[str] = None,
) -> dict:
    settings = _read_workspace_settings()
    saved_tenant = settings.get("tenantId")
    if (
        not requested_workspace
        and not rediscover_workspace
        and saved_tenant
        and tenant_id
        and str(saved_tenant).lower() != str(tenant_id).lower()
    ):
        raise ToolError(
            "Saved workspace settings belong to a different tenant. Use "
            "--rediscover-workspace or provide the workspace ARM resource ID."
        )
    saved_workspace = None if rediscover_workspace else settings.get("workspaceId")
    environment_workspace = (
        os.getenv("AZURE_SENTINEL_WORKSPACE_ID")
        or os.getenv("LA_WORKSPACE_ID")
    )
    selection = requested_workspace or environment_workspace or saved_workspace
    if requested_workspace:
        source = "explicit"
    elif environment_workspace:
        source = "agent-context"
    elif saved_workspace:
        source = "saved-settings"
    else:
        source = "defender-xdr-primary"

    rows = _resource_graph_query(
        token,
        _workspace_query(selection),
        _subscription_ids(subscription_ids),
    )
    rows.sort(key=lambda row: (row.get("name") or "").lower())
    if not rows:
        detail = f" matching {selection!r}" if selection else ""
        raise ToolError(
            f"No accessible Log Analytics workspace{detail} was found in the active subscription."
        )
    if selection:
        if len(rows) > 1:
            matches = "\n".join(f"- {row['id']}" for row in rows)
            raise ToolError(
                f"Multiple workspaces match {selection!r}. Pass a full ARM resource ID:\n{matches}"
            )
        return {
            "workspace": rows[0],
            "alternatives": rows,
            "source": source,
            "settingsExist": bool(saved_workspace),
            "configuredWorkspaceId": saved_workspace,
            "primaryDetection": "not-run",
            "inaccessibleWorkspaces": [],
        }

    candidates, inaccessible = _defender_xdr_primary_candidates(token, rows)
    if len(candidates) > 1:
        matches = "\n".join(f"- {row['id']}" for row in candidates)
        raise ToolError(
            "Multiple accessible workspaces expose a Defender XDR connector, so the "
            f"primary workspace is ambiguous. Pass its full ARM resource ID:\n{matches}"
        )
    if not candidates:
        matches = "\n".join(f"- {row['id']}" for row in rows)
        raise ToolError(
            "The Defender XDR primary workspace could not be inferred from an active "
            "MicrosoftThreatProtection connector. Pass the primary workspace ARM "
            f"resource ID with --workspace. Accessible workspaces:\n{matches}"
        )
    return {
        "workspace": candidates[0],
        "alternatives": rows,
        "source": source,
        "settingsExist": False,
        "configuredWorkspaceId": None,
        "primaryDetection": "microsoft-threat-protection-connector",
        "inaccessibleWorkspaces": inaccessible,
    }


def find_dcr_for_stream(token: str, workspace: dict, stream: str) -> dict:
    workspace_id = workspace["id"]
    subscription_id = workspace["subscriptionId"]
    rows = _resource_graph_query(
        token,
        "Resources | where type =~ 'microsoft.insights/datacollectionrules' "
        "| project id, name, properties",
        [subscription_id],
    )

    for dcr in rows:
        properties = dcr.get("properties") or {}
        streams = {
            candidate
            for flow in properties.get("dataFlows", [])
            for candidate in flow.get("streams", [])
        }
        if stream not in streams:
            continue
        destinations = (properties.get("destinations") or {}).get("logAnalytics", [])
        if not any(
            (destination.get("workspaceResourceId") or "").lower() == workspace_id.lower()
            for destination in destinations
        ):
            continue
        immutable_id = properties.get("immutableId")
        endpoint_id = properties.get("dataCollectionEndpointId")
        if not immutable_id or not endpoint_id:
            continue
        _, dce = _request_json(
            "GET",
            f"https://management.azure.com{endpoint_id}?api-version={DCE_API_VERSION}",
            token,
        )
        endpoint = ((dce or {}).get("properties") or {}).get("logsIngestion", {}).get("endpoint")
        if endpoint:
            return {
                "id": dcr["id"],
                "name": dcr["name"],
                "immutableId": immutable_id,
                "endpoint": endpoint,
            }

    raise ToolError(
        f"No DCR targeting workspace {workspace_id!r} declares stream {stream!r}."
    )


def _workspace_customer_id(token: str, workspace: dict) -> str:
    customer_id = str(((workspace.get("properties") or {}).get("customerId") or "")).strip()
    if customer_id:
        return customer_id
    _, response = _request_json(
        "GET",
        (
            f"https://management.azure.com{workspace['id']}"
            f"?api-version={WORKSPACE_API_VERSION}"
        ),
        token,
    )
    customer_id = str(((response or {}).get("properties") or {}).get("customerId") or "").strip()
    if not customer_id:
        raise ToolError("The selected workspace did not expose its Log Analytics customer ID.")
    return customer_id


def _permission_allows(permission_sets: List[dict], action: str) -> bool:
    requested = action.lower()
    for permission_set in permission_sets:
        allowed = [
            str(pattern).lower()
            for key in ("actions", "dataActions")
            for pattern in permission_set.get(key, [])
        ]
        denied = [
            str(pattern).lower()
            for key in ("notActions", "notDataActions")
            for pattern in permission_set.get(key, [])
        ]
        if any(fnmatch.fnmatchcase(requested, pattern) for pattern in allowed) and not any(
            fnmatch.fnmatchcase(requested, pattern) for pattern in denied
        ):
            return True
    return False


def permission_preflight(arm_token: str, workspace: dict, dcr: dict) -> dict:
    checks: List[dict] = []

    try:
        customer_id = _workspace_customer_id(arm_token, workspace)
        query_token = _access_token(LOG_ANALYTICS_RESOURCE)
        _request_json(
            "POST",
            f"https://api.loganalytics.io/v1/workspaces/{customer_id}/query",
            query_token,
            {"query": "print SentinelMigrationPermissionCheck=1"},
        )
        checks.append({
            "name": "sentinelQueryPermission",
            "status": "ready",
            "detail": "The selected workspace accepted a read-only Log Analytics query.",
        })
    except ToolError as exc:
        checks.append({
            "name": "sentinelQueryPermission",
            "status": "blocked",
            "detail": str(exc),
            "requiredPermission": "Workspace query/read access",
        })

    try:
        _, response = _request_json(
            "GET",
            (
                f"https://management.azure.com{dcr['id']}"
                "/providers/Microsoft.Authorization/permissions"
                f"?api-version={PERMISSIONS_API_VERSION}"
            ),
            arm_token,
        )
        permission_sets = (response or {}).get("value", [])
        if _permission_allows(permission_sets, INGESTION_ACTION):
            checks.append({
                "name": "logsIngestionPermission",
                "status": "ready",
                "detail": f"Effective DCR permissions include {INGESTION_ACTION}.",
            })
        else:
            checks.append({
                "name": "logsIngestionPermission",
                "status": "blocked",
                "detail": f"Effective DCR permissions do not include {INGESTION_ACTION}.",
                "requiredPermission": INGESTION_ACTION,
            })
    except ToolError as exc:
        checks.append({
            "name": "logsIngestionPermission",
            "status": "unknown",
            "detail": (
                "Effective DCR permissions could not be inspected without writing data: "
                f"{exc}"
            ),
            "requiredPermission": INGESTION_ACTION,
        })

    return {
        "status": (
            "ready"
            if all(check["status"] == "ready" for check in checks)
            else "action-required"
        ),
        "checks": checks,
        "writePerformed": False,
    }


def load_payload(path: Path) -> List[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ToolError(f"Cannot read payload {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ToolError(f"Payload {path} is not valid JSON: {exc}") from exc
    if not isinstance(payload, list) or not payload:
        raise ToolError("The payload must be a non-empty JSON array.")
    if not all(isinstance(record, dict) for record in payload):
        raise ToolError("Every payload array item must be a JSON object.")
    return payload


def resolve_payload_path(
    payload: Optional[Path],
    solution: Optional[str],
    rule_id: Optional[str],
    fixture: str,
    mock_data_folder: Optional[Path],
) -> Path:
    if payload:
        return payload.resolve()
    if not solution or not rule_id:
        raise ToolError(
            "Provide --payload, or provide both --solution and --rule-id for default discovery."
        )

    folder = (
        mock_data_folder.resolve()
        if mock_data_folder
        else REPOSITORY_ROOT
        / "Sample Data"
        / "Solutions"
        / "Mock"
        / solution
        / rule_id
    )
    candidate = folder / f"{fixture}.json"
    if not candidate.is_file():
        raise ToolError(
            f"Mock fixture was not found at {candidate}. Ask the user for the mock-data "
            "folder and retry with --mock-data-folder, or pass the file with --payload."
        )
    return candidate


def validate_scenario_for_ingestion(
    payload_path: Path,
    stream: str,
    fixture: str,
) -> Path:
    scenario_path = payload_path.parent / "scenario.json"
    if not scenario_path.is_file():
        raise ToolError(
            f"Scenario manifest was not found at {scenario_path}. Generate or provide a "
            "reviewed scenario before ingestion."
        )
    try:
        scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ToolError(f"Scenario manifest is invalid: {scenario_path}: {exc}") from exc
    if not isinstance(scenario, dict):
        raise ToolError(f"Scenario manifest must be a JSON object: {scenario_path}")

    validation = scenario.get("validation") or {}
    if validation.get("schemaValidation") != "passed":
        raise ToolError("Scenario schema validation has not passed.")
    status = scenario.get("generationStatus")
    if status != "qualification-ready":
        raise ToolError(
            f"Scenario status is {status!r}, not 'qualification-ready'; "
            "direct live ingestion is not approved for this fixture."
        )
    ingestion = scenario.get("ingestion") or {}
    if not ingestion.get("directLogsIngestionSupported"):
        raise ToolError("Scenario does not support direct Logs Ingestion API testing.")
    scenario_stream = ingestion.get("stream")
    if scenario_stream != stream:
        raise ToolError(
            f"Scenario stream {scenario_stream!r} does not match requested stream {stream!r}."
        )
    fixtures = scenario.get("fixtures") or {}
    count_field = f"{fixture}Records"
    if not isinstance(fixtures.get(count_field), int) or fixtures[count_field] < 1:
        raise ToolError(f"Scenario has no reviewed {fixture} records.")
    return scenario_path


def ingest(
    token: str,
    stream: str,
    payload: List[Dict[str, Any]],
    immutable_id: str,
    endpoint: str,
) -> int:
    url = (
        f"{endpoint}/dataCollectionRules/{immutable_id}/streams/{stream}"
        f"?api-version={STREAM_API_VERSION}"
    )
    status, _ = _request_json("POST", url, token, payload)
    return status


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", help="Workspace name, customer ID, or ARM resource ID.")
    parser.add_argument(
        "--rediscover-workspace",
        action="store_true",
        help="Ignore saved workspace settings and rediscover the Defender XDR primary workspace.",
    )
    parser.add_argument(
        "--confirm-workspace",
        action="store_true",
        help="Confirm and persist the selected workspace for this tenant. This is not write approval.",
    )
    parser.add_argument("--stream", required=True, help="DCR input stream, such as Custom-Example_CL.")
    parser.add_argument("--payload", type=Path, help="Explicit reviewed JSON array to ingest.")
    parser.add_argument("--solution", help="Solution folder name used for default fixture discovery.")
    parser.add_argument("--rule-id", help="Rule folder name or identifier used for default fixture discovery.")
    parser.add_argument(
        "--fixture",
        choices=("malicious", "benign"),
        default="malicious",
        help="Fixture file to select when using default folder discovery.",
    )
    parser.add_argument(
        "--mock-data-folder",
        type=Path,
        help="Override folder containing malicious.json and benign.json.",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Resolve and display the workspace and DCR without writing data.",
    )
    parser.add_argument(
        "--approve-write",
        action="store_true",
        help="Required acknowledgement that exact-scope user approval was obtained.",
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="Run `az login` if Azure CLI has no active authenticated account.",
    )
    args = parser.parse_args(argv)

    if not args.discover_only and not args.approve_write:
        parser.error("--approve-write is required for ingestion")

    try:
        account = _active_account(args.login)
        subscriptions = _tenant_subscriptions(account)
        subscription_names = {
            str(subscription.get("id")): subscription.get("name")
            for subscription in subscriptions
        }
        arm_token = _access_token(ARM_RESOURCE)
        discovery = discover_workspace(
            arm_token,
            list(subscription_names),
            args.workspace,
            args.rediscover_workspace,
            account.get("tenantId"),
        )
        workspace = discovery["workspace"]
        verification = {
            "required": not args.confirm_workspace,
            "verifiedThisRun": bool(args.confirm_workspace),
            "settingsExist": discovery["settingsExist"],
            "configuredWorkspaceId": discovery["configuredWorkspaceId"],
            "recommendedWorkspaceId": workspace["id"],
            "recommendedWorkspaceName": workspace["name"],
            "selectionSource": discovery["source"],
            "primaryDetection": discovery["primaryDetection"],
            "actions": (
                ["Use this workspace", "Rediscover primary workspace", "Provide workspace ID", "Cancel"]
                if discovery["settingsExist"]
                else ["Use recommended workspace", "Provide workspace ID", "Cancel"]
            ),
        }
        if not args.confirm_workspace:
            print(json.dumps({
                "status": "awaiting-workspace-confirmation",
                "tenantId": account.get("tenantId"),
                "subscriptionId": workspace["subscriptionId"],
                "subscriptionName": subscription_names.get(workspace["subscriptionId"]),
                "workspace": workspace["name"],
                "workspaceResourceId": workspace["id"],
                "workspaceAlternatives": [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in discovery["alternatives"]
                ],
                "workspaceVerification": verification,
                "writeApproved": False,
            }, indent=2))
            return 0

        settings_path = _save_workspace_settings(workspace, account.get("tenantId"))
        dcr = find_dcr_for_stream(
            arm_token,
            workspace,
            args.stream,
        )
        result = {
            "tenantId": account.get("tenantId"),
            "subscriptionId": workspace["subscriptionId"],
            "subscriptionName": subscription_names.get(workspace["subscriptionId"]),
            "workspace": workspace["name"],
            "workspaceResourceId": workspace["id"],
            "workspaceSelectionSource": discovery["source"],
            "workspaceAlternatives": [
                {"name": item.get("name"), "id": item.get("id")}
                for item in discovery["alternatives"]
            ],
            "workspaceSettings": str(settings_path),
            "workspaceVerification": verification,
            "stream": args.stream,
            "dcr": dcr["name"],
            "dcrResourceId": dcr["id"],
            "dcrImmutableId": dcr["immutableId"],
            "dceEndpoint": dcr["endpoint"],
            "writeApproved": bool(args.approve_write),
        }

        if args.discover_only:
            result["preflight"] = permission_preflight(arm_token, workspace, dcr)
            result["status"] = result["preflight"]["status"]
            print(json.dumps(result, indent=2))
            return 0

        payload_path = resolve_payload_path(
            args.payload,
            args.solution,
            args.rule_id,
            args.fixture,
            args.mock_data_folder,
        )
        payload = load_payload(payload_path)
        scenario_path = validate_scenario_for_ingestion(
            payload_path,
            args.stream,
            args.fixture,
        )
        monitor_token = _access_token(MONITOR_RESOURCE)
        result["httpStatus"] = ingest(
            monitor_token,
            args.stream,
            payload,
            dcr["immutableId"],
            dcr["endpoint"],
        )
        result["recordCount"] = len(payload)
        result["payload"] = str(payload_path)
        result["scenario"] = str(scenario_path)
        result["status"] = "accepted"
        result["validation"] = "not-run"
        print(json.dumps(result, indent=2))
        return 0
    except (ToolError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
