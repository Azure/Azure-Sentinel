from __future__ import annotations

import tempfile
import tomllib
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import yaml

from sentinel_xdr_migration.converter import (
    convert_solution,
    inspect_solution,
    runtime_validation_plan,
    validate_solution,
)
from sentinel_xdr_migration import __version__
from sentinel_xdr_migration.onboarding import doctor, setup
from sentinel_xdr_migration.runtime import (
    record_runtime_validation,
    validate_advanced_hunting,
)


RULE = """\
id: 11111111-2222-3333-4444-555555555555
name: Suspicious test activity
description: Detects a representative activity.
severity: High
queryFrequency: 1h
queryPeriod: 1h
tactics:
  - Discovery
relevantTechniques:
  - T1087
query: |
  DeviceEvents
  | where TimeGenerated > ago(1h)
  | project TimeGenerated, AccountUpn, IPAddress
entityMappings:
  - entityType: Account
    fieldMappings:
      - identifier: Upn
        columnName: AccountUpn
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: IPAddress
version: 1.0.0
kind: Scheduled
"""


class ConverterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.solution = Path(self.temp.name) / "Sample"
        rules = self.solution / "Analytic Rules"
        rules.mkdir(parents=True)
        (rules / "SampleRule.yaml").write_text(RULE, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_inspect_finds_analytic_rules(self) -> None:
        result = inspect_solution(self.solution)
        self.assertEqual(result["analyticRuleCount"], 1)
        self.assertEqual(result["existingXdrDetectionCount"], 0)

    def test_inspect_supports_legacy_analytics_rules_directory(self) -> None:
        legacy_solution = Path(self.temp.name) / "Legacy"
        rules = legacy_solution / "Analytics Rules"
        rules.mkdir(parents=True)
        (rules / "SampleRule.yaml").write_text(RULE, encoding="utf-8")

        result = inspect_solution(legacy_solution)

        self.assertEqual(result["analyticRuleCount"], 1)
        self.assertEqual(result["analyticRulesDirectory"], str(rules.resolve()))

    def test_convert_writes_versioned_provenance_and_disabled_detection(self) -> None:
        result = convert_solution(self.solution)
        self.assertEqual(result["converted"], 1)
        output = self.solution / "XDR Detections" / "SampleRule.yaml"
        document = yaml.safe_load(output.read_text(encoding="utf-8"))
        self.assertEqual(document["schemaVersion"], "1.0.0")
        self.assertEqual(document["resourceType"], "Microsoft.Security/detectionRules")
        self.assertEqual(document["properties"]["status"], "disabled")
        self.assertIn("Timestamp", document["properties"]["queryCondition"]["queryText"])
        self.assertEqual(
            document["contentProvenance"]["source"]["id"],
            "11111111-2222-3333-4444-555555555555",
        )
        self.assertEqual(
            document["contentProvenance"]["conversion"]["requiredWorkloads"], ["sentinel"]
        )
        self.assertFalse(document["contentProvenance"]["conversion"]["reviewRequired"])

    def test_validate_accepts_generated_detection(self) -> None:
        convert_solution(self.solution)
        result = validate_solution(self.solution)
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["invalid"], 0)

    def test_convert_generates_self_contained_html_report(self) -> None:
        result = convert_solution(self.solution)
        report = Path(result["transformationReport"])
        self.assertTrue(report.is_file())
        content = report.read_text(encoding="utf-8")
        self.assertIn("<!doctype html>", content)
        self.assertIn("Sentinel to XDR transformation report", content)
        self.assertIn("Suspicious test activity", content)
        self.assertIn("SampleRule.yaml", content)
        self.assertIn("converted", content)
        self.assertNotIn("https://", content)

    def test_convert_keeps_xdr_detections_yaml_only(self) -> None:
        result = convert_solution(self.solution)
        output = self.solution / "XDR Detections"

        self.assertEqual(
            ["SampleRule.yaml"],
            sorted(path.name for path in output.iterdir()),
        )
        self.assertTrue(Path(result["manifest"]).is_file())
        self.assertNotEqual(output, Path(result["manifest"]).parent)

    def test_converter_refuses_to_overwrite_different_content(self) -> None:
        convert_solution(self.solution)
        output = self.solution / "XDR Detections" / "SampleRule.yaml"
        output.write_text("changed: true\n", encoding="utf-8")
        result = convert_solution(self.solution)
        self.assertEqual(result["conflicts"], 1)

    def test_runtime_plan_pairs_source_and_converted_queries(self) -> None:
        convert_solution(self.solution)
        result = runtime_validation_plan(self.solution)
        self.assertEqual(len(result["rules"]), 1)
        self.assertIn("TimeGenerated", result["rules"][0]["sentinelQuery"])
        self.assertIn("Timestamp", result["rules"][0]["advancedHuntingQuery"])

    def test_explicit_mappings_are_applied(self) -> None:
        output = self.solution / "XDR Detections"
        output.mkdir()
        (output / "migration-config.yaml").write_text(
            """\
schemaVersion: 1.0.0
tableMappings:
  DeviceEvents: AlertEvidence
functionMappings: {}
columnMappings:
  DeviceEvents:
    AccountUpn: InitiatingProcessAccountUpn
""",
            encoding="utf-8",
        )
        convert_solution(self.solution)
        document = yaml.safe_load((output / "SampleRule.yaml").read_text(encoding="utf-8"))
        query = document["properties"]["queryCondition"]["queryText"]
        self.assertIn("AlertEvidence", query)
        self.assertIn("InitiatingProcessAccountUpn", query)
        account = document["properties"]["detectionAction"]["alertTemplate"][
            "entityMappings"
        ]["accounts"][0]
        self.assertEqual(
            account["upnColumn"],
            "InitiatingProcessAccountUpn",
        )
        validation = validate_solution(self.solution)
        self.assertEqual(validation["total"], 1)

    def test_missing_asset_mapping_requires_review(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = """\
DeviceEvents
| where TimeGenerated > ago(1h)
| project TimeGenerated, Url
"""
        document["entityMappings"] = [
            {
                "entityType": "URL",
                "fieldMappings": [{"identifier": "Url", "columnName": "Url"}],
            }
        ]
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        result = convert_solution(self.solution)
        self.assertEqual(result["needsReview"], 1)
        validation = validate_solution(self.solution)
        self.assertEqual(validation["invalid"], 1)

    def test_iso_frequency_is_preserved(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["queryFrequency"] = "PT30M"
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(output["properties"]["schedule"]["frequency"], "PT30M")

    def test_rewrites_skip_strings_and_comments(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = """\
DeviceEvents
| extend Label = "TimeGenerated" // TimeGenerated stays in this comment
| where TimeGenerated > ago(1h)
| project TimeGenerated, AccountUpn, IPAddress, Label
"""
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        query = output["properties"]["queryCondition"]["queryText"]
        self.assertIn('"TimeGenerated"', query)
        self.assertIn("// TimeGenerated stays in this comment", query)
        self.assertIn("| where Timestamp", query)

    def test_passthrough_table_preserves_timegenerated(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = """\
AzureActivity
| where TimeGenerated > ago(1h)
| project TimeGenerated, AccountUpn, IPAddress
"""
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        query = output["properties"]["queryCondition"]["queryText"]
        self.assertIn("TimeGenerated", query)
        self.assertNotIn("Timestamp", query)
        self.assertEqual(validate_solution(self.solution)["valid"], 1)

    def test_mixed_native_and_passthrough_query_preserves_branch_time_columns(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = """\
let Native = DeviceProcessEvents
| where Timestamp > ago(1h)
| project EventTime = Timestamp, AccountUpn, IPAddress;
let Sentinel = SecurityEvent
| where TimeGenerated > ago(1h)
| project EventTime = TimeGenerated, AccountUpn, IPAddress;
union Native, Sentinel
"""
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        result = convert_solution(self.solution)
        self.assertEqual(result["needsReview"], 1)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        query = output["properties"]["queryCondition"]["queryText"]
        self.assertIn("EventTime = Timestamp", query)
        self.assertIn("EventTime = TimeGenerated", query)

    def test_project_away_does_not_hide_passthrough_table_columns(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = """\
AzureActivity
| extend Temporary = parse_json(Properties)
| project-away Temporary
"""
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        mappings = output["properties"]["detectionAction"]["alertTemplate"]["entityMappings"]
        self.assertEqual(mappings["accounts"][0]["upnColumn"], "AccountUpn")
        self.assertEqual(mappings["ips"][0]["addressColumn"], "IPAddress")

    def test_externaldata_requires_runtime_review_but_is_structurally_valid(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] += (
            "\n| join kind=leftouter (externaldata(AccountUpn:string)"
            "['https://example.test/list.csv']) on AccountUpn\n"
        )
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        result = convert_solution(self.solution)
        self.assertEqual(result["needsReview"], 1)
        self.assertEqual(validate_solution(self.solution)["valid"], 1)

    def test_multiple_techniques_are_grouped(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["relevantTechniques"] = ["T1078", "T1078.004", "T1098"]
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        techniques = output["properties"]["detectionAction"]["alertTemplate"]["tactics"][0][
            "techniques"
        ]
        self.assertEqual(
            techniques,
            [
                {"technique": "T1078", "subTechniques": ["T1078.004"]},
                {"technique": "T1098"},
            ],
        )

    def test_multiple_tactics_require_an_explicit_rule_override(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["tactics"] = ["Persistence", "CommandAndControl"]
        document["relevantTechniques"] = ["T1505", "T1071"]
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

        result = convert_solution(self.solution)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(result["needsReview"], 1)
        tactic = output["properties"]["detectionAction"]["alertTemplate"]["tactics"][0]
        self.assertEqual(tactic, {"tactic": "Persistence"})

    def test_rule_override_selects_one_tactic_and_its_techniques(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["tactics"] = ["Persistence", "CommandAndControl"]
        document["relevantTechniques"] = ["T1505", "T1071"]
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        config = self.solution / "override.yaml"
        config.write_text(
            yaml.safe_dump(
                {
                    "ruleOverrides": {
                        document["id"]: {
                            "tactic": "Persistence",
                            "techniques": ["T1505"],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

        result = convert_solution(self.solution, config_path=config)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(result["converted"], 1)
        tactic = output["properties"]["detectionAction"]["alertTemplate"]["tactics"][0]
        self.assertEqual(
            tactic,
            {"tactic": "Persistence", "techniques": [{"technique": "T1505"}]},
        )
        conversion = output["contentProvenance"]["conversion"]
        self.assertEqual(
            conversion["originalTactics"], ["Persistence", "CommandAndControl"]
        )
        self.assertEqual(conversion["originalTechniques"], ["T1505", "T1071"])

    def test_rule_override_can_accept_a_runtime_validated_review(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] += "\n| union isfuzzy=true (DeviceEvents)\n"
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        reason = "isfuzzy unions can still fail semantic binding in Advanced Hunting"
        config = self.solution / "override.yaml"
        config.write_text(
            yaml.safe_dump(
                {
                    "ruleOverrides": {
                        document["id"]: {
                            "acceptedReviewReasons": [reason],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

        result = convert_solution(self.solution, config_path=config)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(result["converted"], 1)
        conversion = output["contentProvenance"]["conversion"]
        self.assertFalse(conversion["reviewRequired"])
        self.assertEqual(conversion["reviewReasons"], [])
        self.assertEqual(conversion["acceptedReviewReasons"], [reason])
        self.assertIn(reason, conversion["warnings"])

    def test_rule_override_can_supply_reviewed_entity_mappings(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["entityMappings"] = []
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        config = self.solution / "override.yaml"
        config.write_text(
            yaml.safe_dump(
                {
                    "ruleOverrides": {
                        document["id"]: {
                            "entityMappings": {
                                "ips": [
                                    {
                                        "id": "ip1",
                                        "addressColumn": "IPAddress",
                                    }
                                ]
                            }
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

        result = convert_solution(self.solution, config_path=config)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(result["converted"], 1)
        self.assertEqual(
            output["properties"]["detectionAction"]["alertTemplate"][
                "entityMappings"
            ],
            {"ips": [{"id": "ip1", "addressColumn": "IPAddress"}]},
        )

    def test_config_can_exclude_a_sentinel_only_rule(self) -> None:
        output = self.solution / "XDR Detections"
        output.mkdir()
        generated = output / "SampleRule.yaml"
        generated.write_text("stale generated output", encoding="utf-8")
        config = output / "migration-config.yaml"
        config.write_text(
            yaml.safe_dump(
                {
                    "excludedRuleIds": {
                        "11111111-2222-3333-4444-555555555555": (
                            "operational health rule has no affected asset"
                        )
                    }
                }
            ),
            encoding="utf-8",
        )

        result = convert_solution(self.solution, overwrite=True)

        self.assertEqual(result["converted"], 0)
        self.assertEqual(result["excluded"], 1)
        self.assertEqual(result["needsReview"], 0)
        self.assertFalse(generated.exists())
        self.assertEqual(result["results"][0]["status"], "excluded")

    def test_account_name_upn_alias_is_repaired(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = """\
AzureActivity
| project TimeGenerated, Caller, CallerIpAddress
"""
        document["entityMappings"] = [
            {
                "entityType": "Account",
                "fieldMappings": [{"identifier": "Name", "columnName": "Caller"}],
            },
            {
                "entityType": "IP",
                "fieldMappings": [
                    {"identifier": "Address", "columnName": "CallerIpAddress"}
                ],
            },
        ]
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        account = output["properties"]["detectionAction"]["alertTemplate"]["entityMappings"][
            "accounts"
        ][0]
        self.assertEqual(account["upnColumn"], "Caller")

    def test_mv_expand_assignment_is_a_projected_column(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = """\
AzureActivity
| summarize make_set(CallerIpAddress) by Caller
| mv-expand CallerIpAddress = set_CallerIpAddress
| project Caller, CallerIpAddress
"""
        document["entityMappings"] = [
            {
                "entityType": "Account",
                "fieldMappings": [{"identifier": "Name", "columnName": "Caller"}],
            },
            {
                "entityType": "IP",
                "fieldMappings": [
                    {"identifier": "Address", "columnName": "CallerIpAddress"}
                ],
            },
        ]
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        mappings = output["properties"]["detectionAction"]["alertTemplate"]["entityMappings"]
        self.assertEqual(mappings["ips"][0]["addressColumn"], "CallerIpAddress")

    def test_nrt_uses_supported_default_schedule_without_review(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["kind"] = "NRT"
        document.pop("queryFrequency")
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        result = convert_solution(self.solution)
        self.assertEqual(result["converted"], 1)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(output["properties"]["schedule"]["frequency"], "PT1H")

    @mock.patch(
        "sentinel_xdr_migration.runtime._advanced_hunting_token",
        return_value="token",
    )
    @mock.patch("sentinel_xdr_migration.runtime.run_advanced_hunting_query")
    def test_runtime_validation_distinguishes_unavailable_tables(
        self, run_query: mock.Mock, _token: mock.Mock
    ) -> None:
        convert_solution(self.solution)
        run_query.return_value = {
            "ok": False,
            "statusCode": 400,
            "rowCount": 0,
            "schema": [],
            "error": "table unavailable",
            "errorDetails": None,
        }
        result = validate_advanced_hunting(self.solution)
        self.assertEqual(result["blocked"], 1)
        self.assertEqual(result["invalid"], 0)
        self.assertEqual(result["provider"], "graph")
        self.assertEqual(result["results"][0]["status"], "blocked")
        self.assertTrue(Path(result["jsonReport"]).is_file())
        self.assertTrue(Path(result["htmlReport"]).is_file())

    @mock.patch(
        "sentinel_xdr_migration.runtime._advanced_hunting_token",
        return_value="token",
    )
    @mock.patch("sentinel_xdr_migration.runtime.run_advanced_hunting_query")
    def test_runtime_validation_ignores_migration_config(
        self, run_query: mock.Mock, _token: mock.Mock
    ) -> None:
        output = self.solution / "XDR Detections"
        output.mkdir()
        (output / "migration-config.yaml").write_text(
            "schemaVersion: 1.0.0\n",
            encoding="utf-8",
        )
        convert_solution(self.solution)
        run_query.return_value = {
            "ok": True,
            "statusCode": 200,
            "rowCount": 0,
            "schema": [],
            "error": None,
            "errorDetails": None,
        }

        result = validate_advanced_hunting(self.solution)

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["results"][0]["detection"], "SampleRule.yaml")

    @mock.patch(
        "sentinel_xdr_migration.runtime._advanced_hunting_token",
        return_value="token",
    )
    @mock.patch("sentinel_xdr_migration.runtime.run_advanced_hunting_query")
    def test_runtime_validation_preflights_solution_parser_functions(
        self, run_query: mock.Mock, _token: mock.Mock
    ) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = "ExampleParser | project Caller, CallerIpAddress"
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        parser_root = self.solution / "Parsers"
        parser_root.mkdir()
        (parser_root / "ExampleParser.yaml").write_text(
            yaml.safe_dump(
                {
                    "FunctionName": "ExampleParser",
                    "FunctionQuery": "Example_CL",
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        convert_solution(self.solution)
        run_query.return_value = {
            "ok": False,
            "statusCode": 400,
            "rowCount": 0,
            "schema": [],
            "error": "function unavailable",
            "errorDetails": None,
        }

        result = validate_advanced_hunting(self.solution)

        self.assertEqual(result["blocked"], 1)
        self.assertIn("ExampleParser", result["tableAvailability"])
        run_query.assert_called_once_with("ExampleParser | take 0", _token="token")

    def test_records_normalized_triage_mcp_results(self) -> None:
        convert_solution(self.solution)
        results_path = Path(self.temp.name) / "triage-results.json"
        results_path.write_text(
            """\
{
  "results": [
    {
      "detection": "SampleRule.yaml",
      "status": "passed",
      "statusCode": 200,
      "rowCount": 1,
      "schemaColumnCount": 3,
      "error": null
    }
  ]
}
""",
            encoding="utf-8",
        )
        result = record_runtime_validation(
            self.solution, provider="triage-mcp", results_path=results_path
        )
        self.assertEqual(result["provider"], "triage-mcp")
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["invalid"], 0)
        self.assertEqual(result["blocked"], 0)
        self.assertEqual(result["notRun"], 0)
        self.assertEqual(result["platform"], "Microsoft Sentinel Triage MCP")
        self.assertTrue(Path(result["jsonReport"]).is_file())
        html = Path(result["htmlReport"]).read_text(encoding="utf-8")
        self.assertIn("Provider: triage-mcp", html)
        self.assertIn("SampleRule.yaml", html)

    def test_records_log_analytics_results_and_not_run_status(self) -> None:
        convert_solution(self.solution)
        results_path = Path(self.temp.name) / "log-analytics-results.json"
        results_path.write_text(
            """\
{
  "results": [
    {
      "detection": "SampleRule.yaml",
      "status": "not-run",
      "statusCode": 0,
      "rowCount": 0,
      "schemaColumnCount": 0,
      "error": null
    }
  ]
}
""",
            encoding="utf-8",
        )
        result = record_runtime_validation(
            self.solution,
            provider="log-analytics-cli",
            results_path=results_path,
        )
        self.assertEqual(result["platform"], "Microsoft Sentinel Log Analytics")
        self.assertEqual(result["notRun"], 1)
        self.assertEqual(result["invalid"], 0)
        self.assertEqual(result["blocked"], 0)
        html = Path(result["htmlReport"]).read_text(encoding="utf-8")
        self.assertIn("Microsoft Sentinel Log Analytics runtime validation", html)
        self.assertIn("not-run", html)

    def test_package_and_provenance_versions_match(self) -> None:
        pyproject = tomllib.loads(
            (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(pyproject["project"]["version"], __version__)

    @mock.patch(
        "sentinel_xdr_migration.onboarding._advanced_hunting_status",
        return_value={
            "name": "advancedHunting",
            "status": "actionRequired",
            "detail": "sign-in required",
        },
    )
    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_doctor_reports_first_run_and_offline_fallback(
        self, _which: mock.Mock, _hunting: mock.Mock
    ) -> None:
        def runner(command, **_kwargs):
            if "get-access-token" in command:
                return CompletedProcess(command, 1, "", "login required")
            return CompletedProcess(command, 0, "", "")

        state_dir = Path(self.temp.name) / "state"
        result = doctor(state_dir=state_dir, runner=runner, environment={})
        self.assertTrue(result["firstRun"])
        self.assertEqual(result["mode"], "offline")
        self.assertTrue(result["conversionAvailable"])
        self.assertFalse(result["runtimeValidationAvailable"])

    @mock.patch(
        "sentinel_xdr_migration.onboarding._advanced_hunting_status",
        return_value={
            "name": "advancedHunting",
            "status": "actionRequired",
            "detail": "sign-in required",
        },
    )
    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_noninteractive_setup_persists_nonsecret_config(
        self, _which: mock.Mock, _hunting: mock.Mock
    ) -> None:
        def runner(command, **_kwargs):
            if "get-access-token" in command:
                return CompletedProcess(command, 1, "", "login required")
            return CompletedProcess(command, 0, "", "")

        state_dir = Path(self.temp.name) / "state"
        result = setup(
            interactive=False,
            tenant_id="tenant-id",
            workspace_id="workspace-id",
            state_dir=state_dir,
            runner=runner,
        )
        self.assertTrue(result["setupCompleted"])
        self.assertEqual(result["mode"], "offline")
        self.assertFalse(result["doctor"]["firstRun"])
        config = (state_dir / "config.json").read_text(encoding="utf-8")
        self.assertIn("tenant-id", config)
        self.assertIn("workspace-id", config)
        self.assertNotIn("token", config.lower())


if __name__ == "__main__":
    unittest.main()
