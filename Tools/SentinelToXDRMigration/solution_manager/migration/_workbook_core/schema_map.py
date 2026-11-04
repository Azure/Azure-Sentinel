"""Column-level schema mapper for Sentinel -> Advanced Hunting migration.

When a Sentinel table maps to an AH table whose schema is **not identical**, a
correct migration must say *how each column maps* - the exact matches, the
renames, the type casts, and the columns that have **no direct AH equivalent**
(with a best-effort suggestion, never a silent drop). This module produces that
per-column mapping so the output contract carries "the most appropriate schema".

Sources of truth, cheapest-first:
  - LA side  : cached `data/la_schema_catalog.json`  ({table: {col: type}}).
  - AH side  : cached `data/ah_schema_catalog.json` (offline, 21 Wave-1 tables),
               or an explicitly supplied schema-provider callback. This
               imported slice contains no live clients or authentication.
  - renames  : the mapping catalog's per-table `columnRenames` (authoritative
               for known Wave-2 column renames).

Relations emitted per column:
  exact        - same name, same/compatible-identical type; use as-is.
  compatible   - same name, trivially-compatible type (e.g. dynamic<->string).
  renamed      - different AH name (via catalog/case), compatible type.
  castNeeded   - real but trivially castable type diff (toint()/tostring()).
  typeMismatch - genuinely incompatible types; blocks that column's uses.
  missing      - no AH counterpart; carries a best-effort `suggestion` or is
                 flagged for review. Never silently dropped.

Reuses `migrate._type_relation` / `LA_TO_AH_RENAME` / `LA_SYSTEM_COLS` so the
type semantics match the schema-diff step exactly.
"""
from __future__ import annotations

import difflib
from pathlib import Path
from typing import Callable, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
from . import mapping_catalog, migrate

_LA_CACHE = ROOT / "data" / "la_schema_catalog.json"
_AH_CACHE = ROOT / "data" / "ah_schema_catalog.json"

AhSchemaProvider = Callable[[str], Optional[Dict[str, str]]]


def _la_cached() -> Dict[str, Dict[str, str]]:
    return migrate._load(_LA_CACHE)


def _ah_cached() -> Dict[str, Dict[str, str]]:
    return migrate._load(_AH_CACHE)






def _suggest(col: str, ah_cols: Dict[str, str],
             catalog_renames: Dict[str, str]) -> tuple[Optional[str], Optional[str]]:
    """Best-effort AH column for an LA column with no direct match."""
    if col in catalog_renames and catalog_renames[col] in ah_cols:
        return catalog_renames[col], "catalog"
    lower = {c.lower(): c for c in ah_cols}
    if col.lower() in lower:
        return lower[col.lower()], "case"
    close = difflib.get_close_matches(col, list(ah_cols), n=1, cutoff=0.82)
    if close:
        return close[0], "fuzzy"
    return None, None


def map_table(la_table: str, ah_table: str, la_cols: Dict[str, str],
              ah_cols: Dict[str, str], catalog_renames: Dict[str, str]) -> dict:
    """Per-column mapping for one LA->AH table pair."""
    ah_lower = {c.lower(): c for c in ah_cols}
    meaningful = [c for c in la_cols if c not in migrate.LA_SYSTEM_COLS]
    columns: List[dict] = []
    used_ah: set[str] = set()

    for col in meaningful:
        la_type = la_cols[col]
        target = catalog_renames.get(col) or migrate.LA_TO_AH_RENAME.get(col, col)
        was_renamed = target != col

        ah_name = ah_type = None
        if target in ah_cols:
            ah_name, ah_type = target, ah_cols[target]
        elif target.lower() in ah_lower:
            ah_name = ah_lower[target.lower()]
            ah_type = ah_cols[ah_name]

        if ah_name is None:
            sug, ssrc = _suggest(col, ah_cols, catalog_renames)
            columns.append({
                "sentinel": col, "laType": la_type, "ah": None, "ahType": None,
                "relation": "missing", "suggestion": sug, "suggestionSource": ssrc,
                "note": (f"no direct AH equivalent; suggest '{sug}'" if sug
                         else "no direct AH equivalent; flag for review"),
            })
            continue

        used_ah.add(ah_name)
        rel = migrate._type_relation(la_type, ah_type)
        if ah_name != col:
            relation = "renamed" if rel in ("exact", "compat") else (
                "castNeeded" if rel == "soft" else "typeMismatch")
        else:
            relation = {"exact": "exact", "compat": "compatible",
                        "soft": "castNeeded", "hard": "typeMismatch"}[rel]

        entry = {"sentinel": col, "ah": ah_name, "laType": la_type,
                 "ahType": ah_type, "relation": relation}
        if ah_name != col:
            entry["renamedFrom"] = col
        columns.append(entry)

    extra = [c for c in ah_cols
             if c not in used_ah and c not in migrate.LA_SYSTEM_COLS]
    # Consistent verdict/score with the schema-diff step.
    diff = migrate.diff_table(la_cols, ah_cols)
    identical = all(c["relation"] in ("exact", "compatible") for c in columns)

    return {
        "sentinelTable": la_table,
        "ahTable": ah_table,
        "identical": identical,
        "verdict": diff["verdict"],
        "score": diff["score"],
        "columns": columns,
        "extraInAh": extra,
    }


def build_schema_map(tables: Optional[List[str]],
                     ah_schema_provider: Optional[AhSchemaProvider] = None,
                     include_identical_columns: bool = True) -> List[dict]:
    """Schema map for every resolved table.

    ``ah_schema_provider`` supplies the AH schema per AH-table-name; pass
    a caller-owned schema provider, or omit to use the
    offline cache. When ``include_identical_columns`` is False, tables whose
    schema is identical collapse to a compact summary (keeps contracts light).
    """
    la = _la_cached()
    cat = mapping_catalog.load_mapping_catalog()["tables"]
    ah_cache = None if ah_schema_provider else _ah_cached()
    out: List[dict] = []

    for t in (tables or []):
        meta = cat.get(t, {})
        ah_table = meta.get("ahTable") or t
        renames = meta.get("columnRenames") or {}
        la_cols = la.get(t)
        ah_cols = (ah_schema_provider(ah_table) if ah_schema_provider
                   else ah_cache.get(ah_table))

        if not ah_cols and not la_cols:
            out.append({"sentinelTable": t, "ahTable": ah_table, "identical": None,
                        "columnRenames": renames,
                        "note": "no cached schema for either side; catalog renames only"})
            continue
        if not ah_cols:
            out.append({"sentinelTable": t, "ahTable": ah_table, "identical": None,
                        "columnRenames": renames,
                        "note": "AH schema unavailable (fetch live for a full map); "
                                "using catalog renames"})
            continue
        if not la_cols:
            out.append({"sentinelTable": t, "ahTable": ah_table, "identical": None,
                        "ahColumns": len(ah_cols), "note": "LA schema not cached"})
            continue

        m = map_table(t, ah_table, la_cols, ah_cols, renames)
        if m["identical"] and not include_identical_columns:
            m = {"sentinelTable": t, "ahTable": ah_table, "identical": True,
                 "verdict": m["verdict"], "score": m["score"],
                 "columnCount": len(m["columns"]),
                 "note": "schema identical; no column changes"}
        out.append(m)
    return out
