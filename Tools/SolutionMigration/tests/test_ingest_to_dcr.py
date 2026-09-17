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
