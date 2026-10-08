#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    raise SystemExit("PyYAML is required. Install it with 'python -m pip install PyYAML'.")


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REPOSITORY_ROOT = SCRIPT_DIR.parents[2]


class ValidationError(Exception):
    pass


def format_default(value: Any, parameter_type: str) -> str:
    if parameter_type == "string":
        return f"'{str(value).replace(chr(39), chr(39) * 2)}'"
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return "null"
    return str(value)


def build_function_parameters(
    parser_path: Path, allow_missing: bool = False
) -> str | None:
    try:
        parser = yaml.safe_load(parser_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ValidationError(f"Cannot read {parser_path}: {error}") from error

    if not isinstance(parser, dict):
        raise ValidationError(f"{parser_path} must contain a YAML mapping.")

    parameters = parser.get("ParserParams")
    if parameters is None and allow_missing:
        return None
    if not isinstance(parameters, list) or not parameters:
        raise ValidationError(f"{parser_path} does not define a non-empty ParserParams list.")

    formatted_parameters = []
    for index, parameter in enumerate(parameters, start=1):
        if not isinstance(parameter, dict):
            raise ValidationError(f"ParserParams item {index} in {parser_path} must be a mapping.")

        name = parameter.get("Name")
        parameter_type = parameter.get("Type")
        if not isinstance(name, str) or not isinstance(parameter_type, str):
            raise ValidationError(
                f"ParserParams item {index} in {parser_path} must have string Name and Type values."
            )

        if parameter_type.startswith("table:"):
            formatted_parameters.append(f"{name}:{parameter_type.split(':', 1)[1]}")
        elif "Default" in parameter:
            default = format_default(parameter["Default"], parameter_type)
            formatted_parameters.append(f"{name}:{parameter_type}={default}")
        else:
            formatted_parameters.append(f"{name}:{parameter_type}")

    return ",".join(formatted_parameters)


def find_saved_search(template: dict[str, Any], template_path: Path) -> dict[str, Any]:
    saved_searches = []

    def visit(resources: Any) -> None:
        if not isinstance(resources, list):
            return
        for resource in resources:
            if not isinstance(resource, dict):
                continue
            if resource.get("type") == "savedSearches":
                saved_searches.append(resource)
            visit(resource.get("resources"))

    visit(template.get("resources"))
    if len(saved_searches) != 1:
        raise ValidationError(
            f"{template_path} must contain exactly one savedSearches resource; "
            f"found {len(saved_searches)}."
        )
    return saved_searches[0]


def load_template(
    template_path: Path, schema: str, template_prefix: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        template = json.loads(template_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"Cannot read {template_path}: {error}") from error

    if not isinstance(template, dict):
        raise ValidationError(f"{template_path} must contain a JSON object.")

    saved_search = find_saved_search(template, template_path)
    expected_name = f"{template_prefix}_{schema}Custom"
    if saved_search.get("name") != expected_name:
        raise ValidationError(
            f"{template_path} has saved search name {saved_search.get('name')!r}; "
            f"expected {expected_name!r}."
        )

    properties = saved_search.get("properties")
    if not isinstance(properties, dict):
        raise ValidationError(
            f"The savedSearches resource in {template_path} does not define properties."
        )
    return template, properties


def write_template(template_path: Path, template: dict[str, Any]) -> None:
    original = template_path.read_bytes()
    newline = "\r\n" if b"\r\n" in original else "\n"
    content = json.dumps(template, indent=2, ensure_ascii=False) + "\n"
    template_path.write_text(content.replace("\n", newline), encoding="utf-8", newline="")


def discover_schemas(template_directory: Path) -> list[str]:
    suffix = "Custom.json"
    schemas = set()
    for prefix in ("Im_", "ASim_"):
        for template_path in template_directory.glob(f"{prefix}*{suffix}"):
            schemas.add(template_path.name[len(prefix) : -len(suffix)])
    return sorted(schemas, key=str.casefold)


def process_template(
    repository_root: Path, schema: str, template_prefix: str, update: bool
) -> bool:
    template_path = (
        repository_root
        / "ASIM"
        / "deploy"
        / "EmptyCustomUnifyingParsers"
        / f"{template_prefix}_{schema}Custom.json"
    )
    parser_name = f"im{schema}" if template_prefix == "Im" else f"ASim{schema}"
    parser_path = (
        repository_root
        / "Parsers"
        / f"ASim{schema}"
        / "Parsers"
        / f"{parser_name}.yaml"
    )

    # TODO: Generate the required templates when a new schema is added or files are missing.
    if not template_path.is_file():
        raise ValidationError(f"Template not found: {template_path}")
    if not parser_path.is_file():
        raise ValidationError(f"Canonical parser not found: {parser_path}")

    expected = build_function_parameters(
        parser_path, allow_missing=template_prefix == "ASim"
    )
    template, properties = load_template(template_path, schema, template_prefix)
    actual = properties.get("functionParameters")
    if actual is not None and not isinstance(actual, str):
        raise ValidationError(f"functionParameters in {template_path} must be a string.")

    if actual == expected:
        print(f"OK      {template_prefix}_{schema}Custom")
        return True

    if update:
        if expected is None:
            properties.pop("functionParameters", None)
        else:
            properties["functionParameters"] = expected
        write_template(template_path, template)
        print(f"UPDATED {template_prefix}_{schema}Custom")
        return True

    print(f"MISMATCH {template_prefix}_{schema}Custom")
    print(f"  actual:   {actual}")
    print(f"  expected: {expected}")
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the functionParameters in ASIM empty custom unifying parser ARM "
            "templates against their canonical parser YAML files."
        )
    )
    parser.add_argument(
        "schemas",
        nargs="*",
        metavar="SCHEMA",
        help="ASIM schema names to process (for example, WebSession). Defaults to all templates.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update mismatched templates instead of only reporting them.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=DEFAULT_REPOSITORY_ROOT,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repository_root = args.repository_root.resolve()
    template_directory = (
        repository_root / "ASIM" / "deploy" / "EmptyCustomUnifyingParsers"
    )
    schemas = args.schemas or discover_schemas(template_directory)
    if not schemas:
        print(
            f"No Im_*Custom.json or ASim_*Custom.json templates found in "
            f"{template_directory}.",
            file=sys.stderr,
        )
        return 2

    all_match = True
    had_error = False
    for schema in schemas:
        for template_prefix in ("Im", "ASim"):
            try:
                all_match = (
                    process_template(
                        repository_root, schema, template_prefix, args.update
                    )
                    and all_match
                )
            except ValidationError as error:
                had_error = True
                print(
                    f"ERROR   {template_prefix}_{schema}Custom: {error}",
                    file=sys.stderr,
                )

    if had_error:
        return 2
    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())
