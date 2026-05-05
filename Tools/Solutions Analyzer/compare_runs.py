#!/usr/bin/env python3
"""Compare two Solutions Analyzer runs (CSV directories), with rename detection.

Two CSV directories are compared row-by-row using each entity type's natural
identifier. For connectors, an additional pass detects **renames** by matching
strictly-removed and strictly-added rows that share the same primary file path
(`connector_files`). This avoids the common mistake of treating a connector
whose ID was changed in JSON as a new connector + a removed connector.

Usage:
    python compare_runs.py --before <dir-or-csv-base> --after <dir-or-csv-base> [--out <md-file>]

By default, prints a summary to stdout. With ``--out``, writes a markdown report.

Each side may be either:
- a directory containing the CSVs (e.g. a checkout of the output branch's
  ``Tools/Solutions Analyzer`` folder), or
- a path produced by ``git show <ref>:Tools/Solutions Analyzer/`` (use a
  helper to materialize that as a directory first).
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# Per-CSV identifier column. Only files listed here are compared.
IDENTIFIERS: dict[str, str] = {
    "solutions.csv": "solution_name",
    "connectors.csv": "connector_id",
    "tables.csv": "table_name",
    "parsers.csv": "parser_name",
    "asim_parsers.csv": "parser_name",
    "content_items.csv": "content_item_id",
}

# CSVs where we attempt rename detection (added<->removed pairs sharing a key).
RENAME_KEYS: dict[str, str] = {
    # Connectors: the JSON path is the most reliable per-connector key.
    "connectors.csv": "connector_files",
}


@dataclass
class CSVDiff:
    name: str
    id_column: str
    added: list[dict] = field(default_factory=list)
    removed: list[dict] = field(default_factory=list)
    renamed: list[tuple[dict, dict]] = field(default_factory=list)  # (old_row, new_row)


def _load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _primary_path(row: dict, key: str) -> str:
    """Return the first non-empty path in a semicolon-joined column, lower-cased."""
    raw = (row.get(key) or "").strip()
    if not raw:
        return ""
    first = raw.split(";")[0].strip()
    return first.lower()


def diff_csv(before_path: Path, after_path: Path, name: str) -> CSVDiff | None:
    if not before_path.exists() or not after_path.exists():
        return None
    id_col = IDENTIFIERS[name]
    before = _load(before_path)
    after = _load(after_path)
    before_by_id = {(r.get(id_col) or "").strip(): r for r in before if (r.get(id_col) or "").strip()}
    after_by_id = {(r.get(id_col) or "").strip(): r for r in after if (r.get(id_col) or "").strip()}

    added_ids = sorted(set(after_by_id) - set(before_by_id))
    removed_ids = sorted(set(before_by_id) - set(after_by_id))

    diff = CSVDiff(name=name, id_column=id_col)

    # Rename detection (connectors only by default).
    rename_key = RENAME_KEYS.get(name)
    if rename_key:
        before_path_index: dict[str, str] = {}
        for cid in removed_ids:
            p = _primary_path(before_by_id[cid], rename_key)
            if p:
                before_path_index[p] = cid

        matched_added: set[str] = set()
        matched_removed: set[str] = set()
        for cid in added_ids:
            p = _primary_path(after_by_id[cid], rename_key)
            if p and p in before_path_index:
                old_id = before_path_index[p]
                diff.renamed.append((before_by_id[old_id], after_by_id[cid]))
                matched_added.add(cid)
                matched_removed.add(old_id)
        added_ids = [c for c in added_ids if c not in matched_added]
        removed_ids = [c for c in removed_ids if c not in matched_removed]

    diff.added = [after_by_id[c] for c in added_ids]
    diff.removed = [before_by_id[c] for c in removed_ids]
    return diff


def _short_path(row: dict, key: str | None) -> str:
    if not key:
        return ""
    raw = (row.get(key) or "").split(";")[0].strip()
    # Trim long GitHub blob URL prefixes for display.
    pfx = "https://github.com/Azure/Azure-Sentinel/blob/master/"
    return raw[len(pfx):] if raw.startswith(pfx) else raw


def write_summary(diffs: list[CSVDiff], out: Path | None) -> str:
    lines: list[str] = []
    p = lines.append

    p("# Solutions Analyzer run comparison")
    p("")
    p("| File | Added | Removed | Renamed |")
    p("|---|---:|---:|---:|")
    for d in diffs:
        p(f"| `{d.name}` | {len(d.added)} | {len(d.removed)} | {len(d.renamed)} |")
    p("")

    for d in diffs:
        if not (d.added or d.removed or d.renamed):
            continue
        p(f"## `{d.name}`")
        p("")
        rkey = RENAME_KEYS.get(d.name)
        if d.renamed:
            p(f"### Renamed ({len(d.renamed)})")
            p("")
            p("| Prior ID | New ID | Shared key |")
            p("|---|---|---|")
            for old, new in d.renamed:
                shared = _short_path(new, rkey)
                p(f"| `{old.get(d.id_column, '')}` | `{new.get(d.id_column, '')}` | `{shared}` |")
            p("")
        if d.added:
            p(f"### Added ({len(d.added)})")
            p("")
            p(f"| {d.id_column} |" + (" Path |" if rkey else ""))
            p("|---|" + ("---|" if rkey else ""))
            for r in d.added:
                row = f"| `{r.get(d.id_column, '')}` |"
                if rkey:
                    row += f" `{_short_path(r, rkey)}` |"
                p(row)
            p("")
        if d.removed:
            p(f"### Removed ({len(d.removed)})")
            p("")
            p(f"| {d.id_column} |" + (" Path |" if rkey else ""))
            p("|---|" + ("---|" if rkey else ""))
            for r in d.removed:
                row = f"| `{r.get(d.id_column, '')}` |"
                if rkey:
                    row += f" `{_short_path(r, rkey)}` |"
                p(row)
            p("")

    text = "\n".join(lines)
    if out:
        out.write_text(text, encoding="utf-8")
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--before", required=True, type=Path,
                    help="Directory containing prior-run CSV files.")
    ap.add_argument("--after", required=True, type=Path,
                    help="Directory containing current-run CSV files.")
    ap.add_argument("--out", type=Path,
                    help="Optional path to write a markdown report. "
                         "When omitted, prints to stdout.")
    args = ap.parse_args()

    if not args.before.is_dir() or not args.after.is_dir():
        print("error: --before and --after must be directories", file=sys.stderr)
        return 2

    diffs: list[CSVDiff] = []
    for name in IDENTIFIERS:
        d = diff_csv(args.before / name, args.after / name, name)
        if d is not None:
            diffs.append(d)

    text = write_summary(diffs, args.out)
    if not args.out:
        print(text)
    else:
        print(f"Wrote {args.out}")
        # Brief stdout summary.
        for d in diffs:
            print(f"  {d.name}: +{len(d.added)} / -{len(d.removed)} / renamed {len(d.renamed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
