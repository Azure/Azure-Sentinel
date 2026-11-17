from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration.artifacts import artifact_path, using_run
from sentinel_xdr_migration.cli import main
from sentinel_xdr_migration.converter import convert_solution, validate_solution
from sentinel_xdr_migration.packaging import package_solution_v3_1
from sentinel_xdr_migration.solution_report import build_solution_report
from sentinel_xdr_migration.workflow import (
    complete_workflow_stage,
    initialize_workflow,
    start_workflow_stage,
    workflow_status,
)
from test_connector_metadata import CONNECTORS
from test_converter import RULE


SOURCE_ID = "ABCDEF12-2222-3333-4444-555555555555"
OTHER_ID = "abcdef12-2222-3333-4444-666666666666"
UNKNOWN_ID = "abcdef12-2222-3333-4444-777777777777"


class RuleScopedConversionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.fixture.cleanup)
        self.solution = Path(self.fixture.name)
        self.source = self.solution / "Analytic Rules/Execution/Rule.YML"
        self.other_source = self.solution / "Analytic Rules/Discovery/Rule.yaml"
        for path, rule_id in ((self.source, SOURCE_ID), (self.other_source, OTHER_ID)):
            path.parent.mkdir(parents=True)
            path.write_text(RULE.replace("11111111-2222-3333-4444-555555555555", rule_id))
        self.output = self.solution / "XDR Detections/Execution/Rule.YML"
        self.other_output = self.solution / "XDR Detections/Discovery/Rule.yaml"

    def snapshot(self):
        return {
            path.relative_to(self.solution).as_posix(): path.read_bytes() if path.is_file() else None
            for path in self.solution.rglob("*")
        }

    def config(self, exclusions):
        path = self.solution / "config.json"
        path.write_text(json.dumps({"excludedRuleIds": exclusions}))
        return path

    def test_new_selected_output_preserves_nested_unselected_exclusion(self):
        self.other_output.parent.mkdir(parents=True)
        draft = b"# unrelated draft retained exactly\r\nmanual: true\r\n"
        self.other_output.write_bytes(draft)
        config = self.config({OTHER_ID: "not part of pilot"})
        sources_before = self.source.read_bytes(), self.other_source.read_bytes()
        result = convert_solution(
            self.solution, rule_id=SOURCE_ID.lower(), config_path=config, overwrite=True,
        )
        self.assertEqual(1, result["total"])
        self.assertEqual(1, result["converted"])
        self.assertEqual(0, result["excluded"])
        self.assertEqual(draft, self.other_output.read_bytes())
        self.assertEqual(sources_before, (self.source.read_bytes(), self.other_source.read_bytes()))
        document = yaml.safe_load(self.output.read_text())
        self.assertEqual(f"xdr-{SOURCE_ID}", document["properties"]["id"])
        self.assertEqual("disabled", document["properties"]["status"])
        self.assertEqual({
            "kind": "rule", "ruleIds": [SOURCE_ID], "sourceTotal": 2, "selectedTotal": 1,
        }, result["scope"])
        manifest = json.loads(Path(result["manifest"]).read_text())
        self.assertEqual(result["scope"], manifest["scope"])
        self.assertEqual("XDR Detections/Execution/Rule.YML", manifest["results"][0]["outputRelativePath"])
        self.assertIn("not full-solution", Path(result["transformationReport"]).read_text())

    def test_refresh_preserves_unselected_bytes_version_identity_and_connectors(self):
        convert_solution(self.solution)
        original = yaml.safe_load(self.output.read_text())
        original["version"] = "3.1.7"
        self.output.write_text(yaml.safe_dump(original, sort_keys=False))
        source = yaml.safe_load(self.source.read_text())
        source["name"] = "Renamed pilot"
        source["requiredDataConnectors"] = CONNECTORS
        source["query"] += "| where AccountUpn != ''\n"
        self.source.write_text(yaml.safe_dump(source, sort_keys=False))
        before = self.output.read_bytes(), self.other_output.read_bytes()
        config = self.config({OTHER_ID: "leave draft alone"})
        result = convert_solution(self.solution, rule_id=SOURCE_ID, config_path=config)
        self.assertEqual(1, result["conflicts"])
        self.assertEqual(before, (self.output.read_bytes(), self.other_output.read_bytes()))
        result = convert_solution(self.solution, rule_id=SOURCE_ID, config_path=config, overwrite=True)
        self.assertEqual(0, result["conflicts"])
        self.assertEqual(before[1], self.other_output.read_bytes())
        updated = yaml.safe_load(self.output.read_text())
        self.assertEqual("3.1.7", updated["version"])
        self.assertEqual(f"xdr-{SOURCE_ID}", updated["properties"]["id"])
        self.assertEqual(CONNECTORS, updated["requiredDataConnectors"])
        self.assertEqual(
            hashlib.sha256(source["query"].encode()).hexdigest(),
            updated["contentProvenance"]["source"]["querySha256"],
        )
        self.assertNotEqual(
            original["contentProvenance"]["source"]["querySha256"],
            updated["contentProvenance"]["source"]["querySha256"],
        )
        updated["requiredDataConnectors"][0]["extension"]["labels"].append("local edit")
        self.assertEqual(CONNECTORS, yaml.safe_load(self.source.read_text())["requiredDataConnectors"])
        self.assertEqual(1, len(json.loads(Path(result["manifest"]).read_text())["results"]))
        self.assertEqual("rule", validate_solution(self.solution)["conversionScope"]["kind"])

    def test_invalid_selector_is_atomic_with_and_without_existing_artifacts(self):
        for existing in (False, True):
            if existing:
                convert_solution(self.solution)
            for rule_id in ("", "not-a-guid", SOURCE_ID.replace("-", ""), SOURCE_ID + " ", UNKNOWN_ID):
                with self.subTest(existing=existing, rule_id=rule_id):
                    before = self.snapshot()
                    with self.assertRaises(ValueError):
                        convert_solution(self.solution, rule_id=rule_id, overwrite=True)
                    self.assertEqual(before, self.snapshot())
                    with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                        self.assertEqual(2, main([
                            "convert", "--solution", str(self.solution),
                            "--rule-id", rule_id, "--overwrite",
                        ]))
                    self.assertEqual(before, self.snapshot())

    def test_duplicate_case_variant_and_zero_match_fail_before_writes(self):
        self.other_source.write_text(self.source.read_text().replace(SOURCE_ID, SOURCE_ID.lower()))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "found 2"):
            convert_solution(self.solution, rule_id=SOURCE_ID, overwrite=True)
        self.assertEqual(before, self.snapshot())
        self.source.unlink()
        self.other_source.unlink()
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "found 0"):
            convert_solution(self.solution, rule_id=SOURCE_ID, overwrite=True)
        self.assertEqual(before, self.snapshot())

    def test_cli_rejects_repeated_selectors_before_writes(self):
        for second in (SOURCE_ID, OTHER_ID):
            before = self.snapshot()
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main(["convert", "--solution", str(self.solution),
                      "--rule-id", SOURCE_ID, "--rule-id", second])
            self.assertEqual(2, error.exception.code)
            self.assertEqual(before, self.snapshot())

    def test_selected_exclusion_is_never_deleted_or_reported_success(self):
        for existing in (False, True):
            if existing:
                convert_solution(self.solution)
            for excluded_id in (SOURCE_ID, SOURCE_ID.lower()):
                for reason in ("not supported", None):
                    config = self.config({excluded_id: reason})
                    before = self.snapshot()
                    with self.assertRaisesRegex(ValueError, "excluded rule"):
                        convert_solution(
                            self.solution, rule_id=SOURCE_ID, config_path=config, overwrite=True,
                        )
                    self.assertEqual(before, self.snapshot())
                    with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                        self.assertEqual(2, main([
                            "convert", "--solution", str(self.solution), "--rule-id", SOURCE_ID,
                            "--config", str(config), "--overwrite",
                        ]))
                    self.assertEqual(before, self.snapshot())

    def test_unselected_output_identity_and_provenance_collisions_still_block(self):
        convert_solution(self.solution)
        other = yaml.safe_load(self.other_output.read_text())
        for field in ("id", "provenance"):
            document = json.loads(json.dumps(other))
            if field == "id":
                document["properties"]["id"] = SOURCE_ID.lower()
            else:
                document["contentProvenance"]["source"]["id"] = SOURCE_ID
            self.other_output.write_text(yaml.safe_dump(document))
            before = self.output.read_bytes(), self.other_output.read_bytes()
            result = convert_solution(self.solution, rule_id=SOURCE_ID, overwrite=True)
            self.assertEqual(1, result["conflicts"])
            self.assertEqual(before, (self.output.read_bytes(), self.other_output.read_bytes()))

    def test_relocated_and_custom_identity_outputs_are_not_replaced(self):
        convert_solution(self.solution)
        relocated = self.output.parents[1] / self.output.name
        self.output.rename(relocated)
        result = convert_solution(self.solution, rule_id=SOURCE_ID, overwrite=True)
        self.assertEqual(1, result["conflicts"])
        self.assertFalse(self.output.exists())
        relocated.rename(self.output)
        document = yaml.safe_load(self.output.read_text())
        document["properties"]["id"] = "hand-authored-id"
        self.output.write_text(yaml.safe_dump(document))
        before = self.output.read_bytes()
        self.assertEqual(1, convert_solution(self.solution, rule_id=SOURCE_ID, overwrite=True)["conflicts"])
        self.assertEqual(before, self.output.read_bytes())

    def test_default_full_conversion_retains_exclusion_behavior(self):
        convert_solution(self.solution, rule_id=SOURCE_ID)
        result = convert_solution(self.solution)
        self.assertEqual(2, result["total"])
        self.assertEqual("solution", result["scope"]["kind"])
        self.assertTrue(self.other_output.exists())
        result = convert_solution(self.solution, config_path=self.config({OTHER_ID: "exclude"}), overwrite=True)
        self.assertEqual(1, result["converted"])
        self.assertEqual(1, result["excluded"])
        self.assertFalse(self.other_output.exists())
        self.assertTrue(self.output.exists())

    def test_solution_report_exposes_partial_scope_and_unselected_not_run(self):
        convert_solution(self.solution)
        convert_solution(self.solution, rule_id=SOURCE_ID)
        report = build_solution_report(self.solution)
        self.assertEqual("rule", report["summary"]["conversionScope"]["kind"])
        self.assertEqual(2, report["summary"]["rules"])
        self.assertEqual(1, report["summary"]["converted"])
        self.assertEqual(
            ["converted", "not-run"],
            sorted(rule["customDetection"]["conversionStatus"] for rule in report["rules"]),
        )
        self.assertIn("Rule-scoped conversion only", Path(report["htmlReport"]).read_text())
        self.assertIn(SOURCE_ID, Path(report["htmlReport"]).read_text())

    def test_scoped_legacy_id_transition_preserves_release_and_connector_metadata(self):
        convert_solution(self.solution)
        document = yaml.safe_load(self.output.read_text())
        document["properties"]["id"] = "xdr-suspicious-test-activity-" + SOURCE_ID[:8]
        document["version"] = "3.1.9"
        self.output.write_text(yaml.safe_dump(document, sort_keys=False))
        before = self.other_output.read_bytes()
        result = convert_solution(self.solution, rule_id=SOURCE_ID, overwrite=True)
        self.assertEqual(0, result["conflicts"])
        document = yaml.safe_load(self.output.read_text())
        self.assertEqual(f"xdr-{SOURCE_ID}", document["properties"]["id"])
        self.assertEqual("3.1.9", document["version"])
        self.assertEqual("local-artifact-only", document["contentProvenance"]["conversion"]["identityChange"]["scope"])
        self.assertEqual(before, self.other_output.read_bytes())
        for connectors in (CONNECTORS, [], None, "absent"):
            with self.subTest(connectors=connectors):
                source = yaml.safe_load(self.source.read_text())
                if connectors == "absent":
                    source.pop("requiredDataConnectors", None)
                else:
                    source["requiredDataConnectors"] = connectors
                self.source.write_text(yaml.safe_dump(source, sort_keys=False))
                result = convert_solution(self.solution, rule_id=SOURCE_ID, overwrite=True)
                self.assertEqual(int(connectors is None), result["needsReview"])
                updated = yaml.safe_load(self.output.read_text())
                self.assertEqual(connectors != "absent", "requiredDataConnectors" in updated)
                if connectors != "absent":
                    self.assertEqual(connectors, updated["requiredDataConnectors"])
                self.assertEqual(before, self.other_output.read_bytes())

    def test_cli_selection_preserves_run_and_returns_scoped_manifest(self):
        initialized = initialize_workflow(self.solution, workflow_profile="authoring")
        second = initialize_workflow(self.solution, workflow_profile="authoring", new_run=True)
        second_state = Path(second["statePath"]).read_bytes()
        with using_run(self.solution, initialized["runId"]):
            config = artifact_path(self.solution, "migration-config.yaml")
            config.write_text(yaml.safe_dump({"excludedRuleIds": {OTHER_ID: "not part of pilot"}}))
        output = io.StringIO()
        with redirect_stdout(output):
            code = main([
                "convert", "--solution", str(self.solution), "--run-id", initialized["runId"],
                "--rule-id", SOURCE_ID,
            ])
        self.assertEqual(0, code)
        result = json.loads(output.getvalue())
        self.assertEqual("rule", result["scope"]["kind"])
        self.assertIn(initialized["runId"], result["manifest"])
        self.assertFalse(self.other_output.exists())
        self.assertEqual(second_state, Path(second["statePath"]).read_bytes())
        self.assertFalse((Path(second["statePath"]).parent / "manifest.json").exists())

    def test_scoped_results_block_workflow_completion_and_packaging(self):
        initialize_workflow(self.solution, workflow_profile="authoring")
        convert_solution(self.solution)
        for stage in ("discovery", "conversion", "validation"):
            start_workflow_stage(self.solution, stage)
            artifacts = None
            message = None
            if stage == "validation":
                artifacts = {"runtimeStatus": "environment-blocked"}
                message = "Runtime validation was not run."
            complete_workflow_stage(
                self.solution,
                stage,
                status="passed",
                message=message,
                artifacts=artifacts,
                evidence=["prior evidence"],
            )
        convert_solution(self.solution, rule_id=SOURCE_ID, overwrite=True)
        state = workflow_status(self.solution)
        self.assertEqual("blocked", state["workflowStatus"])
        self.assertEqual("passed", state["stages"]["discovery"]["status"])
        self.assertEqual("blocked", state["stages"]["conversion"]["status"])
        self.assertEqual("blocked", state["stages"]["validation"]["status"])
        self.assertEqual(["prior evidence"], state["stages"]["validation"]["evidence"])
        self.assertEqual("rule", state["conversionScope"]["kind"])
        start_workflow_stage(self.solution, "conversion")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "rule-scoped"):
            complete_workflow_stage(self.solution, "conversion", status="passed")
        for stage in ("validation", "packaging", "report"):
            with self.assertRaisesRegex(ValueError, "rule-scoped"):
                complete_workflow_stage(self.solution, stage, status="passed")
        with self.assertRaisesRegex(ValueError, "rule-scoped"):
            start_workflow_stage(self.solution, "packaging")
        with mock.patch("sentinel_xdr_migration.packaging.subprocess.run") as process:
            with self.assertRaisesRegex(ValueError, "rule-scoped"):
                package_solution_v3_1(self.solution, version_bump="patch")
            process.assert_not_called()
        self.assertEqual(before, self.snapshot())
        convert_solution(self.solution, overwrite=True)
        complete_workflow_stage(self.solution, "conversion", status="passed")
        start_workflow_stage(self.solution, "validation")
        complete_workflow_stage(
            self.solution,
            "validation",
            status="passed",
            message="Runtime validation was not run.",
            artifacts={"runtimeStatus": "environment-blocked"},
        )
        self.assertEqual("solution", workflow_status(self.solution)["conversionScope"]["kind"])


if __name__ == "__main__":
    unittest.main()
