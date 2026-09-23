import csv
import io
from typing import Any


def parse_csv(
    csv_text: str,
) -> list[dict[str, Any]]:

    reader = csv.DictReader(
        io.StringIO(csv_text)
    )

    # Strip whitespace from header names too. Values were already
    # stripped below, but a header like " domain" (leading/trailing
    # whitespace) would silently fail every `record.get("domain")`
    # lookup downstream in the normalizer, producing null fields
    # with no error raised anywhere.
    if reader.fieldnames:
        reader.fieldnames = [
            name.strip() if isinstance(name, str) else name
            for name in reader.fieldnames
        ]

    records = []

    for row in reader:

        record = {
            (key.strip() if isinstance(key, str) else key): (
                value.strip() if isinstance(value, str) else value
            )
            for key, value in row.items()
            if key
        }

        records.append(record)

    return records


# Lines that indicate a header/metadata row rather than an actual
# domain, if the "without WHOIS" domain-list response ever includes
# one (that endpoint is not CSV, so there is no DictReader to skip a
# header for us).
_DOMAIN_LIST_HEADER_TOKENS = {"domain", "domain_name", "domains"}


def _looks_like_domain(line: str) -> bool:
    # A real domain always has at least one dot and no whitespace.
    # This is enough to reject a stray header/metadata line without
    # needing a full domain-syntax validator.
    return "." in line and " " not in line and "\t" not in line


def parse_domain_list(
    text: str,
) -> tuple[list[dict[str, str]], int]:
    """
    Parse a plain domain-list response.

    Returns:
        (records, raw_line_count) where raw_line_count is the number of
        non-empty lines received *before* header/invalid filtering.
        Callers must use raw_line_count for pagination offset and
        "last page" termination so filtering cannot cause silent data loss.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    raw_line_count = len(lines)

    if lines and lines[0].lower() in _DOMAIN_LIST_HEADER_TOKENS:
        lines = lines[1:]

    records = [
        {"domain_name": domain} for domain in lines if _looks_like_domain(domain)
    ]
    return records, raw_line_count
