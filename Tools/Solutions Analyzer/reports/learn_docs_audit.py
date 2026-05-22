"""Audit report comparing Microsoft Learn `data-connectors-reference` against the analyzer's CSV outputs.

Produces three findings (CSV + a Markdown summary):
  1. Connectors **in published+Active solutions** that are missing from Learn.
  2. Connectors documented on Learn but missing from the analyzer.
  3. Connectors present in both, but with a mismatch in the table list.

The Learn HTML is cached at `.cache/data_connectors_reference.html`
(separate from the anchor-only cache the mapper maintains).  Pass
`--refresh` to force a re-fetch.

Usage:
    python reports/learn_docs_audit.py [--refresh]

Outputs are written to `reports/learn_docs_audit/`.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
ANALYZER_DIR = SCRIPT_DIR.parent
CACHE_DIR = ANALYZER_DIR / ".cache"
REPORT_DIR = SCRIPT_DIR / "learn_docs_audit"

# Reuse the mapper's HTML fetch/cache so the page is downloaded at most once
# across the mapper and this audit. Keeps a single source of truth for cache
# layout and User-Agent string.
sys.path.insert(0, str(ANALYZER_DIR))
from map_solutions_connectors_tables import (  # noqa: E402
    LEARN_DOCS_URL as LEARN_URL,
    fetch_learn_docs_html,
)

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_RECOMMENDED_PREFIX_RE = re.compile(r"^\s*\[(?:recommended|preview)\]\s*", re.IGNORECASE)
_TRAILING_PREVIEW_RE = re.compile(r"\s*\(preview\)\s*$", re.IGNORECASE)
_LEARN_ANCHOR_DROP_RE = re.compile(r"[&/().:,;'\"!?\[\]{}|*<>=+@#$%^`~\\]")
_LEARN_ANCHOR_KEEP_RE = re.compile(r"[^a-z0-9\-]")

# Trailing qualifier suffixes mirrored from the mapper. Keep in sync with
# `_LEARN_QUALIFIER_SUFFIXES` in map_solutions_connectors_tables.py.
_QUAL_SUFFIXES = (
    "using-azure-functions",
    "using-azure-function",
    "via-codeless-connector-framework",
    "via-legacy-agent",
    "polling-ccf",
    "polling-ccp",
    "via-ama",
    "ccf",
    "ccp",
    "preview",
)
_QUAL_STRIP_RE = re.compile(
    r"-(?:" + "|".join(_QUAL_SUFFIXES) + r")(?=-|$)",
    re.IGNORECASE,
)


def slugify(text: str) -> str:
    return _NON_ALNUM_RE.sub("-", text.lower()).strip("-")


def slugify_learn_anchor(text: str) -> str:
    if not text:
        return ""
    s = text.lower()
    s = _LEARN_ANCHOR_DROP_RE.sub("", s)
    s = "".join("-" if c.isspace() else c for c in s)
    s = _LEARN_ANCHOR_KEEP_RE.sub("", s)
    return s.strip("-")


def _strip_qualifiers(slug: str) -> str:
    prev = None
    cur = slug
    while prev != cur:
        prev = cur
        cur = _QUAL_STRIP_RE.sub("", cur).rstrip("-")
    return cur


def title_slug_variants(title: str) -> List[str]:
    """All slug variants the mapper considers for a connector title."""
    out: List[str] = []
    def add(s: str) -> None:
        if s and s not in out:
            out.append(s)

    primary = slugify(title)
    add(primary)
    add(slugify_learn_anchor(title))
    stripped = _RECOMMENDED_PREFIX_RE.sub("", title)
    if stripped != title:
        add(slugify(stripped))
        add(slugify_learn_anchor(stripped))
    no_preview = _TRAILING_PREVIEW_RE.sub("", title)
    if no_preview != title:
        add(slugify(no_preview))
        add(slugify_learn_anchor(no_preview))
    if primary:
        base = _strip_qualifiers(primary)
        if base and base != primary:
            for suf in _QUAL_SUFFIXES:
                add(f"{base}-{suf}")
            add(base)
        else:
            for suf in _QUAL_SUFFIXES:
                add(f"{primary}-{suf}")
    return out


# ---------- Learn page ----------


def parse_learn_sections(html: str) -> Dict[str, Dict]:
    """Return {slug: {title, tables: [str]}} keyed by anchor slug."""
    soup = BeautifulSoup(html, "html.parser")
    # Anchor name pattern: lowercase alnum + hyphens, but exclude page-level
    # anchors like 'ms--in-this-article'.  We accept anything the mapper accepts.
    anchor_re = re.compile(r"^[a-z0-9][a-z0-9-]*$")
    out: Dict[str, Dict] = {}
    for a in soup.find_all("a", attrs={"name": True}):
        slug = a.get("name") or ""
        if not anchor_re.match(slug):
            continue
        # Find the enclosing <details> by walking next siblings of the
        # anchor's parent <p>.
        parent_p = a.parent if a.parent and a.parent.name == "p" else a
        details = parent_p.find_next_sibling("details") if parent_p else None
        if details is None:
            # Fallback: search forward in the document.
            details = a.find_next("details")
            if details is None:
                continue
        # Title comes from <summary><strong>…</strong></summary>
        summary = details.find("summary")
        title = ""
        if summary:
            strong = summary.find("strong")
            title = (strong.get_text(strip=True) if strong else summary.get_text(strip=True))
        # Tables: first <table> following the "Log Analytics table(s):" header
        tables: List[str] = []
        for table in details.find_all("table"):
            # The expected header has a <th>Table</th> as the first column
            ths = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if not ths or ths[0] != "table":
                continue
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if not tds:
                    continue
                code = tds[0].find("code")
                name = (code.get_text(strip=True) if code else tds[0].get_text(strip=True))
                if name:
                    tables.append(name)
            break  # only the first matching table per connector
        out[slug] = {"title": title, "tables": tables}
    return out


# ---------- Analyzer CSVs ----------

def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_published_solutions(solutions_csv: Path) -> Set[str]:
    """Solutions that are published on Marketplace and not deprecated."""
    out: Set[str] = set()
    for row in load_csv(solutions_csv):
        if (row.get("is_published", "").lower() == "true"
                and row.get("is_deprecated", "").lower() != "true"):
            out.add(row.get("solution_name", ""))
    return out


def load_analyzer_connectors(connectors_csv: Path,
                             published_solutions: Set[str]) -> List[Dict]:
    """Active connectors that belong to published solutions."""
    out = []
    for row in load_csv(connectors_csv):
        if row.get("is_deprecated", "").lower() == "true":
            continue
        if row.get("solution_name") not in published_solutions:
            continue
        out.append(row)
    return out


def load_connector_tables(mapping_csv: Path) -> Dict[str, Set[str]]:
    """{connector_id: {table_name, ...}} across all solutions."""
    out: Dict[str, Set[str]] = defaultdict(set)
    for row in load_csv(mapping_csv):
        cid = row.get("connector_id", "")
        tbl = row.get("table_name", "")
        if cid and tbl:
            out[cid].add(tbl)
    return out


# ---------- Report ----------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true",
                    help="Force re-fetch of the Learn page.")
    args = ap.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading Learn page …")
    html = fetch_learn_docs_html(CACHE_DIR, force_refresh=args.refresh)
    if not html:
        print("  ERROR: could not fetch Learn page (no cache and no network).")
        sys.exit(1)
    learn = parse_learn_sections(html)
    print(f"  {len(learn)} connector sections parsed from Learn")

    print("Loading analyzer CSVs …")
    published = load_published_solutions(ANALYZER_DIR / "solutions.csv")
    print(f"  {len(published)} published, non-deprecated solutions")
    connectors = load_analyzer_connectors(ANALYZER_DIR / "connectors.csv", published)
    print(f"  {len(connectors)} active connectors in published solutions")
    conn_tables = load_connector_tables(
        ANALYZER_DIR / "solutions_connectors_tables_mapping_simplified.csv")

    # ---- 1. Connectors in analyzer but missing from Learn ----
    missing_from_learn = []
    learn_used_slugs: Set[str] = set()
    for c in connectors:
        title = c.get("connector_title", "")
        variants = title_slug_variants(title)
        match = next((v for v in variants if v in learn), "")
        if match:
            learn_used_slugs.add(match)
        else:
            missing_from_learn.append({
                "connector_id": c.get("connector_id", ""),
                "connector_title": title,
                "solution_name": c.get("solution_name", ""),
                "collection_method": c.get("collection_method", ""),
                "tried_slugs": " | ".join(variants),
            })

    # ---- 2. Connectors in Learn but missing from analyzer (titles only) ----
    # Match any analyzer connector (regardless of solution/active) by any
    # known title variant, so "missing" really means "no analyzer hit at all".
    all_analyzer_slugs: Set[str] = set()
    for c in load_csv(ANALYZER_DIR / "connectors.csv"):
        for v in title_slug_variants(c.get("connector_title", "")):
            all_analyzer_slugs.add(v)
    missing_from_analyzer = []
    for slug, meta in learn.items():
        if slug in all_analyzer_slugs:
            continue
        missing_from_analyzer.append({
            "learn_slug": slug,
            "learn_title": meta["title"],
            "learn_table_count": len(meta["tables"]),
            "learn_tables": ", ".join(meta["tables"]),
            "learn_url": f"{LEARN_URL}#{slug}",
        })

    # ---- 3. Table-list mismatches for connectors present in both ----
    table_mismatches = []
    for c in connectors:
        title = c.get("connector_title", "")
        variants = title_slug_variants(title)
        match = next((v for v in variants if v in learn), "")
        if not match:
            continue
        cid = c.get("connector_id", "")
        analyzer_tables = conn_tables.get(cid, set())
        learn_tables = set(learn[match]["tables"])
        if analyzer_tables == learn_tables:
            continue
        only_in_analyzer = sorted(analyzer_tables - learn_tables)
        only_in_learn = sorted(learn_tables - analyzer_tables)
        if not only_in_analyzer and not only_in_learn:
            continue
        table_mismatches.append({
            "connector_id": cid,
            "connector_title": title,
            "solution_name": c.get("solution_name", ""),
            "learn_slug": match,
            "only_in_analyzer": ", ".join(only_in_analyzer),
            "only_in_learn": ", ".join(only_in_learn),
            "analyzer_table_count": len(analyzer_tables),
            "learn_table_count": len(learn_tables),
        })

    # ---- Write CSVs ----
    def write_csv(name: str, rows: List[Dict], fieldnames: List[str]) -> Path:
        p = REPORT_DIR / name
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        return p

    p1 = write_csv("connectors_missing_from_learn.csv",
                   sorted(missing_from_learn, key=lambda r: r["connector_title"].lower()),
                   ["connector_id", "connector_title", "solution_name",
                    "collection_method", "tried_slugs"])
    p2 = write_csv("connectors_missing_from_analyzer.csv",
                   sorted(missing_from_analyzer, key=lambda r: r["learn_title"].lower()),
                   ["learn_slug", "learn_title", "learn_table_count",
                    "learn_tables", "learn_url"])
    p3 = write_csv("connector_table_mismatches.csv",
                   sorted(table_mismatches, key=lambda r: r["connector_title"].lower()),
                   ["connector_id", "connector_title", "solution_name", "learn_slug",
                    "analyzer_table_count", "learn_table_count",
                    "only_in_analyzer", "only_in_learn"])

    # ---- Markdown summary ----
    summary = REPORT_DIR / "README.md"
    with summary.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Learn data-connectors-reference audit\n\n")
        f.write(f"Generated against `{LEARN_URL}`\n\n")
        f.write(f"- Learn sections parsed: **{len(learn)}**\n")
        f.write(f"- Published, non-deprecated solutions: **{len(published)}**\n")
        f.write(f"- Active connectors in those solutions: **{len(connectors)}**\n\n")
        f.write("## 1. Active connectors missing from Learn\n\n")
        f.write(f"**{len(missing_from_learn)}** active connectors in published solutions are not on Learn. "
                f"See [`connectors_missing_from_learn.csv`](connectors_missing_from_learn.csv).\n\n")
        if missing_from_learn:
            top = missing_from_learn[:20]
            f.write("| Title | Solution | Collection method |\n|---|---|---|\n")
            for r in sorted(top, key=lambda r: r["connector_title"].lower()):
                f.write(f"| {r['connector_title']} | {r['solution_name']} | {r['collection_method']} |\n")
            if len(missing_from_learn) > 20:
                f.write(f"\n_…and {len(missing_from_learn) - 20} more. Full list in the CSV._\n")
        f.write("\n## 2. Learn entries with no analyzer match\n\n")
        f.write(f"**{len(missing_from_analyzer)}** Learn sections have no matching connector in the analyzer. "
                f"See [`connectors_missing_from_analyzer.csv`](connectors_missing_from_analyzer.csv).\n\n")
        if missing_from_analyzer:
            top = missing_from_analyzer[:20]
            f.write("| Learn title | Tables | URL |\n|---|---|---|\n")
            for r in sorted(top, key=lambda r: r["learn_title"].lower()):
                f.write(f"| {r['learn_title']} | {r['learn_table_count']} | [link]({r['learn_url']}) |\n")
            if len(missing_from_analyzer) > 20:
                f.write(f"\n_…and {len(missing_from_analyzer) - 20} more. Full list in the CSV._\n")
        f.write("\n## 3. Table-list mismatches\n\n")
        f.write(f"**{len(table_mismatches)}** connectors match by title but have a different set of Log Analytics tables. "
                f"See [`connector_table_mismatches.csv`](connector_table_mismatches.csv).\n\n")
        if table_mismatches:
            top = table_mismatches[:20]
            f.write("| Title | Only in analyzer | Only on Learn |\n|---|---|---|\n")
            for r in sorted(top, key=lambda r: r["connector_title"].lower()):
                a = r["only_in_analyzer"] or "—"
                b = r["only_in_learn"] or "—"
                f.write(f"| {r['connector_title']} | {a} | {b} |\n")
            if len(table_mismatches) > 20:
                f.write(f"\n_…and {len(table_mismatches) - 20} more. Full list in the CSV._\n")

    print()
    print(f"  1. Active connectors missing from Learn:    {len(missing_from_learn):4d}  → {p1.relative_to(ANALYZER_DIR)}")
    print(f"  2. Learn entries missing from analyzer:     {len(missing_from_analyzer):4d}  → {p2.relative_to(ANALYZER_DIR)}")
    print(f"  3. Table-list mismatches:                   {len(table_mismatches):4d}  → {p3.relative_to(ANALYZER_DIR)}")
    print(f"  Summary: {summary.relative_to(ANALYZER_DIR)}")


if __name__ == "__main__":
    main()
