"""Validate workflow inputs, build matrices, export targets, and clean up DCRs."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from asim_ingestion.azure.common import (
    CanaryConfig,
    DefaultAzureTokenProvider,
    build_resource_names,
)
from asim_ingestion.azure.runner import AsimIngestionHarness

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

    ordered_targets = sorted(
        targets, key=lambda target: target["targetId"]
    )
    for slot, target in enumerate(ordered_targets):
        target["targetSlot"] = slot
        target["targetCount"] = len(ordered_targets)

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


def _short_message(value: Any, limit: int = 500) -> str:
    return str(value or "").replace("\r", " ").replace("\n", " ")[:limit]


def _github_command_message(value: Any) -> str:
    return (
        _short_message(value)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


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
