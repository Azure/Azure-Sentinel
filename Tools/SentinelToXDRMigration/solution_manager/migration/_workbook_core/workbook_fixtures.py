"""Deterministic, actual-row workbook harnesses and exact result assertions.

Emitting KQL is not executing KQL. No live clients are imported by this module.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re

from . import dataframes, workbook


def substitute(query: str, substitutions: dict[str, str], clock: str) -> str:
    """Explicit fixture literals, never production template neutralization."""
    token = re.compile(r"\{([A-Za-z_][\w .-]*(?::[^{}]*)?)\}")
    missing = set(token.findall(query)) - substitutions.keys()
    if missing:
        raise ValueError(f"Missing explicit fixture substitutions: {sorted(missing)}")
    query = token.sub(lambda m: substitutions[m[1]], query)
    # Only executable now() is fixed; strings/comments remain untouched.
    result = "".join(
        re.sub(r"\bnow\s*\(\s*\)", f"datetime({clock})", text) if kind == "code" else text
        for kind, text in workbook.rewrite._segments(query)
    )
    if any(re.search(r"\b(?:now|ago)\s*\(", text) for kind, text in
           workbook.rewrite._segments(result) if kind == "code"):
        raise ValueError("Express relative time against the pinned fixture clock explicitly.")
    return result


def assert_result(expected: dict, actual: dict) -> None:
    """Compare names/types, cells, nulls, aggregates and bins, not just row counts."""
    if actual.get("columns") != expected["columns"]:
        raise AssertionError(f"Column mismatch: {actual.get('columns')} != {expected['columns']}")
    rows = actual.get("rows")
    if not isinstance(rows, list) or any(len(row) != len(expected["columns"]) for row in rows):
        raise AssertionError("Invalid result row shape")
    encode = lambda row: json.dumps(row, sort_keys=True, separators=(",", ":"))
    if expected.get("ordered", False):
        equal = list(map(encode, rows)) == list(map(encode, expected["rows"]))
    else:
        equal = Counter(map(encode, rows)) == Counter(map(encode, expected["rows"]))
    if not equal:
        raise AssertionError(f"Cell/aggregate/time-bin mismatch: {rows} != {expected['rows']}")
    if expected.get("sortGroups"):
        groups = expected["sortGroups"]
        index = [column["name"] for column in expected["columns"]].index(groups["column"])
        ranks = [groups["ranks"][row[index]] for row in rows]
        if ranks != sorted(ranks):
            raise AssertionError("Result sort-group order mismatch")


def harness_files(manifest: dict, source: dict, converted: dict) -> dict[str, str]:
    """Build artifacts in memory so callers can validate before writing."""
    clock = manifest["clock"]
    if manifest.get("seed") is None:
        raise ValueError("Manifest must pin a seed (rows are explicit; no random generation).")
    source_queries = {s["path"]: s["node"]["query"] for s in workbook.query_surfaces(source)}
    converted_queries = {s["path"]: s["node"]["query"] for s in workbook.query_surfaces(converted)}
    files = {}
    for case in manifest["cases"]:
        case_id = case["id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", case_id):
            raise ValueError("Fixture case IDs must be filesystem-safe.")
        for side, queries, path in (
            ("sentinel", source_queries, case["sourcePath"]),
            ("ah", converted_queries, case.get("outputPath", case["sourcePath"])),
        ):
            query = substitute(queries[path], case["substitutions"], clock)
            stubs = []
            for table, fixture in manifest["tables"].items():
                schema, rows = fixture["schema"], fixture["rows"]
                known = dataframes.schema_for(table, side)
                if known and any(known.get(c) != t for c, t in schema.items()):
                    raise ValueError(f"Fixture schema differs from cached {side} schema: {table}")
                stub = dataframes.datatable_stub(table, schema, rows=rows)
                window = case.get("tableTimeRanges", {}).get(table)
                if window:
                    column = window["column"]
                    if schema.get(column) != "datetime":
                        raise ValueError("Fixture time context must name a datetime column.")
                    start, end = window["start"], window["end"]
                    parsed = [datetime.fromisoformat(v.replace("Z", "+00:00")) for v in (start, end)]
                    if any(v.tzinfo is None for v in parsed) or parsed[0] > parsed[1]:
                        raise ValueError("Invalid fixture time context.")
                    # Model the workbook provider's external timespan on the input,
                    # never filter after an aggregation that removed TimeGenerated.
                    stub = stub[:-1] + (
                        f"\n| where {dataframes._col_name(column)} between "
                        f"(datetime({start}) .. datetime({end}));")
                stubs.append(stub)
            filename = f"{case_id}.{side}.kql"
            if filename in files:
                raise ValueError("Duplicate fixture case ID.")
            files[filename] = (
                "// FIXTURE ONLY: explicit rows and fixed clock; not shipped.\n"
                + "\n".join(stubs) + "\n" + query + "\n")
    expected = {case["id"]: case["expected"] for case in manifest["cases"]}
    files["expected.json"] = json.dumps(expected, indent=2) + "\n"
    return files


def emit(manifest: dict, source: dict, converted: dict, out: Path) -> dict:
    files = harness_files(manifest, source, converted)
    out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8")
    return {"files": [name for name in files if name.endswith(".kql")],
            "execution": "not-run", "seed": manifest["seed"], "clock": manifest["clock"]}
