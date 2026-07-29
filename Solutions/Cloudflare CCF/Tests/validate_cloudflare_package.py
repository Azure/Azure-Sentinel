#!/usr/bin/env python3
"""Targeted source/package checks for the Cloudflare CCF reference proposal."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


SOLUTION_RELATIVE = Path("Solutions/Cloudflare CCF")
CONNECTOR_RELATIVE = Path(
    "Data Connectors/CloudflareLog_CCF/CloudflareLog_ConnectorDefinition.json"
)
POLLER_RELATIVE = Path(
    "Data Connectors/CloudflareLog_CCF/CloudflareLog_PollerConfig.json"
)
DCR_RELATIVE = Path("Data Connectors/CloudflareLog_CCF/CloudflareLog_DCR.json")
TABLE_RELATIVE = Path("Data Connectors/CloudflareLog_CCF/CloudflareLog_Table.json")
PACKAGE_RELATIVE = Path("Package/mainTemplate.json")
SEAN_REF = "refs/remotes/seanstark/seanstark-cloudflare"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def find_connection_template(package: dict[str, Any]) -> dict[str, Any]:
    for resource in package.get("resources", []):
        properties = resource.get("properties", {})
        if "Connections" in str(properties.get("contentId", "")):
            return properties["mainTemplate"]
    raise AssertionError("Connections content template was not generated")


def find_definition_resource(package: dict[str, Any]) -> dict[str, Any]:
    for resource in walk(package):
        if (
            isinstance(resource, dict)
            and resource.get("type")
            == "Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions"
        ):
            return resource
    raise AssertionError("Packaged data connector definition was not found")


def first_resource(resources: list[dict[str, Any]], resource_type: str) -> dict[str, Any]:
    for resource in resources:
        if resource.get("type") == resource_type:
            return resource
    raise AssertionError(f"Required resource type was not generated: {resource_type}")


def projected_columns(transform: str) -> list[str]:
    marker = "| project "
    if marker not in transform:
        raise AssertionError("DCR transform does not contain a final project operator")
    return [column.strip() for column in transform.rsplit(marker, 1)[1].split(",")]


def git_show_json(repo_root: Path, ref: str, relative_path: Path) -> Any | None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{relative_path.as_posix()}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def validate(repo_root: Path) -> list[str]:
    solution = repo_root / SOLUTION_RELATIVE
    connector_definition = load_json(solution / CONNECTOR_RELATIVE)
    poller = load_json(solution / POLLER_RELATIVE)[0]
    dcr = load_json(solution / DCR_RELATIVE)[0]
    table = load_json(solution / TABLE_RELATIVE)
    package = load_json(solution / PACKAGE_RELATIVE)
    messages: list[str] = []

    deployment_config = poller.get("connectionDeployment", {})
    assert deployment_config.get("mode") == "PerInstance"
    assert poller.get("UseRandomGuid") is False
    assert "newGuid" not in json.dumps(poller)
    messages.append("PASS source opts into deterministic per-instance packaging")

    account_columns = {"CloudflareAccountId", "CloudflareAccountName"}
    table_columns = {
        column["name"] for column in table["properties"]["schema"]["columns"]
    }
    stream_columns = {
        column["name"]
        for column in dcr["properties"]["streamDeclarations"]["Custom-Cloudflare"][
            "columns"
        ]
    }
    transform = dcr["properties"]["dataFlows"][0]["transformKql"]
    project_columns = set(projected_columns(transform))
    assert account_columns <= table_columns
    assert account_columns <= stream_columns
    assert account_columns <= project_columns
    assert table_columns == project_columns, (
        f"DCR/table mismatch. Missing from project: {sorted(table_columns - project_columns)}; "
        f"not in table: {sorted(project_columns - table_columns)}"
    )
    assert "NELType = Type" in transform
    assert "LogType =" not in transform
    messages.append("PASS DCR projection exactly matches the shared table and preserves NELType")

    source_instructions = connector_definition["properties"]["connectorUiConfig"][
        "instructionSteps"
    ]
    source_instruction_types = {
        value.get("type")
        for value in walk(source_instructions)
        if isinstance(value, dict) and "type" in value
    }
    assert {"DataConnectorsGrid", "ContextPane"} <= source_instruction_types
    grid = next(
        value
        for value in walk(source_instructions)
        if isinstance(value, dict) and value.get("type") == "DataConnectorsGrid"
    )
    mappings = {
        item["columnName"]: item["columnValue"]
        for item in grid["parameters"]["mapping"]
    }
    assert mappings["Queue URI"] == "properties.request.QueueUri"
    assert "menuItems" not in grid["parameters"]
    messages.append("PASS source grid uses QueueUri casing and does not imply full deletion")

    connection_template = find_connection_template(package)
    serialized_connection = json.dumps(connection_template, separators=(",", ":"))
    assert "newGuid" not in serialized_connection
    assert "guidValue" not in connection_template.get("parameters", {})
    assert "dcrConfig" not in connection_template.get("parameters", {})

    identity_expression = connection_template["variables"]["instanceKey"]
    for parameter_name in deployment_config["identityParameters"]:
        assert f"parameters('{parameter_name}')" in identity_expression
        assert f"toLower(trim(parameters('{parameter_name}')))" in identity_expression
    assert "workspaceResourceId" in identity_expression

    deterministic_variables = {
        "connectorName",
        "dceName",
        "dcrName",
        "diagnosticSettingName",
        "queueName",
        "dlqName",
        "eventGridSubscriptionName",
        "storageNestedDeploymentName",
        "rbacPropagationScriptName",
    }
    for variable_name in deterministic_variables:
        assert "instanceKey" in connection_template["variables"][variable_name]

    queue_prefix = deployment_config["queuePrefix"]
    assert re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,14})[a-z0-9]", queue_prefix)
    maximum_queue_length = len(queue_prefix) + 1 + 13 + len("-notification")
    assert 3 <= maximum_queue_length <= 63
    messages.append("PASS full immutable identity drives collision-safe Azure resource names")

    allowed_parameter_types = {"securestring", "object", "array"}
    for parameter_name, parameter in connection_template["parameters"].items():
        assert parameter["type"] in allowed_parameter_types, (
            f"{parameter_name} uses unsupported connector-template type "
            f"{parameter['type']}"
        )
    context_textboxes = [
        value
        for value in walk(source_instructions)
        if isinstance(value, dict) and value.get("type") == "Textbox"
    ]
    assert all(
        textbox["parameters"].get("type") != "password"
        for textbox in context_textboxes
    )
    assert set(poller["properties"]["addOnAttributes"]) == account_columns
    messages.append("PASS no actual secret field enters resource identity or enrichment")

    resources = connection_template["resources"]
    required_resource_types = {
        "Microsoft.OperationalInsights/workspaces/tables",
        "Microsoft.Insights/dataCollectionEndpoints",
        "Microsoft.Insights/dataCollectionRules",
        "Microsoft.Insights/diagnosticSettings",
        "Microsoft.Resources/deployments",
        "Microsoft.Resources/deploymentScripts",
        "Microsoft.OperationalInsights/workspaces/providers/dataConnectors",
    }
    generated_types = {resource.get("type") for resource in resources}
    assert required_resource_types <= generated_types

    connector = first_resource(
        resources,
        "Microsoft.OperationalInsights/workspaces/providers/dataConnectors",
    )
    assert connector["properties"]["addOnAttributes"] == {
        "CloudflareAccountId": "[[parameters('CloudflareAccountId')]",
        "CloudflareAccountName": "[[parameters('CloudflareAccountName')]",
    }
    assert "QueueUri" in connector["properties"]["request"]
    assert "queueUri" not in connector["properties"]["request"]
    assert "dceResourceId" in connector["properties"]["dcrConfig"][
        "dataCollectionEndpoint"
    ]
    assert "dcrResourceId" in connector["properties"]["dcrConfig"][
        "dataCollectionRuleImmutableId"
    ]

    packaged_dcr = first_resource(resources, "Microsoft.Insights/dataCollectionRules")
    packaged_transform = packaged_dcr["properties"]["dataFlows"][0]["transformKql"]
    assert account_columns <= set(projected_columns(packaged_transform))
    assert "NELType = Type" in packaged_transform

    diagnostics = first_resource(resources, "Microsoft.Insights/diagnosticSettings")
    assert diagnostics["properties"]["workspaceId"] == "[[variables('workspaceResourceId')]"
    assert {"category": "LogErrors", "enabled": True} in diagnostics["properties"]["logs"]
    messages.append("PASS package preserves per-instance DCR/DCE, provenance, and LogErrors")

    forbidden_role = "17d1049b-9a84-46fb-8f53-869881c3d3ab"
    assert forbidden_role not in serialized_connection
    assert "Microsoft.ManagedIdentity/userAssignedIdentities" not in serialized_connection
    assert "managementPolicies" not in serialized_connection
    assert "BlobDeleteRetentionDays" not in serialized_connection
    messages.append("PASS unsafe lifecycle automation and Storage Account Contributor are absent")

    packaged_definition = find_definition_resource(package)
    packaged_instruction_types = {
        value.get("type")
        for value in walk(
            packaged_definition["properties"]["connectorUiConfig"]["instructionSteps"]
        )
        if isinstance(value, dict) and "type" in value
    }
    assert {"DataConnectorsGrid", "ContextPane"} <= packaged_instruction_types
    messages.append("PASS V3 package preserves the grid and nested context pane")

    sean_package = git_show_json(
        repo_root, SEAN_REF, SOLUTION_RELATIVE / PACKAGE_RELATIVE
    )
    if sean_package is None:
        messages.append(
            "SKIP Sean structural comparison (refs/remotes/seanstark/seanstark-cloudflare is unavailable)"
        )
    else:
        sean_connection = find_connection_template(sean_package)
        sean_types = {resource.get("type") for resource in sean_connection["resources"]}
        structural_features = {
            "Microsoft.OperationalInsights/workspaces/tables",
            "Microsoft.Insights/dataCollectionEndpoints",
            "Microsoft.Insights/dataCollectionRules",
            "Microsoft.Insights/diagnosticSettings",
            "Microsoft.Resources/deployments",
            "Microsoft.Resources/deploymentScripts",
            "Microsoft.OperationalInsights/workspaces/providers/dataConnectors",
        }
        assert structural_features <= sean_types
        assert structural_features <= generated_types
        messages.append(
            "PASS hardened package retains Sean's phase-one multi-instance resource topology"
        )

    # Regression guard for the packaging defect that broke lab deployments: the
    # storage-side nested deployment targets the storage account's own
    # subscription/resource group, so it MUST evaluate expressions with inner
    # scope. Under the ARM default (outer) scope every resourceId() below is
    # resolved against the parent deployment's resource group, and ARM rejects
    # the deployment with "The resource '.../queues/<name>' is not defined in
    # the template."
    nested = first_resource(connection_template["resources"], "Microsoft.Resources/deployments")
    assert nested.get("subscriptionId") and nested.get("resourceGroup"), (
        "storage nested deployment must target the storage account scope"
    )
    scope = nested["properties"].get("expressionEvaluationOptions", {}).get("scope")
    assert scope == "inner", (
        "storage nested deployment must set expressionEvaluationOptions.scope='inner'; "
        f"found {scope!r}. Outer scope resolves resourceId() against the parent resource "
        "group and breaks cross-resource-group deployment."
    )

    inner_template = nested["properties"]["template"]
    declared = set(inner_template.get("parameters", {}))
    passed = set(nested["properties"].get("parameters", {}))
    assert declared == passed, (
        f"inner template parameters {sorted(declared)} must match the values passed in {sorted(passed)}"
    )

    referenced: set[str] = set()
    for value in walk(inner_template["resources"]):
        if isinstance(value, str):
            assert "variables(" not in value, (
                f"inner-scope nested template cannot read parent variables: {value}"
            )
            referenced.update(re.findall(r"parameters\('([^']+)'\)", value))
    assert referenced <= declared, (
        f"inner template uses undeclared parameters: {sorted(referenced - declared)}"
    )
    messages.append(
        "PASS storage nested deployment is inner-scoped and self-contained"
    )

    return messages


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    try:
        messages = validate(repo_root)
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1

    for message in messages:
        print(message)
    print(f"PASS {len([message for message in messages if message.startswith('PASS')])} targeted checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
