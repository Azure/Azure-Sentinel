from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import yaml

from .artifacts import existing_artifact_path, report_directory
from .converter import analytic_rule_files, validate_document

JSON_NAME = "migration-report.json"
HTML_NAME = "migration-report.html"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    return value if isinstance(value, dict) else {}


def _error(
    stage: str,
    message: Any,
    *,
    provider: str | None = None,
    status_code: Any = None,
    code: Any = None,
    details: Any = None,
) -> dict[str, Any]:
    return {
        "stage": stage,
        "provider": provider,
        "statusCode": status_code,
        "code": code,
        "message": str(message),
        "details": details,
    }


def _entity_recommendation(source: dict[str, Any], conversion_notes: list[str]) -> str | None:
    if not any(
        "mapping" in value.lower() or "entity confirmation required" in value.lower()
        for value in conversion_notes
    ):
        return None
    for entity in source.get("entityMappings") or []:
        if entity.get("entityType") != "Account":
            continue
        for field in entity.get("fieldMappings") or []:
            if field.get("identifier") == "Name":
                column = str(field.get("columnName") or "the projected user column")
                return (
                    f"Verify whether `{column}` is always a complete UPN. If confirmed, "
                    f"map it to Account.upnColumn. Otherwise project an Entra user ID, SID, "
                    "or account name plus domain. Do not infer identity semantics from the "
                    "column name alone."
                )
    return None


def build_solution_report(
    solution: str | Path,
    *,
    ingestion_reports: list[str | Path] | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    output = root / "XDR Detections"
    reports = report_directory(root, create=True)
    manifest = _read_json(existing_artifact_path(root, "manifest.json"))
    manifest_by_source = {
        Path(item.get("source") or "").name: item for item in manifest.get("results") or []
    }
    runtime_reports = [
        _read_json(path)
        for path in sorted(reports.glob("runtime-validation.*.json"))
    ]
    if not runtime_reports:
        runtime_reports = [
            _read_json(path)
            for path in sorted(output.glob("runtime-validation.*.json"))
        ]
    deployment = _read_json(existing_artifact_path(root, "deployment.graph.json"))
    analytic_deployment = _read_json(
        existing_artifact_path(root, "deployment.sentinel.json")
    )
    parity = _read_json(existing_artifact_path(root, "alert-parity-report.json"))
    query_parity = _read_json(existing_artifact_path(root, "mock-query-parity.json"))
    deployment_by_id = {
        str(item.get("id")): item for item in deployment.get("results") or []
    }
    analytic_deployment_by_id = {
        str(item.get("id")): item
        for item in analytic_deployment.get("results") or []
    }
    parity_by_detection = {
        str(item.get("detection")): item for item in parity.get("comparisons") or []
    }
    query_parity_by_detection = {
        str(item.get("detection")): item
        for item in query_parity.get("comparisons") or []
    }
    ingestion = [
        _read_json(Path(path).expanduser().resolve())
        for path in ingestion_reports or []
    ]

    rules: list[dict[str, Any]] = []
    for source_path in analytic_rule_files(root):
        source = yaml.safe_load(source_path.read_text(encoding="utf-8-sig")) or {}
        conversion = manifest_by_source.get(source_path.name) or {}
        detection_path = output / source_path.name
        detection: dict[str, Any] = {}
        structural_errors: list[str] = []
        if detection_path.exists():
            try:
                detection = (
                    yaml.safe_load(detection_path.read_text(encoding="utf-8-sig")) or {}
                )
                structural_errors = validate_document(detection)
            except (OSError, ValueError, yaml.YAMLError) as exc:
                structural_errors = [str(exc)]
        properties = detection.get("properties") or {}
        detection_id = str(properties.get("id") or "")
        analytic_runtime: list[dict[str, Any]] = []
        custom_runtime: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        for value in conversion.get("errors") or []:
            errors.append(_error("conversion", value, provider="local-cli"))
        for value in structural_errors:
            errors.append(_error("structural-validation", value, provider="local-cli"))
        for report in runtime_reports:
            provider = str(report.get("provider") or "unknown")
            item = next(
                (
                    candidate
                    for candidate in report.get("results") or []
                    if candidate.get("detection") == source_path.name
                ),
                None,
            )
            if not item:
                continue
            platform = str(report.get("platform") or "unknown")
            runtime_item = {
                "provider": provider,
                "platform": platform,
                "status": item.get("status"),
                "rowCount": item.get("rowCount"),
            }
            is_sentinel = "Sentinel" in platform
            (analytic_runtime if is_sentinel else custom_runtime).append(runtime_item)
            if item.get("status") in {"failed", "blocked"}:
                errors.append(
                    _error(
                        (
                            "analytic-rule-runtime-validation"
                            if is_sentinel
                            else "custom-detection-runtime-validation"
                        ),
                        item.get("error") or item.get("status"),
                        provider=provider,
                        status_code=item.get("statusCode"),
                        details=item.get("errorDetails"),
                    )
                )
        deployed = deployment_by_id.get(detection_id) or {}
        analytic_deployed = analytic_deployment_by_id.get(str(source.get("id"))) or {}
        if analytic_deployed and not analytic_deployed.get("success"):
            arm_error = analytic_deployed.get("error") or {}
            errors.append(
                _error(
                    "analytic-rule-deployment",
                    arm_error.get("message") or arm_error,
                    provider=str(
                        analytic_deployment.get("provider")
                        or "azure-resource-manager"
                    ),
                    status_code=analytic_deployed.get("statusCode"),
                    code=arm_error.get("code"),
                    details=arm_error,
                )
            )
        if deployed and not deployed.get("success"):
            graph_error = deployed.get("error") or {}
            errors.append(
                _error(
                    "custom-detection-deployment",
                    graph_error.get("message") or graph_error,
                    provider=str(deployment.get("provider") or "microsoft-graph"),
                    status_code=deployed.get("statusCode"),
                    code=graph_error.get("code"),
                    details=graph_error,
                )
            )
        parity_item = parity_by_detection.get(source_path.name) or {}
        query_parity_item = query_parity_by_detection.get(source_path.name) or {}
        if parity_item and not parity_item.get("passed"):
            errors.append(
                _error(
                    "alert-parity",
                    "Analytic Rule and Custom Detection alerts are not strictly equal",
                    provider="sentinel-and-defender",
                    details=parity_item,
                )
            )
        if query_parity_item and not query_parity_item.get("passed"):
            errors.append(
                _error(
                    "query-result-parity",
                    "Analytic Rule and Custom Detection query results are not equal",
                    provider="sentinel-and-defender",
                    details=query_parity_item,
                )
            )
        conversion_notes = [
            str(value)
            for value in [
                *(conversion.get("errors") or []),
                *(conversion.get("reviewReasons") or []),
            ]
        ]
        rules.append(
            {
                "name": source.get("name") or source_path.stem,
                "sourceFile": str(source_path),
                "analyticRule": {
                    "id": source.get("id"),
                    "sourceStatus": source.get("status"),
                    "deploymentStatus": (
                        "validated-by-alert-parity"
                        if parity_item
                        else analytic_deployed.get("operation") or "not-recorded"
                    ),
                    "alertStatus": (
                        "passed"
                        if parity_item.get("passed")
                        else "failed"
                        if parity_item
                        else "not-run"
                    ),
                    "runtime": analytic_runtime,
                },
                "customDetection": {
                    "id": detection_id or None,
                    "conversionStatus": conversion.get("status") or "not-run",
                    "reviewRequired": bool(conversion.get("reviewRequired")),
                    "reviewReasons": list(conversion.get("reviewReasons") or []),
                    "structuralStatus": (
                        "passed"
                        if detection and not structural_errors
                        else "failed"
                        if detection
                        else "not-generated"
                    ),
                    "deploymentStatus": (
                        deployed.get("operation") or "not-run"
                    ),
                    "runtime": custom_runtime,
                    "alertStatus": (
                        "passed"
                        if parity_item.get("passed")
                        else "failed"
                        if parity_item
                        else "not-run"
                    ),
                },
                "entityRecommendation": _entity_recommendation(
                    source, conversion_notes
                ),
                "queryParity": {
                    "status": (
                        "passed"
                        if query_parity_item.get("passed")
                        else "failed"
                        if query_parity_item
                        else "not-run"
                    ),
                    "matchKey": query_parity_item.get("matchKey"),
                    "analyticRuleRows": query_parity_item.get("analyticRuleRows"),
                    "customDetectionRows": query_parity_item.get(
                        "customDetectionRows"
                    ),
                },
                "warnings": list(conversion.get("warnings") or []),
                "errors": errors,
            }
        )

    report = {
        "solution": root.name,
        "solutionPath": str(root),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "rules": len(rules),
            "converted": sum(
                item["customDetection"]["conversionStatus"] == "converted"
                for item in rules
            ),
            "needsReview": sum(
                item["customDetection"]["reviewRequired"]
                for item in rules
            ),
            "deploymentReady": sum(
                item["customDetection"]["conversionStatus"] == "converted"
                and not item["customDetection"]["reviewRequired"]
                and item["customDetection"]["structuralStatus"] == "passed"
                for item in rules
            ),
            "strictParityPassed": sum(
                item["customDetection"]["alertStatus"] == "passed" for item in rules
            ),
            "analyticRuntimePassed": sum(
                any(
                    runtime["status"] == "passed"
                    for runtime in item["analyticRule"]["runtime"]
                )
                for item in rules
            ),
            "customRuntimePassed": sum(
                any(
                    runtime["status"] == "passed"
                    for runtime in item["customDetection"]["runtime"]
                )
                for item in rules
            ),
            "queryParityPassed": sum(
                item["queryParity"]["status"] == "passed" for item in rules
            ),
            "errors": sum(len(item["errors"]) for item in rules),
        },
        "rules": rules,
        "ingestion": ingestion,
        "artifacts": {
            "transformationReport": manifest.get("transformationReport"),
            "runtimeReports": [
                {
                    "provider": item.get("provider"),
                    "jsonReport": item.get("jsonReport"),
                    "htmlReport": item.get("htmlReport"),
                }
                for item in runtime_reports
            ],
            "deploymentReport": deployment.get("reportPath"),
            "analyticDeploymentReport": analytic_deployment.get("reportPath"),
            "queryParityReport": query_parity.get("reportPath"),
            "alertParityReport": parity.get("reportPath"),
            "ingestionReports": [
                item.get("reportPath") for item in ingestion if item.get("reportPath")
            ],
        },
    }
    json_path = reports / JSON_NAME
    html_path = reports / HTML_NAME
    report["jsonReport"] = str(json_path)
    report["htmlReport"] = str(html_path)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_solution_report(report), encoding="utf-8", newline="\n")
    return report


def render_solution_report(report: dict[str, Any]) -> str:
    def runtime_html(values: list[dict[str, Any]]) -> str:
        if not values:
            return '<span class="muted">not recorded</span>'
        return "<br>".join(
            f"{escape(str(item['provider']))}: "
            f"<span class=\"status {escape(str(item['status']))}\">"
            f"{escape(str(item['status']))}</span>"
            f" ({item.get('rowCount', 0)} rows)"
            for item in values
        )

    rows: list[str] = []
    for rule in report["rules"]:
        errors = rule["errors"]
        error_html = (
            "<span class=\"ok\">None</span>"
            if not errors
            else "".join(
                "<details><summary>"
                f"{escape(str(item['stage']))}: {escape(str(item['message']))}"
                "</summary><pre>"
                f"{escape(json.dumps(item, indent=2, ensure_ascii=True))}"
                "</pre></details>"
                for item in errors
            )
        )
        recommendation = rule.get("entityRecommendation")
        rows.append(
            "<tr>"
            f"<td><strong>{escape(str(rule['name']))}</strong><br>"
            f"<code>{escape(str(rule['analyticRule']['id']))}</code></td>"
            f"<td>{escape(str(rule['analyticRule']['deploymentStatus']))}<br>"
            f"alerts: {escape(str(rule['analyticRule']['alertStatus']))}<br>"
            f"runtime: {runtime_html(rule['analyticRule']['runtime'])}</td>"
            f"<td>{escape(str(rule['customDetection']['conversionStatus']))}<br>"
            f"review required: {escape(str(rule['customDetection']['reviewRequired']).lower())}<br>"
            f"structural: {escape(str(rule['customDetection']['structuralStatus']))}<br>"
            f"deployment: {escape(str(rule['customDetection']['deploymentStatus']))}<br>"
            f"alerts: {escape(str(rule['customDetection']['alertStatus']))}<br>"
            f"runtime: {runtime_html(rule['customDetection']['runtime'])}</td>"
            f"<td>{escape(recommendation) if recommendation else '<span class=\"muted\">None</span>'}</td>"
            f"<td><span class=\"status {escape(str(rule['queryParity']['status']))}\">"
            f"{escape(str(rule['queryParity']['status']))}</span><br>"
            f"AR rows: {escape(str(rule['queryParity']['analyticRuleRows']))}<br>"
            f"CD rows: {escape(str(rule['queryParity']['customDetectionRows']))}<br>"
            f"<code>{escape(json.dumps(rule['queryParity']['matchKey'], ensure_ascii=True))}</code></td>"
            f"<td>{error_html}</td>"
            "</tr>"
        )
    summary = report["summary"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(str(report["solution"]))} migration report</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0}}main{{max-width:1600px;margin:auto;padding:28px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0}}.card,table{{background:#111827;border:1px solid #334155}}
.card{{padding:14px;border-radius:8px}}.card strong{{display:block;font-size:1.7rem}}table{{width:100%;border-collapse:collapse}}
th,td{{padding:12px;border-bottom:1px solid #334155;text-align:left;vertical-align:top}}th{{background:#1e293b}}
.muted{{color:#94a3b8}}.ok{{color:#86efac}}pre{{white-space:pre-wrap;max-width:720px;overflow:auto}}details{{margin-bottom:8px}}
.status{{display:inline-block;border-radius:999px;padding:2px 7px;font-weight:600}}.passed{{background:#14532d;color:#bbf7d0}}.failed{{background:#7f1d1d;color:#fecaca}}.blocked{{background:#78350f;color:#fde68a}}.not-run{{background:#334155;color:#cbd5e1}}
code{{font-size:.8rem}}@media(max-width:900px){{.cards{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><main>
<h1>{escape(str(report["solution"]))} migration report</h1>
<div class="muted">{escape(str(report["generatedAt"]))}</div>
<section class="cards">
<div class="card">Rules<strong>{summary["rules"]}</strong></div>
<div class="card">Converted<strong>{summary["converted"]}</strong></div>
<div class="card">Review required<strong>{summary["needsReview"]}</strong></div>
<div class="card">Deployment ready<strong>{summary["deploymentReady"]}</strong></div>
<div class="card">AR runtime passed<strong>{summary["analyticRuntimePassed"]}</strong></div>
<div class="card">CD runtime passed<strong>{summary["customRuntimePassed"]}</strong></div>
<div class="card">Query parity passed<strong>{summary["queryParityPassed"]}</strong></div>
<div class="card">Parity passed<strong>{summary["strictParityPassed"]}</strong></div>
<div class="card">Errors<strong>{summary["errors"]}</strong></div>
</section>
<table><thead><tr><th>Rule</th><th>Analytic Rule</th><th>Custom Detection</th><th>Entity recommendation</th><th>Query parity</th><th>Detailed errors</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
</main></body></html>"""
