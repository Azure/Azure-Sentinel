from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import ingest_to_dcr


class ScenarioHandoffTests(unittest.TestCase):
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
