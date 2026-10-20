"""Workflow status reminder builder with passive review-notification state projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Optional

from solution_manager.core.workflow import (
    LARGE_DETECTION_BATCH_THRESHOLD,
    LARGE_WORKBOOK_QUERY_BATCH_THRESHOLD,
    STAGES,
    _build_duration_explanation,
    _build_workflow_diagram,
    _describe_current_activity,
    build_migration_status_reminder as _workflow_build_migration_status_reminder,
    extract_review_notification_state,
)


def _build_reminder_from_state_dict(
    state: dict[str, Any],
    *,
    previous_fingerprint: Optional[str] = None,
    persist_cursor: bool = True,
) -> dict[str, Any]:
    run_id = str(state.get("runId") or "default-run")
    solution_name = str(state.get("solutionName") or state.get("solution") or "Solution")
    stages = state.get("stages") if isinstance(state.get("stages"), Mapping) else {}
    next_stage = state.get("next") or state.get("nextStage")
    if not next_stage:
        for st_name in STAGES:
            st_obj = stages.get(st_name)
            if isinstance(st_obj, Mapping) and st_obj.get("status") in {"pending", "running", "blocked"}:
                next_stage = st_name
                break

    item_counts_raw = state.get("itemCounts") if isinstance(state.get("itemCounts"), Mapping) else {}
    analytic_rule_count = int(item_counts_raw.get("analyticRules") or state.get("analyticRuleCount") or 0)
    xdr_detection_count = int(item_counts_raw.get("xdrDetections") or state.get("xdrDetectionCount") or 0)
    workbook_count = int(item_counts_raw.get("workbooks") or state.get("workbookCount") or 0)
    workbook_query_count = int(item_counts_raw.get("workbookQueries") or state.get("workbookQueryCount") or 0)

    recommendation = (
        dict(state["nextStepRecommendation"])
        if isinstance(state.get("nextStepRecommendation"), Mapping)
        else {
            "status": "blocked" if state.get("workflowStatus") == "blocked" else "inProgress",
            "blockerCount": int(state.get("blockerCount") or 0),
            "blockerLabels": list(state.get("blockerLabels") or []),
            "summary": str(
                state.get("expectedNextStep")
                or f"Next migration step: continue stage {next_stage or 'discovery'}."
            ),
        }
    )
    blocker_count = int(recommendation.get("blockerCount") or 0)
    blocker_labels = list(recommendation.get("blockerLabels") or [])

    stage_statuses = {
        stage_name: {
            "status": (stages.get(stage_name) or {}).get("status") if isinstance(stages.get(stage_name), Mapping) else None,
            "attempts": (stages.get(stage_name) or {}).get("attempts", 0) if isinstance(stages.get(stage_name), Mapping) else 0,
            "message": (stages.get(stage_name) or {}).get("message") if isinstance(stages.get(stage_name), Mapping) else None,
        }
        for stage_name in STAGES
    }

    fingerprint_payload = {
        "runId": run_id,
        "workflowStatus": state.get("workflowStatus") or "inProgress",
        "nextStage": next_stage,
        "stages": stage_statuses,
        "itemCounts": {
            "analyticRules": analytic_rule_count,
            "xdrDetections": xdr_detection_count,
            "workbooks": workbook_count,
            "workbookQueries": workbook_query_count,
        },
        "blockerCount": blocker_count,
        "blockerLabels": blocker_labels,
    }
    state_fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    prev_fp = previous_fingerprint
    if prev_fp is None:
        cursor = state.get("statusReminderCursor")
        if isinstance(cursor, Mapping):
            prev_fp = str(cursor.get("stateFingerprint") or "") or None
        elif isinstance(state.get("lastReminderFingerprint"), str):
            prev_fp = state["lastReminderFingerprint"]

    suppressed_no_change = prev_fp == state_fingerprint
    if persist_cursor and not suppressed_no_change:
        state["statusReminderCursor"] = {
            "schemaVersion": "1.0.0",
            "runId": run_id,
            "stateFingerprint": state_fingerprint,
        }

    current_activity = _describe_current_activity(state, next_stage, recommendation)
    duration_explanation, is_large_batch = _build_duration_explanation(
        analytic_rule_count,
        xdr_detection_count,
        workbook_count,
        workbook_query_count,
    )
    workflow_diagram = _build_workflow_diagram(state, next_stage)
    review_notification_state = extract_review_notification_state(state)

    return {
        "schemaVersion": "1.0.0",
        "kind": "migration-status-reminder",
        "solution": str(state.get("solution") or "."),
        "solutionName": solution_name,
        "runId": run_id,
        "workflowStatus": state.get("workflowStatus") or "inProgress",
        "stateFingerprint": state_fingerprint,
        "previousStateFingerprint": prev_fp,
        "suppressedNoChange": suppressed_no_change,
        "currentActivity": current_activity,
        "expectedNextStep": str(recommendation.get("summary") or ""),
        "nextStepRecommendation": recommendation,
        "durationExplanation": duration_explanation,
        "isLargeBatch": is_large_batch,
        "itemCounts": {
            "analyticRules": analytic_rule_count,
            "xdrDetections": xdr_detection_count,
            "workbooks": workbook_count,
            "workbookQueries": workbook_query_count,
        },
        "blockerCount": blocker_count,
        "workflowDiagram": workflow_diagram,
        "watchdogCoordination": {
            "readOnlyObserver": True,
            "createsExecutor": False,
            "singleOwnerRespected": True,
        },
        "countsAsNotificationDelivery": False,
        "reviewNotificationState": review_notification_state,
    }


def build_workflow_status_reminder(
    state_or_solution: dict[str, Any] | str | Path,
    *,
    run_id: Optional[str] = None,
    persist_cursor: bool = True,
    previous_fingerprint: Optional[str] = None,
) -> dict[str, Any]:
    """Build a passive workflow status reminder and surface reviewNotificationState without counting as delivery."""
    if isinstance(state_or_solution, dict):
        return _build_reminder_from_state_dict(
            state_or_solution,
            previous_fingerprint=previous_fingerprint,
            persist_cursor=persist_cursor,
        )

    res = _workflow_build_migration_status_reminder(
        state_or_solution,
        run_id=run_id,
        persist_cursor=persist_cursor,
    )
    res.setdefault("countsAsNotificationDelivery", False)
    return res


build_migration_status_reminder = build_workflow_status_reminder

__all__ = [
    "LARGE_DETECTION_BATCH_THRESHOLD",
    "LARGE_WORKBOOK_QUERY_BATCH_THRESHOLD",
    "build_migration_status_reminder",
    "build_workflow_status_reminder",
    "extract_review_notification_state",
]
