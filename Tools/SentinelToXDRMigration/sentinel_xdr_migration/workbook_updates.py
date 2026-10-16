"""Explicit offline reviews of post-import edits; historical receipts never change.

The reverse delta retains only changed baseline values, not another raw Notebook.
Hashes are review/freshness evidence, not signatures or runtime qualification.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

from ._workbook_core import workbook
from .dependencies import dependency_validation_errors
from .dependencies import TABLE_WORKLOADS
from .catalog import query_table_references
from ._workbook_core import mapping_catalog
from .native_workbooks import _payload, _canonical_payload_sha256, _query
from .workbook_functions import validate_functions
from .workbooks import (
    _root, _path, _document, _load_json, _sha, _write, validate_workbooks,
)


def _canonical(value):
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8"))


def _review_digest(review):
    return _canonical({key: value for key, value in review.items() if key != "reviewSha256"})


def _reverse(current, baseline, path=()):
    if isinstance(current, dict) and isinstance(baseline, dict):
        changes = []
        for key in sorted(current.keys() - baseline.keys()):
            changes.append({"path": [*path, key], "op": "remove"})
        for key in sorted(baseline.keys() - current.keys()):
            changes.append({"path": [*path, key], "op": "add", "value": baseline[key]})
        for key in sorted(current.keys() & baseline.keys()):
            changes.extend(_reverse(current[key], baseline[key], (*path, key)))
        return changes
    if isinstance(current, list) and isinstance(baseline, list):
        changes = []
        for index in range(min(len(current), len(baseline))):
            changes.extend(_reverse(current[index], baseline[index], (*path, index)))
        for index in reversed(range(len(baseline), len(current))):
            changes.append({"path": [*path, index], "op": "remove"})
        for index in range(len(current), len(baseline)):
            changes.append({"path": [*path, index], "op": "add", "value": baseline[index]})
        return changes
    if type(current) is type(baseline) and current == baseline:
        return []
    return [{"path": list(path), "op": "replace", "value": baseline}]


def _restore(payload, changes):
    value = deepcopy(payload)
    for change in changes:
        path, op = change["path"], change["op"]
        if not path:
            raise ValueError("Baseline delta must not replace the entire Notebook.")
        parent = value
        for part in path[:-1]:
            parent = parent[part]
        key = path[-1]
        if op == "remove":
            if isinstance(parent, list):
                parent.pop(key)
            else:
                del parent[key]
        elif op == "add" and isinstance(parent, list):
            parent.insert(key, deepcopy(change["value"]))
        elif op in ("add", "replace"):
            parent[key] = deepcopy(change["value"])
        else:
            raise ValueError("Unknown baseline delta operation.")
    return value


def _historical_errors(root, document):
    if "authoredReview" in document.get("contentProvenance", {}):
        return ["Baseline must be an original reviewed authored artifact, not an update review."]
    result = validate_workbooks(root, selected_only=True, _documents=[
        (root / "XDR Workbooks" / "historical-baseline.json", document)])
    return [error for row in result["results"] for error in row["errors"]]


def _queries(document, provenance, baseline):
    native = provenance.get("origin") == "native-xdr"
    records = provenance.get("requiredWorkspaceFunctions", [])
    aliases = {record["functionAlias"] for record in records}
    declared = {table for record in provenance["requiredWorkloads"] for table in record["dataTypes"]}
    sentinel = {table for record in provenance["requiredWorkloads"]
                if record["workload"] == "sentinel" for table in record["dataTypes"]}
    connectors = {table for record in provenance["requiredDataConnectors"] for table in record["dataTypes"]}
    known = set(TABLE_WORKLOADS) | set(mapping_catalog.load_mapping_catalog()["tables"])
    historical = {surface["path"]: surface for surface in workbook.query_surfaces(baseline)}
    queries, used = [], set()
    for surface in workbook.query_surfaces(document):
        raw = surface["node"]["query"]
        inherited = set()
        previous = historical.get(surface["path"])
        if not native and previous:
            # Some accepted converter receipts predate complete nested-source
            # discovery. Preserve only that exact query's proven old lineage;
            # never invent dependencies or extend the exception to new queries.
            candidates = {row["table"] for row in query_table_references(
                previous["node"]["query"], known_tables=known)} & known
            inherited = set(_query(previous, allowed_tables=declared | candidates,
                                   allowed_functions=aliases, allow_sentinel=True))
        lineage = _query(surface, allowed_tables=declared | inherited if not native else (),
                         allowed_functions=aliases, allow_sentinel=not native,
                         include_lineage=True)
        tables = lineage["tables"]
        if inherited - declared and set(tables) != inherited:
            raise ValueError("Historically incomplete dependencies require unchanged query table lineage.")
        if not set(tables) <= declared | inherited:
            raise ValueError("Current query tables are outside historical reviewed dependencies: "
                             + ", ".join(sorted(set(tables) - declared - inherited)))
        if not native and not (set(tables) & sentinel) <= connectors:
            raise ValueError("Current Sentinel query tables require historical explicit connector coverage.")
        if inherited - declared and not (inherited & sentinel & connectors):
            raise ValueError("Inherited hybrid lineage requires historical explicit Sentinel connector coverage.")
        used.update(lineage["workspaceFunctions"])
        queries.append({
            "path": surface["path"], "querySha256": workbook.query_hash(raw),
            **lineage,
        })
    if used != aliases:
        raise ValueError("Current queries must exactly cover historical workspace function prerequisites.")
    return queries


def _plan(root, current, baseline, baseline_record):
    errors = _historical_errors(root, baseline)
    if errors:
        raise ValueError("Historical baseline failed validation: " + "; ".join(errors))
    historical = baseline["contentProvenance"]
    if not isinstance(current.get("xdrMetadata"), dict) or not isinstance(current.get("contentProvenance"), dict):
        raise ValueError("Current workbook requires authored metadata and historical provenance objects.")
    for field in ("contentId", "instanceId"):
        if current["xdrMetadata"].get(field) != baseline["xdrMetadata"][field]:
            raise ValueError("Workbook identity must remain unchanged.")
    for field in ("requiredWorkloads", "requiredDataConnectors", "requiredWorkspaceFunctions",
                  "dependencyReviewRequired"):
        default = [] if field == "requiredWorkspaceFunctions" else None
        if (field == "dependencyReviewRequired"
                and current["contentProvenance"].get("format") == "public-workbook-v1"):
            continue
        if current["contentProvenance"].get(field, default) != historical.get(field, default):
            raise ValueError("Updates cannot replace historical reviewed dependencies: " + field)
    restored = deepcopy(current)
    restored["contentProvenance"] = deepcopy(historical)
    errors = dependency_validation_errors(restored)
    validate_functions(root, historical.get("requiredWorkspaceFunctions", []))
    if errors:
        raise ValueError("; ".join(errors))
    queries = _queries(restored, historical, baseline)
    old = {q["path"]: q["node"]["query"] for q in workbook.query_surfaces(baseline)}
    new = {q["path"]: q["node"]["query"] for q in workbook.query_surfaces(restored)}
    changed = []
    for pointer in sorted(old.keys() | new.keys()):
        before = workbook.query_hash(old[pointer]) if pointer in old else None
        after = workbook.query_hash(new[pointer]) if pointer in new else None
        if before != after:
            changed.append({"path": pointer, "baselineQuerySha256": before,
                            "querySha256": after, "decision": None, "evidence": ""})
    return {
        "schemaVersion": "1.0.0", "baseline": baseline_record,
        "baselineMetadata": deepcopy(baseline["xdrMetadata"]),
        "reversePayloadChanges": _reverse(_payload(restored), _payload(baseline)),
        "canonicalPayloadSha256": _canonical_payload_sha256(restored),
        "canonicalDocumentSha256": _canonical(restored),
        "queries": queries, "changedQueries": changed,
        "actor": "", "reference": "", "decision": None, "reviewSha256": None,
    }, restored


def _read_external(path):
    path = Path(path).expanduser()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Review/baseline files must not use symlinks.")
    raw = path.read_bytes()
    value = _load_json(raw)
    if not isinstance(value, dict):
        raise ValueError("Review/baseline JSON must be an object.")
    return raw, value


def plan_workbook_update(solution, content, baseline_file):
    root = _root(solution)
    path = _path(root, content)
    if not content.startswith("XDR Workbooks/") or path.suffix.lower() != ".json":
        raise ValueError("Update content must be authored XDR Workbooks JSON.")
    raw, baseline = _read_external(baseline_file)
    record = {"reference": str(Path(baseline_file).name), "sha256": _sha(raw),
              "canonicalDocumentSha256": _canonical(baseline)}
    return _plan(root, _document(path), baseline, record)[0]


def review_workbook_update(solution, content, baseline_file, review):
    expected = plan_workbook_update(solution, content, baseline_file)
    if not isinstance(review, dict) or set(review) != set(expected):
        raise ValueError("Update review must have exactly the current plan fields.")
    for field in ("actor", "reference"):
        if not isinstance(review[field], str) or not review[field].strip():
            raise ValueError("Update review requires " + field)
        expected[field] = review[field]
    if review["decision"] != "accept":
        raise ValueError("Update requires explicit accept of the whole current authored document.")
    expected["decision"] = "accept"
    if not isinstance(review["changedQueries"], list) or len(review["changedQueries"]) != len(expected["changedQueries"]):
        raise ValueError("Review must cover every changed/added/removed query.")
    for actual, query in zip(review["changedQueries"], expected["changedQueries"]):
        if not isinstance(actual, dict):
            raise ValueError("Malformed changed query review.")
        if actual.get("decision") != "accept" or not isinstance(actual.get("evidence"), str) or not actual["evidence"].strip():
            raise ValueError("Every changed query requires explicit accept and evidence.")
        query.update(decision="accept", evidence=actual["evidence"])
    digest = _review_digest(expected)
    if review["reviewSha256"] not in (None, digest):
        raise ValueError("Update review evidence hash is stale.")
    expected["reviewSha256"] = review["reviewSha256"]
    if review != expected:
        raise ValueError("Update review is stale or differs from exact baseline/current query dependencies.")
    expected["reviewSha256"] = digest
    return expected


def apply_workbook_update(solution, content, baseline_file, review):
    root = _root(solution)
    path = _path(root, content)
    previous = path.read_bytes()
    review = review_workbook_update(root, content, baseline_file, review)
    baseline_raw, baseline = _read_external(baseline_file)
    if _sha(baseline_raw) != review["baseline"]["sha256"]:
        raise ValueError("Historical baseline changed before apply.")
    document = _load_json(previous)
    document["contentProvenance"] = deepcopy(baseline["contentProvenance"])
    if _canonical(document) != review["canonicalDocumentSha256"]:
        raise ValueError("Current workbook changed before apply.")
    from .workbook_publication import (
        is_public, public_document, retain_receipt, validate_public_document, source_evidence,
    )
    if is_public(baseline):
        clean = public_document(document)
        errors = validate_public_document(root, clean)
    else:
        document["contentProvenance"]["authoredReview"] = review
        errors = validate_updated_document(root, document)
        clean = public_document(document)
        errors.extend(validate_public_document(root, clean))
    if errors:
        raise ValueError("; ".join(errors))
    from .workbooks import authored_schema_errors
    errors = authored_schema_errors(clean)
    if errors:
        raise ValueError("; ".join(errors))
    receipt = retain_receipt(root, clean, {
        "publicDocument": clean, "inputSha256": _sha(previous),
        "inputArtifact": previous.decode("utf-8"), "review": review,
        "baselineArtifact": baseline_raw.decode("utf-8"), "baselineSha256": _sha(baseline_raw),
        "sourceArtifacts": source_evidence(root, baseline),
    })
    _write(path, (json.dumps(clean, indent=2, ensure_ascii=False) + "\n").encode(), previous)
    return {"path": content, "sha256": _sha(path.read_bytes()), "localReceipt": receipt,
            "runtimeQualified": False}


def validate_updated_document(solution, document):
    try:
        root = _root(solution)
        current = deepcopy(document)
        review = current["contentProvenance"].pop("authoredReview")
        if not isinstance(review, dict):
            return ["authoredReview must be a complete explicit update review."]
        if review.get("reviewSha256") != _review_digest(review):
            return ["Authored review evidence hash is stale."]
        baseline = _restore(_payload(current), review["reversePayloadChanges"])
        baseline["xdrMetadata"] = deepcopy(review["baselineMetadata"])
        baseline["contentProvenance"] = deepcopy(current["contentProvenance"])
        if _canonical(baseline) != review["baseline"]["canonicalDocumentSha256"]:
            return ["Historical baseline/proof hash is stale."]
        expected, _ = _plan(root, current, baseline, review["baseline"])
        for field in ("actor", "reference"):
            if not isinstance(review[field], str) or not review[field].strip():
                return ["Update review requires nonempty " + field]
            expected[field] = review[field]
        if review["decision"] != "accept":
            return ["Update requires explicit whole-document accept."]
        expected["decision"] = "accept"
        if len(review["changedQueries"]) != len(expected["changedQueries"]):
            return ["Changed query review inventory is stale."]
        for actual, query in zip(review["changedQueries"], expected["changedQueries"]):
            if actual["decision"] != "accept" or not isinstance(actual["evidence"], str) or not actual["evidence"].strip():
                return ["Changed query requires accept and evidence."]
            query.update(decision="accept", evidence=actual["evidence"])
        expected["reviewSha256"] = _review_digest(expected)
        if review != expected:
            return ["Authored review is stale: whole document, queries or dependencies changed."]
        return []
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        return ["Invalid authored review: " + str(exc)]


def main():
    if not (3, 11) <= sys.version_info[:2] < (3, 13):
        raise ValueError("Workbook update validation requires Python 3.11 or 3.12.")
    document = _load_json(sys.stdin.read())
    from .workbooks import authored_schema_errors
    errors = authored_schema_errors(document) + validate_updated_document(sys.argv[1], document)
    print(json.dumps({"errors": errors}))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
