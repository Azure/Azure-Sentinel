import csv
import re
from pathlib import Path

ADDITIONAL_UNION_PARSERS = {
    "ProcessEvent": (
        "ASimProcessEventCreate.yaml",
        "ASimProcessEventTerminate.yaml",
        "imProcessCreate.yaml",
        "imProcessTerminate.yaml",
    )
}

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
    legacy_path = sample_data_dir / f"{prefix}_IngestedLogs.csv"
    candidates = [
        (sample_data_dir / f"{prefix}_{table}_IngestedLogs.csv", table)
        for table in sorted(source_tables)
        if (sample_data_dir / f"{prefix}_{table}_IngestedLogs.csv").is_file()
    ]
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
