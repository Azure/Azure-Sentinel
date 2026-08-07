#!/usr/bin/env python3
"""Historical connector counter for the Azure-Sentinel repository.

Reconstructs, from git history, the number of data connectors that are
**part of a solution** and **not deprecated**, sampled on the 1st of each
month. Output is a CSV time-series written next to the other Solutions
Analyzer CSVs.

Definitions (mirroring map_solutions_connectors_tables.py at the time of
writing):

* "Part of a solution": a connector object defined under
  ``Solutions/<Solution>/Data Connectors/**/*.json`` (also the
  ``DataConnectors`` / ``Data Connector`` folder spellings), or a
  ``dataConnectorDefinitions`` resource inside a solution
  ``mainTemplate.json``.
* A connector object is a JSON dict carrying string ``id``, ``publisher`` and
  ``title`` keys (``title`` must be a literal, not an ARM ``[variables(...)]``
  reference). When ``id`` is an ARM variable reference it is regenerated from
  the title (spaces and dashes stripped), matching the mapper.
* "Deprecated" — a connector is excluded when ANY of:
    - its title contains ``[DEPRECATED]`` (case-insensitive) or starts with
      ``[Deprecated]``;
    - its ``availability.status`` is explicitly ``0``;
    - the owning solution is deprecated (the solution's ``Description`` text
      matches the mapper's solution-deprecation patterns).
* Counting unit: distinct connector IDs. A connector ID counts as active if it
  is active in at least one (connector, solution) occurrence.

The reconstruction reads blobs straight out of git (``ls-tree`` +
``cat-file --batch``) without touching the working tree, so it is safe to run
on any branch.

Usage::

    python connector_history.py                 # full history, monthly
    python connector_history.py --start 2023-01 --end 2024-01
    python connector_history.py --ref master --output connector_history.csv
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# --------------------------------------------------------------------------- #
# Deprecation detection (copied from map_solutions_connectors_tables.py so the
# historical tool stays stable even if the mapper evolves).
# --------------------------------------------------------------------------- #
SOLUTION_DEPRECATED_PATTERNS = [
    re.compile(r'this (?:integration|solution) is (?:considered )?deprecated', re.IGNORECASE),
    re.compile(r'this (?:integration|solution) has been deprecated', re.IGNORECASE),
]

# Folder spellings the mapper recognises for connector definitions.
_DC_FOLDERS = ("Data Connectors", "DataConnectors", "Data Connector")

# Path matchers (POSIX separators, as git emits).
_RE_CONNECTOR_FILE = re.compile(
    r'^Solutions/(?P<sol>[^/]+)/(?:Data Connectors|DataConnectors|Data Connector)/.*\.json$'
)
_RE_SOLUTION_DATA = re.compile(
    r'^Solutions/(?P<sol>[^/]+)/Data/Solution_.*\.json$'
)
_RE_MAIN_TEMPLATE = re.compile(
    r'^Solutions/(?P<sol>[^/]+)/.*mainTemplate\.json$', re.IGNORECASE
)


def is_solution_deprecated(description: str) -> bool:
    """True when a solution Description indicates the solution is deprecated."""
    for pattern in SOLUTION_DEPRECATED_PATTERNS:
        if pattern.search(description):
            return True
    return False


def _availability_deprecated(entry: Dict[str, Any]) -> bool:
    """True when availability.status is explicitly 0."""
    availability = entry.get('availability')
    if isinstance(availability, dict) and availability.get('status') == 0:
        return True
    return False


def _title_deprecated(title: str) -> bool:
    upper = title.upper()
    return '[DEPRECATED]' in upper or title.startswith('[Deprecated]')


def find_connector_objects(data: Any) -> List[Dict[str, Any]]:
    """Find connector objects (id/publisher/title dicts) anywhere in ``data``.

    Mirrors the mapper's detection, including ARM-variable id regeneration.
    """
    connectors: List[Dict[str, Any]] = []
    stack = [data]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if {"id", "publisher", "title"}.issubset(current.keys()):
                id_value = current.get("id")
                publisher_value = current.get("publisher")
                title_value = current.get("title")
                if (
                    isinstance(id_value, str)
                    and isinstance(publisher_value, str)
                    and isinstance(title_value, str)
                    and "[variables(" not in title_value.lower()
                ):
                    resolved_id = id_value
                    if "[variables(" in id_value.lower():
                        resolved_id = title_value.replace(" ", "").replace("-", "")
                    connectors.append({
                        "id": resolved_id,
                        "title": title_value,
                        "availability": current.get("availability"),
                    })
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return connectors


def find_connectors_in_main_template(data: Any) -> List[Dict[str, Any]]:
    """Find dataConnectorDefinitions connectors inside an ARM mainTemplate."""
    connectors: List[Dict[str, Any]] = []
    if not isinstance(data, dict):
        return connectors
    resources = data.get("resources", [])
    if not isinstance(resources, list):
        return connectors
    stack = list(resources)
    seen_ids: Set[str] = set()
    while stack:
        resource = stack.pop()
        if not isinstance(resource, dict):
            continue
        resource_type = resource.get("type", "")
        if isinstance(resource_type, str) and "dataconnectordefinitions" in resource_type.lower():
            properties = resource.get("properties", {})
            if isinstance(properties, dict):
                ui_config = properties.get("connectorUiConfig", {})
                if isinstance(ui_config, dict):
                    connector_id = ui_config.get("id", "")
                    title = ui_config.get("title", "")
                    publisher = ui_config.get("publisher", "")
                    if isinstance(connector_id, str) and "[variables(" in connector_id.lower():
                        if isinstance(title, str) and title:
                            connector_id = title.replace(" ", "").replace("-", "")
                        else:
                            connector_id = ""
                    if (
                        isinstance(connector_id, str) and connector_id
                        and isinstance(title, str) and title
                        and isinstance(publisher, str) and publisher
                        and connector_id not in seen_ids
                    ):
                        seen_ids.add(connector_id)
                        connectors.append({
                            "id": connector_id,
                            "title": title,
                            "availability": ui_config.get("availability"),
                        })
        nested_resources = resource.get("resources", [])
        if isinstance(nested_resources, list):
            stack.extend(nested_resources)
        properties = resource.get("properties", {})
        if isinstance(properties, dict):
            main_template = properties.get("mainTemplate", {})
            if isinstance(main_template, dict):
                nested = main_template.get("resources", [])
                if isinstance(nested, list):
                    stack.extend(nested)
    return connectors


def extract_connector_payloads(data: Any) -> List[Tuple[str, str]]:
    """Return [(connector_id, content_hash), ...] for connector objects.

    Used by the merge-based change-flow metric. The hash is a stable SHA-1 of
    the full connector object (sorted keys), so that ``update`` is detected
    only when a connector's own content actually changes — not merely because
    the file it lives in was touched.
    """
    results: List[Tuple[str, str]] = []
    stack = [data]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if {"id", "publisher", "title"}.issubset(current.keys()):
                id_value = current.get("id")
                publisher_value = current.get("publisher")
                title_value = current.get("title")
                if (
                    isinstance(id_value, str)
                    and isinstance(publisher_value, str)
                    and isinstance(title_value, str)
                    and "[variables(" not in title_value.lower()
                ):
                    resolved_id = id_value
                    if "[variables(" in id_value.lower():
                        resolved_id = title_value.replace(" ", "").replace("-", "")
                    payload = json.dumps(current, sort_keys=True, ensure_ascii=False)
                    digest = hashlib.sha1(payload.encode("utf-8", "replace")).hexdigest()
                    results.append((resolved_id, digest))
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return results


# --------------------------------------------------------------------------- #
# Git plumbing helpers.
# --------------------------------------------------------------------------- #
def _git(repo: Path, args: List[str], binary: bool = False) -> Any:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout if binary else result.stdout.decode("utf-8", "replace")


def resolve_ref(repo: Path, preferred: Optional[str]) -> str:
    """Resolve the history ref, preferring origin/master then master then HEAD."""
    candidates = [preferred] if preferred else ["origin/master", "master", "HEAD"]
    for ref in candidates:
        if not ref:
            continue
        try:
            _git(repo, ["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"])
            return ref
        except subprocess.CalledProcessError:
            continue
    raise SystemExit("Could not resolve a git ref (tried: %s)" % candidates)


def commit_before(repo: Path, ref: str, when: dt.date) -> Optional[Tuple[str, str]]:
    """Return (sha, iso_commit_date) of the last commit on ref before ``when``."""
    iso = f"{when.isoformat()}T00:00:00"
    out = _git(repo, ["rev-list", "-1", f"--before={iso}", ref]).strip()
    if not out:
        return None
    cdate = _git(repo, ["show", "-s", "--format=%cs", out]).strip()
    return out, cdate


def list_tree_files(repo: Path, commit: str) -> List[str]:
    """List all file paths under Solutions/ at ``commit`` (NUL-safe)."""
    raw = _git(
        repo,
        ["-c", "core.quotepath=false", "ls-tree", "-r", "-z",
         "--name-only", commit, "--", "Solutions"],
        binary=True,
    )
    if not raw:
        return []
    return [p.decode("utf-8", "replace") for p in raw.split(b"\x00") if p]


def read_blobs(repo: Path, commit: str, paths: List[str]) -> Dict[str, bytes]:
    """Read many blobs at ``commit`` in a single cat-file --batch process.

    A dedicated writer thread feeds object specs into git's stdin while the
    main thread consumes stdout, avoiding the pipe deadlock that occurs when
    git's output buffer fills before all specs have been written.
    """
    if not paths:
        return {}
    proc = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    assert proc.stdin and proc.stdout

    def _feed() -> None:
        try:
            for p in paths:
                proc.stdin.write(f"{commit}:{p}\n".encode("utf-8"))
            proc.stdin.flush()
        finally:
            proc.stdin.close()

    writer = threading.Thread(target=_feed, daemon=True)
    writer.start()

    out: Dict[str, bytes] = {}
    for path in paths:
        header = proc.stdout.readline()
        if not header:
            break
        parts = header.split()
        if len(parts) == 2 and parts[1] == b"missing":
            continue
        if len(parts) < 3:
            # Unexpected; skip remainder for safety.
            continue
        size = int(parts[2])
        content = proc.stdout.read(size)
        proc.stdout.read(1)  # trailing newline
        out[path] = content
    proc.stdout.read()
    writer.join()
    proc.wait()
    return out


def _iter_blobs_multi(repo: Path, specs: List[Tuple[str, str]]):
    """Stream blobs for many (commit, path) specs from one cat-file process.

    Yields ``(index, content_bytes_or_None)`` in the same order as ``specs``.
    A writer thread feeds ``<commit>:<path>`` lines while the main thread reads
    responses, avoiding the cat-file stdin/stdout pipe deadlock.
    """
    if not specs:
        return
    proc = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    assert proc.stdin and proc.stdout

    def _feed() -> None:
        try:
            for commit, path in specs:
                proc.stdin.write(f"{commit}:{path}\n".encode("utf-8"))
            proc.stdin.flush()
        finally:
            proc.stdin.close()

    writer = threading.Thread(target=_feed, daemon=True)
    writer.start()

    for i in range(len(specs)):
        header = proc.stdout.readline()
        if not header:
            break
        parts = header.split()
        if len(parts) == 2 and parts[1] == b"missing":
            yield i, None
            continue
        if len(parts) < 3:
            yield i, None
            continue
        size = int(parts[2])
        content = proc.stdout.read(size)
        proc.stdout.read(1)  # trailing newline
        yield i, content

    proc.stdout.read()
    writer.join()
    proc.wait()


def compute_change_flow(repo: Path, ref: str) -> Dict[str, Dict[str, int]]:
    """Per-month distinct connector creates/updates from first-parent merges.

    Walks the first-parent merge commits on ``ref`` (oldest first), diffing
    each merge against its first parent to find the connector definition files
    it brought to master. Connector IDs are classified, against a running
    global inventory, as:

    * **created** — the ID had not been seen in any earlier merge;
    * **updated** — the ID existed but its content hash changed.

    Within a month, sets are de-duplicated and ``created`` takes precedence
    over ``updated`` (a connector created and later changed in the same month
    counts only as created).

    Scope note: only merge commits are considered. Connectors introduced via
    direct (non-merge) commits to master are attributed to the first merge
    that later touches their file.
    """
    raw = _git(
        repo,
        ["-c", "core.quotepath=false", "log", "--first-parent", "--merges",
         "--name-status", "--date=short", "--format=__C__%x09%H%x09%cs", ref],
    )

    # Parse: each merge -> (sha, YYYY-MM-DD, [connector paths added/modified]).
    merges: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    for line in raw.splitlines():
        if line.startswith("__C__\t"):
            _, sha, cdate = line.split("\t", 2)
            current = {"sha": sha, "date": cdate, "paths": []}
            merges.append(current)
        elif line and current is not None:
            parts = line.split("\t")
            status = parts[0]
            if status.startswith("D"):
                continue
            path = parts[-1]  # for renames (R…) git emits old\tnew -> take new
            if _RE_CONNECTOR_FILE.match(path):
                current["paths"].append(path)

    # Keep only merges that touched connectors; process oldest -> newest.
    merges = [m for m in merges if m["paths"]]
    merges.reverse()

    # Build a flat, chronological spec list with parallel month metadata.
    specs: List[Tuple[str, str]] = []
    spec_month: List[str] = []
    for m in merges:
        month_key = m["date"][:7] + "-01"
        for p in m["paths"]:
            specs.append((m["sha"], p))
            spec_month.append(month_key)

    known: Dict[str, str] = {}
    month_created: Dict[str, Set[str]] = {}
    month_updated: Dict[str, Set[str]] = {}

    for idx, content in _iter_blobs_multi(repo, specs):
        if content is None:
            continue
        data = _load_json(content)
        if data is None:
            continue
        month_key = spec_month[idx]
        created = month_created.setdefault(month_key, set())
        updated = month_updated.setdefault(month_key, set())
        for cid, digest in extract_connector_payloads(data):
            if cid not in known:
                created.add(cid)
            elif known[cid] != digest:
                updated.add(cid)
            known[cid] = digest

    flow: Dict[str, Dict[str, int]] = {}
    for month_key in set(month_created) | set(month_updated):
        created = month_created.get(month_key, set())
        updated = month_updated.get(month_key, set()) - created
        flow[month_key] = {"created": len(created), "updated": len(updated)}
    return flow


def _load_json(blob: bytes) -> Optional[Any]:
    try:
        return json.loads(blob.decode("utf-8-sig", "replace"))
    except (ValueError, UnicodeDecodeError):
        return None


# --------------------------------------------------------------------------- #
# Per-commit analysis.
# --------------------------------------------------------------------------- #
def analyze_commit(repo: Path, commit: str, include_main_template: bool) -> Dict[str, int]:
    """Count distinct active / deprecated connector IDs at ``commit``."""
    all_paths = list_tree_files(repo, commit)

    connector_paths: List[str] = []
    solution_data_paths: List[str] = []
    main_template_paths: List[str] = []
    for p in all_paths:
        if _RE_CONNECTOR_FILE.match(p):
            connector_paths.append(p)
        elif _RE_SOLUTION_DATA.match(p):
            solution_data_paths.append(p)
        elif include_main_template and _RE_MAIN_TEMPLATE.match(p):
            main_template_paths.append(p)

    wanted = connector_paths + solution_data_paths + main_template_paths
    blobs = read_blobs(repo, commit, wanted)

    # Solution-level deprecation, keyed by solution folder name.
    deprecated_solutions: Set[str] = set()
    for p in solution_data_paths:
        m = _RE_SOLUTION_DATA.match(p)
        if not m:
            continue
        data = _load_json(blobs.get(p, b""))
        if not isinstance(data, dict):
            continue
        description = data.get("Description") or data.get("description") or ""
        if isinstance(description, str) and is_solution_deprecated(description):
            deprecated_solutions.add(m.group("sol"))

    # active_ids: connector IDs seen active in >=1 occurrence.
    # all_ids: every connector ID encountered.
    active_ids: Set[str] = set()
    all_ids: Set[str] = set()

    def consider(sol: str, conn: Dict[str, Any]) -> None:
        cid = conn["id"]
        all_ids.add(cid)
        deprecated = (
            _title_deprecated(conn["title"])
            or _availability_deprecated(conn)
            or sol in deprecated_solutions
        )
        if not deprecated:
            active_ids.add(cid)

    for p in connector_paths:
        m = _RE_CONNECTOR_FILE.match(p)
        data = _load_json(blobs.get(p, b""))
        if data is None or not m:
            continue
        for conn in find_connector_objects(data):
            consider(m.group("sol"), conn)

    for p in main_template_paths:
        m = _RE_MAIN_TEMPLATE.match(p)
        data = _load_json(blobs.get(p, b""))
        if data is None or not m:
            continue
        for conn in find_connectors_in_main_template(data):
            consider(m.group("sol"), conn)

    total = len(all_ids)
    active = len(active_ids)
    return {
        "total_connectors": total,
        "active_connectors": active,
        "deprecated_connectors": total - active,
    }


# --------------------------------------------------------------------------- #
# Month iteration & CLI.
# --------------------------------------------------------------------------- #
def month_firsts(start: dt.date, end: dt.date) -> List[dt.date]:
    months: List[dt.date] = []
    y, m = start.year, start.month
    while dt.date(y, m, 1) <= end:
        months.append(dt.date(y, m, 1))
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
    return months


def _parse_month(value: str) -> dt.date:
    for fmt in ("%Y-%m", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(value, fmt).date().replace(day=1)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Invalid month '{value}' (use YYYY-MM)")


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_repo = script_dir.parents[1]  # Tools/Solutions Analyzer -> repo root

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=default_repo,
                        help="Path to the Azure-Sentinel git repo (default: inferred).")
    parser.add_argument("--ref", default=None,
                        help="Git ref to sample (default: origin/master -> master -> HEAD).")
    parser.add_argument("--start", type=_parse_month, default=_parse_month("2021-01"),
                        help="First month to sample, YYYY-MM (default: 2021-01).")
    parser.add_argument("--end", type=_parse_month, default=None,
                        help="Last month to sample, YYYY-MM (default: current month).")
    parser.add_argument("--output", type=Path,
                        default=script_dir / "connector_history.csv",
                        help="Output CSV path.")
    parser.add_argument("--no-main-template", action="store_true",
                        help="Skip dataConnectorDefinitions in mainTemplate.json files.")
    parser.add_argument("--no-flow", action="store_true",
                        help="Skip the merge-based per-month create/update columns.")
    args = parser.parse_args()

    repo: Path = args.repo
    ref = resolve_ref(repo, args.ref)
    today = dt.date.today()
    end: dt.date = args.end or today.replace(day=1)
    if end > today.replace(day=1):
        end = today.replace(day=1)

    include_main_template = not args.no_main_template
    months = month_firsts(args.start, end)

    print(f"Repo:   {repo}")
    print(f"Ref:    {ref}")
    print(f"Range:  {months[0].isoformat()} .. {months[-1].isoformat()} "
          f"({len(months)} months)")
    print(f"Output: {args.output}")
    print("-" * 60)

    rows: List[Dict[str, Any]] = []
    seen_commits: Dict[str, Dict[str, int]] = {}
    for month in months:
        found = commit_before(repo, ref, month)
        if not found:
            print(f"{month.isoformat()}  (no commit before this date — skipped)")
            continue
        sha, cdate = found
        if sha in seen_commits:
            counts = seen_commits[sha]
        else:
            counts = analyze_commit(repo, sha, include_main_template)
            seen_commits[sha] = counts
        rows.append({
            "month": month.isoformat(),
            "commit_sha": sha[:12],
            "commit_date": cdate,
            "active_connectors": counts["active_connectors"],
            "deprecated_connectors": counts["deprecated_connectors"],
            "total_connectors": counts["total_connectors"],
        })
        print(f"{month.isoformat()}  {sha[:12]}  {cdate}  "
              f"active={counts['active_connectors']:>4}  "
              f"deprecated={counts['deprecated_connectors']:>3}  "
              f"total={counts['total_connectors']:>4}")

    fieldnames = ["month", "commit_sha", "commit_date",
                  "active_connectors", "deprecated_connectors", "total_connectors"]

    if not args.no_flow:
        print("-" * 60)
        print("Computing per-month creates/updates from first-parent merges...")
        flow = compute_change_flow(repo, ref)
        for row in rows:
            counts = flow.get(row["month"], {})
            row["connectors_created"] = counts.get("created", 0)
            row["connectors_updated"] = counts.get("updated", 0)
        fieldnames += ["connectors_created", "connectors_updated"]
        total_created = sum(r.get("connectors_created", 0) for r in rows)
        total_updated = sum(r.get("connectors_updated", 0) for r in rows)
        print(f"Flow covered {len(flow)} months; "
              f"in range: created={total_created}, updated={total_updated}")

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("-" * 60)
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
