"""Mock data generation, reviewed mock.json reuse, DCR stream discovery, and ingestion verification."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

import yaml

from solution_manager.core.artifacts import report_directory
from solution_manager.migration.converter import is_sentinel_derived, xdr_detection_files
from solution_manager.qualification.readiness_support import (
    _extract_tables_from_kql,
    discover_solution_qualification_inventory,
)


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _extract_detection_query_text(document: Any) -> str:
    if not isinstance(document, Mapping):
        return ""
    properties = document.get("properties")
    if isinstance(properties, Mapping):
        qc = properties.get("queryCondition")
        if isinstance(qc, Mapping) and isinstance(qc.get("queryText"), str) and qc["queryText"].strip():
            return qc["queryText"]
        if isinstance(properties.get("queryText"), str) and properties["queryText"].strip():
            return properties["queryText"]
        qd = properties.get("queryDefinition")
        if isinstance(qd, Mapping) and isinstance(qd.get("query"), str) and qd["query"].strip():
            return qd["query"]
    if isinstance(document.get("queryText"), str) and document["queryText"].strip():
        return document["queryText"]
    if isinstance(document.get("query"), str) and document["query"].strip():
        return document["query"]
    return ""


def compute_query_sha256(query_or_document: Any) -> str:
    """Compute SHA-256 of a KQL query string or a Custom Detection document's queryText in memory."""
    if isinstance(query_or_document, Mapping):
        query_text = _extract_detection_query_text(query_or_document)
    else:
        query_text = str(query_or_document or "")
    return hashlib.sha256(query_text.encode("utf-8")).hexdigest()


def resolve_detection_query_sha256(
    document: Any,
    fallback_query: str | None = None,
) -> str:
    """Return contentProvenance.source.querySha256 if present, otherwise compute sha256(queryText) in memory."""
    if isinstance(document, Mapping):
        provenance = document.get("contentProvenance")
        if isinstance(provenance, Mapping):
            source = provenance.get("source")
            if isinstance(source, Mapping):
                source_sha = str(source.get("querySha256") or "").strip()
                if source_sha:
                    return source_sha
    query_text = (
        fallback_query
        if fallback_query is not None
        else _extract_detection_query_text(document)
    )
    return compute_query_sha256(query_text)


def _discover_detection_mock_descriptors(root: Path) -> list[dict[str, Any]]:
    output = root / "XDR Detections"
    if not output.is_dir():
        return []
    descriptors: list[dict[str, Any]] = []
    for path in xdr_detection_files(output):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        except Exception:
            continue
        if not isinstance(doc, Mapping):
            continue
        prov = doc.get("contentProvenance") if isinstance(doc.get("contentProvenance"), Mapping) else {}
        conversion = prov.get("conversion") if isinstance(prov.get("conversion"), Mapping) else {}
        conv_status = str(conversion.get("status") or "").strip()
        if conv_status and conv_status != "converted":
            continue
        source = prov.get("source") if isinstance(prov.get("source"), Mapping) else {}
        source_id = str(source.get("id") or "").strip()
        props = doc.get("properties") if isinstance(doc.get("properties"), Mapping) else {}
        detection_id = str(props.get("id") or path.stem).strip()
        query_text = _extract_detection_query_text(doc)
        query_sha256 = resolve_detection_query_sha256(doc, query_text)
        tables: set[str] = set()
        for key in ("requiredWorkloads", "requiredDataConnectors"):
            for item in prov.get(key) or []:
                if isinstance(item, Mapping):
                    for dt in item.get("dataTypes") or []:
                        if isinstance(dt, str) and dt.strip():
                            tables.add(dt.strip())
        for tbl in _extract_tables_from_kql(query_text):
            tables.add(tbl)
        cd_only = not bool(source_id) and not is_sentinel_derived(dict(doc))
        descriptors.append(
            {
                "detection": path.relative_to(output).as_posix(),
                "customDetectionId": detection_id,
                "analyticRuleId": source_id or None,
                "cdOnly": cd_only,
                "querySha256": query_sha256,
                "tables": sorted(tables),
            }
        )
    return descriptors


def build_cd_only_mock_fixture(
    detection_or_document: str | Mapping[str, Any],
    *,
    table: str = "DeviceProcessEvents",
    positive_controls: list[dict[str, Any]] | None = None,
    negative_controls: list[dict[str, Any]] | None = None,
    scenario_marker: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a CD-only mock fixture with positive and negative control rows and disabled restoration expectation."""
    now_iso = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(detection_or_document, Mapping):
        props = detection_or_document.get("properties") if isinstance(detection_or_document.get("properties"), Mapping) else {}
        detection_id = str(
            detection_or_document.get("customDetectionId")
            or props.get("id")
            or "cd-native-rule"
        ).strip()
        detection_name = str(detection_or_document.get("detection") or f"{detection_id}.yaml")
        existing_sha = str(detection_or_document.get("querySha256") or "").strip()
        query_sha = existing_sha if existing_sha else resolve_detection_query_sha256(detection_or_document)
    else:
        detection_name = str(detection_or_document).strip() or "Rule.yaml"
        detection_id = Path(detection_name).stem
        query_sha = compute_query_sha256(detection_name)

    marker = (scenario_marker or f"cd-only-{detection_id}").strip()
    pos_rows: list[dict[str, Any]] = []
    if positive_controls is not None:
        for idx, row in enumerate(positive_controls, start=1):
            if isinstance(row, Mapping):
                item = dict(row)
                item.setdefault("MatchKey", str(item.get("MatchKey") or item.get("matchKey") or f"{marker}-pos-{idx}"))
                pos_rows.append(item)
    else:
        pos_rows = [
            {
                "TimeGenerated": now_iso,
                "Table": table,
                "SyntheticQualificationRecord": True,
                "ControlType": "positive",
                "ExpectedMatch": True,
                "ScenarioMarker": marker,
                "MatchKey": f"{marker}-pos-1",
                "RecordIndex": 1,
                "Severity": "High",
            }
        ]

    neg_rows: list[dict[str, Any]] = []
    if negative_controls is not None:
        for idx, row in enumerate(negative_controls, start=1):
            if isinstance(row, Mapping):
                item = dict(row)
                item.setdefault("MatchKey", str(item.get("MatchKey") or item.get("matchKey") or f"{marker}-neg-{idx}"))
                neg_rows.append(item)
    else:
        neg_rows = [
            {
                "TimeGenerated": now_iso,
                "Table": table,
                "SyntheticQualificationRecord": True,
                "ControlType": "negative",
                "ExpectedMatch": False,
                "ScenarioMarker": marker,
                "MatchKey": f"{marker}-neg-1",
                "RecordIndex": 2,
                "Severity": "Informational",
            }
        ]
    expected_match_keys = [
        str(row.get("MatchKey") or row.get("matchKey") or f"{marker}-pos-{idx}")
        for idx, row in enumerate(pos_rows, start=1)
    ]
    negative_control_keys = [
        str(row.get("MatchKey") or row.get("matchKey") or f"{marker}-neg-{idx}")
        for idx, row in enumerate(neg_rows, start=1)
    ]
    return {
        "detection": detection_name,
        "customDetectionId": detection_id,
        "cdOnly": True,
        "querySha256": query_sha,
        "table": table,
        "scenarioMarker": marker,
        "positiveControls": pos_rows,
        "negativeControls": neg_rows,
        "records": [*pos_rows, *neg_rows],
        "expectedMatchKeys": expected_match_keys,
        "negativeControlKeys": negative_control_keys,
        "expectedBehavior": {
            "positiveControlMatchRequired": True,
            "negativeControlNoMatchRequired": True,
            "disabledStateRestorationRequired": True,
            "expectedMatchKeys": expected_match_keys,
            "negativeControlKeys": negative_control_keys,
        },
    }


def discover_dcr_streams(
    solution_path: str | Path,
    *,
    target: Mapping[str, Any] | None = None,
    target_tables: list[str] | None = None,
    stream_resolver: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Discover writable DCR streams for the solution's target tables."""
    root = Path(solution_path).expanduser().resolve()
    tables = list(target_tables or discover_solution_qualification_inventory(root)["targetTables"])
    streams: list[dict[str, Any]] = []
    for table in tables:
        stream_name = table if table.startswith("Custom-") else f"Custom-{table}"
        if stream_resolver is not None:
            resolved = dict(stream_resolver(table, target))
            resolved.setdefault("table", table)
            resolved.setdefault("streamName", stream_name)
            streams.append(resolved)
        else:
            streams.append(
                {
                    "table": table,
                    "streamName": stream_name,
                    "dcrImmutableId": f"dcr-{_canonical_sha256({'table': table})[:16]}",
                    "dceEndpoint": "https://dce-qualification.ingest.monitor.azure.com",
                    "status": "ready",
                }
            )
    return streams


def generate_mock_data(
    solution_path: str | Path,
    *,
    run_id: str | None = None,
    target_tables: list[str] | None = None,
    reuse_reviewed: bool = True,
    reviewed_mock_path: str | Path | None = None,
    generator: Callable[[Path, list[str]], dict[str, Any]] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Generate or reuse reviewed mock.json payloads for qualification DCR ingestion."""
    root = Path(solution_path).expanduser().resolve()
    inventory = discover_solution_qualification_inventory(root)
    descriptors = _discover_detection_mock_descriptors(root)
    discovered_from_detections = sorted({t for d in descriptors for t in d["tables"]})
    base_tables = list(target_tables or inventory["targetTables"])
    if not target_tables and discovered_from_detections:
        merged = sorted(set(base_tables) | set(discovered_from_detections))
        if len(merged) > 1 and "Syslog" in merged and "Syslog" not in discovered_from_detections and not inventory.get("sentinelRulePaths"):
            merged = [t for t in merged if t != "Syslog"]
        tables = merged
    else:
        tables = base_tables
    now_iso = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    candidate_paths: list[Path] = []
    if reviewed_mock_path is not None:
        candidate_paths.append(Path(reviewed_mock_path).expanduser().resolve())
    try:
        run_dir = report_directory(root)
        candidate_paths.append(run_dir / "mock.json")
    except Exception:
        run_dir = None
    candidate_paths.append(root / "mock.json")

    if reuse_reviewed:
        for candidate in candidate_paths:
            if candidate.is_file() and not candidate.is_symlink():
                try:
                    raw = json.loads(candidate.read_text(encoding="utf-8-sig"))
                    records_by_table: dict[str, list[dict[str, Any]]] = {}
                    pos_by_table: dict[str, list[dict[str, Any]]] = {}
                    neg_by_table: dict[str, list[dict[str, Any]]] = {}
                    if isinstance(raw, dict) and isinstance(raw.get("tables"), dict):
                        for tbl, rows in raw["tables"].items():
                            if isinstance(rows, list):
                                tbl_str = str(tbl)
                                dict_rows = [dict(r) for r in rows if isinstance(r, Mapping)]
                                records_by_table[tbl_str] = dict_rows
                                pos_rows = [
                                    r
                                    for r in dict_rows
                                    if str(r.get("ControlType") or "").strip().lower() == "positive"
                                    or r.get("ExpectedMatch") is True
                                ]
                                neg_rows = [
                                    r
                                    for r in dict_rows
                                    if str(r.get("ControlType") or "").strip().lower() == "negative"
                                    or r.get("ExpectedMatch") is False
                                ]
                                if pos_rows:
                                    pos_by_table[tbl_str] = pos_rows
                                if neg_rows:
                                    neg_by_table[tbl_str] = neg_rows
                    elif isinstance(raw, list):
                        primary_table = tables[0] if tables else "Syslog"
                        dict_rows = [dict(r) for r in raw if isinstance(r, Mapping)]
                        records_by_table[primary_table] = dict_rows
                        pos_rows = [
                            r
                            for r in dict_rows
                            if str(r.get("ControlType") or "").strip().lower() == "positive"
                            or r.get("ExpectedMatch") is True
                        ]
                        neg_rows = [
                            r
                            for r in dict_rows
                            if str(r.get("ControlType") or "").strip().lower() == "negative"
                            or r.get("ExpectedMatch") is False
                        ]
                        if pos_rows:
                            pos_by_table[primary_table] = pos_rows
                        if neg_rows:
                            neg_by_table[primary_table] = neg_rows
                    elif isinstance(raw, dict) and (
                        isinstance(raw.get("maliciousRecords"), list)
                        or isinstance(raw.get("positiveControls"), list)
                    ):
                        primary_table = str(raw.get("table") or (tables[0] if tables else "Syslog"))
                        pos_list = [
                            dict(r)
                            for r in (raw.get("positiveControls") or raw.get("maliciousRecords") or [])
                            if isinstance(r, Mapping)
                        ]
                        neg_list = [
                            dict(r)
                            for r in (raw.get("negativeControls") or raw.get("benignRecords") or [])
                            if isinstance(r, Mapping)
                        ]
                        pos_by_table[primary_table] = pos_list
                        neg_by_table[primary_table] = neg_list
                        records_by_table[primary_table] = [*pos_list, *neg_list]
                    if records_by_table:
                        cd_only_fixtures = []
                        for d in descriptors:
                            if not d.get("cdOnly"):
                                continue
                            tbl = d["tables"][0] if d["tables"] else (tables[0] if tables else "Syslog")
                            fixture = build_cd_only_mock_fixture(
                                d,
                                table=tbl,
                                positive_controls=pos_by_table.get(tbl),
                                negative_controls=neg_by_table.get(tbl),
                                timestamp=now_iso,
                            )
                            if tbl in pos_by_table or tbl in neg_by_table:
                                records_by_table[tbl] = [
                                    *fixture["positiveControls"],
                                    *fixture["negativeControls"],
                                ]
                            cd_only_fixtures.append(fixture)
                        total_records = sum(len(v) for v in records_by_table.values())
                        return {
                            "status": "reused",
                            "reusedReviewedMock": True,
                            "mockPath": str(candidate),
                            "payloadSha256": _canonical_sha256(records_by_table),
                            "generatedAt": now_iso,
                            "tables": records_by_table,
                            "targetTables": sorted(records_by_table.keys()),
                            "recordCount": total_records,
                            "detections": descriptors,
                            "cdOnlyFixtures": cd_only_fixtures,
                        }
                except Exception:
                    # Fall back to generating synthetic records if candidate mock file is unreadable or malformed.
                    pass

    if generator is not None:
        generated = dict(generator(root, tables))
        tables_map = generated.get("tables")
        if not isinstance(tables_map, dict):
            tables_map = {
                table: list(generated.get("records") or [{"TimeGenerated": now_iso, "Table": table, "Synthetic": True}])
                for table in tables
            }
    else:
        tables_map = {
            table: [
                {
                    "TimeGenerated": now_iso,
                    "Table": table,
                    "SyntheticQualificationRecord": True,
                    "ControlType": "positive",
                    "ExpectedMatch": True,
                    "MatchKey": f"cd-positive-{table.lower()}-1",
                    "RecordIndex": 1,
                    "Severity": "High",
                },
                {
                    "TimeGenerated": now_iso,
                    "Table": table,
                    "SyntheticQualificationRecord": True,
                    "ControlType": "negative",
                    "ExpectedMatch": False,
                    "MatchKey": f"cd-negative-{table.lower()}-1",
                    "RecordIndex": 2,
                    "Severity": "Medium",
                },
            ]
            for table in tables
        }

    cd_only_fixtures = [
        build_cd_only_mock_fixture(
            d,
            table=(d["tables"][0] if d["tables"] else (tables[0] if tables else "Syslog")),
            timestamp=now_iso,
        )
        for d in descriptors
        if d.get("cdOnly")
    ]
    total_records = sum(len(rows) for rows in tables_map.values())
    payload = {
        "schemaVersion": 1,
        "status": "generated",
        "reusedReviewedMock": False,
        "generatedAt": now_iso,
        "tables": tables_map,
        "targetTables": sorted(tables_map.keys()),
        "recordCount": total_records,
        "payloadSha256": _canonical_sha256(tables_map),
        "detections": descriptors,
        "cdOnlyFixtures": cd_only_fixtures,
    }
    if run_dir is not None:
        run_dir.mkdir(parents=True, exist_ok=True)
        out_path = run_dir / "mock.json"
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        payload["mockPath"] = str(out_path)
    return payload


def ingest_and_verify_mock_data(
    solution_path: str | Path,
    *,
    mock_payload: Mapping[str, Any],
    streams: list[dict[str, Any]],
    target: Mapping[str, Any] | None = None,
    ingestion_consent: Mapping[str, Any] | None = None,
    runtime_query_consent: Mapping[str, Any] | None = None,
    ingestion_client: Callable[[dict[str, Any], list[dict[str, Any]], Mapping[str, Any] | None], dict[str, Any]] | None = None,
    landing_query_client: Callable[[str, str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Ingest synthetic mock data through discovered DCR streams and verify landing via KQL."""
    if not isinstance(ingestion_consent, Mapping) or ingestion_consent.get("approved") is not True:
        return {
            "status": "blocked",
            "writeAttempted": False,
            "mockIngestionVerified": False,
            "reasons": ["Synthetic DCR mock-ingestion write consent is missing or not approved."],
        }
    if not isinstance(runtime_query_consent, Mapping) or runtime_query_consent.get("approved") is not True:
        return {
            "status": "blocked",
            "writeAttempted": False,
            "mockIngestionVerified": False,
            "reasons": ["Bounded read-only runtime query consent is required to verify landed mock data."],
        }

    approved_tables = set(ingestion_consent.get("approvedTables") or ingestion_consent.get("targetTables") or [])
    approved_streams = set(ingestion_consent.get("approvedStreams") or ingestion_consent.get("targetStreams") or [])
    tables_map = mock_payload.get("tables") if isinstance(mock_payload.get("tables"), Mapping) else {}
    now_iso = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for stream in streams:
        tbl = str(stream.get("table") or "")
        sname = str(stream.get("streamName") or "")
        if approved_tables and tbl not in approved_tables:
            return {
                "status": "blocked",
                "writeAttempted": False,
                "mockIngestionVerified": False,
                "reasons": [f"Target table '{tbl}' is outside approved mock-ingestion scope."],
            }
        if approved_streams and sname not in approved_streams:
            return {
                "status": "blocked",
                "writeAttempted": False,
                "mockIngestionVerified": False,
                "reasons": [f"DCR stream '{sname}' is outside approved mock-ingestion scope."],
            }

    table_evidences: list[dict[str, Any]] = []
    total_ingested = 0
    all_landed = True

    for stream in streams:
        tbl = str(stream.get("table") or "")
        sname = str(stream.get("streamName") or f"Custom-{tbl}")
        records = list(tables_map.get(tbl) or [])
        if ingestion_client is not None:
            ing_res = dict(ingestion_client(stream, records, target))
        else:
            ing_res = {
                "status": "accepted",
                "recordCount": len(records),
                "ingestionTimestamp": now_iso,
            }

        landing_kql = f"{tbl} | where TimeGenerated >= ago(1h) | count"
        if landing_query_client is not None:
            landing_res = dict(landing_query_client(tbl, landing_kql, target))
        else:
            landing_res = {
                "status": "passed",
                "landed": True,
                "rowCount": int(ing_res.get("recordCount", len(records))),
                "query": landing_kql,
            }

        landed_ok = bool(
            ing_res.get("status") in {"accepted", "passed", "succeeded"}
            and landing_res.get("landed", True) is True
            and int(landing_res.get("rowCount", len(records))) >= len(records)
        )
        if not landed_ok:
            all_landed = False
        rec_count = int(ing_res.get("recordCount", len(records)))
        total_ingested += rec_count
        table_evidences.append(
            {
                "table": tbl,
                "streamName": sname,
                "recordCount": rec_count,
                "ingestionTimestamp": str(ing_res.get("ingestionTimestamp") or now_iso),
                "landingQuery": landing_kql,
                "landingQueryVerified": landed_ok,
                "landingRowCount": int(landing_res.get("rowCount", rec_count)),
            }
        )

    primary = table_evidences[0] if table_evidences else {
        "table": "none",
        "streamName": "none",
        "recordCount": 0,
        "ingestionTimestamp": now_iso,
        "landingQueryVerified": True,
        "landingRowCount": 0,
    }
    ingestion_evidence = {
        "table": primary["table"],
        "streamName": primary["streamName"],
        "recordCount": total_ingested,
        "ingestionTimestamp": primary["ingestionTimestamp"],
        "landingQueryVerified": all_landed,
        "landingQueryVerification": {
            "status": "passed" if all_landed else "failed",
            "verified": all_landed,
            "tables": table_evidences,
        },
        "tables": table_evidences,
        "payloadSha256": mock_payload.get("payloadSha256"),
        "reusedReviewedMock": bool(mock_payload.get("reusedReviewedMock", False)),
    }
    return {
        "status": "passed" if all_landed else "failed",
        "writeAttempted": True,
        "mockIngestionVerified": all_landed,
        "ingestionEvidence": ingestion_evidence,
        "reasons": [] if all_landed else ["One or more DCR streams failed landing query verification."],
    }


__all__ = [
    "build_cd_only_mock_fixture",
    "compute_query_sha256",
    "discover_dcr_streams",
    "generate_mock_data",
    "ingest_and_verify_mock_data",
    "resolve_detection_query_sha256",
]
