"""Rebuild selection-criteria-association-impact.md from BEFORE/AFTER CSVs.

Compares the `associated_connectors` column on `asim_parsers.csv` and
`content_items.csv` between two snapshots, and prints each added or
removed (target, connector) pair as a block listing shared tables and
each side's `filter_fields` predicates side-by-side.

By default the BEFORE snapshot is loaded from git via `git show HEAD:...`
relative to the workspace root, and the AFTER snapshot is the working-tree
copy. Override with --before-dir / --after-dir.

Self-contained: csv + subprocess only.
"""
from __future__ import annotations

import argparse
import csv
import io
import subprocess
import sys
from pathlib import Path
from typing import Iterable

DEFAULT_AFTER_DIR = Path(__file__).resolve().parent.parent  # Tools/Solutions Analyzer
DEFAULT_REPO_ROOT = DEFAULT_AFTER_DIR.parent.parent  # workspace root
LINK_PREFIX = "../../../sentinelninja/Solutions Docs"

CSVS = [
    "connectors.csv",
    "asim_parsers.csv",
    "content_items.csv",
    "solutions_connectors_tables_mapping_simplified.csv",
]


def _slug(name: str) -> str:
    return name.lower().replace("_", "-")


def _link(name: str, subdir: str) -> str:
    return f"[`{name}`](<{LINK_PREFIX}/{subdir}/{_slug(name)}.md>)"


def _read_text_csv(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def _read_dir_csv(directory: Path, name: str) -> list[dict]:
    return _read_text_csv((directory / name).read_text(encoding="utf-8"))


def _read_git_csv(repo_root: Path, ref: str, rel_path: str) -> list[dict]:
    text = subprocess.check_output(
        ["git", "show", f"{ref}:{rel_path}"],
        cwd=repo_root,
        encoding="utf-8",
        errors="replace",
    )
    return _read_text_csv(text)


def _split_list(s: str) -> list[str]:
    return [x.strip() for x in (s or "").split(",") if x.strip()]


def _split_predicates(s: str) -> list[str]:
    return [p.strip() for p in (s or "").split("|") if p.strip()]


def _table_set(s: str) -> set[str]:
    return {t.lower() for t in _split_list(s)}


def _index(rows: list[dict], key: str) -> dict[str, dict]:
    return {r[key]: r for r in rows if r.get(key)}


def _connector_tables(
    mapping_rows: list[dict],
) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for r in mapping_rows:
        cid = r.get("connector_id", "").strip()
        tn = r.get("table_name", "").strip().lower()
        if cid and tn:
            out.setdefault(cid, set()).add(tn)
    return out


def _format_block(
    target_link: str,
    connector_link: str,
    shared: set[str],
    target_preds: list[str],
    connector_preds: list[str],
    label: str,
) -> list[str]:
    out = [
        f"#### {label}: {target_link} ↔ {connector_link}",
        "",
        f"- **Shared tables:** {', '.join(sorted(shared)) if shared else '(none)'}",
        "- **Target predicates:**",
    ]
    if target_preds:
        out += [f"  - `{p}`" for p in target_preds]
    else:
        out.append("  - *(empty)*")
    out.append("- **Connector predicates:**")
    if connector_preds:
        out += [f"  - `{p}`" for p in connector_preds]
    else:
        out.append("  - *(empty)*")
    out.append("")
    return out


def _diff_pairs(
    before: list[dict],
    after: list[dict],
    key: str,
) -> tuple[set[tuple[str, str]], set[tuple[str, str]], dict[str, dict], dict[str, dict]]:
    before_pairs: set[tuple[str, str]] = set()
    after_pairs: set[tuple[str, str]] = set()
    for r in before:
        for c in _split_list(r.get("associated_connectors", "")):
            before_pairs.add((r[key], c))
    for r in after:
        for c in _split_list(r.get("associated_connectors", "")):
            after_pairs.add((r[key], c))
    return (
        after_pairs - before_pairs,  # added
        before_pairs - after_pairs,  # removed
        _index(before, key),
        _index(after, key),
    )


def _emit_section(
    *,
    heading: str,
    target_subdir: str,
    target_key: str,
    target_label: str,
    before: list[dict],
    after: list[dict],
    after_connectors: dict[str, dict],
    after_conn_tables: dict[str, set[str]],
) -> tuple[list[str], int, int, int, int]:
    added, removed, before_idx, after_idx = _diff_pairs(before, after, target_key)
    out: list[str] = [heading, ""]
    before_targets_with = sum(
        1 for r in before if _split_list(r.get("associated_connectors", ""))
    )
    after_targets_with = sum(
        1 for r in after if _split_list(r.get("associated_connectors", ""))
    )
    before_pairs_count = sum(
        len(_split_list(r.get("associated_connectors", ""))) for r in before
    )
    after_pairs_count = sum(
        len(_split_list(r.get("associated_connectors", ""))) for r in after
    )

    out.append(
        f"- Items with at least one association: **before {before_targets_with}, "
        f"after {after_targets_with}**"
    )
    out.append(
        f"- (item, connector) pairs: **before {before_pairs_count}, "
        f"after {after_pairs_count}** (delta {after_pairs_count - before_pairs_count:+})"
    )
    out.append("")

    def _block_for(target_id: str, conn_id: str, label: str) -> list[str]:
        # Use AFTER values for shared-tables / predicates when present (gives
        # the corrected view); fall back to BEFORE values for removed pairs.
        target_row = after_idx.get(target_id) or before_idx.get(target_id) or {}
        conn_row = after_connectors.get(conn_id) or {}
        target_tables = _table_set(target_row.get("tables", ""))
        conn_tables = after_conn_tables.get(conn_id, set())
        shared = target_tables & conn_tables
        target_preds = _split_predicates(
            target_row.get("filter_fields") or target_row.get("content_filter_fields") or ""
        )
        conn_preds = _split_predicates(conn_row.get("filter_fields", ""))
        return _format_block(
            _link(target_id, target_subdir),
            _link(conn_id, "connectors"),
            shared,
            target_preds,
            conn_preds,
            label,
        )

    out.append(f"## {target_label} — Added associations")
    out.append("")
    if added:
        for tid, cid in sorted(added):
            out += _block_for(tid, cid, target_label.lower().rstrip("s"))
    else:
        out.append("_(none)_")
        out.append("")

    out.append(f"## {target_label} — Removed associations")
    out.append("")
    if removed:
        for tid, cid in sorted(removed):
            out += _block_for(tid, cid, target_label.lower().rstrip("s"))
    else:
        out.append("_(none)_")
        out.append("")

    return out, before_pairs_count, after_pairs_count, len(added), len(removed)


def _load(
    *,
    repo_root: Path,
    after_dir: Path,
    before_dir: Path | None,
    before_ref: str,
) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    after = {name: _read_dir_csv(after_dir, name) for name in CSVS}
    if before_dir is not None:
        before = {name: _read_dir_csv(before_dir, name) for name in CSVS}
    else:
        # Path inside the repo, with forward slashes for git
        rel = after_dir.relative_to(repo_root).as_posix()
        before = {
            name: _read_git_csv(repo_root, before_ref, f"{rel}/{name}")
            for name in CSVS
        }
    return before, after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--after-dir", type=Path, default=DEFAULT_AFTER_DIR)
    parser.add_argument("--before-dir", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--before-ref", default="HEAD")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent
        / "selection-criteria-association-impact.md",
    )
    args = parser.parse_args()

    before, after = _load(
        repo_root=args.repo_root,
        after_dir=args.after_dir,
        before_dir=args.before_dir,
        before_ref=args.before_ref,
    )

    after_connectors = _index(after["connectors.csv"], "connector_id")
    after_conn_tables = _connector_tables(
        after["solutions_connectors_tables_mapping_simplified.csv"]
    )

    asim_lines, asim_b, asim_a, asim_add, asim_rem = _emit_section(
        heading="## ASIM parsers",
        target_subdir="asim",
        target_key="parser_name",
        target_label="ASIM",
        before=before["asim_parsers.csv"],
        after=after["asim_parsers.csv"],
        after_connectors=after_connectors,
        after_conn_tables=after_conn_tables,
    )

    content_lines, c_b, c_a, c_add, c_rem = _emit_section(
        heading="## Content items",
        target_subdir="content",
        target_key="content_id",
        target_label="Content",
        before=before["content_items.csv"],
        after=after["content_items.csv"],
        after_connectors=after_connectors,
        after_conn_tables=after_conn_tables,
    )

    lines = [
        "# Solution Analyzer — Selection-Criteria Association Impact",
        "",
        "Selection-criteria (filter-field) predicates are used by "
        "`map_solutions_connectors_tables.py` to associate connectors with items "
        "(ASIM parsers and standalone / GitHub-only content items). A connector "
        "matches a target when (a) they share at least one table, and (b) the "
        "connector's per-table filter values are a **subset** of the target's "
        "(an unfiltered connector matches any target on the shared table).",
        "",
        "Each association is rendered as a block with shared tables and both "
        "sides' predicates on separate lines, so wide filter strings remain "
        "readable. An association is correct iff every connector predicate "
        "(per shared table) appears verbatim in the target's predicates. "
        "Connector tables come from "
        "`solutions_connectors_tables_mapping_simplified.csv`; target tables "
        "come from each entity's `tables` column.",
        "",
        "## Summary",
        "",
        "| Target CSV | Before pairs | After pairs | Added | Removed |",
        "|------------|--------------|-------------|-------|---------|",
        f"| `asim_parsers.csv`  | {asim_b} | {asim_a} | {asim_add} | {asim_rem} |",
        f"| `content_items.csv` | {c_b} | {c_a} | {c_add} | {c_rem} |",
        "",
    ] + asim_lines + content_lines

    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output} ({args.output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
