from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import yaml


KQL_HELPER = Path(__file__).resolve().parents[1] / "kql" / "rename-parser-bindings.cjs"


def solution_parser_names(solution: Path) -> list[str]:
    names: set[str] = set()
    root = solution / "Parsers"
    for path in sorted([*root.rglob("*.yaml"), *root.rglob("*.yml")]):
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        if not isinstance(document, dict):
            raise ValueError(f"parser must contain a YAML object: {path}")
        if document.get("FunctionName") is None and document.get("FunctionAlias") is None:
            raise ValueError(f"parser must declare FunctionName or FunctionAlias: {path}")
        for field in ("FunctionName", "FunctionAlias"):
            value = document.get(field)
            if value is not None:
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"parser {field} must be a nonempty string: {path}")
                names.add(value.strip())
    return sorted(names)


def normalize_parser_bindings(query: str, solution: Path) -> tuple[str, list[str]]:
    names = solution_parser_names(solution)
    if not names:
        return query, []
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required for scope-aware KQL parser binding normalization.")
    if not (KQL_HELPER.parent / "node_modules" / "@kusto" / "language-service-next").is_dir():
        raise RuntimeError(
            f"KQL dependency is missing; run npm ci --prefix \"{KQL_HELPER.parent}\""
        )
    completed = subprocess.run(
        [node, str(KQL_HELPER)],
        input=json.dumps({"query": query, "reservedNames": names}),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=60,
        check=False,
    )
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or "KQL parser binding normalization failed.")
    result = json.loads(completed.stdout)
    warnings = [
        f"Renamed local parser binding {item['from']} to {item['to']} to avoid a saved parser collision"
        for item in result["renames"]
    ]
    return result["query"], warnings
