from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from solution_manager.core.artifacts import list_runs, reports_base

BUDGET_SCHEMA_VERSION = "1.0.0"
DEFAULT_POLICY = {
    "activeExecutionSeconds": 120 * 60,
    "ruleRevisions": 3,
    "ruleActiveSeconds": 10 * 60,
    "conversionPasses": 3,
    "packageBuilds": 3,
    "providerHttpAttempts": 500,
    "ingestionSubmissionsPerApproval": 1,
}
CAMPAIGN_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
SHA256_PATTERN = re.compile(r"[a-f0-9]{64}\Z")
_ZERO_HASH = "0" * 64
_DIMENSIONS = {
    "conversionPass": "conversionPasses",
    "packageBuild": "packageBuilds",
    "providerHttpAttempt": "providerHttpAttempts",
    "ruleRevision": "ruleRevisions",
    "ingestionSubmission": "ingestionSubmissionsPerApproval",
    "alertObservationPoll": None,
    "workflowDiscovery": None,
    "workflowValidation": None,
    "workflowRefresh": None,
}
_LEGACY_KEYS = {
    "activeExecutionSeconds",
    "conversionPasses",
    "packageBuilds",
    "providerHttpAttempts",
    "ingestionSubmissions",
    "ruleRevisions",
    "ruleActiveSeconds",
}


class BudgetError(RuntimeError):
    """Base exception for campaign budget checks and receipt failures."""


class BudgetExhausted(BudgetError):
    """The requested work would exceed a campaign budget ceiling."""


class BudgetUnknown(BudgetError):
    """Historical use or an interrupted operation must be reconciled first."""


class BudgetReceiptError(BudgetError):
    """A budget receipt, campaign binding, or hash chain is invalid."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")


def _safe_campaign_id(campaign_id: str) -> str:
    if not isinstance(campaign_id, str) or not CAMPAIGN_ID_PATTERN.fullmatch(campaign_id):
        raise ValueError("campaign ID must be a safe 1-64 character directory name")
    return campaign_id


def default_campaign_id(solution: str | Path) -> str:
    """Derive a stable per-solution identity; changing inventory never auto-resets it."""
    identity = str(Path(solution).expanduser().resolve())
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
    return f"solution-{digest}"


def _campaign_directory(
    solution: str | Path,
    campaign_id: str,
    *,
    create_run_id: str | None = None,
) -> Path:
    base = reports_base(solution)
    campaign_id = _safe_campaign_id(campaign_id)
    runs = list_runs(solution)
    legacy_matches = [
        base / run_id / "campaigns" / campaign_id
        for run_id in runs
        if (base / run_id / "campaigns" / campaign_id / "budget.json").exists()
    ]
    campaign_root = base.parent / f"{base.name}-campaigns"
    canonical = campaign_root / campaign_id
    matches = legacy_matches + (
        [canonical] if (canonical / "budget.json").exists() else []
    )
    if len(matches) > 1:
        raise BudgetReceiptError(
            "campaign ID has multiple competing budget files; reconcile them before continuing"
        )
    if matches:
        directory = matches[0]
    elif create_run_id is not None:
        if create_run_id not in runs:
            raise BudgetReceiptError("campaign storage run is not an initialized workflow run")
        directory = canonical
    else:
        raise BudgetReceiptError(f"campaign budget does not exist: {campaign_id}")
    if (
        directory.parent.is_symlink()
        or directory.is_symlink()
        or campaign_root.is_symlink()
    ):
        raise BudgetReceiptError("symlink campaign directories are not supported")
    resolved_base = base.parent.resolve()
    resolved_directory = directory.resolve()
    if not resolved_directory.is_relative_to(resolved_base):
        raise BudgetReceiptError("campaign path escapes the solution migration Logs directory")
    return directory


def _budget_path(
    solution: str | Path,
    campaign_id: str,
    *,
    create_run_id: str | None = None,
) -> Path:
    return _campaign_directory(
        solution, campaign_id, create_run_id=create_run_id,
    ) / "budget.json"


def _atomic_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or path.is_symlink():
        raise BudgetReceiptError("symlink budget paths are not supported")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".budget.", suffix=".tmp",
            dir=path.parent, delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write((json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
        if os.name != "nt":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def _campaign_lock(
    solution: str | Path,
    campaign_id: str,
    *,
    create_run_id: str | None = None,
) -> Iterator[Path]:
    directory = _campaign_directory(
        solution, campaign_id, create_run_id=create_run_id,
    )
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / ".budget.lock"
    if lock_path.is_symlink():
        raise BudgetReceiptError("symlink budget lock is not supported")
    with lock_path.open("a+b") as handle:
        try:
            import fcntl
        except ImportError:
            import msvcrt
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            unlock = lambda: msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            unlock = lambda: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        try:
            yield _budget_path(solution, campaign_id, create_run_id=create_run_id)
        finally:
            unlock()


def _append_receipt(state: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
    receipts = state["receipts"]
    previous = receipts[-1]["sha256"] if receipts else _ZERO_HASH
    body = {
        "sequence": len(receipts) + 1,
        "previousSha256": previous,
        "createdAt": _now(),
        **fields,
    }
    body["detailsSha256"] = hashlib.sha256(_canonical(fields)).hexdigest()
    body["sha256"] = hashlib.sha256(_canonical(body)).hexdigest()
    receipts.append(body)
    return body


def _validate_state(
    state: Any,
    *,
    campaign_id: str | None = None,
    solution: str | Path | None = None,
    inventory_sha256: str | None = None,
) -> dict[str, Any]:
    if not isinstance(state, dict) or state.get("schemaVersion") != BUDGET_SCHEMA_VERSION:
        raise BudgetReceiptError("unsupported or malformed campaign budget schema")
    if (
        not isinstance(state.get("campaignId"), str)
        or not CAMPAIGN_ID_PATTERN.fullmatch(state["campaignId"])
        or not isinstance(state.get("solutionPath"), str)
        or not isinstance(state.get("createdAt"), str)
    ):
        raise BudgetReceiptError("campaign identity or creation timestamp is malformed")
    if (
        not isinstance(state.get("campaignRunId"), str)
        or not CAMPAIGN_ID_PATTERN.fullmatch(state["campaignRunId"])
    ):
        raise BudgetReceiptError("campaign storage run identity is malformed")
    if campaign_id is not None and state.get("campaignId") != campaign_id:
        raise BudgetReceiptError("campaign ID does not match the selected budget file")
    if solution is not None and state.get("solutionPath") != str(Path(solution).expanduser().resolve()):
        raise BudgetReceiptError("campaign is bound to a different solution path")
    if inventory_sha256 is not None and state.get("inventorySha256") != inventory_sha256:
        raise BudgetReceiptError("campaign is bound to a different frozen source inventory")
    if not SHA256_PATTERN.fullmatch(str(state.get("inventorySha256", ""))):
        raise BudgetReceiptError("campaign inventory SHA-256 is malformed")
    policy = state.get("policy")
    if (
        not isinstance(policy, dict)
        or set(policy) != set(DEFAULT_POLICY)
        or any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < 0
            for value in policy.values()
        )
    ):
        raise BudgetReceiptError("campaign policy is malformed")
    for dimension in set(DEFAULT_POLICY) - {"activeExecutionSeconds", "ruleActiveSeconds"}:
        if not float(policy[dimension]).is_integer():
            raise BudgetReceiptError(f"attempt ceiling {dimension} must be an integer")
    if not isinstance(state.get("receipts"), list):
        raise BudgetReceiptError("campaign receipts must be an array")
    previous = _ZERO_HASH
    starts: dict[str, dict[str, Any]] = {}
    finishes: set[str] = set()
    known_events = {
        "runLinked", "operationStarted", "operationFinished",
        "operationReconciled", "policyExtended", "observationDeadlineSet",
        "legacyUsageReconciled",
    }
    for sequence, receipt in enumerate(state["receipts"], 1):
        if not isinstance(receipt, dict):
            raise BudgetReceiptError("campaign receipt must be an object")
        if receipt.get("eventType") not in known_events:
            raise BudgetReceiptError(f"unsupported campaign receipt at sequence {sequence}")
        body = {key: value for key, value in receipt.items() if key != "sha256"}
        if (
            receipt.get("sequence") != sequence
            or receipt.get("previousSha256") != previous
            or receipt.get("detailsSha256")
            != hashlib.sha256(_canonical({
                key: value for key, value in body.items()
                if key not in {"sequence", "previousSha256", "createdAt", "detailsSha256"}
            })).hexdigest()
            or receipt.get("sha256") != hashlib.sha256(_canonical(body)).hexdigest()
        ):
            raise BudgetReceiptError(f"campaign receipt hash chain is invalid at sequence {sequence}")
        event_type = receipt["eventType"]
        if event_type == "runLinked":
            if not isinstance(receipt.get("runId"), str) or not receipt["runId"]:
                raise BudgetReceiptError("run-linked receipt has no run ID")
        elif event_type == "operationStarted":
            operation_id = receipt.get("operationId")
            dimension = receipt.get("dimension")
            metadata = receipt.get("metadata")
            if (
                not isinstance(operation_id, str)
                or operation_id in starts
                or dimension not in _DIMENSIONS
                or not isinstance(receipt.get("runId"), str)
                or receipt.get("active") is not True
                or not isinstance(metadata, dict)
            ):
                raise BudgetReceiptError("operation-start receipt is malformed or duplicated")
            if dimension == "ruleRevision" and (
                receipt.get("itemId") not in state.get("inventoryRuleIds", [])
                or any(
                    not isinstance(metadata.get(name), str)
                    or not SHA256_PATTERN.fullmatch(metadata[name])
                    for name in ("inputSha256", "evidenceSha256", "proposedChangeSha256")
                )
            ):
                raise BudgetReceiptError("rule revision receipt lacks frozen rule or evidence fingerprints")
            if dimension == "ingestionSubmission" and not all(
                isinstance(receipt.get(name), str) and receipt[name]
                for name in ("itemId", "approvalReference", "attemptMarker", "approvalScopeKey", "markerKey")
            ):
                raise BudgetReceiptError("ingestion receipt lacks exact attempt/approval identity")
            if dimension == "alertObservationPoll" and not (
                isinstance(receipt.get("testId"), str) and receipt["testId"]
            ):
                raise BudgetReceiptError("observation receipt has no test identity")
            starts[operation_id] = receipt
        elif event_type in {"operationFinished", "operationReconciled"}:
            operation_id = receipt.get("operationId")
            elapsed = receipt.get("elapsedSeconds")
            if (
                operation_id not in starts
                or operation_id in finishes
                or receipt.get("runId") != starts[operation_id].get("runId")
                or receipt.get("status") not in {"passed", "failed", "cancelled", "unknown"}
                or isinstance(elapsed, bool)
                or not isinstance(elapsed, (int, float))
                or not math.isfinite(elapsed)
                or elapsed < 0
            ):
                raise BudgetReceiptError("operation-finish receipt is malformed or duplicated")
            if event_type == "operationReconciled" and not all(
                isinstance(receipt.get(key), str) and receipt[key]
                for key in ("actor", "reason", "evidenceReference")
            ):
                raise BudgetReceiptError("operation reconciliation receipt lacks audit evidence")
            if "completionMetadata" in receipt and not isinstance(
                receipt["completionMetadata"], dict
            ):
                raise BudgetReceiptError("operation completion metadata is malformed")
            finishes.add(operation_id)
        elif event_type == "policyExtended":
            if (
                receipt.get("dimension") not in DEFAULT_POLICY
                or isinstance(receipt.get("newLimit"), bool)
                or not isinstance(receipt.get("newLimit"), (int, float))
                or not math.isfinite(receipt["newLimit"])
                or receipt.get("newLimit", 0) <= receipt.get("oldLimit", -1)
                or not receipt.get("actor")
                or not receipt.get("reason")
                or not receipt.get("evidenceReference")
            ):
                raise BudgetReceiptError("policy-extension receipt is malformed")
        elif event_type == "observationDeadlineSet":
            if not all(isinstance(receipt.get(key), str) and receipt[key] for key in (
                "testId", "deadlineAt", "approvalReference", "actor", "reason",
            )):
                raise BudgetReceiptError("observation deadline receipt is malformed")
        elif event_type == "legacyUsageReconciled":
            if not all(isinstance(receipt.get(key), str) and receipt[key] for key in (
                "actor", "reason", "evidenceReference", "consumedSha256",
            )):
                raise BudgetReceiptError("legacy reconciliation receipt is malformed")
        previous = receipt["sha256"]
    if any(operation_id not in state["runIds"] for operation_id in (
        event.get("runId") for event in starts.values()
    )):
        raise BudgetReceiptError("operation receipt references an unlinked workflow run")
    linked_events = [
        event["runId"] for event in state["receipts"]
        if event.get("eventType") == "runLinked"
    ]
    if len(set(linked_events)) != len(linked_events) or set(linked_events) != set(state["runIds"]):
        raise BudgetReceiptError("campaign run linkage receipts do not match the linked run list")
    legacy = state.get("legacyUsage")
    if (
        not isinstance(legacy, dict)
        or legacy.get("status") not in {"known", "unknown"}
        or not isinstance(legacy.get("baseline"), dict)
    ):
        raise BudgetReceiptError("campaign legacy usage metadata is malformed")
    if not isinstance(state.get("inventoryRuleIds"), list) or not all(
        isinstance(value, str) and value for value in state["inventoryRuleIds"]
    ) or len(set(state["inventoryRuleIds"])) != len(state["inventoryRuleIds"]):
        raise BudgetReceiptError("campaign rule inventory is malformed")
    if not isinstance(state.get("runIds"), list) or not all(
        isinstance(value, str) and value for value in state["runIds"]
    ) or len(set(state["runIds"])) != len(state["runIds"]):
        raise BudgetReceiptError("campaign linked run IDs are malformed")
    if state["campaignRunId"] not in state["runIds"]:
        raise BudgetReceiptError("campaign storage run is not linked to the campaign")
    baseline = legacy["baseline"]
    if not isinstance(baseline, dict):
        raise BudgetReceiptError("campaign legacy baseline is malformed")
    if legacy["status"] == "unknown" and baseline:
        raise BudgetReceiptError("unknown legacy usage cannot include inferred baseline counters")
    if legacy["status"] == "known" and baseline and set(baseline) != _LEGACY_KEYS:
        raise BudgetReceiptError("reconciled legacy baseline does not cover every usage dimension")
    if baseline:
        for name in ("activeExecutionSeconds", "conversionPasses", "packageBuilds",
                     "providerHttpAttempts", "ingestionSubmissions"):
            value = baseline[name]
            if (
                isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0
            ):
                raise BudgetReceiptError(f"legacy baseline {name} is invalid")
            if name != "activeExecutionSeconds" and not float(value).is_integer():
                raise BudgetReceiptError(f"legacy baseline {name} must be a whole number")
        for name in ("ruleRevisions", "ruleActiveSeconds"):
            values = baseline[name]
            if (
                not isinstance(values, dict)
                or set(values) != set(state["inventoryRuleIds"])
                or any(
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or value < 0
                    or (name == "ruleRevisions" and not float(value).is_integer())
                    for value in values.values()
                )
            ):
                raise BudgetReceiptError(f"legacy baseline {name} is invalid")
    return state


def _read_state(
    path: Path,
    *,
    campaign_id: str,
    solution: str | Path,
    inventory_sha256: str | None = None,
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise BudgetReceiptError(f"campaign budget file does not exist: {path}")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BudgetReceiptError(f"campaign budget file is unreadable: {path}: {exc}") from exc
    return _validate_state(
        state, campaign_id=campaign_id, solution=solution,
        inventory_sha256=inventory_sha256,
    )


def _write_state(path: Path, state: dict[str, Any]) -> None:
    _validate_state(
        state,
        campaign_id=state["campaignId"],
        solution=state["solutionPath"],
        inventory_sha256=state["inventorySha256"],
    )
    _atomic_json(path, state)


def _event_index(state: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    starts: dict[str, dict[str, Any]] = {}
    finishes: dict[str, dict[str, Any]] = {}
    for event in state["receipts"]:
        if event.get("eventType") == "operationStarted":
            starts[event["operationId"]] = event
        elif event.get("eventType") in {"operationFinished", "operationReconciled"}:
            finishes[event["operationId"]] = event
    return starts, finishes


def _usage(state: dict[str, Any]) -> dict[str, Any]:
    baseline = state["legacyUsage"]["baseline"]
    result: dict[str, Any] = {
        "activeExecutionSeconds": float(baseline.get("activeExecutionSeconds", 0)),
        "conversionPasses": int(baseline.get("conversionPasses", 0)),
        "packageBuilds": int(baseline.get("packageBuilds", 0)),
        "providerHttpAttempts": int(baseline.get("providerHttpAttempts", 0)),
        "ingestionSubmissions": int(baseline.get("ingestionSubmissions", 0)),
        "ruleRevisions": dict(baseline.get("ruleRevisions", {})),
        "ruleActiveSeconds": dict(baseline.get("ruleActiveSeconds", {})),
    }
    starts, finishes = _event_index(state)
    for event in state["receipts"]:
        if event.get("eventType") != "operationStarted":
            continue
        dimension = event["dimension"]
        item_id = event.get("itemId")
        if dimension == "conversionPass":
            result["conversionPasses"] += 1
        elif dimension == "packageBuild":
            result["packageBuilds"] += 1
        elif dimension == "providerHttpAttempt":
            result["providerHttpAttempts"] += 1
        elif dimension == "ingestionSubmission":
            result["ingestionSubmissions"] += 1
        elif dimension == "ruleRevision":
            result["ruleRevisions"][item_id] = result["ruleRevisions"].get(item_id, 0) + 1
        finish = finishes.get(event["operationId"])
        if finish and event.get("active") is True:
            elapsed = float(finish["elapsedSeconds"])
            result["activeExecutionSeconds"] += elapsed
            if dimension == "ruleRevision":
                result["ruleActiveSeconds"][item_id] = (
                    result["ruleActiveSeconds"].get(item_id, 0.0) + elapsed
                )
    result["pendingOperations"] = sorted(set(starts) - set(finishes))
    return result


def _read_locked(
    path: Path,
    campaign_id: str,
    solution: str | Path,
    inventory_sha256: str | None = None,
) -> dict[str, Any]:
    return _read_state(
        path, campaign_id=campaign_id, solution=solution,
        inventory_sha256=inventory_sha256,
    )


def create_or_link_campaign(
    solution: str | Path,
    campaign_id: str,
    *,
    inventory_sha256: str,
    run_id: str,
    rule_ids: list[str],
    legacy_usage_unknown: bool = False,
) -> dict[str, Any]:
    """Create the explicit campaign or link a replacement/resumed workflow run."""
    campaign_id = _safe_campaign_id(campaign_id)
    if not SHA256_PATTERN.fullmatch(inventory_sha256):
        raise ValueError("frozen inventory SHA-256 must be lowercase hexadecimal")
    if not run_id or not isinstance(run_id, str):
        raise ValueError("a workflow run ID is required to link a campaign")
    if len(set(rule_ids)) != len(rule_ids) or not all(isinstance(value, str) for value in rule_ids):
        raise ValueError("campaign rule IDs must be unique strings")
    root = Path(solution).expanduser().resolve()
    with _campaign_lock(root, campaign_id, create_run_id=run_id) as path:
        if path.exists():
            state = _read_locked(path, campaign_id, root, inventory_sha256)
            if state["inventoryRuleIds"] != sorted(rule_ids):
                raise BudgetReceiptError("campaign frozen rule IDs do not match this run")
        else:
            if any(child.name != ".budget.lock" for child in path.parent.iterdir()):
                raise BudgetReceiptError(
                    "campaign directory contains unrelated files; refusing to overwrite them"
                )
            state = {
                "schemaVersion": BUDGET_SCHEMA_VERSION,
                "campaignId": campaign_id,
                "campaignRunId": run_id,
                "solutionPath": str(root),
                "inventorySha256": inventory_sha256,
                "inventoryRuleIds": sorted(rule_ids),
                "createdAt": _now(),
                "policy": dict(DEFAULT_POLICY),
                "legacyUsage": {
                    "status": "unknown" if legacy_usage_unknown else "known",
                    "reason": (
                        "pre-existing run has unmeasured budget history"
                        if legacy_usage_unknown else None
                    ),
                    "baseline": {},
                    "reconciliation": None,
                },
                "runIds": [run_id],
                "receipts": [],
            }
            _append_receipt(state, {
                "eventType": "runLinked",
                "runId": run_id,
            })
            _write_state(path, state)
        if run_id not in state["runIds"]:
            state["runIds"].append(run_id)
            _append_receipt(state, {
                "eventType": "runLinked",
                "runId": run_id,
            })
            _write_state(path, state)
        return budget_summary(root, campaign_id, expected_inventory=inventory_sha256)


def validate_campaign_binding(
    solution: str | Path,
    campaign_id: str,
    *,
    inventory_sha256: str,
    rule_ids: list[str],
) -> bool:
    """Validate an existing campaign before workflow initialization creates run artifacts."""
    campaign_id = _safe_campaign_id(campaign_id)
    if not SHA256_PATTERN.fullmatch(inventory_sha256):
        raise ValueError("frozen inventory SHA-256 must be lowercase hexadecimal")
    if len(set(rule_ids)) != len(rule_ids) or not all(
        isinstance(value, str) for value in rule_ids
    ):
        raise ValueError("campaign rule IDs must be unique strings")
    root = Path(solution).expanduser().resolve()
    runs = list_runs(root)
    try:
        directory = _campaign_directory(
            root,
            campaign_id,
            create_run_id=runs[0] if runs else None,
        )
    except BudgetReceiptError as exc:
        if not runs and str(exc) == f"campaign budget does not exist: {campaign_id}":
            return False
        raise
    path = directory / "budget.json"
    if not path.exists():
        return False
    state = _read_state(
        path,
        campaign_id=campaign_id,
        solution=root,
        inventory_sha256=inventory_sha256,
    )
    if state["inventoryRuleIds"] != sorted(rule_ids):
        raise BudgetReceiptError("campaign frozen rule IDs do not match this run")
    return True


def _check_legacy_usage(state: dict[str, Any]) -> None:
    if state["legacyUsage"]["status"] != "known":
        raise BudgetUnknown(
            "campaign has pre-existing unmeasured usage; reconcile it with authoritative "
            "evidence before dispatching new work"
        )


def _check_pending(state: dict[str, Any]) -> None:
    usage = _usage(state)
    if usage["pendingOperations"]:
        raise BudgetUnknown(
            "campaign has an unresolved operation receipt; reconcile its outcome before new work"
        )


def _check_limit(
    state: dict[str, Any],
    dimension: str,
    item_id: str | None,
    *,
    amount: float = 1,
) -> None:
    policy = state["policy"]
    usage = _usage(state)
    if dimension == "conversionPass":
        used, limit = usage["conversionPasses"], policy["conversionPasses"]
    elif dimension == "packageBuild":
        used, limit = usage["packageBuilds"], policy["packageBuilds"]
    elif dimension == "providerHttpAttempt":
        used, limit = usage["providerHttpAttempts"], policy["providerHttpAttempts"]
    elif dimension == "ingestionSubmission":
        used, limit = 0, policy["ingestionSubmissionsPerApproval"]
    elif dimension == "ruleRevision":
        if not item_id:
            raise ValueError("rule revision receipts require a rule ID")
        used, limit = usage["ruleRevisions"].get(item_id, 0), policy["ruleRevisions"]
    elif dimension == "alertObservationPoll":
        used, limit = 0, None
    elif dimension in {"workflowDiscovery", "workflowValidation", "workflowRefresh"}:
        used, limit = 0, None
    else:
        raise ValueError(f"unsupported budget operation dimension: {dimension}")
    if limit is not None and used + amount > limit:
        raise BudgetExhausted(
            f"campaign budget exhausted for {dimension}"
            + (f" ({item_id})" if item_id else "")
            + f": {used:g} used, limit {limit:g}"
        )
    active_used = usage["activeExecutionSeconds"]
    active_limit = policy["activeExecutionSeconds"]
    if active_used >= active_limit:
        raise BudgetExhausted(
            f"campaign active execution budget exhausted: "
            f"{active_used:g} seconds used, limit {active_limit:g}"
        )
    if dimension == "ruleRevision" and item_id:
        rule_active = usage["ruleActiveSeconds"].get(item_id, 0)
        if rule_active >= policy["ruleActiveSeconds"]:
            raise BudgetExhausted(
                f"rule active execution budget exhausted for {item_id}: "
                f"{rule_active:g} seconds used, limit {policy['ruleActiveSeconds']:g}"
            )


def ensure_work_available(
    solution: str | Path,
    campaign_id: str,
    *,
    inventory_sha256: str,
) -> None:
    """Fail closed before local work when history, an operation, or active time is unresolved."""
    root = Path(solution).expanduser().resolve()
    with _campaign_lock(root, campaign_id) as path:
            state = _read_locked(path, campaign_id, root, inventory_sha256)
            _check_legacy_usage(state)
            _check_pending(state)
            usage = _usage(state)
            if usage["activeExecutionSeconds"] >= state["policy"]["activeExecutionSeconds"]:
                raise BudgetExhausted(
                    "campaign active execution budget is exhausted; no new work may start"
                )


def begin_operation(
    solution: str | Path,
    campaign_id: str,
    *,
    inventory_sha256: str,
    run_id: str,
    dimension: str,
    item_id: str | None = None,
    approval_reference: str | None = None,
    attempt_marker: str | None = None,
    test_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist an attempt before dispatch. Failed and later-reconciled attempts count."""
    if dimension not in _DIMENSIONS:
        raise ValueError(f"unsupported budget operation dimension: {dimension}")
    metadata = metadata or {}
    if not isinstance(metadata, dict):
        raise ValueError("operation metadata must be an object")
    if dimension == "ingestionSubmission":
        if not all(isinstance(value, str) and value.strip() for value in (
            item_id, approval_reference, attempt_marker,
        )):
            raise ValueError(
                "ingestion submissions require an exact pair/fixture key, fresh approval "
                "reference, and unique attempt marker"
            )
    if dimension == "ruleRevision":
        if not isinstance(item_id, str) or not item_id:
            raise ValueError("rule revisions require a frozen source rule ID")
        for name in ("inputSha256", "evidenceSha256", "proposedChangeSha256"):
            value = metadata.get(name)
            if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
                raise ValueError(
                    "rule revisions require input, evidence, and proposed-change SHA-256 fingerprints"
                )
    if dimension == "alertObservationPoll":
        if not test_id:
            raise ValueError("alert observation polls require an approved test ID")
    root = Path(solution).expanduser().resolve()
    with _campaign_lock(root, campaign_id) as path:
        state = _read_locked(path, campaign_id, root, inventory_sha256)
        if dimension == "ruleRevision" and item_id not in state["inventoryRuleIds"]:
            raise BudgetReceiptError("rule revision is outside the frozen campaign inventory")
        _check_legacy_usage(state)
        _check_pending(state)
        _check_limit(state, dimension, item_id)
        if dimension == "ingestionSubmission":
            approval_scope_key = hashlib.sha256(_canonical({
                "itemId": item_id,
                "approvalReference": approval_reference,
            })).hexdigest()
            marker_key = hashlib.sha256(attempt_marker.encode("utf-8")).hexdigest()
            if any(
                event.get("eventType") == "operationStarted"
                and event.get("dimension") == dimension
                and (
                    event.get("approvalScopeKey") == approval_scope_key
                    or event.get("markerKey") == marker_key
                )
                for event in state["receipts"]
            ):
                raise BudgetExhausted(
                    "this approved ingestion pair/fixture attempt already has a submission receipt"
                )
        else:
            approval_scope_key = None
            marker_key = None
        if dimension == "alertObservationPoll":
            deadline = next((
                event for event in reversed(state["receipts"])
                if event.get("eventType") == "observationDeadlineSet"
                and event.get("testId") == test_id
            ), None)
            if deadline is None:
                raise BudgetUnknown("no approved schedule-aware observation deadline is recorded")
            if datetime.now(timezone.utc) > datetime.fromisoformat(
                deadline["deadlineAt"].replace("Z", "+00:00")
            ):
                raise BudgetExhausted(
                    f"approved alert observation deadline passed for test {test_id}"
                )
            approval_reference = deadline["approvalReference"]
        operation_id = str(uuid.uuid4())
        fields = {
            "eventType": "operationStarted",
            "operationId": operation_id,
            "runId": run_id,
            "dimension": dimension,
            "itemId": item_id,
            "active": True,
            "approvalReference": approval_reference,
            "attemptMarker": attempt_marker,
            "approvalScopeKey": approval_scope_key,
            "markerKey": marker_key,
            "testId": test_id,
            "metadata": metadata,
        }
        _append_receipt(state, fields)
        _write_state(path, state)
        return {
            "operationId": operation_id,
            "campaignId": campaign_id,
            "dimension": dimension,
        }


def finish_operation(
    solution: str | Path,
    campaign_id: str,
    operation_id: str,
    *,
    status: str,
    elapsed_seconds: float,
    evidence_reference: str | None = None,
    completion_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Close a receipt with a measured duration; a retry is never implicit."""
    if status not in {"passed", "failed", "cancelled", "unknown"}:
        raise ValueError("operation status must be passed, failed, cancelled, or unknown")
    if (
        isinstance(elapsed_seconds, bool)
        or not isinstance(elapsed_seconds, (int, float))
        or not math.isfinite(elapsed_seconds)
        or elapsed_seconds < 0
    ):
        raise ValueError("measured elapsed seconds must be a finite non-negative number")
    if status == "unknown" and not (
        isinstance(evidence_reference, str) and evidence_reference.strip()
    ):
        raise ValueError("unknown operation outcomes require a receipt or telemetry reference")
    if completion_metadata is not None and not isinstance(completion_metadata, dict):
        raise ValueError("operation completion metadata must be an object")
    root = Path(solution).expanduser().resolve()
    with _campaign_lock(root, campaign_id) as path:
        state = _read_locked(path, campaign_id, root)
        starts, finishes = _event_index(state)
        if operation_id not in starts:
            raise BudgetReceiptError("operation receipt does not exist in this campaign")
        if operation_id in finishes:
            raise BudgetReceiptError("operation receipt has already been closed")
        start = starts[operation_id]
        active_before = _usage(state)["activeExecutionSeconds"]
        fields = {
            "eventType": "operationFinished",
            "operationId": operation_id,
            "runId": start["runId"],
            "status": status,
            "elapsedSeconds": float(elapsed_seconds),
            "evidenceReference": evidence_reference,
            "completionMetadata": completion_metadata or {},
        }
        if start.get("active") is True:
            overrun = max(
                0.0,
                active_before + float(elapsed_seconds) - state["policy"]["activeExecutionSeconds"],
            )
            if overrun:
                fields["overrunSeconds"] = overrun
        _append_receipt(state, fields)
        _write_state(path, state)
        return budget_summary(root, campaign_id)


@contextmanager
def measured_operation(
    solution: str | Path,
    campaign_id: str,
    *,
    inventory_sha256: str,
    run_id: str,
    dimension: str,
    item_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    completion_metadata: dict[str, Any] | None = None,
) -> Iterator[str]:
    """Measure synchronous toolkit work with a durable start and terminal receipt."""
    import time

    receipt = begin_operation(
        solution, campaign_id,
        inventory_sha256=inventory_sha256,
        run_id=run_id,
        dimension=dimension,
        item_id=item_id,
        metadata=metadata,
    )
    started = time.monotonic()
    try:
        yield receipt["operationId"]
    except BaseException as exc:
        status = "cancelled" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed"
        finish_operation(
            solution, campaign_id, receipt["operationId"],
            status=status, elapsed_seconds=max(0.0, time.monotonic() - started),
            completion_metadata=completion_metadata,
        )
        raise
    else:
        finish_operation(
            solution, campaign_id, receipt["operationId"],
            status="passed", elapsed_seconds=max(0.0, time.monotonic() - started),
            completion_metadata=completion_metadata,
        )


def reconcile_pending_operation(
    solution: str | Path,
    campaign_id: str,
    operation_id: str,
    *,
    status: str,
    elapsed_seconds: float,
    actor: str,
    reason: str,
    evidence_reference: str,
) -> dict[str, Any]:
    if status not in {"passed", "failed", "cancelled", "unknown"}:
        raise ValueError("reconciled status must be passed, failed, cancelled, or unknown")
    if (
        isinstance(elapsed_seconds, bool)
        or not isinstance(elapsed_seconds, (int, float))
        or not math.isfinite(elapsed_seconds)
        or elapsed_seconds < 0
    ):
        raise ValueError("reconciled elapsed seconds must be finite and non-negative")
    if not all(isinstance(value, str) and value.strip() for value in (
        actor, reason, evidence_reference,
    )):
        raise ValueError("reconciliation requires actor, reason, and evidence reference")
    root = Path(solution).expanduser().resolve()
    with _campaign_lock(root, campaign_id) as path:
        state = _read_locked(path, campaign_id, root)
        starts, finishes = _event_index(state)
        if operation_id not in starts or operation_id in finishes:
            raise BudgetReceiptError("only an unresolved operation receipt can be reconciled")
        _append_receipt(state, {
            "eventType": "operationReconciled",
            "operationId": operation_id,
            "runId": starts[operation_id]["runId"],
            "status": status,
            "elapsedSeconds": float(elapsed_seconds),
            "actor": actor,
            "reason": reason,
            "evidenceReference": evidence_reference,
        })
        _write_state(path, state)
    return budget_summary(root, campaign_id)


def reconcile_legacy_usage(
    solution: str | Path,
    campaign_id: str,
    *,
    consumed: dict[str, Any],
    actor: str,
    reason: str,
    evidence_reference: str,
) -> dict[str, Any]:
    """Record an owner-reviewed usage baseline; this code never reconstructs history."""
    if set(consumed) != _LEGACY_KEYS:
        raise ValueError("legacy reconciliation must provide every usage dimension")
    if not all(isinstance(value, str) and value.strip() for value in (
        actor, reason, evidence_reference,
    )):
        raise ValueError("legacy reconciliation requires actor, reason, and evidence reference")
    root = Path(solution).expanduser().resolve()
    with _campaign_lock(root, campaign_id) as path:
        state = _read_locked(path, campaign_id, root)
        if state["legacyUsage"]["status"] != "unknown":
            raise BudgetReceiptError("legacy usage has already been reconciled")
        for name in ("activeExecutionSeconds", "conversionPasses", "packageBuilds",
                     "providerHttpAttempts", "ingestionSubmissions"):
            value = consumed[name]
            if (
                isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0
            ):
                raise ValueError(f"legacy usage {name} must be a measured non-negative number")
            if name != "activeExecutionSeconds" and not float(value).is_integer():
                raise ValueError(f"legacy usage {name} must be a whole-number attempt count")
        for name in ("ruleRevisions", "ruleActiveSeconds"):
            values = consumed[name]
            if not isinstance(values, dict) or set(values) != set(state["inventoryRuleIds"]):
                raise ValueError(f"legacy usage {name} must cover the exact frozen rule inventory")
            for value in values.values():
                if (
                    isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0
                ):
                    raise ValueError(f"legacy usage {name} contains an invalid value")
        baseline = json.loads(json.dumps(consumed))
        state["legacyUsage"] = {
            "status": "known",
            "reason": reason,
            "baseline": baseline,
            "reconciliation": {
                "actor": actor,
                "reason": reason,
                "evidenceReference": evidence_reference,
                "createdAt": _now(),
            },
        }
        _append_receipt(state, {
            "eventType": "legacyUsageReconciled",
            "actor": actor,
            "reason": reason,
            "evidenceReference": evidence_reference,
            "consumedSha256": hashlib.sha256(_canonical(baseline)).hexdigest(),
        })
        _write_state(path, state)
    return budget_summary(root, campaign_id)


def extend_budget(
    solution: str | Path,
    campaign_id: str,
    *,
    dimension: str,
    new_limit: int | float,
    actor: str,
    reason: str,
    evidence_reference: str,
) -> dict[str, Any]:
    if dimension not in DEFAULT_POLICY:
        raise ValueError(f"unknown budget dimension: {dimension}")
    if (
        isinstance(new_limit, bool) or not isinstance(new_limit, (int, float))
        or not math.isfinite(new_limit) or new_limit < 0
    ):
        raise ValueError("new budget limit must be a finite non-negative number")
    if dimension not in {"activeExecutionSeconds", "ruleActiveSeconds"} and not float(
        new_limit
    ).is_integer():
        raise ValueError("attempt and revision ceilings must be whole numbers")
    if not all(isinstance(value, str) and value.strip() for value in (
        actor, reason, evidence_reference,
    )):
        raise ValueError("budget extension requires actor, reason, and owner-scope reference")
    root = Path(solution).expanduser().resolve()
    with _campaign_lock(root, campaign_id) as path:
        state = _read_locked(path, campaign_id, root)
        old_limit = state["policy"][dimension]
        if new_limit <= old_limit:
            raise ValueError("budget extensions may only raise a ceiling")
        state["policy"][dimension] = new_limit
        _append_receipt(state, {
            "eventType": "policyExtended",
            "dimension": dimension,
            "oldLimit": old_limit,
            "newLimit": new_limit,
            "actor": actor,
            "reason": reason,
            "evidenceReference": evidence_reference,
        })
        _write_state(path, state)
    return budget_summary(root, campaign_id)


def set_observation_deadline(
    solution: str | Path,
    campaign_id: str,
    *,
    test_id: str,
    deadline_at: str,
    approval_reference: str,
    actor: str,
    reason: str,
) -> dict[str, Any]:
    if not all(isinstance(value, str) and value.strip() for value in (
        test_id, approval_reference, actor, reason,
    )):
        raise ValueError("observation deadline requires test, approval, actor, and reason")
    try:
        deadline = datetime.fromisoformat(deadline_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("deadline must be an ISO-8601 timestamp with a timezone") from exc
    if deadline.tzinfo is None:
        raise ValueError("deadline must include a timezone")
    root = Path(solution).expanduser().resolve()
    with _campaign_lock(root, campaign_id) as path:
        state = _read_locked(path, campaign_id, root)
        if any(
            event.get("eventType") == "observationDeadlineSet"
            and event.get("testId") == test_id
            for event in state["receipts"]
        ):
            raise BudgetReceiptError("test observation deadline is immutable once recorded")
        _append_receipt(state, {
            "eventType": "observationDeadlineSet",
            "testId": test_id,
            "deadlineAt": deadline.astimezone(timezone.utc).isoformat(),
            "approvalReference": approval_reference,
            "actor": actor,
            "reason": reason,
        })
        _write_state(path, state)
    return budget_summary(root, campaign_id)


def budget_summary(
    solution: str | Path,
    campaign_id: str,
    *,
    expected_inventory: str | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    path = _budget_path(root, campaign_id)
    state = _read_state(
        path, campaign_id=campaign_id, solution=root,
        inventory_sha256=expected_inventory,
    )
    usage = _usage(state)
    limits = state["policy"]
    remaining = {
        "activeExecutionSeconds": max(
            0.0, limits["activeExecutionSeconds"] - usage["activeExecutionSeconds"],
        ),
        "conversionPasses": max(0, limits["conversionPasses"] - usage["conversionPasses"]),
        "packageBuilds": max(0, limits["packageBuilds"] - usage["packageBuilds"]),
        "providerHttpAttempts": max(
            0, limits["providerHttpAttempts"] - usage["providerHttpAttempts"],
        ),
        "ingestionSubmissionsPerApproval": limits["ingestionSubmissionsPerApproval"],
        "ruleRevisions": {
            rule_id: max(0, limits["ruleRevisions"] - usage["ruleRevisions"].get(rule_id, 0))
            for rule_id in state["inventoryRuleIds"]
        },
        "ruleActiveSeconds": {
            rule_id: max(
                0.0,
                limits["ruleActiveSeconds"] - usage["ruleActiveSeconds"].get(rule_id, 0),
            )
            for rule_id in state["inventoryRuleIds"]
        },
    }
    exhausted = []
    for dimension, used_key, policy_key in (
        ("activeExecutionSeconds", "activeExecutionSeconds", "activeExecutionSeconds"),
        ("conversionPass", "conversionPasses", "conversionPasses"),
        ("packageBuild", "packageBuilds", "packageBuilds"),
        ("providerHttpAttempt", "providerHttpAttempts", "providerHttpAttempts"),
    ):
        if usage[used_key] >= limits[policy_key]:
            exhausted.append(dimension)
    if state["legacyUsage"]["status"] != "known":
        enforced = "blocked-unknown-history"
    else:
        enforced = "partial-workflow-and-provider-integration"
    deadlines = {
        event["testId"]: event["deadlineAt"]
        for event in state["receipts"]
        if event.get("eventType") == "observationDeadlineSet"
    }
    latest = state["receipts"][-1]["sha256"] if state["receipts"] else _ZERO_HASH
    return {
        "schemaVersion": BUDGET_SCHEMA_VERSION,
        "campaignId": state["campaignId"],
        "campaignRunId": state["campaignRunId"],
        "solutionPath": state["solutionPath"],
        "inventorySha256": state["inventorySha256"],
        "linkedRunIds": list(state["runIds"]),
        "policy": dict(limits),
        "usage": usage,
        "remaining": remaining,
        "exhaustedDimensions": exhausted,
        "legacyUsageStatus": state["legacyUsage"]["status"],
        "legacyUsageReason": state["legacyUsage"].get("reason"),
        "enforcement": enforced,
        "activeTimeCoverage": {
            "measuredOperations": [
                "YOLO local discovery",
                "YOLO full-solution conversion",
                "YOLO structural validation",
                "YOLO V3.1 package invocation",
                "explicit alert-observation receipt API calls",
            ],
            "notIntegrated": [
                "manual workflow stages and report/refresh bookkeeping",
                "provider HTTP calls, deployment, ingestion, and cleanup adapters",
            ],
            "inFlightWorkIsNotPreempted": True,
        },
        "providerReceiptIntegration": {
            "providerHttpAttempts": "not wired to provider adapters; adapters must call begin/finish_operation per actual request including retries",
            "ingestionSubmissions": "not wired to ingestion adapters; adapters must use fresh approval references and attempt markers",
            "ruleRevisions": "receipt API available; no revision/rewrite orchestration exists in the current workflow",
            "observation": "deadline API available; no polling provider is dispatched by this workflow",
        },
        "observationDeadlines": deadlines,
        "receiptCount": len(state["receipts"]),
        "receiptHeadSha256": latest,
    }


def package_history(solution: str | Path, campaign_id: str) -> list[dict[str, Any]]:
    """Return hash-validated package attempts and their terminal receipts."""
    root = Path(solution).expanduser().resolve()
    state = _read_state(
        _budget_path(root, campaign_id), campaign_id=campaign_id, solution=root,
    )
    starts, finishes = _event_index(state)
    return [
        {
            "start": start,
            "finish": finishes.get(operation_id),
        }
        for operation_id, start in starts.items()
        if start.get("dimension") == "packageBuild"
    ]
