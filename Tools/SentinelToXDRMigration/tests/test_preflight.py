from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

from sentinel_xdr_migration.artifacts import artifact_path, existing_artifact_path
from sentinel_xdr_migration.onboarding import configure_workspace, doctor
from sentinel_xdr_migration.preflight import run_preflight
from sentinel_xdr_migration.target_context import build_target
from sentinel_xdr_migration.workflow import initialize_workflow


TENANT_ID = "11111111-2222-4333-8444-555555555555"
SUBSCRIPTION_ID = "22222222-3333-4444-8555-666666666666"
CUSTOMER_ID = "33333333-4444-4555-8666-777777777777"
WORKSPACE = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/rg-test/"
    "providers/Microsoft.OperationalInsights/workspaces/ws-test"
)
OTHER_TENANT = "11111111-1111-1111-1111-111111111111"


class PreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.solution = Path(self.temp.name) / "Sample"
        self.solution.mkdir()
        initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            tenant_id=TENANT_ID,
            subscription_id=SUBSCRIPTION_ID,
            workspace_resource_id=WORKSPACE,
            workspace_customer_id=CUSTOMER_ID,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _runner(command, **_kwargs):
        if command[1:3] != ["version", "--output"]:
            raise AssertionError(f"unexpected command: {command}")
        return CompletedProcess(command, 0, "{}", "")

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_doctor_does_not_treat_independent_tokens_as_runtime_access(
        self, _which: mock.Mock
    ) -> None:
        state_dir = Path(self.temp.name) / "state"
        configure_workspace(
            WORKSPACE,
            workspace_customer_id=CUSTOMER_ID,
            tenant_id=TENANT_ID,
            subscription_id=SUBSCRIPTION_ID,
            state_dir=state_dir,
        )
        commands = []

        def runner(command, **_kwargs):
            commands.append(command)
            return CompletedProcess(command, 0, "{}", "")

        report = doctor(
            state_dir=state_dir,
            runner=runner,
            environment={},
        )

        self.assertFalse(report["runtimeValidationAvailable"])
        self.assertEqual("offline", report["mode"])
        self.assertEqual([["az", "version", "--output", "none"]], commands)
        checks = {check["name"]: check for check in report["checks"]}
        self.assertEqual("notRun", checks["sentinelAuthentication"]["status"])
        self.assertEqual("notRun", checks["advancedHunting"]["status"])
        self.assertEqual("passed", checks["sentinelWorkspace"]["status"])

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_default_preflight_is_offline_and_does_not_materialize_target(
        self, _which: mock.Mock
    ) -> None:
        target_path = artifact_path(self.solution, "qualification-target.json")
        target_path.unlink()

        report = run_preflight(
            self.solution,
            runner=self._runner,
            source_table="SecurityEvent",
        )

        self.assertEqual("unknown", report["overallStatus"])
        self.assertEqual("passed", report["target"]["status"])
        self.assertEqual("notRun", report["providers"]["source"]["tableAccess"]["status"])
        self.assertEqual("unknown", report["deploymentPermissions"]["status"])
        self.assertFalse(target_path.exists())
        self.assertEqual(
            {
                "writesPerformed": False,
                "workspaceEnumerationPerformed": False,
                "newAuthenticationPerformed": False,
            },
            report["safety"],
        )

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_explicit_reads_keep_source_and_converted_provider_families_separate(
        self, _which: mock.Mock
    ) -> None:
        requests = []

        def executor(request):
            requests.append(request)
            return {"ok": True}

        report = run_preflight(
            self.solution,
            runner=self._runner,
            read_executor=executor,
            source_table="SecurityEvent",
            source_query="SecurityEvent | take 0",
            converted_table="DeviceEvents",
            converted_query="DeviceEvents | take 0",
        )

        self.assertEqual(
            [
                ("sentinel-source-table-read", "logAnalytics"),
                ("sentinel-source-query-read", "logAnalytics"),
                ("converted-graph-table-read", "graphAdvancedHunting"),
                ("converted-graph-query-read", "graphAdvancedHunting"),
            ],
            [(request["scope"], request["provider"]) for request in requests],
        )
        for request in requests:
            expected = build_target(
                tenant_id=TENANT_ID,
                subscription_id=SUBSCRIPTION_ID,
                workspace_resource_id=WORKSPACE,
                workspace_customer_id=CUSTOMER_ID,
            )
            self.assertEqual(
                {
                    key: expected[key]
                    for key in (
                        "tenantId",
                        "subscriptionId",
                        "workspaceResourceId",
                        "workspaceCustomerId",
                    )
                },
                request["target"],
            )
        self.assertEqual("passed", report["providers"]["source"]["tableAccess"]["status"])
        self.assertEqual("passed", report["providers"]["source"]["queryExecution"]["status"])
        self.assertEqual(
            "passed", report["providers"]["converted"]["tableAccess"]["status"]
        )
        self.assertEqual(
            "passed", report["providers"]["converted"]["queryExecution"]["status"]
        )
        self.assertEqual("unknown", report["deploymentPermissions"]["status"])

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_locked_target_mismatch_prevents_all_runtime_reads(
        self, _which: mock.Mock
    ) -> None:
        executor = mock.Mock(return_value={"ok": True})

        report = run_preflight(
            self.solution,
            runner=self._runner,
            tenant_id=OTHER_TENANT,
            source_query="SecurityEvent | take 0",
            read_executor=executor,
        )

        self.assertEqual("failed", report["target"]["status"])
        self.assertEqual("locked-target-identity-mismatch", report["target"]["reason"])
        executor.assert_not_called()

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_incomplete_locked_identity_prevents_all_runtime_reads(
        self, _which: mock.Mock
    ) -> None:
        state_path = existing_artifact_path(self.solution, "workflow-state.json")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["context"]["workspaceCustomerId"] = None
        state_path.write_text(json.dumps(state), encoding="utf-8")
        executor = mock.Mock(return_value={"ok": True})

        report = run_preflight(
            self.solution,
            runner=self._runner,
            source_query="SecurityEvent | take 0",
            read_executor=executor,
        )

        self.assertEqual("failed", report["target"]["status"])
        self.assertEqual("locked-target-incomplete", report["target"]["reason"])
        executor.assert_not_called()

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_expired_and_denied_provider_responses_are_not_token_readiness(
        self, _which: mock.Mock
    ) -> None:
        for status_code, auth_status, authz_status in (
            (401, "failed", "notRun"),
            (403, "notRun", "failed"),
        ):
            with self.subTest(status_code=status_code):
                report = run_preflight(
                    self.solution,
                    runner=self._runner,
                    source_query="SecurityEvent | take 0",
                    read_executor=lambda _request: {
                        "ok": False,
                        "statusCode": status_code,
                    },
                )
                provider = report["providers"]["source"]
                self.assertEqual(auth_status, provider["authentication"]["status"])
                self.assertEqual(authz_status, provider["authorization"]["status"])
                self.assertEqual("failed", provider["queryExecution"]["status"])
                self.assertEqual("unknown", report["deploymentPermissions"]["status"])

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_offline_and_throttled_reads_remain_unknown(self, _which: mock.Mock) -> None:
        for executor in (
            lambda _request: (_ for _ in ()).throw(ConnectionError()),
            lambda _request: {"ok": False, "statusCode": 429},
        ):
            report = run_preflight(
                self.solution,
                runner=self._runner,
                converted_query="DeviceEvents | take 0",
                read_executor=executor,
            )
            provider = report["providers"]["converted"]
            self.assertEqual("unknown", provider["queryExecution"]["status"])
            self.assertEqual("notRun", provider["authentication"]["status"])
            self.assertEqual("unknown", report["deploymentPermissions"]["status"])

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value="az")
    def test_missing_table_is_failed_and_no_write_query_is_dispatched(
        self, _which: mock.Mock
    ) -> None:
        executor = mock.Mock(
            return_value={
                "ok": False,
                "tableAvailable": False,
                "failureKind": "missing-table",
            }
        )
        report = run_preflight(
            self.solution,
            runner=self._runner,
            converted_table="DeviceEvents",
            read_executor=executor,
        )
        self.assertEqual(
            "failed", report["providers"]["converted"]["tableAccess"]["status"]
        )
        self.assertEqual(
            "table-unavailable",
            report["providers"]["converted"]["tableAccess"]["reason"],
        )

        executor.reset_mock()
        with self.assertRaisesRegex(ValueError, "read-only KQL"):
            run_preflight(
                self.solution,
                runner=self._runner,
                source_query=".set-or-replace Table <| T",
                read_executor=executor,
            )
        executor.assert_not_called()

    @mock.patch("sentinel_xdr_migration.onboarding.shutil.which", return_value=None)
    def test_azure_cli_missing_is_distinct_from_unchecked_identity(
        self, _which: mock.Mock
    ) -> None:
        report = run_preflight(self.solution, runner=self._runner)

        self.assertEqual("failed", report["localTools"]["azureCli"]["status"])
        self.assertEqual("notRun", report["providers"]["source"]["authentication"]["status"])
        self.assertEqual("notRun", report["providers"]["converted"]["authentication"]["status"])


if __name__ == "__main__":
    unittest.main()
