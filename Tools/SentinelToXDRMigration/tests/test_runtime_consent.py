from __future__ import annotations

import json
import hashlib
import threading
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import yaml

from sentinel_xdr_migration import cli
from sentinel_xdr_migration.artifacts import artifact_path, existing_artifact_path
from sentinel_xdr_migration.runtime_consent import (
    build_runtime_query_plan,
    confirm_primary_lab_setting,
    persist_runtime_query_plan,
    record_runtime_query_consent,
    revoke_runtime_query_consent,
    require_runtime_query_consent,
    runtime_query_consent_status,
)
from sentinel_xdr_migration import runtime_consent
from sentinel_xdr_migration.runtime import (
    record_runtime_validation,
    validate_advanced_hunting,
    validate_sentinel_sdk,
)
from sentinel_xdr_migration.target_context import require_locked_target
from sentinel_xdr_migration.workflow import initialize_workflow

TENANT_ID = "11111111-2222-4333-8444-555555555555"
SUBSCRIPTION_ID = "22222222-3333-4444-8555-666666666666"
CUSTOMER_ID = "33333333-4444-4555-8666-777777777777"
WORKSPACE = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/QueryLab/"
    "providers/Microsoft.OperationalInsights/workspaces/QueryWorkspace"
)
SOURCE = "sentinelSourceQueryFamily"
XDR = "defenderXdrQueryFamily"


class RuntimeQueryConsentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.solution = self.base / "Solutions" / "QueryConsent"
        self.solution.mkdir(parents=True)
        self.state_dir = self.base / "auth-state"
        patcher = mock.patch(
            "sentinel_xdr_migration.runtime_consent._state_dir",
            return_value=self.state_dir,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        profile_patcher = mock.patch(
            "sentinel_xdr_migration.runtime_consent.configured_azure_cli_profile",
            return_value=str(self.base / "isolated-azure-profile"),
        )
        profile_patcher.start()
        self.addCleanup(profile_patcher.stop)
        no_az = mock.patch(
            "sentinel_xdr_migration.runtime_consent.shutil.which",
            return_value=None,
        )
        no_az.start()
        self.addCleanup(no_az.stop)
        self._write_source("SecurityEvent | take 5", "11111111-2222-3333-4444-555555555555")
        self._write_xdr("DeviceEvents | take 5", "xdr-11111111-2222-3333-4444-555555555555")
        initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            tenant_id=TENANT_ID,
            subscription_id=SUBSCRIPTION_ID,
            workspace_resource_id=WORKSPACE,
            workspace_customer_id=CUSTOMER_ID,
        )
        self._confirm_primary(self.solution)

    def _confirm_primary(self, solution: Path, name: str = "qualification-primary") -> dict:
        return confirm_primary_lab_setting(
            solution,
            actor="reviewer@example.test",
            primary_setting_name=name,
            confirmed=True,
        )

    def _write_source(self, query: str, rule_id: str, name: str = "Rule.yaml") -> Path:
        path = self.solution / "Analytic Rules" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump({"id": rule_id, "query": query}),
            encoding="utf-8",
        )
        return path

    def _write_xdr(self, query: str, rule_id: str, name: str = "Rule.yaml") -> Path:
        path = self.solution / "XDR Detections" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(
                {
                    "kind": "CustomDetection",
                    "id": rule_id,
                    "properties": {
                        "queryCondition": {"queryText": query},
                        "detectionAction": {"alertTemplate": {}},
                    },
                }
            ),
            encoding="utf-8",
        )
        return path

    def _approve(self, *families: str, source_provider: str = "azure-monitor-sdk") -> dict:
        if build_runtime_query_plan(
            self.solution,
            source_provider=source_provider,
        )["labReadConsent"]["status"] == "requires-explicit-primary-setting-confirmation":
            self._confirm_primary(self.solution)
        plan = build_runtime_query_plan(
            self.solution,
            source_provider=source_provider,
        )
        return record_runtime_query_consent(
            self.solution,
            expected_plan_sha256=plan["planSha256"],
            actor="reviewer@example.test",
            approved_families=list(families),
            source_provider=source_provider,
        )

    def _latest_decision_record(self) -> dict:
        paths = list(
            (self.state_dir / "lab-runtime-access").glob(
                "*.runtime-query-decision.json"
            )
        )
        self.assertEqual(1, len(paths))
        return json.loads(paths[0].read_text(encoding="utf-8"))

    def test_plan_shows_exact_locked_scope_and_query_families(self) -> None:
        plan = build_runtime_query_plan(self.solution)
        self.assertEqual("qualification", plan["workflowProfile"])
        self.assertEqual("QueryLab", plan["target"]["resourceGroup"])
        self.assertEqual(WORKSPACE, plan["target"]["workspaceResourceId"])
        self.assertEqual(CUSTOMER_ID, plan["target"]["workspaceCustomerId"])
        self.assertEqual(1, plan["families"][SOURCE]["ruleCount"])
        self.assertEqual(1, plan["families"][XDR]["ruleCount"])
        self.assertEqual(
            "SecurityEvent | take 5",
            plan["families"][SOURCE]["queries"][0]["queryText"],
        )
        self.assertEqual(
            "azure-monitor-sdk",
            plan["families"][SOURCE]["provider"]["provider"],
        )
        self.assertFalse(plan["families"][SOURCE]["provider"]["authentication"]["interactiveSignInPermittedByThisConsent"])
        self.assertFalse(plan["authorizationBoundary"]["environmentWritesAuthorized"])

    def test_both_and_each_independent_family_can_be_selected(self) -> None:
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent.shutil.which",
            return_value="/usr/bin/az",
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent.subprocess.run",
            return_value=mock.Mock(
                returncode=0,
                stdout=json.dumps({"tenantId": TENANT_ID}),
                stderr="",
            ),
        ):
            self.assertEqual(
                sorted([SOURCE, XDR]),
                self._approve(SOURCE, XDR)["approvedFamilies"],
            )
            self.assertEqual("approved", require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )["status"])
        self.assertEqual(
            sorted([SOURCE, XDR]),
            runtime_query_consent_status(self.solution)["approvedFamilies"],
        )

        for index, family in enumerate((SOURCE, XDR), start=1):
            with self.subTest(family=family):
                isolated = self.base / "Solutions" / f"Family{index}"
                isolated.mkdir()
                (isolated / "Analytic Rules").mkdir()
                (isolated / "XDR Detections").mkdir()
                (isolated / "Analytic Rules" / "Rule.yaml").write_text(
                    yaml.safe_dump(
                        {
                            "id": "11111111-2222-3333-4444-555555555555",
                            "query": "SecurityEvent | take 1",
                        }
                    ),
                    encoding="utf-8",
                )
                (isolated / "XDR Detections" / "Rule.yaml").write_text(
                    yaml.safe_dump(
                        {
                            "kind": "CustomDetection",
                            "id": "xdr-11111111-2222-3333-4444-555555555555",
                            "properties": {
                                "queryCondition": {"queryText": "DeviceEvents | take 1"},
                                "detectionAction": {"alertTemplate": {}},
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                initialize_workflow(
                    isolated,
                    workflow_profile="qualification",
                    tenant_id=TENANT_ID,
                    subscription_id=SUBSCRIPTION_ID,
                    workspace_resource_id=(
                        WORKSPACE.replace("QueryWorkspace", f"QueryWorkspace{index}")
                    ),
                    workspace_customer_id=f"{CUSTOMER_ID[:-1]}{index}",
                )
                self._confirm_primary(isolated)
                plan = build_runtime_query_plan(isolated)
                record_runtime_query_consent(
                    isolated,
                    expected_plan_sha256=plan["planSha256"],
                    actor="reviewer@example.test",
                    approved_families=[family],
                )
                with self.assertRaisesRegex(ValueError, "does not approve"):
                    require_runtime_query_consent(
                        isolated,
                        family=XDR if family == SOURCE else SOURCE,
                        provider="graph" if family == SOURCE else "azure-monitor-sdk",
                    )

    def test_decline_revision_and_no_selection_never_approve(self) -> None:
        plan = build_runtime_query_plan(self.solution)
        with self.assertRaisesRegex(ValueError, "select at least one"):
            record_runtime_query_consent(
                self.solution,
                expected_plan_sha256=plan["planSha256"],
                actor="reviewer",
                approved_families=[],
            )
        declined = record_runtime_query_consent(
            self.solution,
            expected_plan_sha256=plan["planSha256"],
            actor="reviewer",
            approved_families=[],
            declined=True,
            reason="Defer runtime queries.",
        )
        self.assertEqual("declined", declined["status"])
        self.assertTrue(declined["decisionRecorded"])
        self.assertFalse(declined["consentRecorded"])
        decision = json.loads(Path(declined["decisionPath"]).read_text())
        self.assertEqual("reviewer", decision["actor"])
        self.assertEqual("Defer runtime queries.", decision["reason"])
        self.assertFalse(decision["authorizesRuntimeQueries"])
        self.assertFalse(decision["revokesExistingGrant"])
        self.assertEqual("declined", self._latest_decision_record()["status"])
        self.assertEqual("not-approved", runtime_query_consent_status(self.solution)["families"][SOURCE]["status"])
        with self.assertRaisesRegex(ValueError, "not approved"):
            require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )
        revised = record_runtime_query_consent(
            self.solution,
            expected_plan_sha256=build_runtime_query_plan(self.solution)["planSha256"],
            actor="reviewer",
            approved_families=[],
            revised=True,
        )
        self.assertFalse(revised["consentRecorded"])

    def test_decline_preserves_an_existing_lab_grant(self) -> None:
        self._approve(SOURCE)
        plan = build_runtime_query_plan(self.solution)
        declined = record_runtime_query_consent(
            self.solution,
            expected_plan_sha256=plan["planSha256"],
            actor="reviewer@example.test",
            approved_families=[],
            declined=True,
            reason="Declining to expand the currently approved read scope.",
        )
        self.assertTrue(declined["existingGrantPreserved"])
        status = runtime_query_consent_status(self.solution)
        self.assertEqual("approved", status["status"])
        self.assertEqual([SOURCE], status["approvedFamilies"])
        self.assertEqual("declined", status["latestDecision"]["status"])

    def test_cli_requires_explicit_family_selection_and_reports_decision(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                0,
                cli.main(
                    [
                        "plan-runtime-query-consent",
                        "--solution",
                        str(self.solution),
                    ]
                ),
            )
        plan = json.loads(output.getvalue())
        self.assertEqual(
            [],
            plan["consentChoices"]["preselectedFamilies"],
        )
        self.assertIn("resourceGroup", plan["target"])
        self.assertIn("queries", plan["families"][SOURCE])

        with redirect_stdout(StringIO()):
            self.assertEqual(
                2,
                cli.main(
                    [
                        "review-runtime-query-consent",
                        "--solution",
                        str(self.solution),
                        "--expected-plan-sha256",
                        plan["planSha256"],
                        "--actor",
                        "reviewer",
                    ]
                ),
            )
        with redirect_stdout(StringIO()):
            self.assertEqual(
                0,
                cli.main(
                    [
                        "review-runtime-query-consent",
                        "--solution",
                        str(self.solution),
                        "--expected-plan-sha256",
                        plan["planSha256"],
                        "--actor",
                        "reviewer",
                        "--approve-family",
                        SOURCE,
                    ]
                ),
            )
        status = runtime_query_consent_status(self.solution)
        self.assertEqual("approved", status["families"][SOURCE]["status"])
        self.assertEqual("not-approved", status["families"][XDR]["status"])
        self.assertEqual("not-run", status["families"][SOURCE]["executionStatus"])
        source_query = plan["families"][SOURCE]["queries"][0]
        artifact_path(
            self.solution,
            "runtime-validation.azure-monitor-sdk.json",
            create_parent=True,
        ).write_text(
            json.dumps(
                {
                    "provider": "azure-monitor-sdk",
                    "results": [
                        {
                            "querySha256": source_query["querySha256"],
                            "status": "passed",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        status = runtime_query_consent_status(self.solution)
        self.assertEqual("recorded", status["families"][SOURCE]["executionStatus"])

    def test_lab_approval_reuses_across_solutions_and_refreshes_run_snapshots(self) -> None:
        approval = self._approve(SOURCE)
        original_recorded_at = json.loads(Path(approval["path"]).read_text())["recordedAt"]
        original_plan = build_runtime_query_plan(self.solution)
        source_path = self.solution / "Analytic Rules" / "Rule.yaml"
        source = yaml.safe_load(source_path.read_text())
        source["query"] = "SecurityEvent | take 6"
        source_path.write_text(yaml.safe_dump(source), encoding="utf-8")
        changed_query_plan = build_runtime_query_plan(self.solution)
        self.assertNotEqual(original_plan["planSha256"], changed_query_plan["planSha256"])
        status = runtime_query_consent_status(self.solution)
        self.assertEqual("approved", status["status"])
        self.assertEqual(["sentinelSourceQueryFamily"], status["approvedFamilies"])
        self.assertEqual("not-current", status["runSnapshot"]["status"])
        self.assertTrue(status["runSnapshot"]["queryHashesAreConsentBindings"] is False)

        self._write_source("SigninLogs | take 1", "22222222-2222-3333-4444-555555555555", "Second.yaml")
        status = runtime_query_consent_status(self.solution)
        self.assertEqual("approved", status["status"])

        other = self.base / "Solutions" / "NewSelectedSolution"
        other.mkdir()
        (other / "Analytic Rules").mkdir()
        (other / "XDR Detections").mkdir()
        (other / "Analytic Rules" / "Rule.yaml").write_text(
            yaml.safe_dump(
                {"id": "33333333-2222-3333-4444-555555555555",
                 "query": "AuditLogs | take 2"}
            ),
            encoding="utf-8",
        )
        (other / "XDR Detections" / "Rule.yaml").write_text(
            yaml.safe_dump(
                {
                    "kind": "CustomDetection",
                    "id": "xdr-33333333-2222-3333-4444-555555555555",
                    "properties": {
                        "queryCondition": {"queryText": "DeviceEvents | take 2"},
                        "detectionAction": {"alertTemplate": {}},
                    },
                }
            ),
            encoding="utf-8",
        )
        initialize_workflow(
            other,
            workflow_profile="qualification",
            tenant_id=TENANT_ID,
            subscription_id=SUBSCRIPTION_ID,
            workspace_resource_id=WORKSPACE,
            workspace_customer_id=CUSTOMER_ID,
        )
        other_plan = build_runtime_query_plan(other)
        self.assertEqual(["sentinelSourceQueryFamily"], other_plan["labReadConsent"]["approvedFamilies"])
        self.assertNotEqual(original_plan["planSha256"], other_plan["planSha256"])
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent.shutil.which",
            return_value="/usr/bin/az",
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent.subprocess.run",
            return_value=mock.Mock(
                returncode=0,
                stdout=json.dumps({"tenantId": TENANT_ID}),
                stderr="",
            ),
        ):
            result = require_runtime_query_consent(
                other,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )
            self.assertEqual(
                "current",
                runtime_query_consent_status(other)["runSnapshot"]["status"],
            )
        self.assertEqual("approved", result["status"])
        self.assertNotEqual(original_plan["planSha256"], result["planSha256"])
        self.assertEqual(
            original_recorded_at,
            json.loads(Path(approval["path"]).read_text())["recordedAt"],
        )
        other_plan = build_runtime_query_plan(other)
        expanded = record_runtime_query_consent(
            other,
            expected_plan_sha256=other_plan["planSha256"],
            actor="reviewer@example.test",
            approved_families=[XDR],
        )
        self.assertEqual(sorted([SOURCE, XDR]), expanded["approvedFamilies"])
        self.assertEqual(
            sorted([SOURCE, XDR]),
            runtime_query_consent_status(self.solution)["approvedFamilies"],
        )

    def test_changed_lab_or_primary_setting_and_revocation_deny_reuse(self) -> None:
        approval = self._approve(SOURCE)
        self._confirm_primary(self.solution, name="different-primary-setting")
        self.assertEqual("stale", runtime_query_consent_status(self.solution)["status"])
        with self.assertRaisesRegex(ValueError, "not approved"):
            require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )

        self._approve(SOURCE)
        revoked = revoke_runtime_query_consent(
            self.solution,
            actor="reviewer@example.test",
            reason="The lab read grant is no longer needed.",
        )
        self.assertEqual("revoked", revoked["status"])
        self.assertEqual("revoked", runtime_query_consent_status(self.solution)["status"])
        with self.assertRaisesRegex(ValueError, "not approved"):
            require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )

        target_path = existing_artifact_path(self.solution, "workflow-state.json")
        state = json.loads(target_path.read_text())
        state["context"]["workspaceCustomerId"] = "11111111-1111-1111-1111-111111111111"
        target_path.write_text(json.dumps(state), encoding="utf-8")
        self.assertNotEqual("approved", runtime_query_consent_status(self.solution)["status"])
        self.assertTrue(Path(approval["path"]).is_file())

    def test_approval_and_revocation_are_serialized_without_resurrecting_scope(self) -> None:
        self._approve(SOURCE)
        current_plan = build_runtime_query_plan(self.solution)
        read_started = threading.Event()
        continue_approval = threading.Event()
        revoke_started = threading.Event()
        revoke_lock_requested = threading.Event()
        original_load = runtime_consent._load_lab_consent
        original_lock = runtime_consent._lab_lock
        local_count = threading.local()

        def delayed_load(target, primary_setting):
            result = original_load(target, primary_setting)
            count = getattr(local_count, "count", 0) + 1
            local_count.count = count
            if (
                threading.current_thread().name.startswith("lab-approval")
                and count == 2
            ):
                read_started.set()
                if not continue_approval.wait(timeout=5):
                    raise TimeoutError("test did not release the serialized approval")
            return result

        def revoke():
            revoke_started.set()
            return revoke_runtime_query_consent(
                self.solution,
                actor="revoker@example.test",
                reason="Concurrent revocation wins after the approval transaction.",
            )

        def tracked_lock(target):
            if threading.current_thread().name.endswith("_1"):
                revoke_lock_requested.set()
            return original_lock(target)

        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._load_lab_consent",
            side_effect=delayed_load,
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent._lab_lock",
            side_effect=tracked_lock,
        ):
            with ThreadPoolExecutor(
                max_workers=2,
                thread_name_prefix="lab-approval",
            ) as executor:
                approval = executor.submit(
                    lambda: record_runtime_query_consent(
                        self.solution,
                        expected_plan_sha256=current_plan["planSha256"],
                        actor="approver@example.test",
                        approved_families=[XDR],
                    )
                )
                self.assertTrue(read_started.wait(timeout=5))
                revocation = executor.submit(revoke)
                self.assertTrue(revoke_started.wait(timeout=5))
                self.assertTrue(revoke_lock_requested.wait(timeout=5))
                self.assertFalse(revocation.done())
                continue_approval.set()
                approval.result(timeout=5)
                revocation.result(timeout=5)

        status = runtime_query_consent_status(self.solution)
        self.assertEqual("revoked", status["status"])
        self.assertEqual([], status["approvedFamilies"])
        with self.assertRaisesRegex(ValueError, "not approved"):
            require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )

    def test_provider_and_auth_snapshots_refresh_without_new_lab_approval(self) -> None:
        approval = self._approve(SOURCE)
        original_recorded_at = json.loads(Path(approval["path"]).read_text())["recordedAt"]
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent.shutil.which",
            return_value="/usr/bin/az",
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent.subprocess.run",
            return_value=mock.Mock(
                returncode=0,
                stdout=json.dumps({"tenantId": TENANT_ID}),
                stderr="",
            ),
        ):
            plan = build_runtime_query_plan(self.solution)
            self.assertEqual("approved", runtime_query_consent_status(self.solution)["status"])
            self.assertEqual(
                "approved",
                require_runtime_query_consent(
                    self.solution,
                    family=SOURCE,
                    provider="azure-monitor-sdk",
                )["status"],
            )
            self.assertEqual(
                "current",
                runtime_query_consent_status(self.solution)["runSnapshot"]["status"],
            )
        self.assertEqual(
            original_recorded_at,
            json.loads(Path(approval["path"]).read_text())["recordedAt"],
        )
        self.assertEqual(
            "existing-cached-auth-available",
            plan["families"][SOURCE]["provider"]["authentication"]["classification"],
        )
        self.assertEqual("not-current", runtime_query_consent_status(self.solution)["runSnapshot"]["status"])

    def test_cached_auth_allows_read_only_family_and_interactive_auth_does_not(self) -> None:
        self.state_dir.mkdir(exist_ok=True)
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent.shutil.which",
            return_value="/usr/bin/az",
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent.subprocess.run",
            return_value=mock.Mock(
                returncode=0,
                stdout=json.dumps({"tenantId": TENANT_ID}),
                stderr="",
            ),
        ):
            plan = build_runtime_query_plan(self.solution)
            self.assertEqual(
                "existing-cached-auth-available",
                plan["families"][SOURCE]["provider"]["authentication"]["classification"],
            )
            record_runtime_query_consent(
                self.solution,
                expected_plan_sha256=plan["planSha256"],
                actor="reviewer",
                approved_families=[SOURCE],
            )
            self.assertEqual(
                "approved",
                require_runtime_query_consent(
                    self.solution,
                    family=SOURCE,
                    provider="azure-monitor-sdk",
                )["status"],
            )

        graph_plan = build_runtime_query_plan(self.solution)
        record_runtime_query_consent(
            self.solution,
            expected_plan_sha256=graph_plan["planSha256"],
            actor="reviewer",
            approved_families=[XDR],
        )
        with self.assertRaisesRegex(ValueError, "does not authorize interactive sign-in"):
            require_runtime_query_consent(
                self.solution,
                family=XDR,
                provider="graph",
            )
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._authentication_requirement",
            return_value={
                "classification": "cached-auth-configured-unverified",
                "cachedAuthConfigured": True,
                "interactiveSignInPermittedByThisConsent": False,
                "evidence": "test-only cached auth classification",
            },
        ):
            graph_plan = build_runtime_query_plan(self.solution)
            record_runtime_query_consent(
                self.solution,
                expected_plan_sha256=graph_plan["planSha256"],
                actor="reviewer",
                approved_families=[XDR],
            )
            self.assertEqual(
                "approved",
                require_runtime_query_consent(
                    self.solution,
                    family=XDR,
                    provider="graph",
                )["status"],
            )

    def test_direct_cli_runtime_validation_checks_consent_before_provider(self) -> None:
        with mock.patch.object(cli, "configure_logging"), mock.patch(
            "sentinel_xdr_migration.runtime.validate_advanced_hunting"
        ) as graph_executor, mock.patch(
            "sentinel_xdr_migration.runtime.validate_sentinel_sdk"
        ) as sentinel_executor:
            result = cli.main(
                [
                    "validate-advanced-hunting",
                    "--solution",
                    str(self.solution),
                ]
            )
            source_result = cli.main(
                [
                    "validate-sentinel-sdk",
                    "--solution",
                    str(self.solution),
                ]
            )
            imported_result = cli.main(
                [
                    "record-runtime-validation",
                    "--solution",
                    str(self.solution),
                    "--provider",
                    "triage-mcp",
                    "--results",
                    str(self.base / "not-yet-opened.json"),
                ]
            )
        self.assertEqual(2, result)
        self.assertEqual(2, source_result)
        self.assertEqual(2, imported_result)
        graph_executor.assert_not_called()
        sentinel_executor.assert_not_called()

        uninitialized = self.base / "Solutions" / "NoWorkflowState"
        uninitialized.mkdir(parents=True)
        with mock.patch.object(cli, "configure_logging"), mock.patch(
            "sentinel_xdr_migration.runtime.validate_advanced_hunting"
        ) as graph_executor, mock.patch(
            "sentinel_xdr_migration.runtime.validate_sentinel_sdk"
        ) as sentinel_executor:
            missing_ah = cli.main(
                [
                    "validate-advanced-hunting",
                    "--solution",
                    str(uninitialized),
                ]
            )
            missing_sdk = cli.main(
                [
                    "validate-sentinel-sdk",
                    "--solution",
                    str(uninitialized),
                ]
            )
        self.assertEqual(2, missing_ah)
        self.assertEqual(2, missing_sdk)
        graph_executor.assert_not_called()
        sentinel_executor.assert_not_called()

    def _authoring_solution(self) -> Path:
        solution = self.base / "Solutions" / "AuthoringQueries"
        (solution / "XDR Detections").mkdir(parents=True)
        initialize_workflow(
            solution,
            workflow_profile="authoring",
            tenant_id=TENANT_ID,
        )
        (solution / "XDR Detections" / "Rule.yaml").write_text(
            yaml.safe_dump(
                {
                    "kind": "CustomDetection",
                    "id": "xdr-11111111-2222-3333-4444-555555555555",
                    "properties": {
                        "queryCondition": {"queryText": "DeviceEvents | take 5"},
                        "detectionAction": {"alertTemplate": {}},
                    },
                }
            ),
            encoding="utf-8",
        )
        return solution

    @staticmethod
    def _cached_graph_authentication() -> dict:
        return {
            "classification": "cached-auth-configured-unverified",
            "cachedAuthConfigured": True,
            "interactiveSignInPermittedByThisConsent": False,
            "evidence": "fixture authentication record is bound to the selected tenant",
        }

    def test_authoring_advanced_hunting_requires_exact_run_consent_and_keeps_schema(self) -> None:
        solution = self._authoring_solution()
        cached = self._cached_graph_authentication()
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._authentication_requirement",
            return_value=cached,
        ):
            plan = build_runtime_query_plan(solution)
            self.assertEqual("authoring", plan["workflowProfile"])
            self.assertEqual({"tenantId", "fingerprintSha256", "workspaceSelected"},
                             set(plan["target"]))
            self.assertFalse(plan["target"]["workspaceSelected"])
            self.assertEqual(
                "qualification-only",
                plan["families"][SOURCE]["status"],
            )
            self.assertEqual(
                ["defenderXdrQueryFamily"],
                plan["consentChoices"]["availableFamilies"],
            )
            with mock.patch.object(cli, "configure_logging"), mock.patch(
                "sentinel_xdr_migration.runtime.validate_advanced_hunting"
            ) as graph_executor:
                status = cli.main(
                    [
                        "validate-advanced-hunting",
                        "--solution",
                        str(solution),
                    ]
                )
            self.assertEqual(2, status)
            graph_executor.assert_not_called()
            with self.assertRaisesRegex(ValueError, "not current"):
                require_runtime_query_consent(
                    solution,
                    family=XDR,
                    provider="graph",
                )
            approval = record_runtime_query_consent(
                solution,
                expected_plan_sha256=plan["planSha256"],
                actor="reviewer@example.test",
                approved_families=[XDR],
            )
            self.assertEqual("one-run-authoring-query-only", approval["consentScope"])
            source_query = "SecurityEvent | take 5"
            source_entry = runtime_consent._query_entry(
                rule_id="11111111-2222-3333-4444-555555555555",
                path="Analytic Rules/Rule.yaml",
                query=source_query,
            )
            source_family = {
                **plan["families"][SOURCE],
                "ruleCount": 1,
                "queryCount": 1,
                "queries": [source_entry],
                "status": "ready",
            }
            source_family.pop("familySha256", None)
            source_family["familySha256"] = runtime_consent._canonical_sha256(
                source_family
            )
            full_inventory_plan = {
                **plan,
                "families": {**plan["families"], SOURCE: source_family},
            }
            full_inventory_plan["planSha256"] = (
                runtime_consent._runtime_query_plan_sha256(full_inventory_plan)
            )
            with mock.patch(
                "sentinel_xdr_migration.runtime_consent.build_runtime_query_plan",
                return_value=full_inventory_plan,
            ), self.assertRaisesRegex(
                ValueError,
                "Authoring runtime validation is limited to explicitly approved "
                "Defender XDR Advanced Hunting queries",
            ):
                require_runtime_query_consent(
                    solution,
                    family=SOURCE,
                    provider="azure-monitor-sdk",
                )

            with mock.patch(
                "sentinel_xdr_migration.runtime._assert_graph_auth_tenant_scope"
            ) as auth_scope, mock.patch(
                "sentinel_xdr_migration.runtime._advanced_hunting_token",
                return_value="token",
            ), mock.patch(
                "sentinel_xdr_migration.runtime.run_advanced_hunting_query",
                return_value={
                    "ok": True,
                    "statusCode": 200,
                    "rowCount": 0,
                    "schema": [{"name": "Timestamp", "type": "DateTime"}],
                    "error": None,
                    "errorDetails": None,
                },
            ) as run_query:
                result = validate_advanced_hunting(
                    solution,
                    state_dir=self.state_dir,
                    tenant_id=TENANT_ID,
                )
            self.assertEqual(1, result["valid"])
            self.assertEqual(
                [{"name": "Timestamp", "type": "DateTime"}],
                result["results"][0]["schema"],
            )
            run_query.assert_called_once_with(
                "DeviceEvents | take 5",
                _token="token",
            )
            auth_scope.assert_called_once()
            self.assertEqual(
                TENANT_ID,
                auth_scope.call_args.kwargs["locked_tenant_id"],
            )
            self.assertEqual(
                "authoring",
                result["runtimeQueryConsent"]["workflowProfile"],
            )
            self.assertFalse(
                result["runtimeQueryConsent"]["environmentWritesAuthorized"]
            )
            self.assertEqual(
                "approved",
                runtime_query_consent_status(solution)["status"],
            )

    def test_authoring_advanced_hunting_consent_is_stale_for_query_or_run_change(self) -> None:
        solution = self._authoring_solution()
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._authentication_requirement",
            return_value=self._cached_graph_authentication(),
        ):
            plan = build_runtime_query_plan(solution)
            record_runtime_query_consent(
                solution,
                expected_plan_sha256=plan["planSha256"],
                actor="reviewer@example.test",
                approved_families=[XDR],
            )
            rule_path = solution / "XDR Detections" / "Rule.yaml"
            rule = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
            rule["properties"]["queryCondition"]["queryText"] = "DeviceEvents | take 6"
            rule_path.write_text(yaml.safe_dump(rule), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stale"):
                require_runtime_query_consent(
                    solution,
                    family=XDR,
                    provider="graph",
                )

            current_plan = build_runtime_query_plan(solution)
            record_runtime_query_consent(
                solution,
                expected_plan_sha256=current_plan["planSha256"],
                actor="reviewer@example.test",
                approved_families=[XDR],
            )
            state_path = existing_artifact_path(solution, "workflow-state.json")
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["runId"] = "other-explicit-run"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stale"):
                require_runtime_query_consent(
                    solution,
                    family=XDR,
                    provider="graph",
                )

    def test_azure_cli_account_classification_uses_only_configured_profile(self) -> None:
        ambient = str(self.base / "ambient-profile")
        isolated = str(self.base / "isolated-profile")
        with mock.patch.dict("os.environ", {"AZURE_CONFIG_DIR": ambient}), mock.patch(
            "sentinel_xdr_migration.runtime_consent.shutil.which",
            return_value="/usr/bin/az",
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent.configured_azure_cli_profile",
            return_value=isolated,
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent.subprocess.run",
            return_value=mock.Mock(
                returncode=0,
                stdout=json.dumps({"tenantId": TENANT_ID}),
                stderr="",
            ),
        ) as run:
            result = runtime_consent._authentication_requirement(
                "azure-monitor-sdk",
                {"tenantId": TENANT_ID},
            )
        self.assertEqual("existing-cached-auth-available", result["classification"])
        self.assertEqual(isolated, run.call_args.kwargs["env"]["AZURE_CONFIG_DIR"])
        self.assertNotEqual(
            ambient,
            run.call_args.kwargs["env"]["AZURE_CONFIG_DIR"],
        )

        with mock.patch(
            "sentinel_xdr_migration.runtime_consent.shutil.which",
            return_value="/usr/bin/az",
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent.configured_azure_cli_profile",
            return_value=None,
        ), mock.patch(
            "sentinel_xdr_migration.runtime_consent.subprocess.run"
        ) as run:
            result = runtime_consent._authentication_requirement(
                "azure-monitor-sdk",
                {"tenantId": TENANT_ID},
            )
        self.assertEqual("separate-interactive-sign-in-required", result["classification"])
        run.assert_not_called()

    def _prepare_sdk_detection(self):
        query = "SecurityEvent | take 5"
        source = self.solution / "Analytic Rules" / "Rule.yaml"
        source.write_text(
            yaml.safe_dump(
                {
                    "id": "11111111-2222-3333-4444-555555555555",
                    "query": query,
                }
            ),
            encoding="utf-8",
        )
        detection = self.solution / "XDR Detections" / "Rule.yaml"
        detection.write_text(
            yaml.safe_dump(
                {
                    "kind": "CustomDetection",
                    "id": "xdr-11111111-2222-3333-4444-555555555555",
                    "contentProvenance": {
                        "requiredWorkloads": [{"workload": "sentinel", "dataTypes": ["SecurityEvent"]}],
                        "requiredDataConnectors": [],
                        "source": {
                            "path": "Analytic Rules/Rule.yaml",
                            "querySha256": hashlib.sha256(query.encode()).hexdigest(),
                        }
                    },
                    "properties": {
                        "queryCondition": {"queryText": query},
                        "detectionAction": {"alertTemplate": {}},
                    },
                }
            ),
            encoding="utf-8",
        )
        cached = {
            "classification": "existing-cached-auth-available",
            "cachedAuthConfigured": True,
            "interactiveSignInPermittedByThisConsent": False,
            "evidence": "test cached credential classification",
        }

        class Client:
            closed = False

            def close(self):
                self.closed = True

        return query, cached, Client()

    def test_sdk_provider_failure_records_report_and_consent_snapshot(self) -> None:
        query, cached, client = self._prepare_sdk_detection()

        def provider_failure_during_decline(*_args, **_kwargs):
            current_plan = build_runtime_query_plan(self.solution)
            record_runtime_query_consent(
                self.solution,
                expected_plan_sha256=current_plan["planSha256"],
                actor="reviewer@example.test",
                approved_families=[],
                declined=True,
                reason="Declining a separate, non-revoking Qualification step.",
            )
            raise RuntimeError("test provider failure")

        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._authentication_requirement",
            return_value=cached,
        ):
            self._approve(SOURCE)
            with mock.patch(
                "sentinel_xdr_migration.logs_query.query_family",
                side_effect=provider_failure_during_decline,
            ):
                report = validate_sentinel_sdk(
                    self.solution,
                    target=require_locked_target(
                        self.solution,
                        materialize_missing=False,
                    ),
                    _scope_verifier=lambda _target: None,
                    _credential_factory=lambda _target: object(),
                    _client_factory=lambda _credential, **_kwargs: client,
                )
        self.assertEqual(1, report["notRun"])
        self.assertEqual("provider", report["providerFailure"]["failureKind"])
        self.assertEqual("approved", report["runtimeQueryConsent"]["status"])
        self.assertTrue(client.closed)
        persisted = json.loads(
            existing_artifact_path(
                self.solution,
                "runtime-validation.azure-monitor-sdk.json",
            ).read_text()
        )
        self.assertEqual("approved", persisted["runtimeQueryConsent"]["status"])
        dispatch_snapshot = persisted["runtimeQueryDispatchSnapshot"]
        self.assertEqual(
            dispatch_snapshot["planSha256"],
            persisted["runtimeQueryConsent"]["planSha256"],
        )
        self.assertEqual("declined", self._latest_decision_record()["status"])
        self.assertEqual(
            "lab-wide-across-solutions-and-runs",
            persisted["runtimeQueryConsent"]["consentScope"],
        )
        self.assertEqual(
            report["runtimeQueryConsent"]["labConsentSha256"],
            persisted["runtimeQueryConsent"]["labConsentSha256"],
        )
        self.assertEqual("not-run", persisted["results"][0]["status"])

    def test_sdk_success_evidence_survives_concurrent_nonrevoking_defer(self) -> None:
        query, cached, client = self._prepare_sdk_detection()

        def successful_dispatch_with_defer(*_args, **_kwargs):
            current_plan = build_runtime_query_plan(self.solution)
            record_runtime_query_consent(
                self.solution,
                expected_plan_sha256=current_plan["planSha256"],
                actor="reviewer@example.test",
                approved_families=[],
                revised=True,
                reason="Defer independent follow-up work.",
            )
            return [
                {
                    "detection": "Rule.yaml",
                    "status": "passed",
                    "valid": True,
                    "querySha256": hashlib.sha256(query.encode()).hexdigest(),
                    "statusCode": 200,
                    "rowCount": 1,
                    "schema": [{"name": "Account", "type": "string"}],
                    "error": None,
                    "errorDetails": None,
                }
            ]

        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._authentication_requirement",
            return_value=cached,
        ):
            self._approve(SOURCE)
            with mock.patch(
                "sentinel_xdr_migration.logs_query.query_family",
                side_effect=successful_dispatch_with_defer,
            ):
                report = validate_sentinel_sdk(
                    self.solution,
                    target=require_locked_target(
                        self.solution,
                        materialize_missing=False,
                    ),
                    _scope_verifier=lambda _target: None,
                    _credential_factory=lambda _target: object(),
                    _client_factory=lambda _credential, **_kwargs: client,
                )
        self.assertEqual(1, report["valid"])
        self.assertEqual(0, report["notRun"])
        persisted = json.loads(
            existing_artifact_path(
                self.solution,
                "runtime-validation.azure-monitor-sdk.json",
            ).read_text()
        )
        self.assertEqual("passed", persisted["results"][0]["status"])
        self.assertEqual("revised", self._latest_decision_record()["status"])
        self.assertEqual(
            persisted["runtimeQueryDispatchSnapshot"]["planSha256"],
            persisted["runtimeQueryConsent"]["planSha256"],
        )

    def test_import_guard_is_independent_of_cli_and_precedes_file_read(self) -> None:
        missing_results = self.base / "not-yet-read-runtime-results.json"
        with self.assertRaisesRegex(ValueError, "not approved"):
            record_runtime_validation(
                self.solution,
                provider="triage-mcp",
                results_path=missing_results,
            )
        self.assertFalse(
            existing_artifact_path(
                self.solution,
                "runtime-validation.triage-mcp.json",
            ).exists()
        )

    def test_dispatch_snapshot_fails_closed_after_revoke_target_or_query_change(self) -> None:
        self._prepare_sdk_detection()
        cached = {
            "classification": "existing-cached-auth-available",
            "cachedAuthConfigured": True,
            "interactiveSignInPermittedByThisConsent": False,
            "evidence": "test cached credential classification",
        }
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._authentication_requirement",
            return_value=cached,
        ):
            self._approve(SOURCE)
            revoked_snapshot = require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )
            revoke_runtime_query_consent(
                self.solution,
                actor="revoker@example.test",
                reason="Revoke before evidence import.",
            )
            with self.assertRaisesRegex(ValueError, "not approved"):
                record_runtime_validation(
                    self.solution,
                    provider="azure-monitor-sdk",
                    results_data=[],
                    runtime_query_consent=revoked_snapshot,
                )

            self._approve(SOURCE)
            stale_query_snapshot = require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )
            source_path = self.solution / "Analytic Rules" / "Rule.yaml"
            source = yaml.safe_load(source_path.read_text(encoding="utf-8"))
            source["query"] = "SecurityEvent | take 99"
            source_path.write_text(yaml.safe_dump(source), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "dispatch snapshot"):
                record_runtime_validation(
                    self.solution,
                    provider="azure-monitor-sdk",
                    results_data=[],
                    runtime_query_consent=stale_query_snapshot,
                )

            self._approve(SOURCE)
            stale_target_snapshot = require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )
            state_path = existing_artifact_path(self.solution, "workflow-state.json")
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["context"]["workspaceCustomerId"] = (
                "11111111-1111-1111-1111-111111111111"
            )
            state_path.write_text(json.dumps(state), encoding="utf-8")
            with self.assertRaises(ValueError):
                record_runtime_validation(
                    self.solution,
                    provider="azure-monitor-sdk",
                    results_data=[],
                    runtime_query_consent=stale_target_snapshot,
                )
        self.assertFalse(
            existing_artifact_path(
                self.solution,
                "runtime-validation.azure-monitor-sdk.json",
            ).exists()
        )

    def test_runtime_entrypoints_reject_conflicting_locked_and_auth_targets(self) -> None:
        locked = require_locked_target(self.solution, materialize_missing=False)
        conflicting = {**locked, "workspaceCustomerId": "11111111-1111-1111-1111-111111111111"}
        verifier = mock.Mock()
        with self.assertRaisesRegex(ValueError, "SDK target conflicts"):
            validate_sentinel_sdk(
                self.solution,
                target=conflicting,
                _scope_verifier=verifier,
                _credential_factory=mock.Mock(),
                _client_factory=mock.Mock(),
            )
        verifier.assert_not_called()

        with mock.patch("sentinel_xdr_migration.runtime._advanced_hunting_token") as token:
            with self.assertRaisesRegex(ValueError, "requested Graph tenant"):
                validate_advanced_hunting(
                    self.solution,
                    tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                )
        token.assert_not_called()

        cached = {
            "classification": "cached-auth-configured-unverified",
            "cachedAuthConfigured": True,
            "interactiveSignInPermittedByThisConsent": False,
            "evidence": "test cached credential classification",
        }
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._authentication_requirement",
            return_value=cached,
        ):
            self._approve(XDR)
            with mock.patch(
                "sentinel_xdr_migration.runtime_consent._authentication_requirement",
                return_value=cached,
            ), mock.patch(
                "sentinel_xdr_migration.runtime._load_auth_record",
                return_value=SimpleNamespace(
                    tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
                ),
            ), mock.patch(
                "sentinel_xdr_migration.runtime._read_json",
                return_value={"tenantId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
            ), mock.patch(
                "sentinel_xdr_migration.runtime._advanced_hunting_token"
            ) as token:
                with self.assertRaisesRegex(ValueError, "authentication record tenant"):
                    validate_advanced_hunting(
                        self.solution,
                        state_dir=self.base / "other-tenant-auth",
                    )
        token.assert_not_called()
        with mock.patch(
            "sentinel_xdr_migration.runtime_consent._authentication_requirement",
            return_value=cached,
        ), mock.patch(
            "sentinel_xdr_migration.runtime._load_auth_record",
            return_value=SimpleNamespace(tenant_id=TENANT_ID),
        ), mock.patch(
            "sentinel_xdr_migration.runtime._read_json",
            return_value={
                "tenantId": TENANT_ID,
                "workspaceResourceId": WORKSPACE.replace(
                    "QueryWorkspace",
                    "OtherWorkspace",
                ),
            },
        ), mock.patch(
            "sentinel_xdr_migration.runtime._advanced_hunting_token"
        ) as token:
            with self.assertRaisesRegex(ValueError, "workspaceResourceId"):
                validate_advanced_hunting(
                    self.solution,
                    state_dir=self.base / "other-workspace-auth",
                )
        token.assert_not_called()

    def test_consent_never_infers_write_or_packaging_authority(self) -> None:
        approval = self._approve(SOURCE, XDR)
        path = Path(approval["path"])
        stored = json.loads(path.read_text())
        self.assertEqual("shared-lab-read-only-runtime-query", stored["consentType"])
        self.assertFalse(stored["authorizationBoundary"]["environmentWritesAuthorized"])
        self.assertFalse(stored["authorizationBoundary"]["interactiveAuthenticationAuthorized"])
        self.assertEqual(
            {"sentinelSourceQueryFamily", "defenderXdrQueryFamily"},
            set(stored["approvedFamilies"]),
        )
        self.assertEqual(
            {
                "crossSolution": True,
                "crossRun": True,
                "sourceQueryHashesAreSnapshotsOnly": True,
                "xdrQueryHashesAreSnapshotsOnly": True,
                "querySnapshotsAreNotConsentBindings": True,
            },
            stored["scopePolicy"],
        )
        self.assertEqual(
            {
                "interactiveAuthenticationAuthorized": False,
                "adminConsentAuthorized": False,
                "permissionChangesAuthorized": False,
                "roleAssignmentsAuthorized": False,
                "environmentWritesAuthorized": False,
                "packageOrDeploymentAuthorized": False,
                "ingestionOrParityAuthorized": False,
                "ruleEnablementOrCleanupAuthorized": False,
            },
            stored["authorizationBoundary"],
        )
        stored["authorizationBoundary"]["environmentWritesAuthorized"] = True
        path.write_text(json.dumps(stored), encoding="utf-8")
        self.assertEqual("invalid", runtime_query_consent_status(self.solution)["status"])
        with self.assertRaisesRegex(ValueError, "not approved"):
            require_runtime_query_consent(
                self.solution,
                family=SOURCE,
                provider="azure-monitor-sdk",
            )
        require_locked_target(self.solution)

    def test_primary_setting_is_explicit_user_attestation_not_service_proof(self) -> None:
        another = self.base / "Solutions" / "Unconfirmed"
        another.mkdir()
        (another / "Analytic Rules").mkdir()
        (another / "Analytic Rules" / "Rule.yaml").write_text(
            yaml.safe_dump(
                {
                    "id": "44444444-2222-3333-4444-555555555555",
                    "query": "SecurityEvent | take 1",
                }
            ),
            encoding="utf-8",
        )
        initialize_workflow(
            another,
            workflow_profile="qualification",
            tenant_id=TENANT_ID,
            subscription_id=SUBSCRIPTION_ID,
            workspace_resource_id=WORKSPACE.replace("QueryWorkspace", "UnconfirmedWorkspace"),
            workspace_customer_id="11111111-1111-1111-1111-111111111111",
        )
        with self.assertRaisesRegex(ValueError, "not been explicitly confirmed"):
            record_runtime_query_consent(
                another,
                expected_plan_sha256=build_runtime_query_plan(another)["planSha256"],
                actor="reviewer",
                approved_families=[SOURCE],
            )
        with redirect_stderr(StringIO()):
            self.assertEqual(
                2,
                cli.main(
                    [
                        "confirm-primary-lab-setting",
                        "--solution",
                        str(another),
                        "--actor",
                        "reviewer@example.test",
                        "--primary-setting-name",
                        "qualification-primary",
                    ]
                ),
            )
        confirmation_output = StringIO()
        with redirect_stdout(confirmation_output):
            self.assertEqual(
                0,
                cli.main(
                    [
                        "confirm-primary-lab-setting",
                        "--solution",
                        str(another),
                        "--actor",
                        "reviewer@example.test",
                        "--primary-setting-name",
                        "qualification-primary",
                        "--confirm-primary-setting",
                    ]
                ),
            )
        confirmed = json.loads(confirmation_output.getvalue())
        self.assertFalse(confirmed["serviceVerified"])
        setting_path = Path(confirmed["path"])
        setting = json.loads(setting_path.read_text())
        self.assertEqual("explicit-user-attestation", setting["primarySetting"]["confirmationType"])
        self.assertFalse(setting["primarySetting"]["serviceVerified"])
        setting["primarySetting"]["serviceVerified"] = True
        setting_path.write_text(json.dumps(setting), encoding="utf-8")
        self.assertEqual(
            "requires-explicit-primary-setting-confirmation",
            build_runtime_query_plan(another)["labReadConsent"]["status"],
        )

    def test_read_only_post_operations_are_not_write_authority(self) -> None:
        plan = build_runtime_query_plan(self.solution)
        self.assertEqual("POST", plan["labReadConsent"]["operationFamilies"][SOURCE]["httpMethod"])
        self.assertEqual("read-only query execution", plan["labReadConsent"]["operationFamilies"][SOURCE]["operationSemantics"])
        self.assertFalse(plan["labReadConsent"]["operationFamilies"][SOURCE]["resourceMutation"])
        self.assertEqual("POST", plan["labReadConsent"]["operationFamilies"][XDR]["httpMethod"])
        self.assertFalse(plan["labReadConsent"]["operationFamilies"][XDR]["resourceMutation"])


if __name__ == "__main__":
    unittest.main()
