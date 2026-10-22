"""Build machine-readable results, summaries, and GitHub annotations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    STATUS_ICON,
    WORKFLOW_RESULT_VERSION,
    _github_command_message,
    _load_json,
    _short_message,
)

def _read_optional_json(path: Path | None) -> Any:
    if path is None or not path.is_file():
        return None
    return _load_json(path)


def _stage(
    status: str, detail: str = "", evidence: Any = None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": status,
        "detail": _short_message(detail),
    }
    if evidence is not None:
        result["evidence"] = evidence
    return result


def build_report(
    *,
    target: Mapping[str, Any],
    static_result: Mapping[str, Any] | None,
    prepared_fixture: Mapping[str, Any] | None,
    validation_result: Mapping[str, Any] | None,
    cleanup_result: Mapping[str, Any] | None,
    repository: str,
    pull_request: str,
    run_id: str,
    run_attempt: str,
    enforcement_required: bool,
) -> dict[str, Any]:
    discovery_errors = target.get("discoveryErrors")
    if not isinstance(discovery_errors, list):
        discovery_errors = ["Invalid discoveryErrors contract."]
    discovery = _stage(
        "passed" if not discovery_errors else "failed",
        "" if not discovery_errors else "; ".join(discovery_errors),
        {
            "triggerPaths": target.get("triggerPaths", []),
            "fixturePath": target.get("fixturePath"),
        },
    )

    pair_status = str(target.get("pairStatus") or "invalid")
    qtp_eligibility = (
        static_result.get("queryTimeEligibility")
        if isinstance(static_result, Mapping)
        else None
    )
    if pair_status == "paired":
        qtp_status = (
            qtp_eligibility.get("status")
            if isinstance(qtp_eligibility, Mapping)
            else "not-run"
        )
        counterpart = _stage(
            "passed" if qtp_status == "eligible" else "blocked",
            f"pairStatus={pair_status}; eligibility={qtp_status}",
            {
                "queryTimeParserPath": target.get(
                    "queryTimeParserPath"
                ),
                "pairEvidence": target.get("pairEvidence"),
            },
        )
    elif pair_status == "unpaired":
        counterpart = _stage(
            "not-applicable", "No counterpart QTP resolved."
        )
    elif pair_status == "ambiguous":
        counterpart = _stage(
            "blocked",
            "Multiple QTP candidates block optional execution/parity.",
            {"candidates": target.get("pairCandidates", [])},
        )
    else:
        counterpart = _stage("blocked", f"pairStatus={pair_status}")

    template_valid = (
        isinstance(static_result, Mapping)
        and static_result.get("valid") is True
    )
    template = _stage(
        "passed" if template_valid else "failed",
        (
            ""
            if template_valid
            else _short_message(
                (static_result or {}).get("findings")
                if isinstance(static_result, Mapping)
                else "Static validation did not run."
            )
        ),
        (
            {"findings": static_result.get("findings", [])}
            if isinstance(static_result, Mapping)
            else None
        ),
    )

    validation = (
        validation_result
        if isinstance(validation_result, Mapping)
        else {}
    )
    validation_completed = validation.get("status") == "completed"
    error = validation.get("error")
    error_stage = (
        error.get("stage")
        if isinstance(error, Mapping)
        else None
    )
    error_message = (
        error.get("message")
        if isinstance(error, Mapping)
        else ""
    )

    fixture = _stage(
        "passed" if prepared_fixture is not None else "failed",
        (
            f"{prepared_fixture.get('rowCount')} prepared rows"
            if isinstance(prepared_fixture, Mapping)
            else error_message
            if error_stage == "fixture-preparation"
            else "Fixture preparation did not complete."
        ),
        (
            {
                "path": prepared_fixture.get("fixturePath"),
                "rowCount": prepared_fixture.get("rowCount"),
                "timestampSetHash": (
                    prepared_fixture.get("namespace", {}).get(
                        "timestampSetHash"
                    )
                    if isinstance(
                        prepared_fixture.get("namespace"), Mapping
                    )
                    else None
                ),
            }
            if isinstance(prepared_fixture, Mapping)
            else None
        ),
    )

    raw_dcr = _stage(
        "passed" if validation.get("rawDcr") else (
            "failed" if error_stage in {"raw-table", "dcr-create", "dcr-provisioning"} else "not-run"
        ),
        error_message if error_stage in {"raw-table", "dcr-create", "dcr-provisioning"} else "",
        validation.get("rawDcr"),
    )
    raw_ingestion_failed = error_stage in {
        "upload",
        "upload-reconciliation",
        "raw-visibility",
    } and not validation.get("parserDcr")
    raw_ingestion = _stage(
        "failed"
        if raw_ingestion_failed
        else "passed"
        if validation.get("rawUpload")
        else "not-run",
        error_message if raw_ingestion_failed else "",
        {
            "upload": validation.get("rawUpload", []),
            "snapshot": validation.get("snapshot"),
        },
    )
    filter_validation = validation.get("filterValidation")
    filtering = _stage(
        (
            "passed"
            if isinstance(filter_validation, Mapping)
            and filter_validation.get("status") == "passed"
            else "failed"
            if error_stage == "filter"
            else "not-run"
        ),
        error_message if error_stage == "filter" else "",
        filter_validation,
    )
    parser_dcr = _stage(
        "passed" if validation.get("parserDcr") else (
            "failed" if error_stage in {"dcr-create", "dcr-provisioning"} and validation.get("rawDcr") else "not-run"
        ),
        error_message if error_stage in {"dcr-create", "dcr-provisioning"} and validation.get("rawDcr") else "",
        validation.get("parserDcr"),
    )
    parser_ingestion_failed = error_stage in {
        "upload",
        "upload-reconciliation",
        "target-visibility",
    } and bool(validation.get("parserDcr"))
    parser_ingestion = _stage(
        "failed"
        if parser_ingestion_failed
        else "passed"
        if validation.get("parserUpload")
        else "not-run",
        error_message if parser_ingestion_failed else "",
        validation.get("parserUpload", []),
    )

    output_validation = validation.get("outputValidation")
    schema_validation = (
        output_validation.get("schemaValidation")
        if isinstance(output_validation, Mapping)
        else None
    )
    data_validation = (
        output_validation.get("dataTest")
        if isinstance(output_validation, Mapping)
        else None
    )
    qtp_execution = (
        output_validation.get("queryTimeExecution")
        if isinstance(output_validation, Mapping)
        else None
    )
    parity_validation = (
        output_validation.get("parity")
        if isinstance(output_validation, Mapping)
        else None
    )
    schema_stage = _stage(
        "passed" if validation.get("parserDcr") else (
            "failed" if error_stage == "output-validation" else "not-run"
        ),
        error_message if error_stage == "output-validation" else "",
        schema_validation,
    )
    data_stage = _stage(
        (
            str(data_validation.get("status"))
            if isinstance(data_validation, Mapping)
            else "failed"
            if error_stage == "asim-data"
            else "not-run"
        ),
        error_message if error_stage == "asim-data" else "",
        data_validation,
    )
    if counterpart["status"] in {"not-applicable", "blocked"}:
        qtp_stage = counterpart
        parity_stage = _stage(
            counterpart["status"], counterpart["detail"]
        )
    else:
        qtp_stage = _stage(
            (
                str(qtp_execution.get("status"))
                if isinstance(qtp_execution, Mapping)
                else "passed"
                if error_stage == "parity"
                else "failed"
                if error_stage == "qtp-execution"
                else "not-run"
            ),
            error_message if error_stage == "qtp-execution" else "",
            qtp_execution,
        )
        parity_stage = _stage(
            (
                str(parity_validation.get("status"))
                if isinstance(parity_validation, Mapping)
                else "failed"
                if error_stage == "parity"
                else "not-run"
            ),
            error_message if error_stage == "parity" else "",
            parity_validation or (
                error.get("details")
                if isinstance(error, Mapping)
                and error_stage == "parity"
                else None
            ),
        )

    cleanup_items: list[Any] = []
    validation_cleanup = validation.get("cleanup")
    if isinstance(validation_cleanup, list):
        cleanup_items.extend(validation_cleanup)
    if (
        isinstance(cleanup_result, Mapping)
        and isinstance(cleanup_result.get("resources"), list)
    ):
        cleanup_items.extend(cleanup_result["resources"])
    cleanup_warning = any(
        isinstance(item, Mapping)
        and item.get("status") == "warning"
        for item in cleanup_items
    )
    cleanup_stage = _stage(
        "warning"
        if cleanup_warning
        else "passed"
        if cleanup_items
        else "not-run",
        "Cleanup reported a warning." if cleanup_warning else "",
        cleanup_items,
    )

    required_failure = (
        bool(discovery_errors)
        or not template_valid
        or prepared_fixture is None
        or not validation_completed
    )
    overall_status = (
        "failed"
        if required_failure and enforcement_required
        else "shadow-only-failure"
        if required_failure
        else "passed"
    )
    return {
        "version": WORKFLOW_RESULT_VERSION,
        "status": overall_status,
        "requiredFailure": required_failure,
        "enforcementRequired": enforcement_required,
        "correlation": {
            "repository": repository,
            "pullRequest": pull_request,
            "runId": run_id,
            "runAttempt": run_attempt,
            "targetId": target.get("targetId"),
            "queryTimeParserPath": target.get("queryTimeParserPath"),
            "rawDcr": validation.get("rawDcr"),
            "parserDcr": validation.get("parserDcr"),
        },
        "target": target,
        "stages": {
            "discovery": discovery,
            "counterpart": counterpart,
            "template": template,
            "fixture": fixture,
            "rawDcr": raw_dcr,
            "rawIngestion": raw_ingestion,
            "filtering": filtering,
            "parserDcr": parser_dcr,
            "parserIngestion": parser_ingestion,
            "schema": schema_stage,
            "data": data_stage,
            "qtpExecution": qtp_stage,
            "parity": parity_stage,
            "cleanup": cleanup_stage,
        },
        "telemetry": validation.get("telemetry"),
        "error": error,
    }


def render_summary(report: Mapping[str, Any]) -> str:
    target = report.get("target", {})
    status = str(report.get("status"))
    mode = (
        "required"
        if report.get("enforcementRequired")
        else "shadow"
    )
    lines = [
        f"## ASIM ingestion validation: `{target.get('targetId', 'unknown')}`",
        "",
        f"**Overall:** {STATUS_ICON.get(status, '')} `{status}`  ",
        f"**Mode:** `{mode}`  ",
        f"**ITP:** `{target.get('ingestTimeParserPath', '')}`  ",
        f"**QTP:** `{target.get('queryTimeParserPath') or 'not applicable'}`  ",
        f"**Fixture:** `{target.get('fixturePath') or 'unresolved'}`",
        "",
        "| Stage | Status | Detail |",
        "|---|---|---|",
    ]
    stages = report.get("stages", {})
    if isinstance(stages, Mapping):
        for name, stage in stages.items():
            if not isinstance(stage, Mapping):
                continue
            stage_status = str(stage.get("status", "not-run"))
            detail = _short_message(stage.get("detail")).replace("|", "\\|")
            lines.append(
                f"| {name} | {STATUS_ICON.get(stage_status, '')} "
                f"`{stage_status}` | {detail} |"
            )
    return "\n".join(lines) + "\n"


def emit_annotations(report: Mapping[str, Any]) -> None:
    status = report.get("status")
    target_id = report.get("target", {}).get("targetId", "unknown")
    annotation_kind = "error" if status == "failed" else "warning"
    stages = report.get("stages", {})
    if isinstance(stages, Mapping):
        for stage_name, stage in stages.items():
            if (
                not isinstance(stage, Mapping)
                or stage.get("status") != "failed"
            ):
                continue
            detail = _short_message(
                stage.get("detail") or "Stage failed."
            )
            print(
                f"::{annotation_kind} title=ASIM {stage_name} "
                f"failure::{target_id}: "
                f"{_github_command_message(detail)}"
            )
    if status == "shadow-only-failure":
        print(
            "::warning title=ASIM ingestion validation shadow failure::"
            f"{target_id} failed in shadow mode."
        )
    elif status == "failed":
        print(
            "::error title=ASIM ingestion validation failed::"
            f"{target_id} failed required validation."
        )
    cleanup = report.get("stages", {}).get("cleanup", {})
    if isinstance(cleanup, Mapping) and cleanup.get("status") == "warning":
        print(
            "::warning title=ASIM DCR cleanup warning::"
            f"{target_id} cleanup was incomplete."
        )
