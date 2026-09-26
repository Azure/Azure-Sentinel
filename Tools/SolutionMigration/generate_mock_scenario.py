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
import json
import random
import re
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
SCENARIO_VERSION = 1
SUPPORTED_TYPES = {"string", "datetime", "dynamic", "bool", "boolean", "int", "long", "real", "double"}


class ScenarioError(RuntimeError):
    """A scenario cannot be generated or reused safely."""


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unnamed"


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


def find_analytic_rule(solution: str, selector: str) -> Tuple[Path, dict]:
    solution_root = REPOSITORY_ROOT / "Solutions" / solution
    supplied = Path(selector)
    if supplied.is_file():
        return supplied.resolve(), _load_yaml(supplied)

    candidates: List[Tuple[Path, dict]] = []
    for folder_name in ("Analytic Rules", "Analytics Rules"):
        folder = solution_root / folder_name
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.y*ml")):
            rule = _load_yaml(path)
            if (
                selector == str(rule.get("id"))
                or selector == str(rule.get("name"))
                or selector == path.name
                or selector == path.stem
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
) -> Tuple[Path, dict]:
    supplied = Path(selector) if selector else None
    if supplied and supplied.is_file():
        return supplied.resolve(), _load_yaml(supplied)

    folder = REPOSITORY_ROOT / "Solutions" / solution / "XDR Detections"
    if not folder.is_dir():
        raise ScenarioError(
            f"Converted Custom Detection folder does not exist: {folder}. "
            "Run the conversion stage before generating rule-specific mock data."
        )

    source_id = str(source_rule.get("id") or "")
    source_name = str(source_rule.get("name") or "")
    matches: List[Tuple[Path, dict]] = []
    for path in sorted(folder.glob("*.yaml")):
        detection = _load_yaml(path)
        identifiers = {
            _detection_source_id(detection),
            str(_detection_property(detection, "displayName") or ""),
            str(_detection_property(detection, "name") or ""),
            path.name,
            path.stem,
        }
        wanted = selector or source_id or source_name
        if wanted in identifiers or source_id in identifiers or source_name in identifiers:
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


def scenario_directory(solution: str, rule: dict) -> Path:
    rule_id = _safe_name(str(rule.get("id") or rule.get("name") or "rule"))
    return MOCK_ROOT / solution / rule_id


def validate_existing_scenario(path: Path, solution: str, rule: dict) -> dict:
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


def load_solution_contract(solution: str) -> dict:
    solution_root = REPOSITORY_ROOT / "Solutions" / solution
    package = solution_root / "Package" / "mainTemplate.json"
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
        for path in parser_root.rglob("*.y*ml"):
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


def _load_table_base(table: str) -> Tuple[dict, Dict[str, str]]:
    folder = TABLE_ROOT / table
    base_path = folder / "base-event.json"
    metadata_path = folder / "metadata.json"
    if not base_path.is_file() or not metadata_path.is_file():
        raise ScenarioError(
            f"Neutral base event was not found for table {table!r} under {TABLE_ROOT}."
        )
    base = _load_json(base_path)
    metadata = _load_json(metadata_path)
    columns = metadata.get("columns") if isinstance(metadata, dict) else None
    if not isinstance(base, dict) or not isinstance(columns, dict):
        raise ScenarioError(f"Invalid table base contract for {table!r}.")
    return base, {str(name): str(kind) for name, kind in columns.items()}


def _load_standard_ingestion_contract(table: str) -> Optional[dict]:
    for suffix in (".yaml", ".yml", ".json"):
        path = STANDARD_CONTRACT_ROOT / f"{table}{suffix}"
        if not path.is_file():
            continue
        value = (
            _load_json(path)
            if path.suffix.lower() == ".json"
            else yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        )
        if not isinstance(value, dict):
            raise ScenarioError(f"Invalid standard-table ingestion contract: {path}")
        destination = value.get("destination") or {}
        if (
            value.get("version") != 1
            or destination.get("kind") != "standard"
            or destination.get("table") != table
            or not str(value.get("inputStream") or "").startswith("Custom-")
            or not str(destination.get("outputStream") or "").startswith("Microsoft-")
        ):
            raise ScenarioError(
                f"Standard-table ingestion contract does not match {table!r}: {path}"
            )
        return value
    return None


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
) -> Optional[dict]:
    parser_query = (contract.get("parsers") or {}).get(source_name or "")
    for dcr in contract.get("dcrs") or []:
        declarations = dcr.get("streamDeclarations") or {}
        for flow in dcr.get("dataFlows") or []:
            transform = str(flow.get("transformKql") or "")
            for stream in flow.get("streams") or []:
                if stream not in declarations or not stream.startswith("Custom-"):
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
                if success and mappings:
                    return {
                        "dcr": dcr.get("name"),
                        "stream": stream,
                        "outputStream": flow.get("outputStream") or stream,
                        "transformKql": transform,
                        "columns": declarations[stream].get("columns") or [],
                        "mappings": mappings,
                    }
    return None


def _find_standard_table(query: str, custom_detection_query: str, source_name: Optional[str]) -> str:
    candidates = [source_name, _first_query_source(custom_detection_query)]
    for candidate in candidates:
        if candidate and (TABLE_ROOT / candidate / "base-event.json").is_file():
            return candidate
    tokens = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", f"{query}\n{custom_detection_query}"))
    for path in sorted(TABLE_ROOT.iterdir()):
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
        raise ScenarioError("Reviewed attack scenario must be a JSON object.")
    for field in ("name", "hypothesis"):
        if not isinstance(scenario.get(field), str) or not scenario[field].strip():
            raise ScenarioError(f"Reviewed attack scenario requires {field}.")
    for field in ("maliciousRecords", "benignRecords"):
        records = scenario.get(field)
        if not isinstance(records, list) or not records or not all(
            isinstance(record, dict) for record in records
        ):
            raise ScenarioError(f"Reviewed attack scenario requires non-empty {field}.")
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
    randomize: bool = False,
    copies: int = 1,
    seed: int = 20260917,
    locks: Sequence[Tuple[str, Any]] = (),
    benign_assignments: Sequence[Tuple[str, Any]] = (),
) -> dict:
    rule_path, rule = find_analytic_rule(solution, rule_selector)
    output_dir = scenario_directory(solution, rule)
    if output_dir.exists() and not force:
        return validate_existing_scenario(output_dir, solution, rule)

    detection_path, detection = find_custom_detection(
        solution,
        custom_detection_selector,
        rule,
    )
    source_query = _query(rule)
    destination_query = _query(detection)
    assessment = assess_query(source_query, rule)
    predicates = extract_predicates(source_query)
    if not predicates and not reviewed_scenario:
        raise ScenarioError(
            "No decisive simple predicate could be inferred. Supply --reviewed-scenario."
        )
    if assessment["status"] != "simple" and not reviewed_scenario:
        raise ScenarioError(
            f"Automatic generation is unsafe ({'; '.join(assessment['reasons'])}). "
            "Supply --reviewed-scenario with malicious and benign records."
        )

    contract = load_solution_contract(solution)
    source_name = _first_query_source(source_query)
    custom_stream = _find_custom_stream(contract, source_name, predicates)
    mappings: List[dict] = []
    generated_contract: Optional[dict] = None

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
        source_table = _find_standard_table(source_query, destination_query, source_name)
        base_record, columns = _load_table_base(source_table)
        generated_contract = _load_standard_ingestion_contract(source_table)
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
            base_record = {
                name: copy.deepcopy(base_record[name])
                for name in contract_columns
                if name in base_record
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
        if predicates and not mappings and not reviewed_scenario:
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

    reviewed = load_reviewed_scenario(reviewed_scenario) if reviewed_scenario else None
    if reviewed:
        malicious = copy.deepcopy(reviewed["maliciousRecords"])
        benign = copy.deepcopy(reviewed["benignRecords"])
        locked_paths = list(reviewed.get("lockedPaths") or [])
        hypothesis = reviewed["hypothesis"]
        scenario_name = reviewed["name"]
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

    output_dir.mkdir(parents=True, exist_ok=True)
    mock_path = output_dir / "mock.json"
    mock_path.write_text(json.dumps(malicious, indent=2) + "\n", encoding="utf-8")
    contract_path: Optional[Path] = None
    if generated_contract:
        contract_path = output_dir / "ingestion-contract.yaml"
        contract_path.write_text(
            yaml.safe_dump(generated_contract, sort_keys=False),
            encoding="utf-8",
        )

    status = (
        "qualification-ready"
        if ingestion_mode in {"custom-dcr", "standard-dcr"}
        and assessment["status"] == "simple"
        else "generated-offline-only"
    )
    manifest = {
        "version": SCENARIO_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "solution": solution,
        "ruleId": rule.get("id"),
        "ruleName": rule.get("name"),
        "analyticRule": str(rule_path),
        "customDetectionId": _detection_property(detection, "id"),
        "customDetectionName": (
            _detection_property(detection, "displayName")
            or _detection_property(detection, "name")
        ),
        "customDetection": str(detection_path),
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
            "sentinelSeededQuery": "not-run",
            "advancedHuntingSeededQuery": "not-run",
            "liveIngestion": "not-run",
            "liveSentinel": "not-run",
            "liveAdvancedHunting": "not-run",
            "alertParity": "not-run",
            "cleanup": "not-run",
        },
        "limitations": (
            []
            if status == "qualification-ready"
            else [
                "The selected table does not expose a declared Custom-* input stream "
                "or a reviewed standard-table ingestion contract for direct Logs "
                "Ingestion API testing."
            ]
        ),
    }
    scenario_path = output_dir / "scenario.json"
    scenario_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "generated",
        "scenarioPath": str(scenario_path),
        "mockPath": str(mock_path),
        "scenario": manifest,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution", required=True)
    parser.add_argument("--rule", required=True, help="Rule ID, exact name, filename, or YAML path.")
    parser.add_argument("--custom-detection", help="Exact converted Custom Detection YAML path or selector.")
    parser.add_argument("--force", action="store_true", help="Regenerate an existing scenario.")
    parser.add_argument("--reviewed-scenario", type=Path)
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
            randomize=args.randomize,
            copies=args.copies,
            seed=args.seed,
            locks=[_parse_assignment(item) for item in args.lock],
            benign_assignments=[_parse_assignment(item) for item in args.benign_set],
        )
    except ScenarioError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
