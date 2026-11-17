from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration.artifacts import (
    artifact_path, existing_artifact_path, existing_artifacts, migrate_reports,
    portable_artifact, report_directory, resolve_artifact_reference,
)
from sentinel_xdr_migration.content_paths import yaml_files
from sentinel_xdr_migration.workflow import (
    initialize_workflow, workflow_status, start_workflow_stage,
    complete_workflow_stage, _validate_packaging_evidence,
)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.storage = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.storage.cleanup)
        self.repository = Path(self.storage.name)
        self.solution = self.repository / "Solutions" / "Space Solution"
        self.solution.mkdir(parents=True)
        self.old = self.repository / "Reports" / self.solution.name / "sentinel-xdr-migration"

    @property
    def new(self):
        return report_directory(self.solution)

    def legacy(self, name, value):
        path = self.old / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_default_and_override_only_write_solution_logs(self):
        with mock.patch.dict("os.environ", {"AZURE_SENTINEL_REPORTS_ROOT": str(self.repository / "override")}):
            directory = report_directory(self.solution, create=True)
            self.assertEqual(self.solution / "Logs" / "sentinel-xdr-migration", directory.parent)
            self.assertEqual(self.new, directory)
        self.assertFalse(self.old.exists())

    def test_read_only_fallback_then_explicit_copy_preserves_blocked_state(self):
        initialize_workflow(self.solution, workflow_profile="authoring")
        start_workflow_stage(self.solution, "discovery")
        complete_workflow_stage(self.solution, "discovery", status="blocked", message="Environment unavailable")
        state = artifact_path(self.solution, "workflow-state.json")
        self.old.mkdir(parents=True)
        legacy = self.old / state.name
        state.replace(legacy)
        original = legacy.read_bytes()
        with self.assertWarns(UserWarning):
            status = workflow_status(self.solution)
        self.assertEqual("blocked", status["workflowStatus"])
        self.assertFalse(state.exists())
        self.assertEqual(["workflow-state.json"], migrate_reports(self.solution)["files"])
        self.assertFalse(state.exists())
        with self.assertRaisesRegex(ValueError, "migrate-reports"):
            start_workflow_stage(self.solution, "discovery")
        migrate_reports(self.solution, apply=True)
        self.assertEqual(original, legacy.read_bytes())
        self.assertEqual("blocked", workflow_status(self.solution)["workflowStatus"])
        start_workflow_stage(self.solution, "discovery")
        self.assertEqual(2, workflow_status(self.solution)["stages"]["discovery"]["attempts"])
        self.assertEqual([], migrate_reports(self.solution, apply=True)["files"])

    def test_conflicting_copies_fail_without_partial_copy(self):
        self.legacy("a.json", {"a": 1})
        self.legacy("state.json", {"old": True})
        self.new.mkdir(parents=True)
        (self.new / "state.json").write_text('{"new": true}')
        with self.assertRaisesRegex(ValueError, "conflicting"):
            existing_artifact_path(self.solution, "state.json")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            migrate_reports(self.solution, apply=True)
        self.assertFalse((self.new / "a.json").exists())

    def test_changed_legacy_and_missing_copied_artifacts_fail(self):
        path = self.legacy("manifest.json", {"total": 2})
        migrate_reports(self.solution, apply=True)
        path.write_text('{"total": 3}')
        with self.assertRaisesRegex(ValueError, "changed after migration"):
            existing_artifact_path(self.solution, "manifest.json")
        path.write_text(json.dumps({"total": 2}))
        (self.new / "manifest.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            report_directory(self.solution, create=True)

    def test_runtime_discovery_includes_old_reports_and_detects_conflicts(self):
        old = self.legacy("runtime-validation.graph.json", {"provider": "graph"})
        with self.assertWarns(UserWarning):
            self.assertEqual([old], existing_artifacts(self.solution, "runtime-validation.*.json"))
        self.new.mkdir(parents=True)
        (self.new / old.name).write_text('{"provider": "other"}')
        with self.assertRaisesRegex(ValueError, "conflicting"):
            existing_artifacts(self.solution, "runtime-validation.*.json")

    def test_portable_packaging_evidence_resolves_against_solution_not_cwd(self):
        initialize_workflow(self.solution, workflow_profile="authoring", version_bump="none")
        package = self.solution / "Package"
        package.mkdir()
        document = {"packager": "V3.1", "versionBump": "none"}
        for field, name in (
            ("mainTemplate", "mainTemplate.json"), ("createUiDefinition", "createUiDefinition.json"),
            ("testParameters", "testParameters.json"), ("zip", "3.1.0.zip"),
        ):
            (package / name).write_text("{}")
            document[field] = f"Package\\{name}"
        report = artifact_path(self.solution, "packaging.v3_1.json")
        report.write_text(json.dumps(document))
        state = workflow_status(self.solution)
        state["stages"]["validation"]["status"] = "passed"
        _validate_packaging_evidence(
            state,
            {"packager": "V3.1", "packageReport": "Logs\\sentinel-xdr-migration\\packaging.v3_1.json"},
            self.solution,
        )
        self.assertEqual(package / "mainTemplate.json", resolve_artifact_reference(
            self.solution, "Package\\mainTemplate.json"))

    def test_serialization_preserves_identity_and_error_semantics(self):
        message = f"Provider cannot read {self.solution}/private/file"
        query = (
            'DeviceProcessEvents\n'
            '| where NewProcessName endswith "\\\\\\\\certutil.exe"\n'
            '| extend SourcePath = "C:\\\\\\\\Program Files\\\\\\\\source\\\\\\\\agent.exe"\n'
            '| join kind=inner (DeviceNetworkEvents | project DeviceId, RemoteUrl) on DeviceId\n'
            '| where RemoteUrl contains "https://example.test/source?mode=join"\n'
            '| project DeviceId, SourcePath'
        )
        value = portable_artifact(self.solution, {
            "solution": str(self.solution),
            "source": str(self.solution / "Analytic Rules" / "Nested Rule.yaml"),
            "sourceReference": {"source": "Analytic Rules\\Nested Rule.yaml"},
            "context": {"workspaceResourceId": "/subscriptions/id/resourceGroups/rg", "tenantId": "tenant"},
            "error": message,
            "query": 'print Path="/home/example"',
            "queries": {"source": query, "converted": query},
            "errorDetails": {"message": message, "source": "C:\\provider\\error"},
            "artifacts": {
                "manifest": str(self.solution / "Logs" / "manifest.json"),
            },
            "access_token": "secret", "details": "Bearer eySecret.token.value https://example/?sig=secret&se=secret",
        })
        self.assertEqual(".", value["solution"])
        self.assertEqual("Analytic Rules/Nested Rule.yaml", value["source"])
        self.assertEqual(
            "Analytic Rules/Nested Rule.yaml",
            value["sourceReference"]["source"],
        )
        self.assertEqual(message, value["error"])
        self.assertEqual('print Path="/home/example"', value["query"])
        self.assertEqual(query, value["queries"]["source"])
        self.assertEqual(query, value["queries"]["converted"])
        self.assertEqual(message, value["errorDetails"]["message"])
        self.assertEqual("C:\\provider\\error", value["errorDetails"]["source"])
        self.assertEqual("Logs/manifest.json", value["artifacts"]["manifest"])
        self.assertEqual("tenant", value["context"]["tenantId"])
        self.assertNotIn("secret", json.dumps(value))
        self.assertNotIn("eySecret", value["details"])

    def test_yaml_inventory_excludes_logs_and_reports(self):
        for name in ["Actual.yaml", "Nested/Rule.yml", "Logs/config.yaml", "Reports/config.yml"]:
            path = self.solution / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("name: fixture")
        self.assertEqual(["Actual.yaml", "Nested/Rule.yml"], [
            path.relative_to(self.solution).as_posix() for path in yaml_files(self.solution)
        ])

    def test_all_solution_logs_stay_gitignored(self):
        paths = [
            "Solutions/Reporting Fixture/Logs/sentinel-xdr-migration/workflow-state.json",
            "Solutions/Reporting Fixture/Logs/sentinel-xdr-migration/run.log",
            "Solutions/Other Fixture/Logs/other-run/raw.json",
        ]
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin"],
            input="\n".join(paths) + "\n", capture_output=True, text=True, check=False,
        )
        self.assertEqual(paths, result.stdout.splitlines())

    def test_xdr_legacy_copy_keeps_detection_yaml_and_config_unchanged(self):
        output = self.solution / "XDR Detections"
        output.mkdir()
        (output / "Rule.yaml").write_text("kind: CustomDetection\n")
        config = output / "migration-config.yaml"
        config.write_text("tableMappings:\n  Old: New\n")
        migrate_reports(self.solution, apply=True)
        self.assertEqual(config.read_bytes(), (self.new / config.name).read_bytes())
        self.assertFalse((self.new / "Rule.yaml").exists())
        self.assertTrue(config.exists())

    def test_deployment_blocks_before_auth_or_provider_writes_with_legacy_evidence(self):
        from sentinel_xdr_migration.deployment import deploy_solution
        from sentinel_xdr_migration.analytic_deployment import deploy_analytic_rules

        self.legacy("workflow-state.json", {"status": "blocked"})
        with mock.patch("sentinel_xdr_migration.deployment._deployment_token") as graph_token:
            with self.assertRaisesRegex(ValueError, "migrate-reports"):
                deploy_solution(self.solution)
            graph_token.assert_not_called()
        (self.solution / "Analytic Rules").mkdir()
        with mock.patch("sentinel_xdr_migration.analytic_deployment._arm_token") as arm_token:
            with self.assertRaisesRegex(ValueError, "migrate-reports"):
                deploy_analytic_rules(self.solution)
            arm_token.assert_not_called()

    def test_binary_legacy_evidence_is_preserved_byte_for_byte(self):
        self.old.mkdir(parents=True)
        evidence = self.old / "capture.png"
        evidence.write_bytes(b"\x89PNG\r\n\xff\x00")
        migrate_reports(self.solution, apply=True)
        self.assertEqual(evidence.read_bytes(), (self.new / evidence.name).read_bytes())
