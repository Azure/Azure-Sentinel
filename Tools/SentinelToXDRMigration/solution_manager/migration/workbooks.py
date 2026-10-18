"""Offline, loss-aware solution workbook inventory, conversion and validation.

Reviewed resolutions bind exact original query templates, not scanner output.
Local validation establishes authored structure and freshness, never runtime,
installation, registration, UI fidelity or engine parity.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
from importlib.resources import files as package_files
import json
import os
from pathlib import Path, PurePosixPath
import re
from uuid import UUID, NAMESPACE_URL, uuid4, uuid5

from jsonschema import Draft202012Validator

from solution_manager import __version__
from solution_manager.core.artifacts import report_directory as resolve_report_directory
from solution_manager.authoring.dependencies import dependency_validation_errors, workload_records, telemetry_data_types
from solution_manager.migration._workbook_core import workbook, mapping_catalog

MANIFEST = "workbooks-manifest.json"
REPORT = "workbooks-validation.json"


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_json(text):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"Duplicate JSON key: {key}")
            value[key] = item
        return value
    return json.loads(text, object_pairs_hook=unique)


def _root(solution) -> Path:
    path = Path(solution).expanduser()
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_dir():
        raise ValueError("Solution must be an existing nonsymlink directory.")
    return path.resolve()


def _path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("Content references must use solution-relative POSIX paths.")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or not parts.parts or any(p in ("", "..", ".") for p in relative.split("/")):
        raise ValueError(f"Unsafe content reference: {relative}")
    path = root
    for part in parts.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Symlink content reference: {relative}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Content path escapes solution: {relative}")
    return path


def _files(root: Path, directory: str) -> list[Path]:
    base = _path(root, directory)
    if not base.exists():
        return []
    if not base.is_dir():
        raise ValueError(f"{directory} must be a directory.")
    paths = []
    for path in sorted(base.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink in workbook inventory: {path.relative_to(root)}")
        if path.is_file() and path.suffix.lower() == ".json":
            paths.append(path)
    folded = [p.relative_to(root).as_posix().casefold() for p in paths]
    if len(set(folded)) != len(folded):
        raise ValueError("Case-insensitive workbook path collision.")
    return paths


def _document(path: Path) -> dict:
    value = _load_json(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("Workbook JSON must be an object.")
    if value.get("version") != "Notebook/1.0" or not isinstance(value.get("items"), list):
        raise ValueError("Workbook must contain Notebook/1.0 version and items array.")
    return value


def _guid(value) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        return str(UUID(value))
    except ValueError:
        return None


def _identity(root: Path, relative: str, document: dict) -> str:
    metadata = document.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise ValueError("Workbook metadata must be an object.")
    candidates = [
        document.get("fromTemplateId"), document.get("id"),
        metadata.get("contentId"), metadata.get("workbookId"),
    ]
    for value in candidates:
        identity = _guid(value)
        if identity:
            return identity
    return str(uuid5(NAMESPACE_URL, f"sentinel-workbook:{root.name}:{relative}"))


def _catalog_template_path(value) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parts = PurePosixPath(value.strip().replace("\\", "/")).parts
    workbook_directory = next(
        (index for index in range(len(parts) - 1, -1, -1)
         if parts[index].casefold() == "workbooks"),
        None,
    )
    if workbook_directory is not None:
        parts = parts[workbook_directory + 1:]
    return PurePosixPath(*parts).as_posix().casefold() if parts else None


def _catalog_title(root: Path, source_path: Path, source: dict) -> str | None:
    solutions = next((parent for parent in root.parents
                      if parent.name.casefold() == "solutions"), None)
    if solutions is None:
        return None
    catalog_path = solutions.parent / "Workbooks" / "WorkbooksMetadata.json"
    if not catalog_path.exists():
        return None
    if catalog_path.is_symlink() or not catalog_path.is_file():
        raise ValueError(f"Workbook metadata catalog must be a regular file: {catalog_path}")
    try:
        catalog = _load_json(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError(f"Unable to read workbook metadata catalog {catalog_path}: {exc}") from exc
    if not isinstance(catalog, list) or any(not isinstance(entry, dict) for entry in catalog):
        raise ValueError(f"Workbook metadata catalog must be an array of objects: {catalog_path}")

    relative = source_path.relative_to(root).as_posix()
    source_relative = relative.removeprefix("Workbooks/").casefold()
    basename = PurePosixPath(relative).name.casefold()
    exact, basename_matches = [], []
    for entry in catalog:
        template = _catalog_template_path(entry.get("templateRelativePath"))
        if template == source_relative:
            exact.append(entry)
        elif template and PurePosixPath(template).name == basename:
            basename_matches.append(entry)
    matches = exact or basename_matches
    if not matches:
        return None
    if len(matches) > 1:
        metadata = source.get("metadata") or {}
        source_keys = {
            value.strip().casefold()
            for value in (
                source.get("fromTemplateId"),
                source.get("id"),
                metadata.get("contentId") if isinstance(metadata, dict) else None,
                metadata.get("workbookId") if isinstance(metadata, dict) else None,
            )
            if isinstance(value, str) and value.strip()
        }
        keyed_matches = [
            entry for entry in matches
            if isinstance(entry.get("workbookKey"), str)
            and entry["workbookKey"].strip().casefold() in source_keys
        ]
        if len(keyed_matches) == 1:
            matches = keyed_matches
        else:
            raise ValueError(
                f"Ambiguous workbook metadata catalog match for {relative}; "
                f"check templateRelativePath/workbookKey in {catalog_path}."
            )
    title = matches[0].get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(
            f"Workbook metadata catalog entry for {relative} has no title: {catalog_path}"
        )
    return title.strip()


def _display_name(root: Path, path: Path, source: dict) -> str:
    metadata = source.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise ValueError("Workbook metadata must be an object.")
    name = metadata.get("name")
    if isinstance(name, str) and name.strip():
        return name
    return _catalog_title(root, path, source) or path.stem


def inventory_workbooks(solution) -> list[dict]:
    root = _root(solution)
    result, identities = [], set()
    for path in _files(root, "Workbooks"):
        document = _document(path)
        relative = path.relative_to(root).as_posix()
        identity = _identity(root, relative, document)
        if identity in identities:
            raise ValueError(f"Duplicate workbook identity: {identity}")
        identities.add(identity)
        queries = []
        for surface in workbook.query_surfaces(document):
            raw = surface["node"]["query"]
            if not isinstance(raw, str):
                raise ValueError(f"Nonstring workbook query at {surface['path']}")
            queries.append({
                "path": surface["path"], "querySha256": workbook.query_hash(raw),
                "queryType": surface["queryType"], "resourceType": surface["resourceType"],
                "parameter": surface["parameter"],
            })
        result.append({"path": relative, "sha256": _sha(path.read_bytes()),
                       "identity": identity, "queries": queries})
    return result


def _solution_data(root: Path) -> dict:
    directory = _path(root, "Data")
    files = sorted(directory.glob("Solution_*.json")) if directory.exists() else []
    if len(files) != 1:
        raise ValueError("Expected exactly one Data/Solution_*.json.")
    path = _path(root, files[0].relative_to(root).as_posix())
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("Solution data must be an object.")
    return value


def selected_workbook_files(solution) -> list[Path]:
    """Return only explicit XDR Workbooks references; absence is not selection."""
    root = _root(solution)
    data = _solution_data(root)
    references = data.get("XDR Workbooks")
    if not isinstance(references, list):
        raise ValueError("An explicit XDR Workbooks selection array is required.")
    paths, seen = [], set()
    for reference in references:
        if not isinstance(reference, str) or not reference.startswith("XDR Workbooks/"):
            raise ValueError("Workbook selection must reference XDR Workbooks/ JSON content.")
        path = _path(root, reference)
        if path.suffix.lower() != ".json" or not path.is_file():
            raise ValueError(f"Missing workbook selection: {reference}")
        folded = reference.casefold()
        if folded in seen:
            raise ValueError(f"Duplicate workbook selection: {reference}")
        seen.add(folded)
        paths.append(path)
    return paths


def _release(data: dict, config: dict) -> str | None:
    from solution_manager.packaging.packaging import validate_v31_target_version
    value = config.get("targetVersion", data.get("Version", data.get("version")))
    try:
        return validate_v31_target_version(value)
    except ValueError:
        return None


def _content_release(value: str | None) -> str | None:
    if not isinstance(value, str) or not re.fullmatch(r"3\.[1-9]\d*\.(0|[1-9]\d*)", value):
        return None
    return value


def _dependencies(queries: list[dict], configured: dict | None, reviewed_sources=()) -> dict:
    targets, source_targets = set(), {}
    catalog = mapping_catalog.load_mapping_catalog()["tables"]
    for table in telemetry_data_types(reviewed_sources):
        source_targets[table] = catalog.get(table, {}).get("ahTable") or table
    for query in queries:
        contract = query.get("conversion")
        if not contract or query["status"] == "removed-scope-helper":
            continue
        for table in telemetry_data_types(contract["resolvedTables"]):
            target = catalog.get(table, {}).get("ahTable") or table
            source_targets[table] = target
            targets.add(target)
    records, unknown = workload_records(sorted(targets))
    settings = configured if configured is not None else {}
    if not isinstance(settings, dict):
        raise ValueError("Workbook dependencies must be an object.")
    records = deepcopy(settings.get("requiredWorkloads", records))
    connectors = settings.get("requiredDataConnectors")
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError("Workbook workload prerequisites must be object records.")
    if connectors is not None and not isinstance(connectors, list):
        raise ValueError("Workbook connector prerequisites must be an array.")
    reasons = []
    # Connector records must explicitly identify source tables; rewrite that
    # association to output names rather than guessing from a connector ID.
    output_connectors = []
    for connector in connectors if connectors is not None else []:
        if not isinstance(connector, dict) or not isinstance(connector.get("dataTypes"), list):
            raise ValueError("Workbook connector prerequisites require source dataTypes.")
        if any(table not in source_targets for table in connector["dataTypes"]):
            raise ValueError("Connector prerequisite references a table outside reviewed query sources.")
        output_connectors.append({
            **deepcopy(connector),
            "dataTypes": sorted({source_targets[t] for t in connector["dataTypes"]}),
        })
    declared = {t for record in records for t in record.get("dataTypes", [])
                if isinstance(t, str)} if all(isinstance(r.get("dataTypes"), list) for r in records) else set()
    if not targets <= declared:
        reasons.append("Output data types require reviewed workload mappings.")
    if unknown and "requiredWorkloads" not in settings:
        reasons.append("Unknown output workload: " + ", ".join(unknown))
    if any(r.get("workload") == "sentinel" for r in records) and connectors is None:
        reasons.append("Explicit source-associated Sentinel connector prerequisites required.")
    if settings.get("dependencyReviewRequired") is True:
        reasons.append("Reviewer deferred dependencies; explicit current review is required.")
    provenance = {"requiredWorkloads": records, "requiredDataConnectors": output_connectors,
                  "dependencyReviewRequired": bool(reasons)}
    errors = dependency_validation_errors({"contentProvenance": {
        **provenance, "dependencyReviewRequired": False}})
    if errors:
        raise ValueError("; ".join(errors))
    return {**provenance, "reviewReasons": reasons}


def _write(path: Path, content: bytes, previous: bytes | None) -> None:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Refusing symlink write.")
    if previous is None:
        with path.open("xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    else:
        staged = path.with_name(f".{path.name}.{uuid4().hex}.staged")
        try:
            with staged.open("xb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            if (any(p.is_symlink() for p in (path, *path.parents))
                    or not path.is_file() or path.read_bytes() != previous):
                raise ValueError("Workbook changed during conversion; refusing overwrite.")
            os.replace(staged, path)
        finally:
            if staged.exists():
                staged.unlink()


def convert_workbooks(solution, *, config=None, report_directory=None, overwrite=False) -> dict:
    root = _root(solution)
    inventory = inventory_workbooks(root)
    settings = deepcopy(config if config is not None else {})
    if not isinstance(settings, dict):
        raise ValueError("Workbook configuration must be an object.")
    if "targetVersion" in settings:
        from solution_manager.packaging.packaging import validate_v31_target_version
        validate_v31_target_version(settings["targetVersion"])
    resolutions = settings.get("workbookResolutions", {})
    dependencies = settings.get("workbookDependencies", {})
    if not isinstance(resolutions, dict) or not isinstance(dependencies, dict):
        raise ValueError("Workbook resolutions and dependencies must be objects.")
    sources = {row["path"] for row in inventory}
    if set(resolutions) - sources or set(dependencies) - sources:
        raise ValueError("Workbook configuration references missing source content.")
    from solution_manager.authoring.workbook_functions import validate_functions
    function_dependencies = {}
    for relative, configured in dependencies.items():
        if not isinstance(configured, dict):
            raise ValueError("Workbook dependencies must be an object.")
        function_dependencies[relative] = validate_functions(
            root, configured.get("requiredWorkspaceFunctions", []))
    version = _release(_solution_data(root), settings)
    output_dir = _path(root, "XDR Workbooks")
    _files(root, "XDR Workbooks")
    report_dir = (Path(report_directory).expanduser() if report_directory is not None
                  else resolve_report_directory(root, create=True))
    if any(p.is_symlink() for p in (report_dir, *report_dir.parents)):
        raise ValueError("Report directory must not use symlinks.")
    report_dir = report_dir.resolve()
    if report_dir == root or report_dir.is_relative_to(_path(root, "Workbooks")) or report_dir.is_relative_to(output_dir):
        raise ValueError("Reports must be outside workbook content directories.")
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest_file, report_file = report_dir / MANIFEST, report_dir / REPORT
    for path in (manifest_file, report_file):
        if path.is_symlink():
            raise ValueError("Report artifacts must not be symlinks.")
    previous_manifest = json.loads(manifest_file.read_bytes()) if manifest_file.exists() else {}
    previous_results = {r["sourceRelativePath"]: r for r in previous_manifest.get("results", [])}
    planned = []
    for row in inventory:
        path = _path(root, row["path"])
        source_bytes = path.read_bytes()
        if _sha(source_bytes) != row["sha256"]:
            raise ValueError("Source workbook changed during inventory.")
        source = _document(path)
        query_resolutions = resolutions.get(row["path"], {})
        if not isinstance(query_resolutions, dict):
            raise ValueError("Per-workbook resolutions must be an object.")
        if set(query_resolutions) - {q["path"] for q in row["queries"]}:
            raise ValueError("Workbook resolution references a missing query pointer.")
        functions = function_dependencies.get(row["path"], [])
        converted = workbook.convert_workbook(
            source, resolutions=query_resolutions,
            allowed_workspace_functions=[r["functionAlias"] for r in functions])
        target, report = converted["workbook"], converted["report"]
        used_functions = {name for q in report["queries"] for name in q.get("workspaceFunctions", [])}
        if used_functions != {r["functionAlias"] for r in functions}:
            report["issues"].append({"code": "workspace-function-coverage",
                                    "message": "Workspace prerequisites must match exact query aliases."})
        output_surfaces = {q["path"]: q for q in workbook.query_surfaces(target)}
        originals = {q["path"]: q["querySha256"] for q in row["queries"]}
        for query in report["queries"]:
            query["sourceSha256"] = originals[query["sourcePath"]]
            query["targetSha256"] = (workbook.query_hash(
                output_surfaces[query["outputPath"]]["node"]["query"])
                if query.get("outputPath") else None)
        reviewed_sources = set()
        for pointer, resolution in query_resolutions.items():
            if (isinstance(resolution, dict) and resolution.get("querySha256") == originals[pointer]
                    and isinstance(resolution.get("tables"), list) and resolution.get("evidence")
                    and all(isinstance(table, str) and table.strip() for table in resolution["tables"])):
                reviewed_sources.update(resolution["tables"])
        dependency = _dependencies(report["queries"], dependencies.get(row["path"]), reviewed_sources)
        if version is None:
            report["issues"].append({
                "path": "/xdrMetadata/version", "code": "release-version-required",
                "message": "Select targetVersion >=3.2.0 and <4.0.0; source release is unchanged."})
        canonical = row["identity"]
        instance = str(uuid5(NAMESPACE_URL, f"xdr-workbook-instance:{root.name}:{canonical}"))
        target["xdrMetadata"] = {
            "contentId": canonical, "instanceId": instance, "version": version,
            "schemaVersion": "1.0.0",
            "displayName": _display_name(root, path, source),
        }
        source_metadata = source.get("metadata") or {}
        target["contentProvenance"] = {
            "source": {"path": row["path"], "sha256": row["sha256"],
                       "contentId": (source.get("fromTemplateId") or source.get("id") or
                                     source_metadata.get("contentId") or source_metadata.get("workbookId")),
                       "originalMetadataVersion": source_metadata.get("version")},
            "conversion": {"tool": "sentinel-xdr-migration", "version": __version__,
                           "reviewRequired": bool(report["issues"]), "queries": report["queries"]},
            **{key: dependency[key] for key in (
                "requiredWorkloads", "requiredDataConnectors", "dependencyReviewRequired")},
        }
        if functions:
            target["contentProvenance"]["requiredWorkspaceFunctions"] = functions
        relative = "XDR Workbooks/" + row["path"].removeprefix("Workbooks/")
        output = _path(root, relative)
        content = (json.dumps(target, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        old = output.read_bytes() if output.exists() else None
        issues = report["issues"] + [
            {"code": "dependency-review", "message": message}
            for message in dependency["reviewReasons"]]
        status = "blocked" if issues else "converted"
        if old is not None and old != content:
            receipt = previous_results.get(row["path"])
            managed_hash = (receipt.get("managedOutputSha256", receipt.get("outputSha256"))
                            if receipt else None)
            if not overwrite or not receipt or managed_hash != _sha(old):
                status = "conflict"
                issues.append({"code": "output-conflict",
                               "message": "Existing edited/unbound workbook retained; explicit review required."})
        result = {
            "sourceRelativePath": row["path"], "outputRelativePath": relative,
            "sourceSha256": row["sha256"], "outputSha256": _sha(old if status == "conflict" else content),
            "status": status, "reviewRequired": bool(issues), "identity": canonical,
            "managedOutputSha256": (
                previous_results.get(row["path"], {}).get(
                    "managedOutputSha256", previous_results.get(row["path"], {}).get("outputSha256"))
                if status == "conflict" else _sha(content)),
            "instanceId": instance, "issues": issues, "queries": report["queries"],
            "gates": report["gates"], "validation": report["validation"],
        }
        planned.append((path, source_bytes, output, content, old, result))
    # Complete all conflict/malformed-input checks before touching content.
    for path, source_bytes, output, content, old, result in planned:
        if path.read_bytes() != source_bytes:
            raise ValueError("Source changed before conversion commit.")
        if result["status"] != "conflict" and old != content:
            output.parent.mkdir(parents=True, exist_ok=True)
            _write(output, content, old)
    results = [p[-1] for p in planned]
    summary = {
        "total": len(results), "converted": sum(r["status"] == "converted" for r in results),
        "blocked": sum(r["status"] != "converted" for r in results), "results": results,
        "manifestPath": str(manifest_file), "reportPath": str(report_file),
    }
    manifest = {"schemaVersion": "1.0.0", "scope": "solution", "inventory": inventory,
                **summary}
    for output, value in ((manifest_file, manifest), (report_file, {
        **summary, "validation": {"localStructureOnly": True, "runtime": "not-run", "ui": "not-run"}})):
        _write(output, (json.dumps(value, indent=2) + "\n").encode(),
               output.read_bytes() if output.exists() else None)
    return summary


def authored_schema_errors(document):
    schema = json.loads(package_files("solution_manager.migration._workbook_core").joinpath(
        "data/xdr-workbook.schema.json").read_text("utf-8"))
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}"
            for e in Draft202012Validator(schema).iter_errors(document)]


def validate_workbooks(solution, *, selected_only=False, _documents=None) -> dict:
    root = _root(solution)
    inventory = {r["path"]: r for r in inventory_workbooks(root)}
    files = (selected_workbook_files(root) if selected_only else _files(root, "XDR Workbooks")) if _documents is None else []
    results, identities, instances = [], set(), set()
    source_paths = set()
    documents = ((path, _document(path)) for path in files) if _documents is None else _documents
    for path, document in documents:
        digest = _sha(path.read_bytes()) if _documents is None else _sha(
            json.dumps(document, sort_keys=True, ensure_ascii=False).encode())
        schema_errors = authored_schema_errors(document)
        if schema_errors:
            provenance = document.get("contentProvenance")
            if isinstance(provenance, dict) and isinstance(provenance.get("source"), dict):
                source_paths.add(provenance["source"].get("path"))
            results.append({"path": path.relative_to(root).as_posix(),
                            "sha256": digest, "valid": False, "errors": schema_errors})
            continue
        errors = dependency_validation_errors(document)
        metadata = document.get("xdrMetadata", {})
        provenance = document.get("contentProvenance", {})
        source = provenance.get("source", {})
        conversion = provenance.get("conversion", {})
        from solution_manager.authoring.workbook_functions import validate_functions
        function_records = provenance.get("requiredWorkspaceFunctions", [])
        try:
            validated_functions = validate_functions(root, function_records)
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
            validated_functions = []
        approved_aliases = {record["functionAlias"] for record in validated_functions}
        identity, instance = _guid(metadata.get("contentId")), _guid(metadata.get("instanceId"))
        if not identity or not instance or identity == instance:
            errors.append("Canonical and instance identities must be distinct GUIDs.")
        if identity in identities or instance in instances or identity in instances or instance in identities:
            errors.append("Duplicate authored workbook identity.")
        identities.add(identity)
        instances.add(instance)
        if metadata.get("schemaVersion") != "1.0.0" or _content_release(metadata.get("version")) is None:
            errors.append("Authored metadata requires schema 1.0.0 and content release >=3.1.0,<4.0.0.")
        if not isinstance(metadata.get("displayName"), str) or not metadata["displayName"].strip():
            errors.append("Workbook displayName is required.")
        if any(key in provenance for key in ("packageId", "packageVersion", "contentId", "contentVersion")):
            errors.append("Deployment provenance quartet must not be authored.")
        from solution_manager.authoring.workbook_publication import is_public, validate_public_document
        if is_public(document):
            errors.extend(validate_public_document(root, document))
            source_paths.update(row["path"] for row in inventory.values()
                                if row["identity"] == identity)
            results.append({"path": path.relative_to(root).as_posix(),
                            "sha256": digest, "valid": not errors, "errors": errors})
            continue
        if "authoredReview" in provenance or provenance.get("origin") == "native-xdr":
            if "authoredReview" in provenance:
                from solution_manager.authoring.workbook_updates import validate_updated_document
                errors.extend(validate_updated_document(root, document))
            else:
                from solution_manager.authoring.native_workbooks import validate_native_document
                errors.extend(validate_native_document(root, document))
            if source.get("path") in source_paths:
                errors.append("Duplicate workbook source provenance.")
            source_paths.add(source.get("path"))
            results.append({"path": path.relative_to(root).as_posix(),
                            "sha256": digest, "valid": not errors, "errors": errors})
            continue
        row = inventory.get(source.get("path"))
        if not row or row["sha256"] != source.get("sha256"):
            errors.append("Source provenance is missing or stale.")
        if row:
            expected_instance = str(uuid5(NAMESPACE_URL, f"xdr-workbook-instance:{root.name}:{row['identity']}"))
            if identity != row["identity"] or instance != expected_instance:
                errors.append("Authored workbook identities do not match the stable source assignment.")
        if source.get("path") in source_paths:
            errors.append("Duplicate workbook source provenance.")
        source_paths.add(source.get("path"))
        queries = conversion.get("queries")
        if conversion.get("reviewRequired") is not False:
            errors.append("Conversion review is unresolved.")
        output_queries = {q["path"]: q for q in workbook.query_surfaces(document)}
        if not isinstance(queries, list):
            errors.append("Per-query conversion provenance is required.")
        else:
            recorded_source, recorded_output = set(), set()
            original_queries = {q["path"]: q["querySha256"] for q in row["queries"]} if row else {}
            original_surfaces = {}
            removed_prefixes = []
            if row:
                original = _document(_path(root, row["path"]))
                original_surfaces = {q["path"]: q for q in workbook.query_surfaces(original)}
                parameters, removed, _ = workbook._scope_parameters(original)
                removed_prefixes = [pointer + "/" for pointer, parameter in parameters
                                    if parameter["name"] in removed]
            used_aliases = set()
            for query in queries:
                source_pointer, output_pointer = query.get("sourcePath"), query.get("outputPath")
                if source_pointer in recorded_source or query.get("sourceSha256") != original_queries.get(source_pointer):
                    errors.append("Original query provenance is duplicate or stale.")
                recorded_source.add(source_pointer)
                if query.get("status") == "removed-scope-helper":
                    if output_pointer is not None or query.get("targetSha256") is not None:
                        errors.append("Removed scope query must not have output provenance.")
                    if not any(source_pointer.startswith(prefix) for prefix in removed_prefixes):
                        errors.append("Only proven scope-helper queries may be removed.")
                    continue
                if query.get("status") != "converted":
                    errors.append("Query conversion remains blocked or review-required.")
                output_query = output_queries.get(output_pointer)
                source_query = original_surfaces.get(source_pointer)
                preserved_provider = (
                    isinstance(query.get("preservedProvider"), dict)
                    and source_query is not None
                    and output_query is not None
                    and workbook.is_preserved_provider_surface(source_query)
                    and workbook.is_preserved_provider_surface(output_query)
                )
                try:
                    raw_source = workbook._raw_query(
                        source_query["node"]["query"], source_query["queryType"]) if source_query else ""
                    raw_target = workbook._raw_query(
                        output_query["node"]["query"], output_query["queryType"]) if output_query else ""
                    if preserved_provider:
                        source_aliases, target_aliases, explicit_calls = set(), set(), set()
                    else:
                        source_aliases = workbook.opaque_functions(raw_source) if source_query else set()
                        target_aliases = workbook.opaque_functions(raw_target) if output_query else set()
                        explicit_calls = (
                            (workbook.opaque_functions(raw_source, include_bare=False) if source_query else set())
                            | (workbook.opaque_functions(raw_target, include_bare=False) if output_query else set())
                        )
                except ValueError as exc:
                    errors.append(str(exc))
                    source_aliases, target_aliases, explicit_calls = set(), set(), set()
                contract = query.get("conversion")
                if not isinstance(contract, dict):
                    errors.append("Shared-converter query contract must be an object.")
                    contract = {}
                resolved_tables = (set(contract.get("resolvedTables", []))
                                   if isinstance(contract.get("resolvedTables"), list) else set())
                if (not resolved_tables
                        and not preserved_provider
                        and not workbook.rewrite.is_source_free_literal_query(raw_source)):
                    errors.append("Empty source-table lineage is allowed only for a verified literal datatable or numeric range query.")
                aliases = query.get("workspaceFunctions", [])
                alias_set = (set(aliases) if isinstance(aliases, list)
                             and all(isinstance(a, str) for a in aliases) else set())
                non_function_tables = resolved_tables - explicit_calls - approved_aliases - alias_set
                source_aliases -= non_function_tables
                target_aliases -= non_function_tables
                if (not isinstance(aliases, list) or any(not isinstance(a, str) for a in aliases)
                        or len(aliases) != len(set(aliases))
                        or set(aliases) != source_aliases or set(aliases) != target_aliases
                        or not source_aliases <= approved_aliases):
                    errors.append("Workspace function aliases must exactly match current source, target and prerequisites.")
                used_aliases.update(source_aliases)
                if output_pointer in recorded_output or not output_query or query.get("targetSha256") != workbook.query_hash(output_query["node"]["query"]):
                    errors.append("Output query provenance is missing, duplicate or stale.")
                if output_query and not preserved_provider and output_query["queryType"] != workbook.AH:
                    errors.append("Converted query must use Advanced Hunting.")
                if preserved_provider and (
                    output_query["queryType"] != source_query["queryType"]
                    or (output_query.get("resourceType") or "").lower() != (source_query.get("resourceType") or "").lower()
                    or output_query["node"]["query"] != source_query["node"]["query"]
                ):
                    errors.append("Preserved provider query must retain its original queryType, resourceType, and query.")
                if (not query.get("resolutionEvidence") or contract.get("status") != "converted"
                        or contract.get("sourceId") != source_pointer
                        or not output_query
                        or contract.get("convertedKql") != output_query["node"]["query"]):
                    errors.append("Current reviewed shared-converter query evidence is required.")
                if source_query and not preserved_provider:
                    try:
                        replay = workbook.migrator.convert(
                            workbook._raw_query(source_query["node"]["query"], source_query["queryType"]),
                            tables=contract.get("resolvedTables"), source_id=source_pointer,
                            artifact_type="workbook", resolve=False)
                        if replay != contract:
                            errors.append("Shared query contract does not match current deterministic conversion.")
                    except ValueError as exc:
                        errors.append(str(exc))
                references = sorted(set(contract.get("resolvedTables", [])) & {"Watchlist"})
                if query.get("referenceInputs", []) != references:
                    errors.append("Platform reference inputs must match reviewed raw source lineage.")
                catalog = mapping_catalog.load_mapping_catalog()["tables"]
                expected_types = {catalog.get(table, {}).get("ahTable") or table
                                  for table in telemetry_data_types(contract.get("resolvedTables", []))}
                declared_types = {table for record in provenance["requiredWorkloads"] for table in record["dataTypes"]}
                if not expected_types <= declared_types:
                    errors.append("Workload prerequisites do not cover reviewed telemetry source tables.")
                if source_aliases and (
                    not contract.get("resolvedTables")
                    or source_aliases & set(contract.get("resolvedTables", []))
                    or not source_query or not output_query
                    or workbook._raw_query(source_query["node"]["query"], source_query["queryType"])
                    != output_query["node"]["query"]
                ):
                    errors.append("Preserved function calls require distinct underlying table evidence and unchanged KQL.")
                recorded_output.add(output_pointer)
            if used_aliases != approved_aliases:
                errors.append("Workspace function prerequisites must exactly cover query aliases.")
            if recorded_source != set(original_queries) or recorded_output != set(output_queries):
                errors.append("Query provenance does not cover complete original/output inventory.")
        results.append({"path": path.relative_to(root).as_posix(),
                        "sha256": digest, "valid": not errors, "errors": errors})
    if not selected_only:
        for relative in sorted(set(inventory) - source_paths):
            results.append({"path": relative, "valid": False, "errors": ["Source workbook has no authored candidate."]})
    valid = sum(r["valid"] for r in results)
    return {"total": len(results), "valid": valid, "invalid": len(results) - valid,
            "results": results}
