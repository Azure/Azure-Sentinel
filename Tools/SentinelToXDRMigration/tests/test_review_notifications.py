"""Tests for coordinator-owned review-gate notifications."""

from __future__ import annotations

import pytest

from solution_manager.core.review_notifications import (
    mark_notification_acknowledged,
    mark_notification_delivered,
    mark_notification_failed,
    reconcile_pending_notifications,
    sync_review_gate_notification,
)
from solution_manager.core.workflow_reminders import build_workflow_status_reminder


def _sample_state(*, run_id: str = "authoring-20260420T120000Z") -> dict:
    return {
        "schemaVersion": "1.1.0",
        "runId": run_id,
        "solutionName": "ContosoSample",
        "workflowProfile": "authoring",
        "workflowStatus": "awaiting_user_confirmation",
        "context": {},
        "stages": {
            "rule_conversion": {
                "status": "awaiting_user_confirmation",
                "summary": "Awaiting rule review decision",
            }
        },
    }


def test_sync_and_deliver_review_gate_notification_lifecycle() -> None:
    state = _sample_state()
    packet_v1 = {
        "gate": "rule_review",
        "reviewPacketSha256": "a" * 64,
        "summary": "Review 3 converted rules",
    }

    synced = sync_review_gate_notification(state, packet_v1)
    assert synced["status"] == "pending"
    assert synced["runId"] == "authoring-20260420T120000Z"
    assert synced["reviewPacketSha256"] == "a" * 64
    assert synced["needsImmediateDelivery"] is True
    assert synced["packetChanged"] is True

    # Delivering transitions pending -> delivered
    delivered = mark_notification_delivered(
        state,
        run_id="authoring-20260420T120000Z",
        review_packet_sha256="a" * 64,
        owner_id="coordinator-main",
        channel="coordinator",
    )
    assert delivered["status"] == "delivered"
    assert delivered["duplicateSuppressed"] is False
    assert delivered["needsImmediateDelivery"] is False
    assert delivered["deliveredBy"] == "coordinator-main"
    assert delivered["deliveryAttempts"] == 1

    # Duplicate delivery of unchanged packet is deduplicated
    dup = mark_notification_delivered(
        state,
        run_id="authoring-20260420T120000Z",
        review_packet_sha256="a" * 64,
        owner_id="coordinator-main",
        channel="coordinator",
    )
    assert dup["status"] == "delivered"
    assert dup["duplicateSuppressed"] is True
    assert dup["deliveryAttempts"] == 1

    # Acknowledging transitions delivered -> acknowledged
    acked = mark_notification_acknowledged(
        state,
        run_id="authoring-20260420T120000Z",
        review_packet_sha256="a" * 64,
        acknowledged_by="user-reviewer",
    )
    assert acked["status"] == "acknowledged"
    assert acked["acknowledgedBy"] == "user-reviewer"
    assert acked["needsImmediateDelivery"] is False


def test_changed_review_packet_sha256_resets_delivered_to_pending() -> None:
    state = _sample_state()
    sync_review_gate_notification(
        state,
        {"gate": "rule_review", "reviewPacketSha256": "1" * 64},
    )
    mark_notification_delivered(
        state,
        run_id=state["runId"],
        review_packet_sha256="1" * 64,
        owner_id="coordinator-main",
    )
    assert state["reviewNotificationState"]["status"] == "delivered"

    # Syncing with a new reviewPacketSha256 must reset status to pending and never suppress
    updated = sync_review_gate_notification(
        state,
        {"gate": "rule_review", "reviewPacketSha256": "2" * 64},
    )
    assert updated["status"] == "pending"
    assert updated["reviewPacketSha256"] == "2" * 64
    assert updated["previousReviewPacketSha256"] == "1" * 64
    assert updated["packetChanged"] is True
    assert updated["needsImmediateDelivery"] is True
    assert updated["duplicateSuppressed"] is False


def test_failed_delivery_and_restart_reconciliation_never_suppressed() -> None:
    state = _sample_state()
    sync_review_gate_notification(
        state,
        {"gate": "release_approval", "reviewPacketSha256": "b" * 64},
    )

    failed = mark_notification_failed(
        state,
        run_id=state["runId"],
        review_packet_sha256="b" * 64,
        owner_id="coordinator-main",
        error="Channel timeout",
    )
    assert failed["status"] == "failed"
    assert failed["needsImmediateDelivery"] is True
    assert failed["lastError"] == "Channel timeout"

    # Passive status summary must NOT count as delivery or alter failed status
    reminder = build_workflow_status_reminder(state)
    assert reminder["reviewNotificationState"]["status"] == "failed"
    assert reminder["reviewNotificationState"]["needsImmediateDelivery"] is True
    assert reminder["countsAsNotificationDelivery"] is False
    assert state["reviewNotificationState"]["status"] == "failed"

    # Reconciling after restart or model switch surfaces undelivered notifications
    reconciled = reconcile_pending_notifications(state)
    assert reconciled["reconciled"] is True
    assert reconciled["needsImmediateDelivery"] is True
    assert reconciled["pendingCount"] == 1
    assert reconciled["pendingNotifications"][0]["status"] == "failed"
    assert reconciled["countsAsDelivery"] is False

    # Retry delivery after failure succeeds and is NOT suppressed
    retried = mark_notification_delivered(
        state,
        run_id=state["runId"],
        review_packet_sha256="b" * 64,
        owner_id="coordinator-main",
    )
    assert retried["status"] == "delivered"
    assert retried["duplicateSuppressed"] is False
    assert retried["needsImmediateDelivery"] is False


def test_single_owner_execution_lease_enforced_on_delivery() -> None:
    state = _sample_state()
    state["workflow-execution-owner"] = {
        "ownerId": "coordinator-primary",
        "status": "active",
    }
    sync_review_gate_notification(
        state,
        {"gate": "workbook_review", "reviewPacketSha256": "c" * 64},
    )

    with pytest.raises(PermissionError, match="Single-owner execution lease conflict"):
        mark_notification_delivered(
            state,
            run_id=state["runId"],
            review_packet_sha256="c" * 64,
            owner_id="rogue-subagent",
        )

    # Matching lease owner succeeds
    delivered = mark_notification_delivered(
        state,
        run_id=state["runId"],
        review_packet_sha256="c" * 64,
        owner_id="coordinator-primary",
    )
    assert delivered["status"] == "delivered"
