#!/usr/bin/env python3
"""Validate XDR Detections and Defender XDR Workbooks for local solution validation.

Checks both content families:
- XDR Detections (`Solutions/<Solution>/XDR Detections/*.{yaml,yml}` + `Data/*.json` +
  `Package/mainTemplate.json` `CustomDetection` resources)
- XDR Workbooks (`Solutions/<Solution>/XDR Workbooks/*.json` + `Data/*.json` +
  `Package/mainTemplate.json` `DefenderWorkbook-*` resources & `dependsOn` integrity)

Outputs a structured JSON report consumed by `.script/local-validation/validate.ts`
and `.script/local-validation/build-and-validate.ps1`.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CONTENT_PACKAGE_EXTENSION_DEP = (
    "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', "
    "parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', "
    "variables('_solutionId'))]"
)


def _setup_toolkit_imports(toolkit_root: Path) -> None:
    migration_root = toolkit_root / "Tools" / "SentinelToXDRMigration"
    if str(migration_root) not in sys.path:
        sys.path.insert(0, str(migration_root))


def _rel_path(path: Path, content_root: Path) -> str:
    try:
        return path.resolve().relative_to(content_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _arm_copy(value: Any) -> Any:
    if isinstance(value, str):
        return "[" + value if value.startswith("[") else value
    if isinstance(value, dict):
        return {key: _arm_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_arm_copy(item) for item in value]
    return value


def _discover_solutions(
    content_root: Path,
    solution_path: str | None,
    files: list[str] | None,
) -> list[Path]:
    solutions: list[Path] = []
    seen: set[Path] = set()

    def add_solution(candidate: Path) -> None:
        resolved = candidate.resolve()
        if resolved not in seen and resolved.is_dir():
            seen.add(resolved)
            solutions.append(resolved)

    if solution_path:
        candidate = Path(solution_path)
        if not candidate.is_absolute():
            candidate = content_root / candidate
        if candidate.is_dir():
            # Check if candidate is Solutions/<Name> or a subfolder inside Solutions/<Name>
            try:
                rel = candidate.resolve().relative_to(content_root.resolve())
                parts = rel.parts
                if len(parts) >= 2 and parts[0] == "Solutions":
                    add_solution(content_root / "Solutions" / parts[1])
                else:
                    add_solution(candidate)
            except ValueError:
                add_solution(candidate)

    for raw_file in files or []:
        file_path = Path(raw_file)
        if not file_path.is_absolute():
            file_path = content_root / file_path
        try:
            rel = file_path.resolve().relative_to(content_root.resolve())
            parts = rel.parts
            if len(parts) >= 2 and parts[0] == "Solutions":
                add_solution(content_root / "Solutions" / parts[1])
        except ValueError:
            pass

    return solutions


def _load_solution_data(solution_root: Path) -> tuple[Path | None, dict[str, Any] | None, str | None]:
    from sentinel_xdr_migration.packaging import _read_json, _solution_data_file

    data_dir = solution_root / "Data"
    if not data_dir.is_dir():
        return None, None, None
    try:
        data_file = _solution_data_file(data_dir)
    except ValueError as exc:
        return data_dir, None, str(exc)
    try:
        doc = _read_json(data_file)
        return data_file, doc, None
    except ValueError as exc:
        return data_file, None, str(exc)


def _find_saved_search_dependency(
    resources: list[dict[str, Any]],
    variables: dict[str, Any],
    function_alias: str,
) -> tuple[dict[str, Any] | None, str | None, str | None]:
    """Locate the savedSearches resource for function_alias and compute its expected dependsOn expression."""
    saved = [
        res
        for res in resources
        if isinstance(res, dict)
        and str(res.get("type") or "").lower()
        == "microsoft.operationalinsights/workspaces/savedsearches"
        and isinstance(res.get("properties"), dict)
        and res["properties"].get("functionAlias") == function_alias
    ]
    if len(saved) != 1:
        return (
            None,
            None,
            f"Required workspace function '{function_alias}' must have exactly one emitted "
            f"Microsoft.OperationalInsights/workspaces/savedSearches resource in Package/mainTemplate.json "
            f"(found {len(saved)})",
        )
    resource = saved[0]
    if "condition" in resource or "copy" in resource:
        return (
            resource,
            None,
            f"Required workspace function '{function_alias}' savedSearches resource must be unconditional",
        )
    name = resource.get("name")
    if not isinstance(name, str) or not name:
        return (
            resource,
            None,
            f"Required workspace function '{function_alias}' savedSearches resource has no valid name",
        )

    dependency: str | None = None
    parser_match = re.fullmatch(
        r"\[variables\(\s*'(parserObject([1-9][0-9]*))'\s*\)\.(?:_?parserName\2|_parserId\2)\]",
        name,
    )
    if parser_match:
        parser_object_name, parser_index = parser_match.groups()
        parser_object = variables.get(parser_object_name) if isinstance(variables, dict) else None
        if not isinstance(parser_object, dict):
            return (
                resource,
                None,
                f"Invalid required savedSearch ARM identity for '{function_alias}': missing variable {parser_object_name}",
            )
        parser_id = parser_object.get(f"_parserId{parser_index}")
        if not isinstance(parser_id, str) or not parser_id.strip():
            return (
                resource,
                None,
                f"Invalid required savedSearch ARM identity for '{function_alias}': missing _parserId{parser_index}",
            )
        dependency = f"[variables('{parser_object_name}')._parserId{parser_index}]"
    elif re.match(r"\A\[variables\(\s*'parserObject", name):
        return (
            resource,
            None,
            f"Invalid required savedSearch ARM identity for '{function_alias}': {name}",
        )
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
                return (
                    resource,
                    None,
                    f"Invalid required savedSearch ARM identity for '{function_alias}': {name}",
                )
            argument = name[1:-1]
        else:
            if len(name.split("/")) != 2 or not all(name.split("/")):
                return (
                    resource,
                    None,
                    f"Required savedSearch identity for '{function_alias}' must include workspace and resource name",
                )
            argument = "'" + name.replace("'", "''") + "'"
        dependency = f"[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', {argument})]"

    return resource, dependency, None


def _all_known_dependency_tokens(
    resources: list[dict[str, Any]],
    variables: dict[str, Any],
) -> set[str]:
    """Collect valid ARM dependency expressions that resolve to resources in mainTemplate.json."""
    valid: set[str] = set()
    has_content_packages = any(
        isinstance(res, dict)
        and str(res.get("type") or "").lower()
        == "microsoft.operationalinsights/workspaces/providers/contentpackages"
        for res in resources
    )
    if has_content_packages:
        valid.add(CONTENT_PACKAGE_EXTENSION_DEP)
        valid.add(
            "[resourceId('Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
        )

    for res in resources:
        if not isinstance(res, dict):
            continue
        res_type = str(res.get("type") or "")
        res_name = str(res.get("name") or "")
        if res_type and res_name:
            valid.add(f"[resourceId('{res_type}', '{res_name}')]")
            if res_name.startswith("[") and res_name.endswith("]"):
                valid.add(f"[resourceId('{res_type}', {res_name[1:-1]})]")
            if "/" in res_name:
                parts = [f"'{p}'" for p in res_name.split("/")]
                valid.add(f"[resourceId('{res_type}', {', '.join(parts)})]")
        if res_type.lower() == "microsoft.operationalinsights/workspaces/savedsearches":
            alias = (res.get("properties") or {}).get("functionAlias") if isinstance(res.get("properties"), dict) else None
            if isinstance(alias, str) and alias:
                _, dep, err = _find_saved_search_dependency(resources, variables, alias)
                if dep and not err:
                    valid.add(dep)

    if isinstance(variables, dict):
        for var_name, var_value in variables.items():
            idx_match = re.fullmatch(r"parserObject([1-9][0-9]*)", str(var_name))
            if idx_match and isinstance(var_value, dict):
                idx = idx_match.group(1)
                parser_id = var_value.get(f"_parserId{idx}")
                parser_name = var_value.get(f"_parserName{idx}") or var_value.get(f"parserName{idx}")
                if isinstance(parser_id, str) and parser_id.strip():
                    # Verify a savedSearches resource actually uses this parserObject
                    if any(
                        isinstance(res, dict)
                        and str(res.get("type") or "").lower()
                        == "microsoft.operationalinsights/workspaces/savedsearches"
                        and res.get("name") in (
                            parser_name,
                            f"[variables('{var_name}')._parserName{idx}]",
                            f"[variables('{var_name}').parserName{idx}]",
                            f"[variables('{var_name}')._parserId{idx}]",
                        )
                        for res in resources
                    ):
                        valid.add(f"[variables('{var_name}')._parserId{idx}]")

    return valid


def _is_custom_detection_install_deployment(res: Any) -> bool:
    if not isinstance(res, dict):
        return False
    if str(res.get("type") or "").casefold() != "microsoft.resources/deployments":
        return False
    name = str(res.get("name") or "")
    if name.startswith("CustomDetection-") or "-CD-" in name:
        return True
    props = res.get("properties")
    if isinstance(props, dict) and isinstance(props.get("template"), dict):
        inner_res = props["template"].get("resources")
        if isinstance(inner_res, list) and any(
            isinstance(child, dict)
            and str(child.get("type") or "").casefold() == "microsoft.security/detectionrules"
            for child in inner_res
        ):
            return True
    return False


def validate_solution_xdr_detections(
    solution_root: Path,
    content_root: Path,
    toolkit_root: Path,
) -> dict[str, Any]:
    from sentinel_xdr_migration.converter import (
        custom_detail_binding_warnings,
        validate_document,
        xdr_detection_files,
    )
    from sentinel_xdr_migration.packaging import _read_json, _value, _xdr_references

    xdr_dir = solution_root / "XDR Detections"
    authored_files = xdr_detection_files(xdr_dir) if xdr_dir.is_dir() else []

    data_file, data_doc, data_err = _load_solution_data(solution_root)
    has_data_xdr_key = bool(
        isinstance(data_doc, dict)
        and any(
            key.casefold() in {"xdr detections", "custom detections"}
            for key in data_doc
        )
    )

    main_template_path = solution_root / "Package" / "mainTemplate.json"
    main_template_doc: dict[str, Any] | None = None
    has_packaged_custom_detections = False
    if main_template_path.is_file():
        try:
            main_template_doc = _read_json(main_template_path)
            mt_resources = main_template_doc.get("resources") or []
            mt_params = main_template_doc.get("parameters") or {}
            has_packaged_custom_detections = (
                "DeployCustomDetection" in mt_params
                or any(
                    isinstance(r, dict)
                    and (
                        _is_custom_detection_install_deployment(r)
                        or (
                            isinstance(r.get("properties"), dict)
                            and str(r["properties"].get("contentKind") or "").casefold()
                            == "customdetection"
                        )
                    )
                    for r in (mt_resources if isinstance(mt_resources, list) else [])
                )
            )
        except ValueError:
            main_template_doc = None

    applicable = bool(authored_files or has_data_xdr_key or has_packaged_custom_detections)
    if not applicable:
        return {
            "applicable": False,
            "liveKqlSkipped": False,
            "results": [
                {
                    "validator": "XDR Detection",
                    "filePath": _rel_path(xdr_dir, content_root),
                    "passed": True,
                    "skipped": True,
                    "skipReason": "No XDR Detections or packaged CustomDetection resources found in solution",
                }
            ],
        }

    results: list[dict[str, Any]] = []
    seen_ids: dict[str, list[Path]] = {}
    parsed_docs: dict[Path, dict[str, Any]] = {}

    for path in authored_files:
        file_errors: list[str] = []
        file_warnings: list[str] = []
        try:
            raw_text = path.read_text(encoding="utf-8-sig")
            if any(ord(ch) > 127 for ch in raw_text):
                file_errors.append("XDR Detection YAML contains non-ASCII characters")
            loaded = yaml.safe_load(raw_text)
            if not isinstance(loaded, dict):
                file_errors.append("XDR Detection YAML must contain a mapping object")
                document: dict[str, Any] = {}
            else:
                document = loaded
        except (OSError, yaml.YAMLError) as exc:
            file_errors.append(f"Invalid YAML syntax: {exc}")
            document = {}

        if document:
            parsed_docs[path] = document
            file_errors.extend(validate_document(document))
            file_warnings.extend(custom_detail_binding_warnings(document))

            provenance = document.get("contentProvenance")
            if isinstance(provenance, dict):
                if provenance.get("dependencyReviewRequired") is not False:
                    file_errors.append(
                        "contentProvenance.dependencyReviewRequired must be false "
                        "(dependency review is unresolved)"
                    )
                conversion = provenance.get("conversion")
                if isinstance(conversion, dict):
                    if conversion.get("status") != "converted":
                        file_errors.append(
                            f"contentProvenance.conversion.status must be 'converted', "
                            f"got {conversion.get('status')!r}"
                        )
                    if conversion.get("reviewRequired") is not False:
                        reasons = conversion.get("reviewReasons") or []
                        detail = f": {'; '.join(map(str, reasons))}" if reasons else ""
                        file_errors.append(
                            f"contentProvenance.conversion.reviewRequired must be false "
                            f"(conversion review is unresolved{detail})"
                        )
                source = provenance.get("source")
                if isinstance(source, dict):
                    source_rel = source.get("path")
                    if isinstance(source_rel, str) and source_rel.strip():
                        normalized_source = source_rel.replace("\\", "/")
                        source_candidate = (solution_root / normalized_source).resolve()
                        if not source_candidate.is_relative_to(solution_root.resolve()):
                            file_errors.append(
                                f"contentProvenance.source.path resolves outside solution: {source_rel!r}"
                            )
                        elif not source_candidate.is_file():
                            file_errors.append(
                                f"contentProvenance.source.path does not exist in solution: {source_rel!r}"
                            )
                        else:
                            try:
                                src_doc = yaml.safe_load(
                                    source_candidate.read_text(encoding="utf-8-sig")
                                )
                                if isinstance(src_doc, dict):
                                    src_id = str(src_doc.get("id") or "")
                                    src_query = str(src_doc.get("query") or "")
                                    expected_sha = hashlib.sha256(
                                        src_query.encode("utf-8")
                                    ).hexdigest()
                                    if src_id and src_id != str(source.get("id") or ""):
                                        file_errors.append(
                                            f"contentProvenance.source.id {source.get('id')!r} does not "
                                            f"match source analytic rule id {src_id!r}"
                                        )
                                    if expected_sha != str(source.get("querySha256") or ""):
                                        file_errors.append(
                                            "contentProvenance.source.querySha256 is stale and does not "
                                            "match the current source analytic rule query"
                                        )
                            except (OSError, yaml.YAMLError) as exc:
                                file_errors.append(
                                    f"Failed to read source analytic rule {source_rel!r}: {exc}"
                                )

            detection_id = (
                (document.get("properties") or {}).get("id")
                if isinstance(document.get("properties"), dict)
                else None
            )
            if isinstance(detection_id, str) and detection_id:
                seen_ids.setdefault(detection_id.casefold(), []).append(path)

        results.append(
            {
                "validator": "XDR Detection",
                "filePath": _rel_path(path, content_root),
                "passed": len(file_errors) == 0,
                "error": "; ".join(dict.fromkeys(file_errors)) if file_errors else None,
                "warnings": file_warnings,
            }
        )

    for det_id, paths in seen_ids.items():
        if len(paths) > 1:
            dup_msg = f"duplicate Custom Detection id {det_id!r}"
            for item in results:
                if item["filePath"] in {_rel_path(p, content_root) for p in paths}:
                    item["passed"] = False
                    item["error"] = (
                        f"{item['error']}; {dup_msg}" if item.get("error") else dup_msg
                    )

    # Validate Data/*.json XDR Detections references
    selected_xdr_files: list[Path] = []
    if data_err and data_file is not None:
        results.append(
            {
                "validator": "XDR Detection",
                "filePath": _rel_path(data_file, content_root),
                "passed": False,
                "error": data_err,
            }
        )
    elif data_doc is not None and data_file is not None:
        try:
            selected_xdr_files = _xdr_references(solution_root, data_doc)
        except ValueError as exc:
            # Check if an applied package-selection plan intentionally excluded all XDR detections
            selection_plan_path = solution_root / "Logs" / "package-selection.json"
            excluded_by_plan = False
            if selection_plan_path.is_file() and not has_data_xdr_key:
                try:
                    plan_doc = json.loads(selection_plan_path.read_text(encoding="utf-8"))
                    if (
                        isinstance(plan_doc, dict)
                        and isinstance(plan_doc.get("selection"), dict)
                        and plan_doc["selection"].get("xdrDetections") == []
                    ):
                        excluded_by_plan = True
                except (OSError, json.JSONDecodeError):
                    pass
            if not excluded_by_plan:
                results.append(
                    {
                        "validator": "XDR Detection",
                        "filePath": _rel_path(data_file, content_root),
                        "passed": False,
                        "error": str(exc),
                    }
                )
    else:
        selected_xdr_files = list(authored_files)

    # Validate Package/mainTemplate.json CustomDetection resources if present
    if main_template_doc is not None and (selected_xdr_files or has_packaged_custom_detections):
        pkg_errors = _validate_packaged_custom_detections(
            main_template_doc,
            selected_xdr_files,
            parsed_docs,
        )
        if pkg_errors or not authored_files:
            results.append(
                {
                    "validator": "XDR Detection",
                    "filePath": _rel_path(main_template_path, content_root),
                    "passed": len(pkg_errors) == 0,
                    "error": "; ".join(dict.fromkeys(pkg_errors)) if pkg_errors else None,
                }
            )

    return {
        "applicable": True,
        "liveKqlSkipped": True,
        "liveKqlSkipReason": (
            "Live Advanced Hunting KQL validation for XDR Detections requires an "
            "approved Defender XDR / Log Analytics workspace and is skipped in offline local validation"
        ),
        "fileCount": len(authored_files),
        "results": results,
    }


def _validate_packaged_custom_detections(
    template: dict[str, Any],
    selected_xdr_files: list[Path],
    parsed_docs: dict[Path, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    resources = template.get("resources")
    if not isinstance(resources, list):
        return ["Package/mainTemplate.json resources must be an array"]
    variables = template.get("variables") if isinstance(template.get("variables"), dict) else {}
    parameters = template.get("parameters") if isinstance(template.get("parameters"), dict) else {}

    installs = [
        r
        for r in resources
        if _is_custom_detection_install_deployment(r)
    ]
    registrations = [
        r
        for r in resources
        if isinstance(r, dict)
        and str(r.get("type") or "").casefold()
        == "microsoft.operationalinsights/workspaces/providers/contenttemplates"
        and isinstance(r.get("properties"), dict)
        and str(r["properties"].get("contentKind") or "").casefold() == "customdetection"
    ]

    if selected_xdr_files:
        deploy_param = parameters.get("DeployCustomDetection")
        if (
            not isinstance(deploy_param, dict)
            or deploy_param.get("type") != "bool"
            or deploy_param.get("defaultValue") is not False
        ):
            errors.append(
                "Package/mainTemplate.json must declare boolean parameter "
                "DeployCustomDetection with defaultValue=false when XDR Detections are packaged"
            )
    elif "DeployCustomDetection" in parameters and not installs and not registrations:
        errors.append(
            "Package/mainTemplate.json declares DeployCustomDetection without any packaged XDR Detections"
        )

    if selected_xdr_files and (
        len(installs) != len(selected_xdr_files)
        or len(registrations) != len(selected_xdr_files)
    ):
        errors.append(
            f"Package/mainTemplate.json CustomDetection install/registration count "
            f"({len(installs)} install(s), {len(registrations)} registration(s)) "
            f"differs from selected XDR Detections ({len(selected_xdr_files)})"
        )

    known_deps = _all_known_dependency_tokens(resources, variables)

    for install in installs:
        name = str(install.get("name") or "<unnamed>")
        if install.get("condition") != "[parameters('DeployCustomDetection')]":
            errors.append(
                f"CustomDetection deployment '{name}' must have condition "
                "\"[parameters('DeployCustomDetection')]\""
            )
        deps = install.get("dependsOn")
        if not isinstance(deps, list) or not deps:
            errors.append(f"CustomDetection deployment '{name}' is missing dependsOn")
        else:
            for dep in deps:
                if isinstance(dep, str) and dep not in known_deps:
                    errors.append(
                        f"CustomDetection deployment '{name}' has unresolved dependsOn reference: {dep}"
                    )

    for reg in registrations:
        reg_name = str(reg.get("name") or "<unnamed>")
        if reg.get("condition") != "[parameters('DeployCustomDetection')]":
            errors.append(
                f"CustomDetection registration '{reg_name}' must have condition "
                "\"[parameters('DeployCustomDetection')]\""
            )
        deps = reg.get("dependsOn")
        if not isinstance(deps, list) or not deps:
            errors.append(f"CustomDetection registration '{reg_name}' is missing dependsOn")
        else:
            for dep in deps:
                if isinstance(dep, str) and dep not in known_deps:
                    errors.append(
                        f"CustomDetection registration '{reg_name}' has unresolved dependsOn reference: {dep}"
                    )

    return errors


def validate_solution_xdr_workbooks(
    solution_root: Path,
    content_root: Path,
    toolkit_root: Path,
) -> dict[str, Any]:
    from sentinel_xdr_migration.packaging import _read_json, _value
    from sentinel_xdr_migration.workbook_dependencies import dependency_validation_errors
    from sentinel_xdr_migration.workbook_functions import (
        function_definition,
        function_parameters,
        validate_functions,
    )
    from sentinel_xdr_migration.workbooks import (
        _content_release,
        selected_workbook_files,
        validate_workbooks,
    )

    wb_dir = solution_root / "XDR Workbooks"
    authored_files = (
        sorted(p for p in wb_dir.rglob("*.json") if p.is_file())
        if wb_dir.is_dir()
        else []
    )

    data_file, data_doc, data_err = _load_solution_data(solution_root)
    has_data_wb_key = bool(
        isinstance(data_doc, dict)
        and any(key.casefold() == "xdr workbooks" for key in data_doc)
    )

    main_template_path = solution_root / "Package" / "mainTemplate.json"
    main_template_doc: dict[str, Any] | None = None
    has_packaged_defender_workbooks = False
    if main_template_path.is_file():
        try:
            main_template_doc = _read_json(main_template_path)
            mt_resources = main_template_doc.get("resources") or []
            mt_params = main_template_doc.get("parameters") or {}
            has_packaged_defender_workbooks = (
                "DeployDefenderWorkbook" in mt_params
                or any(
                    isinstance(r, dict)
                    and (
                        str(r.get("name") or "").startswith("DefenderWorkbook-")
                        or (
                            isinstance(r.get("properties"), dict)
                            and str(r["properties"].get("contentKind") or "")
                            == "DefenderWorkbook"
                        )
                    )
                    for r in (mt_resources if isinstance(mt_resources, list) else [])
                )
            )
        except ValueError:
            main_template_doc = None

    applicable = bool(authored_files or has_data_wb_key or has_packaged_defender_workbooks)
    if not applicable:
        return {
            "applicable": False,
            "liveKqlSkipped": False,
            "results": [
                {
                    "validator": "XDR Workbook",
                    "filePath": _rel_path(wb_dir, content_root),
                    "passed": True,
                    "skipped": True,
                    "skipReason": "No XDR Workbooks or packaged DefenderWorkbook resources found in solution",
                }
            ],
        }

    results: list[dict[str, Any]] = []
    schema_path = (
        toolkit_root
        / "Tools"
        / "SentinelToXDRMigration"
        / "schema"
        / "xdr-workbook.schema.json"
    )
    workbook_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_validator = Draft202012Validator(workbook_schema)

    valid_json_files: list[Path] = []
    parsed_workbooks: dict[Path, dict[str, Any]] = {}
    for path in authored_files:
        try:
            raw_text = path.read_text(encoding="utf-8-sig")
            loaded = json.loads(raw_text)
            if not isinstance(loaded, dict):
                results.append(
                    {
                        "validator": "XDR Workbook",
                        "filePath": _rel_path(path, content_root),
                        "passed": False,
                        "error": "XDR Workbook JSON must contain a top-level object",
                    }
                )
            else:
                valid_json_files.append(path)
                parsed_workbooks[path] = loaded
        except (OSError, json.JSONDecodeError) as exc:
            results.append(
                {
                    "validator": "XDR Workbook",
                    "filePath": _rel_path(path, content_root),
                    "passed": False,
                    "error": f"Invalid JSON syntax: {exc}",
                }
            )

    if len(valid_json_files) == len(authored_files) and valid_json_files:
        try:
            wb_summary = validate_workbooks(solution_root, selected_only=False)
            for item in wb_summary.get("results", []):
                rel_item_path = str(item.get("path") or "")
                item_errors = list(item.get("errors") or [])
                # Ignore synthetic "Source workbook has no authored candidate." for unconverted legacy Workbooks
                if (
                    rel_item_path.startswith("Workbooks/")
                    and item_errors == ["Source workbook has no authored candidate."]
                ):
                    continue
                target_path = solution_root / rel_item_path
                # Run explicit schema check against Tools/SentinelToXDRMigration/schema/xdr-workbook.schema.json
                doc = parsed_workbooks.get(target_path)
                if doc is not None:
                    for err in schema_validator.iter_errors(doc):
                        loc = "/".join(map(str, err.absolute_path)) or "<root>"
                        msg = f"{loc}: {err.message}"
                        if msg not in item_errors:
                            item_errors.append(msg)
                results.append(
                    {
                        "validator": "XDR Workbook",
                        "filePath": _rel_path(target_path, content_root),
                        "passed": len(item_errors) == 0,
                        "error": "; ".join(dict.fromkeys(item_errors)) if item_errors else None,
                    }
                )
        except Exception as exc:
            # Per-file fallback if validate_workbooks raised an unexpected exception
            for path in valid_json_files:
                doc = parsed_workbooks[path]
                file_errors = [
                    f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
                    for e in schema_validator.iter_errors(doc)
                ]
                file_errors.extend(dependency_validation_errors(doc))
                file_errors.append(str(exc))
                results.append(
                    {
                        "validator": "XDR Workbook",
                        "filePath": _rel_path(path, content_root),
                        "passed": False,
                        "error": "; ".join(dict.fromkeys(file_errors)),
                    }
                )
    elif valid_json_files:
        # Some files had invalid JSON so validate_workbooks(solution_root) would fail on _document;
        # still validate all valid JSON files against schema, dependencies, and workspace functions.
        for path in valid_json_files:
            doc = parsed_workbooks[path]
            file_errors = [
                f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
                for e in schema_validator.iter_errors(doc)
            ]
            file_errors.extend(dependency_validation_errors(doc))
            provenance = doc.get("contentProvenance")
            if isinstance(provenance, dict):
                fn_records = provenance.get("requiredWorkspaceFunctions", [])
                if isinstance(fn_records, list) and fn_records:
                    try:
                        validate_functions(solution_root, fn_records)
                    except (ValueError, TypeError) as exc:
                        file_errors.append(str(exc))
            results.append(
                {
                    "validator": "XDR Workbook",
                    "filePath": _rel_path(path, content_root),
                    "passed": len(file_errors) == 0,
                    "error": "; ".join(dict.fromkeys(file_errors)) if file_errors else None,
                }
            )

    # Validate Data/*.json XDR Workbooks selection
    selected_wb_files: list[Path] = []
    if data_err and data_file is not None:
        results.append(
            {
                "validator": "XDR Workbook",
                "filePath": _rel_path(data_file, content_root),
                "passed": False,
                "error": data_err,
            }
        )
    elif data_doc is not None and data_file is not None:
        if _value(data_doc, "XDR Workbooks") is None:
            if authored_files:
                results.append(
                    {
                        "validator": "XDR Workbook",
                        "filePath": _rel_path(data_file, content_root),
                        "passed": False,
                        "error": "solution Data is missing an explicit XDR Workbooks array",
                    }
                )
        else:
            try:
                selected_wb_files = selected_workbook_files(solution_root)
            except ValueError as exc:
                results.append(
                    {
                        "validator": "XDR Workbook",
                        "filePath": _rel_path(data_file, content_root),
                        "passed": False,
                        "error": str(exc),
                    }
                )
    else:
        selected_wb_files = list(authored_files)

    # Validate Package/mainTemplate.json DefenderWorkbook-* resources and dependsOn integrity
    if main_template_doc is not None and (
        selected_wb_files or authored_files or has_packaged_defender_workbooks
    ):
        expected_files = selected_wb_files if selected_wb_files else authored_files
        pkg_errors = _validate_packaged_defender_workbooks(
            solution_root,
            main_template_path,
            main_template_doc,
            expected_files,
            parsed_workbooks,
            workbook_schema,
        )
        if pkg_errors or not authored_files:
            results.append(
                {
                    "validator": "XDR Workbook",
                    "filePath": _rel_path(main_template_path, content_root),
                    "passed": len(pkg_errors) == 0,
                    "error": "; ".join(dict.fromkeys(pkg_errors)) if pkg_errors else None,
                }
            )

    return {
        "applicable": True,
        "liveKqlSkipped": True,
        "liveKqlSkipReason": (
            "Live Advanced Hunting / Defender Workbook query & portal rendering validation "
            "requires an approved live tenant/workspace and is skipped in offline local validation"
        ),
        "fileCount": len(authored_files),
        "results": results,
    }


def _validate_packaged_defender_workbooks(
    solution_root: Path,
    main_template_path: Path,
    template: dict[str, Any],
    expected_files: list[Path],
    parsed_workbooks: dict[Path, dict[str, Any]],
    workbook_schema: dict[str, Any],
) -> list[str]:
    from sentinel_xdr_migration.packaging import (
        _verify_workbook_package,
        validate_v31_target_version,
    )
    from sentinel_xdr_migration.workbook_dependencies import dependency_validation_errors
    from sentinel_xdr_migration.workbook_functions import (
        function_definition,
        function_parameters,
        validate_functions,
    )
    from sentinel_xdr_migration.workbooks import _content_release

    errors: list[str] = []
    resources = template.get("resources")
    if not isinstance(resources, list):
        return ["Package/mainTemplate.json resources must be an array"]
    variables = template.get("variables") if isinstance(template.get("variables"), dict) else {}
    parameters = template.get("parameters") if isinstance(template.get("parameters"), dict) else {}

    installs = [
        row
        for row in resources
        if isinstance(row, dict)
        and row.get("type") == "Microsoft.Resources/deployments"
        and str(row.get("name") or "").startswith("DefenderWorkbook-")
    ]
    registrations = [
        row
        for row in resources
        if isinstance(row, dict)
        and isinstance(row.get("properties"), dict)
        and row["properties"].get("contentKind") == "DefenderWorkbook"
    ]
    packages = [
        row
        for row in resources
        if isinstance(row, dict)
        and row.get("type")
        == "Microsoft.OperationalInsights/workspaces/providers/contentPackages"
    ]

    has_any_wb = bool(expected_files or installs or registrations)
    if has_any_wb:
        deploy_param = parameters.get("DeployDefenderWorkbook")
        if (
            not isinstance(deploy_param, dict)
            or deploy_param.get("type") != "bool"
            or deploy_param.get("defaultValue") is not False
        ):
            errors.append(
                "Package/mainTemplate.json must declare boolean parameter "
                "DeployDefenderWorkbook with defaultValue=false when Defender Workbooks are packaged"
            )

    if len(installs) != len(registrations):
        errors.append(
            f"Defender workbook install count ({len(installs)}) differs from "
            f"contentTemplates registration count ({len(registrations)}) in Package/mainTemplate.json"
        )

    if expected_files and (
        len(installs) != len(expected_files) or len(registrations) != len(expected_files)
    ):
        errors.append(
            f"Defender workbook install/registration count ({len(installs)} install(s), "
            f"{len(registrations)} registration(s)) differs from selection ({len(expected_files)})"
        )

    if not installs and not registrations:
        return errors

    if len(packages) != 1:
        errors.append(
            f"Defender workbook packaging requires exactly one contentPackages resource "
            f"in Package/mainTemplate.json (found {len(packages)})"
        )

    package_id = variables.get("solutionId")
    version = variables.get("_solutionVersion")
    try:
        validate_v31_target_version(version)
    except ValueError as exc:
        errors.append(f"Package/mainTemplate.json _solutionVersion invalid: {exc}")
    if not isinstance(package_id, str) or not package_id or package_id.startswith("["):
        errors.append("Defender workbook package identity (variables.solutionId) must be resolved")

    known_deps = _all_known_dependency_tokens(resources, variables)

    # Check every install & registration resource structurally (works both with and without authored XDR Workbooks)
    for install in installs:
        dep_name = str(install.get("name") or "")
        if install.get("apiVersion") != "2025-04-01":
            errors.append(
                f"Defender workbook deployment '{dep_name}' must use apiVersion '2025-04-01'"
            )
        if install.get("condition") != "[parameters('DeployDefenderWorkbook')]":
            errors.append(
                f"Defender workbook deployment '{dep_name}' must have condition "
                "\"[parameters('DeployDefenderWorkbook')]\""
            )
        props = install.get("properties") if isinstance(install.get("properties"), dict) else {}
        if (props.get("expressionEvaluationOptions") or {}).get("scope") != "inner":
            errors.append(
                f"Defender workbook deployment '{dep_name}' must set "
                "properties.expressionEvaluationOptions.scope to 'inner'"
            )
        inner = props.get("template") if isinstance(props.get("template"), dict) else {}
        if inner.get("languageVersion") != "2.0" or inner.get("imports") != {
            "MicrosoftSecurity": {"provider": "MicrosoftSecurity", "version": "1.0.0"}
        }:
            errors.append(
                f"Defender workbook deployment '{dep_name}' inner template must declare "
                "languageVersion '2.0' and MicrosoftSecurity 1.0.0 import"
            )
        inner_resources = inner.get("resources") if isinstance(inner.get("resources"), dict) else {}
        wb_res = inner_resources.get("workbook") if isinstance(inner_resources.get("workbook"), dict) else None
        if not wb_res or wb_res.get("import") != "MicrosoftSecurity" or wb_res.get("type") != "Microsoft.Security/workbooks@2026-06-01-preview":
            errors.append(
                f"Defender workbook deployment '{dep_name}' inner template must contain "
                "workbook resource of type 'Microsoft.Security/workbooks@2026-06-01-preview'"
            )
            content_id = None
        else:
            wb_props = wb_res.get("properties") if isinstance(wb_res.get("properties"), dict) else {}
            wb_id = wb_props.get("id")
            wb_name = wb_props.get("name")
            wb_content = wb_props.get("content") if isinstance(wb_props.get("content"), dict) else {}
            if not isinstance(wb_id, str) or not GUID_RE.fullmatch(wb_id):
                errors.append(
                    f"Defender workbook deployment '{dep_name}' properties.id must be a GUID"
                )
            if not isinstance(wb_name, str) or not wb_name.strip():
                errors.append(
                    f"Defender workbook deployment '{dep_name}' properties.name is required"
                )
            if "xdrMetadata" in wb_content:
                errors.append(
                    f"Defender workbook deployment '{dep_name}' inner content must not retain xdrMetadata"
                )
            inner_prov = wb_content.get("contentProvenance")
            content_id = inner_prov.get("contentId") if isinstance(inner_prov, dict) else None
            expected_quartet = {
                "packageId": package_id,
                "packageVersion": version,
                "contentId": content_id,
                "contentVersion": version,
            }
            if (
                not isinstance(inner_prov, dict)
                or not isinstance(content_id, str)
                or not GUID_RE.fullmatch(content_id)
                or inner_prov != expected_quartet
            ):
                errors.append(
                    f"Defender workbook deployment '{dep_name}' inner contentProvenance must "
                    "equal the 4-field deployment quartet (packageId, packageVersion, contentId, contentVersion)"
                )

        # Verify install dependsOn integrity
        install_deps = install.get("dependsOn")
        if not isinstance(install_deps, list) or not install_deps:
            errors.append(
                f"Defender workbook deployment '{dep_name}' must declare a non-empty dependsOn array"
            )
        else:
            if CONTENT_PACKAGE_EXTENSION_DEP not in install_deps:
                errors.append(
                    f"Defender workbook deployment '{dep_name}' dependsOn must include the "
                    "solution contentPackages extensionResourceId"
                )
            for dep in install_deps:
                if not isinstance(dep, str) or dep not in known_deps:
                    errors.append(
                        f"Defender workbook deployment '{dep_name}' has unresolved or invalid "
                        f"dependsOn reference: {dep!r}"
                    )

        # Cross-check matching registration resource
        if isinstance(content_id, str) and GUID_RE.fullmatch(content_id):
            actual_solution_name = next(
                (entry.name for entry in solution_root.parent.iterdir() if entry.name.lower() == solution_root.name.lower()),
                solution_root.name,
            )
            expected_dep_name = "DefenderWorkbook-" + hashlib.sha256(
                f"{actual_solution_name}/{content_id}".encode("utf-8")
            ).hexdigest()[:32]
            if dep_name != expected_dep_name:
                errors.append(
                    f"Defender workbook deployment name '{dep_name}' does not match "
                    f"deterministic name '{expected_dep_name}' for contentId '{content_id}'"
                )
            matching_regs = [
                r
                for r in registrations
                if (r.get("properties") or {}).get("contentId") == content_id
            ]
            if len(matching_regs) != 1:
                errors.append(
                    f"Defender workbook deployment '{dep_name}' (contentId '{content_id}') "
                    f"must have exactly one matching DefenderWorkbook contentTemplates registration "
                    f"(found {len(matching_regs)})"
                )
            else:
                reg = matching_regs[0]
                reg_props = reg.get("properties") or {}
                expected_reg_deps = [
                    f"[resourceId('Microsoft.Resources/deployments', '{dep_name}')]",
                    CONTENT_PACKAGE_EXTENSION_DEP,
                ]
                if reg.get("dependsOn") != expected_reg_deps:
                    errors.append(
                        f"Defender workbook registration for '{content_id}' has invalid dependsOn: "
                        f"expected {expected_reg_deps}, got {reg.get('dependsOn')}"
                    )
                reg_prov = reg_props.get("contentProvenance")
                if not isinstance(reg_prov, dict):
                    errors.append(
                        f"Defender workbook registration for '{content_id}' is missing properties.contentProvenance"
                    )
                else:
                    for req_key in (
                        "packageId",
                        "packageVersion",
                        "contentId",
                        "contentVersion",
                        "requiredWorkloads",
                        "requiredDataConnectors",
                        "requiredWorkspaceFunctions",
                    ):
                        if req_key not in reg_prov:
                            errors.append(
                                f"Defender workbook registration contentProvenance for '{content_id}' "
                                f"is missing required field '{req_key}'"
                            )
                    # Check requiredWorkspaceFunctions savedSearches & dependsOn
                    fn_records = reg_prov.get("requiredWorkspaceFunctions")
                    if isinstance(fn_records, list):
                        expected_parser_deps: list[str] = []
                        for fn_rec in fn_records:
                            if not isinstance(fn_rec, dict) or not isinstance(fn_rec.get("functionAlias"), str):
                                errors.append(
                                    f"Defender workbook registration for '{content_id}' contains "
                                    f"invalid requiredWorkspaceFunctions entry: {fn_rec!r}"
                                )
                                continue
                            _, dep_expr, dep_err = _find_saved_search_dependency(
                                resources, variables, fn_rec["functionAlias"]
                            )
                            if dep_err:
                                errors.append(dep_err)
                            elif dep_expr and dep_expr not in expected_parser_deps:
                                expected_parser_deps.append(dep_expr)
                        expected_install_deps = [
                            CONTENT_PACKAGE_EXTENSION_DEP,
                            *expected_parser_deps,
                        ]
                        if install.get("dependsOn") != expected_install_deps:
                            errors.append(
                                f"Workbook installation '{dep_name}' must depend on exact mandatory "
                                f"contentPackages and workspace functions: expected {expected_install_deps}, "
                                f"got {install.get('dependsOn')}"
                            )

    # If authored XDR Workbooks exist and all parsed as JSON, also run the full packaging verifier
    if expected_files and all(p in parsed_workbooks for p in expected_files):
        zip_candidates = sorted((solution_root / "Package").glob("*.zip"))
        if zip_candidates:
            try:
                _verify_workbook_package(
                    solution_root,
                    expected_files,
                    template,
                    zip_candidates[-1],
                )
            except (RuntimeError, ValueError) as exc:
                if str(exc) not in errors:
                    errors.append(str(exc))
        else:
            # Verify against authored files even when no .zip exists yet
            for path in expected_files:
                authored = parsed_workbooks[path]
                metadata = authored.get("xdrMetadata") or {}
                provenance = authored.get("contentProvenance") or {}
                content_id = metadata.get("contentId")
                fn_records = provenance.get("requiredWorkspaceFunctions") or []
                if isinstance(fn_records, list) and fn_records:
                    try:
                        validate_functions(solution_root, fn_records)
                    except (ValueError, TypeError) as exc:
                        if str(exc) not in errors:
                            errors.append(str(exc))
                    for fn_rec in fn_records:
                        if not isinstance(fn_rec, dict):
                            continue
                        alias = fn_rec.get("functionAlias")
                        src_path = fn_rec.get("sourcePath")
                        if not isinstance(alias, str) or not isinstance(src_path, str):
                            continue
                        saved_res, _, dep_err = _find_saved_search_dependency(
                            resources, variables, alias
                        )
                        if dep_err and dep_err not in errors:
                            errors.append(dep_err)
                        elif saved_res is not None:
                            try:
                                _, definition = function_definition(solution_root, src_path)
                                emitted_query = (saved_res.get("properties") or {}).get("query")
                                source_query = definition["FunctionQuery"]
                                if (
                                    not isinstance(emitted_query, str)
                                    or emitted_query not in (source_query, f"{source_query}\n")
                                    or (saved_res.get("properties") or {}).get("functionParameters", "")
                                    != function_parameters(definition)
                                ):
                                    errors.append(
                                        "Required workspace function must be unconditional and match current source"
                                    )
                            except (ValueError, KeyError) as exc:
                                errors.append(str(exc))
                if isinstance(content_id, str) and packages:
                    criteria = (
                        ((packages[0].get("properties") or {}).get("dependencies") or {}).get("criteria")
                        or []
                    )
                    wb_criteria = [row for row in criteria if isinstance(row, dict) and row.get("kind") == "DefenderWorkbook"]
                    if not any(row.get("contentId") == content_id for row in wb_criteria):
                        errors.append(
                            f"Defender workbook package dependency criteria is missing DefenderWorkbook '{content_id}'"
                        )

    return errors


def run_validation(
    *,
    content_root: Path,
    solution_paths: list[Path] | None = None,
    solution_path: str | None = None,
    files: list[str] | None = None,
    family: str = "all",
    toolkit_root: Path | None = None,
) -> dict[str, Any]:
    resolved_toolkit = (toolkit_root or Path(__file__).resolve().parents[2]).expanduser().resolve()
    resolved_content = content_root.expanduser().resolve()
    _setup_toolkit_imports(resolved_toolkit)

    solutions = (
        [p.expanduser().resolve() for p in solution_paths]
        if solution_paths is not None
        else _discover_solutions(resolved_content, solution_path, files)
    )
    all_results: list[dict[str, Any]] = []
    detections_reports: list[dict[str, Any]] = []
    workbooks_reports: list[dict[str, Any]] = []

    if not solutions:
        if family in ("all", "detections"):
            all_results.append(
                {
                    "validator": "XDR Detection",
                    "filePath": solution_path or "Solutions",
                    "passed": True,
                    "skipped": True,
                    "skipReason": "No solution scope found for XDR Detection validation",
                }
            )
        if family in ("all", "workbooks"):
            all_results.append(
                {
                    "validator": "XDR Workbook",
                    "filePath": solution_path or "Solutions",
                    "passed": True,
                    "skipped": True,
                    "skipReason": "No solution scope found for XDR Workbook validation",
                }
            )
    else:
        for sol in solutions:
            if family in ("all", "detections"):
                det_report = validate_solution_xdr_detections(sol, resolved_content, resolved_toolkit)
                detections_reports.append(det_report)
                all_results.extend(det_report["results"])
            if family in ("all", "workbooks"):
                wb_report = validate_solution_xdr_workbooks(sol, resolved_content, resolved_toolkit)
                workbooks_reports.append(wb_report)
                all_results.extend(wb_report["results"])

    failed = sum(1 for r in all_results if not r.get("passed", True) and not r.get("skipped", False))
    passed = sum(1 for r in all_results if r.get("passed", True) and not r.get("skipped", False))
    skipped = sum(1 for r in all_results if r.get("skipped", False))

    return {
        "summary": {
            "total": len(all_results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "detections": detections_reports,
        "workbooks": workbooks_reports,
        "results": all_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate XDR Detections and Defender Workbooks in a Sentinel solution."
    )
    parser.add_argument(
        "--toolkit-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Path to the toolkit repository root.",
    )
    parser.add_argument(
        "--content-root",
        default=None,
        help="Path to the content repository root (defaults to --toolkit-root).",
    )
    parser.add_argument(
        "--solution-path",
        default=None,
        help="Solution folder path (relative to --content-root or absolute).",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Specific file paths to validate.",
    )
    parser.add_argument(
        "--family",
        choices=("all", "detections", "workbooks"),
        default="all",
        help="Content family to validate.",
    )
    args = parser.parse_args()

    toolkit_root = Path(args.toolkit_root).expanduser().resolve()
    content_root = (
        Path(args.content_root).expanduser().resolve()
        if args.content_root
        else toolkit_root
    )
    payload = run_validation(
        content_root=content_root,
        solution_path=args.solution_path,
        files=args.files,
        family=args.family,
        toolkit_root=toolkit_root,
    )
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    return 1 if payload["summary"]["failed"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
