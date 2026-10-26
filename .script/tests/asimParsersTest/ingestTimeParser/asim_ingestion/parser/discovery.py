"""ITP-centered target discovery and optional QTP resolution."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence

import yaml

from .common import (
    MANIFEST_VERSION,
    ParserRecord,
    PairResolution,
    _get_nested,
    _repo_relative_path,
    classify_changed_path,
    classify_parser_path,
    load_yaml_file,
    normalize_changed_path,
)
from .kql import (
    _identity_key,
    _query_uses_source_table,
    _token_overlap,
    resolve_source_specific_fixture,
)

def build_parser_record(repo_root: Path, relative_path: str) -> ParserRecord:
    kind = classify_parser_path(relative_path)
    if kind is None:
        raise ValueError(f"Not a supported ASIM parser path: {relative_path}")
    document = load_yaml_file(repo_root / relative_path)
    parser_name = document.get("ParserName")
    schema = _get_nested(document, "Normalization", "Schema")
    schema_version = _get_nested(document, "Normalization", "Version")
    product = _get_nested(document, "Product", "Name")
    parser_query = document.get("ParserQuery")
    required_values = {
        "ParserName": parser_name,
        "Normalization.Schema": schema,
        "Product.Name": product,
        "ParserQuery": parser_query,
    }
    if kind == "ingest-time":
        required_values["Normalization.Version"] = schema_version
    missing = [
        name
        for name, value in required_values.items()
        if not isinstance(value, str) or not value.strip()
    ]
    if missing:
        raise ValueError(
            f"{relative_path} is missing required parser metadata: {', '.join(missing)}."
        )
    source_raw_table = (
        document.get("SourceRawTable")
        if kind == "ingest-time"
        else None
    )
    target_asim_table = (
        document.get("TargetASIMTable")
        if kind == "ingest-time"
        else None
    )
    event_vendor: str | None = None
    event_product: str | None = None
    fixture_path: str | None = None
    fixture_errors: list[str] = []
    if kind == "ingest-time":
        if not isinstance(source_raw_table, str) or not source_raw_table:
            fixture_errors.append(
                f"{relative_path} is missing SourceRawTable."
            )
        else:
            try:
                (
                    event_vendor,
                    event_product,
                    fixture_path,
                ) = resolve_source_specific_fixture(
                    parser_query,
                    schema,
                    source_raw_table,
                )
            except ValueError as exc:
                fixture_errors.append(str(exc))
            else:
                if not (repo_root / fixture_path).is_file():
                    fixture_errors.append(
                        "Missing source-table-specific fixture: "
                        f"{fixture_path}."
                    )
    return ParserRecord(
        path=relative_path,
        kind=kind,
        document=document,
        parser_name=parser_name,
        schema=schema,
        schema_version=schema_version,
        product=product,
        parser_query=parser_query,
        source_raw_table=source_raw_table,
        target_asim_table=target_asim_table,
        event_vendor=event_vendor,
        event_product=event_product,
        fixture_path=fixture_path,
        fixture_errors=tuple(fixture_errors),
    )


def _iter_parser_paths(repo_root: Path, kind: str) -> Iterable[str]:
    if kind == "query-time":
        pattern = "Parsers/ASim*/Parsers/ASim*.yaml"
    else:
        pattern = "Parsers/ASim*/IngestTimeParsers/*.yaml"
    for path in sorted(repo_root.glob(pattern)):
        relative_path = _repo_relative_path(repo_root, path)
        if classify_parser_path(relative_path) == kind:
            yield relative_path


def resolve_query_time_pair(
    ingest_record: ParserRecord, query_records: Sequence[ParserRecord]
) -> PairResolution:
    eligible = [
        record
        for record in query_records
        if record.schema == ingest_record.schema
        and isinstance(ingest_record.source_raw_table, str)
        and _identity_key(record.product)
        == _identity_key(ingest_record.product)
        and _query_uses_source_table(
            record.parser_query, ingest_record.source_raw_table
        )
    ]

    ingestion_identities = {
        _identity_key(ingest_record.parser_name),
        _identity_key(PurePosixPath(ingest_record.path).stem),
    }
    identity_matches = [
        record
        for record in eligible
        if ingestion_identities
        & {
            _identity_key(record.parser_name),
            _identity_key(
                str(record.document.get("EquivalentBuiltInParser", ""))
            ),
            _identity_key(PurePosixPath(record.path).stem),
        }
    ]
    if identity_matches:
        candidates = identity_matches
        tier = "identity"
    else:
        candidates = eligible
        tier = "product"

    candidate_evidence = [
        {
            "path": record.path,
            "identityMatch": record in identity_matches,
            "productMatch": _identity_key(record.product)
            == _identity_key(ingest_record.product),
            "sourceTableMatch": True,
            "schemaMatch": True,
            "nameTokenOverlap": _token_overlap(
                ingest_record.parser_name, record.parser_name
            ),
        }
        for record in candidates
    ]
    evidence = {
        "tier": tier,
        "schema": ingest_record.schema,
        "sourceRawTable": ingest_record.source_raw_table,
        "candidates": candidate_evidence,
    }
    if len(candidates) == 1:
        return PairResolution(
            "paired", candidates[0], tuple(candidates), evidence
        )
    if len(candidates) > 1:
        return PairResolution("ambiguous", None, tuple(candidates), evidence)
    return PairResolution("unpaired", None, tuple(), evidence)


def _make_target_id(record: ParserRecord) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", record.parser_name.lower()).strip("-")
    return slug or hashlib.sha256(record.path.encode("utf-8")).hexdigest()[:12]


def _target_from_ingest(
    ingest_record: ParserRecord,
    resolution: PairResolution,
    trigger_path: str,
) -> dict[str, Any]:
    query_record = resolution.selected
    fixture_status = "resolved"
    if ingest_record.fixture_path is None:
        fixture_status = "invalid"
    elif ingest_record.fixture_errors:
        fixture_status = "missing"
    return {
        "targetId": _make_target_id(ingest_record),
        "triggerPaths": [trigger_path],
        "validationKind": "paired" if query_record else "ingest-only",
        "pairStatus": resolution.status,
        "queryTimeParserPath": query_record.path if query_record else None,
        "ingestTimeParserPath": ingest_record.path,
        "schema": ingest_record.schema,
        "schemaVersion": ingest_record.schema_version,
        "product": ingest_record.product,
        "sourceRawTable": ingest_record.source_raw_table,
        "targetASIMTable": ingest_record.target_asim_table,
        "eventVendor": ingest_record.event_vendor,
        "eventProduct": ingest_record.event_product,
        "fixturePath": ingest_record.fixture_path,
        "fixtureStatus": fixture_status,
        "pairCandidates": [record.path for record in resolution.candidates],
        "pairEvidence": resolution.evidence,
        "discoveryErrors": list(ingest_record.fixture_errors),
    }


def get_changed_files(repo_root: Path, base_ref: str) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "diff",
            "--name-only",
            "--diff-filter=AMRD",
            base_ref,
            "--",
            "Parsers",
            "Sample Data/ASIM",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        normalize_changed_path(line)
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def build_validation_manifest(
    repo_root: Path, changed_files: Sequence[str]
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    normalized_changes = sorted(
        {
            normalize_changed_path(path)
            for path in changed_files
            if classify_changed_path(path)
        }
    )
    index_errors: list[dict[str, str]] = []

    def load_index(kind: str) -> list[ParserRecord]:
        records: list[ParserRecord] = []
        for path in _iter_parser_paths(repo_root, kind):
            try:
                records.append(build_parser_record(repo_root, path))
            except (OSError, ValueError, yaml.YAMLError) as exc:
                index_errors.append({"path": path, "message": str(exc)})
        return records

    query_records = load_index("query-time")
    ingest_records = load_index("ingest-time")
    ingest_by_path = {record.path: record for record in ingest_records}
    resolutions = {
        record.path: resolve_query_time_pair(record, query_records)
        for record in ingest_records
    }
    query_to_ingest: dict[str, list[ParserRecord]] = {}
    fixture_to_ingest: dict[str, list[ParserRecord]] = {}
    for record in ingest_records:
        resolution = resolutions[record.path]
        if resolution.selected is not None:
            query_to_ingest.setdefault(
                resolution.selected.path, []
            ).append(record)
        if record.fixture_path is not None:
            fixture_to_ingest.setdefault(
                record.fixture_path, []
            ).append(record)

    targets: dict[str, dict[str, Any]] = {}

    def add_target(record: ParserRecord, trigger_path: str) -> None:
        target = targets.setdefault(
            record.path,
            _target_from_ingest(
                record,
                resolutions[record.path],
                trigger_path,
            ),
        )
        if trigger_path not in target["triggerPaths"]:
            target["triggerPaths"].append(trigger_path)

    for changed_path in normalized_changes:
        kind = classify_changed_path(changed_path)
        if kind == "ingest-time":
            record = ingest_by_path.get(changed_path)
            if record is None:
                discovery_errors = [
                    error["message"]
                    for error in index_errors
                    if error["path"] == changed_path
                ]
                if not discovery_errors:
                    discovery_errors.append(
                        "Changed ingestion-time parser does not exist "
                        f"in the current revision: {changed_path}."
                    )
                targets[f"invalid:{changed_path}"] = {
                    "targetId": re.sub(
                        r"[^a-z0-9]+",
                        "-",
                        PurePosixPath(changed_path).stem.lower(),
                    ).strip("-"),
                    "triggerPaths": [changed_path],
                    "validationKind": "ingest-only",
                    "pairStatus": "invalid",
                    "queryTimeParserPath": None,
                    "ingestTimeParserPath": changed_path,
                    "schema": None,
                    "schemaVersion": None,
                    "product": None,
                    "sourceRawTable": None,
                    "targetASIMTable": None,
                    "eventVendor": None,
                    "eventProduct": None,
                    "fixturePath": None,
                    "fixtureStatus": "invalid",
                    "pairCandidates": [],
                    "pairEvidence": {},
                    "discoveryErrors": discovery_errors,
                }
                continue
            add_target(record, changed_path)
            continue

        if kind == "query-time":
            for record in query_to_ingest.get(changed_path, []):
                add_target(record, changed_path)
            continue
        if kind == "fixture":
            for record in fixture_to_ingest.get(changed_path, []):
                add_target(record, changed_path)

    ordered_targets = sorted(
        targets.values(),
        key=lambda target: (
            str(target["schema"] or ""),
            str(target["targetId"]),
        ),
    )
    for target in ordered_targets:
        target["triggerPaths"] = sorted(set(target["triggerPaths"]))
    target_id_counts: dict[str, int] = {}
    for target in ordered_targets:
        target_id_counts[target["targetId"]] = (
            target_id_counts.get(target["targetId"], 0) + 1
        )
    for target in ordered_targets:
        if target_id_counts[target["targetId"]] <= 1:
            continue
        identity_path = (
            target["ingestTimeParserPath"]
            or target["queryTimeParserPath"]
            or target["triggerPaths"][0]
        )
        suffix = hashlib.sha256(identity_path.encode("utf-8")).hexdigest()[:8]
        target["targetId"] = f"{target['targetId']}-{suffix}"

    return {
        "version": MANIFEST_VERSION,
        "base": str(repo_root),
        "changedPaths": normalized_changes,
        "changedParserPaths": [
            path
            for path in normalized_changes
            if classify_parser_path(path) is not None
        ],
        "targets": ordered_targets,
        "indexErrors": index_errors,
    }
