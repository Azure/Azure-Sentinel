from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import yaml

from .artifacts import (
    artifact_path, existing_artifact_path, report_directory, resolve_artifact_reference,
    create_run, requested_run_id, solution_for_artifact, using_run, RUN_MARKER,
    conversion_scope, require_solution_conversion_scope, portable_artifact,
)
from .budget import (
    BudgetError,
    BudgetReceiptError,
    budget_summary,
    create_or_link_campaign,
    ensure_work_available,
    measured_operation,
    package_history,
    validate_campaign_binding,
)
from .authoring_contract import (
    AUTHORING_SCHEMA_VERSION,
    AuthoringContractError,
    calculate_inventory_sha256,
    seal_authoring_contract,
    validate_authoring_contract,
)
from .content_paths import content_path
from .converter import (
    BEST_EFFORT_ENTITY_REVIEW_PREFIX,
    SOURCE_ID_PATTERN,
    analytic_rule_files,
    inspect_solution,
    convert_solution,
    validate_document,
    validate_solution,
    solution_paths,
    xdr_detection_files,
)
from .target_context import build_target, write_target
from .packaging import (
    package_input_file_hashes,
    package_input_identity,
    package_solution_v3_1,
    solution_data_version,
    validate_v31_effective_version,
    validate_v31_target_version,
    version_bump_was_consumed,
)
from .packaging_selection import (
    _partial_coverage_allowed,
    verify_applied_package_selection,
)
from .source_runtime_waiver import SOURCE_PROVIDERS, missing_schema_whitelist_match
from . import workbook_workflow

STATE_FILE_NAME = "workflow-state.json"
SCHEMA_VERSION = "1.2.0"
WORKFLOW_PROFILES = ("authoring", "qualification")
STAGES = (
    "discovery",
    "conversion",
    "validation",
    "packaging",
    "deployment",
    "mockIngestion",
    "alertParity",
    "report",
)
QUALIFICATION_DEPENDENCIES = {
    "discovery": (),
    "conversion": ("discovery",),
    "validation": ("conversion",),
    "packaging": ("validation",),
    "deployment": ("packaging",),
    "mockIngestion": ("deployment",),
    "alertParity": ("mockIngestion",),
    "report": ("alertParity",),
}
AUTHORING_DEPENDENCIES = {
    "discovery": (),
    "conversion": ("discovery",),
    "validation": ("conversion",),
    "packaging": ("validation",),
    "report": ("packaging",),
}
AUTHORING_OPTIONAL_STAGES = {"deployment", "mockIngestion", "alertParity"}
TERMINAL_STATUSES = {"passed", "failed", "blocked"}
AUTHORING_CONTRACT_DIRECTORY = "authoring-contracts"
AUTHORING_LOCK_NAME = ".workflow-state.lock"
AUTHORING_CONTRACT_VERSION = "1.0.0"
_HELD_RUN_LOCKS: ContextVar[frozenset[str]] = ContextVar(
    "held_yolo_workflow_locks", default=frozenset()
)

try:
    import fcntl
except ImportError:
    fcntl = None
    import msvcrt


@contextmanager
def _run_writer_lock(run_directory: Path):
    """Serialize workflow-state and authoring-record writers; OS releases locks on exit."""
    run_directory.mkdir(parents=True, exist_ok=True)
    key = str(run_directory.resolve())
    held = _HELD_RUN_LOCKS.get()
    if key in held:
        yield
        return
    lock_path = run_directory / AUTHORING_LOCK_NAME
    with lock_path.open("a+b") as handle:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        else:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        token = _HELD_RUN_LOCKS.set(held | {key})
        try:
            yield
        finally:
            _HELD_RUN_LOCKS.reset(token)
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            else:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _atomic_json(path: Path, value: Any) -> bytes:
    content = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    _atomic_write(path, content)
    return content


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _version_action_was_consumed(
    before: str | None,
    after: str | None,
    version_bump: str,
    target_version: str | None,
) -> bool:
    if target_version is not None:
        return bool(before and after == target_version and before != after)
    return version_bump_was_consumed(before, after, version_bump)


def _paths(solution: str | Path) -> tuple[Path, Path]:
    root = Path(solution).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"solution folder does not exist: {root}")
    return root, artifact_path(root, STATE_FILE_NAME)


def _schema() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "schema" / "workflow-state.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(state: dict[str, Any]) -> None:
    errors = sorted(
        Draft202012Validator(_schema()).iter_errors(state),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid workflow state: {details}")


def _migrate_workflow_state(state: dict[str, Any]) -> dict[str, Any]:
    """Add additive packaging lifecycle fields when reading pre-1.2 workflow state."""
    packaging = state.get("packaging")
    if isinstance(packaging, dict):
        packaging.setdefault("releaseActions", [])
        packaging.setdefault("pendingReleaseAction", None)
    return state


def _write_unlocked(path: Path, state: dict[str, Any]) -> None:
    root = solution_for_artifact(path)
    destination = artifact_path(root, STATE_FILE_NAME, create_parent=True)
    if path != destination:
        raise ValueError("workflow state path does not belong to the selected run")
    state["runId"] = destination.parent.name
    state["updatedAt"] = _utc_now()
    _validate(state)
    _atomic_json(path, portable_artifact(root, state))


def _write(path: Path, state: dict[str, Any]) -> None:
    with _run_writer_lock(path.parent):
        _write_unlocked(path, state)


@contextmanager
def _state_writer_lock(solution: str | Path):
    root, path = _paths(solution)
    with _run_writer_lock(path.parent):
        yield path


def _load(solution: str | Path) -> tuple[Path, dict[str, Any]]:
    root, _ = _paths(solution)
    path = existing_artifact_path(root, STATE_FILE_NAME)
    if not path.is_file():
        raise ValueError(
            f"workflow state does not exist: {path}; run workflow-init first"
        )
    state = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(state, dict):
        raise ValueError(f"workflow state must be a JSON object: {path}")
    if state.get("schemaVersion") == "1.1.0":
        state["schemaVersion"] = SCHEMA_VERSION
        _migrate_workflow_state(state)
    elif state.get("schemaVersion") == SCHEMA_VERSION:
        _migrate_workflow_state(state)
    context = state.get("context")
    if isinstance(context, dict):
        context.setdefault("profileSelectionConfirmed", False)
    _validate(state)
    if (path.parent / RUN_MARKER).is_file() and state.get("runId") != path.parent.name:
        raise ValueError("workflow state runId does not match its run directory")
    return artifact_path(root, STATE_FILE_NAME), state


def _stage_result(name: str, *, required: bool = True) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pending" if required else "notRequired",
        "attempts": 0,
        "startedAt": None,
        "completedAt": None,
        "message": None if required else "not required for the authoring workflow",
        "artifacts": {},
        "evidence": [],
    }


def _source_inventory(solution: str | Path) -> list[dict[str, Any]]:
    root, analytic, _ = solution_paths(solution)
    files = analytic_rule_files(root)
    if not files:
        raise ValueError("YOLO requires a non-empty complete Analytic Rules inventory")
    inventory: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for path in files:
        source_bytes = path.read_bytes()
        try:
            document = yaml.safe_load(source_bytes.decode("utf-8-sig")) or {}
        except (UnicodeError, yaml.YAMLError) as exc:
            raise ValueError(f"cannot freeze source rule {path}: {exc}") from exc
        if not isinstance(document, dict):
            raise ValueError(f"source rule must be a YAML object: {path}")
        rule_id = document.get("id")
        query = document.get("query")
        if not isinstance(rule_id, str) or not re.fullmatch(SOURCE_ID_PATTERN, rule_id):
            raise ValueError(f"source rule has no valid full GUID identity: {path}")
        if rule_id.casefold() in seen_ids:
            raise ValueError(f"duplicate source rule identity in complete inventory: {rule_id}")
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"source rule has no non-empty query: {path}")
        seen_ids.add(rule_id.casefold())
        inventory.append({
            "ruleId": rule_id,
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "querySha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
            "evidenceReferences": [{
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(source_bytes).hexdigest(),
                "kind": "source",
            }],
        })
    inventory.sort(key=lambda item: item["path"])
    return inventory


def _budget_source_inventory(
    solution: str | Path,
    *,
    yolo: bool,
) -> tuple[str, list[str]]:
    root = Path(solution).expanduser().resolve()
    if yolo:
        inventory = _source_inventory(root)
        return (
            calculate_inventory_sha256(inventory),
            [rule["ruleId"] for rule in inventory],
        )
    has_rule_folder = any(
        (root / name).exists() or (root / name).is_symlink()
        for name in ("Analytic Rules", "Analytics Rules")
    )
    files = analytic_rule_files(root) if has_rule_folder else []
    rows = []
    rule_ids: set[str] = set()
    for path in files:
        content = path.read_bytes()
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
        try:
            document = yaml.safe_load(content.decode("utf-8-sig")) or {}
        except (UnicodeError, yaml.YAMLError):
            document = {}
        if (
            isinstance(document, dict)
            and isinstance(document.get("id"), str)
            and re.fullmatch(SOURCE_ID_PATTERN, document["id"])
        ):
            rule_ids.add(document["id"])
    digest = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return digest, sorted(rule_ids)


def _preflight_campaign_binding(
    solution: Path,
    campaign_id: str | None,
    *,
    yolo: bool,
    inventory: list[dict[str, Any]] | None = None,
) -> tuple[str, list[str]] | None:
    if campaign_id is None:
        return None
    if yolo:
        frozen = inventory if inventory is not None else _source_inventory(solution)
        inventory_hash = calculate_inventory_sha256(frozen)
        rule_ids = [rule["ruleId"] for rule in frozen]
    else:
        inventory_hash, rule_ids = _budget_source_inventory(solution, yolo=False)
    validate_campaign_binding(
        solution,
        campaign_id,
        inventory_sha256=inventory_hash,
        rule_ids=rule_ids,
    )
    return inventory_hash, rule_ids


def _initial_rule_result(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "ruleId": rule["ruleId"],
        "sourceSha256": rule["sha256"],
        "status": "unprocessed",
        "conversionStatus": "unprocessed",
        "validationStatus": "notRun",
        "deploymentDisposition": "normal",
        "target": None,
        "reviewRequired": False,
        "mappingAssumptions": [],
        "findings": [],
        "qualificationStatus": "untested",
        "qualificationEvidenceReferences": [],
        "evidenceReferences": [],
    }


def _contract_core(
    root: Path,
    run_id: str,
    inventory: list[dict[str, Any]],
    *,
    revision: int,
    previous_sha256: str | None,
    results: list[dict[str, Any]] | None = None,
    environment_errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    inventory_sha256 = calculate_inventory_sha256(inventory)
    return {
        "schemaVersion": AUTHORING_SCHEMA_VERSION,
        "runId": run_id,
        "snapshot": {
            "revision": revision,
            "previousSha256": previous_sha256,
        },
        "source": {
            "identity": root.name,
            "sha256": inventory_sha256,
        },
        "inventory": {
            "complete": True,
            "sha256": inventory_sha256,
            "rules": inventory,
        },
        "results": results or [_initial_rule_result(rule) for rule in inventory],
        "environmentErrors": environment_errors or [],
        "entityValueParityPolicy": {
            "assertion": "value-preserved-in-actual-corresponding-alert",
            "comparison": "value-only",
            "entityTypeIdentifierAndCustomFieldMayDiffer": True,
            "requiredForQualification": True,
        },
    }


def _persist_contract_snapshot(
    run_directory: Path,
    state: dict[str, Any],
    core_record: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    try:
        record = seal_authoring_contract(core_record)
    except AuthoringContractError as exc:
        raise ValueError(f"authoring contract is invalid: {exc}") from exc
    content = (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    digest = hashlib.sha256(content).hexdigest()
    revision = record["snapshot"]["revision"]
    relative = f"{AUTHORING_CONTRACT_DIRECTORY}/{revision:06d}-{digest}.json"
    destination = content_path(run_directory, relative)
    if destination.exists():
        if destination.read_bytes() != content:
            raise ValueError("authoring contract snapshot hash collision or conflicting artifact")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(destination, content)
    previous_authoring = state.get("authoring") or {}
    status = previous_authoring.get("status", "active")
    state["authoring"] = {
        "schemaVersion": AUTHORING_CONTRACT_VERSION,
        "mode": "yolo",
        "status": status,
        "inventorySha256": record["inventory"]["sha256"],
        "currentContract": {
            "path": relative,
            "sha256": digest,
            "revision": revision,
        },
        "stopReason": previous_authoring.get("stopReason"),
    }
    return record, digest


def _verify_source_inventory(
    solution: Path,
    contract_document: dict[str, Any],
) -> list[dict[str, Any]]:
    current = _source_inventory(solution)
    current_hash = calculate_inventory_sha256(current)
    if current_hash != contract_document["inventory"]["sha256"]:
        raise ValueError(
            "frozen YOLO source inventory is stale or changed; preserve edits and start a new run"
        )
    return current


def _load_contract_snapshot(
    run_directory: Path,
    reference: dict[str, Any],
) -> tuple[dict[str, Any], bytes]:
    relative = reference["path"]
    snapshot_path = content_path(run_directory, relative)
    if snapshot_path.is_symlink() or not snapshot_path.is_file():
        raise ValueError("referenced authoring-contract snapshot is missing or unsafe")
    content = snapshot_path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if digest != reference["sha256"] or snapshot_path.name != (
        f"{reference['revision']:06d}-{digest}.json"
    ):
        raise ValueError("authoring-contract snapshot hash or revision is stale")
    try:
        document = json.loads(content)
        typed = validate_authoring_contract(document)
    except (UnicodeError, json.JSONDecodeError, AuthoringContractError) as exc:
        raise ValueError(f"referenced authoring-contract snapshot is invalid: {exc}") from exc
    if (
        typed.run_id != run_directory.name
        or typed.revision != reference["revision"]
        or typed.inventory_sha256 != reference.get("inventorySha256", typed.inventory_sha256)
    ):
        raise ValueError("authoring-contract snapshot identity does not match workflow state")
    return document, content


def _recover_yolo_state(
    solution: Path,
    state_path: Path,
    state: dict[str, Any],
) -> dict[str, Any]:
    """Roll forward one atomically stored contract snapshot after an interrupted state write."""
    authoring = state.get("authoring")
    if not isinstance(authoring, dict) or authoring.get("mode") != "yolo":
        return state
    run_directory = state_path.parent
    current = authoring.get("currentContract")
    if not isinstance(current, dict):
        raise ValueError("YOLO workflow state has no current authoring-contract reference")
    current_document, _ = _load_contract_snapshot(run_directory, current)
    inventory = _verify_source_inventory(solution, current_document)
    if calculate_inventory_sha256(inventory) != authoring.get("inventorySha256"):
        raise ValueError("workflow inventory hash does not match its frozen contract")

    history = content_path(run_directory, AUTHORING_CONTRACT_DIRECTORY)
    candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    if history.exists():
        if history.is_symlink() or not history.is_dir():
            raise ValueError("authoring-contract history path is unsafe")
        for snapshot_path in sorted(history.glob("*.json")):
            if snapshot_path.is_symlink():
                raise ValueError("authoring-contract history contains an unsafe symlink")
            try:
                candidate_bytes = snapshot_path.read_bytes()
                candidate_hash = hashlib.sha256(candidate_bytes).hexdigest()
                candidate = json.loads(candidate_bytes)
                typed = validate_authoring_contract(candidate)
            except (OSError, UnicodeError, json.JSONDecodeError, AuthoringContractError) as exc:
                raise ValueError(f"invalid authoring-contract history snapshot: {snapshot_path.name}") from exc
            if snapshot_path.name != f"{typed.revision:06d}-{candidate_hash}.json":
                raise ValueError(f"authoring-contract history filename is stale: {snapshot_path.name}")
            if typed.run_id != run_directory.name or typed.inventory_sha256 != authoring["inventorySha256"]:
                raise ValueError("authoring-contract history contains a conflicting run or inventory")
            if (
                typed.revision == current["revision"] + 1
                and typed.previous_sha256 == current["sha256"]
            ):
                candidates.append((candidate, {
                    "path": snapshot_path.relative_to(run_directory).as_posix(),
                    "sha256": candidate_hash,
                    "revision": typed.revision,
                }))
    if len(candidates) > 1:
        raise ValueError("multiple authoring-contract recovery successors conflict")
    if not candidates:
        return state

    recovered, reference = candidates[0]
    authoring["currentContract"] = reference
    coverage = recovered["coverage"]
    if coverage["stopThresholdReached"] and authoring["status"] == "active":
        authoring["status"] = "stopped"
        authoring["stopReason"] = (
            f"Durable rule-error threshold reached: {coverage['E']}/{coverage['N']} "
            "(100*E > 50*N)."
        )
        state["workflowStatus"] = "blocked"
    _write_unlocked(state_path, state)
    return state


def _reference_for_file(root: Path, path: Path, kind: str) -> dict[str, str]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "kind": kind,
    }


def _runtime_observations(
    root: Path,
    run_directory: Path,
    inventory: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], bool]:
    """Consume existing provider reports only; never invent provider or query outcomes."""
    _, _, output = solution_paths(root)
    output_prefix = output.relative_to(root).as_posix() + "/"
    result_by_id = {item["ruleId"]: item for item in results}
    detection_to_rule: dict[str, str] = {}
    expected_hashes: dict[str, dict[str, str]] = {}
    for rule in inventory:
        result = result_by_id[rule["ruleId"]]
        target = result.get("target")
        if not target:
            continue
        target_path = target["path"]
        if not target_path.startswith(output_prefix):
            continue
        detection = target_path[len(output_prefix):]
        if detection in detection_to_rule:
            raise ValueError(f"duplicate generated target path in YOLO contract: {detection}")
        detection_to_rule[detection] = rule["ruleId"]
        expected_hashes[detection] = {
            "triage-mcp": rule["querySha256"],
            "azure-monitor-sdk": rule["querySha256"],
            "log-analytics-cli": rule["querySha256"],
            "graph": target.get("querySha256") or "",
        }

    runtime_findings: dict[str, list[dict[str, Any]]] = {
        rule["ruleId"]: [] for rule in inventory
    }
    environment_errors: list[dict[str, Any]] = []
    environment_keys: set[tuple[str, str]] = set()
    all_reports_passed = bool(expected_hashes)
    source_reports = [
        ("triage-mcp", run_directory / "runtime-validation.triage-mcp.json"),
        ("azure-monitor-sdk", run_directory / "runtime-validation.azure-monitor-sdk.json"),
        ("log-analytics-cli", run_directory / "runtime-validation.log-analytics-cli.json"),
    ]
    available_source_reports = [
        (provider, path) for provider, path in source_reports if path.is_file()
    ]
    selected_reports: list[tuple[str, Path]] = []
    if available_source_reports:
        selected = available_source_reports[0]
        if selected[0] == "triage-mcp":
            try:
                candidate = json.loads(selected[1].read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"existing {selected[0]} runtime report is invalid: {exc}") from exc
            if isinstance(candidate, dict) and isinstance(candidate.get("providerFailure"), dict):
                for fallback in available_source_reports[1:]:
                    fallback_document = json.loads(
                        fallback[1].read_text(encoding="utf-8-sig")
                    )
                    proof = (
                        fallback_document.get("providerFallback")
                        if isinstance(fallback_document, dict) else None
                    ) or {}
                    if (
                        proof.get("mcpProvider") == "triage-mcp"
                        and proof.get("fallbackProvider") == fallback[0]
                        and proof.get("batchComplete") is True
                        and proof.get("scopeVerified") is True
                        and proof.get("permissionsVerified") is True
                        and proof.get("kqlError") is False
                    ):
                        selected = fallback
                        break
        selected_reports.append(selected)
    if not selected_reports:
        all_reports_passed = False
    selected_reports.append(
        ("graph", run_directory / "runtime-validation.graph.json")
    )
    for provider, report_path in selected_reports:
        if not report_path.is_file():
            all_reports_passed = False
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"existing {provider} runtime report is invalid: {exc}") from exc
        if not isinstance(report, dict) or report.get("provider") != provider:
            raise ValueError(f"existing {provider} runtime report has a mismatched provider")
        reference = _reference_for_file(root, report_path, "runtimeVerification")
        shared_failure = False
        for field in ("providerFailure",):
            failure = report.get(field)
            if isinstance(failure, dict):
                shared_failure = True
                code = str(failure.get("code") or failure.get("failureKind") or "providerFailure")
                message = str(failure.get("error") or failure.get("message") or "Provider failure recorded")
                if (provider, code) not in environment_keys:
                    environment_errors.append({
                        "code": f"{provider}:{code}",
                        "message": message,
                        "evidenceReferences": [reference],
                    })
                    environment_keys.add((provider, code))
        availability = report.get("tableAvailability")
        if isinstance(availability, dict):
            for table, item in availability.items():
                if isinstance(item, dict) and item.get("available") is False:
                    shared_failure = True
                    code = f"tableUnavailable:{table}"
                    if (provider, code) not in environment_keys:
                        environment_errors.append({
                            "code": f"{provider}:{code}",
                            "message": str(item.get("error") or f"Provider report marks {table} unavailable"),
                            "evidenceReferences": [reference],
                        })
                        environment_keys.add((provider, code))
        entries = report.get("results")
        if not isinstance(entries, list):
            raise ValueError(f"existing {provider} runtime report has no results list")
        names: set[str] = set()
        waived_source_failures: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"existing {provider} runtime report contains a malformed result")
            detection = str(entry.get("detection") or "").replace("\\", "/")
            if detection in names:
                raise ValueError(f"existing {provider} runtime report duplicates {detection}")
            names.add(detection)
            rule_id = detection_to_rule.get(detection)
            if rule_id is None:
                raise ValueError(f"existing {provider} runtime report contains unknown detection {detection}")
            expected = expected_hashes[detection][provider]
            query_hash = entry.get("querySha256")
            if not expected or query_hash != expected:
                raise ValueError(
                    f"stale {provider} query hash for {detection}; refresh current results before continuing"
                )
            status = str(entry.get("status") or "").lower()
            if status == "passed":
                continue
            all_reports_passed = False
            if status == "not-run":
                continue
            if status not in {"failed", "blocked"}:
                raise ValueError(f"invalid {provider} result status {status!r} for {detection}")
            if status == "blocked" and shared_failure:
                continue
            source_whitelist_match = None
            if (
                status == "failed"
                and provider in SOURCE_PROVIDERS
                and report.get("querySurface") in (
                    None,
                    SOURCE_PROVIDERS[provider],
                )
                and not report.get("providerFallback")
                and report.get("familyComplete") is not False
                and not shared_failure
            ):
                source_whitelist_match = missing_schema_whitelist_match(
                    entry,
                    provider=provider,
                    expected_query_sha256=expected,
                )
            if source_whitelist_match:
                waived_source_failures.append(
                    (rule_id, entry, source_whitelist_match)
                )
                continue
            message = str(entry.get("error") or f"{provider} reported {status}")
            runtime_findings[rule_id].append({
                "findingId": f"runtime-{provider}-{len(runtime_findings[rule_id]) + 1}",
                "kind": "error",
                "message": message,
                "unresolved": True,
                "evidenceReferences": [reference],
            })
        if names != set(detection_to_rule):
            all_reports_passed = False
        if report.get("familyComplete") is False:
            all_reports_passed = False
        family_is_complete = (
            names == set(detection_to_rule)
            and report.get("familyComplete") is not False
            and not shared_failure
            and not report.get("providerFallback")
            and report.get("querySurface")
            in (None, SOURCE_PROVIDERS.get(provider))
        )
        for rule_id, entry, match in waived_source_failures:
            if family_is_complete:
                finding_id = (
                    f"runtime-whitelist-{provider}-"
                    f"{len(runtime_findings[rule_id]) + 1}"
                )
                runtime_findings[rule_id].append({
                    "findingId": finding_id,
                    "kind": "error",
                    "message": (
                        f"Source query is source-waived for {match['table']}: "
                        f"{match['reason']} Raw provider status remains "
                        f"{entry.get('status')!r}: {entry.get('error')!s}"
                    ),
                    "unresolved": False,
                    "evidenceReferences": [reference],
                })
            else:
                runtime_findings[rule_id].append({
                    "findingId": (
                        f"runtime-{provider}-"
                        f"{len(runtime_findings[rule_id]) + 1}"
                    ),
                    "kind": "error",
                    "message": str(
                        entry.get("error")
                        or f"{provider} reported {entry.get('status')}"
                    ),
                    "unresolved": True,
                    "evidenceReferences": [reference],
                })
    if not expected_hashes:
        all_reports_passed = False
    return runtime_findings, environment_errors, all_reports_passed


def _conversion_contract_results(
    root: Path,
    run_directory: Path,
    inventory: list[dict[str, Any]],
    conversion: dict[str, Any],
    validation: dict[str, Any],
    previous_record: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    _, analytic, output = solution_paths(root)
    scope = conversion.get("scope") or {}
    if (
        scope.get("kind") != "solution"
        or scope.get("sourceTotal") != len(inventory)
        or scope.get("selectedTotal") != len(inventory)
        or len(conversion.get("results") or []) != len(inventory)
    ):
        raise ValueError("conversion results do not cover the frozen full source inventory")
    conversion_by_path: dict[str, dict[str, Any]] = {}
    for item in conversion["results"]:
        source_path = str(item.get("sourceRelativePath") or "").replace("\\", "/")
        if source_path in conversion_by_path:
            raise ValueError(f"conversion results duplicate source path: {source_path}")
        conversion_by_path[source_path] = item
    expected_sources = {rule["path"] for rule in inventory}
    if set(conversion_by_path) != expected_sources:
        raise ValueError(
            "conversion result paths do not match the frozen inventory "
            f"(missing={sorted(expected_sources - set(conversion_by_path))}, "
            f"extra={sorted(set(conversion_by_path) - expected_sources)})"
        )

    validation_by_path: dict[str, dict[str, Any]] = {}
    for item in validation.get("results") or []:
        try:
            target_path = Path(item["file"]).expanduser().resolve()
            relative = target_path.relative_to(root).as_posix()
        except (KeyError, OSError, ValueError) as exc:
            raise ValueError("structural validation returned an invalid target path") from exc
        if relative in validation_by_path:
            raise ValueError(f"structural validation duplicates target path: {relative}")
        validation_by_path[relative] = item

    manifest_path = run_directory / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("full conversion did not persist its current manifest")
    manifest_reference = _reference_for_file(root, manifest_path, "other")
    previous_results = {
        item["ruleId"]: item for item in previous_record.get("results", [])
    }
    results: list[dict[str, Any]] = []
    output_source_prefix = output.relative_to(root).as_posix() + "/"
    analytic_prefix = analytic.relative_to(root).as_posix() + "/"
    for rule in inventory:
        source_path = rule["path"]
        prior = previous_results.get(rule["ruleId"], {})
        item = conversion_by_path[source_path]
        output_path = str(item.get("outputRelativePath") or "").replace("\\", "/")
        source_suffix = source_path[len(analytic_prefix):] if source_path.startswith(analytic_prefix) else None
        expected_output = output_source_prefix + source_suffix if source_suffix is not None else None
        if not expected_output or output_path != expected_output:
            raise ValueError(
                f"conversion output path conflicts with source inventory for {rule['ruleId']}"
            )
        conversion_status = item.get("status")
        if conversion_status not in {"converted", "needsReview", "conflict", "excluded"}:
            raise ValueError(f"unsupported conversion result for {rule['ruleId']}: {conversion_status!r}")
        error_messages = [str(value) for value in item.get("errors") or [] if str(value).strip()]
        review_messages = [
            str(value) for value in item.get("reviewReasons") or [] if str(value).strip()
        ]
        warning_messages = [
            str(value) for value in item.get("warnings") or [] if str(value).strip()
        ]
        mapping_assumptions = list(prior.get("mappingAssumptions") or [])
        mapping_assumptions.extend(
            reason for reason in review_messages
            if reason.startswith(BEST_EFFORT_ENTITY_REVIEW_PREFIX)
            and reason not in mapping_assumptions
        )
        if conversion_status == "needsReview" and not error_messages:
            error_messages.extend(review_messages or ["Conversion is blocked pending technical review"])
        elif conversion_status == "conflict" and not error_messages:
            error_messages.append("Conversion reported an artifact or identity conflict")
        elif conversion_status == "excluded":
            error_messages.append("Source rule was excluded; full-solution scope is not complete")

        target_path = content_path(root, output_path)
        target: dict[str, Any] | None = None
        structural = validation_by_path.get(output_path)
        target_document: dict[str, Any] | None = None
        if conversion_status in {"converted", "needsReview"} and target_path.is_file():
            target_bytes = target_path.read_bytes()
            target_digest = hashlib.sha256(target_bytes).hexdigest()
            previous_target = prior.get("target")
            if previous_target and previous_target.get("sha256") != target_digest:
                raise ValueError(
                    f"generated target changed since its prior YOLO result: {output_path}; "
                    "preserve the edit and reconcile in a new run"
                )
            try:
                target_document = yaml.safe_load(target_bytes.decode("utf-8-sig")) or {}
            except (UnicodeError, yaml.YAMLError) as exc:
                error_messages.append(f"generated target YAML is invalid: {exc}")
            if not isinstance(target_document, dict):
                error_messages.append("generated target must be a YAML object")
                target_document = None
            provenance = (
                ((target_document.get("contentProvenance") or {}).get("source") or {})
                if target_document else {}
            )
            if (
                provenance.get("path") != source_path
                or str(provenance.get("id") or "").casefold() != rule["ruleId"].casefold()
            ):
                error_messages.append("generated target provenance conflicts with frozen source identity")
            query_text = (
                ((target_document.get("properties") or {}).get("queryCondition") or {}).get("queryText")
                if target_document else None
            )
            if not isinstance(query_text, str) or not query_text.strip():
                error_messages.append("generated target has no Advanced Hunting query")
                query_hash = None
            else:
                query_hash = hashlib.sha256(query_text.encode("utf-8")).hexdigest()
            structurally_valid = bool(structural and structural.get("valid") is True)
            target = {
                "path": output_path,
                "sha256": target_digest,
                "querySha256": query_hash,
                "structurallyValid": structurally_valid,
            }
            if not structural:
                error_messages.append("generated target has no structural validation result")
            elif not structurally_valid:
                error_messages.extend(str(value) for value in structural.get("errors") or [])
        else:
            if conversion_status in {"converted", "needsReview"}:
                error_messages.append("conversion target is missing")
            elif target_path.exists() and target_path.is_symlink():
                raise ValueError(f"conversion target path is an unsafe symlink: {output_path}")

        errors = list(dict.fromkeys(message for message in error_messages if message.strip()))
        valid_target = target is not None and target["structurallyValid"]
        status = "migrated" if conversion_status == "converted" and valid_target and not errors else "blocked"
        disposition = "normal" if status == "migrated" else "authoringBlocked"
        finding_records: list[dict[str, Any]] = []
        for index, message in enumerate(errors, 1):
            finding_records.append({
                "findingId": f"authoring-error-{index}",
                "kind": "error",
                "message": message,
                "unresolved": True,
                "evidenceReferences": [manifest_reference],
            })
        for index, message in enumerate(warning_messages, 1):
            finding_records.append({
                "findingId": f"conversion-warning-{index}",
                "kind": "warning",
                "message": message,
                "unresolved": False,
                "evidenceReferences": [manifest_reference],
            })
        if conversion_status == "converted" and item.get("reviewRequired") is True:
            for index, message in enumerate(review_messages, 1):
                finding_records.append({
                    "findingId": f"review-pending-{index}",
                    "kind": "warning",
                    "message": message,
                    "unresolved": False,
                    "evidenceReferences": [manifest_reference],
                })
        target_references = (
            [{
                "path": target["path"],
                "sha256": target["sha256"],
                "kind": "generatedTarget",
            }]
            if target else []
        )
        results.append({
            "ruleId": rule["ruleId"],
            "sourceSha256": rule["sha256"],
            "status": status,
            "conversionStatus": conversion_status,
            "validationStatus": (
                "passed" if structural and structural.get("valid") is True
                else "failed" if structural else "notRun"
            ),
            "deploymentDisposition": disposition,
            "target": target,
            "reviewRequired": bool(item.get("reviewRequired")),
            "mappingAssumptions": mapping_assumptions,
            "findings": finding_records,
            "qualificationStatus": "untested",
            "qualificationEvidenceReferences": [],
            "evidenceReferences": [manifest_reference, *target_references],
        })

    runtime_findings, environment_errors, _ = _runtime_observations(
        root, run_directory, inventory, results
    )
    for result in results:
        additional = runtime_findings[result["ruleId"]]
        if not additional:
            continue
        result["findings"].extend(additional)
        result["status"] = "blocked"
        result["deploymentDisposition"] = "authoringBlocked"
        for finding in additional:
            for reference in finding["evidenceReferences"]:
                if reference not in result["evidenceReferences"]:
                    result["evidenceReferences"].append(reference)
    return results, environment_errors


def _current_yolo_record(
    solution: Path,
    state_path: Path,
    state: dict[str, Any],
) -> tuple[dict[str, Any], bytes]:
    authoring = state.get("authoring")
    if not isinstance(authoring, dict) or authoring.get("mode") != "yolo":
        raise ValueError("this workflow was not explicitly initialized in YOLO mode")
    reference = authoring["currentContract"]
    document, content = _load_contract_snapshot(state_path.parent, reference)
    if document["inventory"]["sha256"] != authoring["inventorySha256"]:
        raise ValueError("workflow state and authoring contract inventory hashes differ")
    _verify_source_inventory(solution, document)
    _verify_target_hashes(solution, document)
    return document, content


def read_authoring_contract(solution: str | Path) -> dict[str, Any]:
    """Read only the exact content-addressed contract referenced by selected workflow state."""
    root = Path(solution).expanduser().resolve()
    path, state = _load(root)
    if not state.get("authoring"):
        raise ValueError("selected workflow has no explicit YOLO authoring contract")
    document, _ = _load_contract_snapshot(path.parent, state["authoring"]["currentContract"])
    if document["runId"] != state.get("runId"):
        raise ValueError("authoring contract is bound to a different workflow run")
    return document


def _verify_target_hashes(solution: Path, document: dict[str, Any]) -> None:
    for result in document["results"]:
        target = result.get("target")
        if target is None:
            continue
        path = content_path(solution, target["path"])
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"previously recorded target is missing or unsafe: {target['path']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != target["sha256"]:
            raise ValueError(
                f"generated target hash is stale: {target['path']}; preserve user edits and start a new run"
            )


def _validate_current_yolo_targets(
    solution: Path,
    record: dict[str, Any],
) -> None:
    root = solution.expanduser().resolve()
    inventory = record.get("inventory", {}).get("rules") or []
    results = record.get("results") or []
    results_by_id = {
        item.get("ruleId"): item
        for item in results
        if isinstance(item, dict)
    }
    inventory_by_id = {
        item.get("ruleId"): item
        for item in inventory
        if isinstance(item, dict)
    }
    if (
        not inventory_by_id
        or len(inventory_by_id) != len(inventory)
        or set(results_by_id) != set(inventory_by_id)
        or len(results_by_id) != len(results)
    ):
        raise ValueError(
            "source-waived validation requires current YOLO results for the complete source inventory"
        )

    _verify_target_hashes(root, record)
    expected_outputs: set[str] = set()
    for rule_id, rule in inventory_by_id.items():
        source_path = str(rule.get("path") or "").replace("\\", "/")
        source_parts = Path(source_path).parts
        if (
            len(source_parts) < 2
            or source_parts[0].casefold() not in {"analytic rules", "analytics rules"}
        ):
            raise ValueError(
                "source-waived validation requires safe full-inventory YOLO source paths"
            )
        expected_output = (
            Path("XDR Detections") / Path(*source_parts[1:])
        ).as_posix()
        expected_outputs.add(expected_output)
        result = results_by_id[rule_id]
        target = result.get("target")
        if not isinstance(target, dict) or target.get("path") != expected_output:
            raise ValueError(
                "source-waived validation requires a current generated target for every YOLO inventory rule"
            )
        target_path = content_path(root, expected_output)
        try:
            document = yaml.safe_load(target_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise ValueError(
                f"current YOLO target is unreadable or invalid: {expected_output}"
            ) from exc
        if not isinstance(document, dict):
            raise ValueError(f"current YOLO target is not a YAML object: {expected_output}")
        provenance = document.get("contentProvenance") or {}
        source = provenance.get("source") or {}
        conversion = provenance.get("conversion") or {}
        if (
            source.get("path") != source_path
            or source.get("id") != rule_id
            or source.get("querySha256") != rule.get("querySha256")
            or conversion.get("status") != "converted"
            or conversion.get("reviewRequired") is not False
            or conversion.get("errors") not in ([], None)
        ):
            raise ValueError(
                "source-waived validation is blocked by current YOLO target provenance, "
                "conversion errors, or review requirements"
            )
        structural_errors = validate_document(document)
        if structural_errors:
            raise ValueError(
                "source-waived validation is blocked by current YOLO target technical errors: "
                + "; ".join(structural_errors)
            )

    current_outputs = {
        path.relative_to(root).as_posix()
        for path in xdr_detection_files(root / "XDR Detections")
    }
    if current_outputs != expected_outputs:
        raise ValueError(
            "source-waived validation requires current YOLO targets to match the complete source inventory"
        )


def _refresh_yolo_record_unlocked(
    solution: Path,
    state_path: Path,
    state: dict[str, Any],
    previous_record: dict[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    _verify_target_hashes(solution, previous_record)
    inventory = previous_record["inventory"]["rules"]
    results = json.loads(json.dumps(previous_record["results"]))
    for result in results:
        result["findings"] = [
            finding for finding in result["findings"]
            if not finding["findingId"].startswith("runtime-")
        ]
        result["evidenceReferences"] = [
            reference for reference in result["evidenceReferences"]
            if reference["kind"] != "runtimeVerification"
        ]
        unresolved = any(
            finding["kind"] == "error" and finding["unresolved"]
            for finding in result["findings"]
        )
        if (
            result.get("conversionStatus") == "converted"
            and result.get("validationStatus") == "passed"
            and (result.get("target") or {}).get("structurallyValid") is True
            and not unresolved
        ):
            result["status"] = "migrated"
            result["deploymentDisposition"] = "normal"
        elif result["status"] != "suppressed":
            result["status"] = "blocked" if unresolved or result.get("target") else "unprocessed"
            result["deploymentDisposition"] = (
                "authoringBlocked" if result["status"] == "blocked" else "normal"
            )

    runtime_findings, environment_errors, _ = _runtime_observations(
        solution, state_path.parent, inventory, results
    )
    for result in results:
        findings = runtime_findings[result["ruleId"]]
        if findings:
            result["findings"].extend(findings)
            if any(
                finding.get("kind") == "error"
                and finding.get("unresolved") is True
                for finding in findings
            ):
                result["status"] = "blocked"
                result["deploymentDisposition"] = "authoringBlocked"
            for finding in findings:
                for reference in finding["evidenceReferences"]:
                    if reference not in result["evidenceReferences"]:
                        result["evidenceReferences"].append(reference)

    current_reference = state["authoring"]["currentContract"]
    if (
        results == previous_record["results"]
        and environment_errors == previous_record["environmentErrors"]
    ):
        return previous_record, False, environment_errors
    core = _contract_core(
        solution,
        state_path.parent.name,
        inventory,
        revision=current_reference["revision"] + 1,
        previous_sha256=current_reference["sha256"],
        results=results,
        environment_errors=environment_errors,
    )
    record, digest = _persist_contract_snapshot(state_path.parent, state, core)
    coverage = record["coverage"]
    authoring = state["authoring"]
    if coverage["stopThresholdReached"] and authoring["status"] == "active":
        authoring["status"] = "stopped"
        authoring["stopReason"] = (
            f"Durable rule-error threshold reached: {coverage['E']}/{coverage['N']} "
            "(100*E > 50*N)."
        )
        state["workflowStatus"] = "blocked"
    elif authoring["status"] == "stopped":
        state["workflowStatus"] = "blocked"
    _write_unlocked(state_path, state)
    return record, True, environment_errors


def refresh_yolo_authoring(solution: str | Path) -> dict[str, Any]:
    """Import current hash-bound provider reports without rerunning conversion or validation."""
    root = Path(solution).expanduser().resolve()
    with _state_writer_lock(root) as state_path:
        path, state = _load(root)
        if path != state_path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        with using_run(root, state["runId"]):
            if state["context"].get("workbookFullInventory"):
                workbook_workflow.verify_inventory(root, state)
                workbook_workflow.validate_evidence(root, state)
                return {"runId": state["runId"], "status": state["workflowStatus"],
                        "workbookSummary": workbook_workflow.summary(root, state),
                        "updated": False, "workflowStatus": state["workflowStatus"],
                        "next": _next_stage_name(state)}
            state = _recover_yolo_state(root, path, state)
            if state["authoring"]["status"] == "conflicted":
                raise ValueError("conflicted YOLO runs cannot be refreshed")
            previous, _ = _current_yolo_record(root, path, state)
            record, updated, environment_errors = _refresh_yolo_record_unlocked(
                root, path, state, previous
            )
            state = _load(root)[1]
            if state["authoring"]["status"] == "active":
                state = _complete_runtime_pending_stage(root, path, state, record)
            return {
                "runId": state["runId"],
                "status": state["authoring"]["status"],
                "authoringContract": state["authoring"]["currentContract"],
                "coverage": record["coverage"],
                "environmentErrorCount": len(environment_errors),
                "updated": updated,
                "workflowStatus": state["workflowStatus"],
                "next": _next_stage_name(state),
            }


def _mark_yolo_conflicted(
    state_path: Path,
    state: dict[str, Any],
    reason: str,
) -> None:
    state["authoring"]["status"] = "conflicted"
    state["authoring"]["stopReason"] = reason
    state["workflowStatus"] = "blocked"
    _write_unlocked(state_path, state)


def _read_full_conversion_manifest(
    root: Path,
    run_directory: Path,
    inventory: list[dict[str, Any]],
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    manifest_path = run_directory / "manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError("full-solution conversion manifest is missing or unsafe")
    content = manifest_path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if expected_sha256 and digest != expected_sha256:
        raise ValueError("conversion manifest hash changed after its workflow stage")
    try:
        document = json.loads(content)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"full-solution conversion manifest is invalid: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("full-solution conversion manifest must be a JSON object")
    scope = document.get("scope") or {}
    results = document.get("results")
    if (
        not isinstance(scope, dict)
        or scope.get("kind") != "solution"
        or scope.get("sourceTotal") != len(inventory)
        or scope.get("selectedTotal") != len(inventory)
        or not isinstance(results, list)
        or len(results) != len(inventory)
    ):
        raise ValueError("conversion manifest does not cover the frozen complete source inventory")
    return document


def _validate_clean_full_conversion_manifest(
    root: Path,
    inventory: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> set[str]:
    total = len(inventory)
    if any(
        type(manifest.get(field)) is not int or manifest[field] != expected
        for field, expected in (
            ("total", total),
            ("converted", total),
            ("excluded", 0),
            ("needsReview", 0),
            ("reviewRequired", 0),
            ("conflicts", 0),
        )
    ):
        raise ValueError(
            "conversion manifest is not a complete, technically clean full-solution result"
        )
    _, analytic, _ = solution_paths(root)
    analytic_prefix = analytic.relative_to(root).as_posix() + "/"
    inventory_by_path = {item["path"]: item for item in inventory}
    seen_sources: set[str] = set()
    expected_outputs: set[str] = set()
    for item in manifest["results"]:
        if not isinstance(item, dict):
            raise ValueError("conversion manifest contains a malformed result")
        source_reference = str(item.get("sourceRelativePath") or "").replace("\\", "/")
        suffix = (
            source_reference[len(analytic_prefix):]
            if source_reference.startswith(analytic_prefix)
            else None
        )
        expected_output = (
            (Path("XDR Detections") / Path(suffix)).as_posix()
            if suffix
            else None
        )
        output_reference = str(item.get("outputRelativePath") or "").replace("\\", "/")
        if (
            source_reference not in inventory_by_path
            or source_reference in seen_sources
            or expected_output is None
            or output_reference != expected_output
            or output_reference in expected_outputs
            or item.get("status") != "converted"
            or item.get("reviewRequired") is not False
            or item.get("errors") not in ([], None)
        ):
            raise ValueError(
                "conversion manifest has scoped, stale, incomplete, technical, "
                "or unresolved-review results"
            )
        seen_sources.add(source_reference)
        expected_outputs.add(output_reference)
    if seen_sources != set(inventory_by_path):
        raise ValueError(
            "conversion manifest does not match the current complete source inventory"
        )
    return expected_outputs


def _source_waiver_unrelated_blockers(record: dict[str, Any]) -> list[str]:
    blockers = []
    for result in record.get("results") or []:
        if (
            result.get("status") != "migrated"
            or result.get("conversionStatus") != "converted"
            or result.get("validationStatus") != "passed"
            or result.get("reviewRequired") is True
            or (result.get("target") or {}).get("structurallyValid") is not True
            or any(
                isinstance(finding, dict)
                and finding.get("unresolved") is True
                and finding.get("kind") in {"error", "review"}
                for finding in result.get("findings") or []
            )
        ):
            blockers.append(str(result.get("ruleId") or "<unknown>"))
    return blockers


def _validate_source_waiver_conversion_gates(
    solution: Path,
    state_path: Path,
    state: dict[str, Any],
) -> None:
    if any(
        state["stages"][stage].get("status") != "passed"
        for stage in ("discovery", "conversion")
    ):
        raise ValueError(
            "source-waived validation requires passed discovery and full-solution conversion stages"
        )
    conversion_stage = state["stages"]["conversion"]

    if state.get("authoring"):
        record, _ = _current_yolo_record(solution, state_path, state)
        _validate_current_yolo_targets(solution, record)
        blockers = _source_waiver_unrelated_blockers(record)
        if blockers:
            raise ValueError(
                "source-waived validation is blocked by unrelated technical or review gates: "
                + ", ".join(blockers)
            )
        return

    manifest_path = state_path.parent / "manifest.json"
    conversion_artifacts = conversion_stage.get("artifacts")
    expected_hash = (
        conversion_artifacts.get("manifestSha256")
        if isinstance(conversion_artifacts, dict)
        else None
    )
    if not manifest_path.is_file() or not isinstance(expected_hash, str):
        raise ValueError(
            "source-waived validation requires a current full-solution conversion manifest"
        )
    manifest_bytes = manifest_path.read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != expected_hash:
        raise ValueError("source-waived validation conversion manifest is stale")
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("source-waived validation conversion manifest is invalid") from exc
    scope = manifest.get("scope") if isinstance(manifest, dict) else None
    results = manifest.get("results") if isinstance(manifest, dict) else None
    total = manifest.get("total") if isinstance(manifest, dict) else None
    if (
        not isinstance(scope, dict)
        or scope.get("kind") != "solution"
        or type(total) is not int
        or total < 1
        or scope.get("sourceTotal") != total
        or scope.get("selectedTotal") != total
        or not isinstance(results, list)
        or len(results) != total
        or manifest.get("converted") != total
        or manifest.get("excluded") != 0
        or manifest.get("needsReview") != 0
        or manifest.get("reviewRequired") != 0
        or manifest.get("conflicts") != 0
    ):
        raise ValueError(
            "source-waived validation requires complete, technically clean full-solution conversion"
        )

    root = solution.expanduser().resolve()
    expected_outputs: set[str] = set()
    for item in results:
        if (
            not isinstance(item, dict)
            or item.get("status") != "converted"
            or item.get("reviewRequired") is not False
            or item.get("errors") not in ([], None)
        ):
            raise ValueError(
                "source-waived validation is blocked by unrelated conversion or review findings"
            )
        source_reference = str(item.get("sourceRelativePath") or "").replace("\\", "/")
        output_reference = str(item.get("outputRelativePath") or "").replace("\\", "/")
        parts = Path(source_reference).parts
        if (
            len(parts) < 2
            or parts[0].casefold() not in {"analytic rules", "analytics rules"}
            or output_reference != (Path("XDR Detections") / Path(*parts[1:])).as_posix()
            or output_reference in expected_outputs
        ):
            raise ValueError(
                "source-waived validation conversion manifest has incomplete or conflicting output paths"
            )
        expected_outputs.add(output_reference)
        target_path = content_path(root, output_reference)
        if not target_path.is_file() or target_path.is_symlink():
            raise ValueError(
                "source-waived validation conversion target is missing or unsafe"
            )
        try:
            document = yaml.safe_load(target_path.read_text(encoding="utf-8-sig")) or {}
        except (OSError, yaml.YAMLError) as exc:
            raise ValueError("source-waived validation conversion target is invalid") from exc
        conversion = (
            ((document.get("contentProvenance") or {}).get("conversion") or {})
            if isinstance(document, dict)
            else {}
        )
        if (
            not isinstance(conversion, dict)
            or conversion.get("status") != "converted"
            or conversion.get("reviewRequired") is not False
            or conversion.get("errors") not in ([], None)
        ):
            raise ValueError(
                "source-waived validation is blocked by current Custom Detection review or conversion findings"
            )

    output_directory = root / "XDR Detections"
    current_outputs = {
        path.relative_to(root).as_posix()
        for path in xdr_detection_files(output_directory)
    }
    if current_outputs != expected_outputs:
        raise ValueError(
            "source-waived validation requires conversion targets to match the full manifest inventory"
        )
    structural = validate_solution(root)
    if (
        structural.get("conversionScope", {}).get("kind") != "solution"
        or structural.get("total") != total
        or structural.get("invalid") != 0
        or len(structural.get("results") or []) != total
        or any(item.get("valid") is not True for item in structural.get("results") or [])
    ):
        raise ValueError(
            "source-waived validation requires current full-solution structural validation to pass"
        )


def _validate_offline_authoring_gates(
    solution: Path,
    state_path: Path,
    state: dict[str, Any],
    *,
    record: dict[str, Any] | None = None,
) -> None:
    """Require fresh full-inventory local evidence before offline Authoring completion."""
    if state.get("context", {}).get("workflowProfile") != "authoring":
        raise ValueError("offline validation completion is available only for Authoring")
    if any(
        state["stages"][stage].get("status") != "passed"
        for stage in ("discovery", "conversion")
    ):
        raise ValueError(
            "offline Authoring validation requires passed discovery and full-solution conversion"
        )
    runtime_reports = [
        report_directory(solution) / f"runtime-validation.{provider}.json"
        for provider in ("triage-mcp", "azure-monitor-sdk", "log-analytics-cli", "graph")
    ]
    present_reports = [path.name for path in runtime_reports if path.exists()]
    if present_reports:
        raise ValueError(
            "offline Authoring cannot replace existing runtime evidence; inspect current "
            "reports and preserve their results: " + ", ".join(present_reports)
        )

    root = solution.expanduser().resolve()
    if workbook_workflow.enabled(state):
        workbook_workflow.validate_evidence(root, state)
        if not workbook_workflow.has_analytic_rules(root):
            return
    inventory = _source_inventory(root)
    conversion_artifacts = state["stages"]["conversion"].get("artifacts") or {}
    expected_manifest_hash = conversion_artifacts.get("manifestSha256")
    if not isinstance(expected_manifest_hash, str) or not re.fullmatch(
        r"[a-f0-9]{64}", expected_manifest_hash
    ):
        raise ValueError(
            "offline Authoring requires a hash-bound full-solution conversion manifest; "
            "run workflow-recover-conversion-evidence for eligible legacy evidence"
        )
    manifest = _read_full_conversion_manifest(
        root,
        state_path.parent,
        inventory,
        expected_sha256=expected_manifest_hash,
    )
    manifest_outputs = _validate_clean_full_conversion_manifest(
        root,
        inventory,
        manifest,
    )
    if state.get("authoring"):
        if record is None:
            record, _ = _current_yolo_record(root, state_path, state)
        _validate_current_yolo_targets(root, record)
        blockers = _source_waiver_unrelated_blockers(record)
        if blockers:
            raise ValueError(
                "offline Authoring validation is blocked by current technical or review "
                "findings: " + ", ".join(blockers)
            )
        expected_outputs = {
            (Path("XDR Detections") / Path(*Path(rule["path"]).parts[1:])).as_posix()
            for rule in inventory
        }
    else:
        _validate_source_waiver_conversion_gates(root, state_path, state)
        analytic, output = solution_paths(root)[1:]
        analytic_prefix = analytic.relative_to(root).as_posix() + "/"
        inventory_by_path = {rule["path"]: rule for rule in inventory}
        manifest_by_source: dict[str, dict[str, Any]] = {}
        expected_outputs: set[str] = set()
        for item in manifest.get("results") or []:
            if not isinstance(item, dict):
                raise ValueError("offline Authoring conversion manifest contains a malformed result")
            source_reference = str(item.get("sourceRelativePath") or "").replace("\\", "/")
            if source_reference in manifest_by_source:
                raise ValueError("offline Authoring conversion manifest contains duplicate sources")
            source_rule = inventory_by_path.get(source_reference)
            source_suffix = (
                source_reference[len(analytic_prefix):]
                if source_reference.startswith(analytic_prefix)
                else None
            )
            expected_output = (
                (Path("XDR Detections") / Path(source_suffix)).as_posix()
                if source_suffix
                else None
            )
            if (
                source_rule is None
                or expected_output is None
                or item.get("outputRelativePath") != expected_output
                or item.get("status") != "converted"
                or item.get("reviewRequired") is not False
                or item.get("errors") not in ([], None)
            ):
                raise ValueError(
                    "offline Authoring conversion manifest is incomplete, stale, or has "
                    "unresolved technical/review findings"
                )
            manifest_by_source[source_reference] = item
            expected_outputs.add(expected_output)

            source_path = content_path(root, source_reference)
            target_path = content_path(root, expected_output)
            if (
                source_path.is_symlink()
                or target_path.is_symlink()
                or not source_path.is_file()
                or not target_path.is_file()
            ):
                raise ValueError("offline Authoring source or converted target is missing or unsafe")
            try:
                source_document = yaml.safe_load(source_path.read_text(encoding="utf-8-sig")) or {}
                target_document = yaml.safe_load(target_path.read_text(encoding="utf-8-sig")) or {}
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                raise ValueError(f"offline Authoring source or target YAML is invalid: {exc}") from exc
            provenance = (
                target_document.get("contentProvenance", {})
                if isinstance(target_document, dict)
                else {}
            )
            source_provenance = (
                provenance.get("source", {}) if isinstance(provenance, dict) else {}
            )
            conversion = (
                provenance.get("conversion", {}) if isinstance(provenance, dict) else {}
            )
            review_scope = (
                conversion.get("reviewScope", {}) if isinstance(conversion, dict) else {}
            )
            target_properties = (
                target_document.get("properties")
                if isinstance(target_document, dict)
                else None
            )
            query_condition = (
                target_properties.get("queryCondition")
                if isinstance(target_properties, dict)
                else None
            )
            target_query = (
                query_condition.get("queryText")
                if isinstance(query_condition, dict)
                else None
            )
            source_query = source_document.get("query") if isinstance(source_document, dict) else None
            if (
                not isinstance(source_document, dict)
                or not isinstance(source_provenance, dict)
                or not isinstance(conversion, dict)
                or not isinstance(review_scope, dict)
            ):
                raise ValueError(
                    f"offline Authoring conversion evidence is malformed for {source_reference}"
                )
            canonical_source_hash = hashlib.sha256(
                yaml.safe_dump(
                    source_document,
                    sort_keys=True,
                    allow_unicode=True,
                ).encode("utf-8")
            ).hexdigest()
            current_source_query_hash = (
                hashlib.sha256(source_query.encode("utf-8")).hexdigest()
                if isinstance(source_query, str)
                else None
            )
            current_target_query_hash = (
                hashlib.sha256(target_query.encode("utf-8")).hexdigest()
                if isinstance(target_query, str)
                else None
            )
            if (
                source_provenance.get("path") != source_reference
                or source_provenance.get("id") != source_document.get("id")
                or source_provenance.get("querySha256") != current_source_query_hash
                or not current_target_query_hash
                or conversion.get("status") != "converted"
                or conversion.get("reviewRequired") is not False
                or conversion.get("errors") not in ([], None)
                or review_scope.get("sourceDocumentSha256") != canonical_source_hash
                or review_scope.get("targetQuerySha256") != current_target_query_hash
            ):
                raise ValueError(
                    f"offline Authoring conversion evidence is stale or unresolved for {source_reference}"
                )
        if set(manifest_by_source) != set(inventory_by_path):
            raise ValueError(
                "offline Authoring conversion manifest does not match the current full source inventory"
            )
        current_outputs = {
            path.relative_to(root).as_posix()
            for path in xdr_detection_files(output)
        }
        if current_outputs != expected_outputs:
            raise ValueError(
                "offline Authoring converted targets do not match the complete current inventory"
            )

    if expected_outputs != manifest_outputs:
        raise ValueError(
            "offline Authoring conversion outputs do not match the bound manifest"
        )
    structural = validate_solution(root)
    if (
        structural.get("conversionScope", {}).get("kind") != "solution"
        or structural.get("total") != len(inventory)
        or structural.get("invalid") != 0
        or structural.get("valid") != len(inventory)
        or len(structural.get("results") or []) != len(inventory)
        or any(item.get("valid") is not True for item in structural.get("results") or [])
    ):
        raise ValueError(
            "offline Authoring validation requires current full-solution structural validation to pass"
        )


def recover_conversion_evidence(solution: str | Path) -> dict[str, Any]:
    """Rebind a legacy Authoring conversion manifest only after complete offline revalidation."""
    root = Path(solution).expanduser().resolve()
    with _state_writer_lock(root) as path:
        loaded_path, state = _load(root)
        if loaded_path != path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        if state.get("context", {}).get("workflowProfile") != "authoring":
            raise ValueError(
                "conversion evidence recovery is restricted to explicitly selected Authoring runs"
            )
        if any(
            state["stages"][stage].get("status") != "passed"
            for stage in ("discovery", "conversion")
        ):
            raise ValueError(
                "conversion evidence recovery requires passed discovery and conversion stages"
            )

        conversion_stage = state["stages"]["conversion"]
        artifacts = conversion_stage.get("artifacts")
        if not isinstance(artifacts, dict):
            raise ValueError("passed conversion stage has no artifact record to recover")
        manifest_reference = artifacts.get("manifest")
        if not isinstance(manifest_reference, str) or not manifest_reference.strip():
            raise ValueError(
                "conversion evidence recovery requires the existing manifest artifact reference"
            )

        manifest_path = path.parent / "manifest.json"
        if manifest_path.is_symlink() or not manifest_path.is_file():
            raise ValueError("current run conversion manifest is missing or unsafe")
        if manifest_reference != "manifest.json":
            try:
                referenced_manifest = resolve_artifact_reference(root, manifest_reference)
            except (OSError, ValueError) as exc:
                raise ValueError("conversion manifest artifact reference is invalid") from exc
            if referenced_manifest.resolve() != manifest_path.resolve():
                raise ValueError(
                    "conversion manifest artifact reference does not identify this run's manifest"
                )

        manifest_bytes = manifest_path.read_bytes()
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
        prior_sha256 = artifacts.get("manifestSha256")
        if prior_sha256 is not None and prior_sha256 != manifest_sha256:
            raise ValueError(
                "existing conversion manifest hash does not match current bytes; "
                "recovery will not replace a bound digest"
            )

        inventory = _source_inventory(root)
        canonical_inventory_sha256 = hashlib.sha256(
            json.dumps(
                inventory,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        prior_inventory_sha256 = artifacts.get("sourceInventorySha256")
        if state.get("authoring"):
            record, _ = _current_yolo_record(root, path, state)
            inventory_sha256 = record["inventory"]["sha256"]
        else:
            inventory_sha256 = canonical_inventory_sha256
        if (
            prior_inventory_sha256 is not None
            and prior_inventory_sha256 != inventory_sha256
        ):
            raise ValueError(
                "current source inventory differs from the conversion stage inventory; "
                "recovery will not rebind stale evidence"
            )

        manifest = _read_full_conversion_manifest(
            root,
            path.parent,
            inventory,
            expected_sha256=manifest_sha256,
        )
        total = len(inventory)
        _validate_clean_full_conversion_manifest(root, inventory, manifest)

        candidate_state = dict(state)
        candidate_stages = dict(state["stages"])
        candidate_conversion_stage = dict(conversion_stage)
        candidate_artifacts = dict(artifacts)
        candidate_artifacts["manifestSha256"] = manifest_sha256
        candidate_conversion_stage["artifacts"] = candidate_artifacts
        candidate_stages["conversion"] = candidate_conversion_stage
        candidate_state["stages"] = candidate_stages
        _validate_offline_authoring_gates(
            root,
            path,
            candidate_state,
        )

        if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != manifest_sha256:
            raise ValueError(
                "conversion manifest changed during evidence recovery; no digest was persisted"
            )
        current_inventory = _source_inventory(root)
        current_inventory_sha256 = hashlib.sha256(
            json.dumps(
                current_inventory,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if current_inventory_sha256 != inventory_sha256:
            if state.get("authoring"):
                current_record, _ = _current_yolo_record(root, path, state)
                current_inventory_sha256 = current_record["inventory"]["sha256"]
        if current_inventory_sha256 != inventory_sha256:
            raise ValueError(
                "source inventory changed during evidence recovery; no digest was persisted"
            )

        if prior_sha256 is not None:
            return {
                "runId": state["runId"],
                "status": "already-bound",
                "manifestSha256": manifest_sha256,
                "sourceInventorySha256": inventory_sha256,
                "sourceCount": total,
            }

        artifacts.update({
            "manifestSha256": manifest_sha256,
            "sourceInventorySha256": inventory_sha256,
            "manifestEvidenceRecovery": "offline-authoring-full-revalidation",
            "manifestEvidenceRecoveredAt": _utc_now(),
        })
        _write_unlocked(path, state)
        return {
            "runId": state["runId"],
            "status": "recovered",
            "manifestSha256": manifest_sha256,
            "sourceInventorySha256": inventory_sha256,
            "sourceCount": total,
        }


def _offline_authoring_validation_message() -> str:
    return (
        "Offline Authoring validation passed after full-inventory conversion, current "
        "structural validation, and resolved review checks. Sentinel and Advanced Hunting "
        "runtime validation was not run; this result is not runtime/XDR-qualified."
    )


def _current_runtime_status(
    solution: Path,
    profile: str,
    record: dict[str, Any],
) -> tuple[str, str | None, dict[str, Any]]:
    from .runtime import current_runtime_evidence

    evidence = current_runtime_evidence(solution)
    if (
        evidence.get("sourceWhitelist")
        and not evidence.get("sourceWaiverOnlyBlocker")
    ):
        return (
            "blocked",
            "The IdentityInfo source failure is visible as source-waived, but XDR runtime "
            "or another exact validation gate is incomplete; validation stays blocked.",
            evidence,
        )
    if evidence.get("sourceWaiverOnlyBlocker"):
        unrelated_blockers = _source_waiver_unrelated_blockers(record)
        if unrelated_blockers:
            return (
                "blocked",
                "Source waiver is recorded, but unrelated technical or review gates remain; validation stays blocked.",
                evidence,
            )
        return (
            "source-waived",
            "Validation completed with the built-in IdentityInfo source-table whitelist. "
            "The raw Sentinel query result remains failed; this run is not fully runtime-qualified.",
            evidence,
        )
    if evidence.get("passed"):
        return "passed", None, evidence
    if any(
        result["status"] != "migrated"
        for result in record["results"]
    ):
        return "blocked", "YOLO rule-level technical blockers remain; see the authoring contract.", evidence
    if (
        profile == "authoring"
        and record["environmentErrors"]
        and not evidence.get("currentQueryFailures")
    ):
        return (
            "environment-blocked",
            "Runtime validation is blocked by provider/environment evidence; no KQL/runtime query failure was relabeled.",
            evidence,
        )
    return (
        "not-run",
        "Runtime validation is not complete; exact current-query provider evidence is missing or blocked.",
        evidence,
    )


def _source_whitelist_stage_artifacts(
    runtime_evidence: dict[str, Any],
) -> dict[str, str]:
    entries = runtime_evidence.get("sourceWhitelist")
    if not isinstance(entries, list) or not entries:
        return {}
    summary = [
        {
            "detection": item.get("detection"),
            "table": item.get("table"),
            "status": item.get("status"),
            "applied": item.get("applied") is True,
            "querySha256": item.get("querySha256"),
            "reason": item.get("reason"),
            "rawStatus": (item.get("rawFailure") or {}).get("status"),
            "rawStatusCode": (item.get("rawFailure") or {}).get("statusCode"),
            "rawFailureKind": (item.get("rawFailure") or {}).get("failureKind"),
        }
        for item in entries
        if isinstance(item, dict)
    ]
    return {
        "sourceRuntimeWhitelistTable": "IdentityInfo",
        "sourceRuntimeWhitelistCount": str(len(summary)),
        "sourceRuntimeWhitelistStatus": (
            "source-waived"
            if summary and all(item["applied"] for item in summary)
            else "candidate-blocked"
        ),
        "sourceRuntimeWhitelist": json.dumps(
            summary, sort_keys=True, separators=(",", ":")
        ),
    }


def _complete_runtime_pending_stage(
    solution: Path,
    state_path: Path,
    state: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    stage = state["stages"]["validation"]
    if not (
        stage["status"] == "blocked"
        and str(stage.get("message") or "").startswith("Runtime validation is not complete")
    ):
        return state
    status, message, runtime_evidence = _current_runtime_status(
        solution, state["context"]["workflowProfile"], record
    )
    if status not in {"passed", "environment-blocked", "source-waived", "not-run"}:
        return state
    if status == "not-run":
        try:
            _validate_offline_authoring_gates(solution, state_path, state, record=record)
        except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError):
            return state
    if status == "source-waived":
        _validate_source_waiver_conversion_gates(solution, state_path, state)
        whitelist = runtime_evidence.get("sourceWhitelist") or []
        if not whitelist or any(
            item.get("table") != "IdentityInfo"
            or item.get("rawFailure", {}).get("status") != "failed"
            or item.get("applied") is not True
            for item in whitelist
        ):
            return state
    _start_workflow_stage_unlocked(solution, "validation", state_path)
    artifacts = (
        {"runtimeStatus": status}
        if status in {"environment-blocked", "source-waived"}
        else {}
    )
    if status == "not-run":
        artifacts = {
            "runtimeStatus": "not-run",
            "validationMode": "offline-authoring",
        }
    if status == "source-waived":
        artifacts.update(_source_whitelist_stage_artifacts(runtime_evidence))
        artifacts["sourceRuntimeWhitelistRawStatus"] = "failed"
    _complete_workflow_stage_unlocked(
        solution,
        "validation",
        state_path,
        status="passed",
        message=(
            _offline_authoring_validation_message()
            if status == "not-run"
            else message
        ),
        artifacts=artifacts,
        evidence=None,
    )
    return _load(solution)[1]


def run_workbook_only_authoring(solution: str | Path) -> dict[str, Any]:
    """Account workbook-only full-inventory passes without inventing rule coverage."""
    root = Path(solution).expanduser().resolve()
    with _state_writer_lock(root) as path:
        state = _load(root)[1]
        if not workbook_workflow.enabled(state) or not state["context"].get("workbookFullInventory"):
            raise ValueError("workbook-only full-inventory execution requires a new explicit YOLO run")
        workbook_workflow.verify_inventory(root, state)
        budget = state.get("budget")
        if not budget or budget.get("status") == "stopped":
            raise ValueError("workbook full-inventory execution requires an active campaign budget")
        for name, dimension, action in (
            ("discovery", "workflowDiscovery", workbook_workflow.inspect_content),
            ("conversion", "conversionPass", workbook_workflow.convert_content),
            ("validation", "workflowValidation", workbook_workflow.validate_content),
        ):
            state = _load(root)[1]
            if state["stages"][name]["status"] == "passed":
                continue
            _start_workflow_stage_unlocked(root, name, path)
            try:
                with measured_operation(root, budget["campaignId"],
                                        inventory_sha256=budget["inventorySha256"],
                                        run_id=state["runId"], dimension=dimension):
                    result = action(root)
                if name == "conversion" and result.get("workbooks", {}).get("selectedBlocked"):
                    raise ValueError("workbook conversion contains unresolved review or technical blockers")
                if (
                    name == "validation"
                    and state["context"]["workflowProfile"] == "qualification"
                    and state["context"].get("workbookQualificationAfterArm") is not True
                ):
                    _complete_workflow_stage_unlocked(root, name, path, status="blocked",
                        message="Workbook query/UI Qualification evidence is still required; no detection ingestion/parity is requested.")
                    break
                _complete_workflow_stage_unlocked(root, name, path, status="passed",
                    artifacts=({"runtimeStatus": "not-run", "validationMode":
                                "workbook-content" if state["context"]["workflowProfile"] == "qualification"
                                else "offline-authoring"}
                               if name == "validation" else {}))
            except BudgetError as exc:
                _stop_budget_run(path, _load(root)[1], name, str(exc))
                break
            except (OSError, ValueError, RuntimeError) as exc:
                _complete_workflow_stage_unlocked(root, name, path, status="failed", message=str(exc))
                break
        state = _load(root)[1]
        return {"runId": state["runId"], "status": state["workflowStatus"],
                "workbookSummary": workbook_workflow.summary(root, state),
                "next": _next_stage_name(state)}


def run_yolo_authoring(solution: str | Path) -> dict[str, Any]:
    """Run existing local discovery/conversion/validation once under the frozen YOLO contract."""
    root = Path(solution).expanduser().resolve()
    initial = _load(root)[1]
    if initial["context"].get("workbookFullInventory") is True:
        return run_workbook_only_authoring(root)
    with _state_writer_lock(root) as state_path:
        loaded_path, state = _load(root)
        if loaded_path != state_path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        run_id = state.get("runId")
        if not run_id:
            raise ValueError("YOLO authoring requires an explicitly initialized run-scoped workflow")
        with using_run(root, run_id):
            state = _recover_yolo_state(root, state_path, state)
            if not state.get("authoring") or state["authoring"]["mode"] != "yolo":
                raise ValueError("workflow was not explicitly initialized with --yolo")
            record, _ = _current_yolo_record(root, state_path, state)
            authoring = state["authoring"]
            budget = state.get("budget")
            if not isinstance(budget, dict):
                raise ValueError(
                    "YOLO workflow has no durable campaign budget; initialize or explicitly "
                    "link it with workflow-init --yolo --campaign-id"
                )
            if (
                authoring["status"] in {"stopped", "conflicted"}
                and not str(authoring.get("stopReason") or "").startswith("Campaign budget:")
            ):
                return {
                    "runId": run_id,
                    "status": authoring["status"],
                    "reason": authoring.get("stopReason"),
                    "coverage": record["coverage"],
                    "authoringContract": authoring["currentContract"],
                    "workflowStatus": state["workflowStatus"],
                    "next": _next_stage_name(state),
                    "resumed": True,
                    "workPerformed": False,
                }
            if budget.get("status") == "stopped":
                return {
                    "runId": run_id,
                    "status": "budget-exhausted",
                    "reason": budget.get("stopReason"),
                    "coverage": record["coverage"],
                    "authoringContract": authoring["currentContract"],
                    "workflowStatus": state["workflowStatus"],
                    "next": _next_stage_name(state),
                    "resumed": True,
                    "workPerformed": False,
                }
            if authoring["status"] in {"stopped", "conflicted"}:
                return {
                    "runId": run_id,
                    "status": authoring["status"],
                    "reason": authoring.get("stopReason"),
                    "coverage": record["coverage"],
                    "authoringContract": authoring["currentContract"],
                    "workflowStatus": state["workflowStatus"],
                    "next": _next_stage_name(state),
                    "resumed": True,
                    "workPerformed": False,
                }

            inventory = _verify_source_inventory(root, record)
            inventory_hash = record["inventory"]["sha256"]
            if state["context"].get("profileSelectionConfirmed") is not True:
                raise ValueError("YOLO requires explicit Authoring or Qualification profile selection")
            if state["context"]["workflowProfile"] == "qualification" and not state["context"].get("targetContextLocked"):
                raise ValueError("Qualification YOLO requires its existing locked target")

            if any(
                state["stages"][stage_name]["status"] != "passed"
                for stage_name in ("discovery", "conversion", "validation")
            ):
                try:
                    ensure_work_available(
                        root,
                        budget["campaignId"],
                        inventory_sha256=inventory_hash,
                    )
                except BudgetError as exc:
                    next_stage = next(
                        name for name in ("discovery", "conversion", "validation")
                        if state["stages"][name]["status"] != "passed"
                    )
                    _stop_budget_run(state_path, state, next_stage, str(exc))
                    return {
                        "runId": run_id,
                        "status": "budget-exhausted",
                        "reason": str(exc),
                        "coverage": record["coverage"],
                        "authoringContract": state["authoring"]["currentContract"],
                        "workflowStatus": state["workflowStatus"],
                        "next": None,
                        "resumed": True,
                        "workPerformed": False,
                    }

            discovery = state["stages"]["discovery"]
            if discovery["status"] != "passed":
                if discovery["status"] != "running":
                    _start_workflow_stage_unlocked(root, "discovery", state_path)
                discovery_dispatched = False
                try:
                    with measured_operation(
                        root,
                        budget["campaignId"],
                        inventory_sha256=inventory_hash,
                        run_id=run_id,
                        dimension="workflowDiscovery",
                    ):
                        discovery_dispatched = True
                        inspection = (
                            workbook_workflow.inspect_content(root)
                            if workbook_workflow.enabled(state) else inspect_solution(root)
                        )
                except BudgetError as exc:
                    if discovery_dispatched:
                        raise
                    current_state = _load(root)[1]
                    _stop_budget_run(state_path, current_state, "discovery", str(exc))
                    return {
                        "runId": run_id,
                        "status": "budget-exhausted",
                        "reason": str(exc),
                        "coverage": record["coverage"],
                        "authoringContract": current_state["authoring"]["currentContract"],
                        "workflowStatus": current_state["workflowStatus"],
                        "next": None,
                        "resumed": discovery["status"] == "running",
                        "workPerformed": False,
                    }
                if inspection["analyticRuleCount"] != len(inventory):
                    _mark_yolo_conflicted(
                        state_path, state,
                        "Discovery inventory count changed after YOLO scope freeze.",
                    )
                    raise ValueError("discovery inventory changed after YOLO scope freeze")
                _complete_workflow_stage_unlocked(
                    root,
                    "discovery",
                    state_path,
                    status="passed",
                    message="Complete recursive source inventory verified against frozen YOLO scope.",
                    artifacts={"sourceInventorySha256": inventory_hash},
                )
                state = _load(root)[1]

            conversion_stage = state["stages"]["conversion"]
            if conversion_stage["status"] == "passed":
                expected_manifest_hash = conversion_stage["artifacts"].get("manifestSha256")
                conversion = _read_full_conversion_manifest(
                    root, state_path.parent, inventory, expected_manifest_hash
                )
            else:
                if conversion_stage["status"] != "running":
                    _start_workflow_stage_unlocked(root, "conversion", state_path)
                conversion_dispatched = False
                try:
                    with measured_operation(
                        root,
                        budget["campaignId"],
                        inventory_sha256=inventory_hash,
                        run_id=run_id,
                        dimension="conversionPass",
                    ):
                        conversion_dispatched = True
                        if workbook_workflow.enabled(state):
                            workbook_workflow.convert_content(root)
                        else:
                            convert_solution(root)
                    _verify_source_inventory(root, record)
                    manifest = _read_full_conversion_manifest(
                        root, state_path.parent, inventory
                    )
                except BudgetError as exc:
                    if conversion_dispatched:
                        current_path, current_state = _load(root)
                        stage = current_state["stages"]["conversion"]
                        if stage["status"] == "running":
                            _complete_workflow_stage_unlocked(
                                root, "conversion", state_path, status="failed",
                                message=f"Conversion ran but its budget receipt failed: {exc}",
                            )
                        return {
                            "runId": run_id,
                            "status": "failed",
                            "reason": str(exc),
                            "coverage": record["coverage"],
                            "authoringContract": current_state["authoring"]["currentContract"],
                            "workflowStatus": current_state["workflowStatus"],
                            "next": _next_stage_name(current_state),
                            "resumed": conversion_stage["status"] == "running",
                            "workPerformed": True,
                        }
                    current_path, current_state = _load(root)
                    if current_path != state_path:
                        raise ValueError("workflow state selection changed during budget check") from exc
                    _stop_budget_run(state_path, current_state, "conversion", str(exc))
                    return {
                        "runId": run_id,
                        "status": "budget-exhausted",
                        "reason": str(exc),
                        "coverage": record["coverage"],
                        "authoringContract": current_state["authoring"]["currentContract"],
                        "workflowStatus": current_state["workflowStatus"],
                        "next": None,
                        "resumed": conversion_stage["status"] == "running",
                        "workPerformed": False,
                    }
                except (OSError, RuntimeError, ValueError, yaml.YAMLError) as exc:
                    current_path, current_state = _load(root)
                    if current_path != state_path:
                        raise ValueError("workflow state selection changed during conversion") from exc
                    stage = current_state["stages"]["conversion"]
                    if stage["status"] == "running":
                        _complete_workflow_stage_unlocked(
                            root, "conversion", state_path, status="failed",
                            message=f"Full-solution conversion did not complete: {exc}",
                        )
                    return {
                        "runId": run_id,
                        "status": "failed",
                        "reason": str(exc),
                        "coverage": record["coverage"],
                        "authoringContract": current_state["authoring"]["currentContract"],
                        "workflowStatus": current_state["workflowStatus"],
                        "next": _next_stage_name(current_state),
                        "resumed": conversion_stage["status"] == "running",
                        "workPerformed": True,
                    }
                conversion = manifest
                conversion_sha256 = hashlib.sha256(
                    (state_path.parent / "manifest.json").read_bytes()
                ).hexdigest()
                state = _load(root)[1]
                _complete_workflow_stage_unlocked(
                    root,
                    "conversion",
                    state_path,
                    status="passed",
                    message=(
                        "Existing deterministic converter completed the full frozen source inventory; "
                        "per-rule technical outcomes remain in the authoring contract."
                    ),
                    artifacts={
                        "manifest": "manifest.json",
                        "manifestSha256": conversion_sha256,
                        "sourceInventorySha256": inventory_hash,
                    },
                )
                state = _load(root)[1]

            validation_stage = state["stages"]["validation"]
            if validation_stage["status"] == "passed":
                record, _ = _current_yolo_record(root, state_path, state)
                return {
                    "runId": run_id,
                    "status": state["authoring"]["status"],
                    "coverage": record["coverage"],
                    "authoringContract": state["authoring"]["currentContract"],
                    "workflowStatus": state["workflowStatus"],
                    "next": _next_stage_name(state),
                    "resumed": True,
                    "workPerformed": False,
                }
            if (
                validation_stage["status"] == "blocked"
                and str(validation_stage.get("message") or "").startswith(
                    "Runtime validation is not complete"
                )
            ):
                refreshed = refresh_yolo_authoring(root)
                state = _load(root)[1]
                record, _ = _current_yolo_record(root, state_path, state)
                return {
                    "runId": run_id,
                    "status": state["authoring"]["status"],
                    "coverage": record["coverage"],
                    "authoringContract": state["authoring"]["currentContract"],
                    "workflowStatus": state["workflowStatus"],
                    "next": _next_stage_name(state),
                    "resumed": True,
                    "workPerformed": bool(refreshed["updated"]),
                }
            if validation_stage["status"] == "blocked":
                record, _ = _current_yolo_record(root, state_path, state)
                return {
                    "runId": run_id,
                    "status": "blocked",
                    "reason": validation_stage.get("message"),
                    "coverage": record["coverage"],
                    "authoringContract": state["authoring"]["currentContract"],
                    "workflowStatus": state["workflowStatus"],
                    "next": _next_stage_name(state),
                    "resumed": True,
                    "workPerformed": False,
                }

            _start_workflow_stage_unlocked(root, "validation", state_path)
            state = _load(root)[1]
            validation_dispatched = False
            try:
                with measured_operation(
                    root,
                    budget["campaignId"],
                    inventory_sha256=inventory_hash,
                    run_id=run_id,
                    dimension="workflowValidation",
                ):
                    validation_dispatched = True
                    validation = validate_solution(root)
            except BudgetError as exc:
                if validation_dispatched:
                    current_state = _load(root)[1]
                    _complete_workflow_stage_unlocked(
                        root,
                        "validation",
                        state_path,
                        status="failed",
                        message=f"Validation ran but its budget receipt failed: {exc}",
                    )
                    return {
                        "runId": run_id,
                        "status": "failed",
                        "reason": str(exc),
                        "coverage": record["coverage"],
                        "authoringContract": current_state["authoring"]["currentContract"],
                        "workflowStatus": current_state["workflowStatus"],
                        "next": _next_stage_name(current_state),
                        "resumed": False,
                        "workPerformed": True,
                    }
                current_state = _load(root)[1]
                _stop_budget_run(state_path, current_state, "validation", str(exc))
                return {
                    "runId": run_id,
                    "status": "budget-exhausted",
                    "reason": str(exc),
                    "coverage": record["coverage"],
                    "authoringContract": current_state["authoring"]["currentContract"],
                    "workflowStatus": current_state["workflowStatus"],
                    "next": None,
                    "resumed": False,
                    "workPerformed": False,
                }
            _verify_source_inventory(root, record)
            results, environment_errors = _conversion_contract_results(
                root,
                state_path.parent,
                inventory,
                conversion,
                validation,
                record,
            )
            current_reference = state["authoring"]["currentContract"]
            core = _contract_core(
                root,
                run_id,
                inventory,
                revision=current_reference["revision"] + 1,
                previous_sha256=current_reference["sha256"],
                results=results,
                environment_errors=environment_errors,
            )
            new_record, _ = _persist_contract_snapshot(state_path.parent, state, core)
            coverage = new_record["coverage"]
            stopped = bool(coverage["stopThresholdReached"])
            if stopped:
                state["authoring"]["status"] = "stopped"
                state["authoring"]["stopReason"] = (
                    f"Durable rule-error threshold reached: {coverage['E']}/{coverage['N']} "
                    "(100*E > 50*N)."
                )
                state["workflowStatus"] = "blocked"
            _write_unlocked(state_path, state)

            if validation.get("conversionScope", {}).get("kind") == "rule":
                validation_status, message = "blocked", "Structural validation is scoped; full solution validation is required."
            elif validation["invalid"]:
                validation_status, message = "blocked", "One or more generated detections failed structural validation."
            elif any(result["status"] != "migrated" for result in new_record["results"]):
                validation_status, message = (
                    "blocked",
                    "YOLO rule-level technical blockers remain; inspect the per-rule authoring contract.",
                )
            elif stopped:
                validation_status, message = (
                    "blocked",
                    state["authoring"]["stopReason"],
                )
            else:
                validation_status, message, runtime_evidence = _current_runtime_status(
                    root, state["context"]["workflowProfile"], new_record
                )
                if validation_status == "not-run":
                    try:
                        _validate_offline_authoring_gates(
                            root,
                            state_path,
                            state,
                            record=new_record,
                        )
                    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
                        validation_status = "blocked"
                        message = str(exc)
                    else:
                        message = _offline_authoring_validation_message()
            offline_authoring = (
                validation_status == "not-run"
                and state["context"]["workflowProfile"] == "authoring"
            )
            if offline_authoring:
                final_status = "passed"
                final_artifacts = {
                    "runtimeStatus": "not-run",
                    "validationMode": "offline-authoring",
                }
            elif validation_status == "environment-blocked":
                final_status = "passed"
                final_artifacts = {"runtimeStatus": "environment-blocked"}
            elif validation_status == "source-waived":
                final_status = "passed"
                whitelist = runtime_evidence.get("sourceWhitelist") or []
                final_artifacts = {
                    "runtimeStatus": "source-waived",
                    "sourceRuntimeWhitelistTable": "IdentityInfo",
                    "sourceRuntimeWhitelistCount": str(len(whitelist)),
                    "sourceRuntimeWhitelistRawStatus": "failed",
                }
            elif validation_status == "passed":
                final_status = "passed"
                final_artifacts = {}
            else:
                final_status = "blocked"
                final_artifacts = {"authoringContractSha256": state["authoring"]["currentContract"]["sha256"]}
            _complete_workflow_stage_unlocked(
                root,
                "validation",
                state_path,
                status=final_status,
                message=message,
                artifacts=final_artifacts,
                evidence=[state["authoring"]["currentContract"]["path"]],
            )
            state = _load(root)[1]
            record, _ = _current_yolo_record(root, state_path, state)
            return {
                "runId": run_id,
                "status": state["authoring"]["status"],
                "coverage": record["coverage"],
                "authoringContract": state["authoring"]["currentContract"],
                "workflowStatus": state["workflowStatus"],
                "next": _next_stage_name(state),
                "resumed": conversion_stage["status"] == "running",
                "workPerformed": True,
                "validationStatus": final_status,
                "runtimeStatus": validation_status,
                "packageAuthorized": False,
                "qualificationAuthorized": False,
                "prCreationAuthorized": False,
            }


def initialize_workflow(
    solution: str | Path,
    *,
    tenant_id: str | None = None,
    subscription_id: str | None = None,
    workspace_resource_id: str | None = None,
    workspace_customer_id: str | None = None,
    version_bump: str | None = None,
    target_version: str | None = None,
    workflow_profile: str | None = None,
    yolo: bool | None = None,
    campaign_id: str | None = None,
    new_run: bool = False,
    workbook_capability_version: int | None = None,
    arm_validation_method: str | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"solution folder does not exist: {root}")
    if version_bump not in (None, "none", "patch", "minor", "major"):
        raise ValueError("version bump must be none, patch, minor, or major")
    if target_version is not None:
        validate_v31_target_version(target_version)
        if version_bump not in (None, "none"):
            raise ValueError("target version cannot be combined with a version bump")
    if target_version is not None or (
        version_bump is not None and solution_data_version(root) is not None
    ):
        validate_v31_effective_version(
            solution_data_version(root), version_bump or "none", target_version,
        )
    if workflow_profile is None:
        raise ValueError(
            "workflow profile selection is required: choose authoring or qualification"
        )
    if workflow_profile not in WORKFLOW_PROFILES:
        raise ValueError("workflow profile must be authoring or qualification")
    if workbook_capability_version not in (None, 1):
        raise ValueError("unsupported workbook capability version")
    if arm_validation_method not in (None, *workbook_workflow.ARM_VALIDATION_METHODS):
        raise ValueError("ARM validation method must be arm-ttk or lab-deployment")
    if arm_validation_method and workbook_capability_version != 1:
        raise ValueError("an explicit ARM method requires workbook capability version 1")
    if workflow_profile == "qualification" and arm_validation_method == "arm-ttk":
        raise ValueError("the workbook-capable Qualification route requires lab-deployment")
    explicit_campaign_id = campaign_id
    if campaign_id is not None:
        from .budget import _safe_campaign_id
        campaign_id = _safe_campaign_id(campaign_id)
    if yolo is True and campaign_id is None and new_run:
        raise ValueError("new YOLO workflows require an explicit --campaign-id")
    target = None
    if workflow_profile == "qualification":
        missing = [
            name
            for name, value in (
                ("tenant-id", tenant_id),
                ("subscription-id", subscription_id),
                ("workspace-resource-id", workspace_resource_id),
                ("workspace-customer-id", workspace_customer_id),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                "qualification requires a locked target context: "
                + ", ".join(missing)
            )
        target = build_target(
            tenant_id=tenant_id or "",
            subscription_id=subscription_id or "",
            workspace_resource_id=workspace_resource_id or "",
            workspace_customer_id=workspace_customer_id or "",
        )
    requested_context = {
        "tenantId": target["tenantId"] if target else tenant_id,
        "subscriptionId": target["subscriptionId"] if target else subscription_id,
        "workspaceResourceId": (
            target["workspaceResourceId"] if target else workspace_resource_id
        ),
        "workspaceCustomerId": (
            target["workspaceCustomerId"] if target else workspace_customer_id
        ),
        "targetContextLocked": bool(target),
        "versionBump": version_bump,
        "targetVersion": target_version,
    }
    if new_run:
        if requested_run_id(root):
            raise ValueError("--new-run and --run-id cannot be combined")
        _preflight_campaign_binding(
            root,
            campaign_id,
            yolo=yolo is True and not (
                workbook_capability_version == 1 and not workbook_workflow.has_analytic_rules(root)
            ),
        )
        run = create_run(root)
        with using_run(root, run.name):
            return initialize_workflow(
                root, tenant_id=tenant_id, subscription_id=subscription_id,
                workspace_resource_id=workspace_resource_id,
                workspace_customer_id=workspace_customer_id, version_bump=version_bump,
                target_version=target_version,
                workflow_profile=workflow_profile, yolo=yolo, campaign_id=campaign_id,
                workbook_capability_version=workbook_capability_version,
                arm_validation_method=arm_validation_method,
            )
    existing_path = existing_artifact_path(root, STATE_FILE_NAME)
    if existing_path.exists():
        with _run_writer_lock(existing_path.parent):
            path, state = _load(root)
            if yolo is True and "authoring" not in state and not state["context"].get("workbookFullInventory"):
                raise ValueError(
                    "YOLO cannot be enabled on an existing legacy run; initialize a new run explicitly"
                )
            if yolo is True and not state.get("budget") and not campaign_id:
                raise ValueError(
                    "pre-existing YOLO run has unmeasured usage; provide "
                    "--campaign-id to link it conservatively"
                )
            context = state["context"]
            if workbook_capability_version is not None and context.get("workbookCapabilityVersion") != workbook_capability_version:
                raise ValueError("workbook capability cannot change on resumption; initialize a new run")
            if arm_validation_method is not None and context.get("armValidationMethod") != arm_validation_method:
                raise ValueError("ARM validation method cannot change on resumption; initialize a new run")
            workbook_workflow.verify_inventory(root, state)
            if target_version is not None and context.get("versionBump") not in (None, "none"):
                raise ValueError(
                    "target version cannot be combined with the workflow's selected version bump"
                )
            for key, value in requested_context.items():
                if key == "targetContextLocked":
                    continue
                if value is not None and context.get(key) not in (None, value):
                    raise ValueError(
                        f"workflow already uses {key}={context.get(key)!r}, "
                        f"not {value!r}"
                    )
            if "authoring" in state:
                state = _recover_yolo_state(root, path, state)
                record, _ = _current_yolo_record(root, path, state)
                inventory_hash = record["inventory"]["sha256"]
                rule_ids = [rule["ruleId"] for rule in record["inventory"]["rules"]]
                budget_campaign_id = (
                    state.get("budget", {}).get("campaignId")
                    or campaign_id
                )
            else:
                inventory_hash, rule_ids = _budget_source_inventory(root, yolo=False)
                budget_campaign_id = (
                    state.get("budget", {}).get("campaignId")
                    or campaign_id
                )
            existing_budget = state.get("budget")
            link_campaign = False
            if existing_budget:
                if explicit_campaign_id and explicit_campaign_id != existing_budget["campaignId"]:
                    raise ValueError(
                        "workflow is already linked to a different campaign; "
                        "campaign binding is immutable"
                    )
                if existing_budget["inventorySha256"] != inventory_hash:
                    raise ValueError(
                        "campaign frozen source inventory changed; preserve the existing run "
                        "and explicitly initialize a separately reviewed campaign"
                    )
                budget_summary(
                    root, existing_budget["campaignId"], expected_inventory=inventory_hash,
                )
            elif budget_campaign_id:
                campaign_exists = validate_campaign_binding(
                    root,
                    budget_campaign_id,
                    inventory_sha256=inventory_hash,
                    rule_ids=rule_ids,
                )
                if campaign_exists and state["runId"] not in budget_summary(
                    root, budget_campaign_id, expected_inventory=inventory_hash,
                )["linkedRunIds"]:
                    raise BudgetReceiptError(
                        "an unbudgeted existing workflow cannot be joined to an active "
                        "campaign; initialize an explicitly linked replacement run"
                    )
                link_campaign = True
            for key, value in requested_context.items():
                if key == "targetContextLocked":
                    if value:
                        context[key] = True
                    continue
                if value is not None and context.get(key) is None:
                    context[key] = value
            _select_workflow_profile(state, workflow_profile)
            if link_campaign:
                create_or_link_campaign(
                    root,
                    budget_campaign_id,
                    inventory_sha256=inventory_hash,
                    run_id=state["runId"],
                    rule_ids=rule_ids,
                    legacy_usage_unknown=True,
                )
                state["budget"] = {
                    "schemaVersion": "1.0.0",
                    "campaignId": budget_campaign_id,
                    "inventorySha256": inventory_hash,
                    "status": "active",
                    "stopReason": None,
                }
            _write_unlocked(path, state)
            if target:
                write_target(root, target)
            return {
                **state,
                "statePath": str(path),
                "resumed": True,
                "next": _next_stage_name(state),
            }

    workbook_only = workbook_capability_version == 1 and not workbook_workflow.has_analytic_rules(root)
    frozen_inventory = _source_inventory(root) if yolo is True and not workbook_only else None
    if frozen_inventory is not None and not campaign_id:
        raise ValueError("new YOLO workflows require an explicit --campaign-id")
    preflight_inventory = _preflight_campaign_binding(
        root,
        campaign_id,
        yolo=yolo is True and not workbook_only,
        inventory=frozen_inventory,
    )
    if yolo is True and requested_run_id(root) is None:
        run = create_run(root)
        with using_run(root, run.name):
            return initialize_workflow(
                root,
                tenant_id=tenant_id,
                subscription_id=subscription_id,
                workspace_resource_id=workspace_resource_id,
                workspace_customer_id=workspace_customer_id,
                version_bump=version_bump,
                target_version=target_version,
                workflow_profile=workflow_profile,
                yolo=True,
                campaign_id=campaign_id,
                workbook_capability_version=workbook_capability_version,
                arm_validation_method=arm_validation_method,
            )

    now = _utc_now()
    path = artifact_path(root, STATE_FILE_NAME, create_parent=True)
    state = {
        "schemaVersion": SCHEMA_VERSION,
        "solution": str(root),
        "workflowStatus": "inProgress",
        "createdAt": now,
        "updatedAt": now,
        "context": requested_context,
        "stages": {
            name: _stage_result(
                name,
                required=not (
                    workflow_profile == "authoring"
                    and name in AUTHORING_OPTIONAL_STAGES
                ),
            )
            for name in STAGES
        },
    }
    state["context"]["workflowProfile"] = workflow_profile
    state["context"]["profileSelectionConfirmed"] = True
    if workbook_capability_version == 1:
        state["context"]["workbookCapabilityVersion"] = 1
        state["context"]["armValidationMethod"] = arm_validation_method or "lab-deployment"
        state["workbooks"] = workbook_workflow.freeze_inventory(root)
        if yolo and workbook_only:
            state["context"]["workbookFullInventory"] = True
        if workbook_only and workflow_profile == "qualification":
            state["context"]["workbookQualificationAfterArm"] = True
            for name in ("mockIngestion", "alertParity"):
                state["stages"][name] = _stage_result(name, required=False)
    if frozen_inventory is not None:
        record, _ = _persist_contract_snapshot(
            path.parent,
            state,
            _contract_core(
                root,
                path.parent.name,
                frozen_inventory,
                revision=1,
                previous_sha256=None,
            ),
        )
        campaign_inventory_hash = record["inventory"]["sha256"]
        campaign_rule_ids = [rule["ruleId"] for rule in record["inventory"]["rules"]]
    else:
        campaign_inventory_hash, campaign_rule_ids = (
            preflight_inventory
            if preflight_inventory is not None
            else _budget_source_inventory(root, yolo=False)
        )
    if campaign_id:
        create_or_link_campaign(
            root,
            campaign_id,
            inventory_sha256=campaign_inventory_hash,
            run_id=path.parent.name,
            rule_ids=campaign_rule_ids,
        )
        state["budget"] = {
            "schemaVersion": "1.0.0",
            "campaignId": campaign_id,
            "inventorySha256": campaign_inventory_hash,
            "status": "active",
            "stopReason": None,
        }
    _write(path, state)
    if target:
        write_target(root, target)
    return {
        **state,
        "statePath": str(path),
        "resumed": False,
        "next": _next_stage_name(state),
    }


def _select_workflow_profile(state: dict[str, Any], workflow_profile: str) -> None:
    context = state["context"]
    current = context["workflowProfile"]
    if current != workflow_profile:
        protected = [
            name
            for name in (*AUTHORING_OPTIONAL_STAGES, "report")
            if state["stages"][name]["status"] not in {"pending", "notRequired"}
        ]
        if protected:
            raise ValueError(
                "workflow profile cannot change after qualification/report stages "
                f"started: {', '.join(sorted(protected))}"
            )
        for name in AUTHORING_OPTIONAL_STAGES:
            state["stages"][name] = _stage_result(
                name,
                required=workflow_profile == "qualification",
            )
        context["workflowProfile"] = workflow_profile
    context["profileSelectionConfirmed"] = True


def _validate_packaging_evidence(
    state: dict[str, Any],
    artifacts: dict[str, str],
    solution: str | Path,
    *,
    allow_candidate: bool = False,
) -> None:
    if artifacts.get("packager") != "V3.1":
        raise ValueError("passed packaging stage requires packager=V3.1; rebuild old packages")
    report_value = artifacts.get("packageReport")
    if not report_value:
        raise ValueError("passed packaging stage requires a V3.1 packageReport artifact")
    report_path = resolve_artifact_reference(solution, report_value)
    if not report_path.is_file():
        raise ValueError(f"V3.1 package report does not exist: {report_path}")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"V3.1 package report is invalid: {report_path}: {exc}") from exc
    if not isinstance(report, dict) or report.get("packager") != "V3.1":
        raise ValueError(f"package report does not prove V3.1 packaging: {report_path}")
    selection = verify_applied_package_selection(solution, str(state.get("runId") or ""))
    validation_status = state["stages"]["validation"]["status"]
    if validation_status != "passed":
        if not selection:
            raise ValueError(
                "partial V3.1 packaging requires a fresh, applied evidence-based selection plan"
            )
        plan = selection["plan"]
        verification = report.get("selectionVerification") or {}
        summary = plan.get("summary") or {}
        if (
            plan.get("summary", {}).get("outcome") != "partial"
            or not _partial_coverage_allowed(summary)
            or report.get("selectionOutcome") != "partial-package-validated"
            or report.get("selectionPlanSha256") != plan.get("planSha256")
            or artifacts.get("selectionPlanSha256") != plan.get("planSha256")
            or report.get("selectionSummary") != summary
            or verification.get("planSha256") != plan.get("planSha256")
            or verification.get("outcome") != "partial"
            or verification.get("analyticRuleIncluded")
            != summary.get("analyticRuleIncluded")
            or verification.get("xdrDetectionIncluded")
            != summary.get("xdrDetectionIncluded")
            or verification.get("coverageNumerator")
            != summary.get("coverageNumerator")
            or verification.get("coverageDenominator")
            != summary.get("coverageDenominator")
            or verification.get("partialPublicationAllowed") is not True
            or verification.get("mainTemplateVerified") is not True
            or verification.get("zipVerified") is not True
        ):
            raise ValueError(
                "partial package evidence does not bind the complete current excluded inventory"
            )
    elif selection:
        plan = selection["plan"]
        summary = plan.get("summary") or {}
        verification = report.get("selectionVerification") or {}
        if (
            report.get("selectionPlanSha256") != plan.get("planSha256")
            or artifacts.get("selectionPlanSha256") != plan.get("planSha256")
            or report.get("selectionSummary") != summary
            or verification.get("planSha256") != plan.get("planSha256")
            or verification.get("analyticRuleIncluded")
            != summary.get("analyticRuleIncluded")
            or verification.get("xdrDetectionIncluded")
            != summary.get("xdrDetectionIncluded")
            or verification.get("mainTemplateVerified") is not True
            or verification.get("zipVerified") is not True
        ):
            raise ValueError("V3.1 package report does not match the applied selection plan")
    for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip"):
        value = artifacts.get(name) or report.get(name)
        if not value or not resolve_artifact_reference(solution, value).is_file():
            raise ValueError(f"V3.1 packaging evidence is missing artifact: {name}")
    packaging = state.get("packaging")
    requested_bump = state["context"].get("versionBump")
    effective_bump = (
        ((packaging.get("currentAttempt") or {}).get("effectiveVersionBump"))
        if packaging else requested_bump
    )
    if effective_bump is not None and report.get("versionBump") != effective_bump:
        raise ValueError(
            "V3.1 package report version bump does not match workflow context: "
            f"{report.get('versionBump')!r} != {effective_bump!r}"
        )
    if packaging:
        attempt = packaging.get("currentAttempt") or {}
        if (
            attempt.get("status") not in (
                {"passed", "blocked"} if allow_candidate and workbook_workflow.enabled(state) else {"passed"}
            )
            or report.get("packageAttemptId") != attempt.get("attemptId")
            or report.get("workflowRunId") != state.get("runId")
            or report.get("requestedVersionBump") != attempt.get("requestedVersionBump")
            or report.get("effectiveVersionBump") != attempt.get("effectiveVersionBump")
            or report.get("requestedTargetVersion") != attempt.get("requestedTargetVersion")
            or report.get("effectiveTargetVersion") != attempt.get("effectiveTargetVersion")
        ):
            raise ValueError("V3.1 package report is stale or belongs to another workflow attempt")
        input_after = (report.get("packageInputs") or {}).get("after") or {}
        if input_after.get("sha256") != attempt.get("packageInputSha256"):
            raise ValueError("V3.1 package input identity does not match the current workflow attempt")
        recorded_hashes = report.get("packageArtifactHashes")
        if not isinstance(recorded_hashes, dict):
            raise ValueError("V3.1 package report has no package artifact hashes")
        for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip"):
            path = resolve_artifact_reference(solution, artifacts.get(name) or report.get(name))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if recorded_hashes.get(name) != digest:
                raise ValueError(f"V3.1 package artifact is stale: {name}")
        report_digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
        if report_digest != attempt.get("packageReportSha256"):
            raise ValueError("V3.1 package report hash does not match the current workflow attempt")
    if workbook_workflow.enabled(state) and not allow_candidate and (
        state["context"]["armValidationMethod"] == "lab-deployment" or report.get("xdrWorkbookCount", 0)
    ):
        workbook_workflow.require_accepted(solution, state)


def _yolo_package_readiness(
    solution: Path,
    state_path: Path,
    state: dict[str, Any],
    *,
    allow_partial_selection: bool = False,
) -> None:
    """Require the full YOLO inventory to clear technical and explicit-review gates."""
    validation_status = state["stages"]["validation"]["status"]
    if validation_status != "passed" and not (
        allow_partial_selection
        and not state.get("authoring")
        and validation_status == "blocked"
    ):
        raise ValueError("YOLO packaging requires the existing validation stage to pass")
    if allow_partial_selection and not state.get("authoring"):
        return
    if not state.get("authoring"):
        output = Path(solution).expanduser().resolve() / "XDR Detections"
        pending: list[str] = []
        for path in xdr_detection_files(output):
            try:
                document = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                raise ValueError(f"cannot verify XDR review state in {path}: {exc}") from exc
            if not isinstance(document, dict):
                raise ValueError(f"cannot verify XDR review state in {path}: document is not an object")
            conversion = ((document.get("contentProvenance") or {}).get("conversion") or {})
            if (
                isinstance(conversion, dict)
                and (
                    conversion.get("reviewRequired") is True
                    or conversion.get("status") == "needsReview"
                )
            ):
                pending.append(path.relative_to(solution).as_posix())
        if pending:
            raise ValueError(
                "V3.1 packaging is blocked by unresolved detection review flags: "
                + ", ".join(sorted(pending))
            )
        return
    record, _ = _current_yolo_record(solution, state_path, state)
    results = record.get("results") or []
    rules = record.get("inventory", {}).get("rules") or []
    if len(results) != len(rules) or not results:
        raise ValueError("YOLO packaging requires complete full-inventory authoring results")
    blockers = []
    for result in results:
        rule_id = result.get("ruleId", "<unknown>")
        if (
            result.get("status") != "migrated"
            or result.get("conversionStatus") != "converted"
            or result.get("validationStatus") != "passed"
            or result.get("reviewRequired") is True
            or (result.get("target") or {}).get("structurallyValid") is not True
            or any(
                finding.get("kind") == "error" and finding.get("unresolved") is True
                for finding in result.get("findings", [])
            )
        ):
            blockers.append(rule_id)
    if blockers:
        raise ValueError(
            "YOLO packaging is blocked by unresolved technical or explicit-review "
            "items in the complete inventory: " + ", ".join(blockers)
        )


def _verify_current_package_state(solution: Path, state: dict[str, Any]) -> None:
    packaging = state.get("packaging") or {}
    successful = packaging.get("lastSuccessful") or {}
    if not successful.get("packageSucceeded"):
        raise ValueError("workflow has no successful current V3.1 package attempt")
    if package_input_identity(solution)["sha256"] != successful.get("packageInputSha256"):
        raise ValueError("package inputs changed after V3.1 packaging; rebuild before continuing")
    report_reference = successful.get("packageReport")
    if not isinstance(report_reference, str) or not report_reference:
        raise ValueError("current V3.1 package report reference is missing")
    report_path = resolve_artifact_reference(solution, report_reference)
    if not report_path.is_file():
        raise ValueError("current V3.1 package report is missing")
    report_bytes = report_path.read_bytes()
    if hashlib.sha256(report_bytes).hexdigest() != successful.get("packageReportSha256"):
        raise ValueError("current V3.1 package report is stale or modified")
    report = json.loads(report_bytes)
    if (
        report.get("packager") != "V3.1"
        or report.get("workflowRunId") != state.get("runId")
        or report.get("packageAttemptId") != successful.get("attemptId")
        or report.get("packageArtifactsSha256") != successful.get("packageArtifactsSha256")
    ):
        raise ValueError("current package report does not match the successful V3.1 workflow attempt")
    if report.get("selectionPlanSha256") is not None:
        selection = verify_applied_package_selection(
            solution, str(state.get("runId") or ""),
        )
        if (
            not selection
            or selection["plan"].get("planSha256") != report.get("selectionPlanSha256")
        ):
            raise ValueError("current V3.1 package selection evidence is stale or mismatched")
        summary = selection["plan"].get("summary") or {}
        if (
            summary.get("outcome") == "partial"
            and (
                not _partial_coverage_allowed(summary)
                or report.get("selectionOutcome") != "partial-package-validated"
            )
        ):
            raise ValueError("current partial package no longer meets migrated-detection coverage")
    elif report.get("selectionOutcome") == "partial-package-validated":
        raise ValueError("partial V3.1 package is missing its selection-plan binding")
    recorded_hashes = report.get("packageArtifactHashes") or {}
    for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip"):
        artifact = report.get(name)
        if not artifact:
            raise ValueError(f"current V3.1 package report has no {name} artifact")
        path = resolve_artifact_reference(solution, artifact)
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != recorded_hashes.get(name)
        ):
            raise ValueError(f"current V3.1 package artifact is stale: {name}")


def _package_freshness(solution: str | Path, state: dict[str, Any]) -> dict[str, Any] | None:
    successful = (state.get("packaging") or {}).get("lastSuccessful")
    if not successful:
        return None
    try:
        current_identity = package_input_identity(solution)["sha256"]
    except (OSError, ValueError) as exc:
        return {
            "status": "unverifiable",
            "currentPackageInputSha256": None,
            "packagedInputSha256": successful.get("packageInputSha256"),
            "reason": str(exc),
        }
    packaged_identity = successful.get("packageInputSha256")
    if current_identity != packaged_identity:
        return {
            "status": "stale",
            "currentPackageInputSha256": current_identity,
            "packagedInputSha256": packaged_identity,
            "reason": "solution package inputs changed after the successful V3.1 build",
        }
    try:
        _verify_current_package_state(Path(solution).expanduser().resolve(), state)
    except (OSError, ValueError, json.JSONDecodeError, TypeError, AttributeError) as exc:
        return {
            "status": "stale",
            "currentPackageInputSha256": current_identity,
            "packagedInputSha256": packaged_identity,
            "reason": str(exc),
        }
    return {
        "status": "current",
        "currentPackageInputSha256": current_identity,
        "packagedInputSha256": packaged_identity,
        "reason": None,
    }


def _archive_package_evidence(
    solution: Path,
    successful: dict[str, Any],
) -> dict[str, str]:
    report_reference = successful.get("packageReport")
    if not isinstance(report_reference, str) or not report_reference:
        raise ValueError("prior V3.1 package report reference is missing")
    report_path = resolve_artifact_reference(solution, report_reference)
    if not report_path.is_file():
        raise ValueError("prior V3.1 package report is missing")
    report_bytes = report_path.read_bytes()
    if hashlib.sha256(report_bytes).hexdigest() != successful.get("packageReportSha256"):
        raise ValueError("prior V3.1 package report is stale or modified")
    report = json.loads(report_bytes)
    if report.get("packager") != "V3.1":
        raise ValueError("prior package evidence is not from V3.1")
    attempt_id = str(successful.get("attemptId") or uuid.uuid4())
    archive = report_path.parent / "package-history" / attempt_id
    files = {"packageReport": report_path}
    files.update({
        name: resolve_artifact_reference(solution, report[name])
        for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip")
        if isinstance(report.get(name), str) and report[name]
    })
    if set(files) != {
        "packageReport", "mainTemplate", "createUiDefinition", "testParameters", "zip",
    }:
        raise ValueError("prior V3.1 package report is missing artifact references")
    recorded_hashes = report.get("packageArtifactHashes") or {}
    archived: dict[str, str] = {}
    for name, source in files.items():
        if not source.is_file():
            raise ValueError(f"prior V3.1 package artifact is missing: {name}")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        expected = (
            successful.get("packageReportSha256")
            if name == "packageReport" else recorded_hashes.get(name)
        )
        if digest != expected:
            raise ValueError(f"prior V3.1 package artifact is stale: {name}")
    archive.mkdir(parents=True, exist_ok=False)
    for name, source in files.items():
        destination = archive / f"{name}-{source.name}"
        shutil.copy2(source, destination)
        archived[name] = destination.relative_to(solution).as_posix()
    return archived


def _validate_historical_package_receipt(
    solution: Path,
    state: dict[str, Any],
    successful: dict[str, Any],
    expected_version: str,
) -> dict[str, Any]:
    report_reference = successful.get("packageReport")
    if not isinstance(report_reference, str) or not report_reference:
        raise ValueError("prior V3.1 package report reference is missing")
    report_path = resolve_artifact_reference(solution, report_reference)
    if not report_path.is_file():
        raise ValueError("prior V3.1 package report is missing")
    report_bytes = report_path.read_bytes()
    if hashlib.sha256(report_bytes).hexdigest() != successful.get("packageReportSha256"):
        raise ValueError("prior V3.1 package report is stale or modified")
    try:
        report = json.loads(report_bytes)
    except json.JSONDecodeError as exc:
        raise ValueError("prior V3.1 package report is invalid JSON") from exc
    package_inputs = report.get("packageInputs") or {}
    if (
        report.get("status") != "passed"
        or report.get("packager") != "V3.1"
        or report.get("workflowRunId") != state.get("runId")
        or report.get("packageAttemptId") != successful.get("attemptId")
        or report.get("version") != expected_version
        or successful.get("version") != expected_version
        or report.get("packageArtifactsSha256") != successful.get("packageArtifactsSha256")
        or (package_inputs.get("after") or {}).get("sha256")
        != successful.get("packageInputSha256")
    ):
        raise ValueError(
            "prior package receipt is not a successful V3.1 build for this workflow run, "
            "version, attempt, and input identity"
        )
    return report


def _release_notes_refresh_proposal(
    solution: Path,
    *,
    release_date: str | None = None,
    change_history: str,
) -> tuple[Path, str, str]:
    from .release_notes import release_notes_refresh_proposal

    path, original_sha, expected_sha, _ = release_notes_refresh_proposal(
        solution,
        version=solution_data_version(solution),
        release_date=release_date,
        change_history=change_history,
    )
    return path, original_sha, expected_sha


def _identity_from_file_hashes(files: dict[str, str]) -> str:
    canonical = json.dumps(
        [
            {"path": name, "sha256": digest}
            for name, digest in sorted(files.items(), key=lambda item: Path(item[0]))
        ],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _validate_package_input_file_manifest(
    value: Any,
    *,
    expected_sha256: str,
    expected_file_count: int | None = None,
    label: str,
) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} has no complete per-file package-input manifest")
    files: dict[str, str] = {}
    for name, digest in value.items():
        if (
            not isinstance(name, str)
            or not name
            or name.replace("\\", "/") != name
            or Path(name).is_absolute()
            or ".." in Path(name).parts
            or Path(name).as_posix() != name
            or not isinstance(digest, str)
            or not re.fullmatch(r"[a-f0-9]{64}", digest)
        ):
            raise ValueError(f"{label} contains an invalid package-input manifest entry")
        files[name] = digest
    if (
        not files
        or _identity_from_file_hashes(files) != expected_sha256
        or (expected_file_count is not None and len(files) != expected_file_count)
    ):
        raise ValueError(
            f"{label} per-file manifest does not match its receipt-bound package-input identity"
        )
    return dict(sorted(files.items(), key=lambda item: Path(item[0])))


def _legacy_baseline_evidence(
    solution: Path,
    evidence_reference: str | Path,
    *,
    expected_current_sha256: str,
    current_files: dict[str, str],
    expected_prior_sha256: str,
    expected_prior_file_count: int | None,
    expected_evidence_sha256: str | None = None,
) -> tuple[dict[str, str], dict[str, str]]:
    reference = str(evidence_reference).replace("\\", "/")
    evidence_path = content_path(solution, reference)
    if evidence_path.is_symlink() or not evidence_path.is_file():
        raise ValueError("legacy baseline evidence is missing or unsafe")
    evidence_bytes = evidence_path.read_bytes()
    evidence_sha256 = hashlib.sha256(evidence_bytes).hexdigest()
    if expected_evidence_sha256 and evidence_sha256 != expected_evidence_sha256:
        raise ValueError("legacy baseline evidence changed after the rebuild plan")
    try:
        evidence = json.loads(evidence_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("legacy baseline evidence is not valid JSON") from exc
    current_sha256 = _identity_from_file_hashes(current_files)
    changes = evidence.get("changedInputs") if isinstance(evidence, dict) else None
    if (
        not isinstance(evidence, dict)
        or evidence.get("priorReceiptIdentity") != expected_prior_sha256
        or evidence.get("currentIdentity") != expected_current_sha256
        or current_sha256 != expected_current_sha256
        or evidence.get("currentFileCount") != len(current_files)
        or (
            expected_prior_file_count is not None
            and evidence.get("priorFileCount") != expected_prior_file_count
        )
        or not isinstance(evidence.get("priorFileCount"), int)
        or isinstance(evidence.get("priorFileCount"), bool)
        or not isinstance(evidence.get("currentFileCount"), int)
        or isinstance(evidence.get("currentFileCount"), bool)
        or not isinstance(changes, list)
        or not changes
    ):
        raise ValueError(
            "legacy baseline evidence is not bound to the successful receipt and current input backup"
        )

    baseline = dict(current_files)
    recorded_changes: dict[str, tuple[str | None, str | None]] = {}
    for change in changes:
        if not isinstance(change, dict):
            raise ValueError("legacy baseline evidence has an invalid changed-input record")
        name = change.get("path")
        before = change.get("beforeSha256")
        after = change.get("currentSha256")
        if (
            not isinstance(name, str)
            or not name
            or name.replace("\\", "/") != name
            or Path(name).is_absolute()
            or ".." in Path(name).parts
            or Path(name).as_posix() != name
            or name in recorded_changes
            or (before is not None and (
                not isinstance(before, str) or not re.fullmatch(r"[a-f0-9]{64}", before)
            ))
            or (after is not None and (
                not isinstance(after, str) or not re.fullmatch(r"[a-f0-9]{64}", after)
            ))
            or before == after
            or current_files.get(name) != after
            or (name not in current_files and after is not None)
            or name.casefold().endswith("releasenotes.md")
        ):
            raise ValueError("legacy baseline evidence has an invalid or out-of-scope changed input")
        recorded_changes[name] = (before, after)
        if before is None:
            baseline.pop(name, None)
        else:
            baseline[name] = before

    baseline = dict(sorted(baseline.items(), key=lambda item: Path(item[0])))
    actual_changes = {
        name: (baseline.get(name), current_files.get(name))
        for name in sorted(set(baseline) | set(current_files), key=Path)
        if baseline.get(name) != current_files.get(name)
    }
    if (
        recorded_changes != actual_changes
        or len(baseline) != evidence["priorFileCount"]
        or _identity_from_file_hashes(baseline) != expected_prior_sha256
    ):
        raise ValueError(
            "legacy baseline evidence does not reconstruct the complete successful "
            "package-input manifest"
        )
    return baseline, {
        "path": reference,
        "sha256": evidence_sha256,
    }


def _same_version_rebuild_scope(
    baseline_files: dict[str, str],
    current_files: dict[str, str],
    approved_changes: dict[str, Any],
) -> dict[str, str | None]:
    actual_changes = {
        name: current_files.get(name)
        for name in sorted(set(baseline_files) | set(current_files), key=Path)
        if baseline_files.get(name) != current_files.get(name)
    }
    if not actual_changes:
        raise ValueError("same-version rebuild requires actual package-input changes")
    if any(name.casefold().endswith("releasenotes.md") for name in actual_changes):
        raise ValueError("same-version content rebuild does not permit any ReleaseNotes change")
    if set(approved_changes) != set(actual_changes):
        missing = sorted(set(actual_changes) - set(approved_changes))
        unchanged_or_extra = sorted(set(approved_changes) - set(actual_changes))
        details = []
        if missing:
            details.append(f"unapproved actual changes: {', '.join(missing)}")
        if unchanged_or_extra:
            details.append(
                "approved paths that are unchanged or not package inputs: "
                + ", ".join(unchanged_or_extra)
            )
        raise ValueError(
            "same-version rebuild changed-input scope must exactly match the "
            "successful receipt baseline (" + "; ".join(details) + ")"
        )
    if approved_changes != actual_changes:
        raise ValueError(
            "same-version rebuild approved path hashes do not match the exact "
            "receipt-to-current input diff"
        )
    return actual_changes


def _read_failed_candidate_evidence(
    solution: Path,
    state: dict[str, Any],
    target_version: str,
    evidence_reference: str | Path,
) -> tuple[Path, dict[str, Any]]:
    reference = str(evidence_reference).replace("\\", "/")
    evidence_path = content_path(solution, reference)
    if evidence_path.is_symlink() or not evidence_path.is_file():
        raise ValueError("failed-candidate evidence is missing or unsafe")
    parts = Path(reference).parts
    if (
        Path(reference).is_absolute()
        or ".." in parts
        or len(parts) < 4
        or parts[0] != "Logs"
        or parts[1] != "sentinel-xdr-migration"
        or parts[2] != state.get("runId")
    ):
        raise ValueError("failed-candidate evidence must belong to the selected workflow run")
    try:
        evidence = json.loads(evidence_path.read_bytes())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("failed-candidate evidence is invalid JSON") from exc
    if not isinstance(evidence, dict):
        raise ValueError("failed-candidate evidence must be a JSON object")
    attempt = (state.get("packaging") or {}).get("currentAttempt") or {}
    consumed = (state.get("packaging") or {}).get("lastConsumedAction") or {}
    candidate_inputs = evidence.get("currentPackageInput") or {}
    evidence_consumed = evidence.get("lastConsumedAction")
    if not isinstance(candidate_inputs, dict) or not isinstance(evidence_consumed, dict):
        raise ValueError("failed-candidate evidence is missing its consumed attempt binding")
    attempt_id = attempt.get("attemptId")
    expected_artifacts = {
        "Package/mainTemplate.json": "mainTemplate",
        "Package/createUiDefinition.json": "createUiDefinition",
        "Package/testParameters.json": "testParameters",
        f"Package/{target_version}.zip": "zip",
    }
    generated = evidence.get("generatedArtifacts")
    if (
        evidence.get("artifactKind") != "v3-1-arm-ttk-failure-final-handoff"
        or evidence.get("runId") != state.get("runId")
        or evidence.get("solution") != solution.name
        or evidence.get("shellStatus") != "completed"
        or not isinstance(evidence.get("cliExitCode"), int)
        or isinstance(evidence.get("cliExitCode"), bool)
        or evidence.get("cliExitCode") == 0
        or not isinstance(evidence.get("v31ChildExitCode"), int)
        or isinstance(evidence.get("v31ChildExitCode"), bool)
        or evidence.get("v31ChildExitCode") == 0
        or evidence.get("currentVersion") != target_version
        or solution_data_version(solution) != target_version
        or evidence.get("bumpConsumed") is not True
        or evidence.get("packageReportExists") is not False
        or not isinstance(candidate_inputs, dict)
        or not isinstance(candidate_inputs.get("sha256"), str)
        or not re.fullmatch(r"[a-f0-9]{64}", candidate_inputs["sha256"])
        or not isinstance(candidate_inputs.get("fileCount"), int)
        or isinstance(candidate_inputs.get("fileCount"), bool)
        or candidate_inputs.get("fileCount") < 1
        or (state.get("packaging") or {}).get("lastSuccessful") is not None
        or attempt.get("status") != "failed"
        or attempt.get("bumpConsumed") is not True
        or attempt_id != consumed.get("attemptId")
        or evidence_consumed.get("attemptId") != attempt_id
        or evidence_consumed.get("packageSucceeded") is not False
        or evidence_consumed.get("packageInputSha256") != candidate_inputs.get("sha256")
        or consumed.get("packageSucceeded") is not False
        or consumed.get("bumpConsumed") is not True
        or attempt.get("effectiveVersionBump") not in {"patch", "minor", "major"}
        or attempt.get("packageReportSha256") is not None
        or attempt.get("packageInputSha256") != candidate_inputs.get("sha256")
        or consumed.get("packageInputSha256") != candidate_inputs.get("sha256")
        or not isinstance(generated, dict)
        or set(generated) != set(expected_artifacts)
    ):
        raise ValueError(
            "failed-candidate evidence is not a matching consumed, failed V3.1 attempt "
            "for the selected run and current version"
        )
    package_report = content_path(
        solution,
        f"Logs/sentinel-xdr-migration/{state['runId']}/packaging.v3_1.json",
    )
    if package_report.exists() or package_report.is_symlink():
        raise ValueError(
            "failed-candidate evidence conflicts with an existing V3.1 package report"
        )
    snapshot = evidence.get("failedArtifactSnapshot")
    if (
        not isinstance(snapshot, str)
        or not snapshot
        or Path(snapshot).is_absolute()
        or ".." in Path(snapshot).parts
        or Path(snapshot).as_posix() != snapshot
    ):
        raise ValueError("failed-candidate evidence has no safe artifact snapshot reference")
    for relative, artifact_name in expected_artifacts.items():
        record = generated.get(relative)
        digest = record.get("sha256") if isinstance(record, dict) else None
        size = record.get("bytes") if isinstance(record, dict) else None
        if (
            not isinstance(digest, str)
            or not re.fullmatch(r"[a-f0-9]{64}", digest)
            or not isinstance(size, int)
            or isinstance(size, bool)
            or size < 1
        ):
            raise ValueError(f"failed-candidate evidence has invalid {artifact_name} metadata")
        candidate = content_path(solution, relative)
        if (
            candidate.is_symlink()
            or not candidate.is_file()
            or candidate.stat().st_size != size
            or hashlib.sha256(candidate.read_bytes()).hexdigest() != digest
        ):
            raise ValueError(
                f"failed V3.1 candidate artifact is missing or changed: {artifact_name}"
            )
        snapshot_candidate = content_path(
            solution,
            f"{evidence_path.parent.relative_to(solution).as_posix()}/{snapshot}/{relative}",
        )
        if (
            snapshot_candidate.is_symlink()
            or not snapshot_candidate.is_file()
            or snapshot_candidate.stat().st_size != size
            or hashlib.sha256(snapshot_candidate.read_bytes()).hexdigest() != digest
        ):
            raise ValueError(
                f"archived failed V3.1 candidate artifact is missing or changed: {artifact_name}"
            )
    return evidence_path, evidence


def _archive_failed_candidate_evidence(
    solution: Path,
    evidence_path: Path,
    evidence: dict[str, Any],
    archive_root: Path,
) -> dict[str, str]:
    archive_root.mkdir(parents=True, exist_ok=False)
    archived = {
        "failedCandidateEvidence": archive_root / evidence_path.name,
    }
    shutil.copy2(evidence_path, archived["failedCandidateEvidence"])
    for relative in (evidence.get("generatedArtifacts") or {}):
        source = content_path(solution, relative)
        destination = archive_root / Path(relative).name
        shutil.copy2(source, destination)
        archived[Path(relative).name] = destination
    return {
        name: path.relative_to(solution).as_posix()
        for name, path in archived.items()
    }


def _validate_release_notes_refresh_inputs(
    solution: Path,
    action: dict[str, Any],
    current_identity: str,
) -> None:
    if action.get("actionType") != "release-notes-refresh":
        return
    notes_path = action.get("releaseNotesPath")
    before = action.get("packageInputFilesBefore")
    if not isinstance(notes_path, str) or not isinstance(before, dict):
        raise ValueError("ReleaseNotes refresh action is missing its bound input manifest")
    if (
        not all(
            isinstance(name, str)
            and isinstance(digest, str)
            and re.fullmatch(r"[a-f0-9]{64}", digest)
            for name, digest in before.items()
        )
        or notes_path not in before
        or before.get(notes_path) != action.get("releaseNotesOriginalSha256")
    ):
        raise ValueError("ReleaseNotes refresh baseline manifest is invalid")
    current = package_input_file_hashes(solution)
    if set(current) != set(before):
        raise ValueError("package inventory changed during ReleaseNotes refresh")
    changed = [name for name in current if current[name] != before[name]]
    if changed != [notes_path]:
        raise ValueError(
            "ReleaseNotes refresh permits only the exact planned ReleaseNotes.md change"
        )
    if current[notes_path] != action.get("releaseNotesExpectedSha256"):
        raise ValueError("ReleaseNotes.md does not match the exact approved refresh")
    expected_files = dict(before)
    expected_files[notes_path] = action["releaseNotesExpectedSha256"]
    expected_identity = _identity_from_file_hashes(expected_files)
    if (
        expected_identity != action.get("packageInputSha256")
        or current_identity != expected_identity
    ):
        raise ValueError("ReleaseNotes refresh package-input identity is stale or mismatched")


def _validate_same_version_content_rebuild_inputs(
    solution: Path,
    action: dict[str, Any],
    current_identity: str,
    current_version: str | None,
    successful: dict[str, Any],
    legacy_baseline_evidence: str | Path | None = None,
) -> None:
    if action.get("actionType") not in {
        "same-version-content-rebuild",
        "same-version-failed-candidate-rebuild",
    }:
        return
    target_version = action.get("targetVersion")
    files = action.get("packageInputFilesBefore")
    approved_changes = action.get("approvedChangedInputs")
    backup_root = action.get("inputBackupRoot")
    historical_evidence = action.get("historicalEvidence")
    if (
        not isinstance(target_version, str)
        or target_version != current_version
        or not isinstance(files, dict)
        or not isinstance(approved_changes, dict)
        or not approved_changes
        or not isinstance(backup_root, str)
        or not backup_root
        or Path(backup_root).is_absolute()
        or ".." in Path(backup_root).parts
        or not isinstance(historical_evidence, dict)
    ):
        raise ValueError(
            "same-version rebuild is missing its exact current version or input backup binding"
        )
    if action.get("actionType") == "same-version-failed-candidate-rebuild":
        failed = action.get("failedCandidate") or {}
        baseline_files = action.get("basePackageInputFiles")
        if (
            not isinstance(failed, dict)
            or failed.get("attemptId") != action.get("priorPackageAttemptId")
            or failed.get("packageInputSha256") != action.get("basePackageInputSha256")
            or not isinstance(failed.get("evidencePath"), str)
            or not isinstance(failed.get("evidenceSha256"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", failed.get("evidenceSha256", ""))
            or not isinstance(baseline_files, dict)
            or action.get("runId") is None
        ):
            raise ValueError("failed-candidate rebuild is missing its attempt evidence binding")
        if (
            not all(
                isinstance(name, str)
                and isinstance(digest, str)
                and re.fullmatch(r"[a-f0-9]{64}", digest)
                for name, digest in files.items()
            )
            or package_input_file_hashes(solution) != files
            or _identity_from_file_hashes(files) != action.get("packageInputSha256")
            or current_identity != action.get("packageInputSha256")
        ):
            raise ValueError(
                "failed-candidate rebuild inputs changed or no longer match the explicit approval"
            )
        _validate_package_input_file_manifest(
            baseline_files,
            expected_sha256=action["basePackageInputSha256"],
            expected_file_count=failed.get("packageInputFileCount"),
            label="failed V3.1 candidate input baseline",
        )
        evidence_path = content_path(solution, failed["evidencePath"])
        if (
            evidence_path.is_symlink()
            or not evidence_path.is_file()
            or hashlib.sha256(evidence_path.read_bytes()).hexdigest()
            != failed["evidenceSha256"]
        ):
            raise ValueError("failed-candidate evidence is missing or changed after planning")
        history = action.get("historicalEvidence") or {}
        archived_handoff_ref = history.get("failedCandidateEvidence")
        if not isinstance(archived_handoff_ref, str):
            raise ValueError("failed-candidate rebuild is missing its archived failure evidence")
        archived_handoff = content_path(solution, archived_handoff_ref)
        if (
            archived_handoff.is_symlink()
            or not archived_handoff.is_file()
            or hashlib.sha256(archived_handoff.read_bytes()).hexdigest()
            != failed["evidenceSha256"]
        ):
            raise ValueError("archived failed-candidate evidence is missing or modified")
        try:
            handoff = json.loads(archived_handoff.read_bytes())
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("archived failed-candidate evidence is invalid") from exc
        if (
            handoff.get("artifactKind") != "v3-1-arm-ttk-failure-final-handoff"
            or handoff.get("runId") != action.get("runId")
            or handoff.get("currentVersion") != target_version
            or handoff.get("currentPackageInput", {}).get("sha256")
            != action.get("basePackageInputSha256")
            or handoff.get("lastConsumedAction", {}).get("attemptId")
            != action.get("priorPackageAttemptId")
            or handoff.get("packageReportExists") is not False
        ):
            raise ValueError("archived failure evidence does not match the selected candidate")
        artifact_names = {
            "Package/mainTemplate.json": "mainTemplate.json",
            "Package/createUiDefinition.json": "createUiDefinition.json",
            "Package/testParameters.json": "testParameters.json",
            f"Package/{target_version}.zip": f"{target_version}.zip",
        }
        generated = handoff.get("generatedArtifacts") or {}
        for relative, archive_name in artifact_names.items():
            record = generated.get(relative) or {}
            reference = history.get(archive_name)
            archived_artifact = content_path(solution, reference) if isinstance(reference, str) else None
            if (
                archived_artifact is None
                or archived_artifact.is_symlink()
                or not archived_artifact.is_file()
                or hashlib.sha256(archived_artifact.read_bytes()).hexdigest()
                != record.get("sha256")
            ):
                raise ValueError(
                    f"archived failed V3.1 candidate artifact is missing or modified: {archive_name}"
                )
        _same_version_rebuild_scope(baseline_files, files, approved_changes)
        legacy_binding = action.get("legacyBaselineEvidence")
        if not isinstance(legacy_binding, dict):
            raise ValueError("failed-candidate rebuild is missing exact baseline comparison evidence")
        if (
            legacy_baseline_evidence is not None
            and str(legacy_baseline_evidence).replace("\\", "/") != legacy_binding.get("path")
        ):
            raise ValueError("baseline evidence differs from the evidence selected by the rebuild plan")
        reconstructed, evidence_binding = _legacy_baseline_evidence(
            solution,
            legacy_binding["path"],
            expected_current_sha256=action["packageInputSha256"],
            current_files=files,
            expected_prior_sha256=action["basePackageInputSha256"],
            expected_prior_file_count=failed.get("packageInputFileCount"),
            expected_evidence_sha256=legacy_binding.get("sha256"),
        )
        if reconstructed != baseline_files or evidence_binding != legacy_binding:
            raise ValueError("failed-candidate input baseline no longer matches its comparison evidence")
        for relative, digest in files.items():
            if Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise ValueError("same-version rebuild input manifest contains an unsafe path")
            backup = content_path(solution, f"{backup_root}/{relative}")
            if (
                backup.is_symlink()
                or not backup.is_file()
                or hashlib.sha256(backup.read_bytes()).hexdigest() != digest
            ):
                raise ValueError(
                    f"same-version rebuild input backup is missing or modified: {relative}"
                )
        return

    if target_version != successful.get("version"):
        raise ValueError(
            "same-version rebuild is missing its exact current version or input backup binding"
        )
    if (
        not all(
            isinstance(name, str)
            and isinstance(digest, str)
            and re.fullmatch(r"[a-f0-9]{64}", digest)
            for name, digest in files.items()
        )
        or package_input_file_hashes(solution) != files
        or _identity_from_file_hashes(files) != action.get("packageInputSha256")
        or current_identity != action.get("packageInputSha256")
        or action.get("basePackageInputSha256") != successful.get("packageInputSha256")
        or current_identity == successful.get("packageInputSha256")
        or action.get("priorPackageAttemptId") != successful.get("attemptId")
        or action.get("priorPackageReportSha256") != successful.get("packageReportSha256")
    ):
        raise ValueError(
            "same-version rebuild inputs changed or no longer match the explicit approval"
        )
    archived_report_reference = historical_evidence.get("packageReport")
    if not isinstance(archived_report_reference, str):
        raise ValueError("same-version rebuild is missing its archived prior package report")
    archived_report_path = content_path(solution, archived_report_reference)
    if (
        archived_report_path.is_symlink()
        or not archived_report_path.is_file()
        or hashlib.sha256(archived_report_path.read_bytes()).hexdigest()
        != action.get("priorPackageReportSha256")
    ):
        raise ValueError("archived prior V3.1 package report is missing or modified")
    try:
        archived_report = json.loads(archived_report_path.read_bytes())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("archived prior V3.1 package report is invalid") from exc
    if (
        archived_report.get("packager") != "V3.1"
        or archived_report.get("workflowRunId") != action.get("runId")
        or archived_report.get("packageAttemptId") != action.get("priorPackageAttemptId")
        or archived_report.get("version") != target_version
        or (archived_report.get("packageInputs") or {}).get("after", {}).get("sha256")
        != action.get("basePackageInputSha256")
    ):
        raise ValueError("archived prior V3.1 receipt does not match the rebuild plan")
    package_inputs = archived_report.get("packageInputs") or {}
    prior_inputs = package_inputs.get("after") or {}
    if prior_inputs.get("sha256") != action.get("basePackageInputSha256"):
        raise ValueError("archived prior V3.1 receipt has a mismatched input identity")
    baseline_manifest = prior_inputs.get("files")
    evidence_binding = action.get("legacyBaselineEvidence")
    evidence_reference: str | Path | None = None
    expected_evidence_sha256: str | None = None
    if evidence_binding is not None:
        if (
            not isinstance(evidence_binding, dict)
            or not isinstance(evidence_binding.get("path"), str)
            or not isinstance(evidence_binding.get("sha256"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", evidence_binding["sha256"])
        ):
            raise ValueError("same-version rebuild legacy baseline evidence binding is invalid")
        evidence_reference = evidence_binding["path"]
        expected_evidence_sha256 = evidence_binding["sha256"]
        if (
            legacy_baseline_evidence is not None
            and str(legacy_baseline_evidence).replace("\\", "/")
            != evidence_binding["path"]
        ):
            raise ValueError(
                "legacy baseline evidence differs from the evidence selected by the rebuild plan"
            )
    elif legacy_baseline_evidence is not None:
        evidence_reference = legacy_baseline_evidence

    if baseline_manifest is not None:
        if evidence_reference is not None:
            raise ValueError(
                "legacy baseline evidence is only accepted when the successful receipt "
                "does not contain a per-file manifest"
            )
        baseline_files = _validate_package_input_file_manifest(
            baseline_manifest,
            expected_sha256=action["basePackageInputSha256"],
            expected_file_count=prior_inputs.get("fileCount"),
            label="archived successful V3.1 receipt",
        )
    else:
        if evidence_reference is None:
            raise ValueError(
                "legacy successful V3.1 receipt has no per-file package-input baseline; "
                "provide exact receipt-bound --legacy-baseline-evidence or preserve a "
                "baseline manifest"
            )
        baseline_files, recovered_binding = _legacy_baseline_evidence(
            solution,
            evidence_reference,
            expected_current_sha256=action["packageInputSha256"],
            current_files=files,
            expected_prior_sha256=action["basePackageInputSha256"],
            expected_prior_file_count=prior_inputs.get("fileCount"),
            expected_evidence_sha256=expected_evidence_sha256,
        )
        if evidence_binding and recovered_binding != evidence_binding:
            raise ValueError("legacy baseline evidence binding does not match the rebuild plan")

    approved_changes = {
        name: digest
        for name, digest in approved_changes.items()
        if isinstance(name, str)
    }
    if len(approved_changes) != len(action.get("approvedChangedInputs") or {}):
        raise ValueError("same-version rebuild approved input paths are invalid")
    if any(
        digest is not None
        and (
            not isinstance(digest, str)
            or not re.fullmatch(r"[a-f0-9]{64}", digest)
        )
        for digest in approved_changes.values()
    ):
        raise ValueError("same-version rebuild approved input hashes are invalid")
    _same_version_rebuild_scope(baseline_files, files, approved_changes)

    recorded_hashes = archived_report.get("packageArtifactHashes") or {}
    for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip"):
        reference = historical_evidence.get(name)
        if not isinstance(reference, str):
            raise ValueError(f"same-version rebuild is missing archived {name} evidence")
        archived_artifact = content_path(solution, reference)
        if (
            archived_artifact.is_symlink()
            or not archived_artifact.is_file()
            or hashlib.sha256(archived_artifact.read_bytes()).hexdigest()
            != recorded_hashes.get(name)
        ):
            raise ValueError(f"archived prior V3.1 package artifact is missing or modified: {name}")
    for relative, digest in files.items():
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("same-version rebuild input manifest contains an unsafe path")
        backup = content_path(solution, f"{backup_root}/{relative}")
        if (
            backup.is_symlink()
            or not backup.is_file()
            or hashlib.sha256(backup.read_bytes()).hexdigest() != digest
        ):
            raise ValueError(
                f"same-version rebuild input backup is missing or modified: {relative}"
            )


def verify_same_version_content_rebuild(
    solution: str | Path,
    *,
    legacy_baseline_evidence: str | Path | None = None,
) -> dict[str, Any]:
    """Read-only verification of a pending or completed same-version rebuild."""
    root = Path(solution).expanduser().resolve()
    _state_path, state = _load(root)
    package_state = state.get("packaging") or {}
    pending = package_state.get("pendingReleaseAction") or {}
    completed_action = None
    successful = package_state.get("lastSuccessful") or {}
    if pending.get("actionType") in {
        "same-version-content-rebuild",
        "same-version-failed-candidate-rebuild",
    }:
        action = pending
        prior_successful = successful
        receipt_verified = False
    else:
        actions = package_state.get("releaseActions") or []
        action = next((
            item for item in reversed(actions)
            if item.get("actionType") in {
                "same-version-content-rebuild",
                "same-version-failed-candidate-rebuild",
            }
            and item.get("status") == "consumed"
            and item.get("packageInputSha256") == successful.get("packageInputSha256")
            and item.get("targetVersion") == successful.get("version")
        ), None)
        if action is None:
            raise ValueError(
                "selected run has no pending or successfully consumed same-version rebuild"
            )
        completed_action = action
        last_consumed = package_state.get("lastConsumedAction") or {}
        if (
            successful.get("packageSucceeded") is not True
            or successful.get("effectiveVersionBump") != "none"
            or successful.get("attemptId") != last_consumed.get("attemptId")
            or successful.get("packageInputSha256") != last_consumed.get("packageInputSha256")
            or last_consumed.get("packageSucceeded") is not True
        ):
            raise ValueError("completed same-version rebuild is not linked to its consumed V3.1 receipt")
        receipt_path = resolve_artifact_reference(root, successful.get("packageReport"))
        if (
            receipt_path.is_symlink()
            or not receipt_path.is_file()
            or hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            != successful.get("packageReportSha256")
        ):
            raise ValueError("completed same-version V3.1 receipt is missing or modified")
        try:
            receipt = json.loads(receipt_path.read_bytes())
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("completed same-version V3.1 receipt is invalid") from exc
        current_files = package_input_file_hashes(root)
        current_identity = _identity_from_file_hashes(current_files)
        receipt_inputs = receipt.get("packageInputs") or {}
        before = receipt_inputs.get("before") or {}
        after = receipt_inputs.get("after") or {}
        if (
            receipt.get("status") != "passed"
            or receipt.get("packager") != "V3.1"
            or receipt.get("workflowRunId") != state.get("runId")
            or receipt.get("packageAttemptId") != successful.get("attemptId")
            or receipt.get("version") != action.get("targetVersion")
            or receipt.get("effectiveVersionBump") != "none"
            or receipt.get("effectiveTargetVersion") is not None
            or current_identity != action.get("packageInputSha256")
            or before.get("sha256") != current_identity
            or after.get("sha256") != current_identity
            or after.get("fileCount") != len(current_files)
        ):
            raise ValueError("completed same-version receipt does not bind the approved current inputs")
        candidate_manifest = after.get("files")
        if candidate_manifest is not None and _validate_package_input_file_manifest(
            candidate_manifest,
            expected_sha256=current_identity,
            expected_file_count=len(current_files),
            label="completed same-version V3.1 receipt",
        ) != current_files:
            raise ValueError("completed same-version receipt file manifest differs from current inputs")
        artifact_hashes = receipt.get("packageArtifactHashes") or {}
        for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip"):
            reference = receipt.get(name)
            if not isinstance(reference, str) or not reference:
                raise ValueError(f"completed same-version receipt is missing {name}")
            artifact_path = resolve_artifact_reference(root, reference)
            if (
                artifact_path.is_symlink()
                or not artifact_path.is_file()
                or hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                != artifact_hashes.get(name)
            ):
                raise ValueError(f"completed same-version package artifact is missing or modified: {name}")
        archived_report = action.get("historicalEvidence", {}).get("packageReport")
        if action.get("actionType") == "same-version-failed-candidate-rebuild":
            prior_successful = {}
        else:
            prior_successful = {
                "packageSucceeded": True,
                "version": action.get("targetVersion"),
                "packageInputSha256": action.get("basePackageInputSha256"),
                "attemptId": action.get("priorPackageAttemptId"),
                "packageReportSha256": action.get("priorPackageReportSha256"),
                "packageReport": archived_report,
            }
        receipt_verified = True

    if (
        successful.get("packageSucceeded") is not True
        and not (
            pending.get("actionType") == "same-version-failed-candidate-rebuild"
            and not receipt_verified
        )
    ):
        raise ValueError("same-version rebuild verification requires its successful prior V3.1 receipt")
    current_identity = package_input_identity(root)["sha256"]
    _validate_same_version_content_rebuild_inputs(
        root,
        action,
        current_identity,
        solution_data_version(root),
        prior_successful,
        legacy_baseline_evidence,
    )
    return {
        "runId": state.get("runId"),
        "status": "verified",
        "targetVersion": action.get("targetVersion"),
        "packageInputSha256": action.get("packageInputSha256"),
        "changedInputs": sorted(action.get("approvedChangedInputs") or {}),
        "receiptVerified": receipt_verified,
        "packageReport": successful.get("packageReport") if completed_action else None,
        "stateChanged": False,
        "workflowCompletionClaimed": False,
    }


def plan_release_notes_refresh(
    solution: str | Path,
    *,
    release_date: str | None = None,
    change_history: str,
    expected_package_input_sha256: str,
) -> dict[str, Any]:
    """Authorize only an exact ReleaseNotes row refresh without incrementing package version."""
    from .release_notes import resolve_release_date

    if not re.fullmatch(r"[a-f0-9]{64}", expected_package_input_sha256 or ""):
        raise ValueError("expected package input identity must be a lowercase SHA-256")
    resolved_release_date = resolve_release_date(release_date)
    root = Path(solution).expanduser().resolve()
    with _state_writer_lock(root) as path:
        loaded_path, state = _load(root)
        if loaded_path != path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        if state.get("context", {}).get("profileSelectionConfirmed") is not True:
            raise ValueError("release-notes refresh requires explicit profile selection")
        if state.get("context", {}).get("workflowProfile") != "authoring":
            raise ValueError("same-release ReleaseNotes refresh is supported only for Authoring")
        if state["stages"]["validation"]["status"] != "passed":
            raise ValueError("release-notes refresh requires passed Authoring validation")
        validation_artifacts = state["stages"]["validation"].get("artifacts") or {}
        if (
            validation_artifacts.get("validationMode") != "offline-authoring"
            or validation_artifacts.get("runtimeStatus") != "not-run"
        ):
            raise ValueError("release-notes refresh requires current offline Authoring validation")
        _validate_offline_authoring_gates(root, path, state)
        if state.get("authoring") and state["authoring"]["status"] != "active":
            raise ValueError("stopped or conflicted authoring runs cannot refresh release notes")
        package_state = state.get("packaging") or {}
        if package_state.get("pendingReleaseAction"):
            raise ValueError("another package release action is already pending")
        if (package_state.get("currentAttempt") or {}).get("status") == "running":
            raise ValueError("cannot plan a ReleaseNotes refresh while V3.1 packaging is running")
        successful = package_state.get("lastSuccessful") or {}
        if not successful.get("packageSucceeded"):
            raise ValueError("ReleaseNotes refresh requires a prior successful V3.1 package")
        _verify_current_package_state(root, state)
        files = package_input_file_hashes(root)
        base_identity = _identity_from_file_hashes(files)
        if (
            base_identity != successful.get("packageInputSha256")
            or base_identity != expected_package_input_sha256
        ):
            raise ValueError("package inputs must exactly match the prior successful V3.1 build")
        current_version = solution_data_version(root)
        if current_version != successful.get("version"):
            raise ValueError("same-release notes refresh must retain the last packaged version")
        notes_path, original_notes_sha, expected_notes_sha = _release_notes_refresh_proposal(
            root, release_date=resolved_release_date, change_history=change_history,
        )
        relative_notes = notes_path.relative_to(root).as_posix()
        expected_files = dict(files)
        expected_files[relative_notes] = expected_notes_sha
        expected_identity = _identity_from_file_hashes(expected_files)
        historical_evidence = _archive_package_evidence(root, successful)
        selected_at = _utc_now()
        action = {
            "actionType": "release-notes-refresh",
            "versionBump": "none",
            "basePackageInputSha256": base_identity,
            "packageInputSha256": expected_identity,
            "releaseNotesPath": relative_notes,
            "releaseNotesOriginalSha256": original_notes_sha,
            "releaseNotesExpectedSha256": expected_notes_sha,
            "releaseNotesDate": resolved_release_date,
            "releaseNotesVersion": current_version,
            "releaseNotesChangeHistory": change_history.strip(),
            "packageInputFilesBefore": files,
            "selectedAt": selected_at,
        }
        package_state = state.setdefault("packaging", {})
        package_state.setdefault("releaseActions", []).append({
            **action,
            "status": "selected",
            "historicalEvidence": historical_evidence,
        })
        package_state["pendingReleaseAction"] = action
        for name in ("packaging", "deployment", "mockIngestion", "alertParity", "report"):
            stage = state["stages"][name]
            if stage["status"] != "notRequired":
                stage.update({
                    "status": "blocked",
                    "completedAt": None,
                    "message": (
                        "An explicitly approved same-version ReleaseNotes refresh is pending; "
                        "only the exact planned ReleaseNotes row may change before V3.1 rebuild."
                    ),
                })
        state["workflowStatus"] = "blocked"
        _write_unlocked(path, state)
        return {
            "runId": state["runId"],
            "version": current_version,
            "packageInputSha256Before": base_identity,
            "packageInputSha256After": expected_identity,
            "releaseNotesPath": relative_notes,
            "releaseDate": resolved_release_date,
            "releaseNotesDate": resolved_release_date,
            "releaseNotesChangeHistory": change_history.strip(),
            "next": "add the exact approved row to ReleaseNotes.md, then package-v3-1 --version-bump none",
            "workflowStatus": state["workflowStatus"],
        }


def plan_same_version_content_rebuild(
    solution: str | Path,
    *,
    target_version: str,
    changed_inputs: list[str],
    expected_package_input_sha256: str,
    legacy_baseline_evidence: str | Path | None = None,
    failed_candidate_evidence: str | Path | None = None,
) -> dict[str, Any]:
    """Authorize one exact-input V3.1 rebuild without changing the solution version."""
    validate_v31_target_version(target_version)
    if not re.fullmatch(r"[a-f0-9]{64}", expected_package_input_sha256 or ""):
        raise ValueError("expected package input identity must be a lowercase SHA-256")

    root = Path(solution).expanduser().resolve()
    with _state_writer_lock(root) as path:
        loaded_path, state = _load(root)
        if loaded_path != path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        if state.get("context", {}).get("profileSelectionConfirmed") is not True:
            raise ValueError("same-version rebuild requires explicit profile selection")
        if state.get("context", {}).get("workflowProfile") != "authoring":
            raise ValueError("same-version content rebuild is supported only for Authoring")
        if state["stages"]["validation"]["status"] != "passed":
            raise ValueError(
                "same-version content rebuild requires passed Authoring validation"
            )
        validation_artifacts = state["stages"]["validation"].get("artifacts") or {}
        if (
            validation_artifacts.get("validationMode") != "offline-authoring"
            or validation_artifacts.get("runtimeStatus") != "not-run"
        ):
            raise ValueError(
                "same-version content rebuild requires current offline Authoring validation"
            )
        _validate_offline_authoring_gates(root, path, state)
        if state.get("authoring") and state["authoring"]["status"] != "active":
            raise ValueError("stopped or conflicted authoring runs cannot rebuild a package")
        _yolo_package_readiness(root, path, state)
        if verify_applied_package_selection(root, str(state.get("runId") or "")):
            raise ValueError(
                "same-version content rebuild requires the complete solution package; "
                "evidence-based package selections are not supported"
            )

        current_version = solution_data_version(root)
        if current_version != target_version:
            raise ValueError(
                "same-version rebuild target must exactly match the current solution version"
            )
        package_state = state.get("packaging") or {}
        if package_state.get("pendingReleaseAction"):
            raise ValueError("another package release action is already pending")
        if (package_state.get("currentAttempt") or {}).get("status") == "running":
            raise ValueError("cannot plan a same-version rebuild while V3.1 packaging is running")
        successful = package_state.get("lastSuccessful") or {}
        files = package_input_file_hashes(root)
        current_identity = _identity_from_file_hashes(files)
        if current_identity != expected_package_input_sha256:
            raise ValueError(
                "package inputs changed after same-version rebuild approval; refresh status "
                "and approve the exact current input identity"
            )
        failed_candidate = successful.get("packageSucceeded") is not True
        failure_handoff: dict[str, Any] | None = None
        failure_evidence_path: Path | None = None
        failed_candidate_binding: dict[str, Any] | None = None
        if not failed_candidate:
            if failed_candidate_evidence is not None:
                raise ValueError(
                    "--failed-candidate-evidence is only valid when no successful V3.1 receipt exists"
                )
            if successful.get("effectiveVersionBump") not in {
                "patch", "minor", "major", "none",
            }:
                raise ValueError("prior V3.1 package receipt has no valid version action")
            historical_report = _validate_historical_package_receipt(
                root, state, successful, target_version,
            )
            last_consumed = package_state.get("lastConsumedAction") or {}
            if (
                last_consumed.get("packageSucceeded") is not True
                or last_consumed.get("attemptId") != successful.get("attemptId")
                or last_consumed.get("packageInputSha256") != successful.get("packageInputSha256")
                or last_consumed.get("version") not in (None, target_version)
            ):
                raise ValueError(
                    "prior package receipt is not linked to the current run's successful "
                    "consumed-action chain"
                )
            prior_identity = successful.get("packageInputSha256")
            if not isinstance(prior_identity, str) or prior_identity == current_identity:
                raise ValueError(
                    "same-version content rebuild requires changed package inputs since the "
                    "prior successful V3.1 build"
                )
            package_inputs = historical_report.get("packageInputs") or {}
            prior_inputs = package_inputs.get("after") or {}
            if prior_inputs.get("sha256") != prior_identity:
                raise ValueError("prior successful receipt has a mismatched package-input identity")
            legacy_evidence_binding = None
            if prior_inputs.get("files") is None:
                if legacy_baseline_evidence is None:
                    raise ValueError(
                        "legacy successful V3.1 receipt has no per-file package-input baseline; "
                        "provide exact receipt-bound --legacy-baseline-evidence"
                    )
                baseline_files, legacy_evidence_binding = _legacy_baseline_evidence(
                    root,
                    legacy_baseline_evidence,
                    expected_current_sha256=current_identity,
                    current_files=files,
                    expected_prior_sha256=prior_identity,
                    expected_prior_file_count=prior_inputs.get("fileCount"),
                )
            else:
                if legacy_baseline_evidence is not None:
                    raise ValueError(
                        "legacy baseline evidence is only accepted for receipts without "
                        "a per-file manifest"
                    )
                baseline_files = _validate_package_input_file_manifest(
                    prior_inputs.get("files"),
                    expected_sha256=prior_identity,
                    expected_file_count=prior_inputs.get("fileCount"),
                    label="prior successful V3.1 receipt",
                )
            prior_attempt_id = successful["attemptId"]
            prior_report_sha256 = successful["packageReportSha256"]
        else:
            if failed_candidate_evidence is None:
                raise ValueError(
                    "same-version rebuild requires a prior successful V3.1 receipt or "
                    "explicit failed-candidate evidence"
                )
            if legacy_baseline_evidence is None:
                raise ValueError(
                    "failed V3.1 candidate has no per-file input manifest; provide exact "
                    "--legacy-baseline-evidence that reconstructs its complete input tree"
                )
            failure_evidence_path, failure_handoff = _read_failed_candidate_evidence(
                root, state, target_version, failed_candidate_evidence,
            )
            candidate_inputs = failure_handoff["currentPackageInput"]
            prior_identity = candidate_inputs["sha256"]
            if prior_identity == current_identity:
                raise ValueError(
                    "failed-candidate rebuild requires changed package inputs since the failed attempt"
                )
            baseline_files, legacy_evidence_binding = _legacy_baseline_evidence(
                root,
                legacy_baseline_evidence,
                expected_current_sha256=current_identity,
                current_files=files,
                expected_prior_sha256=prior_identity,
                expected_prior_file_count=candidate_inputs["fileCount"],
            )
            failed_candidate_binding = {
                "attemptId": failure_handoff["lastConsumedAction"]["attemptId"],
                "packageInputSha256": prior_identity,
                "packageInputFileCount": candidate_inputs["fileCount"],
                "evidencePath": str(failure_evidence_path.relative_to(root)).replace("\\", "/"),
                "evidenceSha256": hashlib.sha256(failure_evidence_path.read_bytes()).hexdigest(),
            }
            prior_attempt_id = failed_candidate_binding["attemptId"]
            prior_report_sha256 = None
        normalized_changed_inputs = [
            name.replace("\\", "/") if isinstance(name, str) else name
            for name in changed_inputs
        ]
        if (
            not normalized_changed_inputs
            or any(not isinstance(name, str) for name in normalized_changed_inputs)
            or len(set(normalized_changed_inputs)) != len(normalized_changed_inputs)
            or any(
                not name
                or name.replace("\\", "/") != name
                or Path(name).is_absolute()
                or ".." in Path(name).parts
                or Path(name).as_posix() != name
                for name in normalized_changed_inputs
            )
        ):
            raise ValueError(
                "same-version rebuild requires a unique, nonempty list of safe package-input paths"
            )
        approved_changes = {
            name: files.get(name) for name in normalized_changed_inputs
        }
        _same_version_rebuild_scope(baseline_files, files, approved_changes)
        action_type = (
            "same-version-failed-candidate-rebuild"
            if failed_candidate else "same-version-content-rebuild"
        )
        if any(
            action.get("actionType") == action_type
            and action.get("packageInputSha256") == current_identity
            for action in package_state.get("releaseActions", [])
        ):
            raise ValueError(
                "a same-version rebuild action was already selected for these package inputs"
            )
        backup_id = str(uuid.uuid4())
        backup_root = (
            path.parent / "Reports" / "package-history" / backup_id / "input-backup"
        )
        if failed_candidate:
            archive_root = path.parent / "Reports" / "package-history" / backup_id / "failed-candidate"
            historical_evidence = _archive_failed_candidate_evidence(
                root,
                failure_evidence_path,
                failure_handoff,
                archive_root,
            )
        else:
            historical_evidence = _archive_package_evidence(root, successful)
        current_files = package_input_file_hashes(root)
        if current_files != files:
            raise ValueError("package inputs changed while the rebuild backup was prepared")
        for relative, digest in files.items():
            source = content_path(root, relative)
            if source.is_symlink() or not source.is_file():
                raise ValueError(f"package input cannot be backed up safely: {relative}")
            if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
                raise ValueError(f"package input changed while backing up: {relative}")
            destination = backup_root.joinpath(*Path(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
                raise ValueError(f"package input backup verification failed: {relative}")
        if package_input_file_hashes(root) != files:
            raise ValueError("package inputs changed while the rebuild backup was prepared")
        relative_backup_root = backup_root.relative_to(root).as_posix()
        historical_evidence["inputBackupRoot"] = relative_backup_root

        selected_at = _utc_now()
        action = {
            "actionType": action_type,
            "versionBump": "none",
            "runId": state["runId"],
            "targetVersion": target_version,
            "basePackageInputSha256": prior_identity,
            "packageInputSha256": current_identity,
            "packageInputFilesBefore": files,
            "approvedChangedInputs": approved_changes,
            "priorPackageAttemptId": prior_attempt_id,
            "inputBackupRoot": relative_backup_root,
            "backupId": backup_id,
            "selectedAt": selected_at,
            "historicalEvidence": historical_evidence,
        }
        if failed_candidate:
            action["basePackageInputFiles"] = baseline_files
            action["failedCandidate"] = failed_candidate_binding
        else:
            action["priorPackageReportSha256"] = prior_report_sha256
        if legacy_evidence_binding is not None:
            action["legacyBaselineEvidence"] = legacy_evidence_binding
        if legacy_evidence_binding is not None:
            action["legacyBaselineEvidence"] = legacy_evidence_binding
        release_action = {
            **action,
            "status": "selected",
            "historicalEvidence": historical_evidence,
        }
        package_state.setdefault("releaseActions", []).append(release_action)
        package_state["pendingReleaseAction"] = action
        for name in ("packaging", "deployment", "mockIngestion", "alertParity", "report"):
            stage = state["stages"][name]
            if stage["status"] != "notRequired":
                stage.update({
                    "status": "blocked",
                    "completedAt": None,
                    "message": (
                        "An explicitly approved same-version content rebuild is pending; "
                        "the exact backed-up package inputs and current offline Authoring "
                        "gates must remain unchanged."
                    ),
                })
        state["workflowStatus"] = "blocked"
        _write_unlocked(path, state)
        return {
            "runId": state["runId"],
            "version": target_version,
            "priorPackageInputSha256": prior_identity,
            "packageInputSha256": current_identity,
            "approvedChangedInputs": action["approvedChangedInputs"],
            "inputBackupRoot": relative_backup_root,
            "historicalEvidence": historical_evidence,
            "failedCandidate": failed_candidate_binding,
            "legacyBaselineEvidence": legacy_evidence_binding,
            "next": "package-v3-1 --version-bump none",
            "workflowStatus": state["workflowStatus"],
        }


def plan_new_package_release(
    solution: str | Path,
    *,
    version_bump: str | None = None,
    target_version: str | None = None,
    expected_package_input_sha256: str,
) -> dict[str, Any]:
    """Explicitly reopen a stale package stage for one versioned V3.1 release action."""
    if (version_bump is None) == (target_version is None):
        raise ValueError("select exactly one version bump or target version")
    if target_version is not None:
        validate_v31_target_version(target_version)
        version_bump = "none"
        action_type = "target-version"
    else:
        if version_bump not in {"patch", "minor", "major"}:
            raise ValueError("new package release action must be patch, minor, or major")
        action_type = "version-bump"
    if not re.fullmatch(r"[a-f0-9]{64}", expected_package_input_sha256 or ""):
        raise ValueError("expected package input identity must be a lowercase SHA-256")

    root = Path(solution).expanduser().resolve()
    validate_v31_effective_version(solution_data_version(root), version_bump, target_version)
    with _state_writer_lock(root) as path:
        loaded_path, state = _load(root)
        if loaded_path != path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        if state.get("context", {}).get("profileSelectionConfirmed") is not True:
            raise ValueError("release planning requires explicit profile selection")
        if state.get("authoring") and state["authoring"]["status"] != "active":
            raise ValueError("stopped or conflicted YOLO runs cannot plan a package release")
        selection_evidence = verify_applied_package_selection(
            root, str(state["runId"]),
        )
        partial_selection = bool(
            selection_evidence
            and selection_evidence["plan"].get("summary", {}).get("outcome") == "partial"
        )
        validation_status = state["stages"]["validation"]["status"]
        partial_release_ready = (
            partial_selection
            and validation_status == "blocked"
            and not state.get("authoring")
            and state["stages"]["conversion"]["status"] == "passed"
        )
        complete_selection = bool(
            selection_evidence
            and selection_evidence["plan"].get("summary", {}).get("outcome") == "complete"
        )
        complete_release_ready = (
            complete_selection
            and validation_status == "passed"
            and state["stages"]["conversion"]["status"] == "passed"
        )
        validation_artifacts = state["stages"]["validation"].get("artifacts") or {}
        offline_authoring_ready = (
            state["context"].get("workflowProfile") == "authoring"
            and validation_status == "passed"
            and validation_artifacts.get("runtimeStatus") == "not-run"
            and validation_artifacts.get("validationMode") == "offline-authoring"
        )
        if offline_authoring_ready:
            _validate_offline_authoring_gates(root, path, state)
        first_release_ready = (
            partial_release_ready or complete_release_ready or offline_authoring_ready
        )
        _yolo_package_readiness(
            root,
            path,
            state,
            allow_partial_selection=partial_release_ready,
        )
        if any(
            state["stages"][dependency]["status"] != "passed"
            for dependency in _dependencies(state, "packaging")
            if not (dependency == "validation" and partial_release_ready)
        ):
            raise ValueError("package release planning is blocked by unfinished prerequisites")
        if not first_release_ready and validation_status != "passed":
            raise ValueError(
                "package release planning requires passed validation or a fresh, "
                "applied partial package selection with all exclusions accounted for"
            )

        current_identity = package_input_identity(root)["sha256"]
        if current_identity != expected_package_input_sha256:
            raise ValueError(
                "package inputs changed after release action selection; refresh status "
                "and explicitly select an action for the current input identity"
            )
        if target_version is not None and solution_data_version(root) == target_version:
            raise ValueError(
                "target version already matches the solution; a new release action must "
                "change the version"
            )

        package_state = state.get("packaging")
        if not isinstance(package_state, dict):
            package_state = {
                "schemaVersion": "1.0.0",
                "lastSuccessful": None,
                "lastConsumedAction": None,
                "currentAttempt": None,
                "releaseActions": [],
                "pendingReleaseAction": None,
            }
            state["packaging"] = package_state
        package_state.setdefault("releaseActions", [])
        package_state.setdefault("pendingReleaseAction", None)
        if (package_state.get("currentAttempt") or {}).get("status") == "running":
            raise ValueError("cannot plan a new release while V3.1 packaging is running")
        prior = package_state.get("lastSuccessful")
        last_consumed = package_state.get("lastConsumedAction") or {}
        if prior is None and last_consumed.get("bumpConsumed") is True:
            if last_consumed.get("packageInputSha256") == current_identity:
                raise ValueError(
                    "the initial version action was consumed by a failed build; retry "
                    "with --version-bump none for the matching package inputs"
                )
            raise ValueError(
                "package inputs changed after the initial version action was consumed; "
                "the failed build's retry rules must be resolved before planning a new release"
            )
        if prior is None and not first_release_ready:
            raise ValueError(
                "first release planning without a prior successful V3.1 package requires "
                "fresh passed validation with an applied complete selection or explicit "
                "offline Authoring evidence, or an eligible partial selection with blocked validation"
            )
        if prior and current_identity == prior.get("packageInputSha256"):
            raise ValueError(
                "package inputs still match the successful V3.1 package; "
                "a new release action is not warranted"
            )
        pending = package_state.get("pendingReleaseAction")
        if pending:
            if pending.get("packageInputSha256") == current_identity:
                raise ValueError(
                    "a release action is already selected for these package inputs; "
                    "continue package-v3-1 with that exact action"
                )
            raise ValueError(
                "package inputs changed after the pending release action was selected"
            )
        if any(
            item.get("packageInputSha256") == current_identity
            and (
                (
                    action_type == "target-version"
                    and item.get("actionType") == "target-version"
                    and item.get("targetVersion") == target_version
                )
                or (
                    action_type == "version-bump"
                    and item.get("versionBump") == version_bump
                    and item.get("actionType") != "target-version"
                )
            )
            for item in package_state["releaseActions"]
        ):
            raise ValueError("this explicit release action was already consumed for these inputs")

        selected_at = _utc_now()
        historical_evidence = (
            _archive_package_evidence(root, prior) if prior else {}
        )
        selected_action = {
            "versionBump": version_bump,
            "packageInputSha256": current_identity,
            "selectedAt": selected_at,
            "status": "selected",
            "historicalEvidence": historical_evidence,
        }
        pending_action = {
            "versionBump": version_bump,
            "packageInputSha256": current_identity,
            "selectedAt": selected_at,
        }
        if target_version is not None:
            selected_action.update({
                "actionType": action_type,
                "targetVersion": target_version,
            })
            pending_action.update({
                "actionType": action_type,
                "targetVersion": target_version,
            })
        package_state["releaseActions"].append(selected_action)
        package_state["pendingReleaseAction"] = pending_action
        for name in ("packaging", "deployment", "mockIngestion", "alertParity", "report"):
            stage = state["stages"][name]
            if stage["status"] != "notRequired":
                stage.update({
                    "status": "blocked",
                    "completedAt": None,
                    "message": (
                        "Package inputs changed after the prior V3.1 release. "
                        "Prior artifacts and evidence are historical; an explicit "
                        "new release action was selected."
                    ),
                })
        state["workflowStatus"] = "blocked"
        _write_unlocked(path, state)
        return {
            "runId": state["runId"],
            "versionBump": version_bump,
            "targetVersion": target_version,
            "packageInputSha256": current_identity,
            "selectedAt": selected_at,
            "next": _next_stage_name(state),
            "workflowStatus": state["workflowStatus"],
        }


def package_workflow_v3_1(
    solution: str | Path,
    *,
    requested_version_bump: str,
    requested_target_version: str | None = None,
    toolkit_root: str | Path | None = None,
    legacy_baseline_evidence: str | Path | None = None,
) -> dict[str, Any]:
    """Package one current workflow attempt and persist fresh, hash-bound evidence."""
    if requested_version_bump not in {"none", "patch", "minor", "major"}:
        raise ValueError("version bump must be none, patch, minor, or major")
    if requested_target_version is not None:
        validate_v31_target_version(requested_target_version)
        if requested_version_bump != "none":
            raise ValueError("target version cannot be combined with a version bump")
    root = Path(solution).expanduser().resolve()
    validate_v31_effective_version(
        solution_data_version(root), requested_version_bump, requested_target_version,
    )
    with _state_writer_lock(root) as path:
        loaded_path, state = _load(root)
        if loaded_path != path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        if not state.get("runId"):
            raise ValueError("workflow packaging requires an explicitly selected run")
        if state["context"].get("profileSelectionConfirmed") is not True:
            raise ValueError("workflow packaging requires explicit profile selection")
        workbook_workflow.verify_inventory(root, state)
        if workbook_workflow.enabled(state):
            workbook_workflow.validate_evidence(root, state)
        selection_evidence = verify_applied_package_selection(
            root, str(state["runId"]),
        )
        validation_status = state["stages"]["validation"]["status"]
        partial_selection = bool(
            selection_evidence
            and selection_evidence["plan"].get("summary", {}).get("outcome") == "partial"
        )
        if validation_status != "passed" and not (
            partial_selection
            and validation_status == "blocked"
            and not state.get("authoring")
        ):
            raise ValueError(
                "workflow packaging requires passed validation or a fresh, applied "
                "partial package selection with all exclusions accounted for"
            )
        validation_artifacts = state["stages"]["validation"].get("artifacts") or {}
        offline_authoring_package = (
            state["context"].get("workflowProfile") == "authoring"
            and validation_status == "passed"
            and validation_artifacts.get("runtimeStatus") == "not-run"
            and validation_artifacts.get("validationMode") == "offline-authoring"
        )
        if offline_authoring_package:
            _validate_offline_authoring_gates(root, path, state)
        _yolo_package_readiness(
            root,
            path,
            state,
            allow_partial_selection=partial_selection,
        )
        if state.get("authoring") and state["authoring"]["status"] != "active":
            raise ValueError("stopped or conflicted YOLO runs cannot be packaged")
        campaign_budget = state.get("budget")
        if not campaign_budget and state.get("authoring"):
            raise ValueError(
                "YOLO V3.1 package builds require a persisted campaign budget; resume "
                "workflow-init with its explicit --campaign-id to link this run conservatively"
            )
        if campaign_budget and campaign_budget.get("status") == "stopped":
            raise ValueError(
                "budget-stopped workflow runs cannot be resumed by an extension; "
                "initialize an explicitly linked replacement run"
            )
        if campaign_budget:
            current_inventory_hash, _ = _budget_source_inventory(
                root,
                yolo=bool(state.get("authoring")),
            )
            if current_inventory_hash != campaign_budget["inventorySha256"]:
                raise ValueError(
                    "campaign frozen source inventory changed; package inputs are no longer "
                    "bound to this campaign"
                )
            budget_summary(
                root,
                campaign_budget["campaignId"],
                expected_inventory=current_inventory_hash,
            )
        pending_dependencies = [
            dependency
            for dependency in _dependencies(state, "packaging")
            if state["stages"][dependency]["status"] != "passed"
        ]
        if pending_dependencies and not (
            pending_dependencies == ["validation"]
            and partial_selection
            and validation_status == "blocked"
            and not state.get("authoring")
        ):
            raise ValueError("workflow packaging is blocked by unfinished prerequisites")

        inputs = package_input_identity(root)
        package_state = state.get("packaging") or {}
        pending_release = package_state.get("pendingReleaseAction") or {}
        notes_refresh = pending_release.get("actionType") == "release-notes-refresh"
        same_version_rebuild = pending_release.get("actionType") in {
            "same-version-content-rebuild",
            "same-version-failed-candidate-rebuild",
        }
        if legacy_baseline_evidence is not None and not same_version_rebuild:
            raise ValueError(
                "--legacy-baseline-evidence is only valid for a pending same-version rebuild"
            )
        if notes_refresh and not offline_authoring_package:
            raise ValueError(
                "same-release ReleaseNotes refresh requires offline Authoring validation; "
                "Qualification must use its runtime-bound release gates"
            )
        if same_version_rebuild and not offline_authoring_package:
            raise ValueError(
                "same-version content rebuild requires offline Authoring validation; "
                "Qualification must use its runtime-bound release gates"
            )
        if same_version_rebuild and selection_evidence:
            raise ValueError(
                "same-version content rebuild requires the complete solution package; "
                "evidence-based package selections are not supported"
            )
        if notes_refresh and requested_version_bump != "none":
            raise ValueError(
                "approved same-release ReleaseNotes refresh must be rebuilt with "
                "--version-bump none"
            )
        if same_version_rebuild and (
            requested_version_bump != "none" or requested_target_version is not None
        ):
            raise ValueError(
                "approved same-version content rebuild must use "
                "--version-bump none without --target-version"
            )
        successful_package = package_state.get("lastSuccessful") or {}
        current_successful_no_bump_receipt = bool(
            successful_package.get("packageSucceeded") is True
            and successful_package.get("effectiveVersionBump") == "none"
            and successful_package.get("packageInputSha256") == inputs["sha256"]
            and (package_state.get("lastConsumedAction") or {}).get("effectiveVersionBump") == "none"
            and any(
                action.get("actionType") in {
                    "release-notes-refresh",
                    "same-version-content-rebuild",
                    "same-version-failed-candidate-rebuild",
                }
                and action.get("status") == "consumed"
                and action.get("packageInputSha256") == inputs["sha256"]
                for action in package_state.get("releaseActions", [])
            )
        )
        if current_successful_no_bump_receipt:
            _verify_current_package_state(root, state)
        if campaign_budget:
            prior_package_attempts = package_history(
                root, campaign_budget["campaignId"],
            )
            last_consumed = next((
                item for item in reversed(prior_package_attempts)
                if item["finish"]
                and (item["finish"].get("completionMetadata") or {}).get("bumpConsumed") is True
            ), None)
            if last_consumed:
                prior_after = (
                    last_consumed["finish"].get("completionMetadata") or {}
                ).get("packageInputSha256After")
                if (
                    not (notes_refresh or same_version_rebuild)
                    and not current_successful_no_bump_receipt
                    and prior_after == inputs["sha256"]
                    and (
                        requested_version_bump != "none"
                        or requested_target_version is not None
                    )
                ):
                    raise ValueError(
                        "a campaign version action was already consumed for unchanged "
                        "package inputs; rebuild with --version-bump none"
                    )
                if (
                    not (notes_refresh or same_version_rebuild)
                    and not current_successful_no_bump_receipt
                    and prior_after != inputs["sha256"]
                    and requested_version_bump == "none"
                    and requested_target_version is None
                ):
                    raise ValueError(
                        "campaign package inputs changed after the consumed version action; "
                        "select an explicit new version bump"
                    )
        package_state = state.get("packaging") or {
            "schemaVersion": "1.0.0",
            "lastSuccessful": None,
            "lastConsumedAction": None,
            "currentAttempt": None,
            "releaseActions": [],
            "pendingReleaseAction": None,
        }
        package_state.setdefault("releaseActions", [])
        package_state.setdefault("pendingReleaseAction", None)
        pending_release = package_state.get("pendingReleaseAction")
        notes_refresh = bool(
            pending_release
            and pending_release.get("actionType") == "release-notes-refresh"
        )
        same_version_rebuild = bool(
            pending_release
            and pending_release.get("actionType") in {
                "same-version-content-rebuild",
                "same-version-failed-candidate-rebuild",
            }
        )
        previous = package_state.get("lastSuccessful")
        previous_successful = previous
        last_consumed = package_state.get("lastConsumedAction") or {}
        if notes_refresh:
            _validate_release_notes_refresh_inputs(
                root, pending_release, inputs["sha256"],
            )
        if same_version_rebuild:
            _validate_same_version_content_rebuild_inputs(
                root,
                pending_release,
                inputs["sha256"],
                solution_data_version(root),
                previous or {},
                legacy_baseline_evidence,
            )
        failed_consumed_retry = (
            last_consumed.get("bumpConsumed") is True
            and last_consumed.get("packageSucceeded") is False
            and last_consumed.get("packageInputSha256") == inputs["sha256"]
        )
        if previous is not None and inputs["sha256"] != previous.get("packageInputSha256"):
            if not pending_release and not failed_consumed_retry:
                raise ValueError(
                    "package inputs changed after V3.1 packaging; select an explicit "
                    "new release action before rebuilding"
                )
            if pending_release and (
                pending_release.get("packageInputSha256") != inputs["sha256"]
                or pending_release.get("versionBump") != requested_version_bump
                or (
                    pending_release.get("actionType") == "target-version"
                    and pending_release.get("targetVersion") != requested_target_version
                )
                or (
                    pending_release.get("actionType") != "target-version"
                    and requested_target_version is not None
                )
            ):
                raise ValueError(
                    "package input identity or version action differs from the explicitly "
                    "selected new release action"
                )
        elif pending_release and (
            pending_release.get("packageInputSha256") != inputs["sha256"]
            or pending_release.get("versionBump") != requested_version_bump
            or (
                pending_release.get("actionType") == "target-version"
                and pending_release.get("targetVersion") != requested_target_version
            )
            or (
                pending_release.get("actionType") != "target-version"
                and requested_target_version is not None
            )
        ):
            raise ValueError(
                "pending release action no longer matches changed package inputs"
            )
        if (
            previous is not None
            and inputs["sha256"] == previous.get("packageInputSha256")
            and (
                requested_version_bump != "none"
                or requested_target_version is not None
            )
        ):
            raise ValueError(
                "a V3.1 package already exists for unchanged inputs; use "
                "--version-bump none without --target-version for a repeat build"
            )
        if failed_consumed_retry and requested_version_bump != "none":
            raise ValueError(
                "the selected release action was consumed by a failed build; retry "
                "with --version-bump none for the matching package inputs"
            )
        effective_target_version = None
        if pending_release and pending_release.get("actionType") == "target-version":
            if requested_target_version != pending_release.get("targetVersion"):
                raise ValueError(
                    "package target version differs from the explicitly selected release action"
                )
            effective_target_version = pending_release["targetVersion"]
        elif requested_target_version is not None:
            selected_target = state["context"].get("targetVersion")
            selected_bump = state["context"].get("versionBump")
            if selected_bump not in (None, "none"):
                raise ValueError(
                    "target version cannot be combined with the workflow's selected version bump"
                )
            if selected_target not in (None, requested_target_version):
                raise ValueError(
                    "requested target version differs from the workflow's selected target"
                )
            if previous is None and solution_data_version(root) == requested_target_version:
                raise ValueError(
                    "target version already matches the solution; a new release action must "
                    "change the version"
                )
            effective_target_version = requested_target_version
        elif (
            previous is None
            and state["context"].get("targetVersion") is not None
            and not failed_consumed_retry
        ):
            raise ValueError(
                "the workflow selected a target version; package with the same "
                "--target-version and --version-bump none"
            )

        if (
            not notes_refresh
            and not pending_release
            and requested_version_bump == "none"
            and last_consumed.get("bumpConsumed") is True
        ):
            if inputs["sha256"] != last_consumed.get("packageInputSha256"):
                raise ValueError(
                    "package inputs changed after the consumed version action; "
                    "select an explicit new version bump"
                )
            effective_bump = "none"
        elif notes_refresh:
            effective_bump = "none"
        elif pending_release:
            effective_bump = pending_release["versionBump"]
        elif previous is None:
            selected_bump = state["context"].get("versionBump")
            if selected_bump is not None and selected_bump != requested_version_bump:
                raise ValueError(
                    "requested package version bump differs from the workflow's "
                    f"selected action: {requested_version_bump!r} != {selected_bump!r}"
                )
            if selected_bump is None:
                state["context"]["versionBump"] = requested_version_bump
            if effective_target_version is not None and state["context"].get("targetVersion") is None:
                state["context"]["targetVersion"] = effective_target_version
            effective_bump = requested_version_bump
        elif requested_version_bump == "none":
            raise ValueError(
                "retry with version bump none is allowed only after the original "
                "version action was consumed"
            )
        else:
            effective_bump = requested_version_bump

        stage = state["stages"]["packaging"]
        if stage["status"] == "notRequired":
            raise ValueError("packaging is not required for this workflow")
        attempt_number = stage["attempts"] + 1
        attempt_id = str(uuid.uuid4())
        started_at = _utc_now()
        stage.update({
            "status": "running",
            "attempts": attempt_number,
            "startedAt": started_at,
            "completedAt": None,
            "message": None,
            "artifacts": {},
            "evidence": [],
        })
        package_state["currentAttempt"] = {
            "attemptId": attempt_id,
            "attempt": attempt_number,
            "status": "running",
            "requestedVersionBump": requested_version_bump,
            "effectiveVersionBump": effective_bump,
            "requestedTargetVersion": requested_target_version,
            "effectiveTargetVersion": effective_target_version,
            "bumpConsumed": False,
            "targetConsumed": False,
            "packageInputSha256": inputs["sha256"],
            "packageReportSha256": None,
            "startedAt": started_at,
        }
        state["packaging"] = package_state
        state["workflowStatus"] = "inProgress"
        _write_unlocked(path, state)

        version_before = solution_data_version(root)
        try:
            if campaign_budget:
                package_receipt_details: dict[str, Any] = {}
                operation = measured_operation(
                    root,
                    campaign_budget["campaignId"],
                    inventory_sha256=campaign_budget["inventorySha256"],
                    run_id=state["runId"],
                    dimension="packageBuild",
                    metadata={
                        "packageInputSha256": inputs["sha256"],
                        "requestedVersionBump": requested_version_bump,
                        "effectiveVersionBump": effective_bump,
                        "requestedTargetVersion": requested_target_version,
                        "effectiveTargetVersion": effective_target_version,
                    },
                    completion_metadata=package_receipt_details,
                )
            else:
                from contextlib import nullcontext
                operation = nullcontext()
                package_receipt_details = {}
            package_dispatched = False
            with operation:
                try:
                    current_selection = verify_applied_package_selection(
                        root, str(state["runId"]),
                    )
                    if (
                        selection_evidence
                        and (
                            not current_selection
                            or current_selection["plan"].get("planSha256")
                            != selection_evidence["plan"].get("planSha256")
                        )
                    ):
                        raise ValueError(
                            "applied package selection changed after the workflow attempt was authorized"
                        )
                    package_dispatched = True
                    result = package_solution_v3_1(
                        root,
                        version_bump=effective_bump,
                        target_version=effective_target_version,
                        toolkit_root=toolkit_root,
                        requested_version_bump=requested_version_bump,
                        package_attempt_id=attempt_id,
                        workflow_run_id=state["runId"],
                        selection_plan=(
                            current_selection["plan"] if current_selection else None
                        ),
                        **({
                            "arm_validation_method": state["context"]["armValidationMethod"],
                        } if workbook_workflow.enabled(state) else {}),
                    )
                except BaseException:
                    version_after_failure = solution_data_version(root)
                    consumed_on_failure = _version_action_was_consumed(
                        version_before,
                        version_after_failure,
                        effective_bump,
                        effective_target_version,
                    )
                    package_receipt_details.update({
                        "bumpConsumed": consumed_on_failure,
                        "targetConsumed": (
                            effective_target_version is not None
                            and consumed_on_failure
                        ),
                        "targetVersion": effective_target_version,
                        "packageInputSha256After": (
                            package_input_identity(root)["sha256"]
                            if consumed_on_failure else inputs["sha256"]
                        ),
                    })
                    raise
                else:
                    package_receipt_details.update({
                        "bumpConsumed": _version_action_was_consumed(
                            version_before,
                            solution_data_version(root),
                            effective_bump,
                            effective_target_version,
                        ),
                        "targetConsumed": (
                            effective_target_version is not None
                            and solution_data_version(root) == effective_target_version
                            and version_before != effective_target_version
                        ),
                        "targetVersion": effective_target_version,
                        "packageInputSha256After": package_input_identity(root)["sha256"],
                    })
                    report_for_receipt = json.loads(
                        Path(result["packageReport"]).read_text(encoding="utf-8-sig")
                    )
                    receipt_inputs = report_for_receipt.get("packageInputs") or {}
                    report_after = (receipt_inputs.get("after") or {}).get("sha256")
                    if report_after:
                        package_receipt_details["packageInputSha256After"] = report_after
            report_path = resolve_artifact_reference(root, result["packageReport"])
            report_hash = hashlib.sha256(report_path.read_bytes()).hexdigest()
            report = json.loads(report_path.read_text(encoding="utf-8-sig"))
            report_inputs = report.get("packageInputs") or {}
            report_before = (report_inputs.get("before") or {}).get("sha256")
            if report_before != inputs["sha256"]:
                raise ValueError("package inputs changed after the workflow attempt was authorized")
            input_after = (report_inputs.get("after") or {}).get("sha256")
            if not input_after:
                raise ValueError("V3.1 package report has no post-build package input identity")
            if notes_refresh:
                current_after = package_input_identity(root)["sha256"]
                _validate_release_notes_refresh_inputs(
                    root, pending_release, current_after,
                )
                if (
                    input_after != current_after
                    or report.get("version") != pending_release.get("releaseNotesVersion")
                    or solution_data_version(root) != pending_release.get("releaseNotesVersion")
                    or report.get("effectiveVersionBump") != "none"
                ):
                    raise ValueError(
                        "V3.1 receipt does not bind the exact approved same-version "
                        "ReleaseNotes refresh"
                    )
            if same_version_rebuild:
                current_after = package_input_identity(root)["sha256"]
                _validate_same_version_content_rebuild_inputs(
                    root,
                    pending_release,
                    current_after,
                    solution_data_version(root),
                    successful_package,
                    legacy_baseline_evidence,
                )
                if (
                    input_after != current_after
                    or report.get("version") != pending_release.get("targetVersion")
                    or solution_data_version(root) != pending_release.get("targetVersion")
                    or report.get("effectiveVersionBump") != "none"
                    or report.get("effectiveTargetVersion") is not None
                ):
                    raise ValueError(
                        "V3.1 receipt does not bind the exact approved same-version "
                        "content rebuild"
                    )
            if effective_target_version is not None and (
                report.get("version") != effective_target_version
                or solution_data_version(root) != effective_target_version
                or report.get("effectiveTargetVersion") != effective_target_version
            ):
                raise ValueError(
                    "V3.1 receipt does not bind the explicitly selected target version"
                )
            current_attempt = package_state["currentAttempt"]
            current_attempt.update({
                "status": "passed",
                "bumpConsumed": True,
                "targetConsumed": effective_target_version is not None,
                "packageInputSha256": input_after,
                "packageReportSha256": report_hash,
                "completedAt": _utc_now(),
            })
            package_state["lastConsumedAction"] = {
                "requestedVersionBump": requested_version_bump,
                "effectiveVersionBump": effective_bump,
                "requestedTargetVersion": requested_target_version,
                "effectiveTargetVersion": effective_target_version,
                "targetConsumed": effective_target_version is not None,
                "bumpConsumed": True,
                "packageInputSha256": input_after,
                "attemptId": attempt_id,
                "packageSucceeded": True,
            }
            if pending_release:
                for release_action in reversed(package_state["releaseActions"]):
                    if (
                        release_action["status"] == "selected"
                        and release_action["packageInputSha256"] == inputs["sha256"]
                    ):
                        release_action["status"] = "consumed"
                        break
                package_state["pendingReleaseAction"] = None
            artifacts = dict(result["workflowArtifacts"])
            artifacts.update({
                "requestedVersionBump": requested_version_bump,
                "effectiveVersionBump": effective_bump,
                "packageAttemptId": attempt_id,
                "packageInputSha256": input_after,
                "packageReportSha256": report_hash,
            })
            if requested_target_version is not None or effective_target_version is not None:
                artifacts.update({
                    "requestedTargetVersion": requested_target_version,
                    "effectiveTargetVersion": effective_target_version,
                })
            if selection_evidence:
                artifacts.update({
                    "selectionPlan": selection_evidence["planPath"],
                    "selectionReceipt": selection_evidence["receiptPath"],
                    "selectionPlanSha256": selection_evidence["plan"]["planSha256"],
                    "selectionOutcome": report.get("selectionOutcome"),
                })
            if workbook_workflow.enabled(state) and (
                state["context"]["armValidationMethod"] == "lab-deployment"
                or report.get("xdrWorkbookCount", 0) > 0
            ):
                if report.get("packageAccepted") is not False or report.get("packageLifecycleStatus") != "candidate-generated":
                    raise ValueError("versioned candidate package receipt must remain explicitly unaccepted")
                stage.update({
                    "status": "blocked", "completedAt": _utc_now(),
                    "message": "Candidate generated; official static validation, selected ARM method and independent workbook contract evidence remain required.",
                    "artifacts": {**artifacts, "packageLifecycleStatus": "candidate-generated"},
                    "evidence": [result["packageReport"]],
                })
                current_attempt["status"] = "blocked"
                package_state["lastConsumedAction"]["packageSucceeded"] = False
                state["workflowStatus"] = "blocked"
                _write_unlocked(path, state)
                return {**result, "status": "blocked", "runId": state["runId"],
                        "workflowStatus": "blocked", "next": "workflow-arm-candidate"}
            stage.update({
                "status": "passed",
                "completedAt": _utc_now(),
                "message": (
                    "Fresh V3.1 package evidence verified for the current workflow attempt."
                    if validation_status == "passed"
                    else "Fresh partial V3.1 package evidence verified; excluded inventory remains unchanged."
                ),
                "artifacts": artifacts,
                "evidence": [result["packageReport"]],
            })
            _validate_packaging_evidence(state, artifacts, root)
            package_state["lastSuccessful"] = {
                **package_state["lastConsumedAction"],
                "packageReport": result["packageReport"],
                "packageReportSha256": report_hash,
                "packageArtifactsSha256": report.get("packageArtifactsSha256"),
                "version": result["version"],
            }
            state["workflowStatus"] = (
                "inProgress"
            )
            _write_unlocked(path, state)
            return {
                **result,
                "runId": state["runId"],
                "workflowStatus": state["workflowStatus"],
                "next": _next_stage_name(state),
            }
        except BudgetError as exc:
            if package_dispatched:
                package_state["lastSuccessful"] = previous_successful
                current_attempt = package_state["currentAttempt"]
                version_after = solution_data_version(root)
                consumed = _version_action_was_consumed(
                    version_before,
                    version_after,
                    effective_bump,
                    effective_target_version,
                )
                if consumed:
                    try:
                        input_after_failure = package_input_identity(root)["sha256"]
                    except (OSError, ValueError):
                        input_after_failure = None
                    if input_after_failure:
                        package_state["lastConsumedAction"] = {
                            "requestedVersionBump": requested_version_bump,
                            "effectiveVersionBump": effective_bump,
                            "requestedTargetVersion": requested_target_version,
                            "effectiveTargetVersion": effective_target_version,
                            "targetConsumed": (
                                effective_target_version is not None and consumed
                            ),
                            "bumpConsumed": True,
                            "packageInputSha256": input_after_failure,
                            "attemptId": attempt_id,
                            "packageSucceeded": False,
                        }
                        current_attempt["bumpConsumed"] = True
                        current_attempt["targetConsumed"] = (
                            effective_target_version is not None
                        )
                        current_attempt["packageInputSha256"] = input_after_failure
                        if pending_release:
                            package_state["pendingReleaseAction"] = None
                            for release_action in reversed(package_state["releaseActions"]):
                                if (
                                    release_action["status"] == "selected"
                                    and release_action["packageInputSha256"] == inputs["sha256"]
                                ):
                                    release_action["status"] = "consumed"
                                    break
                current_attempt.update({
                    "status": "failed",
                    "completedAt": _utc_now(),
                    "failure": f"V3.1 build was dispatched but receipt persistence failed: {exc}"[:1000],
                })
                stage.update({
                    "status": "failed",
                    "completedAt": _utc_now(),
                    "message": f"V3.1 build was dispatched but receipt persistence failed: {exc}"[:2000],
                    "artifacts": {},
                    "evidence": [],
                })
                state["workflowStatus"] = "failed"
                _write_unlocked(path, state)
                raise
            package_state["lastSuccessful"] = previous_successful
            current_attempt = package_state["currentAttempt"]
            current_attempt.update({
                "status": "blocked",
                "completedAt": _utc_now(),
                "failure": str(exc)[:1000],
            })
            stage.update({
                "status": "blocked",
                "completedAt": _utc_now(),
                "message": f"V3.1 build was not dispatched: {exc}"[:2000],
                "artifacts": {},
                "evidence": [],
            })
            _stop_budget_run(path, state, "packaging", str(exc))
            raise
        except Exception as exc:
            package_state["lastSuccessful"] = previous_successful
            current_attempt = package_state["currentAttempt"]
            version_after = solution_data_version(root)
            consumed = _version_action_was_consumed(
                version_before,
                version_after,
                effective_bump,
                effective_target_version,
            )
            if consumed:
                try:
                    input_after_failure = package_input_identity(root)["sha256"]
                except (OSError, ValueError):
                    input_after_failure = None
                if input_after_failure:
                    package_state["lastConsumedAction"] = {
                        "requestedVersionBump": requested_version_bump,
                        "effectiveVersionBump": effective_bump,
                        "requestedTargetVersion": requested_target_version,
                        "effectiveTargetVersion": effective_target_version,
                        "targetConsumed": (
                            effective_target_version is not None and consumed
                        ),
                        "bumpConsumed": True,
                        "packageInputSha256": input_after_failure,
                        "attemptId": attempt_id,
                        "packageSucceeded": False,
                    }
                    current_attempt["bumpConsumed"] = True
                    current_attempt["targetConsumed"] = (
                        effective_target_version is not None
                    )
                    current_attempt["packageInputSha256"] = input_after_failure
                    if pending_release:
                        package_state["pendingReleaseAction"] = None
                        for release_action in reversed(package_state["releaseActions"]):
                            if (
                                release_action["status"] == "selected"
                                and release_action["packageInputSha256"] == inputs["sha256"]
                            ):
                                release_action["status"] = "consumed"
                                break
            current_attempt.update({
                "status": "failed",
                "completedAt": _utc_now(),
                "failure": str(exc)[:1000],
            })
            stage.update({
                "status": "failed",
                "completedAt": _utc_now(),
                "message": f"V3.1 package attempt failed: {exc}"[:2000],
                "artifacts": {},
                "evidence": [],
            })
            state["workflowStatus"] = "failed"
            _write_unlocked(path, state)
            raise


def workflow_status(solution: str | Path) -> dict[str, Any]:
    path, state = _load(solution)
    from .runtime import current_runtime_evidence

    try:
        runtime_evidence = current_runtime_evidence(solution)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        runtime_evidence = {
            "passed": False,
            "sourceStatus": "blocked",
            "sourceWhitelist": [],
            "issues": [f"current runtime assessment unavailable: {type(exc).__name__}"],
        }
    authoring_summary = None
    if state.get("authoring"):
        document, _ = _load_contract_snapshot(path.parent, state["authoring"]["currentContract"])
        authoring_summary = {
            "status": state["authoring"]["status"],
            "contract": state["authoring"]["currentContract"],
            "coverage": document["coverage"],
            "inventorySha256": document["inventory"]["sha256"],
        }
    freshness = _package_freshness(solution, state)
    next_stage = _next_stage_name(state)
    if freshness and freshness["status"] != "current":
        next_stage = "packaging"
    partial_package_summary = None
    packaging_stage = (state.get("stages") or {}).get("packaging") or {}
    packaging_artifacts = packaging_stage.get("artifacts") or {}
    validation_stage = (state.get("stages") or {}).get("validation") or {}
    validation_artifacts = validation_stage.get("artifacts") or {}
    offline_authoring_marker = (
        state.get("context", {}).get("workflowProfile") == "authoring"
        and validation_stage.get("status") == "passed"
        and validation_artifacts.get("runtimeStatus") == "not-run"
        and validation_artifacts.get("validationMode") == "offline-authoring"
    )
    runtime_report_directory = report_directory(solution)
    offline_runtime_reports = tuple(
        runtime_report_directory / f"runtime-validation.{provider}.json"
        for provider in (
            "triage-mcp",
            "azure-monitor-sdk",
            "log-analytics-cli",
            "graph",
        )
    )
    offline_authoring = offline_authoring_marker and not any(
        report_path.is_file() for report_path in offline_runtime_reports
    )
    if (
        packaging_stage.get("status") == "passed"
        and packaging_artifacts.get("selectionOutcome") == "partial-package-validated"
        and freshness
        and freshness.get("status") == "current"
    ):
        successful = ((state.get("packaging") or {}).get("lastSuccessful") or {})
        report_reference = successful.get("packageReport")
        if isinstance(report_reference, str):
            report_path = resolve_artifact_reference(solution, report_reference)
            package_report = json.loads(report_path.read_text(encoding="utf-8-sig"))
            partial_package_summary = {
                "status": "partial-package-validated",
                "profile": (state.get("context") or {}).get("workflowProfile"),
                "selectionPlanSha256": package_report.get("selectionPlanSha256"),
                "coverage": package_report.get("selectionSummary"),
                "validationStageStatus": state["stages"]["validation"]["status"],
                "fullyRuntimeQualified": runtime_evidence.get("passed") is True,
                "parityStatus": (
                    (state.get("stages") or {}).get("alertParity") or {}
                ).get("status"),
            }
    workbook_summary = workbook_workflow.summary(solution, state)
    runtime_assessment = {
        "runtimeStatus": (
            "not-run"
            if offline_authoring
            else "passed"
            if runtime_evidence.get("passed")
            else "source-waived"
            if runtime_evidence.get("sourceStatus") == "source-waived"
            else "blocked"
        ),
        "sourceStatus": runtime_evidence.get("sourceStatus", "not-run"),
        "fullyRuntimeQualified": bool(runtime_evidence.get("passed")),
        "sourceWaiverOnlyBlocker": bool(
            runtime_evidence.get("sourceWaiverOnlyBlocker")
        ),
        "sourceWhitelist": runtime_evidence.get("sourceWhitelist") or [],
        "issues": runtime_evidence.get("issues") or [],
    }
    recommendation = _build_next_step_recommendation(
        solution,
        state,
        next_stage=next_stage,
        freshness=freshness,
        runtime_assessment=runtime_assessment,
        workbook_summary=workbook_summary,
    )
    return {
        **state,
        "workbookSummary": workbook_summary,
        "packageFreshness": freshness,
        "runtimeAssessment": runtime_assessment,
        "authoringSummary": authoring_summary,
        "partialSolution": partial_package_summary,
        "budgetSummary": (
            budget_summary(solution, state["budget"]["campaignId"])
            if state.get("budget") else (
                {
                    "enforcement": "unknown-unmeasured-history",
                    "legacyUsageStatus": "unknown",
                    "message": "This workflow has no persisted campaign budget.",
                }
                if state.get("authoring", {}).get("mode") == "yolo" else None
            )
        ),
        "conversionScope": conversion_scope(solution),
        "statePath": str(existing_artifact_path(solution, STATE_FILE_NAME)),
        "next": next_stage,
        "nextStepRecommendation": recommendation,
        "nextBlockerReview": recommendation,
    }


def _stop_budget_run(
    state_path: Path,
    state: dict[str, Any],
    stage_name: str,
    reason: str,
) -> None:
    stage = state["stages"][stage_name]
    if stage["status"] == "running":
        stage.update({
            "status": "blocked",
            "completedAt": _utc_now(),
            "message": f"Campaign budget stopped new work: {reason}"[:2000],
        })
    state["workflowStatus"] = "blocked"
    budget = state.get("budget")
    if isinstance(budget, dict):
        budget["status"] = "stopped"
        budget["stopReason"] = reason[:1000]
    authoring = state.get("authoring")
    if isinstance(authoring, dict):
        authoring["status"] = "stopped"
        authoring["stopReason"] = f"Campaign budget: {reason}"[:1000]
    _write_unlocked(state_path, state)


def invalidate_scoped_completion(solution: str | Path) -> None:
    """Retain historical evidence, but never reuse passed stages after a partial refresh."""
    if not existing_artifact_path(solution, STATE_FILE_NAME).is_file():
        return
    with _state_writer_lock(solution) as path:
        loaded_path, state = _load(solution)
        if loaded_path != path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        for name in STAGES[1:]:
            current = state["stages"][name]
            if current["status"] == "passed":
                current["status"] = "blocked"
                current["message"] = (
                    "Rule-scoped conversion invalidated full-solution completion. "
                    "Retained artifacts/evidence are historical; reconvert and revalidate the solution."
                )
        state["workflowStatus"] = "blocked"
        _write_unlocked(path, state)


def invalidate_runtime_completion(
    solution: str | Path,
    changed_queries: list[str],
    *,
    reason: str | None = None,
) -> None:
    """Block completed validation when current query or post-offline evidence changes."""
    if (
        (not changed_queries and not reason)
        or not existing_artifact_path(solution, STATE_FILE_NAME).is_file()
    ):
        return
    with _state_writer_lock(solution) as path:
        loaded_path, state = _load(solution)
        if loaded_path != path:
            raise ValueError("workflow state selection changed while acquiring its writer lock")
        validation = state["stages"]["validation"]
        offline_validation = (
            validation["status"] == "passed"
            and (validation.get("artifacts") or {}).get("runtimeStatus") == "not-run"
            and (validation.get("artifacts") or {}).get("validationMode") == "offline-authoring"
        )
        if reason and not offline_validation:
            return
        affected = STAGES[2:]
        if not any(
            state["stages"][name]["status"] not in {"pending", "notRequired"}
            for name in affected
        ):
            return
        if reason:
            message = (
                "Runtime validation is not complete: "
                + reason
                + " Reconcile the current complete provider evidence before completing Validation."
            )
        else:
            names = ", ".join(sorted(set(changed_queries)))
            message = (
                "A converted Advanced Hunting query changed; previous runtime evidence is "
                "historical and must not be reused. Rerun the complete Sentinel and Advanced "
                f"Hunting query families against the exact current queries. Changed outputs: {names}"
            )
        for name in affected:
            current = state["stages"][name]
            if current["status"] not in {"pending", "notRequired"}:
                current["status"] = "blocked"
                current["completedAt"] = None
                current["message"] = message
        state["workflowStatus"] = "blocked"
        _write_unlocked(path, state)


def _dependencies(state: dict[str, Any], stage: str) -> tuple[str, ...]:
    if (
        workbook_workflow.enabled(state)
        and state["context"]["workflowProfile"] == "qualification"
        and state["stages"]["alertParity"]["status"] == "notRequired"
        and stage == "report"
    ):
        return ("deployment",)
    if state["context"]["workflowProfile"] == "authoring":
        return AUTHORING_DEPENDENCIES.get(stage, ())
    return QUALIFICATION_DEPENDENCIES[stage]


def _next_stage_name(state: dict[str, Any]) -> str | None:
    if state.get("authoring", {}).get("status") in {"stopped", "conflicted"}:
        return None
    running = [
        name for name in STAGES if state["stages"][name]["status"] == "running"
    ]
    if running:
        return running[0]
    if (state.get("packaging") or {}).get("pendingReleaseAction"):
        return "packaging"
    for name in STAGES:
        stage = state["stages"][name]
        if (
            name == "validation"
            and _partial_package_state(state)
        ):
            continue
        if stage["status"] in {"passed", "notRequired"}:
            continue
        if all(
            state["stages"][dependency]["status"] == "passed"
            for dependency in _dependencies(state, name)
        ):
            return name
    return None


def _partial_package_state(state: dict[str, Any]) -> bool:
    packaging = (state.get("stages") or {}).get("packaging") or {}
    artifacts = packaging.get("artifacts") or {}
    return (
        packaging.get("status") == "passed"
        and artifacts.get("selectionOutcome") == "partial-package-validated"
    )


def next_workflow_stage(solution: str | Path) -> dict[str, Any]:
    path, state = _load(solution)
    name = _next_stage_name(state)
    freshness = _package_freshness(solution, state)
    release_action_required = bool(freshness and freshness["status"] != "current")
    if release_action_required:
        name = "packaging"
    blocked_by = []
    if name is None and state["workflowStatus"] != "completed":
        for candidate in STAGES:
            if candidate == "validation" and _partial_package_state(state):
                continue
            if state["stages"][candidate]["status"] in {"passed", "notRequired"}:
                continue
            blocked_by.extend(
                dependency
                for dependency in _dependencies(state, candidate)
                if state["stages"][dependency]["status"] != "passed"
            )
            if blocked_by:
                break
    recommendation = _build_next_step_recommendation(
        solution,
        state,
        next_stage=name,
        freshness=freshness,
        workbook_summary=workbook_workflow.summary(solution, state),
    )
    return {
        "runId": state.get("runId"),
        "conversionScope": conversion_scope(solution),
        "solution": state["solution"],
        "statePath": str(existing_artifact_path(solution, STATE_FILE_NAME)),
        "workflowStatus": state["workflowStatus"],
        "next": name,
        "blockedBy": blocked_by,
        "packageFreshness": freshness,
        "releaseActionRequired": release_action_required,
        "nextStepRecommendation": recommendation,
        "nextBlockerReview": recommendation,
    }


def start_workflow_stage(solution: str | Path, stage: str) -> dict[str, Any]:
    with _state_writer_lock(solution) as path:
        return _start_workflow_stage_unlocked(solution, stage, path)


def _start_workflow_stage_unlocked(
    solution: str | Path,
    stage: str,
    path: Path,
) -> dict[str, Any]:
    if stage not in STAGES:
        raise ValueError(f"unknown workflow stage: {stage}")
    if stage in STAGES[3:]:
        require_solution_conversion_scope(solution)
    loaded_path, state = _load(solution)
    if loaded_path != path:
        raise ValueError("workflow state selection changed while acquiring its writer lock")
    authoring = state.get("authoring")
    if authoring and authoring["status"] in {"stopped", "conflicted"} and stage != "report":
        raise ValueError(
            "YOLO authoring is stopped; new migration stages cannot be started"
        )
    current = state["stages"][stage]
    if current["status"] == "notRequired":
        raise ValueError(
            f"workflow stage is not required for "
            f"{state['context']['workflowProfile']} profile: {stage}"
        )
    if current["status"] == "passed":
        raise ValueError(f"workflow stage already passed: {stage}")
    if current["status"] == "running":
        return {**current, "statePath": str(path), "resumed": True}

    blocked_by = [
        dependency
        for dependency in _dependencies(state, stage)
        if state["stages"][dependency]["status"] != "passed"
    ]
    if blocked_by:
        raise ValueError(
            f"workflow stage {stage} is blocked by: {', '.join(blocked_by)}"
        )
    if state.get("packaging") and stage in {"deployment", "report"}:
        _verify_current_package_state(Path(solution).expanduser().resolve(), state)

    current.update(
        {
            "status": "running",
            "attempts": current["attempts"] + 1,
            "startedAt": _utc_now(),
            "completedAt": None,
            "message": None,
            "artifacts": {},
            "evidence": [],
        }
    )
    state["workflowStatus"] = "inProgress"
    _write_unlocked(path, state)
    return {**current, "statePath": str(path), "resumed": False}


def complete_workflow_stage(
    solution: str | Path,
    stage: str,
    *,
    status: str,
    message: str | None = None,
    artifacts: dict[str, str] | None = None,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    with _state_writer_lock(solution) as path:
        return _complete_workflow_stage_unlocked(
            solution, stage, path, status=status, message=message,
            artifacts=artifacts, evidence=evidence,
        )


def _complete_workflow_stage_unlocked(
    solution: str | Path,
    stage: str,
    path: Path,
    *,
    status: str,
    message: str | None = None,
    artifacts: dict[str, str] | None = None,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    if stage not in STAGES:
        raise ValueError(f"unknown workflow stage: {stage}")
    if status not in TERMINAL_STATUSES:
        raise ValueError("stage status must be passed, failed, or blocked")
    if status in {"failed", "blocked"} and not str(message or "").strip():
        raise ValueError(f"{status} workflow stages require a message")
    if status == "passed" and stage != "discovery":
        require_solution_conversion_scope(solution)

    loaded_path, state = _load(solution)
    if loaded_path != path:
        raise ValueError("workflow state selection changed while acquiring its writer lock")
    current = state["stages"][stage]
    if current["status"] != "running":
        raise ValueError(f"workflow stage is not running: {stage}")
    final_artifacts = dict(artifacts or {})
    if status == "passed" and workbook_workflow.enabled(state):
        workbook_workflow.verify_inventory(solution, state)
        if stage == "conversion":
            final_artifacts.update(workbook_workflow.bind_conversion(solution, state))
        if stage in {"validation", "packaging", "report"}:
            workbook_workflow.validate_evidence(solution, state)
        if stage == "report" and state["context"]["workflowProfile"] == "qualification":
            from .workbook_qualification import require_current_qualification
            require_current_qualification(solution, state)
    if (
        stage == "validation" and status == "passed"
        and workbook_workflow.enabled(state)
        and not workbook_workflow.has_analytic_rules(solution)
        and state["context"]["workflowProfile"] == "qualification"
    ):
        if state["context"].get("workbookQualificationAfterArm") is True:
            final_artifacts["validationMode"] = "workbook-content"
            final_artifacts["workbookQueryStatus"] = "not-run"
            final_artifacts["workbookUiStatus"] = "not-run"
        else:
            from .workbook_qualification import require_current_qualification
            require_current_qualification(solution, state)
            final_artifacts["validationMode"] = "workbook-qualification"
    elif stage == "validation" and status == "passed":
        runtime_status = final_artifacts.get("runtimeStatus")
        from .runtime import current_runtime_evidence

        runtime_evidence = current_runtime_evidence(solution)
        if runtime_status == "source-waived":
            if not runtime_evidence.get("sourceWaiverOnlyBlocker"):
                raise ValueError(
                    "source-waived validation requires an exact IdentityInfo source failure "
                    "and every other exact runtime gate to pass"
                )
            _validate_source_waiver_conversion_gates(
                Path(solution).expanduser().resolve(),
                path,
                state,
            )
            whitelist = runtime_evidence.get("sourceWhitelist") or []
            if not whitelist or any(
                item.get("table") != "IdentityInfo"
                or item.get("rawFailure", {}).get("status") != "failed"
                or item.get("applied") is not True
                for item in whitelist
            ):
                raise ValueError(
                    "source-waived validation requires current failed raw results "
                    "classified by the IdentityInfo whitelist"
                )
            final_artifacts.update(
                _source_whitelist_stage_artifacts(runtime_evidence)
            )
            final_artifacts["runtimeStatus"] = "source-waived"
            final_artifacts["sourceRuntimeWhitelistRawStatus"] = "failed"
            final_artifacts.setdefault("sentinelRuntimeProvider", runtime_evidence["sentinelProvider"])
            final_artifacts.setdefault("sentinelRuntimeReport", runtime_evidence["sentinelReport"])
            final_artifacts.setdefault("sentinelRuntimeJson", runtime_evidence["sentinelReport"])
            final_artifacts.setdefault("advancedHuntingRuntimeReport", runtime_evidence["graphReport"])
        elif runtime_status == "environment-blocked":
            if (
                runtime_evidence.get("sourceStatus") == "source-waived"
                or runtime_evidence.get("sourceWhitelist")
            ):
                raise ValueError(
                    "an IdentityInfo source whitelist match cannot be relabeled "
                    "environment-blocked; XDR and source-waiver gates must be evaluated"
                )
            if state["context"]["workflowProfile"] != "authoring":
                raise ValueError(
                    "Qualification validation cannot pass as environment-blocked; "
                    "runtime query validation is required"
                )
            if not str(message or "").strip():
                raise ValueError(
                    "environment-blocked Authoring validation requires an explanation"
                )
            if runtime_evidence.get("currentQueryFailures"):
                raise ValueError(
                    "a current exact-query KQL/runtime failure cannot be relabeled "
                    "environment-blocked: "
                    + "; ".join(runtime_evidence["currentQueryFailures"])
                )
        elif runtime_status == "not-run":
            if final_artifacts.get("validationMode") != "offline-authoring":
                raise ValueError(
                    "runtimeStatus=not-run requires the explicit offline-authoring validation mode"
                )
            _validate_offline_authoring_gates(
                Path(solution).expanduser().resolve(),
                path,
                state,
            )
            final_artifacts = {
                "runtimeStatus": "not-run",
                "validationMode": "offline-authoring",
            }
            message = _offline_authoring_validation_message()
        else:
            if not runtime_evidence["passed"]:
                raise ValueError(
                    "passed validation requires complete Sentinel and Advanced Hunting "
                    "runtime evidence bound to every current query: "
                    + "; ".join(runtime_evidence["issues"])
                )
            final_artifacts.setdefault("sentinelRuntimeProvider", runtime_evidence["sentinelProvider"])
            final_artifacts.setdefault("sentinelRuntimeReport", runtime_evidence["sentinelReport"])
            final_artifacts.setdefault("sentinelRuntimeJson", runtime_evidence["sentinelReport"])
            final_artifacts.setdefault("advancedHuntingRuntimeReport", runtime_evidence["graphReport"])
    elif stage == "validation" and status in {"blocked", "failed"}:
        from .runtime import current_runtime_evidence

        try:
            runtime_evidence = current_runtime_evidence(solution)
        except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError):
            runtime_evidence = {}
        final_artifacts.update(
            _source_whitelist_stage_artifacts(runtime_evidence)
        )
        if final_artifacts.get("sourceRuntimeWhitelistCount"):
            final_artifacts["sourceRuntimeWhitelistRawStatus"] = "failed"
    if stage == "packaging" and status == "passed":
        _validate_packaging_evidence(state, final_artifacts, solution)
    if (
        status == "passed"
        and stage in {"deployment", "report"}
        and state.get("packaging")
    ):
        _verify_current_package_state(Path(solution).expanduser().resolve(), state)
    if (
        status == "passed" and stage == "deployment"
        and state["context"].get("workbookQualificationAfterArm") is True
    ):
        workbook_workflow.require_accepted(solution, state)
        final_artifacts["deploymentMode"] = "candidate-arm-lab-validation"
        final_artifacts.update({
            key: value
            for key, value in state["stages"]["packaging"]["artifacts"].items()
            if key in {"armCandidate", "workbookContractPlan", "workbookContractEvidence", "workbookContractResult"}
        })
    current.update(
        {
            "status": status,
            "completedAt": _utc_now(),
            "message": message,
            "artifacts": final_artifacts,
            "evidence": evidence or [],
        }
    )
    if status == "failed":
        state["workflowStatus"] = "failed"
    elif status == "blocked":
        state["workflowStatus"] = "blocked"
    elif stage == "report":
        state["workflowStatus"] = (
            "partialCompleted"
            if _partial_package_state(state)
            else "completed"
        )
    else:
        state["workflowStatus"] = "inProgress"
    _write_unlocked(path, state)
    return {
        **current,
        "statePath": str(path),
        "workflowStatus": state["workflowStatus"],
        "next": _next_stage_name(state),
    }


def _categorize_detection_finding(reason: str) -> str:
    low = reason.casefold()
    if any(
        token in low
        for token in (
            "nrt",
            "frequency",
            "period",
            "lookback",
            "window",
            "schedule",
            "timing",
        )
    ):
        return "timing"
    if any(
        token in low
        for token in (
            "entity",
            "host.",
            "account.",
            "ip.",
            "mailbox",
            "customdetails",
            "custom-detail",
            "asset",
        )
    ):
        return "entityMappings"
    if "truncat" in low or "description" in low:
        return "truncatedDescriptions"
    if any(
        token in low
        for token in (
            "dependency",
            "workload",
            "connector",
            "datatype",
            "data type",
            "unmapped",
        )
    ):
        return "dependencyGaps"
    return "otherConversionFindings"


def _build_next_step_recommendation(
    solution: str | Path,
    state: dict[str, Any],
    *,
    next_stage: str | None = None,
    freshness: dict[str, Any] | None = None,
    runtime_assessment: dict[str, Any] | None = None,
    workbook_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    blockers: list[dict[str, str]] = []
    seen_labels: set[str] = set()

    def add_blocker(
        *,
        blocker_id: str,
        label: str,
        category: str,
        stage: str,
        reason: str,
    ) -> None:
        normalized_label = label.strip() or blocker_id
        if normalized_label in seen_labels:
            return
        seen_labels.add(normalized_label)
        blockers.append(
            {
                "id": blocker_id,
                "label": normalized_label,
                "kind": category,
                "category": category,
                "stage": stage,
                "reason": reason,
            }
        )

    authoring = state.get("authoring") or {}
    if isinstance(authoring, dict) and authoring.get("status") in {
        "stopped",
        "conflicted",
        "budget-exhausted",
    }:
        status_label = str(authoring.get("status"))
        add_blocker(
            blocker_id=f"authoring-{status_label}",
            label=f"authoring-{status_label}",
            category="workflow",
            stage="conversion",
            reason=str(
                authoring.get("stopReason")
                or f"Authoring workflow is {status_label}"
            ),
        )

    stages = state.get("stages") or {}
    for stage_name in STAGES:
        stage_info = stages.get(stage_name) or {}
        if stage_info.get("status") in {"failed", "blocked"}:
            add_blocker(
                blocker_id=f"stage-{stage_name}",
                label=stage_name,
                category="stage",
                stage=stage_name,
                reason=str(
                    stage_info.get("message")
                    or f"Stage {stage_name} is {stage_info.get('status')}"
                ),
            )

    detections_dir = root / "XDR Detections"
    if detections_dir.is_dir():
        try:
            detection_files = xdr_detection_files(detections_dir)
        except (OSError, ValueError):
            detection_files = sorted(
                p
                for p in detections_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in {".yaml", ".yml"}
            )
        for target_path in detection_files:
            try:
                doc = yaml.safe_load(target_path.read_text(encoding="utf-8-sig")) or {}
            except (OSError, yaml.YAMLError):
                continue
            if not isinstance(doc, dict):
                continue
            provenance = doc.get("contentProvenance") or {}
            if not isinstance(provenance, dict):
                continue
            source_meta = provenance.get("source") or {}
            conversion = provenance.get("conversion") or {}
            rule_id = str(source_meta.get("id") or target_path.stem)
            alert_title = str(
                (
                    (((doc.get("properties") or {}).get("detectionAction") or {}).get(
                        "alertTemplate"
                    )
                    or {})
                ).get("title")
                or target_path.stem
            )
            errors = list(conversion.get("errors") or [])
            review_reasons = list(conversion.get("reviewReasons") or [])
            dep_review = bool(provenance.get("dependencyReviewRequired"))
            if errors:
                add_blocker(
                    blocker_id=rule_id,
                    label=alert_title,
                    category="technicalFailure",
                    stage="conversion",
                    reason=str(errors[0]),
                )
            elif review_reasons or conversion.get("reviewRequired"):
                add_blocker(
                    blocker_id=rule_id,
                    label=alert_title,
                    category="detectionReview",
                    stage="conversion",
                    reason=str(
                        review_reasons[0]
                        if review_reasons
                        else "Detection requires author review"
                    ),
                )
            elif dep_review:
                add_blocker(
                    blocker_id=f"{rule_id}:dependencies",
                    label=f"{alert_title} dependencies",
                    category="dependencyReview",
                    stage="conversion",
                    reason="Detection workload/connector dependencies require review",
                )

    if isinstance(workbook_summary, dict):
        for issue in workbook_summary.get("issues") or []:
            add_blocker(
                blocker_id="workbook-inventory",
                label="workbook-inventory",
                category="workbookReview",
                stage="conversion",
                reason=str(issue),
            )
        for source in workbook_summary.get("sources") or []:
            if not isinstance(source, dict) or not source.get("selected"):
                continue
            wb_path = str(source.get("path") or "workbook")
            wb_status = str(source.get("status") or "not-converted")
            wb_issues = list(source.get("issues") or [])
            if wb_status != "converted" or wb_issues:
                add_blocker(
                    blocker_id=wb_path,
                    label=Path(wb_path).stem or wb_path,
                    category="workbookReview",
                    stage="conversion",
                    reason=str(
                        wb_issues[0]
                        if wb_issues
                        else f"Workbook status is {wb_status}"
                    ),
                )

    if (
        isinstance(runtime_assessment, dict)
        and runtime_assessment.get("runtimeStatus") == "blocked"
        and (stages.get("validation") or {}).get("status") != "passed"
    ):
        for index, issue in enumerate((runtime_assessment.get("issues") or [])[:2], start=1):
            add_blocker(
                blocker_id=f"runtime-validation-{index}",
                label="runtime-validation" if index == 1 else f"runtime-validation-{index}",
                category="runtimeValidation",
                stage="validation",
                reason=str(issue),
            )

    if isinstance(freshness, dict) and freshness.get("status") not in {
        "current",
        "notPackaged",
    }:
        add_blocker(
            blocker_id="package-freshness",
            label=f"package-freshness ({freshness.get('status')})",
            category="packaging",
            stage="packaging",
            reason=str(
                freshness.get("reason")
                or f"Package freshness status is {freshness.get('status')}"
            ),
        )

    top_blockers = blockers[:3]
    labels = [item["label"] for item in top_blockers]
    if len(labels) == 1:
        summary_text = f"Next migration step: review blocker {labels[0]}."
    elif len(labels) >= 2:
        summary_text = f"Next migration step: review blockers {labels[0]} and {labels[1]}."
    elif next_stage:
        summary_text = f"Next migration step: run {next_stage} stage."
    else:
        summary_text = "Next migration step: workflow complete; no remaining blockers."

    required_stages = [
        name
        for name in STAGES
        if (stages.get(name) or {}).get("status") != "notRequired"
    ]
    passed_stages = [
        name
        for name in required_stages
        if (stages.get(name) or {}).get("status") == "passed"
    ]
    running_stages = [
        name
        for name in required_stages
        if (stages.get(name) or {}).get("status") == "running"
    ]
    current_phase = (
        running_stages[0]
        if running_stages
        else (next_stage or ("completed" if state.get("workflowStatus") == "completed" else "blocked"))
    )
    recommended_command = (
        "review-packet"
        if any(
            item["category"]
            in {"detectionReview", "dependencyReview", "workbookReview", "technicalFailure"}
            for item in top_blockers
        )
        else f"workflow-start-stage --stage {next_stage}"
        if next_stage
        else "workflow-status"
    )
    return {
        "nextStage": next_stage,
        "status": (
            "blocked"
            if blockers
            else "ready"
            if next_stage
            else "complete"
        ),
        "blockerCount": len(blockers),
        "topBlockers": top_blockers,
        "blockerLabels": labels,
        "summary": summary_text,
        "message": summary_text,
        "recommendedCommand": recommended_command,
        "progress": {
            "completedStages": len(passed_stages),
            "totalRequiredStages": len(required_stages),
            "passedStages": passed_stages,
            "currentPhase": current_phase,
            "phaseSummary": (
                f"{len(passed_stages)}/{len(required_stages)} required stages passed; "
                f"current phase: {current_phase}"
            ),
        },
    }


def build_consolidated_review_packet(
    solution: str | Path,
    *,
    results_path: str | Path | None = None,
    detection_results_path: str | Path | None = None,
    workbook_results_path: str | Path | None = None,
    workspace_id: str | None = None,
    selected_rules: list[str] | None = None,
    rule_selectors: list[str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic, hash-bound one-shot review packet for detections and workbooks."""
    from .converter import load_config, validate_document
    from .dependencies import dependency_plan, plan_solution_dependencies
    from .workbook_dependencies import plan_workbook_dependencies
    from .workbooks import inventory_workbooks

    if results_path is None and detection_results_path is not None:
        results_path = detection_results_path
    if selected_rules is None and rule_selectors is not None:
        selected_rules = rule_selectors

    root = Path(solution).expanduser().resolve()
    state_file = existing_artifact_path(root, STATE_FILE_NAME)
    active_run_id: str | None = None
    if state_file.is_file():
        try:
            _, loaded_state = _load(root)
            active_run_id = loaded_state.get("runId")
        except (OSError, ValueError):
            active_run_id = None

    config = load_config(root / "XDR Detections")
    rule_overrides = config.get("ruleOverrides") if isinstance(config.get("ruleOverrides"), dict) else {}
    table_mappings = config.get("tableMappings") if isinstance(config.get("tableMappings"), dict) else {}

    category_names = (
        "timing",
        "entityMappings",
        "truncatedDescriptions",
        "dependencyGaps",
        "workbookQueryGaps",
        "technicalFailures",
        "otherConversionFindings",
    )
    categories: dict[str, list[dict[str, Any]]] = {name: [] for name in category_names}
    items: list[dict[str, Any]] = []
    preserved_decisions: list[dict[str, Any]] = []
    detection_records: list[dict[str, Any]] = []
    workbook_records: list[dict[str, Any]] = []
    inventory_entries: list[dict[str, str]] = []

    selected_filter = {
        str(value).strip()
        for value in (selected_rules or [])
        if str(value).strip()
    }

    def add_item(
        *,
        domain: str,
        category: str,
        severity: str,
        target_id: str,
        target_name: str,
        source_path: str,
        output_path: str,
        query_pointer: str,
        hashes: dict[str, str],
        finding: str,
        current_decision: str = "pending",
        prior_decision: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resolvable_by_batch = category != "technicalFailures"
        decision_options = (
            ["change", "defer"]
            if category == "technicalFailures"
            else ["accept", "change", "defer"]
        )
        canonical_id_payload = json.dumps(
            {
                "domain": domain,
                "category": category,
                "targetId": target_id,
                "outputPath": output_path,
                "queryPointer": query_pointer,
                "finding": finding,
                "hashes": hashes,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        item_id = hashlib.sha256(canonical_id_payload).hexdigest()
        record: dict[str, Any] = {
            "itemId": item_id,
            "domain": domain,
            "category": category,
            "severity": severity,
            "targetId": target_id,
            "targetName": target_name,
            "sourcePath": source_path,
            "outputPath": output_path,
            "queryPointer": query_pointer,
            "hashes": hashes,
            "finding": finding,
            "currentDecision": current_decision,
            "decisionState": (
                "decided"
                if current_decision in {"accept", "change"}
                else current_decision
            ),
            "decisionOptions": decision_options,
            "resolvableByBatchAccept": resolvable_by_batch,
        }
        if prior_decision is not None:
            record["priorDecision"] = prior_decision
        categories[category].append(record)
        items.append(record)
        return record

    live_dep_by_detection: dict[str, dict[str, Any]] = {}
    if results_path is not None:
        dep_plan_result = plan_solution_dependencies(
            root, results_path=results_path, workspace_id=workspace_id
        )
        for row in dep_plan_result.get("results") or []:
            if isinstance(row, dict) and isinstance(row.get("detection"), str):
                live_dep_by_detection[row["detection"]] = row

    detections_dir = root / "XDR Detections"
    detection_files: list[Path] = []
    if detections_dir.is_dir():
        try:
            detection_files = xdr_detection_files(detections_dir)
        except (OSError, ValueError):
            detection_files = sorted(
                p
                for p in detections_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in {".yaml", ".yml"}
            )

    converted_source_paths: set[str] = set()
    for target_path in detection_files:
        output_rel = target_path.relative_to(root).as_posix()
        raw_bytes = target_path.read_bytes()
        detection_sha = hashlib.sha256(raw_bytes).hexdigest()
        doc = yaml.safe_load(raw_bytes.decode("utf-8-sig")) or {}
        if not isinstance(doc, dict):
            continue
        provenance = doc.get("contentProvenance") or {}
        source_meta = provenance.get("source") or {}
        conversion = provenance.get("conversion") or {}
        rule_id = str(source_meta.get("id") or target_path.stem)
        source_rel = str(source_meta.get("path") or "")
        if source_rel:
            converted_source_paths.add(source_rel)
        if selected_filter and not (
            {rule_id, output_rel, source_rel, target_path.stem, target_path.name}
            & selected_filter
        ):
            continue

        inventory_entries.append(
            {
                "kind": "detection",
                "id": rule_id,
                "path": output_rel,
                "sha256": detection_sha,
            }
        )
        alert_template = (
            ((doc.get("properties") or {}).get("detectionAction") or {}).get(
                "alertTemplate"
            )
            or {}
        )
        rule_name = str(
            alert_template.get("title")
            or (doc.get("properties") or {}).get("displayName")
            or target_path.stem
        )
        query_text = str(
            ((doc.get("properties") or {}).get("queryCondition") or {}).get("queryText")
            or ""
        )
        review_scope = conversion.get("reviewScope") or {}
        source_doc_sha = str(
            review_scope.get("sourceDocumentSha256")
            or source_meta.get("querySha256")
            or ""
        )
        target_query_sha = str(
            review_scope.get("targetQuerySha256")
            or hashlib.sha256(query_text.encode("utf-8")).hexdigest()
        )
        item_hashes = {
            "sourceDocumentSha256": source_doc_sha,
            "targetQuerySha256": target_query_sha,
            "detectionSha256": detection_sha,
        }

        rule_override = (
            rule_overrides.get(rule_id)
            if isinstance(rule_overrides.get(rule_id), dict)
            else {}
        )
        decision_lookup: dict[str, dict[str, Any]] = {}
        for source_list in (
            rule_override.get("reviewDecisions") or [],
            conversion.get("reviewDecisions") or [],
        ):
            if not isinstance(source_list, list):
                continue
            for dec in source_list:
                if not isinstance(dec, dict) or not isinstance(dec.get("reason"), str):
                    continue
                reason_key = dec["reason"]
                hashes_match = (
                    dec.get("sourceDocumentSha256") == source_doc_sha
                    and dec.get("targetQuerySha256") == target_query_sha
                )
                normalized_choice = (
                    "accept"
                    if dec.get("decision") in {"accepted", "accept"}
                    else "change"
                    if dec.get("decision") in {"rejected", "change"}
                    else "defer"
                    if dec.get("decision") in {"deferred", "defer"}
                    else str(dec.get("decision") or "pending")
                )
                status_value = normalized_choice if hashes_match else "stale"
                record_dec = {
                    "domain": "detection",
                    "targetId": rule_id,
                    "reason": reason_key,
                    "decision": normalized_choice,
                    "status": "current" if hashes_match else "stale",
                    "sourceDocumentSha256": str(dec.get("sourceDocumentSha256") or ""),
                    "targetQuerySha256": str(dec.get("targetQuerySha256") or ""),
                }
                decision_lookup[reason_key] = {
                    "currentDecision": status_value,
                    "priorDecision": record_dec,
                }
                if record_dec not in preserved_decisions:
                    preserved_decisions.append(record_dec)

        for accepted_reason in conversion.get("acceptedReviewReasons") or []:
            if isinstance(accepted_reason, str) and accepted_reason not in decision_lookup:
                rec = {
                    "domain": "detection",
                    "targetId": rule_id,
                    "reason": accepted_reason,
                    "decision": "accept",
                    "status": "current",
                    "sourceDocumentSha256": source_doc_sha,
                    "targetQuerySha256": target_query_sha,
                }
                decision_lookup[accepted_reason] = {
                    "currentDecision": "accept",
                    "priorDecision": rec,
                }
                if rec not in preserved_decisions:
                    preserved_decisions.append(rec)

        has_entity_override = isinstance(rule_override.get("entityMappings"), dict)
        if has_entity_override:
            ent_rec = {
                "domain": "detection",
                "targetId": rule_id,
                "reason": "ruleOverrides.entityMappings",
                "decision": "change",
                "status": "current",
                "sourceDocumentSha256": source_doc_sha,
                "targetQuerySha256": target_query_sha,
            }
            if ent_rec not in preserved_decisions:
                preserved_decisions.append(ent_rec)

        rule_items: list[dict[str, Any]] = []
        seen_rule_findings: set[tuple[str, str]] = set()

        conv_errors = list(conversion.get("errors") or [])
        try:
            structural_errors = validate_document(doc)
        except (OSError, ValueError):
            structural_errors = []
        for err in conv_errors + [e for e in structural_errors if e not in conv_errors]:
            err_text = str(err)
            if ("technicalFailures", err_text) in seen_rule_findings:
                continue
            seen_rule_findings.add(("technicalFailures", err_text))
            rule_items.append(
                add_item(
                    domain="detection",
                    category="technicalFailures",
                    severity="error",
                    target_id=rule_id,
                    target_name=rule_name,
                    source_path=source_rel,
                    output_path=output_rel,
                    query_pointer="properties.queryCondition.queryText",
                    hashes=item_hashes,
                    finding=err_text,
                    current_decision="pending",
                )
            )

        source_doc: dict[str, Any] = {}
        if source_rel:
            try:
                source_file = content_path(root, source_rel)
                if source_file.is_file():
                    loaded_src = yaml.safe_load(source_file.read_text(encoding="utf-8-sig"))
                    if isinstance(loaded_src, dict):
                        source_doc = loaded_src
            except (OSError, ValueError, yaml.YAMLError):
                source_doc = {}

        source_desc = str(source_doc.get("description") or "").strip()
        override_desc = (
            rule_override.get("description").strip()
            if isinstance(rule_override.get("description"), str)
            and rule_override.get("description").strip()
            else None
        )
        if len(source_desc) > 600:
            trunc_msg = (
                f"Source description ({len(source_desc)} chars) was truncated to "
                "600 chars in alertTemplate.description."
            )
            dec_info = decision_lookup.get(trunc_msg, {})
            if not dec_info and override_desc:
                desc_rec = {
                    "domain": "detection",
                    "targetId": rule_id,
                    "reason": "ruleOverrides.description",
                    "decision": "change",
                    "status": "current",
                    "description": override_desc,
                    "sourceDocumentSha256": source_doc_sha,
                    "targetQuerySha256": target_query_sha,
                }
                if desc_rec not in preserved_decisions:
                    preserved_decisions.append(desc_rec)
                dec_info = {
                    "currentDecision": "change",
                    "priorDecision": desc_rec,
                }
            seen_rule_findings.add(("truncatedDescriptions", trunc_msg))
            rule_items.append(
                add_item(
                    domain="detection",
                    category="truncatedDescriptions",
                    severity="review",
                    target_id=rule_id,
                    target_name=rule_name,
                    source_path=source_rel,
                    output_path=output_rel,
                    query_pointer="properties.detectionAction.alertTemplate.description",
                    hashes=item_hashes,
                    finding=trunc_msg,
                    current_decision=dec_info.get("currentDecision", "pending"),
                    prior_decision=dec_info.get("priorDecision"),
                )
            )
        source_title = str(source_doc.get("name") or "").strip()
        if len(source_title) > 120:
            trunc_title_msg = (
                f"Source name ({len(source_title)} chars) was truncated to "
                "120 chars in alertTemplate.title."
            )
            dec_info = decision_lookup.get(trunc_title_msg, {})
            seen_rule_findings.add(("truncatedDescriptions", trunc_title_msg))
            rule_items.append(
                add_item(
                    domain="detection",
                    category="truncatedDescriptions",
                    severity="review",
                    target_id=rule_id,
                    target_name=rule_name,
                    source_path=source_rel,
                    output_path=output_rel,
                    query_pointer="properties.detectionAction.alertTemplate.title",
                    hashes=item_hashes,
                    finding=trunc_title_msg,
                    current_decision=dec_info.get("currentDecision", "pending"),
                    prior_decision=dec_info.get("priorDecision"),
                )
            )

        all_reasons = list(conversion.get("reviewReasons") or [])
        for accepted_reason in conversion.get("acceptedReviewReasons") or []:
            if isinstance(accepted_reason, str) and accepted_reason not in all_reasons:
                all_reasons.append(accepted_reason)
        for warning_msg in conversion.get("warnings") or []:
            if isinstance(warning_msg, str) and warning_msg not in all_reasons:
                cat = _categorize_detection_finding(warning_msg)
                if cat in {"timing", "entityMappings", "truncatedDescriptions", "dependencyGaps"}:
                    all_reasons.append(warning_msg)

        for reason_msg in all_reasons:
            reason_text = str(reason_msg)
            cat = _categorize_detection_finding(reason_text)
            if (cat, reason_text) in seen_rule_findings:
                continue
            seen_rule_findings.add((cat, reason_text))
            dec_info = decision_lookup.get(reason_text, {})
            default_dec = (
                "change"
                if cat == "entityMappings" and has_entity_override and not dec_info
                else dec_info.get("currentDecision", "pending")
            )
            pointer = (
                "properties.detectionAction.alertTemplate.entityMappings"
                if cat == "entityMappings"
                else "properties.queryCondition"
                if cat == "timing"
                else "properties.queryCondition.queryText"
            )
            rule_items.append(
                add_item(
                    domain="detection",
                    category=cat,
                    severity="review",
                    target_id=rule_id,
                    target_name=rule_name,
                    source_path=source_rel,
                    output_path=output_rel,
                    query_pointer=pointer,
                    hashes=item_hashes,
                    finding=reason_text,
                    current_decision=default_dec,
                    prior_decision=dec_info.get("priorDecision"),
                )
            )

        rel_from_xdr = (
            target_path.relative_to(detections_dir).as_posix()
            if target_path.is_relative_to(detections_dir)
            else target_path.name
        )
        dep_info = live_dep_by_detection.get(rel_from_xdr)
        if dep_info is None:
            source_query_text = str(source_doc.get("query") or query_text)
            dep_info = dependency_plan(
                source_query_text,
                target_query=query_text,
                connectors=source_doc.get("requiredDataConnectors")
                or doc.get("requiredDataConnectors"),
                table_mappings=table_mappings,
            )
        dep_reasons = list(dep_info.get("reviewReasons") or [])
        for unmapped_dt in dep_info.get("unmappedDataTypes") or []:
            msg = f"Unmapped data type requires workload mapping: {unmapped_dt}"
            if msg not in dep_reasons:
                dep_reasons.append(msg)
        if provenance.get("dependencyReviewRequired") and not dep_reasons:
            dep_reasons.append("Detection workload/connector dependencies require author review.")
        for dep_reason in dep_reasons:
            dep_text = str(dep_reason)
            if ("dependencyGaps", dep_text) in seen_rule_findings:
                continue
            seen_rule_findings.add(("dependencyGaps", dep_text))
            dec_info = decision_lookup.get(dep_text, {})
            rule_items.append(
                add_item(
                    domain="detection",
                    category="dependencyGaps",
                    severity="review",
                    target_id=rule_id,
                    target_name=rule_name,
                    source_path=source_rel,
                    output_path=output_rel,
                    query_pointer="contentProvenance.requiredWorkloads",
                    hashes=item_hashes,
                    finding=dep_text,
                    current_decision=dec_info.get("currentDecision", "pending"),
                    prior_decision=dec_info.get("priorDecision"),
                )
            )

        detection_records.append(
            {
                "ruleId": rule_id,
                "ruleName": rule_name,
                "sourcePath": source_rel,
                "outputFile": output_rel,
                "hashes": item_hashes,
                "status": str(conversion.get("status") or "converted"),
                "reviewRequired": bool(conversion.get("reviewRequired")),
                "dependencyReviewRequired": bool(
                    provenance.get("dependencyReviewRequired")
                ),
                "findingCount": len(rule_items),
                "technicalFailureCount": sum(
                    1 for item in rule_items if item["category"] == "technicalFailures"
                ),
                "itemIds": [item["itemId"] for item in rule_items],
            }
        )

    prior_wb_query_decisions: dict[tuple[str, str], dict[str, Any]] = {}
    prior_wb_dep_decisions: dict[str, dict[str, Any]] = {}
    try:
        reports_dir = report_directory(root)
        receipt_candidates = []
        if reports_dir.is_dir():
            direct_receipt = reports_dir / "workbook-review-receipt.json"
            if direct_receipt.is_file():
                receipt_candidates.append(direct_receipt)
            for child in sorted(reports_dir.iterdir()):
                if child.is_dir():
                    nested = child / "workbook-review-receipt.json"
                    if nested.is_file():
                        receipt_candidates.append(nested)
        for receipt_path in receipt_candidates:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            decisions_obj = (receipt.get("decisions") or {}) if isinstance(receipt, dict) else {}
            for q_dec in decisions_obj.get("queries") or []:
                if isinstance(q_dec, dict) and isinstance(q_dec.get("workbook"), str) and isinstance(q_dec.get("path"), str):
                    prior_wb_query_decisions[(q_dec["workbook"], q_dec["path"])] = q_dec
            for w_dec in decisions_obj.get("workbooks") or []:
                if isinstance(w_dec, dict) and isinstance(w_dec.get("path"), str):
                    prior_wb_dep_decisions[w_dec["path"]] = w_dec
    except (OSError, ValueError, json.JSONDecodeError):
        pass

    wb_plan: dict[str, Any] | None = None
    try:
        wb_inventory = inventory_workbooks(root)
    except (OSError, ValueError):
        wb_inventory = []
    if wb_inventory or workbook_results_path is not None:
        try:
            wb_plan = plan_workbook_dependencies(
                root,
                results_path=workbook_results_path,
                workspace_id=workspace_id,
            )
        except (OSError, ValueError):
            wb_plan = None

    if wb_plan is not None:
        wb_by_path: dict[str, list[dict[str, Any]]] = {}
        for row in wb_plan.get("inventory") or []:
            if isinstance(row, dict) and isinstance(row.get("path"), str):
                inventory_entries.append(
                    {
                        "kind": "workbook",
                        "id": row["path"],
                        "path": row["path"],
                        "sha256": str(row.get("sha256") or ""),
                    }
                )
                wb_by_path[row["path"]] = []

        for query_row in wb_plan.get("queries") or []:
            if not isinstance(query_row, dict):
                continue
            wb_path = str(query_row.get("workbook") or "")
            q_path = str(query_row.get("path") or "")
            wb_sha = str(query_row.get("workbookSha256") or "")
            q_sha = str(query_row.get("querySha256") or "")
            wb_hashes = {
                "workbookSha256": wb_sha,
                "querySha256": q_sha,
            }
            prior_q = prior_wb_query_decisions.get((wb_path, q_path))
            prior_rec: dict[str, Any] | None = None
            resolved_dec = "pending"
            if prior_q is not None:
                hash_matches = prior_q.get("querySha256") == q_sha
                raw_choice = str(prior_q.get("decision") or "pending")
                resolved_dec = raw_choice if hash_matches else "stale"
                prior_rec = {
                    "domain": "workbook",
                    "targetId": wb_path,
                    "queryPointer": q_path,
                    "decision": raw_choice,
                    "status": "current" if hash_matches else "stale",
                    "querySha256": str(prior_q.get("querySha256") or ""),
                }
                if prior_rec not in preserved_decisions:
                    preserved_decisions.append(prior_rec)

            for blocker in query_row.get("technicalBlockers") or []:
                item = add_item(
                    domain="workbook",
                    category="technicalFailures",
                    severity="error",
                    target_id=wb_path,
                    target_name=Path(wb_path).stem or wb_path,
                    source_path=wb_path,
                    output_path=wb_path,
                    query_pointer=q_path,
                    hashes=wb_hashes,
                    finding=str(blocker),
                    current_decision="pending",
                )
                wb_by_path.setdefault(wb_path, []).append(item)

            gap_messages = list(query_row.get("gapExplanations") or []) + list(
                query_row.get("externalSourceWarnings") or []
            )
            if (query_row.get("proposal") or {}).get("reviewRequired") and not gap_messages:
                gap_messages.append("Workbook query dependencies require author review.")
            for gap in gap_messages:
                item = add_item(
                    domain="workbook",
                    category="workbookQueryGaps",
                    severity="review",
                    target_id=wb_path,
                    target_name=Path(wb_path).stem or wb_path,
                    source_path=wb_path,
                    output_path=wb_path,
                    query_pointer=q_path,
                    hashes=wb_hashes,
                    finding=str(gap),
                    current_decision=resolved_dec,
                    prior_decision=prior_rec,
                )
                wb_by_path.setdefault(wb_path, []).append(item)

        for row in wb_plan.get("inventory") or []:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                continue
            wb_path = row["path"]
            wb_items = wb_by_path.get(wb_path, [])
            prior_w = prior_wb_dep_decisions.get(wb_path)
            if prior_w is not None:
                w_rec = {
                    "domain": "workbook",
                    "targetId": wb_path,
                    "reason": "workbookDependencies",
                    "decision": str(prior_w.get("decision") or "pending"),
                    "status": "current",
                    "workbookSha256": str(row.get("sha256") or ""),
                }
                if w_rec not in preserved_decisions:
                    preserved_decisions.append(w_rec)
            workbook_records.append(
                {
                    "workbook": wb_path,
                    "workbookSha256": str(row.get("sha256") or ""),
                    "findingCount": len(wb_items),
                    "technicalFailureCount": sum(
                        1 for i in wb_items if i["category"] == "technicalFailures"
                    ),
                    "itemIds": [i["itemId"] for i in wb_items],
                }
            )

    grouped_map: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for item in items:
        key = (item["domain"], item["category"], item["finding"])
        grouped_map.setdefault(key, []).append(item)

    grouped_findings: list[dict[str, Any]] = []
    for (domain, category, finding), members in sorted(
        grouped_map.items(), key=lambda entry: entry[0]
    ):
        group_id = hashlib.sha256(
            f"{domain}:{category}:{finding}".encode("utf-8")
        ).hexdigest()
        resolvable = category != "technicalFailures"
        grouped_findings.append(
            {
                "groupId": group_id,
                "domain": domain,
                "category": category,
                "severity": "error" if category == "technicalFailures" else "review",
                "finding": finding,
                "count": len(members),
                "allowedDecisions": (
                    ["change", "defer"]
                    if category == "technicalFailures"
                    else ["accept", "change", "defer"]
                ),
                "perItemExceptionsSupported": True,
                "resolvableByBatchAccept": resolvable,
                "affectedItems": [
                    {
                        "itemId": m["itemId"],
                        "targetId": m["targetId"],
                        "targetName": m["targetName"],
                        "sourcePath": m["sourcePath"],
                        "outputPath": m["outputPath"],
                        "queryPointer": m["queryPointer"],
                        "hashes": m["hashes"],
                        "currentDecision": m["currentDecision"],
                    }
                    for m in members
                ],
            }
        )

    inventory_sha = hashlib.sha256(
        json.dumps(
            sorted(inventory_entries, key=lambda x: (x["kind"], x["path"], x["id"])),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    technical_failures = list(categories["technicalFailures"])
    deferred_items = [item for item in items if item["currentDecision"] == "defer"]
    pending_items = [
        item
        for item in items
        if item["currentDecision"] in {"pending", "stale", "defer"}
        or item["category"] == "technicalFailures"
    ]

    top_blocker_labels: list[str] = []
    for item in technical_failures + pending_items:
        label = f"{item['targetName']} ({item['category']})"
        if label not in top_blocker_labels:
            top_blocker_labels.append(label)
        if len(top_blocker_labels) >= 3:
            break
    if len(top_blocker_labels) == 1:
        rec_text = f"Next migration step: review blocker {top_blocker_labels[0]}."
    elif len(top_blocker_labels) >= 2:
        rec_text = (
            f"Next migration step: review blockers {top_blocker_labels[0]} "
            f"and {top_blocker_labels[1]}."
        )
    else:
        rec_text = "Next migration step: all review items resolved; ready for validation."

    summary_counts = {
        "totalItems": len(items),
        "pendingReviewCount": len(pending_items),
        "preservedDecisionCount": len(preserved_decisions),
        "technicalFailureCount": len(technical_failures),
        "deferredItemCount": len(deferred_items),
        "groupCount": len(grouped_findings),
        "timingCount": len(categories["timing"]),
        "entityMappingCount": len(categories["entityMappings"]),
        "truncatedDescriptionCount": len(categories["truncatedDescriptions"]),
        "dependencyGapCount": len(categories["dependencyGaps"]),
        "workbookQueryGapCount": len(categories["workbookQueryGaps"]),
        "otherConversionFindingCount": len(categories["otherConversionFindings"]),
        "readyForValidation": len(pending_items) == 0 and len(technical_failures) == 0,
    }

    packet: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "kind": "consolidated-review-packet",
        "solution": str(root),
        "solutionName": root.name,
        "runId": active_run_id,
        "conversionScope": conversion_scope(root),
        "inventorySha256": inventory_sha,
        "allowedDecisions": ["accept", "change", "defer"],
        "perItemExceptionsSupported": True,
        "authorityLimits": {
            "establishesRuntimeCorrectness": False,
            "establishesAlertParity": False,
            "authorizesPackaging": False,
            "authorizesEnvironmentWrites": False,
        },
        "summary": summary_counts,
        "nextStepRecommendation": {
            "status": "blocked" if pending_items or technical_failures else "ready",
            "blockerCount": len(pending_items),
            "blockerLabels": top_blocker_labels,
            "summary": rec_text,
            "message": rec_text,
        },
        "categories": categories,
        "items": items,
        "groupedFindings": grouped_findings,
        "groups": grouped_findings,
        "detections": detection_records,
        "workbooks": workbook_records,
        "preservedDecisions": preserved_decisions,
        "technicalFailures": technical_failures,
        "deferredItems": deferred_items,
    }
    packet_sha = hashlib.sha256(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()
    return {**packet, "packetSha256": packet_sha}


plan_consolidated_review = build_consolidated_review_packet

STATUS_REMINDER_CURSOR_FILE = "status-reminder-cursor.json"
EXECUTION_OWNERSHIP_FILE = "execution-ownership.json"
FORWARDED_APPROVALS_FILE = "forwarded-approvals.json"
LARGE_DETECTION_BATCH_THRESHOLD = 15
LARGE_WORKBOOK_QUERY_BATCH_THRESHOLD = 50


def _build_workflow_diagram(state: dict[str, Any], next_stage: str | None) -> str:
    stages = state.get("stages") or {}
    packaging_stage = stages.get("packaging") or {}
    packaging_artifacts = packaging_stage.get("artifacts") or {}
    candidate_generated = (
        packaging_artifacts.get("packageLifecycleStatus") == "candidate-generated"
    )
    running = [
        name for name in STAGES if (stages.get(name) or {}).get("status") == "running"
    ]
    focus = running[0] if running else next_stage

    diagram_nodes = [
        ("discovery", "Discovery"),
        ("conversion", "Conversion"),
        ("validation", "Validation"),
        ("candidatePackaging", "Candidate Packaging"),
        ("armValidation", "ARM Validation"),
        ("acceptedPackaging", "Accepted Packaging"),
        ("report", "Report"),
    ]
    active_key: str | None = None
    if focus in {"discovery", "conversion", "validation", "report"}:
        active_key = focus
    elif focus in {"packaging", "workflow-arm-candidate", "deployment", "mockIngestion", "alertParity"}:
        if candidate_generated or focus in {"workflow-arm-candidate", "deployment"}:
            active_key = "armValidation"
        elif (packaging_stage.get("status") or "") == "passed":
            active_key = "acceptedPackaging"
        else:
            active_key = "candidatePackaging"
    elif state.get("workflowStatus") == "completed":
        active_key = "report"
    elif candidate_generated:
        active_key = "armValidation"

    rendered: list[str] = []
    for key, label in diagram_nodes:
        if key == active_key:
            rendered.append(f"[> {label} <]")
        else:
            rendered.append(f"[{label}]")
    return " -> ".join(rendered)


def _describe_current_activity(
    state: dict[str, Any],
    next_stage: str | None,
    recommendation: dict[str, Any],
) -> str:
    stages = state.get("stages") or {}
    running = [
        name for name in STAGES if (stages.get(name) or {}).get("status") == "running"
    ]
    active_stage = running[0] if running else next_stage
    top_blockers = recommendation.get("topBlockers") or []
    blocker_categories = {item.get("category") for item in top_blockers if isinstance(item, dict)}

    if blocker_categories & {"detectionReview", "dependencyReview", "workbookReview", "technicalFailure"}:
        return "Applying reviewed decisions or converting detections before validation."
    if active_stage == "discovery":
        return "Inspecting solution source inventory and validating content structure before conversion."
    if active_stage == "conversion":
        return "Applying reviewed decisions or converting detections before validation."
    if active_stage == "validation":
        return "Validating converted XDR detections and workbooks before candidate packaging."
    if active_stage in {"packaging", "workflow-arm-candidate"}:
        packaging_artifacts = ((stages.get("packaging") or {}).get("artifacts")) or {}
        if packaging_artifacts.get("packageLifecycleStatus") == "candidate-generated":
            return "Validating candidate V3.1 package and ARM template readiness before accepted packaging."
        return "Building and verifying the V3.1 solution package."
    if active_stage == "deployment":
        return "Deploying disabled detections and approved solution resources to the locked lab target."
    if active_stage == "mockIngestion":
        return "Ingesting reviewed mock telemetry into the locked lab workspace."
    if active_stage == "alertParity":
        return "Verifying alert parity between Sentinel Analytic Rules and Defender XDR Custom Detections."
    if active_stage == "report":
        return "Generating the consolidated solution migration report."
    if state.get("workflowStatus") == "completed":
        return "Migration workflow completed; all required stages passed."
    return "Reviewing current workflow gates and blocker evidence before the next stage."


def _build_duration_explanation(
    analytic_rule_count: int,
    xdr_detection_count: int,
    workbook_count: int,
    workbook_query_count: int,
) -> tuple[str, bool]:
    large_rules = analytic_rule_count >= LARGE_DETECTION_BATCH_THRESHOLD
    large_queries = workbook_query_count >= LARGE_WORKBOOK_QUERY_BATCH_THRESHOLD
    is_large = large_rules or large_queries
    if large_rules and large_queries:
        return (
            f"Large migration batch in progress: processing {analytic_rule_count} source analytic rules "
            f"({xdr_detection_count} converted XDR detections) and {workbook_query_count} workbook queries "
            f"across {workbook_count} workbooks; no completion time is estimated.",
            True,
        )
    if large_rules:
        return (
            f"Large detection batch in progress: processing {analytic_rule_count} source analytic rules "
            f"({xdr_detection_count} converted XDR detections); no completion time is estimated.",
            True,
        )
    if large_queries:
        return (
            f"Large workbook query batch in progress: processing {workbook_query_count} workbook queries "
            f"across {workbook_count} workbooks; no completion time is estimated.",
            True,
        )
    return (
        f"Processing {analytic_rule_count} source analytic rules ({xdr_detection_count} converted XDR "
        f"detections) and {workbook_query_count} workbook queries across {workbook_count} workbooks; "
        "no completion time is estimated.",
        False,
    )


def build_migration_status_reminder(
    solution_path: str | Path,
    *,
    run_id: str | None = None,
    persist_cursor: bool = True,
) -> dict[str, Any]:
    """Build a deterministic, evidence-bound status reminder with no-change suppression."""
    from .workbooks import inventory_workbooks

    root = Path(solution_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"solution folder does not exist: {root}")

    from contextlib import nullcontext

    run_ctx = using_run(root, run_id) if run_id else nullcontext()
    with run_ctx:
        state_path, state = _load(root)
        status = workflow_status(root)
        actual_run_id = str(status.get("runId") or state_path.parent.name)

        has_rule_folder = any(
            (root / name).exists() or (root / name).is_symlink()
            for name in ("Analytic Rules", "Analytics Rules")
        )
        try:
            analytic_rule_count = len(analytic_rule_files(root)) if has_rule_folder else 0
        except (OSError, ValueError):
            analytic_rule_count = 0

        detections_dir = root / "XDR Detections"
        try:
            xdr_detection_count = (
                len(xdr_detection_files(detections_dir))
                if detections_dir.is_dir()
                else 0
            )
        except (OSError, ValueError):
            xdr_detection_count = 0

        try:
            wb_inventory = inventory_workbooks(root)
        except (OSError, ValueError):
            wb_inventory = []
        workbook_count = len(wb_inventory)
        workbook_query_count = sum(
            len(wb.get("queries") or [])
            for wb in wb_inventory
            if isinstance(wb, dict)
        )

        recommendation = status["nextStepRecommendation"]
        blocker_count = int(recommendation.get("blockerCount") or 0)
        blocker_labels = list(recommendation.get("blockerLabels") or [])
        next_stage = status.get("next")

        stage_statuses = {
            stage_name: {
                "status": (status["stages"].get(stage_name) or {}).get("status"),
                "attempts": (status["stages"].get(stage_name) or {}).get("attempts", 0),
                "message": (status["stages"].get(stage_name) or {}).get("message"),
            }
            for stage_name in STAGES
        }
        fingerprint_payload = {
            "runId": actual_run_id,
            "workflowStatus": status.get("workflowStatus"),
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
            "packageFreshnessStatus": (status.get("packageFreshness") or {}).get("status"),
        }
        state_fingerprint = hashlib.sha256(
            json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        cursor_path = state_path.parent / STATUS_REMINDER_CURSOR_FILE
        previous_fingerprint: str | None = None
        if cursor_path.is_file():
            try:
                cursor_doc = json.loads(cursor_path.read_text(encoding="utf-8-sig"))
                if isinstance(cursor_doc, dict):
                    previous_fingerprint = str(
                        cursor_doc.get("stateFingerprint")
                        or cursor_doc.get("lastStateFingerprint")
                        or ""
                    ) or None
            except (OSError, json.JSONDecodeError):
                previous_fingerprint = None

        suppressed_no_change = previous_fingerprint == state_fingerprint
        now = _utc_now()
        if persist_cursor and not suppressed_no_change:
            with _run_writer_lock(state_path.parent):
                _atomic_json(
                    cursor_path,
                    {
                        "schemaVersion": "1.0.0",
                        "runId": actual_run_id,
                        "stateFingerprint": state_fingerprint,
                        "lastStateFingerprint": state_fingerprint,
                        "updatedAtUtc": now,
                    },
                )

        current_activity = _describe_current_activity(state, next_stage, recommendation)
        duration_explanation, is_large_batch = _build_duration_explanation(
            analytic_rule_count,
            xdr_detection_count,
            workbook_count,
            workbook_query_count,
        )
        workflow_diagram = _build_workflow_diagram(state, next_stage)
        watchdog_coordination = {
            "readOnlyObserver": True,
            "createsExecutor": False,
            "singleOwnerRespected": True,
        }

        return {
            "schemaVersion": "1.0.0",
            "kind": "migration-status-reminder",
            "solution": str(root),
            "solutionName": root.name,
            "runId": actual_run_id,
            "workflowStatus": status.get("workflowStatus"),
            "stateFingerprint": state_fingerprint,
            "previousStateFingerprint": previous_fingerprint,
            "suppressedNoChange": suppressed_no_change,
            "cursorPath": str(cursor_path),
            "currentActivity": current_activity,
            "expectedNextStep": recommendation["summary"],
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
            "watchdogCoordination": watchdog_coordination,
        }


def claim_execution_ownership(
    solution_path: str | Path,
    owner_id: str | None = None,
    operation: str | None = None,
    *,
    scope: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Claim or renew single-owner execution lease for (runId, operation) in execution-ownership.json."""
    if not isinstance(owner_id, str) or not owner_id.strip():
        raise ValueError("ownerId must be a non-empty string")
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string")
    if scope is not None and not isinstance(scope, dict):
        raise ValueError("scope must be a JSON object when provided")

    owner_clean = owner_id.strip()
    operation_clean = operation.strip()
    normalized_scope = dict(scope or {})
    root = Path(solution_path).expanduser().resolve()

    from contextlib import nullcontext

    run_ctx = using_run(root, run_id) if run_id else nullcontext()
    with run_ctx:
        state_path, state = _load(root)
        actual_run_id = str(state.get("runId") or state_path.parent.name)
        ownership_path = state_path.parent / EXECUTION_OWNERSHIP_FILE
        with _run_writer_lock(state_path.parent):
            doc: dict[str, Any] = {}
            if ownership_path.is_file():
                try:
                    loaded = json.loads(ownership_path.read_text(encoding="utf-8-sig"))
                    if isinstance(loaded, dict):
                        doc = loaded
                except (OSError, json.JSONDecodeError) as exc:
                    raise ValueError(f"invalid execution ownership file: {ownership_path}: {exc}") from exc

            leases = dict(doc.get("leases") or {})
            history = list(doc.get("history") or [])
            existing = leases.get(operation_clean)
            if (
                isinstance(existing, dict)
                and existing.get("status") == "active"
                and existing.get("ownerId") != owner_clean
            ):
                raise ValueError(
                    f"duplicate_executor_blocked: operation {operation_clean!r} in run "
                    f"{actual_run_id!r} is already owned by {existing.get('ownerId')!r}; "
                    f"conflicting claim by {owner_clean!r} rejected"
                )

            now = _utc_now()
            renewed_count = (
                int(existing.get("renewedCount", 0)) + 1
                if isinstance(existing, dict)
                and existing.get("status") == "active"
                and existing.get("ownerId") == owner_clean
                else 0
            )
            claimed_at = (
                str(existing.get("claimedAtUtc") or now)
                if renewed_count > 0 and isinstance(existing, dict)
                else now
            )
            lease_record = {
                "runId": actual_run_id,
                "ownerId": owner_clean,
                "operation": operation_clean,
                "scope": normalized_scope,
                "status": "active",
                "claimedAtUtc": claimed_at,
                "updatedAtUtc": now,
                "releasedAtUtc": None,
                "renewedCount": renewed_count,
                "singleOwnerEnforced": True,
            }
            leases[operation_clean] = lease_record
            history.append({
                "event": "renewed" if renewed_count > 0 else "claimed",
                "runId": actual_run_id,
                "ownerId": owner_clean,
                "operation": operation_clean,
                "scope": normalized_scope,
                "timestampUtc": now,
            })
            updated_doc = {
                "schemaVersion": "1.0.0",
                "runId": actual_run_id,
                "solution": str(root),
                "ownerId": owner_clean,
                "operation": operation_clean,
                "scope": normalized_scope,
                "claimedAtUtc": claimed_at,
                "updatedAtUtc": now,
                "status": "active",
                "leases": leases,
                "history": history,
            }
            _atomic_json(ownership_path, updated_doc)
            return {
                **lease_record,
                "ownershipPath": str(ownership_path),
            }


def release_execution_ownership(
    solution_path: str | Path,
    owner_id: str | None = None,
    operation: str | None = None,
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Release an active single-owner execution lease held by owner_id for (runId, operation)."""
    if not isinstance(owner_id, str) or not owner_id.strip():
        raise ValueError("ownerId must be a non-empty string")
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string")

    owner_clean = owner_id.strip()
    operation_clean = operation.strip()
    root = Path(solution_path).expanduser().resolve()

    from contextlib import nullcontext

    run_ctx = using_run(root, run_id) if run_id else nullcontext()
    with run_ctx:
        state_path, state = _load(root)
        actual_run_id = str(state.get("runId") or state_path.parent.name)
        ownership_path = state_path.parent / EXECUTION_OWNERSHIP_FILE
        with _run_writer_lock(state_path.parent):
            if not ownership_path.is_file():
                raise ValueError(
                    f"execution ownership file does not exist for run {actual_run_id!r}"
                )
            doc = json.loads(ownership_path.read_text(encoding="utf-8-sig"))
            if not isinstance(doc, dict):
                raise ValueError(f"invalid execution ownership file: {ownership_path}")
            leases = dict(doc.get("leases") or {})
            history = list(doc.get("history") or [])
            existing = leases.get(operation_clean)
            if not isinstance(existing, dict) or existing.get("status") != "active":
                raise ValueError(
                    f"no active execution ownership lease for operation {operation_clean!r} in run {actual_run_id!r}"
                )
            if existing.get("ownerId") != owner_clean:
                raise ValueError(
                    f"duplicate_executor_blocked: operation {operation_clean!r} in run "
                    f"{actual_run_id!r} is owned by {existing.get('ownerId')!r}; "
                    f"release by {owner_clean!r} rejected"
                )
            now = _utc_now()
            released_record = {
                **existing,
                "status": "released",
                "releasedAtUtc": now,
                "updatedAtUtc": now,
            }
            leases[operation_clean] = released_record
            history.append({
                "event": "released",
                "runId": actual_run_id,
                "ownerId": owner_clean,
                "operation": operation_clean,
                "scope": existing.get("scope") or {},
                "timestampUtc": now,
            })
            updated_doc = {
                **doc,
                "ownerId": owner_clean,
                "operation": operation_clean,
                "status": "released",
                "updatedAtUtc": now,
                "leases": leases,
                "history": history,
            }
            _atomic_json(ownership_path, updated_doc)
            return {
                **released_record,
                "ownershipPath": str(ownership_path),
            }


def _compute_forwarded_approval_sha256(
    *,
    run_id: str,
    operation: str,
    approved_by: str,
    forwarded_to_owner_id: str,
    exact_scope: dict[str, Any],
) -> str:
    payload = {
        "runId": run_id,
        "operation": operation,
        "approvedBy": approved_by,
        "forwardedToOwnerId": forwarded_to_owner_id,
        "exactScope": exact_scope,
    }
    canonical_bytes = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


def forward_explicit_approval(
    solution_path: str | Path,
    *,
    operation: str,
    approved_by: str,
    forwarded_to_owner_id: str,
    exact_scope: dict[str, Any],
    run_id: str | None = None,
    reference: str | None = None,
) -> dict[str, Any]:
    """Bind runId, operation, approvedBy, forwardedToOwnerId, and exactScope into forwarded-approvals.json."""
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string")
    if not isinstance(approved_by, str) or not approved_by.strip():
        raise ValueError("approvedBy must be a non-empty string")
    if not isinstance(forwarded_to_owner_id, str) or not forwarded_to_owner_id.strip():
        raise ValueError("forwardedToOwnerId must be a non-empty string")
    if not isinstance(exact_scope, dict) or not exact_scope:
        raise ValueError("exactScope must be a non-empty JSON object")

    operation_clean = operation.strip()
    approver_clean = approved_by.strip()
    owner_clean = forwarded_to_owner_id.strip()
    scope_copy = json.loads(json.dumps(exact_scope))
    root = Path(solution_path).expanduser().resolve()

    from contextlib import nullcontext

    run_ctx = using_run(root, run_id) if run_id else nullcontext()
    with run_ctx:
        state_path, state = _load(root)
        actual_run_id = str(state.get("runId") or state_path.parent.name)
        ownership_path = state_path.parent / EXECUTION_OWNERSHIP_FILE
        receipt_path = state_path.parent / FORWARDED_APPROVALS_FILE
        with _run_writer_lock(state_path.parent):
            if ownership_path.is_file():
                ownership_doc = json.loads(ownership_path.read_text(encoding="utf-8-sig"))
                if isinstance(ownership_doc, dict):
                    active_lease = (ownership_doc.get("leases") or {}).get(operation_clean)
                    if (
                        isinstance(active_lease, dict)
                        and active_lease.get("status") == "active"
                        and active_lease.get("ownerId") != owner_clean
                    ):
                        raise ValueError(
                            f"duplicate_executor_blocked: cannot forward approval for operation "
                            f"{operation_clean!r} to {owner_clean!r} while active execution lease "
                            f"is held by {active_lease.get('ownerId')!r}"
                        )

            approval_sha256 = _compute_forwarded_approval_sha256(
                run_id=actual_run_id,
                operation=operation_clean,
                approved_by=approver_clean,
                forwarded_to_owner_id=owner_clean,
                exact_scope=scope_copy,
            )
            now = _utc_now()
            record: dict[str, Any] = {
                "schemaVersion": "1.0.0",
                "runId": actual_run_id,
                "operation": operation_clean,
                "approvedBy": approver_clean,
                "forwardedToOwnerId": owner_clean,
                "exactScope": scope_copy,
                "approvalSha256": approval_sha256,
                "reference": reference,
                "forwardedAtUtc": now,
                "status": "active",
            }
            doc: dict[str, Any] = {}
            if receipt_path.is_file():
                try:
                    loaded = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
                    if isinstance(loaded, dict):
                        doc = loaded
                except (OSError, json.JSONDecodeError) as exc:
                    raise ValueError(f"invalid forwarded approvals file: {receipt_path}: {exc}") from exc

            approvals = dict(doc.get("approvals") or {})
            history = list(doc.get("history") or [])
            approvals[operation_clean] = record
            history.append(record)
            updated_doc = {
                "schemaVersion": "1.0.0",
                "runId": actual_run_id,
                "solution": str(root),
                "operation": operation_clean,
                "approvedBy": approver_clean,
                "forwardedToOwnerId": owner_clean,
                "exactScope": scope_copy,
                "approvalSha256": approval_sha256,
                "forwardedAtUtc": now,
                "approvals": approvals,
                "history": history,
            }
            _atomic_json(receipt_path, updated_doc)
            return {
                **record,
                "receiptPath": str(receipt_path),
            }


def verify_forwarded_approval(
    solution_path: str | Path,
    *,
    owner_id: str | None = None,
    forwarded_to_owner_id: str | None = None,
    operation: str,
    exact_scope: dict[str, Any],
    approval_sha256: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Verify byte-for-byte that recipient ownerId, runId, operation, and exactScope match approvalSha256."""
    recipient = owner_id if owner_id is not None else forwarded_to_owner_id
    if not isinstance(recipient, str) or not recipient.strip():
        raise ValueError("ownerId must be a non-empty string")
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string")
    if not isinstance(exact_scope, dict) or not exact_scope:
        raise ValueError("exactScope must be a non-empty JSON object")

    recipient_clean = recipient.strip()
    operation_clean = operation.strip()
    root = Path(solution_path).expanduser().resolve()

    from contextlib import nullcontext

    run_ctx = using_run(root, run_id) if run_id else nullcontext()
    with run_ctx:
        state_path, state = _load(root)
        actual_run_id = str(state.get("runId") or state_path.parent.name)
        receipt_path = state_path.parent / FORWARDED_APPROVALS_FILE
        if not receipt_path.is_file():
            raise ValueError(
                f"forwarded approval receipt does not exist: {receipt_path}"
            )
        doc = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
        if not isinstance(doc, dict):
            raise ValueError(f"invalid forwarded approvals file: {receipt_path}")
        approvals = doc.get("approvals") or {}
        stored = approvals.get(operation_clean)
        if not isinstance(stored, dict):
            raise ValueError(
                f"no forwarded approval recorded for operation {operation_clean!r} in run {actual_run_id!r}"
            )

        stored_run_id = str(stored.get("runId") or "")
        stored_operation = str(stored.get("operation") or "")
        stored_approved_by = str(stored.get("approvedBy") or "")
        stored_owner = str(stored.get("forwardedToOwnerId") or "")
        stored_scope = stored.get("exactScope")
        stored_sha = str(stored.get("approvalSha256") or "")

        if not isinstance(stored_scope, dict):
            raise ValueError("stored forwarded approval has invalid exactScope")

        recomputed_stored_sha = _compute_forwarded_approval_sha256(
            run_id=stored_run_id,
            operation=stored_operation,
            approved_by=stored_approved_by,
            forwarded_to_owner_id=stored_owner,
            exact_scope=stored_scope,
        )
        if recomputed_stored_sha != stored_sha:
            raise ValueError(
                "forwarded_approval_tampered: stored receipt hash does not match its recorded payload"
            )
        if stored_run_id != actual_run_id:
            raise ValueError(
                f"forwarded_approval_run_mismatch: receipt belongs to run {stored_run_id!r}, not {actual_run_id!r}"
            )
        if stored_operation != operation_clean:
            raise ValueError(
                f"forwarded_approval_operation_mismatch: receipt binds {stored_operation!r}, not {operation_clean!r}"
            )
        if stored_owner != recipient_clean:
            raise ValueError(
                f"forwarded_approval_owner_mismatch: approval was forwarded to {stored_owner!r}, "
                f"not {recipient_clean!r}"
            )

        stored_scope_bytes = json.dumps(
            stored_scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        requested_scope_bytes = json.dumps(
            exact_scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        if stored_scope_bytes != requested_scope_bytes:
            raise ValueError(
                "forwarded_approval_scope_mismatch: requested scope differs from the approved exactScope"
            )

        candidate_sha = _compute_forwarded_approval_sha256(
            run_id=actual_run_id,
            operation=operation_clean,
            approved_by=stored_approved_by,
            forwarded_to_owner_id=recipient_clean,
            exact_scope=exact_scope,
        )
        if candidate_sha != stored_sha:
            raise ValueError(
                "forwarded_approval_hash_mismatch: computed approvalSha256 does not match receipt"
            )
        if approval_sha256 is not None and approval_sha256.strip() != stored_sha:
            raise ValueError(
                f"forwarded_approval_hash_mismatch: expected {approval_sha256.strip()!r}, "
                f"receipt has {stored_sha!r}"
            )

        return {
            "verified": True,
            "status": "verified",
            "runId": actual_run_id,
            "operation": operation_clean,
            "approvedBy": stored_approved_by,
            "forwardedToOwnerId": stored_owner,
            "exactScope": stored_scope,
            "approvalSha256": stored_sha,
            "receiptPath": str(receipt_path),
        }

