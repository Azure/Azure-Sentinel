"""Exact, offline Sentinel workspace-function prerequisites for workbooks only."""
from __future__ import annotations

from copy import deepcopy
import re

import yaml

IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
FIELDS = {"functionAlias", "sourcePath", "sourceSha256"}


def function_parameters(document):
    parameters = document.get("FunctionParams")
    if parameters is None:
        return ""
    if not isinstance(parameters, list):
        raise ValueError("Workspace function FunctionParams must be an array.")
    rendered, names = [], set()
    for parameter in parameters:
        if (not isinstance(parameter, dict) or not isinstance(parameter.get("Name"), str)
                or not IDENTIFIER.fullmatch(parameter["Name"])
                or parameter["Name"] in names or not isinstance(parameter.get("Type"), str)
                or not parameter["Type"].strip()):
            raise ValueError("Workspace function parameters require unique valid names and explicit types.")
        names.add(parameter["Name"])
        kind = parameter["Type"]
        value = f"{parameter['Name']}:{kind.split(':')[-1] if kind.startswith('table:') else kind}"
        if not kind.startswith("table:") and parameter.get("Default") is not None:
            default = parameter["Default"]
            if isinstance(default, (dict, list)):
                raise ValueError("Workspace function defaults must be scalar values.")
            value += "=" + (f"'{default}'" if kind.lower() == "string" else str(default))
        rendered.append(value)
    return ",".join(rendered)


def function_definition(root, relative):
    from solution_manager.migration.workbooks import _path, _sha

    if not isinstance(relative, str) or not relative.startswith(("Parsers/", "Workspace Functions/")):
        raise ValueError("Workspace function source must be Parsers/*.yaml or Workspace Functions/*.yaml.")
    if re.search(r"[\x00-\x1f\x7f]", relative):
        raise ValueError("Workspace function paths must not contain control characters.")
    path = _path(root, relative)
    if path.suffix != ".yaml" or not path.is_file():
        raise ValueError(f"Missing YAML workspace function: {relative}")
    source = path.read_bytes()
    try:
        document = yaml.safe_load(source.decode("utf-8-sig"))
    except (yaml.YAMLError, UnicodeError) as exc:
        raise ValueError(f"Malformed workspace function YAML: {relative}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"Workspace function must contain a YAML object: {relative}")
    names = [document[field] for field in ("FunctionName", "FunctionAlias") if field in document]
    if not names or any(not isinstance(name, str) or not IDENTIFIER.fullmatch(name) for name in names):
        raise ValueError(f"Workspace function requires exact valid FunctionName/FunctionAlias: {relative}")
    if not isinstance(document.get("FunctionQuery"), str) or not document["FunctionQuery"].strip():
        raise ValueError(f"Workspace function requires FunctionQuery: {relative}")
    function_parameters(document)
    # FunctionAlias is the saved-query alias; FunctionName is only its fallback.
    alias = document.get("FunctionAlias", document.get("FunctionName"))
    return {"functionAlias": alias, "sourcePath": relative, "sourceSha256": _sha(source)}, document


def candidates(root):
    from solution_manager.migration.workbooks import _path, _sha
    from solution_manager.migration._workbook_core.workbook import opaque_functions, union_source_names
    from solution_manager.migration._workbook_core import mapping_catalog, rewrite

    result = []
    for directory in ("Parsers", "Workspace Functions"):
        base = _path(root, directory)
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_symlink():
                raise ValueError("Symlink in workspace function inventory.")
            if path.is_file() and path.suffix == ".yaml":
                relative = path.relative_to(root).as_posix()
                try:
                    record, document = function_definition(root, relative)
                    query = document["FunctionQuery"]
                    code = "".join(text if kind == "code" else " " * len(text)
                                   for kind, text in rewrite._segments(query))
                    known_tables = set(mapping_catalog.load_mapping_catalog()["tables"])
                    branches = union_source_names(query) - known_tables - {
                        "externaldata", "datatable", "range", "print", "_GetWatchlist"}
                    result.append({**record,
                                   "nestedFunctions": sorted(opaque_functions(document["FunctionQuery"]) - branches),
                                   "unresolvedBranchCandidates": sorted(branches),
                                   "nestedDiscoveryExhaustive": False,
                                   "externalSourceWarnings": (
                                       ["Definition uses externaldata; review exact external source binding and availability separately."]
                                       if re.search(r"\bexternaldata\s*[\[(]", code) else []),
                                   "coverageWarning": "Nested/optional function branches need separate review; runtime fidelity is not verified."})
                except (ValueError, yaml.YAMLError) as exc:
                    result.append({"sourcePath": relative, "sourceSha256": _sha(path.read_bytes()), "error": str(exc)})
    return result


def validate_functions(root, records):
    from solution_manager.migration.workbooks import _solution_data

    if not isinstance(records, list):
        raise ValueError("requiredWorkspaceFunctions must be an array.")
    data = _solution_data(root)
    selected = []
    for field in ("Parsers", "Data Parsers", "Workspace Functions"):
        values = data.get(field, [])
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise ValueError(f"Solution {field} selection must be a string array.")
        selected.extend(values)
    aliases, paths = set(), set()
    result = []
    for record in records:
        if not isinstance(record, dict) or set(record) != FIELDS:
            raise ValueError("Workspace function records require exactly functionAlias, sourcePath, sourceSha256.")
        current, _ = function_definition(root, record["sourcePath"])
        if current != record:
            raise ValueError("Workspace function alias/hash is stale or does not match its current definition.")
        if selected.count(record["sourcePath"]) != 1:
            raise ValueError("Workspace function requires explicit packaged Data Parsers/Workspace Functions selection.")
        if record["functionAlias"] in aliases or record["sourcePath"] in paths:
            raise ValueError("Duplicate workspace function prerequisite.")
        aliases.add(record["functionAlias"])
        paths.add(record["sourcePath"])
        result.append(deepcopy(record))
    return result
