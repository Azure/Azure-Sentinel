from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess
from typing import Any

import yaml

_URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+", re.IGNORECASE)
DOCUMENTS_LINK_LOCALE_RE = re.compile(
    r"(https://docs\.microsoft\.com|https://azure\.microsoft\.com)(/[a-z]{2}-[a-z]{2})",
    re.IGNORECASE,
)
_MICROSOFT_LOCALE_URL_RE = re.compile(
    r"^(https://(?:docs|azure|learn|support)\.microsoft\.com)/[a-z]{2}-[a-z]{2}(?=/|$|[?#])",
    re.IGNORECASE,
)
_URL_SCAN_SKIP_SUFFIXES: frozenset[str] = frozenset(
    {
        ".zip",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".webp",
        ".pdf",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".dll",
        ".exe",
        ".bin",
    }
)


def _version_tuple(version: Any) -> tuple[int, int, int]:
    parts = str(version).strip().split(".")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        return int(parts[0]), int(parts[1]), int(parts[2])
    if len(parts) == 2 and all(part.isdigit() for part in parts):
        return int(parts[0]), int(parts[1]), 0
    return (0, 0, 0)


def _bump_patch_version(version: Any) -> str:
    parts = str(version).strip().split(".")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        return f"{int(parts[0])}.{int(parts[1])}.{int(parts[2]) + 1}"
    if len(parts) == 2 and all(part.isdigit() for part in parts):
        return f"{int(parts[0])}.{int(parts[1])}.1"
    return str(version).strip()


def _without_version(document: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key != "version"}


def _find_git_repo_root(path: Path) -> Path | None:
    resolved = path.resolve()
    current = resolved if resolved.is_dir() else resolved.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _git_head_tracked_files(solution_root: Path) -> tuple[Path | None, set[str]]:
    repo_root = _find_git_repo_root(solution_root)
    if repo_root is None:
        return None, set()
    try:
        rel_root = solution_root.resolve().relative_to(repo_root.resolve()).as_posix()
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "ls-tree", "-r", "--name-only", "HEAD", "--", rel_root],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except (OSError, ValueError):
        return repo_root, set()
    if proc.returncode != 0 or not proc.stdout.strip():
        return repo_root, set()
    return repo_root, {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def _load_git_head_yaml(
    path: Path,
    repo_root: Path | None,
    tracked_rel_paths: set[str] | None = None,
) -> dict[str, Any] | None:
    if repo_root is None:
        return None
    try:
        rel_posix = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return None
    if tracked_rel_paths is not None and rel_posix not in tracked_rel_paths:
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"HEAD:{rel_posix}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        loaded = yaml.safe_load(proc.stdout)
    except yaml.YAMLError:
        return None
    return loaded if isinstance(loaded, dict) else None


def strip_microsoft_url_locale(url: str) -> str:
    """Strip locale segment (e.g. /en-us) from Microsoft documentation and redirect URLs."""
    cleaned = str(url or "").strip()
    if not cleaned:
        return cleaned
    cleaned = _MICROSOFT_LOCALE_URL_RE.sub(r"\1", cleaned)
    return DOCUMENTS_LINK_LOCALE_RE.sub(r"\1", cleaned)


def _collect_solution_text_files_for_url_scan(
    solution_root: Path,
    files_by_type: Mapping[str, list[str]] | None = None,
    changed_files: list[str] | None = None,
) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []

    def _add(rel_path: str) -> None:
        norm = str(rel_path or "").replace("\\", "/").strip("/")
        if not norm or norm in seen:
            return
        low = norm.lower()
        if low.startswith("logs/") or low.startswith("evidence/pr-qualification/"):
            return
        if Path(norm).name.lower() == ".env":
            return
        fpath = solution_root / norm
        if not fpath.is_file() or fpath.is_symlink():
            return
        try:
            rel_parts = fpath.relative_to(solution_root).parts
        except ValueError:
            return
        cur = solution_root
        for part in rel_parts[:-1]:
            cur = cur / part
            if cur.is_symlink():
                return
        if fpath.suffix.lower() in _URL_SCAN_SKIP_SUFFIXES:
            return
        seen.add(norm)
        ordered.append(norm)

    if isinstance(files_by_type, Mapping):
        for rel_list in files_by_type.values():
            if isinstance(rel_list, list):
                for rel in rel_list:
                    _add(rel)

    if changed_files:
        for rel in changed_files:
            _add(rel)
        ev_dir = solution_root / "Evidence"
        if ev_dir.is_dir() and not ev_dir.is_symlink():
            for fpath in sorted(ev_dir.rglob("*")):
                if fpath.is_file():
                    try:
                        _add(fpath.relative_to(solution_root).as_posix())
                    except ValueError:
                        continue
    elif solution_root.is_dir() and not solution_root.is_symlink():
        for fpath in sorted(solution_root.rglob("*")):
            if fpath.is_file():
                try:
                    _add(fpath.relative_to(solution_root).as_posix())
                except ValueError:
                    continue

    return ordered


def scan_solution_urls(
    solution_root: str | Path,
    *,
    files_by_type: Mapping[str, list[str]] | None = None,
    changed_files: list[str] | None = None,
) -> dict[str, Any]:
    """Scan solution text files for insecure HTTP URLs and CI DocumentsLinkValidation locale URLs."""
    root = Path(solution_root).expanduser().resolve()
    rel_files = _collect_solution_text_files_for_url_scan(
        root,
        files_by_type=files_by_type,
        changed_files=changed_files,
    )
    urls_found: list[str] = []
    bad_urls: list[str] = []
    insecure_urls: list[dict[str, str]] = []
    locale_issues: list[dict[str, str]] = []
    checked_files: list[str] = []
    aka_ms_count = 0

    for rel in rel_files:
        fpath = root / rel
        try:
            txt = fpath.read_text(encoding="utf-8-sig")
        except Exception:
            continue
        checked_files.append(rel)
        rel_low = rel.lower()
        is_rule_or_query_yaml = fpath.suffix.lower() in {".yaml", ".yml"} and any(
            seg in rel_low
            for seg in ("analytic rules/", "xdr detections/", "hunting queries/", "parsers/")
        )
        is_exempt_from_insecure_http = (
            is_rule_or_query_yaml
            or "sample data/" in f"/{rel_low}"
            or fpath.name.lower() == "mock.json"
            or fpath.suffix.lower() == ".csv"
        )
        for m in _URL_RE.finditer(txt):
            u = m.group(0).rstrip(".,;\"'\\")
            urls_found.append(u)
            if "aka.ms/" in u.lower():
                aka_ms_count += 1
            if (
                not is_exempt_from_insecure_http
                and u.lower().startswith("http://")
                and not u.lower().startswith("http://schemas.")
            ):
                msg = f"{rel}: insecure HTTP URL {u}"
                insecure_urls.append({"file": rel, "url": u, "message": msg})
                bad_urls.append(msg)
            if DOCUMENTS_LINK_LOCALE_RE.search(u):
                recommended = strip_microsoft_url_locale(u)
                msg = (
                    f"{rel}: locale URL {u} fails CI DocumentsLinkValidation "
                    f"(recommended fix: {recommended})"
                )
                locale_issues.append(
                    {
                        "file": rel,
                        "url": u,
                        "recommendedUrl": recommended,
                        "message": msg,
                    }
                )
                bad_urls.append(msg)

    return {
        "checkedFiles": checked_files,
        "urlsFound": urls_found,
        "akaMsCount": aka_ms_count,
        "badUrls": bad_urls,
        "insecureUrls": insecure_urls,
        "localeIssues": locale_issues,
    }


def content_path(root: Path, relative: str | Path) -> Path:
    """Resolve a portable content reference without leaving its content root."""
    value = str(relative).replace("\\", "/")
    reference = PurePosixPath(value)
    if (
        reference.is_absolute()
        or PureWindowsPath(value).drive
        or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value)
        or ".." in reference.parts
        or not reference.parts
    ):
        raise ValueError(f"content path must be relative and contained: {relative}")
    path = root.joinpath(*reference.parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"content path escapes its root: {relative}")
    for parent in (path, *path.parents):
        if parent == root.parent:
            break
        if parent.is_symlink():
            raise ValueError(f"symlink content paths are not supported: {parent}")
    return path


def yaml_files(root: Path) -> list[Path]:
    if root.is_symlink():
        raise ValueError(f"symlink content paths are not supported: {root}")
    files: list[Path] = []
    for directory, directories, names in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if name.lower() not in {"logs", "reports", "evidence"}]
        for name in directories:
            content_path(root, (Path(directory) / name).relative_to(root))
        for name in names:
            path = Path(directory) / name
            if path.suffix.lower() in {".yaml", ".yml"}:
                files.append(content_path(root, path.relative_to(root)))
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def detection_reference(requested: str, available: list[str]) -> str:
    """Allow legacy basename/stem selectors only when they are unambiguous."""
    requested = requested.replace("\\", "/")
    if requested in available:
        return requested
    matches = [
        name for name in available
        if requested in {PurePosixPath(name).name, PurePosixPath(name).stem}
    ]
    if len(matches) > 1:
        raise ValueError(
            f"ambiguous detection {requested!r}; use its relative path: {', '.join(matches)}"
        )
    if not matches:
        raise ValueError(f"unknown detection: {requested}")
    return matches[0]
