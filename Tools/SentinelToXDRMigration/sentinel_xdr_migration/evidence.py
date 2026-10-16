"""Explicit, local-only public evidence projection; never a resumable state store."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml

from . import __version__
from .authoring_contract import AuthoringContract, calculate_coverage, validate_authoring_contract
from .artifacts import RUN_MARKER, report_directory
from .content_paths import content_path
from .workflow import STAGES

STATUSES = frozenset({
    "passed", "failed", "blocked", "pending", "running", "notRequired", "not-run",
    "completed", "inProgress", "in-progress", "not-started", "converted", "excluded", "needsReview",
    "conflict", "not-generated", "environment-blocked", "not-recorded",
})
REPORTS = {
    "conversion": "manifest.json",
    "structural": "structural-validation.json",
    "runtimeGraph": "runtime-validation.graph.json",
    "runtimeTriage": "runtime-validation.triage-mcp.json",
    "runtimeLogAnalytics": "runtime-validation.log-analytics-cli.json",
    "runtimeAzureMonitorSdk": "runtime-validation.azure-monitor-sdk.json",
    "packaging": "packaging.v3_1.json",
    "queryParity": "mock-query-parity.json",
    "alertParity": "alert-parity-report.json",
    "solutionReport": "migration-report.json",
}
COUNTS = (
    "total", "converted", "excluded", "needsReview", "reviewRequired",
    "deploymentReady", "conflicts", "valid", "invalid", "blocked", "notRun",
    "xdrDetectionCount",
)
CONTENT_FOLDERS = {"Analytic Rules", "Analytics Rules", "XDR Detections", "Package", "Data"}
SENSITIVE = re.compile(
    r"(?i)(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    r"|password|passwd|secret|token|credential|bearer|tenant|subscription|workspace"
    r"|[A-Za-z0-9_-]{48,}|(?:^|/)Users/|(?:^|/)home/)"
)


def _object(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _enum(value: Any, allowed=STATUSES) -> str:
    return value if isinstance(value, str) and value in allowed else "unknown"


def _count(value: Any) -> int | None:
    return value if type(value) is int and 0 <= value <= 2**53 - 1 else None


def _version(value: Any) -> str | None:
    return value if isinstance(value, str) and re.fullmatch(r"\d{1,6}\.\d{1,6}\.\d{1,6}", value) else None


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _timestamp(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)", value
    ):
        return "unknown (not recorded)"
    return value


def _public_solution_name(value: Any) -> str | None:
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 .()-]{0,119}", value)
        or SENSITIVE.search(value)
        or re.search(r"(?i)(?:\bhttps?\b|\bwww\b|\.\.)", value)
    ):
        return None
    return value


def _public_authoring_rule_id(value: Any) -> str | None:
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value)
        or SENSITIVE.search(value)
        or re.search(r"(?i)(?:https?\b|www\b|\.{2})", value)
    ):
        return None
    return value


def _authoring_contract_projection(contract: AuthoringContract) -> dict:
    results = {result.rule_id: result for result in contract.results}
    rules = []
    for index, source_rule in enumerate(sorted(contract.inventory, key=lambda rule: rule.rule_id), start=1):
        result = results[source_rule.rule_id]
        findings = Counter(finding.kind for finding in result.findings)
        digests = {
            source_rule.sha256,
            *(reference.sha256 for reference in source_rule.evidence_references),
            *(reference.sha256 for reference in result.evidence_references),
            *(reference.sha256 for reference in result.qualification_evidence_references),
            *(reference.sha256 for finding in result.findings for reference in finding.evidence_references),
        }
        target_sha256 = result.target.sha256 if result.target is not None else None
        if target_sha256 is not None:
            digests.add(target_sha256)
        rule_id = _public_authoring_rule_id(source_rule.rule_id)
        rules.append({
            "inventoryIndex": index,
            "sourceRuleId": rule_id,
            "sourceRuleIdAvailability": "available" if rule_id is not None else "withheld",
            "outcome": result.status,
            "qualificationStatus": result.qualification_status,
            "targetStructurallyValid": result.target_structurally_valid,
            "reviewRequired": result.review_required,
            "unresolvedErrorCount": result.unresolved_error_count,
            "mappingAssumptionCount": len(result.mapping_assumptions),
            "assumptionFindingCount": findings["assumption"],
            "findingCounts": {
                "error": findings["error"],
                "warning": findings["warning"],
                "assumption": findings["assumption"],
            },
            "sourceSha256": source_rule.sha256,
            "targetSha256": target_sha256,
            "evidenceDigests": sorted(digests),
        })
    coverage = calculate_coverage(contract)
    return {
        "schemaVersion": "1.0.0",
        "runId": contract.run_id,
        "inventoryComplete": True,
        "rules": rules,
        "coverage": {
            "N": coverage.N,
            "M": coverage.M,
            "E": coverage.E,
            "qualified": coverage.qualified,
            "untested": coverage.untested,
            "qualificationFailed": coverage.qualification_failed,
            "migrationThreshold": {
                "successPercent": 80,
                "comparison": "greaterThanOrEqual",
                "formula": "100*M >= 80*N",
                "met": coverage.migration_threshold_met,
            },
            "errorStopThreshold": {
                "errorPercent": 50,
                "comparison": "strictlyGreaterThan",
                "formula": "100*E > 50*N",
                "reached": coverage.stop_threshold_reached,
            },
            "scope": "advisory-only",
            "coverageAuthorizesOperations": False,
            "packagingAuthorized": False,
            "deploymentAuthorized": False,
            "ingestionAuthorized": False,
            "prCreationAuthorized": False,
        },
        "evidenceDigestBinding": "validated-record-only-not-rehashed-or-authenticated",
    }


class _Snapshot:
    def __init__(self, root: Path, run: Path):
        self.root, self.run = root, run
        self.inputs: dict[Path, bytes | None] = {}

    def read(self, path: Path) -> bytes | None:
        path = content_path(self.root, path.relative_to(self.root))
        if path not in self.inputs:
            self.inputs[path] = path.read_bytes() if path.is_file() else None
        return self.inputs[path]

    def document(self, path: Path) -> tuple[dict, str]:
        data = self.read(path)
        if data is None:
            return {}, "missing"
        try:
            value = json.loads(data)
        except (ValueError, UnicodeError):
            return {}, "invalid"
        return (value, "available") if isinstance(value, dict) else ({}, "invalid")

    def reference(self, value: Any) -> dict:
        # Only content references can contribute variable paths. No arbitrary log,
        # provider, URL, external-file, or stage-evidence reference is copied.
        if not isinstance(value, str):
            return {"availability": "missing", "path": None, "sha256": None}
        text = value.replace("\\", "/")
        if text.startswith(self.root.as_posix() + "/"):
            text = text[len(self.root.as_posix()) + 1:]
        parts = text.split("/")
        if (
            not re.fullmatch(r"[A-Za-z0-9 _./()-]{1,240}", text)
            or SENSITIVE.search(text)
            or parts[0] not in CONTENT_FOLDERS
            or any(p in {"", ".", ".."} or p.lower() in {"logs", "reports", "evidence"} for p in parts)
        ):
            return {"availability": "withheld", "path": None, "sha256": None}
        try:
            path = content_path(self.root, text)
            data = self.read(path)
        except (OSError, ValueError):
            return {"availability": "unsafe", "path": None, "sha256": None}
        return {
            "availability": "available" if data is not None else "missing",
            "path": text, "sha256": _hash(data) if data is not None else None,
        }

    def unchanged(self) -> bool:
        return all(
            (path.read_bytes() if path.is_file() else None) == value
            for path, value in self.inputs.items()
        )


def _solution_metadata(snapshot: _Snapshot) -> dict:
    name = _public_solution_name(snapshot.root.name)
    result = {
        "name": name,
        "nameAvailability": "available" if name else "withheld",
        "nameSource": "solution-folder",
        "currentVersion": None,
        "versionAvailability": "missing",
        "versionObservation": "export",
        "versionSources": [],
        "requestedTargetVersion": None,
        "requestedTargetVersionAvailability": "unsupported",
    }
    metadata_path = snapshot.root / "SolutionMetadata.json"
    data_directory = content_path(snapshot.root, "Data")
    data_paths = sorted(data_directory.glob("Solution_*.json"))
    if len(data_paths) > 1:
        result["versionAvailability"] = "ambiguous"
        return result
    versions = []
    for kind, path in [("solution-metadata", metadata_path), *[("solution-data", path) for path in data_paths]]:
        document, availability = snapshot.document(path)
        candidates = [value for key, value in document.items() if key.lower() == "version"]
        version = _version(candidates[0]) if len(candidates) == 1 else None
        if availability == "available" and not candidates:
            availability = "not-recorded"
        elif availability == "available" and version is None:
            availability = "invalid"
        result["versionSources"].append({
            "kind": kind, "availability": availability, "version": version,
            "sha256": _hash(snapshot.inputs[path]) if snapshot.inputs[path] is not None else None,
        })
        if availability not in {"missing", "not-recorded"}:
            versions.append(version)
    if versions:
        if None in versions:
            result["versionAvailability"] = "invalid"
        elif len(set(versions)) != 1:
            result["versionAvailability"] = "conflict"
        else:
            result.update(currentVersion=versions[0], versionAvailability="available")
    return result


def _provenance(snapshot: _Snapshot, source: dict, output: dict) -> dict:
    result = {"sourceQuery": "unavailable", "historicalValidationBinding": "unsupported"}
    if source["availability"] != "available" or output["availability"] != "available":
        return result
    try:
        original = _object(yaml.safe_load(snapshot.read(snapshot.root / source["path"])))
        generated = _object(yaml.safe_load(snapshot.read(snapshot.root / output["path"])))
        provenance = _object(_object(generated.get("contentProvenance")).get("source"))
        query = original.get("query")
        digest = provenance.get("querySha256")
        if isinstance(query, str) and isinstance(digest, str) and re.fullmatch("[0-9a-f]{64}", digest):
            result["sourceQuery"] = (
                "matches" if digest == _hash(query.encode("utf-8"))
                and provenance.get("path") == source["path"]
                and provenance.get("id") == original.get("id") else "mismatch"
            )
        result["sourceVersion"] = _version(original.get("version"))
        result["outputVersion"] = _version(generated.get("version"))
        result["converterVersion"] = _version(_object(_object(generated.get("contentProvenance")).get("conversion")).get("version"))
    except (ValueError, yaml.YAMLError, UnicodeError):
        result["sourceQuery"] = "invalid"
    return result


def _item(
    snapshot: _Snapshot,
    kind: str,
    value: Any,
    index: int,
    *,
    provider: Any = None,
) -> dict:
    item = _object(value)
    status = item.get("status")
    if status is None:
        for key in ("valid", "passed"):
            if type(item.get(key)) is bool:
                status = "passed" if item[key] else "failed"
                break
    result = {
        "index": index, "recordedStatus": _enum(status),
        "errorCount": len(item["errors"]) if isinstance(item.get("errors"), list) else None,
        "errorDetails": "withheld" if any(item.get(key) for key in ("errors", "error", "errorDetails")) else "not-recorded",
    }
    if kind == "conversion":
        source = snapshot.reference(item.get("sourceRelativePath") or item.get("source"))
        output = snapshot.reference(item.get("outputRelativePath") or item.get("output"))
        result.update(source=source, output=output, provenance=_provenance(snapshot, source, output))
        result["reviewRequired"] = item.get("reviewRequired") if type(item.get("reviewRequired")) is bool else None
    elif kind in {"runtimeGraph", "runtimeTriage", "runtimeLogAnalytics", "runtimeAzureMonitorSdk"}:
        result["provider"] = _enum(
            provider,
            {"graph", "triage-mcp", "log-analytics-cli", "azure-monitor-sdk"},
        )
        detection = item.get("detection")
        output_reference = (
            f"XDR Detections/{detection}" if isinstance(detection, str) else None
        )
        output_ref = snapshot.reference(output_reference)
        result["content"] = output_ref
        query = None
        try:
            if output_ref["availability"] == "available":
                generated = _object(yaml.safe_load(snapshot.read(
                    content_path(snapshot.root, output_ref["path"])
                )))
                if kind == "runtimeGraph":
                    query = _object(_object(generated.get("properties")).get("queryCondition")).get("queryText")
                else:
                    source_path = _object(
                        _object(generated.get("contentProvenance")).get("source")
                    ).get("path")
                    source_ref = snapshot.reference(source_path)
                    if source_ref["availability"] == "available":
                        source = _object(yaml.safe_load(snapshot.read(
                            content_path(snapshot.root, source_ref["path"])
                        )))
                        query = source.get("query")
        except (OSError, ValueError, yaml.YAMLError, UnicodeError):
            query = None
        expected_hash = _hash(query.encode("utf-8")) if isinstance(query, str) else None
        recorded_hash = item.get("querySha256")
        result["queryHashBinding"] = {
            "surface": (
                "advanced-hunting" if kind == "runtimeGraph" else "sentinel"
            ),
            "status": (
                "matches" if expected_hash and recorded_hash == expected_hash
                else "stale-or-missing"
            ),
            "recordedQuerySha256": (
                recorded_hash if isinstance(recorded_hash, str)
                and re.fullmatch(r"[0-9a-f]{64}", recorded_hash) else None
            ),
            "currentQuerySha256": expected_hash,
        }
    elif kind == "solutionReport":
        result["source"] = snapshot.reference(item.get("sourceFile"))
        result["structuralStatus"] = _enum(_object(item.get("customDetection")).get("structuralStatus"))
        result["conversionStatus"] = _enum(_object(item.get("customDetection")).get("conversionStatus"))
        for surface in ("analyticRule", "customDetection"):
            details = _object(item.get(surface))
            runtime = details.get("runtime")
            result[surface] = {
                "alertStatus": _enum(details.get("alertStatus")),
                "deploymentStatus": _enum(details.get("deploymentStatus"), STATUSES | {"created", "updated", "validated-by-alert-parity"}),
                "runtime": [
                    {"recordedStatus": _enum(_object(entry).get("status")),
                     "provider": _enum(_object(entry).get("provider"), {"graph", "triage-mcp", "log-analytics-cli", "azure-monitor-sdk"})}
                    for entry in runtime
                ] if isinstance(runtime, list) else [],
                "runtimeAvailability": "available" if isinstance(runtime, list) and runtime else "not-recorded",
            }
    else:
        reference = item.get("file")
        if reference is None and isinstance(item.get("detection"), str):
            reference = "XDR Detections/" + item["detection"]
        result["content"] = snapshot.reference(reference)
    return result


def _report(snapshot: _Snapshot, kind: str, name: str) -> dict:
    path = snapshot.run / name
    document, availability = snapshot.document(path)
    result = {
        "availability": availability,
        "path": path.relative_to(snapshot.root).as_posix(),
        "sha256": _hash(snapshot.inputs[path]) if snapshot.inputs[path] is not None else None,
        "recordedStatus": _enum(document.get("status")),
        "verification": "recorded-only-not-attested",
    }
    if document.get("runId", snapshot.run.name) != snapshot.run.name:
        result.update(availability="run-mismatch", recordedStatus="unknown")
        return result
    result["counts"] = {key: _count(document[key]) for key in COUNTS if key in document}
    collection = "rules" if kind == "solutionReport" else "comparisons" if kind in {"queryParity", "alertParity"} else "results"
    values = document.get(collection)
    result["itemsAvailability"] = "available" if isinstance(values, list) else "missing-or-unsupported"
    result["items"] = [
        _item(snapshot, kind, item, index, provider=document.get("provider"))
        for index, item in enumerate(values or [])
    ] if isinstance(values, list) else []
    if kind == "packaging":
        result.update(
            packager=_enum(document.get("packager"), {"V3.1", "V4", "V3"}),
            version=_version(document.get("version")),
            versionBump=_enum(document.get("versionBump"), {"none", "patch", "minor", "major"}),
            artifacts={key: snapshot.reference(document.get(key)) for key in (
                "solutionData", "mainTemplate", "createUiDefinition", "testParameters", "zip",
            )},
            warningCount=len(document["warnings"]) if isinstance(document.get("warnings"), list) else None,
        )
    return result


def _markdown(evidence: dict) -> str:
    solution = _object(evidence.get("solution"))
    exporter = _object(evidence.get("exporter"))
    name = _public_solution_name(solution.get("name")) or "unknown"
    current_version = _version(solution.get("currentVersion")) or "unknown"
    requested_target = _version(solution.get("requestedTargetVersion")) or "unknown (not recorded)"
    exported_at = _timestamp(evidence.get("exportedAt"))
    header_update = solution.get("versionObservation") == "header-update"
    observation = "header update" if header_update else "export"
    lines = [
        f"# Migration evidence — {name}", "", f"Solution: **{name}**",
        f"Run: `{evidence['runId']}`",
        f"Profile: **{evidence['profile']}**",
        f"Recorded workflow status: **{evidence['recordedWorkflowStatus']}**",
        f"Current solution version at {observation}: **{current_version}** (not a packaging claim)",
        f"Requested version action: **{_enum(evidence.get('versionDecision'), {'none', 'patch', 'minor', 'major'})}**",
        f"Requested target solution version: **{requested_target}** (not a packaged version)",
        f"Evidence exported at (UTC): **{exported_at}**",
        f"Evidence exporter: **sentinel-xdr-migration {_version(exporter.get('version')) or 'unknown'}** (export tool, not historical run version)",
        f"Exporter Python: **{_version(exporter.get('pythonVersion')) or 'unknown'}**", "",
    ]
    if header_update:
        renderer = _object(evidence.get("headerRenderer"))
        lines.extend([
            f"Header updated at (UTC): **{_timestamp(evidence.get('headerUpdatedAt'))}**",
            f"Header renderer: **sentinel-xdr-migration {_version(renderer.get('version')) or 'unknown'}**",
            "Header-only update: original results, hashes and export identity are preserved;",
            "the current solution version above is a new header observation, not an export-time fact.", "",
        ])
    lines.extend([
        "**This is a local, curated snapshot, not trusted attestation or a new test run.**",
        "Reported passes are not independently verified. Missing evidence is not a pass.",
        "Content hashes describe export-time bytes, not proof of what historical tests ran.", "",
        "## All workflow stages", "", "| Stage | Recorded status | Attempts |",
        "| --- | --- | --- |",
    ])
    for stage, value in evidence["stages"].items():
        lines.append(f"| {stage} | {value['recordedStatus']} | {value['attempts']} |")
    lines.extend(["", "## Evidence coverage", "", "| Report | Availability | Recorded status | Items | Recorded item outcomes |", "| --- | --- | --- | --- | --- |"])
    for name, value in evidence["reports"].items():
        key = "structuralStatus" if name == "solutionReport" else "recordedStatus"
        outcomes = Counter(item.get(key, "unknown") for item in value.get("items", []))
        label = "structural: " if name == "solutionReport" and outcomes else ""
        counts = label + ", ".join(f"{status}={count}" for status, count in sorted(outcomes.items()))
        bindings = Counter(
            _object(item.get("queryHashBinding")).get("status", "not-applicable")
            for item in value.get("items", [])
        )
        if bindings and name.startswith("runtime"):
            counts += "; query hashes: " + ", ".join(
                f"{status}={count}" for status, count in sorted(bindings.items())
            )
        lines.append(f"| {name} | {value['availability']} | {value['recordedStatus']} | {len(value.get('items', []))} | {counts or 'not-recorded'} |")
    mismatches = sum(
        item.get("provenance", {}).get("sourceQuery") == "mismatch"
        for item in evidence["reports"]["conversion"].get("items", [])
    )
    lines.extend([
        "", "See `evidence.json` for every result (including failures, blocks and not-run),",
        "relative paths, hashes, version decisions and provenance mismatches.", "",
        f"Source-query provenance mismatches detected: **{mismatches}**.",
        "Missing/unsupported provenance remains unverified, even when this count is zero.", "",
    ])
    authoring_contract = _object(evidence.get("authoringContract"))
    if authoring_contract:
        coverage = _object(authoring_contract.get("coverage"))
        migration_threshold = _object(coverage.get("migrationThreshold"))
        error_threshold = _object(coverage.get("errorStopThreshold"))
        lines.extend([
            "## B1 authoring-contract projection", "",
            "This is a validated-record projection, not an attestation; evidence digests were not rehashed.",
            "Coverage is advisory only and never authorizes packaging, deployment, ingestion, or PR creation.", "",
            f"Inventory coverage: **N={coverage.get('N', 0)}, M={coverage.get('M', 0)}, E={coverage.get('E', 0)}**",
            f"Migration threshold: **{migration_threshold.get('successPercent', 80)}% success, "
            f"{migration_threshold.get('comparison', 'greaterThanOrEqual')}, "
            f"{migration_threshold.get('formula', '100*M >= 80*N')}, "
            f"met={str(migration_threshold.get('met', False)).lower()}**",
            f"Error stop threshold: **>{error_threshold.get('errorPercent', 50)}% errors, "
            f"{error_threshold.get('formula', '100*E > 50*N')}, "
            f"reached={str(error_threshold.get('reached', False)).lower()}**", "",
            "| Source rule ID | Outcome | Qualification | Target valid | Review required | Unresolved errors | Mapping assumptions | Assumption findings | Evidence digests |",
            "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ])
        for rule in authoring_contract.get("rules", []):
            item = _object(rule)
            rule_id = item.get("sourceRuleId") or f"withheld (inventory {item.get('inventoryIndex', 'unknown')})"
            lines.append(
                f"| {rule_id} | {item.get('outcome', 'unknown')} | "
                f"{item.get('qualificationStatus', 'unknown')} | "
                f"{str(item.get('targetStructurallyValid', False)).lower()} | "
                f"{str(item.get('reviewRequired', False)).lower()} | "
                f"{item.get('unresolvedErrorCount', 0)} | "
                f"{item.get('mappingAssumptionCount', 0)} | "
                f"{item.get('assumptionFindingCount', 0)} | "
                f"{', '.join(item.get('evidenceDigests', [])) or 'not-recorded'} |"
            )
        lines.append("")
    lines.extend([
        "## Limitations", "",
        "- Raw messages, provider records, alerts, credentials and lab identities are omitted.",
        "- Historical commands/tool versions and baseline decisions have no supported persisted contract.",
        "- New runtime reports bind results to the exact source or Advanced Hunting query hash; legacy or mismatched hashes are stale/unbound. Hashes do not attest that a provider executed the query.",
        "- Unknown fields/statuses are excluded or marked unknown, never interpreted as success.",
        "- This directory is never read as workflow state or included in Marketplace packages.", "",
    ])
    return "\n".join(lines)


def export_evidence(
    solution: str | Path,
    *,
    authoring_contract: Mapping[str, Any] | None = None,
) -> dict:
    root = Path(solution).expanduser().resolve()
    run = report_directory(root)
    if not (run / RUN_MARKER).is_file():
        raise ValueError("evidence export requires an existing run marker")
    # Generated run IDs are public opaque identifiers; custom sensitive names fail closed.
    if not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{32}", run.name) and SENSITIVE.search(run.name):
        raise ValueError("run ID is not suitable for public evidence")
    destination = content_path(root, f"Evidence/{run.name}")
    if destination.exists():
        raise ValueError("evidence snapshot already exists; exports never overwrite snapshots")
    snapshot = _Snapshot(root, run)
    marker, marker_status = snapshot.document(run / RUN_MARKER)
    if marker_status != "available" or marker.get("runId") != run.name:
        raise ValueError("invalid evidence run identity")
    contract_projection = None
    if authoring_contract is not None:
        validated_contract = validate_authoring_contract(authoring_contract)
        if validated_contract.run_id != run.name:
            raise ValueError("authoring contract does not match the selected evidence run")
        contract_projection = _authoring_contract_projection(validated_contract)
    state, state_status = snapshot.document(run / "workflow-state.json")
    if state and state.get("runId") != run.name:
        raise ValueError("workflow state does not match the selected evidence run")
    context = _object(state.get("context"))
    evidence = {
        "schemaVersion": "1.0.0", "runId": run.name,
        "solution": _solution_metadata(snapshot),
        "exportedAt": _utc_now(),
        "profile": _enum(context.get("workflowProfile"), {"authoring", "qualification"}),
        "recordedWorkflowStatus": _enum(state.get("workflowStatus")),
        "workflowEvidence": {
            "availability": state_status,
            "path": (run / "workflow-state.json").relative_to(root).as_posix(),
            "sha256": _hash(snapshot.inputs[run / "workflow-state.json"]) if state_status != "missing" else None,
        },
        "versionDecision": _enum(context.get("versionBump"), {"none", "patch", "minor", "major"}),
        "baselineDecision": {"availability": "unsupported"},
        "historicalCommands": {"availability": "unsupported"},
        "historicalToolVersions": {"availability": "unsupported"},
        "exporter": {
            "name": "sentinel-xdr-migration", "version": __version__,
            "pythonVersion": ".".join(map(str, sys.version_info[:3])),
            "command": ["sentinel-xdr-migration", "export-evidence", "--solution", ".", "--run-id", run.name],
        },
        "verification": "recorded-only-not-attested",
        "stages": {},
        "reports": {},
    }
    for stage in STAGES:
        value = _object(_object(state.get("stages")).get(stage))
        evidence["stages"][stage] = {
            "recordedStatus": _enum(value.get("status")),
            "attempts": _count(value.get("attempts")),
            "runtimeStatus": _enum(_object(value.get("artifacts")).get("runtimeStatus")),
            "details": "withheld" if value.get("message") else "not-recorded",
        }
    evidence["reports"] = {kind: _report(snapshot, kind, name) for kind, name in REPORTS.items()}
    if contract_projection is not None:
        evidence["authoringContract"] = contract_projection
    payload = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    summary = _markdown(evidence)
    if not snapshot.unchanged():
        raise ValueError("evidence inputs changed during export; retry after the run is stable")
    destination.parent.mkdir(exist_ok=True)
    destination.mkdir()  # Atomic claim: no concurrent or previous snapshot is overwritten.
    try:
        (destination / "evidence.json").write_text(payload, encoding="utf-8")
        (destination / "summary.md").write_text(summary, encoding="utf-8")
    except OSError:
        for name in ("evidence.json", "summary.md"):
            (destination / name).unlink(missing_ok=True)
        destination.rmdir()
        raise
    return {"status": "exported", "runId": run.name, "evidence": f"Evidence/{run.name}/evidence.json", "summary": f"Evidence/{run.name}/summary.md"}
