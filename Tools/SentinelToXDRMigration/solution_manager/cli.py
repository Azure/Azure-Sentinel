from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from solution_manager.migration.converter import (
    configure_logging,
    convert_solution,
    inspect_solution,
    runtime_validation_plan,
    validate_solution,
)
from solution_manager.core.artifacts import migrate_reports, select_run, reset_run_selection, list_runs, existing_artifact_path
from solution_manager.reporting.evidence import export_evidence
from solution_manager.authoring.dependencies import plan_solution_dependencies
from solution_manager.core.budget import (
    DEFAULT_POLICY,
    budget_summary,
    extend_budget,
    reconcile_legacy_usage,
    reconcile_pending_operation,
    set_observation_deadline,
)
from solution_manager.core.onboarding import configure_workspace, doctor, setup
from solution_manager.qualification.deployment import deploy_solution, setup_deployment_authentication
from solution_manager.qualification.deployment_planning import persist_deployment_plan, record_planning_consent
from solution_manager.qualification.graph_readiness import preflight_deployment
from solution_manager.qualification.analytic_deployment import deploy_analytic_rules
from solution_manager.qualification.arm_acceptance import (
    execute_arm_template_acceptance_batch,
    plan_arm_template_acceptance_batch,
)
from solution_manager.qualification.alert_parity import (
    abort_alert_parity,
    complete_alert_parity,
    start_alert_parity,
    start_alert_parity_batch,
)
from solution_manager.qualification.runtime import (
    record_runtime_validation,
    validate_advanced_hunting,
    validate_sentinel_sdk,
)
from solution_manager.qualification.runtime_consent import (
    SOURCE_PROVIDERS,
    confirm_primary_lab_setting,
    persist_runtime_query_plan,
    record_runtime_query_consent,
    revoke_runtime_query_consent,
    runtime_query_consent_status,
)
from solution_manager.reporting.solution_report import build_solution_report
from solution_manager.qualification.pr_check_runner import (
    evaluate_solution_pr_qualification,
)
from solution_manager.reporting.pr_qualification_report import (
    write_pr_qualification_reports,
)
from solution_manager.core.target_context import diagnose_target, repair_target, require_locked_target
from solution_manager.core.target_config import resolve_qualification_target
from solution_manager.core.workflow import (
    STAGES,
    WORKFLOW_PROFILES,
    build_consolidated_review_packet,
    build_migration_status_reminder,
    claim_execution_ownership,
    complete_workflow_stage,
    forward_explicit_approval,
    initialize_workflow,
    next_workflow_stage,
    read_authoring_contract,
    release_execution_ownership,
    package_workflow_v3_1,
    plan_new_package_release,
    plan_release_notes_refresh,
    plan_same_version_content_rebuild,
    recover_conversion_evidence,
    refresh_yolo_authoring,
    run_yolo_authoring,
    start_workflow_stage,
    verify_forwarded_approval,
    verify_same_version_content_rebuild,
    workflow_status,
)
from solution_manager.packaging.packaging_selection import (
    apply_package_selection,
    create_package_selection_plan,
)
from solution_manager.core.coordinator import (
    acknowledge_outbox,
    claim as coordinator_claim,
    enroll as coordinator_enroll,
    heartbeat as coordinator_heartbeat,
    reconcile as coordinator_reconcile,
    record_event as coordinator_record_event,
    status as coordinator_status,
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


def _json_object_arg(raw: str | None, *, flag_name: str) -> dict:
    if raw is None:
        return {}
    candidate = Path(raw).expanduser()
    try:
        text = (
            candidate.read_text(encoding="utf-8-sig")
            if candidate.is_file()
            else raw
        )
        parsed = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON object for {flag_name}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{flag_name} must decode to a JSON object")
    return parsed


def _package_batch_members(values: list[str]) -> list[dict[str, str]]:
    members: list[dict[str, str]] = []
    for value in values:
        solution_path, separator, run_id = value.rpartition("::")
        if not separator or not solution_path.strip() or not run_id.strip():
            raise ValueError(
                f"expected --member SOLUTION_PATH::RUN_ID, received: {value}"
            )
        members.append(
            {"solution": solution_path.strip(), "runId": run_id.strip()}
        )
    return members


def _require_explicit_authoring_run(solution: str, run_id: str | None) -> dict[str, Any]:
    state = workflow_status(solution)
    if (
        state.get("context", {}).get("workflowProfile") == "authoring"
        and not run_id
    ):
        raise ValueError(
            "Authoring Advanced Hunting requires an explicit --run-id; "
            "no run is inferred"
        )
    return state


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
    for command in ("workbook-publication-plan", "workbook-publication-clean", "workbook-publication-validate"):
        publication = subparsers.add_parser(command, help="Clean public workbook; retain local authoring evidence.")
        publication.add_argument("--solution", required=True)
        publication.add_argument("--content", required=True)
        if command.endswith("-clean"):
            publication.add_argument("--expected-sha256", required=True)
            publication.add_argument("--review", required=True)
        if command.endswith("-validate"):
            publication.add_argument("--mode", choices=("structural", "authoring"), required=True)
    for update_command in ("workbook-update-plan", "workbook-update-review", "workbook-update-apply"):
        update_parser = subparsers.add_parser(
            update_command, help="Offline explicit post-import edits; preserve historical receipts.")
        update_parser.add_argument("--solution", required=True)
        update_parser.add_argument("--content", required=True, help="Authored XDR Workbooks/ relative JSON path.")
        update_parser.add_argument("--baseline", required=True, help="External original reviewed authored artifact.")
        if update_command != "workbook-update-plan":
            update_parser.add_argument("--review", required=True)
    for native_command in ("native-workbook-plan", "native-workbook-review",
                           "native-workbook-import", "native-workbook-validate"):
        native_parser = subparsers.add_parser(
            native_command, help="Offline native AH authoring; never conversion or runtime qualification.")
        native_parser.add_argument("--solution", required=True)
        if native_command != "native-workbook-validate":
            native_parser.add_argument("--source", required=True, help="Workbook Sources/Native/ solution-relative JSON.")
        if native_command in ("native-workbook-review", "native-workbook-import"):
            native_parser.add_argument("--review", required=True, help="Complete reviewed current native plan JSON.")
    dependency_parser = subparsers.add_parser(
        "dependency-plan",
        help="Propose YAML dependencies offline, or verify them from approved lab metadata.",
    )
    dependency_parser.add_argument("--solution", required=True)
    dependency_parser.add_argument("--results", help="Exact-query-bound successful LA metadata results.")
    dependency_parser.add_argument("--workspace-id", help="Explicitly approved lab workspace customer ID.")
    workbook_dependencies = subparsers.add_parser(
        "workbook-dependency-plan", help="Propose offline workbook gaps; import separately approved exact-query lab metadata.")
    workbook_dependencies.add_argument("--solution", required=True)
    workbook_dependencies.add_argument("--results")
    workbook_dependencies.add_argument("--workspace-id")
    workbook_review = subparsers.add_parser(
        "workbook-review", help="Apply complete hash-bound accept/change/defer decisions to run-local config and receipt.")
    for option in ("solution", "plan", "decisions", "plan-sha256", "actor", "reference", "output-dir"):
        workbook_review.add_argument("--" + option, required=True)
    for review_cmd in ("review-packet", "consolidated-review-plan"):
        review_packet_parser = subparsers.add_parser(
            review_cmd,
            help=(
                "Build one consolidated, hash-bound review packet covering outstanding "
                "detection and workbook review items."
            ),
        )
        review_packet_parser.add_argument("--solution", required=True)
        review_packet_parser.add_argument(
            "--results",
            help="Exact-query-bound successful LA metadata results for detection dependencies.",
        )
        review_packet_parser.add_argument(
            "--workbook-results",
            help="Exact-query-bound successful LA metadata results for workbook dependencies.",
        )
        review_packet_parser.add_argument(
            "--workspace-id",
            help="Explicitly approved lab workspace customer ID.",
        )
        review_packet_parser.add_argument(
            "--rule",
            action="append",
            dest="rule_selectors",
            help="Optional rule ID, filename, or stem filter; repeat to select multiple.",
        )
        review_packet_parser.add_argument(
            "--output",
            help="Optional path to write the consolidated review packet JSON.",
        )
    migration = subparsers.add_parser("migrate-reports", help="Plan a non-destructive copy of legacy reports into solution Logs.")
    migration.add_argument("--solution", required=True)
    migration.add_argument("--apply", action="store_true", help="Copy after reviewing the dry-run; originals are preserved.")
    evidence = subparsers.add_parser("export-evidence", help="Explicitly export immutable, curated local PR evidence; no cloud writes.")
    evidence.add_argument("--solution", required=True)
    evidence.add_argument(
        "--include-authoring-contract",
        action="store_true",
        help="Include the selected run's validated, immutable YOLO contract projection.",
    )
    for command in (
        "inspect",
        "convert",
        "validate",
        "validation-plan",
        "validate-advanced-hunting",
        "validate-sentinel-sdk",
    ):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--solution", required=True)
        if command == "convert":
            subparser.add_argument("--overwrite", action="store_true")
            subparser.add_argument("--overwrite-workbooks", action="store_true",
                                   help="Replace only unchanged hash-bound managed workbook drafts; never overwrite detections.")
            subparser.add_argument("--config")
            subparser.add_argument(
                "--rule-id", action="append",
                help="Convert exactly one source template GUID; does not establish solution readiness.",
            )
        if command == "validate-advanced-hunting":
            subparser.add_argument(
                "--provider-gap-evidence",
                help="JSON evidence for a complete Graph fallback after a Triage MCP provider failure.",
            )
        if command == "validate-sentinel-sdk":
            subparser.add_argument(
                "--request-timeout-seconds",
                type=int,
                default=90,
                help="Maximum server/network timeout per Logs query (1-600 seconds).",
            )
            subparser.add_argument(
                "--family-timeout-seconds",
                type=int,
                default=1800,
                help="Maximum elapsed budget for this complete source-query family (1-21600 seconds).",
            )
            subparser.add_argument(
                "--provider-gap-evidence",
                help="JSON evidence for the complete Azure Monitor SDK fallback after a Triage MCP provider failure.",
            )
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
        "--hunting-client-id",
        help="Public delegated Graph client ID for Advanced Hunting; the built-in client remains the default.",
    )
    setup_parser.add_argument(
        "--azure-config-dir",
        help="Explicitly select and persist an isolated Azure CLI profile for this target.",
    )
    setup_parser.add_argument(
        "--hunting-auth-method",
        choices=["device-code", "browser"],
        default="device-code",
        help="Interactive authentication method for Microsoft Graph.",
    )
    setup_parser.add_argument("--skip-sentinel-auth", action="store_true")
    setup_parser.add_argument("--skip-hunting-auth", action="store_true")
    doctor_parser = subparsers.add_parser(
        "doctor", help="Report setup and runtime readiness."
    )
    doctor_parser.add_argument(
        "--solution",
        help="Also inspect this solution's local .env Qualification target.",
    )
    workspace_config = subparsers.add_parser(
        "configure-workspace",
        help="Persist one approved workspace for reuse across solution workflows.",
    )
    workspace_config.add_argument("--workspace-resource-id", required=True)
    workspace_config.add_argument("--workspace-customer-id")
    workspace_config.add_argument("--tenant-id")
    workspace_config.add_argument("--subscription-id")
    target_diagnostics = subparsers.add_parser(
        "qualification-diagnose",
        help="Diagnose the one locked Qualification target without broad discovery.",
    )
    target_diagnostics.add_argument("--solution", required=True)
    target_repair = subparsers.add_parser(
        "qualification-repair-target",
        help="Apply the exact target correction proposed by current diagnostics.",
    )
    target_repair.add_argument("--solution", required=True)
    target_repair.add_argument("--approve-target-update", action="store_true")
    deployment_setup = subparsers.add_parser(
        "setup-deployment",
        help="Authenticate for Microsoft Graph Custom Detection deployment.",
    )
    deployment_setup.add_argument("--tenant-id")
    deployment_setup.add_argument("--solution", required=True)
    deployment_setup.add_argument(
        "--custom-detection-client-id",
        help="Public delegated Graph client ID for Custom Detection; the built-in client remains the default.",
    )
    deployment_setup.add_argument(
        "--azure-config-dir",
        help="Explicitly select and persist an isolated Azure CLI profile for this target.",
    )
    app_registration_auth = subparsers.add_parser(
        "setup-app-registration-auth",
        help="Explicitly authenticate with the least-privilege app-registration bootstrap scope.",
    )
    app_registration_auth.add_argument("--solution", required=True)
    app_registration_auth.add_argument(
        "--auth-method",
        choices=["device-code", "browser"],
        default="device-code",
    )
    app_registration_auth.add_argument(
        "--bootstrap-client-id",
        help="Existing public Graph client ID already able to request the bootstrap scopes; defaults to the built-in client.",
    )
    app_readback_auth = subparsers.add_parser(
        "setup-app-readback-auth",
        help="Set up the separate browser-only, GET-only delegated app verification credential.",
    )
    app_readback_auth.add_argument("--solution", required=True)
    app_readback_auth.add_argument(
        "--readback-client-id",
        required=True,
        help=(
            "Existing approved public Graph client ID; readback uses a separate "
            "auth purpose, record, and token cache."
        ),
    )
    app_readback = subparsers.add_parser(
        "verify-delegated-app-readback",
        help="Read-only reconciliation for the exact approved owned application; performs GET requests only.",
    )
    app_readback.add_argument("--solution", required=True)
    app_readback_scope_diagnostic = subparsers.add_parser(
        "diagnose-app-readback-scopes",
        help="Report required and extra cached readback-token scope names; makes no Microsoft Graph resource requests.",
    )
    app_readback_scope_diagnostic.add_argument("--solution", required=True)
    app_registration_plan = subparsers.add_parser(
        "plan-delegated-app-registration",
        help="Show the exact single-tenant delegated desktop-app plan; performs no cloud calls.",
    )
    app_registration_plan.add_argument("--solution", required=True)
    app_registration_plan.add_argument(
        "--app-display-name",
        help="Exact application display name to bind into the reviewed plan; defaults to the legacy name.",
    )
    app_registration = subparsers.add_parser(
        "register-delegated-app",
        help="Create at most one explicitly approved delegated Graph desktop app; grants no consent.",
    )
    app_registration.add_argument("--solution", required=True)
    app_registration.add_argument(
        "--app-display-name",
        help="Exact application display name bound into the reviewed plan; defaults to the legacy name.",
    )
    app_registration.add_argument("--expected-plan-sha256", required=True)
    app_registration.add_argument(
        "--approve-exact-app-registration",
        action="store_true",
        help="Approve only the application registration bound to the supplied plan hash.",
    )
    app_permission_plan = subparsers.add_parser(
        "plan-delegated-app-permission-update",
        help="Show the exact manual permission-addition plan; performs no cloud calls.",
    )
    app_permission_plan.add_argument("--solution", required=True)
    app_permission_verify = subparsers.add_parser(
        "verify-delegated-app-permission-update",
        help="Verify the reviewed manual permission update; performs GET requests only.",
    )
    app_permission_verify.add_argument("--solution", required=True)
    app_permission_verify.add_argument("--expected-plan-sha256", required=True)
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
    deployment_preflight = subparsers.add_parser(
        "preflight-deployment",
        help=(
            "Run local Graph readiness plus independent read-only DCR, ingestion, "
            "query, and deployment permission diagnostics."
        ),
    )
    deployment_preflight.add_argument("--solution", required=True)
    deployment_preflight.add_argument(
        "--auth-method",
        choices=["azure-cli", "device-code", "browser"],
        help=(
            "Use this existing cached credential method only; authentication "
            "is never started by preflight."
        ),
    )
    deployment_plan = subparsers.add_parser(
        "plan-deployment",
        help="Persist a deterministic local Qualification deployment-scope plan; performs no cloud calls.",
    )
    deployment_plan.add_argument("--solution", required=True)
    runtime_query_plan = subparsers.add_parser(
        "plan-runtime-query-consent",
        help="Create the exact, local-only read-only query inventory and consent plan for the selected workflow profile.",
    )
    runtime_query_plan.add_argument("--solution", required=True)
    runtime_query_plan.add_argument(
        "--source-provider",
        choices=sorted(SOURCE_PROVIDERS),
        default="azure-monitor-sdk",
        help="Exact Sentinel source-query provider route to bind; does not approve execution.",
    )
    primary_setting = subparsers.add_parser(
        "confirm-primary-lab-setting",
        help="Explicitly attest the primary workspace setting before shared lab read approval.",
    )
    primary_setting.add_argument("--solution", required=True)
    primary_setting.add_argument("--actor", required=True)
    primary_setting.add_argument("--primary-setting-name", required=True)
    primary_setting.add_argument(
        "--confirm-primary-setting",
        action="store_true",
        help="Confirm the named setting; this is user attestation, not service verification.",
    )
    runtime_query_consent = subparsers.add_parser(
        "review-runtime-query-consent",
        help=(
            "Record explicit query-family approval for the selected workflow profile, "
            "revise, or decline after reviewing the current inventory. Approval never "
            "authorizes authentication or writes."
        ),
    )
    runtime_query_consent.add_argument("--solution", required=True)
    runtime_query_consent.add_argument("--expected-plan-sha256", required=True)
    runtime_query_consent.add_argument("--actor", required=True)
    runtime_query_consent.add_argument(
        "--source-provider",
        choices=sorted(SOURCE_PROVIDERS),
        default="azure-monitor-sdk",
    )
    runtime_query_consent.add_argument(
        "--approve-family",
        action="append",
        choices=["sentinelSourceQueryFamily", "defenderXdrQueryFamily"],
        default=[],
    )
    runtime_query_consent.add_argument("--decline", action="store_true")
    runtime_query_consent.add_argument(
        "--revise-plan",
        action="store_true",
        help="Return to plan review without recording consent.",
    )
    runtime_query_consent.add_argument("--reason")
    revoke_runtime_consent = subparsers.add_parser(
        "revoke-lab-runtime-query-consent",
        help="Revoke shared lab runtime-query consent for the currently locked lab.",
    )
    revoke_runtime_consent.add_argument("--solution", required=True)
    revoke_runtime_consent.add_argument("--actor", required=True)
    revoke_runtime_consent.add_argument("--reason", required=True)
    runtime_query_check = subparsers.add_parser(
        "check-runtime-query-consent",
        help="Check an exact approved family/provider binding before external provider dispatch.",
    )
    runtime_query_check.add_argument("--solution", required=True)
    runtime_query_check.add_argument(
        "--family",
        required=True,
        choices=["sentinelSourceQueryFamily", "defenderXdrQueryFamily"],
    )
    runtime_query_check.add_argument(
        "--provider",
        required=True,
        choices=["azure-monitor-sdk", "triage-mcp", "log-analytics-cli", "graph"],
    )
    runtime_query_check.add_argument(
        "--source-provider",
        choices=sorted(SOURCE_PROVIDERS),
        default="azure-monitor-sdk",
    )
    planning_consent = subparsers.add_parser(
        "review-deployment-plan",
        help="Record or decline component-specific planning consent bound to the current plan hash; authorizes no writes.",
    )
    planning_consent.add_argument("--solution", required=True)
    planning_consent.add_argument("--expected-plan-sha256", required=True)
    planning_consent.add_argument("--actor", required=True)
    planning_consent.add_argument(
        "--approve-component",
        action="append",
        choices=[
            "sentinelAlertRules",
            "xdrCustomDetections",
            "fullPackageAcceptance",
            "mockTelemetryIngestion",
            "fallbackDcr",
            "fallbackDce",
            "customTableCreate",
        ],
        default=[],
    )
    planning_consent.add_argument("--decline", action="store_true")
    planning_consent.add_argument("--reason")
    planning_consent.add_argument("--max-additional-custom-detections", type=int)
    planning_consent.add_argument(
        "--package-flag",
        action="append",
        help="Explicit package selection as NAME=true|false; repeat for every package flag.",
    )
    planning_consent.add_argument(
        "--dce-selected",
        action="store_true",
        help="Explicitly select the conditional DCE component for this plan.",
    )
    analytic_deployment = subparsers.add_parser(
        "deploy-analytic-rules",
        help="Create or update source Sentinel analytic rules through Azure Resource Manager.",
    )
    analytic_deployment.add_argument("--solution", required=True)
    analytic_deployment.add_argument("--workspace-resource-id")
    arm_acceptance_plan = subparsers.add_parser(
        "plan-arm-template-acceptance-batch",
        help="Plan exact post-validation ARM template deployments for every solution in the approved same-lab workstream.",
    )
    arm_acceptance_plan.add_argument("--member", action="append", required=True)
    arm_acceptance_plan.add_argument(
        "--validation-receipt",
        action="append",
        required=True,
        help="Current build-and-validate-report.md for the corresponding --member; repeat in matching order.",
    )
    arm_acceptance_plan.add_argument("--shared-decisions", required=True)
    arm_acceptance = subparsers.add_parser(
        "deploy-arm-template-acceptance-batch",
        help="Submit the exact final V3.1 mainTemplates; accept only recorded ARM provisioningState Succeeded.",
    )
    arm_acceptance.add_argument("--member", action="append", required=True)
    arm_acceptance.add_argument(
        "--validation-receipt",
        action="append",
        required=True,
        help="Same current build-and-validate-report.md for the corresponding --member; repeat in matching order.",
    )
    arm_acceptance.add_argument("--shared-decisions", required=True)
    arm_acceptance.add_argument("--expected-batch-plan-sha256", required=True)
    arm_acceptance.add_argument("--actor", required=True)
    arm_acceptance.add_argument("--confirm-exact-scope-write", required=True)
    parity_start = subparsers.add_parser(
        "start-alert-parity",
        help="Enable disabled AR/CD pairs, ingest a marked mock payload, and emit capture queries.",
    )
    parity_start.add_argument("--solution", required=True)
    parity_start.add_argument("--workspace-resource-id")
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
    parity_batch.add_argument("--workspace-resource-id")
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
        choices=["triage-mcp", "azure-monitor-sdk", "log-analytics-cli"],
    )
    record_parser.add_argument(
        "--source-provider",
        choices=sorted(SOURCE_PROVIDERS),
        default="azure-monitor-sdk",
        help="Exact Sentinel route bound by the runtime-query consent plan.",
    )
    record_parser.add_argument("--results", required=True)
    record_parser.add_argument(
        "--provider-gap-evidence",
        help="JSON evidence for a complete Log Analytics fallback after a Triage MCP provider failure.",
    )
    package_v3_1 = subparsers.add_parser(
        "package-v3-1",
        help="Package with V3.1; initialized YOLO runs enforce workflow and fresh-evidence gates.",
    )
    package_v3_1.add_argument("--solution", required=True)
    package_v3_1.add_argument(
        "--toolkit-root",
        help=(
            "Repository root containing the V3.1 packaging toolkit. Defaults to the "
            "solution's repository root."
        ),
    )
    package_v3_1.add_argument(
        "--version-bump",
        required=True,
        choices=["none", "patch", "minor", "major"],
    )
    package_v3_1.add_argument(
        "--target-version",
        help="Explicit canonical V3.1 solution version (>=3.2.2 and <4.0.0); use with --version-bump none.",
    )
    package_v3_1.add_argument(
        "--legacy-baseline-evidence",
        help=(
            "Receipt-bound package-input comparison JSON for a legacy same-version "
            "rebuild plan that predates per-file V3.1 receipts."
        ),
    )
    selection_plan = subparsers.add_parser(
        "package-selection-plan",
        help="Plan evidence-based Analytic Rule and Custom Detection package eligibility.",
    )
    selection_plan.add_argument("--solution", required=True)
    selection_apply = subparsers.add_parser(
        "package-selection-apply",
        help="Apply a fresh, hash-bound package selection to Solution_*.json.",
    )
    selection_apply.add_argument("--solution", required=True)
    selection_apply.add_argument("--expected-plan-sha256", required=True)
    package_release = subparsers.add_parser(
        "workflow-plan-package-release",
        help="Explicitly select a new V3.1 release action for changed package inputs.",
    )
    package_release.add_argument("--solution", required=True)
    package_release.add_argument("--version-bump", choices=["patch", "minor", "major"])
    package_release.add_argument(
        "--target-version",
        help="Explicit canonical V3.1 solution version (>=3.2.2 and <4.0.0), instead of a version bump.",
    )
    package_release.add_argument(
        "--expected-package-input-sha256",
        required=True,
        help="Exact current package-input SHA-256 reported by workflow-status.",
    )
    notes_refresh = subparsers.add_parser(
        "workflow-plan-release-notes-refresh",
        help="Authorize one exact ReleaseNotes-only refresh without incrementing the package version.",
    )
    notes_refresh.add_argument("--solution", required=True)
    notes_refresh.add_argument(
        "--release-date",
        default=None,
        help="Release date in DD-MM-YYYY format (defaults to today's date in DD-MM-YYYY).",
    )
    notes_refresh.add_argument("--change-history", required=True)
    notes_refresh.add_argument(
        "--expected-package-input-sha256",
        required=True,
        help="Current hash of the already successfully packaged inputs.",
    )
    same_version_rebuild = subparsers.add_parser(
        "workflow-plan-same-version-content-rebuild",
        help=(
            "Explicitly approve one exact-input Authoring rebuild at the current "
            "solution version after content changes."
        ),
    )
    same_version_rebuild.add_argument("--solution", required=True)
    same_version_rebuild.add_argument(
        "--target-version",
        required=True,
        help="Exact current solution version to preserve; no version bump is performed.",
    )
    same_version_rebuild.add_argument(
        "--expected-package-input-sha256",
        required=True,
        help="Exact current package-input SHA-256 reported by workflow-status.",
    )
    same_version_rebuild.add_argument(
        "--changed-input",
        action="append",
        required=True,
        help=(
            "Exact current non-ReleaseNotes package-input path in the approved "
            "change scope; repeat once per changed input."
        ),
    )
    same_version_rebuild.add_argument(
        "--legacy-baseline-evidence",
        help=(
            "Receipt- or failed-attempt-bound package-input comparison JSON used "
            "only when the prior V3.1 baseline has no per-file manifest."
        ),
    )
    same_version_rebuild.add_argument(
        "--failed-candidate-evidence",
        help=(
            "Exact persisted failure handoff for a consumed V3.1 attempt with no "
            "successful receipt; requires --legacy-baseline-evidence."
        ),
    )
    same_version_verify = subparsers.add_parser(
        "workflow-verify-same-version-content-rebuild",
        help="Read-only verification of the exact scope and receipt for a same-version rebuild.",
    )
    same_version_verify.add_argument("--solution", required=True)
    same_version_verify.add_argument(
        "--legacy-baseline-evidence",
        help="Receipt-bound comparison JSON for a legacy rebuild plan without a saved evidence binding.",
    )
    workflow_init = subparsers.add_parser(
        "workflow-init",
        help="Create or resume the gated end-to-end migration workflow state.",
    )
    workflow_init.add_argument("--solution", required=True)
    workflow_init.add_argument("--tenant-id")
    workflow_init.add_argument("--subscription-id")
    workflow_init.add_argument("--workspace-resource-id")
    workflow_init.add_argument("--workspace-customer-id")
    workflow_init.add_argument(
        "--arm-validation-method", choices=["lab-deployment", "arm-ttk"],
        help="New runs default to lab-deployment; resumption never changes the selected method.",
    )
    workflow_init.add_argument(
        "--confirm-configured-target",
        action="store_true",
        help="Confirm the tenant/workspace shown by doctor for a new Qualification run.",
    )
    workflow_init.add_argument(
        "--version-bump",
        choices=["none", "patch", "minor", "major"],
    )
    workflow_init.add_argument(
        "--target-version",
        help="Persist an explicit canonical V3.1 solution version (>=3.2.2 and <4.0.0); use with --version-bump none.",
    )
    workflow_init.add_argument(
        "--workflow-profile",
        default="authoring",
        choices=WORKFLOW_PROFILES,
        help="Select authoring (default) or qualification before initialization.",
    )
    workflow_init.add_argument(
        "--yolo",
        action="store_true",
        help="Opt into full-inventory, resumable local authoring orchestration for a new run.",
    )
    workflow_init.add_argument(
        "--campaign-id",
        help="Explicit durable budget campaign identity; required for every new YOLO campaign.",
    )
    workflow_yolo = subparsers.add_parser(
        "workflow-yolo",
        help="Run the existing local discovery, full-solution converter, and structural validator under an initialized YOLO contract.",
    )
    workflow_yolo.add_argument("--solution", required=True)
    workflow_yolo_refresh = subparsers.add_parser(
        "workflow-yolo-refresh",
        help="Import current hash-bound provider reports without rerunning conversion or validation.",
    )
    workflow_yolo_refresh.add_argument("--solution", required=True)
    workflow_status_parser = subparsers.add_parser(
        "workflow-status",
        help="Show the persisted end-to-end migration workflow state.",
    )
    workflow_status_parser.add_argument("--solution", required=True)
    workbook_commands = {}
    for command in (
        "workflow-arm-candidate", "workflow-arm-plan", "workflow-arm-review-scope",
        "workflow-arm-withdraw-scope", "workflow-arm-execute", "workflow-arm-reconcile",
        "workflow-arm-import",
        "workflow-arm-preflight-plan", "workflow-arm-preflight-review",
        "workflow-arm-preflight-revoke", "workflow-arm-preflight-execute",
        "workflow-workbook-contract-plan", "workflow-workbook-contract-import",
    ):
        workbook_commands[command] = subparsers.add_parser(command)
        workbook_commands[command].add_argument("--solution", required=True)
    workbook_commands["workflow-arm-candidate"].add_argument("--validation-receipt")
    workbook_commands["workflow-arm-candidate"].add_argument("--toolkit-root")
    for command in ("workflow-arm-plan", "workflow-workbook-contract-plan"):
        workbook_commands[command].add_argument("--target", required=True, help="Local JSON with exact lab identity and optional workspaceLocation.")
        workbook_commands[command].add_argument("--selected-flags", required=True, help="JSON object selecting every declared Deploy flag independently.")
    for command in ("workflow-arm-review-scope", "workflow-arm-withdraw-scope", "workflow-arm-execute", "workflow-arm-reconcile", "workflow-arm-import"):
        workbook_commands[command].add_argument("--actor", required=True)
        workbook_commands[command].add_argument("--reference", required=True)
    workbook_commands["workflow-arm-review-scope"].add_argument("--decision", required=True, choices=["approved", "declined"])
    for command in ("workflow-arm-review-scope", "workflow-arm-execute"):
        workbook_commands[command].add_argument("--plan-sha256", required=True)
    workbook_commands["workflow-arm-execute"].add_argument("--confirmation", required=True)
    for command in ("workflow-arm-preflight-review", "workflow-arm-preflight-revoke"):
        workbook_commands[command].add_argument("--actor", required=True)
        workbook_commands[command].add_argument("--reference", required=True)
    for command in ("workflow-arm-preflight-review", "workflow-arm-preflight-execute"):
        workbook_commands[command].add_argument("--preflight-plan-sha256", required=True)
    workbook_commands["workflow-arm-preflight-review"].add_argument(
        "--decision", required=True, choices=["approved", "declined"],
    )
    workbook_commands["workflow-arm-preflight-execute"].add_argument("--state-dir")
    for command in ("workflow-arm-reconcile", "workflow-arm-import"):
        workbook_commands[command].add_argument("--attempt", required=True)
        workbook_commands[command].add_argument("--observation", required=True)
    workbook_commands["workflow-workbook-contract-import"].add_argument("--evidence", required=True)
    workbook_commands["workflow-workbook-contract-import"].add_argument("--contract-only", action="store_true")
    workflow_status_parser.add_argument(
        "--source-provider",
        choices=sorted(SOURCE_PROVIDERS),
        help="Override the Sentinel source route; otherwise use the persisted plan route.",
    )
    workflow_next = subparsers.add_parser(
        "workflow-next",
        help="Return the next stage whose dependencies have passed.",
    )
    workflow_next.add_argument("--solution", required=True)
    workflow_recover_conversion = subparsers.add_parser(
        "workflow-recover-conversion-evidence",
        help=(
            "Revalidate and bind a legacy full-solution conversion manifest "
            "for offline Authoring in the selected run."
        ),
    )
    workflow_recover_conversion.add_argument("--solution", required=True)
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
    workflow_status_reminder = subparsers.add_parser(
        "workflow-status-reminder",
        help=(
            "Emit a deterministic, evidence-bound operator status reminder with "
            "stage diagram, batch duration explanation, and no-change suppression."
        ),
    )
    workflow_status_reminder.add_argument("--solution", required=True)
    workflow_status_reminder.add_argument(
        "--no-persist-cursor",
        action="store_true",
        help="Compute the reminder without updating status-reminder-cursor.json.",
    )
    workflow_execution_owner = subparsers.add_parser(
        "workflow-execution-owner",
        help="Claim or release single-owner execution lease for a workflow operation.",
    )
    workflow_execution_owner.add_argument("--solution", required=True)
    workflow_execution_owner.add_argument(
        "--action",
        choices=["claim", "release"],
        default="claim",
        help="Claim/renew or release the execution lease for (runId, operation).",
    )
    workflow_execution_owner.add_argument("--owner-id", required=True)
    workflow_execution_owner.add_argument("--operation", required=True)
    workflow_execution_owner.add_argument(
        "--scope",
        help="Optional JSON object string or file path describing the leased scope.",
    )
    workflow_forward_approval = subparsers.add_parser(
        "workflow-forward-approval",
        help="Forward or verify an explicit, hash-bound operation approval for the accountable owner.",
    )
    workflow_forward_approval.add_argument("--solution", required=True)
    workflow_forward_approval.add_argument(
        "--action",
        choices=["forward", "verify"],
        default="forward",
        help="Forward a new approval receipt or verify an existing receipt.",
    )
    workflow_forward_approval.add_argument("--operation", required=True)
    workflow_forward_approval.add_argument(
        "--owner-id",
        "--forwarded-to-owner-id",
        dest="forwarded_to_owner_id",
        required=True,
        help="Accountable owner ID receiving or verifying the forwarded approval.",
    )
    workflow_forward_approval.add_argument(
        "--approved-by",
        help="Approving user/actor identity (required when --action forward).",
    )
    workflow_forward_approval.add_argument(
        "--exact-scope",
        required=True,
        help="JSON object string or file path binding exact target/artifact/hash scope.",
    )
    workflow_forward_approval.add_argument(
        "--approval-sha256",
        help="Expected approvalSha256 when verifying a forwarded approval.",
    )
    workflow_forward_approval.add_argument("--reference")
    coordinator_enroll_parser = subparsers.add_parser(
        "coordinator-enroll",
        help="Enroll a selected persisted run with an accountable owner; shadow mode only.",
    )
    coordinator_enroll_parser.add_argument("--solution", required=True)
    coordinator_enroll_parser.add_argument("--owner", required=True)
    coordinator_enroll_parser.add_argument(
        "--shared-dependency",
        action="append",
        help="Optional exact prerequisite as ACTION=KEY:PURPOSE; repeat as needed.",
    )
    coordinator_enroll_parser.add_argument(
        "--registry", help="Override the ignored local registry path."
    )
    for command, help_text in (
        ("coordinator-reconcile", "Refresh coordination decisions from workflow-status and workflow-next."),
        ("coordinator-status", "Show the current durable coordination view and watchdog exceptions."),
    ):
        coordinator_parser = subparsers.add_parser(command, help=help_text)
        coordinator_parser.add_argument("--solution", required=True)
        coordinator_parser.add_argument("--idle-seconds", type=int, default=900)
        coordinator_parser.add_argument("--registry", help="Override the ignored local registry path.")
    coordinator_event = subparsers.add_parser(
        "coordinator-event",
        help="Append one idempotent coordinator event; approvals are never granted here.",
    )
    coordinator_event.add_argument("--solution", required=True)
    coordinator_event.add_argument("--event-id", required=True)
    coordinator_event.add_argument(
        "--kind",
        required=True,
        choices=[
            "executor-completed",
            "approval-requested",
            "shared-dependency-completed",
            "claim-resolved",
            "owner-handoff",
        ],
    )
    coordinator_event.add_argument("--action-id")
    coordinator_event.add_argument("--purpose")
    coordinator_event.add_argument("--target-sha256")
    coordinator_event.add_argument("--evidence")
    coordinator_event.add_argument("--actor")
    coordinator_event.add_argument("--new-owner")
    coordinator_event.add_argument("--claim-id")
    coordinator_event.add_argument("--outcome", choices=["not-started", "completed", "unknown"])
    coordinator_event.add_argument("--reference")
    coordinator_event.add_argument("--registry")
    coordinator_claim_parser = subparsers.add_parser(
        "coordinator-claim",
        help="Atomically claim one ready local action; does not dispatch it.",
    )
    coordinator_claim_parser.add_argument("--solution", required=True)
    coordinator_claim_parser.add_argument("--action-id", required=True)
    coordinator_claim_parser.add_argument("--executor", required=True)
    coordinator_claim_parser.add_argument("--claim-key", required=True)
    coordinator_claim_parser.add_argument("--lease-seconds", type=float, default=300)
    coordinator_claim_parser.add_argument("--registry")
    coordinator_heartbeat_parser = subparsers.add_parser(
        "coordinator-heartbeat",
        help="Extend a live claim after rechecking its exact evidence and target.",
    )
    coordinator_heartbeat_parser.add_argument("--solution", required=True)
    coordinator_heartbeat_parser.add_argument("--claim-id", required=True)
    coordinator_heartbeat_parser.add_argument("--executor", required=True)
    coordinator_heartbeat_parser.add_argument("--lease-seconds", type=float, default=300)
    coordinator_heartbeat_parser.add_argument("--registry")
    coordinator_ack_parser = subparsers.add_parser(
        "coordinator-ack",
        help="Acknowledge outbox delivery only; this is not user approval.",
    )
    coordinator_ack_parser.add_argument("--solution", required=True)
    coordinator_ack_parser.add_argument("--delivery-id", required=True)
    coordinator_ack_parser.add_argument("--actor", required=True)
    coordinator_ack_parser.add_argument("--registry")
    budget_status = subparsers.add_parser(
        "workflow-budget",
        help="Show configured ceilings, measured receipts, unknown usage, and remaining campaign allowance.",
    )
    budget_status.add_argument("--solution", required=True)
    budget_status.add_argument("--campaign-id", required=True)
    budget_extend = subparsers.add_parser(
        "workflow-budget-extend",
        help="Raise one campaign ceiling with an append-only owner-scope audit receipt.",
    )
    budget_extend.add_argument("--solution", required=True)
    budget_extend.add_argument("--campaign-id", required=True)
    budget_extend.add_argument("--dimension", required=True, choices=sorted(DEFAULT_POLICY))
    budget_extend.add_argument("--new-limit", required=True, type=float)
    budget_extend.add_argument("--actor", required=True)
    budget_extend.add_argument("--reason", required=True)
    budget_extend.add_argument("--reference", required=True)
    budget_reconcile = subparsers.add_parser(
        "workflow-budget-reconcile",
        help="Reconcile one interrupted operation using its authoritative measured outcome.",
    )
    budget_reconcile.add_argument("--solution", required=True)
    budget_reconcile.add_argument("--campaign-id", required=True)
    budget_reconcile.add_argument("--operation-id", required=True)
    budget_reconcile.add_argument(
        "--status", required=True, choices=["passed", "failed", "cancelled", "unknown"],
    )
    budget_reconcile.add_argument("--elapsed-seconds", required=True, type=float)
    budget_reconcile.add_argument("--actor", required=True)
    budget_reconcile.add_argument("--reason", required=True)
    budget_reconcile.add_argument("--reference", required=True)
    budget_legacy = subparsers.add_parser(
        "workflow-budget-reconcile-legacy",
        help="Record an owner-reviewed baseline for a pre-budget run; no history is reconstructed.",
    )
    budget_legacy.add_argument("--solution", required=True)
    budget_legacy.add_argument("--campaign-id", required=True)
    budget_legacy.add_argument("--baseline", required=True, help="JSON file containing every measured legacy dimension.")
    budget_legacy.add_argument("--actor", required=True)
    budget_legacy.add_argument("--reason", required=True)
    budget_legacy.add_argument("--reference", required=True)
    budget_deadline = subparsers.add_parser(
        "workflow-budget-deadline",
        help="Persist the approved schedule-aware alert-observation deadline for one test.",
    )
    budget_deadline.add_argument("--solution", required=True)
    budget_deadline.add_argument("--campaign-id", required=True)
    budget_deadline.add_argument("--test-id", required=True)
    budget_deadline.add_argument("--deadline-at", required=True)
    budget_deadline.add_argument("--approval-reference", required=True)
    budget_deadline.add_argument("--actor", required=True)
    budget_deadline.add_argument("--reason", required=True)

    runs_parser = subparsers.add_parser("workflow-runs", help="List run IDs without selecting or modifying state.")
    runs_parser.add_argument("--solution", required=True)
    pr_qualify_parser = subparsers.add_parser(
        "pr-qualify",
        help="Evaluate PR Validation, Qualification, and Migration checklists and generate HTML/Markdown reports.",
    )
    pr_qualify_parser.add_argument(
        "--solution",
        required=True,
        help="Path to solution directory (e.g., Solutions/Azure DDoS Protection).",
    )
    pr_qualify_parser.add_argument(
        "--mode",
        choices=["validation", "qualification", "full"],
        default="full",
        help="Evaluation mode: validation, qualification, or full (default: full).",
    )
    pr_qualify_mig_group = pr_qualify_parser.add_mutually_exclusive_group()
    pr_qualify_mig_group.add_argument(
        "--is-migration",
        dest="is_migration",
        action="store_true",
        default=None,
        help="Force migration checklist evaluation on.",
    )
    pr_qualify_mig_group.add_argument(
        "--no-migration",
        "--no-is-migration",
        dest="is_migration",
        action="store_false",
        default=None,
        help="Force migration checklist evaluation off (general solution qualification).",
    )
    pr_qualify_parser.add_argument(
        "--output-dir",
        help="Output directory for PR qualification reports (default: <solution>/Evidence/pr-qualification).",
    )
    pr_qualify_parser.add_argument(
        "--waivers-file",
        help="Path to JSON file mapping check IDs to {authorJustification, supportingEvidenceRef, knownLimitationCategory}.",
    )
    pr_qualify_parser.add_argument(
        "--acknowledged-exclusions-file",
        help="Path to JSON file with list of excluded paths.",
    )
    pr_qualify_parser.add_argument(
        "--evidence-dir",
        help="Path to qualification evidence directory or JSON file.",
    )
    pr_qualify_parser.add_argument(
        "--target-version",
        help="Optional target version override for testing/previewing at >= 3.2.2.",
    )
    from solution_manager.qualification.workbook_qualification_cli import (
        register_workbook_qualification_commands, dispatch_workbook_qualification,
    )
    qualification_commands = register_workbook_qualification_commands(subparsers)
    for subparser in subparsers.choices.values():
        if any(action.dest == "solution" for action in subparser._actions):
            subparser.add_argument("--run-id", help="Select an existing run; required when multiple runs exist.")
    for action in subparsers.choices["workflow-plan-package-release"]._actions:
        if action.dest == "run_id":
            action.required = True
            action.help = "Select the exact existing workflow run to update."
            break
    for action in subparsers.choices["workflow-recover-conversion-evidence"]._actions:
        if action.dest == "run_id":
            action.required = True
            action.help = "Select the exact existing Authoring run to revalidate."
            break
    for action in subparsers.choices["workflow-verify-same-version-content-rebuild"]._actions:
        if action.dest == "run_id":
            action.required = True
            action.help = "Select the exact workflow run whose rebuild scope is being verified."
            break
    for action in subparsers.choices["workflow-plan-release-notes-refresh"]._actions:
        if action.dest == "run_id":
            action.required = True
            action.help = "Select the exact existing Authoring run to update."
            break
    for action in subparsers.choices[
        "workflow-plan-same-version-content-rebuild"
    ]._actions:
        if action.dest == "run_id":
            action.required = True
            action.help = "Select the exact existing Authoring run to update."
            break
    for name in ("package-selection-plan", "package-selection-apply"):
        for action in subparsers.choices[name]._actions:
            if action.dest == "run_id":
                action.required = True
                action.help = "Select the exact existing workflow run."
                break
    for action in subparsers.choices["diagnose-app-readback-scopes"]._actions:
        if action.dest == "run_id":
            action.required = True
            action.help = "Select the exact approved Cisco qualification run."
            break
    subparsers.choices["workflow-init"].add_argument(
        "--new-run", action="store_true", help="Create an isolated new workflow instead of resuming."
    )
    for command in (*workbook_commands, *qualification_commands):
        for action in subparsers.choices[command]._actions:
            if action.dest == "run_id":
                action.required = True
    args = parser.parse_args(argv)
    if args.command == "convert" and args.rule_id and len(args.rule_id) != 1:
        parser.error("--rule-id accepts exactly one GUID; repeated selectors are not supported")
    selection = None
    try:
        isolated_permission_commands = {
            "workbook-publication-plan", "workbook-publication-clean", "workbook-publication-validate",
            "workbook-update-plan",
            "workbook-update-review",
            "workbook-update-apply",
            "native-workbook-plan",
            "native-workbook-review",
            "native-workbook-import",
            "native-workbook-validate",
            "plan-delegated-app-permission-update",
            "verify-delegated-app-permission-update",
            "workbook-dependency-plan",
            "workbook-review",
            "pr-qualify",
        }
        if getattr(args, "solution", None) and args.command not in isolated_permission_commands:
            selection = select_run(args.solution, args.run_id)
        # Read-only status and migration planning must not initialize or change artifacts.
        if args.command not in {"migrate-reports", "workflow-status", "workflow-status-reminder", "workflow-execution-owner", "workflow-forward-approval", "workflow-next", "workflow-init", "workflow-runs", "workflow-verify-same-version-content-rebuild", "export-evidence", "preflight-deployment", "plan-deployment", "review-deployment-plan", "plan-runtime-query-consent", "confirm-primary-lab-setting", "review-runtime-query-consent", "revoke-lab-runtime-query-consent", "check-runtime-query-consent", "coordinator-enroll", "coordinator-status", "coordinator-reconcile", "coordinator-event", "coordinator-claim", "coordinator-heartbeat", "coordinator-ack", "review-packet", "consolidated-review-plan", *isolated_permission_commands} and not (
            args.command == "convert" and args.rule_id
        ):
            configure_logging(getattr(args, "solution", None))
        if args.command in qualification_commands:
            result = dispatch_workbook_qualification(args)
        elif args.command == "coordinator-enroll":
            result = coordinator_enroll(
                args.solution,
                owner=args.owner,
                required_shared_dependencies=args.shared_dependency,
                registry_path=args.registry,
            )
        elif args.command == "coordinator-reconcile":
            result = coordinator_reconcile(
                args.solution,
                registry_path=args.registry,
                idle_seconds=args.idle_seconds,
            )
        elif args.command == "coordinator-status":
            result = coordinator_status(
                args.solution,
                registry_path=args.registry,
                idle_seconds=args.idle_seconds,
            )
        elif args.command == "coordinator-event":
            result = coordinator_record_event(
                args.solution,
                event_id=args.event_id,
                kind=args.kind,
                action_id=args.action_id,
                purpose=args.purpose,
                target_sha256=args.target_sha256,
                evidence=args.evidence,
                actor=args.actor,
                new_owner=args.new_owner,
                claim_id=args.claim_id,
                outcome=args.outcome,
                reference=args.reference,
                registry_path=args.registry,
            )
        elif args.command == "coordinator-claim":
            result = coordinator_claim(
                args.solution,
                action_id=args.action_id,
                executor=args.executor,
                claim_key=args.claim_key,
                lease_seconds=args.lease_seconds,
                registry_path=args.registry,
            )
        elif args.command == "coordinator-heartbeat":
            result = coordinator_heartbeat(
                args.solution,
                claim_id=args.claim_id,
                executor=args.executor,
                lease_seconds=args.lease_seconds,
                registry_path=args.registry,
            )
        elif args.command == "coordinator-ack":
            result = acknowledge_outbox(
                args.solution,
                delivery_id=args.delivery_id,
                actor=args.actor,
                registry_path=args.registry,
            )
        elif args.command == "workflow-runs":
            result = {"runs": list_runs(args.solution)}
        elif args.command == "pr-qualify":
            sol_root = Path(args.solution).expanduser().resolve()
            out_dir = (
                Path(args.output_dir).expanduser().resolve()
                if args.output_dir
                else sol_root / "Evidence" / "pr-qualification"
            )
            report_data = evaluate_solution_pr_qualification(
                sol_root,
                mode=args.mode,
                is_migration=args.is_migration,
                waivers_file=args.waivers_file,
                acknowledged_exclusions_file=args.acknowledged_exclusions_file,
                evidence_dir=args.evidence_dir,
                target_version=args.target_version,
            )
            out_dir.mkdir(parents=True, exist_ok=True)
            result_json_path = out_dir / "pr-qualification-result.json"
            result_json_path.write_text(
                json.dumps(report_data, indent=2) + "\n",
                encoding="utf-8",
            )
            written_reports = write_pr_qualification_reports(
                report_data,
                out_dir,
                solution_root=sol_root,
            )
            result = {
                "solutionName": report_data["solutionName"],
                "solutionVersion": report_data["solutionVersion"],
                "mode": report_data["mode"],
                "isMigration": report_data["isMigration"],
                "validationStatus": report_data["validationStatus"],
                "qualificationStatus": report_data["qualificationStatus"],
                "migrationStatus": report_data["migrationStatus"],
                "overallVerdict": report_data["overallVerdict"],
                "summary": report_data["summary"],
                "outputDir": str(out_dir),
                "resultJsonPath": str(result_json_path),
                "htmlReportPath": str(written_reports["html"]),
                "markdownSummaryPath": str(written_reports["markdown"]),
                "outputPaths": {
                    "resultJson": str(result_json_path),
                    "htmlReport": str(written_reports["html"]),
                    "markdownSummary": str(written_reports["markdown"]),
                },
            }
        elif args.command == "export-evidence":
            if args.include_authoring_contract and not args.run_id:
                raise ValueError(
                    "--include-authoring-contract requires an explicit --run-id"
                )
            authoring_contract = (
                read_authoring_contract(args.solution)
                if args.include_authoring_contract else None
            )
            result = export_evidence(
                args.solution,
                authoring_contract=authoring_contract,
            )
        elif args.command == "migrate-reports":
            result = migrate_reports(args.solution, apply=args.apply)
        elif args.command == "setup":
            result = setup(
                interactive=not args.non_interactive,
                tenant_id=args.tenant_id,
                workspace_id=args.workspace_id,
                skip_sentinel_auth=args.skip_sentinel_auth,
                skip_hunting_auth=args.skip_hunting_auth,
                hunting_auth_method=args.hunting_auth_method,
                hunting_client_id=args.hunting_client_id,
                azure_config_dir=args.azure_config_dir,
            )
        elif args.command == "doctor":
            result = doctor(solution=args.solution)
        elif args.command == "configure-workspace":
            result = configure_workspace(
                args.workspace_resource_id,
                workspace_customer_id=args.workspace_customer_id,
                tenant_id=args.tenant_id,
                subscription_id=args.subscription_id,
            )
        elif args.command == "qualification-diagnose":
            result = diagnose_target(args.solution)
        elif args.command == "qualification-repair-target":
            result = repair_target(
                args.solution,
                approve_target_update=args.approve_target_update,
            )
        elif args.command == "setup-deployment":
            target = require_locked_target(
                args.solution,
                tenant_id=args.tenant_id,
            )
            result = setup_deployment_authentication(
                tenant_id=target["tenantId"],
                auth_method=args.auth_method,
                graph_client_id=args.custom_detection_client_id,
                azure_config_dir=args.azure_config_dir,
            )
        elif args.command == "setup-app-registration-auth":
            target = require_locked_target(args.solution, materialize_missing=False)
            from solution_manager.qualification.delegated_app_registration import (
                setup_app_registration_authentication,
            )

            result = setup_app_registration_authentication(
                tenant_id=target["tenantId"],
                auth_method=args.auth_method,
                bootstrap_client_id=args.bootstrap_client_id,
            )
        elif args.command == "setup-app-readback-auth":
            target = require_locked_target(args.solution, materialize_missing=False)
            from solution_manager.qualification.delegated_app_registration import (
                setup_app_readback_authentication,
            )

            result = setup_app_readback_authentication(
                tenant_id=target["tenantId"],
                readback_client_id=args.readback_client_id,
            )
        elif args.command == "verify-delegated-app-readback":
            from solution_manager.qualification.delegated_app_registration import verify_delegated_app_readback

            result = verify_delegated_app_readback(args.solution)
        elif args.command == "diagnose-app-readback-scopes":
            from solution_manager.qualification.delegated_app_registration import diagnose_app_readback_scopes

            result = diagnose_app_readback_scopes(
                args.solution,
                run_id=args.run_id,
            )
        elif args.command == "plan-delegated-app-registration":
            from solution_manager.qualification.delegated_app_registration import plan_delegated_app_registration

            result = plan_delegated_app_registration(
                args.solution,
                app_display_name=args.app_display_name,
            )
        elif args.command == "register-delegated-app":
            from solution_manager.qualification.delegated_app_registration import register_delegated_app

            result = register_delegated_app(
                args.solution,
                expected_plan_sha256=args.expected_plan_sha256,
                approve_exact_app_registration=args.approve_exact_app_registration,
                app_display_name=args.app_display_name,
            )
        elif args.command == "plan-delegated-app-permission-update":
            from solution_manager.qualification.delegated_app_registration import (
                plan_delegated_app_permission_update,
            )

            result = plan_delegated_app_permission_update(args.solution)
        elif args.command == "verify-delegated-app-permission-update":
            from solution_manager.qualification.delegated_app_registration import (
                verify_delegated_app_permission_update,
            )

            result = verify_delegated_app_permission_update(
                args.solution,
                expected_plan_sha256=args.expected_plan_sha256,
            )
        elif args.command == "deploy":
            result = deploy_solution(args.solution)
        elif args.command == "preflight-deployment":
            result = preflight_deployment(
                args.solution,
                auth_method=args.auth_method,
            )
        elif args.command == "plan-deployment":
            result = persist_deployment_plan(args.solution)
        elif args.command == "plan-runtime-query-consent":
            _require_explicit_authoring_run(args.solution, args.run_id)
            result = persist_runtime_query_plan(
                args.solution,
                source_provider=args.source_provider,
            )
        elif args.command == "confirm-primary-lab-setting":
            result = confirm_primary_lab_setting(
                args.solution,
                actor=args.actor,
                primary_setting_name=args.primary_setting_name,
                confirmed=args.confirm_primary_setting,
            )
        elif args.command == "review-runtime-query-consent":
            _require_explicit_authoring_run(args.solution, args.run_id)
            result = record_runtime_query_consent(
                args.solution,
                expected_plan_sha256=args.expected_plan_sha256,
                actor=args.actor,
                approved_families=args.approve_family,
                declined=args.decline,
                revised=args.revise_plan,
                reason=args.reason,
                source_provider=args.source_provider,
            )
        elif args.command == "revoke-lab-runtime-query-consent":
            result = revoke_runtime_query_consent(
                args.solution,
                actor=args.actor,
                reason=args.reason,
            )
        elif args.command == "check-runtime-query-consent":
            from solution_manager.qualification.runtime_consent import require_runtime_query_consent

            result = require_runtime_query_consent(
                args.solution,
                family=args.family,
                provider=args.provider,
                source_provider=args.source_provider,
            )
        elif args.command == "review-deployment-plan":
            package_flags: dict[str, bool] = {}
            for name, value in _key_values(args.package_flag).items():
                if value.casefold() not in {"true", "false"}:
                    raise ValueError("--package-flag values must be true or false")
                package_flags[name] = value.casefold() == "true"
            result = record_planning_consent(
                args.solution,
                expected_plan_sha256=args.expected_plan_sha256,
                actor=args.actor,
                approved_components=args.approve_component,
                declined=args.decline,
                reason=args.reason,
                max_additional_custom_detections=args.max_additional_custom_detections,
                package_flags=package_flags,
                dce_selected=args.dce_selected,
            )
        elif args.command == "deploy-analytic-rules":
            result = deploy_analytic_rules(
                args.solution,
                workspace_resource_id=args.workspace_resource_id,
            )
        elif args.command == "plan-arm-template-acceptance-batch":
            result = plan_arm_template_acceptance_batch(
                _package_batch_members(args.member),
                shared_decisions_path=args.shared_decisions,
                validation_receipts=args.validation_receipt,
            )
        elif args.command == "deploy-arm-template-acceptance-batch":
            result = execute_arm_template_acceptance_batch(
                _package_batch_members(args.member),
                expected_batch_plan_sha256=args.expected_batch_plan_sha256,
                shared_decisions_path=args.shared_decisions,
                validation_receipts=args.validation_receipt,
                actor=args.actor,
                confirmation=args.confirm_exact_scope_write,
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
        elif args.command == "package-v3-1":
            try:
                current_workflow = workflow_status(args.solution)
            except ValueError as exc:
                if "workflow state does not exist" not in str(exc):
                    raise
                current_workflow = None
            if current_workflow:
                result = package_workflow_v3_1(
                    args.solution,
                    requested_version_bump=args.version_bump,
                    requested_target_version=args.target_version,
                    toolkit_root=args.toolkit_root,
                    legacy_baseline_evidence=args.legacy_baseline_evidence,
                )
            else:
                raise ValueError(
                    "V3.1 package builds require a persisted workflow and campaign budget; "
                    "run workflow-init before packaging"
                )
        elif args.command == "package-selection-plan":
            result = create_package_selection_plan(args.solution, args.run_id)
        elif args.command == "package-selection-apply":
            result = apply_package_selection(
                args.solution,
                args.run_id,
                expected_plan_sha256=args.expected_plan_sha256,
            )
        elif args.command == "workflow-plan-package-release":
            if not args.run_id:
                raise ValueError(
                    "workflow-plan-package-release requires an explicit --run-id"
                )
            result = plan_new_package_release(
                args.solution,
                version_bump=args.version_bump,
                target_version=args.target_version,
                expected_package_input_sha256=args.expected_package_input_sha256,
            )
        elif args.command == "workflow-plan-release-notes-refresh":
            result = plan_release_notes_refresh(
                args.solution,
                release_date=args.release_date,
                change_history=args.change_history,
                expected_package_input_sha256=args.expected_package_input_sha256,
            )
        elif args.command == "workflow-plan-same-version-content-rebuild":
            result = plan_same_version_content_rebuild(
                args.solution,
                target_version=args.target_version,
                changed_inputs=args.changed_input,
                expected_package_input_sha256=args.expected_package_input_sha256,
                legacy_baseline_evidence=args.legacy_baseline_evidence,
                failed_candidate_evidence=args.failed_candidate_evidence,
            )
        elif args.command == "workflow-verify-same-version-content-rebuild":
            result = verify_same_version_content_rebuild(
                args.solution,
                legacy_baseline_evidence=args.legacy_baseline_evidence,
            )
        elif args.command == "dependency-plan":
            result = plan_solution_dependencies(
                args.solution, results_path=args.results, workspace_id=args.workspace_id,
            )
        elif args.command.startswith("workbook-publication-"):
            from solution_manager.authoring.workbook_publication import plan_publication, clean_publication, publication_errors, is_public
            from solution_manager.authoring.workbook_updates import _read_external
            if args.command.endswith("-plan"):
                result = plan_publication(args.solution, args.content)
            elif args.command.endswith("-validate"):
                from solution_manager.migration.workbooks import _root, _path, _document, validate_workbooks
                root = _root(args.solution)
                path = _path(root, args.content)
                document = _document(path)
                validation = validate_workbooks(root, selected_only=True, _documents=[(path, document)])
                errors = [error for row in validation["results"] for error in row["errors"]]
                if not is_public(document):
                    errors.append("Public workbook validation requires clean publication metadata.")
                if not errors and args.mode == "authoring":
                    errors = publication_errors(root, document)
                result = {"valid": not errors, "validationScope": args.mode,
                          "errors": errors, "runtimeQualified": False}
            else:
                _, review = _read_external(args.review)
                result = clean_publication(args.solution, args.content, args.expected_sha256, review)
        elif args.command.startswith("workbook-update-"):
            from solution_manager.authoring.workbook_updates import (
                plan_workbook_update, review_workbook_update, apply_workbook_update, _read_external,
            )
            if args.command == "workbook-update-plan":
                result = plan_workbook_update(args.solution, args.content, args.baseline)
            else:
                _, review = _read_external(args.review)
                operation = (review_workbook_update if args.command == "workbook-update-review"
                             else apply_workbook_update)
                result = operation(args.solution, args.content, args.baseline, review)
        elif args.command.startswith("native-workbook-"):
            from solution_manager.authoring.native_workbooks import (
                plan_native_workbook, review_native_workbook, import_native_workbook, load_json,
            )
            from solution_manager.migration.workbooks import validate_workbooks
            if args.command == "native-workbook-plan":
                result = plan_native_workbook(args.solution, args.source)
            elif args.command in ("native-workbook-review", "native-workbook-import"):
                review_path = Path(args.review)
                if any(p.is_symlink() for p in (review_path, *review_path.parents)):
                    raise ValueError("Native review must not use symlinks.")
                operation = (review_native_workbook if args.command == "native-workbook-review"
                             else import_native_workbook)
                result = operation(args.solution, args.source, load_json(review_path.read_bytes()))
            else:
                result = validate_workbooks(args.solution, selected_only=True)
                from solution_manager.authoring.workbook_publication import is_public, publication_errors
                from solution_manager.migration.workbooks import _root, _path, _document
                root = _root(args.solution)
                for row in result["results"]:
                    document = _document(_path(root, row["path"]))
                    if is_public(document):
                        row["errors"].extend(publication_errors(root, document))
                        row["valid"] = not row["errors"]
                result["valid"] = sum(row["valid"] for row in result["results"])
                result["invalid"] = result["total"] - result["valid"]
        elif args.command == "workbook-dependency-plan":
            from solution_manager.authoring.workbook_dependencies import plan_workbook_dependencies
            result = plan_workbook_dependencies(
                args.solution, results_path=args.results, workspace_id=args.workspace_id)
        elif args.command == "workbook-review":
            from solution_manager.authoring.workbook_dependencies import review_workbook_dependencies
            result = review_workbook_dependencies(
                args.solution, plan_path=args.plan, decisions_path=args.decisions,
                expected_plan_sha256=args.plan_sha256, actor=args.actor, reference=args.reference,
                output_directory=args.output_dir)
        elif args.command in {"review-packet", "consolidated-review-plan"}:
            result = build_consolidated_review_packet(
                args.solution,
                detection_results_path=args.results,
                workbook_results_path=args.workbook_results,
                workspace_id=args.workspace_id,
                rule_selectors=args.rule_selectors,
            )
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
        elif args.command == "inspect":
            from solution_manager.migration.workbook_workflow import inspect_content
            result = inspect_content(args.solution)
        elif args.command == "convert":
            from solution_manager.migration.workbook_workflow import convert_content
            result = convert_content(
                args.solution, overwrite=args.overwrite, config_path=args.config,
                overwrite_workbooks=args.overwrite_workbooks,
                rule_id=args.rule_id[0] if args.rule_id else None,
            )
            if args.rule_id:
                configure_logging(args.solution)
        elif args.command == "validate":
            from solution_manager.migration.workbook_workflow import validate_content
            result = validate_content(args.solution)
        elif args.command == "validate-advanced-hunting":
            state = workflow_status(args.solution)
            profile = (
                (state.get("context") or {}).get("workflowProfile")
                if isinstance(state, dict)
                else None
            )
            if profile not in {"authoring", "qualification"}:
                raise ValueError(
                    "Advanced Hunting requires an active authoring or qualification workflow run"
                )
            if profile == "authoring" and not args.run_id:
                raise ValueError(
                    "Authoring Advanced Hunting requires an explicit --run-id; "
                    "no run is inferred"
                )
            target = (
                require_locked_target(args.solution)
                if profile == "qualification"
                else None
            )
            authoring_tenant_id = None
            if profile == "authoring":
                authoring_tenant_id = (state.get("context") or {}).get("tenantId")
                if not isinstance(authoring_tenant_id, str) or not authoring_tenant_id:
                    raise ValueError(
                        "Authoring Advanced Hunting requires the explicit tenant "
                        "stored in the selected workflow run"
                    )
            from solution_manager.qualification.runtime_consent import require_runtime_query_consent

            require_runtime_query_consent(
                args.solution,
                family="defenderXdrQueryFamily",
                provider="graph",
            )
            result = validate_advanced_hunting(
                args.solution,
                tenant_id=(
                    target["tenantId"] if target else authoring_tenant_id
                ),
                provider_gap_evidence=args.provider_gap_evidence,
            )
        elif args.command == "validate-sentinel-sdk":
            from solution_manager.qualification.runtime_consent import require_runtime_query_consent

            require_runtime_query_consent(
                args.solution,
                family="sentinelSourceQueryFamily",
                provider="azure-monitor-sdk",
            )
            target = require_locked_target(args.solution)
            result = validate_sentinel_sdk(
                args.solution,
                target=target,
                request_timeout_seconds=args.request_timeout_seconds,
                family_timeout_seconds=args.family_timeout_seconds,
                provider_gap_evidence=args.provider_gap_evidence,
            )
        elif args.command == "record-runtime-validation":
            result = record_runtime_validation(
                args.solution,
                provider=args.provider,
                results_path=args.results,
                provider_gap_evidence=args.provider_gap_evidence,
                source_provider=args.source_provider,
            )
        elif args.command in workbook_commands:
            from solution_manager.migration import workbook_workflow as workbooks
            if args.command.startswith("workflow-arm-preflight-"):
                from solution_manager.qualification import workbook_preflight_workflow as preflight
                if args.command == "workflow-arm-preflight-plan":
                    result = preflight.create_plan(args.solution)
                elif args.command == "workflow-arm-preflight-review":
                    result = preflight.review(
                        args.solution, expected_sha256=args.preflight_plan_sha256,
                        actor=args.actor, reference=args.reference, approved=args.decision == "approved",
                    )
                elif args.command == "workflow-arm-preflight-revoke":
                    result = preflight.revoke(args.solution, actor=args.actor, reference=args.reference)
                else:
                    result = preflight.execute(
                        args.solution, expected_sha256=args.preflight_plan_sha256,
                        state_dir=args.state_dir,
                    )
            elif args.command == "workflow-arm-candidate":
                result = workbooks.create_candidate(args.solution, validation_receipt=args.validation_receipt,
                                                    toolkit_root=args.toolkit_root)
            elif args.command in {"workflow-arm-plan", "workflow-workbook-contract-plan"}:
                result = workbooks.plan_candidate(args.solution,
                    target=json.loads(Path(args.target).read_text(encoding="utf-8-sig")),
                    selected_flags=json.loads(Path(args.selected_flags).read_text(encoding="utf-8-sig")),
                    contract_only=args.command == "workflow-workbook-contract-plan")
            elif args.command == "workflow-arm-review-scope":
                result = workbooks.review_scope(args.solution, actor=args.actor, reference=args.reference,
                    approved=args.decision == "approved", expected_plan_sha256=args.plan_sha256)
            elif args.command == "workflow-arm-withdraw-scope":
                result = workbooks.withdraw_scope(args.solution, actor=args.actor, reference=args.reference)
            elif args.command == "workflow-arm-execute":
                result = workbooks.execute_candidate(args.solution, expected_plan_sha256=args.plan_sha256,
                    actor=args.actor, reference=args.reference, confirmation=args.confirmation)
            elif args.command in {"workflow-arm-reconcile", "workflow-arm-import"}:
                action = workbooks.reconcile_attempt if args.command == "workflow-arm-reconcile" else workbooks.import_arm_only
                result = action(args.solution, attempt=args.attempt,
                    observation=args.observation, actor=args.actor, reference=args.reference)
            else:
                result = workbooks.import_contract(args.solution, evidence=args.evidence, contract_only=args.contract_only)
        elif args.command == "workflow-init":
            if args.new_run and args.run_id:
                raise ValueError("--new-run and --run-id cannot be combined")
            if (
                args.confirm_configured_target
                and args.workflow_profile != "qualification"
            ):
                raise ValueError(
                    "--confirm-configured-target is only valid for Qualification"
                )
            locked_context = None
            if not args.new_run:
                try:
                    current = workflow_status(args.solution)
                except ValueError as exc:
                    if "workflow state does not exist" not in str(exc):
                        raise
                else:
                    context = current.get("context") or {}
                    if (
                        context.get("workflowProfile") == "qualification"
                        and context.get("targetContextLocked") is True
                    ):
                        locked_context = context
            target = None
            if args.workflow_profile == "qualification":
                target = resolve_qualification_target(
                    args.solution,
                    tenant_id=args.tenant_id,
                    subscription_id=args.subscription_id,
                    workspace_resource_id=args.workspace_resource_id,
                    workspace_customer_id=args.workspace_customer_id,
                    confirm_configured_target=args.confirm_configured_target,
                    locked_context=locked_context,
                )
            result = initialize_workflow(
                args.solution,
                tenant_id=target["tenantId"] if target else args.tenant_id,
                subscription_id=(
                    target["subscriptionId"] if target else args.subscription_id
                ),
                workspace_resource_id=(
                    target["workspaceResourceId"] if target else args.workspace_resource_id
                ),
                workspace_customer_id=(
                    target["workspaceCustomerId"] if target else args.workspace_customer_id
                ),
                version_bump=args.version_bump,
                target_version=args.target_version,
                workflow_profile=args.workflow_profile,
                yolo=True if args.yolo else None,
                campaign_id=args.campaign_id,
                new_run=args.new_run,
                workbook_capability_version=(
                    1 if args.new_run or not existing_artifact_path(args.solution, "workflow-state.json").exists()
                    or args.arm_validation_method is not None else None
                ),
                arm_validation_method=args.arm_validation_method,
            )
        elif args.command == "workflow-budget":
            result = budget_summary(args.solution, args.campaign_id)
        elif args.command == "workflow-budget-extend":
            result = extend_budget(
                args.solution,
                args.campaign_id,
                dimension=args.dimension,
                new_limit=args.new_limit,
                actor=args.actor,
                reason=args.reason,
                evidence_reference=args.reference,
            )
        elif args.command == "workflow-budget-reconcile":
            result = reconcile_pending_operation(
                args.solution,
                args.campaign_id,
                args.operation_id,
                status=args.status,
                elapsed_seconds=args.elapsed_seconds,
                actor=args.actor,
                reason=args.reason,
                evidence_reference=args.reference,
            )
        elif args.command == "workflow-budget-reconcile-legacy":
            baseline_path = Path(args.baseline).expanduser().resolve()
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            result = reconcile_legacy_usage(
                args.solution,
                args.campaign_id,
                consumed=baseline,
                actor=args.actor,
                reason=args.reason,
                evidence_reference=args.reference,
            )
        elif args.command == "workflow-budget-deadline":
            result = set_observation_deadline(
                args.solution,
                args.campaign_id,
                test_id=args.test_id,
                deadline_at=args.deadline_at,
                approval_reference=args.approval_reference,
                actor=args.actor,
                reason=args.reason,
            )
        elif args.command == "workflow-status":
            result = workflow_status(args.solution)
            result["runtimeQueryConsent"] = runtime_query_consent_status(
                args.solution,
                source_provider=getattr(args, "source_provider", None),
            )
        elif args.command == "workflow-next":
            result = next_workflow_stage(args.solution)
        elif args.command == "workflow-status-reminder":
            result = build_migration_status_reminder(
                args.solution,
                run_id=args.run_id,
                persist_cursor=not args.no_persist_cursor,
            )
        elif args.command == "workflow-execution-owner":
            if args.action == "release":
                result = release_execution_ownership(
                    args.solution,
                    owner_id=args.owner_id,
                    operation=args.operation,
                    run_id=args.run_id,
                )
            else:
                result = claim_execution_ownership(
                    args.solution,
                    owner_id=args.owner_id,
                    operation=args.operation,
                    scope=_json_object_arg(args.scope, flag_name="--scope"),
                    run_id=args.run_id,
                )
        elif args.command == "workflow-forward-approval":
            scope_dict = _json_object_arg(args.exact_scope, flag_name="--exact-scope")
            if args.action == "verify":
                result = verify_forwarded_approval(
                    args.solution,
                    owner_id=args.forwarded_to_owner_id,
                    operation=args.operation,
                    exact_scope=scope_dict,
                    approval_sha256=args.approval_sha256,
                    run_id=args.run_id,
                )
            else:
                if not args.approved_by:
                    raise ValueError("--approved-by is required when --action forward")
                result = forward_explicit_approval(
                    args.solution,
                    operation=args.operation,
                    approved_by=args.approved_by,
                    forwarded_to_owner_id=args.forwarded_to_owner_id,
                    exact_scope=scope_dict,
                    run_id=args.run_id,
                    reference=args.reference,
                )
        elif args.command == "workflow-recover-conversion-evidence":
            result = recover_conversion_evidence(args.solution)
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
        elif args.command == "workflow-yolo":
            if not args.run_id:
                raise ValueError("workflow-yolo requires an explicit --run-id")
            result = run_yolo_authoring(args.solution)
        elif args.command == "workflow-yolo-refresh":
            if not args.run_id:
                raise ValueError("workflow-yolo-refresh requires an explicit --run-id")
            result = refresh_yolo_authoring(args.solution)
        else:
            result = runtime_validation_plan(args.solution)
    except (OSError, RuntimeError, ValueError, yaml.YAMLError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        if selection is not None:
            reset_run_selection(selection)

    _print(result)
    if args.command == "validate" and result["invalid"]:
        return 1
    if args.command == "validate-advanced-hunting" and (
        result["invalid"] or result["blocked"]
    ):
        return 1
    if args.command == "validate-sentinel-sdk" and (
        result["invalid"] or result["blocked"] or not result.get("familyComplete", False)
    ):
        return 1
    if args.command == "record-runtime-validation" and (
        result["invalid"] or result["blocked"]
    ):
        return 1
    if args.command in ("deploy", "deploy-analytic-rules") and result["failed"]:
        return 1
    if args.command == "plan-arm-template-acceptance-batch" and result.get(
        "status"
    ) != "ready":
        return 1
    if args.command == "deploy-arm-template-acceptance-batch" and result.get(
        "status"
    ) != "accepted":
        return 1
    if args.command == "complete-alert-parity" and result["status"] != "passed":
        return 1
    if args.command == "abort-alert-parity" and result["status"] != "aborted":
        return 1
    if (
        args.command == "verify-delegated-app-readback"
        and result.get("status") != "readback-verified-private-config-completed"
    ):
        return 1
    if (
        args.command == "diagnose-app-readback-scopes"
        and result.get("status") != "required-scopes-present"
    ):
        return 1
    if (
        args.command == "verify-delegated-app-permission-update"
        and result.get("status") != "manual-permission-update-verified"
    ):
        return 1
    if (
        args.command == "package-selection-plan"
        and result.get("status") != "ready"
    ):
        return 1
    if (
        args.command == "package-selection-apply"
        and result.get("status") != "applied"
    ):
        return 1
    if args.command == "convert" and (
        result["needsReview"] or result["conflicts"] or result.get("workbooks", {}).get("selectedBlocked", 0)
    ):
        return 1
    if args.command == "package-v3-1" and result.get("status") == "blocked":
        return 1
    if args.command == "workbook-publication-validate" and not result["valid"]:
        return 1
    if args.command in {"workflow-arm-execute", "workflow-workbook-contract-import"} and result.get("accepted") is not True:
        return 1
    if args.command == "workflow-arm-preflight-execute" and result.get("status") != "ready":
        return 1
    if args.command == "dependency-plan" and args.results and any(
        item["validation"]["status"] != "passed" for item in result["results"]
    ):
        return 1
    if (
        args.command == "workflow-complete-stage"
        and result["status"] != "passed"
    ):
        return 1
    if args.command == "workflow-yolo" and (
        result["status"] != "active"
        or result.get("validationStatus") == "blocked"
    ):
        return 1
    if args.command == "native-workbook-validate" and result["invalid"]:
        return 1
    if args.command == "native-workbook-import" and result["validation"]["invalid"]:
        return 1
    if args.command == "native-workbook-plan" and any(q["blockers"] for q in result["queries"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
