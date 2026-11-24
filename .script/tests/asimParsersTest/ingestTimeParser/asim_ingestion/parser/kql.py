"""KQL policy metadata and deterministic ingestion-parser helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

ALLOWED_FILTER_OPERATORS = {
    "where",
}
QUERY_TIME_PARAMETER_TYPES = {
    "bool",
    "boolean",
    "datetime",
    "dynamic",
    "int",
    "long",
    "real",
    "string",
}
QUERY_TIME_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_IGNORED_KQL_TOKENS_RE = re.compile(
    r"//[^\r\n]*|/\*.*?\*/|```.*?```"
    r"|@'(?:''|[^'])*'"
    r'|@"(?:""|[^"])*"'
    r"|'(?:\\.|''|[^'\\])*'"
    r'|"(?:\\.|""|[^"\\])*"',
    flags=re.DOTALL,
)
_MANAGEMENT_COMMAND_RE = re.compile(
    r"(?:^|;)\s*(\.[A-Za-z])",
    flags=re.MULTILINE,
)


@dataclass(frozen=True)
class KqlRule:
    code: str
    construct: str
    message: str


def _named_rules(rule: KqlRule, *names: str) -> dict[str, KqlRule]:
    return {name: rule for name in names}


DENY_EXTERNAL_ASIM_HELPER_REFERENCE_RULE = KqlRule(
    "KQL003",
    "ASIM helper",
    "Inline ASIM helper functions.",
)

DENY_KQL_OPERATOR_RULES = {
    "InvokeOperator": KqlRule(
        "KQL002", "invoke", "Inline the invoked function."
    ),
    "LookupOperator": KqlRule(
        "KQL004",
        "lookup",
        "Replace lookup with DCR-compatible scalar mapping.",
    ),
    "UnionOperator": KqlRule(
        "KQL006", "union", "A DCR parser must use one source pipeline."
    ),
    "DistinctOperator": KqlRule(
        "KQL007",
        "distinct",
        "Per-row transformations cannot deduplicate records.",
    ),
    "MvApplyOperator": KqlRule(
        "KQL027",
        "mv operator",
        "DCR transformations cannot fan out rows.",
    ),
    "MvExpandOperator": KqlRule(
        "KQL027",
        "mv operator",
        "DCR transformations cannot fan out rows.",
    ),
    "SummarizeOperator": KqlRule(
        "KQL028",
        "summarize",
        "DCR transformations process each record independently.",
    ),
    "JoinOperator": KqlRule(
        "KQL031", "join", "A DCR transformation has one input stream."
    ),
}

DENY_KQL_FUNCTION_RULES = {
    **_named_rules(
        KqlRule(
            "KQL029",
            "aggregation function",
            "Aggregation functions are not supported.",
        ),
        "make_set",
        "make_list",
        "make_set_if",
        "make_list_if",
        "take_anyif",
        "take_any",
    ),
}

DENY_KQL_CONSTRUCT_RULES = {
    "ToScalarExpression": KqlRule(
        "KQL035",
        "toscalar",
        "Subqueries are not supported by the parser contract.",
    ),
    "WildcardedName": KqlRule(
        "KQL037",
        "wildcard projection",
        "Resolve wildcard projections explicitly.",
    ),
}

DENY_UNTRUSTED_KQL_OPERATOR_RULES = {
    "EvaluateOperator": KqlRule(
        "KQL047",
        "evaluate",
        "Plugin execution is not allowed in untrusted parser KQL.",
    ),
}

DENY_UNTRUSTED_KQL_FUNCTION_RULES = {
    **_named_rules(
        KqlRule(
            "KQL045",
            "cross-resource function",
            "Cross-workspace, cluster, and database access is not allowed.",
        ),
        "workspace",
        "cluster",
        "database",
    ),
    "external_table": KqlRule(
        "KQL046",
        "external_table",
        "External table access is not allowed in untrusted parser KQL.",
    ),
}

DENY_UNTRUSTED_KQL_CONSTRUCT_RULES = {
    "ExternalDataExpression": KqlRule(
        "KQL038",
        "externaldata",
        "External data sources are not allowed in untrusted parser KQL.",
    ),
}

DENY_MANAGEMENT_COMMAND_RULE = KqlRule(
    "KQL048",
    "management command",
    "Kusto management commands are not allowed in parser KQL.",
)


def _mask_kql_non_code(query: str) -> str:
    return _IGNORED_KQL_TOKENS_RE.sub(
        lambda match: re.sub(r"[^\r\n]", " ", match.group()),
        query,
    )


def iter_untrusted_kql_rule_matches(
    analysis: dict[str, Any],
    query: str,
) -> list[tuple[KqlRule, dict[str, Any]]]:
    matches: list[tuple[KqlRule, dict[str, Any]]] = []
    for operator in analysis["operators"]:
        rule = DENY_UNTRUSTED_KQL_OPERATOR_RULES.get(operator["type"])
        if rule is not None:
            matches.append((rule, operator))
    for function in analysis["functions"]:
        name = function.get("name")
        rule = (
            DENY_UNTRUSTED_KQL_FUNCTION_RULES.get(name.casefold())
            if isinstance(name, str)
            else None
        )
        if rule is not None:
            matches.append((rule, function))
    for construct in analysis["constructs"]:
        rule = DENY_UNTRUSTED_KQL_CONSTRUCT_RULES.get(
            construct["type"]
        )
        if rule is not None:
            matches.append((rule, construct))

    command = _MANAGEMENT_COMMAND_RE.search(_mask_kql_non_code(query))
    if command is not None:
        start = command.start(1)
        line = query.count("\n", 0, start) + 1
        column = start - query.rfind("\n", 0, start)
        matches.append(
            (
                DENY_MANAGEMENT_COMMAND_RULE,
                {
                    "location": {
                        "start": start,
                        "length": 1,
                        "line": line,
                        "column": column,
                        "text": ".",
                        "normalizedText": ".",
                    },
                },
            )
        )
    return matches


def query_time_parameter_errors(
    parser_params: Any,
) -> list[tuple[str, str]]:
    if not isinstance(parser_params, list):
        return [("ParserParams", "ParserParams must be an array.")]

    errors: list[tuple[str, str]] = []
    seen_names: set[str] = set()
    for index, parameter in enumerate(parser_params):
        field = f"ParserParams[{index}]"
        if not isinstance(parameter, dict):
            errors.append((field, "Parser parameter must be an object."))
            continue
        name = parameter.get("Name")
        parameter_type = parameter.get("Type")
        if (
            not isinstance(name, str)
            or not QUERY_TIME_IDENTIFIER_RE.fullmatch(name)
        ):
            errors.append(
                (f"{field}.Name", "Parameter name must be a KQL identifier.")
            )
        else:
            normalized_name = name.casefold()
            if normalized_name in seen_names:
                errors.append(
                    (f"{field}.Name", "Parameter names must be unique.")
                )
            seen_names.add(normalized_name)

        normalized_type = (
            parameter_type.strip().casefold()
            if isinstance(parameter_type, str)
            else ""
        )
        if (
            parameter_type != normalized_type
            or normalized_type not in QUERY_TIME_PARAMETER_TYPES
        ):
            errors.append(
                (
                    f"{field}.Type",
                    "Parameter type must be one of "
                    + ", ".join(sorted(QUERY_TIME_PARAMETER_TYPES))
                    + ".",
                )
            )
            continue
        if "Default" not in parameter:
            errors.append(
                (f"{field}.Default", "Parameter default is required.")
            )
            continue
        default = parameter["Default"]
        if normalized_type in {"bool", "boolean"}:
            valid_default = isinstance(default, bool)
        elif normalized_type == "string":
            valid_default = isinstance(default, str)
        elif normalized_type == "dynamic":
            valid_default = (
                isinstance(default, (list, dict))
                or default == "dynamic([])"
            )
        elif normalized_type == "datetime":
            valid_default = (
                isinstance(default, str)
                and (
                    default == "datetime(null)"
                    or re.fullmatch(r"[0-9T:.+\-Z]+", default) is not None
                )
            )
        else:
            valid_default = (
                not isinstance(default, bool)
                and isinstance(default, (int, float))
            ) or default == f"{normalized_type}(null)"
        if not valid_default:
            errors.append(
                (
                    f"{field}.Default",
                    f"Default is invalid for type {normalized_type}.",
                )
            )
    return errors


def query_uses_source_table(
    analysis: dict[str, Any],
    table_name: str,
) -> bool:
    return any(
        reference["name"].casefold() == table_name.casefold()
        for reference in analysis["sourceReferences"]
    )


def _resolve_static_string_assignment(
    analysis: dict[str, Any],
    field: str,
) -> str:
    matches = [
        assignment
        for assignment in analysis["assignments"]
        if assignment["name"].casefold() == field.casefold()
    ]
    if not matches:
        raise ValueError(
            f"ParserQuery does not assign a static {field} value."
        )
    values: list[str] = []
    for assignment in matches:
        if not assignment["isStringLiteral"]:
            raise ValueError(
                f"ParserQuery assigns {field} from a non-static expression."
            )
        values.append(assignment["stringValue"])
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
    analysis: dict[str, Any],
    schema: str,
    source_raw_table: str,
) -> tuple[str, str, str]:
    event_vendor = _resolve_static_string_assignment(
        analysis, "EventVendor"
    )
    event_product = _resolve_static_string_assignment(
        analysis, "EventProduct"
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
