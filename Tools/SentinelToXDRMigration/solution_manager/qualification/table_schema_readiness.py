"""AI-ready custom table schema readiness discovery and validation (AB#65158259).

Discovers ``Microsoft.OperationalInsights/workspaces/tables`` resources across:
- Bare root resource JSON files (e.g., ``*_tables.json``)
- Standard ARM template ``resources[]`` arrays
- Child ``tables`` resources nested under ``Microsoft.OperationalInsights/workspaces``
- Nested ``Microsoft.Resources/deployments`` (``properties.template.resources[]``)
- Packaged V3/V3.1 content templates (``resources[].properties.mainTemplate.resources[]``)

Provides static validation helpers for ``VAL-TBL-01..03`` and live receipt evaluation
helpers for ``QUAL-TBL-01..03`` with minimum-blocking adoption mode support.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


TABLE_RESOURCE_TYPE = "microsoft.operationalinsights/workspaces/tables"
WORKSPACE_RESOURCE_TYPE = "microsoft.operationalinsights/workspaces"
DEPLOYMENT_RESOURCE_TYPE = "microsoft.resources/deployments"

# Standard Log Analytics system columns that do not require author-provided custom descriptions.
SYSTEM_COLUMN_NAMES_LOWER: Set[str] = {
    "timegenerated",
    "tenantid",
    "type",
    "_resourceid",
    "_subscriptionid",
    "_itemid",
    "_billedsize",
    "_isbillable",
    "sourcesystem",
    "mg",
    "managementgroupname",
    "computer",
    "rawdata",
}

TRIVIAL_PLACEHOLDER_VALUES: Set[str] = {
    "todo",
    "tbd",
    "n/a",
    "na",
    "none",
    "null",
    "unknown",
    "description",
    "column",
    "field",
    "table",
    "custom table",
    "custom column",
    "column description",
    "table description",
    "placeholder",
    "-",
    "_",
    ".",
}


@dataclass
class ColumnSchemaRecord:
    """Represents a single column in a custom table schema."""

    name: str
    column_type: str = ""
    description: str = ""
    is_system_column: bool = False
    is_unresolved_expression: bool = False


@dataclass
class TableSchemaRecord:
    """Represents a discovered Microsoft.OperationalInsights/workspaces/tables resource."""

    table_name: str
    file_rel_path: str
    is_packaged: bool
    table_description: str = ""
    columns: List[ColumnSchemaRecord] = field(default_factory=list)
    unresolved_errors: List[str] = field(default_factory=list)
    table_kind: str = "custom_log"  # "custom_log" | "microsoft_standard_config"
    is_microsoft_standard_table_config: bool = False


@dataclass
class SolutionTableInventory:
    """Aggregated custom table schema inventory for a solution."""

    source_tables: List[TableSchemaRecord] = field(default_factory=list)
    packaged_tables: List[TableSchemaRecord] = field(default_factory=list)
    standard_table_configs: List[TableSchemaRecord] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)

    @property
    def has_any_custom_tables(self) -> bool:
        return bool(self.source_tables or self.packaged_tables or self.parse_errors)

    @property
    def has_only_standard_table_configs(self) -> bool:
        return bool(self.standard_table_configs) and not self.has_any_custom_tables

    @property
    def custom_source_tables(self) -> List[TableSchemaRecord]:
        return [r for r in self.source_tables if not r.is_microsoft_standard_table_config]

    @property
    def custom_packaged_tables(self) -> List[TableSchemaRecord]:
        return [r for r in self.packaged_tables if not r.is_microsoft_standard_table_config]

    @property
    def standard_source_tables(self) -> List[TableSchemaRecord]:
        return [r for r in self.standard_table_configs if not r.is_packaged]

    @property
    def standard_packaged_tables(self) -> List[TableSchemaRecord]:
        return [r for r in self.standard_table_configs if r.is_packaged]

    @property
    def canonical_table_names(self) -> List[str]:
        seen: Dict[str, str] = {}
        for rec in (*self.source_tables, *self.packaged_tables):
            key = rec.table_name.lower()
            if key not in seen and rec.table_name != "<unresolved_table>":
                seen[key] = rec.table_name
        return sorted(seen.values(), key=lambda s: s.lower())

    @property
    def standard_table_config_names(self) -> List[str]:
        seen: Dict[str, str] = {}
        for rec in self.standard_table_configs:
            key = rec.table_name.lower()
            if key not in seen:
                seen[key] = rec.table_name
        return sorted(seen.values(), key=lambda s: s.lower())


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _normalize_identifier_tokens(identifier: str) -> str:
    """Normalize an identifier like 'OnePasswordEventLogs_CL' or 'user_name_s' for repetition checks."""
    cleaned = re.sub(r"_(cl|s|d|b|g|t)$", "", (identifier or "").strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", cleaned)
    cleaned = re.sub(r"[_\-\s]+", " ", cleaned)
    return cleaned.strip().lower()


def _is_arm_expression_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    return stripped.startswith("[") and stripped.endswith("]")


def is_meaningful_description(description: Any, entity_name: str = "") -> Tuple[bool, str]:
    """Return (is_valid, reason_if_invalid) for a table or column description."""
    if not isinstance(description, str):
        return False, "missing_or_non_string"
    normalized = _normalize_whitespace(description)
    if not normalized:
        return False, "empty"
    if _is_arm_expression_string(normalized):
        return False, "unresolved_arm_expression"

    lowered = normalized.lower().rstrip(".")
    if lowered in TRIVIAL_PLACEHOLDER_VALUES:
        return False, f"trivial_placeholder({normalized!r})"

    if entity_name:
        raw_entity_lower = entity_name.strip().lower().rstrip(".")
        tokenized_entity = _normalize_identifier_tokens(entity_name)
        normalized_words = re.sub(r"[_\-\s]+", " ", lowered).strip()
        if lowered == raw_entity_lower or (tokenized_entity and normalized_words == tokenized_entity):
            return False, f"repeats_identifier({entity_name})"

    return True, ""


def _resolve_arm_value(
    raw_value: Any,
    parameters: Dict[str, Any],
    variables: Dict[str, Any],
) -> Tuple[Optional[str], bool]:
    """Best-effort static resolution for ARM string/expression values.

    Returns ``(resolved_string, is_unresolved_expression)``.
    """
    if not isinstance(raw_value, str):
        return None, False
    stripped = raw_value.strip()
    if not _is_arm_expression_string(stripped):
        return stripped, False

    expr = stripped[1:-1].strip()
    # Direct parameters('foo') or variables('bar')
    m_param = re.fullmatch(r"parameters\(\s*'([^']+)'\s*\)", expr, flags=re.IGNORECASE)
    if m_param:
        p_name = m_param.group(1)
        p_obj = parameters.get(p_name)
        if isinstance(p_obj, dict) and isinstance(p_obj.get("defaultValue"), str):
            return p_obj["defaultValue"].strip(), False
        return None, True

    m_var = re.fullmatch(r"variables\(\s*'([^']+)'\s*\)", expr, flags=re.IGNORECASE)
    if m_var:
        v_name = m_var.group(1)
        v_val = variables.get(v_name)
        if isinstance(v_val, str) and not _is_arm_expression_string(v_val):
            return v_val.strip(), False
        return None, True

    # Extract last segment from concat(..., '/TableName_CL') or format('{0}/{1}', ..., 'TableName_CL')
    literals = re.findall(r"'([^']*)'", expr)
    for lit in reversed(literals):
        cleaned = lit.strip().lstrip("/")
        if cleaned and not cleaned.startswith("{") and ("_CL" in cleaned or "/" in lit):
            table_candidate = cleaned.split("/")[-1].strip()
            if table_candidate and not table_candidate.startswith("{"):
                return table_candidate, False

    # Look for variables('...') inside concat/format
    var_refs = re.findall(r"variables\(\s*'([^']+)'\s*\)", expr, flags=re.IGNORECASE)
    for v_name in reversed(var_refs):
        v_val = variables.get(v_name)
        if isinstance(v_val, str) and not _is_arm_expression_string(v_val):
            candidate = v_val.strip().split("/")[-1].strip()
            if candidate:
                return candidate, False

    param_refs = re.findall(r"parameters\(\s*'([^']+)'\s*\)", expr, flags=re.IGNORECASE)
    for p_name in reversed(param_refs):
        p_obj = parameters.get(p_name)
        if isinstance(p_obj, dict) and isinstance(p_obj.get("defaultValue"), str):
            candidate = p_obj["defaultValue"].strip().split("/")[-1].strip()
            if candidate:
                return candidate, False

    return None, True


def _extract_table_name(
    resource: Dict[str, Any],
    schema_obj: Dict[str, Any],
    parameters: Dict[str, Any],
    variables: Dict[str, Any],
) -> Tuple[str, List[str]]:
    """Extract canonical custom table name from properties.schema.name or resource.name."""
    errors: List[str] = []
    schema_name = schema_obj.get("name")
    if isinstance(schema_name, str) and schema_name.strip():
        resolved, unresolved = _resolve_arm_value(schema_name, parameters, variables)
        if resolved:
            return resolved.split("/")[-1].strip(), errors
        if unresolved:
            errors.append(f"Unresolved ARM expression in properties.schema.name: {schema_name!r}")

    res_name = resource.get("name")
    if isinstance(res_name, str) and res_name.strip():
        resolved, unresolved = _resolve_arm_value(res_name, parameters, variables)
        if resolved:
            return resolved.split("/")[-1].strip(), errors
        if unresolved:
            errors.append(f"Unresolved ARM expression in resource.name: {res_name!r}")

    errors.append("Unable to resolve table name from properties.schema.name or resource.name")
    return "<unresolved_table>", errors


def _resolve_arm_description_value(
    raw_value: Any,
    parameters: Dict[str, Any],
    variables: Dict[str, Any],
) -> Tuple[Optional[str], bool]:
    """Strict static resolution for table and column description values.

    Only plain strings or direct ``[parameters('x')]`` / ``[variables('y')]``
    references that resolve to a plain static string are accepted. Complex or
    unresolved ARM expressions (such as ``concat(...)`` or ``format(...)``) are
    never reduced to partial substrings so preservation checks cannot pass on
    misleading reduced values.
    """
    if not isinstance(raw_value, str):
        return None, False
    stripped = raw_value.strip()
    if not _is_arm_expression_string(stripped):
        return stripped, False

    expr = stripped[1:-1].strip()
    m_param = re.fullmatch(r"parameters\(\s*'([^']+)'\s*\)", expr, flags=re.IGNORECASE)
    if m_param:
        p_name = m_param.group(1)
        p_obj = parameters.get(p_name)
        if isinstance(p_obj, dict) and isinstance(p_obj.get("defaultValue"), str):
            def_val = p_obj["defaultValue"].strip()
            if not _is_arm_expression_string(def_val):
                return def_val, False
        return None, True

    m_var = re.fullmatch(r"variables\(\s*'([^']+)'\s*\)", expr, flags=re.IGNORECASE)
    if m_var:
        v_name = m_var.group(1)
        v_val = variables.get(v_name)
        if isinstance(v_val, str) and not _is_arm_expression_string(v_val.strip()):
            return v_val.strip(), False
        return None, True

    return None, True


def _is_standard_table_name(table_name: str) -> bool:
    """Return True when a resolved table name is a non-custom Microsoft-standard table name."""
    cleaned = (table_name or "").strip()
    if not cleaned or cleaned.startswith("<") or _is_arm_expression_string(cleaned):
        return False
    return not cleaned.lower().endswith("_cl")


def _parse_table_resource(
    resource: Dict[str, Any],
    file_rel_path: str,
    is_packaged: bool,
    parameters: Dict[str, Any],
    variables: Dict[str, Any],
) -> TableSchemaRecord:
    errors: List[str] = []
    props = resource.get("properties")
    if not isinstance(props, dict):
        return TableSchemaRecord(
            table_name=str(resource.get("name") or "<unknown_table>"),
            file_rel_path=file_rel_path,
            is_packaged=is_packaged,
            unresolved_errors=["Table resource is missing a valid 'properties' object."],
        )

    schema_obj = props.get("schema")
    if not isinstance(schema_obj, dict):
        table_name, name_errs = _extract_table_name(resource, {}, parameters, variables)
        if schema_obj is None and not name_errs and _is_standard_table_name(table_name):
            return TableSchemaRecord(
                table_name=table_name,
                file_rel_path=file_rel_path,
                is_packaged=is_packaged,
                table_kind="microsoft_standard_config",
                is_microsoft_standard_table_config=True,
            )
        errors.extend(name_errs)
        errors.append("Table resource 'properties.schema' is missing or not a JSON object.")
        return TableSchemaRecord(
            table_name=table_name,
            file_rel_path=file_rel_path,
            is_packaged=is_packaged,
            unresolved_errors=errors,
        )

    table_name, name_errs = _extract_table_name(resource, schema_obj, parameters, variables)
    errors.extend(name_errs)
    if (
        _is_arm_expression_string(table_name)
        or "parameters(" in table_name.lower()
        or "variables(" in table_name.lower()
    ):
        errors.append(f"Unresolved ARM expression in table name: {table_name!r}")

    raw_desc = schema_obj.get("description")
    table_desc = ""
    if isinstance(raw_desc, str):
        resolved_desc, is_unresolved = _resolve_arm_description_value(raw_desc, parameters, variables)
        if is_unresolved:
            table_desc = raw_desc.strip()
            errors.append(f"Unresolved ARM expression in properties.schema.description: {raw_desc!r}")
        else:
            table_desc = (resolved_desc or "").strip()
    elif raw_desc is not None:
        errors.append("properties.schema.description must be a string.")

    raw_columns = schema_obj.get("columns")
    if raw_columns is None and "customColumns" in schema_obj:
        raw_columns = schema_obj.get("customColumns")

    columns: List[ColumnSchemaRecord] = []
    if raw_columns is None:
        if not name_errs and _is_standard_table_name(table_name):
            return TableSchemaRecord(
                table_name=table_name,
                file_rel_path=file_rel_path,
                is_packaged=is_packaged,
                table_description=table_desc,
                columns=[],
                unresolved_errors=[],
                table_kind="microsoft_standard_config",
                is_microsoft_standard_table_config=True,
            )
        errors.append("properties.schema.columns is missing.")
    elif not isinstance(raw_columns, list):
        errors.append("properties.schema.columns is not a list (possible unresolved ARM expression).")
    else:
        for idx, col in enumerate(raw_columns):
            if not isinstance(col, dict):
                errors.append(f"properties.schema.columns[{idx}] is not an object.")
                continue
            c_name = str(col.get("name") or col.get("columnName") or "").strip()
            c_type = str(col.get("type") or col.get("columnType") or col.get("dataType") or "").strip()
            if not c_name:
                errors.append(f"properties.schema.columns[{idx}] is missing 'name'.")
                continue
            name_unresolved = (
                _is_arm_expression_string(c_name)
                or "parameters(" in c_name.lower()
                or "variables(" in c_name.lower()
            )
            if name_unresolved:
                errors.append(
                    f"properties.schema.columns[{idx}] ('{c_name}') has an unresolved ARM expression in column name."
                )
            raw_c_desc = col.get("description")
            c_desc = ""
            c_unresolved = False
            if isinstance(raw_c_desc, str):
                resolved_c_desc, c_unresolved = _resolve_arm_description_value(raw_c_desc, parameters, variables)
                c_desc = raw_c_desc.strip() if c_unresolved else (resolved_c_desc or "").strip()
            elif raw_c_desc is not None:
                c_unresolved = True
                errors.append(
                    f"properties.schema.columns[{idx}] ('{c_name}') description must be a string."
                )
            if name_unresolved:
                c_unresolved = True
            is_sys = c_name.lower() in SYSTEM_COLUMN_NAMES_LOWER
            columns.append(
                ColumnSchemaRecord(
                    name=c_name,
                    column_type=c_type,
                    description=c_desc,
                    is_system_column=is_sys,
                    is_unresolved_expression=c_unresolved,
                )
            )

    custom_cols = [c for c in columns if not c.is_system_column]
    if not errors and not custom_cols and _is_standard_table_name(table_name):
        return TableSchemaRecord(
            table_name=table_name,
            file_rel_path=file_rel_path,
            is_packaged=is_packaged,
            table_description=table_desc,
            columns=columns,
            unresolved_errors=[],
            table_kind="microsoft_standard_config",
            is_microsoft_standard_table_config=True,
        )

    return TableSchemaRecord(
        table_name=table_name,
        file_rel_path=file_rel_path,
        is_packaged=is_packaged,
        table_description=table_desc,
        columns=columns,
        unresolved_errors=errors,
        table_kind="custom_log",
        is_microsoft_standard_table_config=False,
    )


def _walk_arm_node_for_tables(
    node: Any,
    file_rel_path: str,
    is_packaged: bool,
    parameters: Dict[str, Any],
    variables: Dict[str, Any],
    out_records: List[TableSchemaRecord],
    parent_type: str = "",
) -> None:
    if isinstance(node, list):
        for item in node:
            _walk_arm_node_for_tables(
                item,
                file_rel_path=file_rel_path,
                is_packaged=is_packaged,
                parameters=parameters,
                variables=variables,
                out_records=out_records,
                parent_type=parent_type,
            )
        return

    if not isinstance(node, dict):
        return

    local_params = dict(parameters)
    if isinstance(node.get("parameters"), dict):
        local_params.update(node["parameters"])

    local_vars = dict(variables)
    if isinstance(node.get("variables"), dict):
        local_vars.update(node["variables"])

    res_type = str(node.get("type") or "").strip().lower()
    is_table_res = res_type == TABLE_RESOURCE_TYPE or (
        res_type == "tables" and parent_type == WORKSPACE_RESOURCE_TYPE
    )
    if is_table_res:
        out_records.append(
            _parse_table_resource(
                node,
                file_rel_path=file_rel_path,
                is_packaged=is_packaged,
                parameters=local_params,
                variables=local_vars,
            )
        )

    # Walk direct resources[] array
    if isinstance(node.get("resources"), list):
        _walk_arm_node_for_tables(
            node["resources"],
            file_rel_path=file_rel_path,
            is_packaged=is_packaged,
            parameters=local_params,
            variables=local_vars,
            out_records=out_records,
            parent_type=res_type or parent_type,
        )

    # Walk nested template or V3/V3.1 content templates inside properties
    props = node.get("properties")
    if isinstance(props, dict):
        if isinstance(props.get("template"), dict):
            _walk_arm_node_for_tables(
                props["template"],
                file_rel_path=file_rel_path,
                is_packaged=is_packaged,
                parameters=local_params,
                variables=local_vars,
                out_records=out_records,
                parent_type=res_type or parent_type,
            )
        if isinstance(props.get("mainTemplate"), dict):
            _walk_arm_node_for_tables(
                props["mainTemplate"],
                file_rel_path=file_rel_path,
                is_packaged=is_packaged,
                parameters=local_params,
                variables=local_vars,
                out_records=out_records,
                parent_type=res_type or parent_type,
            )


def discover_tables_in_json_file(
    file_path: Path,
    solution_root: Path,
    is_packaged: Optional[bool] = None,
) -> Tuple[List[TableSchemaRecord], List[str]]:
    """Discover all custom table definitions in a single JSON file."""
    try:
        rel_path = file_path.relative_to(solution_root).as_posix()
    except ValueError:
        rel_path = file_path.as_posix()

    if is_packaged is None:
        is_packaged = rel_path.lower() == "package/maintemplate.json"

    try:
        raw_text = file_path.read_text(encoding="utf-8-sig")
    except Exception as exc:
        return [], [f"{rel_path}: failed to read file ({exc})"]

    # Quick pre-filter: only parse JSON files that mention 'tables' and either 'OperationalInsights' or 'schema'
    lowered_text = raw_text.lower()
    if "tables" not in lowered_text or ("operationalinsights" not in lowered_text and '"schema"' not in lowered_text):
        return [], []

    try:
        doc = json.loads(raw_text)
    except Exception as exc:
        return [], [f"{rel_path}: invalid JSON ({exc})"]

    records: List[TableSchemaRecord] = []
    _walk_arm_node_for_tables(
        doc,
        file_rel_path=rel_path,
        is_packaged=is_packaged,
        parameters={},
        variables={},
        out_records=records,
    )
    return records, []


def discover_solution_tables(
    solution_root: Path,
    candidate_rel_paths: Optional[Iterable[str]] = None,
) -> SolutionTableInventory:
    """Scan a solution directory (or explicit relative paths) for custom table resources."""
    inventory = SolutionTableInventory()
    if not solution_root or not solution_root.exists():
        return inventory

    seen_paths: Set[str] = set()
    files_to_scan: List[Path] = []

    if candidate_rel_paths is not None:
        for rel in candidate_rel_paths:
            norm_rel = str(rel).replace("\\", "/").strip("/")
            if not norm_rel.lower().endswith(".json"):
                continue
            if norm_rel.lower() not in seen_paths:
                seen_paths.add(norm_rel.lower())
                abs_p = solution_root / norm_rel
                if abs_p.is_file():
                    files_to_scan.append(abs_p)
        # Always include Package/mainTemplate.json if present on disk
        pkg_main = solution_root / "Package" / "mainTemplate.json"
        if pkg_main.is_file():
            rel_pkg = pkg_main.relative_to(solution_root).as_posix().lower()
            if rel_pkg not in seen_paths:
                seen_paths.add(rel_pkg)
                files_to_scan.append(pkg_main)
    else:
        for json_p in sorted(solution_root.rglob("*.json")):
            rel_norm = json_p.relative_to(solution_root).as_posix().lower()
            if rel_norm.startswith("package/") and rel_norm != "package/maintemplate.json":
                continue
            if rel_norm not in seen_paths:
                seen_paths.add(rel_norm)
                files_to_scan.append(json_p)

    for fp in files_to_scan:
        records, errs = discover_tables_in_json_file(fp, solution_root)
        inventory.parse_errors.extend(errs)
        for rec in records:
            if rec.is_microsoft_standard_table_config:
                inventory.standard_table_configs.append(rec)
            elif rec.is_packaged:
                inventory.packaged_tables.append(rec)
            else:
                inventory.source_tables.append(rec)

    return inventory


def resolve_table_schema_blocking_mode(
    qualification_evidence: Optional[Dict[str, Any]] = None,
    workflow_state: Optional[Dict[str, Any]] = None,
    default_blocking: bool = True,
) -> bool:
    """Return True to enforce AI-ready table schema requirements as a blocking acceptance gate.

    Table and custom column descriptions (``VAL-TBL-01..03``) are mandatory
    acceptance gates in Validation, local validation, PR CI, and Qualification.
    Advisory PASS overrides are not permitted.
    """
    _ = (qualification_evidence, workflow_state, default_blocking)
    return True


def evaluate_val_tbl_01(
    inventory: SolutionTableInventory,
    enforce_blocking: bool = True,
) -> Tuple[str, str]:
    """Evaluate VAL-TBL-01: Custom table schema description present and meaningful."""
    _ = enforce_blocking
    tables_to_check = inventory.source_tables or inventory.packaged_tables
    if not tables_to_check and not inventory.parse_errors:
        if inventory.standard_table_configs:
            std_names = ", ".join(inventory.standard_table_config_names[:8])
            return (
                "PASS",
                f"Verified 0 authored custom-log tables in solution (found Microsoft-standard table "
                f"configuration only: {std_names}); no custom table schema description gaps.",
            )
        return (
            "PASS",
            "Verified 0 custom Microsoft.OperationalInsights/workspaces/tables resources in solution "
            "(solution uses standard/built-in tables); no custom table schema description gaps.",
        )

    issues: List[str] = list(inventory.parse_errors)
    verified: List[str] = []

    for rec in tables_to_check:
        for err in rec.unresolved_errors:
            if "description" in err or "schema" in err or "name" in err:
                issues.append(f"{rec.file_rel_path} ({rec.table_name}): {err}")
        ok, reason = is_meaningful_description(rec.table_description, rec.table_name)
        if not ok:
            issues.append(
                f"{rec.file_rel_path}: table '{rec.table_name}' has invalid properties.schema.description ({reason})"
            )
        else:
            verified.append(f"{rec.table_name} ({rec.file_rel_path})")

    if issues:
        detail = f"Custom table description gaps ({len(issues)}): " + "; ".join(issues[:6])
        return "FAIL", detail

    return (
        "PASS",
        f"All {len(verified)} custom table definition(s) provide a meaningful properties.schema.description: "
        + ", ".join(verified[:8]),
    )


def evaluate_val_tbl_02(
    inventory: SolutionTableInventory,
    enforce_blocking: bool = True,
) -> Tuple[str, str]:
    """Evaluate VAL-TBL-02: 100% custom table column description coverage."""
    _ = enforce_blocking
    tables_to_check = inventory.source_tables or inventory.packaged_tables
    if not tables_to_check and not inventory.parse_errors:
        if inventory.standard_table_configs:
            std_names = ", ".join(inventory.standard_table_config_names[:8])
            return (
                "PASS",
                f"Verified 0 authored custom-log tables in solution (found Microsoft-standard table "
                f"configuration only: {std_names}); no custom column description gaps.",
            )
        return (
            "PASS",
            "Verified 0 custom Microsoft.OperationalInsights/workspaces/tables resources in solution "
            "(solution uses standard/built-in tables); no custom column description gaps.",
        )

    issues: List[str] = list(inventory.parse_errors)
    total_custom_cols = 0
    documented_custom_cols = 0

    for rec in tables_to_check:
        for err in rec.unresolved_errors:
            if "columns" in err or "schema" in err or "name" in err:
                issues.append(f"{rec.file_rel_path} ({rec.table_name}): {err}")
        custom_cols = [c for c in rec.columns if not c.is_system_column]
        if not custom_cols:
            issues.append(
                f"{rec.file_rel_path}: table '{rec.table_name}' defines 0 custom columns in properties.schema.columns"
            )
            continue

        missing_cols: List[str] = []
        for col in custom_cols:
            total_custom_cols += 1
            if col.is_unresolved_expression:
                missing_cols.append(f"{col.name} (unresolved_arm_expression)")
                continue
            ok, reason = is_meaningful_description(col.description, col.name)
            if not ok:
                missing_cols.append(f"{col.name} ({reason})")
            else:
                documented_custom_cols += 1

        if missing_cols:
            issues.append(
                f"{rec.file_rel_path} ({rec.table_name}): {len(missing_cols)}/{len(custom_cols)} custom column(s) "
                f"missing meaningful description [{', '.join(missing_cols[:8])}]"
            )

    if issues:
        detail = (
            f"Custom column description coverage {documented_custom_cols}/{total_custom_cols}: "
            + "; ".join(issues[:5])
        )
        return "FAIL", detail

    return (
        "PASS",
        f"100% custom column description coverage verified ({documented_custom_cols}/{total_custom_cols} "
        f"custom columns across {len(tables_to_check)} table definition(s); system columns exempted).",
    )


def evaluate_val_tbl_03(
    inventory: SolutionTableInventory,
    enforce_blocking: bool = True,
) -> Tuple[str, str]:
    """Evaluate VAL-TBL-03: Packaged mainTemplate preserves custom table and column descriptions."""
    _ = enforce_blocking
    if not inventory.source_tables and not inventory.packaged_tables and not inventory.parse_errors:
        if inventory.standard_table_configs:
            std_names = ", ".join(inventory.standard_table_config_names[:8])
            return (
                "PASS",
                f"Verified 0 authored custom-log tables in solution (found Microsoft-standard table "
                f"configuration only: {std_names}); no source-to-package custom table description drift.",
            )
        return (
            "PASS",
            "Verified 0 custom Microsoft.OperationalInsights/workspaces/tables resources in solution; "
            "no source-to-package custom table description drift.",
        )

    issues: List[str] = list(inventory.parse_errors)
    for rec in list(inventory.source_tables) + list(inventory.packaged_tables):
        for err in rec.unresolved_errors:
            issues.append(f"{rec.file_rel_path} ({rec.table_name}): {err}")
        for col in rec.columns:
            if not col.is_system_column and col.is_unresolved_expression:
                issues.append(
                    f"{rec.file_rel_path} ({rec.table_name}): column '{col.name}' has unresolved ARM expression"
                )

    if inventory.source_tables and not inventory.packaged_tables:
        issues.append(
            "Source files define custom table(s) "
            f"[{', '.join(sorted({r.table_name for r in inventory.source_tables}))}], "
            "but Package/mainTemplate.json contains 0 custom table resources."
        )

    # Index packaged tables by canonical table name (case-insensitive)
    pkg_by_name: Dict[str, TableSchemaRecord] = {}
    for pkg_rec in inventory.packaged_tables:
        pkg_by_name[pkg_rec.table_name.lower()] = pkg_rec

    # Detect conflicting duplicate source definitions for the same table
    source_by_name: Dict[str, List[TableSchemaRecord]] = {}
    for src_rec in inventory.source_tables:
        source_by_name.setdefault(src_rec.table_name.lower(), []).append(src_rec)

    matched_tables: List[str] = []
    for tbl_lower, src_list in sorted(source_by_name.items()):
        canonical_src = src_list[0]
        merged_src_cols: Dict[str, ColumnSchemaRecord] = {
            c.name.lower(): c for c in canonical_src.columns if not c.is_system_column
        }
        if len(src_list) > 1:
            # Check if duplicate source files disagree on table/column descriptions
            ref_desc = _normalize_whitespace(canonical_src.table_description)
            for other in src_list[1:]:
                if _normalize_whitespace(other.table_description) != ref_desc:
                    issues.append(
                        f"Conflicting duplicate source table descriptions for '{canonical_src.table_name}' "
                        f"between {canonical_src.file_rel_path} and {other.file_rel_path}"
                    )
                for o_col in other.columns:
                    if o_col.is_system_column:
                        continue
                    col_key = o_col.name.lower()
                    if col_key in merged_src_cols:
                        if _normalize_whitespace(o_col.description) != _normalize_whitespace(
                            merged_src_cols[col_key].description
                        ):
                            issues.append(
                                f"Conflicting duplicate source column descriptions for "
                                f"'{canonical_src.table_name}.{o_col.name}' between "
                                f"{canonical_src.file_rel_path} and {other.file_rel_path}"
                            )
                    else:
                        merged_src_cols[col_key] = o_col

        src_ok, src_reason = is_meaningful_description(canonical_src.table_description, canonical_src.table_name)
        if not src_ok:
            issues.append(
                f"Source table '{canonical_src.table_name}' ({canonical_src.file_rel_path}) has invalid "
                f"properties.schema.description ({src_reason}); invalid descriptions cannot satisfy preservation."
            )

        pkg_rec = pkg_by_name.get(tbl_lower)
        if pkg_rec is None:
            if inventory.packaged_tables:
                issues.append(
                    f"Custom table '{canonical_src.table_name}' ({canonical_src.file_rel_path}) is missing from Package/mainTemplate.json"
                )
            continue

        pkg_ok, pkg_reason = is_meaningful_description(pkg_rec.table_description, pkg_rec.table_name)
        if not pkg_ok:
            issues.append(
                f"Packaged table '{pkg_rec.table_name}' ({pkg_rec.file_rel_path}) has invalid "
                f"properties.schema.description ({pkg_reason})"
            )

        src_t_desc = _normalize_whitespace(canonical_src.table_description)
        pkg_t_desc = _normalize_whitespace(pkg_rec.table_description)
        if src_t_desc != pkg_t_desc:
            issues.append(
                f"Table '{canonical_src.table_name}' schema.description drift between {canonical_src.file_rel_path} "
                f"({src_t_desc!r}) and {pkg_rec.file_rel_path} ({pkg_t_desc!r})"
            )

        pkg_cols_by_name = {c.name.lower(): c for c in pkg_rec.columns if not c.is_system_column}
        if not merged_src_cols and not pkg_cols_by_name:
            issues.append(
                f"Table '{canonical_src.table_name}' defines 0 custom columns in both source and package"
            )

        for src_col in merged_src_cols.values():
            s_col_ok, s_col_reason = is_meaningful_description(src_col.description, src_col.name)
            if not s_col_ok or src_col.is_unresolved_expression:
                issues.append(
                    f"Source table '{canonical_src.table_name}' column '{src_col.name}' has invalid "
                    f"description ({'unresolved_arm_expression' if src_col.is_unresolved_expression else s_col_reason})"
                )
            pkg_col = pkg_cols_by_name.get(src_col.name.lower())
            if pkg_col is None:
                issues.append(
                    f"Table '{canonical_src.table_name}' column '{src_col.name}' missing from packaged {pkg_rec.file_rel_path}"
                )
                continue
            p_col_ok, p_col_reason = is_meaningful_description(pkg_col.description, pkg_col.name)
            if not p_col_ok or pkg_col.is_unresolved_expression:
                issues.append(
                    f"Packaged table '{pkg_rec.table_name}' column '{pkg_col.name}' has invalid "
                    f"description ({'unresolved_arm_expression' if pkg_col.is_unresolved_expression else p_col_reason})"
                )
            s_c_desc = _normalize_whitespace(src_col.description)
            p_c_desc = _normalize_whitespace(pkg_col.description)
            if s_c_desc != p_c_desc:
                issues.append(
                    f"Table '{canonical_src.table_name}' column '{src_col.name}' description drift between "
                    f"source ({s_c_desc!r}) and package ({p_c_desc!r})"
                )

        # Also check any packaged-only custom columns not in source
        for col_key, pkg_col in pkg_cols_by_name.items():
            if col_key not in merged_src_cols:
                issues.append(
                    f"Packaged table '{pkg_rec.table_name}' contains undeclared custom column '{pkg_col.name}' "
                    f"not present in source ({canonical_src.file_rel_path})"
                )

        matched_tables.append(canonical_src.table_name)

    # Check packaged tables that have no source table counterpart
    for pkg_key, pkg_rec in sorted(pkg_by_name.items()):
        if pkg_key in source_by_name:
            continue
        ok_t, reason_t = is_meaningful_description(pkg_rec.table_description, pkg_rec.table_name)
        if not ok_t:
            issues.append(
                f"Packaged table '{pkg_rec.table_name}' ({pkg_rec.file_rel_path}) missing meaningful table description ({reason_t})"
            )
        pkg_custom_cols = [c for c in pkg_rec.columns if not c.is_system_column]
        if not pkg_custom_cols:
            issues.append(
                f"Packaged table '{pkg_rec.table_name}' ({pkg_rec.file_rel_path}) defines 0 custom columns"
            )
        missing_pkg_cols = [
            c.name
            for c in pkg_custom_cols
            if c.is_unresolved_expression or not is_meaningful_description(c.description, c.name)[0]
        ]
        if missing_pkg_cols:
            issues.append(
                f"Packaged table '{pkg_rec.table_name}' ({pkg_rec.file_rel_path}) missing column descriptions for: "
                + ", ".join(missing_pkg_cols[:8])
            )
        else:
            matched_tables.append(pkg_rec.table_name)

    if issues:
        detail = f"Package custom table schema preservation gaps ({len(issues)}): " + "; ".join(issues[:5])
        return "FAIL", detail

    return (
        "PASS",
        f"Packaged mainTemplate preserves table and column descriptions for {len(matched_tables)} custom table(s): "
        + ", ".join(matched_tables[:8]),
    )


def build_expected_custom_table_map(inventory: SolutionTableInventory) -> Dict[str, TableSchemaRecord]:
    """Return canonical expected custom tables keyed by lowercased table name."""
    expected: Dict[str, TableSchemaRecord] = {}
    for rec in inventory.packaged_tables:
        if not rec.is_microsoft_standard_table_config and rec.table_name != "<unresolved_table>":
            expected[rec.table_name.lower()] = rec
    for rec in inventory.source_tables:
        if not rec.is_microsoft_standard_table_config and rec.table_name != "<unresolved_table>":
            expected.setdefault(rec.table_name.lower(), rec)
    return expected


def _check_static_table_prerequisites(
    inventory: SolutionTableInventory,
    static_passed: bool = True,
) -> Optional[str]:
    """Return a failure detail string if static VAL-TBL-01..03 prerequisites do not pass."""
    if not static_passed:
        return "Static table schema validation prerequisite (VAL-TBL-01..03) did not pass."
    for check_id, fn in (
        ("VAL-TBL-01", evaluate_val_tbl_01),
        ("VAL-TBL-02", evaluate_val_tbl_02),
        ("VAL-TBL-03", evaluate_val_tbl_03),
    ):
        status, detail = fn(inventory, enforce_blocking=True)
        if status != "PASS":
            return f"Static prerequisite {check_id} failed: {detail}"
    return None


def _check_receipt_integrity_and_target(
    receipt: Any,
    check_id: str,
    target: Optional[Dict[str, Any]] = None,
    *,
    require_workspace_resource_id: bool = False,
    require_workspace_guid: bool = False,
) -> Optional[str]:
    """Validate receipt authenticity, HTTP/auth status, and target workspace binding."""
    if not isinstance(receipt, dict) or not receipt:
        return f"Missing live {check_id} qualification receipt."

    if (
        receipt.get("simulated") is True
        or receipt.get("isSimulated") is True
        or receipt.get("dryRun") is True
        or str(receipt.get("mode") or "").strip().lower() in {"simulated", "dry-run", "dry_run", "mock"}
    ):
        return f"{check_id} receipt is marked simulated/dry-run; simulated evidence cannot qualify as PASS."

    status_code = receipt.get("statusCode") or receipt.get("httpStatus")
    if status_code is not None:
        try:
            code_int = int(status_code)
        except (TypeError, ValueError):
            code_int = 0
        if code_int in (401, 403):
            return f"{check_id} failed with HTTP {code_int} authorization error."
        if code_int < 200 or code_int >= 300:
            return f"{check_id} failed with HTTP status {status_code}."

    if receipt.get("authorizationFailed") is True or receipt.get("authError"):
        return f"{check_id} reported an authorization failure: {receipt.get('authError') or 'authorizationFailed'}."

    err_msg = receipt.get("error") or receipt.get("providerError") or receipt.get("errorMessage")
    if err_msg:
        return f"{check_id} reported provider/execution error: {err_msg}"

    if receipt.get("ok") is False:
        return f"{check_id} receipt explicitly reports ok=False."

    if isinstance(target, dict) and target:
        exp_ws_res = str(target.get("workspaceResourceId") or "").strip().rstrip("/")
        exp_ws_guid = str(target.get("workspaceCustomerId") or target.get("workspaceId") or "").strip().lower()
        exp_tenant = str(target.get("tenantId") or "").strip().lower()

        rec_ws_res = str(receipt.get("workspaceResourceId") or "").strip().rstrip("/")
        rec_ws_guid = str(receipt.get("workspaceId") or receipt.get("workspaceCustomerId") or "").strip().lower()
        rec_tenant = str(receipt.get("tenantId") or "").strip().lower()

        if exp_ws_res:
            if rec_ws_res and rec_ws_res.lower() != exp_ws_res.lower():
                return (
                    f"{check_id} receipt workspaceResourceId '{rec_ws_res}' does not match approved target "
                    f"'{exp_ws_res}'."
                )
            if require_workspace_resource_id and not rec_ws_res:
                return f"{check_id} receipt is missing workspaceResourceId for target verification."

        if exp_ws_guid:
            if rec_ws_guid and rec_ws_guid != exp_ws_guid:
                return (
                    f"{check_id} receipt workspaceId '{rec_ws_guid}' does not match approved target "
                    f"workspaceCustomerId '{exp_ws_guid}'."
                )
            if require_workspace_guid and not rec_ws_guid:
                return f"{check_id} receipt is missing workspaceId for target verification."

        if exp_tenant and rec_tenant and rec_tenant != exp_tenant:
            return f"{check_id} receipt tenantId '{rec_tenant}' does not match approved target '{exp_tenant}'."

    return None


def _extract_live_columns_map(table_entry: Dict[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], bool]:
    """Extract lowercased column name -> column dict from a live table receipt entry."""
    raw_cols = table_entry.get("columns")
    if raw_cols is None and isinstance(table_entry.get("schema"), list):
        raw_cols = table_entry.get("schema")
    if raw_cols is None and isinstance(table_entry.get("schema"), dict):
        raw_cols = table_entry["schema"].get("columns")
        if raw_cols is None:
            raw_cols = table_entry["schema"].get("customColumns")
    if raw_cols is None and isinstance(table_entry.get("properties"), dict):
        schema = table_entry["properties"].get("schema")
        if isinstance(schema, dict):
            raw_cols = schema.get("columns")
            if raw_cols is None:
                raw_cols = schema.get("customColumns")
    if raw_cols is None:
        raw_cols = table_entry.get("schemaColumns")

    if not isinstance(raw_cols, list) and not isinstance(table_entry.get("results"), list):
        return {}, False

    col_map: Dict[str, Dict[str, Any]] = {}
    if isinstance(raw_cols, list):
        for item in raw_cols:
            if isinstance(item, dict):
                c_name = str(item.get("name") or item.get("columnName") or item.get("ColumnName") or "").strip()
                if c_name:
                    col_map[c_name.lower()] = item
            elif isinstance(item, str) and item.strip():
                col_map[item.strip().lower()] = {"name": item.strip()}

    # Also extract column rows returned by `{TableName} | getschema` in `results`
    raw_results = table_entry.get("results")
    if isinstance(raw_results, list):
        for row in raw_results:
            if isinstance(row, dict):
                c_name = str(row.get("ColumnName") or row.get("columnName") or "").strip()
                if c_name and c_name.lower() not in col_map:
                    col_map[c_name.lower()] = {
                        "name": c_name,
                        "type": str(row.get("DataType") or row.get("ColumnType") or row.get("type") or ""),
                    }
    return col_map, True


def _extract_live_table_description(table_entry: Dict[str, Any]) -> str:
    """Extract table description from a live ARM or Graph table entry."""
    for key in ("tableDescription", "description", "schemaDescription"):
        val = table_entry.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    if isinstance(table_entry.get("schema"), dict):
        val = table_entry["schema"].get("description")
        if isinstance(val, str):
            return val.strip()
    if isinstance(table_entry.get("properties"), dict):
        schema = table_entry["properties"].get("schema")
        if isinstance(schema, dict) and isinstance(schema.get("description"), str):
            return schema["description"].strip()
    return ""


def _index_live_table_entries(receipt: Dict[str, Any], candidate_keys: Tuple[str, ...]) -> Dict[str, Dict[str, Any]]:
    """Index per-table live evidence entries by lowercased table name."""
    indexed: Dict[str, Dict[str, Any]] = {}
    for key in candidate_keys:
        container = receipt.get(key)
        if isinstance(container, list):
            for entry in container:
                if not isinstance(entry, dict):
                    continue
                t_name = str(
                    entry.get("tableName")
                    or entry.get("name")
                    or ((entry.get("properties") or {}).get("schema") or {}).get("name")
                    or ""
                ).strip()
                if "/" in t_name:
                    t_name = t_name.split("/")[-1].strip()
                if t_name:
                    indexed[t_name.lower()] = entry
        elif isinstance(container, dict):
            for k_name, entry in container.items():
                if isinstance(entry, dict):
                    t_name = str(entry.get("tableName") or entry.get("name") or k_name).strip()
                    if "/" in t_name:
                        t_name = t_name.split("/")[-1].strip()
                    if t_name:
                        indexed[t_name.lower()] = entry

    # Support single-table receipt dictionaries only when they carry explicit schema/column fields
    top_name = str(receipt.get("tableName") or "").strip()
    if top_name and top_name.lower() not in indexed:
        if any(k in receipt for k in ("columns", "schema", "properties", "schemaColumns", "tableDescription")):
            indexed[top_name.lower()] = receipt

    # Support direct table-name-keyed dictionaries (e.g., {"AcmeEvents_CL": {...}})
    if not indexed:
        for k_name, entry in receipt.items():
            if isinstance(entry, dict) and any(
                f in entry
                for f in (
                    "columns",
                    "schema",
                    "properties",
                    "schemaColumns",
                    "tableDescription",
                    "description",
                    "ok",
                    "httpStatus",
                    "statusCode",
                    "error",
                )
            ):
                t_name = str(entry.get("tableName") or entry.get("name") or k_name).strip()
                if "/" in t_name:
                    t_name = t_name.split("/")[-1].strip()
                if t_name:
                    indexed[t_name.lower()] = entry

    return indexed


def _unwrap_qual_receipt_and_target(
    receipt: Any,
    target: Optional[Dict[str, Any]],
    sub_keys: Tuple[str, ...],
) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """Unwrap parent qualification_evidence or tableSchemaReadiness dicts when passed directly."""
    if not isinstance(receipt, dict):
        return receipt, target
    resolved_target = target
    if resolved_target is None and isinstance(receipt.get("target"), dict):
        resolved_target = receipt.get("target")
    root = receipt.get("tableSchemaReadiness") if isinstance(receipt.get("tableSchemaReadiness"), dict) else receipt
    if resolved_target is None and isinstance(root.get("target"), dict):
        resolved_target = root.get("target")
    for key in sub_keys:
        if isinstance(root.get(key), dict):
            return root[key], resolved_target
    return root, resolved_target


def evaluate_qual_tbl_01(
    inventory: SolutionTableInventory,
    receipt: Any,
    target: Optional[Dict[str, Any]] = None,
    static_passed: bool = True,
    enforce_blocking: bool = True,
) -> Tuple[str, str]:
    """Evaluate QUAL-TBL-01: Live ARM table readback preserves table and column descriptions."""
    _ = enforce_blocking
    receipt, target = _unwrap_qual_receipt_and_target(
        receipt,
        target,
        ("armTableReadback", "armTables", "armReadbackTables"),
    )
    expected_map = build_expected_custom_table_map(inventory)
    if not expected_map and not inventory.parse_errors:
        return "NOT_APPLICABLE", "No authored custom-log tables in solution."

    prereq_err = _check_static_table_prerequisites(inventory, static_passed=static_passed)
    if prereq_err:
        return "FAIL", prereq_err

    live_tables = (
        _index_live_table_entries(
            receipt,
            ("tables", "armTables", "armReadbackTables", "tableReadbacks"),
        )
        if isinstance(receipt, dict)
        else {}
    )
    base_err = _check_receipt_integrity_and_target(
        receipt,
        "QUAL-TBL-01",
        target=target,
        require_workspace_resource_id=not bool(live_tables),
    )
    if base_err:
        return "FAIL", base_err

    if receipt.get("armDescriptionReadbackVerified") is False:
        return "FAIL", "QUAL-TBL-01 receipt explicitly reports armDescriptionReadbackVerified=False."

    if not live_tables:
        return (
            "FAIL",
            "QUAL-TBL-01 receipt is missing per-table live ARM schema readback evidence "
            "(HTTP success or summary boolean alone is insufficient).",
        )

    issues: List[str] = []
    verified_summary: List[str] = []
    exp_ws_res = str((target or {}).get("workspaceResourceId") or "").strip().rstrip("/").lower()

    for tbl_key, exp_rec in sorted(expected_map.items()):
        live_entry = live_tables.get(tbl_key)
        if live_entry is None:
            issues.append(f"Missing live ARM table readback for expected custom table '{exp_rec.table_name}'")
            continue

        entry_err = _check_receipt_integrity_and_target(
            live_entry,
            f"QUAL-TBL-01 ({exp_rec.table_name})",
            target=target,
            require_workspace_resource_id=bool(exp_ws_res and not receipt.get("workspaceResourceId")),
        )
        if entry_err:
            issues.append(entry_err)
            continue

        entry_res_id = str(live_entry.get("resourceId") or live_entry.get("id") or "").strip().lower()
        if exp_ws_res and entry_res_id and not entry_res_id.startswith(exp_ws_res + "/tables/"):
            issues.append(
                f"Table '{exp_rec.table_name}' ARM resourceId '{entry_res_id}' does not belong to target workspace '{exp_ws_res}'"
            )
            continue

        live_t_desc = _extract_live_table_description(live_entry)
        ok_t, reason_t = is_meaningful_description(live_t_desc, exp_rec.table_name)
        if not ok_t:
            issues.append(
                f"Live ARM readback for '{exp_rec.table_name}' has invalid properties.schema.description ({reason_t})"
            )
            continue
        if _normalize_whitespace(live_t_desc) != _normalize_whitespace(exp_rec.table_description):
            issues.append(
                f"Live ARM readback table description for '{exp_rec.table_name}' ({_normalize_whitespace(live_t_desc)!r}) "
                f"drifted from authored description ({_normalize_whitespace(exp_rec.table_description)!r})"
            )
            continue

        live_cols, has_cols_list = _extract_live_columns_map(live_entry)
        if not has_cols_list:
            issues.append(
                f"Live ARM readback for '{exp_rec.table_name}' is missing properties.schema.columns evidence"
            )
            continue

        exp_custom_cols = [c for c in exp_rec.columns if not c.is_system_column]
        col_issues: List[str] = []
        for exp_col in exp_custom_cols:
            live_col = live_cols.get(exp_col.name.lower())
            if live_col is None:
                col_issues.append(f"{exp_col.name} (missing_in_live_arm_schema)")
                continue
            live_c_desc = str(live_col.get("description") or "").strip()
            ok_c, reason_c = is_meaningful_description(live_c_desc, exp_col.name)
            if not ok_c:
                col_issues.append(f"{exp_col.name} ({reason_c})")
                continue
            if _normalize_whitespace(live_c_desc) != _normalize_whitespace(exp_col.description):
                col_issues.append(f"{exp_col.name} (description_drift)")

        if col_issues:
            issues.append(
                f"Live ARM readback column issues for '{exp_rec.table_name}': {', '.join(col_issues[:8])}"
            )
        else:
            verified_summary.append(f"{exp_rec.table_name} ({len(exp_custom_cols)} custom columns)")

    if issues:
        return "FAIL", f"QUAL-TBL-01 verification failed ({len(issues)} issue(s)): " + "; ".join(issues[:5])

    return (
        "PASS",
        f"Live ARM table readback verified table and custom column descriptions for {len(verified_summary)} "
        f"custom table(s): {', '.join(verified_summary[:8])}",
    )


def evaluate_qual_tbl_02(
    inventory: SolutionTableInventory,
    receipt: Any,
    target: Optional[Dict[str, Any]] = None,
    static_passed: bool = True,
    enforce_blocking: bool = True,
) -> Tuple[str, str]:
    """Evaluate QUAL-TBL-02: Graph Advanced Hunting schema exposes custom table and column descriptions."""
    _ = enforce_blocking
    receipt, target = _unwrap_qual_receipt_and_target(
        receipt,
        target,
        ("huntingSchema", "graphHuntingSchema", "huntingSchemaTables"),
    )
    expected_map = build_expected_custom_table_map(inventory)
    if not expected_map and not inventory.parse_errors:
        return "NOT_APPLICABLE", "No authored custom-log tables in solution."

    prereq_err = _check_static_table_prerequisites(inventory, static_passed=static_passed)
    if prereq_err:
        return "FAIL", prereq_err

    base_err = _check_receipt_integrity_and_target(
        receipt,
        "QUAL-TBL-02",
        target=target,
        require_workspace_guid=True,
    )
    if base_err:
        return "FAIL", base_err

    if receipt.get("graphHuntingSchemaVerified") is False:
        return "FAIL", "QUAL-TBL-02 receipt explicitly reports graphHuntingSchemaVerified=False."

    if (
        receipt.get("paginationComplete") is False
        or receipt.get("incompletePagination") is True
        or receipt.get("complete") is False
        or receipt.get("hasUnfetchedPages") is True
        or bool(receipt.get("nextLink") or receipt.get("@odata.nextLink"))
    ):
        return (
            "FAIL",
            "QUAL-TBL-02 failed (incomplete_hunting_schema_pagination): Graph getHuntingSchemaTables pagination is incomplete "
            "(@odata.nextLink was not exhausted).",
        )

    req_url = str(receipt.get("requestUrl") or receipt.get("endpoint") or "").strip()
    if req_url:
        if "workspaceId='" in req_url or 'workspaceId="' in req_url or "workspaceId=%27" in req_url:
            return (
                "FAIL",
                f"QUAL-TBL-02 invalid OData syntax in requestUrl '{req_url}': workspaceId is Edm.Guid and must not be quoted.",
            )
        exp_guid = str((target or {}).get("workspaceCustomerId") or (target or {}).get("workspaceId") or "").strip().lower()
        if exp_guid and "gethuntingschematables" in req_url.lower() and exp_guid not in req_url.lower():
            return (
                "FAIL",
                f"QUAL-TBL-02 requestUrl '{req_url}' does not target approved workspaceCustomerId '{exp_guid}'.",
            )

    live_tables = _index_live_table_entries(
        receipt,
        ("tables", "huntingSchemaTables", "value", "schemaTables"),
    )
    if not live_tables:
        return (
            "FAIL",
            "QUAL-TBL-02 receipt is missing per-table Graph Advanced Hunting schema evidence "
            "(HTTP success or summary boolean alone is insufficient).",
        )

    issues: List[str] = []
    verified_summary: List[str] = []

    for tbl_key, exp_rec in sorted(expected_map.items()):
        live_entry = live_tables.get(tbl_key)
        if live_entry is None:
            issues.append(
                f"Custom table '{exp_rec.table_name}' is absent from Graph getHuntingSchemaTables response"
            )
            continue

        entry_err = _check_receipt_integrity_and_target(live_entry, f"QUAL-TBL-02 ({exp_rec.table_name})")
        if entry_err:
            issues.append(entry_err)
            continue

        live_t_desc = _extract_live_table_description(live_entry)
        ok_t, reason_t = is_meaningful_description(live_t_desc, exp_rec.table_name)
        if not ok_t:
            issues.append(
                f"Graph hunting schema entry for '{exp_rec.table_name}' has invalid table description ({reason_t})"
            )
            continue
        if _normalize_whitespace(live_t_desc) != _normalize_whitespace(exp_rec.table_description):
            issues.append(
                f"Graph hunting schema table description for '{exp_rec.table_name}' ({_normalize_whitespace(live_t_desc)!r}) "
                f"drifted from authored description ({_normalize_whitespace(exp_rec.table_description)!r})"
            )
            continue

        live_cols, has_cols_list = _extract_live_columns_map(live_entry)
        if not has_cols_list:
            issues.append(
                f"Graph hunting schema entry for '{exp_rec.table_name}' is missing column schema evidence"
            )
            continue

        exp_custom_cols = [c for c in exp_rec.columns if not c.is_system_column]
        col_issues: List[str] = []
        for exp_col in exp_custom_cols:
            live_col = live_cols.get(exp_col.name.lower())
            if live_col is None:
                col_issues.append(f"{exp_col.name} (missing_in_hunting_schema)")
                continue
            live_c_desc = str(live_col.get("description") or "").strip()
            ok_c, reason_c = is_meaningful_description(live_c_desc, exp_col.name)
            if not ok_c:
                col_issues.append(f"{exp_col.name} ({reason_c})")
                continue
            if _normalize_whitespace(live_c_desc) != _normalize_whitespace(exp_col.description):
                col_issues.append(f"{exp_col.name} (description_drift)")

        if col_issues:
            issues.append(
                f"Graph hunting schema column issues for '{exp_rec.table_name}': {', '.join(col_issues[:8])}"
            )
        else:
            verified_summary.append(f"{exp_rec.table_name} ({len(exp_custom_cols)} custom columns)")

    if issues:
        return "FAIL", f"QUAL-TBL-02 verification failed ({len(issues)} issue(s)): " + "; ".join(issues[:5])

    return (
        "PASS",
        f"Graph Advanced Hunting schema verified table and column descriptions for {len(verified_summary)} "
        f"custom table(s): {', '.join(verified_summary[:8])}",
    )


def evaluate_qual_tbl_03(
    inventory: SolutionTableInventory,
    receipt: Any,
    target: Optional[Dict[str, Any]] = None,
    static_passed: bool = True,
    enforce_blocking: bool = True,
) -> Tuple[str, str]:
    """Evaluate QUAL-TBL-03: Graph Advanced Hunting workspace-scoped query executes against custom table."""
    _ = enforce_blocking
    receipt, target = _unwrap_qual_receipt_and_target(
        receipt,
        target,
        ("workspaceHuntingQuery", "graphRunHuntingQuery", "huntingQuery"),
    )
    expected_map = build_expected_custom_table_map(inventory)
    if not expected_map and not inventory.parse_errors:
        return "NOT_APPLICABLE", "No authored custom-log tables in solution."

    prereq_err = _check_static_table_prerequisites(inventory, static_passed=static_passed)
    if prereq_err:
        return "FAIL", prereq_err

    live_queries = (
        _index_live_table_entries(
            receipt,
            ("tableQueries", "queries", "tables", "huntingQueries"),
        )
        if isinstance(receipt, dict)
        else {}
    )
    if not live_queries and isinstance(receipt, dict):
        top_name = str(receipt.get("tableName") or "").strip()
        if top_name and any(k in receipt for k in ("schema", "columns", "schemaColumns", "results")):
            live_queries[top_name.lower()] = receipt

    base_err = _check_receipt_integrity_and_target(
        receipt,
        "QUAL-TBL-03",
        target=target,
        require_workspace_guid=not bool(live_queries),
    )
    if base_err:
        return "FAIL", base_err

    if receipt.get("workspaceScopedHuntingQueryVerified") is False:
        return "FAIL", "QUAL-TBL-03 receipt explicitly reports workspaceScopedHuntingQueryVerified=False."

    if receipt.get("fallbackUsed") is True or receipt.get("unscopedFallback") is True:
        return (
            "FAIL",
            "QUAL-TBL-03 failed: unscoped POST /security/runHuntingQuery fallback cannot qualify workspace-scoped custom tables.",
        )

    if not live_queries:
        return (
            "FAIL",
            "QUAL-TBL-03 receipt is missing per-table workspace-scoped getRunHuntingQuery schema evidence "
            "(HTTP success or summary boolean alone is insufficient).",
        )

    exp_guid = str((target or {}).get("workspaceCustomerId") or (target or {}).get("workspaceId") or "").strip().lower()
    issues: List[str] = []
    verified_summary: List[str] = []

    for tbl_key, exp_rec in sorted(expected_map.items()):
        q_entry = live_queries.get(tbl_key)
        if q_entry is None:
            issues.append(
                f"Missing workspace-scoped getRunHuntingQuery evidence for custom table '{exp_rec.table_name}'"
            )
            continue

        entry_err = _check_receipt_integrity_and_target(
            q_entry,
            f"QUAL-TBL-03 ({exp_rec.table_name})",
            target=target,
            require_workspace_guid=bool(exp_guid and not receipt.get("workspaceId")),
        )
        if entry_err:
            issues.append(entry_err)
            continue

        if q_entry.get("fallbackUsed") is True:
            issues.append(
                f"Table '{exp_rec.table_name}' query used unscoped fallback instead of getRunHuntingQuery(...,workspaceId=...)"
            )
            continue

        req_url = str(
            q_entry.get("requestUrl")
            or q_entry.get("endpoint")
            or receipt.get("requestUrl")
            or receipt.get("endpoint")
            or ""
        ).strip()
        if req_url:
            if "getrunhuntingquery" not in req_url.lower():
                issues.append(
                    f"Table '{exp_rec.table_name}' requestUrl '{req_url}' did not use getRunHuntingQuery endpoint"
                )
                continue
            if "workspaceId='" in req_url or 'workspaceId="' in req_url or "workspaceId=%27" in req_url:
                issues.append(
                    f"Table '{exp_rec.table_name}' requestUrl '{req_url}' quotes Edm.Guid workspaceId"
                )
                continue
            if exp_guid and exp_guid not in req_url.lower():
                issues.append(
                    f"Table '{exp_rec.table_name}' requestUrl '{req_url}' does not match target workspaceId '{exp_guid}'"
                )
                continue

        q_text = str(q_entry.get("query") or receipt.get("query") or "").strip()
        if not q_text or exp_rec.table_name.lower() not in q_text.lower():
            issues.append(
                f"Table '{exp_rec.table_name}' getRunHuntingQuery probe did not query '{exp_rec.table_name}' (query={q_text!r})"
            )
            continue

        live_cols, has_cols_list = _extract_live_columns_map(q_entry)
        if not has_cols_list or not live_cols:
            issues.append(
                f"Table '{exp_rec.table_name}' getRunHuntingQuery response is missing returned schema columns"
            )
            continue

        exp_custom_cols = [c for c in exp_rec.columns if not c.is_system_column]
        missing_cols = [c.name for c in exp_custom_cols if c.name.lower() not in live_cols]
        if missing_cols:
            issues.append(
                f"Table '{exp_rec.table_name}' getRunHuntingQuery schema is missing expected custom column(s): "
                + ", ".join(missing_cols[:8])
            )
        else:
            verified_summary.append(f"{exp_rec.table_name} ({len(exp_custom_cols)} custom columns)")

    if issues:
        return "FAIL", f"QUAL-TBL-03 verification failed ({len(issues)} issue(s)): " + "; ".join(issues[:5])

    return (
        "PASS",
        f"Graph getRunHuntingQuery verified workspace-scoped query and schema columns for {len(verified_summary)} "
        f"custom table(s): {', '.join(verified_summary[:8])}",
    )
