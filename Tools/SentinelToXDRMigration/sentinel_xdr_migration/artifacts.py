from __future__ import annotations

import os
import shutil
from pathlib import Path


REPORT_FOLDER_NAME = "sentinel-xdr-migration"


def repository_root(solution: str | Path) -> Path:
    root = Path(solution).expanduser().resolve()
    if root.parent.name.lower() == "solutions":
        return root.parent.parent
    return root.parent


def report_directory(
    solution: str | Path,
    *,
    create: bool = False,
) -> Path:
    root = Path(solution).expanduser().resolve()
    configured = os.getenv("AZURE_SENTINEL_REPORTS_ROOT")
    reports_root = (
        Path(configured).expanduser().resolve()
        if configured
        else repository_root(root) / "Reports"
    )
    path = reports_root / root.name / REPORT_FOLDER_NAME
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def artifact_path(
    solution: str | Path,
    name: str,
    *,
    create_parent: bool = False,
) -> Path:
    return report_directory(solution, create=create_parent) / name


def existing_artifact_path(solution: str | Path, name: str) -> Path:
    preferred = artifact_path(solution, name)
    if preferred.exists():
        return preferred
    return Path(solution).expanduser().resolve() / "XDR Detections" / name


def migrate_legacy_artifact(solution: str | Path, name: str) -> Path:
    preferred = artifact_path(solution, name, create_parent=True)
    if preferred.exists():
        return preferred
    legacy = Path(solution).expanduser().resolve() / "XDR Detections" / name
    if legacy.exists():
        shutil.move(str(legacy), str(preferred))
    return preferred
