from __future__ import annotations

import hashlib
import io
import json
import logging
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
from pathlib import Path

from sentinel_xdr_migration.artifacts import (
    MIGRATION_RECEIPT, RUN_MARKER, artifact_path, existing_artifact_path,
    list_runs, migrate_reports, portable_artifact, report_directory, reports_base,
    resolve_artifact_reference, using_run, write_json_artifact,
)
from sentinel_xdr_migration.cli import main
from sentinel_xdr_migration.converter import configure_logging
from sentinel_xdr_migration.workflow import (
    initialize_workflow, workflow_status, start_workflow_stage, complete_workflow_stage,
)


class RunScopingTests(unittest.TestCase):
    def setUp(self):
        self.storage = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.storage.cleanup)
        self.solution = Path(self.storage.name) / "Solutions" / "Space Solution"
        self.solution.mkdir(parents=True)

    def init(self, **kwargs):
        return initialize_workflow(self.solution, workflow_profile="authoring", **kwargs)

    def legacy_flat(self):
        state = self.init()
        path = Path(state["statePath"])
        document = json.loads(path.read_text())
        document.pop("runId")
        document["workflowStatus"] = "blocked"
        document["stages"]["discovery"]["status"] = "passed"
        document["stages"]["conversion"]["status"] = "blocked"
        document["stages"]["conversion"]["message"] = "22 drafts require review"
        document["stages"]["conversion"]["artifacts"] = {
            "manifest": "Logs/sentinel-xdr-migration/manifest.json",
        }
        flat = reports_base(self.solution)
        path.unlink()
        (path.parent / RUN_MARKER).unlink()
        remaining = {item.name for item in path.parent.iterdir()}
        self.assertEqual(remaining, {".workflow-state.lock"})
        (path.parent / ".workflow-state.lock").unlink()
        path.parent.rmdir()
        (flat / "workflow-state.json").write_text(json.dumps(document))
        (flat / "manifest.json").write_text(json.dumps({"converted": 18, "needsReview": 22}))
        return flat, document

    def cli(self, *args):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            status = main(list(args))
        return status, output.getvalue(), errors.getvalue()

    def test_new_workflow_new_id_and_resume_same_id(self):
        first = self.init()
        resumed = self.init()
        self.assertEqual(first["runId"], resumed["runId"])
        self.assertTrue(resumed["resumed"])
        second = self.init(new_run=True)
        self.assertNotEqual(first["runId"], second["runId"])
        self.assertFalse(second["resumed"])
        self.assertEqual(2, len(list_runs(self.solution)))
        self.assertEqual(first["runId"], Path(first["statePath"]).parent.name)
        self.assertEqual(second["runId"], Path(second["statePath"]).parent.name)

    def test_ambiguous_default_fails_and_explicit_selection_is_isolated(self):
        first, second = self.init(), self.init(new_run=True)
        with self.assertRaisesRegex(ValueError, "multiple migration runs"):
            workflow_status(self.solution)
        with self.assertRaisesRegex(ValueError, "multiple migration runs"):
            report_directory(self.solution, create=True)
        with using_run(self.solution, first["runId"]):
            start_workflow_stage(self.solution, "discovery")
            complete_workflow_stage(self.solution, "discovery", status="blocked", message="first only")
            manifest = artifact_path(self.solution, "manifest.json")
            write_json_artifact(self.solution, manifest, {"run": "first"})
        with using_run(self.solution, second["runId"]):
            self.assertEqual("pending", workflow_status(self.solution)["stages"]["discovery"]["status"])
            self.assertFalse(existing_artifact_path(self.solution, "manifest.json").exists())
        with using_run(self.solution, first["runId"]):
            self.assertEqual("blocked", workflow_status(self.solution)["workflowStatus"])

    def test_json_artifacts_use_lf_line_endings_on_every_platform(self):
        state = self.init()
        with using_run(self.solution, state["runId"]):
            manifest = artifact_path(self.solution, "manifest.json")
            write_json_artifact(self.solution, manifest, {"nested": {"value": 1}})
        raw = manifest.read_bytes()
        self.assertNotIn(b"\r\n", raw)
        self.assertEqual(raw, (json.dumps({"nested": {"value": 1}}, indent=2) + "\n").encode("utf-8"))

    def test_unknown_and_traversal_run_ids_cannot_write(self):
        with self.assertRaisesRegex(ValueError, "safe directory"):
            with using_run(self.solution, "../escape"):
                self.init()
        with using_run(self.solution, "unknown"):
            with self.assertRaisesRegex(ValueError, "does not exist"):
                report_directory(self.solution, create=True)
        self.assertEqual([], list_runs(self.solution))

    def test_invalid_profile_does_not_allocate_a_run(self):
        for invalid in (None, "", "invalid"):
            with self.assertRaises(ValueError):
                initialize_workflow(self.solution, workflow_profile=invalid, new_run=True)
        self.assertEqual([], list_runs(self.solution))

    def test_missing_marker_cannot_fall_back_to_stale_flat_state(self):
        self.legacy_flat()
        migrated = migrate_reports(self.solution, apply=True)
        marker = reports_base(self.solution) / migrated["runId"] / RUN_MARKER
        marker.unlink()
        with self.assertRaisesRegex(ValueError, "marker is missing"):
            workflow_status(self.solution)

    def test_flat_migration_preview_apply_preserves_status_and_originals(self):
        flat, state = self.legacy_flat()
        originals = {path.name: path.read_bytes() for path in flat.iterdir() if path.is_file()}
        with self.assertWarns(UserWarning):
            self.assertEqual("blocked", workflow_status(self.solution)["workflowStatus"])
        preview = migrate_reports(self.solution)
        self.assertEqual([], list_runs(self.solution))
        with using_run(self.solution, preview["runId"]):
            result = migrate_reports(self.solution, apply=True)
            migrated = workflow_status(self.solution)
            self.assertEqual("blocked", migrated["workflowStatus"])
            self.assertEqual(state["stages"]["conversion"]["message"], migrated["stages"]["conversion"]["message"])
            manifest = migrated["stages"]["conversion"]["artifacts"]["manifest"]
            self.assertEqual(artifact_path(self.solution, "manifest.json"),
                             resolve_artifact_reference(self.solution, manifest))
            self.assertIn(preview["runId"], manifest)
            self.assertEqual([], migrate_reports(self.solution, apply=True)["files"])
        self.assertEqual(preview["destination"], result["destination"])
        for name, value in originals.items():
            self.assertEqual(value, (flat / name).read_bytes())
        self.assertTrue((flat / result["runId"] / MIGRATION_RECEIPT).is_file())

    def test_prior_flat_receipt_preserves_newer_flat_state_over_archived_root(self):
        flat, state = self.legacy_flat()
        root_reports = self.solution.parents[1] / "Reports" / self.solution.name / "sentinel-xdr-migration"
        root_reports.mkdir(parents=True)
        old_state = deepcopy(state)
        old_state["stages"]["discovery"]["status"] = "blocked"
        old = root_reports / "workflow-state.json"
        old.write_text(json.dumps(old_state))
        (flat / MIGRATION_RECEIPT).write_text(json.dumps({
            old.name: [hashlib.sha256(old.read_bytes()).hexdigest()],
        }))
        migrate_reports(self.solution, apply=True)
        self.assertEqual("passed", workflow_status(self.solution)["stages"]["discovery"]["status"])
        self.assertEqual("blocked", json.loads(old.read_text())["stages"]["discovery"]["status"])
        old.write_text("{}")
        with self.assertRaisesRegex(ValueError, "changed after migration"):
            workflow_status(self.solution)

    def test_unreceipted_root_and_flat_conflict_blocks_without_creating_run(self):
        flat, _ = self.legacy_flat()
        root_reports = self.solution.parents[1] / "Reports" / self.solution.name / "sentinel-xdr-migration"
        root_reports.mkdir(parents=True)
        (root_reports / "workflow-state.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            migrate_reports(self.solution, apply=True)
        self.assertEqual([], list_runs(self.solution))
        self.assertTrue((flat / "workflow-state.json").is_file())

    def test_archived_legacy_does_not_leak_into_new_run(self):
        self.legacy_flat()
        imported = migrate_reports(self.solution, apply=True)["runId"]
        fresh = self.init(new_run=True)
        with using_run(self.solution, fresh["runId"]):
            self.assertFalse(existing_artifact_path(self.solution, "manifest.json").exists())
            self.assertEqual("pending", workflow_status(self.solution)["stages"]["conversion"]["status"])
        with using_run(self.solution, imported):
            self.assertEqual("blocked", workflow_status(self.solution)["stages"]["conversion"]["status"])

    def test_cross_run_packaging_references_are_rejected(self):
        first, second = self.init(), self.init(new_run=True)
        with using_run(self.solution, second["runId"]):
            reference = f"Logs/sentinel-xdr-migration/{first['runId']}/packaging.v3_1.json"
            with self.assertRaisesRegex(ValueError, "different migration run"):
                resolve_artifact_reference(self.solution, reference)
            with self.assertRaisesRegex(ValueError, "selected migration run"):
                write_json_artifact(self.solution, Path(first["statePath"]), {})

    def test_cli_run_selection_and_migration_reuse_preview_id(self):
        self.legacy_flat()
        code, output, _ = self.cli("migrate-reports", "--solution", str(self.solution))
        self.assertEqual(0, code)
        run_id = json.loads(output)["runId"]
        code, _, error = self.cli("migrate-reports", "--solution", str(self.solution), "--run-id", run_id, "--apply")
        self.assertEqual(0, code, error)
        self.init(new_run=True)
        code, _, error = self.cli("workflow-status", "--solution", str(self.solution))
        self.assertEqual(2, code)
        self.assertIn("multiple migration runs", error)
        code, output, error = self.cli("workflow-status", "--solution", str(self.solution), "--run-id", run_id)
        self.assertEqual(0, code, error)
        self.assertEqual(run_id, json.loads(output)["runId"])
        code, output, _ = self.cli("workflow-runs", "--solution", str(self.solution))
        self.assertEqual(2, len(json.loads(output)["runs"]))

    def test_logging_switches_only_toolkit_handlers_between_runs(self):
        first, second = self.init(), self.init(new_run=True)
        try:
            for item, message in [(first, "FIRST RUN"), (second, "SECOND RUN")]:
                with using_run(self.solution, item["runId"]), redirect_stderr(io.StringIO()):
                    configure_logging(self.solution)
                    logging.info(message)
            first_log = Path(first["statePath"]).parent / "sentinel-xdr-migration.log"
            second_log = Path(second["statePath"]).parent / "sentinel-xdr-migration.log"
            self.assertNotIn("SECOND RUN", first_log.read_text())
            self.assertNotIn("FIRST RUN", second_log.read_text())
        finally:
            for handler in list(logging.getLogger().handlers):
                if getattr(handler, "_sentinel_xdr_handler", False):
                    logging.getLogger().removeHandler(handler)
                    handler.close()
