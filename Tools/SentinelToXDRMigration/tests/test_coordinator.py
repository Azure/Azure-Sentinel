from __future__ import annotations

import json
import io
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration import coordinator
from sentinel_xdr_migration.cli import main as cli_main
from sentinel_xdr_migration.workflow import initialize_workflow, workflow_status


class CoordinatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temp.name)
        self.solution = self.root / "Solutions" / "Cisco"
        self.solution.mkdir(parents=True)
        self.registry = self.root / "coordinator" / "registry.json"
        self.run = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            version_bump="none",
        )["runId"]
        self.real_status = workflow_status(self.solution)
        self.stages = json.loads(
            Path(self.real_status["statePath"]).read_text(encoding="utf-8")
        )["stages"]
        self.next_stage = "discovery"
        self.workflow_state = self.real_status
        self._patches: list[mock._patch] = []
        self._install_fake_workflow()

    def tearDown(self) -> None:
        for patcher in reversed(self._patches):
            patcher.stop()
        self.temp.cleanup()

    def _install_fake_workflow(self) -> None:
        def get_status(solution: str | Path) -> dict:
            return {
                **self.workflow_state,
                "runId": self.run,
                "statePath": self.real_status["statePath"],
                "stages": self.stages,
                "context": {
                    **self.workflow_state.get("context", {}),
                    "workflowProfile": self.workflow_state.get("context", {}).get(
                        "workflowProfile", "authoring"
                    ),
                },
            }

        def get_next(solution: str | Path) -> dict:
            return {
                "runId": self.run,
                "next": self.next_stage,
                "blockedBy": [],
            }

        self._patches.extend([
            mock.patch.object(coordinator, "workflow_status", side_effect=get_status),
            mock.patch.object(coordinator, "next_workflow_stage", side_effect=get_next),
            mock.patch.object(
                coordinator,
                "runtime_validation_plan",
                return_value={
                    "rules": [{
                        "sentinelQuerySha256": "a" * 64,
                        "advancedHuntingQuerySha256": "b" * 64,
                    }]
                },
            ),
            mock.patch.object(
                coordinator,
                "current_runtime_evidence",
                return_value={
                    "sourceStatus": "blocked",
                    "graphReport": None,
                    "issues": ["runtime evidence is not complete"],
                },
            ),
        ])
        for patcher in self._patches[-4:]:
            patcher.start()

    def _enroll(self, *, owner: str = "solution-owner", dependencies: list[str] | None = None) -> dict:
        return coordinator.enroll(
            self.solution,
            owner=owner,
            required_shared_dependencies=dependencies,
            registry_path=self.registry,
        )

    def _qualification_run(self) -> None:
        self.workflow_state = initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            tenant_id="11111111-2222-4333-8444-555555555555",
            subscription_id="22222222-3333-4444-8555-666666666666",
            workspace_resource_id=(
                "/subscriptions/22222222-3333-4444-8555-666666666666/"
                "resourceGroups/rg/providers/Microsoft.OperationalInsights/workspaces/ws"
            ),
            workspace_customer_id="33333333-4444-4555-8666-777777777777",
            version_bump="none",
        )
        self.run = self.workflow_state["runId"]
        self.real_status = workflow_status(self.solution)
        self.stages = json.loads(
            Path(self.real_status["statePath"]).read_text(encoding="utf-8")
        )["stages"]

    def test_shadow_enrollment_produces_cisco_preflight_or_approval_decision(self) -> None:
        self._qualification_run()
        self.next_stage = "deployment"
        result = self._enroll()
        deployment = next(item for item in result["actions"] if item["actionId"] == "deployment")
        self.assertEqual("approval-needed", deployment["status"])
        self.assertEqual("customDetection", deployment["authPurpose"])
        self.assertIn("preflight", deployment["reason"])
        self.assertEqual(["preflight-deployment"], deployment["recommendedCommands"])
        self.assertFalse(deployment["serviceSettingsVerifiedByCoordinator"])
        self.assertFalse(deployment["authorizationGrantedByCoordinator"])
        self.assertEqual("shadow", result["dispatchMode"])
        self.assertFalse(result["automaticCommandExecution"])
        self.assertTrue(deployment["targetSha256"])
        with self.assertRaisesRegex(ValueError, "approval-needed"):
            coordinator.claim(
                self.solution,
                action_id="deployment",
                executor="ephemeral-executor",
                claim_key="claim-1",
                registry_path=self.registry,
            )

    def test_cli_registry_reconcile_and_status_entrypoints(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = cli_main([
                "coordinator-enroll",
                "--solution", str(self.solution),
                "--run-id", self.run,
                "--owner", "cli-owner",
                "--registry", str(self.registry),
            ])
        self.assertEqual(0, result)
        enrolled = json.loads(output.getvalue())
        self.assertEqual(self.run, enrolled["runId"])
        output.seek(0)
        output.truncate()
        with redirect_stdout(output):
            result = cli_main([
                "coordinator-status",
                "--solution", str(self.solution),
                "--run-id", self.run,
                "--registry", str(self.registry),
            ])
        self.assertEqual(0, result)
        current = json.loads(output.getvalue())
        self.assertEqual("cli-owner", current["owner"])
        self.assertEqual("shadow", current["dispatchMode"])

    def test_owner_handoff_is_explicit_and_audited(self) -> None:
        self._enroll(owner="current-owner")
        with self.assertRaisesRegex(ValueError, "only the current accountable owner"):
            coordinator.record_event(
                self.solution,
                event_id="unauthorized-handoff",
                kind="owner-handoff",
                actor="other-actor",
                new_owner="new-owner",
                reference="change-ticket",
                registry_path=self.registry,
            )
        handoff = coordinator.record_event(
            self.solution,
            event_id="authorized-handoff",
            kind="owner-handoff",
            actor="current-owner",
            new_owner="new-owner",
            reference="reviewed ownership transfer",
            registry_path=self.registry,
        )
        self.assertTrue(handoff["created"])
        self.assertEqual(
            "new-owner",
            coordinator.status(self.solution, registry_path=self.registry)["owner"],
        )

    def test_stale_package_inputs_still_require_existing_release_gate(self) -> None:
        self.next_stage = "packaging"
        self.stages["validation"]["status"] = "passed"
        next_info = mock.patch.object(
            coordinator,
            "next_workflow_stage",
            return_value={
                "runId": self.run,
                "next": "packaging",
                "blockedBy": [],
                "releaseActionRequired": True,
                "packageFreshness": {
                    "status": "stale",
                    "currentPackageInputSha256": "e" * 64,
                },
            },
        )
        next_info.start()
        self._patches.append(next_info)
        result = self._enroll()
        packaging = next(
            item for item in result["actions"] if item["actionId"] == "packaging"
        )
        self.assertEqual("approval-needed", packaging["status"])
        self.assertEqual("e" * 64, packaging["packageInputSha256"])
        self.assertEqual(["workflow-plan-package-release"], packaging["recommendedCommands"])

    def test_claim_and_event_are_idempotent_and_do_not_start_workflow(self) -> None:
        self._enroll()
        first = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="worker-1",
            claim_key="stable-claim",
            registry_path=self.registry,
        )
        replay = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="worker-1",
            claim_key="stable-claim",
            registry_path=self.registry,
        )
        self.assertEqual(first["claimId"], replay["claimId"])
        self.assertTrue(replay["idempotentReplay"])
        self.assertEqual("pending", self.stages["discovery"]["status"])
        evidence = self.solution / "completion.json"
        evidence.write_text('{"result":"passed"}', encoding="utf-8")
        self.stages["discovery"]["status"] = "passed"
        self.stages["discovery"]["artifacts"] = {"result": "completion.json"}
        self.next_stage = "conversion"
        first_event = coordinator.record_event(
            self.solution,
            event_id="completion-1",
            kind="executor-completed",
            action_id="discovery",
            target_sha256=None,
            evidence=evidence,
            registry_path=self.registry,
        )
        replay_event = coordinator.record_event(
            self.solution,
            event_id="completion-1",
            kind="executor-completed",
            action_id="discovery",
            target_sha256=None,
            evidence=evidence,
            registry_path=self.registry,
        )
        self.assertTrue(first_event["created"])
        self.assertFalse(replay_event["created"])
        self.assertEqual(first_event["evidenceSha256"], replay_event["evidenceSha256"])
        registry = json.loads(self.registry.read_text(encoding="utf-8"))
        self.assertEqual(1, len([e for e in registry["events"] if e["eventId"] == "completion-1"]))
        self.assertEqual("pending", self.stages["conversion"]["status"])

    def test_expired_executor_retains_owner_and_unknown_outcome_blocks_retry(self) -> None:
        self._enroll(owner="durable-solution-owner")
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="ephemeral-worker",
            claim_key="vanishing-worker",
            lease_seconds=0.1,
            registry_path=self.registry,
        )
        time.sleep(0.15)
        reconciled = coordinator.reconcile(self.solution, registry_path=self.registry)
        self.assertEqual("durable-solution-owner", reconciled["owner"])
        self.assertEqual("blocked", reconciled["actions"][0]["status"])
        self.assertEqual("expired-unknown", coordinator.status(
            self.solution, registry_path=self.registry
        )["claim"]["status"])
        self.assertIn("expired-claim-unknown", {
            warning["type"] for warning in coordinator.status(
                self.solution, registry_path=self.registry
            )["watchdog"]
        })
        with self.assertRaisesRegex(ValueError, "unknown outcome"):
            coordinator.claim(
                self.solution,
                action_id="discovery",
                executor="replacement-worker",
                claim_key="must-not-retry",
                registry_path=self.registry,
            )
        self.assertEqual(claim["claimId"], reconciled["actions"][0]["claimId"])
        owner_evidence = self.solution / "claim-reconciliation.json"
        owner_evidence.write_text('{"requestWasNotIssued":true}', encoding="utf-8")
        resolved = coordinator.record_event(
            self.solution,
            event_id="claim-not-started",
            kind="claim-resolved",
            claim_id=claim["claimId"],
            outcome="not-started",
            actor="durable-solution-owner",
            reference="reviewed local executor record",
            evidence=owner_evidence,
            registry_path=self.registry,
        )
        self.assertTrue(resolved["created"])
        replacement = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="replacement-after-evidence",
            claim_key="verified-not-started",
            registry_path=self.registry,
        )
        self.assertEqual("active", replacement["status"])

    def test_status_persists_expired_claim_and_blocks_the_action(self) -> None:
        self._enroll()
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="short-lived-worker",
            claim_key="status-expiry",
            lease_seconds=0.1,
            registry_path=self.registry,
        )
        time.sleep(0.15)
        current = coordinator.status(self.solution, registry_path=self.registry)
        self.assertEqual("expired-unknown", current["claim"]["status"])
        self.assertEqual("blocked", current["actions"][0]["status"])
        persisted = json.loads(self.registry.read_text(encoding="utf-8"))
        entry = next(iter(persisted["solutions"].values()))
        self.assertEqual("expired-unknown", entry["claim"]["status"])
        reconciled = coordinator.reconcile(self.solution, registry_path=self.registry)
        self.assertEqual("blocked", reconciled["actions"][0]["status"])
        self.assertEqual(claim["claimId"], entry["claim"]["claimId"])
        self.assertEqual(
            "expired-unknown",
            coordinator.status(self.solution, registry_path=self.registry)["claim"]["status"],
        )

    def test_authoritative_stage_evidence_resolves_expired_claim_exactly(self) -> None:
        self._enroll()
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="vanished-worker",
            claim_key="authoritative-completion",
            lease_seconds=0.1,
            registry_path=self.registry,
        )
        time.sleep(0.15)
        expired = coordinator.status(self.solution, registry_path=self.registry)
        self.assertEqual("expired-unknown", expired["claim"]["status"])

        evidence = self.solution / "completion.json"
        evidence.write_text('{"official":"passed"}', encoding="utf-8")
        self.stages["discovery"]["status"] = "passed"
        self.stages["discovery"]["artifacts"] = {"result": "completion.json"}
        self.next_stage = "conversion"
        unrelated = self.solution / "unrelated.json"
        unrelated.write_text('{"not":"official evidence"}', encoding="utf-8")
        coordinator.status(self.solution, registry_path=self.registry)
        with self.assertRaisesRegex(ValueError, "exact target, action, and official workflow evidence"):
            coordinator.record_event(
                self.solution,
                event_id="wrong-completion-evidence",
                kind="executor-completed",
                action_id="discovery",
                target_sha256=None,
                evidence=unrelated,
                registry_path=self.registry,
            )

        completion = coordinator.record_event(
            self.solution,
            event_id="official-completion",
            kind="executor-completed",
            action_id="discovery",
            target_sha256=None,
            evidence=evidence,
            registry_path=self.registry,
        )
        self.assertTrue(completion["consumed"])
        resolved = coordinator.status(self.solution, registry_path=self.registry)
        self.assertEqual(claim["claimId"], resolved["claim"]["claimId"])
        self.assertEqual("completed", resolved["claim"]["status"])
        self.assertEqual("passed", self.stages["discovery"]["status"])

    def test_claim_resolved_completed_requires_official_bound_evidence(self) -> None:
        self._enroll()
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="vanished-worker",
            claim_key="claim-resolution-completion",
            lease_seconds=0.1,
            registry_path=self.registry,
        )
        time.sleep(0.15)
        coordinator.status(self.solution, registry_path=self.registry)
        evidence = self.solution / "completion.json"
        evidence.write_text('{"official":"passed"}', encoding="utf-8")
        self.stages["discovery"]["status"] = "passed"
        self.stages["discovery"]["artifacts"] = {"result": "completion.json"}
        self.next_stage = "conversion"
        unrelated = self.solution / "unrelated.json"
        unrelated.write_text('{"not":"official evidence"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "exact current target and evidence"):
            coordinator.record_event(
                self.solution,
                event_id="claim-completed-without-target",
                kind="claim-resolved",
                claim_id=claim["claimId"],
                outcome="completed",
                actor="solution-owner",
                reference="reviewed official result",
                evidence=unrelated,
                registry_path=self.registry,
            )
        completed = coordinator.record_event(
            self.solution,
            event_id="claim-completed-authoritatively",
            kind="claim-resolved",
            claim_id=claim["claimId"],
            outcome="completed",
            actor="solution-owner",
            reference="reviewed official result",
            target_sha256=None,
            evidence=evidence,
            registry_path=self.registry,
        )
        self.assertTrue(completed["created"])
        current = coordinator.status(self.solution, registry_path=self.registry)
        self.assertEqual("completed", current["claim"]["status"])

    def test_active_claim_completion_survives_status_interleave(self) -> None:
        self._enroll()
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="completion-worker",
            claim_key="status-interleave",
            registry_path=self.registry,
        )
        evidence = self.solution / "discovery-result.json"
        evidence.write_text('{"result":"passed"}', encoding="utf-8")
        self.stages["discovery"]["status"] = "passed"
        self.stages["discovery"]["artifacts"] = {"result": "discovery-result.json"}
        self.next_stage = "conversion"

        current = coordinator.status(self.solution, registry_path=self.registry)
        self.assertEqual("active", current["claim"]["status"])
        persisted = json.loads(self.registry.read_text(encoding="utf-8"))
        entry = next(iter(persisted["solutions"].values()))
        self.assertEqual(claim["actionSha256"], entry["claim"]["action"]["actionSha256"])
        self.assertNotIn("discovery", {item["actionId"] for item in entry["actions"]})

        wrong_evidence = self.solution / "wrong-result.json"
        wrong_evidence.write_text('{"result":"not the official artifact"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "exact target, action, and official workflow evidence"):
            coordinator.record_event(
                self.solution,
                event_id="status-interleave-wrong-evidence",
                kind="executor-completed",
                action_id="discovery",
                target_sha256=claim["targetSha256"],
                evidence=wrong_evidence,
                registry_path=self.registry,
            )
        completion = coordinator.record_event(
            self.solution,
            event_id="status-interleave-completion",
            kind="executor-completed",
            action_id="discovery",
            target_sha256=claim["targetSha256"],
            evidence=evidence,
            registry_path=self.registry,
        )
        self.assertTrue(completion["consumed"])
        self.assertEqual(
            "completed",
            coordinator.status(self.solution, registry_path=self.registry)["claim"]["status"],
        )

    def test_active_claim_completion_survives_reconcile_interleave(self) -> None:
        self._enroll()
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="completion-worker",
            claim_key="reconcile-interleave",
            registry_path=self.registry,
        )
        evidence = self.solution / "discovery-result.json"
        evidence.write_text('{"result":"passed"}', encoding="utf-8")
        self.stages["discovery"]["status"] = "passed"
        self.stages["discovery"]["artifacts"] = {"result": "discovery-result.json"}
        self.next_stage = "conversion"

        coordinator.reconcile(self.solution, registry_path=self.registry)
        persisted = json.loads(self.registry.read_text(encoding="utf-8"))
        entry = next(iter(persisted["solutions"].values()))
        self.assertEqual("active", entry["claim"]["status"])
        self.assertEqual(claim["actionSha256"], entry["claim"]["action"]["actionSha256"])
        completion = coordinator.record_event(
            self.solution,
            event_id="reconcile-interleave-completion",
            kind="executor-completed",
            action_id="discovery",
            target_sha256=claim["targetSha256"],
            evidence=evidence,
            registry_path=self.registry,
        )
        self.assertTrue(completion["consumed"])
        self.assertEqual(
            "completed",
            coordinator.status(self.solution, registry_path=self.registry)["claim"]["status"],
        )

    def _assert_terminal_retry_handoff_uses_original_claim(
        self, terminal_status: str
    ) -> None:
        self._enroll()
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor=f"{terminal_status}-worker",
            claim_key=f"{terminal_status}-retry-handoff",
            registry_path=self.registry,
        )
        evidence = self.solution / f"{terminal_status}-result.json"
        evidence.write_text(
            json.dumps({"officialStatus": terminal_status}),
            encoding="utf-8",
        )
        self.stages["discovery"]["status"] = terminal_status
        self.stages["discovery"]["artifacts"] = {"result": evidence.name}
        self.next_stage = "discovery"

        refreshed = coordinator.status(self.solution, registry_path=self.registry)
        retry_action = next(
            item for item in refreshed["actions"]
            if item["actionId"] == "discovery"
        )
        self.assertNotEqual(claim["actionSha256"], retry_action["actionSha256"])
        self.assertEqual("blocked", retry_action["status"])
        persisted = json.loads(self.registry.read_text(encoding="utf-8"))
        entry = next(iter(persisted["solutions"].values()))
        self.assertEqual("active", entry["claim"]["status"])
        self.assertEqual(
            claim["actionSha256"],
            entry["claim"]["action"]["actionSha256"],
        )
        wrong_evidence = self.solution / "wrong-retry-evidence.json"
        wrong_evidence.write_text('{"not":"official"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "claim's exact target, action"):
            coordinator.record_event(
                self.solution,
                event_id=f"{terminal_status}-wrong-evidence",
                kind="executor-completed",
                action_id="discovery",
                target_sha256=claim["targetSha256"],
                evidence=wrong_evidence,
                registry_path=self.registry,
            )
        completion = coordinator.record_event(
            self.solution,
            event_id=f"{terminal_status}-authoritative-handoff",
            kind="executor-completed",
            action_id="discovery",
            target_sha256=claim["targetSha256"],
            evidence=evidence,
            registry_path=self.registry,
        )
        self.assertTrue(completion["consumed"])
        self.assertEqual(
            "completed",
            coordinator.status(self.solution, registry_path=self.registry)["claim"]["status"],
        )

    def test_failed_stage_handoff_uses_original_claim_action_on_retry(self) -> None:
        self._assert_terminal_retry_handoff_uses_original_claim("failed")

    def test_blocked_stage_handoff_uses_original_claim_action_on_retry(self) -> None:
        self._assert_terminal_retry_handoff_uses_original_claim("blocked")

    def test_claim_completion_rejects_stale_qualification_target(self) -> None:
        self._qualification_run()
        self._enroll()
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="qualification-worker",
            claim_key="stale-target-completion",
            registry_path=self.registry,
        )
        evidence = self.solution / "discovery-result.json"
        evidence.write_text('{"result":"passed"}', encoding="utf-8")
        self.stages["discovery"]["status"] = "passed"
        self.stages["discovery"]["artifacts"] = {"result": "discovery-result.json"}
        self.next_stage = "conversion"

        state_path = Path(self.real_status["statePath"])
        state_document = json.loads(state_path.read_text(encoding="utf-8"))
        changed_customer_id = "44444444-5555-4666-8777-888888888888"
        state_document["context"]["workspaceCustomerId"] = changed_customer_id
        state_path.write_text(json.dumps(state_document), encoding="utf-8")
        target_path = state_path.parent / "qualification-target.json"
        target_document = json.loads(target_path.read_text(encoding="utf-8"))
        target_document["workspaceCustomerId"] = changed_customer_id
        target_path.write_text(json.dumps(target_document), encoding="utf-8")
        self.workflow_state["context"]["workspaceCustomerId"] = changed_customer_id

        coordinator.reconcile(self.solution, registry_path=self.registry)
        persisted = json.loads(self.registry.read_text(encoding="utf-8"))
        entry = next(iter(persisted["solutions"].values()))
        self.assertEqual("stale", entry["claim"]["status"])
        with self.assertRaisesRegex(ValueError, "event target does not match the current locked target"):
            coordinator.record_event(
                self.solution,
                event_id="stale-target-completion",
                kind="executor-completed",
                action_id="discovery",
                target_sha256=claim["targetSha256"],
                evidence=evidence,
                registry_path=self.registry,
            )

    def test_recurrent_ready_decision_gets_a_fresh_outbox_delivery(self) -> None:
        self._enroll()
        initial = coordinator.status(self.solution, registry_path=self.registry)
        original = next(
            item for item in initial["outbox"]
            if item.get("kind") == "action-decision"
            and item["action"]["actionId"] == "discovery"
        )
        coordinator.acknowledge_outbox(
            self.solution,
            delivery_id=original["deliveryId"],
            actor="delivery-adapter",
            registry_path=self.registry,
        )
        claim = coordinator.claim(
            self.solution,
            action_id="discovery",
            executor="temporary-worker",
            claim_key="decision-recurrence",
            lease_seconds=0.02,
            registry_path=self.registry,
        )
        time.sleep(0.04)
        coordinator.reconcile(self.solution, registry_path=self.registry)
        evidence = self.solution / "not-started.json"
        evidence.write_text('{"requestIssued":false}', encoding="utf-8")
        coordinator.record_event(
            self.solution,
            event_id="resolve-recurrence",
            kind="claim-resolved",
            claim_id=claim["claimId"],
            outcome="not-started",
            actor="solution-owner",
            reference="checked executor ledger",
            evidence=evidence,
            registry_path=self.registry,
        )
        ready = coordinator.status(self.solution, registry_path=self.registry)
        recurrent = [
            item for item in ready["outbox"]
            if item.get("kind") == "action-decision"
            and item.get("action", {}).get("actionId") == "discovery"
            and item.get("status") == "pending"
        ]
        self.assertTrue(recurrent)
        self.assertNotEqual(original["deliveryId"], recurrent[-1]["deliveryId"])
        self.assertGreater(
            recurrent[-1]["decisionGeneration"],
            original["decisionGeneration"],
        )

    def test_same_event_id_is_idempotent_only_within_its_run(self) -> None:
        self._enroll(owner="accountable-owner")
        first = coordinator.record_event(
            self.solution,
            event_id="cross-run-handoff",
            kind="owner-handoff",
            actor="accountable-owner",
            new_owner="next-owner",
            reference="handoff-ticket",
            registry_path=self.registry,
        )
        self.assertTrue(first["created"])

        first_solution = self.solution
        second_solution = self.root / "Solutions" / "Cisco-Second-Run"
        second_solution.mkdir(parents=True)
        self.solution = second_solution
        self.workflow_state = initialize_workflow(
            self.solution,
            workflow_profile="authoring",
            version_bump="none",
        )
        self.run = self.workflow_state["runId"]
        self.real_status = workflow_status(self.solution)
        self.stages = json.loads(
            Path(self.real_status["statePath"]).read_text(encoding="utf-8")
        )["stages"]
        self.next_stage = "discovery"
        self._enroll(owner="accountable-owner")
        second = coordinator.record_event(
            self.solution,
            event_id="cross-run-handoff",
            kind="owner-handoff",
            actor="accountable-owner",
            new_owner="next-owner",
            reference="handoff-ticket",
            registry_path=self.registry,
        )
        self.assertTrue(second["created"])
        self.assertEqual(first["eventId"], second["eventId"])
        persisted = json.loads(self.registry.read_text(encoding="utf-8"))
        matching = [
            item for item in persisted["events"]
            if item["eventId"] == "cross-run-handoff"
        ]
        self.assertEqual(2, len(matching))
        self.assertNotEqual(
            matching[0]["payload"]["entryId"],
            matching[1]["payload"]["entryId"],
        )
        self.assertNotEqual(first_solution, self.solution)

    def test_watchdog_reports_missing_owner_idle_work_and_unconsumed_handoff(self) -> None:
        self._enroll()
        registry_document = json.loads(self.registry.read_text(encoding="utf-8"))
        next(iter(registry_document["solutions"].values()))["owner"] = None
        self.registry.write_text(json.dumps(registry_document), encoding="utf-8")
        stale = coordinator.status(
            self.solution,
            registry_path=self.registry,
            idle_seconds=0,
        )
        self.assertIn("missing-owner", {item["type"] for item in stale["watchdog"]})

        self._enroll(owner="reassigned-owner")
        ready = coordinator.status(
            self.solution,
            registry_path=self.registry,
            idle_seconds=0,
        )
        self.assertIn("ready-idle", {item["type"] for item in ready["watchdog"]})
        handoff = self.solution / "unmatched-handoff.json"
        handoff.write_text('{"stage":"not-yet-finished"}', encoding="utf-8")
        event = coordinator.record_event(
            self.solution,
            event_id="unfinished-handoff",
            kind="executor-completed",
            action_id="discovery",
            target_sha256=None,
            evidence=handoff,
            registry_path=self.registry,
        )
        self.assertFalse(event["consumed"])
        current = coordinator.status(
            self.solution,
            registry_path=self.registry,
            idle_seconds=0,
        )
        warnings = {item["type"] for item in current["watchdog"]}
        self.assertIn("unconsumed-handoff", warnings)
        self.assertIn("ready-idle", warnings)

    def test_restart_keeps_pending_outbox_and_ack_does_not_grant_approval(self) -> None:
        self._qualification_run()
        self.next_stage = "deployment"
        enrolled = self._enroll()
        approval = coordinator.record_event(
            self.solution,
            event_id="deployment-approval-request",
            kind="approval-requested",
            action_id="deployment",
            purpose="customDetection",
            target_sha256=enrolled["target"]["sha256"],
            actor="solution-owner",
            registry_path=self.registry,
        )
        self.assertFalse(approval["approvalGranted"])
        pending = next(
            item for item in approval["reconciliation"]["outbox"]
            if item["kind"] == "approval-request"
        )
        restarted = coordinator.status(self.solution, registry_path=self.registry)
        self.assertIn(
            pending["deliveryId"],
            {item["deliveryId"] for item in restarted["outbox"]},
        )
        self.assertIn(
            "undelivered-approval",
            {
                item["type"]
                for item in coordinator.status(
                    self.solution,
                    registry_path=self.registry,
                    idle_seconds=0,
                )["watchdog"]
            },
        )
        ack = coordinator.acknowledge_outbox(
            self.solution,
            delivery_id=pending["deliveryId"],
            actor="adapter",
            registry_path=self.registry,
        )
        self.assertFalse(ack["approvalGranted"])
        current = coordinator.status(self.solution, registry_path=self.registry)
        self.assertEqual("approval-needed", current["actions"][0]["status"])
        acked = next(item for item in current["outbox"] if item["deliveryId"] == pending["deliveryId"])
        self.assertEqual("acknowledged", acked["status"])

    def test_validation_source_completion_is_independent_of_xdr_blocker(self) -> None:
        self.stages["conversion"]["status"] = "passed"
        self.stages["validation"]["status"] = "blocked"
        self.next_stage = "validation"
        graph_report = self.solution / "Logs" / "sentinel-xdr-migration" / self.run / "runtime-validation.graph.json"
        graph_report.parent.mkdir(parents=True, exist_ok=True)
        graph_report.write_text('{"status":"failed"}', encoding="utf-8")
        patcher = mock.patch.object(
            coordinator,
            "current_runtime_evidence",
            return_value={
                "sourceStatus": "passed",
                "graphReport": None,
                "issues": ["Advanced Hunting is blocked"],
            },
        )
        patcher.start()
        self._patches.append(patcher)
        result = self._enroll()
        actions = {item["actionId"]: item for item in result["actions"]}
        self.assertEqual("complete", actions["validation:sentinel-runtime"]["status"])
        self.assertEqual("blocked", actions["validation:advanced-hunting"]["status"])
        self.assertEqual("validation", result["nextStage"])

    def test_source_query_remains_independently_actionable_under_xdr_blocker(self) -> None:
        self.stages["conversion"]["status"] = "passed"
        self.stages["validation"]["status"] = "blocked"
        self.next_stage = "validation"
        graph_report = self.solution / "Logs" / "sentinel-xdr-migration" / self.run / "runtime-validation.graph.json"
        graph_report.parent.mkdir(parents=True, exist_ok=True)
        graph_report.write_text('{"status":"failed"}', encoding="utf-8")
        patcher = mock.patch.object(
            coordinator,
            "current_runtime_evidence",
            return_value={
                "sourceStatus": "blocked",
                "graphReport": None,
                "issues": ["Advanced Hunting query failed"],
            },
        )
        patcher.start()
        self._patches.append(patcher)
        result = self._enroll()
        actions = {item["actionId"]: item for item in result["actions"]}
        self.assertEqual("approval-needed", actions["validation:sentinel-runtime"]["status"])
        self.assertEqual("blocked", actions["validation:advanced-hunting"]["status"])

    def test_advanced_hunting_and_custom_detection_dependencies_are_purpose_scoped(self) -> None:
        self._qualification_run()
        self.stages["conversion"]["status"] = "passed"
        self.next_stage = "validation"
        declarations = [
            "validation:advanced-hunting=graph-auth:advancedHunting",
            "validation:advanced-hunting=graph-auth:customDetection",
        ]
        enrolled = self._enroll(dependencies=declarations)
        target_hash = enrolled["target"]["sha256"]
        evidence = self.solution / "graph-auth.json"
        evidence.write_text('{"granted":true}', encoding="utf-8")
        event = coordinator.record_event(
            self.solution,
            event_id="ah-auth-ready",
            kind="shared-dependency-completed",
            action_id="graph-auth",
            purpose="advancedHunting",
            target_sha256=target_hash,
            evidence=evidence,
            actor="identity-owner",
            registry_path=self.registry,
        )
        self.assertTrue(event["created"])
        reconciled = coordinator.reconcile(self.solution, registry_path=self.registry)
        hunting = next(
            item for item in reconciled["actions"]
            if item["actionId"] == "validation:advanced-hunting"
        )
        purposes = {item["purpose"]: item["status"] for item in hunting["sharedPrerequisites"]}
        self.assertEqual("reported", purposes["advancedHunting"])
        self.assertEqual("missing", purposes["customDetection"])
        self.assertEqual("blocked", hunting["status"])

    def test_stale_target_or_query_approval_is_not_claimable(self) -> None:
        self._qualification_run()
        self.stages["conversion"]["status"] = "passed"
        self.next_stage = "validation"
        enrolled = self._enroll()
        hunting = next(
            item for item in enrolled["actions"]
            if item["actionId"] == "validation:advanced-hunting"
        )
        event = coordinator.record_event(
            self.solution,
            event_id="approval-1",
            kind="approval-requested",
            action_id=hunting["actionId"],
            purpose="advancedHunting",
            target_sha256=enrolled["target"]["sha256"],
            actor="operator",
            registry_path=self.registry,
        )
        self.assertFalse(event["approvalGranted"])
        approval_delivery_id = next(
            item["deliveryId"]
            for item in event["reconciliation"]["outbox"]
            if item.get("eventId") == "approval-1"
        )
        changed_plan = mock.patch.object(
            coordinator,
            "runtime_validation_plan",
            return_value={
                "rules": [{
                    "sentinelQuerySha256": "c" * 64,
                    "advancedHuntingQuerySha256": "d" * 64,
                }]
            },
        )
        changed_plan.start()
        self._patches.append(changed_plan)
        refreshed = coordinator.reconcile(self.solution, registry_path=self.registry)
        fresh = next(
            item for item in refreshed["actions"]
            if item["actionId"] == "validation:advanced-hunting"
        )
        self.assertNotEqual(hunting["actionSha256"], fresh["actionSha256"])
        after_query_change = coordinator.status(
            self.solution,
            registry_path=self.registry,
        )
        stale_approval = next(
            item for item in after_query_change["outbox"]
            if item["deliveryId"] == approval_delivery_id
        )
        self.assertEqual("superseded", stale_approval["status"])
        state_path = Path(self.real_status["statePath"])
        state_document = json.loads(state_path.read_text(encoding="utf-8"))
        state_context = state_document["context"]
        changed_customer_id = "44444444-5555-4666-8777-888888888888"
        state_context["workspaceCustomerId"] = changed_customer_id
        state_path.write_text(json.dumps(state_document), encoding="utf-8")
        target_path = Path(self.real_status["statePath"]).parent / "qualification-target.json"
        target_document = json.loads(target_path.read_text(encoding="utf-8"))
        target_document["workspaceCustomerId"] = changed_customer_id
        target_path.write_text(json.dumps(target_document), encoding="utf-8")
        self.workflow_state["context"]["workspaceCustomerId"] = changed_customer_id
        coordinator.reconcile(self.solution, registry_path=self.registry)
        with self.assertRaisesRegex(ValueError, "not claimable"):
            coordinator.claim(
                self.solution,
                action_id="validation:advanced-hunting",
                executor="dispatcher",
                claim_key="approval-cannot-dispatch",
                registry_path=self.registry,
            )
        with self.assertRaisesRegex(ValueError, "target does not match"):
            coordinator.record_event(
                self.solution,
                event_id="stale-approval",
                kind="approval-requested",
                action_id=fresh["actionId"],
                purpose="advancedHunting",
                target_sha256="0" * 64,
                actor="operator",
                registry_path=self.registry,
            )


if __name__ == "__main__":
    unittest.main()
