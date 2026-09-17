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
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "name": "w",
            "subscriptionId": "subscription-id",
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

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = ingest_to_dcr.main(
                [
                    "--workspace",
                    workspace["id"],
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
            payload = folder / "malicious.json"
            payload.write_text('[{"message":"match"}]', encoding="utf-8")
            scenario = {
                "generationStatus": "qualification-ready",
                "ingestion": {
                    "directLogsIngestionSupported": True,
                    "stream": "Custom-Example_CL",
                },
                "fixtures": {"maliciousRecords": 1, "benignRecords": 1},
                "validation": {"schemaValidation": "passed"},
            }
            (folder / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")

            result = ingest_to_dcr.validate_scenario_for_ingestion(
                payload,
                "Custom-Example_CL",
                "malicious",
            )

        self.assertEqual(folder / "scenario.json", result)

    def test_rejects_offline_only_scenario(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            payload = folder / "malicious.json"
            payload.write_text('[{"message":"match"}]', encoding="utf-8")
            scenario = {
                "generationStatus": "generated-offline-only",
                "ingestion": {
                    "directLogsIngestionSupported": False,
                    "stream": None,
                },
                "fixtures": {"maliciousRecords": 1, "benignRecords": 1},
                "validation": {"schemaValidation": "passed"},
            }
            (folder / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")

            with self.assertRaisesRegex(ingest_to_dcr.ToolError, "qualification-ready"):
                ingest_to_dcr.validate_scenario_for_ingestion(
                    payload,
                    "Microsoft-DeviceEvents",
                    "malicious",
                )


if __name__ == "__main__":
    unittest.main()
