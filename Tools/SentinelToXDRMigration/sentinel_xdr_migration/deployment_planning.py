from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml

from .artifacts import (
    artifact_path,
    existing_artifact_path,
    report_directory,
    repository_root,
    resolve_artifact_reference,
    write_json_artifact,
)
from .content_paths import content_path
from .converter import (
    analytic_rule_files,
    build_xdr_document,
    load_config,
    validate_document,
    xdr_detection_files,
)
from .packaging import (
    DATA_EXCLUSIONS,
    _solution_data_file,
    package_input_identity,
    solution_data_version,
)
from .target_context import require_locked_target, workspace_identity

PLAN_SCHEMA_VERSION = "1.0.0"
PLAN_FILE_NAME = "deployment-scope-plan.json"
CONSENT_FILE_NAME = "deployment-planning-consent.json"
COMPONENTS = {
    "sentinelAlertRules",
    "xdrCustomDetections",
    "fullPackageAcceptance",
    "mockTelemetryIngestion",
    "fallbackDcr",
    "fallbackDce",
    "customTableCreate",
}
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GUID = re.compile(r"^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")
_CONTENT_FOLDERS = {
    "analyticRules": ("Analytic Rules", "Analytics Rules"),
    "playbooks": ("Playbooks",),
    "workbooks": ("Workbooks",),
    "dataConnectors": ("Data Connectors",),
}
_OTHER_CONTENT_FOLDERS = (
    "Hunting Queries",
    "Parsers",
    "Watchlists",
    "Notebooks",
    "Functions",
    "Exploration Queries",
    "Summary rules",
)
_SKIP_PARTS = {"logs", "reports", "evidence", ".git", "package"}
_MANIFEST_CATEGORIES = {
    "analytic rules": "analyticRules",
    "analytics rules": "analyticRules",
    "playbooks": "playbooks",
    "workbooks": "workbooks",
    "data connectors": "dataConnectors",
    "hunting queries": "other",
    "parsers": "other",
    "watchlists": "other",
    "notebooks": "other",
    "functions": "other",
    "exploration queries": "other",
    "summary rules": "other",
}


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _file_inventory(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if any(part.casefold() in _SKIP_PARTS for part in relative.parts):
            continue
        if any(part.casefold() == ".env" or part.casefold().startswith(".env.") for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"deployment planning does not follow symlink content: {relative}")
        if not path.is_file():
            continue
        content_path(root, relative)
        entries.append(
            {
                "path": relative.as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return entries


def _count_files(root: Path, folder: str, suffixes: set[str]) -> int:
    directory = root / folder
    if not directory.exists():
        return 0
    if directory.is_symlink():
        raise ValueError(f"deployment planning does not follow symlink content: {directory}")
    count = 0
    for path in directory.rglob("*"):
        if any(part.casefold() in _SKIP_PARTS for part in path.relative_to(root).parts):
            continue
        if path.is_symlink():
            raise ValueError(f"deployment planning does not follow symlink content: {path}")
        if path.is_file() and path.suffix.casefold() in suffixes:
            count += 1
    return count


def _resolve_manifest_reference(root: Path, reference: str) -> Path:
    normalized = reference.replace("\\", "/")
    candidate = Path(normalized)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("solution manifest references must be relative and contained")
    repository = repository_root(root).resolve()
    if candidate.parts and candidate.parts[0].casefold() == "solutions":
        path = repository.joinpath(*candidate.parts)
    else:
        path = content_path(root, normalized)
    resolved = path.resolve()
    if not resolved.is_relative_to(repository):
        raise ValueError("solution manifest reference escapes the repository")
    current = resolved
    while current != repository and repository in current.parents:
        if current.is_symlink():
            raise ValueError("solution manifest reference traverses a symlink")
        current = current.parent
    return resolved


def _playbook_workflows(path: Path) -> list[str]:
    try:
        document = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    identities: set[str] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            resources = node.get("resources")
            if isinstance(resources, list):
                for resource in resources:
                    if not isinstance(resource, dict):
                        continue
                    resource_type = str(resource.get("type") or "").split("@", 1)[0]
                    if resource_type.casefold() == "microsoft.logic/workflows":
                        name = resource.get("name")
                        if isinstance(name, str) and name.strip():
                            identities.add(name.strip().casefold())
                    visit(resource)
            elif isinstance(resources, dict):
                for key, resource in resources.items():
                    if not isinstance(resource, dict):
                        continue
                    resource_type = str(resource.get("type") or key).split("@", 1)[0]
                    if resource_type.casefold() == "microsoft.logic/workflows":
                        name = resource.get("name")
                        if isinstance(name, str) and name.strip():
                            identities.add(name.strip().casefold())
                    visit(resource)
            properties = node.get("properties")
            if isinstance(properties, dict) and isinstance(properties.get("template"), dict):
                visit(properties["template"])
            definition = node.get("definition")
            if isinstance(definition, dict) and (
                isinstance(definition.get("triggers"), dict)
                or isinstance(definition.get("actions"), dict)
            ):
                name = (node.get("metadata") or {}).get("title") or path.stem
                identities.add(str(name).casefold())
            for key, value in node.items():
                if key not in {"resources", "properties", "definition"}:
                    visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(document)
    return sorted(identities)


def _manifest_content_inventory(root: Path) -> dict[str, Any]:
    data_directory = root / "Data"
    if not data_directory.is_dir():
        return {
            "status": "unavailable",
            "manifestPath": None,
            "contentCounts": {},
            "manifestReferenceCounts": {},
            "playbookTemplateFiles": 0,
            "unlistedFiles": {},
            "missingOrInvalidReferences": [],
        }
    try:
        manifest_path = _solution_data_file(data_directory)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if not isinstance(manifest, dict):
            raise ValueError("solution data manifest must contain a JSON object")
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "status": "invalid",
            "manifestPath": None,
            "contentCounts": {},
            "manifestReferenceCounts": {},
            "playbookTemplateFiles": 0,
            "unlistedFiles": {},
            "missingOrInvalidReferences": [str(exc)],
        }

    references: dict[str, dict[str, Path]] = {}
    missing: list[str] = []
    for manifest_key, category in _MANIFEST_CATEGORIES.items():
        value = next(
            (
                items for key, items in manifest.items()
                if isinstance(key, str) and key.strip().casefold() == manifest_key
            ),
            [],
        )
        if not isinstance(value, list):
            continue
        category_refs = references.setdefault(category, {})
        for reference in value:
            if not isinstance(reference, str) or not reference.strip():
                missing.append(f"{manifest_key}: invalid empty/non-string reference")
                continue
            try:
                path = _resolve_manifest_reference(root, reference)
                if not path.is_file():
                    raise ValueError("referenced file is missing")
                category_refs[path.as_posix()] = path
            except (OSError, RuntimeError, ValueError) as exc:
                missing.append(f"{reference}: {exc}")

    playbook_files = references.get("playbooks", {})
    workflow_items: set[tuple[str, str]] = set()
    workflow_references: set[tuple[str, str]] = set()
    for path_text, path in playbook_files.items():
        for workflow_name in _playbook_workflows(path):
            workflow_items.add((path_text, workflow_name))
            workflow_references.add((path_text, workflow_name))

    folder_by_category = {
        "analyticRules": ("Analytic Rules", "Analytics Rules"),
        "playbooks": ("Playbooks",),
        "workbooks": ("Workbooks",),
        "dataConnectors": ("Data Connectors",),
        "other": _OTHER_CONTENT_FOLDERS,
    }
    folder_file_counts: dict[str, int] = {}
    unlisted_files: dict[str, list[str]] = {}
    for category, folders in folder_by_category.items():
        listed = set(references.get(category, {}))
        discovered: set[str] = set()
        for folder in folders:
            directory = root / folder
            if not directory.is_dir():
                continue
            for path in directory.rglob("*"):
                if any(part.casefold() in _SKIP_PARTS for part in path.relative_to(root).parts):
                    continue
                if path.is_symlink():
                    raise ValueError(f"deployment planning does not follow symlink content: {path}")
                if path.is_file() and path.suffix.casefold() in {".yaml", ".yml", ".json"}:
                    discovered.add(path.resolve().as_posix())
        folder_file_counts[category] = len(discovered)
        unlisted_files[category] = sorted(discovered - listed)

    manifest_counts = {
        category: len(items)
        for category, items in references.items()
    }
    content_counts = {
        "analyticRules": len(references.get("analyticRules", {})),
        "playbooks": len(workflow_items),
        "workbooks": len(references.get("workbooks", {})),
        "dataConnectors": len(references.get("dataConnectors", {})),
        "other": len(references.get("other", {})),
    }
    return {
        "status": "ready" if not missing else "partial",
        "manifestPath": manifest_path.relative_to(repository_root(root)).as_posix(),
        "contentCounts": content_counts,
        "manifestReferenceCounts": manifest_counts,
        "playbookTemplateFiles": len(playbook_files),
        "configuredPlaybookTemplateCount": len(playbook_files),
        "playbookWorkflows": [
            {"path": path_text, "name": workflow_name}
            for path_text, workflow_name in sorted(workflow_references)
        ],
        "uniquePlaybookWorkflowCount": len(workflow_items),
        "folderFileCounts": folder_file_counts,
        "unlistedFiles": unlisted_files,
        "missingOrInvalidReferences": missing,
    }


def _source_inventory(root: Path) -> dict[str, Any]:
    file_counts: dict[str, int] = {}
    for key, folders in _CONTENT_FOLDERS.items():
        file_counts[key] = sum(
            _count_files(root, folder, {".yaml", ".yml", ".json"})
            for folder in folders
        )
    file_counts["other"] = sum(
        _count_files(root, folder, {".yaml", ".yml", ".json"})
        for folder in _OTHER_CONTENT_FOLDERS
    )
    rules, duplicate_ids = _source_records(root)
    content_inventory = _manifest_content_inventory(root)
    counts = {
        **content_inventory.get("contentCounts", {}),
        "analyticRules": len(rules),
        "analyticRuleFiles": file_counts.get("analyticRules", 0),
        "playbookFiles": file_counts.get("playbooks", 0),
        "playbooks": content_inventory.get("contentCounts", {}).get("playbooks"),
        "configuredPlaybookTemplateCount": content_inventory.get("configuredPlaybookTemplateCount", 0),
        "uniquePlaybookWorkflowCount": content_inventory.get("uniquePlaybookWorkflowCount", 0),
        "workbookFiles": file_counts.get("workbooks", 0),
        "workbooks": content_inventory.get("contentCounts", {}).get("workbooks"),
        "dataConnectorFiles": file_counts.get("dataConnectors", 0),
        "dataConnectors": content_inventory.get("contentCounts", {}).get("dataConnectors"),
        "otherFiles": file_counts.get("other", 0),
        "solutionDataManifests": int(content_inventory.get("manifestPath") is not None),
        "solutionMetadata": int((root / "SolutionMetadata.json").is_file()),
    }
    return {
        "counts": counts,
        "fileCounts": file_counts,
        "manifestContentInventory": content_inventory,
        "analyticRuleFileCount": len(analytic_rule_files(root)),
        "analyticRuleCount": len(rules),
        "duplicateSourceRuleCount": len(duplicate_ids),
        "sourceInventorySha256": _canonical_sha256(_file_inventory(root)),
    }


def _source_records(root: Path) -> tuple[dict[str, dict[str, Any]], set[str]]:
    rules: dict[str, dict[str, Any]] = {}
    duplicate_ids: set[str] = set()
    for path in analytic_rule_files(root):
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, yaml.YAMLError):
            continue
        if not isinstance(document, dict):
            continue
        rule_id = document.get("id")
        if not isinstance(rule_id, str) or not _GUID.fullmatch(rule_id):
            continue
        key = rule_id.casefold()
        if key in rules:
            duplicate_ids.add(key)
        rules[key] = {
            "id": rule_id,
            "path": path.relative_to(root).as_posix(),
            "document": document,
        }
    return rules, duplicate_ids


def _reviewed_current_drafts(
    root: Path,
    rules: Mapping[str, Mapping[str, Any]],
) -> tuple[list[str], list[str], dict[str, dict[str, Any]]]:
    reviewed: dict[str, str] = {}
    projections: dict[str, dict[str, Any]] = {}
    output_counts: dict[str, int] = {}
    output = root / "XDR Detections"
    if not output.is_dir():
        return [], [], {}
    config = load_config(output)
    configured_exclusions = config.get("excludedRuleIds") or {}
    if not isinstance(configured_exclusions, dict):
        raise ValueError("excludedRuleIds must contain an object of rule IDs and reasons")
    exclusions = {str(value).casefold() for value in configured_exclusions}
    for path in xdr_detection_files(output):
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
            if not isinstance(document, dict) or validate_document(document):
                continue
            provenance = (document.get("contentProvenance") or {}).get("source") or {}
            rule_id = provenance.get("id")
            if not isinstance(rule_id, str) or rule_id.casefold() not in rules:
                continue
            source = rules[rule_id.casefold()]
            if rule_id.casefold() in exclusions:
                continue
            source_query = str((source.get("document") or {}).get("query") or "")
            query_sha = hashlib.sha256(source_query.encode("utf-8")).hexdigest()
            conversion = (document.get("contentProvenance") or {}).get("conversion") or {}
            properties = document.get("properties") or {}
            query_text = str((properties.get("queryCondition") or {}).get("queryText") or "")
            review_scope = conversion.get("reviewScope") or {}
            source_document_sha = hashlib.sha256(
                yaml.safe_dump(
                    source["document"],
                    sort_keys=True,
                    allow_unicode=True,
                ).encode("utf-8")
            ).hexdigest()
            if (
                provenance.get("path") != source["path"]
                or provenance.get("querySha256") != query_sha
                or review_scope.get("sourceDocumentSha256") != source_document_sha
                or review_scope.get("targetQuerySha256")
                != hashlib.sha256(query_text.encode("utf-8")).hexdigest()
            ):
                continue
            if (
                conversion.get("status") == "converted"
                and conversion.get("reviewRequired") is False
                and not conversion.get("errors")
                and properties.get("status") == "disabled"
            ):
                key = rule_id.casefold()
                output_counts[key] = output_counts.get(key, 0) + 1
                try:
                    from .graph_readiness import graph_detection_payload_with_projection

                    _, projection = graph_detection_payload_with_projection(document)
                except (AttributeError, TypeError, ValueError):
                    continue
                reviewed[key] = source["id"]
                projections[source["id"]] = projection
        except (OSError, UnicodeError, ValueError, yaml.YAMLError, AttributeError):
            continue
    unique_reviewed = [
        source_id
        for key, source_id in reviewed.items()
        if output_counts.get(key) == 1
    ]
    unique_ids = {value.casefold() for value in unique_reviewed}
    return (
        sorted(unique_reviewed),
        sorted(exclusions),
        {
            source_id: projections[source_id]
            for source_id in unique_reviewed
            if source_id in projections
        },
    )


def _eligible_rule_ids(
    root: Path,
    rules: Mapping[str, Mapping[str, Any]],
    duplicate_ids: set[str],
    exclusions: set[str],
) -> tuple[list[str], list[str], dict[str, dict[str, Any]]]:
    output = root / "XDR Detections"
    config = load_config(output)
    excluded = {value.casefold() for value in exclusions}
    eligible: list[str] = []
    ineligible: list[str] = []
    projections: dict[str, dict[str, Any]] = {}
    for key, item in sorted(rules.items()):
        if key in duplicate_ids or key in excluded:
            ineligible.append(item["id"])
            continue
        try:
            candidate = build_xdr_document(
                root / item["path"],
                root,
                config,
            )
        except (OSError, UnicodeError, ValueError, yaml.YAMLError):
            ineligible.append(item["id"])
            continue
        conversion = (candidate.get("contentProvenance") or {}).get("conversion") or {}
        errors = conversion.get("errors")
        if (
            conversion.get("status") == "converted"
            and conversion.get("reviewRequired") is False
            and not errors
        ):
            try:
                from .graph_readiness import graph_detection_payload_with_projection

                _, projection = graph_detection_payload_with_projection(candidate)
            except (AttributeError, TypeError, ValueError):
                ineligible.append(item["id"])
                continue
            eligible.append(item["id"])
            projections[item["id"]] = projection
        else:
            ineligible.append(item["id"])
    return eligible, ineligible, projections


def _eligible_analytic_rule_ids(
    rules: Mapping[str, Mapping[str, Any]],
    duplicate_ids: set[str],
) -> tuple[list[str], list[str]]:
    eligible: list[str] = []
    ineligible: list[str] = []
    from .analytic_deployment import analytic_rule_payload

    for key, item in sorted(rules.items()):
        try:
            payload = analytic_rule_payload(item["document"])
            if (
                key in duplicate_ids
                or payload.get("kind") != "Scheduled"
                or (payload.get("properties") or {}).get("enabled") is not False
            ):
                raise ValueError("source AR is duplicate or not deployable as a disabled Scheduled rule")
        except (KeyError, TypeError, ValueError):
            ineligible.append(item["id"])
        else:
            eligible.append(item["id"])
    return eligible, ineligible


def _scan_package_resources(template: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: dict[tuple[str, str], dict[str, Any]] = {}
    imports: list[dict[str, Any]] = []

    def scan_document(node: Any) -> None:
        if isinstance(node, dict):
            import_record = node.get("imports")
            if isinstance(import_record, list):
                for item in import_record:
                    if isinstance(item, dict):
                        imports.append(
                            {
                                key: item[key]
                                for key in ("provider", "version", "name")
                                if isinstance(item.get(key), (str, int, float))
                            }
                        )
            if isinstance(node.get("resources"), (list, dict)):
                scan_collection(node["resources"])
            for key, value in node.items():
                if key != "resources":
                    scan_document(value)
        elif isinstance(node, list):
            for value in node:
                scan_document(value)

    def scan_resource(resource: Any, form: str) -> None:
        if not isinstance(resource, dict):
            return
        raw_type = resource.get("type")
        if isinstance(raw_type, str):
            resource_type, separator, embedded_version = raw_type.partition("@")
            if "/" in resource_type:
                api_version = resource.get("apiVersion")
                if not isinstance(api_version, str) or not api_version:
                    api_version = embedded_version if separator else ""
                key = (resource_type, api_version)
                item = records.setdefault(
                    key,
                    {
                        "type": resource_type,
                        "apiVersion": api_version,
                        "typeAtVersion": (
                            f"{resource_type}@{api_version}" if api_version else resource_type
                        ),
                        "count": 0,
                        "sourceForms": set(),
                        "extensionResource": False,
                        "scopeModel": "resource-scope-not-declared",
                    },
                )
                item["count"] += 1
                item["sourceForms"].add(form)
                if "scope" in resource or "scopeExpression" in resource:
                    item["extensionResource"] = True
                    item["scopeModel"] = "generic-arm-extension-resource-scope"
        nested = resource.get("resources")
        if isinstance(nested, list):
            for child in nested:
                scan_resource(child, "nested ARM resources array")
        elif isinstance(nested, dict):
            scan_collection(nested)
        properties = resource.get("properties")
        if isinstance(properties, dict) and isinstance(properties.get("template"), dict):
            scan_document(properties["template"])

    def scan_collection(resources: Any) -> None:
        if isinstance(resources, list):
            for resource in resources:
                scan_resource(resource, "ARM resources array")
        elif isinstance(resources, dict):
            if isinstance(resources.get("type"), str):
                scan_resource(resources, "ARM resource object")
            else:
                for key, resource in resources.items():
                    if isinstance(resource, dict):
                        if not resource.get("type") and "/" in str(key):
                            resource = {**resource, "type": key}
                        scan_resource(resource, "languageVersion 2 resource dictionary")

    scan_document(template)
    inventory = [
        {
            **record,
            "sourceForms": sorted(record["sourceForms"]),
        }
        for _, record in sorted(records.items())
    ]
    return inventory, imports


def _current_package(root: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    current_input_sha256 = None
    try:
        current_input_sha256 = package_input_identity(root).get("sha256")
    except (OSError, ValueError, TypeError):
        pass
    live_artifact_hashes: dict[str, str] = {}
    package_file_inventory: list[dict[str, str]] = []
    package_folder = root / "Package"
    if package_folder.is_dir() and not package_folder.is_symlink():
        for path in sorted(package_folder.rglob("*"), key=lambda item: item.as_posix()):
            if path.is_symlink():
                raise ValueError(f"deployment planning does not follow symlink content: {path}")
            if path.is_file():
                package_file_inventory.append(
                    {
                        "path": path.relative_to(package_folder).as_posix(),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
        for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip"):
            matches = (
                [package_folder / "mainTemplate.json"]
                if name == "mainTemplate"
                else [package_folder / "createUiDefinition.json"]
                if name == "createUiDefinition"
                else [package_folder / "testParameters.json"]
                if name == "testParameters"
                else sorted(package_folder.glob("*.zip"))
            )
            if len(matches) == 1 and matches[0].is_file() and not matches[0].is_symlink():
                live_artifact_hashes[name] = hashlib.sha256(matches[0].read_bytes()).hexdigest()
    packaging = state.get("packaging")
    successful = packaging.get("lastSuccessful") if isinstance(packaging, dict) else None
    if not isinstance(successful, dict) or successful.get("packageSucceeded") is not True:
        return {
            "status": "provisional",
            "version": None,
            "packageInputSha256": current_input_sha256,
            "packageArtifactHashes": live_artifact_hashes,
            "packageContentSha256": _canonical_sha256(package_file_inventory),
            "recordedPackageArtifactHashes": {},
            "deploymentParameters": {},
            "resourceInventory": [],
            "bicepExtensibilityImports": [],
            "whatIfSupport": "not-evaluated",
        }
    packaging_stage = (state.get("stages") or {}).get("packaging") or {}
    stage_artifacts = packaging_stage.get("artifacts") or {}
    package_hash = successful.get("packageArtifactsSha256")
    report_ref = successful.get("packageReport")
    if (
        packaging_stage.get("status") != "passed"
        or not isinstance(report_ref, str)
        or stage_artifacts.get("packageAttemptId") != successful.get("attemptId")
        or not isinstance(stage_artifacts.get("packageReport"), str)
    ):
        return {
            "status": "stale",
            "version": successful.get("version"),
            "packageInputSha256": current_input_sha256,
            "packageArtifactHashes": live_artifact_hashes,
            "packageContentSha256": _canonical_sha256(package_file_inventory),
            "recordedPackageArtifactHashes": {},
            "deploymentParameters": {},
            "resourceInventory": [],
            "bicepExtensibilityImports": [],
            "whatIfSupport": "not-evaluated",
        }
    try:
        report_path = resolve_artifact_reference(root, report_ref)
        selected_report_path = resolve_artifact_reference(
            root, stage_artifacts["packageReport"]
        )
        if selected_report_path.resolve() != report_path.resolve():
            return {
                "status": "stale",
                "version": successful.get("version"),
                "packageInputSha256": current_input_sha256,
                "packageArtifactHashes": live_artifact_hashes,
                "packageContentSha256": _canonical_sha256(package_file_inventory),
                "recordedPackageArtifactHashes": {},
                "deploymentParameters": {},
                "resourceInventory": [],
                "bicepExtensibilityImports": [],
                "whatIfSupport": "not-evaluated",
            }
        report_hash = hashlib.sha256(report_path.read_bytes()).hexdigest()
        report = json.loads(report_path.read_text(encoding="utf-8-sig"))
        if (
            not isinstance(report, dict)
            or report.get("packager") != "V3.1"
            or report.get("packageAttemptId") != successful.get("attemptId")
            or report.get("packageArtifactsSha256") != package_hash
            or report_hash != successful.get("packageReportSha256")
            or report_hash != stage_artifacts.get("packageReportSha256")
            or current_input_sha256 != successful.get("packageInputSha256")
            or current_input_sha256
            != ((report.get("packageInputs") or {}).get("after") or {}).get("sha256")
        ):
            return {
                "status": "stale",
                "version": report.get("version") if isinstance(report, dict) else None,
                "packageInputSha256": current_input_sha256,
                "packageArtifactHashes": live_artifact_hashes,
                "packageContentSha256": _canonical_sha256(package_file_inventory),
                "recordedPackageArtifactHashes": report.get("packageArtifactHashes", {}) if isinstance(report, dict) else {},
                "deploymentParameters": report.get("deploymentParameters", {}) if isinstance(report, dict) else {},
                "resourceInventory": [],
                "bicepExtensibilityImports": [],
                "whatIfSupport": "not-evaluated",
            }
        artifact_hashes = report.get("packageArtifactHashes")
        if not isinstance(artifact_hashes, dict):
            return {"status": "stale", "packageInputSha256": current_input_sha256, "packageArtifactHashes": live_artifact_hashes, "packageContentSha256": _canonical_sha256(package_file_inventory)}
        for name in ("mainTemplate", "createUiDefinition", "testParameters", "zip"):
            path_value = report.get(name)
            if not isinstance(path_value, str):
                return {"status": "stale", "packageInputSha256": current_input_sha256, "packageArtifactHashes": live_artifact_hashes, "packageContentSha256": _canonical_sha256(package_file_inventory)}
            path = resolve_artifact_reference(root, path_value)
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != artifact_hashes.get(name):
                return {
                    "status": "stale",
                    "version": report.get("version"),
                    "packageInputSha256": current_input_sha256,
                    "packageArtifactHashes": live_artifact_hashes,
                    "packageContentSha256": _canonical_sha256(package_file_inventory),
                    "recordedPackageArtifactHashes": artifact_hashes,
                    "deploymentParameters": report.get("deploymentParameters") or {},
                    "resourceInventory": [],
                    "bicepExtensibilityImports": [],
                    "whatIfSupport": "not-evaluated",
                }
        template_path = resolve_artifact_reference(root, report["mainTemplate"])
        template = json.loads(template_path.read_text(encoding="utf-8-sig"))
        inventory, imports = _scan_package_resources(template)
        return {
            "status": "current",
            "version": report.get("version"),
            "packageInputSha256": current_input_sha256,
            "packageArtifactHashes": live_artifact_hashes,
            "packageContentSha256": _canonical_sha256(package_file_inventory),
            "recordedPackageArtifactHashes": artifact_hashes,
            "deploymentParameters": report.get("deploymentParameters") or {},
            "resourceInventory": inventory,
            "bicepExtensibilityImports": imports,
            "whatIfSupport": (
                "unsupported-bicep-extensibility-imports"
                if imports
                else "not-required-for-planning"
            ),
        }
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return {
            "status": "stale",
            "packageInputSha256": current_input_sha256,
            "packageArtifactHashes": live_artifact_hashes,
            "packageContentSha256": _canonical_sha256(package_file_inventory),
            "recordedPackageArtifactHashes": {},
            "deploymentParameters": {},
            "resourceInventory": [],
            "bicepExtensibilityImports": [],
            "whatIfSupport": "not-evaluated",
        }


def _read_existing_dcr_preflight(root: Path, target: Mapping[str, Any]) -> dict[str, Any]:
    try:
        path = existing_artifact_path(root, "qualification-dcr-preflight.json")
        report = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {"status": "not-recorded", "contracts": []}
    expected_target = {
        key: target[key]
        for key in ("tenantId", "subscriptionId", "workspaceResourceId", "workspaceCustomerId")
    }
    target_fingerprint = _canonical_sha256(expected_target)
    if (
        not isinstance(report, dict)
        or report.get("targetFingerprint") != target_fingerprint
        or (report.get("target") or {}).get("locked") is not True
    ):
        return {"status": "stale", "contracts": []}
    contracts = report.get("contracts")
    return {
        "status": report.get("status", "unknown"),
        "targetFingerprint": report.get("targetFingerprint"),
        "plan": report.get("plan") or {},
        "contracts": contracts if isinstance(contracts, list) else [],
        "limitations": report.get("limitations") or [],
    }


def _mock_ingestion_plan(root: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    stage = (state.get("stages") or {}).get("mockIngestion") or {}
    artifacts = stage.get("artifacts") or {}
    selected: dict[str, Any] | None = None
    for name in ("mockIngestionPlan", "ingestionPlan"):
        reference = artifacts.get(name)
        if isinstance(reference, str):
            try:
                path = resolve_artifact_reference(root, reference)
                selected = json.loads(path.read_text(encoding="utf-8-sig"))
                break
            except (OSError, ValueError, json.JSONDecodeError):
                continue
    required = {
        "destinationKind",
        "destinationTable",
        "destinationResourceId",
        "inputStream",
        "outputStream",
        "payloadPath",
        "payloadSha256",
        "recordCount",
        "batchCount",
        "maxBatchRecordCount",
        "estimatedBytes",
        "estimatedCost",
        "retentionImpact",
        "contractFingerprint",
        "transformFingerprint",
        "schemaFingerprint",
        "markerField",
        "timestampFields",
        "pairRuleIds",
        "sharedOncePerPair",
    }
    if not isinstance(selected, dict) or not required <= set(selected):
        return {
            "status": "provisional",
            "reason": "exact reviewed ingestion plan and payload evidence are not recorded",
            "payloads": [],
            "benignControlRecordCount": None,
        }
    if (
        not _SHA256.fullmatch(str(selected.get("payloadSha256") or ""))
        or any(
            not _SHA256.fullmatch(str(selected.get(key) or ""))
            for key in ("contractFingerprint", "transformFingerprint", "schemaFingerprint")
        )
        or type(selected.get("recordCount")) is not int
        or selected["recordCount"] < 1
        or type(selected.get("batchCount")) is not int
        or selected["batchCount"] < 1
        or type(selected.get("maxBatchRecordCount")) is not int
        or selected["maxBatchRecordCount"] < 1
        or type(selected.get("estimatedBytes")) is not int
        or selected["estimatedBytes"] < 0
        or not isinstance(selected.get("estimatedCost"), dict)
        or not isinstance(selected.get("retentionImpact"), (str, dict))
        or not isinstance(selected.get("markerField"), str)
        or not selected["markerField"]
        or selected.get("destinationKind") not in {"standard", "custom"}
        or not isinstance(selected.get("timestampFields"), list)
        or not selected["timestampFields"]
        or not isinstance(selected.get("pairRuleIds"), list)
        or not selected.get("pairRuleIds")
        or selected.get("sharedOncePerPair") is not True
        or type(selected.get("benignControlRecordCount")) is not int
        or selected["benignControlRecordCount"] < 0
    ):
        return {
            "status": "provisional",
            "reason": "ingestion plan evidence is incomplete or malformed",
            "payloads": [],
            "benignControlRecordCount": None,
        }
    try:
        payload = resolve_artifact_reference(root, selected["payloadPath"])
        selected_run = report_directory(root).resolve(strict=True)
        payload.resolve(strict=True).relative_to(selected_run)
        payload_bytes = payload.read_bytes()
        records = json.loads(payload_bytes.decode("utf-8-sig"))
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        return {
            "status": "provisional",
            "reason": "payload is missing or is not confined to the selected run",
            "payloads": [],
            "benignControlRecordCount": None,
        }
    if (
        hashlib.sha256(payload_bytes).hexdigest() != selected["payloadSha256"]
        or not isinstance(records, list)
        or len(records) != selected["recordCount"]
        or any(not isinstance(item, dict) for item in records)
    ):
        return {
            "status": "provisional",
            "reason": "payload hash or record count does not match the reviewed ingestion plan",
            "payloads": [],
            "benignControlRecordCount": None,
        }
    return {
        "status": "ready",
        "payloads": [
            {
                key: selected[key]
                for key in sorted(required)
            }
        ],
        "benignControlRecordCount": selected.get("benignControlRecordCount"),
        "estimatedBytes": selected.get("estimatedBytes"),
        "retentionImpact": selected.get("retentionImpact"),
        "sharedOncePerPair": selected.get("sharedOncePerPair") is True,
    }


def _components(
    root: Path,
    *,
    source_ids: list[str],
    sentinel_rule_ids: list[str],
    pair_rule_ids: list[str],
    additional_rule_ids: list[str],
    graph_projections: Mapping[str, Mapping[str, Any]],
    package: Mapping[str, Any],
    dcr: Mapping[str, Any],
    ingestion: Mapping[str, Any],
) -> dict[str, Any]:
    contracts = dcr.get("contracts") if isinstance(dcr.get("contracts"), list) else []
    compatible = any(
        (item.get("existingCandidateCompatibility") or {}).get("status") == "compatible-existing"
        and (item.get("tableSchemaCompatibility") or {}).get("status") == "compatible"
        for item in contracts
        if isinstance(item, dict)
    )
    dcr_determination = bool(contracts) and all(
        isinstance(item, dict)
        and (
            (item.get("existingCandidateCompatibility") or {}).get("status")
            == "compatible-existing"
            or item.get("candidateState") in {
                "planned-missing-resources",
                "blocked-destination",
                "inspection-denied",
                "inspection-unknown",
                "partial-resource-pair",
            }
        )
        for item in contracts
    )
    fallback_dcr_confirmed = (
        bool(contracts)
        and dcr_determination
        and not compatible
        and all(
            item.get("candidateState") == "planned-missing-resources"
            or (
                item.get("candidateState") == "blocked-destination"
                and (item.get("existingCandidateCompatibility") or {}).get("reason")
            )
            for item in contracts
            if isinstance(item, dict)
        )
    )
    custom_missing = []
    custom_incompatible = []
    known_destinations: list[dict[str, Any]] = []
    resource_candidates: list[dict[str, Any]] = []
    for item in contracts:
        if not isinstance(item, dict) or not item.get("schemaFingerprint"):
            continue
        resources = item.get("resources") or {}
        table = resources.get("destinationTable") or {}
        dcr_resource = resources.get("dcr") or {}
        dce_resource = resources.get("dce") or {}
        resource_candidates.append({
            "contractPath": item.get("contractPath"),
            "contractFingerprint": item.get("contractFingerprint"),
            "resourceFingerprint": item.get("resourceFingerprint"),
            "candidateState": item.get("candidateState", "unknown"),
            "dcr": {
                "resourceId": dcr_resource.get("id"),
                "state": dcr_resource.get("state", "unknown"),
            },
            "dce": {
                "resourceId": dce_resource.get("id"),
                "state": dce_resource.get("state", "unknown"),
            },
        })
        contract_path = item.get("contractPath")
        try:
            contract = repository_root(root) / "Tools" / "AzureMonitorLogsIngestion" / str(contract_path)
            contract_document = yaml.safe_load(contract.read_text(encoding="utf-8-sig")) or {}
        except (OSError, ValueError, yaml.YAMLError):
            continue
        destination = contract_document.get("destination") or {}
        if destination.get("kind") not in {"custom", "standard"}:
            continue
        destination_record = {
            "table": item.get("table"),
            "tableResourceId": table.get("id"),
            "destinationKind": destination.get("kind"),
            "contractPath": contract_path,
            "schemaFingerprint": item.get("schemaFingerprint"),
            "transformFingerprint": item.get("transformFingerprint"),
            "contractFingerprint": item.get("contractFingerprint"),
            "columnCount": len(destination.get("columns") or []),
            "state": table.get("state", "unknown"),
            "schemaCompatibility": (item.get("tableSchemaCompatibility") or {}).get("status", "unknown"),
        }
        known_destinations.append(destination_record)
        if destination.get("kind") == "custom" and table.get("state") == "missing":
            custom_missing.append(destination_record)
        elif (
            destination.get("kind") == "custom"
            and table.get("state") == "present"
            and destination_record["schemaCompatibility"] != "compatible"
        ):
            custom_incompatible.append(destination_record)
    package_current = package.get("status") == "current"
    flags = package.get("deploymentParameters")
    return {
        "sentinelAlertRules": {
            "status": "proposed",
            "resourceTypes": ["Microsoft.SecurityInsights/alertRules"],
            "disabled": True,
            "maximumCount": len(sentinel_rule_ids),
            "sourceRuleIds": sentinel_rule_ids,
            "eligiblePairs": pair_rule_ids,
        },
        "xdrCustomDetections": {
            "status": "proposed",
            "resourceTypes": ["Microsoft.Security/detectionRules"],
            "disabled": True,
            "maximumCount": len(source_ids),
            "maximumAdditionalCount": len(additional_rule_ids),
            "sourceRuleIds": source_ids,
            "currentlyReviewedDraftIds": sorted(
                set(source_ids) - set(additional_rule_ids)
            ),
            "maximumTotalIncludesCurrentReviewedDrafts": True,
            "eligiblePairs": pair_rule_ids,
            "graphProjectionByRule": [
                {
                    "sourceRuleId": rule_id,
                    "status": projection.get("status"),
                    "projectedTactics": projection.get("projectedTactics") or [],
                    "omittedTactics": projection.get("omittedTactics") or [],
                    "projectedTechniques": projection.get("projectedTechniques") or [],
                    "omittedTechniques": projection.get("omittedTechniques") or [],
                    "classificationParity": projection.get("classificationParity", "not-established"),
                }
                for rule_id, projection in sorted(graph_projections.items())
                if rule_id in source_ids
            ],
        },
        "controlledAlertParity": {
            "status": "provisional" if pair_rule_ids else "unavailable",
            "advanceConsentSupported": False,
            "reason": (
                "the scope planner does not bind a finite parity test window or "
                "a complete batch fixture plan"
            ),
            "operation": "temporarily-enable-reviewed-pairs-then-restore-disabled",
            "resourceTypes": [
                "Microsoft.SecurityInsights/alertRules",
                "Microsoft.Security/detectionRules",
            ],
            "eligiblePairRuleIds": pair_rule_ids,
            "maximumRulePairCount": len(pair_rule_ids),
            "maximumEnableWriteRequests": 2 * len(pair_rule_ids),
            "maximumRestoreWriteRequests": 2 * len(pair_rule_ids),
            "maximumWriteRequestsForOneBoundedRun": 4 * len(pair_rule_ids),
            "timeWindow": {"status": "not-recorded", "startsAt": None, "endsAt": None},
            "restoreDisabledOnCompletionOrAbort": True,
            "repeatedRunsRequireNewExactScope": True,
        },
        "fullPackageAcceptance": {
            "status": "available" if package_current else "provisional",
            "resourceInventory": package.get("resourceInventory", []),
            "resourceTypes": sorted({
                item.get("typeAtVersion", item.get("type"))
                for item in package.get("resourceInventory", [])
                if isinstance(item, dict) and isinstance(item.get("type"), str)
            }),
            "availableFlags": flags if isinstance(flags, dict) else {},
            "packageInstallationAndXdrRegistration": True,
            "nonRuleStoredContentAutoApproval": False,
        },
        "mockTelemetryIngestion": {
            "status": ingestion.get("status", "provisional"),
            "plan": ingestion,
            "purpose": "ingest reviewed local mock telemetry once per AR/CD pair",
            "benignControlsAreNotIngested": True,
        },
        "fallbackDcr": {
            "status": "conditional",
            "condition": "no proven compatible existing solution DCR",
            "resourceTypes": ["Microsoft.Insights/dataCollectionRules"],
            "maximumCount": 1,
            "scope": {
                "subscriptionId": (package.get("target") or {}).get("subscriptionId"),
                "resourceGroup": (package.get("target") or {}).get("resourceGroup"),
            },
            "compatibleExistingDcrProven": compatible,
            "absenceOfCompatibleDcrProven": fallback_dcr_confirmed,
            "resourceCandidates": resource_candidates,
            "absenceEvidence": (
                "registered-candidate-check"
                if fallback_dcr_confirmed
                else "unknown; resolver does not discover arbitrary solution-owned DCRs"
            ),
            "requiresFreshExactReadinessBeforeProvisioning": True,
        },
        "fallbackDce": {
            "status": "conditional",
            "condition": "DCE selected or required by the chosen ingestion route",
            "resourceTypes": ["Microsoft.Insights/dataCollectionEndpoints"],
            "maximumCount": 1,
            "resourceCandidates": [
                {
                    key: candidate.get(key)
                    for key in ("contractPath", "contractFingerprint", "resourceFingerprint", "dce")
                }
                for candidate in resource_candidates
            ],
            "scope": {
                "subscriptionId": (package.get("target") or {}).get("subscriptionId"),
                "resourceGroup": (package.get("target") or {}).get("resourceGroup"),
            },
            "requiresExplicitSelection": True,
        },
        "customTableCreate": {
            "status": (
                "conditional"
                if custom_missing
                else "blocked-existing-incompatible"
                if custom_incompatible
                else "not-needed"
                if known_destinations and all(
                    item["destinationKind"] == "standard" or item["state"] == "present"
                    for item in known_destinations
                )
                else "provisional"
            ),
            "condition": "custom-log destination is contract-proven absent",
            "resourceTypes": ["Microsoft.OperationalInsights/workspaces/tables"],
            "tables": custom_missing,
            "knownDestinations": known_destinations,
            "incompatibleExistingTables": custom_incompatible,
            "existingIncompatibleTableMayBeAltered": False,
            "nativeCommonSecurityLogLookalikeAllowed": False,
        },
        "ownedResourceCleanup": {
            "status": "unsupported",
            "advanceConsentSupported": False,
            "reason": (
                "no exact run-owned cleanup inventory or deletion executor is "
                "implemented by the current scope planner"
            ),
            "resourceTypes": [],
            "resources": [],
            "maximumDeleteCount": 0,
            "ownershipEvidence": "not-recorded",
            "existingOrUnownedResourcesMayBeDeleted": False,
        },
    }


def _consent_state(
    root: Path,
    plan_sha256: str,
    *,
    components: Mapping[str, Any],
    package: Mapping[str, Any],
    target: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        path = existing_artifact_path(root, CONSENT_FILE_NAME)
        record = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {"status": "not-recorded", "approvedComponents": []}
    if not isinstance(record, dict) or record.get("schemaVersion") != PLAN_SCHEMA_VERSION:
        return {"status": "unknown", "approvedComponents": []}
    approved = record.get("approvedComponents")
    if record.get("planSha256") != plan_sha256:
        return {
            "status": "stale",
            "approvedComponents": [],
            "previousPlanSha256": record.get("planSha256"),
        }
    if (
        record.get("status") != "approved"
        or not isinstance(approved, list)
        or not approved
        or any(name not in COMPONENTS for name in approved)
    ):
        return {
            "status": "declined" if record.get("status") == "declined" else "not-approved",
            "approvedComponents": [],
            "actor": record.get("actor"),
            "approvedAt": record.get("approvedAt"),
            "reason": record.get("reason"),
        }
    if (
        not isinstance(record.get("actor"), str)
        or not record["actor"].strip()
        or not isinstance(record.get("approvedAt"), str)
        or (record.get("scope") or {}).get("planSha256") != plan_sha256
    ):
        return {"status": "unknown", "approvedComponents": []}
    fingerprinted_record = {
        key: value for key, value in record.items() if key != "approvalSha256"
    }
    if record.get("approvalSha256") != _canonical_sha256(fingerprinted_record):
        return {"status": "unknown", "approvedComponents": []}
    if len(set(approved)) != len(approved):
        return {"status": "unknown", "approvedComponents": []}
    has_pair_component = bool(
        {"sentinelAlertRules", "xdrCustomDetections"} & set(approved)
    )
    pair_components = {"sentinelAlertRules", "xdrCustomDetections"} & set(approved)
    if pair_components and pair_components != {"sentinelAlertRules", "xdrCustomDetections"}:
        return {"status": "unknown", "approvedComponents": []}
    cap = record.get("maxAdditionalCustomDetections")
    eligible_max = (
        components.get("xdrCustomDetections", {}).get("maximumAdditionalCount", 0)
        if isinstance(components.get("xdrCustomDetections"), dict)
        else 0
    )
    if has_pair_component:
        if type(cap) is not int or cap < 0 or cap > eligible_max:
            return {"status": "unknown", "approvedComponents": []}
    elif cap is not None:
        return {"status": "unknown", "approvedComponents": []}
    conditional = record.get("conditionalSelections")
    if not isinstance(conditional, dict):
        return {"status": "unknown", "approvedComponents": []}
    if "fallbackDce" in approved and (
        "fallbackDcr" not in approved
        or conditional.get("dceSelectedOrRequired") is not True
    ):
        return {"status": "unknown", "approvedComponents": []}
    if "fallbackDcr" in approved and (
        components.get("fallbackDcr", {}).get("status") != "conditional"
        or components.get("fallbackDcr", {}).get("compatibleExistingDcrProven") is True
    ):
        return {"status": "stale", "approvedComponents": []}
    if "fullPackageAcceptance" in approved:
        expected_flags = (
            components.get("fullPackageAcceptance", {}).get("availableFlags") or {}
        )
        package_flags = record.get("packageFlags")
        if (
            package.get("status") != "current"
            or not isinstance(package_flags, dict)
            or set(package_flags) != set(expected_flags)
            or any(type(value) is not bool for value in package_flags.values())
        ):
            return {"status": "stale", "approvedComponents": []}
    elif record.get("packageFlags") != {}:
        return {"status": "unknown", "approvedComponents": []}
    recorded_scope = record.get("scope")
    expected_resource_types = sorted({
        item
        for name in approved
        for item in (components.get(name, {}).get("resourceTypes") or [])
    })
    scope_resource_types = recorded_scope.get("resourceTypes") if isinstance(recorded_scope, dict) else None
    if (
        not isinstance(recorded_scope, dict)
        or recorded_scope.get("target") != target
        or not isinstance(scope_resource_types, list)
        or any(not isinstance(item, str) for item in scope_resource_types)
        or sorted(scope_resource_types) != expected_resource_types
    ):
        return {"status": "unknown", "approvedComponents": []}
    expected_package_inventory = (
        package.get("resourceInventory") or []
        if "fullPackageAcceptance" in approved
        else []
    )
    if recorded_scope.get("packageResourceInventory") != expected_package_inventory:
        return {"status": "unknown", "approvedComponents": []}
    scoped = []
    for name in approved:
        component = components.get(name)
        if not isinstance(component, dict):
            continue
        if name == "fullPackageAcceptance" and package.get("status") != "current":
            continue
        scoped.append(name)
    return {
        "status": "approved" if scoped and scoped == approved else "stale",
        "executionMode": (
            "both"
            if {"sentinelAlertRules", "xdrCustomDetections"} & set(scoped)
            and "fullPackageAcceptance" in scoped
            else "pairs"
            if {"sentinelAlertRules", "xdrCustomDetections"} & set(scoped)
            else "package"
            if "fullPackageAcceptance" in scoped
            else "not-selected"
        ),
        "approvedComponents": scoped,
        "approvedAt": record.get("approvedAt"),
        "actor": record.get("actor"),
        "planSha256": plan_sha256,
        "maxAdditionalCustomDetections": record.get("maxAdditionalCustomDetections"),
        "packageFlags": record.get("packageFlags") or {},
        "conditionalSelections": record.get("conditionalSelections") or {},
        "resourceTypes": (record.get("scope") or {}).get("resourceTypes") or [],
    }


def build_deployment_plan(
    solution: str | Path,
    *,
    target: Mapping[str, Any] | None = None,
    dcr_preflight: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    state_path = existing_artifact_path(root, "workflow-state.json")
    if not state_path.is_file():
        return {
            "schemaVersion": PLAN_SCHEMA_VERSION,
            "status": "unavailable",
            "selectedProfile": "unknown",
            "planningConsent": {"status": "not-recorded", "approvedComponents": []},
            "exactScopeWriteApproval": "not-recorded",
            "reason": "persisted Qualification workflow state is unavailable",
        }
    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    context = state.get("context") or {}
    selected_profile = (
        context.get("workflowProfile")
        if context.get("profileSelectionConfirmed") is True
        else "unknown"
    )
    if selected_profile != "qualification":
        return {
            "schemaVersion": PLAN_SCHEMA_VERSION,
            "status": "not-applicable",
            "selectedProfile": selected_profile,
            "planningConsent": {"status": "not-recorded", "approvedComponents": []},
            "exactScopeWriteApproval": "not-recorded",
            "reason": "advance deployment planning is Qualification-only",
        }
    locked = target or require_locked_target(root, materialize_missing=False)
    workspace = workspace_identity(locked["workspaceResourceId"])
    source = _source_inventory(root)
    rules, duplicates = _source_records(root)
    reviewed_drafts, excluded_ids, reviewed_projections = _reviewed_current_drafts(root, rules)
    eligible_ids, ineligible_ids, eligible_projections = _eligible_rule_ids(
        root, rules, duplicates, set(excluded_ids)
    )
    sentinel_ids, sentinel_ineligible_ids = _eligible_analytic_rule_ids(rules, duplicates)
    from .packaging_selection import (
        _partial_coverage_allowed,
        verify_applied_package_selection,
    )

    package_selection = verify_applied_package_selection(
        root, str(state.get("runId") or ""),
    )
    package_stage = (state.get("stages") or {}).get("packaging") or {}
    package_stage_selection = (package_stage.get("artifacts") or {}).get(
        "selectionOutcome"
    )
    if package_stage_selection == "partial-package-validated" and not package_selection:
        raise ValueError("partial Qualification requires its current applied package selection")
    qualification_scope = None
    if package_selection is not None:
        selection_plan = package_selection["plan"]
        selection_summary = selection_plan.get("summary") or {}
        if (
            selection_summary.get("outcome") == "partial"
            and not _partial_coverage_allowed(selection_summary)
        ):
            raise ValueError("current package selection no longer meets migrated-detection coverage")
        selected_source_paths = {
            str(value).replace("\\", "/").casefold()
            for value in (selection_plan.get("selection") or {}).get(
                "analyticRules", []
            )
        }
        selected_source_ids = {
            str(item.get("id") or "").casefold()
            for item in selection_plan.get("analyticRules") or []
            if item.get("included") is True
        }
        selected_detection_ids = {
            str(item.get("sourceId") or "").casefold()
            for item in selection_plan.get("xdrDetections") or []
            if item.get("included") is True
        }
        selected_source_id_by_path = {
            str(item.get("path") or "").replace("\\", "/").casefold():
                str(item.get("id") or "").casefold()
            for item in selection_plan.get("analyticRules") or []
            if item.get("included") is True
        }
        if selected_source_ids != {
            value for value in selected_source_id_by_path.values() if value
        }:
            raise ValueError("applied package selection source IDs do not match selected AR paths")
        reviewed_drafts = [
            item for item in reviewed_drafts if item.casefold() in selected_detection_ids
        ]
        eligible_ids = [
            item for item in eligible_ids if item.casefold() in selected_detection_ids
        ]
        eligible_projections = {
            key: value for key, value in eligible_projections.items()
            if key.casefold() in selected_detection_ids
        }
        reviewed_projections = {
            key: value for key, value in reviewed_projections.items()
            if key.casefold() in selected_detection_ids
        }
        sentinel_ids = [
            item for item in sentinel_ids if item.casefold() in selected_source_ids
        ]
        sentinel_ineligible_ids = [
            item for item in sentinel_ineligible_ids
            if item.casefold() in selected_source_ids
        ]
        ineligible_ids = [
            item for item in ineligible_ids
            if item.casefold() in selected_detection_ids
        ]
        qualification_scope = {
            "kind": "applied-package-selection",
            "planSha256": selection_plan.get("planSha256"),
            "outcome": selection_summary.get("outcome"),
            "coverage": selection_summary,
            "selectedAnalyticRulePaths": sorted(selected_source_paths),
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
    current_ids = {item.casefold() for item in reviewed_drafts}
    additional_ids = [
        item for item in eligible_ids if item.casefold() not in current_ids
    ]
    all_graph_ids_by_key = {
        item.casefold(): item for item in [*reviewed_drafts, *eligible_ids]
    }
    graph_scope_ids = sorted(all_graph_ids_by_key.values(), key=str.casefold)
    sentinel_ids_by_key = {item.casefold(): item for item in sentinel_ids}
    pair_ids = sorted(
        (
            sentinel_ids_by_key[key]
            for key in all_graph_ids_by_key.keys() & sentinel_ids_by_key.keys()
        ),
        key=str.casefold,
    )
    pair_additional_ids = [
        item for item in additional_ids if item.casefold() in sentinel_ids_by_key
    ]
    graph_projections = {**eligible_projections, **reviewed_projections}
    package = _current_package(root, state)
    package["target"] = {
        "subscriptionId": locked["subscriptionId"],
        "resourceGroup": workspace["resourceGroup"],
    }
    dcr_report = (
        dict(dcr_preflight)
        if isinstance(dcr_preflight, Mapping)
        else _read_existing_dcr_preflight(root, locked)
    )
    ingestion = _mock_ingestion_plan(root, state)
    component_details = _components(
        root,
        source_ids=graph_scope_ids,
        sentinel_rule_ids=sentinel_ids,
        pair_rule_ids=pair_ids,
        additional_rule_ids=additional_ids,
        graph_projections=graph_projections,
        package=package,
        dcr=dcr_report,
        ingestion=ingestion,
    )
    source_name = root.name
    try:
        solution_version = package.get("version") or solution_data_version(root)
    except (OSError, ValueError):
        solution_version = package.get("version")
    plan = {
        "schemaVersion": PLAN_SCHEMA_VERSION,
        "status": (
            "provisional"
            if (
                package.get("status") != "current"
                or ingestion.get("status") != "ready"
                or source.get("manifestContentInventory", {}).get("status") != "ready"
            )
            else "current"
        ),
        "selectedProfile": selected_profile,
        "qualificationScope": qualification_scope,
        "executionMode": "not-selected",
        "target": {
            "tenantId": locked["tenantId"],
            "subscriptionId": locked["subscriptionId"],
            "resourceGroup": workspace["resourceGroup"],
            "workspaceResourceId": locked["workspaceResourceId"],
            "workspaceCustomerId": locked["workspaceCustomerId"],
            "solution": source_name,
            "version": solution_version,
        },
        "sourceInventory": source["counts"],
        "sourceFileCounts": source.get("fileCounts", {}),
        "manifestContentInventory": source.get("manifestContentInventory", {}),
        "sourceInventorySha256": source["sourceInventorySha256"],
        "detectionScope": {
            "sourceAnalyticRuleCount": source["analyticRuleCount"],
            "currentReviewedDraftCount": len(reviewed_drafts),
            "currentReviewedDraftIds": reviewed_drafts,
            "eligibleSentinelAlertRuleIds": sentinel_ids,
            "ineligibleSentinelAlertRuleIds": sentinel_ineligible_ids,
            "eligibleMaximumAdditionalCustomDetections": len(additional_ids),
            "eligibleAdditionalRuleIds": additional_ids,
            "eligibleMaximumTotalCustomDetections": len(graph_scope_ids),
            "eligibleMaximumAdditionalDisabledRulePairs": len(pair_additional_ids),
            "eligibleAdditionalPairRuleIds": pair_additional_ids,
            "eligibleMaximumTotalDisabledRulePairs": len(pair_ids),
            "eligiblePairRuleIds": pair_ids,
            "maximumTotalDisabledRulePairs": len(pair_ids),
            "maximumTotalCustomDetectionsIncludesCurrentDrafts": True,
            "excludedRuleIds": excluded_ids,
            "ineligibleRuleIds": [
                rule_id
                for rule_id in ineligible_ids
                if rule_id.casefold() not in current_ids
            ],
            "ineligibleNewConversionCandidateRuleIds": ineligible_ids,
            "currentReviewedDraftsNotEligibleAsNewConversionCandidates": [
                rule_id
                for rule_id in reviewed_drafts
                if rule_id.casefold() in {item.casefold() for item in ineligible_ids}
            ],
            "eligibilityNote": (
                "Current reviewed drafts are evaluated from their persisted reviewed "
                "disabled Graph payloads and explicit projections. New-conversion "
                "candidate failures do not invalidate a matching current reviewed draft."
            ),
            "duplicateSourceRuleIds": sorted(
                rules[item]["id"] for item in duplicates if item in rules
            ),
        },
        "scopeCaps": {
            "maxAdditionalCustomDetections": len(additional_ids),
            "maxDcrCount": 1,
            "maxDceCount": 1,
            "maxCustomTableCount": len(component_details["customTableCreate"]["tables"]),
        },
        "packageInputSha256": package.get("packageInputSha256"),
        "packageArtifactHashes": package.get("packageArtifactHashes") or {},
        "packageContentSha256": package.get("packageContentSha256"),
        "recordedPackageArtifactHashes": package.get("recordedPackageArtifactHashes") or {},
        "packageIdentity": {
            "status": package.get("status", "unavailable"),
            "version": package.get("version"),
        },
        "packageResourceInventory": package.get("resourceInventory") or [],
        "bicepExtensibilityImports": package.get("bicepExtensibilityImports") or [],
        "whatIfSupport": package.get("whatIfSupport", "not-evaluated"),
        "components": component_details,
        "packageAcceptancePlan": {
            "status": "proposed-not-approved" if package.get("status") == "current" else "provisional",
            "executionStatus": "not-started",
            "resourceTypes": sorted({
                item["typeAtVersion"]
                for item in package.get("resourceInventory") or []
                if isinstance(item, dict) and isinstance(item.get("typeAtVersion"), str)
            }),
            "identity": {
                "status": package.get("status"),
                "packageInputSha256": package.get("packageInputSha256"),
                "packageArtifactHashes": package.get("packageArtifactHashes") or {},
                "version": package.get("version"),
            },
        },
        "dcrEvidence": {
            "targetFingerprint": dcr_report.get("targetFingerprint"),
            "plan": {
                key: (dcr_report.get("plan") or {}).get(key)
                for key in ("status", "inventorySha256", "targetSha256")
                if key in (dcr_report.get("plan") or {})
            },
            "contracts": [
                {
                    key: item[key]
                    for key in (
                        "table",
                        "contractPath",
                        "schemaFingerprint",
                        "transformFingerprint",
                        "contractFingerprint",
                        "resourceFingerprint",
                        "candidateSelection",
                        "candidateState",
                        "resourceFingerprint",
                    )
                    if key in item
                }
                for item in (dcr_report.get("contracts") or [])
                if isinstance(item, dict)
            ],
            "resourceCandidates": component_details["fallbackDcr"]["resourceCandidates"],
        },
        "dcrResolver": {
            "kind": "registered-exact-resource-name-only",
            "arbitrarySolutionOwnedDcrDiscovery": False,
            "limitations": dcr_report.get("limitations") or [
                "Only registered contract-specific resource candidates are inspected; arbitrary solution-listed DCR discovery is not implemented."
            ],
        },
        "separateApprovals": {
            "planningConsent": "not-recorded",
            "exactScopeWriteApproval": "required-immediately-before-each-write",
            "permissions": "diagnostic-only",
            "technicalReadiness": "diagnostic-only",
            "deploymentEvidence": "not-recorded",
            "resourceProvisioning": "distinct-write-operation",
            "mockIngestion": "distinct-write-operation",
            "enablement": "not-authorized",
            "cleanup": "not-authorized",
            "retentionChanges": "not-authorized",
            "roleAssignments": "not-authorized",
        },
    }
    plan["planSha256"] = _canonical_sha256(plan)
    plan["planningConsent"] = _consent_state(
        root,
        plan["planSha256"],
        components=component_details,
        package=package,
        target=plan["target"],
    )
    plan["executionMode"] = plan["planningConsent"].get("executionMode", "not-selected")
    plan["packageAcceptancePlan"]["approvalStatus"] = (
        "approved"
        if "fullPackageAcceptance" in plan["planningConsent"].get("approvedComponents", [])
        else "not-approved"
    )
    plan["packageAcceptancePlan"]["planningConsent"] = plan["planningConsent"]["status"]
    plan["packageAcceptancePlan"]["selectedFlags"] = (
        plan["planningConsent"].get("packageFlags", {})
        if "fullPackageAcceptance" in plan["planningConsent"].get("approvedComponents", [])
        else {}
    )
    plan["exactScopeWriteApproval"] = "not-recorded"
    return plan


def record_planning_consent(
    solution: str | Path,
    *,
    expected_plan_sha256: str,
    actor: str,
    approved_components: list[str],
    declined: bool = False,
    reason: str | None = None,
    max_additional_custom_detections: int | None = None,
    package_flags: Mapping[str, bool] | None = None,
    dce_selected: bool = False,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("planning consent requires an explicit nonempty actor")
    plan = build_deployment_plan(root)
    if not _SHA256.fullmatch(expected_plan_sha256) or plan.get("planSha256") != expected_plan_sha256:
        raise ValueError("deployment plan changed; rerun preflight and review its current plan hash")
    if declined:
        if approved_components:
            raise ValueError("decline cannot be combined with approved components")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("declining planning consent requires a reason")
        status = "declined"
    else:
        if not approved_components:
            raise ValueError("select at least one component to approve")
        if len(set(approved_components)) != len(approved_components):
            raise ValueError("planning consent components must be unique")
        unknown = set(approved_components) - COMPONENTS
        if unknown:
            raise ValueError("unsupported planning consent component: " + ", ".join(sorted(unknown)))
        components = plan.get("components") or {}
        for component in approved_components:
            details = components.get(component) or {}
            if component in {"sentinelAlertRules", "xdrCustomDetections"} and details.get("maximumCount", 0) < 1:
                raise ValueError(f"{component} has no eligible source rules in the current plan")
            if component == "fullPackageAcceptance" and details.get("status") != "available":
                raise ValueError("full-package planning consent requires a current verified package")
            if component == "mockTelemetryIngestion" and details.get("status") != "ready":
                raise ValueError("mock-ingestion consent requires a complete reviewed payload and ingestion plan")
            if component == "customTableCreate" and details.get("status") != "conditional":
                raise ValueError("custom-table creation is not proven necessary by the current exact contract")
            if component == "fallbackDce" and not dce_selected:
                raise ValueError("DCE consent requires an explicit --dce-selected decision")
            if component == "fallbackDce" and "fallbackDcr" not in approved_components:
                raise ValueError("conditional DCE consent must be paired with fallback DCR scope")
            if (
                component == "fallbackDcr"
                and details.get("compatibleExistingDcrProven") is True
            ):
                raise ValueError("fallback DCR is not in scope while a compatible existing solution DCR is proven")
        if {"sentinelAlertRules", "xdrCustomDetections"} & set(approved_components):
            if not {"sentinelAlertRules", "xdrCustomDetections"} <= set(approved_components):
                raise ValueError(
                    "disabled Sentinel/XDR pair consent must include both sentinelAlertRules and xdrCustomDetections"
                )
            if max_additional_custom_detections is None:
                raise ValueError("pair planning consent requires --max-additional-custom-detections")
            maximum = (plan.get("detectionScope") or {}).get(
                "eligibleMaximumAdditionalCustomDetections", 0
            )
            if (
                type(max_additional_custom_detections) is not int
                or not 0 <= max_additional_custom_detections <= maximum
            ):
                raise ValueError(
                    "max additional Custom Detections must be an integer within the current eligible bound"
                )
        if "fullPackageAcceptance" in approved_components:
            expected_flags = (components.get("fullPackageAcceptance") or {}).get("availableFlags") or {}
            supplied_flags = dict(package_flags or {})
            if (
                not expected_flags
                or set(supplied_flags) != set(expected_flags)
                or any(type(value) is not bool for value in supplied_flags.values())
            ):
                raise ValueError(
                    "full-package consent requires an explicit boolean value for every current package selection flag"
                )
        else:
            supplied_flags = {}
        status = "approved"
    record = {
        "schemaVersion": PLAN_SCHEMA_VERSION,
        "status": status,
        "planSha256": expected_plan_sha256,
        "approvedComponents": sorted(approved_components) if not declined else [],
        "actor": actor.strip(),
        "approvedAt": datetime.now(timezone.utc).isoformat(),
        "reason": reason.strip() if isinstance(reason, str) else None,
        "maxAdditionalCustomDetections": (
            max_additional_custom_detections if not declined else None
        ),
        "packageFlags": supplied_flags if not declined else {},
        "executionMode": (
            "both"
            if "fullPackageAcceptance" in approved_components
            and {"sentinelAlertRules", "xdrCustomDetections"} <= set(approved_components)
            else "pairs"
            if {"sentinelAlertRules", "xdrCustomDetections"} <= set(approved_components)
            else "package"
            if "fullPackageAcceptance" in approved_components
            else "ingestion-or-provisioning"
        ) if not declined else "not-selected",
        "conditionalSelections": {
            "dceSelectedOrRequired": dce_selected,
            "fallbackDcrOnlyWhenNoProvenCompatibleSolutionDcr": True,
            "customTableOnlyWhenExactContractProvesAbsent": True,
        },
        "scope": {
            "target": plan.get("target"),
            "resourceTypes": sorted({
                item
                for name in approved_components if name in (plan.get("components") or {})
                for item in (plan["components"][name].get("resourceTypes") or [])
            }),
            "packageResourceInventory": (
                plan.get("packageResourceInventory") or []
                if "fullPackageAcceptance" in approved_components
                else []
            ),
            "planSha256": expected_plan_sha256,
        },
        "environmentWritesAuthorized": False,
    }
    record["approvalSha256"] = _canonical_sha256(record)
    path = artifact_path(root, CONSENT_FILE_NAME, create_parent=True)
    write_json_artifact(root, path, record)
    return {
        "status": status,
        "path": str(path),
        "planSha256": expected_plan_sha256,
        "approvedComponents": record["approvedComponents"],
        "environmentWritesAuthorized": False,
    }


def persist_deployment_plan(solution: str | Path) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    plan = build_deployment_plan(root)
    path = artifact_path(root, PLAN_FILE_NAME, create_parent=True)
    write_json_artifact(root, path, plan)
    return {**plan, "planPath": str(path)}
