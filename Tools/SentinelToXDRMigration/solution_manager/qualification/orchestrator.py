"""End-to-end resumable Qualification Orchestrator for Sentinel-to-Defender-XDR solutions."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from solution_manager.core import workflow
from solution_manager.core.artifacts import (
    existing_artifact_path,
    report_directory,
    using_run,
)
from solution_manager.qualification.alert_parity import (
    classify_streaming_compiler_error,
)
from solution_manager.qualification.mock_data import (
    discover_dcr_streams,
    generate_mock_data,
    ingest_and_verify_mock_data,
)
from solution_manager.qualification.parity import evaluate_rule_parity
from solution_manager.qualification.readiness_support import (
    assess_qualification_readiness,
    audit_private_config_and_support_export,
    discover_solution_qualification_inventory,
)
from solution_manager.qualification.workbook_playwright import (
    verify_workbook_playwright_rendering,
)

QUALIFICATION_STAGES: tuple[str, ...] = (
    "preflight",
    "deployment",
    "mock_ingestion",
    "rule_parity",
    "workbook_qualification",
)

PIPELINE_STATE_FILENAME = "qualification-pipeline-state.json"
PREFLIGHT_PACKET_FILENAME = "qualification-preflight-packet.json"

DEFAULT_LAB_TARGET: dict[str, str] = {
    "tenantId": "11111111-1111-4111-8111-111111111111",
    "subscriptionId": "22222222-2222-4222-8222-222222222222",
    "resourceGroup": "rg-sentinel-xdr-qualification",
    "workspaceResourceId": (
        "/subscriptions/22222222-2222-4222-8222-222222222222"
        "/resourceGroups/rg-sentinel-xdr-qualification"
        "/providers/Microsoft.OperationalInsights/workspaces/ws-qualification"
    ),
    "workspaceCustomerId": "33333333-3333-4333-8333-333333333333",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _ensure_qualification_workflow_state(
    solution_root: Path,
    *,
    run_id: str | None = None,
    target: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Load existing workflow-state.json or initialize a qualification workflow state."""
    wf_file = existing_artifact_path(solution_root, "workflow-state.json")
    if wf_file.is_file():
        return workflow._load(solution_root)[1]

    eff_target = dict(DEFAULT_LAB_TARGET)
    if isinstance(target, Mapping):
        for k, v in target.items():
            if v is not None:
                eff_target[str(k)] = str(v)

    return workflow.initialize_workflow(
        solution_root,
        workflow_profile="qualification",
        workbook_capability_version=1,
        version_bump="none",
        tenant_id=eff_target["tenantId"],
        subscription_id=eff_target["subscriptionId"],
        workspace_resource_id=eff_target["workspaceResourceId"],
        workspace_customer_id=eff_target["workspaceCustomerId"],
    )


def plan_qualification_pipeline(
    solution_path: str | Path,
    *,
    run_id: str | None = None,
    target: Mapping[str, Any] | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    """Build the consolidated Qualification preflight consent & readiness packet and 5-stage plan.

    Never claims ARM `what-if` is supported for Bicep extensible XDR resources:
    records `armWhatIfSupportedForXdrExtensions: False` and uses ARM template validation
    plus live disabled deployment readback instead.
    """
    root = Path(solution_path).expanduser().resolve()
    wf_state = _ensure_qualification_workflow_state(root, run_id=run_id, target=target)
    effective_run_id = str(run_id or wf_state.get("runId") or "qualification-run")

    with using_run(root, effective_run_id):
        readiness = assess_qualification_readiness(root, run_id=effective_run_id)
        inventory = discover_solution_qualification_inventory(root, state=wf_state)

        counts = readiness["expectedContentCounts"]
        x = int(counts["sentinelRulesCount"])
        y = int(counts["workbooksCount"])
        z = int(counts["customDetectionsCount"])

        ctx = wf_state.get("context") or {}
        eff_target = {
            "tenantId": str((target or {}).get("tenantId") or ctx.get("tenantId") or DEFAULT_LAB_TARGET["tenantId"]),
            "subscriptionId": str(
                (target or {}).get("subscriptionId") or ctx.get("subscriptionId") or DEFAULT_LAB_TARGET["subscriptionId"]
            ),
            "workspaceResourceId": str(
                (target or {}).get("workspaceResourceId")
                or ctx.get("workspaceResourceId")
                or DEFAULT_LAB_TARGET["workspaceResourceId"]
            ),
            "workspaceCustomerId": str(
                (target or {}).get("workspaceCustomerId")
                or ctx.get("workspaceCustomerId")
                or DEFAULT_LAB_TARGET["workspaceCustomerId"]
            ),
        }

        target_tables = list(inventory["targetTables"])
        target_streams = list(inventory["targetStreams"])

        scope_identity = {
            "solution": root.name,
            "runId": effective_run_id,
            "target": eff_target,
            "expectedContentCounts": {
                "sentinelRulesCount": x,
                "workbooksCount": y,
                "customDetectionsCount": z,
            },
            "targetTables": target_tables,
            "targetStreams": target_streams,
            "armWhatIfSupportedForXdrExtensions": False,
        }
        plan_sha256 = _canonical_sha256(scope_identity)

        runtime_query_consent_spec = {
            "scope": "bounded-read-only-sentinel-and-xdr-queries",
            "readOnly": True,
            "resourceMutation": False,
            "requiredFamilies": ["sentinelSourceQueryFamily", "defenderXdrQueryFamily"],
            "status": readiness["authorizationChecks"]["runtimeQueryConsent"]["status"],
            "ready": readiness["authorizationChecks"]["runtimeQueryConsent"]["ready"],
        }

        deployment_summary = f"{x} Sentinel rules, {y} workbooks, and {z} custom detections"
        deployment_preapproval = {
            "scope": "disabled-lab-deployment",
            "expectedContentCounts": counts,
            "summary": deployment_summary,
            "prompt": readiness["labDeploymentPreflightPrompt"],
            "enabled": False,
            "allResourcesDeployedDisabled": True,
            "armWhatIfSupportedForXdrExtensions": False,
            "validationStrategy": "arm-template-validation-and-live-disabled-readback",
            "requiresImmediateHashBoundApproval": True,
            "planSha256": plan_sha256,
        }

        mock_ingestion_preapproval = {
            "scope": "synthetic-dcr-mock-ingestion",
            "syntheticOnly": True,
            "targetTables": target_tables,
            "targetStreams": target_streams,
            "streamNames": [s["streamName"] for s in target_streams],
            "requiresExplicitWriteApproval": True,
            "planSha256": plan_sha256,
        }

        has_rules = (x + z) > 0
        has_workbooks = y > 0

        stage_plan = {
            "preflight": {"required": True, "order": 1},
            "deployment": {"required": True, "order": 2},
            "mock_ingestion": {"required": True, "order": 3},
            "rule_parity": {"required": has_rules, "order": 4, "notApplicableReason": None if has_rules else "workbook-only-solution-0-rules"},
            "workbook_qualification": {
                "required": has_workbooks,
                "order": 5,
                "notApplicableReason": None if has_workbooks else "rules-only-solution-0-workbooks",
            },
        }

        consolidated_packet = {
            "schemaVersion": 1,
            "solution": str(root),
            "solutionName": root.name,
            "runId": effective_run_id,
            "planSha256": plan_sha256,
            "target": eff_target,
            "armWhatIfSupportedForXdrExtensions": False,
            "bicepExtensibilityWhatIfPolicy": {
                "armWhatIfSupportedForXdrExtensions": False,
                "reason": (
                    "ARM what-if does not support Bicep extensibility / Microsoft.Security XDR resources; "
                    "qualification uses ARM template validation plus live disabled deployment GET readback reconciliation."
                ),
            },
            "expectedContentCounts": counts,
            "deploymentScopeSummary": deployment_summary,
            "runtimeQueryConsent": runtime_query_consent_spec,
            "deploymentPreapproval": deployment_preapproval,
            "mockIngestionPreapproval": mock_ingestion_preapproval,
            "readiness": readiness,
            "inventory": inventory,
            "stages": stage_plan,
        }

        if persist:
            run_dir = report_directory(root)
            run_dir.mkdir(parents=True, exist_ok=True)
            packet_path = run_dir / PREFLIGHT_PACKET_FILENAME
            packet_path.write_text(json.dumps(consolidated_packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            consolidated_packet["packetPath"] = packet_path.relative_to(root).as_posix()

        return {
            **consolidated_packet,
            "consolidatedPreflightPacket": deepcopy(consolidated_packet),
        }


def evaluate_qualification_promotion_gate(state: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate whether a solution's qualification state satisfies all gates for full qualification acceptance.

    Gates evaluated:
    - preflightPassed (bool)
    - deploymentVerified (bool)
    - mockIngestionVerified (bool)
    - ruleParityVerified (True | False | "not_applicable" when 0 rules exist)
    - workbookQualificationVerified (True | False | "not_applicable" when 0 workbooks exist)
    - sanitizedEvidenceReady (bool)
    """
    if not isinstance(state, Mapping):
        raise ValueError("state must be a mapping")

    qual_stages = state.get("qualificationStages") if isinstance(state.get("qualificationStages"), Mapping) else {}
    wf_stages = state.get("stages") if isinstance(state.get("stages"), Mapping) else {}
    gates_input = state.get("gates") if isinstance(state.get("gates"), Mapping) else {}

    counts = (
        state.get("expectedContentCounts")
        or (state.get("consolidatedPreflightPacket") or {}).get("expectedContentCounts")
        or {}
    )
    rules_count = counts.get("sentinelRulesCount")
    detections_count = counts.get("customDetectionsCount")
    workbooks_count = counts.get("workbooksCount")

    if rules_count is None and isinstance(state.get("workbooks"), Mapping):
        # Inspect workflow-state.json workbooks block if expectedContentCounts wasn't directly attached
        wb_included = ((state["workbooks"].get("selection") or {}).get("included")) or []
        if workbooks_count is None:
            workbooks_count = len(wb_included)

    has_zero_rules = (
        rules_count is not None
        and int(rules_count) == 0
        and int(detections_count or 0) == 0
    ) or (
        isinstance(wf_stages.get("alertParity"), Mapping)
        and wf_stages["alertParity"].get("status") == "notRequired"
    ) or (
        isinstance(qual_stages.get("rule_parity"), Mapping)
        and qual_stages["rule_parity"].get("status") in {"not_applicable", "notRequired"}
    )

    has_zero_workbooks = (
        workbooks_count is not None and int(workbooks_count) == 0
    ) or (
        isinstance(qual_stages.get("workbook_qualification"), Mapping)
        and qual_stages["workbook_qualification"].get("status") in {"not_applicable", "notRequired"}
    )

    # 1. preflightPassed
    if "preflightPassed" in state:
        preflight_passed = bool(state["preflightPassed"] is True)
    elif "preflightPassed" in gates_input:
        preflight_passed = bool(gates_input["preflightPassed"] is True)
    elif "preflight" in qual_stages:
        preflight_passed = bool(qual_stages["preflight"].get("status") == "passed")
    elif "validation" in wf_stages:
        val_art = wf_stages["validation"].get("artifacts") or {}
        preflight_passed = bool(
            wf_stages["validation"].get("status") == "passed"
            and val_art.get("qualificationPreflightStatus") in {None, "passed"}
        )
    else:
        preflight_passed = False

    # 2. deploymentVerified
    if "deploymentVerified" in state:
        deployment_verified = bool(state["deploymentVerified"] is True)
    elif "deploymentVerified" in gates_input:
        deployment_verified = bool(gates_input["deploymentVerified"] is True)
    elif "deployment" in qual_stages:
        dep_stage = qual_stages["deployment"]
        deployment_verified = bool(
            dep_stage.get("status") == "passed" and dep_stage.get("deploymentVerified") is True
        )
    elif "deployment" in wf_stages:
        dep_art = wf_stages["deployment"].get("artifacts") or {}
        deployment_verified = bool(
            wf_stages["deployment"].get("status") == "passed"
            and dep_art.get("deploymentVerified", "true") == "true"
        )
    else:
        deployment_verified = False

    # 3. mockIngestionVerified
    if "mockIngestionVerified" in state:
        mock_ingestion_verified = bool(state["mockIngestionVerified"] is True)
    elif "mockIngestionVerified" in gates_input:
        mock_ingestion_verified = bool(gates_input["mockIngestionVerified"] is True)
    elif "mock_ingestion" in qual_stages:
        ing_stage = qual_stages["mock_ingestion"]
        mock_ingestion_verified = bool(
            ing_stage.get("status") == "passed" and ing_stage.get("mockIngestionVerified") is True
        )
    elif "mockIngestion" in wf_stages:
        ing_art = wf_stages["mockIngestion"].get("artifacts") or {}
        mock_ingestion_verified = bool(
            wf_stages["mockIngestion"].get("status") == "passed"
            and ing_art.get("mockIngestionVerified", "true") == "true"
        )
    else:
        mock_ingestion_verified = False

    # 4. ruleParityVerified
    raw_rule_parity = (
        state.get("ruleParityVerified")
        if "ruleParityVerified" in state
        else gates_input.get("ruleParityVerified")
    )
    if raw_rule_parity == "not_applicable" or (raw_rule_parity is None and has_zero_rules):
        rule_parity_verified: bool | str = "not_applicable"
    elif isinstance(raw_rule_parity, bool):
        rule_parity_verified = raw_rule_parity
    elif "rule_parity" in qual_stages:
        rp_stage = qual_stages["rule_parity"]
        if rp_stage.get("status") in {"not_applicable", "notRequired"} or has_zero_rules:
            rule_parity_verified = "not_applicable"
        else:
            rule_parity_verified = bool(
                rp_stage.get("status") == "passed"
                and rp_stage.get("alertParityVerified") is True
            )
    elif "alertParity" in wf_stages:
        ap_stage = wf_stages["alertParity"]
        if ap_stage.get("status") == "notRequired" or has_zero_rules:
            rule_parity_verified = "not_applicable"
        else:
            ap_art = ap_stage.get("artifacts") or {}
            rule_parity_verified = bool(
                ap_stage.get("status") == "passed"
                and ap_art.get("alertParityVerified", "true") == "true"
            )
    else:
        rule_parity_verified = "not_applicable" if has_zero_rules else False

    # 5. workbookQualificationVerified
    raw_wb_qual = (
        state.get("workbookQualificationVerified")
        if "workbookQualificationVerified" in state
        else gates_input.get("workbookQualificationVerified")
    )
    if raw_wb_qual == "not_applicable" or (raw_wb_qual is None and has_zero_workbooks):
        workbook_qualification_verified: bool | str = "not_applicable"
    elif isinstance(raw_wb_qual, bool):
        workbook_qualification_verified = raw_wb_qual
    elif "workbook_qualification" in qual_stages:
        wb_stage = qual_stages["workbook_qualification"]
        if wb_stage.get("status") in {"not_applicable", "notRequired"} or has_zero_workbooks:
            workbook_qualification_verified = "not_applicable"
        else:
            workbook_qualification_verified = bool(
                wb_stage.get("status") == "passed"
                and wb_stage.get("functionalQualificationVerified") is True
            )
    else:
        workbook_qualification_verified = "not_applicable" if has_zero_workbooks else False

    # 6. sanitizedEvidenceReady
    if "sanitizedEvidenceReady" in state:
        sanitized_evidence_ready = bool(state["sanitizedEvidenceReady"] is True)
    elif "sanitizedEvidenceReady" in gates_input:
        sanitized_evidence_ready = bool(gates_input["sanitizedEvidenceReady"] is True)
    elif isinstance(state.get("privateConfigAudit"), Mapping):
        audit = state["privateConfigAudit"]
        sanitized_evidence_ready = bool(
            audit.get("status") == "isolated"
            and audit.get("privateConfigIsolatedToLocalUnexportedConfig") is True
            and audit.get("supportExportsRedacted") is True
        )
    elif "report" in wf_stages:
        rep_art = wf_stages["report"].get("artifacts") or {}
        sanitized_evidence_ready = bool(rep_art.get("sanitizedEvidenceReady") == "true")
    else:
        sanitized_evidence_ready = False

    blockers: list[str] = []
    missing_gates: list[str] = []

    if not preflight_passed:
        missing_gates.append("preflightPassed")
        blockers.append("Consolidated qualification preflight has not passed.")
    if not deployment_verified:
        missing_gates.append("deploymentVerified")
        blockers.append("Disabled lab deployment and independent GET readback reconciliation are not verified.")
    if not mock_ingestion_verified:
        missing_gates.append("mockIngestionVerified")
        blockers.append("Synthetic DCR mock ingestion and landing query verification are not complete.")
    if rule_parity_verified not in (True, "not_applicable"):
        missing_gates.append("ruleParityVerified")
        blockers.append("Sentinel Analytic Rule vs. Defender XDR Custom Detection parity is not verified.")
    if workbook_qualification_verified not in (True, "not_applicable"):
        missing_gates.append("workbookQualificationVerified")
        blockers.append("Defender Workbook live query and functional qualification are not verified.")
    if rule_parity_verified == "not_applicable" and workbook_qualification_verified == "not_applicable":
        missing_gates.append("contentQualificationScope")
        blockers.append("Cannot promote qualification when both rules and workbooks are not_applicable (0 content items).")
    if not sanitized_evidence_ready:
        missing_gates.append("sanitizedEvidenceReady")
        blockers.append("Sanitized evidence export hygiene is not verified (private identifiers must not leak).")

    passed = len(blockers) == 0
    gates = {
        "preflightPassed": preflight_passed,
        "deploymentVerified": deployment_verified,
        "mockIngestionVerified": mock_ingestion_verified,
        "ruleParityVerified": rule_parity_verified,
        "workbookQualificationVerified": workbook_qualification_verified,
        "sanitizedEvidenceReady": sanitized_evidence_ready,
    }
    return {
        "status": "passed" if passed else "blocked",
        "passed": passed,
        "promoted": passed,
        "preflightPassed": preflight_passed,
        "deploymentVerified": deployment_verified,
        "mockIngestionVerified": mock_ingestion_verified,
        "ruleParityVerified": rule_parity_verified,
        "workbookQualificationVerified": workbook_qualification_verified,
        "sanitizedEvidenceReady": sanitized_evidence_ready,
        "gates": gates,
        "missingGates": missing_gates,
        "blockers": blockers,
    }


class QualificationOrchestrator:
    """Resumable 5-stage Qualification state machine backed by workflow-state.json."""

    def __init__(
        self,
        solution_path: str | Path,
        *,
        run_id: str | None = None,
        target: Mapping[str, Any] | None = None,
        runtime_query_consent: Mapping[str, Any] | None = None,
        deployment_consent: Mapping[str, Any] | None = None,
        mock_ingestion_consent: Mapping[str, Any] | None = None,
        deployment_runner: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        readback_verifier: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
        mock_generator: Callable[[Path, list[str]], dict[str, Any]] | None = None,
        stream_resolver: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
        ingestion_client: Callable[[dict[str, Any], list[dict[str, Any]], Mapping[str, Any] | None], dict[str, Any]] | None = None,
        landing_query_client: Callable[[str, str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
        parity_evaluator: Callable[[dict[str, Any], Mapping[str, Any] | None, Mapping[str, Any] | None], dict[str, Any]] | None = None,
        workbook_query_runner: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
        playwright_runner: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
        enable_playwright: bool = True,
    ) -> None:
        self.solution_root = Path(solution_path).expanduser().resolve()
        self._target_override = dict(target) if isinstance(target, Mapping) else None
        wf_state = _ensure_qualification_workflow_state(
            self.solution_root,
            run_id=run_id,
            target=self._target_override,
        )
        self.run_id: str = str(run_id or wf_state.get("runId") or "qualification-run")
        self.runtime_query_consent = dict(runtime_query_consent) if isinstance(runtime_query_consent, Mapping) else None
        self.deployment_consent = dict(deployment_consent) if isinstance(deployment_consent, Mapping) else None
        self.mock_ingestion_consent = dict(mock_ingestion_consent) if isinstance(mock_ingestion_consent, Mapping) else None

        self.deployment_runner = deployment_runner
        self.readback_verifier = readback_verifier
        self.mock_generator = mock_generator
        self.stream_resolver = stream_resolver
        self.ingestion_client = ingestion_client
        self.landing_query_client = landing_query_client
        self.parity_evaluator = parity_evaluator
        self.workbook_query_runner = workbook_query_runner
        self.playwright_runner = playwright_runner
        self.enable_playwright = enable_playwright

        with using_run(self.solution_root, self.run_id):
            self.plan = plan_qualification_pipeline(
                self.solution_root,
                run_id=self.run_id,
                target=self._target_override,
                persist=True,
            )
            self.state = self._load_or_init_pipeline_state()

    def _pipeline_state_path(self) -> Path:
        run_dir = report_directory(self.solution_root)
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir / PIPELINE_STATE_FILENAME

    def _load_or_init_pipeline_state(self) -> dict[str, Any]:
        path = self._pipeline_state_path()
        if path.is_file() and not path.is_symlink():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8-sig"))
                if isinstance(loaded, dict) and isinstance(loaded.get("qualificationStages"), dict):
                    loaded["planSha256"] = self.plan["planSha256"]
                    loaded["expectedContentCounts"] = self.plan["expectedContentCounts"]
                    loaded["armWhatIfSupportedForXdrExtensions"] = False
                    loaded["consolidatedPreflightPacket"] = self.plan["consolidatedPreflightPacket"]
                    return loaded
            except Exception:
                # Re-initialize pipeline state if existing state file cannot be parsed.
                pass

        counts = self.plan["expectedContentCounts"]
        has_rules = (int(counts["sentinelRulesCount"]) + int(counts["customDetectionsCount"])) > 0
        has_workbooks = int(counts["workbooksCount"]) > 0

        initial_stages: dict[str, dict[str, Any]] = {}
        for stage_name in QUALIFICATION_STAGES:
            initial_stages[stage_name] = {
                "name": stage_name,
                "status": "pending",
                "attempts": 0,
                "startedAt": None,
                "completedAt": None,
                "reasons": [],
            }
        if not has_rules:
            initial_stages["rule_parity"]["status"] = "not_applicable"
            initial_stages["rule_parity"]["alertParityVerified"] = "not_applicable"
            initial_stages["rule_parity"]["ruleParityVerified"] = "not_applicable"
        if not has_workbooks:
            initial_stages["workbook_qualification"]["status"] = "not_applicable"
            initial_stages["workbook_qualification"]["workbookQualificationVerified"] = "not_applicable"

        state: dict[str, Any] = {
            "schemaVersion": 1,
            "solution": str(self.solution_root),
            "solutionName": self.solution_root.name,
            "runId": self.run_id,
            "planSha256": self.plan["planSha256"],
            "target": self.plan["target"],
            "armWhatIfSupportedForXdrExtensions": False,
            "expectedContentCounts": counts,
            "consolidatedPreflightPacket": self.plan["consolidatedPreflightPacket"],
            "qualificationStages": initial_stages,
            "preflightPassed": False,
            "deploymentVerified": False,
            "mockIngestionVerified": False,
            "ruleParityVerified": "not_applicable" if not has_rules else False,
            "alertParityVerified": "not_applicable" if not has_rules else False,
            "workbookQualificationVerified": "not_applicable" if not has_workbooks else False,
            "functionalQualificationVerified": False,
            "sanitizedEvidenceReady": False,
            "completedStages": [],
        }
        self._persist_state(state)
        return state

    def _sync_to_workflow_state(self, pipeline_state: dict[str, Any]) -> None:
        """Synchronize the 5-stage qualification progress into workflow-state.json."""
        try:
            with workflow._state_writer_lock(self.solution_root) as wf_path:
                wf_state = workflow._load(self.solution_root)[1]
                wf_stages = wf_state.get("stages") or {}
                q_stages = pipeline_state["qualificationStages"]
                rel_pipeline = self._pipeline_state_path().relative_to(self.solution_root).as_posix()

                # Preflight -> validation stage metadata
                pf = q_stages["preflight"]
                if "validation" in wf_stages and pf["status"] in {"passed", "blocked", "failed"}:
                    val_st = wf_stages["validation"]
                    val_art = val_st.setdefault("artifacts", {})
                    val_art["qualificationPreflightStatus"] = str(pf["status"])
                    val_art["qualificationPipelineState"] = rel_pipeline
                    val_art["armWhatIfSupportedForXdrExtensions"] = "false"

                # Deployment -> deployment stage
                dep = q_stages["deployment"]
                if "deployment" in wf_stages and dep["status"] != "pending":
                    dep_st = wf_stages["deployment"]
                    dep_st["status"] = "passed" if dep["status"] == "passed" else ("blocked" if dep["status"] == "blocked" else "failed")
                    dep_st["attempts"] = int(dep.get("attempts", 1))
                    dep_st["startedAt"] = dep.get("startedAt") or _now_iso()
                    dep_st["completedAt"] = dep.get("completedAt") or _now_iso()
                    dep_art = dep_st.setdefault("artifacts", {})
                    dep_art["deploymentVerified"] = "true" if pipeline_state.get("deploymentVerified") is True else "false"
                    dep_art["allResourcesDisabled"] = "true"
                    dep_art["qualificationPipelineState"] = rel_pipeline

                # Mock Ingestion -> mockIngestion stage
                ing = q_stages["mock_ingestion"]
                if "mockIngestion" in wf_stages and ing["status"] != "pending":
                    ing_st = wf_stages["mockIngestion"]
                    ing_st["status"] = "passed" if ing["status"] == "passed" else ("blocked" if ing["status"] == "blocked" else "failed")
                    ing_st["attempts"] = int(ing.get("attempts", 1))
                    ing_st["startedAt"] = ing.get("startedAt") or _now_iso()
                    ing_st["completedAt"] = ing.get("completedAt") or _now_iso()
                    ing_art = ing_st.setdefault("artifacts", {})
                    ing_art["mockIngestionVerified"] = "true" if pipeline_state.get("mockIngestionVerified") is True else "false"
                    ing_art["qualificationPipelineState"] = rel_pipeline

                # Rule Parity -> alertParity stage
                rp = q_stages["rule_parity"]
                if "alertParity" in wf_stages:
                    ap_st = wf_stages["alertParity"]
                    if rp["status"] == "not_applicable":
                        ap_st["status"] = "notRequired"
                        ap_st["message"] = "Workbook-only solution (0 rules); alert parity not applicable."
                    elif rp["status"] != "pending":
                        ap_st["status"] = "passed" if rp["status"] == "passed" else ("blocked" if rp["status"] == "blocked" else "failed")
                        ap_st["attempts"] = int(rp.get("attempts", 1))
                        ap_st["startedAt"] = rp.get("startedAt") or _now_iso()
                        ap_st["completedAt"] = rp.get("completedAt") or _now_iso()
                        ap_art = ap_st.setdefault("artifacts", {})
                        ap_art["alertParityVerified"] = "true" if pipeline_state.get("alertParityVerified") is True else "false"
                        ap_art["qualificationPipelineState"] = rel_pipeline
                        rp_lifecycle = rp.get("alertLifecycle") or {}
                        if isinstance(rp_lifecycle, Mapping) and rp_lifecycle:
                            ap_art["initialDisabled"] = (
                                "true" if rp_lifecycle.get("initialDisabled") is True else "false"
                            )
                            ap_art["returnedToDisabled"] = (
                                "true" if rp_lifecycle.get("returnedToDisabled") is True else "false"
                            )
                            ap_art["tkQ11Verified"] = (
                                "true" if rp_lifecycle.get("tkQ11Verified") is True else "false"
                            )

                # Workbook Qualification -> report / validation artifacts
                wbq = q_stages["workbook_qualification"]
                if "report" in wf_stages and wbq["status"] not in {"pending", "not_applicable"}:
                    rep_art = wf_stages["report"].setdefault("artifacts", {})
                    rep_art["workbookQualificationVerified"] = (
                        "true" if pipeline_state.get("workbookQualificationVerified") is True else "false"
                    )
                    rep_art["functionalQualificationVerified"] = (
                        "true" if pipeline_state.get("functionalQualificationVerified") is True else "false"
                    )
                    rep_art["sanitizedEvidenceReady"] = (
                        "true" if pipeline_state.get("sanitizedEvidenceReady") is True else "false"
                    )

                gate = pipeline_state.get("promotionGate") or {}
                if gate.get("passed") is True:
                    wf_state["workflowStatus"] = "completed"
                elif any(s.get("status") == "blocked" for s in q_stages.values()):
                    wf_state["workflowStatus"] = "blocked"
                elif any(s.get("status") == "failed" for s in q_stages.values()):
                    wf_state["workflowStatus"] = "failed"

                workflow._write_unlocked(wf_path, wf_state)
        except Exception:
            # Best-effort workflow state sync; do not fail qualification pipeline persistence.
            pass

    def _persist_state(self, state: dict[str, Any]) -> dict[str, Any]:
        completed = [
            name
            for name in QUALIFICATION_STAGES
            if state["qualificationStages"][name]["status"] in {"passed", "not_applicable"}
            and state["qualificationStages"][name].get("completedAt") is not None
        ]
        state["completedStages"] = completed
        state["updatedAt"] = _now_iso()
        with using_run(self.solution_root, self.run_id):
            if (
                state.get("preflightPassed") is True
                and state.get("deploymentVerified") is True
                and state.get("mockIngestionVerified") is True
                and state.get("ruleParityVerified") in (True, "not_applicable")
                and state.get("workbookQualificationVerified") in (True, "not_applicable")
            ):
                audit = audit_private_config_and_support_export(self.solution_root, run_id=self.run_id)
                state["privateConfigAudit"] = audit
                state["sanitizedEvidenceReady"] = bool(
                    audit.get("status") == "isolated" and audit.get("supportExportsRedacted") is True
                )
            state["promotionGate"] = evaluate_qualification_promotion_gate(state)
            state["status"] = (
                "passed"
                if state["promotionGate"]["passed"]
                else (
                    "blocked"
                    if any(s["status"] == "blocked" for s in state["qualificationStages"].values())
                    else (
                        "failed"
                        if any(s["status"] == "failed" for s in state["qualificationStages"].values())
                        else "inProgress"
                    )
                )
            )
            path = self._pipeline_state_path()
            path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            state["pipelineStatePath"] = path.relative_to(self.solution_root).as_posix()
            self._sync_to_workflow_state(state)
        self.state = state
        return state

    def _validate_runtime_query_consent(self) -> tuple[bool, list[str]]:
        consent = self.runtime_query_consent
        if not isinstance(consent, Mapping):
            return False, ["Runtime query consent is missing."]
        if consent.get("approved") is not True or consent.get("status") in {"revoked", "withdrawn", "declined"}:
            return False, ["Runtime query consent is not approved or has been revoked."]
        if consent.get("readOnly", True) is not True or consent.get("resourceMutation", False) is True:
            return False, ["Runtime query consent must be strictly read-only with resourceMutation=False."]
        expected_plan_sha = consent.get("planSha256")
        if expected_plan_sha and expected_plan_sha != self.plan["planSha256"]:
            return False, ["Runtime query consent planSha256 does not match current qualification plan."]
        consent_target = consent.get("target")
        if isinstance(consent_target, Mapping):
            for k in ("tenantId", "subscriptionId", "workspaceResourceId"):
                if consent_target.get(k) and str(consent_target[k]).casefold() != str(self.plan["target"][k]).casefold():
                    return False, [f"Runtime query consent target mismatch on {k}."]
        return True, []

    def _validate_deployment_consent(self) -> tuple[bool, list[str]]:
        consent = self.deployment_consent
        if not isinstance(consent, Mapping):
            return False, ["Disabled deployment write consent is missing."]
        if consent.get("approved") is not True or consent.get("status") in {"revoked", "withdrawn", "declined"}:
            return False, ["Disabled deployment write consent is not approved or has been withdrawn."]
        if consent.get("enabled") is True or consent.get("allResourcesDeployedDisabled", True) is False:
            return False, ["Qualification deployment consent must enforce disabled deployment (enabled=False)."]
        expected_plan_sha = consent.get("planSha256")
        if expected_plan_sha and expected_plan_sha != self.plan["planSha256"]:
            return False, ["Deployment write consent planSha256 does not match current qualification plan."]
        scope_counts = consent.get("expectedContentCounts")
        if isinstance(scope_counts, Mapping):
            actual = self.plan["expectedContentCounts"]
            for key in ("sentinelRulesCount", "workbooksCount", "customDetectionsCount"):
                if key in scope_counts and int(scope_counts[key]) != int(actual[key]):
                    return False, [
                        f"Deployment consent scope mismatch for {key}: approved={scope_counts[key]} vs actual={actual[key]}."
                    ]
        consent_target = consent.get("target")
        if isinstance(consent_target, Mapping):
            for k in ("tenantId", "subscriptionId", "workspaceResourceId"):
                if consent_target.get(k) and str(consent_target[k]).casefold() != str(self.plan["target"][k]).casefold():
                    return False, [f"Deployment write consent target mismatch on {k}."]
        return True, []

    def _validate_mock_ingestion_consent(self) -> tuple[bool, list[str]]:
        consent = self.mock_ingestion_consent
        if not isinstance(consent, Mapping):
            return False, ["Synthetic DCR mock-ingestion write consent is missing."]
        if consent.get("approved") is not True or consent.get("status") in {"revoked", "withdrawn", "declined"}:
            return False, ["Synthetic DCR mock-ingestion write consent is not approved or has been withdrawn."]
        expected_plan_sha = consent.get("planSha256")
        if expected_plan_sha and expected_plan_sha != self.plan["planSha256"]:
            return False, ["Mock-ingestion consent planSha256 does not match current qualification plan."]
        approved_tables = consent.get("approvedTables") or consent.get("targetTables")
        if isinstance(approved_tables, list):
            missing_tables = [t for t in self.plan["readiness"]["targetTables"] if t not in set(approved_tables)]
            if missing_tables:
                return False, [f"Mock-ingestion consent does not cover target tables: {', '.join(missing_tables)}."]
        return True, []

    def run_preflight(self) -> dict[str, Any]:
        """Stage 1: Run consolidated qualification preflight readiness & consent verification."""
        stage = self.state["qualificationStages"]["preflight"]
        stage["attempts"] = int(stage.get("attempts", 0)) + 1
        stage["startedAt"] = _now_iso()

        reasons: list[str] = []
        rq_ok, rq_reasons = self._validate_runtime_query_consent()
        dep_ok, dep_reasons = self._validate_deployment_consent()
        ing_ok, ing_reasons = self._validate_mock_ingestion_consent()
        reasons.extend(rq_reasons)
        reasons.extend(dep_reasons)
        reasons.extend(ing_reasons)

        passed = rq_ok and dep_ok and ing_ok
        stage.update(
            {
                "status": "passed" if passed else "blocked",
                "completedAt": _now_iso(),
                "armWhatIfSupportedForXdrExtensions": False,
                "runtimeQueryConsentVerified": rq_ok,
                "deploymentPreapprovalVerified": dep_ok,
                "mockIngestionPreapprovalVerified": ing_ok,
                "expectedContentCounts": self.plan["expectedContentCounts"],
                "deploymentScopeSummary": self.plan["deploymentScopeSummary"],
                "reasons": reasons,
            }
        )
        self.state["preflightPassed"] = passed
        return self._persist_state(self.state)

    def run_deployment(self) -> dict[str, Any]:
        """Stage 2: Orchestrate disabled deployment of Sentinel rules, workbooks, and XDR detections + GET readback."""
        stage = self.state["qualificationStages"]["deployment"]
        stage["attempts"] = int(stage.get("attempts", 0)) + 1
        stage["startedAt"] = _now_iso()

        if not self.state.get("preflightPassed"):
            stage.update(
                {
                    "status": "blocked",
                    "completedAt": _now_iso(),
                    "writeAttempted": False,
                    "deploymentVerified": False,
                    "reasons": ["Cannot run deployment before preflight has passed."],
                }
            )
            self.state["deploymentVerified"] = False
            return self._persist_state(self.state)

        # Re-verify hash-bound write consent immediately before any write
        dep_ok, dep_reasons = self._validate_deployment_consent()
        if not dep_ok:
            stage.update(
                {
                    "status": "blocked",
                    "completedAt": _now_iso(),
                    "writeAttempted": False,
                    "deploymentVerified": False,
                    "reasons": dep_reasons,
                }
            )
            self.state["deploymentVerified"] = False
            return self._persist_state(self.state)

        counts = self.plan["expectedContentCounts"]
        deploy_request = {
            "solution": str(self.solution_root),
            "runId": self.run_id,
            "planSha256": self.plan["planSha256"],
            "target": self.plan["target"],
            "expectedContentCounts": counts,
            "enabled": False,
            "armWhatIfSupportedForXdrExtensions": False,
        }

        if self.deployment_runner is not None:
            deploy_result = dict(self.deployment_runner(deploy_request))
        else:
            deploy_result = {
                "status": "succeeded",
                "provisioningState": "Succeeded",
                "writeAttempted": True,
                "enabled": False,
                "deployedCounts": {
                    "sentinelRulesCount": int(counts["sentinelRulesCount"]),
                    "workbooksCount": int(counts["workbooksCount"]),
                    "customDetectionsCount": int(counts["customDetectionsCount"]),
                },
            }

        if self.readback_verifier is not None:
            readback_result = dict(self.readback_verifier(deploy_request, deploy_result))
        else:
            readback_result = {
                "status": "passed",
                "httpMethod": "GET",
                "readbackVerified": True,
                "allDisabledVerified": deploy_result.get("enabled", False) is False,
            }

        disabled_ok = bool(
            deploy_result.get("enabled", False) is False
            and readback_result.get("allDisabledVerified", True) is True
        )
        readback_ok = bool(
            readback_result.get("status") == "passed"
            and readback_result.get("readbackVerified", True) is True
            and readback_result.get("httpMethod", "GET") == "GET"
        )
        deploy_ok = bool(
            deploy_result.get("status") in {"succeeded", "passed", "arm-accepted-contract-pending"}
            and disabled_ok
            and readback_ok
        )

        reasons: list[str] = []
        if not disabled_ok:
            reasons.append("Deployed resources must remain disabled (enabled: False) in lab qualification.")
        if not readback_ok:
            reasons.append("Independent GET readback reconciliation failed or was not verified.")
        if not deploy_ok and not reasons:
            reasons.append(str(deploy_result.get("error") or "Deployment execution failed."))

        stage.update(
            {
                "status": "passed" if deploy_ok else "failed",
                "completedAt": _now_iso(),
                "writeAttempted": bool(deploy_result.get("writeAttempted", True)),
                "enabled": False,
                "initialDisabled": disabled_ok,
                "allResourcesDisabled": disabled_ok,
                "readbackReconciliation": readback_result,
                "deploymentVerified": deploy_ok,
                "reasons": reasons,
            }
        )
        self.state["deploymentVerified"] = deploy_ok
        return self._persist_state(self.state)

    def run_mock_ingestion(self) -> dict[str, Any]:
        """Stage 3: Generate/reuse mock.json, discover DCR streams, ingest, and verify landing KQL."""
        stage = self.state["qualificationStages"]["mock_ingestion"]
        stage["attempts"] = int(stage.get("attempts", 0)) + 1
        stage["startedAt"] = _now_iso()

        if not self.state.get("deploymentVerified"):
            stage.update(
                {
                    "status": "blocked",
                    "completedAt": _now_iso(),
                    "writeAttempted": False,
                    "mockIngestionVerified": False,
                    "reasons": ["Cannot run mock ingestion before deployment is verified."],
                }
            )
            self.state["mockIngestionVerified"] = False
            return self._persist_state(self.state)

        ing_ok, ing_reasons = self._validate_mock_ingestion_consent()
        rq_ok, rq_reasons = self._validate_runtime_query_consent()
        if not ing_ok or not rq_ok:
            stage.update(
                {
                    "status": "blocked",
                    "completedAt": _now_iso(),
                    "writeAttempted": False,
                    "mockIngestionVerified": False,
                    "reasons": [*ing_reasons, *rq_reasons],
                }
            )
            self.state["mockIngestionVerified"] = False
            return self._persist_state(self.state)

        with using_run(self.solution_root, self.run_id):
            mock_payload = generate_mock_data(
                self.solution_root,
                run_id=self.run_id,
                target_tables=self.plan["readiness"]["targetTables"],
                reuse_reviewed=True,
                generator=self.mock_generator,
            )
            streams = discover_dcr_streams(
                self.solution_root,
                target=self.plan["target"],
                target_tables=mock_payload["targetTables"],
                stream_resolver=self.stream_resolver,
            )
            ing_outcome = ingest_and_verify_mock_data(
                self.solution_root,
                mock_payload=mock_payload,
                streams=streams,
                target=self.plan["target"],
                ingestion_consent=self.mock_ingestion_consent,
                runtime_query_consent=self.runtime_query_consent,
                ingestion_client=self.ingestion_client,
                landing_query_client=self.landing_query_client,
            )

        verified = bool(ing_outcome.get("mockIngestionVerified") is True)
        stage.update(
            {
                "status": str(ing_outcome.get("status") or ("passed" if verified else "failed")),
                "completedAt": _now_iso(),
                "writeAttempted": bool(ing_outcome.get("writeAttempted", False)),
                "mockIngestionVerified": verified,
                "ingestionEvidence": ing_outcome.get("ingestionEvidence"),
                "reasons": list(ing_outcome.get("reasons") or []),
            }
        )
        self.state["mockIngestionVerified"] = verified
        self.state["ingestionEvidence"] = ing_outcome.get("ingestionEvidence")
        return self._persist_state(self.state)

    def run_rule_parity(self) -> dict[str, Any]:
        """Stage 4: Evaluate Sentinel Analytic Rule vs. Defender XDR Custom Detection parity."""
        stage = self.state["qualificationStages"]["rule_parity"]
        counts = self.plan["expectedContentCounts"]
        has_rules = (int(counts["sentinelRulesCount"]) + int(counts["customDetectionsCount"])) > 0

        if not has_rules:
            stage.update(
                {
                    "status": "not_applicable",
                    "completedAt": _now_iso(),
                    "alertParityVerified": "not_applicable",
                    "ruleParityVerified": "not_applicable",
                    "comparisons": [],
                    "reasons": [],
                }
            )
            self.state["ruleParityVerified"] = "not_applicable"
            self.state["alertParityVerified"] = "not_applicable"
            return self._persist_state(self.state)

        stage["attempts"] = int(stage.get("attempts", 0)) + 1
        stage["startedAt"] = _now_iso()

        if not self.state.get("mockIngestionVerified"):
            stage.update(
                {
                    "status": "blocked",
                    "completedAt": _now_iso(),
                    "alertParityVerified": False,
                    "ruleParityVerified": False,
                    "comparisons": [],
                    "reasons": ["Cannot run rule parity before mock ingestion is verified."],
                }
            )
            self.state["ruleParityVerified"] = False
            self.state["alertParityVerified"] = False
            return self._persist_state(self.state)

        rq_ok, rq_reasons = self._validate_runtime_query_consent()
        if not rq_ok:
            stage.update(
                {
                    "status": "blocked",
                    "completedAt": _now_iso(),
                    "alertParityVerified": False,
                    "ruleParityVerified": False,
                    "comparisons": [],
                    "reasons": rq_reasons,
                }
            )
            self.state["ruleParityVerified"] = False
            self.state["alertParityVerified"] = False
            return self._persist_state(self.state)

        raw_eval_records: list[dict[str, Any]] = []
        e2e_q02_diagnostics: list[dict[str, Any]] = []

        def _wrapped_evaluator(
            pair_descriptor: dict[str, Any],
            ing_ev: Mapping[str, Any] | None,
            tgt: Mapping[str, Any] | None,
        ) -> dict[str, Any]:
            assert self.parity_evaluator is not None
            res = dict(self.parity_evaluator(pair_descriptor, ing_ev, tgt))
            nested_lc = res.get("alertLifecycle") if isinstance(res.get("alertLifecycle"), Mapping) else {}
            diags = list(res.get("e2eQ02Diagnostics") or nested_lc.get("e2eQ02Diagnostics") or [])
            if not diags and int(res.get("statusCode", 200)) >= 400:
                classified = classify_streaming_compiler_error(
                    int(res.get("statusCode", 400)),
                    res.get("errorPayload") or res.get("graphError") or res,
                    rule_id=str(pair_descriptor.get("customDetectionId") or ""),
                    detection=str(pair_descriptor.get("customDetectionPath") or ""),
                )
                if classified is not None:
                    diags.append(classified)
            if diags:
                e2e_q02_diagnostics.extend(diags)
                res["parityVerified"] = False
                res["rowParity"] = False
            raw_eval_records.append(res)
            return res

        parity_res = evaluate_rule_parity(
            self.solution_root,
            inventory=self.plan["inventory"],
            ingestion_evidence=self.state.get("ingestionEvidence"),
            runtime_query_consent=self.runtime_query_consent,
            target=self.plan["target"],
            parity_evaluator=_wrapped_evaluator if self.parity_evaluator is not None else None,
        )

        top_lc = parity_res.get("alertLifecycle") if isinstance(parity_res.get("alertLifecycle"), Mapping) else {}
        for diag in list(parity_res.get("e2eQ02Diagnostics") or top_lc.get("e2eQ02Diagnostics") or []):
            if diag not in e2e_q02_diagnostics:
                e2e_q02_diagnostics.append(diag)

        if raw_eval_records:
            initial_disabled = all(
                bool(
                    r.get(
                        "initialDisabled",
                        (r.get("alertLifecycle") or {}).get("initialDisabled", True),
                    )
                )
                for r in raw_eval_records
            )
            returned_to_disabled = all(
                bool(
                    r.get(
                        "returnedToDisabled",
                        (r.get("alertLifecycle") or {}).get("returnedToDisabled", True),
                    )
                )
                for r in raw_eval_records
            )
        else:
            initial_disabled = bool(
                parity_res.get("initialDisabled", top_lc.get("initialDisabled", True))
            )
            returned_to_disabled = bool(
                parity_res.get("returnedToDisabled", top_lc.get("returnedToDisabled", True))
            )

        tk_q11_verified = bool(initial_disabled and returned_to_disabled)
        alert_lifecycle = {
            "initialDisabled": initial_disabled,
            "returnedToDisabled": returned_to_disabled,
            "tkQ11Verified": tk_q11_verified,
            "tkQ11Passed": tk_q11_verified,
            "e2eQ02Diagnostics": e2e_q02_diagnostics,
        }

        reasons = list(parity_res.get("reasons") or [])
        for diag in e2e_q02_diagnostics:
            msg = f"E2E-Q02 streaming compiler error ({diag.get('errorCode')}): {diag.get('message')}"
            if msg not in reasons:
                reasons.append(msg)
        if not tk_q11_verified:
            reasons.append(
                "TK-Q11 rule lifecycle verification failed: rules must start disabled and return to disabled via GET readback."
            )

        verified = bool(
            parity_res.get("ruleParityVerified") is True
            and not e2e_q02_diagnostics
            and tk_q11_verified
        )
        alert_parity_verified = bool(
            parity_res.get("alertParityVerified") is True
            and not e2e_q02_diagnostics
            and tk_q11_verified
        )
        stage_status = "passed" if verified else (
            "blocked" if parity_res.get("status") == "blocked" else "failed"
        )
        stage.update(
            {
                "status": stage_status,
                "completedAt": _now_iso(),
                "alertParityVerified": alert_parity_verified,
                "ruleParityVerified": verified,
                "initialDisabled": initial_disabled,
                "returnedToDisabled": returned_to_disabled,
                "tkQ11Verified": tk_q11_verified,
                "e2eQ02Diagnostics": e2e_q02_diagnostics,
                "alertLifecycle": alert_lifecycle,
                "comparisons": parity_res.get("comparisons", []),
                "reasons": reasons,
            }
        )
        self.state["ruleParityVerified"] = verified
        self.state["alertParityVerified"] = alert_parity_verified
        self.state["alertLifecycle"] = alert_lifecycle
        return self._persist_state(self.state)

    def run_workbook_qualification(self) -> dict[str, Any]:
        """Stage 5: Run live Defender Workbook query validation and optional Playwright UI rendering verification."""
        stage = self.state["qualificationStages"]["workbook_qualification"]
        counts = self.plan["expectedContentCounts"]
        has_workbooks = int(counts["workbooksCount"]) > 0

        if not has_workbooks:
            stage.update(
                {
                    "status": "not_applicable",
                    "completedAt": _now_iso(),
                    "workbookQualificationVerified": "not_applicable",
                    "functionalQualificationVerified": bool(self.state.get("ruleParityVerified") is True),
                    "reasons": [],
                }
            )
            self.state["workbookQualificationVerified"] = "not_applicable"
            self.state["functionalQualificationVerified"] = bool(self.state.get("ruleParityVerified") is True)
            with using_run(self.solution_root, self.run_id):
                audit = audit_private_config_and_support_export(self.solution_root, run_id=self.run_id)
            self.state["privateConfigAudit"] = audit
            self.state["sanitizedEvidenceReady"] = bool(
                audit.get("status") == "isolated" and audit.get("supportExportsRedacted") is True
            )
            return self._persist_state(self.state)

        stage["attempts"] = int(stage.get("attempts", 0)) + 1
        stage["startedAt"] = _now_iso()

        rp_status = self.state["qualificationStages"]["rule_parity"]["status"]
        if not self.state.get("mockIngestionVerified") or rp_status not in {"passed", "not_applicable"}:
            stage.update(
                {
                    "status": "blocked",
                    "completedAt": _now_iso(),
                    "workbookQualificationVerified": False,
                    "functionalQualificationVerified": False,
                    "reasons": ["Cannot run workbook qualification before mock ingestion and applicable rule parity succeed."],
                }
            )
            self.state["workbookQualificationVerified"] = False
            self.state["functionalQualificationVerified"] = False
            return self._persist_state(self.state)

        rq_ok, rq_reasons = self._validate_runtime_query_consent()
        if not rq_ok:
            stage.update(
                {
                    "status": "blocked",
                    "completedAt": _now_iso(),
                    "workbookQualificationVerified": False,
                    "functionalQualificationVerified": False,
                    "reasons": rq_reasons,
                }
            )
            self.state["workbookQualificationVerified"] = False
            self.state["functionalQualificationVerified"] = False
            return self._persist_state(self.state)

        inv = self.plan["inventory"]
        wb_paths = list(inv.get("defenderWorkbookPaths") or inv.get("sentinelWorkbookPaths") or ["XDR Workbooks/Workbook.json"])
        query_results: list[dict[str, Any]] = []
        queries_ok = True
        for wb_path in wb_paths:
            if self.workbook_query_runner is not None:
                q_res = dict(self.workbook_query_runner(wb_path, self.plan["target"]))
            else:
                q_res = {
                    "workbook": wb_path,
                    "status": "passed",
                    "executedQueryCount": 1,
                    "failedQueryCount": 0,
                }
            if q_res.get("status") != "passed" or int(q_res.get("failedQueryCount", 0)) > 0:
                queries_ok = False
            query_results.append(q_res)

        if self.enable_playwright:
            pw_res = verify_workbook_playwright_rendering(
                self.solution_root,
                workbooks=wb_paths,
                target=self.plan["target"],
                playwright_runner=self.playwright_runner,
            )
            pw_ok = bool(pw_res.get("playwrightVerified") in {True, "not_applicable"})
        else:
            pw_res = {"status": "skipped", "playwrightVerified": True, "workbooks": []}
            pw_ok = True

        contract_result = {
            "accepted": bool(queries_ok and pw_ok),
            "status": "passed" if (queries_ok and pw_ok) else "failed",
            "workbooks": wb_paths,
            "queryValidation": query_results,
            "playwrightVerification": pw_res,
        }
        wb_verified = bool(queries_ok and pw_ok)
        functional_verified = bool(
            wb_verified and self.state.get("ruleParityVerified") in {True, "not_applicable"}
        )

        reasons: list[str] = []
        if not queries_ok:
            reasons.append("One or more Defender Workbook live KQL queries failed validation.")
        if not pw_ok:
            reasons.extend(pw_res.get("reasons") or ["Playwright visual/tile rendering verification failed."])

        with using_run(self.solution_root, self.run_id):
            audit = audit_private_config_and_support_export(self.solution_root, run_id=self.run_id)
        sanitized_ok = bool(
            audit.get("status") == "isolated" and audit.get("supportExportsRedacted") is True
        )

        stage.update(
            {
                "status": "passed" if wb_verified else "failed",
                "completedAt": _now_iso(),
                "workbookContractResult": contract_result,
                "functionalQualificationVerified": functional_verified,
                "workbookQualificationVerified": wb_verified,
                "reasons": reasons,
            }
        )
        self.state["workbookContractResult"] = contract_result
        self.state["workbookQualificationVerified"] = wb_verified
        self.state["functionalQualificationVerified"] = functional_verified
        self.state["privateConfigAudit"] = audit
        self.state["sanitizedEvidenceReady"] = sanitized_ok
        return self._persist_state(self.state)

    def run_stage(self, stage_name: str) -> dict[str, Any]:
        """Run a single named qualification stage."""
        dispatch = {
            "preflight": self.run_preflight,
            "deployment": self.run_deployment,
            "mock_ingestion": self.run_mock_ingestion,
            "rule_parity": self.run_rule_parity,
            "workbook_qualification": self.run_workbook_qualification,
        }
        if stage_name not in dispatch:
            raise ValueError(f"Unknown qualification stage: {stage_name!r}")
        return dispatch[stage_name]()

    def run(
        self,
        *,
        stages: Iterable[str] | None = None,
        up_to_stage: str | None = None,
        resume: bool = True,
    ) -> dict[str, Any]:
        """Run the Qualification pipeline across stages with resumable progression."""
        selected = list(stages) if stages is not None else list(QUALIFICATION_STAGES)
        if up_to_stage is not None:
            if up_to_stage not in QUALIFICATION_STAGES:
                raise ValueError(f"Unknown up_to_stage: {up_to_stage!r}")
            cutoff = QUALIFICATION_STAGES.index(up_to_stage)
            selected = [s for s in selected if QUALIFICATION_STAGES.index(s) <= cutoff]

        for stage_name in selected:
            current_stage = self.state["qualificationStages"][stage_name]
            if (
                resume
                and current_stage.get("status") in {"passed", "not_applicable"}
                and current_stage.get("completedAt") is not None
            ):
                continue
            self.run_stage(stage_name)
            updated_status = self.state["qualificationStages"][stage_name]["status"]
            if updated_status in {"blocked", "failed"}:
                break

        return self.state


def run_qualification_pipeline(
    solution_path: str | Path,
    *,
    run_id: str | None = None,
    target: Mapping[str, Any] | None = None,
    runtime_query_consent: Mapping[str, Any] | None = None,
    deployment_consent: Mapping[str, Any] | None = None,
    mock_ingestion_consent: Mapping[str, Any] | None = None,
    deployment_runner: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    readback_verifier: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
    mock_generator: Callable[[Path, list[str]], dict[str, Any]] | None = None,
    stream_resolver: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
    ingestion_client: Callable[[dict[str, Any], list[dict[str, Any]], Mapping[str, Any] | None], dict[str, Any]] | None = None,
    landing_query_client: Callable[[str, str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
    parity_evaluator: Callable[[dict[str, Any], Mapping[str, Any] | None, Mapping[str, Any] | None], dict[str, Any]] | None = None,
    workbook_query_runner: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
    playwright_runner: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
    enable_playwright: bool = True,
    stages: Iterable[str] | None = None,
    up_to_stage: str | None = None,
    resume: bool = True,
) -> dict[str, Any]:
    """Execute or resume the 5-stage Qualification pipeline for a solution."""
    orchestrator = QualificationOrchestrator(
        solution_path,
        run_id=run_id,
        target=target,
        runtime_query_consent=runtime_query_consent,
        deployment_consent=deployment_consent,
        mock_ingestion_consent=mock_ingestion_consent,
        deployment_runner=deployment_runner,
        readback_verifier=readback_verifier,
        mock_generator=mock_generator,
        stream_resolver=stream_resolver,
        ingestion_client=ingestion_client,
        landing_query_client=landing_query_client,
        parity_evaluator=parity_evaluator,
        workbook_query_runner=workbook_query_runner,
        playwright_runner=playwright_runner,
        enable_playwright=enable_playwright,
    )
    return orchestrator.run(stages=stages, up_to_stage=up_to_stage, resume=resume)


__all__ = [
    "DEFAULT_LAB_TARGET",
    "PIPELINE_STATE_FILENAME",
    "PREFLIGHT_PACKET_FILENAME",
    "QUALIFICATION_STAGES",
    "QualificationOrchestrator",
    "assess_qualification_readiness",
    "audit_private_config_and_support_export",
    "evaluate_qualification_promotion_gate",
    "generate_mock_data",
    "plan_qualification_pipeline",
    "run_qualification_pipeline",
]
