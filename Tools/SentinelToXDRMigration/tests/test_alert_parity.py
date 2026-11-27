from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration.alert_parity import (
    _capture_queries,
    _qualification_scope,
    _set_pair_enabled,
    compare_alert_captures,
    complete_alert_parity,
    start_alert_parity,
    start_alert_parity_batch,
)
from sentinel_xdr_migration.artifacts import artifact_path

TARGET = {
    "tenantId": "11111111-2222-4333-8444-555555555555",
    "subscriptionId": "22222222-3333-4444-8555-666666666666",
    "workspaceResourceId": (
        "/subscriptions/22222222-3333-4444-8555-666666666666/"
        "resourceGroups/r/providers/Microsoft.OperationalInsights/workspaces/w"
    ),
    "workspaceCustomerId": "33333333-4444-4555-8666-777777777777",
}


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
    @mock.patch(
        "sentinel_xdr_migration.alert_parity.require_locked_target",
        return_value=TARGET,
    )
    def test_complete_always_disables_rules_on_invalid_capture(
        self, _target: mock.Mock, disable: mock.Mock
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            state = {
                "runId": "run-1",
                "status": "awaiting-alerts",
                "scenarioMarker": "scenario-1",
                "workspaceResourceId": TARGET["workspaceResourceId"],
                "target": TARGET,
                "rules": [{"detection": "Rule.yaml"}],
            }
            artifact_path(root, "alert-parity-state.json", create_parent=True).write_text(
                json.dumps(state), encoding="utf-8"
            )
            results = root / "results.json"
            results.write_text("{}", encoding="utf-8")

            report = complete_alert_parity(root, results_path=results)

        disable.assert_called_once()
        self.assertEqual(report["status"], "failed")
        self.assertTrue(report["cleanup"][0]["disabled"])

    @mock.patch(
        "sentinel_xdr_migration.packaging_selection.current_applied_package_selection",
        return_value={
            "plan": {
                "planSha256": "new-plan",
                "selection": {"xdrDetections": ["XDR Detections/Rule.yaml"]},
                "summary": {"outcome": "partial"},
            }
        },
    )
    @mock.patch(
        "sentinel_xdr_migration.alert_parity._disable_all",
        return_value=[
            {"detection": "Rule.yaml", "disabled": True, "errors": []}
        ],
    )
    @mock.patch(
        "sentinel_xdr_migration.alert_parity.require_locked_target",
        return_value=TARGET,
    )
    def test_complete_rejects_changed_selection_and_still_cleans_up(
        self,
        _target: mock.Mock,
        disable: mock.Mock,
        _selection: mock.Mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detection = root / "XDR Detections" / "Rule.yaml"
            detection.parent.mkdir(parents=True)
            detection.write_text("kind: CustomDetection\n", encoding="utf-8")
            pair = {
                "detection": "Rule.yaml",
                "analyticRuleId": "source-id",
                "customDetectionId": "detection-id",
            }
            original_selection = {
                "plan": {
                    "planSha256": "old-plan",
                    "selection": {"xdrDetections": ["XDR Detections/Rule.yaml"]},
                    "summary": {"outcome": "partial"},
                }
            }
            state = {
                "runId": "run-1",
                "status": "awaiting-alerts",
                "scenarioMarker": "scenario-1",
                "target": TARGET,
                "rules": [pair],
                "qualificationScope": _qualification_scope(
                    root, [pair], original_selection
                ),
            }
            artifact_path(root, "alert-parity-state.json", create_parent=True).write_text(
                json.dumps(state), encoding="utf-8"
            )
            results = root / "results.json"
            results.write_text("{}", encoding="utf-8")

            report = complete_alert_parity(root, results_path=results)

        disable.assert_called_once()
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["qualificationScopeVerified"])
        self.assertIn("no longer matches", report["scopeVerificationError"])
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
    @mock.patch(
        "sentinel_xdr_migration.alert_parity.require_locked_target",
        return_value=TARGET,
    )
    def test_start_disables_rules_when_ingestion_fails(
        self,
        _target: mock.Mock,
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
                        workspace_resource_id=TARGET["workspaceResourceId"],
                        contract=root / "contract.json",
                        payload=payload,
                        scenario_marker="scenario-user@example.test",
                    )

            state = json.loads(
                artifact_path(root, "alert-parity-state.json").read_text(
                    encoding="utf-8"
                )
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
    @mock.patch(
        "sentinel_xdr_migration.alert_parity.require_locked_target",
        return_value=TARGET,
    )
    def test_batch_start_enables_all_and_ingests_each_fixture(
        self,
        _target: mock.Mock,
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
                    workspace_resource_id=TARGET["workspaceResourceId"],
                    plan_path=plan,
                )

            state = json.loads(
                artifact_path(root, "alert-parity-state.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(result["rulesEnabled"], 2)
        self.assertEqual(result["fixturesIngested"], 2)
        self.assertEqual(enable.call_count, 2)
        self.assertEqual(ingest.call_count, 2)
        self.assertEqual(
            state["expectedMatchKeysByDetection"]["One.yaml"],
            ["event-1"],
        )

    @mock.patch(
        "sentinel_xdr_migration.alert_parity._ingest",
        return_value={"status": "accepted", "recordsAccepted": 2},
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
    @mock.patch(
        "sentinel_xdr_migration.alert_parity.require_locked_target",
        return_value=TARGET,
    )
    def test_batch_start_combines_payloads_for_shared_contract(
        self,
        _target: mock.Mock,
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
            shared_contract = root / "shared-contract.json"
            shared_contract.write_text("{}", encoding="utf-8")
            fixtures = []
            pairs = []
            for index, name in enumerate(("One.yaml", "Two.yaml"), start=1):
                payload = root / f"payload-{index}.json"
                payload.write_text(
                    json.dumps([{"marker": f"scenario-{index}"}]),
                    encoding="utf-8",
                )
                fixtures.append(
                    {
                        "detection": name,
                        "contract": shared_contract.name,
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
                    workspace_resource_id=TARGET["workspaceResourceId"],
                    plan_path=plan,
                )

            ingest.assert_called_once()
            combined_payload_path = Path(ingest.call_args.args[1])
            combined_records = json.loads(
                combined_payload_path.read_text(encoding="utf-8")
            )

        self.assertEqual(result["rulesEnabled"], 2)
        self.assertEqual(result["fixturesIngested"], 2)
        self.assertEqual(enable.call_count, 2)
        self.assertEqual(
            combined_records,
            [{"marker": "scenario-1"}, {"marker": "scenario-2"}],
        )

    def test_cd_only_expected_behavior_positive_negative_controls_and_disabled_restoration(
        self,
    ) -> None:
        import yaml
        from solution_manager.qualification.alert_parity import (
            _disable_all,
            _load_pairs,
            _read_rule_states,
            _set_pair_enabled,
            compute_query_sha256,
            evaluate_cd_only_expected_behavior,
        )

        query_text = "DeviceProcessEvents | where FileName =~ 'mimikatz.exe'"
        expected_sha = compute_query_sha256(query_text)
        native_doc = {
            "schemaVersion": "1.0.0",
            "version": "3.1.0",
            "kind": "CustomDetection",
            "resourceType": "Microsoft.Security/detectionRules",
            "apiVersion": "2026-06-01-preview",
            "contentProvenance": {
                "requiredWorkloads": [{"workload": "mde", "dataTypes": ["DeviceProcessEvents"]}],
                "requiredDataConnectors": [],
            },
            "properties": {
                "id": "xdr-11111111-2222-3333-4444-555555555555",
                "displayName": "Native CD Only 01",
                "status": "disabled",
                "queryCondition": {"queryText": query_text},
                "schedule": {"frequency": "PT1H"},
                "detectionAction": {
                    "alertTemplate": {
                        "title": "Native CD Only 01",
                        "description": "Test",
                        "severity": "high",
                        "entityMappings": {
                            "hosts": [{"id": "host1", "deviceIdColumn": "DeviceId"}]
                        },
                    }
                },
            },
        }

        passing = evaluate_cd_only_expected_behavior(
            native_doc,
            [alert("pos-control-1")],
            positive_control_keys=["pos-control-1"],
            negative_control_keys=["neg-control-1"],
            initial_disabled=True,
            returned_to_disabled=True,
        )
        self.assertTrue(passing["passed"])
        self.assertEqual("passed", passing["status"])
        self.assertEqual(expected_sha, passing["querySha256"])
        self.assertTrue(passing["positiveControlsPassed"])
        self.assertTrue(passing["negativeControlsPassed"])
        self.assertTrue(passing["disabledRestorationPassed"])
        self.assertTrue(passing["tkQ11Passed"])

        neg_triggered = evaluate_cd_only_expected_behavior(
            native_doc,
            [alert("pos-control-1"), alert("neg-control-1")],
            positive_control_keys=["pos-control-1"],
            negative_control_keys=["neg-control-1"],
            initial_disabled=True,
            returned_to_disabled=True,
        )
        self.assertFalse(neg_triggered["passed"])
        self.assertFalse(neg_triggered["negativeControlsPassed"])
        self.assertEqual(["neg-control-1"], neg_triggered["matchedNegativeControls"])

        not_restored = evaluate_cd_only_expected_behavior(
            native_doc,
            [alert("pos-control-1")],
            positive_control_keys=["pos-control-1"],
            negative_control_keys=["neg-control-1"],
            initial_disabled=True,
            returned_to_disabled=False,
        )
        self.assertFalse(not_restored["passed"])
        self.assertFalse(not_restored["disabledRestorationPassed"])

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            (output / "Native.yaml").write_text(yaml.safe_dump(native_doc), encoding="utf-8")
            _, loaded_pairs = _load_pairs(root)
            self.assertEqual(1, len(loaded_pairs))
            self.assertTrue(loaded_pairs[0]["cdOnly"])
            self.assertIsNone(loaded_pairs[0]["analyticRuleId"])
            self.assertEqual(expected_sha, loaded_pairs[0]["querySha256"])

            with (
                mock.patch(
                    "sentinel_xdr_migration.alert_parity._arm_request"
                ) as arm_req,
                mock.patch(
                    "sentinel_xdr_migration.alert_parity._graph_request",
                    return_value=(200, {"id": "xdr-11111111-2222-3333-4444-555555555555", "status": "disabled", "isEnabled": False}),
                ) as graph_req,
            ):
                states = _read_rule_states(
                    loaded_pairs,
                    TARGET["workspaceResourceId"],
                    "arm-token",
                    "graph-token",
                )
                self.assertEqual(1, len(states))
                self.assertTrue(states[0]["cdOnly"])
                self.assertTrue(states[0]["initialDisabled"])
                arm_req.assert_not_called()
                graph_req.assert_called_once()

                errs = _set_pair_enabled(
                    loaded_pairs[0],
                    TARGET["workspaceResourceId"],
                    "arm-token",
                    "graph-token",
                    True,
                )
                self.assertEqual([], errs)
                arm_req.assert_not_called()

                state_obj = {
                    "target": TARGET,
                    "workspaceResourceId": TARGET["workspaceResourceId"],
                    "rules": loaded_pairs,
                }
                cleanup = _disable_all(
                    state_obj,
                    arm_token="arm-token",
                    graph_token="graph-token",
                )
                self.assertTrue(cleanup[0]["returnedToDisabled"])
                self.assertTrue(state_obj["tkQ11Passed"])

    def test_migrated_detection_cannot_be_downgraded_to_cd_only_in_compare_and_complete(
        self,
    ) -> None:
        import yaml
        from solution_manager.qualification.alert_parity import (
            _expected_alert_modes_by_detection,
            poll_alert_parity_batch,
        )

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            migrated_doc = {
                "kind": "CustomDetection",
                "contentProvenance": {
                    "origin": "migrated",
                    "source": {"id": "11111111-2222-3333-4444-555555555555"},
                    "conversion": {"status": "converted", "reviewRequired": False},
                },
                "properties": {
                    "id": "xdr-11111111-2222-3333-4444-555555555555",
                    "displayName": "Migrated Rule",
                    "queryCondition": {"queryText": "DeviceEvents | take 1"},
                    "detectionAction": {"alertTemplate": {}},
                },
            }
            native_doc = {
                "kind": "CustomDetection",
                "contentProvenance": {"origin": "native"},
                "properties": {
                    "id": "xdr-22222222-3333-4444-5555-666666666666",
                    "displayName": "Native Rule",
                    "queryCondition": {"queryText": "DeviceProcessEvents | take 1"},
                    "detectionAction": {"alertTemplate": {}},
                },
            }
            (output / "Migrated.yaml").write_text(
                yaml.safe_dump(migrated_doc), encoding="utf-8"
            )
            (output / "Native.yaml").write_text(
                yaml.safe_dump(native_doc), encoding="utf-8"
            )
            pairs = [
                {
                    "detection": "Migrated.yaml",
                    "displayName": "Migrated Rule",
                    "analyticRuleId": "11111111-2222-3333-4444-555555555555",
                    "customDetectionId": "xdr-11111111-2222-3333-4444-555555555555",
                    "cdOnly": False,
                },
                {
                    "detection": "Native.yaml",
                    "displayName": "Native Rule",
                    "analyticRuleId": None,
                    "customDetectionId": "xdr-22222222-3333-4444-5555-666666666666",
                    "cdOnly": True,
                },
            ]
            expected_modes = _expected_alert_modes_by_detection(root, pairs)
            self.assertEqual(
                {"Migrated.yaml": "parity", "Native.yaml": "cd-only"},
                expected_modes,
            )

            for bad_entry in (
                {
                    "detection": "Migrated.yaml",
                    "cdOnly": True,
                    "customDetection": {"alerts": [alert("event-1")]},
                },
                {
                    "detection": "Migrated.yaml",
                    "mode": "cd-only",
                    "customDetection": {"alerts": [alert("event-1")]},
                },
                {
                    "detection": "Migrated.yaml",
                    "customDetection": {"alerts": [alert("event-1")]},
                },
            ):
                with self.assertRaisesRegex(
                    ValueError, "Migrated.yaml: migrated detection requires"
                ):
                    compare_alert_captures(
                        {"Migrated.yaml"},
                        {"results": [bad_entry]},
                        expected_modes_by_detection=expected_modes,
                    )

            for bad_native in (
                {
                    "detection": "Native.yaml",
                    "cdOnly": False,
                    "customDetection": {"alerts": [alert("event-1")]},
                },
                {
                    "detection": "Native.yaml",
                    "mode": "parity",
                    "customDetection": {"alerts": [alert("event-1")]},
                },
                {
                    "detection": "Native.yaml",
                    "analyticRule": {"alerts": [alert("event-1")]},
                    "customDetection": {"alerts": [alert("event-1")]},
                },
            ):
                with self.assertRaisesRegex(
                    ValueError, "Native.yaml: native detection requires cd-only mode"
                ):
                    compare_alert_captures(
                        {"Native.yaml"},
                        {"results": [bad_native]},
                        expected_modes_by_detection=expected_modes,
                    )

            valid_compare = compare_alert_captures(
                {"Migrated.yaml", "Native.yaml"},
                {
                    "results": [
                        {
                            "detection": "Migrated.yaml",
                            "analyticRule": {"alerts": [alert("event-1")]},
                            "customDetection": {"alerts": [alert("event-1")]},
                        },
                        {
                            "detection": "Native.yaml",
                            "cdOnly": True,
                            "mode": "cd-only",
                            "customDetection": {"alerts": [alert("event-2")]},
                        },
                    ]
                },
                expected_modes_by_detection=expected_modes,
            )
            self.assertTrue(all(item["passed"] for item in valid_compare))

            # Omitting a detection from captures when expected_modes_by_detection has it must fail
            with self.assertRaisesRegex(ValueError, r"missing detections: Native\.yaml"):
                compare_alert_captures(
                    set(),
                    {
                        "results": [
                            {
                                "detection": "Migrated.yaml",
                                "analyticRule": {"alerts": [alert("event-1")]},
                                "customDetection": {"alerts": [alert("event-1")]},
                            }
                        ]
                    },
                    expected_modes_by_detection=expected_modes,
                )

            # Windows backslash path in expected_detections normalizes cleanly
            backslash_compare = compare_alert_captures(
                {"Sub\\Native.yaml"},
                {
                    "results": [
                        {
                            "detection": "Sub/Native.yaml",
                            "cdOnly": True,
                            "mode": "cd-only",
                            "customDetection": {"alerts": [alert("event-2")]},
                        }
                    ]
                },
                expected_modes_by_detection={"Sub\\Native.yaml": "cd-only"},
            )
            self.assertEqual(1, len(backslash_compare))
            self.assertTrue(backslash_compare[0]["passed"])

            scope = _qualification_scope(root, [pairs[0]], None)
            state_payload = {
                "runId": "run-1",
                "status": "awaiting-alerts",
                "target": TARGET,
                "workspaceResourceId": TARGET["workspaceResourceId"],
                "qualificationScope": scope,
                "rules": [pairs[0]],
                "fixtures": [{"detection": "Migrated.yaml"}],
            }
            state_path = artifact_path(root, "alert-parity-state.json", create_parent=True)
            state_path.write_text(json.dumps(state_payload), encoding="utf-8")
            captures_path = root / "downgraded-captures.json"
            captures_path.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "detection": "Migrated.yaml",
                                "cdOnly": True,
                                "mode": "cd-only",
                                "customDetection": {"alerts": [alert("event-1")]},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.alert_parity.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.alert_parity._verify_qualification_scope",
                    return_value=scope,
                ),
                mock.patch(
                    "sentinel_xdr_migration.alert_parity._disable_all",
                    return_value=[{"detection": "Migrated.yaml", "disabled": True, "errors": []}],
                ),
            ):
                complete_report = complete_alert_parity(root, results_path=captures_path)
                self.assertEqual("failed", complete_report["status"])
                self.assertIn("migrated detection requires", complete_report["comparisonError"])

                state_path.write_text(json.dumps(state_payload), encoding="utf-8")
                poll_report = poll_alert_parity_batch(root, results_path=captures_path)
                self.assertEqual("failed", poll_report["status"])
                self.assertIn("migrated detection requires", poll_report["comparisonError"])

    def test_persisted_positive_and_negative_controls_cannot_be_overridden_by_submitted_captures(
        self,
    ) -> None:
        import yaml
        from solution_manager.qualification.alert_parity import poll_alert_parity_batch

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            native_doc = {
                "kind": "CustomDetection",
                "contentProvenance": {"origin": "native"},
                "properties": {
                    "id": "xdr-11111111-1111-4111-8111-111111111111",
                    "displayName": "Native Rule",
                    "queryCondition": {"queryText": "DeviceInfo | take 1"},
                    "detectionAction": {"alertTemplate": {"title": "Native Rule", "severity": "medium"}},
                },
            }
            (output / "NativeRule.yaml").write_text(
                yaml.safe_dump(native_doc), encoding="utf-8"
            )
            pairs = [
                {
                    "detection": "NativeRule.yaml",
                    "displayName": "Native Rule",
                    "analyticRuleId": None,
                    "customDetectionId": "xdr-11111111-1111-4111-8111-111111111111",
                    "cdOnly": True,
                }
            ]
            scope = _qualification_scope(root, pairs, None)
            state_payload = {
                "runId": "run-native-controls",
                "status": "awaiting-alerts",
                "target": TARGET,
                "workspaceResourceId": TARGET["workspaceResourceId"],
                "qualificationScope": scope,
                "rules": pairs,
                "expectedMatchKeys": ["reviewed-positive"],
                "negativeControlKeys": ["reviewed-negative"],
                "fixtures": [{"detection": "NativeRule.yaml"}],
            }
            state_path = artifact_path(root, "alert-parity-state.json", create_parent=True)
            state_path.write_text(json.dumps(state_payload), encoding="utf-8")
            substituted_captures = root / "substituted-captures.json"
            substituted_captures.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "detection": "NativeRule.yaml",
                                "cdOnly": True,
                                "expectedMatchKeys": ["wrong-positive"],
                                "customDetection": {
                                    "alerts": [alert("wrong-positive")]
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.alert_parity.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.alert_parity._verify_qualification_scope",
                    return_value=scope,
                ),
                mock.patch(
                    "sentinel_xdr_migration.alert_parity._disable_all",
                    return_value=[{"detection": "NativeRule.yaml", "disabled": True, "errors": []}],
                ),
            ):
                report = complete_alert_parity(root, results_path=substituted_captures)
                self.assertEqual("failed", report["status"])
                self.assertFalse(report["comparisons"][0]["passed"])
                self.assertEqual([], report["comparisons"][0]["matchedPositiveControls"])
                self.assertEqual(
                    ["reviewed-positive"],
                    report["comparisons"][0]["missingPositiveControls"],
                )

                state_path.write_text(json.dumps(state_payload), encoding="utf-8")
                poll_report = poll_alert_parity_batch(root, results_path=substituted_captures)
                self.assertEqual("failed", poll_report["status"])
                self.assertFalse(poll_report["comparisons"][0]["passed"])
                self.assertEqual(
                    ["reviewed-positive"],
                    poll_report["comparisons"][0]["missingPositiveControls"],
                )


if __name__ == "__main__":
    unittest.main()
