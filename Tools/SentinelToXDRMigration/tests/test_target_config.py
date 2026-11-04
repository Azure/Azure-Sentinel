from __future__ import annotations

import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration.cli import main
from sentinel_xdr_migration import target_context
from sentinel_xdr_migration.target_config import (
    doctor_solution_target,
    read_solution_target_config,
    resolve_qualification_target,
)

TENANT_ID = "a1111111-2222-4333-8444-555555555555"
SUBSCRIPTION_ID = "b2222222-3333-4444-8555-666666666666"
CUSTOMER_ID = "c3333333-4444-4555-8666-777777777777"
WORKSPACE_ID = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/Approved-RG/"
    "providers/Microsoft.OperationalInsights/workspaces/Approved-Workspace"
)


class TargetConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.solution = Path(self.temp.name) / "Solutions" / "Sample"
        self.solution.mkdir(parents=True)
        self.env_file = self.solution / ".env"

    def _write_config(
        self,
        tenant: str = TENANT_ID,
        workspace: str = WORKSPACE_ID,
    ) -> None:
        self.env_file.write_text(
            f"AZURE_TENANT_ID={tenant}\n"
            f"SENTINEL_WORKSPACE_RESOURCE_ID={workspace}\n",
            encoding="utf-8",
        )

    def _mock_exact_workspace(self):
        return mock.patch(
            "sentinel_xdr_migration.target_context._run_az",
            side_effect=[
                subprocess.CompletedProcess(
                    ["az"],
                    0,
                    f'{{"tenantId":"{TENANT_ID}","id":"{SUBSCRIPTION_ID}"}}',
                    "",
                ),
                subprocess.CompletedProcess(
                    ["az"],
                    0,
                    f'{{"id":"{WORKSPACE_ID}","properties":{{"customerId":"{CUSTOMER_ID}"}}}}',
                    "",
                ),
            ],
        )

    def test_absent_config_is_optional_for_non_qualification(self) -> None:
        self.assertEqual({}, read_solution_target_config(self.solution))

    def test_authoring_initialization_remains_offline_without_env(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = main(
                [
                    "workflow-init",
                    "--solution",
                    str(self.solution),
                    "--workflow-profile",
                    "authoring",
                ]
            )
        self.assertEqual(0, result)
        self.assertEqual(
            "authoring", json.loads(output.getvalue())["context"]["workflowProfile"]
        )

    def test_cli_workflow_init_defaults_to_qualification_profile(self) -> None:
        self._write_config()
        output = io.StringIO()
        with self._mock_exact_workspace():
            with redirect_stdout(output):
                result = main(
                    [
                        "workflow-init",
                        "--solution",
                        str(self.solution),
                        "--confirm-configured-target",
                        "--version-bump",
                        "none",
                    ]
                )
        self.assertEqual(0, result)
        payload = json.loads(output.getvalue())
        self.assertEqual("qualification", payload["context"]["workflowProfile"])
        self.assertRegex(payload["operatorHash"], r"^[0-9a-f]{16}$")
        self.assertEqual(payload["operatorHash"], payload["context"]["operatorHash"])

    def test_doctor_displays_configured_target_without_resolving_customer_id(self) -> None:
        self._write_config()
        status = doctor_solution_target(self.solution)
        self.assertEqual("configured", status["status"])
        self.assertEqual(TENANT_ID, status["tenantId"])
        self.assertEqual(WORKSPACE_ID, status["workspaceResourceId"])
        self.assertEqual(SUBSCRIPTION_ID, status["subscriptionId"])
        self.assertIn(
            "only after explicit target confirmation",
            status["workspaceCustomerId"],
        )

    def test_shared_example_placeholders_are_rejected_as_unconfigured_values(self) -> None:
        example = (
            Path(__file__).resolve().parents[1] / ".env.example"
        ).read_text(encoding="utf-8")
        self.env_file.write_text(example, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "replace the placeholder"):
            read_solution_target_config(self.solution)

    def test_literal_config_parses_and_derives_subscription(self) -> None:
        self._write_config()
        self.assertEqual(
            {"tenantId": TENANT_ID, "workspaceResourceId": WORKSPACE_ID},
            read_solution_target_config(self.solution),
        )
        with self._mock_exact_workspace() as run_az:
            target = resolve_qualification_target(
                self.solution, confirm_configured_target=True
            )
        self.assertEqual(TENANT_ID, target["tenantId"])
        self.assertEqual(SUBSCRIPTION_ID, target["subscriptionId"])
        self.assertEqual(WORKSPACE_ID, target["workspaceResourceId"])
        self.assertEqual(CUSTOMER_ID, target["workspaceCustomerId"])
        self.assertEqual(("account", "show"), run_az.call_args_list[0].args[0])
        self.assertEqual(
            (
                "resource",
                "show",
                "--ids",
                WORKSPACE_ID,
                "--api-version",
                "2023-09-01",
            ),
            run_az.call_args_list[1].args[0],
        )
        self.assertEqual(2, run_az.call_count)

    def test_config_requires_explicit_confirmation_before_azure_access(self) -> None:
        self._write_config()
        with mock.patch("sentinel_xdr_migration.target_context._run_az") as run_az:
            with self.assertRaisesRegex(ValueError, "doctor --solution"):
                resolve_qualification_target(self.solution)
        run_az.assert_not_called()

    def test_missing_workspace_configuration_is_actionable_and_offline(self) -> None:
        self.env_file.write_text(f"AZURE_TENANT_ID={TENANT_ID}\n", encoding="utf-8")
        with mock.patch("sentinel_xdr_migration.target_context._run_az") as run_az:
            with self.assertRaisesRegex(ValueError, "SENTINEL_WORKSPACE_RESOURCE_ID"):
                resolve_qualification_target(
                    self.solution, confirm_configured_target=True
                )
        run_az.assert_not_called()

    def test_explicit_cli_tenant_and_workspace_confirm_config_target(self) -> None:
        self._write_config()
        with self._mock_exact_workspace() as run_az:
            target = resolve_qualification_target(
                self.solution,
                tenant_id=TENANT_ID,
                workspace_resource_id=WORKSPACE_ID,
            )
        self.assertEqual(CUSTOMER_ID, target["workspaceCustomerId"])
        self.assertEqual(2, run_az.call_count)

    def test_cli_initializes_and_resumes_with_the_locked_configured_target(self) -> None:
        self._write_config()
        output = io.StringIO()
        with self._mock_exact_workspace():
            with redirect_stdout(output):
                result = main(
                    [
                        "workflow-init",
                        "--solution",
                        str(self.solution),
                        "--workflow-profile",
                        "qualification",
                        "--confirm-configured-target",
                        "--version-bump",
                        "none",
                    ]
                )
        self.assertEqual(0, result)
        initialized = json.loads(output.getvalue())
        context = initialized["context"]
        self.assertEqual(TENANT_ID, context["tenantId"])
        self.assertEqual(SUBSCRIPTION_ID, context["subscriptionId"])
        self.assertEqual(WORKSPACE_ID, context["workspaceResourceId"])
        self.assertEqual(CUSTOMER_ID, context["workspaceCustomerId"])
        state_path = Path(initialized["statePath"])
        state_before = state_path.read_bytes()

        self.env_file.write_text(
            f"AZURE_TENANT_ID={TENANT_ID}\n"
            "SENTINEL_WORKSPACE_RESOURCE_ID=/subscriptions/"
            "11111111-2222-4333-8444-555555555555/resourceGroups/Other/"
            "providers/Microsoft.OperationalInsights/workspaces/Other\n",
            encoding="utf-8",
        )
        error = io.StringIO()
        with mock.patch("sentinel_xdr_migration.target_context._run_az") as run_az:
            with redirect_stderr(error):
                result = main(
                    [
                        "workflow-init",
                        "--solution",
                        str(self.solution),
                        "--workflow-profile",
                        "qualification",
                        "--version-bump",
                        "none",
                    ]
                )
        self.assertEqual(2, result)
        self.assertIn("conflicts with the locked Qualification run", error.getvalue())
        self.assertEqual(state_before, state_path.read_bytes())
        run_az.assert_not_called()

    def test_cli_config_conflict_fails_without_echoing_values_or_cloud_access(self) -> None:
        self._write_config()
        different_tenant = "11111111-2222-4333-8444-555555555555"
        with mock.patch("sentinel_xdr_migration.target_context._run_az") as run_az:
            with self.assertRaisesRegex(ValueError, "conflicts with solution .env") as error:
                resolve_qualification_target(
                    self.solution,
                    tenant_id=different_tenant,
                    confirm_configured_target=True,
                )
        self.assertNotIn(different_tenant, str(error.exception))
        run_az.assert_not_called()

    def test_rejects_missing_duplicate_unknown_malformed_and_expansion_values(self) -> None:
        cases = (
            ("AZURE_TENANT_ID=\n", "non-empty"),
            (
                f"AZURE_TENANT_ID={TENANT_ID}\nAZURE_TENANT_ID={TENANT_ID}\n",
                "duplicate AZURE_TENANT_ID",
            ),
            ("AZURE_CLIENT_SECRET=never-a-supported-setting\n", "unsupported entry"),
            ("AZURE_TENANT_ID=$(read-secret)\n", "unsupported syntax"),
            (
                "AZURE_TENANT_ID='11111111-2222-4333-8444-555555555555'\n",
                "unsupported syntax",
            ),
        )
        for contents, expected in cases:
            with self.subTest(expected=expected):
                self.env_file.write_text(contents, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, expected) as error:
                    read_solution_target_config(self.solution)
                self.assertNotIn("read-secret", str(error.exception))

    def test_rejects_unsafe_workspace_path_segment(self) -> None:
        self._write_config(
            workspace=(
                f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/Bad Group/"
                "providers/Microsoft.OperationalInsights/workspaces/Approved-Workspace"
            )
        )
        with self.assertRaisesRegex(ValueError, "unsupported syntax"):
            read_solution_target_config(self.solution)

    def test_workspace_subscription_argument_must_match_arm_id(self) -> None:
        self._write_config()
        with mock.patch("sentinel_xdr_migration.target_context._run_az") as run_az:
            with self.assertRaisesRegex(ValueError, "does not match subscription-id"):
                resolve_qualification_target(
                    self.solution,
                    subscription_id="11111111-2222-4333-8444-555555555555",
                    confirm_configured_target=True,
                )
        run_az.assert_not_called()

    def test_authenticated_scope_must_match_before_exact_get(self) -> None:
        self._write_config()
        with mock.patch(
            "sentinel_xdr_migration.target_context._run_az",
            return_value=subprocess.CompletedProcess(
                ["az"], 0, '{"tenantId":"11111111-2222-4333-8444-555555555555",'
                f'"id":"{SUBSCRIPTION_ID}"}}', ""
            ),
        ) as run_az:
            with self.assertRaisesRegex(
                RuntimeError, "does not match AZURE_TENANT_ID"
            ):
                resolve_qualification_target(
                    self.solution, confirm_configured_target=True
                )
        self.assertEqual(1, run_az.call_count)

    def test_authenticated_subscription_must_match_before_exact_get(self) -> None:
        self._write_config()
        with mock.patch(
            "sentinel_xdr_migration.target_context._run_az",
            return_value=subprocess.CompletedProcess(
                ["az"],
                0,
                '{"tenantId":"' + TENANT_ID
                + '","id":"11111111-2222-4333-8444-555555555555"}',
                "",
            ),
        ) as run_az:
            with self.assertRaisesRegex(RuntimeError, "active Azure subscription"):
                resolve_qualification_target(
                    self.solution, confirm_configured_target=True
                )
        self.assertEqual(1, run_az.call_count)

    def test_locked_run_cannot_be_retargeted_by_changed_env_or_cli(self) -> None:
        self._write_config()
        locked = {
            "tenantId": TENANT_ID,
            "subscriptionId": SUBSCRIPTION_ID,
            "workspaceResourceId": WORKSPACE_ID,
            "workspaceCustomerId": CUSTOMER_ID,
        }
        self.env_file.write_text(
            f"AZURE_TENANT_ID={TENANT_ID}\n"
            "SENTINEL_WORKSPACE_RESOURCE_ID=/subscriptions/"
            "11111111-2222-4333-8444-555555555555/resourceGroups/Other/"
            "providers/Microsoft.OperationalInsights/workspaces/Other\n",
            encoding="utf-8",
        )
        with mock.patch("sentinel_xdr_migration.target_context._run_az") as run_az:
            with self.assertRaisesRegex(ValueError, "conflicts with the locked"):
                resolve_qualification_target(
                    self.solution, locked_context=locked
                )
        run_az.assert_not_called()

        self._write_config()
        different_workspace = (
            f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/Other/"
            "providers/Microsoft.OperationalInsights/workspaces/Other"
        )
        with mock.patch("sentinel_xdr_migration.target_context._run_az") as run_az:
            with self.assertRaisesRegex(ValueError, "conflicts with solution .env"):
                resolve_qualification_target(
                    self.solution,
                    workspace_resource_id=different_workspace,
                    locked_context=locked,
                )
        run_az.assert_not_called()

    def test_locked_target_resumes_without_environment_call(self) -> None:
        self._write_config()
        locked = {
            "tenantId": TENANT_ID,
            "subscriptionId": SUBSCRIPTION_ID,
            "workspaceResourceId": WORKSPACE_ID,
            "workspaceCustomerId": CUSTOMER_ID,
        }
        with mock.patch("sentinel_xdr_migration.target_context._run_az") as run_az:
            target = resolve_qualification_target(
                self.solution, locked_context=locked
            )
        self.assertEqual(locked, target)
        run_az.assert_not_called()

    def test_cli_pr_qualify_accepts_pr_number_and_run_number(self) -> None:
        captured: dict[str, object] = {}

        def fake_evaluate(
            sol_root,
            *,
            mode="auto",
            is_migration=None,
            waivers_file=None,
            acknowledged_exclusions_file=None,
            evidence_dir=None,
            target_version=None,
            pr_number=None,
            run_number=None,
        ):
            captured["pr_number"] = pr_number
            captured["run_number"] = run_number
            return {
                "solutionName": "Sample",
                "solutionVersion": "3.0.0",
                "mode": mode,
                "isMigration": True,
                "validationStatus": "Pass",
                "qualificationStatus": "Pass",
                "migrationStatus": "Pass",
                "overallVerdict": "Pass",
                "summary": {},
            }

        output = io.StringIO()
        with mock.patch(
            "solution_manager.cli.evaluate_solution_pr_qualification",
            side_effect=fake_evaluate,
        ), mock.patch(
            "solution_manager.cli.write_pr_qualification_reports",
            return_value={
                "html": self.solution / "report.html",
                "markdown": self.solution / "summary.md",
            },
        ), redirect_stdout(output):
            rc = main(
                [
                    "pr-qualify",
                    "--solution",
                    str(self.solution),
                    "--pr-number",
                    "42",
                    "--run-number",
                    "7",
                ]
            )
        self.assertEqual(0, rc)
        self.assertEqual(42, captured["pr_number"])
        self.assertEqual(7, captured["run_number"])


if __name__ == "__main__":
    unittest.main()
