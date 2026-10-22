"""Directional, hash-bound mapping evidence for Sentinel-to-XDR query conversion.

The module records evidence; it does not infer DCR inverses or execute queries.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from solution_manager.migration.catalog import (
    NATIVE_XDR_TABLES,
    PASSTHROUGH_TABLES,
    configured_column_renames,
    query_column_renames,
    query_has_ambiguous_table_scope,
    query_table_references,
)

SCHEMA_VERSION = "1.0.0"
_IDENTIFIERS = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")
_CAST = re.compile(
    r"(?is)^\s*(?:tostring|toint|tolong|toreal|todouble|todatetime|tobool|"
    r"toguid|todecimal)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*$"
)


class MappingEvidenceError(ValueError):
    """Supplied mapping metadata or evidence is malformed or stale."""


def _canonical(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"bytesSha256": hashlib.sha256(value).hexdigest()}
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise MappingEvidenceError(f"unsupported mapping metadata value: {type(value).__name__}")


def _digest(value: Any) -> str:
    encoded = json.dumps(
        _canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _evidence_payload(
    evidence: Mapping[str, Any],
    where: str,
    *,
    expected_table: str,
    expected_columns: Mapping[str, str],
) -> dict[str, Any]:
    kind = evidence.get("kind")
    path = evidence.get("path")
    content = evidence.get("content")
    if kind not in {"connector", "dcr", "schema", "table-schema", "catalog"}:
        raise MappingEvidenceError(f"{where}.kind must identify connector, DCR, or schema evidence")
    if not isinstance(path, str) or not path.strip():
        raise MappingEvidenceError(f"{where}.path is required")
    if not isinstance(content, (str, bytes)):
        raise MappingEvidenceError(f"{where}.content must contain the supplied evidence bytes or text")
    actual = hashlib.sha256(content.encode("utf-8") if isinstance(content, str) else content).hexdigest()
    expected = evidence.get("sha256")
    if expected is not None and expected != actual:
        raise MappingEvidenceError(f"{where}.sha256 is stale or does not match its evidence content")
    if kind in {"schema", "table-schema"}:
        try:
            document = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise MappingEvidenceError(f"{where} schema content must be a JSON table definition") from exc
        if not isinstance(document, Mapping) or str(document.get("table", "")).casefold() != expected_table.casefold():
            raise MappingEvidenceError(f"{where} does not describe table {expected_table!r}")
        declared_columns = document.get("columns")
        if not isinstance(declared_columns, Mapping):
            raise MappingEvidenceError(f"{where} schema content must include a columns object")
        normalized_declared = {
            str(name).casefold(): str(type_name).casefold()
            for name, type_name in declared_columns.items()
        }
        normalized_expected = {
            str(name).casefold(): str(type_name).casefold()
            for name, type_name in expected_columns.items()
        }
        if normalized_declared != normalized_expected:
            raise MappingEvidenceError(f"{where} schema content does not match the supplied columns")
    return {"path": path, "sha256": actual, "kind": kind}


def _schema_columns(value: Any, where: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise MappingEvidenceError(f"{where}.columns must be an object")
    result: dict[str, str] = {}
    for name, type_name in value.items():
        if not isinstance(name, str) or not name:
            raise MappingEvidenceError(f"{where}.columns contains an invalid column name")
        if not isinstance(type_name, str) or not type_name:
            raise MappingEvidenceError(f"{where}.columns[{name!r}] must be a type name")
        result[name] = type_name
    return result


def _field_references(query: str, aliases: set[str]) -> dict[str, set[str]]:
    """Collect alias-qualified fields and identifiers outside strings/comments."""
    lexical = re.compile(
        r"//[^\n]*|/\*[\s\S]*?\*/|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
        r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|[A-Za-z_][A-Za-z0-9_]*|[^\s]"
    )
    tokens = [
        match.group(0) for match in lexical.finditer(query)
        if not match.group(0).startswith(("//", "/*", "'", '"', "@'", '@"'))
    ]
    result: dict[str, set[str]] = {}
    for index in range(len(tokens) - 2):
        if (
            tokens[index].casefold() in aliases
            and tokens[index + 1] == "."
            and _IDENTIFIERS.fullmatch(tokens[index + 2])
        ):
            result.setdefault(tokens[index].casefold(), set()).add(tokens[index + 2])
    return result


def _query_words(query: str) -> set[str]:
    lexical = re.compile(
        r"//[^\n]*|/\*[\s\S]*?\*/|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
        r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|[A-Za-z_][A-Za-z0-9_]*"
    )
    return {
        match.group(0)
        for match in lexical.finditer(query)
        if not match.group(0).startswith(("//", "/*", "'", '"', "@'", '@"'))
    }


def _metadata_fingerprint(
    source_metadata: Mapping[str, Any],
    target_metadata: Mapping[str, Any],
    config: Mapping[str, Any],
) -> str:
    return _digest({
        "sourceMetadata": source_metadata,
        "targetMetadata": target_metadata,
        "config": config,
        "catalogSha256": hashlib.sha256(Path(__file__).with_name("catalog.py").read_bytes()).hexdigest(),
    })


def _runtime_references(
    runtime_evidence: Mapping[str, Any] | None,
    source_query_sha256: str,
    target_query_sha256: str,
) -> list[dict[str, Any]] | None:
    """Verify supplied Sentinel and Graph reports against the exact two query hashes."""
    if not runtime_evidence:
        return None

    def report_reference(
        key: str, expected_hash: str, providers: set[str], surfaces: set[str]
    ) -> dict[str, Any] | None:
        report = runtime_evidence.get(key)
        if not isinstance(report, Mapping):
            return None
        path, content = report.get("path"), report.get("content")
        if not isinstance(path, str) or not isinstance(content, (str, bytes)):
            return None
        raw = content.encode("utf-8") if isinstance(content, str) else content
        actual_hash = hashlib.sha256(raw).hexdigest()
        if report.get("sha256") not in (None, actual_hash):
            return None
        try:
            document = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        if (
            not isinstance(document, Mapping)
            or document.get("provider") not in providers
            or document.get("querySurface") not in surfaces
            or not isinstance(document.get("results"), list)
        ):
            return None
        matching = [
            result for result in document["results"]
            if isinstance(result, Mapping) and result.get("querySha256") == expected_hash
        ]
        if len(matching) != 1 or matching[0].get("status") != "passed":
            return None
        return {"path": path, "sha256": actual_hash, "kind": "runtimeVerification"}

    source_ref = report_reference(
        "sourceReport",
        source_query_sha256,
        {"triage-mcp", "log-analytics-cli", "azure-monitor-sdk"},
        {"microsoft-sentinel-triage", "log-analytics-workspace"},
    )
    target_ref = report_reference(
        "targetReport",
        target_query_sha256,
        {"graph"},
        {"defender-advanced-hunting"},
    )
    return [source_ref, target_ref] if source_ref and target_ref else None


def _status(references: list[dict[str, Any]]) -> str:
    if len([ref for ref in references if ref.get("kind") == "runtimeVerification"]) >= 2:
        return "runtime-validated"
    if any(ref.get("kind") == "catalog" for ref in references):
        return "schema-verified"
    if len([
        ref for ref in references if ref.get("kind") in {"schema", "table-schema"}
    ]) >= 2:
        return "schema-verified"
    return "inferred"


def _mapping_kind(source: str, target: str | None, transform: str | None) -> str:
    if target is None:
        return "dropped"
    if transform:
        cast = _CAST.fullmatch(transform)
        if cast:
            return "cast"
        if transform.strip() != source:
            return "derived"
    return "direct" if source == target else "rename"


def _where_predicates(query: str) -> list[dict[str, str]]:
    """Capture simple pipeline filters verbatim; never reconstruct their logic."""
    lexical = re.compile(
        r"//[^\n]*|/\*[\s\S]*?\*/|@'(?:''|[^'])*'|@\"(?:\"\"|[^\"])*\""
        r"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|[^\s]"
    )
    masked = list(query)
    for match in lexical.finditer(query):
        token = match.group(0)
        if token.startswith(("//", "/*", "'", '"', "@'", '@"')):
            for position in range(match.start(), match.end()):
                if masked[position] != "\n":
                    masked[position] = " "
    clean = "".join(masked)
    result: list[dict[str, str]] = []
    for match in re.finditer(r"(?is)\|\s*where\b(.*?)(?=\|\s*[A-Za-z_][A-Za-z0-9_-]*\b|$)", clean):
        predicate = query[match.start(1):match.end(1)].strip()
        if predicate:
            result.append({"predicate": predicate})
    return result


def build_mapping_evidence(
    source_query: str,
    target_query: str | None = None,
    *,
    source_metadata: Mapping[str, Any] | None = None,
    target_metadata: Mapping[str, Any] | None = None,
    config: Mapping[str, Any] | None = None,
    runtime_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build directional, query-scoped field evidence from supplied metadata.

    Metadata is keyed by table name. Each table descriptor may include
    ``columns``, ``targetTable``, ``columnMappings``, ``droppedColumns``,
    ``transformKql``, and an ``evidence`` object containing kind/path/content.
    Explicit mapping expressions are recorded, not executed or inverted.
    """
    if not isinstance(source_query, str) or not source_query.strip():
        raise MappingEvidenceError("source_query must be non-empty text")
    target_query = source_query if target_query is None else target_query
    if not isinstance(target_query, str):
        raise MappingEvidenceError("target_query must be text")
    source_metadata = source_metadata or {}
    target_metadata = target_metadata or {}
    config = config or {}
    for name, value in (
        ("source_metadata", source_metadata), ("target_metadata", target_metadata), ("config", config)
    ):
        if not isinstance(value, Mapping):
            raise MappingEvidenceError(f"{name} must be an object keyed by table or option")

    source_hash = hashlib.sha256(source_query.encode("utf-8")).hexdigest()
    target_hash = hashlib.sha256(target_query.encode("utf-8")).hexdigest()
    runtime_references = _runtime_references(runtime_evidence, source_hash, target_hash)
    target_words = _query_words(target_query)
    table_references = query_table_references(source_query)
    issues: list[dict[str, str]] = []
    if not table_references:
        issues.append({"code": "table-binding-unresolved", "message": "No supported table binding was found."})
    has_ambiguous_scope = query_has_ambiguous_table_scope(source_query)
    if has_ambiguous_scope:
        issues.append({
            "code": "table-scope-ambiguous",
            "message": "Join/union or multiple table inputs prevent unqualified field attribution.",
        })

    mapping_records: list[dict[str, Any]] = []
    catalog_ref = {
        "path": "sentinel_xdr_migration/catalog.py",
        "sha256": hashlib.sha256(Path(__file__).with_name("catalog.py").read_bytes()).hexdigest(),
        "kind": "catalog",
    }
    known_column_renames = query_column_renames(source_query)
    configured, config_ambiguous = configured_column_renames(source_query, dict(config))
    if config_ambiguous:
        issues.append({
            "code": "configured-column-map-not-applied",
            "message": "Configured column mappings were not attributed because the query has multiple table scopes.",
        })

    aliases = {
        str(ref["alias"]).casefold()
        for ref in table_references if ref.get("alias")
    }
    qualified_fields = _field_references(source_query, aliases)
    query_words = {word.casefold() for word in _query_words(source_query)}
    global_mapping_count = 0
    for reference in table_references:
        table = str(reference["table"])
        alias = reference.get("alias")
        descriptor = next(
            (value for key, value in source_metadata.items() if str(key).casefold() == table.casefold()),
            {},
        )
        if not isinstance(descriptor, Mapping):
            raise MappingEvidenceError(f"source_metadata[{table!r}] must be an object")
        target_table = descriptor.get("targetTable")
        configured_table = next(
            (value for key, value in (config.get("tableMappings") or {}).items()
             if str(key).casefold() == table.casefold()),
            None,
        )
        if configured_table:
            target_table = configured_table
        if target_table is not None and not isinstance(target_table, str):
            raise MappingEvidenceError(f"target table for {table!r} must be text")
        if not target_table and (
            table in NATIVE_XDR_TABLES or table in PASSTHROUGH_TABLES
        ):
            target_table = table
        target_descriptor = next(
            (value for key, value in target_metadata.items()
             if target_table and str(key).casefold() == str(target_table).casefold()),
            {},
        )
        if not isinstance(target_descriptor, Mapping):
            raise MappingEvidenceError(f"target_metadata[{target_table!r}] must be an object")
        source_columns = _schema_columns(descriptor.get("columns"), f"source_metadata[{table!r}]")
        target_columns = _schema_columns(target_descriptor.get("columns"), f"target_metadata[{target_table!r}]")
        evidence_references: list[dict[str, Any]] = []
        source_evidence = descriptor.get("evidence")
        target_evidence = target_descriptor.get("evidence")
        if source_evidence is not None:
            if not isinstance(source_evidence, Mapping):
                raise MappingEvidenceError(f"source_metadata[{table!r}].evidence must be an object")
            evidence_references.append(_evidence_payload(
                source_evidence,
                f"source_metadata[{table!r}].evidence",
                expected_table=table,
                expected_columns=source_columns,
            ))
        if target_evidence is not None:
            if not isinstance(target_evidence, Mapping):
                raise MappingEvidenceError(f"target_metadata[{target_table!r}].evidence must be an object")
            evidence_references.append(_evidence_payload(
                target_evidence,
                f"target_metadata[{target_table!r}].evidence",
                expected_table=str(target_table),
                expected_columns=target_columns,
            ))

        explicit_mappings = descriptor.get("columnMappings") or {}
        if not isinstance(explicit_mappings, Mapping):
            raise MappingEvidenceError(f"source_metadata[{table!r}].columnMappings must be an object")
        column_candidates: dict[str, Any] = dict(explicit_mappings)
        if not has_ambiguous_scope:
            column_candidates.update({
                source: target for source, target in configured.items()
                if source.casefold() not in {key.casefold() for key in column_candidates}
            })
            if table in NATIVE_XDR_TABLES or table in PASSTHROUGH_TABLES:
                for source, target in known_column_renames.items():
                    if source.casefold() not in {key.casefold() for key in column_candidates}:
                        column_candidates[source] = target

        aliases_for_scope = [str(ref["alias"]).casefold() for ref in table_references if ref.get("alias")]
        alias_ambiguous = bool(alias and aliases_for_scope.count(str(alias).casefold()) > 1)
        if alias_ambiguous:
            issues.append({
                "code": "alias-binding-ambiguous",
                "message": f"Alias {alias!r} is bound to more than one input; no columns were attributed.",
            })
            continue
        field_scope = (
            qualified_fields.get(str(alias).casefold(), set())
            if has_ambiguous_scope and alias
            else set()
        )
        if not has_ambiguous_scope and len(table_references) == 1:
            field_scope = {
                name for name in set(source_columns) | set(column_candidates) | set(descriptor.get("droppedColumns") or [])
                if name.casefold() in query_words
            }
        if has_ambiguous_scope and not alias:
            if column_candidates or source_columns:
                issues.append({
                    "code": "unqualified-field-unresolved",
                    "message": f"Fields for {table} have no unique query alias; no per-column binding was asserted.",
                })
            continue

        dropped = descriptor.get("droppedColumns") or []
        if not isinstance(dropped, (list, tuple)) or any(not isinstance(name, str) for name in dropped):
            raise MappingEvidenceError(f"source_metadata[{table!r}].droppedColumns must be a list of names")
        for source_column in sorted(field_scope, key=str.casefold):
            explicit = next(
                (value for key, value in column_candidates.items() if str(key).casefold() == source_column.casefold()),
                None,
            )
            transform: str | None = None
            target_column: str | None = None
            target_type: str | None = None
            if source_column.casefold() in {name.casefold() for name in dropped}:
                target_column = None
            elif isinstance(explicit, str):
                target_column = explicit
            elif isinstance(explicit, Mapping):
                target_column = explicit.get("target")
                transform_value = explicit.get("transform") or explicit.get("expression")
                transform = transform_value if isinstance(transform_value, str) else None
                explicit_type = explicit.get("targetType")
                target_type = explicit_type if isinstance(explicit_type, str) else None
            elif explicit is not None:
                raise MappingEvidenceError(f"mapping for {source_column!r} must be text or an object")
            elif source_column in target_columns:
                target_column = source_column
            elif source_column in source_columns and target_table and target_columns:
                target_column = None
            else:
                continue
            if target_column is not None and not isinstance(target_column, str):
                raise MappingEvidenceError(f"target column for {source_column!r} must be text or null")
            if target_column is not None and target_column in target_columns:
                target_type = target_type or target_columns[target_column]
            elif target_column is not None and source_column in source_columns:
                issues.append({
                    "code": "target-column-schema-missing",
                    "message": f"Target column {target_table}.{target_column} is absent from supplied target schema.",
                })
            source_type = source_columns.get(source_column)
            kind = _mapping_kind(source_column, target_column, transform)
            is_catalog = source_column in known_column_renames and (
                table in NATIVE_XDR_TABLES or table in PASSTHROUGH_TABLES
            )
            references_for_mapping = list(evidence_references)
            if is_catalog:
                references_for_mapping.append(catalog_ref)
            if runtime_references:
                references_for_mapping.extend(runtime_references)
            status = _status(references_for_mapping)
            if not is_catalog and not (
                source_evidence and source_evidence.get("kind") in {"schema", "table-schema"}
                and target_evidence and target_evidence.get("kind") in {"schema", "table-schema"}
            ):
                status = "inferred"
            notes: list[str] = []
            if transform:
                notes.append("Supplied forward expression is recorded verbatim and was not executed.")
            mapping_records.append({
                "sourceTable": table,
                "sourceAlias": alias,
                "targetTable": target_table,
                "sourceColumn": source_column,
                "targetColumn": target_column,
                "sourceType": source_type,
                "targetType": target_type,
                "transform": transform,
                "kind": kind,
                "status": status,
                "appliedToTargetQuery": bool(
                    target_column
                    and target_column in target_words
                    and (
                        source_column == target_column
                        or source_column not in target_words
                    )
                    and (not transform or transform in target_query)
                ),
                "evidenceReferences": references_for_mapping,
                "notes": notes,
            })
            global_mapping_count += 1

        transform_kql = descriptor.get("transformKql")
        if transform_kql is not None:
            if not isinstance(transform_kql, str):
                raise MappingEvidenceError(f"source_metadata[{table!r}].transformKql must be text")
            issues.append({
                "code": "forward-dcr-transform-not-inverted",
                "message": (
                    f"DCR transform for {table} is forward-only evidence; its inverse was not inferred."
                ),
            })

    if runtime_evidence and not runtime_references:
        issues.append({
            "code": "runtime-evidence-not-current",
            "message": "Runtime evidence was not applied because it was absent, failed, or bound to different query hashes.",
        })
    filters = _where_predicates(source_query)
    target_filters = _where_predicates(target_query)
    for index, item in enumerate(filters):
        item["sha256"] = hashlib.sha256(item["predicate"].encode("utf-8")).hexdigest()
        target_predicate = target_filters[index]["predicate"] if index < len(target_filters) else None
        item["targetPredicate"] = target_predicate
        item["targetPredicateSha256"] = (
            hashlib.sha256(target_predicate.encode("utf-8")).hexdigest()
            if target_predicate is not None else None
        )
        item["rewriteStatus"] = (
            "unchanged" if target_predicate == item["predicate"]
            else "rewritten-by-converter" if target_predicate is not None
            else "not-found-in-target"
        )

    return {
        "schemaVersion": SCHEMA_VERSION,
        "direction": "sentinel-to-xdr",
        "sourceSurface": "sentinel-log-analytics",
        "targetSurface": "graph-advanced-hunting",
        "sourceQuery": source_query,
        "targetQuery": target_query,
        "sourceQuerySha256": source_hash,
        "targetQuerySha256": target_hash,
        "metadataSha256": _metadata_fingerprint(source_metadata, target_metadata, config),
        "mappings": mapping_records,
        "filters": filters,
        "issues": issues,
        "queryRewritePerformed": target_query != source_query,
        "queryRewriteNotes": (
            ["Target query is supplied by the existing converter; this module did not rewrite KQL."]
            if target_query != source_query else []
        ),
        "overallStatus": (
            min(
                (item["status"] for item in mapping_records),
                key={"inferred": 0, "schema-verified": 1, "runtime-validated": 2}.get,
            )
            if mapping_records else "inferred"
        ),
        "mappingCount": global_mapping_count,
    }


def validate_mapping_evidence_freshness(
    record: Mapping[str, Any],
    source_query: str,
    target_query: str,
    *,
    source_metadata: Mapping[str, Any] | None = None,
    target_metadata: Mapping[str, Any] | None = None,
    config: Mapping[str, Any] | None = None,
    runtime_evidence: Mapping[str, Any] | None = None,
) -> list[str]:
    """Return exact stale-input errors; no hash is trusted without recomputation."""
    errors: list[str] = []
    checks = (
        ("sourceQuerySha256", hashlib.sha256(source_query.encode("utf-8")).hexdigest()),
        ("targetQuerySha256", hashlib.sha256(target_query.encode("utf-8")).hexdigest()),
        (
            "metadataSha256",
            _metadata_fingerprint(source_metadata or {}, target_metadata or {}, config or {}),
        ),
    )
    for field, actual in checks:
        if record.get(field) != actual:
            errors.append(f"{field} is stale")
        elif not isinstance(record.get(field), str) or not _SHA256.fullmatch(str(record[field])):
            errors.append(f"{field} is not lowercase SHA-256")
    if record.get("sourceQuery") != source_query:
        errors.append("sourceQuery is stale")
    if record.get("targetQuery") != target_query:
        errors.append("targetQuery is stale")
    try:
        current = build_mapping_evidence(
            source_query,
            target_query,
            source_metadata=source_metadata,
            target_metadata=target_metadata,
            config=config,
            runtime_evidence=runtime_evidence,
        )
    except MappingEvidenceError as exc:
        errors.append(f"mapping evidence inputs are invalid: {exc}")
    else:
        actual_mappings = record.get("mappings")
        if not isinstance(actual_mappings, list):
            errors.append("mappings are malformed")
        else:
            expected_by_key = {
                (item["sourceTable"], item["sourceAlias"], item["sourceColumn"]): item
                for item in current["mappings"]
            }
            actual_by_key = {
                (item.get("sourceTable"), item.get("sourceAlias"), item.get("sourceColumn")): item
                for item in actual_mappings if isinstance(item, Mapping)
            }
            if actual_by_key.keys() != expected_by_key.keys():
                errors.append("mapping scopes are stale")
            for key in actual_by_key.keys() & expected_by_key.keys():
                actual_item, expected_item = actual_by_key[key], expected_by_key[key]
                if (
                    actual_item.get("evidenceReferences") != expected_item.get("evidenceReferences")
                    or actual_item.get("status") != expected_item.get("status")
                ):
                    errors.append(f"mapping evidence is stale for {key[0]}.{key[2]}")
    for index, mapping in enumerate(record.get("mappings", [])):
        if not isinstance(mapping, Mapping):
            errors.append(f"mappings[{index}] is malformed")
            continue
        for reference in mapping.get("evidenceReferences", []):
            if not isinstance(reference, Mapping) or not _SHA256.fullmatch(str(reference.get("sha256", ""))):
                errors.append(f"mappings[{index}] has an invalid evidence hash")
    return errors
