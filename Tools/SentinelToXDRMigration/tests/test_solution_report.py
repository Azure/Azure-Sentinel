from __future__ import annotations

import ast
import hashlib
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from sentinel_xdr_migration.converter import convert_solution
from sentinel_xdr_migration.dependencies import dependency_identity
from sentinel_xdr_migration.artifacts import existing_artifact_path, report_directory
from sentinel_xdr_migration import deployment_planning
from sentinel_xdr_migration.report_dashboard import _deployment_planning_html
from sentinel_xdr_migration.solution_report import (
    _partial_selection_parity_matches,
    _package_resource_inventory,
    _planning_summary,
    _preflight_projection,
    _selected_packaging_report,
    build_solution_report,
)
from test_converter import RULE


class SolutionReportTests(unittest.TestCase):
    def test_partial_qualification_requires_exact_current_parity_scope(self) -> None:
        plan = {
            "planSha256": "plan-current",
            "selection": {
                "xdrDetections": [
                    "XDR Detections/A.yaml",
                    "XDR Detections/B.yaml",
                ]
            },
            "xdrDetections": [
                {"included": True, "sourceId": "source-a"},
                {"included": True, "sourceId": "source-b"},
            ],
        }
        applied = {"planSha256": "plan-current"}
        parity = {
            "status": "passed",
            "qualificationScopeVerified": True,
            "selectionPlanSha256": "plan-current",
            "testedDetectionPaths": ["A.yaml", "B.yaml"],
            "testedSourceIds": ["source-a", "source-b"],
            "qualificationScope": {"selectionComplete": True},
        }
        self.assertTrue(
            _partial_selection_parity_matches(
                plan, parity, applied, stage_passed=True
            )[0]
        )
        self.assertFalse(
            _partial_selection_parity_matches(
                plan, parity, applied, stage_passed=False
            )[0]
        )

        narrower = dict(parity, testedDetectionPaths=["A.yaml"], testedSourceIds=["source-a"])
        self.assertFalse(
            _partial_selection_parity_matches(
                plan, narrower, applied, stage_passed=True
            )[0]
        )
        stale = dict(parity, selectionPlanSha256="old-plan")
        self.assertFalse(
            _partial_selection_parity_matches(
                plan, stale, applied, stage_passed=True
            )[0]
        )
        incomplete = dict(
            parity,
            qualificationScope={"selectionComplete": False},
        )
        self.assertFalse(
            _partial_selection_parity_matches(
                plan, incomplete, applied, stage_passed=True
            )[0]
        )

    def test_runtime_evidence_unavailable_does_not_hide_structural_errors(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Example"
            analytic = root / "Analytic Rules"
            analytic.mkdir(parents=True)
            (analytic / "Rule.yaml").write_text(RULE, encoding="utf-8")
            convert_solution(root)
            target = root / "XDR Detections" / "Rule.yaml"
            target.write_text(
                yaml.safe_dump({"kind": "InvalidCustomDetection", "properties": {}}),
                encoding="utf-8",
            )

            with patch(
                "sentinel_xdr_migration.runtime.current_runtime_evidence",
                side_effect=ValueError("invalid current XDR runtime target"),
            ):
                report = build_solution_report(root)

            self.assertTrue(any(
                error["stage"] == "structural-validation"
                for error in report["rules"][0]["errors"]
            ))
            self.assertEqual(
                "invalid current XDR runtime target",
                report["runtimeAssessment"]["runtimeUnavailable"],
            )
            self.assertEqual("unavailable", report["runtimeAssessment"]["sourceStatus"])

    def test_recorded_planning_consent_is_projected_without_write_authority(self) -> None:
        digest = "a" * 64
        template_hash = "1" * 64
        artifact_hashes = {
            "mainTemplate": template_hash,
            "createUiDefinition": "2" * 64,
            "testParameters": "3" * 64,
            "zip": "4" * 64,
        }
        target = {
            "tenantId": "tenant",
            "subscriptionId": "subscription",
            "resourceGroup": "resource-group",
            "workspaceResourceId": "/subscriptions/example/workspaces/lab",
            "workspaceCustomerId": "workspace-customer",
            "solution": "Example",
            "version": "3.1.1",
        }
        resource_inventory = [{"type": "Microsoft.Resources/deployments"}]
        resource_type = "Microsoft.Security/detectionRules@2026-06-01-preview"
        package_resource_type = "Microsoft.Resources/deployments"
        flags = {
            "DeployAnalyticsRule": True,
            "DeployPlaybook": True,
            "DeployWorkbook": True,
            "DeployDataConnector": True,
            "DeployCustomDetection": True,
        }
        plan = {
            "schemaVersion": "1.0.0",
            "status": "provisional",
            "planSha256": "c" * 64,
            "target": target,
            "packageResourceInventory": resource_inventory,
            "components": {
                "sentinelAlertRules": {
                    "maximumCount": 1,
                    "resourceTypes": [resource_type],
                },
                "xdrCustomDetections": {
                    "maximumCount": 1,
                    "maximumAdditionalCount": 0,
                    "resourceTypes": [resource_type],
                },
                "fullPackageAcceptance": {
                    "status": "available",
                    "availableFlags": flags,
                    "resourceTypes": [package_resource_type],
                },
            },
            "planningConsent": {"status": "not-recorded", "approvedComponents": []},
            "packageAcceptancePlan": {
                "status": "proposed",
                "approvalStatus": "not-approved",
                "packageIdentity": {"status": "current", "version": "3.1.1"},
            },
        }
        recorded: dict[str, dict] = {}

        def capture_record(_root, _path, document):
            recorded["consent"] = document

        with (
            patch.object(deployment_planning, "build_deployment_plan", return_value=plan),
            patch.object(
                deployment_planning,
                "artifact_path",
                return_value=Path("deployment-planning-consent.json"),
            ),
            patch.object(deployment_planning, "write_json_artifact", side_effect=capture_record),
        ):
            result = deployment_planning.record_planning_consent(
                Path("/selected-run"),
                expected_plan_sha256=plan["planSha256"],
                actor="reviewer",
                approved_components=[
                    "fullPackageAcceptance",
                    "sentinelAlertRules",
                    "xdrCustomDetections",
                ],
                max_additional_custom_detections=0,
                package_flags=flags,
            )
        self.assertEqual("approved", result["status"])
        self.assertFalse(result["environmentWritesAuthorized"])
        consent_record = recorded["consent"]

        package = {
            "packageInputs": {"after": {"sha256": digest}},
            "packageArtifactHashes": artifact_hashes,
            "packageArtifactsSha256": "d" * 64,
            "packageReport": "Logs/run/packaging.v3_1.attempt.json",
            "version": "3.1.1",
            "deploymentParameters": {},
        }
        workflow = {
            "profile": "qualification",
            "profileSelectionConfirmed": True,
            "packageFreshness": {
                "status": "current",
                "currentPackageInputSha256": digest,
            },
        }
        persisted_consent_path = Path("deployment-planning-consent.json")
        original_read_text = Path.read_text

        def read_consent(path, *args, **kwargs):
            if path == persisted_consent_path:
                return json.dumps(consent_record)
            return original_read_text(path, *args, **kwargs)

        with (
            patch(
                "sentinel_xdr_migration.solution_report._read_local_package_template",
                return_value=({"resources": []}, template_hash),
            ),
            patch(
                "sentinel_xdr_migration.solution_report._deployment_planning_input",
                return_value=plan,
            ),
            patch.object(
                deployment_planning,
                "existing_artifact_path",
                return_value=persisted_consent_path,
            ),
            patch.object(Path, "read_text", autospec=True, side_effect=read_consent),
        ):
            validated = deployment_planning._consent_state(
                Path("/selected-run"),
                plan["planSha256"],
                components=plan["components"],
                package={"status": "current", "resourceInventory": resource_inventory},
                target=target,
            )
            self.assertEqual("approved", validated["status"])
            projected = _planning_summary(Path("/selected-run"), package, workflow, {})

        self.assertEqual("approved", projected["deploymentPlan"]["planningConsent"]["status"])
        self.assertEqual("both", projected["deploymentPlan"]["executionMode"])
        self.assertEqual(
            ["fullPackageAcceptance", "sentinelAlertRules", "xdrCustomDetections"],
            projected["deploymentPlan"]["planningConsent"]["componentKeys"],
        )
        self.assertEqual(
            "approved",
            projected["deploymentPlan"]["packageAcceptancePlan"]["approvalStatus"],
        )
        self.assertEqual(
            flags,
            projected["deploymentPlan"]["packageAcceptancePlan"]["selectedFlags"],
        )
        self.assertEqual("not-recorded", projected["deploymentPlan"]["exactScopeWriteApproval"])
        self.assertFalse(consent_record["environmentWritesAuthorized"])

    def test_selected_package_report_is_bound_to_current_workflow_attempt(self) -> None:
        report_bytes = b"current package report"
        report_hash = hashlib.sha256(report_bytes).hexdigest()
        package_input_hash = "a" * 64
        artifact_hashes = {
            name: (value * 64)[:64]
            for name, value in (
                ("mainTemplate", "1"),
                ("createUiDefinition", "2"),
                ("testParameters", "3"),
                ("zip", "4"),
            )
        }
        attempt_id = "current-attempt"
        selected_reference = "Logs/run/packaging.v3_1.current-attempt.json"
        package_document = {
            "packager": "V3.1",
            "packageAttemptId": attempt_id,
            "workflowRunId": "selected-run",
            "packageArtifactsSha256": "b" * 64,
            "packageInputs": {"after": {"sha256": package_input_hash}},
            "packageArtifactHashes": artifact_hashes,
        }
        workflow = {
            "runId": "selected-run",
            "stages": {
                "packaging": {
                    "status": "passed",
                    "artifacts": {
                        "packageReport": selected_reference,
                        "packageAttemptId": attempt_id,
                        "packageReportSha256": report_hash,
                    },
                },
            },
            "packaging": {
                "lastSuccessful": {
                    "packageSucceeded": True,
                    "attemptId": attempt_id,
                    "packageReport": selected_reference,
                    "packageReportSha256": report_hash,
                    "packageArtifactsSha256": "b" * 64,
                    "packageInputSha256": package_input_hash,
                },
            },
        }
        resolved = Mock()
        resolved.resolve.return_value = Path("/selected-run/current-package.json")
        resolved.read_bytes.return_value = report_bytes
        with (
            patch("sentinel_xdr_migration.solution_report.report_directory", return_value=Path("/selected-run/reports")),
            patch("sentinel_xdr_migration.solution_report.resolve_artifact_reference", return_value=resolved),
            patch("sentinel_xdr_migration.solution_report._read_run_json", return_value=package_document),
        ):
            selected, reference = _selected_packaging_report(Path("/selected-run"), workflow)
        self.assertEqual(package_document, selected)
        self.assertEqual(selected_reference, reference)

        workflow["packaging"]["lastSuccessful"]["packageReport"] = "Logs/run/packaging.v3_1.json"
        with (
            patch("sentinel_xdr_migration.solution_report.report_directory", return_value=Path("/selected-run/reports")),
            patch("sentinel_xdr_migration.solution_report.resolve_artifact_reference", return_value=resolved),
            patch("sentinel_xdr_migration.solution_report._read_run_json", return_value=package_document),
        ):
            selected, reference = _selected_packaging_report(Path("/selected-run"), workflow)
        self.assertEqual({}, selected)
        self.assertIsNone(reference)

    def test_embedded_planning_consent_without_recorded_artifact_is_not_trusted(self) -> None:
        digest = "a" * 64
        contract = {
            "schemaVersion": "1.0.0",
            "status": "provisional",
            "selectedProfile": "qualification",
            "executionMode": "pairs",
            "target": {"workspaceResourceId": "<script>alert(1)</script>"},
            "planSha256": digest,
            "components": {
                "disabledRulePairValidation": {
                    "planningConsent": {"status": "approved"},
                    "resourceTypes": ["Microsoft.Security/detectionRules@2026-06-01-preview"],
                    "selectedFlags": {"disabledOnly": True},
                },
                "mockTelemetryIngestion": {
                    "planningConsent": {"status": "unknown"},
                    "conditional": True,
                },
            },
            "planningConsent": {
                "status": "approved",
                "planSha256": digest,
                "componentKeys": ["disabledRulePairValidation"],
                "resourceTypes": ["Microsoft.Security/detectionRules@2026-06-01-preview"],
                "selectedFlags": {"disabledOnly": True},
            },
            "exactScopeWriteApproval": "not-recorded",
            "readiness": "not-evaluated",
            "deploymentEvidence": "not-recorded",
        }
        with patch.object(
            deployment_planning,
            "existing_artifact_path",
            return_value=Path("/selected-run/deployment-planning-consent.json"),
        ):
            projected = _planning_summary(
                Path("/selected-run"),
                {},
                {"packageFreshness": {"status": "current"}},
                {"deploymentPlanning": contract},
            )

        self.assertEqual("unknown", projected["deploymentPlan"]["status"])
        self.assertEqual("not-recorded", projected["deploymentPlan"]["planningConsent"]["status"])
        self.assertEqual("not-recorded", projected["deploymentPlan"]["exactScopeWriteApproval"])
        self.assertEqual("pairs", projected["deploymentPlan"]["executionMode"])
        self.assertEqual(
            ["Microsoft.Security/detectionRules@2026-06-01-preview"],
            projected["deploymentPlan"]["components"]["disabledRulePairValidation"]["resourceTypes"],
        )
        self.assertEqual(
            "not-recorded",
            projected["deploymentPlan"]["components"]["disabledRulePairValidation"]["planningConsent"],
        )
        self.assertEqual(
            "unknown",
            projected["deploymentPlan"]["components"]["mockTelemetryIngestion"]["planningConsent"],
        )
        html = _deployment_planning_html({"deploymentPlanning": projected})
        self.assertIn("Qualification", html)
        self.assertIn("disabledRulePairValidation", html)
        self.assertIn("Microsoft.Security/detectionRules", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_plan_approval_and_identity_follow_current_package_freshness(self) -> None:
        digest = "a" * 64
        changed_digest = "b" * 64
        artifact_hashes = {
            "mainTemplate": "1" * 64,
            "createUiDefinition": "2" * 64,
            "testParameters": "3" * 64,
            "zip": "4" * 64,
        }
        resource_type = "Microsoft.Security/detectionRules"
        package_resource_type = "Microsoft.Resources/deployments"
        target = {
            "tenantId": "tenant",
            "subscriptionId": "subscription",
            "resourceGroup": "resource-group",
            "workspaceResourceId": "/subscriptions/example/workspaces/lab",
            "solution": "Example",
            "version": "3.1.1",
        }
        plan_template = {
            "schemaVersion": "1.0.0",
            "status": "current",
            "selectedProfile": "qualification",
            "executionMode": "pairs",
            "target": target,
            "planSha256": "c" * 64,
            "packageInputSha256": digest,
            "packageArtifactHashes": artifact_hashes,
            "recordedPackageArtifactHashes": artifact_hashes,
            "packageIdentity": {"status": "current", "version": "3.1.1"},
            "components": {
                "sentinelAlertRules": {
                    "resourceTypes": [resource_type],
                    "planningConsent": {"status": "approved"},
                },
                "fullPackageAcceptance": {
                    "resourceTypes": [package_resource_type],
                    "availableFlags": {"DeployWorkbook": True},
                    "planningConsent": {"status": "approved"},
                },
            },
            "planningConsent": {
                "status": "approved",
                "planSha256": "c" * 64,
                "componentKeys": ["sentinelAlertRules"],
                "resourceTypes": [resource_type],
                "selectedFlags": {"disabledOnly": True},
            },
            "packageAcceptancePlan": {
                "status": "proposed",
                "approvalStatus": "approved",
                "packageIdentity": {"status": "current", "version": "3.1.1"},
            },
        }
        package = {
            "packageInputs": {"after": {"sha256": digest}},
            "packageArtifactHashes": artifact_hashes,
            "packageArtifactsSha256": "d" * 64,
            "packageReport": "Logs/run/packaging.v3_1.attempt.json",
            "version": "3.1.1",
            "deploymentParameters": {},
        }
        template = {"resources": []}

        def project(freshness: dict) -> dict:
            workflow = {
                "profile": "qualification",
                "profileSelectionConfirmed": True,
                "packageFreshness": freshness,
            }
            with (
                patch(
                    "sentinel_xdr_migration.solution_report._read_local_package_template",
                    return_value=(template, artifact_hashes["mainTemplate"]),
                ),
                patch(
                    "sentinel_xdr_migration.solution_report._deployment_planning_input",
                    return_value=plan_template,
                ),
                patch(
                    "sentinel_xdr_migration.solution_report._validated_planning_consent",
                    return_value={
                        "status": "approved",
                        "planSha256": plan_template["planSha256"],
                        "approvedComponents": ["fullPackageAcceptance", "sentinelAlertRules"],
                        "resourceTypes": [package_resource_type, resource_type],
                        "packageFlags": {"DeployWorkbook": True},
                        "executionMode": "both",
                    },
                ),
            ):
                return _planning_summary(Path("/selected-run"), package, workflow, {})

        stale = project({
            "status": "stale",
            "currentPackageInputSha256": changed_digest,
        })
        self.assertEqual("stale", stale["packageFreshness"])
        self.assertEqual("stale", stale["packageIdentity"])
        self.assertEqual(changed_digest, stale["currentPackageInputSha256"])
        self.assertEqual("stale", stale["deploymentPlan"]["status"])
        self.assertEqual("stale", stale["deploymentPlan"]["packageIdentity"]["status"])
        self.assertEqual("stale", stale["deploymentPlan"]["planningConsent"]["status"])
        self.assertEqual(
            "stale",
            stale["deploymentPlan"]["components"]["sentinelAlertRules"]["planningConsent"],
        )
        self.assertEqual("stale", stale["deploymentPlan"]["packageAcceptancePlan"]["approvalStatus"])
        self.assertEqual(
            "stale",
            stale["deploymentPlan"]["packageAcceptancePlan"]["packageIdentity"]["status"],
        )

        unknown = project({"status": "unverifiable"})
        self.assertEqual("unknown", unknown["packageFreshness"])
        self.assertEqual("unknown", unknown["packageIdentity"])
        self.assertEqual("unknown", unknown["deploymentPlan"]["status"])
        self.assertEqual("unknown", unknown["deploymentPlan"]["planningConsent"]["status"])
        self.assertEqual(
            "unknown",
            unknown["deploymentPlan"]["components"]["sentinelAlertRules"]["planningConsent"],
        )
        self.assertEqual("unknown", unknown["deploymentPlan"]["packageAcceptancePlan"]["approvalStatus"])

        missing_current_identity = project({"status": "current"})
        self.assertEqual("unknown", missing_current_identity["packageFreshness"])
        self.assertEqual("unknown", missing_current_identity["packageIdentity"])
        self.assertEqual("unknown", missing_current_identity["deploymentPlan"]["status"])
        self.assertEqual("unknown", missing_current_identity["deploymentPlan"]["planningConsent"]["status"])

        current = project({
            "status": "current",
            "currentPackageInputSha256": digest,
        })
        self.assertEqual("current", current["packageFreshness"])
        self.assertEqual(digest, current["currentPackageInputSha256"])
        self.assertEqual("verified current", current["packageIdentity"])
        self.assertEqual("current", current["deploymentPlan"]["status"])
        self.assertEqual("approved", current["deploymentPlan"]["planningConsent"]["status"])
        self.assertEqual(
            "approved",
            current["deploymentPlan"]["components"]["sentinelAlertRules"]["planningConsent"],
        )
        self.assertEqual("approved", current["deploymentPlan"]["packageAcceptancePlan"]["approvalStatus"])

    def test_package_inventory_reads_nested_arrays_and_language_version_two_resources(self) -> None:
        inventory = _package_resource_inventory({
            "resources": {
                "nested": {
                    "type": "Microsoft.Resources/deployments",
                    "properties": {
                        "template": {
                            "resources": [
                                {"type": "Microsoft.Security/detectionRules@2026-06-01-preview"},
                            ],
                        },
                    },
                },
                "alertRule": {
                    "type": "Microsoft.SecurityInsights/alertRules",
                    "apiVersion": "2024-03-01",
                },
            },
        })
        by_type = {item["type"]: item for item in inventory}
        self.assertEqual("2026-06-01-preview", by_type["Microsoft.Security/detectionRules"]["apiVersion"])
        self.assertEqual(
            "Microsoft.Security/detectionRules@2026-06-01-preview",
            by_type["Microsoft.Security/detectionRules"]["originalType"],
        )
        self.assertEqual("2024-03-01", by_type["Microsoft.SecurityInsights/alertRules"]["apiVersion"])
        self.assertIn("languageVersion 2 resource dictionary", by_type["Microsoft.SecurityInsights/alertRules"]["sourceForms"])
        self.assertIn("nested ARM resources array", by_type["Microsoft.Security/detectionRules"]["sourceForms"])

    def test_preflight_projection_keeps_management_grant_separate_from_read_and_get(self) -> None:
        projected = _preflight_projection({
            "status": "ready",
            "requiredManagementPermission": "CustomDetection.ReadWrite.All",
            "managementPermissionGrant": {
                "status": "missing",
                "grantType": "delegated",
                "claimType": "scp",
                "permission": "CustomDetection.ReadWrite.All",
                "credentialRequestScope": "graph-resource-default",
            },
            "deploymentReadiness": "action-required",
            "authentication": {
                "status": "acquired",
                "tokenPermissionClaims": {"status": "present", "claimType": "scp"},
            },
            "permissions": {
                "readAccess": "confirmed",
                "writeAuthorization": "not-tested",
                "effectiveRole": {"status": "unknown"},
            },
            "readChecks": [{"status": "confirmed", "httpStatus": 200}],
        })
        self.assertEqual("confirmed", projected["permissions"]["readAccess"])
        self.assertEqual(200, projected["readChecks"][0]["httpStatus"])
        self.assertEqual("missing", projected["managementPermissionGrant"]["status"])
        self.assertEqual("action-required", projected["deploymentReadiness"])
        self.assertEqual("unknown", projected["effectiveRoleStatus"])
        self.assertEqual("scp", projected["tokenPermissionClaims"]["claimType"])

    def test_runtime_pass_is_blocked_when_current_advanced_hunting_query_hash_differs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Example"
            analytic = root / "Analytic Rules"
            analytic.mkdir(parents=True)
            (analytic / "Rule.yaml").write_text(RULE, encoding="utf-8")
            convert_solution(root)
            detection_path = root / "XDR Detections/Rule.yaml"
            detection = yaml.safe_load(detection_path.read_text())
            target_query = detection["properties"]["queryCondition"]["queryText"]
            report_directory(root, create=True).joinpath(
                "runtime-validation.graph.json"
            ).write_text(json.dumps({
                "provider": "graph",
                "platform": "Microsoft Defender XDR Advanced Hunting",
                "results": [{
                    "detection": "Rule.yaml",
                    "status": "passed",
                    "rowCount": 1,
                    "querySha256": hashlib.sha256(b"DeviceEvents").hexdigest(),
                }],
            }))

            report = build_solution_report(root)
            runtime = report["rules"][0]["customDetection"]["runtime"][0]
            self.assertEqual("blocked", runtime["status"])
            self.assertEqual("stale-or-missing", runtime["queryHashStatus"])
            self.assertTrue(any(
                error["stage"] == "custom-detection-runtime-validation"
                and "exact current query was not validated" in error["message"]
                for error in report["rules"][0]["errors"]
            ))

            runtime_hash = hashlib.sha256(target_query.encode()).hexdigest()
            report_path = report_directory(root) / "runtime-validation.graph.json"
            result_document = json.loads(report_path.read_text())
            result_document["results"][0]["querySha256"] = runtime_hash
            report_path.write_text(json.dumps(result_document))
            refreshed = build_solution_report(root)
            self.assertEqual(
                "passed",
                refreshed["rules"][0]["customDetection"]["runtime"][0]["status"],
            )

    def test_source_waiver_is_visible_without_hiding_failure_or_blocked_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Example"
            analytic = root / "Analytic Rules"
            analytic.mkdir(parents=True)
            for index in range(14):
                rule = yaml.safe_load(RULE)
                rule["id"] = str(__import__("uuid").UUID(int=index + 1))
                rule["name"] = f"Example rule {index + 1}"
                rule["query"] = (
                    "DeviceEvents\n"
                    f"| where DeviceId == '{index + 1}'\n"
                    "| project TimeGenerated, AccountUpn, IPAddress"
                )
                (analytic / f"Rule{index + 1:02}.yaml").write_text(
                    yaml.safe_dump(rule), encoding="utf-8"
                )
            convert_solution(root)
            report_dir = report_directory(root)
            source_results = []
            for path in sorted(analytic.glob("*.yaml")):
                rule = yaml.safe_load(path.read_text(encoding="utf-8"))
                result = {
                    "detection": path.name,
                    "status": "passed",
                    "rowCount": 1,
                    "dependencyProvenanceSha256": dependency_identity(yaml.safe_load(
                        (root / "XDR Detections" / path.name).read_text(encoding="utf-8")
                    )),
                    "querySha256": hashlib.sha256(
                        rule["query"].encode("utf-8")
                    ).hexdigest(),
                }
                if path.name == "Rule01.yaml":
                    diagnostic = (
                        "'summarize' operator: Failed to resolve table or "
                        "column expression named 'IdentityInfo'"
                    )
                    result.update({
                        "status": "failed",
                        "statusCode": 400,
                        "failureKind": "query",
                        "error": {
                            "code": "BadArgumentError",
                            "message": diagnostic,
                            "innererror": {
                                "code": "SemanticError",
                                "innererror": {
                                    "code": "SEM0100",
                                    "message": diagnostic,
                                },
                            },
                        },
                        "errorDetails": {
                            "code": "BadArgumentError",
                            "innererror": {
                                "code": "SemanticError",
                                "innererror": {
                                    "code": "SEM0100",
                                    "message": diagnostic,
                                },
                            },
                        },
                    })
                source_results.append(result)
            (report_dir / "runtime-validation.azure-monitor-sdk.json").write_text(
                json.dumps({
                    "provider": "azure-monitor-sdk",
                    "querySurface": "log-analytics-workspace",
                    "platform": "Microsoft Sentinel Log Analytics",
                    "total": 14,
                    "familyComplete": True,
                    "results": source_results,
                }),
                encoding="utf-8",
            )
            graph_results = []
            for path in sorted((root / "XDR Detections").glob("*.yaml")):
                detection = yaml.safe_load(path.read_text(encoding="utf-8"))
                target_query = detection["properties"]["queryCondition"]["queryText"]
                graph_results.append({
                    "detection": path.name,
                    "status": "not-run",
                    "statusCode": 0,
                    "rowCount": None,
                    "querySha256": hashlib.sha256(
                        target_query.encode("utf-8")
                    ).hexdigest(),
                    "error": "XDR runtime validation was not run.",
                })
            (report_dir / "runtime-validation.graph.json").write_text(
                json.dumps({
                    "provider": "graph",
                    "querySurface": "defender-advanced-hunting",
                    "platform": "Defender Advanced Hunting",
                    "total": 14,
                    "notRun": 14,
                    "results": graph_results,
                }),
                encoding="utf-8",
            )
            workflow_path = existing_artifact_path(root, "workflow-state.json")
            workflow_path.write_text(
                json.dumps({
                    "runId": report_dir.parent.name,
                    "workflowStatus": "active",
                    "stages": {
                        "validation": {
                            "status": "blocked",
                            "message": "Graph validation remains not run.",
                        }
                    },
                }),
                encoding="utf-8",
            )
            report = build_solution_report(root)

            rule = next(
                item for item in report["rules"]
                if any(
                    runtime["status"] == "failed"
                    for runtime in item["analyticRule"]["runtime"]
                )
            )
            source_runtime = next(
                runtime for runtime in rule["analyticRule"]["runtime"]
                if runtime["status"] == "failed"
            )
            self.assertEqual("failed", source_runtime["status"])
            self.assertEqual("IdentityInfo", source_runtime["sourceWhitelist"]["table"])
            self.assertEqual(
                "source-waived", source_runtime["sourceWhitelist"]["status"]
            )
            self.assertEqual(
                "failed", source_runtime["sourceWhitelist"]["rawFailure"]["status"]
            )
            self.assertEqual(14, len(report["rules"]))
            self.assertEqual(
                14,
                sum(
                    runtime["status"] == "not-run"
                    for item in report["rules"]
                    for runtime in item["customDetection"]["runtime"]
                ),
            )
            self.assertEqual("not-run", rule["customDetection"]["runtime"][0]["status"])
            self.assertTrue(any(
                error["stage"] == "analytic-rule-runtime-validation"
                for error in rule["errors"]
            ))
            self.assertEqual("blocked", report["runtimeAssessment"]["validationStageStatus"])
            self.assertFalse(report["runtimeAssessment"]["fullyRuntimeQualified"])
            self.assertEqual("source-waived", report["runtimeAssessment"]["sourceStatus"])
            self.assertEqual(1, len(report["runtimeAssessment"]["sourceWhitelist"]))
            self.assertEqual(13, report["summary"]["analyticRuntimePassed"])
            self.assertEqual(0, report["summary"]["customRuntimePassed"])
            self.assertEqual(1, report["summary"]["errors"])
            self.assertEqual(0, report["summary"]["strictParityPassed"])
            self.assertEqual(0, report["summary"]["queryParityPassed"])
            self.assertIn("does not qualify", rule["warnings"][-1])
            self.assertEqual(14, report["summary"]["rules"])
            persisted = json.loads(Path(report["jsonReport"]).read_text(encoding="utf-8"))
            self.assertEqual(
                "source-waived",
                persisted["runtimeAssessment"]["sourceWhitelist"][0]["status"],
            )
            html = Path(report["htmlReport"]).read_text(encoding="utf-8")
            self.assertIn("Source runtime whitelist", html)
            self.assertIn("IdentityInfo", html)

    def test_information_uses_manifest_with_provenance_fallback_without_status_changes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Example"
            analytic = root / "Analytic Rules"
            analytic.mkdir(parents=True)
            (analytic / "Rule.yaml").write_text(yaml.safe_dump({
                "id": "11111111-1111-1111-1111-111111111111", "name": "Example",
                "description": "Example", "severity": "High", "queryFrequency": "1h", "queryPeriod": "4h",
                "query": "DeviceEvents | project Timestamp, DeviceId, DeviceName",
                "entityMappings": [{"entityType": "Host", "fieldMappings": [{"identifier": "HostName", "columnName": "DeviceName"}]}],
            }), encoding="utf-8")
            convert_solution(root)
            reports = report_directory(root)
            manifest_path = reports / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["results"][0].pop("informational", None)
            manifest_path.write_text(json.dumps(manifest))
            draft_path = root / "XDR Detections" / "Rule.yaml"
            draft = yaml.safe_load(draft_path.read_text())
            draft["contentProvenance"]["conversion"]["informational"] = ["Provenance fallback"]
            draft_path.write_text(yaml.safe_dump(draft))
            fallback = build_solution_report(root)
            self.assertEqual(fallback["rules"][0]["informational"], ["Provenance fallback"])
            self.assertEqual(len(fallback["rules"][0]["sourceSha256"]), 64)
            manifest["results"][0]["informational"] = []
            manifest_path.write_text(json.dumps(manifest))
            empty = build_solution_report(root)
            self.assertEqual(empty["rules"][0]["informational"], [])
            self.assertEqual(empty["summary"]["informational"], 0)
            self.assertEqual(fallback["summary"]["informational"], 1)
            self.assertEqual(fallback["summary"]["rulesWithInformation"], 1)
            self.assertEqual(
                {key: value for key, value in empty["summary"].items() if key not in {"informational", "rulesWithInformation"}},
                {key: value for key, value in fallback["summary"].items() if key not in {"informational", "rulesWithInformation"}},
            )
            manifest["results"][0]["informational"] = ["Manifest <information>"]
            manifest_path.write_text(json.dumps(manifest))
            explicit = build_solution_report(root)
            self.assertEqual(explicit["rules"][0]["informational"], ["Manifest <information>"])
            self.assertEqual(explicit["summary"], fallback["summary"])
            self.assertIn("Manifest &lt;information&gt;", Path(explicit["htmlReport"]).read_text())

    def test_report_renderer_parses_as_python_311(self) -> None:
        source_path = (
            Path(__file__).parents[1]
            / "solution_manager"
            / "reporting"
            / "solution_report.py"
        )
        ast.parse(
            source_path.read_text(encoding="utf-8"),
            filename=str(source_path),
            feature_version=(3, 11),
        )

    def test_report_contains_rule_status_and_entity_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Example"
            rules = root / "Analytic Rules"
            rules.mkdir(parents=True)
            source = {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "Example rule",
                "description": "Example",
                "severity": "High",
                "tactics": ["Execution"],
                "relevantTechniques": ["T1059"],
                "queryFrequency": "1h",
                "queryPeriod": "1h",
                "query": "Example_CL | project User",
                "entityMappings": [
                    {
                        "entityType": "Account",
                        "fieldMappings": [
                            {"identifier": "Name", "columnName": "User"}
                        ],
                    }
                ],
            }
            (rules / "Rule.yaml").write_text(
                yaml.safe_dump(source, sort_keys=False), encoding="utf-8"
            )
            convert_solution(root)
            output = root / "XDR Detections"
            reports = report_directory(root, create=True)
            (reports / "runtime-validation.log-analytics-cli.json").write_text(
                json.dumps(
                    {
                        "platform": "Microsoft Sentinel Log Analytics",
                        "provider": "log-analytics-cli",
                        "results": [
                            {
                                "detection": "Rule.yaml",
                                "status": "passed",
                                "rowCount": 1,
                                "querySha256": hashlib.sha256(
                                    source["query"].encode()
                                ).hexdigest(),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (reports / "runtime-validation.graph.json").write_text(
                json.dumps(
                    {
                        "platform": "Microsoft Defender XDR Advanced Hunting",
                        "provider": "graph",
                        "results": [
                            {
                                "detection": "Rule.yaml",
                                "status": "blocked",
                                "rowCount": 0,
                                "querySha256": hashlib.sha256(
                                    yaml.safe_load(
                                        (output / "Rule.yaml").read_text()
                                    )["properties"]["queryCondition"]["queryText"].encode()
                                ).hexdigest(),
                                "error": "table unavailable",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (reports / "mock-query-parity.json").write_text(
                json.dumps(
                    {
                        "reportPath": str(reports / "mock-query-parity.json"),
                        "comparisons": [
                            {
                                "detection": "Rule.yaml",
                                "passed": True,
                                "matchKey": {"IPAddress": "192.0.2.1"},
                                "analyticRuleRows": 1,
                                "customDetectionRows": 1,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (reports / "packaging.v3_1.json").write_text(
                json.dumps({
                    "packageReport": str(reports / "packaging.v3_1.json"),
                    "tacticProjection": [{
                        "detectionId": f"xdr-{source['id']}",
                        "authoredTactics": ["Execution", "Persistence"],
                        "packagedTactics": ["Execution"],
                        "omittedTactics": ["Persistence"],
                    }],
                }),
                encoding="utf-8",
            )

            report = build_solution_report(root)

            self.assertEqual(report["solution"], "Example")
            self.assertEqual(report["summary"]["rules"], 1)
            self.assertEqual(report["rules"][0]["queries"]["source"], source["query"])
            self.assertTrue(report["rules"][0]["queries"]["converted"])
            self.assertIn("workflow", report)
            classification = report["rules"][0]["attackClassification"]
            self.assertEqual(classification["sourceTactics"], ["Execution"])
            self.assertEqual(classification["sourceTechniques"], ["T1059"])
            self.assertEqual(classification["originalTactics"], ["Execution"])
            self.assertEqual(classification["originalTechniques"], ["T1059"])
            self.assertEqual(classification["draftTactics"], [
                {"tactic": "Execution", "techniques": [{"technique": "T1059"}]}
            ])
            self.assertEqual(
                report["rules"][0]["customDetection"]["conversionStatus"],
                "converted",
            )
            self.assertTrue(
                report["rules"][0]["customDetection"]["reviewRequired"]
            )
            self.assertIn("complete UPN", report["rules"][0]["entityRecommendation"])
            self.assertEqual(
                report["rules"][0]["analyticRule"]["runtime"][0]["status"], "passed"
            )
            self.assertEqual(
                report["rules"][0]["customDetection"]["runtime"][0]["status"],
                "blocked",
            )
            self.assertEqual(report["summary"]["analyticRuntimePassed"], 1)
            self.assertEqual(report["summary"]["customRuntimePassed"], 0)
            self.assertEqual(report["summary"]["queryParityPassed"], 1)
            self.assertEqual(report["summary"]["packagedTacticOmissions"], 1)
            self.assertEqual(
                report["rules"][0]["packagingProjection"]["omittedTactics"],
                ["Persistence"],
            )
            self.assertTrue(any(
                "not parity" in message for message in report["rules"][0]["informational"]
            ))
            self.assertEqual(report["rules"][0]["queryParity"]["status"], "passed")
            self.assertTrue(Path(report["jsonReport"]).exists())
            self.assertTrue(Path(report["htmlReport"]).exists())
            self.assertEqual(reports, Path(report["jsonReport"]).parent)
            self.assertEqual(
                ["Rule.yaml"],
                sorted(path.name for path in output.iterdir()),
            )
            html = Path(report["htmlReport"]).read_text(encoding="utf-8")
            self.assertIn("log-analytics-cli", html)
            self.assertIn("graph", html)
            self.assertIn("Query parity", html)

    def test_report_json_and_html_preserve_source_and_converted_kql_exactly(self) -> None:
        class SourceQueryParser(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.heading = None
                self.next_pre_is_source = False
                self.capture = False
                self.current = []
                self.queries = []

            def handle_starttag(self, tag, attrs):
                if tag == "h4":
                    self.heading = []
                elif tag == "pre" and self.next_pre_is_source:
                    self.capture = True
                    self.current = []
                    self.next_pre_is_source = False

            def handle_data(self, data):
                if self.heading is not None:
                    self.heading.append(data)
                if self.capture:
                    self.current.append(data)

            def handle_endtag(self, tag):
                if tag == "h4" and self.heading is not None:
                    self.next_pre_is_source = "".join(self.heading) == "Source Sentinel KQL"
                    self.heading = None
                elif tag == "pre" and self.capture:
                    self.queries.append("".join(self.current))
                    self.capture = False

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Example"
            rules = root / "Analytic Rules"
            rules.mkdir(parents=True)
            query = (
                "DeviceProcessEvents\n"
                '| where NewProcessName endswith "\\\\\\\\certutil.exe"\n'
                '| extend SourcePath = "C:\\\\\\\\Program Files\\\\\\\\source\\\\\\\\agent.exe"\n'
                "| join kind=inner (DeviceNetworkEvents | project DeviceId, RemoteUrl) on DeviceId\n"
                '| where RemoteUrl contains "https://example.test/source?mode=join"\n'
                "| project TimeGenerated, DeviceId, SourcePath"
            )
            source = {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "Query fidelity",
                "description": "Report serialization fidelity fixture.",
                "severity": "High",
                "queryFrequency": "1h",
                "queryPeriod": "1h",
                "query": query,
            }
            source_path = rules / "Rule.yaml"
            source_path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
            loaded_source = yaml.safe_load(source_path.read_text(encoding="utf-8"))
            self.assertEqual(query, loaded_source["query"])
            convert_solution(root)
            target_path = root / "XDR Detections" / "Rule.yaml"
            target_query = yaml.safe_load(target_path.read_text(encoding="utf-8"))[
                "properties"
            ]["queryCondition"]["queryText"]

            report = build_solution_report(root)
            rule = report["rules"][0]
            self.assertEqual(loaded_source["query"], rule["queries"]["source"])
            self.assertEqual(target_query, rule["queries"]["converted"])
            persisted = json.loads(Path(report["jsonReport"]).read_text(encoding="utf-8"))
            self.assertEqual(loaded_source["query"], persisted["rules"][0]["queries"]["source"])
            self.assertEqual(target_query, persisted["rules"][0]["queries"]["converted"])
            self.assertEqual("Analytic Rules/Rule.yaml", persisted["rules"][0]["sourceFile"])
            self.assertEqual("XDR Detections/Rule.yaml", persisted["rules"][0]["outputFile"])

            parser = SourceQueryParser()
            parser.feed(Path(report["htmlReport"]).read_text(encoding="utf-8"))
            self.assertEqual([loaded_source["query"]], parser.queries)


if __name__ == "__main__":
    unittest.main()
