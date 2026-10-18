from __future__ import annotations

import json
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sentinel_xdr_migration.budget import (
    BudgetExhausted,
    BudgetReceiptError,
    BudgetUnknown,
    begin_operation,
    budget_summary,
    create_or_link_campaign,
    extend_budget,
    finish_operation,
    measured_operation,
    reconcile_legacy_usage,
    reconcile_pending_operation,
    set_observation_deadline,
)
from sentinel_xdr_migration.artifacts import create_run


INVENTORY = "a" * 64
RULES = ["11111111-1111-1111-1111-111111111111"]


class CampaignBudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.solution = Path(self.temp.name) / "Sample"
        self.solution.mkdir()
        create_run(self.solution, run_id="run-1")
        self.campaign_id = "campaign-a"
        create_or_link_campaign(
            self.solution,
            self.campaign_id,
            inventory_sha256=INVENTORY,
            run_id="run-1",
            rule_ids=RULES,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _begin(self, dimension: str, **kwargs):
        if dimension == "ruleRevision":
            kwargs.setdefault("metadata", {
                "inputSha256": "b" * 64,
                "evidenceSha256": "c" * 64,
                "proposedChangeSha256": "d" * 64,
            })
        return begin_operation(
            self.solution,
            self.campaign_id,
            inventory_sha256=INVENTORY,
            run_id="run-1",
            dimension=dimension,
            **kwargs,
        )

    def _finish(self, receipt: dict, *, status: str = "passed", elapsed: float = 0):
        return finish_operation(
            self.solution,
            self.campaign_id,
            receipt["operationId"],
            status=status,
            elapsed_seconds=elapsed,
        )

    def test_conversion_limit_boundary_and_audited_extension(self) -> None:
        for _ in range(3):
            receipt = self._begin("conversionPass")
            self._finish(receipt, status="failed")
        with self.assertRaises(BudgetExhausted):
            self._begin("conversionPass")
        summary = budget_summary(self.solution, self.campaign_id)
        self.assertEqual(summary["usage"]["conversionPasses"], 3)
        self.assertEqual(summary["remaining"]["conversionPasses"], 0)
        # Read-only status/evidence remains available after a budget stop.
        self.assertEqual(
            3,
            budget_summary(self.solution, self.campaign_id)["usage"]["conversionPasses"],
        )
        extended = extend_budget(
            self.solution,
            self.campaign_id,
            dimension="conversionPasses",
            new_limit=4,
            actor="owner",
            reason="approved retry",
            evidence_reference="approval-42",
        )
        self.assertEqual(extended["remaining"]["conversionPasses"], 1)
        receipt = self._begin("conversionPass")
        self._finish(receipt)
        self.assertEqual(
            budget_summary(self.solution, self.campaign_id)["usage"]["conversionPasses"],
            4,
        )

    def test_rule_limit_per_rule_and_active_time_is_measured_not_waited(self) -> None:
        rule_id = RULES[0]
        for elapsed in (1.25, 2.5, 0.75):
            receipt = self._begin("ruleRevision", item_id=rule_id)
            self._finish(receipt, elapsed=elapsed)
        summary = budget_summary(self.solution, self.campaign_id)
        self.assertEqual(summary["usage"]["ruleRevisions"][rule_id], 3)
        self.assertEqual(summary["usage"]["ruleActiveSeconds"][rule_id], 4.5)
        self.assertEqual(summary["usage"]["activeExecutionSeconds"], 4.5)
        with self.assertRaises(BudgetExhausted):
            self._begin("ruleRevision", item_id=rule_id)

    def test_failed_cancelled_and_provider_retry_attempts_are_consumed(self) -> None:
        failed = self._begin("providerHttpAttempt")
        self._finish(failed, status="failed", elapsed=0.4)

        def _cancelled_attempt() -> None:
            with measured_operation(
                self.solution,
                self.campaign_id,
                inventory_sha256=INVENTORY,
                run_id="run-1",
                dimension="providerHttpAttempt",
            ):
                raise RuntimeError("cancel")

        self.assertRaisesRegex(RuntimeError, "cancel", _cancelled_attempt)
        summary = budget_summary(self.solution, self.campaign_id)
        self.assertEqual(summary["usage"]["providerHttpAttempts"], 2)
        self.assertGreater(summary["usage"]["activeExecutionSeconds"], 0.4)
        self.assertEqual(summary["usage"]["pendingOperations"], [])

    def test_ingestion_unknown_reconciliation_prevents_replay(self) -> None:
        arguments = {
            "item_id": "pair-1/fixture-1",
            "approval_reference": "write-approval-1",
            "attempt_marker": "marker-1",
        }
        pending = self._begin("ingestionSubmission", **arguments)
        with self.assertRaises(BudgetUnknown):
            self._begin("ingestionSubmission", **arguments)
        reconcile_pending_operation(
            self.solution,
            self.campaign_id,
            pending["operationId"],
            status="unknown",
            elapsed_seconds=2.0,
            actor="owner",
            reason="submission outcome reconciled as unknown",
            evidence_reference="provider-receipt-1",
        )
        with self.assertRaises(BudgetExhausted):
            self._begin("ingestionSubmission", **arguments)
        # A genuinely new attempt has a new marker and a new exact-scope approval.
        fresh = self._begin(
            "ingestionSubmission",
            item_id="pair-1/fixture-1",
            approval_reference="write-approval-2",
            attempt_marker="marker-2",
        )
        self._finish(fresh, status="passed", elapsed=1)
        self.assertEqual(
            budget_summary(self.solution, self.campaign_id)["usage"]["ingestionSubmissions"],
            2,
        )

    def test_unknown_legacy_usage_blocks_until_explicit_evidence_reconciliation(self) -> None:
        other = self.solution
        create_run(other, run_id="old-run")
        create_or_link_campaign(
            other,
            "legacy",
            inventory_sha256=INVENTORY,
            run_id="old-run",
            rule_ids=RULES,
            legacy_usage_unknown=True,
        )
        with self.assertRaises(BudgetUnknown):
            begin_operation(
                other, "legacy", inventory_sha256=INVENTORY,
                run_id="old-run", dimension="conversionPass",
            )
        baseline = {
            "activeExecutionSeconds": 12.0,
            "conversionPasses": 1,
            "packageBuilds": 0,
            "providerHttpAttempts": 4,
            "ingestionSubmissions": 0,
            "ruleRevisions": {RULES[0]: 1},
            "ruleActiveSeconds": {RULES[0]: 8.0},
        }
        reconciled = reconcile_legacy_usage(
            other,
            "legacy",
            consumed=baseline,
            actor="owner",
            reason="reviewed preserved artifacts and provider logs",
            evidence_reference="legacy-usage-review-17",
        )
        self.assertEqual(reconciled["legacyUsageStatus"], "known")
        self.assertEqual(reconciled["usage"]["conversionPasses"], 1)
        for _ in range(2):
            next_receipt = begin_operation(
                other, "legacy", inventory_sha256=INVENTORY,
                run_id="old-run", dimension="ruleRevision", item_id=RULES[0],
                metadata={
                    "inputSha256": "b" * 64,
                    "evidenceSha256": "c" * 64,
                    "proposedChangeSha256": "d" * 64,
                },
            )
            finish_operation(
                other, "legacy", next_receipt["operationId"],
                status="passed", elapsed_seconds=0.01,
            )
        with self.assertRaises(BudgetExhausted):
            begin_operation(
                other, "legacy", inventory_sha256=INVENTORY,
                run_id="old-run", dimension="ruleRevision", item_id=RULES[0],
                metadata={
                    "inputSha256": "b" * 64,
                    "evidenceSha256": "c" * 64,
                    "proposedChangeSha256": "d" * 64,
                },
            )

    def test_linked_replacement_run_shares_campaign_and_inventory_binding(self) -> None:
        receipt = self._begin("packageBuild")
        self._finish(receipt)
        replacement = create_or_link_campaign(
            self.solution,
            self.campaign_id,
            inventory_sha256=INVENTORY,
            run_id="replacement-run",
            rule_ids=RULES,
        )
        self.assertEqual(replacement["usage"]["packageBuilds"], 1)
        self.assertEqual(replacement["linkedRunIds"], ["run-1", "replacement-run"])
        with self.assertRaises(BudgetReceiptError):
            create_or_link_campaign(
                self.solution,
                self.campaign_id,
                inventory_sha256="b" * 64,
                run_id="replacement-2",
                rule_ids=RULES,
            )
        with self.assertRaises(ValueError):
            create_or_link_campaign(
                self.solution,
                "../escape",
                inventory_sha256=INVENTORY,
                run_id="replacement-2",
                rule_ids=RULES,
            )

    def test_concurrent_work_never_spends_more_than_campaign_limit(self) -> None:
        def attempt(_: int) -> bool:
            for _ in range(20):
                try:
                    with measured_operation(
                        self.solution,
                        self.campaign_id,
                        inventory_sha256=INVENTORY,
                        run_id="run-1",
                        dimension="conversionPass",
                    ):
                        time.sleep(0.003)
                    return True
                except BudgetUnknown:
                    time.sleep(0.001)
                except BudgetExhausted:
                    return False
            return False

        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(attempt, range(8)))
        summary = budget_summary(self.solution, self.campaign_id)
        self.assertEqual(sum(outcomes), 3)
        self.assertEqual(summary["usage"]["conversionPasses"], 3)
        self.assertEqual(summary["usage"]["pendingOperations"], [])

    def test_observation_deadline_is_schedule_aware_and_wait_is_not_active(self) -> None:
        past = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        set_observation_deadline(
            self.solution,
            self.campaign_id,
            test_id="test-past",
            deadline_at=past,
            approval_reference="approval-test-1",
            actor="owner",
            reason="approved schedule window",
        )
        with self.assertRaises(BudgetExhausted):
            self._begin("alertObservationPoll", test_id="test-past")
        self.assertEqual(
            budget_summary(self.solution, self.campaign_id)["usage"]["activeExecutionSeconds"],
            0,
        )
        future = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        set_observation_deadline(
            self.solution,
            self.campaign_id,
            test_id="test-future",
            deadline_at=future,
            approval_reference="approval-test-2",
            actor="owner",
            reason="approved schedule window",
        )
        time.sleep(0.02)
        receipt = self._begin("alertObservationPoll", test_id="test-future")
        self._finish(receipt, elapsed=0.25)
        self.assertEqual(
            0.25,
            budget_summary(self.solution, self.campaign_id)["usage"]["activeExecutionSeconds"],
        )

    def test_tampered_receipt_hash_is_rejected(self) -> None:
        receipt = self._begin("conversionPass")
        self._finish(receipt)
        path = (
            self.solution / "Logs" / "sentinel-xdr-migration-campaigns"
            / self.campaign_id / "budget.json"
        )
        self.assertFalse(
            (self.solution / "Logs" / "sentinel-xdr-migration" / "run-1" / "campaigns").exists()
        )
        document = json.loads(path.read_text())
        valid = json.dumps(document)
        document["receipts"][0]["runId"] = "tampered"
        path.write_text(json.dumps(document))
        with self.assertRaises(BudgetReceiptError):
            budget_summary(self.solution, self.campaign_id)
        document = json.loads(valid)
        document["schemaVersion"] = "2.0.0"
        path.write_text(json.dumps(document))
        with self.assertRaises(BudgetReceiptError):
            budget_summary(self.solution, self.campaign_id)


if __name__ == "__main__":
    unittest.main()
