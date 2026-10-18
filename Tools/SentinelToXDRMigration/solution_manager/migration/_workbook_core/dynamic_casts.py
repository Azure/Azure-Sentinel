"""Wave-1 XDR table column gotchas: dynamic-as-string casts, a removed
column, and a string->int type change (mcp/rewrite.py, step 3 extension).

Source: docs/Sentinel-to-XDR-KQL-Migration-V2 1.md - a per-table playbook
backed by live schema (`getschema`) and per-record value comparison on both
platforms. Three classes of gotcha, none of which the Judge's static/runtime
bind check catches (the query still binds and "passes" - it just silently
returns 0/wrong rows):

  1. Dynamic columns (e.g. `AdditionalFields`, `LoggedOnUsers`) are delivered
     as JSON **text** in Advanced Hunting. `Col.Field` member access or
     `mv-expand Col` on an un-cast column fails **silently** - this module
     auto-injects the documented fix (`| extend Col = todynamic(tostring(Col))`)
     right after the table's first reference, deterministic and safe.
  2. `Port`/`DestinationPort` changed type string->int on the three Identity*
     tables - a quoted numeric-literal comparison (`Port == "445"`) silently
     returns nothing. This module auto-unquotes it (mechanical, safe: only
     touches a quoted *numeric* literal).
  3. `DeviceInfo.DeviceObjectId` was removed in AH (replaced by `DeviceId`).
     There's no safe mechanical rewrite for this (the query's logic may
     depend on it), so it is only *flagged* for manual review, never
     auto-fixed - consistent with how `rewrite.py` treats other LA-only
     columns.

Always-on (unlike bronze.py's opt-in Bronze-tier handling): these gaps are a
fixed property of the AH schema (confirmed live on the target tenant), not
tenant-dependent.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

__all__ = ["inject_dynamic_casts", "unquote_int_literals", "flag_removed_columns"]


def _split_statements(kql: str) -> List[str]:
    return kql.split(";")


def _references_table(stmt: str, table: str) -> bool:
    t = re.escape(table)
    return bool(re.search(rf"\b{t}\b", stmt)
                or re.search(rf"\[\s*[\"']{t}[\"']\s*\]", stmt))


def _inject_after_table(stmt: str, table: str, clause: str) -> "str | None":
    """Insert `clause` immediately after the first reference to `table` in
    `stmt` (mirrors bronze.py's `_inject_after_table`)."""
    m = re.search(rf"\b{re.escape(table)}\b", stmt)
    if not m:
        m = re.search(rf"\[\s*[\"']{re.escape(table)}[\"']\s*\]", stmt)
    if not m:
        return None
    end = m.end()
    trailing = stmt[end:]
    ws = re.match(r"[ \t]*\r?\n[ \t]*", trailing)
    sep = ws.group(0) if ws else "\n"
    return stmt[:end] + sep + clause + " " + trailing.lstrip(" \t")


def _needs_cast(stmt: str, col: str) -> bool:
    """True if `stmt` accesses `col.<member>` or `mv-expand col` without an
    existing `todynamic(tostring(col))` cast already present."""
    if re.search(rf"todynamic\s*\(\s*tostring\s*\(\s*{re.escape(col)}\s*\)\s*\)", stmt):
        return False
    return bool(re.search(rf"\b{re.escape(col)}\s*\.\s*\w", stmt)
                or re.search(rf"mv-expand\s+{re.escape(col)}\b", stmt, re.I))


def inject_dynamic_casts(kql: str, tables: Dict[str, List[str]]) -> Tuple[str, List[dict]]:
    """For every `{table: [castColumns]}` pair, inject a `todynamic(tostring())`
    cast right after the table's first reference in any statement that accesses
    the column without one already present. Returns (new_kql, diff_entries)."""
    if not tables:
        return kql, []
    stmts = _split_statements(kql)
    diffs: List[dict] = []
    for i, stmt in enumerate(stmts):
        for table, cols in tables.items():
            if not cols or not _references_table(stmt, table):
                continue
            for col in cols:
                if not _needs_cast(stmt, col):
                    continue
                clause = f"| extend {col} = todynamic(tostring({col}))"
                new_stmt = _inject_after_table(stmt, table, clause)
                if new_stmt and new_stmt != stmt:
                    stmts[i] = new_stmt
                    stmt = new_stmt
                    diffs.append({
                        "kind": "dynamic-cast", "before": col,
                        "after": f"{col} = todynamic(tostring({col}))",
                        "count": 1, "source": "deterministic",
                        "reason": f"`{col}` on `{table}` is delivered as a JSON "
                                  f"string in Advanced Hunting; member access / "
                                  f"mv-expand without a cast fails silently "
                                  f"(0 rows, no bind error).",
                    })
    return ";".join(stmts), diffs


def unquote_int_literals(kql: str, tables: Dict[str, List[str]]) -> Tuple[str, List[dict]]:
    """For tables whose columns changed type string->int in AH (e.g.
    `Port`/`DestinationPort` on the Identity* tables), strip quotes off a
    quoted *numeric*-literal comparison (`Port == "445"` -> `Port == 445`).
    Only touches a quoted numeric literal, so it's mechanical and safe."""
    cols = sorted({c for t_cols in tables.values() for c in t_cols})
    if not cols:
        return kql, []
    pat = re.compile(
        r'\b(' + "|".join(re.escape(c) for c in cols) + r')'
        r'(\s*(?:==|!=)\s*)"(\d+)"')
    diffs: List[dict] = []

    def repl(m: "re.Match") -> str:
        col, op, num = m.group(1), m.group(2), m.group(3)
        diffs.append({
            "kind": "int-literal-unquote", "before": f'{col}{op}"{num}"',
            "after": f'{col}{op}{num}', "count": 1, "source": "deterministic",
            "reason": f"`{col}` changed type string->int in Advanced Hunting; "
                      f"a quoted literal comparison silently returns no rows.",
        })
        return f"{col}{op}{num}"

    new_kql = pat.sub(repl, kql)
    return new_kql, diffs


def flag_removed_columns(kql: str, tables: Dict[str, List[str]]) -> List[dict]:
    """Flag (never auto-fix) a reference to a column removed in AH - the query
    may depend on it, so only a human can decide the right replacement."""
    flags: List[dict] = []
    for table, cols in tables.items():
        for col in cols:
            if re.search(rf"\b{re.escape(col)}\b", kql):
                flags.append({
                    "kind": "removed-column", "name": col,
                    "reason": f"`{col}` was removed on `{table}` in Advanced "
                              f"Hunting; use `DeviceId` as the device key "
                              f"instead. Needs manual handling.",
                })
    return flags
