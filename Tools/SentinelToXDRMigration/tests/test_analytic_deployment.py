from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration.analytic_deployment import (
    analytic_rule_payload,
    deploy_analytic_rules,
)


def document() -> dict:
    return {
        "id": "a7ce6135-9d55-4f14-b058-adc2e920a4fb",
        "name": "Test analytic rule",
        "description": "Test",
        "severity": "Medium",
        "queryFrequency": "1h",
        "queryPeriod": "2h",
        "triggerOperator": "gt",
        "triggerThreshold": 0,
        "query": "Cloudflare | take 1",
        "tactics": ["InitialAccess"],
        "relevantTechniques": ["T1190"],
        "entityMappings": [
            {
                "entityType": "IP",
                "fieldMappings": [
                    {"identifier": "Address", "columnName": "SrcIpAddr"}
                ],
            }
        ],
        "version": "1.0.1",
        "kind": "Scheduled",
    }


class AnalyticDeploymentTests(unittest.TestCase):
    def test_payload_is_disabled_and_preserves_source_metadata(self) -> None:
        payload = analytic_rule_payload(document())

        self.assertFalse(payload["properties"]["enabled"])
        self.assertEqual(payload["properties"]["queryFrequency"], "PT1H")
        self.assertEqual(payload["properties"]["queryPeriod"], "PT2H")
        self.assertEqual(payload["properties"]["triggerOperator"], "GreaterThan")
        self.assertEqual(
            payload["properties"]["alertRuleTemplateName"], document()["id"]
        )

    @mock.patch(
        "sentinel_xdr_migration.analytic_deployment._arm_token",
        return_value="token",
    )
    @mock.patch("sentinel_xdr_migration.analytic_deployment._arm_request")
    def test_deploy_upserts_rule_disabled(
        self, request: mock.Mock, _token: mock.Mock
    ) -> None:
        request.return_value = (
            201,
            {"properties": {"enabled": False}},
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "Analytic Rules"
            source.mkdir()
            (source / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )

            result = deploy_analytic_rules(
                root,
                workspace_resource_id="/subscriptions/sub/resourceGroups/rg"
                "/providers/Microsoft.OperationalInsights/workspaces/ws",
            )

        self.assertEqual(result["succeeded"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(request.call_args.args[0], "PUT")
        self.assertFalse(request.call_args.args[3]["properties"]["enabled"])


if __name__ == "__main__":
    unittest.main()
