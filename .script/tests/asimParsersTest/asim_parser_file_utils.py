import csv
import json
import re
import sys
from pathlib import Path

ADDITIONAL_UNION_PARSERS = {
    "ProcessEvent": (
        "ASimProcessEventCreate.yaml",
        "ASimProcessEventTerminate.yaml",
        "imProcessCreate.yaml",
        "imProcessTerminate.yaml",
    )
}
FIXTURE_NAME_COMPONENT_RE = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9 _-]{0,126}[A-Za-z0-9])?$"
)
SCHEMA_NAME_COMPONENT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{0,63}$")


def _validate_fixture_component(value, label, pattern):
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f"{label} is not safe for sample fixture lookup")
    return value


def _resolve_contained_path(root, filename):
    candidate = root / filename
    resolved_root = root.resolve()
    resolved_candidate = candidate.resolve()
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(
            "Resolved sample fixture path is outside the ASIM sample directory"
        ) from error
    return candidate


KQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
KQL_SCHEMA_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
KQL_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
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
IGNORED_KQL_TOKENS_RE = re.compile(
    r"//[^\r\n]*|/\*.*?\*/|```.*?```"
    r"|@'(?:''|[^'])*'"
    r'|@"(?:""|[^"])*"'
    r"|'(?:\\.|''|[^'\\])*'"
    r'|"(?:\\.|""|[^"\\])*"',
    flags=re.DOTALL,
)
UNTRUSTED_KQL_RULES = (
    ("workspace", re.compile(r"\bworkspace\s*\(", re.IGNORECASE)),
    ("cluster", re.compile(r"\bcluster\s*\(", re.IGNORECASE)),
    ("database", re.compile(r"\bdatabase\s*\(", re.IGNORECASE)),
    ("externaldata", re.compile(r"\bexternaldata\s*\(", re.IGNORECASE)),
    ("external_table", re.compile(r"\bexternal_table\s*\(", re.IGNORECASE)),
    ("evaluate", re.compile(r"\bevaluate\b", re.IGNORECASE)),
    (
        "management command",
        re.compile(r"(?:^|;)\s*\.[A-Za-z]", re.MULTILINE),
    ),
)


def _mask_kql_non_code(query):
    return IGNORED_KQL_TOKENS_RE.sub(
        lambda match: re.sub(r"[^\r\n]", " ", match.group()),
        query,
    )


def validate_untrusted_kql(query, field="ParserQuery"):
    if not isinstance(query, str) or not query.strip():
        raise ValueError(f"{field} must be a non-empty string")
    masked_query = _mask_kql_non_code(query)
    for construct, pattern in UNTRUSTED_KQL_RULES:
        if pattern.search(masked_query):
            raise ValueError(
                f"{field} contains disallowed KQL construct "
                f"{construct!r}"
            )


def _validate_query_time_parameters(parser_params):
    if not isinstance(parser_params, list):
        raise ValueError("ParserParams must be an array")
    seen_names = set()
    for index, parameter in enumerate(parser_params):
        field = f"ParserParams[{index}]"
        if not isinstance(parameter, dict):
            raise ValueError(f"{field} must be an object")
        name = parameter.get("Name")
        parameter_type = parameter.get("Type")
        if (
            not isinstance(name, str)
            or not KQL_IDENTIFIER_RE.fullmatch(name)
        ):
            raise ValueError(f"{field}.Name must be a KQL identifier")
        normalized_name = name.casefold()
        if normalized_name in seen_names:
            raise ValueError(f"{field}.Name must be unique")
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
            raise ValueError(f"{field}.Type is not supported")
        if "Default" not in parameter:
            raise ValueError(f"{field}.Default is required")
        default = parameter["Default"]
        if normalized_type in {"bool", "boolean"}:
            valid_default = isinstance(default, bool)
        elif normalized_type == "string":
            valid_default = isinstance(default, str)
        elif normalized_type == "dynamic":
            valid_default = default == "dynamic([])"
        elif normalized_type == "datetime":
            valid_default = default == "datetime(null)"
        else:
            valid_default = (
                not isinstance(default, bool)
                and isinstance(default, (int, float))
            ) or default == f"{normalized_type}(null)"
        if not valid_default:
            raise ValueError(
                f"{field}.Default is invalid for type {normalized_type}"
            )


def validate_query_time_parser_document(document, source="query-time parser"):
    if not isinstance(document, dict):
        raise ValueError(f"{source} must contain an object")
    validate_untrusted_kql(document.get("ParserQuery"), "ParserQuery")
    normalization = document.get("Normalization")
    schema = (
        normalization.get("Schema")
        if isinstance(normalization, dict)
        else None
    )
    if not isinstance(schema, str) or not KQL_SCHEMA_RE.fullmatch(schema):
        raise ValueError(
            "Normalization.Schema must be a KQL identifier"
        )
    for field in ("ParserName", "EquivalentBuiltInParser"):
        value = document.get(field)
        if (
            not isinstance(value, str)
            or not KQL_IDENTIFIER_RE.fullmatch(value)
        ):
            raise ValueError(f"{field} must be a KQL identifier")
    parser = document.get("Parser")
    version = parser.get("Version") if isinstance(parser, dict) else None
    if not isinstance(version, str) or not KQL_VERSION_RE.fullmatch(version):
        raise ValueError("Parser.Version must use X.X.X format")
    _validate_query_time_parameters(document.get("ParserParams"))


def _main(arguments):
    if len(arguments) != 2 or arguments[0] != "validate-query-document":
        print(
            "Usage: asim_parser_file_utils.py "
            "validate-query-document <json-file>",
            file=sys.stderr,
        )
        return 2
    try:
        path = Path(arguments[1])
        document = json.loads(path.read_text(encoding="utf-8"))
        validate_query_time_parser_document(document, str(path))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1
    return 0

def extract_schema_name(parser_path):
    match = re.search(r'ASim(\w+)[/\\]', parser_path)
    return match.group(1) if match else None

def is_union_parser(parser_filename, schema_name):
    if not schema_name:
        return False

    return (
        parser_filename in (f'ASim{schema_name}.yaml', f'im{schema_name}.yaml')
        or parser_filename in ADDITIONAL_UNION_PARSERS.get(schema_name, ())
    )

def is_empty_parser(parser_filename):
    return parser_filename.startswith('vim') and parser_filename.endswith('Empty.yaml')

def filter_query_time_parser_files(modified_files):
    return [
        path for path in modified_files
        if path.endswith('.yaml')
        and 'IngestTimeParsers' not in path.replace('\\', '/').split('/')
    ]

def resolve_sample_data_path(sample_data_dir, event_vendor, event_product, schema, parser_query):
    """Keep matching legacy data; use source-specific data for target collisions."""
    event_vendor = _validate_fixture_component(
        event_vendor, "EventVendor", FIXTURE_NAME_COMPONENT_RE
    )
    event_product = _validate_fixture_component(
        event_product, "EventProduct", FIXTURE_NAME_COMPONENT_RE
    )
    schema = _validate_fixture_component(
        schema, "Normalization.Schema", SCHEMA_NAME_COMPONENT_RE
    )
    ignored_tokens = (
        r"//[^\r\n]*|/\*.*?\*/|```.*?```"
        r"|@'(?:''|[^'])*'"
        r'|@"(?:""|[^"])*"'
        r"|'(?:\\.|''|[^'\\])*'"
        r'|"(?:\\.|""|[^"\\])*"'
    )
    masked_query = re.sub(
        ignored_tokens,
        lambda match: re.sub(r"[^\r\n]", " ", match.group()),
        parser_query,
        flags=re.DOTALL,
    )
    source_tables = set(re.findall(
        r"(?:^|[({=;])\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?=\|)",
        masked_query,
        flags=re.MULTILINE,
    ))
    unions = list(re.finditer(r"\bunion\b", masked_query, flags=re.IGNORECASE))
    resolved_unions = list(re.finditer(
        r"\bunion(?:\s+(?:kind|isfuzzy|withsource)\s*=\s*[A-Za-z0-9_]+)*\s+"
        r"([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)"
        r"\s*(?=\||;|\)|\Z)",
        masked_query,
        flags=re.IGNORECASE,
    ))
    for union in resolved_unions:
        source_tables.update(table.strip() for table in union.group(1).split(","))

    sample_data_dir = Path(sample_data_dir)
    prefix = f"{event_vendor}_{event_product}_{schema}"
    legacy_path = _resolve_contained_path(
        sample_data_dir, f"{prefix}_IngestedLogs.csv"
    )
    candidates = []
    for table in sorted(source_tables):
        source_path = _resolve_contained_path(
            sample_data_dir,
            f"{prefix}_{table}_IngestedLogs.csv",
        )
        if source_path.is_file():
            candidates.append((source_path, table))
    # A matching legacy fixture remains authoritative for version-aware unions.
    if candidates and legacy_path.is_file():
        with legacy_path.open(newline="", encoding="utf-8-sig") as legacy_file:
            legacy_types = {row.get("Type") for row in csv.DictReader(legacy_file)}
        if any(legacy_types == {table} for _, table in candidates):
            return legacy_path
    if len(candidates) > 1:
        raise ValueError(
            f"Multiple source-specific sample fixtures match the parser: "
            f"{[path.name for path, _ in candidates]}"
        )
    if len(unions) != len(resolved_unions):
        source_fixture_pattern = re.compile(
            rf"{re.escape(prefix)}_[A-Za-z_][A-Za-z0-9_]*_IngestedLogs\.csv"
        )
        if any(
            path.is_file() and source_fixture_pattern.fullmatch(path.name)
            for path in sample_data_dir.iterdir()
        ):
            raise ValueError(
                "Cannot resolve union source tables safely for source-specific "
                "sample selection"
            )
    if candidates:
        sample_path, source_table = candidates[0]
        with sample_path.open(newline="", encoding="utf-8-sig") as sample_file:
            fixture_types = {row.get("Type") for row in csv.DictReader(sample_file)}
        if fixture_types != {source_table}:
            raise ValueError(
                f"Source-specific sample fixture {sample_path} must contain "
                f"only Type={source_table!r}; found {fixture_types!r}"
            )
        return sample_path

    if not legacy_path.is_file():
        raise FileNotFoundError(
            f"No matching source-specific sample fixture or legacy fixture {legacy_path}"
        )
    return legacy_path


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
