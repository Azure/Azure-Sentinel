"""Move non-detection artifacts out of solution XDR Detections directories.

Only YAML files with the minimum Analytic Rule/Custom Detection shape remain:
top-level id, name, and query fields. Reports, manifests, workflow state,
deployment captures, validation evidence, and migration configuration are
moved to the repository-root Reports directory.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORTS_ROOT = REPOSITORY_ROOT / "Reports"
DETECTION_DIRECTORY = "XDR Detections"
REQUIRED_YAML_FIELDS = ("id", "name", "query")


class CleanupError(RuntimeError):
    """The output layout cannot be cleaned safely."""


def is_detection_yaml(path: Path) -> bool:
    if path.suffix.lower() != ".yaml":
        return False
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise CleanupError(f"Cannot read {path}: {exc}") from exc
    return all(
        re.search(rf"(?m)^{re.escape(field)}\s*:", text)
        for field in REQUIRED_YAML_FIELDS
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
    *,
    run_id: str | None = None,
) -> dict:
    run_segment = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    moved: List[dict] = []
    for item in plan:
        source = item["source"]
        destination = (
            reports_root
            / item["solution"]
            / "xdr-detection-artifacts"
            / run_segment
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

    return {"runId": run_segment, "moved": moved, "movedCount": len(moved)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--reports-root", type=Path, default=DEFAULT_REPORTS_ROOT)
    parser.add_argument("--run-id")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Move files. Without this flag, print the planned changes only.",
    )
    args = parser.parse_args()

    try:
        plan = plan_cleanup(args.repository_root)
        if args.apply:
            result = apply_cleanup(plan, args.reports_root, run_id=args.run_id)
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
