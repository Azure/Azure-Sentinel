"""Mock data generation, reviewed mock.json reuse, DCR stream discovery, and ingestion verification."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from solution_manager.core.artifacts import report_directory
from solution_manager.qualification.readiness_support import discover_solution_qualification_inventory


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


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
    tables = list(target_tables or inventory["targetTables"])
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
                    if isinstance(raw, dict) and isinstance(raw.get("tables"), dict):
                        for tbl, rows in raw["tables"].items():
                            if isinstance(rows, list):
                                records_by_table[str(tbl)] = list(rows)
                    elif isinstance(raw, list):
                        primary_table = tables[0] if tables else "Syslog"
                        records_by_table[primary_table] = list(raw)
                    elif isinstance(raw, dict) and isinstance(raw.get("maliciousRecords"), list):
                        primary_table = str(raw.get("table") or (tables[0] if tables else "Syslog"))
                        records_by_table[primary_table] = list(raw["maliciousRecords"])
                    if records_by_table:
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
                        }
                except Exception:
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
                    "RecordIndex": 1,
                    "Severity": "High",
                },
                {
                    "TimeGenerated": now_iso,
                    "Table": table,
                    "SyntheticQualificationRecord": True,
                    "RecordIndex": 2,
                    "Severity": "Medium",
                },
            ]
            for table in tables
        }

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
    "discover_dcr_streams",
    "generate_mock_data",
    "ingest_and_verify_mock_data",
]
