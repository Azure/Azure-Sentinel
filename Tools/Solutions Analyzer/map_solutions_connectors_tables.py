from __future__ import annotations

import csv
import json
import os
import re
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import quote

try:
    import json5  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    json5 = None

GITHUB_REPO_URL = "https://github.com/Azure/Azure-Sentinel/blob/master"

# Regex patterns for query parsing
PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_.]+")
ARM_VARIABLE_PATTERN = re.compile(r"\[\s*variables\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\]\s*", re.IGNORECASE)
UNION_KEYWORD_PATTERN = re.compile(r"\bunion\b", re.IGNORECASE)
LET_ASSIGNMENT_PATTERN = re.compile(r"\blet\s+([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_.]+)", re.IGNORECASE)
LINE_COMMENT_PATTERN = re.compile(r"(?m)^\s*//.*$")
FIELD_GENERATING_PATTERN = re.compile(
    r'^\s*\|\s*(?:extend|project|project-away|project-keep|project-rename|project-reorder|'
    r'summarize|make-series|mv-expand|mv-apply|evaluate)',
    re.IGNORECASE
)

# Token validation sets
PARSER_NAME_KEYS = {"functionname", "functionalias"}
NON_TABLE_TOKENS = {
    "let",
    "ago",
    "alerts",
    "datatable",
    "pack_array",
    "array_concat",
    "datetime_part",
    "dynamic",
    "time",
    "toscalar",
    "union",
    "view",
    "_im_dns",
}
PIPE_BLOCK_COMMANDS = {
    "project",
    "project-away",
    "project-rename",
    "extend",
    "summarize",
    "sort",
    "order",
    "top",
    "take",
    "limit",
    "parse",
}


def is_valid_table_candidate(token: Optional[str], *, allow_parser_names: bool = False) -> bool:
    if not isinstance(token, str):
        return False
    cleaned = token.strip()
    if not cleaned:
        return False
    lowered = cleaned.lower()
    if lowered in NON_TABLE_TOKENS:
        return False
    if lowered.isdigit():
        return False
    if re.fullmatch(r"\d+[smhd]", lowered):
        return False
    if cleaned[0].isdigit():
        return False
    if lowered.startswith("_") and not cleaned.upper().endswith("_CL"):
        return False
    if lowered.endswith("_parser") and not allow_parser_names:
        return False
    return True


def is_true_table_name(value: Optional[str]) -> bool:
    return isinstance(value, str) and value.strip().lower().endswith("_cl")


def prefers_asim_name(value: Optional[str]) -> bool:
    return isinstance(value, str) and value.strip().lower().startswith("asim")


PLURAL_TABLE_CORRECTIONS = {
    "securityevents": "SecurityEvent",
    "windowsevents": "WindowsEvent",
}


# Override system types
class Override:
    """Represents a single override rule from the overrides CSV."""
    def __init__(self, entity: str, pattern: str, field: str, value: str):
        self.entity = entity.lower().strip()
        self.pattern = pattern.strip()
        self.field = field.strip()
        self.value = value
        # Compile regex with anchors for full match, case insensitive
        try:
            self.regex = re.compile(f"^{self.pattern}$", re.IGNORECASE)
        except re.error:
            self.regex = None
    
    def matches(self, key: str) -> bool:
        """Check if the key matches this override's pattern."""
        if self.regex is None:
            return False
        return bool(self.regex.match(key))


def load_overrides(overrides_path: Path) -> List[Override]:
    """Load overrides from CSV file.
    
    CSV format: Entity,Pattern,Field,Value
    - Entity: table, connector, or solution (case insensitive)
    - Pattern: regex pattern to match against key (full match, case insensitive)
    - Field: the field to override
    - Value: the new value
    """
    overrides: List[Override] = []
    if not overrides_path.exists():
        return overrides
    
    try:
        # Use utf-8-sig to handle BOM (Byte Order Mark) from Excel
        with overrides_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entity = row.get("Entity", "").strip()
                pattern = row.get("Pattern", "").strip()
                field = row.get("Field", "").strip()
                value = row.get("Value", "")
                
                # Skip empty rows
                if not entity or not pattern or not field:
                    continue
                
                overrides.append(Override(entity, pattern, field, value))
    except Exception as e:
        print(f"Warning: Could not load overrides from {overrides_path}: {e}")
    
    return overrides


def apply_overrides_to_row(
    row: Dict[str, str],
    overrides: List[Override],
    entity_type: str,
    key_field: str
) -> Dict[str, str]:
    """Apply matching overrides to a row.
    
    Args:
        row: The data row to modify
        overrides: List of Override objects
        entity_type: 'table', 'connector', or 'solution'
        key_field: The field name to use for pattern matching (e.g., 'table_name', 'connector_id')
    
    Returns:
        Modified row with overrides applied
    """
    key_value = row.get(key_field, "")
    if not key_value:
        return row
    
    for override in overrides:
        if override.entity != entity_type.lower():
            continue
        if override.matches(key_value):
            # Apply the override
            if override.field in row:
                row[override.field] = override.value
    
    return row


def apply_overrides_to_data(
    data: List[Dict[str, str]],
    overrides: List[Override],
    entity_type: str,
    key_field: str
) -> List[Dict[str, str]]:
    """Apply overrides to all rows in a dataset.
    
    Args:
        data: List of data rows
        overrides: List of Override objects
        entity_type: 'table', 'connector', or 'solution'
        key_field: The field name to use for pattern matching
    
    Returns:
        Modified data with overrides applied
    """
    return [apply_overrides_to_row(row, overrides, entity_type, key_field) for row in data]


def apply_plural_table_fix(name: str) -> Tuple[str, Optional[str]]:
    lowered = name.lower()
    corrected = PLURAL_TABLE_CORRECTIONS.get(lowered)
    if corrected and corrected != name:
        return corrected, name
    return name, None


def safe_relative(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> Optional[Any]:
    """
    Read and parse JSON file with tolerance for common syntax issues.
    Attempts to strip JSON comments and trailing commas before parsing.
    """
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            content = handle.read()
        
        # Try standard JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Attempt to clean common issues
            # 1. Strip line comments (// ...)
            lines = content.splitlines()
            cleaned_lines = []
            for line in lines:
                # Remove // comments but preserve URLs (http://, https://)
                if '//' in line:
                    # Check if it's a comment (not part of a URL)
                    parts = line.split('//')
                    if len(parts) > 1:
                        # Keep the part before // if it doesn't look like a URL
                        before = parts[0]
                        if not before.rstrip().endswith(':'):
                            cleaned_lines.append(before)
                            continue
                cleaned_lines.append(line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            
            # 2. Attempt to fix trailing commas before } or ]
            import re
            cleaned_content = re.sub(r',(\s*[}\]])', r'\1', cleaned_content)
            
            # Try parsing cleaned content
            try:
                return json.loads(cleaned_content)
            except json.JSONDecodeError:
                pass
        
        # Fallback to json5 if available
        if json5 is not None:
            try:
                with path.open("r", encoding="utf-8-sig") as handle:
                    return json5.load(handle)
            except Exception as secondary_error:
                print(f"Failed to read {path}: {secondary_error}")
                return None
        
        # If all attempts failed, report the original error
        with path.open("r", encoding="utf-8-sig") as handle:
            json.load(handle)  # This will raise the original error
            
    except json.JSONDecodeError as primary_error:
        print(f"Failed to read {path}: {primary_error}")
        return None
    except Exception as exc:
        print(f"Failed to read {path}: {exc}")
        return None


def remove_line_comments(text: str) -> str:
    if not text:
        return text
    return LINE_COMMENT_PATTERN.sub("", text)


def strip_pipe_command_blocks(text: str) -> str:
    if not text:
        return text
    lines = text.splitlines()
    result: List[str] = []
    skip_block = False
    for line in lines:
        stripped = line.lstrip()
        if skip_block:
            if stripped.startswith("|"):
                skip_block = False
            else:
                continue
        if stripped.startswith("|"):
            command_parts = stripped[1:].lstrip().split()
            keyword = command_parts[0].lower() if command_parts else ""
            extended_keyword = keyword
            if keyword in {"order", "sort"} and len(command_parts) > 1:
                extended_keyword = f"{keyword} {command_parts[1].lower()}"
            if keyword in PIPE_BLOCK_COMMANDS or extended_keyword in {"order by", "sort by"}:
                skip_block = True
                continue
        result.append(line)
    return "\n".join(result)


def detect_pipeline_heads(
    text: str,
    *,
    assigned_variables: Set[str],
    allow_parser_tokens: bool,
) -> Set[str]:
    """
    Detect table names that appear as pipeline heads by analyzing query structure.
    Uses context-aware validation to distinguish tables from field names without whitelisting.
    """
    if not text:
        return set()
    tokens: Set[str] = set()
    lines = text.splitlines()
    total = len(lines)
    
    # Pattern for operators that generate fields (subset of FIELD_GENERATING_PATTERN)
    # These specific operators indicate field context where identifiers on subsequent lines
    # are likely field names rather than table names
    pipeline_field_pattern = re.compile(
        r"^\s*\|\s*(project|extend|parse|mv-expand|mv-apply|summarize)\b",
        re.IGNORECASE
    )
    
    # Track if we're inside a multi-line field-generating statement
    in_field_context = False
    
    for idx, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if this line starts a top-level field-generating operation (at start of line)
        if pipeline_field_pattern.match(line):
            in_field_context = True
            continue
        
        # Reset field context when we hit a new pipeline operator (that's not field-generating)
        if stripped.startswith("|"):
            in_field_context = False
            continue
        
        # Skip lines in field context that don't start with |
        if in_field_context:
            continue
        
        # Now check for pipeline head candidates (non-pipe lines)
        if not stripped:
            continue
        
        candidate = stripped.rstrip(";").strip()
        if not candidate:
            continue
        if not TOKEN_PATTERN.fullmatch(candidate):
            continue
        lowered = candidate.lower()
        if lowered in assigned_variables:
            continue
        
        # Check if followed by pipe (pipeline head pattern)
        next_idx = idx + 1
        while next_idx < total and lines[next_idx].strip() == "":
            next_idx += 1
        
        if next_idx < total and lines[next_idx].lstrip().startswith("|"):
            if is_valid_table_candidate(candidate, allow_parser_names=allow_parser_tokens):
                tokens.add(candidate)
    
    return tokens


def find_value_by_key(obj: Any, key: str) -> Optional[str]:
    if isinstance(obj, dict):
        for k, value in obj.items():
            if k == key and isinstance(value, str):
                return value
            result = find_value_by_key(value, key)
            if isinstance(result, str):
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_value_by_key(item, key)
            if isinstance(result, str):
                return result
    return None


def substitute_placeholders(text: str, root: Any, cache: Dict[str, Optional[str]]) -> str:
    def _replace(match: re.Match[str]) -> str:
        placeholder = match.group(1).strip()
        if placeholder not in cache:
            cache[placeholder] = find_value_by_key(root, placeholder)
        replacement = cache.get(placeholder)
        return replacement.strip() if isinstance(replacement, str) else ""

    return PLACEHOLDER_PATTERN.sub(_replace, text)


def extract_table_token(
    raw_text: Any,
    root: Any,
    cache: Dict[str, Optional[str]],
    *,
    allow_parser_tokens: bool = False,
) -> Optional[str]:
    if not isinstance(raw_text, str):
        return None
    cleaned = raw_text.strip()
    if not cleaned:
        return None
    cleaned = remove_line_comments(cleaned)
    cleaned = substitute_placeholders(cleaned, root, cache)
    for match in TOKEN_PATTERN.finditer(cleaned):
        token = match.group(0)
        if not token:
            continue
        if token.lower() == "variables":
            continue
        resolved_token = resolve_table_token_reference(token, root, cache)
        if resolved_token:
            token = resolved_token
        return token
    return None


def extract_query_table_tokens(
    raw_text: Any,
    root: Any,
    cache: Dict[str, Optional[str]],
    *,
    allow_parser_tokens: bool = False,
) -> Set[str]:
    tokens: Set[str] = set()
    if not isinstance(raw_text, str):
        token = extract_table_token(raw_text, root, cache, allow_parser_tokens=allow_parser_tokens)
        if token:
            tokens.add(token)
        return tokens
    cleaned = raw_text.strip()
    if not cleaned:
        return tokens
    without_comments = remove_line_comments(cleaned)
    pruned = strip_pipe_command_blocks(without_comments)
    substituted = substitute_placeholders(pruned, root, cache)

    assigned_variables: Set[str] = set()
    for match in LET_ASSIGNMENT_PATTERN.finditer(substituted):
        variable_name = match.group(1).strip().lower()
        candidate = match.group(2).strip()
        if candidate and is_valid_table_candidate(candidate, allow_parser_names=allow_parser_tokens):
            candidate_lower = candidate.lower()
            if candidate_lower not in assigned_variables:
                tokens.add(candidate)
        if variable_name:
            assigned_variables.add(variable_name)

    if UNION_KEYWORD_PATTERN.search(substituted):
        for match in TOKEN_PATTERN.finditer(substituted):
            candidate = match.group(0)
            lowered = candidate.lower()
            if lowered in {"union", "isfuzzy", "true", "false"}:
                continue
            if lowered.endswith("_cl") and is_valid_table_candidate(candidate):
                tokens.add(candidate)

    pipeline_tokens = detect_pipeline_heads(
        without_comments,
        assigned_variables=assigned_variables,
        allow_parser_tokens=allow_parser_tokens,
    )
    tokens.update(pipeline_tokens)
    token = extract_table_token(raw_text, root, cache, allow_parser_tokens=allow_parser_tokens)
    if token and is_valid_table_candidate(token, allow_parser_names=allow_parser_tokens):
        tokens.add(token)
    return {
        token
        for token in tokens
        if is_valid_table_candidate(token, allow_parser_names=allow_parser_tokens)
        or (allow_parser_tokens and isinstance(token, str) and token.lower().endswith("_parser"))
    }


def resolve_table_token_reference(token: str, root: Any, cache: Dict[str, Optional[str]]) -> Optional[str]:
    key = token.strip()
    if not key:
        return None
    if key not in cache:
        cache[key] = find_value_by_key(root, key)
    value = cache.get(key)
    if isinstance(value, str):
        variables = root.get("variables") if isinstance(root, dict) else None
        resolved = _resolve_arm_reference(value, variables) or value
        cleaned = resolved.strip().strip('"').strip("'")
        if cleaned and cleaned.lower() != key.lower():
            return cleaned
    return None


def extract_tables(data: Any) -> Dict[str, Dict[str, Any]]:
    tables: Dict[str, Dict[str, Any]] = {}
    cache: Dict[str, Optional[str]] = {}

    def build_method_label(path: Iterable[Any]) -> str:
        parts: List[str] = []
        for segment in path:
            if segment is None:
                continue
            if isinstance(segment, str):
                cleaned = segment.strip()
                if cleaned:
                    parts.append(cleaned)
            else:
                parts.append(str(segment))
        return ".".join(parts) if parts else "unknown"

    def record_table(
        name: Optional[str],
        *,
        mismatch: bool = False,
        actual: Optional[str] = None,
        method: str = "unknown",
    ) -> None:
        canonical_name = name.strip() if isinstance(name, str) else ""
        actual_clean = actual.strip() if isinstance(actual, str) else None
        method_label = method or "unknown"

        if mismatch:
            if actual_clean and is_true_table_name(actual_clean):
                canonical_name = actual_clean
                mismatch = False
                actual_clean = None
            elif is_true_table_name(canonical_name):
                mismatch = False
                actual_clean = None
            elif actual_clean and prefers_asim_name(actual_clean):
                canonical_name = actual_clean
                mismatch = False
                actual_clean = None
            elif prefers_asim_name(canonical_name):
                mismatch = False
                actual_clean = None
            elif actual_clean:
                canonical_name = actual_clean
                mismatch = False
                actual_clean = None

        if not canonical_name and actual_clean:
            canonical_name = actual_clean
            mismatch = False
            actual_clean = None

        if not canonical_name:
            return

        canonical_name, plural_source = apply_plural_table_fix(canonical_name)

        entry = tables.setdefault(canonical_name, {"has_mismatch": False, "actual_table": None, "sources": set()})
        entry["has_mismatch"] = entry["has_mismatch"] or mismatch
        if mismatch and actual_clean:
            entry["actual_table"] = actual_clean
        if plural_source:
            plural_list = entry.setdefault("plural_sources", [])
            if plural_source not in plural_list:
                plural_list.append(plural_source)
        sources: Set[str] = entry.setdefault("sources", set())
        sources.add(method_label)

    def walk(obj: Any, key_path: Tuple[Any, ...] = ()):  # noqa: ANN401
        if isinstance(obj, dict):
            for key, value in obj.items():
                lower_key = key.lower()
                current_path = key_path + (key,)
                method_label = build_method_label(current_path)
                if lower_key == "basequery" or lower_key == "query":
                    tokens = extract_query_table_tokens(value, data, cache, allow_parser_tokens=True)
                    if tokens:
                        for token in tokens:
                            record_table(token, method=method_label)
                    else:
                        record_table(
                            extract_table_token(value, data, cache, allow_parser_tokens=True),
                            method=method_label,
                        )
                elif key == "dataTypes" and isinstance(value, list):
                    for idx, item in enumerate(value):
                        if isinstance(item, dict):
                            item_path = current_path + (str(idx),)
                            name_method = build_method_label(item_path + ("name",))
                            name_token = extract_table_token(
                                item.get("name"),
                                data,
                                cache,
                                allow_parser_tokens=True,
                            )
                            query_key = "lastDataReceivedQuery" if item.get("lastDataReceivedQuery") else "query"
                            query_field = item.get("lastDataReceivedQuery") or item.get("query")
                            query_method = build_method_label(item_path + (query_key,))
                            query_tokens = list(
                                extract_query_table_tokens(
                                    query_field,
                                    data,
                                    cache,
                                    allow_parser_tokens=True,
                                )
                            )
                            primary_actual = query_tokens[0] if query_tokens else None
                            if not primary_actual:
                                primary_actual = extract_table_token(
                                    query_field,
                                    data,
                                    cache,
                                    allow_parser_tokens=True,
                                )
                            mismatch = False
                            if name_token and primary_actual and name_token.lower() != primary_actual.lower():
                                mismatch = True
                            record_table(
                                name_token or primary_actual,
                                mismatch=mismatch,
                                actual=primary_actual,
                                method=name_method if name_token else query_method,
                            )
                            for extra_table in query_tokens[1:]:
                                record_table(extra_table, method=query_method)
                walk(value, current_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                walk(item, key_path + (str(idx),))

    walk(data)
    return tables



def find_connector_objects(data: Any) -> List[Dict[str, Any]]:
    """Find connector objects and extract description, instructionSteps, and permissions if present."""
    connectors: List[Dict[str, Any]] = []
    stack = [data]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if {"id", "publisher", "title"}.issubset(current.keys()):
                id_value = current.get("id")
                publisher_value = current.get("publisher")
                title_value = current.get("title")
                # Allow connectors where title is a valid string (most important for display)
                # id and publisher may contain ARM variable references which we can resolve later
                if (
                    isinstance(id_value, str)
                    and isinstance(publisher_value, str)
                    and isinstance(title_value, str)
                    and "[variables(" not in title_value.lower()  # title must be literal
                ):
                    # Extract description, instructionSteps, and permissions if available
                    connector_copy = current.copy()
                    connector_copy["id_generated"] = False
                    # Resolve id if it's a variable reference - use a fallback based on title
                    if "[variables(" in id_value.lower():
                        # Try to create a reasonable id from the title
                        connector_copy["id"] = title_value.replace(" ", "").replace("-", "")
                        connector_copy["id_generated"] = True
                    # Resolve publisher if it's a variable reference - mark as unknown
                    if "[variables(" in publisher_value.lower():
                        connector_copy["publisher"] = "Unknown (ARM variable)"
                    if "descriptionMarkdown" in current:
                        connector_copy["description"] = current["descriptionMarkdown"]
                    if "instructionSteps" in current:
                        # Store instructionSteps as JSON-encoded string
                        connector_copy["instructionSteps"] = json.dumps(current["instructionSteps"])
                    if "permissions" in current:
                        # Store permissions as JSON-encoded string
                        connector_copy["permissions"] = json.dumps(current["permissions"])
                    connectors.append(connector_copy)
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return connectors


def collect_solution_info(solution_dir: Path) -> Dict[str, str]:
    metadata_path = solution_dir / "SolutionMetadata.json"
    metadata = read_json(metadata_path) if metadata_path.exists() else {}
    if not isinstance(metadata, dict):
        metadata = {}
    
    # Flatten support object
    support = metadata.get("support", {})
    if not isinstance(support, dict):
        support = {}
    
    # Flatten author object
    author = metadata.get("author", {})
    if not isinstance(author, dict):
        author = {}
    
    # Extract categories as comma-separated string
    categories = metadata.get("categories", {})
    if isinstance(categories, dict):
        category_keys = [k for k in categories.keys() if categories.get(k)]
        categories_str = ",".join(category_keys)
    else:
        categories_str = ""
    
    return {
        "solution_name": solution_dir.name,
        "solution_folder": solution_dir.name,
        "solution_publisher_id": metadata.get("publisherId", ""),
        "solution_offer_id": metadata.get("offerId", ""),
        "solution_first_publish_date": metadata.get("firstPublishDate", ""),
        "solution_last_publish_date": metadata.get("lastPublishDate", ""),
        "solution_version": metadata.get("version", ""),
        "solution_support_name": support.get("name", ""),
        "solution_support_tier": support.get("tier", ""),
        "solution_support_link": support.get("link", ""),
        "solution_author_name": author.get("name", ""),
        "solution_categories": categories_str,
    }


def collect_parser_metadata(solution_dir: Path) -> Tuple[Set[str], Dict[str, Set[str]]]:
    parsers_dir = solution_dir / "Parsers"
    names: Set[str] = set()
    tables_by_parser: Dict[str, Set[str]] = defaultdict(set)
    if not parsers_dir.exists():
        return names, {}

    for yaml_path in list(parsers_dir.rglob("*.yml")) + list(parsers_dir.rglob("*.yaml")):
        parser_names, function_queries = _extract_parser_details_from_file(yaml_path)
        if not parser_names and not function_queries:
            continue
        names.update(parser_names)
        parser_tables: Set[str] = set()
        for query in function_queries:
            parser_tables.update(extract_query_table_tokens(query, {}, {}))
        if not parser_tables:
            continue
        for parser_name in parser_names:
            lowered = parser_name.lower()
            if lowered:
                tables_by_parser.setdefault(lowered, set()).update(parser_tables)

    return names, tables_by_parser


def _strip_quoted(value: str) -> str:
    value = value.strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        return value[1:-1]
    return value


def _extract_parser_details_from_file(path: Path) -> Tuple[Set[str], List[str]]:
    names: Set[str] = set()
    queries: List[str] = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return names, queries
    lines = content.splitlines()
    names.update(_extract_parser_names_from_lines(lines))
    queries.extend(_extract_function_queries_from_lines(lines))
    return names, queries


def _extract_parser_names_from_lines(lines: List[str]) -> Set[str]:
    names: Set[str] = set()
    for raw_line in lines:
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip().strip("\"'")
        if key.lower() not in PARSER_NAME_KEYS:
            continue
        cleaned = _strip_quoted(value.split("#", 1)[0])
        if cleaned:
            names.add(cleaned)
    return names


def _extract_function_queries_from_lines(lines: List[str]) -> List[str]:
    queries: List[str] = []
    idx = 0
    total = len(lines)
    while idx < total:
        line = lines[idx]
        stripped = line.strip()
        if ":" not in line:
            idx += 1
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() != "functionquery":
            idx += 1
            continue
        remainder = value.strip()
        if remainder and not remainder.startswith(("|", ">")):
            queries.append(_strip_quoted(remainder))
            idx += 1
            continue
        block, new_index = _capture_block_scalar(lines, idx)
        if block:
            queries.append(block)
        idx = new_index + 1
    return queries


def _capture_block_scalar(lines: List[str], start_index: int) -> Tuple[str, int]:
    buffer: List[str] = []
    block_indent: Optional[int] = None
    idx = start_index + 1
    total = len(lines)
    while idx < total:
        line = lines[idx]
        stripped = line.rstrip("\n")
        if stripped.strip() == "" and block_indent is None:
            buffer.append("")
            idx += 1
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if block_indent is None and stripped.strip() != "":
            block_indent = current_indent
        if block_indent is not None and stripped.strip() != "" and current_indent < block_indent:
            break
        if block_indent is None:
            buffer.append("")
        else:
            buffer.append(line[block_indent:])
        idx += 1
    joined = "\n".join(buffer).rstrip("\n")
    return joined, idx - 1 if idx <= total else total - 1


def expand_parser_tables(parser_name: str, parser_table_map: Dict[str, Set[str]], max_depth: int = 5) -> Set[str]:
    visited: Set[str] = set()

    def _walk(name: str, depth: int) -> Set[str]:
        lowered = name.lower()
        if not lowered or lowered in visited or depth > max_depth:
            return set()
        visited.add(lowered)
        direct = parser_table_map.get(lowered)
        if not direct:
            return set()
        resolved: Set[str] = set()
        for candidate in direct:
            candidate_lower = candidate.lower()
            if candidate_lower in parser_table_map:
                resolved.update(_walk(candidate, depth + 1))
            else:
                resolved.add(candidate)
        return resolved or set(direct)

    return _walk(parser_name, 0)


def _collect_values_for_key(obj: Any, key: str) -> List[str]:
    values: List[str] = []

    def walk(node: Any) -> None:  # noqa: ANN401
        if isinstance(node, dict):
            for current_key, value in node.items():
                if current_key == key and isinstance(value, str):
                    values.append(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(obj)
    return values


def _resolve_arm_reference(value: Optional[str], variables: Optional[Dict[str, Any]], depth: int = 0) -> Optional[str]:
    if not isinstance(value, str) or depth > 5:
        return None
    trimmed = value.strip().strip('"').strip("'")
    if not trimmed:
        return None
    match = ARM_VARIABLE_PATTERN.fullmatch(trimmed)
    if match and isinstance(variables, dict):
        lookup_key = match.group(1)
        replacement = variables.get(lookup_key)
        if isinstance(replacement, str):
            return _resolve_arm_reference(replacement, variables, depth + 1) or replacement.strip()
        return None
    if trimmed.startswith("[") and trimmed.endswith("]"):
        return None
    return trimmed


def extract_log_analytics_tables(data: Any) -> Set[str]:
    tables: Set[str] = set()
    variables = data.get("variables") if isinstance(data, dict) else None
    for raw_value in _collect_values_for_key(data, "logAnalyticsTableId"):
        resolved = _resolve_arm_reference(raw_value, variables) or raw_value.strip()
        cleaned = resolved.strip('"').strip("'") if isinstance(resolved, str) else ""
        if cleaned:
            tables.add(cleaned)
    return tables


def determine_collection_method(
    connector_id: str,
    connector_title: str,
    connector_description: str,
    json_content: Optional[str] = None,
    filename: Optional[str] = None,
    table_metadata: Optional[List[Dict[str, str]]] = None,
) -> Tuple[str, str, List[Tuple[str, str]]]:
    """
    Determine the data collection method based on connector metadata, JSON content, and table metadata.
    
    Collection Methods:
    - CCF (Codeless Connector Framework): Uses pollingConfig, RestApiPoller, CCP/CCF patterns
    - Azure Function: Uses Azure Functions to collect and ingest data
    - AMA (Azure Monitor Agent): Uses Azure Monitor Agent for CEF/Syslog collection
    - MMA (Log Analytics Agent): Legacy agent using workspace ID/key
    - Azure Diagnostics: Uses Azure diagnostic settings
    - REST API: Direct REST API integration
    - Native: Built-in Microsoft integrations
    
    Detection Priority:
    1. Explicit AMA/MMA in title (strongest indicator)
    2. Azure Diagnostics patterns
    3. Native Microsoft integrations
    4. CCF patterns (content-based)
    5. Azure Function patterns
    6. REST API patterns
    7. Table metadata fallback
    
    Args:
        connector_id: The connector identifier
        connector_title: The connector title
        connector_description: The connector description
        json_content: Optional JSON content from the connector definition file
        filename: Optional filename of the connector definition
        table_metadata: Optional list of table metadata dicts with 'category' and 'resource_types'
    
    Returns:
        Tuple of (collection_method, detection_reason, all_matches)
        where all_matches is a list of (method, reason) for all detected methods
    """
    # Normalize inputs for case-insensitive matching
    conn_id_lower = (connector_id or "").lower()
    conn_title_lower = (connector_title or "").lower()
    conn_desc_lower = (connector_description or "").lower()
    content = json_content or ""
    file_lower = (filename or "").lower()
    
    # Track all matching methods for reporting
    all_matches: List[Tuple[str, str]] = []
    
    # === PRIORITY 1: Explicit AMA/MMA in title only (strongest indicator) ===
    # Only title-based detection - must be explicit in connector name
    title_indicates_ama = ('AMA' in connector_title or 'via AMA' in connector_title or
                           'ama' in conn_id_lower.split('-') or conn_id_lower.endswith('ama'))
    title_indicates_mma = ('Legacy Agent' in connector_title or 'via Legacy Agent' in connector_title)
    
    # Special case: WindowsFirewall (without Ama suffix) is MMA
    if connector_id == 'WindowsFirewall':
        title_indicates_mma = True
    
    if title_indicates_ama:
        all_matches.append(("AMA", "Title/ID indicates AMA"))
    if title_indicates_mma:
        all_matches.append(("MMA", "Title mentions Legacy Agent"))
    
    # === PRIORITY 2: Azure Function Detection - FILENAME ONLY ===
    # Only filename-based detection at this priority - content patterns are lower
    is_azure_function_filename = False
    if 'functionapp' in file_lower or 'function_app' in file_lower or '_api_function' in file_lower:
        all_matches.append(("Azure Function", "Filename indicates Azure Function"))
        is_azure_function_filename = True
    if 'azurefunction' in conn_id_lower or 'functionapp' in conn_id_lower:
        all_matches.append(("Azure Function", "ID contains AzureFunction/FunctionApp"))
        is_azure_function_filename = True
    
    # === PRIORITY 3: CCF Content Detection (strong patterns - before Azure Diagnostics) ===
    is_ccf_content = False
    # CCF Push variant - uses DCR/DCE for partner push ingestion
    if 'DeployPushConnectorButton' in content and 'HasDataConnectors' in content:
        all_matches.append(("CCF", "CCF Push connector (DCR/DCE based)"))
        is_ccf_content = True
    # Check content-based patterns (more reliable than name-based)
    if 'pollingConfig' in content:
        all_matches.append(("CCF", "Has pollingConfig"))
        is_ccf_content = True
    if 'dcrConfig' in content and '"type"' in content and 'RestApiPoller' in content:
        all_matches.append(("CCF", "Has dcrConfig with RestApiPoller"))
        is_ccf_content = True
    if 'GCPAuthConfig' in content:
        all_matches.append(("CCF", "Has GCPAuthConfig"))
        is_ccf_content = True
    # dataConnectorDefinitions - but not if AMA is in title
    if 'dataConnectorDefinitions' in content and not title_indicates_ama:
        all_matches.append(("CCF", "Uses dataConnectorDefinitions"))
        is_ccf_content = True
    
    # === PRIORITY 4: Azure Diagnostics patterns (before CCF name patterns) ===
    is_azure_diagnostics = False
    if not is_azure_function_filename:
        if 'AzureDiagnostics' in content or 'diagnostic settings' in conn_desc_lower:
            all_matches.append(("Azure Diagnostics", "References Azure Diagnostics"))
            is_azure_diagnostics = True
        if 'Microsoft.Insights/diagnosticSettings' in content:
            all_matches.append(("Azure Diagnostics", "Uses diagnostic settings resource"))
            is_azure_diagnostics = True
        if 'policyDefinitionGuid' in content and 'PolicyAssignment' in content:
            all_matches.append(("Azure Diagnostics", "Uses Azure Policy for diagnostics"))
            is_azure_diagnostics = True
    
    # === PRIORITY 5: CCF Name-based Detection (lower priority - after Azure Diagnostics) ===
    # Only use name-based CCF if no Azure Diagnostics patterns found
    is_ccf_name = False
    if not is_azure_diagnostics:
        if ('ccp' in conn_id_lower or 'ccf' in conn_id_lower or 'codeless' in conn_title_lower):
            all_matches.append(("CCF", "ID/title contains CCP/CCF/Codeless"))
            is_ccf_name = True
        if 'polling' in conn_id_lower and 'function' not in conn_id_lower:
            all_matches.append(("CCF", "ID contains Polling pattern (CCF)"))
            is_ccf_name = True
    
    is_ccf = is_ccf_content or is_ccf_name
    
    # === PRIORITY 6: Azure Function Content Detection (lower priority) ===
    # Content-based Azure Function patterns - only if not already detected as CCF content
    is_azure_function_content = False
    if not is_ccf_content:
        if 'azure functions' in conn_desc_lower:
            all_matches.append(("Azure Function", "Description mentions Azure Functions"))
            is_azure_function_content = True
        if 'Deploy to Azure' in content and 'Function App' in content:
            all_matches.append(("Azure Function", "Deploy Azure Function pattern"))
            is_azure_function_content = True
        if 'Azure Function App' in content:
            all_matches.append(("Azure Function", "Content mentions Azure Function App"))
            is_azure_function_content = True
        if 'azure-functions' in content.lower() and 'pricing/details/functions' in content.lower():
            all_matches.append(("Azure Function", "References Azure Functions pricing"))
            is_azure_function_content = True
    
    is_azure_function = is_azure_function_filename or is_azure_function_content
    
    # === PRIORITY 7: Native Microsoft Integration (skip if CCF content detected) ===
    # Native patterns are broad, so only use if no CCF content patterns found
    is_native = False
    if not is_ccf_content:
        if 'SentinelKinds' in content:
            all_matches.append(("Native", "Uses SentinelKinds (Native integration)"))
            is_native = True
        if any(x in connector_title for x in ['Microsoft Defender', 'Microsoft 365', 'Office 365', 'Microsoft Entra ID']):
            all_matches.append(("Native", "Microsoft native integration"))
            is_native = True
        if any(x in connector_id for x in ['AzureActivity', 'AzureActiveDirectory', 'Office365', 'MicrosoftDefender']):
            all_matches.append(("Native", "Known native connector ID"))
            is_native = True
    
    # === PRIORITY 8: Additional AMA/MMA patterns (lower priority) ===
    if 'Azure Monitor Agent' in connector_description and 'AMA' in content:
        all_matches.append(("AMA", "Description mentions Azure Monitor Agent"))
    if 'sent_by_ama' in content:
        all_matches.append(("AMA", "Uses sent_by_ama field"))
    if 'CEF via AMA' in content or 'Syslog via AMA' in content:
        all_matches.append(("AMA", "References CEF/Syslog via AMA"))
    if 'cef_installer.py' in content:
        all_matches.append(("MMA", "Uses CEF installer script"))
    if 'omsagent' in content.lower():
        all_matches.append(("MMA", "References omsagent"))
    if 'Install the agent' in content and 'Syslog' in content and 'AMA' not in content:
        all_matches.append(("MMA", "Syslog with agent installation (no AMA)"))
    if ('workspaceId' in content.lower() and 'sharedKeys' in content.lower() and 
        'Azure Function' not in connector_description):
        all_matches.append(("MMA", "Uses workspace ID/key pattern"))
    
    # === PRIORITY 9: REST API patterns ===
    if 'REST API' in connector_title or 'REST API' in connector_description:
        all_matches.append(("REST API", "Title/description mentions REST API"))
    if 'push' in conn_title_lower or 'push' in conn_id_lower:
        all_matches.append(("REST API", "Push connector (REST API based)"))
    if 'webhook' in conn_title_lower or ('webhook' in conn_desc_lower and 'http' in conn_desc_lower):
        all_matches.append(("REST API", "Webhook pattern (REST API based)"))
    if 'http endpoint' in conn_desc_lower or 'http trigger' in conn_desc_lower:
        all_matches.append(("REST API", "HTTP endpoint/trigger (REST API)"))
    
    # === PRIORITY 10: Table metadata-based detection (lowest content-based priority) ===
    # Only use if no stronger patterns detected - this is a fallback
    if table_metadata and not is_azure_function and not is_ccf and not is_native and not is_azure_diagnostics:
        for table_info in table_metadata:
            category = table_info.get('category', '')
            resource_types = table_info.get('resource_types', '').lower()
            
            # Azure Resources category -> Azure Diagnostics
            if category == 'Azure Resources':
                all_matches.append(("Azure Diagnostics", f"Table category is 'Azure Resources'"))
                break  # Only add once
            
            # virtualmachines in resource_types -> AMA
            if 'virtualmachines' in resource_types:
                all_matches.append(("AMA", f"Table resource_types includes 'virtualmachines'"))
                break  # Only add once
    
    # === PRIORITY 11: Custom log fallback ===
    if '_CL' in content and not all_matches:
        all_matches.append(("Unknown (Custom Log)", "Custom log table - needs analysis"))
    
    # Determine final method based on priority
    # Priority order reflects detection order - higher = selected first
    # Title-based AMA/MMA > Azure Function (filename) > CCF (content) > Azure Diagnostics > CCF (name) > Azure Function (content) > Native > AMA/MMA (content) > REST API
    priority_order = ["Azure Diagnostics", "CCF", "Azure Function", "Native", "AMA", "MMA", "REST API", "Unknown (Custom Log)", "Unknown"]
    
    # Special case: If title explicitly indicates AMA/MMA, prioritize that
    if title_indicates_ama:
        priority_order = ["AMA"] + [m for m in priority_order if m != "AMA"]
    elif title_indicates_mma:
        priority_order = ["MMA"] + [m for m in priority_order if m != "MMA"]
    
    if all_matches:
        # Select based on priority
        for method in priority_order:
            for match in all_matches:
                if match[0] == method:
                    return match[0], match[1], all_matches
    
    return "Unknown", "Method not detected", all_matches

def add_issue(
    issues: List[Dict[str, str]],
    *,
    solution_name: str,
    solution_folder: str,
    reason: str,
    details: str,
    connector_id: str = "",
    connector_title: str = "",
    connector_publisher: str = "",
    connector_file: str = "",
) -> None:
    issues.append({
        "solution_name": solution_name,
        "solution_folder": solution_folder,
        "connector_id": connector_id,
        "connector_title": connector_title,
        "connector_publisher": connector_publisher,
        "connector_file": connector_file,
        "reason": reason,
        "details": details,
    })


def parse_args(default_repo_root: Path) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract connector metadata and table usage per solution")
    parser.add_argument(
        "--solutions-dir",
        type=Path,
        default=default_repo_root / "Solutions",
        help="Path to the Solutions directory (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solutions_connectors_tables_mapping.csv",
        help="Path for the generated CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solutions_connectors_tables_issues_and_exceptions_report.csv",
        help="Path for the no-table issues report file (default: %(default)s)",
    )
    parser.add_argument(
        "--connectors-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "connectors.csv",
        help="Path for the connectors CSV file with collection methods (default: %(default)s)",
    )
    parser.add_argument(
        "--solutions-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solutions.csv",
        help="Path for the solutions CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--tables-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "tables.csv",
        help="Path for the tables CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--tables-reference-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "tables_reference.csv",
        help="Path to tables_reference.csv for table metadata (default: %(default)s)",
    )
    parser.add_argument(
        "--mapping-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solutions_connectors_tables_mapping_simplified.csv",
        help="Path for the simplified mapping CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--show-detection-methods",
        action="store_true",
        default=False,
        help="Include table_detection_methods column in output CSV (default: False)",
    )
    parser.add_argument(
        "--overrides-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solution_analyzer_overrides.csv",
        help="Path to overrides CSV file for field value overrides (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    # Script is in Tools/Solutions Analyzer, repo root is 2 levels up
    repo_root = Path(__file__).resolve().parents[2]
    args = parse_args(repo_root)

    solutions_dir = args.solutions_dir.resolve()
    if not solutions_dir.exists() or not solutions_dir.is_dir():
        raise SystemExit(f"Solutions directory not found: {solutions_dir}")

    output_path = args.output.resolve()
    output_parent = output_path.parent
    output_parent.mkdir(parents=True, exist_ok=True)

    report_path = args.report.resolve()
    report_parent = report_path.parent
    report_parent.mkdir(parents=True, exist_ok=True)

    # Load tables_reference.csv early for use in collection method detection
    tables_reference: Dict[str, Dict[str, str]] = {}
    tables_reference_path = args.tables_reference_csv.resolve()
    if tables_reference_path.exists():
        with tables_reference_path.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                table_name = row.get('table_name', '')
                if table_name:
                    tables_reference[table_name] = row

    # Load overrides from CSV file
    overrides: List[Override] = load_overrides(args.overrides_csv.resolve())
    if overrides:
        print(f"Loaded {len(overrides)} override(s) from {args.overrides_csv}")

    grouped_rows: Dict[Tuple[str, ...], Dict[str, bool]] = defaultdict(dict)
    row_key_metadata: Dict[Tuple[str, ...], Dict[str, str]] = {}
    combo_with_non_azure: Set[Tuple[str, str, str]] = set()
    missing_connector_json: List[str] = []
    missing_metadata_with_connectors: List[str] = []

    solution_rows_kept: Dict[str, int] = defaultdict(int)
    solution_parser_skipped: Dict[str, Set[str]] = defaultdict(set)
    issues: List[Dict[str, str]] = []
    
    # Track all solutions and identify those without any connectors
    all_solutions_info: Dict[str, Dict[str, str]] = {}
    solutions_without_connectors: Set[str] = set()

    for solution_dir in sorted([p for p in solutions_dir.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        solution_info = collect_solution_info(solution_dir.resolve())
        
        # Store all solution info for later processing
        all_solutions_info[solution_info["solution_name"]] = solution_info
        
        has_metadata = (solution_dir / "SolutionMetadata.json").exists()
        parser_names, parser_table_map = collect_parser_metadata(solution_dir.resolve())
        parser_names_lower = {name.lower() for name in parser_names if name}
        # Support "Data Connectors" (preferred), "DataConnectors", and "Data Connector" (singular) folder naming
        data_connectors_dirs = [
            solution_dir / "Data Connectors",
            solution_dir / "DataConnectors",
            solution_dir / "Data Connector",
        ]
        has_valid_connector = False
        has_data_connectors_dir = False

        for data_connectors_dir in data_connectors_dirs:
            if not data_connectors_dir.exists():
                continue
            has_data_connectors_dir = True
            for json_path in sorted(data_connectors_dir.rglob("*.json")):
                data = read_json(json_path)
                if data is None:
                    # Log JSON parsing failure as an issue
                    relative_path = safe_relative(json_path, data_connectors_dir)
                    issues.append({
                        "solution_name": solution_info["name"],
                        "solution_folder": solution_info["folder"],
                        "connector_id": "",
                        "connector_title": "",
                        "connector_publisher": "",
                        "connector_file": str(relative_path),
                        "reason": "json_parse_error",
                        "details": f"Failed to parse JSON file: {json_path.name}",
                    })
                    continue
                connector_entries = find_connector_objects(data)
                if not connector_entries:
                    continue
                has_valid_connector = True
                table_map = {k: v for k, v in extract_tables(data).items() if k.lower() != "let"}
                log_table_candidates = extract_log_analytics_tables(data)
                used_loganalytics_fallback = False
                had_raw_table_definitions = bool(table_map)
                if not table_map and log_table_candidates:
                    used_loganalytics_fallback = True
                    for table_name in log_table_candidates:
                        table_map[table_name] = {
                            "has_mismatch": False,
                            "actual_table": None,
                            "sources": {"logAnalyticsTableId"},
                        }
                if parser_names_lower:
                    for info in table_map.values():
                        actual_name = info.get("actual_table")
                        if actual_name and actual_name.lower() in parser_names_lower:
                            info["has_mismatch"] = False
                            info["actual_table"] = None
                table_entries = list(table_map.items())
                relative_path = safe_relative(json_path, data_connectors_dir)
                is_azuredeploy = json_path.name.lower().startswith("azuredeploy")
                for entry in connector_entries:
                    connector_id = entry.get("id", "")
                    connector_publisher = entry.get("publisher", "")
                    connector_title = entry.get("title", "")
                    connector_id_generated = entry.get("id_generated", False)
                    # Replace newlines with <br> for GitHub CSV rendering
                    connector_description = entry.get("description", "").replace("\n", "<br>").replace("\r", "")
                    connector_instruction_steps = entry.get("instructionSteps", "")
                    connector_permissions = entry.get("permissions", "")
                    had_table_definitions = had_raw_table_definitions
                    parser_filtered_tables: Set[str] = set()
                    parser_expansion_details: Dict[str, Set[str]] = {}
                    produced_rows = 0
                    total_table_entries = len(table_entries)

                    effective_table_entries: List[Tuple[str, Dict[str, Any]]] = []
                    for original_name, table_info in table_entries:
                        if not isinstance(original_name, str) or not original_name:
                            continue
                        lowered = original_name.lower()
                        if lowered and lowered in parser_names_lower:
                            original_sources = set(table_info.get("sources") or [])
                            derived_tables = expand_parser_tables(original_name, parser_table_map)
                            if derived_tables:
                                parser_expansion_details[original_name] = derived_tables
                                for derived_table in sorted(derived_tables):
                                    if not is_valid_table_candidate(derived_table):
                                        continue
                                    derived_sources = set(original_sources)
                                    derived_sources.add(f"parser:{original_name}")
                                    effective_table_entries.append((
                                        derived_table,
                                        {
                                            "has_mismatch": False,
                                            "actual_table": None,
                                            "sources": derived_sources,
                                        },
                                    ))
                                continue
                            solution_parser_skipped[solution_info["solution_name"]].add(original_name)
                            parser_filtered_tables.add(original_name)
                            continue
                        if not is_valid_table_candidate(original_name):
                            continue
                        effective_table_entries.append((original_name, table_info))

                    if (
                        effective_table_entries
                        and log_table_candidates
                        and not used_loganalytics_fallback
                    ):
                        extracted_lower = {
                            name.lower()
                            for name, _ in effective_table_entries
                            if isinstance(name, str)
                        }
                        extracted_names = sorted(
                            name for name, _ in effective_table_entries if isinstance(name, str)
                        )
                        for log_name in log_table_candidates:
                            if log_name.lower() not in extracted_lower:
                                add_issue(
                                    issues,
                                    solution_name=solution_info["solution_name"],
                                    solution_folder=solution_info["solution_folder"],
                                    connector_id=connector_id,
                                    connector_title=connector_title,
                                    connector_publisher=connector_publisher,
                                    connector_file=relative_path,
                                    reason="loganalytics_mismatch",
                                    details=f"logAnalyticsTableId '{log_name}' differs from detected table tokens {extracted_names}",
                                )

                    for table_name, table_info in effective_table_entries:
                        if table_name and not is_valid_table_candidate(table_name):
                            continue
                        if table_name and table_name.lower() in parser_names_lower:
                            continue
                        if not table_name:
                            continue
                        plural_sources = table_info.get("plural_sources") or []
                        mismatch = table_info.get("has_mismatch", False)
                        actual_name = table_info.get("actual_table")
                        if plural_sources:
                            plural_list = ", ".join(sorted(plural_sources))
                            add_issue(
                                issues,
                                solution_name=solution_info["solution_name"],
                                solution_folder=solution_info["solution_folder"],
                                connector_id=connector_id,
                                connector_title=connector_title,
                                connector_publisher=connector_publisher,
                                connector_file=relative_path,
                                reason="plural_table_name",
                                details=f"Plural table name(s) {plural_list} replaced with '{table_name}'.",
                            )
                        row_key = (
                            solution_info["solution_name"],
                            solution_info["solution_folder"],
                            solution_info["solution_publisher_id"],
                            solution_info["solution_offer_id"],
                            solution_info["solution_first_publish_date"],
                            solution_info["solution_last_publish_date"],
                            solution_info["solution_version"],
                            solution_info["solution_support_name"],
                            solution_info["solution_support_tier"],
                            solution_info["solution_support_link"],
                            solution_info["solution_author_name"],
                            solution_info["solution_categories"],
                            connector_id,
                            connector_publisher,
                            connector_title,
                            connector_description,
                            connector_instruction_steps,
                            connector_permissions,
                            connector_id_generated,
                            table_name,
                        )
                        combo_key = (solution_info["solution_name"], connector_id, table_name)
                        if not is_azuredeploy:
                            combo_with_non_azure.add(combo_key)

                        existing_flag = grouped_rows[row_key].get(relative_path)
                        if existing_flag is None or (existing_flag and not is_azuredeploy):
                            grouped_rows[row_key][relative_path] = is_azuredeploy
                        metadata_entry = row_key_metadata.setdefault(row_key, {
                            "table_detection_methods": set(),
                        })
                        sources = table_info.get("sources")
                        if sources:
                            existing_sources: Set[str] = metadata_entry.setdefault("table_detection_methods", set())
                            if isinstance(sources, set):
                                existing_sources.update(sources)
                            else:
                                existing_sources.update(set(sources))
                        produced_rows += 1

                    if parser_expansion_details:
                        expansion_messages = []
                        for parser_name in sorted(parser_expansion_details.keys()):
                            resolved_tables = ", ".join(sorted(parser_expansion_details[parser_name]))
                            expansion_messages.append(f"{parser_name}: {resolved_tables}")
                        add_issue(
                            issues,
                            solution_name=solution_info["solution_name"],
                            solution_folder=solution_info["solution_folder"],
                            connector_id=connector_id,
                            connector_title=connector_title,
                            connector_publisher=connector_publisher,
                            connector_file=relative_path,
                            reason="parser_tables_resolved",
                            details="Parser functions expanded to tables -> " + "; ".join(expansion_messages),
                        )

                    if produced_rows == 0:
                        if not had_table_definitions:
                            reason = "no_table_definitions"
                            details = "Connector definition did not expose any table tokens."
                            # Still include connector in output with empty table
                            row_key = (
                                solution_info["solution_name"],
                                solution_info["solution_folder"],
                                solution_info["solution_publisher_id"],
                                solution_info["solution_offer_id"],
                                solution_info["solution_first_publish_date"],
                                solution_info["solution_last_publish_date"],
                                solution_info["solution_version"],
                                solution_info["solution_support_name"],
                                solution_info["solution_support_tier"],
                                solution_info["solution_support_link"],
                                solution_info["solution_author_name"],
                                solution_info["solution_categories"],
                                connector_id,
                                connector_publisher,
                                connector_title,
                                connector_description,
                                connector_instruction_steps,
                                connector_permissions,
                                connector_id_generated,
                                "",  # Empty table name
                            )
                            existing_flag = grouped_rows[row_key].get(relative_path)
                            if existing_flag is None or (existing_flag and not is_azuredeploy):
                                grouped_rows[row_key][relative_path] = is_azuredeploy
                            produced_rows += 1
                        elif parser_filtered_tables and len(parser_filtered_tables) == total_table_entries:
                            reason = "parser_tables_only"
                            tables_list = ", ".join(sorted(parser_filtered_tables))
                            details = f"All table tokens correspond to parser functions: {tables_list}"
                        elif parser_filtered_tables:
                            reason = "partial_parser_tables"
                            tables_list = ", ".join(sorted(parser_filtered_tables))
                            details = f"Parser tables removed output rows: {tables_list}"
                        else:
                            reason = "table_detection_failed"
                            details = "Table tokens were detected but none could be emitted."
                        if used_loganalytics_fallback and reason == "no_table_definitions":
                            details = "No table tokens detected; emitted tables solely from logAnalyticsTableId values but still filtered."
                        # Only log issue for cases other than no_table_definitions (which is now included in output)
                        if reason != "no_table_definitions":
                            add_issue(
                                issues,
                                solution_name=solution_info["solution_name"],
                                solution_folder=solution_info["solution_folder"],
                                connector_id=connector_id,
                                connector_title=connector_title,
                                connector_publisher=connector_publisher,
                                connector_file=relative_path,
                                reason=reason,
                                details=details,
                            )

        if has_data_connectors_dir and not has_valid_connector:
            missing_connector_json.append(solution_dir.name)
            add_issue(
                issues,
                solution_name=solution_info["solution_name"],
                solution_folder=solution_info["solution_folder"],
                reason="missing_connector_json",
                details="Data Connectors folder exists but contains no readable connector JSON files.",
            )
        if not has_metadata and has_valid_connector:
            missing_metadata_with_connectors.append(solution_dir.name)
            add_issue(
                issues,
                solution_name=solution_info["solution_name"],
                solution_folder=solution_info["solution_folder"],
                reason="missing_solution_metadata",
                details="Solution contains connectors but is missing SolutionMetadata.json.",
            )
        
        # Track solutions that truly have no connectors (no Data Connectors dir or no valid connectors)
        if not data_connectors_dir.exists() or not has_valid_connector:
            solutions_without_connectors.add(solution_info["solution_name"])

    # Add rows for solutions without any connectors
    for solution_name in sorted(solutions_without_connectors):
        solution_info = all_solutions_info[solution_name]
        # Create a row with solution info but empty connector and table fields
        row_key = (
            solution_info["solution_name"],
            solution_info["solution_folder"],
            solution_info["solution_publisher_id"],
            solution_info["solution_offer_id"],
            solution_info["solution_first_publish_date"],
            solution_info["solution_last_publish_date"],
            solution_info["solution_version"],
            solution_info["solution_support_name"],
            solution_info["solution_support_tier"],
            solution_info["solution_support_link"],
            solution_info["solution_author_name"],
            solution_info["solution_categories"],
            "",  # connector_id
            "",  # connector_publisher
            "",  # connector_title
            "",  # connector_description
            "",  # connector_instruction_steps
            "",  # connector_permissions
            False,  # connector_id_generated
            "",  # table_name
        )
        grouped_rows[row_key] = {}  # Empty file map for solutions without connectors

    rows: List[Dict[str, str]] = []
    
    # Track unique connectors for connectors.csv with collection method info
    connector_info_map: Dict[str, Dict[str, Any]] = {}
    # Track connector -> json_content for collection method detection
    connector_json_content: Dict[str, Tuple[str, str]] = {}  # connector_id -> (json_content, filename)
    
    for row_key in sorted(grouped_rows.keys()):
        path_map = grouped_rows[row_key]
        combo_key = (row_key[0], row_key[12], row_key[19])  # solution_name, connector_id, table_name
        non_azure_files = sorted([path for path, is_azure in path_map.items() if not is_azure])
        if non_azure_files:
            file_list = non_azure_files
        elif combo_key in combo_with_non_azure:
            continue
        else:
            file_list = sorted(path_map.keys())
        
        # Convert file paths to GitHub URLs
        github_urls = []
        for file_path in file_list:
            # Convert backslashes to forward slashes and prepend Solutions/
            normalized = file_path.replace("\\", "/")
            # URL encode all path components to handle spaces
            github_url = f"{GITHUB_REPO_URL}/Solutions/{quote(row_key[1])}/{quote('Data Connectors')}/{quote(normalized)}"
            github_urls.append(github_url)
        
        support_info = row_key_metadata.get(row_key, {"table_detection_methods": set()})
        
        # Build row data WITHOUT collection_method for main CSV (to match master branch format)
        row_data = {
            "Table": row_key[19],
            "solution_name": row_key[0],
            "solution_folder": f"{GITHUB_REPO_URL}/Solutions/{quote(row_key[1])}",
            "solution_publisher_id": row_key[2],
            "solution_offer_id": row_key[3],
            "solution_first_publish_date": row_key[4],
            "solution_last_publish_date": row_key[5],
            "solution_version": row_key[6],
            "solution_support_name": row_key[7],
            "solution_support_tier": row_key[8],
            "solution_support_link": row_key[9],
            "solution_author_name": row_key[10],
            "solution_categories": row_key[11],
            "connector_id": row_key[12],
            "connector_publisher": row_key[13],
            "connector_title": row_key[14],
            "connector_description": row_key[15],
            "connector_instruction_steps": row_key[16],
            "connector_permissions": row_key[17],
            "connector_id_generated": "true" if row_key[18] else "false",
            "connector_files": ";".join(github_urls),
            "is_unique": "true" if len(file_list) == 1 else "false",
        }
        
        # Only add detection methods if flag is set
        if args.show_detection_methods:
            row_data["table_detection_methods"] = ";".join(sorted(support_info.get("table_detection_methods", set()))) if support_info.get("table_detection_methods") else ""
        
        rows.append(row_data)
        solution_rows_kept[row_key[0]] += 1
        
        # Track connector info for connectors.csv
        connector_id = row_key[12]
        if connector_id and connector_id not in connector_info_map:
            connector_info_map[connector_id] = {
                'connector_id': connector_id,
                'connector_publisher': row_key[13],
                'connector_title': row_key[14],
                'connector_description': row_key[15],
                'connector_instruction_steps': row_key[16],
                'connector_permissions': row_key[17],
                'connector_id_generated': "true" if row_key[18] else "false",
                'connector_files': ";".join(github_urls),
                'solution_name': row_key[0],  # First solution name (can be multiple)
            }

    # Now analyze collection methods for all connectors
    # We need to read JSON files again to get content for analysis
    for solution_dir in sorted([p for p in solutions_dir.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        for dc_folder_name in ["Data Connectors", "DataConnectors", "Data Connector"]:
            data_connectors_dir = solution_dir / dc_folder_name
            if not data_connectors_dir.exists():
                continue
            for json_path in sorted(data_connectors_dir.rglob("*.json")):
                # Skip non-connector files
                filename = json_path.name.lower()
                if filename in ['function.json', 'host.json', 'proxies.json', 'local.settings.json']:
                    continue
                try:
                    content = json_path.read_text(encoding='utf-8')
                    data = read_json(json_path)
                    if data is None:
                        continue
                    connector_entries = find_connector_objects(data)
                    for entry in connector_entries:
                        conn_id = entry.get('id', '')
                        if conn_id and conn_id not in connector_json_content:
                            connector_json_content[conn_id] = (content, json_path.name)
                except Exception:
                    continue
    
    # Build connector -> tables mapping for table-based collection method detection
    connector_tables_map: Dict[str, List[str]] = defaultdict(list)
    for row in rows:
        connector_id = row.get('connector_id', '')
        table_name = row.get('Table', '')
        if connector_id and table_name:
            connector_tables_map[connector_id].append(table_name)
    
    # Build connectors with collection method info
    connectors_data: List[Dict[str, str]] = []
    
    for connector_id, info in sorted(connector_info_map.items()):
        json_content, filename = connector_json_content.get(connector_id, ("", ""))
        
        # Get table metadata for this connector's tables
        table_metadata_list = []
        for table_name in connector_tables_map.get(connector_id, []):
            if table_name in tables_reference:
                table_metadata_list.append(tables_reference[table_name])
        
        collection_method, detection_reason, all_matches = determine_collection_method(
            connector_id=info['connector_id'],
            connector_title=info['connector_title'],
            connector_description=info['connector_description'],
            json_content=json_content,
            filename=filename,
            table_metadata=table_metadata_list if table_metadata_list else None,
        )
        
        connectors_data.append({
            'connector_id': info['connector_id'],
            'connector_publisher': info['connector_publisher'],
            'connector_title': info['connector_title'],
            'connector_description': info['connector_description'],
            'connector_instruction_steps': info['connector_instruction_steps'],
            'connector_permissions': info['connector_permissions'],
            'connector_id_generated': info['connector_id_generated'],
            'connector_files': info['connector_files'],
            'collection_method': collection_method,
            'collection_method_reason': detection_reason,
        })
    
    # Build solutions data
    solutions_data: List[Dict[str, str]] = []
    for solution_name, info in sorted(all_solutions_info.items()):
        solutions_data.append({
            'solution_name': info['solution_name'],
            'solution_folder': f"{GITHUB_REPO_URL}/Solutions/{quote(info['solution_folder'])}",
            'solution_publisher_id': info['solution_publisher_id'],
            'solution_offer_id': info['solution_offer_id'],
            'solution_first_publish_date': info['solution_first_publish_date'],
            'solution_last_publish_date': info['solution_last_publish_date'],
            'solution_version': info['solution_version'],
            'solution_support_name': info['solution_support_name'],
            'solution_support_tier': info['solution_support_tier'],
            'solution_support_link': info['solution_support_link'],
            'solution_author_name': info['solution_author_name'],
            'solution_categories': info['solution_categories'],
            'has_connectors': 'true' if solution_name not in solutions_without_connectors else 'false',
        })
    
    # Build tables data from tables_reference.csv metadata (tables_reference was loaded early)
    # Collect all unique tables from connector data
    all_tables: Set[str] = set()
    for row in rows:
        table = row.get('Table', '')
        if table:
            all_tables.add(table)
    
    # Apply solution overrides to rows early, before building table_support_tiers
    # This ensures solution-level overrides (like support_tier fixes) affect derived table data
    if overrides:
        rows = apply_overrides_to_data(rows, overrides, 'solution', 'solution_name')
    
    # Build table -> support_tier mapping from solution data
    # For each table, collect all unique support tiers from associated solutions
    table_support_tiers: Dict[str, Set[str]] = {}
    for row in rows:
        table = row.get('Table', '')
        support_tier = row.get('solution_support_tier', '')
        if table and support_tier:
            if table not in table_support_tiers:
                table_support_tiers[table] = set()
            table_support_tiers[table].add(support_tier)
    
    # Build tables data with metadata from tables_reference.csv
    tables_data: List[Dict[str, str]] = []
    for table_name in sorted(all_tables):
        ref = tables_reference.get(table_name, {})
        
        # Determine support_tier based on associated solutions
        tiers = table_support_tiers.get(table_name, set())
        if len(tiers) == 0:
            support_tier = ''
        elif len(tiers) == 1:
            support_tier = next(iter(tiers))
        else:
            support_tier = 'Various'
        
        # Use collection_method from tables_reference.csv if available
        collection_method = ref.get('collection_method', '')
        
        tables_data.append({
            'table_name': table_name,
            'description': ref.get('description', ''),
            'category': ref.get('category', ''),
            'support_tier': support_tier,
            'collection_method': collection_method,
            'resource_types': ref.get('resource_types', ''),
            'source_azure_monitor': ref.get('source_azure_monitor', ''),
            'source_defender_xdr': ref.get('source_defender_xdr', ''),
            'azure_monitor_doc_link': ref.get('azure_monitor_doc_link', ''),
            'defender_xdr_doc_link': ref.get('defender_xdr_doc_link', ''),
            'basic_logs_eligible': ref.get('basic_logs_eligible', ''),
            'supports_transformations': ref.get('supports_transformations', ''),
            'ingestion_api_supported': ref.get('ingestion_api_supported', ''),
        })
    
    # Build simplified mapping (key fields only)
    mapping_data: List[Dict[str, str]] = []
    seen_mappings: Set[Tuple[str, str, str]] = set()
    for row in rows:
        key = (row['solution_name'], row.get('connector_id', ''), row.get('Table', ''))
        if key not in seen_mappings:
            seen_mappings.add(key)
            mapping_data.append({
                'solution_name': row['solution_name'],
                'connector_id': row.get('connector_id', ''),
                'table_name': row.get('Table', ''),
            })

    # Apply overrides to all data sets
    if overrides:
        # Apply table overrides (key field is 'Table' in rows, 'table_name' in tables_data)
        rows = apply_overrides_to_data(rows, overrides, 'table', 'Table')
        tables_data = apply_overrides_to_data(tables_data, overrides, 'table', 'table_name')
        mapping_data = apply_overrides_to_data(mapping_data, overrides, 'table', 'table_name')
        
        # Apply connector overrides
        connectors_data = apply_overrides_to_data(connectors_data, overrides, 'connector', 'connector_id')
        rows = apply_overrides_to_data(rows, overrides, 'connector', 'connector_id')
        
        # Apply solution overrides (rows already had solution overrides applied earlier for table_support_tiers)
        solutions_data = apply_overrides_to_data(solutions_data, overrides, 'solution', 'solution_name')
        
        print(f"Applied overrides to data")

    # Write main CSV (without collection_method to match master branch format)
    fieldnames = [
        "Table",
        "solution_name",
        "solution_folder",
        "solution_publisher_id",
        "solution_offer_id",
        "solution_first_publish_date",
        "solution_last_publish_date",
        "solution_version",
        "solution_support_name",
        "solution_support_tier",
        "solution_support_link",
        "solution_author_name",
        "solution_categories",
        "connector_id",
        "connector_publisher",
        "connector_title",
        "connector_description",
        "connector_instruction_steps",
        "connector_permissions",
        "connector_id_generated",
        "connector_files",
        "is_unique",
    ]
    
    if args.show_detection_methods:
        fieldnames.append("table_detection_methods")

    with output_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    
    # Write connectors.csv
    connectors_fieldnames = [
        'connector_id',
        'connector_publisher',
        'connector_title',
        'connector_description',
        'connector_instruction_steps',
        'connector_permissions',
        'connector_id_generated',
        'connector_files',
        'collection_method',
        'collection_method_reason',
    ]
    connectors_path = args.connectors_csv.resolve()
    with connectors_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=connectors_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(connectors_data)
    
    # Write solutions.csv
    solutions_fieldnames = [
        'solution_name',
        'solution_folder',
        'solution_publisher_id',
        'solution_offer_id',
        'solution_first_publish_date',
        'solution_last_publish_date',
        'solution_version',
        'solution_support_name',
        'solution_support_tier',
        'solution_support_link',
        'solution_author_name',
        'solution_categories',
        'has_connectors',
    ]
    solutions_path = args.solutions_csv.resolve()
    with solutions_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=solutions_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(solutions_data)
    
    # Write tables.csv
    tables_fieldnames = [
        'table_name',
        'description',
        'category',
        'support_tier',
        'collection_method',
        'resource_types',
        'source_azure_monitor',
        'source_defender_xdr',
        'azure_monitor_doc_link',
        'defender_xdr_doc_link',
        'basic_logs_eligible',
        'supports_transformations',
        'ingestion_api_supported',
    ]
    tables_path = args.tables_csv.resolve()
    with tables_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=tables_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(tables_data)
    
    # Write simplified mapping CSV
    mapping_fieldnames = ['solution_name', 'connector_id', 'table_name']
    mapping_path = args.mapping_csv.resolve()
    with mapping_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=mapping_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(mapping_data)

    report_fieldnames = [
        "solution_name",
        "solution_folder",
        "connector_id",
        "connector_title",
        "connector_publisher",
        "connector_file",
        "reason",
        "details",
    ]
    
    # Filter out parser_tables_resolved and add GitHub URLs to connector_file
    filtered_issues = []
    for issue in issues:
        if issue.get("reason") == "parser_tables_resolved":
            continue
        # Convert solution_folder to GitHub URL
        if issue.get("solution_folder"):
            issue["solution_folder"] = f"{GITHUB_REPO_URL}/Solutions/{quote(issue['solution_folder'])}"
        # Convert connector_file path to GitHub URL if present
        if issue.get("connector_file"):
            solution_name = issue.get("solution_name", "")
            # Extract original folder name from solution_folder URL or use solution_name
            folder_name = solution_name
            normalized = issue["connector_file"].replace("\\", "/")
            issue["connector_file"] = f"{GITHUB_REPO_URL}/Solutions/{quote(folder_name)}/Data Connectors/{quote(normalized)}"
        filtered_issues.append(issue)
    
    with report_path.open("w", encoding="utf-8", newline="") as report_file:
        writer = csv.DictWriter(report_file, fieldnames=report_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(filtered_issues)

    # Print summary
    if missing_connector_json:
        print("Solutions with Data Connectors folder but no connector JSON detected:")
        for name in missing_connector_json:
            print(f" - {name}")
    else:
        print("All Data Connectors folders contained connector definitions.")

    if missing_metadata_with_connectors:
        print("Solutions containing connectors but missing SolutionMetadata.json:")
        for name in missing_metadata_with_connectors:
            print(f" - {name}")
    else:
        print("All connector-producing solutions include SolutionMetadata.json.")

    solutions_missing_due_to_parsers = [
        name
        for name, skipped_tables in solution_parser_skipped.items()
        if skipped_tables and solution_rows_kept.get(name, 0) == 0
    ]
    if solutions_missing_due_to_parsers:
        print("Solutions skipped entirely because tables map to parser functions:")
        for name in sorted(solutions_missing_due_to_parsers):
            skipped_list = ", ".join(sorted(solution_parser_skipped[name]))
            print(f" - {name} (parser tables: {skipped_list})")

    # Print collection method distribution
    method_counts: Dict[str, int] = defaultdict(int)
    for conn in connectors_data:
        method_counts[conn['collection_method']] += 1
    
    print(f"\nCollection Method Distribution ({len(connectors_data)} connectors):")
    print("-" * 50)
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(connectors_data) * 100) if connectors_data else 0
        print(f"  {method:30} {count:4} ({pct:.1f}%)")

    print(f"\nWrote {len(rows)} rows to {safe_relative(output_path, repo_root)}")
    print(f"Wrote {len(connectors_data)} connectors to {safe_relative(connectors_path, repo_root)}")
    print(f"Wrote {len(solutions_data)} solutions to {safe_relative(solutions_path, repo_root)}")
    print(f"Wrote {len(tables_data)} tables to {safe_relative(tables_path, repo_root)}")
    print(f"Wrote {len(mapping_data)} mappings to {safe_relative(mapping_path, repo_root)}")
    print(f"Logged {len(issues)} connector issues to {safe_relative(report_path, repo_root)}")


if __name__ == "__main__":
    main()
