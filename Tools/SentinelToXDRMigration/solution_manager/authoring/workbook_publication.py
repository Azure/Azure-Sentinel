"""Public workbook dependencies, with private, hash-bound authoring receipts."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys

from solution_manager.migration._workbook_core import workbook
from solution_manager.migration._workbook_core import mapping_catalog
from solution_manager.authoring.dependencies import (
    CONNECTOR_OPTIONAL_SENTINEL_TABLES,
    TABLE_WORKLOADS,
    dependency_validation_errors,
)
from solution_manager.authoring.native_workbooks import _query
from solution_manager.authoring.workbook_functions import validate_functions
from solution_manager.migration.workbooks import _root, _path, _document, _load_json, _sha, _write

FORMAT = "public-workbook-v1"
DEPENDENCIES = ("requiredWorkloads", "requiredDataConnectors", "requiredWorkspaceFunctions")


def digest(value):
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8"))


def is_public(document):
    return document.get("contentProvenance", {}).get("format") == FORMAT


def public_document(document, dependencies=None):
    result = deepcopy(document)
    old = document["contentProvenance"]
    dependencies = old if dependencies is None else dependencies
    result["contentProvenance"] = {
        "format": FORMAT, "origin": old.get("origin", "sentinel-migration"),
        **{key: deepcopy(dependencies.get(key, [])) for key in DEPENDENCIES},
    }
    return result


def validate_public_document(solution, document):
    """Structure and current source/function dependencies, never acceptance."""
    root = _root(solution)
    errors = dependency_validation_errors(document)
    provenance = document["contentProvenance"]
    try:
        records = validate_functions(root, provenance["requiredWorkspaceFunctions"])
        aliases = {record["functionAlias"] for record in records}
        declared = {table for row in provenance["requiredWorkloads"] for table in row["dataTypes"]}
        sentinel = {table for row in provenance["requiredWorkloads"]
                    if row["workload"] == "sentinel" for table in row["dataTypes"]}
        connectors = {table for row in provenance["requiredDataConnectors"] for table in row["dataTypes"]}
        used = set()
        known = set(TABLE_WORKLOADS) | set(mapping_catalog.load_mapping_catalog()["tables"])
        if not declared <= known:
            errors.append("Unknown public dependency tables: " + ", ".join(sorted(declared - known)))
        if not connectors <= declared:
            errors.append("Public connector tables must be covered by workload prerequisites.")
        native = provenance["origin"] == "native-xdr"
        if native and (aliases or connectors or sentinel):
            errors.append("Native public workbooks cannot declare Sentinel/function prerequisites.")
        for surface in workbook.query_surfaces(document):
            lineage = _query(surface, allowed_tables=declared, allowed_functions=aliases,
                             allow_sentinel=not native, include_lineage=True)
            tables = set(lineage["tables"])
            if not tables <= known:
                errors.append("Unknown public query tables: " + ", ".join(sorted(tables - known)))
            if not tables <= declared:
                errors.append("Current query tables are outside public dependencies: "
                              + ", ".join(sorted(tables - declared)))
            connector_required = (
                tables & sentinel
            ) - CONNECTOR_OPTIONAL_SENTINEL_TABLES
            if not connector_required <= connectors:
                errors.append("Current Sentinel query tables require explicit connector coverage: "
                              + ", ".join(sorted(connector_required - connectors)))
            for table in tables:
                expected = TABLE_WORKLOADS.get(table)
                if expected and not any(row["workload"] == expected and table in row["dataTypes"]
                                        for row in provenance["requiredWorkloads"]):
                    errors.append("Incorrect public workload for table: " + table)
            used.update(lineage["workspaceFunctions"])
        if used != aliases:
            errors.append("Public workspace functions must exactly cover current query aliases.")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors.append(str(exc))
    return errors


def _receipt_path(root, document):
    path = _path(root, "Logs/workbook-reviews/" + digest(document) + ".json")
    # Logs is excluded from publication. Refuse tracked or non-ignored evidence.
    probe = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
    if probe.returncode == 0:
        tracked = subprocess.run(["git", "-C", str(root), "ls-files", "--", str(path)],
                                 capture_output=True, text=True, check=True)
        ignored = subprocess.run(["git", "-C", str(root), "check-ignore", "--quiet", str(path)],
                                 capture_output=True)
        if tracked.stdout.strip() or ignored.returncode:
            raise ValueError("Local workbook receipts must be untracked and gitignored under Logs.")
    return path


def retain_receipt(solution, document, evidence):
    root = _root(solution)
    receipt = {"format": FORMAT, "canonicalDocumentSha256": digest(document),
               "evidence": evidence}
    receipt["receiptSha256"] = digest(receipt)
    path = _receipt_path(root, document)
    raw = (json.dumps(receipt, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != raw:
            old = path.read_bytes()
            archive = path.with_name(path.stem + "-" + _sha(old) + ".json")
            _write(archive, old, archive.read_bytes() if archive.exists() else None)
    path.parent.mkdir(parents=True, exist_ok=True)
    _write(path, raw, path.read_bytes() if path.exists() else None)
    return str(path)


def source_evidence(root, document):
    source = document["contentProvenance"].get("source")
    if not source:
        return {}
    path = _path(root, source["path"])
    if not path.exists():
        return {}
    raw = path.read_bytes()
    if _sha(raw) != source["sha256"]:
        raise ValueError("Historical source changed before retaining local proof.")
    return {source["path"]: {"sha256": _sha(raw), "artifact": raw.decode("utf-8")}}


def _review_binding_errors(document, evidence):
    review = evidence["review"]
    original = json.loads(evidence["inputArtifact"])
    if "dependencies" in review:
        if review["inputSha256"] != evidence["inputSha256"]:
            return ["Publication authorization has a stale original input hash."]
        expected = public_document(original, review["dependencies"])
    else:
        from solution_manager.authoring.workbook_updates import _canonical, _review_digest
        from solution_manager.authoring.native_workbooks import _canonical_payload_sha256
        baseline = json.loads(evidence["baselineArtifact"])
        if (review["reviewSha256"] != _review_digest(review)
                or review["baseline"]["sha256"] != evidence["baselineSha256"]
                or review["baseline"]["canonicalDocumentSha256"] != _canonical(baseline)):
            return ["Local update review or historical baseline binding is stale."]
        original["contentProvenance"] = deepcopy(baseline["contentProvenance"])
        if (review["canonicalDocumentSha256"] != _canonical(original)
                or review["canonicalPayloadSha256"] != _canonical_payload_sha256(original)):
            return ["Local update authorization does not bind the current authored payload."]
        expected = public_document(original)
    if digest(expected) != digest(document):
        return ["Local authorization is stale for the current public artifact/dependencies."]
    return []


def publication_errors(solution, document, *, public_ref=None):
    """Authoring requires a local receipt; explicit reproduction is not review."""
    root = _root(solution)
    if not is_public(document):
        return ["Published authored workbooks must be clean; run workbook-publication-plan/clean."]
    from solution_manager.migration.workbooks import validate_workbooks
    validation = validate_workbooks(root, selected_only=True, _documents=[
        (root / "XDR Workbooks" / "publication.json", document)])
    errors = [error for row in validation["results"] for error in row["errors"]]
    if errors:
        return errors
    if public_ref is not None:
        try:
            from solution_manager.migration.workbooks import selected_workbook_files
            commit = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "--verify", "--end-of-options",
                 public_ref + "^{commit}"], capture_output=True, text=True, check=True).stdout.strip()
            top = Path(subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                                      capture_output=True, text=True, check=True).stdout.strip())
            matches = []
            for path in selected_workbook_files(root):
                if digest(_document(path)) == digest(document):
                    relative = path.relative_to(top).as_posix()
                    raw = subprocess.run(["git", "-C", str(top), "show", commit + ":" + relative],
                                         capture_output=True, check=True).stdout
                    matches.append(digest(json.loads(raw)) == digest(document))
            if matches == [True]:
                return []
            return ["Reproduction requires the exact public workbook at the explicit Git ref."]
        except (OSError, ValueError, subprocess.CalledProcessError) as exc:
            return ["Cannot verify public reproduction ref: " + str(exc)]
    path = _receipt_path(root, document)
    try:
        receipt = json.loads(path.read_bytes())
        claimed = receipt.pop("receiptSha256")
        if claimed != digest(receipt) or receipt["canonicalDocumentSha256"] != digest(document):
            return ["Local workbook receipt is stale."]
        evidence = receipt["evidence"]
        if digest(evidence["publicDocument"]) != digest(document):
            return ["Local workbook receipt does not bind the exact current document."]
        review = evidence["review"]
        if (review["decision"] != "accept" or not review["actor"].strip()
                or not review["reference"].strip()):
            return ["Local authoring receipt requires explicit authorization."]
        if evidence["inputSha256"] != _sha(evidence["inputArtifact"].encode("utf-8")):
            return ["Local historical source/proof hash is stale."]
        if "baselineArtifact" in evidence and evidence["baselineSha256"] != _sha(
                evidence["baselineArtifact"].encode("utf-8")):
            return ["Local historical baseline hash is stale."]
        for record in evidence.get("sourceArtifacts", {}).values():
            if record["sha256"] != _sha(record["artifact"].encode("utf-8")):
                return ["Local historical raw source hash is stale."]
        return _review_binding_errors(document, evidence)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return ["Current hash-bound local authoring receipt required; run an explicit review: " + str(exc)]


def plan_publication(solution, content, *, _raw=None):
    root = _root(solution)
    path = _path(root, content)
    if not content.startswith("XDR Workbooks/") or path.suffix.lower() != ".json":
        raise ValueError("Publication content must be XDR Workbooks JSON.")
    raw = path.read_bytes() if _raw is None else _raw
    document = _load_json(raw)
    if (not isinstance(document, dict) or document.get("version") != "Notebook/1.0"
            or not isinstance(document.get("items"), list)):
        raise ValueError("Workbook must be a complete Notebook/1.0 object.")
    from solution_manager.migration.workbooks import validate_workbooks
    validation = validate_workbooks(root, selected_only=True, _documents=[(path, document)])
    if validation["invalid"]:
        raise ValueError("Input proof/structure failed: " + "; ".join(validation["results"][0]["errors"]))
    dependencies = {key: deepcopy(document["contentProvenance"].get(key, [])) for key in DEPENDENCIES}
    # Expose missing current table prerequisites, never invent connector coverage.
    tables = set()
    provenance = document["contentProvenance"]
    if "authoredReview" in provenance:
        tables = {table for query in provenance["authoredReview"]["queries"] for table in query["tables"]}
    else:
        for surface in workbook.query_surfaces(document):
            aliases = {row["functionAlias"] for row in dependencies["requiredWorkspaceFunctions"]}
            declared = {table for row in dependencies["requiredWorkloads"] for table in row["dataTypes"]}
            tables.update(_query(surface, allowed_tables=declared, allowed_functions=aliases,
                                 allow_sentinel=provenance.get("origin") != "native-xdr"))
    declared = {table for row in dependencies["requiredWorkloads"] for table in row["dataTypes"]}
    for table in sorted(tables - declared):
        workload = TABLE_WORKLOADS.get(table)
        if workload is None:
            raise ValueError("Explicit workload mapping required for current table: " + table)
        row = next((row for row in dependencies["requiredWorkloads"] if row["workload"] == workload), None)
        if row is None:
            row = {"workload": workload, "dataTypes": []}
            dependencies["requiredWorkloads"].append(row)
        row["dataTypes"].append(table)
    return {"inputSha256": _sha(raw), "dependencies": dependencies,
            "dependencyErrors": sorted(set(validate_public_document(
                root, public_document(document, dependencies)))),
            "actor": "", "reference": "", "decision": None}


def clean_publication(solution, content, expected_sha256, review):
    root = _root(solution)
    path = _path(root, content)
    raw = path.read_bytes()
    expected = plan_publication(root, content, _raw=raw)
    if not isinstance(review, dict):
        raise ValueError("Publication review must be an object.")
    if expected_sha256 != _sha(raw) or review.get("inputSha256") != expected_sha256:
        raise ValueError("Original workbook hash changed; fresh publication review required.")
    if set(review) != set(expected):
        raise ValueError("Publication review requires exactly the plan fields.")
    if review["dependencyErrors"] != expected["dependencyErrors"]:
        raise ValueError("Publication review diagnostics differ from the current plan.")
    if review["decision"] != "accept" or any(
            not isinstance(review[field], str) or not review[field].strip()
            for field in ("actor", "reference")):
        raise ValueError("Publication cleanup requires explicit local actor/reference/accept authorization.")
    dependencies = review["dependencies"]
    if not isinstance(dependencies, dict) or set(dependencies) != set(DEPENDENCIES):
        raise ValueError("Publication dependency fields must match the plan.")
    original = _load_json(raw)
    document = public_document(original, dependencies)
    from solution_manager.migration.workbooks import authored_schema_errors
    errors = authored_schema_errors(document) + validate_public_document(root, document)
    if errors:
        raise ValueError("; ".join(errors))
    if dependencies["requiredWorkspaceFunctions"] != expected["dependencies"]["requiredWorkspaceFunctions"]:
        raise ValueError("Cleanup cannot change workspace function dependencies.")
    for key, identity in (("requiredWorkloads", "workload"), ("requiredDataConnectors", "connectorId")):
        for row in expected["dependencies"][key]:
            if not any(other[identity] == row[identity] and set(row["dataTypes"]) <= set(other["dataTypes"])
                       for other in dependencies[key]):
                raise ValueError("Cleanup cannot remove existing/discovered dependencies.")
    receipt = retain_receipt(root, document, {
        "publicDocument": document, "inputSha256": _sha(raw),
        "inputArtifact": raw.decode("utf-8"), "review": review,
        "sourceArtifacts": source_evidence(root, original),
    })
    _write(path, (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8"), raw)
    return {"path": content, "sha256": _sha(path.read_bytes()), "localReceipt": receipt,
            "runtimeQualified": False}


def main():
    if not (3, 11) <= sys.version_info[:2] < (3, 13):
        raise ValueError("Workbook publication requires Python 3.11 or 3.12.")
    document = json.loads(sys.stdin.read())
    errors = publication_errors(sys.argv[1], document,
                                public_ref=os.environ.get("SENTINEL_XDR_WORKBOOK_PUBLIC_REF"))
    print(json.dumps({"errors": errors}))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
