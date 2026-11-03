from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration.artifacts import (
    artifact_path,
    existing_artifact_path,
    using_run,
)
from sentinel_xdr_migration.report_dashboard import _flow_stage
from sentinel_xdr_migration.dependencies import dependency_identity
from sentinel_xdr_migration.runtime import (
    current_runtime_evidence,
    record_runtime_validation,
)
from sentinel_xdr_migration.source_runtime_waiver import (
    MISSING_SCHEMA_TABLES,
    missing_schema_whitelist_match,
)
from sentinel_xdr_migration.workflow import (
    complete_workflow_stage,
    initialize_workflow,
    start_workflow_stage,
    workflow_status,
)
from sentinel_xdr_migration import workflow as workflow_module


TABLE_DIAGNOSTIC = (
    "'summarize' operator: Failed to resolve table or column expression "
    "named 'IdentityInfo'"
)
TABLE_QUERY = "IdentityInfo | summarize Count=count()"


def _sha256(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _sdk_failure(query: str, *, table_name: str = "IdentityInfo") -> dict:
    diagnostic = TABLE_DIAGNOSTIC.replace("IdentityInfo", table_name)
    sdk_error = {
        "code": "BadArgumentError",
        "message": diagnostic,
        "innererror": {
            "code": "SemanticError",
            "innererror": {
                "code": "SEM0100",
                "message": diagnostic,
            },
        },
    }
    return {
        "status": "failed",
        "statusCode": 400,
        "failureKind": "query",
        "querySha256": _sha256(query),
        "error": sdk_error,
        "errorDetails": sdk_error,
        "partial": False,
    }


class IdentityInfoSourceWhitelistTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def _create_solution(
        self,
        name: str,
        queries: list[str],
        *,
        provider: str = "azure-monitor-sdk",
        source_failure_indices: tuple[int, ...] = (0,),
        graph_status: str = "passed",
        graph_schema_overrides: dict[int, object] | None = None,
        source_overrides: dict[int, dict] | None = None,
        provider_failure: dict | None = None,
        family_complete: bool = True,
    ) -> tuple[Path, str, dict[str, str]]:
        solution = self.root / name
        source_root = solution / "Analytic Rules"
        detection_root = solution / "XDR Detections"
        source_root.mkdir(parents=True)
        detection_root.mkdir()
        run_id = initialize_workflow(
            solution,
            workflow_profile="authoring",
            version_bump="none",
        )["runId"]
        query_hashes: dict[str, str] = {}
        source_results: list[dict] = []
        graph_results: list[dict] = []
        surface = {
            "triage-mcp": "microsoft-sentinel-triage",
            "azure-monitor-sdk": "log-analytics-workspace",
            "log-analytics-cli": "log-analytics-workspace",
        }[provider]

        for index, query in enumerate(queries):
            name_on_disk = f"Rule{index:02}.yaml"
            rule_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{name}/{index}"))
            source_doc = {
                "id": rule_id,
                "name": f"Rule {index}",
                "query": query,
            }
            source_path = source_root / name_on_disk
            source_bytes = yaml.safe_dump(source_doc, sort_keys=False).encode()
            source_path.write_bytes(source_bytes)
            target_query = f"DeviceInfo | project DeviceName | take {index + 1}"
            detection_doc = {
                "kind": "CustomDetection",
                "contentProvenance": {
                    "source": {
                        "path": f"Analytic Rules/{name_on_disk}",
                        "id": rule_id,
                    },
                    "conversion": {
                        "status": "converted",
                        "reviewRequired": False,
                        "errors": [],
                    },
                },
                "properties": {
                    "id": rule_id,
                    "queryCondition": {"queryText": target_query},
                    "detectionAction": {"alertTemplate": {}},
                },
            }
            (detection_root / name_on_disk).write_text(
                yaml.safe_dump(detection_doc, sort_keys=False),
                encoding="utf-8",
            )
            query_hashes[name_on_disk] = _sha256(query)

            if index in source_failure_indices:
                result = _sdk_failure(query)
            else:
                result = {
                    "status": "passed",
                    "statusCode": 200,
                    "failureKind": None,
                    "querySha256": _sha256(query),
                    "rowCount": 0,
                    "dependencyProvenanceSha256": dependency_identity(detection_doc),
                }
            result["detection"] = name_on_disk
            if source_overrides and index in source_overrides:
                result.update(source_overrides[index])
            source_results.append(result)

            graph_entry = {
                "detection": name_on_disk,
                "status": graph_status,
                "statusCode": 200 if graph_status == "passed" else 0,
                "rowCount": 0,
                "querySha256": _sha256(target_query),
                "schemaColumnCount": 1,
                "error": None if graph_status == "passed" else "XDR query not run.",
            }
            if graph_status == "passed":
                graph_entry["schema"] = [{"name": "DeviceName", "type": "String"}]
            if graph_schema_overrides and index in graph_schema_overrides:
                schema = graph_schema_overrides[index]
                if schema is None:
                    graph_entry.pop("schema", None)
                else:
                    graph_entry["schema"] = schema
            graph_results.append(graph_entry)

        source_report_path = artifact_path(
            solution,
            f"runtime-validation.{provider}.json",
            create_parent=True,
        )
        source_report = {
            "provider": provider,
            "querySurface": surface,
            "total": len(source_results),
            "valid": sum(item["status"] == "passed" for item in source_results),
            "invalid": sum(item["status"] == "failed" for item in source_results),
            "blocked": sum(item["status"] == "blocked" for item in source_results),
            "notRun": sum(item["status"] == "not-run" for item in source_results),
            "familyComplete": family_complete,
            "results": source_results,
        }
        if provider_failure:
            source_report["providerFailure"] = provider_failure
        source_report_path.write_text(json.dumps(source_report), encoding="utf-8")
        graph_path = artifact_path(solution, "runtime-validation.graph.json")
        graph_path.write_text(json.dumps({
            "provider": "graph",
            "querySurface": "defender-advanced-hunting",
            "total": len(graph_results),
            "familyComplete": True,
            "results": graph_results,
        }), encoding="utf-8")
        return solution, run_id, query_hashes

    def _evidence(self, solution: Path, run_id: str) -> dict:
        with using_run(solution, run_id):
            return current_runtime_evidence(solution)

    def test_global_whitelist_across_solutions_and_rules_keeps_raw_failures(self) -> None:
        self.assertEqual(("IdentityInfo",), MISSING_SCHEMA_TABLES)
        first, first_run, _ = self._create_solution(
            "SolutionOne",
            [
                TABLE_QUERY,
                "DeviceEvents | take 1",
                "identityinfo | summarize Count=count()",
            ],
            source_failure_indices=(0, 2),
        )
        second, second_run, _ = self._create_solution(
            "SolutionTwo",
            [
                "IDENTITYINFO | project AccountUPN",
                "DeviceEvents | take 2",
            ],
            provider="triage-mcp",
            source_failure_indices=(0,),
        )

        for solution, run_id, count in (
            (first, first_run, 2),
            (second, second_run, 1),
        ):
            provider = "triage-mcp" if solution == second else "azure-monitor-sdk"
            raw_path = artifact_path(
                solution, f"runtime-validation.{provider}.json"
            )
            raw_before = raw_path.read_bytes()
            evidence = self._evidence(solution, run_id)
            self.assertFalse(evidence["passed"])
            self.assertEqual("source-waived", evidence["sourceStatus"])
            self.assertTrue(evidence["sourceWaiverOnlyBlocker"])
            self.assertEqual(count, len(evidence["sourceWhitelist"]))
            self.assertTrue(all(
                item["table"] == "IdentityInfo"
                and item["status"] == "source-waived"
                and item["applied"] is True
                and item["rawFailure"]["status"] == "failed"
                and item["sourceExecutionPassed"] is False
                and item["runtimeQualified"] is False
                for item in evidence["sourceWhitelist"]
            ))
            raw_after = json.loads(raw_path.read_bytes())
            self.assertEqual(raw_before, raw_path.read_bytes())
            self.assertTrue(all(
                item["status"] == "failed"
                for item in raw_after["results"]
                if item["detection"] in {
                    assessment["detection"]
                    for assessment in evidence["sourceWhitelist"]
                }
            ))
            self.assertEqual(
                len(raw_after["results"]),
                sum(item["status"] == "passed" for item in raw_after["results"])
                + sum(item["status"] == "failed" for item in raw_after["results"]),
            )

    def test_yolo_runtime_observations_keep_eligible_failure_nonblocking_and_raw(self) -> None:
        solution, run_id, _ = self._create_solution(
            "YoloObservation",
            [TABLE_QUERY],
            source_failure_indices=(0,),
        )
        source_path = solution / "Analytic Rules" / "Rule00.yaml"
        source = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        target_path = solution / "XDR Detections" / "Rule00.yaml"
        target = yaml.safe_load(target_path.read_text(encoding="utf-8"))
        target_query = target["properties"]["queryCondition"]["queryText"]
        raw_report_path = artifact_path(
            solution, "runtime-validation.azure-monitor-sdk.json"
        )
        raw_before = raw_report_path.read_bytes()
        inventory = [{
            "ruleId": source["id"],
            "querySha256": _sha256(source["query"]),
        }]
        results = [{
            "ruleId": source["id"],
            "status": "migrated",
            "target": {
                "path": "XDR Detections/Rule00.yaml",
                "querySha256": _sha256(target_query),
                "structurallyValid": True,
            },
        }]

        with using_run(solution, run_id):
            findings, environment_errors, _ = workflow_module._runtime_observations(
                solution, raw_report_path.parent, inventory, results
            )

        self.assertEqual([], environment_errors)
        waiver_finding = findings[source["id"]][0]
        self.assertFalse(waiver_finding["unresolved"])
        self.assertIn("source-waived for IdentityInfo", waiver_finding["message"])
        self.assertIn("Raw provider status remains 'failed'", waiver_finding["message"])
        self.assertEqual(raw_before, raw_report_path.read_bytes())

    def test_exact_nested_azure_sdk_sem0100_diagnostic_is_recognized(self) -> None:
        match = missing_schema_whitelist_match(
            _sdk_failure(TABLE_QUERY),
            provider="azure-monitor-sdk",
            expected_query_sha256=_sha256(TABLE_QUERY),
        )
        self.assertIsNotNone(match)
        self.assertEqual("IdentityInfo", match["table"])
        self.assertEqual("failed", match["rawFailure"]["status"])
        self.assertFalse(match["sourceExecutionPassed"])
        self.assertFalse(match["runtimeQualified"])

    def test_case_and_equivalent_explicit_table_diagnostic_are_supported(self) -> None:
        for spelling in ("identityinfo", "IDENTITYINFO"):
            query = f"{spelling} | take 1"
            failure = _sdk_failure(query, table_name=spelling)
            match = missing_schema_whitelist_match(
                failure,
                provider="log-analytics-cli",
                expected_query_sha256=_sha256(query),
            )
            self.assertIsNotNone(match)
            self.assertEqual("IdentityInfo", match["table"])

        query = "IdentityInfo | count"
        failure = {
            "status": "failed",
            "statusCode": 400,
            "failureKind": "query",
            "querySha256": _sha256(query),
            "error": "SEM0100: Failed to resolve table 'IdentityInfo'.",
            "errorDetails": "SEM0100: Failed to resolve table 'IdentityInfo'.",
        }
        self.assertIsNotNone(
            missing_schema_whitelist_match(
                failure,
                provider="triage-mcp",
                expected_query_sha256=_sha256(query),
            )
        )

    def test_missing_columns_other_tables_mixed_or_multiple_errors_are_not_whitelisted(self) -> None:
        query = TABLE_QUERY
        failures = [
            {"error": "SEM0100: Failed to resolve column 'IdentityInfo'."},
            {"error": "SEM0100: Failed to resolve table 'DeviceEvents'."},
            {
                "error": (
                    "SEM0100: Failed to resolve table 'IdentityInfo'; "
                    "SEM0200: Failed to resolve column 'AccountUPN'."
                )
            },
            {
                "error": (
                    "SEM0100: Failed to resolve table 'IdentityInfo'; "
                    "SEM0100: Failed to resolve table 'DeviceEvents'."
                )
            },
            {
                "error": "SEM0100: Failed to resolve table 'IdentityInfo'.",
                "errorDetails": "SEM0200: Failed to resolve column 'AccountUPN'.",
            },
            {"error": "KQL parse error near IdentityInfo."},
            {"error": "SEM0100: Failed to resolve table 'IdentityInfo'; authorization denied."},
        ]
        for override in failures:
            with self.subTest(override=override):
                entry = {
                    "status": "failed",
                    "statusCode": 400,
                    "failureKind": "query",
                    "querySha256": _sha256(query),
                    "errorDetails": "SEM0100",
                    **override,
                }
                self.assertIsNone(
                    missing_schema_whitelist_match(
                        entry,
                        provider="azure-monitor-sdk",
                        expected_query_sha256=_sha256(query),
                    )
                )

    def test_partial_authentication_provider_and_stale_failures_are_not_whitelisted(self) -> None:
        query = TABLE_QUERY
        variants = [
            {"partial": True},
            {"partialError": {"message": "some rows failed"}},
            {"failureKind": "authentication"},
            {"failureKind": "authorization", "statusCode": 403},
            {"failureKind": "provider"},
            {"statusCode": 408, "failureKind": "timeout"},
            {"querySha256": "0" * 64},
        ]
        for override in variants:
            with self.subTest(override=override):
                entry = {**_sdk_failure(query), **override}
                self.assertIsNone(
                    missing_schema_whitelist_match(
                        entry,
                        provider="azure-monitor-sdk",
                        expected_query_sha256=_sha256(query),
                    )
                )
        self.assertIsNone(
            missing_schema_whitelist_match(
                _sdk_failure(query),
                provider="graph",
                expected_query_sha256=_sha256(query),
            )
        )

    def test_provider_or_partial_family_failure_prevents_application(self) -> None:
        solution, run_id, _ = self._create_solution(
            "ProviderFailure",
            [TABLE_QUERY, "DeviceEvents | take 1"],
            provider_failure={"failureKind": "timeout", "message": "provider timed out"},
        )
        evidence = self._evidence(solution, run_id)
        self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
        self.assertEqual("candidate-blocked", evidence["sourceWhitelist"][0]["status"])

        partial, partial_run, _ = self._create_solution(
            "PartialFamily",
            [TABLE_QUERY, "DeviceEvents | take 1"],
            family_complete=False,
        )
        evidence = self._evidence(partial, partial_run)
        self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
        self.assertEqual("candidate-blocked", evidence["sourceWhitelist"][0]["status"])

        blocked, blocked_run, _ = self._create_solution(
            "AuthFailure",
            [TABLE_QUERY, "DeviceEvents | take 1"],
            source_overrides={
                1: {
                    "status": "blocked",
                    "statusCode": 401,
                    "failureKind": "authentication",
                    "error": "authentication failed",
                }
            },
        )
        evidence = self._evidence(blocked, blocked_run)
        self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
        self.assertEqual("candidate-blocked", evidence["sourceWhitelist"][0]["status"])
        self.assertEqual([], evidence["currentQueryFailures"])

    def test_stale_source_query_binding_blocks_whitelist(self) -> None:
        solution, run_id, hashes = self._create_solution(
            "StaleHash",
            [TABLE_QUERY],
        )
        source_path = artifact_path(
            solution, "runtime-validation.azure-monitor-sdk.json"
        )
        report = json.loads(source_path.read_text())
        report["results"][0]["querySha256"] = "0" * 64
        source_path.write_text(json.dumps(report), encoding="utf-8")
        evidence = self._evidence(solution, run_id)
        self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
        self.assertEqual([], evidence["sourceWhitelist"])
        self.assertTrue(any("stale" in issue.lower() for issue in evidence["issues"]))
        self.assertNotEqual("0" * 64, hashes["Rule00.yaml"])

    def test_recorded_stale_identityinfo_failure_is_candidate_only(self) -> None:
        for stale in (False, True):
            with self.subTest(stale=stale):
                solution, run_id, hashes = self._create_solution(
                    f"RecordedStale{stale}",
                    [TABLE_QUERY],
                )
                failure = _sdk_failure(TABLE_QUERY)
                failure["detection"] = "Rule00.yaml"
                if stale:
                    failure["querySha256"] = "0" * 64
                with using_run(solution, run_id):
                    report = record_runtime_validation(
                        solution,
                        provider="azure-monitor-sdk",
                        results_data=[failure],
                        family_complete=True,
                    )
                    evidence = current_runtime_evidence(solution)
                assessment = report["sourceWhitelist"][0]
                self.assertEqual("failed", report["results"][0]["status"])
                self.assertEqual("0" * 64 if stale else hashes["Rule00.yaml"], report["results"][0]["querySha256"])
                self.assertEqual(not stale, assessment["applied"])
                self.assertEqual(
                    "candidate-blocked" if stale else "source-waived",
                    assessment["status"],
                )
                if stale:
                    self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
                    self.assertEqual([], evidence["sourceWhitelist"])
                    self.assertTrue(any("stale" in issue.lower() for issue in evidence["issues"]))
                else:
                    self.assertTrue(evidence["sourceWaiverOnlyBlocker"])
                    self.assertEqual("source-waived", evidence["sourceWhitelist"][0]["status"])

    def test_changed_detection_inventory_blocks_source_whitelist_application(self) -> None:
        solution, run_id, _ = self._create_solution(
            "ChangedInventory",
            [TABLE_QUERY],
        )
        source_root = solution / "Analytic Rules"
        detection_root = solution / "XDR Detections"
        new_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "changed-inventory-added-rule"))
        (source_root / "Rule99.yaml").write_text(
            yaml.safe_dump({
                "id": new_id,
                "name": "Added after runtime",
                "query": "IdentityInfo | take 1",
            }),
            encoding="utf-8",
        )
        (detection_root / "Rule99.yaml").write_text(
            yaml.safe_dump({
                "kind": "CustomDetection",
                "contentProvenance": {
                    "source": {"path": "Analytic Rules/Rule99.yaml", "id": new_id},
                    "conversion": {
                        "status": "converted",
                        "reviewRequired": False,
                        "errors": [],
                    },
                },
                "properties": {
                    "id": new_id,
                    "queryCondition": {"queryText": "DeviceInfo | take 1"},
                    "detectionAction": {"alertTemplate": {}},
                },
            }),
            encoding="utf-8",
        )
        evidence = self._evidence(solution, run_id)
        self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
        self.assertEqual("candidate-blocked", evidence["sourceWhitelist"][0]["status"])
        self.assertIn("not a complete detection family", " ".join(evidence["issues"]))

    def test_xdr_unrun_schema_count_only_and_custom_details_remain_blockers(self) -> None:
        unrun, unrun_id, _ = self._create_solution(
            "XdrUnrun",
            [TABLE_QUERY],
            graph_status="not-run",
        )
        evidence = self._evidence(unrun, unrun_id)
        self.assertEqual("source-waived", evidence["sourceStatus"])
        self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
        self.assertFalse(evidence["passed"])
        self.assertTrue(any("not-run" in issue for issue in evidence["issues"]))

        count_only, count_only_id, _ = self._create_solution(
            "SchemaCountOnly",
            [TABLE_QUERY],
            graph_schema_overrides={0: None},
        )
        evidence = self._evidence(count_only, count_only_id)
        self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
        self.assertTrue(any("schemaColumnCount is not sufficient" in issue for issue in evidence["issues"]))

        custom, custom_id, _ = self._create_solution(
            "CustomDetails",
            [TABLE_QUERY],
            graph_schema_overrides={0: [{"name": "OtherColumn", "type": "String"}]},
        )
        detection_path = custom / "XDR Detections/Rule00.yaml"
        detection = yaml.safe_load(detection_path.read_text())
        detection["properties"]["detectionAction"]["alertTemplate"]["customDetails"] = {
            "account": "DeviceName"
        }
        detection_path.write_text(yaml.safe_dump(detection), encoding="utf-8")
        evidence = self._evidence(custom, custom_id)
        self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
        self.assertTrue(any("customDetails 'account' column `DeviceName` is absent" in issue for issue in evidence["issues"]))

    def test_xdr_actual_schema_requires_named_typed_columns(self) -> None:
        for index, schema in enumerate(
            ([], [{}], [{"name": "DeviceName"}], [{"name": "", "type": "String"}])
        ):
            with self.subTest(schema=schema):
                solution, run_id, _ = self._create_solution(
                    f"MalformedSchema{index}",
                    [TABLE_QUERY],
                    graph_schema_overrides={0: schema},
                )
                evidence = self._evidence(solution, run_id)
                self.assertFalse(evidence["sourceWaiverOnlyBlocker"])
                self.assertFalse(evidence["passed"])
                self.assertTrue(any(
                    "usable, uniquely named columns with types" in issue
                    for issue in evidence["issues"]
                ))

    def _prepare_direct_completion(
        self,
        name: str,
        *,
        graph_status: str = "passed",
        graph_schema_overrides: dict[int, object] | None = None,
        review_required: bool = False,
        technical_error: bool = False,
    ) -> tuple[Path, str]:
        solution, run_id, _ = self._create_solution(
            name,
            [TABLE_QUERY, "DeviceEvents | take 1"],
            graph_status=graph_status,
            graph_schema_overrides=graph_schema_overrides,
        )
        manifest_results = []
        for index in range(2):
            filename = f"Rule{index:02}.yaml"
            manifest_results.append({
                "sourceRelativePath": f"Analytic Rules/{filename}",
                "outputRelativePath": f"XDR Detections/{filename}",
                "status": "needsReview" if review_required and index == 1 else "converted",
                "reviewRequired": bool(review_required and index == 1),
                "errors": ["unrelated technical validation failure"]
                if technical_error and index == 1
                else [],
            })
            if review_required and index == 1:
                detection_path = solution / "XDR Detections" / filename
                detection = yaml.safe_load(detection_path.read_text())
                detection["contentProvenance"]["conversion"]["reviewRequired"] = True
                detection_path.write_text(yaml.safe_dump(detection), encoding="utf-8")
        manifest = {
            "scope": {"kind": "solution", "sourceTotal": 2, "selectedTotal": 2},
            "total": 2,
            "converted": 2,
            "excluded": 0,
            "needsReview": 0,
            "reviewRequired": 0,
            "conflicts": 0,
            "results": manifest_results,
        }
        manifest_path = artifact_path(solution, "manifest.json", create_parent=True)
        manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
        manifest_path.write_bytes(manifest_bytes)
        for stage in ("discovery", "conversion"):
            start_workflow_stage(solution, stage)
            complete_workflow_stage(
                solution,
                stage,
                status="passed",
                artifacts=(
                    {
                        "manifest": "manifest.json",
                        "manifestSha256": _sha256(manifest_bytes),
                    }
                    if stage == "conversion"
                    else {}
                ),
            )
        start_workflow_stage(solution, "validation")
        return solution, run_id

    def _complete_source_waived(self, solution: Path, *, structural_valid: bool = True) -> None:
        with mock.patch.object(
            workflow_module,
            "validate_solution",
            return_value={
                "conversionScope": {"kind": "solution"},
                "total": 2,
                "invalid": 0 if structural_valid else 1,
                "results": [{"valid": structural_valid}] * 2,
            },
        ):
            complete_workflow_stage(
                solution,
                "validation",
                status="passed",
                artifacts={"runtimeStatus": "source-waived"},
            )

    def test_direct_validation_completion_rechecks_xdr_and_review_gates(self) -> None:
        unrun, _ = self._prepare_direct_completion(
            "DirectUnrun",
            graph_status="not-run",
        )
        with self.assertRaisesRegex(ValueError, "every other exact runtime gate"):
            self._complete_source_waived(unrun)
        complete_workflow_stage(
            unrun, "validation", status="blocked", message="XDR is not run."
        )
        blocked_status = workflow_status(unrun)
        self.assertEqual("blocked", blocked_status["stages"]["validation"]["status"])
        self.assertEqual("source-waived", blocked_status["runtimeAssessment"]["sourceStatus"])
        self.assertFalse(blocked_status["runtimeAssessment"]["fullyRuntimeQualified"])
        self.assertEqual(
            "IdentityInfo",
            blocked_status["stages"]["validation"]["artifacts"][
                "sourceRuntimeWhitelistTable"
            ],
        )
        self.assertEqual(
            "failed",
            blocked_status["stages"]["validation"]["artifacts"][
                "sourceRuntimeWhitelistRawStatus"
            ],
        )

        schema_count, _ = self._prepare_direct_completion(
            "DirectSchemaCountOnly",
            graph_schema_overrides={0: None},
        )
        with self.assertRaisesRegex(ValueError, "every other exact runtime gate"):
            self._complete_source_waived(schema_count)

        custom_details, _ = self._prepare_direct_completion(
            "DirectCustomDetails",
            graph_schema_overrides={0: [{"name": "OtherColumn", "type": "String"}]},
        )
        detection_path = custom_details / "XDR Detections/Rule00.yaml"
        detection = yaml.safe_load(detection_path.read_text())
        detection["properties"]["detectionAction"]["alertTemplate"]["customDetails"] = {
            "account": "DeviceName"
        }
        detection_path.write_text(yaml.safe_dump(detection), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "every other exact runtime gate"):
            self._complete_source_waived(custom_details)

        review, _ = self._prepare_direct_completion(
            "DirectReview",
            review_required=True,
        )
        with self.assertRaisesRegex(ValueError, "unrelated conversion or review findings"):
            self._complete_source_waived(review)

        technical, _ = self._prepare_direct_completion(
            "DirectTechnical",
            technical_error=True,
        )
        with self.assertRaisesRegex(ValueError, "unrelated conversion or review findings"):
            self._complete_source_waived(technical)

        structural, _ = self._prepare_direct_completion("DirectStructural")
        with self.assertRaisesRegex(ValueError, "structural validation to pass"):
            self._complete_source_waived(structural, structural_valid=False)

    def test_environment_blocked_cannot_bypass_source_whitelist_xdr_gates(self) -> None:
        cases = (
            ("EnvBlockedXdrUnrun", "not-run", None),
            ("EnvBlockedSchemaMissing", "passed", None),
            ("EnvBlockedMalformedSchema", "passed", []),
        )
        for name, graph_status, schema in cases:
            with self.subTest(name=name):
                solution, _ = self._prepare_direct_completion(
                    name,
                    graph_status=graph_status,
                    graph_schema_overrides=(
                        {0: schema} if graph_status == "passed" else None
                    ),
                )
                with self.assertRaisesRegex(
                    ValueError, "cannot be relabeled environment-blocked"
                ):
                    complete_workflow_stage(
                        solution,
                        "validation",
                        status="passed",
                        message="runtime provider unavailable",
                        artifacts={"runtimeStatus": "environment-blocked"},
                    )

    def test_runtime_pending_stage_completes_source_waiver_without_scope_error(self) -> None:
        solution, _ = self._prepare_direct_completion("PendingStageSourceWaived")
        complete_workflow_stage(
            solution,
            "validation",
            status="blocked",
            message="Runtime validation is not complete.",
        )
        state_path, state = workflow_module._load(solution)
        structural = {
            "conversionScope": {"kind": "solution"},
            "total": 2,
            "invalid": 0,
            "results": [{"valid": True}, {"valid": True}],
        }
        with mock.patch.object(
            workflow_module, "validate_solution", return_value=structural
        ):
            updated = workflow_module._complete_runtime_pending_stage(
                solution, state_path, state, {"results": []}
            )
        self.assertEqual("passed", updated["stages"]["validation"]["status"])
        self.assertEqual(
            "source-waived",
            updated["stages"]["validation"]["artifacts"]["runtimeStatus"],
        )

    def test_direct_validation_records_source_waived_not_passed_query(self) -> None:
        solution, run_id = self._prepare_direct_completion("DirectSuccess")
        self._complete_source_waived(solution)
        with using_run(solution, run_id):
            evidence = current_runtime_evidence(solution)
        state = workflow_status(solution)
        validation = state["stages"]["validation"]
        raw = json.loads(
            artifact_path(
                solution, "runtime-validation.azure-monitor-sdk.json"
            ).read_text()
        )
        self.assertEqual("passed", validation["status"])
        self.assertEqual("source-waived", validation["artifacts"]["runtimeStatus"])
        self.assertEqual("IdentityInfo", validation["artifacts"]["sourceRuntimeWhitelistTable"])
        self.assertEqual("failed", validation["artifacts"]["sourceRuntimeWhitelistRawStatus"])
        self.assertFalse(evidence["passed"])
        self.assertEqual(
            "failed",
            next(item for item in raw["results"] if item["detection"] == "Rule00.yaml")["status"],
        )
        flow = _flow_stage({
            "status": "passed",
            "artifacts": {
                "runtimeStatus": "source-waived",
                "sourceRuntimeWhitelistTable": "IdentityInfo",
            },
            "message": validation["message"],
        })
        self.assertIn("Source waived", flow["display"])
        self.assertIn("not fully runtime-qualified", flow["display"])


if __name__ == "__main__":
    unittest.main()
