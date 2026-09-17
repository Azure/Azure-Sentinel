from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import ingest_to_dcr


class ScenarioHandoffTests(unittest.TestCase):
    @mock.patch.object(ingest_to_dcr, "_run_az")
    def test_tenant_subscription_discovery_excludes_other_tenants(
        self,
        run_az: mock.Mock,
    ):
        run_az.return_value = [
            {"id": "primary-sub", "tenantId": "tenant", "state": "Enabled"},
            {"id": "disabled-sub", "tenantId": "tenant", "state": "Disabled"},
            {"id": "other-sub", "tenantId": "other", "state": "Enabled"},
        ]

        result = ingest_to_dcr._tenant_subscriptions({
            "id": "primary-sub",
            "tenantId": "tenant",
        })

        self.assertEqual(["primary-sub"], [item["id"] for item in result])

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

    @mock.patch.object(ingest_to_dcr, "_request_json")
    @mock.patch.object(ingest_to_dcr, "_resource_graph_query")
    def test_discovers_defender_xdr_primary_when_settings_are_missing(
        self,
        resource_graph: mock.Mock,
        request_json: mock.Mock,
    ):
        workspaces = [
            {
                "id": "/subscriptions/s/resourceGroups/r/providers/"
                "Microsoft.OperationalInsights/workspaces/secondary",
                "name": "secondary",
                "subscriptionId": "s",
                "resourceGroup": "r",
                "properties": {},
            },
            {
                "id": "/subscriptions/s/resourceGroups/r/providers/"
                "Microsoft.OperationalInsights/workspaces/primary",
                "name": "primary",
                "subscriptionId": "s",
                "resourceGroup": "r",
                "properties": {},
            },
        ]
        resource_graph.return_value = workspaces
        request_json.side_effect = lambda _method, url, _token: (
            (
                200,
                {
                    "value": [{
                        "kind": "MicrosoftThreatProtection",
                        "properties": {
                            "dataTypes": {
                                "alerts": {"state": "enabled"},
                                "incidents": {"state": "enabled"},
                            }
                        },
                    }]
                },
            )
            if "/workspaces/primary/" in url
            else (200, {"value": []})
        )
        with tempfile.TemporaryDirectory() as temp, mock.patch.dict(
            ingest_to_dcr.os.environ,
            {"SENTINEL_XDR_MIGRATION_STATE_DIR": temp},
            clear=True,
        ):
            result = ingest_to_dcr.discover_workspace("token", "s", None)

        self.assertEqual("primary", result["workspace"]["name"])
        self.assertEqual("defender-xdr-primary", result["source"])
        self.assertFalse(result["settingsExist"])

    def test_primary_connector_requires_enabled_alerts_and_incidents(self):
        base = {
            "kind": "MicrosoftThreatProtection",
            "properties": {
                "dataTypes": {
                    "alerts": {"state": "enabled"},
                    "incidents": {"state": "enabled"},
                }
            },
        }
        self.assertTrue(ingest_to_dcr._is_primary_defender_xdr_connector(base))
        secondary = json.loads(json.dumps(base))
        secondary["properties"]["dataTypes"]["incidents"]["state"] = "disabled"
        self.assertFalse(ingest_to_dcr._is_primary_defender_xdr_connector(secondary))

    @mock.patch.object(
        ingest_to_dcr,
        "_request_json",
        return_value=(200, {"value": []}),
    )
    @mock.patch.object(ingest_to_dcr, "_resource_graph_query")
    def test_missing_primary_signal_requires_workspace_id(
        self,
        resource_graph: mock.Mock,
        _request_json: mock.Mock,
    ):
        resource_graph.return_value = [
            {
                "id": "/subscriptions/s/resourceGroups/r/providers/"
                "Microsoft.OperationalInsights/workspaces/a",
                "name": "a",
                "subscriptionId": "s",
                "resourceGroup": "r",
                "properties": {},
            },
            {
                "id": "/subscriptions/s/resourceGroups/r/providers/"
                "Microsoft.OperationalInsights/workspaces/b",
                "name": "b",
                "subscriptionId": "s",
                "resourceGroup": "r",
                "properties": {},
            },
        ]
        with tempfile.TemporaryDirectory() as temp, mock.patch.dict(
            ingest_to_dcr.os.environ,
            {"SENTINEL_XDR_MIGRATION_STATE_DIR": temp},
            clear=True,
        ):
            with self.assertRaisesRegex(ingest_to_dcr.ToolError, "--workspace"):
                ingest_to_dcr.discover_workspace("token", "s", None)

    @mock.patch.object(ingest_to_dcr, "_resource_graph_query")
    def test_saved_workspace_requires_verification_without_rediscovery(
        self,
        resource_graph: mock.Mock,
    ):
        saved_id = (
            "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/saved"
        )
        resource_graph.return_value = [{
            "id": saved_id,
            "name": "saved",
            "subscriptionId": "s",
            "resourceGroup": "r",
            "properties": {},
        }]
        with tempfile.TemporaryDirectory() as temp, mock.patch.dict(
            ingest_to_dcr.os.environ,
            {"SENTINEL_XDR_MIGRATION_STATE_DIR": temp},
            clear=True,
        ):
            config = Path(temp) / ingest_to_dcr.CONFIG_NAME
            config.write_text(json.dumps({"workspaceId": saved_id}), encoding="utf-8")
            result = ingest_to_dcr.discover_workspace("token", "s", None)

        self.assertEqual("saved-settings", result["source"])
        self.assertTrue(result["settingsExist"])
        self.assertEqual(saved_id, result["configuredWorkspaceId"])

    def test_saved_workspace_from_another_tenant_requires_rediscovery(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.dict(
            ingest_to_dcr.os.environ,
            {"SENTINEL_XDR_MIGRATION_STATE_DIR": temp},
            clear=True,
        ):
            config = Path(temp) / ingest_to_dcr.CONFIG_NAME
            config.write_text(
                json.dumps({
                    "tenantId": "old-tenant",
                    "workspaceId": "/subscriptions/s/resourceGroups/r/providers/"
                    "Microsoft.OperationalInsights/workspaces/saved",
                }),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ingest_to_dcr.ToolError, "different tenant"):
                ingest_to_dcr.discover_workspace(
                    "token",
                    "s",
                    None,
                    tenant_id="new-tenant",
                )

    def test_confirmed_workspace_is_saved_without_secrets(self):
        workspace = {
            "id": "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/primary",
            "name": "primary",
        }
        with tempfile.TemporaryDirectory() as temp, mock.patch.dict(
            ingest_to_dcr.os.environ,
            {"SENTINEL_XDR_MIGRATION_STATE_DIR": temp},
            clear=True,
        ):
            path = ingest_to_dcr._save_workspace_settings(workspace, "tenant")
            saved = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(workspace["id"], saved["workspaceId"])
        self.assertEqual("primary", saved["workspaceName"])
        self.assertEqual("tenant", saved["tenantId"])
        self.assertTrue(saved["workspaceVerifiedAt"])
        self.assertNotIn("token", json.dumps(saved).lower())

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
