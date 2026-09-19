from __future__ import annotations

from dataclasses import dataclass

import pytest

from azure_monitor_logs_ingestion.azure import (
    ARM_SCOPE,
    AzureClient,
    ProvisionedResources,
    Workspace,
)
from azure_monitor_logs_ingestion.contract import load_contract


@dataclass
class Token:
    token: str = "token"


class Credential:
    def get_token(self, scope):
        return Token()


class Response:
    def __init__(self, status_code, value=None, headers=None, text=""):
        self.status_code = status_code
        self._value = value or {}
        self.headers = headers or {}
        self.text = text
        self.content = b"{}" if value is not None else b""

    def json(self):
        return self._value


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)


def contract(tmp_path, kind="custom"):
    value = {
        "version": 1,
        "name": "sample",
        "workspace": "workspace",
        "inputStream": "Custom-SampleRaw",
        "inputColumns": [{"name": "EventTime", "type": "datetime"}],
        "transformKql": "source | project TimeGenerated=todatetime(EventTime)",
        "destination": {
            "kind": kind,
            "table": "Sample_CL" if kind == "custom" else "CommonSecurityLog",
            "outputStream": (
                "Custom-Sample_CL"
                if kind == "custom"
                else "Microsoft-CommonSecurityLog"
            ),
        },
        "resources": {"dce": "sample-dce", "dcr": "sample-dcr"},
    }
    if kind == "custom":
        value["destination"]["columns"] = [
            {"name": "TimeGenerated", "type": "datetime"}
        ]
    path = tmp_path / "contract.yaml"
    import yaml

    path.write_text(yaml.safe_dump(value), encoding="utf-8")
    return load_contract(path)


def workspace():
    return Workspace(
        id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.OperationalInsights/workspaces/ws",
        name="ws",
        subscription_id="sub",
        resource_group="rg",
        location="eastus",
        customer_id="customer",
    )


def test_ingest_posts_to_custom_input_stream(tmp_path):
    session = Session([Response(204)])
    client = AzureClient(credential=Credential(), session=session, retries=0)
    resources = ProvisionedResources(
        workspace=workspace(),
        dce_id="/dce",
        dce_endpoint="https://example.ingest.monitor.azure.com",
        dcr_id="/dcr",
        dcr_immutable_id="dcr-immutable",
    )

    result = client.ingest(
        contract(tmp_path),
        resources,
        [{"EventTime": "2026-09-09T12:00:00Z"}],
    )

    assert result == {"recordsAccepted": 1, "batchesAccepted": 1}
    method, url, kwargs = session.calls[0]
    assert method == "POST"
    assert "/streams/Custom-SampleRaw?" in url
    assert kwargs["json"][0]["EventTime"].endswith("Z")


def test_authorize_uses_subscription_scoped_role_definition():
    client = AzureClient(credential=Credential())
    captured = {}

    def put(resource_id, api_version, body):
        captured.update(body)
        return {}

    client._put_resource = put
    client.authorize(
        "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Insights/"
        "dataCollectionRules/dcr",
        "principal",
        principal_type="User",
    )

    role_id = captured["properties"]["roleDefinitionId"]
    assert role_id.startswith("/subscriptions/sub/")
    assert role_id.endswith("3913510d-42f4-4e42-8a64-420c390055eb")
    assert captured["properties"]["principalType"] == "User"


def test_refuses_to_overwrite_unmanaged_resource():
    session = Session(
        [Response(200, {"tags": {"managed-by": "someone-else"}})]
    )
    client = AzureClient(credential=Credential(), session=session, retries=0)

    with pytest.raises(RuntimeError, match="not managed"):
        client._put_managed_resource("/resource", "1", {"location": "eastus"})


def test_request_uses_arm_scope_by_default():
    credential = Credential()
    client = AzureClient(
        credential=credential,
        session=Session([Response(200, {"value": "ok"})]),
        retries=0,
    )

    response = client.request("GET", "https://management.azure.com/resource")

    assert response.json()["value"] == "ok"
    assert client._tokens[ARM_SCOPE] == "token"


def test_provision_builds_custom_input_to_standard_output(tmp_path):
    class ProvisionClient(AzureClient):
        def __init__(self):
            super().__init__(credential=Credential())
            self.resources = []

        def resolve_workspace(self, identifier):
            return workspace()

        def ensure_destination_table(self, workspace_value, contract_value):
            return {"name": contract_value.destination.table}

        def _put_managed_resource(self, resource_id, api_version, body):
            self.resources.append((resource_id, body))
            return {
                "properties": {
                    "logsIngestion": {
                        "endpoint": "https://example.ingest.monitor.azure.com"
                    }
                }
            }

        def request(self, method, url, **kwargs):
            return Response(404)

        def _put_resource(self, resource_id, api_version, body):
            self.resources.append((resource_id, body))
            return {"properties": {"immutableId": "dcr-immutable"}}

    client = ProvisionClient()

    client.provision(contract(tmp_path, kind="standard"))

    dcr_body = client.resources[1][1]
    properties = dcr_body["properties"]
    assert dcr_body["kind"] == "Direct"
    assert "Custom-SampleRaw" in properties["streamDeclarations"]
    assert properties["dataFlows"][0]["outputStream"] == "Microsoft-CommonSecurityLog"


def test_merge_dcr_body_preserves_existing_streams():
    existing = {
        "id": "/dcr",
        "name": "shared",
        "type": "Microsoft.Insights/dataCollectionRules",
        "etag": "etag",
        "location": "eastus",
        "kind": "Direct",
        "tags": {"managed-by": "azure-monitor-logs-ingestion"},
        "properties": {
            "dataCollectionEndpointId": "/dce",
            "streamDeclarations": {
                "Custom-Existing": {
                    "columns": [{"name": "Existing", "type": "string"}]
                }
            },
            "destinations": {
                "logAnalytics": [
                    {"name": "shared", "workspaceResourceId": "/workspace"}
                ]
            },
            "dataFlows": [
                {
                    "streams": ["Custom-Existing"],
                    "destinations": ["shared"],
                    "transformKql": "source",
                    "outputStream": "Custom-Existing_CL",
                }
            ],
        },
    }
    requested = {
        "location": "eastus",
        "kind": "Direct",
        "tags": {"managed-by": "azure-monitor-logs-ingestion"},
        "properties": {
            "dataCollectionEndpointId": "/dce",
            "streamDeclarations": {
                "Custom-New": {
                    "columns": [{"name": "New", "type": "string"}]
                }
            },
            "dataFlows": [
                {
                    "streams": ["Custom-New"],
                    "destinations": ["destination"],
                    "transformKql": "source",
                    "outputStream": "Custom-New_CL",
                }
            ],
        },
    }

    merged = AzureClient._merge_dcr_body(
        existing, requested, "Custom-New", "/workspace"
    )

    assert set(merged["properties"]["streamDeclarations"]) == {
        "Custom-Existing",
        "Custom-New",
    }
    assert [flow["streams"][0] for flow in merged["properties"]["dataFlows"]] == [
        "Custom-Existing",
        "Custom-New",
    ]
    assert merged["properties"]["dataFlows"][1]["destinations"] == ["shared"]
    assert "id" not in merged


@pytest.mark.parametrize(
    ("row_count", "found"),
    [(0, False), (3, True)],
)
def test_verify_reports_whether_fresh_rows_exist(row_count, found):
    session = Session(
        [
            Response(
                200,
                {
                    "tables": [
                        {
                            "columns": [
                                {"name": "Rows"},
                                {"name": "FirstIngested"},
                                {"name": "LastIngested"},
                            ],
                            "rows": [[row_count, None, None]],
                        }
                    ]
                },
            )
        ]
    )
    client = AzureClient(credential=Credential(), session=session, retries=0)
    resources = ProvisionedResources(
        workspace=workspace(),
        dce_id="/dce",
        dce_endpoint="https://example.ingest.monitor.azure.com",
        dcr_id="/dcr",
        dcr_immutable_id="dcr-immutable",
    )

    result = client.verify(resources, "CommonSecurityLog", 30)

    assert result["freshRows"] == row_count
    assert result["found"] is found
