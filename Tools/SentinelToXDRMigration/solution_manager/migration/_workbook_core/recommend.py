"""Best-fit AH table recommender for Sentinel tables with **no confirmed mapping**.

When a Sentinel table can't be converted (tier `blocked`/`unknown`), the pipeline
shouldn't just say "no equivalent" - it should point the reviewer at the AH
table(s) that come closest, so the query can be re-homed by hand or by the LLM
step. This module produces those recommendations. They are **suggestions, never
automatic conversions** - a blocked table stays `blocked`.

Signals, strongest-first:
  1. curated category hints  - domain knowledge for common Sentinel tables that
     have a well-understood closest AH home (e.g. CommonSecurityLog -> network
     device telemetry). High signal, human-curated.
  2. column overlap          - when the source table's columns are known, score
     each candidate AH table by shared column names (after LA->AH renames). The
     table sharing the most columns is the most natural rewrite target.
  3. fuzzy name similarity   - last resort when nothing else applies.

Every recommendation carries a `basis` and a `reason` so the reviewer can judge
it; recommendations are ranked and capped.
"""
from __future__ import annotations

import difflib
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent
from . import mapping_catalog, migrate

_AH_CACHE = ROOT / "data" / "ah_schema_catalog.json"

# A broad AH advanced-hunting table pool for name/column matching (superset of the
# 21 cached schemas). Kept explicit so recommendations aren't limited to Wave-1.
_AH_TABLE_POOL = {
    # Endpoint / device
    "DeviceEvents", "DeviceFileEvents", "DeviceImageLoadEvents", "DeviceLogonEvents",
    "DeviceNetworkEvents", "DeviceProcessEvents", "DeviceRegistryEvents",
    "DeviceFileCertificateInfo", "DeviceInfo", "DeviceNetworkInfo",
    "DeviceTvmSoftwareInventory", "DeviceTvmSoftwareVulnerabilities",
    "DeviceTvmSecureConfigurationAssessment",
    # Email / collaboration
    "EmailEvents", "EmailAttachmentInfo", "EmailPostDeliveryEvents", "EmailUrlInfo",
    "UrlClickEvents",
    # Cloud apps
    "CloudAppEvents",
    # Identity
    "IdentityLogonEvents", "IdentityDirectoryEvents", "IdentityQueryEvents", "IdentityInfo",
    # Alerts
    "AlertInfo", "AlertEvidence",
    # Entra (AH advanced-hunting Entra tables)
    "EntraIdSignInEvents", "EntraIdSpnSignInEvents", "EntraIdDirectoryAuditEvents",
    "GraphAPIAuditEvents",
}

# Curated closest-AH-home hints for common Sentinel tables with no direct mapping.
# Each entry: (recommended AH tables in priority order, confidence, reason).
_CATEGORY_HINTS: Dict[str, tuple] = {
    # Windows event logs -> device event families
    "SecurityEvent": (["DeviceProcessEvents", "DeviceLogonEvents", "DeviceEvents"], "medium",
                      "Windows Security events map to endpoint device telemetry; pick the "
                      "family matching the EventID (process create/logon/other)."),
    "WindowsEvent": (["DeviceEvents", "DeviceProcessEvents", "DeviceLogonEvents"], "medium",
                     "Windows event logs map to endpoint device telemetry by event type."),
    "Event": (["DeviceEvents", "DeviceProcessEvents"], "low",
              "Generic Windows/Sysmon events map to endpoint device telemetry by event type."),
    # Firewall / CEF / syslog / network
    "CommonSecurityLog": (["DeviceNetworkEvents"], "low",
                          "CEF firewall/appliance network logs have no exact AH equivalent; "
                          "device network telemetry is the closest, but coverage differs."),
    "Syslog": (["DeviceEvents", "DeviceNetworkEvents"], "low",
               "Linux syslog has no exact AH equivalent; device event/network telemetry is closest."),
    "VMConnection": (["DeviceNetworkEvents"], "low",
                     "Azure Monitor VM network connections map closest to device network events."),
    # DNS
    "DnsEvents": (["DeviceNetworkEvents"], "low",
                  "No dedicated AH DNS table; DNS-over-network activity appears in device network events."),
    "ASimDnsActivityLogs": (["DeviceNetworkEvents"], "low",
                            "ASIM DNS parser has no AH equivalent; closest is device network events."),
    # IIS / web
    "W3CIISLog": (["DeviceNetworkEvents"], "low",
                  "IIS web logs have no AH equivalent; only network-level activity is comparable."),
    # Office / cloud app / AWS
    "OfficeActivity": (["CloudAppEvents"], "high",
                       "O365 audit activity is surfaced in AH as CloudAppEvents."),
    "AWSCloudTrail": (["CloudAppEvents"], "medium",
                      "Third-party cloud audit trails are normalized into CloudAppEvents."),
    "AzureActivity": (["CloudAppEvents"], "low",
                      "Azure control-plane activity has no exact AH table; CloudAppEvents is the nearest."),
    # Identity / sign-in
    "SigninLogs": (["EntraIdSignInEvents", "IdentityLogonEvents"], "medium",
                   "Interactive Entra sign-ins map to EntraIdSignInEvents (needs review); "
                   "on-prem/hybrid logons appear in IdentityLogonEvents."),
    "AADNonInteractiveUserSignInLogs": (["EntraIdSignInEvents"], "medium",
                                        "Non-interactive Entra sign-ins merge into EntraIdSignInEvents "
                                        "(discriminate via a sign-in-type column)."),
    "AADServicePrincipalSignInLogs": (["EntraIdSpnSignInEvents"], "medium",
                                      "Service-principal sign-ins map to EntraIdSpnSignInEvents."),
    "AADManagedIdentitySignInLogs": (["EntraIdSpnSignInEvents"], "medium",
                                     "Managed-identity sign-ins fold into EntraIdSpnSignInEvents "
                                     "alongside service-principal sign-ins."),
    "AuditLogs": (["EntraIdDirectoryAuditEvents", "IdentityDirectoryEvents"], "medium",
                  "Entra directory audit maps to EntraIdDirectoryAuditEvents."),
    "MicrosoftGraphActivityLogs": (["GraphAPIAuditEvents"], "medium",
                                   "Graph API activity maps to GraphAPIAuditEvents."),
    # Alerts / TI
    "SecurityAlert": (["AlertInfo", "AlertEvidence"], "medium",
                      "Sentinel alerts map to AH AlertInfo (+ AlertEvidence for entities)."),
    "ThreatIntelligenceIndicator": ([], "none",
                                    "Threat-intel indicators have no AH hunting-table equivalent."),
}


def _ah_schemas() -> Dict[str, Dict[str, str]]:
    return migrate._load(_AH_CACHE)


def _candidate_pool(ah_schemas: Optional[Dict[str, Dict[str, str]]] = None) -> set[str]:
    pool = set(_AH_TABLE_POOL)
    pool |= set((ah_schemas or _ah_schemas()).keys())
    cat = mapping_catalog.load_mapping_catalog()["tables"]
    for meta in cat.values():
        if meta.get("ahTable"):
            pool.add(meta["ahTable"])
    return pool


def _column_overlap(source_cols: Dict[str, str], ah_cols: Dict[str, str]) -> tuple[float, list]:
    """Fraction of meaningful source columns that also exist in the AH table
    (case-insensitive, honoring any global column renames - currently none;
    TimeGenerated exists in AH unchanged)."""
    meaningful = [c for c in source_cols if c not in migrate.LA_SYSTEM_COLS]
    if not meaningful:
        return 0.0, []
    ah_lower = {c.lower() for c in ah_cols}
    matched = []
    for c in meaningful:
        target = migrate.LA_TO_AH_RENAME.get(c, c)
        if target.lower() in ah_lower:
            matched.append(c)
    return round(len(matched) / len(meaningful), 3), matched


def recommend_table(table: str, source_cols: Optional[Dict[str, str]] = None,
                    ah_schemas: Optional[Dict[str, Dict[str, str]]] = None,
                    top: int = 3) -> dict:
    """Rank the best-fit AH tables for one unmapped Sentinel table."""
    ah_schemas = ah_schemas if ah_schemas is not None else _ah_schemas()
    pool = _candidate_pool(ah_schemas)
    recs: List[dict] = []
    seen: set[str] = set()

    # 0. catalog self-mapping wins outright. A table mapped 1:1 to itself is
    #    already a valid AH table on the target tenant - it is its own best
    #    home, so never recommend a different table (kills self->self noise and
    #    now-obsolete category hints like WindowsEvent->DeviceEvents).
    meta = mapping_catalog.load_mapping_catalog()["tables"].get(table)
    if (meta and meta.get("tier") == "1to1" and meta.get("ahTable") == table) or (
        not meta and isinstance(table, str) and table.endswith("_CL")
    ):
        return {"sentinelTable": table,
                "recommendations": [{
                    "ahTable": table, "basis": "catalogSelf", "confidence": "high",
                    "reason": "Offline catalog maps this table to itself; selected "
                              "environment visibility remains unverified."}],
                "hasHint": False}

    # 1. curated category hint
    hint = _CATEGORY_HINTS.get(table)
    if hint:
        ah_list, conf, reason = hint
        for ah in ah_list:
            recs.append({"ahTable": ah, "basis": "category", "confidence": conf,
                         "reason": reason})
            seen.add(ah)
        if not ah_list:  # explicit "no equivalent"
            return {"sentinelTable": table, "recommendations": [],
                    "note": reason, "hasHint": True}

    # 2. column overlap (only if we know the source schema)
    if source_cols:
        scored = []
        for ah in pool:
            ah_cols = ah_schemas.get(ah)
            if not ah_cols:
                continue
            score, matched = _column_overlap(source_cols, ah_cols)
            if score > 0:
                # An AH table with the identical name is, by definition, the
                # right home - it must win ties against sibling tables whose
                # columns happen to overlap just as much (e.g. Device* family).
                exact = 1 if ah.lower() == table.lower() else 0
                scored.append((exact, score, ah, matched))
        scored.sort(reverse=True)
        for _exact, score, ah, matched in scored:
            if ah in seen:
                # enrich the existing category rec with overlap evidence
                for r in recs:
                    if r["ahTable"] == ah:
                        r["columnOverlap"] = score
                        r["matchedColumns"] = matched[:12]
                continue
            recs.append({"ahTable": ah, "basis": "columnOverlap",
                         "confidence": "high" if score >= 0.6 else
                                       "medium" if score >= 0.3 else "low",
                         "reason": f"shares {int(score*100)}% of source columns with {ah}.",
                         "columnOverlap": score, "matchedColumns": matched[:12]})
            seen.add(ah)

    # 3. fuzzy name similarity - only as a last resort, when neither a curated
    #    hint nor column overlap produced anything (avoids noisy matches like
    #    Event -> EmailEvents).
    if not recs:
        for ah in difflib.get_close_matches(table, sorted(pool), n=top, cutoff=0.6):
            if ah in seen:
                continue
            recs.append({"ahTable": ah, "basis": "nameSimilarity", "confidence": "low",
                         "reason": f"table name is similar to '{ah}'."})
            seen.add(ah)

    return {
        "sentinelTable": table,
        "recommendations": recs[:top],
        "note": ("No confirmed AH equivalent; recommendations are best-effort and "
                 "require human/LLM review before use."),
        "hasHint": bool(hint),
    }


def recommend_for_tables(tables: List[str],
                         source_schemas: Optional[Dict[str, Dict[str, str]]] = None,
                         ah_schemas: Optional[Dict[str, Dict[str, str]]] = None,
                         top: int = 3) -> List[dict]:
    """Recommend best-fit AH tables for each unmapped Sentinel table."""
    source_schemas = source_schemas or {}
    return [recommend_table(t, source_cols=source_schemas.get(t),
                            ah_schemas=ah_schemas, top=top) for t in tables]


def unmapped_tables(tables: Optional[List[str]]) -> List[str]:
    """The subset of resolved tables that have no convertible AH mapping
    (catalog tier `blocked`, or absent from the catalog = `unknown`)."""
    cat = mapping_catalog.load_mapping_catalog()["tables"]
    out = []
    for t in (tables or []):
        tier = cat[t]["tier"] if t in cat else ("1to1" if isinstance(t, str) and t.endswith("_CL") else "unknown")
        if tier in ("blocked", "unknown"):
            out.append(t)
    return out


def _main(argv: Optional[List[str]] = None) -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="Recommend best-fit AH tables for unmapped Sentinel tables.")
    p.add_argument("tables", nargs="+", help="Sentinel table name(s)")
    p.add_argument("--top", type=int, default=3)
    args = p.parse_args(argv)
    print(json.dumps(recommend_for_tables(args.tables, top=args.top), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
