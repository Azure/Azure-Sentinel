from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration.deployment import (
    _deployment_token,
    deploy_solution,
    graph_detection_payload,
)

TARGET = {
    "tenantId": "39768270-33ce-4b90-a1a6-e0caeb3ba0ab",
    "subscriptionId": "42382e39-f157-46d1-a931-b8cfd779ece5",
    "workspaceResourceId": (
        "/subscriptions/42382e39-f157-46d1-a931-b8cfd779ece5/"
        "resourceGroups/rg/providers/Microsoft.OperationalInsights/workspaces/ws"
    ),
    "workspaceCustomerId": "756386d8-e2d4-4f09-905a-74b24313721f",
}


def document(rule_id: str = "test-rule") -> dict:
    return {
        "schemaVersion": "1.0.0",
        "kind": "CustomDetection",
        "resourceType": "Microsoft.Security/detectionRules",
        "apiVersion": "2026-06-01-preview",
        "contentProvenance": {
            "source": {
                "platform": "Microsoft Sentinel",
                "kind": "AnalyticsRule",
                "id": "source-id",
                "path": "Analytic Rules/rule.yaml",
                "querySha256": "hash",
                "schedule": {
                    "queryFrequency": "1h",
                    "queryPeriod": "1h",
                },
            },
            "conversion": {
                "tool": "sentinel-to-xdr-migration",
                "version": "0.1.0",
                "status": "converted",
                "reviewRequired": False,
                "reviewReasons": [],
                "requiredWorkloads": ["defender"],
                "warnings": [],
                "errors": [],
            },
        },
        "properties": {
            "id": rule_id,
            "displayName": "Test rule",
            "status": "disabled",
            "queryCondition": {"queryText": "DeviceInfo | take 1"},
            "schedule": {"frequency": "PT1H"},
            "detectionAction": {
                "alertTemplate": {
                    "title": "Test rule",
                    "description": "Test",
                    "severity": "low",
                    "entityMappings": {
                        "hosts": [{"id": "host1", "deviceIdColumn": "DeviceId"}]
                    },
                }
            },
        },
    }


class DeploymentTests(unittest.TestCase):
    def test_payload_is_graph_ready_and_disabled(self) -> None:
        payload = graph_detection_payload(document())

        self.assertEqual(
            payload["@odata.type"], "#microsoft.graph.security.detectionRule"
        )
        self.assertEqual(payload["status"], "disabled")

    def test_payload_rejects_review_required_detection(self) -> None:
        value = document()
        value["contentProvenance"]["conversion"]["status"] = "needsReview"
        value["contentProvenance"]["conversion"]["reviewRequired"] = True

        with self.assertRaisesRegex(ValueError, "no review required"):
            graph_detection_payload(value)

    @mock.patch("azure.identity.AzureCliCredential")
    def test_deployment_token_falls_back_to_azure_cli(
        self, credential: mock.Mock
    ) -> None:
        credential.return_value.get_token.return_value.token = "cli-token"
        with tempfile.TemporaryDirectory() as temp:
            token = _deployment_token(temp)

        self.assertEqual(token, "cli-token")

    @mock.patch(
        "sentinel_xdr_migration.deployment._deployment_token",
        return_value="token",
    )
    @mock.patch(
        "sentinel_xdr_migration.deployment.require_locked_target",
        return_value=TARGET,
    )
    @mock.patch("sentinel_xdr_migration.deployment._graph_request")
    def test_deploy_creates_missing_rule(
        self, request: mock.Mock, _target: mock.Mock, _token: mock.Mock
    ) -> None:
        request.side_effect = [
            (404, {"error": {"code": "NotFound"}}),
            (201, {"id": "test-rule"}),
            (200, {"id": "test-rule", "status": "disabled"}),
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            (output / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )

            result = deploy_solution(root)

        self.assertEqual(result["succeeded"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["results"][0]["deployedStatus"], "disabled")
        self.assertEqual(request.call_args_list[1].args[0], "POST")

    @mock.patch(
        "sentinel_xdr_migration.deployment._deployment_token",
        return_value="token",
    )
    @mock.patch(
        "sentinel_xdr_migration.deployment.require_locked_target",
        return_value=TARGET,
    )
    @mock.patch("sentinel_xdr_migration.deployment._graph_request")
    def test_deploy_updates_existing_rule(
        self, request: mock.Mock, _target: mock.Mock, _token: mock.Mock
    ) -> None:
        request.side_effect = [
            (200, {"id": "test-rule"}),
            (200, {"id": "test-rule"}),
            (200, {"id": "test-rule", "status": "disabled"}),
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            (output / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )

            result = deploy_solution(root)

        self.assertEqual(result["succeeded"], 1)
        self.assertEqual(result["results"][0]["deployedStatus"], "disabled")
        self.assertEqual(request.call_args_list[1].args[0], "PATCH")
        update = request.call_args_list[1].args[3]
        self.assertNotIn("id", update)


if __name__ == "__main__":
    unittest.main()
