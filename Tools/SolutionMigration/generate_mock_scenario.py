"""Generate a shared AR/CD mock payload from Azure-Sentinel repository content.

The tool is standalone within Azure-Sentinel. It reads a source Analytic Rule,
the converted Custom Detection, checked-in Standard-table base events, and the
solution package's DCR/transform/parser definitions. It never writes to Azure.

Existing valid scenarios are reused by default. Automatic generation is limited
to simple decisive predicates. Complex behavior requires a reviewed scenario
JSON containing maliciousRecords and benignRecords. Only the malicious records
are persisted as mock.json for the shared one-time AR/CD ingestion. Benign
records remain validation controls and are not a second ingestion payload.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TABLE_ROOT = REPOSITORY_ROOT / "Sample Data" / "Tables"
MOCK_ROOT = REPOSITORY_ROOT / "Sample Data" / "Solutions" / "Mock"
STANDARD_CONTRACT_ROOT = (
    REPOSITORY_ROOT / "Tools" / "AzureMonitorLogsIngestion" / "contracts"
)
INGESTION_TOOL_ROOT = REPOSITORY_ROOT / "Tools" / "AzureMonitorLogsIngestion"
if str(INGESTION_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(INGESTION_TOOL_ROOT))
from azure_monitor_logs_ingestion.registry import (
    find_capability,
    resolve_contract as resolve_registered_contract,
)

SCENARIO_VERSION = 1
SUPPORTED_TYPES = {"string", "datetime", "dynamic", "bool", "boolean", "int", "long", "real", "double"}


class ScenarioError(RuntimeError):
    """A scenario cannot be generated or reused safely."""


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unnamed"


def _resolved_directory(path: Path, label: str, *, required: bool = False) -> Path:
    path = Path(path).expanduser()
    if path.is_symlink():
        raise ScenarioError(f"{label} must not be a symlink: {path}")
    resolved = path.resolve()
    if required and not resolved.is_dir():
        raise ScenarioError(f"{label} is not a directory: {resolved}")
    if resolved.exists() and not resolved.is_dir():
        raise ScenarioError(f"{label} is not a directory: {resolved}")
    return resolved


def _reject_symlink_path(path: Path, label: str) -> Path:
    path = Path(path).expanduser()
    if path.is_symlink():
        raise ScenarioError(f"{label} must not be a symlink: {path}")
    return path.resolve()


def _assert_no_symlink_below(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    absolute_path = path.absolute()
    try:
        relative = absolute_path.relative_to(root)
    except ValueError:
        relative = None
    if relative is not None:
        current = root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise ScenarioError(f"Symlink {label} paths are not supported: {current}")
    resolved_path = path.resolve()
    if not resolved_path.is_relative_to(root):
        raise ScenarioError(f"{label} escapes its root {root}: {path}")
    return resolved_path


def _solution_directory(source_root: Path, solution: str) -> Path:
    if solution in {"", ".", ".."} or "/" in solution or "\\" in solution:
        raise ScenarioError("Solution must be a single folder name.")
    root = source_root / "Solutions"
    if root.is_symlink():
        raise ScenarioError(f"Symlink solution paths are not supported: {root}")
    directory = root / solution
    if directory.is_symlink():
        raise ScenarioError(f"Symlink solution paths are not supported: {directory}")
    _assert_no_symlink_below(root, directory, "solution")
    if not directory.is_dir():
        raise ScenarioError(f"Solution folder was not found: {directory}")
    return directory


def _source_file(selector: str, source_root: Path, label: str) -> Optional[Path]:
    supplied = Path(selector).expanduser()
    candidate = supplied if supplied.is_absolute() else source_root / supplied
    if not candidate.is_file():
        return None
    solution_root = source_root.resolve()
    resolved = _assert_no_symlink_below(solution_root, candidate, label)
    if not resolved.is_file():
        return None
    return resolved


def _load_yaml(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as exc:
        raise ScenarioError(f"Cannot read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ScenarioError(f"YAML file must contain an object: {path}")
    return value


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScenarioError(f"Cannot read JSON {path}: {exc}") from exc


def _query(document: dict) -> str:
    for key in ("query", "customDetectionQuery", "queryCondition"):
        value = document.get(key)
        if isinstance(value, str) and value.strip():
            return value
    properties = document.get("properties")
    if isinstance(properties, dict):
        condition = properties.get("queryCondition")
        if isinstance(condition, dict):
            value = condition.get("queryText")
            if isinstance(value, str) and value.strip():
                return value
    raise ScenarioError("The content file does not contain a query.")


def _detection_property(document: dict, name: str) -> Any:
    value = document.get(name)
    if value is not None:
        return value
    properties = document.get("properties")
    return properties.get(name) if isinstance(properties, dict) else None


def _detection_source_id(document: dict) -> str:
    for key in ("sourceId", "sourceRuleId", "analyticRuleId"):
        value = document.get(key)
        if value:
            return str(value)
    source = (document.get("contentProvenance") or {}).get("source") or {}
    return str(source.get("id") or "")


def _content_yaml_files(folder: Path) -> List[Path]:
    if folder.is_symlink():
        raise ScenarioError(f"Symlink content paths are not supported: {folder}")
    files = []
    for path in folder.rglob("*"):
        if any(part.lower() in {"logs", "reports"} for part in path.relative_to(folder).parts):
            continue
        if path.is_symlink():
            raise ScenarioError(f"Symlink content paths are not supported: {path}")
        if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}:
            if not path.resolve().is_relative_to(folder.resolve()):
                raise ScenarioError(f"Content path escapes its root: {path}")
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(folder).as_posix())


def find_analytic_rule(
    solution: str,
    selector: str,
    source_root: Optional[Path] = None,
) -> Tuple[Path, dict]:
    source_root = Path(source_root or REPOSITORY_ROOT).resolve()
    supplied = _source_file(selector, source_root, "Analytic Rule")
    if supplied:
        return supplied, _load_yaml(supplied)

    candidates: List[Tuple[Path, dict]] = []
    solution_root = _solution_directory(source_root, solution)
    for folder_name in ("Analytic Rules", "Analytics Rules"):
        folder = solution_root / folder_name
        if not folder.is_dir():
            continue
        for path in _content_yaml_files(folder):
            rule = _load_yaml(path)
            if (
                selector == str(rule.get("id"))
                or selector == str(rule.get("name"))
                or selector == path.name
                or selector == path.stem
                or selector.replace("\\", "/") == path.relative_to(folder).as_posix()
                or selector.replace("\\", "/") == path.relative_to(solution_root).as_posix()
            ):
                candidates.append((path, rule))
    if not candidates:
        raise ScenarioError(
            f"Analytic Rule {selector!r} was not found under solution {solution!r}."
        )
    if len(candidates) > 1:
        raise ScenarioError(f"Analytic Rule selector {selector!r} is ambiguous.")
    return candidates[0]


def find_custom_detection(
    solution: str,
    selector: Optional[str],
    source_rule: dict,
    source_root: Optional[Path] = None,
) -> Tuple[Path, dict]:
    source_root = Path(source_root or REPOSITORY_ROOT).resolve()
    supplied = _source_file(selector, source_root, "Custom Detection") if selector else None
    if supplied:
        return supplied, _load_yaml(supplied)

    folder = _solution_directory(source_root, solution) / "XDR Detections"
    if not folder.is_dir():
        raise ScenarioError(
            f"Converted Custom Detection folder does not exist: {folder}. "
            "Run the conversion stage before generating rule-specific mock data."
        )

    source_id = str(source_rule.get("id") or "")
    source_name = str(source_rule.get("name") or "")
    matches: List[Tuple[Path, dict]] = []
    for path in _content_yaml_files(folder):
        if path.name.lower() in {"migration-config.yaml", "migration-config.yml"}:
            continue
        detection = _load_yaml(path)
        identifiers = {
            _detection_source_id(detection),
            str(_detection_property(detection, "displayName") or ""),
            str(_detection_property(detection, "name") or ""),
            path.name,
            path.stem,
            path.relative_to(folder).as_posix(),
            path.relative_to(folder.parent).as_posix(),
        }
        wanted = selector.replace("\\", "/") if selector else source_id or source_name
        if wanted in identifiers:
            matches.append((path, detection))
    if not matches:
        raise ScenarioError(
            f"No converted Custom Detection matched Analytic Rule {source_name!r} in {folder}."
        )
    if len(matches) > 1:
        raise ScenarioError(
            f"Multiple Custom Detections matched Analytic Rule {source_name!r}; "
            "pass --custom-detection with an exact path."
        )
    return matches[0]


def scenario_directory(
    solution: str,
    rule: dict,
    output_root: Optional[Path] = None,
) -> Path:
    if solution in {"", ".", ".."} or "/" in solution or "\\" in solution:
        raise ScenarioError("Solution must be a single folder name.")
    rule_id = _safe_name(str(rule.get("id") or rule.get("name") or "rule"))
    root = _resolved_directory(output_root or MOCK_ROOT, "Output root")
    return root / solution / rule_id


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def validate_existing_scenario(
    path: Path,
    solution: str,
    rule: dict,
    rule_path: Path,
    detection: dict,
    detection_path: Path,
    registry_path: Optional[Path] = None,
    scenario_input: Optional[Path] = None,
    scenario_input_kind: Optional[str] = None,
    scenario_input_hash: Optional[str] = None,
) -> dict:
    scenario_path = path / "scenario.json"
    mock_path = path / "mock.json"
    if not all(candidate.is_file() for candidate in (scenario_path, mock_path)):
        raise ScenarioError(f"Existing scenario folder is incomplete: {path}")
    scenario = _load_json(scenario_path)
    mock_records = _load_json(mock_path)
    if not isinstance(scenario, dict):
        raise ScenarioError(f"Scenario manifest must be an object: {scenario_path}")
    if scenario.get("solution") != solution:
        raise ScenarioError(f"Scenario solution does not match {solution!r}: {scenario_path}")
    if str(scenario.get("ruleId")) != str(rule.get("id")):
        raise ScenarioError(f"Scenario rule ID does not match the selected rule: {scenario_path}")
    expected_hashes = {
        "analyticRuleFileSha256": _sha256_bytes(rule_path.read_bytes()),
        "analyticRuleQuerySha256": _sha256_bytes(_query(rule).encode("utf-8")),
        "customDetectionFileSha256": _sha256_bytes(detection_path.read_bytes()),
        "customDetectionQuerySha256": _sha256_bytes(
            _query(detection).encode("utf-8")
        ),
    }
    if scenario.get("sourceHashes") != expected_hashes:
        raise ScenarioError(
            "Existing scenario source hashes are stale or absent; review and "
            "regenerate it before reuse."
        )
    stored_scenario_review = scenario.get("scenarioReview") or {}
    if scenario_input:
        if (
            stored_scenario_review.get("inputKind") != scenario_input_kind
            or stored_scenario_review.get("inputSha256") != scenario_input_hash
        ):
            raise ScenarioError(
                "Existing scenario input hash or review state does not match the "
                "supplied scenario input; regenerate only after reviewing the prior fixture."
            )
        expected_review_status = (
            "review-pending" if scenario_input_kind == "candidate" else "reviewed"
        )
        if stored_scenario_review.get("status") != expected_review_status:
            raise ScenarioError(
                "Existing scenario review status does not match the supplied input."
            )
    stored_resolution = (scenario.get("ingestion") or {}).get("contractResolution") or {}
    if stored_resolution.get("schemaFingerprint"):
        if not registry_path or not Path(registry_path).is_file():
            raise ScenarioError(
                "The toolkit registry required to verify this scenario is missing."
            )
        current_resolution = resolve_registered_contract(
            str(scenario.get("sourceTable") or ""),
            registry_path=registry_path or STANDARD_CONTRACT_ROOT.parent / "registry.yaml",
        )
        if (
            stored_resolution.get("schemaFingerprint")
            != current_resolution.get("schemaFingerprint")
            or stored_resolution.get("transformFingerprint")
            != current_resolution.get("transformFingerprint")
        ):
            raise ScenarioError(
                "Existing scenario contract fingerprints are stale; review and "
                "regenerate it before reuse."
            )
    if not isinstance(mock_records, list) or not mock_records:
        raise ScenarioError(f"Mock payload must be a non-empty array: {mock_path}")
    validation = scenario.get("validation") or {}
    if validation.get("schemaValidation") != "passed":
        raise ScenarioError(f"Existing scenario has not passed schema validation: {scenario_path}")
    return {
        "status": "existing-scenario",
        "scenarioPath": str(scenario_path),
        "mockPath": str(mock_path),
        "scenario": scenario,
    }


def _walk_resources(resources: Sequence[dict]) -> Iterable[dict]:
    for resource in resources:
        if not isinstance(resource, dict):
            continue
        yield resource
        nested = resource.get("resources")
        if isinstance(nested, list):
            yield from _walk_resources(nested)
        properties = resource.get("properties") or {}
        for template_key in ("template", "mainTemplate"):
            template = properties.get(template_key) or {}
            if isinstance(template, dict):
                yield from _walk_resources(template.get("resources") or [])


def load_solution_contract(solution: str, source_root: Optional[Path] = None) -> dict:
    source_root = Path(source_root or REPOSITORY_ROOT).resolve()
    solution_root = _solution_directory(source_root, solution)
    package = solution_root / "Package" / "mainTemplate.json"
    _assert_no_symlink_below(solution_root, package, "solution package")
    if not package.is_file():
        raise ScenarioError(f"Solution package was not found: {package}")
    template = _load_json(package)
    dcrs: List[dict] = []
    tables: Dict[str, List[dict]] = {}
    for resource in _walk_resources(template.get("resources") or []):
        resource_type = str(resource.get("type") or "").lower()
        properties = resource.get("properties") or {}
        if resource_type == "microsoft.insights/datacollectionrules":
            dcrs.append({
                "name": resource.get("name"),
                "streamDeclarations": properties.get("streamDeclarations") or {},
                "dataFlows": properties.get("dataFlows") or [],
            })
        elif resource_type == "microsoft.operationalinsights/workspaces/tables":
            raw_name = str(resource.get("name") or "").split("/")[-1].strip("[]'\"")
            schema = properties.get("schema") or {}
            if raw_name and isinstance(schema.get("columns"), list):
                tables[raw_name] = schema["columns"]

    parsers: Dict[str, str] = {}
    parser_root = solution_root / "Parsers"
    if parser_root.is_dir():
        for path in _content_yaml_files(parser_root):
            document = _load_yaml(path)
            alias = document.get("FunctionAlias") or document.get("FunctionName")
            query = document.get("FunctionQuery")
            if alias and isinstance(query, str):
                parsers[str(alias)] = query
    return {"package": package, "dcrs": dcrs, "tables": tables, "parsers": parsers}


def _split_top_level(text: str, separators: str = ",") -> List[str]:
    output: List[str] = []
    current: List[str] = []
    depth = 0
    quote: Optional[str] = None
    for char in text:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        if char in separators and depth == 0:
            output.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        output.append("".join(current))
    return output


_ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", re.S)
_STAGE_RE = re.compile(r"^\s*(extend|project-rename|project)\s+(.*)$", re.I | re.S)
_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
_CAST_RE = re.compile(
    r"^to(?:string|int|long|real|double|bool|datetime|dynamic)\(\s*(.+)\s*\)$",
    re.I | re.S,
)
_COLUMN_IF_EXISTS_RE = re.compile(
    r"^column_ifexists\(\s*['\"]([^'\"]+)['\"]\s*,.+\)$",
    re.I | re.S,
)


def _assignments(kql: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    project: Dict[str, str] = {}
    extend: Dict[str, str] = {}
    for segment in _split_top_level(kql, separators="|;"):
        match = _STAGE_RE.match(segment)
        if not match:
            continue
        target = extend if match.group(1).lower() == "extend" else project
        for item in _split_top_level(match.group(2)):
            item = item.strip()
            assignment = _ASSIGNMENT_RE.match(item)
            if assignment:
                target[assignment.group(1)] = assignment.group(2).strip()
            elif _NAME_RE.match(item):
                target[item] = item
    return project, extend


def _resolve_expression(
    expression: str,
    value: Any,
    project: Dict[str, str],
    extend: Dict[str, str],
    seen: Optional[set] = None,
) -> Tuple[str, Any]:
    seen = seen or set()
    expression = expression.strip()
    cast = _CAST_RE.match(expression)
    if cast:
        return _resolve_expression(cast.group(1), value, project, extend, seen)
    column_if_exists = _COLUMN_IF_EXISTS_RE.match(expression)
    if column_if_exists:
        return column_if_exists.group(1), value
    if _NAME_RE.match(expression):
        if expression in seen:
            return expression, value
        seen.add(expression)
        next_expression = project.get(expression, extend.get(expression, expression))
        if next_expression != expression:
            return _resolve_expression(next_expression, value, project, extend, seen)
        return expression, value
    raise ScenarioError(f"Expression cannot be reverse-mapped safely: {expression}")


def resolve_column(kql: str, column: str, value: Any) -> Tuple[str, Any]:
    project, extend = _assignments(kql)
    expression = project.get(column, extend.get(column, column))
    return _resolve_expression(expression, value, project, extend)


_EQUALITY_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_.]*)\s*(==|=~|!=|!~|>=|<=|>|<)\s*"
    r"(datetime\([^)]*\)|['\"][^'\"]*['\"]|-?\d+(?:\.\d+)?|true|false)",
    re.I,
)
_ISEMPTY_RE = re.compile(r"\b(isempty|isnotempty)\(\s*([A-Za-z_][A-Za-z0-9_.]*)\s*\)", re.I)
_IN_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_.]*)\s+(in~?|has_any)\s*\(([^)]*)\)",
    re.I,
)
_DYNAMIC_LIST_LET_RE = re.compile(
    r"\blet\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*dynamic\s*\(\s*\[([^\]]*)\]\s*\)\s*;",
    re.I,
)


def _literal(raw: str) -> Any:
    value = raw.strip()
    if value.lower().startswith("datetime("):
        return value[value.find("(") + 1:value.rfind(")")].strip("'\"")
    if value[:1] in {"'", '"'} and value[-1:] == value[:1]:
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def extract_predicates(kql: str) -> List[dict]:
    predicates: List[dict] = []
    dynamic_lists = {
        match.group(1): [
            _literal(item)
            for item in _split_top_level(match.group(2))
            if item.strip()
        ]
        for match in _DYNAMIC_LIST_LET_RE.finditer(kql)
    }
    for match in _EQUALITY_RE.finditer(kql):
        predicates.append({
            "column": match.group(1),
            "operator": match.group(2),
            "value": _literal(match.group(3)),
        })
    for match in _ISEMPTY_RE.finditer(kql):
        predicates.append({
            "column": match.group(2),
            "operator": match.group(1).lower(),
            "value": "" if match.group(1).lower() == "isempty" else "synthetic-present",
        })
    for match in _IN_RE.finditer(kql):
        raw_values = match.group(3).strip()
        values = dynamic_lists.get(raw_values)
        if values is None:
            values = [
                _literal(item)
                for item in _split_top_level(raw_values)
                if item.strip()
            ]
        if values:
            predicates.append({
                "column": match.group(1),
                "operator": match.group(2).lower(),
                "value": values[0],
            })
    unique: List[dict] = []
    seen = set()
    for predicate in predicates:
        key = (predicate["column"], predicate["operator"], repr(predicate["value"]))
        if key not in seen:
            seen.add(key)
            unique.append(predicate)
    return unique


def assess_query(query: str, rule: dict) -> dict:
    lower = query.lower()
    reasons: List[str] = []
    if str(rule.get("triggerOperator") or "").lower() == "equal" and rule.get("triggerThreshold") == 0:
        return {
            "status": "unsupported-payload",
            "reasons": ["The rule triggers on zero matching rows."],
        }
    checks = (
        (r"\|\s*join\b|\bunion\b", "The query correlates multiple result sets."),
        (r"\b(dcount|countif|make_set|make_list)\s*\(", "The query requires aggregation."),
        (r"\bsummarize\b", "The query summarizes multiple events."),
        (r"_getwatchlist|externaldata", "The query depends on external reference data."),
        (r"\bseries_|anomal", "The query depends on anomaly or baseline behavior."),
        (
            r"\bparse_xml\s*\(|\bparse_json\s*\(|\|\s*mv-expand\b|"
            r"\|\s*evaluate\s+(?:bag_unpack|pivot)\b",
            "The query parses or expands structured event content.",
        ),
        (
            r"\b(?:contains|has_all|has_any|has|startswith|endswith|matches\s+regex)\b",
            "The query uses a content predicate that automatic fixtures do not model.",
        ),
    )
    for pattern, reason in checks:
        if re.search(pattern, lower):
            reasons.append(reason)
    return {
        "status": "manual-review-required" if reasons else "simple",
        "reasons": reasons,
    }


def _first_query_source(query: str) -> Optional[str]:
    without_lets = re.sub(r"(?is)\blet\s+.*?;", "", query)
    match = re.search(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\||$)", without_lets)
    return match.group(1) if match else None


def _table_from_stream(stream: str) -> str:
    value = stream
    for prefix in ("Custom-", "Microsoft-"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value


def _load_table_base(
    table: str,
    table_root: Optional[Path] = None,
) -> Tuple[dict, Dict[str, str]]:
    if table in {"", ".", ".."} or "/" in table or "\\" in table:
        raise ScenarioError(f"Invalid source table name: {table!r}")
    table_root = Path(table_root or TABLE_ROOT).resolve()
    folder = table_root / table
    _assert_no_symlink_below(table_root, folder, "table sample")
    base_path = folder / "base-event.json"
    metadata_path = folder / "metadata.json"
    if not base_path.is_file() or not metadata_path.is_file():
        raise ScenarioError(
            f"Neutral base event was not found for table {table!r} under {table_root}."
        )
    _assert_no_symlink_below(table_root, base_path, "table sample")
    _assert_no_symlink_below(table_root, metadata_path, "table sample")
    base = _load_json(base_path)
    metadata = _load_json(metadata_path)
    columns = metadata.get("columns") if isinstance(metadata, dict) else None
    if not isinstance(base, dict) or not isinstance(columns, dict):
        raise ScenarioError(f"Invalid table base contract for {table!r}.")
    return base, {str(name): str(kind) for name, kind in columns.items()}


def _load_standard_ingestion_contract(
    table: str,
    registry_path: Optional[Path] = None,
) -> Optional[dict]:
    registry_path = registry_path or STANDARD_CONTRACT_ROOT.parent / "registry.yaml"
    if not Path(registry_path).is_file():
        return None
    capability = find_capability(table, registry_path)
    if capability is None:
        return None
    value = _load_yaml(capability.contract_path)
    destination = value.get("destination") or {}
    if (
        value.get("version") != 1
        or destination.get("kind") != "standard"
        or destination.get("table") != capability.table
        or destination.get("outputStream") != capability.output_stream
        or not str(value.get("inputStream") or "").startswith("Custom-")
    ):
        raise ScenarioError(
            f"Registered standard-table contract does not match {table!r}: "
            f"{capability.contract_path}"
        )
    return value


def _query_fields_from_schema(query: str, schema: Dict[str, str]) -> Dict[str, str]:
    """Extract only exact schema identifiers; this is not a general KQL parser."""
    required: Dict[str, str] = {}
    aliases = _query_output_aliases(query)
    for name, kind in schema.items():
        if name.casefold() in aliases:
            continue
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", query, re.I):
            required[name] = kind
    return required


def _query_output_aliases(query: str) -> set[str]:
    project, extend = _assignments(query)
    aliases = set()
    for name, expression in {**project, **extend}.items():
        if expression.strip().casefold() != name.casefold():
            aliases.add(name.casefold())
    return aliases


def _query_predicate_fields(
    query: str,
    schema: Dict[str, str],
) -> Tuple[Dict[str, Optional[str]], List[str]]:
    """Resolve simple predicate identifiers without treating query aliases as source fields."""
    aliases = _query_output_aliases(query)
    schema_names = {name.casefold(): name for name in schema}
    required: Dict[str, Optional[str]] = {}
    unresolved_aliases: List[str] = []
    for predicate in extract_predicates(query):
        field = str(predicate["column"])
        if field.casefold() in aliases:
            if field not in unresolved_aliases:
                unresolved_aliases.append(field)
            continue
        canonical_name = schema_names.get(field.casefold(), field)
        required[canonical_name] = schema.get(canonical_name)
    return required, unresolved_aliases


def _default_value(kind: str) -> Any:
    normalized = kind.lower()
    if normalized == "datetime":
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if normalized in {"int", "long"}:
        return 0
    if normalized in {"real", "double"}:
        return 0.0
    if normalized in {"bool", "boolean"}:
        return False
    if normalized == "dynamic":
        return {}
    return ""


def _set_path(record: dict, path: str, value: Any) -> None:
    parts = path.split(".")
    node = record
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def _get_path(record: dict, path: str) -> Any:
    node: Any = record
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise ScenarioError(f"Field path {path!r} does not exist.")
        node = node[part]
    return node


def _benign_value(value: Any, operator: str) -> Any:
    if operator == "isnotempty":
        return ""
    if operator == "isempty":
        return "synthetic-benign"
    if isinstance(value, bool):
        return not value
    if isinstance(value, int) and not isinstance(value, bool):
        return value + 1
    if isinstance(value, float):
        return value + 1.0
    if isinstance(value, str):
        return "__benign_non_match__"
    raise ScenarioError("A type-safe benign value could not be inferred.")


def _find_custom_stream(
    contract: dict,
    source_name: Optional[str],
    predicates: Sequence[dict],
    *,
    allow_unmapped: bool = False,
) -> Optional[dict]:
    parser_query = (contract.get("parsers") or {}).get(source_name or "")
    parser_table = _first_query_source(parser_query) if parser_query else None
    matches = []
    for dcr in contract.get("dcrs") or []:
        declarations = dcr.get("streamDeclarations") or {}
        for flow in dcr.get("dataFlows") or []:
            transform = str(flow.get("transformKql") or "")
            for stream in flow.get("streams") or []:
                if stream not in declarations or not stream.startswith("Custom-"):
                    continue
                if not predicates and (
                    not allow_unmapped
                    or not parser_table
                    or _table_from_stream(stream) != parser_table
                ):
                    continue
                mappings = []
                success = True
                for predicate in predicates:
                    column = predicate["column"]
                    value = predicate["value"]
                    try:
                        intermediate, value = (
                            resolve_column(parser_query, column, value)
                            if parser_query
                            else (column, value)
                        )
                        raw_path, raw_value = resolve_column(transform, intermediate, value)
                    except ScenarioError:
                        success = False
                        break
                    if raw_path.split(".")[0] not in {
                        item["name"] for item in declarations[stream].get("columns") or []
                    }:
                        success = False
                        break
                    mappings.append((predicate, raw_path, raw_value))
                if success and (mappings or not predicates):
                    matches.append({
                        "dcr": dcr.get("name"),
                        "stream": stream,
                        "outputStream": flow.get("outputStream") or stream,
                        "transformKql": transform,
                        "columns": declarations[stream].get("columns") or [],
                        "mappings": mappings,
                    })
    if len(matches) > 1:
        raise ScenarioError(
            f"Multiple custom DCR input streams match parser {source_name!r}; "
            "the reviewed fixture route is ambiguous."
        )
    if matches:
        return matches[0]
    return None


def _find_standard_table(
    query: str,
    custom_detection_query: str,
    source_name: Optional[str],
    table_root: Optional[Path] = None,
) -> str:
    table_root = Path(table_root or TABLE_ROOT).resolve()
    candidates = [source_name, _first_query_source(custom_detection_query)]
    for candidate in candidates:
        if candidate and (table_root / candidate / "base-event.json").is_file():
            return candidate
    tokens = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", f"{query}\n{custom_detection_query}"))
    for path in sorted(table_root.iterdir()):
        if path.name in tokens and (path / "base-event.json").is_file():
            return path.name
    raise ScenarioError("No checked-in Standard-table base event matched the AR/CD queries.")


def _validate_value(value: Any, kind: str) -> bool:
    normalized = kind.lower()
    if value is None:
        return True
    if normalized == "string":
        return isinstance(value, str)
    if normalized == "datetime":
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False
    if normalized == "dynamic":
        return isinstance(value, (dict, list, str, int, float, bool))
    if normalized in {"bool", "boolean"}:
        return isinstance(value, bool)
    if normalized in {"int", "long"}:
        return isinstance(value, int) and not isinstance(value, bool)
    if normalized in {"real", "double"}:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return normalized in SUPPORTED_TYPES


def validate_records(records: Sequence[dict], columns: Dict[str, str]) -> None:
    for index, record in enumerate(records):
        unknown = sorted(set(record) - set(columns))
        if unknown:
            raise ScenarioError(
                f"Record {index} contains fields absent from the schema: {', '.join(unknown)}"
            )
        for name, value in record.items():
            if not _validate_value(value, columns[name]):
                raise ScenarioError(
                    f"Record {index} field {name!r} is invalid for type {columns[name]!r}."
                )


def _parse_assignment(raw: str) -> Tuple[str, Any]:
    if "=" not in raw:
        raise ScenarioError(f"Expected PATH=VALUE, got {raw!r}.")
    path, value = raw.split("=", 1)
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value
    return path.strip(), parsed


def _leaf_paths(value: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(value, dict):
        for name, child in value.items():
            path = f"{prefix}.{name}" if prefix else name
            yield from _leaf_paths(child, path)
    else:
        yield prefix, value


def _randomized_value(
    path: str,
    value: Any,
    rng: random.Random,
    index: int,
    declared_type: Optional[str] = None,
) -> Any:
    name = path.rsplit(".", 1)[-1].lower()
    normalized_type = (declared_type or "").lower()
    if normalized_type == "datetime":
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif isinstance(value, datetime):
            parsed = value
        else:
            raise ScenarioError(f"Cannot randomize non-datetime value at {path!r}.")
        return (parsed + timedelta(seconds=rng.randint(1, 86400) + index)).isoformat()
    if normalized_type in {"int", "long"}:
        return rng.randint(1, 65535)
    if normalized_type in {"real", "double"}:
        return round(rng.uniform(1.0, 1000.0), 3)
    if normalized_type in {"bool", "boolean"}:
        return bool(rng.getrandbits(1))
    if normalized_type == "dynamic":
        return value
    if isinstance(value, bool):
        return bool(rng.getrandbits(1))
    if isinstance(value, int) and not isinstance(value, bool):
        return rng.randint(1, 65535)
    if isinstance(value, float):
        return round(rng.uniform(1.0, 1000.0), 3)
    if not isinstance(value, str):
        return value
    if re.search(r"(time|date|timestamp)", name):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return (parsed + timedelta(seconds=rng.randint(1, 86400) + index)).isoformat()
    if "ip" in name:
        return f"192.0.2.{rng.randint(1, 254)}"
    if "email" in name or name.endswith("upn"):
        return f"synthetic-{rng.randint(1000, 9999)}@example.invalid"
    if re.search(r"(id|guid|session|request|correlation)", name):
        return str(uuid.UUID(int=rng.getrandbits(128)))
    return f"synthetic-{rng.randint(1000, 9999)}"


def randomized_copies(
    records: Sequence[dict],
    copies: int,
    seed: int,
    locked_paths: Sequence[str],
    column_types: Optional[Dict[str, str]] = None,
) -> List[dict]:
    if copies < 1:
        raise ScenarioError("--copies must be at least 1.")
    output: List[dict] = []
    for copy_index in range(copies):
        for source_index, source in enumerate(records):
            record = copy.deepcopy(source)
            rng = random.Random(f"{seed}:{copy_index}:{source_index}")
            for path, value in list(_leaf_paths(record)):
                locked = any(
                    path == item
                    or path.startswith(f"{item}.")
                    or item.startswith(f"{path}.")
                    for item in locked_paths
                )
                if path and not locked:
                    declared_type = (column_types or {}).get(path.split(".", 1)[0])
                    _set_path(
                        record,
                        path,
                        _randomized_value(
                            path,
                            value,
                            rng,
                            copy_index,
                            declared_type,
                        ),
                    )
            output.append(record)
    return output


def load_reviewed_scenario(path: Path) -> dict:
    scenario = _load_json(path)
    if not isinstance(scenario, dict):
        raise ScenarioError("Scenario input must be a JSON object.")
    for field in ("name", "hypothesis"):
        if not isinstance(scenario.get(field), str) or not scenario[field].strip():
            raise ScenarioError(f"Scenario input requires {field}.")
    for field in ("maliciousRecords", "benignRecords"):
        records = scenario.get(field)
        if not isinstance(records, list) or not records or not all(
            isinstance(record, dict) for record in records
        ):
            raise ScenarioError(f"Scenario input requires non-empty {field}.")
    locks = scenario.get("lockedPaths") or []
    if not isinstance(locks, list) or not all(isinstance(item, str) for item in locks):
        raise ScenarioError("lockedPaths must be an array of strings.")
    return scenario


def generate_scenario(
    solution: str,
    rule_selector: str,
    *,
    custom_detection_selector: Optional[str] = None,
    force: bool = False,
    reviewed_scenario: Optional[Path] = None,
    candidate_scenario: Optional[Path] = None,
    randomize: bool = False,
    copies: int = 1,
    seed: int = 20260917,
    locks: Sequence[Tuple[str, Any]] = (),
    benign_assignments: Sequence[Tuple[str, Any]] = (),
    source_root: Optional[Path] = None,
    toolkit_root: Optional[Path] = None,
    sample_data_root: Optional[Path] = None,
    output_root: Optional[Path] = None,
) -> dict:
    if reviewed_scenario and candidate_scenario:
        raise ScenarioError(
            "Pass either --reviewed-scenario or --candidate-scenario, not both."
        )
    scenario_input = reviewed_scenario or candidate_scenario
    scenario_input_kind = (
        "candidate" if candidate_scenario else "reviewed" if reviewed_scenario else None
    )
    if scenario_input:
        scenario_input = _reject_symlink_path(
            Path(scenario_input),
            "Scenario input",
        )
        if not scenario_input.is_file():
            raise ScenarioError(f"Scenario input was not found: {scenario_input}")
    scenario_input_hash = (
        _sha256_bytes(Path(scenario_input).read_bytes()) if scenario_input else None
    )
    source_root = _resolved_directory(
        source_root or REPOSITORY_ROOT,
        "Source repository root",
        required=True,
    )
    if toolkit_root is not None:
        toolkit_root = _resolved_directory(
            toolkit_root,
            "Toolkit root",
            required=True,
        )
        registry_path = toolkit_root / "Tools" / "AzureMonitorLogsIngestion" / "registry.yaml"
        default_sample_data_root = toolkit_root / "Sample Data"
    else:
        toolkit_root = REPOSITORY_ROOT.resolve()
        registry_path = STANDARD_CONTRACT_ROOT.parent / "registry.yaml"
        default_sample_data_root = toolkit_root / "Sample Data"
    sample_data_root_explicit = sample_data_root is not None
    if sample_data_root_explicit:
        sample_data_root = _resolved_directory(
            sample_data_root,
            "Sample data root",
            required=True,
        )
        table_root = sample_data_root / "Tables"
    else:
        sample_data_root = _resolved_directory(
            default_sample_data_root,
            "Sample data root",
        )
    table_root = sample_data_root / "Tables"
    output_root = _resolved_directory(output_root or MOCK_ROOT, "Output root")

    rule_path, rule = find_analytic_rule(solution, rule_selector, source_root)
    output_dir = scenario_directory(solution, rule, output_root)
    _assert_no_symlink_below(output_root, output_dir, "output")
    detection_path, detection = find_custom_detection(
        solution,
        custom_detection_selector,
        rule,
        source_root,
    )
    if output_dir.exists() and force and candidate_scenario:
        prior_manifest = output_dir / "scenario.json"
        prior_scenario = _load_json(prior_manifest) if prior_manifest.is_file() else {}
        prior_review = (
            (prior_scenario.get("scenarioReview") or {}).get("status")
            if isinstance(prior_scenario, dict)
            else None
        )
        if prior_review != "reviewed":
            raise ScenarioError(
                "A review-pending or unreviewed scenario cannot be overwritten with "
                "--force; review the existing fixture first."
            )
    if output_dir.exists() and not force:
        result = validate_existing_scenario(
            output_dir,
            solution,
            rule,
            rule_path,
            detection,
            detection_path,
            registry_path,
            scenario_input=scenario_input,
            scenario_input_kind=scenario_input_kind,
            scenario_input_hash=scenario_input_hash,
        )
        if (
            (result.get("scenario") or {}).get("scenarioReview", {}).get("status")
            == "review-pending"
        ):
            result["status"] = "existing-candidate"
        result["paths"] = {
            "sourceRoot": str(source_root),
            "toolkitRoot": str(toolkit_root),
            "sampleDataRoot": str(sample_data_root),
            "outputRoot": str(output_root),
        }
        return result

    source_query = _query(rule)
    destination_query = _query(detection)
    assessment = assess_query(source_query, rule)
    predicates = extract_predicates(source_query)
    if not predicates and not scenario_input:
        raise ScenarioError(
            "No decisive simple predicate could be inferred. Supply a reviewed or candidate scenario input."
        )
    if assessment["status"] != "simple" and not scenario_input:
        raise ScenarioError(
            f"Automatic generation is unsafe ({'; '.join(assessment['reasons'])}). "
            "Supply --reviewed-scenario or --candidate-scenario with malicious and benign records."
        )

    contract = load_solution_contract(solution, source_root)
    source_name = _first_query_source(source_query)
    custom_stream = _find_custom_stream(contract, source_name, predicates)
    if not custom_stream and scenario_input:
        custom_stream = _find_custom_stream(
            contract,
            source_name,
            [],
            allow_unmapped=True,
        )
    mappings: List[dict] = []
    generated_contract: Optional[dict] = None
    contract_resolution: Optional[dict] = None

    if custom_stream:
        columns = {
            item["name"]: str(item.get("type") or "dynamic")
            for item in custom_stream["columns"]
        }
        base_record = {name: _default_value(kind) for name, kind in columns.items()}
        for predicate, raw_path, value in custom_stream["mappings"]:
            _set_path(base_record, raw_path, value)
            mappings.append({
                "ruleColumn": predicate["column"],
                "operator": predicate["operator"],
                "rawPath": raw_path,
                "value": value,
            })
        ingestion_mode = "custom-dcr"
        source_table = _table_from_stream(str(custom_stream["outputStream"]))
        stream = custom_stream["stream"]
        output_stream = custom_stream["outputStream"]
    else:
        source_table = _find_standard_table(
            source_query,
            destination_query,
            source_name,
            table_root,
        )
        base_record, columns = _load_table_base(source_table, table_root)
        generated_contract = _load_standard_ingestion_contract(
            source_table,
            registry_path,
        )
        if generated_contract:
            contract_columns = {
                str(item["name"]): str(item["type"])
                for item in generated_contract.get("inputColumns") or []
                if isinstance(item, dict) and item.get("name") and item.get("type")
            }
            if not contract_columns:
                raise ScenarioError(
                    f"The registered {source_table} ingestion contract has no input columns."
                )
            output_columns = {
                str(item["name"]): str(item["type"])
                for item in (generated_contract.get("destination") or {}).get("columns") or []
                if isinstance(item, dict) and item.get("name") and item.get("type")
            } or contract_columns
            combined_query = source_query + "\n" + destination_query
            required_fields = _query_fields_from_schema(combined_query, output_columns)
            predicate_fields, unresolved_aliases = _query_predicate_fields(
                combined_query,
                columns,
            )
            for name, kind in predicate_fields.items():
                if name.casefold() not in {
                    field.casefold() for field in required_fields
                }:
                    required_fields[name] = kind
            contract_resolution = resolve_registered_contract(
                source_table,
                required_fields,
                registry_path=registry_path,
            )
            if unresolved_aliases:
                alias_blockers = [
                    f"Decisive predicate field {name!r} is a query alias and cannot be "
                    "mapped to a source field safely."
                    for name in unresolved_aliases
                ]
                contract_resolution["blockers"] = list(
                    contract_resolution.get("blockers") or []
                ) + alias_blockers
                contract_resolution["status"] = "blocked"
            if contract_resolution["status"] == "blocked":
                generated_contract = None
            else:
                base_record = {
                    name: copy.deepcopy(
                        base_record.get(name, _default_value(kind))
                    )
                    for name, kind in contract_columns.items()
                }
                columns = contract_columns
        for predicate in predicates:
            if predicate["column"] in columns:
                base_record[predicate["column"]] = predicate["value"]
                mappings.append({
                    "ruleColumn": predicate["column"],
                    "operator": predicate["operator"],
                    "rawPath": predicate["column"],
                    "value": predicate["value"],
                })
        if predicates and not mappings and not scenario_input:
            raise ScenarioError(
                "The decisive AR predicates could not be mapped to the Standard-table base event."
            )
        if generated_contract:
            ingestion_mode = "standard-dcr"
            stream = str(generated_contract["inputStream"])
            output_stream = str(generated_contract["destination"]["outputStream"])
        else:
            ingestion_mode = "offline-standard-table"
            stream = None
            output_stream = f"Microsoft-{source_table}"

    scenario_fixture = load_reviewed_scenario(scenario_input) if scenario_input else None
    if scenario_fixture:
        malicious = copy.deepcopy(scenario_fixture["maliciousRecords"])
        benign = copy.deepcopy(scenario_fixture["benignRecords"])
        locked_paths = list(scenario_fixture.get("lockedPaths") or [])
        hypothesis = scenario_fixture["hypothesis"]
        scenario_name = scenario_fixture["name"]
    else:
        malicious = [copy.deepcopy(base_record)]
        benign_record = copy.deepcopy(base_record)
        decisive = mappings[0]
        _set_path(
            benign_record,
            decisive["rawPath"],
            _benign_value(decisive["value"], decisive["operator"]),
        )
        benign = [benign_record]
        locked_paths = [item["rawPath"] for item in mappings]
        hypothesis = f"Synthetic records exercise the decisive predicates in {rule.get('name')}."
        scenario_name = "automatic-simple-predicate"

    for path, value in locks:
        for record in malicious:
            _set_path(record, path, value)
        locked_paths.append(path)
    for path, value in benign_assignments:
        for record in benign:
            _set_path(record, path, value)
    locked_paths = sorted(set(locked_paths))

    if randomize:
        malicious = randomized_copies(malicious, copies, seed, locked_paths, columns)
        benign = randomized_copies(benign, copies, seed + 1, locked_paths, columns)
    elif copies != 1:
        raise ScenarioError("--copies requires --randomize.")

    validate_records(malicious, columns)
    validate_records(benign, columns)

    _assert_no_symlink_below(output_root, output_dir, "output")
    output_dir.mkdir(parents=True, exist_ok=True)
    _assert_no_symlink_below(output_root, output_dir, "output")
    mock_path = output_dir / "mock.json"
    mock_path.write_text(json.dumps(malicious, indent=2) + "\n", encoding="utf-8")
    contract_path: Optional[Path] = None
    if generated_contract:
        contract_path = output_dir / "ingestion-contract.yaml"
        contract_path.write_text(
            yaml.safe_dump(generated_contract, sort_keys=False),
            encoding="utf-8",
        )

    remaining_predicates = list(predicates)
    for mapping in mappings:
        mapping_key = (
            str(mapping["ruleColumn"]).casefold(),
            str(mapping["operator"]).casefold(),
        )
        for index, predicate in enumerate(remaining_predicates):
            predicate_key = (
                str(predicate["column"]).casefold(),
                str(predicate["operator"]).casefold(),
            )
            if predicate_key == mapping_key:
                remaining_predicates.pop(index)
                break
    unmapped_predicate_limitations = [
        f"Decisive predicate {item['column']!r} ({item['operator']}) is not represented "
        "by an ingestion mapping."
        for item in remaining_predicates
    ]
    status = (
        "qualification-ready"
        if ingestion_mode in {"custom-dcr", "standard-dcr"}
        and assessment["status"] == "simple"
        and scenario_input_kind != "candidate"
        and not unmapped_predicate_limitations
        else "generated-offline-only"
    )
    manifest = {
        "version": SCENARIO_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "solution": solution,
        "ruleId": rule.get("id"),
        "ruleName": rule.get("name"),
        "analyticRule": str(rule_path),
        "sourceRoot": str(source_root),
        "toolkitRoot": str(toolkit_root),
        "sampleDataRoot": str(sample_data_root),
        "customDetectionId": _detection_property(detection, "id"),
        "customDetectionName": (
            _detection_property(detection, "displayName")
            or _detection_property(detection, "name")
        ),
        "customDetection": str(detection_path),
        "reviewedScenario": (
            str(scenario_input) if scenario_input_kind == "reviewed" else None
        ),
        "candidateScenario": (
            str(scenario_input) if scenario_input_kind == "candidate" else None
        ),
        "scenarioReview": {
            "status": (
                "review-pending"
                if scenario_input_kind == "candidate"
                else "reviewed"
                if scenario_input_kind == "reviewed"
                else "not-required"
            ),
            "inputKind": scenario_input_kind,
            "inputPath": str(scenario_input) if scenario_input else None,
            "inputSha256": scenario_input_hash,
            "semanticValidation": "not-run",
        },
        "outputRoot": str(output_root),
        "sourceHashes": {
            "analyticRuleFileSha256": _sha256_bytes(rule_path.read_bytes()),
            "analyticRuleQuerySha256": _sha256_bytes(
                source_query.encode("utf-8")
            ),
            "customDetectionFileSha256": _sha256_bytes(
                detection_path.read_bytes()
            ),
            "customDetectionQuerySha256": _sha256_bytes(
                destination_query.encode("utf-8")
            ),
        },
        "scenarioName": scenario_name,
        "hypothesis": hypothesis,
        "generationStatus": status,
        "queryAssessment": assessment,
        "sourceTable": source_table,
        "destinationTables": sorted(
            set(
                name
                for name in [_first_query_source(destination_query)]
                if name
            )
        ),
        "ingestion": {
            "mode": ingestion_mode,
            "dcr": custom_stream.get("dcr") if custom_stream else None,
            "stream": stream,
            "outputStream": output_stream,
            "contract": str(contract_path) if contract_path else None,
            "contractResolution": (
                {
                    "status": contract_resolution.get("status"),
                    "schemaFingerprint": contract_resolution.get("schemaFingerprint"),
                    "transformFingerprint": contract_resolution.get("transformFingerprint"),
                    "liveValidated": contract_resolution.get("liveValidated"),
                    "references": contract_resolution.get("references"),
                    "blockers": contract_resolution.get("blockers"),
                }
                if contract_resolution
                else None
            ),
            "directLogsIngestionSupported": ingestion_mode
            in {"custom-dcr", "standard-dcr"},
        },
        "mapping": {
            "decisiveFields": mappings,
            "lockedPaths": locked_paths,
        },
        "fixtures": {
            "mock": str(mock_path),
            "mockRecords": len(malicious),
            "benignValidationRecords": len(benign),
        },
        "validation": {
            "schemaValidation": "passed",
            "semanticReview": (
                "pending"
                if scenario_input_kind == "candidate"
                else "reviewed"
                if scenario_input_kind == "reviewed"
                else "not-required"
            ),
            "semanticMatch": "not-run",
            "sentinelSeededQuery": "not-run",
            "advancedHuntingSeededQuery": "not-run",
            "liveIngestion": "not-run",
            "liveSentinel": "not-run",
            "liveAdvancedHunting": "not-run",
            "alertParity": "not-run",
            "cleanup": "not-run",
        },
        "limitations": (
            list((contract_resolution or {}).get("blockers") or [])
            if status == "qualification-ready"
            else (
                [
                    "Candidate fixture input is review-pending; it is schema-checked only and cannot proceed to direct ingestion."
                ]
                if scenario_input_kind == "candidate"
                else [
                    "The query requires semantic review; generation does not establish that fixture records match it."
                ]
                if ingestion_mode in {"custom-dcr", "standard-dcr"}
                else [
                "The selected table does not expose a declared Custom-* input stream "
                "or a reviewed standard-table ingestion contract for direct Logs "
                "Ingestion API testing."
                ]
            ) + list((contract_resolution or {}).get("blockers") or [])
        ) + unmapped_predicate_limitations,
    }
    scenario_path = output_dir / "scenario.json"
    scenario_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "generated-candidate" if scenario_input_kind == "candidate" else "generated",
        "scenarioPath": str(scenario_path),
        "mockPath": str(mock_path),
        "paths": {
            "sourceRoot": str(source_root),
            "toolkitRoot": str(toolkit_root),
            "sampleDataRoot": str(sample_data_root),
            "outputRoot": str(output_root),
        },
        "scenario": manifest,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution", required=True)
    parser.add_argument("--rule", required=True, help="Rule ID, exact name, filename, or YAML path.")
    parser.add_argument("--custom-detection", help="Exact converted Custom Detection YAML path or selector.")
    parser.add_argument(
        "--source-root",
        type=Path,
        help="Azure-Sentinel repository containing Solutions/<solution> (defaults to this toolkit repository).",
    )
    parser.add_argument(
        "--toolkit-root",
        type=Path,
        help="Toolkit repository containing the standard-table registry (defaults to this repository).",
    )
    parser.add_argument(
        "--sample-data-root",
        type=Path,
        help="Root containing Tables/ base events (defaults to the toolkit Sample Data folder).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Exact mock output root; solution and rule-ID folders are created beneath it.",
    )
    parser.add_argument("--force", action="store_true", help="Regenerate an existing scenario.")
    scenario_inputs = parser.add_mutually_exclusive_group()
    scenario_inputs.add_argument(
        "--reviewed-scenario",
        type=Path,
        help="Reviewed complex scenario JSON; only use after human review.",
    )
    scenario_inputs.add_argument(
        "--candidate-scenario",
        type=Path,
        help="Provisional scenario JSON; generation remains review-pending and offline-only.",
    )
    parser.add_argument("--randomize", action="store_true")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260917)
    parser.add_argument("--lock", action="append", default=[], metavar="PATH=VALUE")
    parser.add_argument("--benign-set", action="append", default=[], metavar="PATH=VALUE")
    args = parser.parse_args(argv)

    try:
        result = generate_scenario(
            args.solution,
            args.rule,
            custom_detection_selector=args.custom_detection,
            force=args.force,
            reviewed_scenario=args.reviewed_scenario,
            candidate_scenario=args.candidate_scenario,
            randomize=args.randomize,
            copies=args.copies,
            seed=args.seed,
            locks=[_parse_assignment(item) for item in args.lock],
            benign_assignments=[_parse_assignment(item) for item in args.benign_set],
            source_root=args.source_root,
            toolkit_root=args.toolkit_root,
            sample_data_root=args.sample_data_root,
            output_root=args.output_root,
        )
    except ScenarioError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
