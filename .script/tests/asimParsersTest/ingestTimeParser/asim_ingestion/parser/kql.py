"""KQL policy metadata and deterministic ingestion-parser helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

ALLOWED_FILTER_OPERATORS = {
    "extend",
    "parse",
    "parse-kv",
    "project-rename",
    "where",
}


@dataclass(frozen=True)
class KqlRule:
    code: str
    construct: str
    message: str


def _named_rules(rule: KqlRule, *names: str) -> dict[str, KqlRule]:
    return {name: rule for name in names}


ASIM_HELPER_RULE = KqlRule(
    "KQL003",
    "ASIM helper",
    "Inline ASIM helper functions.",
)

KQL_OPERATOR_RULES = {
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

KQL_FUNCTION_RULES = {
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

KQL_CONSTRUCT_RULES = {
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
    "ExternalDataExpression": KqlRule(
        "KQL038",
        "externaldata",
        "External data sources cannot be used in a DCR transformation.",
    ),
}


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
