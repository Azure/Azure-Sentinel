from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:
    fcntl = None
    import msvcrt

from solution_manager.core.artifacts import existing_artifact_path, report_directory, using_run
from solution_manager.migration.converter import runtime_validation_plan
from solution_manager.qualification.runtime import current_runtime_evidence
from solution_manager.core.workflow import next_workflow_stage, workflow_status

REGISTRY_NAME = "registry.json"
DEFAULT_IDLE_SECONDS = 900
ENVIRONMENT_WRITE_STAGES = {"deployment", "mockIngestion", "alertParity"}
AUTH_PURPOSES = {
    "validation:sentinel-runtime": "sentinelRuntime",
    "validation:advanced-hunting": "advancedHunting",
    "deployment": "customDetection",
}


def default_registry_path() -> Path:
    repository_root = Path(__file__).resolve().parents[4]
    return repository_root / "Tools" / "ignored" / "sentinel-xdr-coordinator" / REGISTRY_NAME


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_registry(path: str | Path | None) -> Path:
    return Path(path).expanduser().resolve() if path else default_registry_path()


@contextmanager
def _registry_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as handle:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        else:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            else:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def _atomic_json(path: Path, document: dict[str, Any]) -> None:
    content = (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp",
            dir=path.parent, delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
        if fcntl is not None:
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _empty_registry() -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "revision": 0,
        "updatedAt": _timestamp(),
        "solutions": {},
        "events": [],
        "outbox": [],
        "sharedDependencies": {},
    }


def _read_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _empty_registry()
    document = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(document, dict)
        or document.get("schemaVersion") != "1.0.0"
        or not isinstance(document.get("solutions"), dict)
        or not isinstance(document.get("events"), list)
        or not isinstance(document.get("outbox"), list)
        or not isinstance(document.get("sharedDependencies"), dict)
    ):
        raise ValueError(f"invalid coordinator registry: {path}")
    return document


def _write_registry(path: Path, document: dict[str, Any]) -> None:
    document["revision"] = int(document.get("revision", 0)) + 1
    document["updatedAt"] = _timestamp()
    _atomic_json(path, document)


def _entry_key(solution: Path, run_id: str) -> str:
    return _sha256(_canonical({"solution": str(solution), "runId": run_id}))


def _record_event(
    registry: dict[str, Any],
    *,
    event_id: str,
    kind: str,
    payload: dict[str, Any],
    scope: str | None = None,
) -> tuple[dict[str, Any], bool]:
    if not event_id.strip() or len(event_id) > 200:
        raise ValueError("event ID must be non-empty and at most 200 characters")
    event_hash = _sha256(_canonical({"kind": kind, "payload": payload}))
    for existing in registry["events"]:
        if existing["eventId"] != event_id or existing.get("scope") != scope:
            continue
        if existing["eventSha256"] != event_hash:
            raise ValueError(f"event ID was already used with different content: {event_id}")
        return existing, False
    event = {
        "eventId": event_id,
        "scope": scope,
        "eventSha256": event_hash,
        "kind": kind,
        "payload": payload,
        "createdAt": _timestamp(),
        "consumedAt": None,
    }
    registry["events"].append(event)
    return event, True


def _append_system_event(
    registry: dict[str, Any], event_id: str, kind: str, payload: dict[str, Any]
) -> None:
    _record_event(
        registry,
        event_id=event_id,
        kind=kind,
        payload=payload,
        scope=payload.get("entryId"),
    )


def _authoritative_claim_completion(
    claim: dict[str, Any] | None,
    action: dict[str, Any] | None,
    snapshot: dict[str, Any],
    *,
    action_id: str,
    target_sha256: str | None,
    evidence_sha256: str | None,
) -> bool:
    if (
        not claim
        or claim.get("status") not in {"active", "expired-unknown"}
        or claim.get("actionId") != action_id
        or not action
        or action.get("actionId") != action_id
        or action.get("actionSha256") != claim.get("actionSha256")
        or action.get("targetSha256") != claim.get("targetSha256")
        or action.get("stage") != claim.get("stage")
        or target_sha256 != claim.get("targetSha256")
        or target_sha256 != snapshot["target"]["sha256"]
        or not evidence_sha256
    ):
        return False
    stage = (snapshot["status"].get("stages") or {}).get(action.get("stage"), {})
    if stage.get("status") not in {"passed", "failed", "blocked"}:
        return False
    return any(
        evidence.get("sha256") == evidence_sha256
        for evidence in snapshot["stageEvidence"].get(action.get("stage"), [])
    )


def _claim_stage_is_officially_complete(
    claim: dict[str, Any], snapshot: dict[str, Any]
) -> bool:
    if claim.get("targetSha256") != snapshot["target"]["sha256"]:
        return False
    stage = (snapshot["status"].get("stages") or {}).get(claim.get("stage"), {})
    return stage.get("status") in {"passed", "failed", "blocked"}


def _hash_local_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_evidence(root: Path, refs: list[Any]) -> list[dict[str, str]]:
    evidence: dict[str, str] = {}
    for raw in refs:
        if not isinstance(raw, str) or not raw:
            continue
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = root / candidate
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(root)
        except (OSError, ValueError):
            continue
        if resolved.is_file():
            evidence[resolved.relative_to(root).as_posix()] = _hash_local_file(resolved)
    return [
        {"path": item, "sha256": digest}
        for item, digest in sorted(evidence.items())
    ]


def _target_snapshot(solution: Path, state: dict[str, Any]) -> dict[str, Any]:
    context = state.get("context") or {}
    fields = (
        "tenantId",
        "subscriptionId",
        "workspaceResourceId",
        "workspaceCustomerId",
    )
    target = {field: context.get(field) for field in fields if context.get(field)}
    target_path = existing_artifact_path(solution, "qualification-target.json")
    if target_path.is_file():
        try:
            stored_target = json.loads(target_path.read_text(encoding="utf-8-sig"))
            if isinstance(stored_target, dict):
                file_target = {
                    field: stored_target.get(field)
                    for field in fields
                    if stored_target.get(field)
                }
                if target and target != file_target:
                    raise ValueError(
                        "qualification-target.json does not match the persisted workflow target"
                    )
                if not target and file_target:
                    raise ValueError(
                        "qualification target sidecar exists without a persisted workflow target"
                    )
                target = file_target
        except (OSError, json.JSONDecodeError):
            raise ValueError("locked Qualification target is unreadable")
    return {
        "values": target,
        "sha256": _sha256(_canonical(target)) if target else None,
        "path": (
            str(target_path)
            if target_path.is_file()
            else None
        ),
        "fileSha256": _hash_local_file(target_path) if target_path.is_file() else None,
    }


def _workflow_snapshot(solution: str | Path) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    status_before = workflow_status(root)
    run_id = status_before.get("runId")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("selected workflow has no persisted run ID")
    state_path = Path(status_before["statePath"]).resolve()
    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    if state.get("runId") != run_id:
        raise ValueError("workflow state run ID does not match the selected run")
    state_sha256 = _hash_local_file(state_path)
    next_action = next_workflow_stage(root)
    if next_action.get("runId") != run_id:
        raise ValueError("workflow-next returned a different run ID")
    status = workflow_status(root)
    compared_fields = ("runId", "workflowStatus", "context", "stages")
    if (
        _hash_local_file(state_path) != state_sha256
        or any(status_before.get(field) != status.get(field) for field in compared_fields)
    ):
        raise ValueError(
            "workflow state changed while taking the coordinator snapshot; reconcile again"
        )
    target = _target_snapshot(root, state)
    stage_evidence = {}
    for name, stage in (status.get("stages") or {}).items():
        stage_evidence[name] = _file_evidence(
            root,
            list(stage.get("artifacts", {}).values())
            + list(stage.get("evidence", [])),
        )
    return {
        "solution": str(root),
        "runId": run_id,
        "statePath": str(state_path),
        "stateSha256": state_sha256,
        "workflowStatus": status.get("workflowStatus"),
        "profile": (status.get("context") or {}).get("workflowProfile"),
        "status": status,
        "next": next_action,
        "target": target,
        "stageEvidence": stage_evidence,
    }


def _required_shared_dependencies(entry: dict[str, Any], action_id: str) -> list[dict[str, Any]]:
    requirements = entry.get("requiredSharedDependencies") or {}
    return requirements.get(action_id, [])


def _dependency_key(key: str, purpose: str, target_sha256: str | None) -> str:
    return _sha256(_canonical({
        "key": key,
        "purpose": purpose,
        "targetSha256": target_sha256,
    }))


def _apply_shared_dependencies(
    registry: dict[str, Any],
    entry: dict[str, Any],
    action: dict[str, Any],
) -> None:
    required = _required_shared_dependencies(entry, action["actionId"])
    observed = []
    for requirement in required:
        key = requirement["key"]
        purpose = requirement["purpose"]
        dep_id = _dependency_key(key, purpose, action.get("targetSha256"))
        dependency = registry["sharedDependencies"].get(dep_id)
        evidence_path = (
            Path(dependency["solution"]) / dependency["evidencePath"]
            if dependency
            and dependency.get("solution")
            and dependency.get("evidencePath")
            else None
        )
        try:
            evidence_current = bool(
                evidence_path
                and evidence_path.is_file()
                and _hash_local_file(evidence_path) == dependency.get("evidenceSha256")
            )
        except OSError:
            evidence_current = False
        reported = bool(
            dependency
            and dependency.get("status") == "reported"
            and evidence_current
        )
        observed.append({
            **requirement,
            "targetSha256": action.get("targetSha256"),
            "status": "reported" if reported else "missing",
            "evidenceSha256": dependency.get("evidenceSha256") if dependency else None,
        })
        if not reported and action["status"] not in {"complete", "blocked"}:
            action["status"] = "blocked"
            action["reason"] = (
                f"required shared dependency is not complete for purpose {purpose}: {key}"
            )
    action["sharedPrerequisites"] = observed


def _runtime_actions(root: Path, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    stages = snapshot["status"].get("stages") or {}
    if (
        snapshot["profile"] not in {"authoring", "qualification"}
        or stages.get("conversion", {}).get("status") != "passed"
        or stages.get("validation", {}).get("status") in {"passed", "notRequired"}
    ):
        return []
    try:
        plan = runtime_validation_plan(root)
        evidence = current_runtime_evidence(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [{
            "actionId": "validation:runtime-evidence",
            "stage": "validation",
            "purpose": "runtimeEvidence",
            "status": "blocked",
            "reason": f"current exact-query plan is unavailable: {type(exc).__name__}",
            "prerequisites": [{"stage": "conversion", "status": "passed"}],
            "evidence": [],
            "targetSha256": snapshot["target"]["sha256"],
        }]
    if not plan.get("rules"):
        return []
    query_hashes = {
        provider: _sha256(_canonical(sorted(
            rule.get(field)
            for rule in plan["rules"]
            if isinstance(rule.get(field), str)
        )))
        for provider, field in (
            ("sentinelRuntime", "sentinelQuerySha256"),
            ("advancedHunting", "advancedHuntingQuerySha256"),
        )
    }
    report_root = report_directory(root)
    source_paths = [
        report_root / f"runtime-validation.{provider}.json"
        for provider in ("triage-mcp", "azure-monitor-sdk", "log-analytics-cli")
    ]
    source_report = next((path for path in source_paths if path.is_file()), None)
    graph_report = report_root / "runtime-validation.graph.json"
    source_passed = evidence.get("sourceStatus") in {"passed", "source-waived"}
    graph_passed = bool(evidence.get("graphReport"))
    common = {
        "stage": "validation",
        "targetSha256": snapshot["target"]["sha256"],
        "prerequisites": [{
            "stage": "conversion",
            "status": "passed",
            "evidence": snapshot["stageEvidence"].get("conversion", []),
        }],
    }
    return [
        {
            **common,
            "actionId": "validation:sentinel-runtime",
            "purpose": "sentinelRuntime",
            "authPurpose": None,
            "querySetSha256": query_hashes["sentinelRuntime"],
            "status": (
                "complete" if source_passed
                else "blocked" if source_report
                else "approval-needed"
            ),
            "result": evidence.get("sourceStatus") if source_passed else None,
            "reason": (
                "Current source-family evidence is not passing; inspect the persisted report before any retry."
                if source_report and not source_passed else
                "Explicit user authorization is required before read-only source queries."
                if not source_passed else None
            ),
            "evidence": _file_evidence(root, [str(source_report)] if source_report else []),
        },
        {
            **common,
            "actionId": "validation:advanced-hunting",
            "purpose": "advancedHunting",
            "authPurpose": "advancedHunting",
            "querySetSha256": query_hashes["advancedHunting"],
            "status": (
                "complete" if graph_passed
                else "blocked" if graph_report.is_file()
                else "approval-needed"
            ),
            "reason": (
                "Current Advanced Hunting evidence is not passing; inspect the persisted report before any retry."
                if graph_report.is_file() and not graph_passed else
                "Explicit user authorization is required before Advanced Hunting queries."
                if not graph_passed else None
            ),
            "evidence": _file_evidence(root, [str(graph_report)] if graph_report.is_file() else []),
        },
    ]


def _derive_actions(
    registry: dict[str, Any],
    entry: dict[str, Any],
    snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    next_info = snapshot["next"]
    status = snapshot["status"]
    actions: list[dict[str, Any]] = []
    next_stage = next_info.get("next")
    if next_stage:
        stage_status = (status.get("stages") or {}).get(next_stage, {})
        needs_approval = next_stage in ENVIRONMENT_WRITE_STAGES
        release_action_needed = (
            next_stage == "packaging"
            and bool(next_info.get("releaseActionRequired"))
        )
        if next_stage in ENVIRONMENT_WRITE_STAGES and not snapshot["target"]["sha256"]:
            action_status = "blocked"
            reason = "qualification target is not available in the persisted workflow state"
        elif stage_status.get("status") == "running":
            action_status = "running"
            reason = "existing workflow state reports this stage running"
        elif release_action_needed:
            action_status = "approval-needed"
            freshness = next_info.get("packageFreshness") or {}
            reason = (
                "an explicit package-version action is required for the current input hash "
                f"{freshness.get('currentPackageInputSha256') or 'unavailable'}"
            )
        else:
            action_status = "approval-needed" if needs_approval else "ready"
            reason = (
                "read-only preflight and exact-scope user approval are still required; no live command is dispatched here"
                if needs_approval else None
            )
        action = {
            "actionId": next_stage,
            "stage": next_stage,
            "status": action_status,
            "purpose": AUTH_PURPOSES.get(next_stage),
            "reason": reason,
            "prerequisites": [{
                "workflowNextBlockedBy": next_info.get("blockedBy") or [],
                "workflowStatus": status.get("workflowStatus"),
                "releaseActionRequired": next_info.get("releaseActionRequired", False),
                "packageFreshness": next_info.get("packageFreshness"),
                "passedStages": {
                    name: {
                        "status": stage.get("status"),
                        "evidence": snapshot["stageEvidence"].get(name, []),
                    }
                    for name, stage in (status.get("stages") or {}).items()
                    if stage.get("status") == "passed"
                },
            }],
            "evidence": snapshot["stageEvidence"].get(next_stage, []),
            "targetSha256": snapshot["target"]["sha256"],
            "target": snapshot["target"]["values"],
            "stateSha256": snapshot["stateSha256"],
        }
        if next_stage == "deployment":
            action["recommendedCommands"] = ["preflight-deployment"]
            action["serviceSettingsVerifiedByCoordinator"] = False
            action["authorizationGrantedByCoordinator"] = False
        elif release_action_needed:
            action["recommendedCommands"] = ["workflow-plan-package-release"]
            action["packageInputSha256"] = (
                (next_info.get("packageFreshness") or {}).get("currentPackageInputSha256")
            )
        if next_stage == "validation":
            actions.extend(_runtime_actions(Path(snapshot["solution"]), snapshot))
        actions.append(action)
    elif status.get("workflowStatus") == "completed":
        actions.append({
            "actionId": "workflow",
            "stage": None,
            "status": "complete",
            "purpose": None,
            "reason": None,
            "prerequisites": [],
            "evidence": [],
            "targetSha256": snapshot["target"]["sha256"],
            "target": snapshot["target"]["values"],
            "stateSha256": snapshot["stateSha256"],
        })
    else:
        actions.append({
            "actionId": "workflow",
            "stage": None,
            "status": "blocked",
            "purpose": None,
            "reason": "the existing workflow reports no stage eligible to start",
            "prerequisites": [{
                "workflowStatus": status.get("workflowStatus"),
                "blockedBy": next_info.get("blockedBy") or [],
            }],
            "evidence": [],
            "targetSha256": snapshot["target"]["sha256"],
            "target": snapshot["target"]["values"],
            "stateSha256": snapshot["stateSha256"],
        })
    owner = entry.get("owner")
    for action in actions:
        action.setdefault("authPurpose", AUTH_PURPOSES.get(action["actionId"]))
        action.setdefault("querySetSha256", None)
        action["prerequisitesSha256"] = _sha256(_canonical(action["prerequisites"]))
        action["evidenceSha256"] = _sha256(_canonical(action["evidence"]))
        action["sharedPrerequisites"] = []
        _apply_shared_dependencies(registry, entry, action)
        action["actionSha256"] = _sha256(_canonical({
            "runId": snapshot["runId"],
            "actionId": action["actionId"],
            "stage": action["stage"],
            "targetSha256": action["targetSha256"],
            "prerequisitesSha256": action["prerequisitesSha256"],
            "evidenceSha256": action["evidenceSha256"],
            "querySetSha256": action["querySetSha256"],
            "purpose": action["purpose"],
            "authPurpose": action["authPurpose"],
            "sharedPrerequisites": action["sharedPrerequisites"],
            "owner": entry.get("owner"),
        }))
        if not owner:
            action["status"] = "blocked"
            action["reason"] = "an accountable owner is required before coordination"
    return actions


def _expire_claim_if_needed(registry: dict[str, Any], entry: dict[str, Any]) -> None:
    claim = entry.get("claim")
    if not claim or claim.get("status") != "active":
        return
    if _parse_timestamp(claim["expiresAt"]) > _now():
        return
    claim["status"] = "expired-unknown"
    claim["expiredAt"] = _timestamp()
    claim["outcome"] = "unknown"
    entry["updatedAt"] = _timestamp()
    _append_system_event(
        registry,
        f"claim-expired:{claim['claimId']}",
        "claim-expired-unknown",
        {
            "entryId": entry["entryId"],
            "claimId": claim["claimId"],
            "actionId": claim["actionId"],
            "targetSha256": claim["targetSha256"],
        },
    )


def _watchdog(
    registry: dict[str, Any],
    entry: dict[str, Any],
    actions: list[dict[str, Any]],
    idle_seconds: int,
) -> list[dict[str, str]]:
    now = _now()
    warnings: list[dict[str, str]] = []
    if not entry.get("owner"):
        warnings.append({"type": "missing-owner", "message": "work item has no accountable owner"})
    claim = entry.get("claim") or {}
    for action in actions:
        if (
            action["status"] == "ready"
            and _parse_timestamp(entry.get("decisionAt") or entry["createdAt"])
            < now - timedelta(seconds=idle_seconds)
            and claim.get("status") != "active"
        ):
            warnings.append({
                "type": "ready-idle",
                "message": f"ready action has no active executor: {action['actionId']}",
            })
        if action["status"] == "running":
            claim = entry.get("claim")
            if not claim or claim.get("status") != "active":
                warnings.append({
                    "type": "running-without-claim",
                    "message": f"workflow stage is running without a tracked claim: {action['actionId']}",
                })
    for event in registry["events"]:
        if (
            event.get("kind") == "executor-completed"
            and event.get("payload", {}).get("entryId") == entry["entryId"]
            and event.get("consumedAt") is None
        ):
            warnings.append({
                "type": "unconsumed-handoff",
                "message": f"completion handoff has not been matched to workflow state: {event['eventId']}",
            })
    pending = [
        item for item in registry["outbox"]
        if item.get("entryId") == entry["entryId"] and item.get("status") == "pending"
    ]
    for item in pending:
        if _parse_timestamp(item["createdAt"]) < now - timedelta(seconds=idle_seconds):
            warnings.append({
                "type": (
                    "undelivered-approval"
                    if item.get("kind") == "approval-request"
                    else "undelivered-handoff"
                ),
                "message": f"outbox item remains unacknowledged: {item['deliveryId']}",
            })
    claim = entry.get("claim")
    if claim and (
        claim.get("status") == "expired-unknown"
        or (
            claim.get("status") == "active"
            and _parse_timestamp(claim["expiresAt"]) <= now
        )
    ):
        warnings.append({
            "type": "expired-claim-unknown",
            "message": "executor lease expired with unknown outcome; dispatch remains blocked",
        })
    return warnings


def _publish_decision(
    registry: dict[str, Any], entry: dict[str, Any], actions: list[dict[str, Any]]
) -> None:
    decision = {
        "actions": actions,
        "owner": entry.get("owner"),
        "targetSha256": entry.get("targetSha256"),
    }
    decision_hash = _sha256(_canonical(decision))
    if decision_hash == entry.get("decisionSha256"):
        return
    generation = int(entry.get("decisionGeneration", 0)) + 1
    entry["decisionGeneration"] = generation
    entry["decisionSha256"] = decision_hash
    entry["decisionAt"] = _timestamp()
    entry["actions"] = actions
    entry["updatedAt"] = _timestamp()
    current_actions = {item["actionId"]: item for item in actions}
    for item in registry["outbox"]:
        if item.get("entryId") != entry["entryId"] or item.get("status") != "pending":
            continue
        previous_action = item.get("action") or {}
        current_action = current_actions.get(previous_action.get("actionId"))
        if (
            not current_action
            or current_action.get("actionSha256") != previous_action.get("actionSha256")
            or current_action.get("targetSha256") != previous_action.get("targetSha256")
            or current_action.get("status") != previous_action.get("status")
        ):
            item["status"] = "superseded"
            item["supersededAt"] = _timestamp()
            item["supersededReason"] = "current workflow decision, target, or evidence changed"
            _append_system_event(
                registry,
                f"outbox-superseded:{item['deliveryId']}",
                "outbox-item-superseded",
                {
                    "entryId": entry["entryId"],
                    "deliveryId": item["deliveryId"],
                    "reason": item["supersededReason"],
                },
            )
    for action in actions:
        if action["status"] in {"ready", "approval-needed", "blocked", "complete"}:
            kind = "action-decision"
            delivery_id = _sha256(_canonical({
                "entryId": entry["entryId"],
                "decisionGeneration": generation,
                "actionSha256": action["actionSha256"],
                "status": action["status"],
                "kind": kind,
            }))
            if not any(item.get("deliveryId") == delivery_id for item in registry["outbox"]):
                registry["outbox"].append({
                    "deliveryId": delivery_id,
                    "entryId": entry["entryId"],
                    "decisionGeneration": generation,
                    "kind": kind,
                    "status": "pending",
                    "owner": entry.get("owner"),
                    "action": action,
                    "createdAt": _timestamp(),
                    "acknowledgedAt": None,
                    "acknowledgedBy": None,
                })
    _append_system_event(
        registry,
        f"decision:{entry['entryId']}:{generation}:{decision_hash}",
        "decision-created",
        {
            "entryId": entry["entryId"],
            "decisionSha256": decision_hash,
            "decisionGeneration": generation,
        },
    )


def _load_entry(
    registry: dict[str, Any], snapshot: dict[str, Any]
) -> dict[str, Any]:
    key = _entry_key(Path(snapshot["solution"]), snapshot["runId"])
    entry = registry["solutions"].get(key)
    if not entry:
        raise ValueError("workflow is not enrolled; use coordinator-enroll with an accountable owner")
    if entry.get("runId") != snapshot["runId"] or entry.get("solution") != snapshot["solution"]:
        raise ValueError("coordinator entry identity does not match the selected run")
    return entry


def _reconcile_locked(
    registry: dict[str, Any],
    entry: dict[str, Any],
    snapshot: dict[str, Any],
    *,
    idle_seconds: int = DEFAULT_IDLE_SECONDS,
) -> dict[str, Any]:
    _expire_claim_if_needed(registry, entry)
    entry["targetSha256"] = snapshot["target"]["sha256"]
    actions = _derive_actions(registry, entry, snapshot)
    claim = entry.get("claim")
    if claim and claim.get("status") == "active":
        matching = next(
            (
                action for action in actions
                if action["actionId"] == claim["actionId"]
                and action["actionSha256"] == claim["actionSha256"]
                and action["targetSha256"] == claim["targetSha256"]
            ),
            None,
        )
        if matching:
            matching["status"] = "running"
            matching["claimId"] = claim["claimId"]
            matching["executor"] = claim["executor"]
        elif _claim_stage_is_officially_complete(claim, snapshot):
            retry_action = next(
                (action for action in actions if action["actionId"] == claim["actionId"]),
                None,
            )
            if retry_action:
                retry_action["status"] = "blocked"
                retry_action["reason"] = (
                    "the prior claim's terminal workflow result is awaiting an "
                    "authoritative completion handoff before retry"
                )
                retry_action["claimId"] = claim["claimId"]
        else:
            claim["status"] = "stale"
            claim["outcome"] = "stale-target-or-evidence"
    elif claim and claim.get("status") == "expired-unknown":
        for action in actions:
            if action["actionId"] == claim.get("actionId"):
                action["status"] = "blocked"
                action["reason"] = (
                    "executor lease expired with unknown outcome; obtain an authoritative "
                    "result before any retry"
                )
                action["claimId"] = claim["claimId"]
    _publish_decision(registry, entry, actions)
    entry["observedWorkflowStateSha256"] = snapshot["stateSha256"]
    entry["workflowStatus"] = snapshot["workflowStatus"]
    entry["nextStage"] = snapshot["next"].get("next")
    entry["observedAt"] = _timestamp()
    return {
        "entryId": entry["entryId"],
        "solution": snapshot["solution"],
        "runId": snapshot["runId"],
        "owner": entry.get("owner"),
        "workflowStatus": snapshot["workflowStatus"],
        "nextStage": snapshot["next"].get("next"),
        "target": snapshot["target"],
        "actions": actions,
        "outbox": [
            item for item in registry["outbox"]
            if item.get("entryId") == entry["entryId"] and item.get("status") == "pending"
        ],
        "watchdog": _watchdog(registry, entry, actions, idle_seconds),
        "registryRevision": registry["revision"],
        "dispatchMode": "shadow",
        "automaticCommandExecution": False,
    }


def enroll(
    solution: str | Path,
    *,
    owner: str,
    required_shared_dependencies: list[str] | None = None,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    if not owner.strip():
        raise ValueError("an accountable owner is required")
    registry_file = _safe_registry(registry_path)
    with _registry_lock(registry_file):
        registry = _read_registry(registry_file)
        snapshot = _workflow_snapshot(solution)
        key = _entry_key(Path(snapshot["solution"]), snapshot["runId"])
        required: dict[str, list[dict[str, str]]] = {}
        for declaration in required_shared_dependencies or []:
            action, separator, dependency = declaration.partition("=")
            dep_key, purpose_separator, purpose = dependency.partition(":")
            if not separator or not action or not purpose_separator or not dep_key or not purpose:
                raise ValueError(
                    "shared dependency must be ACTION=KEY:PURPOSE"
                )
            if action not in {
                "discovery", "conversion", "validation", "packaging",
                "deployment", "mockIngestion", "alertParity", "report",
                "validation:sentinel-runtime", "validation:advanced-hunting",
            }:
                raise ValueError(f"unknown shared-dependency action: {action}")
            required.setdefault(action, []).append({"key": dep_key, "purpose": purpose})
        entry = registry["solutions"].get(key)
        if entry:
            if entry.get("owner") and entry.get("owner") != owner:
                raise ValueError(
                    "work item already has a different accountable owner; use an explicit owner handoff"
                )
            if not entry.get("owner"):
                entry["owner"] = owner.strip()
                _append_system_event(
                    registry,
                    f"owner-assigned:{key}:{_sha256(owner.strip().encode())}",
                    "accountable-owner-assigned",
                    {
                        "entryId": key,
                        "owner": owner.strip(),
                        "previousOwner": None,
                        "assignmentMethod": "explicit-enrollment",
                    },
                )
            if entry.get("requiredSharedDependencies", {}) != required:
                raise ValueError("enrollment dependencies are immutable for this run")
        else:
            entry = {
                "entryId": key,
                "solution": snapshot["solution"],
                "runId": snapshot["runId"],
                "owner": owner.strip(),
                "createdAt": _timestamp(),
                "updatedAt": _timestamp(),
                "targetSha256": snapshot["target"]["sha256"],
                "requiredSharedDependencies": required,
                "claim": None,
                "events": [],
            }
            registry["solutions"][key] = entry
            _append_system_event(
                registry,
                f"enrolled:{key}",
                "work-item-enrolled",
                {
                    "entryId": key,
                    "runId": snapshot["runId"],
                    "owner": owner.strip(),
                    "targetSha256": snapshot["target"]["sha256"],
                },
            )
        result = _reconcile_locked(registry, entry, snapshot)
        _write_registry(registry_file, registry)
        result["registryPath"] = str(registry_file)
        result["registryRevision"] = registry["revision"]
        return result


def reconcile(
    solution: str | Path,
    *,
    registry_path: str | Path | None = None,
    idle_seconds: int = DEFAULT_IDLE_SECONDS,
) -> dict[str, Any]:
    registry_file = _safe_registry(registry_path)
    with _registry_lock(registry_file):
        registry = _read_registry(registry_file)
        snapshot = _workflow_snapshot(solution)
        entry = _load_entry(registry, snapshot)
        result = _reconcile_locked(
            registry, entry, snapshot, idle_seconds=idle_seconds
        )
        _write_registry(registry_file, registry)
        result["registryPath"] = str(registry_file)
        result["registryRevision"] = registry["revision"]
        return result


def status(
    solution: str | Path,
    *,
    registry_path: str | Path | None = None,
    idle_seconds: int = DEFAULT_IDLE_SECONDS,
) -> dict[str, Any]:
    registry_file = _safe_registry(registry_path)
    with _registry_lock(registry_file):
        registry = _read_registry(registry_file)
        snapshot = _workflow_snapshot(solution)
        entry = _load_entry(registry, snapshot)
        result = _reconcile_locked(
            registry, entry, snapshot, idle_seconds=idle_seconds
        )
        result["claim"] = dict(entry["claim"]) if entry.get("claim") else None
        result["outbox"] = [
            item for item in registry["outbox"]
            if item.get("entryId") == entry["entryId"]
        ]
        _write_registry(registry_file, registry)
        result["registryPath"] = str(registry_file)
        result["registryRevision"] = registry["revision"]
        return result


def claim(
    solution: str | Path,
    *,
    action_id: str,
    executor: str,
    claim_key: str,
    lease_seconds: float = 300,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    if lease_seconds <= 0 or lease_seconds > 86400:
        raise ValueError("claim lease must be greater than 0 and no more than 86400 seconds")
    if not executor.strip() or not claim_key.strip():
        raise ValueError("executor and idempotency claim key are required")
    registry_file = _safe_registry(registry_path)
    with _registry_lock(registry_file):
        registry = _read_registry(registry_file)
        snapshot = _workflow_snapshot(solution)
        entry = _load_entry(registry, snapshot)
        _expire_claim_if_needed(registry, entry)
        if (entry.get("claim") or {}).get("status") == "expired-unknown":
            raise ValueError(
                "previous claim has unknown outcome; reconcile it before another claim"
            )
        actions = _derive_actions(registry, entry, snapshot)
        action = next((item for item in actions if item["actionId"] == action_id), None)
        if action is None:
            raise ValueError(f"action is not currently offered: {action_id}")
        if action["status"] != "ready":
            raise ValueError(
                f"action is not claimable in shadow mode (status={action['status']}); "
                "approval-needed and blocked actions cannot be dispatched"
            )
        existing = entry.get("claim")
        if existing and existing.get("status") == "active":
            if (
                existing.get("executor") == executor
                and existing.get("claimKey") == claim_key
                and existing.get("actionSha256") == action["actionSha256"]
            ):
                result = dict(existing)
                result["idempotentReplay"] = True
                return result
            raise ValueError("another executor holds the active atomic claim")
        claim_id = _sha256(_canonical({
            "entryId": entry["entryId"],
            "actionSha256": action["actionSha256"],
            "executor": executor,
            "claimKey": claim_key,
        }))
        now = _now()
        claim_record = {
            "claimId": claim_id,
            "claimKey": claim_key,
            "actionId": action_id,
            "actionSha256": action["actionSha256"],
            "action": dict(action),
            "stage": action["stage"],
            "targetSha256": action["targetSha256"],
            "executor": executor.strip(),
            "status": "active",
            "claimedAt": _timestamp(now),
            "heartbeatAt": _timestamp(now),
            "expiresAt": _timestamp(now + timedelta(seconds=lease_seconds)),
            "outcome": "pending",
            "dispatchMode": "shadow",
        }
        entry["claim"] = claim_record
        _append_system_event(
            registry,
            f"claim:{claim_id}",
            "execution-claim-created",
            {
                "entryId": entry["entryId"],
                "claimId": claim_id,
                "actionId": action_id,
                "actionSha256": action["actionSha256"],
                "targetSha256": action["targetSha256"],
                "executor": executor.strip(),
            },
        )
        _reconcile_locked(registry, entry, snapshot)
        _write_registry(registry_file, registry)
        return {**claim_record, "idempotentReplay": False}


def heartbeat(
    solution: str | Path,
    *,
    claim_id: str,
    executor: str,
    lease_seconds: float = 300,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    if lease_seconds <= 0 or lease_seconds > 86400:
        raise ValueError("claim lease must be greater than 0 and no more than 86400 seconds")
    registry_file = _safe_registry(registry_path)
    with _registry_lock(registry_file):
        registry = _read_registry(registry_file)
        snapshot = _workflow_snapshot(solution)
        entry = _load_entry(registry, snapshot)
        _expire_claim_if_needed(registry, entry)
        current = entry.get("claim")
        if (
            not current
            or current.get("claimId") != claim_id
            or current.get("executor") != executor
            or current.get("status") != "active"
        ):
            raise ValueError("claim is not active for this executor")
        if current.get("targetSha256") != snapshot["target"]["sha256"]:
            current["status"] = "stale"
            current["outcome"] = "target-changed"
            _write_registry(registry_file, registry)
            raise ValueError("claim target changed; no command may be dispatched")
        actions = _derive_actions(registry, entry, snapshot)
        action = next((item for item in actions if item["actionId"] == current["actionId"]), None)
        if not action or action["actionSha256"] != current["actionSha256"]:
            current["status"] = "stale"
            current["outcome"] = "evidence-or-query-changed"
            _write_registry(registry_file, registry)
            raise ValueError("claim evidence or query identity changed; no command may be dispatched")
        now = _now()
        current["heartbeatAt"] = _timestamp(now)
        current["expiresAt"] = _timestamp(now + timedelta(seconds=lease_seconds))
        _append_system_event(
            registry,
            f"heartbeat:{claim_id}:{current['heartbeatAt']}",
            "execution-claim-heartbeat",
            {"entryId": entry["entryId"], "claimId": claim_id, "executor": executor},
        )
        _write_registry(registry_file, registry)
        return dict(current)


def record_event(
    solution: str | Path,
    *,
    event_id: str,
    kind: str,
    action_id: str | None = None,
    purpose: str | None = None,
    target_sha256: str | None = None,
    evidence: str | Path | None = None,
    actor: str | None = None,
    new_owner: str | None = None,
    claim_id: str | None = None,
    outcome: str | None = None,
    reference: str | None = None,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    allowed = {
        "executor-completed",
        "approval-requested",
        "shared-dependency-completed",
        "claim-resolved",
        "owner-handoff",
    }
    if kind not in allowed:
        raise ValueError(f"unsupported coordinator event kind: {kind}")
    registry_file = _safe_registry(registry_path)
    with _registry_lock(registry_file):
        registry = _read_registry(registry_file)
        snapshot = _workflow_snapshot(solution)
        entry = _load_entry(registry, snapshot)
        evidence_path = None
        evidence_sha256 = None
        if evidence:
            evidence_path = Path(evidence).expanduser()
            if not evidence_path.is_absolute():
                evidence_path = Path(snapshot["solution"]) / evidence_path
            evidence_path = evidence_path.resolve(strict=True)
            try:
                evidence_relative = evidence_path.relative_to(Path(snapshot["solution"]))
            except ValueError as exc:
                raise ValueError("coordinator event evidence must be inside the selected solution") from exc
            if not evidence_path.is_file():
                raise ValueError("coordinator event evidence must be a regular file")
            evidence_path = evidence_relative
            evidence_sha256 = _hash_local_file(Path(snapshot["solution"]) / evidence_path)
        current_target = snapshot["target"]["sha256"]
        request = {
            "actionId": action_id,
            "purpose": purpose,
            "targetSha256": target_sha256,
            "evidencePath": evidence_path.as_posix() if evidence_path else None,
            "evidenceSha256": evidence_sha256,
            "actor": actor,
            "newOwner": new_owner,
            "claimId": claim_id,
            "outcome": outcome,
            "reference": reference,
        }
        previous = next(
            (
                item for item in registry["events"]
                if item.get("eventId") == event_id
                and item.get("payload", {}).get("entryId") == entry["entryId"]
            ),
            None,
        )
        if previous:
            if previous.get("kind") != kind or previous.get("payload", {}).get("_request") != request:
                raise ValueError(f"event ID was already used with different content: {event_id}")
            return {
                "eventId": event_id,
                "kind": kind,
                "created": False,
                "consumed": bool(previous.get("consumedAt")),
                "targetSha256": previous.get("payload", {}).get("targetSha256"),
                "evidenceSha256": previous.get("payload", {}).get("evidenceSha256"),
                "reconciliation": None,
                "dispatchMode": "shadow",
                "approvalGranted": False,
            }
        payload: dict[str, Any] = {"entryId": entry["entryId"]}
        action: dict[str, Any] | None = None
        if kind in {"approval-requested", "executor-completed"}:
            if not action_id:
                raise ValueError(f"{kind} requires --action-id")
            actions = _derive_actions(registry, entry, snapshot)
            current_claim = entry.get("claim")
            if (
                kind == "executor-completed"
                and current_claim
                and current_claim.get("actionId") == action_id
                and current_claim.get("status") in {
                    "active", "expired-unknown", "stale"
                }
            ):
                action = dict(current_claim.get("action") or {})
            if not action:
                action = next((item for item in actions if item["actionId"] == action_id), None)
            if not action:
                if kind == "executor-completed":
                    action = next(
                        (
                            item for item in entry.get("actions", [])
                            if item.get("actionId") == action_id
                            and item.get("targetSha256") == target_sha256
                        ),
                        None,
                    )
                if not action:
                    if (
                        current_claim
                        and current_claim.get("status") in {
                            "active", "expired-unknown", "stale"
                        }
                        and current_claim.get("actionId") == action_id
                        and current_claim.get("targetSha256") == target_sha256
                    ):
                        action = dict(current_claim.get("action") or {
                            "actionId": current_claim["actionId"],
                            "actionSha256": current_claim["actionSha256"],
                            "stage": current_claim["stage"],
                            "targetSha256": current_claim["targetSha256"],
                        })
                if not action:
                    raise ValueError(f"action is no longer current: {action_id}")
            if target_sha256 != current_target or target_sha256 != action["targetSha256"]:
                raise ValueError("event target does not match the current locked target")
            if kind == "approval-requested":
                if action["status"] != "approval-needed":
                    raise ValueError("approval request is not needed for the current action")
                expected_purpose = action.get("authPurpose") or action.get("purpose")
                if purpose != expected_purpose:
                    raise ValueError("approval purpose does not match the current action purpose")
                payload.update({
                    "actionId": action_id,
                    "actionSha256": action["actionSha256"],
                    "purpose": purpose,
                    "targetSha256": current_target,
                    "actor": actor,
                })
            else:
                if not evidence_sha256:
                    raise ValueError("executor completion requires hash-bound --evidence")
                current_claim = entry.get("claim")
                if current_claim and current_claim.get("actionId") == action_id:
                    if current_claim.get("status") == "stale":
                        raise ValueError("completion cannot resolve a stale claim binding")
                    if current_claim.get("status") in {"active", "expired-unknown"}:
                        if not _authoritative_claim_completion(
                            current_claim,
                            action,
                            snapshot,
                            action_id=action_id,
                            target_sha256=target_sha256,
                            evidence_sha256=evidence_sha256,
                        ):
                            raise ValueError(
                                "completion does not match the claim's exact target, "
                                "action, and official workflow evidence"
                            )
                payload.update({
                    "actionId": action_id,
                    "actionSha256": action["actionSha256"],
                    "targetSha256": current_target,
                    "evidencePath": evidence_path.as_posix(),
                    "evidenceSha256": evidence_sha256,
                })
        elif kind == "shared-dependency-completed":
            if (
                not action_id or not purpose or not target_sha256
                or not evidence_sha256 or not actor
            ):
                raise ValueError(
                    "shared dependency event requires --action-id (dependency key), --purpose, "
                    "--target-sha256, --actor, and hash-bound --evidence"
                )
            if target_sha256 != current_target:
                raise ValueError("shared dependency target does not match the current target")
            requirement = {
                "key": action_id,
                "purpose": purpose,
                "targetSha256": current_target,
            }
            dep_id = _dependency_key(action_id, purpose, current_target)
            payload.update({
                **requirement,
                "evidencePath": evidence_path.as_posix(),
                "evidenceSha256": evidence_sha256,
                "actor": actor,
            })
            registry["sharedDependencies"][dep_id] = {
                **requirement,
                "status": "reported",
                "solution": snapshot["solution"],
                "evidencePath": evidence_path.as_posix(),
                "evidenceSha256": evidence_sha256,
                "reportedBy": actor,
                "recordedAt": _timestamp(),
                "eventId": event_id,
            }
        elif kind == "owner-handoff":
            if not new_owner or not new_owner.strip() or not actor or not reference:
                raise ValueError("owner handoff requires --new-owner, current-owner --actor, and --reference")
            if entry.get("owner") != actor:
                raise ValueError("only the current accountable owner can hand off ownership")
            payload.update({
                "previousOwner": entry["owner"],
                "owner": new_owner.strip(),
                "actor": actor,
                "reference": reference,
            })
            entry["owner"] = new_owner.strip()
        else:
            if not claim_id or outcome not in {"not-started", "completed", "unknown"}:
                raise ValueError("claim resolution requires --claim-id and a valid --outcome")
            if not actor or not reference:
                raise ValueError("claim resolution requires accountable --actor and --reference")
            if outcome == "not-started" and not evidence_sha256:
                raise ValueError(
                    "confirming a claim was not started requires hash-bound --evidence"
                )
            current = entry.get("claim")
            if not current or current.get("claimId") != claim_id or current.get("status") != "expired-unknown":
                raise ValueError("only an expired unknown claim can be resolved")
            payload.update({
                "claimId": claim_id,
                "outcome": outcome,
                "actor": actor,
                "reference": reference,
                "targetSha256": current["targetSha256"],
            })
            if outcome == "completed":
                action = next(
                    (
                        item for item in entry.get("actions", [])
                        if item.get("actionId") == current.get("actionId")
                        and item.get("actionSha256") == current.get("actionSha256")
                    ),
                    None,
                )
                if action is None and current.get("stage"):
                    action = {
                        "actionId": current["actionId"],
                        "actionSha256": current["actionSha256"],
                        "targetSha256": current["targetSha256"],
                        "stage": current["stage"],
                    }
                if not _authoritative_claim_completion(
                    current,
                    action,
                    snapshot,
                    action_id=current.get("actionId"),
                    target_sha256=target_sha256,
                    evidence_sha256=evidence_sha256,
                ):
                    raise ValueError(
                        "claim completion requires exact current target and evidence "
                        "from an officially completed workflow stage"
                    )
                payload.update({
                    "actionId": current["actionId"],
                    "actionSha256": current["actionSha256"],
                    "targetSha256": current_target,
                    "evidencePath": evidence_path.as_posix(),
                    "evidenceSha256": evidence_sha256,
                })
                current["status"] = "completed"
                current["outcome"] = "authoritative-completion-observed"
                current["completedAt"] = _timestamp()
                current["resolvedBy"] = actor
                current["resolutionReference"] = reference
            elif outcome == "not-started":
                stage = current.get("actionId")
                official_stage = (snapshot["status"].get("stages") or {}).get(stage, {})
                if official_stage.get("status") == "running":
                    raise ValueError(
                        "workflow state still reports the claimed stage running; unknown outcome remains blocked"
                    )
                if current.get("targetSha256") != current_target:
                    raise ValueError("claim target changed; unknown outcome remains blocked")
                current["status"] = "resolved-not-started"
                current["outcome"] = "not-started"
                current["resolvedAt"] = _timestamp()
                current["resolvedBy"] = actor
                current["resolutionReference"] = reference
            else:
                current["status"] = "expired-unknown"
                current["outcome"] = "unknown"
                current["resolutionReference"] = reference
                current["resolvedBy"] = actor
        payload["_request"] = request
        event, created = _record_event(
            registry,
            event_id=event_id,
            kind=kind,
            payload=payload,
            scope=entry["entryId"],
        )
        if kind == "approval-requested" and created and action:
            delivery_id = _sha256(_canonical({
                "entryId": entry["entryId"],
                "eventId": event_id,
                "kind": "approval-request",
            }))
            registry["outbox"].append({
                "deliveryId": delivery_id,
                "entryId": entry["entryId"],
                "eventId": event_id,
                "kind": "approval-request",
                "status": "pending",
                "owner": entry.get("owner"),
                "action": action,
                "purpose": purpose,
                "targetSha256": current_target,
                "createdAt": _timestamp(),
                "acknowledgedAt": None,
                "acknowledgedBy": None,
            })
        if kind == "executor-completed" and created:
            stage_name = action.get("stage") if action else None
            stage_state = (snapshot["status"].get("stages") or {}).get(stage_name, {})
            current_actions = _derive_actions(registry, entry, snapshot)
            current_action = next(
                (item for item in current_actions if item["actionId"] == action_id),
                None,
            )
            evidence_is_current = bool(
                current_action
                and evidence_sha256
                and any(item["sha256"] == evidence_sha256 for item in current_action["evidence"])
            )
            stage_complete = stage_state.get("status") in {"passed", "failed", "blocked"}
            if stage_complete or evidence_is_current:
                event["consumedAt"] = _timestamp()
                current_claim = entry.get("claim")
                if current_claim and (
                    current_claim.get("status") in {"active", "expired-unknown"}
                    and current_claim.get("actionId") == action_id
                    and current_claim.get("targetSha256") == target_sha256
                ):
                    claimed_action = current_claim.get("action") or action
                    if _authoritative_claim_completion(
                        current_claim,
                        claimed_action,
                        snapshot,
                        action_id=action_id,
                        target_sha256=target_sha256,
                        evidence_sha256=evidence_sha256,
                    ):
                        current_claim["status"] = "completed"
                        current_claim["outcome"] = "authoritative-completion-observed"
                        current_claim["completedAt"] = _timestamp()
            entry.setdefault("events", []).append(event_id)
        result = None
        if kind == "shared-dependency-completed":
            # Re-evaluate every registered consumer in this exact purpose and target scope.
            for consumer in registry["solutions"].values():
                if not any(
                    requirement["key"] == action_id and requirement["purpose"] == purpose
                    for requirements in consumer.get("requiredSharedDependencies", {}).values()
                    for requirement in requirements
                ):
                    continue
                consumer_path = Path(consumer["solution"])
                with using_run(consumer_path, consumer["runId"]):
                    consumer_snapshot = _workflow_snapshot(consumer_path)
                if consumer_snapshot["target"]["sha256"] != current_target:
                    continue
                _reconcile_locked(registry, consumer, consumer_snapshot)
        else:
            result = _reconcile_locked(registry, entry, snapshot)
        _write_registry(registry_file, registry)
        return {
            "eventId": event_id,
            "kind": kind,
            "created": created,
            "consumed": bool(event.get("consumedAt")),
            "targetSha256": current_target,
            "evidenceSha256": evidence_sha256,
            "reconciliation": result,
            "dispatchMode": "shadow",
            "approvalGranted": False,
        }


def acknowledge_outbox(
    solution: str | Path,
    *,
    delivery_id: str,
    actor: str,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    if not actor.strip():
        raise ValueError("outbox acknowledgement requires an actor")
    registry_file = _safe_registry(registry_path)
    with _registry_lock(registry_file):
        registry = _read_registry(registry_file)
        snapshot = _workflow_snapshot(solution)
        entry = _load_entry(registry, snapshot)
        item = next(
            (
                current for current in registry["outbox"]
                if current.get("deliveryId") == delivery_id
                and current.get("entryId") == entry["entryId"]
            ),
            None,
        )
        if not item:
            raise ValueError("outbox delivery ID does not belong to this selected workflow")
        if item["status"] == "pending":
            item["status"] = "acknowledged"
            item["acknowledgedAt"] = _timestamp()
            item["acknowledgedBy"] = actor.strip()
            _append_system_event(
                registry,
                f"outbox-ack:{delivery_id}",
                "outbox-delivery-acknowledged",
                {
                    "entryId": entry["entryId"],
                    "deliveryId": delivery_id,
                    "actor": actor.strip(),
                    "meaning": "delivery acknowledgement only; not user approval",
                },
            )
        _write_registry(registry_file, registry)
        return {
            "deliveryId": delivery_id,
            "status": item["status"],
            "acknowledgedBy": item.get("acknowledgedBy"),
            "approvalGranted": False,
        }
