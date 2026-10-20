from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from solution_manager.core.artifacts import (
    report_directory,
    repository_root,
    write_json_artifact,
    require_solution_conversion_scope,
)
from solution_manager.core.content_paths import content_path


PACKAGER_NAME = "V3.1"
TACTIC_PROJECTION_PREFIX = "V3.1 TACTIC PROJECTION: "
IDENTITY_PROJECTION_PREFIX = "V3.1 ID PROJECTION: "
DATA_EXCLUSIONS = {
    "parameter.json",
    "parameters.json",
    "system_generated_metadata.json",
    "testparameters.json",
}
PACKAGE_OUTPUT_DIRECTORIES = {
    "package",
    "logs",
    "evidence",
    ".git",
    ".venv",
    "__pycache__",
}
V31_TARGET_VERSION_PATTERN = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z"
)
V31_TOOLKIT_PATHS = (
    "Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3_1.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/createSolutionLocal.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/get-ccp-details.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/summaryRules.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/contentDeploymentParameters.json",
    "Tools/Create-Azure-Sentinel-Solution/common/contentDeploymentParameters.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/templating/baseMainTemplate.json",
    "Tools/Create-Azure-Sentinel-Solution/common/templating/baseCreateUiDefinition.json",
    "Tools/Create-Azure-Sentinel-Solution/common/customDetections.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/defenderWorkbooks.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/customerUsageAttribution.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/AttributionMetadata.cs",
    "Tools/Create-Azure-Sentinel-Solution/common/versionPolicy.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/standardLogStreams.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/createCCPConnector.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/storageAccountDeploymentTemplate.ps1",
    "Tools/Create-Azure-Sentinel-Solution/common/eventGridManagedIdentityDeploymentTemplate.ps1",
    "Tools/Create-Azure-Sentinel-Solution/arm-ttk/download-arm-ttk.ps1",
    "Tools/Create-Azure-Sentinel-Solution/arm-ttk/run-arm-ttk-in-automation.ps1",
    "Tools/SentinelToXDRMigration/kql/rename-parser-bindings.cjs",
)
_NON_PATH_ARRAYS = {
    "dependentdomainsolutionids",
    "staticdataconnectorids",
    "xdr detections",
    "custom detections",
}
_ENCODED_CONTENT_ARRAYS = {
    "parsers",
    "data connectors",
    "dataconnectors",
    "playbooks",
    "workbooks",
    "xdr workbooks",
    "analytic rules",
    "analytics rules",
    "hunting queries",
    "watchlists",
    "summary rules",
    "summaryrules",
    "xdr detections",
    "custom detections",
    "savedsearches",
}


def validate_v31_target_version(version: str | None) -> str:
    """Validate an explicitly selected canonical V3.1 solution release version."""
    if not isinstance(version, str) or not V31_TARGET_VERSION_PATTERN.fullmatch(version):
        raise ValueError(
            "target version must be canonical major.minor.patch in the V3.1 "
            "range >= 3.2.0 and < 4.0.0"
        )
    major, minor, _patch = version.split(".")
    if major != "3" or minor in {"0", "1"}:
        raise ValueError(
            "target version must be in the V3.1 range >= 3.2.0 and < 4.0.0"
        )
    return version


def validate_v31_effective_version(
    source_version: str | None, version_bump: str, target_version: str | None = None,
) -> str:
    """Validate the selected solution release without consuming its version action."""
    if target_version is not None:
        return validate_v31_target_version(target_version)
    if not isinstance(source_version, str) or not V31_TARGET_VERSION_PATTERN.fullmatch(source_version):
        return validate_v31_target_version(source_version)
    major, minor, patch = (int(part) for part in source_version.split("."))
    if version_bump == "patch":
        patch += 1
    elif version_bump == "minor":
        minor, patch = minor + 1, 0
    elif version_bump == "major":
        major, minor, patch = major + 1, 0, 0
    elif version_bump != "none":
        raise ValueError("version bump must be none, patch, minor, or major")
    return validate_v31_target_version(f"{major}.{minor}.{patch}")


def package_input_file_hashes(solution: str | Path) -> dict[str, str]:
    """Return the complete package-input file manifest, excluding generated output."""
    root = Path(solution).expanduser().resolve()
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        parts = relative.parts
        if any(part.lower() in PACKAGE_OUTPUT_DIRECTORIES for part in parts):
            continue
        if any(part.lower() == ".env" or part.lower().startswith(".env.") for part in parts):
            continue
        if path.is_symlink():
            raise ValueError(f"package input contains an unsafe symlink: {relative.as_posix()}")
        if not path.is_file():
            continue
        files[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def package_input_identity(solution: str | Path) -> dict[str, Any]:
    """Hash the complete local solution input tree, excluding generated/runtime output."""
    files = package_input_file_hashes(solution)
    canonical = json.dumps(
        [{"path": path, "sha256": digest} for path, digest in files.items()],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "sha256": hashlib.sha256(canonical).hexdigest(),
        "fileCount": len(files),
    }


def solution_data_version(solution: str | Path) -> str | None:
    root = Path(solution).expanduser().resolve()
    data_directory = root / "Data"
    if not data_directory.is_dir():
        return None
    try:
        value = _value(_read_json(_solution_data_file(data_directory)), "Version")
        return str(value or "").strip() or None
    except (OSError, ValueError):
        return None


def version_bump_was_consumed(
    before: str | None,
    after: str | None,
    version_bump: str,
) -> bool:
    if not before or not after or before == after:
        return False
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", before)
    if not match:
        return False
    major, minor, patch = (int(value) for value in match.groups())
    if version_bump == "patch":
        expected = f"{major}.{minor}.{patch + 1}"
    elif version_bump == "minor":
        expected = f"{major}.{minor + 1}.0"
    elif version_bump == "major":
        expected = f"{major + 1}.0.0"
    else:
        return False
    return after == expected


def _package_artifact_hashes(paths: dict[str, Path]) -> dict[str, str]:
    return {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in sorted(paths.items())
    }


def _canonical_digest(value: dict[str, Any]) -> str:
    content = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def _deployment_parameters(
    template: dict[str, Any], ui: dict[str, Any], test_parameters: dict[str, Any],
    *, has_xdr: bool, has_workbooks: bool | None = None, contract_path: Path | None = None,
) -> dict[str, bool]:
    contract_path = contract_path or (
        Path(__file__).resolve().parents[3] / "Create-Azure-Sentinel-Solution"
        / "common" / "contentDeploymentParameters.json"
    )
    contract = _read_json(contract_path)
    parameters = template.get("parameters", {})
    if {"E5Flavor", "RegisterE5Content"} & parameters.keys():
        raise RuntimeError("V3.1 package declares obsolete E5 deployment controls; rebuild it.")
    selected = {name: value for name, value in parameters.items() if name.startswith("Deploy")}
    outputs = ui.get("parameters", {}).get("outputs", {})
    controls = {
        element["name"]: element
        for step in ui.get("parameters", {}).get("steps", [])
        if step.get("name") == "contentSelection"
        for element in step.get("elements", [])
    }
    if set(selected) != set(controls) or set(selected) != {
        name for name in outputs if name.startswith("Deploy")
    }:
        raise RuntimeError("V3.1 deployment parameters and UI selections disagree.")
    if test_parameters != parameters:
        raise RuntimeError("V3.1 testParameters.json must match the declared parameter subset.")
    for name, value in selected.items():
        expected = contract.get(name)
        if (
            expected is None or value.get("type") != "bool"
            or value.get("defaultValue") is not expected["defaultValue"]
            or controls[name].get("defaultValue") is not expected["defaultValue"]
            or controls[name].get("type") != "Microsoft.Common.CheckBox"
            or outputs[name] != f"[steps('contentSelection').{name}]"
        ):
            raise RuntimeError(f"Invalid V3.1 content selection contract for {name}.")
    if has_xdr != ("DeployCustomDetection" in selected):
        raise RuntimeError("V3.1 Custom Detection declaration does not match the packaged XDR inputs.")
    if has_workbooks is not None and has_workbooks != ("DeployDefenderWorkbook" in selected):
        raise RuntimeError("V3.1 Defender workbook declaration does not match the selected workbook inputs.")
    return {name: value["defaultValue"] for name, value in selected.items()}


def _solution_data_file(data_directory: Path) -> Path:
    solution = data_directory.parent.resolve()
    candidates = sorted(
        path
        for path in data_directory.glob("*.json")
        if path.name.lower() not in DATA_EXCLUSIONS
    )
    if len(candidates) != 1:
        raise ValueError(
            f"expected exactly one solution data JSON in {data_directory}, "
            f"found {len(candidates)}"
        )
    return content_path(solution, candidates[0].relative_to(solution))


def _validate_solution_name(name: Any, solution: Path) -> None:
    if (
        not isinstance(name, str)
        or not name.strip()
        or name in {".", ".."}
        or "/" in name
        or "\\" in name
        or ":" in name
        or name.casefold() != solution.name.casefold()
    ):
        raise ValueError(
            "solution Data Name must match the selected solution folder and must not be a path"
        )


def _solution_relative_reference(solution: Path, reference: Any, label: str) -> Path:
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError(f"solution Data {label} contains an invalid local path reference")
    normalized = reference.replace("\\", "/")
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", normalized):
        raise ValueError(f"solution Data {label} must use a local solution-relative path")
    parts = normalized.split("/")
    if normalized.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"solution Data {label} path must be relative and contained: {reference!r}")
    if parts[0] == "Solutions":
        if len(parts) < 3 or parts[1] != solution.name:
            raise ValueError(
                f"solution Data {label} repository path must name the selected solution"
            )
        normalized = "/".join(parts[2:])
        parts = normalized.split("/")
    if any(part.lower() in {"logs", "reports", "evidence"} for part in parts):
        raise ValueError("solution Data content arrays must never include Logs, Reports or Evidence")
    if any(part.lower() == ".env" or part.lower().startswith(".env.") for part in parts):
        raise ValueError(
            "solution Data content arrays must never include local .env configuration"
        )
    candidate = content_path(solution, normalized)
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError(f"referenced solution content does not exist as a local file: {reference}")
    return candidate.resolve()


def _validate_solution_package_inputs(solution: Path, document: dict[str, Any]) -> None:
    name = _value(document, "Name")
    _validate_solution_name(name, solution)

    metadata = _value(document, "Metadata")
    if metadata is not None:
        metadata_path = _solution_relative_reference(solution, metadata, "Metadata")
        if not metadata_path.is_relative_to(solution.resolve()):
            raise ValueError("solution Data Metadata path resolves outside the selected solution")

    for key, value in list(document.items()):
        if isinstance(value, str) and key.casefold() in _ENCODED_CONTENT_ARRAYS:
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"solution Data {key} must be a JSON-encoded content array"
                ) from exc
            if not isinstance(value, list) or any(
                not isinstance(reference, str) or not reference.strip()
                for reference in value
            ):
                raise ValueError(f"solution Data {key} must be a JSON-encoded content array")
            document[key] = value
        if not isinstance(value, list):
            continue
        if key.casefold() in {"xdr detections", "custom detections"}:
            for reference in value:
                if isinstance(reference, str):
                    parts = reference.replace("\\", "/").split("/")
                    if any(part.lower() in {"logs", "reports", "evidence"} for part in parts):
                        raise ValueError(
                            "solution Data content arrays must never include Logs, Reports or Evidence"
                        )
                    if any(
                        part.lower() == ".env" or part.lower().startswith(".env.")
                        for part in parts
                    ):
                        raise ValueError(
                            "solution Data content arrays must never include local .env configuration"
                        )
            continue
        if key.casefold() in _NON_PATH_ARRAYS:
            continue
        for reference in value:
            _solution_relative_reference(solution, reference, key)


def _validate_v31_toolkit_root(toolkit_root: str | Path) -> Path:
    if isinstance(toolkit_root, str) and not toolkit_root.strip():
        raise ValueError("V3.1 toolkit root must not be empty")
    try:
        root = Path(toolkit_root).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"V3.1 toolkit root does not exist: {toolkit_root}") from exc
    if not root.is_dir():
        raise ValueError(f"V3.1 toolkit root is not a directory: {root}")
    missing = [relative for relative in V31_TOOLKIT_PATHS if not (root / relative).is_file()]
    if missing:
        raise ValueError(
            f"V3.1 toolkit root is incomplete: {root}; missing "
            + ", ".join(missing)
        )
    return root


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return value


def _value(document: dict[str, Any], name: str) -> Any:
    for key, value in document.items():
        if key.lower() == name.lower():
            return value
    return None


def _xdr_references(solution: Path, document: dict[str, Any]) -> list[Path]:
    keys = [
        key for key in ("XDR Detections", "Custom Detections")
        if any(name.casefold() == key.casefold() for name in document)
    ]
    if len(keys) > 1:
        raise ValueError("solution data has ambiguous XDR Detection selection arrays")
    if not keys:
        folder = solution / "XDR Detections"
        discovered = [
            path for path in folder.rglob("*")
            if path.is_file() and path.suffix.casefold() in {".yaml", ".yml"}
        ] if folder.is_dir() else []
        if discovered:
            raise ValueError(
                "solution data is missing an explicit XDR Detections array; "
                "folder discovery is not a package-selection policy"
            )
        return []
    values = _value(document, keys[0])
    if not isinstance(values, list):
        raise ValueError("solution data XDR Detections must be an array")

    references: list[Path] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("solution data contains an invalid XDR Detection reference")
        normalized = value.replace("\\", "/")
        parts = normalized.split("/")
        if (
            not normalized.startswith("XDR Detections/")
            or any(part in {"", ".", ".."} for part in parts)
            or normalized.startswith("/")
            or re.match(r"^[A-Za-z]:", normalized)
        ):
            raise ValueError("XDR references must be under XDR Detections, never Logs or Reports")
        candidate = content_path(solution, normalized)
        if not candidate.is_file():
            raise ValueError(f"referenced XDR Detection does not exist: {candidate}")
        resolved = candidate.resolve()
        if not resolved.is_relative_to(solution.resolve()) or candidate.is_symlink():
            raise ValueError(f"XDR Detection reference resolves outside the solution: {value!r}")
        key = resolved.as_posix().casefold()
        if key in seen:
            raise ValueError(f"duplicate XDR Detection reference: {value!r}")
        seen.add(key)
        references.append(resolved)
    return references


def _verify_package_selection(
    solution: Path,
    selection_plan: dict[str, Any],
    template: dict[str, Any],
    zip_path: Path,
) -> dict[str, Any]:
    from solution_manager.packaging.packaging_selection import _partial_coverage_allowed

    plan_sha = selection_plan.get("planSha256")
    if not isinstance(plan_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", plan_sha):
        raise ValueError("package selection evidence has no valid plan SHA-256")
    expected = selection_plan.get("selection") or {}
    summary = selection_plan.get("summary") or {}
    if summary.get("outcome") == "partial" and not _partial_coverage_allowed(summary):
        raise ValueError(
            "partial package selection does not meet the strict over-50% "
            "validated migrated-detection coverage policy"
        )
    if summary.get("outcome") == "blocked":
        raise ValueError("blocked package selection cannot be packaged")
    data = _read_json(_solution_data_file(solution / "Data"))
    current = {
        "analyticRules": _value(data, "Analytic Rules") or _value(data, "Analytics Rules") or [],
        "xdrDetections": _value(data, "XDR Detections") or _value(data, "Custom Detections") or [],
    }
    normalized_expected = {
        "analyticRules": [str(value).replace("\\", "/") for value in expected.get("analyticRules", [])],
        "xdrDetections": [str(value).replace("\\", "/") for value in expected.get("xdrDetections", [])],
    }
    if current != normalized_expected:
        raise RuntimeError("solution-data selections differ from the applied package selection plan")

    def resources(document: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        found: list[tuple[dict[str, Any], dict[str, Any]]] = []

        def visit(template: Any, inherited_variables: dict[str, Any] | None = None) -> None:
            if not isinstance(template, dict):
                return
            variables = dict(inherited_variables or {})
            template_variables = template.get("variables")
            if isinstance(template_variables, dict):
                variables.update(template_variables)
            entries = template.get("resources")
            if isinstance(entries, dict):
                entries = [
                    ({**entry, "name": entry.get("name", name)} if isinstance(entry, dict) else entry)
                    for name, entry in entries.items()
                ]
            if isinstance(entries, list):
                for resource in entries:
                    if not isinstance(resource, dict):
                        continue
                    found.append((resource, variables))
                    properties = resource.get("properties")
                    if isinstance(properties, dict):
                        visit(properties.get("template"), variables)
                        visit(properties.get("mainTemplate"), variables)
            visit(template.get("template"), variables)
            visit(template.get("mainTemplate"), variables)

        visit(document)
        return found

    def exact_token(value: Any, identifier: str) -> bool:
        if not isinstance(value, str):
            return False
        return re.search(
            rf"(?<![0-9a-f]){re.escape(identifier)}(?![0-9a-f])",
            value.casefold(),
        ) is not None

    guid_token = re.compile(
        r"(?i)(?<![0-9a-f])[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}(?![0-9a-f])"
    )
    variable_reference = re.compile(
        r"variables\(\s*['\"]([^'\"]+)['\"]\s*\)(?:\.([A-Za-z_][A-Za-z0-9_]*))?"
    )
    deployment_reference = re.compile(
        r"resourceId\(\s*['\"]Microsoft\.Resources/deployments['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)",
        re.IGNORECASE,
    )

    def variable_value(variables: dict[str, Any], name: str, field: str | None) -> Any:
        value = next(
            (item for key, item in variables.items() if key.casefold() == name.casefold()),
            None,
        )
        if field is None or not isinstance(value, dict):
            return value
        return next(
            (item for key, item in value.items() if key.casefold() == field.casefold()),
            None,
        )

    def resource_ids(value: Any, variables: dict[str, Any], seen: frozenset[str] = frozenset()) -> set[str]:
        if isinstance(value, dict):
            return set().union(*(resource_ids(item, variables, seen) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(resource_ids(item, variables, seen) for item in value))
        if not isinstance(value, str):
            return set()
        identifiers = {match.group(0).casefold() for match in guid_token.finditer(value)}
        for match in variable_reference.finditer(value):
            reference = f"{match.group(1)}.{match.group(2) or ''}".casefold()
            if reference in seen:
                continue
            resolved = variable_value(variables, match.group(1), match.group(2))
            identifiers.update(
                resource_ids(resolved, variables, seen | {reference})
            )
        return identifiers

    def resource_matches_id(
        resource: dict[str, Any],
        variables: dict[str, Any],
        identifier: str,
    ) -> bool:
        properties = resource.get("properties")
        if not isinstance(properties, dict):
            properties = {}
        identity_fields = [
            resource.get("name"),
            properties.get("id"),
            properties.get("alertRuleTemplateName"),
            properties.get("contentId"),
        ]
        if guid_token.fullmatch(identifier):
            return any(
                identifier.casefold() in resource_ids(value, variables)
                for value in identity_fields
            )
        return any(exact_token(value, identifier.casefold()) for value in identity_fields)

    def custom_detection_child(
        document: dict[str, Any],
        packaged_id: str,
    ) -> bool:
        return any(
            str(child.get("type") or "").casefold()
            == "microsoft.security/detectionrules"
            and str(child.get("name") or "").casefold() == "detectionrule"
            and exact_token(
                (
                    child.get("properties", {}).get("id")
                    if isinstance(child.get("properties"), dict)
                    else None
                ),
                packaged_id,
            )
            for child, _ in resources(document)
        )

    def verify_template(document: dict[str, Any], label: str) -> None:
        tree = resources(document)
        for item in selection_plan.get("analyticRules", []):
            identifier = str(item.get("id") or "").casefold()
            if not identifier:
                raise ValueError("package selection inventory contains an Analytic Rule without an ID")
            matching = [
                resource for resource, variables in tree
                if str(resource.get("type") or "").casefold() in {
                    "microsoft.operationalinsights/workspaces/providers/alertrules",
                    "microsoft.securityinsights/alertruletemplates",
                }
                and resource_matches_id(resource, variables, identifier)
            ]
            analytic_content_templates = [
                resource for resource, variables in tree
                if str(resource.get("type") or "").casefold()
                == "microsoft.operationalinsights/workspaces/providers/contenttemplates"
                and isinstance(resource.get("properties"), dict)
                and str(resource["properties"].get("contentKind") or "").casefold()
                == "analyticsrule"
                and resource_matches_id(resource, variables, identifier)
            ]
            expected_count = 1 if item.get("included") else 0
            if (
                len(matching) != expected_count
                or len(analytic_content_templates) != expected_count
            ):
                raise RuntimeError(
                    f"{label} must contain exactly {expected_count} matching Analytic Rule "
                    f"resources and content templates for {item.get('path')}; found "
                    f"{len(matching)} resource(s), {len(analytic_content_templates)} content template(s)"
                )
        for item in selection_plan.get("xdrDetections", []):
            source_id = str(item.get("sourceId") or "")
            detection_id = str(item.get("id") or "")
            if not detection_id:
                raise ValueError("package selection inventory contains a Custom Detection without an ID")
            packaged_id = (
                f"xdr-{source_id}"
                if re.fullmatch(
                    r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}",
                    source_id,
                )
                else detection_id
            ).casefold()
            installation_resources = []
            for resource, _ in tree:
                resource_type = str(resource.get("type") or "").casefold()
                properties = resource.get("properties") or {}
                if (
                    resource_type == "microsoft.resources/deployments"
                    and isinstance(properties, dict)
                    and isinstance(properties.get("template"), dict)
                    and custom_detection_child(properties["template"], packaged_id)
                ):
                    installation_resources.append(resource)
            install_names = {
                resource["name"]
                for resource in installation_resources
                if isinstance(resource.get("name"), str)
            }
            registration_count = 0
            for resource, _ in tree:
                resource_type = str(resource.get("type") or "").casefold()
                properties = resource.get("properties") or {}
                if (
                    resource_type == "microsoft.operationalinsights/workspaces/providers/contenttemplates"
                    and str(properties.get("contentKind") or "").casefold() == "customdetection"
                    and exact_token(properties.get("contentId"), packaged_id)
                    and isinstance(properties.get("mainTemplate"), dict)
                    and custom_detection_child(properties["mainTemplate"], packaged_id)
                ):
                    dependencies = resource.get("dependsOn") or []
                    if isinstance(dependencies, str):
                        dependencies = [dependencies]
                    dependency_names = [
                        name.casefold()
                        for dependency in dependencies
                        if isinstance(dependency, str)
                        for name in deployment_reference.findall(dependency)
                    ]
                    linked_installations = [
                        name for name in dependency_names if name in {
                            install_name.casefold() for install_name in install_names
                        }
                    ]
                    if len(linked_installations) == 1:
                        registration_count += 1
            expected_count = 1 if item.get("included") else 0
            if len(installation_resources) != expected_count or registration_count != expected_count:
                raise RuntimeError(
                    f"{label} must contain exactly {expected_count} Custom Detection installations "
                    f"and registrations for {item.get('path')}; found "
                    f"{len(installation_resources)} installation(s), {registration_count} registration(s)"
                )
        if not normalized_expected["xdrDetections"]:
            parameters = document.get("parameters") or {}
            if "DeployCustomDetection" in parameters:
                raise RuntimeError(
                    f"{label} emits Custom Detection controls for an explicitly empty XDR selection"
                )

    verify_template(template, "mainTemplate.json")
    try:
        with zipfile.ZipFile(zip_path) as archive:
            matches = [
                name for name in archive.namelist()
                if Path(name).name.casefold() == "maintemplate.json"
            ]
            if len(matches) != 1:
                raise RuntimeError("package ZIP must contain exactly one mainTemplate.json")
            embedded = json.loads(archive.read(matches[0]))
            excluded_references = [
                ("Analytic Rules", item)
                for item in selection_plan.get("analyticRules", [])
                if not item.get("included")
            ] + [
                ("XDR Detections", item)
                for item in selection_plan.get("xdrDetections", [])
                if not item.get("included")
            ]
            text_entries = []
            for member in archive.namelist():
                normalized_member = member.replace("\\", "/")
                parts = [part for part in normalized_member.split("/") if part]
                for family, item in excluded_references:
                    path_parts = str(item.get("path") or "").replace("\\", "/").split("/")
                    for index, part in enumerate(parts):
                        if (
                            part.casefold() == family.casefold()
                            and [value.casefold() for value in parts[index:]]
                            == [value.casefold() for value in path_parts]
                        ):
                            raise RuntimeError(
                                f"package ZIP includes explicitly excluded content: {item.get('path')}"
                            )
                if Path(normalized_member).suffix.casefold() in {".json", ".yaml", ".yml", ".txt"}:
                    text_entries.append((member, archive.read(member).decode("utf-8", errors="replace")))
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot verify the package selection inside ZIP: {exc}") from exc
    if not isinstance(embedded, dict):
        raise RuntimeError("package ZIP mainTemplate.json must contain an object")
    verify_template(embedded, "package ZIP mainTemplate.json")
    for family, item in excluded_references:
        identifiers = []
        if family == "Analytic Rules":
            identifiers.extend((str(item.get("id") or ""), str(item.get("path") or "")))
        else:
            source_id = str(item.get("sourceId") or "")
            detection_id = str(item.get("id") or "")
            identifiers.append(
                f"xdr-{source_id}"
                if re.fullmatch(
                    r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}",
                    source_id,
                )
                else detection_id
            )
            identifiers.append(detection_id)
            identifiers.append(str(item.get("path") or ""))
        for member, content in text_entries:
            searchable = content.replace("\\", "/")
            if any(exact_token(searchable, identifier.casefold()) for identifier in identifiers if identifier):
                raise RuntimeError(
                    f"package ZIP contains a reference to explicitly excluded content "
                    f"{item.get('path')} in {member}"
                )
    return {
        "planSha256": plan_sha,
        "analyticRuleIncluded": len(normalized_expected["analyticRules"]),
        "xdrDetectionIncluded": len(normalized_expected["xdrDetections"]),
        "outcome": summary.get("outcome"),
        "coverageNumerator": summary.get("coverageNumerator"),
        "coverageDenominator": summary.get("coverageDenominator"),
        "partialPublicationAllowed": summary.get("partialPublicationAllowed"),
        "mainTemplateVerified": True,
        "zipVerified": True,
    }


def _verify_workbook_package(
    solution: Path, files: list[Path], template: dict[str, Any], zip_path: Path,
) -> dict[str, Any]:
    """Verify the full candidate install/registration projection, not provider acceptance."""
    from copy import deepcopy
    from solution_manager.migration.workbooks import _content_release

    def arm_copy(value: Any) -> Any:
        if isinstance(value, str):
            return "[" + value if value.startswith("[") else value
        if isinstance(value, dict):
            return {key: arm_copy(item) for key, item in value.items()}
        if isinstance(value, list):
            return [arm_copy(item) for item in value]
        return value

    resources = template.get("resources") or []
    if not isinstance(resources, list):
        raise RuntimeError("V3.1 workbook package resources must be an array")
    installs = [row for row in resources if
                row.get("type") == "Microsoft.Resources/deployments" and
                row.get("name", "").startswith("DefenderWorkbook-")]
    registrations = [row for row in resources if
                     row.get("properties", {}).get("contentKind") == "DefenderWorkbook"]
    packages = [row for row in resources if row.get("type") ==
                "Microsoft.OperationalInsights/workspaces/providers/contentPackages"]
    if len(installs) != len(files) or len(registrations) != len(files):
        raise RuntimeError("Defender workbook install/registration count differs from selection")
    if not files:
        return {"count": 0, "contractSupport": "notApplicable"}
    if len(packages) != 1:
        raise RuntimeError("Defender workbook packaging requires exactly one contentPackages resource")
    variables = template.get("variables") or {}
    package_id = variables.get("solutionId")
    version = variables.get("_solutionVersion")
    validate_v31_target_version(version)
    if not isinstance(package_id, str) or not package_id or package_id.startswith("["):
        raise RuntimeError("Defender workbook package identity must be resolved")
    expected_criteria = []
    identities = []
    for path in files:
        authored = _read_json(path)
        metadata = authored["xdrMetadata"]
        content_id = metadata["contentId"]
        instance_id = metadata["instanceId"]
        if _content_release(metadata["version"]) is None:
            raise ValueError("Defender workbook content version must be >=3.1.0 and <4.0.0")
        actual_solution_name = next(
            (entry.name for entry in solution.parent.iterdir() if entry.name.lower() == solution.name.lower()),
            solution.name,
        )
        deployment_name = "DefenderWorkbook-" + hashlib.sha256(
            f"{actual_solution_name}/{content_id}".encode("utf-8")
        ).hexdigest()[:32]
        install_rows = [row for row in installs if row.get("name") == deployment_name]
        registration_rows = [row for row in registrations if row.get("properties", {}).get("contentId") == content_id]
        if len(install_rows) != 1 or len(registration_rows) != 1:
            raise RuntimeError("Defender workbook identities are missing or duplicated")
        install, registration = install_rows[0], registration_rows[0]
        function_records = authored["contentProvenance"].get("requiredWorkspaceFunctions", [])
        from solution_manager.authoring.workbook_functions import validate_functions, function_definition, function_parameters
        from solution_manager.migration.workbooks import _root
        if function_records:
            validate_functions(_root(solution), function_records)
        parser_dependencies = []
        for record in function_records:
            saved = [resource for resource in resources if
                     resource.get("type", "").lower() == "microsoft.operationalinsights/workspaces/savedsearches"
                     and resource.get("properties", {}).get("functionAlias") == record["functionAlias"]]
            if len(saved) != 1:
                raise RuntimeError("Required workspace function must have exactly one emitted savedSearch")
            resource = saved[0]
            _, definition = function_definition(_root(solution), record["sourcePath"])
            emitted_query = resource.get("properties", {}).get("query")
            source_query = definition["FunctionQuery"]
            if ("condition" in resource or "copy" in resource
                    or not isinstance(emitted_query, str)
                    or emitted_query not in (source_query, f"{source_query}\n")
                    or resource.get("properties", {}).get("functionParameters", "") != function_parameters(definition)):
                raise RuntimeError("Required workspace function must be unconditional and match current source")
            name = resource.get("name")
            if not isinstance(name, str) or not name:
                raise RuntimeError("Required savedSearch has no exact resource identity")
            dependency = None
            parser_match = re.fullmatch(
                r"\[variables\(\s*'(parserObject([1-9][0-9]*))'\s*\)\.(?:_?parserName\2|_parserId\2)\]",
                name,
            )
            if parser_match:
                parser_object_name, parser_index = parser_match.groups()
                parser_object = variables.get(parser_object_name) if isinstance(variables, dict) else None
                if not isinstance(parser_object, dict):
                    raise RuntimeError("Invalid required savedSearch ARM identity")
                parser_id = parser_object.get(f"_parserId{parser_index}")
                if not isinstance(parser_id, str) or not parser_id.strip():
                    raise RuntimeError("Invalid required savedSearch ARM identity")
                dependency = f"[variables('{parser_object_name}')._parserId{parser_index}]"
            elif re.match(r"\A\[variables\(\s*'parserObject", name):
                raise RuntimeError("Invalid required savedSearch ARM identity")
            elif isinstance(variables, dict):
                for var_name, var_value in variables.items():
                    idx_match = re.fullmatch(r"parserObject([1-9][0-9]*)", str(var_name))
                    if idx_match and isinstance(var_value, dict):
                        idx = idx_match.group(1)
                        parser_id = var_value.get(f"_parserId{idx}")
                        if (
                            isinstance(parser_id, str)
                            and parser_id.strip()
                            and name in (var_value.get(f"_parserName{idx}"), var_value.get(f"parserName{idx}"))
                        ):
                            dependency = f"[variables('{var_name}')._parserId{idx}]"
                            break
            if dependency is None:
                if name.startswith("["):
                    if name.startswith("[[") or not name.endswith("]"):
                        raise RuntimeError("Invalid required savedSearch ARM identity")
                    argument = name[1:-1]
                else:
                    if len(name.split("/")) != 2 or not all(name.split("/")):
                        raise RuntimeError("Required savedSearch identity must include workspace and resource name")
                    argument = "'" + name.replace("'", "''") + "'"
                dependency = f"[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', {argument})]"
            if dependency not in parser_dependencies:
                parser_dependencies.append(dependency)
        expected_install_dependencies = [
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]",
            *parser_dependencies,
        ]
        if install.get("dependsOn") != expected_install_dependencies:
            raise RuntimeError("Workbook installation must depend on exact mandatory workspace functions")
        inner = install.get("properties", {}).get("template") or {}
        quartet = {"packageId": package_id, "packageVersion": version,
                   "contentId": content_id, "contentVersion": version}
        notebook = deepcopy(authored)
        notebook.pop("xdrMetadata")
        notebook["contentProvenance"] = quartet
        expected_resource = arm_copy({
            "import": "MicrosoftSecurity", "type": "Microsoft.Security/workbooks@2026-06-01-preview",
            "properties": {"id": instance_id, "name": metadata["displayName"], "content": notebook},
        })
        if (
            install.get("apiVersion") != "2025-04-01"
            or install.get("condition") != "[parameters('DeployDefenderWorkbook')]"
            or install.get("properties", {}).get("expressionEvaluationOptions", {}).get("scope") != "inner"
            or inner.get("languageVersion") != "2.0"
            or inner.get("imports") != {"MicrosoftSecurity": {"provider": "MicrosoftSecurity", "version": "1.0.0"}}
            or inner.get("resources") != {"workbook": expected_resource}
        ):
            raise RuntimeError("Defender workbook installation template/provenance projection is incorrect")
        properties = registration.get("properties") or {}
        full_provenance = {**quartet, **{
            key: authored["contentProvenance"][key]
            for key in ("requiredWorkloads", "requiredDataConnectors")
        }, "requiredWorkspaceFunctions": function_records}
        expected_name = (
            "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',"
            f"concat(parameters('workspace'),'-dwb-',uniqueString('{content_id}')))]"
        )
        if (
            registration.get("type") != "Microsoft.OperationalInsights/workspaces/providers/contentTemplates"
            or registration.get("apiVersion") != "2023-04-01-preview"
            or registration.get("condition") != "[parameters('DeployDefenderWorkbook')]"
            or registration.get("name") != expected_name
            or properties.get("mainTemplate") != inner
            or properties.get("contentProvenance") != arm_copy(full_provenance)
            or any(properties.get(key) != value for key, value in
                   {"contentId": content_id, "version": version, "packageId": package_id,
                    "packageVersion": version, "contentKind": "DefenderWorkbook"}.items())
            or registration.get("dependsOn") != [
                f"[resourceId('Microsoft.Resources/deployments', '{deployment_name}')]",
                "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]",
            ]
        ):
            raise RuntimeError("Defender workbook registration/stored template/provenance is incorrect")
        expected_criteria.append({"kind": "DefenderWorkbook", "contentId": content_id, "version": version})
        identities.append({"contentId": content_id, "instanceId": instance_id,
                           "path": path.relative_to(solution).as_posix()})
    criteria = packages[0].get("properties", {}).get("dependencies", {}).get("criteria") or []
    if [row for row in criteria if row.get("kind") == "DefenderWorkbook"] != expected_criteria:
        raise RuntimeError("Defender workbook package dependency criteria differs from selection")
    with zipfile.ZipFile(zip_path) as archive:
        entries = [name for name in archive.namelist() if Path(name).name == "mainTemplate.json"]
        if len(entries) != 1 or archive.read(entries[0]) != (solution / "Package" / "mainTemplate.json").read_bytes():
            raise RuntimeError("Defender workbook ZIP template does not match the exact current package bytes")
    return {"count": len(files), "identities": identities, "contractSupport": "unverified"}


def package_solution_v3_1(
    solution: str | Path,
    *,
    version_bump: str,
    target_version: str | None = None,
    toolkit_root: str | Path | None = None,
    requested_version_bump: str | None = None,
    package_attempt_id: str | None = None,
    workflow_run_id: str | None = None,
    selection_plan: dict[str, Any] | None = None,
    arm_validation_method: str = "arm-ttk",
) -> dict[str, Any]:
    if arm_validation_method not in {"arm-ttk", "lab-deployment"}:
        raise ValueError("ARM validation method must be arm-ttk or lab-deployment")
    if version_bump not in {"none", "patch", "minor", "major"}:
        raise ValueError("version bump must be none, patch, minor, or major")
    if target_version is not None:
        validate_v31_target_version(target_version)
        if version_bump != "none":
            raise ValueError("target version cannot be combined with a version bump")

    root = Path(solution).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"solution folder does not exist: {root}")
    require_solution_conversion_scope(root)
    applied_selection = None
    if workflow_run_id is not None:
        from solution_manager.packaging.packaging_selection import verify_applied_package_selection

        applied_selection = verify_applied_package_selection(root, workflow_run_id)
        if selection_plan is not None and (
            not applied_selection
            or applied_selection["plan"].get("planSha256")
            != selection_plan.get("planSha256")
        ):
            raise ValueError("V3.1 packaging selection is missing, stale, or mismatched")
        if selection_plan is None and applied_selection is not None:
            raise ValueError(
                "an applied evidence-based selection must be passed explicitly to V3.1 packaging"
            )
    elif selection_plan is not None:
        raise ValueError("V3.1 evidence-based packaging selection requires a bound workflow run ID")
    repository = repository_root(root)
    selected_toolkit_root = _validate_v31_toolkit_root(
        toolkit_root if toolkit_root is not None else repository
    )
    data_directory = root / "Data"
    if not data_directory.is_dir():
        raise ValueError(f"solution data folder does not exist: {data_directory}")

    data_file = _solution_data_file(data_directory)
    before = _read_json(data_file)
    _validate_solution_package_inputs(root, before)
    validate_v31_effective_version(_value(before, "Version"), version_bump, target_version)
    reports = report_directory(root, create=True)
    xdr_files = _xdr_references(root, before)
    from solution_manager.migration.workbooks import selected_workbook_files, validate_workbooks
    if _value(before, "XDR Workbooks") is None:
        if any((root / "XDR Workbooks").rglob("*.json")):
            raise ValueError("solution Data is missing an explicit XDR Workbooks array")
        workbook_files = []
    else:
        workbook_files = selected_workbook_files(root)
    if workbook_files:
        workbook_validation = validate_workbooks(root, selected_only=True)
        if workbook_validation["invalid"] or workbook_validation["valid"] != len(workbook_files):
            raise ValueError("selected Defender workbooks have unresolved structural or review blockers")
        from solution_manager.authoring.workbook_publication import publication_errors
        for workbook_file in workbook_files:
            blockers = publication_errors(root, _read_json(workbook_file))
            if blockers:
                raise ValueError("; ".join(blockers))
    script = (
        selected_toolkit_root
        / "Tools"
        / "Create-Azure-Sentinel-Solution"
        / "V3"
        / "createSolutionV3_1.ps1"
    )
    if not script.is_file():
        raise ValueError(f"V3.1 solution packager does not exist: {script}")
    pwsh = shutil.which("pwsh")
    if not pwsh:
        raise RuntimeError("PowerShell 7 is required to run the V3.1 solution packager.")

    command = [
        pwsh,
        "-NoProfile",
        "-File",
        str(script),
        "-SolutionDataFolderPath",
        str(data_directory),
        "-VersionMode",
        "local",
        "-ArmValidationMethod",
        arm_validation_method,
        "-VersionBump",
        version_bump,
    ]
    if target_version is not None:
        command.extend(["-TargetVersion", target_version])
    if toolkit_root is not None:
        command.extend(["-ToolkitRootPath", str(selected_toolkit_root)])
    input_before = package_input_identity(root)
    if applied_selection is not None:
        current_selection = verify_applied_package_selection(root, workflow_run_id)
        if (
            not current_selection
            or current_selection["plan"].get("planSha256")
            != selection_plan.get("planSha256")
        ):
            raise ValueError(
                "V3.1 package selection changed immediately before the package build"
            )
    package_attempt_id = package_attempt_id or str(uuid.uuid4())
    completed = subprocess.run(
        command,
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = "\n".join(
        value.strip() for value in (completed.stdout, completed.stderr) if value.strip()
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"V3.1 solution packaging failed with exit code {completed.returncode}: "
            f"{output[-4000:]}"
        )
    if "Starting Package Creation using V3.1 tool" not in output:
        raise RuntimeError("Packaging output did not confirm the V3.1 entry point.")
    warnings = [
        line for line in output.splitlines()
        if any(label in line for label in (
            "CUSTOMER USAGE ATTRIBUTION:", "V3.1 CONTENT SELECTION:",
        ))
    ]
    for warning in warnings:
        print(warning, file=sys.stderr)
    informational = [
        line for line in output.splitlines()
        if line.startswith((
            "INFORMATION: V3.1 TACTIC SELECTION:",
            "INFORMATION: V3.1 ID NORMALIZATION:",
        ))
    ]
    for message in informational:
        print(message, file=sys.stderr)
    tactic_projection = []
    identity_projection = []
    for line in output.splitlines():
        if line.startswith(TACTIC_PROJECTION_PREFIX):
            try:
                record = json.loads(line[len(TACTIC_PROJECTION_PREFIX):])
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid V3.1 tactic projection evidence: {exc}") from exc
            if (
                not isinstance(record, dict)
                or not isinstance(record.get("detectionId"), str)
                or not record["detectionId"]
                or any(
                    not isinstance(record.get(key), list)
                    or any(not isinstance(value, str) for value in record[key])
                    for key in ("authoredTactics", "packagedTactics", "omittedTactics")
                )
            ):
                raise RuntimeError("V3.1 tactic projection evidence has an invalid structure.")
            tactic_projection.append(record)
        elif line.startswith(IDENTITY_PROJECTION_PREFIX):
            try:
                record = json.loads(line[len(IDENTITY_PROJECTION_PREFIX):])
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid V3.1 identity projection evidence: {exc}") from exc
            if (
                not isinstance(record, dict)
                or not isinstance(record.get("inputId"), str)
                or not isinstance(record.get("packagedId"), str)
                or not isinstance(record.get("changed"), bool)
                or record.get("scope") != "package-projection-only"
            ):
                raise RuntimeError("V3.1 identity projection evidence has an invalid structure.")
            identity_projection.append(record)
    attribution_sources = [
        line for line in output.splitlines() if "CUSTOMER USAGE ATTRIBUTION SOURCE:" in line
    ]
    for source in attribution_sources:
        print(source, file=sys.stderr)

    after = _read_json(data_file)
    version = str(_value(after, "Version") or "").strip()
    if not version:
        raise ValueError(f"solution data does not declare a package version: {data_file}")
    if target_version is not None and version != target_version:
        raise RuntimeError(
            "V3.1 packager did not persist the explicitly selected target version: "
            f"{version!r} != {target_version!r}"
        )

    package = root / "Package"
    main_template = package / "mainTemplate.json"
    create_ui = package / "createUiDefinition.json"
    test_parameters = package / "testParameters.json"
    zip_path = package / f"{version}.zip"
    required = (main_template, create_ui, test_parameters, zip_path)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(
            "V3.1 packaging completed without required artifacts: " + ", ".join(missing)
        )
    template_document = _read_json(main_template)
    deployment_parameters = _deployment_parameters(
        template_document, _read_json(create_ui), _read_json(test_parameters),
        has_xdr=bool(xdr_files),
        has_workbooks=bool(workbook_files),
        contract_path=(
            selected_toolkit_root
            / "Tools" / "Create-Azure-Sentinel-Solution" / "common"
            / "contentDeploymentParameters.json"
        ),
    )
    try:
        with zipfile.ZipFile(zip_path) as archive:
            names = {Path(name).name for name in archive.namelist()}
            if any(
                part.lower() in {"logs", "reports", "evidence"}
                for name in archive.namelist()
                for part in name.replace("\\", "/").split("/")
            ):
                raise RuntimeError("generated package ZIP must not contain Logs, Reports or Evidence")
            if any(
                part.lower() == ".env" or part.lower().startswith(".env.")
                for name in archive.namelist()
                for part in name.replace("\\", "/").split("/")
            ):
                raise RuntimeError(
                    "generated package ZIP must not contain local .env configuration"
                )
    except (OSError, zipfile.BadZipFile) as exc:
        raise RuntimeError(f"generated package ZIP is invalid: {zip_path}: {exc}") from exc
    missing_entries = {"mainTemplate.json", "createUiDefinition.json"} - names
    if missing_entries:
        raise RuntimeError(
            "generated package ZIP is missing: " + ", ".join(sorted(missing_entries))
        )
    selection_verification = (
        _verify_package_selection(root, selection_plan, template_document, zip_path)
        if selection_plan is not None else None
    )
    workbook_verification = _verify_workbook_package(root, workbook_files, template_document, zip_path)

    artifact_paths = {
        "mainTemplate": main_template,
        "createUiDefinition": create_ui,
        "testParameters": test_parameters,
        "zip": zip_path,
    }
    artifact_hashes = _package_artifact_hashes(artifact_paths)
    input_after = package_input_identity(root)
    input_after_files = package_input_file_hashes(root)
    input_after_manifest_identity = hashlib.sha256(
        json.dumps(
            [
                {"path": name, "sha256": digest}
                for name, digest in input_after_files.items()
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    if (
        input_after_manifest_identity != input_after["sha256"]
        or len(input_after_files) != input_after["fileCount"]
    ):
        raise RuntimeError("package inputs changed while the V3.1 receipt manifest was captured")
    reports = report_directory(root, create=True)
    report_path = reports / "packaging.v3_1.json"
    if report_path.exists():
        suffix = package_attempt_id or uuid.uuid4().hex
        report_path = reports / f"packaging.v3_1.{suffix}.json"
    selection_outcome = (
        "partial-package-validated"
        if selection_plan is not None
        and selection_plan.get("summary", {}).get("outcome") == "partial"
        else "package-validated"
        if selection_plan is not None else None
    )
    result = {
        "status": "passed",
        "armValidationMethod": arm_validation_method,
        "packageLifecycleStatus": (
            "candidate-generated" if arm_validation_method == "lab-deployment" or workbook_files else "accepted"
        ),
        "packageAccepted": arm_validation_method == "arm-ttk" and not workbook_files,
        "packager": PACKAGER_NAME,
        "warnings": warnings,
        "informational": informational,
        "tacticProjection": tactic_projection,
        "identityProjection": identity_projection,
        "attributionSources": attribution_sources,
        "solution": str(root),
        "toolkitRoot": str(selected_toolkit_root),
        "packagerScript": str(script),
        "version": version,
        "versionBump": version_bump,
        "requestedVersionBump": requested_version_bump or version_bump,
        "effectiveVersionBump": version_bump,
        "requestedTargetVersion": target_version,
        "effectiveTargetVersion": target_version,
        "packageAttemptId": package_attempt_id,
        "workflowRunId": workflow_run_id,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "packageInputs": {
            "before": input_before,
            "after": {
                **input_after,
                "files": input_after_files,
            },
        },
        "packageArtifactHashes": artifact_hashes,
        "packageArtifactsSha256": _canonical_digest(artifact_hashes),
        "solutionData": str(data_file),
        "xdrDetectionCount": len(xdr_files),
        "xdrWorkbookCount": len(workbook_files),
        "workbookVerification": workbook_verification,
        "defenderWorkbookContractSupport": "unverified" if workbook_files else "notApplicable",
        "deploymentParameters": deployment_parameters,
        "customDetectionRegistrationSupport": "unverified" if xdr_files else "notApplicable",
        "selectionOutcome": selection_outcome,
        "selectionPlanSha256": (
            selection_plan.get("planSha256") if selection_plan is not None else None
        ),
        "selectionPlanPath": (
            applied_selection["planPath"] if applied_selection is not None else None
        ),
        "selectionReceiptPath": (
            applied_selection["receiptPath"] if applied_selection is not None else None
        ),
        "selectionSummary": (
            selection_plan.get("summary") if selection_plan is not None else None
        ),
        "selectionVerification": selection_verification,
        "mainTemplate": str(main_template),
        "createUiDefinition": str(create_ui),
        "testParameters": str(test_parameters),
        "zip": str(zip_path),
        "packageReport": str(report_path),
        "workflowArtifacts": {
            "packager": PACKAGER_NAME,
            "packageReport": str(report_path),
            "mainTemplate": str(main_template),
            "createUiDefinition": str(create_ui),
            "testParameters": str(test_parameters),
            "zip": str(zip_path),
            **({
                "selectionPlan": applied_selection["planPath"],
                "selectionReceipt": applied_selection["receiptPath"],
                "selectionPlanSha256": selection_plan["planSha256"],
                "selectionOutcome": selection_outcome,
            } if applied_selection is not None and selection_plan is not None else {}),
        },
    }
    write_json_artifact(root, report_path, result)
    return result
