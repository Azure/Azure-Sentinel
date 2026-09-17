from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .artifacts import artifact_path
from .alert_parity import _arm_request, _arm_token, _sentinel_rule_url
from .converter import iso_duration, solution_paths


TRIGGER_OPERATORS = {
    "gt": "GreaterThan",
    "lt": "LessThan",
    "eq": "Equal",
    "ne": "NotEqual",
}


def _duration(value: Any, field: str) -> str:
    duration, warning = iso_duration(value)
    if warning:
        raise ValueError(f"{field}: {warning}")
    return duration


def analytic_rule_payload(document: dict[str, Any]) -> dict[str, Any]:
    if str(document.get("kind") or "").lower() != "scheduled":
        raise ValueError("only Scheduled analytic rules can be deployed")
    required = ("id", "name", "query", "severity", "queryFrequency", "queryPeriod")
    missing = [field for field in required if not document.get(field)]
    if missing:
        raise ValueError(f"analytic rule is missing: {', '.join(missing)}")

    trigger = str(document.get("triggerOperator") or "gt").lower()
    if trigger not in TRIGGER_OPERATORS:
        raise ValueError(f"unsupported triggerOperator: {trigger}")

    properties: dict[str, Any] = {
        "displayName": str(document["name"]),
        "description": str(document.get("description") or ""),
        "severity": str(document["severity"]),
        "enabled": False,
        "query": str(document["query"]),
        "queryFrequency": _duration(document["queryFrequency"], "queryFrequency"),
        "queryPeriod": _duration(document["queryPeriod"], "queryPeriod"),
        "triggerOperator": TRIGGER_OPERATORS[trigger],
        "triggerThreshold": int(document.get("triggerThreshold") or 0),
        "suppressionDuration": _duration(
            document.get("suppressionDuration") or "5h", "suppressionDuration"
        ),
        "suppressionEnabled": bool(document.get("suppressionEnabled", False)),
        "eventGroupingSettings": document.get("eventGroupingSettings")
        or {"aggregationKind": "SingleAlert"},
        "alertRuleTemplateName": str(document["id"]),
        "templateVersion": str(document.get("version") or ""),
    }
    for source, target in (
        ("tactics", "tactics"),
        ("relevantTechniques", "techniques"),
        ("entityMappings", "entityMappings"),
        ("customDetails", "customDetails"),
        ("alertDetailsOverride", "alertDetailsOverride"),
        ("incidentConfiguration", "incidentConfiguration"),
    ):
        value = document.get(source)
        if value is not None:
            properties[target] = value
    return {"kind": "Scheduled", "properties": properties}


def deploy_analytic_rules(
    solution: str | Path,
    *,
    workspace_resource_id: str,
) -> dict[str, Any]:
    root, source_dir, output = solution_paths(solution)
    output.mkdir(parents=True, exist_ok=True)

    token = _arm_token()
    results: list[dict[str, Any]] = []
    source_files = sorted(source_dir.glob("*.yaml")) + sorted(source_dir.glob("*.yml"))
    for source_path in source_files:
        result: dict[str, Any] = {
            "source": str(source_path),
            "id": None,
            "name": source_path.stem,
            "success": False,
            "operation": "upsert",
            "statusCode": None,
            "error": None,
        }
        try:
            document = yaml.safe_load(source_path.read_text(encoding="utf-8-sig"))
            if not isinstance(document, dict):
                raise ValueError("analytic rule YAML must contain an object")
            rule_id = str(document.get("id") or "")
            result["id"] = rule_id
            result["name"] = str(document.get("name") or source_path.stem)
            payload = analytic_rule_payload(document)
            status, response = _arm_request(
                "PUT",
                _sentinel_rule_url(workspace_resource_id, rule_id),
                token,
                payload,
            )
            result["statusCode"] = status
            result["success"] = status in (200, 201)
            if result["success"]:
                result["enabled"] = bool(
                    (response.get("properties") or {}).get("enabled", False)
                )
                if result["enabled"]:
                    result["success"] = False
                    result["error"] = {
                        "code": "UnexpectedEnabledState",
                        "message": "deployed analytic rule was not disabled",
                        "response": response,
                    }
            else:
                result["error"] = response.get("error") or response
        except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
            result["error"] = {"code": type(exc).__name__, "message": str(exc)}
        results.append(result)

    report = {
        "provider": "azure-resource-manager",
        "workspaceResourceId": workspace_resource_id,
        "solution": str(root),
        "total": len(results),
        "succeeded": sum(bool(item["success"]) for item in results),
        "failed": sum(not item["success"] for item in results),
        "results": results,
    }
    report_path = artifact_path(root, "deployment.sentinel.json", create_parent=True)
    report["reportPath"] = str(report_path)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
