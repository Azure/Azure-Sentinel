"""Pure shared schema compatibility helpers."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict

LA_SYSTEM_COLS = {
    "TenantId", "Type", "SourceSystem", "_ResourceId", "_SubscriptionId",
    "_ItemId", "_TimeReceived", "_BilledSize", "_IsBillable", "MG",
}

LA_TO_AH_RENAME: dict[str, str] = {}

_NUMERIC = {"int", "long", "real", "double", "decimal", "float"}

def _type_relation(la: str, ah: str) -> str:
    """Classify how an LA column type relates to its AH counterpart.

    exact  - same type.
    compat - functionally identical for migration (no code change needed):
             * dynamic <-> string  (AH getschema reports JSON `dynamic` cols as
               `string`; you just parse_json() them, same as in LA).
             * any numeric <-> any numeric (int/long/real...).
             * guid <-> string, bool <-> boolean.
    soft   - a real but trivially castable change (e.g. string <-> int on Port);
             the query needs a toint()/tostring(), but nothing is lost.
    hard   - genuinely incompatible types.
    """
    a, b = (la or "").lower(), (ah or "").lower()
    if a == b:
        return "exact"
    pair = {a, b}
    if pair <= {"dynamic", "string"}:
        return "compat"
    if a in _NUMERIC and b in _NUMERIC:
        return "compat"
    if pair <= {"guid", "string"} or pair <= {"bool", "boolean"}:
        return "compat"
    if ("string" in pair and (a in _NUMERIC or b in _NUMERIC)):
        return "soft"
    return "hard"

def _load(path: Path) -> Dict[str, Dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8"))

def diff_table(la: Dict[str, str], ah: Dict[str, str]) -> dict:
    """Compare one table's LA schema against its AH schema.

    Each meaningful LA column is classified as matched / renamed / compatible
    (trivial type diff) / soft (castable type diff) / typeMismatch (incompatible)
    / missing (no AH counterpart - blocks that column's uses).

    Verdict:
      Easy   - every column matches or is trivially compatible.
      Review - no missing/incompatible cols, but some need a simple cast.
      Hard   - at least one column is missing or has an incompatible type.
    Score = fraction of meaningful LA columns usable in AH (soft counts as 0.5).
    """
    matched, renamed, compatible, soft, type_mismatch, missing = [], [], [], [], [], []
    ah_lower = {k.lower(): (k, v) for k, v in ah.items()}

    meaningful = [c for c in la if c not in LA_SYSTEM_COLS]
    for col in meaningful:
        la_type = la[col]
        target = LA_TO_AH_RENAME.get(col, col)
        if target in ah:
            ah_type = ah[target]
        else:
            _, ah_type = ah_lower.get(target.lower(), (None, None))
        if ah_type is None:
            missing.append(col)
            continue

        rel = _type_relation(la_type, ah_type)
        entry = {"column": col, "la": la_type, "ah": ah_type}
        if target != col:
            entry["ahName"] = target
        if rel == "exact":
            (renamed if target != col else matched).append(entry if target != col else col)
        elif rel == "compat":
            compatible.append(entry)
        elif rel == "soft":
            soft.append(entry)
        else:
            type_mismatch.append(entry)

    considered = len(meaningful) or 1
    ok = len(matched) + len(renamed) + len(compatible) + 0.5 * len(soft)
    score = round(ok / considered, 3)
    extra = [c for c in ah if c not in la and c not in LA_TO_AH_RENAME.values()]

    if missing or type_mismatch:
        verdict = "Hard"
    elif soft:
        verdict = "Review"
    else:
        verdict = "Easy"
    return {
        "verdict": verdict,
        "score": score,
        "matched": matched,
        "renamed": renamed,
        "compatible": compatible,    # trivial type diffs (dynamic<->string, numeric widening)
        "soft": soft,                # castable type diffs (e.g. Port string<->int)
        "typeMismatch": type_mismatch,  # incompatible types -> blocks those uses
        "missingInAh": missing,      # LA columns with no AH counterpart -> blocks those uses
        "extraInAh": extra,          # AH-only columns (harmless for migration)
        "laColumns": len(la),
        "ahColumns": len(ah),
    }
