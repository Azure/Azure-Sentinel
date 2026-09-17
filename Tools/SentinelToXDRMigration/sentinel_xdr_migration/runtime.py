from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from .artifacts import report_directory
from .catalog import referenced_catalog_tables, referenced_custom_tables
from .converter import xdr_detection_files
from .onboarding import (
    AUTH_RECORD_NAME,
    CONFIG_NAME,
    GRAPH_CLIENT_ID,
    GRAPH_SCOPE,
    TOKEN_CACHE_NAME,
    _load_auth_record,
    _read_json,
    _state_dir,
)
from .report import write_runtime_validation_report

ADVANCED_HUNTING_ENDPOINT = "https://graph.microsoft.com/v1.0/security/runHuntingQuery"
PROVIDER_PLATFORMS = {
    "graph": "Microsoft Defender XDR Advanced Hunting",
    "triage-mcp": "Microsoft Sentinel Triage MCP",
    "log-analytics-cli": "Microsoft Sentinel Log Analytics",
}
SUPPORTED_EXTERNAL_PROVIDERS = frozenset(
    provider for provider in PROVIDER_PLATFORMS if provider != "graph"
)


def _detection_files(output: Path) -> list[Path]:
    return xdr_detection_files(output)


def _referenced_solution_functions(root: Path, query: str) -> set[str]:
    functions: set[str] = set()
    parser_root = root / "Parsers"
    if not parser_root.exists():
        return functions
    for path in sorted([*parser_root.rglob("*.yaml"), *parser_root.rglob("*.yml")]):
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        except (OSError, yaml.YAMLError):
            continue
        name = str(document.get("FunctionName") or "").strip()
        if name and re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", query
        ):
            functions.add(name)
    return functions


def _write_runtime_artifacts(
    root: Path,
    provider: str,
    results: list[dict[str, Any]],
    *,
    table_availability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output = report_directory(root, create=True)
    summary = {
        "solution": str(root),
        "platform": PROVIDER_PLATFORMS[provider],
        "provider": provider,
        "total": len(results),
        "valid": sum(item["status"] == "passed" for item in results),
        "invalid": sum(item["status"] == "failed" for item in results),
        "blocked": sum(item["status"] == "blocked" for item in results),
        "notRun": sum(item["status"] == "not-run" for item in results),
        "tableAvailability": table_availability or {},
        "results": results,
    }
    json_path = output / f"runtime-validation.{provider}.json"
    html_path = output / f"runtime-validation.{provider}.html"
    summary["jsonReport"] = str(json_path)
    summary["htmlReport"] = str(html_path)
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_runtime_validation_report(summary, html_path)

    local_report = (
        Path(__file__).resolve().parents[1]
        / "Data"
        / "reports"
        / "last-runtime-validation.json"
    )
    local_report.parent.mkdir(parents=True, exist_ok=True)
    local_report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def _advanced_hunting_token(state_root: Path) -> str:
    from azure.identity import DeviceCodeCredential, TokenCachePersistenceOptions

    record = _load_auth_record(state_root / AUTH_RECORD_NAME)
    if record is None:
        raise RuntimeError(
            "Advanced Hunting authentication is missing; run "
            "`sentinel-xdr-migration setup` first"
        )
    config = _read_json(state_root / CONFIG_NAME)
    credential = DeviceCodeCredential(
        client_id=GRAPH_CLIENT_ID,
        tenant_id=config.get("tenantId") or getattr(record, "tenant_id", None),
        authentication_record=record,
        cache_persistence_options=TokenCachePersistenceOptions(name=TOKEN_CACHE_NAME),
        disable_automatic_authentication=True,
    )
    return credential.get_token(GRAPH_SCOPE).token


def run_advanced_hunting_query(
    query: str,
    *,
    state_dir: str | Path | None = None,
    timeout: int = 90,
    retries: int = 2,
    _token: str | None = None,
) -> dict[str, Any]:
    token = _token or _advanced_hunting_token(_state_dir(state_dir))
    request = urllib.request.Request(
        ADVANCED_HUNTING_ENDPOINT,
        data=json.dumps({"Query": query}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    result: dict[str, Any] = {}
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
                status_code = response.status
            rows = body.get("results") or body.get("Results") or []
            return {
                "ok": True,
                "statusCode": status_code,
                "rowCount": len(rows),
                "schema": body.get("schema") or body.get("Schema") or [],
                "error": None,
                "errorDetails": None,
            }
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
                error = parsed.get("error") or {}
                message = error.get("message") or body
            except json.JSONDecodeError:
                message = body
            result = {
                "ok": False,
                "statusCode": exc.code,
                "rowCount": 0,
                "schema": [],
                "error": message[:2000],
                "errorDetails": body[:8000],
            }
            if exc.code not in {429, 502, 503, 504} or attempt == retries:
                return result
        except (TimeoutError, urllib.error.URLError) as exc:
            result = {
                "ok": False,
                "statusCode": 0,
                "rowCount": 0,
                "schema": [],
                "error": str(exc),
                "errorDetails": str(exc),
            }
            if attempt == retries:
                return result
        time.sleep(2 * (attempt + 1))
    return result


def validate_advanced_hunting(
    solution: str | Path,
    *,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    output = root / "XDR Detections"
    results: list[dict[str, Any]] = []
    token = _advanced_hunting_token(_state_dir(state_dir))
    table_status: dict[str, dict[str, Any]] = {}
    for path in _detection_files(output):
        with path.open(encoding="utf-8-sig") as handle:
            document = yaml.safe_load(handle) or {}
        query = document["properties"]["queryCondition"]["queryText"]
        unavailable: list[str] = []
        dependencies = (
            referenced_catalog_tables(query)
            | referenced_custom_tables(query)
            | _referenced_solution_functions(root, query)
        )
        for dependency in sorted(dependencies):
            if dependency not in table_status:
                table_status[dependency] = run_advanced_hunting_query(
                    f"{dependency} | take 0", _token=token
                )
            if not table_status[dependency]["ok"]:
                unavailable.append(dependency)
        if unavailable:
            results.append(
                {
                    "detection": path.name,
                    "status": "blocked",
                    "valid": False,
                    "statusCode": 0,
                    "rowCount": 0,
                    "schemaColumnCount": 0,
                    "error": (
                        "required Advanced Hunting table or function is unavailable in the "
                        f"current tenant: {', '.join(unavailable)}"
                    ),
                    "errorDetails": None,
                }
            )
            continue
        runtime = run_advanced_hunting_query(query, _token=token)
        results.append(
            {
                "detection": path.name,
                "status": "passed" if runtime["ok"] else "failed",
                "valid": runtime["ok"],
                "statusCode": runtime["statusCode"],
                "rowCount": runtime["rowCount"],
                "schemaColumnCount": len(runtime["schema"]),
                "error": runtime["error"],
                "errorDetails": runtime["errorDetails"],
            }
        )
    return _write_runtime_artifacts(
        root,
        "graph",
        results,
        table_availability={
            table: {
                "available": status["ok"],
                "statusCode": status["statusCode"],
                "error": status["error"],
            }
            for table, status in table_status.items()
        },
    )


def record_runtime_validation(
    solution: str | Path,
    *,
    provider: str,
    results_path: str | Path,
) -> dict[str, Any]:
    if provider not in SUPPORTED_EXTERNAL_PROVIDERS:
        raise ValueError(
            f"unsupported external runtime provider {provider!r}; "
            f"expected one of {sorted(SUPPORTED_EXTERNAL_PROVIDERS)}"
        )
    root = Path(solution).expanduser().resolve()
    output = root / "XDR Detections"
    expected = {path.name for path in _detection_files(output)}
    raw = json.loads(Path(results_path).expanduser().read_text(encoding="utf-8"))
    entries = raw.get("results") if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ValueError("runtime results must be a JSON list or an object containing results")

    normalized: list[dict[str, Any]] = []
    names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each runtime result must be a JSON object")
        detection = str(entry.get("detection") or "").strip()
        if not detection:
            raise ValueError("each runtime result requires a detection filename")
        if detection in names:
            raise ValueError(f"duplicate runtime result for {detection}")
        names.add(detection)
        status = str(entry.get("status") or "").strip().lower()
        if not status:
            status = "passed" if entry.get("valid") is True else "failed"
        if status not in {"passed", "failed", "blocked", "not-run"}:
            raise ValueError(f"invalid runtime status {status!r} for {detection}")
        normalized.append(
            {
                "detection": detection,
                "status": status,
                "valid": status == "passed",
                "statusCode": int(entry.get("statusCode") or 0),
                "rowCount": int(entry.get("rowCount") or 0),
                "schemaColumnCount": int(entry.get("schemaColumnCount") or 0),
                "error": entry.get("error"),
                "errorDetails": entry.get("errorDetails"),
            }
        )

    missing = sorted(expected - names)
    unknown = sorted(names - expected)
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing detections: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown detections: {', '.join(unknown)}")
        raise ValueError("; ".join(details))
    return _write_runtime_artifacts(root, provider, normalized)
