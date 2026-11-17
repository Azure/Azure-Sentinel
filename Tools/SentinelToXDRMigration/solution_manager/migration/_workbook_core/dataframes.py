"""Schema-driven `datatable()` "dataframe" stubs for tenant-independent unit tests.

A converted query can only be validated against a live tenant if that tenant
actually *has* the referenced table. That makes validation tenant-dependent and
brittle: a table absent on the validation tenant fails to bind even when the
query is perfectly correct.

This module removes that dependency. For any table we have a schema for, it emits

    let <Table> = datatable(<Col:type>, ...)[ <rows> ];

Because a `let` binding resolves **ahead of** any real table of the same name,
prepending this stub to a query lets it parse, bind, and run whether or not the
tenant has the table. An **empty** datatable (`[]`) binds and returns 0 rows -
a deterministic *schema/bind* unit test. Seeded rows (a later hook) turn it into
a *behavioral* test.

Two flavours, from the two schema catalogs:
  - **sentinel** side: `data/la_schema_catalog.json` (Log Analytics schema) - so
    the *original* Sentinel query is self-contained and testable.
  - **ah** side: `data/ah_schema_catalog.json` (Advanced Hunting schema) - so the
    *converted* query is self-contained and testable.

These stubs are **test scaffolding only**. They are never injected into the
delivered KQL - the shipped query stays byte-faithful.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent
from . import mapping_catalog, migrate

_LA_CACHE = ROOT / "data" / "la_schema_catalog.json"
_AH_CACHE = ROOT / "data" / "ah_schema_catalog.json"

# KQL scalar types valid inside `datatable(...)`. Anything else falls back to
# `string` (a stub never needs to be type-perfect - it must only bind).
_VALID_DATATABLE_TYPES = {
    "bool", "boolean", "datetime", "date", "decimal", "dynamic", "guid",
    "int", "long", "real", "double", "string", "timespan", "time",
}
_TYPE_ALIASES = {
    "boolean": "bool", "date": "datetime", "double": "real", "time": "timespan",
}

_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _norm_type(kql_type: Optional[str]) -> str:
    t = (kql_type or "").strip().lower()
    t = _TYPE_ALIASES.get(t, t)
    return t if t in _VALID_DATATABLE_TYPES else "string"


def _col_name(name: str) -> str:
    """Bare identifier when possible, else a bracketed/quoted name so odd column
    names (spaces, punctuation) still form a valid `datatable` schema."""
    return name if _IDENT_RE.match(name) else '["%s"]' % name.replace('"', '\\"')


# --- schema lookup -----------------------------------------------------------
def _la_cached() -> Dict[str, Dict[str, str]]:
    return migrate._load(_LA_CACHE)


def _ah_cached() -> Dict[str, Dict[str, str]]:
    return migrate._load(_AH_CACHE)


def _ah_table_name(sentinel_table: str) -> str:
    """AH table name for a Sentinel table (identical for Wave-1 XDR tables;
    catalog-mapped for renamed Wave-2 tables)."""
    meta = mapping_catalog.load_mapping_catalog()["tables"].get(sentinel_table, {})
    return meta.get("ahTable") or sentinel_table


def schema_for(table: str, side: str = "ah") -> Optional[Dict[str, str]]:
    """Return `{column: kqlType}` for `table` on the given side, or None if the
    schema isn't cached. For the AH side, `table` may be either the Sentinel name
    (it is mapped to its AH counterpart) or the AH name directly."""
    if side == "sentinel":
        return _la_cached().get(table)
    if side == "ah":
        ah = _ah_cached()
        return ah.get(table) or ah.get(_ah_table_name(table))
    raise ValueError(f"side must be 'sentinel' or 'ah', got {side!r}")


# --- stub construction -------------------------------------------------------
def datatable_stub(table: str, schema: Dict[str, str],
                   rows: Optional[Sequence[Sequence[object]]] = None,
                   let_name: Optional[str] = None) -> str:
    """Build `let <table> = datatable(<schema>)[ <rows> ];` from a `{col: type}`
    schema. `rows` is an optional list of value-tuples (behavioral hook); omit
    for an empty schema/bind stub. Column order follows the schema dict order."""
    if not schema:
        raise ValueError(f"empty schema for {table!r}; cannot build a stub")
    name = let_name or table
    cols = ", ".join(f"{_col_name(c)}:{_norm_type(t)}" for c, t in schema.items())
    body = _format_rows(schema, rows) if rows else ""
    return f"let {name} = datatable({cols})[{body}];"


def _format_rows(schema: Dict[str, str],
                 rows: Sequence[Sequence[object]]) -> str:
    types = [_norm_type(t) for t in schema.values()]
    flat: List[str] = []
    for row in rows:
        if len(row) != len(types):
            raise ValueError(
                f"row has {len(row)} values but schema has {len(types)} columns")
        flat.extend(_literal(v, ty) for v, ty in zip(row, types))
    return "\n    " + ",\n    ".join(
        ", ".join(flat[i:i + len(types)]) for i in range(0, len(flat), len(types))
    ) + "\n" if flat else ""


def _literal(value: object, kql_type: str) -> str:
    if value is None:
        return {"string": '""', "dynamic": "dynamic(null)"}.get(
            kql_type, f"{kql_type}(null)")
    if kql_type in ("int", "long", "real", "decimal"):
        return str(value)
    if kql_type == "bool":
        return "true" if value else "false"
    if kql_type == "datetime":
        return f"datetime({value})"
    if kql_type == "timespan":
        return str(value)
    if kql_type == "dynamic":
        import json
        return f"dynamic({json.dumps(value)})"
    s = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def stub_for(table: str, side: str = "ah",
             rows: Optional[Sequence[Sequence[object]]] = None) -> Optional[str]:
    """`datatable` stub for `table` on `side`, or None if no schema is cached.
    On the AH side the stub's `let` name is the AH table name (what the converted
    query references)."""
    schema = schema_for(table, side)
    if not schema:
        return None
    let_name = _ah_table_name(table) if side == "ah" else table
    return datatable_stub(table, schema, rows=rows, let_name=let_name)


# --- referenced-table detection ----------------------------------------------
