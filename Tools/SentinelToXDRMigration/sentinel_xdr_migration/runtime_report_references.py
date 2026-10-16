from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from .artifacts import portable_artifact, report_directory, using_run
from .converter import xdr_detection_files
from .packaging_selection import (
    SOURCE_PROVIDER_SURFACES,
    _current_target,
    _read_json,
    _runtime_binding,
    _runtime_family,
    _run_context,
    _source_runtime_reference_status,
)
from .workflow import (
    _load,
    _migrate_workflow_state,
    _state_writer_lock,
    _write_unlocked,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _typed_sdk_schema_errors(report: dict[str, Any]) -> list[str]:
    results = report.get("results")
    if not isinstance(results, list):
        return ["SDK report has no complete results list"]
    errors = []
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            errors.append(f"SDK result {index} is malformed")
            continue
        tables = result.get("tables")
        if not isinstance(tables, list) or not tables:
            errors.append(f"SDK result {index} has no typed table schema")
            continue
        column_count = 0
        for table_index, table in enumerate(tables):
            columns = table.get("columns") if isinstance(table, dict) else None
            if (
                not isinstance(table, dict)
                or not isinstance(table.get("name"), str)
                or not table["name"].strip()
                or not isinstance(table.get("rowCount"), int)
                or isinstance(table.get("rowCount"), bool)
                or table["rowCount"] < 0
                or not isinstance(columns, list)
                or not columns
            ):
                errors.append(
                    f"SDK result {index} table {table_index} has an invalid typed schema"
                )
                continue
            seen: set[str] = set()
            for column in columns:
                if not isinstance(column, dict):
                    errors.append(
                        f"SDK result {index} table {table_index} contains a malformed column"
                    )
                    break
                name = column.get("name")
                kind = column.get("type")
                if (
                    not isinstance(name, str)
                    or not name.strip()
                    or not isinstance(kind, str)
                    or not kind.strip()
                    or name.casefold() in seen
                ):
                    errors.append(
                        f"SDK result {index} table {table_index} has invalid or duplicate columns"
                    )
                    break
                seen.add(name.casefold())
                column_count += 1
        if result.get("schemaColumnCount") != column_count:
            errors.append(f"SDK result {index} schemaColumnCount does not match its typed tables")
    return errors


def _validate_complete_runtime_evidence(
    root: Path,
    run_directory: Path,
    state: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    target, target_fingerprint = _current_target(
        root, state, materialize_missing=False,
    )
    if not target or not target_fingerprint:
        raise ValueError("runtime-report reference repair requires the current locked Qualification target")

    plan_path = run_directory / "runtime-query-plan.json"
    if not plan_path.is_file():
        raise ValueError("runtime query plan is missing; current execution bindings cannot be established")
    plan = _read_json(plan_path, "runtime query plan")
    source_family = (plan.get("families") or {}).get("sentinelSourceQueryFamily") or {}
    source_provider = (source_family.get("provider") or {}).get("provider")
    if source_provider != "azure-monitor-sdk":
        raise ValueError(
            f"current plan routes source queries through {source_provider!r}, not azure-monitor-sdk"
        )

    detection_paths = {
        path.relative_to(root / "XDR Detections").as_posix(): path
        for path in xdr_detection_files(root / "XDR Detections")
    }
    if not detection_paths:
        raise ValueError("current detection inventory is empty")

    sdk_path = run_directory / "runtime-validation.azure-monitor-sdk.json"
    if not sdk_path.is_file():
        raise ValueError("current Azure Monitor SDK runtime report is missing")
    consent_path = run_directory / "runtime-query-consent.json"
    if not consent_path.is_file():
        raise ValueError("current source execution consent evidence is missing")
    sdk_report = _read_json(sdk_path, "Azure Monitor SDK runtime report")
    source_bound, source_reason = _runtime_binding(
        root,
        run_directory,
        state,
        provider="azure-monitor-sdk",
        report=sdk_report,
        target_fingerprint=target_fingerprint,
        allow_missing_source_reference=True,
    )
    if not source_bound:
        raise ValueError(f"SDK report execution binding is not current: {source_reason}")

    sdk_evidence, sdk_provider, sdk_errors = _runtime_family(
        root,
        run_directory,
        state,
        provider="azure-monitor-sdk",
        detection_paths=detection_paths,
        target_fingerprint=target_fingerprint,
        allow_missing_source_reference=True,
    )
    if sdk_errors:
        raise ValueError("SDK runtime evidence is incomplete or invalid: " + "; ".join(sdk_errors))
    if not sdk_evidence or any(item.get("status") != "passed" for item in sdk_evidence.values()):
        failures = sorted(
            f"{name}: {item.get('status')} ({item.get('reason') or 'no passing result'})"
            for name, item in sdk_evidence.items()
            if item.get("status") != "passed"
        )
        raise ValueError(
            "SDK runtime family contains a failure, blocked, missing, or stale result"
            + (": " + "; ".join(failures) if failures else "")
        )
    if sdk_report.get("familyComplete") is False:
        raise ValueError("SDK runtime report marks the source query family incomplete")
    expected_count = len(detection_paths)
    if (
        sdk_report.get("total") != expected_count
        or sdk_report.get("valid") != expected_count
        or sdk_report.get("invalid") != 0
        or sdk_report.get("blocked") != 0
        or sdk_report.get("notRun") != 0
    ):
        raise ValueError("SDK summary counts do not prove complete current-family success")
    schema_errors = _typed_sdk_schema_errors(sdk_report)
    if schema_errors:
        raise ValueError("SDK typed schema evidence is incomplete: " + "; ".join(schema_errors))
    for index, item in enumerate(sdk_report.get("results", [])):
        if item.get("status") != "passed" or item.get("valid") is not True or item.get("statusCode") != 200:
            raise ValueError(f"SDK result {index} is not a successful HTTP 200 query result")

    graph_evidence, _, graph_errors = _runtime_family(
        root,
        run_directory,
        state,
        provider="graph",
        detection_paths=detection_paths,
        target_fingerprint=target_fingerprint,
    )
    if graph_errors:
        raise ValueError("Graph runtime evidence is incomplete or invalid: " + "; ".join(graph_errors))
    if not graph_evidence or any(item.get("status") != "passed" for item in graph_evidence.values()):
        failures = sorted(
            f"{name}: {item.get('status')} ({item.get('reason') or 'no passing result'})"
            for name, item in graph_evidence.items()
            if item.get("status") != "passed"
        )
        raise ValueError(
            "Graph runtime family contains a failure, blocked, missing, or stale result"
            + (": " + "; ".join(failures) if failures else "")
        )
    graph_path = run_directory / "runtime-validation.graph.json"
    if not graph_path.is_file():
        raise ValueError("current Graph runtime report is missing")
    graph_report = _read_json(graph_path, "Graph runtime report")
    if (
        graph_report.get("total") != expected_count
        or graph_report.get("valid") != expected_count
        or graph_report.get("invalid") != 0
        or graph_report.get("blocked") != 0
        or graph_report.get("notRun") != 0
    ):
        raise ValueError("Graph summary counts do not prove complete current-family success")
    for index, item in enumerate(graph_report.get("results", [])):
        if item.get("status") != "passed" or item.get("valid") is not True or item.get("statusCode") != 200:
            raise ValueError(f"Graph result {index} is not a successful HTTP 200 query result")
    return sdk_report, sdk_provider, target_fingerprint


def _build_reference_repair_plan(solution: str | Path, run_id: str) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    with using_run(root, run_id):
        run_directory, state = _run_context(root, run_id)
        state_path, state = _load(root)
    validation = (state.get("stages") or {}).get("validation") or {}
    if validation.get("status") != "passed":
        artifacts = validation.get("artifacts") or {}
        source_path = run_directory / "runtime-validation.azure-monitor-sdk.json"
        canonical_ref = artifacts.get("sentinelRuntimeJson")
        reference_ok, reference_reason = _source_runtime_reference_status(
            root,
            run_directory,
            state,
            provider="azure-monitor-sdk",
        )
        if (
            canonical_ref
            and reference_ok
            and source_path.is_file()
        ):
            original_state = state_path.read_bytes()
            result = {
                "schemaVersion": "1.0.0",
                "solution": root.name,
                "runId": run_id,
                "workflowStageStatus": validation.get("status"),
                "action": "already-current-noop",
                "eligible": False,
                "noChange": True,
                "reason": (
                    "canonical source report reference is already correct; "
                    f"validation stage remains unchanged ({validation.get('status')!r})"
                ),
                "sourceProvider": "azure-monitor-sdk",
                "sourceReportPath": source_path.relative_to(root).as_posix(),
                "sourceReportSha256": _sha256(source_path.read_bytes()),
                "validationStatePath": state_path.relative_to(root).as_posix(),
                "validationStateSha256": _sha256(original_state),
                "existingCanonicalReference": canonical_ref,
                "existingLegacyReference": artifacts.get("sentinelRuntimeReport"),
                "desiredCanonicalReference": canonical_ref,
                "stageStatusPreserved": validation.get("status"),
                "stateArtifactsPreserved": sorted(artifacts),
            }
            result["planSha256"] = hashlib.sha256(
                json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            ).hexdigest()
            return result
        raise ValueError(
            f"validation stage is {validation.get('status')!r}; "
            f"repair only augments an already-passed stage "
            f"({reference_reason})"
        )
    sdk_report, sdk_provider, target_fingerprint = _validate_complete_runtime_evidence(
        root, run_directory, state
    )
    artifacts = validation.get("artifacts") or {}
    reference_ok, reference_reason = _source_runtime_reference_status(
        root,
        run_directory,
        state,
        provider="azure-monitor-sdk",
        allow_missing=True,
    )
    if not reference_ok:
        raise ValueError(f"source runtime report reference is conflicting or invalid: {reference_reason}")

    source_path = run_directory / "runtime-validation.azure-monitor-sdk.json"
    graph_path = run_directory / "runtime-validation.graph.json"
    consent_path = run_directory / "runtime-query-consent.json"
    plan_path = run_directory / "runtime-query-plan.json"
    source_hash = _sha256(source_path.read_bytes())
    original_state = state_path.read_bytes()
    legacy_ref = artifacts.get("sentinelRuntimeReport")
    canonical_ref = artifacts.get("sentinelRuntimeJson")
    expected_ref = (source_path.relative_to(root)).as_posix()
    already_current = canonical_ref == expected_ref
    if canonical_ref is None and reference_reason == "provider-runtime-report-reference-current":
        already_current = True
    if canonical_ref is None:
        action = "add-canonical-reference"
    elif already_current:
        action = "already-current"
    else:
        action = "normalize-canonical-reference"
    result = {
        "schemaVersion": "1.0.0",
        "solution": root.name,
        "runId": run_id,
        "workflowStageStatus": validation.get("status"),
        "action": action,
        "eligible": True,
        "reason": "complete current source and Graph evidence is bound to this run and target",
        "targetFingerprintSha256": target_fingerprint,
        "sourceProvider": sdk_provider.get("provider"),
        "sourceReportPath": source_path.relative_to(root).as_posix(),
        "sourceReportSha256": source_hash,
        "runtimeQueryPlanSha256": _sha256(plan_path.read_bytes()),
        "runtimeQueryConsentSha256": _sha256(consent_path.read_bytes()),
        "graphRuntimeReportPath": graph_path.relative_to(root).as_posix(),
        "graphRuntimeReportSha256": _sha256(graph_path.read_bytes()),
        "sourceRuntimeReportSha256": source_hash,
        "validationStatePath": state_path.relative_to(root).as_posix(),
        "validationStateSha256": _sha256(original_state),
        "existingCanonicalReference": canonical_ref,
        "existingLegacyReference": legacy_ref,
        "desiredCanonicalReference": expected_ref,
        "stageStatusPreserved": validation.get("status"),
        "stateArtifactsPreserved": sorted(artifacts),
    }
    result["planSha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return result


def plan_runtime_report_reference_repair(solution: str | Path, run_id: str) -> dict[str, Any]:
    try:
        return _build_reference_repair_plan(solution, run_id)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        return {
            "schemaVersion": "1.0.0",
            "solution": Path(solution).expanduser().resolve().name,
            "runId": run_id,
            "eligible": False,
            "action": "rejected",
            "reason": str(exc),
        }


def _receipt_from_pending(root: Path, pending: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "action": "canonical-reference-added",
        "runId": pending["runId"],
        "planSha256": pending["planSha256"],
        "backupPath": pending["backupPath"],
        "receiptPath": pending["receiptPath"],
        "originalWorkflowStateSha256": pending["originalWorkflowStateSha256"],
        "currentWorkflowStateSha256": pending["currentWorkflowStateSha256"],
        "sourceReportPath": pending["sourceReportPath"],
        "sourceReportSha256": pending["sourceReportSha256"],
        "runtimeQueryPlanSha256": pending["runtimeQueryPlanSha256"],
        "runtimeQueryConsentSha256": pending["runtimeQueryConsentSha256"],
        "graphRuntimeReportPath": pending["graphRuntimeReportPath"],
        "graphRuntimeReportSha256": pending["graphRuntimeReportSha256"],
        "targetFingerprintSha256": pending["targetFingerprintSha256"],
        "legacyReferencePreserved": pending["legacyReferencePreserved"],
        "canonicalReference": pending["canonicalReference"],
        "workflowStageStatusPreserved": pending["workflowStageStatusPreserved"],
    }


def _pending_evidence_matches_plan(
    pending: dict[str, Any],
    plan: dict[str, Any],
) -> bool:
    return all(
        pending.get(pending_key) == plan.get(plan_key)
        for pending_key, plan_key in (
            ("sourceReportPath", "sourceReportPath"),
            ("sourceReportSha256", "sourceReportSha256"),
            ("runtimeQueryPlanSha256", "runtimeQueryPlanSha256"),
            ("runtimeQueryConsentSha256", "runtimeQueryConsentSha256"),
            ("graphRuntimeReportPath", "graphRuntimeReportPath"),
            ("graphRuntimeReportSha256", "graphRuntimeReportSha256"),
            ("targetFingerprintSha256", "targetFingerprintSha256"),
            ("canonicalReference", "desiredCanonicalReference"),
            ("workflowStageStatusPreserved", "stageStatusPreserved"),
        )
    )


def _state_matches_pending_postimage(
    root: Path,
    state_path: Path,
    backup_path: Path,
    pending: dict[str, Any],
) -> bool:
    current_bytes = state_path.read_bytes()
    current_hash = _sha256(current_bytes)
    if pending.get("currentWorkflowStateSha256"):
        return current_hash == pending["currentWorkflowStateSha256"]
    original_bytes = backup_path.read_bytes()
    if _sha256(original_bytes) != pending["originalWorkflowStateSha256"]:
        return False
    original = json.loads(original_bytes)
    expected = _migrate_workflow_state(deepcopy(original))
    context = expected.get("context")
    if isinstance(context, dict):
        context.setdefault("profileSelectionConfirmed", False)
    expected["runId"] = state_path.parent.name
    expected["updatedAt"] = json.loads(current_bytes).get("updatedAt")
    artifacts = expected["stages"]["validation"].setdefault("artifacts", {})
    artifacts["sentinelRuntimeJson"] = pending["canonicalReference"]
    return json.loads(current_bytes) == portable_artifact(root, expected)


def _finish_pending_transaction(
    root: Path,
    pending_path: Path,
    receipt_path: Path,
    pending: dict[str, Any],
) -> dict[str, Any]:
    if pending.get("status") not in {"prepared", "state-written"}:
        raise ValueError("runtime-reference transaction has an unknown recovery state")
    receipt = _receipt_from_pending(root, pending)
    if receipt_path.exists():
        existing = _read_json(receipt_path, "runtime-report reference repair receipt")
        if existing != receipt:
            raise ValueError("existing repair receipt conflicts with pending transaction")
    else:
        _atomic_json(receipt_path, receipt)
    pending_path.unlink()
    return receipt


def apply_runtime_report_reference_repair(
    solution: str | Path,
    run_id: str,
    *,
    expected_plan_sha256: str,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    with using_run(root, run_id):
        from .workflow import _state_writer_lock

        with _state_writer_lock(root) as locked_state_path:
            plan = _build_reference_repair_plan(root, run_id)
            state_path, state = _load(root)
            if state_path != locked_state_path:
                raise ValueError("selected workflow state changed while acquiring the writer lock")
            artifacts = (
                ((state.get("stages") or {}).get("validation") or {}).get("artifacts") or {}
            )
            run_directory = report_directory(root)
            repair_dir = run_directory / "runtime-report-reference-repair"
            if plan.get("action") == "already-current-noop":
                if repair_dir.is_dir():
                    for candidate_path in repair_dir.glob("pending.*.json"):
                        candidate = _read_json(
                            candidate_path,
                            "runtime-report reference transaction",
                        )
                        if candidate.get("runId") == run_id:
                            raise ValueError(
                                "pending runtime-reference transaction cannot be recovered "
                                "because current validation evidence is not passed"
                            )
                return {
                    "runId": run_id,
                    "action": "already-current-noop",
                    "eligible": False,
                    "noChange": True,
                    "workflowStageStatusPreserved": plan.get("stageStatusPreserved"),
                    "reason": plan.get("reason"),
                }
            if not plan.get("eligible"):
                raise ValueError(plan.get("reason") or "runtime-report reference repair is ineligible")
            pending_sha = expected_plan_sha256
            pending_path = repair_dir / f"pending.{pending_sha}.json"
            receipt_path = repair_dir / f"receipt.{pending_sha}.json"
            pending = (
                _read_json(pending_path, "runtime-report reference transaction")
                if pending_path.is_file()
                else None
            )
            if pending is None and plan.get("action") == "already-current":
                pending_paths = (
                    sorted(repair_dir.glob("pending.*.json"))
                    if repair_dir.is_dir()
                    else []
                )
                if plan.get("planSha256") == expected_plan_sha256:
                    candidates = []
                    for candidate_path in pending_paths:
                        candidate = _read_json(
                            candidate_path,
                            "runtime-report reference transaction",
                        )
                        if (
                            candidate.get("runId") == run_id
                            and _pending_evidence_matches_plan(candidate, plan)
                            and plan.get("workflowStageStatus") == "passed"
                        ):
                            candidates.append((candidate_path, candidate))
                    if len(candidates) > 1:
                        raise ValueError(
                            "multiple matching pending runtime-reference transactions exist"
                        )
                    if candidates:
                        pending_path, pending = candidates[0]
                        pending_sha = pending["planSha256"]
                        receipt_path = repair_dir / f"receipt.{pending_sha}.json"
                    elif any(
                        _read_json(path, "runtime-report reference transaction").get("runId")
                        == run_id
                        for path in pending_paths
                    ):
                        raise ValueError(
                            "pending runtime-reference transaction no longer matches current evidence"
                        )
                elif any(
                    _read_json(path, "runtime-report reference transaction").get("runId")
                    == run_id
                    for path in pending_paths
                ):
                    raise ValueError(
                        "pending runtime-reference transaction exists; refresh the plan before recovery"
                    )
            if pending is not None:
                original_hash = pending.get("originalWorkflowStateSha256")
                if not isinstance(original_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", original_hash):
                    raise ValueError("pending runtime-reference transaction has an invalid preimage hash")
                expected_backup = (
                    repair_dir
                    / f"workflow-state.{original_hash}.json"
                )
                if (
                    pending.get("planSha256") != pending_sha
                    or pending_path.name != f"pending.{pending_sha}.json"
                    or not _pending_evidence_matches_plan(pending, plan)
                    or plan.get("workflowStageStatus") != "passed"
                    or pending.get("runId") != run_id
                    or pending.get("backupPath")
                    != expected_backup.relative_to(root).as_posix()
                    or pending.get("receiptPath")
                    != receipt_path.relative_to(root).as_posix()
                ):
                    raise ValueError(
                        "pending runtime-reference transaction is stale or no longer eligible"
                    )
                backup_path = root / pending["backupPath"]
                current_hash = _sha256(state_path.read_bytes())
                is_preimage = (
                    current_hash == pending.get("originalWorkflowStateSha256")
                    and pending.get("status") == "prepared"
                    and not pending.get("currentWorkflowStateSha256")
                )
                is_postimage = _state_matches_pending_postimage(
                    root, state_path, backup_path, pending,
                )
                if not is_preimage and not is_postimage:
                    raise ValueError(
                        "pending runtime-reference transaction conflicts with current workflow state"
                    )
                if is_preimage:
                    artifacts = state["stages"]["validation"].setdefault("artifacts", {})
                    artifacts["sentinelRuntimeJson"] = pending["canonicalReference"]
                    _write_unlocked(state_path, state)
                    current_hash = _sha256(state_path.read_bytes())
                    pending["currentWorkflowStateSha256"] = current_hash
                    pending["status"] = "state-written"
                    _atomic_json(pending_path, pending)
                elif not pending.get("currentWorkflowStateSha256"):
                    pending["currentWorkflowStateSha256"] = current_hash
                    pending["status"] = "state-written"
                    _atomic_json(pending_path, pending)
                if pending.get("currentWorkflowStateSha256") != current_hash:
                    raise ValueError("workflow state changed during runtime-reference recovery")
                return _finish_pending_transaction(
                    root, pending_path, receipt_path, pending,
                )

            if plan.get("action") == "already-current":
                if artifacts.get("sentinelRuntimeJson") != plan.get("desiredCanonicalReference"):
                    raise ValueError("current canonical runtime report reference changed")
                if receipt_path.is_file():
                    receipt = _read_json(receipt_path, "runtime-report reference repair receipt")
                    if (
                        receipt.get("currentWorkflowStateSha256")
                        == _sha256(state_path.read_bytes())
                        and receipt.get("sourceReportSha256") == plan.get("sourceReportSha256")
                        and receipt.get("runtimeQueryPlanSha256")
                        == plan.get("runtimeQueryPlanSha256")
                        and receipt.get("runtimeQueryConsentSha256")
                        == plan.get("runtimeQueryConsentSha256")
                        and receipt.get("graphRuntimeReportSha256")
                        == plan.get("graphRuntimeReportSha256")
                    ):
                        return receipt
                return {
                    "runId": run_id,
                    "action": "already-current",
                    "eligible": True,
                    "noChange": True,
                    "reason": "canonical runtime report reference already matches current evidence",
                }
            if plan["planSha256"] != expected_plan_sha256:
                raise ValueError("runtime-report reference repair plan is stale; dry-run again")
            if _sha256(state_path.read_bytes()) != plan["validationStateSha256"]:
                raise ValueError("workflow state changed since repair planning")
            source_path = root / plan["sourceReportPath"]
            if _sha256(source_path.read_bytes()) != plan["sourceReportSha256"]:
                raise ValueError("SDK report changed since repair planning")

            repair_dir.mkdir(exist_ok=True)
            backup_path = repair_dir / f"workflow-state.{plan['validationStateSha256']}.json"
            if backup_path.exists():
                if _sha256(backup_path.read_bytes()) != plan["validationStateSha256"]:
                    raise ValueError("existing workflow-state backup conflicts with this preimage")
            else:
                with backup_path.open("xb") as backup:
                    backup.write(state_path.read_bytes())
                    backup.flush()
                    os.fsync(backup.fileno())

            pending = {
                "schemaVersion": "1.0.0",
                "status": "prepared",
                "runId": run_id,
                "planSha256": plan["planSha256"],
                "backupPath": backup_path.relative_to(root).as_posix(),
                "receiptPath": receipt_path.relative_to(root).as_posix(),
                "originalWorkflowStateSha256": plan["validationStateSha256"],
                "currentWorkflowStateSha256": None,
                "sourceReportPath": plan["sourceReportPath"],
                "sourceReportSha256": plan["sourceReportSha256"],
                "runtimeQueryPlanSha256": plan["runtimeQueryPlanSha256"],
                "runtimeQueryConsentSha256": plan["runtimeQueryConsentSha256"],
                "graphRuntimeReportPath": plan["graphRuntimeReportPath"],
                "graphRuntimeReportSha256": plan["graphRuntimeReportSha256"],
                "targetFingerprintSha256": plan["targetFingerprintSha256"],
                "legacyReferencePreserved": plan["existingLegacyReference"],
                "canonicalReference": plan["desiredCanonicalReference"],
                "workflowStageStatusPreserved": plan["stageStatusPreserved"],
            }
            _atomic_json(pending_path, pending)
            try:
                artifacts = state["stages"]["validation"].setdefault("artifacts", {})
                artifacts["sentinelRuntimeJson"] = plan["desiredCanonicalReference"]
                _write_unlocked(state_path, state)
                pending["currentWorkflowStateSha256"] = _sha256(state_path.read_bytes())
                pending["status"] = "state-written"
                _atomic_json(pending_path, pending)
                return _finish_pending_transaction(
                    root, pending_path, receipt_path, pending,
                )
            except OSError as exc:
                raise RuntimeError(
                    "runtime-report reference transaction is pending recovery; "
                    f"preserved backup={backup_path} transaction={pending_path}"
                ) from exc
