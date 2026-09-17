from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import generate_mock_scenario as generator


RULE = {
    "id": "rule-123",
    "name": "Example - Delete activity",
    "query": "ExampleParser\n| where EventMessage =~ 'Delete activity'",
    "triggerOperator": "gt",
    "triggerThreshold": 0,
}

DETECTION = {
    "id": "detection-123",
    "sourceRuleId": "rule-123",
    "name": "Example - Delete activity",
    "query": "DeviceEvents\n| where ActionType =~ 'Delete activity'",
}


def _write_yaml(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def _create_custom_solution(root: Path) -> None:
    solution = root / "Solutions" / "Example"
    _write_yaml(solution / "Analytic Rules" / "rule.yaml", RULE)
    _write_yaml(solution / "XDR Detections" / "rule.yaml", DETECTION)
    _write_yaml(
        solution / "Parsers" / "ExampleParser.yaml",
        {
            "FunctionAlias": "ExampleParser",
            "FunctionQuery": "Example_CL | project EventMessage",
        },
    )
    dcr = {
        "type": "Microsoft.Insights/dataCollectionRules",
        "name": "ExampleDcr",
        "properties": {
            "streamDeclarations": {
                "Custom-Example_CL": {
                    "columns": [
                        {"name": "message", "type": "string"},
                        {"name": "created", "type": "datetime"},
                        {"name": "requestId", "type": "string"},
                    ]
                }
            },
            "dataFlows": [
                {
                    "streams": ["Custom-Example_CL"],
                    "outputStream": "Custom-Example_CL",
                    "transformKql": (
                        "source | project-rename EventMessage=message "
                        "| extend TimeGenerated=todatetime(created)"
                    ),
                }
            ],
        },
    }
    template = {
        "resources": [
            {
                "type": "Microsoft.Resources/templateSpecs/versions",
                "properties": {"mainTemplate": {"resources": [dcr]}},
            }
        ]
    }
    package = solution / "Package" / "mainTemplate.json"
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text(json.dumps(template), encoding="utf-8")


class MockScenarioGeneratorTests(unittest.TestCase):
    def test_randomization_uses_declared_types(self):
        original = {
            "created": "2026-09-17T00:00:00Z",
            "count": 1,
            "score": 1.5,
            "enabled": True,
            "details": {"source": "synthetic"},
            "message": "original",
        }
        records = generator.randomized_copies(
            [original],
            copies=1,
            seed=17,
            locked_paths=[],
            column_types={
                "created": "datetime",
                "count": "long",
                "score": "real",
                "enabled": "boolean",
                "details": "dynamic",
                "message": "string",
            },
        )

        randomized = records[0]
        repeated = generator.randomized_copies(
            [original],
            copies=1,
            seed=17,
            locked_paths=[],
            column_types={
                "created": "datetime",
                "count": "long",
                "score": "real",
                "enabled": "boolean",
                "details": "dynamic",
                "message": "string",
            },
        )
        generator.validate_records(records, {
            "created": "datetime",
            "count": "long",
            "score": "real",
            "enabled": "boolean",
            "details": "dynamic",
            "message": "string",
        })
        self.assertEqual(records, repeated)
        self.assertEqual(original["details"], randomized["details"])
        self.assertNotEqual(original["message"], randomized["message"])

    def test_generates_custom_dcr_scenario_and_reuses_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _create_custom_solution(root)
            with mock.patch.object(generator, "REPOSITORY_ROOT", root), \
                    mock.patch.object(generator, "TABLE_ROOT", root / "Sample Data" / "Tables"), \
                    mock.patch.object(
                        generator,
                        "MOCK_ROOT",
                        root / "Sample Data" / "Solutions" / "Mock",
                    ):
                result = generator.generate_scenario(
                    "Example",
                    "rule-123",
                    randomize=True,
                    copies=2,
                    seed=7,
                )
                existing = generator.generate_scenario("Example", "rule-123")

            scenario = result["scenario"]
            malicious = json.loads(Path(result["maliciousPath"]).read_text(encoding="utf-8"))
            benign = json.loads(Path(result["benignPath"]).read_text(encoding="utf-8"))

        self.assertEqual("qualification-ready", scenario["generationStatus"])
        self.assertEqual("Custom-Example_CL", scenario["ingestion"]["stream"])
        self.assertEqual("message", scenario["mapping"]["decisiveFields"][0]["rawPath"])
        self.assertEqual(2, len(malicious))
        self.assertEqual(2, len(benign))
        self.assertTrue(all(item["message"] == "Delete activity" for item in malicious))
        self.assertTrue(all(item["message"] == "__benign_non_match__" for item in benign))
        self.assertEqual("existing-scenario", existing["status"])

    def test_generates_standard_table_offline_scenario(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            solution = root / "Solutions" / "Example"
            standard_rule = {
                "id": "rule-standard",
                "name": "Device action",
                "query": "DeviceEvents\n| where ActionType == 'ExampleAction'",
                "triggerOperator": "gt",
                "triggerThreshold": 0,
            }
            _write_yaml(solution / "Analytic Rules" / "rule.yaml", standard_rule)
            _write_yaml(
                solution / "XDR Detections" / "rule.yaml",
                {
                    "id": "cd-standard",
                    "sourceRuleId": "rule-standard",
                    "name": "Device action",
                    "query": "DeviceEvents\n| where ActionType == 'ExampleAction'",
                },
            )
            package = solution / "Package" / "mainTemplate.json"
            package.parent.mkdir(parents=True)
            package.write_text('{"resources":[]}', encoding="utf-8")
            table = root / "Sample Data" / "Tables" / "DeviceEvents"
            table.mkdir(parents=True)
            (table / "base-event.json").write_text(
                json.dumps({"ActionType": "synthetic", "Timestamp": "2026-09-17T00:00:00Z"}),
                encoding="utf-8",
            )
            (table / "metadata.json").write_text(
                json.dumps({
                    "table": "DeviceEvents",
                    "schemaSource": "Microsoft public table schema",
                    "columns": {"ActionType": "string", "Timestamp": "datetime"},
                }),
                encoding="utf-8",
            )
            with mock.patch.object(generator, "REPOSITORY_ROOT", root), \
                    mock.patch.object(generator, "TABLE_ROOT", root / "Sample Data" / "Tables"), \
                    mock.patch.object(
                        generator,
                        "MOCK_ROOT",
                        root / "Sample Data" / "Solutions" / "Mock",
                    ):
                result = generator.generate_scenario("Example", "rule-standard")

        self.assertEqual("generated-offline-only", result["scenario"]["generationStatus"])
        self.assertFalse(result["scenario"]["ingestion"]["directLogsIngestionSupported"])

    def test_complex_rule_requires_reviewed_scenario(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _create_custom_solution(root)
            rule_path = root / "Solutions" / "Example" / "Analytic Rules" / "rule.yaml"
            complex_rule = dict(RULE)
            complex_rule["query"] = (
                "ExampleParser | summarize Events=count() by EventMessage "
                "| where Events > 3"
            )
            _write_yaml(rule_path, complex_rule)
            with mock.patch.object(generator, "REPOSITORY_ROOT", root), \
                    mock.patch.object(generator, "TABLE_ROOT", root / "Sample Data" / "Tables"), \
                    mock.patch.object(
                        generator,
                        "MOCK_ROOT",
                        root / "Sample Data" / "Solutions" / "Mock",
                    ):
                with self.assertRaisesRegex(generator.ScenarioError, "reviewed-scenario"):
                    generator.generate_scenario("Example", "rule-123")


if __name__ == "__main__":
    unittest.main()
