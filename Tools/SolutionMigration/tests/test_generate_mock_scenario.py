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


class QueryExtractionTests(unittest.TestCase):
    def test_nested_rule_and_detection_selection_preserves_relative_identity(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            root = Path(temp)
            solution = root / "Solutions" / "Example"
            for index, relative in enumerate(("Execution/Deep/rule.yml", "Persistence/rule.yml", "ROOT.YAML")):
                rule = dict(RULE, id=f"source-{index}")
                detection = dict(DETECTION, sourceRuleId=rule["id"])
                _write_yaml(solution / "Analytic Rules" / relative, rule)
                _write_yaml(solution / "XDR Detections" / relative, detection)
            with mock.patch.object(generator, "REPOSITORY_ROOT", root):
                source, rule = generator.find_analytic_rule("Example", "Execution\\Deep\\rule.yml")
                detection, _ = generator.find_custom_detection("Example", None, rule)
                self.assertEqual("Execution/Deep/rule.yml", source.relative_to(solution / "Analytic Rules").as_posix())
                self.assertEqual("Execution/Deep/rule.yml", detection.relative_to(solution / "XDR Detections").as_posix())
                selected, _ = generator.find_custom_detection("Example", "Execution/Deep/rule.yml", rule)
                self.assertEqual(detection, selected)
                self.assertEqual("ROOT.YAML", generator.find_analytic_rule("Example", "source-2")[0].name)
                with self.assertRaisesRegex(generator.ScenarioError, "ambiguous"):
                    generator.find_analytic_rule("Example", "rule")
                with self.assertRaisesRegex(generator.ScenarioError, "Multiple"):
                    generator.find_custom_detection("Example", "rule", rule)

    def test_reads_converted_custom_detection_query(self) -> None:
        document = {
            "properties": {
                "queryCondition": {
                    "queryText": "DeviceEvents | take 1",
                }
            }
        }

        self.assertEqual(
            "DeviceEvents | take 1",
            generator._query(document),
        )

    def test_extracts_first_value_from_dynamic_let_list(self) -> None:
        query = (
            "let reputation = dynamic(['unknown', 'badHost']);\n"
            "Cloudflare\n"
            "| where ClientIPClass in~ (reputation)"
        )

        self.assertEqual(
            [{
                "column": "ClientIPClass",
                "operator": "in~",
                "value": "unknown",
            }],
            generator.extract_predicates(query),
        )

    def test_structured_event_parsing_requires_review(self) -> None:
        assessment = generator.assess_query(
            "SecurityEvent | extend EventData=parse_xml(EventData) "
            "| mv-expand EventData | evaluate bag_unpack(EventData)",
            {},
        )

        self.assertEqual("manual-review-required", assessment["status"])
        self.assertIn(
            "The query parses or expands structured event content.",
            assessment["reasons"],
        )

    def test_unmodeled_content_predicate_requires_review(self) -> None:
        assessment = generator.assess_query(
            'SecurityEvent | where CommandLine has_all ("-r", "-s")',
            {},
        )

        self.assertEqual("manual-review-required", assessment["status"])
        self.assertIn(
            "The query uses a content predicate that automatic fixtures do not model.",
            assessment["reasons"],
        )

    def test_reads_converted_custom_detection_identity(self) -> None:
        document = {
            "contentProvenance": {"source": {"id": "rule-123"}},
            "properties": {
                "id": "detection-123",
                "displayName": "Example detection",
            },
        }

        self.assertEqual("rule-123", generator._detection_source_id(document))
        self.assertEqual(
            "detection-123",
            generator._detection_property(document, "id"),
        )

    def test_query_alias_predicate_is_not_reported_as_a_source_field(self) -> None:
        query = (
            "CommonSecurityLog\n"
            "| extend EventClass = DeviceEventClassID\n"
            "| where EventClass == '733101'"
        )

        required, aliases = generator._query_predicate_fields(
            query,
            {"DeviceEventClassID": "string", "EventClass": "string"},
        )

        self.assertEqual({}, required)
        self.assertEqual(["EventClass"], aliases)
        self.assertEqual(
            {"DeviceEventClassID": "string"},
            generator._query_fields_from_schema(
                query,
                {"DeviceEventClassID": "string", "EventClass": "string"},
            ),
        )


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
    def test_routes_source_candidate_fixture_and_output_across_worktrees(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_root = root / "azure-sentinel-source"
            output_root = root / "azure-sentinel-target" / "Sample Data" / "Solutions" / "Mock"
            _create_custom_solution(source_root)
            (root / "toolkit-sample-data" / "Tables").mkdir(parents=True)
            rule_path = source_root / "Solutions" / "Example" / "Analytic Rules" / "rule.yaml"
            complex_rule = dict(RULE)
            complex_rule["query"] = (
                "ExampleParser | where EventMessage == 'synthetic-match-a' "
                "| summarize Events=count() by EventMessage "
                "| where Events > 1"
            )
            _write_yaml(rule_path, complex_rule)
            detection_path = source_root / "Solutions" / "Example" / "XDR Detections" / "rule.yaml"
            detection = dict(DETECTION, query=complex_rule["query"])
            _write_yaml(detection_path, detection)
            candidate_path = root / "candidate-scenario.json"
            candidate_path.write_text(
                json.dumps({
                    "name": "candidate-multi-event",
                    "hypothesis": "Two synthetic records are a provisional count-scenario candidate.",
                    "lockedPaths": ["requestId"],
                    "maliciousRecords": [
                        {
                            "message": "synthetic-match-a",
                            "created": "2026-10-11T12:00:00Z",
                            "requestId": "campaign-unique-1",
                        },
                        {
                            "message": "synthetic-match-a",
                            "created": "2026-10-11T12:01:00Z",
                            "requestId": "campaign-unique-1",
                        },
                    ],
                    "benignRecords": [
                        {
                            "message": "synthetic-benign",
                            "created": "2026-10-11T12:02:00Z",
                            "requestId": "benign-unique-1",
                        }
                    ],
                }),
                encoding="utf-8",
            )

            result = generator.generate_scenario(
                "Example",
                str(rule_path),
                custom_detection_selector=str(detection_path),
                candidate_scenario=candidate_path,
                source_root=source_root,
                toolkit_root=Path(generator.__file__).resolve().parents[2],
                sample_data_root=root / "toolkit-sample-data",
                output_root=output_root,
            )
            reused = generator.generate_scenario(
                "Example",
                str(rule_path),
                custom_detection_selector=str(detection_path),
                candidate_scenario=candidate_path,
                source_root=source_root,
                toolkit_root=Path(generator.__file__).resolve().parents[2],
                sample_data_root=root / "toolkit-sample-data",
                output_root=output_root,
            )
            payload = json.loads(Path(result["mockPath"]).read_text(encoding="utf-8"))
            manifest = result["scenario"]

            self.assertEqual(output_root.resolve(), Path(result["paths"]["outputRoot"]))
            self.assertEqual(source_root.resolve(), Path(result["paths"]["sourceRoot"]))
            self.assertEqual(
                Path(result["paths"]["toolkitRoot"]),
                Path(manifest["toolkitRoot"]),
            )
            self.assertEqual(
                Path(result["paths"]["sampleDataRoot"]),
                Path(manifest["sampleDataRoot"]),
            )
            self.assertEqual(2, len(payload))
            self.assertEqual(1, manifest["fixtures"]["benignValidationRecords"])
            self.assertEqual("manual-review-required", manifest["queryAssessment"]["status"])
            self.assertEqual("generated-offline-only", manifest["generationStatus"])
            self.assertEqual("generated-candidate", result["status"])
            self.assertEqual("review-pending", manifest["scenarioReview"]["status"])
            self.assertEqual("candidate", manifest["scenarioReview"]["inputKind"])
            self.assertEqual("pending", manifest["validation"]["semanticReview"])
            self.assertEqual("not-run", manifest["validation"]["semanticMatch"])
            self.assertEqual("existing-candidate", reused["status"])
            with self.assertRaisesRegex(generator.ScenarioError, "review the existing fixture first"):
                generator.generate_scenario(
                    "Example",
                    str(rule_path),
                    custom_detection_selector=str(detection_path),
                    candidate_scenario=candidate_path,
                    force=True,
                    source_root=source_root,
                    toolkit_root=Path(generator.__file__).resolve().parents[2],
                    sample_data_root=root / "toolkit-sample-data",
                    output_root=output_root,
                )
            changed_candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            changed_candidate["hypothesis"] = "Updated provisional hypothesis."
            candidate_path.write_text(json.dumps(changed_candidate), encoding="utf-8")
            with self.assertRaisesRegex(generator.ScenarioError, "input hash or review state"):
                generator.generate_scenario(
                    "Example",
                    str(rule_path),
                    custom_detection_selector=str(detection_path),
                    candidate_scenario=candidate_path,
                    source_root=source_root,
                    toolkit_root=Path(generator.__file__).resolve().parents[2],
                    sample_data_root=root / "toolkit-sample-data",
                    output_root=output_root,
                )
            self.assertEqual(
                Path(result["scenarioPath"]).parents[2],
                output_root.resolve(),
            )
            self.assertFalse((source_root / "Sample Data" / "Solutions" / "Mock").exists())

    def test_blocks_missing_or_symlinked_reviewed_scenario(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _create_custom_solution(root)
            candidate_path = root / "candidate.json"
            candidate_path.write_text("{}", encoding="utf-8")
            with mock.patch.object(generator, "REPOSITORY_ROOT", root), \
                    mock.patch.object(generator, "TABLE_ROOT", root / "Sample Data" / "Tables"), \
                    mock.patch.object(
                        generator,
                        "MOCK_ROOT",
                        root / "Sample Data" / "Solutions" / "Mock",
                    ):
                with self.assertRaisesRegex(generator.ScenarioError, "Scenario input was not found"):
                    generator.generate_scenario(
                        "Example",
                        "rule-123",
                        candidate_scenario=root / "missing.json",
                    )
                if hasattr(Path, "symlink_to"):
                    link = root / "candidate-link.json"
                    link.symlink_to(candidate_path)
                    with self.assertRaisesRegex(generator.ScenarioError, "must not be a symlink"):
                        generator.generate_scenario(
                            "Example",
                            "rule-123",
                            candidate_scenario=link,
                        )
                    output_root = root / "mock-output"
                    output_root.mkdir()
                    target = root / "outside-target"
                    target.mkdir()
                    (output_root / "Example").symlink_to(target, target_is_directory=True)
                    with self.assertRaisesRegex(generator.ScenarioError, "Symlink output"):
                        generator.generate_scenario(
                            "Example",
                            "rule-123",
                            output_root=output_root,
                        )

    def test_candidate_on_simple_rule_remains_offline_and_pending_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _create_custom_solution(root)
            candidate_path = root / "candidate.json"
            candidate_path.write_text(
                json.dumps({
                    "name": "simple-rule-candidate",
                    "hypothesis": "Provisional simple predicate candidate.",
                    "lockedPaths": ["requestId"],
                    "maliciousRecords": [{
                        "message": "Delete activity",
                        "created": "2026-10-11T12:00:00Z",
                        "requestId": "candidate-unique",
                    }],
                    "benignRecords": [{
                        "message": "not the matching action",
                        "created": "2026-10-11T12:01:00Z",
                        "requestId": "benign-unique",
                    }],
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
                result = generator.generate_scenario(
                    "Example",
                    "rule-123",
                    candidate_scenario=candidate_path,
                )
                with self.assertRaisesRegex(generator.ScenarioError, "not both"):
                    generator.generate_scenario(
                        "Example",
                        "rule-123",
                        reviewed_scenario=candidate_path,
                        candidate_scenario=candidate_path,
                    )

        scenario = result["scenario"]
        self.assertEqual("simple", scenario["queryAssessment"]["status"])
        self.assertEqual("generated-offline-only", scenario["generationStatus"])
        self.assertEqual("review-pending", scenario["scenarioReview"]["status"])
        self.assertEqual("pending", scenario["validation"]["semanticReview"])
        self.assertEqual("not-run", scenario["validation"]["semanticMatch"])
        self.assertNotEqual("qualification-ready", scenario["generationStatus"])

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
            mock_records = json.loads(Path(result["mockPath"]).read_text(encoding="utf-8"))

        self.assertEqual("qualification-ready", scenario["generationStatus"])
        self.assertEqual("Custom-Example_CL", scenario["ingestion"]["stream"])
        self.assertEqual("message", scenario["mapping"]["decisiveFields"][0]["rawPath"])
        self.assertEqual(2, len(mock_records))
        self.assertTrue(all(item["message"] == "Delete activity" for item in mock_records))
        self.assertEqual(2, scenario["fixtures"]["benignValidationRecords"])
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

    def test_generates_supported_standard_table_ingestion_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            solution = root / "Solutions" / "Example"
            _write_yaml(
                solution / "Analytic Rules" / "rule.yaml",
                {
                    "id": "rule-event",
                    "name": "Synthetic Event",
                    "query": "Event\n| where EventID == 13",
                    "triggerOperator": "gt",
                    "triggerThreshold": 0,
                },
            )
            _write_yaml(
                solution / "XDR Detections" / "rule.yaml",
                {
                    "id": "cd-event",
                    "sourceRuleId": "rule-event",
                    "name": "Synthetic Event",
                    "query": "Event\n| where EventID == 13",
                },
            )
            package = solution / "Package" / "mainTemplate.json"
            package.parent.mkdir(parents=True)
            package.write_text('{"resources":[]}', encoding="utf-8")
            table = root / "Sample Data" / "Tables" / "Event"
            table.mkdir(parents=True)
            (table / "base-event.json").write_text(
                json.dumps({
                    "Computer": "synthetic-host.example.invalid",
                    "EventID": 0,
                    "TenantId": "must-be-pruned",
                    "TimeGenerated": "2026-09-22T00:00:00Z",
                }),
                encoding="utf-8",
            )
            (table / "metadata.json").write_text(
                json.dumps({
                    "table": "Event",
                    "schemaSource": "Microsoft public table schema",
                    "columns": {
                        "Computer": "string",
                        "EventID": "int",
                        "TenantId": "string",
                        "TimeGenerated": "datetime",
                    },
                }),
                encoding="utf-8",
            )
            contracts = root / "contracts"
            _write_yaml(
                contracts / "Event.yaml",
                {
                    "version": 1,
                    "name": "event-mock",
                    "workspace": "qualification-target",
                    "inputStream": "Custom-EventMock",
                    "inputColumns": [
                        {"name": "Computer", "type": "string"},
                        {"name": "EventID", "type": "int"},
                        {"name": "TimeGenerated", "type": "datetime"},
                    ],
                    "transformKql": "source | project Computer, EventID, TimeGenerated",
                    "destination": {
                        "kind": "standard",
                        "table": "Event",
                        "outputStream": "Microsoft-Event",
                    },
                    "resources": {
                        "dce": "event-mock-dce",
                        "dcr": "event-mock-dcr",
                    },
                },
            )
            _write_yaml(
                root / "registry.yaml",
                {
                    "version": 1,
                    "tables": [
                        {
                            "table": "Event",
                            "contract": "contracts/Event.yaml",
                            "route": "logs-ingestion-api",
                            "inputKind": "custom-stream",
                            "outputKind": "standard-table",
                            "outputStream": "Microsoft-Event",
                            "schemaReference": "https://learn.microsoft.com/azure/azure-monitor/reference/tables/event",
                            "metadataReference": "https://api.loganalytics.io/v1/metadata",
                            "capabilityReference": "https://learn.microsoft.com/azure/azure-monitor/reference/tables-features",
                            "routeReference": "https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview",
                            "liveValidated": False,
                        }
                    ],
                },
            )
            with mock.patch.object(generator, "REPOSITORY_ROOT", root), \
                    mock.patch.object(
                        generator,
                        "TABLE_ROOT",
                        root / "Sample Data" / "Tables",
                    ), \
                    mock.patch.object(
                        generator,
                        "MOCK_ROOT",
                        root / "Sample Data" / "Solutions" / "Mock",
                    ), \
                    mock.patch.object(
                        generator,
                        "STANDARD_CONTRACT_ROOT",
                        contracts,
                    ):
                result = generator.generate_scenario("Example", "rule-event")

            mock_records = json.loads(
                Path(result["mockPath"]).read_text(encoding="utf-8")
            )
            contract_path = Path(result["scenario"]["ingestion"]["contract"])
            manifest = result["scenario"]

        self.assertEqual("qualification-ready", result["scenario"]["generationStatus"])
        self.assertTrue(result["scenario"]["ingestion"]["directLogsIngestionSupported"])
        self.assertEqual("standard-dcr", result["scenario"]["ingestion"]["mode"])
        self.assertEqual("Custom-EventMock", result["scenario"]["ingestion"]["stream"])
        self.assertTrue(contract_path.name == "ingestion-contract.yaml")
        self.assertNotIn("TenantId", mock_records[0])
        self.assertEqual(root.resolve(), Path(manifest["toolkitRoot"]))
        self.assertEqual(
            (root / "Sample Data").resolve(),
            Path(manifest["sampleDataRoot"]),
        )

    def test_unsupported_standard_predicate_blocks_qualification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_root = root / "source"
            toolkit_root = Path(generator.__file__).resolve().parents[2]
            solution = source_root / "Solutions" / "Example"
            query = (
                'CommonSecurityLog | where DeviceEventClassID == "733101" '
                "| where DestinationUserName == 'alice'"
            )
            _write_yaml(
                solution / "Analytic Rules" / "rule.yaml",
                {
                    "id": "rule-csl-unsupported",
                    "name": "Common security event",
                    "query": query,
                    "triggerOperator": "gt",
                    "triggerThreshold": 0,
                },
            )
            _write_yaml(
                solution / "XDR Detections" / "rule.yaml",
                {
                    "id": "cd-csl-unsupported",
                    "sourceRuleId": "rule-csl-unsupported",
                    "name": "Common security event",
                    "query": query,
                },
            )
            package = solution / "Package" / "mainTemplate.json"
            package.parent.mkdir(parents=True)
            package.write_text('{"resources":[]}', encoding="utf-8")
            table = root / "Sample Data" / "Tables" / "CommonSecurityLog"
            table.mkdir(parents=True)
            (table / "base-event.json").write_text(
                json.dumps({
                    "DeviceEventClassID": "0",
                    "DestinationUserName": "synthetic-user",
                }),
                encoding="utf-8",
            )
            (table / "metadata.json").write_text(
                json.dumps({
                    "table": "CommonSecurityLog",
                    "schemaSource": "Microsoft public table schema",
                    "columns": {
                        "DeviceEventClassID": "string",
                        "DestinationUserName": "string",
                    },
                }),
                encoding="utf-8",
            )

            result = generator.generate_scenario(
                "Example",
                "rule-csl-unsupported",
                source_root=source_root,
                toolkit_root=toolkit_root,
                sample_data_root=root / "Sample Data",
                output_root=root / "output",
            )

            scenario = result["scenario"]
            record = json.loads(
                Path(result["mockPath"]).read_text(encoding="utf-8")
            )[0]

        self.assertEqual("generated-offline-only", scenario["generationStatus"])
        self.assertEqual("offline-standard-table", scenario["ingestion"]["mode"])
        self.assertFalse(scenario["ingestion"]["directLogsIngestionSupported"])
        self.assertEqual("733101", record["DeviceEventClassID"])
        self.assertEqual("alice", record["DestinationUserName"])
        self.assertTrue(
            any(
                "DestinationUserName" in blocker
                for blocker in scenario["ingestion"]["contractResolution"]["blockers"]
            )
        )

    def test_explicit_toolkit_root_selects_its_sample_data_by_default(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_root = root / "source"
            toolkit_root = root / "toolkit"
            solution = source_root / "Solutions" / "Example"
            _write_yaml(
                solution / "Analytic Rules" / "rule.yaml",
                {
                    "id": "rule-toolkit-sample",
                    "name": "Synthetic event",
                    "query": "Event | where EventID == 13",
                    "triggerOperator": "gt",
                    "triggerThreshold": 0,
                },
            )
            _write_yaml(
                solution / "XDR Detections" / "rule.yaml",
                {
                    "id": "cd-toolkit-sample",
                    "sourceRuleId": "rule-toolkit-sample",
                    "name": "Synthetic event",
                    "query": "Event | where EventID == 13",
                },
            )
            package = solution / "Package" / "mainTemplate.json"
            package.parent.mkdir(parents=True)
            package.write_text('{"resources":[]}', encoding="utf-8")
            registry_root = toolkit_root / "Tools" / "AzureMonitorLogsIngestion"
            _write_yaml(
                registry_root / "contracts" / "Event.yaml",
                {
                    "version": 1,
                    "name": "event-mock",
                    "workspace": "qualification-target",
                    "inputStream": "Custom-EventMock",
                    "inputColumns": [
                        {"name": "EventID", "type": "int"},
                        {"name": "Computer", "type": "string"},
                    ],
                    "transformKql": "source | project EventID=toint(EventID), Computer=tostring(Computer)",
                    "destination": {
                        "kind": "standard",
                        "table": "Event",
                        "outputStream": "Microsoft-Event",
                        "columns": [
                            {"name": "EventID", "type": "int"},
                            {"name": "Computer", "type": "string"},
                        ],
                    },
                    "resources": {"dce": "event-dce", "dcr": "event-dcr"},
                },
            )
            _write_yaml(
                registry_root / "registry.yaml",
                {
                    "version": 1,
                    "tables": [
                        {
                            "table": "Event",
                            "contract": "contracts/Event.yaml",
                            "route": "logs-ingestion-api",
                            "inputKind": "custom-stream",
                            "outputKind": "standard-table",
                            "outputStream": "Microsoft-Event",
                            "schemaReference": "https://example.invalid/schema",
                            "metadataReference": "https://example.invalid/metadata",
                            "capabilityReference": "https://example.invalid/capability",
                            "routeReference": "https://example.invalid/route",
                            "liveValidated": False,
                        }
                    ],
                },
            )
            sample_table = toolkit_root / "Sample Data" / "Tables" / "Event"
            sample_table.mkdir(parents=True)
            (sample_table / "base-event.json").write_text(
                json.dumps({"EventID": 0, "Computer": "toolkit-sample"}),
                encoding="utf-8",
            )
            (sample_table / "metadata.json").write_text(
                json.dumps({
                    "table": "Event",
                    "columns": {"EventID": "int", "Computer": "string"},
                }),
                encoding="utf-8",
            )
            decoy_table_root = source_root / "Sample Data" / "Tables"
            decoy_table_root.mkdir(parents=True)

            with mock.patch.object(generator, "TABLE_ROOT", decoy_table_root):
                result = generator.generate_scenario(
                    "Example",
                    "rule-toolkit-sample",
                    source_root=source_root,
                    toolkit_root=toolkit_root,
                    output_root=root / "output",
                )

            manifest = result["scenario"]
            record = json.loads(
                Path(result["mockPath"]).read_text(encoding="utf-8")
            )[0]

        self.assertEqual("qualification-ready", manifest["generationStatus"])
        self.assertEqual(toolkit_root.resolve(), Path(manifest["toolkitRoot"]))
        self.assertEqual(
            (toolkit_root / "Sample Data").resolve(),
            Path(manifest["sampleDataRoot"]),
        )
        self.assertEqual(13, record["EventID"])
        self.assertEqual("toolkit-sample", record["Computer"])

    def test_common_security_log_scenario_uses_registered_contract_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            solution = root / "Solutions" / "Example"
            _write_yaml(
                solution / "Analytic Rules" / "rule.yaml",
                {
                    "id": "rule-csl",
                    "name": "Common security event",
                    "query": (
                        'CommonSecurityLog | where DeviceEventClassID == "733101" '
                        "| where isempty(CommunicationDirection)"
                    ),
                    "triggerOperator": "gt",
                    "triggerThreshold": 0,
                },
            )
            _write_yaml(
                solution / "XDR Detections" / "rule.yaml",
                {
                    "id": "cd-csl",
                    "sourceRuleId": "rule-csl",
                    "name": "Common security event",
                    "query": (
                        'CommonSecurityLog | where DeviceEventClassID == "733101" '
                        "| where isempty(CommunicationDirection)"
                    ),
                },
            )
            package = solution / "Package" / "mainTemplate.json"
            package.parent.mkdir(parents=True)
            package.write_text('{"resources":[]}', encoding="utf-8")
            table = root / "Sample Data" / "Tables" / "CommonSecurityLog"
            table.mkdir(parents=True)
            (table / "base-event.json").write_text(
                json.dumps(
                    {
                        "TimeGenerated": "2026-09-17T00:00:00Z",
                        "DeviceEventClassID": "0",
                        "CommunicationDirection": "1",
                        "DeviceName": "firewall.example.invalid",
                        "SourceIP": "192.0.2.10",
                    }
                ),
                encoding="utf-8",
            )
            (table / "metadata.json").write_text(
                json.dumps(
                    {
                        "table": "CommonSecurityLog",
                        "schemaSource": "Microsoft Learn CommonSecurityLog reference",
                        "columns": {
                            "TimeGenerated": "datetime",
                            "DeviceEventClassID": "string",
                            "CommunicationDirection": "string",
                            "DeviceName": "string",
                            "SourceIP": "string",
                        },
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(generator, "REPOSITORY_ROOT", root), \
                    mock.patch.object(generator, "TABLE_ROOT", root / "Sample Data" / "Tables"), \
                    mock.patch.object(
                        generator,
                        "MOCK_ROOT",
                        root / "Sample Data" / "Solutions" / "Mock",
                    ):
                result = generator.generate_scenario(
                    "Example",
                    "rule-csl",
                    source_root=root,
                    toolkit_root=Path(generator.__file__).resolve().parents[2],
                    sample_data_root=root / "Sample Data",
                    output_root=root / "target" / "Sample Data" / "Solutions" / "Mock",
                )

            record = json.loads(Path(result["mockPath"]).read_text(encoding="utf-8"))[0]
            ingestion = result["scenario"]["ingestion"]

        self.assertEqual("qualification-ready", result["scenario"]["generationStatus"])
        self.assertEqual("standard-dcr", ingestion["mode"])
        self.assertEqual("Custom-XDRMigrationCommonSecurityLogMock", ingestion["stream"])
        self.assertEqual(
            "provisioning-plan",
            ingestion["contractResolution"]["status"],
        )
        self.assertFalse(ingestion["contractResolution"]["liveValidated"])
        self.assertTrue(ingestion["contractResolution"]["schemaFingerprint"])
        self.assertTrue(ingestion["contractResolution"]["transformFingerprint"])
        self.assertEqual("733101", record["DeviceEventClassID"])
        self.assertEqual("", record["CommunicationDirection"])
        self.assertEqual(
            (root / "target" / "Sample Data" / "Solutions" / "Mock").resolve(),
            Path(result["paths"]["outputRoot"]),
        )
        self.assertFalse((root / "Sample Data" / "Solutions" / "Mock").exists())

    def test_existing_scenario_rejects_changed_source_query_hash(self):
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
                generator.generate_scenario("Example", "rule-123")
                rule_path = root / "Solutions" / "Example" / "Analytic Rules" / "rule.yaml"
                changed_rule = dict(RULE)
                changed_rule["query"] = (
                    "ExampleParser\n| where EventMessage =~ 'Different activity'"
                )
                _write_yaml(rule_path, changed_rule)

                with self.assertRaisesRegex(generator.ScenarioError, "source hashes"):
                    generator.generate_scenario("Example", "rule-123")

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
