from __future__ import annotations

import json
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import ingest_to_dcr


class ScenarioHandoffTests(unittest.TestCase):
    def test_target_context_rejects_subscription_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "qualification-target.json"
            path.write_text(
                json.dumps(
                    {
                        "locked": True,
                        "tenantId": "tenant-id",
                        "subscriptionId": "expected-subscription",
                        "workspaceResourceId": (
                            "/subscriptions/other-subscription/resourceGroups/rg/"
                            "providers/Microsoft.OperationalInsights/workspaces/ws"
                        ),
                        "workspaceCustomerId": "customer-id",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ingest_to_dcr.ToolError,
                "workspace and subscription identifiers do not match",
            ):
                ingest_to_dcr._load_target_context(path)

    def test_target_context_forces_exact_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "qualification-target.json"
            workspace_id = (
                "/subscriptions/subscription-id/resourceGroups/rg/providers/"
                "Microsoft.OperationalInsights/workspaces/ws"
            )
            path.write_text(
                json.dumps(
                    {
                        "locked": True,
                        "tenantId": "tenant-id",
                        "subscriptionId": "subscription-id",
                        "workspaceResourceId": workspace_id,
                        "workspaceCustomerId": "customer-id",
                    }
                ),
                encoding="utf-8",
            )

            target = ingest_to_dcr._load_target_context(path)

        self.assertEqual(workspace_id, target["workspaceResourceId"])

    @mock.patch.object(ingest_to_dcr.shutil, "which")
    def test_windows_azure_cli_resolution_uses_command_shim(
        self,
        which: mock.Mock,
    ):
        which.return_value = r"C:\AzureCLI\az.cmd"
        with mock.patch.object(ingest_to_dcr.os, "name", "nt"):
            result = ingest_to_dcr._az_executable()

        self.assertEqual(r"C:\AzureCLI\az.cmd", result)
        which.assert_called_once_with("az.cmd")

    @mock.patch.object(ingest_to_dcr, "_resource_graph_query")
    def test_full_workspace_resource_id_never_lists_workspaces(
        self,
        resource_graph_query: mock.Mock,
    ):
        workspace_id = (
            "/subscriptions/subscription-id/resourceGroups/resource-group/providers/"
            "Microsoft.OperationalInsights/workspaces/workspace-name"
        )

        selected, alternatives, source = ingest_to_dcr.discover_workspace(
            "arm-token",
            "active-subscription",
            workspace_id,
        )

        self.assertEqual(workspace_id, selected["id"])
        self.assertEqual("subscription-id", selected["subscriptionId"])
        self.assertEqual([], alternatives)
        self.assertEqual("explicit", source)
        resource_graph_query.assert_not_called()

    @mock.patch.object(ingest_to_dcr, "_resource_graph_query")
    def test_customer_id_uses_one_exact_filtered_resolution(
        self,
        resource_graph_query: mock.Mock,
    ):
        customer_id = "756386d8-e2d4-4f09-905a-74b24313721f"
        workspace = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "name": "w",
            "subscriptionId": "s",
            "resourceGroup": "r",
            "properties": {"customerId": customer_id},
        }
        resource_graph_query.return_value = [workspace]

        selected, alternatives, source = ingest_to_dcr.discover_workspace(
            "arm-token",
            "active-subscription",
            customer_id,
        )

        self.assertEqual(workspace, selected)
        self.assertEqual([], alternatives)
        self.assertEqual("explicit", source)
        resource_graph_query.assert_called_once()
        self.assertIn(customer_id, resource_graph_query.call_args.args[1])

    def test_permission_matching_honors_wildcards_and_denies(self):
        self.assertTrue(ingest_to_dcr._permission_allows(
            [{"actions": ["Microsoft.Insights/*"], "notActions": []}],
            ingest_to_dcr.INGESTION_ACTION,
        ))
        self.assertFalse(ingest_to_dcr._permission_allows(
            [{
                "actions": ["Microsoft.Insights/*"],
                "notActions": ["Microsoft.Insights/Telemetry/Write"],
            }],
            ingest_to_dcr.INGESTION_ACTION,
        ))

    @mock.patch.object(ingest_to_dcr, "_request_json")
    @mock.patch.object(ingest_to_dcr, "_resource_graph_query")
    def test_dcr_discovery_prefers_isolated_standard_stream(
        self,
        resource_graph_query: mock.Mock,
        request_json: mock.Mock,
    ):
        workspace = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "subscriptionId": "s",
        }
        resource_graph_query.return_value = [
            {
                "id": "/shared",
                "name": "shared",
                "properties": {
                    "immutableId": "shared-id",
                    "dataCollectionEndpointId": "/shared-dce",
                    "streamDeclarations": {
                        "Custom-Example": {},
                        "Custom-Other": {},
                    },
                    "destinations": {
                        "logAnalytics": [{
                            "workspaceResourceId": workspace["id"],
                        }]
                    },
                    "dataFlows": [
                        {
                            "streams": ["Custom-Example"],
                            "outputStream": "Microsoft-Event",
                        },
                        {
                            "streams": ["Custom-Other"],
                            "outputStream": "Microsoft-Syslog",
                        },
                    ],
                },
            },
            {
                "id": "/isolated",
                "name": "isolated",
                "properties": {
                    "immutableId": "isolated-id",
                    "dataCollectionEndpointId": "/isolated-dce",
                    "streamDeclarations": {"Custom-Example": {}},
                    "destinations": {
                        "logAnalytics": [{
                            "workspaceResourceId": workspace["id"],
                        }]
                    },
                    "dataFlows": [{
                        "streams": ["Custom-Example"],
                        "outputStream": "Microsoft-Event",
                    }],
                },
            },
        ]
        request_json.return_value = (
            200,
            {
                "properties": {
                    "logsIngestion": {
                        "endpoint": "https://isolated.ingest.monitor.azure.com"
                    }
                }
            },
        )

        result = ingest_to_dcr.find_dcr_for_stream(
            "arm-token",
            workspace,
            "Custom-Example",
        )

        self.assertEqual("isolated", result["name"])
        self.assertTrue(result["isolated"])
        self.assertIn("/isolated-dce", request_json.call_args.args[1])

    @mock.patch.object(ingest_to_dcr, "_resource_graph_query")
    def test_dcr_discovery_rejects_shared_standard_stream(
        self,
        resource_graph_query: mock.Mock,
    ):
        workspace = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "subscriptionId": "s",
        }
        resource_graph_query.return_value = [{
            "id": "/shared",
            "name": "shared",
            "properties": {
                "immutableId": "shared-id",
                "dataCollectionEndpointId": "/shared-dce",
                "streamDeclarations": {
                    "Custom-Example": {},
                    "Custom-Other": {},
                },
                "destinations": {
                    "logAnalytics": [{
                        "workspaceResourceId": workspace["id"],
                    }]
                },
                "dataFlows": [{
                    "streams": ["Custom-Example"],
                    "outputStream": "Microsoft-Event",
                }],
            },
        }]

        with self.assertRaisesRegex(
            ingest_to_dcr.ToolError,
            "contract-specific DCE/DCR pair",
        ):
            ingest_to_dcr.find_dcr_for_stream(
                "arm-token",
                workspace,
                "Custom-Example",
            )

    @mock.patch.object(
        ingest_to_dcr,
        "_access_token",
        return_value="query-token",
    )
    @mock.patch.object(ingest_to_dcr, "_request_json")
    def test_permission_preflight_reports_ready_without_writing(
        self,
        request_json: mock.Mock,
        _access_token: mock.Mock,
    ):
        request_json.side_effect = [
            (200, {"tables": []}),
            (
                200,
                {
                    "value": [{
                        "actions": ["Microsoft.Insights/Telemetry/Write"],
                        "notActions": [],
                    }]
                },
            ),
        ]
        workspace = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "properties": {"customerId": "customer-id"},
        }
        dcr = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.Insights/dataCollectionRules/d",
        }

        result = ingest_to_dcr.permission_preflight("arm-token", workspace, dcr)

        self.assertEqual("ready", result["status"])
        self.assertFalse(result["writePerformed"])
        self.assertTrue(all(check["status"] == "ready" for check in result["checks"]))

    @mock.patch.object(
        ingest_to_dcr,
        "_access_token",
        return_value="query-token",
    )
    @mock.patch.object(ingest_to_dcr, "_request_json")
    def test_permission_preflight_reports_query_and_ingestion_failures(
        self,
        request_json: mock.Mock,
        _access_token: mock.Mock,
    ):
        request_json.side_effect = [
            ingest_to_dcr.ToolError("query forbidden"),
            (200, {"value": [{"actions": [], "notActions": []}]}),
        ]
        workspace = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "properties": {"customerId": "customer-id"},
        }
        dcr = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.Insights/dataCollectionRules/d",
        }

        result = ingest_to_dcr.permission_preflight("arm-token", workspace, dcr)

        self.assertEqual("action-required", result["status"])
        self.assertEqual(
            ["blocked", "blocked"],
            [check["status"] for check in result["checks"]],
        )

    @mock.patch.object(
        ingest_to_dcr,
        "_access_token",
        return_value="query-token",
    )
    @mock.patch.object(ingest_to_dcr, "_request_json")
    def test_permission_preflight_offers_approved_missing_table_recovery(
        self,
        request_json: mock.Mock,
        _access_token: mock.Mock,
    ):
        request_json.side_effect = [
            (200, {"tables": []}),
            (
                200,
                {
                    "value": [{
                        "actions": ["Microsoft.Insights/Telemetry/Write"],
                        "notActions": [],
                    }]
                },
            ),
            (404, {"error": {"code": "ResourceNotFound"}}),
            (
                200,
                {
                    "value": [{
                        "actions": [
                            "Microsoft.OperationalInsights/workspaces/tables/write"
                        ],
                        "notActions": [],
                    }]
                },
            ),
        ]
        workspace = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "properties": {"customerId": "customer-id"},
        }
        dcr = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.Insights/dataCollectionRules/d",
            "outputTable": "Example_CL",
        }
        contract = {
            "tableName": "Example_CL",
            "schemaSource": "mainTemplate.json",
            "columnCount": 2,
            "properties": {
                "schema": {
                    "name": "Example_CL",
                    "columns": [
                        {"name": "TimeGenerated", "type": "dateTime"},
                        {"name": "Message", "type": "string"},
                    ],
                }
            },
        }

        result = ingest_to_dcr.permission_preflight(
            "arm-token",
            workspace,
            dcr,
            contract,
        )

        self.assertEqual("action-required", result["status"])
        checks = {check["name"]: check for check in result["checks"]}
        self.assertEqual("missing", checks["customLogTable"]["status"])
        self.assertTrue(checks["customLogTable"]["deploymentAvailable"])
        self.assertEqual(
            "ready",
            checks["customTableDeploymentPermission"]["status"],
        )
        self.assertFalse(result["writePerformed"])

    def test_loads_exact_table_schema_from_packaged_solution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "Solutions" / "Sample" / "Package" / "mainTemplate.json"
            package.parent.mkdir(parents=True)
            package.write_text(
                json.dumps({
                    "resources": [{
                        "type": "Wrapper",
                        "properties": {
                            "mainTemplate": {
                                "resources": [{
                                    "type": (
                                        "Microsoft.OperationalInsights/"
                                        "workspaces/tables"
                                    ),
                                    "name": "Example_CL",
                                    "properties": {
                                        "schema": {
                                            "name": "Example_CL",
                                            "columns": [
                                                {
                                                    "name": "TimeGenerated",
                                                    "type": "datetime",
                                                },
                                                {
                                                    "name": "Message",
                                                    "type": "string",
                                                },
                                            ],
                                        }
                                    },
                                }]
                            }
                        },
                    }]
                }),
                encoding="utf-8",
            )
            with mock.patch.object(ingest_to_dcr, "REPOSITORY_ROOT", root):
                contract = ingest_to_dcr.load_custom_table_contract(
                    "Sample",
                    "Example_CL",
                )

        self.assertEqual("Example_CL", contract["tableName"])
        self.assertEqual(2, contract["columnCount"])
        self.assertEqual("Analytics", contract["tablePlan"])
        self.assertEqual(
            "dateTime",
            contract["properties"]["schema"]["columns"][0]["type"],
        )

    @mock.patch.object(ingest_to_dcr.time, "sleep")
    @mock.patch.object(ingest_to_dcr, "_request_json")
    def test_deploys_missing_table_and_verifies_schema(
        self,
        request_json: mock.Mock,
        sleep: mock.Mock,
    ):
        request_json.side_effect = [
            (202, None),
            (
                200,
                {
                    "id": "/subscriptions/s/tables/Example_CL",
                    "properties": {
                        "provisioningState": "Succeeded",
                        "schema": {
                            "columns": [
                                {"name": "TimeGenerated", "type": "dateTime"},
                                {"name": "Message", "type": "string"},
                            ]
                        },
                    },
                },
            ),
        ]
        workspace = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
        }
        contract = {
            "tableName": "Example_CL",
            "schemaSource": "mainTemplate.json",
            "columnCount": 2,
            "properties": {
                "schema": {
                    "name": "Example_CL",
                    "columns": [
                        {"name": "TimeGenerated", "type": "dateTime"},
                        {"name": "Message", "type": "string"},
                    ],
                }
            },
        }

        result = ingest_to_dcr.deploy_custom_table(
            "arm-token",
            workspace,
            contract,
            delay_seconds=0,
        )

        self.assertEqual("created", result["status"])
        self.assertEqual("Example_CL", result["tableName"])
        sleep.assert_not_called()
        self.assertEqual("PUT", request_json.call_args_list[0].args[0])
        self.assertEqual(
            {"properties": contract["properties"]},
            request_json.call_args_list[0].args[3],
        )

    def test_refuses_table_deployment_without_separate_approval(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            ingest_to_dcr.main(
                [
                    "--stream",
                    "Custom-Example_CL",
                    "--solution",
                    "Sample",
                    "--deploy-missing-table",
                ]
            )

    @mock.patch.object(ingest_to_dcr, "deploy_custom_table")
    @mock.patch.object(ingest_to_dcr, "permission_preflight")
    @mock.patch.object(ingest_to_dcr, "load_custom_table_contract")
    @mock.patch.object(ingest_to_dcr, "find_dcr_for_stream")
    @mock.patch.object(ingest_to_dcr, "discover_workspace")
    @mock.patch.object(ingest_to_dcr, "_access_token", return_value="arm-token")
    @mock.patch.object(ingest_to_dcr, "_active_account")
    def test_approved_table_recovery_deploys_then_retries_preflight(
        self,
        active_account: mock.Mock,
        _access_token: mock.Mock,
        discover_workspace: mock.Mock,
        find_dcr: mock.Mock,
        load_contract: mock.Mock,
        permission_preflight: mock.Mock,
        deploy_table: mock.Mock,
    ):
        active_account.return_value = {
            "id": "subscription-id",
            "tenantId": "tenant-id",
            "name": "subscription",
        }
        workspace = {
            "id": "/subscriptions/subscription-id/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "name": "w",
            "subscriptionId": "subscription-id",
            "properties": {"customerId": "customer-id"},
        }
        discover_workspace.return_value = (workspace, [workspace], "explicit")
        dcr = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.Insights/dataCollectionRules/d",
            "name": "d",
            "immutableId": "dcr-id",
            "endpoint": "https://example.ingest.monitor.azure.com",
            "outputStream": "Custom-Example_CL",
            "outputTable": "Example_CL",
        }
        find_dcr.return_value = dcr
        contract = {
            "tableName": "Example_CL",
            "schemaSource": "mainTemplate.json",
            "columnCount": 2,
            "tablePlan": "Analytics",
            "retentionInDays": None,
            "totalRetentionInDays": None,
            "properties": {"schema": {"name": "Example_CL", "columns": []}},
        }
        load_contract.return_value = contract
        permission_preflight.side_effect = [
            {
                "status": "action-required",
                "checks": [
                    {"name": "customLogTable", "status": "missing"},
                    {
                        "name": "customTableDeploymentPermission",
                        "status": "ready",
                    },
                ],
                "writePerformed": False,
            },
            {
                "status": "ready",
                "checks": [{"name": "customLogTable", "status": "ready"}],
                "writePerformed": False,
            },
        ]
        deploy_table.return_value = {
            "status": "created",
            "tableName": "Example_CL",
        }

        with tempfile.TemporaryDirectory() as temp:
            target_path = Path(temp) / "qualification-target.json"
            target_path.write_text(
                json.dumps(
                    {
                        "locked": True,
                        "tenantId": "tenant-id",
                        "subscriptionId": "subscription-id",
                        "workspaceResourceId": workspace["id"],
                        "workspaceCustomerId": "customer-id",
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = ingest_to_dcr.main(
                    [
                        "--target-context",
                        str(target_path),
                        "--stream",
                        "Custom-Example_CL",
                        "--solution",
                        "Sample",
                        "--deploy-missing-table",
                        "--approve-table-write",
                    ]
                )

        self.assertEqual(0, exit_code)
        deploy_table.assert_called_once_with("arm-token", workspace, contract)
        self.assertEqual("ready", json.loads(stdout.getvalue())["status"])

    def test_accepts_qualification_ready_matching_stream(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            payload = folder / "mock.json"
            payload.write_text('[{"message":"match"}]', encoding="utf-8")
            scenario = {
                "generationStatus": "qualification-ready",
                "ingestion": {
                    "directLogsIngestionSupported": True,
                    "stream": "Custom-Example_CL",
                },
                "fixtures": {"mockRecords": 1},
                "validation": {"schemaValidation": "passed"},
            }
            (folder / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")

            result = ingest_to_dcr.validate_scenario_for_ingestion(
                payload,
                "Custom-Example_CL",
                "mock",
            )

        self.assertEqual(folder / "scenario.json", result)

    def test_default_payload_discovery_uses_shared_mock_json(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            mock_path = folder / "mock.json"
            mock_path.write_text('[{"message":"match"}]', encoding="utf-8")

            result = ingest_to_dcr.resolve_payload_path(
                None,
                "Sample",
                "rule-id",
                "mock",
                folder,
            )

        self.assertEqual(mock_path, result)

    def test_rejects_offline_only_scenario(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            payload = folder / "mock.json"
            payload.write_text('[{"message":"match"}]', encoding="utf-8")
            scenario = {
                "generationStatus": "generated-offline-only",
                "ingestion": {
                    "directLogsIngestionSupported": False,
                    "stream": None,
                },
                "fixtures": {"mockRecords": 1},
                "validation": {"schemaValidation": "passed"},
            }
            (folder / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")

            with self.assertRaisesRegex(ingest_to_dcr.ToolError, "qualification-ready"):
                ingest_to_dcr.validate_scenario_for_ingestion(
                    payload,
                    "Microsoft-DeviceEvents",
                    "mock",
                )


if __name__ == "__main__":
    unittest.main()
