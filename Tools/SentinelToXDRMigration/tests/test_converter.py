from __future__ import annotations

import json
import hashlib
import tempfile
import tomllib
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import yaml
from sentinel_xdr_migration.artifacts import artifact_path

from sentinel_xdr_migration.converter import (
    convert_query,
    convert_solution,
    inspect_solution,
    runtime_validation_plan,
    validate_document,
    validate_solution,
)
from sentinel_xdr_migration import __version__
from sentinel_xdr_migration.onboarding import configure_workspace, doctor, setup
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
        self.assertEqual(document["version"], "3.1.0")
        self.assertEqual(document["contentProvenance"]["source"]["version"], "1.0.0")
        self.assertEqual(document["contentProvenance"]["conversion"]["version"], __version__)
        self.assertEqual(document["apiVersion"], "2026-06-01-preview")
        self.assertEqual((self.solution / "Analytic Rules/SampleRule.yaml").read_text(), RULE)
        self.assertEqual(document["resourceType"], "Microsoft.Security/detectionRules")
        self.assertEqual(document["properties"]["status"], "disabled")
        self.assertIn("Timestamp", document["properties"]["queryCondition"]["queryText"])
        self.assertEqual(
            document["contentProvenance"]["source"]["id"],
            "11111111-2222-3333-4444-555555555555",
        )
        self.assertEqual(
            f"xdr-{document['contentProvenance']['source']['id']}",
            document["properties"]["id"],
        )
        self.assertEqual(
            document["contentProvenance"]["conversion"]["requiredWorkloads"], ["sentinel"]
        )
        self.assertFalse(document["contentProvenance"]["conversion"]["reviewRequired"])

    def test_reconversion_preserves_independent_release_version(self) -> None:
        convert_solution(self.solution)
        output = self.solution / "XDR Detections/SampleRule.yaml"
        original = yaml.safe_load(output.read_text())
        for version in ("3.1.1", "3.9.0"):
            with self.subTest(version=version):
                output.write_text(output.read_text().replace(f"version: {original['version']}\n", f"version: {version}\n", 1))
                before = output.read_bytes()
                result = convert_solution(self.solution)
                self.assertEqual(0, result["conflicts"])
                self.assertEqual(before, output.read_bytes())
                source = self.solution / "Analytic Rules/SampleRule.yaml"
                source.write_text(RULE.replace("version: 1.0.0", "version: 1.0.3"))
                result = convert_solution(self.solution, overwrite=True)
                self.assertEqual(0, result["conflicts"])
                updated = yaml.safe_load(output.read_text())
                self.assertEqual(version, updated["version"])
                self.assertEqual("1.0.3", updated["contentProvenance"]["source"]["version"])
                self.assertEqual(original["properties"]["id"], updated["properties"]["id"])
                self.assertEqual(RULE.replace("version: 1.0.0", "version: 1.0.3"), source.read_text())
                original = updated

    def test_conversion_information_round_trips_yaml_and_manifest(self) -> None:
        source = self.solution / "Analytic Rules/SampleRule.yaml"
        source.write_text(RULE.replace("queryPeriod: 1h", "queryPeriod: 4h"), encoding="utf-8")
        summary = convert_solution(self.solution)
        document = yaml.safe_load((self.solution / "XDR Detections/SampleRule.yaml").read_text())
        conversion = document["contentProvenance"]["conversion"]
        manifest = json.loads(Path(summary["manifest"]).read_text())
        self.assertEqual("converted", conversion["status"])
        self.assertFalse(conversion["reviewRequired"])
        self.assertFalse(conversion["errors"])
        self.assertTrue(conversion["informational"])
        self.assertEqual(conversion["informational"], summary["results"][0]["informational"])
        self.assertEqual(conversion["informational"], manifest["results"][0]["informational"])

    def test_xdr_release_boundaries_in_schema_and_structural_validation(self) -> None:
        convert_solution(self.solution)
        output = self.solution / "XDR Detections/SampleRule.yaml"
        document = yaml.safe_load(output.read_text())
        for version, accepted in (("3.0.0", False), ("3.1.0", True), ("3.9.0", True),
                                  ("4.0.0", False), ("1.0.0", False), ("3.1", False),
                                  ("3.1.0.1", False), ("3.1.0-preview", False),
                                  ("", False), (None, False), (3.1, False)):
            with self.subTest(version=version):
                document["version"] = version
                errors = validate_document(document)
                self.assertEqual(accepted, not errors, errors)
                if not accepted:
                    self.assertTrue(any(error.startswith("schema:") for error in errors))
                    self.assertTrue(any("XDR top-level version" in error for error in errors))
        document.pop("version")
        errors = validate_document(document)
        self.assertTrue(any("'version' is a required property" in error for error in errors))
        self.assertTrue(any("reconvert with --overwrite" in error for error in errors))

    def test_reconversion_does_not_reset_invalid_or_unrelated_existing_release(self) -> None:
        convert_solution(self.solution)
        output = self.solution / "XDR Detections/SampleRule.yaml"
        original = yaml.safe_load(output.read_text())
        for version in ("3.0.0", "4.0.0", "", None):
            for overwrite in (False, True):
                with self.subTest(version=version, overwrite=overwrite):
                    document = dict(original, version=version)
                    output.write_text(yaml.safe_dump(document, sort_keys=False))
                    before = output.read_bytes()
                    result = convert_solution(self.solution, overwrite=overwrite)
                    self.assertEqual(1, result["conflicts"])
                    self.assertEqual(before, output.read_bytes())
                    self.assertIn("XDR top-level version", result["results"][0]["errors"][0])
        original["contentProvenance"]["source"]["id"] = "different-source"
        output.write_text(yaml.safe_dump(original, sort_keys=False))
        before = output.read_bytes()
        result = convert_solution(self.solution, overwrite=True)
        self.assertEqual(1, result["conflicts"])
        self.assertEqual(before, output.read_bytes())
        self.assertIn("different source rule", result["results"][0]["errors"][0])

    def test_legacy_detection_requires_explicit_reconversion(self) -> None:
        convert_solution(self.solution)
        output = self.solution / "XDR Detections/SampleRule.yaml"
        document = yaml.safe_load(output.read_text())
        document.pop("version")
        output.write_text(yaml.safe_dump(document, sort_keys=False))
        before = output.read_bytes()
        self.assertEqual(1, validate_solution(self.solution)["invalid"])
        self.assertEqual(1, convert_solution(self.solution)["conflicts"])
        self.assertEqual(before, output.read_bytes())
        self.assertEqual(0, convert_solution(self.solution, overwrite=True)["conflicts"])
        updated = yaml.safe_load(output.read_text())
        self.assertEqual("3.1.0", updated["version"])
        self.assertEqual(document["contentProvenance"], updated["contentProvenance"])
        self.assertEqual(1, validate_solution(self.solution)["valid"])

    def test_validate_accepts_generated_detection(self) -> None:
        convert_solution(self.solution)
        result = validate_solution(self.solution)
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["invalid"], 0)

    def test_conversion_does_not_require_event_time_output(self) -> None:
        queries = (
            "DeviceEvents",
            "DeviceEvents | project DeviceName",
            "DeviceEvents | summarize Events=count() by DeviceName",
            "DeviceEvents | project EventTime=Timestamp, DeviceName",
            "DeviceEvents | where Timestamp > ago(1h) | project DeviceName",
            "DeviceEvents | project-away Timestamp",
            "SecurityEvent | project Computer",
        )
        for query in queries:
            with self.subTest(query=query):
                converted, warnings, errors = convert_query(query, {})
                self.assertEqual(query, converted)
                self.assertEqual([], errors)
                self.assertEqual([], warnings)

    def test_detection_without_event_time_passes_conversion_and_structure(self) -> None:
        source = self.solution / "Analytic Rules/SampleRule.yaml"
        rule = yaml.safe_load(RULE)
        rule["query"] = "DeviceEvents | project AccountUpn, IPAddress"
        source.write_text(yaml.safe_dump(rule), encoding="utf-8")

        result = convert_solution(self.solution)
        self.assertEqual(1, result["converted"])
        self.assertEqual(0, result["needsReview"])
        output = self.solution / "XDR Detections/SampleRule.yaml"
        document = yaml.safe_load(output.read_text(encoding="utf-8"))
        self.assertEqual(rule["query"], document["properties"]["queryCondition"]["queryText"])
        self.assertEqual([], validate_document(document))
        conversion = document["contentProvenance"]["conversion"]
        self.assertEqual("converted", conversion["status"])
        self.assertEqual("default-native-lookback", conversion["eventTimeWindow"]["status"])
        self.assertEqual("PT4H", conversion["eventTimeWindow"]["effectiveLookback"])
        self.assertFalse(conversion["eventTimeWindow"]["filterInjected"])

        # For a non-1h lookback that is still narrower than the 4h service window,
        # missing an event-time column continues to require review.
        rule["queryPeriod"] = "2h"
        source.write_text(yaml.safe_dump(rule), encoding="utf-8")
        result_2h = convert_solution(self.solution, overwrite=True)
        self.assertEqual(0, result_2h["converted"])
        self.assertEqual(1, result_2h["needsReview"])
        document_2h = yaml.safe_load(output.read_text(encoding="utf-8"))
        self.assertEqual([], validate_document(document_2h))
        conversion_2h = document_2h["contentProvenance"]["conversion"]
        self.assertEqual("needsReview", conversion_2h["status"])
        self.assertTrue(any(
            "source query does not establish an event-time column" in reason
            for reason in conversion_2h["reviewReasons"]
        ))

    def test_other_query_blockers_remain_without_event_time(self) -> None:
        _, _, errors = convert_query(
            'workspace("other").DeviceEvents | project DeviceName', {}
        )
        self.assertEqual(["cross-workspace queries require manual redesign"], errors)

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
        self.assertNotRegex(content, r"(?is)<(?:script|img|iframe|source|video|audio|embed)\b[^>]*\bsrc\s*=")
        self.assertNotRegex(content, r"(?is)<link\b[^>]*\brel\s*=\s*[\"'](?:stylesheet|preload|modulepreload)")
        self.assertNotRegex(content, r"(?i)@import\b|url\s*\(")

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
        self.assertEqual(
            hashlib.sha256(result["rules"][0]["sentinelQuery"].encode()).hexdigest(),
            result["rules"][0]["sentinelQuerySha256"],
        )
        self.assertEqual(
            hashlib.sha256(result["rules"][0]["advancedHuntingQuery"].encode()).hexdigest(),
            result["rules"][0]["advancedHuntingQuerySha256"],
        )

    def test_explicit_mappings_are_applied(self) -> None:
        output = self.solution / "XDR Detections"
        output.mkdir()
        artifact_path(self.solution, "migration-config.yaml", create_parent=True).write_text(
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
        document["requiredDataConnectors"] = [
            {"connectorId": "AzureActivity", "dataTypes": ["AzureActivity"]},
        ]
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
        document["tactics"] = ["Persistence"]
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

    def test_multiple_tactics_preserved_without_rule_override(self) -> None:
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

        self.assertEqual(result["needsReview"], 0)
        self.assertEqual(result["deploymentReady"], 0)
        self.assertEqual(output["properties"]["detectionAction"]["alertTemplate"]["tactics"], [
            {"tactic": "Persistence", "techniques": [{"technique": "T1505"}]},
            {"tactic": "CommandAndControl", "techniques": [{"technique": "T1071"}]},
        ])

    def test_rule_override_changes_named_tactic_techniques_without_narrowing(self) -> None:
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
        self.assertEqual(
            output["properties"]["detectionAction"]["alertTemplate"]["tactics"][1],
            {"tactic": "CommandAndControl", "techniques": [{"technique": "T1071"}]},
        )
        conversion = output["contentProvenance"]["conversion"]
        self.assertEqual(
            conversion["originalTactics"], ["Persistence", "CommandAndControl"]
        )
        self.assertEqual(conversion["originalTechniques"], ["T1505", "T1071"])

    def test_rule_override_acceptance_is_explicit_and_hash_scoped(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["queryPeriod"] = "4h"
        document["query"] += "\n| union isfuzzy=true (DeviceEvents)\n"
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        reason = "isfuzzy unions can still fail semantic binding in Advanced Hunting"
        convert_solution(self.solution)
        output_path = self.solution / "XDR Detections" / "SampleRule.yaml"
        current = yaml.safe_load(output_path.read_text(encoding="utf-8"))
        scope = current["contentProvenance"]["conversion"]["reviewScope"]
        config = self.solution / "override.yaml"
        config.write_text(
            yaml.safe_dump(
                {
                    "ruleOverrides": {
                        document["id"]: {
                            "reviewDecisions": [{
                                "reason": reason,
                                "decision": "accepted",
                                **scope,
                            }],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

        result = convert_solution(self.solution, overwrite=True, config_path=config)
        output = yaml.safe_load(output_path.read_text(encoding="utf-8"))

        self.assertEqual(result["converted"], 1)
        conversion = output["contentProvenance"]["conversion"]
        self.assertFalse(conversion["reviewRequired"])
        self.assertEqual(conversion["reviewReasons"], [])
        self.assertEqual(conversion["acceptedReviewReasons"], [reason])
        self.assertEqual(conversion["reviewDecisions"][0]["decision"], "accepted")
        self.assertIn(reason, conversion["warnings"])

    def test_review_approval_expires_when_converted_query_hash_changes(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["queryPeriod"] = "4h"
        document["query"] = 'DeviceEvents | search "needle"'
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution)
        output_path = self.solution / "XDR Detections" / "SampleRule.yaml"
        current = yaml.safe_load(output_path.read_text(encoding="utf-8"))
        conversion = current["contentProvenance"]["conversion"]
        reason = "search queries should be replaced with explicit tables"
        self.assertIn(reason, conversion["reviewReasons"])
        scope = conversion["reviewScope"]
        config = self.solution / "changed-target.yaml"
        config.write_text(yaml.safe_dump({
            "schemaVersion": "1.0.0",
            "tableMappings": {"DeviceEvents": "AlertEvidence"},
            "ruleOverrides": {
                document["id"]: {
                    "reviewDecisions": [{
                        "reason": reason,
                        "decision": "accepted",
                        **scope,
                    }],
                },
            },
        }), encoding="utf-8")

        result = convert_solution(self.solution, overwrite=True, config_path=config)
        updated = yaml.safe_load(output_path.read_text(encoding="utf-8"))
        conversion = updated["contentProvenance"]["conversion"]
        self.assertEqual(1, result["needsReview"])
        self.assertTrue(conversion["reviewRequired"])
        self.assertTrue(any("reviewDecision" in error and "stale" in error for error in conversion["errors"]))
        self.assertNotEqual(
            scope["targetQuerySha256"],
            conversion["reviewScope"]["targetQuerySha256"],
        )

    def test_review_decisions_reject_unscoped_and_stale_acceptance(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] += "\n| union isfuzzy=true (DeviceEvents)\n"
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        reason = "isfuzzy unions can still fail semantic binding in Advanced Hunting"
        unscoped = self.solution / "unscoped.yaml"
        unscoped.write_text(yaml.safe_dump({
            "ruleOverrides": {document["id"]: {"acceptedReviewReasons": [reason]}}
        }), encoding="utf-8")
        convert_solution(self.solution, config_path=unscoped)
        output_path = self.solution / "XDR Detections" / "SampleRule.yaml"
        result = yaml.safe_load(output_path.read_text(encoding="utf-8"))
        conversion = result["contentProvenance"]["conversion"]
        self.assertTrue(conversion["reviewRequired"])
        self.assertTrue(any("is unscoped" in error for error in conversion["errors"]))

        first = convert_solution(self.solution, overwrite=True)
        output = yaml.safe_load(output_path.read_text(encoding="utf-8"))
        scope = output["contentProvenance"]["conversion"]["reviewScope"]
        scoped = self.solution / "scoped.yaml"
        scoped.write_text(yaml.safe_dump({
            "ruleOverrides": {document["id"]: {"reviewDecisions": [{
                "reason": reason, "decision": "accepted", **scope,
            }]}}
        }), encoding="utf-8")
        document["description"] = "changed source content invalidates the decision"
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        convert_solution(self.solution, overwrite=True, config_path=scoped)
        output = yaml.safe_load(output_path.read_text(encoding="utf-8"))
        conversion = output["contentProvenance"]["conversion"]
        self.assertTrue(conversion["reviewRequired"])
        self.assertTrue(any("is stale" in error for error in conversion["errors"]))

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
        convert_solution(self.solution)
        output = self.solution / "XDR Detections"
        generated = output / "SampleRule.yaml"
        config = artifact_path(self.solution, "migration-config.yaml", create_parent=True)
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
        self.assertEqual(output["kind"], "CustomDetection")
        self.assertEqual(output["properties"]["schedule"]["frequency"], "PT0S")
        self.assertEqual([], validate_document(output))

    def test_nrt_incompatible_query_requires_review_instead_of_silent_schedule(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["kind"] = "NRT"
        document.pop("queryFrequency")
        document["query"] = (
            "DeviceEvents | summarize Count = count() by AccountUpn, IPAddress, Timestamp"
        )
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        result = convert_solution(self.solution)
        self.assertEqual(result["converted"], 0)
        self.assertEqual(result["needsReview"], 1)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(output["properties"]["schedule"]["frequency"], "PT0S")
        conversion = output["contentProvenance"]["conversion"]
        self.assertEqual(conversion["status"], "needsReview")
        self.assertTrue(conversion["reviewRequired"])
        self.assertTrue(
            any("not eligible for Continuous (NRT)" in r for r in conversion["reviewReasons"])
        )

    def test_standard_builtin_asim_parsers_allowed_in_detections(self) -> None:
        for query in (
            "_ASim_NetworkSession | where TimeGenerated > ago(1h) | project AccountUpn=SrcUsername, IPAddress=SrcIpAddr",
            "_Im_WebSession(url_has_any=dynamic(['example.com'])) | where TimeGenerated > ago(1h) | project AccountUpn=SrcUsername, IPAddress=SrcIpAddr",
        ):
            with self.subTest(query=query):
                converted, warnings, errors = convert_query(query, {})
                self.assertEqual([], errors)
                self.assertEqual([], warnings)
                self.assertEqual(query, converted)

    def test_solution_release_version_inheritance_and_source_version_lexical_preservation(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        raw = path.read_text(encoding="utf-8").replace("version: 1.0.0", "version: 1.0")
        path.write_text(raw, encoding="utf-8")
        data_dir = self.solution / "Data"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "Solution_Sample.json").write_text(
            json.dumps({"Name": "Sample", "Version": "3.2.1"}),
            encoding="utf-8",
        )
        result = convert_solution(self.solution, overwrite=True)
        self.assertEqual(result["converted"], 1)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(output["version"], "3.2.1")
        self.assertEqual(output["contentProvenance"]["source"]["version"], "1.0")

    def test_entity_identity_rejects_synthetic_hash_and_filename_only_hash_bindings(self) -> None:
        path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["query"] = (
            'DeviceEvents\n'
            '| where TimeGenerated > ago(1h)\n'
            '| extend Algorithm = "SHA256"\n'
            '| extend FileEntity = strcat("See_auditd_events_for_details_", tostring(hash(AccountUpn)))\n'
            '| project Timestamp = TimeGenerated, AccountUpn, IPAddress, Algorithm, FileEntity, FileName\n'
        )
        document["entityMappings"].append(
            {
                "entityType": "FileHash",
                "fieldMappings": [
                    {"identifier": "Algorithm", "columnName": "Algorithm"},
                    {"identifier": "Value", "columnName": "FileEntity"},
                ],
            }
        )
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        result = convert_solution(self.solution, overwrite=True)
        self.assertEqual(result["converted"], 0)
        self.assertEqual(result["needsReview"], 1)
        output = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(encoding="utf-8")
        )
        conversion = output["contentProvenance"]["conversion"]
        self.assertTrue(
            any("genuine content SHA-1/SHA-256 is required" in r for r in conversion["reviewReasons"])
        )

    @mock.patch(
        "sentinel_xdr_migration.runtime._advanced_hunting_token",
        return_value="token",
    )
    @mock.patch("sentinel_xdr_migration.runtime.run_advanced_hunting_query")
    def test_runtime_validation_reports_query_failure_without_table_probes(
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
        self.assertEqual(result["blocked"], 0)
        self.assertEqual(result["invalid"], 1)
        self.assertEqual(result["provider"], "graph")
        self.assertEqual(result["results"][0]["status"], "failed")
        expected_query = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(
                encoding="utf-8"
            )
        )["properties"]["queryCondition"]["queryText"]
        run_query.assert_called_once_with(expected_query, _token="token")
        self.assertEqual({}, result["tableAvailability"])
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
        artifact_path(self.solution, "migration-config.yaml", create_parent=True).write_text(
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
        self.assertEqual(
            hashlib.sha256(
                yaml.safe_load(
                    (self.solution / "XDR Detections/SampleRule.yaml").read_text()
                )["properties"]["queryCondition"]["queryText"].encode()
            ).hexdigest(),
            result["results"][0]["querySha256"],
        )

    @mock.patch(
        "sentinel_xdr_migration.runtime._advanced_hunting_token",
        return_value="token",
    )
    @mock.patch("sentinel_xdr_migration.runtime.run_advanced_hunting_query")
    def test_runtime_validation_queries_parser_function_without_probe(
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
            "ok": True,
            "statusCode": 200,
            "rowCount": 0,
            "schema": [],
            "error": None,
            "errorDetails": None,
        }

        result = validate_advanced_hunting(self.solution)

        expected_query = yaml.safe_load(
            (self.solution / "XDR Detections" / "SampleRule.yaml").read_text(
                encoding="utf-8"
            )
        )["properties"]["queryCondition"]["queryText"]
        self.assertEqual(result["valid"], 1)
        run_query.assert_called_once_with(expected_query, _token="token")
        self.assertNotEqual(expected_query, "ExampleParser | take 0")

    def test_records_normalized_triage_mcp_results(self) -> None:
        convert_solution(self.solution)
        source_query_hash = hashlib.sha256(
            yaml.safe_load((self.solution / "Analytic Rules/SampleRule.yaml").read_text())["query"].encode()
        ).hexdigest()
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
      "querySha256": "%s",
      "schemaColumnCount": 3,
      "error": null
    }
  ]
}
""" % source_query_hash,
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
        self.assertEqual(result["querySurface"], "microsoft-sentinel-triage")
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
        self.assertEqual(result["querySurface"], "log-analytics-workspace")
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

    def test_configured_workspace_is_reusable_across_solutions(self) -> None:
        state_dir = Path(self.temp.name) / "state"
        resource_id = (
            "/subscriptions/subscription-id/resourceGroups/resource-group/providers/"
            "Microsoft.OperationalInsights/workspaces/lab-workspace"
        )

        configured = configure_workspace(
            resource_id,
            workspace_customer_id="customer-id",
            state_dir=state_dir,
        )

        self.assertEqual("configured", configured["status"])
        config = json.loads(
            (state_dir / "config.json").read_text(encoding="utf-8")
        )
        self.assertEqual(resource_id, config["workspaceResourceId"])
        self.assertEqual("customer-id", config["workspaceId"])

    @mock.patch(
        "sentinel_xdr_migration.onboarding._advanced_hunting_status",
        return_value={
            "name": "advancedHunting",
            "status": "ready",
            "detail": "ready",
        },
    )
    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_doctor_returns_configured_workspace_for_confirmation(
        self,
        _which: mock.Mock,
        _hunting: mock.Mock,
    ) -> None:
        def runner(command, **_kwargs):
            return CompletedProcess(command, 0, "", "")

        state_dir = Path(self.temp.name) / "state"
        resource_id = (
            "/subscriptions/subscription-id/resourceGroups/resource-group/providers/"
            "Microsoft.OperationalInsights/workspaces/lab-workspace"
        )
        configure_workspace(
            resource_id,
            workspace_customer_id="customer-id",
            tenant_id="tenant-id",
            subscription_id="subscription-id",
            state_dir=state_dir,
        )

        result = doctor(state_dir=state_dir, runner=runner, environment={})

        self.assertEqual(resource_id, result["configuredWorkspaceResourceId"])
        self.assertEqual("customer-id", result["configuredWorkspaceCustomerId"])
        self.assertEqual("tenant-id", result["configuredTenantId"])
        self.assertEqual("subscription-id", result["configuredSubscriptionId"])


if __name__ == "__main__":
    unittest.main()
