from __future__ import annotations

import json
import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, unquote, urlsplit

import yaml

from solution_manager.core.artifacts import existing_artifact_path, existing_artifacts, report_directory, resolve_artifact_reference, portable_artifact, write_json_artifact
from solution_manager.migration.converter import (
    analytic_rule_files,
    custom_detail_binding_warnings,
    solution_paths,
    validate_document,
)
from solution_manager.core.content_paths import content_path
from solution_manager.qualification.deployment_planning import _consent_state as _validated_planning_consent
from solution_manager.reporting.report_dashboard import render_dashboard
from solution_manager.qualification.runtime_consent import runtime_query_consent_status
from solution_manager.core.workflow import _package_freshness

JSON_NAME = "migration-report.json"
HTML_NAME = "migration-report.html"
FLOW_STAGE_NAMES = (
    "setup", "discovery", "conversion", "validation", "packaging", "preflight",
    "validationSuite", "deployment", "mockIngestion", "queryValidation",
    "alertParity", "packageAcceptance", "report",
)


def _local_flow_evidence_link(root: Path, reports: Path, reference: Any) -> dict[str, Any]:
    unavailable = {"available": False, "label": "Evidence reference unavailable or non-portable"}
    if not isinstance(reference, str) or not reference:
        return unavailable
    try:
        candidate = resolve_artifact_reference(root, reference)
        if candidate.is_symlink():
            return unavailable
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return unavailable
    try:
        run_root = reports.resolve(strict=True)
        relative = resolved.relative_to(run_root)
        lexical = Path(os.path.abspath(candidate))
        lexical_relative = lexical.relative_to(run_root)
    except (OSError, RuntimeError, ValueError):
        return unavailable
    current = run_root
    for part in lexical_relative.parts:
        current = current / part
        if current.is_symlink():
            return unavailable
    if not resolved.is_file():
        return unavailable
    href = quote(relative.as_posix(), safe="/-._~")
    parsed = urlsplit(href)
    decoded = unquote(href)
    if (
        parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
        or href.startswith(("/", "\\")) or "\\" in href
        or any(part in {"", ".", ".."} for part in PurePosixPath(href).parts)
        or any(":" in part for part in PurePosixPath(decoded).parts)
    ):
        return unavailable
    return {"available": True, "label": resolved.name, "href": href}


def _build_flow_evidence(root: Path, reports: Path, workflow: dict[str, Any], artifacts: dict[str, Any], package: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result = {name: [] for name in FLOW_STAGE_NAMES}

    def add(stage: str, reference: Any) -> None:
        link = _local_flow_evidence_link(root, reports, reference)
        if link not in result[stage]:
            result[stage].append(link)
        if stage == "deployment" and isinstance(reference, str) and "preflight" in Path(reference.replace("\\", "/")).name.casefold():
            preflight_link = _local_flow_evidence_link(root, reports, reference)
            if preflight_link not in result["preflight"]:
                result["preflight"].append(preflight_link)

    for name, stage in (workflow.get("stages") or {}).items():
        if name in result and isinstance(stage, dict):
            for reference in stage.get("evidence") or []:
                add(name, reference)
                if isinstance(reference, str):
                    base = Path(reference.replace("\\", "/")).name.casefold()
                    if "preflight" in base:
                        add("preflight", reference)
                    if (
                        ("full" in base or "official" in base or "local" in base)
                        and ("validation" in base or "suite" in base)
                    ):
                        add("validationSuite", reference)
    for reference in (artifacts.get("transformationReport"),):
        if reference:
            add("conversion", reference)
    for runtime in artifacts.get("runtimeReports") or []:
        if isinstance(runtime, dict):
            for field in ("jsonReport", "htmlReport"):
                if runtime.get(field):
                    add("validation", runtime[field])
    for field in ("deploymentReport", "analyticDeploymentReport"):
        if artifacts.get(field):
            add("deployment", artifacts[field])
    for field in ("queryParityReport",):
        if artifacts.get(field):
            add("queryValidation", artifacts[field])
    if artifacts.get("alertParityReport"):
        add("alertParity", artifacts["alertParityReport"])
    if artifacts.get("packagingReport"):
        add("packaging", artifacts["packagingReport"])
    for reference in artifacts.get("ingestionReports") or []:
        add("mockIngestion", reference)
    if artifacts.get("qualificationDcrPreflight"):
        add("preflight", artifacts["qualificationDcrPreflight"])
    if artifacts.get("qualificationPreflightPacket"):
        add("preflight", artifacts["qualificationPreflightPacket"])
        add("setup", artifacts["qualificationPreflightPacket"])
    if artifacts.get("qualificationPipelineState"):
        for qual_stage in ("setup", "preflight", "deployment", "mockIngestion", "queryValidation", "packageAcceptance"):
            add(qual_stage, artifacts["qualificationPipelineState"])
    if artifacts.get("qualificationTarget"):
        add("setup", artifacts["qualificationTarget"])
    for field in ("mainTemplate", "createUiDefinition", "testParameters", "zip"):
        if package.get(field):
            add("packaging", package[field])
    return result


def _package_resource_inventory(template: Any) -> list[dict[str, Any]]:
    records: dict[tuple[str, str], dict[str, Any]] = {}

    def scan_document(node: Any, *, extension_resource: bool = False) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "resources":
                    scan_collection(value, extension_resource=False)
                elif key == "extensionResources":
                    scan_collection(value, extension_resource=True)
                else:
                    scan_document(value, extension_resource=extension_resource)
        elif isinstance(node, list):
            for value in node:
                scan_document(value, extension_resource=extension_resource)

    def scan_resource(resource: Any, container: str, *, extension_resource: bool = False) -> None:
        if not isinstance(resource, dict):
            return
        original_type = resource.get("type")
        if isinstance(original_type, str):
            resource_type, separator, embedded_version = original_type.partition("@")
            if "/" in resource_type:
                api_version = resource.get("apiVersion")
                if not isinstance(api_version, str) or not api_version:
                    api_version = embedded_version if separator else ""
                key = (resource_type, api_version)
                record = records.setdefault(key, {
                    "type": resource_type,
                    "originalType": original_type,
                    "apiVersion": api_version,
                    "count": 0,
                    "sourceForms": set(),
                    "extensionResource": False,
                })
                record["count"] += 1
                record["sourceForms"].add(container)
                record["extensionResource"] = (
                    record["extensionResource"]
                    or extension_resource
                    or resource.get("extensionResource") is True
                )
        for key, value in resource.items():
            if key == "resources":
                scan_collection(value, extension_resource=False)
            elif key == "extensionResources":
                scan_collection(value, extension_resource=True)
            else:
                scan_document(value, extension_resource=extension_resource)

    def scan_collection(resources: Any, *, extension_resource: bool = False) -> None:
        if isinstance(resources, list):
            for resource in resources:
                scan_resource(
                    resource,
                    "extension resources collection" if extension_resource else "nested ARM resources array",
                    extension_resource=extension_resource,
                )
        elif isinstance(resources, dict):
            if isinstance(resources.get("type"), str):
                scan_resource(
                    resources,
                    "extension resource object" if extension_resource else "ARM resource object",
                    extension_resource=extension_resource,
                )
            else:
                for resource in resources.values():
                    scan_resource(
                        resource,
                        "languageVersion 2 extension resource dictionary"
                        if extension_resource else "languageVersion 2 resource dictionary",
                        extension_resource=extension_resource,
                    )

    scan_document(template)
    return [
        {
            **record,
            "sourceForms": sorted(record["sourceForms"]),
        }
        for _, record in sorted(records.items())
    ]


def _read_local_package_template(root: Path, package: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    reference = package.get("mainTemplate")
    if not isinstance(reference, str) or not reference:
        return {}, None
    try:
        candidate = resolve_artifact_reference(root, reference)
        if candidate.is_symlink():
            return {}, None
        path = candidate.resolve(strict=True)
        package_candidate = root / "Package"
        if package_candidate.is_symlink():
            return {}, None
        package_root = package_candidate.resolve(strict=True)
        path.relative_to(package_root)
        lexical = Path(os.path.abspath(candidate))
        lexical_relative = lexical.relative_to(package_candidate.absolute())
        current = package_candidate.absolute()
        for part in lexical_relative.parts:
            current = current / part
            if current.is_symlink():
                return {}, None
        if not path.is_file() or path.stat().st_size > 10_000_000:
            return {}, None
        content = path.read_bytes()
        document = json.loads(content.decode("utf-8-sig"))
    except (OSError, RuntimeError, UnicodeError, ValueError, json.JSONDecodeError):
        return {}, None
    return (
        document if isinstance(document, dict) else {},
        hashlib.sha256(content).hexdigest(),
    )


def _safe_plan_value(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return None
    if isinstance(value, dict):
        result = {}
        for key, item in list(value.items())[:100]:
            if not isinstance(key, str):
                continue
            lowered = key.casefold()
            if any(term in lowered for term in (
                "path", "token", "secret", "password", "authorization",
            )):
                continue
            cleaned = _safe_plan_value(item, depth + 1)
            if cleaned is not None:
                result[key[:120]] = cleaned
        return result
    if isinstance(value, list):
        return [
            cleaned for item in value[:200]
            if (cleaned := _safe_plan_value(item, depth + 1)) is not None
        ]
    if isinstance(value, str):
        return value[:2000]
    if isinstance(value, (bool, int, float)):
        return value
    return None


def _deployment_planning_input(root: Path, raw_workflow: dict[str, Any]) -> dict[str, Any]:
    stages = raw_workflow.get("stages")
    stages = stages if isinstance(stages, dict) else {}
    context = raw_workflow.get("context")
    context = context if isinstance(context, dict) else {}
    for candidate in (
        raw_workflow.get("deploymentPlanning"),
        context.get("deploymentPlanning"),
        (stages.get("preflight") or {}).get("artifacts", {}).get("deploymentPlanning")
        if isinstance(stages.get("preflight"), dict)
        and isinstance(stages.get("preflight", {}).get("artifacts"), dict)
        else None,
        (stages.get("deployment") or {}).get("artifacts", {}).get("deploymentPlanning")
        if isinstance(stages.get("deployment"), dict)
        and isinstance(stages.get("deployment", {}).get("artifacts"), dict)
        else None,
    ):
        if isinstance(candidate, dict) and candidate:
            return candidate

    reports = report_directory(root)
    persisted = _read_run_json(root, reports, reports / "deployment-scope-plan.json")
    if persisted:
        return persisted

    for stage_name in ("preflight", "deployment"):
        stage = stages.get(stage_name)
        if not isinstance(stage, dict):
            continue
        for reference in stage.get("evidence") or []:
            if not isinstance(reference, str):
                continue
            if stage_name == "preflight" or "preflight" in Path(reference.replace("\\", "/")).name.casefold():
                document = _read_run_json(root, reports, reference)
                candidate = document.get("deploymentPlanning")
                if isinstance(candidate, dict) and candidate:
                    return candidate
    return {}


def _planning_summary(
    root: Path,
    package: dict[str, Any],
    workflow: dict[str, Any],
    raw_workflow: dict[str, Any],
) -> dict[str, Any]:
    template, template_sha256 = _read_local_package_template(root, package)
    hashes = package.get("packageArtifactHashes")
    recorded_template_hash = hashes.get("mainTemplate") if isinstance(hashes, dict) else None
    hash_matches = (
        isinstance(template_sha256, str)
        and isinstance(recorded_template_hash, str)
        and template_sha256 == recorded_template_hash
    )
    freshness = workflow.get("packageFreshness")
    freshness_status = (
        freshness.get("status")
        if isinstance(freshness, dict) and isinstance(freshness.get("status"), str)
        else "unverified"
    )
    freshness_current_input_hash = (
        freshness.get("currentPackageInputSha256")
        if isinstance(freshness, dict)
        and isinstance(freshness.get("currentPackageInputSha256"), str)
        else None
    )
    if freshness_status == "stale" or (
        isinstance(template_sha256, str)
        and isinstance(recorded_template_hash, str)
        and not hash_matches
    ):
        identity_status = "stale"
    elif hash_matches and freshness_status == "current":
        identity_status = "verified current"
    elif template_sha256:
        identity_status = "unverified"
    else:
        identity_status = "unavailable"
    context_profile = workflow.get("profile")
    mode = (
        context_profile
        if context_profile in {"authoring", "qualification"}
        and workflow.get("profileSelectionConfirmed") is True
        else "unknown"
    )
    parameters = package.get("deploymentParameters")
    safe_defaults = (
        [
            {"name": str(name), "value": value}
            for name, value in parameters.items()
            if isinstance(name, str) and isinstance(value, (str, bool, int, float))
        ]
        if isinstance(parameters, dict)
        else []
    )
    raw_stages = raw_workflow.get("stages")
    deployment_stage = raw_stages.get("deployment") if isinstance(raw_stages, dict) else None
    stage_artifacts = deployment_stage.get("artifacts") if isinstance(deployment_stage, dict) else None
    plan = _deployment_planning_input(root, raw_workflow)
    raw_package_plan = (
        plan.get("packageAcceptancePlan")
        if isinstance(plan.get("packageAcceptancePlan"), dict)
        else stage_artifacts.get("packageAcceptancePlan") if isinstance(stage_artifacts, dict) else None
    )
    package_plan = raw_package_plan if isinstance(raw_package_plan, dict) else {}
    resource_types = package_plan.get("resourceTypes")
    safe_types = sorted({
        str(item).split("@", 1)[0]
        for item in resource_types
        if isinstance(item, str) and "/" in item.split("@", 1)[0]
    }) if isinstance(resource_types, list) else []
    plan_identity = package_plan.get("packageIdentity")
    safe_plan_identity = (
        {
            key: plan_identity[key]
            for key in ("status", "sha256", "packageArtifactsSha256")
            if isinstance(plan_identity.get(key), (str, bool, int))
        }
        if isinstance(plan_identity, dict)
        else {}
    )
    plan_sha = plan.get("planSha256") if isinstance(plan.get("planSha256"), str) else None
    raw_consent = plan.get("planningConsent")
    raw_consent = raw_consent if isinstance(raw_consent, dict) else {}
    consent_status = raw_consent.get("status")
    consent_plan_sha = raw_consent.get("planSha256")
    consent_components = raw_consent.get("approvedComponents")
    if not isinstance(consent_components, list):
        consent_components = raw_consent.get("componentKeys")
    consent_types = raw_consent.get("resourceTypes")
    selected_flags = raw_consent.get("packageFlags")
    if not isinstance(selected_flags, dict):
        selected_flags = raw_consent.get("selectedFlags")
    consent_component_keys = (
        [
            value for value in consent_components
            if isinstance(value, str) and value
        ]
        if isinstance(consent_components, list)
        else []
    )
    consent_resource_types = (
        [
            value for value in consent_types
            if isinstance(value, str) and "/" in value.split("@", 1)[0]
        ]
        if isinstance(consent_types, list)
        else []
    )
    raw_components = plan.get("components")
    raw_components = raw_components if isinstance(raw_components, dict) else {}
    current_component_keys = {
        key for key, value in raw_components.items()
        if isinstance(key, str) and isinstance(value, dict)
    }
    expected_consent_types = sorted({
        resource_type
        for component_key in consent_component_keys
        for resource_type in (
            raw_components.get(component_key, {}).get("resourceTypes") or []
            if isinstance(raw_components.get(component_key), dict)
            else []
        )
        if isinstance(resource_type, str)
    })
    consent_flags_valid = isinstance(selected_flags, dict) and any(
        isinstance(key, str) and isinstance(value, (str, bool, int))
        for key, value in selected_flags.items()
    )
    if consent_status == "approved":
        if not (
            isinstance(plan_sha, str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", plan_sha)
            and isinstance(consent_plan_sha, str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", consent_plan_sha)
            and plan_sha.casefold() == consent_plan_sha.casefold()
            and bool(consent_component_keys)
            and set(consent_component_keys).issubset(current_component_keys)
            and expected_consent_types == sorted(consent_resource_types)
            and (
                isinstance(target := plan.get("target"), dict)
                and all(
                    isinstance(target.get(key), str) and target.get(key)
                    for key in (
                        "tenantId", "subscriptionId", "resourceGroup",
                        "workspaceResourceId", "solution", "version",
                    )
                )
            )
            and (bool(consent_resource_types) or consent_flags_valid or consent_component_keys)
        ):
            consent_status = "stale"
    elif consent_status not in {
        "declined", "stale", "not-recorded", "not-approved", "unknown",
    }:
        consent_status = "not-recorded"
    components = raw_components
    target = plan.get("target") if isinstance(plan.get("target"), dict) else {}
    source_inventory = plan.get("sourceInventory") if isinstance(plan.get("sourceInventory"), dict) else {}
    detection_scope = plan.get("detectionScope") if isinstance(plan.get("detectionScope"), dict) else {}
    scope_caps = plan.get("scopeCaps") if isinstance(plan.get("scopeCaps"), dict) else {}
    planned_resource_inventory = plan.get("packageResourceInventory")
    planned_resource_inventory = (
        _safe_plan_value(planned_resource_inventory)
        if isinstance(planned_resource_inventory, list)
        else []
    )
    package_acceptance = plan.get("packageAcceptancePlan")
    package_acceptance = (
        _safe_plan_value(package_acceptance)
        if isinstance(package_acceptance, dict)
        else {}
    )
    artifact_hashes = plan.get("packageArtifactHashes") if isinstance(plan.get("packageArtifactHashes"), dict) else {}
    recorded_artifact_hashes = (
        plan.get("recordedPackageArtifactHashes")
        if isinstance(plan.get("recordedPackageArtifactHashes"), dict)
        else {}
    )
    contract_input_hash = plan.get("packageInputSha256")
    current_input_hash = (
        package.get("packageInputs", {}).get("after", {}).get("sha256")
        if isinstance(package.get("packageInputs"), dict)
        and isinstance(package.get("packageInputs", {}).get("after"), dict)
        else None
    )
    input_identity_matches = (
        isinstance(contract_input_hash, str)
        and isinstance(current_input_hash, str)
        and contract_input_hash.casefold() == current_input_hash.casefold()
    )
    package_report_hashes = package.get("packageArtifactHashes")
    required_package_hashes = {"mainTemplate", "createUiDefinition", "testParameters", "zip"}
    valid_current_hashes = (
        required_package_hashes.issubset(artifact_hashes)
        and all(
            isinstance(artifact_hashes.get(key), str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", artifact_hashes[key])
            for key in required_package_hashes
        )
        and required_package_hashes.issubset(recorded_artifact_hashes)
        and required_package_hashes.issubset(package_report_hashes or {})
    ) if isinstance(package_report_hashes, dict) else False
    artifact_identity_matches = bool(
        valid_current_hashes
        and all(
            artifact_hashes.get(key) == recorded_artifact_hashes.get(key)
            == package_report_hashes.get(key)
            for key in required_package_hashes
        )
        and isinstance(template_sha256, str)
        and template_sha256 == artifact_hashes.get("mainTemplate")
    )
    hash_pattern = r"[0-9a-fA-F]{64}"
    report_input_hash_valid = (
        isinstance(current_input_hash, str)
        and re.fullmatch(hash_pattern, current_input_hash) is not None
    )
    freshness_input_hash_valid = (
        isinstance(freshness_current_input_hash, str)
        and re.fullmatch(hash_pattern, freshness_current_input_hash) is not None
    )
    known_input_mismatch = bool(
        report_input_hash_valid
        and freshness_input_hash_valid
        and current_input_hash.casefold() != freshness_current_input_hash.casefold()
    )
    report_template_hash = (
        package_report_hashes.get("mainTemplate")
        if isinstance(package_report_hashes, dict)
        else None
    )
    template_hash_mismatch = bool(
        isinstance(template_sha256, str)
        and isinstance(report_template_hash, str)
        and re.fullmatch(hash_pattern, report_template_hash)
        and template_sha256.casefold() != report_template_hash.casefold()
    )
    if freshness_status == "stale" or known_input_mismatch or template_hash_mismatch:
        package_evidence_status = "stale"
    elif (
        freshness_status == "current"
        and report_input_hash_valid
        and freshness_input_hash_valid
        and current_input_hash.casefold() == freshness_current_input_hash.casefold()
        and isinstance(template_sha256, str)
        and isinstance(report_template_hash, str)
        and re.fullmatch(hash_pattern, report_template_hash)
        and template_sha256.casefold() == report_template_hash.casefold()
    ):
        package_evidence_status = "current"
    else:
        package_evidence_status = "unknown"

    if plan and isinstance(plan_sha, str):
        consent_from_artifact = _validated_planning_consent(
            root,
            plan_sha,
            components=raw_components,
            package={
                "status": (
                    "current" if package_evidence_status == "current"
                    else package_evidence_status
                ),
                "resourceInventory": (
                    plan.get("packageResourceInventory")
                    if isinstance(plan.get("packageResourceInventory"), list)
                    else []
                ),
            },
            target=plan.get("target") if isinstance(plan.get("target"), dict) else {},
        )
        if isinstance(consent_from_artifact, dict):
            raw_consent = consent_from_artifact
            consent_status = consent_from_artifact.get("status")
            consent_plan_sha = consent_from_artifact.get("planSha256")
            consent_components = consent_from_artifact.get("approvedComponents")
            consent_component_keys = (
                [
                    value for value in consent_components
                    if isinstance(value, str) and value
                ]
                if isinstance(consent_components, list)
                else []
            )
            consent_resource_types = (
                [
                    value for value in consent_from_artifact.get("resourceTypes", [])
                    if isinstance(value, str) and "/" in value.split("@", 1)[0]
                ]
                if isinstance(consent_from_artifact.get("resourceTypes"), list)
                else []
            )
            selected_flags = consent_from_artifact.get("packageFlags")
            if not isinstance(selected_flags, dict):
                selected_flags = {}
            expected_consent_types = sorted({
                resource_type
                for component_key in consent_component_keys
                for resource_type in (
                    raw_components.get(component_key, {}).get("resourceTypes") or []
                    if isinstance(raw_components.get(component_key), dict)
                    else []
                )
                if isinstance(resource_type, str)
            })
            if consent_status == "approved" and not (
                isinstance(plan_sha, str)
                and re.fullmatch(r"[0-9a-fA-F]{64}", plan_sha)
                and isinstance(consent_plan_sha, str)
                and re.fullmatch(r"[0-9a-fA-F]{64}", consent_plan_sha)
                and plan_sha.casefold() == consent_plan_sha.casefold()
                and bool(consent_component_keys)
                and set(consent_component_keys).issubset(current_component_keys)
                and expected_consent_types == sorted(consent_resource_types)
                and isinstance(plan.get("target"), dict)
            ):
                consent_status = "unknown"

    safe_flags = (
        {
            key: value
            for key, value in selected_flags.items()
            if isinstance(key, str) and isinstance(value, (str, bool, int))
        }
        if isinstance(selected_flags, dict)
        else {}
    )
    contract_status = plan.get("status") if isinstance(plan.get("status"), str) else "not-recorded"
    if contract_status not in {
        "current", "provisional", "stale", "unavailable", "not-applicable",
        "not-recorded", "unknown",
    }:
        contract_status = "unknown"
    contract_input_hash_valid = (
        isinstance(contract_input_hash, str)
        and re.fullmatch(hash_pattern, contract_input_hash) is not None
    )
    plan_package_identity_status = (
        plan.get("packageIdentity", {}).get("status")
        if isinstance(plan.get("packageIdentity"), dict)
        and isinstance(plan["packageIdentity"].get("status"), str)
        else None
    )
    if plan and package_evidence_status == "stale":
        contract_status = "stale"
    elif plan and package_evidence_status == "unknown" and contract_status not in {
        "not-applicable", "unavailable", "not-recorded",
    }:
        contract_status = "unknown"
    elif contract_status == "current":
        if not (
            report_input_hash_valid
            and freshness_input_hash_valid
            and contract_input_hash_valid
            and isinstance(artifact_hashes, dict)
            and isinstance(recorded_artifact_hashes, dict)
            and isinstance(package_report_hashes, dict)
        ):
            contract_status = "unknown"
        elif (
            not input_identity_matches
            or contract_input_hash.casefold() != freshness_current_input_hash.casefold()
        ):
            contract_status = "stale"
        elif not valid_current_hashes:
            contract_status = "unknown"
        elif not artifact_identity_matches:
            contract_status = "stale"
    if plan_package_identity_status == "stale":
        contract_status = "stale"
    elif plan_package_identity_status not in {None, "current", "verified current", "stale"}:
        if contract_status == "current":
            contract_status = "unknown"
    recorded_profile = plan.get("selectedProfile")
    if (
        mode in {"authoring", "qualification"}
        and isinstance(recorded_profile, str)
        and recorded_profile != mode
    ):
        contract_status = "stale"
    if consent_status == "approved" and (
        contract_status not in {"current", "provisional"}
        or package_evidence_status != "current"
    ):
        consent_status = (
            "stale"
            if contract_status == "stale" or package_evidence_status == "stale"
            else "unknown"
        )

    if package_evidence_status == "stale" or plan_package_identity_status == "stale":
        final_package_identity_status = "stale"
    elif (
        package_evidence_status == "unknown"
        or plan_package_identity_status == "unknown"
        or contract_status == "unknown"
    ):
        final_package_identity_status = "unknown"
    elif package_evidence_status == "current" and hash_matches:
        final_package_identity_status = "verified current"
    elif identity_status == "stale":
        final_package_identity_status = "stale"
    else:
        final_package_identity_status = "unknown"

    safe_components = {}
    for key, item in components.items():
        if not isinstance(key, str) or not isinstance(item, dict):
            continue
        safe_component = _safe_plan_value(item)
        if not isinstance(safe_component, dict):
            continue
        raw_component_consent = item.get("planningConsent")
        raw_component_consent = (
            raw_component_consent.get("status")
            if isinstance(raw_component_consent, dict)
            else raw_component_consent
        )
        if item.get("advanceConsentSupported") is False:
            component_consent_status = "not-supported"
        elif consent_status in {"stale", "unknown"} and (
            key in consent_component_keys or raw_component_consent == "approved"
        ):
            component_consent_status = consent_status
        elif consent_status == "approved" and key in consent_component_keys:
            component_consent_status = "approved"
        elif raw_component_consent in {
            "unknown", "stale", "declined", "not-approved", "not-recorded",
        }:
            component_consent_status = raw_component_consent
        else:
            component_consent_status = "not-recorded"
        safe_component["planningConsent"] = component_consent_status
        safe_components[key] = safe_component

    package_acceptance_approval = package_acceptance.get("approvalStatus")
    if (
        consent_status == "approved"
        and "fullPackageAcceptance" in consent_component_keys
    ):
        package_acceptance["approvalStatus"] = "approved"
        package_acceptance["selectedFlags"] = safe_flags
    elif consent_status == "approved":
        package_acceptance["approvalStatus"] = "not-approved"
    elif package_acceptance_approval == "approved":
        if contract_status == "stale" or package_evidence_status == "stale":
            package_acceptance["approvalStatus"] = "stale"
        elif (
            contract_status not in {"current", "provisional"}
            or package_evidence_status != "current"
        ):
            package_acceptance["approvalStatus"] = "unknown"
        elif consent_status in {"not-recorded", "not-approved", "declined"}:
            package_acceptance["approvalStatus"] = consent_status
    package_acceptance_identity = package_acceptance.get("packageIdentity")
    if isinstance(package_acceptance_identity, dict):
        package_acceptance_identity["status"] = final_package_identity_status
    elif plan_package_identity_status is not None:
        package_acceptance["packageIdentity"] = {
            "status": final_package_identity_status,
        }
    safe_plan_identity = {
        **safe_plan_identity,
        "status": final_package_identity_status,
    }
    projected_freshness_status = package_evidence_status
    planning_contract = {
        "schemaVersion": plan.get("schemaVersion") if isinstance(plan.get("schemaVersion"), str) else None,
        "status": contract_status,
        "selectedProfile": plan.get("selectedProfile") if isinstance(plan.get("selectedProfile"), str) else mode,
        "executionMode": (
            raw_consent.get("executionMode")
            if consent_status == "approved"
            and raw_consent.get("executionMode") in {
                "pairs", "package", "both", "ingestion-or-provisioning",
            }
            else plan.get("executionMode")
            if isinstance(plan.get("executionMode"), str)
            and plan.get("executionMode") in {
                "pairs", "package", "both", "ingestion-or-provisioning", "not-selected",
            }
            else "not-selected"
        ),
        "target": {
            key: target.get(key)
            for key in (
                "tenantId", "subscriptionId", "resourceGroup", "workspaceResourceId",
                "workspaceCustomerId", "solution", "version",
            )
            if isinstance(target.get(key), str)
        },
        "planSha256": plan_sha,
        "packageInputSha256": contract_input_hash if isinstance(contract_input_hash, str) else None,
        "packageArtifactHashes": {
            key: artifact_hashes.get(key)
            for key in ("mainTemplate", "createUiDefinition", "testParameters", "zip")
            if isinstance(artifact_hashes.get(key), str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", artifact_hashes[key])
        },
        "recordedPackageArtifactHashes": {
            key: recorded_artifact_hashes.get(key)
            for key in ("mainTemplate", "createUiDefinition", "testParameters", "zip")
            if isinstance(recorded_artifact_hashes.get(key), str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", recorded_artifact_hashes[key])
        },
        "packageContentSha256": (
            plan.get("packageContentSha256")
            if isinstance(plan.get("packageContentSha256"), str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", plan["packageContentSha256"])
            else None
        ),
        "packageIdentity": {
            "version": (
                plan.get("packageIdentity", {}).get("version")
                if isinstance(plan.get("packageIdentity"), dict)
                and isinstance(plan["packageIdentity"].get("version"), str)
                else package.get("version") if isinstance(package.get("version"), str) else None
            ),
            "status": final_package_identity_status,
        },
        "sourceInventory": {
            key: value for key, value in source_inventory.items()
            if isinstance(key, str) and isinstance(value, (str, int, bool))
        },
        "sourceInventorySha256": (
            plan.get("sourceInventorySha256")
            if isinstance(plan.get("sourceInventorySha256"), str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", plan["sourceInventorySha256"])
            else None
        ),
        "detectionScope": _safe_plan_value(detection_scope),
        "scopeCaps": {
            key: value for key, value in scope_caps.items()
            if isinstance(key, str) and isinstance(value, (str, bool, int))
        },
        "packageResourceInventory": planned_resource_inventory,
        "bicepExtensibilityImports": _safe_plan_value(plan.get("bicepExtensibilityImports") or []),
        "whatIfSupport": (
            plan.get("whatIfSupport")
            if isinstance(plan.get("whatIfSupport"), str)
            else "not-evaluated"
        ),
        "components": safe_components,
        "planningConsent": {
            "status": consent_status or "not-recorded",
            "approvedAt": raw_consent.get("approvedAt") if isinstance(raw_consent.get("approvedAt"), str) else None,
            "actor": raw_consent.get("actor") if isinstance(raw_consent.get("actor"), str) else None,
            "planSha256": consent_plan_sha if isinstance(consent_plan_sha, str) else None,
            "componentKeys": [
                key for key in consent_component_keys
            ],
            "resourceTypes": consent_resource_types,
            "selectedFlags": safe_flags,
            "maxAdditionalCustomDetections": (
                raw_consent.get("maxAdditionalCustomDetections")
                if type(raw_consent.get("maxAdditionalCustomDetections")) is int
                else None
            ),
            "conditionalSelections": _safe_plan_value(
                raw_consent.get("conditionalSelections")
                if isinstance(raw_consent.get("conditionalSelections"), dict)
                else {}
            ),
        },
        "exactScopeWriteApproval": "not-recorded",
        "readiness": plan.get("readiness") if isinstance(plan.get("readiness"), str) else "not-evaluated",
        "deploymentEvidence": plan.get("deploymentEvidence") if isinstance(plan.get("deploymentEvidence"), str) else "not-recorded",
        "dcrEvidence": _safe_plan_value(plan.get("dcrEvidence") or {}),
        "dcrResolver": _safe_plan_value(plan.get("dcrResolver") or {}),
        "separateApprovals": _safe_plan_value(plan.get("separateApprovals") or {}),
        "packageAcceptancePlan": package_acceptance,
    }
    return {
        "profile": mode,
        "executionMode": planning_contract["executionMode"],
        "planningConsent": planning_contract["planningConsent"]["status"],
        "exactScopeWriteApproval": planning_contract["exactScopeWriteApproval"],
        "deploymentPlan": planning_contract,
        "packageFreshness": projected_freshness_status,
        "packageIdentity": final_package_identity_status,
        "packageVersion": (
            plan.get("packageIdentity", {}).get("version")
            if isinstance(plan.get("packageIdentity"), dict)
            and isinstance(plan["packageIdentity"].get("version"), str)
            else package.get("version") if isinstance(package.get("version"), str) else None
        ),
        "selectedPackageReport": package.get("packageReport") if isinstance(package.get("packageReport"), str) else None,
        "selectedPackageReportStatus": package.get("status") if isinstance(package.get("status"), str) else "not-recorded",
        "templateSha256": template_sha256,
        "recordedTemplateSha256": recorded_template_hash,
        "packageArtifactsSha256": package.get("packageArtifactsSha256"),
        "packageInputSha256": (
            current_input_hash if isinstance(current_input_hash, str) else None
        ),
        "currentPackageInputSha256": (
            freshness_current_input_hash
            if freshness_input_hash_valid
            else None
        ),
        "resourceInventory": _package_resource_inventory(template),
        "resourceInventoryAvailable": bool(template_sha256 and template),
        "deploymentDefaults": safe_defaults,
        "packageAcceptancePlan": {
            "recorded": bool(package_plan),
            **(
                package_acceptance
                if package_acceptance
                else {
            "status": (
                package_plan.get("status")
                if isinstance(package_plan.get("status"), str)
                else "proposed-not-approved" if package_plan else "not-recorded"
            ),
            "resourceTypes": safe_types,
            "packageIdentity": safe_plan_identity,
            "executionStatus": (
                package_plan.get("executionStatus")
                if isinstance(package_plan.get("executionStatus"), str)
                else "not-recorded"
            ),
            "approvalStatus": (
                package_plan.get("approvalStatus")
                if isinstance(package_plan.get("approvalStatus"), str)
                else "not-recorded"
            ),
            "planningConsent": (
                package_plan.get("planningConsent")
                if isinstance(package_plan.get("planningConsent"), str)
                else "not-recorded"
            ),
            "executionMode": (
                package_plan.get("executionMode")
                if isinstance(package_plan.get("executionMode"), str)
                else "not-recorded"
            ),
                }
            ),
        },
        "additionalQualificationResources": [],
        "additionalQualificationPlanStatus": "recorded in component plan" if safe_components else "not-recorded",
    }


def _preflight_projection(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    authentication = value.get("authentication")
    permissions = value.get("permissions")
    read_checks = value.get("readChecks")
    dcr = value.get("dcrPermissionPreflight")
    if not isinstance(dcr, dict) and "workspaceQueryPermission" in value:
        dcr = value
    dcr = dcr if isinstance(dcr, dict) else {}
    dcr_auth = dcr.get("authentication")
    contracts = dcr.get("contracts")
    return {
        "status": value.get("status") if isinstance(value.get("status"), str) else "unknown",
        "graphRecorded": isinstance(authentication, dict) and isinstance(read_checks, list),
        "dcrRecorded": isinstance(value.get("dcrPermissionPreflight"), dict)
        or isinstance(value.get("workspaceQueryPermission"), dict),
        "checkedAt": value.get("checkedAt") if isinstance(value.get("checkedAt"), str) else value.get("generatedAt") if isinstance(value.get("generatedAt"), str) else None,
        "authentication": {
            key: authentication.get(key)
            for key in (
                "status", "method", "selectedMethod", "requestedScope",
                "tenantMatch", "graphAudience",
            )
            if isinstance(authentication, dict) and isinstance(authentication.get(key), (str, int, bool))
        },
        "permissions": {
            key: permissions.get(key)
            for key in ("readAccess", "writeScopeInToken", "consent", "writeAuthorization")
            if isinstance(permissions, dict) and isinstance(permissions.get(key), (str, int, bool))
        },
        "requiredManagementPermission": (
            value.get("requiredManagementPermission")
            if isinstance(value.get("requiredManagementPermission"), str)
            else None
        ),
        "tokenPermissionClaims": {
            key: value.get("authentication", {}).get("tokenPermissionClaims", {}).get(key)
            for key in ("status", "claimType")
            if isinstance(value.get("authentication"), dict)
            and isinstance(value["authentication"].get("tokenPermissionClaims"), dict)
            and isinstance(value["authentication"]["tokenPermissionClaims"].get(key), (str, int, bool))
        },
        "managementPermissionGrant": {
            key: grant.get(key)
            for key in ("status", "grantType", "claimType", "permission", "credentialRequestScope", "reason")
            if isinstance(grant, dict) and isinstance(grant.get(key), (str, int, bool))
        } if isinstance((grant := value.get("managementPermissionGrant")), dict) else {},
        "deploymentReadiness": (
            value.get("deploymentReadiness")
            if isinstance(value.get("deploymentReadiness"), str)
            else "unknown"
        ),
        "effectiveRoleStatus": (
            permissions.get("effectiveRole", {}).get("status")
            if isinstance(permissions, dict)
            and isinstance(permissions.get("effectiveRole"), dict)
            and isinstance(permissions["effectiveRole"].get("status"), str)
            else "unknown"
        ),
        "readChecks": [
            {
                key: check.get(key)
                for key in ("status", "httpStatus")
                if isinstance(check, dict) and isinstance(check.get(key), (str, int, bool))
            }
            for check in read_checks if isinstance(check, dict)
        ] if isinstance(read_checks, list) else [],
        "dcr": {
            "status": dcr.get("status") if isinstance(dcr.get("status"), str) else "unknown",
            "authenticationStatus": (
                dcr_auth.get("status") if isinstance(dcr_auth, dict) and isinstance(dcr_auth.get("status"), str) else "unknown"
            ),
            "targetVerificationStatus": (
                dcr.get("targetVerification", {}).get("status")
                if isinstance(dcr.get("targetVerification"), dict)
                and isinstance(dcr["targetVerification"].get("status"), str)
                else "unknown"
            ),
            "localReadinessStatus": (
                dcr.get("localReadiness", {}).get("status")
                if isinstance(dcr.get("localReadiness"), dict)
                and isinstance(dcr["localReadiness"].get("status"), str)
                else "unknown"
            ),
            "workspaceQueryPermissionStatus": (
                dcr.get("workspaceQueryPermission", {}).get("status")
                if isinstance(dcr.get("workspaceQueryPermission"), dict)
                and isinstance(dcr["workspaceQueryPermission"].get("status"), str)
                else "unknown"
            ),
            "resourcePlanStatus": "not-recorded",
            "resourceTypes": [],
            "contractCount": len(contracts) if isinstance(contracts, list) else 0,
            "contractStatuses": [
                item.get("status") for item in contracts
                if isinstance(item, dict) and isinstance(item.get("status"), str)
            ] if isinstance(contracts, list) else [],
        },
    }


def _read_run_json(root: Path, reports: Path, reference: Any) -> dict[str, Any]:
    link = _local_flow_evidence_link(root, reports, str(reference) if isinstance(reference, Path) else reference)
    if link.get("available") is not True or not str(link.get("label", "")).lower().endswith(".json"):
        return {}
    try:
        path = reports / PurePosixPath(unquote(link["href"]))
        if path.stat().st_size > 2_000_000:
            return {}
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _selected_packaging_report(
    root: Path,
    workflow: dict[str, Any],
) -> tuple[dict[str, Any], str | None]:
    reports = report_directory(root)
    stages = workflow.get("stages")
    stages = stages if isinstance(stages, dict) else {}
    packaging_stage = stages.get("packaging")
    packaging_stage = packaging_stage if isinstance(packaging_stage, dict) else {}
    artifacts = packaging_stage.get("artifacts")
    artifacts = artifacts if isinstance(artifacts, dict) else {}

    selected_reference = artifacts.get("packageReport")
    if "packaging" in stages:
        package_state = workflow.get("packaging")
        successful = (
            package_state.get("lastSuccessful")
            if isinstance(package_state, dict)
            else None
        )
        if not (
            packaging_stage.get("status") == "passed"
            and isinstance(successful, dict)
            and successful.get("packageSucceeded") is True
            and isinstance(successful.get("attemptId"), str)
            and artifacts.get("packageAttemptId") == successful.get("attemptId")
            and isinstance(selected_reference, str)
            and selected_reference
            and selected_reference == successful.get("packageReport")
        ):
            return {}, None
        try:
            selected_path = resolve_artifact_reference(root, selected_reference)
            successful_path = resolve_artifact_reference(
                root, successful["packageReport"]
            )
            if selected_path.resolve() != successful_path.resolve():
                return {}, None
            document = _read_run_json(root, reports, selected_reference)
            report_sha256 = hashlib.sha256(selected_path.read_bytes()).hexdigest()
        except (OSError, RuntimeError, ValueError, KeyError):
            return {}, None
        report_inputs = document.get("packageInputs")
        report_after = (
            report_inputs.get("after")
            if isinstance(report_inputs, dict)
            else None
        )
        recorded_hashes = document.get("packageArtifactHashes")
        if not (
            document.get("packager") == "V3.1"
            and document.get("packageAttemptId") == successful.get("attemptId")
            and document.get("workflowRunId") == workflow.get("runId")
            and report_sha256 == successful.get("packageReportSha256")
            and report_sha256 == artifacts.get("packageReportSha256")
            and document.get("packageArtifactsSha256")
            == successful.get("packageArtifactsSha256")
            and isinstance(report_after, dict)
            and report_after.get("sha256") == successful.get("packageInputSha256")
            and isinstance(recorded_hashes, dict)
            and all(
                isinstance(recorded_hashes.get(name), str)
                and re.fullmatch(r"[0-9a-fA-F]{64}", recorded_hashes[name])
                for name in (
                    "mainTemplate", "createUiDefinition",
                    "testParameters", "zip",
                )
            )
        ):
            return {}, None
        return document, selected_reference

    if isinstance(selected_reference, str) and selected_reference:
        return _read_run_json(root, reports, selected_reference), selected_reference

    for reference in packaging_stage.get("evidence") or []:
        if (
            isinstance(reference, str)
            and Path(reference.replace("\\", "/")).name.casefold().startswith("packaging.v3_1.")
        ):
            document = _read_run_json(root, reports, reference)
            if document:
                return document, reference

    if "packaging" in stages:
        return {}, None

    legacy_path = existing_artifact_path(root, "packaging.v3_1.json")
    document = _read_run_json(root, reports, legacy_path)
    if document:
        return document, str(legacy_path)
    return {}, None


def _qualification_preflight(
    root: Path,
    reports: Path,
    workflow: dict[str, Any],
) -> dict[str, Any]:
    dcr_reference = "qualification-dcr-preflight.json"
    dcr_file = reports / dcr_reference
    dcr_document = _read_run_json(root, reports, dcr_reference)
    graph = {}
    for stage in (workflow.get("stages") or {}).values():
        if not isinstance(stage, dict):
            continue
        for reference in stage.get("evidence") or []:
            if isinstance(reference, str) and "preflight" in Path(reference.replace("\\", "/")).name.casefold():
                candidate = _read_run_json(root, reports, reference)
                if isinstance(candidate.get("authentication"), dict) and isinstance(candidate.get("readChecks"), list):
                    graph = candidate
                    break
        if graph:
            break
    dcr = dcr_document.get("dcrPermissionPreflight") if isinstance(dcr_document.get("dcrPermissionPreflight"), dict) else dcr_document
    projected = _preflight_projection(graph) if graph else {}
    if dcr:
        projected["dcr"] = _preflight_projection(
            {"dcrPermissionPreflight": dcr}
        )["dcr"]
    if not projected:
        projected = _preflight_projection({})
    projected["graphRecorded"] = bool(graph)
    projected["dcrRecorded"] = bool(dcr)
    return projected


def _startup_setup_summary(
    root: Path,
    reports: Path,
    workflow: dict[str, Any],
    preflight: dict[str, Any],
    planning: dict[str, Any],
) -> dict[str, Any]:
    context = workflow.get("context") if isinstance(workflow.get("context"), dict) else {}
    target_document = _read_run_json(
        root, reports, reports / "qualification-target.json"
    )
    context_target = context.get("target") if isinstance(context.get("target"), dict) else context
    recorded_target = target_document if target_document else context_target
    target = {
        key: recorded_target.get(key)
        for key in (
            "tenantId", "subscriptionId", "resourceGroup", "workspaceResourceId",
            "workspaceCustomerId", "workspaceName",
        )
        if isinstance(recorded_target.get(key), str)
    }
    target_locked = (
        target_document.get("locked") is True
        or context.get("targetContextLocked") is True
        or context.get("lockedTargetConfirmed") is True
    )
    profile = context.get("workflowProfile")
    profile_confirmed = (
        profile in {"authoring", "qualification"}
        and context.get("profileSelectionConfirmed") is True
    )
    consent = (
        planning.get("deploymentPlan", {}).get("planningConsent", {})
        if isinstance(planning.get("deploymentPlan"), dict)
        else {}
    )
    preflight_auth = (
        preflight.get("authentication")
        if isinstance(preflight.get("authentication"), dict)
        else {}
    )
    preflight_at = preflight.get("checkedAt")
    if preflight.get("graphRecorded") is True:
        auth_state = "Recorded from a scoped preflight; not rechecked by report generation"
    else:
        auth_state = "Not checked in this selected-run snapshot"
    checks = []
    if not target:
        checks.append("No locked target details are recorded in workflow metadata or qualification-target.json.")
    elif not target_locked:
        checks.append("Target identifiers are recorded, but a locked-target confirmation is not recorded.")
    if not profile_confirmed:
        checks.append("Workflow profile selection is not confirmed in persisted run state.")
    if not preflight.get("graphRecorded"):
        checks.append("Cached authentication, scoped read access, and management permissions were not checked by this report.")
    return {
        "state": "unknown",
        "display": (
            "Target/profile recorded; runtime checks unknown"
            if target and profile_confirmed
            else "Setup evidence incomplete"
        ),
        "runId": workflow.get("runId") if isinstance(workflow.get("runId"), str) else None,
        "profile": profile if profile_confirmed else "not-recorded",
        "profileConfirmed": profile_confirmed,
        "target": target,
        "targetSource": (
            "qualification-target.json"
            if target_document
            else "workflow-state metadata"
            if target
            else "not-recorded"
        ),
        "targetLocked": target_locked,
        "localToolChecks": "not-recorded",
        "authentication": {
            "status": auth_state,
            "method": preflight_auth.get("method") or preflight_auth.get("selectedMethod"),
            "checkedAt": preflight_at,
        },
        "planningConsentStatus": (
            consent.get("status")
            if isinstance(consent, dict) and isinstance(consent.get("status"), str)
            else "not-recorded"
        ),
        "planningConsentPlanSha256": (
            consent.get("planSha256")
            if isinstance(consent, dict) and isinstance(consent.get("planSha256"), str)
            else None
        ),
        "exactScopeWriteApproval": "not-recorded",
        "notes": checks,
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    return value if isinstance(value, dict) else {}


def _partial_selection_parity_matches(
    selection_plan: dict[str, Any],
    parity: dict[str, Any],
    applied_plan: dict[str, Any] | None,
    *,
    stage_passed: bool,
) -> tuple[bool, str]:
    current_plan_sha = (
        applied_plan.get("planSha256") if isinstance(applied_plan, dict) else None
    )
    expected_paths = sorted(
        Path(str(value).replace("\\", "/"))
        .relative_to("XDR Detections").as_posix()
        for value in (selection_plan.get("selection") or {}).get(
            "xdrDetections", []
        )
    )
    expected_sources = sorted({
        str(item.get("sourceId") or "").casefold()
        for item in selection_plan.get("xdrDetections") or []
        if isinstance(item, dict)
        and item.get("included") is True
        and item.get("sourceId")
    })
    parity_paths = sorted(
        str(value).replace("\\", "/")
        for value in parity.get("testedDetectionPaths") or []
    )
    parity_sources = sorted({
        str(value).casefold()
        for value in parity.get("testedSourceIds") or []
    })
    matches = bool(
        stage_passed
        and parity.get("status") == "passed"
        and parity.get("qualificationScopeVerified") is True
        and isinstance(current_plan_sha, str)
        and bool(current_plan_sha)
        and isinstance(selection_plan.get("planSha256"), str)
        and bool(selection_plan.get("planSha256"))
        and current_plan_sha == selection_plan.get("planSha256")
        and parity.get("selectionPlanSha256") == current_plan_sha
        and parity_paths == expected_paths
        and parity_sources == expected_sources
        and (parity.get("qualificationScope") or {}).get("selectionComplete") is True
    )
    return (
        matches,
        "parity evidence matches the exact current applied selection"
        if matches
        else "parity evidence does not cover the exact current applied selection",
    )


def _error(
    stage: str,
    message: Any,
    *,
    provider: str | None = None,
    status_code: Any = None,
    code: Any = None,
    details: Any = None,
) -> dict[str, Any]:
    return {
        "stage": stage,
        "provider": provider,
        "statusCode": status_code,
        "code": code,
        "message": str(message),
        "details": details,
    }


def _entity_recommendation(source: dict[str, Any], conversion_notes: list[str]) -> str | None:
    if not any(
        "mapping" in value.lower() or "entity confirmation required" in value.lower()
        for value in conversion_notes
    ):
        return None
    for entity in source.get("entityMappings") or []:
        if entity.get("entityType") != "Account":
            continue
        for field in entity.get("fieldMappings") or []:
            if field.get("identifier") == "Name":
                column = str(field.get("columnName") or "the projected user column")
                return (
                    f"Verify whether `{column}` is always a complete UPN. If confirmed, "
                    f"map it to Account.upnColumn. Otherwise project an Entra user ID, SID, "
                    "or account name plus domain. Do not infer identity semantics from the "
                    "column name alone."
                )
    return None


def _current_source_whitelist(
    root: Path,
    runtime_reports: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, Any]]:
    from solution_manager.qualification.runtime import current_runtime_evidence

    try:
        evidence = current_runtime_evidence(root)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        return {}, {
            "passed": False,
            "sourceStatus": "unavailable",
            "sourceWhitelist": [],
            "runtimeUnavailable": str(exc),
        }
    reports_by_provider = {
        str(report.get("provider") or ""): report for report in runtime_reports
    }
    assessments: dict[tuple[str, str], dict[str, Any]] = {}
    for item in evidence.get("sourceWhitelist") or []:
        provider = str(evidence.get("sentinelProvider") or "")
        report = reports_by_provider.get(provider) or {}
        assessments[(provider, str(item.get("detection") or ""))] = {
            **item,
            "provider": provider,
            "surface": report.get("querySurface"),
            "sourceExecutionPassed": False,
            "runtimeQualified": bool(evidence.get("passed")),
        }
    return assessments, evidence


def build_solution_report(
    solution: str | Path,
    *,
    ingestion_reports: list[str | Path] | None = None,
) -> dict[str, Any]:
    from solution_manager.migration import workbook_workflow
    root = Path(solution).expanduser().resolve()
    workflow = _read_json(existing_artifact_path(root, "workflow-state.json"))
    workbook_context = workflow.get("context")
    has_workbook_state = "workbooks" in workflow or (
        isinstance(workbook_context, dict) and "workbookCapabilityVersion" in workbook_context
    )
    current_workflow = workbook_workflow.current_state(root) if has_workbook_state else None
    workbook_only = bool(current_workflow and workbook_workflow.enabled(current_workflow)
                         and not workbook_workflow.has_analytic_rules(root))
    if workbook_only:
        analytic, output = root / "Analytic Rules", root / "XDR Detections"
    else:
        root, analytic, output = solution_paths(solution)
    reports = report_directory(root, create=True)
    manifest = _read_json(existing_artifact_path(root, "manifest.json"))
    runtime_consent = {"status": "notApplicable"} if workbook_only else runtime_query_consent_status(root)
    manifest_by_source = {}
    for item in manifest.get("results") or []:
        reference = str(item.get("sourceRelativePath") or item.get("source") or "").replace("\\", "/")
        root_prefix = root.as_posix() + "/"
        if reference.startswith(root_prefix):
            reference = reference[len(root_prefix):]
        manifest_by_source[reference] = item
    runtime_reports = [
        _read_json(path)
        for path in existing_artifacts(root, "runtime-validation.*.json")
    ]
    current_source_whitelist, runtime_evidence = _current_source_whitelist(
        root, runtime_reports
    )
    deployment = _read_json(existing_artifact_path(root, "deployment.graph.json"))
    analytic_deployment = _read_json(
        existing_artifact_path(root, "deployment.sentinel.json")
    )
    parity = _read_json(existing_artifact_path(root, "alert-parity-report.json"))
    query_parity = _read_json(existing_artifact_path(root, "mock-query-parity.json"))
    packaging, selected_package_reference = _selected_packaging_report(root, workflow)
    deployment_by_id = {
        str(item.get("id")): item for item in deployment.get("results") or []
    }
    analytic_deployment_by_id = {
        str(item.get("id")): item
        for item in analytic_deployment.get("results") or []
    }
    parity_by_detection = {
        str(item.get("detection")).replace("\\", "/"): item for item in parity.get("comparisons") or []
    }
    query_parity_by_detection = {
        str(item.get("detection")).replace("\\", "/"): item
        for item in query_parity.get("comparisons") or []
    }
    tactic_projection_by_id = {
        str(item.get("detectionId")): item
        for item in packaging.get("tacticProjection") or []
        if isinstance(item, dict) and item.get("detectionId")
    }
    identity_projection_by_id = {
        str(item.get("packagedId")): item
        for item in packaging.get("identityProjection") or []
        if isinstance(item, dict) and item.get("packagedId")
    }
    ingestion = [
        _read_json(resolve_artifact_reference(root, path))
        for path in ingestion_reports or []
    ]

    rules: list[dict[str, Any]] = []
    for source_path in ([] if workbook_only else analytic_rule_files(root)):
        source = yaml.safe_load(source_path.read_text(encoding="utf-8-sig")) or {}
        conversion = manifest_by_source.get(source_path.relative_to(root).as_posix()) or {}
        detection_name = source_path.relative_to(analytic).as_posix()
        detection_path = content_path(output, detection_name)
        detection: dict[str, Any] = {}
        structural_errors: list[str] = []
        structural_warnings: list[str] = []
        if detection_path.exists():
            try:
                detection = (
                    yaml.safe_load(detection_path.read_text(encoding="utf-8-sig")) or {}
                )
                structural_errors = validate_document(detection)
                structural_warnings = custom_detail_binding_warnings(detection)
            except (OSError, ValueError, yaml.YAMLError) as exc:
                structural_errors = [str(exc)]
        properties = detection.get("properties") or {}
        detection_id = str(properties.get("id") or "")
        tactic_projection = tactic_projection_by_id.get(detection_id)
        identity_projection = identity_projection_by_id.get(detection_id)
        analytic_runtime: list[dict[str, Any]] = []
        custom_runtime: list[dict[str, Any]] = []
        rule_warnings = list(conversion.get("warnings") or []) + [
            value
            for value in structural_warnings
            if value not in (conversion.get("warnings") or [])
        ]
        errors: list[dict[str, Any]] = []
        for value in conversion.get("errors") or []:
            errors.append(_error("conversion", value, provider="local-cli"))
        for value in structural_errors:
            errors.append(_error("structural-validation", value, provider="local-cli"))
        for report in runtime_reports:
            provider = str(report.get("provider") or "unknown")
            item = next(
                (
                    candidate
                    for candidate in report.get("results") or []
                    if str(candidate.get("detection") or "").replace("\\", "/") == detection_name
                ),
                None,
            )
            if not item:
                continue
            platform = str(report.get("platform") or "unknown")
            is_sentinel = "Sentinel" in platform
            expected_query = (
                str(source.get("query") or "")
                if is_sentinel
                else str(
                    (((properties.get("queryCondition") or {}).get("queryText")) or "")
                )
            )
            expected_query_hash = hashlib.sha256(
                expected_query.encode("utf-8")
            ).hexdigest()
            recorded_query_hash = item.get("querySha256")
            query_hash_matches = recorded_query_hash == expected_query_hash
            runtime_status = item.get("status")
            stale_query_message = None
            if runtime_status == "passed" and not query_hash_matches:
                runtime_status = "blocked"
                stale_query_message = (
                    "runtime success is stale or unbound: the exact current query was not "
                    "validated; rerun this complete query family before claiming validation"
                )
            runtime_item = {
                "provider": provider,
                "platform": platform,
                "status": runtime_status,
                "recordedStatus": item.get("status"),
                "querySha256": recorded_query_hash,
                "queryHashStatus": "matches" if query_hash_matches else "stale-or-missing",
                "rowCount": item.get("rowCount"),
                "providerFallback": report.get("providerFallback"),
            }
            source_whitelist = (
                current_source_whitelist.get((provider, detection_name))
                if is_sentinel
                else None
            )
            if source_whitelist:
                runtime_item["sourceWhitelist"] = source_whitelist
                rule_warnings.append(
                    f"Source runtime whitelist classified the raw failed query for "
                    f"{source_whitelist['table']}: {source_whitelist['reason']} "
                    "The source query remains failed; this does not qualify XDR runtime, "
                    "schema bindings, validation review gates, or alert parity."
                )
            (analytic_runtime if is_sentinel else custom_runtime).append(runtime_item)
            if stale_query_message or item.get("status") in {"failed", "blocked"}:
                errors.append(
                    _error(
                        (
                            "analytic-rule-runtime-validation"
                            if is_sentinel
                            else "custom-detection-runtime-validation"
                        ),
                        stale_query_message or item.get("error") or item.get("status"),
                        provider=provider,
                        status_code=item.get("statusCode"),
                        details=item.get("errorDetails"),
                    )
                )
        deployed = deployment_by_id.get(detection_id) or {}
        analytic_deployed = analytic_deployment_by_id.get(str(source.get("id"))) or {}
        if analytic_deployed and not analytic_deployed.get("success"):
            arm_error = analytic_deployed.get("error") or {}
            errors.append(
                _error(
                    "analytic-rule-deployment",
                    arm_error.get("message") or arm_error,
                    provider=str(
                        analytic_deployment.get("provider")
                        or "azure-resource-manager"
                    ),
                    status_code=analytic_deployed.get("statusCode"),
                    code=arm_error.get("code"),
                    details=arm_error,
                )
            )
        if deployed and not deployed.get("success"):
            graph_error = deployed.get("error") or {}
            errors.append(
                _error(
                    "custom-detection-deployment",
                    graph_error.get("message") or graph_error,
                    provider=str(deployment.get("provider") or "microsoft-graph"),
                    status_code=deployed.get("statusCode"),
                    code=graph_error.get("code"),
                    details=graph_error,
                )
            )
        parity_item = parity_by_detection.get(detection_name) or {}
        query_parity_item = query_parity_by_detection.get(detection_name) or {}
        if parity_item and not parity_item.get("passed"):
            errors.append(
                _error(
                    "alert-parity",
                    "Analytic Rule and Custom Detection alerts are not strictly equal",
                    provider="sentinel-and-defender",
                    details=parity_item,
                )
            )
        if query_parity_item and not query_parity_item.get("passed"):
            errors.append(
                _error(
                    "query-result-parity",
                    "Analytic Rule and Custom Detection query results are not equal",
                    provider="sentinel-and-defender",
                    details=query_parity_item,
                )
            )
        conversion_notes = [
            str(value)
            for value in [
                *(conversion.get("errors") or []),
                *(conversion.get("reviewReasons") or []),
            ]
        ]
        rules.append(
            {
                "name": source.get("name") or source_path.stem,
                "sourceFile": str(source_path),
                "sourceSha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                "outputFile": str(detection_path),
                "queries": {
                    "source": source.get("query"),
                    "converted": (properties.get("queryCondition") or {}).get("queryText"),
                },
                "attackClassification": {
                    "sourceTactics": source.get("tactics"),
                    "sourceTechniques": source.get("relevantTechniques"),
                    "draftTactics": (
                        (properties.get("detectionAction") or {}).get("alertTemplate") or {}
                    ).get("tactics"),
                    "originalTactics": (
                        (detection.get("contentProvenance") or {}).get("conversion") or {}
                    ).get("originalTactics"),
                    "originalTechniques": (
                        (detection.get("contentProvenance") or {}).get("conversion") or {}
                    ).get("originalTechniques"),
                },
                "analyticRule": {
                    "id": source.get("id"),
                    "sourceStatus": source.get("status"),
                    "deploymentStatus": (
                        "validated-by-alert-parity"
                        if parity_item
                        else analytic_deployed.get("operation") or "not-recorded"
                    ),
                    "alertStatus": (
                        "passed"
                        if parity_item.get("passed")
                        else "failed"
                        if parity_item
                        else "not-run"
                    ),
                    "runtime": analytic_runtime,
                },
                "customDetection": {
                    "id": detection_id or None,
                    "conversionStatus": conversion.get("status") or "not-run",
                    "reviewRequired": bool(conversion.get("reviewRequired")),
                    "reviewReasons": list(conversion.get("reviewReasons") or []),
                    "reviewScope": (
                        (detection.get("contentProvenance") or {}).get("conversion") or {}
                    ).get("reviewScope"),
                    "reviewDecisions": (
                        (detection.get("contentProvenance") or {}).get("conversion") or {}
                    ).get("reviewDecisions") or [],
                    "structuralStatus": (
                        "passed"
                        if detection and not structural_errors
                        else "failed"
                        if detection
                        else "not-generated"
                    ),
                    "deploymentStatus": (
                        deployed.get("operation") or "not-run"
                    ),
                    "runtime": custom_runtime,
                    "alertStatus": (
                        "passed"
                        if parity_item.get("passed")
                        else "failed"
                        if parity_item
                        else "not-run"
                    ),
                },
                "packagingProjection": tactic_projection,
                "packagingIdentity": identity_projection,
                "entityRecommendation": _entity_recommendation(
                    source, conversion_notes
                ),
                "queryParity": {
                    "status": (
                        "passed"
                        if query_parity_item.get("passed")
                        else "failed"
                        if query_parity_item
                        else "not-run"
                    ),
                    "matchKey": query_parity_item.get("matchKey"),
                    "analyticRuleRows": query_parity_item.get("analyticRuleRows"),
                    "customDetectionRows": query_parity_item.get(
                        "customDetectionRows"
                    ),
                },
                "warnings": rule_warnings,
                "informational": list(
                    conversion.get("informational") or []
                    if "informational" in conversion
                    else (
                        (detection.get("contentProvenance") or {}).get("conversion") or {}
                    ).get("informational") or []
                ) + ([
                    "V3.1 ARM packaging retains authored tactic "
                    f"{', '.join(tactic_projection.get('packagedTactics') or []) or '(none)'} "
                    "and omits "
                    f"{', '.join(tactic_projection.get('omittedTactics') or []) or '(none)'}; "
                    "authored YAML is unchanged and this projection is not parity"
                ] if tactic_projection else []) + ([
                    "V3.1 ARM packaging normalized Custom Detection ID "
                    f"{identity_projection.get('inputId')!r} to {identity_projection.get('packagedId')!r}; "
                    "source/provenance YAML remains unchanged and deployed IDs are not migrated"
                ] if identity_projection and identity_projection.get("changed") else []),
                "errors": errors,
            }
        )

    report = {
        "solution": root.name,
        "solutionPath": str(root),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "workflow": {
            "runId": workflow.get("runId"),
            "profile": (workflow.get("context") or {}).get("workflowProfile"),
            "profileSelectionConfirmed": (workflow.get("context") or {}).get("profileSelectionConfirmed"),
            "status": workflow.get("workflowStatus"),
            "workspaceConfigured": bool(
                (workflow.get("context") or {}).get("workspaceResourceId")
            ),
            "stages": {
                name: {
                    key: stage.get(key)
                    for key in (
                        "status", "attempts", "message", "evidence", "updatedAt",
                        "startedAt", "completedAt", "artifacts",
                    )
                    if stage.get(key) is not None
                }
                for name, stage in (workflow.get("stages") or {}).items()
            },
            "packageFreshness": _package_freshness(root, workflow),
            "runtimeQueryConsent": runtime_consent,
        },
        "runtimeAssessment": {
            "validationStageStatus": (
                ((workflow.get("stages") or {}).get("validation") or {}).get("status")
            ),
            "sourceStatus": runtime_evidence.get("sourceStatus", "not-run"),
            "sourceWhitelist": [
                {
                    **item,
                    "provider": runtime_evidence.get("sentinelProvider"),
                    "runtimeQualified": bool(runtime_evidence.get("passed")),
                }
                for item in runtime_evidence.get("sourceWhitelist") or []
            ],
            "fullyRuntimeQualified": (
                bool(runtime_evidence.get("passed"))
                if runtime_reports
                else None
            ),
            "runtimeUnavailable": runtime_evidence.get("runtimeUnavailable"),
        },
        "summary": {
            "conversionScope": manifest.get("scope") or {},
            "rules": len(rules),
            "converted": sum(
                item["customDetection"]["conversionStatus"] == "converted"
                for item in rules
            ),
            "needsReview": sum(
                item["customDetection"]["reviewRequired"]
                for item in rules
            ),
            "deploymentReady": sum(
                item["customDetection"]["conversionStatus"] == "converted"
                and not item["customDetection"]["reviewRequired"]
                and item["customDetection"]["structuralStatus"] == "passed"
                and len(item["attackClassification"].get("draftTactics") or []) <= 1
                for item in rules
            ),
            "strictParityPassed": sum(
                item["customDetection"]["alertStatus"] == "passed" for item in rules
            ),
            "analyticRuntimePassed": sum(
                any(
                    runtime["status"] == "passed"
                    for runtime in item["analyticRule"]["runtime"]
                )
                for item in rules
            ),
            "customRuntimePassed": sum(
                any(
                    runtime["status"] == "passed"
                    for runtime in item["customDetection"]["runtime"]
                )
                for item in rules
            ),
            "queryParityPassed": sum(
                item["queryParity"]["status"] == "passed" for item in rules
            ),
            "errors": sum(len(item["errors"]) for item in rules),
            "informational": sum(len(item["informational"]) for item in rules),
            "rulesWithInformation": sum(bool(item["informational"]) for item in rules),
            "packagedTacticOmissions": sum(
                len((item.get("packagingProjection") or {}).get("omittedTactics") or [])
                for item in rules
            ),
            "packageIdentityNormalizations": sum(
                bool((item.get("packagingIdentity") or {}).get("changed"))
                for item in rules
            ),
            "providerFallbackRules": sum(
                any(runtime.get("providerFallback") for side in (
                    item["analyticRule"], item["customDetection"],
                ) for runtime in side["runtime"])
                for item in rules
            ),
        },
        "rules": rules,
        "ingestion": ingestion,
        "artifacts": {
            "transformationReport": manifest.get("transformationReport"),
            "runtimeReports": [
                {
                    "provider": item.get("provider"),
                    "providerFallback": item.get("providerFallback"),
                    "jsonReport": item.get("jsonReport"),
                    "htmlReport": item.get("htmlReport"),
                }
                for item in runtime_reports
            ],
            "deploymentReport": deployment.get("reportPath"),
            "analyticDeploymentReport": analytic_deployment.get("reportPath"),
            "queryParityReport": query_parity.get("reportPath"),
            "alertParityReport": parity.get("reportPath"),
            "packagingReport": packaging.get("packageReport"),
            "selectedPackagingEvidence": selected_package_reference,
            "qualificationDcrPreflight": (
                str(reports / "qualification-dcr-preflight.json")
                if (reports / "qualification-dcr-preflight.json").is_file()
                else None
            ),
            "ingestionReports": [
                item.get("reportPath") for item in ingestion if item.get("reportPath")
            ],
        },
    }
    if packaging.get("selectionOutcome") == "partial-package-validated":
        selection_plan = _read_run_json(
            root,
            report_directory(root),
            packaging.get("selectionPlanPath"),
        )
        selection_summary = selection_plan.get("summary") or {}
        if selection_summary.get("outcome") == "partial":
            profile = (workflow.get("context") or {}).get("workflowProfile")
            stages = workflow.get("stages") or {}
            parity_passed = (stages.get("alertParity") or {}).get("status") == "passed"
            qualification_progression_passed = bool(
                profile == "qualification"
                and workflow.get("workflowStatus") in {"completed", "partialCompleted"}
                and all(
                    (stages.get(name) or {}).get("status") == "passed"
                    for name in (
                        "packaging", "deployment", "mockIngestion", "alertParity"
                    )
                )
            )
            parity_scope_matches = False
            parity_scope_reason = "current selected-scope parity evidence is unavailable"
            try:
                from solution_manager.packaging.packaging_selection import current_applied_package_selection

                applied = current_applied_package_selection(root)
                applied_plan = applied.get("plan") if isinstance(applied, dict) else None
                parity_scope_matches, parity_scope_reason = (
                    _partial_selection_parity_matches(
                        selection_plan,
                        parity,
                        applied_plan,
                        stage_passed=(
                            parity_passed and qualification_progression_passed
                        ),
                    )
                )
            except (OSError, RuntimeError, TypeError, ValueError):
                parity_scope_matches = False
            report["partialSolution"] = {
                "status": (
                    "selected-subset-qualified"
                    if profile == "qualification" and parity_scope_matches
                    else "partial-package-validated"
                ),
                "profile": profile,
                "fullInventoryQualification": "not-qualified",
                "fullInventoryParity": "not-proven",
                "selectedParityScope": (
                    "exact-current-selection"
                    if parity_scope_matches else "not-proven"
                ),
                "selectedParityScopeReason": parity_scope_reason,
                "qualificationScopeVerified": parity_scope_matches,
                "selectionPlanSha256": selection_plan.get("planSha256"),
                "selectionSummary": selection_summary,
                "selectedDetections": [
                    {
                        "id": item.get("id"),
                        "sourceId": item.get("sourceId"),
                        "path": item.get("path"),
                        "evidencePaths": item.get("evidencePaths") or [],
                    }
                    for item in selection_plan.get("xdrDetections") or []
                    if item.get("included") is True
                ],
                "excludedAnalyticRules": [
                    {
                        "id": item.get("id"),
                        "path": item.get("path"),
                        "reasons": item.get("reasons") or [],
                    }
                    for item in selection_plan.get("analyticRules") or []
                    if item.get("included") is not True
                ],
                "excludedDetections": [
                    {
                        "id": item.get("id"),
                        "sourceId": item.get("sourceId"),
                        "path": item.get("path"),
                        "reasons": item.get("reasons") or [],
                    }
                    for item in selection_plan.get("xdrDetections") or []
                    if item.get("included") is not True
                ],
            }
    json_path = reports / JSON_NAME
    if current_workflow and workbook_workflow.enabled(current_workflow):
        report["workbooks"] = workbook_workflow.summary(root, current_workflow)
    html_path = reports / HTML_NAME
    report["jsonReport"] = str(json_path)
    report["htmlReport"] = str(html_path)
    report["deploymentPlanning"] = _planning_summary(
        root, packaging, report["workflow"], workflow
    )
    report["qualificationPreflight"] = _qualification_preflight(
        root, reports, workflow
    )
    report["startupSetup"] = _startup_setup_summary(
        root, reports, workflow, report["qualificationPreflight"],
        report["deploymentPlanning"],
    )
    target_reference = reports / "qualification-target.json"
    target_link = _local_flow_evidence_link(root, reports, str(target_reference))
    report["artifacts"]["qualificationTarget"] = (
        str(target_reference) if target_link.get("available") is True else None
    )
    preflight_packet_reference = reports / "qualification-preflight-packet.json"
    preflight_packet_link = _local_flow_evidence_link(root, reports, str(preflight_packet_reference))
    report["artifacts"]["qualificationPreflightPacket"] = (
        str(preflight_packet_reference) if preflight_packet_link.get("available") is True else None
    )
    pipeline_state_reference = reports / "qualification-pipeline-state.json"
    pipeline_state_link = _local_flow_evidence_link(root, reports, str(pipeline_state_reference))
    report["artifacts"]["qualificationPipelineState"] = (
        str(pipeline_state_reference) if pipeline_state_link.get("available") is True else None
    )
    pipeline_state = _read_run_json(root, reports, "qualification-pipeline-state.json")
    if pipeline_state:
        qual_stages = (
            pipeline_state.get("qualificationStages")
            if isinstance(pipeline_state.get("qualificationStages"), dict)
            else {}
        )
        report["qualificationPipeline"] = {
            "status": pipeline_state.get("status"),
            "preflightPassed": bool(pipeline_state.get("preflightPassed")),
            "deploymentVerified": bool(pipeline_state.get("deploymentVerified")),
            "mockIngestionVerified": bool(pipeline_state.get("mockIngestionVerified")),
            "ruleParityVerified": pipeline_state.get("ruleParityVerified"),
            "functionalQualificationVerified": bool(pipeline_state.get("functionalQualificationVerified")),
            "promotionGate": _safe_plan_value(pipeline_state.get("promotionGate") or {}),
            "qualificationStages": _safe_plan_value(qual_stages),
            "workbookContractResult": _safe_plan_value(pipeline_state.get("workbookContractResult") or {}),
            "updatedAt": pipeline_state.get("updatedAt"),
        }
    from solution_manager.reporting.decision_manifest import build_sanitized_decision_manifest

    decision_manifest = build_sanitized_decision_manifest(root)
    report["decisionManifestSummary"] = {
        "schemaVersion": decision_manifest["schemaVersion"],
        "decisionCount": len(decision_manifest["decisions"]),
        "totalDecisions": len(decision_manifest["decisions"]),
        "count": len(decision_manifest["decisions"]),
        "manifestSha256": decision_manifest["manifestSha256"],
        "sanitizedVerified": True,
        "scopes": sorted({item["scope"] for item in decision_manifest["decisions"]}),
    }
    report["flowEvidence"] = _build_flow_evidence(
        root, reports, report["workflow"], report["artifacts"], packaging
    )
    write_json_artifact(root, json_path, report)
    report["flowEvidence"]["report"].append(
        _local_flow_evidence_link(root, reports, json_path)
    )
    write_json_artifact(root, json_path, report)
    html_path.write_text(render_solution_report(portable_artifact(root, report)), encoding="utf-8", newline="\n")
    return report


def render_solution_report(report: dict[str, Any]) -> str:
    return render_dashboard(report)
