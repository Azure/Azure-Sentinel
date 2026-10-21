"""Inline solution-local Sentinel parsers into Custom Detection queries.

Graph refuses to enable a Custom Detection whose query calls a Sentinel workspace
function. Solution parsers are therefore expanded into ``let`` statements; names are
renamed with the KQL binder (rename-free-references.cjs), never by text replacement.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml

from solution_manager.core.content_paths import yaml_files


KQL_HELPER = Path(__file__).resolve().parents[2] / "kql" / "rename-free-references.cjs"
INLINE_PREFIX = "XdrInline"
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def inlining_enabled(config: dict[str, Any] | None) -> bool:
    value = (config or {}).get("inlineSolutionParsers", True)
    if not isinstance(value, bool):
        raise ValueError("inlineSolutionParsers must be true or false")
    return value


def _param_text(parameters: Any, path: Path) -> str | None:
    """Return the KQL parameter list, or None when the parser cannot be inlined."""
    if parameters in (None, []):
        return None
    if not isinstance(parameters, list):
        raise ValueError(f"parser FunctionParams must be a list: {path}")
    parts = []
    for item in parameters:
        if not isinstance(item, dict) or not item.get("Name") or not item.get("Type"):
            raise ValueError(f"parser FunctionParams entries need Name and Type: {path}")
        type_name = str(item["Type"]).strip()
        if type_name.lower().startswith("table"):
            raise ValueError(f"parser has a tabular parameter and cannot be inlined: {path}")
        text = f"{str(item['Name']).strip()}:{type_name}"
        default = item.get("Default")
        if default is not None:
            if isinstance(default, bool):
                default = str(default).lower()
            elif type_name.lower() == "string":
                default = "'" + str(default).replace("\\", "\\\\").replace("'", "\\'") + "'"
            text += f"={default}"
        parts.append(text)
    return ", ".join(parts)


def load_solution_parsers(solution: Path) -> dict[str, dict[str, Any]]:
    """Map every FunctionName/FunctionAlias to its parser record."""
    records: dict[str, dict[str, Any]] = {}
    for path in yaml_files(solution / "Parsers"):
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        if not isinstance(document, dict):
            continue
        names = [
            str(document[field]).strip()
            for field in ("FunctionAlias", "FunctionName")
            if isinstance(document.get(field), str) and document[field].strip()
        ]
        body = document.get("FunctionQuery")
        if not names or not isinstance(body, str) or not body.strip():
            continue
        body = re.sub(r"[;\s]+\Z", "", body.strip())
        record = {
            "alias": names[0],
            "names": names,
            "path": path.relative_to(solution).as_posix(),
            "body": body,
            "params": None,
            "error": None,
        }
        try:
            record["params"] = _param_text(document.get("FunctionParams"), path)
        except ValueError as exc:
            record["error"] = str(exc)
        for name in names:
            records.setdefault(name, record)
    return records


def _rename(query: str, mapping: dict[str, str]) -> tuple[str, list[str]]:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required for scope-aware KQL parser inlining.")
    if not (KQL_HELPER.parent / "node_modules" / "@kusto" / "language-service-next").is_dir():
        raise RuntimeError(f"KQL dependency is missing; run npm ci --prefix \"{KQL_HELPER.parent}\"")
    completed = subprocess.run(
        [node, str(KQL_HELPER)],
        input=json.dumps({"query": query, "mapping": mapping}),
        text=True, encoding="utf-8", capture_output=True, timeout=60, check=False,
    )
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or "KQL parser inlining failed.")
    result = json.loads(completed.stdout)
    return result["query"], result["renamed"]


def _mentions(text: str, names: set[str]) -> set[str]:
    return {word for word in _WORD.findall(text) if word in names}


def inline_solution_parsers(
    query: str,
    solution: Path,
    config: dict[str, Any] | None = None,
) -> tuple[str, list[dict[str, str]], list[str]]:
    """Return (query, inlined parser records, warnings); the query is unchanged if nothing applies."""
    if not inlining_enabled(config):
        return query, [], []
    parsers = load_solution_parsers(solution)
    if not parsers or not _mentions(query, set(parsers)):
        return query, [], []

    # Textual closure of candidate parsers, so names can be allocated before renaming.
    candidates: dict[str, dict[str, Any]] = {}
    pending = _mentions(query, set(parsers))
    while pending:
        name = pending.pop()
        record = parsers[name]
        if record["alias"] in candidates:
            continue
        candidates[record["alias"]] = record
        pending |= _mentions(record["body"], set(parsers)) - {n for r in candidates.values() for n in r["names"]}

    occupied = set(_WORD.findall(query))
    for record in candidates.values():
        occupied |= set(_WORD.findall(record["body"]))
    targets: dict[str, str] = {}
    mapping: dict[str, str] = {}
    for alias, record in sorted(candidates.items()):
        base = INLINE_PREFIX + re.sub(r"[^A-Za-z0-9]", "", alias)
        target, suffix = base, 1
        while target in occupied:
            suffix += 1
            target = f"{base}{suffix}"
        occupied.add(target)
        targets[alias] = target
        for name in record["names"]:
            mapping[name] = target

    warnings: list[str] = []
    rewritten, used_names = _rename(query, mapping)
    used = {parsers[name]["alias"] for name in used_names}
    if not used:
        return query, [], []

    ordered: list[str] = []
    bodies: dict[str, str] = {}
    visiting: set[str] = set()

    def visit(alias: str) -> None:
        if alias in ordered:
            return
        record = candidates[alias]
        if record["error"]:
            raise ValueError(f"cannot inline parser {alias}: {record['error']}")
        if alias in visiting:
            raise ValueError(f"cannot inline parser {alias}: parsers reference each other in a cycle")
        visiting.add(alias)
        body, dependencies = _rename(record["body"], mapping)
        bodies[alias] = body
        for dependency in sorted({parsers[name]["alias"] for name in dependencies}):
            visit(dependency)
        visiting.discard(alias)
        ordered.append(alias)

    for alias in sorted(used):
        visit(alias)

    lets = []
    for alias in ordered:
        record = candidates[alias]
        signature = f"({record['params']})" if record["params"] else "view()"
        lets.append(f"let {targets[alias]} = {signature} {{\n{bodies[alias]}\n}};")
    records = [
        {
            "alias": alias,
            "inlineName": targets[alias],
            "path": candidates[alias]["path"],
            "functionQuerySha256": hashlib.sha256(candidates[alias]["body"].encode("utf-8")).hexdigest(),
        }
        for alias in ordered
    ]
    warnings.extend(
        f"Inlined solution parser {item['alias']} as {item['inlineName']} because Custom Detections cannot call "
        "Sentinel workspace functions"
        for item in records
    )
    return "\n".join(lets) + "\n" + rewritten.strip(), records, warnings
