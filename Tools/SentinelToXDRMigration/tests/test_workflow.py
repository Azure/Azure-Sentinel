from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sentinel_xdr_migration.workflow import (
    complete_workflow_stage,
    initialize_workflow,
    next_workflow_stage,
    start_workflow_stage,
    workflow_status,
)


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.solution = Path(self.temp.name) / "Sample"
        self.solution.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_initialize_creates_resumable_state(self) -> None:
        created = initialize_workflow(
            self.solution,
            workspace_resource_id="/subscriptions/test/workspaces/sample",
            version_bump="patch",
        )
        resumed = initialize_workflow(
            self.solution,
            workspace_resource_id="/subscriptions/test/workspaces/sample",
            version_bump="patch",
        )

        self.assertFalse(created["resumed"])
        self.assertTrue(resumed["resumed"])
        self.assertEqual(resumed["next"], "discovery")
        self.assertTrue(
            (self.solution / "XDR Detections" / "workflow-state.json").is_file()
        )
        self.assertEqual(
            resumed["stages"]["mockIngestion"]["status"],
            "notRequired",
        )

    def test_stage_gate_requires_dependencies(self) -> None:
        initialize_workflow(self.solution)

        with self.assertRaisesRegex(ValueError, "blocked by: discovery"):
            start_workflow_stage(self.solution, "conversion")

    def test_failed_stage_can_be_retried(self) -> None:
        initialize_workflow(self.solution)
        start_workflow_stage(self.solution, "discovery")
        complete_workflow_stage(
            self.solution,
            "discovery",
            status="failed",
            message="source metadata is incomplete",
        )

        retry = start_workflow_stage(self.solution, "discovery")

        self.assertEqual(retry["attempts"], 2)
        self.assertEqual(retry["status"], "running")

    def test_complete_stage_persists_contract_and_unlocks_next(self) -> None:
        initialize_workflow(self.solution)
        start_workflow_stage(self.solution, "discovery")
        result = complete_workflow_stage(
            self.solution,
            "discovery",
            status="passed",
            message="one source rule discovered",
            artifacts={"inspection": "XDR Detections/inspection.json"},
            evidence=["Analytic Rules/Sample.yaml"],
        )

        self.assertEqual(result["next"], "conversion")
        self.assertEqual(next_workflow_stage(self.solution)["next"], "conversion")
        persisted = workflow_status(self.solution)
        discovery = persisted["stages"]["discovery"]
        self.assertEqual(discovery["artifacts"]["inspection"], "XDR Detections/inspection.json")
        self.assertEqual(discovery["evidence"], ["Analytic Rules/Sample.yaml"])

    def test_context_mismatch_is_rejected(self) -> None:
        initialize_workflow(self.solution, version_bump="patch")

        with self.assertRaisesRegex(ValueError, "workflow already uses"):
            initialize_workflow(self.solution, version_bump="minor")

    def test_authoring_profile_moves_from_packaging_to_report(self) -> None:
        initialize_workflow(self.solution, workflow_profile="authoring")
        for stage in ("discovery", "conversion", "validation", "packaging"):
            start_workflow_stage(self.solution, stage)
            complete_workflow_stage(self.solution, stage, status="passed")

        self.assertEqual(next_workflow_stage(self.solution)["next"], "report")

    def test_qualification_profile_requires_internal_test_stages(self) -> None:
        initialized = initialize_workflow(
            self.solution,
            workflow_profile="qualification",
        )
        self.assertEqual(initialized["stages"]["mockIngestion"]["status"], "pending")
        for stage in ("discovery", "conversion", "validation", "packaging"):
            start_workflow_stage(self.solution, stage)
            complete_workflow_stage(self.solution, stage, status="passed")

        self.assertEqual(next_workflow_stage(self.solution)["next"], "deployment")

    def test_blocked_stage_requires_explanation(self) -> None:
        initialize_workflow(self.solution)
        start_workflow_stage(self.solution, "discovery")

        with self.assertRaisesRegex(ValueError, "require a message"):
            complete_workflow_stage(
                self.solution,
                "discovery",
                status="blocked",
            )


if __name__ == "__main__":
    unittest.main()
