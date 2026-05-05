"""Rebuild selection-criteria.md from the current Solutions Analyzer CSVs.

Self-contained — no dependencies beyond the csv module. Run from the
Tools/Solutions Analyzer/.session-2026-04-30/ folder, or pass --csv-dir.

The output is the same selection-criteria.md report that was produced
during the 2026-04-30 session: one section per source CSV
(connectors / parsers / asim_parsers / content_items), one row per item
with the item name (linked into the local sentinelninja docs repo)
and its filter_fields predicates.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable

# Default CSV dir is the parent (Tools/Solutions Analyzer/) of this script.
DEFAULT_CSV_DIR = Path(__file__).resolve().parent.parent

# Relative prefix from .session-2026-04-30/ to the sibling sentinelninja repo.
LINK_PREFIX = "../../../sentinelninja/Solutions Docs"


def _slug(name: str) -> str:
    return name.lower().replace("_", "-")


def _link(name: str, subdir: str) -> str:
    return f"[`{name}`](<{LINK_PREFIX}/{subdir}/{_slug(name)}.md>)"


def _row(name_md: str, filter_fields: str) -> str:
    # Pipe in filter_fields must be escaped to keep markdown table cells intact.
    cleaned = (filter_fields or "").strip()
    cleaned = cleaned.replace("|", "\\|")
    return f"| {name_md} | {cleaned} |"


def _section(
    title: str,
    rows: Iterable[tuple[str, str]],
) -> list[str]:
    rows_sorted = sorted(rows, key=lambda r: r[0].lower())
    rows_with_filter = [r for r in rows_sorted if r[1].strip()]
    out = [
        f"## {title} — {len(rows_with_filter)} items",
        "",
        "| Item | Selection criteria |",
        "|------|--------------------|",
    ]
    for name_md, ff in rows_with_filter:
        out.append(_row(name_md, ff))
    out.append("")
    return out


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-dir", type=Path, default=DEFAULT_CSV_DIR)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "selection-criteria.md",
    )
    args = parser.parse_args()

    csv_dir: Path = args.csv_dir

    connectors = _read_csv(csv_dir / "connectors.csv")
    parsers = _read_csv(csv_dir / "parsers.csv")
    asim_parsers = _read_csv(csv_dir / "asim_parsers.csv")
    content_items = _read_csv(csv_dir / "content_items.csv")

    lines: list[str] = [
        "# Solution Analyzer — Selection Criteria",
        "",
        "All extracted selection-criteria predicates (filter fields) per item, "
        "produced by `map_solutions_connectors_tables.py`. Predicates use the "
        'format `Table.Field operator "value"`. The synthetic table name '
        "`_Computed` indicates a predicate on a field defined earlier in the "
        "query via `| extend Name = ...`.",
        "",
        "Item names link to the corresponding page in the local "
        "`sentinelninja/Solutions Docs/` repository (sibling of this repo). If a "
        "target page is missing, the link will 404 in the local browser.",
        "",
        "See [`script-docs/map_solutions_connectors_tables.md` › Filter Fields "
        "Detection](../script-docs/map_solutions_connectors_tables.md#filter-fields-detection)"
        " for how this is extracted.",
        "",
    ]

    lines += _section(
        "Connectors (`connectors.csv` › `filter_fields`)",
        (
            (_link(r["connector_id"], "connectors"), r.get("filter_fields", ""))
            for r in connectors
        ),
    )
    lines += _section(
        "Non-ASIM parsers (`parsers.csv` › `filter_fields`)",
        (
            (_link(r["parser_name"], "parsers"), r.get("filter_fields", ""))
            for r in parsers
        ),
    )
    lines += _section(
        "ASIM parsers (`asim_parsers.csv` › `filter_fields`)",
        (
            (_link(r["parser_name"], "asim"), r.get("filter_fields", ""))
            for r in asim_parsers
        ),
    )
    # Content items aren't linked (slug rules are inconsistent with the
    # generator's; render as plain code with the kind suffix).
    content_rows: list[tuple[str, str]] = []
    for r in content_items:
        kind = r.get("content_kind", "") or r.get("content_type", "") or ""
        label = f"{r['content_name']} [{kind}]" if kind else r["content_name"]
        content_rows.append((f"`{label}`", r.get("content_filter_fields", "")))
    lines += _section(
        "Content items (`content_items.csv` › `content_filter_fields`)",
        content_rows,
    )

    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output} ({args.output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
