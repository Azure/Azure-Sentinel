"""Predictable release-notes date resolution and validation helpers."""
from __future__ import annotations

from datetime import date, datetime
import hashlib
from pathlib import Path
import re

RELEASE_DATE_FORMAT = "%d-%m-%Y"
EXPECTED_RELEASE_NOTES_HEADER = [
    "**Version**",
    "**Date Modified (DD-MM-YYYY)**",
    "**Change History**",
]


def default_release_date(*, today: date | None = None) -> str:
    """Return today's date in the repository-standard DD-MM-YYYY format."""
    current = today if today is not None else date.today()
    return current.strftime(RELEASE_DATE_FORMAT)


def resolve_release_date(
    release_date: str | None = None,
    *,
    today: date | None = None,
) -> str:
    """Resolve an optional release date to a validated DD-MM-YYYY string."""
    if release_date is None or (isinstance(release_date, str) and not release_date.strip()):
        return default_release_date(today=today)
    if not isinstance(release_date, str):
        raise ValueError("release date must be a valid DD-MM-YYYY date")
    try:
        parsed_date = datetime.strptime(release_date, RELEASE_DATE_FORMAT)
    except ValueError as exc:
        raise ValueError("release date must be a valid DD-MM-YYYY date") from exc
    if parsed_date.strftime(RELEASE_DATE_FORMAT) != release_date:
        raise ValueError("release date must use DD-MM-YYYY format")
    return release_date


def _table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def release_notes_refresh_proposal(
    solution: Path,
    *,
    version: str | None,
    release_date: str | None = None,
    change_history: str,
    today: date | None = None,
) -> tuple[Path, str, str, str]:
    """Validate ReleaseNotes.md and compute the expected single-row refresh digest."""
    if not version or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("current solution package version must use X.Y.Z format")
    resolved_date = resolve_release_date(release_date, today=today)
    if (
        not change_history.strip()
        or "|" in change_history
        or "\n" in change_history
        or "\r" in change_history
    ):
        raise ValueError("release history must be one non-empty Markdown table cell")
    path = solution / "ReleaseNotes.md"
    if not path.is_file():
        raise ValueError("solution ReleaseNotes.md is missing")
    original = path.read_bytes()
    try:
        text = original.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("ReleaseNotes.md must be UTF-8") from exc
    lines = text.splitlines(keepends=True)

    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if _table_cells(line) == EXPECTED_RELEASE_NOTES_HEADER
        ),
        None,
    )
    if header_index is None or header_index + 1 >= len(lines):
        raise ValueError("ReleaseNotes.md does not have the required three-column table header")
    separator_cells = _table_cells(lines[header_index + 1])
    if (
        separator_cells is None
        or len(separator_cells) != 3
        or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in separator_cells)
    ):
        raise ValueError("ReleaseNotes.md table separator is invalid")

    versions: list[tuple[int, int, int]] = []
    seen: set[str] = set()
    for line in lines[header_index + 2:]:
        stripped = line.strip()
        if not stripped:
            continue
        cells = _table_cells(line)
        if cells is None or len(cells) != 3:
            raise ValueError("ReleaseNotes.md contains a row that is not exactly three columns")
        if not cells[0]:
            continue
        if not re.fullmatch(r"\d+\.\d+\.\d+", cells[0]):
            raise ValueError("ReleaseNotes.md contains an invalid semantic version")
        if cells[0] in seen:
            raise ValueError("ReleaseNotes.md contains a duplicate version")
        seen.add(cells[0])
        try:
            date_value = datetime.strptime(cells[1], RELEASE_DATE_FORMAT)
        except ValueError as exc:
            raise ValueError("ReleaseNotes.md contains an invalid DD-MM-YYYY date") from exc
        if date_value.strftime(RELEASE_DATE_FORMAT) != cells[1] or not cells[2]:
            raise ValueError("ReleaseNotes.md contains an invalid date or empty change history")
        versions.append(tuple(int(part) for part in cells[0].split(".")))
    if versions != sorted(versions, reverse=True):
        raise ValueError("ReleaseNotes.md versions are not in descending order")
    new_version = tuple(int(part) for part in version.split("."))
    if version in seen or (versions and new_version <= versions[0]):
        raise ValueError(
            "same-release notes refresh requires the current package version to be absent "
            "and newer than the existing release notes"
        )

    newline = "\r\n" if "\r\n" in text else "\n"
    row = f"| {version} | {resolved_date} | {change_history.strip()} |{newline}"
    updated_lines = lines[:header_index + 2] + [row] + lines[header_index + 2:]
    updated = "".join(updated_lines)
    if not text.endswith(("\n", "\r")) and updated.endswith(("\n", "\r")):
        updated = updated.rstrip("\r\n")
    return (
        path,
        hashlib.sha256(original).hexdigest(),
        hashlib.sha256(updated.encode("utf-8")).hexdigest(),
        resolved_date,
    )
