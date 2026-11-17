from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration.artifacts import artifact_path, report_directory, using_run
from sentinel_xdr_migration.runtime_report_references import (
    apply_runtime_report_reference_repair,
    plan_runtime_report_reference_repair,
)
from sentinel_xdr_migration.packaging_selection import _current_target
from sentinel_xdr_migration.packaging_selection import _source_runtime_reference_status
from sentinel_xdr_migration.target_context import TARGET_FILE_NAME
from sentinel_xdr_migration.workflow import (
    _load,
    _write_unlocked,
    complete_workflow_stage,
    initialize_workflow,
)


class RuntimeReportReferenceRepairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.solution = Path(self.temp.name) / "ReferenceRepair"
        self.solution.mkdir()
        detection = self.solution / "XDR Detections" / "Keep.yaml"
        detection.parent.mkdir(parents=True)
        detection.write_text("kind: CustomDetection\n", encoding="utf-8")
        self.run_id = initialize_workflow(
            self.solution, workflow_profile="authoring",
        )["runId"]
        with using_run(self.solution, self.run_id):
            self.run_directory = report_directory(self.solution, create=True)
        self.source_report = self.run_directory / "runtime-validation.azure-monitor-sdk.json"
        self.graph_report = self.run_directory / "runtime-validation.graph.json"
        self.plan_report = self.run_directory / "runtime-query-plan.json"
        self.consent_report = self.run_directory / "runtime-query-consent.json"
        for path, payload in (
            (self.source_report, {"provider": "azure-monitor-sdk", "results": []}),
            (self.graph_report, {"provider": "graph", "results": []}),
            (self.plan_report, {"runId": self.run_id}),
            (self.consent_report, {"status": "approved"}),
        ):
            path.write_text(json.dumps(payload), encoding="utf-8")
        self.state_path, state = _load(self.solution)
        validation = state["stages"]["validation"]
        validation.update({
            "status": "passed",
            "attempts": 1,
            "startedAt": "2026-10-11T20:00:00Z",
            "completedAt": "2026-10-11T20:01:00Z",
            "message": None,
            "artifacts": {
                "sentinelRuntimeReport": self.source_report.relative_to(self.solution).as_posix(),
                "advancedHuntingRuntimeReport": self.graph_report.relative_to(self.solution).as_posix(),
                "runtimeStatus": "passed",
            },
            "evidence": ["historical-validation-failure"],
        })
        _write_unlocked(self.state_path, state)
        self.state_before = self.state_path.read_bytes()
        self.validation_before = state["stages"]["validation"].copy()
        self.binding = mock.patch(
            "sentinel_xdr_migration.runtime_report_references._validate_complete_runtime_evidence",
            return_value=(
                {"provider": "azure-monitor-sdk", "results": []},
                {"provider": "azure-monitor-sdk"},
                "f" * 64,
            ),
        )
        self.binding.start()
        self.addCleanup(self.binding.stop)

    def _state(self) -> dict:
        return _load(self.solution)[1]

    def _set_references(self, *, canonical: str | None, legacy: str | None) -> None:
        path, state = _load(self.solution)
        artifacts = state["stages"]["validation"]["artifacts"]
        artifacts.pop("sentinelRuntimeJson", None)
        artifacts.pop("sentinelRuntimeReport", None)
        if canonical is not None:
            artifacts["sentinelRuntimeJson"] = canonical
        if legacy is not None:
            artifacts["sentinelRuntimeReport"] = legacy
        _write_unlocked(path, state)

    def test_legacy_alias_on_passed_stage_plans_canonical_reference(self) -> None:
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        self.assertTrue(plan["eligible"], plan.get("reason"))
        self.assertEqual("add-canonical-reference", plan["action"])
        self.assertEqual("passed", plan["workflowStageStatus"])
        self.assertEqual(
            self.source_report.relative_to(self.solution).as_posix(),
            plan["desiredCanonicalReference"],
        )

    def test_blocked_validation_stage_is_not_repaired(self) -> None:
        path, state = _load(self.solution)
        state["stages"]["validation"]["status"] = "blocked"
        _write_unlocked(path, state)
        before = path.read_bytes()
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        self.assertFalse(plan["eligible"])
        self.assertEqual("rejected", plan["action"])
        self.assertIn("blocked", plan["reason"])
        self.assertEqual(before, path.read_bytes())

    def test_blocked_stage_with_current_canonical_reference_is_noop(self) -> None:
        path, state = _load(self.solution)
        validation = state["stages"]["validation"]
        validation["status"] = "blocked"
        validation["artifacts"]["sentinelRuntimeJson"] = (
            self.source_report.relative_to(self.solution).as_posix()
        )
        _write_unlocked(path, state)
        before = path.read_bytes()
        validator = mock.patch(
            "sentinel_xdr_migration.runtime_report_references._validate_complete_runtime_evidence",
            side_effect=AssertionError("blocked no-op must not claim complete validation"),
        )
        with validator:
            plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        self.assertFalse(plan["eligible"])
        self.assertTrue(plan["noChange"])
        self.assertEqual("already-current-noop", plan["action"])
        self.assertEqual("blocked", plan["stageStatusPreserved"])
        no_op = apply_runtime_report_reference_repair(
            self.solution,
            self.run_id,
            expected_plan_sha256=plan["planSha256"],
        )
        self.assertEqual("already-current-noop", no_op["action"])
        self.assertTrue(no_op["noChange"])
        self.assertEqual(before, path.read_bytes())

    def test_absent_reference_can_be_repaired_only_after_complete_proof(self) -> None:
        self._set_references(canonical=None, legacy=None)
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        self.assertTrue(plan["eligible"], plan.get("reason"))
        self.assertEqual("add-canonical-reference", plan["action"])

    def test_matching_alias_and_canonical_are_accepted(self) -> None:
        reference = self.source_report.relative_to(self.solution).as_posix()
        self._set_references(canonical=reference, legacy=reference)
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        self.assertTrue(plan["eligible"], plan.get("reason"))
        self.assertEqual("already-current", plan["action"])

    def test_conflicting_alias_and_canonical_are_rejected(self) -> None:
        self._set_references(
            canonical=self.source_report.relative_to(self.solution).as_posix(),
            legacy="Logs/sentinel-xdr-migration/other-run/runtime-validation.azure-monitor-sdk.json",
        )
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        self.assertFalse(plan["eligible"])
        self.assertIn("reference", plan["reason"])

    def test_runtime_reference_traversal_is_rejected_before_resolution(self) -> None:
        path, state = _load(self.solution)
        state["stages"]["validation"]["artifacts"]["sentinelRuntimeJson"] = (
            f"../{self.run_id}/runtime-validation.azure-monitor-sdk.json"
        )
        _write_unlocked(path, state)
        valid, reason = _source_runtime_reference_status(
            self.solution,
            self.run_directory,
            _load(self.solution)[1],
            provider="azure-monitor-sdk",
        )
        self.assertFalse(valid)
        self.assertEqual("source-runtime-report-reference-unsafe-path", reason)

    def test_incomplete_or_unbound_runtime_proof_is_rejected_without_state_change(self) -> None:
        blocking_reasons = (
            "stale query hash",
            "wrong locked target",
            "SDK execution binding missing",
            "Graph execution binding unsigned",
            "missing source-family coverage",
            "later applicable runtime failure",
        )
        for reason in blocking_reasons:
            with self.subTest(reason=reason):
                with mock.patch(
                    "sentinel_xdr_migration.runtime_report_references._validate_complete_runtime_evidence",
                    side_effect=ValueError(reason),
                ):
                    result = plan_runtime_report_reference_repair(self.solution, self.run_id)
                self.assertFalse(result["eligible"])
                self.assertIn(reason, result["reason"])
                self.assertEqual(self.state_before, self.state_path.read_bytes())

    def test_dry_run_failure_creates_or_changes_no_artifacts(self) -> None:
        before = {
            path.relative_to(self.solution).as_posix(): path.read_bytes()
            for path in self.solution.rglob("*")
            if path.is_file()
        }
        with mock.patch(
            "sentinel_xdr_migration.runtime_report_references._validate_complete_runtime_evidence",
            side_effect=ValueError("injected missing current target"),
        ):
            result = plan_runtime_report_reference_repair(self.solution, self.run_id)
        after = {
            path.relative_to(self.solution).as_posix(): path.read_bytes()
            for path in self.solution.rglob("*")
            if path.is_file()
        }
        self.assertFalse(result["eligible"])
        self.assertEqual(before, after)

    def test_apply_is_idempotent_and_preserves_stage_and_failure_history(self) -> None:
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        first = apply_runtime_report_reference_repair(
            self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
        )
        second = apply_runtime_report_reference_repair(
            self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
        )
        self.assertEqual("canonical-reference-added", first["action"])
        self.assertEqual(first, second)
        backup_path = self.solution / first["backupPath"]
        receipt_path = self.solution / first["receiptPath"]
        self.assertEqual(self.state_before, backup_path.read_bytes())
        self.assertTrue(receipt_path.is_file())
        self.assertEqual(first["planSha256"], json.loads(receipt_path.read_text())["planSha256"])
        after = self._state()["stages"]["validation"]
        self.assertEqual(self.validation_before["status"], after["status"])
        self.assertEqual(self.validation_before["evidence"], after["evidence"])
        self.assertEqual(
            self.validation_before["artifacts"]["sentinelRuntimeReport"],
            after["artifacts"]["sentinelRuntimeReport"],
        )
        self.assertIn("sentinelRuntimeJson", after["artifacts"])

    def test_apply_selects_the_exact_run_before_acquiring_the_state_lock(self) -> None:
        other = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            new_run=True,
        )["runId"]
        self.assertNotEqual(self.run_id, other)
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        result = apply_runtime_report_reference_repair(
            self.solution,
            self.run_id,
            expected_plan_sha256=plan["planSha256"],
        )
        self.assertEqual(self.run_id, result["runId"])
        self.assertIn(self.run_id, result["receiptPath"])
        with using_run(self.solution, other):
            other_state = _load(self.solution)[1]
        other_artifacts = other_state["stages"]["validation"].get("artifacts") or {}
        self.assertEqual("pending", other_state["stages"]["validation"]["status"])
        self.assertNotIn("sentinelRuntimeJson", other_artifacts)

    def test_receipt_write_failure_is_recovered_before_retry_reports_success(self) -> None:
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        module = "sentinel_xdr_migration.runtime_report_references"
        original_atomic = __import__(module, fromlist=["_atomic_json"])._atomic_json

        def fail_receipt(path: Path, payload: dict) -> None:
            if path.name.startswith("receipt."):
                raise OSError("injected receipt failure")
            original_atomic(path, payload)

        with mock.patch(f"{module}._atomic_json", side_effect=fail_receipt):
            with self.assertRaisesRegex(RuntimeError, "pending recovery"):
                apply_runtime_report_reference_repair(
                    self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
                )
        repair_dir = self.source_report.parent / "runtime-report-reference-repair"
        self.assertTrue(list(repair_dir.glob("pending.*.json")))
        self.assertFalse(list(repair_dir.glob("receipt.*.json")))
        retry_plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        self.assertEqual("already-current", retry_plan["action"])
        recovered = apply_runtime_report_reference_repair(
            self.solution, self.run_id, expected_plan_sha256=retry_plan["planSha256"],
        )
        self.assertEqual("canonical-reference-added", recovered["action"])
        self.assertTrue(list(repair_dir.glob("receipt.*.json")))
        self.assertFalse(list(repair_dir.glob("pending.*.json")))

    def test_blocked_stage_does_not_hide_unreceipted_pending_transaction(self) -> None:
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        pending_path = (
            self.source_report.parent
            / "runtime-report-reference-repair"
            / f"pending.{plan['planSha256']}.json"
        )
        pending_path.parent.mkdir(exist_ok=True)
        pending_path.write_text(
            json.dumps(
                {
                    "schemaVersion": "1.0.0",
                    "runId": self.run_id,
                    "planSha256": plan["planSha256"],
                    "status": "prepared",
                }
            ),
            encoding="utf-8",
        )
        self._set_references(
            canonical=self.source_report.relative_to(self.solution).as_posix(),
            legacy=None,
        )
        state_path, state = _load(self.solution)
        state["stages"]["validation"]["status"] = "blocked"
        _write_unlocked(state_path, state)
        blocked_plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        self.assertEqual("already-current-noop", blocked_plan["action"])
        with self.assertRaisesRegex(ValueError, "cannot be recovered"):
            apply_runtime_report_reference_repair(
                self.solution,
                self.run_id,
                expected_plan_sha256=blocked_plan["planSha256"],
            )

    def test_prepared_transaction_recovers_if_state_write_fails_before_mutation(self) -> None:
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        original_state = self.state_path.read_bytes()
        with mock.patch(
            "sentinel_xdr_migration.runtime_report_references._write_unlocked",
            side_effect=OSError("injected workflow state write failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "pending recovery"):
                apply_runtime_report_reference_repair(
                    self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
                )
        self.assertEqual(original_state, self.state_path.read_bytes())
        pending = list(
            (self.source_report.parent / "runtime-report-reference-repair").glob("pending.*.json")
        )
        self.assertEqual(1, len(pending))
        recovered = apply_runtime_report_reference_repair(
            self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
        )
        self.assertEqual("canonical-reference-added", recovered["action"])
        self.assertFalse(list(pending[0].parent.glob("pending.*.json")))

    def test_stale_state_plan_does_not_overwrite_a_concurrent_change(self) -> None:
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        path, state = _load(self.solution)
        state["stages"]["validation"]["artifacts"]["operatorNote"] = "concurrent update"
        _write_unlocked(path, state)
        changed = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "stale"):
            apply_runtime_report_reference_repair(
                self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
            )
        self.assertEqual(changed, path.read_bytes())

    def test_stale_report_or_authorization_evidence_invalidates_the_plan(self) -> None:
        for evidence_path in (
            self.source_report,
            self.graph_report,
            self.plan_report,
            self.consent_report,
        ):
            with self.subTest(path=evidence_path.name):
                plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
                evidence_path.write_text(
                    evidence_path.read_text(encoding="utf-8") + " ",
                    encoding="utf-8",
                )
                state_before = self.state_path.read_bytes()
                with self.assertRaisesRegex(ValueError, "stale"):
                    apply_runtime_report_reference_repair(
                        self.solution,
                        self.run_id,
                        expected_plan_sha256=plan["planSha256"],
                    )
                self.assertEqual(state_before, self.state_path.read_bytes())

    def test_commit_lock_rechecks_state_after_plan_construction(self) -> None:
        plan = plan_runtime_report_reference_repair(self.solution, self.run_id)
        module = "sentinel_xdr_migration.runtime_report_references"
        original_build = __import__(module, fromlist=["_build_reference_repair_plan"])._build_reference_repair_plan

        def edit_after_plan(solution: str | Path, run_id: str) -> dict:
            built = original_build(solution, run_id)
            path, state = _load(solution)
            state["stages"]["validation"]["artifacts"]["operatorNote"] = "commit-boundary edit"
            _write_unlocked(path, state)
            return built

        with mock.patch(
            f"{module}._build_reference_repair_plan",
            side_effect=edit_after_plan,
        ):
            with self.assertRaisesRegex(ValueError, "changed since repair planning"):
                apply_runtime_report_reference_repair(
                    self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
                )

    def test_future_passed_stage_writer_emits_canonical_and_legacy_references(self) -> None:
        path, state = _load(self.solution)
        state["stages"]["validation"]["status"] = "running"
        _write_unlocked(path, state)
        evidence = {
            "passed": True,
            "sentinelProvider": "azure-monitor-sdk",
            "sentinelReport": self.source_report.relative_to(self.solution).as_posix(),
            "graphReport": self.graph_report.relative_to(self.solution).as_posix(),
        }
        with (
            mock.patch("sentinel_xdr_migration.workflow.require_solution_conversion_scope"),
            mock.patch(
                "sentinel_xdr_migration.runtime.current_runtime_evidence",
                return_value=evidence,
            ),
        ):
            complete_workflow_stage(
                self.solution, "validation", status="passed", artifacts={},
            )
        artifacts = self._state()["stages"]["validation"]["artifacts"]
        self.assertEqual(artifacts["sentinelRuntimeReport"], artifacts["sentinelRuntimeJson"])
        self.assertEqual(
            self.source_report.relative_to(self.solution).as_posix(),
            artifacts["sentinelRuntimeJson"],
        )

    def test_future_source_waiver_stage_writer_emits_canonical_reference(self) -> None:
        path, state = _load(self.solution)
        state["stages"]["validation"]["status"] = "running"
        _write_unlocked(path, state)
        evidence = {
            "sourceWaiverOnlyBlocker": True,
            "sourceWhitelist": [{
                "table": "IdentityInfo",
                "rawFailure": {"status": "failed"},
                "applied": True,
            }],
            "sentinelProvider": "azure-monitor-sdk",
            "sentinelReport": self.source_report.relative_to(self.solution).as_posix(),
            "graphReport": self.graph_report.relative_to(self.solution).as_posix(),
        }
        with (
            mock.patch("sentinel_xdr_migration.workflow._validate_source_waiver_conversion_gates"),
            mock.patch(
                "sentinel_xdr_migration.workflow._source_whitelist_stage_artifacts",
                return_value={},
            ),
            mock.patch(
                "sentinel_xdr_migration.runtime.current_runtime_evidence",
                return_value=evidence,
            ),
        ):
            complete_workflow_stage(
                self.solution,
                "validation",
                status="passed",
                artifacts={"runtimeStatus": "source-waived"},
            )
        artifacts = self._state()["stages"]["validation"]["artifacts"]
        self.assertEqual(
            self.source_report.relative_to(self.solution).as_posix(),
            artifacts["sentinelRuntimeJson"],
        )
        self.assertEqual(
            artifacts["sentinelRuntimeReport"],
            artifacts["sentinelRuntimeJson"],
        )

    def test_qualification_target_lookup_does_not_materialize_missing_target(self) -> None:
        qualification = self.solution.parent / "ReadOnlyTarget"
        qualification.mkdir()
        run_id = initialize_workflow(
            qualification,
            workflow_profile="qualification",
            tenant_id="11111111-2222-4333-8444-555555555555",
            subscription_id="22222222-3333-4444-8555-666666666666",
            workspace_resource_id=(
                "/subscriptions/22222222-3333-4444-8555-666666666666/"
                "resourceGroups/QueryLab/providers/Microsoft.OperationalInsights/"
                "workspaces/QueryWorkspace"
            ),
            workspace_customer_id="33333333-4444-4555-8666-777777777777",
        )["runId"]
        target_path = artifact_path(qualification, TARGET_FILE_NAME)
        target_path.unlink(missing_ok=True)
        state_path, state = _load(qualification)
        with mock.patch(
            "sentinel_xdr_migration.target_context.write_target",
            side_effect=AssertionError("read-only target lookup attempted a write"),
        ) as write_target:
            target, fingerprint = _current_target(
                qualification, state, materialize_missing=False,
            )
        write_target.assert_not_called()
        self.assertTrue(target)
        self.assertTrue(fingerprint)
        self.assertFalse(target_path.exists())
        state["stages"]["validation"].update({
            "status": "passed",
            "attempts": 1,
            "startedAt": "2026-10-11T20:00:00Z",
            "completedAt": "2026-10-11T20:01:00Z",
            "message": None,
        })
        _write_unlocked(state_path, state)
        state_before = state_path.read_bytes()
        files_before = {
            path.relative_to(qualification).as_posix(): path.read_bytes()
            for path in qualification.rglob("*")
            if path.is_file()
        }
        with using_run(qualification, run_id), mock.patch(
            "sentinel_xdr_migration.target_context.write_target",
            side_effect=AssertionError("read-only planning attempted a target write"),
        ) as write_target:
            result = plan_runtime_report_reference_repair(qualification, run_id)
        self.assertFalse(result["eligible"])
        self.assertIn("runtime-validation.azure-monitor-sdk.json", result["reason"])
        write_target.assert_not_called()
        files_after = {
            path.relative_to(qualification).as_posix(): path.read_bytes()
            for path in qualification.rglob("*")
            if path.is_file()
        }
        self.assertEqual(files_before, files_after)
        self.assertEqual(state_before, artifact_path(qualification, "workflow-state.json").read_bytes())
        self.assertFalse(target_path.exists())


if __name__ == "__main__":
    unittest.main()
