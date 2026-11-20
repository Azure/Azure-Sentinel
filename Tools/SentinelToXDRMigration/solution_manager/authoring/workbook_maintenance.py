"""Explicit, local review of published workbook reuse; never runtime acceptance.

Plans and approved records contain identities, not private authoring receipts.
All entry points are read-only. A configured remote identifies what the reviewer
is approving; it is not itself evidence of trust or publication.
Explicit acceptance grants policy-level trust in that baseline, not a verified
signature, provider result, or qualification claim.
"""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import unquote, urlsplit

from solution_manager.authoring import workbook_publication as publication
from solution_manager.core.content_paths import content_path
from solution_manager.migration import workbooks

FORMAT = "workbook-maintenance-v1"
_REVIEW_FIELDS = {"actor", "reference", "decision"}
_PLAN_FIELDS = {
    "format", "repository", "commit", "solutionPath", "workbooks",
    "dependencies", "baselineDependenciesSha256",
}
_DEPENDENCY_DIRS = ("Data Connectors", "Parsers")


def _validate_repository_url(value: str) -> None:
    """Keep reportable repository identities free of transport credentials."""
    message = ("Published repository must use a credential-free HTTPS or SSH remote "
               "without passwords, HTTPS user information, query strings or fragments.")
    if not isinstance(value, str) or not value:
        raise ValueError(message)
    decoded = unquote(value)
    if (any(character.isspace() for character in value)
            or any(ord(character) < 32 or ord(character) == 127 for character in decoded)
            or any(character in decoded for character in ("?", "#", "\\"))):
        raise ValueError(message)
    if "://" in value:
        try:
            url = urlsplit(value)
            if (url.scheme not in {"https", "ssh"} or not url.hostname
                    or not url.path or url.path == "/" or url.password is not None
                    or "%" in url.netloc
                    or (url.scheme == "https" and url.username is not None)
                    or (url.username is not None
                        and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", url.username))):
                raise ValueError(message)
            # Accessing port validates malformed and out-of-range port values.
            url.port
        except ValueError:
            raise ValueError(message) from None
    elif not re.fullmatch(
        r"(?:[A-Za-z_][A-Za-z0-9_.-]*@)?"
        r"(?:[A-Za-z0-9][A-Za-z0-9_.-]*|\[[0-9A-Fa-f:]+\]):"
        r"[^:@]+", value,
    ):
        raise ValueError(message)


def _git(root: Path, *args: str, missing_ok: bool = False) -> bytes:
    # Do not fetch promised objects or substitute locally replaced Git objects.
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "--no-replace-objects",
             "--literal-pathspecs", "-C", str(root), *args],
            capture_output=True,
            env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"},
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Maintenance requires an available local Git repository and baseline.") from exc
    if result.returncode and not (missing_ok and result.returncode == 1):
        raise ValueError("Cannot read the exact maintenance Git baseline/configuration locally; "
                         "make the approved commit and all required objects available.")
    return result.stdout


def _excluded(parts: tuple[str, ...]) -> bool:
    from solution_manager.packaging.packaging import PACKAGE_OUTPUT_DIRECTORIES

    return any(part.lower() in PACKAGE_OUTPUT_DIRECTORIES
               or part.lower() == ".env" or part.lower().startswith(".env.")
               for part in parts)


def _dependencies(root: Path) -> list[dict]:
    rows = []

    def fail(error):
        raise error

    for directory in _DEPENDENCY_DIRS:
        base = content_path(root, directory)
        if not base.exists():
            continue
        if not base.is_dir():
            raise ValueError(f"Maintenance dependency directory is not a directory: {directory}")
        for current, directories, names in os.walk(base, followlinks=False, onerror=fail):
            directories[:] = [
                name for name in directories
                if not _excluded((Path(current) / name).relative_to(root).parts)
            ]
            for name in directories:
                content_path(root, (Path(current) / name).relative_to(root))
            for name in names:
                relative = (Path(current) / name).relative_to(root)
                if _excluded(relative.parts):
                    continue
                path = content_path(root, relative)
                if not path.is_file():
                    raise ValueError(f"Maintenance dependency is not a regular file: {relative}")
                rows.append({"path": relative.as_posix(),
                             "sha256": workbooks._sha(path.read_bytes())})
    rows.sort(key=lambda row: row["path"])
    if len({row["path"].casefold() for row in rows}) != len(rows):
        raise ValueError("Case-insensitive maintenance dependency path collision.")
    return rows


def _baseline(root: Path, commit: str, solution_path: str) -> dict:
    prefix = "" if solution_path == "." else solution_path + "/"
    scopes = [prefix + directory for directory in (*_DEPENDENCY_DIRS, "XDR Workbooks")]
    entries = {}
    for entry in _git(root, "ls-tree", "-r", "-z", commit, "--", *scopes).split(b"\0"):
        if not entry:
            continue
        header, raw_path = entry.split(b"\t", 1)
        mode, kind, object_id = header.decode("ascii").split()
        relative = raw_path.decode("utf-8").removeprefix(prefix)
        parts = PurePosixPath(relative).parts
        if _excluded(parts):
            continue
        if mode not in {"100644", "100755"} or kind != "blob":
            raise ValueError(f"Unsafe symlink/submodule in maintenance baseline: {relative}")
        if "\\" in relative or ".." in parts:
            raise ValueError("Unsafe path in maintenance baseline.")
        entries[relative] = object_id
    if len({path.casefold() for path in entries}) != len(entries):
        raise ValueError("Case-insensitive maintenance baseline path collision.")
    return entries


def plan_maintenance(solution, *, public_ref: str, repository_url: str) -> dict:
    """Plan exact selected clean workbooks against a reviewer-named local commit.

    Changed/new workbooks and any connector/parser inventory change require a
    valid current local authoring receipt. Baseline equality only makes reuse
    eligible for the separate explicit maintenance review.
    """
    try:
        return _plan(solution, public_ref=public_ref, repository_url=repository_url)
    except (OSError, UnicodeError, TypeError, KeyError, AttributeError) as exc:
        raise ValueError("Cannot plan workbook maintenance; check selected public JSON, "
                         "dependencies and the local baseline: " + str(exc)) from exc


def _plan(solution, *, public_ref: str, repository_url: str) -> dict:
    if not isinstance(public_ref, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", public_ref):
        raise ValueError("Maintenance requires a full immutable 40-hex commit SHA, not a symbolic ref.")
    _validate_repository_url(repository_url)
    root = workbooks._root(solution)
    top = Path(_git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
    if not root.is_relative_to(top):
        raise ValueError("Maintenance solution must be contained in its Git repository.")
    remote_lines = _git(top, "config", "--get-regexp", r"^remote\..*\.url$",
                        missing_ok=True).decode("utf-8").splitlines()
    remotes = [line.split(None, 1)[1] for line in remote_lines if len(line.split(None, 1)) == 2]
    if repository_url not in remotes:
        raise ValueError("Published repository URL must exactly match a configured Git remote URL; "
                         "the reviewer must explicitly approve that repository.")
    commit = _git(top, "rev-parse", "--verify", "--end-of-options",
                  public_ref + "^{commit}").decode("ascii").strip()
    if commit != public_ref.lower():
        raise ValueError("Maintenance baseline must identify the exact commit, not a tag object.")
    solution_path = root.relative_to(top).as_posix()
    paths = workbooks.selected_workbook_files(root)
    documents = [(path, workbooks._document(path)) for path in paths]
    for path, document in documents:
        if not publication.is_public(document):
            raise ValueError(f"{path.relative_to(root).as_posix()}: maintenance requires "
                             "public-workbook-v1; run workbook-publication-plan/clean with "
                             "explicit review before planning maintenance.")
    validation = workbooks.validate_workbooks(root, selected_only=True, _documents=documents)
    errors = [f"{row['path']}: {error}"
              for row in validation["results"] for error in row["errors"]]
    if errors:
        raise ValueError("Current workbook structure/dependencies/identity failed: " + "; ".join(errors))
    dependencies = _dependencies(root)
    baseline = _baseline(top, commit, solution_path)
    baseline_dependencies = [
        {"path": path, "sha256": workbooks._sha(_git(top, "cat-file", "blob", object_id))}
        for path, object_id in sorted(baseline.items())
        if PurePosixPath(path).parts[0] in _DEPENDENCY_DIRS
    ]
    dependencies_match = dependencies == baseline_dependencies
    rows = []
    for path, document in documents:
        relative = path.relative_to(root).as_posix()
        document_hash = publication.digest(document)
        baseline_matches = False
        if relative in baseline:
            raw = _git(top, "cat-file", "blob", baseline[relative])
            try:
                previous = workbooks._load_json(raw)
                baseline_matches = (isinstance(previous, dict)
                                    and publication.is_public(previous)
                                    and publication.digest(previous) == document_hash)
            except (ValueError, TypeError, AttributeError):
                baseline_matches = False
        inherited = baseline_matches and dependencies_match
        if not inherited:
            errors = publication.publication_errors(root, document)
            if errors:
                reason = ("connector/parser dependency inventory changed" if not dependencies_match
                          else "workbook differs from or is absent at the published baseline")
                raise ValueError(f"{relative}: {reason}; current local authoring review required: "
                                 + "; ".join(errors))
        raw = path.read_bytes()
        if publication.digest(workbooks._load_json(raw)) != document_hash:
            raise ValueError("Workbook changed during maintenance planning; replan and review.")
        rows.append({"path": relative, "documentSha256": document_hash,
                     "fileSha256": workbooks._sha(raw),
                     "acceptance": "published-baseline" if inherited else "local-review"})
    if workbooks.selected_workbook_files(root) != paths or _dependencies(root) != dependencies:
        raise ValueError("Selection/dependencies changed during maintenance planning; replan and review.")
    if any(workbooks._sha(path.read_bytes()) != row["fileSha256"]
           for path, row in zip(paths, rows)):
        raise ValueError("Workbook bytes changed during maintenance planning; replan and review.")
    plan = {
        "format": FORMAT, "repository": repository_url, "commit": commit,
        "solutionPath": solution_path, "workbooks": rows, "dependencies": dependencies,
        "baselineDependenciesSha256": publication.digest(baseline_dependencies),
    }
    plan["planSha256"] = publication.digest(plan)
    plan.update(actor="", reference="", decision=None)
    return plan


def review_maintenance(solution, review: dict) -> dict:
    """Verify an explicit, current maintenance authorization; write nothing."""
    if not isinstance(review, dict) or set(review) != _PLAN_FIELDS | _REVIEW_FIELDS | {"planSha256"}:
        raise ValueError("Maintenance review must have the exact workbook-maintenance-v1 plan shape.")
    if (review["decision"] != "accept"
            or any(not isinstance(review[key], str) or not review[key].strip()
                   for key in ("actor", "reference"))):
        raise ValueError("Maintenance requires explicit decision=accept and nonempty actor/reference.")
    current = plan_maintenance(solution, public_ref=review["commit"],
                               repository_url=review["repository"])
    try:
        substantive = {key: review[key] for key in _PLAN_FIELDS}
        if (publication.digest(substantive) != review["planSha256"]
                or any(review[key] != current[key] for key in _PLAN_FIELDS | {"planSha256"})):
            raise ValueError("Maintenance review is stale or tampered; replan and explicitly review "
                             "the exact repository, commit, selection, workbook bytes and dependencies.")
    except (TypeError, OverflowError) as exc:
        raise ValueError("Maintenance review must contain valid JSON plan values.") from exc
    return deepcopy(review)


def validate_maintenance(solution, record: dict) -> None:
    """Recheck the exact approval and live local inputs, without implicit trust."""
    review_maintenance(solution, record)
