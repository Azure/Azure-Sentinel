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
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
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
TABLE_API_VERSION = "2025-07-01"
INGESTION_ACTION = "Microsoft.Insights/Telemetry/Write"
TABLE_WRITE_ACTION = "Microsoft.OperationalInsights/workspaces/tables/write"
WORKSPACE_WRITE_ACTION = "Microsoft.OperationalInsights/workspaces/write"


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
    accepted_error_codes: Sequence[int] = (),
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
        if exc.code in accepted_error_codes:
            return exc.code, detail
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
        return selected, [], source

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
    return rows[0], [] if selection else rows, source


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
        flow = next(
            (
                candidate
                for candidate in properties.get("dataFlows", [])
                if stream in candidate.get("streams", [])
            ),
            None,
        )
        if flow is None:
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
            output_stream = str(flow.get("outputStream") or stream)
            return {
                "id": dcr["id"],
                "name": dcr["name"],
                "immutableId": immutable_id,
                "endpoint": endpoint,
                "outputStream": output_stream,
                "outputTable": _custom_table_name(output_stream),
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


def _custom_table_name(output_stream: str) -> Optional[str]:
    if not output_stream.startswith("Custom-"):
        return None
    table_name = output_stream.removeprefix("Custom-")
    return table_name if table_name.endswith("_CL") else None


def _walk_resources(resources: Iterable[dict]) -> Iterable[dict]:
    for resource in resources:
        if not isinstance(resource, dict):
            continue
        yield resource
        nested = resource.get("resources")
        if isinstance(nested, list):
            yield from _walk_resources(nested)
        properties = resource.get("properties") or {}
        for template_key in ("template", "mainTemplate"):
            template = properties.get(template_key) or {}
            if isinstance(template, dict):
                yield from _walk_resources(template.get("resources") or [])


def _solution_root(solution: str) -> Path:
    requested = Path(solution).expanduser()
    root = requested.resolve() if requested.is_dir() else REPOSITORY_ROOT / "Solutions" / solution
    if not root.is_dir():
        raise ToolError(f"Solution folder does not exist: {root}")
    return root


def _column_type(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    aliases = {
        "bool": "boolean",
        "boolean": "boolean",
        "datetime": "dateTime",
        "date_time": "dateTime",
        "dynamic": "dynamic",
        "guid": "guid",
        "int": "int",
        "integer": "int",
        "long": "long",
        "real": "real",
        "double": "real",
        "string": "string",
    }
    if normalized not in aliases:
        raise ToolError(f"Unsupported custom-table column type: {value!r}")
    return aliases[normalized]


def load_custom_table_contract(solution: str, table_name: str) -> dict:
    root = _solution_root(solution)
    package = root / "Package" / "mainTemplate.json"
    if not package.is_file():
        raise ToolError(f"Solution package was not found: {package}")
    try:
        template = json.loads(package.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ToolError(f"Solution package is invalid: {package}: {exc}") from exc

    for resource in _walk_resources(template.get("resources") or []):
        if str(resource.get("type") or "").lower() != (
            "microsoft.operationalinsights/workspaces/tables"
        ):
            continue
        properties = resource.get("properties") or {}
        schema = properties.get("schema") or {}
        if str(schema.get("name") or "") != table_name:
            continue
        columns = schema.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ToolError(
                f"Packaged table {table_name!r} has no deployable schema columns: {package}"
            )
        normalized_columns = []
        for column in columns:
            if not isinstance(column, dict) or not column.get("name"):
                raise ToolError(f"Packaged table {table_name!r} has an invalid column.")
            normalized_columns.append({
                "name": str(column["name"]),
                "type": _column_type(column.get("type")),
            })
        table_properties: Dict[str, Any] = {
            "schema": {
                "name": table_name,
                "columns": normalized_columns,
            }
        }
        for name in ("plan", "retentionInDays", "totalRetentionInDays"):
            if properties.get(name) is not None:
                table_properties[name] = properties[name]
        return {
            "tableName": table_name,
            "properties": table_properties,
            "schemaSource": str(package),
            "columnCount": len(normalized_columns),
            "tablePlan": str(table_properties.get("plan") or "Analytics"),
            "retentionInDays": table_properties.get("retentionInDays"),
            "totalRetentionInDays": table_properties.get("totalRetentionInDays"),
        }

    raise ToolError(
        f"Solution package does not define custom table {table_name!r}: {package}"
    )


def _table_url(workspace: dict, table_name: str) -> str:
    return (
        f"https://management.azure.com{workspace['id']}/tables/{table_name}"
        f"?api-version={TABLE_API_VERSION}"
    )


def _schema_differences(contract: dict, table: dict) -> List[str]:
    expected_columns = (
        ((contract.get("properties") or {}).get("schema") or {}).get("columns") or []
    )
    actual_schema = ((table.get("properties") or {}).get("schema") or {})
    actual_columns = [
        *actual_schema.get("columns", []),
        *actual_schema.get("standardColumns", []),
    ]
    actual_by_name = {
        str(column.get("name") or "").lower(): _column_type(column.get("type"))
        for column in actual_columns
        if isinstance(column, dict) and column.get("name") and column.get("type")
    }
    differences: List[str] = []
    for column in expected_columns:
        name = str(column["name"])
        expected_type = _column_type(column["type"])
        actual_type = actual_by_name.get(name.lower())
        if actual_type is None:
            differences.append(f"missing column {name}")
        elif actual_type != expected_type:
            differences.append(
                f"column {name} is {actual_type}, expected {expected_type}"
            )
    return differences


def inspect_custom_table(
    arm_token: str,
    workspace: dict,
    table_name: str,
    contract: Optional[dict],
    contract_error: Optional[str] = None,
) -> dict:
    status, response = _request_json(
        "GET",
        _table_url(workspace, table_name),
        arm_token,
        accepted_error_codes=(404,),
    )
    if status == 404:
        return {
            "name": "customLogTable",
            "status": "missing",
            "detail": f"Custom table {table_name!r} does not exist in the selected workspace.",
            "tableName": table_name,
            "deploymentAvailable": contract is not None,
            "schemaSource": contract.get("schemaSource") if contract else None,
            "columnCount": contract.get("columnCount") if contract else None,
            "tablePlan": contract.get("tablePlan") if contract else None,
            "retentionInDays": contract.get("retentionInDays") if contract else None,
            "totalRetentionInDays": (
                contract.get("totalRetentionInDays") if contract else None
            ),
            "schemaError": contract_error,
        }

    if contract_error:
        return {
            "name": "customLogTable",
            "status": "unknown",
            "detail": (
                f"Custom table {table_name!r} exists, but its schema could not be "
                f"compared with the solution package: {contract_error}"
            ),
            "tableName": table_name,
            "deploymentAvailable": False,
            "schemaCompatible": None,
        }

    differences = _schema_differences(contract, response or {}) if contract else []
    if differences:
        return {
            "name": "customLogTable",
            "status": "blocked",
            "detail": (
                f"Custom table {table_name!r} exists but does not match the packaged schema: "
                + "; ".join(differences)
            ),
            "tableName": table_name,
            "deploymentAvailable": False,
            "schemaCompatible": False,
        }
    return {
        "name": "customLogTable",
        "status": "ready",
        "detail": f"Custom table {table_name!r} exists in the selected workspace.",
        "tableName": table_name,
        "deploymentAvailable": False,
        "schemaCompatible": True if contract else None,
    }


def _effective_permissions(arm_token: str, resource_id: str) -> List[dict]:
    _, response = _request_json(
        "GET",
        (
            f"https://management.azure.com{resource_id}"
            "/providers/Microsoft.Authorization/permissions"
            f"?api-version={PERMISSIONS_API_VERSION}"
        ),
        arm_token,
    )
    return (response or {}).get("value", [])


def _table_deployment_permissions(contract: dict) -> List[str]:
    required = [TABLE_WRITE_ACTION]
    if (contract.get("properties") or {}).get("plan") is not None:
        required.append(WORKSPACE_WRITE_ACTION)
    return required


def permission_preflight(
    arm_token: str,
    workspace: dict,
    dcr: dict,
    table_contract: Optional[dict] = None,
    table_contract_error: Optional[str] = None,
) -> dict:
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
        permission_sets = _effective_permissions(arm_token, dcr["id"])
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

    table_name = dcr.get("outputTable")
    if table_name:
        try:
            table_check = inspect_custom_table(
                arm_token,
                workspace,
                table_name,
                table_contract,
                table_contract_error,
            )
            checks.append(table_check)
        except ToolError as exc:
            table_check = {
                "name": "customLogTable",
                "status": "unknown",
                "detail": f"Custom table state could not be inspected: {exc}",
                "tableName": table_name,
                "deploymentAvailable": False,
                "requiredPermission": (
                    "Microsoft.OperationalInsights/workspaces/tables/read"
                ),
            }
            checks.append(table_check)

        if table_check["status"] == "missing":
            if table_contract is None:
                checks.append({
                    "name": "customTableDeploymentPermission",
                    "status": "blocked",
                    "detail": (
                        "The table is missing, but no exact packaged schema was supplied. "
                        + (
                            table_contract_error
                            if table_contract_error
                            else "Pass --solution to enable guarded deployment."
                        )
                    ),
                    "requiredPermission": TABLE_WRITE_ACTION,
                })
            else:
                required_actions = _table_deployment_permissions(table_contract)
                try:
                    permission_sets = _effective_permissions(arm_token, workspace["id"])
                    missing_actions = [
                        action
                        for action in required_actions
                        if not _permission_allows(permission_sets, action)
                    ]
                    if missing_actions:
                        checks.append({
                            "name": "customTableDeploymentPermission",
                            "status": "blocked",
                            "detail": (
                                "Effective workspace permissions do not allow creation "
                                f"of {table_name!r}."
                            ),
                            "requiredPermissions": missing_actions,
                        })
                    else:
                        checks.append({
                            "name": "customTableDeploymentPermission",
                            "status": "ready",
                            "detail": (
                                "Effective workspace permissions allow creation of "
                                f"{table_name!r}."
                            ),
                            "requiredPermissions": required_actions,
                        })
                except ToolError as exc:
                    checks.append({
                        "name": "customTableDeploymentPermission",
                        "status": "unknown",
                        "detail": (
                            "Effective workspace table permissions could not be "
                            f"inspected without writing: {exc}"
                        ),
                        "requiredPermissions": required_actions,
                    })

    return {
        "status": (
            "ready"
            if all(check["status"] in {"ready", "not-required"} for check in checks)
            else "action-required"
        ),
        "checks": checks,
        "writePerformed": False,
    }


def deploy_custom_table(
    arm_token: str,
    workspace: dict,
    contract: dict,
    *,
    attempts: int = 20,
    delay_seconds: float = 3,
) -> dict:
    table_name = contract["tableName"]
    status, _ = _request_json(
        "PUT",
        _table_url(workspace, table_name),
        arm_token,
        {"properties": contract["properties"]},
    )
    if status not in {200, 201, 202}:
        raise ToolError(
            f"Custom table deployment returned unexpected HTTP status {status}."
        )

    for _ in range(attempts):
        read_status, table = _request_json(
            "GET",
            _table_url(workspace, table_name),
            arm_token,
            accepted_error_codes=(404,),
        )
        if read_status != 404:
            provisioning = str(
                ((table or {}).get("properties") or {}).get("provisioningState") or ""
            )
            if provisioning.lower() in {"failed", "deleting"}:
                raise ToolError(
                    f"Custom table {table_name!r} provisioning ended in {provisioning!r}."
                )
            if provisioning.lower() in {"", "succeeded"}:
                differences = _schema_differences(contract, table or {})
                if differences:
                    raise ToolError(
                        f"Custom table {table_name!r} was created with an unexpected schema: "
                        + "; ".join(differences)
                    )
                return {
                    "status": "created",
                    "httpStatus": status,
                    "tableName": table_name,
                    "tableResourceId": (table or {}).get("id"),
                    "schemaSource": contract["schemaSource"],
                    "columnCount": contract["columnCount"],
                    "tablePlan": contract.get("tablePlan") or "Analytics",
                    "retentionInDays": contract.get("retentionInDays"),
                    "totalRetentionInDays": contract.get("totalRetentionInDays"),
                }
        time.sleep(delay_seconds)
    raise ToolError(
        f"Timed out waiting for custom table {table_name!r} to finish provisioning."
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
        "--deploy-missing-table",
        action="store_true",
        help="Create the missing packaged custom table, then rerun the preflight.",
    )
    parser.add_argument(
        "--approve-table-write",
        action="store_true",
        help="Required acknowledgement of exact workspace/table deployment approval.",
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

    if args.deploy_missing_table:
        if args.discover_only:
            parser.error("--deploy-missing-table and --discover-only are separate modes")
        if not args.approve_table_write:
            parser.error("--approve-table-write is required for custom-table deployment")
        if not args.solution:
            parser.error("--solution is required for custom-table deployment")
        if args.approve_write:
            parser.error("table deployment and payload ingestion must be approved separately")
    elif args.approve_table_write:
        parser.error("--approve-table-write requires --deploy-missing-table")
    elif not args.discover_only and not args.approve_write:
        parser.error("--approve-write is required for ingestion")

    try:
        account = _active_account(args.login)
        arm_token = _access_token(ARM_RESOURCE)
        workspace, alternatives, selection_source = discover_workspace(
            arm_token,
            account["id"],
            args.workspace,
        )
        dcr = find_dcr_for_stream(
            arm_token,
            workspace,
            args.stream,
        )
        workspace_customer_id = _workspace_customer_id(arm_token, workspace)
        workspace.setdefault("properties", {})["customerId"] = workspace_customer_id
        table_contract = None
        table_contract_error = None
        if (
            args.solution
            and dcr.get("outputTable")
            and (args.discover_only or args.deploy_missing_table)
        ):
            try:
                table_contract = load_custom_table_contract(
                    args.solution,
                    dcr["outputTable"],
                )
            except ToolError as exc:
                if args.deploy_missing_table:
                    raise
                table_contract_error = str(exc)
        result = {
            "tenantId": account.get("tenantId"),
            "subscriptionId": workspace["subscriptionId"],
            "subscriptionName": account.get("name"),
            "workspace": workspace["name"],
            "workspaceResourceId": workspace["id"],
            "workspaceCustomerId": workspace_customer_id,
            "workspaceSelectionSource": selection_source,
            "workspaceAlternatives": [
                {"name": item.get("name"), "id": item.get("id")} for item in alternatives
            ],
            "stream": args.stream,
            "dcr": dcr["name"],
            "dcrResourceId": dcr["id"],
            "dcrImmutableId": dcr["immutableId"],
            "dceEndpoint": dcr["endpoint"],
            "outputStream": dcr.get("outputStream"),
            "outputTable": dcr.get("outputTable"),
            "writeApproved": bool(args.approve_write),
            "tableWriteApproved": bool(args.approve_table_write),
        }

        if args.discover_only or args.deploy_missing_table:
            result["preflight"] = permission_preflight(
                arm_token,
                workspace,
                dcr,
                table_contract,
                table_contract_error,
            )
        if args.discover_only:
            result["status"] = result["preflight"]["status"]
            print(json.dumps(result, indent=2))
            return 0
        if args.deploy_missing_table:
            table_check = next(
                (
                    check
                    for check in result["preflight"]["checks"]
                    if check["name"] == "customLogTable"
                ),
                None,
            )
            permission_check = next(
                (
                    check
                    for check in result["preflight"]["checks"]
                    if check["name"] == "customTableDeploymentPermission"
                ),
                None,
            )
            if not table_check or table_check["status"] != "missing":
                raise ToolError(
                    "Custom-table deployment is allowed only when preflight confirms "
                    "that the exact destination table is missing."
                )
            if not permission_check or permission_check["status"] != "ready":
                raise ToolError(
                    "Effective workspace permissions do not authorize custom-table deployment."
                )
            result["tableDeployment"] = deploy_custom_table(
                arm_token,
                workspace,
                table_contract,
            )
            result["preflightAfterDeployment"] = permission_preflight(
                arm_token,
                workspace,
                dcr,
                table_contract,
                table_contract_error,
            )
            result["status"] = result["preflightAfterDeployment"]["status"]
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
