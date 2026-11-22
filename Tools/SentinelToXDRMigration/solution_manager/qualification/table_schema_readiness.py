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


@dataclass
class SolutionTableInventory:
    """Aggregated custom table schema inventory for a solution."""

    source_tables: List[TableSchemaRecord] = field(default_factory=list)
    packaged_tables: List[TableSchemaRecord] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)

    @property
    def has_any_custom_tables(self) -> bool:
        return bool(self.source_tables or self.packaged_tables or self.parse_errors)


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

    raw_desc = schema_obj.get("description")
    table_desc = ""
    if isinstance(raw_desc, str):
        resolved_desc, is_unresolved = _resolve_arm_value(raw_desc, parameters, variables)
        if is_unresolved:
            table_desc = raw_desc.strip()
            errors.append(f"Unresolved ARM expression in properties.schema.description: {raw_desc!r}")
        else:
            table_desc = (resolved_desc or "").strip()
    elif raw_desc is not None:
        errors.append("properties.schema.description must be a string.")

    raw_columns = schema_obj.get("columns")
    columns: List[ColumnSchemaRecord] = []
    if raw_columns is None:
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
            raw_c_desc = col.get("description")
            c_desc = ""
            c_unresolved = False
            if isinstance(raw_c_desc, str):
                resolved_c_desc, c_unresolved = _resolve_arm_value(raw_c_desc, parameters, variables)
                c_desc = raw_c_desc.strip() if c_unresolved else (resolved_c_desc or "").strip()
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

    return TableSchemaRecord(
        table_name=table_name,
        file_rel_path=file_rel_path,
        is_packaged=is_packaged,
        table_description=table_desc,
        columns=columns,
        unresolved_errors=errors,
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
            if rec.is_packaged:
                inventory.packaged_tables.append(rec)
            else:
                inventory.source_tables.append(rec)

    return inventory


def resolve_table_schema_blocking_mode(
    qualification_evidence: Optional[Dict[str, Any]] = None,
    workflow_state: Optional[Dict[str, Any]] = None,
    default_blocking: bool = False,
) -> bool:
    """Determine whether AI-ready table schema gaps should block (FAIL) or run in minimum-blocking adoption mode.

    Priority:
    1. Explicit ``enforceTableSchemaDescriptions`` in ``qualification_evidence``
    2. Explicit ``enforceTableSchemaDescriptions`` in ``workflow_state``
    3. Environment variable ``SM_ENFORCE_AI_TABLE_SCHEMA`` (``1``/``true`` vs ``0``/``false``)
    4. ``default_blocking`` (defaults to ``False`` for minimum-blocking adoption rollout)
    """
    for container in (qualification_evidence, workflow_state):
        if isinstance(container, dict) and "enforceTableSchemaDescriptions" in container:
            val = container.get("enforceTableSchemaDescriptions")
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.strip().lower() in ("1", "true", "yes", "strict", "block")

    env_val = os.environ.get("SM_ENFORCE_AI_TABLE_SCHEMA")
    if env_val is not None and env_val.strip() != "":
        return env_val.strip().lower() in ("1", "true", "yes", "strict", "block")

    return default_blocking


def evaluate_val_tbl_01(
    inventory: SolutionTableInventory,
    enforce_blocking: bool = False,
) -> Tuple[str, str]:
    """Evaluate VAL-TBL-01: Custom table schema description present and meaningful."""
    tables_to_check = inventory.source_tables or inventory.packaged_tables
    if not tables_to_check and not inventory.parse_errors:
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
        if enforce_blocking:
            return "FAIL", detail
        return "PASS", f"[Advisory: adoption mode] {detail}"

    return (
        "PASS",
        f"All {len(verified)} custom table definition(s) provide a meaningful properties.schema.description: "
        + ", ".join(verified[:8]),
    )


def evaluate_val_tbl_02(
    inventory: SolutionTableInventory,
    enforce_blocking: bool = False,
) -> Tuple[str, str]:
    """Evaluate VAL-TBL-02: 100% custom table column description coverage."""
    tables_to_check = inventory.source_tables or inventory.packaged_tables
    if not tables_to_check and not inventory.parse_errors:
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
        if enforce_blocking:
            return "FAIL", detail
        return "PASS", f"[Advisory: adoption mode] {detail}"

    return (
        "PASS",
        f"100% custom column description coverage verified ({documented_custom_cols}/{total_custom_cols} "
        f"custom columns across {len(tables_to_check)} table definition(s); system columns exempted).",
    )


def evaluate_val_tbl_03(
    inventory: SolutionTableInventory,
    enforce_blocking: bool = False,
) -> Tuple[str, str]:
    """Evaluate VAL-TBL-03: Packaged mainTemplate preserves custom table and column descriptions."""
    if not inventory.source_tables and not inventory.packaged_tables and not inventory.parse_errors:
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
        merged_src_cols: Dict[str, TableColumnRecord] = {
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

        pkg_rec = pkg_by_name.get(tbl_lower)
        if pkg_rec is None:
            if inventory.packaged_tables:
                issues.append(
                    f"Custom table '{canonical_src.table_name}' ({canonical_src.file_rel_path}) is missing from Package/mainTemplate.json"
                )
            continue

        src_t_desc = _normalize_whitespace(canonical_src.table_description)
        pkg_t_desc = _normalize_whitespace(pkg_rec.table_description)
        if src_t_desc != pkg_t_desc:
            issues.append(
                f"Table '{canonical_src.table_name}' schema.description drift between {canonical_src.file_rel_path} "
                f"({src_t_desc!r}) and {pkg_rec.file_rel_path} ({pkg_t_desc!r})"
            )

        pkg_cols_by_name = {c.name.lower(): c for c in pkg_rec.columns}
        for src_col in merged_src_cols.values():
            pkg_col = pkg_cols_by_name.get(src_col.name.lower())
            if pkg_col is None:
                issues.append(
                    f"Table '{canonical_src.table_name}' column '{src_col.name}' missing from packaged {pkg_rec.file_rel_path}"
                )
                continue
            s_c_desc = _normalize_whitespace(src_col.description)
            p_c_desc = _normalize_whitespace(pkg_col.description)
            if s_c_desc != p_c_desc:
                issues.append(
                    f"Table '{canonical_src.table_name}' column '{src_col.name}' description drift between "
                    f"source ({s_c_desc!r}) and package ({p_c_desc!r})"
                )

        matched_tables.append(canonical_src.table_name)

    # If only packaged tables exist (no separate source table JSON), verify packaged table descriptions are non-empty
    if not inventory.source_tables and inventory.packaged_tables:
        for pkg_rec in inventory.packaged_tables:
            ok_t, reason_t = is_meaningful_description(pkg_rec.table_description, pkg_rec.table_name)
            if not ok_t:
                issues.append(
                    f"Packaged table '{pkg_rec.table_name}' ({pkg_rec.file_rel_path}) missing meaningful table description ({reason_t})"
                )
            missing_pkg_cols = [
                c.name
                for c in pkg_rec.columns
                if not c.is_system_column and not is_meaningful_description(c.description, c.name)[0]
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
        if enforce_blocking:
            return "FAIL", detail
        return "PASS", f"[Advisory: adoption mode] {detail}"

    return (
        "PASS",
        f"Packaged mainTemplate preserves table and column descriptions for {len(matched_tables)} custom table(s): "
        + ", ".join(matched_tables[:8]),
    )
