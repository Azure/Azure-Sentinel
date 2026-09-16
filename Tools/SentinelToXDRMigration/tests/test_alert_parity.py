from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration.alert_parity import (
    _capture_queries,
    _set_pair_enabled,
    compare_alert_captures,
    complete_alert_parity,
    start_alert_parity,
    start_alert_parity_batch,
)


def alert(match_key: str, *, account: str = "user@example.test") -> dict:
    return {
        "matchKey": match_key,
        "severity": "high",
        "tactics": ["Exfiltration"],
        "entities": {"accounts": [{"upn": account}]},
        "evidence": {"eventIds": [match_key], "bytes": 1024},
    }


class AlertParityTests(unittest.TestCase):
    def test_custom_detection_capture_query_uses_valid_unambiguous_columns(
        self,
    ) -> None:
        queries = _capture_queries(
            {"displayName": "Rule"},
            "2026-09-10T13:00:00+00:00",
            "192.0.2.11",
        )

        custom = queries["customDetection"]
        self.assertIn('DetectionSource == "Custom detection"', custom)
        self.assertIn("AlertTimestamp=Timestamp", custom)
        self.assertIn("EvidenceTimestamp=Timestamp", custom)
        self.assertIn("URL=RemoteUrl", custom)
        self.assertNotIn(", URL, Timestamp", custom)
        self.assertIn('ProviderName == "ASI Scheduled Alerts"', queries["sentinel"])
        self.assertIn("summarize arg_max", queries["sentinel"])

    @mock.patch(
        "sentinel_xdr_migration.alert_parity._graph_request",
        return_value=(200, {"status": "enabled"}),
    )
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._arm_request",
        return_value=(200, {"properties": {"enabled": True}}),
    )
    def test_rule_enablement_omits_sentinel_read_only_properties(
        self, arm_request: mock.Mock, _graph_request: mock.Mock
    ) -> None:
        pair = {
            "analyticRuleId": "source-id",
            "customDetectionId": "detection-id",
            "sentinelResource": {
                "kind": "Scheduled",
                "properties": {
                    "displayName": "Rule",
                    "query": "Cloudflare | take 1",
                    "enabled": False,
                    "lastModifiedUtc": "2026-09-10T00:00:00Z",
                    "createdBy": {"name": "read-only"},
                },
            },
        }

        errors = _set_pair_enabled(
            pair,
            "/subscriptions/s/resourceGroups/r/providers/"
            "Microsoft.OperationalInsights/workspaces/w",
            "arm-token",
            "graph-token",
            True,
        )

        self.assertEqual(errors, [])
        body = arm_request.call_args.args[3]
        self.assertTrue(body["properties"]["enabled"])
        self.assertNotIn("lastModifiedUtc", body["properties"])
        self.assertNotIn("createdBy", body["properties"])

    def test_strict_comparison_passes_for_identical_alerts(self) -> None:
        results = {
            "results": [
                {
                    "detection": "Rule.yaml",
                    "analyticRule": {"alerts": [alert("event-1")]},
                    "customDetection": {"alerts": [alert("event-1")]},
                }
            ]
        }

        comparison = compare_alert_captures({"Rule.yaml"}, results)

        self.assertTrue(comparison[0]["passed"])
        self.assertTrue(all(comparison[0]["dimensions"].values()))

    def test_strict_comparison_fails_entity_mismatch(self) -> None:
        results = {
            "results": [
                {
                    "detection": "Rule.yaml",
                    "analyticRule": {"alerts": [alert("event-1")]},
                    "customDetection": {
                        "alerts": [alert("event-1", account="other@example.test")]
                    },
                }
            ]
        }

        comparison = compare_alert_captures({"Rule.yaml"}, results)

        self.assertFalse(comparison[0]["passed"])
        self.assertFalse(comparison[0]["dimensions"]["entities"])

    def test_strict_comparison_fails_alert_count_mismatch(self) -> None:
        results = {
            "results": [
                {
                    "detection": "Rule.yaml",
                    "analyticRule": {"alerts": [alert("event-1")]},
                    "customDetection": {"alerts": []},
                }
            ]
        }

        comparison = compare_alert_captures({"Rule.yaml"}, results)

        self.assertFalse(comparison[0]["passed"])
        self.assertFalse(comparison[0]["dimensions"]["alertCount"])

    def test_strict_comparison_rejects_shared_benign_false_positive(self) -> None:
        results = {
            "results": [
                {
                    "detection": "Rule.yaml",
                    "analyticRule": {
                        "alerts": [alert("malicious"), alert("benign-control")]
                    },
                    "customDetection": {
                        "alerts": [alert("malicious"), alert("benign-control")]
                    },
                }
            ]
        }

        comparison = compare_alert_captures(
            {"Rule.yaml"}, results, expected_match_keys={"malicious"}
        )

        self.assertFalse(comparison[0]["passed"])
        self.assertFalse(comparison[0]["dimensions"]["expectedMatches"])

    def test_strict_comparison_uses_per_detection_expected_keys(self) -> None:
        results = {
            "results": [
                {
                    "detection": "One.yaml",
                    "analyticRule": {"alerts": [alert("one-event")]},
                    "customDetection": {"alerts": [alert("one-event")]},
                },
                {
                    "detection": "Two.yaml",
                    "analyticRule": {"alerts": [alert("two-event")]},
                    "customDetection": {"alerts": [alert("two-event")]},
                },
            ]
        }

        comparison = compare_alert_captures(
            {"One.yaml", "Two.yaml"},
            results,
            expected_match_keys_by_detection={
                "One.yaml": {"one-event"},
                "Two.yaml": {"two-event"},
            },
        )

        self.assertTrue(all(item["passed"] for item in comparison))

    @mock.patch(
        "sentinel_xdr_migration.alert_parity._disable_all",
        return_value=[
            {"detection": "Rule.yaml", "disabled": True, "errors": []}
        ],
    )
    def test_complete_always_disables_rules_on_invalid_capture(
        self, disable: mock.Mock
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            state = {
                "runId": "run-1",
                "status": "awaiting-alerts",
                "scenarioMarker": "scenario-1",
                "workspaceResourceId": "/subscriptions/s/resourceGroups/r/providers/Microsoft.OperationalInsights/workspaces/w",
                "rules": [{"detection": "Rule.yaml"}],
            }
            (output / "alert-parity-state.json").write_text(
                json.dumps(state), encoding="utf-8"
            )
            results = root / "results.json"
            results.write_text("{}", encoding="utf-8")

            report = complete_alert_parity(root, results_path=results)

        disable.assert_called_once()
        self.assertEqual(report["status"], "failed")
        self.assertTrue(report["cleanup"][0]["disabled"])

    @mock.patch(
        "sentinel_xdr_migration.alert_parity._disable_all",
        return_value=[
            {"detection": "Rule.yaml", "disabled": True, "errors": []}
        ],
    )
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._ingest",
        side_effect=RuntimeError("rejected"),
    )
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._set_pair_enabled",
        return_value=[],
    )
    @mock.patch("sentinel_xdr_migration.alert_parity._read_rule_states")
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._deployment_token",
        return_value="graph-token",
    )
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._arm_token",
        return_value="arm-token",
    )
    def test_start_disables_rules_when_ingestion_fails(
        self,
        _arm: mock.Mock,
        _graph: mock.Mock,
        _read: mock.Mock,
        _enable: mock.Mock,
        _ingest: mock.Mock,
        disable: mock.Mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            payload = root / "payload.json"
            payload.write_text(
                json.dumps([{"user": "scenario-user@example.test"}]),
                encoding="utf-8",
            )
            pair = {
                "detection": "Rule.yaml",
                "displayName": "Rule",
                "analyticRuleId": "source-id",
                "customDetectionId": "detection-id",
                "entityMappings": {},
                "sentinelResource": {"kind": "Scheduled", "properties": {}},
            }
            with mock.patch(
                "sentinel_xdr_migration.alert_parity._load_pairs",
                return_value=(root, [pair]),
            ):
                with self.assertRaisesRegex(RuntimeError, "rejected"):
                    start_alert_parity(
                        root,
                        workspace_resource_id=(
                            "/subscriptions/s/resourceGroups/r/providers/"
                            "Microsoft.OperationalInsights/workspaces/w"
                        ),
                        contract=root / "contract.json",
                        payload=payload,
                        scenario_marker="scenario-user@example.test",
                    )

            state = json.loads(
                (output / "alert-parity-state.json").read_text(encoding="utf-8")
            )

        disable.assert_called_once()
        self.assertEqual(state["status"], "failed")
        self.assertTrue(state["cleanup"][0]["disabled"])

    @mock.patch(
        "sentinel_xdr_migration.alert_parity._ingest",
        side_effect=[{"status": "accepted"}, {"status": "accepted"}],
    )
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._set_pair_enabled",
        return_value=[],
    )
    @mock.patch("sentinel_xdr_migration.alert_parity._read_rule_states")
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._deployment_token",
        return_value="graph-token",
    )
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._arm_token",
        return_value="arm-token",
    )
    def test_batch_start_enables_all_and_ingests_each_fixture(
        self,
        _arm: mock.Mock,
        _graph: mock.Mock,
        _read: mock.Mock,
        enable: mock.Mock,
        ingest: mock.Mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            fixtures = []
            pairs = []
            for index, name in enumerate(("One.yaml", "Two.yaml"), start=1):
                contract = root / f"contract-{index}.json"
                payload = root / f"payload-{index}.json"
                contract.write_text("{}", encoding="utf-8")
                payload.write_text(
                    json.dumps([{"marker": f"scenario-{index}"}]),
                    encoding="utf-8",
                )
                fixtures.append(
                    {
                        "detection": name,
                        "contract": contract.name,
                        "payload": payload.name,
                        "scenarioMarker": f"scenario-{index}",
                        "expectedMatchKeys": [f"event-{index}"],
                    }
                )
                pairs.append(
                    {
                        "detection": name,
                        "displayName": name,
                        "analyticRuleId": f"source-{index}",
                        "customDetectionId": f"detection-{index}",
                        "entityMappings": {},
                    }
                )
            plan = root / "plan.json"
            plan.write_text(json.dumps({"fixtures": fixtures}), encoding="utf-8")

            with mock.patch(
                "sentinel_xdr_migration.alert_parity._load_pairs",
                return_value=(root, pairs),
            ):
                result = start_alert_parity_batch(
                    root,
                    workspace_resource_id=(
                        "/subscriptions/s/resourceGroups/r/providers/"
                        "Microsoft.OperationalInsights/workspaces/w"
                    ),
                    plan_path=plan,
                )

            state = json.loads(
                (output / "alert-parity-state.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result["rulesEnabled"], 2)
        self.assertEqual(result["fixturesIngested"], 2)
        self.assertEqual(enable.call_count, 2)
        self.assertEqual(ingest.call_count, 2)
        self.assertEqual(
            state["expectedMatchKeysByDetection"]["One.yaml"],
            ["event-1"],
        )


if __name__ == "__main__":
    unittest.main()
