from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
import yaml
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration.artifacts import report_directory, using_run, write_json_artifact
from sentinel_xdr_migration.dependencies import dependency_identity
from sentinel_xdr_migration.packaging_selection import (
    PLAN_NAME,
    STRUCTURAL_NAME,
    _build_package_selection_plan,
    _analytic_rule_structure_errors,
    _content_reference,
    _current_target,
    _data_context_sha256,
    _manifest_reference,
    _run_context,
    _runtime_target_fingerprint,
    _runtime_binding,
    _runtime_family,
    _review_evidence_sha256,
    _source_provider_route_errors,
    _selection_arrays,
    _selection_plan_hash,
    _atomic_exchange_if_unchanged,
    _file_snapshot,
    _exchange_paths,
    _write_selection_receipt,
    apply_package_selection,
    create_package_selection_plan,
    verify_applied_package_selection,
)
from sentinel_xdr_migration import runtime_consent
from sentinel_xdr_migration.workflow import initialize_workflow
from sentinel_xdr_migration import cli as cli_module


class PackagingSelectionTests(unittest.TestCase):
    def test_source_runtime_selection_requires_canonical_verified_fallback(self) -> None:
        from sentinel_xdr_migration.artifacts import report_directory

        with using_run(self.solution, self.run_id):
            reports = report_directory(self.solution, create=True)
            (reports / "runtime-validation.triage-mcp.json").write_text(
                json.dumps({
                    "provider": "triage-mcp",
                    "providerFailure": {"failureKind": "provider-unavailable"},
                }),
                encoding="utf-8",
            )
            sdk_path = reports / "runtime-validation.azure-monitor-sdk.json"
            sdk_report = {
                "provider": "azure-monitor-sdk",
                "providerFallback": {
                    "mcpProvider": "triage-mcp",
                    "fallbackProvider": "azure-monitor-sdk",
                    "batchComplete": True,
                    "permissionsVerified": True,
                    "kqlError": False,
                },
            }
            sdk_path.write_text(json.dumps(sdk_report), encoding="utf-8")

            self.assertEqual(
                [],
                _source_provider_route_errors(reports, "azure-monitor-sdk"),
            )
            sdk_report["providerFallback"]["batchComplete"] = False
            sdk_path.write_text(json.dumps(sdk_report), encoding="utf-8")
            self.assertTrue(
                _source_provider_route_errors(
                    reports, "azure-monitor-sdk"
                )
            )
            sdk_report["providerFallback"] = True
            sdk_path.write_text(json.dumps(sdk_report), encoding="utf-8")
            self.assertTrue(
                _source_provider_route_errors(
                    reports, "azure-monitor-sdk"
                )
            )

    def test_selection_plan_blocks_unverified_global_provider_fallback(self) -> None:
        invalid = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            source_fallback_verified=False,
        )
        self.assertEqual("blocked", invalid["summary"]["outcome"])
        self.assertEqual("failed", invalid["providers"]["sentinel"]["routeStatus"])
        self.assertTrue(any(
            "canonical verified Triage fallback proof" in error
            for error in invalid["executionErrors"]
        ))

        valid = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            source_fallback_verified=True,
        )
        self.assertEqual("complete", valid["summary"]["outcome"])
        self.assertEqual("passed", valid["providers"]["sentinel"]["routeStatus"])

        excluded_item = self._build_one_rule_plan(
            source_status="passed",
            review_required=True,
            source_fallback_verified=True,
        )
        self.assertFalse(excluded_item["xdrDetections"][0]["included"])
        self.assertEqual([], excluded_item["executionErrors"])
        self.assertEqual(
            "passed", excluded_item["providers"]["sentinel"]["routeStatus"]
        )

    def test_runtime_families_require_exact_result_inventory(self) -> None:
        from sentinel_xdr_migration.content_paths import detection_reference

        names = ["A.yaml", "B.yaml", "C.yaml"]
        detection_paths = {}
        for name in names:
            path = self.solution / "XDR Detections" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("kind: CustomDetection\nproperties: {}\n", encoding="utf-8")
            detection_paths[name] = path
        self.assertEqual(
            "C.yaml",
            detection_reference("C.yaml", names),
        )
        query_hash = "a" * 64

        def entries(provider: str) -> list[dict]:
            result = []
            for name in names:
                item = {
                    "detection": name,
                    "status": "passed",
                    "querySha256": query_hash,
                }
                if provider == "graph":
                    item["schema"] = [{"name": "Column", "type": "string"}]
                else:
                    item["dependencyProvenanceSha256"] = dependency_identity(
                        yaml.safe_load(detection_paths[name].read_text())
                    )
                result.append(item)
            return result

        with using_run(self.solution, self.run_id):
            run_directory = report_directory(self.solution, create=True)
        state = {
            "context": {"workflowProfile": "authoring"},
            "stages": {"validation": {"artifacts": {}}},
        }
        for provider, surface in (
            ("azure-monitor-sdk", "log-analytics-workspace"),
            ("graph", "defender-advanced-hunting"),
        ):
            report_path = run_directory / f"runtime-validation.{provider}.json"
            valid_entries = entries(provider)

            def assess(results, *, family_complete=True):
                report_path.write_text(
                    json.dumps({
                        "provider": provider,
                        "querySurface": surface,
                        "familyComplete": family_complete,
                        "results": results,
                    }),
                    encoding="utf-8",
                )
                with (
                    mock.patch(
                        "sentinel_xdr_migration.packaging_selection._runtime_binding",
                        return_value=(True, "provider-target-binding-current"),
                    ),
                    mock.patch(
                        "sentinel_xdr_migration.packaging_selection.current_runtime_query_hash",
                        return_value=query_hash,
                    ),
                    mock.patch(
                        "sentinel_xdr_migration.packaging_selection.custom_detail_schema_errors",
                        return_value=[],
                    ),
                ):
                    return _runtime_family(
                        self.solution,
                        run_directory,
                        state,
                        provider=provider,
                        detection_paths=detection_paths,
                        target_fingerprint="f" * 64,
                    )

            missing = valid_entries[:-1]
            missing_evidence, missing_provider, missing_errors = assess(missing)
            self.assertTrue(any("missing expected detection results" in e for e in missing_errors))
            self.assertEqual("error", missing_provider["reportStatus"])

            failed = [dict(item) for item in valid_entries]
            failed[-1]["status"] = "failed"
            failed_evidence, failed_provider, failed_errors = assess(failed)
            self.assertEqual([], failed_errors)
            self.assertEqual("available", failed_provider["reportStatus"])
            self.assertEqual("failed", failed_evidence["C.yaml"]["status"])

            duplicate = valid_entries + [{
                **valid_entries[-1],
                "detection": "XDR Detections/C.yaml",
            }]
            _, _, duplicate_errors = assess(duplicate)
            self.assertTrue(any("duplicate results" in e for e in duplicate_errors))

            unknown = valid_entries + [{
                "detection": "Unknown.yaml",
                "status": "passed",
                "querySha256": query_hash,
            }]
            _, _, unknown_errors = assess(unknown)
            self.assertTrue(any("unknown or ambiguous" in e for e in unknown_errors))

            _, _, incomplete_errors = assess(valid_entries, family_complete=False)
            self.assertTrue(any("family incomplete" in e for e in incomplete_errors))

            _, _, malformed_errors = assess([*valid_entries, None])
            self.assertTrue(any("malformed result" in e for e in malformed_errors))

            _, _, empty_errors = assess(None)
            self.assertTrue(any("no results inventory" in e for e in empty_errors))
            self.assertTrue(any("missing expected detection results" in e for e in empty_errors))

    def test_lab_consent_change_preserves_persisted_runtime_plan_binding(self) -> None:
        target_fingerprint = "f" * 64
        plan = {
            "schemaVersion": runtime_consent.PLAN_SCHEMA_VERSION,
            "status": "ready",
            "solution": ".",
            "runId": self.run_id,
            "workflowProfile": "qualification",
            "target": {"fingerprintSha256": target_fingerprint},
            "labReadConsent": {
                "scope": {
                    "targetFingerprintSha256": target_fingerprint,
                    "confirmedPrimarySetting": {
                        "name": "primary-workspace",
                        "value": "synthetic-primary-workspace",
                    },
                },
                "status": "not-approved",
                "approvedFamilies": [],
                "requiresExplicitApproval": True,
                "recordedAt": None,
                "latestDecision": {"status": "unanswered"},
            },
            "families": {
                "defenderXdrQueryFamily": {
                    "provider": {"provider": "graph"},
                    "familySha256": "a" * 64,
                },
            },
        }
        plan["planSha256"] = runtime_consent._runtime_query_plan_sha256(plan)
        with using_run(self.solution, self.run_id):
            run_directory = report_directory(self.solution, create=True)
        plan_path = run_directory / "runtime-query-plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")

        approved_plan = copy.deepcopy(plan)
        approved_plan["labReadConsent"].update({
            "status": "approved",
            "approvedFamilies": ["defenderXdrQueryFamily"],
            "requiresExplicitApproval": False,
            "recordedAt": "synthetic-approval-time",
            "latestDecision": {"status": "approved"},
        })
        self.assertEqual(
            plan["planSha256"],
            runtime_consent._runtime_query_plan_sha256(approved_plan),
        )
        changed_scope = copy.deepcopy(approved_plan)
        changed_scope["labReadConsent"]["scope"]["confirmedPrimarySetting"][
            "value"
        ] = "changed-primary-workspace"
        self.assertNotEqual(
            plan["planSha256"],
            runtime_consent._runtime_query_plan_sha256(changed_scope),
        )
        changed_inventory = copy.deepcopy(approved_plan)
        changed_inventory["families"]["defenderXdrQueryFamily"][
            "familySha256"
        ] = "b" * 64
        self.assertNotEqual(
            plan["planSha256"],
            runtime_consent._runtime_query_plan_sha256(changed_inventory),
        )

        binding = {
            "runId": self.run_id,
            "workflowProfile": "qualification",
            "solution": ".",
            "targetFingerprintSha256": target_fingerprint,
        }
        snapshot = {
            "status": "derived-from-lab-consent",
            "provider": "graph",
            "family": "defenderXdrQueryFamily",
            "planSha256": runtime_consent._runtime_query_plan_sha256(approved_plan),
            "binding": binding,
        }
        report = {
            "provider": "graph",
            "runtimeQueryConsent": snapshot,
            "runtimeQueryDispatchSnapshot": snapshot,
        }
        state = {"context": {"workflowProfile": "qualification"}}
        bound, reason = _runtime_binding(
            self.solution,
            run_directory,
            state,
            provider="graph",
            report=report,
            target_fingerprint=target_fingerprint,
        )

        self.assertTrue(bound, reason)
        persisted = json.loads(plan_path.read_text(encoding="utf-8"))
        self.assertEqual("not-approved", persisted["labReadConsent"]["status"])
        self.assertEqual(plan["planSha256"], persisted["planSha256"])

    def test_coverage_threshold_cannot_waive_global_family_completeness(self) -> None:
        from sentinel_xdr_migration.packaging_selection import _coverage_summary

        inventory = [
            {"id": f"00000000-0000-0000-0000-{index:012d}"}
            for index in (1, 2, 3)
        ]
        threshold = _coverage_summary(
            inventory,
            {item["id"] for item in inventory[:2]},
        )
        self.assertTrue(threshold["partialPublicationAllowed"])

        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            global_runtime_inventory_error=True,
        )
        self.assertEqual("blocked", plan["summary"]["outcome"])
        self.assertTrue(plan["summary"]["partialPublicationAllowed"])
        self.assertTrue(plan["executionErrors"])

    def test_review_evidence_projection_ignores_report_presentation_only_changes(self) -> None:
        review = {
            "workflow": {"runId": self.run_id},
            "rules": [{
                "sourceFile": "Analytic Rules/A.yaml",
                "sourceSha256": "source-hash",
                "analyticRule": {"id": "source-id"},
                "customDetection": {
                    "conversionStatus": "converted",
                    "reviewRequired": False,
                    "reviewScope": {"queryHash": "query-hash"},
                    "reviewDecisions": [{"decision": "approved"}],
                },
            }],
            "updatedAt": "before",
            "partialSolution": {"status": "partial-package-validated"},
        }
        before = _review_evidence_sha256(review)
        presentation_update = copy.deepcopy(review)
        presentation_update["updatedAt"] = "after"
        presentation_update["partialSolution"]["status"] = "report-refreshed"
        presentation_update["rules"][0]["sourceFile"] = (
            "/workspace/Solution/Analytic Rules/A.yaml"
        )
        self.assertEqual(before, _review_evidence_sha256(presentation_update))

        changed_review = copy.deepcopy(review)
        changed_review["rules"][0]["customDetection"]["reviewDecisions"] = []
        self.assertNotEqual(before, _review_evidence_sha256(changed_review))
        changed_source = copy.deepcopy(review)
        changed_source["rules"][0]["sourceSha256"] = "new-source-hash"
        self.assertNotEqual(before, _review_evidence_sha256(changed_source))

    def test_applied_selection_stays_current_after_final_report_presentation_update(self) -> None:
        from sentinel_xdr_migration.solution_report import build_solution_report

        initial = self._build_one_rule_plan(
            source_status="passed", review_required=False
        )

        with using_run(self.solution, self.run_id):
            plan_path = report_directory(self.solution, create=True) / PLAN_NAME
        write_json_artifact(self.solution, plan_path, initial)
        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            return_value=initial,
        ):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=initial["planSha256"],
            )
        with using_run(self.solution, self.run_id):
            build_solution_report(self.solution)
        finalized = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            reuse_existing_review=True,
        )
        self.assertEqual(initial["planSha256"], finalized["planSha256"])
        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            return_value=finalized,
        ):
            current = verify_applied_package_selection(self.solution, self.run_id)
        self.assertEqual(initial["planSha256"], current["plan"]["planSha256"])

        changed_review = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            review_decision_change=True,
        )
        self.assertNotEqual(initial["planSha256"], changed_review["planSha256"])
        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            return_value=changed_review,
        ), self.assertRaisesRegex(ValueError, "evidence or artifact hashes changed"):
            verify_applied_package_selection(self.solution, self.run_id)

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.solution = Path(self.temp.name) / "Selection"
        self.solution.mkdir()
        for folder, name in (
            ("Analytic Rules", "Keep.yaml"),
            ("Analytic Rules", "Drop.yaml"),
            ("XDR Detections", "Keep.yaml"),
            ("XDR Detections", "Drop.yaml"),
        ):
            path = self.solution / folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"name: {name}\n", encoding="utf-8")
        self.data_path = self.solution / "Data" / "Solution_Selection.json"
        self.data_path.parent.mkdir()
        self.original_data = {
            "Name": "Selection",
            "Version": "3.1.1",
            "Analytic Rules": [
                "Analytic Rules/Keep.yaml",
                "Analytic Rules/Drop.yaml",
            ],
            "XDR Detections": [
                "XDR Detections/Keep.yaml",
                "XDR Detections/Drop.yaml",
            ],
            "Parsers": ["Parsers/Hand-authored.yaml"],
        }
        self.data_path.write_text(json.dumps(self.original_data), encoding="utf-8")
        self.run_id = initialize_workflow(
            self.solution, workflow_profile="authoring",
        )["runId"]

    def test_content_reference_normalizes_selected_solution_repository_prefix(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            repository = Path(temp)
            solution = repository / "Solutions" / "Selected"
            for relative in (
                Path("Analytic Rules/Rule.yaml"),
                Path("XDR Detections/Detection.yaml"),
            ):
                path = solution / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("name: synthetic\n", encoding="utf-8")

            prefix = solution.relative_to(repository).as_posix()
            for family, relative in (
                ("Analytic Rules", "Analytic Rules/Rule.yaml"),
                ("XDR Detections", "XDR Detections/Detection.yaml"),
            ):
                with self.subTest(family=family):
                    normalized, resolved = _content_reference(
                        solution,
                        f"{prefix}/{relative}",
                        family,
                    )
                    self.assertEqual(relative, normalized)
                    self.assertEqual((solution / relative).resolve(), resolved)

            windows_reference = (
                f"{prefix}/XDR Detections/Detection.yaml".replace("/", "\\")
            )
            normalized, _ = _content_reference(
                solution,
                windows_reference,
                "XDR Detections",
            )
            self.assertEqual("XDR Detections/Detection.yaml", normalized)

    def test_content_reference_rejects_wrong_prefix_family_and_traversal(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            repository = Path(temp)
            solution = repository / "Solutions" / "Selected"
            detection = solution / "XDR Detections" / "Detection.yaml"
            detection.parent.mkdir(parents=True)
            detection.write_text("name: synthetic\n", encoding="utf-8")

            for reference in (
                "Solutions/Other/XDR Detections/Detection.yaml",
                "Solutions/Selected/Analytic Rules/Detection.yaml",
                "Solutions/Selected/XDR Detections/../Analytic Rules/Detection.yaml",
                "../Solutions/Selected/XDR Detections/Detection.yaml",
                "/Solutions/Selected/XDR Detections/Detection.yaml",
                "C:/Solutions/Selected/XDR Detections/Detection.yaml",
            ):
                with self.subTest(reference=reference):
                    with self.assertRaises(ValueError):
                        _content_reference(solution, reference, "XDR Detections")

    def test_content_reference_rejects_symlink_targets(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            repository = Path(temp)
            solution = repository / "Solutions" / "Selected"
            output = solution / "XDR Detections"
            output.mkdir(parents=True)
            outside = repository / "Outside.yaml"
            outside.write_text("name: synthetic\n", encoding="utf-8")
            link = output / "Linked.yaml"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable in this environment")

            with self.assertRaisesRegex(
                ValueError,
                "content path escapes its root: XDR Detections/Linked.yaml",
            ):
                _content_reference(
                    solution,
                    "Solutions/Selected/XDR Detections/Linked.yaml",
                    "XDR Detections",
                )

    def _plan_builder(self, solution, run_id, *, candidate_lists_override=None, **_kwargs):
        data = json.loads(self.data_path.read_text(encoding="utf-8"))
        candidates = candidate_lists_override or {
            "analyticRules": data["Analytic Rules"],
            "xdrDetections": data["XDR Detections"],
        }
        file_hashes = {
            path.relative_to(self.solution).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for folder in ("Analytic Rules", "XDR Detections")
            for path in sorted((self.solution / folder).glob("*.yaml"))
        }
        plan = {
            "solution": ".",
            "runId": run_id,
            "summary": {
                "outcome": "partial",
                "coveragePolicy": "strictly-greater-than-50-percent-of-original-sentinel-rules",
                "originalSourceRuleCount": 1,
                "originalSourceRuleIds": ["11111111-1111-1111-1111-111111111111"],
                "validatedMigratedSourceRuleCount": 1,
                "validatedMigratedSourceRuleIds": ["11111111-1111-1111-1111-111111111111"],
                "coverageNumerator": 1,
                "coverageDenominator": 1,
                "partialPublicationAllowed": True,
            },
            "input": {
                "candidateReferences": candidates,
                "solutionDataContextSha256": _data_context_sha256(data),
                "originalSourceInventorySha256": "b" * 64,
                "files": file_hashes,
            },
            "selection": {
                "analyticRules": ["Analytic Rules/Keep.yaml"],
                "xdrDetections": ["XDR Detections/Keep.yaml"],
            },
        }
        plan["planSha256"] = _selection_plan_hash(plan)
        return plan

    def test_partial_coverage_uses_strict_integer_boundary_and_full_inventory(self) -> None:
        from sentinel_xdr_migration.packaging_selection import (
            _coverage_summary,
            _partial_coverage_allowed,
        )

        for denominator, numerator, expected in (
            (2, 1, False),
            (3, 2, True),
            (7, 6, True),
            (14, 13, True),
            (7, 3, False),
        ):
            source_inventory = [
                {
                    "id": f"00000000-0000-0000-0000-{index:012d}",
                    "path": f"Analytic Rules/{index}.yaml",
                }
                for index in range(1, denominator + 1)
            ]
            migrated = {item["id"] for item in source_inventory[:numerator]}
            summary = _coverage_summary(source_inventory, migrated)

            with self.subTest(denominator=denominator, numerator=numerator):
                self.assertEqual(expected, summary["partialPublicationAllowed"])
                self.assertEqual(expected, _partial_coverage_allowed(summary))
                self.assertEqual(denominator, summary["originalSourceRuleCount"])
                self.assertEqual(numerator, summary["validatedMigratedSourceRuleCount"])

        self.assertFalse(_partial_coverage_allowed(_coverage_summary([], set())))

        inventory = [
            {"id": "11111111-1111-1111-1111-111111111111"},
            {"id": "22222222-2222-2222-2222-222222222222"},
        ]
        duplicate_detection_rows = [
            "11111111-1111-1111-1111-111111111111",
            "11111111-1111-1111-1111-111111111111",
        ]
        duplicate_summary = _coverage_summary(inventory, duplicate_detection_rows)
        self.assertEqual(1, duplicate_summary["validatedMigratedSourceRuleCount"])
        self.assertFalse(duplicate_summary["partialPublicationAllowed"])

    def _save_plan(self) -> dict:
        plan = self._plan_builder(self.solution, self.run_id)
        with using_run(self.solution, self.run_id):
            path = report_directory(self.solution, create=True) / PLAN_NAME
        write_json_artifact(self.solution, path, plan)
        return plan

    def _build_one_rule_plan(
        self,
        *,
        source_status: str,
        review_required: bool,
        review_scope_mismatch: bool = False,
        metadata_change_after_review: bool = False,
        malformed_source: bool = False,
        source_kind: str = "Scheduled",
        nrt_with_scheduling_fields: bool = False,
        missing_xdr_array: bool = False,
        explicit_empty_xdr_array: bool = False,
        omit_manifest_source: bool = False,
        source_fallback_verified: bool | None = None,
        review_decision_change: bool = False,
        reuse_existing_review: bool = False,
        global_runtime_inventory_error: bool = False,
        plan_operation=None,
    ) -> dict:
        source_id = "11111111-1111-1111-1111-111111111111"
        source = self.solution / "Analytic Rules" / "Keep.yaml"
        output = self.solution / "XDR Detections" / "Keep.yaml"
        (self.solution / "Analytic Rules" / "Drop.yaml").unlink(missing_ok=True)
        (self.solution / "XDR Detections" / "Drop.yaml").unlink(missing_ok=True)
        source_fields = [
            f"id: {source_id}",
            "name: Keep",
            f"kind: {source_kind}",
            "description: Identifies a test event.",
            "severity: Medium",
            "status: Available",
            "version: 1.0.0",
            "tactics: [Execution]",
            "relevantTechniques: [T1059]",
            "requiredDataConnectors:",
            "  - connectorId: AzureActiveDirectory",
            "    dataTypes: [SigninLogs]",
            "query: DeviceEvents | where Timestamp > ago(5m) | count",
        ]
        if source_kind == "Scheduled":
            source_fields.extend((
                "queryFrequency: 5m",
                "queryPeriod: 5m",
                "triggerOperator: gt",
                "triggerThreshold: 0",
            ))
        elif nrt_with_scheduling_fields:
            source_fields.append("queryFrequency: 5m")
        source.write_text("\n".join((*source_fields, "")), encoding="utf-8")
        if malformed_source:
            source.write_text(f"id: {source_id}\nname: Keep\nquery: DeviceEvents | count\n", encoding="utf-8")
        output.write_text(
            "\n".join((
                "kind: CustomDetection",
                "contentProvenance:",
                "  source:",
                f"    id: {source_id}",
                "    path: Analytic Rules/Keep.yaml",
                "  conversion:",
                "    status: converted",
                f"    reviewRequired: {'true' if review_required else 'false'}",
                "    reviewScope:",
                "      mappingHash: current",
                "properties:",
                "  id: xdr-11111111-1111-1111-1111-111111111111",
                "",
            )),
            encoding="utf-8",
        )
        self.original_data["Analytic Rules"] = ["Analytic Rules/Keep.yaml"]
        if missing_xdr_array:
            self.original_data.pop("XDR Detections", None)
        else:
            self.original_data["XDR Detections"] = (
                [] if explicit_empty_xdr_array else ["XDR Detections/Keep.yaml"]
            )
        self.data_path.write_text(json.dumps(self.original_data), encoding="utf-8")

        with using_run(self.solution, self.run_id):
            run_directory = report_directory(self.solution, create=True)
        manifest_results = [] if omit_manifest_source else [{
            "sourceRelativePath": "Analytic Rules/Keep.yaml",
            "outputRelativePath": "XDR Detections/Keep.yaml",
            "status": "needsReview" if review_required else "converted",
            "reviewRequired": review_required,
            "errors": [],
        }]
        (run_directory / "manifest.json").write_text(json.dumps({
            "scope": {"kind": "solution"},
            "total": len(manifest_results),
            "results": manifest_results,
        }), encoding="utf-8")
        if source_fallback_verified is not None:
            (run_directory / "runtime-validation.triage-mcp.json").write_text(
                json.dumps({
                    "provider": "triage-mcp",
                    "providerFailure": {"failureKind": "provider-unavailable"},
                }),
                encoding="utf-8",
            )
            proof = {
                "mcpProvider": "triage-mcp",
                "fallbackProvider": "azure-monitor-sdk",
                "batchComplete": source_fallback_verified,
                "permissionsVerified": True,
                "kqlError": False,
            }
            (run_directory / "runtime-validation.azure-monitor-sdk.json").write_text(
                json.dumps({
                    "provider": "azure-monitor-sdk",
                    "providerFallback": proof,
                }),
                encoding="utf-8",
            )
        review = {
            "workflow": {"runId": self.run_id},
            "rules": [{
                "sourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "sourceFile": "Analytic Rules/Keep.yaml",
                "analyticRule": {"id": source_id},
                "customDetection": {
                    "reviewRequired": review_required,
                    "reviewScope": {
                        "mappingHash": "stale" if review_scope_mismatch else "current",
                    },
                    "reviewDecisions": [],
                    "conversionStatus": "converted",
                },
            }],
        }
        if review_decision_change:
            review["rules"][0]["customDetection"]["reviewDecisions"] = [
                {"decision": "changed"}
            ]
        review_path = run_directory / "migration-report.json"
        if reuse_existing_review:
            review = json.loads(review_path.read_text(encoding="utf-8"))
        else:
            review_path.write_text(json.dumps(review), encoding="utf-8")
        if metadata_change_after_review:
            output.write_text(
                output.read_text(encoding="utf-8") + "description: metadata-only change\n",
                encoding="utf-8",
            )
        state = {
            "context": {"workflowProfile": "authoring"},
            "stages": {"validation": {
                "artifacts": {
                    "sentinelRuntimeJson": "runtime-validation.azure-monitor-sdk.json",
                },
            }},
        }
        query_hash = "a" * 64

        def runtime_family(_root, _run_directory, _state, *, provider, **_kwargs):
            entry = (
                {"status": source_status, "expectedQuerySha256": query_hash}
                if provider != "graph"
                else {"status": "failed" if review_required else "passed", "reason": "graph-failed"}
            )
            errors = (
                [f"{provider} runtime report is missing expected detection results: C.yaml"]
                if global_runtime_inventory_error and provider == "graph"
                else []
            )
            return {"Keep.yaml": entry}, {"provider": provider}, errors

        source_structural_status = (
            "failed"
            if malformed_source or (source_kind == "NRT" and nrt_with_scheduling_fields)
            else "passed"
        )
        source_structural_errors = (
            ["analytic rule is missing: kind, severity, queryFrequency, queryPeriod"]
            if malformed_source else
            ["NRT rules must not include queryFrequency"]
            if source_kind == "NRT" and nrt_with_scheduling_fields else []
        )
        structural = {
            "results": [
                {
                    "file": "Analytic Rules/Keep.yaml",
                    "fileSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "status": source_structural_status,
                    "kind": "analyticRule",
                    "errors": source_structural_errors,
                },
                {
                    "file": "XDR Detections/Keep.yaml",
                    "fileSha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                    "status": "passed",
                    "valid": True,
                    "kind": "customDetection",
                    "errors": [],
                },
            ],
        }
        full_hashes = {
            "Analytic Rules/Keep.yaml": hashlib.sha256(source.read_bytes()).hexdigest(),
            "XDR Detections/Keep.yaml": hashlib.sha256(output.read_bytes()).hexdigest(),
        }
        patches = (
            mock.patch(
                "sentinel_xdr_migration.packaging_selection._run_context",
                return_value=(run_directory, state),
            ),
            mock.patch(
                "sentinel_xdr_migration.packaging_selection._validation_evidence",
                return_value=(structural, full_hashes),
            ),
            mock.patch(
                "sentinel_xdr_migration.packaging_selection._current_target",
                return_value=(None, None),
            ),
            mock.patch(
                "sentinel_xdr_migration.packaging_selection._current_review_report",
                side_effect=lambda _directory, _run_id: (
                    json.loads(review_path.read_text(encoding="utf-8")),
                    review_path,
                ),
            ),
            mock.patch(
                "sentinel_xdr_migration.packaging_selection._runtime_family",
                side_effect=runtime_family,
            ),
            mock.patch(
                "sentinel_xdr_migration.packaging_selection.current_runtime_query_hash",
                return_value=query_hash,
            ),
        )
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            if plan_operation is not None:
                return plan_operation()
            return _build_package_selection_plan(self.solution, self.run_id)

    def test_crlf_structural_report_retains_exact_reviewed_hash_before_apply_commit(self) -> None:
        def write_crlf_artifact(solution, path, document):
            write_json_artifact(solution, path, document)
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))

        def check_plan_and_apply():
            plan = create_package_selection_plan(self.solution, self.run_id)
            with using_run(self.solution, self.run_id):
                structural = report_directory(self.solution) / STRUCTURAL_NAME
            saved = structural.read_bytes()
            self.assertIn(b"\r\n", saved)
            self.assertEqual(hashlib.sha256(saved).hexdigest(), plan["input"]["structuralValidationSha256"])
            refreshed = _build_package_selection_plan(self.solution, self.run_id)
            self.assertEqual(plan["planSha256"], refreshed["planSha256"])
            before = self.data_path.read_bytes()
            with mock.patch(
                "sentinel_xdr_migration.packaging_selection._atomic_exchange_if_unchanged",
                side_effect=RuntimeError("serialization checks reached commit boundary"),
            ) as commit, self.assertRaisesRegex(RuntimeError, "reached commit boundary"):
                apply_package_selection(
                    self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
                )
            commit.assert_called_once()
            self.assertEqual(before, self.data_path.read_bytes())
            self.assertEqual(saved, structural.read_bytes())
            return plan

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection.write_json_artifact",
            side_effect=write_crlf_artifact,
        ):
            self._build_one_rule_plan(
                source_status="passed", review_required=False,
                plan_operation=check_plan_and_apply,
            )

    def test_structural_report_byte_edits_still_invalidate_reviewed_plan(self) -> None:
        for edit in ("line-endings", "whitespace"):
            with self.subTest(edit=edit):
                def check_rejection():
                    plan = create_package_selection_plan(self.solution, self.run_id)
                    with using_run(self.solution, self.run_id):
                        structural = report_directory(self.solution) / STRUCTURAL_NAME
                    saved = structural.read_bytes()
                    if edit == "line-endings":
                        changed = (
                            saved.replace(b"\r\n", b"\n")
                            if b"\r\n" in saved else saved.replace(b"\n", b"\r\n")
                        )
                    else:
                        changed = saved + b" \n"
                    structural.write_bytes(changed)
                    refreshed = _build_package_selection_plan(self.solution, self.run_id)
                    self.assertNotEqual(plan["planSha256"], refreshed["planSha256"])
                    self.assertEqual(
                        hashlib.sha256(changed).hexdigest(),
                        refreshed["input"]["structuralValidationSha256"],
                    )
                    before = self.data_path.read_bytes()
                    with mock.patch(
                        "sentinel_xdr_migration.packaging_selection._atomic_exchange_if_unchanged",
                    ) as commit, self.assertRaisesRegex(ValueError, "selection plan is stale"):
                        apply_package_selection(
                            self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
                        )
                    commit.assert_not_called()
                    self.assertEqual(before, self.data_path.read_bytes())
                    return plan

                self._build_one_rule_plan(
                    source_status="passed", review_required=False, plan_operation=check_rejection,
                )

    def test_structural_report_changed_findings_and_invalid_json_block_apply(self) -> None:
        for edit in ("findings", "invalid-json"):
            with self.subTest(edit=edit):
                def check_rejection():
                    plan = create_package_selection_plan(self.solution, self.run_id)
                    with using_run(self.solution, self.run_id):
                        structural = report_directory(self.solution) / STRUCTURAL_NAME
                    if edit == "findings":
                        changed = json.loads(structural.read_bytes())
                        changed["results"][0]["status"] = "failed"
                        structural.write_text(json.dumps(changed), encoding="utf-8")
                    else:
                        structural.write_bytes(b"not a JSON report")
                    before = self.data_path.read_bytes()
                    with mock.patch(
                        "sentinel_xdr_migration.packaging_selection._atomic_exchange_if_unchanged",
                    ) as commit, self.assertRaisesRegex(
                        ValueError, "structural-validation evidence changed|structural-validation evidence is invalid",
                    ):
                        apply_package_selection(
                            self.solution, self.run_id, expected_plan_sha256=plan["planSha256"],
                        )
                    commit.assert_not_called()
                    self.assertEqual(before, self.data_path.read_bytes())
                    return plan

                self._build_one_rule_plan(
                    source_status="passed", review_required=False, plan_operation=check_rejection,
                )

    def test_plan_hash_does_not_mutate_nested_plan_data(self) -> None:
        plan = {
            "input": {
                "solutionDataSha256AtPlan": "data-hash",
                "versionAtPlan": "3.1.1",
                "candidateReferences": {"analyticRules": [], "xdrDetections": []},
            },
            "createdAt": "ignored",
        }
        original = copy.deepcopy(plan)

        _selection_plan_hash(plan)

        self.assertEqual(original, plan)

    def test_conversion_manifest_paths_reject_escape_and_wrong_family(self) -> None:
        for path, family in (
            ("Analytic Rules/../secret.yaml", "Analytic Rules"),
            ("XDR Detections\\..\\secret.yaml", "XDR Detections"),
            ("Other/Rule.yaml", "Analytic Rules"),
        ):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unsafe"):
                _manifest_reference(path, family)

    def test_missing_xdr_array_is_not_interpreted_as_an_empty_selection(self) -> None:
        data = dict(self.original_data)
        del data["XDR Detections"]

        with self.assertRaisesRegex(ValueError, "missing an explicit XDR Detections array"):
            _selection_arrays(self.solution, data)

    def test_legacy_dot_solution_binding_is_rooted_in_its_run_directory(self) -> None:
        with using_run(self.solution, self.run_id):
            run_directory = report_directory(self.solution)
        state_path = run_directory / "workflow-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["solution"] = "."
        state_path.write_text(json.dumps(state), encoding="utf-8")

        bound_directory, bound_state = _run_context(self.solution, self.run_id)

        self.assertEqual(run_directory, bound_directory)
        self.assertEqual(".", bound_state["solution"])

    def test_apply_updates_only_selection_arrays_and_verify_binds_full_file_hashes(self) -> None:
        plan = self._save_plan()
        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ):
            result = apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )
            applied = verify_applied_package_selection(self.solution, self.run_id)

        updated = json.loads(self.data_path.read_text(encoding="utf-8"))
        self.assertEqual(plan["selection"]["analyticRules"], updated["Analytic Rules"])
        self.assertEqual(plan["selection"]["xdrDetections"], updated["XDR Detections"])
        self.assertEqual(self.original_data["Name"], updated["Name"])
        self.assertEqual(self.original_data["Version"], updated["Version"])
        self.assertEqual(self.original_data["Parsers"], updated["Parsers"])
        self.assertEqual(plan["planSha256"], result["selectionPlanSha256"])
        self.assertEqual(plan["planSha256"], applied["plan"]["planSha256"])

        (self.solution / "XDR Detections" / "Keep.yaml").write_text(
            "name: edited after selection\n", encoding="utf-8",
        )
        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ), self.assertRaisesRegex(ValueError, "evidence or artifact hashes changed"):
            verify_applied_package_selection(self.solution, self.run_id)

    def test_apply_rejects_stale_plan_without_changing_data_arrays(self) -> None:
        plan = self._save_plan()
        (self.solution / "XDR Detections" / "Keep.yaml").write_text(
            "name: changed before apply\n", encoding="utf-8",
        )
        before = self.data_path.read_bytes()

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ), self.assertRaisesRegex(ValueError, "selection plan is stale"):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )

        self.assertEqual(before, self.data_path.read_bytes())

    def test_failed_detection_review_does_not_exclude_healthy_source_rule(self) -> None:
        plan = self._build_one_rule_plan(source_status="passed", review_required=True)

        self.assertTrue(plan["analyticRules"][0]["included"])
        self.assertEqual(["Analytic Rules/Keep.yaml"], plan["selection"]["analyticRules"])
        self.assertFalse(plan["xdrDetections"][0]["included"])
        self.assertIn("unresolved-review-required", plan["xdrDetections"][0]["reasons"])

    def test_failed_source_runtime_excludes_paired_detection_by_closure(self) -> None:
        plan = self._build_one_rule_plan(source_status="failed", review_required=False)

        self.assertFalse(plan["analyticRules"][0]["included"])
        self.assertFalse(plan["xdrDetections"][0]["included"])
        self.assertIn(
            "source-analytic-rule-is-not-included",
            plan["xdrDetections"][0]["reasons"],
        )

    def test_stale_source_query_evidence_excludes_rule_without_rerunning(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="stale",
            review_required=False,
        )

        self.assertFalse(plan["analyticRules"][0]["included"])
        self.assertEqual("a" * 64, plan["analyticRules"][0]["querySha256"])
        self.assertIn(
            "source-runtime-not-passed-for-current-query",
            plan["analyticRules"][0]["reasons"],
        )

    def test_changed_review_scope_does_not_reuse_old_review_evidence(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            review_scope_mismatch=True,
        )

        self.assertTrue(plan["analyticRules"][0]["included"])
        self.assertFalse(plan["xdrDetections"][0]["included"])
        self.assertIn(
            "source-or-review-evidence-stale-or-missing",
            plan["xdrDetections"][0]["reasons"],
        )

    def test_metadata_only_yaml_change_keeps_query_hash_and_refreshes_full_hash(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            metadata_change_after_review=True,
        )

        output = self.solution / "XDR Detections" / "Keep.yaml"
        self.assertTrue(plan["analyticRules"][0]["included"])
        self.assertTrue(plan["xdrDetections"][0]["included"], plan["xdrDetections"][0])
        self.assertEqual("a" * 64, plan["analyticRules"][0]["querySha256"])
        self.assertEqual("a" * 64, plan["xdrDetections"][0]["sourceQuerySha256"])
        self.assertEqual(
            hashlib.sha256(output.read_bytes()).hexdigest(),
            plan["xdrDetections"][0]["fileSha256"],
        )

    def test_structural_analytic_rule_validation_excludes_invalid_source_and_paired_detection(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            malformed_source=True,
        )

        self.assertFalse(plan["analyticRules"][0]["included"])
        self.assertEqual("failed", plan["analyticRules"][0]["checks"]["sourceYamlStructure"]["status"])
        self.assertFalse(plan["xdrDetections"][0]["included"])
        self.assertIn(
            "source-analytic-rule-is-not-included",
            plan["xdrDetections"][0]["reasons"],
        )

    def test_valid_nrt_source_rule_passes_kind_specific_structural_validation(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            source_kind="NRT",
        )

        self.assertTrue(plan["analyticRules"][0]["included"], plan["analyticRules"][0])
        self.assertIn(
            "kind: NRT",
            (self.solution / "Analytic Rules" / "Keep.yaml").read_text(encoding="utf-8"),
        )
        self.assertTrue(plan["xdrDetections"][0]["included"], plan["xdrDetections"][0])
        self.assertEqual(
            [],
            _analytic_rule_structure_errors({
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "NRT rule",
                "kind": "NRT",
                "description": "Identifies a test event.",
                "severity": "Medium",
                "status": "Available",
                "version": "1.0.0",
                "tactics": ["Execution"],
                "relevantTechniques": ["T1059"],
                "requiredDataConnectors": [{
                    "connectorId": "AzureActiveDirectory",
                    "dataTypes": ["SigninLogs"],
                }],
                "query": "DeviceEvents | where Timestamp > ago(5m) | count",
            }),
        )

    def test_nrt_with_scheduled_fields_is_structurally_excluded(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            source_kind="NRT",
            nrt_with_scheduling_fields=True,
        )

        self.assertFalse(plan["analyticRules"][0]["included"])
        self.assertIn(
            "NRT rules must not include queryFrequency",
            plan["analyticRules"][0]["checks"]["sourceYamlStructure"]["reason"],
        )
        self.assertIn(
            "NRT rules must not include queryFrequency",
            _analytic_rule_structure_errors({
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "NRT rule",
                "kind": "NRT",
                "description": "Identifies a test event.",
                "severity": "Medium",
                "status": "Available",
                "version": "1.0.0",
                "tactics": ["Execution"],
                "relevantTechniques": ["T1059"],
                "requiredDataConnectors": [{
                    "connectorId": "AzureActiveDirectory",
                    "dataTypes": ["SigninLogs"],
                }],
                "query": "DeviceEvents | where Timestamp > ago(5m) | count",
                "queryFrequency": "5m",
            }),
        )
        self.assertFalse(plan["xdrDetections"][0]["included"])

    def test_missing_xdr_array_bootstraps_reviewed_manifest_outputs_only_for_planning(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            missing_xdr_array=True,
        )

        self.assertTrue(plan["input"]["xdrArrayWasMissing"])
        self.assertTrue(plan["input"]["xdrReferencesBootstrappedFromManifest"])
        self.assertEqual(
            ["XDR Detections/Keep.yaml"],
            plan["input"]["bootstrapManifestOutputReferences"],
        )
        self.assertTrue(plan["xdrDetections"][0]["included"], plan["xdrDetections"][0])
        with using_run(self.solution, self.run_id):
            plan_path = report_directory(self.solution, create=True) / PLAN_NAME
        write_json_artifact(self.solution, plan_path, plan)

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            return_value=plan,
        ):
            applied = apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )
            verified = verify_applied_package_selection(self.solution, self.run_id)

        updated = json.loads(self.data_path.read_text(encoding="utf-8"))
        self.assertEqual(
            ["XDR Detections/Keep.yaml"],
            updated["XDR Detections"],
        )
        self.assertEqual("applied", applied["status"])
        self.assertEqual(plan["planSha256"], verified["plan"]["planSha256"])

    def test_explicit_empty_xdr_array_is_not_bootstrapped_from_manifest(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            explicit_empty_xdr_array=True,
        )

        self.assertFalse(plan["input"]["xdrArrayWasMissing"])
        self.assertFalse(plan["input"]["xdrReferencesBootstrappedFromManifest"])
        self.assertEqual([], plan["input"]["candidateReferences"]["xdrDetections"])
        self.assertEqual(1, len(plan["xdrDetections"]))
        self.assertFalse(plan["xdrDetections"][0]["included"])
        self.assertIn(
            "not-in-current-xdr-detection-selection",
            plan["xdrDetections"][0]["reasons"],
        )

    def test_all_excluded_inventory_is_blocked_not_ready(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="failed",
            review_required=False,
        )

        self.assertEqual("blocked", plan["summary"]["outcome"])
        self.assertEqual("no-eligible-analytic-rules", plan["summary"]["eligibilityBlockReason"])
        self.assertEqual([], plan["selection"]["analyticRules"])
        self.assertEqual([], plan["selection"]["xdrDetections"])

    def test_manifest_omission_cannot_shrink_original_inventory(self) -> None:
        plan = self._build_one_rule_plan(
            source_status="passed",
            review_required=False,
            omit_manifest_source=True,
        )

        self.assertEqual(1, plan["summary"]["originalSourceRuleCount"])
        self.assertEqual(0, plan["summary"]["validatedMigratedSourceRuleCount"])
        self.assertEqual("blocked", plan["summary"]["outcome"])
        self.assertTrue(any(
            "omits current source inventory item" in error
            for error in plan["executionErrors"]
        ))

    def test_blocked_all_excluded_plan_cannot_be_applied(self) -> None:
        plan = self._save_plan()
        plan["summary"]["outcome"] = "blocked"
        plan["summary"]["eligibilityBlockReason"] = "no-eligible-analytic-rules"
        plan["selection"] = {"analyticRules": [], "xdrDetections": []}
        plan["planSha256"] = _selection_plan_hash(plan)
        with using_run(self.solution, self.run_id):
            plan_path = report_directory(self.solution, create=True) / PLAN_NAME
        write_json_artifact(self.solution, plan_path, plan)
        original = self.data_path.read_bytes()

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            return_value=plan,
        ), self.assertRaisesRegex(ValueError, "no eligible Analytic Rules"):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )

        self.assertEqual(original, self.data_path.read_bytes())

    def test_runtime_plan_and_report_bindings_round_trip_for_source_and_graph(self) -> None:
        target = {
            "tenantId": "tenant",
            "subscriptionId": "subscription",
            "resourceGroup": "group",
            "workspaceResourceId": "/subscriptions/subscription/resourceGroups/group/providers/Microsoft.OperationalInsights/workspaces/lab",
            "workspaceName": "lab",
            "workspaceCustomerId": "customer",
        }
        target_fingerprint = _runtime_target_fingerprint(target)
        self.assertEqual(
            target_fingerprint,
            hashlib.sha256(
                json.dumps(
                    target, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                ).encode("utf-8")
            ).hexdigest(),
        )
        changed_name = dict(target, workspaceName="different")
        self.assertNotEqual(
            target_fingerprint,
            _runtime_target_fingerprint(changed_name),
        )
        initialize_workflow(self.solution, workflow_profile="authoring")

        def load_locked_target(root, *, materialize_missing=True):
            self.assertEqual(self.run_id, report_directory(root).name)
            return target

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection.require_locked_target",
            side_effect=load_locked_target,
        ):
            selected_target, selected_fingerprint = _current_target(
                self.solution,
                {
                    "runId": self.run_id,
                    "context": {"workflowProfile": "qualification"},
                },
            )
        self.assertEqual(target, selected_target)
        self.assertEqual(target_fingerprint, selected_fingerprint)
        run_directory = report_directory(self.solution, create=True)
        state = {
            "context": {"workflowProfile": "qualification"},
            "stages": {"validation": {
                "artifacts": {
                    "sentinelRuntimeJson": "runtime-validation.azure-monitor-sdk.json",
                },
            }},
        }
        binding = {
            "runId": self.run_id,
            "workflowProfile": "qualification",
            "solution": ".",
            "targetFingerprintSha256": target_fingerprint,
        }
        source_family = "sentinelSourceQueryFamily"
        source_plan = {
            "runId": self.run_id,
            "workflowProfile": "qualification",
            "solution": ".",
            "target": {"fingerprintSha256": target_fingerprint},
            "planSha256": "plan-sha",
            "families": {
                source_family: {"provider": {"provider": "azure-monitor-sdk"}},
                "defenderXdrQueryFamily": {"provider": {"provider": "graph"}},
            },
        }
        source_consent = {
            "status": "approved",
            "approvedFamilies": [source_family],
            "planSha256": "plan-sha",
            "binding": binding,
        }
        (run_directory / "runtime-query-plan.json").write_text(
            json.dumps(source_plan), encoding="utf-8",
        )
        (run_directory / "runtime-query-consent.json").write_text(
            json.dumps(source_consent), encoding="utf-8",
        )
        source_report = json.loads(json.dumps({
            "provider": "azure-monitor-sdk",
            "querySurface": "log-analytics-workspace",
            "runtimeQueryConsent": {
                "status": "approved",
                "provider": "azure-monitor-sdk",
                "family": source_family,
                "planSha256": "plan-sha",
                "binding": binding,
            },
            "runtimeQueryDispatchSnapshot": {
                "status": "approved",
                "provider": "azure-monitor-sdk",
                "family": source_family,
                "planSha256": "plan-sha",
                "binding": binding,
            },
        }))
        bound, reason = _runtime_binding(
            self.solution,
            run_directory,
            state,
            provider="azure-monitor-sdk",
            report=source_report,
            target_fingerprint=target_fingerprint,
        )
        self.assertTrue(bound, reason)
        unbound_report = {"provider": "azure-monitor-sdk"}
        bound, reason = _runtime_binding(
            self.solution,
            run_directory,
            state,
            provider="azure-monitor-sdk",
            report=unbound_report,
            target_fingerprint=target_fingerprint,
        )
        self.assertFalse(bound)
        self.assertEqual("provider-runtime-execution-binding-missing", reason)
        wrong_binding = dict(binding, targetFingerprintSha256="f" * 64)
        wrong_report = json.loads(json.dumps(source_report))
        wrong_report["runtimeQueryConsent"]["binding"] = wrong_binding
        wrong_report["runtimeQueryDispatchSnapshot"]["binding"] = wrong_binding
        bound, reason = _runtime_binding(
            self.solution,
            run_directory,
            state,
            provider="azure-monitor-sdk",
            report=wrong_report,
            target_fingerprint=target_fingerprint,
        )
        self.assertFalse(bound)
        self.assertEqual("provider-runtime-execution-binding-stale-or-mismatched", reason)
        stale_binding = dict(binding, runId="other-run")
        wrong_report["runtimeQueryConsent"]["binding"] = stale_binding
        wrong_report["runtimeQueryDispatchSnapshot"]["binding"] = stale_binding
        bound, reason = _runtime_binding(
            self.solution,
            run_directory,
            state,
            provider="azure-monitor-sdk",
            report=wrong_report,
            target_fingerprint=target_fingerprint,
        )
        self.assertFalse(bound)

        graph_family = "defenderXdrQueryFamily"
        graph_report = json.loads(json.dumps({
            "provider": "graph",
            "runtimeQueryConsent": {
                "status": "approved",
                "provider": "graph",
                "family": graph_family,
                "planSha256": "plan-sha",
                "binding": binding,
            },
            "runtimeQueryDispatchSnapshot": {
                "status": "approved",
                "provider": "graph",
                "family": graph_family,
                "planSha256": "plan-sha",
                "binding": binding,
            },
        }))
        bound, reason = _runtime_binding(
            self.solution,
            run_directory,
            state,
            provider="graph",
            report=graph_report,
            target_fingerprint=target_fingerprint,
        )
        self.assertTrue(bound, reason)

    def test_receipt_failure_rolls_back_data_and_allows_clean_retry(self) -> None:
        plan = self._save_plan()
        original_bytes = self.data_path.read_bytes()

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ), mock.patch(
            "sentinel_xdr_migration.packaging_selection._write_selection_receipt",
            side_effect=OSError("simulated receipt write failure"),
        ), self.assertRaisesRegex(
            RuntimeError, "rolled back under the package-selection writer lock"
        ):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )

        self.assertEqual(original_bytes, self.data_path.read_bytes())
        receipt_path = report_directory(self.solution) / "package-selection-applied.json"
        self.assertFalse(receipt_path.exists())
        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ):
            applied = apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )
        self.assertEqual("applied", applied["status"])

    def test_concurrent_receipt_is_not_overwritten_and_data_rolls_back(self) -> None:
        plan = self._save_plan()
        original_bytes = self.data_path.read_bytes()
        receipt_path = report_directory(self.solution) / "package-selection-applied.json"
        concurrent_bytes = b'{"concurrent":"receipt"}\n'
        def race_receipt(solution, path, receipt):
            path.write_bytes(concurrent_bytes)
            return _write_selection_receipt(solution, path, receipt)

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ), mock.patch(
            "sentinel_xdr_migration.packaging_selection._write_selection_receipt",
            side_effect=race_receipt,
        ), self.assertRaisesRegex(
            RuntimeError, "rolled back under the package-selection writer lock"
        ):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )

        self.assertEqual(original_bytes, self.data_path.read_bytes())
        self.assertEqual(concurrent_bytes, receipt_path.read_bytes())

    def test_apply_detects_data_race_after_plan_freshness_check(self) -> None:
        plan = self._save_plan()
        original_bytes = self.data_path.read_bytes()
        calls = 0

        def plan_with_concurrent_edit(solution, run_id, **kwargs):
            nonlocal calls
            result = self._plan_builder(solution, run_id, **kwargs)
            calls += 1
            if calls == 2:
                changed = json.loads(self.data_path.read_text(encoding="utf-8"))
                changed["Name"] = "concurrent edit"
                self.data_path.write_text(json.dumps(changed), encoding="utf-8")
            return result

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=plan_with_concurrent_edit,
        ), self.assertRaisesRegex(RuntimeError, "solution data changed during package-selection update"):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )

        self.assertNotEqual(original_bytes, self.data_path.read_bytes())
        self.assertEqual(
            "concurrent edit",
            json.loads(self.data_path.read_text(encoding="utf-8"))["Name"],
        )

    def test_apply_preserves_edit_arriving_while_commit_temp_is_prepared(self) -> None:
        plan = self._save_plan()
        original_fsync = os.fsync
        concurrent_bytes = b'{"Name":"user edit during commit"}\n'

        def edit_during_temp_flush(descriptor: int) -> None:
            original_fsync(descriptor)
            self.data_path.write_bytes(concurrent_bytes)

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ), mock.patch(
            "sentinel_xdr_migration.packaging_selection.os.fsync",
            side_effect=edit_during_temp_flush,
        ), self.assertRaisesRegex(RuntimeError, "solution data changed during package-selection update"):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )

        self.assertEqual(concurrent_bytes, self.data_path.read_bytes())
        receipt_path = report_directory(self.solution) / "package-selection-applied.json"
        self.assertFalse(receipt_path.exists())

    def test_atomic_exchange_restores_edit_arriving_at_commit_boundary(self) -> None:
        before = _file_snapshot(self.data_path)
        concurrent_bytes = b'{"Name":"user edit at exchange boundary"}\n'
        real_exchange = _exchange_paths
        changed = False

        def edit_then_exchange(left: Path, right: Path) -> None:
            nonlocal changed
            if not changed:
                changed = True
                self.data_path.write_bytes(concurrent_bytes)
            real_exchange(left, right)

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._exchange_paths",
            side_effect=edit_then_exchange,
        ), self.assertRaisesRegex(RuntimeError, "concurrent edit was restored"):
            _atomic_exchange_if_unchanged(
                self.data_path,
                b'{"Name":"selected"}\n',
                before,
            )

        self.assertEqual(concurrent_bytes, self.data_path.read_bytes())

    def test_receipt_failure_rollback_preserves_edit_arriving_during_rollback(self) -> None:
        plan = self._save_plan()
        original_fsync = os.fsync
        flush_count = 0
        concurrent_bytes = b'{"Name":"user edit during rollback"}\n'

        def edit_during_rollback_flush(descriptor: int) -> None:
            nonlocal flush_count
            flush_count += 1
            original_fsync(descriptor)
            if flush_count == 2:
                self.data_path.write_bytes(concurrent_bytes)

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ), mock.patch(
            "sentinel_xdr_migration.packaging_selection._write_selection_receipt",
            side_effect=OSError("simulated receipt write failure"),
        ), mock.patch(
            "sentinel_xdr_migration.packaging_selection.os.fsync",
            side_effect=edit_during_rollback_flush,
        ), self.assertRaisesRegex(RuntimeError, "concurrent solution-data edit was preserved"):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )

        self.assertEqual(2, flush_count)
        self.assertEqual(concurrent_bytes, self.data_path.read_bytes())
        receipt_path = report_directory(self.solution) / "package-selection-applied.json"
        self.assertFalse(receipt_path.exists())

    def test_post_receipt_freshness_check_preserves_concurrent_solution_data_edit(self) -> None:
        plan = self._save_plan()
        receipt_path = report_directory(self.solution) / "package-selection-applied.json"
        concurrent_bytes = b'{"Name":"user edit after receipt"}\n'

        def publish_receipt_then_edit(solution, path, receipt):
            _write_selection_receipt(solution, path, receipt)
            self.data_path.write_bytes(concurrent_bytes)

        with mock.patch(
            "sentinel_xdr_migration.packaging_selection._build_package_selection_plan",
            side_effect=self._plan_builder,
        ), mock.patch(
            "sentinel_xdr_migration.packaging_selection._write_selection_receipt",
            side_effect=publish_receipt_then_edit,
        ), self.assertRaisesRegex(RuntimeError, "concurrent solution-data edit was preserved"):
            apply_package_selection(
                self.solution,
                self.run_id,
                expected_plan_sha256=plan["planSha256"],
            )

        self.assertEqual(concurrent_bytes, self.data_path.read_bytes())
        self.assertTrue(receipt_path.is_file())
        self.assertEqual(
            self.run_id,
            json.loads(receipt_path.read_text(encoding="utf-8"))["runId"],
        )

    def test_cli_requires_an_exact_run_id_for_plan_and_apply(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
            with self.assertRaises(SystemExit) as raised:
                cli_module.main([
                    "package-selection-plan",
                    "--solution", str(self.solution),
                ])
        self.assertEqual(2, raised.exception.code)
        self.assertIn("--run-id", stderr.getvalue())

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr), mock.patch.object(
            cli_module,
            "create_package_selection_plan",
            return_value={"status": "ready", "runId": self.run_id},
        ) as plan:
            code = cli_module.main([
                "package-selection-plan",
                "--solution", str(self.solution),
                "--run-id", self.run_id,
            ])
        self.assertEqual(0, code, stderr.getvalue())
        plan.assert_called_once_with(str(self.solution), self.run_id)
        self.assertEqual(self.run_id, json.loads(stdout.getvalue())["runId"])

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr), mock.patch.object(
            cli_module,
            "create_package_selection_plan",
            return_value={"status": "blocked", "executionErrors": ["invalid report"]},
        ):
            blocked = cli_module.main([
                "package-selection-plan",
                "--solution", str(self.solution),
                "--run-id", self.run_id,
            ])
        self.assertEqual(1, blocked)


if __name__ == "__main__":
    unittest.main()
