"""Coordinator-owned review-gate notification state management bound to (runId, reviewPacketSha256)."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping, Optional

NOTIFICATION_STATES = ("pending", "delivered", "acknowledged", "failed")
VALID_NOTIFICATION_STATES = frozenset(NOTIFICATION_STATES)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _resolve_packet_sha256(review_packet: Mapping[str, Any]) -> str:
    for key in ("reviewPacketSha256", "packetSha256", "sha256"):
        raw = review_packet.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return _canonical_sha256(dict(review_packet))


def _resolve_run_id(state: Mapping[str, Any], review_packet: Optional[Mapping[str, Any]] = None) -> str:
    if isinstance(review_packet, Mapping):
        pkt_run = review_packet.get("runId")
        if isinstance(pkt_run, str) and pkt_run.strip():
            return pkt_run.strip()
    state_run = state.get("runId")
    if isinstance(state_run, str) and state_run.strip():
        return state_run.strip()
    existing_notif = state.get("reviewNotification")
    if isinstance(existing_notif, Mapping):
        notif_run = existing_notif.get("runId")
        if isinstance(notif_run, str) and notif_run.strip():
            return notif_run.strip()
    return "default-run"


class SingleOwnerLeaseError(PermissionError, ValueError):
    """Raised when a non-owner attempts coordinator notification delivery under an active lease."""


def _verify_single_owner_lease(state: Mapping[str, Any], owner_id: str) -> None:
    """Enforce single-owner execution lease check using workflow-execution-owner state if present."""
    if not isinstance(owner_id, str) or not owner_id.strip():
        raise ValueError("owner_id must be a non-empty string")
    clean_owner = owner_id.strip()

    owner_containers: list[Any] = []
    for key in (
        "workflow-execution-owner",
        "workflowExecutionOwner",
        "executionOwnership",
        "executionOwner",
    ):
        if key in state and state[key] is not None:
            owner_containers.append(state[key])

    for container in owner_containers:
        if isinstance(container, str) and container.strip():
            active_owner = container.strip()
            if active_owner != clean_owner:
                raise SingleOwnerLeaseError(
                    f"Single-owner execution lease conflict (duplicate_executor_blocked): active execution owner is {active_owner!r}; "
                    f"delivery by {clean_owner!r} rejected"
                )
        elif isinstance(container, Mapping):
            status = str(container.get("status") or "active").strip()
            direct_owner = container.get("ownerId")
            if (
                status == "active"
                and isinstance(direct_owner, str)
                and direct_owner.strip()
                and direct_owner.strip() != clean_owner
            ):
                raise SingleOwnerLeaseError(
                    f"Single-owner execution lease conflict (duplicate_executor_blocked): active execution owner is {direct_owner.strip()!r}; "
                    f"delivery by {clean_owner!r} rejected"
                )
            leases = container.get("leases")
            if isinstance(leases, Mapping):
                for op_name, lease in leases.items():
                    if not isinstance(lease, Mapping):
                        continue
                    lease_status = str(lease.get("status") or "active").strip()
                    lease_owner = lease.get("ownerId")
                    if (
                        lease_status == "active"
                        and isinstance(lease_owner, str)
                        and lease_owner.strip()
                        and lease_owner.strip() != clean_owner
                    ):
                        raise SingleOwnerLeaseError(
                            f"Single-owner execution lease conflict (duplicate_executor_blocked): operation {op_name!r} is owned by "
                            f"{lease_owner.strip()!r}; delivery by {clean_owner!r} rejected"
                        )


def _get_notifications_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_map = state.get("reviewNotifications")
    notifications: dict[str, dict[str, Any]] = {}
    if isinstance(raw_map, Mapping):
        for k, v in raw_map.items():
            if isinstance(k, str) and isinstance(v, Mapping):
                notifications[k] = dict(v)
    current = state.get("reviewNotification")
    if isinstance(current, Mapping):
        r_id = str(current.get("runId") or state.get("runId") or "default-run")
        notifications.setdefault(r_id, dict(current))
    state["reviewNotifications"] = notifications
    return notifications


def _store_notification(state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    notifications = _get_notifications_map(state)
    run_id = str(record["runId"])
    notifications[run_id] = record
    state["reviewNotifications"] = notifications
    state["reviewNotification"] = record
    state["reviewNotificationState"] = record
    return record


def sync_review_gate_notification(
    state: dict[str, Any],
    review_packet: dict[str, Any],
) -> dict[str, Any]:
    """Create or update a coordinator-owned review-gate notification record bound to (runId, reviewPacketSha256).

    If reviewPacketSha256 changes, resets state to 'pending' so changed review packets are never suppressed.
    """
    if not isinstance(state, dict):
        raise ValueError("state must be a dict")
    if not isinstance(review_packet, Mapping):
        raise ValueError("review_packet must be a mapping")

    run_id = _resolve_run_id(state, review_packet)
    packet_sha256 = _resolve_packet_sha256(review_packet)
    gate_type = str(
        review_packet.get("gateType")
        or review_packet.get("gate")
        or ("release_approval" if review_packet.get("releaseApprovalRequired") else "review")
    )
    summary = review_packet.get("summary") if isinstance(review_packet.get("summary"), Mapping) else {}
    blocker_count = int(
        summary.get("pendingReviewCount")
        or (review_packet.get("nextStepRecommendation") or {}).get("blockerCount")
        or review_packet.get("blockerCount")
        or len(review_packet.get("items") or [])
        or 0
    )

    notifications = _get_notifications_map(state)
    existing = notifications.get(run_id)
    now = _utc_now()

    if existing is None:
        record: dict[str, Any] = {
            "schemaVersion": "1.0.0",
            "runId": run_id,
            "reviewPacketSha256": packet_sha256,
            "previousReviewPacketSha256": None,
            "status": "pending",
            "gateType": gate_type,
            "blockerCount": blocker_count,
            "needsImmediateDelivery": True,
            "duplicateSuppressed": False,
            "packetChanged": True,
            "packetChangedReset": False,
            "deliveryCount": 0,
            "deliveryAttempts": 0,
            "failureCount": 0,
            "lastError": None,
            "ownerId": None,
            "deliveredBy": None,
            "channel": None,
            "acknowledgedBy": None,
            "createdAtUtc": now,
            "updatedAtUtc": now,
            "deliveredAtUtc": None,
            "acknowledgedAtUtc": None,
        }
        return _store_notification(state, record)

    old_sha = str(existing.get("reviewPacketSha256") or "")
    old_status = str(existing.get("status") or "pending")
    if old_status not in VALID_NOTIFICATION_STATES:
        old_status = "pending"

    if old_sha != packet_sha256:
        record = {
            **existing,
            "runId": run_id,
            "reviewPacketSha256": packet_sha256,
            "previousReviewPacketSha256": old_sha or None,
            "status": "pending",
            "gateType": gate_type,
            "blockerCount": blocker_count,
            "needsImmediateDelivery": True,
            "duplicateSuppressed": False,
            "packetChanged": True,
            "packetChangedReset": True,
            "lastError": None,
            "acknowledgedBy": None,
            "updatedAtUtc": now,
            "deliveredAtUtc": None,
            "acknowledgedAtUtc": None,
        }
        return _store_notification(state, record)

    needs_delivery = old_status in {"pending", "failed"}
    record = {
        **existing,
        "runId": run_id,
        "reviewPacketSha256": packet_sha256,
        "status": old_status,
        "gateType": gate_type,
        "blockerCount": blocker_count,
        "needsImmediateDelivery": needs_delivery,
        "duplicateSuppressed": False,
        "packetChanged": False,
        "packetChangedReset": False,
        "updatedAtUtc": now,
    }
    return _store_notification(state, record)


def _require_bound_notification(
    state: dict[str, Any],
    *,
    run_id: str,
    review_packet_sha256: str,
) -> dict[str, Any]:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be a non-empty string")
    if not isinstance(review_packet_sha256, str) or not review_packet_sha256.strip():
        raise ValueError("review_packet_sha256 must be a non-empty string")

    clean_run_id = run_id.strip()
    clean_sha = review_packet_sha256.strip()
    notifications = _get_notifications_map(state)
    existing = notifications.get(clean_run_id)
    if existing is None:
        raise ValueError(f"no review-gate notification found for runId {clean_run_id!r}")
    bound_sha = str(existing.get("reviewPacketSha256") or "")
    if bound_sha != clean_sha:
        raise ValueError(
            f"review_packet_sha256 mismatch for runId {clean_run_id!r}: "
            f"expected {bound_sha!r}, got {clean_sha!r}"
        )
    return existing


def mark_notification_delivered(
    state: dict[str, Any],
    *,
    run_id: str,
    review_packet_sha256: str,
    owner_id: str,
    channel: str = "coordinator",
    error: Optional[str] = None,
) -> dict[str, Any]:
    """Transition a pending/failed notification to delivered, or deduplicate if already delivered.

    Enforces single-owner execution lease check (using workflow-execution-owner state if present),
    deduplicates already-delivered unchanged packets (duplicateSuppressed: True), and never
    suppresses pending or failed notifications.
    """
    _verify_single_owner_lease(state, owner_id)
    existing = _require_bound_notification(
        state,
        run_id=run_id,
        review_packet_sha256=review_packet_sha256,
    )
    if error is not None:
        return mark_notification_failed(
            state,
            run_id=run_id,
            review_packet_sha256=review_packet_sha256,
            owner_id=owner_id,
            error=error,
            channel=channel,
        )

    current_status = str(existing.get("status") or "pending")
    now = _utc_now()
    clean_owner = owner_id.strip()

    if current_status in {"delivered", "acknowledged"}:
        record = {
            **existing,
            "duplicateSuppressed": True,
            "needsImmediateDelivery": False,
            "updatedAtUtc": now,
        }
        return _store_notification(state, record)

    # Status is 'pending' or 'failed' -> never suppress; transition to 'delivered'
    delivery_count = int(existing.get("deliveryCount") or 0) + 1
    record = {
        **existing,
        "status": "delivered",
        "ownerId": clean_owner,
        "deliveredBy": clean_owner,
        "channel": channel,
        "deliveryCount": delivery_count,
        "deliveryAttempts": delivery_count,
        "duplicateSuppressed": False,
        "needsImmediateDelivery": False,
        "lastError": None,
        "deliveredAtUtc": now,
        "updatedAtUtc": now,
    }
    return _store_notification(state, record)


def mark_notification_failed(
    state: dict[str, Any],
    *,
    run_id: str,
    review_packet_sha256: str,
    owner_id: Optional[str] = None,
    error: str = "notification delivery failed",
    channel: str = "coordinator",
) -> dict[str, Any]:
    """Record a notification delivery failure so it remains eligible for retry and reconciliation."""
    if owner_id is not None:
        _verify_single_owner_lease(state, owner_id)
    existing = _require_bound_notification(
        state,
        run_id=run_id,
        review_packet_sha256=review_packet_sha256,
    )
    now = _utc_now()
    failure_count = int(existing.get("failureCount") or 0) + 1
    record = {
        **existing,
        "status": "failed",
        "ownerId": owner_id.strip() if isinstance(owner_id, str) and owner_id.strip() else existing.get("ownerId"),
        "channel": channel,
        "failureCount": failure_count,
        "lastError": str(error),
        "duplicateSuppressed": False,
        "needsImmediateDelivery": True,
        "updatedAtUtc": now,
    }
    return _store_notification(state, record)


def mark_notification_acknowledged(
    state: dict[str, Any],
    *,
    run_id: str,
    review_packet_sha256: str,
    acknowledged_by: str,
) -> dict[str, Any]:
    """Transition a review-gate notification bound to (runId, reviewPacketSha256) to acknowledged."""
    if not isinstance(acknowledged_by, str) or not acknowledged_by.strip():
        raise ValueError("acknowledged_by must be a non-empty string")
    existing = _require_bound_notification(
        state,
        run_id=run_id,
        review_packet_sha256=review_packet_sha256,
    )
    now = _utc_now()
    record = {
        **existing,
        "status": "acknowledged",
        "acknowledgedBy": acknowledged_by.strip(),
        "acknowledgedAtUtc": now,
        "needsImmediateDelivery": False,
        "duplicateSuppressed": False,
        "updatedAtUtc": now,
    }
    return _store_notification(state, record)


def reconcile_pending_notifications(state: dict[str, Any]) -> dict[str, Any]:
    """Reconcile undelivered (pending/failed) notifications after restart or model change.

    Never counts a passive status summary as delivery and never creates a duplicate workflow executor.
    """
    if not isinstance(state, dict):
        raise ValueError("state must be a dict")

    notifications = _get_notifications_map(state)
    now = _utc_now()
    pending_records: list[dict[str, Any]] = []
    reconciled_map: dict[str, dict[str, Any]] = {}

    for run_id, record in sorted(notifications.items()):
        status = str(record.get("status") or "pending")
        if status not in VALID_NOTIFICATION_STATES:
            status = "pending"
        is_undelivered = status in {"pending", "failed"}
        updated = {
            **record,
            "runId": run_id,
            "status": status,
            "needsImmediateDelivery": is_undelivered,
            "duplicateSuppressed": False if is_undelivered else bool(record.get("duplicateSuppressed", False)),
            "reconciledAfterRestart": True,
            "reconciledAtUtc": now,
        }
        reconciled_map[run_id] = updated
        if is_undelivered:
            pending_records.append(updated)

    state["reviewNotifications"] = reconciled_map
    current = state.get("reviewNotification")
    if isinstance(current, Mapping):
        curr_run = str(current.get("runId") or "")
        if curr_run in reconciled_map:
            state["reviewNotification"] = reconciled_map[curr_run]
            state["reviewNotificationState"] = reconciled_map[curr_run]
    elif pending_records:
        state["reviewNotification"] = pending_records[0]
        state["reviewNotificationState"] = pending_records[0]

    summary = {
        "reconciled": True,
        "reconciledAtUtc": now,
        "pendingNotificationCount": len(pending_records),
        "pendingCount": len(pending_records),
        "pendingNotifications": pending_records,
        "needsImmediateDelivery": len(pending_records) > 0,
        "countedAsDelivery": False,
        "countsAsDelivery": False,
        "singleOwnerReadOnlySchedule": True,
        "createsExecutor": False,
        "notifications": reconciled_map,
    }
    state["notificationReconciliation"] = summary
    return summary


__all__ = [
    "NOTIFICATION_STATES",
    "VALID_NOTIFICATION_STATES",
    "mark_notification_acknowledged",
    "mark_notification_delivered",
    "mark_notification_failed",
    "reconcile_pending_notifications",
    "sync_review_gate_notification",
]
