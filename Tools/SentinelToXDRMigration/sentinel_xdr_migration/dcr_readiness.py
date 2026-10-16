from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .artifacts import (
    artifact_path,
    resolve_artifact_reference,
    write_json_artifact,
)
from .logs_query import (
    azure_cli_credential,
    execute_workspace_query,
    logs_query_client,
)
from .target_context import resolve_workspace_customer_id, workspace_identity

ARM_SCOPE = "https://management.azure.com/.default"
ARM_BASE = "https://management.azure.com"
PERMISSIONS_API_VERSION = "2022-04-01"
RESOURCE_API_VERSION = "2023-03-11"
TABLE_API_VERSION = "2022-10-01"
INGESTION_ACTION = "Microsoft.Insights/Telemetry/Write"
DCR_WRITE_ACTION = "Microsoft.Insights/dataCollectionRules/write"
DCE_WRITE_ACTION = "Microsoft.Insights/dataCollectionEndpoints/write"
TABLE_WRITE_ACTION = "Microsoft.OperationalInsights/workspaces/tables/write"
REPORT_NAME = "qualification-dcr-preflight.json"
_UUID_TEXT = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
_EMAIL_TEXT = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_BEARER_TEXT = re.compile(r"(?i)\bBearer\s+\S+")
_JWT_TEXT = re.compile(
    r"\beyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
)


def _safe_message(value: Any) -> str:
    message = str(value)
    message = _BEARER_TEXT.sub("Bearer [REDACTED]", message)
    message = _JWT_TEXT.sub("[REDACTED_TOKEN]", message)
    message = _EMAIL_TEXT.sub("[REDACTED_IDENTITY]", message)
    return _UUID_TEXT.sub("[REDACTED_ID]", message)[:1000]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _ingestion_root() -> Path:
    return _repo_root() / "Tools" / "AzureMonitorLogsIngestion"


def _ingestion_modules():
    tool_root = str(_ingestion_root())
    if tool_root not in sys.path:
        sys.path.insert(0, tool_root)
    from azure_monitor_logs_ingestion.contract import load_contract
    from azure_monitor_logs_ingestion.registry import (
        destination_schema_blockers,
        inspect_managed_resources,
        resolve_contract,
    )

    return load_contract, destination_schema_blockers, inspect_managed_resources, resolve_contract


def _build_local_plan(solution: Path, target: Mapping[str, str]) -> dict[str, Any]:
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)
    from Tools.SolutionMigration.resolve_ingestion_contracts import build_plan
    from .packaging_selection import current_applied_package_selection

    locked = {
        field: str(target[field])
        for field in (
            "tenantId",
            "subscriptionId",
            "workspaceResourceId",
            "workspaceCustomerId",
        )
    }
    selection = current_applied_package_selection(solution)
    if selection is None:
        return build_plan(solution, locked)
    plan = selection["plan"]
    selection_path = resolve_artifact_reference(solution, selection["planPath"])
    return build_plan(
        solution,
        locked,
        selection_plan_path=selection_path,
        expected_selection_plan_sha256=plan["planSha256"],
    )


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_error(response: Mapping[str, Any] | None) -> dict[str, str | None]:
    error = response.get("error") if isinstance(response, Mapping) else None
    if not isinstance(error, Mapping):
        return {"code": None, "message": None}
    code = error.get("code")
    message = error.get("message")
    return {
        "code": str(code)[:200] if code is not None else None,
        "message": _safe_message(message) if message is not None else None,
    }


def _arm_get(token: str, resource_id: str, api_version: str) -> tuple[int, Any]:
    url = (
        f"{ARM_BASE}{resource_id}?api-version="
        f"{urllib.parse.quote(api_version, safe='')}"
    )
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read()
            return int(response.status), json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read()
            payload = json.loads(body) if body else {}
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            payload = {}
        return int(exc.code), payload


def _action_permission(
    permission_sets: Any, requested_action: str
) -> dict[str, Any]:
    if not isinstance(permission_sets, list):
        return {"status": "unknown", "reason": "permissions.value is not an array"}
    if not permission_sets:
        return {"status": "denied", "matchingAllows": [], "matchingExclusions": []}

    requested = requested_action.casefold()
    matching_allows: set[str] = set()
    matching_exclusions: set[str] = set()
    for index, permission_set in enumerate(permission_sets):
        if not isinstance(permission_set, Mapping):
            return {
                "status": "unknown",
                "reason": f"permissions.value[{index}] is not an object",
            }
        if "condition" in permission_set or "conditionVersion" in permission_set:
            return {
                "status": "unknown",
                "reason": "permission response contains a condition that cannot be evaluated",
            }

        allowed: list[str] = []
        excluded: list[str] = []
        for key in ("actions", "dataActions", "notActions", "notDataActions"):
            values = permission_set.get(key, [])
            if not isinstance(values, list) or any(
                not isinstance(value, str) for value in values
            ):
                return {
                    "status": "unknown",
                    "reason": f"permissions.value[{index}].{key} is malformed",
                }
            normalized = [value.casefold() for value in values]
            if key in {"actions", "dataActions"}:
                allowed.extend(normalized)
            else:
                excluded.extend(normalized)

        allows = {
            pattern
            for pattern in allowed
            if fnmatch.fnmatchcase(requested, pattern)
        }
        denies = {
            pattern
            for pattern in excluded
            if fnmatch.fnmatchcase(requested, pattern)
        }
        matching_allows.update(allows)
        matching_exclusions.update(denies)
        if allows and not denies:
            return {
                "status": "ready",
                "matchingAllows": sorted(allows),
                "matchingExclusions": [],
            }

    return {
        "status": "denied",
        "matchingAllows": sorted(matching_allows),
        "matchingExclusions": sorted(matching_exclusions),
    }


def _permissions_for_scope(
    token: str, scope_id: str
) -> dict[str, Any]:
    status_code, response = _arm_get(
        token,
        f"{scope_id}/providers/Microsoft.Authorization/permissions",
        PERMISSIONS_API_VERSION,
    )
    if status_code != 200:
        return {
            "inspectionStatus": (
                "unavailable" if status_code == 401 else "denied" if status_code == 403 else "unknown"
            ),
            "httpStatus": status_code,
            "error": _safe_error(response),
        }
    if not isinstance(response, Mapping) or not isinstance(response.get("value"), list):
        return {
            "inspectionStatus": "unknown",
            "httpStatus": status_code,
            "error": {"code": "MalformedPermissionResponse", "message": "expected value array"},
        }
    if response.get("nextLink"):
        return {
            "inspectionStatus": "unknown",
            "httpStatus": status_code,
            "error": {
                "code": "PartialPermissionResponse",
                "message": "permission results have a nextLink and were not treated as complete",
            },
        }
    return {
        "inspectionStatus": "complete",
        "httpStatus": status_code,
        "permissionSets": response["value"],
    }


def _check_action(
    token: str, scope_id: str, action: str
) -> dict[str, Any]:
    inspected = _permissions_for_scope(token, scope_id)
    if inspected["inspectionStatus"] != "complete":
        return {
            "status": "unknown",
            "requiredAction": action,
            "inspectionStatus": inspected["inspectionStatus"],
            "httpStatus": inspected.get("httpStatus"),
            "error": inspected.get("error"),
            "scope": scope_id,
        }
    evaluation = _action_permission(inspected["permissionSets"], action)
    return {
        **evaluation,
        "requiredAction": action,
        "inspectionStatus": "complete",
        "httpStatus": inspected["httpStatus"],
        "scope": scope_id,
    }


def _arm_resource_ids(target: Mapping[str, str], contract: Any) -> tuple[str, str, str]:
    identity = workspace_identity(target["workspaceResourceId"])
    prefix = (
        f"/subscriptions/{identity['subscriptionId']}"
        f"/resourceGroups/{identity['resourceGroup']}"
        "/providers/Microsoft.Insights"
    )
    dce_id = f"{prefix}/dataCollectionEndpoints/{contract.resources.dce}"
    dcr_id = f"{prefix}/dataCollectionRules/{contract.resources.dcr}"
    table_id = (
        f"{target['workspaceResourceId']}/tables/{contract.destination.table}"
    )
    return dce_id, dcr_id, table_id


def _contract_records(plan: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups = plan.get("groups")
    if not isinstance(groups, list):
        return [], [{"status": "unknown", "reason": "local plan groups are malformed"}]
    records: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    load_contract, _, _, resolve_contract = _ingestion_modules()
    ingestion_root = _ingestion_root().resolve()
    for group in groups:
        if not isinstance(group, Mapping) or not isinstance(group.get("table"), str):
            blockers.append({"status": "unknown", "reason": "local plan group is malformed"})
            continue
        table = group["table"]
        resolution = resolve_contract(table)
        if resolution.get("status") == "blocked":
            blockers.append(
                {
                    "status": "blocked",
                    "table": table,
                    "reason": "; ".join(resolution.get("blockers") or []),
                }
            )
            continue
        relative = Path(str(resolution.get("contractPath") or ""))
        contract_path = (ingestion_root / relative).resolve()
        if ingestion_root not in contract_path.parents or not contract_path.is_file():
            blockers.append(
                {
                    "status": "unknown",
                    "table": table,
                    "reason": "registered contract path is invalid",
                }
            )
            continue
        contract = load_contract(contract_path)
        if (
            group.get("schemaFingerprint") != resolution.get("schemaFingerprint")
            or group.get("transformFingerprint") != resolution.get("transformFingerprint")
        ):
            blockers.append(
                {
                    "status": "unknown",
                    "table": table,
                    "reason": "local plan fingerprints differ from current registered contract",
                }
            )
            continue
        records.append(
            {
                "table": table,
                "contractPath": relative.as_posix(),
                "schemaFingerprint": resolution["schemaFingerprint"],
                "transformFingerprint": resolution["transformFingerprint"],
                "contractFingerprint": _fingerprint(contract.as_dict()),
                "contract": contract,
                "ruleIds": group.get("ruleIds") or [],
            }
        )
    return records, blockers


def _check_query_permission(target: Mapping[str, str], credential: Any) -> dict[str, Any]:
    client = logs_query_client(credential, retry_total=0)
    try:
        result = execute_workspace_query(
            client,
            target["workspaceCustomerId"],
            "print SentinelXdrPreflight=1",
            request_timeout_seconds=15,
            retry_count=0,
        )
        if result.get("status") != "passed":
            return {
                "status": "unknown",
                "httpStatus": result.get("statusCode"),
                "failureKind": result.get("failureKind") or "partial-response",
                "error": (
                    _safe_message(result.get("error"))
                    if result.get("error") is not None
                    else None
                ),
                "meansDataVisible": False,
            }
        return {
            "status": "ready",
            "detail": "Read-only query succeeded against the exact locked workspace.",
            "rowsReturned": result.get("rowCount", 0),
            "meansDataVisible": False,
        }
    except Exception as exc:
        status_code = getattr(exc, "status_code", None)
        failure_kind = getattr(exc, "failure_kind", None)
        return {
            "status": "denied" if failure_kind == "authorization" else "unknown",
            "httpStatus": status_code,
            "failureKind": failure_kind or type(exc).__name__,
            "error": _safe_message(exc),
            "meansDataVisible": False,
        }
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()


def _check_resource(
    token: str, resource_id: str, api_version: str
) -> tuple[str, dict[str, Any] | None, dict[str, Any]]:
    status_code, response = _arm_get(token, resource_id, api_version)
    if status_code == 200 and isinstance(response, Mapping):
        actual_id = str(response.get("id") or "")
        if actual_id.casefold() != resource_id.casefold():
            return "unknown", None, {
                "httpStatus": status_code,
                "error": {
                    "code": "UnexpectedResourceId",
                    "message": "resource GET did not match the exact selected resource ID",
                },
            }
        return "present", dict(response), {"httpStatus": status_code}
    if status_code == 404:
        return "missing", None, {"httpStatus": status_code, "error": _safe_error(response)}
    return (
        "denied" if status_code == 403 else "unavailable" if status_code == 401 else "unknown",
        None,
        {"httpStatus": status_code, "error": _safe_error(response)},
    )


def _destination_schema(table: Any) -> Mapping[str, Any] | None:
    if not isinstance(table, Mapping):
        return None
    properties = table.get("properties")
    if not isinstance(properties, Mapping):
        return None
    schema = properties.get("schema")
    return schema if isinstance(schema, Mapping) else None


def _check_candidate(
    target: Mapping[str, str],
    token: str,
    record: Mapping[str, Any],
) -> dict[str, Any]:
    contract = record["contract"]
    dce_id, dcr_id, table_id = _arm_resource_ids(target, contract)
    dce_state, dce, dce_evidence = _check_resource(token, dce_id, RESOURCE_API_VERSION)
    dcr_state, dcr, dcr_evidence = _check_resource(token, dcr_id, RESOURCE_API_VERSION)
    table_state, table, table_evidence = _check_resource(token, table_id, TABLE_API_VERSION)
    def _read_status(state: str) -> str:
        if state == "present":
            return "ready"
        if state == "denied":
            return "denied"
        if state == "unavailable":
            return "unavailable"
        return "unknown"

    result: dict[str, Any] = {
        "table": record["table"],
        "contractPath": record["contractPath"],
        "schemaFingerprint": record["schemaFingerprint"],
        "transformFingerprint": record["transformFingerprint"],
        "contractFingerprint": record["contractFingerprint"],
        "resourceFingerprint": _fingerprint(
            {
                "targetWorkspace": target["workspaceResourceId"],
                "dceId": dce_id,
                "dcrId": dcr_id,
                "tableId": table_id,
                "dce": dce,
                "dcr": dcr,
                "destinationSchema": (
                    _destination_schema(table)
                    if table_state == "present"
                    else None
                ),
                "states": {
                    "dce": dce_state,
                    "dcr": dcr_state,
                    "table": table_state,
                },
            }
        ),
        "ruleIds": record["ruleIds"],
        "candidateProvenance": "registered-contract-resolver",
        "candidateSelection": "exact-contract-resource-names-only",
        "resources": {
            "dce": {
                "id": dce_id,
                "state": dce_state,
                "readAccess": _read_status(dce_state),
                **dce_evidence,
            },
            "dcr": {
                "id": dcr_id,
                "state": dcr_state,
                "readAccess": _read_status(dcr_state),
                **dcr_evidence,
            },
            "destinationTable": {
                "id": table_id,
                "state": table_state,
                "readAccess": _read_status(table_state),
                **table_evidence,
            },
        },
        "resourceReadAccess": {
            "status": "ready"
            if dce_state == dcr_state == table_state == "present"
            else "denied"
            if "denied" in {dce_state, dcr_state, table_state}
            else "unknown"
            if "unknown" in {dce_state, dcr_state, table_state}
            or "unavailable" in {dce_state, dcr_state, table_state}
            else "unknown",
        },
        "tableSchemaCompatibility": {"status": "unknown"},
        "ingestionAuthorization": {
            "status": "not-yet-verifiable",
            "requiredAction": INGESTION_ACTION,
        },
        "resourceProvisioningAuthorization": {"status": "not-needed"},
        "tableCreationAuthorization": {
            "status": "not-needed",
            "requiredAction": TABLE_WRITE_ACTION,
        },
    }

    if table_state == "present":
        _, table_blockers, _, _ = _ingestion_modules()
        blockers = table_blockers(contract, table or {})
        result["tableSchemaCompatibility"] = {
            "status": "compatible" if not blockers else "blocked",
            "blockers": blockers,
        }
    elif table_state == "missing" and contract.destination.kind == "standard":
        result["tableSchemaCompatibility"] = {
            "status": "blocked",
            "blockers": [
                "Registered standard destination table is absent; the selected contract does not plan to create it."
            ],
        }

    if dce_state == dcr_state == "present":
        if table_state == "present" and result["tableSchemaCompatibility"]["status"] == "compatible":
            _, _, inspect_resources, _ = _ingestion_modules()
            compatibility = inspect_resources(
                contract,
                target["workspaceResourceId"],
                dce,
                dcr,
                dce_resource_id=dce_id,
                dcr_resource_id=dcr_id,
            )
            result["existingCandidateCompatibility"] = compatibility
            if compatibility["status"] == "compatible-existing":
                permissions = _check_action(token, dcr_id, INGESTION_ACTION)
                result["ingestionAuthorization"] = {
                    **permissions,
                    "status": permissions["status"],
                    "resource": "existing-compatible-dcr",
                    "note": (
                        "An effective-permissions snapshot is not proof that an upload "
                        "will be accepted."
                    ),
                }
            else:
                result["existingCandidateCompatibility"] = compatibility
        else:
            result["existingCandidateCompatibility"] = {
                "status": "blocked",
                "blockers": ["destination table is missing or schema-incompatible"],
            }
    elif dce_state == dcr_state == "missing":
        if table_state == "present" and result["tableSchemaCompatibility"]["status"] == "compatible":
            result["candidateState"] = "planned-missing-resources"
            result["resources"]["plannedScope"] = (
                f"/subscriptions/{target['subscriptionId']}/resourceGroups/"
                f"{workspace_identity(target['workspaceResourceId'])['resourceGroup']}"
            )
            result["ingestionAuthorization"] = {
                "status": "not-yet-verifiable",
                "requiredAction": INGESTION_ACTION,
                "note": "Effective ingestion authorization can be inspected only after DCR creation.",
            }
            scope = result["resources"]["plannedScope"]
            dcr_permission = _check_action(token, scope, DCR_WRITE_ACTION)
            dce_permission = _check_action(token, scope, DCE_WRITE_ACTION)
            result["resourceProvisioningAuthorization"] = {
                "status": "ready"
                if dcr_permission["status"] == dce_permission["status"] == "ready"
                else "denied"
                if "denied" in {dcr_permission["status"], dce_permission["status"]}
                else "unknown",
                "scope": scope,
                "dcrWrite": dcr_permission,
                "dceWrite": dce_permission,
            }
        else:
            result["candidateState"] = "blocked-destination"
            result["existingCandidateCompatibility"] = {
                "status": "blocked",
                "reason": "the destination table is missing or schema-incompatible",
            }
    elif "denied" in {dce_state, dcr_state}:
        result["candidateState"] = "inspection-denied"
        result["existingCandidateCompatibility"] = {
            "status": "unknown",
            "reason": "candidate resource read was denied; absence was not assumed",
        }
    elif "unavailable" in {dce_state, dcr_state, table_state} or "unknown" in {
        dce_state,
        dcr_state,
        table_state,
    }:
        result["candidateState"] = "inspection-unknown"
        result["existingCandidateCompatibility"] = {
            "status": "unknown",
            "reason": "candidate resource state could not be established",
        }
    elif dce_state != dcr_state:
        result["candidateState"] = "partial-resource-pair"
        result["existingCandidateCompatibility"] = {
            "status": "blocked",
            "reason": "only one contract-specific DCE/DCR resource exists",
        }

    # Native Standard tables, including CommonSecurityLog, are existing
    # destinations; this resolver does not plan their creation.
    if contract.destination.kind == "custom" and table_state == "missing":
        result["tableCreationAuthorization"] = _check_action(
            token,
            target["workspaceResourceId"],
            TABLE_WRITE_ACTION,
        )
    return result


def _aggregate_status(
    records: list[Mapping[str, Any]],
    blockers: list[Mapping[str, Any]],
    additional_statuses: tuple[str, ...] = (),
) -> str:
    statuses: list[str] = list(additional_statuses)
    for record in records:
        if record.get("status") in {"denied", "blocked", "unknown"}:
            statuses.append(str(record["status"]))
        for key in (
            "resourceReadAccess",
            "tableSchemaCompatibility",
            "ingestionAuthorization",
            "resourceProvisioningAuthorization",
            "tableCreationAuthorization",
        ):
            value = record.get(key)
            if isinstance(value, Mapping):
                statuses.append(str(value.get("status")))
    statuses.extend(str(item.get("status")) for item in blockers)
    if not statuses:
        return "not-applicable"
    if "denied" in statuses or "blocked" in statuses:
        return "action-required"
    if "unknown" in statuses or "not-yet-verifiable" in statuses:
        return "unknown"
    if all(status in {"ready", "compatible", "not-needed"} for status in statuses):
        return "ready"
    return "unknown"


def preflight_dcr_permissions(
    solution: str | Path,
    target: Mapping[str, str],
    *,
    auth_method: str | None,
) -> dict[str, Any]:
    """Inspect exact registered ingestion candidates without creating resources or sending data."""
    root = Path(solution).expanduser().resolve()
    locked_target = {
        key: str(target[key])
        for key in (
            "tenantId",
            "subscriptionId",
            "workspaceResourceId",
            "workspaceCustomerId",
        )
    }
    plan_error = None
    try:
        plan = _build_local_plan(root, locked_target)
        candidates, blockers = _contract_records(plan)
    except (OSError, ValueError, RuntimeError, TypeError, KeyError) as exc:
        plan = {
            "status": "unavailable",
            "inventory": {},
            "groups": [],
            "rules": [],
            "targetSha256": None,
        }
        candidates = []
        blockers = [
            {
                "status": "unknown",
                "reason": f"local ingestion contract planning failed: {exc}",
            }
        ]
        plan_error = type(exc).__name__
    target_fingerprint = _fingerprint(locked_target)
    report: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "status": "unknown",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "target": {**locked_target, "locked": True},
        "targetFingerprint": target_fingerprint,
        "plan": {
            "status": plan.get("status"),
            "inventorySha256": (plan.get("inventory") or {}).get("sha256"),
            "targetSha256": plan.get("targetSha256"),
            "writesPerformed": False,
            "cloudCallsPerformed": False,
        },
        "localReadiness": {
            "status": "ready" if candidates else "blocked" if blockers else "not-applicable",
            "candidateCount": len(candidates),
            "blockers": blockers,
            "errorType": plan_error,
            "reviewRequiredRules": [
                {
                    "ruleId": item.get("ruleId"),
                    "status": item.get("status"),
                    "blockers": item.get("blockers") or [],
                }
                for item in plan.get("rules") or []
                if isinstance(item, Mapping) and item.get("status") != "ready-for-fixture-review"
            ],
        },
        "authentication": {
            "selectedMethod": auth_method,
            "status": "not-attempted",
            "interactive": False,
        },
        "workspaceQueryPermission": {"status": "not-checked"},
        "contracts": [],
        "limitations": [
            "Only registered contract-specific resource candidates are inspected; arbitrary solution-listed DCR discovery is not implemented.",
            "A permission snapshot is diagnostic only and is not proof of an accepted upload, data visibility, or alert parity.",
            "Azure RBAC conditions or deny assignments not exposed by the permissions response may still affect an operation.",
        ],
        "writesPerformed": False,
        "payloadsSent": 0,
    }
    target_path = Path(str(target.get("targetPath") or ""))
    if not target_path.is_file():
        report["status"] = "blocked"
        report["targetVerification"] = {
            "status": "blocked",
            "reason": "the locked qualification-target.json artifact is missing",
            "cloudCallsPerformed": False,
        }
        report["authentication"]["status"] = "not-attempted"
        return report
    report["targetVerification"] = {
        "status": "pending",
        "source": "locked-qualification-target-artifact",
    }
    report_path = artifact_path(root, REPORT_NAME, create_parent=True)
    report["reportPath"] = str(report_path)

    if auth_method is None:
        report["targetVerification"]["status"] = "not-checked"
        report["authentication"].update(
            {
                "status": "action-required",
                "action": "Select the existing Azure CLI credential with --auth-method azure-cli; preflight never logs in.",
            }
        )
        report["contracts"] = [
            {
                "table": item["table"],
                "contractPath": item["contractPath"],
                "schemaFingerprint": item["schemaFingerprint"],
                "transformFingerprint": item["transformFingerprint"],
                "contractFingerprint": item["contractFingerprint"],
                "candidateProvenance": "registered-contract-resolver",
                "status": "not-checked",
            }
            for item in candidates
        ]
        report["status"] = (
            "action-required"
            if candidates
            else _aggregate_status([], blockers)
        )
        write_json_artifact(root, report_path, report)
        return report

    if auth_method != "azure-cli":
        report["targetVerification"]["status"] = "not-checked"
        report["authentication"].update(
            {
                "status": "unavailable",
                "reason": "The selected cached credential provider is not an Azure CLI ARM credential.",
            }
        )
        report["contracts"] = [
            {
                "table": item["table"],
                "contractPath": item["contractPath"],
                "schemaFingerprint": item["schemaFingerprint"],
                "transformFingerprint": item["transformFingerprint"],
                "contractFingerprint": item["contractFingerprint"],
                "candidateProvenance": "registered-contract-resolver",
                "status": "not-checked",
            }
            for item in candidates
        ]
        report["status"] = "unknown"
        write_json_artifact(root, report_path, report)
        return report

    try:
        customer_id = resolve_workspace_customer_id(
            locked_target["tenantId"], locked_target["workspaceResourceId"]
        )
    except Exception as exc:
        detail = _safe_message(exc)
        mismatch = "match" in detail.casefold()
        report["targetVerification"].update(
            {
                "status": "blocked" if mismatch else "unavailable",
                "reason": detail,
                "cloudCallsPerformed": True,
            }
        )
        report["authentication"].update(
            {
                "status": "unavailable",
                "errorType": type(exc).__name__,
                "reason": detail,
            }
        )
        report["status"] = "blocked" if mismatch else "unknown"
        report["contracts"] = []
        write_json_artifact(root, report_path, report)
        return report

    if customer_id.casefold() != locked_target["workspaceCustomerId"].casefold():
        report["targetVerification"].update(
            {
                "status": "blocked",
                "reason": "workspace customer ID does not match the locked Qualification target",
                "cloudCallsPerformed": True,
            }
        )
        report["authentication"]["status"] = "not-attempted"
        report["status"] = "blocked"
        write_json_artifact(root, report_path, report)
        return report

    report["targetVerification"].update(
        {
            "status": "confirmed",
            "cloudCallsPerformed": True,
        }
    )
    try:
        credential = azure_cli_credential(locked_target)
        token = credential.get_token(ARM_SCOPE).token
    except Exception as exc:
        report["authentication"].update(
            {
                "status": "unavailable",
                "errorType": type(exc).__name__,
                "reason": _safe_message(exc),
            }
        )
        report["status"] = "unknown"
        report["contracts"] = []
        write_json_artifact(root, report_path, report)
        return report

    report["authentication"]["status"] = "verified"
    report["workspaceQueryPermission"] = _check_query_permission(
        locked_target, credential
    )
    for candidate in candidates:
        try:
            report["contracts"].append(
                _check_candidate(locked_target, token, candidate)
            )
        except (OSError, urllib.error.URLError, TimeoutError, ValueError, TypeError) as exc:
            report["contracts"].append(
                {
                    "table": candidate["table"],
                    "contractPath": candidate["contractPath"],
                    "schemaFingerprint": candidate["schemaFingerprint"],
                    "transformFingerprint": candidate["transformFingerprint"],
                    "contractFingerprint": candidate["contractFingerprint"],
                    "candidateProvenance": "registered-contract-resolver",
                    "status": "unknown",
                    "errorType": type(exc).__name__,
                    "error": _safe_message(exc),
                }
            )
    if not candidates and not blockers:
        report["status"] = "not-applicable"
    else:
        query_status = str(report["workspaceQueryPermission"].get("status"))
        report["status"] = _aggregate_status(
            report["contracts"],
            blockers,
            additional_statuses=(query_status,),
        )
    write_json_artifact(root, report_path, report)
    return report
