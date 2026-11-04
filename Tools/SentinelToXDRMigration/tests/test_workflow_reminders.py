"""Tests for workflow status reminders and non-delivery review notification surfacing."""

from __future__ import annotations

import copy
from pathlib import Path

from solution_manager.core.review_notifications import (
    mark_notification_delivered,
    sync_review_gate_notification,
)
from solution_manager.core.workflow import initialize_workflow
from solution_manager.core.workflow_reminders import build_workflow_status_reminder


def test_build_workflow_status_reminder_preserves_pending_notification_state() -> None:
    state = {
        "schemaVersion": "1.1.0",
        "runId": "authoring-20260420T150000Z",
        "solutionName": "ContosoSolution",
        "workflowProfile": "authoring",
        "workflowStatus": "awaiting_user_confirmation",
        "stages": {
            "rule_conversion": {
                "status": "awaiting_user_confirmation",
                "summary": "Waiting for reviewer confirmation",
            }
        },
    }
    sync_review_gate_notification(
        state,
        {
            "gate": "rule_conversion",
            "reviewPacketSha256": "d" * 64,
            "summary": "Confirm rule review packet",
        },
    )
    before_snapshot = copy.deepcopy(state["reviewNotificationState"])

    reminder = build_workflow_status_reminder(state)
    assert reminder["reviewNotificationState"]["status"] == "pending"
    assert reminder["reviewNotificationState"]["needsImmediateDelivery"] is True
    assert reminder["reviewNotificationState"]["reviewPacketSha256"] == "d" * 64
    assert reminder["countsAsNotificationDelivery"] is False

    # State must remain untouched (generating a status reminder never counts as delivery)
    assert state["reviewNotificationState"] == before_snapshot

    mark_notification_delivered(
        state,
        run_id="authoring-20260420T150000Z",
        review_packet_sha256="d" * 64,
        owner_id="coordinator-1",
    )
    reminder_after = build_workflow_status_reminder(state)
    assert reminder_after["reviewNotificationState"]["status"] == "delivered"
    assert reminder_after["reviewNotificationState"]["needsImmediateDelivery"] is False


def test_build_workflow_status_reminder_on_solution_directory(tmp_path: Path) -> None:
    sol = tmp_path / "SampleSolution"
    (sol / "Analytic Rules").mkdir(parents=True)
    (sol / "SolutionMetadata.json").write_text(
        '{"publisherId": "contoso", "offerId": "sample", "version": "3.0.0"}',
        encoding="utf-8",
    )
    initialize_workflow(sol, workflow_profile="authoring")

    reminder = build_workflow_status_reminder(sol)
    assert reminder["solutionName"] == "SampleSolution"
    assert "reviewNotificationState" in reminder
    assert reminder["countsAsNotificationDelivery"] is False
