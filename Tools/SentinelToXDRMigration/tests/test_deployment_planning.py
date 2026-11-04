from __future__ import annotations

import json
import hashlib
import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration import artifacts
from sentinel_xdr_migration.cli import main
from sentinel_xdr_migration import deployment_planning as planning

FIXTURE = Path(__file__).parent / "fixtures" / "deployment-planning"
INVENTORY_FIXTURE = Path(__file__).parent / "fixtures" / "deployment-planning-inventory"
TARGET = {
    "tenantId": "11111111-2222-4333-8444-555555555555",
    "subscriptionId": "22222222-3333-4444-8555-666666666666",
    "workspaceResourceId": (
        "/subscriptions/22222222-3333-4444-8555-666666666666/"
        "resourceGroups/rg-test/providers/Microsoft.OperationalInsights/"
        "workspaces/ws-test"
    ),
    "workspaceCustomerId": "33333333-4444-4555-8666-777777777777",
}


class DeploymentPlanningTests(unittest.TestCase):
    RULE_IDS = [
        "11111111-2222-3333-4444-555555555551",
        "11111111-2222-3333-4444-555555555552",
        "11111111-2222-3333-4444-555555555553",
    ]

    @staticmethod
    def _rule_record(rule_id: str, index: int) -> dict:
        return {
            "id": rule_id,
            "path": f"Analytic Rules/rule-{index}.yaml",
            "document": {
                "id": rule_id,
                "kind": "Scheduled",
                "name": f"Rule {index}",
                "query": "DeviceEvents",
                "severity": "Medium",
                "queryFrequency": "PT5M",
                "queryPeriod": "PT5M",
            },
        }

    @staticmethod
    def _candidate(rule: dict, *, multi_tactic: bool = False, review: bool = False, valid: bool = True) -> dict:
        source_document = rule["document"]
        source_yaml = yaml.safe_dump(source_document, sort_keys=True, allow_unicode=True).encode("utf-8")
        tactics = [
            {"tactic": "Exfiltration", "techniques": [{"technique": "T1041"}]},
        ]
        if multi_tactic:
            tactics.append(
                {"tactic": "Impact", "techniques": [{"technique": "T1498"}]}
            )
        query_text = "DeviceEvents"
        source_id = source_document["id"]
        candidate = {
            "schemaVersion": "1.0.0",
            "version": "3.1.1",
            "kind": "CustomDetection",
            "resourceType": "Microsoft.Security/detectionRules",
            "apiVersion": "2026-06-01-preview",
            "contentProvenance": {
                "requiredWorkloads": [{"workload": "mde", "dataTypes": ["DeviceEvents"]}],
                "requiredDataConnectors": [],
                "source": {
                    "platform": "Microsoft Sentinel",
                    "kind": "AnalyticsRule",
                    "id": source_id,
                    "path": rule["path"],
                    "querySha256": hashlib.sha256(
                        source_document["query"].encode("utf-8")
                    ).hexdigest(),
                    "schedule": {"frequency": "PT5M", "period": "PT5M"},
                },
                "conversion": {
                    "tool": "sentinel-to-xdr-migration",
                    "version": "1.0.0",
                    "status": "converted",
                    "reviewRequired": review,
                    "reviewReasons": [],
                    "requiredWorkloads": [],
                    "warnings": [],
                },
            },
            "properties": {
                "id": f"xdr-{source_id}",
                "displayName": source_document["name"],
                "status": "disabled",
                "queryCondition": {"queryText": query_text if valid else ""},
                "schedule": {"frequency": "PT5M"},
                "detectionAction": {
                    "alertTemplate": {
                        "entityMappings": {"hosts": {}},
                        "tactics": tactics,
                    }
                },
            },
        }
        candidate["contentProvenance"]["conversion"]["reviewScope"] = {
            "sourceDocumentSha256": hashlib.sha256(source_yaml).hexdigest(),
            "targetQuerySha256": hashlib.sha256(query_text.encode("utf-8")).hexdigest(),
        }
        return candidate

    def _artifact(self, root: Path, name: str) -> Path:
        if name == "workflow-state.json":
            return FIXTURE / name
        return root / "Logs" / "sentinel-xdr-migration" / name

    def _build(
        self,
        target=TARGET,
        consent_record=None,
        *,
        source_sha256=None,
        package_content_sha256="f" * 64,
        source_inventory=None,
    ):
        original = planning.existing_artifact_path
        original_source_inventory = planning._source_inventory

        def artifact(root, name):
            if name == planning.CONSENT_FILE_NAME and consent_record is not None:
                return Path("consent-record.json")
            return self._artifact(Path(root), name)

        def read_path(path, *args, **kwargs):
            if Path(path) == Path("consent-record.json"):
                return json.dumps(consent_record)
            with Path(path).open(*args, **kwargs) as stream:
                return stream.read()

        package = {
            "status": "provisional",
            "version": None,
            "packageInputSha256": None,
            "packageArtifactHashes": {},
            "packageContentSha256": package_content_sha256,
            "recordedPackageArtifactHashes": {},
            "deploymentParameters": {},
            "resourceInventory": [],
            "bicepExtensibilityImports": [],
            "whatIfSupport": "not-evaluated",
        }
        with (
            mock.patch.object(planning, "existing_artifact_path", side_effect=artifact),
            mock.patch.object(
                planning,
                "_read_existing_dcr_preflight",
                return_value={"status": "not-recorded", "contracts": []},
            ),
            mock.patch.object(planning, "package_input_identity", side_effect=ValueError("package not built")),
            mock.patch.object(planning, "_current_package", return_value=package),
            mock.patch.object(
                planning,
                "_source_inventory",
                side_effect=lambda root: (
                    {
                        **(
                            source_inventory
                            if source_inventory is not None
                            else original_source_inventory(root)
                        ),
                        **(
                            {"sourceInventorySha256": source_sha256}
                            if source_sha256 is not None
                            else {}
                        ),
                    }
                ),
            ),
            mock.patch.object(
                planning.Path,
                "read_text",
                autospec=True,
                side_effect=read_path,
            ) if consent_record is not None else mock.patch.object(planning, "_consent_state", return_value={"status": "not-recorded", "approvedComponents": []}),
        ):
            return planning.build_deployment_plan(FIXTURE, target=target)

    def test_recursive_inventory_counts_duplicate_rule_files_once_by_identity(self) -> None:
        plan = self._build()

        self.assertEqual(plan["sourceInventory"]["analyticRules"], 1)
        self.assertEqual(plan["sourceInventory"]["analyticRuleFiles"], 2)
        self.assertEqual(plan["detectionScope"]["sourceAnalyticRuleCount"], 1)
        self.assertEqual(plan["detectionScope"]["duplicateSourceRuleIds"], [
            "11111111-2222-3333-4444-555555555555"
        ])
        self.assertEqual(plan["detectionScope"]["eligibleMaximumAdditionalCustomDetections"], 0)

    def test_graph_payload_projection_controls_eligibility_not_stale_converter_flag(self) -> None:
        rules = {
            rule_id.casefold(): self._rule_record(rule_id, index)
            for index, rule_id in enumerate(self.RULE_IDS)
        }

        def build_candidate(source, _root, _config):
            index = int(Path(source).stem.rsplit("-", 1)[1])
            return self._candidate(rules[self.RULE_IDS[index].casefold()], multi_tactic=index < 2)

        with mock.patch.object(planning, "build_xdr_document", side_effect=build_candidate):
            eligible, ineligible, projections = planning._eligible_rule_ids(
                FIXTURE, rules, set(), set()
            )

        self.assertEqual(eligible, self.RULE_IDS)
        self.assertEqual(ineligible, [])
        self.assertEqual(projections[self.RULE_IDS[0]]["projectedTactics"], ["Exfiltration"])
        self.assertEqual(projections[self.RULE_IDS[0]]["omittedTactics"], ["Impact"])
        self.assertEqual(
            projections[self.RULE_IDS[0]]["omittedTechniques"],
            [{"tactic": "Impact", "techniques": ["T1498"]}],
        )
        self.assertEqual(projections[self.RULE_IDS[0]]["classificationParity"], "not-established")

        candidates = {
            self.RULE_IDS[0].casefold(): self._candidate(
                rules[self.RULE_IDS[0].casefold()], multi_tactic=True, review=True
            ),
            self.RULE_IDS[1].casefold(): self._candidate(
                rules[self.RULE_IDS[1].casefold()], valid=False
            ),
            self.RULE_IDS[2].casefold(): self._candidate(rules[self.RULE_IDS[2].casefold()]),
        }
        with mock.patch.object(
            planning,
            "build_xdr_document",
            side_effect=lambda source, _root, _config: candidates[
                self.RULE_IDS[int(Path(source).stem.rsplit("-", 1)[1])].casefold()
            ],
        ):
            eligible, ineligible, _ = planning._eligible_rule_ids(
                FIXTURE, rules, set(), {self.RULE_IDS[2].casefold()}
            )
        self.assertEqual(eligible, [])
        self.assertEqual(set(ineligible), set(self.RULE_IDS))

    def test_source_analytic_rule_eligibility_is_independent_from_graph_projection(self) -> None:
        rules = {
            rule_id.casefold(): self._rule_record(rule_id, index)
            for index, rule_id in enumerate(self.RULE_IDS)
        }
        eligible, ineligible = planning._eligible_analytic_rule_ids(rules, set())

        self.assertEqual(eligible, self.RULE_IDS)
        self.assertEqual(ineligible, [])

    def test_plan_distinguishes_total_reviewed_custom_detections_from_additional_cap(self) -> None:
        rules = {
            rule_id.casefold(): self._rule_record(rule_id, index)
            for index, rule_id in enumerate(self.RULE_IDS)
        }
        projections = {
            rule_id: {
                "status": "projected",
                "projectedTactics": ["Exfiltration"],
                "omittedTactics": ["Impact"],
                "projectedTechniques": ["T1041"],
                "omittedTechniques": ["T1498"],
                "classificationParity": "not-established",
            }
            for rule_id in self.RULE_IDS[:2]
        }
        with (
            mock.patch.object(planning, "_source_records", return_value=(rules, set())),
            mock.patch.object(
                planning,
                "_reviewed_current_drafts",
                return_value=(self.RULE_IDS, [], projections),
            ),
            mock.patch.object(
                planning,
                "_eligible_rule_ids",
                return_value=(self.RULE_IDS[2:], self.RULE_IDS[:2], projections),
            ),
            mock.patch.object(
                planning,
                "_eligible_analytic_rule_ids",
                return_value=(self.RULE_IDS, []),
            ),
        ):
            plan = self._build(
                source_inventory={
                    "counts": {
                        "analyticRules": 3,
                        "playbooks": 3,
                        "configuredPlaybookTemplateCount": 4,
                        "uniquePlaybookWorkflowCount": 3,
                        "workbooks": 1,
                        "dataConnectors": 1,
                    },
                    "fileCounts": {"playbooks": 6, "dataConnectors": 2},
                    "manifestContentInventory": {
                        "status": "ready",
                        "manifestReferenceCounts": {"playbooks": 4, "dataConnectors": 1},
                        "configuredPlaybookTemplateCount": 4,
                        "uniquePlaybookWorkflowCount": 3,
                    },
                    "analyticRuleCount": 3,
                    "sourceInventorySha256": "a" * 64,
                }
            )

        scope = plan["detectionScope"]
        self.assertEqual(scope["currentReviewedDraftCount"], 3)
        self.assertEqual(scope["eligibleMaximumAdditionalCustomDetections"], 0)
        self.assertEqual(scope["eligibleMaximumTotalCustomDetections"], 3)
        self.assertEqual(scope["eligibleMaximumTotalDisabledRulePairs"], 3)
        self.assertEqual(plan["components"]["xdrCustomDetections"]["maximumCount"], 3)
        self.assertEqual(plan["components"]["xdrCustomDetections"]["maximumAdditionalCount"], 0)
        self.assertEqual(plan["components"]["sentinelAlertRules"]["maximumCount"], 3)
        self.assertEqual(plan["sourceInventory"]["playbooks"], 3)
        self.assertEqual(plan["sourceInventory"]["configuredPlaybookTemplateCount"], 4)
        self.assertEqual(plan["sourceInventory"]["uniquePlaybookWorkflowCount"], 3)
        self.assertEqual(plan["sourceFileCounts"]["playbooks"], 6)
        self.assertEqual(
            plan["manifestContentInventory"]["manifestReferenceCounts"]["playbooks"],
            4,
        )
        self.assertEqual(scope["ineligibleRuleIds"], [])
        self.assertEqual(scope["ineligibleNewConversionCandidateRuleIds"], self.RULE_IDS[:2])
        self.assertEqual(
            scope["currentReviewedDraftsNotEligibleAsNewConversionCandidates"],
            self.RULE_IDS[:2],
        )
        self.assertEqual(scope["eligiblePairRuleIds"], self.RULE_IDS)
        parity = plan["components"]["controlledAlertParity"]
        self.assertEqual(parity["status"], "provisional")
        self.assertEqual(parity["eligiblePairRuleIds"], self.RULE_IDS)
        self.assertEqual(parity["maximumEnableWriteRequests"], 6)
        self.assertEqual(parity["maximumRestoreWriteRequests"], 6)
        self.assertEqual(parity["maximumWriteRequestsForOneBoundedRun"], 12)
        self.assertEqual(scope["sourceAnalyticRuleCount"], 3)

    def test_plan_keeps_sentinel_rule_scope_when_graph_payload_is_ineligible(self) -> None:
        rules = {
            rule_id.casefold(): self._rule_record(rule_id, index)
            for index, rule_id in enumerate(self.RULE_IDS)
        }
        with (
            mock.patch.object(planning, "_source_records", return_value=(rules, set())),
            mock.patch.object(planning, "_reviewed_current_drafts", return_value=([], [], {})),
            mock.patch.object(
                planning,
                "_eligible_rule_ids",
                return_value=([], self.RULE_IDS, {}),
            ),
            mock.patch.object(
                planning,
                "_eligible_analytic_rule_ids",
                return_value=(self.RULE_IDS, []),
            ),
        ):
            plan = self._build(
                source_inventory={
                    "counts": {"analyticRules": 3},
                    "manifestContentInventory": {"status": "ready"},
                    "analyticRuleCount": 3,
                    "sourceInventorySha256": "b" * 64,
                }
            )

        self.assertEqual(plan["components"]["sentinelAlertRules"]["maximumCount"], 3)
        self.assertEqual(plan["components"]["xdrCustomDetections"]["maximumCount"], 0)
        self.assertEqual(plan["detectionScope"]["eligibleMaximumTotalDisabledRulePairs"], 0)

    def test_parity_and_cleanup_scope_gaps_are_explicit_and_not_consentable(self) -> None:
        plan = self._build()

        parity = plan["components"]["controlledAlertParity"]
        self.assertFalse(parity["advanceConsentSupported"])
        self.assertEqual(parity["status"], "unavailable")
        self.assertEqual(parity["timeWindow"]["status"], "not-recorded")
        self.assertEqual(parity["maximumRulePairCount"], 0)
        cleanup = plan["components"]["ownedResourceCleanup"]
        self.assertEqual(cleanup["status"], "unsupported")
        self.assertFalse(cleanup["advanceConsentSupported"])
        self.assertEqual(cleanup["maximumDeleteCount"], 0)
        self.assertEqual(cleanup["resources"], [])
        self.assertNotIn("controlledAlertParity", planning.COMPONENTS)
        self.assertNotIn("ownedResourceCleanup", planning.COMPONENTS)
        for unsupported_component in ("controlledAlertParity", "ownedResourceCleanup"):
            with (
                mock.patch.object(planning, "build_deployment_plan", return_value=plan),
                self.assertRaisesRegex(ValueError, "unsupported planning consent component"),
            ):
                planning.record_planning_consent(
                    FIXTURE,
                    expected_plan_sha256=plan["planSha256"],
                    actor="reviewer",
                    approved_components=[unsupported_component],
                )

    def test_dotenv_is_excluded_before_reading_content(self) -> None:
        with (
            mock.patch.object(Path, "rglob", return_value=[FIXTURE / ".env"]),
            mock.patch.object(Path, "read_bytes", side_effect=AssertionError(".env must not be read")),
        ):
            self.assertEqual(planning._file_inventory(FIXTURE), [])

    def test_authoring_profile_has_no_deployment_plan_or_target_lookup(self) -> None:
        state = json.loads((FIXTURE / "workflow-state.json").read_text())
        state["context"]["workflowProfile"] = "authoring"
        with (
            mock.patch.object(
                planning,
                "existing_artifact_path",
                return_value=Path("workflow-state.json"),
            ),
            mock.patch.object(
                Path,
                "read_text",
                autospec=True,
                side_effect=lambda path, *args, **kwargs: json.dumps(state),
            ),
            mock.patch.object(Path, "is_file", return_value=True),
            mock.patch.object(planning, "require_locked_target") as locked_target,
        ):
            plan = planning.build_deployment_plan(FIXTURE)

        self.assertEqual(plan["status"], "not-applicable")
        self.assertEqual(plan["selectedProfile"], "authoring")
        locked_target.assert_not_called()

    def test_resource_scan_handles_nested_templates_language_v2_and_extension_scope(self) -> None:
        inventory, imports = planning._scan_package_resources(
            {
                "languageVersion": "2.0",
                "imports": [{"provider": "Contoso.Extensions", "version": "1.0.0"}],
                "resources": {
                    "extension": {
                        "type": "Contoso.Extensions/widgets@2026-01-01",
                        "scope": "[resourceGroup().id]",
                    },
                    "nestedDeployment": {
                        "type": "Microsoft.Resources/deployments",
                        "apiVersion": "2025-04-01",
                        "properties": {
                            "template": {
                                "resources": [
                                    {
                                        "type": "Microsoft.Insights/dataCollectionRules",
                                        "apiVersion": "2023-03-11",
                                    }
                                ]
                            }
                        },
                    },
                },
            }
        )

        by_type = {item["type"]: item for item in inventory}
        self.assertEqual(by_type["Contoso.Extensions/widgets"]["typeAtVersion"], "Contoso.Extensions/widgets@2026-01-01")
        self.assertTrue(by_type["Contoso.Extensions/widgets"]["extensionResource"])
        self.assertEqual(
            by_type["Contoso.Extensions/widgets"]["scopeModel"],
            "generic-arm-extension-resource-scope",
        )
        self.assertEqual(by_type["Microsoft.Resources/deployments"]["count"], 1)
        self.assertIn("Microsoft.Insights/dataCollectionRules", by_type)
        self.assertEqual(imports, [{"provider": "Contoso.Extensions", "version": "1.0.0"}])

    def test_package_identity_uses_selected_current_attempt_not_historical_report(self) -> None:
        input_sha = "9" * 64
        artifact_contents = {
            "mainTemplate": json.dumps(
                {
                    "imports": [{"provider": "Contoso.Extensions", "version": "1.0.0"}],
                    "resources": [
                        {
                            "type": "Contoso.Extensions/widgets@2026-01-01",
                            "scope": "[resourceGroup().id]",
                        },
                        {
                            "type": "Microsoft.Insights/dataCollectionRules",
                            "apiVersion": "2023-03-11",
                        },
                    ],
                }
            ).encode(),
            "createUiDefinition": b"{}",
            "testParameters": b"{}",
            "zip": b"package",
        }
        artifact_hashes = {
            name: hashlib.sha256(content).hexdigest()
            for name, content in artifact_contents.items()
        }
        report = {
            "packager": "V3.1",
            "packageAttemptId": "current-attempt",
            "packageArtifactsSha256": "a" * 64,
            "packageInputs": {"after": {"sha256": input_sha}},
            "packageArtifactHashes": artifact_hashes,
            "version": "3.1.2",
            "deploymentParameters": {"DeployAnalyticsRule": True, "DeployCustomDetection": False},
            **{name: name for name in artifact_contents},
        }
        report_bytes = json.dumps(report).encode()
        report_hash = hashlib.sha256(report_bytes).hexdigest()

        class MemoryArtifact:
            def __init__(self, name: str, content: bytes):
                self.name = name
                self.content = content

            def read_bytes(self):
                return self.content

            def read_text(self, encoding=None):
                return self.content.decode(encoding or "utf-8")

            def is_file(self):
                return True

            def resolve(self):
                return self

        report_artifact = MemoryArtifact("current-report", report_bytes)
        resolved_artifacts = {
            "current-report": report_artifact,
            "historical-report": MemoryArtifact("historical-report", b"{}"),
            **{
                name: MemoryArtifact(name, content)
                for name, content in artifact_contents.items()
            },
        }
        selected_state = {
            "packaging": {
                "lastSuccessful": {
                    "packageSucceeded": True,
                    "attemptId": "current-attempt",
                    "packageInputSha256": input_sha,
                    "packageReport": "current-report",
                    "packageReportSha256": report_hash,
                    "packageArtifactsSha256": "a" * 64,
                    "version": "3.1.2",
                }
            },
            "stages": {
                "packaging": {
                    "status": "passed",
                    "artifacts": {
                        "packageAttemptId": "current-attempt",
                        "packageReport": "current-report",
                        "packageReportSha256": report_hash,
                    },
                }
            },
        }
        with (
            mock.patch.object(planning, "package_input_identity", return_value={"sha256": input_sha}),
            mock.patch.object(
                planning,
                "resolve_artifact_reference",
                side_effect=lambda _root, value: resolved_artifacts[value],
            ),
        ):
            current = planning._current_package(FIXTURE, selected_state)

        self.assertEqual(current["status"], "current")
        self.assertEqual(current["version"], "3.1.2")
        self.assertEqual(current["recordedPackageArtifactHashes"], artifact_hashes)
        resources_by_type = {item["type"]: item for item in current["resourceInventory"]}
        self.assertIn("Microsoft.Insights/dataCollectionRules", resources_by_type)
        self.assertEqual(
            resources_by_type["Contoso.Extensions/widgets"]["scopeModel"],
            "generic-arm-extension-resource-scope",
        )
        self.assertEqual(current["whatIfSupport"], "unsupported-bicep-extensibility-imports")

        historical_state = json.loads(json.dumps(selected_state))
        historical_state["stages"]["packaging"]["artifacts"]["packageReport"] = "historical-report"
        historical_state["stages"]["packaging"]["artifacts"]["packageAttemptId"] = "old-attempt"
        historical = planning._current_package(FIXTURE, historical_state)
        self.assertEqual(historical["status"], "stale")
        self.assertEqual(historical["resourceInventory"], [])

    def test_missing_or_changed_plan_consent_never_becomes_approved(self) -> None:
        plan = self._build()
        changed_target = {**TARGET, "workspaceCustomerId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}
        changed = self._build(target=changed_target)
        changed_package = self._build(package_content_sha256="0" * 64)
        stale_consent = self._build(
            source_sha256="0" * 64,
            consent_record={
                "schemaVersion": planning.PLAN_SCHEMA_VERSION,
                "status": "approved",
                "planSha256": plan["planSha256"],
            },
        )

        self.assertNotEqual(plan["planSha256"], changed["planSha256"])
        self.assertNotEqual(plan["planSha256"], changed_package["planSha256"])
        self.assertEqual(changed["planningConsent"]["status"], "not-recorded")
        self.assertEqual(changed["exactScopeWriteApproval"], "not-recorded")
        self.assertNotEqual(plan["planSha256"], stale_consent["planSha256"])
        self.assertEqual(stale_consent["planningConsent"]["status"], "stale")
        self.assertEqual(stale_consent["packageIdentity"]["status"], "provisional")
        self.assertEqual(stale_consent["packageAcceptancePlan"]["status"], "provisional")

    def test_preflight_consent_is_scoped_local_artifact_not_write_authority(self) -> None:
        plan = {
            "planSha256": "a" * 64,
            "components": {
                "fallbackDcr": {
                    "status": "conditional",
                    "compatibleExistingDcrProven": False,
                    "resourceTypes": ["Microsoft.Insights/dataCollectionRules"],
                }
            },
            "target": TARGET,
            "packageResourceInventory": [],
        }
        with (
            mock.patch.object(planning, "build_deployment_plan", return_value=plan),
            mock.patch.object(planning, "artifact_path", return_value=Path("consent.json")),
            mock.patch.object(planning, "write_json_artifact") as write_json,
        ):
            result = planning.record_planning_consent(
                FIXTURE,
                expected_plan_sha256="a" * 64,
                actor="reviewer",
                approved_components=["fallbackDcr"],
            )

        record = write_json.call_args.args[2]
        self.assertEqual(result["status"], "approved")
        self.assertEqual(record["approvedComponents"], ["fallbackDcr"])
        self.assertFalse(record["environmentWritesAuthorized"])
        self.assertEqual(record["scope"]["target"], TARGET)
        self.assertEqual(record["scope"]["resourceTypes"], ["Microsoft.Insights/dataCollectionRules"])

    def test_persisting_plan_does_not_change_workflow_state_or_stage_status(self) -> None:
        original_state = (FIXTURE / "workflow-state.json").read_bytes()
        plan = {"planSha256": "f" * 64, "status": "provisional"}
        with (
            mock.patch.object(planning, "build_deployment_plan", return_value=plan),
            mock.patch.object(planning, "artifact_path", return_value=Path("scope-plan.json")),
            mock.patch.object(planning, "write_json_artifact") as write_json,
        ):
            persisted = planning.persist_deployment_plan(FIXTURE)

        self.assertEqual(persisted["planSha256"], "f" * 64)
        self.assertEqual(write_json.call_args.args[1], Path("scope-plan.json"))
        self.assertEqual((FIXTURE / "workflow-state.json").read_bytes(), original_state)

    def test_plan_cli_uses_explicit_run_without_authentication(self) -> None:
        output = io.StringIO()

        def persist(_solution):
            return {"selectedRunId": artifacts.requested_run_id(FIXTURE)}

        with (
            mock.patch("sentinel_xdr_migration.cli.persist_deployment_plan", side_effect=persist),
            redirect_stdout(output),
        ):
            exit_code = main(
                [
                    "plan-deployment",
                    "--solution",
                    str(FIXTURE),
                    "--run-id",
                    "run-2026-10-11",
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(output.getvalue())["selectedRunId"], "run-2026-10-11")

    def test_cli_help_and_workflow_module_imports_succeed_in_clean_processes(self) -> None:
        package_dir = Path(__file__).parents[1]
        commands = [
            ["--help"],
            ["doctor", "--help"],
            ["plan-deployment", "--help"],
            ["solution-report", "--help"],
        ]
        for arguments in commands:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, "-m", "sentinel_xdr_migration.cli", *arguments],
                    cwd=package_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

        for module in (
            "sentinel_xdr_migration.cli",
            "sentinel_xdr_migration.deployment",
            "sentinel_xdr_migration.graph_readiness",
            "sentinel_xdr_migration.deployment_planning",
            "sentinel_xdr_migration.solution_report",
        ):
            with self.subTest(module=module):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        f"import importlib; importlib.import_module({module!r})",
                    ],
                    cwd=package_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_stale_plan_hash_and_partial_rule_pair_consent_are_rejected(self) -> None:
        pair_plan = {
            "planSha256": "b" * 64,
            "components": {
                "sentinelAlertRules": {"maximumCount": 2},
                "xdrCustomDetections": {"maximumCount": 2},
            },
            "detectionScope": {"eligibleMaximumAdditionalCustomDetections": 2},
            "target": TARGET,
            "packageResourceInventory": [],
        }
        with mock.patch.object(planning, "build_deployment_plan", return_value=pair_plan):
            with self.assertRaisesRegex(ValueError, "current plan hash"):
                planning.record_planning_consent(
                    FIXTURE,
                    expected_plan_sha256="c" * 64,
                    actor="reviewer",
                    approved_components=["sentinelAlertRules", "xdrCustomDetections"],
                    max_additional_custom_detections=2,
                )
            with self.assertRaisesRegex(ValueError, "both sentinelAlertRules"):
                planning.record_planning_consent(
                    FIXTURE,
                    expected_plan_sha256="b" * 64,
                    actor="reviewer",
                    approved_components=["xdrCustomDetections"],
                    max_additional_custom_detections=1,
                )

    def test_changed_consent_cap_is_not_reused_without_a_new_review(self) -> None:
        pair_components = {
            "sentinelAlertRules": {
                "resourceTypes": ["Microsoft.SecurityInsights/alertRules"],
                "maximumCount": 3,
            },
            "xdrCustomDetections": {
                "resourceTypes": ["Microsoft.Security/detectionRules"],
                "maximumCount": 3,
                "maximumAdditionalCount": 2,
            },
        }
        plan = {
            "planSha256": "e" * 64,
            "components": pair_components,
            "detectionScope": {"eligibleMaximumAdditionalCustomDetections": 2},
            "target": TARGET,
            "packageResourceInventory": [],
        }
        with (
            mock.patch.object(planning, "build_deployment_plan", return_value=plan),
            mock.patch.object(planning, "artifact_path", return_value=Path("consent.json")),
            mock.patch.object(planning, "write_json_artifact") as write_json,
        ):
            planning.record_planning_consent(
                FIXTURE,
                expected_plan_sha256="e" * 64,
                actor="reviewer",
                approved_components=["sentinelAlertRules", "xdrCustomDetections"],
                max_additional_custom_detections=1,
            )
        record = write_json.call_args.args[2]
        with (
            mock.patch.object(planning, "existing_artifact_path", return_value=Path("consent.json")),
            mock.patch.object(Path, "read_text", autospec=True, return_value=json.dumps(record)),
        ):
            accepted = planning._consent_state(
                FIXTURE,
                "e" * 64,
                components=pair_components,
                package={"status": "provisional", "resourceInventory": []},
                target=TARGET,
            )
        self.assertEqual(accepted["status"], "approved")

        record["maxAdditionalCustomDetections"] = 2
        with (
            mock.patch.object(planning, "existing_artifact_path", return_value=Path("consent.json")),
            mock.patch.object(Path, "read_text", autospec=True, return_value=json.dumps(record)),
        ):
            tampered = planning._consent_state(
                FIXTURE,
                "e" * 64,
                components=pair_components,
                package={"status": "provisional", "resourceInventory": []},
                target=TARGET,
            )
        self.assertEqual(tampered["status"], "unknown")
        self.assertEqual(tampered["approvedComponents"], [])

    def test_unknown_ingestion_plan_stays_provisional_and_dce_requires_explicit_selection(self) -> None:
        self.assertEqual(
            planning._mock_ingestion_plan(FIXTURE, {"stages": {"mockIngestion": {"artifacts": {}}}})["status"],
            "provisional",
        )
        plan = {
            "planSha256": "d" * 64,
            "components": {
                "fallbackDcr": {"status": "conditional", "compatibleExistingDcrProven": False},
                "fallbackDce": {"status": "conditional"},
            },
            "target": TARGET,
            "packageResourceInventory": [],
        }
        with mock.patch.object(planning, "build_deployment_plan", return_value=plan):
            with self.assertRaisesRegex(ValueError, "explicit --dce-selected"):
                planning.record_planning_consent(
                    FIXTURE,
                    expected_plan_sha256="d" * 64,
                    actor="reviewer",
                    approved_components=["fallbackDcr", "fallbackDce"],
                )

    def test_custom_table_creation_requires_proven_absence_and_native_tables_never_get_lookalikes(self) -> None:
        contract_text = """
destination:
  kind: custom
  columns:
    - name: TimeGenerated
      type: datetime
    - name: EventType
      type: string
"""
        contract = {
            "table": "Example_CL",
            "contractPath": "contracts/example.yaml",
            "schemaFingerprint": "a" * 64,
            "transformFingerprint": "b" * 64,
            "contractFingerprint": "c" * 64,
            "resources": {
                "destinationTable": {
                    "id": "/subscriptions/example/workspaces/ws/tables/Example_CL",
                    "state": "missing",
                }
            },
            "tableSchemaCompatibility": {"status": "unknown"},
        }
        with (
            mock.patch.object(planning, "repository_root", return_value=FIXTURE),
            mock.patch.object(Path, "read_text", autospec=True, side_effect=lambda path, *args, **kwargs: (
                contract_text if path.name == "example.yaml" else Path.open(path, *args, **kwargs).read()
            )),
        ):
            components = planning._components(
                FIXTURE,
                source_ids=[],
                sentinel_rule_ids=[],
                pair_rule_ids=[],
                additional_rule_ids=[],
                graph_projections={},
                package={"status": "provisional", "target": {"subscriptionId": "sub", "resourceGroup": "rg"}},
                dcr={"contracts": [contract]},
                ingestion={"status": "provisional"},
            )
        table_scope = components["customTableCreate"]
        self.assertEqual(table_scope["status"], "conditional")
        self.assertEqual(table_scope["tables"][0]["columnCount"], 2)
        self.assertEqual(table_scope["tables"][0]["schemaFingerprint"], "a" * 64)
        self.assertFalse(table_scope["nativeCommonSecurityLogLookalikeAllowed"])

        standard_text = "destination:\n  kind: standard\n  columns: []\n"
        standard_contract = {
            **contract,
            "table": "CommonSecurityLog",
            "resources": {
                "destinationTable": {
                    "id": "/subscriptions/example/workspaces/ws/tables/CommonSecurityLog",
                    "state": "present",
                }
            },
            "tableSchemaCompatibility": {"status": "compatible"},
        }
        with (
            mock.patch.object(planning, "repository_root", return_value=FIXTURE),
            mock.patch.object(Path, "read_text", autospec=True, side_effect=lambda path, *args, **kwargs: (
                standard_text if path.name == "example.yaml" else Path.open(path, *args, **kwargs).read()
            )),
        ):
            native_components = planning._components(
                FIXTURE,
                source_ids=[],
                sentinel_rule_ids=[],
                pair_rule_ids=[],
                additional_rule_ids=[],
                graph_projections={},
                package={"status": "provisional", "target": {"subscriptionId": "sub", "resourceGroup": "rg"}},
                dcr={"contracts": [standard_contract]},
                ingestion={"status": "provisional"},
            )
        self.assertEqual(native_components["customTableCreate"]["status"], "not-needed")
        self.assertEqual(native_components["customTableCreate"]["tables"], [])

    def test_manifest_inventory_counts_unique_workflows_and_separates_unlisted_files(self) -> None:
        inventory = planning._manifest_content_inventory(INVENTORY_FIXTURE)

        self.assertEqual(inventory["status"], "ready")
        self.assertEqual(inventory["manifestReferenceCounts"]["playbooks"], 4)
        self.assertEqual(inventory["configuredPlaybookTemplateCount"], 4)
        self.assertEqual(inventory["uniquePlaybookWorkflowCount"], 3)
        self.assertEqual(inventory["contentCounts"]["playbooks"], 3)
        self.assertEqual(inventory["folderFileCounts"]["playbooks"], 5)
        self.assertEqual(len(inventory["unlistedFiles"]["playbooks"]), 1)
        self.assertEqual(inventory["manifestReferenceCounts"]["dataConnectors"], 1)
        self.assertEqual(inventory["contentCounts"]["dataConnectors"], 1)
        self.assertEqual(inventory["folderFileCounts"]["dataConnectors"], 2)
        self.assertEqual(len(inventory["unlistedFiles"]["dataConnectors"]), 1)


if __name__ == "__main__":
    unittest.main()
