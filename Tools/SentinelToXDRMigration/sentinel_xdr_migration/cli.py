from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from .converter import (
    configure_logging,
    convert_solution,
    inspect_solution,
    runtime_validation_plan,
    validate_solution,
)
from .onboarding import configure_workspace, doctor, setup
from .packaging import package_solution_v4
from .deployment import deploy_solution, setup_deployment_authentication
from .analytic_deployment import deploy_analytic_rules
from .alert_parity import (
    abort_alert_parity,
    complete_alert_parity,
    start_alert_parity,
    start_alert_parity_batch,
)
from .runtime import record_runtime_validation, validate_advanced_hunting
from .solution_report import build_solution_report
from .workflow import (
    STAGES,
    WORKFLOW_PROFILES,
    complete_workflow_stage,
    initialize_workflow,
    next_workflow_stage,
    start_workflow_stage,
    workflow_status,
)

SUPPORTED_PYTHON_MIN = (3, 11)
SUPPORTED_PYTHON_MAX_EXCLUSIVE = (3, 13)


def _print(value: dict) -> None:
    print(json.dumps(value, indent=2))


def _key_values(values: list[str] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values or []:
        key, separator, item = value.partition("=")
        if not separator or not key.strip() or not item.strip():
            raise ValueError(f"expected NAME=VALUE, received: {value}")
        if key in result:
            raise ValueError(f"duplicate artifact name: {key}")
        result[key] = item
    return result


def main(argv: list[str] | None = None) -> int:
    if not (
        SUPPORTED_PYTHON_MIN
        <= sys.version_info[:2]
        < SUPPORTED_PYTHON_MAX_EXCLUSIVE
    ):
        print(
            "sentinel-xdr-migration requires Python 3.11 or 3.12. "
            "Install or select a supported interpreter; do not modify toolkit "
            "source to compensate for the local Python version.",
            file=sys.stderr,
        )
        return 2

    parser = argparse.ArgumentParser(
        description="Convert Microsoft Sentinel analytic rules into XDR Custom Detection YAML."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in (
        "inspect",
        "convert",
        "validate",
        "validation-plan",
        "validate-advanced-hunting",
    ):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--solution", required=True)
        if command == "convert":
            subparser.add_argument("--overwrite", action="store_true")
            subparser.add_argument("--config")
    setup_parser = subparsers.add_parser(
        "setup", help="Initialize the toolkit and optionally launch guided authentication."
    )
    setup_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Inspect and initialize without opening authentication prompts.",
    )
    setup_parser.add_argument("--tenant-id")
    setup_parser.add_argument("--workspace-id")
    setup_parser.add_argument(
        "--hunting-auth-method",
        choices=["device-code", "browser"],
        default="device-code",
        help="Interactive authentication method for Microsoft Graph.",
    )
    setup_parser.add_argument("--skip-sentinel-auth", action="store_true")
    setup_parser.add_argument("--skip-hunting-auth", action="store_true")
    subparsers.add_parser("doctor", help="Report setup and runtime readiness.")
    workspace_config = subparsers.add_parser(
        "configure-workspace",
        help="Persist one approved workspace for reuse across solution workflows.",
    )
    workspace_config.add_argument("--workspace-resource-id", required=True)
    workspace_config.add_argument("--workspace-customer-id")
    deployment_setup = subparsers.add_parser(
        "setup-deployment",
        help="Authenticate for Microsoft Graph Custom Detection deployment.",
    )
    deployment_setup.add_argument("--tenant-id")
    deployment_setup.add_argument(
        "--auth-method",
        choices=["azure-cli", "device-code", "browser"],
        default="azure-cli",
    )
    deployment = subparsers.add_parser(
        "deploy",
        help="Create or update generated Custom Detections through Microsoft Graph beta.",
    )
    deployment.add_argument("--solution", required=True)
    analytic_deployment = subparsers.add_parser(
        "deploy-analytic-rules",
        help="Create or update source Sentinel analytic rules through Azure Resource Manager.",
    )
    analytic_deployment.add_argument("--solution", required=True)
    analytic_deployment.add_argument("--workspace-resource-id", required=True)
    parity_start = subparsers.add_parser(
        "start-alert-parity",
        help="Enable disabled AR/CD pairs, ingest a marked mock payload, and emit capture queries.",
    )
    parity_start.add_argument("--solution", required=True)
    parity_start.add_argument("--workspace-resource-id", required=True)
    parity_start.add_argument("--contract", required=True)
    parity_start.add_argument("--payload", required=True)
    parity_start.add_argument("--scenario-marker", required=True)
    parity_start.add_argument(
        "--expected-match-key",
        action="append",
        dest="expected_match_keys",
        help="Exact malicious alert match key; repeat for multiple expected alerts. Defaults to the scenario marker.",
    )
    parity_start.add_argument(
        "--detection",
        action="append",
        dest="detections",
        help="Detection filename or stem to validate; repeat to select multiple.",
    )
    parity_complete = subparsers.add_parser(
        "complete-alert-parity",
        help="Compare normalized AR/CD alerts strictly and disable every test rule.",
    )
    parity_complete.add_argument("--solution", required=True)
    parity_complete.add_argument("--results", required=True)
    parity_batch = subparsers.add_parser(
        "start-alert-parity-batch",
        help="Enable all reviewed AR/CD pairs and ingest one fixture per detection.",
    )
    parity_batch.add_argument("--solution", required=True)
    parity_batch.add_argument("--workspace-resource-id", required=True)
    parity_batch.add_argument("--plan", required=True)
    parity_abort = subparsers.add_parser(
        "abort-alert-parity",
        help="Disable every rule associated with an active parity run.",
    )
    parity_abort.add_argument("--solution", required=True)
    report_parser = subparsers.add_parser(
        "solution-report",
        help="Build one consolidated per-rule AR/CD migration report.",
    )
    report_parser.add_argument("--solution", required=True)
    report_parser.add_argument(
        "--ingestion-report",
        action="append",
        dest="ingestion_reports",
        help="Ingestion report JSON to include; repeat for multiple streams.",
    )
    record_parser = subparsers.add_parser(
        "record-runtime-validation",
        help="Normalize and report results produced by an external runtime provider.",
    )
    record_parser.add_argument("--solution", required=True)
    record_parser.add_argument(
        "--provider",
        required=True,
        choices=["triage-mcp", "log-analytics-cli"],
    )
    record_parser.add_argument("--results", required=True)
    package_v4 = subparsers.add_parser(
        "package-v4",
        help="Package the solution through the V4 XDR-aware local packager.",
    )
    package_v4.add_argument("--solution", required=True)
    package_v4.add_argument(
        "--version-bump",
        required=True,
        choices=["none", "patch", "minor", "major"],
    )
    workflow_init = subparsers.add_parser(
        "workflow-init",
        help="Create or resume the gated end-to-end migration workflow state.",
    )
    workflow_init.add_argument("--solution", required=True)
    workflow_init.add_argument("--workspace-resource-id")
    workflow_init.add_argument(
        "--version-bump",
        choices=["none", "patch", "minor", "major"],
    )
    workflow_init.add_argument(
        "--workflow-profile",
        required=True,
        choices=WORKFLOW_PROFILES,
        help="Explicitly select authoring or qualification before initialization.",
    )
    workflow_status_parser = subparsers.add_parser(
        "workflow-status",
        help="Show the persisted end-to-end migration workflow state.",
    )
    workflow_status_parser.add_argument("--solution", required=True)
    workflow_next = subparsers.add_parser(
        "workflow-next",
        help="Return the next stage whose dependencies have passed.",
    )
    workflow_next.add_argument("--solution", required=True)
    workflow_start = subparsers.add_parser(
        "workflow-start-stage",
        help="Start or retry one gated workflow stage.",
    )
    workflow_start.add_argument("--solution", required=True)
    workflow_start.add_argument("--stage", required=True, choices=STAGES)
    workflow_complete = subparsers.add_parser(
        "workflow-complete-stage",
        help="Persist the terminal result and evidence for a running stage.",
    )
    workflow_complete.add_argument("--solution", required=True)
    workflow_complete.add_argument("--stage", required=True, choices=STAGES)
    workflow_complete.add_argument(
        "--status",
        required=True,
        choices=["passed", "failed", "blocked"],
    )
    workflow_complete.add_argument("--message")
    workflow_complete.add_argument(
        "--artifact",
        action="append",
        help="Stage artifact as NAME=VALUE; repeat for multiple artifacts.",
    )
    workflow_complete.add_argument(
        "--evidence",
        action="append",
        help="Evidence path or reference; repeat for multiple values.",
    )

    args = parser.parse_args(argv)
    tool_root = Path(__file__).resolve().parents[1]
    configure_logging(tool_root)

    try:
        if args.command == "setup":
            result = setup(
                interactive=not args.non_interactive,
                tenant_id=args.tenant_id,
                workspace_id=args.workspace_id,
                skip_sentinel_auth=args.skip_sentinel_auth,
                skip_hunting_auth=args.skip_hunting_auth,
                hunting_auth_method=args.hunting_auth_method,
            )
        elif args.command == "doctor":
            result = doctor()
        elif args.command == "configure-workspace":
            result = configure_workspace(
                args.workspace_resource_id,
                workspace_customer_id=args.workspace_customer_id,
            )
        elif args.command == "setup-deployment":
            result = setup_deployment_authentication(
                tenant_id=args.tenant_id,
                auth_method=args.auth_method,
            )
        elif args.command == "deploy":
            result = deploy_solution(args.solution)
        elif args.command == "deploy-analytic-rules":
            result = deploy_analytic_rules(
                args.solution,
                workspace_resource_id=args.workspace_resource_id,
            )
        elif args.command == "start-alert-parity":
            result = start_alert_parity(
                args.solution,
                workspace_resource_id=args.workspace_resource_id,
                contract=args.contract,
                payload=args.payload,
                scenario_marker=args.scenario_marker,
                expected_match_keys=args.expected_match_keys,
                detections=args.detections,
            )
        elif args.command == "complete-alert-parity":
            result = complete_alert_parity(
                args.solution,
                results_path=args.results,
            )
        elif args.command == "start-alert-parity-batch":
            result = start_alert_parity_batch(
                args.solution,
                workspace_resource_id=args.workspace_resource_id,
                plan_path=args.plan,
            )
        elif args.command == "abort-alert-parity":
            result = abort_alert_parity(args.solution)
        elif args.command == "solution-report":
            result = build_solution_report(
                args.solution,
                ingestion_reports=args.ingestion_reports,
            )
        elif args.command == "package-v4":
            result = package_solution_v4(
                args.solution,
                version_bump=args.version_bump,
            )
        elif args.command == "inspect":
            result = inspect_solution(args.solution)
        elif args.command == "convert":
            result = convert_solution(
                args.solution, overwrite=args.overwrite, config_path=args.config
            )
        elif args.command == "validate":
            result = validate_solution(args.solution)
        elif args.command == "validate-advanced-hunting":
            result = validate_advanced_hunting(args.solution)
        elif args.command == "record-runtime-validation":
            result = record_runtime_validation(
                args.solution,
                provider=args.provider,
                results_path=args.results,
            )
        elif args.command == "workflow-init":
            result = initialize_workflow(
                args.solution,
                workspace_resource_id=args.workspace_resource_id,
                version_bump=args.version_bump,
                workflow_profile=args.workflow_profile,
            )
        elif args.command == "workflow-status":
            result = workflow_status(args.solution)
        elif args.command == "workflow-next":
            result = next_workflow_stage(args.solution)
        elif args.command == "workflow-start-stage":
            result = start_workflow_stage(args.solution, args.stage)
        elif args.command == "workflow-complete-stage":
            result = complete_workflow_stage(
                args.solution,
                args.stage,
                status=args.status,
                message=args.message,
                artifacts=_key_values(args.artifact),
                evidence=args.evidence,
            )
        else:
            result = runtime_validation_plan(args.solution)
    except (OSError, RuntimeError, ValueError, yaml.YAMLError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    _print(result)
    if args.command == "validate" and result["invalid"]:
        return 1
    if args.command == "validate-advanced-hunting" and (
        result["invalid"] or result["blocked"]
    ):
        return 1
    if args.command == "record-runtime-validation" and (
        result["invalid"] or result["blocked"]
    ):
        return 1
    if args.command in ("deploy", "deploy-analytic-rules") and result["failed"]:
        return 1
    if args.command == "complete-alert-parity" and result["status"] != "passed":
        return 1
    if args.command == "abort-alert-parity" and result["status"] != "aborted":
        return 1
    if args.command == "convert" and (result["needsReview"] or result["conflicts"]):
        return 1
    if (
        args.command == "workflow-complete-stage"
        and result["status"] != "passed"
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
