"""Migrator core - orchestrates resolve -> classify -> rewrite and emits the
Sentinel->AH conversion output contract (KQL-Conversion-Service-Spec.md §4).

Pure, importable logic (no MCP runtime) so it is unit-testable. The MCP server
(`migrator_server.py`) is a thin wrapper over these functions.

The Migrator fills everything in the contract EXCEPT `validation` - that is the
Judge MCP's job. `confidence` here is therefore *provisional* (pre-validation):
a clean deterministic 1:1 conversion is only high-confidence once the Judge's
static bind / runtime / parity pass.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from . import mapping_catalog, recommend, rewrite, schema_map

# Contract vocab: 1to1 | renamed | merged | blocked. `unknown` (table not in the
# catalog) collapses to `blocked` in the contract's mappingTier.
_CONTRACT_TIERS = {"1to1", "renamed", "merged", "blocked"}
# Provisional confidence per status, before the Judge validates.
_CONFIDENCE = {"converted": 0.7, "needs-review": 0.3, "blocked": 0.0}


def classify(tables: Optional[List[str]]) -> dict:
    """Per-table tier + worst overall tier for a set of resolved tables."""
    cat = mapping_catalog.load_mapping_catalog()["tables"]
    tiers = {
        t: (cat[t]["tier"] if t in cat else ("1to1" if isinstance(t, str) and t.endswith("_CL") else "unknown"))
        for t in (tables or [])
    }
    if not tiers:
        overall = "unknown"
    else:
        overall = max(tiers.values(), key=lambda x: rewrite._TIER_RANK.get(x, 2))
    return {"tiers": tiers, "overallTier": overall}


def _status_of(tables: Optional[List[str]], res: dict) -> str:
    if not tables:
        return "needs-review"          # unresolved data sources -> manual review
    tier = res["overallTier"]
    if tier in ("blocked", "unknown"):
        return "blocked"
    if res["deterministic"]:
        return "converted"
    return "needs-review"


def convert(kql: str, tables: Optional[List[str]] = None,
            source_id: Optional[str] = None, artifact_type: str = "analyticRule",
            resolve: bool = False) -> dict:
    """Convert one Sentinel KQL query and return the output contract.

    tables   - resolved data sources; pass them for offline/batch use.
    resolve  - legacy compatibility argument; True is explicitly unsupported
               by this offline slice.
    """
    resolve_error = None
    if resolve:
        raise ValueError("Live resolution is not supported by the offline converter.")

    res = rewrite.rewrite(kql, tables)
    source_free_literal = (
        not tables and rewrite.is_source_free_literal_query(kql)
    )
    if source_free_literal:
        res["deterministic"] = True
        res["overallTier"] = "1to1"
    status = "converted" if source_free_literal else _status_of(tables, res)
    tier = res["overallTier"]
    mapping_tier = tier if tier in _CONTRACT_TIERS else "blocked"

    unsupported = [{"construct": f["name"], "kind": f["kind"], "reason": f["reason"]}
                   for f in res["flags"]]
    if tables is None and not source_free_literal:
        unsupported.append({
            "construct": "data-sources", "kind": "unresolved",
            "reason": resolve_error or "Data sources could not be resolved "
                      "(ASIM unifying parser / dynamic field access); manual review."})

    blocked_reason = None
    if status == "blocked":
        reasons = [f["reason"] for f in res["flags"]
                   if f["kind"] in ("blocked-table", "unknown-table")]
        blocked_reason = "; ".join(dict.fromkeys(reasons)) or "No convertible AH mapping."

    # For tables with no confirmed AH mapping, recommend the best-fit AH table(s)
    # so a reviewer/LLM can re-home the query instead of hitting a dead end.
    unmapped = recommend.unmapped_tables(tables)
    recommendations = recommend.recommend_for_tables(unmapped) if unmapped else []

    return {
        "sourceId": source_id,
        "artifactType": artifact_type,
        "status": status,
        "convertedKql": res["convertedKql"],
        "resolvedTables": tables or [],
        "mappingTier": mapping_tier,
        "renamedTables": res["renamedTables"],
        "renamedAsimTables": res.get("renamedAsimTables") or {},
        "diff": res["diff"],
        "schemaMap": schema_map.build_schema_map(tables, include_identical_columns=False),
        "recommendations": recommendations,
        "confidence": _CONFIDENCE[status],
        "unsupported": unsupported,
        "validation": None,           # filled by the Judge MCP
        "blockedReason": blocked_reason,
    }
