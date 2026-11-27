#!/usr/bin/env python3
"""Build a CCF Push package for workspaces that already have six compatible tables."""

import argparse
import json
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile


TABLE_RESOURCE = "Microsoft.OperationalInsights/workspaces/tables"
DCR_RESOURCE = "Microsoft.Insights/dataCollectionRules"
V2_TABLES = {
    f"ABNORMAL_SECURITY_{event}_CL": f"ABNORMAL_SECURITY_{event}_V2_CL"
    for event in ("ABUSE_MAILBOX", "POSTURE_CHANGE", "LOGS")
}
REUSED_TABLES = {
    f"ABNORMAL_SECURITY_{event}_CL"
    for event in ("THREAT_LOG", "AUDIT_LOG", "CASE", "ATO_CASE", "VENDOR_CASE", "REMEDIATION")
}
TABLE_NAMES = re.compile(r"(?<![\w])(?:" + "|".join(V2_TABLES) + r")(?![\w])")


def rename_table_references(value):
    """Update table names in ARM resource fields and embedded Sentinel queries."""
    if isinstance(value, dict):
        return {key: rename_table_references(item) for key, item in value.items()}
    if isinstance(value, list):
        return [rename_table_references(item) for item in value]
    if isinstance(value, str):
        return TABLE_NAMES.sub(lambda match: V2_TABLES[match[0]], value)
    return value


def build_template(template, version):
    resources = [
        resource["properties"]["mainTemplate"]["resources"]
        for resource in template["resources"]
        if any(
            entry["type"] == DCR_RESOURCE and entry["name"] == "AbnormalSecurityPushDCR"
            for entry in resource.get("properties", {}).get("mainTemplate", {}).get("resources", [])
        )
    ]
    if len(resources) != 1:
        raise ValueError("Expected one AbnormalSecurityPushDCR connector template")

    connector_resources = resources[0]
    table_names = [
        entry["name"] for entry in connector_resources if entry["type"] == TABLE_RESOURCE
    ]
    expected_tables = set(V2_TABLES) | REUSED_TABLES
    if len(table_names) != len(expected_tables) or set(table_names) != expected_tables:
        raise ValueError("The original Push template must define the nine expected tables")

    dcr = next(
        entry for entry in connector_resources
        if entry["type"] == DCR_RESOURCE and entry["name"] == "AbnormalSecurityPushDCR"
    )
    outputs = [flow["outputStream"] for flow in dcr["properties"]["dataFlows"]]
    if len(outputs) != len(expected_tables) or set(outputs) != {
        f"Custom-{name}" for name in expected_tables
    }:
        raise ValueError("The original Push DCR must route to the nine expected tables")

    for version_key in ("_solutionVersion", "dataConnectorCCPVersion"):
        current_version = template["variables"][version_key]
        if tuple(map(int, version.split("."))) <= tuple(map(int, current_version.split("."))):
            raise ValueError(f"Package version must be higher than {current_version}")
        template["variables"][version_key] = version

    connector_resources[:] = [
        entry for entry in connector_resources
        if entry["type"] != TABLE_RESOURCE or entry["name"] not in REUSED_TABLES
    ]
    return rename_table_references(template)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "Package")
    parser.add_argument("--version", required=True, help="A package version greater than the source version")
    parser.add_argument("--output", type=Path, required=True, help="Path to the new ARM package ZIP")
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        parser.error("--version must have the form MAJOR.MINOR.PATCH")

    try:
        template = json.loads((args.source / "mainTemplate.json").read_text(encoding="utf-8-sig"))
        ui_definition = (args.source / "createUiDefinition.json").read_bytes()
        json.loads(ui_definition)
        template = build_template(template, args.version)
        with ZipFile(args.output, mode="x", compression=ZIP_DEFLATED) as package:
            package.writestr("mainTemplate.json", json.dumps(template, indent=2) + "\n")
            package.writestr("createUiDefinition.json", ui_definition)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Could not build the selective Push package: {exc}\n")

    print(args.output)


if __name__ == "__main__":
    main()
