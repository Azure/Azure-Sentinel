"""Offline, loss-aware Notebook/1.0 adapter around the shared KQL migrator."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Iterator

from . import migrator, rewrite

AH = "advancedHunting"
LA = "microsoft.operationalinsights/workspaces"
ARG_RESOURCE_TYPE = "microsoft.resourcegraph/resources"
SCOPE_KEYS = {
    "crossComponentResources", "fallbackResourceIds", "resourceIds",
    "workspaceId", "workspaceResourceId", "selectedWorkspaceIds",
}
PARAMETER_KEYS = {
    "parameterName", "exportParameterName", "timeContextFromParameter",
    "resourceContextFromParameter",
}
TOKEN = re.compile(r"\{([A-Za-z_][\w .-]*)(?::[^{}]*)?\}")


def walk(value, path="") -> Iterator[tuple[str, dict]]:
    """Yield dictionaries with RFC 6901 JSON pointers, including nested groups."""
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            escaped = key.replace("~", "~0").replace("/", "~1")
            yield from walk(child, f"{path}/{escaped}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, f"{path}/{i}")


def query_hash(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()


def references(value, *, skip_scope=False) -> set[str]:
    found = set()
    if isinstance(value, str):
        found.update(TOKEN.findall(value))
    elif isinstance(value, list):
        for child in value:
            found.update(references(child, skip_scope=skip_scope))
    elif isinstance(value, dict):
        for key, child in value.items():
            if skip_scope and (key in SCOPE_KEYS or key == "resourceContextFromParameter"):
                continue
            if key in PARAMETER_KEYS and isinstance(child, str):
                found.add(child)
            if key == "linkTarget" and child == "parameter":
                found.add(value.get("cellValue", ""))
            found.update(references(child, skip_scope=skip_scope))
    return found


def query_surfaces(doc: dict) -> list[dict]:
    """Inventory every nonempty query, honoring inherited provider settings."""
    result = []

    def visit(value, path="", inherited=None, parameter=False):
        if isinstance(value, dict):
            settings = dict(inherited or {})
            settings.update({k: value[k] for k in ("queryType", "resourceType") if k in value})
            if "query" in value and value["query"] not in ("", None):
                result.append({
                    "path": path + "/query", "node": value,
                    "queryType": settings.get("queryType", 0),
                    "resourceType": settings.get("resourceType"),
                    "parameter": parameter,
                })
            for key, child in value.items():
                escaped = key.replace("~", "~0").replace("/", "~1")
                visit(child, f"{path}/{escaped}", settings,
                      parameter or key == "parameters")
        elif isinstance(value, list):
            for i, child in enumerate(value):
                visit(child, f"{path}/{i}", inherited, parameter)

    visit(doc)
    return result


def is_preserved_provider_surface(surface: dict | None) -> bool:
    """Return True when a query surface uses a preserved non-Log-Analytics provider."""
    if not isinstance(surface, dict):
        return False
    qt = surface.get("queryType")
    rt = (surface.get("resourceType") or "").strip().lower()
    node = surface.get("node")
    raw = node.get("query") if isinstance(node, dict) else (surface.get("sourceKql") or surface.get("queryKql"))
    return (
        qt == 1
        and rt == ARG_RESOURCE_TYPE
        and isinstance(raw, str)
        and LA not in raw.lower()
    )


def _scope_parameters(doc, protected=()):
    entries = [(path, node) for path, node in walk(doc)
               if re.search(r"/parameters/\d+$", path) and node.get("name")]
    names = {node["name"] for _, node in entries}
    if len(names) != len(entries):
        raise ValueError("Duplicate parameter names: scope dependencies are ambiguous.")
    params = {node["name"]: node for _, node in entries}
    nodes = dict(walk(doc))
    inherited_resources = {}
    for path, p in entries:
        ancestor = path
        while True:
            if nodes.get(ancestor, {}).get("resourceType"):
                inherited_resources[p["name"]] = nodes[ancestor]["resourceType"].lower()
                break
            if not ancestor:
                break
            ancestor = ancestor.rsplit("/", 1)[0]
    surfaces = {id(s["node"]): s for s in query_surfaces(doc)}
    bindings = set()
    for _, node in walk(doc):
        for key in SCOPE_KEYS | {"resourceContextFromParameter"}:
            if key in node:
                bindings |= references({key: node[key]})
    dependencies = {
        name: references(p, skip_scope=surfaces.get(id(p), {}).get("queryType", 0)
                         in (0, None, AH)) & names
        for name, p in params.items()
    }
    all_dependencies = {name: references(p) & names for name, p in params.items()}

    def eligible(name):
        p = params[name]
        # A type-5 parameter may be a KQL-backed Computer filter or preserved ARG resource picker, not a workspace.
        surface = surfaces.get(id(p))
        qt = surface.get("queryType") if surface else None
        return (
            not (p.get("query") and qt in (0, None, AH))
            and not (p.get("type") == 5 and is_preserved_provider_surface(surface))
            and p.get("type") != 4
        )

    candidates = {
        name for name, p in params.items()
        if eligible(name) and (
            p.get("type") == 6
            or (p.get("type") == 5 and (
                name in bindings or inherited_resources.get(name) == LA))
            or LA in json.dumps(p.get("typeSettings", {})).lower()
            or (p.get("queryType") == 1 and LA in p.get("query", "").lower())
        )
    }
    # Include both upstream scope helpers and hidden derived helpers (ContextFree).
    while True:
        expanded = candidates | {
            dep for name in candidates for dep in all_dependencies[name] if eligible(dep)
        } | {
            name for name, p in params.items()
            if eligible(name) and p.get("isHiddenWhenLocked")
            and all_dependencies[name] & candidates
        }
        if expanded == candidates:
            break
        candidates = expanded

    outside = copy.deepcopy(doc)
    for _, node in walk(outside):
        if isinstance(node.get("parameters"), list):
            node["parameters"] = []
    live = ((names - candidates) | (references(outside, skip_scope=True) & names)
            | (set(protected) & names))
    while True:
        expanded = live | {
            dep for name in live
            for dep in (all_dependencies[name] if name in candidates else dependencies[name])
        }
        if expanded == live:
            break
        live = expanded
    removed = candidates - live
    return entries, removed, candidates & live


def _raw_query(query, query_type):
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    if query_type == AH and query.lstrip().startswith("{"):
        try:
            settings = json.loads(query)
        except ValueError as exc:
            raise ValueError("Malformed Advanced Hunting settings wrapper") from exc
        if not isinstance(settings, dict) or settings.get("__advancedHuntingSettings") is not True:
            raise ValueError("Unrecognized Advanced Hunting query wrapper")
        if set(settings) - {"__advancedHuntingSettings", "query", "selectedWorkspaceIds"}:
            raise ValueError("Unknown Advanced Hunting wrapper settings; review before removing")
        if not isinstance(settings.get("query"), str):
            raise ValueError("Advanced Hunting wrapper has no string query")
        return settings["query"]
    return query


_BUILTINS = {
    "datatable", "range", "print", "externaldata", "external_data", "dynamic", "datetime", "timespan",
    "toscalar", "tostring", "toint", "tolong", "todouble", "todatetime", "todecimal", "todynamic", "toreal", "totable",
    "totimespan", "tobool", "now", "ago", "startofday", "endofday", "startofweek", "endofweek",
    "startofmonth", "endofmonth", "startofyear", "endofyear", "tolower", "toupper", "coalesce", "iff", "iif", "case",
    "_GetWatchlist", "workspace", "app", "resource", "cluster", "database", "table", "view", "materialize",
    "abs", "acos", "asin", "atan", "atan2", "beta_cdf", "beta_inv", "beta_pdf", "bin", "bin_at", " ceiling", "ceiling",
    "cos", "cot", " count", "count", "count_distinct", "count_distinctif", "countif", "countof",
    " dcount", "dcount", "dcount_hll", "dcountif", "degrees", "exp", "exp10", "exp2", "floor", "gamma",
    "hash", "hash_combine", "hash_many", "hash_md5", "hash_sha1", "hash_sha256", "hash_xxhash64",
    "isnan", "isfinite", "isinf", "isascii", "isempty", "isnotempty", "isnull", "isnotnull", "isutf8",
    "log", "log10", "log2", "loggamma", "max", "max_of", "maxif", "min", "min_of", "minif", "mod",
    "not", "and", "or", "between", "in", "has", "has_all", "has_any", "has_cs", "contains", "contains_cs",
    "startswith", "startswith_cs", "endswith", "endswith_cs", "matches", "regex",
    "avg", "avgif", "sum", "sumif", "stdev", "stdevif", "stdevp", "variance", "varianceif", "variancep",
    "percentile", "percentiles", "percentilew", "percentilesw", "arg_max", "arg_min", "any", "anyif", "take_any", "take_anyif",
    "make_list", "make_list_if", "make_list_with_nulls", "makelist", "make_set", "make_set_if", "makeset",
    "make_bag", "make_bag_if", "pack", "pack_all", "pack_array", "pack_dictionary", "bag_keys", "bag_pack",
    "bag_pack_columns", "bag_merge", "bag_remove_keys", "bag_set_key", "bag_has_key", "bag_unpack",
    "unpack_object", "treepath", "zip", "repeat",
    "array_concat", "array_iif", "array_index_of", "array_iff", "array_length", "array_reverse",
    "array_rotate_left", "array_rotate_right", "array_shift_left", "array_shift_right", "array_slice",
    "array_sort_asc", "array_sort_desc", "array_split", "array_strcat", "array_sum",
    "set_difference", "set_has_element", "set_intersect", "set_union",
    "strcat", "strcat_array", "strcat_delim", "strcmp", "string_size", "strlen", "strrep", "substring",
    "split", "trim", "trim_end", "trim_start", "replace", "replace_regex", "replace_string", "replace_strings",
    "reverse", "translate", "url_decode", "url_encode", "url_encode_component",
    "base64_decode_toarray", "base64_decode_toguid", "base64_decode_tostring", "base64_encode_fromguid", "base64_encode_tostring",
    " zlib_compress_to_base64_string", "zlib_decompress_from_base64_string", "gzip_compress_to_base64_string", "gzip_decompress_from_base64_string",
    "extract", "extract_all", "extractall", "extract_json", "extractjson",
    "parse_command_line", "parse_csv", "parse_ipv4", "parse_ipv4_mask", "parse_ipv6", "parse_ipv6_mask",
    "parse_json", "parsejson", "parse_path", "parse_url", "parse_urlquery", "parse_user_agent", "parse_version", "parse_xml",
    "dynamic_to_json", "format_bytes", "format_datetime", "format_ipv4", "format_ipv4_mask", "format_timespan",
    "datetime_add", "datetime_diff", "datetime_local_to_utc", "datetime_part", "datetime_utc_to_local",
    "dayofmonth", "dayofweek", "dayofyear", "getmonth", "getyear", "hourofday", "monthofyear", "weekofyear", " week_of_year",
    "make_datetime", "make_timespan", "unixtime_microseconds_todatetime", "unixtime_milliseconds_todatetime",
    "unixtime_nanoseconds_todatetime", "unixtime_seconds_todatetime", "ingestion_time", "cursor_after", "cursor_before_or_at", "current_cursor",
    "ipv4_compare", "ipv4_is_in_any_range", "ipv4_is_in_range", "ipv4_is_match", "ipv4_is_private", "ipv4_lookup",
    "ipv4_netmask_suffix", "ipv6_compare", "ipv6_is_in_any_range", "ipv6_is_in_range", "ipv6_is_match",
    "geo_distance_2points", "geo_info_from_ip_address", "geo_point_in_circle", "geo_point_in_polygon", "geo_point_to_geohash", "geo_point_to_s2cell", "geo_point_to_h3cell",
    "indexof", "indexof_regex", "next", "prev", "row_cumsum", "row_number", "row_rank_dense", "row_rank_min", "row_window_session",
    "pi", "pow", "radians", "rand", "round", "sign", "sin", "sqrt", "tan",
    "series_abs", "series_acos", "series_add", "series_asin", "series_atan", "series_ ceiling", "series_cos",
    "series_decompose", "series_decompose_anomalies", "series_decompose_forecast", "series_divide", "series_equals",
    "series_exp", "series_fill_backward", "series_fill_const", "series_fill_forward", "series_fill_linear",
    "series_fir", "series_fit_2lines", "series_fit_2lines_dynamic", "series_fit_line", "series_fit_line_dynamic",
    "series_fit_poly", "series_greater", "series_greater_equals", "series_iir", "series_less", "series_less_equals",
    "series_multiply", "series_not_equals", "series_outliers", "series_pearson_correlation", "series_periods_detect",
    "series_periods_validate", "series_pow", "series_ seasonal", "series_sign", "series_sin", "series_stats",
    "series_stats_dynamic", "series_subtract", "series_tan",
    "column_ifexists", "columnifexists", "gettype", "typeof", "bool", "int", "long", "real", "double", "decimal", "string", "guid", " new_guid",
    "autocluster", "basket", "diffpatterns", "narrow", "pivot", "rolling_percentile", "sql_request", "cosmosdb_sql_request",
    "true", "false", "null", "by", "from", "to", "on", "with", "as", "asc", "desc", "step", "default", "kind", "in",
}
_STATEMENT_PREFIXES = {
    "let", "set", "alias", "declare", "restrict", "evaluate", "access", "pattern",
    "find", "search", "fork", "facet", "consume", "where", "project", "project-away",
    "project-keep", "project-rename", "project-reorder", "extend", "summarize",
    "order", "sort", "top", "take", "limit", "distinct", "count", "render",
    "mv-expand", "mvexpand", "mv-apply", "mvapply", "parse", "parse-where", "parse-kv",
    "make-series", "lookup", "join", "union", "invoke", "as", "partition", "serialize",
    "sample", "sample-distinct", "scan", "reduce", "top-nested", "top-hitters", "getschema",
}


_QUOTED_LITERAL_RE = re.compile(
    r"//[^\r\n]*|@\"(?:\"\"|[^\"])*\"|@'(?:''|[^'])*'|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'"
)
_BRACKETED_QUOTED_NAME_RE = re.compile(
    r"\[\s*(@\"(?:\"\"|[^\"])*\"|@'(?:''|[^'])*'|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')\s*\]",
    re.DOTALL,
)
_TABLE_LITERAL_CALL_RE = re.compile(
    r"(?<![.\w])(?:table|totable)\s*\(\s*(@\"(?:\"\"|[^\"])*\"|@'(?:''|[^'])*'|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')\s*(?:,[^;\r\n)]*)?\)",
    re.IGNORECASE,
)
_TABLE_ANY_CALL_RE = re.compile(
    r"(?<![.\w])(?:table|totable)\s*\(",
    re.IGNORECASE,
)


def _unquote_kql_string(literal: str) -> str:
    if literal.startswith('@"') and literal.endswith('"'):
        return literal[2:-1].replace('""', '"')
    if literal.startswith("@'") and literal.endswith("'"):
        return literal[2:-1].replace("''", "'")
    if len(literal) >= 2 and literal[0] == literal[-1] and literal[0] in ('"', "'"):
        inner = literal[1:-1]
        return re.sub(r"\\(.)", r"\1", inner)
    return literal


def _is_union_withsource_output_binding(code: str, start: int) -> bool:
    prefix = _QUOTED_LITERAL_RE.sub(lambda m: " " * len(m.group(0)), code[:start])
    segment_start = max(prefix.rfind("|"), prefix.rfind(";"))
    return re.search(
        r"\bunion\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*"
        r"\s+withsource\s*=\s*$",
        prefix[segment_start + 1:],
        re.IGNORECASE,
    ) is not None


def _union_operands(code):
    # Union operands are separated at the union's own depth, not by commas
    # inside function arguments. Include later operands, not only the first.
    for union in re.finditer(r"\bunion\b", code):
        start = union.end()
        flags = re.match(r"(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*", code[start:])
        start += flags.end()
        depth, operand = 0, True
        for index in range(start, len(code)):
            char = code[index]
            if operand and not char.isspace():
                source = re.match(r"(?:\(\s*)*([A-Za-z_]\w*)\s*(\()?", code[index:])
                if source:
                    yield source.group(1), bool(source.group(2))
                operand = False
            if depth == 0 and char in "|;":
                break
            if char in "([{":
                depth += 1
            elif char in ")]}":
                if depth == 0:
                    break
                depth -= 1
            elif char == "," and depth == 0:
                operand = True


def _stripped_code(query: str, *, preserve_tokens: bool = False) -> str:
    masked = _QUOTED_LITERAL_RE.sub(lambda m: " " * len(m.group(0)), query)
    if preserve_tokens:
        return masked
    return re.sub(
        r"\{[A-Za-z0-9_.:$ -]+\}",
        lambda m: (
            m.group(0)
            if re.search(
                r"(?:\)|(?<![.\w])\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*)\s*$",
                masked[:m.start()],
                re.IGNORECASE,
            )
            else (" " * len(m.group(0)) if re.search(r"[A-Za-z0-9_]", m.group(0)) else m.group(0))
        ),
        masked,
    )


def _quoted_calls_and_table_sources(query: str) -> tuple[set[str], set[str]]:
    calls: set[str] = set()
    bare: set[str] = set()
    # Mask single-line // comments only first, then inspect quoted constructs at top level.
    no_comments = re.sub(r"//[^\r\n]*", lambda m: " " * len(m.group(0)), query)
    protectedspans: list[tuple[int, int]] = []
    for m in _BRACKETED_QUOTED_NAME_RE.finditer(no_comments):
        protectedspans.append(m.span())
    for m in _TABLE_LITERAL_CALL_RE.finditer(no_comments):
        protectedspans.append(m.span())

    # Check that each protected span does not start inside an outer string literal
    valid_spans: set[tuple[int, int]] = set()
    outer_string_spans: list[tuple[int, int]] = []
    idx = 0
    n = len(no_comments)
    while idx < n:
        for s, e in protectedspans:
            if s == idx:
                valid_spans.add((s, e))
                idx = e
                break
        else:
            m_str = _QUOTED_LITERAL_RE.match(no_comments, idx)
            if m_str:
                outer_string_spans.append(m_str.span())
                idx = m_str.end()
                continue
            idx += 1

    for m in _TABLE_LITERAL_CALL_RE.finditer(no_comments):
        if m.span() in valid_spans:
            name = _unquote_kql_string(m.group(1)).strip()
            if name:
                bare.add(name)

    # Fail closed on non-literal or unsupported table()/totable() indirection
    for m in _TABLE_ANY_CALL_RE.finditer(no_comments):
        if any(s <= m.start() < e for s, e in outer_string_spans):
            continue
        if _is_union_withsource_output_binding(no_comments, m.start()):
            continue
        if not any(s == m.start() for s, _ in valid_spans):
            calls.add("{__unsupported_table_indirection__}")

    for m in _BRACKETED_QUOTED_NAME_RE.finditer(no_comments):
        if m.span() not in valid_spans:
            continue
        name = _unquote_kql_string(m.group(1)).strip()
        if not name:
            continue
        before = no_comments[:m.start()]
        after = no_comments[m.end():]
        # Skip externaldata(...) [...]
        if re.search(r"\bexternal_?data\s*\([^;|\r\n]*$", before, re.IGNORECASE):
            continue
        if re.match(r"^\s*\(", after):
            calls.add(name)
            if re.search(r"(?:[)\]}]|\.[A-Za-z_]\w*)\s*$", before):
                calls.add("{__unsupported_escaped_call_context__}")
        elif not re.search(r"(?:[)\]}]|\.[A-Za-z_]\w*)\s*$", before) and (
            (re.search(r"(?:^|[;{]|/\*|\*/|\bmaterialize\s*\(|\btoscalar\s*\(|\b(?:join|lookup|union)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*)(?:\s*\()*\s*$", before, re.IGNORECASE) and re.match(r"^(?:\s*\))*\s*(?:\*/\s*)?\|", after))
            or (re.search(r"(\(\s*(?:\(\s*)*)$", before) and re.match(r"^((?:\s*\))*)\s*(?:\*/\s*)?\|", after) and re.search(r"(\(\s*(?:\(\s*)*)$", before).group(1).count("(") > re.match(r"^((?:\s*\))*)\s*(?:\*/\s*)?\|", after).group(1).count(")"))
            or re.search(r"\binvoke\s*$", before)
            or (re.search(r"\blet\s+[A-Za-z_]\w*\s*=(?:\s*\()*\s*$", before) and re.match(r"^(?:\s*\))*\s*[;|]", after))
            or (re.search(r"\blet\s+[A-Za-z_]\w*\s*=\s*(?:view\s*)?\([^)]*\)\s*\{(?:\s*\()*\s*$", before) and re.match(r"^(?:\s*\))*\s*[;|}]", after))
            or (re.search(r"\bview\s*\([^)]*\)\s*\{(?:\s*\()*\s*$", before) and re.match(r"^(?:\s*\))*\s*[;|}]", after))
            or (re.search(r"\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*\s*\{(?:\s*\()*\s*$", before, re.IGNORECASE) and re.match(r"^(?:\s*\))*\s*[;|}]", after))
            or (re.search(r"\bfork\b(?:\s+[A-Za-z_]\w*\s*=)?\s*\((?:\s*\()*\s*$", before, re.IGNORECASE) and re.match(r"^(?:\s*\))*\s*[|)]", after))
            or (re.search(r"\b(?:toscalar|materialize)\s*\((?:\s*\()*\s*$", before, re.IGNORECASE) and re.match(r"^(?:\s*\))*\s*[|)]", after))
            or (re.search(r"\b(?:join|lookup|union)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*(?:\s*\()*\s*$", before) and not re.match(r"^\s*=", after))
            or re.search(r"\bunion\b[^;|]*,\s*(?:\(\s*)*$", before)
            or re.search(r"\b(?:find|search)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*\s+in\s*\([^)]*$", before, re.IGNORECASE)
        ):
            bare.add(name)
    return calls, bare


def _local_tabular_vars(code: str) -> set[str]:
    return (
        set(re.findall(r"\blet\s+([A-Za-z_]\w*)\s*=", code))
        | set(re.findall(r"\|\s*as\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+([A-Za-z_]\w*)", code, re.IGNORECASE))
    )


def union_source_names(query: str) -> set[str]:
    """Heuristic operands, not proof of a table or saved-function dependency."""
    code = _stripped_code(query)
    locals = _local_tabular_vars(code)
    return {name for name, _ in _union_operands(code)} - locals


_STANDARD_BUILTIN_ASIM_PARSER_RE = re.compile(
    r"^_(?:asim|im)_(?!test$)[a-z0-9_]+$",
    re.IGNORECASE,
)


def is_standard_builtin_asim_parser(name: str) -> bool:
    """Return True for standard built-in ASIM parsers (_ASim_* and _Im_*)."""
    return bool(isinstance(name, str) and _STANDARD_BUILTIN_ASIM_PARSER_RE.match(name.strip()))


def _bare_source_identifiers(code: str) -> set[str]:
    code_no_flags = re.sub(
        r"\b(?:union|join|lookup)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)+",
        lambda m: re.sub(r"\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+", " ", m.group(0)),
        code,
    )
    bare_matches = re.findall(
        r"(?:^|[;{]|/\*|\*/|\bmaterialize\s*\(|\btoscalar\s*\(|\b(?:join|lookup|union)\b)(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?:\*/\s*)?(?=\|)"
        r"|\(\s*([A-Za-z_]\w*)\s*(?:\*/\s*)?(?=\|)"
        r"|\blet\s+[A-Za-z_]\w*\s*=(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[;|])"
        r"|\blet\s+[A-Za-z_]\w*\s*=\s*(?:view\s*)?\([^)]*\)\s*\{(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[;|}])"
        r"|\bview\s*\([^)]*\)\s*\{(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[;|}])"
        r"|\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*\s*\{(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[;|}])"
        r"|\b(?:toscalar|materialize)\s*\((?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[|)])",
        code_no_flags,
        flags=re.IGNORECASE,
    )
    bare = {name for groups in bare_matches for name in groups if name}
    for m in re.finditer(r"(\(\s*(?:\(\s*)*)([A-Za-z_]\w*)((?:\s*\))*)\s*(?:\*/\s*)?(?=\|)", code_no_flags):
        if m.group(1).count("(") > m.group(3).count(")"):
            bare.add(m.group(2))
    for m in re.finditer(r"\bfork\b([^;|]*)", code_no_flags, re.IGNORECASE):
        for bm in re.finditer(r"(?:[A-Za-z_]\w*\s*=\s*)?\((?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[|)])", m.group(1)):
            bare.add(bm.group(1))
    for op in re.finditer(r"\b(?:join|lookup)\b", code):
        pos = op.end()
        flags = re.match(r"(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*", code[pos:])
        pos += flags.end()
        target = re.match(r"(?:\s*\()*\s*([A-Za-z_]\w*)\b(?!\s*[\(=.])", code[pos:])
        if target:
            bare.add(target.group(1))
    for op in re.finditer(r"\b(?:find|search)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*\s+in\s*\(([^)]*)\)", code, re.IGNORECASE):
        for ident in re.findall(r"(?<![.\w])([A-Za-z_]\w*)\b(?!\s*\()", op.group(1)):
            bare.add(ident)
    bare.update(name for name, is_call in _union_operands(code) if not is_call)
    local_vars = _local_tabular_vars(code)
    return {
        name for name in (bare - _BUILTINS - _STATEMENT_PREFIXES - local_vars)
        if not is_standard_builtin_asim_parser(name)
    }


def _parameter_source_or_call_tokens(query: str) -> set[str]:
    code = _stripped_code(query, preserve_tokens=True)
    # Mask KQL function/view/partition brace bodies `{ ... }` so they are not misread as `{Param}` tokens.
    code = re.sub(
        r"((?:\)|(?<![.\w])\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*)\s*)\{([A-Za-z0-9_.:$ -]+)\}",
        lambda m: f"{m.group(1)}{{(){m.group(2)}}}",
        code,
        flags=re.IGNORECASE,
    )
    tok_pat = r"\{[A-Za-z0-9_.:$ -]+\}"
    tokens: set[str] = set()
    for match in re.finditer(rf"({tok_pat})\s*\(", code):
        tokens.add(match.group(1))
    for match in re.finditer(
        rf"(?:^|[;{{]|/\*|\*/|\bmaterialize\s*\(|\btoscalar\s*\(|\b(?:join|lookup|union)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*)(?:\s*\()*\s*({tok_pat})(?:\s*\))*\s*(?:\*/\s*)?(?=\|)"
        rf"|\(\s*({tok_pat})\s*(?:\*/\s*)?(?=\|)"
        rf"|\binvoke\s+({tok_pat})"
        rf"|\blet\s+[A-Za-z_]\w*\s*=(?:\s*\()*\s*({tok_pat})(?:\s*\))*\s*(?=[;|(])"
        rf"|\blet\s+[A-Za-z_]\w*\s*=\s*(?:view\s*)?\([^)]*\)\s*\{{(?:\s*\()*\s*({tok_pat})(?:\s*\))*\s*(?=[;|(\}}])"
        rf"|\bview\s*\([^)]*\)\s*\{{(?:\s*\()*\s*({tok_pat})(?:\s*\))*\s*(?=[;|(\}}])"
        rf"|\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*\s*\{{(?:\s*\()*\s*({tok_pat})(?:\s*\))*\s*(?=[;|(\}}])"
        rf"|\bfork\b(?:\s+[A-Za-z_]\w*\s*=)?\s*\((?:\s*\()*\s*({tok_pat})(?:\s*\))*\s*(?=[|)\(])"
        rf"|\b(?:toscalar|materialize|table|totable)\s*\((?:\s*\()*\s*({tok_pat})(?:\s*\))*\s*(?=[|)\(,])",
        code,
        flags=re.IGNORECASE,
    ):
        captured = [g for g in match.groups() if g]
        scalar_granularity = False
        let_match = re.match(
            rf"\blet\s+gran\s*=\s*({tok_pat})\s*;",
            code[match.start():],
            flags=re.IGNORECASE,
        )
        if let_match and let_match.group(1) in captured:
            token = let_match.group(1)
            scalar_granularity = (
                token.casefold() == "{granularity}"
                and bool(re.search(
                    r"\bmake-series\b.*?\bstep\s+gran\b|\bbin\s*\([^)]*,\s*gran\s*\)",
                    code, flags=re.IGNORECASE | re.DOTALL,
                ))
            )
        if not scalar_granularity:
            tokens.update(captured)
    for m in re.finditer(rf"(\(\s*(?:\(\s*)*)({tok_pat})((?:\s*\))*)\s*(?:\*/\s*)?(?=\|)", code):
        if m.group(1).count("(") > m.group(3).count(")"):
            tokens.add(m.group(2))
    for op in re.finditer(r"\b(?:union|join|lookup)\b", code):
        pos = op.end()
        flags = re.match(r"(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*", code[pos:])
        pos += flags.end()
        target = re.match(rf"(?:\s*\()*\s*({tok_pat})", code[pos:])
        if target:
            tokens.add(target.group(1))
    for op in re.finditer(r"\b(?:find|search)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*\s+in\s*\(([^)]*)\)", code, re.IGNORECASE):
        for tok in re.findall(tok_pat, op.group(1)):
            tokens.add(tok)
    return {tok for tok in tokens if re.search(r"[A-Za-z0-9_]", tok)}


def opaque_functions(query: str, *, include_bare: bool = True) -> set[str]:
    """Conservative callable and bare saved-function scanner across all expressions."""
    code = _stripped_code(query)
    quoted_calls, quoted_bare = _quoted_calls_and_table_sources(query)
    code_no_flags = re.sub(
        r"\b(?:union|join|lookup)\b(?:\s+([A-Za-z_][\w.]*)\s*=\s*([\w.*-]+))+",
        lambda m: re.sub(r"\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+", " ", m.group(0)),
        code,
    )
    code_no_flags = re.sub(
        r"\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*\s*(?=[({])",
        "partition ",
        code_no_flags,
        flags=re.IGNORECASE,
    )
    calls = set(re.findall(r"(?<![.\w])([A-Za-z_]\w*)\s*\(", code_no_flags))
    calls.update(re.findall(r"\binvoke\s+([A-Za-z_]\w*)", code_no_flags))
    calls.update(name for name, is_call in _union_operands(code) if is_call)
    calls.update(quoted_calls)
    local_funcs = set(re.findall(r"\blet\s+([A-Za-z_]\w*)\s*=\s*(?:view\s*)?\(", code))
    local_vars = _local_tabular_vars(code)
    result = calls - _BUILTINS - _STATEMENT_PREFIXES - local_funcs - local_vars
    result |= _parameter_source_or_call_tokens(query)
    if include_bare:
        bare = _bare_source_identifiers(code) | (quoted_bare - _BUILTINS - _STATEMENT_PREFIXES - local_vars)
        known_tables = set(migrator.mapping_catalog.load_mapping_catalog()["tables"])
        custom_tables = {name for name in bare if isinstance(name, str) and name.endswith("_CL")}
        result |= (bare - known_tables - custom_tables - local_vars)
    return {name for name in result if not is_standard_builtin_asim_parser(name)}


def convert_workbook(source: dict, resolutions: dict | None = None,
                     tables: list[str] | None = None,
                     allowed_workspace_functions=(),
                     *,
                     preserve_sentinel_tables: bool = False) -> dict:
    """Return an intact review draft and report. Never resolves or executes live.

    resolutions maps original query pointers to {querySha256, tables, evidence}.
    tables is an explicit caller-reviewed fallback, NOT a discovered table list.
    """
    if source.get("version") != "Notebook/1.0" or not isinstance(source.get("items"), list):
        raise ValueError("Expected a Notebook/1.0 document with an items array.")
    doc = copy.deepcopy(source)
    originals = query_surfaces(source)
    surfaces = query_surfaces(doc)
    entries, removed, retained_scope = _scope_parameters(doc)
    removed_prefixes = [path + "/" for path, p in entries if p["name"] in removed]
    issues, reports, gates = [], [], set()
    provenance_notes: list[str] = []

    def issue(path, code, message):
        issues.append({"path": path, "code": code, "message": message})

    converted_nodes = set()
    preserved_nodes = set()
    for surface, original in zip(surfaces, originals):
        path, node, qt = surface["path"], surface["node"], surface["queryType"]
        if any(path.startswith(prefix) for prefix in removed_prefixes):
            reports.append({"sourcePath": path, "status": "removed-scope-helper"})
            continue
        entry = {"sourcePath": path, "parameter": surface["parameter"]}
        reports.append(entry)
        if is_preserved_provider_surface(surface):
            evidence = (resolutions or {}).get(path)
            resolution_note = f"preserved non-Log-Analytics query type ({surface['resourceType']})"
            if evidence is not None:
                if (not isinstance(evidence, dict)
                        or evidence.get("querySha256") != query_hash(original["node"]["query"])
                        or not isinstance(evidence.get("tables"), list)
                        or evidence.get("tables") != []
                        or not evidence.get("evidence")):
                    entry["status"] = "blocked"
                    issue(path, "stale-resolution",
                          "Supply empty tables, evidence and matching SHA256 of the raw preserved-provider query at this path.")
                    continue
                resolution_note = evidence["evidence"]
            raw = node["query"]
            entry["status"] = "converted"
            entry["preservedProvider"] = {"queryType": qt, "resourceType": surface["resourceType"]}
            entry["resolutionEvidence"] = resolution_note
            entry["workspaceFunctions"] = []
            entry["conversion"] = {
                "sourceId": path,
                "artifactType": "workbook",
                "status": "converted",
                "convertedKql": raw,
                "resolvedTables": [],
                "mappingTier": "1to1",
                "renamedTables": {},
                "renamedAsimTables": {},
                "diff": [],
                "schemaMap": {},
                "recommendations": [],
                "confidence": 0.7,
                "unsupported": [],
                "validation": None,
                "blockedReason": None,
            }
            preserved_nodes.add(id(node))
            continue
        if qt not in (0, None, AH) or (
            qt != AH and (surface["resourceType"] or "").lower() not in ("", LA)
        ):
            entry["status"] = "blocked"
            issue(path, "unsupported-provider",
                  f"Provider {qt!r}/{surface['resourceType']!r} is retained unchanged; "
                  "supply a reviewed provider migration.")
            continue
        try:
            raw = _raw_query(node["query"], qt)
        except ValueError as exc:
            entry["status"] = "blocked"
            issue(path, "query-format", str(exc))
            continue
        code = "".join(text if kind == "code" else " " * len(text)
                       for kind, text in rewrite._segments(raw))
        if re.search(r"\b(?:workspace|app|resource|cluster|database)\s*\(", code,
                     re.IGNORECASE):
            entry["status"] = "blocked"
            issue(path, "explicit-scope-function",
                  "Explicit workspace/app/resource/cluster/database function cannot be "
                  "replaced by blank AH selection. Keep this panel and review its sources.")
            continue
        evidence = (resolutions or {}).get(path)
        reviewed_tables = (evidence.get("tables") if isinstance(evidence, dict)
                           and isinstance(evidence.get("tables"), list) else tables) or ()
        explicit_calls = opaque_functions(raw, include_bare=False)
        opaque = opaque_functions(raw) - (
            set(reviewed_tables) - explicit_calls - set(allowed_workspace_functions)
            - (set(evidence.get("workspaceFunctions", ()))
               if isinstance(evidence, dict) and isinstance(evidence.get("workspaceFunctions"), list)
               else set())
        )
        function_names = evidence.get("workspaceFunctions", []) if isinstance(evidence, dict) else []
        if (not isinstance(function_names, list)
                or any(not isinstance(name, str) for name in function_names)
                or len(set(function_names)) != len(function_names)
                or set(function_names) != opaque
                or not opaque <= set(allowed_workspace_functions)):
            entry["status"] = "blocked"
            issue(path, "saved-function",
                  f"Source function(s) {', '.join(sorted(opaque))} need a reviewed AH "
                  "workspace definition, exact aliases and separate underlying table evidence.")
            continue
        resolved = tables
        entry["resolutionEvidence"] = "caller-reviewed tables" if tables is not None else None
        if resolved is None and evidence is None and not preserve_sentinel_tables:
            bare_sources = _bare_source_identifiers(code)
            alert_tables = {"SecurityAlert", "SecurityIncident", "AlertInfo", "AlertEvidence"}
            if bare_sources and bare_sources <= alert_tables and not opaque:
                resolved = sorted(bare_sources)
                entry["resolutionEvidence"] = "deterministic SecurityAlert/SecurityIncident to AlertInfo/AlertEvidence migration"
        if evidence is not None:
            if (not isinstance(evidence, dict)
                    or evidence.get("querySha256") != query_hash(original["node"]["query"])
                    or not isinstance(evidence.get("tables"), list)
                    or not all(isinstance(t, str) and t for t in evidence["tables"])
                    or not evidence.get("evidence")):
                entry["status"] = "blocked"
                issue(path, "stale-resolution",
                      "Supply tables, evidence and matching SHA256 of the raw query at this path.")
                continue
            resolved = evidence["tables"]
            entry["resolutionEvidence"] = evidence["evidence"]
        if opaque:
            entry["workspaceFunctions"] = sorted(opaque)
            if not resolved or opaque & set(resolved):
                entry["status"] = "blocked"
                issue(path, "function-underlying-tables",
                      "Supply underlying source tables separately from workspace function aliases.")
                continue
        contract = migrator.convert(raw, tables=resolved, source_id=path,
                                    artifact_type="workbook", resolve=False,
                                    preserve_sentinel_tables=preserve_sentinel_tables)
        entry["conversion"] = contract
        if contract.get("notes"):
            entry["notes"] = list(contract["notes"])
            entry["provenanceNotes"] = list(contract["notes"])
            for note in contract["notes"]:
                if note not in provenance_notes:
                    provenance_notes.append(note)
        if "Watchlist" in contract["resolvedTables"]:
            entry["referenceInputs"] = ["Watchlist"]
        entry["status"] = contract["status"]
        if contract["status"] == "blocked" or resolved is None:
            issue(path, "mapping-or-resolution",
                  contract["blockedReason"] or
                  "No offline source evidence. Supply --resolutions (per-path query hash, "
                  "tables and evidence) or --tables after reviewing ALL query sources.")
            continue
        if contract["unsupported"] or contract["status"] == "needs-review":
            issue(path, "query-review",
                  "; ".join(x["reason"] for x in contract["unsupported"])
                  or "Shared migrator requires source/mapping review; conversion is not deterministic.")
        if opaque and contract["convertedKql"] != raw:
            entry["status"] = "blocked"
            issue(path, "function-query-rewrite",
                  "Shared conversion would modify a preserved function query; review a source change separately.")
            continue
        node["query"] = contract["convertedKql"]
        node["queryType"] = AH
        converted_nodes.add(id(node))
        if surface["parameter"]:
            gates.add("ah-query-backed-parameters")
        # The mapping catalog's resolve-to-self does not establish blank-selection visibility.
        if contract["resolvedTables"]:
            gates.add("blank-ah-selection-table-visibility")
        if opaque:
            gates.add("sentinel-workspace-function-availability-and-branch-coverage")
        if re.search(r"\bexternaldata\s*[\[(]", code):
            gates.add("external-source-binding-and-availability")
        if references(raw) - references(node["query"]):
            raise AssertionError(f"Parameter templates lost at {path}")

    # Blocked panels keep the scope inputs they still need. Revisit the graph
    # before removing any helper; an unsupported sibling is not disposable.
    blocked = [s for s, r in zip(surfaces, reports) if r["status"] == "blocked"
               or (id(s["node"]) not in (converted_nodes | preserved_nodes)
                   and r["status"] != "removed-scope-helper")]
    if blocked:
        protected = set()
        nodes = dict(walk(doc))
        for surface in blocked:
            protected |= references(surface["node"])
            ancestor = surface["path"].rsplit("/", 1)[0]
            while True:
                node = nodes.get(ancestor, {})
                for key in SCOPE_KEYS | {"resourceContextFromParameter"}:
                    if key in node:
                        protected |= references({key: node[key]})
                if not ancestor:
                    break
                ancestor = ancestor.rsplit("/", 1)[0]
        entries, removed, retained_scope = _scope_parameters(doc, protected)
        removed_prefixes = [path + "/" for path, p in entries if p["name"] in removed]
        for surface, entry in zip(surfaces, reports):
            if entry["status"] == "removed-scope-helper" and not any(
                surface["path"].startswith(prefix) for prefix in removed_prefixes
            ):
                entry["status"] = "retained-scope-helper"
                issue(surface["path"], "blocked-panel-scope",
                      "Helper retained because an unsupported panel still needs its scope.")

    retained_scope_nodes = {id(p) for _, p in entries if p["name"] in retained_scope}

    def _non_preserved_references(value, cur_path="") -> set[str]:
        found = set()
        if any(cur_path == prefix[:-1] or cur_path.startswith(prefix) for prefix in removed_prefixes):
            return found
        if isinstance(value, dict):
            if id(value) in preserved_nodes or id(value) in retained_scope_nodes:
                return found
            for key, child in value.items():
                if key in SCOPE_KEYS | {"resourceContextFromParameter"}:
                    continue
                if key in PARAMETER_KEYS and isinstance(child, str):
                    found.add(child)
                if key == "linkTarget" and child == "parameter":
                    found.add(value.get("cellValue", ""))
                escaped = key.replace("~", "~0").replace("/", "~1")
                found |= _non_preserved_references(child, f"{cur_path}/{escaped}")
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                found |= _non_preserved_references(child, f"{cur_path}/{idx}")
        elif isinstance(value, str):
            found |= set(TOKEN.findall(value))
        return {x for x in found if x}

    non_preserved_refs = _non_preserved_references(doc)
    for path, p in entries:
        if p["name"] in retained_scope and p["name"] in non_preserved_refs:
            issue(path, "scope-used-by-content",
                  f"{p['name']} is used by retained business content or a drilldown. "
                  "Retained; manually replace its Azure scope semantics.")

    # Keep item arrays and layout untouched, including now-empty parameter groups.
    for _, node in walk(doc):
        if isinstance(node.get("parameters"), list):
            node["parameters"] = [p for p in node["parameters"]
                                  if p.get("name") not in removed]

    def clean(value, path=""):
        if isinstance(value, dict):
            descendants = query_surfaces(value)
            safe = all(id(s["node"]) in (converted_nodes | preserved_nodes) for s in descendants)
            binding_container = (
                bool(descendants) or not path
                or "parameters" in value or "items" in value
                or re.search(r"/parameters/\d+$", path)
                or str(value.get("version", "")).startswith(("KqlItem/", "KqlParameterItem/",
                                                            "NotebookGroup/"))
            )
            if id(value) in converted_nodes or (
                safe and binding_container
                and id(value) not in retained_scope_nodes
                and id(value) not in preserved_nodes
            ):
                for key in SCOPE_KEYS | {"resourceContextFromParameter"}:
                    value.pop(key, None)
                if value.get("resourceType", "").lower() in (
                    LA, "microsoft.resourcegraph/resources", "microsoft.insights/components"
                ):
                    value.pop("resourceType", None)
                if "parameters" in value or "items" in value:
                    value.pop("queryType", None)
                context = value.get("context")
                if isinstance(context, dict) and isinstance(context.get("ownerId"), str):
                    owner = context["ownerId"]
                    if "/subscriptions/" in owner.lower() or references(owner) & removed:
                        context.pop("ownerId")
            for key, child in list(value.items()):
                clean(child, path + "/" + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                clean(child, f"{path}/{index}")

    clean(doc)
    output_paths = {id(s["node"]): s["path"] for s in query_surfaces(doc)}
    for surface, entry in zip(surfaces, reports):
        entry["outputPath"] = output_paths.get(id(surface["node"]))
    report_payload = {
        "status": "blocked" if issues else ("needs-validation" if gates else "converted"),
        "queries": reports,
        "removedParameters": [{"name": p["name"], "sourcePath": path}
                              for path, p in entries if p["name"] in removed],
        "issues": issues,
        "gates": [{"code": gate, "status": "unverified"} for gate in sorted(gates)],
        "validation": {"localStructureOnly": True, "runtime": "not-run", "ui": "not-run"},
    }
    if provenance_notes:
        report_payload["notes"] = list(provenance_notes)
        report_payload["provenanceNotes"] = list(provenance_notes)
    return {
        "workbook": doc,
        "report": report_payload,
    }
