"""Shared Solution Manager foundation: workflow state, coordination, onboarding, preflight, config, budgets, and paths."""
from __future__ import annotations

from typing import Any

_REVIEW_NOTIFICATION_EXPORTS = {
    "NOTIFICATION_STATES",
    "VALID_NOTIFICATION_STATES",
    "mark_notification_acknowledged",
    "mark_notification_delivered",
    "mark_notification_failed",
    "reconcile_pending_notifications",
    "sync_review_gate_notification",
}
_WORKFLOW_REMINDER_EXPORTS = {
    "build_migration_status_reminder",
    "build_workflow_status_reminder",
    "extract_review_notification_state",
}

__all__ = [
    "NOTIFICATION_STATES",
    "VALID_NOTIFICATION_STATES",
    "build_migration_status_reminder",
    "build_workflow_status_reminder",
    "extract_review_notification_state",
    "mark_notification_acknowledged",
    "mark_notification_delivered",
    "mark_notification_failed",
    "reconcile_pending_notifications",
    "sync_review_gate_notification",
]


def __getattr__(name: str) -> Any:
    if name in _REVIEW_NOTIFICATION_EXPORTS:
        from solution_manager.core import review_notifications

        return getattr(review_notifications, name)
    if name in _WORKFLOW_REMINDER_EXPORTS:
        from solution_manager.core import workflow_reminders

        return getattr(workflow_reminders, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

