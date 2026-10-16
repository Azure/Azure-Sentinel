from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest
import yaml

from azure_monitor_logs_ingestion.contract import load_contract
from azure_monitor_logs_ingestion import cli
from azure_monitor_logs_ingestion.cli import main
from azure_monitor_logs_ingestion.azure import AzureClient, Workspace
from azure_monitor_logs_ingestion.registry import (
    destination_schema_blockers,
    inspect_managed_resources,
    resolve_contract,
)


ROOT = Path(__file__).resolve().parents[1]


def common_security_log_contract():
    return load_contract(ROOT / "contracts" / "CommonSecurityLog.yaml")


def candidate_resources(contract, workspace_id="/workspace"):
    dce_id = "/dce"
    dce = {
        "tags": {
            "managed-by": "azure-monitor-logs-ingestion",
            "ingestion-contract": contract.name,
        },
        "properties": {"logsIngestion": {"endpoint": "https://example.ingest.azure.com"}},
    }
    dcr = {
        "kind": "Direct",
        "tags": {
            "managed-by": "azure-monitor-logs-ingestion",
            "ingestion-contract": contract.name,
        },
        "properties": {
            "dataCollectionEndpointId": dce_id,
            "streamDeclarations": {
                contract.input_stream: {
                    "columns": [column.as_dict() for column in contract.input_columns]
                }
            },
            "destinations": {
                "logAnalytics": [
                    {"name": "destination", "workspaceResourceId": workspace_id}
                ]
            },
            "dataFlows": [
                {
                    "streams": [contract.input_stream],
                    "destinations": ["destination"],
                    "transformKql": contract.transform_kql,
                    "outputStream": contract.destination.output_stream,
                }
            ],
        },
    }
    return dce_id, dce, dcr


def arm_table_document(*, standard=None, custom=None):
    schema = {}
    if standard is not None:
        schema["standardColumns"] = standard
    if custom is not None:
        schema["columns"] = custom
    return {"properties": {"schema": schema}}


def arm_columns(columns):
    return [
        {
            "name": column.name,
            "type": "dateTime" if column.type == "datetime" else column.type,
            "isHidden": False,
        }
        for column in columns
    ]


def test_common_security_log_resolves_supported_fields_and_stable_identity():
    forward = resolve_contract(
        "CommonSecurityLog",
        {
            "DeviceEventClassID": "string",
            "SourceIP": "string",
            "SentBytes": "long",
        },
    )
    reverse = resolve_contract(
        "commonsecuritylog",
        {
            "SentBytes": "long",
            "SourceIP": "string",
            "DeviceEventClassID": "string",
        },
    )

    assert forward["status"] == "provisioning-plan"
    assert forward["schemaFingerprint"] == reverse["schemaFingerprint"]
    assert forward["transformFingerprint"] == reverse["transformFingerprint"]
    assert forward["liveValidated"] is False
    assert forward["plan"]["writesPerformed"] is False
    assert forward["plan"]["requiresSeparateApproval"] is True


def test_transform_change_invalidates_only_transform_identity(tmp_path):
    contract_path = tmp_path / "contracts" / "CommonSecurityLog.yaml"
    contract_path.parent.mkdir()
    shutil.copyfile(ROOT / "contracts" / "CommonSecurityLog.yaml", contract_path)
    registry_value = yaml.safe_load((ROOT / "registry.yaml").read_text(encoding="utf-8"))
    registry_value["tables"] = [
        item
        for item in registry_value["tables"]
        if item["table"] == "CommonSecurityLog"
    ]
    (tmp_path / "registry.yaml").write_text(
        yaml.safe_dump(registry_value, sort_keys=False),
        encoding="utf-8",
    )
    before = resolve_contract("CommonSecurityLog", registry_path=tmp_path / "registry.yaml")

    contract_value = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    contract_value["transformKql"] += "\n| where isnotempty(DeviceName)"
    contract_path.write_text(
        yaml.safe_dump(contract_value, sort_keys=False),
        encoding="utf-8",
    )
    after = resolve_contract("CommonSecurityLog", registry_path=tmp_path / "registry.yaml")

    assert before["schemaFingerprint"] == after["schemaFingerprint"]
    assert before["transformFingerprint"] != after["transformFingerprint"]


def test_unknown_table_and_unregistered_field_are_blocked():
    assert resolve_contract("UnregisteredTable")["status"] == "blocked"

    result = resolve_contract("CommonSecurityLog", {"MadeUpField": "string"})

    assert result["status"] == "blocked"
    assert "MadeUpField" in result["blockers"][0]
    assert result["plan"] is None
    assert resolve_contract("CommonSecurityLog", {"TenantId": "guid"})["status"] == "blocked"


def test_registered_field_type_mismatch_is_blocked():
    result = resolve_contract("CommonSecurityLog", {"DestinationPort": "long"})

    assert result["status"] == "blocked"
    assert "not required type 'long'" in result["blockers"][0]


def test_existing_resources_are_reusable_only_when_exactly_compatible():
    contract = common_security_log_contract()
    dce_id, dce, dcr = candidate_resources(contract)

    result = inspect_managed_resources(
        contract, "/workspace", dce, dcr, dce_resource_id=dce_id
    )

    assert result["status"] == "compatible-existing"
    assert result["writesPerformed"] is False


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda dce, dcr: dcr["tags"].update({"managed-by": "unrelated"}),
            "not owned",
        ),
        (
            lambda dce, dcr: dcr["properties"]["dataFlows"][0].update(
                {"transformKql": "source"}
            ),
            "transform differs",
        ),
        (
            lambda dce, dcr: dcr["properties"]["destinations"]["logAnalytics"][0].update(
                {"workspaceResourceId": "/other-workspace"}
            ),
            "locked workspace",
        ),
        (
            lambda dce, dcr: dcr["properties"]["streamDeclarations"][
                "Custom-XDRMigrationCommonSecurityLogMock"
            ]["columns"].append({"name": "Extra", "type": "string"}),
            "input schema differs",
        ),
        (
            lambda dce, dcr: dcr["properties"].update(
                {"dataCollectionEndpointId": "/other-dce"}
            ),
            "contract-specific DCE",
        ),
    ],
)
def test_incompatible_existing_candidate_is_blocked_without_writes(mutate, message):
    contract = common_security_log_contract()
    dce_id, dce, dcr = candidate_resources(contract)
    mutate(dce, dcr)

    result = inspect_managed_resources(
        contract, "/workspace", dce, dcr, dce_resource_id=dce_id
    )

    assert result["status"] == "blocked"
    assert result["writesPerformed"] is False
    assert any(message in blocker for blocker in result["blockers"])


def test_ingest_resource_lookup_rejects_incompatible_dcr_before_any_write():
    contract = common_security_log_contract()
    dce_id, dce, dcr = candidate_resources(contract)
    dcr["properties"]["dataFlows"][0]["transformKql"] = "source"
    calls = []

    class Response:
        status_code = 200

        def __init__(self, value):
            self.value = value

        def json(self):
            return self.value

    class ReadOnlyClient(AzureClient):
        def __init__(self):
            self.table = {
                "properties": {
                    "schema": {
                        "standardColumns": arm_columns(contract.destination.columns)
                    }
                }
            }

        def resolve_workspace(self, identifier):
            return Workspace(
                id="/workspace",
                name="ws",
                subscription_id="sub",
                resource_group="rg",
                location="eastus",
                customer_id="customer",
            )

        def _resource_ids(self, workspace, contract_value):
            return dce_id, "/dcr"

        def _resource_url(self, resource_id, api_version):
            return resource_id

        def request(self, method, url, **kwargs):
            calls.append(method)
            if "/tables/" in url:
                return Response(self.table)
            if url == dce_id:
                return Response(dce)
            return Response(dcr)

    client = ReadOnlyClient()

    with pytest.raises(RuntimeError, match="refusing ingestion"):
        client.get_resources(contract)
    assert calls == ["GET", "GET", "GET"]


def test_unknown_or_ambiguous_partial_resource_state_is_not_reused():
    contract = common_security_log_contract()

    result = inspect_managed_resources(contract, "/workspace", {"tags": {}}, None)

    assert result["status"] == "blocked"
    assert "partial resource pair" in result["blockers"][0]


def test_destination_schema_requires_all_registered_columns_and_types():
    contract = common_security_log_contract()
    table = arm_table_document(
        custom=arm_columns(contract.destination.columns),
    )

    assert destination_schema_blockers(contract, table) == []
    table["properties"]["schema"]["columns"][0]["type"] = "string"

    assert any(
        "not contract type" in blocker
        for blocker in destination_schema_blockers(contract, table)
    )


def test_arm_standard_only_schema_satisfies_registered_destination():
    contract = common_security_log_contract()
    table = arm_table_document(
        standard=arm_columns(contract.destination.columns),
    )

    assert destination_schema_blockers(contract, table) == []


def test_arm_standard_and_custom_columns_are_merged():
    contract = common_security_log_contract()
    columns = arm_columns(contract.destination.columns)
    table = arm_table_document(
        standard=columns[::2],
        custom=columns[1::2],
    )

    assert destination_schema_blockers(contract, table) == []


@pytest.mark.parametrize(
    ("standard", "custom", "expected"),
    [
        (
            [{"name": "TimeGenerated", "type": "dateTime"}],
            [{"name": "timegenerated", "type": "dateTime"}],
            "appears more than once",
        ),
        (
            [{"name": "TimeGenerated", "type": "dateTime"}],
            [{"name": "timegenerated", "type": "string"}],
            "conflicting types",
        ),
    ],
)
def test_arm_schema_rejects_standard_custom_column_collisions(
    standard, custom, expected
):
    contract = common_security_log_contract()
    table = arm_table_document(
        standard=standard,
        custom=custom,
    )

    assert any(
        expected in blocker
        for blocker in destination_schema_blockers(contract, table)
    )


@pytest.mark.parametrize(
    ("table", "expected"),
    [
        ({}, "missing an object-valued properties"),
        ({"properties": {"schema": None}}, "missing an object-valued properties.schema"),
        ({"properties": {"schema": {"columns": None}}}, "columns must be an array"),
        (
            {"properties": {"schema": {"standardColumns": [{"name": "x"}]}}},
            "missing a non-empty column type",
        ),
        (
            {"properties": {"schema": {"standardColumns": [{"type": "string"}]}}},
            "missing a non-empty column name",
        ),
        (
            {"properties": {"schema": {"standardColumns": [{"name": "x", "type": "map"}]}}},
            "unsupported ARM column type",
        ),
        (
            {"properties": {"schema": {}}},
            "missing both standardColumns and columns",
        ),
    ],
)
def test_arm_schema_rejects_absent_or_malformed_metadata(table, expected):
    contract = common_security_log_contract()

    assert any(
        expected in blocker
        for blocker in destination_schema_blockers(contract, table)
    )


def test_existing_registered_templates_remain_loadable():
    for table in ("Event", "Syslog"):
        result = resolve_contract(table)
        assert result["status"] == "provisioning-plan"


def test_cli_resolve_prints_offline_plan_without_azure_access(capsys):
    result = main(
        [
            "resolve",
            "--table",
            "CommonSecurityLog",
            "--required-field",
            "DeviceEventClassID:string",
            "--required-field",
            "SourceIP",
        ]
    )

    output = capsys.readouterr().out
    assert result == 0
    assert '"status": "provisioning-plan"' in output
    assert '"writesPerformed": false' in output
    assert "schemaFingerprint" in output


def test_cli_candidate_check_is_read_only_and_scoped_to_exact_contract_resources(
    monkeypatch, capsys
):
    contract = common_security_log_contract()
    calls = []

    class Response:
        def __init__(self, status_code, value=None):
            self.status_code = status_code
            self._value = value or {}

        def json(self):
            return self._value

    class ReadOnlyClient:
        def resolve_workspace(self, identifier):
            assert identifier == "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.OperationalInsights/workspaces/ws"
            return Workspace(
                id=identifier,
                name="ws",
                subscription_id="sub",
                resource_group="rg",
                location="eastus",
                customer_id="customer",
            )

        def _resource_url(self, resource_id, api_version):
            return f"https://management.azure.com{resource_id}?api-version={api_version}"

        def request(self, method, url, **kwargs):
            calls.append((method, url))
            if "/tables/CommonSecurityLog?" in url:
                return Response(
                    200,
                    {
                        "properties": {
                            "schema": {
                                "standardColumns": arm_columns(contract.destination.columns)
                            }
                        }
                    },
                )
            return Response(404)

        def _resource_ids(self, workspace, contract_value):
            return "/dce", "/dcr"

    monkeypatch.setattr(cli, "AzureClient", ReadOnlyClient)
    result = main(
        [
            "resolve",
            "--table",
            "CommonSecurityLog",
            "--workspace",
            "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.OperationalInsights/workspaces/ws",
            "--check-existing",
        ]
    )

    output = capsys.readouterr().out
    assert result == 0
    assert '"status": "provisioning-plan"' in output
    assert calls and all(method == "GET" for method, _ in calls)
    assert any("/tables/CommonSecurityLog?" in url for _, url in calls)
    assert any(url.startswith("https://management.azure.com/dce?") for _, url in calls)
    assert any(url.startswith("https://management.azure.com/dcr?") for _, url in calls)


def test_cli_report_preserves_exact_workspace_without_cloud_access(tmp_path, capsys):
    workspace_id = (
        "/subscriptions/sub/resourceGroups/rg/providers/"
        "Microsoft.OperationalInsights/workspaces/ws"
    )
    report_path = tmp_path / "resolution.json"

    result = main(
        [
            "resolve",
            "--table",
            "CommonSecurityLog",
            "--workspace",
            workspace_id,
            "--report",
            str(report_path),
        ]
    )

    output = capsys.readouterr().out
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert result == 0
    assert f'"targetWorkspace": "{workspace_id}"' in output
    assert report["targetWorkspace"] == workspace_id
    assert report["writesPerformed"] is False
