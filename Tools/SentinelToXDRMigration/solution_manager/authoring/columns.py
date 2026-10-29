from __future__ import annotations

import re

_IDENTIFIER = r"[A-Za-z_][A-Za-z0-9_]*"
_ASSIGNING_OPERATORS = (
    "distinct",
    "extend",
    "mv-apply",
    "mv-expand",
    "summarize",
    "project",
    "project-rename",
    "project-keep",
    "parse",
    "parse-where",
)


def _strip_comments(query: str) -> str:
    return re.sub(r"//[^\n]*", "", query)


def _split_top_level(value: str) -> list[str]:
    parts: list[str] = []
    buffer: list[str] = []
    depth = 0
    quote: str | None = None
    escaped = False
    for character in value:
        if quote:
            buffer.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
            buffer.append(character)
        elif character in "([{":
            depth += 1
            buffer.append(character)
        elif character in ")]}":
            depth = max(0, depth - 1)
            buffer.append(character)
        elif character == "," and depth == 0:
            if "".join(buffer).strip():
                parts.append("".join(buffer).strip())
            buffer = []
        else:
            buffer.append(character)
    if "".join(buffer).strip():
        parts.append("".join(buffer).strip())
    return parts


def has_output_projection(query: str) -> bool:
    return bool(
        re.search(
            r"\|\s*(?:project(?!-away)\b|project-(?:keep|rename|reorder)\b|summarize\b|distinct\b|make-series\b)",
            _strip_comments(query),
            re.IGNORECASE,
        )
    )


def projected_columns(query: str) -> set[str] | None:
    """Return an intentionally permissive approximation of final output columns.

    None means the query does not constrain its output, so source-table columns
    must not be rejected merely because they are not explicitly named.
    """
    cleaned = _strip_comments(query)
    if not has_output_projection(cleaned):
        return None

    columns: set[str] = set()
    operators = "|".join(re.escape(value) for value in _ASSIGNING_OPERATORS)
    for match in re.finditer(rf"\|\s*({operators})\b([^|]*)", cleaned, re.IGNORECASE):
        operator = match.group(1).lower()
        operand = match.group(2)
        segments = re.split(r"\bby\b", operand, maxsplit=1, flags=re.IGNORECASE)
        if operator not in {"summarize"}:
            segments = [operand]
        for segment in segments:
            if operator in {"parse", "parse-where"}:
                columns.update(
                    found.group(1)
                    for found in re.finditer(
                        rf"\b({_IDENTIFIER})\s*:\s*(?:string|int|long|real|datetime|bool|guid|dynamic|decimal|timespan)\b",
                        segment,
                        re.IGNORECASE,
                    )
                )
                continue
            for item in _split_top_level(segment):
                assignment = re.match(rf"^\s*({_IDENTIFIER})\s*=(?!=)", item)
                if assignment:
                    columns.add(assignment.group(1))
                elif re.fullmatch(rf"\s*{_IDENTIFIER}\s*", item):
                    columns.add(item.strip())
    return columns
