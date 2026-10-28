from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

from solution_manager.core.artifacts import artifact_path, migrate_legacy_artifact, write_json_artifact
from solution_manager.migration.converter import validate_document, xdr_detection_files
from solution_manager.core.content_paths import detection_reference
from solution_manager.qualification.deployment import DEPLOYMENT_ENDPOINT, _deployment_token, _graph_request
from solution_manager.qualification.graph_client_config import azure_cli_credential
from solution_manager.core.onboarding import _state_dir
from solution_manager.core.target_context import require_locked_target

ARM_SCOPE = "https://management.azure.com/.default"
SENTINEL_ALERT_RULE_API_VERSION = "2024-03-01"
STATE_FILE_NAME = "alert-parity-state.json"
REPORT_FILE_NAME = "alert-parity-report.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _arm_token(state_dir: str | Path | None = None) -> str:
    return azure_cli_credential(
        state_root=_state_dir(state_dir)
    ).get_token(ARM_SCOPE).token


def _arm_request(
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


def _sentinel_rule_url(workspace_resource_id: str, rule_id: str) -> str:
    workspace = workspace_resource_id.rstrip("/")
    encoded_id = urllib.parse.quote(rule_id, safe="")
    return (
        "https://management.azure.com"
        f"{workspace}/providers/Microsoft.SecurityInsights/alertRules/{encoded_id}"
        f"?api-version={SENTINEL_ALERT_RULE_API_VERSION}"
    )


def _error_message(response: dict[str, Any]) -> str:
    error = response.get("error") if isinstance(response, dict) else None
    if isinstance(error, dict):
        return str(error.get("message") or error.get("code") or error)
    return str(error or response)


STREAMING_COMPILER_ERROR_CODES = (
    "HuntingRuleQueryStreamingNotSupported",
    "KqlCompilationFailed",
)

_STREAMING_COMPILER_PHRASES = (
    "huntingrulequerystreamingnotsupported",
    "kqlcompilationfailed",
    "streaming not supported",
    "not supported in streaming",
    "unsupported streaming",
    "streaming table",
    "streaming query",
    "dynamic literal",
    "dynamic literals",
    "runtime-only",
    "runtime only",
    "kql compilation",
    "query compilation failed",
    "compilation failed",
)


def classify_streaming_compiler_error(
    status_code: int,
    payload: Any,
    *,
    rule_id: str | None = None,
    detection: str | None = None,
) -> dict[str, Any] | None:
    if int(status_code) < 400:
        return None

    codes: list[str] = []
    messages: list[str] = []
    resolved_rule_id = rule_id
    resolved_detection = detection

    def _collect(node: Any) -> None:
        nonlocal resolved_rule_id, resolved_detection
        if isinstance(node, dict):
            if not resolved_rule_id and node.get("ruleId"):
                resolved_rule_id = str(node["ruleId"])
            if not resolved_detection and node.get("detection"):
                resolved_detection = str(node["detection"])
            code_val = node.get("code") or node.get("errorCode")
            if code_val:
                codes.append(str(code_val).strip())
            msg_val = node.get("message") or node.get("errorMessage")
            if msg_val:
                messages.append(str(msg_val).strip())
            for key in ("error", "innerError", "innererror", "details", "response"):
                if key in node:
                    _collect(node[key])
        elif isinstance(node, list):
            for item in node:
                _collect(item)
        elif isinstance(node, str) and node.strip():
            messages.append(node.strip())

    _collect(payload)
    combined_text = " | ".join(codes + messages)
    lower_text = combined_text.lower()
    lower_codes = {code.lower(): code for code in codes}

    matched_code: str | None = None
    for canonical in STREAMING_COMPILER_ERROR_CODES:
        if canonical.lower() in lower_codes or canonical.lower() in lower_text:
            matched_code = canonical
            break

    if matched_code is None:
        if any(phrase in lower_text for phrase in _STREAMING_COMPILER_PHRASES):
            non_generic = next(
                (
                    code
                    for code in codes
                    if code.lower() not in {"badrequest", "invalidargument", "unknown", "error"}
                ),
                None,
            )
            if non_generic:
                matched_code = non_generic
            elif "streaming" in lower_text:
                matched_code = "HuntingRuleQueryStreamingNotSupported"
            else:
                matched_code = "KqlCompilationFailed"

    if matched_code is None:
        return None

    message = (
        messages[0]
        if messages
        else (_error_message(payload) if isinstance(payload, dict) else str(payload))
    )
    diagnostic: dict[str, Any] = {
        "checkId": "E2E-Q02",
        "errorCode": matched_code,
        "statusCode": int(status_code),
        "message": message,
        "ruleId": str(resolved_rule_id or ""),
        "stage": "enablement",
        "streamingCompilerError": True,
    }
    if resolved_detection:
        diagnostic["detection"] = str(resolved_detection)
    return diagnostic


def _load_pairs(
    solution: str | Path, selected: list[str] | None = None
) -> tuple[Path, list[dict[str, Any]]]:
    root = Path(solution).expanduser().resolve()
    output = root / "XDR Detections"
    files = xdr_detection_files(output)
    available = [path.relative_to(output).as_posix() for path in files]
    from solution_manager.packaging.packaging_selection import current_applied_package_selection

    applied_selection = current_applied_package_selection(root)
    allowed = None
    if applied_selection is not None:
        allowed = {
            Path(str(value).replace("\\", "/")).relative_to("XDR Detections").as_posix()
            for value in (applied_selection["plan"].get("selection") or {}).get(
                "xdrDetections", []
            )
        }
        if not allowed:
            raise ValueError("current applied package selection contains no parity-ready detections")
    wanted = {detection_reference(name, available) for name in selected or []}
    if allowed is not None:
        if wanted and not wanted.issubset(allowed):
            raise ValueError("requested parity detections exceed the current applied package selection")
        if not wanted:
            wanted = allowed
    pairs: list[dict[str, Any]] = []
    for path in files:
        detection_name = path.relative_to(output).as_posix()
        if wanted and detection_name not in wanted:
            continue
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        errors = validate_document(document)
        conversion = (document.get("contentProvenance") or {}).get("conversion") or {}
        if conversion.get("status") != "converted" or conversion.get("reviewRequired"):
            errors.append("detection must be converted with no review required")
        if errors:
            raise ValueError(f"{detection_name}: {'; '.join(errors)}")
        source = (document.get("contentProvenance") or {}).get("source") or {}
        source_id = str(source.get("id") or "").strip()
        detection_id = str((document.get("properties") or {}).get("id") or "").strip()
        if not source_id or not detection_id:
            raise ValueError(f"{detection_name}: source and detection IDs are required")
        alert = (
            ((document.get("properties") or {}).get("detectionAction") or {}).get(
                "alertTemplate"
            )
            or {}
        )
        pairs.append(
            {
                "detection": detection_name,
                "displayName": str(
                    (document.get("properties") or {}).get("displayName") or path.stem
                ),
                "analyticRuleId": source_id,
                "customDetectionId": detection_id,
                "entityMappings": alert.get("entityMappings") or {},
            }
        )
    if not pairs:
        raise ValueError(f"no converted detections selected under {output}")
    return root, pairs


def _qualification_scope(
    root: Path,
    pairs: list[dict[str, Any]],
    applied_selection: dict[str, Any] | None,
) -> dict[str, Any]:
    plan = applied_selection.get("plan") if isinstance(applied_selection, dict) else None
    plan = plan if isinstance(plan, dict) else {}
    selection = plan.get("selection") if isinstance(plan.get("selection"), dict) else {}
    planned_paths = sorted(
        Path(str(value).replace("\\", "/")).relative_to("XDR Detections").as_posix()
        for value in selection.get("xdrDetections", [])
    )
    selected_paths = sorted(str(pair["detection"]).replace("\\", "/") for pair in pairs)
    detections = []
    for pair in pairs:
        path = root / "XDR Detections" / str(pair["detection"])
        try:
            content = path.read_bytes()
        except OSError:
            content = json.dumps(
                pair, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        digest = hashlib.sha256(content).hexdigest()
        detections.append({
            "path": str(pair["detection"]).replace("\\", "/"),
            "sourceId": str(pair.get("analyticRuleId") or "").casefold(),
            "detectionId": str(pair.get("customDetectionId") or "").casefold(),
            "fileSha256": digest,
        })
    detections.sort(key=lambda item: item["path"].casefold())
    summary = plan.get("summary") if isinstance(plan.get("summary"), dict) else {}
    return {
        "kind": "applied-package-selection" if plan else "current-detection-content",
        "planSha256": plan.get("planSha256"),
        "selectedDetectionPaths": selected_paths,
        "selectedSourceIds": sorted({item["sourceId"] for item in detections}),
        "detectionContentSha256": hashlib.sha256(
            json.dumps(detections, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "selectionComplete": bool(plan) and selected_paths == planned_paths,
        "coverage": summary or None,
    }


def _verify_qualification_scope(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    stored = state.get("qualificationScope")
    if not isinstance(stored, dict):
        raise ValueError("alert parity state has no exact qualification-scope binding")
    pairs = state.get("rules")
    if not isinstance(pairs, list) or not pairs:
        raise ValueError("alert parity state has no tested detection identities")
    from solution_manager.packaging.packaging_selection import current_applied_package_selection

    applied = current_applied_package_selection(root)
    current = _qualification_scope(root, pairs, applied)
    if stored != current:
        raise ValueError("alert parity qualification scope no longer matches the current selection and detection content")
    return current


def _contains_marker(value: Any, marker: str) -> bool:
    if isinstance(value, dict):
        return any(_contains_marker(item, marker) for item in value.values())
    if isinstance(value, list):
        return any(_contains_marker(item, marker) for item in value)
    return marker in str(value)


def _validate_marked_payload(payload_path: str | Path, marker: str) -> None:
    payload = json.loads(Path(payload_path).expanduser().read_text(encoding="utf-8-sig"))
    if not _contains_marker(payload, marker):
        raise ValueError(
            f"scenario marker {marker!r} does not occur in the ingestion payload"
        )


def _is_graph_detection_disabled(graph: Any) -> tuple[bool, bool]:
    if not isinstance(graph, dict):
        return False, False
    is_enabled_val = graph.get("isEnabled") if "isEnabled" in graph else None
    status_val = str(graph.get("status") or "").strip().lower()
    is_enabled = (is_enabled_val is True) or (status_val == "enabled")
    if is_enabled:
        return True, False
    is_disabled = (is_enabled_val is False) or (status_val == "disabled")
    if "isEnabled" not in graph and not status_val:
        is_disabled = True
    return False, is_disabled


def _read_rule_states(
    pairs: list[dict[str, Any]],
    workspace_resource_id: str,
    arm_token: str,
    graph_token: str,
) -> list[dict[str, Any]]:
    states: list[dict[str, Any]] = []
    for pair in pairs:
        sentinel_status, sentinel = _arm_request(
            "GET",
            _sentinel_rule_url(workspace_resource_id, pair["analyticRuleId"]),
            arm_token,
        )
        if sentinel_status != 200:
            raise RuntimeError(
                f"{pair['detection']}: cannot read Sentinel analytic rule: "
                f"{_error_message(sentinel)}"
            )
        graph_id = urllib.parse.quote(pair["customDetectionId"], safe="")
        graph_status, graph = _graph_request(
            "GET", f"{DEPLOYMENT_ENDPOINT}/{graph_id}", graph_token
        )
        if graph_status != 200:
            raise RuntimeError(
                f"{pair['detection']}: cannot read Custom Detection: "
                f"{_error_message(graph)}"
            )
        sentinel_enabled = bool((sentinel.get("properties") or {}).get("enabled"))
        graph_enabled, graph_disabled = _is_graph_detection_disabled(graph)
        if sentinel_enabled or graph_enabled or not graph_disabled:
            raise RuntimeError(
                f"{pair['detection']}: parity validation requires both rules to "
                "be disabled before start"
            )
        pair["sentinelResource"] = sentinel
        pair["initialDisabled"] = True
        states.append(
            {
                "detection": pair["detection"],
                "analyticRuleId": pair["analyticRuleId"],
                "customDetectionId": pair["customDetectionId"],
                "sentinelEnabled": False,
                "xdrEnabled": False,
                "initialDisabled": True,
            }
        )
    return states


def _set_pair_enabled(
    pair: dict[str, Any],
    workspace_resource_id: str,
    arm_token: str,
    graph_token: str,
    enabled: bool,
) -> list[str]:
    errors: list[str] = []
    sentinel = dict(pair.get("sentinelResource") or {})
    source_properties = dict(sentinel.get("properties") or {})
    writable_properties = {
        "displayName",
        "description",
        "severity",
        "query",
        "queryFrequency",
        "queryPeriod",
        "triggerOperator",
        "triggerThreshold",
        "suppressionDuration",
        "suppressionEnabled",
        "tactics",
        "techniques",
        "subTechniques",
        "entityMappings",
        "eventGroupingSettings",
        "alertDetailsOverride",
        "customDetails",
        "incidentConfiguration",
        "alertRuleTemplateName",
        "templateVersion",
    }
    sentinel_properties = {
        key: value
        for key, value in source_properties.items()
        if key in writable_properties
    }
    sentinel_properties["enabled"] = enabled
    sentinel_body = {
        "kind": sentinel.get("kind"),
        "properties": sentinel_properties,
    }
    status, response = _arm_request(
        "PUT",
        _sentinel_rule_url(workspace_resource_id, pair["analyticRuleId"]),
        arm_token,
        sentinel_body,
    )
    if status not in {200, 201}:
        errors.append(f"Sentinel: {_error_message(response)}")

    graph_id = urllib.parse.quote(pair["customDetectionId"], safe="")
    status, response = _graph_request(
        "PATCH",
        f"{DEPLOYMENT_ENDPOINT}/{graph_id}",
        graph_token,
        {
            "isEnabled": enabled,
            "status": "enabled" if enabled else "disabled",
        },
    )
    if status != 200:
        compiler_diag = (
            classify_streaming_compiler_error(
                status,
                response,
                rule_id=str(pair.get("customDetectionId") or ""),
                detection=str(pair.get("detection") or ""),
            )
            if enabled
            else None
        )
        if compiler_diag is not None:
            pair.setdefault("e2eQ02Diagnostics", []).append(compiler_diag)
            errors.append(
                f"Custom Detection (E2E-Q02 {compiler_diag['errorCode']}): "
                f"{compiler_diag['message']}"
            )
        else:
            errors.append(f"Custom Detection: {_error_message(response)}")
    return errors


def _disable_all(
    state: dict[str, Any],
    *,
    arm_token: str | None = None,
    graph_token: str | None = None,
    state_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    arm = arm_token or _arm_token(state_dir)
    target = state.get("target") or {}
    graph = graph_token or _deployment_token(
        state_dir,
        tenant_id=target.get("tenantId"),
    )
    workspace_resource_id = (
        state.get("workspaceResourceId")
        or target.get("workspaceResourceId")
        or ""
    )
    rules = list(state.get("rules") or [])
    results: list[dict[str, Any]] = []
    readback_candidates: list[dict[str, Any]] = []
    receipt_by_detection: dict[str, dict[str, Any]] = {}
    for pair in rules:
        errors = list(
            _set_pair_enabled(
                pair, workspace_resource_id, arm, graph, False
            )
        )
        can_readback = bool(
            not errors
            and pair.get("analyticRuleId")
            and pair.get("customDetectionId")
        )
        receipt = {
            "detection": pair["detection"],
            "initialDisabled": bool(pair.get("initialDisabled", True)),
            "disabled": not errors,
            "returnedToDisabled": not errors,
            "errors": errors,
        }
        results.append(receipt)
        receipt_by_detection[pair["detection"]] = receipt
        if can_readback:
            readback_candidates.append(pair)

    if readback_candidates:
        try:
            _read_rule_states(readback_candidates, workspace_resource_id, arm, graph)
        except Exception as exc:
            exc_msg = str(exc)
            matched_any = False
            for pair in readback_candidates:
                det = pair["detection"]
                if det in exc_msg or len(readback_candidates) == 1:
                    matched_any = True
                    receipt = receipt_by_detection[det]
                    receipt["errors"].append(f"Readback: {exc_msg}")
                    receipt["disabled"] = False
                    receipt["returnedToDisabled"] = False
            if not matched_any:
                for pair in readback_candidates:
                    receipt = receipt_by_detection[pair["detection"]]
                    receipt["errors"].append(f"Readback: {exc_msg}")
                    receipt["disabled"] = False
                    receipt["returnedToDisabled"] = False

    for pair in rules:
        pair["returnedToDisabled"] = bool(
            receipt_by_detection[pair["detection"]]["returnedToDisabled"]
        )

    initial_disabled = bool(rules) and all(
        bool(pair.get("initialDisabled", True)) for pair in rules
    )
    returned_to_disabled = bool(results) and all(
        bool(item.get("returnedToDisabled")) for item in results
    )
    tk_q11_passed = bool(initial_disabled and returned_to_disabled)
    lifecycle = dict(state.get("alertLifecycle") or {})
    lifecycle["initialDisabled"] = initial_disabled
    lifecycle["returnedToDisabled"] = returned_to_disabled
    lifecycle["tkQ11Passed"] = tk_q11_passed
    lifecycle["tkQ11Verified"] = tk_q11_passed
    if state.get("e2eQ02Diagnostics") and "e2eQ02Diagnostics" not in lifecycle:
        lifecycle["e2eQ02Diagnostics"] = list(state["e2eQ02Diagnostics"])
    state["alertLifecycle"] = lifecycle
    state["tkQ11Passed"] = tk_q11_passed
    return results


def _ingest(contract: str | Path, payload: str | Path) -> dict[str, Any]:
    executable = shutil.which("azure-monitor-logs-ingestion")
    environment = None
    if executable:
        command = [
            executable,
            "ingest",
            "--contract",
            str(Path(contract).expanduser()),
            "--payload",
            str(Path(payload).expanduser()),
        ]
    else:
        ingestion_tool = Path(__file__).resolve().parents[3] / "AzureMonitorLogsIngestion"
        environment = os.environ.copy()
        current_path = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = (
            f"{ingestion_tool}{os.pathsep}{current_path}"
            if current_path
            else str(ingestion_tool)
        )
        command = [
            sys.executable,
            "-m",
            "azure_monitor_logs_ingestion.cli",
            "ingest",
            "--contract",
            str(Path(contract).expanduser()),
            "--payload",
            str(Path(payload).expanduser()),
        ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout or "unknown error").strip()
        raise RuntimeError(f"mock ingestion failed: {detail}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"status": "accepted", "output": completed.stdout.strip()}


def _capture_queries(pair: dict[str, Any], started_at: str, marker: str) -> dict[str, str]:
    title = pair["displayName"].replace('"', '\\"')
    marker_text = marker.replace('"', '\\"')
    return {
        "sentinel": (
            "SecurityAlert\n"
            f'| where TimeGenerated >= datetime({started_at})\n'
            f'| where AlertName == "{title}"\n'
            '| where ProductName == "Azure Sentinel" '
            'and ProviderName == "ASI Scheduled Alerts"\n'
            f'| where tostring(Entities) has "{marker_text}" '
            f'or tostring(ExtendedProperties) has "{marker_text}"\n'
            "| summarize arg_max(TimeGenerated, *) by SystemAlertId\n"
            "| project SystemAlertId, AlertName, AlertSeverity, Tactics, "
            "Entities, ExtendedProperties, TimeGenerated"
        ),
        "customDetection": (
            "let MatchingAlerts = AlertInfo\n"
            f"| where Timestamp >= datetime({started_at})\n"
            f'| where Title == "{title}"\n'
            '| where ServiceSource == "Microsoft Defender XDR" '
            'and DetectionSource == "Custom detection"\n'
            "| project AlertId, AlertTitle=Title, AlertSeverity=Severity, "
            "Category, AttackTechniques, AlertTimestamp=Timestamp;\n"
            "MatchingAlerts\n"
            "| join kind=leftouter (\n"
            "    AlertEvidence\n"
            "    | project AlertId, EvidenceRole, EntityType, DeviceId, DeviceName, "
            "AccountUpn, AccountSid, RemoteIP, LocalIP, FileName, FolderPath, "
            "SHA256, RemoteUrl, EvidenceTimestamp=Timestamp\n"
            ") on AlertId\n"
            f'| where tostring(pack_all()) has "{marker_text}"\n'
            "| project AlertId, Title=AlertTitle, Severity=AlertSeverity, "
            "Category, AttackTechniques, "
            "EvidenceRole, EntityType, DeviceId, DeviceName, AccountUpn, "
            "AccountSid, RemoteIP, LocalIP, FileName, FolderPath, SHA256, "
            "URL=RemoteUrl, Timestamp=AlertTimestamp"
        ),
    }


def start_alert_parity(
    solution: str | Path,
    *,
    workspace_resource_id: str | None = None,
    contract: str | Path,
    payload: str | Path,
    scenario_marker: str,
    expected_match_keys: list[str] | None = None,
    detections: list[str] | None = None,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    target = require_locked_target(
        solution,
        workspace_resource_id=workspace_resource_id,
    )
    workspace_resource_id = target["workspaceResourceId"]
    marker = scenario_marker.strip()
    if not marker:
        raise ValueError("scenario-marker is required")
    _validate_marked_payload(payload, marker)
    expected_keys = sorted(
        {str(value).strip() for value in (expected_match_keys or [marker]) if str(value).strip()}
    )
    if not expected_keys:
        raise ValueError("at least one expected match key is required")
    root, pairs = _load_pairs(solution, detections)
    from solution_manager.packaging.packaging_selection import current_applied_package_selection

    applied_selection = current_applied_package_selection(root)
    qualification_scope = _qualification_scope(root, pairs, applied_selection)
    state_path = migrate_legacy_artifact(root, STATE_FILE_NAME)
    if state_path.exists():
        existing = json.loads(state_path.read_text(encoding="utf-8"))
        if existing.get("status") == "awaiting-alerts":
            raise RuntimeError(
                "an alert parity run is already active; complete or abort it first"
            )

    arm_token = _arm_token(state_dir)
    graph_token = _deployment_token(state_dir, tenant_id=target["tenantId"])
    _read_rule_states(pairs, workspace_resource_id, arm_token, graph_token)
    for pair in pairs:
        pair.setdefault("initialDisabled", True)
    initial_disabled = bool(pairs) and all(
        bool(pair.get("initialDisabled", True)) for pair in pairs
    )
    started_at = _utc_now()
    state = {
        "runId": str(uuid.uuid4()),
        "status": "enabling",
        "startedAt": started_at,
        "solution": str(root),
        "workspaceResourceId": workspace_resource_id.rstrip("/"),
        "target": target,
        "scenarioMarker": marker,
        "expectedMatchKeys": expected_keys,
        "qualificationScope": qualification_scope,
        "contract": str(Path(contract).expanduser().resolve()),
        "payload": str(Path(payload).expanduser().resolve()),
        "initialDisabled": initial_disabled,
        "alertLifecycle": {
            "initialDisabled": initial_disabled,
            "returnedToDisabled": None,
            "tkQ11Passed": None,
            "tkQ11Verified": None,
            "e2eQ02Diagnostics": [],
        },
        "e2eQ02Diagnostics": [],
        "rules": pairs,
    }
    write_json_artifact(root, state_path, state)

    enabled: list[dict[str, Any]] = []
    need_rollback = True
    try:
        for pair in pairs:
            errors = _set_pair_enabled(
                pair, workspace_resource_id, arm_token, graph_token, True
            )
            enabled.append({"detection": pair["detection"], "errors": errors})
            if pair.get("e2eQ02Diagnostics"):
                state["e2eQ02Diagnostics"].extend(pair["e2eQ02Diagnostics"])
                state["alertLifecycle"]["e2eQ02Diagnostics"] = list(
                    state["e2eQ02Diagnostics"]
                )
            if errors:
                raise RuntimeError(
                    f"{pair['detection']}: failed to enable parity rules: "
                    f"{'; '.join(errors)}"
                )
        ingestion = _ingest(contract, payload)
        state["status"] = "awaiting-alerts"
        state["enabledAt"] = _utc_now()
        state["ingestion"] = ingestion
        state["capturePlan"] = [
            {
                "detection": pair["detection"],
                "displayName": pair["displayName"],
                "queries": _capture_queries(pair, started_at, marker),
                "entityMappings": pair["entityMappings"],
            }
            for pair in pairs
        ]
        write_json_artifact(root, state_path, state)
        need_rollback = False
        return {
            "status": state["status"],
            "runId": state["runId"],
            "statePath": str(state_path),
            "rulesEnabled": len(pairs),
            "initialDisabled": initial_disabled,
            "alertLifecycle": state["alertLifecycle"],
            "ingestion": ingestion,
            "capturePlan": state["capturePlan"],
            "nextCommand": (
                "sentinel-xdr-migration complete-alert-parity "
                f'--solution "{root}" --run-id "{state_path.parent.name}" --results "<normalized-results.json>"'
            ),
        }
    except Exception:
        state["status"] = "failed"
        raise
    finally:
        if need_rollback:
            state["status"] = "failed"
            raw_cleanup = _disable_all(
                state,
                arm_token=arm_token,
                graph_token=graph_token,
                state_dir=state_dir,
            )
            cleanup, _, _ = _normalize_cleanup_and_lifecycle(state, raw_cleanup)
            state["cleanup"] = cleanup
            write_json_artifact(root, state_path, state)


def _normalize_cleanup_and_lifecycle(
    state: dict[str, Any],
    cleanup: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any], bool]:
    rules = list(state.get("rules") or [])
    initial_disabled = bool(
        (state.get("alertLifecycle") or {}).get(
            "initialDisabled",
            bool(rules) and all(bool(pair.get("initialDisabled", True)) for pair in rules),
        )
    )
    for item in cleanup:
        if "initialDisabled" not in item:
            item["initialDisabled"] = initial_disabled
        if "returnedToDisabled" not in item:
            item["returnedToDisabled"] = bool(item.get("disabled"))
    returned_to_disabled = bool(cleanup) and all(
        bool(item.get("disabled")) and bool(item.get("returnedToDisabled"))
        for item in cleanup
    )
    tk_q11_passed = bool(initial_disabled and returned_to_disabled)
    lifecycle = dict(state.get("alertLifecycle") or {})
    lifecycle["initialDisabled"] = initial_disabled
    lifecycle["returnedToDisabled"] = returned_to_disabled
    lifecycle["tkQ11Passed"] = tk_q11_passed
    lifecycle["tkQ11Verified"] = tk_q11_passed
    if state.get("e2eQ02Diagnostics") is not None:
        lifecycle["e2eQ02Diagnostics"] = list(state.get("e2eQ02Diagnostics") or [])
    else:
        lifecycle.setdefault("e2eQ02Diagnostics", [])
    state["alertLifecycle"] = lifecycle
    state["tkQ11Passed"] = tk_q11_passed
    state["initialDisabled"] = initial_disabled
    state["returnedToDisabled"] = returned_to_disabled
    return cleanup, lifecycle, tk_q11_passed


def start_alert_parity_batch(
    solution: str | Path,
    *,
    workspace_resource_id: str | None = None,
    plan_path: str | Path,
    state_dir: str | Path | None = None,
    raise_on_compiler_error: bool = False,
) -> dict[str, Any]:
    target = require_locked_target(
        solution,
        workspace_resource_id=workspace_resource_id,
    )
    workspace_resource_id = target["workspaceResourceId"]
    plan_file = Path(plan_path).expanduser().resolve()
    plan = json.loads(plan_file.read_text(encoding="utf-8-sig"))
    fixtures = plan.get("fixtures") if isinstance(plan, dict) else None
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("batch parity plan must contain a non-empty fixtures list")

    root, pairs = _load_pairs(solution)
    from solution_manager.packaging.packaging_selection import current_applied_package_selection

    applied_selection = current_applied_package_selection(root)
    qualification_scope = _qualification_scope(root, pairs, applied_selection)
    pairs_by_name = {pair["detection"]: pair for pair in pairs}
    fixture_by_detection: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise ValueError("each batch parity fixture must be an object")
        requested = str(fixture.get("detection") or "").strip()
        pair = pairs_by_name[detection_reference(requested, list(pairs_by_name))]
        detection = pair["detection"]
        if detection in fixture_by_detection:
            raise ValueError(f"duplicate batch parity fixture: {detection}")
        marker = str(fixture.get("scenarioMarker") or "").strip()
        if not marker:
            raise ValueError(f"{detection}: scenarioMarker is required")
        expected_keys = sorted(
            {
                str(value).strip()
                for value in (fixture.get("expectedMatchKeys") or [marker])
                if str(value).strip()
            }
        )
        if not expected_keys:
            raise ValueError(f"{detection}: at least one expected match key is required")
        contract = (plan_file.parent / str(fixture.get("contract") or "")).resolve()
        payload = (plan_file.parent / str(fixture.get("payload") or "")).resolve()
        if not contract.is_file():
            raise ValueError(f"{detection}: ingestion contract does not exist: {contract}")
        if not payload.is_file():
            raise ValueError(f"{detection}: ingestion payload does not exist: {payload}")
        _validate_marked_payload(payload, marker)
        fixture_by_detection[detection] = {
            "detection": detection,
            "contract": str(contract),
            "payload": str(payload),
            "scenarioMarker": marker,
            "expectedMatchKeys": expected_keys,
        }

    missing = sorted(set(pairs_by_name) - set(fixture_by_detection))
    if missing:
        raise ValueError(
            "batch parity plan must include every converted detection; missing: "
            + ", ".join(missing)
        )

    state_path = migrate_legacy_artifact(root, STATE_FILE_NAME)
    if state_path.exists():
        existing = json.loads(state_path.read_text(encoding="utf-8"))
        if existing.get("status") == "awaiting-alerts":
            raise RuntimeError(
                "an alert parity run is already active; complete or abort it first"
            )

    arm_token = _arm_token(state_dir)
    graph_token = _deployment_token(state_dir, tenant_id=target["tenantId"])
    _read_rule_states(pairs, workspace_resource_id, arm_token, graph_token)
    for pair in pairs:
        pair.setdefault("initialDisabled", True)
    initial_disabled = bool(pairs) and all(
        bool(pair.get("initialDisabled", True)) for pair in pairs
    )
    started_at = _utc_now()
    state = {
        "runId": str(uuid.uuid4()),
        "status": "enabling",
        "mode": "batch",
        "startedAt": started_at,
        "solution": str(root),
        "workspaceResourceId": workspace_resource_id.rstrip("/"),
        "target": target,
        "plan": str(plan_file),
        "fixtures": list(fixture_by_detection.values()),
        "expectedMatchKeysByDetection": {
            detection: fixture["expectedMatchKeys"]
            for detection, fixture in fixture_by_detection.items()
        },
        "qualificationScope": qualification_scope,
        "initialDisabled": initial_disabled,
        "alertLifecycle": {
            "initialDisabled": initial_disabled,
            "returnedToDisabled": None,
            "tkQ11Passed": None,
            "tkQ11Verified": None,
            "e2eQ02Diagnostics": [],
        },
        "e2eQ02Diagnostics": [],
        "rules": pairs,
    }
    write_json_artifact(root, state_path, state)

    batch_result: dict[str, Any] = {}
    need_rollback = True
    enabled_count = 0
    try:
        ingestions = []
        for pair in pairs:
            fixture = fixture_by_detection[pair["detection"]]
            ingestions.append(
                {
                    "detection": pair["detection"],
                    "result": _ingest(fixture["contract"], fixture["payload"]),
                }
            )
        state["ingestions"] = ingestions

        for pair in pairs:
            errors = _set_pair_enabled(
                pair, workspace_resource_id, arm_token, graph_token, True
            )
            if errors:
                pair_diags = list(pair.get("e2eQ02Diagnostics") or [])
                if pair_diags:
                    state["e2eQ02Diagnostics"].extend(pair_diags)
                    state["alertLifecycle"]["e2eQ02Diagnostics"] = list(
                        state["e2eQ02Diagnostics"]
                    )
                    state["status"] = "failed"
                    state["error"] = (
                        f"{pair['detection']}: failed to enable parity rules: "
                        f"{'; '.join(errors)}"
                    )
                    if raise_on_compiler_error:
                        raise RuntimeError(state["error"])
                    batch_result.update(
                        {
                            "status": "failed",
                            "runId": state["runId"],
                            "statePath": str(state_path),
                            "rulesEnabled": enabled_count,
                            "fixturesIngested": len(ingestions),
                            "ingestions": ingestions,
                            "initialDisabled": initial_disabled,
                            "e2eQ02Diagnostics": list(state["e2eQ02Diagnostics"]),
                            "error": state["error"],
                        }
                    )
                    return batch_result
                raise RuntimeError(
                    f"{pair['detection']}: failed to enable parity rules: "
                    f"{'; '.join(errors)}"
                )
            enabled_count += 1

        state["status"] = "awaiting-alerts"
        state["enabledAt"] = _utc_now()
        state["capturePlan"] = [
            {
                "detection": pair["detection"],
                "displayName": pair["displayName"],
                "queries": _capture_queries(
                    pair,
                    started_at,
                    fixture_by_detection[pair["detection"]]["scenarioMarker"],
                ),
                "scenarioMarker": fixture_by_detection[pair["detection"]][
                    "scenarioMarker"
                ],
                "expectedMatchKeys": fixture_by_detection[pair["detection"]][
                    "expectedMatchKeys"
                ],
                "entityMappings": pair["entityMappings"],
            }
            for pair in pairs
        ]
        write_json_artifact(root, state_path, state)
        need_rollback = False
        return {
            "status": state["status"],
            "runId": state["runId"],
            "statePath": str(state_path),
            "rulesEnabled": len(pairs),
            "fixturesIngested": len(ingestions),
            "ingestions": ingestions,
            "initialDisabled": initial_disabled,
            "alertLifecycle": state["alertLifecycle"],
            "e2eQ02Diagnostics": list(state.get("e2eQ02Diagnostics") or []),
            "capturePlan": state["capturePlan"],
            "nextCommand": (
                "sentinel-xdr-migration complete-alert-parity "
                f'--solution "{root}" --run-id "{state_path.parent.name}" --results "<normalized-results.json>"'
            ),
        }
    except Exception:
        state["status"] = "failed"
        raise
    finally:
        if need_rollback:
            state["status"] = "failed"
            raw_cleanup = _disable_all(
                state,
                arm_token=arm_token,
                graph_token=graph_token,
                state_dir=state_dir,
            )
            cleanup, lifecycle, tk_q11_passed = _normalize_cleanup_and_lifecycle(
                state, raw_cleanup
            )
            state["cleanup"] = cleanup
            write_json_artifact(root, state_path, state)
            if batch_result:
                batch_result["cleanup"] = cleanup
                batch_result["returnedToDisabled"] = lifecycle["returnedToDisabled"]
                batch_result["tkQ11Passed"] = tk_q11_passed
                batch_result["alertLifecycle"] = lifecycle


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _normalize_alert(alert: dict[str, Any]) -> dict[str, Any]:
    required = {"matchKey", "severity", "tactics", "entities", "evidence"}
    missing = sorted(required - set(alert))
    if missing:
        raise ValueError(f"normalized alert is missing: {', '.join(missing)}")
    return {
        "matchKey": str(alert["matchKey"]),
        "severity": str(alert["severity"]).lower(),
        "tactics": sorted(str(item) for item in alert["tactics"]),
        "entities": alert["entities"],
        "evidence": alert["evidence"],
    }


def compare_alert_captures(
    expected_detections: set[str],
    raw_results: Any,
    *,
    expected_match_keys: set[str] | None = None,
    expected_match_keys_by_detection: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    entries = raw_results.get("results") if isinstance(raw_results, dict) else raw_results
    if not isinstance(entries, list):
        raise ValueError("alert parity results must contain a results list")
    names: set[str] = set()
    comparisons: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each alert parity result must be an object")
        detection = str(entry.get("detection") or "")
        if not detection or detection in names:
            raise ValueError("each detection must occur exactly once")
        names.add(detection)
        sides: dict[str, list[dict[str, Any]]] = {}
        for side in ("analyticRule", "customDetection"):
            value = entry.get(side) or {}
            alerts = value.get("alerts") if isinstance(value, dict) else None
            if not isinstance(alerts, list):
                raise ValueError(f"{detection}: {side}.alerts must be a list")
            normalized = [_normalize_alert(alert) for alert in alerts]
            keys = [alert["matchKey"] for alert in normalized]
            if len(keys) != len(set(keys)):
                raise ValueError(f"{detection}: duplicate {side} matchKey")
            sides[side] = sorted(normalized, key=lambda item: item["matchKey"])

        analytic = sides["analyticRule"]
        custom = sides["customDetection"]
        analytic_by_key = {item["matchKey"]: item for item in analytic}
        custom_by_key = {item["matchKey"]: item for item in custom}
        detection_expected_keys = (
            (expected_match_keys_by_detection or {}).get(detection)
            or expected_match_keys
        )
        dimensions = {
            "alertCount": len(analytic) == len(custom),
            "matchKeys": set(analytic_by_key) == set(custom_by_key),
            "expectedMatches": (
                detection_expected_keys is None
                or (
                    set(analytic_by_key) == detection_expected_keys
                    and set(custom_by_key) == detection_expected_keys
                )
            ),
            "severity": all(
                analytic_by_key[key]["severity"] == custom_by_key[key]["severity"]
                for key in set(analytic_by_key) & set(custom_by_key)
            ),
            "tactics": all(
                analytic_by_key[key]["tactics"] == custom_by_key[key]["tactics"]
                for key in set(analytic_by_key) & set(custom_by_key)
            ),
            "entities": all(
                _canonical(analytic_by_key[key]["entities"])
                == _canonical(custom_by_key[key]["entities"])
                for key in set(analytic_by_key) & set(custom_by_key)
            ),
            "evidence": all(
                _canonical(analytic_by_key[key]["evidence"])
                == _canonical(custom_by_key[key]["evidence"])
                for key in set(analytic_by_key) & set(custom_by_key)
            ),
        }
        comparisons.append(
            {
                "detection": detection,
                "passed": all(dimensions.values()),
                "analyticRuleAlertCount": len(analytic),
                "customDetectionAlertCount": len(custom),
                "dimensions": dimensions,
                "analyticRuleOnlyMatchKeys": sorted(
                    set(analytic_by_key) - set(custom_by_key)
                ),
                "customDetectionOnlyMatchKeys": sorted(
                    set(custom_by_key) - set(analytic_by_key)
                ),
            }
        )
    missing = sorted(expected_detections - names)
    unknown = sorted(names - expected_detections)
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing detections: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown detections: {', '.join(unknown)}")
        raise ValueError("; ".join(details))
    return comparisons


def complete_alert_parity(
    solution: str | Path,
    *,
    results_path: str | Path,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    state_path = migrate_legacy_artifact(root, STATE_FILE_NAME)
    if not state_path.exists():
        raise ValueError("no alert parity state exists for this solution")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("status") != "awaiting-alerts":
        raise ValueError(f"alert parity run is not active: {state.get('status')}")
    target = require_locked_target(root)
    if (state.get("target") or {}).get("workspaceResourceId", "").lower() != target[
        "workspaceResourceId"
    ].lower():
        raise ValueError("alert parity state does not match the locked target")

    comparison_error: str | None = None
    scope_error: str | None = None
    verified_scope: dict[str, Any] | None = None
    comparisons: list[dict[str, Any]] = []
    cleanup: list[dict[str, Any]] = []
    try:
        verified_scope = _verify_qualification_scope(root, state)
        raw = json.loads(
            Path(results_path).expanduser().read_text(encoding="utf-8-sig")
        )
        expected = {pair["detection"] for pair in state["rules"]}
        comparisons = compare_alert_captures(
            expected,
            raw,
            expected_match_keys=set(state.get("expectedMatchKeys") or []),
            expected_match_keys_by_detection={
                detection: set(keys)
                for detection, keys in (
                    state.get("expectedMatchKeysByDetection") or {}
                ).items()
            },
        )
    except Exception as exc:
        if verified_scope is None:
            scope_error = str(exc)
        else:
            comparison_error = str(exc)
    finally:
        raw_cleanup = _disable_all(state, state_dir=state_dir)
        cleanup, lifecycle, tk_q11_passed = _normalize_cleanup_and_lifecycle(
            state, raw_cleanup
        )

    cleanup_ok = all(item["disabled"] for item in cleanup)
    passed = (
        comparison_error is None
        and scope_error is None
        and bool(comparisons)
        and all(item["passed"] for item in comparisons)
        and cleanup_ok
    )
    report = {
        "runId": state["runId"],
        "status": "passed" if passed else "failed",
        "completedAt": _utc_now(),
        "solution": str(root),
        "scenarioMarker": state.get("scenarioMarker"),
        "fixtures": state.get("fixtures") or [],
        "strictParity": True,
        "comparisonError": comparison_error,
        "scopeVerificationError": scope_error,
        "qualificationScopeVerified": verified_scope is not None and scope_error is None,
        "selectionPlanSha256": (
            verified_scope.get("planSha256") if verified_scope else None
        ),
        "testedDetectionPaths": (
            verified_scope.get("selectedDetectionPaths") if verified_scope else []
        ),
        "testedSourceIds": (
            verified_scope.get("selectedSourceIds") if verified_scope else []
        ),
        "comparisons": comparisons,
        "qualificationScope": verified_scope or state.get("qualificationScope"),
        "initialDisabled": lifecycle["initialDisabled"],
        "returnedToDisabled": lifecycle["returnedToDisabled"],
        "tkQ11Passed": tk_q11_passed,
        "alertLifecycle": lifecycle,
        "e2eQ02Diagnostics": list(lifecycle.get("e2eQ02Diagnostics") or []),
        "cleanup": cleanup,
    }
    report_path = artifact_path(root, REPORT_FILE_NAME, create_parent=True)
    report["reportPath"] = str(report_path)
    write_json_artifact(root, report_path, report)
    state["status"] = "completed" if passed else "failed"
    state["completedAt"] = report["completedAt"]
    state["reportPath"] = str(report_path)
    state["cleanup"] = cleanup
    write_json_artifact(root, state_path, state)
    return report


def poll_alert_parity_batch(
    solution: str | Path,
    *,
    results: dict[str, Any] | list[dict[str, Any]] | None = None,
    results_path: str | Path | None = None,
    poll_fn: Callable[[dict[str, Any]], dict[str, Any] | list[dict[str, Any]] | None] | None = None,
    timeout_expired: bool = False,
    finalize: bool = True,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    state_path = migrate_legacy_artifact(root, STATE_FILE_NAME)
    if not state_path.exists():
        raise ValueError("no alert parity state exists for this solution")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("status") != "awaiting-alerts":
        raise ValueError(f"alert parity run is not active: {state.get('status')}")
    target = require_locked_target(root)
    if (state.get("target") or {}).get("workspaceResourceId", "").lower() != target[
        "workspaceResourceId"
    ].lower():
        raise ValueError("alert parity state does not match the locked target")

    comparison_error: str | None = None
    scope_error: str | None = None
    verified_scope: dict[str, Any] | None = None
    comparisons: list[dict[str, Any]] = []
    cleanup: list[dict[str, Any]] = []
    lifecycle: dict[str, Any] = dict(state.get("alertLifecycle") or {})
    tk_q11_passed = False
    should_disable = bool(finalize or timeout_expired)
    try:
        verified_scope = _verify_qualification_scope(root, state)
        if timeout_expired:
            raise TimeoutError("alert parity batch polling timed out")
        raw = results
        if raw is None and results_path is not None:
            raw = json.loads(
                Path(results_path).expanduser().read_text(encoding="utf-8-sig")
            )
        if raw is None and poll_fn is not None:
            raw = poll_fn(state)
        if raw is None and not finalize:
            should_disable = False
            return {
                "status": "awaiting-alerts",
                "runId": state["runId"],
                "statePath": str(state_path),
            }
        expected = {pair["detection"] for pair in state["rules"]}
        comparisons = compare_alert_captures(
            expected,
            raw,
            expected_match_keys=set(state.get("expectedMatchKeys") or []),
            expected_match_keys_by_detection={
                detection: set(keys)
                for detection, keys in (
                    state.get("expectedMatchKeysByDetection") or {}
                ).items()
            },
        )
    except Exception as exc:
        should_disable = True
        if verified_scope is None:
            scope_error = str(exc)
        else:
            comparison_error = str(exc)
    finally:
        if should_disable:
            raw_cleanup = _disable_all(state, state_dir=state_dir)
            cleanup, lifecycle, tk_q11_passed = _normalize_cleanup_and_lifecycle(
                state, raw_cleanup
            )

    cleanup_ok = bool(cleanup) and all(item["disabled"] for item in cleanup)
    passed = (
        comparison_error is None
        and scope_error is None
        and bool(comparisons)
        and all(item["passed"] for item in comparisons)
        and cleanup_ok
    )
    report = {
        "runId": state["runId"],
        "status": "passed" if passed else "failed",
        "completedAt": _utc_now(),
        "solution": str(root),
        "scenarioMarker": state.get("scenarioMarker"),
        "fixtures": state.get("fixtures") or [],
        "strictParity": True,
        "comparisonError": comparison_error,
        "scopeVerificationError": scope_error,
        "qualificationScopeVerified": verified_scope is not None and scope_error is None,
        "selectionPlanSha256": (
            verified_scope.get("planSha256") if verified_scope else None
        ),
        "testedDetectionPaths": (
            verified_scope.get("selectedDetectionPaths") if verified_scope else []
        ),
        "testedSourceIds": (
            verified_scope.get("selectedSourceIds") if verified_scope else []
        ),
        "comparisons": comparisons,
        "qualificationScope": verified_scope or state.get("qualificationScope"),
        "initialDisabled": lifecycle.get("initialDisabled", True),
        "returnedToDisabled": lifecycle.get("returnedToDisabled", False),
        "tkQ11Passed": tk_q11_passed,
        "alertLifecycle": lifecycle,
        "e2eQ02Diagnostics": list(lifecycle.get("e2eQ02Diagnostics") or []),
        "cleanup": cleanup,
    }
    report_path = artifact_path(root, REPORT_FILE_NAME, create_parent=True)
    report["reportPath"] = str(report_path)
    write_json_artifact(root, report_path, report)
    state["status"] = "completed" if passed else "failed"
    state["completedAt"] = report["completedAt"]
    state["reportPath"] = str(report_path)
    state["cleanup"] = cleanup
    write_json_artifact(root, state_path, state)
    return report


def abort_alert_parity(
    solution: str | Path, *, state_dir: str | Path | None = None
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    state_path = migrate_legacy_artifact(root, STATE_FILE_NAME)
    if not state_path.exists():
        raise ValueError("no alert parity state exists for this solution")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    target = require_locked_target(root)
    if (state.get("target") or {}).get("workspaceResourceId", "").lower() != target[
        "workspaceResourceId"
    ].lower():
        raise ValueError("alert parity state does not match the locked target")
    cleanup: list[dict[str, Any]] = []
    lifecycle: dict[str, Any] = {}
    tk_q11_passed = False
    try:
        raw_cleanup = _disable_all(state, state_dir=state_dir)
        cleanup, lifecycle, tk_q11_passed = _normalize_cleanup_and_lifecycle(
            state, raw_cleanup
        )
    finally:
        success = bool(cleanup) and all(item.get("disabled") for item in cleanup)
        state["status"] = "aborted" if success else "cleanup-failed"
        state["abortedAt"] = _utc_now()
        state["cleanup"] = cleanup
        write_json_artifact(root, state_path, state)
    return {
        "status": state["status"],
        "runId": state["runId"],
        "initialDisabled": lifecycle.get("initialDisabled", True),
        "returnedToDisabled": lifecycle.get("returnedToDisabled", False),
        "tkQ11Passed": tk_q11_passed,
        "alertLifecycle": lifecycle,
        "cleanup": cleanup,
        "statePath": str(state_path),
    }


def abort_alert_parity_batch(
    solution: str | Path, *, state_dir: str | Path | None = None
) -> dict[str, Any]:
    return abort_alert_parity(solution, state_dir=state_dir)
