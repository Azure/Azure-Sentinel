"""KQL tokenization and deterministic ingestion-parser checks."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .common import Finding

ALLOWED_DCR_OPERATORS = {
    "extend",
    "parse",
    "project",
    "project-away",
    "project-rename",
    "where",
}
ALLOWED_FILTER_OPERATORS = {
    "extend",
    "parse",
    "project-rename",
    "where",
}


@dataclass(frozen=True)
class KqlRule:
    code: str
    construct: str
    pattern: re.Pattern[str]
    message: str


KQL_RULES = (
    KqlRule("KQL002", "invoke", re.compile(r"\|\s*invoke\b", re.I), "Inline the invoked function."),
    KqlRule("KQL003", "ASIM helper", re.compile(r"\b_ASIM_[A-Za-z0-9_]+", re.I), "Inline ASIM helper functions."),
    KqlRule("KQL004", "lookup", re.compile(r"\|\s*lookup\b", re.I), "Replace lookup with DCR-compatible scalar mapping."),
    KqlRule("KQL006", "union", re.compile(r"(^|\|)\s*union\b", re.I), "A DCR parser must use one source pipeline."),
    KqlRule("KQL007", "distinct", re.compile(r"\|\s*distinct\b", re.I), "Per-row transformations cannot deduplicate records."),
    KqlRule("KQL008", "materialize", re.compile(r"\bmaterialize\s*\(", re.I), "Remove the query-time caching hint."),
    KqlRule("KQL009", "project-reorder", re.compile(r"\|\s*project-reorder\b", re.I), "Column order is not part of the DCR contract."),
    KqlRule("KQL010", "dynamic literal", re.compile(r"\bdynamic\s*\(", re.I), "Use parse_json for dynamic literals."),
    KqlRule("KQL011", "has_any", re.compile(r"\bhas_any\s*\(", re.I), "Expand to supported scalar comparisons."),
    KqlRule("KQL012", "has_all", re.compile(r"\bhas_all\s*\(", re.I), "Expand to supported scalar comparisons."),
    KqlRule("KQL013", "coalesce", re.compile(r"\bcoalesce\s*\(", re.I), "Rewrite with iif and null or empty checks."),
    KqlRule("KQL014", "parse-kv", re.compile(r"\|\s*parse-kv\b", re.I), "Rewrite with supported parsing expressions."),
    KqlRule("KQL015", "parse-where", re.compile(r"\|\s*parse-where\b", re.I), "Rewrite with parse or extract plus where."),
    KqlRule("KQL016", "case-insensitive operator", re.compile(r"==~|!=~|\bin~|\b!in~", re.I), "Normalize operands and use the supported operator."),
    KqlRule("KQL017", "column_ifexists", re.compile(r"\bcolumn_ifexists\s*\(", re.I), "Use columnifexists or a confirmed source column."),
    KqlRule("KQL018", "Unix time conversion", re.compile(r"\bunixtime_(milliseconds|seconds|microseconds|nanoseconds)_todatetime\s*\(", re.I), "Rewrite with datetime arithmetic."),
    KqlRule("KQL019", "between", re.compile(r"\b!?between\s*\(", re.I), "Rewrite as explicit comparisons."),
    KqlRule("KQL020", "bag_pack", re.compile(r"\bbag_pack(_columns)?\s*\(", re.I), "Use pack or an explicit supported projection."),
    KqlRule("KQL021", "replace_string", re.compile(r"\breplace_string\s*\(", re.I), "Use the DCR-supported replace form."),
    KqlRule("KQL022", "array_index_of", re.compile(r"\barray_index_of\s*\(", re.I), "Rewrite as supported scalar logic."),
    KqlRule("KQL023", "array_slice", re.compile(r"\barray_slice\s*\(", re.I), "Rewrite with indexof and substring."),
    KqlRule("KQL024", "trim", re.compile(r"\btrim(_start|_end)?\s*\(", re.I), "Rewrite with anchored replace."),
    KqlRule("KQL025", "parse_url", re.compile(r"\bparse_url\s*\(", re.I), "Extract only the required URL components."),
    KqlRule("KQL026", "parse_user_agent", re.compile(r"\bparse_user_agent\s*\(", re.I), "Extract only the required user-agent fields."),
    KqlRule("KQL027", "mv operator", re.compile(r"\|\s*mv-(apply|expand)\b", re.I), "DCR transformations cannot fan out rows."),
    KqlRule("KQL028", "summarize", re.compile(r"\|\s*summarize\b", re.I), "DCR transformations process each record independently."),
    KqlRule("KQL029", "aggregation function", re.compile(r"\b(make_set|make_list|make_set_if|make_list_if|take_anyif|take_any)\s*\(", re.I), "Aggregation functions are not supported."),
    KqlRule("KQL030", "bag_merge", re.compile(r"\bbag_merge\s*\(", re.I), "No sound DCR equivalent is available."),
    KqlRule("KQL031", "join", re.compile(r"\|\s*join\b", re.I), "A DCR transformation has one input stream."),
    KqlRule("KQL032", "tohex", re.compile(r"\btohex\s*\(", re.I), "No general DCR equivalent is available."),
    KqlRule(
        "KQL033",
        "IP utility",
        re.compile(
            r"\b(ipv6_is_match|ipv4_netmask_suffix)\s*\(",
            re.I,
        ),
        "This IP utility is not supported by DCR transformations.",
    ),
    KqlRule("KQL034", "url_decode", re.compile(r"\burl_decode\s*\(", re.I), "No exact DCR equivalent is available."),
    KqlRule("KQL035", "toscalar", re.compile(r"\btoscalar\s*\(", re.I), "Subqueries are not supported by the parser contract."),
    KqlRule("KQL036", "project-keep", re.compile(r"\|\s*project-keep\b", re.I), "Emit an explicit supported projection."),
    KqlRule("KQL037", "wildcard projection", re.compile(r"\|\s*project-(away|keep)\s+[^|\r\n]*\*", re.I), "Resolve wildcard projections explicitly."),
    KqlRule("KQL038", "externaldata", re.compile(r"\bexternaldata\s*\(", re.I), "External data sources cannot be used in a DCR transformation."),
)


def mask_kql(text: str) -> str:
    """Mask comments and string contents while preserving positions and lines."""
    chars = list(text)
    index = 0
    length = len(chars)
    while index < length:
        char = chars[index]
        if char == "/" and index + 1 < length and chars[index + 1] == "/":
            while index < length and chars[index] != "\n":
                if chars[index] != "\r":
                    chars[index] = " "
                index += 1
            continue
        if (
            char == "@"
            and index + 1 < length
            and chars[index + 1] in {'"', "'"}
        ):
            quote = chars[index + 1]
            chars[index] = " "
            chars[index + 1] = " "
            index += 2
            while index < length:
                if chars[index] == quote:
                    if index + 1 < length and chars[index + 1] == quote:
                        chars[index] = " "
                        chars[index + 1] = " "
                        index += 2
                        continue
                    chars[index] = " "
                    index += 1
                    break
                if chars[index] not in {"\r", "\n"}:
                    chars[index] = " "
                index += 1
            continue
        if char in {'"', "'"}:
            quote = char
            chars[index] = " "
            index += 1
            while index < length:
                if chars[index] == "\\" and index + 1 < length:
                    chars[index] = " "
                    index += 1
                    if chars[index] not in {"\r", "\n"}:
                        chars[index] = " "
                    index += 1
                    continue
                if chars[index] == quote:
                    if index + 1 < length and chars[index + 1] == quote:
                        chars[index] = " "
                        chars[index + 1] = " "
                        index += 2
                        continue
                    chars[index] = " "
                    index += 1
                    break
                if chars[index] not in {"\r", "\n"}:
                    chars[index] = " "
                index += 1
            continue
        index += 1
    return "".join(chars)


def compact_kql(text: str) -> str:
    """Remove non-semantic indentation and line comments outside strings."""
    output: list[str] = []
    index = 0
    length = len(text)
    quote: str | None = None
    verbatim = False
    at_line_start = True
    while index < length:
        char = text[index]
        if quote is not None:
            output.append(char)
            if char in {"\r", "\n"}:
                at_line_start = True
            else:
                at_line_start = False
            if char == quote:
                if index + 1 < length and text[index + 1] == quote:
                    output.append(text[index + 1])
                    index += 2
                    continue
                quote = None
                verbatim = False
            elif not verbatim and char == "\\" and index + 1 < length:
                output.append(text[index + 1])
                if text[index + 1] in {"\r", "\n"}:
                    at_line_start = True
                else:
                    at_line_start = False
                index += 2
                continue
            index += 1
            continue
        if char == "/" and index + 1 < length and text[index + 1] == "/":
            index += 2
            while index < length and text[index] not in {"\r", "\n"}:
                index += 1
            continue
        if char in {"\r", "\n"}:
            while output and output[-1] in {" ", "\t"}:
                output.pop()
            output.append(char)
            at_line_start = True
            index += 1
            continue
        if at_line_start and char in {" ", "\t"}:
            index += 1
            continue
        if (
            char == "@"
            and index + 1 < length
            and text[index + 1] in {'"', "'"}
        ):
            verbatim = True
            quote = text[index + 1]
            output.append(char)
            output.append(quote)
            at_line_start = False
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
        output.append(char)
        if char not in {" ", "\t"}:
            at_line_start = False
        index += 1
    return "".join(output).strip()


def _canonical_kql(value: str) -> str:
    output: list[str] = []
    index = 0
    length = len(value)
    quote: str | None = None
    verbatim = False
    pending_space = False
    while index < length:
        char = value[index]
        if quote is not None:
            output.append(char)
            if char == quote:
                if index + 1 < length and value[index + 1] == quote:
                    output.append(value[index + 1])
                    index += 2
                    continue
                quote = None
                verbatim = False
            elif not verbatim and char == "\\" and index + 1 < length:
                output.append(value[index + 1])
                index += 2
                continue
            index += 1
            continue
        if char.isspace():
            pending_space = True
            index += 1
            continue
        if pending_space and output:
            output.append(" ")
        pending_space = False
        if (
            char == "@"
            and index + 1 < length
            and value[index + 1] in {'"', "'"}
        ):
            verbatim = True
            quote = value[index + 1]
            output.append(char)
            output.append(quote)
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
        output.append(char)
        index += 1
    return "".join(output).strip()


def split_pipeline(query: str) -> list[str]:
    parts: list[str] = []
    buffer: list[str] = []
    index = 0
    length = len(query)
    quote: str | None = None
    verbatim = False
    while index < length:
        char = query[index]
        if quote is not None:
            buffer.append(char)
            if char == quote:
                if index + 1 < length and query[index + 1] == quote:
                    buffer.append(query[index + 1])
                    index += 2
                    continue
                quote = None
                verbatim = False
            elif not verbatim and char == "\\" and index + 1 < length:
                buffer.append(query[index + 1])
                index += 2
                continue
            index += 1
            continue
        if char == "/" and index + 1 < length and query[index + 1] == "/":
            while index < length and query[index] != "\n":
                index += 1
            buffer.append(" ")
            continue
        if (
            char == "@"
            and index + 1 < length
            and query[index + 1] in {'"', "'"}
        ):
            verbatim = True
            quote = query[index + 1]
            buffer.append(char)
            buffer.append(quote)
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
            buffer.append(char)
            index += 1
            continue
        if char == "|":
            parts.append(_canonical_kql("".join(buffer)))
            buffer = []
            index += 1
            continue
        buffer.append(char)
        index += 1
    parts.append(_canonical_kql("".join(buffer)))
    return parts


def split_kql_statements(query: str) -> list[str]:
    """Split top-level KQL statements while preserving strings and function bodies."""
    statements: list[str] = []
    buffer: list[str] = []
    index = 0
    length = len(query)
    quote: str | None = None
    verbatim = False
    line_comment = False
    paren_depth = 0
    brace_depth = 0
    bracket_depth = 0
    while index < length:
        char = query[index]
        if line_comment:
            if char == "\n":
                line_comment = False
                buffer.append(" ")
            index += 1
            continue
        if quote is not None:
            buffer.append(char)
            if char == quote:
                if index + 1 < length and query[index + 1] == quote:
                    buffer.append(query[index + 1])
                    index += 2
                    continue
                quote = None
                verbatim = False
            elif not verbatim and char == "\\" and index + 1 < length:
                buffer.append(query[index + 1])
                index += 2
                continue
            index += 1
            continue
        if char == "/" and index + 1 < length and query[index + 1] == "/":
            line_comment = True
            index += 2
            continue
        if (
            char == "@"
            and index + 1 < length
            and query[index + 1] in {'"', "'"}
        ):
            verbatim = True
            quote = query[index + 1]
            buffer.append(char)
            buffer.append(quote)
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
            buffer.append(char)
            index += 1
            continue
        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth = max(0, paren_depth - 1)
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth = max(0, brace_depth - 1)
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth = max(0, bracket_depth - 1)
        elif (
            char == ";"
            and paren_depth == 0
            and brace_depth == 0
            and bracket_depth == 0
        ):
            statement = _canonical_kql("".join(buffer))
            if statement:
                statements.append(statement)
            buffer = []
            index += 1
            continue
        buffer.append(char)
        index += 1
    statement = _canonical_kql("".join(buffer))
    if statement:
        statements.append(statement)
    return statements


def _pipeline_operator(stage: str) -> str | None:
    match = re.match(r"([a-z][a-z0-9-]*)\b", stage, re.I)
    return match.group(1).lower() if match else None


def _validate_statement_shape(
    query: str, field: str, findings: list[Finding]
) -> str | None:
    statements = split_kql_statements(query)
    if not statements:
        findings.append(
            Finding("KQL039", field, "Query must not be empty.")
        )
        return None
    for statement in statements[:-1]:
        let_match = re.match(
            r"let\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?P<rhs>.+)$",
            statement,
            re.I | re.S,
        )
        if let_match is None:
            findings.append(
                Finding(
                    "KQL042",
                    field,
                    "Only let statements may precede the final source pipeline.",
                )
            )
            continue
        rhs = let_match.group("rhs").strip()
        if "|" in rhs:
            root_match = re.match(
                r"(source|print|datatable\b)",
                rhs,
                re.I,
            )
            if root_match is None and not rhs.startswith("("):
                findings.append(
                    Finding(
                        "KQL043",
                        field,
                        "A tabular let binding may only use source, print, or datatable.",
                    )
                )
    return statements[-1]


def _query_uses_source_table(query: str, table_name: str) -> bool:
    masked_query = mask_kql(query)
    identifier_pattern = re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(table_name)}(?![A-Za-z0-9_])",
        re.I,
    )
    for match in identifier_pattern.finditer(masked_query):
        line_start = masked_query.rfind("\n", 0, match.start()) + 1
        line_end = masked_query.find("\n", match.end())
        if line_end < 0:
            line_end = len(masked_query)
        prefix = masked_query[line_start:match.start()].rstrip()
        suffix = masked_query[match.end():line_end].lstrip()
        source_position = (
            not prefix
            or prefix[-1:] in {"{", "(", ",", "=", ";"}
            or bool(
                re.search(
                    r"\bunion(?:\s+[A-Za-z_][A-Za-z0-9_]*"
                    r"\s*=\s*\S+)*\s*$",
                    prefix,
                    re.I,
                )
            )
        )
        source_terminator = not suffix or suffix[0] in {"|", ",", ")"}
        if source_position and source_terminator:
            return True
    return False


def _parse_kql_string_literal(
    query: str, start: int
) -> tuple[str, int] | None:
    index = start
    while index < len(query) and query[index].isspace():
        index += 1
    verbatim = False
    if (
        index + 1 < len(query)
        and query[index] == "@"
        and query[index + 1] in {"'", '"'}
    ):
        verbatim = True
        index += 1
    if index >= len(query) or query[index] not in {"'", '"'}:
        return None
    quote = query[index]
    index += 1
    value: list[str] = []
    escapes = {
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "\\": "\\",
        "'": "'",
        '"': '"',
    }
    while index < len(query):
        char = query[index]
        if char == quote:
            if index + 1 < len(query) and query[index + 1] == quote:
                value.append(quote)
                index += 2
                continue
            return "".join(value), index + 1
        if not verbatim and char == "\\":
            if index + 1 >= len(query):
                raise ValueError("KQL string literal ends with an escape.")
            escaped = query[index + 1]
            value.append(escapes.get(escaped, escaped))
            index += 2
            continue
        value.append(char)
        index += 1
    raise ValueError("KQL string literal is not terminated.")


def _resolve_static_string_assignment(query: str, field: str) -> str:
    masked_query = mask_kql(query)
    assignment_pattern = re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(field)}"
        r"(?![A-Za-z0-9_])\s*=",
        re.I,
    )
    matches = list(assignment_pattern.finditer(masked_query))
    if not matches:
        raise ValueError(
            f"ParserQuery does not assign a static {field} value."
        )
    values: list[str] = []
    for match in matches:
        parsed = _parse_kql_string_literal(query, match.end())
        if parsed is None:
            raise ValueError(
                f"ParserQuery assigns {field} from a non-static expression."
            )
        values.append(parsed[0])
    unique_values = sorted(set(values))
    if len(unique_values) != 1:
        raise ValueError(
            f"ParserQuery assigns conflicting {field} values: "
            f"{unique_values}."
        )
    value = unique_values[0]
    if not value:
        raise ValueError(f"ParserQuery assigns an empty {field} value.")
    if any(
        ord(char) < 32 or char in '<>:"/\\|?*'
        for char in value
    ):
        raise ValueError(
            f"ParserQuery {field} value cannot be used in a fixture name: "
            f"{value!r}."
        )
    return value


def resolve_source_specific_fixture(
    parser_query: str,
    schema: str,
    source_raw_table: str,
) -> tuple[str, str, str]:
    event_vendor = _resolve_static_string_assignment(
        parser_query, "EventVendor"
    )
    event_product = _resolve_static_string_assignment(
        parser_query, "EventProduct"
    )
    fixture_name = (
        f"{event_vendor}_{event_product}_{schema}_{source_raw_table}"
        "_IngestedLogs.csv"
    )
    return (
        event_vendor,
        event_product,
        f"Sample Data/ASIM/{fixture_name}",
    )


def _identity_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _name_tokens(value: str) -> list[str]:
    words = re.findall(r"[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|\d+", value)
    return [
        word.lower()
        for word in words
        if word.lower()
        not in {
            "a",
            "asim",
            "ingest",
            "ingestion",
            "parser",
            "sim",
            "time",
        }
    ]


def _token_overlap(first: str, second: str) -> list[str]:
    return sorted(set(_name_tokens(first)) & set(_name_tokens(second)))
