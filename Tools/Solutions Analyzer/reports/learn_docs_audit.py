"""Audit report comparing Microsoft Learn `data-connectors-reference` against the analyzer's CSV outputs.

Produces three CSV findings (plus a Markdown summary). All comparisons are
scoped to **active connectors in published, non-deprecated solutions**:
  1. `connector_coverage_gaps.csv` — union of (a) active connectors missing
     from Learn and (b) Learn entries with no active analyzer connector.
     A `missing_from` column distinguishes the two directions.
  2. `connector_table_mismatches.csv` — connectors present in both, but
     with a mismatch in the table list.
  3. `connector_potential_matches.csv` — pairs of gap rows (one from each
     direction) that share most of their content tokens. These are typically
     V1/V2 splits, minor word differences (Audit vs Events), or renames —
     surfaced for human review without auto-matching.

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import quote

from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
ANALYZER_DIR = SCRIPT_DIR.parent
CACHE_DIR = ANALYZER_DIR / ".cache"
REPORT_DIR = SCRIPT_DIR / "learn_docs_audit"

# Published sentinelninja Solutions Docs base URL. Each analyzer connector
# has a per-connector page at `<base>/<connector_id-lowercased>.html`.
SENTINELNINJA_CONNECTORS_BASE = (
    "https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors"
)


def sentinelninja_connector_url(connector_id: str) -> str:
    """Return the published sentinelninja docs URL for an analyzer connector."""
    if not connector_id:
        return ""
    slug = quote(connector_id.lower(), safe="")
    return f"{SENTINELNINJA_CONNECTORS_BASE}/{slug}.html"

# Reuse the mapper's HTML fetch/cache so the page is downloaded at most once
# across the mapper and this audit. Keeps a single source of truth for cache
# layout and User-Agent string.
sys.path.insert(0, str(ANALYZER_DIR))
from map_solutions_connectors_tables import (  # noqa: E402
    LEARN_DOCS_URL as LEARN_URL,
    fetch_learn_docs_html,
)

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
# Bracketed marketing prefix on a title. Stripped on both sides so that an
# in-repo `[Recommended] X` matches a Learn `recommended-x` anchor and an
# in-repo `Y` matches a Learn `[Deprecated] Y` / `deprecated-y` anchor.
_RECOMMENDED_PREFIX_RE = re.compile(
    r"^\s*\[(?:recommended|preview|deprecated)\]\s*", re.IGNORECASE
)
_TRAILING_PREVIEW_RE = re.compile(r"\s*\(preview\)\s*$", re.IGNORECASE)
# Trailing parenthesised clause on a title (used to peel off, iteratively,
# `(Push)`, `(using Azure Functions)`, `(via Codeless Connector Framework)`,
# `(Preview)`, etc., so that titles with multiple bracketed suffixes still
# reach a bare base).
_PAREN_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")
_LEARN_ANCHOR_DROP_RE = re.compile(r"[&/().:,;'\"!?\[\]{}|*<>=+@#$%^`~\\]")
_LEARN_ANCHOR_KEEP_RE = re.compile(r"[^a-z0-9\-]")
_ANCHOR_PREFIX_RE = re.compile(r"^(?:recommended|preview|deprecated)-", re.IGNORECASE)
_DASH_RUN_RE = re.compile(r"-+")

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
    "standalone",
)
_QUAL_STRIP_RE = re.compile(
    r"-(?:" + "|".join(_QUAL_SUFFIXES) + r")(?=-|$)",
    re.IGNORECASE,
)
# Trailing `-v<digits>` on a slug — V1/V2 analyzer connectors collapse onto a
# single Learn anchor (Learn does not currently expose V-specific anchors).
_VERSION_SUFFIX_RE = re.compile(r"-v\d+(?=-|$)", re.IGNORECASE)

# Tokens that are used interchangeably across Learn and in-repo titles
# (e.g. Learn says "Admin Audit", repo says "Admin Events"). For every slug we
# register additional keys with each member of the group substituted in.
# Collision-checked against both Learn anchors and connectors.csv — see
# README v9.9 notes for FP analysis.
_SYNONYM_GROUPS: List[Tuple[str, ...]] = [
    ("audit", "activity", "events", "event", "activities"),
]
_SYNONYM_TOKEN_RE = re.compile(
    r"(?<![a-z0-9])(" + "|".join(t for g in _SYNONYM_GROUPS for t in g) + r")(?![a-z0-9])",
    re.IGNORECASE,
)
_TOKEN_TO_GROUP: Dict[str, Tuple[str, ...]] = {t: g for g in _SYNONYM_GROUPS for t in g}


def _synonym_variants(slug: str) -> List[str]:
    """Yield slug variants with each synonym token swapped for the others."""
    out: List[str] = []
    m = _SYNONYM_TOKEN_RE.search(slug)
    if not m:
        return out
    tok = m.group(1).lower()
    for alt in _TOKEN_TO_GROUP.get(tok, ()):
        if alt != tok:
            out.append(slug[:m.start(1)] + alt + slug[m.end(1):])
    return out


def _no_separator(slug: str) -> str:
    """Slug with all hyphens removed — used for spacing-insensitive comparison
    (e.g. Learn `dynamics365` vs analyzer `dynamics-365`, or Learn
    `auth0-logsvia-codeless-...` vs analyzer `auth0-logs-via-codeless-...`)."""
    return slug.replace("-", "")

# ---- Explicit Learn-anchor ↔ analyzer-connector_id aliases ----
# Some Learn entries carry marketing titles that are too different from the
# in-repo connector title for normalisation to bridge. Pin them here
# (keyed by Learn anchor slug) so they don't surface as false-positive gaps.
# The right-hand side is the analyzer `connector_id` (stable id). The audit
# treats the Learn anchor as covered when the target connector_id is found:
# active connectors count toward `covered`, deprecated ones toward
# `suppressed-deprecated`.
LEARN_ANCHOR_ALIASES: Dict[str, str] = {
    # Marketing rename in Learn vs. in-repo title.
    "a365-observability": "A365",                          # Agent 365
    # Learn renames the deprecated Auth0 Function connector from "Logs" to
    # "Access Management"; both write to `Auth0AM_CL`.
    "auth0-access-management-using-azure-functions": "Auth0",
    # Learn uses a marketing tagline; repo uses "Onapsis Defend Integration".
    "onapsis-defend-integrate-unmatched-sap-threat-detection--intel-with-microsoft-sentinel": "Onapsis",
    # Deprecated counterpart that the qualifier-strip can't bridge
    # (repo "Box Events" vs. Learn "Box").
    "box-using-azure-functions": "BoxDataConnector",
}


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
    """Strip trailing qualifier suffixes and `-v\\d+` repeatedly."""
    prev = None
    cur = slug
    while prev != cur:
        prev = cur
        cur = _QUAL_STRIP_RE.sub("", cur).rstrip("-")
        cur = _VERSION_SUFFIX_RE.sub("", cur).rstrip("-")
    return cur


def title_slug_variants(title: str) -> List[str]:
    """All slug variants the mapper considers for a connector title."""
    out: List[str] = []
    def add(s: str) -> None:
        if s and s not in out:
            out.append(s)

    def add_for(text: str) -> None:
        if not text:
            return
        prim = slugify(text)
        add(prim)
        add(slugify_learn_anchor(text))
        if prim:
            add(_no_separator(prim))
            for syn in _synonym_variants(prim):
                add(syn)
                add(_no_separator(syn))
            base = _strip_qualifiers(prim)
            if base and base != prim:
                for suf in _QUAL_SUFFIXES:
                    add(f"{base}-{suf}")
                add(base)
                add(_no_separator(base))
                for syn in _synonym_variants(base):
                    add(syn)
                    add(_no_separator(syn))
            else:
                for suf in _QUAL_SUFFIXES:
                    add(f"{prim}-{suf}")

    add_for(title)
    stripped = _RECOMMENDED_PREFIX_RE.sub("", title)
    if stripped != title:
        add_for(stripped)
    # Iteratively peel trailing `(…)` clauses (handles multi-suffix titles).
    cur = stripped
    while True:
        new = _PAREN_SUFFIX_RE.sub("", cur).rstrip()
        if new == cur or not new:
            break
        add_for(new)
        cur = new
    return out


def build_learn_lookup(learn: Dict[str, Dict]) -> Dict[str, str]:
    """Return `{normalised_slug: original_anchor}` over all Learn anchors.

    Adds extra keys absorbing common diffs vs in-repo titles:
      * the raw anchor;
      * dash-collapsed anchor (e.g. `mimecast-audit--authentication-…`
        → `mimecast-audit-authentication-…`);
      * anchor with leading `recommended-`/`preview-`/`deprecated-` stripped;
      * anchor with a hyphen inserted at letter↔digit boundaries
        (`dynamics365` → `dynamics-365`);
      * anchor with a hyphen inserted before a glued method keyword
        (`auth0-logsvia-…` → `auth0-logs-via-…`);
      * slugs derived from the Learn *title* with marketing tails removed
        (split at the first `:` for `Onapsis Defend: …`, or at ` & ` for
        `Mimecast Audit & Authentication …`);
      * all combinations of the above.
    Earlier (raw) keys win over later normalisations.
    """
    lookup: Dict[str, str] = {}
    def _add(key: str, anchor: str) -> None:
        if key and key not in lookup:
            lookup[key] = anchor

    def _add_normalised(slug: str, anchor: str) -> None:
        if not slug:
            return
        _add(slug, anchor)
        _add(_DASH_RUN_RE.sub("-", slug).strip("-"), anchor)
        _add(_no_separator(slug), anchor)
        no_pref = _ANCHOR_PREFIX_RE.sub("", slug)
        _add(no_pref, anchor)
        _add(_DASH_RUN_RE.sub("-", no_pref).strip("-"), anchor)
        _add(_no_separator(no_pref), anchor)
        for syn in _synonym_variants(slug):
            _add(syn, anchor)
            _add(_no_separator(syn), anchor)

    for slug, meta in learn.items():
        _add_normalised(slug, slug)
        # Title-truncation variants: split at the first `:` (marketing
        # taglines) and at ` & ` (compound titles), and register slugs of
        # the prefix. We do this from the title rather than the anchor so
        # that punctuation that was lost during slugification is recovered.
        title = (meta or {}).get("title", "") or ""
        for sep in (":", " & "):
            if sep in title:
                head = title.split(sep, 1)[0].strip()
                if head:
                    _add_normalised(slugify(head), slug)
                    _add_normalised(slugify_learn_anchor(head), slug)
    return lookup


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset({
    "a", "an", "and", "the", "for", "of", "to", "with", "via", "using",
    "data", "connector", "connectors", "logs", "log", "sentinel",
    "microsoft", "azure", "function", "functions", "push", "polling",
    "ccf", "ccp", "ama", "codeless", "framework", "legacy", "agent",
    "preview", "recommended", "deprecated", "v1", "v2", "v3",
})


def _core_tokens(title: str) -> Set[str]:
    return {t for t in _TOKEN_RE.findall(title.lower()) if t not in _STOPWORDS}


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


def load_solution_publish_dates(solutions_csv: Path) -> Dict[str, str]:
    """{solution_name: solution_last_publish_date} (Marketplace date).

    Connectors don't have their own Marketplace publish date — they inherit it
    from the solution they ship in. We surface the last-publish date so the
    audit can show "how fresh is this connector".
    """
    out: Dict[str, str] = {}
    for row in load_csv(solutions_csv):
        name = row.get("solution_name", "")
        if not name:
            continue
        out[name] = (row.get("solution_last_publish_date", "")
                     or row.get("mp_last_modified_date", "")
                     or row.get("solution_first_publish_date", "")
                     or row.get("mp_creation_date", ""))
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


def load_deprecated_connectors(connectors_csv: Path) -> List[Dict]:
    """Deprecated connectors (any solution). Used solely to suppress Learn
    entries from the "missing from analyzer" bucket when the only analyzer
    counterpart is a deprecated connector — those Learn entries are typically
    `[Deprecated] …` / `deprecated-…` anchors and are correctly covered, just
    not by an *active* connector.
    """
    return [r for r in load_csv(connectors_csv)
            if r.get("is_deprecated", "").lower() == "true"]


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
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("Loading Learn page …")
    html = fetch_learn_docs_html(CACHE_DIR, force_refresh=args.refresh)
    if not html:
        print("  ERROR: could not fetch Learn page (no cache and no network).")
        sys.exit(1)
    learn = parse_learn_sections(html)
    print(f"  {len(learn)} connector sections parsed from Learn")
    learn_lookup = build_learn_lookup(learn)

    print("Loading analyzer CSVs …")
    published = load_published_solutions(ANALYZER_DIR / "solutions.csv")
    print(f"  {len(published)} published, non-deprecated solutions")
    publish_dates = load_solution_publish_dates(ANALYZER_DIR / "solutions.csv")
    connectors = load_analyzer_connectors(ANALYZER_DIR / "connectors.csv", published)
    print(f"  {len(connectors)} active connectors in published solutions")
    deprecated_connectors = load_deprecated_connectors(ANALYZER_DIR / "connectors.csv")
    print(f"  {len(deprecated_connectors)} deprecated connectors (for suppression only)")
    conn_tables = load_connector_tables(
        ANALYZER_DIR / "solutions_connectors_tables_mapping_simplified.csv")

    # ---- 1. Connectors in analyzer but missing from Learn ----
    # Pre-resolve the explicit aliases so we know which connector_ids are
    # already covered (and which deprecated ones should suppress a Learn entry).
    active_by_id = {c.get("connector_id", ""): c for c in connectors}
    deprecated_by_id = {c.get("connector_id", ""): c for c in deprecated_connectors}
    alias_active_anchor_by_cid: Dict[str, str] = {
        cid: anchor for anchor, cid in LEARN_ANCHOR_ALIASES.items()
        if cid in active_by_id and anchor in learn
    }
    alias_deprecated_anchor_by_cid: Dict[str, str] = {
        cid: anchor for anchor, cid in LEARN_ANCHOR_ALIASES.items()
        if cid in deprecated_by_id and cid not in active_by_id and anchor in learn
    }

    missing_from_learn = []
    learn_used_slugs: Set[str] = set()
    for c in connectors:
        title = c.get("connector_title", "")
        cid = c.get("connector_id", "")
        variants = title_slug_variants(title)
        match = next((learn_lookup[v] for v in variants if v in learn_lookup), "")
        if not match and cid in alias_active_anchor_by_cid:
            match = alias_active_anchor_by_cid[cid]
        if match:
            learn_used_slugs.add(match)
        else:
            missing_from_learn.append({
                "connector_id": c.get("connector_id", ""),
                "connector_title": title,
                "solution_name": c.get("solution_name", ""),
                "solution_publish_date": publish_dates.get(c.get("solution_name", ""), ""),
                "collection_method": c.get("collection_method", ""),
                "tried_slugs": " | ".join(variants),
                "sentinelninja_url": sentinelninja_connector_url(
                    c.get("connector_id", "")),
            })

    # ---- 2. Connectors in Learn but missing from analyzer (active-published only) ----
    # Build the slug set from active published connectors only, so "missing
    # from analyzer" means "no active connector in any published, non-deprecated
    # solution covers this Learn entry". Use the same normalised lookup
    # semantics: a Learn anchor is covered if *any* variant of *any* active
    # connector resolves to that anchor via `learn_lookup`.
    covered_learn_anchors: Set[str] = set()
    for c in connectors:
        for v in title_slug_variants(c.get("connector_title", "")):
            anchor = learn_lookup.get(v)
            if anchor:
                covered_learn_anchors.add(anchor)
    # Anchors covered by an explicit alias to an active connector.
    covered_learn_anchors.update(alias_active_anchor_by_cid.values())
    missing_from_analyzer = []
    suppressed_deprecated = 0
    # Learn anchors covered only by a *deprecated* analyzer connector — those
    # are typically the `[Deprecated] …` / `deprecated-…` Learn entries and
    # are correctly covered, just not by anything active. Suppress them from
    # the gap report and just count them.
    deprecated_covered_anchors: Set[str] = set()
    for c in deprecated_connectors:
        for v in title_slug_variants(c.get("connector_title", "")):
            anchor = learn_lookup.get(v)
            if anchor:
                deprecated_covered_anchors.add(anchor)
    # Also treat the qualifier-stripped form of each deprecated-covered
    # anchor as covered, so Learn anchors that carry an extra qualifier
    # suffix (e.g. `cloudflare-preview-using-azure-functions` vs. the
    # in-repo bare `cloudflare`) get suppressed too. We compute the base
    # set from the deprecated connectors' slug variants directly (not just
    # from anchors that already match), so deprecated connectors with no
    # current Learn anchor still contribute their base.
    deprecated_covered_bases: Set[str] = set()
    for c in deprecated_connectors:
        for v in title_slug_variants(c.get("connector_title", "")):
            base = _strip_qualifiers(v)
            if base:
                deprecated_covered_bases.add(base)
    # Anchors covered by an explicit alias to a deprecated connector.
    deprecated_covered_anchors.update(alias_deprecated_anchor_by_cid.values())
    for slug, meta in learn.items():
        if slug in covered_learn_anchors:
            continue
        if slug in deprecated_covered_anchors:
            suppressed_deprecated += 1
            continue
        if _strip_qualifiers(slug) in deprecated_covered_bases:
            suppressed_deprecated += 1
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
        cid = c.get("connector_id", "")
        variants = title_slug_variants(title)
        match = next((learn_lookup[v] for v in variants if v in learn_lookup), "")
        if not match and cid in alias_active_anchor_by_cid:
            match = alias_active_anchor_by_cid[cid]
        if not match:
            continue
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

    # ---- Build combined coverage-gap rows ----
    coverage_gaps: List[Dict] = []
    for r in missing_from_learn:
        coverage_gaps.append({
            "missing_from": "learn",
            "connector_title": r["connector_title"],
            "connector_id": r["connector_id"],
            "solution_name": r["solution_name"],
            "solution_publish_date": r["solution_publish_date"],
            "collection_method": r["collection_method"],
            "learn_slug": "",
            "learn_url": "",
            "learn_table_count": "",
            "learn_tables": "",
            "tried_slugs": r["tried_slugs"],
            "sentinelninja_url": r["sentinelninja_url"],
        })
    for r in missing_from_analyzer:
        coverage_gaps.append({
            "missing_from": "analyzer",
            "connector_title": r["learn_title"],
            "connector_id": "",
            "solution_name": "",
            "solution_publish_date": "",
            "collection_method": "",
            "learn_slug": r["learn_slug"],
            "learn_url": r["learn_url"],
            "learn_table_count": r["learn_table_count"],
            "learn_tables": r["learn_tables"],
            "tried_slugs": "",
            "sentinelninja_url": "",
        })

    # ---- Write CSVs ----
    def write_csv(name: str, rows: List[Dict], fieldnames: List[str]) -> Path:
        # Stamp every row with the generation timestamp so each CSV is
        # self-describing without needing a sidecar file.
        fieldnames = [*fieldnames, "generated_at"]
        p = REPORT_DIR / name
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                r["generated_at"] = generated_at
                w.writerow(r)
        return p

    # Remove the old split CSVs if present (the audit now publishes one
    # combined coverage-gap file).
    for stale in ("connectors_missing_from_learn.csv",
                  "connectors_missing_from_analyzer.csv"):
        stale_p = REPORT_DIR / stale
        if stale_p.exists():
            stale_p.unlink()

    p1 = write_csv(
        "connector_coverage_gaps.csv",
        sorted(coverage_gaps,
               key=lambda r: (r["missing_from"], r["connector_title"].lower())),
        ["missing_from", "connector_title", "connector_id", "solution_name",
         "solution_publish_date", "collection_method",
         "learn_slug", "learn_url",
         "learn_table_count", "learn_tables", "tried_slugs",
         "sentinelninja_url"],
    )
    p2 = write_csv("connector_table_mismatches.csv",
                   sorted(table_mismatches, key=lambda r: r["connector_title"].lower()),
                   ["connector_id", "connector_title", "solution_name", "learn_slug",
                    "analyzer_table_count", "learn_table_count",
                    "only_in_analyzer", "only_in_learn"])

    # ---- 4. Potential matches between the two gap directions ----
    # For each (analyzer-side missing, Learn-side missing) pair, compute a
    # Jaccard similarity over their content tokens (after stripping common
    # stopwords like `using`, `via`, `function`, `v1`, `v2`, etc.). Pairs
    # with similarity >= 0.5 are surfaced for human review — these are
    # typically V1/V2 splits, `Audit` vs `Events`, `Activity` vs `Activities`,
    # or other one-word differences that should not be auto-matched.
    potential_matches: List[Dict] = []
    THRESHOLD = 0.5
    for a in missing_from_learn:
        a_tokens = _core_tokens(a["connector_title"])
        if not a_tokens:
            continue
        for l in missing_from_analyzer:
            l_tokens = _core_tokens(l["learn_title"])
            if not l_tokens:
                continue
            inter = a_tokens & l_tokens
            if not inter:
                continue
            union = a_tokens | l_tokens
            sim = len(inter) / len(union)
            if sim < THRESHOLD:
                continue
            potential_matches.append({
                "similarity": f"{sim:.2f}",
                "analyzer_title": a["connector_title"],
                "analyzer_connector_id": a["connector_id"],
                "analyzer_solution": a["solution_name"],
                "learn_title": l["learn_title"],
                "learn_slug": l["learn_slug"],
                "learn_url": f"{LEARN_URL}#{l['learn_slug']}",
                "shared_tokens": ", ".join(sorted(inter)),
                "only_in_analyzer": ", ".join(sorted(a_tokens - l_tokens)) or "—",
                "only_in_learn": ", ".join(sorted(l_tokens - a_tokens)) or "—",
            })
    potential_matches.sort(key=lambda r: (-float(r["similarity"]),
                                          r["analyzer_title"].lower()))
    p3 = write_csv(
        "connector_potential_matches.csv",
        potential_matches,
        ["similarity", "analyzer_title", "analyzer_connector_id",
         "analyzer_solution", "learn_title", "learn_slug", "learn_url",
         "shared_tokens", "only_in_analyzer", "only_in_learn"],
    )

    # ---- Markdown summary ----
    summary = REPORT_DIR / "README.md"
    with summary.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Learn data-connectors-reference audit\n\n")
        f.write(f"Generated **{generated_at}** against `{LEARN_URL}`\n\n")
        f.write(f"- Learn sections parsed: **{len(learn)}**\n")
        f.write(f"- Published, non-deprecated solutions: **{len(published)}**\n")
        f.write(f"- Active connectors in those solutions: **{len(connectors)}**\n\n")
        f.write("## 1. Connector coverage gaps\n\n")
        f.write(
            f"**{len(coverage_gaps)}** total gaps — "
            f"**{len(missing_from_learn)}** active connectors not on Learn, "
            f"**{len(missing_from_analyzer)}** Learn entries not covered by any active connector "
            f"(an additional **{suppressed_deprecated}** Learn entries are covered only by a deprecated connector and are suppressed). "
            f"See [`connector_coverage_gaps.csv`](connector_coverage_gaps.csv).\n\n"
        )
        if missing_from_learn:
            f.write("### 1a. Active connectors missing from Learn\n\n")
            f.write("| Title | Solution | Published | Collection method | Docs |\n|---|---|---|---|---|\n")
            for r in sorted(missing_from_learn, key=lambda r: r["connector_title"].lower()):
                docs = f"[link]({r['sentinelninja_url']})" if r['sentinelninja_url'] else "—"
                pub = (r['solution_publish_date'] or "—")[:10]
                f.write(f"| {r['connector_title']} | {r['solution_name']} | {pub} | {r['collection_method']} | {docs} |\n")
            f.write("\n")
        if missing_from_analyzer:
            f.write("### 1b. Learn entries with no active analyzer connector\n\n")
            f.write("| Learn title | Tables | URL |\n|---|---|---|\n")
            for r in sorted(missing_from_analyzer, key=lambda r: r["learn_title"].lower()):
                f.write(f"| {r['learn_title']} | {r['learn_table_count']} | [link]({r['learn_url']}) |\n")
        f.write("\n## 2. Table-list mismatches\n\n")
        f.write(f"**{len(table_mismatches)}** connectors match by title but have a different set of Log Analytics tables. "
                f"See [`connector_table_mismatches.csv`](connector_table_mismatches.csv).\n\n")
        if table_mismatches:
            f.write("| Title | Solution | Only in analyzer | Only on Learn |\n|---|---|---|---|\n")
            for r in sorted(table_mismatches, key=lambda r: r["connector_title"].lower()):
                a = r["only_in_analyzer"] or "—"
                b = r["only_in_learn"] or "—"
                f.write(f"| {r['connector_title']} | {r['solution_name']} | {a} | {b} |\n")
        f.write("\n## 3. Potential matches (for manual review)\n\n")
        f.write(
            f"**{len(potential_matches)}** pair(s) of gap rows share ≥ 50% of "
            f"their content tokens after stripping stopwords. These are likely "
            f"V1/V2 splits, minor word differences (`Audit` vs `Events`), or "
            f"renames — surfaced here so they can be confirmed or dismissed "
            f"without auto-matching. See [`connector_potential_matches.csv`](connector_potential_matches.csv).\n\n"
        )
        if potential_matches:
            f.write("| Sim | Analyzer title | Learn title | Only in analyzer | Only on Learn |\n|---|---|---|---|---|\n")
            for r in potential_matches:
                f.write(
                    f"| {r['similarity']} | {r['analyzer_title']} | "
                    f"[{r['learn_title']}]({r['learn_url']}) | "
                    f"{r['only_in_analyzer']} | {r['only_in_learn']} |\n"
                )

    print()
    print(f"  1. Connector coverage gaps:                 {len(coverage_gaps):4d}  → {p1.relative_to(ANALYZER_DIR)}")
    print(f"       (missing from Learn: {len(missing_from_learn)}, missing from analyzer: {len(missing_from_analyzer)}, suppressed-deprecated: {suppressed_deprecated})")
    print(f"  2. Table-list mismatches:                   {len(table_mismatches):4d}  → {p2.relative_to(ANALYZER_DIR)}")
    print(f"  3. Potential matches (manual review):       {len(potential_matches):4d}  → {p3.relative_to(ANALYZER_DIR)}")
    print(f"  Summary: {summary.relative_to(ANALYZER_DIR)}")


if __name__ == "__main__":
    main()
