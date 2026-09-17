"""Discover a workspace DCR and optionally ingest a reviewed JSON payload.

This tool is intentionally standalone: it uses Azure CLI authentication and the
Python standard library only. Payload generation and rule validation are separate
steps. A successful HTTP response proves ingestion acceptance, not rule execution.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ARM_RESOURCE = "https://management.azure.com/"
MONITOR_RESOURCE = "https://monitor.azure.com/"
RESOURCE_GRAPH_URL = (
    "https://management.azure.com/providers/Microsoft.ResourceGraph/resources"
    "?api-version=2021-03-01"
)
DCE_API_VERSION = "2023-03-11"
STREAM_API_VERSION = "2023-01-01"


class ToolError(RuntimeError):
    """A user-actionable discovery or ingestion failure."""


def _run_az(*args: str) -> Any:
    command = ["az", *args, "--output", "json", "--only-show-errors"]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise ToolError("Azure CLI is not installed or is not available on PATH.") from exc
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
        subprocess.run(["az", "login"], check=True)
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


def _workspace_query(selection: Optional[str]) -> str:
    base = "Resources | where type =~ 'microsoft.operationalinsights/workspaces'"
    if not selection:
        return base + " | project id, name, subscriptionId, resourceGroup, properties"
    escaped = selection.replace("'", "''")
    return (
        base
        + f" | where name =~ '{escaped}' or tostring(properties.customerId) =~ '{escaped}'"
        + " | project id, name, subscriptionId, resourceGroup, properties"
    )


def discover_workspace(
    token: str,
    subscription_id: str,
    requested_workspace: Optional[str],
) -> Tuple[dict, List[dict], str]:
    selection = (
        requested_workspace
        or os.getenv("AZURE_SENTINEL_WORKSPACE_ID")
        or os.getenv("LA_WORKSPACE_ID")
    )
    source = (
        "explicit"
        if requested_workspace
        else "agent-context"
        if selection
        else "active-subscription"
    )

    if selection and selection.lower().startswith("/subscriptions/"):
        parts = selection.split("/")
        if len(parts) < 9:
            raise ToolError("The workspace ARM resource ID is malformed.")
        selected = {
            "id": selection,
            "name": parts[-1],
            "subscriptionId": parts[2],
            "resourceGroup": parts[4],
            "properties": {},
        }
        return selected, [selected], source

    rows = _resource_graph_query(
        token,
        _workspace_query(selection),
        [subscription_id],
    )
    rows.sort(key=lambda row: (row.get("name") or "").lower())
    if not rows:
        detail = f" matching {selection!r}" if selection else ""
        raise ToolError(
            f"No accessible Log Analytics workspace{detail} was found in the active subscription."
        )
    if selection and len(rows) > 1:
        matches = "\n".join(f"- {row['id']}" for row in rows)
        raise ToolError(
            f"Multiple workspaces match {selection!r}. Pass a full ARM resource ID:\n{matches}"
        )
    return rows[0], rows, source


def find_dcr_for_stream(token: str, workspace: dict, stream: str) -> Tuple[str, str, str]:
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
            return dcr["name"], immutable_id, endpoint

    raise ToolError(
        f"No DCR targeting workspace {workspace_id!r} declares stream {stream!r}."
    )


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
        arm_token = _access_token(ARM_RESOURCE)
        workspace, alternatives, selection_source = discover_workspace(
            arm_token,
            account["id"],
            args.workspace,
        )
        dcr_name, immutable_id, endpoint = find_dcr_for_stream(
            arm_token,
            workspace,
            args.stream,
        )
        result = {
            "tenantId": account.get("tenantId"),
            "subscriptionId": workspace["subscriptionId"],
            "subscriptionName": account.get("name"),
            "workspace": workspace["name"],
            "workspaceResourceId": workspace["id"],
            "workspaceSelectionSource": selection_source,
            "workspaceAlternatives": [
                {"name": item.get("name"), "id": item.get("id")} for item in alternatives
            ],
            "stream": args.stream,
            "dcr": dcr_name,
            "dcrImmutableId": immutable_id,
            "dceEndpoint": endpoint,
            "writeApproved": bool(args.approve_write),
        }

        if args.discover_only:
            result["status"] = "ready"
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
            immutable_id,
            endpoint,
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
