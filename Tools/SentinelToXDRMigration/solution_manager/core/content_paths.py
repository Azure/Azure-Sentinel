from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath, PureWindowsPath


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
