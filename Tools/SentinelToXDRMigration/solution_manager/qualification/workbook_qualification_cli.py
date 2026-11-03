from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from solution_manager.qualification import workbook_qualification as qualification
from solution_manager.core.artifacts import report_directory, write_json_artifact
from solution_manager.core.content_paths import content_path


def register_workbook_qualification_commands(subparsers) -> tuple[str, ...]:
    names = (
        "workbook-query-plan", "workbook-query-review", "workbook-query-revoke",
        "workbook-query-execute", "workbook-ui-plan", "workbook-ui-review",
        "workbook-ui-revoke", "workbook-ui-import", "workbook-ui-execute",
    )
    parsers = {}
    for name in names:
        parser = subparsers.add_parser(name, help="Qualification-only workbook read planning, approval, or evidence.")
        parser.add_argument("--solution", required=True)
        parsers[name] = parser
    for name in ("workbook-query-plan", "workbook-ui-plan"):
        parsers[name].add_argument("--workbook", required=True)
    parsers["workbook-query-plan"].add_argument("--clock", required=True, help="Reviewed fixed UTC fixture clock.")
    parsers["workbook-query-plan"].add_argument("--seed", type=int, default=42)
    parsers["workbook-query-plan"].add_argument("--scale", type=int, default=1)
    parsers["workbook-query-plan"].add_argument("--recipe", default="syslog-operational-v1")
    parsers["workbook-ui-plan"].add_argument("--url", required=True)
    parsers["workbook-ui-plan"].add_argument("--readiness-selectors", required=True, help="Local JSON with reviewed tenant/workbook/ready selectors.")
    parsers["workbook-ui-plan"].add_argument("--steps", required=True, help="Local JSON array of every reviewed non-edit UI check.")
    parsers["workbook-ui-plan"].add_argument("--background-activity-review", required=True)
    parsers["workbook-ui-plan"].add_argument(
        "--browser-config", help="Optional local JSON with exact reviewed DOM assertions, private session hash and network allowlists.",
    )
    parsers["workbook-ui-execute"].add_argument("--plan-sha256", required=True)
    parsers["workbook-ui-execute"].add_argument(
        "--storage-state", required=True, help="Existing owner-only Playwright storage state; never authenticates or exports it.",
    )
    for name in names:
        if name not in ("workbook-query-plan", "workbook-ui-plan"):
            parsers[name].add_argument("--plan", required=True, help="Exact selected-run plan JSON path, relative to the solution.")
    for name in ("workbook-query-review", "workbook-ui-review", "workbook-ui-import"):
        parsers[name].add_argument("--plan-sha256", required=True)
    parsers["workbook-query-execute"].add_argument("--plan-sha256", required=True)
    parsers["workbook-query-execute"].add_argument("--state-dir")
    parsers["workbook-query-execute"].add_argument("--family-timeout-seconds", type=int, default=1800)
    for name in (
        "workbook-query-review", "workbook-ui-review",
        "workbook-query-revoke", "workbook-ui-revoke", "workbook-ui-import",
    ):
        parsers[name].add_argument("--actor", required=True)
        parsers[name].add_argument("--reference", required=True)
    for name in ("workbook-query-review", "workbook-ui-review"):
        parsers[name].add_argument("--decision", required=True, choices=("approved", "declined"))
    parsers["workbook-ui-import"].add_argument(
        "--evidence", required=True,
        help="Reviewed complete external browser capture JSON; this command does not launch a browser.",
    )
    return names


def _family(plan: dict[str, Any]) -> str:
    if plan.get("operation") == "workbook-query-qualification":
        return "workbook-queries"
    if plan.get("operation") == "workbook-ui-qualification":
        return "workbook-ui"
    raise ValueError("unsupported workbook qualification operation")


def _read_plan(solution: str | Path, reference: str, *, ui: bool) -> dict[str, Any]:
    root, state, _ = qualification._context(solution)
    path = content_path(root, reference)
    if path.parent != report_directory(root):
        raise ValueError("workbook qualification plans must belong to the exact selected run")
    plan = json.loads(path.read_text(encoding="utf-8-sig"))
    expected_operation = "workbook-ui-qualification" if ui else "workbook-query-qualification"
    if plan.get("operation") != expected_operation or plan.get("runId") != state["runId"]:
        raise ValueError("workbook qualification plan has the wrong operation or run")
    if ui:
        current = qualification.current_workbook_ui_plan(root, plan)
        if current != plan:
            raise ValueError("workbook UI plan is stale or edited")
    else:
        qualification._current_plan(root, plan)
    return plan


def _consent_path(solution: str | Path, plan: dict[str, Any]) -> Path:
    return report_directory(solution) / f"{_family(plan)}.consent.{plan['contentId']}.json"


def _read_consent(solution: str | Path, plan: dict[str, Any]) -> dict[str, Any]:
    path = _consent_path(solution, plan)
    if not path.is_file():
        raise ValueError("explicit workbook qualification consent is missing")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dispatch_workbook_qualification(args) -> dict[str, Any]:
    root = Path(args.solution).expanduser().resolve()
    ui = args.command.startswith("workbook-ui-")
    if args.command == "workbook-query-plan":
        plan = qualification.plan_workbook_queries(
            root, workbook=args.workbook, clock=args.clock,
            seed=args.seed, scale=args.scale, recipe=args.recipe,
        )
    elif args.command == "workbook-ui-plan":
        selectors = json.loads(content_path(root, args.readiness_selectors).read_text(encoding="utf-8-sig"))
        steps = json.loads(content_path(root, args.steps).read_text(encoding="utf-8-sig"))
        plan = qualification.plan_workbook_ui(
            root, workbook=args.workbook, url=args.url, readiness_selectors=selectors,
            steps=steps, background_activity_review=args.background_activity_review,
            browser_config=(
                json.loads(content_path(root, args.browser_config).read_text(encoding="utf-8-sig"))
                if args.browser_config else None
            ),
        )
    else:
        plan = _read_plan(root, args.plan, ui=ui)
        if args.command.endswith("-revoke"):
            if not args.actor.strip() or not args.reference.strip():
                raise ValueError("withdrawal requires an actor and reference")
            approval = _read_consent(root, plan)
            approval.update({
                "withdrawn": True,
                "withdrawal": {"actor": args.actor, "reference": args.reference},
            })
            path = _consent_path(root, plan)
            write_json_artifact(root, path, approval)
            return {"status": "withdrawn", "consentPath": path.relative_to(root).as_posix()}
        if plan["planSha256"] != args.plan_sha256:
            raise ValueError("qualification requires the exact reviewed current plan hash")
        if args.command.endswith("-review"):
            approval = qualification.review_workbook_query_consent(
                plan, actor=args.actor, reference=args.reference,
                approved=args.decision == "approved",
            )
            path = _consent_path(root, plan)
            write_json_artifact(root, path, approval)
            return {
                "status": args.decision, "planSha256": plan["planSha256"],
                "consentPath": path.relative_to(root).as_posix(),
            }
        if args.command == "workbook-query-execute":
            return qualification.execute_workbook_queries(
                root, plan, read_consent=lambda: _read_consent(root, plan),
                providers=qualification.default_query_providers(state_dir=args.state_dir),
                family_timeout_seconds=args.family_timeout_seconds,
            )
        if args.command == "workbook-ui-execute":
            from solution_manager.qualification.workbook_browser import execute_workbook_browser

            result = execute_workbook_browser(
                root, plan, read_consent=lambda: _read_consent(root, plan),
                storage_state=args.storage_state,
            )
            return {
                **result, "browserExecution": "playwright-dom-v1",
                "armContentHubAcceptance": "separate; not proven by UI capture",
            }
        if args.command == "workbook-ui-import":
            if not args.actor.strip() or not args.reference.strip():
                raise ValueError("external browser capture review requires an actor and reference")
            proof = json.loads(content_path(root, args.evidence).read_text(encoding="utf-8-sig"))
            proof["captureReview"] = {"actor": args.actor, "reference": args.reference}
            result = qualification.execute_workbook_ui(
                root, plan, read_consent=lambda: _read_consent(root, plan),
                browser_runner=lambda _: proof,
            )
            return {**result, "browserExecution": "external-reviewed-capture; not executed by this command"}
        raise ValueError("unsupported workbook qualification command")
    path = report_directory(root) / f"{_family(plan)}.plan.{plan['contentId']}.json"
    write_json_artifact(root, path, plan)
    return {
        "status": "planned", "operation": plan["operation"],
        "planPath": path.relative_to(root).as_posix(), "planSha256": plan["planSha256"],
        "target": plan["target"], "workbook": plan["workbook"],
        "queryCount": len(plan.get("queries") or []),
        "uiStepCount": len(plan.get("steps") or []),
        "execution": "not-run", "ingestion": "not-run",
    }
