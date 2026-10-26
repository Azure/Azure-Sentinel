from __future__ import annotations

import ctypes
import hashlib
import json
import os
import re
import stat
import sys
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from solution_manager.core.artifacts import (
    RUN_MARKER,
    existing_artifact_path,
    requested_run_id,
    repository_root,
    report_directory,
    using_run,
    portable_artifact,
    write_json_artifact,
)
from solution_manager.core.content_paths import content_path, detection_reference
from solution_manager.migration.converter import (
    _duration_seconds,
    analytic_rule_files,
    custom_detail_schema_errors,
    iso_duration,
    validate_solution,
    xdr_detection_files,
)
from solution_manager.qualification.runtime import current_runtime_query_hash
from solution_manager.core.target_context import require_locked_target


PLAN_NAME = "package-selection-plan.json"
RECEIPT_NAME = "package-selection-applied.json"
STRUCTURAL_NAME = "package-selection-structural-validation.json"
GUID_PATTERN = re.compile(
    r"\A[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\Z"
)
SOURCE_PROVIDER_SURFACES = {
    "triage-mcp": "microsoft-sentinel-triage",
    "azure-monitor-sdk": "log-analytics-workspace",
    "log-analytics-cli": "log-analytics-workspace",
}
SELECTION_FIELDS = {
    "analytic rules": "Analytic Rules",
    "analytics rules": "Analytics Rules",
    "xdr detections": "XDR Detections",
    "custom detections": "Custom Detections",
}
RULE_SEVERITIES = {"Low", "Medium", "High", "Informational"}
RULE_STATUSES = {"Available", "InPreview", "Deprecated"}
RULE_TECHNIQUE_PATTERN = re.compile(r"T\d{4}(?:\.\d{3})?\Z")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _analytic_rule_structure_errors(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return ["Analytic Rule YAML must contain an object"]

    errors: list[str] = []
    string_fields = ("id", "name", "description", "severity", "status", "version", "kind")
    for field in string_fields:
        value = document.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
    if isinstance(document.get("id"), str) and not GUID_PATTERN.fullmatch(document["id"]):
        errors.append("id must be a GUID")
    if isinstance(document.get("version"), str) and not re.fullmatch(
        r"\d+\.\d+\.\d+", document["version"]
    ):
        errors.append("version must use X.Y.Z semantic versioning")
    if isinstance(document.get("severity"), str) and document["severity"] not in RULE_SEVERITIES:
        errors.append("severity must be Low, Medium, High, or Informational")
    if isinstance(document.get("status"), str) and document["status"] not in RULE_STATUSES:
        errors.append("status must be Available, InPreview, or Deprecated")

    kind = document.get("kind")
    if not isinstance(kind, str) or kind not in {"Scheduled", "NRT"}:
        errors.append("kind must be Scheduled or NRT")

    for field, limit, pattern in (
        ("tactics", 5, None),
        ("relevantTechniques", 10, RULE_TECHNIQUE_PATTERN),
    ):
        value = document.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{field} must be a non-empty array")
            continue
        if len(value) > limit:
            errors.append(f"{field} cannot contain more than {limit} entries")
        if any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"{field} entries must be non-empty strings")
        elif pattern and any(not pattern.fullmatch(item) for item in value):
            errors.append(f"{field} contains an invalid technique ID")

    query = document.get("query")
    if not isinstance(query, str) or not query.strip():
        errors.append("query must be a non-empty string")

    connectors = document.get("requiredDataConnectors")
    if not isinstance(connectors, list) or not connectors:
        errors.append("requiredDataConnectors must be a non-empty array")
    else:
        for index, connector in enumerate(connectors):
            if not isinstance(connector, dict):
                errors.append(f"requiredDataConnectors[{index}] must be an object")
                continue
            if not isinstance(connector.get("connectorId"), str) or not connector["connectorId"].strip():
                errors.append(f"requiredDataConnectors[{index}].connectorId must be a non-empty string")
            data_types = connector.get("dataTypes")
            if (
                not isinstance(data_types, list)
                or not data_types
                or any(not isinstance(item, str) or not item.strip() for item in data_types)
            ):
                errors.append(f"requiredDataConnectors[{index}].dataTypes must be a non-empty string array")

    scheduled_fields = ("queryFrequency", "queryPeriod", "triggerOperator", "triggerThreshold")
    if kind == "NRT":
        for field in scheduled_fields:
            if field in document:
                errors.append(f"NRT rules must not include {field}")
    elif kind == "Scheduled":
        frequency = document.get("queryFrequency")
        period = document.get("queryPeriod")
        for field, value in (("queryFrequency", frequency), ("queryPeriod", period)):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} must be a non-empty timespan string")
            elif iso_duration(value)[1]:
                errors.append(f"{field} must be a recognized timespan")
        frequency_seconds = _duration_seconds(frequency) if isinstance(frequency, str) else None
        period_seconds = _duration_seconds(period) if isinstance(period, str) else None
        if frequency_seconds is not None and frequency_seconds < 300:
            errors.append("queryFrequency must be at least 5 minutes")
        if period_seconds is not None and period_seconds < 300:
            errors.append("queryPeriod must be at least 5 minutes")
        if (
            frequency_seconds is not None
            and period_seconds is not None
            and period_seconds < frequency_seconds
        ):
            errors.append("queryPeriod cannot be less than queryFrequency")
        if period_seconds is not None and period_seconds > 14 * 24 * 60 * 60:
            errors.append("queryPeriod cannot exceed 14 days")

        operator = document.get("triggerOperator")
        if not isinstance(operator, str) or operator not in {"gt", "lt", "eq"}:
            errors.append("triggerOperator must be gt, lt, or eq")
        threshold = document.get("triggerThreshold")
        if (
            not isinstance(threshold, int)
            or isinstance(threshold, bool)
            or not 0 <= threshold <= 10_000
        ):
            errors.append("triggerThreshold must be an integer between 0 and 10000")
    return errors


def _canonical_sha256(value: Any) -> str:
    return _sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8"))


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is missing or invalid: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return value


def _relative_artifact(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _solution_binding_matches(value: Any, root: Path) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if value == ".":
        return True
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve() == root.resolve()
    return value.casefold() == root.name.casefold()


def _runtime_target_fingerprint(target: dict[str, Any]) -> str:
    return _canonical_sha256({
        key: target[key]
        for key in (
            "tenantId",
            "subscriptionId",
            "resourceGroup",
            "workspaceResourceId",
            "workspaceName",
            "workspaceCustomerId",
        )
    })


def _manifest_reference(value: Any, family: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"conversion manifest has an invalid {family} path")
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if (
        normalized.startswith("/")
        or re.match(r"^[A-Za-z]:", normalized)
        or "\x00" in normalized
        or any(part in {"", ".", ".."} for part in parts)
        or parts[0].casefold() != family.casefold()
        or Path(parts[-1]).suffix.casefold() not in {".yaml", ".yml"}
    ):
        raise ValueError(f"conversion manifest has an unsafe {family} path: {value!r}")
    return "/".join(parts)


def _run_context(solution: str | Path, run_id: str) -> tuple[Path, dict[str, Any]]:
    root = Path(solution).expanduser().resolve()
    with using_run(root, run_id):
        run_directory = report_directory(root)
    marker = _read_json(run_directory / RUN_MARKER, "migration run marker")
    state = _read_json(run_directory / "workflow-state.json", "workflow state")
    if marker.get("runId") != run_id or state.get("runId") != run_id:
        raise ValueError("selected run ID does not match its current run marker and workflow state")
    if not _solution_binding_matches(state.get("solution"), root):
        raise ValueError("workflow state is bound to a different solution")
    if (state.get("context") or {}).get("profileSelectionConfirmed") is not True:
        raise ValueError("package selection requires an explicitly confirmed workflow profile")
    return run_directory, state


def _data_file(root: Path) -> Path:
    paths = sorted((root / "Data").glob("Solution_*.json"))
    if len(paths) != 1:
        raise ValueError(
            f"expected exactly one Data/Solution_*.json file, found {len(paths)}"
        )
    return paths[0]


def _case_key(document: dict[str, Any], key: str) -> str | None:
    matches = [name for name in document if name.casefold() == key.casefold()]
    if len(matches) > 1:
        raise ValueError(f"solution data has duplicate case-insensitive {key!r} properties")
    return matches[0] if matches else None


def _content_reference(root: Path, value: Any, family: str) -> tuple[str, Path]:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{family} selection contains an invalid reference")
    text = value.replace("\\", "/")
    parts = text.split("/")
    if (
        text.startswith("/")
        or re.match(r"^[A-Za-z]:", text)
        or any(part in {"", ".", ".."} for part in parts)
        or "\x00" in text
    ):
        raise ValueError(f"unsafe {family} content reference: {value!r}")
    selected_root = root.resolve()
    repository = repository_root(selected_root).resolve()
    try:
        selected_prefix = selected_root.relative_to(repository).parts
    except ValueError:
        selected_prefix = ()
    if (
        len(selected_prefix) == 2
        and selected_prefix[0].casefold() == "solutions"
        and selected_prefix[1].casefold() == selected_root.name.casefold()
        and len(parts) > len(selected_prefix)
        and tuple(part.casefold() for part in parts[:len(selected_prefix)])
        == tuple(part.casefold() for part in selected_prefix)
    ):
        parts = parts[len(selected_prefix):]
    if not parts or parts[0].casefold() != family.casefold():
        raise ValueError(f"unsafe {family} content reference: {value!r}")
    text = "/".join(parts)
    path = content_path(root, text).resolve()
    if not path.is_relative_to(root.resolve()) or path.is_symlink() or not path.is_file():
        raise ValueError(f"{family} reference does not resolve to a safe file: {value!r}")
    if path.suffix.casefold() not in {".yaml", ".yml"}:
        raise ValueError(f"{family} reference must point to a YAML file: {value!r}")
    return path.relative_to(root).as_posix(), path


def _selection_arrays(
    root: Path,
    document: dict[str, Any],
    *,
    allow_missing_xdr: bool = False,
) -> dict[str, list[str]]:
    source_keys = [
        key for key in ("Analytic Rules", "Analytics Rules")
        if _case_key(document, key) is not None
    ]
    if len(source_keys) > 1:
        raise ValueError("solution data contains ambiguous Analytic Rules selection arrays")
    xdr_keys = [
        key for key in ("XDR Detections", "Custom Detections")
        if _case_key(document, key) is not None
    ]
    if len(xdr_keys) > 1:
        raise ValueError("solution data contains ambiguous XDR Detection selection arrays")
    if (
        not xdr_keys
        and not allow_missing_xdr
        and xdr_detection_files(root / "XDR Detections")
    ):
        raise ValueError(
            "solution data is missing an explicit XDR Detections array; "
            "folder discovery is not a package-selection policy"
        )

    result: dict[str, list[str]] = {"analyticRules": [], "xdrDetections": []}
    for family, key, prefix in (
        ("analyticRules", source_keys[0] if source_keys else None, "Analytic Rules"),
        ("xdrDetections", xdr_keys[0] if xdr_keys else None, "XDR Detections"),
    ):
        if key is None:
            continue
        values = document[key]
        if not isinstance(values, list):
            raise ValueError(f"solution data {key} must be an array")
        paths = []
        seen: set[str] = set()
        for value in values:
            relative, _ = _content_reference(root, value, prefix)
            normalized = relative.casefold()
            if normalized in seen:
                raise ValueError(f"duplicate {key} content reference: {value!r}")
            seen.add(normalized)
            paths.append(relative)
        result[family] = paths
    return result


def _data_context_sha256(document: dict[str, Any]) -> str:
    context = {
        key: value for key, value in document.items()
        if key.casefold() not in {
            "version", "analytic rules", "analytics rules",
            "xdr detections", "custom detections",
        }
    }
    return _canonical_sha256(context)


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"invalid {label} YAML: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} YAML must contain an object: {path}")
    return value


def _validation_evidence(root: Path, run_directory: Path) -> tuple[dict[str, Any], dict[str, str]]:
    with using_run(root, run_directory.name):
        validation = validate_solution(root)
    results: dict[str, dict[str, Any]] = {}
    full_hashes: dict[str, str] = {}
    for path in analytic_rule_files(root):
        relative = path.relative_to(root).as_posix()
        digest = _sha256(path.read_bytes())
        full_hashes[relative] = digest
        try:
            source = _load_yaml(path, "Analytic Rule")
            source_errors = _analytic_rule_structure_errors(source)
        except (
            OSError,
            ValueError,
            yaml.YAMLError,
            TypeError,
            AttributeError,
            OverflowError,
        ) as exc:
            source_errors = [str(exc)]
        results[relative] = {
            "status": "failed" if source_errors else "passed",
            "errors": source_errors,
            "kind": "analyticRule",
        }
    for path in xdr_detection_files(root / "XDR Detections"):
        relative = path.relative_to(root).as_posix()
        digest = _sha256(path.read_bytes())
        full_hashes[relative] = digest
        results[relative] = {"status": "notRun", "errors": [], "kind": "customDetection"}
    for item in validation.get("results", []):
        raw_path = Path(str(item.get("file") or ""))
        try:
            relative = raw_path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            raise ValueError("structural validator returned a path outside the selected solution")
        if relative not in results:
            raise ValueError(f"structural validator returned an unknown detection path: {relative}")
        if results[relative]["status"] != "notRun":
            raise ValueError(f"structural validator returned duplicate results for {relative}")
        results[relative] = {
            "status": "passed" if item.get("valid") is True else "failed",
            "errors": [str(error) for error in item.get("errors", [])],
            "kind": "customDetection",
        }
    report = {
        "schemaVersion": "1.0.0",
        "validator": "sentinel_xdr_migration.converter.validate_solution",
        "runId": run_directory.name,
        "total": len(results),
        "valid": sum(item["status"] == "passed" for item in results.values()),
        "invalid": sum(item["status"] == "failed" for item in results.values()),
        "results": [
            {
                "file": name,
                "fileSha256": full_hashes[name],
                "kind": results[name]["kind"],
                **results[name],
            }
            for name in sorted(results)
        ],
    }
    return report, full_hashes


def _coverage_summary(
    source_inventory: list[dict[str, Any]],
    validated_source_ids: set[str] | list[str],
) -> dict[str, Any]:
    source_ids = [str(item.get("id") or "") for item in source_inventory]
    source_keys = [value.casefold() for value in source_ids]
    if (
        not source_ids
        or any(not GUID_PATTERN.fullmatch(value) for value in source_ids)
        or len(source_keys) != len(set(source_keys))
    ):
        denominator = 0
        source_ids = []
        source_keys = []
    validated_by_key = {
        value.casefold(): value for value in validated_source_ids
        if isinstance(value, str) and GUID_PATTERN.fullmatch(value)
    }
    if not set(validated_by_key).issubset(set(source_keys)):
        raise ValueError("validated migrated detections do not bind to the complete source inventory")
    validated_ids = sorted(
        validated_by_key[key] for key in validated_by_key
    )
    denominator = len(source_ids)
    numerator = len(validated_ids)
    return {
        "coveragePolicy": "strictly-greater-than-50-percent-of-original-sentinel-rules",
        "originalSourceRuleCount": denominator,
        "originalSourceRuleIds": sorted(source_ids, key=str.casefold),
        "validatedMigratedSourceRuleCount": numerator,
        "validatedMigratedSourceRuleIds": validated_ids,
        "coverageNumerator": numerator,
        "coverageDenominator": denominator,
        "coveragePercent": (100.0 * numerator / denominator) if denominator else 0.0,
        "partialPublicationAllowed": denominator > 0 and 2 * numerator > denominator,
    }


def _partial_coverage_allowed(summary: dict[str, Any]) -> bool:
    source_ids = summary.get("originalSourceRuleIds")
    validated_ids = summary.get("validatedMigratedSourceRuleIds")
    denominator = summary.get("originalSourceRuleCount")
    numerator = summary.get("validatedMigratedSourceRuleCount")
    if (
        not isinstance(source_ids, list)
        or not isinstance(validated_ids, list)
        or not isinstance(denominator, int)
        or isinstance(denominator, bool)
        or not isinstance(numerator, int)
        or isinstance(numerator, bool)
        or denominator <= 0
        or denominator != len(source_ids)
        or numerator != len(validated_ids)
        or summary.get("coverageNumerator") != numerator
        or summary.get("coverageDenominator") != denominator
        or summary.get("coveragePolicy")
        != "strictly-greater-than-50-percent-of-original-sentinel-rules"
        or summary.get("partialPublicationAllowed") is not True
        or numerator < 0
        or numerator > denominator
    ):
        return False
    source_keys = [str(value).casefold() for value in source_ids]
    validated_keys = [str(value).casefold() for value in validated_ids]
    return (
        all(GUID_PATTERN.fullmatch(str(value)) for value in source_ids)
        and all(GUID_PATTERN.fullmatch(str(value)) for value in validated_ids)
        and len(source_keys) == len(set(source_keys))
        and len(validated_keys) == len(set(validated_keys))
        and set(validated_keys).issubset(set(source_keys))
        and 2 * numerator > denominator
    )


def _report_path(run_directory: Path, state: dict[str, Any], name: str) -> Path:
    path = run_directory / name
    return path


def _current_target(
    root: Path,
    state: dict[str, Any],
    *,
    materialize_missing: bool = True,
) -> tuple[dict[str, str] | None, str | None]:
    profile = (state.get("context") or {}).get("workflowProfile")
    if profile != "qualification":
        return None, None
    run_id = state.get("runId")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("qualification package selection requires a bound workflow run ID")
    with using_run(root, run_id):
        target = require_locked_target(root, materialize_missing=materialize_missing)
    return target, _runtime_target_fingerprint(target)


def _source_runtime_reference_status(
    root: Path,
    run_directory: Path,
    state: dict[str, Any],
    *,
    provider: str,
    allow_missing: bool = False,
) -> tuple[bool, str]:
    artifacts = (
        ((state.get("stages") or {}).get("validation") or {}).get("artifacts") or {}
    )
    references = []
    for key in ("sentinelRuntimeJson", "sentinelRuntimeReport"):
        value = artifacts.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            return False, "source-runtime-report-reference-invalid"
        normalized = value.replace("\\", "/")
        if "\x00" in normalized or ".." in normalized.split("/"):
            return False, "source-runtime-report-reference-unsafe-path"
        references.append((key, normalized))
    if not references:
        return (
            (True, "source-runtime-report-reference-missing")
            if allow_missing
            else (False, "source-runtime-report-not-bound-to-validation-stage")
        )

    expected = (run_directory / f"runtime-validation.{provider}.json").resolve()
    resolved: list[Path] = []
    for _, value in references:
        path = Path(value)
        candidates = [path] if path.is_absolute() else [root / path, run_directory / path]
        matches = []
        for candidate in candidates:
            try:
                if candidate.resolve() == expected:
                    matches.append(candidate.resolve())
            except OSError:
                continue
        if not matches:
            return False, "source-runtime-report-reference-provider-or-path-mismatch"
        resolved.append(matches[0])
    if len(set(resolved)) != 1:
        return False, "source-runtime-report-reference-conflict"
    return True, "provider-runtime-report-reference-current"


def _runtime_binding(
    root: Path,
    run_directory: Path,
    state: dict[str, Any],
    *,
    provider: str,
    report: dict[str, Any],
    target_fingerprint: str | None,
    allow_missing_source_reference: bool = False,
) -> tuple[bool, str]:
    profile = (state.get("context") or {}).get("workflowProfile")
    family = "defenderXdrQueryFamily" if provider == "graph" else "sentinelSourceQueryFamily"
    plan_path = run_directory / "runtime-query-plan.json"
    if not plan_path.is_file():
        return False, "provider-runtime-plan-binding-missing"
    plan = _read_json(plan_path, "runtime query plan")
    plan_target = plan.get("target") or {}
    family_plan = (plan.get("families") or {}).get(family) or {}
    provider_plan = family_plan.get("provider") or {}
    if (
        plan.get("runId") != run_directory.name
        or plan.get("workflowProfile") != profile
        or not _solution_binding_matches(plan.get("solution"), root)
        or plan_target.get("fingerprintSha256") != target_fingerprint
        or not isinstance(provider_plan, dict)
        or provider_plan.get("provider") != provider
        or report.get("provider") != provider
    ):
        return False, "provider-runtime-plan-binding-stale-or-mismatched"
    snapshots = []
    for field in ("runtimeQueryConsent", "runtimeQueryDispatchSnapshot"):
        snapshot = report.get(field)
        if not isinstance(snapshot, dict):
            return False, "provider-runtime-execution-binding-missing"
        snapshots.append(snapshot)
    for snapshot in snapshots:
        binding = snapshot.get("binding")
        if (
            snapshot.get("status") not in {"approved", "derived-from-lab-consent"}
            or snapshot.get("provider") != provider
            or snapshot.get("family") != family
            or snapshot.get("planSha256") != plan.get("planSha256")
            or not isinstance(binding, dict)
            or binding.get("runId") != run_directory.name
            or binding.get("workflowProfile") != profile
            or not _solution_binding_matches(binding.get("solution"), root)
            or not target_fingerprint
            or binding.get("targetFingerprintSha256") != target_fingerprint
        ):
            return False, "provider-runtime-execution-binding-stale-or-mismatched"
    if provider != "graph":
        reference_ok, reference_reason = _source_runtime_reference_status(
            root,
            run_directory,
            state,
            provider=provider,
            allow_missing=allow_missing_source_reference,
        )
        if not reference_ok:
            return False, reference_reason
        consent_path = run_directory / "runtime-query-consent.json"
        if not consent_path.is_file():
            return False, "source-runtime-target-consent-binding-missing"
        consent = _read_json(consent_path, "runtime query consent")
        consent_binding = consent.get("binding") or {}
        if (
            consent.get("status") not in {"approved", "derived-from-lab-consent"}
            or family not in consent.get("approvedFamilies", [])
            or consent.get("planSha256") != plan.get("planSha256")
            or consent_binding.get("runId") != run_directory.name
            or consent_binding.get("workflowProfile") != profile
            or not _solution_binding_matches(consent_binding.get("solution"), root)
            or consent_binding.get("targetFingerprintSha256") != target_fingerprint
        ):
            return False, "source-runtime-target-consent-binding-stale-or-mismatched"
    return True, "provider-target-binding-current"


def _runtime_family(
    root: Path,
    run_directory: Path,
    state: dict[str, Any],
    *,
    provider: str,
    detection_paths: dict[str, Path],
    target_fingerprint: str | None,
    allow_missing_source_reference: bool = False,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], list[str]]:
    report_path = run_directory / f"runtime-validation.{provider}.json"
    expected_surface = (
        "defender-advanced-hunting"
        if provider == "graph"
        else SOURCE_PROVIDER_SURFACES[provider]
    )

    def unavailable(status: str, reason: str, report_hash: str | None = None):
        base = {
            "provider": provider,
            "querySurface": expected_surface,
            "runId": run_directory.name,
            "targetFingerprintSha256": target_fingerprint,
            "providerBindingStatus": "not-established",
        }
        if report_hash:
            base["reportSha256"] = report_hash
            base["evidencePath"] = _relative_artifact(
                root, report_path,
            )
        return (
            {
                name: {**base, "status": status, "reason": reason}
                for name in detection_paths
            },
            {
                **base,
                "reportPath": _relative_artifact(root, report_path),
                "reportSha256": report_hash,
                "status": status,
            },
        )

    evidence: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    if not report_path.is_file():
        missing_evidence, provider_evidence = unavailable(
            "missing", "runtime-report-missing",
        )
        return missing_evidence, provider_evidence, errors
    raw = report_path.read_bytes()
    try:
        report = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        invalid_evidence, provider_evidence = unavailable(
            "invalid", "runtime-report-invalid", _sha256(raw),
        )
        return invalid_evidence, provider_evidence, [
            f"{provider} runtime report is invalid: {exc}"
        ]
    if not isinstance(report, dict) or report.get("provider") != provider:
        mismatch_evidence, provider_evidence = unavailable(
            "invalid", "runtime-provider-mismatch", _sha256(raw),
        )
        return mismatch_evidence, provider_evidence, [
            f"{provider} runtime report provider does not match its selected route"
        ]
    if report.get("querySurface") != expected_surface:
        errors.append(f"{provider} runtime report query surface does not match its selected provider")
    if report.get("providerFailure"):
        errors.append(f"{provider} runtime report records a provider failure")
    if report.get("familyComplete") is False:
        errors.append(f"{provider} runtime report marks the detection family incomplete")
    bound, binding_reason = _runtime_binding(
        root, run_directory, state, provider=provider, report=report,
        target_fingerprint=target_fingerprint,
        allow_missing_source_reference=allow_missing_source_reference,
    )
    if not bound:
        errors.append(f"{provider} runtime report is not bound to the current run and target")
    raw_results = report.get("results")
    if not isinstance(raw_results, list):
        raw_results = []
        errors.append(f"{provider} runtime report has no results inventory")
    by_name: dict[str, dict[str, Any]] = {}
    expected_names = set(detection_paths)
    for item in raw_results:
        if not isinstance(item, dict):
            errors.append(f"{provider} runtime report contains a malformed result")
            continue
        name = str(item.get("detection") or "").replace("\\", "/")
        if name.startswith("XDR Detections/"):
            name = name[len("XDR Detections/"):]
        try:
            canonical_name = detection_reference(name, list(expected_names))
        except ValueError:
            errors.append(f"{provider} runtime report contains an unknown or ambiguous detection result")
            continue
        if canonical_name in by_name:
            errors.append(f"{provider} runtime report contains duplicate results")
        else:
            by_name[canonical_name] = item
    missing_names = sorted(expected_names - set(by_name))
    if missing_names:
        errors.append(
            f"{provider} runtime report is missing expected detection results: "
            + ", ".join(missing_names)
        )
    report_failed = bool(
        report.get("providerFailure")
        or report.get("familyComplete") is False
        or errors
    )
    for name, detection_path in detection_paths.items():
        entry = by_name.get(name)
        if report_failed:
            result = {"status": "blocked", "reason": "runtime-provider-or-inventory-error"}
        elif entry is None:
            result = {"status": "missing", "reason": "runtime-result-missing"}
        else:
            try:
                expected_query_hash = current_runtime_query_hash(
                    root, detection_path,
                    provider="graph" if provider == "graph" else provider,
                )
            except (OSError, ValueError, yaml.YAMLError):
                expected_query_hash = None
            actual_hash = entry.get("querySha256")
            status = str(entry.get("status") or "missing")
            result = {
                "status": status,
                "querySha256": actual_hash if isinstance(actual_hash, str) else None,
                "expectedQuerySha256": expected_query_hash,
                "evidencePath": (
                    f"{_relative_artifact(root, report_path)}#results:{name}"
                ),
                "reportSha256": _sha256(raw),
            }
            for field in (
                "failureKind", "statusCode", "schemaColumnCount", "tables",
                "sourceMissing", "reasonCode", "errorCode",
            ):
                value = entry.get(field)
                if isinstance(value, (str, int, bool, list)):
                    result[field] = value
            if expected_query_hash is None or actual_hash != expected_query_hash:
                result.update(status="stale", reason="runtime-query-hash-stale")
            elif provider != "graph" and status == "passed":
                from solution_manager.authoring.dependencies import dependency_identity

                current_document = yaml.safe_load(detection_path.read_text(encoding="utf-8-sig"))
                if entry.get("dependencyProvenanceSha256") != dependency_identity(current_document):
                    result.update(status="stale", reason="runtime-dependency-provenance-stale")
            elif status != "passed":
                result["reason"] = f"runtime-result-{status}"
            elif provider == "graph":
                schema = entry.get("schema")
                if not isinstance(schema, list):
                    result.update(status="invalid", reason="graph-output-schema-missing")
                else:
                    columns = []
                    seen: set[str] = set()
                    for column in schema:
                        if not isinstance(column, dict):
                            columns = []
                            break
                        column_name = column.get("name", column.get("Name"))
                        column_type = column.get("type", column.get("Type"))
                        if (
                            not isinstance(column_name, str) or not column_name.strip()
                            or not isinstance(column_type, str) or not column_type.strip()
                            or column_name.casefold() in seen
                        ):
                            columns = []
                            break
                        seen.add(column_name.casefold())
                        columns.append(column)
                    if not columns:
                        result.update(status="invalid", reason="graph-output-schema-invalid")
                    else:
                        document = _load_yaml(detection_path, "Custom Detection")
                        binding_errors = custom_detail_schema_errors(document, columns)
                        if binding_errors:
                            result.update(
                                status="invalid",
                                reason="graph-output-schema-binding-invalid",
                                schemaErrors=[str(error) for error in binding_errors],
                            )
                        else:
                            result["schemaSha256"] = _canonical_sha256(columns)
        result.update({
            "provider": provider,
            "querySurface": expected_surface,
            "runId": run_directory.name,
            "targetFingerprintSha256": target_fingerprint,
            "providerBindingStatus": binding_reason,
            "reportPath": _relative_artifact(root, report_path),
            "reportSha256": _sha256(raw),
            "evidencePath": (
                f"{_relative_artifact(root, report_path)}#results:{name}"
            ),
        })
        evidence[name] = result
    return (
        evidence,
        {
            "provider": provider,
            "querySurface": expected_surface,
            "reportPath": _relative_artifact(root, report_path),
            "reportSha256": _sha256(raw),
            "bindingStatus": binding_reason,
            "reportStatus": "error" if errors else "available",
            "familyComplete": report.get("familyComplete"),
            "providerFallback": bool(report.get("providerFallback")),
            "providerFailure": {
                key: report["providerFailure"][key]
                for key in ("failureKind", "statusCode")
                if isinstance(report.get("providerFailure"), dict)
                and key in report["providerFailure"]
            } or None,
        },
        errors,
    )


def _current_review_report(run_directory: Path, run_id: str) -> tuple[dict[str, Any] | None, Path | None]:
    path = run_directory / "migration-report.json"
    if not path.is_file():
        return None, None
    document = _read_json(path, "current migration review report")
    workflow = document.get("workflow") or {}
    if workflow.get("runId") != run_id:
        return None, path
    return document, path


def _review_evidence_sha256(report: dict[str, Any] | None) -> str | None:
    if report is None:
        return None
    workflow = report.get("workflow")
    workflow = workflow if isinstance(workflow, dict) else {}
    rules = report.get("rules")
    if not isinstance(rules, list):
        return _canonical_sha256({"runId": workflow.get("runId"), "rules": None})
    projection = []
    for rule in rules:
        if not isinstance(rule, dict):
            projection.append({"invalidReviewRecord": rule})
            continue
        analytic = rule.get("analyticRule")
        analytic = analytic if isinstance(analytic, dict) else {}
        custom = rule.get("customDetection")
        custom = custom if isinstance(custom, dict) else {}
        projection.append({
            "sourceFilePresent": (
                isinstance(rule.get("sourceFile"), str)
                and bool(rule.get("sourceFile").strip())
            ),
            "sourceSha256": rule.get("sourceSha256"),
            "analyticRuleId": analytic.get("id"),
            "conversionStatus": custom.get("conversionStatus"),
            "reviewRequired": custom.get("reviewRequired"),
            "reviewScope": custom.get("reviewScope"),
            "reviewDecisions": custom.get("reviewDecisions"),
        })
    projection.sort(
        key=lambda item: (
            str(item.get("analyticRuleId") or "").casefold(),
            str(item.get("sourceSha256") or ""),
        )
    )
    return _canonical_sha256({
        "runId": workflow.get("runId"),
        "rules": projection,
    })


def _source_provider_route_errors(run_directory: Path, provider: str) -> list[str]:
    providers = ("triage-mcp", "azure-monitor-sdk", "log-analytics-cli")
    if provider not in providers:
        return [f"unknown selected Sentinel runtime provider: {provider}"]
    reports = run_directory
    available = [
        (name, reports / f"runtime-validation.{name}.json")
        for name in providers
        if (reports / f"runtime-validation.{name}.json").is_file()
    ]
    selected_index = next(
        (index for index, (name, _) in enumerate(available) if name == provider),
        None,
    )
    if selected_index is None:
        return []
    selected_path = available[selected_index][1]
    try:
        selected_report = json.loads(selected_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return [f"{provider} runtime report is invalid"]
    if not isinstance(selected_report, dict) or selected_report.get("provider") != provider:
        return [f"{provider} runtime report provider does not match"]
    if selected_index == 0:
        if selected_report.get("providerFallback"):
            return [f"{provider} runtime report claims an unverified provider fallback"]
        return []

    triage_path = reports / "runtime-validation.triage-mcp.json"
    try:
        triage_report = json.loads(triage_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ["Sentinel provider fallback has no valid preceding Triage report"]
    if (
        not isinstance(triage_report, dict)
        or triage_report.get("provider") != "triage-mcp"
        or not isinstance(triage_report.get("providerFailure"), dict)
        or bool(triage_report.get("providerFallback"))
    ):
        return [
            "Sentinel provider fallback requires a current Triage provider-failure report"
        ]
    proof = selected_report.get("providerFallback")
    if (
        not isinstance(proof, dict)
        or proof.get("mcpProvider") != "triage-mcp"
        or proof.get("fallbackProvider") != provider
        or proof.get("batchComplete") is not True
        or proof.get("permissionsVerified") is not True
        or proof.get("kqlError") is not False
    ):
        return [
            f"{provider} runtime report lacks the canonical verified Triage fallback proof"
        ]
    return []


def _build_package_selection_plan(
    solution: str | Path,
    run_id: str,
    *,
    candidate_lists_override: dict[str, list[str]] | None = None,
    xdr_array_was_missing_override: bool | None = None,
    xdr_references_bootstrapped_override: bool | None = None,
    bootstrap_missing_outputs_override: list[dict[str, str]] | None = None,
    persist_structural: bool = False,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    run_directory, state = _run_context(root, run_id)
    data_path = _data_file(root)
    try:
        data = json.loads(data_path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot parse solution data {data_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("solution data must contain a JSON object")
    arrays = _selection_arrays(root, data, allow_missing_xdr=True)
    xdr_array_was_missing = (
        _case_key(data, "XDR Detections") is None
        and _case_key(data, "Custom Detections") is None
    )
    if xdr_array_was_missing_override is not None:
        xdr_array_was_missing = xdr_array_was_missing_override
    candidate_lists = (
        {
            name: list(candidate_lists_override[name])
            for name in ("analyticRules", "xdrDetections")
        }
        if candidate_lists_override is not None
        else dict(arrays)
    )
    for name in ("analyticRules", "xdrDetections"):
        if not isinstance(candidate_lists.get(name), list):
            raise ValueError(f"selection plan has an invalid {name} candidate list")
    context_hash = _data_context_sha256(data)

    manifest_path = run_directory / "manifest.json"
    manifest = _read_json(manifest_path, "current conversion manifest")
    if (
        (manifest.get("scope") or {}).get("kind") != "solution"
        or not isinstance(manifest.get("results"), list)
        or manifest.get("total") != len(manifest.get("results", []))
    ):
        raise ValueError("package selection requires a complete full-solution conversion manifest")
    manifest_by_source: dict[str, dict[str, Any]] = {}
    manifest_by_output: dict[str, dict[str, Any]] = {}
    seen_manifest_sources: set[str] = set()
    seen_manifest_outputs: set[str] = set()
    for record in manifest["results"]:
        source = _manifest_reference(record.get("sourceRelativePath"), "Analytic Rules")
        output = _manifest_reference(record.get("outputRelativePath"), "XDR Detections")
        if source.casefold() in seen_manifest_sources or output.casefold() in seen_manifest_outputs:
            raise ValueError("conversion manifest contains duplicate artifact paths")
        seen_manifest_sources.add(source.casefold())
        seen_manifest_outputs.add(output.casefold())
        manifest_by_source[source] = record
        manifest_by_output[output] = record

    xdr_references_bootstrapped = (
        xdr_references_bootstrapped_override
        if xdr_references_bootstrapped_override is not None
        else bool(xdr_array_was_missing and candidate_lists_override is None)
    )
    bootstrap_missing_outputs: list[dict[str, str]] = (
        deepcopy(bootstrap_missing_outputs_override)
        if bootstrap_missing_outputs_override is not None
        else []
    )
    if xdr_references_bootstrapped:
        if candidate_lists_override is None:
            manifest_outputs = sorted(manifest_by_output)
            manifest_references: list[str] = []
            for output in manifest_outputs:
                relative = output
                path = content_path(root, output).resolve()
                if not path.is_relative_to(root) or path.is_symlink():
                    raise ValueError(f"conversion manifest output is not a safe path: {output}")
                if path.is_file():
                    manifest_references.append(relative)
                else:
                    source = next(
                        source
                        for source, record in manifest_by_source.items()
                        if record.get("outputRelativePath") == output
                    )
                    bootstrap_missing_outputs.append({
                        "sourcePath": source,
                        "outputPath": output,
                        "reason": "conversion-output-missing",
                    })
            candidate_lists["xdrDetections"] = manifest_references

    detection_paths = {
        path.relative_to(root / "XDR Detections").as_posix(): path
        for path in xdr_detection_files(root / "XDR Detections")
    }
    structural_report, structural_hashes = _validation_evidence(root, run_directory)
    structural_path = run_directory / STRUCTURAL_NAME
    structural_bytes = (json.dumps(structural_report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    structural_hash = _sha256(structural_bytes)
    if persist_structural:
        write_json_artifact(root, structural_path, structural_report)
        if _sha256(structural_path.read_bytes()) != structural_hash:
            structural_hash = _sha256(structural_path.read_bytes())
    elif structural_path.is_file() and _sha256(structural_path.read_bytes()) != structural_hash:
        raise ValueError("current local structural-validation evidence changed after selection planning")

    target, target_fingerprint = _current_target(root, state)
    source_provider = None
    source_plan = _read_json(run_directory / "runtime-query-plan.json", "runtime query plan") if (run_directory / "runtime-query-plan.json").is_file() else {}
    source_provider_doc = (
        ((source_plan.get("families") or {}).get("sentinelSourceQueryFamily") or {}).get("provider") or {}
    )
    source_provider = source_provider_doc.get("provider") if isinstance(source_provider_doc, dict) else None
    if source_provider not in SOURCE_PROVIDER_SURFACES:
        source_artifacts = ((state.get("stages") or {}).get("validation") or {}).get("artifacts") or {}
        for key in ("sentinelRuntimeJson", "sentinelRuntimeReport"):
            source_ref = source_artifacts.get(key)
            if isinstance(source_ref, str):
                name = Path(source_ref.replace("\\", "/")).name
                match = re.fullmatch(
                    r"runtime-validation\.(triage-mcp|azure-monitor-sdk|log-analytics-cli)\.json",
                    name,
                )
                if match:
                    source_provider = match.group(1)
                    break
    source_runtime, source_provider_evidence, source_errors = _runtime_family(
        root, run_directory, state, provider=source_provider or "azure-monitor-sdk",
        detection_paths=detection_paths, target_fingerprint=target_fingerprint,
    )
    graph_runtime, graph_provider_evidence, graph_errors = _runtime_family(
        root, run_directory, state, provider="graph",
        detection_paths=detection_paths, target_fingerprint=target_fingerprint,
    )
    source_route_errors = _source_provider_route_errors(
        run_directory, source_provider or "azure-monitor-sdk",
    )
    source_provider_evidence["routeStatus"] = (
        "passed" if not source_route_errors else "failed"
    )
    source_provider_evidence["routeErrors"] = source_route_errors
    source_errors.extend(source_route_errors)

    review_report, review_path = _current_review_report(run_directory, run_id)
    review_by_id: dict[str, dict[str, Any]] = {}
    if review_report is not None:
        for rule in review_report.get("rules", []):
            analytic = rule.get("analyticRule") or {}
            source_id = str(analytic.get("id") or "").casefold()
            if source_id:
                if source_id in review_by_id:
                    raise ValueError("current migration report contains duplicate source IDs")
                review_by_id[source_id] = rule
    review_evidence_hash = _review_evidence_sha256(review_report)

    selected_sources = {p.casefold() for p in candidate_lists["analyticRules"]}
    selected_detections = {
        p[len("XDR Detections/"):].casefold()
        for p in candidate_lists["xdrDetections"]
    }
    all_source_paths = {
        path.relative_to(root).as_posix(): path for path in analytic_rule_files(root)
    }
    current_source_keys = {path.casefold() for path in all_source_paths}
    stale_manifest_sources = sorted(
        source for source in manifest_by_source
        if source.casefold() not in current_source_keys
    )
    selection_errors = [
        f"conversion manifest source is not present in the current solution: {source}"
        for source in stale_manifest_sources
    ]
    missing_manifest_sources = sorted(
        source for source in all_source_paths
        if source.casefold() not in {item.casefold() for item in manifest_by_source}
    )
    selection_errors.extend(
        f"full-solution conversion manifest omits current source inventory item: {source}"
        for source in missing_manifest_sources
    )
    source_ids: dict[str, list[str]] = {}
    source_records: dict[str, dict[str, Any]] = {}
    for relative, path in all_source_paths.items():
        source_doc = _load_yaml(path, "Analytic Rule")
        source_id = str(source_doc.get("id") or "")
        if not GUID_PATTERN.fullmatch(source_id):
            raise ValueError(f"Analytic Rule has an invalid or missing template ID: {relative}")
        key = source_id.casefold()
        source_ids.setdefault(key, []).append(relative)
        source_records[relative] = {
            "id": source_id,
            "querySha256": None,
            "fileSha256": _sha256(path.read_bytes()),
            "structuralStatus": "passed",
            "structuralReason": None,
            "selectedInData": relative.casefold() in selected_sources,
            "manifest": manifest_by_source.get(relative),
        }
    duplicate_sources = [source_id for source_id, paths in source_ids.items() if len(paths) != 1]
    if duplicate_sources:
        raise ValueError("duplicate source Analytic Rule IDs make the packaging selection ambiguous")

    structural_by_path = {item["file"]: item for item in structural_report["results"]}
    for relative, facts in source_records.items():
        structural = structural_by_path.get(relative, {})
        if structural.get("fileSha256") != facts["fileSha256"]:
            facts["structuralStatus"] = "stale"
            facts["structuralReason"] = "source-structural-validation-file-hash-mismatch"
        else:
            facts["structuralStatus"] = structural.get("status", "missing")
            if structural.get("errors"):
                facts["structuralReason"] = "; ".join(structural["errors"])
    for output_name, path in detection_paths.items():
        source_status = source_runtime.get(output_name) or {}
        try:
            source_records[next(
                source for source in source_records
                if source.casefold() == str(
                    (_load_yaml(path, "Custom Detection").get("contentProvenance") or {})
                    .get("source", {}).get("path", "")
                ).replace("\\", "/").casefold()
            )]["querySha256"] = source_status.get("expectedQuerySha256")
        except (StopIteration, KeyError, AttributeError):
            pass

    analytic_inventory: list[dict[str, Any]] = []
    eligible_source_ids: set[str] = set()
    for relative, facts in sorted(source_records.items()):
        reasons: list[str] = []
        checks: dict[str, dict[str, Any]] = {}
        manifest_record = facts["manifest"]
        source_path = all_source_paths[relative]
        source_id = facts["id"]
        review = review_by_id.get(source_id.casefold())
        conversion_ok = bool(
            manifest_record
            and manifest_record.get("status") in {"converted", "needsReview"}
            and not manifest_record.get("errors")
        )
        checks["conversion"] = {
            "status": "passed" if conversion_ok else "failed",
            "manifestPath": _relative_artifact(root, manifest_path),
        }
        if not conversion_ok:
            reasons.append("conversion-not-currently-converted-or-reviewed")
        if review is None or review.get("sourceSha256") != facts["fileSha256"]:
            checks["conversionReviewBinding"] = {"status": "stale", "evidencePath": _relative_artifact(root, review_path) if review_path else None}
            reasons.append("source-file-or-review-evidence-stale")
        else:
            source_structural = (
                isinstance(review.get("sourceFile"), str)
                and str(review.get("analyticRule", {}).get("id") or "").casefold() == source_id.casefold()
            )
            checks["conversionReviewBinding"] = {
                "status": "passed" if source_structural else "failed",
                "evidencePath": _relative_artifact(root, review_path) if review_path else None,
                "reviewEvidenceSha256": review_evidence_hash,
            }
            if not source_structural:
                reasons.append("source-review-evidence-mismatch")
        checks["sourceYamlStructure"] = {
            "status": facts["structuralStatus"],
            "fileSha256": facts["fileSha256"],
            "evidencePath": _relative_artifact(root, structural_path),
            "evidenceSha256": structural_hash,
            **({"reason": facts["structuralReason"]} if facts["structuralReason"] else {}),
        }
        if facts["structuralStatus"] != "passed":
            reasons.append(facts["structuralReason"] or "source-yaml-structure-invalid")
        if not facts["selectedInData"]:
            reasons.append("not-in-current-analytic-rule-selection")
        try:
            query_hash = current_runtime_query_hash(
                root,
                next(
                    path for path in detection_paths.values()
                    if str(((_load_yaml(path, "Custom Detection").get("contentProvenance") or {}).get("source") or {}).get("path", "")).replace("\\", "/").casefold() == relative.casefold()
                ),
                provider=source_provider or "azure-monitor-sdk",
            )
        except (StopIteration, OSError, ValueError, yaml.YAMLError):
            query_hash = None
        facts["querySha256"] = query_hash
        runtime_entry = next(
            (
                source_runtime.get(name, {})
                for name, path in detection_paths.items()
                if str(((_load_yaml(path, "Custom Detection").get("contentProvenance") or {}).get("source") or {}).get("path", "")).replace("\\", "/").casefold() == relative.casefold()
            ),
            {},
        )
        runtime_ok = (
            runtime_entry.get("status") == "passed"
            and runtime_entry.get("expectedQuerySha256") == query_hash
        )
        checks["sourceRuntime"] = {
            **runtime_entry,
            "status": "passed" if runtime_ok else runtime_entry.get("status", "missing"),
        }
        if not runtime_ok:
            reasons.append(runtime_entry.get("reason") or "source-runtime-not-passed-for-current-query")
        if not reasons:
            eligible_source_ids.add(source_id.casefold())
        analytic_inventory.append({
            "id": source_id,
            "path": relative,
            "fileSha256": facts["fileSha256"],
            "querySha256": query_hash,
            "checks": checks,
            "evidencePaths": sorted({
                _relative_artifact(root, manifest_path),
                *([_relative_artifact(root, review_path)] if review_path else []),
                *([runtime_entry["evidencePath"]] if runtime_entry.get("evidencePath") else []),
            }),
            "eligible": not reasons,
            "included": not reasons,
            "reasons": reasons,
        })

    xdr_inventory: list[dict[str, Any]] = []
    analytic_by_id = {
        item["id"].casefold(): item for item in analytic_inventory
    }
    for output_name, path in sorted(detection_paths.items()):
        document = _load_yaml(path, "Custom Detection")
        provenance = (document.get("contentProvenance") or {}).get("source") or {}
        source_id = str(provenance.get("id") or "")
        source_relative = str(provenance.get("path") or "").replace("\\", "/")
        properties = document.get("properties") or {}
        detection_id = str(properties.get("id") or "")
        record = manifest_by_output.get(f"XDR Detections/{output_name}")
        source_matches = source_ids.get(source_id.casefold(), []) if source_id else []
        reasons: list[str] = []
        checks: dict[str, dict[str, Any]] = {}
        if len(source_matches) != 1 or source_matches[0].casefold() != source_relative.casefold():
            reasons.append("source-provenance-does-not-resolve-exactly-one-analytic-rule")
            checks["sourceProvenance"] = {"status": "failed"}
        else:
            checks["sourceProvenance"] = {"status": "passed", "sourcePath": source_relative}
        if not detection_id:
            reasons.append("custom-detection-id-missing")
        conversion = (document.get("contentProvenance") or {}).get("conversion") or {}
        conversion_ok = bool(
            record
            and record.get("status") == "converted"
            and record.get("reviewRequired") is False
            and not record.get("errors")
            and conversion.get("status") == "converted"
            and conversion.get("reviewRequired") is False
            and conversion.get("scope", "solution") != "rule"
        )
        checks["conversion"] = {
            "status": "passed" if conversion_ok else "failed",
            "manifestPath": _relative_artifact(root, manifest_path),
        }
        if not conversion_ok:
            reasons.append("conversion-not-currently-converted-or-reviewed")
        review = review_by_id.get(source_id.casefold())
        current_source = all_source_paths.get(source_relative)
        current_source_hash = _sha256(current_source.read_bytes()) if current_source else None
        current_conversion = (
            (document.get("contentProvenance") or {}).get("conversion") or {}
        )
        review_custom = (review.get("customDetection") or {}) if review else {}
        current_scope_sha = _canonical_sha256(
            current_conversion.get("reviewScope") or {}
        )
        reviewed_scope_sha = _canonical_sha256(
            review_custom.get("reviewScope") or {}
        )
        current_decisions_sha = _canonical_sha256(
            current_conversion.get("reviewDecisions") or []
        )
        reviewed_decisions_sha = _canonical_sha256(
            review_custom.get("reviewDecisions") or []
        )
        review_binding_ok = bool(
            review
            and current_source_hash
            and review.get("sourceSha256") == current_source_hash
            and str((review.get("analyticRule") or {}).get("id") or "").casefold() == source_id.casefold()
            and review_custom.get("conversionStatus", current_conversion.get("status"))
            == current_conversion.get("status")
            and review_custom.get("reviewRequired")
            == current_conversion.get("reviewRequired")
            and reviewed_scope_sha == current_scope_sha
            and reviewed_decisions_sha == current_decisions_sha
        )
        review_required = (
            current_conversion.get("reviewRequired") if review_binding_ok else None
        )
        checks["review"] = {
            "status": (
                "passed" if review_binding_ok and review_required is False
                else "unresolved" if review_binding_ok and review_required is True
                else "missing-or-stale"
            ),
            "evidencePath": _relative_artifact(root, review_path) if review_path else None,
            "reviewEvidenceSha256": review_evidence_hash,
            "reviewScopeSha256": _canonical_sha256(
                review_custom.get("reviewScope") or {}
            ) if review else None,
            "reviewDecisionsSha256": _canonical_sha256(
                review_custom.get("reviewDecisions") or []
            ) if review else None,
            "currentReviewScopeSha256": current_scope_sha,
            "currentReviewDecisionsSha256": current_decisions_sha,
        }
        if not review_binding_ok:
            reasons.append("source-or-review-evidence-stale-or-missing")
        elif review_required is True:
            reasons.append("unresolved-review-required")
        elif review_required is not False:
            reasons.append("source-or-review-evidence-stale-or-missing")
        structural = structural_by_path.get(f"XDR Detections/{output_name}", {})
        structure_ok = structural.get("status") == "passed" and structural_hashes.get(f"XDR Detections/{output_name}") == _sha256(path.read_bytes())
        checks["currentStructuralValidation"] = {
            "status": "passed" if structure_ok else structural.get("status", "missing"),
            "fileSha256": _sha256(path.read_bytes()),
            "evidencePath": _relative_artifact(root, structural_path),
            "evidenceSha256": structural_hash,
        }
        if not structure_ok:
            reasons.append("current-structural-validation-not-passed")
        if output_name.casefold() not in selected_detections:
            reasons.append("not-in-current-xdr-detection-selection")
        runtime_entry = graph_runtime.get(output_name, {})
        graph_ok = runtime_entry.get("status") == "passed"
        checks["graphRuntime"] = runtime_entry
        if not graph_ok:
            reasons.append(runtime_entry.get("reason") or "graph-runtime-not-passed-for-current-query")
        source_analytic = analytic_by_id.get(source_id.casefold())
        if source_analytic is None or not source_analytic.get("included"):
            reasons.append("source-analytic-rule-is-not-included")
        if not reasons:
            selected_detections.add(output_name.casefold())
        xdr_inventory.append({
            "id": detection_id,
            "sourceId": source_id,
            "sourcePath": source_relative or None,
            "path": f"XDR Detections/{output_name}",
            "fileSha256": _sha256(path.read_bytes()),
            "sourceQuerySha256": source_runtime.get(output_name, {}).get("expectedQuerySha256"),
            "advancedHuntingQuerySha256": graph_runtime.get(output_name, {}).get("expectedQuerySha256"),
            "checks": checks,
            "evidencePaths": sorted({
                _relative_artifact(root, manifest_path),
                _relative_artifact(root, structural_path),
                *([_relative_artifact(root, review_path)] if review_path else []),
                *([source_runtime[output_name]["evidencePath"]] if source_runtime.get(output_name, {}).get("evidencePath") else []),
                *([graph_runtime[output_name]["evidencePath"]] if graph_runtime.get(output_name, {}).get("evidencePath") else []),
            }),
            "eligible": not reasons,
            "included": not reasons,
            "reasons": reasons,
        })

    original_source_inventory = [
        {
            "id": facts["id"],
            "path": relative,
            "fileSha256": facts["fileSha256"],
        }
        for relative, facts in sorted(source_records.items())
    ]
    validated_migrated_source_ids = {
        str(item.get("sourceId") or "").casefold()
        for item in xdr_inventory
        if item.get("included") is True
    }
    source_id_by_key = {
        item["id"].casefold(): item["id"]
        for item in original_source_inventory
    }
    coverage = _coverage_summary(
        original_source_inventory,
        {
            source_id_by_key[key]
            for key in validated_migrated_source_ids
            if key in source_id_by_key
        },
    )
    source_inventory_sha256 = _canonical_sha256(original_source_inventory)

    # A failed source rule remains accounted for independently; only its paired
    # Custom Detection is removed by the source-AR closure check above.
    result: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "kind": "evidence-based-v3.1-package-selection",
        "solution": ".",
        "runId": run_id,
        "workflowProfile": (state.get("context") or {}).get("workflowProfile"),
        "targetFingerprintSha256": target_fingerprint,
        "providers": {
            "sentinel": source_provider_evidence,
            "graph": graph_provider_evidence,
        },
        "executionErrors": sorted(set(source_errors + graph_errors + selection_errors)),
        "input": {
            "solutionDataPath": _relative_artifact(root, data_path),
            "solutionDataSha256AtPlan": _sha256(data_path.read_bytes()),
            "solutionDataContextSha256": context_hash,
            "versionAtPlan": next(
                (value for key, value in data.items() if key.casefold() == "version"),
                None,
            ),
            "xdrArrayWasMissing": xdr_array_was_missing,
            "xdrReferencesBootstrappedFromManifest": xdr_references_bootstrapped,
            "bootstrapManifestOutputReferences": (
                list(candidate_lists["xdrDetections"])
                if xdr_references_bootstrapped
                else []
            ),
            "bootstrapMissingOutputs": bootstrap_missing_outputs,
            "candidateReferences": candidate_lists,
            "conversionManifestPath": _relative_artifact(root, manifest_path),
            "conversionManifestSha256": _sha256(manifest_path.read_bytes()),
            "migrationReportPath": _relative_artifact(root, review_path) if review_path else None,
            "migrationReviewEvidenceSha256": review_evidence_hash,
            "structuralValidationPath": _relative_artifact(root, structural_path),
            "structuralValidationSha256": structural_hash,
            "originalSourceInventory": original_source_inventory,
            "originalSourceInventorySha256": source_inventory_sha256,
        },
        "analyticRules": analytic_inventory,
        "xdrDetections": xdr_inventory,
        "selection": {
            "analyticRules": [item["path"] for item in analytic_inventory if item["included"]],
            "xdrDetections": [item["path"] for item in xdr_inventory if item["included"]],
        },
        "summary": {
            "analyticRuleTotal": len(analytic_inventory),
            "analyticRuleIncluded": sum(item["included"] for item in analytic_inventory),
            "analyticRuleExcluded": sum(not item["included"] for item in analytic_inventory),
            "xdrDetectionTotal": len(xdr_inventory),
            "xdrDetectionIncluded": sum(item["included"] for item in xdr_inventory),
            "xdrDetectionExcluded": sum(not item["included"] for item in xdr_inventory),
            **coverage,
            "outcome": (
                "blocked"
                if bool(source_errors + graph_errors + selection_errors)
                or coverage["originalSourceRuleCount"] == 0
                or not coverage["partialPublicationAllowed"]
                or not any(item["included"] for item in analytic_inventory)
                else "partial"
                if any(not item["included"] for item in (*analytic_inventory, *xdr_inventory))
                else "complete"
            ),
            "eligibilityBlockReason": (
                "empty-or-invalid-original-source-inventory"
                if coverage["originalSourceRuleCount"] == 0
                else "no-eligible-analytic-rules"
                if not any(item["included"] for item in analytic_inventory)
                else "validated-migrated-detection-coverage-not-over-50-percent"
                if not coverage["partialPublicationAllowed"]
                else None
            ),
        },
    }
    result["planSha256"] = _selection_plan_hash(result)
    return result


def _selection_plan_hash(plan: dict[str, Any]) -> str:
    value = deepcopy(plan)
    value.pop("planSha256", None)
    value.pop("createdAt", None)
    value.get("input", {}).pop("solutionDataSha256AtPlan", None)
    value.get("input", {}).pop("versionAtPlan", None)
    return _canonical_sha256(value)


def _write_selection_receipt(solution: Path, path: Path, receipt: dict[str, Any]) -> None:
    payload = (
        json.dumps(portable_artifact(solution, receipt), indent=2) + "\n"
    ).encode("utf-8")
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        if path.read_bytes() != payload:
            raise RuntimeError("package selection apply receipt changed during publication")
    finally:
        try:
            temporary.unlink()
        except OSError:
            pass


def _file_snapshot(path: Path) -> tuple[bytes, tuple[int, int, int, int, int]]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"solution data must be a regular non-symlink file: {path}")
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        content = stream.read()
        after = os.fstat(stream.fileno())
    current = path.stat()

    def identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
        return (
            value.st_dev,
            value.st_ino,
            value.st_size,
            value.st_mtime_ns,
            stat.S_IMODE(value.st_mode),
        )

    before_identity = identity(before)
    if before_identity != identity(after) or before_identity != identity(current):
        raise RuntimeError(f"file changed while reading its package-selection snapshot: {path}")
    return content, before_identity


def _exchange_paths_windows(left: Path, right: Path) -> None:
    """Exchange two same-directory files using ReplaceFileW plus a private backup.

    ReplaceFileW atomically puts ``left`` at ``right`` and moves the previous
    ``right`` into the backup name; the backup is then renamed to ``left``. The
    first step is the commit boundary: the displaced ``right`` bytes are exactly
    what was replaced. ``left`` must be a private name no other writer uses.
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
    replace_file = kernel32.ReplaceFileW
    replace_file.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_void_p,
    )
    replace_file.restype = ctypes.c_int
    move_file = kernel32.MoveFileExW
    move_file.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    move_file.restype = ctypes.c_int
    backup = left.with_name(f".{left.name}.{uuid.uuid4().hex}.bak")
    if not replace_file(str(right), str(left), str(backup), 0, None, None):
        error = ctypes.get_last_error()  # type: ignore[attr-defined]
        raise OSError(None, ctypes.FormatError(error).strip(), f"{left} <-> {right}", error)
    # MOVEFILE_WRITE_THROUGH
    if not move_file(str(backup), str(left), 0x8):
        error = ctypes.get_last_error()  # type: ignore[attr-defined]
        raise OSError(
            None,
            ctypes.FormatError(error).strip(),
            f"exchange completed but displaced file retained at {backup}",
            error,
        )


def _exchange_paths(left: Path, right: Path) -> None:
    if sys.platform == "win32":
        _exchange_paths_windows(left, right)
        return
    if sys.platform == "darwin":
        symbol = "renameatx_np"
        current_directory = -2
    elif sys.platform.startswith("linux"):
        symbol = "renameat2"
        current_directory = -100
    else:
        raise RuntimeError(
            "package-selection apply requires an atomic same-filesystem path exchange; "
            f"unsupported platform: {sys.platform}"
        )
    library = ctypes.CDLL(None, use_errno=True)
    exchange = getattr(library, symbol, None)
    if exchange is None:
        raise RuntimeError(
            "package-selection apply requires an atomic same-filesystem path exchange; "
            f"{symbol} is unavailable"
        )
    exchange.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    exchange.restype = ctypes.c_int
    # RENAME_SWAP on Darwin and RENAME_EXCHANGE on Linux share flag value 2.
    if exchange(
        current_directory,
        os.fsencode(left),
        current_directory,
        os.fsencode(right),
        2,
    ) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), f"{left} <-> {right}")


def _atomic_exchange_if_unchanged(
    path: Path,
    content: bytes,
    expected: tuple[bytes, tuple[int, int, int, int, int]],
) -> tuple[bytes, tuple[int, int, int, int, int]]:
    """Atomically exchange staged bytes after the caller excludes external writers.

    The migration writer lock serializes this tool's own updates. Filesystem
    exchange is used to detect an edit made before commit, but editors that do
    not honor that lock must not modify the solution-data file during apply.
    """
    expected_bytes, expected_identity = expected
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, expected_identity[4])
    preserve_temporary = False
    try:
        with os.fdopen(descriptor, "wb") as stream:
            os.chmod(temporary, expected_identity[4])
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        staged = _file_snapshot(temporary)
        _exchange_paths(temporary, path)
        displaced = _file_snapshot(temporary)
        if displaced != expected or displaced[0] != expected_bytes:
            current = _file_snapshot(path)
            if current == staged:
                _exchange_paths(temporary, path)
                restored = _file_snapshot(temporary)
                if restored == staged:
                    raise RuntimeError(
                        f"solution data changed during package-selection update; "
                        f"the concurrent edit was restored: {path}"
                    )
                preserve_temporary = True
            else:
                preserve_temporary = True
            raise RuntimeError(
                f"solution data changed during package-selection update; "
                f"concurrent file evidence retained at {temporary}"
            )
        written = _file_snapshot(path)
        if written[0] != content:
            raise RuntimeError(f"solution data changed during package-selection commit: {path}")
        return written
    finally:
        if not preserve_temporary:
            try:
                temporary.unlink()
            except OSError:
                pass


def create_package_selection_plan(solution: str | Path, run_id: str) -> dict[str, Any]:
    plan = _build_package_selection_plan(
        solution, run_id, persist_structural=True,
    )
    with using_run(solution, run_id):
        path = report_directory(solution, create=True) / PLAN_NAME
    write_json_artifact(solution, path, plan)
    return {
        "status": (
            "ready"
            if not plan["executionErrors"] and plan["summary"]["outcome"] != "blocked"
            else "blocked"
        ),
        "planPath": _relative_artifact(Path(solution).resolve(), path),
        **plan,
    }


def _load_selection_plan(solution: str | Path, run_id: str) -> tuple[Path, dict[str, Any]]:
    with using_run(solution, run_id):
        path = report_directory(solution) / PLAN_NAME
    plan = _read_json(path, "package selection plan")
    if plan.get("runId") != run_id or plan.get("planSha256") != _selection_plan_hash(plan):
        raise ValueError("package selection plan is invalid or belongs to another run")
    return path, plan


def apply_package_selection(
    solution: str | Path,
    run_id: str,
    *,
    expected_plan_sha256: str,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    from solution_manager.core.workflow import _state_writer_lock

    with _state_writer_lock(root):
        return _apply_package_selection_unlocked(
            root,
            run_id,
            expected_plan_sha256=expected_plan_sha256,
        )


def _apply_package_selection_unlocked(
    solution: str | Path,
    run_id: str,
    *,
    expected_plan_sha256: str,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    plan_path, plan = _load_selection_plan(root, run_id)
    if plan.get("planSha256") != expected_plan_sha256:
        raise ValueError("expected package selection hash does not match the saved plan")
    if plan.get("executionErrors"):
        raise ValueError("package selection plan contains execution errors and cannot be applied")
    if plan.get("summary", {}).get("outcome") == "blocked":
        reason = (plan.get("summary") or {}).get("eligibilityBlockReason")
        if reason == "validated-migrated-detection-coverage-not-over-50-percent":
            raise ValueError(
                "validated migrated Custom Detections must represent strictly more "
                "than 50% of the original Sentinel rule inventory"
            )
        raise ValueError(
            "package selection plan has no eligible Analytic Rules and cannot be applied"
        )
    current = _build_package_selection_plan(root, run_id)
    if current["planSha256"] != plan["planSha256"]:
        raise ValueError("package selection plan is stale; regenerate and review it before applying")

    data_path = _data_file(root)
    original_data_snapshot = _file_snapshot(data_path)
    original_data_bytes = original_data_snapshot[0]
    try:
        data = json.loads(original_data_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot parse solution data {data_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("solution data must contain a JSON object")
    arrays = _selection_arrays(root, data, allow_missing_xdr=True)
    xdr_array_missing_now = (
        _case_key(data, "XDR Detections") is None
        and _case_key(data, "Custom Detections") is None
    )
    if (
        xdr_array_missing_now
        != bool(plan["input"].get("xdrArrayWasMissing"))
    ):
        raise ValueError("solution-data XDR array presence changed after package selection planning")
    expected_candidates = plan["input"]["candidateReferences"]
    if xdr_array_missing_now:
        arrays_match = arrays["analyticRules"] == expected_candidates["analyticRules"]
        arrays_match = arrays_match and bool(
            plan["input"].get("xdrReferencesBootstrappedFromManifest")
        )
        arrays_match = arrays_match and plan["input"].get(
            "bootstrapManifestOutputReferences"
        ) == expected_candidates["xdrDetections"]
    else:
        arrays_match = arrays == expected_candidates
    if not arrays_match:
        raise ValueError("solution-data selections changed after package selection planning")
    if _data_context_sha256(data) != plan["input"]["solutionDataContextSha256"]:
        raise ValueError("unrelated solution-data content changed after package selection planning")
    selected = plan["selection"]
    source_key = _case_key(data, "Analytic Rules") or _case_key(data, "Analytics Rules") or "Analytic Rules"
    xdr_key = _case_key(data, "XDR Detections") or _case_key(data, "Custom Detections") or "XDR Detections"
    data[source_key] = list(selected["analyticRules"])
    data[xdr_key] = list(selected["xdrDetections"])
    encoded = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    current = _build_package_selection_plan(root, run_id)
    if current["planSha256"] != plan["planSha256"]:
        raise ValueError("package selection evidence changed immediately before solution-data update")
    receipt = {
        "schemaVersion": "1.0.0",
        "runId": run_id,
        "selectionPlanPath": _relative_artifact(root, plan_path),
        "selectionPlanSha256": plan["planSha256"],
        "solutionDataPath": _relative_artifact(root, data_path),
        "solutionDataSha256": _sha256(encoded),
        "solutionDataContextSha256": _data_context_sha256(data),
        "selected": selected,
        "selectionSummary": plan["summary"],
        "originalSourceInventorySha256": plan["input"]["originalSourceInventorySha256"],
        "outcome": "partial-package-validated" if plan["summary"]["outcome"] == "partial" else "package-validated",
    }
    with using_run(root, run_id):
        receipt_path = report_directory(root, create=True) / RECEIPT_NAME
    if receipt_path.exists():
        raise ValueError(
            "package selection apply receipt already exists; verify or replan before applying again"
        )
    applied_data_snapshot = _atomic_exchange_if_unchanged(
        data_path,
        encoded,
        original_data_snapshot,
    )
    try:
        _write_selection_receipt(root, receipt_path, receipt)
    except Exception as exc:
        try:
            _atomic_exchange_if_unchanged(
                data_path,
                original_data_bytes,
                applied_data_snapshot,
            )
        except Exception as rollback_exc:
            raise RuntimeError(
                "package selection receipt write failed and safe rollback could not be completed; "
                "a concurrent solution-data edit was preserved, inspect and replan"
            ) from rollback_exc
        raise RuntimeError(
            "package selection receipt write failed; solution-data update was rolled back "
            "under the package-selection writer lock"
        ) from exc
    try:
        current_after_receipt = _file_snapshot(data_path)
    except Exception as exc:
        raise RuntimeError(
            "package selection receipt was published but solution-data freshness could not be "
            "verified; inspect the durable receipt and replan"
        ) from exc
    if current_after_receipt != applied_data_snapshot:
        raise RuntimeError(
            "package selection receipt was published but a concurrent solution-data edit was "
            "preserved; inspect the durable receipt and replan"
        )
    return {"status": "applied", "receiptPath": _relative_artifact(root, receipt_path), **receipt}


def verify_applied_package_selection(
    solution: str | Path,
    run_id: str,
) -> dict[str, Any] | None:
    root = Path(solution).expanduser().resolve()
    with using_run(root, run_id):
        run_directory = report_directory(root)
    receipt_path = run_directory / RECEIPT_NAME
    plan_path = run_directory / PLAN_NAME
    if not receipt_path.is_file() and not plan_path.is_file():
        return None
    if not receipt_path.is_file() or not plan_path.is_file():
        raise ValueError("package selection plan and apply receipt must both exist")
    plan_path, plan = _load_selection_plan(root, run_id)
    receipt = _read_json(receipt_path, "package selection apply receipt")
    if (
        receipt.get("runId") != run_id
        or receipt.get("selectionPlanSha256") != plan.get("planSha256")
        or receipt.get("solutionDataContextSha256") is None
        or receipt.get("selectionSummary") != plan.get("summary")
        or receipt.get("originalSourceInventorySha256")
        != (plan.get("input") or {}).get("originalSourceInventorySha256")
    ):
        raise ValueError("package selection apply receipt is stale or mismatched")
    data_path = _data_file(root)
    data = _read_json(data_path, "solution data")
    arrays = _selection_arrays(root, data)
    expected = plan.get("selection") or {}
    if arrays != expected:
        raise ValueError("solution-data package selections changed after evidence-based apply")
    if _data_context_sha256(data) != receipt.get("solutionDataContextSha256"):
        raise ValueError("unrelated solution-data content changed after package selection apply")
    if plan.get("executionErrors"):
        raise ValueError("applied package selection contains execution errors")
    refreshed = _build_package_selection_plan(
        root,
        run_id,
        candidate_lists_override=plan["input"]["candidateReferences"],
        xdr_array_was_missing_override=plan["input"].get("xdrArrayWasMissing"),
        xdr_references_bootstrapped_override=plan["input"].get(
            "xdrReferencesBootstrappedFromManifest"
        ),
        bootstrap_missing_outputs_override=plan["input"].get("bootstrapMissingOutputs"),
    )
    if refreshed.get("planSha256") != plan.get("planSha256"):
        raise ValueError("package selection evidence or artifact hashes changed; replan before packaging")
    return {
        "plan": plan,
        "receipt": receipt,
        "planPath": _relative_artifact(root, plan_path),
        "receiptPath": _relative_artifact(root, receipt_path),
    }


def current_applied_package_selection(solution: str | Path) -> dict[str, Any] | None:
    root = Path(solution).expanduser().resolve()
    run_id = requested_run_id(root)
    if not run_id:
        state_path = existing_artifact_path(root, "workflow-state.json")
        if not state_path.is_file():
            return None
        state = json.loads(state_path.read_text(encoding="utf-8-sig"))
        run_id = state.get("runId") if isinstance(state, dict) else None
    if not isinstance(run_id, str) or not run_id:
        return None
    return verify_applied_package_selection(root, run_id)
