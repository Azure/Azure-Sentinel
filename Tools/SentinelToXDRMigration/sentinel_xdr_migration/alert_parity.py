from __future__ import annotations

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
from typing import Any

import yaml

from .artifacts import artifact_path, migrate_legacy_artifact
from .converter import validate_document, xdr_detection_files
from .deployment import DEPLOYMENT_ENDPOINT, _deployment_token, _graph_request
from .target_context import require_locked_target

ARM_SCOPE = "https://management.azure.com/.default"
SENTINEL_ALERT_RULE_API_VERSION = "2024-03-01"
STATE_FILE_NAME = "alert-parity-state.json"
REPORT_FILE_NAME = "alert-parity-report.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _arm_token() -> str:
    from azure.identity import AzureCliCredential

    return AzureCliCredential().get_token(ARM_SCOPE).token


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


def _load_pairs(
    solution: str | Path, selected: list[str] | None = None
) -> tuple[Path, list[dict[str, Any]]]:
    root = Path(solution).expanduser().resolve()
    output = root / "XDR Detections"
    wanted = set(selected or [])
    pairs: list[dict[str, Any]] = []
    for path in xdr_detection_files(output):
        if wanted and path.name not in wanted and path.stem not in wanted:
            continue
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        errors = validate_document(document)
        conversion = (document.get("contentProvenance") or {}).get("conversion") or {}
        if conversion.get("status") != "converted" or conversion.get("reviewRequired"):
            errors.append("detection must be converted with no review required")
        if errors:
            raise ValueError(f"{path.name}: {'; '.join(errors)}")
        source = (document.get("contentProvenance") or {}).get("source") or {}
        source_id = str(source.get("id") or "").strip()
        detection_id = str((document.get("properties") or {}).get("id") or "").strip()
        if not source_id or not detection_id:
            raise ValueError(f"{path.name}: source and detection IDs are required")
        alert = (
            ((document.get("properties") or {}).get("detectionAction") or {}).get(
                "alertTemplate"
            )
            or {}
        )
        pairs.append(
            {
                "detection": path.name,
                "displayName": str(
                    (document.get("properties") or {}).get("displayName") or path.stem
                ),
                "analyticRuleId": source_id,
                "customDetectionId": detection_id,
                "entityMappings": alert.get("entityMappings") or {},
            }
        )
    if wanted:
        found = {pair["detection"] for pair in pairs} | {
            Path(pair["detection"]).stem for pair in pairs
        }
        missing = sorted(wanted - found)
        if missing:
            raise ValueError(f"unknown detections: {', '.join(missing)}")
    if not pairs:
        raise ValueError(f"no converted detections selected under {output}")
    return root, pairs


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


def _read_rule_states(
    pairs: list[dict[str, Any]],
    workspace_resource_id: str,
    arm_token: str,
    graph_token: str,
) -> None:
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
        graph_enabled = str(graph.get("status") or "").lower() == "enabled"
        if sentinel_enabled or graph_enabled:
            raise RuntimeError(
                f"{pair['detection']}: parity validation requires both rules to "
                "be disabled before start"
            )
        pair["sentinelResource"] = sentinel


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
        {"status": "enabled" if enabled else "disabled"},
    )
    if status != 200:
        errors.append(f"Custom Detection: {_error_message(response)}")
    return errors


def _disable_all(
    state: dict[str, Any],
    *,
    arm_token: str | None = None,
    graph_token: str | None = None,
    state_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    arm = arm_token or _arm_token()
    target = state.get("target") or {}
    graph = graph_token or _deployment_token(
        state_dir,
        tenant_id=target.get("tenantId"),
    )
    results: list[dict[str, Any]] = []
    for pair in state.get("rules") or []:
        errors = _set_pair_enabled(
            pair, state["workspaceResourceId"], arm, graph, False
        )
        results.append(
            {
                "detection": pair["detection"],
                "disabled": not errors,
                "errors": errors,
            }
        )
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
        ingestion_tool = Path(__file__).resolve().parents[2] / "AzureMonitorLogsIngestion"
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
    state_path = migrate_legacy_artifact(root, STATE_FILE_NAME)
    if state_path.exists():
        existing = json.loads(state_path.read_text(encoding="utf-8"))
        if existing.get("status") == "awaiting-alerts":
            raise RuntimeError(
                "an alert parity run is already active; complete or abort it first"
            )

    arm_token = _arm_token()
    graph_token = _deployment_token(state_dir, tenant_id=target["tenantId"])
    _read_rule_states(pairs, workspace_resource_id, arm_token, graph_token)
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
        "contract": str(Path(contract).expanduser().resolve()),
        "payload": str(Path(payload).expanduser().resolve()),
        "rules": pairs,
    }
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    enabled: list[dict[str, Any]] = []
    try:
        for pair in pairs:
            errors = _set_pair_enabled(
                pair, workspace_resource_id, arm_token, graph_token, True
            )
            enabled.append({"detection": pair["detection"], "errors": errors})
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
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return {
            "status": state["status"],
            "runId": state["runId"],
            "statePath": str(state_path),
            "rulesEnabled": len(pairs),
            "ingestion": ingestion,
            "capturePlan": state["capturePlan"],
            "nextCommand": (
                "sentinel-xdr-migration complete-alert-parity "
                f'--solution "{root}" --results "<normalized-results.json>"'
            ),
        }
    except Exception:
        state["status"] = "failed"
        state["cleanup"] = _disable_all(
            state,
            arm_token=arm_token,
            graph_token=graph_token,
            state_dir=state_dir,
        )
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        raise


def start_alert_parity_batch(
    solution: str | Path,
    *,
    workspace_resource_id: str | None = None,
    plan_path: str | Path,
    state_dir: str | Path | None = None,
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
    pairs_by_name = {pair["detection"]: pair for pair in pairs}
    pairs_by_stem = {Path(pair["detection"]).stem: pair for pair in pairs}
    fixture_by_detection: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise ValueError("each batch parity fixture must be an object")
        requested = str(fixture.get("detection") or "").strip()
        pair = pairs_by_name.get(requested) or pairs_by_stem.get(requested)
        if pair is None:
            raise ValueError(f"unknown detection in batch parity plan: {requested}")
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

    arm_token = _arm_token()
    graph_token = _deployment_token(state_dir, tenant_id=target["tenantId"])
    _read_rule_states(pairs, workspace_resource_id, arm_token, graph_token)
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
        "rules": pairs,
    }
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    try:
        for pair in pairs:
            errors = _set_pair_enabled(
                pair, workspace_resource_id, arm_token, graph_token, True
            )
            if errors:
                raise RuntimeError(
                    f"{pair['detection']}: failed to enable parity rules: "
                    f"{'; '.join(errors)}"
                )
        ingestions = []
        for pair in pairs:
            fixture = fixture_by_detection[pair["detection"]]
            ingestions.append(
                {
                    "detection": pair["detection"],
                    "result": _ingest(fixture["contract"], fixture["payload"]),
                }
            )
        state["status"] = "awaiting-alerts"
        state["enabledAt"] = _utc_now()
        state["ingestions"] = ingestions
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
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return {
            "status": state["status"],
            "runId": state["runId"],
            "statePath": str(state_path),
            "rulesEnabled": len(pairs),
            "fixturesIngested": len(ingestions),
            "ingestions": ingestions,
            "capturePlan": state["capturePlan"],
            "nextCommand": (
                "sentinel-xdr-migration complete-alert-parity "
                f'--solution "{root}" --results "<normalized-results.json>"'
            ),
        }
    except Exception:
        state["status"] = "failed"
        state["cleanup"] = _disable_all(
            state,
            arm_token=arm_token,
            graph_token=graph_token,
            state_dir=state_dir,
        )
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        raise


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
    comparisons: list[dict[str, Any]] = []
    cleanup: list[dict[str, Any]] = []
    try:
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
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        comparison_error = str(exc)
    finally:
        cleanup = _disable_all(state, state_dir=state_dir)

    cleanup_ok = all(item["disabled"] for item in cleanup)
    passed = (
        comparison_error is None
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
        "comparisons": comparisons,
        "cleanup": cleanup,
    }
    report_path = artifact_path(root, REPORT_FILE_NAME, create_parent=True)
    report["reportPath"] = str(report_path)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    state["status"] = "completed" if passed else "failed"
    state["completedAt"] = report["completedAt"]
    state["reportPath"] = str(report_path)
    state["cleanup"] = cleanup
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
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
    cleanup = _disable_all(state, state_dir=state_dir)
    success = all(item["disabled"] for item in cleanup)
    state["status"] = "aborted" if success else "cleanup-failed"
    state["abortedAt"] = _utc_now()
    state["cleanup"] = cleanup
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return {
        "status": state["status"],
        "runId": state["runId"],
        "cleanup": cleanup,
        "statePath": str(state_path),
    }
