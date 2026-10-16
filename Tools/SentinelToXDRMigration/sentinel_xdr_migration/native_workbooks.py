"""Offline native Advanced Hunting import; no conversion or runtime claims."""
from __future__ import annotations

from copy import deepcopy
import json
import re
import sys
from pathlib import PurePosixPath
from uuid import NAMESPACE_URL, uuid5

from ._workbook_core import workbook, mapping_catalog, rewrite
from .catalog import query_table_references
from .dependencies import TABLE_WORKLOADS, workload_records
from .workbooks import (
    _root, _path, _document, _sha, _write, _solution_data, _release, _load_json as load_json,
)

SOURCE_PREFIX = "Workbook Sources/Native/"
ORIGIN = "native-xdr"


def _source(root, relative):
    path = _path(root, relative)
    if not relative.startswith(SOURCE_PREFIX) or path.suffix.lower() != ".json" or not path.is_file():
        raise ValueError(f"Native source must be an existing {SOURCE_PREFIX} JSON file.")
    document = _document(path)
    if any(key in document for key in ("xdrMetadata", "contentProvenance")):
        raise ValueError("Native source must be raw Notebook content, not an authored candidate.")
    return path, document


def _payload(document):
    return {key: value for key, value in document.items()
            if key not in ("contentProvenance", "xdrMetadata")}


def _canonical_payload_sha256(document):
    canonical = json.dumps(
        _payload(document), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    return _sha(canonical)


def _valid_source_identity(source):
    if not isinstance(source, dict) or set(source) != {"path", "sha256"}:
        return False
    relative, digest = source["path"], source["sha256"]
    return (
        isinstance(relative, str)
        and relative.startswith(SOURCE_PREFIX)
        and "\\" not in relative
        and relative.lower().endswith(".json")
        and all(part not in ("", ".", "..") for part in relative.split("/"))
        and isinstance(digest, str)
        and re.fullmatch(r"[0-9a-f]{64}", digest) is not None
    )


def identities(root, relative):
    content = str(uuid5(NAMESPACE_URL, f"native-xdr-workbook:{root.name}:{relative}"))
    instance = str(uuid5(NAMESPACE_URL, f"xdr-workbook-instance:{root.name}:{content}"))
    return content, instance


def _query(surface, *, allowed_tables=(), allowed_functions=(), allow_sentinel=False,
           include_lineage=False):
    raw = surface["node"]["query"]
    if not isinstance(raw, str) or surface["queryType"] != workbook.AH:
        raise ValueError("Every native query must be a string using advancedHunting.")
    code = workbook._stripped_code(raw)
    for match in re.finditer(r"\b(?:workspace|app|resource|cluster|database|table|totable|externaldata)\s*[\[(]", code, re.I):
        if not workbook._is_union_withsource_output_binding(code, match.start()):
            raise ValueError("Native import does not support dynamic, external or cross-resource sources.")
    allowed_tables, allowed_functions = set(allowed_tables), set(allowed_functions)
    known = set(TABLE_WORKLOADS) | set(mapping_catalog.load_mapping_catalog()["tables"]) | allowed_tables
    asim_names = {name for name in re.findall(r"\b[A-Za-z_]\w*", code)
                  if workbook.is_standard_builtin_asim_parser(name)}
    tables = {r["table"] for r in query_table_references(raw, known_tables=known | asim_names)}
    # Include quoted/union sources and reject unknown calls/bare sources rather
    # than interpreting a reviewer's assertion as proof that they are tables.
    quoted_calls, quoted_tables = workbook._quoted_calls_and_table_sources(raw)
    tables |= quoted_tables | workbook.union_source_names(raw)
    calls = set(re.findall(r"(?<![.\w])([A-Za-z_]\w*)\s*\(", code))
    asim = {name for name in tables | calls | quoted_calls
            if workbook.is_standard_builtin_asim_parser(name)}
    # Built-in parsers are supported functions, not proof of their hidden
    # input tables, workloads or connector prerequisites.
    tables -= asim | allowed_functions
    local = set(re.findall(r"\blet\s+([A-Za-z_]\w*)\s*=", code))
    tables -= local | workbook._BUILTINS | workbook._STATEMENT_PREFIXES
    opaque = workbook.opaque_functions(raw) - tables - allowed_functions
    explicit = (workbook.opaque_functions(raw, include_bare=False)
                | (quoted_calls - asim)) - allowed_functions
    if opaque or explicit:
        raise ValueError("Unreviewable native functions/sources: " + ", ".join(sorted(opaque | explicit)))
    if any((table not in TABLE_WORKLOADS or TABLE_WORKLOADS[table] == "sentinel")
           and not (allow_sentinel and table in allowed_tables) for table in tables):
        raise ValueError("Unknown or non-native tables: " + ", ".join(sorted(tables)))
    known_function_input = allowed_functions & (calls | quoted_calls | workbook.opaque_functions(raw))
    if not tables and not asim and not known_function_input and not rewrite.is_source_free_literal_query(raw):
        raise ValueError("Empty lineage requires a standard built-in ASIM parser "
                         "or a recognized literal datatable or numeric range query.")
    if include_lineage:
        return {"tables": sorted(tables), "builtinAsimParsers": sorted(asim),
                "workspaceFunctions": sorted(known_function_input)}
    return sorted(tables)


def _plan_document(document, source):
    queries, all_tables = [], set()
    for surface in workbook.query_surfaces(document):
        if not isinstance(surface["node"]["query"], str):
            raise ValueError("Every native query must be a string.")
        blockers = []
        try:
            tables = _query(surface)
        except ValueError as exc:
            tables = []
            blockers.append(str(exc))
        all_tables.update(tables)
        raw = surface["node"]["query"]
        queries.append({
            "path": surface["path"], "querySha256": workbook.query_hash(raw),
            "tables": tables, "decision": None, "evidence": "", "blockers": blockers,
        })
    workloads, _ = workload_records(sorted(all_tables))
    return {
        "origin": ORIGIN, "source": source,
        "canonicalPayloadSha256": _canonical_payload_sha256(document),
        "displayName": PurePosixPath(source["path"]).stem, "actor": "", "reference": "",
        "requiredWorkloads": workloads, "requiredDataConnectors": [],
        "queries": queries,
    }


def plan_native_workbook(solution, source):
    root = _root(solution)
    path, document = _source(root, source)
    return _plan_document(document, {"path": source, "sha256": _sha(path.read_bytes())})


def _review_errors_for_document(document, source, review):
    errors = []
    expected = _plan_document(document, source)
    if not isinstance(review, dict) or set(review) != set(expected):
        return ["Native review must have exactly the current plan fields."]
    for field in ("origin", "source", "canonicalPayloadSha256",
                  "requiredWorkloads", "requiredDataConnectors"):
        if review[field] != expected[field]:
            errors.append(f"Native review {field} is stale or differs from strict native dependencies.")
    for field in ("actor", "reference", "displayName"):
        if not isinstance(review[field], str) or not review[field].strip():
            errors.append(f"Native review requires {field}.")
    queries = review["queries"]
    if not isinstance(queries, list) or len(queries) != len(expected["queries"]):
        return errors + ["Native review must cover every current query exactly once."]
    by_path = {q["path"]: q for q in expected["queries"]}
    seen = set()
    for query in queries:
        if not isinstance(query, dict) or set(query) != {"path", "querySha256", "tables", "decision", "evidence", "blockers"}:
            errors.append("Malformed native query review.")
            continue
        pointer = query["path"]
        if not isinstance(pointer, str) or pointer in seen or pointer not in by_path:
            errors.append("Duplicate or unknown native query pointer.")
            continue
        seen.add(pointer)
        current = by_path[pointer]
        if any(query[field] != current[field] for field in ("querySha256", "tables", "blockers")):
            errors.append("Native query hash/tables/blockers are stale.")
        if current["blockers"]:
            errors.extend(current["blockers"])
        if query["decision"] != "accept" or not isinstance(query["evidence"], str) or not query["evidence"].strip():
            errors.append("Every native query requires explicit accept and nonempty evidence.")
    if seen != set(by_path):
        errors.append("Native review does not cover the complete current query inventory.")
    return errors


def _review_errors(root, source, review):
    path, document = _source(root, source)
    source_record = {"path": source, "sha256": _sha(path.read_bytes())}
    return _review_errors_for_document(document, source_record, review)


def validate_native_document(solution, document):
    root = _root(solution)
    provenance = document.get("contentProvenance", {})
    if not isinstance(provenance, dict):
        return ["Native provenance must be an object."]
    if provenance.get("origin") != ORIGIN:
        return ["Expected explicit native-xdr origin."]
    source = provenance.get("source", {})
    if not isinstance(source, dict):
        return ["Native historical source identity/hash is malformed."]
    relative = source.get("path")
    try:
        review = provenance.get("nativeReview")
        if not _valid_source_identity(source):
            return ["Native historical source identity/hash is malformed."]
        payload = _payload(document)
        errors = _review_errors_for_document(payload, source, review)
        canonical_hash = _canonical_payload_sha256(document)
        if provenance.get("canonicalPayloadSha256") != canonical_hash:
            errors.append("Native canonical payload hash is stale.")
        expected_provenance = {
            "origin": ORIGIN, "source": source, "nativeReview": review,
            "canonicalPayloadSha256": canonical_hash,
            "requiredWorkloads": review["requiredWorkloads"],
            "requiredDataConnectors": review["requiredDataConnectors"],
            "dependencyReviewRequired": False,
        }
        if provenance != expected_provenance:
            errors.append("Native provenance must match the complete reviewed dependencies; no conversion receipt.")
        content, instance = identities(root, relative)
        metadata = document.get("xdrMetadata", {})
        if (metadata.get("contentId"), metadata.get("instanceId")) != (content, instance):
            errors.append("Native identities do not match stable source assignment.")
        if metadata.get("displayName") != review["displayName"]:
            errors.append("Native displayName differs from reviewed name.")
        return errors
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [str(exc)]


def review_native_workbook(solution, source, review):
    root = _root(solution)
    errors = _review_errors(root, source, review)
    if errors:
        raise ValueError("; ".join(errors))
    return deepcopy(review)


def import_native_workbook(solution, source, review):
    root = _root(solution)
    review = review_native_workbook(root, source, review)
    path, document = _source(root, source)
    data = _solution_data(root)
    if "XDR Workbooks" in data:
        from .workbooks import selected_workbook_files
        selected_workbook_files(root)
    version = _release(data, {})
    if version is None:
        raise ValueError("Native import requires a solution release >=3.2.0,<4.0.0.")
    content, instance = identities(root, source)
    document["xdrMetadata"] = {
        "contentId": content, "instanceId": instance, "version": version,
        "schemaVersion": "1.0.0", "displayName": review["displayName"],
    }
    document["contentProvenance"] = {
        "origin": ORIGIN, "source": deepcopy(review["source"]), "nativeReview": deepcopy(review),
        "canonicalPayloadSha256": review["canonicalPayloadSha256"],
        "requiredWorkloads": deepcopy(review["requiredWorkloads"]),
        "requiredDataConnectors": deepcopy(review["requiredDataConnectors"]),
        "dependencyReviewRequired": False,
    }
    relative = "XDR Workbooks/" + source.removeprefix(SOURCE_PREFIX)
    target = _path(root, relative)
    raw = (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode()
    if target.exists() and target.read_bytes() != raw:
        raise ValueError("Existing native candidate differs; refusing overwrite.")
    # Validate all existing candidates/identities before adding this selection.
    from .workbooks import _files, validate_workbooks, authored_schema_errors
    errors = authored_schema_errors(document) + validate_native_document(root, document)
    if errors:
        raise ValueError("; ".join(errors))
    existing_validation = validate_workbooks(root, selected_only=False)
    invalid = [r for r in existing_validation["results"]
               if not r["valid"] and r["errors"] != ["Source workbook has no authored candidate."]]
    if invalid:
        raise ValueError("Existing authored candidates must validate before native import: " + str(invalid))
    for existing in _files(root, "XDR Workbooks"):
        if existing == target:
            continue
        metadata = _document(existing).get("xdrMetadata", {})
        if {content, instance} & {metadata.get("contentId"), metadata.get("instanceId")}:
            raise ValueError("Duplicate authored workbook identity.")
    references = data.get("XDR Workbooks", [])
    if not isinstance(references, list) or any(not isinstance(ref, str) for ref in references):
        raise ValueError("XDR Workbooks selection must be an array of paths.")
    if len({ref.casefold() for ref in references}) != len(references):
        raise ValueError("Duplicate workbook selection.")
    if any(ref.casefold() == relative.casefold() and ref != relative for ref in references):
        raise ValueError("Case-insensitive workbook selection collision.")
    if relative not in references:
        references.append(relative)
    data["XDR Workbooks"] = references
    data_path = next(_path(root, "Data").glob("Solution_*.json"))
    previous_data = data_path.read_bytes()
    data_raw = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode()
    if _sha(path.read_bytes()) != review["source"]["sha256"]:
        raise ValueError("Native source changed before import.")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        _write(target, raw, None)
    if data_raw != previous_data:
        _write(data_path, data_raw, previous_data)
    return {"path": relative, "contentId": content, "instanceId": instance,
            "runtimeQualified": False, "validation": validate_workbooks(root, selected_only=True)}


def main():
    # Private stdin adapter for PowerShell: validate the actual in-memory
    # document without scratch files or an independently maintained validator.
    if not (3, 11) <= sys.version_info[:2] < (3, 13):
        raise ValueError("Native workbook validation requires Python 3.11 or 3.12.")
    root = sys.argv[1]
    document = load_json(sys.stdin.read())
    from .workbooks import authored_schema_errors
    errors = authored_schema_errors(document) + validate_native_document(root, document)
    print(json.dumps({"errors": errors}))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
