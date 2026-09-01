import re

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
