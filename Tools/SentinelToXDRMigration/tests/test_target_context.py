from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

from sentinel_xdr_migration.artifacts import artifact_path
from sentinel_xdr_migration.target_context import (
    build_target,
    diagnose_target,
    repair_target,
    require_locked_target,
)
from sentinel_xdr_migration.workflow import initialize_workflow, workflow_status


TENANT_ID = "11111111-2222-4333-8444-555555555555"
SUBSCRIPTION_ID = "22222222-3333-4444-8555-666666666666"
CUSTOMER_ID = "33333333-4444-4555-8666-777777777777"
OLD_WORKSPACE = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/rg-test/"
    "providers/Microsoft.OperationalInsights/workspaces/ws-test"
)
NEW_WORKSPACE = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/OptimizeSentinelResourceGroup/"
    "providers/Microsoft.OperationalInsights/workspaces/ws-test"
)


class TargetContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.solution = Path(self.temp.name) / "Sample"
        self.solution.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _initialize(self) -> None:
        initialize_workflow(
            self.solution,
            workflow_profile="qualification",
            tenant_id=TENANT_ID,
            subscription_id=SUBSCRIPTION_ID,
            workspace_resource_id=OLD_WORKSPACE,
            workspace_customer_id=CUSTOMER_ID,
        )

    def test_build_target_rejects_workspace_subscription_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not match subscription-id"):
            build_target(
                tenant_id=TENANT_ID,
                subscription_id="11111111-1111-1111-1111-111111111111",
                workspace_resource_id=OLD_WORKSPACE,
                workspace_customer_id=CUSTOMER_ID,
            )

    def test_locked_target_rejects_supplied_workspace_mismatch(self) -> None:
        self._initialize()

        with self.assertRaisesRegex(ValueError, "does not match"):
            require_locked_target(
                self.solution,
                workspace_resource_id=NEW_WORKSPACE,
            )

    def test_locked_target_rejects_artifact_state_mismatch(self) -> None:
        self._initialize()
        target_path = artifact_path(self.solution, "qualification-target.json")
        target = json.loads(target_path.read_text(encoding="utf-8"))
        target["workspaceCustomerId"] = "11111111-1111-1111-1111-111111111111"
        target_path.write_text(json.dumps(target), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "does not match workflow state"):
            require_locked_target(self.solution)

    def test_locked_target_rejects_unlocked_artifact(self) -> None:
        self._initialize()
        target_path = artifact_path(self.solution, "qualification-target.json")
        target = json.loads(target_path.read_text(encoding="utf-8"))
        target["locked"] = False
        target_path.write_text(json.dumps(target), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "locked-target identity"):
            require_locked_target(self.solution)

    def test_locked_target_can_be_read_without_materializing_missing_artifact(self) -> None:
        self._initialize()
        target_path = artifact_path(self.solution, "qualification-target.json")
        target_path.unlink()

        target = require_locked_target(self.solution, materialize_missing=False)

        self.assertEqual(OLD_WORKSPACE, target["workspaceResourceId"])
        self.assertFalse(target_path.exists())

    @mock.patch(
        "sentinel_xdr_migration.target_context.shutil.which",
        return_value="az",
    )
    def test_diagnose_and_repair_use_one_exact_match(
        self,
        _which: mock.Mock,
    ) -> None:
        self._initialize()
        commands: list[list[str]] = []

        def runner(command, **_kwargs):
            commands.append(command)
            if command[1:3] == ["account", "show"]:
                return CompletedProcess(
                    command,
                    0,
                    json.dumps(
                        {
                            "tenantId": TENANT_ID,
                            "id": SUBSCRIPTION_ID,
                        }
                    ),
                    "",
                )
            if command[1:3] == ["resource", "show"]:
                return CompletedProcess(
                    command,
                    3,
                    "",
                    "ResourceGroupNotFound",
                )
            if command[1:3] == ["graph", "query"]:
                return CompletedProcess(
                    command,
                    0,
                    json.dumps(
                        {
                            "data": [
                                {
                                    "id": NEW_WORKSPACE,
                                    "customerId": CUSTOMER_ID,
                                }
                            ]
                        }
                    ),
                    "",
                )
            raise AssertionError(command)

        diagnostics = diagnose_target(self.solution, runner=runner)

        self.assertEqual("repair-available", diagnostics["status"])
        graph_command = next(
            command for command in commands if command[1:3] == ["graph", "query"]
        )
        self.assertIn(SUBSCRIPTION_ID, graph_command)
        graph_query = graph_command[graph_command.index("-q") + 1]
        self.assertIn(CUSTOMER_ID, graph_query)
        self.assertNotIn("project-away", graph_query)

        with self.assertRaisesRegex(ValueError, "approve-target-update"):
            repair_target(
                self.solution,
                approve_target_update=False,
                state_dir=Path(self.temp.name) / "config",
            )

        repaired = repair_target(
            self.solution,
            approve_target_update=True,
            state_dir=Path(self.temp.name) / "config",
        )

        self.assertEqual(NEW_WORKSPACE, repaired["target"]["workspaceResourceId"])
        state = workflow_status(self.solution)
        self.assertEqual(NEW_WORKSPACE, state["context"]["workspaceResourceId"])
        self.assertEqual(TENANT_ID, state["context"]["tenantId"])
        self.assertEqual(SUBSCRIPTION_ID, state["context"]["subscriptionId"])
        self.assertEqual(CUSTOMER_ID, state["context"]["workspaceCustomerId"])


if __name__ == "__main__":
    unittest.main()
