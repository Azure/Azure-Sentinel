#!/usr/bin/env python3
"""Trusted GitHub Actions helpers for ASIM ingestion-time validation."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from asim_ingestion_harness import (
    DEFAULT_DCE_NAME,
    DEFAULT_INGESTION_ENDPOINT,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP,
    DEFAULT_SUBSCRIPTION_ID,
    DEFAULT_WORKSPACE_ID,
    DEFAULT_WORKSPACE_NAME,
    AsimIngestionHarness,
    CanaryConfig,
    DefaultAzureTokenProvider,
    build_resource_names,
)


WORKFLOW_RESULT_VERSION = 1
TARGET_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
INGEST_PATH_RE = re.compile(
    r"^Parsers/ASim[^/]+/IngestTimeParsers/[^/]+\.yaml$"
)
QUERY_PATH_RE = re.compile(
    r"^Parsers/ASim[^/]+/Parsers/ASim[^/]+\.yaml$"
)
FIXTURE_PATH_RE = re.compile(
    r"^Sample Data/ASIM/[^/]+_IngestedLogs\.csv$"
)
STATUS_ICON = {
    "passed": "✅",
    "failed": "❌",
    "blocked": "⛔",
    "not-applicable": "➖",
    "not-run": "⏭️",
    "warning": "⚠️",
    "shadow-only-failure": "⚠️",
}


class WorkflowContractError(ValueError):
    pass


def _load_json(path: Path, *, required: bool = True) -> Any:
    if not path.is_file():
        if required:
            raise WorkflowContractError(f"Missing JSON file: {path}")
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _normalize_repo_path(value: str, expected_prefix: str) -> str:
    normalized = value.replace("\\", "/").strip()
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or ".." in path.parts
        or not normalized.startswith(expected_prefix)
    ):
        raise WorkflowContractError(
            f"Unsafe repository path: {value!r}"
        )
    return path.as_posix()


def _require_path_pattern(
    value: str, pattern: re.Pattern[str], field: str
) -> str:
    if not pattern.fullmatch(value):
        raise WorkflowContractError(
            f"{field} has an unsupported repository path: {value!r}"
        )
    return value


def _require_identifier(value: Any, field: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise WorkflowContractError(
            f"{field} must be a KQL identifier: {value!r}"
        )
    return value


def _require_target_id(value: Any) -> str:
    if not isinstance(value, str) or not TARGET_ID_RE.fullmatch(value):
        raise WorkflowContractError(
            f"Invalid targetId: {value!r}"
        )
    return value


def _append_discovery_error(
    target: dict[str, Any], message: str
) -> None:
    errors = target.setdefault("discoveryErrors", [])
    if not isinstance(errors, list):
        raise WorkflowContractError(
            "target.discoveryErrors must be an array."
        )
    if message not in errors:
        errors.append(message)


def build_matrix_manifest(
    manifest: Mapping[str, Any],
    *,
    repo_root: Path,
    max_targets: int,
    max_fixture_bytes: int,
) -> dict[str, Any]:
    raw_targets = manifest.get("targets")
    if not isinstance(raw_targets, list):
        raise WorkflowContractError("Manifest targets must be an array.")
    if len(raw_targets) > max_targets:
        raise WorkflowContractError(
            f"Manifest selected {len(raw_targets)} ITP targets; "
            f"the workflow limit is {max_targets}."
        )

    targets: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw_target in raw_targets:
        if not isinstance(raw_target, dict):
            raise WorkflowContractError(
                "Every manifest target must be an object."
            )
        target = deepcopy(raw_target)
        target_id = _require_target_id(target.get("targetId"))
        if target_id in seen_ids:
            raise WorkflowContractError(
                f"Duplicate matrix targetId: {target_id}"
            )
        seen_ids.add(target_id)

        ingest_path = target.get("ingestTimeParserPath")
        if isinstance(ingest_path, str):
            target["ingestTimeParserPath"] = _require_path_pattern(
                _normalize_repo_path(ingest_path, "Parsers/ASim"),
                INGEST_PATH_RE,
                "ingestTimeParserPath",
            )
        query_path = target.get("queryTimeParserPath")
        if isinstance(query_path, str):
            target["queryTimeParserPath"] = _require_path_pattern(
                _normalize_repo_path(query_path, "Parsers/ASim"),
                QUERY_PATH_RE,
                "queryTimeParserPath",
            )
        fixture_path = target.get("fixturePath")
        if isinstance(fixture_path, str):
            fixture_path = _require_path_pattern(
                _normalize_repo_path(
                    fixture_path, "Sample Data/ASIM/"
                ),
                FIXTURE_PATH_RE,
                "fixturePath",
            )
            target["fixturePath"] = fixture_path
            absolute_fixture = repo_root / fixture_path
            if absolute_fixture.is_file():
                fixture_size = absolute_fixture.stat().st_size
                target["fixtureSizeBytes"] = fixture_size
                if fixture_size > max_fixture_bytes:
                    _append_discovery_error(
                        target,
                        f"Fixture exceeds the {max_fixture_bytes}-byte "
                        f"workflow limit: {fixture_path} "
                        f"({fixture_size} bytes).",
                    )

        source_table = target.get("sourceRawTable")
        if source_table is not None:
            _require_identifier(source_table, "sourceRawTable")
        target_table = target.get("targetASIMTable")
        if target_table is not None:
            _require_identifier(target_table, "targetASIMTable")
        targets.append(target)

    groups: dict[str, list[dict[str, Any]]] = {}
    for target in targets:
        group = str(
            target.get("targetASIMTable")
            or f"invalid-{target['targetId']}"
        )
        groups.setdefault(group, []).append(target)
    for group_targets in groups.values():
        ordered = sorted(
            group_targets, key=lambda target: target["targetId"]
        )
        for slot, target in enumerate(ordered):
            target["targetSlot"] = slot
            target["targetCount"] = len(ordered)

    ordered_targets = sorted(
        targets, key=lambda target: target["targetId"]
    )
    output = dict(manifest)
    output["workflowVersion"] = WORKFLOW_RESULT_VERSION
    output["targets"] = ordered_targets
    output["limits"] = {
        "maxTargets": max_targets,
        "maxFixtureBytes": max_fixture_bytes,
    }
    return output


def _write_github_output(
    path: Path | None, values: Mapping[str, Any]
) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for key, value in values.items():
            text = str(value)
            if "\r" in text or "\n" in text:
                raise WorkflowContractError(
                    f"GitHub output {key} contains a newline."
                )
            stream.write(f"{key}={text}\n")


def _append_summary(path: Path | None, markdown: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(markdown.rstrip() + "\n")


def _find_target(
    manifest: Mapping[str, Any], target_id: str
) -> dict[str, Any]:
    targets = manifest.get("targets")
    if not isinstance(targets, list):
        raise WorkflowContractError("Manifest targets must be an array.")
    matches = [
        target
        for target in targets
        if isinstance(target, dict)
        and target.get("targetId") == target_id
    ]
    if len(matches) != 1:
        raise WorkflowContractError(
            f"Expected one target {target_id!r}; found {len(matches)}."
        )
    return matches[0]


def export_target(
    manifest: Mapping[str, Any],
    target_id: str,
    *,
    target_output: Path,
    github_output: Path | None,
) -> dict[str, Any]:
    target = _find_target(manifest, target_id)
    _write_json(target, target_output)
    errors = target.get("discoveryErrors")
    discovery_valid = isinstance(errors, list) and not errors
    values = {
        "target_id": target["targetId"],
        "ingest_time_path": target.get("ingestTimeParserPath") or "",
        "query_time_path": target.get("queryTimeParserPath") or "",
        "fixture_path": target.get("fixturePath") or "",
        "source_raw_table": target.get("sourceRawTable") or "",
        "target_asim_table": target.get("targetASIMTable") or "",
        "pair_status": target.get("pairStatus") or "invalid",
        "target_slot": target.get("targetSlot", 0),
        "target_count": target.get("targetCount", 1),
        "discovery_valid": str(discovery_valid).lower(),
    }
    _write_github_output(github_output, values)
    return target


def export_static_decision(
    static_result: Mapping[str, Any],
    github_output: Path | None,
) -> dict[str, Any]:
    valid = static_result.get("valid") is True
    eligibility = static_result.get("queryTimeEligibility")
    qtp_status = (
        eligibility.get("status")
        if isinstance(eligibility, dict)
        else "not-applicable"
    )
    values = {
        "itp_valid": str(valid).lower(),
        "qtp_status": qtp_status,
        "qtp_eligible": str(qtp_status == "eligible").lower(),
    }
    _write_github_output(github_output, values)
    return values


def write_error_result(
    *,
    stage: str,
    message: str,
    output: Path,
) -> dict[str, Any]:
    if not re.fullmatch(r"[a-z][a-z0-9-]*", stage):
        raise WorkflowContractError(
            f"Invalid workflow error stage: {stage!r}"
        )
    result = {
        "version": WORKFLOW_RESULT_VERSION,
        "status": "failed",
        "error": {
            "type": "WorkflowStageError",
            "stage": stage,
            "message": _short_message(message),
        },
        "cleanup": [],
    }
    _write_json(result, output)
    return result


def cleanup_target(
    *,
    target_id: str,
    pull_request: str,
    run_id: str,
    run_attempt: int,
    config: CanaryConfig,
    deadline_seconds: float = 120,
) -> dict[str, Any]:
    names = build_resource_names(
        target_id,
        pull_request,
        run_id,
        run_attempt,
    )
    harness = AsimIngestionHarness(
        config,
        DefaultAzureTokenProvider(),
        deadline_seconds=deadline_seconds,
    )
    resources = []
    for name in (names["parserDcr"], names["rawDcr"]):
        resources.append(
            harness.delete_dcr(harness.dcr_resource_id(name))
        )
    status = (
        "warning"
        if any(item.get("status") == "warning" for item in resources)
        else "passed"
    )
    return {
        "version": WORKFLOW_RESULT_VERSION,
        "status": status,
        "resources": resources,
    }


def _read_optional_json(path: Path | None) -> Any:
    if path is None or not path.is_file():
        return None
    return _load_json(path)


def _short_message(value: Any, limit: int = 500) -> str:
    text = str(value or "").replace("\r", " ").replace("\n", " ")
    return text[:limit]


def _github_command_message(value: Any) -> str:
    return (
        _short_message(value)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


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


def _config_from_args(args: argparse.Namespace) -> CanaryConfig:
    return CanaryConfig(
        subscription_id=args.subscription_id,
        resource_group=args.resource_group,
        workspace_name=args.workspace_name,
        workspace_id=args.workspace_id,
        dce_name=args.dce_name,
        ingestion_endpoint=args.ingestion_endpoint,
        location=args.location,
    )


def _add_canary_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--subscription-id",
        default=os.getenv(
            "ASIM_CANARY_SUBSCRIPTION_ID",
            DEFAULT_SUBSCRIPTION_ID,
        ),
    )
    parser.add_argument(
        "--resource-group",
        default=os.getenv(
            "ASIM_CANARY_RESOURCE_GROUP",
            DEFAULT_RESOURCE_GROUP,
        ),
    )
    parser.add_argument(
        "--workspace-name",
        default=os.getenv(
            "ASIM_CANARY_WORKSPACE_NAME",
            DEFAULT_WORKSPACE_NAME,
        ),
    )
    parser.add_argument(
        "--workspace-id",
        default=os.getenv(
            "ASIM_CANARY_WORKSPACE_ID",
            DEFAULT_WORKSPACE_ID,
        ),
    )
    parser.add_argument(
        "--dce-name",
        default=os.getenv("ASIM_CANARY_DCE_NAME", DEFAULT_DCE_NAME),
    )
    parser.add_argument(
        "--ingestion-endpoint",
        default=os.getenv(
            "ASIM_CANARY_INGESTION_ENDPOINT",
            DEFAULT_INGESTION_ENDPOINT,
        ),
    )
    parser.add_argument(
        "--location",
        default=os.getenv(
            "ASIM_CANARY_LOCATION", DEFAULT_LOCATION
        ),
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    matrix = subparsers.add_parser("matrix")
    matrix.add_argument("--manifest", type=Path, required=True)
    matrix.add_argument("--output", type=Path, required=True)
    matrix.add_argument("--repo-root", type=Path, default=Path("."))
    matrix.add_argument("--max-targets", type=int, default=25)
    matrix.add_argument(
        "--max-fixture-bytes", type=int, default=5 * 1024 * 1024
    )
    matrix.add_argument("--github-output", type=Path)
    matrix.add_argument("--summary", type=Path)

    export = subparsers.add_parser("export-target")
    export.add_argument("--manifest", type=Path, required=True)
    export.add_argument("--target-id", required=True)
    export.add_argument("--output", type=Path, required=True)
    export.add_argument("--github-output", type=Path)

    static = subparsers.add_parser("export-static")
    static.add_argument("--result", type=Path, required=True)
    static.add_argument("--github-output", type=Path)

    error_result = subparsers.add_parser("error-result")
    error_result.add_argument("--stage", required=True)
    error_result.add_argument("--message", required=True)
    error_result.add_argument("--output", type=Path, required=True)

    cleanup = subparsers.add_parser("cleanup")
    cleanup.add_argument("--target-id", required=True)
    cleanup.add_argument("--pull-request", required=True)
    cleanup.add_argument("--run-id", required=True)
    cleanup.add_argument("--run-attempt", type=int, required=True)
    cleanup.add_argument("--output", type=Path, required=True)
    cleanup.add_argument("--deadline-seconds", type=float, default=120)
    _add_canary_arguments(cleanup)

    report = subparsers.add_parser("report")
    report.add_argument("--target", type=Path, required=True)
    report.add_argument("--static-result", type=Path)
    report.add_argument("--prepared-fixture", type=Path)
    report.add_argument("--validation-result", type=Path)
    report.add_argument("--cleanup-result", type=Path)
    report.add_argument("--repository", required=True)
    report.add_argument("--pull-request", required=True)
    report.add_argument("--run-id", required=True)
    report.add_argument("--run-attempt", required=True)
    report.add_argument("--enforcement-required", required=True)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--summary", type=Path)
    report.add_argument("--github-output", type=Path)
    return parser


def _parse_bool(value: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no", ""}:
        return False
    raise WorkflowContractError(
        f"Expected a boolean value, received {value!r}."
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    try:
        if args.command == "matrix":
            manifest = _load_json(args.manifest)
            matrix_manifest = build_matrix_manifest(
                manifest,
                repo_root=args.repo_root.resolve(),
                max_targets=args.max_targets,
                max_fixture_bytes=args.max_fixture_bytes,
            )
            _write_json(matrix_manifest, args.output)
            target_ids = [
                target["targetId"]
                for target in matrix_manifest["targets"]
            ]
            _write_github_output(
                args.github_output,
                {
                    "has_targets": str(bool(target_ids)).lower(),
                    "target_ids": json.dumps(
                        target_ids, separators=(",", ":")
                    ),
                },
            )
            _append_summary(
                args.summary,
                "## ASIM ingestion target discovery\n\n"
                f"Selected `{len(target_ids)}` ITP target(s).\n",
            )
            return 0

        if args.command == "export-target":
            export_target(
                _load_json(args.manifest),
                args.target_id,
                target_output=args.output,
                github_output=args.github_output,
            )
            return 0

        if args.command == "export-static":
            export_static_decision(
                _load_json(args.result),
                args.github_output,
            )
            return 0

        if args.command == "error-result":
            write_error_result(
                stage=args.stage,
                message=args.message,
                output=args.output,
            )
            return 0

        if args.command == "cleanup":
            result = cleanup_target(
                target_id=_require_target_id(args.target_id),
                pull_request=args.pull_request,
                run_id=args.run_id,
                run_attempt=args.run_attempt,
                config=_config_from_args(args),
                deadline_seconds=args.deadline_seconds,
            )
            _write_json(result, args.output)
            for item in result["resources"]:
                if item.get("status") == "warning":
                    print(
                        "::warning title=ASIM DCR cleanup warning::"
                        + _github_command_message(item.get("message"))
                    )
            return 0

        target = _load_json(args.target)
        report = build_report(
            target=target,
            static_result=_read_optional_json(args.static_result),
            prepared_fixture=_read_optional_json(
                args.prepared_fixture
            ),
            validation_result=_read_optional_json(
                args.validation_result
            ),
            cleanup_result=_read_optional_json(args.cleanup_result),
            repository=args.repository,
            pull_request=args.pull_request,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
            enforcement_required=_parse_bool(
                args.enforcement_required
            ),
        )
        _write_json(report, args.output)
        _append_summary(args.summary, render_summary(report))
        _write_github_output(
            args.github_output,
            {
                "required_failure": str(
                    report["requiredFailure"]
                ).lower(),
                "overall_status": report["status"],
            },
        )
        emit_annotations(report)
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        WorkflowContractError,
        KeyError,
        TypeError,
    ) as exc:
        print(
            f"::error::{_github_command_message(exc)}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
