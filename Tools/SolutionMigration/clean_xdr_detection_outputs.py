"""Move non-detection artifacts out of solution XDR Detections directories.

Only YAML files with a supported deployable detection shape remain. Reports,
manifests, workflow state, deployment captures, validation evidence, and
migration configuration are moved to the repository-root Reports directory.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Iterable, List

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORTS_ROOT = REPOSITORY_ROOT / "Reports"
DETECTION_DIRECTORY = "XDR Detections"
REPORT_DIRECTORY = "sentinel-xdr-migration"


class CleanupError(RuntimeError):
    """The output layout cannot be cleaned safely."""


def is_detection_yaml(path: Path) -> bool:
    if path.suffix.lower() not in {".yaml", ".yml"}:
        return False
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as exc:
        raise CleanupError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(document, dict):
        return False
    if all(document.get(field) for field in ("id", "name", "query")):
        return True
    properties = document.get("properties")
    query_condition = (
        properties.get("queryCondition") if isinstance(properties, dict) else None
    )
    return bool(
        document.get("resourceType") == "Microsoft.Security/detectionRules"
        and isinstance(properties, dict)
        and properties.get("id")
        and properties.get("displayName")
        and isinstance(query_condition, dict)
        and query_condition.get("queryText")
    )


def find_xdr_directories(repository_root: Path) -> Iterable[Path]:
    solutions_root = repository_root / "Solutions"
    if not solutions_root.is_dir():
        return []
    return sorted(
        path
        for path in solutions_root.glob(f"*/{DETECTION_DIRECTORY}")
        if path.is_dir()
    )


def plan_cleanup(repository_root: Path) -> List[dict]:
    plan: List[dict] = []
    for xdr_dir in find_xdr_directories(repository_root):
        solution = xdr_dir.parent.name
        for path in sorted(item for item in xdr_dir.rglob("*") if item.is_file()):
            if is_detection_yaml(path):
                continue
            plan.append({
                "solution": solution,
                "xdrDirectory": xdr_dir,
                "source": path,
                "relativePath": path.relative_to(xdr_dir),
            })
    return plan


def apply_cleanup(
    plan: List[dict],
    reports_root: Path,
) -> dict:
    moved: List[dict] = []
    for item in plan:
        source = item["source"]
        destination = (
            reports_root
            / item["solution"]
            / REPORT_DIRECTORY
            / item["relativePath"]
        )
        if destination.exists():
            raise CleanupError(f"Cleanup destination already exists: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved.append({
            "solution": item["solution"],
            "source": str(source),
            "destination": str(destination),
        })

    xdr_roots = {Path(item["xdrDirectory"]) for item in plan}
    for xdr_root in xdr_roots:
        for directory in sorted(
            (path for path in xdr_root.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            if not any(directory.iterdir()):
                directory.rmdir()

    return {"moved": moved, "movedCount": len(moved)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--reports-root", type=Path, default=DEFAULT_REPORTS_ROOT)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Move files. Without this flag, print the planned changes only.",
    )
    args = parser.parse_args()

    try:
        plan = plan_cleanup(args.repository_root)
        if args.apply:
            result = apply_cleanup(plan, args.reports_root)
        else:
            result = {
                "mode": "dry-run",
                "moveCount": len(plan),
                "moves": [
                    {
                        "solution": item["solution"],
                        "source": str(item["source"]),
                        "relativePath": str(item["relativePath"]),
                    }
                    for item in plan
                ],
            }
    except CleanupError as exc:
        raise SystemExit(str(exc))

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
