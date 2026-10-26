from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qsl, urlsplit

from solution_manager.core.artifacts import report_directory, write_json_artifact
from solution_manager.core.content_paths import content_path
from solution_manager.migration.workbook_workflow import enabled, selected_workbook_references, verify_inventory


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _seal(value: dict[str, Any]) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def _context(solution: str | Path) -> tuple[Path, dict[str, Any], dict[str, str]]:
    from solution_manager.core.workflow import _load

    root = Path(solution).expanduser().resolve()
    _, state = _load(root)
    context = state["context"]
    if not enabled(state) or context.get("workflowProfile") != "qualification":
        raise ValueError("workbook query/UI qualification requires an enabled Qualification run")
    if context.get("targetContextLocked") is not True:
        raise ValueError("workbook qualification requires the locked Qualification target")
    target = {
        key: context[key]
        for key in ("tenantId", "subscriptionId", "workspaceResourceId", "workspaceCustomerId")
    }
    if any(not isinstance(value, str) or not value for value in target.values()):
        raise ValueError("workbook qualification target is incomplete")
    verify_inventory(root, state)
    return root, state, target


def plan_workbook_queries(
    solution: str | Path,
    *,
    workbook: str,
    seed: int = 42,
    clock: str,
    scale: int = 1,
    recipe: str = "syslog-operational-v1",
) -> dict[str, Any]:
    from solution_manager.migration._workbook_core.workbook_fixtures import harness_files
    from solution_manager.migration._workbook_core.workbook_mock import build, configuration
    from solution_manager.migration.workbooks import validate_workbooks

    root, state, target = _context(solution)
    selected = selected_workbook_references(root)
    path = content_path(root, workbook)
    if path not in selected:
        raise ValueError("query qualification requires an explicitly selected Defender workbook")
    validation = validate_workbooks(root, selected_only=True)
    if validation["invalid"] or validation["valid"] != len(selected):
        raise ValueError("selected workbooks have unresolved structural or review blockers")
    converted = json.loads(path.read_text(encoding="utf-8-sig"))
    source = content_path(root, converted["contentProvenance"]["source"]["path"])
    if _sha(source.read_bytes()) != converted["contentProvenance"]["source"]["sha256"]:
        raise ValueError("workbook qualification source provenance is stale")
    config = configuration(
        seed, clock, scale, recipe, "run-" + _sha(state["runId"].encode())[:16]
    )
    bundle = build(source.read_bytes(), config)
    manifest = json.loads(bundle["manifest.json"])
    harnesses = harness_files(
        manifest, json.loads(source.read_text(encoding="utf-8-sig")), converted
    )
    entries = []
    for case in manifest["cases"]:
        for side, suffix in (("sentinel", "sentinel"), ("advanced-hunting", "ah")):
            name = f"{case['id']}.{suffix}.kql"
            query = harnesses[name]
            if query.encode() != bundle["harnesses/" + name]:
                raise ValueError("authored workbook queries differ from the reviewed fixture oracle")
            entries.append({
                "caseId": case["id"],
                "side": side,
                "sourcePath": case["sourcePath"],
                "outputPath": case["outputPath"],
                "originalQuerySha256": case["querySha256"],
                "query": query,
                "querySha256": _sha(query.encode()),
                "expected": case["expected"],
            })
    diagnostic = json.loads(bundle["diagnostic.json"])["expected"]
    for side, suffix in (("sentinel", "sentinel"), ("advanced-hunting", "ah")):
        query = bundle[f"harnesses/diagnostic-hourly.{suffix}.kql"].decode()
        entries.append({
            "caseId": "diagnostic-hourly",
            "side": side,
            "sourcePath": None,
            "outputPath": None,
            "originalQuerySha256": None,
            "query": query,
            "querySha256": _sha(query.encode()),
            "expected": diagnostic,
        })
    plan = {
        "schemaVersion": "1.0.0",
        "operation": "workbook-query-qualification",
        "runId": state["runId"],
        "target": target,
        "workbook": path.relative_to(root).as_posix(),
        "contentId": converted["xdrMetadata"]["contentId"],
        "sourceSha256": _sha(source.read_bytes()),
        "targetSha256": _sha(path.read_bytes()),
        "fixtureConfig": config,
        "fixtureProvenance": manifest["provenance"],
        "queries": entries,
        "ingestion": "not-ingestible",
        "uiStatus": "not-run",
    }
    plan["planSha256"] = _seal(plan)
    return plan


def _current_plan(solution: str | Path, plan: dict[str, Any]) -> dict[str, Any]:
    config = plan["fixtureConfig"]
    current = plan_workbook_queries(
        solution, workbook=plan["workbook"], seed=config["seed"],
        clock=config["clock"], scale=config["scale"], recipe=config["recipe"],
    )
    if current != plan:
        raise ValueError("workbook query plan is stale or has been edited")
    return current


def review_workbook_query_consent(
    plan: dict[str, Any], *, actor: str, reference: str, approved: bool,
) -> dict[str, Any]:
    if not actor.strip() or not reference.strip() or not isinstance(approved, bool):
        raise ValueError("workbook query consent requires an actor, reference, and affirmative decision")
    if plan.get("operation") not in {"workbook-query-qualification", "workbook-ui-qualification"}:
        raise ValueError("workbook consent cannot authorize other operations")
    return {
        "schemaVersion": "1.0.0",
        "operation": plan["operation"],
        "runId": plan["runId"],
        "target": plan["target"],
        "planSha256": plan["planSha256"],
        "approved": approved,
        "withdrawn": False,
        "actor": actor,
        "reference": reference,
    }


def _check_consent(plan: dict[str, Any], consent: dict[str, Any]) -> None:
    if (
        consent.get("schemaVersion") != "1.0.0"
        or consent.get("approved") is not True
        or consent.get("withdrawn") is not False
        or not str(consent.get("actor") or "").strip()
        or not str(consent.get("reference") or "").strip()
        or any(consent.get(key) != plan[key] for key in (
            "operation", "runId", "target", "planSha256",
        ))
    ):
        raise ValueError("current exact workbook harness query consent is missing, stale, or withdrawn")


def _current_inputs(solution: str | Path, plan: dict[str, Any]) -> None:
    root, state, target = _context(solution)
    path = content_path(root, plan["workbook"])
    if (
        state["runId"] != plan["runId"] or target != plan["target"]
        or path not in selected_workbook_references(root)
        or _sha(path.read_bytes()) != plan["targetSha256"]
    ):
        raise ValueError("workbook qualification inputs or target changed during execution")
    source = json.loads(path.read_text(encoding="utf-8-sig"))["contentProvenance"]["source"]
    if _sha(content_path(root, source["path"]).read_bytes()) != plan["sourceSha256"]:
        raise ValueError("workbook qualification source changed during execution")


def execute_workbook_queries(
    solution: str | Path,
    plan: dict[str, Any],
    *,
    read_consent: Callable[[], dict[str, Any]],
    providers: dict[str, Callable[[str, dict[str, str]], dict[str, Any]]],
    family_timeout_seconds: int = 1800,
) -> dict[str, Any]:
    from solution_manager.core.workflow import _run_writer_lock

    if isinstance(family_timeout_seconds, bool) or not isinstance(family_timeout_seconds, int) or not 1 <= family_timeout_seconds <= 21600:
        raise ValueError("workbook query family timeout must be an integer between 1 and 21600 seconds")
    with _run_writer_lock(report_directory(solution) / "workbook-qualification-executor"):
        return _execute_workbook_queries(
            solution, plan, read_consent=read_consent, providers=providers,
            family_timeout_seconds=family_timeout_seconds,
        )


def _execute_workbook_queries(
    solution: str | Path, plan: dict[str, Any], *,
    read_consent: Callable[[], dict[str, Any]],
    providers: dict[str, Callable[[str, dict[str, str]], dict[str, Any]]],
    family_timeout_seconds: int,
) -> dict[str, Any]:
    from solution_manager.migration._workbook_core.workbook_fixtures import assert_result

    _current_plan(solution, plan)
    _check_consent(plan, read_consent())
    if set(providers) != {"sentinel", "advanced-hunting"}:
        raise ValueError("qualification requires independent Sentinel and Advanced Hunting providers")
    if providers["sentinel"] is providers["advanced-hunting"]:
        raise ValueError("the two qualification sides must use independent providers")
    root = Path(solution).expanduser().resolve()
    path = report_directory(root) / f"workbook-queries.{plan['contentId']}.json"
    running = {
        "schemaVersion": "1.0.0", "status": "running", "runId": plan["runId"],
        "target": plan["target"], "planSha256": plan["planSha256"], "plan": plan,
        "results": [], "uiStatus": "not-run", "ingestion": "not-run",
    }
    if path.is_file():
        prior = json.loads(path.read_text(encoding="utf-8-sig"))
        archive = path.with_name(f"{path.stem}.{_sha(path.read_bytes())}.json")
        write_json_artifact(root, archive, prior)
    write_json_artifact(root, path, running)
    deadline = time.monotonic() + family_timeout_seconds
    captured = []
    for entry in plan["queries"]:
        if time.monotonic() >= deadline:
            write_json_artifact(root, path, {
                **running, "status": "failed", "results": captured,
                "error": "query-family-timeout",
            })
            raise ValueError("bounded workbook query family timeout expired")
        _current_inputs(solution, plan)
        _check_consent(plan, read_consent())
        result = providers[entry["side"]](entry["query"], plan["target"])
        if time.monotonic() >= deadline:
            write_json_artifact(root, path, {
                **running, "status": "failed", "results": captured,
                "error": "query-family-timeout",
            })
            raise ValueError("bounded workbook query family timeout expired")
        if (
            not isinstance(result, dict)
            or result.get("status") != "passed"
            or result.get("complete") is not True
            or result.get("provider") != entry["side"]
            or result.get("target") != plan["target"]
            or result.get("querySha256") != entry["querySha256"]
        ):
            write_json_artifact(root, path, {
                **running, "status": "failed", "results": captured,
                "failedCase": {"caseId": entry["caseId"], "side": entry["side"]},
                "providerFailure": result,
            })
            raise ValueError(f"workbook query execution failed or is incomplete: {entry['side']}/{entry['caseId']}")
        try:
            assert_result(entry["expected"], result["result"])
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            write_json_artifact(root, path, {
                **running, "status": "failed", "results": captured,
                "failedCase": {"caseId": entry["caseId"], "side": entry["side"]},
                "error": "exact-result-mismatch",
            })
            raise ValueError(
                f"exact workbook result mismatch: {entry['side']}/{entry['caseId']}"
            ) from exc
        captured.append({
            "caseId": entry["caseId"],
            "side": entry["side"],
            "querySha256": entry["querySha256"],
            "status": "passed",
            "provider": result["provider"],
            "result": result["result"],
        })
    _current_plan(solution, plan)
    final_consent = read_consent()
    _check_consent(plan, final_consent)
    receipt = {
        "schemaVersion": "1.0.0",
        "status": "passed",
        "operation": plan["operation"],
        "runId": plan["runId"],
        "target": plan["target"],
        "planSha256": plan["planSha256"],
        "plan": plan,
        "approval": final_consent,
        "results": captured,
        "completedAt": datetime.now(timezone.utc).isoformat(),
        "ingestion": "not-run",
        "uiStatus": "not-run",
    }
    write_json_artifact(root, path, receipt)
    return {"status": "passed", "cases": len(captured), "reportPath": str(path), "uiStatus": "not-run"}


def default_query_providers(
    *, state_dir: str | Path | None = None,
) -> dict[str, Callable[[str, dict[str, str]], dict[str, Any]]]:
    def sentinel(query: str, target: dict[str, str]) -> dict[str, Any]:
        from solution_manager.qualification.logs_query import (
            azure_cli_credential, execute_workspace_query, logs_query_client,
            verify_azure_cli_target,
        )

        verify_azure_cli_target(target)
        client = logs_query_client(azure_cli_credential(target))
        try:
            response = execute_workspace_query(client, target["workspaceCustomerId"], query)
        finally:
            client.close()
        tables = response.get("tables") or []
        complete = response.get("status") == "passed" and response.get("partial") is False and len(tables) == 1
        return {
            "status": "passed" if complete else "failed",
            "complete": complete, "provider": "sentinel", "target": target,
            "querySha256": _sha(query.encode()),
            "result": _normalize_result(tables[0]["columns"], tables[0]["rows"]) if complete else None,
            "error": response.get("error"),
        }

    def advanced_hunting(query: str, target: dict[str, str]) -> dict[str, Any]:
        from solution_manager.core.onboarding import _state_dir
        from solution_manager.qualification.runtime import _advanced_hunting_token, run_advanced_hunting_query

        token = _advanced_hunting_token(_state_dir(state_dir), tenant_id=target["tenantId"])
        response = run_advanced_hunting_query(
            query, _token=token, capture_full_results=True,
        )
        complete = response.get("ok") is True and isinstance(response.get("results"), list)
        return {
            "status": "passed" if complete else "failed",
            "complete": complete, "provider": "advanced-hunting", "target": target,
            "querySha256": _sha(query.encode()),
            "result": _normalize_result(response["schema"], response["results"]) if complete else None,
            "error": response.get("error"),
        }

    return {"sentinel": sentinel, "advanced-hunting": advanced_hunting}


def _normalize_result(columns: list[dict[str, str]], rows: list[Any]) -> dict[str, Any]:
    aliases = {
        "string": "string", "datetime": "datetime", "int64": "long",
        "long": "long", "int32": "int", "int": "int", "double": "real",
        "real": "real", "boolean": "bool", "bool": "bool", "dynamic": "dynamic",
    }
    normalized = []
    for column in columns:
        name = column.get("name", column.get("Name"))
        raw_type = column.get("type", column.get("Type"))
        if not isinstance(name, str) or not isinstance(raw_type, str) or raw_type.lower() not in aliases:
            raise ValueError("query provider returned an unsupported or malformed column schema")
        normalized.append({"name": name, "type": aliases[raw_type.lower()]})
    names = [column["name"] for column in normalized]
    if len(set(names)) != len(names):
        raise ValueError("query provider returned duplicate columns")
    values = []
    for row in rows:
        if isinstance(row, dict):
            if {key for key in row if not (isinstance(key, str) and key.endswith("@odata.type"))
                    or key in names} != set(names):
                raise ValueError("query provider row keys differ from its schema")
            cells = [row[name] for name in names]
        elif isinstance(row, list) and len(row) == len(names):
            cells = list(row)
        else:
            raise ValueError("query provider returned a malformed result row")
        for index, column in enumerate(normalized):
            if column["type"] == "datetime" and cells[index] is not None:
                value = cells[index]
                if isinstance(value, dict) and set(value) == {"$datetime"}:
                    value = value["$datetime"]
                if not isinstance(value, str):
                    raise ValueError("query provider returned an invalid datetime cell")
                timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    raise ValueError("query provider returned a timezone-less datetime cell")
                cells[index] = timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        values.append(cells)
    return {"columns": normalized, "rows": values}


def plan_workbook_ui(
    solution: str | Path, *, workbook: str, url: str,
    readiness_selectors: dict[str, str],
    steps: list[dict[str, Any]],
    background_activity_review: str,
    browser_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root, state, target = _context(solution)
    path = content_path(root, workbook)
    if path not in selected_workbook_references(root):
        raise ValueError("UI qualification requires an explicitly selected Defender workbook")
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https" or parsed.hostname != "security.microsoft.com"
        or parsed.username or parsed.password or parsed.port not in (None, 443)
        or not parsed.path.strip("/")
        or any(key.casefold() in {
            "access_token", "token", "code", "sig", "signature", "client_secret",
        } for key, _ in parse_qsl(parsed.query))
    ):
        raise ValueError("workbook UI requires an exact reviewed Defender portal HTTPS URL")
    if (
        set(readiness_selectors) != {"tenant", "workbook", "ready"}
        or any(not value.strip() for value in readiness_selectors.values())
        or not background_activity_review.strip()
    ):
        raise ValueError("UI readiness selectors and background/service-worker review are required")
    required = {"pickers", "dependent-refresh", "filters", "drill-down", "reload", "layout", "conditional-visibility"}
    if (
        {step.get("kind") for step in steps} != required
        or any(not str(step.get("id") or "").strip() for step in steps)
        or len({step["id"] for step in steps}) != len(steps)
        or any(step.get("action") not in {"observe", "select", "reload", "drill-down"} for step in steps)
    ):
        raise ValueError("UI plan must include every reviewed check and only permitted non-edit actions")
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    plan = {
        "schemaVersion": "1.0.0",
        "operation": "workbook-ui-qualification",
        "runId": state["runId"],
        "target": target,
        "workbook": path.relative_to(root).as_posix(),
        "contentId": document["xdrMetadata"]["contentId"],
        "instanceId": document["xdrMetadata"]["instanceId"],
        "targetSha256": _sha(path.read_bytes()),
        "url": url,
        "readinessSelectors": readiness_selectors,
        "steps": steps,
        "backgroundActivityReview": background_activity_review,
        "saveEditAllowed": False,
        "browserWideNoWriteSandbox": False,
    }
    if browser_config is not None:
        from solution_manager.qualification.workbook_browser import validate_browser_config

        source = document["contentProvenance"]["source"]
        source_hash = _sha(content_path(root, source["path"]).read_bytes())
        if source_hash != source["sha256"]:
            raise ValueError("workbook UI qualification source provenance is stale")
        plan["schemaVersion"] = "1.1.0"
        plan["sourceSha256"] = source_hash
        plan["browserConfig"] = browser_config
        validate_browser_config(plan, browser_config)
    plan["planSha256"] = _seal(plan)
    return plan


def current_workbook_ui_plan(solution: str | Path, plan: dict[str, Any]) -> dict[str, Any]:
    return plan_workbook_ui(
        solution, workbook=plan["workbook"], url=plan["url"],
        readiness_selectors=plan["readinessSelectors"], steps=plan["steps"],
        background_activity_review=plan["backgroundActivityReview"],
        browser_config=plan.get("browserConfig"),
    )


def execute_workbook_ui(
    solution: str | Path, plan: dict[str, Any], *,
    read_consent: Callable[[], dict[str, Any]],
    browser_runner: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    from solution_manager.core.workflow import _run_writer_lock

    with _run_writer_lock(report_directory(solution) / "workbook-qualification-executor"):
        return _execute_workbook_ui(
            solution, plan, read_consent=read_consent, browser_runner=browser_runner,
        )


def _execute_workbook_ui(
    solution: str | Path, plan: dict[str, Any], *,
    read_consent: Callable[[], dict[str, Any]],
    browser_runner: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    current = current_workbook_ui_plan(solution, plan)
    if current != plan:
        raise ValueError("workbook UI plan is stale or has been edited")
    _check_consent(plan, read_consent())
    root = Path(solution).expanduser().resolve()
    if plan.get("browserConfig") is not None:
        from solution_manager.qualification.workbook_browser import prepare_private_browser_evidence

        prepare_private_browser_evidence(root)
    path = report_directory(root) / f"workbook-ui.{plan['contentId']}.json"
    running = {
        "schemaVersion": "1.0.0", "status": "running", "runId": plan["runId"],
        "target": plan["target"], "targetSha256": plan["targetSha256"],
        "plan": plan, "planSha256": plan["planSha256"],
        "execution": "approved-browser-capture", "checksComplete": False,
    }
    if path.is_file():
        prior = json.loads(path.read_text(encoding="utf-8-sig"))
        archive = path.with_name(f"{path.stem}.{_sha(path.read_bytes())}.json")
        write_json_artifact(root, archive, prior)
    write_json_artifact(root, path, running)
    capture = None
    try:
        capture = browser_runner(plan)
        _check_consent(plan, read_consent())
        _validate_ui_capture(plan, capture)
        if current != current_workbook_ui_plan(solution, plan):
            raise ValueError("workbook UI target changed during capture")
        approval = read_consent()
        _check_consent(plan, approval)
    except Exception as exc:
        diagnostics = {}
        if plan.get("browserConfig") is not None:
            from solution_manager.qualification.workbook_browser import BrowserQualificationError

            if isinstance(exc, BrowserQualificationError):
                diagnostics["diagnosticEvents"] = getattr(exc, "diagnostic_events", [])
        elif capture is not None:
            diagnostics["capture"] = capture
        write_json_artifact(root, path, {
            **running, "status": "failed",
            "error": "incomplete-or-failed-ui-capture",
            **diagnostics,
        })
        raise
    receipt = {
        "schemaVersion": "1.0.0",
        "status": "passed",
        "runId": plan["runId"],
        "target": plan["target"],
        "targetSha256": plan["targetSha256"],
        "plan": plan,
        "planSha256": plan["planSha256"],
        "approval": approval,
        "capture": capture,
        "execution": "approved-browser-capture",
        "queryErrors": capture["queryErrors"],
        "javascriptErrors": capture["javascriptErrors"],
        "checksComplete": True,
        "browserWideNoWriteSandbox": False,
    }
    write_json_artifact(root, path, receipt)
    return {"status": "passed", "reportPath": str(path), "queryQualification": "separate"}


def _validate_ui_capture(plan: dict[str, Any], capture: dict[str, Any]) -> None:
    if not isinstance(capture, dict):
        raise ValueError("workbook UI capture must be a complete result object")
    readiness = capture.get("readiness") or {}
    results = capture.get("steps")
    if (
        capture.get("target") != plan["target"] or capture.get("url") != plan["url"]
        or readiness.get("tenantId") != plan["target"]["tenantId"]
        or readiness.get("contentId") != plan["contentId"]
        or readiness.get("instanceId") != plan["instanceId"]
        or readiness.get("ready") is not True
        or capture.get("queryErrors") != [] or capture.get("javascriptErrors") != []
        or capture.get("saveEditObserved") is not False
        or capture.get("backgroundActivityReview") != plan["backgroundActivityReview"]
        or not isinstance(results, list) or len(results) != len(plan["steps"])
    ):
        raise ValueError("workbook UI capture has incomplete readiness, errors, or prohibited actions")
    for expected, actual in zip(plan["steps"], results, strict=True):
        if (
            not isinstance(actual, dict)
            or any(actual.get(key) != expected[key] for key in ("id", "kind"))
            or actual.get("status") != "passed"
            or not str(actual.get("evidence") or "").strip()
        ):
            raise ValueError("workbook UI capture has incomplete reviewed step evidence")
        if plan.get("browserConfig") is not None:
            from solution_manager.qualification.workbook_browser import validate_browser_step_proofs

            validate_browser_step_proofs(expected, actual)


def require_current_qualification(solution: str | Path, state: dict[str, Any]) -> None:
    if not enabled(state) or state["context"]["workflowProfile"] != "qualification":
        return
    root, current, target = _context(solution)
    if current["runId"] != state["runId"]:
        raise ValueError("workbook qualification run changed")
    for path in selected_workbook_references(root):
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        content_id = document["xdrMetadata"]["contentId"]
        query_path = report_directory(root) / f"workbook-queries.{content_id}.json"
        ui_path = report_directory(root) / f"workbook-ui.{content_id}.json"
        if not query_path.is_file() or not ui_path.is_file():
            raise ValueError("selected workbook query and UI qualification evidence is missing")
        query = json.loads(query_path.read_text(encoding="utf-8-sig"))
        plan = _current_plan(root, query["plan"])
        if query.get("status") != "passed" or query.get("planSha256") != plan["planSha256"]:
            raise ValueError("workbook query qualification evidence failed or is stale")
        _check_consent(plan, query["approval"])
        from solution_manager.migration._workbook_core.workbook_fixtures import assert_result

        results = query.get("results") or []
        if len(results) != len(plan["queries"]):
            raise ValueError("workbook query evidence has incomplete case coverage")
        for expected, actual in zip(plan["queries"], results, strict=True):
            if any(actual.get(key) != expected[key] for key in ("caseId", "side", "querySha256")):
                raise ValueError("workbook query evidence has mismatched case identities")
            if actual.get("status") != "passed" or actual.get("provider") != expected["side"]:
                raise ValueError("workbook query evidence has unsuccessful provider execution")
            try:
                assert_result(expected["expected"], actual["result"])
            except (AssertionError, KeyError, TypeError, ValueError) as exc:
                raise ValueError("workbook captured result evidence does not match the exact oracle") from exc
        ui = json.loads(ui_path.read_text(encoding="utf-8-sig"))
        if (
            ui.get("status") != "passed" or ui.get("runId") != state["runId"]
            or ui.get("target") != target or ui.get("targetSha256") != _sha(path.read_bytes())
            or ui.get("queryErrors") != [] or ui.get("javascriptErrors") != []
            or ui.get("checksComplete") is not True
            or ui.get("execution") != "approved-browser-capture"
        ):
            raise ValueError("workbook UI qualification remains failed, stale, or unverified")
        ui_plan = current_workbook_ui_plan(root, ui["plan"])
        if ui_plan != ui["plan"] or ui.get("planSha256") != ui_plan["planSha256"]:
            raise ValueError("workbook UI qualification plan is stale or edited")
        _check_consent(ui_plan, ui["approval"])
        _validate_ui_capture(ui_plan, ui["capture"])
